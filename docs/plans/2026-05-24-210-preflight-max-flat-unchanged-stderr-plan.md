---
title: "refactor: preflight max_flat_unchanged stderr gate helper"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Preflight max_flat_unchanged Stderr Gate Helper (plan 210)

## Summary

Add **`_preflight_max_flat_unchanged_for_stderr`** to centralize gated **`max_flat_unchanged=`** emission in **`_preflight_watch_summary_flat_stderr_parts`**.

---

## Requirements

- R1. Helper returns peak streak only when **`0 < max < unchanged`**.
- R2. Summary flat stderr uses helper instead of inline gate.
- R3. No behavior change; tests; **`PLAN_TRACK_CAP`** 210; index **019–210**.

---

## Test scenarios

- T1. Helper returns **1** when peak **<** total unchanged.
- T2. Helper returns **0** when peak equals total unchanged.
- T3. Plan patch expects **`019–210`**.
