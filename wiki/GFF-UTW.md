# UTW (Waypoint)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTW files define [waypoint templates](GFF-File-Format#utw-waypoint). Waypoints are invisible markers used for spawn points, navigation targets, map notes, and reference points for scripts. UTW files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Waypoint format specification, see [Bioware Aurora Waypoint Format](Bioware-Aurora-Waypoint).

**For mod developers:** To modify waypoint templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`utw.py` `UTW` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L17) — in-memory waypoint model (map notes, tags, links)
- [`construct_utw` L115+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L115), [`read_utw` L183+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L183), [`write_utw` L192+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L192) — GFF ↔ `UTW` round-trip
- [`gff_data.py` `GFFContent.UTW` L158](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L158) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTW as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Waypoint and map-pin behavior is a common module-design topic—see [GFF-GIT](GFF-GIT) and [Home — Community sources](Home#community-sources-and-archives). Treat forum threads as **workflow** context; **UTW fields** follow this page + BioWare + PyKotor.

## Core Identity fields

| field | type | Engine default | Description |
|:------|:-----|:---------------|:------------|
| `TemplateResRef` | *ResRef* | blank | Template identifier; max 16 chars. Engine loads the matching .utw. |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | "" | Unique tag for GetObjectByTag/GetWaypointByTag and door/trigger links. Keep unique per area. |
| `LocalizedName` | [CExoLocString](GFF-File-Format#gff-data-types) | empty | Waypoint name on map and in travel menu. |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | empty | Not read by engine; toolset/legacy only. |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | "" | Developer comment; not used by the game. |

---

## Map Note Functionality

| field | type | Description |
|:------|:-----|:------------|
| `HasMapNote` | Byte | Waypoint has a map note |
| `MapNoteEnabled` | Byte | Map note is initially visible |
| `MapNote` | [CExoLocString](GFF-File-Format#gff-data-types) | Text displayed on map |

### Map Notes

- If enabled, shows text on the in-game map
- Can be enabled/disabled via script (`SetMapPinEnabled`)
- Used for quest objectives and locations

---

## Linking & Appearance

| field | type | Description |
|:------|:-----|:------------|
| `LinkedTo` | [CExoString](GFF-File-Format#gff-data-types) | Tag of linked object (unused) |
| `Appearance` | Byte | Appearance type (1=Waypoint) |
| `PaletteID` | Byte | Toolset palette category |

---

## Usage

- **Spawn Points**: `CreateObject` uses waypoint location
- **Patrols**: AI walks between waypoints
- **Teleport**: `JumpToLocation` targets waypoints
- **Transitions**: Doors/Triggers link to waypoint tags

### See also

- [GFF File Format](GFF-File-Format) - Parent format and [UTW waypoint](GFF-File-Format#utw-waypoint) definition
- [GFF-GIT](GFF-GIT) - Game instance template (waypoint placement)
- [GFF-UTE](GFF-UTE) - Encounters use waypoints as spawn points
- [GFF-UTD](GFF-UTD) - Doors can link to waypoint tags
- [Bioware Aurora Waypoint](Bioware-Aurora-Waypoint) - Official waypoint specification
