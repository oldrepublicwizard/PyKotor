---
title: "feat: max_flat_unchanged on preflight watch summary"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: max_flat_unchanged on Preflight Watch Summary (plan 197)

## Summary

Compute peak consecutive **`flat_unchanged`** streak from watch history and expose **`max_flat_unchanged`** on **`preflight_watch_summary`**. Emit summary stderr **`max_flat_unchanged=N`** when peak streak is below total unchanged polls (mid-watch key churn).

---

## Requirements

- R1. **`_max_preflight_flat_unchanged_streak`** scans history snapshot **`flat_unchanged`** values.
- R2. Summary JSON includes **`max_flat_unchanged`** when **> 0**.
- R3. Summary stderr emits **`max_flat_unchanged=N`** when **`N < flat_unchanged`** total.
- R4. Tests; **`PLAN_TRACK_CAP`** 197; closeout index **019–197**.

---

## Test scenarios

- T1. Continuous streak history → **`max_flat_unchanged=2`**, no extra stderr token.
- T2. Broken streak → **`max_flat_unchanged=1`**, total **2**, stderr includes **`max_flat_unchanged=1`**.
- T3. Plan patch expects **`019–197`**.
