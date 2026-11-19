# Static Analysis Issues — Library Catalog System

Line numbers refer to the original file (`original_code.py`).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command injection (Bandit B605) | Security, High | 58 | `os.system("echo ... " + filename)` passes a caller-controlled filename to the shell, so a name such as `x.txt & del *` would run extra commands. | Removed the shell call and report the export with a plain `print()`. |
| Weak MD5 hash (Bandit B324) | Security, High | 47 | Patron identifiers were hashed with MD5, which is broken and unsuitable for anything security related. | Switched to `hashlib.sha256`. |
| Arbitrary code execution through `eval` (Bandit B307, Pylint W0123) | Security, Medium | 40-43 | `calculate_fine()` evaluated a string expression, so any Python code passed in would be executed. The unused `days` variable only existed so the expression could reference it. | Replaced the expression with a fixed `FINE_PER_DAY` rate: `days_overdue * rate_per_day`, and reject negative days. |
| Hardcoded secret printed to the console | Security, Medium (found by review, not flagged by tools) | 62, 70 | `librarian_key = "MASTER_LIB_ACCESS_TOKEN_2026"` was stored in the source and printed in plain text. | Read the key from the `LIBRARIAN_KEY` environment variable and only print whether it is configured. |
| Logic bug: returning a book that was never issued | Bug, Medium (found by running the program, not flagged by tools) | 23-27, 64 | `return_book("B02")` raised B02 from 1 copy to 2 even though the library only owns one, so the catalog drifted away from real stock. | Added a `total` field per book; a return is rejected when all copies are already on the shelf. The function now returns `True`/`False`. |
| Insecure random PIN (Bandit B311) | Security, Low | 51 | `random.randint` is predictable and should not be used for PINs. | Used `secrets.randbelow()` to produce the four-digit PIN. |
| Bare `except: pass` (Bandit B110, Pylint W0702, Flake8 E722) | Bug risk, Low | 26-27 | Every error in `return_book()`, including typos, was silently swallowed. | Removed the `try` block and check `catalog.get(book_id)` explicitly. |
| Mutable default argument (Pylint W0102) | Bug risk | 15 | `active_issues=[]` was shared between calls, so issue logs leaked from one call into the next. | Default changed to `None` with a new list created per call. |
| File opened without `with` / encoding (Pylint R1732, W1514) | Reliability | 55-57 | The export file would stay open if `write()` failed and used the platform default encoding. | Used `with open(..., encoding="utf-8")` and wrote the catalog as JSON. |
| Style and quality findings (C0116, C0103, C0121, C0209, R1703, R1705, W0611, W0612, C0304 / F401, F841, E711, W292) | Style/quality | Throughout | Missing docstrings, camelCase `issueBook`, `== None`, `%` formatting, redundant `if/else`, unused `csv` import and `late_fee` variable, no final newline. | Added docstrings, renamed to `issue_book`, used `is None`, f-strings and a direct boolean return, removed unused code, added a `__main__` guard. |

## Tool results

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.32/10 (22 messages) | 10.00/10 |
| Flake8 | 6 violations | 0 |
| Bandit | 5 issues (2 High, 1 Medium, 2 Low) | No issues identified |
