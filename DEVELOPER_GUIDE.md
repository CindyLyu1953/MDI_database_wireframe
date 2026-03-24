# Developer Guide

This guide is for collaborators maintaining and deploying the StudyLens Flask app, especially on PythonAnywhere.

---

## 1) Project Overview

StudyLens is a Flask application for searching, reading, and comparing social media deactivation studies.

- Backend: Flask (`app.py`)
- Frontend: Jinja templates + page-specific CSS + inline JavaScript
- Research dataset: CSV in `data/input/`
- Tracking and upload workflow: SQLite in `data/output/tracking.db`
- Admin pages: login, usage analytics, upload request review

Key user flows:
- Search studies and add/remove items in compare list
- Open individual article details with condensed/verbatim toggles
- Compare up to 5 papers side-by-side
- Build a custom comparison by selecting indicators
- Submit upload requests from Profile page

---

## 2) Current Project Structure

```text
database_wireframe/
├── app.py
├── requirements.txt
├── README.md
├── ADMIN_GUIDE.md
├── DEVELOPER_GUIDE.md
├── database/
│   └── init_db.py
├── data/
│   ├── input/          # CSV source data
│   ├── output/         # tracking.db
│   └── user_uploads/   # uploaded PDFs
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── search.html
│   ├── compare.html
│   ├── article.html
│   ├── profile.html
│   ├── database.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── admin_requests.html
└── static/css/
    ├── main.css
    ├── home.css
    ├── search.css
    ├── compare.css
    ├── article.css
    ├── profile.css
    └── database.css
```

---

## 3) Runtime Architecture

### 3.1 App startup

`app.py` is both module and local entrypoint:
- Creates `app = Flask(__name__)`
- Registers Jinja filters (`word_count`, `truncate_words`, `extract_url`)
- Loads CSV data into global `papers_data` at import time (`load_papers_from_csv()`)
- Local run command uses `app.run(..., port=5001)`

Important implication:
- Each WSGI worker loads CSV at startup.
- Citation counts are fetched via Semantic Scholar API when data is loaded.

### 3.2 Data model

There is no ORM. Core data stores:

1) **CSV papers dataset** (`data/input/...`)
- Accepts first existing file among:
  - `paper_extracted.csv`
  - `papers_extracted.csv`
  - `papers.csv`

2) **SQLite tracking DB** (`data/output/tracking.db`)
- Tables:
  - `search_logs`
  - `compare_view_logs`
  - `download_logs`
  - `upload_requests`

3) **Uploaded files**
- PDFs saved in `data/user_uploads/`
- Admin-only download route: `/uploads/<filename>`

### 3.3 Frontend architecture

- `base.html` provides shared layout (header/nav/footer).
- Most pages extend `base.html`.
- `article.html` is currently standalone (does not extend `base.html`).
- JS is embedded in templates (no separate `static/js` folder yet).

State handling:
- `localStorage`: comparison IDs, favorites, saved comparisons, profile draft data
- `sessionStorage`: lightweight session ID on home page
- Flask session: admin auth state

---

## 4) Route Map (High-Level)

### Pages
- `/` -> home
- `/search`
- `/article/<paper_id>`
- `/compare`
- `/profile`
- `/database`

### Public API
- `/api/papers`
- `/api/search`
- `/api/paper/<paper_id>`
- `/api/statistics`
- `/api/tracking/stats`
- `/api/track/search` (POST)
- `/api/track/compare_view` (POST)
- `/api/track/download` (POST)
- `/api/upload-request` (POST)
- `/api/my-requests`

### Admin
- `/admin/login` (GET/POST)
- `/admin/logout`
- `/admin/dashboard`
- `/admin/requests`
- `/api/admin/search_logs`
- `/api/admin/compare_view_logs`
- `/api/admin/download_logs`
- `/api/admin/stats`
- `/api/admin/requests`
- `/api/admin/requests/<id>/status` (POST)

Security note:
- `/api/admin/refresh-citations` currently has no admin guard and should be protected before public deployment.

---

## 5) Local Development

### 5.1 Setup

```bash
cd database_wireframe
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install requests
python database/init_db.py
```

Why install `requests` manually?
- `app.py` imports and uses `requests`, but it is currently not pinned in `requirements.txt`.

### 5.2 Run

```bash
python app.py
```

Default local URL:
- `http://127.0.0.1:5001`

If port is busy:
```bash
lsof -i :5001
kill <PID>
```

---

## 6) PythonAnywhere Deployment Guide

This is the most important section for collaborators.

### 6.1 Create environment

In a PythonAnywhere Bash console:

```bash
cd ~
git clone <your-repo-url> database_wireframe
cd database_wireframe
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install requests
python database/init_db.py
```

### 6.2 Ensure required files exist

- CSV exists in `data/input/` with one supported name.
- `data/output/tracking.db` exists (created by init script).
- `data/user_uploads/` exists and is writable.

### 6.3 Configure PythonAnywhere web app

1. In the **Web** tab, set source code path to your project.
2. Set virtualenv path to `.../database_wireframe/.venv`.
3. Add static mapping:
   - URL: `/static/`
   - Directory: `/home/<username>/database_wireframe/static/`

### 6.4 WSGI file

Edit your WSGI config and import the Flask app object:

```python
import sys
path = '/home/<username>/database_wireframe'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

Then reload the web app from the Web tab.

### 6.5 Critical deployment caveat (paths)

Some file paths in `app.py` are currently relative (`os.path.join("data", ...)`), so app behavior depends on process working directory.

For stability on PythonAnywhere, ensure:
- the app runs with project root as working directory, or
- refactor path usage to always build from `BASE_DIR`.

Recommended future hardening:
- Replace all relative DB/CSV/upload paths with `BASE_DIR / ...`.

---

## 7) Configuration Checklist Before Production

Must do:
- Change `app.secret_key` to a strong secret.
- Move admin credentials (`ADMIN_USERNAME`, `ADMIN_PASSWORD`) to environment variables.
- Protect `/api/admin/refresh-citations` with admin auth.
- Add `requests` to `requirements.txt`.

Should do:
- Add structured logging.
- Add error pages for 404/500.
- Add backup strategy for `tracking.db` and `data/user_uploads/`.

---

## 8) Data + Content Maintenance

### Add new papers
1. Update CSV in `data/input/`.
2. Keep column naming conventions (`feature`, `feature_verbatim`).
3. Use `NOT SPECIFIED` for unavailable fields.
4. Restart app workers so `papers_data` reloads.

### Handle upload requests
1. Review in `/admin/requests`.
2. Download uploaded PDFs via admin route.
3. Run external extraction pipeline.
4. Append processed rows to input CSV.
5. Mark request status approved/rejected.

---

## 9) Frontend Notes for Collaborators

- Compare page now includes:
  - left subtitle navigation
  - custom comparison mode with indicator multi-select
  - section-level select/deselect controls
  - expandable selected indicator tags (`+N more`)

- Search page compare button state is persisted in `localStorage`.
- Profile page is heavily localStorage-driven and reads tracking stats from API.

If UI changes seem missing after deployment:
- hard-refresh browser cache
- verify static file mapping
- reload PythonAnywhere web app

---

## 10) Troubleshooting (PythonAnywhere-focused)

### A) App boots but shows no papers
- Confirm CSV exists in `data/input/`.
- Confirm filename is one of the supported names.
- Check web app error log for CSV read errors.

### B) 500 errors on tracking/upload endpoints
- Confirm `tracking.db` exists and tables were initialized.
- Confirm process can write to `data/output/` and `data/user_uploads/`.

### C) CSS/JS updates not visible
- Hard refresh browser.
- Verify `/static/` mapping points to the correct directory.
- Reload web app.

### D) Admin login works locally but not on server
- Confirm session secret and cookie/domain settings.
- Ensure no stale old workers are running after credential changes.

### E) Citation refresh or startup delays
- Semantic Scholar API calls can be slow/rate-limited.
- Consider background jobs or cached citation updates in future iterations.

---

## 11) Immediate TODOs (Recommended)

1. Add `requests` to `requirements.txt`.
2. Move secrets/credentials to env vars.
3. Refactor all data paths to `BASE_DIR`.
4. Guard `/api/admin/refresh-citations` with `@require_admin`.
5. Optionally convert `article.html` to extend `base.html` for consistency.

---

If you are deploying to PythonAnywhere for the first time, follow sections **6** and **7** exactly in order.
