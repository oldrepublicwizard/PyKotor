---
title: "fix: blocked on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: blocked on Defer Watch Poll stderr (plan 151)

## Summary

Plan 140 flattened **`blocked`** to top-level gate JSON and added **`blocked=`** on strict exit and watch summary one-liners. Deferred watch poll stderr still omits **`blocked=`**, so agents polling **`--lfg-gate-watch`** cannot see defer vs other blocked states on each poll.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** appends **`blocked=`** when top-level **`blocked`** is set after **`_apply_lfg_agent_briefing`**.
- R2. Tests for preflight and gate poll lines with deferred **`blocked=deferred`**.
- R3. **`PLAN_TRACK_CAP`** 151; closeout doc bullet; plans index **019–151**.

---

## Test scenarios

- T1. Preflight watch poll stderr includes **`blocked=deferred`** when deferred.
- T2. Gate watch poll stderr includes **`blocked=deferred`** on the same fixture.
- T3. Plan patch expects **`019–151`**.
