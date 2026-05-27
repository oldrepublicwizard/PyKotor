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
python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight --strict-defer-exit  # exit 2 when deferred
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --emit-checkpoint-snippet  # Last CI check markdown
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --validate-checkpoint-doc --json  # doc vs live drift
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --compare-checkpoint --apply-checkpoint-snippet --json  # dry-run doc apply
python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight --auto-apply-on-proceed --write  # apply docs when CI terminal
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --compare-checkpoint --dispatch-on-proceed --json  # dry-run gh dispatch plan
python3 .github/scripts/local_verify_pypi_slice.py --monitor-preflight --include-proceed-actions  # dry-run doc + dispatch previews
python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh  # one-shot doc apply / dispatch / sync (blocked when deferred)
python3 .github/scripts/local_verify_pypi_slice.py --lfg-preflight  # monitor + refresh dry-run + proceed_hint
python3 .github/scripts/local_verify_pypi_slice.py --lfg-gate  # lfg-preflight + strict-defer-exit
python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-gate  # lfg-gate + strict-pr-ci-exit
python3 .github/scripts/local_verify_pypi_slice.py --lfg-merge-watch --watch-interval 30 --watch-stall-polls 6 --watch-timeout 7200  # extended poll + stall detection
python3 .github/scripts/local_verify_pypi_slice.py --lfg-closeout  # lfg-refresh + write (terminal doc sync)
python3 .github/scripts/local_verify_pypi_slice.py --lfg-refresh --dry-run  # preview refresh actions without side effects
python3 .github/scripts/local_verify_pypi_slice.py --ci-status-only --compare-checkpoint --dispatch-on-proceed --execute --cancel-stale --sync-docs-after-dispatch --write  # dispatch + doc sync
```

Use system **`python3`**, not `uv run`: workspace resolution can fail on unpublished packages (e.g. kotordiff). The script uses an ephemeral venv and installs `pykotor[all]` from PyPI. Documented CLI skips (kotordiff not on PyPI; `--help` rc≠0) match CI `continue-on-error` behavior. **`--json`** prints a machine-readable pass/skip/fail summary for agents. **`--ci-status-only`** queries latest Verify PyPI / Forward Commits runs via `gh` without installing packages (monitoring-only track). **`--compare-checkpoint`** adds a `checkpoint` object with `defer_lfg_pr` when run IDs and active status match the solution doc **Last CI check** (plan 059). **`--exit-on-defer`** adds `lfg_deferred: true` and prints a stderr hint when the checkpoint is unchanged (plan 061). **`--monitor-preflight`** is shorthand for monitoring flags plus embedded **`doc_validation`** and **`checkpoint_snippet`** (plans 063–070). **`--strict-defer-exit`** exits **2** when deferred so `/lfg` can stop before noop PRs (plan 064); exit **0** when monitoring may proceed or docs need updating after terminal runs. **`--validate-checkpoint-doc`** reports solution doc vs live gh run ID and status drift (plans 068–069). **`fc_sha_stale_benign`** in checkpoint JSON means FC SHA lag is docs-only and no FC re-dispatch needed (plan 068). **`--auto-apply-on-proceed`** embeds `doc_apply` in preflight when `lfg_proceed_reason` is eligible; pair with **`--write`** after terminal CI (plan 073). **`--dispatch-on-proceed`** embeds `dispatch_on_proceed` dry-run when `proceed_reason` is `refresh_verify_dispatch` or `refresh_fc_dispatch`; add **`--execute`** and optional **`--cancel-stale`** to run `gh workflow run` / `gh run cancel` (plan 074). **`--include-proceed-actions`** embeds both `doc_apply` and `dispatch_on_proceed` dry-runs when eligible (plan 075). **`--sync-docs-after-dispatch`** with **`--execute --write`** re-fetches gh runs after dispatch and updates monitoring docs when run IDs change (plan 075). **`--lfg-refresh`** is a one-shot alias for compare + apply + dispatch + cancel-stale + sync-docs; blocked when deferred, checkpoint parse/gh errors, or `classify_fc_stale_gap` (plan 076–077). Pair with **`--dry-run`** to embed `lfg_refresh_plan` and proceed-action previews without write/execute (plan 077). **`--lfg-preflight`** is shorthand for monitor + refresh dry-run + **`proceed_hint`** (plan 078). **`--lfg-gate`** adds **`--strict-defer-exit`** after full JSON (plan 079). **`--lfg-merge-gate`** adds **`--strict-pr-ci-exit`** (plan 085). **`--lfg-merge-watch`** adds poll + stderr progress (plan 086). **`--lfg-pr-watch`** polls PR check rollup (plan 085). **`pending_check_details`** / **`failed_check_details`** include job URLs (plan 086). **`lfg_exit_code`** in JSON under strict flags (plan 087). **`lfg_exit_reason`** and **`pr_ci_progress`** on PR rollup (plans 088–089). **`lfg_exit_codes`** legend in strict JSON (plan 090). **`merge_actions`**, **`next_pending_check`**, and **`next_failed_check`** in strict JSON (plans 091–092). **`pr_watch_history`**, **`pr_ci_bottlenecks`**, **`--watch-stall-polls`**, **`queue_stalled`** vs **`stalled`** (plans 093–094). **`pr_queue_stalled`** when 0 jobs running (plan 094). **`--watch-exit-on-queue-stall`** for early exit on queue backlog (default: continue watch, plan 095). **`no_open_pr`** when no PR on branch (plan 090). **`pr_merge_conflicts`** when mergeable is CONFLICTING (plan 087). **`--lfg-closeout`** runs refresh with **`--write`** when CI is terminal (plan 080). JSON includes **`lfg_mode`** for agent routing. **`lfg_track_complete`** when docs match live gh (plan 082). **`pr_merge_status`** / **`merge_hint`** when track complete (plan 083). **`pr_merge_ready`**, **`lfg_merge_blocked`**, and deduped check names in rollup (plans 084–085). **`--strict-pr-ci-exit`** exits **3** when PR CI blocks merge (plan 084). Post-dispatch sync polls gh up to 3 times (2s interval) by default; override with **`--dispatch-poll-attempts`** / **`--dispatch-poll-interval`**. Checkpoint JSON includes **`lfg_proceed`** / **`lfg_proceed_reason`** when not deferring (plan 073).

See also `docs/solutions/testing/verify-pypi-regression-closeout.md` for prefer/defer/avoid guidance and CI closeout history.

When `checkpoint.defer_lfg_pr` or `lfg_deferred` is true, defer further LFG PRs on this track until status or conclusion changes (plans 056–066). When `checkpoint.verify_sha_stale` is true, proceed with verify refresh (cancel + `workflow_dispatch`) per plan 055/066 — do not defer.

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
