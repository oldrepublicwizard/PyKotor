---
title: "fix: bleeding-edge .gitmodules merge conflict markers"
type: fix
status: completed
date: 2026-05-24
origin: lfg-master-post-pypi-merge
strategy_track: test-signal-quality
---

# fix: Bleeding-Edge `.gitmodules` Merge Conflict Markers

## Summary

Resolve leftover Git merge conflict markers in `bleeding-edge` `.gitmodules` so `Forward Commits to Bleeding-Edge` can checkout the branch and cherry-pick master commits after PR #268.

---

## Problem Frame

Master merge commit `01edca184` triggered `Forward Commits to Bleeding-Edge` run `26361732290`, which failed at `git checkout bleeding-edge` with `fatal: bad config line 56 in file .gitmodules`. Remote `bleeding-edge` still contains `<<<<<<< HEAD`, `=======`, and `>>>>>>> b18669b96 (test)` markers.

---

## Requirements

- R1. Remove all conflict markers from `bleeding-edge` `.gitmodules`.
- R2. Preserve the bleeding-edge submodule inventory (HEAD side of the conflict).
- R3. Validate `.gitmodules` parses with `git config -f .gitmodules --list`.
- R4. Push fixed `bleeding-edge` so forward-commits workflow succeeds on next master push.

---

## Scope Boundaries

- Do not rewrite master `.gitmodules` (already clean).
- Do not change forward-commits workflow logic in this slice unless validation still fails after the branch fix.

---

## Implementation Units

- U1. **Resolve bleeding-edge `.gitmodules` conflict**

**Goal:** Restore a valid `.gitmodules` on `bleeding-edge`.

**Requirements:** R1, R2, R3

**Dependencies:** None

**Files:**
- Modify: `.gitmodules` (on `bleeding-edge` branch only)

**Approach:**
- Checkout `bleeding-edge`, remove conflict marker lines, keep HEAD submodule entries.
- Run `git config -f .gitmodules --list` to confirm parse success.

**Test scenarios:**
- Happy path: `git config -f .gitmodules --list` exits 0 with no parse errors.
- Edge case: No `<<<<<<<`, `=======`, or `>>>>>>>` substrings remain in `.gitmodules`.

**Verification:**
- `git checkout bleeding-edge` succeeds locally.
- Push updates remote `bleeding-edge`.

- U2. **Confirm forward-commits path**

**Goal:** Document that the next master push should re-run forward-commits successfully.

**Requirements:** R4

**Dependencies:** U1

**Files:**
- Modify: `docs/plans/2026-05-24-019-fix-master-pypi-regression-plan.md` (mark completed)

**Approach:** Mark plan 019 `status: completed` after U1 lands; note verification deferred to CI re-run.

**Test expectation:** none — documentation status update only.

**Verification:** Plan 019 status reflects merged PR #268 and bleeding-edge unblock.

---

## Verification (closeout)

| Check | Evidence | Result |
|-------|----------|--------|
| R1–R3: `.gitmodules` valid on `bleeding-edge` | `f15e4769d` on `origin/bleeding-edge`; `git config -f .gitmodules --list` parse OK; no `<<<<<<<` / `>>>>>>>` markers | ✅ pass (2026-05-24) |
| R4: remote `bleeding-edge` updated | `git rev-parse origin/bleeding-edge` = `f15e4769d` | ✅ pushed |
| Forward Commits re-run after #268 | [run 26361732290](https://github.com/OpenKotOR/PyKotor/actions/runs/26361732290) | ⏳ queued (post-fix) |
| PR #269 (docs closeout) | `fix/bleeding-edge-gitmodules` → `master` | ✅ open for plan traceability |

**Note:** The `.gitmodules` fix lands on branch `bleeding-edge` only (not via PR #269 diff to `master`). PR #269 documents the incident and closeout; `master` `.gitmodules` was already clean.

---

## Sources & References

- Failed run: https://github.com/OpenKotOR/PyKotor/actions/runs/26361732290
- Workflow: `.github/workflows/commit-all-to-bleeding-edge.yml`
- Prior plan: `docs/plans/2026-05-24-019-fix-master-pypi-regression-plan.md`
