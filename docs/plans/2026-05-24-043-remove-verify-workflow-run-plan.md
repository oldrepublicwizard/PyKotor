---
title: "fix: remove verify-pypi workflow_run trigger"
type: fix
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# fix: Remove Verify PyPI workflow_run Trigger

## Summary

Verify PyPI `workflow_run` runs keep appearing **pending** with `jobs: []` (e.g. [26364480958](https://github.com/OpenKotOR/PyKotor/actions/runs/26364480958)) when Auto-Publish completes. Gate job fixes dispatch runs but `workflow_run` noise persists. Remove `workflow_run` trigger; retain `workflow_dispatch` and weekly `schedule`.

## Problem Frame

Plans 031/040 validated dispatch scheduling. Auto-Publish completions still spawn workflow_run verify runs that stall pending with empty jobs, adding queue noise without running tests.

## Requirements

- R1. Remove `workflow_run` block from `.github/workflows/verify-pypi-regression.yml`.
- R2. Update workflow header comment to match triggers.
- R3. Cancel pending workflow_run [26364480958](https://github.com/OpenKotOR/PyKotor/actions/runs/26364480958).
- R4. Leave dispatch [26364391944](https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944) unchanged.
- R5. Update plan 020; mark plan 043 completed.

## Implementation Units

- U1. `.github/workflows/verify-pypi-regression.yml` — remove workflow_run trigger.
- U2. Docs — plan 020, 043 verification.

## Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | YAML triggers | dispatch + schedule only |
| T2 | Cancel 26364480958 | cancelled |
| T3 | Gate job logic | still handles dispatch/schedule |

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| workflow_run removed | verify-pypi-regression.yml | ✅ pass |
| Pending run cancelled | 26364480958 | ✅ pass |
| Dispatch unchanged | 26364391944 queued | ⏳ runner backlog |
| Gate logic | dispatch/schedule paths retained | ✅ pass |

## Scope Boundaries

- Does not add publish→dispatch hook (deferred; weekly + manual suffice).
- Does not re-dispatch verify.

## Sources & References

- Pending empty: https://github.com/OpenKotOR/PyKotor/actions/runs/26364480958
- Plan 031: gate job fix
- Workflow: `.github/workflows/verify-pypi-regression.yml`
