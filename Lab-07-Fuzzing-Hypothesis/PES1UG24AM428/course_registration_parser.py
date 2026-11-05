# -*- coding: utf-8 -*-
"""
Course Registration Parser Module (Hardened & Defensive Implementation)
Department of Computer Science & Engineering (AIML), PES University
Student: Dharshini V (PES1UG24AM428)
Course: Software Engineering Lab - Lab 7: Fuzzing for Input Validation Bugs

Robust input validation module that safely parses course codes, credit tallies,
and student pipe-separated records against arbitrary, malformed, or null inputs.
"""


def format_course_code(code):
    """
    Formats 'cs 301' as 'CS301'.
    Safely handles any input type, empty values, or malformed strings without crashing.
    """
    if code is None or not isinstance(code, str):
        return ""
    parts = code.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].upper()
    dept = parts[0].upper()
    number = "".join(parts[1:])
    return dept + number


def total_credits(text):
    """
    Adds up comma-separated course credits.
    Safely ignores empty tokens, non-numeric values, whitespace, and None.
    """
    if text is None or not isinstance(text, str):
        return 0
    total = 0
    for item in text.split(','):
        cleaned = item.strip()
        if not cleaned:
            continue
        try:
            val = int(cleaned)
            total += val
        except (ValueError, TypeError):
            # Ignore malformed or non-integer tokens gracefully
            continue
    return total


def parse_student_record(line):
    """
    Parses 'SRN|name|status' into a dictionary.
    Safely handles missing fields, empty strings, delimiter mismatches, and None.
    """
    default_record = {"srn": "", "name": "", "status": ""}
    if line is None or not isinstance(line, str):
        return default_record
    
    parts = [p.strip() for p in line.split('|')]
    srn = parts[0].upper() if len(parts) > 0 else ""
    name = parts[1] if len(parts) > 1 else ""
    status = parts[2].lower() if len(parts) > 2 else ""
    
    return {"srn": srn, "name": name, "status": status}


def main():
    try:
        print("==== Running format_course_code ====")
        value = input("Enter a course code as DEPT NUMBER (e.g. cs 301): ")
        if not value:
            value = "cs 301"
        print("Formatted course code:", format_course_code(value))

        print("\n==== Running total_credits ====")
        value = input("Enter course credits separated by commas (e.g. 4,3,4): ")
        if not value:
            value = "4,3,4"
        print("Total credits:", total_credits(value))

        print("\n==== Running parse_student_record ====")
        value = input("Enter a student record as SRN|name|status (e.g. pes1ug23cs001|Asha|regular): ")
        if not value:
            value = "pes1ug23cs001|Asha|regular"
        print("Student record:", parse_student_record(value))
    except EOFError:
        pass


if __name__ == "__main__":
    main()
