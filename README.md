# Student Result Management System

**Course:** Computational Thinking and Programming (2026CSAE100)  
**Team:** Prisha Mishra · Kinjal Kadiyan · Arnav Mittal · Payal Kansal · Jishnu Priya Hasini

---

## 🌐 Live Deployment

| Layer    | Service | URL |
|----------|---------|-----|
| Frontend | Vercel  | [student-result-management-system-vert.vercel.app](https://student-result-management-system-vert.vercel.app) |
| Backend  | Render  | *Set after Render deployment — update `public/index.html`* |

---

## 📌 Project Overview

A Python-based Student Result Management System that:

- **Stores** student marks in CSV format (Python `csv` module)
- **Calculates** totals, percentages, and grades using a computational engine
- **Ranks** students with competition-style tie-handling algorithm
- **Analyses** class statistics: mean, median, standard deviation, subject averages
- **Recommends** personalised remedial or merit actions using rule-based logic
- **Visualises** performance via Matplotlib charts (bar, pie, scatter)
- **Exports** results as CSV download

---

## 🏗️ Architecture

```
GitHub Repository (source)
       │
       ├── Vercel (Frontend)
       │     └── public/ → index.html, style.css, app.js
       │
       └── Render (Backend API)
             └── app.py → FastAPI + CSV + Matplotlib
```

---

## 🗂️ Project Structure

```
StudentResultManagementSystem/
├── app.py                  ← FastAPI backend (Render)
├── main.py                 ← ANSI terminal CLI
├── server.py               ← Zero-dependency local server
├── requirements.txt        ← Python dependencies
├── render.yaml             ← Render deployment config
├── vercel.json             ← Vercel static site config
│
├── core/
│   ├── result_engine.py    ← Computation: grades, rankings, stats, diagnostics
│   └── visualizer.py       ← Matplotlib chart generator
│
├── data/
│   └── students.csv        ← Persistent student data (CSV)
│
├── public/                 ← Static frontend served by Vercel
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── static/                 ← Same frontend, served by FastAPI locally
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── tests/
    └── test_result_system.py  ← 11 unit tests
```

---

## 🚀 Deployment Guide

### Step 1 — Backend on Render

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repository: `Astitwa2006/Student-Result-Management-System`
3. Set the following:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Add Environment Variable: `RENDER = true`
5. Click **Deploy** → wait ~2 minutes
6. Copy your Render URL, e.g. `https://student-result-management-system.onrender.com`

### Step 2 — Connect Frontend to Backend

Open `public/index.html` and find this line (near the bottom of `<head>`):

```html
window.__API_BASE__ = 'PLACEHOLDER_RENDER_URL';
```

Replace `PLACEHOLDER_RENDER_URL` with your Render URL:

```html
window.__API_BASE__ = 'https://student-result-management-system.onrender.com';
```

Then push to GitHub — Vercel redeploys automatically.

### Step 3 — Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → your `student-result-management-system` project
2. It auto-deploys on every GitHub push (already connected)
3. Live at: `https://student-result-management-system-vert.vercel.app`

---

## 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server (backend + serves frontend)
python app.py
# → Open http://127.0.0.1:8000

# OR: run CLI terminal app
python main.py

# Run all unit tests
python -m unittest discover tests
```

---

## 🧪 Tests

```
tests/test_result_system.py — 11 unit tests
  ✓ Grade calculation (A+, A, B+, B, C, D, F)
  ✓ Mark validation (range, missing subjects)
  ✓ Total & percentage computation
  ✓ PASS/FAIL determination (failed subjects)
  ✓ Competition ranking with ties
  ✓ CSV save & reload round-trip
```

Run: `python -m unittest discover tests -v`

---

## 🐍 Python Concepts Used

| Concept               | Where Used |
|-----------------------|------------|
| `csv.DictReader/Writer` | `result_engine.py` — persistent data storage |
| **Tuples** (immutable) | `SUBJECTS`, `GRADE_SCALE` constants |
| **Dictionaries**       | Student records, subject stats |
| **Lists**              | Student roster, rankings |
| **Sets**               | Failed subjects detection |
| `sorted()` + lambda    | Competition ranking algorithm |
| Standard deviation     | Class analytics engine |
| Rule-based `if/elif`   | Diagnostic recommendations |
| Matplotlib             | 3-chart data visualisation |
| FastAPI / `http.server`| REST API + static serving |
| `unittest`             | 11 automated test cases |

---

## 👥 Team Contributions

| Student              | Roll No      | Contribution |
|----------------------|--------------|--------------|
| Prisha Mishra        | S26CSEU1899  | Research & Python concept analysis |
| Kinjal Kadiyan       | S26CSEU1905  | Research & project planning |
| Arnav Mittal         | S26CSEU1901  | Input & data management |
| Payal Kansal         | S26CSEU1907  | Testing & error checking |
| Jishnu Priya Hasini  | S26CSEU1887  | Documentation & presentation |
