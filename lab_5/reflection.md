# Reflection

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the style findings: the unused `csv` import, the missing final
newline, `== None`, the `%` string formatting and the missing docstrings. Each
one has a single obvious fix and cannot change what the program does.

The hardest was the `eval()` in `calculate_fine()`. Removing it meant deciding
what the function is actually supposed to do. The caller passed the string
`"days * 2.0"`, so the real requirement was a fixed per-day rate. I turned that
into a `FINE_PER_DAY` constant and made the function plain arithmetic. The
`return_book()` bug was also tricky, because no tool reported it. I only
noticed it because B02 ended up with more copies than the library owns, and
fixing it needed a new `total` field in the catalog.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Not strictly, but Bandit's B311 warning on `random.randint` depends on context.
For a coin toss or a game it would be a false positive. Here the number is a
patron PIN, so the warning was valid and I switched to `secrets`. Some Pylint
convention messages, such as the request to merge the `if/else` into a single
`return`, are about taste rather than correctness, but following them still
made the code shorter.

## 3. How would you integrate static analysis tools into your actual software development workflow?

I would run Flake8 and Pylint on every save through the editor, and add all
three tools as a pre-commit hook so issues are caught before a commit. In CI,
I would run them on every pull request and fail the build on any Bandit
finding of Medium severity or higher, or a Pylint score below an agreed
threshold such as 9.0. Reports would be saved as build artifacts so reviewers
can see trends over time.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- Pylint went from 5.32/10 to 10.00/10, Flake8 from 6 violations to 0 and
  Bandit from 5 issues to none.
- The two High-severity problems (shell injection and MD5) and the `eval`
  code-execution risk are gone, and the librarian key is no longer printed.
- `return_book()` can no longer inflate the stock count, and errors are no
  longer hidden by `except: pass`.
- Every function now has a docstring and a snake_case name, the export file is
  closed safely and written as readable JSON, and the `__main__` guard means
  the module can be imported without running the demo.
