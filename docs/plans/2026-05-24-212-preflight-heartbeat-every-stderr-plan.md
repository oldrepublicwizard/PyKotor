---
title: "refactor: preflight heartbeat_every stderr gate helper"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Preflight heartbeat_every Stderr Gate Helper (plan 212)

## Summary

Add **`_preflight_heartbeat_every_for_stderr`** to emit **`heartbeat_every=`** on summary stderr only when unchanged flat-key polls occurred, reusing **`_preflight_watch_heartbeat_interval`**.

---

## Requirements

- R1. Helper returns interval only when **`_preflight_unchanged_flat_keys_polls` > 0**.
- R2. Summary flat stderr uses helper instead of inline unchanged guard + interval lookup.
- R3. No behavior change; tests; **`PLAN_TRACK_CAP`** 212; index **019–212**.

---

## Test scenarios

- T1. Helper returns **12** when unchanged polls occurred and interval set.
- T2. Helper returns **0** when no unchanged polls.
- T3. Plan patch expects **`019–212`**.
