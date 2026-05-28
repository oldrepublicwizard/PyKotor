---
title: "fix: active_runs on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level active_runs on Defer Watch Poll stderr (plan 160)

## Summary

Plan 130 flattened **`active_runs`** to top-level gate JSON and strict exit already emits **`active_runs=`**. Deferred watch poll stderr still derives **`active_runs=`** from **`_build_active_runs_list`** before briefing apply instead of the top-level mirror.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** emits **`active_runs=`** from top-level **`active_runs`** after **`_apply_lfg_agent_briefing`** when deferred.
- R2. Skip pre-briefing **`_build_active_runs_list`** token when **`lfg_deferred`** to avoid duplicates.
- R3. Tests; **`PLAN_TRACK_CAP`** 160; closeout doc bullet; plans index **019–160**.

---

## Test scenarios

- T1. Preflight watch poll stderr includes **`active_runs=verify,fc`** exactly once when deferred.
- T2. Gate watch poll stderr includes the same token exactly once.
- T3. Plan patch expects **`019–160`**.
