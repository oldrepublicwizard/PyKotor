# AGENTS.md

## Cursor Cloud specific instructions

### Overview

PyKotor is a pure-Python monorepo for modding Knights of the Old Republic I & II. It uses **uv** as the package manager with a workspace defined in the root `pyproject.toml`. Minimum supported Python is 3.8; local development may use 3.13 (per `.python-version`). See `README.md` and `CONTRIBUTING.md` for standard commands.

### Running commands

Always use `uv run` to execute commands (per `.cursorrules`), e.g. `uv run pytest`, `uv run ruff check .`, `uv run pykotor --help`.

### Lint

```
uv run ruff check .
uv run ruff format --check .
```

Pre-existing lint violations exist; 259 ruff findings are normal on the current codebase.

### Tests

```
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  --ignore=Libraries/PyKotor/tests/resource/formats/test_mdl_ascii.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py
```

**Gotchas:**
- **`--import-mode=importlib` is required on Linux**: Without it, pytest fails with `ModuleNotFoundError: No module named 'resource.formats'` because the test directory `Libraries/PyKotor/tests/resource/` collides with Python's stdlib `resource` module.
- `test_mdl_ascii.py` must be `--ignore`d: it tries to open KotOR game files from a hardcoded Windows path at *collection* time and will fail with `FileNotFoundError` if `K1_PATH`/`K2_PATH` env vars are not set to valid game directories.
- `test_registry_strict_typing.py` must be `--ignore`d on Linux: it imports the Windows-only `winreg` module unconditionally.
- Set `QT_QPA_PLATFORM=offscreen` for headless Qt test execution; `xvfb` is available but `offscreen` is simpler.
- The pytest process may crash (exit 134 / SIGABRT) during teardown due to PyQt6 thread cleanup. This is a known upstream issue and does not affect test results. Check the output for pass/fail counts before the crash.
- Many test failures are expected without KotOR game files installed (the `K1_PATH` and `K2_PATH` environment variables point to Windows paths by default in `.env`).

### Building / running the application

- **PyKotor CLI**: `uv run pykotor --help` — format conversions, archive operations, diffing, etc.
- **HolocronToolset GUI**: `QT_QPA_PLATFORM=offscreen uv run holocrontoolset` — requires display or offscreen mode.
- **HoloPatcher**: `uv run holopatcher --help`
- **KotorDiff**: `uv run kotordiff --help`

### Dependency sync

Run `CXX=g++ uv sync --all-packages --all-extras` (not bare `uv sync`) to install all workspace members (HolocronToolset, HoloPatcher, etc.) and dev extras (ruff, pytest plugins, type stubs). Bare `uv sync` only installs the root meta-package.

### System dependencies (already in snapshot)

Python 3.8–3.13, uv, g++/gfortran (for numpy build), and Qt6/OpenGL/xcb system libraries are pre-installed. The `CXX=g++` env var may be needed when `uv sync` rebuilds numpy from source.

### UI regeneration (convertui)

After changing any `.ui` file under `Tools/HolocronToolset/src/ui/`, run convertui to regenerate Python bindings under `toolset/uic/qtpy/`:

```bash
uv run python Tools/HolocronToolset/src/ui/convertui.py
```

This works after a successful `uv sync --all-packages --all-extras`. **Python 3.8 is the minimum target.** Dependencies are pinned so that on 3.8 the highest version compatible with 3.8 is used (e.g. `numpy>=1.19.0,<1.25`, `requests>=2.23.0,<2.32.5`, PyQt5 on 3.8 with PyQt5-Qt5 constrained to a version that has Windows wheels). On 3.9+ the same packages use `>=` current/min versions (e.g. `numpy>=1.25`, `requests>=2.32.4`). All such splits use `python_version < \"3.9\"` vs `python_version >= \"3.9\"` (and where needed, e.g. Pillow/PyQt6-sip, additional splits for 3.10+). This keeps 3.9–3.13 working with newer releases while 3.8 gets the latest 3.8-compatible versions.

## Learned User Preferences

- Edit only `.ui` files under `Tools/HolocronToolset/src/ui/`; never edit generated files under `uic/`.
- After changing any `.ui` file, run `Tools/HolocronToolset/src/ui/convertui.py` to regenerate Python bindings.
- Do not use `getattr(self.ui, "widgetName", None)` or similar for UI widgets; reference widgets directly (e.g. `self.ui.toolbarModuleCombo`) and compile the UI first so the uic has the widget.
- Do not construct Qt widgets (QPushButton, QLineEdit, QButtonGroup, QWidget, etc.) in Python; define all GUI in `.ui` files and use the LTR pattern (`self.ui = Ui_Form(); self.ui.setupUi(self)`).

## Learned Workspace Facts

- Holocron UI workflow is compile-first: change `.ui` → run convertui → then use `self.ui.<name>` in code; defensive getattr for UI is prohibited in `.cursorrules`.
- CLI command names should follow existing patterns and use domain-accurate terminology (e.g. avoid "archive" where Bioware or docs use different names).

### Reverse engineering (agdec-http MCP)

- Binary analysis tools (list-functions, search-everything, match-function, create-label, etc.) require a Ghidra project with at least one program **open/loaded**. If `list-project-files` returns Count: 0 or tools report "No program loaded", open the project and load a binary in Ghidra first; then MCP tools can target programs by project path (e.g. `/TSL/k2_win_gog_aspyr_swkotor2.exe`).
- When matching K1→K2, prefer search-everything and address/size/call-graph over match-function (which often returns wrong mappings). Apply labels from layout and cross-binary comparison.
- Wiki documentation stays conceptual only; no tool names or raw RE dumps in `.md`. Document resource resolution and engine behavior; link format pages to [KEY-File-Format](wiki/KEY-File-Format.md) for resolution order.
- Wiki format pages (e.g. BWM-File-Format.md) describe binary layout and game behavior only; do not include PyKotor class/method names, identity-based indexing, or implementation references.

### KotorMCP and MCP governance

- **Transport**: Run KotorMCP over **stdio** (local command). Do not bind to 0.0.0.0 or expose the server on the network.
- **Path safety**: Extract and write tools use `pykotor.tools.path_safety`: canonicalization, resolve-under-base, and allowlist. Do not bypass path validation.
- **No shadow MCPs**: Use the workspace-approved MCP configuration; do not install or enable unmanaged MCP servers without following project governance.
