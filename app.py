"""
Web Application Backend for Student Result Management System.
Built with FastAPI to deliver a responsive, interactive web dashboard.
Directly uses the computational engine in core/result_engine.py.
"""

import os
import sys
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
    save_individual_report_card,
)
from core.visualizer import generate_all_charts

DATA_FILE = os.path.join(BASE_DIR, "data", "students.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
CHARTS_DIR = os.path.join(BASE_DIR, "data", "charts")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure charts directory exists
def get_charts_dir():
    if os.environ.get("VERCEL") or not os.access(CHARTS_DIR if os.path.exists(CHARTS_DIR) else BASE_DIR, os.W_OK):
        tmp_charts = "/tmp/charts"
        os.makedirs(tmp_charts, exist_ok=True)
        if os.path.exists(CHARTS_DIR):
            import shutil
            for f in os.listdir(CHARTS_DIR):
                src = os.path.join(CHARTS_DIR, f)
                dst = os.path.join(tmp_charts, f)
                if os.path.isfile(src) and not os.path.exists(dst):
                    try:
                        shutil.copyfile(src, dst)
                    except Exception:
                        pass
        return tmp_charts
    os.makedirs(CHARTS_DIR, exist_ok=True)
    return CHARTS_DIR

app = FastAPI(title="Student Result Management System API")

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/charts/{filename}")
def serve_chart(filename: str):
    """Serves charts from writable runtime directory or local bundle."""
    target = os.path.join(get_charts_dir(), filename)
    if os.path.exists(target):
        return FileResponse(target, media_type="image/png")
    fallback = os.path.join(CHARTS_DIR, filename)
    if os.path.exists(fallback):
        return FileResponse(fallback, media_type="image/png")
    raise HTTPException(status_code=404, detail="Chart not found")


class StudentInput(BaseModel):
    roll_no: str = Field(..., example="S26CSEU1920")
    name: str = Field(..., example="Rohit Verma")
    marks: Dict[str, float]


@app.get("/")
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/meta")
def get_metadata():
    """Returns subjects, grade scales, and team information."""
    return {
        "course": "Computational Thinking and Programming",
        "course_code": "2026CSAE100",
        "project_title": "Student Result Management System",
        "subjects": list(SUBJECTS),
        "grade_scale": [{"min": g[0], "grade": g[1], "gpa": g[2], "desc": g[3]} for g in GRADE_SCALE],
        "team": [
            {"name": "Prisha Mishra", "roll": "S26CSEU1899", "role": "Research & Python Concept Analysis"},
            {"name": "Kinjal Kadiyan", "roll": "S26CSEU1905", "role": "Research & Project Planning"},
            {"name": "Arnav Mittal", "roll": "S26CSEU1901", "role": "Input & Data Management"},
            {"name": "Payal Kansal", "roll": "S26CSEU1907", "role": "Testing & Error Checking"},
            {"name": "Jishnu Priya Hasini", "roll": "S26CSEU1887", "role": "Documentation & Presentation"},
        ]
    }


@app.get("/api/students")
def get_students():
    """Returns all students sorted by rank."""
    students = load_students_from_csv(DATA_FILE)
    return {"students": students}


@app.post("/api/students")
def add_student(data: StudentInput):
    """Registers a new student record with computational validation."""
    students = load_students_from_csv(DATA_FILE)

    # Check for duplicate roll number
    clean_roll = data.roll_no.strip().upper()
    if any(s["roll_no"] == clean_roll for s in students):
        raise HTTPException(status_code=400, detail=f"Roll number '{clean_roll}' already exists.")

    try:
        new_record = process_student_record(clean_roll, data.name, data.marks)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    students.append(new_record)
    students = compute_class_rankings(students)
    save_students_to_csv(students, DATA_FILE)

    # Refresh charts in background
    stats = compute_class_statistics(students)
    generate_all_charts(students, stats, get_charts_dir())

    # Find the newly added student's updated record with its assigned rank
    created = next((s for s in students if s["roll_no"] == clean_roll), new_record)
    return {"message": "Student record created successfully", "student": created}


@app.delete("/api/students/{roll_no}")
def delete_student(roll_no: str):
    """Deletes a student record and recalculates ranks."""
    clean_roll = roll_no.strip().upper()
    students = load_students_from_csv(DATA_FILE)

    initial_len = len(students)
    students = [s for s in students if s["roll_no"] != clean_roll]

    if len(students) == initial_len:
        raise HTTPException(status_code=404, detail=f"Student '{clean_roll}' not found.")

    students = compute_class_rankings(students)
    save_students_to_csv(students, DATA_FILE)

    stats = compute_class_statistics(students)
    generate_all_charts(students, stats, get_charts_dir())

    return {"message": f"Student '{clean_roll}' deleted successfully."}


@app.get("/api/students/{roll_no}/report")
def get_student_report(roll_no: str):
    """Generates individual student report card with rule-based recommendations."""
    clean_roll = roll_no.strip().upper()
    students = load_students_from_csv(DATA_FILE)
    student = next((s for s in students if s["roll_no"] == clean_roll), None)

    if not student:
        raise HTTPException(status_code=404, detail=f"Student '{clean_roll}' not found.")

    stats = compute_class_statistics(students)
    recommendations = generate_academic_recommendations(student, stats)
    raw_ascii = generate_text_report_card(student, stats)

    return {
        "student": student,
        "recommendations": recommendations,
        "ascii_report": raw_ascii,
    }


@app.get("/api/analytics")
def get_analytics():
    """Computes and returns class-wide performance analytics & charts."""
    students = load_students_from_csv(DATA_FILE)
    stats = compute_class_statistics(students)
    generate_all_charts(students, stats, get_charts_dir())
    return stats


@app.get("/api/export/csv")
def export_csv():
    """Download the latest CSV file."""
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Data file not found.")
    return FileResponse(
        DATA_FILE,
        media_type="text/csv",
        filename="student_results_export.csv"
    )


if __name__ == "__main__":
    import uvicorn
    # Generate initial charts
    studs = load_students_from_csv(DATA_FILE)
    st = compute_class_statistics(studs)
    generate_all_charts(studs, st, CHARTS_DIR)

    print("\nStarting Student Result Management System Web Server...")
    print("Open your browser at: http://127.0.0.1:8000\n")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
