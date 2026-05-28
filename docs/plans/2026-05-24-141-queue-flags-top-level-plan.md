---
title: "fix: top-level queue backlog flags json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level queue backlog flags JSON (plan 141)

## Summary

Defer **`queue_context`** nests **`queue_backlog`**, **`queue_backlog_severe`**, **`queue_backlog_warning`**, and **`max_queued_hours`**, but agents scanning top-level gate JSON must drill into the object even though stderr already prints **`queue_warn=`** / **`queue_backlog=`**.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors queue backlog flags and **`max_queued_hours`** to top-level status JSON from **`queue_context`**.
- R2. **`preflight_watch_summary`** JSON includes the same flattened queue fields on deferred watch end.
- R3. Tests; **`PLAN_TRACK_CAP`** 141; closeout doc bullet; plans index **019–141**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`queue_backlog_warning: true`** and **`max_queued_hours`** when deferred with ≥2h queue.
- T2. Watch summary JSON includes flattened queue fields.
- T3. Plan patch expects **`019–141`**.
