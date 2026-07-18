# PyKotor Tools

This directory holds **standalone applications** built on the [`pykotor`](../../Libraries/PyKotor) library. Each tool is its own installable package (own `pyproject.toml` and usually a `README.md`).

The **PyKotor CLI** (`pykotor` / `pykotorcli`) ships with the library under `Libraries/PyKotor`, not here.

## Relationship to the rest of the repo

- **`Libraries/PyKotor`** — core formats, installation APIs, and the `pykotor` CLI.
- **`Tools/`** — GUIs, patchers, diff utilities, and other entry points that depend on that library.

For workspace layout, install, and `uv` commands, see the repository root [`README.md`](../../README.md) and [`CONTRIBUTING.md`](../../CONTRIBUTING.md). The doc index lists tool-specific pages in [`DOCUMENTATION_INDEX.md`](../../DOCUMENTATION_INDEX.md).

## uv workspace members

The root [`pyproject.toml`](../../pyproject.toml) `[tool.uv.workspace]` `members` list includes:

| Member | Console examples (from root `[project.scripts]`) |
|--------|---------------------------------------------------|
| `Libraries/PyKotor` | `pykotor`, `pykotorcli` |
| `Tools/BatchPatcher` | `batchpatcher`, `batch-patcher` |
| `Tools/HolocronToolset` | `holocrontoolset`, `toolset`, plus standalone `kotor-*-editor` scripts |
| `Tools/HoloPatcher` | `holopatcher`, `holo-patcher` |
| `Tools/HoloPazaak` | `holopazaak`, `holo-pazaak` |
| `Tools/KotorDiff` | `kotordiff`, `kotor-diff` |

**Not** in that workspace list: **`Tools/KotorMCP`** — it is still a normal tool package under this folder (`kotormcp` / `kotor-mcp` scripts in the root meta-package). Install or run it per [`KotorMCP/README.md`](KotorMCP/README.md).

Some clones (for example shallow submodules) may not include every workspace path; if `Tools/BatchPatcher` is missing, sync or clone the full upstream repo.

## Tools in this folder

| Directory | Role |
|-----------|------|
| [**HolocronToolset**](HolocronToolset/) | PyQt/QtPy GUI suite for editing KotOR engine files. |
| [**HoloPatcher**](HoloPatcher/) | Cross-platform TSLPatcher-style mod installer (GUI + CLI). |
| [**HoloPazaak**](HoloPazaak/) | PyQt Pazaak minigame implementation. |
| [**KotorDiff**](KotorDiff/) | CLI for KOTOR-aware diffs and install-oriented workflows. |
| [**KotorMCP**](KotorMCP/) | MCP server for AI clients to inspect K1/TSL installs and resources. |
| **BatchPatcher** | Batch patching workflow (workspace member when present). |

## Developing a tool

Typical patterns from `CONTRIBUTING.md`:

- Sync the full workspace: `CXX=g++ uv sync --all-packages --all-extras` (from the repo root).
- Run with editable library + tool, e.g.  
  `uvx --with-editable Libraries/PyKotor --with-editable Tools/HoloPatcher holopatcher --help`

Tool tests usually live under `Tools/<Tool>/tests/`; library tests under `Libraries/PyKotor/tests/`. See root [`AGENTS.md`](../../AGENTS.md) for pytest flags and Qt/headless notes.

### HolocronToolset UI files

After editing `.ui` files under `Tools/HolocronToolset/src/ui/`, regenerate bindings:

```bash
uv run python Tools/HolocronToolset/src/ui/convertui.py
```

Do not hand-edit generated code under `toolset/uic/`; details are in `AGENTS.md`.

## Upstream

Canonical repository: [oldrepublicwizard/PyKotor](https://github.com/oldrepublicwizard/PyKotor).
