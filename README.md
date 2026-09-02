# Resume Screener

A small hiring tool: admins post job descriptions and see LLM-scored applications
against each one; candidates browse open roles and apply with a `.docx` resume, and
only ever see a confirmation.

- **Admin** (`/admin`, password-gated) — post JDs, see every application per JD with
  match score, fit summary, and gaps/follow-up questions.
- **Candidate** (`/`, public) — open roles, application form, `.docx` upload,
  confirmation. No scores anywhere.

**Stack:** FastAPI + Jinja2 · Turso (libSQL) · Groq `openai/gpt-oss-120b` · Vercel.

See [SHORTWRITEUP.md](SHORTWRITEUP.md) for approach and trade-offs.

## Local development

```bash
python -m venv .venv && .venv/Scripts/activate      # Windows; use bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env                                 # then fill in the values
python scripts/init_db.py                            # create tables
uvicorn app.main:app --reload --port 8000
```

`TURSO_DATABASE_URL` accepts a plain file path locally (`resume_screener.db`) and a
`libsql://` URL in production — the same code path serves both.

## Environment variables

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Groq API key for resume scoring |
| `ADMIN_PASSWORD` | Password for the admin login |
| `SECRET_KEY` | Signs the admin session cookie — must stay stable across deploys |
| `TURSO_DATABASE_URL` | `libsql://...` in production, a file path locally |
| `TURSO_AUTH_TOKEN` | Turso token; leave empty for a local file |

## Deploying

1. Create the database at [turso.tech](https://turso.tech) and copy its URL and token.
2. Point a local `.env` at it and run `python scripts/init_db.py` once to create the schema.
3. `vercel` to link the project, set the five variables above in the Vercel dashboard
   (or via `vercel env add`), then `vercel --prod`.

`vercel.json` rewrites every path to `api/index.py`, which serves the FastAPI app.
