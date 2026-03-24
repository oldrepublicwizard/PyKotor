# Welcome to the PyKotor Wiki

## Documentation

### KotOR modding toolchain (SDK overview)

[OldRepublicDevs/PyKotor](https://github.com/OldRepublicDevs/PyKotor) is a **source-available** spine for formats, HoloPatcher, Holocron Toolset, CLI automation, and KotorDiff. This wiki emphasizes **concepts** (resource resolution, patch semantics, binary layouts) so skills transfer across executables. **Interop first:** you do not have to abandon KotOR Tool, K-GFF, xoreos-tools, or other workflows that already work for you—use installers when you need safe [2DA](2DA-File-Format) / [TLK](TLK-File-Format) / [GFF](GFF-File-Format) merges, and use [Concepts](Concepts) plus format pages as SSOT for behavior.

**Non-goals:** “PyKotor only” or “replace every legacy tool.” **Cross-implementation references** on many pages point to [reone](https://github.com/modawan/reone), [KotOR.js](https://github.com/KobaltBlu/KotOR.js), and [Kotor.NET](https://github.com/NickHugi/Kotor.NET) with line anchors where practical.

A high-level **author → automate → player** diagram lives on [HoloPatcher internal logic — Toolchain flow](Explanations-on-HoloPatcher-Internal-Logic#toolchain-flow-high-level).

#### When to use which part of the stack

| You need | Start here | Alternatives |
| -------- | ---------- | ------------- |
| Install or revert a mod | [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) | Copy to `override/`; [KotORModSync](https://github.com/th3w1zard1/KotORModSync) for multi-mod workflows |
| Author HoloPatcher / TSLPatcher INI | [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) | [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) |
| Merge 2DA / TLK / GFF | HoloPatcher INI ([2DAList](TSLPatcher-2DAList-Syntax), [TLKList](TSLPatcher-TLKList-Syntax), [GFFList](TSLPatcher-GFFList-Syntax)) | Manual merge (fragile); state load order in readme |
| Edit resources in a GUI | [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) | KotOR Tool, K-GFF |
| Headless convert / pack / kit | [CLI quickstart](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md) (`uv run pykotor`, `pykotorcli`) | [xoreos-tools](https://github.com/xoreos/xoreos-tools) |
| Compare installs or emit patch data | [KotorDiff Integration](KotorDiff-Integration) | Manual diff |
| Resolution order and vocabulary | [Concepts](Concepts) | [Resource formats and resolution](Resource-Formats-and-Resolution) |

#### Learning paths

- **New player:** [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) → if conflicts or missing textures, [Concepts — resource resolution](Concepts#resource-resolution-order) and [Mod Creation Best Practices — testing](Mod-Creation-Best-Practices#testing-and-compatibility) → [Community sources](#community-sources-and-archives).
- **First mod author:** [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) (includes a **first-mod walkthrough**) → deep-dive [2DA](2DA-File-Format) or [GFF](GFF-File-Format) → [Mod Creation Best Practices](Mod-Creation-Best-Practices).
- **Contributor / integrator:** [Wiki Conventions](Wiki-Conventions) → PyKotor [`resource/formats/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats) and NSS/format **Implementation cross-reference** blocks (reone, KotOR.js, Kotor.NET).

**Start here (compact):** [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) → [Mod Creation Best Practices](Mod-Creation-Best-Practices) → [File formats and specifications](#file-formats-and-specifications) or [TSLPatcher guides](TSLPatcher's-Official-Readme) as needed. Core terms: [Concepts](Concepts); format index and type IDs: [Resource formats and resolution](Resource-Formats-and-Resolution). Binary and engine-level detail: [Low-level structures and implementations](#low-level-structures-and-implementations). [Community sources and archives](#community-sources-and-archives). Contributing: [Wiki Conventions](Wiki-Conventions).

### For End Users

- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher)

### Guides and tutorials

Installation, tool use, and step-by-step guides:

- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers)
- [HoloPatcher Feature Coverage Overview](Explanations-on-HoloPatcher-Internal-Logic)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)
- [TSLPatcher Thread Complete Container](TSLPatcher_Thread_Complete)
- **[TSLPatcher InstallList Syntax Guide](TSLPatcher-InstallList-Syntax)** -- File installation
- **[TSLPatcher TLKList Syntax Guide](TSLPatcher-TLKList-Syntax)** -- TLK ([TalkTable](TLK-File-Format)) modifications
- **[TSLPatcher 2DAList Syntax Guide](TSLPatcher-2DAList-Syntax)** -- [2DA](2DA-File-Format) patches
- **[TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax)** -- [GFF](GFF-File-Format) modifications
- **[TSLPatcher SSFList Syntax Guide](TSLPatcher-SSFList-Syntax)** -- SSF ([sound set files](SSF-File-Format))
- **[TSLPatcher HACKList Syntax Guide](TSLPatcher-HACKList-Syntax)** -- Binary patches
- [Blender Integration](Blender-Integration)
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- Build indoor modules from kits
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) -- Understanding why room crossing fails and what must agree: layout, walkmesh, roomlinks, LYT/VIS
- [Indoor Area Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide) -- Complete modder workflow for indoor rooms, walkmeshes, roomlinks, doors, LYT, and VIS
- [KotorDiff Integration in PyKotorCLI](KotorDiff-Integration)

**Holocron Toolset (in-app help):**

- [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started)
- [Holocron Toolset: New Features Quick Guide](Holocron-Toolset-New-Features-Guide) -- Favorites, batch ops, rename, Open With, etc.
- [Holocron Toolset: Core resources](Holocron-Toolset-Core-Resources) -- Core tab (KEY/BIF)
- [Holocron Toolset: Module resources](Holocron-Toolset-Module-Resources)
- [Holocron Toolset: Override resources](Holocron-Toolset-Override-Resources)
- [Holocron Toolset: Module Editor](Holocron-Toolset-Module-Editor) -- Module Designer controls
- [Holocron Toolset: Map Builder](Holocron-Toolset-Map-Builder) -- Indoor Map Builder controls

**Tutorials:**

- [Tutorial: Creating custom robes](Tutorial-Creating-Custom-Robes)
- [Tutorial: Creating a new store](Tutorial-Creating-a-New-Store)
- [Tutorial: Area transitions](Tutorial-Area-Transitions)
- [Tutorial: Creating static cameras](Tutorial-Creating-Static-Cameras)

**Scripting (NWScript):** Function and constant reference for writing scripts. Full index and all routine/constant pages: [NSS File Format](NSS-File-Format). Quick links to major categories:

- [NSS Shared Functions: Actions](NSS-Shared-Functions-Actions) · [Combat](NSS-Shared-Functions-Combat-Functions) · [Dialog and conversation](NSS-Shared-Functions-Dialog-and-Conversation-Functions) · [Effects](NSS-Shared-Functions-Effects-System) · [Item management](NSS-Shared-Functions-Item-Management) · [Module and area](NSS-Shared-Functions-Module-and-Area) · [Party](NSS-Shared-Functions-Party-Management) · [Skills and feats](NSS-Shared-Functions-Skills-and-Feats)
- [NSS Shared Constants: Ability](NSS-Shared-Constants-Ability-Constants) · [Object type](NSS-Shared-Constants-Object-Type-Constants) · [Class type](NSS-Shared-Constants-Class-Type-Constants) · [Visual effects](NSS-Shared-Constants-Visual-Effects-%28VFX%29)
- [NSS K1-Only constants and functions](NSS-K1-Only-Constants-NPC-Constants) (see [NSS File Format](NSS-File-Format) for full K1 index)
- [NSS TSL-Only constants and functions](NSS-TSL-Only-Functions-Combat-Functions) (see [NSS File Format](NSS-File-Format) for full TSL index)

### File formats and specifications

Reference for binary layout, field definitions, and format behaviour. For scripting usage see [Scripting (NWScript)](#guides-and-tutorials) above; for implementation details see [Low-level structures and implementations](#low-level-structures-and-implementations).

### Official Bioware Aurora Documentation

The following documents are official Bioware Aurora Engine file format specifications. These are authoritative references for the underlying file formats used by KotOR:

- **[2DA File Format](Bioware-Aurora-2DA)** - Official 2DA (Two-Dimensional array) format specification
- **[GFF File Format](Bioware-Aurora-GFF)** - Official Generic file format specification
- **[Common GFF Structs](Bioware-Aurora-CommonGFFStructs)** - Common [GFF](GFF-File-Format) structure definitions
- **[Area File Format](Bioware-Aurora-AreaFile)** - Official ARE (Area) file format
- **[Creature Format](Bioware-Aurora-Creature)** - Official UTC (Creature) format
- **[Item Format](Bioware-Aurora-Item)** - Official UTI (Item) format
- **[Door/Placeable Format](Bioware-Aurora-DoorPlaceableGFF)** - Official [UTD](GFF-File-Format#utd-door)/[UTP](GFF-File-Format#utp-placeable) formats
- **[Encounter Format](Bioware-Aurora-Encounter)** - Official UTE (Encounter) format
- **[Trigger Format](Bioware-Aurora-Trigger)** - Official UTT (Trigger) format
- **[Waypoint Format](Bioware-Aurora-Waypoint)** - Official UTW (Waypoint) format
- **[Store Format](Bioware-Aurora-Store)** - Official UTM (Store) format
- **[Sound Object Format](Bioware-Aurora-SoundObject)** - Official UTS (Sound) format
- **[Journal Format](Bioware-Aurora-Journal)** - Official JRL (Journal) format
- **[Conversation Format](Bioware-Aurora-Conversation)** - Official DLG (Dialogue) format
- **[IFO Format](Bioware-Aurora-IFO)** - Official [module info](GFF-File-Format#ifo-module-info) format
- **[ERF Format](Bioware-Aurora-ERF)** - Official Encapsulated Resource format
- **[Key/BIF Format](Bioware-Aurora-KeyBIF)** - Official [KEY](KEY-File-Format) and [BIF file](BIF-File-Format) formats
- **[TalkTable Format](Bioware-Aurora-TalkTable)** - Official TLK ([Talk Table](TLK-File-Format)) format
- **[SSF Format](Bioware-Aurora-SSF)** - Official [sound set files](SSF-File-Format) format
- **[Localized Strings Format](Bioware-Aurora-LocalizedStrings)** - Official localized strings format
- **[Faction Format](Bioware-Aurora-Faction)** - Official faction data format
- **[Palette/ITP Format](Bioware-Aurora-PaletteITP)** - Official palette and ITP formats

### Odyssey Engine Basics (KotOR)

The following information describes the resource system used by **KotOR and TSL**. While KotOR is derived from the Aurora engine (Neverwinter Nights) and shares the same resource system, this section focuses on **KotOR-specific** behavior and file locations. Some details (like `nwn.ini`) are NWN-specific and are noted as such.

#### Application lifecycle (KotOR and TSL)

Both games use the same high-level flow: the executable initializes an application manager, creates a server (game world) and client (rendering, input, UI), then runs a main loop that pumps window messages, updates the render window, and drives the Aurora/Odyssey subsystems. Resource loading follows the [resource resolution order](Concepts#resource-resolution-order); the resource manager services requests from override, then module [RIM](RIM-File-Format)/[ERF](ERF-File-Format) capsules, then KEY/BIF. Reinitializing the Aurora engine (e.g. after resolution or display changes) reloads or refreshes core subsystems while preserving the same client/server split. Scripts (NCS) and dialogues (DLG) run in the server context; the client handles display, camera, and input and receives updates from the server.

**Client and server:** The Odyssey engine (like Aurora) separates a **server** (game world, rules, scripts, resources) from a **client** (rendering, input, UI). The server owns area state, creatures, items, and script execution; the client displays the world and sends input. This split is important for modding and for understanding [NCS execution](NCS-File-Format) and [resource resolution](Concepts#resource-resolution-order).

#### Important Files

- **[`chitin.key`](KEY-File-Format)**: Master index file that maps resource names to [BIF containers](BIF-File-Format) locations. Given a resource name, [chitin.key](KEY-File-Format) can be used to locate the master data file ([BIF](BIF-File-Format)) containing the resource.
- **[`dialog.tlk`](TLK-File-Format)**: Text resource file containing localized strings referenced by [StrRef](TLK-File-Format#string-references-strref) IDs. This centralizes strings for easy localization and allows changing text without modifying or recompiling scripts. Different language versions of [dialog.tlk](TLK-File-Format) can be installed for localization support.
- **`kotor.ini`**: Configuration file with `[Alias]` section mapping logical directory names to physical paths. This allows the game to locate data files regardless of installation directory structure.

**Reference:** [xoreos-docs](https://github.com/xoreos/xoreos-docs) — [`specs/torlack/basics.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html) (Tim Smith / Torlack; NWN-focused Aurora basics).

#### Resource system (see Concepts)

- **Lookup order and how demands are satisfied:** [Concepts — Resource resolution order](Concepts#resource-resolution-order)
- **Hex resource type IDs:** [Resource formats and resolution — Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)
- **Language IDs** (`dialog.tlk`, localization): [Concepts — Language IDs](Concepts#language-ids-kotor)
- **KEY file role and binary format:** [KEY-File-Format](KEY-File-Format)
- **Format page index (all extensions, ResRef, resolution order):** [Resource formats and resolution](Resource-Formats-and-Resolution)

### File format index

The linked table of contents for format pages (2DA anchors, GFF variants, archives, media) lives on **[Resource formats and resolution](Resource-Formats-and-Resolution)** together with [ResRef / resource type](Resource-Formats-and-Resolution#resref-and-resource-type) and the [hex resource type ID table](Resource-Formats-and-Resolution#resource-type-identifiers). Narrative resolution order: [Concepts](Concepts#resource-resolution-order).

### Low-level structures and implementations

Binary layout, engine behaviour, and implementation details for developers and reverse engineering. These pages are **conceptual summaries** for the wiki (no raw tool dumps); see [Wiki Conventions](Wiki-Conventions) and [AGENTS.md](https://github.com/OldRepublicDevs/PyKotor/blob/main/AGENTS.md) for project policy.

- [Reverse Engineering Findings](reverse_engineering_findings) (includes `CExoResMan` / resource manager notes and BWM / AABB / walkmesh engine analysis)
- [Qt ItemView selection and RobustTableView](Qt-ItemView-Selection-and-RobustTableView)
- [UTC Editor field types (AgentDecompile)](UTC-Editor-Field-Types-AgentDecompile)
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) -- Technical details (distinct from the [user guide](Indoor-Map-Builder-User-Guide) in Guides and tutorials)
- [HoloPatcher internal logic](Explanations-on-HoloPatcher-Internal-Logic)

## Cross-reference: other tools and engines

PyKotor is not the only KotOR tooling ecosystem. Below are other engines, libraries, and community projects (canonical repository links; compare with [OldRepublicDevs](https://github.com/OldRepublicDevs) for PyKotor, kotorblender, bioware-kaitai-formats, and related repos).

### Engine Reimplementations

Complete game engine rewrites that can load and play KotOR:

- **[xoreos](https://github.com/xoreos/xoreos)** - C++ reimplementation of BioWare's Aurora/Odyssey/Eclipse engine, supports multiple BioWare games including KotOR.
- **[reone](https://github.com/modawan/reone)** — Community-maintained continuation of the modern C++ KotOR engine (OpenGL). Historical upstream: [seedhartha/reone](https://github.com/seedhartha/reone).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** - TypeScript/JavaScript engine running in browsers via WebGL. Enables playing KotOR directly in web browsers.
- **[NorthernLights](https://github.com/lachjames/NorthernLights)** - .NET/C# engine implementation with Unity integration capabilities (based on KotOR-Unity project with further improvements)
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)** - Unity-based KotOR engine rewrite. Leverages Unity's rendering and physics.

### File Format Libraries

Libraries focused on reading/writing KotOR file formats:

- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** - Command-line tools for extracting and converting Aurora file formats
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** - .NET library for KotOR file formats with builder APIs
- **[BioWare.NET](https://github.com/th3w1zard1/BioWare.NET)** - Another .NET library for KotOR file formats, intended to be a direct port of PyKotor
- **[Rakata](https://codeberg.org/Synchro/rakata)** - A rust-native codebase for working with the Odyssey engine.

### 3D Modeling Tools

Tools for working with KotOR 3D [models](MDL-MDX-File-Format) and [textures](TPC-File-Format):

- **[kotorblender](https://github.com/OldRepublicDevs/kotorblender)** - Blender add-on for importing/exporting KotOR [MDL files](MDL-MDX-File-Format), [LYT layouts](LYT-File-Format), [PTH paths](GFF-PTH), and [walkmeshes](BWM-File-Format) with active Holocron Toolset bridge support (see [Blender Integration](Blender-Integration))
- **[mdlops](https://github.com/ndixUR/mdlops)** - Legacy Python [MDL](MDL-MDX-File-Format) toolkit for [model](MDL-MDX-File-Format) conversions
- **[tga2tpc](https://github.com/ndixUR/tga2tpc)** - Standalone TGA to [TPC](TPC-File-Format) [texture](TPC-File-Format) converter
- **[DLZ-Tool](https://github.com/LaneDibello/DLZ-Tool)** - DLZ file decompression tool
- **[WalkmeshVisualizer](https://github.com/glasnonck/WalkmeshVisualizer)** - [walkmesh](BWM-File-Format) viewing and debugging tool

### Script Development

Tools and Resources for working with NWScript in KotOR:

- **[HoloLSP](https://github.com/th3w1zard1/HoloLSP)** - Language Server Protocol implementation for NWScript, complete with all kotor-specific constants and functions, as well as everything else from each game's (k1/tsl's) `nwscript.nss`
- **[nwscript-mode.el](https://github.com/implicit-image/nwscript-mode.el)** - Emacs major mode for NWScript editing
- **[Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source)** - Decompiled vanilla KotOR scripts for reference

### Modding Tools

Tools for creating and installing mods:

- **PyKotorCLI (PyKotor)** - CLI-first toolset for packing, conversion, Holocron kit generation, and [GUI](GFF-File-Format#gui-graphical-user-interface) layout scaling. `uvx --refresh pykotor kit-generate --installation <path> --module <module> --output <dir>` runs headless; launching with no arguments opens the Tkinter kit generator [GUI](GFF-File-Format#gui-graphical-user-interface) for interactive use. `uvx --refresh pykotor gui-convert --input <gui_or_folder> --output <dir> --resolution ALL` runs headless for [GUI](GFF-File-Format#gui-graphical-user-interface) resizing; omitting args opens the converter [GUI](GFF-File-Format#gui-graphical-user-interface). Developers: `uv run --directory Libraries/PyKotor/src --module pykotor` for local source. (Implementations: `kit_generator.py` wraps `Libraries/PyKotor/src/pykotor/tools/kit.py`; `Libraries/PyKotor/src/pykotor/cli/gui_converter.py` delegates to `pykotor.resource.formats.gff`.)
- **[HoloPatcher.NET](https://github.com/th3w1zard1/HoloPatcher.NET)** - .NET reimplementation of TSLPatcher
- **[Kotor-Patch-Manager](https://github.com/LaneDibello/Kotor-Patch-Manager)** - Alternative mod manager
- **[ModSync](https://github.com/th3w1zard1/KotORModSync)** - Mod synchronization and installation
- **[StarForge](https://github.com/th3w1zard1/StarForge)** - Module editor and modding toolkit
- **[KotorModTools](https://github.com/Box65535/KotorModTools)** - Collection of modding utilities

### Save Editors

Tools for editing KotOR save games:

- **[sotor](https://github.com/StarfishXeno/sotor)** - Terminal-based save editor
- **[KSELinux](https://github.com/Bolche/KSELinux)** - KotOR Save Editor for Linux
- **[KotOR-Save-Editor](https://github.com/Fair-Strides/KotOR-Save-Editor)** - [GUI](GFF-File-Format#gui-graphical-user-interface) save editor
- **[kotor-savegame-editor](https://github.com/nadrino/kotor-savegame-editor)** - Web-based save editor

### Audio Tools

Tools for working with KotOR audio:

- **[SithCodec](https://github.com/BBBrassil/SithCodec)** - KotOR audio codec implementation
- **[SWKotOR-Audio-Encoder](https://github.com/LoranRendel/SWKotOR-Audio-Encoder)** - Audio encoding tool for KotOR

### Community Resources

Guides, patches, and community-maintained resources:

- **[K1_Community_Patch](https://github.com/KOTORCommunityPatches/K1_Community_Patch)** - Community bug fix patch for KotOR 1
- **[TSL_Community_Patch](https://github.com/KOTORCommunityPatches/TSL_Community_Patch)** - Community bug fix patch for KotOR 2
- **[KOTOR-utils](https://github.com/JCarter426/KOTOR-utils)** - JCarter426's utility scripts and tools
- **[KotOR-Bioware-Libs](https://github.com/Fair-Strides/KotOR-Bioware-Libs)** - BioWare library references
- **[kotor_combat_faq](https://github.com/statsjedi/kotor_combat_faq)** - Combat mechanics documentation
- **[ds-kotor-modding-wiki](https://github.com/DeadlyStream/ds-kotor-modding-wiki)** - DeadlyStream modding wiki container

### Community sources and archives

For **complete, comprehensive, and accurate** wiki coverage, the following community sites and archives hold historical and ongoing KotOR/TSL modding knowledge. Use them to cross-check format behavior, tool usage, and engine quirks.

| Source | Description | Use for |
|--------|-------------|--------|
| **[DeadlyStream](https://deadlystream.com)** | Primary KotOR modding hub: mod releases, tutorials, Script Shack, tool discussions. | File format questions, TSLPatcher/HoloPatcher usage, nwscript.nss and animation references, override practices. |
| **[LucasForums Container](https://lucasforumscontainer.com)** | Archive of original LucasForums (StarWarsKnights.com) threads, reconstructed from the Wayback Machine. | TSLPatcher history and changelogs, Stoffe’s posts, format and tool discussions (2004–2007). |
| **[LucasForums Archive](https://lucasforumsarchive.com)** | Alternative archive project (Editing/Modding, Holowan Laboratories, tutorials). | TSLPatcher thread, KotOR tool docs, mod-finding threads. |
| **[PCGamingWiki — Star Wars: KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic)** / **[KotOR II](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords)** | Player-facing paths, widescreen/mod lists, common folders. | **Not** authoritative for binary semantics—cross-check [KEY-File-Format](KEY-File-Format), [Concepts](Concepts), and this wiki’s format pages. |
| **Holowan Laboratories / MixNMojo** | Historical KotOR modding forums (MixNMojo). | Early format and tool discussions; some content may be in archives or mirrors. |
| **Reddit** (e.g. r/kotor) | General KotOR community. | Mod installation, troubleshooting, links to DeadlyStream and wiki. |

**Further reading (community):**

- [DeadlyStream: Help setting up TSLPatcher](https://deadlystream.com/topic/5785-help-setting-up-the-tslpatcher-for-mods/) -- TSLPatcher setup
- [DeadlyStream: TSL Patcher, TLKEd, and accessories](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/) -- Modding tools
- [DeadlyStream: Modding tools category](https://deadlystream.com/files/category/17-modding-tools/) -- Tool releases
- [LucasForums Archive: TSLPatcher v1.2.10b1](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer/) -- Original TSLPatcher thread (see also [TSLPatcher Thread Complete](TSLPatcher_Thread_Complete) in this wiki)
- [LucasForums Archive: Editing / Modding](https://lucasforumsarchive.com/forum/521) -- Holowan Laboratories and tutorials

**How to use these sources:**

- **DeadlyStream:** Search the forums for specific topics (e.g. "override folder", "TSLPatcher 2DA merge", "GFF struct", "nwscript"). The Script Shack and modding tools sections contain tutorials and tool releases. When the wiki documents a format or tool, DeadlyStream threads often provide real-world modder reports (e.g. which 2DA columns are safe to add, TSLPatcher setup gotchas). Cite threads in "See also" or "Further reading" when they are the best source for a given detail.
- **LucasForums Container / LucasForums Archive:** Use for historical and authoritative context. The original TSLPatcher thread (Stoffe, etc.), KotOR Tool discussions, and early GFF/2DA explanations live in these archives. Search by keyword (e.g. "2da", "GFF", "TSLPatcher") in the Editing/Modding or Holowan Laboratories sections. Content may be fragmented across Wayback reconstructions; when a thread is cited, prefer stable archive URLs.
- **Holowan / Mixmojo:** Early KotOR modding community; some content is preserved in archives or linked from LucasForums. Use for very old format or tool history when other sources do not cover it.
- **Reddit (r/kotor):** Useful for installation help, troubleshooting, and links to DeadlyStream or this wiki. For format or engine-level accuracy, prefer this wiki and the format pages; for "how do I install X" or "why does my mod conflict with Y", community posts can complement the docs.

This wiki aims to consolidate and cite that knowledge where relevant. When adding or refining format or tool pages, prefer linking to authoritative specs (e.g. [KEY-File-Format](KEY-File-Format), [GFF-File-Format](GFF-File-Format), official BioWare Aurora docs) and to PyKotor ([OldRepublicDevs](https://github.com/OldRepublicDevs/PyKotor)) and other canonical implementation repos; for community consensus or historical context, link to DeadlyStream threads or LucasForums archive threads where appropriate.

### External Documentation

Reference documentation from related projects (external sources):

- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)** - Aurora engine format documentation repository containing file format specifications for reverse-engineering BioWare's Aurora engine games. Part of the [xoreos project](https://xoreos.org/). The repository includes:
  - **Official BioWare specifications** (`specs/bioware/`): Official Aurora Engine file format PDFs from the now-defunct nwn.bioware.com developer site. These documents are authoritative references for formats used across Aurora engine games including KotOR.
  - **Torlack's reverse-engineered specs** (`specs/torlack/`): Tim Smith (Torlack)'s reverse-engineered format documentation from his now-defunct website (torlock.com). These include detailed field-by-field breakdowns for formats like BIF, KEY, ERF (MOD), GFF (ITP), NCS, and binary MDL files.
  - **KotOR-specific documentation** (`specs/kotor_mdl.html`): Partial KotOR model format specifications with detailed field descriptions.
  - **Binary templates** (`templates/`): 010 Editor binary template files for analyzing binary file structures
  
  **Note:** Much of the *KotOR*-relevant content from xoreos-docs has been comprehensively integrated into this wiki. See individual format documentation pages for specific source references.
- **[nwn-docs](https://github.com/kucik/nwn-docs)** - Neverwinter Nights documentation (shares Aurora formats)
- **[bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats)** - Kaitai Struct format specifications for GFF, 2DA, BIF, ERF, TLK, and other BioWare/KotOR formats; useful for parser generation and cross-tool validation.

### See also

- [KEY-File-Format](KEY-File-Format) -- Resource resolution; [GFF-File-Format](GFF-File-Format), [2DA-File-Format](2DA-File-Format) -- Core formats
- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) -- Mod installation; [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) -- Mod development
- [Wiki-Conventions](Wiki-Conventions) -- Wiki structure and style
