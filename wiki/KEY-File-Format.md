# KotOR KEY file format Documentation

This document provides a detailed description of the KEY (KEY Table) file format used in Knights of the Old Republic (KotOR) games. KEY files serve as the master index for all [BIF files](BIF-File-Format) in the game.

## Table of Contents

- KotOR KEY File format Documentation
  - Table of Contents
  - [File structure overview](#file-structure-overview)
    - [KEY File Purpose](#key-file-purpose)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [File Table](#file-table)
    - [Filename Table](#filename-table)
    - [KEY Table](#key-table)
  - [Resource ID Encoding](#resource-id-encoding)
  - [Implementation Details](#implementation-details)

---

## File structure overview

KEY files map resource names ([ResRefs](GFF-File-Format#gff-data-types)) and types to specific locations within [BIF containers](BIF-File-Format). KotOR uses `chitin.key` as the main KEY file which references all game [BIF files](BIF-File-Format). **Modder note:** Mods do not edit the KEY; they add content via the [override folder](Concepts#override-folder) or [MOD/ERF](Concepts#mod-erf-rim) so the engine finds their resources first. See [Concepts](Concepts) and [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files).

### KEY File Purpose

The *KEY* file, specifically `chitin.key` in KotOR, serves as the master index for the game's resource system:

1. **Resource Lookup**: Maps *ResRef* + *Resource Type* ([hex IDs and labels](Resource-Formats-and-Resolution#resource-type-identifiers)) → [BIF](BIF-File-Format) location
2. **[BIF](BIF-File-Format) Registration**: Tracks all [BIF files](BIF-File-Format) and their install paths
3. **Resource Naming**: Provides the filename (*ResRef*) missing from [BIF files](BIF-File-Format)
4. **Drive Mapping**: Historical feature indicating which media ([CD](https://en.wikipedia.org/wiki/Compact_disc)/[HD](https://en.wikipedia.org/wiki/Hard_disk_drive)) contained each [BIF](BIF-File-Format)

**Resource resolution (conceptual):** The full search order (override → MOD/ERF → save → KEY/BIF → defaults) and how the resource manager satisfies a demand are documented on [Concepts](Concepts#resource-resolution-order). This page describes what the *KEY* contributes to that pipeline.

The *KEY* indexes [BIF](BIF-File-Format) entries only (step 4 in that order). Higher-priority sources can shadow *KEY*-indexed assets without editing the *KEY*; using override or MOD for that is normal modding practice.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/key/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/key/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — in-repo layout spec: [`key_data.py` L1–L55](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L1-L55); binary I/O: [`KEYBinaryReader.load`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L65-L128), [`KEYBinaryWriter`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L143-L195) (`io_key.py`); data model: [`BifEntry`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L66-L152), [`KeyEntry`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L154-L288), [`KEY`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L291-L473).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)) — [`keyreader.cpp` `KeyReader::load`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L29-L39), [`loadFiles` / `readFileEntry`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L41-L66), [`loadKeys` / `readKeyEntry`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L68-L86) (lowercases ResRefs; splits `resource_id` into BIF index and resource index). reone reads the 8-byte `"KEY V1 "` signature as one block, then the four table counts/offsets; it does not surface build year/day in this reader (those bytes are still present in KotOR `chitin.key` after the offsets).
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora *KEY* (`src/aurora/keyfile.cpp`), shared across Aurora-family games ([tools mirror: xoreos-tools](https://github.com/xoreos/xoreos-tools)).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — [`KEYObject.ts` `loadFile`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/KEYObject.ts#L39-L89) (header, BIF table, filename resolution, key entries); resource id helpers: [`getBIFIndex` / `getBIFResourceIndex`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/KEYObject.ts#L139-L147) (note: `getBIFResourceIndex` masks with `0x3FFF` in this file — the on-disk encoding uses **20** low bits; prefer `resId & 0xFFFFF` to match PyKotor/reone and the table below).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — [`KEYBinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs#L17-L114) (`FileRoot`, `FileHeader`, `BIFInfo`, `Key` with `IndexIntoFileTable` / `IndexIntoResourceTable` properties).

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

### File Header

The file header is 64 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| File Type           | [Char](https://en.wikipedia.org/wiki/Character_(computer_science)) | `0` (`0x00`) | `4`    | Always `"KEY "` (space-padded)                 |
| File Version        | [Char](https://en.wikipedia.org/wiki/Character_(computer_science)) | `4` (`0x04`) | `4`    | `"V1  "` or `"V1.1"`                           |
| [BIF](BIF-File-Format) count           | UInt32  | `8` (`0x08`) | `4`    | Number of [BIF files](BIF-File-Format) referenced                 |
| KEY count           | UInt32  | `12` (`0x0C`) | `4`    | Number of *Resource Entries*                     |
| Offset to File Table | UInt32 | `16` (`0x10`) | `4`    | Offset to [BIF File](BIF-File-Format) Entries* Array               |
| Offset to KEY Table | UInt32 | `20` (`0x14`) | `4`    | Offset to *Resource Entries* Array               |
| Build Year          | UInt32  | `24` (`0x18`) | `4`    | Build Year (years since 1900)                  |
| Build Day           | UInt32  | `28` (`0x1C`) | `4`    | Build Day (days since Jan 1)                   |
| Reserved            | [Byte](https://en.wikipedia.org/wiki/Byte) | `32` (`0x20`) | `32`   | Padding (usually zeros)                        |

**Note on Header Variations**: **[xoreos-docs](https://github.com/xoreos/xoreos-docs)**: [`specs/torlack/key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) (Tim Smith/Torlack's reverse-engineered documentation) shows the header ending at offset `0x0040` with unknown values at offset `0x0018`. The structure shown here (with *Build Year*/*Build Day* and *Reserved* fields) matches the actual *KotOR KEY* File Format.

**References**

**Vendor Implementations:**

- [Kotor.NET `KEYBinaryStructure.cs` L17–L114](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs#L17-L114) — .NET *KEY* binary layout (`FileRoot` constructor walks BIF list, filename table, then keys).
- [xoreos-docs Torlack `key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) — historical community *KEY* write-up (header details may differ slightly from KotOR on-disk layout above).

### File Table

Each file entry is 12 bytes:

| Name            | Type   | Offset | Size | Description                                                      |
| --------------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| File Size       | UInt32 | `0` (0x00) | `4`    | Size of [BIF](BIF-File-Format) file on disk                                         |
| Filename Offset | UInt32 | `4` (0x04) | `4`    | Offset into filename table                                       |
| Filename Length | [UInt16](GFF-File-Format#gff-data-types) | `8` (0x08) | `2`    | Length of filename in bytes                                      |
| Drives          | [UInt16](GFF-File-Format#gff-data-types) | `10` (0x0A) | `2`    | Drive flags (`0x0001=HD0`, `0x0002=CD1`, etc.)                      |

**Drive Flags Explained:**

*Drive Flags* are a legacy feature from the multi-[CD](https://en.wikipedia.org/wiki/Compact_disc) distribution era:

| Flag Value | Meaning | Description |
| ---------- | ------- | ----------- |
| `0x0001` | `HD` ([Hard Drive](https://en.wikipedia.org/wiki/Hard_disk_drive)) | [BIF](BIF-File-Format) is installed on the hard drive |
| `0x0002` | `CD1` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 1) | [BIF](BIF-File-Format) is on the first game disc |
| `0x0004` | `CD2` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 2) | [BIF](BIF-File-Format) is on the second game disc |
| `0x0008` | `CD3` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 3) | [BIF](BIF-File-Format) is on the third game disc |
| `0x0010` | `CD4` ([CD](https://en.wikipedia.org/wiki/Compact_disc) 4) | [BIF](BIF-File-Format) is on the fourth game disc |

**Modern Usage:**

In contemporary distributions ([Steam](https://store.steampowered.com/), [GOG](https://www.gog.com/), [digital](https://en.wikipedia.org/wiki/Digital_distribution)):

- All [BIF files](BIF-File-Format) use `0x0001` (`HD` Flag) since everything is installed locally
- The engine doesn't prompt for disc swapping
- Multiple flags can be combined (bitwise OR) if a [BIF](BIF-File-Format) could be on multiple sources (e.g. `0x0001 | 0x0002` ([HD](https://en.wikipedia.org/wiki/Hard_disk_drive) Flag | [CD1](https://en.wikipedia.org/wiki/Compact_disc) Flag) for a [BIF](BIF-File-Format) that is on both the hard drive and the first game disc)
- Mod tools typically set this to `0x0001` (`HD` Flag) for all files

The drive system was originally designed so the engine could:

- Prompt users to insert specific [CD](https://en.wikipedia.org/wiki/Compact_disc)s when needed resources weren't on the hard drive
- Optimize installation by allowing users to choose what to install vs. run from [CD](https://en.wikipedia.org/wiki/Compact_disc)
- Support partial installs to save disk space (common in the early 2000s)

**References**

**Vendor Implementations:**

- [reone `keyreader.cpp` `loadFiles` / `readFileEntry` L41–L66](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L41-L66) — file table and filename resolution.

### Filename Table

The *Filename Table* contains [null-terminated](https://en.cppreference.com/w/c/string/byte) strings:

| Name      | Type   | Description                                                      |
| --------- | ------ | ---------------------------------------------------------------- |
| Filenames | [char](GFF-File-Format#gff-data-types)[] | [null-terminated](https://en.cppreference.com/w/c/string/byte) [BIF](BIF-File-Format) Filenames (e.g., `data/[models](MDL-MDX-File-Format).bif`)         |

### *KEY* Table

Each *KEY* entry is `22` (`0x16`) bytes in size:

| Name        | Type     | Offset | Size | Description                                                      |
| ----------- | -------- | ------ | ---- | ---------------------------------------------------------------- |
| *ResRef*      | [char](GFF-File-Format#gff-data-types) | `0` (`0x00`) | `16`   | Resource Filename (null-padded, max 16 characters)                   |
| Resource Type | [UInt16](GFF-File-Format#gff-data-types) | `16` (`0x10`) | `2`    | Numeric resource type ID ([wiki table](Resource-Formats-and-Resolution#resource-type-identifiers); PyKotor [`ResourceType`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py))                                         |
| Resource ID | UInt32   | `18` (`0x12`) | `4`    | Encoded Resource Location (see [Resource ID Encoding](#resource-id-encoding)) (e.g. `0x00000005` for the 5th Resource in the 1st [BIF](BIF-File-Format)) |

**Critical Structure Packing Note:**

  The *KEY* entry structure must use **[byte](https://en.wikipedia.org/wiki/Byte) or [word](https://en.wikipedia.org/wiki/Word_(computer_architecture)) alignment** (1-[byte](https://en.wikipedia.org/wiki/Byte) or 2-[byte](https://en.wikipedia.org/wiki/Byte) packing). If the structure is packed with `4-[byte](https://en.wikipedia.org/wiki/Byte)` or `8-[byte](https://en.wikipedia.org/wiki/Byte)` alignment, the `UInt32` at offset `0x0012` (`18`) will be incorrectly placed at offset `0x0014` (`20`), causing incorrect *Resource ID* decoding.

On non-Intel platforms, this alignment requirement may cause alignment faults unless the compiler provides an "unaligned" type or special care is taken when accessing the `UInt32` field. The structure should be explicitly packed to ensure the `UInt32` starts at offset `18` (`0x12`) rather than being aligned to a `4-[byte](https://en.wikipedia.org/wiki/Byte)` or `8-[byte](https://en.wikipedia.org/wiki/Byte)` boundary.

**References**

**Vendor Implementations:**

- [reone `keyreader.cpp` `loadKeys` / `readKeyEntry` L68–L86](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L68-L86) — 16-byte ResRef, type `uint16`, `resource_id` `uint32`, then split `>> 20` / `& 0xFFFFF`.

---

## Resource ID Encoding

The *Resource ID* field encodes both the [BIF](BIF-File-Format) index and resource index within that [BIF](BIF-File-Format):

- **bits `31-20`**: [BIF](BIF-File-Format) Index (top 12 bits) - index into file table
- **bits `19-0`**: Resource Index (bottom 20 bits) - index within the [BIF](BIF-File-Format) file

**Decoding:**

```python
bif_index = (resource_id >> 20) & 0xFFF  # top 12 bits
resource_index = resource_id & 0xFFFFF   # bottom 20 bits
```

**Encoding:**

```python
resource_id = (bif_index << 20) | resource_index
```

**Practical Limits:**

- Maximum [BIF](BIF-File-Format) Files: `4,096` (12-bit [BIF](BIF-File-Format) index)
- Maximum Resources per [BIF](BIF-File-Format) File: `1,048,576` (20-bit resource index)

These limits are more than sufficient for KotOR, which typically has:

- `~50-100` [BIF](BIF-File-Format) Files in a full installation
- `~100-10,000` Resources per [BIF](BIF-File-Format) File (largest [BIF](BIF-File-Format) Files are [texture](TPC-File-Format) packs)

**Example:**

Given *Resource ID* `0x00123456`:

```plaintext
Binary: 0000 0000 0001 0010 0011 0100 0101 0110
        |---- 12 bits -----|------ 20 bits ------|
BIF Index:     0x001 (BIF Index: `1`)
Resource Index: 0x23456 (Resource Index: `144,470` within that [BIF](BIF-File-Format) file)
```

The encoding allows a single 32-bit integer to precisely locate any resource in the entire [BIF](BIF-File-Format) system (e.g. `0x00123456` for the 5th resource in the 1st [BIF](BIF-File-Format) file).

**References**

**Vendor Implementations:**

- [reone `readKeyEntry` L82–L84](https://github.com/modawan/reone/blob/master/src/libs/resource/format/keyreader.cpp#L82-L84) — `bifIdx = resId >> 20`, `resIdx = resId & 0xfffff`.
- [xoreos-docs Torlack `key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) — worked example of packed *Resource ID* (BIF index + index within BIF).

---

## Implementation Details

| Layer | PyKotor (`master`) |
| ----- | ------------------- |
| Binary read | [`io_key.py` `KEYBinaryReader.load` L65–L128](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L65-L128) |
| Binary write | [`io_key.py` `KEYBinaryWriter` L143–L195](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/io_key.py#L143-L195) |
| Layout reference (docstring) | [`key_data.py` L1–L55](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L1-L55) |
| `BifEntry` / `KeyEntry` / `KEY` | [`key_data.py` L66–L473](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/key/key_data.py#L66-L473) |

See **Cross-reference implementations** under [File structure overview](#file-structure-overview) for reone, KotOR.js, Kotor.NET, and xoreos.

### See also

- [BIF File Format](BIF-File-Format) - Container format indexed by KEY
- [ERF File Format](ERF-File-Format) - Self-contained containers (MOD/SAV/HAK) and resolution order
- [RIM File Format](RIM-File-Format) - Stock module archives (resource image); [RIM versus ERF](ERF-File-Format#rim-versus-erf)
- [GFF File Format](GFF-File-Format) - Common content type resolved via KEY/BIF
- [Bioware Aurora KeyBIF](Bioware-Aurora-KeyBIF) - Official BioWare KEY/BIF specification
- [Concepts](Concepts) - Resource resolution order, override folder
- [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers) - Hex resource type IDs (SSOT table)
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for override and resolution troubleshooting

---

This documentation aims to provide a comprehensive overview of the *KotOR KEY* File Format, focusing on the detailed file structure and data formats used within the games.
