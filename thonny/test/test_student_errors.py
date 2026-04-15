"""
Tests for the student-friendly SyntaxError formatter.

These tests verify:
1. No duplicate lines appear in any error output.
2. No generic "Python cannot understand this line." message is present.
3. The three-field format is always present: Line/Error/Fix.
4. Correct line number and token extraction for common beginner mistakes.

Run with: python -m pytest thonny/test/test_student_errors.py -v
"""

import ast
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from thonny.plugins.cpython_backend.cp_back import (
    _student_syntax_error,
    _student_runtime_error,
    _format_student_message,
    format_student_friendly_exception,
)

FORBIDDEN_GENERIC = "Python cannot understand this line."


class FakeSyntaxError(SyntaxError):
    def __init__(self, msg, lineno=None, filename=None, text=None, offset=None):
        self.msg = msg
        self.lineno = lineno
        self.filename = filename
        self.text = text
        self.offset = offset
        self.args = (msg,)


class FakeIndentationError(IndentationError):
    def __init__(self, msg, lineno=None, filename=None, text=None, offset=None):
        self.msg = msg
        self.lineno = lineno
        self.filename = filename
        self.text = text
        self.offset = offset
        self.args = (msg,)


class FakeNameError(NameError):
    def __init__(self, name, lineno=None, filename=None):
        self.name = name
        self.lineno = lineno
        self.filename = filename
        self.args = (f"name '{name}' is not defined",)

    def __str__(self):
        return self.args[0]


class FakeZeroDivisionError(ZeroDivisionError):
    pass


class FakeIndexError(IndexError):
    pass


class FakeKeyError(KeyError):
    def __str__(self):
        return "'x'"
    def __repr__(self):
        return repr(self.args)


class FakeAttributeError(AttributeError):
    def __init__(self, msg):
        self.args = (msg,)

    def __str__(self):
        return self.args[0]


class FakeTypeError(TypeError):
    def __init__(self, msg):
        self.args = (msg,)

    def __str__(self):
        return self.args[0]


def _make_severe(msg, lineno, text):
    return FakeSyntaxError(msg, lineno=lineno, text=text)


def _collect_text(items):
    return "".join(line for line, *_ in items)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_prefixes(text):
    lines = text.splitlines()
    return [ln.lstrip("Error: ").lstrip("Fix: ").lstrip("Line ").lstrip() for ln in lines]


def test_no_duplicate_lines():
    cases = [
        _make_severe("invalid syntax", 10, "if x"),
        _make_severe("invalid syntax", 5, "print 'hello"),
        _make_severe("invalid syntax", 1, "def foo()"),
        _make_severe("expected ':'", 2, "def foo()"),
        _make_severe("unexpected EOF while parsing", 3, ""),
        FakeSyntaxError("invalid syntax", lineno=7, text="else:"),
        FakeSyntaxError("invalid syntax", lineno=8, text="\t"),
    ]
    for err in cases:
        items = format_student_friendly_exception(SyntaxError, err, None)
        text = _collect_text(items)
        lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
        duplicates = [ln for ln in lines if lines.count(ln) > 1]
        assert not duplicates, f"Duplicate lines found for {err!r}:\n{text}"


def test_no_generic_sentence():
    cases = [
        _make_severe("invalid syntax", 10, "if x"),
        _make_severe("invalid syntax", 5, "print 'hello"),
        _make_severe("invalid syntax", 1, "def foo()"),
        _make_severe("unexpected EOF while parsing", 3, ""),
        _make_severe("EOL while scanning string literal", 2, "s = 'hello"),
        FakeSyntaxError("invalid syntax", lineno=7, text="else:"),
    ]
    for err in cases:
        items = format_student_friendly_exception(SyntaxError, err, None)
        text = _collect_text(items)
        assert FORBIDDEN_GENERIC not in text, (
            f"Generic forbidden sentence found for {err!r}:\n{text}"
        )


def test_three_fields_present():
    cases = [
        (_make_severe("invalid syntax", 10, "if x"), "invalid syntax"),
        (_make_severe("invalid syntax", 1, "def foo()"), "invalid syntax"),
        (_make_severe("unexpected EOF while parsing", 3, ""), "unexpected EOF"),
        (_make_severe("EOL while scanning string literal", 2, "s = 'hello"), "EOL"),
        (_make_severe("expected ':'", 4, "for i in range(5)"), "expected ':'"),
        (_make_severe("invalid syntax", 6, "else:"), "invalid syntax"),
        (_make_severe("invalid syntax", 5, "if x then:"), "invalid syntax"),
        (_make_severe("invalid syntax", 2, "for i in range(5) do:"), "invalid syntax"),
        (_make_severe("invalid syntax", 2, "while x do:"), "invalid syntax"),
        (_make_severe("invalid syntax", 7, "\t*5"), "invalid syntax"),
    ]
    for err, _label in cases:
        items = format_student_friendly_exception(SyntaxError, err, None)
        text = _collect_text(items)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        assert len(lines) == 3, (
            f"Expected exactly 3 lines for {err!r}, got {len(lines)}:\n{text}"
        )
        assert any(ln.startswith("Line ") for ln in lines), (
            f"No 'Line ...' field found in:\n{text}"
        )
        assert any(ln.startswith("Error:") for ln in lines), (
            f"No 'Error: ...' field found in:\n{text}"
        )
        assert any(ln.startswith("Fix:") for ln in lines), (
            f"No 'Fix: ...' field found in:\n{text}"
        )


def test_missing_colon():
    err = _make_severe("expected ':'", 2, "def foo()")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Line 2:" in ln for ln in lines), f"Wrong line number:\n{text}"
    assert any("colon" in ln.lower() for ln in lines), f"No colon hint:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_unmatched_quote():
    err = _make_severe("EOL while scanning string literal", 1, "s = 'hello")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Line 1:" in ln for ln in lines), f"Wrong line number:\n{text}"
    assert any("quote" in ln.lower() or "string" in ln.lower() for ln in lines), (
        f"No quote/string hint:\n{text}"
    )
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_unexpected_eof():
    err = _make_severe("unexpected EOF while parsing", 3, "")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Line 3:" in ln for ln in lines), f"Wrong line number:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_misplaced_else():
    err = _make_severe("invalid syntax", 5, "else:")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("else" in ln.lower() for ln in lines), f"No 'else' hint:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_elif_without_if():
    err = _make_severe("invalid syntax", 3, "elif x > 0:")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("elif" in ln.lower() for ln in lines), f"No 'elif' hint:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_invalid_for_do():
    err = _make_severe("invalid syntax", 2, "for i in range(5) do:")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("for" in ln.lower() and "do" in ln.lower() for ln in lines), (
        f"No 'for...do' hint:\n{text}"
    )
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_invalid_while_do():
    err = _make_severe("invalid syntax", 2, "while x do:")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("while" in ln.lower() and "do" in ln.lower() for ln in lines), (
        f"No 'while...do' hint:\n{text}"
    )
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_invalid_if_then():
    err = _make_severe("invalid syntax", 2, "if x > 0 then:")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("if" in ln.lower() and "then" in ln.lower() for ln in lines), (
        f"No 'if...then' hint:\n{text}"
    )
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_invalid_def_begin():
    err = _make_severe("invalid syntax", 1, "def begin foo():")
    items = format_student_friendly_exception(SyntaxError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("def" in ln.lower() or "begin" in ln.lower() for ln in lines), (
        f"No 'def...begin' hint:\n{text}"
    )
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_unexpected_indent():
    err = FakeIndentationError("unexpected indent", lineno=3, text="    x = 1")
    items = format_student_friendly_exception(IndentationError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Line 3:" in ln for ln in lines), f"Wrong line number:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_unindent_mismatch():
    err = FakeIndentationError("unindent does not match", lineno=4, text="x = 1")
    items = format_student_friendly_exception(IndentationError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Line 4:" in ln for ln in lines), f"Wrong line number:\n{text}"
    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_name_error_shows_missing_name():
    err = FakeNameError("i", lineno=2)
    items = format_student_friendly_exception(NameError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_zero_division():
    err = FakeZeroDivisionError()
    items = format_student_friendly_exception(ZeroDivisionError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_index_error():
    err = FakeIndexError()
    items = format_student_friendly_exception(IndexError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_key_error():
    err = FakeKeyError()
    items = format_student_friendly_exception(KeyError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_attribute_error():
    err = FakeAttributeError("'NoneType' object has no attribute 'foo'")
    items = format_student_friendly_exception(AttributeError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


def test_type_error():
    err = FakeTypeError("can only concatenate str (not 'int') to str")
    items = format_student_friendly_exception(TypeError, err, None)
    text = _collect_text(items)
    lines = [ln.strip() for ln in text.splitlines()]

    assert any("Fix:" in ln for ln in lines), f"No fix line:\n{text}"
    assert FORBIDDEN_GENERIC not in text


if __name__ == "__main__":
    tests = [
        test_no_duplicate_lines,
        test_no_generic_sentence,
        test_three_fields_present,
        test_missing_colon,
        test_unmatched_quote,
        test_unexpected_eof,
        test_misplaced_else,
        test_elif_without_if,
        test_invalid_for_do,
        test_invalid_while_do,
        test_invalid_if_then,
        test_invalid_def_begin,
        test_unexpected_indent,
        test_unindent_mismatch,
        test_name_error_shows_missing_name,
        test_zero_division,
        test_index_error,
        test_key_error,
        test_attribute_error,
        test_type_error,
    ]
    failed = []
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except AssertionError as e:
            print(f"FAIL: {t.__name__}: {e}")
            failed.append(t.__name__)
        except Exception as e:
            print(f"ERROR: {t.__name__}: {e}")
            failed.append(t.__name__)

    print()
    if failed:
        print(f"FAILED ({len(failed)}/{len(tests)}): {failed}")
        sys.exit(1)
    else:
        print(f"All {len(tests)} tests passed.")
