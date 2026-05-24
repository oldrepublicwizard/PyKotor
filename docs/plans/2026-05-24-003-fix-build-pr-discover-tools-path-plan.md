---
title: "fix: build-pr detect-changes KeyError on tool path"
type: fix
status: completed
date: 2026-05-24
origin: gh-pr-266-detect-changed-tools
strategy_track: test-signal-quality
---

# fix: build-pr detect-changes KeyError on tool path

## Summary

Fix PR Build Validation `detect-changes` job failing with `KeyError: 'path'` when parsing `discover_tools.py` JSON output.

---

## Problem Frame

`Detect Changed Tools` fails after submodule checkout succeeds. Inline Python in `.github/workflows/build-pr.yml` uses `tool["path"]`, but `ToolMetadata.to_dict()` emits `relative_path` (see `tool_metadata.py`), not `path`.

---

## Requirements

- R1. `detect-changes` resolves tool directory via `path`, `relative_path`, or `Tools/{directory}` fallback.
- R2. No change to `ToolMetadata` schema required (workflows already use `.get("path")` elsewhere).
- R3. Libraries-only PR changes still mark all tools affected.

---

## Implementation Units

- U1. Patch `build-pr.yml` detect script: replace `tool["path"]` with resilient path resolution matching `release-ready.yml`.

**Verification:** Local dry-run of discover JSON + path resolution logic; CI `Detect Changed Tools` passes on PR #266.

---

## Sources & References

- CI run 26350791981 job 77568601918
- `tool_metadata.py` `ToolMetadata.to_dict()`
- `release-ready.yml` path fallback pattern
