---
title: KOTOR/TSL Save/Load 1:1 Python from Binary RE
problem_type: logic-errors
component: extract/savedata, MCP (user-agdec-http), reverse engineering
symptoms: |
  No 1:1 Python implementation of K1/TSL save/load; engine order and steps were not
  documented; decompiler unavailable in AgentDecompile MCP so only disassembly was
  available for key functions.
root_cause: |
  PyKotor save/load logic did not follow the exact order of operations used by the
  K1 and TSL binaries. The engine uses a fixed sequence (e.g. disk check -> create
  dir -> screenshot -> SAVENFO/PARTYTABLE/GLOBALVARS/SAVEGAME.sav on save; on load:
  LoadTableInfo -> Load -> LoadModule). Deviating from that order can affect
  compatibility. The fix was to implement dedicated flows that mirror the engine
  step-by-step using reverse-engineering as the source of truth.
solution: |
  Implemented save_load_flow_k1.py and save_load_flow_tsl.py with engine-aligned
  sequence; RE summary in wiki/reverse_engineering_findings.md (Save / Load System);
  tests in test_save_load_flow_k1.py. K1 disk threshold from HasEnoughDiskSpaceForSaveGame:
  K1_MIN_FREE_BYTES_ENGINE = 26_214_400 (~25 MiB). Exhaustive byte-level parity tracked
  in todos/001-pending-p2-exhaustive-1-1-save-load-python-from-agdec.md.
prevention: |
  Update wiki/reverse_engineering_findings.md and flow modules when changing save/load
  behavior; run test_save_load_flow_k1.py. Use flow functions for engine-parity order;
  use SaveFolderEntry for convenience when strict ordering is not required. docs/reva_roadmap/
  is gitignored local RE workspace only.
related_docs: |
  wiki/reverse_engineering_findings.md (Save / Load System), helper_scripts/agdec_save_load/README.md,
  todos/001-pending-p2-exhaustive-1-1-save-load-python-from-agdec.md, .cursorrules,
  .cursor/skills/assembly-transpile-parity/SKILL.md
category: logic-errors
doc_status: partially_stale
last_verified: 2026-05-23
---

# KOTOR/TSL Save/Load 1:1 Python from Binary RE

Reverse-engineered K1 and TSL save/load from game binaries (`k1_win_gog_swkotor.exe`, `k2_win_gog_aspyr_swkotor2.exe`) via AgentDecompile MCP and implemented engine-aligned Python flows in `save_load_flow_k1.py` and `save_load_flow_tsl.py`.

## Status (2026-05-23)

**Sequence-aligned flows landed** — disk checks, directory creation, screenshot timing, and component order match the RE-derived sequence in the flow modules and tests.

**Known gaps** — byte-level golden-SAV verification, full TSL StallEventSaveGame mapping, and exhaustive LoadGame/LoadModule callee documentation remain open; tracked in `todos/001-pending-p2-exhaustive-1-1-save-load-python-from-agdec.md`.

**Dual API by design** — `run_k1_save_flow` / `run_k1_load_flow` (and TSL equivalents) are the engine-parity surface. `SaveFolderEntry.save()` / `load()` use a different order and do not delegate to flow functions; callers needing 1:1 behavior must use the flow modules directly.

**Canonical RE docs** — checked-in summary: `wiki/reverse_engineering_findings.md` (Save / Load System). `docs/reva_roadmap/` is gitignored local agent workspace; not present in a fresh clone.

---

## Root cause

PyKotor's save/load logic did not follow the exact order of operations used by the K1 and TSL binaries. The engine uses a fixed sequence (e.g. disk check -> create dir -> screenshot -> SAVENFO/PARTYTABLE/GLOBALVARS/SAVEGAME.sav on save; on load: LoadTableInfo -> Load -> LoadModule). Deviating from that order can affect compatibility and behavior. The fix was to implement dedicated flows that mirror the engine step-by-step, using reverse-engineering as the source of truth.

---

## Solution

### Single source of truth

- **`wiki/reverse_engineering_findings.md`** (Save / Load System section) — Checked-in K1/TSL save/load RE summary with step order and addresses.
- **Local RE workspace:** `docs/reva_roadmap/` (gitignored) may hold detailed RE reports and caches when present; use `helper_scripts/agdec_save_load/` for the agdec pipeline.

### K1 flow module — `Libraries/PyKotor/src/pykotor/extract/save_load_flow_k1.py`

- **Helpers:** `get_free_disk_space_k1(path)`, `get_directory_size_k1(path)` (GetDirectorySize @ 005e6650), `clean_directory_k1(path)` (CleanDirectory retry path), `create_directory_k1(path)`.
- **Constant:** `K1_MIN_FREE_BYTES_ENGINE = 26_214_400` (~25 MiB), from HasEnoughDiskSpaceForSaveGame @ 004b2520: `(free >> 14) >= 0x640`.
- **Save:** `run_k1_save_flow(entry, *, min_free_bytes=..., required_save_bytes=..., required_max_directory_bytes=..., skip_screenshot_if_path_equal=..., retry_create_after_clean=..., write_components=...)` — (1) free disk + optional [EDI+0x100c8] check, (2) create directory with optional clean+retry on failure, (3) GetDirectorySize vs required_max_directory_bytes, (4–7) path/network/alias (screenshot skip when path matches 0x73d71c), (8–9) write screenshot unless skipped, (10–12) write components in engine order; return 1/0.
- **Load:** `run_k1_load_flow(entry)` — (6) `partytable.load()` (LoadTableInfo @ this+0x1b770), (7) `save_info.load()`, `globals.load()` (Load @ this+0x100fc), (10) `sav.load()` (LoadModule); then read screenshot; return entry.

### TSL flow module — `Libraries/PyKotor/src/pykotor/extract/save_load_flow_tsl.py`

- **Helpers:** `get_free_disk_space_tsl(path)`, `create_directory_tsl(path)`.
- **Save:** `run_tsl_save_flow(entry, ...)` — Same logical order as K1: disk check, create dir, screenshot write, then `save_info.save()`, `partytable.save()`, `globals.save()`, `sav.save()`; return 1/0.
- **Load:** `run_tsl_load_flow(entry)` — `partytable.load()` (LoadTableInfo @ 0x1f0b4), then `save_info.load()`, `globals.load()` (Load @ 0x100fc), then `sav.load()` (LoadModule); then screenshot read; return entry.

### Tests — `Libraries/PyKotor/tests/extract/test_save_load_flow_k1.py`

- Disk space and directory helpers for K1 and TSL; `get_directory_size_k1` (empty/sums), `clean_directory_k1` (empties dir).
- Minimal save flow: return 1 and screenshot file content; skip-screenshot when `skip_screenshot_if_path_equal` matches; return 0 when `required_save_bytes` exceeds free or `required_max_directory_bytes` <= dir size.

### Integration

- **`SaveFolderEntry.save()` / `load()`** — Convenience API with a different load order (`sav → partytable → save_info → globals`) and screenshot written last on save. Does not delegate to flow functions.
- **Flow modules** — Use `run_k1_save_flow` / `run_k1_load_flow` (or TSL equivalents) when engine-parity order and disk gates are required.

---

## How to verify

From repo root:

```bash
uv run pytest Libraries/PyKotor/tests/extract/test_save_load_flow_k1.py -v --timeout=30
```

Expect: All tests in `test_save_load_flow_k1.py` pass (disk helpers, directory helpers, `run_k1_save_flow` and `run_tsl_save_flow` return 1 and write screenshot with minimal fixture). No game install or K1_PATH/K2_PATH required.

---

## Related documentation

- **`.cursorrules`** — Game-engine fidelity rules; mandatory K1+TSL RE via agentdecompile.
- **`wiki/reverse_engineering_findings.md`** — Save / Load System RE summary.
- **`helper_scripts/agdec_save_load/README.md`** — AgentDecompile save/load RE pipeline.
- **`todos/001-pending-p2-exhaustive-1-1-save-load-python-from-agdec.md`** — Remaining exhaustive 1:1 acceptance criteria.
- **`.cursor/skills/assembly-transpile-parity/SKILL.md`** — Decompile/transpile parity workflow.

---

## Prevention and testing

### Best practices

- When changing save/load behavior: update `wiki/reverse_engineering_findings.md` (Save/Load section) and the corresponding flow module (`save_load_flow_k1.py` or `save_load_flow_tsl.py`); run `Libraries/PyKotor/tests/extract/test_save_load_flow_k1.py`. Optional local RE notes under gitignored `docs/reva_roadmap/` may be updated for developer convenience but are not required in fresh clones.

### Avoiding drift

- Treat the **flow functions** as the engine-parity API; do not assume `SaveFolderEntry` matches engine order.
- When 1:1 with the engine is required, call `run_k1_save_flow` / `run_k1_load_flow` (or TSL equivalents) directly instead of `SaveFolderEntry.save()` / `load()`.

### Test cases

- **Existing:** Disk space, directory creation, minimal save flow (screenshot write) for K1 and TSL.
- **Suggested:** Golden SAV roundtrip test (save then load, compare critical fields) when a fixture SAV folder is available.

### When to use flow modules vs SaveFolderEntry.save() / load()

- Use **flow modules** when you need engine-parity order, disk gates, and screenshot timing (tooling, RE validation, 1:1 tests).
- Use **SaveFolderEntry.save()** / **load()** when you only need to read or write save data and strict engine ordering is not required.
- Optional future work: opt-in delegation from `SaveFolderEntry` to flow functions (see `todos/001-…`).
