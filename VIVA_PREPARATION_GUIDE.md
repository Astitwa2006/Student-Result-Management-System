# Individual Viva Voce Preparation Master Guide
**Course:** Computational Thinking and Programming (2026CSAE100)  
**Project:** Student Result Management System  

---

## 🎯 Viva Overview & Evaluation Criteria
According to the official project guidelines, the viva evaluates:
1. **Explain a function or section of the program**
2. **Explain the logic and computational thinking used**
3. **Predict the output of a code segment**
4. **Identify or correct an error**
5. **Make a small live modification to the program**

---

## 👤 Part 1: Member-Specific Questions & Model Answers

### 1. Prisha Mishra (S26CSEU1899)
**Role:** Research & Python Concept Analysis

#### Q1: "Why did you use Tuples for the grading scale instead of Lists or Dictionaries?"
> **Answer:**  
> "We used a tuple for `GRADE_SCALE` because grade boundaries and letter grade mappings are fixed, immutable academic rules. Tuples protect against accidental runtime mutation (`TypeError` if anyone tries to reassign `GRADE_SCALE[0] = ...`), provide slight memory and speed optimizations, and allow us to iterate through ordered pairs `(min_percentage, grade, gpa, description)` deterministically."

#### Q2: "How does the project demonstrate computational thinking?"
> **Answer:**  
> "The project implements all four pillars of computational thinking:
> 1. **Decomposition:** Breaking the complex problem of result management into discrete modules: input validation, mathematical aggregation, ranking algorithm, statistical analysis, and report generation.
> 2. **Pattern Recognition:** Recognizing that grade classification follows an ordered threshold comparison, and that student performance falls into statistical distributions (mean, median, standard deviation).
> 3. **Abstraction:** Representing each student as a clean dictionary schema hiding calculation complexity behind clear functional interfaces (`process_student_record`, `compute_class_rankings`).
> 4. **Algorithm Design:** Designing step-by-step algorithms for competition ranking with tie-breaking, percentile scoring, and rule-based diagnostic alerts."

---

### 2. Kinjal Kadiyan (S26CSEU1905)
**Role:** Research & Project Planning

#### Q1: "Explain how your competition ranking algorithm works and how it handles ties."
> **Answer:**  
> "Rather than using simple enumeration which assigns arbitrary ranks (1, 2, 3) to students with identical scores, we implemented standard **Competition Ranking ('1224' ranking)**:
> 1. We first sort the students descending by percentage, breaking ties with total marks.
> 2. We compare the current student with the previous student. If both percentage and total are identical, the current student receives the same rank as the previous student.
> 3. If the score differs, the student receives their actual position in the cohort (`index + 1`). For example, two students tied at 90% both get Rank #1, and the next student gets Rank #3."

#### Q2: "Explain the logic of your Rule-Based Academic Diagnostic Engine."
> **Answer:**  
> "Beyond just displaying marks, our computational engine compares a student's performance against two benchmarks: the absolute passing threshold (40 marks) and the class average ($\mu$). If a student scores below 40 in any subject, they are flagged for 'Remedial Attention' with the exact mark deficit. If they score more than 10% below class average in a subject, it flags 'Improvement Needed'. If they score $\ge 90$, they are awarded 'Mastery'. This provides actionable guidance rather than passive data."

---

### 3. Arnav Mittal (S26CSEU1901)
**Role:** Input & Data Management

#### Q1: "How do you handle CSV file storage, and why did you use `csv.DictReader` instead of regular `csv.reader`?"
> **Answer:**  
> "We used Python's built-in `csv` module with `csv.DictReader` and `csv.DictWriter`. Unlike standard index-based readers (`row[0]`, `row[1]`), `DictReader` maps each column to dictionary keys based on the CSV header (`row['roll_no']`, `row['Python Programming']`). This makes the code immune to column reordering, highly readable, and naturally compatible with our student dictionary records."

#### Q2: "How does the system prevent duplicate roll numbers and invalid marks?"
> **Answer:**  
> "For duplicate prevention, we collect existing roll numbers into a Python `set` of uppercase strings (`existing_rolls = {s['roll_no'].upper() for s in students}`). A set lookup runs in $O(1)$ constant time. For mark validation, our `validate_marks` function checks that every mark is an `int` or `float` and satisfies $0.0 \le \text{mark} \le 100.0$. If any check fails, it returns `(False, error_message)` or raises a `ValueError`."

---

### 4. Payal Kansal (S26CSEU1907)
**Role:** Testing & Error Checking

#### Q1: "Explain your automated testing strategy and what test cases you designed."
> **Answer:**  
> "We implemented an automated test suite with 11 test cases using Python's standard `unittest` framework in `tests/test_result_system.py`. We tested:
> 1. **Boundary conditions:** Exact percentage boundaries (90%, 80%, 70%, 60%, 50%, 40%, 39.9%, and 0%).
> 2. **Negative & Out-of-bounds inputs:** Marks like $-5.0$ and $105.0$ are caught and rejected.
> 3. **Subject-level failure:** A student with total $> 40\%$ but one subject $< 40$ correctly receives status 'FAIL'.
> 4. **Competition ranking ties:** Verified that two tied students share Rank #1 and the next receives Rank #3.
> 5. **CSV Round-trip integrity:** Saving a record to a temporary CSV and reading it back to verify zero data loss."

#### Q2: "How does the program handle unexpected inputs or missing files without crashing?"
> **Answer:**  
> "We use defensive programming with `try-except` blocks. If `data/students.csv` is missing, `load_students_from_csv` catches `FileNotFoundError` or verifies `os.path.exists()`, safely returning an empty list rather than crashing. In input loops, `float(input_str)` is wrapped in `try-except ValueError` to catch non-numeric inputs like 'abc' and re-prompt the user gracefully."

---

### 5. Jishnu Priya Hasini (S26CSEU1887)
**Role:** Documentation & Presentation

#### Q1: "Walk through the structure of the Project Report and why each section is included."
> **Answer:**  
> "The report strictly follows Section 1.6 of the instructor's instructions:
> 1. **Project Title & Team Details:** Identifies our group and individual roles.
> 2. **Problem Statement:** Defines the inefficiencies of manual result preparation.
> 3. **Objectives:** States our 5 core goals from Milestone 1.
> 4. **Main Features:** Outlines the core engine, diagnostics, visualizer, and UI.
> 5. **Algorithm & Flowchart:** Illustrates the computational execution logic.
> 6. **Python Concepts Used:** Maps Python structures (tuples, lists, dicts, sets, file I/O).
> 7. **Important Screenshots:** Includes ASCII marksheet and chart descriptions.
> 8. **Testing:** Summarizes our 11 unit test cases and verification results.
> 9. **Team Contributions:** Documents individual responsibilities.
> 10. **Conclusion & Future Scope:** Summarizes outcomes and future improvements."

#### Q2: "How does the web application complement the Python core engine?"
> **Answer:**  
> "The web application provides an intuitive graphical interface without altering the core Python computational engine. Both our interactive Terminal CLI (`main.py`) and Web Dashboard (`app.py` / `server.py`) call the exact same functions in `core/result_engine.py`. This ensures full separation of concerns: all computational logic remains pure Python, while the web front-end makes results accessible to teachers and students."

---

## 💻 Part 2: Code Walkthrough & Line-by-Line Explanations

### 1. `calculate_grade` Function
```python
def calculate_grade(percentage: float) -> Tuple[str, float, str]:
    for min_pct, grade, gpa, desc in GRADE_SCALE:
        if percentage >= min_pct:
            return grade, gpa, desc
    return "F", 0.0, "Fail"
```
- **Explanation:** Takes student percentage as input. Iterates through the pre-sorted `GRADE_SCALE` tuple. Because tuples are ordered from highest (90.0) to lowest (0.0), the first threshold that `percentage >= min_pct` evaluates to `True` assigns the correct letter grade and GPA immediately.

### 2. Set Comprehension for Failed Subjects
```python
failed_subjects: Set[str] = {
    sub for sub, mark in marks.items() if mark < SUBJECT_PASS_MARK
}
```
- **Explanation:** Uses **Set Comprehension** over dictionary items. For each `(subject, mark)` pair in `marks.items()`, if `mark < 40`, the subject name is added to the set. Using a set guarantees unique entries and allows instant length checks (`len(failed_subjects) == 0`).

### 3. Population Standard Deviation Formula
```python
variance = sum((p - class_avg) ** 2 for p in percentages) / total_count
std_dev = round(math.sqrt(variance), 2)
```
- **Explanation:** Calculates the variance by computing the squared deviation $(p - \mu)^2$ for each student's percentage using a generator expression, summing them, and dividing by total students. Standard deviation is the square root of variance, measuring how spread out student marks are around the class mean.

---

## 🔮 Part 3: Predict-the-Output Drills

### Drill 1:
```python
marks = {"Python": 95, "Maths": 38, "Physics": 75}
failed = {s for s, m in marks.items() if m < 40}
print(len(failed), "Maths" in failed)
```
- **Predicted Output:** `1 True`
- **Reasoning:** Only 'Maths' has marks (38) less than 40. Therefore, the set contains `{'Maths'}` with length 1.

### Drill 2:
```python
scale = ((90, "A+"), (80, "A"), (70, "B"), (0, "F"))
pct = 85.0
for min_p, g in scale:
    if pct >= min_p:
        print(g)
        break
```
- **Predicted Output:** `A`
- **Reasoning:** 85.0 is not $\ge 90$, but is $\ge 80$. Loop prints "A" and breaks immediately.

---

## 🛠️ Part 4: Live Code Modifications (Common Viva Tasks)

During the viva, the examiner might say: *"Make this change in your code and run it right now."* Here is how to execute common requested modifications:

### Challenge 1: "Change the passing mark from 40 to 45"
**Where to change:** `core/result_engine.py`  
**Line:**
```python
# Change from:
PASSING_PERCENTAGE: float = 40.0
SUBJECT_PASS_MARK: float = 40.0

# To:
PASSING_PERCENTAGE: float = 45.0
SUBJECT_PASS_MARK: float = 45.0
```

### Challenge 2: "Change the grade threshold for A+ from 90 to 85"
**Where to change:** `core/result_engine.py`  
**Line:**
```python
# In GRADE_SCALE tuple:
GRADE_SCALE = (
    (85.0, "A+", 10.0, "Outstanding"),  # Changed from 90.0 to 85.0
    (80.0, "A", 9.0, "Excellent"),
    ...
)
```

### Challenge 3: "Add a 6th subject: 'Artificial Intelligence'"
**Where to change:** `core/result_engine.py`  
**Line:**
```python
# In SUBJECTS tuple:
SUBJECTS = (
    "Python Programming",
    "Mathematics",
    "Digital Electronics",
    "Physics",
    "Professional Communication",
    "Artificial Intelligence",  # Added 6th subject
)
```
*Note: Because max total is dynamically computed as `len(SUBJECTS) * 100`, total marks will automatically adjust from 500 to 600 without any extra changes!*
