---
title: "fix: briefing_reason on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: briefing_reason on Defer Watch Poll stderr (plan 152)

## Summary

Plan 144 flattened **`briefing_reason`** to top-level gate JSON and added **`briefing_reason=`** on strict exit and watch summary one-liners. Deferred watch poll stderr still omits **`briefing_reason=`**, so agents polling **`--lfg-gate-watch`** only see the raw **`lfg_defer_reason`** prefix and miss the normalized briefing reason on each poll.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** appends **`briefing_reason=`** when top-level **`briefing_reason`** is set after **`_apply_lfg_agent_briefing`**.
- R2. Tests for preflight and gate poll lines with deferred **`briefing_reason=unchanged_active_runs`**.
- R3. **`PLAN_TRACK_CAP`** 152; closeout doc bullet; plans index **019–152**.

---

## Test scenarios

- T1. Preflight watch poll stderr includes **`briefing_reason=unchanged_active_runs`** when deferred.
- T2. Gate watch poll stderr includes **`briefing_reason=unchanged_active_runs`** on the same fixture.
- T3. Plan patch expects **`019–152`**.
