# Contributing to PyLedger 🤝

Thank you for considering a contribution! PyLedger is Apache-2.0 licensed and community-driven. Every contribution — code, docs, tests, translations, bug reports — matters.

## Code of Conduct

By participating you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Be kind, be professional.

## How to contribute

### 1. Reporting bugs
- Search [existing issues](../../issues) first to avoid duplicates.
- Use the **Bug report** template: version, Python version, minimal reproducer, expected vs actual behavior, traceback.

### 2. Suggesting features
- Use the **Feature request** template. Explain the accounting use-case, proposed API, and alternatives.
- Accounting-correctness matters: new posting logic must keep `debits == credits`.

### 3. Code contributions
1. Fork the repo and create a branch: `git checkout -b feat/short-name` (or `fix/...`, `docs/...`).
2. Set up the environment:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e ".[database,cli]"
   ```
3. Make focused changes (one concern per PR).
4. Run the gates before pushing:
   ```bash
   pytest test_pyledger.py -q
   black --check pyledger/ || black pyledger/
   flake8 pyledger/ --max-line-length=100
   ```
5. Add/extend tests for any behavior change (`test_pyledger.py` — full suite must stay green: **214 passing** is the bar).
6. Update docs: `README.md` API section and/or `CHANGELOG.md` when user-facing behavior changes.
7. Open a Pull Request against `main` using the PR template. Link related issues (`Fixes #123`).

## Accounting rules for contributors (important)

- **Never use `float` for money** — `Decimal` everywhere, via `format_amount()`.
- **Never allow unbalanced postings** — `JournalEntry.validate()` is the gate.
- **Never mutate posted entries** — add `reverse()` entries instead.
- **New account types / posting rules** must update `NORMAL_BALANCE`, trial-balance helpers, and reports.
- **Public API changes** must stay backward compatible or go through deprecation (alias + warning, remove after one minor).

## Style guide

- `black` (line length 100), `flake8`, type hints on new public functions.
- Docstrings on public classes/methods with a runnable example where practical.
- No secrets, no hardcoded credentials, no network calls in the core library (API/PDF extras excepted).

## Review process

Maintainers review within a few days. Expect requests for tests/docs. Two approvals merge. After merge, your contribution is released under Apache-2.0 in the next version — thank you! ⭐
