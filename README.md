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

## Deployment boundary

GitHub stores and versions this source code. GitHub Pages can serve static files, but it cannot run this FastAPI backend. A live, connected demo needs a separate application host and a persistent database strategy.

The current demo API has no authentication and permits public writes if exposed directly. Before connecting a public host, add an appropriate access control or read-only demo mode, move away from local SQLite for persistent multi-user use, configure secrets and HTTPS, and complete a security review. Never deploy real grievance records in this demo.

## SIH submission notes

- Confirm the official SIH edition and exact wording for SIH26264 before submission. The project folder currently contains a 2026 SIH template; verify the problem ID against the official portal.
- Replace team placeholders in the presentation and source materials before publishing them.
- Do not present the app as an operational AICTE system or claim that the proposed security controls are already implemented.
