---
title: "fix: mirrored run status on defer watch poll stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Top-Level verify_status / fc_status on Defer Watch Poll stderr (plan 157)

## Summary

Plan 139 flattened **`verify_status`** / **`fc_status`** to top-level gate JSON and added them on strict exit and watch summary one-liners. Deferred watch poll stderr still derives **`verify_status=`** / **`fc_status=`** only from raw run dicts before briefing apply, so poll tokens can drift from top-level mirror when briefing adjusts labels.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** emits **`verify_status=`** / **`fc_status=`** from top-level mirrored fields after **`_apply_lfg_agent_briefing`** when deferred.
- R2. Skip run-dict status tokens when **`lfg_deferred`** so poll stderr does not duplicate them.
- R3. Tests; **`PLAN_TRACK_CAP`** 157; closeout doc bullet; plans index **019–157**.

---

## Test scenarios

- T1. Preflight watch poll stderr includes **`verify_status=queued`** and **`fc_status=queued`** once each when deferred.
- T2. Gate watch poll stderr includes the same tokens once each.
- T3. Plan patch expects **`019–157`**.
