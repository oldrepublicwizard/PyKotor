---
title: "feat: lfg preflight watch polls until defer clears"
type: feat
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# feat: LFG Preflight Watch (plan 114)

## Summary

Agents waiting on queued FC must manually re-run `--lfg-preflight` or external `gh run watch`. Add **`--lfg-preflight-watch`** to poll CI checkpoint until `defer_lfg_pr` clears or timeout (default 7200s).

---

## Problem Frame

Live: `fc_active_pending` with `monitor_commands.watch_fc_run`; no in-script poll loop for preflight defer.

---

## Requirements

- R1. `--lfg-preflight-watch` enables preflight + poll until not deferred or timeout.
- R2. `_watch_lfg_preflight_defer` re-fetches gh each poll; stderr poll lines with FC/verify status.
- R3. `preflight_watch_summary` + `lfg_preflight_watch_result` on status JSON.
- R4. Defer `monitor_commands.preflight_watch`; `lfg_mode` `preflight_watch`; default timeout 7200s.
- R5. Tests; `PLAN_TRACK_CAP` `114`; closeout + plan 020 docs.

---

## Test scenarios

- T1. Mock defer then proceed → `lfg_preflight_watch_result` `proceed`.
- T2. Mock always defer + short timeout → `timeout`.
- T3. Defer briefing includes `preflight_watch` command.
