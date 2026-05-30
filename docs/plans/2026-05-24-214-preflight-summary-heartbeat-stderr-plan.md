---
title: "refactor: extract preflight summary heartbeat flat stderr parts"
type: refactor
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Extract Preflight Summary Heartbeat Flat Stderr Parts (plan 214)

## Summary

Extract **`_preflight_watch_summary_heartbeat_flat_stderr_parts`** from **`_preflight_watch_summary_flat_stderr_parts`**, composing plan 211 gate helper for the heartbeat-block **`flat_hb_total`** token.

---

## Requirements

- R1. Heartbeat block helper emits gated **`flat_hb_total`** via **`_preflight_flat_hb_total_for_stderr`**.
- R2. Summary flat stderr composes unchanged block (plan 213) then heartbeat block.
- R3. No behavior change; tests; **`PLAN_TRACK_CAP`** 214; index **019–214**.

---

## Test scenarios

- T1. Direct heartbeat-block helper test when gate passes.
- T2. Existing summary flat stderr tests pass.
- T3. Plan patch expects **`019–214`**.
