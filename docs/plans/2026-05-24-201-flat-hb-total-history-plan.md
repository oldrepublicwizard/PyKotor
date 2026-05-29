---
title: "feat: flat_hb_total alias in preflight watch history snapshots"
type: feat
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_hb_total in Watch History Snapshots (plan 201)

## Summary

Add **`flat_hb_total`** to **`preflight_watch_history`** heartbeat snapshots alongside existing **`flat_hb`**, aligning history keys with summary JSON and stderr from plans 199–200.

---

## Requirements

- R1. Heartbeat poll snapshots record **`flat_hb_total`** (cumulative count).
- R2. Legacy **`flat_hb`** snapshot key retained for compatibility.
- R3. Tests; **`PLAN_TRACK_CAP`** 201; closeout index **019–201**.

---

## Test scenarios

- T1. Cumulative watch history entries include **`flat_hb_total=1`** then **`2`**.
- T2. Non-heartbeat snapshots omit **`flat_hb_total`**.
- T3. Plan patch expects **`019–201`**.
