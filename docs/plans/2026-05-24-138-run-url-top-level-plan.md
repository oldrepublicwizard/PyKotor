---
title: "fix: top-level verify and fc run url json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level verify_run_url and fc_run_url JSON (plan 138)

## Summary

Defer briefing exposes **`verify_run_url`** / **`fc_run_url`** via **`_attach_active_run_refs`**, but top-level gate JSON and **`preflight_watch_summary`** omit URLs unless agents drill into **`lfg_agent_briefing`**. Strict exit stderr also omits **`verify_run=`** / **`fc_run=`** IDs present on the briefing line.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`verify_run_url`** and **`fc_run_url`** to top-level status JSON when set.
- R2. **`preflight_watch_summary`** JSON includes both run URLs on deferred watch end.
- R3. **`_emit_lfg_strict_exit_stderr`** appends **`verify_run=`** / **`fc_run=`** when briefing carries run IDs.
- R4. Tests; **`PLAN_TRACK_CAP`** 138; closeout doc bullet; plans index **019–138**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`verify_run_url`** and **`fc_run_url`** when deferred with active runs.
- T2. Watch summary JSON includes both run URLs.
- T3. Strict exit stderr includes **`verify_run=`** and **`fc_run=`** when deferred.
- T4. Plan patch expects **`019–138`**.
