---
title: "feat: gate preflight flat-keys heartbeat summary stderr"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Gate Preflight Flat-Keys Heartbeat Summary Stderr (plan 188)

## Summary

Record **`watch_heartbeat_polls`** on **`preflight_watch_summary`** and emit **`flat_keys_heartbeat_polls=`** on the summary one-liner only when unchanged flat-key polls reached the heartbeat interval. Relocate **`_count_unchanged_preflight_flat_keys_polls`** with flat-field helpers.

---

## Requirements

- R1. Watch loop stores **`preflight_watch_heartbeat_polls`** from **`--watch-heartbeat-polls`**.
- R2. Summary JSON includes **`watch_heartbeat_polls`**; stderr **`flat_keys_heartbeat_polls=`** only when **`unchanged_flat_keys_polls >= watch_heartbeat_polls`** and heartbeats **> 0**.
- R3. Move **`_count_unchanged_preflight_flat_keys_polls`** next to flat-field builders.
- R4. **`PLAN_TRACK_CAP`** 188; closeout index **019–188**.

---

## Test scenarios

- T1. Summary stderr includes heartbeat count when unchanged meets interval.
- T2. Summary stderr omits heartbeat count when unchanged below interval.
- T3. Plan patch expects **`019–188`**.
