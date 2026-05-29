---
title: "refactor: preflight flat_hb_total stderr gate helper"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Preflight flat_hb_total Stderr Gate Helper (plan 211)

## Summary

Add **`_preflight_flat_hb_total_for_stderr`** to centralize gated **`flat_hb_total=`** emission in **`_preflight_watch_summary_flat_stderr_parts`**, pairing with plan 210’s max-unchanged gate helper.

---

## Requirements

- R1. Helper returns heartbeat count only when summary heartbeat gate passes.
- R2. Summary flat stderr uses helper instead of inline gate + count.
- R3. No behavior change; tests; **`PLAN_TRACK_CAP`** 211; index **019–211**.

---

## Test scenarios

- T1. Helper returns count when unchanged ≥ interval and heartbeats > 0.
- T2. Helper returns **0** when unchanged below interval.
- T3. Plan patch expects **`019–211`**.
