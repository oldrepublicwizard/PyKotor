---
title: "feat: watch heartbeat interval on preflight summary stderr"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Watch Heartbeat Interval on Preflight Summary Stderr (plan 189)

## Summary

When preflight/gate watch saw unchanged flat-key polls, emit **`watch_heartbeat_polls=N`** on the summary one-liner so agents see the heartbeat interval alongside **`unchanged_flat_keys_polls=`**.

---

## Requirements

- R1. **`_format_preflight_watch_summary_line`** appends **`watch_heartbeat_polls=N`** when **`unchanged_flat_keys_polls > 0`** and **`watch_heartbeat_polls > 0`**.
- R2. Tests; **`PLAN_TRACK_CAP`** 189; closeout index **019–189**.

---

## Test scenarios

- T1. Unchanged flat polls present → summary stderr includes **`watch_heartbeat_polls=12`**.
- T2. No unchanged flat polls → omit **`watch_heartbeat_polls=`**.
- T3. Plan patch expects **`019–189`**.
