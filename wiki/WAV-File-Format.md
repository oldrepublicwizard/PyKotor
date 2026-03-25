# KotOR WAV file format Documentation

KotOR stores both standard WAV voice-over lines and Bioware-obfuscated sound-effect files. Voice-over assets are regular RIFF containers with PCM headers, while SFX assets prepend a 470-[byte](https://en.wikipedia.org/wiki/Byte) custom block before the RIFF data. PyKotor handles both variants transparently. WAV files are resolved using the same [resource resolution order](Concepts#resource-resolution-order) as other resources ([override](Concepts#override-folder), [MOD/ERF/SAV](ERF-File-Format), [KEY/BIF](KEY-File-Format)). Hex type id **`0x0004`** is listed under [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers).

**Implementation (PyKotor)**

- **Binary reader/writer:** [`io_wav.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py) — [`WAVBinaryReader` L100+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L100), [`load` L148+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L148) (SFX obfuscation + RIFF); [`WAVBinaryWriter` L302+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L302); RIFF parse helper [`_parse_riff_wave_from_kaitai` L56+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/io_wav.py#L56).
- **Data model:** [`wav_data.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/wav/wav_data.py).

**Cross-reference implementations (line anchors are against `master` and may drift):**

- **[reone](https://github.com/modawan/reone)** ([historical upstream / mirror: seedhartha/reone](https://github.com/modawan/reone)) — [`wavreader.cpp` — `WavReader::load` L32+](https://github.com/modawan/reone/blob/master/src/libs/audio/format/wavreader.cpp#L32) (470-byte SFX signature `FF F3 60 C4` then seek `0x1DA`, RIFF/`fmt`/`data`, MP3-in-WAV edge case).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — [`AudioFile.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/audio/AudioFile.ts) — SFX probe [`fakeHeaderTest` / `riffHeaderTest` L12-L13](https://github.com/KobaltBlu/KotOR.js/blob/master/src/audio/AudioFile.ts#L12-L13), strip 470-byte prefix [`processFile` L118-L124](https://github.com/KobaltBlu/KotOR.js/blob/master/src/audio/AudioFile.ts#L118-L124), MP3-in-WAV `riffSize == 50` branch [L131-L137](https://github.com/KobaltBlu/KotOR.js/blob/master/src/audio/AudioFile.ts#L131-L137).
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — no dedicated `KotorWAV` reader on the default branch; creature sound **StrRefs** (resolved to `.wav` via [TLK](TLK-File-Format) at runtime) are modeled in [`Kotor.NET/Formats/KotorSSF/SSF.cs` L12+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorSSF/SSF.cs#L12). For byte-level RIFF/SFX layout, prefer **PyKotor**, **reone**, and **KotOR.js** above.

**For mod developers:** WAV files are referenced by [TLK](TLK-File-Format) (voice-over) and [SSF](SSF-File-Format); see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** WAV is referenced by [TLK](TLK-File-Format) (StrRef --> sound), [SSF](SSF-File-Format), [LIP](LIP-File-Format), and [DLG](GFF-DLG) (VO_ResRef).

## Table of Contents

- KotOR WAV File Format Documentation
  - Table of Contents
  - File Types
  - [Standard RIFF/WAVE Structure](#standard-riffwave-structure)
    - [Format Chunk](#format-chunk)
    - [Data Chunk](#data-chunk)
  - [KotOR SFX Header](#kotor-sfx-header)
  - [Encoding Details](#encoding-details)
  - [Implementation Details](#implementation-details)

---

## File types

| type | Usage | Description |
| ---- | ----- | ----------- |
| **VO (Voice-over)** | Dialogue lines (`*.wav` referenced by [TLK](TLK-File-Format) [StrRefs](TLK-File-Format#string-references-strref)). | Plain RIFF/WAVE PCM files readable by any media player. |
| **SFX (Sound effects)** | Combat, UI, ambience, `.wav` files under `StreamSounds`/`SFX`. | Contains a Bioware 470-[byte](https://en.wikipedia.org/wiki/Byte) obfuscation header followed by the same RIFF data. |

PyKotor exposes these via the `WAVType` enum (`VO` vs. `SFX`) so tools know whether to insert/remove the proprietary header (`io_wav.py:52-121`).

---

## Standard RIFF/WAVE structure

KotOR sticks to the canonical RIFF chunk order:

| offset | field | Description |
| ------ | ----- | ----------- |
| 0 (0x00) | `"RIFF"` | Chunk ID |
| 4 (0x04) | `<uint32>` | file size minus 8 |
| 8 (0x08) | `"WAVE"` | format tag |
| 12 (0x0C) | `"fmt "` | format chunk ID |
| 16 (0x10) | `<uint32>` | format chunk size (usually 0x10) |
| … | See below | |

### Format chunk

| field | type | Description |
| ----- | ---- | ----------- |
| `audio_format` | uint16 | `0x0001` for PCM, `0x0011` for IMA ADPCM. |
| `channels` | uint16 | 1 (mono) or 2 (stereo). |
| `sample_rate` | uint32 | Typically 22050 Hz (SFX) or 44100 Hz (VO). |
| `bytes_per_sec` | uint32 | `sample_rate × block_align`. |
| `block_align` | uint16 | Bytes per sample frame. |
| `bits_per_sample` | uint16 | 8 or 16 for PCM. |
| `extra_bytes` | … | Present only when `fmt_size > 0x10` (e.g., ADPCM coefficients). |

### Data chunk

After the `fmt` chunk (and any optional `fact` chunk), the `"data"` chunk begins:

| field | Description |
| ----- | ----------- |
| `"data"` | Chunk ID. |
| `<uint32>` | Number of bytes of raw audio. |
| `<byte[]>` | PCM/ADPCM sample data. |

KotOR voice-over WAVs add a `"fact"` chunk with a 32-bit sample count, which PyKotor writes for compatibility (`io_wav.py:182-186`).

---

## KotOR SFX header

- SFX assets start with 470 bytes of obfuscated metadata (magic numbers plus filler `0x55`).  
- After this header, the file resumes at the `"RIFF"` signature described above.  
- When exporting SFX, PyKotor recreates the header verbatim so the game recognizes the asset (`io_wav.py:150-163`).  

*(See **Cross-reference implementations** above for reone / KotOR.js / Kotor.NET line anchors.)*

---

## Encoding Details

- **PCM (`audio_format = 0x0001`)**: Most dialogue is 16-bit mono PCM, which streams directly through the engine mixer.  
- **IMA ADPCM (`audio_format = 0x0011`)**: Some ambient SFX use compressed ADPCM frames; when present, the `fmt` chunk includes the extra coefficient block defined by the WAV spec.  
- KotOR requires `block_align` and `bytes_per_sec` to match the values implied by the codec; mismatched headers can crash the in-engine decoder.  

External tooling such as SithCodec and `SWKotOR-Audio-Encoder` implement the same formats; PyKotor simply exposes the metadata so conversions stay lossless.

### Community context (workflow)

- Deadly Stream — [SithCodec](https://deadlystream.com/files/file/1716-sithcodec/) (Windows tool for KotOR audio header strip/add; pair with PyKotor `io_wav` when verifying bytes).
- Deadly Stream — [Extracting dialogue](https://deadlystream.com/topic/9437-extracting-dialogue/) — **community-reported** layout notes (e.g. some assets under `StreamWaves` / `StreamVoice`); treat thread as **workflow hints**, not normative RIFF layout—verify against **PyKotor** / **reone** / **KotOR.js** above.

### Historical context (LucasForums Archive)

TSLPatcher-era threads discuss **Streamsounds** / **Streamwaves** paths, codec issues in Miles-based workflows, and DLG-related **`StreamVoice`** layout (e.g. `alienvo.2da` → `StreamVoice\AVO\`). Treat these as **dated player/modder reports**, not engine specifications—pair with **SithCodec**, **PyKotor `io_wav`**, and the cross-refs at the top of this page.

- [Convert KOTOR sounds to a usable audio file](https://www.lucasforumsarchive.com/thread/208881-convert-kotor-sounds-to-a-usable-audio-file)
- [Editing KotOR voiceover files — which program?](https://www.lucasforumsarchive.com/thread/208744-editing-kotor-voiceover-files-program)
- [Listening and editing KotOR I & II audio](https://www.lucasforumsarchive.com/thread/174967-listening-and-editing-kotor-i-amp-ii-audio)
- [KotOR/TSL GUI Dialog Editor (DLGEditor) — `StreamVoice` / `alienvo` discussion (e.g. p.2)](https://www.lucasforumsarchive.com/thread/135639-kotortsl-gui-dialog-editor-dlgeditor-current-version-232/page/2)

---

## Implementation Details

- **Reference implementations (engines):** same as **Cross-reference implementations** at the top of this page (PyKotor `io_wav.py`, reone `wavreader.cpp`, KotOR.js `AudioFile.ts`).
- **Community tooling (not normative):** **[SithCodec](https://github.com/BBBrassil/SithCodec)** — encode/decode helper; **[SWKotOR-Audio-Encoder](https://github.com/LoranRendel/SWKotOR-Audio-Encoder)** — batch-friendly encoder. Prefer verifying headers against **PyKotor** / **reone** / **KotOR.js** when debugging engine mismatches.

With this structure, WAV assets authored in PyKotor will play identically in the base game and in the other vendor tools.

### See also

- [Resource formats and resolution](Resource-Formats-and-Resolution) - [Resource type identifiers](Resource-Formats-and-Resolution#resource-type-identifiers) (`WAV` / `0x0004`)
- [TLK File Format](TLK-File-Format) - Talk table that references WAV voice-over
- [SSF File Format](SSF-File-Format) - Sound set files that reference WAV via StrRef
- [LIP File Format](LIP-File-Format) - Lip-sync paired with WAV dialogue
- [GFF-DLG](GFF-DLG) - Dialogue files that reference WAV (VO_ResRef)

---
