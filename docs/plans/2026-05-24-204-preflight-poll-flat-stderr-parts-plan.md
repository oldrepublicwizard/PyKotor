---
title: "refactor: extract preflight watch poll flat stderr parts"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Extract Preflight Watch Poll Flat Stderr Parts (plan 204)

## Summary

Extract **`_preflight_watch_poll_flat_stderr_parts`** from **`_format_preflight_watch_poll_line`**, co-locating unchanged/heartbeat flat-key stderr tokens with plan 190’s shared mirror helper pattern.

---

## Requirements

- R1. Poll line defers flat unchanged/heartbeat tokens to **`_preflight_watch_poll_flat_stderr_parts`**.
- R2. No stderr behavior change.
- R3. Tests; **`PLAN_TRACK_CAP`** 204; closeout index **019–204**.

---

## Test scenarios

- T1. Direct helper test for unchanged vs heartbeat branches.
- T2. Existing poll-line tests still pass.
- T3. Plan patch expects **`019–204`**.
