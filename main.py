from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
DB_PATH = ROOT / "resolveiq.db"
STATUSES = ("Open", "In Progress", "Resolved", "Escalated")


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialize():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL,
            priority TEXT NOT NULL, status TEXT NOT NULL, student TEXT NOT NULL,
            institution TEXT NOT NULL, assigned_to TEXT NOT NULL DEFAULT 'Unassigned',
            created_at TEXT NOT NULL, due_date TEXT NOT NULL
        )""")
        if db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0] == 0:
            now = date.today()
            examples = [
                ("Scholarship payment delayed", "Post-matric scholarship has not been credited for two months.", "Scholarship", "High", "Open", "Aarav Sharma", "North Valley Institute", "Priya Nair", now-timedelta(days=4), now+timedelta(days=3)),
                ("Hostel water supply issue", "No running water in the east wing for three days.", "Infrastructure", "Medium", "In Progress", "Meera Joshi", "Central Tech College", "Rohan Das", now-timedelta(days=2), now+timedelta(days=5)),
                ("Exam fee charged twice", "Payment portal shows two successful deductions for one exam form.", "Fees", "High", "Escalated", "Kabir Patel", "Lakeside Engineering", "Priya Nair", now-timedelta(days=9), now-timedelta(days=2)),
                ("Accessible lab equipment request", "Request for screen reader support in the computer lab.", "Accessibility", "Medium", "Resolved", "Ananya Roy", "Metro Polytechnic", "Sana Khan", now-timedelta(days=12), now-timedelta(days=5)),
                ("Faculty conduct concern", "Requesting review of repeated inappropriate classroom comments.", "Conduct", "Urgent", "Open", "Student representative", "Western Arts University", "Sana Khan", now-timedelta(days=1), now+timedelta(days=1)),
            ]
            db.executemany("INSERT INTO complaints(title,description,category,priority,status,student,institution,assigned_to,created_at,due_date) VALUES(?,?,?,?,?,?,?,?,?,?)", [(*e[:8], e[8].isoformat(), e[9].isoformat()) for e in examples])


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title="AICTE Grievance Tracker API", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class ComplaintIn(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=5, max_length=4000)
    category: str = Field(min_length=2, max_length=80)
    priority: Literal["Low", "Medium", "High", "Urgent"] = "Medium"
    status: Literal["Open", "In Progress", "Resolved", "Escalated"] = "Open"
    student: str = Field(min_length=2, max_length=120)
    institution: str = Field(min_length=2, max_length=160)
    assigned_to: str = "Unassigned"
    due_date: date


class ComplaintUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, min_length=5, max_length=4000)
    category: str | None = None
    priority: Literal["Low", "Medium", "High", "Urgent"] | None = None
    status: Literal["Open", "In Progress", "Resolved", "Escalated"] | None = None
    student: str | None = None
    institution: str | None = None
    assigned_to: str | None = None
    due_date: date | None = None


def serialize(row):
    item = dict(row)
    item["overdue"] = item["status"] != "Resolved" and item["due_date"] < date.today().isoformat()
    return item


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "AICTE Grievance Tracker API"}


@app.get("/api/complaints")
def list_complaints(status: str | None = None, search: str | None = None, limit: int = Query(200, ge=1, le=500)):
    sql, values = "SELECT * FROM complaints WHERE 1=1", []
    if status and status != "All":
        sql += " AND status=?"; values.append(status)
    if search:
        sql += " AND (title LIKE ? OR student LIKE ? OR institution LIKE ? OR category LIKE ?)"
        values.extend([f"%{search}%"] * 4)
    sql += " ORDER BY created_at DESC, id DESC LIMIT ?"; values.append(limit)
    with connect() as db:
        return [serialize(row) for row in db.execute(sql, values)]


@app.post("/api/complaints", status_code=201)
def create_complaint(payload: ComplaintIn):
    data = payload.model_dump()
    data["due_date"] = data["due_date"].isoformat()
    data["created_at"] = datetime.now(timezone.utc).date().isoformat()
    with connect() as db:
        cur = db.execute("INSERT INTO complaints(title,description,category,priority,status,student,institution,assigned_to,due_date,created_at) VALUES(:title,:description,:category,:priority,:status,:student,:institution,:assigned_to,:due_date,:created_at)", data)
        return serialize(db.execute("SELECT * FROM complaints WHERE id=?", (cur.lastrowid,)).fetchone())


@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM complaints WHERE id=?", (complaint_id,)).fetchone()
    if not row: raise HTTPException(404, "Complaint not found")
    return serialize(row)


@app.patch("/api/complaints/{complaint_id}")
def update_complaint(complaint_id: int, payload: ComplaintUpdate):
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not changes: raise HTTPException(400, "Provide at least one field to update")
    for key, value in changes.items():
        if isinstance(value, date): changes[key] = value.isoformat()
    with connect() as db:
        exists = db.execute("SELECT id FROM complaints WHERE id=?", (complaint_id,)).fetchone()
        if not exists: raise HTTPException(404, "Complaint not found")
        assignments = ",".join(f"{key}=?" for key in changes)
        db.execute(f"UPDATE complaints SET {assignments} WHERE id=?", [*changes.values(), complaint_id])
        return serialize(db.execute("SELECT * FROM complaints WHERE id=?", (complaint_id,)).fetchone())


@app.delete("/api/complaints/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: int):
    with connect() as db:
        cur = db.execute("DELETE FROM complaints WHERE id=?", (complaint_id,))
        if cur.rowcount == 0: raise HTTPException(404, "Complaint not found")


@app.get("/api/dashboard")
def dashboard():
    with connect() as db:
        items = [serialize(r) for r in db.execute("SELECT * FROM complaints")]
    counts = {status: sum(c["status"] == status for c in items) for status in STATUSES}
    cats = {}
    for c in items: cats[c["category"]] = cats.get(c["category"], 0) + 1
    return {"total": len(items), "open": counts["Open"], "in_progress": counts["In Progress"], "resolved": counts["Resolved"], "escalated": counts["Escalated"], "overdue": sum(c["overdue"] for c in items), "by_status": counts, "by_category": cats, "recent": sorted(items, key=lambda c: (c["created_at"], c["id"]), reverse=True)[:5]}


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")
