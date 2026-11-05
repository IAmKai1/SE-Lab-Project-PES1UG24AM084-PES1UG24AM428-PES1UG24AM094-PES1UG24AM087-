# Lab 6: Code and Branch Coverage Analysis — Course Registration

**Course:** Software Engineering Lab (SE Lab)  
**Department:** Computer Science & Engineering (AIML), PES University  
**Student Name:** Dharshini V  
**SRN:** PES1UG24AM428  
**Assigned System:** `L6_L7_56_course_registration` (`course_registration.py`)  

---

## 📊 Coverage Results Summary

| Metric | Starter Test | Target Threshold | Final Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Statement (Line) Coverage** | `38%` (20 missed lines) | $\ge 90\%$ | **`100%`** (0 missed lines) | **Exceeded** |
| **Branch Coverage** | `32%` (18 missed branch paths) | $\ge 90\%$ | **`100%`** (24/24 branches covered) | **Exceeded** |
| **Automated Test Count** | 2 tests | — | **54 tests** (13 line + 41 branch) | **100% Passing** |

---

## 📁 Deliverables Structure

* **`course_registration.py`**: The application module under test containing `can_register()`, `waitlist_position()`, and `late_fee()`.
* **`CodeCoverageTest_course_registration.py`**: Test cases specifically exercising every statement to achieve **100% Line (Code) Coverage**.
* **`BranchCoverageTest_course_registration.py`**: Comprehensive test cases evaluating every conditional control structure (`if`, `else`) to both `True` and `False`, testing equivalence partitions and boundary conditions to achieve **100% Branch Coverage**.
* **`test_course_registration.py`**: Unified runner suite executing all 54 unit and boundary test cases.
* **`coverage_line_report.txt`**: Raw line coverage report (`coverage report -m`).
* **`coverage_branch_report.txt`**: Raw branch coverage report (`coverage report -m --branch`).

---

## 🛠️ Execution Commands

```bash
# 1. Run Line (Code) Coverage
coverage run -m pytest CodeCoverageTest_course_registration.py
coverage report -m

# 2. Run Branch Coverage
coverage run --branch -m pytest BranchCoverageTest_course_registration.py
coverage report -m

# 3. Run Combined Suite
coverage run --branch -m pytest test_course_registration.py
coverage report -m
```

---

## 🔄 Commit Log
* **Commit 1 (`9846edc`):** `Add CodeCoverageTest_course_registration.py achieving 100% statement (line) coverage`
* **Commit 2:** `Add BranchCoverageTest_course_registration.py achieving 100% branch coverage, reports and documentation`
