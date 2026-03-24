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

BIF files work in tandem with [KEY files](KEY-File-Format) which provide the filename-to-resource mappings. BIF files contain only resource IDs, types, and data - the actual filenames ([ResRefs](GFF-File-Format#gff-data-types)) are stored in the [KEY file](KEY-File-Format). BIF files are [containers](ERF-File-Format) that store the bulk of game resources.

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

The [modular structure](https://en.wikipedia.org/wiki/Modular_programming) allows for efficient loading and potential platform-specific optimizations. Resources in BIF files are read-only at runtime; mods override them via the `override/` directory or custom [ERF](ERF-File-Format)/MOD files. The engine loads from BIF only when the resource is not found in [override](Concepts#override-folder), loaded MOD, or save (see [resource resolution order](Concepts#resource-resolution-order)); the [KEY file](KEY-File-Format) supplies the mapping from ResRef to the correct BIF and offset.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/bif/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — layout (header + variable entries + BZF note): [`bif_data.py` module docstring L1–L40](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L1-L40); `BIFType` / `BIFResource` / `BIF`: [`bif_data.py` L60–L569](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L60-L569); binary I/O: [`BIFBinaryReader`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L51-L180) (`load` L83–L89, signature L91–L109, header L111–L120, resource table L122–L155, payload L157–L179), [`BIFBinaryWriter`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L183-L256); raw LZMA helper for BZF: [`_decompress_bzf_payload` L20–L48](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L20-L48).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/seedhartha/reone)): [`bifreader.cpp` `BifReader::load` L27–L31](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L27-L31) (expects an 8-byte signature: `BIFFV1` plus one trailing ASCII space), [`loadHeader` L34–L41](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L34-L41), [`loadResources` L43–L50](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L43-L50), [`readResourceEntry` L52–L67](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L52-L67).
- **[xoreos](https://github.com/xoreos/xoreos)** / **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`biffile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp) — Aurora-family BIF (fixed vs variable resource handling, KEY merge helpers).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`BIFObject.ts` `readFromDisk` L84–L115](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/BIFObject.ts#L84-L115) — reads 20-byte header and 16-byte variable rows; [`getResourceBuffer` L164–L177](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/BIFObject.ts#L164-L177).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`BIFBinaryStructure.cs` `FileRoot` / `FileHeader` / `VariableResource` L16–L65](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L16-L65) — header skips the fixed-resource `uint32` with `BaseStream.Position += 4` before reading `OffsetToResources` (same on-disk layout as PyKotor/reone).
- **[bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats)** — Kaitai Struct specs for BIF and related BioWare containers.

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

**Note on header Variations**: [xoreos-docs Torlack `bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html) shows the field at offset `0x000C` as “Unknown value” rather than “Fixed Resource count”. In *KotOR* it is always `0`; PyKotor **rejects** `fixed_res_count > 0` ([`io_bif.py` L117–L120](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L117-L120)).

**References:** [xoreos `biffile.cpp` L64–L67](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L64-L67) (fixed count must be 0); [reone `loadHeader` L34–L41](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L34-L41); [Kotor.NET `FileHeader` L35–L47](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L35-L47); [Torlack `bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html).

### Variable Resource Table

Each variable resource entry is 16 bytes:

| Name        | type   | offset | size | Description                                                      |
| ----------- | ------ | ------ | ---- | ---------------------------------------------------------------- |
| Resource ID | `UInt32` | 0 (0x00) | 4    | Resource ID (matches [KEY file](KEY-File-Format) entry, encodes BIF index and resource index) |
| Offset      | `UInt32` | 4 (0x04) | 4    | Offset to resource data in file (absolute file offset)                    |
| File Size   | `UInt32` | 8 (0x08) | 4    | Uncompressed size of resource data (bytes)                                 |
| Resource type | `UInt32` | 12 (0x0C) | 4    | Resource type identifier (hex IDs and labels: [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers); PyKotor: `ResourceType` enum)                          |

**Entry Reading Order:**

Entries are read sequentially from the variable resource table. The table is located at the offset specified in the file header. Each entry is exactly 16 bytes, allowing efficient sequential reading.

**References:** [reone `readResourceEntry` L52–L67](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L52-L67); [Kotor.NET `VariableResource` L49–L64](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs#L49-L64); [xoreos `biffile.cpp` L84–L96](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L84-L96); PyKotor table loop [`io_bif.py` L122–L141](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L122-L141).

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
- [reone `loadResources` L43–L50](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L43-L50) — resource table load
- [`vendor/xoreos/src/aurora/biffile.cpp:99-123`](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.cpp#L99-L123) - mergeKEY process combining KEY and BIF
- [xoreos-docs Torlack `bif.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/bif.html) — resource row semantics (ID, offset, length, type)

**Resource IDs:**

The *Resource ID* in the *BIF* file's *variable resource table* must match the *Resource ID* stored in the [KEY file](KEY-File-Format). The *Resource ID* is a 32-bit value that encodes two pieces of information:

- **Lower 20 bits (bits 0-19)**: Resource index within the *BIF* file (0-based index into the variable resource table)
- **Upper 12 bits (bits 20-31)**: BIF index in the [KEY file](KEY-File-Format)'s *BIF* table (identifies which *BIF* file contains this resource)

**Example:** A *Resource ID* of `0x00400029` decodes as:

- Resource index: `0x29` (41st resource in the *BIF*)
- BIF index: `0x004` (4th *BIF* file in the [KEY](KEY-File-Format)'s *BIF* table)

**References:** [KEY File Format](KEY-File-Format#resource-id-encoding); [Torlack `key.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/key.html) (worked examples); [reone `readResourceEntry` L54–L56](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L54-L56) (reads `id` field from each 16-byte row).

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

**References:** PyKotor documents the BZF wrapper in [`bif_data.py` L35–L39](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L35-L39); decompression path [`io_bif.py` L162–L169](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L162-L169) + [`_decompress_bzf_payload` L20–L48](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L20-L48). **Version string:** `BIFBinaryReader` accepts the second 4-byte field as either `V1` plus two trailing ASCII spaces (the usual `"V1  "` layout) or `V1.1` in the 8-byte signature for **both** BIF and BZF ([`io_bif.py` L107–L109](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py#L107-L109)); some distributions describe mobile BZF as `V1.0` in prose—verify against real headers if a file fails to load. [xoreos `biffile.h` L56–L60](https://github.com/xoreos/xoreos/blob/master/src/aurora/biffile.h#L56-L60); [reone `BifReader::load` L27–L31](https://github.com/modawan/reone/blob/master/src/libs/resource/format/bifreader.cpp#L27-L31).

---

## [KEY](KEY-File-Format) File Relationship

*BIF* files require a [KEY file](KEY-File-Format) to map resource IDs to filenames (ResRefs). The [KEY file](KEY-File-Format) contains:

- *BIF* file entries (filename, size, location)
- [KEY](KEY-File-Format) entries mapping *ResRef* + *ResourceType* (see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)) to *Resource ID*

The *Resource ID* in the *BIF* file matches the *Resource ID* in the [KEY File](KEY-File-Format)'s [KEY](KEY-File-Format) entries.

**References**

- See [KEY File Format](KEY-File-Format) for resource resolution and *BIF* indexing.

---

## Implementation Details

**Binary Reading**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py)

**Binary Writing**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/io_bif.py)

**BIF Class**: [`Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py:100-575`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/bif/bif_data.py#L100-L575)

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution#resource-type-identifiers) -- Hex resource type IDs
- [KEY-File-Format](KEY-File-Format) -- *BIF* indexing and resource resolution
- [ERF-File-Format](ERF-File-Format) -- *ERF/MOD* containers; [GFF-File-Format](GFF-File-Format) -- *GFF* resources in *BIF*
- [RIM File Format](RIM-File-Format) — Resource image module archives ([contrast with ERF](ERF-File-Format#rim-versus-erf))
- [Bioware-Aurora-KeyBIF](Bioware-Aurora-KeyBIF) -- *Aurora* *KEY/BIF* specification

---

This documentation aims to provide a comprehensive overview of the *KotOR* *BIF* file format, focusing on the detailed file structure and data formats used within the games.
