# UTS (Sound)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTS files define [sound object templates](GFF-File-Format#uts-sound) for ambient and environmental audio. These can be positional 3D sounds or global stereo sounds, with looping, randomization, and volume control. UTS files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Sound Object format specification, see [Bioware Aurora Sound Object Format](Bioware-Aurora-SoundObject).

**For mod developers:** To modify sound blueprints in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`uts.py` `UTS` L18+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L18) — in-memory sound-object model (playback, 3D params, sound list)
- [`construct_uts` L187+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L187), [`read_uts` L286+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L286), [`write_uts` L295+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L295) — GFF ↔ `UTS` round-trip
- [`gff_data.py` `GFFContent.UTS` L155](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L155) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTS as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Ambient audio and WAV/MP3 packaging threads appear on Deadly Stream and archives—see [WAV-File-Format](WAV-File-Format) and [Home — Community sources](Home#community-sources-and-archives). Forum posts explain **workflow**; **UTS field tables** stay anchored here + BioWare + PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this sound |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocName` | [CExoLocString](GFF-File-Format#gff-data-types) | Sound name (unused) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Playback Control

| field | type | Description |
| ----- | ---- | ----------- |
| `Active` | Byte | Sound is currently active |
| `Continuous` | Byte | Sound plays continuously |
| `Looping` | Byte | Individual samples loop |
| `Positional` | Byte | Sound is 3D positional |
| `Random` | Byte | Randomly select from Sounds list |
| `Volume` | Byte | Volume level (0-127) |
| `VolumeVary` | Byte | Random volume variation |
| `PitchVary` | Byte | Random pitch variation |

## Timing & Interval

| field | type | Description |
| ----- | ---- | ----------- |
| `Interval` | Int | Delay between plays (seconds) |
| `IntervalVary` | Int | Random interval variation |
| `Times` | Int | Times to play (unused) |

**Playback Modes:**

- **Continuous**: Loops one sample indefinitely (machinery, hum)
- **Interval**: Plays samples with delays (birds, random creaks)
- **Random**: Picks different sample each time

## Positioning

| field | type | Description |
| ----- | ---- | ----------- |
| `Elevation` | Float | Height offset from ground |
| `MaxDistance` | Float | Distance where sound becomes inaudible |
| `MinDistance` | Float | Distance where sound is at full volume |
| `RandomPosition` | Byte | Randomize emitter position |
| `RandomRangeX` | Float | X-axis random range |
| `RandomRangeY` | Float | Y-axis random range |

**3D Audio:**

- **Positional=1**: Sound attenuates with distance and pans
- **Positional=0**: Global stereo sound (music, voiceover)
- **Min/Max Distance**: Controls falloff curve

## Sound List

| field | type | Description |
| ----- | ---- | ----------- |
| `Sounds` | List | List of [WAV](WAV-File-Format)/MP3 files to play |

**Sounds Struct fields:**

- `Sound` (*ResRef*): Audio file resource

**Randomization:**

- If `Random=1`, engine picks one sound from list each interval
- Allows for varied ambience (e.g., 5 different bird calls)

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure; [Bioware-Aurora-SoundObject](Bioware-Aurora-SoundObject) -- Aurora sound spec
- [WAV-File-Format](WAV-File-Format) -- Audio resources; [GFF-GIT](GFF-GIT) -- Sound instances in areas
- [KEY-File-Format](KEY-File-Format) -- Resource resolution
