---
title: TSLPatcher Parity Harness MVP (HACKList corpus + runner)
status: completed
date: 2026-05-23
origin: docs/ideation/2026-05-23-pykotor-strategy-aligned-ideation.md
strategy_track: End-to-end mod workflow
issues: [83, 67, 59, 55, 53]
---

# TSLPatcher Parity Harness MVP

## Problem frame

PyKotor's HoloPatcher/TSLPatcher engine (`pykotor/tslpatcher/`) has open parity gaps (#83 HACKList, #67 namespaces, #59 compiler, #55 RequiredMsg, #53 ListIndex). Existing tests cover reader/mods/diff comprehensively but lack a **versioned parity corpus** that maps GitHub issues to reproducible INI+fixture installs with expected outcomes.

STRATEGY metric: **TSLPatcher install parity** — mods install identically to classic TSLPatcher.

## Scope boundary

**In scope (this slice):**

- Parity harness **scaffold**: manifest format, runner helper, pytest integration
- First corpus entry: **[HACKList]** synthetic case (issue #83) with minimal NCS fixture
- Documentation for adding future corpus cases tied to issue numbers
- CI-runnable tests under `Libraries/PyKotor/tests` (no game install required)

**Out of scope (deferred):**

- Full real-mod corpus redistribution
- Headless HoloPatcher GUI CLI wrapper in CI
- Namespace/RequiredMsg/ListIndex/compiler cases (manifest slots only, tests in follow-up)
- Classic TSLPatcher binary comparison on Windows

## Requirements traceability

| ID | Requirement | Source |
|----|-------------|--------|
| R1 | Manifest lists parity cases with issue ref, INI path, expected pass/fail | Ideation #1 |
| R2 | Runner loads INI via `ConfigReader`, applies NCS HACKList patches in temp dir | Issue #83 |
| R3 | Parametrized pytest executes all manifest cases | Test consolidation plan TSLPatcher priority |
| R4 | README explains how to add cases without code changes to runner | Agent-native discoverability |

## Decisions

1. **Library-first runner** — Use `PatcherConfig` + `ModificationsNCS.apply` directly; no HoloPatcher submodule dependency (empty in many clones).
2. **Synthetic fixtures** — Minimal NCS byte buffers in-repo; no copyrighted mod assets.
3. **JSON manifest** — Human-editable; one file `manifest.json` co-located with fixtures (stdlib `json`; no PyYAML dependency).
4. **pytest parametrize** — Single test module discovers cases at collection time.

## Implementation units

### IU-1: Parity manifest schema and HACKList fixture

**Files:**

- `Libraries/PyKotor/tests/tslpatcher/parity/manifest.json`
- `Libraries/PyKotor/tests/tslpatcher/parity/fixtures/hacklist_uint32/changes.ini`
- `Libraries/PyKotor/tests/tslpatcher/parity/fixtures/hacklist_uint32/patchdata/test.ncs` (renamed to `tslpatchdata/` at runtime; root `.gitignore` blocks committed `tslpatchdata/` paths)

**Test scenarios:**

- Manifest parses without error
- HACKList fixture INI loads via `ConfigReader`
- At least one NCS modifier is created

### IU-2: Parity runner module

**Files:**

- `Libraries/PyKotor/tests/tslpatcher/parity/runner.py`

**Behavior:**

- `load_manifest(path) -> list[ParityCase]`
- `run_case(case, tmp_path) -> ParityResult` — copies fixture, reads INI, runs NCS patch apply, checks byte assertions

**Test scenarios:**

- `run_case` on HACKList fixture returns pass
- Missing fixture dir raises clear error

### IU-3: Pytest harness

**Files:**

- `Libraries/PyKotor/tests/tslpatcher/parity/test_parity_harness.py`

**Test scenarios:**

- All non-skipped manifest cases pass in CI scope
- Collection finds at least one case

### IU-4: Documentation

**Files:**

- `Libraries/PyKotor/tests/tslpatcher/parity/README.md`

## Verification

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 Libraries/PyKotor/tests/tslpatcher/parity/test_parity_harness.py -v
```

## Risks

| Risk | Mitigation |
|------|------------|
| NCS fixture too synthetic | Document follow-up for issue-derived cases |
| Manifest assertion types proliferate | Start with `ncs_bytes_at_offset` only |

## Deferred to implementation

- Exact minimal NCS bytes and expected post-patch hex (resolve from `mods/ncs.py` apply behavior)
