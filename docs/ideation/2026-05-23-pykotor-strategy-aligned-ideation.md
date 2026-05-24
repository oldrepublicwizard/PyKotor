---
date: 2026-05-23
topic: pykotor-strategy-aligned
focus: surprise-me (autonomous, no user intake)
mode: repo-grounded
---

# Ideation: PyKotor Strategy-Aligned Improvements

## Grounding Context

**Codebase context:** PyKotor is a uv monorepo (v2.3.12) centered on typed K1+TSL format I/O, with Holocron Toolset, HoloPatcher, KotorDiff, and KotorMCP as product surfaces. STRATEGY.md (2026-05-23) anchors four tracks: engine fidelity, end-to-end mod workflow, Module Designer convergence, agent-native tooling. Tool submodules are empty in many clones; save/load has dual APIs (convenience vs engine-parity flows); BWM authority lives at `wiki/Level-Layout-Formats#bwm`; ~2599 tests with consolidation plan pending; open HoloPatcher/TSLPatcher parity issues dominate GitHub (#83, #67, #59, #55, #53).

**Past learnings:** RE-first authority; dual API by intent; consolidate scattered wiki knowledge; partial landing with explicit backlog (`docs/solutions/`).

**Issue intelligence:** HoloPatcher/TSLPatcher parity cluster (compiler, HACKList, namespaces, ListIndex); cross-platform runtime (#54 Steam Deck, #77 libc).

**External context:** Radoub/nasher/nwt Aurora workflows; retro-data-structures parity matrix; Unity MCP tool breadth; BSPEntSpy post-compile entity editing; KOTORModSync orchestration above patcher.

## Ranked Ideas

### 1. TSLPatcher Parity Harness (Corpus + CI)

**Description:** Build a versioned test corpus of real TSLPatcher mod INIs (HACKList, namespace edge cases, struct ListIndex, Required/RequiredMsg) with expected install outcomes. Run headless HoloPatcher against vanilla+modded installs in CI; gate releases on parity with classic TSLPatcher or documented exceptions.

**Warrant:** `direct:` STRATEGY metric "TSLPatcher install parity"; open issues #83, #67, #59, #55, #53; `pykotor/tslpatcher/` is library-resident.

**Rationale:** Parity gaps are the highest-frequency user pain and block the end-to-end mod workflow track. A harness turns reactive issue fixes into a compounding regression asset.

**Downsides:** Corpus curation is labor-intensive; some mods may be redistribution-restricted; false positives if vanilla baselines drift.

**Confidence:** 85%

**Complexity:** High

**Status:** Partially landed — MVP harness at `Libraries/PyKotor/tests/tslpatcher/parity/` ([plan](../plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md), PR #266). Corpus expansion (#55, #53, HoloPatcher headless CI) remains open.

---

### 2. "Nasher for KotOR" — Git-Native Module Pipeline

**Description:** Productize the existing CLI verbs (`init`, `unpack`, `compile`, `pack`, `install`, `launch`) into one documented workflow with human-editable intermediates (JSON/GFF roundtrips), `.gitignore` templates, and round-trip diff validation — the mod author's daily loop without legacy Windows tools.

**Warrant:** `external:` nasher/nwt git-native Aurora workflows; `direct:` pyproject.toml already registers 70+ CLI commands including project build verbs.

**Rationale:** STRATEGY wins when a mod author completes edit→diff→patch→install on Linux. A named pipeline lowers cognitive load more than scattered subcommands.

**Downsides:** KotOR module complexity exceeds NWN in places (BWM, VIS, MDL); needs clear scope boundaries vs full Toolset.

**Confidence:** 80%

**Complexity:** Medium

**Status:** Unexplored

---

### 3. Living Format Parity Matrix (K1 / TSL)

**Description:** Publish and maintain a repo-visible matrix (wiki or `docs/`) listing each format's read/write/round-trip status for K1 and TSL, with caveats — modeled on Randovania's retro-data-structures table. Tie STRATEGY "format round-trip fidelity" metric to explicit cells.

**Warrant:** `external:` retro-data-structures parity matrix pattern; `direct:` README references Format Support Matrix but no authoritative in-repo table found in recent KB audit.

**Rationale:** Prevents over-claiming support, guides contributors, and gives agents/MCP a single truth surface for capability questions.

**Downsides:** Maintenance burden if not generated from tests; risk of stale cells without CI linkage.

**Confidence:** 78%

**Complexity:** Medium

**Status:** Unexplored

---

### 4. KotorMCP Vertical Slice — Top-10 CLI Action Parity

**Description:** Ship a minimal KotorMCP with ~10 high-value tools mirroring CLI: `validate-installation`, `grep/find` resources, `diff`, `patch-file`, `extract`, `compile`, `decompile`, installation path detection, and `kotor://` resource URIs. Document as STRATEGY track 4 MVP before full Toolset parity.

**Warrant:** `direct:` STRATEGY "Agent-native tooling" track; `docs/brainstorms/2026-03-12-kotormcp-mcp-builder-agent-native-brainstorm.md`; KotorMCP submodule empty but console scripts exist.

**Rationale:** Differentiates PyKotor vs xoreos/Kotor.NET in the AI-assisted modding lane with a shippable slice rather than all-or-nothing MCP coverage.

**Downsides:** Packaging gap (not in root deps); security/review surface for agent tools; submodule sync required for development.

**Confidence:** 75%

**Complexity:** High

**Status:** Unexplored

---

### 5. Save/Load Engine Parity Gate

**Description:** Add golden SAV fixture roundtrip tests and opt-in `SaveFolderEntry(engine_order=True)` delegation to flow modules. Close the dual-API drift documented in KB refresh; track remaining byte-level gaps in todo 001.

**Warrant:** `direct:` `docs/solutions/logic-errors/kotor-save-load-1-1-python-from-re.md` (partially_stale); flow modules + tests exist; SaveFolderEntry order differs from engine flows.

**Rationale:** Save/load is a trust-critical surface for save editors and tooling; sequence alignment without byte gates leaves silent compatibility risk.

**Downsides:** Golden fixtures may be game-install dependent; behavior change if default delegation flips.

**Confidence:** 72%

**Complexity:** Medium

**Status:** Unexplored

---

### 6. Radoub-Style Mod Author Hub (CLI + Launcher)

**Description:** Single entry command (e.g. `pykotor hub` or `holocron-hub`) orchestrating unpack→edit pointers→compile→pack→launch, routing to standalone editors or CLI — inspired by Radoub's Trebuchet hub without rebuilding every editor.

**Warrant:** `external:` Radoub Trebuchet hub; `direct:` root pyproject already exposes 40+ standalone Holocron editor entry points.

**Rationale:** Reduces fragmentation between Holocron standalone editors and library CLI; supports STRATEGY end-to-end workflow without waiting for full GUI refactor.

**Downsides:** Requires populated tool submodules or PyPI tool packages; UX design needed to avoid another half-finished shell.

**Confidence:** 70%

**Complexity:** Medium

**Status:** Unexplored

---

### 7. Walkmesh Roomlink Designer Slice

**Description:** One vertical slice in Module Designer: import WOK, edit perimeter transitions against LYT room indices, validate adjacency, export game-compatible BWM — leveraging authoritative `Level-Layout-Formats#bwm` and closing the "can't cross between rooms" debugging loop in-editor.

**Warrant:** `direct:` BWM solution doc outcome; STRATEGY Module Designer convergence; KOTORMax preferred for roomlinks per wiki; LEVEL_EDITOR_CHECKLIST gaps.

**Rationale:** Walkmesh/room transitions are a mod-author pain point that external tools (KOTORMax) still own; in-editor slice advances self-contained workflow metric.

**Downsides:** High 3D/UI complexity; overlaps Indoor Map Builder; perf budget (120 FPS) pressure.

**Confidence:** 68%

**Complexity:** High

**Status:** Unexplored

---

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | Delete all low-value tests immediately | Too vague without consolidation plan execution order; overlaps #3 quality gate |
| 2 | Wiki citation gate blocks all releases | Too expensive relative to value; better as staged audit |
| 3 | Agent-first: deprecate GUI | Subject-replacement tone; GUI remains primary mod author surface |
| 4 | Panda3D engine as product | Explicitly out of STRATEGY scope |
| 5 | KotorModSync load-order ownership | STRATEGY "not working on" |
| 6 | Zero-budget: drop Linux PyInstaller only | Tactical; insufficient meeting-test alone |
| 7 | 10x Hammer-class Module Designer in one sprint | Unbounded scope; belongs in brainstorm not ideation survivor |
| 8 | Resource resolution UI (full product) | Interesting but duplicate of Installation API docs; lower leverage than parity harness |
| 9 | Merge wiki audit plans (implementation) | Process fix, not product improvement — route to kb-stale-pruner |
| 10 | CONTRIBUTING pytest alignment | DX/doc fix; below product ideation floor |
| 11 | Submodule init documentation only | Necessary but not a strategic product move |
| 12 | LDtk entity export (full) | Premature without Module Designer entity model |
| 13 | BSPEntSpy-style GIT spy (full) | Strong adjacency but duplicates #7 scope; defer to brainstorm variant |
| 14 | TOML mod manifest alone | Weaker alone; folded into #1+#2 cross-cutting note |
| 15 | RE→Python factory (generic) | High value but too broad for one survivor; split in brainstorm |
| 16 | Expand docs/solutions/ (process) | Meta; important but not a user-facing product idea |
| 17 | Single-maintainer: tools PyPI-only | Constraint flip insight already captured in onboarding pain |
| 18 | Engine reimplementation pivot | Subject-replacement |
| 19 | Runtime DLL patch manager integration | Adjacent paradigm; out of install-time toolchain identity |
| 20 | nwt JSON5 GFF only | Subsumed by #2 nasher pipeline |

## Cross-Cutting Note

**Mod platform layer:** Combine #1 (parity harness) with a shared TOML manifest validator (KOTORModSync signal) so HoloPatcher becomes the execution engine for both standalone mods and orchestrated installs — strongest compound move across tracks 2 and 4.
