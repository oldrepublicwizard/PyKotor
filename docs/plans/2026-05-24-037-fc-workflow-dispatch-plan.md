---
title: "feat: forward-commits workflow_dispatch recovery"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: Forward Commits workflow_dispatch Recovery

## Summary

Forward Commits run [26363271048](https://github.com/OpenKotOR/PyKotor/actions/runs/26363271048) has been **queued** since #283 with no runner progress and no manual retrigger path. Add `workflow_dispatch` to `.github/workflows/commit-all-to-bleeding-edge.yml` and fix the merge job `if` so dispatch events are not blocked by missing `head_commit`. Merging this change triggers FC via push (non-docs path).

## Problem Frame

Plans 035–036 cancelled stale runs and refreshed Verify PyPI dispatch, but FC lacks `workflow_dispatch`. Cancelling the stalled FC run would lose the post-#283 trigger with no way to re-run except another non-docs push.

## Requirements

- R1. Add `workflow_dispatch` to Forward Commits workflow (default ref: master).
- R2. Merge job runs on `workflow_dispatch` even when `github.event.head_commit` is absent.
- R3. Cherry-pick step continues to use `${{ github.sha }}` (dispatch ref HEAD).
- R4. Local FC dry-run on current master tip succeeds (plan 030 pattern).
- R5. Update plan 020 FC row; mark plan 037 completed after merge.

## Implementation Units

- U1. `.github/workflows/commit-all-to-bleeding-edge.yml` — add `workflow_dispatch`; fix job `if`.
- U2. Docs — plan 037 verification; plan 020 FC evidence row.

## Test Scenarios

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | workflow_dispatch job condition | job not skipped on dispatch |
| T2 | Local FC dry-run | cherry-pick + workflow restore |
| T3 | Push merge of U1 | FC workflow triggered (paths not docs-only) |

## Verification

| Check | Evidence | Result |
|-------|----------|--------|
| workflow_dispatch | added to `commit-all-to-bleeding-edge.yml` | ✅ pass |
| Job if | dispatch OR non-skip-edge push | ✅ pass |
| Local FC dry-run | cherry-pick f2feedf3c + workflow restore | ✅ pass |
| Local discovery | 3 CLI tools | ✅ pass |
| Post-merge FC | triggered by `.github/workflows` push | ⏳ pending merge |

## Scope Boundaries

- Does not change cherry-pick or workflow-restore logic (#277).
- Does not wait for full runner backlog clearance.
- Verify PyPI matrix unchanged.

## Sources & References

- Stalled FC: https://github.com/OpenKotOR/PyKotor/actions/runs/26363271048
- Workflow: `.github/workflows/commit-all-to-bleeding-edge.yml`
- Plan 030 dry-run: `docs/plans/2026-05-24-030-finalize-post-277-ci-evidence-plan.md`
