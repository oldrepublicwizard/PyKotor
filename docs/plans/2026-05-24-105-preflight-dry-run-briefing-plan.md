---
title: "fix: preflight refresh dry-run json and blocked briefing"
type: fix
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Preflight Refresh Dry-Run JSON + Blocked Briefing (plan 105)

## Summary

`--lfg-preflight` / `--lfg-gate` / `--lfg-merge-gate` use dry-run refresh but omit **`lfg_refresh_dry_run`** when refresh is blocked (e.g. `classify_fc_stale_gap`). Agents lose the dry-run signal; CLI tests fail. Extend **`lfg_agent_briefing`** for blocked/deferred pre-merge states.

---

## Problem Frame

When `lfg_refresh` is blocked during dry-run preflight, JSON sets `lfg_refresh_blocked` but not `lfg_refresh_dry_run`. Track may be incomplete (FC drift) so merge briefing is empty despite actionable `proceed_hint`.

---

## Requirements

- R1. Set `lfg_refresh_dry_run: true` whenever preflight refresh runs with `--dry-run`, including when blocked.
- R2. `lfg_agent_briefing` when `lfg_refresh_blocked` or `lfg_deferred` with action/reason/command from `proceed_hint`.
- R3. Stderr `LFG briefing:` for blocked refresh on preflight (non-zero optional; include when briefing present).
- R4. Fix CLI tests; bump `PLAN_TRACK_CAP` to `105`; update closeout + AGENTS.

---

## Scope Boundaries

- Does not auto-dispatch FC or change classify_fc_stale_gap logic.
- Does not merge PR #308.

---

## Test scenarios

- T1. Blocked dry-run refresh sets both `lfg_refresh_blocked` and `lfg_refresh_dry_run`.
- T2. Briefing for `classify_fc_stale_gap` includes `--prefetch-git --lfg-gate` command.
- T3. CLI preflight test passes with blocked or dry-run plan present.
