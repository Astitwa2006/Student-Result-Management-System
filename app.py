"""
Web Application Backend – Student Result Management System.
FastAPI backend deployed on Render (backend) with Vercel (frontend).

Architecture:
  - Render (this file): REST API + CSV data storage + chart generation
  - Vercel (public/):   Static HTML/CSS/JS dashboard

Locally: run with `uvicorn app:app --reload` then open http://127.0.0.1:8000
"""

# ---------------------------------------------------------------------------
# CRITICAL: Set writable dirs BEFORE any import that touches the filesystem.
# matplotlib builds a font cache on first run. On fresh servers (Render) this
# can take 60+ seconds and blocks the entire event loop if not redirected to /tmp.
# ---------------------------------------------------------------------------
import os
import sys

os.makedirs("/tmp/matplotlib", exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import threading
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.result_engine import (
    SUBJECTS,
    GRADE_SCALE,
    load_students_from_csv,
    save_students_to_csv,
    process_student_record,
    compute_class_rankings,
    compute_class_statistics,
    generate_academic_recommendations,
    generate_text_report_card,
)

# ---------------------------------------------------------------------------
# Directory constants
# ---------------------------------------------------------------------------
DATA_FILE  = os.path.join(BASE_DIR, "data", "students.csv")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CHARTS_DIR = os.path.join(BASE_DIR, "data", "charts")

IS_RENDER = bool(os.environ.get("RENDER"))
IS_VERCEL = bool(os.environ.get("VERCEL"))


def get_charts_dir() -> str:
    """Return writable charts directory. Uses /tmp on cloud environments."""
    if IS_RENDER or IS_VERCEL:
        d = "/tmp/charts"
        os.makedirs(d, exist_ok=True)
        return d
    os.makedirs(CHARTS_DIR, exist_ok=True)
    return CHARTS_DIR


def _generate_charts_background():
    """
    Generate charts in a background thread so startup is non-blocking.
    matplotlib's font-cache build can take 30-60 s on a fresh server —
    running it in a thread keeps the event loop (and all HTTP requests) live.
    """
    try:
        # Import here (inside thread) so the font-cache build doesn't block startup
        from core.visualizer import generate_all_charts
        students = load_students_from_csv(DATA_FILE)
        if students:
            stats = compute_class_statistics(students)
            generate_all_charts(students, stats, get_charts_dir())
            print(f"[charts] Generated for {len(students)} students.", flush=True)
    except Exception as exc:
        print(f"[charts] Background generation warning: {exc}", flush=True)


# ---------------------------------------------------------------------------
# Startup — non-blocking chart generation
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Fast startup: verify data, kick off chart generation in background."""
    try:
        students = load_students_from_csv(DATA_FILE)
        print(f"[startup] Ready — {len(students)} students in CSV.", flush=True)
    except Exception as exc:
        print(f"[startup] Data warning: {exc}", flush=True)

    # Kick off chart generation without blocking the event loop
    t = threading.Thread(target=_generate_charts_background, daemon=True)
    t.start()

    yield  # App is live and serving requests while charts build in background


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Student Result Management System API",
    description=(
        "Python computational backend for the Student Result Management System. "
        "Course: Computational Thinking and Programming (2026CSAE100)."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Vercel frontend and local dev to call this backend
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Open for college project; restrict to Vercel domain in production
    allow_credentials=False,       # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)

# ---------------------------------------------------------------------------
# Serve static files for LOCAL development convenience
# (On Render/Vercel, Vercel serves the frontend — this is a local fallback only)
# ---------------------------------------------------------------------------
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static-files")


# ---------------------------------------------------------------------------
# Pydantic model
# ---------------------------------------------------------------------------
class StudentInput(BaseModel):
    roll_no: str = Field(..., example="S26CSEU1920")
    name:    str = Field(..., example="Rohit Verma")
    marks:   Dict[str, float]


# ===========================================================================
# API Routes
# ===========================================================================

@app.get("/", include_in_schema=False)
def serve_index():
    """Serve frontend HTML for local development."""
    for candidate in [
        os.path.join(PUBLIC_DIR, "index.html"),
        os.path.join(STATIC_DIR, "index.html"),
    ]:
        if os.path.exists(candidate):
            return FileResponse(candidate)
    return JSONResponse({
        "message": "Student Result Management System API",
        "docs": "/docs",
        "health": "/api/health",
    })


@app.get("/api/health")
def health_check():
    """Health-check endpoint for Render uptime monitoring."""
    students = load_students_from_csv(DATA_FILE)
    return {
        "status": "ok",
        "service": "Student Result Management System",
        "version": "2.0.0",
        "students_loaded": len(students),
    }


@app.get("/api/meta")
def get_metadata():
    """Returns subjects, grade scale, and team details."""
    return {
        "course":        "Computational Thinking and Programming",
        "course_code":   "2026CSAE100",
        "project_title": "Student Result Management System",
        "subjects":      list(SUBJECTS),
        "grade_scale":   [
            {"min": g[0], "grade": g[1], "gpa": g[2], "desc": g[3]}
            for g in GRADE_SCALE
        ],
        "team": [
            {"name": "Prisha Mishra",       "roll": "S26CSEU1899", "role": "Research & Python Concept Analysis"},
            {"name": "Kinjal Kadiyan",      "roll": "S26CSEU1905", "role": "Research & Project Planning"},
            {"name": "Arnav Mittal",        "roll": "S26CSEU1901", "role": "Input & Data Management"},
            {"name": "Payal Kansal",        "roll": "S26CSEU1907", "role": "Testing & Error Checking"},
            {"name": "Jishnu Priya Hasini", "roll": "S26CSEU1887", "role": "Documentation & Presentation"},
        ],
    }


@app.get("/api/students")
def get_students():
    """Returns all student records sorted by rank."""
    students = load_students_from_csv(DATA_FILE)
    return {"students": students}


@app.post("/api/students", status_code=201)
def add_student(data: StudentInput):
    """Registers a new student with computational validation and rank recalculation."""
    students  = load_students_from_csv(DATA_FILE)
    clean_roll = data.roll_no.strip().upper()

    if any(s["roll_no"] == clean_roll for s in students):
        raise HTTPException(status_code=400, detail=f"Roll number '{clean_roll}' already exists.")

    try:
        new_record = process_student_record(clean_roll, data.name, data.marks)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    students.append(new_record)
    students = compute_class_rankings(students)
    save_students_to_csv(students, DATA_FILE)

    # Regenerate charts in background after data change
    threading.Thread(target=_generate_charts_background, daemon=True).start()

    created = next((s for s in students if s["roll_no"] == clean_roll), new_record)
    return {"message": "Student record created successfully.", "student": created}


@app.delete("/api/students/{roll_no}")
def delete_student(roll_no: str):
    """Deletes a student record and recalculates class rankings."""
    clean_roll = roll_no.strip().upper()
    students   = load_students_from_csv(DATA_FILE)
    initial    = len(students)
    students   = [s for s in students if s["roll_no"] != clean_roll]

    if len(students) == initial:
        raise HTTPException(status_code=404, detail=f"Student '{clean_roll}' not found.")

    students = compute_class_rankings(students)
    save_students_to_csv(students, DATA_FILE)
    threading.Thread(target=_generate_charts_background, daemon=True).start()

    return {"message": f"Student '{clean_roll}' deleted. Rankings recalculated."}


@app.get("/api/students/{roll_no}/report")
def get_student_report(roll_no: str):
    """Generates an individual student report with rule-based recommendations."""
    clean_roll = roll_no.strip().upper()
    students   = load_students_from_csv(DATA_FILE)
    student    = next((s for s in students if s["roll_no"] == clean_roll), None)

    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{clean_roll}' not found.")

    stats           = compute_class_statistics(students)
    recommendations = generate_academic_recommendations(student, stats)
    ascii_report    = generate_text_report_card(student, stats)

    return {
        "student":         student,
        "recommendations": recommendations,
        "ascii_report":    ascii_report,
    }


@app.get("/api/analytics")
def get_analytics():
    """Computes class-wide analytics and triggers chart regeneration."""
    students = load_students_from_csv(DATA_FILE)
    stats    = compute_class_statistics(students)
    # Regenerate charts in background (non-blocking)
    threading.Thread(target=_generate_charts_background, daemon=True).start()
    return stats


@app.get("/api/export/csv")
def export_csv():
    """Downloads the latest student records as a CSV file."""
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Data file not found.")
    return FileResponse(
        DATA_FILE,
        media_type="text/csv",
        filename="student_results_export.csv",
    )


@app.get("/charts/{filename}")
def serve_chart(filename: str):
    """Serves generated chart PNG files."""
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    for directory in [get_charts_dir(), CHARTS_DIR]:
        path = os.path.join(directory, filename)
        if os.path.exists(path):
            return FileResponse(path, media_type="image/png")

    raise HTTPException(status_code=404, detail=f"Chart '{filename}' not yet generated. Call /api/analytics first.")


# ---------------------------------------------------------------------------
# Local dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("  Student Result Management System — Local Server")
    print("  Open: http://127.0.0.1:8000")
    print("  API Docs: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
