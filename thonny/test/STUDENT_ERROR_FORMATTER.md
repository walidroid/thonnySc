# Student-Friendly Error Formatter

A drop-in replacement for Python's traceback system that presents errors
in a fixed three-field format designed to help beginning programmers
understand and fix mistakes quickly.

---

## Before / After Examples

### Missing colon after `if`
**Before (standard Python traceback):**
```
Traceback (most recent call last):
  File "program.py", line 1, in <module>
    if x
SyntaxError: invalid syntax
```

**After (student-friendly):**
```
Line 1: if x
Error: A colon was expected after this statement but is missing.
Fix: Add a colon (:) at the end of the line.
```

---

### Unclosed string (missing closing quote)
**Before:**
```
print('hello)
           ^
SyntaxError: EOL while scanning string literal
```

**After:**
```
Line 1: print('hello)
Error: An opened quote was never closed.
Fix: Add a closing quote (' or ") to match the opening one.
```

---

### Undefined variable (NameError)
**Before:**
```
Traceback (most recent call last):
  File "program.py", line 2, in <module>
    print(i)
NameError: name 'i' is not defined
```

**After:**
```
Line 2: print(i)
Error: Name "i" is not defined.
A variable or function with this name has not been created yet.
Fix: Define it before using it, e.g. i = 0
```

---

## Three-Field Format

Every error (SyntaxError and runtime) is always presented as:

```
Line {n}: {offending_token}
Error: {specific_reason}
Fix: {one_line_suggestion}
```

- **Line {n}** – the exact line number and the code on that line
- **Error:** – a short, specific explanation of what went wrong
- **Fix:** – one concrete step the student can take to correct the error

The line number in the first field is clickable in the Thonny shell
and jumps directly to the relevant line in the editor.

---

## Supported Error Types

| Error type | Example mistake | Shown as |
|---|---|---|
| Missing colon | `if x` | Error: A colon was expected... |
| Unclosed string | `s = 'hello` | Error: An opened quote was never closed... |
| Unexpected EOF | code ends mid-expression | Error: The code ended unexpectedly... |
| Misplaced `else` | `else:` without matching `if` | Error: 'else' must be at the same level... |
| `elif` without `if` | standalone `elif` | Error: 'elif' must follow an 'if' block... |
| `for … do` | Pascal-style loop | Error: Python uses 'for' without 'do'... |
| `while … do` | Pascal-style loop | Error: Python uses 'while' without 'do'... |
| `if … then` | BASIC-style | Error: Python uses 'if' without 'then'... |
| Unexpected indent | extra spaces at start | Error: There are extra spaces at the start... |
| Indent mismatch | wrong block alignment | Error: The indent of this line does not match... |
| NameError | variable used before definition | Error: Name "x" is not defined... |
| ZeroDivisionError | division by zero | Error: Division by zero... |
| IndexError | out-of-range list access | Error: List index out of range... |
| KeyError | missing dict key | Error: Key not found... |
| AttributeError | wrong attribute | Error: ... |

---

## How It Works

The formatter is implemented in:

- `thonny/plugins/cpython_backend/cp_back.py`
  - `_student_syntax_error()` – builds the 3-field tuple for SyntaxErrors
  - `_student_runtime_error()` – builds the 3-field tuple for runtime errors
  - `format_student_friendly_exception()` – assembles the final clickable items

The shell renderer in `thonny/shell.py` (`_show_user_exception()`) displays
these items. The first line (containing `Line {n}: ...`) carries the
filename and line number and is rendered as a clickable hyperlink.

---

## Enabling / Disabling

### Runtime (temporary)
Set the environment variable **before** starting Thonny:

```bash
# Enable student-friendly errors (default)
THONNY_STUDENT_ERRORS=1 thonny

# Disable — use standard Python tracebacks
THONNY_STUDENT_ERRORS=0 thonny
```

### Permanent (in Thonny's user configuration directory)

Edit or create `~/.thonny/configuration.ini` (Linux/macOS) or
`%APPDATA%\Thonny\configuration.ini` (Windows):

```ini
[general]
student_friendly_errors = True
```

### Programmatic check

```python
import os
if os.environ.get("THONNY_STUDENT_ERRORS", "1") == "0":
    # Use standard format_exception / traceback
    ...
else:
    # Use student-friendly formatter
    from thonny.plugins.cpython_backend.cp_back import (
        format_student_friendly_exception,
    )
    ...
```

---

## Running the Tests

The test suite (`thonny/test/test_student_errors.py`) verifies:

1. **No duplicate lines** – no "Problem on line 10" appears twice
2. **No generic sentence** – `"Python cannot understand this line."` never appears
3. **Three required fields** – every output has a `Line`, `Error:`, and `Fix:` line
4. **Correct extraction** – line numbers and tokens are accurate for 10+ mistake types
5. **All error types** – SyntaxError, IndentationError, NameError, ZeroDivisionError,
   IndexError, KeyError, AttributeError, TypeError

```bash
# Run all tests
python thonny/test/test_student_errors.py

# Or with pytest
python -m pytest thonny/test/test_student_errors.py -v
```

Expected output:
```
PASS: test_no_duplicate_lines
PASS: test_no_generic_sentence
PASS: test_three_fields_present
PASS: test_missing_colon
PASS: test_unmatched_quote
PASS: test_unexpected_eof
PASS: test_misplaced_else
PASS: test_elif_without_if
PASS: test_invalid_for_do
PASS: test_invalid_while_do
PASS: test_invalid_if_then
PASS: test_invalid_def_begin
PASS: test_unexpected_indent
PASS: test_unindent_mismatch
PASS: test_name_error_shows_missing_name
PASS: test_zero_division
PASS: test_index_error
PASS: test_key_error
PASS: test_attribute_error
PASS: test_type_error

All 20 tests passed.
```

---

## Design Principles

1. **No technical jargon in the error reason** – "A colon was expected" not "SyntaxError: invalid syntax"
2. **Concrete next step** – every `Fix:` line gives one specific action
3. **Exact token shown** – the offending line is always displayed verbatim
4. **No duplication** – the line number appears only once per error
5. **Clickable navigation** – clicking the `Line {n}: ...` field jumps to the file/line in Thonny
