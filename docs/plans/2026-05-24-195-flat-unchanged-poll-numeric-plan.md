---
title: "feat: flat_unchanged=1 on gate-watch poll stderr"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_unchanged=1 on Gate-Watch Poll Stderr (plan 195)

## Summary

Replace boolean **`flat_unchanged=true`** on compact gate-watch poll lines with numeric **`flat_unchanged=1`** to align with summary **`flat_unchanged=N`** tokens.

---

## Requirements

- R1. **`_format_preflight_watch_poll_line`** emits **`flat_unchanged=1`** when flat keys unchanged (non-heartbeat poll).
- R2. Tests; **`PLAN_TRACK_CAP`** 195; closeout index **019–195**.

---

## Test scenarios

- T1. Unchanged poll → **`flat_unchanged=1`**, not **`flat_unchanged=true`**.
- T2. Changed keys → no **`flat_unchanged=`** token.
- T3. Plan patch expects **`019–195`**.
