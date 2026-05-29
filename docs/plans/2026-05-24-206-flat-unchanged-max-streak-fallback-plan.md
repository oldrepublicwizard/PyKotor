---
title: "feat: flat_unchanged max-streak fallback in watch summary"
type: feat
status: active
date: 2026-05-29
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: flat_unchanged Max-Streak Fallback in Watch Summary (plan 206)

## Summary

When **`unchanged_flat_keys_polls`** is zero, derive **`flat_unchanged`** in **`preflight_watch_summary`** from **`_max_preflight_flat_unchanged_streak`**, mirroring plan 202’s history fallback for **`flat_hb_total`**.

---

## Requirements

- R1. Summary uses max streak fallback before setting **`flat_unchanged`** alias.
- R2. **`unchanged_flat_keys_polls`** in summary reflects fallback value.
- R3. Tests; **`PLAN_TRACK_CAP`** 206; closeout index **019–206**.

---

## Test scenarios

- T1. History with streak snapshots only → **`flat_unchanged=2`**.
- T2. Pairwise count present still wins over fallback.
- T3. Plan patch expects **`019–206`**.
