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
- For Qt enum/flag properties in `.ui` (focusPolicy, contextMenuPolicy, allowedAreas, scrollBarPolicy, toolBarArea), use `<enum>Qt::...</enum>` or `<set>Qt::...|...</set>` in the `.ui` file so generated code works with PyQt6; do not set these in Python instead of in the `.ui`.
- When asked to refine, deepen, or extend a plan document only, change the named plan under `.cursor/plans/` (or the path given) and do not start executing the planned implementation until the user asks to begin that work.
- When the user specifies a no-pull-request delivery model for wiki or documentation batches, ship updates with commit and push (including the separate `wiki` submodule when that workflow applies) rather than opening pull requests.
- When merging or retiring a wiki page into another, remove the old page, update inbound links across the repo (wiki, `docs/`, batch catalogs, cross-references in plans or solutions notes), and run markdown link validation on the files you changed.
- For a complete, zero-omission inventory of files under a directory tree (for example every `*.ksy` under `vendor/bioware-kaitai-formats`), use a recursive shell listing instead of inferring from search tools or stale counts from earlier messages.
- When wiring Kaitai-backed parsing into `resource/formats`, integrate **one format at a time**, run that format’s tests before moving on, and keep public `*_auto.py` entry points and binary writer signatures compatible with existing callers unless the project explicitly changes scope.

## Learned Workspace Facts

- Holocron UI workflow is compile-first: change `.ui` → run convertui → then use `self.ui.<name>` in code; defensive getattr for UI is prohibited in `.cursorrules`.
- Holocron `Editor` subclasses can receive `InstallationToolbar.installation_changed` during `super().__init__` before `setupUi`; init any state handlers touch (e.g. `GITEditor._git`) before `super().__init__`, skip handlers until `ui` exists, and use `self._installation` for the first mode when the toolbar may have set it during construction.
- GFF auto-read treats binary GFF only when a known four-character type is immediately followed by `V3.2`; a non-zero start offset is applied only if every byte before that header is UTF-8 BOM, ASCII whitespace, or NUL, so arbitrary junk prefixes are not parsed as GFF.
- The generic GFF editor resolves `GFFContent` for save as loaded content, then `from_res` (special `.res` names only), then `from_resource_type` when unambiguous, else `GFFContent.GFF`; clear stored content on `new()`.
- CLI command names should follow existing patterns and use domain-accurate terminology (e.g. avoid "archive" where Bioware or docs use different names).
- Instance dialogs (e.g. DoorDialog) import `Ui_*` from `toolset.uic.qtpy.dialogs.instance.<name>`; ensure the `instance` package and the corresponding UI module (e.g. `door.py` from `.ui` + convertui or programmatic) exist.
- Root `wiki/` is a git submodule (`PyKotor.wiki.git`); initialize or update it before full-tree wiki scans, edits, or local link checks, and assume CI may need recursive submodule checkout to see wiki content.
- HolocronToolset packaging copies `wiki/**/*.md` into the shipped help tree; wiki layout or content changes affect what appears in the GUI help bundle.
- In Windows PowerShell, change directories with `Set-Location` or `cd` to a path; `cd /d` is cmd.exe-only and errors in PowerShell.
- For Kaitai Struct work, fix `.ksy` in upstream `bioware-kaitai-formats`, regenerate Python into `Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats/` via `Libraries/bioware-kaitai-formats/scripts/regenerate_python.py` (or compile + `Libraries/bioware-kaitai-formats/scripts/postprocess_generated.py`), then run `scripts/rewrite_kaitai_generated_imports.py` and `scripts/strip_https_from_kaitai_generated.py` on that tree. Regenerate compatibility shims with `scripts/rewrite_kaitai_compat_shims.py`. Do not hand-edit generated parsers for logic or layout fixes; adjust the `.ksy` and regenerate. Keep type hints Python 3.8–safe where they are evaluated at runtime (e.g. use `os.PathLike`, not `os.PathLike[str]`).
- PyKotor depends on the workspace package `bioware-kaitai-formats` (import name `bioware_kaitai_formats`). `pykotor.kaitai_generated` remains as thin shims for backward compatibility. Canonical `.ksy` sources still live in the separate `OldRepublicDevs/bioware-kaitai-formats` repo (clone into e.g. `vendor/bioware-kaitai-formats` for regeneration).
- For Kaitai-backed formats, prefer **one parse**: map the Kaitai object into existing `*_data` models (or consume its `*_content` string) and keep `BinaryReader` legacy paths only as fallback when `KaitaiStructError` or spec gaps require it; avoid `from_bytes` + full legacy re-read on the success path.
- Hand-maintained `Libraries/PyKotor/src/pykotor/**/*.py` (excluding `kaitai_generated/`): scrub third-party `https://` from docstrings and comments into wiki pages under `wiki/reverse_engineering_findings_*` (GitHub lines via `scripts/archive_github_url_lines.py`; other hosts in small `*_external_refs_pre_scrub.md` pages or appended sections on the matching GitHub archive). Keep in-code wording neutral and point the module docstring at the archive. `tslpatcher/writer.py` INI template sample lines that embed URLs are intentional fixture text, not RE citations.
