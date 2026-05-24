---
title: "feat: checkpoint compare for ci-status-only defer"
type: feat
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# feat: Checkpoint Compare for ci-status-only Defer

## Summary

`--ci-status-only --json` matches plan 058 checkpoint (verify 26365458400, FC 26365648344, both queued). Per plans 056–057, defer LFG PR. Add `--compare-checkpoint` to emit `checkpoint_unchanged` and `defer_lfg_pr` by parsing run IDs from solution doc **Last CI check**.

## Problem Frame

Agents repeatedly invoke `/lfg` on an unchanged monitoring track. Manual comparison against solution doc is error-prone; automate defer signal in script JSON.

## Requirements

- R1. `--compare-checkpoint` with `--ci-status-only --json` parses run IDs from solution doc Last CI check.
- R2. JSON adds `checkpoint_unchanged`, `defer_lfg_pr` when run IDs and verify status unchanged (still queued).
- R3. `defer_lfg_pr` false when conclusion changes or run IDs differ.
- R4. Document in AGENTS.md; mark plan 059 completed.
- R5. No CI cancel/dispatch; no plan 020 PR when defer true.

## Implementation Units

- U1. **Script** — checkpoint parse + compare.
- U2. **AGENTS.md** — `--compare-checkpoint` usage.

## Verification

| Check | Expected |
|-------|----------|
| `--ci-status-only --json --compare-checkpoint` | defer_lfg_pr true today |
| No dispatch | unchanged |

## Scope Boundaries

- Does not update plan 020 when defer_lfg_pr true.

## Sources & References

- Solution doc Last CI check (plan 058)
- Plans 056–057 defer rules
