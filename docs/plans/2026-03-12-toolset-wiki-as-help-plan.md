# Toolset: Wiki as single source for help — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove `toolset/help` (and its `wiki/` subfolder and `contents.xml`); use repo `wiki/` as the only help source; generate contents.xml at startup; point updates and packaging at OpenKotOR/PyKotor wiki.

**Architecture:** Help path resolution uses only wiki (and vendor) base paths. A new module generates the Contents XML tree from the resolved wiki directory at startup; the legacy and new help windows load that (from memory or a generated temp file). Editor F1 help resolves wiki from the same bases. Updater fetches wiki content from OpenKotOR (e.g. main-repo wiki zip or GitHub wiki). Build/compile already bundle repo `wiki/`; remove help from package data and MANIFEST.

**Tech Stack:** Python 3.8+, setuptools, PyInstaller (compile), ElementTree, pathlib.

**Context:** Brainstorm: `docs/brainstorms/2026-03-12-toolset-wiki-as-help-brainstorm.md`. Repo research: help loaded in `help_paths.py`, `help_content.py`, `help.py`, `help_window.py`, `editor_help.py`, `help_updater.py`; `generate_help_contents.py` in `helper_scripts/wiki_scripts/` builds XML from `wiki/`; setup.py copies repo `wiki/` → `src/toolset/wiki`; compile_tool.py adds `wiki` via `--include-wiki-if-present`.

---

## Task 1: Add in-toolset contents generator (wiki → XML)

**Files:**
- Create: `Tools/HolocronToolset/src/toolset/help_contents.py`
- Test: `Tools/HolocronToolset/tests/test_help_contents.py` (optional; can be added later)

**Step 1:** Create `Tools/HolocronToolset/src/toolset/help_contents.py` that:
- Takes a `wiki_base: Path` (and optionally `xoreos_base: Path | None`).
- Scans `wiki_base.glob("*.md")` and optionally `xoreos_base.rglob("*.md")`.
- Categorizes wiki filenames like `helper_scripts/wiki_scripts/generate_help_contents.py`: Introduction (fixed list of Holocron-Toolset-*, Tutorial-*), Tools (Module-Editor, Map-Builder), Tutorials (Tutorial-*), File Formats, 2DA Files, GFF Files, NSS Shared/K1/TSL, TSLPatcher, HoloPatcher, Other, plus Xoreos if present.
- Builds an `xml.etree.ElementTree.Element` tree with root tag `Contents` version `"5"`, Folders and Documents with `file` set to the **wiki-relative path** (e.g. `Holocron-Toolset-Getting-Started.md`, `Tutorial-Creating-Custom-Robes.md`) or `vendor/xoreos-docs/...` for xoreos.
- Exposes `generate_contents_tree(wiki_base: Path, xoreos_base: Path | None = None) -> ET.Element` and optionally `write_contents_xml(path: Path, ...)` for tests.

Map Introduction entries to wiki filenames:
- Getting Started → `Holocron-Toolset-Getting-Started.md`
- Core Tab → `Holocron-Toolset-Core-Resources.md`
- Modules Tab → `Holocron-Toolset-Module-Resources.md`
- Override Tab → `Holocron-Toolset-Override-Resources.md`
Tools: Module Editor → `Holocron-Toolset-Module-Editor.md`, Map Builder → `Holocron-Toolset-Map-Builder.md`. Tutorials: Custom Robes → `Tutorial-Creating-Custom-Robes.md`, New Store → `Tutorial-Creating-a-New-Store.md`, Area Transitions → `Tutorial-Area-Transitions.md`, DLG Static Cameras → `Tutorial-Creating-Static-Cameras.md`. New Features Quick Guide → `Holocron-Toolset-New-Features-Guide.md` (in Introduction or Other). Only include documents whose file exists under `wiki_base` (or xoreos_base).

**Step 2:** Add a simple test in `Tools/HolocronToolset/tests/test_help_contents.py` that, given a temp dir with a few .md files, calls `generate_contents_tree` and asserts root.tag == "Contents", root.get("version") == "5", and at least one Folder exists. (Skip if tests dir structure doesn’t exist.)

**Step 3:** Run tests (if added). `uv run pytest Tools/HolocronToolset/tests/test_help_contents.py -v`

**Step 4:** Commit: `feat(toolset): add help_contents module to generate contents XML from wiki`

---

## Task 2: Resolve wiki base path and use generator on startup

**Files:**
- Modify: `Tools/HolocronToolset/src/toolset/gui/windows/help_paths.py`
- Modify: `Tools/HolocronToolset/src/toolset/gui/windows/help_content.py`
- Modify: `Tools/HolocronToolset/src/toolset/gui/windows/help.py`

**Step 1:** In `help_paths.py`, remove every reference to `toolset/help`. In `get_help_base_paths()` and in the list used by `get_help_file_path()`, remove:
- `repo_root / "Tools" / "HolocronToolset" / "src" / "toolset" / "help"`
- `exe_path / "help"` (frozen)
- `Path("./help")`
So the only bases remain: **wiki** (package/frozen/repo) and **vendor/xoreos-docs**. Add a function `get_wiki_base_path() -> Path | None` that returns the first existing base that looks like a wiki dir (has .md files): from the same order as current get_help_base_paths but only wiki and xoreos; or keep get_help_base_paths returning only wiki + vendor paths.

**Step 2:** In `help_content.py`, in `setup_contents()`: first try `get_help_file_path("contents.xml")`. If None or file doesn’t exist, call `help_contents.generate_contents_tree(wiki_base, xoreos_base)` using the first valid wiki base from `get_help_base_paths()` (filter to a path that contains .md files). Build the tree in memory; use that ElementTree root for `_setup_contents_rec_xml` instead of parsing a file. Set version from root.get("version", "5"). Remove the fallback to `help/contents.xml`.

**Step 3:** In `help.py`, in `_setup_contents()`: same logic — if `get_help_path() / "contents.xml"` doesn’t exist (or get_help_path is removed), use generated tree from `help_contents.generate_contents_tree(...)` with wiki base from path resolution. Replace `ET.parse(str(get_help_path() / "contents.xml"))` with loading from the generator when no contents.xml is found. Also change `setSearchPaths` to use `get_help_base_paths()` from help_paths (so the text display resolves links against wiki/vendor).

**Step 4:** Run the toolset locally (no freeze) with repo root `wiki/` present and confirm the help window opens and shows a TOC; click a few entries and confirm content loads.

**Step 5:** Commit: `feat(toolset): generate contents.xml from wiki on startup; drop help path`

---

## Task 3: Editor help use wiki path only

**Files:**
- Modify: `Tools/HolocronToolset/src/toolset/gui/dialogs/editor_help.py`

**Step 1:** In `get_wiki_path()`, remove the branch that returns `this_file_path.parents[2] / "help" / "wiki"`. In development, return the same wiki path as the rest of the toolset: e.g. `repo_root / "wiki"` if it exists, else `toolset_package / "wiki"` (from Path(toolset.__file__).parent), matching the order in help_paths. When frozen, keep `exe_path / "wiki"`.

**Step 2:** Run toolset, open an editor that shows F1/wiki help, confirm a wiki .md file loads.

**Step 3:** Commit: `fix(toolset): editor help resolve wiki from repo/wiki or package wiki`

---

## Task 4: Remove toolset/help from repo and package data

**Files:**
- Delete: entire directory `Tools/HolocronToolset/src/toolset/help/` (all of its contents and the directory itself)
- Modify: `Tools/HolocronToolset/pyproject.toml`
- Modify: `Tools/HolocronToolset/MANIFEST.in`

**Step 1:** Delete `Tools/HolocronToolset/src/toolset/help/` (including `help/wiki/`, `help/contents.xml`, `help/introduction*.md`, `help/tools/`, `help/tutorials/`).

**Step 2:** In `pyproject.toml`, under `[tool.setuptools.packages.find]` or package data, remove any `help/**` entries. Keep only `wiki/**/*.md` (and correct the comment to say wiki is copied to `src/toolset/wiki`).

**Step 3:** In `MANIFEST.in`, remove `recursive-include src/toolset/help ...`. Keep `recursive-include src/toolset/wiki *.md` (wiki is populated by setup.py before sdist).

**Step 4:** Run `uv run pyinstaller` or build from Tools/HolocronToolset and confirm no references to `help` in package data break the build.

**Step 5:** Commit: `chore(toolset): remove toolset/help; package only wiki`

---

## Task 5: Help updater fetch from OpenKotOR wiki

**Files:**
- Modify: `Tools/HolocronToolset/src/toolset/gui/windows/help_updater.py`
- Modify: `Tools/HolocronToolset/src/toolset/config.py` (or wherever `get_remote_toolset_update_info` and help version live)

**Step 1:** Decide updater source: (A) Download a zip of the main repo’s `wiki/` folder (e.g. from a GitHub API URL like `https://github.com/OpenKotOR/PyKotor/archive/refs/heads/master.zip` and extract `PyKotor-master/wiki` into the app’s wiki location), or (B) use the GitHub wiki repo clone URL and tarball (e.g. `https://api.github.com/repos/OpenKotOR/PyKotor.wiki/tarball`). Recommended: (A) so the updater matches the same content as repo root `wiki/` and compile. Implement in `help_updater.py`: replace `download_github_file("th3w1zard1/PyKotor", ..., "/Tools/HolocronToolset/downloads/help.zip")` with fetching from OpenKotOR/PyKotor (e.g. main branch archive or a release asset that contains wiki). Extract into the **wiki** directory the app uses (e.g. same path as `get_help_base_paths()[0]` or a dedicated “downloaded help” dir that is then used as wiki base). If the app is frozen, extract to exe-relative `wiki/` or a user-writable location and point the next startup to it.

**Step 2:** Update `get_remote_toolset_update_info` (or equivalent) so the “help” version / URL refers to OpenKotOR/PyKotor. If the project stores help version in a file on the repo (e.g. `Tools/HolocronToolset/downloads/help_version.txt`), add or move that to a path under OpenKotOR/PyKotor and update the config to read it from there.

**Step 3:** Remove `get_help_path()` usage from help_updater (or make it return the wiki path). Remove any creation of `help/`; create/update only `wiki/`.

**Step 4:** Commit: `feat(toolset): help updater fetch wiki from OpenKotOR/PyKotor`

---

## Task 6: Legacy help.py stop using get_help_path for contents and search paths

**Files:**
- Modify: `Tools/HolocronToolset/src/toolset/gui/windows/help.py`

**Step 1:** Replace `get_help_path()` with the same wiki/base resolution as help_content: use `get_help_base_paths()` for search paths and for deciding where to load content. Remove or deprecate `get_help_path()` in help.py if it’s only used there; if it’s used in help_updater, keep a single “wiki directory” getter in help_paths (e.g. `get_wiki_path_for_updates()`) that returns the writable wiki location for the updater.

**Step 2:** Ensure `showEvent` sets `setSearchPaths` to `get_help_base_paths()` (list of wiki + vendor paths). Ensure `display_file` resolves the clicked file path via `get_help_file_path(relative_path)`.

**Step 3:** Run help window (legacy) and confirm TOC and content load from wiki.

**Step 4:** Commit: `fix(toolset): legacy help window use wiki bases and generated contents`

---

## Task 7: Update helper script and CI (optional)

**Files:**
- Modify: `helper_scripts/wiki_scripts/generate_help_contents.py`

**Step 1:** Change `generate_help_contents.py` so it no longer writes to `Tools/HolocronToolset/src/toolset/help/contents.xml`. Either (a) remove the script, or (b) have it write to a temp path or to `Tools/HolocronToolset/src/toolset/wiki/contents.xml` for one-off use, or (c) document that the toolset generates contents at runtime and this script is only for reference/offline generation. Prefer (c) or (b) so CI/docs can still generate a static contents.xml for inspection.

**Step 2:** If there is a CI job that builds or publishes “help” (e.g. help.zip), change it to build from repo `wiki/` and publish under OpenKotOR/PyKotor (e.g. release asset or a known URL). Document the URL in help_updater or config.

**Step 3:** Commit: `chore: generate_help_contents and CI use wiki; no toolset/help`

---

## Task 8: Compile and packaging verification

**Files:**
- Verify: `compile/compile_tool.py`, `compile/compile_toolset.ps1`, `Tools/HolocronToolset/setup.py`

**Step 1:** Confirm `compile_tool.py` with `--include-wiki-if-present` adds repo root `wiki/` to PyInstaller `--add-data` (already does). Confirm no step copies or expects `toolset/help`.

**Step 2:** Run the compile script for the toolset (e.g. `compile/compile_toolset.ps1` or equivalent). After build, run the generated exe and open the help window; confirm TOC and wiki pages load from the bundled wiki.

**Step 3:** Run `uv build` (or `python -m build`) from Tools/HolocronToolset; confirm sdist includes `src/toolset/wiki` and does not include `src/toolset/help`. Install the built package in a clean env and run the toolset; confirm help works from the installed wiki.

**Step 4:** Commit: `chore: verify compile and sdist bundle wiki only; no help`

---

## Summary of file changes

| Action | Path |
|--------|------|
| Create | `Tools/HolocronToolset/src/toolset/help_contents.py` |
| Create | `Tools/HolocronToolset/tests/test_help_contents.py` (optional) |
| Modify | `Tools/HolocronToolset/src/toolset/gui/windows/help_paths.py` |
| Modify | `Tools/HolocronToolset/src/toolset/gui/windows/help_content.py` |
| Modify | `Tools/HolocronToolset/src/toolset/gui/windows/help.py` |
| Modify | `Tools/HolocronToolset/src/toolset/gui/dialogs/editor_help.py` |
| Modify | `Tools/HolocronToolset/src/toolset/gui/windows/help_updater.py` |
| Modify | `Tools/HolocronToolset/src/toolset/config.py` (or update-info module) |
| Modify | `Tools/HolocronToolset/pyproject.toml` |
| Modify | `Tools/HolocronToolset/MANIFEST.in` |
| Modify | `helper_scripts/wiki_scripts/generate_help_contents.py` |
| Delete | `Tools/HolocronToolset/src/toolset/help/` (entire directory) |

---

## References

- Brainstorm: `docs/brainstorms/2026-03-12-toolset-wiki-as-help-brainstorm.md`
- Existing generator: `helper_scripts/wiki_scripts/generate_help_contents.py`
- Path resolution: `Tools/HolocronToolset/src/toolset/gui/windows/help_paths.py`
- Setup wiki copy: `Tools/HolocronToolset/setup.py`
- Compile: `compile/compile_tool.py` (--include-wiki-if-present), `compile/compile_toolset.ps1`
