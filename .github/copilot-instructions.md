# AI Coding Agent Instructions (PyKotor)

Concise, actionable guidance to get an AI productive fast. Prefer small, surgical changes that respect existing architecture.

## Core idea 🔧
- Core vs Tools: Libraries under `Libraries/` (e.g. PyKotor); Tools under `Tools/` (HolocronToolset, HoloPatcher, KotorDiff, BatchPatcher).
- Tools sit atop the core library. Keep library APIs stable; UI/tool code depends on them.
- Priorities: game game engine fidelity, type-safety, reproducible builds. See essentials below.

**Workspace Layout**
- Libraries: `Libraries/PyKotor/src`
- Tools: `Tools/HolocronToolset`, `Tools/HoloPatcher`, `Tools/KotorDiff`, `Tools/BatchPatcher`.
- Scripts & docs: `compile/` (build helpers), `docs/` (setup, tests), `wiki/` (format references).

**Setup & Run (Windows)**
- Preferred: `uv sync`, then activate `.venv\Scripts\activate`.
- Install editable packages selectively: `uv pip install -e Libraries/PyKotor [-e Tools/HolocronToolset ...]`.
- End users: `uvx --refresh holocrontoolset`, `uvx --refresh holopatcher`, `uvx --refresh kotordiff` (ensures latest).
- Developers: `uvx --with-editable Libraries/PyKotor --with-editable Tools/HolocronToolset holocrontoolset` (uses local source).

**Builds & Packaging**
- Use VS Code tasks / `compile/` scripts; don’t reinvent pipelines.
- PyInstaller one-file builds: tasks like "Build KotorDiff”, "Build K-BatchPatcher”, "Build GUI Creator”, "Build Model ASCII Compiler”, "Build Toolset - PyInstaller”.
- Respect excludes (numpy, PyQt6, PIL, matplotlib, multiprocessing, PyOpenGL, PyGLM, dl_translate, torch) as defined in tasks.

**Testing & Linting**
- Tests: `pytest` or `uv run pytest`. TSLPatcher unit testing suite lives under `tests/test_tslpatcher/`.
- Test assertions must be precise and strict: never simplify or weaken assertions. All tests should be asserting data and contents at the strictest most meticulous level possible (20-30 assertions each) e.g. do not ever assert 'length' or greater/less than checks, assertion and tests must be checking absolutes and values. Not just 'has content' or 'is not empty'.
- Static checks: `ruff` (style), `mypy` (types), `pylint` (analysis). Prefer targeted runs on changed modules.

**Conventions & Patterns**
- Qt UI: use `qtpy` for backend-agnostic bindings. New widgets live under `Libraries/PyKotor/src/utility/gui/qt/...`.
- Resource types: use `pykotor.resource.type.ResourceType` with format helpers; avoid ad-hoc parsers.
- Error strategy: raise typed exceptions from `pykotor` modules; present user-facing messages in Tools.
- Dependencies: keep `pyproject.toml` and `requirements.txt` mirrored; don’t drift.

**Game Engine Fidelity (REVA Essentials)**
- Treat K1 (swkotor.exe) and TSL (swkotor2.exe) as a unified game engine with conditional divergences; all functions exist in both.
- Mandatory workflow for game engine-related changes:
	1. Confirm/open both executables in REVA MCP: `open-project <full path to .gpr>` (e.g., `%USERPROFILE%\Odyssey.gpr`).
	2. Locate and decompile the relevant function in K1; note address and key logic.
	3. Locate the corresponding function in TSL; note address and key logic.
	4. Compare side-by-side; identify differences in logic/flow.
	5. Use unified naming for functions/features.
	6. Format addresses exactly per rules below.
	7. Write a single unified description/docstring with inline notes on differences.
	8. If an address is unknown, mark `TODO` and continue searching.
- Address formatting:
	- `FunctionName @ (K1: 0xADDRESS, TSL: 0xADDRESS)`; if unknown, `TODO: <task>` for the missing one.
	- Reference comment: `# Reference: K1 swkotor.exe:0xADDRESS, TSL swkotor2.exe:0xADDRESS`.
- Prohibited: single-game-only analysis, single-game headings, or addresses for only one game without noting the other.
- At the end of any response involving game engine-related changes, add exactly one:
	- `REVA status: Completed - Analyzed both K1 and TSL :)`
	- `REVA status: Partially completed - Missing TSL address for <function>, TODO find it :(`
	- `REVA status: Skipped - <exact reason> :(`

**Git Commit Discipline**
- Never use `git add .` / `git add -A` or any wildcard-all-files adds.
- Always add and commit one file at a time (or a tightly related small group).

**Toolset Integration Notes**
- Holocron Toolset is modular; see `Tools/HolocronToolset/CONVENTIONS.md` for Spyder plugin patterns.
- Avoid creating `ToolWindow` in plugin contexts; prefer Spyder-compatible widgets and signals.

**Useful Commands (Examples)**
```powershell
# Setup (Windows)
uv sync
.venv\Scripts\Activate.ps1

# Run tools from source (canonical uv run --directory ... --module)
$Env:QT_API="PyQt6"
uv run --directory Tools/HolocronToolset/src --module toolset
uv run --directory Tools/HoloPatcher/src --module holopatcher
```

**Quick Dev Runs (without uv / fallback)**
```powershell
# Run tools from source when uv not used (requires venv + pip install -r requirements.txt)
python Tools\HolocronToolset\src\toolset\__main__.py
python Tools\HoloPatcher\src\holopatcher\__main__.py
python Tools\KotorDiff\src\__main__.py
# Pattern (others): python Tools\<ToolName>\src\__main__.py
```

**VS Code Build Tasks (labels)**
- Build KotorDiff — one-file console binary via PyInstaller.
- Build K-BatchPatcher — one-file console binary via PyInstaller.
- Build GUI Creator — one-file console binary via PyInstaller.
- Build Model ASCII Compiler — one-file console binary via PyInstaller.
- Build Toolset - PyInstaller — bundled GUI build.

**REVA Project Path**
- Default `.gpr`: `%USERPROFILE%\Odyssey.gpr` (Windows).
- Use: `open-project %USERPROFILE%\Odyssey.gpr` before game engine analyses.

**Read First**
- README.md – overview, features, quick install.
- docs/SETUP.md – dev environment, dependency managers, testing.
- docs/QUICK_START.md – targeted test commands for TSLPatcher.
- Tools/HolocronToolset/CONVENTIONS.md – dual-mode UI integration.
- .cursorrules – game engine fidelity + commit discipline (mirrored above).
