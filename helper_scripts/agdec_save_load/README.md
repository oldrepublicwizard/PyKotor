# RE cache + codegen pipeline (save/load)

Proves the **~5 minute** path: load cache -> generate Python -> run tests. Full RE (get-function batch or execute-script) is done once; after that, codegen + verify takes under a minute.

## Quick run

From repo root:

```bash
uv run python helper_scripts/agdec_save_load/run_pipeline.py
```

This reads `docs/reva_roadmap/agdec_cache/k1_save_load_cache.json` (or set `AGDEC_SAVE_LOAD_CACHE` to override), runs codegen (prepends cache provenance to `save_load_flow_k1.py`), and runs pytest on `test_save_load_flow_k1.py`. The cache path is optional local RE workspace — fresh clones may build or copy a cache per [Building the cache](#building-the-cache) below.

## Building the cache

**Option A: get-function (MCP)**  
Call `get-function` for each required save/load entry point and merge the results into one JSON. Save as `docs/reva_roadmap/agdec_cache/k1_save_load_cache.json` with keys: `program`, `program_path`, `source`, `functions` (list of `{address, name, signature, callees}`). The canonical address list now lives in `wiki/reverse_engineering_findings.md`.

**Option B: execute-script (MCP)**  
Run `export_save_load_functions.py` via `execute-script` with `program_path: "/K1/k1_win_gog_swkotor.exe"`. The script assigns to `__result__` a dict with `program` and `functions`. Serialize that to the same JSON path. Note: in some environments `currentProgram` may be the program object directly (not callable).

## Files

| File | Purpose |
|------|--------|
| `run_pipeline.py` | Entry: load cache, codegen, verify (pytest) |
| `k1_save_load_addresses.json` | Static address list / fallback summary |
| `export_save_load_functions.py` | Ghidra Python script for batch export via execute-script |
| `README.md` | This file |

## Options

- `--cache path` — Use a different cache JSON.
- `--codegen` — Only run codegen (no pytest).
- `--verify` — Only run pytest (no codegen).
- `--output path` — Write codegen output to this path (default: `save_load_flow_k1.py`).

## See also

- `docs/brainstorms/2026-03-12-agdec-re-to-python-5min-brainstorm.md`
- `docs/reva_roadmap/SAVE_LOAD_ENGINE_BEHAVIOR.md`
- `.cursor/skills/assembly-transpile-parity/SKILL.md`
