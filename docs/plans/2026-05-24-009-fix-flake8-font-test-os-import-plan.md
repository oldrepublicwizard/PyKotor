---
title: "fix: add missing os import in font test for flake8"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-python-app-flake8-f821
strategy_track: test-signal-quality
---

# fix: add missing os import in font test for flake8

## Summary

Restore **Python application** CI on `aef29ac3c` by fixing flake8 F821 in the font test module.

---

## Problem Frame

Run `26351757268` fails at **Lint with flake8** before pytest:

```
Libraries/PyKotor/tests/font/test_txi_tga_font.py:58:22: F821 undefined name 'os'
```

Introduced when `@unittest.skipIf(os.name != "nt", ...)` was added without importing `os`.

---

## Requirements

- R1. `Libraries/PyKotor/tests/font/test_txi_tga_font.py` imports `os`.
- R2. flake8 `--select=E9,F63,F7,F82` passes on the file.

---

## Implementation Units

- U1. Add `import os` to `test_txi_tga_font.py`.

**Verification:** `flake8 Libraries/PyKotor/tests/font/test_txi_tga_font.py --select=E9,F63,F7,F82`

---

## Scope Boundaries

- No other lint cleanup in this slice.
