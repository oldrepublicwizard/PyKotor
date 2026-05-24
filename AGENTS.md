# AGENTS.md

## Cursor Cloud specific instructions

### Overview

PyKotor is a pure-Python monorepo for modding Knights of the Old Republic I & II. It uses **uv** as the package manager with a workspace defined in the root `pyproject.toml`. Minimum supported Python is 3.8; local development may use 3.13 (per `.python-version`). See `README.md` and `CONTRIBUTING.md` for standard commands.

**Knowledgebase map:** `STRATEGY.md` (product intent and metrics) → `docs/plans/` (active execution plans) → `docs/solutions/` (validated learnings with YAML frontmatter: `title`, `component`, `problem_type`, `doc_status`, `last_verified`, plus optional `symptoms`, `root_cause`, `solution`, `prevention`, `related_docs`, `category`) → `wiki/` (public format and RE specs) → `docs/` (implementation deep dives). Solution categories today: `docs/solutions/documentation/` (e.g. BWM authority), `docs/solutions/logic-errors/` (e.g. save/load parity), `docs/solutions/testing/` (e.g. TSLPatcher parity harness, **verify-pypi regression closeout**). Relevant when implementing or debugging in documented areas.

### Running commands

Always use `uv run` to execute commands (per `.cursorrules`), e.g. `uv run pytest`, `uv run ruff check .`, `uv run pykotor --help`.

### PyPI verify local parity

When validating published PyPI packages (same checks as `.github/workflows/verify-pypi-regression.yml`) without waiting on CI:

```bash
python3 .github/scripts/local_verify_pypi_slice.py
python3 .github/scripts/local_verify_pypi_slice.py --json
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --json
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --json --compare-checkpoint
python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight
```

Use system **`python3`**, not `uv run`: workspace resolution can fail on unpublished packages (e.g. kotordiff). The script uses an ephemeral venv and installs `pykotor[all]` from PyPI. Documented CLI skips (kotordiff not on PyPI; `--help` rc≠0) match CI `continue-on-error` behavior. **`--json`** prints a machine-readable pass/skip/fail summary for agents. **`--ci-status-only`** queries latest Verify PyPI / Forward Commits runs via `gh` without installing packages (monitoring-only track). **`--compare-checkpoint`** adds a `checkpoint` object with `defer_lfg_pr` when run IDs and queued status match the solution doc **Last CI check** (plan 059). **`--exit-on-defer`** adds `lfg_deferred: true` and prints a stderr hint when the checkpoint is unchanged (plan 061). **`--monitor-preflight`** is shorthand for all four monitoring flags (plan 063).

See also `docs/solutions/testing/verify-pypi-regression-closeout.md` for prefer/defer/avoid guidance and CI closeout history.

When `checkpoint.defer_lfg_pr` or `lfg_deferred` is true, defer further LFG PRs on this track until status or conclusion changes (plans 056–063).

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
  --ignore=Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_file_dialog_components.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_keyboard_accessibility_conformance.py \
  Libraries/PyKotor/tests
```

**Gotchas:**
- **Scope tests to `Libraries/PyKotor/tests`** (matches `.github/workflows/python-package.yml`). Running pytest from the repo root without that path collects other packages (e.g. Toolset) and often fails during collection.
- **`--import-mode=importlib` is required on Linux**: Without it, pytest fails with `ModuleNotFoundError: No module named 'resource.formats'` because the test directory `Libraries/PyKotor/tests/resource/` collides with Python's stdlib `resource` module.

### System dependencies (already in snapshot)

Python 3.8–3.13, uv, g++/gfortran (for numpy build), and Qt6/OpenGL/xcb system libraries are pre-installed. The `CXX=g++` env var may be needed when `uv sync` rebuilds numpy from source.

### UI regeneration (convertui)

After changing any `.ui` file under `Tools/HolocronToolset/src/ui/`, run convertui to regenerate Python bindings under `toolset/uic/qtpy/`:

```bash
uv run python Tools/HolocronToolset/src/ui/convertui.py
```

This works after a successful `uv sync --all-packages --all-extras`. **Python 3.8 is the minimum target.** Dependencies are pinned so that on 3.8 the highest version compatible with 3.8 is used (e.g. `numpy>=1.19.0,<1.25`, `requests>=2.23.0,<2.32.5`, PyQt5 on 3.8 with PyQt5-Qt5 constrained to a version that has Windows wheels). On 3.9+ the same packages use `>=` current/min versions (e.g. `numpy>=1.25`, `requests>=2.32.4`). All such splits use `python_version < \"3.9\"` vs `python_version >= \"3.9\"` (and where needed, e.g. Pillow/PyQt6-sip, additional splits for 3.10+). This keeps 3.9–3.13 working with newer releases while 3.8 gets the latest 3.8-compatible versions.

### Git commits

- Proposed git commands must be copy-paste-ready **single-line** commands only. Do not include comments, shell prompts, or wrapped multi-line blocks.
- Use the normal PyKotor root add/commit command when only root-level files changed.
- If a submodule was updated, recommend a single one-line command that commits the PyKotor root changes including the submodule gitlink, then `cd`s into the submodule, runs `git add .`, commits with the same message, pushes when required, and `cd`s back to the PyKotor root.

## Learned User Preferences

- When implementing an existing plan, do not edit the plan file unless asked; mark the existing plan todos as work progresses instead of recreating them.
- For Holocron Toolset UI work, keep layouts and controls in `.ui` files, compile with `convertui.py`, and avoid building replacement UI directly in Python.
- Preserve broad compatibility for PyKotor and Holocron changes: Python 3.8 minimum plus Windows 7-11, macOS, Linux, and arm64 where practical.
- For wiki and reverse-engineering documentation, prefer comprehensive, authoritative coverage grounded in game behavior and external/source evidence over PyKotor-specific implementation notes.
- Give guidance and next steps to the person in this thread; avoid hypothetical third-party phrasing when they are the same audience you are replying to.
- When the user expects an outcome to be finished in-session, run the repo’s commands and iterate until it works yourself rather than instructing them to perform the steps manually.

## Learned Workspace Facts

- Installation and resource lookup tools must treat resource resolution order as a core invariant and expose priority behavior clearly when users need control.
- For wiki pages that enumerate references, vendors, or implementations, use normal markdown list syntax with one entry per line instead of comma-joined run-on lines.
- Holocron indoor-builder and Module Designer should converge on one editor surface over time; avoid treating IndoorMapBuilder and Module Designer as a permanent legacy versus modern split.
- For TGA to TPC in PyKotor, prefer the shared `read_tga` / `write_tpc` pipeline as the canonical API surface instead of parallel conversion helpers or duplicate entry points.
- Shell scripts meant for bash (Git Bash, WSL, Linux, macOS) should be committed with LF line endings; CRLF can break `bash` and WSL with `$'\r'` or `bash -n` failures.
- Do not add or re-enable GitHub Actions workflows that automatically mark issues or PRs stale or close them for inactivity unless the user explicitly wants that automation.
