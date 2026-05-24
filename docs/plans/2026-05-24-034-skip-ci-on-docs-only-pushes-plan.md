---
title: "fix: skip ci fan-out on docs-only master pushes"
type: fix
status: completed
date: 2026-05-24
origin: lfg-ci-queue-fanout
strategy_track: test-signal-quality
---

# fix: Skip CI Fan-Out on Docs-Only Master Pushes

## Summary

Repeated docs/plans merges (#278–#282) each queued Forward Commits and Auto-Publish runs, amplifying runner backlog. Add `paths-ignore: docs/**` to both workflows so documentation-only commits do not fan out heavy CI.

## Problem Frame

Three+ Forward Commits runs stuck **queued** from consecutive plan-doc squash merges. Verify PyPI `workflow_run` triggers follow every Auto-Publish completion, adding more queued runs.

## Requirements

- R1. `commit-all-to-bleeding-edge.yml`: ignore pushes that only change `docs/**`.
- R2. `publish-pypi-auto.yml`: ignore docs-only pushes (keep `workflow_dispatch`).
- R3. Workflow/product path pushes still trigger both workflows.
- R4. Record verification in plan 033/028.

## Implementation Units

- U1. Add `paths-ignore` to both workflow `on.push` blocks.

## Verification

| Check | Expected |
|-------|----------|
| Docs-only push | FC + Auto-Publish not triggered |
| `.github/workflows` push | still triggers |
| Local discovery | unchanged |

## Scope Boundaries

- Does not cancel existing queued runs.
- Does not change verify-pypi matrix.

## Sources & References

- Queued FC: runs 26363209835, 26363169705, 26363111619
- Forward Commits: `.github/workflows/commit-all-to-bleeding-edge.yml`
- Auto-Publish: `.github/workflows/publish-pypi-auto.yml`
