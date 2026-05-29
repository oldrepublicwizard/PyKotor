---
title: "feat: flat_unchanged streak in preflight watch history"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_unchanged Streak in Preflight Watch History (plan 196)

## Summary

Record **`flat_unchanged`** streak count on each **`preflight_watch_history`** snapshot when flat keys match the prior poll; record **`flat_hb=1`** on heartbeat polls.

---

## Requirements

- R1. Snapshots include **`flat_unchanged`** streak when **> 0**.
- R2. Snapshots include **`flat_hb: 1`** when a flat-keys heartbeat fires.
- R3. Tests; **`PLAN_TRACK_CAP`** 196; closeout index **019–196**.

---

## Test scenarios

- T1. Three unchanged deferred polls → history entries **`flat_unchanged`** 1 then 2.
- T2. Plan patch expects **`019–196`**.
