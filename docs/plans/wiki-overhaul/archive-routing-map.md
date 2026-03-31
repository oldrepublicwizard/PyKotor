# Wiki overhaul archive routing map

This map records where preserved historical, provenance, and evidence-heavy material lives in the final architecture and how readers are supposed to reach it.

## Reverse-engineering archive-support pages

| Archive page | Parent route | Role in final architecture | Notes |
|------|------|------|------|
| `wiki/reverse_engineering_findings_archive_engine_rendering.md` | `wiki/reverse_engineering_findings.md` | grouped evidence archive | engine, rendering, extraction, and MDL/model implementation links |
| `wiki/reverse_engineering_findings_archive_game_objects.md` | `wiki/reverse_engineering_findings.md` | grouped evidence archive | common game-object and shared-structure provenance |
| `wiki/reverse_engineering_findings_archive_resource_formats.md` | `wiki/reverse_engineering_findings.md` | grouped evidence archive | resource-format implementation links and supporting evidence |
| `wiki/reverse_engineering_findings_archive_toolset.md` | `wiki/reverse_engineering_findings.md` | grouped evidence archive | Holocron Toolset implementation provenance |
| `wiki/reverse_engineering_findings_archive_tslpatcher.md` | `wiki/reverse_engineering_findings.md` | grouped evidence archive | patcher implementation provenance |
| `wiki/reverse_engineering_findings_py_kotor_migrated_docstrings.md` | `wiki/reverse_engineering_findings.md` | migrated reference-text archive | preserved deep technical notes derived from migrated docstrings |
| `wiki/reverse_engineering_findings_py_kotor_migrated_io_mdl.md` | `wiki/reverse_engineering_findings.md` | migrated reference-text archive | preserved MDL binary I/O provenance notes |

## Preserved official and historical source artifacts

| Preserved page | Parent route | Role in final architecture | Notes |
|------|------|------|------|
| `wiki/Bioware-Aurora-Core-Formats.md` | KotOR-specific format pages and `wiki/Home.md` companion references | preserved official mirror | immutable grouped official reference |
| `wiki/Bioware-Aurora-Module-and-Area.md` | KotOR-specific module and area pages | preserved official mirror | immutable grouped official reference |
| `wiki/Bioware-Aurora-Creature.md` | creature and character-related GFF pages | preserved official mirror | immutable official reference |
| `wiki/Bioware-Aurora-Items-Economy-and-Narrative.md` | item, store, journal, and related pages | preserved official mirror | immutable grouped official reference |
| `wiki/Bioware-Aurora-Spatial-and-Interactive.md` | spatial-object and trigger-related pages | preserved official mirror | immutable grouped official reference |
| `wiki/Bioware-Aurora-Conversation.md` | dialogue and conversation routes | preserved official mirror | immutable official reference |
| `wiki/TSLPatcher's-Official-Readme.md` | `wiki/HoloPatcher.md` and syntax pages | preserved primary source | immutable legacy technical source |
| `wiki/TSLPatcher_Thread_Complete.md` | `wiki/HoloPatcher.md` | preserved historical archive | release-thread and provenance archive |

## Specialized residual pages retained outside the main routing spine

| Page | Parent route | Role in final architecture | Notes |
|------|------|------|------|
| `wiki/Ghidra-Reversing-Guide.md` | `wiki/reverse_engineering_findings.md` and contributor routes | specialized workflow reference | methodology guide, not a general landing page |
| `wiki/Kit-Structure-Documentation.md` | map-builder and area-creation routes | specialized project-structure reference | contributor/supporting page |
| `wiki/Qt-ItemView-Selection-and-RobustTableView.md` | toolset contributor routes | specialized framework reference | contributor/supporting page |
| `wiki/UTC-Editor-Field-Types-AgentDecompile.md` | toolset and RE contributor routes | specialized verified findings page | narrow contributor reference |

## Routing rules enforced by the final architecture

- archive-support pages are reached from synthesis or companion pages, not surfaced as peer-level first-stop destinations
- preserved official mirrors are cited and linked as companion authority, not treated as primary practical docs for first-time readers
- preserved TSLPatcher source artifacts are routed through the modern `wiki/HoloPatcher.md` hub rather than presented as the recommended entry path
- specialized residual pages are retained for contributor utility, but are not part of the public front-door navigation spine