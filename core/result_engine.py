"""
Core Computational Engine for Student Result Management System.
Demonstrates computational thinking, structured functions, data structures
(Lists, Tuples, Dictionaries, Sets), CSV file handling, and rule-based diagnostics.
"""

import csv
import math
import os
from typing import Dict, List, Tuple, Set, Any, Optional

# Default subjects for the academic term
SUBJECTS: Tuple[str, ...] = (
    "Python Programming",
    "Mathematics",
    "Digital Electronics",
    "Physics",
    "Professional Communication",
)

# Grade scale: Tuple of (Minimum Percentage, Letter Grade, Grade Point, Description)
# Tuples are used because grade thresholds are immutable constants.
GRADE_SCALE: Tuple[Tuple[float, str, float, str], ...] = (
    (90.0, "A+", 10.0, "Outstanding"),
    (80.0, "A", 9.0, "Excellent"),
    (70.0, "B+", 8.0, "Very Good"),
    (60.0, "B", 7.0, "Good"),
    (50.0, "C", 6.0, "Average"),
    (40.0, "D", 5.0, "Pass"),
    (0.0, "F", 0.0, "Fail"),
)

PASSING_PERCENTAGE: float = 40.0
SUBJECT_PASS_MARK: float = 40.0


def validate_marks(marks: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validates mark dictionary:
    - Must contain numbers
    - Must be between 0 and 100
    - Must cover required subjects
    Returns: (is_valid, error_message)
    """
    for sub in SUBJECTS:
        if sub not in marks:
            return False, f"Missing marks for subject: {sub}"
        val = marks[sub]
        if not isinstance(val, (int, float)):
            return False, f"Marks for {sub} must be a number, got {type(val).__name__}"
        if val < 0 or val > 100:
            return False, f"Marks for {sub} must be between 0 and 100, got {val}"
    return True, ""


def calculate_grade(percentage: float) -> Tuple[str, float, str]:
    """
    Determines grade, grade point, and description using the immutable GRADE_SCALE tuple.
    """
    for min_pct, grade, gpa, desc in GRADE_SCALE:
        if percentage >= min_pct:
            return grade, gpa, desc
    return "F", 0.0, "Fail"


def process_student_record(
    roll_no: str,
    name: str,
    marks: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculates total, percentage, grade, passing status, and failed subjects.
    Uses Dictionary data structure to return a structured student record.
    """
    valid, err = validate_marks(marks)
    if not valid:
        raise ValueError(err)

    total_marks = round(sum(marks[sub] for sub in SUBJECTS), 2)
    max_marks = len(SUBJECTS) * 100
    percentage = round((total_marks / max_marks) * 100, 2)
    grade, gpa, grade_desc = calculate_grade(percentage)

    # Use a set to identify subjects where marks are below passing threshold
    failed_subjects: Set[str] = {
        sub for sub, mark in marks.items() if mark < SUBJECT_PASS_MARK
    }

    # Pass status requires overall >= 40% and zero failed subjects
    is_passed = (percentage >= PASSING_PERCENTAGE) and (len(failed_subjects) == 0)
    status = "PASS" if is_passed else "FAIL"

    return {
        "roll_no": str(roll_no).strip().upper(),
        "name": str(name).strip(),
        "marks": {sub: round(float(marks[sub]), 2) for sub in SUBJECTS},
        "total": total_marks,
        "max_total": max_marks,
        "percentage": percentage,
        "grade": grade,
        "gpa": gpa,
        "grade_desc": grade_desc,
        "status": status,
        "failed_subjects": list(failed_subjects),
        "rank": 0,  # Computed at class level
        "percentile": 0.0,  # Computed at class level
    }


def compute_class_rankings(students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computational Feature: Computes class ranks and percentiles.
    Handles tied scores fairly (competition ranking: 1, 2, 2, 4...).
    Calculates statistical percentile rank for each student.
    """
    if not students:
        return []

    # Sort students by percentage descending; break ties by total marks
    sorted_students = sorted(
        students,
        key=lambda s: (s["percentage"], s["total"]),
        reverse=True
    )

    total_count = len(sorted_students)
    current_rank = 1

    for idx, student in enumerate(sorted_students):
        if idx > 0:
            prev = sorted_students[idx - 1]
            if student["percentage"] == prev["percentage"] and student["total"] == prev["total"]:
                student["rank"] = prev["rank"]
            else:
                student["rank"] = idx + 1
        else:
            student["rank"] = 1

        # Percentile calculation: (count of students below score / total) * 100
        students_below = sum(1 for s in sorted_students if s["percentage"] < student["percentage"])
        student["percentile"] = round((students_below / total_count) * 100, 2) if total_count > 0 else 100.0

    return sorted_students


def compute_class_statistics(students: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computational Feature: Statistical analysis of student performance.
    Computes:
    - Total students, passed, failed, pass percentage
    - Class Average, Median, Min, Max, Standard Deviation
    - Subject-wise performance metrics (Average, Highest, Lowest, Pass Rate)
    - Grade distribution count
    """
    if not students:
        return {
            "total_students": 0,
            "passed_count": 0,
            "failed_count": 0,
            "pass_rate": 0.0,
            "class_average": 0.0,
            "median_percentage": 0.0,
            "highest_percentage": 0.0,
            "lowest_percentage": 0.0,
            "std_deviation": 0.0,
            "topper": None,
            "subject_stats": {},
            "grade_distribution": {},
        }

    total_count = len(students)
    percentages = [s["percentage"] for s in students]
    passed_count = sum(1 for s in students if s["status"] == "PASS")
    failed_count = total_count - passed_count
    pass_rate = round((passed_count / total_count) * 100, 2)

    class_avg = round(sum(percentages) / total_count, 2)
    sorted_pcts = sorted(percentages)
    mid = total_count // 2
    if total_count % 2 == 0:
        median_pct = round((sorted_pcts[mid - 1] + sorted_pcts[mid]) / 2, 2)
    else:
        median_pct = round(sorted_pcts[mid], 2)

    highest_pct = max(percentages)
    lowest_pct = min(percentages)

    # Standard Deviation calculation
    variance = sum((p - class_avg) ** 2 for p in percentages) / total_count
    std_dev = round(math.sqrt(variance), 2)

    # Topper
    topper = max(students, key=lambda s: s["percentage"])

    # Subject-wise statistics
    subject_stats = {}
    for sub in SUBJECTS:
        sub_marks = [s["marks"][sub] for s in students]
        sub_passed = sum(1 for m in sub_marks if m >= SUBJECT_PASS_MARK)
        sub_avg = round(sum(sub_marks) / total_count, 2)
        sub_variance = sum((m - sub_avg) ** 2 for m in sub_marks) / total_count
        subject_stats[sub] = {
            "average": sub_avg,
            "highest": max(sub_marks),
            "lowest": min(sub_marks),
            "pass_count": sub_passed,
            "pass_rate": round((sub_passed / total_count) * 100, 2),
            "std_dev": round(math.sqrt(sub_variance), 2),
        }

    # Grade distribution dictionary
    # All possible grades initialized to 0
    grade_distribution = {grade_info[1]: 0 for grade_info in GRADE_SCALE}
    for s in students:
        g = s["grade"]
        grade_distribution[g] = grade_distribution.get(g, 0) + 1

    return {
        "total_students": total_count,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "pass_rate": pass_rate,
        "class_average": class_avg,
        "median_percentage": median_pct,
        "highest_percentage": highest_pct,
        "lowest_percentage": lowest_pct,
        "std_deviation": std_dev,
        "topper": {
            "roll_no": topper["roll_no"],
            "name": topper["name"],
            "percentage": topper["percentage"],
            "grade": topper["grade"],
        },
        "subject_stats": subject_stats,
        "grade_distribution": grade_distribution,
    }


def generate_academic_recommendations(
    student: Dict[str, Any],
    class_stats: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Computational Feature: Rule-based recommendation engine.
    Analyzes student marks against subject benchmarks and class averages.
    Returns tailored academic diagnostic points and study recommendations.
    """
    recommendations = []
    marks = student["marks"]
    subj_stats = class_stats.get("subject_stats", {})

    # Rule 1: High Distinction Performance
    if student["percentage"] >= 85.0:
        recommendations.append({
            "category": "Excellence",
            "type": "success",
            "subject": "Overall Academic Standing",
            "message": "Outstanding overall achievement! Eligible for honors list, peer tutoring, and advanced project work.",
        })

    # Rule 2: Subject-specific weakness & remediation
    for sub in SUBJECTS:
        mark = marks.get(sub, 0)
        avg = subj_stats.get(sub, {}).get("average", 60.0)

        if mark < SUBJECT_PASS_MARK:
            gap = round(SUBJECT_PASS_MARK - mark, 1)
            recommendations.append({
                "category": "Remedial Attention",
                "type": "danger",
                "subject": sub,
                "message": f"Critical concern: Scored {mark}/100 (Failed by {gap} marks). Mandatory remedial tutorials and daily problem practice required.",
            })
        elif mark < avg - 10:
            diff = round(avg - mark, 1)
            recommendations.append({
                "category": "Improvement Needed",
                "type": "warning",
                "subject": sub,
                "message": f"Scored {mark}/100, which is {diff}% below the class average ({avg}). Focus on core concepts and weekly revision.",
            })
        elif mark >= 90:
            recommendations.append({
                "category": "Mastery",
                "type": "info",
                "subject": sub,
                "message": f"Exceptional mastery in {sub} ({mark}/100). Consider undertaking competitive algorithmic challenges or mini research projects.",
            })

    # Rule 3: Balance diagnostic (high variance between best and worst subject)
    sub_scores = list(marks.values())
    spread = max(sub_scores) - min(sub_scores)
    if spread >= 35:
        recommendations.append({
            "category": "Study Balance",
            "type": "warning",
            "subject": "Study Habit Recommendation",
            "message": f"High score discrepancy of {spread} marks between strongest and weakest subjects. Reallocate daily study hours to maintain balanced CGPA.",
        })

    if not recommendations:
        recommendations.append({
            "category": "Steady Progress",
            "type": "info",
            "subject": "General Advice",
            "message": "Consistent performance across all modules. Maintain regular study schedule to prepare for upcoming semester assessments.",
        })

    return recommendations


def generate_text_report_card(
    student: Dict[str, Any],
    class_stats: Optional[Dict[str, Any]] = None
) -> str:
    """
    Computational Feature: Automatic generation of a formatted ASCII report card.
    Can be saved to a text file or displayed directly in console/web.
    """
    border = "=" * 68
    sub_border = "-" * 68

    recs = generate_academic_recommendations(student, class_stats or {}) if class_stats else []

    lines = [
        border,
        "               ACADEMIC PERFORMANCE REPORT CARD",
        "             Course: Computational Thinking (2026CSAE100)",
        border,
        f" Roll Number: {student['roll_no']:<18} Student Name: {student['name']}",
        f" Final Rank : #{student.get('rank', 'N/A'):<17} Class Percentile: {student.get('percentile', 0.0):.1f}%",
        f" Final Grade: {student['grade']} ({student['grade_desc']:<12}) Result Status  : {student['status']}",
        sub_border,
        f" {'SUBJECT':<32} {'MAX':<6} {'OBTAINED':<10} {'STATUS':<8}",
        sub_border,
    ]

    for sub in SUBJECTS:
        score = student["marks"][sub]
        sub_status = "PASS" if score >= SUBJECT_PASS_MARK else "FAIL *"
        lines.append(f" {sub:<32} {100:<6} {score:<10.1f} {sub_status:<8}")

    lines.extend([
        sub_border,
        f" Total Marks : {student['total']:.1f} / {student['max_total']}       Percentage: {student['percentage']:.2f}%",
        f" Grade Points: {student['gpa']:.1f} / 10.0",
        border,
        " ACADEMIC DIAGNOSTICS & RECOMMENDATIONS:",
    ])

    for r in recs:
        lines.append(f"  • [{r['category'].upper()}] {r['subject']}:")
        lines.append(f"    {r['message']}")

    lines.extend([
        border,
        " Note: Minimum 40% required per subject and aggregate for PASS.",
        border,
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File Handling Functions (CSV & Text Report Files)
# ---------------------------------------------------------------------------

def resolve_writable_path(file_path: str) -> str:
    """
    Returns file_path if directory is writable, or copies and resolves to /tmp
    when executing in serverless environments like Vercel with read-only root filesystems.
    """
    if os.environ.get("VERCEL") or not os.access(os.path.dirname(os.path.abspath(file_path)), os.W_OK):
        tmp_path = os.path.join("/tmp", os.path.basename(file_path))
        if not os.path.exists(tmp_path) and os.path.exists(file_path):
            try:
                import shutil
                shutil.copyfile(file_path, tmp_path)
            except Exception:
                pass
        return tmp_path
    return file_path


def load_students_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads student records from a CSV file.
    Performs data sanitization and handles missing or corrupted entries.
    """
    resolved_path = resolve_writable_path(file_path)
    target_path = resolved_path if os.path.exists(resolved_path) else file_path

    if not os.path.exists(target_path):
        return []

    students = []
    with open(target_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                roll_no = row.get("roll_no", "").strip()
                name = row.get("name", "").strip()
                if not roll_no or not name:
                    continue

                marks = {}
                for sub in SUBJECTS:
                    marks[sub] = float(row.get(sub, 0.0))

                record = process_student_record(roll_no, name, marks)
                students.append(record)
            except (ValueError, KeyError):
                # Safely skip ill-formatted rows with logging
                continue

    # Compute rankings across all loaded students
    return compute_class_rankings(students)


def save_students_to_csv(students: List[Dict[str, Any]], file_path: str) -> None:
    """
    Writes student records to a CSV file.
    Ensures parent directory exists and uses /tmp if root is read-only.
    """
    target_path = resolve_writable_path(file_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    fieldnames = ["roll_no", "name"] + list(SUBJECTS) + ["total", "percentage", "grade", "gpa", "status", "rank"]

    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in students:
            row = {
                "roll_no": s["roll_no"],
                "name": s["name"],
                "total": s["total"],
                "percentage": s["percentage"],
                "grade": s["grade"],
                "gpa": s["gpa"],
                "status": s["status"],
                "rank": s.get("rank", 0),
            }
            for sub in SUBJECTS:
                row[sub] = s["marks"].get(sub, 0.0)
            writer.writerow(row)


def save_individual_report_card(
    student: Dict[str, Any],
    output_dir: str,
    class_stats: Optional[Dict[str, Any]] = None
) -> str:
    """
    Saves student ASCII report card to a text file in `output_dir`.
    Returns the file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_name = f"Report_Card_{student['roll_no']}.txt"
    file_path = os.path.join(output_dir, file_name)
    report_content = generate_text_report_card(student, class_stats)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return file_path
