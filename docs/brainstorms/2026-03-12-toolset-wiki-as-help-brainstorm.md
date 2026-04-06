---
date: 2026-03-12
topic: toolset-wiki-as-help
---

# Holocron Toolset: Wiki as single source for help

## What we're building

- **Remove** from the repo: `Tools/HolocronToolset/src/toolset/help/` (entire folder: `help/wiki/`, `contents.xml`, introduction/tools/tutorials .md files). No more duplicated wiki or static contents.xml in the toolset.
- **Single source of truth:** Repo root `wiki/` for all help content. When running locally, the toolset uses `wiki/`; when packaged (PyPI or compile), the build copies `wiki/` into the package/exe.
- **Generate contents.xml on startup:** The toolset builds the help TOC (contents.xml structure) at runtime from the available wiki (and optionally vendor/xoreos-docs), so no static contents.xml is shipped.
- **Update pipelines:** In-app “check for updates” for help should fetch from **OpenKotOR/PyKotor** (e.g. main repo’s wiki or GitHub wiki), not th3w1zard1 or a pre-built help.zip at a fixed path.
- **Local run:** Resolve help and wiki from repo root `wiki/` when not frozen.
- **Compile (PyInstaller):** Continue to bundle `wiki/` (e.g. `--include-wiki-if-present` using repo root `wiki/`) so the packaged toolset has help without a separate `help/` folder.

## Why this approach

- Avoids maintaining two copies of docs (toolset/help/wiki vs wiki/).
- contents.xml stays in sync with actual wiki files by being generated from the wiki directory.
- Aligns help source with project home (OpenKotOR/PyKotor) and ensures compile and packaging use the same wiki content.

## Key decisions

- **contents.xml:** Generated at startup (in-memory or temp file) from the resolved wiki base path(s); structure mirrors existing `generate_help_contents.py` but references only wiki filenames (e.g. `Holocron-Toolset-Getting-Started.md`, `Tutorial-Creating-Custom-Robes.md`) and vendor paths.
- **Path resolution:** `help_paths.py` and editor help use only **wiki** (and vendor) bases; remove all `toolset/help` references. Dev: repo root `wiki/` or package `toolset/wiki`; frozen: exe-relative `wiki/`.
- **Help updater:** Change download source to OpenKotOR/PyKotor (URL/artifact to be chosen: e.g. wiki repo tarball or CI-built zip of repo `wiki/`).
- **Build/packaging:** setup.py already copies repo `wiki/` → `src/toolset/wiki`; compile_toolset.ps1 already uses `--include-wiki-if-present` (repo root `wiki/`). No packaging of `help/`.

## Resolved / recommendation

- **Updater source:** Fetch the main repo’s `wiki/` content (e.g. GitHub archive `OpenKotOR/PyKotor` main branch and extract `*/wiki` into the app’s wiki directory, or a CI-built zip of `wiki/` published as a release asset). This keeps one source (repo `wiki/`) for local dev, packaging, and updates. Plan leaves exact URL to implementation (Task 5).

## Next steps

→ Implementation plan: generate contents on startup, remove help folder, switch path resolution and updater, then verify local + compile + tests.
