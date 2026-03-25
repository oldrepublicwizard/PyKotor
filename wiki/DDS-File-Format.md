# KotOR DDS file format Documentation

*DirectDraw Surface* (DDS) [textures](TPC-File-Format) appear in two flavours across Odyssey engine content:

- **Standard DirectX DDS** (header magic `0x44445320`, 124-byte header) used by downstream tools/ports.
- **BioWare DDS variant** (no magic; width/height/bpp/dataSize leading integers) used in *KotOR* and *Neverwinter Nights* game assets (shared Aurora engine format).

This page documents how PyKotor interprets both formats and how it aligns with reference implementations in [xoreos](https://github.com/xoreos/xoreos) and [xoreos-tools](https://github.com/xoreos/xoreos-tools). When the engine or tools load DDS by ResRef, they use the same [resource resolution order](Concepts#resource-resolution-order) as other resources ([override](Concepts#override-folder), [MOD/ERF/SAV](ERF-File-Format), [KEY/BIF](KEY-File-Format)). Hex type id **`0x07F1`** is listed under [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers).

## Table of Contents

- KotOR DDS file format Documentation
  - Table of Contents
  - [Standard DDS (DX7+ container)](#standard-dds-dx7-container)
  - [BioWare DDS variant](#bioware-dds-variant)
  - [Writer Behaviour (PyKotor)](#writer-behaviour-pykotor)
  - [Detection and Routing](#detection-and-routing)
  - [Testing coverage](#testing-coverage)
  - [Practical differences vs. TGA/TPC](#practical-differences-vs-tgatpc)
  - [Notes and limits](#notes-and-limits)
  - [See also](#see-also)

---

**Implementation (PyKotor)**

- **Reader / writer:** [`io_dds.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py) — [`TPCDDSReader` L49+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L49), [`load` L191+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L191), [`TPCDDSWriter` L351+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py#L351); routing via [`tpc_auto.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/tpc_auto.py) (`ResourceType.DDS` detection).

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **[xoreos](https://github.com/xoreos/xoreos)** ([tools mirror: xoreos-tools](https://github.com/xoreos/xoreos-tools)): [`src/graphics/images/dds.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/images/dds.cpp) — engine DDS loading (standard and BioWare variant).
- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`src/images/dds.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/images/dds.cpp) — command-line DDS conversion.
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)) — no standalone DDS reader in-tree; the game pipeline loads **TPC** via [`TpcReader::load` L32+](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/tpcreader.cpp#L32). Use PyKotor or xoreos-tools to convert DDS for KotOR-style assets.
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — runtime textures follow the **TPC** path ([`TPCObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TPCObject.ts), [`TextureLoader.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/loaders/TextureLoader.ts)); see [TPC File Format](TPC-File-Format) for JS anchors. DDS remains an interchange format for tools, not the on-disk KotOR default.
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — managed **TPC** under [`Kotor.NET/Formats/KotorTPC/`](https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats/KotorTPC); no separate `KotorDDS` project on the default branch—treat DDS like other tool-chain inputs mapped into TPC in PyKotor.

**For mod developers:** DDS is an alternative texture format; *KotOR* typically uses [TPC](TPC-File-Format). See [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** DDS is read/written via PyKotor's [TPC](TPC-File-Format) pipeline; see [TPC File Format](TPC-File-Format) and [TXI File Format](TXI-File-Format).

### Standard DDS (DX7+ container)

- Magic: `DDS` followed by a 124-[byte](https://en.wikipedia.org/wiki/Byte) header.
- Important header fields:
  - `dwFlags` bit `0x00020000` signals mipmap count; otherwise one mipmap is assumed.
  - `dwHeight`, `dwWidth` validated up to 0x8000.
  - `DDPIXELFORMAT` describes layout:
    - FourCC `DXT1` --> TPC `DXT1`
    - FourCC `DXT3` --> TPC `DXT3`
    - FourCC `DXT5` --> TPC `DXT5`
    - Uncompressed 32-bit BGRA masks (`00FF0000/0000FF00/000000FF/FF000000`) --> TPC `BGRA`
    - Uncompressed 24-bit BGR masks (`00FF0000/0000FF00/000000FF`) --> TPC `BGR`
    - 16-bit ARGB 1-5-5-5 (`7C00/03E0/001F/8000`) --> converted to RGBA
    - 16-bit ARGB 4-4-4-4 (`0F00/00F0/000F/F000`) --> converted to RGBA
    - 16-bit RGB 5-6-5 (`F800/07E0/001F/0`) --> converted to RGB
  - Cubemap detection via `dwCaps2 & 0x00000200`; faces counted from `dwCaps2 & 0x0000FC00`.
- Each mip size is computed with the format-aware block sizing from `TPCTextureFormat.get_size`.
- data layouts that are not directly usable (4444, 1555, 565) are expanded into RGBA/RGB before storing in the `TPC` object.

Implementation reference:

- **PyKotor** — [`io_dds.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py) (standard DDS path and format mapping)
- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/graphics/images/dds.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/images/dds.cpp) and **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`src/images/dds.cpp`](https://github.com/xoreos/xoreos-tools/blob/master/src/images/dds.cpp) (baseline behaviour and [mask](GFF-File-Format#gff-data-types) checks)

### BioWare DDS variant

| Field           | Type                | Description                                                                                   |
|-----------------|---------------------|-----------------------------------------------------------------------------------------------|
| width           | UInt32 (LE)         | Image width, must be a power of two and less than 0x8000                                      |
| height          | UInt32 (LE)         | Image height, must be a power of two and less than 0x8000                                     |
| bytesPerPixel   | UInt32 (LE)         | Pixel format: `3` = DXT1, `4` = DXT5                                                          |
| dataSize        | UInt32 (LE)         | Size in bytes; must be `(width*height)/2` for DXT1, or `width*height` for DXT5                |
| unused float    | Float32 (LE)        | Ignored (unused float value follows header)                                                   |
| payload         | Byte array          | Compressed texture data, may include multiple mipmaps until all data consumed                 |
| mipmap count    | Inferred            | Determined by computing expected mip sizes until reading all data                             |
| palette/layout  | n/a                 | Always compressed; no palettes or alternative pixel layouts supported                         |

**Notes:**

- No file magic is present in this format.
- Payload is always compressed data (DXT1 or DXT5); there is no support for palettes or uncompressed formats.

**Implementation Reference:**

- **PyKotor** — [`io_dds.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tpc/io_dds.py) (BioWare header path)
- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/graphics/images/dds.cpp`](https://github.com/xoreos/xoreos/blob/master/src/graphics/images/dds.cpp) (BioWare branch for comparison).

### Writer Behaviour (PyKotor)

- `TPCDDSWriter` emits only standard DDS headers:
  - Supports *DXT1*, *DXT3*, *DXT5*, and uncompressed *BGR/BGRA*.
  - Non-DDS-friendly formats are converted (*RGB*→*BGR*, *RGBA*→*BGRA*).
  - Mipmap counts validated per layer; cubemaps set caps (*DDSCAPS2_CUBEMAP*|*ALLFACES*).
- Payloads are written in the already-compressed/uncompressed form stored in the [*TPC*](TPC-File-Format) instance; no re-compression occurs.

### Detection and Routing

- `detect_tpc()` now returns `ResourceType.DDS` when:
  - File extension is `.dds`, or
  - Magic `DDS` is present, or
  - BioWare header heuristics match width/height/bpp/dataSize.
- `read_tpc()` dispatches to `TPCDDSReader` when `ResourceType.DDS` is detected.
- `write_tpc(..., ResourceType.DDS)` routes to `TPCDDSWriter`.

### Testing coverage

- [`Libraries/PyKotor/tests/resource/formats/test_dds.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/tests/resource/formats/test_dds.py)
  - Standard DDS *DXT1* load/write roundtrip
  - *BioWare* DDS multi-mip parsing
  - Uncompressed *BGRA* header parsing
  - Writer roundtrip for *DXT1* payloads

### Practical differences vs. TGA/TPC

- **TGA**: uncompressed/RLE raster data; no block compression; single [face](MDL-MDX-File-Format#face-structure) only; origin/alpha flags live in the header. DDS can be block-compressed (*DXT1/DXT5*) and include cubemap [faces](MDL-MDX-File-Format#face-structure)/mip hierarchies in one container.
- **TPC**: *KotOR*-specific container with [TXI](TXI-File-Format) embedded and different header layout; PyKotor maps DDS surfaces into [*TPC*](TPC-File-Format) objects for unified downstream handling (conversion, [TXI](TXI-File-Format) logic, cubemap normalization).

### Notes and limits

- Palette-based DDS (*DDPF_INDEXED*) is rejected.
- Dimensions beyond 0x8000 are rejected, matching xoreos limits.
- *BioWare* DDS may require **power-of-two** sizes; standard DDS does not enforce power-of-two beyond the existing dimension guard.

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution) - [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers) (`DDS` / `0x07F1`)
- [TPC File Format](TPC-File-Format) - *KotOR*'s primary texture format; PyKotor maps DDS into [*TPC*](TPC-File-Format).
- [TXI File Format](TXI-File-Format) - Texture metadata used with [*TPC*](TPC-File-Format).
- [KEY File Format](KEY-File-Format) - Resource resolution order for DDS by [ResRef](Concepts#resref-resource-reference).
