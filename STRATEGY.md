---
name: PyKotor
last_updated: 2026-05-23
---

# PyKotor Strategy

## Target problem

KotOR modding still runs on fragmented, Windows-centric legacy tools and ad-hoc format parsers. The crux is that mod authors cannot reliably move from edit → diff → patch → install on modern platforms without engine-fidelity gaps breaking real mods.

## Our approach

Build one typed, cross-platform Python toolchain anchored on reverse-engineered K1+TSL fidelity — shared library, CLI, Holocron Toolset, HoloPatcher, KotorDiff, and KotorMCP — so every format and install path is game-verified before it ships.

## Who it's for

**Primary:** Mod author — they're hiring PyKotor to author, package, and install KotOR I/II mods without legacy Windows-only tools.

**Secondary:** Developer / integrator — they're hiring PyKotor to automate mod pipelines, CI, and AI-assisted modding via library and MCP APIs.

## Key metrics

- **TSLPatcher install parity** — mods install identically to classic TSLPatcher; tracked via [`Libraries/PyKotor/tests/tslpatcher/parity/`](Libraries/PyKotor/tests/tslpatcher/parity/) (manifest + parametrized pytest), [`docs/solutions/testing/tslpatcher-parity-harness-mvp.md`](docs/solutions/testing/tslpatcher-parity-harness-mvp.md) (prefer/defer/avoid), HoloPatcher regression tests when submodules are initialized, and open parity issues (#83, #67, #59)
- **Format round-trip fidelity** — read→write→read produces game-compatible output; tracked via scoped pytest in `Libraries/PyKotor/tests`
- **Cross-platform install success** — HoloPatcher runs on Windows, macOS, Linux, and Steam Deck; tracked via CI matrix and platform issue resolution (#54, #77)
- **Module Designer performance** — ≥120 FPS (≤8.33 ms frame budget); tracked via GL performance benchmarks and `docs/plans/2026-03-12-feat-module-designer-performance-bottleneck-plan.md`
- **Module Designer self-contained workflow** — level design without external tools; tracked via `docs/LEVEL_EDITOR_CHECKLIST.md` success criteria
- **Test signal quality** — high-value regression coverage without ~2600-test noise; tracked via [`docs/plans/pykotor-test-suite-consolidation-plan.md`](docs/plans/pykotor-test-suite-consolidation-plan.md) and CI green on master via [`.github/workflows/python-package.yml`](.github/workflows/python-package.yml) (Python 3.9–3.11 primary gate; Python 3.8 minimum supported per AGENTS.md)

## Tracks

### Engine fidelity & format library

Reverse-engineered, unified K1+TSL format I/O with strict typing — the moat every tool surface depends on.

_Why it serves the approach:_ Without game-verified formats, the rest of the toolchain cannot earn mod author trust.

### End-to-end mod workflow

Holocron authoring → KotorDiff patch data → HoloPatcher install, with TSLPatcher compatibility as the acceptance bar.

_Why it serves the approach:_ The product wins when a mod author completes the full loop on Linux without legacy tools.

### Module Designer convergence

**Current:** Indoor Map Builder (Layout workflow) runs inside Module Designer. **Target:** one editor surface with contextual modes (Layout, walkmesh, module editing) per `docs/LEVEL_EDITOR_CHECKLIST.md`; close gaps (transform gizmos, walkmesh editing, inspector).

_Why it serves the approach:_ Duplicate editor surfaces drain maintenance and block the north-star level-design UX.

### Agent-native tooling

KotorMCP (emerging; submodule/PyPI packaging in progress) plus CLI action parity so every Toolset workflow is reachable by agents and automation.

_Why it serves the approach:_ Differentiates PyKotor from xoreos, reone, and Kotor.NET in the emerging AI-assisted modding lane.

## Not working on

- KotOR engine reimplementation (reone / KotOR.js territory)
- Multi-mod load-order orchestration (KotorModSync's lane)
- Panda3D game engine as a shipping product surface (experimental research only)

## Marketing

**One-liner:** A modern, cross-platform Python ecosystem for reading, modifying, and installing Knights of the Old Republic mods — with game-engine fidelity built in.

**Key message:** PyKotor replaces the legacy Windows toolchain with one typed library and integrated tools (Holocron, HoloPatcher, KotorDiff, CLI, MCP). Mod authors get authoring, packaging, and installation on any platform; developers get automation APIs grounded in reverse-engineered K1+TSL behavior.
