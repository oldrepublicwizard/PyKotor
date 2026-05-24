---
title: "feat: monitor-preflight shorthand flag"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: monitor-preflight Shorthand (plan 063)

## Summary

`lfg_deferred: true`; PR #308 open. Add `--monitor-preflight` as shorthand for `--ci-status-only --json --compare-checkpoint --exit-on-defer` to simplify repeated agent/LFG preflight.

## Requirements

- R1. `--monitor-preflight` enables all four underlying flags.
- R2. Conflicts with partial manual flags resolved by preflight taking precedence (document in help).
- R3. Unit test via subprocess; update AGENTS.md and solution doc **Agent defer check**.
- R4. Append to PR #308; no Last CI check update.

## Implementation Units

- U1. `.github/scripts/local_verify_pypi_slice.py`
- U2. `Libraries/PyKotor/tests/test_utility/test_local_verify_checkpoint.py`
- U3. `AGENTS.md`, solution doc

## Verification

| Check | Expected |
|-------|----------|
| `--monitor-preflight` JSON | `lfg_deferred: true` today |
| unittest | pass |

## Scope Boundaries

- No plan 020 CI conclusion update.
