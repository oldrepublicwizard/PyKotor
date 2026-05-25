---
title: "feat: dispatch-on-proceed gh workflow helpers"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: Dispatch-on-Proceed Workflow Helpers (plan 074)

## Gaps

- G1. `recommended_action` tells agents to `workflow_dispatch` verify/FC but no scripted helper exists.
- G2. Plan 066 cancel+dispatch steps are manual `gh` one-liners with no dry-run preview in preflight JSON.
- G3. `refresh_verify_dispatch` / `refresh_fc_dispatch` proceed paths lack parity with `--auto-apply-on-proceed` for docs.

## Requirements

- R1. `_build_dispatch_plan` maps `refresh_verify_dispatch` and `refresh_fc_dispatch` to workflow file, ref, inputs.
- R2. `--dispatch-on-proceed` embeds `dispatch_on_proceed` dry-run in monitor preflight JSON when eligible.
- R3. `--dispatch-on-proceed --execute` runs `gh workflow run`; optional `--cancel-stale` runs `gh run cancel` on stale active run first.
- R4. Skip dispatch when `defer_lfg_pr` or proceed reason not dispatch-eligible.
- R5. Unit tests for plan building, defer skip, and execute path (mocked subprocess).
- R6. Bump `PLAN_TRACK_CAP` to `074`.

## Test scenarios

- T1. Verify SHA stale → dispatch plan includes verify workflow + optional cancel step.
- T2. FC non-docs stale → dispatch plan for FC workflow.
- T3. Deferred checkpoint → no dispatch plan.
- T4. Execute path calls `gh workflow run` with expected args (mocked).
