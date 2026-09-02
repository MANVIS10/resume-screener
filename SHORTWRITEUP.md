# Short Write-up

**Approach.** FastAPI + Jinja2 server-rendered templates, deployed to Vercel as a
single serverless function, with Turso (hosted libSQL) for storage and Groq
(`openai/gpt-oss-120b`) for the fit assessment. Two tables, `jds` and `resumes`,
with `resumes.jd_id` as a foreign key — a JD has many resumes from the start, not
hardcoded to one. Candidate and admin are separate route groups; every admin route
is gated by a signed session cookie checked server-side via a FastAPI dependency,
so hitting `/admin/jds/{id}` directly without the cookie gets a 303 to the login
page. Scores exist in no candidate-facing template, so there is nothing to unhide.

**Why Turso rather than plain SQLite.** Vercel's filesystem is read-only apart from
`/tmp`, which doesn't survive between invocations — a local SQLite file would
silently lose every application. Turso is libSQL over HTTP, so the SQL dialect and
`?` placeholders stay identical and only the connection layer changed. It also
suits serverless better than a pooled Postgres connection: each request opens a
stateless HTTP connection rather than holding a socket open.

**LLM design.** The prompt sends the full JD text and the resume text extracted via
`python-docx` (`.docx` only, per the brief), forces strict JSON (`match_score`,
`fit_summary`, `gaps`), and explicitly instructs the model to cite concrete
overlaps and mismatches rather than generic praise, and to produce interview-ready
follow-up questions. Output is validated and the score clamped to 0-100; malformed
JSON raises and is logged rather than being stored as a silent blank.

**Robustness testing.** Four resumes across both openings, deliberately varied: a
Tier-1 consulting profile scored 85 against Opening A while a backend engineer
scored 18, and a content/community lead scored 58 against Opening B while a
practising accountant scored 5. The 58 is the interesting one — the candidate has
real audience-growth numbers but only general spiritual grounding against a JD that
asks for Vedic depth, and the summary says exactly that instead of rounding her up
on keyword overlap. Non-`.docx` uploads, corrupt `.docx` files, and empty documents
are each rejected with their own message before any LLM call is made.

**Trade-offs / what I'd do next.** Scoring runs inline in the request, so a
submission blocks for as long as Groq takes — a queue with a "pending" state in the
admin table is the right fix past a handful of applications. Auth is a single shared
password, appropriate for this exercise but not for real multi-recruiter use. Beyond
that: resume dedup and re-application handling, pagination on the admin list, richer
`.docx` parsing (tables and headers, which `python-docx` skips today), and an
automated test suite around the access-separation boundary, which is currently
covered by a manual end-to-end script rather than CI.
