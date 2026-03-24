# KotOR LTR files format Documentation

LTR (Letter) resources store third-order Markov chain probability tables that the game uses to procedurally generate NPC names. The data encodes likelihoods for characters appearing at the start, middle, and end of names given zero, one, or two-character context. LTR files are loaded with the same [Resource Resolution Order](Concepts#resource-resolution-order) as other resources (`override/`, [`.erf/.mod/.sav`](ERF-File-Format), [`.rim`](RIM-File-Format), [`KEY`](KEY-File-Format)/[`BIF`](BIF-File-Format)).

**For mod developers:** *LTR* is used by the engine for random name generation; see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## Table of Contents

- KotOR LTR files format Documentation
  - Table of Contents
  - [File Structure Overview](#file-structure-overview)
  - [Binary Format](#binary-format)
    - [Header](#header)
    - [Single-Letter Block](#single-letter-block)
    - [Double-Letter Blocks](#double-letter-blocks)
    - [Triple-Letter Blocks](#triple-letter-blocks)
  - [Probability Blocks](#probability-blocks)
  - [Name Generation Process](#name-generation-process)

---

## File Structure Overview

- KotOR always uses the **28-character alphabet** (`a–z` plus `'` and `-`). **Neverwinter Nights (NWN) used 26 characters**; the header stores the count. This is a **KotOR-specific difference** from NWN.
- *LTR* files are binary: a short header (see below) followed by three probability tables (singles, doubles, triples) stored as contiguous **float32** arrays (cumulative probabilities in vanilla data).

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **PyKotor** — on-disk layout and offsets in module docstring: [`ltr_data.py` L1–L50](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L1-L50); `LTR` model + `generate()`: [`ltr_data.py` L64–L288](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L64-L288); binary I/O: [`LTRBinaryReader.load` L55–L113](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L55-L113), [`LTRBinaryWriter.write` L125–L156](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L125-L156).
- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/seedhartha/reone)): [`ltrreader.cpp` `LtrReader::load` L27–L61](https://github.com/modawan/reone/blob/master/src/libs/resource/format/ltrreader.cpp#L27-L61) (8-byte `"LTR V1.0"` signature, `uint8` letter count, nested `readLetterSet` L63–L79); struct layout [`include/reone/resource/ltr.h` L24–L48](https://github.com/modawan/reone/blob/master/include/reone/resource/ltr.h#L24-L48).
- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/aurora/ltrfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/ltrfile.cpp), [`ltrfile.h` L57–L76](https://github.com/xoreos/xoreos/blob/master/src/aurora/ltrfile.h#L57-L76).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`LTRObject.ts` `readBuffer` L51–L124](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LTRObject.ts#L51-L124) (`LTR_HEADER_LENGTH = 9`); runtime name roll [`getName` L128–L210](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LTRObject.ts#L128-L210).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — check [`Kotor.NET/Formats/`](https://github.com/NickHugi/Kotor.NET/tree/master/Kotor.NET/Formats) for LTR support in your checkout (paths have changed across branches; no stable permalink verified from this wiki revision).

---

## Binary Format

### Header

The header is **9 bytes** for standard Aurora/KotOR *LTR* (not 12): 4-byte type, 4-byte version, 1-byte letter count. PyKotor and reone both read **8 bytes** of signature as the literal string **`LTR V1.0`** (no separate padding), then the letter count.

| Name         | type    | offset | size | Description |
| ------------ | ------- | ------ | ---- | ----------- |
| File Type + Version | [char](GFF-File-Format#gff-data-types) | 0 (0x00)   | 8    | ASCII `"LTR V1.0"` (see [`io_ltr.py` L66–L76](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L66-L76), [reone `ltrreader.cpp` L28](https://github.com/modawan/reone/blob/master/src/libs/resource/format/ltrreader.cpp#L28)). |
| Letter Count | [uint8](GFF-File-Format#gff-data-types)   | 8 (0x08)   | 1    | Must be **28** for KotOR (PyKotor enforces this: [`io_ltr.py` L81–L84](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L81-L84)). |

### Single-Letter Block

Immediately after the header, the **single-letter** probabilities are stored as three arrays of `letter_count` floats (*start*, *middle*, *end*). For KotOR (`letter_count == 28`) that is `28 × 3 × 4 = 336` bytes.

| Section | Entries | Description |
| ------- | ------- | ----------- |
| Start   | 28 floats | Probability of each letter starting a name |
| Middle  | 28 floats | Probability of each letter appearing mid-name |
| End     | 28 floats | Probability of each letter ending a name |

### Double-Letter Blocks

For each character in the alphabet there is a **double-letter** block (context length 1). Each block repeats the same *start/middle/end* layout (28 floats each).

Total size (KotOR): `28 × 3 × 28 × 4 = 9,408` bytes.

### Triple-Letter Blocks

The **triple-letter** section encodes 2-character context. There are `letter_count × letter_count` blocks, each with *start/middle/end* arrays of 28 floats.

Total size (KotOR): `28 × 28 × 3 × 28 × 4 = 263,424` bytes.

**Layout offsets (28-letter, float32):** singles begin at byte **9** (immediately after header). Doubles begin at `9 + 28×3×4 = 345` (`0x159`). Triples begin at `345 + 28×28×3×4 = 9,753` (`0x2619`). (Some older notes and comments used different hex offsets—trust the byte counts and reader loops in [`io_ltr.py` L88–L108](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L88-L108).)

---

## Probability Blocks

Each block is represented by the `LTRBlock` class in PyKotor ([`ltr_data.py` `LTRBlock` L363+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L363-L615)), mirroring `LetterSet` / `Ltr::LetterSet` in reone and xoreos. Blocks store **cumulative** probabilities (monotonically increasing floats) that are compared against random roll values.

- **Singles (`_singles`)**: No context; used for the very first character.
- **Doubles (`_doubles`)**: Indexed by the previous character; used for the second character.
- **Triples (`_triples`)**: Two-dimensional array indexed by the previous two characters; used for every character after the second.

**References:** [reone `ltr.h` L24–L48](https://github.com/modawan/reone/blob/master/include/reone/resource/ltr.h#L24-L48); [xoreos `ltrfile.h` L57–L76](https://github.com/xoreos/xoreos/blob/master/src/aurora/ltrfile.h#L57-L76).

---

## Name Generation Process

The runtime algorithm (PyKotor, reone, xoreos, KotOR.js, etc.) follows the same broad steps:

1. **Seed/Random Setup** – optional deterministic seed for reproducible results (PyKotor: [`LTR.generate` L170–L288](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L170-L288)).
2. **First Character** – roll against single-letter *start* weights.
3. **Second Character** – roll against double-letter *start* for the previous letter.
4. **Third Character** – roll against triple-letter *start* for the previous two letters.
5. **Subsequent Characters** – roll against triple-letter *middle*; termination uses triple-letter *end* plus length heuristics (compare KotOR.js [`getName` L173–L200](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LTRObject.ts#L173-L200) with PyKotor [`generate` L252–L285](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L252-L285)).
6. **Post-processing** – capitalize / minimum length; retries on failed rolls.

**References**

- Community C reference: [mtijanic `nwnltr.c`](https://github.com/mtijanic/nwn-misc/blob/master/nwnltr.c) (NWN lineage; KotOR uses 28 letters).
- PyKotor: [`ltr_data.py` `generate` L170–L288](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/ltr_data.py#L170-L288); I/O [`io_ltr.py` L55–L156](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/ltr/io_ltr.py#L55-L156).
- [reone `ltrreader.cpp` L27–L79](https://github.com/modawan/reone/blob/master/src/libs/resource/format/ltrreader.cpp#L27-L79); [xoreos `ltrfile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/ltrfile.cpp); [KotOR.js `LTRObject.ts` L51–L210](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/LTRObject.ts#L51-L210).

Because PyKotor matches the binary layout described above, *LTR* resources round-trip with the other cited implementations for **28-letter** KotOR tables.
