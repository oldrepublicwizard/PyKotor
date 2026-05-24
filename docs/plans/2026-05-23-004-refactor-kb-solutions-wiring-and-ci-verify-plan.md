---
title: "refactor: KB solutions wiring and CI parity verification"
type: refactor
status: completed
date: 2026-05-23
origin: docs/plans/2026-05-23-003-refactor-kb-audit-batch-b-plan.md
strategy_track: test-signal-quality
---

# refactor: KB solutions wiring and CI parity verification

## Summary

Close the loop between STRATEGY metrics, the solutions layer, and CI: cross-link the parity harness solution from STRATEGY and AGENTS, enumerate solutions categories for agents, and verify the canonical scoped pytest command collects and passes parity harness tests locally.

---

## Problem Frame

Batch B added `docs/solutions/testing/tslpatcher-parity-harness-mvp.md`, but STRATEGY still points only at the harness path (not the solution doc), and AGENTS describes solutions generically without category examples. CI on PR #266 is re-running; we need local proof that parity tests are in the CI collection path before claiming merge readiness.

---

## Requirements

- R1. `AGENTS.md` KB map lists solution category folders with one example path each (`documentation/`, `logic-errors/`, `testing/`).
- R2. `STRATEGY.md` TSLPatcher parity metric links the solutions companion doc.
- R3. Canonical scoped pytest (AGENTS command) collects `tslpatcher/parity/` tests.
- R4. Parity harness tests pass under that command locally.
- R5. Accidental local `pyproject.toml` / `uv.lock` drift is reverted (not committed).

---

## Scope Boundaries

- No new parity corpus cases.
- No CI workflow edits unless collection fails.
- No flake8/ruff CI migration.

---

## Implementation Units

- U1. **Cross-link solutions in AGENTS and STRATEGY**

**Files:** `AGENTS.md`, `STRATEGY.md`

**Verification:** Grep finds `docs/solutions/testing/tslpatcher-parity-harness-mvp.md` in STRATEGY; AGENTS lists three category examples.

---

- U2. **Run CI-scoped pytest including parity collection**

**Files:** none (verification only; fix test/workflow only if R3/R4 fail)

**Verification:** pytest output shows parity tests collected and passed.

---

- U3. **Revert accidental lockfile drift**

**Files:** restore `pyproject.toml`, `uv.lock`

**Verification:** `git status` clean except intentional doc edits.

---

## Sources & References

- `docs/solutions/testing/tslpatcher-parity-harness-mvp.md`
- `.github/workflows/python-package.yml`
- AGENTS.md pytest block
