---
title: "fix: top-level lfg briefing blocked json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level blocked JSON (plan 140)

## Summary

Defer briefing exposes **`blocked: deferred`**, and the briefing stderr line prints **`blocked=deferred`**, but top-level gate JSON and **`preflight_watch_summary`** omit **`blocked`** unless agents drill into **`lfg_agent_briefing`**. Strict exit stderr also omits it.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`blocked`** to top-level status JSON when set.
- R2. **`preflight_watch_summary`** JSON includes **`blocked`** on deferred watch end.
- R3. **`_emit_lfg_strict_exit_stderr`** appends **`blocked=`** when briefing carries it.
- R4. Watch summary one-liner includes **`blocked=`** when present.
- R5. Tests; **`PLAN_TRACK_CAP`** 140; closeout doc bullet; plans index **019–140**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`blocked: deferred`** when deferred.
- T2. Watch summary JSON includes **`blocked`**.
- T3. Strict exit stderr includes **`blocked=deferred`**.
- T4. Plan patch expects **`019–140`**.
