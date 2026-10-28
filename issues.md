# Static Analysis Issues — `expense_tracker.py` (before fix)

Tool versions: Pylint, Flake8, Bandit (Python 3.11). Line numbers refer to the original file.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell injection via `os.system` | Security (Bandit B605, High) | 61 | `os.system("xdg-open " + path)` runs a shell with string concatenation. A malicious `path` such as `file.txt; rm -rf ~` would execute arbitrary commands (CWE-78). | Replaced with `subprocess.run([viewer, path], check=False)` (no shell) and resolved the viewer with `shutil.which("xdg-open")`; raise if viewer missing. |
| Insecure temporary file with `mktemp` | Security (Bandit B306, Medium) | 55 | `tempfile.mktemp()` only returns a name and is vulnerable to TOCTOU / symlink attacks between name generation and file creation (CWE-377). Deprecated. | Replaced with `tempfile.NamedTemporaryFile(mode="w", suffix=".txt", dir=REPORT_DIR, delete=False)` which atomically creates the file; create `REPORT_DIR` with `os.makedirs(..., exist_ok=True)`. |
| Hardcoded `/tmp` directory | Security (Bandit B108, Medium) | 8 | `REPORT_DIR = "/tmp/expense_reports"` hardcodes a world-writable temp path, fragile on Windows and prone to collisions (CWE-377). | Built with `os.path.join(tempfile.gettempdir(), "expense_reports")` so the correct temp dir is used per-OS with no `/tmp` literal. |
| Hardcoded password + unsafe comparison | Security (Bandit B105, Low) + correctness | 5, 49–50 | `BANK_SYNC_PASSWORD = "demo-sync-pass"` ships a secret in source; `password == BANK_SYNC_PASSWORD` uses a non-timing-safe `==` comparison. | Secret now comes from env var `EXPENSE_TRACKER_SYNC_PASSWORD` (default `""` for demo) and is compared with `hmac.compare_digest()`. No password literal remains in source. |
| Overly broad `except Exception` | Quality (Pylint W0718) | 38–42 | `biggestExpense()` catches all `Exception` and returns `None`, hiding real bugs (e.g. `TypeError`). Empty list is the only expected case (`ValueError` from `max`). | Removed try/except; explicit `if not expenses: return None` before `max(...)`. Clearer and no hidden failures. |
| `global` statement + constant naming | Quality (Pylint W0603, C0103) | 7, 28–30 | `monthly_budget = 20000` reassigned via `global monthly_budget` in `setBudget()`. Globals make state hard to track, and the name violates UPPER_CASE for a module constant. | Introduced `DEFAULT_MONTHLY_BUDGET = 20000` constant plus mutable `_budget_state = {"monthly": ...}` dict; `set_budget()`/`get_budget()` mutate the dict, so no `global` statement is needed. |
| Non-PEP 8 names + missing docstrings | Style (Pylint C0103, C0114, C0116; Flake8) | 11, 20, 28, 33, 38, 44, 49, 53, 59, 64 | camelCase functions (`addExpense`, `totalByCategory`, `setBudget`, …), camelCase args/locals (`newBudget`, `reportPath`), and no module/function docstrings. Hurts readability and Pylint score (was 5.27/10). | Renamed everything to `snake_case` (`add_expense`, `total_by_category`, …), added module + per-function docstrings. |
| Loop/style issues + import-time side effect | Style/correctness (Pylint C0200; Flake8 E203, E302, E261, E501) | 15, 44–46, 74, 77, 79 | `for i in range(len(expenses))` instead of `enumerate`; `{"amount" : amount}` spacing (E203); missing 2 blank lines (E302); 1-space inline comment (E261); 93-char line (E501); `main()` runs on import with no `if __name__ == "__main__":` guard. | Used `enumerate(expenses, start=1)`; fixed spacing/blank lines/comments/line length (all lines ≤ 79 chars); wrapped demo in `main()` + `if __name__ == "__main__":` guard; also made timestamps timezone-aware (`timezone.utc`). |

## Result after fix

- `python expense_tracker.py` output is byte-identical to the original demo (verified).
- Pylint: **5.27/10 → 10.00/10**
- Flake8: **4 warnings → 0 warnings**
- Bandit: **1 High + 2 Medium + 1 Low → 0 High, 0 Medium** (only 2 residual Lows: `import subprocess` notice B404 and `subprocess_without_shell_equals_true` B603, both safe by design — no `shell=True`, argument list only, viewer resolved via `shutil.which`).
