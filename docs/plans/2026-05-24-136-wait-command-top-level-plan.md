---
title: "fix: top-level wait_command and monitor_commands json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level wait_command and monitor_commands JSON (plan 136)

## Summary

Defer briefing carries **`command`** (gate-watch wait) and structured **`monitor_commands`**, but gate JSON requires drilling into **`lfg_agent_briefing`**. Live queue age now triggers **`queue_warn=true`** at ≥2h — agents need the wait command at top level.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`wait_command`** from briefing **`command`** and **`monitor_commands`** when present.
- R2. **`preflight_watch_summary`** JSON includes **`wait_command`** and **`monitor_commands`** on deferred watch end.
- R3. Tests; **`PLAN_TRACK_CAP`** 136; closeout doc bullet; plans index **019–136**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`wait_command`** and **`monitor_commands.gate_watch`** when deferred.
- T2. Watch summary JSON includes **`wait_command`** and **`monitor_commands`**.
- T3. Plan patch expects **`019–136`**.
