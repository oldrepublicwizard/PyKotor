# Wiki Source Audit Plan

This plan tracks the ongoing rewrite of wiki content so that every retained statement is backed by concrete repository sources, generated package artifacts, or reverse-engineering results.

## Sourcing rules

- Prefer local PyKotor source, packaging metadata, vendored tools, and generated manifests first.
- For external ecosystem claims, cite concrete repository files such as `README.md`, solution files, source files, or directory trees.
- For engine-behavior pages, require at least three-binary corroboration before retaining gameplay or runtime claims.
- Default binary comparison set for Odyssey-engine behavior: `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`, and `/Other BioWare Engines/Aurora/nwmain.exe` unless a different third comparator is more appropriate for the topic.
- Delete or replace any prose that cannot be traced to a specific source.

## Status

- [x] Home.md — TODO completed: local package inventory, shipped-wiki packaging path, and adjacent-repository survey rewritten from repository sources.
- [ ] 2DA-File-Format.md — TODO: keep original scope, replace weak prose with parser-code citations, and anchor runtime claims in three binaries; the generic format half plus `appearance`, `baseitems`, `classes`, `feat`, `skills`, `spells`, `itemprops`, `placeables`, `genericdoors`, `doortypes`, `soundset`, `visualeffects`, `portraits`, and `heads` now have narrower source-backed sections, but the remaining catalog still needs the same treatment.
- [ ] Area-Modding-and-Room-Transitions.md — TODO: audit room-transition workflow against toolset code, area resource formats, and three-binary runtime handling.
- [ ] Audio-and-Localization-Formats.md — TODO: re-source TLK, SSF, WAV/streaming, and StrRef claims from local parsers plus tri-binary string-loading paths.
- [ ] Bioware-Aurora-Conversation.md — TODO: preserve only source-backed Aurora conversation material and tie KotOR carryovers to local code or archived specs.
- [ ] Bioware-Aurora-Core-Formats.md — TODO: verify each preserved Aurora-format claim against archived specifications and current parser implementations.
- [ ] Bioware-Aurora-Creature.md — TODO: map every retained creature-format statement back to archived docs or current generic readers.
- [ ] Bioware-Aurora-Items-Economy-and-Narrative.md — TODO: audit item, merchant, and narrative format claims against local generic schemas and archived Aurora docs.
- [ ] Bioware-Aurora-Module-and-Area.md — TODO: tie ARE/GIT/IFO heritage prose to archived docs, local readers, and tri-binary loader evidence where applicable.
- [ ] Bioware-Aurora-Spatial-and-Interactive.md — TODO: re-source walkmesh, trigger, waypoint, and placeable heritage claims from archived docs and local code.
- [ ] Blender-Integration.md — TODO: verify Blender pipeline claims against kotorblender, KOTORMax, and local export/import code paths.
- [ ] Concepts.md — TODO: continue tightening every concept statement to local code plus tri-binary runtime anchors.
- [ ] Container-Formats.md — TODO: continue auditing KEY/BIF/ERF/RIM sections sentence-by-sentence with parser code and tri-binary lookup logic; KEY/BIF scaffolding and ERF/RIM overview sections have now been tightened against local reader/writer code, but the deeper binary-format tables still need a full pass.
- [ ] Explanations-on-HoloPatcher-Internal-Logic.md — TODO: rewrite from HoloPatcher source modules, not from inherited prose summaries.
- [ ] GFF-Creature-and-Dialogue.md — TODO: map UTC/DLG claims to local generic readers, field maps, and tri-binary GFF decoding paths.
- [ ] GFF-File-Format.md — TODO: continue replacing unsourced format prose with local parser code and three-binary GFF access anchors.
- [ ] GFF-GUI.md — TODO: verify GUI-family GFF statements from local GUI schemas and toolset editors.
- [ ] GFF-Items-and-Economy.md — TODO: source UTI/UTM/economy claims from local generics, toolset editors, and runtime references.
- [ ] GFF-Module-and-Area.md — TODO: continue tightening ARE/GIT/IFO/PTH sections to code-backed statements and tri-binary anchors.
- [ ] GFF-Spatial-Objects.md — TODO: map UTD/UTP/UTS/UTW/UTE claims to local schemas, editors, and runtime consumers.
- [ ] Ghidra-Reversing-Guide.md — TODO: ensure every reversing workflow instruction matches the actual AgentDecompile and Ghidra workflow in use.
- [ ] Holocron-Toolset-Core-Resources.md — TODO: re-source editor/resource coverage from toolset registries and installation data code.
- [ ] Holocron-Toolset-Getting-Started.md — TODO: rewrite setup and launch guidance from current package metadata and entry points.
- [ ] Holocron-Toolset-Map-Builder.md — TODO: audit map-builder claims against indoor builder and renderer implementation files.
- [ ] Holocron-Toolset-Module-Editor.md — TODO: source module-editor capabilities from concrete GUI code and packaged entry points.
- [ ] Holocron-Toolset-Module-Resources.md — TODO: tie resource-browser claims to toolset installation/resource modules and editor registry.
- [ ] Holocron-Toolset-New-Features-Guide.md — TODO: verify each feature bullet against actual code or release artifacts before keeping it.
- [ ] Holocron-Toolset-Override-Resources.md — TODO: source override behavior from installation search logic and toolset workflows.
- [ ] HoloPatcher-README-for-mod-developers.md — TODO: rewrite from current HoloPatcher behavior and patcher source code.
- [ ] HoloPatcher.md — TODO: source end-user and internal behavior from package metadata, CLI entrypoint, and patcher modules.
- [ ] Indoor-Area-Room-Layout-and-Walkmesh-Guide.md — TODO: map room and walkmesh guidance to kit/build code, BWM parsers, and renderer logic.
- [ ] Indoor-Map-Builder-Implementation-Guide.md — TODO: tie implementation notes directly to indoor builder source files and renderer code.
- [ ] Indoor-Map-Builder-User-Guide.md — TODO: audit user-guide statements against actual UI actions and builder behavior in source.
- [ ] Installing-Mods-with-HoloPatcher.md — TODO: source installer workflow text from current HoloPatcher CLI/GUI code and docs.
- [ ] Kit-Structure-Documentation.md — TODO: continue grounding kit, PWK, and DWK claims in local kit toolchain code and external engines.
- [ ] KotorDiff-Integration.md — TODO: rewrite from KotorDiff package metadata and `pykotor.diff_tool` application flow.
- [ ] Level-Layout-Formats.md — TODO: audit LYT/VIS/BWM/PWK/DWK sections from parser code and tri-binary consumers.
- [ ] LTR-File-Format.md — TODO: source LTR format claims from local parser code and any runtime text-generation references.
- [ ] MDL-MDX-File-Format.md — TODO: perform full tri-binary-plus-tooling audit of model claims before retaining them.
- [ ] Mod-Creation-Best-Practices.md — TODO: keep only recommendations that can be justified from actual tool behavior and resource-resolution logic.
- [ ] NCS-File-Format.md — TODO: source bytecode format and execution claims from local compiler/decompiler code and tri-binary VM anchors.
- [ ] NSS-File-Format.md — TODO: rewrite from compiler tooling, script definitions, and authoritative external references.
- [ ] NWNNSSCOMP-Command-Line-Reference.md — TODO: verify every flag and behavior against shipped wrapper/tool documentation or source.
- [ ] Qt-ItemView-Selection-and-RobustTableView.md — TODO: source Qt behavior notes from actual view/widget implementation code.
- [ ] Resource-Formats-and-Resolution.md — TODO: continue auditing format table and resolution prose from local registries and three-binary lookup logic.
- [ ] Texture-Formats.md — TODO: source TPC/TGA/DDS behavior from parser code, toolset editors, and runtime texture consumers.
- [ ] TSLPatcher's-Official-Readme.md — TODO: preserve only text traceable to the actual bundled/readme source.
- [ ] TSLPatcher-2DAList-Syntax.md — TODO: source every directive and example from patcher parser code and shipped readme material.
- [ ] TSLPatcher-Data-Syntax.md — TODO: ground syntax overview in actual parser behavior and bundled docs.
- [ ] TSLPatcher-GFF-Syntax.md — TODO: rewrite from patcher source and retained official readme material.
- [ ] TSLPatcher-GFFList-Syntax.md — TODO: source every list directive from parser code and retained official docs.
- [ ] TSLPatcher-HACKList-Syntax.md — TODO: verify all HACKList semantics from patcher implementation and official readme text.
- [ ] TSLPatcher-Install-and-Hack-Syntax.md — TODO: source install/hack workflow text from parser behavior and original docs.
- [ ] TSLPatcher-InstallList-Syntax.md — TODO: audit install-list directives against code and official readme material.
- [ ] TSLPatcher-SSFList-Syntax.md — TODO: source SSF patch syntax from parser code and retained official docs.
- [ ] TSLPatcher-TLKList-Syntax.md — TODO: source TLK patch syntax from parser code and retained official docs.
- [ ] Tutorial-Area-Transitions.md — TODO: retain only steps justified by current tools, formats, and runtime references.
- [ ] Tutorial-Creating-a-New-Store.md — TODO: re-source store tutorial steps from UTM/toolset workflows and actual files.
- [ ] Tutorial-Creating-Custom-Robes.md — TODO: audit robe tutorial claims against model, texture, and item resource pipelines.
- [ ] Tutorial-Creating-Static-Cameras.md — TODO: tie static-camera instructions to GIT camera data, toolset UI, and runtime behavior.
- [ ] UTC-Editor-Field-Types-AgentDecompile.md — TODO: continue field-by-field verification against UTC schema and tri-binary consumer code.
- [ ] reverse_engineering_findings.md — TODO: normalize every finding entry to explicit binary-qualified citations and evidence scope.
- [ ] reverse_engineering_findings_archive_engine_rendering.md — TODO: audit archived rendering findings for tri-binary specificity and source retention.
- [ ] reverse_engineering_findings_archive_game_objects.md — TODO: audit archived game-object findings for tri-binary specificity and source retention.
- [ ] reverse_engineering_findings_archive_resource_formats.md — TODO: audit archived resource-format findings for tri-binary specificity and source retention.
- [ ] reverse_engineering_findings_archive_toolset.md — TODO: audit archived toolset findings against live code or clearly mark them archival.
- [ ] reverse_engineering_findings_archive_tslpatcher.md — TODO: audit archived tslpatcher findings against live code or clearly mark them archival.
- [ ] reverse_engineering_findings_py_kotor_migrated_docstrings.md — TODO: verify migrated docstrings against current PyKotor code before retaining them as findings.
- [ ] reverse_engineering_findings_py_kotor_migrated_io_mdl.md — TODO: verify migrated MDL IO findings against current code and binary evidence.

## Current queue

1. 2DA-File-Format.md
2. Resource-Formats-and-Resolution.md
3. GFF-File-Format.md
4. MDL-MDX-File-Format.md
5. Audio-and-Localization-Formats.md

## Notes

- AgentDecompile shared project is already accessible for search and file listing, even though direct `open` against `C:\Users\boden\Odyssey.gpr` currently resolves to the shared-server path and errors when treated as a local project.
- Search coverage already confirms shared `2DA` analysis data exists in `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`, and `/Other BioWare Engines/Aurora/nwmain.exe` via the `CRes2DA` structure.
- `phaethon` has now been confirmed as `xoreos/phaethon`; use `doc/doxygen/README` plus concrete source files such as `src/aurora/erffile.h` when citing it.
