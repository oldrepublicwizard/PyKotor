---
title: "feat: cumulative flat_hb on heartbeat poll stderr"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: Cumulative flat_hb on Heartbeat Poll Stderr (plan 199)

## Summary

Emit cumulative **`flat_hb=N`** on gate-watch heartbeat poll lines and add **`flat_hb_total`** JSON alias on **`preflight_watch_summary`**. History snapshots store cumulative **`flat_hb`** counts.

---

## Requirements

- R1. Heartbeat poll stderr uses cumulative heartbeat count (not fixed **`flat_hb=1`**).
- R2. Summary JSON includes **`flat_hb_total`** when heartbeats **> 0**.
- R3. History snapshots record cumulative **`flat_hb`** on heartbeat polls.
- R4. Tests; **`PLAN_TRACK_CAP`** 199; closeout index **019–199**.

---

## Test scenarios

- T1. Second heartbeat poll → **`flat_hb=2`** on stderr.
- T2. Summary JSON includes **`flat_hb_total`** alias.
- T3. Plan patch expects **`019–199`**.
