---
title: "fix: verify-pypi empty-run cancellation storm"
type: fix
status: completed
date: 2026-05-24
origin: lfg-verify-pypi-cancelled
strategy_track: test-signal-quality
---

# fix: Verify PyPI Empty-Run Cancellation Storm

## Summary

Verify PyPI Regression runs show **cancelled** with zero jobs when triggered by failed/cancelled `Auto-Publish to PyPI` workflow_run events. Manual `workflow_dispatch` runs also stall behind the shared concurrency group. Add a gate job and split concurrency by event name.

## Problem Frame

Runs 26362999987 (workflow_dispatch) and 26363039361 (workflow_run) completed **cancelled** with `jobs: []`. All test jobs skip when `workflow_run.conclusion != success`, leaving GitHub with an empty workflow.

## Requirements

- R1. Add `gate` job that always runs and sets `run_tests` output.
- R2. Test/report jobs depend on `gate` with `run_tests == true`.
- R3. Split concurrency: `verify-pypi-${{ github.event_name }}-${{ github.ref }}`.
- R4. Manual dispatch produces a runnable workflow with jobs scheduled.

## Implementation Units

- U1. `.github/workflows/verify-pypi-regression.yml` — gate job + concurrency split.

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| workflow_dispatch | [26363113375](https://github.com/OpenKotOR/PyKotor/actions/runs/26363113375) — gate job scheduled | ✅ pass (not empty-cancelled) |
| workflow_run (failed publish) | [26363111385](https://github.com/OpenKotOR/PyKotor/actions/runs/26363111385) — gate queued | ✅ pass (gate present) |
| Local discovery | holopatcher, kotordiff, kotormcp | ✅ pass |
| Full test matrix | runner backlog | ⏳ queued |

## Scope Boundaries

- Does not change Auto-Publish trigger frequency.
- Does not modify test matrix contents.

## Sources & References

- Cancelled dispatch: https://github.com/OpenKotOR/PyKotor/actions/runs/26362999987
- Workflow: `.github/workflows/verify-pypi-regression.yml`
