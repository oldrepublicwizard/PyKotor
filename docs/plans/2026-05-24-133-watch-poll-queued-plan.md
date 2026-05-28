---
title: "fix: watch poll queued and expected_after stderr"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Watch Poll queued and expected_after Stderr (plan 133)

## Summary

Watch poll stderr lists per-run **`fc_queued=`** / **`verify_queued=`** and **`gh_watch=`**, but lacks aggregate **`queued=`**, queue flags, **`expected_after=`**, and **`primary_action=`** present on **`LFG exit:`** and watch summary lines.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** appends aggregate **`queued=`** and queue flags from **`_build_defer_queue_context`**.
- R2. Poll line appends **`expected_after=`** and **`primary_action=`** from defer briefing when **`lfg_deferred`**.
- R3. Tests; **`PLAN_TRACK_CAP`** 133; closeout doc bullet; plans index **019–133**.

---

## Test scenarios

- T1. Poll line includes **`queued=1.5h`** and **`queue_warn=true`** when warning threshold met.
- T2. Poll line includes **`expected_after=closeout`** and **`primary_action=gate_watch`** when deferred.
- T3. Plan patch expects **`019–133`**.
