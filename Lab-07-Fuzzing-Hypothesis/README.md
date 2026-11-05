# Lab 7: Fuzzing for Input Validation Bugs

**Course:** Software Engineering Lab (SE Lab)  
**Department:** Computer Science & Engineering (AIML), PES University  

## Objective
To explore fuzz testing as a dynamic security and quality assurance technique by identifying and fixing bugs in assigned Python programs using the **Hypothesis** property-based fuzzing library. Detect edge-case inputs, understand test-case shrinking, and harden code through defensive programming.

## Member Deliverables Directory
Each team member maintains their assigned program analysis in their dedicated SRN folder:
- `PES1UG24AM428/` — **Dharshini V** (Assigned: `L6_L7_56_course_registration` / `LAB7` / `course_registration_parser.py`)
  - **Standalone Repo:** `https://github.com/DharshiniPES/L6_L7_56_course_registration`
  - **Fuzzing Engine:** Hypothesis (`@given(st.text() | st.none())`)
  - **Defects Fixed:** 11 edge cases (`None`, empty strings, delimiter mismatches, trailing commas, non-numeric values, unpacking errors)
  - **Status:** 3/3 Hypothesis tests passing with 0 crashes.
  - **Deliverables:** `course_registration_parser.py` (fixed), `processor.py`, `test_course_registration_parser.py`, `test_processor.py`, `PES1UG24AM428_DHARSHINI_V_LAB7.pdf` and `PES1UG24AM428_DHARSHINI_V_LAB7.docx`.
- `PES1UG24AM084/` — Dhareen G
- `PES1UG24AM094/` — Divyansh
- `PES1UG24AM087/` — Dhruv Talavat
