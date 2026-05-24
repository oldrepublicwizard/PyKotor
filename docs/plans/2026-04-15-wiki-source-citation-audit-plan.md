---
title: Wiki source-citation audit plan
status: active
date: 2026-04-15
supersedes: docs/plans/wiki-source-audit-plan.md
---

# Wiki source-citation audit plan

Goal: rewrite each wiki page from source-derived material only, with sentence-level citations. If a statement cannot be tied to code, package metadata, repository structure, or an explicitly preserved source repository, remove it instead of paraphrasing it without evidence.

Working rules:

- Edit one wiki page at a time.
- Prefer local monorepo source first, then external code repositories and preserved-source repositories.
- Keep planning and audit state in `docs/plans/`, not in the wiki pages themselves.
- For engine-behavior pages, require at least three-binary corroboration before retaining gameplay or runtime claims (merged from superseded `wiki-source-audit-plan.md`).
- Default binary comparison set for Odyssey-engine behavior: `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`, and `/Other BioWare Engines/Aurora/nwmain.exe` unless a different third comparator is more appropriate for the topic.
- Delete or replace any prose that cannot be traced to a specific source.

Current corroboration set:

- Local monorepo: PyKotor, HoloPatcher, Holocron Toolset, KotorDiff.
- External repositories reviewed for the current pass: xoreos, xoreos-tools, xoreos-docs, reone, KotOR.js, Kotor.NET, OpenKotOR/bioware-kaitai-formats, OpenKotOR/KotorMCP.
- Additional repositories are allowed when a page needs them, but each claim must still resolve to a concrete source.

Audit queue:

## Hub and cross-cutting pages

- `Home.md` - active
- `Concepts.md` - pending
- `Resource-Formats-and-Resolution.md` - pending
- `Container-Formats.md` - pending
- `Mod-Creation-Best-Practices.md` - pending
- `KotorDiff-Integration.md` - pending
- `Blender-Integration.md` - pending
- `Ghidra-Reversing-Guide.md` - pending
- `Qt-ItemView-Selection-and-RobustTableView.md` - pending
- `Kit-Structure-Documentation.md` - pending

## Format pages

- `2DA-File-Format.md` - pending
- `Audio-and-Localization-Formats.md` - pending
- `GFF-File-Format.md` - pending
- `Texture-Formats.md` - pending
- `Level-Layout-Formats.md` - pending
- `MDL-MDX-File-Format.md` - pending
- `LTR-File-Format.md` - pending
- `NCS-File-Format.md` - pending
- `NSS-File-Format.md` - pending

## GFF family pages

- `GFF-Creature-and-Dialogue.md` - pending
- `GFF-GUI.md` - pending
- `GFF-Items-and-Economy.md` - pending
- `GFF-Module-and-Area.md` - pending
- `GFF-Spatial-Objects.md` - pending

## Preserved-source and reverse-engineering pages

- `Bioware-Aurora-Core-Formats.md` - pending
- `Bioware-Aurora-Module-and-Area.md` - pending
- `Bioware-Aurora-Creature.md` - pending
- `Bioware-Aurora-Items-Economy-and-Narrative.md` - pending
- `Bioware-Aurora-Spatial-and-Interactive.md` - pending
- `Bioware-Aurora-Conversation.md` - pending
- `reverse_engineering_findings.md` - pending
- `reverse_engineering_findings_archive_engine_rendering.md` - pending
- `reverse_engineering_findings_archive_game_objects.md` - pending
- `reverse_engineering_findings_archive_resource_formats.md` - pending
- `reverse_engineering_findings_archive_toolset.md` - pending
- `reverse_engineering_findings_archive_tslpatcher.md` - pending
- `reverse_engineering_findings_py_kotor_migrated_docstrings.md` - pending
- `reverse_engineering_findings_py_kotor_migrated_io_mdl.md` - pending
- `UTC-Editor-Field-Types-AgentDecompile.md` - pending

## HoloPatcher and TSLPatcher pages

- `HoloPatcher.md` - pending
- `HoloPatcher-README-for-mod-developers.md` - pending
- `Installing-Mods-with-HoloPatcher.md` - pending
- `Explanations-on-HoloPatcher-Internal-Logic.md` - pending
- `TSLPatcher's-Official-Readme.md` - pending
- `TSLPatcher-Data-Syntax.md` - pending
- `TSLPatcher-2DAList-Syntax.md` - pending
- `TSLPatcher-GFF-Syntax.md` - pending
- `TSLPatcher-GFFList-Syntax.md` - pending
- `TSLPatcher-HACKList-Syntax.md` - pending
- `TSLPatcher-Install-and-Hack-Syntax.md` - pending
- `TSLPatcher-InstallList-Syntax.md` - pending
- `TSLPatcher-SSFList-Syntax.md` - pending
- `TSLPatcher-TLKList-Syntax.md` - pending

## Holocron Toolset and map-builder pages

- `Holocron-Toolset-Getting-Started.md` - pending
- `Holocron-Toolset-Core-Resources.md` - pending
- `Holocron-Toolset-Module-Resources.md` - pending
- `Holocron-Toolset-Module-Editor.md` - pending
- `Holocron-Toolset-Map-Builder.md` - pending
- `Holocron-Toolset-New-Features-Guide.md` - pending
- `Holocron-Toolset-Override-Resources.md` - pending
- `Indoor-Map-Builder-User-Guide.md` - pending
- `Indoor-Map-Builder-Implementation-Guide.md` - pending
- `Indoor-Area-Room-Layout-and-Walkmesh-Guide.md` - pending
- `Area-Modding-and-Room-Transitions.md` - pending

## Tutorials and workflows

- `Tutorial-Area-Transitions.md` - pending
- `Tutorial-Creating-a-New-Store.md` - pending
- `Tutorial-Creating-Custom-Robes.md` - pending
- `Tutorial-Creating-Static-Cameras.md` - pending

## Remaining topic pages

- `NWNNSSCOMP-Command-Line-Reference.md` - pending
