# Wiki overhaul navigation spine map

This map records the final parent-child routing model for the rebuilt 62-page wiki.

## Allowed first-stop destinations

| First-stop page | Audience | Role | Primary downstream routes |
|------|------|------|------|
| `wiki/Home.md` | all readers | public front door | `Concepts.md`, `Resource-Formats-and-Resolution.md`, `HoloPatcher.md`, `Holocron-Toolset-Getting-Started.md`, `reverse_engineering_findings.md` |
| `wiki/Concepts.md` | mod authors, tool authors | canonical terminology and resolution hub | `Resource-Formats-and-Resolution.md`, workflow pages, format pages |
| `wiki/Resource-Formats-and-Resolution.md` | mod authors, tool authors | canonical format and resource index | `2DA-File-Format.md`, `Container-Formats.md`, `GFF-File-Format.md`, `Texture-Formats.md`, `Audio-and-Localization-Formats.md`, `Level-Layout-Formats.md`, `MDL-MDX-File-Format.md`, `NCS-File-Format.md`, `NSS-File-Format.md`, `LTR-File-Format.md` |
| `wiki/Holocron-Toolset-Getting-Started.md` | GUI users | Holocron Toolset hub | `Holocron-Toolset-Core-Resources.md`, `Holocron-Toolset-Module-Resources.md`, `Holocron-Toolset-Override-Resources.md`, `Holocron-Toolset-Module-Editor.md`, `Holocron-Toolset-Map-Builder.md`, `Holocron-Toolset-New-Features-Guide.md` |
| `wiki/HoloPatcher.md` | players and mod authors | modern patcher hub | `TSLPatcher-Data-Syntax.md`, `TSLPatcher-GFF-Syntax.md`, `TSLPatcher-Install-and-Hack-Syntax.md`, `Mod-Creation-Best-Practices.md`, preserved source pages |
| `wiki/reverse_engineering_findings.md` | advanced contributors | synthesis hub for engine-facing analysis | grouped RE archive pages and migrated provenance pages |
| `wiki/Wiki-Conventions.md` | maintainers | editorial contract | overhaul artifacts and future maintenance work |

## Family routing

### Top-level hubs

| Parent | Children |
|------|------|
| `wiki/Home.md` | `wiki/Concepts.md`, `wiki/Resource-Formats-and-Resolution.md`, `wiki/HoloPatcher.md`, `wiki/Holocron-Toolset-Getting-Started.md`, `wiki/reverse_engineering_findings.md`, major workflow pages |
| `wiki/Concepts.md` | all format and workflow pages that need shared vocabulary |
| `wiki/Resource-Formats-and-Resolution.md` | all core format hubs and standalone format pages |

### Holocron Toolset

| Parent | Children |
|------|------|
| `wiki/Holocron-Toolset-Getting-Started.md` | `wiki/Holocron-Toolset-Core-Resources.md`, `wiki/Holocron-Toolset-Module-Resources.md`, `wiki/Holocron-Toolset-Override-Resources.md`, `wiki/Holocron-Toolset-Module-Editor.md`, `wiki/Holocron-Toolset-Map-Builder.md`, `wiki/Holocron-Toolset-New-Features-Guide.md` |

### Patcher family

| Parent | Children |
|------|------|
| `wiki/HoloPatcher.md` | `wiki/TSLPatcher-Data-Syntax.md`, `wiki/TSLPatcher-GFF-Syntax.md`, `wiki/TSLPatcher-Install-and-Hack-Syntax.md`, `wiki/TSLPatcher's-Official-Readme.md`, `wiki/TSLPatcher_Thread_Complete.md` |

### Format ecosystem

| Parent | Children |
|------|------|
| `wiki/Resource-Formats-and-Resolution.md` | `wiki/2DA-File-Format.md`, `wiki/Container-Formats.md`, `wiki/GFF-File-Format.md`, `wiki/Texture-Formats.md`, `wiki/Audio-and-Localization-Formats.md`, `wiki/Level-Layout-Formats.md`, `wiki/MDL-MDX-File-Format.md`, `wiki/NCS-File-Format.md`, `wiki/NSS-File-Format.md`, `wiki/LTR-File-Format.md` |
| `wiki/GFF-File-Format.md` | `wiki/GFF-Creature-and-Dialogue.md`, `wiki/GFF-GUI.md`, `wiki/GFF-Items-and-Economy.md`, `wiki/GFF-Module-and-Area.md`, `wiki/GFF-Spatial-Objects.md` |
| `wiki/NSS-File-Format.md` | in-page category routes for shared, K1-only, and TSL-only scripting material |
| `wiki/2DA-File-Format.md` | in-page per-table anchors replacing former 2DA leaf pages |

### Workflow and tutorial routes

| Parent or entry route | Children |
|------|------|
| `wiki/Home.md` and `wiki/Mod-Creation-Best-Practices.md` | tutorials, patcher workflows, toolset workflows |
| `wiki/Holocron-Toolset-Map-Builder.md` | `wiki/Indoor-Map-Builder-User-Guide.md`, `wiki/Indoor-Map-Builder-Implementation-Guide.md`, `wiki/Indoor-Area-Room-Layout-and-Walkmesh-Guide.md` |
| `wiki/Area-Modding-and-Room-Transitions.md` | `wiki/Tutorial-Area-Transitions.md`, `wiki/Level-Layout-Formats.md`, `wiki/Concepts.md` |

### Reverse-engineering routing

| Parent | Children |
|------|------|
| `wiki/reverse_engineering_findings.md` | `wiki/reverse_engineering_findings_archive_engine_rendering.md`, `wiki/reverse_engineering_findings_archive_game_objects.md`, `wiki/reverse_engineering_findings_archive_resource_formats.md`, `wiki/reverse_engineering_findings_archive_toolset.md`, `wiki/reverse_engineering_findings_archive_tslpatcher.md`, `wiki/reverse_engineering_findings_py_kotor_migrated_docstrings.md`, `wiki/reverse_engineering_findings_py_kotor_migrated_io_mdl.md` |

## Pages that must not behave as first-stop destinations

- individual archive-support pages under `reverse_engineering_findings_archive_*`
- migrated provenance pages under `reverse_engineering_findings_py_kotor_*`
- Bioware-Aurora companion mirrors
- preserved TSLPatcher source artifacts

These pages remain reachable through controlled parent routes, but are intentionally not presented as peer-level first stops.