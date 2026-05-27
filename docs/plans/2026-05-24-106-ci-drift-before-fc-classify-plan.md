---
title: "fix: prioritize run id drift over fc stale classify gap"
type: fix
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Run ID Drift Before FC Classify Gap (plan 106)

## Summary

When live FC run ID differs from the doc checkpoint but `fc_sha_stale_benign` is unclassified, `_compare_checkpoint` returns **`classify_fc_stale_gap`** and blocks refresh. Agents should get **`investigate_ci_drift`** first (new FC run queued is the actionable signal).

---

## Problem Frame

Checkpoint compare checks unclassified FC SHA before run ID drift. Live state: FC run `26543899770` vs doc `26365648344` masked as classify gap.

---

## Requirements

- R1. Reorder `_compare_checkpoint`: after `verify_sha_stale`, handle `not ids_match` before `fc_sha_stale_benign is None`.
- R2. Add `ci_drift_note` with live vs checkpoint run IDs when investigating drift.
- R3. Surface note in `lfg_agent_briefing.notes` when present.
- R4. Tests; bump `PLAN_TRACK_CAP` to `106`; update closeout + AGENTS.

---

## Scope Boundaries

- Does not auto-update monitoring docs.
- Does not change git classification logic.

---

## Test scenarios

- T1. ID drift + fc benign unknown → `investigate_ci_drift`, not `classify_fc_stale_gap`.
- T2. IDs match + fc benign unknown → still `classify_fc_stale_gap`.
- T3. `ci_drift_note` includes both run IDs.
