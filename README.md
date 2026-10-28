# AICTE Grievance Tracker

An independent concept application for the SIH problem statement **SIH26264: Integrated Dashboard for Monitoring and Tracking Institution-Related Complaint Cases Across AICTE Bureaus/Cells**. It demonstrates an institution-centred grievance dashboard and basic complaint workflows using synthetic sample records.

> This is not an official AICTE service. The sample records are fictional. Do not enter real student, staff, institution, or complaint data. Authentication, authorization, privacy controls, and production deployment approvals are not implemented in this demo.

## What it demonstrates

- Dashboard counts for open, in-progress, resolved, escalated, and overdue cases
- Search and status filtering across complaint records
- Complaint creation, detail view, status update, and deletion
- CSV export of the currently loaded sample records
- FastAPI JSON endpoints backed by a local SQLite database
- Responsive dashboard served by the same FastAPI application

## Technology

- **Web interface:** HTML, CSS, and JavaScript, served from `static/`
- **API:** Python and FastAPI with Pydantic request validation
- **Storage:** SQLite for a local demonstration; not configured for reliable public production hosting
- **Server:** Uvicorn

## Run locally

Use Python 3.10 or newer. From the project directory in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>. The API health check is at <http://127.0.0.1:8000/api/health>, and the interactive API schema is at <http://127.0.0.1:8000/docs>.

The app creates `resolveiq.db` locally and seeds fictional examples when the database has no complaints. The database is intentionally excluded from Git.

## API overview

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service health |
| `GET` | `/api/dashboard` | Dashboard summary and category counts |
| `GET` | `/api/complaints` | List and filter complaints |
| `POST` | `/api/complaints` | Create a complaint record |
| `GET` | `/api/complaints/{id}` | Read one complaint |
| `PATCH` | `/api/complaints/{id}` | Update complaint fields |
| `DELETE` | `/api/complaints/{id}` | Delete a complaint record |

## GitHub Pages demo

The `docs/` folder contains a standalone browser-only version of the dashboard. It stores fictional demo cases in the visitor's browser. The FastAPI API is not used by that Pages site, and demo edits do not sync between visitors.

The included GitHub Actions workflow publishes `docs/` to GitHub Pages when changes reach `main`. In the GitHub repository, open **Settings → Pages** and set **Source** to **GitHub Actions**. GitHub Pages sites are publicly available on the internet, so the site clearly identifies itself as an independent concept demonstration and contains no real grievance records.

GitHub Pages serves static files and cannot run the FastAPI backend. To host the connected API, use a separate application host and persistent database. The current FastAPI API has no authentication and permits public writes if exposed directly; do not expose it publicly until access controls or a read-only mode, persistent storage, secrets handling, HTTPS, and a security review are in place.

## SIH submission notes

- Confirm the official SIH edition and exact wording for SIH26264 before submission. The project folder currently contains a 2026 SIH template; verify the problem ID against the official portal.
- Replace team placeholders in the presentation and source materials before publishing them.
- Do not present the app as an operational AICTE system or claim that the proposed security controls are already implemented.
