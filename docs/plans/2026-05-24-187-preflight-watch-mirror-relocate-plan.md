---
title: "refactor: relocate preflight watch summary mirror"
type: refactor
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# refactor: Relocate `_mirror_preflight_watch_summary_from_status` (plan 187)

## Summary

Move **`_mirror_preflight_watch_summary_from_status`** from the preflight-watch section to the flat-field mirror cluster (after **`_build_lfg_flat_field_keys_present`**) alongside **`_mirror_lfg_flat_fields`** and flat-field builders.

---

## Requirements

- R1. No behavior change — pure relocation.
- R2. **`PLAN_TRACK_CAP`** 187; closeout index **019–187**.
- R3. Existing mirror/watch summary tests still pass.

---

## Test scenarios

- T1. **`test_mirror_preflight_watch_summary_from_status`** unchanged behavior.
- T2. Plan patch expects **`019–187`**.
