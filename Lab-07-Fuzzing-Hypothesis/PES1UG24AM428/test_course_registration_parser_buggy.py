from hypothesis import given, strategies as st
from course_registration_parser_buggy import format_course_code, total_credits, parse_student_record

@given(st.text() | st.none())
def test_format_course_code_no_crash(s):
    try:
        format_course_code(s)
    except Exception as e:
        assert False, f"format_course_code crashed with: {e}"

@given(st.text() | st.none())
def test_total_credits_no_crash(s):
    try:
        total_credits(s)
    except Exception as e:
        assert False, f"total_credits crashed with: {e}"

@given(st.text() | st.none())
def test_parse_student_record_no_crash(s):
    try:
        parse_student_record(s)
    except Exception as e:
        assert False, f"parse_student_record crashed with: {e}"
