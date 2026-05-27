---
title: "feat: lfg-preflight shorthand and proceed hints"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: lfg-preflight Shorthand + Proceed Hints (plan 078)

## Gaps

- G1. Agents must combine `--monitor-preflight --lfg-refresh --dry-run` manually for a full briefing.
- G2. `--lfg-refresh --dry-run` exits 2 when deferred before emitting full preflight JSON.
- G3. No `proceed_hint` recommending the next CLI command based on checkpoint state.

## Requirements

- R1. `--lfg-preflight` expands to monitor-preflight + lfg-refresh + dry-run.
- R2. Dry-run lfg-refresh when blocked embeds `lfg_refresh_blocked` and continues (no early exit 2).
- R3. `_build_proceed_hint` returns next recommended command; embedded in JSON for monitor/lfg paths.
- R4. Unit tests; bump `PLAN_TRACK_CAP` to `078`.

## Test scenarios

- T1. lfg-preflight sets monitor + refresh + dry-run flags.
- T2. proceed_hint for deferred vs terminal proceed paths.
- T3. dry-run blocked refresh does not hard-exit (logic unit test).
