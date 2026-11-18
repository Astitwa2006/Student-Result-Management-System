# Student Result Management System

A Python-based academic evaluation and analytics platform featuring automated grade calculation, competition ranking, statistical performance analysis, rule-based diagnostics, and an interactive web dashboard.

---

## 🌟 Key Features

- **Automated Score Evaluation:** Computes total marks, percentage, 10-point GPA, and assigns letter grades (`A+` to `F`) using immutable grading thresholds.
- **Competition Ranking Algorithm:** Implements standard competition ranking (`1224` format) with fair tie-breaking and relative student percentile calculations.
- **Statistical Analytics Engine:** Computes descriptive cohort statistics including Class Mean, Median, Population Standard Deviation ($\sigma = \sqrt{\frac{1}{N}\sum(x-\mu)^2}$), Highest/Lowest performers, and subject-wise pass rates.
- **Rule-Based Academic Diagnostics:** Prescribes targeted remedial guidance for subjects with marks $< 40$ or $>10\%$ below class average, recognizes subject mastery ($\ge 90$), and flags performance discrepancies.
- **Dual User Interface:**
  - **Interactive Web Dashboard:** Modern, responsive UI with real-time KPI metrics, search, sorting, grade filtering, live mark calculator modal, and printable academic marksheets.
  - **Terminal CLI:** Full-featured console application with colored ANSI menus.
- **Zero-Dependency Fallback Server:** Can run locally via Python's standard library `http.server` with zero external pip dependencies.
- **Serverless Cloud Ready:** Configured for Vercel deployment with serverless runtime support.

---

## 📂 Project Structure

```
StudentResultManagementSystem/
│
├── api/
│   └── index.py                # Vercel serverless ASGI entrypoint
│
├── core/
│   ├── result_engine.py        # Core computational engine & algorithms
│   └── visualizer.py           # Matplotlib analytical chart generator
│
├── data/
│   └── students.csv            # Persistent CSV data storage
│
├── static/
│   ├── index.html              # Web dashboard interface
│   ├── style.css               # Modern responsive styling
│   └── app.js                  # Frontend controller & REST API client
│
├── tests/
│   └── test_result_system.py   # Automated unit test suite (11 test cases)
│
├── app.py                      # FastAPI web application backend
├── server.py                   # Zero-dependency fallback standard library server
├── main.py                     # Terminal CLI application
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel deployment configuration
├── .gitignore                  # Git ignore rules
│
├── run_web.sh                  # Web dashboard launcher script
├── run_cli.sh                  # Terminal CLI launcher script
└── run_tests.sh                # Test suite launcher script
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Optional: Virtual environment (`venv`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Astitwa2006/Student-Result-Management-System.git
   cd Student-Result-Management-System
   ```

2. (Optional) Install dependencies for the FastAPI web server and Matplotlib visualizer:
   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

### 1. Run the Web Dashboard

**Option A — FastAPI Server (Recommended):**
```bash
./run_web.sh
# or
python3 app.py
```
Open your browser at `http://127.0.0.1:8000`.

**Option B — Zero-Dependency Server (No pip packages required):**
```bash
python3 server.py 8000
```
Open your browser at `http://127.0.0.1:8000`.

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

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the web dashboard interface |
| `GET` | `/api/meta` | System metadata (subjects, grading scales) |
| `GET` | `/api/students` | Retrieve all student records with computed ranks |
| `POST` | `/api/students` | Register a new student record (validates input) |
| `DELETE` | `/api/students/{roll_no}` | Delete a student and recalculate class rankings |
| `GET` | `/api/students/{roll_no}/report` | Generate individual report card with diagnostic advice |
| `GET` | `/api/analytics` | Compute class statistical metrics & generate charts |
| `GET` | `/api/export/csv` | Download the current CSV dataset |

---

## ☁️ Deployment (Vercel)

The application is structured for Vercel deployment via `vercel.json` and `api/index.py`:

```bash
# Deploy with Vercel CLI
vercel --prod
```

Or connect the GitHub repository directly to [Vercel](https://vercel.com/new) for continuous deployment on push.

---

## 📄 License

This project is licensed under the MIT License.
