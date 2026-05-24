---
title: "verify: tomli venv install and pr266 tool builds on 847a06e20"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# verify: tomli venv install and PR 266 tool builds on 847a06e20

## Summary

Confirm plan 014 fix (`$venvPython -m pip install tomli` before `--skip-venv` deps) unblocks PR Build Validation on head `847a06e20`. Fix only if required checks fail.

---

## Problem Frame

Plan 014 venv bootstrap worked but Windows builds still failed: `tomli` was on host Python while `deps_tool.py` runs with venv Python. Fix `847a06e20` installs tomli into the venv.

---

## Requirements

- R1. Python application + parity harness green on `847a06e20`.
- R2. PR Build Validation Windows/Ubuntu tool jobs pass deps / dry-run.
- R3. Pylint matrix green.
- R4. No product code unless a required check fails.

---

## Implementation Units

- U1. Monitor CI on `847a06e20`.
- U2. Fix regressions only if tool builds fail after queue drain.

**Verification:** R1–R3 green on required checks.

---

## Sources

- Plan `2026-05-24-014`
- PR #266, head `847a06e20`
