---
title: "feat: dispatch verify-pypi after auto-publish success"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: Dispatch Verify PyPI After Auto-Publish Success

## Summary

Plan 043 removed noisy `workflow_run` verify triggers. Restore post-publish verification by dispatching `verify-pypi-regression.yml` from Auto-Publish when packages actually publish successfully (replaces workflow_run with an explicit success-only hook).

## Problem Frame

Without `workflow_run`, successful PyPI publishes no longer trigger regression tests until manual dispatch or weekly cron. Auto-Publish already knows when packages were published.

## Requirements

- R1. New job in `publish-pypi-auto.yml` after `publish-packages` succeeds.
- R2. Run only when `discover-packages` output is non-empty and `publish-packages` result is `success`.
- R3. Use `actions: write` to `createWorkflowDispatch` for `verify-pypi-regression.yml` on default branch with `pypi_source: pypi`.
- R4. Do not dispatch when no packages published or publish failed.
- R5. Update plan 020/043 deferred note; mark plan 044 completed.

## Implementation Units

- U1. `.github/workflows/publish-pypi-auto.yml` — `trigger-verify-pypi` job.
- U2. Docs — plan 044, plan 020 row.

## Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | Job if condition | success + packages non-empty |
| T2 | Permissions | actions: write on job |
| T3 | No packages | job skipped |

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| trigger-verify-pypi job | publish-pypi-auto.yml | ✅ pass |
| Job if | packages non-empty + publish success | ✅ pass |
| Permissions | actions: write on job | ✅ pass |
| Dispatch inputs | pypi_source=pypi, default branch ref | ✅ pass |
| Post-merge test | FC + auto-publish on workflow push | ⏳ pending merge |

## Scope Boundaries

- Does not re-dispatch stale verify 26364391944.
- Does not change verify-pypi matrix.

## Sources & References

- Plan 043 deferred hook
- Publish workflow: `.github/workflows/publish-pypi-auto.yml`
- Verify workflow: `.github/workflows/verify-pypi-regression.yml`
