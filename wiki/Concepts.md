# KotOR/TSL modding and engine concepts

The Odyssey engine resolves every resource request through a fixed priority chain: override folder, then module capsules (MOD/SAV/ERF/RIM), then KEY/BIF base archives. Understanding this chain — along with ResRefs, resource types, and the difference between template data and instance data — is essential for any modding work. Other wiki pages reference the definitions here rather than re-explaining the rules.

## Verified against implementations

These concepts are cross-checked against active code, not preserved here as folklore.

- **PyKotor:** `pykotor.extract.installation`, `pykotor.extract.chitin`, `pykotor.resource.formats.key.io_key`, `pykotor.resource.formats.bif.io_bif`, `pykotor.resource.formats.erf.io_erf`, `pykotor.resource.formats.rim.io_rim`, `pykotor.resource.formats.tlk.io_tlk`, `pykotor.resource.formats.twoda.io_twoda`
- **reone:** `src/libs/resource/director.cpp`, `src/libs/resource/resources.cpp`, `src/libs/resource/format/keyreader.cpp`, `src/libs/resource/format/bifreader.cpp`, `src/libs/resource/format/erfreader.cpp`
- **KotOR.js:** `src/loaders/ResourceLoader.ts`, `src/resource/KEYObject.ts`, `src/resource/BIFObject.ts`, `src/managers/TwoDAManager.ts`, `src/managers/TLKManager.ts`
- **Kotor.NET:** `Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs`, `Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs`, `Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs`, `Kotor.NET/Formats/Kotor2DA/TwoDABinaryReader.cs`, `Kotor.NET/ResourceContainers/Chitin.cs`

## Resource Resolution Order

When the game needs a resource, it resolves a pair: **ResRef + resource type**. The search order is stable enough that most compatibility problems reduce to one question: which source is being searched first?

In normal play, the effective order is:

1. **Override folder** (`override/` in the game directory)
2. **Currently loaded MOD/ERF/[RIM](Container-Formats#rim) module archives** (e.g. the module being played)
3. **Currently loaded save game** (when in-game; situational — often exposed as a loaded SAV / save-side container)
4. **BIF files** indexed by **KEY** (vanilla game data)
5. **Hardcoded defaults** (if the engine provides them)

Anything in `override/` or in the active module capsule wins before the game falls back to vanilla KEY/BIF data. That is why “just copy a file into override” works for quick tests, but also why it causes collisions when multiple mods ship the same ResRef and type.

### How the *resource manager* resolves a request

The engine first checks whether the resource is already loaded or cached. If not, it routes the request to the correct backend for that storage shape: directory, active module capsule, save-side data, or the KEY/BIF stack. The [KEY](Container-Formats#key) only participates in that fourth step. It does not control override precedence, and it does not need to be edited for a mod to shadow a vanilla file.

### Role of the [**KEY**](Container-Formats#key) file

The [**KEY**](Container-Formats#key) file (normally `chitin.key`) is the master index for vanilla archive data. It maps a ResRef and resource type to a specific BIF archive and an entry inside that archive. It does not define the whole resolution order; it only enables the vanilla-data fallback stage.

That distinction matters for authors. If your mod ships a file in `override/`, or a resource in a module `.mod`, the engine can find it before ever consulting `chitin.key`.

## ResRef (Resource Reference)

A **ResRef** is the resource’s name: a short string (up to ***16 characters*** in *KotOR*). Together with a **Resource Type** (numeric ID; see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers) and [GFF-File-Format](GFF-File-Format#gff-data-types)), the engine uses the *ResRef* to look up the resource via the [resource resolution order](#resource-resolution-order) above.

## Override Folder

The **override** folder is the bluntest and most powerful mod-install location in the game. Loose files placed there are resolved before the vanilla KEY/BIF stack and before most stock content for the active module.

That makes override useful for rapid testing and for global replacements, but it also makes it the easiest place to create mod conflicts. Only one file for a given ResRef and resource type can win. For mergeable content such as [2DA](2DA-File-Format), [TLK](Audio-and-Localization-Formats#tlk), and many [GFF](GFF-File-Format) resources, patcher-based merging is usually safer than shipping a monolithic loose-file replacement.

**Community context:** Players often compare loadouts in threads such as [Deadly Stream — What's in your Override folder?](https://deadlystream.com/topic/7279-whats-in-your-override-folder/) (mod combinations in practice). **Historical (pre-HoloPatcher era):** [LucasForums Archive — Load order?](https://www.lucasforumsarchive.com/thread/206128-load-order) and [Guide for the newbie: tools and how to install mods](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods) (dated workflows; prefer current [Installing-Mods-with-HoloPatcher](HoloPatcher#installing-mods) and this page for **resolution order**). **Resolution order and conflicts** here and [KEY-File-Format](Container-Formats#key) remain SSOT.

**Player-facing install paths (not SSOT for resolution):** For Steam/GOG/Aspyr folder layouts, widescreen, and common OS fixes, [PCGamingWiki — KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic) and [KotOR II: The Sith Lords](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords) complement [Installing-Mods-with-HoloPatcher](HoloPatcher#installing-mods); do **not** treat PCGW as authoritative for KEY/BIF semantics or override precedence—those stay on this page and [KEY-File-Format](Container-Formats#key).

## [**BIF**](Container-Formats#bif) and [**KEY**](Container-Formats#key)

[**BIF**](Container-Formats#bif) files store most of the shipped game data. [**KEY**](Container-Formats#key) tells the game which BIF contains a given ResRef and type, and which entry inside that BIF to read.

From a modder’s point of view, the important rule is simple: BIF and KEY are the baseline, not the preferred mod target. Most mods leave them untouched and win by providing a higher-priority file in override or a module capsule.

## [**MOD**](Container-Formats#erf) / [**ERF**](Container-Formats#erf) / [**RIM**](Container-Formats#rim)

[**ERF**](Container-Formats#erf) is a general-purpose container format. [**MOD**](Container-Formats#erf) files are ERFs used as module capsules; [**SAV**](Container-Formats#erf) files are ERF-style save containers. [**RIM**](Container-Formats#rim) is the stock module archive format used by the shipped game data.

The practical rule is that module-scoped content belongs here, not in global override, when you want the resource to apply only to a specific area or module. In many common setups, a module `.mod` in `modules/` overrides the matching stock `.rim` pair for that module name.

### Module packaging for mod authors (override vs `modules/`)

| Delivery | Typical use | Notes |
| -------- | ----------- | ----- |
| **`override/`** | Global scripts, textures, 2DAs, TLK, GFF templates used in many modules | Highest precedence vs BIF; last writer wins if two mods use the same ResRef+type—prefer [2DAList](TSLPatcher-Data-Syntax#2dalist-syntax) / [TLKList](TSLPatcher-Data-Syntax#tlklist-syntax) merges |
| **`Modules/*.mod`** | Module-scoped capsule (ERF-type [MOD](Container-Formats#erf)) | Often overrides the vanilla `.rim` pair for that module name when present |
| **Vanilla `.rim` / `_s.rim`** | Stock module archives ([RIM](Container-Formats#rim)) | Mods usually ship a `.mod` instead of editing RIMs in place |

Choose scope first, then choose the packaging target. If the resource should affect many modules, ship it to `override/` or merge it through patch lists. If the resource belongs to one module, build or patch a `.mod` so the files stay capsule-scoped instead of leaking into the global override.

For distribution work, the usual failure modes are scope mistakes rather than format mistakes: shipping a module-only resource to `override/`, or reinstalling patcher options until duplicate 2DA rows accumulate. Use [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) for player-facing restore and troubleshooting guidance, and use the [resource resolution order](#resource-resolution-order) on this page to decide where the resource belongs.

## [**GFF** (Generic File Format)](GFF-File-Format)

[**GFF**](GFF-File-Format) is BioWare’s binary format for structured game data: areas (ARE), creatures (UTC), items (UTI), dialogues (DLG), placeables (UTP), and many others. Files are hierarchical (structs, fields, lists). The same GFF layout is used across Aurora/Odyssey games; KotOR and TSL use specific GFF types and field meanings. Modders edit GFF with tools (KotOR Tool, Holocron Toolset, K-GFF) or via [TSLPatcher/HoloPatcher `[GFFList]` implementation](TSLPatcher-GFFList-Syntax). See [GFF-File-Format](GFF-File-Format), [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff).

## [**2DA** (Two-Dimensional Array)](2DA-File-Format)

[**2DA**](2DA-File-Format) files are tabular data: rows and columns used for items, [spells](2DA-File-Format#spells2da), [appearances](2DA-File-Format#appearance2da), and most game configuration. The engine and [GFF](GFF-File-Format) resources reference [*2DA*](2DA-File-Format) rows by index or label. Mods often add or edit rows (e.g. new appearance row, new spell); when multiple mods change the same [*2DA*](2DA-File-Format), merging (e.g. via [*TSLPatcher*'s](TSLPatcher's-Official-Readme) `[2DAList]` implementation) avoids overwriting. See [2DA-File-Format](2DA-File-Format), [TSLPatcher-2DAList-Syntax](TSLPatcher-Data-Syntax#2dalist-syntax).

**Historical forum example:** Veterans debated `spells.2da` edits vs multi-mod compatibility in [LucasForums Archive — spells.2da, compatibility and TSL Patcher](https://www.lucasforumsarchive.com/thread/205823-spells2da-compatibility-and-tsl-patcher) (2010); the takeaway for authors is still **merge-aware installers** and row-level patches, not dropping a monolithic override—see [2DA-spells](2DA-File-Format#spells2da) **Community context**.

**Campaign globals (scripting):** NWScript `GetGlobal*` / `SetGlobal*` identifiers are declared in [globalcat.2da](2DA-File-Format#globalcat2da). Value limits and usage patterns are summarized on [NSS — Global Variables](NSS-File-Format#global-variables). Treat forum threads on “quest globals” as **workflow hints**—verify names exist in `globalcat.2da` or your installer’s expectations.

## Resource Type Identifiers

The canonical **hex resource type ID** table (*Aurora* / *Odyssey* family, including rows unused in *KotOR*) lives on **[Resource formats and resolution — Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)**. That page is the wiki SSOT for the numeric IDs and their four-character labels.

## Language IDs (*KotOR*)

Language IDs are a small integer enum shared across *Infinity*/*Aurora*/*Odyssey*/*Eclipse*-era engines (TLK headers, [ERF](Container-Formats#erf) localized string lists, [GFF](GFF-File-Format) `LocalizedString` substrings, etc.). Newer *BioWare* titles added values but usually stay backward compatible with 0–5.

Use this table as the **wiki SSOT** for numeric IDs and typical text encodings. Official *BioWare* PDFs duplicate the same numbering in places like [Bioware-Aurora-TalkTable](Bioware-Aurora-Core-Formats#talktable) and [Bioware-Aurora-LocalizedStrings](Bioware-Aurora-Core-Formats#localizedstrings).

| Language | ID | Typical encoding | Description |
| -------- | -- | ---------------- | ----- |
| English  | 0  | Windows-1252     | Default for Western `dialog.tlk` and many legacy Aurora payloads |
| French   | 1  | Windows-1252     | |
| German   | 2  | Windows-1252     | |
| Italian  | 3  | Windows-1252     | |
| Spanish  | 4  | Windows-1252     | |
| Polish   | 5  | Windows-1250     | *KotOR 1 Polish* retail (**`cp-1250`**); see also **`dialogf.tlk`** in [TSLPatcher `[TLKList]` implementation](TSLPatcher-TLKList-Syntax) |
| Korean   | 6  | UTF-8            | Aurora TLK / tooling enum value; **not** used in shipped *KotOR 1/2* retail `dialog.tlk` sets |
| Chinese  | 7  | UTF-8            | Same as Korean row |
| Japanese | 8  | UTF-8            | Same as Korean row |

**Where the ID appears:** [TLK-File-Format](Audio-and-Localization-Formats#tlk) file header and tooling; [ERF-File-Format](Container-Formats#erf) localized description list per language; [GFF-File-Format](GFF-File-Format) `LocalizedString` embedded strings. KotOR often ignores the TLK header language field and loads the `dialog.tlk` that matches the installation—see [TLK-File-Format](Audio-and-Localization-Formats#localization).

**Reference**:

- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**
- [`specs/torlack/basics.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html) — Torlack’s Aurora basics (NWN-focused; IDs apply to *KotOR*).

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution) -- Format index, resolution order, hex resource type table
- [Home — community sources and archives](Home#community-sources-and-archives) -- Deadly Stream, LucasForums Archive, PCGamingWiki (player paths and forum context)
- [Home](Home) -- Wiki hub (formats, tools, tutorials)
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) -- Reader-facing install and troubleshooting workflow
- [KEY-File-Format](Container-Formats#key) -- KEY file format (e.g. `chitin.key`)
- [GFF-File-Format](GFF-File-Format) -- GFF file format (e.g. `area.gff`)
- [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices) -- Best practices for modding
- [TLK-File-Format](Audio-and-Localization-Formats#tlk) -- TLK file format (e.g. `dialog.tlk`)
- [2DA-File-Format](2DA-File-Format) -- 2DA structure and table reference
