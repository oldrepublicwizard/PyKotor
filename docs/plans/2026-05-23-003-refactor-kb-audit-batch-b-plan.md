---
title: "refactor: KB audit batch B — solutions companion and doc index repair"
type: refactor
status: completed
date: 2026-05-23
origin: docs/plans/2026-05-23-002-refactor-kb-audit-remediation-plan.md
strategy_track: test-signal-quality
---

# refactor: KB audit batch B — solutions companion and doc index repair

## Summary

Complete the next KB audit follow-ups: add a focused `docs/solutions/` companion for the TSLPatcher parity harness MVP, and repair root `DOCUMENTATION_INDEX.md` so it reflects the declared authority ladder and does not link to missing setup docs or bare `pytest`.

---

## Problem Frame

Batch A landed the authority ladder and repaired `docs/INDEX.md`, but three gaps remain from the audit: (1) parity harness learnings live only in plan/README, not in `docs/solutions/`; (2) root `DOCUMENTATION_INDEX.md` still links to missing `docs/SETUP.md` and `docs/QUICK_START.md` and shows unscoped `pytest`; (3) agents reading the root index misroute despite Batch A fixes elsewhere.

---

## Requirements

- R1. New solution doc captures parity harness prefer/defer/avoid, manifest.json schema, INI u32 syntax, and verification command.
- R2. Solution uses standard YAML frontmatter (`doc_status`, `last_verified`, `related_docs`, `prevention`).
- R3. `DOCUMENTATION_INDEX.md` removes or replaces broken links (`docs/SETUP.md`, `docs/QUICK_START.md`).
- R4. Root index points to `AGENTS.md` KB map and `STRATEGY.md` for agent/contributor navigation.
- R5. Root index pytest examples match AGENTS scoped command.
- R6. No unrelated workspace dependency changes (`pyproject.toml` / `uv.lock` out of scope).

---

## Scope Boundaries

- No wiki page edits.
- No CI flake8/ruff alignment (deferred).
- Do not split test consolidation mega-plan.

---

## Implementation Units

- U1. **Parity harness solutions companion**

**Goal:** Promote harness MVP into validated learnings layer.

**Requirements:** R1, R2

**Files:**
- Create: `docs/solutions/testing/tslpatcher-parity-harness-mvp.md`

**Approach:** Mirror save-load solution structure; link manifest, runner, README, STRATEGY metric, parity plan.

**Test scenarios:** Test expectation: none — documentation.

**Verification:** File exists with frontmatter and `## How to verify` block.

---

- U2. **Repair DOCUMENTATION_INDEX.md**

**Goal:** Fix broken navigation at repo root.

**Requirements:** R3, R4, R5

**Files:**
- Modify: `DOCUMENTATION_INDEX.md`

**Approach:**
- Add KB navigation section (AGENTS → STRATEGY → plans → solutions → wiki).
- Remove references to missing SETUP/QUICK_START or replace with CONTRIBUTING + AGENTS.
- Replace bare `pytest` quick reference with scoped AGENTS one-liner.
- Link new parity harness solution doc.

**Verification:** No links to non-existent `docs/SETUP.md` or `docs/QUICK_START.md`.

---

## Key Technical Decisions

- **Solutions path:** `docs/solutions/testing/` — matches category folder pattern used by `documentation/` and `logic-errors/`.
- **INDEX strategy:** Repair in place rather than archive — file is linked from README-adjacent contexts; slim stale Figma session stats rather than delete entire sections.

---

## Sources & References

- `Libraries/PyKotor/tests/tslpatcher/parity/README.md`
- `docs/plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md`
- `docs/plans/2026-05-23-002-refactor-kb-audit-remediation-plan.md` (Deferred follow-ups)
