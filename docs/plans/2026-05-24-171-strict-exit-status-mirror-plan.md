---
title: "fix: strict exit stderr from top-level status"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Strict Exit stderr from Top-Level status (plan 171)

## Summary

`_apply_lfg_agent_briefing` runs before `_emit_lfg_strict_exit_stderr`, flattening defer mirrors onto top-level **`status`**. Strict exit stderr still reads nested **`lfg_agent_briefing`**, diverging from deferred poll stderr (plans 165–167) and watch summary (plan 170).

---

## Requirements

- R1. Extract **`_lfg_briefing_mirror_stderr_parts(status)`** shared by deferred poll stderr and strict exit.
- R2. **`_emit_lfg_strict_exit_stderr`** appends tokens from top-level **`status`**, with briefing fallback for direct unit tests.
- R3. Tests; **`PLAN_TRACK_CAP`** 171; closeout bullet; plans index **019–171**.

---

## Test scenarios

- T1. Strict exit prefers top-level **`primary_action`** / **`max_queued_hours`** over nested briefing when both present.
- T2. Existing defer briefing strict-exit tests still pass via briefing fallback.
- T3. Plan patch expects **`019–171`**.
