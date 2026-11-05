# Lab 7: Fuzzing for Input Validation Bugs (Hypothesis Property-Based Testing)

**Student Name:** Dharshini V  
**SRN:** PES1UG24AM428  
**Department:** Department of Computer Science & Engineering (AIML), PES University  
**Course:** Software Engineering Lab (SE Lab)  
**Assigned System:** Course Registration Parser (`course_registration_parser.py` / `processor.py`)  
**Assigned Repo:** `SETAPESU26/L6_L7_56_course_registration` (under `LAB7/`)  
**Personal Standalone Repo:** `https://github.com/DharshiniPES/L6_L7_56_course_registration`  

---

## 📌 Lab Objectives
1. Understand the purpose, principles, and methodology of fuzz testing as a dynamic security and quality assurance technique.
2. Formulate and apply property-based fuzz testing using Python's **Hypothesis** framework (`@given(st.text() | st.none())`).
3. Detect, isolate, and analyze software crashes and input validation defects surfaced by Hypothesis's test-case shrinking engine.
4. Refactor and harden the application module through defensive programming practices to achieve 100% crash immunity against arbitrary, malformed, and null inputs.

---

## 📁 Files & Deliverables

| File | Description |
|------|-------------|
| `course_registration_parser.py` | **Fixed & hardened application module**. Handles arbitrary strings, empty strings, malformed tokens, and `None` without crashing. |
| `course_registration_parser_buggy.py` | Original naive module preserved for demonstration and reproducing Hypothesis crash findings. |
| `processor.py` | Alias entrypoint forwarding to `course_registration_parser.py`. |
| `test_course_registration_parser.py` | **Hypothesis test suite** with `@given(st.text() | st.none())` verifying crash-free operation. |
| `test_course_registration_parser_buggy.py` | Fuzz test suite executing against buggy code to verify failing edge cases. |
| `test_processor.py` | Test suite alias forwarding to `test_course_registration_parser.py`. |
| `PES1UG24AM428_DHARSHINI_V_LAB7.pdf` | **Final official PDF submission** containing terminal execution screenshots (SS1–SS4), defect analysis, code diffs, and answers to reflection questions. |
| `PES1UG24AM428_DHARSHINI_V_LAB7.docx` | Editable Word submission document. |

---

## 🔍 Fuzz Testing Findings & Defect Remediation

| Function | Falsifying Edge Case | Unhandled Exception | Root Cause & Defensive Fix |
|---|---|---|---|
| `format_course_code(code)` | `code = None` | `AttributeError: 'NoneType' object has no attribute 'split'` | Added `if code is None or not isinstance(code, str): return ""` guard. |
| `format_course_code(code)` | `code = ''` | `ValueError: not enough values to unpack (expected 2, got 0)` | Checked `if not parts: return ""` before tuple assignment. |
| `format_course_code(code)` | `code = 'CS'` | `ValueError: not enough values to unpack (expected 2, got 1)` | Added single-token handling returning `parts[0].upper()`. |
| `format_course_code(code)` | `code = 'cs 301 extra'` | `ValueError: too many values to unpack (expected 2)` | Safely joined all remaining tokens via `dept + "".join(parts[1:])`. |
| `total_credits(text)` | `text = None` | `AttributeError: 'NoneType' object has no attribute 'split'` | Added null/type guard returning `0`. |
| `total_credits(text)` | `text = ''` | `ValueError: invalid literal for int() with base 10: ''` | Checked `if not cleaned: continue` to avoid empty conversions. |
| `total_credits(text)` | `text = '4,,3'` or `'4,3,'` | `ValueError: invalid literal for int()` | Filtered empty tokens resulting from trailing or consecutive commas. |
| `total_credits(text)` | `text = 'four,three'` | `ValueError: invalid literal for int()` | Enclosed token conversion in `try...except (ValueError, TypeError): continue`. |
| `parse_student_record(line)` | `line = None` | `AttributeError: 'NoneType' object has no attribute 'split'` | Added guard returning default empty record dictionary. |
| `parse_student_record(line)` | `line = ''` or `'|'` | `IndexError: list index out of range` | Replaced direct indexing `parts[1]`, `parts[2]` with bounds-checked conditional assignment. |

---

## 🧪 Verification & Execution

### 1. Run Fixed Module with Standard Inputs (SS3):
```powershell
python course_registration_parser.py
```
Output:
```text
==== Running format_course_code ====
Formatted course code: CS301

==== Running total_credits ====
Total credits: 11

==== Running parse_student_record ====
Student record: {'srn': 'PES1UG23CS001', 'name': 'Asha', 'status': 'regular'}
```

### 2. Run Hypothesis Fuzzing Test Suite (SS4):
```powershell
pytest test_course_registration_parser.py
```
Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
plugins: hypothesis-6.170.14
collected 3 items

test_course_registration_parser.py ...                                   [100%]

============================== 3 passed in 3.07s ==============================
```
