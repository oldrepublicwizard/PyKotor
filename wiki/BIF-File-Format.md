# KotOR BIF file format Documentation

This document provides a detailed description of the BIF (BioWare index file) file format used in Knights of the Old Republic (KotOR) games. BIF files are [container containers](ERF-File-Format) that store the bulk of game resources.

## Table of Contents

- KotOR BIF file format Documentation
  - Table of Contents
  - [File structure overview](#file-structure-overview)
    - [BIF Usage in KotOR](#bif-usage-in-kotor)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Variable resource table](#variable-resource-table)
    - [Resource data](#resource-data)
  - [BZF Compression](#bzf-compression)
    - [BZF format details](#bzf-format-details)
  - [KEY file Relationship](#key-file-relationship)
  - [Implementation Details](#implementation-details)

---

## File structure overview

BIF files work in tandem with [KEY files](KEY-File-Format) which provide the filename-to-resource mappings. BIF files contain only resource IDs, types, and data - the actual filenames ([ResRefs](GFF-File-Format#gff-data-types)) are stored in the [KEY file](KEY-File-Format). BIF files are [container containers](ERF-File-Format) that store the bulk of game resources.

### BIF Usage in KotOR

BIF containers are the primary storage mechanism for game assets. The game organizes resources into multiple BIF files by category:

- `data/models.bif`: 3D [model](MDL-MDX-File-Format) files ([MDL/MDX](MDL-MDX-File-Format))
- `data/textures_*.bif`: [texture](TPC-File-Format) data ([TPC](TPC-File-Format)/[TXI](TXI-File-Format) files) - split across multiple containers
- `data/sounds.bif`: Audio files ([WAV](WAV-File-Format))
- `data/2da.bif`: Game data tables ([2DA files](2DA-File-Format))
- `data/scripts.bif`: Compiled scripts ([NCS](NCS-File-Format))
- `data/dialogs.bif`: Conversation files ([DLG](GFF-DLG))
- `data/lips.bif`: [LIP](LIP-File-Format)-sync [animation](MDL-MDX-File-Format#animation-header) data ([LIP](LIP-File-Format))
- Additional platform-specific BIFs (e.g., `dataxbox/`, `data_mac/`)

The [modular structure](https://en.wikipedia.org/wiki/Modular_programming) allows for efficient loading and potential platform-specific optimizations. Resources in BIF files are read-only at runtime; mods override them via the `override/` directory or custom [ERF](ERF-File-Format)/MOD files. The engine loads from BIF only when the resource is not found in [override](KEY-File-Format#key-file-purpose), loaded MOD, or save; the [KEY file](KEY-File-Format) supplies the mapping from ResRef to the correct BIF and offset.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/bif/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/)

**Vendor References:**

Repositories (original first, mirror second): **[reone](https://github.com/seedhartha/reone)** ([Mirror: th3w1zard1/reone](https://github.com/th3w1zard1/reone)), **[xoreos](https://github.com/xoreos/xoreos)** ([Mirror: th3w1zard1/xoreos](https://github.com/th3w1zard1/xoreos)), **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** ([Mirror: th3w1zard1/KotOR.js](https://github.com/th3w1zard1/KotOR.js)), **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** ([Mirror: th3w1zard1/Kotor.NET](https://github.com/th3w1zard1/Kotor.NET)), **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** ([Mirror: th3w1zard1/xoreos-tools](https://github.com/th3w1zard1/xoreos-tools)), **[bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats)** - Kaitai Struct format specs for BIF and other BioWare formats (no mirror).

- **[reone](https://github.com/seedhartha/reone)** ([Mirror: th3w1zard1/reone](https://github.com/th3w1zard1/reone)): [`src/libs/resource/format/bifreader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/bifreader.cpp) - Complete C++ BIF reader implementation
- **[xoreos](https://github.com/xoreos/xoreos)** ([Mirror: th3w1zard1/xoreos](https://github.com/th3w1zard1/xoreos)): [`src/aurora/biffile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp) - Generic Aurora BIF implementation (shared format across KotOR, NWN, and other Aurora games)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** ([Mirror: th3w1zard1/KotOR.js](https://github.com/th3w1zard1/KotOR.js)): [`src/resource/BIFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/BIFObject.ts) - TypeScript BIF parser with decompression
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** ([Mirror: th3w1zard1/Kotor.NET](https://github.com/th3w1zard1/Kotor.NET)): [`Kotor.NET/Formats/KotorBIF/`](https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats/KotorBIF) - .NET BIF reader/writer
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** ([Mirror: th3w1zard1/xoreos-tools](https://github.com/th3w1zard1/xoreos-tools)): [`src/aurora/biffile.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/aurora/biffile.cpp) - Command-line BIF extraction tools

---

## [Binary Format](https://en.wikipedia.org/wiki/Binary_file)

### File Header

The file header is 20 bytes in size:

| Name                      | type    | offset | size | Description                                    |
| ------------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| File Type                 | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | `"BIFF"` for BIF, `"BZF "` for compressed BIF  |
| File Version              | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | `"V1  "` for BIF, `"V1.0"` for BZF             |
| Variable Resource count   | UInt32  | 8 (0x08) | 4    | Number of variable-size resources              |
| Fixed Resource count      | UInt32  | 12 (0x0C) | 4    | Number of fixed-size resources (unused, always 0) |
| Offset to Variable Resource Table | UInt32 | 16 (0x10) | 4 | offset to variable resource entries            |

**Note on Fixed Resources:** The "Fixed Resource count" field is a legacy holdover from *Neverwinter Nights* (not used in *KotOR*) where some resource types had predetermined sizes. In *KotOR*, this field is always `0` and fixed resource tables are never used. All resources are stored in the variable resource table regardless of their size.

**Note on header Variations**: [`vendor/xoreos-docs/specs/torlack/bif.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/bif.html) (Tim Smith/Torlack's reverse-engineered documentation) shows the field at offset `0x000C` as "Unknown value" rather than "Fixed Resource count". This reflects the field's historical ambiguity, but in practice it serves as the fixed resource count (always `0` in *KotOR*).

**References**

**Vendor Implementations:**

- [`vendor/xoreos/src/aurora/biffile.cpp:64-67`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L64-L67) - Checks fixed resource count is 0
- [`vendor/reone/src/libs/resource/format/bifreader.cpp:34`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/bifreader.cpp#L34) - Header parsing
- [`vendor/Kotor.NET/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs:13-67`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L13-L67) - .NET BIF binary structure
- [`vendor/xoreos-docs/specs/torlack/bif.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/bif.html) - Tim Smith (Torlack)'s reverse-engineered BIF format documentation

### Variable Resource Table

Each variable resource entry is 16 bytes:

| Name        | type   | offset | size | Description                                                      |
| ----------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| Resource ID | `UInt32` | 0 (0x00) | 4    | Resource ID (matches [KEY file](KEY-File-Format) entry, encodes BIF index and resource index) |
| Offset      | `UInt32` | 4 (0x04) | 4    | Offset to resource data in file (absolute file offset)                    |
| File Size   | `UInt32` | 8 (0x08) | 4    | Uncompressed size of resource data (bytes)                                 |
| Resource type | `UInt32` | 12 (0x0C) | 4    | Resource type identifier (see ResourceType enum)                          |

**Entry Reading Order:**

Entries are read sequentially from the variable resource table. The table is located at the offset specified in the file header. Each entry is exactly 16 bytes, allowing efficient sequential reading.

**References**

**Vendor Implementations:**

- [`vendor/reone/src/libs/resource/format/bifreader.cpp:50-63`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/bifreader.cpp#L50-L63) - Variable resource entry reading order
- [`vendor/Kotor.NET/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs:51-65`](https://github.com/th3w1zard1/Kotor.NET/blob/master/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L51-L65) - Entry structure
- [`vendor/xoreos/src/aurora/biffile.cpp:84-96`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L84-L96) - Reading with version-specific handling

### Resource Data

*Resource Data* is stored at the offsets specified in the resource table:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Resource Data | [byte](https://en.wikipedia.org/wiki/Byte)[] | Raw binary data for each resource                               |

**Resource Storage Details:**

- Resources are stored sequentially but not necessarily contiguously (gaps may exist between resources)
- Each resource's size is specified in the variable resource table entry
- *Resource Data* is stored in its native format (no additional BIF-specific wrapping or metadata)
- Offsets in the variable resource table are absolute file offsets (relative to start of file)
- *Resource Data* begins immediately at the specified offset

**Resource Access Flow:**

The engine reads resources through the following process:

1. **KEY Lookup**: Look up the ResRef (and optionally *ResourceType*) in the [KEY file](KEY-File-Format) to get the Resource ID
2. **ID Decoding**: Extract the BIF index (upper 12 bits) and resource index (lower 20 bits) from the *Resource ID*
3. **BIF Selection**: Use the BIF index to identify which *BIF* file contains the resource
4. **Table Access**: Read the *BIF* file header to find the offset to the variable resource table
5. **Entry Lookup**: Find the resource entry at the specified index in the *variable resource table*
6. **Data Reading**: Seek to the offset specified in the entry and read the number of bytes specified by the file size

**References**

**Vendor Implementations:**

- [`vendor/xoreos/src/aurora/biffile.cpp:84-96`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L84-L96) - Variable resource entry reading
- [`vendor/reone/src/libs/resource/format/bifreader.cpp:41-48`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/bifreader.cpp#L41-L48) - Resource table loading
- [`vendor/xoreos/src/aurora/biffile.cpp:99-123`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L99-L123) - mergeKEY process combining KEY and BIF
- [`vendor/xoreos-docs/specs/torlack/bif.html`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/bif.html) - Resource structure details (Resource ID, offset, length, type)

**Resource IDs:**

The *Resource ID* in the *BIF* file's *variable resource table* must match the *Resource ID* stored in the [KEY file](KEY-File-Format). The *Resource ID* is a 32-bit value that encodes two pieces of information:

- **Lower 20 bits (bits 0-19)**: Resource index within the *BIF* file (0-based index into the variable resource table)
- **Upper 12 bits (bits 20-31)**: BIF index in the [KEY file](KEY-File-Format)'s *BIF* table (identifies which *BIF* file contains this resource)

**Example:** A *Resource ID* of `0x00400029` decodes as:

- Resource index: `0x29` (41st resource in the *BIF*)
- BIF index: `0x004` (4th *BIF* file in the [KEY](KEY-File-Format)'s *BIF* table)

**References**

**Vendor Implementations:**

- [`vendor/xoreos-docs/specs/torlack/key.html:154-168`](https://github.com/th3w1zard1/xoreos-docs/blob/master/specs/torlack/key.html#L154-L168) - Resource ID encoding
- [`vendor/reone/src/libs/resource/format/bifreader.cpp:50-54`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/bifreader.cpp#L50-L54) - Resource ID reading from BIF entries

---

## BZF [Compression](https://en.wikipedia.org/wiki/Data_compression)

*BZF* files are LZMA-compressed *BIF* files used primarily in iOS (and maybe Android) ports of *KotOR*. The *BZF* header contains `"BZF "` + `"V1.0"`, followed by LZMA-compressed *BIF* data. Decompression reveals a standard *BIF* structure.

### BZF format details

The *BZF* format wraps a complete *BIF* file in LZMA compression:

1. **BZF header** (8 bytes): `"BZF "` + `"V1.0"` signature
2. **LZMA Stream**: Compressed *BIF* file data using LZMA algorithm
3. **Decompressed Result**: Standard *BIF* file structure (as described above)

**compression Details:**

- The entire *BIF* file (after the 8-[byte](https://en.wikipedia.org/wiki/Byte) header) is compressed using LZMA (Lempel-Ziv-Markov chain Algorithm)
- LZMA provides high compression ratios with good decompression speed
- The compressed stream follows immediately after the BZF header
- Decompression yields a standard *BIF* file that can be read normally

**Benefits of BZF:**

- Significantly reduced file sizes (typically 40-60% compression ratio)
- Faster download times for mobile platforms
- Reduced storage requirements
- Identical resource access after decompression
- No performance penalty during gameplay (decompressed once at load time)

**Platform Usage:**

- PC releases use uncompressed *BIF* files for faster access
- Mobile releases (iOS/Android) use *BZF* for storage efficiency
- Modding tools can (and should) convert between *BIF* and *BZF* formats freely

**Implementation Notes:**

The *BZF* wrapper is completely transparent to the game engine - once decompressed in memory, the resource access patterns are identical to standard BIF files. Tools should decompress *BZF* files before reading resource entries, as the variable resource table offsets are relative to the decompressed BIF structure.

**References**

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py:45-52`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L45-L52) - *BZF* compression details

**Vendor Implementations:**

- [`vendor/xoreos/src/aurora/biffile.h:56-60`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.h#L56-L60) - *BZF* as compressed *BIF* (Android/iOS)
- [`vendor/reone/src/libs/resource/format/bifreader.cpp:27-30`](https://github.com/th3w1zard1/reone/blob/master/src/libs/resource/format/bifreader.cpp#L27-L30) - *BIF* signature detection

---

## [KEY](KEY-File-Format) File Relationship

*BIF* files require a [KEY file](KEY-File-Format) to map resource IDs to filenames (ResRefs). The [KEY file](KEY-File-Format) contains:

- *BIF* file entries (filename, size, location)
- [KEY](KEY-File-Format) entries mapping *ResRef* + *ResourceType* to *Resource ID*

The *Resource ID* in the *BIF* file matches the *Resource ID* in the [KEY File](KEY-File-Format)'s [KEY](KEY-File-Format) entries.

**References**

- See [KEY File Format](KEY-File-Format) for resource resolution and *BIF* indexing.

---

## Implementation Details

**Binary Reading**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py)

**Binary Writing**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py)

**BIF Class**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py:100-575`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L100-L575)

### See also

- [KEY-File-Format](KEY-File-Format) — *BIF* indexing and resource resolution
- [ERF-File-Format](ERF-File-Format) — *ERF/MOD* containers; [GFF-File-Format](GFF-File-Format) — *GFF* resources in *BIF*
- [RIM-File-Format](RIM-File-Format) — RIM (Resource Index Manifest) containers
- [Bioware-Aurora-KeyBIF](Bioware-Aurora-KeyBIF) — *Aurora* *KEY/BIF* specification

---

This documentation aims to provide a comprehensive overview of the *KotOR* *BIF* file format, focusing on the detailed file structure and data formats used within the games.
