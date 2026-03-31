# Wiki overhaul source-to-target consolidation matrix

This matrix records the exact end-state destination for every current wiki page in the live 62-file wiki and preserves the historical absorption notes needed to reconcile the original 324-file inventory.

## Final current-state matrix

Every current markdown file under `wiki/` appears below with its final destination, role, and survival status.

### Top-level hubs

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/Home.md` | `wiki/Home.md` | not absorbed | public front door for the toolchain | yes | `top-level-routing` | exhaustive for front-door routing | downstream families own detail pages; Home remains routing-only |
| `wiki/Concepts.md` | `wiki/Concepts.md` | not absorbed | canonical shared terminology and resolution-order hub | yes | `shared-concepts` | exhaustive | overlapping vocabulary was removed from workflow and registry pages |
| `wiki/Resource-Formats-and-Resolution.md` | `wiki/Resource-Formats-and-Resolution.md` | not absorbed | canonical resource-type and format index | yes | `format-index-vs-concepts` | exhaustive for registry content | long-form conceptual explanation stays on `wiki/Concepts.md` |
| `wiki/Wiki-Conventions.md` | `wiki/Wiki-Conventions.md` | not absorbed | canonical editorial contract for the rebuilt wiki | yes | `maintainer-governance` | exhaustive | artifact set and final wiki now align with this page |

### Tutorials and workflow pages

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/Area-Modding-and-Room-Transitions.md` | `wiki/Area-Modding-and-Room-Transitions.md` | not absorbed | workflow guide for room transitions and area assembly | yes | `area-workflows` | exhaustive workflow page | linked from adjacent area and map-builder docs |
| `wiki/Blender-Integration.md` | `wiki/Blender-Integration.md` | not absorbed | practical Blender-to-toolset workflow guide | yes | `toolset-blender-workflow` | exhaustive workflow page | positioned under workflow routes rather than as a front-door page |
| `wiki/Indoor-Area-Room-Layout-and-Walkmesh-Guide.md` | `wiki/Indoor-Area-Room-Layout-and-Walkmesh-Guide.md` | not absorbed | technical workflow for room layout and walkmesh authoring | yes | `area-workflows` | exhaustive workflow page | cross-linked with map builder and level-layout references |
| `wiki/Indoor-Map-Builder-Implementation-Guide.md` | `wiki/Indoor-Map-Builder-Implementation-Guide.md` | not absorbed | contributor-facing implementation guide for the map builder | yes | `map-builder-guides` | exhaustive contributor guide | explicitly framed as implementation guidance, not beginner help |
| `wiki/Indoor-Map-Builder-User-Guide.md` | `wiki/Indoor-Map-Builder-User-Guide.md` | not absorbed | task-oriented map-builder user guide | yes | `map-builder-guides` | exhaustive user guide | paired with the implementation guide without duplicating it |
| `wiki/KotorDiff-Integration.md` | `wiki/KotorDiff-Integration.md` | not absorbed | tool-integration workflow page | yes | `tool-integration-guides` | exhaustive workflow page | kept as a distinct task path |
| `wiki/Mod-Creation-Best-Practices.md` | `wiki/Mod-Creation-Best-Practices.md` | not absorbed | canonical authoring workflow and best-practice guide | yes | `mod-authoring-best-practices` | exhaustive | patcher and format pages defer here for broad workflow guidance |
| `wiki/Tutorial-Area-Transitions.md` | `wiki/Tutorial-Area-Transitions.md` | not absorbed | step-by-step tutorial for linking modules | yes | `tutorials` | exhaustive tutorial page | retained as a practical walkthrough |
| `wiki/Tutorial-Creating-a-New-Store.md` | `wiki/Tutorial-Creating-a-New-Store.md` | not absorbed | step-by-step tutorial for adding a store | yes | `tutorials` | exhaustive tutorial page | cross-linked from item and GFF pages |
| `wiki/Tutorial-Creating-Custom-Robes.md` | `wiki/Tutorial-Creating-Custom-Robes.md` | not absorbed | step-by-step tutorial for custom robes | yes | `tutorials` | exhaustive tutorial page | cross-linked from texture and item references |
| `wiki/Tutorial-Creating-Static-Cameras.md` | `wiki/Tutorial-Creating-Static-Cameras.md` | not absorbed | step-by-step tutorial for static cameras | yes | `tutorials` | exhaustive tutorial page | linked from area and conversation-related docs |

### Holocron Toolset family

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/Holocron-Toolset-Getting-Started.md` | `wiki/Holocron-Toolset-Getting-Started.md` | not absorbed | primary entry page for GUI editing workflows | yes | `holocron-getting-started` | exhaustive getting-started guide | downstream toolset pages defer here for overall orientation |
| `wiki/Holocron-Toolset-Core-Resources.md` | `wiki/Holocron-Toolset-Core-Resources.md` | not absorbed | task page for editing core game resources | yes | `holocron-core-resources` | exhaustive task page | sibling routing added across resource categories |
| `wiki/Holocron-Toolset-Map-Builder.md` | `wiki/Holocron-Toolset-Map-Builder.md` | not absorbed | task page for map-builder workflows | yes | `holocron-map-builder` | exhaustive task page | linked to area and layout guides |
| `wiki/Holocron-Toolset-Module-Editor.md` | `wiki/Holocron-Toolset-Module-Editor.md` | not absorbed | task page for module editing | yes | `holocron-module-editor` | exhaustive task page | linked to module resources and concepts |
| `wiki/Holocron-Toolset-Module-Resources.md` | `wiki/Holocron-Toolset-Module-Resources.md` | not absorbed | task page for module-scoped resources | yes | `holocron-module-resources` | exhaustive task page | lateral sibling links added during final validation |
| `wiki/Holocron-Toolset-New-Features-Guide.md` | `wiki/Holocron-Toolset-New-Features-Guide.md` | not absorbed | feature overview for recent toolset capabilities | yes | `holocron-new-features` | exhaustive feature guide | reframed around user tasks instead of UI-tour prose |
| `wiki/Holocron-Toolset-Override-Resources.md` | `wiki/Holocron-Toolset-Override-Resources.md` | not absorbed | task page for override editing workflows | yes | `holocron-override-resources` | exhaustive task page | sibling routing aligns with core and module resource pages |

### Patcher family

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/HoloPatcher.md` | `wiki/HoloPatcher.md` | not absorbed | unified modern patcher hub for players and mod authors | yes | `patcher-player-vs-author` | exhaustive modern hub | absorbed install, mod-developer, and implementation pages |
| `wiki/TSLPatcher-Data-Syntax.md` | `wiki/TSLPatcher-Data-Syntax.md` | not absorbed | consolidated syntax reference for data-style patch lists | yes | `patcher-syntax-guides` | exhaustive syntax | absorbs 2DAList, TLKList, and SSFList content |
| `wiki/TSLPatcher-GFF-Syntax.md` | `wiki/TSLPatcher-GFF-Syntax.md` | not absorbed | consolidated syntax reference for GFF patching | yes | `patcher-syntax-guides` | exhaustive syntax | absorbs GFFList content |
| `wiki/TSLPatcher-Install-and-Hack-Syntax.md` | `wiki/TSLPatcher-Install-and-Hack-Syntax.md` | not absorbed | consolidated syntax reference for install and binary patch operations | yes | `patcher-syntax-guides` | exhaustive syntax | absorbs InstallList and HACKList content |
| `wiki/TSLPatcher's-Official-Readme.md` | `wiki/TSLPatcher's-Official-Readme.md` | preserved source only | immutable historical source artifact | yes | `patcher-preserved-sources` | preserved source | modern pages route here for provenance rather than rewriting it |
| `wiki/TSLPatcher_Thread_Complete.md` | `wiki/TSLPatcher_Thread_Complete.md` | preserved archive only | immutable historical thread archive | yes | `patcher-preserved-sources` | preserved archive support | retained for provenance, not as a first-stop destination |

### Core format hubs and standalone format pages

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/2DA-File-Format.md` | `wiki/2DA-File-Format.md` | not absorbed | canonical 2DA reference hub after full stub consolidation | yes | `dup-2da-stubs-vs-hub` | exhaustive | 92 former stubs route here by anchor |
| `wiki/Audio-and-Localization-Formats.md` | `wiki/Audio-and-Localization-Formats.md` | not absorbed | consolidated audio and localization reference | yes | `audio-localization-formats` | exhaustive | absorbs TLK, SSF, LIP, and WAV reference roles |
| `wiki/Container-Formats.md` | `wiki/Container-Formats.md` | not absorbed | consolidated KEY/BIF/ERF/RIM container reference | yes | `container-ecosystem` | exhaustive | centralizes resource-container behavior |
| `wiki/Level-Layout-Formats.md` | `wiki/Level-Layout-Formats.md` | not absorbed | consolidated LYT/VIS/BWM reference | yes | `level-layout-formats` | exhaustive | centralizes area-layout formats and routing |
| `wiki/LTR-File-Format.md` | `wiki/LTR-File-Format.md` | not absorbed | standalone format page with distinct scope | yes | `ltr-format` | exhaustive | small enough and distinct enough to remain standalone |
| `wiki/MDL-MDX-File-Format.md` | `wiki/MDL-MDX-File-Format.md` | not absorbed | canonical model-format page with absorbed appendices | yes | `mdl-mdx-format` | exhaustive | MDL supplementary pages were absorbed as appendices |
| `wiki/NCS-File-Format.md` | `wiki/NCS-File-Format.md` | not absorbed | compiled bytecode reference page | yes | `nss-ncs-family` | exhaustive for bytecode | paired with NSS hub without duplicating scripting taxonomy |
| `wiki/NSS-File-Format.md` | `wiki/NSS-File-Format.md` | not absorbed | canonical scripting hub after 54-page absorption | yes | `nss-ncs-family` | exhaustive | manual TOC clutter removed; category navigation retained |
| `wiki/NWNNSSCOMP-Command-Line-Reference.md` | `wiki/NWNNSSCOMP-Command-Line-Reference.md` | not absorbed | standalone CLI reference with distinct utility | yes | `nss-ncs-family` | exhaustive CLI reference | kept as supporting script-tool reference |
| `wiki/Texture-Formats.md` | `wiki/Texture-Formats.md` | not absorbed | consolidated texture and TXI reference | yes | `texture-formats` | exhaustive | absorbs DDS, TPC, PLT, and TXI reference roles |

### GFF family

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/GFF-File-Format.md` | `wiki/GFF-File-Format.md` | not absorbed | canonical GFF container hub | yes | `gff-family-root` | exhaustive | generic GFF explanation centralized here |
| `wiki/GFF-Creature-and-Dialogue.md` | `wiki/GFF-Creature-and-Dialogue.md` | not absorbed | consolidated creature and dialogue schemas | yes | `gff-family-creature-dialogue` | exhaustive for its subtype group | absorbed UTC and DLG leaves |
| `wiki/GFF-GUI.md` | `wiki/GFF-GUI.md` | not absorbed | distinct GUI reference page | yes | `gff-family-gui` | exhaustive | retained because GUI scope is unique |
| `wiki/GFF-Items-and-Economy.md` | `wiki/GFF-Items-and-Economy.md` | not absorbed | consolidated items and economy schemas | yes | `gff-family-items-economy` | exhaustive for its subtype group | absorbed UTI, UTM, JRL, and FAC leaves |
| `wiki/GFF-Module-and-Area.md` | `wiki/GFF-Module-and-Area.md` | not absorbed | consolidated module and area schemas | yes | `gff-family-module-area` | exhaustive for its subtype group | absorbed ARE, GIT, and IFO leaves |
| `wiki/GFF-Spatial-Objects.md` | `wiki/GFF-Spatial-Objects.md` | not absorbed | consolidated spatial-object schemas | yes | `gff-family-spatial-objects` | exhaustive for its subtype group | absorbed UTD, UTP, UTT, UTE, UTS, UTW, and PTH leaves |

### Bioware-Aurora companion references

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/Bioware-Aurora-Core-Formats.md` | `wiki/Bioware-Aurora-Core-Formats.md` | preserved grouped mirror | official reference mirror grouped by related format topics | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved; routing demoted behind KotOR-specific hubs |
| `wiki/Bioware-Aurora-Conversation.md` | `wiki/Bioware-Aurora-Conversation.md` | preserved mirror | official conversation reference mirror | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved |
| `wiki/Bioware-Aurora-Creature.md` | `wiki/Bioware-Aurora-Creature.md` | preserved mirror | official creature reference mirror | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved |
| `wiki/Bioware-Aurora-Items-Economy-and-Narrative.md` | `wiki/Bioware-Aurora-Items-Economy-and-Narrative.md` | preserved grouped mirror | official items, economy, and narrative reference grouping | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved |
| `wiki/Bioware-Aurora-Module-and-Area.md` | `wiki/Bioware-Aurora-Module-and-Area.md` | preserved grouped mirror | official module and area reference grouping | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved |
| `wiki/Bioware-Aurora-Spatial-and-Interactive.md` | `wiki/Bioware-Aurora-Spatial-and-Interactive.md` | preserved grouped mirror | official spatial and interactive reference grouping | yes | `bioware-aurora-companion` | preserved source artifact | immutable content preserved |

### Reverse-engineering synthesis and archives

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/reverse_engineering_findings.md` | `wiki/reverse_engineering_findings.md` | not absorbed | canonical synthesis hub for advanced engine-facing material | yes | `dup-re-synthesis-vs-archive` | exhaustive synthesis hub | 69 former fragment pages reconciled into the hub and archive-support pages |
| `wiki/reverse_engineering_findings_archive_engine_rendering.md` | `wiki/reverse_engineering_findings_archive_engine_rendering.md` | preserved archive-support page | grouped evidence archive for engine, rendering, and extraction topics | yes | `dup-re-synthesis-vs-archive` | archive support | only reached through synthesis routing and related pages |
| `wiki/reverse_engineering_findings_archive_game_objects.md` | `wiki/reverse_engineering_findings_archive_game_objects.md` | preserved archive-support page | grouped evidence archive for game objects and shared structures | yes | `dup-re-synthesis-vs-archive` | archive support | only reached through synthesis routing and related pages |
| `wiki/reverse_engineering_findings_archive_resource_formats.md` | `wiki/reverse_engineering_findings_archive_resource_formats.md` | preserved archive-support page | grouped evidence archive for resource-format internals | yes | `dup-re-synthesis-vs-archive` | archive support | only reached through synthesis routing and related pages |
| `wiki/reverse_engineering_findings_archive_toolset.md` | `wiki/reverse_engineering_findings_archive_toolset.md` | preserved archive-support page | grouped evidence archive for toolset/editor internals | yes | `dup-re-synthesis-vs-archive` | archive support | only reached through synthesis routing and related pages |
| `wiki/reverse_engineering_findings_archive_tslpatcher.md` | `wiki/reverse_engineering_findings_archive_tslpatcher.md` | preserved archive-support page | grouped evidence archive for patcher internals | yes | `dup-re-synthesis-vs-archive` | archive support | only reached through synthesis routing and related pages |
| `wiki/reverse_engineering_findings_py_kotor_migrated_docstrings.md` | `wiki/reverse_engineering_findings_py_kotor_migrated_docstrings.md` | preserved archive-support page | migrated reference text archive for resource-format engine notes | yes | `dup-re-synthesis-vs-archive` | archive support | retained for provenance and deep contributor tracing |
| `wiki/reverse_engineering_findings_py_kotor_migrated_io_mdl.md` | `wiki/reverse_engineering_findings_py_kotor_migrated_io_mdl.md` | preserved archive-support page | migrated reference text archive for MDL binary I/O notes | yes | `dup-re-synthesis-vs-archive` | archive support | retained for provenance and deep contributor tracing |

### Specialized residual pages

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/Ghidra-Reversing-Guide.md` | `wiki/Ghidra-Reversing-Guide.md` | not absorbed | distinct reverse-engineering methodology guide | yes | `specialized-residual` | exhaustive for its niche workflow | retained because it serves a unique contributor task |
| `wiki/Kit-Structure-Documentation.md` | `wiki/Kit-Structure-Documentation.md` | not absorbed | distinct project-structure reference for kits and indoor content | yes | `specialized-residual` | exhaustive for its niche reference | retained because no broader page can absorb it cleanly |
| `wiki/Qt-ItemView-Selection-and-RobustTableView.md` | `wiki/Qt-ItemView-Selection-and-RobustTableView.md` | not absorbed | distinct UI framework reference for toolset contributors | yes | `specialized-residual` | exhaustive for its niche reference | retained because it documents a narrow but unique framework concern |
| `wiki/UTC-Editor-Field-Types-AgentDecompile.md` | `wiki/UTC-Editor-Field-Types-AgentDecompile.md` | not absorbed | distinct agentdecompile-backed reference page | yes | `specialized-residual` | exhaustive for its niche RE finding | retained because it captures a narrow, verified contributor topic |

## Historical absorbed and removed inventory groups

These rows reconcile the original pre-consolidation inventory against the final 62-page state.

| Source path | Target file path | Target section or appendix destination if absorbed | Justification for consolidation | Survives as standalone file in final `<=100` | Exhaustive-topic identifier | Summary-versus-exhaustive role after consolidation | No-omission reconciliation note |
|------|------|------|------|------|------|------|------|
| `wiki/2DA-acbonus.md` through `wiki/2DA-weaponsounds.md` (92 files) | `wiki/2DA-File-Format.md` | absorbed into existing `### tablename.2da` sections | per-table stubs duplicated the hub content exactly and created peer-level overload | no | `dup-2da-stubs-vs-hub` | absorbed | all 92 pages were reconciled; 96 inbound links were rewritten to hub anchors |
| `wiki/NSS-Shared-*`, `wiki/NSS-K1-Only-*`, and `wiki/NSS-TSL-Only-*` (54 files) | `wiki/NSS-File-Format.md` | absorbed into category sections already present in the consolidated hub | family was search-rich but orientation-poor; one scripting hub now owns discovery | no | `nss-family-consolidated` | absorbed | all category leaves were reconciled into the hub and relinked before deletion |
| `wiki/GFF-ARE.md`, `wiki/GFF-GIT.md`, `wiki/GFF-IFO.md`, `wiki/GFF-UTC.md`, `wiki/GFF-DLG.md`, `wiki/GFF-UTD.md`, `wiki/GFF-UTE.md`, `wiki/GFF-UTI.md`, `wiki/GFF-UTM.md`, `wiki/GFF-UTP.md`, `wiki/GFF-UTS.md`, `wiki/GFF-UTT.md`, `wiki/GFF-UTW.md`, `wiki/GFF-PTH.md`, `wiki/GFF-FAC.md`, `wiki/GFF-JRL.md` | consolidated GFF family pages | absorbed into family group pages | leaf-level subtype pages duplicated family introductions and fragmented navigation | no | `gff-family-consolidated` | absorbed | unique subtype detail was preserved under the grouped family pages |
| `wiki/BIF-File-Format.md`, `wiki/ERF-File-Format.md`, `wiki/KEY-File-Format.md`, `wiki/RIM-File-Format.md` | `wiki/Container-Formats.md` | absorbed into per-format sections | container ecosystem works better as one canonical parent page | no | `container-ecosystem` | absorbed | unique per-format details remain as dedicated sections |
| `wiki/TLK-File-Format.md`, `wiki/SSF-File-Format.md`, `wiki/LIP-File-Format.md`, `wiki/WAV-File-Format.md` | `wiki/Audio-and-Localization-Formats.md` | absorbed into per-format sections | localization and audio formats share one discovery path | no | `audio-localization-formats` | absorbed | unique format detail preserved in the grouped page |
| `wiki/DDS-File-Format.md`, `wiki/TPC-File-Format.md`, `wiki/PLT-File-Format.md`, `wiki/TXI-File-Format.md` | `wiki/Texture-Formats.md` | absorbed into per-format sections | texture formats benefit from consolidated sibling routing | no | `texture-formats` | absorbed | unique format detail preserved in the grouped page |
| `wiki/LYT-File-Format.md`, `wiki/VIS-File-Format.md`, `wiki/BWM-File-Format.md` | `wiki/Level-Layout-Formats.md` | absorbed into per-format sections | area-layout formats are best consumed together | no | `level-layout-formats` | absorbed | unique format detail preserved in the grouped page |
| `wiki/Installing-Mods-with-HoloPatcher.md`, `wiki/HoloPatcher-README-for-mod-developers.md`, `wiki/Explanations-on-HoloPatcher-Internal-Logic.md` | `wiki/HoloPatcher.md` | absorbed into player, author, and implementation sections | modern patcher narrative required one parent hub instead of three competing pages | no | `dup-patcher-player-vs-author` | absorbed | all unique workflow and implementation content was preserved in the unified page |
| `wiki/TSLPatcher-2DAList-Syntax.md`, `wiki/TSLPatcher-TLKList-Syntax.md`, `wiki/TSLPatcher-SSFList-Syntax.md`, `wiki/TSLPatcher-GFFList-Syntax.md`, `wiki/TSLPatcher-InstallList-Syntax.md`, `wiki/TSLPatcher-HACKList-Syntax.md` | consolidated patcher syntax pages | absorbed into `TSLPatcher-Data-Syntax.md`, `TSLPatcher-GFF-Syntax.md`, and `TSLPatcher-Install-and-Hack-Syntax.md` | list-type syntax pages were too fragmented and repeated their framing | no | `dup-patcher-syntax-guides` | absorbed | each list-type syntax block has a preserved destination in the consolidated set |
| `wiki/Bioware-Aurora-2DA.md`, `wiki/Bioware-Aurora-ERF.md`, `wiki/Bioware-Aurora-GFF.md`, `wiki/Bioware-Aurora-KeyBIF.md`, `wiki/Bioware-Aurora-TalkTable.md`, `wiki/Bioware-Aurora-LocalizedStrings.md`, `wiki/Bioware-Aurora-SSF.md`, `wiki/Bioware-Aurora-AreaFile.md`, `wiki/Bioware-Aurora-CommonGFFStructs.md`, `wiki/Bioware-Aurora-DoorPlaceableGFF.md`, `wiki/Bioware-Aurora-Encounter.md`, `wiki/Bioware-Aurora-IFO.md`, `wiki/Bioware-Aurora-Item.md`, `wiki/Bioware-Aurora-Journal.md`, `wiki/Bioware-Aurora-PaletteITP.md`, `wiki/Bioware-Aurora-SoundObject.md`, `wiki/Bioware-Aurora-Store.md`, `wiki/Bioware-Aurora-Trigger.md`, `wiki/Bioware-Aurora-Waypoint.md` | grouped Bioware-Aurora companion pages | absorbed into grouped mirror pages by topic | official mirrors were preserved but grouped to reduce peer-level sprawl | no | `bioware-aurora-companion` | absorbed into preserved groupings | mirror content stayed intact while discovery was simplified |
| `wiki/reverse_engineering_findings_*_pre_scrub.md` fragment pages and `wiki/reverse_engineering_findings_library_github_url_archives_index.md` | RE synthesis hub and grouped RE archive pages | absorbed by subsystem and provenance grouping | raw archive fragments needed subsystem-based routing and consolidation | no | `dup-re-synthesis-vs-archive` | absorbed or grouped archive support | 77-page RE family reconciled to one hub plus seven grouped archive-support pages |
| `wiki/_mdl_section_rewrite.md`, `wiki/MDL-ASCII-Support-Engine-Analysis.md`, `wiki/MDL-Implementation-Verification-Report.md` | `wiki/MDL-MDX-File-Format.md` | appendix material within the MDL page | supplementary MDL notes belonged with the canonical model-format reference | no | `mdl-mdx-format` | absorbed appendix support | model-format details preserved inside the canonical page |