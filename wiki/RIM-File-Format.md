# KotOR RIM file format

This document describes the **RIM** (**resource image**) container used in *Knights of the Old Republic* and *The Sith Lords*. RIM files ship with the game under `modules/` (and related paths) and hold the same kinds of resources as [ERF/MOD](ERF-File-Format) archives—[GFF](GFF-File-Format), [2DA](2DA-File-Format), [TPC](TPC-File-Format), [NCS](NCS-File-Format), models, walkmeshes, and so on—but use a **smaller, simpler binary layout** than [ERF](ERF-File-Format).

## Table of contents

- [Role in the game and modding](#role-in-the-game-and-modding)
- [File structure overview](#file-structure-overview)
- [Binary format](#binary-format)
  - [File header](#file-header)
  - [Resource entries](#resource-entries)
  - [Resource data and padding](#resource-data-and-padding)
- [Module file sets (rim, _s, dlg)](#module-file-sets-rim-_s-dlg)
- [Relationship to ERF and MOD](#relationship-to-erf-and-mod)
- [Implementation details](#implementation-details)

---

## Role in the game and modding

Vanilla modules are usually split across one or more `.rim` files (for example a main archive and a `_s` supplementary archive). The engine resolves resources using the same high-level rules as for MOD/ERF: module-scoped containers participate in the pipeline described in [resource resolution order](Concepts#resource-resolution-order). A `module_name.mod` file in `modules/` typically **shadows** the corresponding `.rim` pair when present; see [Concepts](Concepts#mod-erf-rim) and [Holocron Toolset module resources](Holocron-Toolset-Module-Resources).

RIM is appropriate to read and edit when you are working directly with shipped module archives or building tools that must round-trip vanilla layout. Many modders ship changes as `.mod` ([ERF](ERF-File-Format) variant) instead so the game loads a single encapsulated file without replacing base RIMs.

---

## File structure overview

A RIM file is a **self-contained** archive: each stored resource has a [ResRef](GFF-File-Format#gff-data-types), a **resource type** id, and raw **payload bytes**. There is **no** separate [KEY](KEY-File-Format) file and **no** localized description block like ERF’s optional string list.

At a high level:

1. Fixed **120-byte** header (`RIM` + `V1.0` + counts and offsets).
2. **Resource table**: one **32-byte** record per resource (ResRef, type, index, offset, size).
3. **Resource blobs** concatenated after the table, with alignment and trailing padding as used by vanilla-style writers.

Unlike [ERF](ERF-File-Format), RIM does **not** split “key” and “resource list” into two parallel arrays of different record sizes: **offset and size live in the same 32-byte entry** as the name and type.

---

## Binary format

Offsets are from the **start of the file** unless noted.

### File header

The header is **120 bytes**.

| Name | Type | Offset | Size | Description |
| ---- | ---- | ------ | ---- | ----------- |
| File type | char[4] | 0 | 4 | Always `RIM` (space-padded fourCC). |
| File version | char[4] | 4 | 4 | Always `V1.0`. |
| Unknown | UInt32 | 8 | 4 | Observed as `0` in vanilla-style files; treat as reserved. |
| Entry count | UInt32 | 12 | 4 | Number of resources in the archive. |
| Offset to resource table | UInt32 | 16 | 4 | Byte offset to the first resource entry. If **0**, tools treat this as **120** (table immediately after the header). |
| Offset to resources / reserved | UInt32 | 20 | 4 | PyKotor’s writer records **`0` here** (“implicit” layout: data follows the table and alignment padding). Older descriptions sometimes treat parts of the tail of the header as opaque padding; readers should not depend on undocumented flags without verification. |
| Reserved | byte[] | 24 | 96 | Padding (typically zeros) to complete 120 bytes. |

**Implicit offset:** If the offset at **0x10** is `0`, compliant readers assume the resource table starts at byte **120**.

### Resource entries

Each entry is **32 bytes**. Field order matches the reader in PyKotor’s `RIMBinaryReader` (ResRef, then **type**, then **id**, then offset, then size).

| Name | Type | Offset | Size | Description |
| ---- | ---- | ------ | ---- | ----------- |
| ResRef | char[16] | 0 | 16 | Resource name, null-padded to 16 bytes; not necessarily null-terminated if length is 16. |
| Resource type | UInt32 | 16 | 4 | Numeric resource type id (same family of ids as elsewhere in KotOR; see [Resource Type Identifiers](Resource-Formats-and-Resolution#resource-type-identifiers)). |
| Resource id | UInt32 | 20 | 4 | Index or slot id; vanilla writers typically use **0 .. n−1** in order. |
| Offset to data | UInt32 | 24 | 4 | File offset to the first byte of this resource’s payload. |
| Resource size | UInt32 | 28 | 4 | Length of the payload in bytes. |

**Contrast with ERF:** In [ERF](ERF-File-Format), the parallel “key” record uses a **UInt16** resource type plus **2 bytes** padding, and **offsets/sizes** live in a **separate** 8-byte-per-entry resource list. RIM folds metadata and locating information into this single 32-byte record.

### Resource data and padding

Payloads are stored at the offsets given in the table. PyKotor’s `RIMBinaryWriter` reproduces a **vanilla-style** layout:

- After the last resource entry, the writer may insert **padding** so the start of the first blob aligns to a **16-byte** boundary.
- After each resource’s bytes, the writer appends **0–3** padding bytes so the stream is **4-byte aligned**, then writes **16** additional **zero** bytes before the next resource (including after the last resource, so the on-disk file size reflects that trailing region).

Other tools may emit slightly different padding; parsers should trust **only** the offset/size fields in the table for the extent of each resource.

---

## Module file sets (rim, _s, dlg)

A single logical module often spans **multiple** archives:

| Pattern | Typical role |
| ------- | ------------ |
| `module.rim` | Main module payload (areas, templates, scripts, textures, etc.). |
| `module_s.rim` | **S**upplementary resources for the same module (split for size or organization). |
| `module_dlg.erf` | (TSL especially) Dialog and related resources in a separate [ERF](ERF-File-Format) capsule. |

Exact splits vary by module. Kit and extraction tooling that scans `modules/` treats `.mod` as highest priority, then `.rim` / `_s.rim`, then other ERFs; see [Kit structure documentation](Kit-Structure-Documentation).

---

## Relationship to ERF and MOD

RIM and ERF solve the same problem—**named, typed resources in one file**—but they are **not** bit-identical layouts.

| Topic | RIM | ERF / MOD / SAV / HAK |
| ----- | --- | --------------------- |
| Header size | **120** bytes | **160** bytes |
| File type tag | `RIM` | `ERF`, `MOD`, `SAV`, `HAK` |
| Localized description strings | **No** | Optional block (language id + CP1252 text) |
| Build year/day, description StrRef | **No** | Present in ERF header |
| Per-resource metadata | One **32-byte** entry (includes offset + size) | **24-byte** key + **8-byte** resource entry |
| Resource type in entry | **UInt32** | **UInt16** + 2 unused bytes |
| MOD “blank block” quirk | **No** | Documented between key list and resource list for MOD/NWM in [ERF File Format](ERF-File-Format) |

For a side-by-side narrative aimed at ERF readers, see [RIM versus ERF](ERF-File-Format#rim-versus-erf) on the ERF page.

**Conversion:** PyKotor exposes `RIM.to_erf()` to build an in-memory [ERF](ERF-File-Format) with the same resources, which can then be serialized as MOD/ERF for tools that only speak the ERF layout.

---

## Implementation details

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — on-disk layout (120-byte header, 32-byte keys): [`rim_data.py` module docstring L1–L45](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/rim_data.py#L1-L45); `RIMResource` / `RIM`: [`rim_data.py` L59–L173](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/rim_data.py#L59-L173); Kaitai load: [`io_rim.py` `_load_rim_from_kaitai` L22–L35](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L22-L35); legacy reader (implicit table offset **120**, row order **ResRef, UInt32 type, id, offset, size**): [`_load_rim_legacy` L38–L61](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L38-L61), [`_read_rim_entries` L64–L88](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L64-L88); `RIMBinaryReader.load` L120–L127; vanilla-style writer: [`RIMBinaryWriter.write` L142–L198](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/rim/io_rim.py#L142-L198).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`RIMBinaryStructure.cs` `FileRoot` / `FileHeader` / `ResourceEntry` L16–L116](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorRIM/RIMBinaryStructure.cs#L16-L116) — reads the **20-byte** logical header then seeks `OffsetToResources` (vanilla **120**).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)): [`rimreader.cpp` `RimReader::load` L27–L35](https://github.com/modawan/reone/blob/master/src/libs/resource/format/rimreader.cpp#L27-L35), [`readResource` L47–L58](https://github.com/modawan/reone/blob/master/src/libs/resource/format/rimreader.cpp#L47-L58) — **`UInt16` type** plus **`skipBytes(6)`**; **not** the same 32-byte KotOR row as PyKotor/Kotor.NET.
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`RIMObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/RIMObject.ts) — uses **`UInt16` + `UInt16`** after ResRef, **`RIM_HEADER_LENGTH = 160`** ([L9](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/RIMObject.ts#L9)), and **`34` bytes × row count** for `rimDataOffset` ([L84–L95](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/RIMObject.ts#L84-L95)); retail **KotOR** RIMs follow **120** / **32** as on this page.

Community tools and installers (TSLPatcher, HoloPatcher) support inserting or patching files inside RIM capsules as well as ERF/MOD; see [TSLPatcher’s official readme](TSLPatcher's-Official-Readme) and [HoloPatcher internal logic](Explanations-on-HoloPatcher-Internal-Logic).

This page summarizes the KotOR **RIM** container for modders and implementers. For ERF-specific fields and engine behavior around MOD/SAV, use [ERF File Format](ERF-File-Format).

### See also

- [ERF File Format](ERF-File-Format) — Encapsulated resource format (MOD, SAV, HAK, generic ERF) and [RIM versus ERF](ERF-File-Format#rim-versus-erf)
- [Concepts](Concepts) — Resource resolution, override, MOD versus RIM priority
- [KEY File Format](KEY-File-Format) — Index format for BIF storage (contrast with self-contained RIM)
- [BIF File Format](BIF-File-Format) — Vanilla bulk storage with KEY
- [Holocron Toolset module resources](Holocron-Toolset-Module-Resources) — Practical module/RIM editing notes
