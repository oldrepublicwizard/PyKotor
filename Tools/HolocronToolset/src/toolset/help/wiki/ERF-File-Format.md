# KotOR ERF file format Documentation

This document provides a detailed description of the ERF (Encapsulated Resource file) file format used in Knights of the Old Republic (KotOR) games. ERF files are self-contained containers used for modules, save games, [texture](TPC-File-Format) packs, and hak paks.

## Table of Contents

- KotOR ERF file format Documentation
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
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
    - [ERF Files (Generic Containers)](#erf-files-generic-containers)
  - [Implementation Details](#implementation-details)

---

## File Structure Overview

ERF files are self-contained containers that store both resource names ([ResRefs](GFF-File-Format#gff-data-types)) and data in the same file. Unlike [BIF files](BIF-File-Format) which require a [KEY file](KEY-File-Format) for filename lookups, ERF files include *ResRef* information directly in the container.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/erf/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/)

**Vendor References:**

- [`vendor/reone/src/libs/resource/format/erfreader.cpp`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/erfreader.cpp) - Complete C++ ERF reader implementation with MOD/SAV/HAK support
- [`vendor/reone/include/reone/resource/format/erfreader.h`](https://github.com/th3w1zard1/reone/blob/master/include/reone/resource/format/erfreader.h) - ERF reader type definitions
- [`vendor/xoreos/src/aurora/erffile.cpp`](https://github.com/th3w1zard1/xoreos/blob/master/src/aurora/erffile.cpp) - Generic Aurora ERF implementation (shared format across KotOR, NWN, and other Aurora games)
- [`vendor/KotOR.js/src/resource/ERFObject.ts`](https://github.com/th3w1zard1/KotOR.js/blob/master/src/resource/ERFObject.ts) - TypeScript ERF parser with streaming support
- [`vendor/KotOR-Unity/Assets/Scripts/FileObjects/ERFObject.cs`](https://github.com/th3w1zard1/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/ERFObject.cs) - C# Unity ERF loader
- [`vendor/Kotor.NET/Kotor.NET/Formats/KotorERF/`](https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Formats/KotorERF) - .NET ERF reader/writer with builder API
- [`vendor/xoreos-tools/src/aurora/erffile.cpp`](https://github.com/th3w1zard1/xoreos-tools/blob/master/src/aurora/erffile.cpp) - Command-line ERF extraction tools

**See Also:**

- [BIF File Format](BIF-File-Format) - Alternative container format used with KEY files
- [KEY File Format](KEY-File-Format) - index file for [BIF containers](BIF-File-Format)
- [GFF File Format](GFF-File-Format) - Common content type stored in ERF containers
- [RIM File Format](RIM-File-Format) - Resource Index Manifest file format

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

### File Header

The *file header* is 160 bytes in size:

| Name                      | type    | offset | size | Description                                    |
| ------------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| **File Type**                 | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | `"ERF "`, `"MOD "`, `"SAV "`, or `"HAK "`     |
| **File Version**              | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | Always `"V1.0"`                                 |
| **Language count**            | *UInt32*  | 8 (0x08) | 4    | Number of localized string entries             |
| **Localized string size**     | *UInt32*  | 12 (0x0C) | 4    | Total size of localized string data in bytes   |
| **Entry count**               | *UInt32*  | 16 (0x10) | 4    | Number of resources in the container              |
| **offset to Localized string List** | *UInt32* | 20 (0x14) | 4 | offset to localized string entries             |
| **offset to KEY List**        | *UInt32*  | 24 (0x18) | 4    | offset to KEY entries array                    |
| **offset to Resource List**   | *UInt32*  | 28 (0x1C) | 4    | offset to resource entries array                |
| **Build Year**                | *UInt32*  | 32 (0x20) | 4    | Build year (years since 1900)                   |
| **Build Day**                 | *UInt32*  | 36 (0x24) | 4    | Build day (days since Jan 1)                   |
| **Description [StrRef](TLK-File-Format#string-references-strref)**        | *UInt32*  | 40 (0x28) | 4    | [TLK](TLK-File-Format) string reference for description           |
| **Reserved**                  | *[byte](https://en.wikipedia.org/wiki/Byte)* | 44 (0x2C)  | 116  | Padding (usually zeros)                         |

**Build Date Fields:**

The **Build Year** and **Build Day** fields timestamp when the ERF file was created:

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

The **Description [StrRef](TLK-File-Format#string-references-strref)** field (offset 0x0028 / 0x28) varies depending on the ERF variant:

- **MOD files**: `0xFFFFFFFF` (-1) is the standard for BioWare modules.
  - *Exception*: TSL LIPS files consistently use `0xCDCDCDCD` (Debug Fill).
  - *Exception*: Some KOTOR 1 modules (e.g. `unk_m41` series) use `0`.
- **SAV files**: `0` (typically no description)
- **NWM files**: `-1` (**Neverwinter Nights module format, NOT used in KotOR**)
- **ERF/HAK files**: Unpredictable (may contain valid [StrRef](TLK-File-Format#string-references-strref) or `-1`)

**Technical Note**: The engine determines if a file is a Save Game based on context (loading from `saves/` vs `modules/` and presence of `SAVES:` resource alias), **NOT** by any flag or value in the ERF header.

**Reference**: [`vendor/Kotor.NET/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs:11-46`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L11-L46)  
**Reference**: [`vendor/xoreos-docs/specs/torlack/mod.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/mod.html) - Tim Smith (Torlack)'s reverse-engineered ERF format documentation

### Localized String List

The *Localized string list* provides descriptions in multiple languages:

| Name         | type    | size | Description                                                      |
| ------------ | ------- | ---- | ---------------------------------------------------------------- |
| **Language ID**  | *UInt32*  | 4    | Language identifier (see Language enum)                          |
| **String Size**  | *UInt32*  | 4    | Length of string in bytes                                       |
| **String Data**  | [char](GFF-File-Format#gff-data-types)[]  | N    | `windows-1252` encoded text                     |

**Localized string Usage:**

ERF localized strings provide multi-language descriptions for the container itself. These are primarily used in MOD files to display module names and descriptions in the game's module selection screen.

**Language IDs:**

- `0` = English
- `1` = French  
- `2` = German
- `3` = Italian
- `4` = Spanish
- `5` = Polish

**Important Notes:**

- Most *ERF* files have zero localized strings (*Language count* = 0)
- *MOD* files may include localized module names for the load screen
- **Engine Behavior**: The game engine's resource loader (`CExoKeyTable::AddEncapsulatedContents`) **ignores** these fields. They are likely used only by the specific UI components (like the Module Selection screen).
- **Encoding**: Strings should be encoded as `windows-1252` (CP1252) to support legacy BioWare character sets.
- The **Description [StrRef](TLK-File-Format#string-references-strref)** field (in header) provides an alternative via [TLK](TLK-File-Format) reference

**Reference**: [`vendor/reone/src/libs/resource/format/erfreader.cpp:47-65`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/erfreader.cpp#L47-L65)

### KEY List

Each **KEY** entry is 24 bytes and maps **[ResRefs](GFF-File-Format#gff-data-types)** to resource indices:

| Name        | type     | offset | size | Description                                                      |
| ----------- | -------- | ------ | ---- | ---------------------------------------------------------------- |
| **ResRef**      | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 16   | Resource filename (null-padded, max 16 chars)                    |
| **Resource ID** | UInt32   | 16 (0x10) | 4    | index into resource list                                         |
| **Resource Type** | [uint16](GFF-File-Format#gff-data-types) | 20 (0x14) | 2    | Resource type identifier                                         |
| **Unused**      | [uint16](GFF-File-Format#gff-data-types)   | 22 (0x16) | 2    | Padding                                                           |

***ResRef* Padding Notes:**

Resource names are padded with NULL bytes to 16 characters, but are not necessarily [null-terminated](https://en.cppreference.com/w/c/string/byte). If a resource name is exactly 16 characters long, no [null terminator](https://en.cppreference.com/w/c/string/byte) exists. Resource names can be mixed case, though most are lowercase in practice.

**Reference**: [`vendor/Kotor.NET/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs:115-168`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L115-L168)  
**Reference**: [`vendor/xoreos-docs/specs/torlack/mod.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/mod.html) - Resource structure details and **ResRef** padding notes

### Resource List

Each resource entry is 8 bytes:

| Name          | Type   | Offset | Size | Description                                                      |
| ------------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| Offset to Data | *UInt32* | 0 (0x00) | 4    | offset to resource data in file                                  |
| Resource Size | *UInt32* | 4 (0x04) | 4    | size of resource data in bytes                                   |

**Reference**: [`vendor/Kotor.NET/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs:119-120`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs#L119-L120)

### Resource data

Resource data is stored at the offsets specified in the resource list:

| Name         | Type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Resource Data | *[byte](https://en.wikipedia.org/wiki/Byte)* | Raw binary data for each resource                               |

### MOD/NWM File Format Quirk: Blank Data Block

**Note**: For *MOD* files only, there exists an unusual block of data between the resource structures (KEY List) and the position structures (Resource List). This block is 8 bytes per resource and appears to be all NULL bytes in practice. This data block is not referenced by any offset in the ERF *file header*, which is uncharacteristic of BioWare's file format design.

**Reference**: [`vendor/xoreos-docs/specs/torlack/mod.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/mod.html) - "Strange Blank data" section documenting this MOD/NWM-specific quirk

---

## ERF Variants

ERF files come in several variants based on *file type*:

| File Type | Extension | Description                                                      |
| --------- | --------- | ---------------------------------------------------------------- |
| ERF       | `.erf`    | Generic encapsulated resource file                               |
| MOD       | `.mod`    | Module file (contains area resources)                            |
| SAV       | `.sav`    | Save game file (contains saved game state)                       | 

All variants use the same binary format structure, differing only in the *file type signature*.

### MOD Files (module containers)

*MOD* files package all resources needed for a game module (level/area):

**Typical Contents:**

- *Area* layouts (`.are`, `.git`)
- *Module* information (`.ifo`)
- *Dialogs* and scripts (`.dlg`, `.ncs`)
- *Module*-specific [2DA](2DA-File-Format) overrides
- *Character* templates (`.utc`, `.utp`, `.utd`)
- *Waypoints* and triggers (`.utw`, `.utt`)

The game loads *MOD* files from the `modules/` directory. When entering a module, the engine mounts the *MOD* container and prioritizes its resources over [BIF files](BIF-File-Format) but below the `override/` folder.

### SAV Files (save game containers)

*SAV* files store complete game state:

**Contents:**

- Party member data (inventory, stats, equipped items)
- Module state (spawned creatures, opened containers)
- Global variables and plot flags
- Area layouts with modifications
- Quick bar configurations
- Portrait images

Save files preserve the state of all modified resources. When a placeable is looted or a door opened, the updated `.git` resource is stored in the *SAV* file.

### ERF Files (Generic Containers)

Generic ERF files serve miscellaneous purposes:

- [texture](TPC-File-Format) packs
- *Audio* replacement packs
- Campaign-specific resources
- Developer test containers

**Reference**: [`vendor/reone/src/libs/resource/format/erfreader.cpp:27-34`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/erfreader.cpp#L27-L34)

---

## Engine Internal Behavior

Reverse engineering of the game engine (specifically `CExoKeyTable::AddEncapsulatedContents` at `0x0040f3c0` in `swkotor.exe`) reveals how the engine actually parses these files.

### Critical vs. Metadata Fields

The engine's resource manager is surprisingly strict, reading the 160-byte header but **ignoring** most fields. It only validates/uses:

- **File Type** and **Version** (Verified against expected values)
- **Entry Count** (Used to allocate memory for the key table)
- **Offset to KEY List** (Used to seek to the *KEY* entries array)

The following fields are **parsed but ignored** by the resource manager (though they may be used by the UI/Menus):

- **Language Count** and **Localized string size**
- **Offset to Localized string List**
- **Build Year** and **Build Day**
- **Description [StrRef](TLK-File-Format#string-references-strref)**

### Save Game Detection

Contrary to popular belief, the engine does **not** identify Save Games based on the file type signature (*SAV* vs *ERF*) or the **Description [StrRef](TLK-File-Format#string-references-strref)** being `0`.

- **Mechanism**: The engine distinguishes save games based on **file context** (loading from the `saves/` directory) and the resource system usage (aliasing `SAVES:` path).
- **Implication**: Setting **Description [StrRef](TLK-File-Format#string-references-strref)** to `0` in a *MOD* file does *not* make it a save file. Legitimate modules (e.g., `unk_m41` series) use `0` as their **StrRef**.

### TSL Specific Quirks

- **LIPS MODs**: In *Knights of the Old Republic II: The Sith Lords*, *MOD* files related to lip-syncing (`lips_*.mod`) consistently use `0xCDCDCDCD` for the **Description [StrRef](TLK-File-Format#string-references-strref)**. This value (`0xCDCDCDCD` or `-842150451`) is a common "uninitialized memory" fill pattern in Microsoft C++ debug runtimes, suggesting these files were built with a debug version of the toolset.

---

## Implementation Details

**Binary Reading**: [`Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py)

**Binary Writing**: [`Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/io_erf.py)

**ERF Class**: [`Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py:100-229`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/erf/erf_data.py#L100-L229)

---

This documentation aims to provide a comprehensive overview of the *KotOR* *ERF* file format, focusing on the detailed file structure and data formats used within the games.

## See Also

- [BIF File Format](BIF-File-Format) - Container format used with [KEY File Format](KEY-File-Format) files
- [KEY File Format](KEY-File-Format) - Index for [BIF containers](BIF-File-Format) and resource resolution
- [GFF File Format](GFF-File-Format) - Common content type stored in *ERF* containers
- [RIM File Format](RIM-File-Format) - Resource Index Manifest file format

---

This documentation aims to provide a comprehensive overview of the *KotOR* *ERF* file format, focusing on the detailed file structure and data formats used within the games.