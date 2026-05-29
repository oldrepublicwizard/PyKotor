---
title: "feat: flat_unchanged streak on gate-watch poll stderr"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_unchanged Streak on Gate-Watch Poll Stderr (plan 198)

## Summary

Emit **`flat_unchanged=N`** on compact gate-watch poll lines using the live unchanged streak count (replacing fixed **`flat_unchanged=1`**) to match history snapshots and summary tokens.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** uses **`flat_keys_unchanged_streak`** for **`flat_unchanged=N`**.
- R2. Tests; **`PLAN_TRACK_CAP`** 198; closeout index **019–198**.

---

## Test scenarios

- T1. Streak 1 → **`flat_unchanged=1`**; streak 3 → **`flat_unchanged=3`**.
- T2. Heartbeat poll still uses **`flat_hb=1`**, not **`flat_unchanged=`**.
- T3. Plan patch expects **`019–198`**.
