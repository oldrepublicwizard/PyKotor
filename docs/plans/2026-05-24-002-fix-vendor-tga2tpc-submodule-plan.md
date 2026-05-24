---
title: "fix: register orphan vendor/tga2tpc submodule gitlink"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-check-default-branch
strategy_track: test-signal-quality
---

# fix: register orphan vendor/tga2tpc submodule gitlink

## Summary

Register the remaining orphan submodule `vendor/tga2tpc` in `.gitmodules` so recursive CI checkout succeeds (same pattern as `vendor/ref-tga2tpc` / `vendor/ref-xoreos-tools` fixes).

---

## Problem Frame

PR #266 `check-default-branch` and submodule-aware workflows fail with:

`fatal: No url found for submodule path 'vendor/tga2tpc' in .gitmodules`

Git index contains gitlink `vendor/tga2tpc` @ `758f3dbd` (same commit as `vendor/ref-tga2tpc`) but only `ref-tga2tpc` is registered.

---

## Requirements

- R1. `.gitmodules` includes `[submodule "vendor/tga2tpc"]` with URL `https://github.com/ndixUR/tga2tpc.git`.
- R2. Repo-wide orphan scan returns zero unmatched gitlinks.
- R3. No duplicate-path conflicts in submodule sync.

---

## Scope Boundaries

- Do not remove `vendor/tga2tpc` gitlink (may be referenced elsewhere); register only.
- MSDO / pytest fixes out of scope unless CI still fails after this.

---

## Implementation Units

- U1. Add `vendor/tga2tpc` entry to `.gitmodules`; verify `git submodule sync`.

**Verification:** Orphan scan clean; `git submodule sync vendor/tga2tpc` succeeds.

---

## Sources & References

- CI job 77568505543 (run 26350759644)
- Prior: `5fed98936`, `0042f8057`
