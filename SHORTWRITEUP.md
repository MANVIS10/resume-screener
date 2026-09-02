# Short Write-up

**Approach.** FastAPI + Jinja2 server-rendered templates, SQLite for storage, Groq
(`openai/gpt-oss-120b`) for the fit assessment. Two tables, `jds` and `resumes`, with
`resumes.jd_id` as a foreign key — a JD is modeled as having many resumes from the
start, not hardcoded to one. Candidate and admin are separate route groups; every
admin route (page and data) is gated by a signed session cookie checked server-side
via a FastAPI dependency, so hitting `/admin/jds/{id}` directly without the cookie
gets a 303 to the login page — there's no client-side-only hiding of scores.

**LLM design.** The prompt sends the full JD text and the resume text extracted via
`python-docx`, forces strict JSON output (`match_score`, `fit_summary`, `gaps`), and
explicitly instructs the model to cite concrete overlaps/mismatches rather than
generic praise, and to produce interview-ready follow-up questions. Malformed JSON
raises loudly and is logged rather than silently stored as a blank score. Tested
against 4 varied resumes (2 strong, 2 clear mismatches) across both JDs — scores and
reasoning differentiated sensibly in each case.

**Trade-offs / deviations.** The brief's default target was Vercel, but this app uses
a stateful FastAPI process with a local SQLite file, which needs a persistent disk
and long-running process — Vercel's serverless functions don't fit that. Deployed to
Render instead (a `Procfile`-driven web service with a persistent disk), which the
brief explicitly allows as a substitution if I explain it. In a real production
setting I'd swap SQLite for managed Postgres (e.g. Render Postgres or Neon) so state
isn't tied to a single instance/disk and the app can scale horizontally.

**What I'd improve with more time:** resume dedup/re-application handling, pagination
on the admin applications list, richer resume parsing (tables, headers via
`python-docx`), streaming the LLM call so large resumes don't block the request, and
a proper test suite around the access-separation boundary.
