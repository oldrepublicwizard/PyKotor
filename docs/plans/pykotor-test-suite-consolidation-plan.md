# PyKotor Test Suite Consolidation Plan

## Scope

This plan audits the test suite under `Libraries/PyKotor/tests` with two goals:

1. keep the tests that catch meaningful regressions in public behavior, file-format fidelity, and end-to-end workflows;
2. reduce noise from duplicate, brittle, skipped, overly granular, or expensive tests that mostly validate implementation detail.

The inventory appendix at the end names every collected test symbol discovered from `test_*.py` files so no test is omitted from the planning surface.

## What Matters

Prioritize these categories:

- format round-trip and corruption handling for stable resource formats;
- integration tests that exercise CLI workflows, TSLPatcher behavior, and installation/resource discovery;
- public API behavior for common utilities, path handling, stream handling, and model helpers;
- UI functional behavior such as file selection, navigation, signals, keyboard access, and task execution.

De-prioritize these categories:

- exact pixel sizes, exact Fluent color values, and OS-theme rendering details;
- trivial wrappers around Python builtins when dozens of nearly identical tests say the same thing;
- tests that are permanently skipped, unfinished, or known broken;
- duplicate internal-helper tests that are already covered through higher-value CLI or integration coverage.

## Executive Summary

The suite currently collects about 2599 tests across 115 test modules. The biggest problems are concentration and duplication rather than total count alone.

The highest-value areas are:

- `resource/formats/test_ncs.py`, `resource/formats/test_bwm.py`, `resource/formats/test_mdl_ascii.py`, `resource/formats/test_wav.py`
- `resource/generics/test_dlg.py` and the better generic round-trip tests
- CLI workflow coverage in `cli/test_json_commands.py`, `cli/test_walkmesh_rebuild.py`, `cli/test_indoor_roundtrip.py`
- TSLPatcher integration in `tslpatcher/test_mods.py`, `tslpatcher/test_reader.py`, `tslpatcher/test_tslpatcher.py`
- filesystem/task/dialog behavior in `test_utility/test_qfiledialog.py`, `test_utility/test_qfiledialog2.py`, `test_utility/test_filesystem_components.py`, `test_utility/test_pyfileinfogatherer.py`, `test_utility/test_tasks.py`

The lowest-value areas are:

- pixel-perfect and exact visual conformance tests
- duplicate or hidden duplicate diff tests
- permanently skipped or unfinished path/config tests
- ultra-granular wrapper-string tests that mostly restate stdlib behavior
- repeated binary/xml/json/file-io permutations written as separate tests instead of parametrized variants

## Priority Decisions By Area

### Top-Level and Common

- Keep `test_compile_tool.py`, `resource/test_replace_module_extensions.py`, and `resource/test_resource_from_path.py`.
- Keep `test_markdown_validation.py`, but treat it as a documentation integrity suite, not product behavior.
- Rename or move `test_kaitai_generated_parity.py` into an integrity/lint bucket unless true parser parity checks are added.
- Consolidate `common/test_wrapped_str.py` and `common/test_wrapped_str2.py` into one focused behavior file.
- Reduce `common/test_path_mixed_slash_handling.py` to representative cross-platform cases instead of exhaustive slash permutations.
- Keep `common/test_decode_fallbacks.py`, `common/test_geometry.py`, `common/test_stream.py`, and the stronger `CaseAwarePath`/glob tests.
- Review and either finish or remove explicitly unfinished path tests in `common/test_get_case_sensitive_path.py`.

### Extract, Font, GL, and Engine

- Keep the extract suite because it covers real resource-loading workflows, but mark game-installation dependent tests as integration-only.
- Keep `font/test_txi_tga_font.py`, but leave it outside the fast default suite because it depends on real fonts and file output.
- Keep `gl/test_texture_loader_core.py`, `gl/test_camera_controller.py`, `gl/test_frustum_culling.py`, `gl/test_mdl_mesh_alpha_modes.py`, and `gl/test_async_loader_texture_txi_none.py` if they validate public rendering logic.
- Keep `gl/test_gl_accel.py` as an optional compiled-extension check only.
- Consolidate overly mocked GL tests if they only assert exact internal OpenGL calls instead of stable behavior.
- Consolidate simple constructor-style engine checks in `test_engine/test_mdl_loader.py`; keep the math-heavy behavior tests.

### Resource Format Tests

- Keep the format suites for BIF, BWM, DDS, ERF, GFF, KEY, LIP, LYT, MDL, MDL ASCII, NCS, RIM, SSF, TLK, TPC, TwoDA, TXI I/O, VIS, WAV, and WOK.
- Convert repeated `binary_io`, `xml_io`, `json_io`, and `file_io` variants into parametrized tests where the assertions are materially the same.
- Keep `test_model_parsers_against_mdlops.py`, but move it into a very-slow integration bucket because it depends on external tooling and real models.
- Keep installation-wide conversion/compile suites only as explicitly slow, opt-in suites.
- Remove or merge ultra-narrow tests such as `test_gff_list_compare.py` when the same regression can live in the main format test file.
- Expand `test_txi_data.py` or merge it into broader TXI coverage; as written it is too narrow to justify its own file.

### Resource Generic Tests

- Keep `test_dlg.py` as a dedicated complex-graph test file.
- Consolidate the UT* generic files (`utc`, `utd`, `ute`, `uti`, `utp`, `uts`, `utt`, `utw`) into a parametrized template-oriented suite where possible.
- Group smaller minimal generics such as `are`, `ifo`, `jrl`, and `pth` into shared minimal round-trip coverage if they do not justify separate modules.
- Keep files with distinct logic such as `test_git.py`, `test_gui.py`, and `test_fac.py`.
- Remove or fix known-broken generic tests rather than leaving them permanently skipped.

### CLI

- Keep `cli/test_cli_backwards_compat.py`.
- Keep `cli/test_json_commands.py`, `cli/test_walkmesh_rebuild.py`, and `cli/test_indoor_roundtrip.py`.
- Keep `cli/test_indoor_extract_installation_modules.py` only as a slow integration suite.
- Consolidate `cli/test_diff_command.py` and `cli/test_diff_comprehensive.py`; there is redundant coverage and evidence of duplicated class definitions that likely hide tests.
- Move tests of private diff helper functions into a clearly labeled internal-only module or remove them if CLI-path coverage already exercises the same behavior.

### TSLPatcher

- Keep `tslpatcher/test_mods.py`, `tslpatcher/test_reader.py`, and `tslpatcher/test_tslpatcher.py`; they are the core behavior suites.
- Reduce repetition in `tslpatcher/test_reader.py` by parametrizing the many near-identical 2DA row-operation variants.
- Split or reduce `tslpatcher/test_config.py`; fix or delete the broken skipped tests instead of carrying them indefinitely.
- Keep `tslpatcher/diff/test_diff_comprehensive.py`, `test_diff_tslpatcher.py`, `test_diff_2damemory_generation.py`, and `test_twoda.py` if they cover unique patch-generation behavior.
- The `test_gff.py`, `test_ssf.py`, and `test_tlk.py` placeholders under `tslpatcher/diff` currently collect zero tests and should either gain real coverage or be removed.
- Keep `tslpatcher/diff/test_full_execution.py` only as optional integration coverage.

### Utility and UI

- Keep the functional UI suites: `test_qfiledialog.py`, `test_qfiledialog2.py`, `test_qfiledialogextended.py`, `test_filesystem_components.py`, `test_file_dialog_components.py`, `test_pyfileinfogatherer.py`, `test_dynamic_view.py`, `test_tasks.py`, `test_actions_dispatcher.py`.
- Consolidate `test_qfiledialogextended_comprehensive.py` into the main extended-dialog suite unless it contains materially different behavior coverage.
- Remove `test_pixel_perfect_layout.py` and `test_fluent_design_conformance.py` from the default plan; they mostly test visual constants and are too brittle for their value.
- Consolidate `test_windows_file_dialog_conformance.py`, `test_windows_explorer_conformance.py`, `test_visual_layout_conformance.py`, and `test_explorer_widget_components.py` into a smaller behavioral suite focused on navigation, selection, shortcuts, and widget structure.
- Keep `test_keyboard_accessibility_conformance.py`, but move vague visual-only checks to semantic focus and shortcut assertions.
- Keep the strict-typing micro-tests only if they encode repo policy; otherwise merge them into a smaller policy suite.

## Recommended Target Layout

A more manageable suite would look like this:

- `tests/fast/format/` for stable codec and public API coverage
- `tests/fast/common/` for utilities and path/stream behavior
- `tests/fast/ui/` for dialog/explorer/tasks behavior without pixel fidelity checks
- `tests/integration/cli/` for CLI workflow tests
- `tests/integration/tslpatcher/` for patcher end-to-end behavior
- `tests/slow/` for installation-wide, mdlops, font-generation, and full-game conversion/compiler sweeps

This does not require immediate file movement; the same outcome can start with markers and consolidation inside the current tree.

## Concrete Consolidation Actions

1. Delete or quarantine low-value visual-conformance files:
   - `test_utility/test_pixel_perfect_layout.py`
   - `test_utility/test_fluent_design_conformance.py`
2. Merge overlapping Windows UI conformance coverage into behavior-first suites:
   - `test_windows_file_dialog_conformance.py`
   - `test_windows_explorer_conformance.py`
   - `test_visual_layout_conformance.py`
   - `test_explorer_widget_components.py`
3. Collapse repeated wrapper-string tests into one focused behavior suite:
   - `common/test_wrapped_str.py`
   - `common/test_wrapped_str2.py`
   - keep the truly distinct case-insensitive behavior tests
4. Parametrize repetitive format tests instead of maintaining separate `binary/xml/json/file` clones.
5. Parametrize repetitive TSLPatcher 2DA operation variants.
6. Fix or remove permanently skipped tests in:
   - `tslpatcher/test_config.py`
   - `common/test_get_case_sensitive_path.py`
   - `test_utility/test_qfiledialog2.py`
   - `resource/generics/test_utd.py`
7. Mark and isolate expensive suites:
   - installation-wide compile/convert tests
   - `resource/formats/test_model_parsers_against_mdlops.py`
   - `cli/test_indoor_extract_installation_modules.py`
   - heavy font/GL tests if runtime proves material
8. Remove zero-test placeholder modules in `tslpatcher/diff` if they remain empty.

## Expected Outcome

If executed well, this plan should:

- preserve nearly all real regression-detection power;
- cut substantial maintenance overhead in UI tests;
- reduce default runtime by moving install-wide and tool-dependent tests out of the fast path;
- make failures easier to interpret because each remaining test will map more clearly to a behavior the project actually cares about.

## Module-by-Module Disposition

This section turns the summary into explicit per-module actions.

Status meanings:

- `keep`: keep in the fast or standard suite with only minor cleanup.
- `keep-slow`: keep, but move behind a slow or opt-in marker.
- `consolidate`: keep the behavior coverage, but merge, parametrize, or shrink the current file.
- `fix-then-keep`: repair broken, skipped, or duplicate structure before keeping it.
- `remove-or-merge`: delete the file as a standalone suite or merge its assertions into a stronger neighboring suite.
- `policy-only`: keep only if the repository explicitly wants coding-policy enforcement at runtime; otherwise merge into a smaller policy suite.

### Top-Level and Resource Root

- `Libraries/PyKotor/tests/test_compile_tool.py`: `keep` — compact, practical coverage for build-helper behavior.
- `Libraries/PyKotor/tests/test_engine/test_mdl_loader.py`: `consolidate` — keep the geometry and hierarchy behavior, trim constructor-style checks that duplicate richer model suites.
- `Libraries/PyKotor/tests/test_finder.py`: `consolidate` — keep the resource-finding contract, but drop trivial static-order assertions unless paired with real search scenarios.
- `Libraries/PyKotor/tests/test_kaitai_generated_parity.py`: `remove-or-merge` — better treated as vendor integrity or lint coverage unless true parser parity is added.
- `Libraries/PyKotor/tests/test_markdown_validation.py`: `keep` — useful documentation integrity guardrail.
- `Libraries/PyKotor/tests/resource/test_replace_module_extensions.py`: `keep` — strong edge-case coverage for important module-name normalization.
- `Libraries/PyKotor/tests/resource/test_resource_from_path.py`: `keep` — high-value coverage for resource typing and path parsing.

### Common

- `Libraries/PyKotor/tests/common/test_case_aware_path.py`: `keep` — useful public-path behavior coverage; trim helper-internal assertions if they block refactors.
- `Libraries/PyKotor/tests/common/test_caseawarepath_globber_bug.py`: `keep` — regression-focused and tied to real filesystem behavior.
- `Libraries/PyKotor/tests/common/test_consumer_manager.py`: `keep` — meaningful async/task lifecycle coverage.
- `Libraries/PyKotor/tests/common/test_decode_fallbacks.py`: `keep` — practical encoding fallback coverage with real failure modes.
- `Libraries/PyKotor/tests/common/test_geometry.py`: `keep` — compact math and geometry behavior suite with clear value.
- `Libraries/PyKotor/tests/common/test_get_case_sensitive_path.py`: `fix-then-keep` — retain the core filesystem behavior, but remove or complete explicitly unfinished cases.
- `Libraries/PyKotor/tests/common/test_path_isinstance.py`: `consolidate` — keep one representative cross-platform inheritance matrix instead of many near-identical platform permutations.
- `Libraries/PyKotor/tests/common/test_path_mixed_slash_handling.py`: `consolidate` — reduce the exhaustive slash/permutation matrix to representative contract-level cases.
- `Libraries/PyKotor/tests/common/test_stream.py`: `keep` — strong low-level stream behavior coverage.
- `Libraries/PyKotor/tests/common/test_wrapped_case_insens_str.py`: `consolidate` — keep truly distinct case-insensitive behavior, trim builtin-wrapper exhaustiveness.
- `Libraries/PyKotor/tests/common/test_wrapped_str.py`: `consolidate` — merge with `test_wrapped_str2.py` and keep only contract-level behavior.
- `Libraries/PyKotor/tests/common/test_wrapped_str2.py`: `remove-or-merge` — fold into `test_wrapped_str.py`.

### Extract

- `Libraries/PyKotor/tests/extract/test_capsule.py`: `keep` — small but meaningful container behavior coverage.
- `Libraries/PyKotor/tests/extract/test_chitin.py`: `keep-slow` — useful integration test, but installation-dependent.
- `Libraries/PyKotor/tests/extract/test_installation.py`: `keep` — important installation/resource access behavior.
- `Libraries/PyKotor/tests/extract/test_nested_capsule.py`: `keep` — real nested-container behavior that is hard to replace with simpler tests.
- `Libraries/PyKotor/tests/extract/test_save_load_flow_k1.py`: `keep` — workflow-level behavior with concrete filesystem outcomes.
- `Libraries/PyKotor/tests/extract/test_talktable.py`: `keep` — small, cheap, and still behaviorally useful.

### Font and GL

- `Libraries/PyKotor/tests/font/test_txi_tga_font.py`: `keep-slow` — keep, but not in the default fast path because it depends on fonts and output assets.
- `Libraries/PyKotor/tests/gl/test_async_loader_texture_txi_none.py`: `keep` — small regression coverage with direct rendering value.
- `Libraries/PyKotor/tests/gl/test_camera_controller.py`: `keep` — strong user-facing camera behavior suite.
- `Libraries/PyKotor/tests/gl/test_frustum_culling.py`: `keep` — high-value visibility and caching behavior coverage.
- `Libraries/PyKotor/tests/gl/test_gl_accel.py`: `keep-slow` — keep as optional compiled-extension validation only.
- `Libraries/PyKotor/tests/gl/test_mdl_mesh_alpha_modes.py`: `consolidate` — keep alpha-mode behavior but reduce exact internal GL-call coupling where possible.
- `Libraries/PyKotor/tests/gl/test_texture_loader_core.py`: `keep` — compact, meaningful serialization and queue behavior coverage.

### Resource Formats

- `Libraries/PyKotor/tests/resource/formats/ncs/test_do_types_strict_typing.py`: `policy-only` — keep only if runtime policy tests are an intentional repo standard.
- `Libraries/PyKotor/tests/resource/formats/test_base_comparable_strict_typing.py`: `policy-only` — merge with other policy tests if retained at all.
- `Libraries/PyKotor/tests/resource/formats/test_bif.py`: `keep` — useful container/index coverage.
- `Libraries/PyKotor/tests/resource/formats/test_bwm.py`: `keep` — one of the strongest format suites in the repository.
- `Libraries/PyKotor/tests/resource/formats/test_dds.py`: `keep` — practical texture codec coverage.
- `Libraries/PyKotor/tests/resource/formats/test_erf.py`: `consolidate` — keep behavior, parametrize repeated I/O forms.
- `Libraries/PyKotor/tests/resource/formats/test_gff.py`: `consolidate` — keep, but merge repetitive binary/XML/file variants.
- `Libraries/PyKotor/tests/resource/formats/test_gff_list_compare.py`: `remove-or-merge` — merge the regression into `test_gff.py` instead of keeping a single-assert file.
- `Libraries/PyKotor/tests/resource/formats/test_key.py`: `keep` — still important for archive index behavior.
- `Libraries/PyKotor/tests/resource/formats/test_lip.py`: `consolidate` — keep behavior, reduce repeated format-shape duplication.
- `Libraries/PyKotor/tests/resource/formats/test_lyt.py`: `keep` — small but useful layout parsing coverage.
- `Libraries/PyKotor/tests/resource/formats/test_mdl.py`: `consolidate` — merge overlapping round-trip and structure checks with the stronger MDL ASCII and loader suites.
- `Libraries/PyKotor/tests/resource/formats/test_mdl_ascii.py`: `keep-slow` — preserve, but split by feature or marker because it is a major, expensive suite.
- `Libraries/PyKotor/tests/resource/formats/test_model_parsers_against_mdlops.py`: `keep-slow` — valuable reference-tool comparison, but strictly opt-in.
- `Libraries/PyKotor/tests/resource/formats/test_ncs.py`: `keep` — critical compiler/runtime coverage.
- `Libraries/PyKotor/tests/resource/formats/test_rim.py`: `consolidate` — keep behavior, reduce repeated binary/file variants.
- `Libraries/PyKotor/tests/resource/formats/test_ssf.py`: `consolidate` — keep behavior, parametrize binary/XML/JSON variants.
- `Libraries/PyKotor/tests/resource/formats/test_tlk.py`: `consolidate` — keep behavior, parametrize binary/XML/JSON variants.
- `Libraries/PyKotor/tests/resource/formats/test_tpc.py`: `keep` — meaningful texture behavior coverage.
- `Libraries/PyKotor/tests/resource/formats/test_twoda.py`: `consolidate` — keep behavior, parametrize binary/CSV/JSON variants.
- `Libraries/PyKotor/tests/resource/formats/test_txi_data.py`: `remove-or-merge` — too narrow as a standalone suite; merge into broader TXI coverage or expand substantially.
- `Libraries/PyKotor/tests/resource/formats/test_txi_io.py`: `keep` — compact and directly useful.
- `Libraries/PyKotor/tests/resource/formats/test_utm.py`: `remove-or-merge` — fold into a parametrized UT* generic suite.
- `Libraries/PyKotor/tests/resource/formats/test_vis.py`: `keep` — low-cost behavior coverage.
- `Libraries/PyKotor/tests/resource/formats/test_wav.py`: `keep` — broad, practical audio coverage.
- `Libraries/PyKotor/tests/resource/formats/test_wok.py`: `keep` — useful walkmesh file coverage; merge only if runtime pressure makes the overlap with `test_bwm.py` unjustified.

### Resource Generics

- `Libraries/PyKotor/tests/resource/generics/test_are.py`: `consolidate` — move into a minimal-generics group unless richer area-specific behavior is added.
- `Libraries/PyKotor/tests/resource/generics/test_dlg.py`: `keep` — complex graph behavior fully justifies a dedicated suite.
- `Libraries/PyKotor/tests/resource/generics/test_dlg_twine.py`: `keep` — distinct feature surface with genuine behavior coverage.
- `Libraries/PyKotor/tests/resource/generics/test_fac.py`: `keep` — sufficiently distinct and not overly large.
- `Libraries/PyKotor/tests/resource/generics/test_git.py`: `keep` — meaningful area-instance serialization coverage.
- `Libraries/PyKotor/tests/resource/generics/test_gui.py`: `keep` — compact and distinct GUI resource behavior.
- `Libraries/PyKotor/tests/resource/generics/test_ifo.py`: `consolidate` — group with other minimal generics unless more module-specific behavior is added.
- `Libraries/PyKotor/tests/resource/generics/test_jrl.py`: `consolidate` — group with other minimal generics unless deeper journal behavior is added.
- `Libraries/PyKotor/tests/resource/generics/test_pth.py`: `consolidate` — group with other minimal generics unless path-specific behavior is expanded.
- `Libraries/PyKotor/tests/resource/generics/test_utc.py`: `keep` — keep as the richest UT* anchor if one dedicated UT suite remains.
- `Libraries/PyKotor/tests/resource/generics/test_utd.py`: `fix-then-keep` — repair the known broken case, then fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_ute.py`: `consolidate` — fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_uti.py`: `consolidate` — fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_utp.py`: `consolidate` — fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_uts.py`: `consolidate` — fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_utt.py`: `consolidate` — fold into a parametrized UT* suite.
- `Libraries/PyKotor/tests/resource/generics/test_utw.py`: `consolidate` — fold into a parametrized UT* suite.

### CLI

- `Libraries/PyKotor/tests/cli/test_cli_backwards_compat.py`: `keep` — tiny but high-signal CLI contract suite.
- `Libraries/PyKotor/tests/cli/test_diff_command.py`: `fix-then-keep` — remove duplicate/hidden structure, then keep the best CLI-path behavior checks.
- `Libraries/PyKotor/tests/cli/test_diff_comprehensive.py`: `consolidate` — merge the real coverage into `test_diff_command.py` and delete duplicative or aspirational cases.
- `Libraries/PyKotor/tests/cli/test_indoor_extract_installation_modules.py`: `keep-slow` — strong integration value, but not for the default suite.
- `Libraries/PyKotor/tests/cli/test_indoor_roundtrip.py`: `keep-slow` — high-value end-to-end workflow coverage; keep behind a slow marker.
- `Libraries/PyKotor/tests/cli/test_json_commands.py`: `keep` — focused feature-level CLI coverage.
- `Libraries/PyKotor/tests/cli/test_walkmesh_rebuild.py`: `keep` — good workflow and invariant coverage.

### Utility and UI

- `Libraries/PyKotor/tests/test_utility/test_actions_dispatcher.py`: `keep` — retain, but tighten any vague or non-behavioral assertions.
- `Libraries/PyKotor/tests/test_utility/test_actions_executor_strict_typing.py`: `policy-only` — merge with the other strict-typing policy tests if retained.
- `Libraries/PyKotor/tests/test_utility/test_drag_drop_conformance.py`: `consolidate` — keep real drag/drop behavior, merge into dialog or explorer behavior suites.
- `Libraries/PyKotor/tests/test_utility/test_dynamic_view.py`: `keep` — strong component behavior suite.
- `Libraries/PyKotor/tests/test_utility/test_explorer_widget_components.py`: `consolidate` — merge with explorer behavior suites to avoid widget-existence duplication.
- `Libraries/PyKotor/tests/test_utility/test_file_dialog_components.py`: `keep` — useful component behavior coverage.
- `Libraries/PyKotor/tests/test_utility/test_filesystem_components.py`: `keep` — one of the better utility suites; high behavior-to-maintenance ratio.
- `Libraries/PyKotor/tests/test_utility/test_fluent_design_conformance.py`: `remove-or-merge` — remove as a standalone suite; exact visual constants are too brittle.
- `Libraries/PyKotor/tests/test_utility/test_keyboard_accessibility_conformance.py`: `keep` — retain keyboard and accessibility behavior, but trim vague visual-only checks.
- `Libraries/PyKotor/tests/test_utility/test_mutable_str_strict_typing.py`: `policy-only` — merge with the strict-typing policy bucket if retained.
- `Libraries/PyKotor/tests/test_utility/test_pixel_perfect_layout.py`: `remove-or-merge` — remove as a standalone suite; exact pixel checks are low-value and fragile.
- `Libraries/PyKotor/tests/test_utility/test_pyfileinfogatherer.py`: `keep` — focused, practical filesystem infrastructure coverage.
- `Libraries/PyKotor/tests/test_utility/test_qfiledialog.py`: `keep` — primary dialog behavior suite.
- `Libraries/PyKotor/tests/test_utility/test_qfiledialog2.py`: `fix-then-keep` — keep the valid regression coverage, but isolate or remove permanently crashing/skipped cases.
- `Libraries/PyKotor/tests/test_utility/test_qfiledialogextended.py`: `keep` — useful extension-specific behavior coverage.
- `Libraries/PyKotor/tests/test_utility/test_qfiledialogextended_comprehensive.py`: `consolidate` — merge distinct behavior into `test_qfiledialogextended.py` and `test_qfiledialog.py`.
- `Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py`: `policy-only` — merge with the strict-typing policy bucket if retained.
- `Libraries/PyKotor/tests/test_utility/test_string_util_strict_typing.py`: `policy-only` — merge with the strict-typing policy bucket if retained.
- `Libraries/PyKotor/tests/test_utility/test_sys_attributes_strict_typing.py`: `policy-only` — merge with the strict-typing policy bucket if retained.
- `Libraries/PyKotor/tests/test_utility/test_tasks.py`: `keep` — good async/task execution coverage.
- `Libraries/PyKotor/tests/test_utility/test_visual_layout_conformance.py`: `consolidate` — keep structural hierarchy checks, drop layout/pixel fidelity assertions.
- `Libraries/PyKotor/tests/test_utility/test_windows_explorer_conformance.py`: `consolidate` — merge behavioral explorer checks into slimmer explorer suites.
- `Libraries/PyKotor/tests/test_utility/test_windows_file_dialog_conformance.py`: `consolidate` — merge behavioral dialog checks into slimmer dialog suites.

### TSLPatcher

- `Libraries/PyKotor/tests/tslpatcher/diff/test_diff_2damemory_generation.py`: `keep` — focused and distinct token-generation behavior.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_diff_comprehensive.py`: `keep-slow` — preserve the broad diff-generation scenarios, but move heavier cases out of the fast lane if runtime demands it.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_diff_tslpatcher.py`: `keep` — useful bridge between diff generation and patcher output.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_full_execution.py`: `keep-slow` — end-to-end execution value is real, but it should be opt-in.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_twoda.py`: `keep` — small, distinct, and practical vendor-diff behavior.
- `Libraries/PyKotor/tests/tslpatcher/mods/test_vendor_twoda_mods.py`: `keep` — compact and directly tied to vendor behavior parity.
- `Libraries/PyKotor/tests/tslpatcher/test_config.py`: `fix-then-keep` — remove skipped broken cases or repair them, then keep only the configuration behaviors that still matter.
- `Libraries/PyKotor/tests/tslpatcher/test_mods.py`: `keep` — core patch-application behavior suite.
- `Libraries/PyKotor/tests/tslpatcher/test_reader.py`: `consolidate` — preserve behavior, but parametrize the many near-identical 2DA and config-reader variants.
- `Libraries/PyKotor/tests/tslpatcher/test_tslpatcher.py`: `keep` — primary integration suite, though it may eventually be split for readability.

### Non-Inventory but In-Scope Follow-Up Files

These files do not appear in the `test_*.py` inventory appendix, but they are part of the test-plan surface and should be handled explicitly.

- `Libraries/PyKotor/tests/resource/formats/pytest_ncs_compile_installation.py`: `keep-slow` — retain only as an explicit installation-wide compiler sweep.
- `Libraries/PyKotor/tests/resource/formats/pytest_gff_convert_installations.py`: `keep-slow` — retain only as an explicit installation-wide conversion sweep.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_gff.py`: `fix-then-keep` or remove — currently zero collected tests; either add real tests or delete the placeholder.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_ssf.py`: `fix-then-keep` or remove — currently zero collected tests; either add real tests or delete the placeholder.
- `Libraries/PyKotor/tests/tslpatcher/diff/test_tlk.py`: `fix-then-keep` or remove — currently zero collected tests; either add real tests or delete the placeholder.

## Execution Sequence

1. Remove or quarantine the brittle visual-conformance files and the zero-test placeholders.
2. Fix known broken or unfinished suites so the remaining baseline is trustworthy.
3. Consolidate repeated wrapper, generic UT*, diff, and UI-conformance suites into behavior-first modules.
4. Parametrize repeated format and TSLPatcher variants to preserve coverage while cutting maintenance cost.
5. Move install-wide, external-tool, and full-workflow suites behind explicit slow markers.
6. Re-run collection and compare the resulting file/module/test counts to this document before doing any deeper deletions.

## Implementation Progress

- Completed tranche 1:
   - consolidated `Libraries/PyKotor/tests/common/test_wrapped_str.py` from exhaustive builtin-proxy checks into a smaller contract-focused suite;
   - removed `Libraries/PyKotor/tests/common/test_wrapped_str2.py` because it duplicated coverage already present in `test_wrapped_case_insens_str.py`;
   - deleted empty placeholder modules `Libraries/PyKotor/tests/tslpatcher/diff/test_gff.py`, `test_ssf.py`, and `test_tlk.py`.
- Validation completed for the touched string-wrapper slice with:
   - `uv run pytest Libraries/PyKotor/tests/common/test_wrapped_str.py Libraries/PyKotor/tests/common/test_wrapped_case_insens_str.py --import-mode=importlib`

## Full Test Inventory

The list below names every collected test symbol discovered from `test_*.py` files under `Libraries/PyKotor/tests`.

### Libraries/PyKotor/tests/cli/test_cli_backwards_compat.py (2 tests)

- test_all_commands_have_help
- test_unknown_command_returns_nonzero

### Libraries/PyKotor/tests/cli/test_diff_command.py (66 tests)

- TestPathTypeDetection.test_detect_file
- TestPathTypeDetection.test_detect_folder
- TestPathTypeDetection.test_detect_installation
- TestPathTypeDetection.test_detect_bioware_archive
- TestPathTypeDetection.test_detect_module_piece
- TestPathResolution.test_resolve_file_path
- TestPathResolution.test_resolve_folder_path
- TestPathResolution.test_resolve_installation_path
- TestDiffCommand.test_file_vs_file_gff
- TestDiffCommand.test_file_vs_file_identical
- TestDiffCommand.test_file_vs_file_2da
- TestDiffCommand.test_text_file_diff
- TestDiffCommand.test_verbose_output
- TestDiffCommand.test_missing_file
- TestDiffCommand.test_generate_ini_error_for_files
- TestDiffFormats.test_unified_format
- TestDiffFormats.test_context_format
- TestDiffFormats.test_default_format
- TestBiowareArchives.test_rim_vs_rim
- TestInstallationComparisons.test_identical_installations
- TestInstallationComparisons.test_detect_bioware_archive
- TestInstallationComparisons.test_detect_module_piece
- TestInstallationComparisons.test_detect_module_piece_dlg
- TestPathResolution.test_resolve_file
- TestPathResolution.test_resolve_folder
- TestPathResolution.test_resolve_installation
- TestPathResolution.test_resolve_bioware_archive
- TestPathResolution.test_resolve_path_relative_case_mismatch
- TestPathResolution.test_resolve_container_resource_syntax
- TestPathResolution.test_resolve_container_resource_not_found
- TestPathResolution.test_resolve_container_not_found
- TestDiffCommand.test_file_vs_file_identical
- TestDiffCommand.test_file_vs_file_different
- TestDiffCommand.test_folder_vs_folder
- TestDiffCommand.test_bioware_archive_vs_bioware_archive
- TestDiffCommand.test_installation_vs_file
- TestDiffCommand.test_folder_vs_module_piece
- TestDiffCommand.test_verbose_output
- TestDiffCommand.test_output_to_file
- TestCompositeModules.test_composite_module_detection
- TestCompositeModules.test_composite_module_diff
- TestOutputModes.test_diff_only_mode_file_vs_file
- TestOutputModes.test_diff_only_mode_archive_vs_archive
- TestOutputModes.test_quiet_mode
- TestOutputModes.test_full_mode_includes_summary
- TestInstallationErrorHandling.test_installation_invalid_path
- TestInstallationErrorHandling.test_mod_file_not_treated_as_installation
- TestInstallationErrorHandling.test_diff_with_nonexistent_path
- TestInstallationErrorHandling.test_generate_ini_with_non_installation_paths
- TestComprehensivePathCombinations.test_file_vs_folder
- TestComprehensivePathCombinations.test_archive_vs_folder
- TestComprehensivePathCombinations.test_module_piece_vs_regular_file
- TestComprehensivePathCombinations.test_folder_vs_module_piece
- TestComprehensivePathCombinations.test_erf_vs_rim
- TestComprehensivePathCombinations.test_mod_vs_erf
- TestComprehensivePathCombinations.test_text_file_vs_binary_file
- TestComprehensivePathCombinations.test_nested_folders
- TestComprehensivePathCombinations.test_empty_vs_populated_archive
- TestDiffWithTestFiles.test_gff_files_diff
- TestDiffWithTestFiles.test_2da_files_diff
- TestDiffWithTestFiles.test_tlk_files_diff
- TestDiffWithTestFiles.test_archive_files_diff
- TestDiffWithTestFiles.test_corrupted_vs_valid_files
- TestDiffWithTestFiles.test_text_files_unified_diff
- TestDiffWithTestFiles.test_side_by_side_format
- TestDiffWithTestFiles.test_context_format

### Libraries/PyKotor/tests/cli/test_diff_comprehensive.py (25 tests)

- TestDiffFileVsFile.test_diff_identical_text_files
- TestDiffFileVsFile.test_diff_different_text_files
- TestDiffFileVsFile.test_diff_identical_binary_files
- TestDiffFileVsFile.test_diff_different_binary_files
- TestDiffFolderVsFolder.test_diff_identical_folders
- TestDiffFolderVsFolder.test_diff_folders_with_added_file
- TestDiffFolderVsFolder.test_diff_folders_with_modified_file
- TestDiffInstallationVsInstallation.test_detect_installation_marker
- TestDiffFileVsInstallation.test_detect_mixed_path_types
- TestPathTypeDetection.test_detect_file
- TestPathTypeDetection.test_detect_folder
- TestPathTypeDetection.test_detect_installation
- TestPathTypeDetection.test_detect_archive_rim
- TestPathTypeDetection.test_detect_archive_erf
- TestPathTypeDetection.test_detect_module_piece_structure_rim
- TestPathTypeDetection.test_detect_module_piece_layout_rim
- TestPathTypeDetection.test_detect_module_piece_dialog_erf
- TestOutputModes.test_output_mode_quiet
- TestOutputModes.test_output_mode_diff_only
- TestEdgeCases.test_diff_empty_files
- TestEdgeCases.test_diff_empty_vs_nonempty_file
- TestEdgeCases.test_diff_identical_paths
- TestEdgeCases.test_diff_nonexistent_file
- TestComplexScenarios.test_diff_folder_with_multiple_files_partial_diff
- TestComplexScenarios.test_diff_folder_with_subdirectories

### Libraries/PyKotor/tests/cli/test_indoor_extract_installation_modules.py (1 tests)

- test_indoor_extract_each_module_matches_modulekit_loadability

### Libraries/PyKotor/tests/cli/test_indoor_roundtrip.py (17 tests)

- TestIndoorCLIRoundtrip.test_roundtrip_lyt_room_count
- TestIndoorCLIRoundtrip.test_roundtrip_lyt_room_positions
- TestIndoorCLIRoundtrip.test_roundtrip_wok_face_count
- TestIndoorCLIRoundtrip.test_roundtrip_wok_walkable_count
- TestIndoorCLIRoundtrip.test_roundtrip_wok_vertex_count
- TestIndoorCLIRoundtrip.test_roundtrip_wok_material_distribution
- TestIndoorCLIRoundtrip.test_roundtrip_required_resources
- TestIndoorCLIRoundtrip.test_roundtrip_are_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_ifo_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_git_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_lyt_full_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_lyt_room_models
- TestIndoorCLIRoundtrip.test_roundtrip_resource_set
- TestIndoorCLIRoundtrip.test_roundtrip_vis_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_pth_equivalent
- TestIndoorCLIRoundtrip.test_roundtrip_wok_byte_exact
- TestIndoorCLIRoundtripIndoorMapComparison.test_indoor_map_compare_after_roundtrip

### Libraries/PyKotor/tests/cli/test_json_commands.py (4 tests)

- test_to_json_and_from_json_roundtrip_tlk
- test_get_supports_auto_detected_installation_and_json_export
- test_kotor_paths_can_emit_json
- test_ssf_json_commands_roundtrip

### Libraries/PyKotor/tests/cli/test_walkmesh_rebuild.py (7 tests)

- test_walkmesh_rebuild_binary_to_file
- test_walkmesh_rebuild_overwrite
- test_walkmesh_rebuild_ascii_input_to_wok
- test_walkmesh_rebuild_with_ascii_flag
- test_walkmesh_rebuild_transition_arrows_invariant
- test_walkmesh_rebuild_missing_input_returns_nonzero
- test_render_bwm_to_pngs_writes_four_views

### Libraries/PyKotor/tests/common/test_case_aware_path.py (19 tests)

- TestCaseAwarePath.test_new_valid_str_argument
- TestCaseAwarePath.test_hashing
- TestCaseAwarePath.test_valid_name_property
- TestCaseAwarePath.test_valid_name_property_on_pathlib_path
- TestCaseAwarePath.test_new_invalid_argument
- TestCaseAwarePath.test_endswith
- TestCaseAwarePath.test_find_closest_match
- TestCaseAwarePath.test_get_matching_characters_count
- TestCaseAwarePath.test_relative_to_relpath
- TestCaseAwarePath.test_relative_to_relpath_case_sensitive
- TestCaseAwarePath.test_relative_to_abspath
- TestCaseAwarePath.test_relative_to_abspath_case_sensitive
- TestCaseAwarePath.test_fix_path_formatting
- TestIsRelativeTo.test_basic
- TestIsRelativeTo.test_different_paths
- TestIsRelativeTo.test_relative_paths
- TestIsRelativeTo.test_case_insensitive
- TestIsRelativeTo.test_not_path
- TestIsRelativeTo.test_same_path

### Libraries/PyKotor/tests/common/test_caseawarepath_globber_bug.py (12 tests)

- TestGlobberBug.test_rglob_simple_pattern
- TestGlobberBug.test_rglob_recursive_pattern
- TestGlobberBug.test_rglob_file_extension
- TestGlobberBug.test_rglob_case_sensitive_parameter
- TestGlobberBug.test_rglob_recurse_symlinks_parameter
- TestGlobberBug.test_glob_simple_pattern
- TestGlobberBug.test_glob_with_kwargs
- TestGlobberBug.test_rglob_from_utility
- TestGlobberBug.test_compare_with_standard_pathlib
- TestGlobberBug.test_nested_directory_rglob
- TestGlobberBug.test_globber_signature_analysis
- TestGlobberBug.test_installation_load_override_scenario

### Libraries/PyKotor/tests/common/test_consumer_manager.py (13 tests)

- TestConsumerManagerMainThreadAsync.test_singleton_behavior
- TestConsumerManagerMainThreadAsync.test_initialization
- TestConsumerManagerMainThreadAsync.test_add_task
- TestConsumerManagerMainThreadAsync.test_run_and_process_tasks
- TestConsumerManagerMainThreadAsync.test_get_results
- TestConsumerManagerMainThreadAsync.test_queue_stop_event
- TestConsumerManagerMainThreadAsync.test_process_remaining_tasks
- TestConsumerManagerMainThreadAsync.test_discard_remaining_tasks
- TestConsumerManagerMainThreadAsync.test_is_running
- TestConsumerManagerMainThreadAsync.test_is_running_async
- TestConsumerManagerMainThreadAsync.test_exception_handling_in_task
- TestConsumerManagerMainThreadAsync.test_consumer_start_and_stop
- TestConsumerManagerMainThreadAsync.test_async_get_results

### Libraries/PyKotor/tests/common/test_decode_fallbacks.py (15 tests)

- TestDecodeBytes.test_basic
- TestDecodeBytes.test_non_ascii
- TestDecodeBytes.test_unknown_encoding
- TestDecodeBytes.test_bom
- TestDecodeBytes.test_errors_replace
- TestDecodeBytes.test_known_encoding
- TestDecodeBytes.test_language_provided
- TestDecodeBytes.test_language_detect
- TestDecodeBytes.test_invalid_bytes_for_encoding
- TestDecodeBytes.test_fallback_to_detected_encoding
- TestDecodeBytes.test_8bit_encoding_only
- TestDecodeBytes.test_with_BOM_included
- TestDecodeBytes.test_undetectable_encoding_replace_errors
- TestDecodeBytes.test_strict_error_handling_decoding_failure
- TestDecodeBytes.test_no_valid_encoding_found_strict_errors

### Libraries/PyKotor/tests/common/test_geometry.py (16 tests)

- TestVector2.test_unpacking
- TestVector2.test_from_vector2
- TestVector2.test_from_vector3
- TestVector2.test_from_vector4
- TestVector3.test_unpacking
- TestVector3.test_from_vector2
- TestVector3.test_from_vector3
- TestVector3.test_from_vector4
- TestVector4.test_unpacking
- TestVector4.test_from_vector2
- TestVector4.test_from_vector3
- TestVector4.test_from_vector4
- TestVector4.test_from_euler
- TestFace.test_determine_z
- TestPolygon2.test_inside
- TestPolygon2.test_area

### Libraries/PyKotor/tests/common/test_get_case_sensitive_path.py (20 tests)

- TestCaseAwarePath.test_join_with_nonexistent_path
- TestCaseAwarePath.test_truediv_equivalent_to_joinpath
- TestCaseAwarePath.test_rtruediv
- TestCaseAwarePath.test_make_and_parse_uri
- TestCaseAwarePath.test_case_change_after_creation
- TestCaseAwarePath.test_complex_case_changes
- TestCaseAwarePath.test_mixed_case_creation_and_deletion
- TestCaseAwarePath.test_joinpath_chain
- TestCaseAwarePath.test_deep_directory_truediv
- TestCaseAwarePath.test_recursive_directory_creation
- TestCaseAwarePath.test_cascading_file_creation
- TestCaseAwarePath.test_relative_to
- TestCaseAwarePath.test_chmod
- TestCaseAwarePath.test_open_read_write
- TestCaseAwarePath.test_touch
- TestCaseAwarePath.test_samefile
- TestCaseAwarePath.test_replace
- TestCaseAwarePath.test_rename
- TestCaseAwarePath.test_symlink_to
- TestCaseAwarePath.test_hardlink_to

### Libraries/PyKotor/tests/common/test_path_isinstance.py (23 tests)

- TestPathInheritance.test_nt_case_hashing
- TestPathInheritance.test_path_attributes
- TestPathInheritance.test_path_hashing
- TestPathInheritance.test_pure_windows_path_isinstance
- TestPathInheritance.test_pure_posix_path_isinstance
- TestPathInheritance.test_path_isinstance
- TestPathInheritance.test_windows_path_isinstance
- TestPathInheritance.test_posix_path_isinstance
- TestPathInheritance.test_windows_path_isinstance_path
- TestPathInheritance.test_posix_path_isinstance_path
- TestPathInheritance.test_purepath_not_isinstance_windows_path
- TestPathInheritance.test_purepath_not_isinstance_posix_path
- TestPathInheritance.test_purepath_not_isinstance_path
- TestPathInheritance.test_pathlib_pure_windows_path_isinstance
- TestPathInheritance.test_pathlib_pure_posix_path_isinstance
- TestPathInheritance.test_pathlib_path_isinstance
- TestPathInheritance.test_pathlib_windows_path_isinstance
- TestPathInheritance.test_pathlib_posix_path_isinstance
- TestPathInheritance.test_pathlib_windows_path_isinstance_path
- TestPathInheritance.test_pathlib_posix_path_isinstance_path
- TestPathInheritance.test_pathlib_purepath_not_isinstance_windows_path
- TestPathInheritance.test_pathlib_purepath_not_isinstance_posix_path
- TestPathInheritance.test_pathlib_purepath_not_isinstance_path

### Libraries/PyKotor/tests/common/test_path_mixed_slash_handling.py (19 tests)

- TestPathlibMixedSlashes.test_low_granular_path_usage
- TestPathlibMixedSlashes.test_posix_exists_alternatives
- TestPathlibMixedSlashes.test_posix_case_hashing_custom_posix_path
- TestPathlibMixedSlashes.test_posix_case_hashing_custom_pure_posix_path
- TestPathlibMixedSlashes.test_posix_case_hashing_custom_path
- TestPathlibMixedSlashes.test_windows_case_hashing_custom_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_posix_posix_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_posix_pure_posix_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_windows_windows_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_windows_pure_windows_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_os_specific_path
- TestPathlibMixedSlashes.test_pathlib_path_edge_cases_os_specific_pure_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_posix_custom_posix_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_posix_custom_pure_posix_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_windows_custom_windows_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_windows_custom_pure_windows_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_os_specific_case_aware_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_os_specific_custom_path
- TestPathlibMixedSlashes.test_custom_path_edge_cases_os_specific_custom_pure_path

### Libraries/PyKotor/tests/common/test_stream.py (23 tests)

- TestBinaryReader.test_read
- TestBinaryReader.test_size
- TestBinaryReader.test_true_size
- TestBinaryReader.test_position
- TestBinaryReader.test_seek
- TestBinaryReader.test_skip
- TestBinaryReader.test_remaining
- TestBinaryReader.test_peek
- TestBinaryReader.test_read_locstring_with_unset_language
- TestBinaryWriterBytearray.test_write_terminated_string_empty_bytearray
- TestBinaryWriterBytearray.test_write_terminated_string_position_beyond_size
- TestBinaryWriterBytearray.test_write_terminated_string_extends_bytearray
- TestBinaryWriterBytearray.test_write_terminated_string_fits_existing_space
- TestBinaryWriterBytearray.test_write_terminated_string_null_terminator
- TestBinaryWriterBytearray.test_write_terminated_string_multiple_writes
- TestBinaryWriterBytearray.test_write_terminated_string_encoding
- TestBinaryWriterBytearray.test_write_terminated_string_empty_string
- TestBinaryWriterBytearray.test_write_terminated_string_large_string
- TestBinaryReaderPorted.test_seek_ignore_and_tell_in_little_endian_stream
- TestBinaryReaderPorted.test_read_from_little_endian_stream
- TestBinaryReaderPorted.test_read_from_big_endian_stream
- TestBinaryWriter.test_write_to_little_endian_stream
- TestBinaryWriter.test_write_to_big_endian_stream

### Libraries/PyKotor/tests/common/test_wrapped_case_insens_str.py (47 tests)

- TestCaseInsensImmutableStr.test_capitalize
- TestCaseInsensImmutableStr.test_casefold
- TestCaseInsensImmutableStr.test_center
- TestCaseInsensImmutableStr.test_count
- TestCaseInsensImmutableStr.test_encode
- TestCaseInsensImmutableStr.test_endswith
- TestCaseInsensImmutableStr.test_expandtabs
- TestCaseInsensImmutableStr.test_find
- TestCaseInsensImmutableStr.test_format
- TestCaseInsensImmutableStr.test_format_map
- TestCaseInsensImmutableStr.test_index
- TestCaseInsensImmutableStr.test_isalnum
- TestCaseInsensImmutableStr.test_isalpha
- TestCaseInsensImmutableStr.test_isascii
- TestCaseInsensImmutableStr.test_isdecimal
- TestCaseInsensImmutableStr.test_isdigit
- TestCaseInsensImmutableStr.test_isidentifier
- TestCaseInsensImmutableStr.test_islower
- TestCaseInsensImmutableStr.test_isnumeric
- TestCaseInsensImmutableStr.test_isprintable
- TestCaseInsensImmutableStr.test_isspace
- TestCaseInsensImmutableStr.test_istitle
- TestCaseInsensImmutableStr.test_isupper
- TestCaseInsensImmutableStr.test_join
- TestCaseInsensImmutableStr.test_ljust
- TestCaseInsensImmutableStr.test_lower
- TestCaseInsensImmutableStr.test_lstrip
- TestCaseInsensImmutableStr.test_partition
- TestCaseInsensImmutableStr.test_removeprefix
- TestCaseInsensImmutableStr.test_removesuffix
- TestCaseInsensImmutableStr.test_replace
- TestCaseInsensImmutableStr.test_replace_extras
- TestCaseInsensImmutableStr.test_rfind
- TestCaseInsensImmutableStr.test_rindex
- TestCaseInsensImmutableStr.test_rjust
- TestCaseInsensImmutableStr.test_rpartition
- TestCaseInsensImmutableStr.test_rsplit
- TestCaseInsensImmutableStr.test_rstrip
- TestCaseInsensImmutableStr.test_split
- TestCaseInsensImmutableStr.test_splitlines
- TestCaseInsensImmutableStr.test_startswith
- TestCaseInsensImmutableStr.test_strip
- TestCaseInsensImmutableStr.test_swapcase
- TestCaseInsensImmutableStr.test_title
- TestCaseInsensImmutableStr.test_translate
- TestCaseInsensImmutableStr.test_upper
- TestCaseInsensImmutableStr.test_zfill

### Libraries/PyKotor/tests/common/test_wrapped_str.py (73 tests)

- TestMutableStr.test_init
- TestMutableStr.test_str
- TestMutableStr.test_repr
- TestMutableStr.test_eq
- TestMutableStr.test_ne
- TestMutableStr.test_lt
- TestMutableStr.test_le
- TestMutableStr.test_gt
- TestMutableStr.test_ge
- TestMutableStr.test_hash
- TestMutableStr.test_bool
- TestMutableStr.test_getitem
- TestMutableStr.test_len
- TestMutableStr.test_contains
- TestMutableStr.test_add
- TestMutableStr.test_mul
- TestMutableStr.test_mod
- TestMutableStr.test_capitalize
- TestMutableStr.test_casefold
- TestMutableStr.test_center
- TestMutableStr.test_count
- TestMutableStr.test_encode
- TestMutableStr.test_endswith
- TestMutableStr.test_expandtabs
- TestMutableStr.test_find
- TestMutableStr.test_format
- TestMutableStr.test_format_map
- TestMutableStr.test_index
- TestMutableStr.test_isalnum
- TestMutableStr.test_isalpha
- TestMutableStr.test_isascii
- TestMutableStr.test_isdecimal
- TestMutableStr.test_isdigit
- TestMutableStr.test_isidentifier
- TestMutableStr.test_islower
- TestMutableStr.test_isnumeric
- TestMutableStr.test_isprintable
- TestMutableStr.test_isspace
- TestMutableStr.test_istitle
- TestMutableStr.test_isupper
- TestMutableStr.test_join
- TestMutableStr.test_ljust
- TestMutableStr.test_lower
- TestMutableStr.test_lstrip
- TestMutableStr.test_partition
- TestMutableStr.test_removeprefix
- TestMutableStr.test_removesuffix
- TestMutableStr.test_replace
- TestMutableStr.test_rfind
- TestMutableStr.test_rindex
- TestMutableStr.test_rjust
- TestMutableStr.test_rpartition
- TestMutableStr.test_rsplit
- TestMutableStr.test_rstrip
- TestMutableStr.test_split
- TestMutableStr.test_splitlines
- TestMutableStr.test_startswith
- TestMutableStr.test_strip
- TestMutableStr.test_swapcase
- TestMutableStr.test_title
- TestMutableStr.test_translate
- TestMutableStr.test_upper
- TestMutableStr.test_zfill
- TestMutableStr.test_iter
- TestMutableStr.test_reversed
- TestMutableStr.test_getstate
- TestMutableStr.test_getnewargs
- TestMutableStr.test_sizeof
- TestMutableStr.test_reduce
- TestMutableStr.test_reduce_ex
- TestMutableStr.test_format_spec
- TestMutableStr.test_dir
- TestMutableStr.test_subclasshook

### Libraries/PyKotor/tests/common/test_wrapped_str2.py (15 tests)

- TestCaseInsensImmutableStr.test_coerce_str
- TestCaseInsensImmutableStr.test_init
- TestCaseInsensImmutableStr.test_contains
- TestCaseInsensImmutableStr.test_eq
- TestCaseInsensImmutableStr.test_ne
- TestCaseInsensImmutableStr.test_hash
- TestCaseInsensImmutableStr.test_find
- TestCaseInsensImmutableStr.test_partition
- TestCaseInsensImmutableStr.test_replace
- TestCaseInsensImmutableStr.test_rpartition
- TestCaseInsensImmutableStr.test_endswith
- TestCaseInsensImmutableStr.test_rfind
- TestCaseInsensImmutableStr.test_rsplit
- TestCaseInsensImmutableStr.test_split
- TestCaseInsensImmutableStr.test_split_by_indices

### Libraries/PyKotor/tests/extract/test_capsule.py (2 tests)

- TestCapsule.test_add_to_capsule_file
- TestCapsule.test_existing_capsule_contents

### Libraries/PyKotor/tests/extract/test_chitin.py (2 tests)

- TestChitin.test_k1_chitin
- TestChitin.test_k2_chitin

### Libraries/PyKotor/tests/extract/test_installation.py (12 tests)

- TestInstallation.test_resource
- TestInstallation.test_resources
- TestInstallation.test_location
- TestInstallation.test_locations
- TestInstallation.test_texture
- TestInstallation.test_textures
- TestInstallation.test_sounds
- TestInstallation.test_string
- TestInstallation.test_strings
- TestInstallation.test_pickle_unpickle
- TestInstallation.test_pickle_to_file
- TestInstallation.test_multiple_unpickle

### Libraries/PyKotor/tests/extract/test_nested_capsule.py (12 tests)

- TestFindRealFilesystemPath.test_existing_file_returns_path_no_parts
- TestFindRealFilesystemPath.test_nested_path_returns_real_path_and_parts
- TestFindRealFilesystemPath.test_nonexistent_path_returns_none
- TestNestedCapsuleExtraction.test_single_level_capsule
- TestNestedCapsuleExtraction.test_nested_erf_extraction
- TestNestedCapsuleExtraction.test_file_resource_data_nested
- TestNestedCapsuleExtraction.test_file_resource_exists_nested
- TestNestedCapsuleExtraction.test_triple_nested_capsule
- TestNestedCapsuleExtraction.test_rim_nested_in_erf
- TestNestedCapsuleExtraction.test_file_resource_exists_inside_bif_does_not_use_lazy_capsule
- TestResourceIdentifierFromPath.test_nested_path_parses_correctly
- TestResourceIdentifierFromPath.test_capsule_path_parses_correctly

### Libraries/PyKotor/tests/extract/test_save_load_flow_k1.py (16 tests)

- TestSaveLoadFlowK1.test_get_free_disk_space_k1_returns_positive
- TestSaveLoadFlowK1.test_create_directory_k1_creates_and_exists_ok
- TestSaveLoadFlowK1.test_get_directory_size_k1_empty_is_zero
- TestSaveLoadFlowK1.test_get_directory_size_k1_sums_file_sizes
- TestSaveLoadFlowK1.test_clean_directory_k1_empties_dir
- TestSaveLoadFlowK1.test_run_k1_save_flow_skip_screenshot_when_path_equal
- TestSaveLoadFlowK1.test_run_k1_save_flow_fails_when_required_save_bytes_exceeds_free
- TestSaveLoadFlowK1.test_run_k1_save_flow_fails_when_dir_size_at_least_required_max
- TestSaveLoadFlowK1.test_run_k1_save_flow_minimal_returns_one_and_writes_screenshot
- TestSaveLoadFlowK1.test_run_tsl_save_flow_minimal_returns_one_and_writes_screenshot
- TestSaveLoadFlowK1.test_get_free_disk_space_tsl_returns_positive
- TestSaveLoadFlowK1.test_create_directory_tsl_creates_and_exists_ok
- TestSaveLoadFlowK1.test_run_save_flow_returns_zero_when_game_undetermined
- TestSaveLoadFlowK1.test_run_load_flow_raises_when_game_undetermined
- TestSaveLoadFlowK1.test_run_save_flow_k1_path_uses_k1_flow
- TestSaveLoadFlowK1.test_run_save_flow_k2_path_uses_tsl_flow

### Libraries/PyKotor/tests/extract/test_talktable.py (2 tests)

- TestTalkTable.test_basic_accessors
- TestTalkTable.test_batch

### Libraries/PyKotor/tests/font/test_txi_tga_font.py (6 tests)

- TestWriteBitmapFont.test_bitmap_font
- TestWriteBitmapFont.test_bitmap_font_thai
- TestWriteBitmapFont.test_valid_inputs
- TestWriteBitmapFont.test_invalid_font_path
- TestWriteBitmapFont.test_invalid_language
- TestWriteBitmapFont.test_invalid_resolution

### Libraries/PyKotor/tests/gl/test_async_loader_texture_txi_none.py (2 tests)

- test_parse_texture_data_tpc_without_txi_does_not_error
- test_parse_texture_data_dxt1_cutout_without_txi_preserves_alpha

### Libraries/PyKotor/tests/gl/test_camera_controller.py (28 tests)

- TestInputState.test_default_values
- TestCameraControllerSettings.test_default_values
- TestCameraControllerSettings.test_custom_settings
- TestCameraState.test_default_values
- TestCameraState.test_sync_to_camera
- TestCameraController.test_initialization
- TestCameraController.test_mode_detection_orbit_middle_mouse
- TestCameraController.test_mode_detection_orbit_left_mouse
- TestCameraController.test_mode_detection_orbit_alt_left
- TestCameraController.test_mode_detection_pan_shift_middle
- TestCameraController.test_mode_detection_pan_ctrl_left
- TestCameraController.test_mode_detection_zoom_right_mouse
- TestCameraController.test_mode_detection_none
- TestCameraController.test_orbit_changes_rotation
- TestCameraController.test_orbit_drag_right_matches_rotate_right_direction
- TestCameraController.test_orbit_drag_up_moves_toward_top_view
- TestCameraController.test_pan_changes_position
- TestCameraController.test_zoom_scroll_changes_distance
- TestCameraController.test_zoom_clamps_to_limits
- TestCameraController.test_pitch_clamps_to_limits
- TestCameraController.test_smoothing_interpolates_values
- TestCameraController.test_no_smoothing_instant_update
- TestCameraController.test_input_acceleration
- TestCameraController.test_focus_on_point
- TestCameraController.test_reset_to_default
- TestCameraController.test_camera_is_updated
- TestCameraModeEnum.test_all_modes_exist
- TestCameraModeEnum.test_modes_are_distinct

### Libraries/PyKotor/tests/gl/test_frustum_culling.py (33 tests)

- TestCameraMatrixCaching.test_view_matrix_caching
- TestCameraMatrixCaching.test_view_matrix_invalidation_on_position_change
- TestCameraMatrixCaching.test_view_matrix_invalidation_on_rotation
- TestCameraMatrixCaching.test_projection_matrix_caching
- TestCameraMatrixCaching.test_projection_matrix_invalidation_on_fov_change
- TestCameraMatrixCaching.test_set_resolution_invalidates_projection
- TestFrustum.test_frustum_initialization
- TestFrustum.test_frustum_update_from_camera
- TestFrustum.test_frustum_caching
- TestFrustum.test_point_in_frustum_origin
- TestFrustum.test_point_behind_camera
- TestFrustum.test_point_beyond_far_plane
- TestFrustum.test_sphere_in_frustum_visible
- TestFrustum.test_sphere_partially_in_frustum
- TestFrustum.test_sphere_completely_outside
- TestFrustum.test_aabb_in_frustum_visible
- TestFrustum.test_aabb_behind_camera
- TestFrustum.test_sphere_distance_calculation
- TestFrustum.test_frustum_plane_indices
- TestCullingStats.test_initial_state
- TestCullingStats.test_record_visible_object
- TestCullingStats.test_record_culled_object
- TestCullingStats.test_cull_rate_calculation
- TestCullingStats.test_cull_rate_empty
- TestCullingStats.test_reset
- TestCullingStats.test_end_frame
- TestCullingStats.test_repr
- TestFrustumIntegration.test_typical_module_scene
- TestFrustumIntegration.test_camera_rotation_affects_culling
- TestPerformanceOptimizations.test_frustum_caching_avoids_recalculation
- TestPerformanceOptimizations.test_culling_stats_reset_per_frame
- TestPerformanceOptimizations.test_culling_stats_accuracy
- TestPerformanceOptimizations.test_sphere_culling_performance

### Libraries/PyKotor/tests/gl/test_gl_accel.py (29 tests)

- TestExtractFrustumPlanes.test_identity_matrix
- TestExtractFrustumPlanes.test_planes_are_normalized
- TestExtractFrustumPlanes.test_rejects_wrong_size
- TestBatchFrustumCull.test_all_visible
- TestBatchFrustumCull.test_mixed_visibility
- TestBatchFrustumCull.test_empty_spheres
- TestTransformBounds.test_identity_transform
- TestTransformBounds.test_translation_transform
- TestTransformBounds.test_zero_vertices
- TestMat4MultiplyBatch.test_identity_multiply
- TestAabbInFrustumBatch.test_visible_aabb
- TestComputeNodeWorldTransforms.test_single_root_node_identity
- TestComputeNodeWorldTransforms.test_root_translation_propagates
- TestComputeNodeWorldTransforms.test_parent_child_chain
- TestComputeNodeWorldTransforms.test_rejects_mismatched_sizes
- TestBatchTransformVertices2D.test_identity_transform
- TestBatchTransformVertices2D.test_translation_only
- TestBatchTransformVertices2D.test_90_degree_rotation
- TestBatchTransformVertices2D.test_flip_x
- TestBatchTransformVertices2D.test_flip_y
- TestBatchHookSnapDistances.test_no_snap_when_far
- TestBatchHookSnapDistances.test_snap_found
- TestBatchHookSnapDistances.test_picks_closest
- TestBatchHookSnapDistances.test_local_offset_applied
- TestBatchVerticesInRect.test_vertex_inside
- TestBatchVerticesInRect.test_vertex_outside
- TestBatchVerticesInRect.test_translation_brings_inside
- TestBatchVerticesInRect.test_flip_moves_outside
- TestBatchVerticesInRect.test_early_termination

### Libraries/PyKotor/tests/gl/test_mdl_mesh_alpha_modes.py (2 tests)

- test_default_alpha_texture_renders_opaque
- test_cutout_texture_disables_regular_blending

### Libraries/PyKotor/tests/gl/test_texture_loader_core.py (6 tests)

- TestMipmapSerialization.test_serialize_deserialize_rgba
- TestMipmapSerialization.test_serialize_deserialize_rgb
- TestMipmapSerialization.test_serialize_deserialize_greyscale
- TestMipmapSerialization.test_serialize_format
- TestQueueCommunication.test_queue_put_get
- TestQueueCommunication.test_queue_multiple_items

### Libraries/PyKotor/tests/resource/formats/ncs/test_do_types_strict_typing.py (2 tests)

- TestDoTypesStrictTyping.test_assert_stack_calls_print_state_directly
- TestDoTypesStrictTyping.test_subroutine_state_has_print_state_method

### Libraries/PyKotor/tests/resource/formats/test_base_comparable_strict_typing.py (5 tests)

- TestComparableMixinStrictTyping.test_compare_uses_class_variable_directly
- TestComparableMixinStrictTyping.test_compare_uses_getattr_for_field_values
- TestComparableMixinStrictTyping.test_compare_sequence_fields
- TestComparableMixinStrictTyping.test_compare_set_fields
- TestComparableMixinStrictTyping.test_compare_missing_field_handles_gracefully

### Libraries/PyKotor/tests/resource/formats/test_bif.py (8 tests)

- TestBIFFormats.test_bif_from_plaintext_json
- TestBIFFormats.test_bzf_read
- TestBIFFormats.test_bif_write
- TestBIFFormats.test_bzf_write
- TestBIFFormats.test_to_raw_data_simple_read_size_unchanged
- TestBIFFormats.test_write_to_file_valid_path_size_unchanged
- TestBIFFormats.test_read_bif_with_key_source_lookup_by_resref
- TestBIFFormats.test_bif_composite_id_nonzero_bif_index

### Libraries/PyKotor/tests/resource/formats/test_bwm.py (125 tests)

- TestBWMFormatDetection.test_read_bwm_binary_magic_uses_binary
- TestBWMFormatDetection.test_read_bwm_ascii_detection
- TestBWMFormatDetection.test_write_bwm_ascii_roundtrip
- TestBWMHeaderValidation.test_invalid_magic
- TestBWMHeaderValidation.test_invalid_version
- TestBWMHeaderValidation.test_valid_header
- TestBWMHeaderValidation.test_header_signature_exact_match
- TestBWMHeaderValidation.test_header_version_parsing
- TestBWMHeaderValidation.test_walkmesh_type_area
- TestBWMHeaderValidation.test_header_offsets_valid
- TestBWMVertexHandling.test_vertex_roundtrip
- TestBWMVertexHandling.test_vertex_deduplication
- TestBWMVertexHandling.test_vertex_count
- TestBWMVertexHandling.test_vertex_coordinates_precision
- TestBWMVertexHandling.test_vertex_sharing
- TestBWMFaceHandling.test_face_material_preservation
- TestBWMFaceHandling.test_walkable_face_ordering
- TestBWMFaceHandling.test_face_vertex_indices_bounds_checking
- TestBWMFaceHandling.test_face_count
- TestBWMFaceHandling.test_face_vertex_indices_valid
- TestBWMFaceHandling.test_face_normal_computation
- TestBWMFaceHandling.test_face_planar_distance
- TestBWMMaterials.test_material_assignment
- TestBWMMaterials.test_walkable_materials
- TestBWMMaterials.test_unwalkable_materials
- TestBWMMaterials.test_material_id_range
- TestBWMTransitions.test_transition_preservation
- TestBWMTransitions.test_perimeter_edge_identification
- TestBWMTransitions.test_perimeter_edge_set
- TestBWMTransitions.test_enforce_transition_invariant_clears_internal
- TestBWMTransitions.test_assert_transition_arrows_invariant_valid
- TestBWMTransitions.test_assert_transition_arrows_invariant_invalid
- TestBWMTransitions.test_read_bwm_regenerate_derived_true_enforces
- TestBWMTransitions.test_read_bwm_regenerate_derived_false_skips_enforce
- TestBWMTransitions.test_edge_inward_direction_xy
- TestBWMEdges.test_edge_count
- TestBWMEdges.test_edges_have_no_adjacent_walkable
- TestBWMEdges.test_edge_transition_values
- TestBWMEdges.test_perimeter_loop_closure
- TestBWMWOKvsPWK.test_wok_has_aabb_tree
- TestBWMWOKvsPWK.test_pwk_no_aabb_tree
- TestBWMWOKvsPWK.test_wok_has_adjacencies
- TestBWMRoundtrip.test_complete_roundtrip
- TestBWMRoundtrip.test_roundtrip_preserves_vertices
- TestBWMRoundtrip.test_roundtrip_preserves_faces
- TestBWMRoundtrip.test_roundtrip_preserves_materials
- TestBWMRoundtrip.test_roundtrip_preserves_transitions
- TestBWMRoundtrip.test_roundtrip_preserves_hooks
- TestBWMRoundtrip.test_roundtrip_with_transitions
- TestBWMEdgeCases.test_single_face_walkmesh
- TestBWMEdgeCases.test_all_unwalkable_faces
- TestBWMEdgeCases.test_all_walkable_faces
- TestBWMEdgeCases.test_empty_faces_list
- TestBWMEdgeCases.test_pwk_dwk_no_aabb_adjacency
- TestBWMEdgeCases.test_adjacency_encoding_formula
- TestBWMEdgeCases.test_perimeter_edge_transitions
- TestBWMEdgeCases.test_face_winding_order
- TestBWMEdgeCases.test_vertex_index_bounds
- TestBWMEdgeCases.test_material_walkability_consistency
- TestBWMEdgeCases.test_hook_positions_preserved
- TestBWMEdgeCases.test_face_ordering_walkable_first
- TestBWMEdgeCases.test_adjacency_only_walkable_faces
- TestBWMEdgeCases.test_perimeter_loop_construction
- TestBWMEdgeCases.test_aabb_tree_balance
- TestBWMEdgeCases.test_edge_index_encoding
- TestBWMEdgeCases.test_roundtrip_preserves_walkmesh_type
- TestBWMFaceEquality.test_face_value_equality
- TestBWMFaceEquality.test_face_inequality_different_vertices
- TestBWMFaceEquality.test_face_inequality_different_material
- TestBWMFaceEquality.test_face_inequality_different_transitions
- TestBWMFaceEquality.test_face_set_membership
- TestBWMSpatialQueries.test_point_in_face_2d
- TestBWMSpatialQueries.test_face_centroid
- TestBWMSpatialQueries.test_face_area
- TestBWMFromRealFiles.test_read_real_wok_file
- TestBWMFromRealFiles.test_roundtrip_real_wok_file
- TestBWMFromRealFiles.test_second_file_roundtrip
- TestBWMFromRealFiles.test_second_file_properties
- TestBWMAdjacency.test_adjacent_faces_detection
- TestBWMAdjacency.test_non_adjacent_faces
- TestBWMAdjacency.test_adjacency_encoding
- TestBWMAdjacency.test_adjacency_bidirectional
- TestBWMAdjacency.test_adjacency_shared_vertices
- TestBWMAABBTree.test_aabb_tree_generation
- TestBWMAABBTree.test_aabb_tree_structure
- TestBWMAABBTree.test_aabb_count
- TestBWMAABBTree.test_aabb_leaf_nodes
- TestBWMAABBTree.test_aabb_bounds_contain_face
- TestBWMBinaryFormat.test_header_bytes
- TestBWMBinaryFormat.test_walkmesh_type_byte_offset
- TestBWMBinaryFormat.test_pwk_dwk_type_byte
- TestBWMBinaryFormat.test_vertex_count_offset
- TestBWMBinaryFormat.test_face_count_offset
- TestBWMAABBPlanes.test_most_significant_plane_values
- TestBWMAABBPlanes.test_internal_nodes_have_children
- TestBWMEdgeDetails.test_edge_vertices
- TestBWMEdgeDetails.test_edge_face_reference
- TestBWMMaterialCompleteness.test_walkable_materials
- TestBWMMaterialCompleteness.test_non_walkable_materials
- TestBWMVendorDiscrepancies.test_adjacency_decoding_consensus
- TestBWMVendorDiscrepancies.test_perimeter_index_handling
- TestBWMRaycasting.test_raycast_hits_face
- TestBWMRaycasting.test_raycast_misses_face
- TestBWMRaycasting.test_raycast_respects_max_distance
- TestBWMRaycasting.test_raycast_filters_by_material
- TestBWMRaycasting.test_raycast_with_pwk_dwk
- TestBWMPointInFace.test_point_inside_face
- TestBWMPointInFace.test_point_outside_face
- TestBWMPointInFace.test_point_on_edge
- TestBWMPointInFace.test_point_at_vertex
- TestBWMHeightCalculation.test_get_height_at_point_on_face
- TestBWMHeightCalculation.test_get_height_at_point_off_face
- TestBWMHeightCalculation.test_get_height_at_with_tilted_face
- TestBWMHeightCalculation.test_get_height_at_filters_by_material
- TestBWMFaceFinding.test_find_face_at_point_on_face
- TestBWMFaceFinding.test_find_face_at_point_off_face
- TestBWMFaceFinding.test_find_face_at_with_multiple_faces
- TestBWMFaceFinding.test_find_face_at_filters_by_material
- TestBWMFaceFinding.test_find_face_at_with_pwk_dwk
- TestBWMFaceFinding.test_find_face_at_with_real_file
- TestBWMSerializeStrictTyping.test_serialize_walkmesh_type_enum_value
- TestBWMSerializeStrictTyping.test_serialize_walkmesh_type_placeable_enum_value
- TestBWMSerializeStrictTyping.test_serialize_face_material_enum_value
- TestBWMSerializeStrictTyping.test_serialize_multiple_faces_different_materials
- TestBWMSerializeStrictTyping.test_serialize_complete_bwm_structure

### Libraries/PyKotor/tests/resource/formats/test_dds.py (20 tests)

- TestDDSParsing.test_standard_dds_dxt1_roundtrip
- TestDDSParsing.test_bioware_dds_multiple_mips
- TestDDSParsing.test_bioware_dds_requires_power_of_two
- TestDDSParsing.test_uncompressed_bgra_header
- TestDDSParsing.test_uncompressed_bgr_header
- TestDDSParsing.test_uncompressed_4444_expands_to_rgba
- TestDDSParsing.test_uncompressed_1555_expands_to_rgba
- TestDDSParsing.test_uncompressed_565_expands_to_rgb
- TestDDSParsing.test_dds_writer_from_tpc_instance
- TestDDSParsing.test_dds_writer_converts_rgba_to_bgra
- TestDDSParsing.test_standard_dxt5_mip_chain
- TestDDSParsing.test_standard_dxt3_format_recognized
- TestDDSParsing.test_standard_cubemap_faces_parsed
- TestDDSParsing.test_standard_dds_dxt5_alpha_and_multiple_mips
- TestDDSParsing.test_standard_dds_uncompressed_bgr_24bit
- TestDDSParsing.test_uncompressed_16bit_paths_4444_1555_565
- TestDDSParsing.test_cubemap_faces_detection
- TestDDSParsing.test_detect_tpc_by_extension
- TestDDSParsing.test_bioware_invalid_data_size_raises
- TestDDSParsing.test_writer_converts_rgba_to_bgra_for_dds

### Libraries/PyKotor/tests/resource/formats/test_erf.py (4 tests)

- TestERF.test_binary_io
- TestERF.test_file_io
- TestERF.test_read_raises
- TestERF.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_gff.py (8 tests)

- TestGFF.test_binary_io
- TestGFF.test_file_io
- TestGFF.test_xml_io
- TestGFF.test_to_raw_data_simple_read_size_unchanged
- TestGFF.test_detect_gff_no_false_resync_after_binary_junk
- TestGFF.test_read_gff_binary_after_non_padding_prefix
- TestGFF.test_read_raises
- TestGFF.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_gff_list_compare.py (1 tests)

- test_gfflist_compare_handles_vector_values_without_type_error

### Libraries/PyKotor/tests/resource/formats/test_key.py (12 tests)

- TestKEY.test_write_key
- TestKEY.test_key_multiple_resources
- TestKEY.test_key_v1_write
- TestKEY.test_key_invalid_type
- TestKEY.test_key_invalid_version
- TestKEY.test_key_create_empty
- TestKEY.test_key_add_bif
- TestKEY.test_key_remove_bif
- TestKEY.test_key_add_resource
- TestKEY.test_key_get_resources
- TestKEY.test_key_offset_calculations
- TestKEY.test_key_v1_read

### Libraries/PyKotor/tests/resource/formats/test_lip.py (5 tests)

- TestLIP.test_binary_io
- TestLIP.test_file_io
- TestLIP.test_xml_io
- TestLIP.test_read_raises
- TestLIP.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_lyt.py (4 tests)

- TestLYT.test_binary_io
- TestLYT.test_file_io
- TestLYT.test_read_raises
- TestLYT.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_mdl.py (33 tests)

- TestMDLBinaryIO.test_read_mdl_basic
- TestMDLBinaryIO.test_read_mdl_fast
- TestMDLBinaryIO.test_read_mdl_fast_vs_full
- TestMDLBinaryIO.test_read_all_test_files
- TestMDLBinaryIO.test_mdl_node_hierarchy
- TestMDLBinaryIO.test_mdl_mesh_data
- TestMDLBinaryIO.test_mdl_get_node_by_name
- TestMDLBinaryIO.test_mdl_textures
- TestMDLBinaryIO.test_mdl_lightmaps
- TestMDLBinaryIO.test_write_mdl_binary
- TestMDLBinaryIO.test_mdl_roundtrip
- TestMDLData.test_mdl_creation
- TestMDLData.test_mdl_node_creation
- TestMDLData.test_mdl_node_hierarchy_creation
- TestMDLData.test_mdl_mesh_creation
- TestMDLData.test_mdl_animation_creation
- TestMDLData.test_mdl_find_parent
- TestMDLData.test_mdl_global_position
- TestMDLData.test_skin_prepare_bone_lookups
- TestMDLPerformance.test_fast_load_performance
- TestMDLEdgeCases.test_read_nonexistent_file
- TestMDLEdgeCases.test_empty_mdl
- TestMDLEdgeCases.test_node_with_no_children
- TestMDLEdgeCases.test_get_nonexistent_node_by_id
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_character_model
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_door_model
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_placeable_model
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_animation_model
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_camera_model
- TestMDLRoundTripBinaryToAsciiToBinary.test_roundtrip_all_models
- TestMDLExtendedRoundTrip.test_triple_roundtrip_binary_to_ascii_to_binary_to_ascii
- TestMDLExtendedRoundTrip.test_multiple_roundtrip_all_models
- TestMDLCrossModelRoundTrip.test_all_models_binary_to_ascii_preserve_structure

### Libraries/PyKotor/tests/resource/formats/test_mdl_ascii.py (77 tests)

- TestMDLAsciiDetection.test_detect_ascii_format
- TestMDLAsciiDetection.test_detect_binary_format
- TestMDLAsciiDetection.test_detect_from_bytes
- TestMDLAsciiBasicIO.test_write_empty_mdl
- TestMDLAsciiBasicIO.test_read_write_roundtrip_basic
- TestMDLAsciiBasicIO.test_write_to_bytes
- TestMDLAsciiBasicIO.test_write_to_bytesio
- TestMDLAsciiNodeTypes.test_write_dummy_node
- TestMDLAsciiNodeTypes.test_read_dummy_node
- TestMDLAsciiNodeTypes.test_write_trimesh_node
- TestMDLAsciiNodeTypes.test_roundtrip_face_payload_is_derived_deterministically
- TestMDLAsciiNodeTypes.test_read_trimesh_node
- TestMDLAsciiNodeTypes.test_write_light_node
- TestMDLAsciiNodeTypes.test_read_light_node
- TestMDLAsciiNodeTypes.test_write_emitter_node
- TestMDLAsciiNodeTypes.test_read_emitter_node
- TestMDLAsciiNodeTypes.test_write_reference_node
- TestMDLAsciiNodeTypes.test_read_reference_node
- TestMDLAsciiNodeTypes.test_write_saber_node
- TestMDLAsciiNodeTypes.test_read_saber_node
- TestMDLAsciiNodeTypes.test_write_aabb_node
- TestMDLAsciiNodeTypes.test_read_aabb_node
- TestMDLAsciiControllers.test_write_position_controller
- TestMDLAsciiControllers.test_read_position_controller
- TestMDLAsciiControllers.test_write_orientation_controller
- TestMDLAsciiControllers.test_read_orientation_controller
- TestMDLAsciiControllers.test_write_scale_controller
- TestMDLAsciiControllers.test_write_bezier_controller
- TestMDLAsciiControllers.test_read_bezier_controller
- TestMDLAsciiControllers.test_write_all_header_controllers
- TestMDLAsciiControllers.test_write_light_controllers
- TestMDLAsciiControllers.test_write_emitter_controllers
- TestMDLAsciiMeshData.test_write_mesh_vertices
- TestMDLAsciiMeshData.test_read_mesh_vertices
- TestMDLAsciiMeshData.test_write_mesh_faces
- TestMDLAsciiMeshData.test_read_mesh_faces
- TestMDLAsciiMeshData.test_write_mesh_tverts
- TestMDLAsciiMeshData.test_read_mesh_tverts
- TestMDLAsciiMeshData.test_write_skin_mesh
- TestMDLAsciiMeshData.test_read_skin_mesh
- TestMDLAsciiMeshData.test_write_dangly_mesh
- TestMDLAsciiAnimations.test_write_animation_basic
- TestMDLAsciiAnimations.test_read_animation_basic
- TestMDLAsciiAnimations.test_write_animation_with_events
- TestMDLAsciiAnimations.test_read_animation_with_events
- TestMDLAsciiAnimations.test_write_animation_with_nodes
- TestMDLAsciiAnimations.test_read_animation_with_nodes
- TestMDLAsciiAnimations.test_write_multiple_animations
- TestMDLAsciiRoundTrip.test_ascii_to_ascii_roundtrip
- TestMDLAsciiRoundTrip.test_ascii_with_all_node_types_roundtrip
- TestMDLAsciiRoundTrip.test_ascii_with_all_controllers_roundtrip
- TestMDLAsciiRoundTrip.test_ascii_with_animations_roundtrip
- TestMDLAsciiClassifications.test_write_all_classifications
- TestMDLAsciiClassifications.test_read_all_classifications
- TestMDLAsciiEdgeCases.test_read_empty_file
- TestMDLAsciiEdgeCases.test_read_malformed_header
- TestMDLAsciiEdgeCases.test_read_missing_endmarkers
- TestMDLAsciiEdgeCases.test_write_node_with_no_name
- TestMDLAsciiEdgeCases.test_write_controller_with_no_rows
- TestMDLAsciiEdgeCases.test_read_controller_with_old_format
- TestMDLAsciiEdgeCases.test_write_large_mesh
- TestMDLAsciiEdgeCases.test_read_large_mesh
- TestMDLAsciiEdgeCases.test_write_deep_hierarchy
- TestMDLAsciiEdgeCases.test_read_deep_hierarchy
- TestMDLAsciiBinaryIntegration.test_binary_to_ascii_conversion
- TestMDLAsciiBinaryIntegration.test_ascii_to_binary_conversion
- TestMDLAsciiBinaryIntegration.test_binary_ascii_binary_roundtrip
- TestMDLAsciiBinaryIntegration.test_ascii_binary_ascii_roundtrip
- TestMDLAsciiComprehensive.test_complex_model_all_features
- TestMDLAsciiComprehensive.test_model_with_nested_hierarchy_and_controllers
- TestMDLAsciiComprehensive.test_animation_with_complex_node_structure
- TestMDLAsciiPerformance.test_write_performance_large_model
- TestMDLAsciiPerformance.test_read_performance_large_model
- TestMDLRoundTripAsciiToBinaryToAscii.test_roundtrip_character_model_reverse
- TestMDLRoundTripAsciiToBinaryToAscii.test_roundtrip_all_models_reverse
- TestMDLEqualityAndHashing.test_mdl_eq_hash_and_component_compare
- test_models_bif_roundtrip_eq_hash_pytest

### Libraries/PyKotor/tests/resource/formats/test_model_parsers_against_mdlops.py (2 tests)

- test_k1_models_random_sample
- test_k2_models_random_sample

### Libraries/PyKotor/tests/resource/formats/test_ncs.py (214 tests)

- TestNCSBinaryIO.test_binary_io
- TestNCSCompiler.test_enginecall
- TestNCSCompiler.test_enginecall_return_value
- TestNCSCompiler.test_enginecall_with_params
- TestNCSCompiler.test_enginecall_with_default_params
- TestNCSCompiler.test_enginecall_with_missing_params
- TestNCSCompiler.test_enginecall_with_too_many_params
- TestNCSCompiler.test_enginecall_delay_command_1
- TestNCSCompiler.test_enginecall_GetFirstObjectInShape_defaults
- TestNCSCompiler.test_enginecall_GetFactionEqual
- TestNCSCompiler.test_addop_int_int
- TestNCSCompiler.test_addop_float_float
- TestNCSCompiler.test_addop_string_string
- TestNCSCompiler.test_subop_int_int
- TestNCSCompiler.test_subop_float_float
- TestNCSCompiler.test_mulop_int_int
- TestNCSCompiler.test_mulop_float_float
- TestNCSCompiler.test_divop_int_int
- TestNCSCompiler.test_divop_float_float
- TestNCSCompiler.test_modop_int_int
- TestNCSCompiler.test_negop_int
- TestNCSCompiler.test_negop_float
- TestNCSCompiler.test_bidmas
- TestNCSCompiler.test_op_with_variables
- TestNCSCompiler.test_not_op
- TestNCSCompiler.test_logical_and_op
- TestNCSCompiler.test_logical_or_op
- TestNCSCompiler.test_logical_equals
- TestNCSCompiler.test_logical_notequals_op
- TestNCSCompiler.test_compare_greaterthan_op
- TestNCSCompiler.test_compare_greaterthanorequal_op
- TestNCSCompiler.test_compare_lessthan_op
- TestNCSCompiler.test_compare_lessthanorequal_op
- TestNCSCompiler.test_bitwise_or_op
- TestNCSCompiler.test_bitwise_xor_op
- TestNCSCompiler.test_bitwise_not_int
- TestNCSCompiler.test_bitwise_and_op
- TestNCSCompiler.test_bitwise_shiftleft_op
- TestNCSCompiler.test_bitwise_shiftright_op
- TestNCSCompiler.test_assignment
- TestNCSCompiler.test_assignment_complex
- TestNCSCompiler.test_assignment_string_constant
- TestNCSCompiler.test_assignment_string_enginecall
- TestNCSCompiler.test_addition_assignment_int_int
- TestNCSCompiler.test_addition_assignment_int_float
- TestNCSCompiler.test_addition_assignment_float_float
- TestNCSCompiler.test_addition_assignment_float_int
- TestNCSCompiler.test_addition_assignment_string_string
- TestNCSCompiler.test_subtraction_assignment_int_int
- TestNCSCompiler.test_subtraction_assignment_int_float
- TestNCSCompiler.test_subtraction_assignment_float_float
- TestNCSCompiler.test_subtraction_assignment_float_int
- TestNCSCompiler.test_multiplication_assignment
- TestNCSCompiler.test_division_assignment
- TestNCSCompiler.test_bitwise_and_assignment
- TestNCSCompiler.test_bitwise_or_assignment
- TestNCSCompiler.test_bitwise_xor_assignment
- TestNCSCompiler.test_bitwise_left_shift_assignment
- TestNCSCompiler.test_bitwise_right_shift_assignment
- TestNCSCompiler.test_bitwise_unsigned_right_shift_assignment
- TestNCSCompiler.test_bitwise_assignment_with_expression
- TestNCSCompiler.test_global_bitwise_assignment
- TestNCSCompiler.test_modulo_assignment
- TestNCSCompiler.test_bitwise_unsigned_right_shift_op
- TestNCSCompiler.test_const_global_declaration
- TestNCSCompiler.test_const_global_initialization
- TestNCSCompiler.test_const_local_declaration
- TestNCSCompiler.test_const_local_initialization
- TestNCSCompiler.test_const_assignment_error
- TestNCSCompiler.test_const_compound_assignment_error
- TestNCSCompiler.test_const_bitwise_assignment_error
- TestNCSCompiler.test_const_increment_error
- TestNCSCompiler.test_const_multi_declaration
- TestNCSCompiler.test_ternary_basic
- TestNCSCompiler.test_ternary_false_branch
- TestNCSCompiler.test_ternary_with_variables
- TestNCSCompiler.test_ternary_nested
- TestNCSCompiler.test_ternary_in_expression
- TestNCSCompiler.test_ternary_type_mismatch_error
- TestNCSCompiler.test_ternary_float_branches
- TestNCSCompiler.test_ternary_string_branches
- TestNCSCompiler.test_ternary_with_function_calls
- TestNCSCompiler.test_ternary_assignment
- TestNCSCompiler.test_ternary_precedence
- TestNCSCompiler.test_if
- TestNCSCompiler.test_if_multiple_conditions
- TestNCSCompiler.test_if_else
- TestNCSCompiler.test_if_else_if
- TestNCSCompiler.test_if_else_if_else
- TestNCSCompiler.test_single_statement_if
- TestNCSCompiler.test_single_statement_else_if_else
- TestNCSCompiler.test_while_loop
- TestNCSCompiler.test_while_loop_with_break
- TestNCSCompiler.test_while_loop_with_continue
- TestNCSCompiler.test_while_loop_scope
- TestNCSCompiler.test_do_while_loop
- TestNCSCompiler.test_do_while_loop_with_break
- TestNCSCompiler.test_do_while_loop_with_continue
- TestNCSCompiler.test_do_while_loop_scope
- TestNCSCompiler.test_for_loop
- TestNCSCompiler.test_for_loop_with_break
- TestNCSCompiler.test_for_loop_with_continue
- TestNCSCompiler.test_for_loop_scope
- TestNCSCompiler.test_switch_no_breaks
- TestNCSCompiler.test_switch_jump_over
- TestNCSCompiler.test_switch_with_breaks
- TestNCSCompiler.test_switch_with_default
- TestNCSCompiler.test_switch_scoped_blocks
- TestNCSCompiler.test_switch_scope_a
- TestNCSCompiler.test_switch_scope_b
- TestNCSCompiler.test_scope
- TestNCSCompiler.test_scoped_block
- TestNCSCompiler.test_multi_declarations
- TestNCSCompiler.test_local_declarations
- TestNCSCompiler.test_global_declarations
- TestNCSCompiler.test_global_initializations
- TestNCSCompiler.test_global_initialization_with_unary
- TestNCSCompiler.test_global_int_addition_assignment
- TestNCSCompiler.test_global_int_subtraction_assignment
- TestNCSCompiler.test_global_int_multiplication_assignment
- TestNCSCompiler.test_global_int_division_assignment
- TestNCSCompiler.test_declaration_int
- TestNCSCompiler.test_declaration_float
- TestNCSCompiler.test_declaration_string
- TestNCSCompiler.test_float_notations
- TestNCSCompiler.test_vector
- TestNCSCompiler.test_vector_notation
- TestNCSCompiler.test_vector_get_components
- TestNCSCompiler.test_vector_set_components
- TestNCSCompiler.test_struct_get_members
- TestNCSCompiler.test_struct_get_invalid_member
- TestNCSCompiler.test_struct_set_members
- TestNCSCompiler.test_prefix_increment_sp_int
- TestNCSCompiler.test_prefix_increment_bp_int
- TestNCSCompiler.test_postfix_increment_sp_int
- TestNCSCompiler.test_postfix_increment_bp_int
- TestNCSCompiler.test_prefix_decrement_sp_int
- TestNCSCompiler.test_prefix_decrement_bp_int
- TestNCSCompiler.test_postfix_decrement_sp_int
- TestNCSCompiler.test_postfix_decrement_bp_int
- TestNCSCompiler.test_prototype_no_args
- TestNCSCompiler.test_prototype_with_arg
- TestNCSCompiler.test_prototype_with_three_args
- TestNCSCompiler.test_prototype_with_many_args
- TestNCSCompiler.test_prototype_with_default_arg
- TestNCSCompiler.test_prototype_with_default_constant_arg
- TestNCSCompiler.test_prototype_missing_arg
- TestNCSCompiler.test_prototype_missing_arg_and_default
- TestNCSCompiler.test_prototype_default_before_required
- TestNCSCompiler.test_redefine_function
- TestNCSCompiler.test_double_prototype
- TestNCSCompiler.test_prototype_after_definition
- TestNCSCompiler.test_prototype_and_definition_param_mismatch
- TestNCSCompiler.test_prototype_and_definition_default_param_mismatch
- TestNCSCompiler.test_prototype_and_definition_return_mismatch
- TestNCSCompiler.test_call_undefined
- TestNCSCompiler.test_call_void_with_no_args
- TestNCSCompiler.test_call_void_with_one_arg
- TestNCSCompiler.test_call_void_with_two_args
- TestNCSCompiler.test_call_int_with_no_args
- TestNCSCompiler.test_call_int_with_no_args_and_forward_declared
- TestNCSCompiler.test_call_param_mismatch
- TestNCSCompiler.test_return
- TestNCSCompiler.test_return_parenthesis
- TestNCSCompiler.test_return_parenthesis_constant
- TestNCSCompiler.test_int_parenthesis_declaration
- TestNCSCompiler.test_include_builtin
- TestNCSCompiler.test_include_lookup
- TestNCSCompiler.test_nested_include
- TestNCSCompiler.test_missing_include
- TestNCSCompiler.test_imported_global_variable
- TestNCSCompiler.test_comment
- TestNCSCompiler.test_multiline_comment
- TestNCSCompiler.test_assignmentless_expression
- TestNCSCompiler.test_nop_statement
- TestNCSCompiler.test_vector_addition
- TestNCSCompiler.test_vector_subtraction
- TestNCSCompiler.test_vector_multiplication_float
- TestNCSCompiler.test_vector_division_float
- TestNCSCompiler.test_vector_compound_assignment_addition
- TestNCSCompiler.test_vector_compound_assignment_subtraction
- TestNCSCompiler.test_vector_compound_assignment_multiplication
- TestNCSCompiler.test_vector_compound_assignment_division
- TestNCSCompiler.test_nested_struct_access
- TestNCSCompiler.test_complex_expression_precedence
- TestNCSCompiler.test_expression_with_all_operators
- TestNCSInterpreter.test_peek_past_vector
- TestNCSInterpreter.test_move_negative
- TestNCSInterpreter.test_move_zero
- TestNCSInterpreter.test_copy_down_single
- TestNCSInterpreter.test_copy_down_many
- TestNCSOptimizer.test_no_op_optimizer
- TestNCSRoundtrip.test_nss_roundtrip
- TestNssNcsRoundtripGranular.test_roundtrip_primitives_and_structural_types
- TestNssNcsRoundtripGranular.test_roundtrip_arithmetic_operations
- TestNssNcsRoundtripGranular.test_roundtrip_bitwise_and_shift_operations
- TestNssNcsRoundtripGranular.test_roundtrip_logical_and_relational_operations
- TestNssNcsRoundtripGranular.test_roundtrip_compound_assignments
- TestNssNcsRoundtripGranular.test_roundtrip_increment_and_decrement
- TestNssNcsRoundtripGranular.test_roundtrip_if_else_nesting
- TestNssNcsRoundtripGranular.test_roundtrip_while_for_do_loops
- TestNssNcsRoundtripGranular.test_roundtrip_switch_case
- TestNssNcsRoundtripGranular.test_roundtrip_struct_usage
- TestNssNcsRoundtripGranular.test_roundtrip_function_definitions_and_returns
- TestNssNcsRoundtripGranular.test_roundtrip_action_queue_and_delays
- TestNssNcsRoundtripGranular.test_roundtrip_include_resolution
- TestNssNcsRoundtripGranular.test_roundtrip_tsl_specific_functionality
- test_binary_roundtrip_samples
- test_k1_undecompilable_roundtrip
- test_compile_a_galaxy_map_tsl
- test_compile_k_sup_galaxymap_tsl
- test_compile_a_galaxymap_tsl
- test_compile_tr_leave_ehawk_tsl
- test_compile_all_tsl_scripts_batch

### Libraries/PyKotor/tests/resource/formats/test_rim.py (5 tests)

- TestRIM.test_binary_io
- TestRIM.test_file_io
- TestRIM.test_read_raises
- TestRIM.test_write_raises
- TestRIM.test_malformed_header

### Libraries/PyKotor/tests/resource/formats/test_ssf.py (6 tests)

- TestSSF.test_binary_io
- TestSSF.test_file_io
- TestSSF.test_xml_io
- TestSSF.test_json_io
- TestSSF.test_read_raises
- TestSSF.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_tlk.py (6 tests)

- TestTLK.test_resize
- TestTLK.test_binary_io
- TestTLK.test_xml_io
- TestTLK.test_json_io
- TestTLK.test_read_raises
- TestTLK.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_tpc.py (6 tests)

- TestTPCData.test_dxt1_decompression_accuracy
- TestTPCData.test_dxt1_gradient_compression
- TestTPCData.test_rgb_to_rgba_precision
- TestTPCData.test_dxt1_block_boundaries
- TestTPCData.test_dxt1_rgba_preserves_one_bit_alpha
- TestTPCData.test_tpc_convert_dxt1_to_rgba_preserves_transparency

### Libraries/PyKotor/tests/resource/formats/test_twoda.py (6 tests)

- TestTwoDA.test_binary_io
- TestTwoDA.test_csv_io
- TestTwoDA.test_json_io
- TestTwoDA.test_read_raises
- TestTwoDA.test_write_raises
- TestTwoDA.test_row_max

### Libraries/PyKotor/tests/resource/formats/test_txi_data.py (5 tests)

- TestTXI.test_parse_blending_default
- TestTXI.test_parse_blending_additive
- TestTXI.test_parse_blending_punchthrough
- TestTXI.test_parse_blending_invalid
- TestTXI.test_parse_blending_case_insensitive

### Libraries/PyKotor/tests/resource/formats/test_txi_io.py (3 tests)

- test_read_txi
- test_write_txi
- test_bytes_txi

### Libraries/PyKotor/tests/resource/formats/test_utm.py (1 tests)

- TestUTM.test_io

### Libraries/PyKotor/tests/resource/formats/test_vis.py (4 tests)

- TestVIS.test_binary_io
- TestVIS.test_file_io
- TestVIS.test_read_raises
- TestVIS.test_write_raises

### Libraries/PyKotor/tests/resource/formats/test_wav.py (42 tests)

- TestWAVData.test_wav_creation_defaults
- TestWAVData.test_wav_creation_custom
- TestWAVData.test_wav_equality
- TestWAVData.test_wav_hash
- TestWAVData.test_wav_type_enum
- TestWAVData.test_wave_encoding_enum
- TestWAVIO.test_read_standard_wav_mono
- TestWAVIO.test_read_standard_wav_stereo
- TestWAVIO.test_read_different_sample_rates
- TestWAVIO.test_read_different_bit_depths
- TestWAVIO.test_read_from_bytes
- TestWAVIO.test_read_from_bytesio
- TestWAVIO.test_read_from_path_string
- TestWAVIO.test_read_from_pathlib_path
- TestWAVIO.test_read_raises_file_not_found
- TestWAVIO.test_read_raises_directory_error
- TestWAVIO.test_read_raises_invalid_format
- TestWAVIO.test_read_raises_missing_riff
- TestWAVIO.test_read_raises_missing_wave
- TestWAVIO.test_read_raises_missing_format_chunk
- TestWAVIO.test_read_raises_missing_data_chunk
- TestWAVWrite.test_write_wav_obfuscated
- TestWAVWrite.test_write_wav_deobfuscated
- TestWAVWrite.test_write_wav_to_file
- TestWAVWrite.test_write_wav_to_string_path
- TestWAVWrite.test_bytes_wav_obfuscated
- TestWAVWrite.test_bytes_wav_deobfuscated
- TestWAVWrite.test_bytes_wav_default
- TestWAVWrite.test_write_raises_directory_error
- TestWAVRoundTrip.test_roundtrip_obfuscated
- TestWAVRoundTrip.test_roundtrip_deobfuscated
- TestWAVRoundTrip.test_roundtrip_all_test_files
- TestWAVObfuscation.test_deobfuscate_clean_data
- TestWAVObfuscation.test_deobfuscate_short_data
- TestWAVObfuscation.test_obfuscate_sfx
- TestWAVObfuscation.test_obfuscate_vo
- TestWAVObfuscation.test_obfuscate_deobfuscate_roundtrip_sfx
- TestWAVObfuscation.test_obfuscate_deobfuscate_roundtrip_vo
- TestWAVEdgeCases.test_empty_wav_data
- TestWAVEdgeCases.test_wav_with_large_data
- TestWAVEdgeCases.test_wav_with_various_channels
- TestWAVEdgeCases.test_wav_with_various_sample_rates

### Libraries/PyKotor/tests/resource/formats/test_wok.py (1 tests)

- TestBWM.test_binary_io

### Libraries/PyKotor/tests/resource/generics/test_are.py (3 tests)

- TestARE.test_io_construct
- TestARE.test_io_reconstruct
- TestARE.test_file_io

### Libraries/PyKotor/tests/resource/generics/test_dlg.py (43 tests)

- TestDLG.test_k1_reconstruct
- TestDLG.test_k1_reconstruct_from_reconstruct
- TestDLG.test_k1_serialization
- TestDLG.test_k2_reconstruct
- TestDLG.test_k2_reconstruct_from_reconstruct
- TestDLG.test_io_construct
- TestDLG.test_file_io
- TestDLGEntrySerialization.test_dlg_entry_serialization_basic
- TestDLGEntrySerialization.test_dlg_entry_serialization_with_links
- TestDLGEntrySerialization.test_dlg_entry_serialization_all_attributes
- TestDLGEntrySerialization.test_dlg_entry_serialization_with_multilanguage_text
- TestDLGEntrySerialization.test_dlg_entry_with_nested_replies
- TestDLGEntrySerialization.test_dlg_entry_with_circular_reference
- TestDLGEntrySerialization.test_dlg_entry_with_multiple_levels
- TestDLGReplySerialization.test_dlg_reply_serialization_basic
- TestDLGReplySerialization.test_dlg_reply_serialization_with_links
- TestDLGReplySerialization.test_dlg_reply_serialization_all_attributes
- TestDLGReplySerialization.test_dlg_reply_with_nested_entries
- TestDLGReplySerialization.test_dlg_reply_with_circular_reference
- TestDLGReplySerialization.test_dlg_reply_with_multiple_levels
- TestDLGLinkSerialization.test_dlg_link_serialization_basic
- TestDLGLinkSerialization.test_dlg_link_serialization_with_node
- TestDLGLinkSerialization.test_dlg_link_serialization_all_attributes
- TestDLGLinkSerialization.test_dlg_link_with_nested_entries_and_replies
- TestDLGLinkSerialization.test_dlg_link_with_circular_references
- TestDLGLinkSerialization.test_dlg_link_with_multiple_levels
- TestDLGLinkSerialization.test_dlg_link_serialization_preserves_shared_nodes
- TestDLGLinkSerialization.test_dlg_link_iteration_traverses_all_descendants
- TestDLGAnimationSerialization.test_dlg_animation_serialization_basic
- TestDLGAnimationSerialization.test_dlg_animation_serialization_default
- TestDLGAnimationSerialization.test_dlg_animation_serialization_with_custom_values
- TestDLGStuntSerialization.test_dlg_stunt_serialization_basic
- TestDLGStuntSerialization.test_dlg_stunt_serialization_default
- TestDLGStuntSerialization.test_dlg_stunt_serialization_with_custom_values
- TestDLGGraphUtilities.test_find_paths_for_nodes_and_links
- TestDLGGraphUtilities.test_get_link_parent_and_partial_path
- TestDLGGraphUtilities.test_all_entries_and_replies_sorted_and_unique
- TestDLGGraphUtilities.test_calculate_links_and_nodes_counts_cycles_included
- TestDLGGraphUtilities.test_shift_item_and_bounds
- TestDLGGraphUtilities.test_node_dict_roundtrip_preserves_metadata
- TestDLGGraphUtilities.test_find_paths_respects_multiple_starters_and_link_parenting
- test_serialization_roundtrip_preserves_deep_chain
- test_shared_node_identity_survives_link_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_dlg_twine.py (12 tests)

- test_write_read_json
- test_write_read_html
- test_metadata_preservation
- test_passage_metadata
- test_link_preservation
- test_invalid_json
- test_invalid_html
- test_complex_dialog_structure
- test_comment_metadata_is_restored_into_twine_story
- test_first_starter_becomes_start_pid
- test_get_links_to_reports_sources
- test_metadata_comment_roundtrip_for_tag_colors_and_zoom

### Libraries/PyKotor/tests/resource/generics/test_fac.py (8 tests)

- TestFAC.test_gff_reconstruct
- TestFAC.test_io_construct
- TestFAC.test_io_reconstruct
- TestFAC.test_create_empty_fac
- TestFAC.test_create_faction_with_custom_parent
- TestFAC.test_reputation_ranges
- TestFAC.test_missing_field_defaults
- TestFAC.test_empty_lists_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_git.py (10 tests)

- TestGIT.test_k1_io_construct
- TestGIT.test_k2_io_construct
- TestGIT.test_k2_io_reconstruct
- TestGITSerializeStrictTyping.test_git_door_serialize_localized_string_stringref
- TestGITSerializeStrictTyping.test_git_door_serialize_linked_to_flags_enum_value
- TestGITSerializeStrictTyping.test_git_door_serialize_invalid_stringref
- TestGITSerializeStrictTyping.test_git_trigger_serialize_localized_string_stringref
- TestGITSerializeStrictTyping.test_git_door_serialize_all_fields
- TestGITSerializeStrictTyping.test_git_missing_area_properties_and_empty_lists
- TestGITSerializeStrictTyping.test_git_empty_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_gui.py (4 tests)

- TestGUI.test_io_construct
- TestGUI.test_io_reconstruct
- TestGUI.test_gui_missing_extent_and_controls_defaults
- TestGUI.test_gui_minimal_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_ifo.py (5 tests)

- TestIFO.test_gff_reconstruct
- TestIFO.test_io_construct
- TestIFO.test_io_reconstruct
- TestIFO.test_ifo_missing_field_defaults
- TestIFO.test_ifo_empty_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_jrl.py (5 tests)

- TestJRL.test_gff_reconstruct
- TestJRL.test_io_construct
- TestJRL.test_io_reconstruct
- TestJRL.test_jrl_missing_field_defaults
- TestJRL.test_jrl_empty_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_pth.py (5 tests)

- TestPTH.test_gff_reconstruct
- TestPTH.test_io_construct
- TestPTH.test_io_reconstruct
- TestPTH.test_pth_missing_field_defaults
- TestPTH.test_pth_empty_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_utc.py (5 tests)

- TestUTC.test_io_construct
- TestUTC.test_io_reconstruct
- TestUTC.test_file_io
- TestUTC.test_utc_missing_field_defaults
- TestUTC.test_utc_empty_roundtrip

### Libraries/PyKotor/tests/resource/generics/test_utd.py (4 tests)

- TestUTD.test_gff_reconstruct
- TestUTD.test_io_construct
- TestUTD.test_io_reconstruct
- TestUTD.test_file_io

### Libraries/PyKotor/tests/resource/generics/test_ute.py (3 tests)

- TestUTE.test_gff_reconstruct
- TestUTE.test_io_construct
- TestUTE.test_io_reconstruct

### Libraries/PyKotor/tests/resource/generics/test_uti.py (3 tests)

- TestUTI.test_gff_reconstruct
- TestUTI.test_io_construct
- TestUTI.test_io_reconstruct

### Libraries/PyKotor/tests/resource/generics/test_utp.py (4 tests)

- Test.test_gff_reconstruct
- Test.test_io_construct
- Test.test_io_reconstruct
- Test.test_file_io

### Libraries/PyKotor/tests/resource/generics/test_uts.py (4 tests)

- TestUTS.test_gff_reconstruct
- TestUTS.test_k1_gff_reconstruct
- TestUTS.test_io_construct
- TestUTS.test_io_reconstruct

### Libraries/PyKotor/tests/resource/generics/test_utt.py (3 tests)

- TestUTT.test_gff_reconstruct
- TestUTT.test_io_construct
- TestUTT.test_io_reconstruct

### Libraries/PyKotor/tests/resource/generics/test_utw.py (3 tests)

- TestUTW.test_gff_reconstruct
- TestUTW.test_io_construct
- TestUTW.test_io_reconstruct

### Libraries/PyKotor/tests/resource/test_replace_module_extensions.py (1 tests)

- TestReplaceModuleExtensions.test_replace_module_extensions

### Libraries/PyKotor/tests/resource/test_resource_from_path.py (16 tests)

- TestResourceType.test_resource_type_hashing
- TestResourceType.test_from_extension
- TestResourceType.test_from_id
- TestResourceIdentifier.test_hashing
- TestResourceIdentifier.test_from_path_mdl
- TestResourceIdentifier.test_from_path_tga
- TestResourceIdentifier.test_from_path_wav
- TestResourceIdentifier.test_from_path_tlk_xml
- TestResourceIdentifier.test_from_path_long_suffix_gff_xml
- TestResourceIdentifier.test_from_path_hidden_file
- TestResourceIdentifier.test_from_path_no_extension
- TestResourceIdentifier.test_from_path_long_extension
- TestResourceIdentifier.test_from_path_none_file_path
- TestResourceIdentifier.test_from_path_empty_file_path
- TestResourceIdentifier.test_from_path_invalid_extension
- TestResourceIdentifier.test_from_path_trailing_dot

### Libraries/PyKotor/tests/test_compile_tool.py (24 tests)

- TestDetectOS.test_detect_os_windows
- TestDetectOS.test_detect_os_mac
- TestDetectOS.test_detect_os_linux
- TestDetectOS.test_detect_os_unsupported
- TestPathSeparatorForData.test_path_separator_windows
- TestPathSeparatorForData.test_path_separator_mac
- TestPathSeparatorForData.test_path_separator_linux
- TestAddFlagValues.test_add_flag_values_single
- TestAddFlagValues.test_add_flag_values_multiple
- TestAddFlagValues.test_add_flag_values_empty
- TestComputeFinalExecutable.test_compute_final_executable_windows
- TestComputeFinalExecutable.test_compute_final_executable_mac
- TestComputeFinalExecutable.test_compute_final_executable_linux
- TestNormalizeAddData.test_normalize_add_data_windows_valid
- TestNormalizeAddData.test_normalize_add_data_unix_valid
- TestNormalizeAddData.test_normalize_add_data_windows_invalid
- TestNormalizeAddData.test_normalize_add_data_unix_invalid
- TestNormalizeAddData.test_normalize_add_data_windows_with_colon
- TestCompileToolIntegration.test_all_tools_have_valid_structure
- TestCompileToolIntegration.test_compile_tool_skips_venv_when_requested
- TestCompileToolIntegration.test_path_separator_compatibility
- TestCompileToolIntegration.test_compute_executable_compatibility
- TestCompileToolIntegration.test_python_version_compatibility
- TestToolSpecificCompilation.test_tool_entrypoints

### Libraries/PyKotor/tests/test_engine/test_mdl_loader.py (11 tests)

- TestMDLDataStructures.test_mdl_creation
- TestMDLDataStructures.test_mdl_node_creation
- TestMDLDataStructures.test_mdl_mesh_creation
- TestMDLDataStructures.test_mdl_animation_creation
- TestMDLDataStructures.test_mdl_controller_creation
- TestTangentSpaceCalculation.test_face_normal_calculation
- TestTangentSpaceCalculation.test_tangent_space_calculation
- TestTangentSpaceCalculation.test_tangent_space_orthogonality
- TestMDLHierarchy.test_node_hierarchy
- TestMDLHierarchy.test_all_nodes_traversal
- TestAnimationControllers.test_position_controller

### Libraries/PyKotor/tests/test_finder.py (3 tests)

- test_canonical_search_order
- test_find_result_identifier
- test_find_resource_no_query_returns_empty

### Libraries/PyKotor/tests/test_kaitai_generated_parity.py (2 tests)

- test_all_kaitai_generated_modules_import
- test_kaitai_generated_sources_have_no_http_urls

### Libraries/PyKotor/tests/test_markdown_validation.py (6 tests)

- test_markdownlint_compliance
- test_wiki_files_exist
- test_markdown_links_valid
- test_all_links_clickable
- test_no_overly_broad_hyperlinks
- test_no_self_referential_links

### Libraries/PyKotor/tests/test_utility/test_actions_dispatcher.py (11 tests)

- test_declarative_action_definitions
- test_actions_dispatcher_initialization
- test_declarative_action_execution
- test_multiprocessing_execution
- test_error_handling_in_declarative_actions
- test_integration_with_file_operations
- test_action_metadata_consistency
- test_async_flags_in_definitions
- test_memory_management_with_declarative_actions
- test_cross_platform_compatibility
- test_full_integration_workflow

### Libraries/PyKotor/tests/test_utility/test_actions_executor_strict_typing.py (4 tests)

- TestActionsExecutorStrictTyping.test_execute_task_with_existing_operation
- TestActionsExecutorStrictTyping.test_execute_task_with_nonexistent_operation
- TestActionsExecutorStrictTyping.test_file_operations_has_attributes
- TestActionsExecutorStrictTyping.test_execute_task_uses_getattr_not_object_getattribute

### Libraries/PyKotor/tests/test_utility/test_drag_drop_conformance.py (19 tests)

- TestFileDialogDragInitiation.test_drag_enabled_on_file_list
- TestFileDialogDragInitiation.test_selection_mode_allows_drag
- TestFileDialogDragInitiation.test_drag_drop_mode_set
- TestFileDialogDropAcceptance.test_accepts_drops
- TestFileDialogDropAcceptance.test_drag_enter_event_handled
- TestFileDialogDropAcceptance.test_accepts_file_urls
- TestFileDialogDragFeedback.test_drop_indicator_visible
- TestExplorerDragInitiation.test_drag_enabled_on_content_view
- TestExplorerDragInitiation.test_multi_selection_drag
- TestExplorerDropZones.test_content_area_accepts_drops
- TestExplorerDropZones.test_sidebar_accepts_drops
- TestExplorerDropZones.test_folder_items_are_drop_targets
- TestExplorerCopyMoveOperations.test_default_action_within_same_drive
- TestExplorerCopyMoveOperations.test_ctrl_modifier_forces_copy
- TestExplorerCopyMoveOperations.test_shift_modifier_forces_move
- TestCrossWidgetDragDrop.test_drag_between_explorers
- TestSidebarDragDrop.test_sidebar_item_click_navigates
- TestSidebarDragDrop.test_can_drag_folder_to_sidebar
- TestDragScrollBehavior.test_scroll_bars_present

### Libraries/PyKotor/tests/test_utility/test_dynamic_view.py (29 tests)

- TestDynamicStackedView.test_init_default_widgets
- TestDynamicStackedView.test_init_custom_widgets
- TestDynamicStackedView.test_set_widgets
- TestDynamicStackedView.test_all_views
- TestDynamicStackedView.test_all_widgets
- TestDynamicStackedView.test_current_view
- TestDynamicStackedView.test_list_view
- TestDynamicStackedView.test_tree_view
- TestDynamicStackedView.test_table_view
- TestDynamicStackedView.test_column_view
- TestDynamicStackedView.test_set_model
- TestDynamicStackedView.test_set_current_widget
- TestDynamicStackedView.test_switch_to_next_view
- TestDynamicStackedView.test_switch_to_previous_view
- TestDynamicStackedView.test_switch_to_next_view_at_end
- TestDynamicStackedView.test_switch_to_previous_view_at_start
- TestDynamicStackedView.test_set_root_index
- TestDynamicStackedView.test_root_index
- TestDynamicStackedView.test_clear_selection
- TestDynamicStackedView.test_selection_model
- TestDynamicStackedView.test_selected_indexes
- TestDynamicStackedView.test_select_all
- TestDynamicStackedView.test_update_icon_size
- TestDynamicStackedView.test_adjust_view_size
- TestDynamicStackedView.test_is_size_suitable_for_view
- TestDynamicStackedView.test_is_size_suitable_for_view_no_current_view
- TestDynamicStackedView.test_get_actual_view
- TestDynamicStackedView.test_get_actual_view_specific_type
- TestDynamicStackedView.test_wheel_event_with_ctrl

### Libraries/PyKotor/tests/test_utility/test_explorer_widget_components.py (57 tests)

- TestExplorerMainWindowStructure.test_explorer_is_main_window
- TestExplorerMainWindowStructure.test_explorer_has_menu_bar
- TestExplorerMainWindowStructure.test_explorer_has_status_bar
- TestExplorerMainWindowStructure.test_explorer_has_central_widget
- TestExplorerMainWindowStructure.test_explorer_minimum_size
- TestExplorerToolbars.test_has_navigation_toolbar
- TestExplorerToolbars.test_navigation_buttons_exist
- TestExplorerRibbon.test_ribbon_widget_exists
- TestExplorerRibbon.test_ribbon_has_tabs
- TestExplorerRibbon.test_ribbon_file_tab_exists
- TestExplorerRibbon.test_ribbon_home_tab_exists
- TestExplorerRibbon.test_ribbon_share_tab_exists
- TestExplorerRibbon.test_ribbon_view_tab_exists
- TestExplorerRibbonHomeTab.test_home_tab_has_copy_action
- TestExplorerRibbonHomeTab.test_home_tab_has_paste_action
- TestExplorerRibbonHomeTab.test_home_tab_has_cut_action
- TestExplorerRibbonHomeTab.test_home_tab_has_delete_action
- TestExplorerRibbonHomeTab.test_home_tab_has_rename_action
- TestExplorerRibbonViewTab.test_view_tab_has_extra_large_icons_action
- TestExplorerRibbonViewTab.test_view_tab_has_large_icons_action
- TestExplorerRibbonViewTab.test_view_tab_has_medium_icons_action
- TestExplorerRibbonViewTab.test_view_tab_has_small_icons_action
- TestExplorerRibbonViewTab.test_view_tab_has_list_action
- TestExplorerRibbonViewTab.test_view_tab_has_details_action
- TestExplorerRibbonViewTab.test_view_tab_has_tiles_action
- TestExplorerRibbonViewTab.test_view_tab_has_content_action
- TestNavigationPane.test_navigation_pane_exists
- TestNavigationPane.test_navigation_pane_visible_by_default
- TestNavigationPane.test_navigation_pane_can_be_hidden
- TestNavigationPane.test_navigation_pane_can_be_shown
- TestNavigationPane.test_navigation_pane_min_width
- TestNavigationPane.test_navigation_pane_has_tree_view
- TestNavigationPaneContent.test_navigation_pane_click_navigates
- TestContentArea.test_content_area_exists
- TestContentArea.test_content_shows_files
- TestContentArea.test_content_min_width
- TestContentAreaViewModes.test_can_switch_to_icons_view
- TestContentAreaViewModes.test_can_switch_to_list_view
- TestContentAreaViewModes.test_can_switch_to_details_view
- TestContentAreaViewModes.test_can_switch_to_tiles_view
- TestExplorerAddressBar.test_address_bar_exists
- TestExplorerAddressBar.test_address_bar_shows_path
- TestExplorerAddressBar.test_address_bar_height
- TestExplorerStatusBar.test_status_bar_exists
- TestExplorerStatusBar.test_status_bar_visible
- TestExplorerStatusBar.test_status_bar_height
- TestExplorerStatusBar.test_status_bar_shows_item_count
- TestExplorerKeyboardNavigation.test_alt_d_focuses_address_bar
- TestExplorerKeyboardNavigation.test_f4_opens_address_bar_dropdown
- TestExplorerKeyboardNavigation.test_backspace_goes_up
- TestExplorerKeyboardNavigation.test_enter_opens_selected_folder
- TestExplorerDragDrop.test_view_accepts_drops
- TestExplorerDragDrop.test_drag_enabled
- TestExplorerContextMenu.test_context_menu_policy
- TestExplorerSelection.test_selection_mode
- TestExplorerSelection.test_ctrl_a_selects_all
- TestExplorerSelection.test_click_selects_item

### Libraries/PyKotor/tests/test_utility/test_file_dialog_components.py (42 tests)

- TestAddressBarStructure.test_address_bar_exists
- TestAddressBarStructure.test_address_bar_is_visible
- TestAddressBarStructure.test_address_bar_height
- TestAddressBarStructure.test_address_bar_min_width
- TestAddressBarStructure.test_address_bar_shows_current_path
- TestAddressBarNavigation.test_can_navigate_to_directory
- TestAddressBarNavigation.test_path_completion
- TestAddressBarNavigation.test_breadcrumb_navigation
- TestAddressBarKeyboard.test_address_bar_focusable
- TestAddressBarKeyboard.test_escape_clears_edit
- TestSearchBoxStructure.test_search_box_exists
- TestSearchBoxStructure.test_search_box_visible
- TestSearchBoxStructure.test_search_box_height
- TestSearchBoxStructure.test_search_box_placeholder
- TestSearchBoxFunctionality.test_search_filters_files
- TestSearchBoxFunctionality.test_search_clear_restores_list
- TestSearchBoxFunctionality.test_search_realtime_filtering
- TestPreviewPaneStructure.test_preview_pane_exists
- TestPreviewPaneStructure.test_preview_pane_can_be_shown
- TestPreviewPaneStructure.test_preview_pane_can_be_hidden
- TestPreviewPaneStructure.test_preview_pane_min_width
- TestPreviewPaneContent.test_preview_updates_on_selection
- TestPreviewPaneContent.test_preview_shows_file_info
- TestSidebarStructure.test_sidebar_exists
- TestSidebarStructure.test_sidebar_visible_by_default
- TestSidebarStructure.test_sidebar_min_width
- TestSidebarStructure.test_sidebar_max_width
- TestSidebarContent.test_sidebar_has_tree_or_list
- TestSidebarContent.test_sidebar_shows_standard_locations
- TestSidebarNavigation.test_sidebar_click_navigates
- TestFileListStructure.test_file_list_exists
- TestFileListStructure.test_file_list_shows_files
- TestFileListStructure.test_file_list_min_width
- TestFileListDetailView.test_detail_view_has_columns
- TestFileListDetailView.test_detail_view_column_order
- TestFileListSelection.test_single_selection_mode
- TestFileListSelection.test_multi_selection_mode
- TestBottomControlsStructure.test_filename_edit_exists
- TestBottomControlsStructure.test_open_button_exists
- TestBottomControlsStructure.test_cancel_button_exists
- TestBottomControlsBehavior.test_filename_updates_on_selection
- TestBottomControlsBehavior.test_can_type_filename

### Libraries/PyKotor/tests/test_utility/test_filesystem_components.py (110 tests)

- TestPyQExtendedInformation.test_extended_information_constructor_default
- TestPyQExtendedInformation.test_extended_information_constructor_with_fileinfo
- TestPyQExtendedInformation.test_extended_information_directory
- TestPyQExtendedInformation.test_extended_information_equality
- TestPyQExtendedInformation.test_extended_information_permissions
- TestPyQExtendedInformation.test_extended_information_last_modified
- TestPyQExtendedInformation.test_extended_information_size
- TestPyQExtendedInformation.test_extended_information_is_hidden
- TestPyQExtendedInformation.test_extended_information_is_symlink
- TestPyQExtendedInformation.test_extended_information_type_enum
- TestPyQExtendedInformation.test_extended_information_icon
- TestPyQExtendedInformation.test_extended_information_display_type
- TestPyFileSystemNode.test_node_constructor_default
- TestPyFileSystemNode.test_node_constructor_with_filename
- TestPyFileSystemNode.test_node_constructor_with_parent
- TestPyFileSystemNode.test_node_size
- TestPyFileSystemNode.test_node_type
- TestPyFileSystemNode.test_node_permissions
- TestPyFileSystemNode.test_node_is_dir
- TestPyFileSystemNode.test_node_is_file
- TestPyFileSystemNode.test_node_is_hidden
- TestPyFileSystemNode.test_node_comparison_operators
- TestPyFileSystemNode.test_node_visible_location
- TestPyFileSystemNode.test_node_populate
- TestPyFileSystemNode.test_node_file_info
- TestPyFileSystemModelSorter.test_sorter_constructor
- TestPyFileSystemModelSorter.test_sorter_with_different_columns
- TestPyFileSystemModelSorter.test_sorter_compare_nodes_name_column
- TestPyFileSystemModelSorter.test_sorter_compare_nodes_size_column
- TestPyFileSystemModelSorter.test_sorter_compare_nodes_type_column
- TestPyFileSystemModelSorter.test_sorter_compare_nodes_time_column
- TestPyFileSystemModelSorter.test_sorter_call_operator
- TestPyFileSystemWatcher.test_watcher_constructor
- TestPyFileSystemWatcher.test_watcher_add_path_file
- TestPyFileSystemWatcher.test_watcher_add_path_directory
- TestPyFileSystemWatcher.test_watcher_remove_path
- TestPyFileSystemWatcher.test_watcher_file_changed_signal
- TestPyFileSystemWatcher.test_watcher_directory_changed_signal
- TestPyFileSystemWatcher.test_watcher_add_path_nonexistent
- TestPyFileSystemWatcher.test_watcher_files_method
- TestPyFileSystemWatcher.test_watcher_directories_method
- TestPyFileInfoGatherer.test_gatherer_constructor
- TestPyFileInfoGatherer.test_gatherer_icon_provider
- TestPyFileInfoGatherer.test_gatherer_set_icon_provider
- TestPyFileInfoGatherer.test_gatherer_resolve_symlinks
- TestPyFileInfoGatherer.test_gatherer_set_resolve_symlinks
- TestPyFileInfoGatherer.test_gatherer_is_watching
- TestPyFileInfoGatherer.test_gatherer_set_watching
- TestPyFileInfoGatherer.test_gatherer_updates_signal
- TestPyFileInfoGatherer.test_gatherer_new_list_of_files_signal
- TestPyFileInfoGatherer.test_gatherer_watch_paths
- TestPyFileInfoGatherer.test_gatherer_unwatch_paths
- TestPyFileSystemModel.test_model_index_path
- TestPyFileSystemModel.test_model_root_path
- TestPyFileSystemModel.test_model_read_only
- TestPyFileSystemModel.test_model_icon_provider
- TestPyFileSystemModel.test_model_null_icon_provider
- TestPyFileSystemModel.test_model_row_count
- TestPyFileSystemModel.test_model_rows_inserted
- TestPyFileSystemModel.test_model_filters
- TestPyFileSystemModel.test_model_name_filters
- TestPyFileSystemModel.test_model_sort
- TestPyFileSystemModel.test_model_file_name
- TestPyFileSystemModel.test_model_file_path
- TestPyFileSystemModel.test_model_file_info
- TestFilesystemComponentsIntegration.test_dialog_uses_filesystem_model
- TestFilesystemComponentsIntegration.test_dialog_uses_proxy_model
- TestFilesystemComponentsIntegration.test_dialog_search_filters_proxy
- TestFilesystemComponentsIntegration.test_dialog_address_bar_syncs
- TestComponentStateConsistency.test_pyfilesystemmodel_state_consistency
- TestComponentStateConsistency.test_pyfileinfogatherer_state_consistency
- TestComponentStateConsistency.test_pyfilesystemnode_state_consistency
- TestComponentEdgeCases.test_extended_information_nonexistent_file
- TestComponentEdgeCases.test_filesystem_node_empty_filename
- TestComponentEdgeCases.test_sorter_invalid_column
- TestComponentEdgeCases.test_watcher_duplicate_paths
- TestComponentEdgeCases.test_model_invalid_path
- TestComponentPerformance.test_model_large_directory
- TestComponentPerformance.test_watcher_many_paths
- TestPyFileSystemModelAdvanced.test_model_rows_removed
- TestPyFileSystemModelAdvanced.test_model_set_data
- TestPyFileSystemModelAdvanced.test_model_sort_persistent_index
- TestPyFileSystemModelAdvanced.test_model_mkdir
- TestPyFileSystemModelAdvanced.test_model_delete_file
- TestPyFileSystemModelAdvanced.test_model_delete_directory
- TestPyFileSystemModelAdvanced.test_model_case_sensitivity
- TestPyFileSystemModelAdvanced.test_model_dirs_before_files
- TestPyFileSystemModelAdvanced.test_model_role_names
- TestPyFileSystemModelAdvanced.test_model_permissions
- TestPyFileSystemModelAdvanced.test_model_do_not_unwatch_on_failed_rmdir
- TestPyQFileSystemModelNodePathKey.test_node_path_key_constructor
- TestPyQFileSystemModelNodePathKey.test_node_path_key_equality_case_insensitive_windows
- TestPyQFileSystemModelNodePathKey.test_node_path_key_hash_case_insensitive_windows
- TestPyQFileSystemModelNodePathKey.test_node_path_key_with_string
- TestPyFileInfo.test_pyfileinfo_constructor_default
- TestPyFileInfo.test_pyfileinfo_constructor_with_file
- TestPyFileInfo.test_pyfileinfo_absolute_path
- TestPyFileInfo.test_pyfileinfo_base_name
- TestPyFileInfo.test_pyfileinfo_suffix
- TestAllComponentsIntegration.test_fileinfogatherer_with_watcher
- TestAllComponentsIntegration.test_filesystemmodel_with_gatherer
- TestAllComponentsIntegration.test_all_components_state_consistency
- TestComponentEdgeCasesAdvanced.test_extended_information_symlink
- TestComponentEdgeCasesAdvanced.test_filesystem_node_without_info
- TestComponentEdgeCasesAdvanced.test_filesystem_node_children
- TestComponentEdgeCasesAdvanced.test_watcher_empty_path
- TestComponentEdgeCasesAdvanced.test_model_invalid_root_path
- TestComponentSignals.test_filesystemmodel_all_signals
- TestComponentSignals.test_fileinfogatherer_all_signals
- TestComponentBehavior.test_model_filter_combinations

### Libraries/PyKotor/tests/test_utility/test_fluent_design_conformance.py (19 tests)

- TestRibbonVisualConformance.test_ribbon_tab_widget_exists
- TestRibbonVisualConformance.test_ribbon_tab_count
- TestRibbonVisualConformance.test_ribbon_tab_names
- TestRibbonVisualConformance.test_ribbon_large_button_size
- TestRibbonVisualConformance.test_ribbon_small_button_height
- TestControlVisualConformance.test_button_minimum_width
- TestControlVisualConformance.test_line_edit_height
- TestControlVisualConformance.test_combobox_height
- TestIconSizeConformance.test_small_icon_size
- TestIconSizeConformance.test_medium_icon_size
- TestIconSizeConformance.test_large_icon_size
- TestIconSizeConformance.test_extra_large_icon_size
- TestSplitterConformance.test_splitter_handle_width
- TestStatusBarConformance.test_status_bar_height
- TestTreeViewConformance.test_tree_view_header_visible
- TestTreeViewConformance.test_tree_view_indentation
- TestListViewConformance.test_list_view_icon_mode_spacing
- TestListViewConformance.test_list_view_list_mode_layout
- TestScrollbarConformance.test_scrollbar_width

### Libraries/PyKotor/tests/test_utility/test_keyboard_accessibility_conformance.py (26 tests)

- TestFileDialogTabNavigation.test_tab_moves_focus
- TestFileDialogTabNavigation.test_shift_tab_moves_focus_backward
- TestFileDialogTabNavigation.test_all_interactive_elements_focusable
- TestFileDialogKeyboardShortcuts.test_alt_d_focuses_address_bar
- TestFileDialogKeyboardShortcuts.test_escape_closes_dialog
- TestFileDialogKeyboardShortcuts.test_f5_refreshes
- TestFileDialogKeyboardShortcuts.test_ctrl_a_selects_all
- TestFileDialogArrowNavigation.test_arrow_keys_navigate_list
- TestFileDialogArrowNavigation.test_enter_opens_folder
- TestExplorerTabNavigation.test_tab_navigates_through_ui
- TestExplorerTabNavigation.test_focus_ring_visible
- TestExplorerKeyboardShortcuts.test_backspace_navigates_up
- TestExplorerKeyboardShortcuts.test_f5_refreshes_view
- TestExplorerKeyboardShortcuts.test_f2_renames_selected_item
- TestExplorerKeyboardShortcuts.test_alt_left_goes_back
- TestExplorerRibbonKeyboard.test_ribbon_tabs_keyboard_accessible
- TestFileDialogAccessibility.test_dialog_has_accessible_name
- TestFileDialogAccessibility.test_buttons_have_accessible_names
- TestFileDialogAccessibility.test_inputs_have_accessible_descriptions
- TestExplorerAccessibility.test_explorer_has_accessible_name
- TestExplorerAccessibility.test_toolbar_buttons_accessible
- TestFocusManagement.test_dialog_captures_initial_focus
- TestFocusManagement.test_focus_does_not_escape_dialog
- TestFocusManagement.test_escape_releases_focus_correctly
- TestMinimumTargetSize.test_buttons_meet_minimum_size
- TestMinimumTargetSize.test_toolbar_buttons_meet_minimum_size

### Libraries/PyKotor/tests/test_utility/test_mutable_str_strict_typing.py (4 tests)

- TestMutableStrStrictTyping.test_attribute_forwarding_uses_getattr
- TestMutableStrStrictTyping.test_hasattr_checks_for_compatibility_methods
- TestMutableStrStrictTyping.test_removeprefix_if_not_available
- TestMutableStrStrictTyping.test_removesuffix_if_not_available

### Libraries/PyKotor/tests/test_utility/test_pixel_perfect_layout.py (20 tests)

- TestFileDialogNavigationLayout.test_navigation_bar_height
- TestFileDialogNavigationLayout.test_navigation_button_size
- TestFileDialogAddressBarLayout.test_address_bar_height
- TestFileDialogAddressBarLayout.test_address_bar_minimum_width
- TestFileDialogSearchBoxLayout.test_search_box_height
- TestFileDialogSearchBoxLayout.test_search_box_width_constraints
- TestFileDialogSidebarLayout.test_sidebar_minimum_width
- TestFileDialogSidebarLayout.test_sidebar_maximum_width
- TestFileDialogSidebarLayout.test_sidebar_default_width
- TestFileDialogBottomControlsLayout.test_button_dimensions
- TestFileDialogBottomControlsLayout.test_line_edit_height
- TestFileDialogBottomControlsLayout.test_combobox_height
- TestExplorerRibbonLayout.test_ribbon_tab_height
- TestExplorerRibbonLayout.test_ribbon_tab_minimum_width
- TestExplorerSidebarLayout.test_sidebar_minimum_width
- TestExplorerStatusBarLayout.test_status_bar_height
- TestResponsiveFileDialogLayout.test_minimum_size_respected
- TestResponsiveFileDialogLayout.test_sidebar_resizes_with_dialog
- TestResponsiveExplorerLayout.test_minimum_window_size
- TestResponsiveExplorerLayout.test_content_area_grows_with_window

### Libraries/PyKotor/tests/test_utility/test_pyfileinfogatherer.py (15 tests)

- test_set_resolve_symlinks
- test_run_abort
- test_drive_added
- test_drive_removed
- test_fetch_extended_information_boiler
- test_fetch_extended_information
- test_update_file
- test_watched_files
- test_watched_directories
- test_create_watcher
- test_unwatch_paths
- test_clear
- test_remove_path
- test_list
- test_get_file_infos

### Libraries/PyKotor/tests/test_utility/test_qfiledialog.py (92 tests)

- test_constructor_default
- test_constructor_with_parent
- test_constructor_with_caption
- test_constructor_with_directory
- test_constructor_with_filter
- test_file_mode_set_get
- test_file_mode_with_accept_mode
- test_accept_mode_set_get
- test_view_mode_set_get
- test_view_mode_switching
- test_directory_set_get
- test_directory_with_qdir
- test_directory_url_set_get
- test_directory_edge_cases
- test_name_filter_set_get
- test_name_filters_set_get
- test_select_name_filter
- test_mime_type_filters
- test_empty_name_filter
- test_empty_name_filters_list
- test_option_set_test
- test_options_combinations
- test_default_suffix
- test_filter_set_get
- test_select_file
- test_select_file_nonexistent
- test_select_file_empty_string
- test_select_url
- test_get_open_file_name
- test_get_save_file_name
- test_get_open_file_names
- test_get_existing_directory
- test_get_open_file_url
- test_get_open_file_urls
- test_get_save_file_url
- test_get_existing_directory_url
- test_current_changed_signal
- test_directory_entered_signal
- test_file_selected_signal
- test_files_selected_signal
- test_filter_selected_signal
- test_url_selected_signal
- test_urls_selected_signal
- test_current_url_changed_signal
- test_directory_url_entered_signal
- test_history_set_get
- test_history_empty
- test_history_with_none_values
- test_sidebar_urls_set_get
- test_sidebar_urls_empty
- test_label_text_set_get
- test_label_text_empty
- test_icon_provider_set_get
- test_icon_provider_none
- test_item_delegate_set_get
- test_item_delegate_none
- test_proxy_model_set_get
- test_proxy_model_none
- test_save_state
- test_restore_state
- test_restore_state_invalid
- test_restore_state_bytes
- test_restore_state_empty
- test_supported_schemes_set_get
- test_supported_schemes_empty
- test_supported_schemes_with_none
- test_open_with_slot
- test_open_without_slot
- test_select_file_invalid_path
- test_set_directory_invalid
- test_open_dir_navigates_in_app
- test_set_directory_url_invalid
- test_empty_name_filter_edge_cases
- test_filter_with_special_characters
- test_mode_combinations
- test_options_combinations_with_modes
- test_static_methods_with_various_captions
- test_static_methods_with_various_directories
- test_static_methods_with_various_filters
- test_all_three_implementations_identical_state
- test_state_save_restore_across_implementations
- test_all_properties_accessible
- test_complete_roundtrip_file_selection
- test_complete_roundtrip_directory_selection
- test_extended_has_address_bar
- test_extended_has_search_filter
- test_extended_has_ribbons
- test_extended_search_filter_works
- test_change_event_handling
- test_change_event_none
- test_all_methods_callable
- test_static_method_parameter_combinations

### Libraries/PyKotor/tests/test_utility/test_qfiledialog2.py (34 tests)

- TestQFileDialog2.test_listRoot
- TestQFileDialog2.test_heapCorruption
- TestQFileDialog2.test_deleteDirAndFiles
- TestQFileDialog2.test_filter
- TestQFileDialog2.test_showNameFilterDetails
- TestQFileDialog2.test_unc
- TestQFileDialog2.test_emptyUncPath
- TestQFileDialog2.test_task143519_deleteAndRenameActionBehavior
- TestQFileDialog2.test_task178897_minimumSize
- TestQFileDialog2.test_task180459_lastDirectory_data
- TestQFileDialog2.test_task180459_lastDirectory
- TestQFileDialog2.test_settingsCompatibility_data
- TestQFileDialog2.test_settingsCompatibility
- TestQFileDialog2.test_task227930_correctNavigationKeyboardBehavior
- TestQFileDialog2.test_task226366_lowerCaseHardDriveWindows
- TestQFileDialog2.test_completionOnLevelAfterRoot
- TestQFileDialog2.test_task233037_selectingDirectory
- TestQFileDialog2.test_task235069_hideOnEscape_data
- TestQFileDialog2.test_task235069_hideOnEscape
- TestQFileDialog2.test_task236402_dontWatchDeletedDir
- TestQFileDialog2.test_task203703_returnProperSeparator
- TestQFileDialog2.test_task228844_ensurePreviousSorting
- TestQFileDialog2.test_task239706_editableFilterCombo
- TestQFileDialog2.test_task218353_relativePaths
- TestQFileDialog2.test_task251321_sideBarHiddenEntries
- TestQFileDialog2.test_task251341_sideBarRemoveEntries
- TestQFileDialog2.test_task254490_selectFileMultipleTimes
- TestQFileDialog2.test_task257579_sideBarWithNonCleanUrls
- TestQFileDialog2.test_task259105_filtersCornerCases
- TestQFileDialog2.test_QTBUG4419_lineEditSelectAll
- TestQFileDialog2.test_QTBUG6558_showDirsOnly
- TestQFileDialog2.test_QTBUG4842_selectFilterWithHideNameFilterDetails
- TestQFileDialog2.test_dontShowCompleterOnRoot
- TestQFileDialog2.test_nameFilterParsing_data

### Libraries/PyKotor/tests/test_utility/test_qfiledialogextended.py (11 tests)

- TestQFileDialogExtended.test_extended_rows_inserted
- TestQFileDialogExtended.test_address_bar_syncs_directory
- TestQFileDialogExtended.test_search_filter_updates_proxy
- TestQFileDialogExtended.test_search_filter_clear
- TestQFileDialogExtended.test_proxy_model_is_attached
- TestQFileDialogExtended.test_context_menu_dispatcher_exists
- TestQFileDialogExtended.test_context_menu_creation
- TestQFileDialogExtended.test_view_mode_buttons_switch
- TestQFileDialogExtended.test_drop_in_api_compatibility
- TestQFileDialogExtended.test_directory_entered_signal_updates_address
- TestQFileDialogExtended.test_address_bar_path_changed_signal

### Libraries/PyKotor/tests/test_utility/test_qfiledialogextended_comprehensive.py (112 tests)

- TestQFileDialogExtendedComprehensive.test_constructor_default
- TestQFileDialogExtendedComprehensive.test_constructor_with_parent
- TestQFileDialogExtendedComprehensive.test_constructor_with_caption
- TestQFileDialogExtendedComprehensive.test_constructor_with_directory
- TestQFileDialogExtendedComprehensive.test_constructor_with_filter
- TestQFileDialogExtendedComprehensive.test_constructor_full_args
- TestQFileDialogExtendedComprehensive.test_ui_components_exist
- TestQFileDialogExtendedComprehensive.test_views_exist
- TestQFileDialogExtendedComprehensive.test_proxy_model_setup
- TestQFileDialogExtendedComprehensive.test_sidebar_exists
- TestQFileDialogExtendedComprehensive.test_splitter_exists
- TestQFileDialogExtendedComprehensive.test_file_mode_any_file
- TestQFileDialogExtendedComprehensive.test_file_mode_existing_file
- TestQFileDialogExtendedComprehensive.test_file_mode_existing_files
- TestQFileDialogExtendedComprehensive.test_file_mode_directory
- TestQFileDialogExtendedComprehensive.test_file_mode_switching
- TestQFileDialogExtendedComprehensive.test_accept_mode_open
- TestQFileDialogExtendedComprehensive.test_accept_mode_save
- TestQFileDialogExtendedComprehensive.test_accept_mode_switching
- TestQFileDialogExtendedComprehensive.test_view_mode_list
- TestQFileDialogExtendedComprehensive.test_view_mode_detail
- TestQFileDialogExtendedComprehensive.test_view_mode_switching_list_to_detail
- TestQFileDialogExtendedComprehensive.test_view_mode_switching_detail_to_list
- TestQFileDialogExtendedComprehensive.test_view_mode_buttons
- TestQFileDialogExtendedComprehensive.test_set_directory
- TestQFileDialogExtendedComprehensive.test_directory_changed_signal
- TestQFileDialogExtendedComprehensive.test_navigate_to_nested_directory
- TestQFileDialogExtendedComprehensive.test_navigate_up_directory
- TestQFileDialogExtendedComprehensive.test_navigate_back_history
- TestQFileDialogExtendedComprehensive.test_navigate_forward_history
- TestQFileDialogExtendedComprehensive.test_address_bar_synchronization
- TestQFileDialogExtendedComprehensive.test_address_bar_manual_path_change
- TestQFileDialogExtendedComprehensive.test_select_file
- TestQFileDialogExtendedComprehensive.test_select_files_multiple
- TestQFileDialogExtendedComprehensive.test_selected_files_signal
- TestQFileDialogExtendedComprehensive.test_search_filter_updates_proxy_model
- TestQFileDialogExtendedComprehensive.test_search_filter_case_insensitive
- TestQFileDialogExtendedComprehensive.test_search_filter_clear
- TestQFileDialogExtendedComprehensive.test_search_filter_multiple_searches
- TestQFileDialogExtendedComprehensive.test_search_filter_with_special_characters
- TestQFileDialogExtendedComprehensive.test_set_name_filter
- TestQFileDialogExtendedComprehensive.test_set_multiple_name_filters
- TestQFileDialogExtendedComprehensive.test_filter_selected_signal
- TestQFileDialogExtendedComprehensive.test_context_menu_on_file
- TestQFileDialogExtendedComprehensive.test_context_menu_on_directory
- TestQFileDialogExtendedComprehensive.test_context_menu_has_open_action
- TestQFileDialogExtendedComprehensive.test_ribbon_exists
- TestQFileDialogExtendedComprehensive.test_ribbon_actions_defined
- TestQFileDialogExtendedComprehensive.test_ribbon_list_view_action
- TestQFileDialogExtendedComprehensive.test_ribbon_detail_view_action
- TestQFileDialogExtendedComprehensive.test_ribbon_navigation_pane_toggle
- TestQFileDialogExtendedComprehensive.test_keyboard_navigation_arrow_keys
- TestQFileDialogExtendedComprehensive.test_keyboard_enter_opens_folder
- TestQFileDialogExtendedComprehensive.test_keyboard_backspace_parent_directory
- TestQFileDialogExtendedComprehensive.test_keyboard_home_key
- TestQFileDialogExtendedComprehensive.test_keyboard_end_key
- TestQFileDialogExtendedComprehensive.test_keyboard_ctrl_l_address_bar
- TestQFileDialogExtendedComprehensive.test_mouse_click_on_folder
- TestQFileDialogExtendedComprehensive.test_mouse_double_click_opens_folder
- TestQFileDialogExtendedComprehensive.test_mouse_right_click_context_menu
- TestQFileDialogExtendedComprehensive.test_mouse_ctrl_click_multiple_selection
- TestQFileDialogExtendedComprehensive.test_option_dont_use_native_dialog
- TestQFileDialogExtendedComprehensive.test_option_show_dirs_only
- TestQFileDialogExtendedComprehensive.test_option_read_only
- TestQFileDialogExtendedComprehensive.test_option_hide_name_filter_details
- TestQFileDialogExtendedComprehensive.test_multiple_options_combined
- TestQFileDialogExtendedComprehensive.test_current_directory_persistence
- TestQFileDialogExtendedComprehensive.test_selected_files_persistence
- TestQFileDialogExtendedComprehensive.test_view_mode_persistence
- TestQFileDialogExtendedComprehensive.test_navigation_sequence_multiple_folders
- TestQFileDialogExtendedComprehensive.test_navigation_and_file_selection_sequence
- TestQFileDialogExtendedComprehensive.test_view_switching_with_navigation
- TestQFileDialogExtendedComprehensive.test_search_with_navigation
- TestQFileDialogExtendedComprehensive.test_preview_pane_initialization
- TestQFileDialogExtendedComprehensive.test_preview_pane_toggle_show
- TestQFileDialogExtendedComprehensive.test_preview_pane_toggle_hide
- TestQFileDialogExtendedComprehensive.test_preview_pane_updates_on_selection
- TestQFileDialogExtendedComprehensive.test_sidebar_visibility
- TestQFileDialogExtendedComprehensive.test_sidebar_toggle_via_ribbon
- TestQFileDialogExtendedComprehensive.test_set_extra_large_icons
- TestQFileDialogExtendedComprehensive.test_set_large_icons
- TestQFileDialogExtendedComprehensive.test_set_medium_icons
- TestQFileDialogExtendedComprehensive.test_set_small_icons
- TestQFileDialogExtendedComprehensive.test_set_default_suffix
- TestQFileDialogExtendedComprehensive.test_default_suffix_multiple_changes
- TestQFileDialogExtendedComprehensive.test_icon_provider_exists
- TestQFileDialogExtendedComprehensive.test_set_icon_provider
- TestQFileDialogExtendedComprehensive.test_item_delegate_exists
- TestQFileDialogExtendedComprehensive.test_set_item_delegate
- TestQFileDialogExtendedComprehensive.test_label_text_accept_label
- TestQFileDialogExtendedComprehensive.test_label_text_reject_label
- TestQFileDialogExtendedComprehensive.test_label_text_file_name_label
- TestQFileDialogExtendedComprehensive.test_resolve_symlinks_setting
- TestQFileDialogExtendedComprehensive.test_history_empty_initially
- TestQFileDialogExtendedComprehensive.test_history_navigation_back_forward
- TestQFileDialogExtendedComprehensive.test_current_changed_signal
- TestQFileDialogExtendedComprehensive.test_sequence_navigate_select_filter_switch_view
- TestQFileDialogExtendedComprehensive.test_sequence_keyboard_mouse_mixed_interaction
- TestQFileDialogExtendedComprehensive.test_stress_rapid_navigation
- TestQFileDialogExtendedComprehensive.test_stress_rapid_view_switching
- TestQFileDialogExtendedComprehensive.test_stress_rapid_search_filtering
- TestQFileDialogExtendedComprehensive.test_navigate_to_nonexistent_directory
- TestQFileDialogExtendedComprehensive.test_select_nonexistent_file
- TestQFileDialogExtendedComprehensive.test_empty_directory_browsing
- TestQFileDialogExtendedComprehensive.test_special_characters_in_path
- TestQFileDialogExtendedComprehensive.test_proxy_model_filters_correctly
- TestQFileDialogExtendedComprehensive.test_proxy_model_case_insensitivity
- TestQFileDialogExtendedComprehensive.test_proxy_model_with_name_filters
- TestQFileDialogExtendedComprehensive.test_dispatcher_initialized
- TestQFileDialogExtendedComprehensive.test_dispatcher_has_menus
- TestQFileDialogExtendedComprehensive.test_executor_initialized
- TestQFileDialogExtendedComprehensive.test_windows11_styling_applied

### Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py (4 tests)

- TestRegistryStrictTyping.test_resolve_reg_key_with_valid_root
- TestRegistryStrictTyping.test_resolve_reg_key_with_invalid_root
- TestRegistryStrictTyping.test_resolve_registry_key_uses_getattr
- TestRegistryStrictTyping.test_winreg_has_standard_roots

### Libraries/PyKotor/tests/test_utility/test_string_util_strict_typing.py (4 tests)

- TestStringUtilStrictTyping.test_setattr_prevents_modifying_existing_attribute
- TestStringUtilStrictTyping.test_setattr_allows_setting_new_attribute
- TestStringUtilStrictTyping.test_setattr_uses_hasattr_for_immutability_check
- TestStringUtilStrictTyping.test_immutability_check_works_with_slots

### Libraries/PyKotor/tests/test_utility/test_sys_attributes_strict_typing.py (6 tests)

- TestSysAttributesStrictTyping.test_is_frozen_uses_getattr
- TestSysAttributesStrictTyping.test_is_frozen_app_process_uses_getattr
- TestSysAttributesStrictTyping.test_is_frozen_tkinter_uses_getattr
- TestSysAttributesStrictTyping.test_get_app_dir_uses_getattr_for_file
- TestSysAttributesStrictTyping.test_sys_frozen_attribute_check
- TestSysAttributesStrictTyping.test_sys_meipass_attribute_check

### Libraries/PyKotor/tests/test_utility/test_tasks.py (24 tests)

- TestFileActionsExecutor.test_queue_task_with_custom_function
- TestFileActionsExecutor.test_cancel_task
- TestFileActionsExecutor.test_pause_resume_task
- TestFileActionsExecutor.test_retry_task
- TestFileActionsExecutor.test_get_task_details
- TestFileActionsExecutor.test_task_completed
- TestFileActionsExecutor.test_queue_task
- TestFileActionsExecutor.test_get_task
- TestFileActionsExecutor.test_update_task_progress
- TestFileActionsExecutor.test_cleanup_tasks
- TestFileActionsExecutor.test_custom_function
- TestFileActionsExecutor.test_pickleable_task
- TestFileActionsExecutor.test_task_status
- TestFileActionsExecutor.test_task_result
- TestFileActionsExecutor.test_task_error
- TestFileActionsExecutor.test_task_progress
- TestFileActionsExecutor.test_task_priority
- TestFileActionsExecutor.test_task_description
- TestFileActionsExecutor.test_task_start_time
- TestFileActionsExecutor.test_task_end_time
- TestFileActionsExecutor.test_task_kwargs
- TestFileActionsExecutor.test_task_pause_flag
- TestFileActionsExecutor.test_task_cancel_flag
- TestFileActionsExecutor.test_task_retry

### Libraries/PyKotor/tests/test_utility/test_visual_layout_conformance.py (78 tests)

- TestQFileDialogExtendedLayout.test_main_layout_is_grid
- TestQFileDialogExtendedLayout.test_grid_has_minimum_rows
- TestQFileDialogExtendedLayout.test_ribbon_position_in_grid
- TestQFileDialogExtendedLayout.test_address_bar_position_in_grid
- TestQFileDialogExtendedLayout.test_search_filter_position_in_grid
- TestQFileDialogExtendedLayout.test_splitter_position_in_grid
- TestQFileDialogExtendedLayout.test_splitter_contains_sidebar
- TestQFileDialogExtendedLayout.test_splitter_contains_content_frame
- TestQFileDialogExtendedLayout.test_sidebar_is_visible_by_default
- TestQFileDialogExtendedLayout.test_sidebar_width_reasonable
- TestQFileDialogExtendedLayout.test_stacked_widget_has_two_pages
- TestQFileDialogExtendedLayout.test_list_view_exists_in_stack
- TestQFileDialogExtendedLayout.test_tree_view_exists_in_stack
- TestQFileDialogExtendedLayout.test_view_mode_buttons_exist
- TestQFileDialogExtendedLayout.test_view_mode_list_shows_list_view
- TestQFileDialogExtendedLayout.test_view_mode_detail_shows_tree_view
- TestQFileDialogExtendedLayout.test_navigation_buttons_exist
- TestQFileDialogExtendedLayout.test_navigation_buttons_are_tool_buttons
- TestQFileDialogExtendedLayout.test_new_folder_button_exists
- TestQFileDialogExtendedLayout.test_file_name_label_exists
- TestQFileDialogExtendedLayout.test_file_name_edit_exists
- TestQFileDialogExtendedLayout.test_file_type_label_exists
- TestQFileDialogExtendedLayout.test_file_type_combo_exists
- TestQFileDialogExtendedLayout.test_button_box_exists
- TestQFileDialogExtendedLayout.test_address_bar_has_navigation_buttons
- TestQFileDialogExtendedLayout.test_address_bar_shows_current_path
- TestQFileDialogExtendedLayout.test_address_bar_updates_on_navigation
- TestQFileDialogExtendedLayout.test_search_filter_has_line_edit
- TestQFileDialogExtendedLayout.test_search_filter_has_placeholder
- TestQFileDialogExtendedLayout.test_preview_pane_exists
- TestQFileDialogExtendedLayout.test_preview_pane_hidden_by_default
- TestQFileDialogExtendedLayout.test_preview_pane_can_be_shown
- TestQFileDialogExtendedLayout.test_preview_pane_in_splitter
- TestQFileDialogExtendedLayout.test_ribbon_exists
- TestQFileDialogExtendedLayout.test_ribbon_has_tab_widget
- TestQFileDialogExtendedLayout.test_ribbon_has_view_tab
- TestQFileDialogExtendedLayout.test_ribbon_has_home_tab
- TestQFileDialogExtendedLayout.test_tree_view_has_header
- TestQFileDialogExtendedLayout.test_tree_view_shows_name_column
- TestQFileDialogExtendedLayout.test_tree_view_shows_size_column
- TestQFileDialogExtendedLayout.test_tree_view_shows_type_column
- TestQFileDialogExtendedLayout.test_tree_view_shows_date_column
- TestFileSystemExplorerWidgetLayout.test_is_main_window
- TestFileSystemExplorerWidgetLayout.test_has_central_widget
- TestFileSystemExplorerWidgetLayout.test_has_status_bar
- TestFileSystemExplorerWidgetLayout.test_has_menu_bar
- TestFileSystemExplorerWidgetLayout.test_ribbon_widget_exists
- TestFileSystemExplorerWidgetLayout.test_ribbon_at_top
- TestFileSystemExplorerWidgetLayout.test_address_bar_exists
- TestFileSystemExplorerWidgetLayout.test_search_bar_exists
- TestFileSystemExplorerWidgetLayout.test_main_splitter_exists
- TestFileSystemExplorerWidgetLayout.test_sidebar_widget_exists
- TestFileSystemExplorerWidgetLayout.test_sidebar_has_tree_view
- TestFileSystemExplorerWidgetLayout.test_sidebar_tree_shows_only_name
- TestFileSystemExplorerWidgetLayout.test_sidebar_has_bookmarks
- TestFileSystemExplorerWidgetLayout.test_sidebar_has_drives_widget
- TestFileSystemExplorerWidgetLayout.test_dynamic_view_exists
- TestFileSystemExplorerWidgetLayout.test_dynamic_view_has_multiple_modes
- TestFileSystemExplorerWidgetLayout.test_has_list_view
- TestFileSystemExplorerWidgetLayout.test_has_tree_view
- TestFileSystemExplorerWidgetLayout.test_status_bar_has_item_count
- TestFileSystemExplorerWidgetLayout.test_status_bar_has_selected_count
- TestFileSystemExplorerWidgetLayout.test_status_bar_has_free_space
- TestFileSystemExplorerWidgetLayout.test_status_bar_has_zoom_slider
- TestFileSystemExplorerWidgetLayout.test_status_bar_has_progress_bar
- TestFileSystemExplorerWidgetLayout.test_preview_widget_exists
- TestFileSystemExplorerWidgetLayout.test_preview_widget_hidden_by_default
- TestFileSystemExplorerWidgetLayout.test_task_status_widget_exists
- TestFileSystemExplorerWidgetLayout.test_address_bar_has_refresh_button
- TestFileSystemExplorerWidgetLayout.test_address_bar_shows_current_path
- TestFileSystemExplorerWidgetLayout.test_sidebar_has_fixed_minimum_width
- TestFileSystemExplorerWidgetLayout.test_dynamic_view_expands
- TestFileSystemExplorerWidgetLayout.test_has_filesystem_model
- TestFileSystemExplorerWidgetLayout.test_has_proxy_model
- TestFileSystemExplorerWidgetLayout.test_proxy_model_source_is_fs_model
- TestFileSystemExplorerWidgetLayout.test_views_use_proxy_model
- TestLayoutConformanceIntegration.test_both_widgets_initialize_without_error
- TestLayoutConformanceIntegration.test_widgets_share_similar_structure

### Libraries/PyKotor/tests/test_utility/test_windows_explorer_conformance.py (102 tests)

- TestExplorerWindowStructure.test_is_main_window
- TestExplorerWindowStructure.test_has_central_widget
- TestExplorerWindowStructure.test_has_status_bar
- TestExplorerWindowStructure.test_minimum_size
- TestExplorerWindowStructure.test_window_title_set
- TestExplorerMenuBar.test_has_menu_bar
- TestExplorerMenuBar.test_menu_bar_has_file_menu
- TestExplorerMenuBar.test_menu_bar_has_edit_menu
- TestExplorerMenuBar.test_menu_bar_has_view_menu
- TestExplorerRibbon.test_ribbon_exists
- TestExplorerRibbon.test_ribbon_has_tab_widget
- TestExplorerRibbon.test_ribbon_tab_count
- TestExplorerRibbon.test_ribbon_has_file_tab
- TestExplorerRibbon.test_ribbon_has_home_tab
- TestExplorerRibbon.test_ribbon_has_share_tab
- TestExplorerRibbon.test_ribbon_has_view_tab
- TestExplorerRibbon.test_home_tab_has_clipboard_group
- TestExplorerRibbon.test_home_tab_has_organize_group
- TestExplorerRibbon.test_home_tab_has_new_group
- TestExplorerRibbon.test_home_tab_has_open_group
- TestExplorerRibbon.test_home_tab_has_select_group
- TestExplorerRibbonViewTab.test_view_tab_has_layout_group
- TestExplorerRibbonViewTab.test_view_tab_has_panes_group
- TestExplorerRibbonViewTab.test_view_tab_has_show_hide_group
- TestExplorerRibbonViewTab.test_view_tab_has_sort_group
- TestExplorerRibbonShareTab.test_share_tab_has_share_action
- TestExplorerRibbonShareTab.test_share_tab_has_email_action
- TestExplorerRibbonShareTab.test_share_tab_has_zip_action
- TestExplorerRibbonShareTab.test_share_tab_has_print_action
- TestExplorerNavigationBar.test_has_address_bar
- TestExplorerNavigationBar.test_has_back_button
- TestExplorerNavigationBar.test_has_forward_button
- TestExplorerNavigationBar.test_has_up_button
- TestExplorerNavigationBar.test_back_button_initially_disabled
- TestExplorerNavigationBar.test_forward_button_initially_disabled
- TestExplorerNavigationBar.test_address_bar_shows_current_path
- TestExplorerSearchBox.test_has_search_widget
- TestExplorerSearchBox.test_search_box_has_line_edit
- TestExplorerSearchBox.test_search_box_placeholder_text
- TestExplorerSearchBox.test_search_filters_content
- TestExplorerSearchBox.test_search_clear_restores_content
- TestExplorerSidebar.test_has_sidebar
- TestExplorerSidebar.test_sidebar_is_visible_by_default
- TestExplorerSidebar.test_sidebar_width_reasonable
- TestExplorerSidebar.test_sidebar_has_tree_view
- TestExplorerSidebar.test_sidebar_tree_shows_drives
- TestExplorerSidebar.test_sidebar_can_be_hidden
- TestExplorerContentArea.test_has_content_view
- TestExplorerContentArea.test_content_view_has_current_view
- TestExplorerContentArea.test_content_view_shows_files
- TestExplorerContentArea.test_content_view_is_item_view
- TestExplorerViewModes.test_extra_large_icons_mode
- TestExplorerViewModes.test_large_icons_mode
- TestExplorerViewModes.test_medium_icons_mode
- TestExplorerViewModes.test_small_icons_mode
- TestExplorerViewModes.test_list_view_mode
- TestExplorerViewModes.test_detail_view_mode
- TestExplorerViewModes.test_detail_view_has_header
- TestExplorerViewModes.test_detail_view_has_multiple_columns
- TestExplorerViewModeColumns.test_has_name_column
- TestExplorerViewModeColumns.test_has_size_column
- TestExplorerViewModeColumns.test_has_type_column
- TestExplorerViewModeColumns.test_has_date_modified_column
- TestExplorerViewModeColumns.test_columns_are_resizable
- TestExplorerViewModeColumns.test_header_is_clickable_for_sort
- TestExplorerSorting.test_sort_by_name_action
- TestExplorerSorting.test_sort_by_date_action
- TestExplorerSorting.test_sort_by_type_action
- TestExplorerSorting.test_sort_by_size_action
- TestExplorerSorting.test_sort_ascending_action
- TestExplorerSorting.test_sort_descending_action
- TestExplorerStatusBar.test_status_bar_exists
- TestExplorerStatusBar.test_status_bar_shows_item_count
- TestExplorerStatusBar.test_status_bar_updates_on_selection
- TestExplorerFileOperations.test_new_folder_action
- TestExplorerFileOperations.test_delete_action
- TestExplorerFileOperations.test_rename_action
- TestExplorerFileOperations.test_properties_action
- TestExplorerFileOperations.test_cut_action
- TestExplorerFileOperations.test_copy_action
- TestExplorerFileOperations.test_paste_action
- TestExplorerFileOperations.test_copy_path_action
- TestExplorerNavigation.test_navigate_to_subfolder
- TestExplorerNavigation.test_navigate_up
- TestExplorerNavigation.test_back_navigation
- TestExplorerNavigation.test_forward_navigation
- TestExplorerNavigation.test_double_click_opens_folder
- TestExplorerKeyboardNavigation.test_arrow_down_moves_selection
- TestExplorerKeyboardNavigation.test_enter_opens_folder
- TestExplorerKeyboardNavigation.test_backspace_goes_up
- TestExplorerKeyboardNavigation.test_ctrl_a_selects_all
- TestExplorerContextMenu.test_context_menu_on_empty_area
- TestExplorerContextMenu.test_context_menu_on_file
- TestExplorerPanes.test_preview_pane_toggle
- TestExplorerPanes.test_details_pane_toggle
- TestExplorerPanes.test_navigation_pane_toggle
- TestExplorerShowHideOptions.test_show_hidden_files_action
- TestExplorerShowHideOptions.test_show_file_extensions_action
- TestExplorerShowHideOptions.test_toggle_hidden_files
- TestExplorerSelection.test_select_all_action
- TestExplorerSelection.test_select_none_action
- TestExplorerSelection.test_invert_selection_action

### Libraries/PyKotor/tests/test_utility/test_windows_file_dialog_conformance.py (97 tests)

- TestFileDialogLayoutStructure.test_main_layout_type
- TestFileDialogLayoutStructure.test_grid_layout_minimum_dimensions
- TestFileDialogLayoutStructure.test_ribbons_widget_position
- TestFileDialogLayoutStructure.test_address_bar_position
- TestFileDialogLayoutStructure.test_search_filter_position
- TestFileDialogLayoutStructure.test_look_in_label_offset_position
- TestFileDialogLayoutStructure.test_splitter_position
- TestFileDialogLayoutStructure.test_splitter_widget_count
- TestFileDialogLayoutStructure.test_splitter_first_widget_is_sidebar
- TestFileDialogLayoutStructure.test_splitter_second_widget_is_frame
- TestFileDialogLayoutStructure.test_stacked_widget_page_count
- TestFileDialogLayoutStructure.test_list_view_in_stacked_page
- TestFileDialogLayoutStructure.test_tree_view_in_stacked_page
- TestFileDialogLayoutStructure.test_file_name_controls_row
- TestFileDialogLayoutStructure.test_file_type_controls_row
- TestFileDialogLayoutStructure.test_file_type_row_below_file_name_row
- TestFileDialogSidebarStructure.test_sidebar_is_qframe
- TestFileDialogSidebarStructure.test_sidebar_visible_by_default
- TestFileDialogSidebarStructure.test_sidebar_minimum_width
- TestFileDialogSidebarStructure.test_sidebar_default_width_in_splitter
- TestFileDialogToolbarStructure.test_back_button_exists
- TestFileDialogToolbarStructure.test_forward_button_exists
- TestFileDialogToolbarStructure.test_to_parent_button_exists
- TestFileDialogToolbarStructure.test_new_folder_button_exists
- TestFileDialogToolbarStructure.test_list_mode_button_exists
- TestFileDialogToolbarStructure.test_detail_mode_button_exists
- TestFileDialogToolbarStructure.test_navigation_buttons_in_horizontal_layout
- TestFileDialogViewModes.test_list_view_mode_shows_list_view
- TestFileDialogViewModes.test_detail_view_mode_shows_tree_view
- TestFileDialogViewModes.test_list_mode_button_switches_to_list
- TestFileDialogViewModes.test_detail_mode_button_switches_to_detail
- TestFileDialogViewModes.test_list_mode_button_pressed_state
- TestFileDialogViewModes.test_detail_mode_button_pressed_state
- TestFileDialogViewModes.test_view_mode_persistence_across_navigation
- TestFileDialogDetailViewColumns.test_tree_view_has_header
- TestFileDialogDetailViewColumns.test_tree_view_has_name_column
- TestFileDialogDetailViewColumns.test_tree_view_has_size_column
- TestFileDialogDetailViewColumns.test_tree_view_has_type_column
- TestFileDialogDetailViewColumns.test_tree_view_has_date_modified_column
- TestFileDialogDetailViewColumns.test_tree_view_columns_resizable
- TestFileDialogDetailViewColumns.test_tree_view_header_clickable_for_sort
- TestFileDialogNavigation.test_set_directory_updates_view
- TestFileDialogNavigation.test_set_directory_updates_address_bar
- TestFileDialogNavigation.test_navigate_to_parent
- TestFileDialogNavigation.test_navigate_back_in_history
- TestFileDialogNavigation.test_navigate_forward_in_history
- TestFileDialogNavigation.test_double_click_folder_navigates
- TestFileDialogKeyboardNavigation.test_arrow_down_moves_selection
- TestFileDialogKeyboardNavigation.test_arrow_up_moves_selection
- TestFileDialogKeyboardNavigation.test_enter_opens_folder
- TestFileDialogKeyboardNavigation.test_backspace_goes_to_parent
- TestFileDialogKeyboardNavigation.test_home_key_selects_first_item
- TestFileDialogKeyboardNavigation.test_end_key_selects_last_item
- TestFileDialogFileSelection.test_single_file_selection
- TestFileDialogFileSelection.test_multiple_file_selection_mode
- TestFileDialogFileSelection.test_directory_selection_mode
- TestFileDialogFileSelection.test_ctrl_click_adds_to_selection
- TestFileDialogFileSelection.test_shift_click_range_selection
- TestFileDialogFileFiltering.test_set_name_filter
- TestFileDialogFileFiltering.test_multiple_name_filters
- TestFileDialogFileFiltering.test_filter_selection
- TestFileDialogFileFiltering.test_search_filter_updates_proxy
- TestFileDialogFileFiltering.test_search_filter_case_insensitive
- TestFileDialogFileFiltering.test_search_filter_clear
- TestFileDialogBottomControls.test_file_name_label_text
- TestFileDialogBottomControls.test_file_name_edit_is_editable
- TestFileDialogBottomControls.test_file_name_edit_updates_selection
- TestFileDialogBottomControls.test_file_type_combo_has_filters
- TestFileDialogBottomControls.test_button_box_has_accept_button
- TestFileDialogBottomControls.test_button_box_has_reject_button
- TestFileDialogAcceptModes.test_accept_open_mode
- TestFileDialogAcceptModes.test_accept_save_mode
- TestFileDialogAcceptModes.test_accept_mode_changes_button_text
- TestFileDialogPreviewPane.test_preview_pane_exists
- TestFileDialogPreviewPane.test_preview_pane_hidden_by_default
- TestFileDialogPreviewPane.test_preview_pane_can_be_shown
- TestFileDialogPreviewPane.test_preview_pane_can_be_hidden
- TestFileDialogPreviewPane.test_preview_pane_in_splitter
- TestFileDialogRibbon.test_ribbon_exists
- TestFileDialogRibbon.test_ribbon_has_tab_widget
- TestFileDialogRibbon.test_ribbon_has_home_tab
- TestFileDialogRibbon.test_ribbon_has_view_tab
- TestFileDialogRibbon.test_ribbon_view_tab_has_preview_pane_action
- TestFileDialogRibbon.test_ribbon_view_tab_has_navigation_pane_action
- TestFileDialogRibbon.test_ribbon_has_view_mode_actions
- TestFileDialogContextMenu.test_context_menu_can_be_created
- TestFileDialogContextMenu.test_context_menu_has_actions
- TestFileDialogContextMenu.test_context_menu_on_file_has_open
- TestFileDialogSignals.test_directory_entered_signal
- TestFileDialogSignals.test_current_changed_signal
- TestFileDialogSignals.test_files_selected_signal
- TestFileDialogSignals.test_filter_selected_signal
- TestFileDialogOptions.test_dont_use_native_dialog_option
- TestFileDialogOptions.test_show_dirs_only_option
- TestFileDialogOptions.test_read_only_option
- TestFileDialogOptions.test_hide_name_filter_details_option
- TestFileDialogOptions.test_dont_resolve_symlinks_option

### Libraries/PyKotor/tests/tslpatcher/diff/test_diff_2damemory_generation.py (6 tests)

- TestDiff2DAMemoryGeneration.test_gff_references_new_2da_row
- TestDiff2DAMemoryGeneration.test_gff_references_modified_2da_row
- TestDiff2DAMemoryGeneration.test_multiple_gff_files_reference_same_2da_row
- TestDiff2DAMemoryGeneration.test_2da_row_label_storage
- TestDiff2DAMemoryGeneration.test_addcolumn_with_2damemory_storage
- TestDiff2DAMemoryGeneration.test_multiple_repair_rows_share_token

### Libraries/PyKotor/tests/tslpatcher/diff/test_diff_comprehensive.py (31 tests)

- Test2DAMemory.test_addrow_stores_row_index
- Test2DAMemory.test_changerow_stores_row_index
- Test2DAMemory.test_2damemory_cross_reference_chain
- Test2DAMemory.test_addcolumn_with_2damemory_storage
- Test2DAMemory.test_multiple_gff_files_use_same_2damemory_token
- Test2DAMemory.test_2damemory_row_label_storage
- Test2DAMemory.test_2damemory_row_cell_storage
- Test2DAMemory.test_2damemory_high_function
- TestTLKStrRef.test_tlk_append_basic
- TestTLKStrRef.test_tlk_replace_existing_entries
- TestTLKStrRef.test_strref_used_in_2da
- TestTLKStrRef.test_strref_used_in_gff_localized_string
- TestTLKStrRef.test_strref_used_in_ssf
- TestGFF.test_gff_modify_all_field_types
- TestGFF.test_gff_add_field_to_struct
- TestGFF.test_gff_nested_struct_modifications
- TestGFF.test_gff_list_modifications
- TestGFF.test_gff_localized_string_with_multiple_languages
- TestSSF.test_ssf_modify_all_sound_slots
- TestIntegration.test_full_mod_scenario_new_spell
- TestIntegration.test_full_mod_scenario_new_item_type
- TestRealWorldScenarios.test_ajunta_pall_appearance_mod
- TestRealWorldScenarios.test_k1_community_patch_pattern
- TestInstallList.test_install_to_override
- TestInstallList.test_install_to_modules
- TestEdgeCases.test_empty_2da_modification
- TestEdgeCases.test_2da_with_empty_cells
- TestEdgeCases.test_gff_with_special_characters_in_strings
- TestEdgeCases.test_large_2da_many_rows
- TestPerformance.test_many_2da_files
- TestPerformance.test_many_gff_files

### Libraries/PyKotor/tests/tslpatcher/diff/test_diff_tslpatcher.py (9 tests)

- TestTSLPatcherFromDiff.test_merge_tslpatcher_generates_changes_ini_for_dlg
- TestTSLPatcherFromDiff.test_merge_tslpatcher_detects_conflicting_dlg_edits
- TestTSLPatcherFromDiff.test_change_existing_rowindex
- TestTSLPatcherFromDiff.test_2da_addcolumn_basic
- TestTSLPatcherFromDiff.test_2da_addcolumn_indexinsert
- TestTSLPatcherFromDiff.test_2da_addcolumn_labelinsert
- TestTSLPatcherFromDiff.test_2da_addcolumn_default
- TestTSLPatcherFromDiff.test_ssf_stored_constant
- TestTSLPatcherFromDiff.test_ssf_set

### Libraries/PyKotor/tests/tslpatcher/diff/test_full_execution.py (4 tests)

- TestKotorDiffFullExecution.test_01_step1_generate_patch
- TestKotorDiffFullExecution.test_02_step2_install_patch
- TestKotorDiffFullExecution.test_03_step3_verify_installation
- TestKotorDiffFullExecution.test_04_step4_uninstall_patch

### Libraries/PyKotor/tests/tslpatcher/diff/test_twoda.py (6 tests)

- TestVendorTwoDAComparison.test_column_count_mismatch
- TestVendorTwoDAComparison.test_row_count_mismatch
- TestVendorTwoDAComparison.test_cell_mismatch
- TestVendorTwoDAComparison.test_are_matching
- TestVendorTwoDADiffAnalyzer.test_find_new_column
- TestVendorTwoDADiffAnalyzer.test_find_new_row

### Libraries/PyKotor/tests/tslpatcher/mods/test_vendor_twoda_mods.py (11 tests)

- TestVendorAddColumnModifier.test_correct_column_header
- TestVendorAddColumnModifier.test_correct_default_value
- TestVendorAddRowModifier.test_not_exclusive_no_row_label_no_store
- TestVendorAddRowModifier.test_assign_row_label
- TestVendorAddRowModifier.test_exclusive_and_existing
- TestVendorAddRowModifier.test_exclusive_and_not_existing
- TestVendorAddRowModifier.test_store_value
- TestVendorCopyRowModifier.test_copy_row
- TestVendorCopyRowModifier.test_copy_row_exclusive_and_existing
- TestVendorEditRowModifier.test_edit_cells
- TestVendorEditRowModifier.test_store_value

### Libraries/PyKotor/tests/tslpatcher/test_config.py (23 tests)

- TestLookupResourceFunction.test_lookup_resource_replace_file_true
- TestLookupResourceFunction.test_lookup_resource_capsule_exists_true
- TestLookupResourceFunction.test_lookup_resource_no_capsule_exists_true
- TestLookupResourceFunction.test_lookup_resource_no_capsule_exists_false
- TestLookupResourceFunction.test_lookup_resource_capsule_exists_false
- TestLookupResourceFunction.test_lookup_resource_replace_file_true_no_file
- TestLookupResourceFunction.test_lookup_resource_capsule_exists_true_no_file
- TestLookupResourceFunction.test_lookup_resource_no_capsule_exists_true_no_file
- TestLookupResourceFunction.test_lookup_resource_no_capsule_exists_false_no_file
- TestShouldPatchFunction.test_replace_file_exists_destination_dot
- TestShouldPatchFunction.test_replace_file_exists_saveas_destination_dot
- TestShouldPatchFunction.test_replace_file_exists_destination_override
- TestShouldPatchFunction.test_replace_file_exists_saveas_destination_override
- TestShouldPatchFunction.test_replace_file_not_exists_saveas_destination_override
- TestShouldPatchFunction.test_replace_file_not_exists_destination_override
- TestShouldPatchFunction.test_replace_file_exists_destination_capsule
- TestShouldPatchFunction.test_replace_file_exists_saveas_destination_capsule
- TestShouldPatchFunction.test_replace_file_not_exists_saveas_destination_capsule
- TestShouldPatchFunction.test_replace_file_not_exists_destination_capsule
- TestShouldPatchFunction.test_not_replace_file_exists_skip_false
- TestShouldPatchFunction.test_skip_if_not_replace_not_replace_file_exists
- TestShouldPatchFunction.test_capsule_not_exist
- TestShouldPatchFunction.test_default_behavior

### Libraries/PyKotor/tests/tslpatcher/test_mods.py (66 tests)

- TestManipulateTLK.test_apply_append
- TestManipulateTLK.test_apply_replace
- TestManipulate2DA.test_change_existing_rowindex
- TestManipulate2DA.test_change_existing_rowlabel
- TestManipulate2DA.test_change_existing_labelindex
- TestManipulate2DA.test_change_assign_tlkmemory
- TestManipulate2DA.test_change_assign_2damemory
- TestManipulate2DA.test_change_assign_high
- TestManipulate2DA.test_set_2damemory_rowindex
- TestManipulate2DA.test_set_2damemory_rowlabel
- TestManipulate2DA.test_set_2damemory_columnlabel
- TestManipulate2DA.test_add_rowlabel_use_maxrowlabel
- TestManipulate2DA.test_add_rowlabel_use_constant
- TestManipulate2DA.test_add_rowlabel_existing
- TestManipulate2DA.test_add_exclusive_notexists
- TestManipulate2DA.test_add_exclusive_exists
- TestManipulate2DA.test_add_exclusive_badcolumn
- TestManipulate2DA.test_add_exclusive_none
- TestManipulate2DA.test_add_assign_high
- TestManipulate2DA.test_add_assign_tlkmemory
- TestManipulate2DA.test_add_assign_2damemory
- TestManipulate2DA.test_add_2damemory_rowindex
- TestManipulate2DA.test_copy_existing_rowindex
- TestManipulate2DA.test_copy_existing_rowlabel
- TestManipulate2DA.test_copy_exclusive_notexists
- TestManipulate2DA.test_copy_exclusive_exists
- TestManipulate2DA.test_copy_exclusive_none
- TestManipulate2DA.test_copy_set_newrowlabel
- TestManipulate2DA.test_copy_assign_high
- TestManipulate2DA.test_copy_assign_tlkmemory
- TestManipulate2DA.test_copy_assign_2damemory
- TestManipulate2DA.test_copy_2damemory_rowindex
- TestManipulate2DA.test_addcolumn_empty
- TestManipulate2DA.test_addcolumn_default
- TestManipulate2DA.test_addcolumn_rowindex_constant
- TestManipulate2DA.test_addcolumn_rowlabel_2damemory
- TestManipulate2DA.test_addcolumn_rowlabel_tlkmemory
- TestManipulate2DA.test_addcolumn_2damemory_index
- TestManipulate2DA.test_addcolumn_2damemory_line
- TestManipulateGFF.test_modify_field_uint8
- TestManipulateGFF.test_modify_field_int8
- TestManipulateGFF.test_modify_field_uint16
- TestManipulateGFF.test_modify_field_int16
- TestManipulateGFF.test_modify_field_uint32
- TestManipulateGFF.test_modify_field_int32
- TestManipulateGFF.test_modify_field_uint64
- TestManipulateGFF.test_modify_field_int64
- TestManipulateGFF.test_modify_field_single
- TestManipulateGFF.test_modify_field_double
- TestManipulateGFF.test_modify_field_string
- TestManipulateGFF.test_modify_field_locstring
- TestManipulateGFF.test_modify_field_vector3
- TestManipulateGFF.test_modify_field_vector4
- TestManipulateGFF.test_modify_nested
- TestManipulateGFF.test_modify_2damemory
- TestManipulateGFF.test_modify_tlkmemory
- TestManipulateGFF.test_add_newnested
- TestManipulateGFF.test_add_nested
- TestManipulateGFF.test_add_use_2damemory
- TestManipulateGFF.test_add_use_tlkmemory
- TestManipulateGFF.test_add_field_locstring
- TestManipulateGFF.test_addlist_listindex
- TestManipulateGFF.test_addlist_store_2damemory
- TestManipulateSSF.test_assign_int
- TestManipulateSSF.test_assign_2datoken
- TestManipulateSSF.test_assign_tlktoken

### Libraries/PyKotor/tests/tslpatcher/test_reader.py (46 tests)

- TestConfigReader.test_tlk_appendfile_functionality
- TestConfigReader.test_tlk_strref_default_functionality
- TestConfigReader.test_tlk_complex_changes
- TestConfigReader.test_tlk_replacefile_functionality
- TestConfigReader.test_2da_changerow_identifier
- TestConfigReader.test_2da_changerow_targets
- TestConfigReader.test_2da_changerow_store2da
- TestConfigReader.test_2da_changerow_cells
- TestConfigReader.test_2da_addrow_identifier
- TestConfigReader.test_2da_addrow_exclusivecolumn
- TestConfigReader.test_2da_addrow_rowlabel
- TestConfigReader.test_2da_addrow_store2da
- TestConfigReader.test_2da_addrow_cells
- TestConfigReader.test_2da_copyrow_identifier
- TestConfigReader.test_2da_copyrow_high
- TestConfigReader.test_2da_copyrow_target
- TestConfigReader.test_2da_copyrow_exclusivecolumn
- TestConfigReader.test_2da_copyrow_rowlabel
- TestConfigReader.test_2da_copyrow_store2da
- TestConfigReader.test_2da_copyrow_cells
- TestConfigReader.test_2da_addcolumn_basic
- TestConfigReader.test_2da_addcolumn_indexinsert
- TestConfigReader.test_2da_addcolumn_labelinsert
- TestConfigReader.test_2da_addcolumn_2damemory
- TestConfigReader.test_ssf_replace
- TestConfigReader.test_ssf_stored_constant
- TestConfigReader.test_ssf_stored_2da
- TestConfigReader.test_ssf_stored_tlk
- TestConfigReader.test_ssf_set
- TestConfigReader.test_gff_modify_pathing
- TestConfigReader.test_gff_modify_type_int
- TestConfigReader.test_gff_modify_type_string
- TestConfigReader.test_gff_modify_type_vector3
- TestConfigReader.test_gff_modify_type_vector4
- TestConfigReader.test_gff_modify_type_locstring
- TestConfigReader.test_gff_modify_2damemory
- TestConfigReader.test_gff_modify_tlkmemory
- TestConfigReader.test_gff_add_ints
- TestConfigReader.test_gff_add_floats
- TestConfigReader.test_gff_add_string
- TestConfigReader.test_gff_add_vector3
- TestConfigReader.test_gff_add_vector4
- TestConfigReader.test_gff_add_resref
- TestConfigReader.test_gff_add_locstring
- TestConfigReader.test_gff_add_inside_struct
- TestConfigReader.test_gff_add_inside_list

### Libraries/PyKotor/tests/tslpatcher/test_tslpatcher.py (116 tests)

- TestTSLPatcher.test_change_existing_rowindex
- TestTSLPatcher.test_change_existing_rowlabel
- TestTSLPatcher.test_gff_add_inside_struct
- TestTSLPatcher.test_gff_add_field_locstring
- TestTSLPatcher.test_gff_modifier_path_shorter_than_self_path
- TestTSLPatcher.test_gff_modifier_path_longer_than_self_path
- TestTSLPatcher.test_gff_modifier_path_partial_absolute
- TestTSLPatcher.test_gff_add_field_with_sentinel_at_start
- TestTSLPatcher.test_gff_add_field_with_empty_paths
- TestTSLPatcher.test_2da_changerow_identifier
- TestTSLPatcher.test_2da_changerow_targets
- TestTSLPatcher.test_2da_changerow_store2da
- TestTSLPatcher.test_2da_changerow_cells
- TestTSLPatcher.test_2da_addcolumn_basic
- TestTSLPatcher.test_2da_addcolumn_indexinsert
- TestTSLPatcher.test_2da_addcolumn_labelinsert
- TestTSLPatcher.test_2da_addcolumn_2damemory
- TestTSLPatcher.test_2da_addrow_identifier
- TestTSLPatcher.test_2da_addrow_exclusivecolumn
- TestTSLPatcher.test_2da_addrow_rowlabel
- TestTSLPatcher.test_2da_addrow_store2da
- TestTSLPatcher.test_2da_addrow_cells
- TestTSLPatcher.test_2da_copyrow_identifier
- TestTSLPatcher.test_2da_copyrow_high
- TestTSLPatcher.test_2da_copyrow_target
- TestTSLPatcher.test_2da_copyrow_exclusivecolumn
- TestTSLPatcher.test_2da_copyrow_rowlabel
- TestTSLPatcher.test_2da_copyrow_store2da
- TestTSLPatcher.test_2da_copyrow_cells
- TestTSLPatcher.test_change_existing_labelindex
- TestTSLPatcher.test_change_assign_tlkmemory
- TestTSLPatcher.test_change_assign_2damemory
- TestTSLPatcher.test_change_assign_high
- TestTSLPatcher.test_set_2damemory_rowindex
- TestTSLPatcher.test_set_2damemory_rowlabel
- TestTSLPatcher.test_set_2damemory_columnlabel
- TestTSLPatcher.test_add_rowlabel_use_maxrowlabel
- TestTSLPatcher.test_add_rowlabel_use_constant
- TestTSLPatcher.test_add_rowlabel_existing
- TestTSLPatcher.test_add_exclusive_notexists
- TestTSLPatcher.test_add_exclusive_exists
- TestTSLPatcher.test_add_exclusive_none
- TestTSLPatcher.test_add_assign_high
- TestTSLPatcher.test_add_assign_tlkmemory
- TestTSLPatcher.test_add_assign_2damemory
- TestTSLPatcher.test_add_2damemory_rowindex
- TestTSLPatcher.test_copy_existing_rowindex
- TestTSLPatcher.test_copy_existing_rowlabel
- TestTSLPatcher.test_copy_exclusive_notexists
- TestTSLPatcher.test_copy_exclusive_exists
- TestTSLPatcher.test_copy_exclusive_none
- TestTSLPatcher.test_copy_set_newrowlabel
- TestTSLPatcher.test_copy_assign_high
- TestTSLPatcher.test_copy_assign_tlkmemory
- TestTSLPatcher.test_copy_assign_2damemory
- TestTSLPatcher.test_copy_2damemory_rowindex
- TestTSLPatcher.test_addcolumn_empty
- TestTSLPatcher.test_addcolumn_default
- TestTSLPatcher.test_addcolumn_rowindex_constant
- TestTSLPatcher.test_addcolumn_rowlabel_2damemory
- TestTSLPatcher.test_addcolumn_rowlabel_tlkmemory
- TestTSLPatcher.test_addcolumn_2damemory_index
- TestTSLPatcher.test_addcolumn_2damemory_line
- TestTSLPatcher.test_ssf_replace
- TestTSLPatcher.test_ssf_stored_constant
- TestTSLPatcher.test_ssf_stored_2da
- TestTSLPatcher.test_ssf_stored_tlk
- TestTSLPatcher.test_ssf_set
- TestTSLPatcher.test_tlk_appendfile_functionality
- TestTSLPatcher.test_tlk_strref_default_functionality
- TestTSLPatcher.test_tlk_complex_changes
- TestTSLPatcher.test_tlk_replacefile_functionality
- TestTSLPatcher.test_tlk_apply_append
- TestTSLPatcher.test_tlk_apply_replace
- TestTSLPatcher.test_gff_modify_pathing
- TestTSLPatcher.test_gff_modify_type_int
- TestTSLPatcher.test_gff_modify_type_string
- TestTSLPatcher.test_gff_modify_type_vector3
- TestTSLPatcher.test_gff_modify_type_vector4
- TestTSLPatcher.test_gff_modify_type_locstring
- TestTSLPatcher.test_gff_modify_2damemory
- TestTSLPatcher.test_gff_modify_tlkmemory
- TestTSLPatcher.test_gff_add_ints
- TestTSLPatcher.test_gff_add_floats
- TestTSLPatcher.test_gff_add_string
- TestTSLPatcher.test_gff_add_vector3
- TestTSLPatcher.test_gff_add_vector4
- TestTSLPatcher.test_gff_add_resref
- TestTSLPatcher.test_gff_add_locstring
- TestTSLPatcher.test_gff_add_inside_list
- TestTSLPatcher.test_modify_field_uint8
- TestTSLPatcher.test_modify_field_int8
- TestTSLPatcher.test_modify_field_uint16
- TestTSLPatcher.test_modify_field_int16
- TestTSLPatcher.test_modify_field_uint32
- TestTSLPatcher.test_modify_field_int32
- TestTSLPatcher.test_modify_field_uint64
- TestTSLPatcher.test_modify_field_int64
- TestTSLPatcher.test_modify_field_single
- TestTSLPatcher.test_modify_field_double
- TestTSLPatcher.test_modify_field_string
- TestTSLPatcher.test_modify_field_locstring
- TestTSLPatcher.test_modify_field_vector3
- TestTSLPatcher.test_modify_field_vector4
- TestTSLPatcher.test_modify_nested
- TestTSLPatcher.test_modify_2damemory
- TestTSLPatcher.test_modify_tlkmemory
- TestTSLPatcher.test_add_newnested
- TestTSLPatcher.test_add_nested
- TestTSLPatcher.test_add_use_2damemory
- TestTSLPatcher.test_add_use_tlkmemory
- TestTSLPatcher.test_addlist_listindex
- TestTSLPatcher.test_addlist_store_2damemory
- TestTSLPatcher.test_assign_int
- TestTSLPatcher.test_assign_2datoken
- TestTSLPatcher.test_assign_tlktoken

Collected modules: 115
Collected tests: 2599
