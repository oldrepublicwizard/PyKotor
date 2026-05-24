---
title: "fix: PR #266 CI — orphan submodule and flaky Qt GUI tests"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-ci-failures
strategy_track: test-signal-quality
---

# fix: PR #266 CI — orphan submodule and flaky Qt GUI tests

## Summary

Restore green CI for PR #266 by registering the orphan `vendor/ref-xoreos-tools` gitlink in `.gitmodules` and excluding flaky offscreen Qt keyboard accessibility tests that segfault in GitHub Actions (same class of failure as `test_file_dialog_components.py`).

---

## Problem Frame

CI on PR #266 fails on:

1. **check-default-branch / Detect Changed Tools / build-pr** — `fatal: No url found for submodule path 'vendor/ref-xoreos-tools' in .gitmodules` during recursive checkout.
2. **python-package matrix** — segfault at ~58% in `test_keyboard_accessibility_conformance.py` despite `-m "not gui and not slow"` (file lacks `pytest.mark.gui`).

MSDO Windows Bandit may still fail separately (path-length/timeout); not in this slice unless trivial config exists.

---

## Requirements

- R1. `.gitmodules` includes `vendor/ref-xoreos-tools` with URL resolving gitlink `b2ebf4fb`.
- R2. `test_keyboard_accessibility_conformance.py` marked `pytest.mark.gui`.
- R3. CI workflows and `AGENTS.md` ignore keyboard accessibility test module.
- R4. Scoped pytest passes locally for parity harness path.

---

## Scope Boundaries

- No MSDO Bandit path rewrite unless failure is reproducible and fix is one config line.
- No changes to keyboard test implementation logic.

---

## Implementation Units

- U1. Register `vendor/ref-xoreos-tools` in `.gitmodules` (mirror: `th3w1zard1/xoreos-tools` @ pinned commit).

- U2. Mark keyboard accessibility tests as GUI; add `--ignore` to `python-package.yml`, `python-app.yml`, and `AGENTS.md`.

**Verification:** Submodule sync succeeds; pytest ignore list includes both file_dialog and keyboard modules.

---

## Sources & References

- CI logs: runs 26349937588, 26349938367, 26349938346
- Prior fix: `5fed98936` (ref-tga2tpc + file_dialog ignore)
