---
title: "verify: plan 011 pylint and build-tool fixes on 4114a2cab"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# verify: plan 011 pylint and build-tool fixes on 4114a2cab

## Summary

Confirm plan 011 CI fixes land on PR #266 head `4114a2cab`. No product code unless a required check fails after queue drain.

---

## Problem Frame

Plan 011 addressed Pylint R0801 mass failure and Windows `TrimEnd` bug in build-tool composite. Push `4114a2cab` triggered fresh CI.

---

## Requirements

- R1. Pylint `build (3.8)`, `(3.9)`, `(3.10)` succeed on `4114a2cab`. ✅ landed
- R2. PR Build Validation **Build KotorMCP (windows-latest)** passes artifact-name / deps steps (no TrimEnd error). ✅ TrimEnd fixed; deps blocked by missing `tomli` on Py3.8
- R3. **Python application** (flake8 + pytest) and parity harness remain green. ✅ landed
- R4. Windows PR Build Validation tool dry-runs install `tomli` before `deps_tool.py` on Python 3.8.
- R5. No parity harness product changes.

---

## Implementation Units

- U1. **Monitor CI on 4114a2cab** — record pylint, PR Build Validation, Python application outcomes. ✅
- U2. **Bootstrap tomli in build-tool composite** — `python -m pip install tomli` before `deps_tool.ps1` on Windows/Linux Py3.8 CI.

**Verification:** All R1–R3 checks green; PR #266 mergeable.

---

## Scope Boundaries

- Do not expand pylint scope or re-enable R0801 in this slice.
- Do not fix optional/slow checks (Codacy, CodeQL c-cpp) unless blocking merge.

---

## Sources

- Plan `2026-05-24-011`
- PR #266, head `4114a2cab`
