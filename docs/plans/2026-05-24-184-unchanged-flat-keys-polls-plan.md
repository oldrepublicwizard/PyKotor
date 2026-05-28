---
title: "feat: unchanged_flat_keys_polls in watch summary"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: unchanged_flat_keys_polls in Watch Summary (plan 184)

## Summary

Plan 183 omitted unchanged **`flat_keys=`** on consecutive gate-watch polls. Add **`flat_keys`** to preflight watch history snapshots and **`unchanged_flat_keys_polls`** on **`preflight_watch_summary`** JSON + summary stderr.

---

## Requirements

- R1. Deferred poll snapshots record **`flat_keys`** list after apply.
- R2. **`_count_unchanged_preflight_flat_keys_polls(history)`** counts consecutive equal **`flat_keys`** pairs.
- R3. **`preflight_watch_summary`** and summary stderr include **`unchanged_flat_keys_polls`** when **> 0**.
- R4. Tests; **`PLAN_TRACK_CAP`** 184; closeout bullet; plans index **019–184**.

---

## Test scenarios

- T1. History with two polls same **`flat_keys`** → count **1**.
- T2. Summary line includes **`unchanged_flat_keys_polls=1`** when applicable.
- T3. Plan patch expects **`019–184`**.
