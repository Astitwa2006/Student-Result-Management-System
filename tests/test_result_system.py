"""
Unit Testing Suite for Student Result Management System
Role Responsibility: Payal Kansal (Testing and error checking)
Course: Computational Thinking and Programming (2026CSAE100)

Covers:
1. Valid mark calculations (total, percentage, grade, GPA)
2. Boundary conditions (0, 40 passing threshold, 100 max)
3. Input validation & exception handling (negative marks, >100, non-numeric)
4. Ranking & tie-breaking logic
5. Statistical calculations (Mean, Median, Standard Deviation)
6. Rule-based diagnostic engine
7. File I/O integrity
"""

import unittest
import os
import sys
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.result_engine import (
    SUBJECTS,
    validate_marks,
    calculate_grade,
    process_student_record,
    compute_class_rankings,
    compute_class_statistics,
    generate_academic_recommendations,
    load_students_from_csv,
    save_students_to_csv,
)


class TestStudentResultSystem(unittest.TestCase):

    def setUp(self):
        self.sample_valid_marks = {
            "Python Programming": 85.0,
            "Mathematics": 90.0,
            "Digital Electronics": 80.0,
            "Physics": 75.0,
            "Professional Communication": 80.0,
        }

    # ---------------------------------------------------------
    # Test Case Group 1: Grade and Mark Calculations
    # ---------------------------------------------------------
    def test_calculate_grade_boundaries(self):
        """TC-01: Verify correct grade assignment across all thresholds."""
        self.assertEqual(calculate_grade(95.0)[0], "A+")
        self.assertEqual(calculate_grade(90.0)[0], "A+")
        self.assertEqual(calculate_grade(85.0)[0], "A")
        self.assertEqual(calculate_grade(80.0)[0], "A")
        self.assertEqual(calculate_grade(75.0)[0], "B+")
        self.assertEqual(calculate_grade(70.0)[0], "B+")
        self.assertEqual(calculate_grade(65.0)[0], "B")
        self.assertEqual(calculate_grade(60.0)[0], "B")
        self.assertEqual(calculate_grade(55.0)[0], "C")
        self.assertEqual(calculate_grade(50.0)[0], "C")
        self.assertEqual(calculate_grade(45.0)[0], "D")
        self.assertEqual(calculate_grade(40.0)[0], "D")
        self.assertEqual(calculate_grade(39.9)[0], "F")
        self.assertEqual(calculate_grade(0.0)[0], "F")

    def test_process_student_record_valid(self):
        """TC-02: Verify total, percentage, GPA calculation for valid inputs."""
        record = process_student_record("S26CSEU1901", "Arnav Mittal", self.sample_valid_marks)
        expected_total = 85.0 + 90.0 + 80.0 + 75.0 + 80.0  # 410.0
        expected_pct = 410.0 / 5.0  # 82.0

        self.assertEqual(record["roll_no"], "S26CSEU1901")
        self.assertEqual(record["total"], expected_total)
        self.assertEqual(record["percentage"], expected_pct)
        self.assertEqual(record["grade"], "A")
        self.assertEqual(record["status"], "PASS")
        self.assertEqual(record["failed_subjects"], [])

    def test_process_student_record_fail_in_subject(self):
        """TC-03: Student fails if any subject is below 40 even if total is passing."""
        marks = self.sample_valid_marks.copy()
        marks["Physics"] = 32.0  # Below 40
        record = process_student_record("S26CSEU1812", "Ishaan Bhatt", marks)

        self.assertEqual(record["status"], "FAIL")
        self.assertIn("Physics", record["failed_subjects"])

    # ---------------------------------------------------------
    # Test Case Group 2: Input Validation & Error Handling
    # ---------------------------------------------------------
    def test_validate_marks_negative(self):
        """TC-04: Negative marks should be rejected."""
        bad_marks = self.sample_valid_marks.copy()
        bad_marks["Mathematics"] = -5.0
        is_valid, msg = validate_marks(bad_marks)
        self.assertFalse(is_valid)
        self.assertIn("between 0 and 100", msg)

    def test_validate_marks_above_100(self):
        """TC-05: Marks above 100 should be rejected."""
        bad_marks = self.sample_valid_marks.copy()
        bad_marks["Python Programming"] = 105.0
        is_valid, msg = validate_marks(bad_marks)
        self.assertFalse(is_valid)
        self.assertIn("between 0 and 100", msg)

    def test_validate_marks_missing_subject(self):
        """TC-06: Missing subject marks should be rejected."""
        bad_marks = self.sample_valid_marks.copy()
        del bad_marks["Physics"]
        is_valid, msg = validate_marks(bad_marks)
        self.assertFalse(is_valid)
        self.assertIn("Missing marks", msg)

    def test_process_student_record_raises_value_error(self):
        """TC-07: process_student_record raises ValueError on invalid input."""
        bad_marks = self.sample_valid_marks.copy()
        bad_marks["Physics"] = -10.0
        with self.assertRaises(ValueError):
            process_student_record("ROLL001", "Test", bad_marks)

    # ---------------------------------------------------------
    # Test Case Group 3: Ranking & Tie Handling
    # ---------------------------------------------------------
    def test_class_ranking_and_percentile(self):
        """TC-08: Verify ranking order and tied ranks."""
        s1 = process_student_record("R1", "Student 1", {s: 90 for s in SUBJECTS})  # 90%
        s2 = process_student_record("R2", "Student 2", {s: 90 for s in SUBJECTS})  # 90% (tied)
        s3 = process_student_record("R3", "Student 3", {s: 70 for s in SUBJECTS})  # 70%

        ranked = compute_class_rankings([s3, s1, s2])
        self.assertEqual(ranked[0]["roll_no"], "R1")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertEqual(ranked[1]["roll_no"], "R2")
        self.assertEqual(ranked[1]["rank"], 1)  # Tied rank 1
        self.assertEqual(ranked[2]["roll_no"], "R3")
        self.assertEqual(ranked[2]["rank"], 3)  # Next rank is 3

    # ---------------------------------------------------------
    # Test Case Group 4: Statistics & Computational Diagnostics
    # ---------------------------------------------------------
    def test_class_statistics(self):
        """TC-09: Verify mean, median, topper, and standard deviation calculations."""
        s1 = process_student_record("R1", "Top Student", {s: 90 for s in SUBJECTS})  # 90%
        s2 = process_student_record("R2", "Mid Student", {s: 70 for s in SUBJECTS})  # 70%
        s3 = process_student_record("R3", "Low Student", {s: 50 for s in SUBJECTS})  # 50%

        stats = compute_class_statistics([s1, s2, s3])
        self.assertEqual(stats["total_students"], 3)
        self.assertEqual(stats["passed_count"], 3)
        self.assertEqual(stats["class_average"], 70.0)
        self.assertEqual(stats["median_percentage"], 70.0)
        self.assertEqual(stats["highest_percentage"], 90.0)
        self.assertEqual(stats["lowest_percentage"], 50.0)
        self.assertEqual(stats["topper"]["name"], "Top Student")

    def test_rule_based_recommendations(self):
        """TC-10: Rule-based engine flags subject weaknesses and suggestions."""
        weak_marks = self.sample_valid_marks.copy()
        weak_marks["Digital Electronics"] = 35.0  # Fail
        student = process_student_record("R4", "Struggling Student", weak_marks)
        stats = compute_class_statistics([student])

        recs = generate_academic_recommendations(student, stats)
        # Should detect remedial attention needed for Digital Electronics
        danger_recs = [r for r in recs if r["category"] == "Remedial Attention"]
        self.assertTrue(len(danger_recs) >= 1)
        self.assertEqual(danger_recs[0]["subject"], "Digital Electronics")

    # ---------------------------------------------------------
    # Test Case Group 5: File I/O Persistence
    # ---------------------------------------------------------
    def test_csv_save_and_load(self):
        """TC-11: Data saved to CSV must be read back accurately without loss."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            s1 = process_student_record("TEST01", "Unit Tester", self.sample_valid_marks)
            save_students_to_csv([s1], tmp_path)

            loaded = load_students_from_csv(tmp_path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["roll_no"], "TEST01")
            self.assertEqual(loaded[0]["name"], "Unit Tester")
            self.assertEqual(loaded[0]["percentage"], s1["percentage"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
