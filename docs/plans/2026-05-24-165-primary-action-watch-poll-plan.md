---
title: "fix: top-level primary_action on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level primary_action / expected_after on Defer Watch Poll stderr (plan 165)

## Summary

Plan 132 flattened **`primary_action`** and **`expected_after_terminal`** to top-level gate JSON. Deferred watch poll stderr still reads both from the nested **`lfg_agent_briefing`** dict instead of the top-level mirrors after **`_apply_lfg_agent_briefing`**.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** emits **`primary_action=`** from top-level **`primary_action`** after briefing apply when deferred.
- R2. Emit **`expected_after=`** from top-level **`expected_after_terminal.action`** after briefing apply when deferred.
- R3. Tests; **`PLAN_TRACK_CAP`** 165; closeout doc bullet; plans index **019–165**.

---

## Test scenarios

- T1. Deferred preflight watch poll stderr includes **`primary_action=gate_watch`** and **`expected_after=closeout`** from top-level mirrors.
- T2. Gate watch poll stderr includes the same tokens.
- T3. Plan patch expects **`019–165`**.
