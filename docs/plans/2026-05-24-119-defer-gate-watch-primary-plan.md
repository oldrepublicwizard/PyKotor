---
title: "fix: defer and drift wait prefer gate-watch command"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Prefer Gate-Watch as Primary Wait Command (plan 119)

## Summary

Defer and drift-wait briefings still primary-route to `--lfg-preflight-watch`. Prefer **`--lfg-gate-watch`** so agents poll once and get strict gate exit semantics.

---

## Problem Frame

Live: `fc_active_pending`; `gate_watch` exists in monitor_commands but `command`/`proceed_hint` use preflight-watch.

---

## Requirements

- R1. Defer `command` and `_build_proceed_hint` use `gate_watch` when watch recommended.
- R2. Drift wait uses `refresh_commands.gate_watch` as primary command.
- R3. Preflight watch poll stderr includes `sha_gap=` when present.
- R4. Tests; `PLAN_TRACK_CAP` `119`; closeout + plan 020 docs.

---

## Test scenarios

- T1. fc_active_pending defer → command is gate-watch.
- T2. investigate_ci_drift + active FC → command is gate-watch.
- T3. Watch poll line includes sha_gap when checkpoint stale.
