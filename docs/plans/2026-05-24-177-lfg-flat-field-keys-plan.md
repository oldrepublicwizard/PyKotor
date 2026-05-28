---
title: "feat: lfg_flat_field_keys in gate JSON"
type: feat
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: lfg_flat_field_keys in Gate JSON (plan 177)

## Summary

Plans 174–176 flattened briefing onto top-level **`status`** and shared **`_mirror_lfg_flat_fields`**. Agents polling **`--lfg-gate --json`** still had to guess which keys to read. Export **`LFG_FLAT_FIELD_KEYS`** as **`lfg_flat_field_keys`** on status (and watch summary) after apply.

---

## Requirements

- R1. Module-level **`LFG_FLAT_FIELD_KEYS`** tuple documents all flattened top-level keys.
- R2. **`_apply_lfg_agent_briefing`** sets **`lfg_flat_field_keys`** when briefing exists; pops when cleared.
- R3. **`preflight_watch_summary`** copies **`lfg_flat_field_keys`** from status after mirror.
- R4. Tests; **`PLAN_TRACK_CAP`** 177; closeout bullet; plans index **019–177**.

---

## Test scenarios

- T1. Apply briefing → status includes **`lfg_flat_field_keys`** matching **`LFG_FLAT_FIELD_KEYS`**.
- T2. Watch summary mirror copies **`lfg_flat_field_keys`** from status.
- T3. Plan patch expects **`019–177`**.
