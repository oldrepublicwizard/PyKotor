---
title: "verify: local fc dry-run and fresh verify dispatch"
type: verify
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# verify: Local FC Dry-Run and Fresh Verify Dispatch

## Summary

Verify PyPI [26364391944](https://github.com/OpenKotOR/PyKotor/actions/runs/26364391944) remains queued on SHA `1c64bea` (pre-#292/#293). FC [26364669571](https://github.com/OpenKotOR/PyKotor/actions/runs/26364669571) merge job still pending. Run local forward-commits cherry-pick dry-run, cancel stale verify dispatch, re-dispatch on current master tip, and record evidence in plan 020.

## Problem Frame

Runner backlog blocks CI closure. Verify dispatch targets stale master; `test-cli-tools` checkout would not reflect #292–#294 fixes. Local FC dry-run validates bleeding-edge sync logic without waiting on merge job.

## Requirements

- R1. Local FC dry-run: cherry-pick `master` onto `origin/bleeding-edge` with conflict auto-resolve + workflow restore (matches `commit-all-to-bleeding-edge.yml`).
- R2. Cancel stale verify 26364391944; `workflow_dispatch` verify on master tip.
- R3. Confirm new verify run has **Check trigger** job scheduled.
- R4. Local gate simulation + `discover_tools.py --cli-only` smoke pass.
- R5. Update plan 020 verification rows; mark plan 046 completed.

## Implementation Units

- U1. **Local FC dry-run** — ephemeral worktree/branch.
- U2. **CI hygiene** — cancel stale verify; fresh dispatch.
- U3. **Docs** — plan 020, plan 046 verification.

## Verification

| Check | Expected | Result |
|-------|----------|--------|
| FC dry-run | cherry-pick completes | ✅ `c3d17d579` (docs conflict auto-resolved) |
| Stale verify cancelled | 26364391944 | ✅ cancelled |
| Fresh verify dispatch | Check trigger on master tip | ✅ [26364756399](https://github.com/OpenKotOR/PyKotor/actions/runs/26364756399) queued `2946d823e` |
| Local smoke | discover + gate script | ✅ pass |

## Scope Boundaries

- Does not push to `bleeding-edge` (dry-run only).
- No workflow YAML changes unless dry-run reveals breakage.

## Sources & References

- FC workflow: `.github/workflows/commit-all-to-bleeding-edge.yml`
- Verify workflow: `.github/workflows/verify-pypi-regression.yml`
- Plan 020: `docs/plans/2026-05-24-020-verify-pypi-regression-post-268-plan.md`
