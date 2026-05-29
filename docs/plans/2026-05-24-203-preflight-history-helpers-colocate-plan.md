---
title: "refactor: co-locate preflight watch history helpers"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Co-locate Preflight Watch History Helpers (plan 203)

## Summary

Move **`_count_unchanged_preflight_flat_keys_polls`**, **`_max_preflight_flat_unchanged_streak`**, and **`_max_preflight_flat_hb_total`** adjacent to **`_build_preflight_watch_summary`**, matching plans 186–187 helper clustering.

---

## Requirements

- R1. History helpers sit immediately above **`_build_preflight_watch_summary`**.
- R2. No behavior change.
- R3. Tests; **`PLAN_TRACK_CAP`** 203; closeout index **019–203**.

---

## Test scenarios

- T1. Existing history/count/max tests still pass.
- T2. Plan patch expects **`019–203`**.
