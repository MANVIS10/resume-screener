import io
import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from docx import Document
from pypdf import PdfReader

from app.db import init_db, db_session
from app.auth import create_session_token, verify_session_token, require_admin, COOKIE_NAME
from app.llm import score_resume, LLMScoringError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resume_screener")

app = FastAPI(title="Resume Screener")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


# ---------- Public / candidate routes ----------

@app.get("/", response_class=HTMLResponse)
def list_jobs(request: Request):
    with db_session() as conn:
        jobs = conn.execute("SELECT id, title, company, created_at FROM jds ORDER BY created_at DESC").fetchall()
    return templates.TemplateResponse("candidate_jobs.html", {"request": request, "jobs": jobs})


@app.get("/apply/{jd_id}", response_class=HTMLResponse)
def apply_form(request: Request, jd_id: int):
    with db_session() as conn:
        job = conn.execute("SELECT id, title, company, jd_text FROM jds WHERE id = ?", (jd_id,)).fetchone()
    if job is None:
        return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)
    return templates.TemplateResponse("apply_form.html", {"request": request, "job": job, "error": None})


@app.post("/apply/{jd_id}", response_class=HTMLResponse)
async def apply_submit(
    request: Request,
    jd_id: int,
    full_name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
    age: str = Form(...),
    location: str = Form(...),
    resume: UploadFile = File(...),
):
    with db_session() as conn:
        job = conn.execute("SELECT id, title, company, jd_text FROM jds WHERE id = ?", (jd_id,)).fetchone()
    if job is None:
        return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)

    filename = resume.filename or ""
    lower_name = filename.lower()
    if not (lower_name.endswith(".docx") or lower_name.endswith(".pdf")):
        return templates.TemplateResponse(
            "apply_form.html",
            {"request": request, "job": job, "error": "Please upload a .docx or .pdf file — other formats (.doc, images) are not accepted."},
            status_code=400,
        )

    raw_bytes = await resume.read()
    try:
        if lower_name.endswith(".docx"):
            doc = Document(io.BytesIO(raw_bytes))
            resume_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            reader = PdfReader(io.BytesIO(raw_bytes))
            resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return templates.TemplateResponse(
            "apply_form.html",
            {"request": request, "job": job, "error": "We couldn't read that file. Please make sure it's a valid .docx or .pdf document and try again."},
            status_code=400,
        )

    if not resume_text.strip():
        return templates.TemplateResponse(
            "apply_form.html",
            {"request": request, "job": job, "error": "That resume appears to be empty. Please upload a .docx file with your resume text."},
            status_code=400,
        )

    try:
        result = score_resume(job["jd_text"], resume_text)
        match_score = result["match_score"]
        fit_summary = result["fit_summary"]
        gaps_json = json.dumps(result["gaps"])
    except LLMScoringError as e:
        logger.error("LLM scoring failed for jd_id=%s: %s", jd_id, e)
        match_score = None
        fit_summary = f"[SCORING FAILED] {e}"
        gaps_json = json.dumps([])

    with db_session() as conn:
        conn.execute(
            """INSERT INTO resumes
               (jd_id, name, address, phone, email, age, location, resume_text,
                match_score, fit_summary, gaps_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                jd_id, full_name, address, phone, email, age, location, resume_text,
                match_score, fit_summary, gaps_json,
            ),
        )

    return templates.TemplateResponse("apply_confirmation.html", {"request": request})


# ---------- Admin auth ----------

@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})


@app.post("/admin/login", response_class=HTMLResponse)
def admin_login_submit(request: Request, password: str = Form(...)):
    expected = os.environ.get("ADMIN_PASSWORD")
    if not expected or password != expected:
        return templates.TemplateResponse(
            "admin_login.html", {"request": request, "error": "Incorrect password."}, status_code=401
        )
    token = create_session_token()
    resp = RedirectResponse(url="/admin", status_code=303)
    resp.set_cookie(COOKIE_NAME, token, httponly=True, samesite="lax", max_age=8 * 60 * 60)
    return resp


@app.get("/admin/logout")
def admin_logout():
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp


# ---------- Admin routes (all gated) ----------

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, _=Depends(require_admin)):
    with db_session() as conn:
        jobs = conn.execute(
            """SELECT jds.id, jds.title, jds.company, jds.created_at,
                      COUNT(resumes.id) as resume_count
               FROM jds LEFT JOIN resumes ON resumes.jd_id = jds.id
               GROUP BY jds.id ORDER BY jds.created_at DESC"""
        ).fetchall()
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "jobs": jobs})


@app.post("/admin/jds")
def admin_create_jd(
    request: Request,
    title: str = Form(...),
    company: str = Form(...),
    jd_text: str = Form(...),
    _=Depends(require_admin),
):
    with db_session() as conn:
        conn.execute(
            "INSERT INTO jds (title, company, jd_text) VALUES (?, ?, ?)",
            (title, company, jd_text),
        )
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/admin/jds/{jd_id}", response_class=HTMLResponse)
def admin_view_jd(request: Request, jd_id: int, _=Depends(require_admin)):
    with db_session() as conn:
        job = conn.execute("SELECT id, title, company, jd_text, created_at FROM jds WHERE id = ?", (jd_id,)).fetchone()
        if job is None:
            return templates.TemplateResponse("not_found.html", {"request": request}, status_code=404)
        resumes = conn.execute(
            """SELECT id, name, address, phone, email, age, location,
                      match_score, fit_summary, gaps_json, submitted_at
               FROM resumes WHERE jd_id = ? ORDER BY submitted_at DESC""",
            (jd_id,),
        ).fetchall()

    parsed_resumes = []
    for r in resumes:
        d = dict(r)
        try:
            d["gaps"] = json.loads(d["gaps_json"]) if d["gaps_json"] else []
        except (TypeError, ValueError):
            d["gaps"] = []
        parsed_resumes.append(d)

    return templates.TemplateResponse(
        "admin_jd_detail.html", {"request": request, "job": job, "resumes": parsed_resumes}
    )
