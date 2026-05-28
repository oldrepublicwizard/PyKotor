---
title: "feat: flat_hb poll stderr and json alias"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_hb Poll Stderr and JSON Alias (plan 193)

## Summary

Align gate-watch **poll** stderr with summary: emit **`flat_hb=1`** on heartbeat polls (replacing **`flat_keys_heartbeat=1`**) and add **`flat_hb`** JSON alias on **`preflight_watch_summary`**.

---

## Requirements

- R1. Heartbeat poll lines emit **`flat_hb=1`** instead of **`flat_keys_heartbeat=1`**.
- R2. Summary JSON sets **`flat_hb`** when **`flat_keys_heartbeat_polls > 0`**.
- R3. Heartbeat gate/formatter resolve count from **`flat_hb`** or **`flat_keys_heartbeat_polls`**.
- R4. Tests; **`PLAN_TRACK_CAP`** 193; closeout index **019–193**.

---

## Test scenarios

- T1. Heartbeat poll line includes **`flat_hb=1`**, not **`flat_keys_heartbeat=`**.
- T2. Summary JSON includes **`flat_hb`** when heartbeats occurred.
- T3. Plan patch expects **`019–193`**.
