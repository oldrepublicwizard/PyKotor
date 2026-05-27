---
title: "fix: doc patch accuracy and closeout proceed hints"
type: fix
status: completed
date: 2026-05-24
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Doc Patch Accuracy + Closeout Proceed Hints (plan 081)

## Summary

Fix oversimplified doc-apply `changes` flags, sync Last CI check / Track status section headers on closeout, and route `proceed_hint` to `--lfg-closeout` for terminal doc updates.

---

## Problem Frame

Plan 080 added `--lfg-closeout` but `proceed_hint` still recommends `--lfg-refresh` for `update_monitoring_docs`. Doc apply reports `changes.*: true` while `would_change: false` because regex matched without content delta. Solution doc Last CI check header remains `(plan 066)` and Track status still says runs are pending completion.

---

## Requirements

- R1. `_build_proceed_hint`: `update_monitoring_docs` → `--lfg-closeout`; dispatch reasons keep `--lfg-refresh`; `investigate_ci_drift` → `--lfg-refresh --dry-run`.
- R2. Blocked `classify_fc_stale_gap` hint mentions `git fetch origin master`.
- R3. Patch updates `## Last CI check (plan NNN)` header to `PLAN_TRACK_CAP`.
- R4. Patch updates Track status when CI terminal (both runs success).
- R5. `changes` dict reflects actual content delta, not regex match alone.
- R6. Tests; bump `PLAN_TRACK_CAP` to `081`.

---

## Scope Boundaries

- No workflow YAML changes.
- No PR merge in this plan.

---

## Implementation Units

- U1. Hint routing + blocked classify message — `.github/scripts/local_verify_pypi_slice.py`
- U2. Doc patch header/track status + accurate changes — same file
- U3. Tests — `test_local_verify_checkpoint.py`
- U4. Docs — solution closeout agent loop, AGENTS.md

---

## Test scenarios

- T1. terminal proceed_hint contains `--lfg-closeout`.
- T2. patch updates Last CI check section header plan number.
- T3. changes false when table row content unchanged.
