---
title: "fix: defer classify fc stale gap while fc run active"
type: fix
status: active
date: 2026-05-27
origin: docs/solutions/testing/verify-pypi-regression-closeout.md
---

# fix: Defer Classify FC Stale Gap While FC Active (plan 107)

## Summary

When verify is terminal but FC is still queued/in_progress, IDs match, and `fc_sha_stale_benign` is unclassified, `_compare_checkpoint` returns **`classify_fc_stale_gap`** and blocks refresh. Agents should **defer** until FC reaches terminal status — classification requires a finished run, not prefetch-git on an in-flight FC.

---

## Problem Frame

Live state: verify **success** on `8916e2f`; FC **queued** on `bcb5586` (run `26543899770`). Doc checkpoint IDs match. Preflight blocks with `classify_fc_stale_gap` even though FC is still active.

---

## Requirements

- R1. Before `classify_fc_stale_gap`, if `fc_active`, return defer (`defer_lfg_pr: true`, `checkpoint_unchanged: true`) with reason noting FC still active.
- R2. Add `fc_stale_gap_pending_note` when deferring for active FC with SHA mismatch.
- R3. Surface pending note in `lfg_agent_briefing.notes` when present.
- R4. `classify_fc_stale_gap` only when FC is terminal and benign status is still unknown.
- R5. Tests; bump `PLAN_TRACK_CAP` to `107`; update closeout + AGENTS.

---

## Scope Boundaries

- Does not change git classification logic.
- Does not auto-dispatch FC.

---

## Test scenarios

- T1. Verify terminal + FC queued + IDs match + benign unknown → defer, not `classify_fc_stale_gap`.
- T2. Both terminal + benign unknown → still `classify_fc_stale_gap`.
- T3. `fc_stale_gap_pending_note` includes FC status word.
- T4. Preflight JSON sets `lfg_deferred: true` for T1 case.
