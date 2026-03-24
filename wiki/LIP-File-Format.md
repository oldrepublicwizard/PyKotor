# KotOR LIP file format Documentation

LIP (LIP Synchronization) files drive mouth [animation](MDL-MDX-File-Format#animation-header) for voiced dialogue. Each file contains a compact series of [keyframes](MDL-MDX-File-Format#controller-structure) that map timestamps to discrete viseme (mouth shape) indices so that the engine can interpolate character LIP movement while playing the companion [WAV](WAV-File-Format) line. LIP files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**For mod developers:** LIP is paired with [WAV](WAV-File-Format) voice-over; see [TLK](TLK-File-Format), [DLG](GFF-DLG), and [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** LIP is referenced by [TLK](TLK-File-Format) (voice-over) and [DLG](GFF-DLG); duration must match the companion [WAV](WAV-File-Format).

## Table of Contents

- KotOR LIP File Format Documentation
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
  - [Binary format](#binary-format)
    - [Header](#header)
    - [Keyframe Table](#keyframe-table)
  - [Mouth Shapes (Viseme Table)](#mouth-shapes-viseme-table)
  - [Animation Rules](#animation-rules)
  - [Implementation Details](#implementation-details)

---


## File structure overview

- LIP files are always binary (`"LIP V1.0"` signature) and contain only [animation](MDL-MDX-File-Format#animation-header) data.  
- They are paired with [WAV](WAV-File-Format) voice-over resources of identical duration; the LIP `length` field must match the [WAV](WAV-File-Format) `data` playback time for glitch-free [animation](MDL-MDX-File-Format#animation-header).  
- [keyframes](MDL-MDX-File-Format#controller-structure) are sorted chronologically and store a timestamp (float seconds) plus a 1-[byte](https://en.wikipedia.org/wiki/Byte) viseme index (0–15).  
- The layout is identical across **[reone](https://github.com/modawan/reone)**, **[xoreos](https://github.com/xoreos/xoreos)**, **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**, **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**, and **mdlops**, so the header/[keyframe](MDL-MDX-File-Format#controller-structure) offsets below are cross-confirmed against those implementations.  

**Implementation (PyKotor):** [`resource/formats/lip/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/) — binary read [`LIPBinaryReader.load` L95+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py#L95), write [`LIPBinaryWriter.write` L117+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py#L117); data model in `lip_data.py`; XML/JSON in `io_lip_xml`, `io_lip_json`.

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`lipreader.cpp` L27+](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/lipreader.cpp#L27) — C++ LIP parser
- **[xoreos](https://github.com/xoreos/xoreos)**: [`lipfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/lipfile.cpp) — Aurora LIP
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`LIPObject.ts` L26+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LIPObject.ts#L26), [`readBinary` L112–L136](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LIPObject.ts#L112-L136) — header + keyframe table
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`LIP.cs` L11+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorLIP/LIP.cs#L11) — in-memory LIP / viseme DTOs

### See also

- [TLK File Format](TLK-File-Format) - [Talk Table](TLK-File-Format) containing voice-over references
- [WAV File Format](WAV-File-Format) - Audio format paired with LIP files
- [GFF-DLG](GFF-DLG) - [dialogue files](GFF-File-Format#dlg-dialogue) that trigger LIP [animations](MDL-MDX-File-Format#animation-header)

---

## Binary format

### Header

| Name          | type    | offset | size | Description |
| ------------- | ------- | ------ | ---- | ----------- |
| file type     | [char](GFF-File-Format#gff-data-types) | 0 (0x00)   | 4    | Always `"LIP "` |
| file Version  | [char](GFF-File-Format#gff-data-types) | 4 (0x04)   | 4    | Always `"V1.0"` |
| Sound Length  | [float32](GFF-File-Format#gff-data-types) | 8 (0x08)   | 4    | Duration in seconds (must equal [WAV](WAV-File-Format) length) |
| Entry count   | UInt32  | 12 (0x0C)   | 4    | Number of [keyframes](MDL-MDX-File-Format#controller-structure) immediately following |

**References**

**Cross-reference:**

- **[reone](https://github.com/modawan/reone)**: [`lipreader.cpp` L27–L42](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/lipreader.cpp#L27-L42) — LIP header parsing

### [keyframe](MDL-MDX-File-Format#controller-structure) Table

[keyframes](MDL-MDX-File-Format#controller-structure) follow immediately after the header; there is no padding.

| Name       | type    | Offset (per entry) | size | Description |
| ---------- | ------- | ------------------ | ---- | ----------- |
| Timestamp  | [float32](GFF-File-Format#gff-data-types) | 0 (0x00)               | 4    | Seconds from [animation](MDL-MDX-File-Format#animation-header) start |
| Shape      | [uint8](GFF-File-Format#gff-data-types)   | 4 (0x04)               | 1    | Viseme index (`0–15`) |

- Entries are stored sequentially and **must** be sorted ascending by timestamp.  
- Libraries average multiple implementations to validate this layout ([reone](https://github.com/modawan/reone), [xoreos](https://github.com/xoreos/xoreos), [KotOR.js](https://github.com/KobaltBlu/KotOR.js), [Kotor.NET](https://github.com/NickHugi/Kotor.NET)).  

**References**

**Cross-reference:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`LIPObject.ts` `readBinary` L112–L136](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LIPObject.ts#L112-L136) — keyframe table parsing

---

## Mouth Shapes (Viseme Table)

KotOR reuses the 16-shape Preston Blair [phoneme](https://en.wikipedia.org/wiki/Phoneme) set. Every implementation agrees on the [byte](https://en.wikipedia.org/wiki/Byte) value assignments; KotOR.js only renames a few labels but the indices match.

| value | Shape | Description |
| ----- | ----- | ----------- |
| 0 | **NEUTRAL** | Rest/closed mouth |
| 1 | **EE** | Teeth apart, wide smile (long "ee") |
| 2 | **EH** | Relaxed mouth ("eh") |
| 3 | **AH** | Mouth open ("ah/aa") |
| 4 | **OH** | Rounded lips ("oh") |
| 5 | **OOH** | Pursed lips ("oo", "w") |
| 6 | **Y** | Slight smile ("y") |
| 7 | **STS** | Teeth touching ("s", "z", "ts") |
| 8 | **FV** | Lower LIP touches teeth ("f", "v") |
| 9 | **NG** | Tongue raised ("n", "ng") |
| 10 | **TH** | Tongue between teeth ("th") |
| 11 | **MPB** | Lips closed ("m", "p", "b") |
| 12 | **TD** | Tongue up ("t", "d") |
| 13 | **SH** | Rounded relaxed ("sh", "ch", "j") |
| 14 | **L** | Tongue forward ("l", "r") |
| 15 | **KG** | Back of tongue raised ("k", "g", "h") |

**Reference:** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py:50-169`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L50-L169)

---

## [animation](MDL-MDX-File-Format#animation-header) Rules

- **[Interpolation](https://en.wikipedia.org/wiki/Interpolation):** The engine interpolates between consecutive [keyframes](https://en.wikipedia.org/wiki/Key_frame); PyKotor exposes `LIP.get_shapes()` to compute the left/right [visemes](https://en.wikipedia.org/wiki/Viseme) plus blend factor.  
  **Reference:** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py:342-385`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L342-L385)
- **Sorting:** When adding frames, PyKotor removes existing entries at the same timestamp and keeps the list sorted.  
  **Reference:** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py:305-323`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L305-L323)
- **Duration Alignment:** LIP `length` is updated to the max timestamp so exported [animations](MDL-MDX-File-Format#animation-header) stay aligned with their [WAV](WAV-File-Format) line.  
  **Reference:** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py:267-323`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py#L267-L323)
- **Generation:** Automated pipelines (MDLOps, KotORBlender) map phonemes to visemes via `LIPShape.from_phoneme()`, and the same mapping table appears in the vendor projects referenced above to keep authoring tools consistent.  

---

## Implementation Details

- **Binary Reader:** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/io_lip.py)  
- **data [model](MDL-MDX-File-Format):** [`Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/lip/lip_data.py)  
- **Reference implementations:**  
  - **[reone](https://github.com/modawan/reone)** [`lipreader.cpp` L27+](https://github.com/modawan/reone/blob/master/src/libs/graphics/format/lipreader.cpp#L27)
  - **[xoreos](https://github.com/xoreos/xoreos)** [`lipfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/lipfile.cpp)
  - **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** [`LIPObject.ts` L26+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LIPObject.ts#L26)
  - **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** [`LIP.cs` L11+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorLIP/LIP.cs#L11)

The references above implement the same header layout and [keyframe](MDL-MDX-File-Format#controller-structure) encoding, ensuring PyKotor stays compatible with the other toolchains.
