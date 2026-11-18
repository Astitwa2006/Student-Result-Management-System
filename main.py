#!/usr/bin/env python3
"""
Student Result Management System - Interactive Console Interface
Course: Computational Thinking and Programming (2026CSAE100)
Team: Prisha Mishra, Kinjal Kadiyan, Arnav Mittal, Payal Kansal, Jishnu Priya Hasini

Features:
- Student Record Management (CRUD)
- Grade & CGPA computation
- Class Ranking & Percentile Calculation
- Statistical Analysis (Mean, Median, Standard Deviation, Subject Stats)
- Rule-based Diagnostics & Recommendations
- CSV Data Persistence & TXT Report Card Generation
- Visual Analytics via Matplotlib
"""

import os
import sys

# Ensure core package is accessible
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

# ANSI Color codes for clean terminal presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"{BOLD}{CYAN}{title.center(70)}{RESET}")
    print("=" * 70)


def prompt_valid_mark(subject: str) -> float:
    """Prompt user for a mark with validation loop."""
    while True:
        try:
            val_str = input(f"  Enter marks for {subject} (0-100): ").strip()
            val = float(val_str)
            if 0.0 <= val <= 100.0:
                return val
            print(f"  {RED}Error: Marks must be between 0 and 100.{RESET}")
        except ValueError:
            print(f"  {RED}Error: Invalid numerical input. Please re-enter.{RESET}")


def display_students_table(students):
    if not students:
        print(f"\n{YELLOW}No student records found.{RESET}")
        return

    print_header("CLASS RESULT SUMMARY TABLE")
    print(f"{'Rank':<5} {'Roll No':<14} {'Student Name':<20} {'Total':<7} {'%age':<7} {'Grade':<6} {'Status':<6}")
    print("-" * 70)

    for s in students:
        status_color = GREEN if s["status"] == "PASS" else RED
        print(
            f"{s.get('rank', '-'):<5} "
            f"{s['roll_no']:<14} "
            f"{s['name'][:19]:<20} "
            f"{s['total']:<7.1f} "
            f"{s['percentage']:<7.2f} "
            f"{s['grade']:<6} "
            f"{status_color}{s['status']:<6}{RESET}"
        )
    print("-" * 70)
    print(f"Total Records: {len(students)}")


def add_student_flow(students):
    print_header("ADD NEW STUDENT RECORD")
    existing_rolls = {s["roll_no"].upper() for s in students}

    while True:
        roll = input("Enter Student Roll Number (e.g. S26CSEU1920): ").strip().upper()
        if not roll:
            print(f"{RED}Roll number cannot be empty.{RESET}")
            continue
        if roll in existing_rolls:
            print(f"{RED}Roll number {roll} already exists! Use unique roll number.{RESET}")
            continue
        break

    while True:
        name = input("Enter Student Full Name: ").strip()
        if len(name) >= 2:
            break
        print(f"{RED}Name must contain at least 2 characters.{RESET}")

    print("\nEnter Marks for each subject:")
    marks = {}
    for sub in SUBJECTS:
        marks[sub] = prompt_valid_mark(sub)

    new_student = process_student_record(roll, name, marks)
    students.append(new_student)
    # Recompute rankings
    students[:] = compute_class_rankings(students)
    save_students_to_csv(students, DATA_FILE)
    print(f"\n{GREEN}✓ Student {name} ({roll}) successfully registered with Rank #{new_student['rank']}!{RESET}")


def search_student_flow(students):
    print_header("SEARCH STUDENT RECORD")
    query = input("Enter Roll Number or Name to search: ").strip().lower()
    if not query:
        print("Empty search query.")
        return

    matches = [
        s for s in students
        if query in s["roll_no"].lower() or query in s["name"].lower()
    ]

    if not matches:
        print(f"\n{YELLOW}No matching student records found for '{query}'.{RESET}")
        return

    display_students_table(matches)


def view_detailed_report_card(students):
    print_header("STUDENT DETAILED REPORT CARD & DIAGNOSTICS")
    roll = input("Enter Student Roll Number: ").strip().upper()

    target = next((s for s in students if s["roll_no"] == roll), None)
    if not target:
        print(f"\n{RED}Student with Roll Number '{roll}' not found.{RESET}")
        return

    stats = compute_class_statistics(students)
    report_text = generate_text_report_card(target, stats)
    print("\n" + report_text)

    # Prompt to export
    export = input("\nSave this report card to text file? (y/n, default 'y'): ").strip().lower()
    if export in ("", "y", "yes"):
        path = save_individual_report_card(target, REPORTS_DIR, stats)
        print(f"{GREEN}✓ Report card saved to: {path}{RESET}")


def display_analytics_flow(students):
    if not students:
        print(f"\n{YELLOW}No data available for analytics.{RESET}")
        return

    stats = compute_class_statistics(students)
    print_header("COMPUTATIONAL CLASS PERFORMANCE ANALYTICS")

    print(f"{BOLD}Overall Class Performance:{RESET}")
    print(f"  • Total Enrolled Students : {stats['total_students']}")
    print(f"  • Passed Students         : {GREEN}{stats['passed_count']}{RESET} ({stats['pass_rate']}%)")
    print(f"  • Students Needing Help   : {RED}{stats['failed_count']}{RESET}")
    print(f"  • Class Mean Percentage   : {stats['class_average']:.2f}%")
    print(f"  • Class Median Percentage : {stats['median_percentage']:.2f}%")
    print(f"  • Standard Deviation (σ)  : {stats['std_deviation']:.2f}%")
    print(f"  • Highest Percentage      : {stats['highest_percentage']:.2f}%")
    print(f"  • Lowest Percentage       : {stats['lowest_percentage']:.2f}%")

    if stats["topper"]:
        t = stats["topper"]
        print(f"  • {BOLD}Class Topper{RESET}            : {GREEN}{t['name']} ({t['roll_no']}) - {t['percentage']}% [Grade {t['grade']}]{RESET}")

    print(f"\n{BOLD}Subject-wise Performance Breakdown:{RESET}")
    print(f"{'Subject':<28} {'Average':<9} {'Highest':<9} {'Lowest':<8} {'Pass %':<8} {'StdDev':<7}")
    print("-" * 70)
    for sub, sinfo in stats["subject_stats"].items():
        print(
            f"{sub[:27]:<28} "
            f"{sinfo['average']:<9.1f} "
            f"{sinfo['highest']:<9.1f} "
            f"{sinfo['lowest']:<8.1f} "
            f"{sinfo['pass_rate']:<8.1f}% "
            f"{sinfo['std_dev']:<7.1f}"
        )

    print(f"\n{BOLD}Grade Distribution:{RESET}")
    for g, count in stats["grade_distribution"].items():
        bar = "█" * count
        print(f"  {g:<3}: {count:<2} {bar}")


def generate_charts_flow(students):
    if not students:
        print(f"\n{YELLOW}No data available to generate charts.{RESET}")
        return

    print_header("GENERATING ANALYTICAL CHARTS (MATPLOTLIB)")
    stats = compute_class_statistics(students)
    paths = generate_all_charts(students, stats, CHARTS_DIR)

    print(f"{GREEN}✓ Successfully generated {len(paths)} visualization charts:{RESET}")
    for name, path in paths.items():
        print(f"  • {name}: {path}")


def main_menu():
    students = load_students_from_csv(DATA_FILE)

    while True:
        print_header("STUDENT RESULT MANAGEMENT SYSTEM (Python CLI)")
        print(f"{BOLD}1.{RESET} Display All Student Results (Summary Table)")
        print(f"{BOLD}2.{RESET} Add New Student Record")
        print(f"{BOLD}3.{RESET} Search Student by Roll No or Name")
        print(f"{BOLD}4.{RESET} View Detailed Student Report Card & Diagnostics")
        print(f"{BOLD}5.{RESET} Compute & Display Class Analytics (Mean, Median, StdDev)")
        print(f"{BOLD}6.{RESET} Generate Visualization Charts (Matplotlib)")
        print(f"{BOLD}7.{RESET} Export All Student Report Cards to Text Files")
        print(f"{BOLD}8.{RESET} Save & Exit")
        print("=" * 70)

        choice = input("Enter your option (1-8): ").strip()

        if choice == "1":
            display_students_table(students)
        elif choice == "2":
            add_student_flow(students)
        elif choice == "3":
            search_student_flow(students)
        elif choice == "4":
            view_detailed_report_card(students)
        elif choice == "5":
            display_analytics_flow(students)
        elif choice == "6":
            generate_charts_flow(students)
        elif choice == "7":
            stats = compute_class_statistics(students)
            for s in students:
                save_individual_report_card(s, REPORTS_DIR, stats)
            print(f"\n{GREEN}✓ Exported {len(students)} individual report cards into '{REPORTS_DIR}'!{RESET}")
        elif choice == "8":
            save_students_to_csv(students, DATA_FILE)
            print(f"\n{GREEN}All data successfully saved to {DATA_FILE}. Goodbye!{RESET}\n")
            break
        else:
            print(f"\n{RED}Invalid choice '{choice}'. Please choose 1 to 8.{RESET}")


if __name__ == "__main__":
    main_menu()
