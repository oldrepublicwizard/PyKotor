---
title: "fix: top-level verify and fc status json"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level verify_status and fc_status JSON (plan 139)

## Summary

Defer briefing exposes **`verify_status`** / **`fc_status`** via **`_attach_active_run_refs`**, and watch poll stderr already prints **`verify_status=`** / **`fc_status=`**, but top-level gate JSON and **`preflight_watch_summary`** omit status words unless agents drill into **`lfg_agent_briefing`**. Strict exit stderr also omits them.

---

## Requirements

- R1. **`_apply_lfg_agent_briefing`** mirrors **`verify_status`** and **`fc_status`** to top-level status JSON when set.
- R2. **`preflight_watch_summary`** JSON includes both status words on deferred watch end.
- R3. **`_emit_lfg_strict_exit_stderr`** appends **`verify_status=`** / **`fc_status=`** when briefing carries them.
- R4. Watch summary one-liner includes **`verify_status=`** / **`fc_status=`** when present.
- R5. Tests; **`PLAN_TRACK_CAP`** 139; closeout doc bullet; plans index **019–139**.

---

## Test scenarios

- T1. Gate JSON top-level includes **`verify_status`** and **`fc_status`** when deferred with active runs.
- T2. Watch summary JSON includes both status words.
- T3. Strict exit stderr includes **`verify_status=`** and **`fc_status=`**.
- T4. Plan patch expects **`019–139`**.
