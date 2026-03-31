# GFF — Generic File Format

The Generic File Format (GFF) is the all-purpose binary container used to store structured game data in Knights of the Old Republic and The Sith Lords. Nearly every non-script, non-texture resource the engine reads at runtime is a GFF file: area definitions, creature templates, item blueprints, dialogue trees, journal entries, placeables, triggers, waypoints, and user interface layouts. The format was designed for rapid iteration — new fields can be added to any resource type without breaking backward compatibility, because readers simply skip labels they do not recognize.

GFF is shared across BioWare's Aurora engine family. The [official BioWare GFF specification](Bioware-Aurora-Core-Formats#gff) documents the format as it was designed; this page documents the format as KotOR and TSL actually use it, including field schemas, type-specific layouts, and practical modding considerations. For the common GFF struct schemas shared across area and module files, see [Bioware Aurora Common GFF Structs](Bioware-Aurora-Module-and-Area#commongffstructs).

Like all game resources, GFF files are resolved through the standard [resource resolution order](Concepts#resource-resolution-order): the engine checks the [override folder](Concepts#override-folder) first, then the active [MOD/ERF](Container-Formats#erf) module capsule, then [KEY/BIF](Container-Formats#key) base data. Modders can therefore shadow any vanilla GFF by placing a replacement in override or inside a module `.mod` file (see [Mod Creation Best Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files)). For merge-safe field-level edits, use [TSLPatcher/HoloPatcher GFFList syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) instead of full-file replacement.

GFF files work alongside [2DA](2DA-File-Format) configuration tables, [TLK](Audio-and-Localization-Formats#tlk) localized strings, [MDL/MDX](MDL-MDX-File-Format) 3D models, and [NCS](NCS-File-Format) compiled scripts. Historical editors include K-GFF ([LucasForums thread](https://www.lucasforumsarchive.com/thread/149407), [Deadly Stream listing](https://deadlystream.com/files/file/719-k-gff/)) and KotOR Tool; for current editing, use [Holocron Toolset](Holocron-Toolset-Getting-Started).

## Table of Contents

- GFF — Generic File Format
  - Table of Contents
  - [File structure overview](#file-structure-overview)
    - [GFF as a Universal Container](#gff-as-a-universal-container)
  - [Binary format](#binary-format)
    - [file header](#file-header)
    - [Label array](#label-array)
    - [Struct array](#struct-array)
    - [field array](#field-array)
    - [field data](#field-data)
    - [field Indices (Multiple Element Map / MultiMap)](#field-indices-multiple-element-map--multimap)
    - [List indices](#list-indices)
  - [GFF data types](#gff-data-types)
  - [GFF structure](#gff-structure)
    - [GFFStruct](#gffstruct)
    - [GFFField](#gfffield)
    - [GFFList](#gfflist)
  - [GFF Generic types](#gff-generic-types)
    - [ARE (Area)](#are-area)
    - [DLG (Dialogue)](#dlg-dialogue)
    - [FAC (Faction)](#fac-faction)
    - [GIT (game instance template)](#git-game-instance-template)
    - [GUI (Graphical User Interface)](#gui-graphical-user-interface)
    - [IFO (module info)](#ifo-module-info)
    - [JRL (Journal)](#jrl-journal)
    - [PTH (Path)](#pth-path)
    - [UTC (Creature)](#utc-creature)
    - [UTD (Door)](#utd-door)
    - [UTE (Encounter)](#ute-encounter)
    - [UTI (Item)](#uti-item)
    - [UTM (Merchant)](#utm-merchant)
    - [UTP (Placeable)](#utp-placeable)
    - [UTS (Sound)](#uts-sound)
    - [UTT (Trigger)](#utt-trigger)
    - [UTW (Waypoint)](#utw-waypoint)
  - [Alternative Terminology (Historical)](#alternative-terminology-historical)
  - [field data Access Patterns](#field-data-access-patterns)
    - [Direct Access types](#direct-access-types)
    - [Indirect Access types](#indirect-access-types)
    - [Complex Access types](#complex-access-types)
  - [Implementation Details](#implementation-details)

---

## File structure overview

A GFF file is a hierarchical tree of structs, fields, and lists. Each struct contains named fields; each field holds either a simple value (integer, float, string) or a reference to a nested struct or list of structs. This recursive design means the same binary container can represent a creature with an inventory of items, a dialogue tree with branching replies, or an area definition with dozens of placed objects — all without changing the file format itself.

### GFF as a universal container

The format provides several properties that made it practical for rapid game development:

- **Type safety**: every field carries an explicit data type, so readers can validate structure without external schemas.
- **Compact binary encoding**: significantly smaller than equivalent XML or JSON, which mattered for CD-based distribution.
- **Direct memory mapping**: the offset-based layout allows fast load without full parsing.
- **Backward and forward compatibility**: readers skip unknown labels, so adding a new field to a creature template does not break older tools or saves.

The engine uses the four-character file type signature (e.g. `UTC `, `DLG `, `ARE `) plus the version tag `V3.2` to identify GFF content. The same binary layout serves all of these resource types:

**Common Uses:**

- Character/Creature templates:

  - [UTC](GFF-File-Format#utc-creature)
  - [UTP](GFF-File-Format#utp-placeable)
  - [UTD](GFF-File-Format#utd-door)
  - [UTE](GFF-File-Format#ute-encounter)
  - Other UT* templates as needed

- Area definitions:

  - ARE
  - [GIT](GFF-File-Format#git-game-instance-template)
  - [IFO](GFF-File-Format#ifo-module-info)
- Dialogue trees ([DLG](GFF-File-Format#dlg-dialogue))
- Quest journals ([JRL](GFF-File-Format#jrl-journal))
- Module information ([IFO](GFF-File-Format#ifo-module-info))
- Save game state (SAV files contain GFF resources)
- User interface layouts ([GUI](GFF-File-Format#gui-graphical-user-interface))

Many KotOR file types are GFF containers with different signatures and field schemas, for example:

- `.utc` ([UTC](GFF-File-Format#utc-creature))
- `.uti` ([UTI](GFF-File-Format#uti-item))
- `.dlg` ([DLG](GFF-File-Format#dlg-dialogue))
- `.are` (ARE)

Dozens of other extensions are documented across this wiki.

**Implementation (PyKotor):**

- package: [`resource/formats/gff/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/)
- binary read [`GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82)
- write [`GFFBinaryWriter.write` L355+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L355)
- data model [`GFF` L509+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L509)
- [`GFFStruct` L689+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L689)
- XML/JSON/Twine variants in `io_gff_xml`, `io_gff_json`, `io_gff_twine`

**Cross-reference (other implementations):**

| Project | Path | Role |
|---------|------|------|
| [reone](https://github.com/modawan/reone) | [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) | C++ reader |
| [reone](https://github.com/modawan/reone) | [`gffwriter.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffwriter.cpp) | C++ writer |
| [reone](https://github.com/modawan/reone) | [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) | core GFF types |
| [xoreos](https://github.com/xoreos/xoreos) | [`gff3file.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/gff3file.cpp) | Aurora GFF3 |
| [KotOR.js](https://github.com/KobaltBlu/KotOR.js) | [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/resource/GFFObject.ts#L24) | TypeScript parser |
| [Kotor.NET](https://github.com/NickHugi/Kotor.NET) | [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) | .NET reader/writer |
| [KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity) | [`GFFObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/GFFObject.cs) | C# Unity loader |
| [xoreos-tools](https://github.com/xoreos/xoreos-tools) | [`gff3file.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/gff3file.cpp) | CLI tools |
| [bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats) | GFF Kaitai specs | Format specs |

### See also

- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) - Modding GFF files with TSLPatcher
- [2DA File Format](2DA-File-Format) - Configuration data referenced by GFF files
- [TLK File Format](Audio-and-Localization-Formats#tlk) - Text strings used by GFF LocalizedString fields
- [Bioware Aurora GFF Format](Bioware-Aurora-Core-Formats#gff) - Official BioWare specification

---

## Binary format

### File Header

The file header is 56 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type           | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | Content type (e.g., `"GFF "`, `"ARE "`, `"UTC "`) |
| file Version        | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | format version (`"V3.2"` for KotOR)           |
| Struct array offset | UInt32  | 8 (0x08) | 4    | offset to struct array                        |
| Struct count        | UInt32  | 12 (0x0C) | 4    | Number of structs                              |
| field array offset  | UInt32  | 16 (0x10) | 4    | offset to field array                         |
| field count         | UInt32  | 20 (0x14) | 4    | Number of fields                               |
| Label array offset   | UInt32  | 24 (0x18) | 4    | offset to label array                         |
| Label count          | UInt32  | 28 (0x1C) | 4    | Number of labels                               |
| field data offset    | UInt32  | 32 (0x20) | 4    | offset to field data section                  |
| field data count     | UInt32  | 36 (0x24) | 4    | size of field data section in bytes           |
| field indices offset | UInt32  | 40 (0x28) | 4    | offset to field indices array                 |
| field indices count  | UInt32  | 44 (0x2C) | 4    | Number of field indices                       |
| List indices offset  | UInt32  | 48 (0x30) | 4    | offset to list indices array                  |
| List indices count   | UInt32  | 52 (0x34) | 4    | Number of list indices                        |

**References:**

- PyKotor [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82)
- [reone](https://github.com/modawan/reone)
- [`gffreader.cpp` L30–L44](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/gffreader.cpp#L30-L44)

### Label array

Labels are 16-[byte](https://en.wikipedia.org/wiki/Byte) [null-terminated](https://en.cppreference.com/w/c/string/byte) strings used as field names:

| Name   | type     | size | Description                                                      |
| ------ | -------- | ---- | ---------------------------------------------------------------- |
| Labels | [char](GFF-File-Format#gff-data-types) | 16×N | array of field name labels (null-padded to 16 bytes)            |

**References:**

- [reone](https://github.com/modawan/reone)
- [`gffreader.cpp` L151–L154](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/gffreader.cpp#L151-L154)

### Struct array

Each struct entry is 12 bytes:

| Name       | type   | offset | size | Description                                                      |
| ---------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| Struct ID  | [int32](GFF-File-Format#gff-data-types)  | 0 (0x00) | 4    | structure type identifier                                        |
| data/offset| UInt32 | 4 (0x04) | 4    | field index (if 1 field) or offset to field indices (if multiple) |
| field count| UInt32 | 8 (0x08) | 4    | Number of fields in this struct (0, 1, or >1)                   |

**References:**

- [reone](https://github.com/modawan/reone)
- [`gffreader.cpp` L40–L62](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/gffreader.cpp#L40-L62)

### field array

Each field entry is 12 bytes:

| Name        | type   | offset | size | Description                                                      |
| ----------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| field type  | UInt32 | 0 (0x00) | 4    | data type (see [GFF Data Types](#gff-data-types))              |
| Label index | UInt32 | 4 (0x04) | 4    | index into label array for field name                           |
| data/offset | UInt32 | 8 (0x08) | 4    | Inline data (simple types) or offset to field data (complex types) |

**References:**

- [reone](https://github.com/modawan/reone)
- [`gffreader.cpp` L67–L76](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/gffreader.cpp#L67-L76)

### field data

Complex field types store their data in the field data section:

| field type        | Storage format                                                      |
| ----------------- | ------------------------------------------------------------------- |
| UInt64            | 8 bytes (uint64)                                                    |
| Int64             | 8 bytes (int64)                                                     |
| double            | 8 bytes (double)                                                    |
| string            | 4 bytes length + N bytes string data                                |
| ResRef            | 1 byte length + N bytes ResRef data (max 16 chars)                  |
| LocalizedString   | 4 bytes count + N×8 bytes ([Language ID](Concepts#language-ids-kotor) + [StrRef](Audio-and-Localization-Formats#string-references-strref) pairs)              |
| Binary            | 4 bytes length + N bytes binary data                                 |
| Vector3           | 12 bytes (3×float)                                                   |
| Vector4           | 16 bytes (4×float)                                                   |

**References:**

- [reone](https://github.com/modawan/reone)
- [`gffreader.cpp` L78–L146](https://github.com/modawan/reone/blob/61531089341caf5827abbc54346c8c959b03d449/src/libs/resource/format/gffreader.cpp#L78-L146)

### field Indices (Multiple Element Map / MultiMap)

When a struct has multiple fields, the struct's data field contains an offset into the field indices array (also called the "Multiple Element Map" or "MultiMap" in [xoreos-docs `specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html)), which lists the field indices for that struct.

**Access Pattern**: When a struct has exactly one field, the struct's data field directly contains the field index. When a struct has more than one field, the data field contains a byte offset into the field indices array, which is an array of uint32 values listing the field indices.

**References:**

- [xoreos-docs](https://github.com/xoreos/xoreos-docs)
- [`specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html) — MultiMap, entry/entity access

### List indices

Lists are stored as arrays of struct indices. The list field contains an offset into the list indices array, which contains the struct indices that make up the list.

**Access Pattern**: For a LIST type field, the field's data/offset value specifies a byte offset into the list indices table. At that offset, the first uint32 is the count of entries, followed by that many uint32 values representing the struct indices.

**References:**

- [xoreos-docs](https://github.com/xoreos/xoreos-docs)
- [`specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html) — LIST access

---

## GFF data types

GFF supports the following field types:

| type ID | Name              | Size (inline) | Description                                                      |
| ------- | ----------------- | ------------- | ---------------------------------------------------------------- |
| 0       | byte              | 1             | 8-bit unsigned integer                                           |
| 1       | char              | 1             | 8-bit signed integer                                              |
| 2       | Word              | 2             | 16-bit unsigned integer                                          |
| 3       | Short             | 2             | 16-bit signed integer                                             |
| 4       | DWord             | 4             | 32-bit unsigned integer                                          |
| 5       | Int               | 4             | 32-bit signed integer                                             |
| 6       | DWord64           | 8             | 64-bit unsigned integer (stored in field data)                  |
| 7       | Int64              | 8             | 64-bit signed integer (stored in field data)                      |
| 8       | float             | 4             | 32-bit floating point                                             |
| 9       | double            | 8             | 64-bit floating point (stored in field data)                     |
| 10      | CExoString        | varies        | [null-terminated](https://en.cppreference.com/w/c/string/byte) string (stored in field data)                    |
| 11      | ResRef            | varies        | Resource reference (stored in field data, max 16 chars)          |
| 12      | CExoLocString     | varies        | Localized string (stored in field data)                           |
| 13      | Void              | varies        | Binary data blob (stored in field data)                          |
| 14      | Struct            | 4             | Nested struct (struct index stored inline)                       |
| 15      | List              | 4             | List of structs (offset to list indices stored inline)            |
| 16      | orientation       | 16            | Quaternion (4×float, stored in field data as Vector4)            |
| 17      | vector            | 12            | 3D vector (3×float, stored in field data)                       |
| 18      | [StrRef](Audio-and-Localization-Formats#string-references-strref)            | 4             | string reference ([TLK](Audio-and-Localization-Formats#tlk) [StrRef](Audio-and-Localization-Formats#string-references-strref), stored inline as int32)             |

**References**

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py:73-108`](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L73-L108) - GFF data type definitions

**type Selection Guidelines:**

- Use **byte/char** for small integers (-128 to 255) and boolean flags
- Use **Word/Short** for medium integers like IDs and counts
- Use **DWord/Int** for large values and most numeric fields
- Use **float** for decimals that don't need high precision (positions, angles)
- Use **double** for high-precision calculations (rare in KotOR)
- Use **CExoString** for text that doesn't need localization
- Use **CExoLocString** for player-visible text that should be translated
- Use **ResRef** for filenames without extensions. Typical payloads include:

  - [models](MDL-MDX-File-Format)
  - [textures](Texture-Formats#tpc)
  - Scripts and other resources referenced by ResRef
- Use **Void** for binary blobs like encrypted data or custom structures
- Use **Struct** for nested objects with multiple fields
- Use **List** for arrays of structs (inventory items, dialogue replies)
- Use **vector** for 3D positions and directions
- Use **orientation** for [quaternion](MDL-MDX-File-Format#node-header) rotations
- Use **[StrRef](Audio-and-Localization-Formats#string-references-strref)** for references to [dialog.tlk](Audio-and-Localization-Formats#tlk) entries

**Storage Optimization:**

Inline types (0-5, 8, 14, 15, 18) store their value directly in the field entry, saving space and improving access speed. Complex types (6-7, 9-13, 16-17) require an offset to field data, adding overhead. When designing custom GFF schemas, prefer inline types where possible.

---

## GFF structure

### GFFStruct

A GFF struct is a collection of named fields. Each struct has:

- **Struct ID**: type identifier (often 0xFFFFFFFF for generic structs)
- **fields**: Dictionary mapping field names (labels) to field values

**References**

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py) - GFFStruct, GFFField, GFFList implementation

### GFFField

fields can be accessed using type-specific getter/setter methods:

- `get_uint8(label)`, `set_uint8(label, value)`
- `get_int32(label)`, `set_int32(label, value)`
- `get_float(label)`, `set_float(label, value)`
- `get_string(label)`, `set_string(label, value)`
- `get_resref(label)`, `set_resref(label, value)`
- `get_locstring(label)`, `set_locstring(label, value)`
- `get_vector3(label)`, `set_vector3(label, value)`
- `get_struct(label)`, `set_struct(label, struct)`
- `get_list(label)`, `set_list(label, list)`

### GFFList

A GFF list is an ordered collection of structs. Lists are accessed via:

- `get_list(label)`: Returns a `GFFList` object
- `GFFList.get(i)`: Gets struct at index `i`
- `GFFList.append(struct)`: Adds a struct to the list

**Common List Usage:**

Lists are used extensively for variable-length arrays:

- **ItemList** in [UTC](GFF-File-Format#utc-creature) files: Character inventory items
- **Equip_ItemList** in [UTC](GFF-File-Format#utc-creature) files: Equipped items
- **EntryList** in [DLG](GFF-File-Format#dlg-dialogue) files: Dialogue entry [nodes](MDL-MDX-File-Format#node-structures)
- **ReplyList** in [DLG](GFF-File-Format#dlg-dialogue) files: Dialogue reply options
- **SkillList** in [UTC](GFF-File-Format#utc-creature) files: Character skills
- **FeatList** in [UTC](GFF-File-Format#utc-creature) files: Character feats
- **EffectList** in various files: Applied effects
- **Creature_List** in [GIT](GFF-File-Format#git-game-instance-template) files: Spawned creatures in area

When modifying lists, always maintain struct IDs and parent references to avoid breaking internal links.

---

## GFF Generic types

GFF files are used as containers for various game resource types. Each generic type has its own structure and field definitions.

### ARE (Area)

See [ARE (Area)](GFF-Module-and-Area#are) for detailed documentation.

### DLG (Dialogue)

See [DLG (Dialogue)](GFF-Creature-and-Dialogue#dlg) for detailed documentation.

### FAC (Faction)

See [FAC (Faction)](GFF-Items-and-Economy#fac) for detailed documentation.

### GIT (game instance template)

See [GIT (Game Instance Template)](GFF-Module-and-Area#git) for detailed documentation.

### GUI (Graphical User Interface)

See [GUI (Graphical User Interface)](GFF-GUI) for detailed documentation.

### IFO (module info)

See [IFO (Module Info)](GFF-Module-and-Area#ifo) for detailed documentation.

### JRL (Journal)

See [JRL (Journal)](GFF-Items-and-Economy#jrl) for detailed documentation.

### PTH (Path)

See [PTH (Path)](GFF-Spatial-Objects#pth) for detailed documentation.

### UTC (Creature)

See [UTC (Creature)](GFF-Creature-and-Dialogue#utc) for detailed documentation.

### UTD (Door)

See [UTD (Door)](GFF-Spatial-Objects#utd) for detailed documentation.

### UTE (Encounter)

See [UTE (Encounter)](GFF-Spatial-Objects#ute) for detailed documentation.

### UTI (Item)

See [UTI (Item)](GFF-Items-and-Economy#uti) for detailed documentation.

### UTM (Merchant)

See [UTM (Merchant)](GFF-Items-and-Economy#utm) for detailed documentation.

### UTP (Placeable)

See [UTP (Placeable)](GFF-Spatial-Objects#utp) for detailed documentation.

### UTS (Sound)

See [UTS (Sound)](GFF-Spatial-Objects#uts) for detailed documentation.

### UTT (Trigger)

See [UTT (Trigger)](GFF-Spatial-Objects#utt) for detailed documentation.

### UTW (Waypoint)

See [UTW (Waypoint)](GFF-Spatial-Objects#utw) for detailed documentation.

## Alternative Terminology (Historical)

The GFF format is also known as "ITP" in [xoreos-docs `specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html) (Tim Smith/Torlack's reverse-engineered documentation from the **Neverwinter Nights era**, but the format is **identical in KotOR**).

The following terminology mapping may be helpful when reading older specifications:

| Modern Term (GFF) | Historical Term (ITP) | Description |
| ----------------- | --------------------- | ----------- |
| Struct array | Entry Table / Entity Table | array of struct entries |
| field array | Element Table | array of field/element entries |
| Label array | Variable Names Table | array of 16-byte field name strings |
| field data | Variable data Section | Storage for complex field types |
| field indices | Multiple Element Map (MultiMap) | array mapping structs to their fields |
| List indices | List Section | array mapping list fields to struct indices |

**Note**: The first entry in the struct array is always the root of the entire hierarchy. All other structs and fields can be accessed from this root entry.

**References:**

- [xoreos-docs](https://github.com/xoreos/xoreos-docs)
- [`specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html) — Torlack GFF/ITP spec

## field data Access Patterns

### Direct Access types

Simple types (uint8, Int8, uint16, int16, uint32, int32, float) store their values directly in the field entry's data/offset field (offset 0x0008 in the element structure). These values are stored in [little-endian](https://en.wikipedia.org/wiki/Endianness) format.

### Indirect Access types

Complex types require accessing data from the field data section:

- **UInt64, Int64, double**: The field's data/offset contains a byte offset into the field data section where the 8-byte value is stored.
- **String (CExoString)**: The offset points to a uint32 length followed by the string bytes (not [null-terminated](https://en.cppreference.com/w/c/string/byte)).
- **ResRef**: The offset points to a uint8 length (max 16) followed by the resource name bytes (not [null-terminated](https://en.cppreference.com/w/c/string/byte)).
- **LocalizedString (CExoLocString)**: The offset points to a structure containing:
  - uint32: Total size (not including this count)
  - int32: [StrRef](Audio-and-Localization-Formats#string-references-strref) ID ([dialog.tlk](Audio-and-Localization-Formats#tlk) reference, -1 if none)
  - uint32: Number of language-specific strings
  - For each language string (if count > 0):
    - uint32: Language ID ([Concepts](Concepts#language-ids-kotor))
    - uint32: string length in bytes
    - char[]: string data
- **Void (Binary)**: The offset points to a uint32 length followed by the binary data bytes.
- **Vector3**: The offset points to 12 bytes (3×float) in the field data section.
- **Vector4 / orientation**: The offset points to 16 bytes (4×float) in the field data section.

### Complex Access types

- **Struct (CAPREF)**: The field's data/offset contains a struct index (not an offset). This references a struct in the struct array.
- **List**: The field's data/offset contains a byte offset into the list indices array. At that offset, the first uint32 is the entry count, followed by that many uint32 struct indices.

**References:**

- [xoreos-docs](https://github.com/xoreos/xoreos-docs)
- [`specs/torlack/itp.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/itp.html) — access patterns, code examples

## Implementation Details

| Component | PyKotor path | Line reference |
|-----------|--------------|----------------|
| Binary read | `io_gff.py` | [`GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) |
| Binary write | `io_gff.py` | [`GFFBinaryWriter.write` L345+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L345) |
| GFF data model | `gff_data.py` | [`GFF` L509+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L509) |
| GFFStruct | `gff_data.py` | [L689+](https://github.com/OldRepublicDevs/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L689) |

### See also

- [GFF-ARE](GFF-Module-and-Area#are)
- [GFF-DLG](GFF-Creature-and-Dialogue#dlg)
- [GFF-IFO](GFF-Module-and-Area#ifo)
- [GFF-UTI](GFF-Items-and-Economy#uti)
- [GFF-UTC](GFF-Creature-and-Dialogue#utc)
- [GIT](GFF-File-Format#git-game-instance-template) -- GFF-based game resources
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Patching GFF via HoloPatcher/TSLPatcher
- [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers) -- Hex resource type IDs (ResRef + type in archives)
- [KEY-File-Format](Container-Formats#key) -- Resource resolution
- [Bioware-Aurora-GFF](Bioware-Aurora-Core-Formats#gff) -- Aurora GFF specification
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for GFF structure and modding

---
