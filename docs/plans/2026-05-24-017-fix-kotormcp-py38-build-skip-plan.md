---
title: "fix: skip kotormcp py3.8 pr build validation"
type: fix
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# fix: skip KotorMCP Py3.8 PR build validation

## Summary

Plan 016 urllib3 fix is in flight; KotorMCP Windows (Py3.8) fails because `mcp` has no Py3.8 wheels. KotorMCP targets Py3.10+ (ruff py311, classifiers). Expose `min_python` / `validate_py38` in tool metadata and skip incompatible tools in PR Build Validation dry-run matrix.

---

## Requirements

- R1. PR Build Validation on Py3.8 skips tools with `requires-python >= 3.10`.
- R2. KotorMCP `pyproject.toml` declares `requires-python >= 3.10`.
- R3. HolocronToolset and other Py3.8-compatible tools still build on matrix.

---

## Implementation Units

- U1. Parse `requires-python` in `tool_metadata.py`; emit `min_python` and `validate_py38`.
- U2. Pass flags through `build-pr.yml` matrix; skip build step when `validate_py38` is false.
- U3. Update KotorMCP submodule `requires-python`; commit gitlink.

**Verification:** PR #266 Build Validation green on `a67aae1eb` + fix commit.
