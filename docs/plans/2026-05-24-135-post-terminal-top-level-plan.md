---
title: "fix: top-level post_terminal_commands and poll watch_recommended"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level post_terminal_commands and Poll watch_recommended (plan 135)

## Summary

Defer briefing includes **`post_terminal_commands`** (preflight/gate/closeout) for after verify+FC terminal, but gate JSON and watch summary omit it unless agents drill into **`lfg_agent_briefing`**. Watch poll stderr also lacks **`watch_recommended=true`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`post_terminal_commands`** to top-level status JSON when present.
- R2. **`preflight_watch_summary`** JSON includes **`post_terminal_commands`** on deferred watch end.
- R3. Watch poll stderr appends **`watch_recommended=true`** when defer briefing recommends watch.
- R4. Tests; **`PLAN_TRACK_CAP`** 135; closeout doc bullet; plans index **019–135**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`post_terminal_commands.closeout`** when deferred.
- T2. Watch summary JSON includes **`post_terminal_commands`**.
- T3. Poll line includes **`watch_recommended=true`** when deferred with watch recommended.
- T4. Plan patch expects **`019–135`**.
