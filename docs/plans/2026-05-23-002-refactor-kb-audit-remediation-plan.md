---
title: "refactor: KB audit remediation batch A"
type: refactor
status: completed
date: 2026-05-23
origin: audit-knowledgebase-2026-05-23
strategy_track: test-signal-quality
---

# refactor: KB audit remediation batch A

## Summary

Land the knowledgebase authority ladder and high-impact audit fixes in one vertical slice: commit Batch A authority docs, repair broken navigation indexes, merge duplicate wiki audit plans, align CONTRIBUTING pytest guidance with AGENTS/CI, and close plan-vs-shipped drift on the parity harness manifest format.

---

## Problem Frame

The `/audit-knowledgebase` pass scored PyKotor at **51% (Partial)**. Agents and contributors misroute because (a) Batch A authority edits remain uncommitted, (b) `docs/INDEX.md` links to missing paths, (c) two wiki audit plans compete as authority, (d) CONTRIBUTING documents bare `pytest` while AGENTS/CI use scoped commands, and (e) the completed parity plan still references `manifest.yaml` while shipped code uses `manifest.json`.

---

## Requirements

- R1. HEAD reflects the declared KB ladder in `AGENTS.md` (STRATEGY → plans → solutions → wiki → docs).
- R2. BWM authority chain is committed: solutions doc, `docs/walkmesh.md` stub, `wiki/BWM-File-Format.md` redirect.
- R3. `STRATEGY.md` links the shipped parity harness path.
- R4. `docs/INDEX.md` navigation targets resolve (no dead links to missing files).
- R5. One wiki audit plan remains authoritative; the other is superseded with explicit frontmatter.
- R6. `CONTRIBUTING.md` Testing section matches AGENTS scoped pytest one-liner and Linux gotcha.
- R7. Completed parity plan documents `manifest.json` (not YAML).
- R8. BWM solution doc includes a copy-paste verification block.

---

## Scope Boundaries

- No wiki page rewrites in this batch (audit execution deferred).
- No splitting of `pykotor-test-suite-consolidation-plan.md` mega-file.
- No new `docs/knowledgebase/` hub tree (INDEX repair only).
- Do not commit unrelated `pyproject.toml` / `uv.lock` changes unless required for doc validation.

### Deferred to Follow-Up Work

- Add `docs/solutions/` entry for parity harness MVP learnings (separate PR).
- Merge `DOCUMENTATION_INDEX.md` or archive it.
- CI flake8 vs AGENTS ruff alignment.

---

## Context & Research

### Relevant Code and Patterns

- `AGENTS.md` — KB map + canonical pytest block (working tree includes `file_dialog` ignore).
- `STRATEGY.md` — metrics with parity harness link (working tree).
- `docs/solutions/*` — YAML frontmatter schema with `doc_status`, `last_verified`.
- `docs/kotordiff/README_TSLPATCHDATA_DOCS.md` — correct TSLPatchData doc hub.
- `Libraries/PyKotor/tests/tslpatcher/parity/manifest.json` — shipped registry.

### Institutional Learnings

- BWM policy: `docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md`.
- Save/load verify pattern: `docs/solutions/logic-errors/kotor-save-load-1-1-python-from-re.md`.

---

## Key Technical Decisions

- **INDEX repair via redirect hub, not full rewrite:** Replace broken relative links with paths under `docs/kotordiff/` and `Libraries/PyKotor/tests/`; add a top banner pointing to `AGENTS.md` KB map for general navigation.
- **Supersede older wiki audit plan:** Keep `docs/plans/2026-04-15-wiki-source-citation-audit-plan.md` as authority (sentence-level citations + external corroboration set); archive `docs/plans/wiki-source-audit-plan.md` with `status: superseded` and `superseded_by` pointer.
- **Parity plan amendment only:** Update Decision #3 and IU-1 text to JSON; do not change harness code.

---

## Implementation Units

- U1. **Land Batch A authority docs**

**Goal:** Commit KB ladder, STRATEGY parity link, solutions updates, walkmesh stub, BWM redirect.

**Requirements:** R1, R2, R3

**Dependencies:** None

**Files:**
- Modify: `AGENTS.md`, `STRATEGY.md`
- Modify: `docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md`
- Modify: `docs/solutions/logic-errors/kotor-save-load-1-1-python-from-re.md`
- Modify: `docs/walkmesh.md`, `docs/ideation/2026-05-23-pykotor-strategy-aligned-ideation.md`
- Create: `wiki/BWM-File-Format.md`
- Modify: `helper_scripts/agdec_save_load/README.md` (if part of save/load authority chain)

**Approach:**
- Stage only KB-related files; exclude `pyproject.toml` and `uv.lock`.

**Test scenarios:**
- Test expectation: none — documentation-only.

**Verification:**
- `git show HEAD:AGENTS.md` contains KB map and three `--ignore` paths.
- `wiki/BWM-File-Format.md` redirects to `Level-Layout-Formats.md#bwm`.

---

- U2. **Repair docs/INDEX.md navigation**

**Goal:** Fix all broken doc and test file links.

**Requirements:** R4

**Dependencies:** None

**Files:**
- Modify: `docs/INDEX.md`

**Approach:**
- Prefix TSLPatchData docs with `kotordiff/`.
- Point test examples to `Libraries/PyKotor/tests/tslpatcher/...`.
- Remove or mark missing legacy docs (`QUICK_START.md`, etc.) as archived/not maintained.
- Add banner: general KB navigation → `AGENTS.md` + `STRATEGY.md`.

**Test scenarios:**
- Happy path: every markdown link target in `docs/INDEX.md` resolves to an existing file.
- Edge case: pytest command examples use scoped path consistent with AGENTS.

**Verification:**
- Script or manual check: no 404 paths from INDEX relative links.

---

- U3. **Merge wiki audit plan authority**

**Goal:** Single authoritative wiki audit plan.

**Requirements:** R5

**Dependencies:** None

**Files:**
- Modify: `docs/plans/2026-04-15-wiki-source-citation-audit-plan.md` (add note absorbing tri-binary rules from sibling)
- Modify: `docs/plans/wiki-source-audit-plan.md` (add frontmatter `status: superseded`, `superseded_by`)

**Approach:**
- Copy tri-binary sourcing rules from superseded plan into authority plan's Working rules section.
- Do not delete superseded file (history preservation).

**Test scenarios:**
- Test expectation: none — plan metadata.

**Verification:**
- Superseded plan frontmatter points to 2026-04-15 plan; no conflicting "active" status on both.

---

- U4. **Align CONTRIBUTING pytest with AGENTS/CI**

**Goal:** Contributor onboarding matches agent/CI test commands.

**Requirements:** R6

**Dependencies:** U1 (AGENTS is source of truth)

**Files:**
- Modify: `CONTRIBUTING.md`

**Approach:**
- Replace bare `pytest` in Testing section with AGENTS scoped one-liner.
- Add Linux `--import-mode=importlib` gotcha bullet.
- Update pre-submit checklist line to reference scoped command.

**Test scenarios:**
- Test expectation: none — documentation.

**Verification:**
- CONTRIBUTING Testing section includes `Libraries/PyKotor/tests` and `--import-mode=importlib`.

---

- U5. **Close parity plan manifest drift + BWM verify block**

**Goal:** Completed plan matches shipped harness; BWM solution has verification.

**Requirements:** R7, R8

**Dependencies:** None

**Files:**
- Modify: `docs/plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md`
- Modify: `docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md`

**Approach:**
- Change `manifest.yaml` references to `manifest.json`; note `patchdata/` fixture layout vs runtime `tslpatchdata/` rename.
- Add `## How to verify` with link-check steps for BWM authority chain.

**Test scenarios:**
- Test expectation: none — documentation.

**Verification:**
- Grep plan file: zero `manifest.yaml` references.
- BWM solution contains `## How to verify`.

---

## System-Wide Impact

- **Interaction graph:** Agent onboarding (`AGENTS.md`), contributor onboarding (`CONTRIBUTING.md`), and CI gate docs converge.
- **Unchanged invariants:** Parity harness code, wiki format pages, pytest CI workflow behavior.

---

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| INDEX fix misses edge links | Validate all markdown links after edit |
| Supersession loses tri-binary rules | Explicit merge into authority plan |
| Commit includes unrelated lockfile changes | Stage explicit file list only |

---

## Sources & References

- KB audit scorecard (2026-05-23 conversation)
- `docs/plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md`
- `Libraries/PyKotor/tests/tslpatcher/parity/README.md`
