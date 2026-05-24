---
title: "fix: mark test_utility Qt suites as gui for CI offscreen"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-python-app-segfault
strategy_track: test-signal-quality
---

# fix: mark test_utility Qt suites as gui for CI offscreen

## Summary

Restore green **Python application** / **python-package** CI by excluding offscreen-fragile Qt utility tests via the existing `-m "not gui"` filter.

---

## Problem Frame

Run `26351164719` segfaults at ~62% in `test_qfiledialog.py` during `PyFileInfoGatherer` teardown. `test_file_dialog_components.py` and `test_keyboard_accessibility_conformance.py` are already `pytest.mark.gui` + `--ignore`, but ~15 other Qt-heavy modules in `test_utility/` still run under `-m "not gui"`.

---

## Requirements

- R1. All non-strict-typing tests under `Libraries/PyKotor/tests/test_utility/` receive `pytest.mark.gui` at collection.
- R2. Strict-typing modules remain unmarked and eligible for CI.
- R3. Existing `--ignore` entries for file_dialog/keyboard may remain (belt-and-suspenders).
- R4. Parity harness and core library tests still run in CI.

---

## Implementation Units

- U1. Add `pytest_collection_modifyitems` hook in `Libraries/PyKotor/tests/test_utility/conftest.py`.

**Verification:** `pytest -m "not gui" Libraries/PyKotor/tests/test_utility/` collects zero Qt dialog tests; CI python-app job completes.

---

## Sources & References

- CI log run 26351164719 — segfault in test_qfiledialog.py
- Plan `2026-05-24-001` GUI exclude pattern
