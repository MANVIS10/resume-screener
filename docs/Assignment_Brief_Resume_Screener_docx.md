# Take-Home Assignment

*Build a Resume Screener — Candidate Brief*

# 1\. Context

We're hiring for a role that involves building lightweight internal tools quickly and thoughtfully. Rather than a generic coding test, we'd like you to build something close to a real problem we face: screening applicants against open roles at the speed we hire.

Attached are two sample job openings (Opening A and Opening B) from a partner brand we work with. Treat them as real job descriptions for the purpose of this exercise — the names have been anonymised, but the content and requirements are representative of what you'd be working with on the job.

# 2\. The Task

Build a small web application — a "Resume Screener" — that a hiring team could actually use day to day. Think of it as two sides of one platform, not one flat form:

## Admin Tab (admin-only)

* Post a new job opening — title, company/brand, and the full JD text.

* See every JD that's been posted so far, and open any one of them.

* For each JD, see every resume submitted against it — one JD will realistically receive many resumes over time, from many different candidates.

* For each submitted resume, see the LLM's fit summary, match score, and gaps/follow-up questions.

* This tab is the only place any score or analysis is visible, anywhere in the app.

## Candidate Tab (public)

* Shows the list of currently open JDs — whatever the admin has posted — so a candidate can pick which one they're applying for.

* A candidate details form: full name, address, phone number, email address, age, and current location/place.

* A resume/CV upload field that accepts Word documents (.docx) only — not PDF.

* On submit, the candidate sees only a simple confirmation — something like "Thanks, we've received your application. We'll reach out soon." No score, no analysis, no ranking. Ever.

So functionally: the admin owns the JDs and is the only one who ever sees how a resume scored; a candidate only ever sees that their own application went through. Model the JD → resume relationship as one-to-many from the start — don't hardcode it around a single fixed JD.

You're free to choose your own stack, as long as it runs end-to-end and deploys cleanly to Vercel — a static HTML/JS app, a Next.js app, or any frontend framework with serverless API routes all work well. If you'd naturally reach for something Vercel doesn't run well (e.g. a long-running Python/Flask backend), pick a Vercel-friendly equivalent instead. The admin/candidate separation doesn't need real production-grade auth for this exercise — a simple gate (password, hardcoded route, whatever) is fine, as long as the two views are genuinely separated and a candidate has no way to see scores through the UI.

# 3\. On the LLM piece

You don't need a paid API key for this. Free tiers work fine for a take-home — for example Groq (fast open-weight models, generous free tier), Google's Gemini API free tier, or OpenRouter's free-tier models. Pick whichever is easiest for you to wire up quickly; we're evaluating your judgement and execution, not which vendor you pick.

If you'd rather mock the LLM call with a clearly-labelled stub (e.g. because of API key friction under time pressure), that's acceptable too — just say so in your write-up and explain what the real call would look like.

# 4\. What We're Evaluating

* Product judgement — how you interpret an ambiguous brief and what you choose to prioritise.

* Data modelling — is a JD properly modelled as having many resumes against it, or did you hardcode around one JD and one resume?

* Access separation — is the admin-only scoring view actually inaccessible to a candidate through the UI, or just hidden by convention?

* Robustness — does the LLM comparison hold up across different JDs and different resumes (varied formats, lengths, messy content), not just the one happy-path example you tested with?

* Execution speed and pragmatism — a working end-to-end flow beats a polished but incomplete one.

* Prompt/LLM design — how you structure the comparison so the output is actually useful to whoever's reading it on the admin side, not just a generic summary.

* Communication — a short (5–10 line) write-up of your approach, trade-offs, and what you'd do next with more time.

# 5\. Supporting Documents

Two files are attached alongside this brief:

* Opening A — Founders Office Associate (Satva Partners)

* Opening B — Content & Communities Lead (House of Ved)

Post both of these as JDs from your admin tab, then test by submitting a few different resumes (your own, a friend's, anything reasonably real) against each one — that's what will actually show whether your JD → resume modelling and your LLM comparison hold up.

# 6\. Submission

Please deploy your app to Vercel and submit a live link — we want to actually click through the flow, not just read the code.

* A live Vercel URL where we can run through the full flow ourselves — post a JD as admin, then apply to it as a candidate, then check the score back in the admin tab.

* A link to your code (a GitHub repo is preferred; a zip is fine if you'd rather not make it public).

* Your short write-up (see Section 4).

If any part of your stack can't run on Vercel (e.g. a backend that needs long-running processes), that's fine — just say so in your write-up and explain how you'd deploy it in a real setting.

*Please submit by Sunday, 30 Aug 2026, 11:59 PM. Reach out any time if something in the brief is unclear — asking a sharp clarifying question is itself a positive signal, not a negative one.*