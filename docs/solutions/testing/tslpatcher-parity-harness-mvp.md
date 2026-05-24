---
title: TSLPatcher Parity Harness MVP
problem_type: testing
component: tslpatcher, parity harness, HoloPatcher, STRATEGY metrics
symptoms: |
  TSLPatcher/HoloPatcher parity gaps (#83 HACKList, #67 namespaces, #59 compiler, #55 RequiredMsg,
  #53 ListIndex) lacked a versioned in-repo corpus mapping GitHub issues to reproducible INI+fixture
  installs with expected byte outcomes. Existing tslpatcher tests were comprehensive but not
  issue-indexed for STRATEGY "install parity" tracking.
root_cause: |
  No manifest-driven harness under Libraries/PyKotor/tests that parametrizes cases from a single
  registry, applies library ConfigReader + ModificationsNCS without HoloPatcher submodule, and
  asserts post-patch NCS bytes. Plans and README existed but learnings were not captured in
  docs/solutions/ for agent prefer/defer/avoid guidance.
solution: |
  Ship Libraries/PyKotor/tests/tslpatcher/parity/ with manifest.json (stdlib JSON), runner.py,
  test_parity_harness.py, and fixtures under patchdata/ (renamed to tslpatchdata/ at runtime to
  avoid root .gitignore on tslpatchdata/). Active cases: issue #83 HACKList u16/u32 typed literals.
  Placeholders skipped for #55, #53; #67/#59 documented in README. Prefer library-first runner;
  defer classic TSLPatcher binary compare and HoloPatcher GUI CI.
prevention: |
  Add new parity cases via manifest.json entries only — avoid runner changes unless assertion types
  expand. Keep INI typed literal syntax as u32:VALUE (e.g. 0x10=u32:12345678), not VALUE:u32.
  Run scoped pytest on parity/ before claiming STRATEGY parity metric progress.
related_docs: |
  Libraries/PyKotor/tests/tslpatcher/parity/README.md,
  docs/plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md,
  STRATEGY.md (TSLPatcher install parity metric),
  .github/workflows/python-package.yml
category: testing
doc_status: current
last_verified: 2026-05-23
---

# TSLPatcher Parity Harness MVP

Issue-indexed parity corpus for TSLPatcher install behavior, tied to STRATEGY **TSLPatcher install parity**.

## Prefer

- **`Libraries/PyKotor/tests/tslpatcher/parity/`** as the canonical regression surface for library install parity.
- **`ConfigReader` + `ModificationsNCS.apply`** in the runner — no HoloPatcher submodule required.
- **`manifest.json`** for case registry (stdlib JSON; no PyYAML in minimal test runs).
- **`patchdata/` in fixtures**, renamed to `tslpatchdata/` at runtime (root `.gitignore` blocks committed `tslpatchdata/` paths).
- **Synthetic NCS fixtures** for new cases until mod redistribution is cleared.

## Defer

- Classic TSLPatcher binary comparison on Windows.
- Headless HoloPatcher GUI wrapper in CI.
- Namespace (#67), compiler (#59), RequiredMsg (#55), ListIndex (#53) cases until fixtures land (manifest placeholders may stay `skip: true`).

## Avoid

- Adding HoloPatcher submodule as a hard dependency for parity tests.
- Using `manifest.yaml` — shipped harness uses JSON (`runner.py` and tests hardcode `manifest.json`).
- INI syntax `VALUE:u32` — engine expects **`u32:VALUE`** (e.g. `0x10=u32:12345678`).

## How to verify

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  Libraries/PyKotor/tests/tslpatcher/parity/test_parity_harness.py -v
```

Expected: all non-skipped manifest cases pass; manifest validation test passes.

## Adding a case

1. Create `fixtures/<name>/patchdata/changes.ini` and source files.
2. Append entry to `manifest.json` with `issue`, `fixture_dir`, `expect`, and optional `assertions`.
3. Re-run verify command above.

See `Libraries/PyKotor/tests/tslpatcher/parity/README.md` for schema examples.

## References

- [Parity harness README](../../../Libraries/PyKotor/tests/tslpatcher/parity/README.md)
- [MVP plan](../../plans/2026-05-23-feat-tslpatcher-parity-harness-mvp-plan.md)
- [STRATEGY.md](../../../STRATEGY.md)
