---
title: "fix: print ci status bug and checkpoint snippet"
type: fix
status: completed
date: 2026-05-24
origin: lfg-pypi-regression-closeout
strategy_track: test-signal-quality
---

# fix: Print Bug and Checkpoint Snippet (plan 067)

## Gaps

- G1. `_print_ci_status` uses undefined `checkpoint` (NameError on non-JSON path).
- G2. Manual Last CI check edits are error-prone; add `--emit-checkpoint-snippet`.
- G3. Parser has no fallback when Last CI check missing; use CI canonical runs table.

## Requirements

- R1. Fix `_print_ci_status` to use `status.get("checkpoint")`.
- R2. `--emit-checkpoint-snippet` with `--ci-status-only` prints markdown for Last CI check.
- R3. `_parse_solution_checkpoint_run_ids` falls back to canonical runs table.
- R4. Unit tests; append to PR #308.
