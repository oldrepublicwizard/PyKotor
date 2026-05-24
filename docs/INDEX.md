# PyKotor TSLPatcher Test Suite & Documentation - Complete Index

> **General knowledgebase navigation:** See [`AGENTS.md`](../AGENTS.md) (KB map + canonical pytest) and [`STRATEGY.md`](../STRATEGY.md) (product metrics and tracks). This index covers TSLPatchData docs and tslpatcher tests only.

## 📚 Documentation Files

### For Learning TSLPatchData Generation

1. **[HOW_TSLPATCHDATA_WORKS.md](kotordiff/HOW_TSLPATCHDATA_WORKS.md)** - **START HERE**
   - 60-second summary
   - What goes into tslpatchdata/
   - The four main writers (2DA, GFF, TLK, SSF)
   - The INI file and token system
   - Complete working example
   - File writing rules

2. **[TSLPATCHDATA_GENERATION_EXPLAINED.md](kotordiff/TSLPATCHDATA_GENERATION_EXPLAINED.md)** - Deep Dive
   - Architecture overview
   - Key classes (`IncrementalTSLPatchDataWriter`)
   - Step-by-step file writing process
   - INI generation explained
   - Real-world patterns from actual mods

3. **[TSLPATCHDATA_FLOW_DIAGRAM.md](kotordiff/TSLPATCHDATA_FLOW_DIAGRAM.md)** - Visual Guide
   - Overall data flow diagram
   - Writer type dispatch diagram
   - Internal state machine
   - Modification sequence flowcharts
   - Cross-file reference chains
   - Directory structure visualization

4. **[README_TSLPATCHDATA_DOCS.md](kotordiff/README_TSLPATCHDATA_DOCS.md)** - Navigation
   - Quick links to all docs
   - Big picture overview
   - Key concepts summary
   - Common patterns
   - Code references
   - Troubleshooting guide

### Legacy test-suite overview docs (removed)

The following files were removed from the repo; use [`AGENTS.md`](../AGENTS.md#tests) for running tests and the kotordiff docs above for TSLPatchData concepts:

- `README_COMPREHENSIVE_TESTS.md`, `QUICK_START.md`, `IMPLEMENTATION_SUMMARY.md`, `COMPLETE_OVERVIEW.md`

### Pattern Reference

1. **[example_patterns.py](../Libraries/PyKotor/tests/tslpatcher/example_patterns.py)** - Runnable Pattern Examples
   - 15 TSLPatcher patterns
   - Complete real-world examples (Bastila, dm_qrts)
   - Pattern summary table
   - Can be imported for reference

## 🧪 Test Suite Files

### Main Test Suite

- **[test_diff_comprehensive.py](../Libraries/PyKotor/tests/tslpatcher/diff/test_diff_comprehensive.py)** (1,434 lines)
  - 30+ tests covering all TSLPatcher features
  - 9 test categories:
    - Test2DAMemoryComprehensive (8 tests)
    - TestTLKStrRefComprehensive (5 tests)
    - TestGFFComprehensive (5 tests)
    - TestSSFComprehensive (1 test)
    - TestIntegrationComprehensive (2 tests)
    - TestRealWorldScenarios (2 tests)
    - TestInstallListComprehensive (2 tests)
    - TestEdgeCasesComprehensive (4 tests)
    - TestPerformanceComprehensive (2 tests)
  - TestDataHelper utility class

### Original Test Suite (Kept for Compatibility)

- **[test_diff_2damemory_generation.py](../Libraries/PyKotor/tests/tslpatcher/diff/test_diff_2damemory_generation.py)** (352 lines)
  - Original 3 basic tests
  - Still functional, complementary to new suite

### TSLPatcher parity harness

- **[parity/README.md](../Libraries/PyKotor/tests/tslpatcher/parity/README.md)** — issue-indexed HACKList corpus; see [`STRATEGY.md`](../STRATEGY.md) TSLPatcher install parity metric.

## 🎯 Quick Navigation

### "I want to understand how tslpatchdata works"

-> Read [HOW_TSLPATCHDATA_WORKS.md](kotordiff/HOW_TSLPATCHDATA_WORKS.md)

### "I want to see code explanations"

-> Read [TSLPATCHDATA_GENERATION_EXPLAINED.md](kotordiff/TSLPATCHDATA_GENERATION_EXPLAINED.md)

### "I want visual flowcharts"

-> Read [TSLPATCHDATA_FLOW_DIAGRAM.md](kotordiff/TSLPATCHDATA_FLOW_DIAGRAM.md)

### "I want to run tests"

-> Read [`AGENTS.md`](../AGENTS.md#tests)

### "I want to see code patterns"

-> See [example_patterns.py](../Libraries/PyKotor/tests/tslpatcher/example_patterns.py)

## 📋 Test Execution

```bash
# Canonical scoped run (see AGENTS.md)
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  --ignore=Libraries/PyKotor/tests/resource/formats/test_mdl_ascii.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_file_dialog_components.py \
  Libraries/PyKotor/tests/tslpatcher/diff/test_diff_comprehensive.py -v

# Parity harness smoke
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  Libraries/PyKotor/tests/tslpatcher/parity/test_parity_harness.py -v
```

## 📖 Reading Order (Recommended)

**For understanding TSLPatchData:**

1. [HOW_TSLPATCHDATA_WORKS.md](kotordiff/HOW_TSLPATCHDATA_WORKS.md) - 15 min read
2. [TSLPATCHDATA_FLOW_DIAGRAM.md](kotordiff/TSLPATCHDATA_FLOW_DIAGRAM.md) - 10 min read
3. [TSLPATCHDATA_GENERATION_EXPLAINED.md](kotordiff/TSLPATCHDATA_GENERATION_EXPLAINED.md) - 20 min read
4. [example_patterns.py](../Libraries/PyKotor/tests/tslpatcher/example_patterns.py) - Reference as needed

**For running tests:**

1. [`AGENTS.md`](../AGENTS.md#tests) - canonical command
2. Run a simple test - 2 min

---

**Note:** Line counts and legacy checklist items below may be stale; prefer live paths above and AGENTS.md for current test commands.
