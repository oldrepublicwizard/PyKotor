# KotOR SSF file format Documentation

This document provides a detailed description of the SSF (sound set files) file format used in Knights of the Old Republic (KotOR) games. SSF files contain mappings from sound event types to string references ([StrRefs](TLK-File-Format#string-references-strref)) in the [TLK file](TLK-File-Format).

**For mod developers:** To modify SSF files in your mods, see the [TSLPatcher SSFList Syntax Guide](TSLPatcher-SSFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** SSF files reference [TLK files](TLK-File-Format) for string references ([StrRefs](TLK-File-Format#string-references-strref)) that point to the actual sound text strings.

## Table of Contents

- KotOR SSF File Format Documentation
  - Table of Contents
  - [File structure overview](#file-structure-overview)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [Sound Table](#sound-table)
  - [Sound event types](#sound-event-types)
  - [Implementation Details](#implementation-details)

---



## File structure overview

SSF files define **28** logical sound slots (indices `0`–`27`) that creatures use for battle cries, selection lines, grunts, UI feedback, etc. Each slot holds a [StrRef](TLK-File-Format#string-references-strref) into [`dialog.tlk`](TLK-File-Format) (or `-1` / `0xFFFFFFFF` for “no sound”). SSF files load through the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**On-disk size:** The header is **12** bytes; the **semantic** KotOR table is **28** × 4 = **112** bytes. Some writers emit **40** × 4 = **160** bytes after the header (28 mapped slots plus **12** extra `0xFFFFFFFF` words). PyKotor’s writer does this ([`io_ssf.py` L177–L181](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L177-L181)); Kotor.NET models a 40-entry table in [`SSFBinaryStructure.cs` `SoundTable` L61–L77](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorSSF/SSFBinaryStructure.cs#L61-L77). Readers that only consume the first 28 entries after `offset` still match vanilla behavior; KotOR.js [`SSFObject.Open`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/SSFObject.ts#L31-L49) derives `soundCount = (length - 12) / 4` and therefore accepts either width.

**Implementation (PyKotor):** [`Libraries/PyKotor/src/pykotor/resource/formats/ssf/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — format notes in module docstring: [`io_ssf.py` L1–L42](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L1-L42); legacy load path (28 slots, order fixed): [`_load_ssf_legacy` L63–L112](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L63-L112); reader dispatch: [`SSFBinaryReader.load` L152–L159](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L152-L159); writer: [`SSFBinaryWriter.write` L171–L181](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L171-L181); enum + semantics: [`SSFSound` L123–L234](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234).
- **[reone](https://github.com/modawan/reone)** — [`ssfreader.cpp` `SsfReader::load` L28–L36](https://github.com/modawan/reone/blob/master/src/libs/resource/format/ssfreader.cpp#L28-L36) (validates `SSF V1.1`, seeks to table offset, reads **all** remaining `int32`s into an array — works for 28- or 40-word tables).
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora SSF (`src/aurora/ssffile.cpp`), shared with other Aurora titles.
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — [`SSFObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/SSFObject.ts#L31-L49); slot names: [`SSFType` enum L14–L43](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/resource/SSFType.ts#L14-L43) (same indices as PyKotor `SSFSound`; identifier spellings differ slightly — see table below).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — header + 40-slot table: [`SSFBinaryStructure.cs` L29–L77](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorSSF/SSFBinaryStructure.cs#L29-L77); high-level read loop (28 creature sounds): [`SSFBinaryReader.Read` L31–L45](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorSSF/SSFBinaryReader.cs#L31-L45).

### See also

- [TSLPatcher SSFList Syntax](TSLPatcher-SSFList-Syntax) - Modding SSF files with TSLPatcher
- [TLK File Format](TLK-File-Format) - [Talk Table](TLK-File-Format) containing actual sound references
- [Bioware Aurora SSF Format](Bioware-Aurora-SSF) - Official BioWare specification
- [GFF-UTC](GFF-UTC) - [creature templates](GFF-File-Format#utc-creature) that reference SSF files
- [2DA-soundset](2DA-soundset) - Sound set definitions table

---

## Binary format

### File Header

The file header is 12 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type           | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | Always `"SSF "` (space-padded)                 |
| file Version        | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | Always `"V1.1"`                                 |
| offset to Sound Table | UInt32 | 8 (0x08) | 4    | Byte offset to the first StrRef (almost always **12**)          |

### Sound Table

After the header, the file contains a contiguous array of **little-endian int32** StrRefs. **KotOR uses the first 28 entries** (indices `0`–`27`) as in the **Sound event types** table below. `-1` or `0xFFFFFFFF` means “no sound” for that slot.

Some files and tools use **40** uint32 entries (extra trailing `-1` words). Treat anything beyond index **27** as padding unless you have a specific toolchain that assigns meaning to it.

---

## Sound event types

Indices are fixed; **do not reorder**. PyKotor names are authoritative for this repo; [KotOR.js `SSFType`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/resource/SSFType.ts#L14-L43) uses the same numeric values with different spellings on a few rows (noted in the third column).

| Index | PyKotor `SSFSound` | KotOR.js `SSFType` (if different) | Role |
| ----- | ------------------ | ----------------------------------- | ---- |
| 0–5 | `BATTLE_CRY_1` … `BATTLE_CRY_6` | (same) | Combat entry / battle cries |
| 6–8 | `SELECT_1` … `SELECT_3` | (same) | Creature selected |
| 9–11 | `ATTACK_GRUNT_1` … `ATTACK_GRUNT_3` | `ATTACK_1` … `ATTACK_3` | Attack animation grunts |
| 12–13 | `PAIN_GRUNT_1` … `PAIN_GRUNT_2` | `PAIN_1` … `PAIN_2` | Damage reactions |
| 14 | `LOW_HEALTH` | (same) | Low HP warning |
| 15 | `DEAD` | (same) | Death |
| 16 | `CRITICAL_HIT` | (same) | Critical hit feedback |
| 17 | `TARGET_IMMUNE` | (same) | Immune target |
| 18 | `LAY_MINE` | (same) | Place mine |
| 19 | `DISARM_MINE` | (same) | Disarm mine |
| 20 | `BEGIN_STEALTH` | `STEALTH` | Enter stealth |
| 21 | `BEGIN_SEARCH` | `SEARCH` | Search mode |
| 22 | `BEGIN_UNLOCK` | `UNLOCK` | Start unlock |
| 23 | `UNLOCK_FAILED` | `UNLOCK_FAIL` | Unlock failed |
| 24 | `UNLOCK_SUCCESS` | (same) | Unlock succeeded |
| 25 | `SEPARATED_FROM_PARTY` | `SOLO_MODE` | Left party / solo |
| 26 | `REJOINED_PARTY` | `PARTY_MODE` | Rejoined party |
| 27 | `POISONED` | (same) | Poisoned |

**Primary references:** [`ssf_data.py` `SSFSound` L123–L234](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234), [`io_ssf.py` `_load_ssf_legacy` L80–L110](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py#L80-L110), [KotOR.js `SSFType.ts` L14–L43](https://github.com/KobaltBlu/KotOR.js/blob/master/src/enums/resource/SSFType.ts#L14-L43).

---

## Implementation Details

| Component | Location |
| --------- | -------- |
| SSF data model | [`ssf_data.py` `SSF` L26–L121](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L26-L121), [`SSFSound` L123–L234](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/ssf_data.py#L123-L234) |
| Binary I/O | [`io_ssf.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ssf/io_ssf.py) (see [File structure overview](#file-structure-overview) for line-level anchors) |

---

This documentation aims to provide a comprehensive overview of the KotOR SSF file format, focusing on the detailed file structure and data formats used within the games.
