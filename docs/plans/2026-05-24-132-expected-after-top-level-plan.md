---
title: "fix: top-level expected_after and watch summary primary_action"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level expected_after and Watch Summary primary_action (plan 132)

## Summary

Strict exit stderr carries **`expected_after=closeout`** and **`primary_action=gate_watch`**, but top-level gate JSON and **`preflight_watch_summary`** omit them unless agents drill into **`lfg_agent_briefing`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`expected_after_terminal`** and **`primary_action`** to top-level status JSON.
- R2. **`preflight_watch_summary`** JSON includes both when defer briefing applies on watch end.
- R3. **`_format_preflight_watch_summary_line`** appends **`expected_after=`** and **`primary_action=`**.
- R4. Tests; **`PLAN_TRACK_CAP`** 132; closeout doc bullet; plans index **019–132**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`expected_after_terminal.action=closeout`** and **`primary_action=gate_watch`** when deferred.
- T2. Watch summary JSON/one-liner include **`expected_after=closeout`** and **`primary_action=gate_watch`**.
- T3. Plan patch expects **`019–132`**.
