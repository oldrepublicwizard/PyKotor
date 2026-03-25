# KotOR ERF file format Documentation

This document provides a detailed description of the ERF (Encapsulated Resource file) file format used in Knights of the Old Republic (KotOR) games. ERF files are self-contained containers used for modules, save games, [texture](TPC-File-Format) packs, and hak paks. Shipped modules also use **[RIM](RIM-File-Format)** (resource image) archives; RIM is a **different** binary layout—see [RIM versus ERF](#rim-versus-erf) and the dedicated [RIM File Format](RIM-File-Format) page.

## Table of Contents

- KotOR ERF file format Documentation
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
  - [RIM versus ERF](#rim-versus-erf)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Localized String List](#localized-string-list)
    - [KEY List](#key-list)
    - [Resource List](#resource-list)
    - [Resource Data](#resource-data)
    - [MOD/NWM File Format Quirk: Blank Data Block](#modnwm-file-format-quirk-blank-data-block)
  - [ERF Variants](#erf-variants)
    - [MOD Files (module containers)](#mod-files-module-containers)
    - [SAV Files (save game containers)](#sav-files-save-game-containers)
    - [HAK Files (Override Paks)](#hak-files-override-paks)
    - [RIM files (resource image)](#rim-files-resource-image)
    - [ERF Files (Generic Containers)](#erf-files-generic-containers)
  - [Implementation Details](#implementation-details)

---

## File Structure Overview

*ERF* files are self-contained containers that store both resource names ([ResRefs](GFF-File-Format#gff-data-types)) and data in the same file. Unlike [BIF files](BIF-File-Format) which require a [KEY file](KEY-File-Format) for filename lookups, *ERF* files include *ResRef* information directly in the container. When the engine resolves a resource request, it can service from encapsulated containers (*MOD/ERF* and stock [RIM](RIM-File-Format) module archives) before falling back to *KEY/BIF*; see [resource resolution order](Concepts#resource-resolution-order).

**For mod developers:** *MOD* and *HAK* files are built with Holocron Toolset or other packers; see [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) and [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers). Vanilla modules ship as `.rim` / `_s.rim` ([RIM](RIM-File-Format)); a `.mod` in `modules/` overrides the same module’s RIM set when present.

**Related formats:** *ERF* containers hold [GFF](GFF-File-Format), [2DA](2DA-File-Format), [TPC](TPC-File-Format), [NCS](NCS-File-Format), and other resource types; see [KEY](KEY-File-Format) and [BIF](BIF-File-Format) for alternative storage. **Modder note:** Use *MOD*s for module-specific content (area GFFs, module 2DAs); use [override](Concepts#override-folder) for global replacements. See [Concepts](Concepts#mod-erf-rim) and [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files).

**Implementation (PyKotor):** [`Libraries/PyKotor/src/pykotor/resource/formats/erf/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/) — layout table in [`erf_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L54) docstring; read path [`ERFBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L51-L169); write path [`ERFBinaryWriter.write`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L186-L256).

**Cross-reference (other implementations):**

More engines and tools: [Home — Cross-reference: other tools and engines](Home#cross-reference-other-tools-and-engines).

- **[reone](https://github.com/modawan/reone)** (community continuation; historical upstream [seedhartha/reone](https://github.com/seedhartha/reone)): [`src/libs/resource/format/erfreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp) — `ErfReader::load` ([L29–L40](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L29-L40)), signature check ([L42–L52](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L42-L52); accepts only `ERF V1.0` and `MOD V1.0` as one 8-byte string), key entries ([L62–L71](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L62-L71)), resource entries ([L84–L92](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L84-L92)); header [`erfreader.h`](https://github.com/modawan/reone/blob/master/include/reone/resource/format/erfreader.h). This reader **does not** parse the localized-string block; **SAV** files that still use the `MOD` + `V1.0` header may match the MOD branch, but **`HAK`** / **`SAV`** fourcc paths are not handled here.
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/resource/ERFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts) — [`parseHeader` L69–L85](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L69-L85), [`parseStructures` L87–L119](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L87-L119) (localized strings, keys, resource list), [`getExportBuffer` L280–L346](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L280-L346) (serialize).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs) — `FileRoot` load path ([L25–L46](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L25-L46)); `FileHeader` reader ([L86–L97](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L86-L97)) skips **Description StrRef** and the **116-byte** reserved tail (see PyKotor for the full 160-byte header); `KeyEntry` reader ([L128–L134](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L128-L134)); `ResourceEntry` reader ([L157–L161](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L157-L161)).
- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/aurora/erffile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/erffile.cpp) — Aurora-wide ERF/MOD reader (multiple games).
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`src/aurora/erffile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/erffile.cpp) — CLI extraction / tooling.
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)**: [`Assets/Scripts/FileObjects/ERFObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/ERFObject.cs) — Unity-side loader.
- **[bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats)** — Kaitai Struct specs (ERF and related BioWare formats).

---

## RIM versus ERF

[RIM](RIM-File-Format) (**resource image**) files are the **stock** module archives under `modules/`. They are **encapsulated** containers like ERF/MOD (ResRef + type + bytes in one file) but **not** the same on-disk structure as this document’s 160-byte **ERF** header. Tools that only parse ERF must convert or use a RIM-aware reader.

| Feature | RIM ([RIM File Format](RIM-File-Format)) | ERF / MOD / SAV / HAK (this page) |
| ------- | ---------------------------------------- | ---------------------------------- |
| Signature | `RIM` + `V1.0` | `ERF` / `MOD` / `SAV` / `HAK` + `V1.0` |
| Header size | **120** bytes | **160** bytes |
| Localized strings, build date, description StrRef | Absent | Present (strings optional) |
| Index layout | One **32-byte** record per resource (includes **UInt32** type, offset, size) | **24-byte** [KEY](KEY-File-Format)-style list + separate **8-byte** offset/size list |
| MOD-only gap | N/A | Optional **8-byte × entry_count** zero block between key list and resource list ([quirk](#modnwm-file-format-quirk-blank-data-block)) |

**Engine and tooling:** Both families are loaded as module-side capsules ahead of [KEY](KEY-File-Format)/[BIF](BIF-File-Format) for resources they contain; see [resource resolution order](Concepts#resource-resolution-order). PyKotor can turn a loaded RIM into an in-memory ERF via `RIM.to_erf()` for writing MOD/ERF output.

**Normative RIM layout:** Field sizes, implicit offset `0` → table at byte 120, and padding behavior are specified on [RIM File Format](RIM-File-Format).

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

Everything in this section applies to **ERF**, **MOD**, **SAV**, and **HAK** signatures only. **[RIM](RIM-File-Format)** uses a shorter header and a different index record layout; do not treat these tables as the RIM specification.

### File Header

The file header is 160 bytes in size:

| Name                      | type    | offset | size | Description                                    |
| ------------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type                 | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | `"ERF "`, `"MOD "`, `"SAV "`, or `"HAK "`     |
| file Version              | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | Always `"V1.0"`                                 |
| Language count            | UInt32  | 8 (0x08) | 4    | Number of localized string entries             |
| Localized string size     | UInt32  | 12 (0x0C) | 4    | Total size of localized string data in bytes   |
| Entry count               | UInt32  | 16 (0x10) | 4    | Number of resources in the container              |
| offset to Localized string List | UInt32 | 20 (0x14) | 4 | offset to localized string entries             |
| offset to [KEY](KEY-File-Format) List        | UInt32  | 24 (0x18) | 4    | offset to [KEY](KEY-File-Format) entries array                    |
| offset to Resource List   | UInt32  | 28 (0x1C) | 4    | offset to resource entries array                |
| Build Year                | UInt32  | 32 (0x20) | 4    | Build year (years since 1900)                   |
| Build Day                 | UInt32  | 36 (0x24) | 4    | Build day (days since Jan 1)                   |
| Description [StrRef](TLK-File-Format#string-references-strref)        | UInt32  | 40 (0x28) | 4    | [TLK](TLK-File-Format) string reference for description           |
| Reserved                  | [byte](https://en.wikipedia.org/wiki/Byte) | 44 (0x2C)  | 116  | Padding (usually zeros)                         |

**Build Date Fields:**

The Build Year and Build Day fields timestamp when the ERF file was created:

- **Build Year**: Years since 1900 (e.g., `103` = year 2003)
- **Build Day**: Day of year (1-365/366, with January 1 = day 1)

These timestamps are primarily informational and used by development tools to track module versions. The game engine doesn't rely on them for functionality.

**Example Calculation:**

```plaintext
Build Year: 103 --> 1900 + 103 = 2003
Build Day: 247 --> September 4th (the 247th day of 2003)
```

Most mod tools either zero out these fields or set them to the current date when creating/modifying ERF files.

**Description [StrRef](TLK-File-Format#string-references-strref) values by file type:**

The Description [StrRef](TLK-File-Format#string-references-strref) field (offset 0x0028 / 0x28) varies depending on the ERF variant:

- **MOD files**: `0xFFFFFFFF` (-1) is the standard for BioWare modules.
  - *Exception*: TSL LIPS files consistently use `0xCDCDCDCD` (Debug Fill).
  - *Exception*: Some KOTOR 1 modules (e.g. `unk_m41` series) use `0`.
- **SAV files**: `0` (typically no description)
- **NWM files**: `-1` (**Neverwinter Nights module format, NOT used in KotOR**)
- **ERF/HAK files**: Unpredictable (may contain valid [StrRef](TLK-File-Format#string-references-strref) or `-1`)

**Technical Note**: The engine determines if a file is a Save Game based on context (loading from `saves/` vs `modules/` and presence of `SAVES:` resource alias), **NOT** by any flag or value in the ERF header.

**References**

**Cross-reference:**

- PyKotor — full 160-byte header read: [`io_erf.py` L70–L96](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L70-L96); layout table: [`erf_data.py` L19–L36](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L36).
- KotOR.js — [`ERFObject.parseHeader` L69–L85](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L69-L85).
- Kotor.NET — [`FileHeader` reader L86–L97](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L86-L97) (partial; omits description StrRef + reserved).
- Torlack (historical RE) — [xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html) (canonical repo).

### Localized String List

Localized strings provide descriptions in multiple languages:

| Name         | type    | size | Description                                                      |
| ------------ | ------- | ---- | ---------------------------------------------------------------- |
| Language ID  | UInt32  | 4    | Language identifier ([Concepts](Concepts#language-ids-kotor))                          |
| string size  | UInt32  | 4    | Length of string in bytes                                       |
| string data  | [char](GFF-File-Format#gff-data-types)[]  | N    | `windows-1252` encoded text                     |

**Localized string Usage:**

ERF localized strings provide multi-language descriptions for the container itself. These are primarily used in MOD files to display module names and descriptions in the game's module selection screen.

**Language IDs:** Use the shared Aurora numeric enum and encodings on [Concepts](Concepts#language-ids-kotor) (same values as TLK and GFF localized strings).

**Important Notes:**

- Most ERF files have zero localized strings (Language count = 0)
- MOD files may include localized module names for the load screen
- **Engine Behavior**: The game engine's resource loader (`CExoKeyTable::AddEncapsulatedContents`) **ignores** these fields. They are likely used only by the specific UI components (like the Module Selection screen).
- **Encoding**: Strings should be encoded as `windows-1252` (CP1252) to support legacy BioWare character sets.
- The Description [StrRef](TLK-File-Format#string-references-strref) field (in header) provides an alternative via [TLK](TLK-File-Format) reference

**References**

**Cross-reference:**

- PyKotor — localized block: [`io_erf.py` L122–L143](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L122-L143); writer: [`io_erf.py` L235–L240](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L235-L240).
- KotOR.js — [`parseStructures` L91–L97](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L91-L97).
- reone — `ErfReader` does **not** read localized strings (see [cross-reference at top](#file-structure-overview)); use PyKotor or KotOR.js for that path.

### [KEY](KEY-File-Format) List

Each [KEY](KEY-File-Format) entry is 24 bytes and maps ResRefs to resource indices:

| Name        | type     | offset | size | Description                                                      |
| ----------- | -------- | ------ | ---- | ---------------------------------------------------------------- |
| *ResRef*      | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 16   | Resource filename (null-padded, max 16 chars)                    |
| Resource ID | UInt32   | 16 (0x10) | 4    | index into resource list                                         |
| Resource type | [uint16](GFF-File-Format#gff-data-types) | 20 (0x14) | 2    | Resource type ID ([table](Resource-Formats-and-Resolution#resource-type-identifiers))                                         |
| Unused      | [uint16](GFF-File-Format#gff-data-types)   | 22 (0x16) | 2    | Padding                                                           |

***ResRef* Padding Notes:**

Resource names are padded with NULL bytes to 16 characters, but are not necessarily [null-terminated](https://en.cppreference.com/w/c/string/byte). If a resource name is exactly 16 characters long, no [null terminator](https://en.cppreference.com/w/c/string/byte) exists. Resource names can be mixed case, though most are lowercase in practice.

**References**

**Cross-reference:**

- PyKotor — key list: [`io_erf.py` L148–L155](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L148-L155); writer: [`io_erf.py` L242–L246](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L242-L246) (PyKotor preserves ResRef case; reone lowercases in [`readKeyEntry` L63](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L63)).
- KotOR.js — key loop [`parseStructures` L101–L108](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L101-L108).
- Kotor.NET — [`KeyEntry` reader L128–L134](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L128-L134).
- reone — [`readKeyEntry` L62–L71](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L62-L71).
- Torlack — [xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html) (*ResRef* padding notes).

### Resource List

Each resource entry is 8 bytes:

| Name          | type   | offset | size | Description                                                      |
| ------------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| offset to data | UInt32 | 0 (0x00) | 4    | offset to resource data in file                                  |
| Resource size | UInt32 | 4 (0x04) | 4    | size of resource data in bytes                                   |

**References**

**Cross-reference:**

- PyKotor — resource list: [`io_erf.py` L159–L162](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L159-L162); writer: [`io_erf.py` L248–L252](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L248-L252).
- KotOR.js — [`parseStructures` L112–L116](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/ERFObject.ts#L112-L116).
- Kotor.NET — [`ResourceEntry` reader L157–L161](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L157-L161).
- reone — [`readResourceEntry` L84–L92](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L84-L92).

### Resource data

Resource data is stored at the offsets specified in the resource list:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Resource data | [byte](https://en.wikipedia.org/wiki/Byte)[] | Raw binary data for each resource                               |

### MOD/NWM file format Quirk: Blank data Block

**Note**: For MOD and NWM files only, there exists an unusual block of data between the resource structures ([KEY](KEY-File-Format) List) and the position structures (Resource List). This block is 8 bytes per resource and appears to be all NULL bytes in practice. This data block is not referenced by any offset in the ERF file header, which is uncharacteristic of BioWare's file format design.

**References**

**Cross-reference:**

- Torlack — [xoreos-docs `specs/torlack/mod.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/mod.html) (“Strange Blank data”).

---

## ERF Variants

ERF files come in several variants based on file type:

| file type | Extension | Description                                                      |
| --------- | --------- | ---------------------------------------------------------------- |
| ERF       | `.erf`    | Generic encapsulated resource file                               |
| MOD       | `.mod`    | Module file (contains area resources)                            |
| SAV       | `.sav`    | Save game file (contains saved game state)                       |

The **on-disk** 160-byte layout is the same family for shipped KotOR capsules; the **first four bytes** are not always a distinct `SAV` type code—PyKotor treats many `.sav` files as the `MOD` / `V1.0` header pair for typing purposes ([`ERFType.from_extension`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L128-L135)). `ERF` and `HAK` (and `SAV` when present) are still valid Aurora signatures when they appear.

### MOD Files (module containers)

MOD files package all resources needed for a game module (level/area):

**Typical Contents:**

- Area layouts (`.are`, `.git`)
- Module information (`.ifo`)
- Dialogs and scripts (`.dlg`, `.ncs`)
- Module-specific [2DA](2DA-File-Format) overrides
- Character templates (`.utc`, `.utp`, `.utd`)
- Waypoints and triggers (`.utw`, `.utt`)

The game loads MOD files from the `modules/` directory. When entering a module, the engine mounts the MOD container and prioritizes its resources over [BIF files](BIF-File-Format) but below the `override/` folder.

### SAV Files (save game containers)

SAV files store complete game state:

**Contents:**

- Party member data (inventory, stats, equipped items)
- Module state (spawned creatures, opened containers)
- Global variables and plot flags
- Area layouts with modifications
- Quick bar configurations
- Portrait images

Save files preserve the state of all modified resources. When a placeable is looted or a door opened, the updated `.git` resource is stored in the SAV file.

### HAK Files (Override Paks)

`HAK` uses the same ERF binary layout as other variants; the file type signature is `"HAK "`. Historically used in Neverwinter Nights for hak paks; KotOR lists the type in the resource table but does not use HAK the same way as NWN. Treat as a generic ERF container when encountered.

### RIM files (resource image)

`.rim` files are **not** ERF binaries: they use a **120-byte** header and **32-byte** resource records (see [RIM File Format](RIM-File-Format) and [RIM versus ERF](#rim-versus-erf)). They are the usual shipped module capsules under `modules/`; [MOD](ERF-File-Format#mod-files-module-containers) overrides the same module when both exist.

### ERF Files (Generic Containers)

Generic ERF files serve miscellaneous purposes:

- [texture](TPC-File-Format) packs
- Audio replacement packs
- Campaign-specific resources
- Developer test containers

**References**

**Cross-reference:**

- reone — [`ErfReader::checkSignature` L42–L52](https://github.com/modawan/reone/blob/master/src/libs/resource/format/erfreader.cpp#L42-L52) (accepts `ERF V1.0` and `MOD V1.0` only, as a single 8-byte read after opening the stream).

---

## Engine Internal Behavior

Reverse engineering of the game engine (specifically `CExoKeyTable::AddEncapsulatedContents` at `0x0040f3c0` in `swkotor.exe`) reveals how the engine actually parses these files.

### Critical vs. Metadata Fields

The engine's resource manager is surprisingly strict, reading the 160-byte header but **ignoring** most fields. It only validates/uses:

- **file type** and **Version** (Verified against expected values)
- **Entry Count** (Used to allocate memory for the key table)
- **offset to [KEY](KEY-File-Format) List** (Used to seek to the key data)

The following fields are **parsed but ignored** by the resource manager (though they may be used by the UI/Menus):

- `Language count` and `Localized string size`
- `offset to Localized string List`
- `Build Year` and `Build Day`
- `Description [StrRef](TLK-File-Format#string-references-strref)`

### Save Game Detection

Contrary to popular belief, the engine does **not** identify Save Games based on the file type signature (`SAV` vs `ERF`) or the `Description StrRef` being `0`.

- **Mechanism**: The engine distinguishes save games based on **file context** (loading from the `saves/` directory) and the resource system usage (aliasing `SAVES:` path).
- **Implication**: Setting `Description StrRef` to `0` in a `MOD` file does *not* make it a save file. Legitimate modules (e.g., `unk_m41` series) use `0` as their StrRef.

### TSL Specific Quirks

- **LIPS MODs**: In *Knights of the Old Republic II: The Sith Lords*, MOD files related to lip-syncing (`lips_*.mod`) consistently use `0xCDCDCDCD` for the `Description StrRef`. This value (`-842150451`) is a common "uninitialized memory" fill pattern in Microsoft C++ debug runtimes, suggesting these files were built with a debug version of the toolset.

---

## Implementation Details

| Component | PyKotor (line anchors) |
| --------- | ------------------------ |
| Layout / types | [`erf_data.py` L19–L54](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L19-L54) (docstring), [`ERFType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L107-L137), [`ERF` archive](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L140-L253) |
| Binary read | [`ERFBinaryReader.load` L51–L169](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L51-L169) |
| Binary write | [`ERFBinaryWriter.write` L186–L256](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py#L186-L256) |

See also **Cross-reference** at the [top of this page](#file-structure-overview) for KotOR.js, Kotor.NET, reone, and xoreos.

### See also

- [Concepts](Concepts#language-ids-kotor) - Language ID enum and encodings (ERF localized strings, TLK, GFF)
- [BIF File Format](BIF-File-Format) - Container format used with [KEY](KEY-File-Format) files
- [KEY File Format](KEY-File-Format) - Index for [BIF containers](BIF-File-Format) and resource resolution
- [GFF File Format](GFF-File-Format) - Common content type stored in ERF containers
- [RIM File Format](RIM-File-Format) — Resource image containers (distinct binary layout; [comparison](ERF-File-Format#rim-versus-erf))

---

This documentation aims to provide a comprehensive overview of the KotOR ERF file format, focusing on the detailed file structure and data formats used within the games.
