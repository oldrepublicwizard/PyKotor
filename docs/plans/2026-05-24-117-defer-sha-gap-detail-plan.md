---
title: "fix: defer briefing sha gap detail and preflight retry"
type: fix
status: active
date: 2026-05-28
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Defer SHA Gap Detail (plan 117)

## Summary

Defer `monitor_commands.preflight_retry` incorrectly copies the watch `command`. Fix to always single-shot preflight. Add structured **`sha_gap`** on defer when FC SHA lags master.

---

## Problem Frame

Live: `fc_active_pending`; `preflight_retry` duplicates preflight-watch; agents lack structured SHA fields beyond text notes.

---

## Requirements

- R1. `_build_defer_monitor_commands` always sets `preflight_retry` to `--lfg-preflight --json`.
- R2. `_build_defer_sha_gap_detail` exposes fc_head, master_sha, queued_hours.
- R3. Defer briefing attaches `sha_gap` when FC stale gap pending.
- R4. Defer stderr includes `sha_gap=` short form; tests; `PLAN_TRACK_CAP` `117`; docs.

---

## Test scenarios

- T1. Watch defer → preflight_retry is single-shot, command is watch.
- T2. fc_active_pending briefing includes sha_gap with head SHAs.
- T3. stderr includes sha_gap= prefix.
