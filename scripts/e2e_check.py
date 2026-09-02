"""End-to-end check: access separation, upload validation, and LLM scoring.

Generates its own varied .docx resumes, then drives the running app the way a
real admin and a real candidate would.

    python scripts/e2e_check.py                        # against localhost:8000
    python scripts/e2e_check.py https://your.vercel.app

Note: this posts real applications and burns real Groq calls, so point it at a
scratch environment rather than anything you care about.
"""
import io
import os
import re
import sys

import httpx
from docx import Document
from dotenv import load_dotenv

load_dotenv()

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PASSWORD = os.environ.get("ADMIN_PASSWORD")

RESUMES = {
    "strong_founders": ("Ananya Rao", """Ananya Rao — Mumbai, India
Associate, Bain & Company (2023-2026). Built financial models and market-sizing
analyses for 11 growth-stage clients. Storyboarded 40+ exec-ready decks for CXO and
board audiences. Co-led mobilisation of a target operating model redesign. Ran 60+
expert interviews and competitor teardowns. B.Com (Hons), SRCC. Deep personal
interest in Indic philosophy and dharmic texts."""),
    "weak_founders": ("Rohit Menon", """Rohit Menon — Kochi, India
Senior Software Engineer, CloudScale Systems (2021-2026). Maintained Kubernetes
clusters serving 200M requests/day. Wrote Go microservices and Postgres migrations.
Reduced p99 latency 40%. B.Tech Computer Science, NIT Calicut.
Skills: Go, Python, Kubernetes, Kafka, Terraform, AWS."""),
    "strong_content": ("Meera Iyer", """Meera Iyer — London, UK
Content Lead, Mindful Media Collective (2023-2026). Grew a spirituality-focused
channel from 12k to 240k subscribers. Owned the calendar across YouTube long-form and
Instagram short-form; scripted 300+ shorts, three past 5M views. Built a 9,000-member
virtual community. Ran live events in London and Manchester averaging 400 attendees.
BA English Literature, Warwick. Lifelong student of the Bhagavad Gita."""),
    "weak_content": ("Daniel Fisher", """Daniel Fisher — San Francisco, USA
Senior Auditor, Whitfield & Grange LLP (2020-2026). Led statutory audits for 14
manufacturing clients. Prepared consolidated tax filings and transfer-pricing
documentation. Supervised four junior auditors. BS Accounting, San Jose State.
Skills: GAAP, IFRS, audit planning, tax compliance, SAP."""),
}

failures = []


def check(condition, message):
    print(("  PASS  " if condition else "  FAIL  ") + message)
    if not condition:
        failures.append(message)


def as_docx(body: str) -> bytes:
    doc = Document()
    for line in body.strip().splitlines():
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def main():
    if not PASSWORD:
        sys.exit("ADMIN_PASSWORD is not set")

    anon = httpx.Client(base_url=BASE, follow_redirects=False, timeout=120)
    admin = httpx.Client(base_url=BASE, follow_redirects=True, timeout=120)

    print(f"\n[1] Admin routes are closed without a session cookie ({BASE})")
    for path in ("/admin", "/admin/jds/1"):
        r = anon.get(path)
        check(r.status_code == 303 and r.headers.get("location") == "/admin/login",
              f"{path} -> {r.status_code} Location={r.headers.get('location')}")

    print("\n[2] Login")
    check(anon.post("/admin/login", data={"password": "wrong"}).status_code == 401,
          "wrong password rejected")
    r = admin.post("/admin/login", data={"password": PASSWORD})
    check(r.status_code == 200 and "Job Descriptions" in r.text, "correct password accepted")

    print("\n[3] Admin posts a JD")
    r = admin.post("/admin/jds", data={
        "title": "E2E Check Role", "company": "Test Co",
        "jd_text": "Strategy support: data analysis, exec-ready decks, project mobilisation."})
    check(r.status_code == 200 and "E2E Check Role" in r.text, "JD created and listed")
    jd_ids = [int(m) for m in re.findall(r'/admin/jds/(\d+)', r.text)]
    jd_id = max(jd_ids) if jd_ids else 1

    print("\n[4] Bad uploads rejected before any LLM call")
    form = {"full_name": "Bad File", "address": "x", "phone": "1",
            "email": "b@x.com", "age": "30", "location": "x"}
    r = anon.post(f"/apply/{jd_id}", data=form,
                  files={"resume": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")})
    check(r.status_code == 400 and ".docx" in r.text, f"PDF -> {r.status_code}")
    r = anon.post(f"/apply/{jd_id}", data=form,
                  files={"resume": ("resume.docx", b"not a docx", "application/octet-stream")})
    check(r.status_code == 400, f"corrupt .docx -> {r.status_code}")

    print("\n[5] Candidates apply and see a confirmation only")
    for key, (name, body) in RESUMES.items():
        r = anon.post(f"/apply/{jd_id}",
                      data={"full_name": name, "address": "Somewhere", "phone": "+91 90000 00000",
                            "email": f"{key}@example.com", "age": "28", "location": "Remote"},
                      files={"resume": (f"{key}.docx", as_docx(body),
                             "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
        leaked = re.search(r"score|/100|match|gap", r.text, re.I)
        check(r.status_code == 200 and "received your application" in r.text.lower() and not leaked,
              f"{name:14s} -> {r.status_code}, confirmation only, nothing leaked")

    print("\n[6] Scores are visible on the admin side")
    page = admin.get(f"/admin/jds/{jd_id}").text
    scores = [int(s) for s in re.findall(r"(\d+)/100", page)]
    for name, _ in RESUMES.values():
        check(name in page, f"{name:14s} listed for JD {jd_id}")
    check(len(scores) >= len(RESUMES), f"scores rendered: {scores}")
    check(len(set(scores)) > 1, f"scores differentiate between candidates: {scores}")

    print("\n" + ("ALL PASSED" if not failures else f"{len(failures)} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
