# Frontend Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve the visual polish, responsiveness, and form UX of the existing Resume Screener frontend without changing the backend, database, or deployment target.

**Architecture:** No architecture change. The app stays FastAPI + Jinja2 server-rendered templates + SQLite, deployed to Render — this plan touches only `app/static/style.css` and the eight files in `app/templates/`. No new routes, no new dependencies, no JS framework. A small amount of vanilla `<script>` is allowed inline in templates for pure UX sugar (showing the picked filename, disabling a submit button on click) — nothing that talks to the network or changes app behavior.

**Tech Stack:** Same as existing app — Jinja2 templates, hand-written CSS. No build step, no npm, no new packages.

**Spec:** This plan has no separate spec doc — the "spec" is the scope decision made in chat: polish only, keep current stack, no Vercel migration. Deviating from that (e.g. adding a JS framework, changing the DB, moving to Vercel) is out of scope for this plan.

## Global Constraints

- No new Python dependencies, no new routes, no schema changes.
- No client-side framework (React/Vue/etc) and no build step — plain CSS + optional inline `<script>` only.
- Every page must still render correctly with JavaScript disabled (progressive enhancement only — file-picker filename display, submit-button disabling, etc. are nice-to-haves, not requirements).
- Existing template variable names, route names, and form field names (`full_name`, `resume`, etc.) must not change — the backend in `app/main.py` reads them by exact name.
- Verification for this plan is visual (via the Browser pane / `preview_start`), not `pytest` — there is no meaningful unit test for CSS layout. Each task's "test" step is a manual visual check with a screenshot.

---

### Task 1: Responsive layout foundation + design tokens

**Files:**
- Modify: `app/static/style.css` (full rewrite of the top of the file — CSS variables, responsive container, mobile breakpoint)

**Interfaces:**
- Consumes: nothing (base layer all other tasks build on)
- Produces: CSS custom properties (`--color-bg`, `--color-card`, `--color-border`, `--color-text`, `--color-text-muted`, `--color-primary`, `--color-primary-hover`, `--radius`, `--shadow-sm`) that Tasks 2-4 reuse instead of hardcoded hex values. Produces a `@media (max-width: 640px)` breakpoint pattern that later tasks follow for their own mobile rules.

- [ ] **Step 1: Take a baseline screenshot for comparison**

Start the local server if it isn't already running:
```bash
cd "/c/Users/sonim/resume screener" && source .venv/Scripts/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
sleep 2
```
Use the Browser pane to navigate to `http://localhost:8000/` and take a screenshot at desktop size (800px+) and at mobile size (375px, via `resize_window` preset `"mobile"`). Save both mentally/visually — no file needed, this is just a reference point for "did it get better."

- [ ] **Step 2: Add CSS custom properties and responsive container**

Replace the top of `app/static/style.css` (everything before `.card {`) with:

```css
:root {
    --color-bg: #f7f7f8;
    --color-card: #ffffff;
    --color-border: #e2e2e6;
    --color-text: #1a1a1a;
    --color-text-muted: #666666;
    --color-primary: #4b3fdb;
    --color-primary-hover: #3a2fc0;
    --color-error-bg: #fde2e2;
    --color-error-text: #9b1c1c;
    --radius: 10px;
    --radius-sm: 6px;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.06);
}

* { box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0;
    background: var(--color-bg);
    color: var(--color-text);
    line-height: 1.5;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: #1a1a2e;
    color: white;
    position: sticky;
    top: 0;
    z-index: 10;
}
.topbar .brand { color: white; text-decoration: none; font-weight: 700; font-size: 1.15rem; }
.topbar nav a { color: #cfcfe8; text-decoration: none; margin-left: 1.25rem; font-size: 0.9rem; }
.topbar nav a:hover { color: white; }

.container {
    max-width: 860px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

h1 { font-size: 1.6rem; margin: 0 0 0.5rem; }
h2 { font-size: 1.2rem; margin: 2rem 0 0.75rem; }

@media (max-width: 640px) {
    .container { padding: 1.25rem 1rem; }
    .topbar { padding: 0.85rem 1rem; }
    h1 { font-size: 1.35rem; }
}
```

- [ ] **Step 3: Update the `.card`, `.btn`, `.job-list-item` rules below to use the new variables**

Replace the remaining rules (everything from `.card {` to the end of the file) with the same rules but swapping hardcoded colors for variables, and adding a shadow + mobile stacking for `.job-list-item`:

```css
.card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
}

.job-list-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}
.job-list-item h3 { margin: 0 0 0.25rem; }
.job-list-item p { margin: 0; color: var(--color-text-muted); font-size: 0.9rem; }

@media (max-width: 640px) {
    .job-list-item { flex-direction: column; align-items: flex-start; }
    .job-list-item .btn { width: 100%; text-align: center; }
}

.btn {
    display: inline-block;
    background: var(--color-primary);
    color: white;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: var(--radius-sm);
    text-decoration: none;
    cursor: pointer;
    font-size: 0.95rem;
    transition: background 0.15s ease;
}
.btn:hover { background: var(--color-primary-hover); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--color-border); color: var(--color-text); }
.btn-secondary:hover { background: #cfcfd6; }

form label { display: block; margin-top: 1rem; font-weight: 600; font-size: 0.9rem; }
form input[type=text],
form input[type=email],
form input[type=tel],
form input[type=number],
form textarea,
form input[type=password] {
    width: 100%;
    padding: 0.6rem 0.7rem;
    margin-top: 0.3rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: 0.95rem;
    font-family: inherit;
}
form input:focus, form textarea:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(75, 63, 219, 0.15);
}
form textarea { min-height: 160px; font-family: inherit; resize: vertical; }

.error {
    background: var(--color-error-bg);
    color: var(--color-error-text);
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    margin-top: 1rem;
    font-size: 0.9rem;
}

.score-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.9rem;
    white-space: nowrap;
}
.score-high { background: #dcfce7; color: #166534; }
.score-mid { background: #fef9c3; color: #854d0e; }
.score-low { background: #fee2e2; color: #991b1b; }

.resume-detail { border-top: 1px solid var(--color-border); margin-top: 1rem; padding-top: 1rem; }
.gaps-list { margin: 0.5rem 0 0; padding-left: 1.2rem; }
.meta { color: var(--color-text-muted); font-size: 0.85rem; }
.confirmation { text-align: center; padding: 3rem 1rem; }
```

- [ ] **Step 4: Visual check — desktop and mobile**

Server should already be running from Step 1 (restart if you changed Python, but CSS is static — no restart needed, just hard-refresh the browser tab). Navigate to `http://localhost:8000/`, screenshot at desktop width, then use `resize_window` preset `"mobile"` and screenshot again.

Expected: cards have a subtle shadow, job list items stack vertically with a full-width Apply button on mobile (< 640px), topbar stays fixed at top when scrolling. No layout should overflow horizontally at 375px width.

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/sonim/resume screener" && git add app/static/style.css && git commit -m "$(cat <<'EOF'
Add responsive layout foundation and CSS design tokens

Introduces CSS custom properties for colors/radius/shadow and a
640px mobile breakpoint so cards, buttons, and job list items adapt
on small screens. No markup or backend changes.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Apply form UX (file picker feedback, inline validation hints, submit state)

**Files:**
- Modify: `app/templates/apply_form.html`
- Modify: `app/static/style.css` (append file-input and hint styles)

**Interfaces:**
- Consumes: CSS variables from Task 1 (`--color-primary`, `--color-border`, `--radius-sm`, `--color-text-muted`).
- Produces: a `.file-picker` component pattern (styled label + hidden native input + filename display) that no other task currently reuses, but is the pattern to copy if a future page needs file upload styling.

- [ ] **Step 1: Add a styled file-picker component to `style.css`**

Append to `app/static/style.css`:

```css
.file-picker {
    margin-top: 0.3rem;
}
.file-picker input[type=file] {
    position: absolute;
    width: 1px; height: 1px;
    opacity: 0; overflow: hidden;
}
.file-picker-label {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 1rem;
    border: 1px dashed var(--color-border);
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 0.9rem;
    color: var(--color-text-muted);
    background: var(--color-bg);
    transition: border-color 0.15s ease;
}
.file-picker-label:hover { border-color: var(--color-primary); }
.file-picker-filename { font-weight: 600; color: var(--color-text); }
.field-hint { font-size: 0.8rem; color: var(--color-text-muted); margin-top: 0.25rem; }
```

- [ ] **Step 2: Update the resume upload field in `apply_form.html`**

Read the current file first, then replace the resume field block:

Current block (around line 27-28 of `app/templates/apply_form.html`):
```html
        <label for="resume">Resume (.docx or .pdf)</label>
        <input type="file" id="resume" name="resume" accept=".docx,.pdf" required>
```

Replace with:
```html
        <label for="resume">Resume</label>
        <div class="file-picker">
            <label class="file-picker-label" for="resume">
                <span id="file-picker-text">Choose a .docx or .pdf file</span>
            </label>
            <input type="file" id="resume" name="resume" accept=".docx,.pdf" required
                   onchange="document.getElementById('file-picker-text').textContent = this.files.length ? this.files[0].name : 'Choose a .docx or .pdf file'; document.getElementById('file-picker-text').className = this.files.length ? 'file-picker-filename' : '';">
        </div>
        <p class="field-hint">Accepted formats: Word (.docx) or PDF (.pdf).</p>
```

- [ ] **Step 3: Disable the submit button on click to prevent double-submits**

Find the submit button block in `apply_form.html`:
```html
        <div style="margin-top:1.5rem;">
            <button class="btn" type="submit">Submit Application</button>
        </div>
```

Replace with:
```html
        <div style="margin-top:1.5rem;">
            <button class="btn" type="submit" id="submit-btn" onclick="this.disabled=true; this.textContent='Submitting…'; this.form.submit();">Submit Application</button>
        </div>
```

Note: `this.form.submit()` is required here because disabling the button before the browser processes the click can prevent the click's own form submission in some browsers — calling `.submit()` explicitly guarantees the POST still fires.

- [ ] **Step 4: Visual + functional check**

Navigate to `http://localhost:8000/apply/1` (assuming JD id 1 exists — check `http://localhost:8000/` first and use whatever id is listed). Click the file picker — confirm it opens a native file dialog and, after picking a file, the filename appears in place of "Choose a .docx or .pdf file". Fill out the rest of the form with test data and click Submit — confirm the button becomes disabled and reads "Submitting…" before the page navigates to the confirmation page.

Expected: no console errors (`read_console_messages` in the Browser pane should show nothing new), confirmation page still reads "Thanks! We've received your application."

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/sonim/resume screener" && git add app/templates/apply_form.html app/static/style.css && git commit -m "$(cat <<'EOF'
Polish apply form: styled file picker, submit-state feedback

Shows the picked filename instead of the raw browser file input,
and disables the submit button with a "Submitting..." label on
click to prevent accidental double-submits. Pure progressive
enhancement -- form still works with JS disabled.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Admin dashboard and JD-detail visual polish

**Files:**
- Modify: `app/templates/admin_dashboard.html`
- Modify: `app/templates/admin_jd_detail.html`
- Modify: `app/static/style.css` (append admin-specific rules)

**Interfaces:**
- Consumes: `.card`, `.score-badge`, `.job-list-item` from Task 1; `.field-hint` pattern from Task 2 (reused for the JD-post-form textarea).
- Produces: `.stat-row` and `.empty-state` classes that either template can reuse for future admin views.

- [ ] **Step 1: Add admin-specific CSS**

Append to `app/static/style.css`:

```css
.empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    color: var(--color-text-muted);
}
.stat-row {
    display: flex;
    gap: 1.5rem;
    margin: 0.25rem 0 0;
    font-size: 0.85rem;
    color: var(--color-text-muted);
}
.stat-row strong { color: var(--color-text); }
details summary {
    cursor: pointer;
    font-weight: 600;
    color: var(--color-primary);
}
details summary:hover { text-decoration: underline; }
details pre {
    margin-top: 0.75rem;
    background: var(--color-bg);
    padding: 1rem;
    border-radius: var(--radius-sm);
    max-height: 400px;
    overflow-y: auto;
}
```

- [ ] **Step 2: Update the empty states in both admin templates**

In `app/templates/admin_dashboard.html`, find:
```html
{% if not jobs %}
<div class="card"><p>No JDs posted yet.</p></div>
{% endif %}
```
Replace with:
```html
{% if not jobs %}
<div class="card empty-state"><p>No JDs posted yet. Use the form above to post your first job description.</p></div>
{% endif %}
```

In `app/templates/admin_jd_detail.html`, find:
```html
{% if not resumes %}
<div class="card"><p>No applications yet for this role.</p></div>
{% endif %}
```
Replace with:
```html
{% if not resumes %}
<div class="card empty-state"><p>No applications yet for this role. Share the candidate link once you're ready.</p></div>
{% endif %}
```

- [ ] **Step 3: Use `.stat-row` for the JD detail meta line**

In `app/templates/admin_jd_detail.html`, find:
```html
<p class="meta">{{ job.company }} &middot; posted {{ job.created_at }}</p>
```
Replace with:
```html
<div class="stat-row">
    <span><strong>{{ job.company }}</strong></span>
    <span>Posted {{ job.created_at }}</span>
    <span>{{ resumes|length }} application(s)</span>
</div>
```

- [ ] **Step 4: Visual check**

Log in at `http://localhost:8000/admin/login` (password from your `.env`'s `ADMIN_PASSWORD`), view `/admin` and `/admin/jds/1`. Confirm the JD detail page shows the new stat row, the `<details>` JD-text toggle still expands/collapses correctly, and score badges still render with correct high/mid/low colors. If you have a JD with zero applications, check its empty state renders with the new copy and centered styling.

- [ ] **Step 5: Commit**

```bash
cd "/c/Users/sonim/resume screener" && git add app/templates/admin_dashboard.html app/templates/admin_jd_detail.html app/static/style.css && git commit -m "$(cat <<'EOF'
Polish admin dashboard and JD detail views

Adds a proper empty state for JDs/applications with zero results,
and a compact stat row (company, posted date, application count)
on the JD detail page. No route or query changes.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Final cross-page visual QA pass

**Files:**
- None (verification-only task; may produce small follow-up fixes in `app/static/style.css` or any template if issues are found)

**Interfaces:**
- Consumes: everything from Tasks 1-3.
- Produces: nothing new — this is the acceptance gate for the whole plan.

- [ ] **Step 1: Restart the server clean**

```bash
cd "/c/Users/sonim/resume screener"
netstat -ano | grep :8000 | grep LISTENING
```
Note the PID, then:
```bash
taskkill //PID <pid> //F
cd "/c/Users/sonim/resume screener" && source .venv/Scripts/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
sleep 2 && curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/
```
Expected: `200`.

- [ ] **Step 2: Walk every page at desktop width (Browser pane)**

Navigate to and screenshot each of:
- `http://localhost:8000/` (candidate job list)
- `http://localhost:8000/apply/1` (apply form — substitute a real JD id from the list)
- `http://localhost:8000/admin/login`
- `http://localhost:8000/admin` (after logging in)
- `http://localhost:8000/admin/jds/1` (substitute a real JD id)

For each: confirm no visual overflow, no broken CSS (unstyled raw HTML), consistent spacing with the rest of the app.

- [ ] **Step 3: Walk every page at mobile width**

Use `resize_window` with `preset: "mobile"`, then repeat Step 2's navigation + screenshot for all five URLs. Confirm: topbar nav links don't overlap the brand, forms are full-width and usable, job list items stack, buttons don't overflow their container, score badges wrap sensibly if a resume card is narrow.

Reset with `resize_window` `preset: "desktop"` when done.

- [ ] **Step 4: Full functional smoke test**

Repeat the same end-to-end flow used to validate the original build: post a JD (or reuse existing), submit a resume as a candidate, confirm the generic thank-you page, log into admin, confirm the score/summary/gaps show correctly with the new styling. This confirms polish didn't break any functionality (e.g. the `onclick` submit-button JS from Task 2 didn't prevent the POST from firing).

- [ ] **Step 5: Fix and commit any issues found**

If Steps 2-4 surface a layout bug, fix it directly in `app/static/style.css` or the relevant template, and commit:
```bash
cd "/c/Users/sonim/resume screener" && git add -A && git commit -m "$(cat <<'EOF'
Fix visual QA issues found in frontend polish pass

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```
If no issues are found, no commit is needed for this task — it was verification-only.

---

## Explicitly Out of Scope

- Migrating any part of the stack to Vercel, Next.js, or any JS framework.
- Changing SQLite to Postgres or any other database.
- Adding new routes, new form fields, or new backend logic.
- A CSS framework (Tailwind, Bootstrap) — hand-written CSS only, consistent with the existing codebase.
