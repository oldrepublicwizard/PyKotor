# UTT (Trigger)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTT files define [trigger templates](GFF-File-Format#utt-trigger) for invisible volumes that fire scripts when entered, exited, or used. Triggers are essential for area transitions, cutscenes, traps, and game logic. UTT files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Trigger format specification, see [Bioware Aurora Trigger Format](Bioware-Aurora-Trigger).

**For mod developers:** To modify trigger templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`utt.py` `UTT` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L17) — in-memory trigger model (transitions, traps, script hooks)
- [`construct_utt` L148+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L148), [`read_utt` L265+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L265), [`write_utt` L274+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L274) — GFF ↔ `UTT` round-trip
- [`gff_data.py` `GFFContent.UTT` L157](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L157) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTT as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Area transitions and trap behavior are discussed across forums—see [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) and [Home — Community sources](Home#community-sources-and-archives). Use community write-ups for **playtesting and tooling**; **UTT fields** follow this page + BioWare + PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this trigger |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocName` | [CExoLocString](GFF-File-Format#gff-data-types) | Trigger name (localized) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Trigger Configuration

| field | type | Description |
| ----- | ---- | ----------- |
| `Type` | Int | Trigger type (0=Generic, 1=Transition, 2=Trap) |
| `Faction` | Word | Faction identifier |
| `Cursor` | Int | Cursor icon when hovered (0=None, 1=Door, etc) |
| `HighlightHeight` | Float | Height of selection highlight |

**Trigger types:**

- **Generic**: Script execution volume
- **Transition**: Loads new module or moves to waypoint
- **Trap**: Damages/effects entering object

## Transition Settings

| field | type | Description |
| ----- | ---- | ----------- |
| `LinkedTo` | [CExoString](GFF-File-Format#gff-data-types) | Destination waypoint tag |
| `LinkedToModule` | *ResRef* | Destination module *ResRef* |
| `LinkedToFlags` | Byte | Transition behavior flags |
| `LoadScreenID` | Word | Loading screen ID |
| `PortraitId` | Word | Portrait ID (unused) |

**Area Transitions:**

- **LinkedToModule**: Target module to load
- **LinkedTo**: Waypoint where player spawns
- **LoadScreenID**: Image displayed during load

## Trap System

| field | type | Description |
| ----- | ---- | ----------- |
| `TrapFlag` | Byte | Trigger is a trap |
| `TrapType` | Byte | index into `traps.2da` |
| `TrapDetectable` | Byte | Can be detected |
| `TrapDetectDC` | Byte | Awareness DC to detect |
| `TrapDisarmable` | Byte | Can be disarmed |
| `DisarmDC` | Byte | Security DC to disarm |
| `TrapOneShot` | Byte | Fires once then disables |
| `AutoRemoveKey` | Byte | [KEY](KEY-File-Format) removed on use |
| `KeyName` | [CExoString](GFF-File-Format#gff-data-types) | [KEY](KEY-File-Format) tag required to disarm/bypass |

**Trap Mechanics:**

- Floor traps (mines, pressure plates) are triggers
- Detection makes trap visible and clickable
- Entering without disarm triggers trap effect

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `OnClick` | *ResRef* | Fires when clicked |
| `OnDisarm` | *ResRef* | Fires when disarmed |
| `OnHeartbeat` | *ResRef* | Fires periodically |
| `OnScriptEnter` | *ResRef* | Fires when object enters |
| `OnScriptExit` | *ResRef* | Fires when object exits |
| `OnTrapTriggered` | *ResRef* | Fires when trap activates |
| `OnUserDefined` | *ResRef* | Fires on user event |

**Scripting:**

- **OnScriptEnter**: Most common hook (cutscenes, spawns)
- **OnHeartbeat**: Area-of-effect damage/buffs
- **OnClick**: Used for interactive transitions

### See also

- [GFF File Format](GFF-File-Format) - Parent format and [UTT trigger](GFF-File-Format#utt-trigger) definition
- [GFF-GIT](GFF-GIT) - Game instance template (trigger placement)
- [GFF-UTD](GFF-UTD) - Doors often linked to triggers
- [NCS File Format](NCS-File-Format) - Scripts referenced by trigger hooks
- [Bioware Aurora Trigger](Bioware-Aurora-Trigger) - Official trigger specification
