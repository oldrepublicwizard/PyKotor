---
title: "fix: strict exit stderr and verify_run briefing"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Strict Exit Stderr and Verify Run Briefing (plan 125)

## Summary

Live defer shows **`active_runs=verify,fc`** but **`LFG exit:`** omits expected-after context and **`verify_run`**. Enrich strict exit stderr from briefing; add **`verify_run=`** to briefing stderr; drift wait gets top-level **`active_runs`**.

---

## Requirements

- R1. `_emit_lfg_strict_exit_stderr` appends `expected_after`, `active_runs`, `primary_action` from `lfg_agent_briefing`.
- R2. Briefing stderr includes `verify_run=` when `verify_run_id` present.
- R3. Drift wait briefing sets top-level `active_runs`; drift stderr includes `active_runs=`.
- R4. Tests; `PLAN_TRACK_CAP` 125; closeout doc bullet.

---

## Test scenarios

- T1. Strict exit with defer briefing → line includes `expected_after=closeout active_runs=fc`.
- T2. Briefing stderr with verify_run_id → `verify_run=123`.
- T3. Drift wait briefing includes top-level `active_runs`.
- T4. Plan patch expects `019–125`.
