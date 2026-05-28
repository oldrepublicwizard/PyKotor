---
title: "fix: top-level gh watch command json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level gh_watch_command JSON (plan 148)

## Summary

Defer briefing stderr prints **`watch=gh run watch …`**, but top-level gate JSON only exposes the long **`wait_command`** gate-watch script unless agents drill into **`monitor_commands`**. Strict exit stderr also omits **`watch=`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors primary **`gh run watch`** command to top-level **`gh_watch_command`** when set.
- R2. **`preflight_watch_summary`** JSON includes **`gh_watch_command`** on deferred watch end.
- R3. **`_emit_lfg_strict_exit_stderr`** appends **`watch=`** when briefing carries a gh watch command.
- R4. Watch summary one-liner includes **`watch=`** when present.
- R5. Tests; **`PLAN_TRACK_CAP`** 148; closeout doc bullet; plans index **019–148**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`gh_watch_command`** when deferred with active FC run.
- T2. Watch summary JSON includes **`gh_watch_command`**.
- T3. Strict exit stderr includes **`watch=gh run watch`**.
- T4. Plan patch expects **`019–148`**.
