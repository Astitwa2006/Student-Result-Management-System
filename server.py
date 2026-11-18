"""
Zero-Dependency Fallback Web Server for Student Result Management System.
Uses Python's standard library `http.server` and `json` modules.
Runs on ANY standard Python 3.x installation with NO pip dependencies required!
"""

import json
import os
import sys
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

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
)

DATA_FILE = os.path.join(BASE_DIR, "data", "students.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "data", "charts")
STATIC_DIR = os.path.join(BASE_DIR, "static")


class ResultSystemHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data, status=HTTPStatus.OK):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Static charts
        if path.startswith("/charts/"):
            chart_file = os.path.join(CHARTS_DIR, os.path.basename(path))
            if os.path.exists(chart_file):
                with open(chart_file, "rb") as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return

        # API Endpoints
        if path == "/api/meta":
            meta = {
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
            self._send_json(meta)
            return

        if path == "/api/students":
            students = load_students_from_csv(DATA_FILE)
            self._send_json({"students": students})
            return

        if path.startswith("/api/students/") and path.endswith("/report"):
            parts = path.strip("/").split("/")
            roll = parts[2].upper()
            students = load_students_from_csv(DATA_FILE)
            target = next((s for s in students if s["roll_no"] == roll), None)
            if not target:
                self._send_json({"error": "Student not found"}, HTTPStatus.NOT_FOUND)
                return

            stats = compute_class_statistics(students)
            recs = generate_academic_recommendations(target, stats)
            raw = generate_text_report_card(target, stats)
            self._send_json({
                "student": target,
                "recommendations": recs,
                "ascii_report": raw
            })
            return

        if path == "/api/analytics":
            students = load_students_from_csv(DATA_FILE)
            stats = compute_class_statistics(students)
            self._send_json(stats)
            return

        if path == "/api/export/csv":
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "rb") as f:
                    content = f.read()
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Disposition", "attachment; filename=students_export.csv")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
                return

        # Default fallback to static file server (serves index.html, style.css, app.js)
        if path.startswith("/static/"):
            self.path = path[7:]  # strip leading /static to match STATIC_DIR root
        elif path == "/" or path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/students":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            try:
                data = json.loads(post_body.decode("utf-8"))
                roll = data.get("roll_no", "").strip().upper()
                name = data.get("name", "").strip()
                marks = data.get("marks", {})

                students = load_students_from_csv(DATA_FILE)
                if any(s["roll_no"] == roll for s in students):
                    self._send_json({"detail": f"Roll number '{roll}' already exists."}, HTTPStatus.BAD_REQUEST)
                    return

                new_record = process_student_record(roll, name, marks)
                students.append(new_record)
                students = compute_class_rankings(students)
                save_students_to_csv(students, DATA_FILE)

                # Try generating charts if matplotlib is present
                try:
                    from core.visualizer import generate_all_charts
                    stats = compute_class_statistics(students)
                    generate_all_charts(students, stats, CHARTS_DIR)
                except Exception:
                    pass

                self._send_json({"message": "Student created", "student": new_record}, HTTPStatus.CREATED)
            except Exception as e:
                self._send_json({"detail": str(e)}, HTTPStatus.UNPROCESSABLE_ENTITY)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/students/"):
            roll = parsed.path.split("/")[-1].upper()
            students = load_students_from_csv(DATA_FILE)
            initial_len = len(students)
            students = [s for s in students if s["roll_no"] != roll]

            if len(students) == initial_len:
                self._send_json({"detail": f"Student '{roll}' not found."}, HTTPStatus.NOT_FOUND)
                return

            students = compute_class_rankings(students)
            save_students_to_csv(students, DATA_FILE)

            try:
                from core.visualizer import generate_all_charts
                stats = compute_class_statistics(students)
                generate_all_charts(students, stats, CHARTS_DIR)
            except Exception:
                pass

            self._send_json({"message": f"Student '{roll}' deleted successfully."})
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def run_standalone_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, ResultSystemHandler)
    print(f"\n==================================================================")
    print(f" Standalone Result System Web Server running at: http://127.0.0.1:{port}")
    print(f" Zero external dependencies required - standard library only!")
    print(f" Press Ctrl+C to stop.")
    print(f"==================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_standalone_server(port)
