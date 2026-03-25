# UTE (Encounter)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTE files define [encounter templates](GFF-File-Format#ute-encounter) which spawn creatures when triggered by the player. Encounters handle spawning logic, difficulty scaling, respawning, and faction settings for groups of enemies or neutral creatures. UTE files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Encounter format specification, see [Bioware Aurora Encounter Format](Bioware-Aurora-Encounter).

**For mod developers:** To modify encounter templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`ute.py` `UTE` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L17) — in-memory encounter model (creature list, spawn options, scripts)
- [`construct_ute` L219+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L219), [`read_ute` L329+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L329), [`write_ute` L338+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L338) — GFF ↔ `UTE` round-trip
- [`gff_data.py` `GFFContent.UTE` L152](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L152) — four-character GFF type id (see also `GFFListSemanticConfig` for `CreatureList` in the same file)
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTE as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Encounter placement and spawn behavior are frequent mod topics—see [Home — Community sources](Home#community-sources-and-archives). Use threads for workflow and tooling tips; **field layout** stays anchored to this page, the BioWare spec, and PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this encounter |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocalizedName` | [CExoLocString](GFF-File-Format#gff-data-types) | Encounter name (unused in game) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Spawn Configuration

| field | type | Description |
| ----- | ---- | ----------- |
| `Active` | Byte | Encounter is currently active |
| `Difficulty` | Int | Difficulty setting (unused) |
| `DifficultyIndex` | Int | Difficulty scaling index |
| `Faction` | Word | Faction of spawned creatures |
| `MaxCreatures` | Int | Maximum concurrent creatures |
| `RecCreatures` | Int | Recommended number of creatures |
| `SpawnOption` | Int | Spawn behavior (0=Continuous, 1=Single Shot) |

**Spawn Behavior:**

- **Active**: If 0, encounter won't trigger until activated by script
- **MaxCreatures**: Hard limit on spawned entities to prevent overcrowding
- **RecCreatures**: Target number to maintain
- **SpawnOption**: Single Shot encounters fire once and disable

## Respawn Logic

| field | type | Description |
| ----- | ---- | ----------- |
| `Reset` | Byte | Encounter resets after being cleared |
| `ResetTime` | Int | Time in seconds before reset |
| `Respawns` | Int | Number of times it can respawn (-1 = infinite) |

**Respawn System:**

- Allows for renewable enemy sources
- **ResetTime**: Cooldown period after players leave area
- **Respawns**: Limits farming/grinding

## Creature List

| field | type | Description |
| ----- | ---- | ----------- |
| `CreatureList` | List | List of creatures to spawn |

**CreatureList Struct fields:**

- `*ResRef*` (*ResRef*): [UTC](GFF-File-Format#utc-creature) template to spawn
- `Appearance` (Int): Appearance type (optional override)
- `CR` (Float): Challenge Rating
- `SingleSpawn` (Byte): Unique spawn flag

**Spawn Selection:**

- Engine selects from CreatureList based on CR and difficulty
- Random selection weighted by difficulty settings

## Trigger Logic

| field | type | Description |
| ----- | ---- | ----------- |
| `PlayerOnly` | Byte | Only triggers for player (not NPCs) |
| `OnEntered` | *ResRef* | Script fires when trigger entered |
| `OnExit` | *ResRef* | Script fires when trigger exited |
| `OnExhausted` | *ResRef* | Script fires when spawns depleted |
| `OnHeartbeat` | *ResRef* | Script fires periodically |
| `OnUserDefined` | *ResRef* | Script fires on user events |

**Implementation Notes:**

- Encounters are volumes ([geometry](MDL-MDX-File-Format#geometry-header) defined in [GIT](GFF-File-Format#git-game-instance-template))
- Spawning happens when volume is entered
- Creatures spawn at specific spawn points ([UTW](GFF-File-Format#utw-waypoint)) or random locations

### See also

- [GFF File Format](GFF-File-Format) - Parent format and [UTE encounter](GFF-File-Format#ute-encounter) definition
- [GFF-GIT](GFF-GIT) - Game instance template (encounter placement)
- [GFF-UTW](GFF-UTW) - Waypoints used as spawn points
- [GFF-UTC](GFF-UTC) - Creature templates spawned by encounters
- [Bioware Aurora Encounter](Bioware-Aurora-Encounter) - Official encounter specification
