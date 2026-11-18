# Student Result Management System

🎓 **Course:** Computational Thinking and Programming (Course Code: `2026CSAE100`)  
👥 **Group Members:**
1. **Prisha Mishra** (`S26CSEU1899`) — Research & Python Concept Analysis
2. **Kinjal Kadiyan** (`S26CSEU1905`) — Research & Project Planning
3. **Arnav Mittal** (`S26CSEU1901`) — Input & Data Management
4. **Payal Kansal** (`S26CSEU1907`) — Testing & Error Checking
5. **Jishnu Priya Hasini** (`S26CSEU1887`) — Documentation & Presentation

---

## 🌟 Project Overview

The **Student Result Management System** is a modular Python project engineered to automate academic evaluation. It eliminates manual errors by processing student scores across 5 core modules, executing multi-tier grading, computing fair competition rankings with tie-breaking, generating class dispersion statistics (Mean, Median, Standard Deviation), and providing prescriptive rule-based diagnostics to guide struggling students.

The project offers **two interfaces** sharing the exact same Python computational core:
1. **Interactive Terminal CLI (`main.py`):** Rich ANSI colored menu for console demonstration during viva.
2. **Modern Web Dashboard (`app.py` / `server.py`):** Interactive browser dashboard with live KPI cards, search/filter table, modal forms, printable marksheets, and Matplotlib analytics charts.

---

## 📂 Project Structure & Deliverables

```
StudentResultManagementSystem/
│
├── core/                                   # Computational Engine
│   ├── result_engine.py                    # Calculations, grades, rankings, stats, diagnostics, CSV I/O
│   └── visualizer.py                       # Matplotlib chart generator (subject averages, grade donut, score spread)
│
├── data/
│   ├── students.csv                        # Persistent CSV data storage (pre-seeded with 18 records)
│   ├── charts/                             # Generated analytical charts (.png)
│   └── reports/                            # Generated ASCII student report cards (.txt)
│
├── static/                                 # Web Dashboard Frontend
│   ├── index.html                          # Semantic HTML5 dashboard layout
│   ├── style.css                           # Modern, responsive UI design
│   └── app.js                              # REST API controller, live calculator, filters & search
│
├── tests/
│   └── test_result_system.py               # 11 automated unit tests (Payal Kansal's role)
│
├── main.py                                 # Interactive Terminal CLI Application
├── app.py                                  # FastAPI Web Backend
├── server.py                               # Zero-dependency fallback server (Python http.server)
│
├── generate_presentation.py                # Python script generating 12-slide PPTX
├── generate_report_pdf.py                  # Python script generating 10-section PDF Report
│
├── Student_Result_Management_System_Presentation.pptx  # 12-slide PowerPoint presentation
├── Student_Result_Management_System_Project_Report.pdf  # Formal academic PDF report
├── PROJECT_REPORT.md                       # Comprehensive 10-section Markdown report
├── VIVA_PREPARATION_GUIDE.md               # Master viva voce preparation guide for all 5 students
│
├── run_cli.sh                              # Run Terminal CLI
├── run_web.sh                              # Run Web Dashboard
└── run_tests.sh                            # Run Automated Unit Tests
```

---

## 🚀 Quick Start Instructions

### 1. Run the Web Dashboard
```bash
# Option A: Using launcher script
./run_web.sh

# Option B: Run with virtual environment (FastAPI)
python3 app.py

# Option C: Zero-dependency fallback server (runs on any Python 3 machine without pip!)
python3 server.py 8000
```
Open your browser at: **`http://127.0.0.1:8000`**

### 2. Run the Terminal CLI
```bash
./run_cli.sh
# or
python3 main.py
```

### 3. Run Automated Unit Tests
```bash
./run_tests.sh
# or
python3 -m unittest discover tests -v
```
*(All 11 test cases pass with a 100% success rate)*

---

## 💡 Key Computational Features

1. **Competition Ranking Algorithm:** Handles tied scores fairly (`1, 2, 2, 4` ranking) and calculates student percentiles.
2. **Statistical Analysis:** Computes Class Mean ($\mu$), Median, Population Standard Deviation ($\sigma = \sqrt{\frac{1}{N}\sum(x-\mu)^2}$), Topper, and Subject-wise pass rates.
3. **Rule-Based Diagnostic Intelligence:** Evaluates student scores against class averages:
   - **Remedial Attention:** Flags marks $< 40$ and calculates the exact mark deficit.
   - **Improvement Needed:** Flags subjects $> 10\%$ below class average.
   - **Mastery:** Recognizes scores $\ge 90$ with honors and peer-mentorship recommendations.
4. **Data Persistence:** Reads and writes CSV format without external database dependencies.
5. **Formatted Marksheet Generation:** Generates individual printable ASCII report cards.

---

## 👥 Viva Voce Preparation
Refer to **`VIVA_PREPARATION_GUIDE.md`** for:
- Individual questions & model answers tailored to each team member's role.
- Line-by-line function walkthroughs.
- Predict-the-output drills.
- Live code modification challenges commonly requested by examiners.
