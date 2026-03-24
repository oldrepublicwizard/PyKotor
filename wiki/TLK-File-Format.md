# KotOR TLK file format Documentation

This document provides a detailed description of the TLK (Talk Table) file format used in Knights of the Old Republic (KotOR) games. TLK files contain all text strings used in the game, both written and spoken, enabling easy localization by providing a lookup table from string reference numbers ([StrRef](TLK-File-Format#string-references-strref)) to localized text and associated voice-over audio files.

**For mod developers:** To modify TLK files in your mods, see the [TSLPatcher TLKList Syntax Guide](TSLPatcher-TLKList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** TLK files are referenced by [GFF files](GFF-File-Format) (especially [DLG](GFF-File-Format#dlg-dialogue) [dialogue files](GFF-File-Format#dlg-dialogue)), [2DA files](2DA-File-Format) for item names and descriptions, and [SSF files](SSF-File-Format) for character sound sets.

## Table of Contents

- KotOR TLK File Format Documentation
  - [File Structure Overview](#file-structure-overview)
  - [Binary Format](#binary-format)
    - [File Header](#file-header)
    - [String Data Table](#string-data-table)
    - [String Entries](#string-entries)
  - [TLKEntry Structure](#tlkentry-structure)
  - [String References (StrRef)](#string-references-strref)
    - [Custom TLK Files](#custom-tlk-files)
  - [Localization](#localization)
  - [Implementation Details](#implementation-details)

---

## File structure overview

TLK files store localized strings in a binary format. The game loads `dialog.tlk` at startup and references strings throughout the game using [StrRef](TLK-File-Format#string-references-strref) numbers (array indices). String lookups use the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, then module/SAV, then KEY/BIF), so custom TLKs in override or in a MOD take precedence over the base game `dialog.tlk`.

**Implementation:** [`Libraries/PyKotor/src/pykotor/resource/formats/tlk/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/)

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — binary layout in module docstring: [`tlk_data.py` L1–L39](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L39); `TLK` / `TLKEntry`: [`tlk_data.py` L54–L282](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L282), [`L285–L420`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L285-L420); read path (Kaitai + legacy 40-byte rows): [`io_tlk.py` `_load_tlk_from_kaitai` L32–L63](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L32-L63), [`_load_tlk_legacy` L66–L120](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L66-L120), [`TLKBinaryReader.load` L149–L156](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L149-L156); write path: [`TLKBinaryWriter` L168–L219](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L168-L219) (`_write_file_header` L183–L192, `_write_entry` L194–L219).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/seedhartha/reone)): [`tlkreader.cpp` `TlkReader::load` L34–L43](https://github.com/modawan/reone/blob/master/src/libs/resource/format/tlkreader.cpp#L34-L43) (8-byte `"TLK V3.0"` signature + language/count/offset), [`loadStrings` L45–L71](https://github.com/modawan/reone/blob/master/src/libs/resource/format/tlkreader.cpp#L45-L71) (40-byte rows, **lowercases** sound ResRef); flag constants L28–L32.
- **[xoreos](https://github.com/xoreos/xoreos)** / **[xoreos-tools](https://github.com/xoreos/xoreos-tools)**: [`talktable.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/talktable.cpp) — Aurora talk table (shared with other Aurora titles).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`TLKObject.ts` `LoadFromBuffer` L51–L96](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TLKObject.ts#L51-L96) — 20-byte header then per-entry metadata; note the last field before text is read with `readUInt32()` while the on-disk field is a **float** sound length—compare PyKotor [`struct.unpack("<f", ...)` L106](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L106).
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)**: [`TLKObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/TLKObject.cs).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`TLKBinaryStructure.cs` `FileHeader` / `StringData` / `FileRoot` L16–L130](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L16-L130).

### See also

- [2DA File Format](2DA-File-Format) - Game tables with name/description StrRefs
- [GFF File Format](GFF-File-Format) - Dialogue and templates that reference TLK strings
- [SSF File Format](SSF-File-Format) - Sound sets that reference TLK entries
- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax) - Modding TLK files with TSLPatcher

---

## Binary format

### File Header

The file header is 20 bytes in size:

| Name                | type    | offset | size | Description                                    |
| ------------------- | ------- | ------ | ---- | ---------------------------------------------- |
| file type           | [char](GFF-File-Format#gff-data-types) | 0 (0x00) | 4    | Always `"TLK "` (space-padded)                  |
| file Version        | [char](GFF-File-Format#gff-data-types) | 4 (0x04) | 4    | `"V3.0"` for KotOR, `"V4.0"` for Jade Empire  |
| Language ID         | [int32](GFF-File-Format#gff-data-types)   | 8 (0x08) | 4    | Language identifier (see [Concepts](Concepts#language-ids-kotor); [TLK-specific notes](#localization)) |
| string count        | [int32](GFF-File-Format#gff-data-types)   | 12 (0x0C) | 4    | Number of string entries in the file           |
| string Entries offset | [int32](GFF-File-Format#gff-data-types) | 16 (0x10) | 4    | offset to string entries array (typically 20)  |

**References:** [reone `TlkReader::load` L34–L43](https://github.com/modawan/reone/blob/master/src/libs/resource/format/tlkreader.cpp#L34-L43); PyKotor header parse [`_load_tlk_legacy` L71–L75](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L71-L75) / Kaitai path [`_load_tlk_from_kaitai` L35–L44](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L35-L44); [Kotor.NET `FileHeader` L66–L76](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L66-L76); [KotOR.js `LoadFromBuffer` L59–L64](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TLKObject.ts#L59-L64).

### String data table

The string data table contains metadata for each string entry. Each entry is 40 bytes:

| Name              | type      | offset | size | Description                                                      |
| ----------------- | --------- | ------ | ---- | ---------------------------------------------------------------- |
| flags             | UInt32    | 0 (0x00) | 4    | bit flags: bit 0=text present, bit 1=sound present, bit 2=sound length present |
| Sound *ResRef*      | [char](GFF-File-Format#gff-data-types)  | 4 (0x04) | 16   | Voice-over audio filename ([null-terminated](https://en.cppreference.com/w/c/string/byte), max 16 chars)        |
| Volume Variance   | UInt32    | 20 (0x14) | 4    | Unused in KotOR (always 0)                                      |
| Pitch Variance    | UInt32    | 24 (0x18) | 4    | Unused in KotOR (always 0)                                      |
| offset to string  | UInt32    | 28 (0x1C) | 4    | offset to string text (relative to string Entries offset)       |
| string size       | UInt32    | 32 (0x20) | 4    | Length of string text in bytes                                  |
| Sound Length      | float     | 36 (0x24) | 4    | Duration of voice-over audio in seconds                         |

**References:** [Kotor.NET `StringData` L92–L129](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L92-L129); PyKotor row decode [`_load_tlk_legacy` L96–L112](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L96-L112); [reone `loadStrings` L45–L69](https://github.com/modawan/reone/blob/master/src/libs/resource/format/tlkreader.cpp#L45-L69); [KotOR.js `LoadFromBuffer` L65–L75](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TLKObject.ts#L65-L75).

**flag bits:**

- **bit 0 (0x0001)**: Text present - string has text content
- **bit 1 (0x0002)**: Sound present - string has associated voice-over audio
- **bit 2 (0x0004)**: Sound length present - sound length field is valid

**flag Combinations:**

Common flag patterns in KotOR TLK files:

| flags | Hex | Description | Usage |
| ----- | --- | ----------- | ----- |
| `0x0001` | `0x01` | Text only | Menu options, item descriptions, non-voiced dialog |
| `0x0003` | `0x03` | Text + Sound | Voiced dialog lines (most common for party/NPC speech) |
| `0x0007` | `0x07` | Text + Sound + Length | Fully voiced with duration data (cutscenes, important dialog) |
| `0x0000` | `0x00` | Empty entry | Unused [StrRef](TLK-File-Format#string-references-strref) slots |

The engine uses these flags to decide:

- Whether to display subtitles (Text present flag)
- Whether to play voice-over audio (Sound present flag)
- How long to wait before auto-advancing dialog (Sound length present flag)

Missing flags are treated as `false` - if Text present is not set, the string is treated as empty even if text data exists.

### String entries

String entries follow the string data table:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| string Text  | [char](GFF-File-Format#gff-data-types)[] | [null-terminated string](https://en.cppreference.com/w/c/string/byte) data (UTF-8 or Windows-1252 encoded)     |

string text is stored at the offset specified in the string data table entry. The encoding depends on the language ID (see [Concepts](Concepts#language-ids-kotor) and [Localization](#localization) below).

---

## TLKEntry structure

Each TLK entry contains:

**References:** PyKotor `TLK` / `TLKEntry` — [`tlk_data.py` L54–L420](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L420); entry serialization — [`io_tlk.py` `_write_entry` L194–L219](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L194-L219).

| Attribute        | type   | Description                                                      |
| ---------------- | ------ | ---------------------------------------------------------------- |
| `text`           | str    | Localized text string                                            |
| `voiceover`      | *ResRef* | Voice-over audio filename ([WAV file](WAV-File-Format))                            |
| `text_present`   | bool   | Whether text content exists                                      |
| `sound_present`  | bool   | Whether voice-over audio exists                                  |
| `soundlength_present` | bool | Whether sound length is valid                                    |
| `sound_length`   | float  | Duration of voice-over audio in seconds                         |

---

## string References (StrRef)

string references (StrRef) are integer indices into the TLK file's entry array:

- **StrRef 0**: First entry in the TLK file
- **StrRef -1**: No string reference (used to indicate missing/empty strings)
- **StrRef N**: Nth entry (0-based indexing)

The game uses StrRef values throughout [GFF files](GFF-File-Format), scripts, and other resources to reference localized text. When displaying text, the game looks up the StrRef in `dialog.tlk` and displays the corresponding text.

### Custom TLK files

Mods can add custom TLK files to extend available strings:

**dialog.tlk structure:**

- Base game: `dialog.tlk` (read-only, ~50,000-100,000 entries)
- Custom content: `dialogf.tlk` or custom TLK files placed in override

**[StrRef](TLK-File-Format#string-references-strref) Ranges:**

- `0` to `~50,000`: Base game strings (varies by language)
- `16,777,216` (`0x01000000`) and above: Custom TLK range (TSLPatcher convention)
- Negative values: Invalid/missing references

**Mod Tools Approach:**

TSLPatcher and similar tools use high [StrRef](TLK-File-Format#string-references-strref) ranges for custom strings:

```plaintext
Base [StrRef](TLK-File-Format#string-references-strref):   0 - 50,000 (dialog.tlk)
Custom Range:  16777216+ (custom TLK files)
```

This avoids conflicts with base game strings and allows mods to add thousands of custom text entries without overwriting existing content.

**Multiple TLK files:**

The game can load multiple TLK files:

1. `dialog.tlk` - Primary game text
2. `dialogf.tlk` - Female-specific variants (polish K1 only)

Priority: Custom TLKs --> dialogf.tlk --> `dialog.tlk`

---

## Localization

Numeric **language IDs** and typical encodings (0–8) are defined on [Concepts](Concepts#language-ids-kotor). This section covers **TLK-specific** behavior only.

**KotOR:** Retail builds usually install one `dialog.tlk` per language; the file header’s Language ID is often ignored at runtime and is mainly useful for tools tagging which language a TLK was built for.

**Encoding:** Western languages (IDs 0–4) normally use Windows-1252 in legacy tooling; Polish (5) uses Windows-1250. IDs 6–8 use UTF-8 in the wider Aurora spec. String payloads may still be UTF-8 or Windows-1252 depending on the tool and target game—see the string entry description above.

Windows-1252 is a single-byte encoding (256 code points) and is often loosely called "ISO-8859-1" or *cp1252*.

---

## Implementation Details

| Layer | PyKotor (`master`) |
| ----- | ------------------- |
| Layout spec (docstring) | [`tlk_data.py` L1–L39](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L1-L39) |
| `TLK` / `TLKEntry` | [`tlk_data.py` L54–L420](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/tlk_data.py#L54-L420) |
| Binary read | [`io_tlk.py` L32–L156](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L32-L156) (`TLKBinaryReader` L123–L156) |
| Binary write | [`io_tlk.py` L159–L219](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/tlk/io_tlk.py#L159-L219) |

**Kotor.NET:** [`TLKBinaryStructure.cs` L16–L130](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs#L16-L130).

See **Cross-reference implementations** under [File structure overview](#file-structure-overview) for reone, xoreos, KotOR.js, and KotOR-Unity.

### See also

- [Concepts](Concepts#language-ids-kotor) -- Language IDs and encodings
- [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax) -- Modifying TLK via HoloPatcher/TSLPatcher
- [2DA-File-Format](2DA-File-Format), [GFF-File-Format](GFF-File-Format) -- StrRef consumers; [NSS-File-Format](NSS-File-Format) -- Script strings
- [Bioware-Aurora-TalkTable](Bioware-Aurora-TalkTable) -- Aurora talk table spec
- [Concepts](Concepts#resource-resolution-order) -- Resource resolution; [KEY-File-Format](KEY-File-Format) -- KEY/BIF index
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for TLK/StrRef modding

---

This documentation aims to provide a comprehensive overview of the KotOR TLK file format, focusing on the detailed file structure and data formats used within the games.
