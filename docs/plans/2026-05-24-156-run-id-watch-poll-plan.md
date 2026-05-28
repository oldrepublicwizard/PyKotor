---
title: "fix: verify_run fc_run on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: verify_run / fc_run on Defer Watch Poll stderr (plan 156)

## Summary

Plan 137 flattened **`verify_run_id`** / **`fc_run_id`** to top-level gate JSON and plan 138 added strict-exit **`verify_run=`** / **`fc_run=`** tokens. Deferred watch poll stderr uses legacy **`verify=`** / **`fc=`** run keys only, so agents parsing strict-exit-style run IDs miss them unless they know both naming schemes.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** appends **`verify_run=`** / **`fc_run=`** from top-level mirrored IDs after **`_apply_lfg_agent_briefing`** when set.
- R2. Tests for preflight and gate poll lines with both run IDs present.
- R3. **`PLAN_TRACK_CAP`** 156; closeout doc bullet; plans index **019–156**.

---

## Test scenarios

- T1. Preflight watch poll stderr includes **`verify_run=1`** and **`fc_run=2`** when deferred with active runs.
- T2. Gate watch poll stderr includes the same tokens.
- T3. Plan patch expects **`019–156`**.
