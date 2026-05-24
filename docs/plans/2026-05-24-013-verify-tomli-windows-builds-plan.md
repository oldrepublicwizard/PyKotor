---
title: "verify: tomli bootstrap and pr266 windows tool builds on e0bf16c79"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# verify: tomli bootstrap and PR 266 Windows tool builds on e0bf16c79

## Summary

Confirm plan 012 `tomli` bootstrap fix unblocks Windows PR Build Validation dry-runs on head `e0bf16c79`. Fix only if a required check fails after queue drain.

---

## Problem Frame

Plan 012 verified plan 011 (Pylint + TrimEnd) and found Windows tool builds failing at `deps_tool.py` with missing `tomli` on Python 3.8. Fix landed in `e0bf16c79`.

---

## Requirements

- R1. **Python application** (flake8 + pytest) and parity harness remain green on `e0bf16c79`.
- R2. PR Build Validation Windows jobs pass deps / dry-run steps (use Actions-hosted `python -m venv`, skip `install_python_venv.ps1`).
- R3. Pylint matrix remains green (regression guard).
- R4. No product code changes unless a required check fails.

---

## Implementation Units

- U1. **Monitor CI on e0bf16c79** — record Python application, PR Build Validation, Pylint outcomes.
- U2. **Bootstrap CI venv from setup-python** — create venv with `python -m venv`, set `pythonExePath`, call `deps_tool.ps1 --skip-venv`.

**Verification:** R1–R3 green; PR #266 mergeable on required checks.

---

## Scope Boundaries

- Do not run full release builds in this slice (dry-run validation only).
- Do not fix optional scans (Codacy) unless blocking merge.

---

## Sources

- Plan `2026-05-24-012`
- PR #266, head `e0bf16c79`
