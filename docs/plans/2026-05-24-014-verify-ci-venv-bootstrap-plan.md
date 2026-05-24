---
title: "verify: ci venv bootstrap and pr266 tool builds on f86697ae5"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# verify: CI venv bootstrap and PR 266 tool builds on f86697ae5

## Summary

Confirm plan 013 fix (`python -m venv` + `pythonExePath` skip-venv path) unblocks PR Build Validation on head `f86697ae5`. Fix only if required checks fail.

---

## Problem Frame

Plan 013 verified `tomli` bootstrap but Windows builds still failed when `install_python_venv.ps1` attempted python.org installs in CI. Fix `f86697ae5` creates venv from Actions-hosted Python before `deps_tool.ps1`.

---

## Requirements

- R1. **Python application** and parity harness remain green on `f86697ae5`.
- R2. PR Build Validation Windows + Ubuntu tool matrix jobs pass deps / dry-run (venv bootstrap + **tomli installed into venv python**).
- R3. Pylint matrix remains green.
- R4. No product code unless a required check fails.

---

## Implementation Units

- U1. Monitor CI on `f86697ae5` for Python application, PR Build Validation, Pylint.
- U2. Fix regressions only if tool build jobs still fail after queue drain.

**Verification:** R1–R3 green on required checks.

---

## Sources

- Plan `2026-05-24-013`
- PR #266, head `f86697ae5`
