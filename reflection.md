# Reflection — Lab 5: Static Code Analysis

## 1. What were the most important issues the tools found, and which one was the most serious?

The most serious was the **High-severity shell injection** (Bandit B605):
`os.system("xdg-open " + path)`. Because the path is concatenated into a shell
command, a crafted filename could run arbitrary commands. It is the only issue
that could lead to full compromise of the machine running the tracker, so I
fixed it first.

Next were the two **Medium** Bandit issues: insecure `tempfile.mktemp()`
(race/symlink attack) and the hardcoded `/tmp` path. Both relate to unsafe file
handling. The hardcoded password (B105) is lower severity in this demo but
matters in real code because secrets in source leak via git. Pylint's
`broad-exception-caught` and `global-statement` findings were the most
important quality issues because they hide bugs and make state unpredictable.

## 2. How did fixing these issues improve the quality, security, and maintainability of the code?

- **Security:** No shell is invoked anymore (`subprocess.run` with an argument
  list), temp files are created atomically with `NamedTemporaryFile`, the temp
  directory is resolved per-OS, and the password comes from an environment
  variable compared with `hmac.compare_digest()`. The attack surface for
  command injection, file races, and secret leakage is removed.
- **Quality/correctness:** `biggest_expense()` now explicitly handles the empty
  case instead of swallowing every exception; timezone-aware timestamps avoid
  naive-datetime bugs; the `if __name__ == "__main__":` guard stops the demo
  from running on import.
- **Maintainability:** PEP 8 `snake_case` names, module and function
  docstrings, `enumerate()` loop, `get_budget()` accessor instead of a raw
  global, and lines under 79 characters make the code readable and keep all
  three tools clean (Pylint 10.00/10, Flake8 0 warnings). Future contributors
  can understand each function without reading its body.

I verified after every change that `python expense_tracker.py` prints exactly
the same demo output as before, so behaviour was preserved.

## 3. What did you learn about the differences and strengths of Pylint, Flake8, and Bandit?

- **Pylint** checks deep code quality and conventions: naming, docstrings,
  `global`, broad exceptions, `consider-using-enumerate`. It gave the clearest
  single number (5.27 → 10.00) and taught me the most about Python idioms.
- **Flake8** is narrow but fast: purely mechanical style (spacing, blank
  lines, line length). It caught things Pylint worded differently (E203, E302,
  E261, E501) and enforces a consistent visual style.
- **Bandit** is the only security-focused tool. Pylint/Flake8 said nothing
  about `os.system` or `mktemp`, yet those were the most dangerous lines.
  Conversely Bandit says nothing about naming or docstrings.

The lesson: the tools are complementary — Flake8 for style, Pylint for
maintainability, Bandit for security. Running only one would miss whole
classes of problems. None of them replaces testing or review: Bandit's two
residual Lows (`import subprocess`, `subprocess_without_shell_equals_true`)
are safe in my fixed code but still reported, so human judgement is needed.

## 4. What will you do differently when writing Python code in the future?

1. **Never build shell commands from strings** — always use `subprocess` with
   an argument list and no `shell=True`, and resolve executables explicitly.
2. **Never commit secrets** — read passwords/tokens from environment variables
   (or a secret manager) and compare with `hmac.compare_digest()`.
3. **Use safe temp-file APIs** (`NamedTemporaryFile`/`mkstemp`) and
   `tempfile.gettempdir()` instead of hardcoded `/tmp` and `mktemp`.
4. **Write tool-clean code from the start:** `snake_case` names, docstrings,
   no `global` (use parameters, return values, or small classes/dicts), narrow
   exceptions, `enumerate`, short lines, and a `main()` guard. I will run
   `pylint`, `flake8`, and `bandit` before every commit, aiming for Pylint
   ≥ 9.5 and zero High/Medium Bandit issues.
