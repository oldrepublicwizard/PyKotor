# UTC (Creature)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTC files define [creature templates](GFF-File-Format#utc-creature) including NPCs, party members, enemies, and the player character. They are comprehensive [GFF files](GFF-File-Format) containing all data needed to spawn and control a creature in the game world. UTC files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Creature format specification, see [Bioware Aurora Creature Format](Bioware-Aurora-Creature).

**For mod developers:** To modify creature templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** UTC references [2DA](2DA-File-Format) (appearance, portraits, classes, feats, racialtypes, creaturespeed), [SSF](SSF-File-Format), [TLK](TLK-File-Format), [MDL](MDL-MDX-File-Format), [TPC](TPC-File-Format), and [GFF-UTI](GFF-UTI) for inventory items.

## References

**PyKotor:**

- [`utc.py` `UTC` L36+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L36) — in-memory creature model (classes, feats, inventory, appearance, scripts)
- [`construct_utc` L494+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L494), [`read_utc` L982+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L982), [`write_utc` L992+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L992) — GFF ↔ `UTC` round-trip
- [`gff_data.py` `GFFContent.UTC` L150](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L150) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**HolocronToolset:**

- [`utc.py` (creature / UTC editor)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py) — GUI for UTC fields and creature templates in modules

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTC as GFF)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Creature editing and appearance threads are common on Deadly Stream—see [Home — Community sources](Home#community-sources-and-archives). Use forums for **workflow**; **UTC field layout** follows this page, BioWare spec, and PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this creature (max 16 characters; should match UTC filename without extension) |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script/conversation references |
| `FirstName` | [CExoLocString](GFF-File-Format#gff-data-types) | Creature's first name (localized) |
| `LastName` | [CExoLocString](GFF-File-Format#gff-data-types) | Creature's last name (localized) |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Appearance & Visuals

| field | type | Description |
| ----- | ---- | ----------- |
| `Appearance_Type` | UInt32 | Index into [`appearance.2da`](2DA-appearance) |
| `PortraitId` | [word](GFF-File-Format#gff-data-types) | Index into [`portraits.2da`](2DA-portraits); 65535 (0xFFFF) = use Portrait ResRef instead |
| `Gender` | [byte](GFF-File-Format#gff-data-types) | 0=Male, 1=Female, 2=Both, 3=Other, 4=None (engine clamps values > 4 to 4) |
| `Race` | [byte](GFF-File-Format#gff-data-types) | Index into [`racialtypes.2da`](2DA-racialtypes). If value is greater than or equal to the number of rows in race.2da, the creature fails to load. |
| `SubraceIndex` | [byte](GFF-File-Format#gff-data-types) | Index into subrace.2da; refines race (e.g. subspecies). |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) variation (0-9) |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](TPC-File-Format) variation (1-9) |
| `SoundSetFile` | [word](GFF-File-Format#gff-data-types) | Index into [sound set table](SSF-File-Format) |

## Core Stats & Attributes

| field | type | Description |
| ----- | ---- | ----------- |
| `Str` | [byte](GFF-File-Format#gff-data-types) | Strength score (3-255) |
| `Dex` | [byte](GFF-File-Format#gff-data-types) | Dexterity score (3-255) |
| `Con` | [byte](GFF-File-Format#gff-data-types) | Constitution score (3-255) |
| `Int` | [byte](GFF-File-Format#gff-data-types) | Intelligence score (3-255) |
| `Wis` | [byte](GFF-File-Format#gff-data-types) | Wisdom score (3-255) |
| `Cha` | [byte](GFF-File-Format#gff-data-types) | Charisma score (3-255) |
| `HitPoints` | [int16](GFF-File-Format#gff-data-types) | Current hit points |
| `CurrentHitPoints` | [int16](GFF-File-Format#gff-data-types) | Alias for hit points |
| `MaxHitPoints` | [int16](GFF-File-Format#gff-data-types) | Maximum hit points |
| `ForcePoints` | [int16](GFF-File-Format#gff-data-types) | Current Force points (KotOR specific) |
| `CurrentForce` | [int16](GFF-File-Format#gff-data-types) | Alias for Force points |
| `MaxForcePoints` | [int16](GFF-File-Format#gff-data-types) | Maximum Force points |

## Character Progression

| field | type | Description |
| ----- | ---- | ----------- |
| `ClassList` | [List](GFF-File-Format#gff-data-types) | List of character classes with levels |
| `Experience` | UInt32 | Total experience points |
| `LevelUpStack` | [List](GFF-File-Format#gff-data-types) | Pending level-up choices |
| `SkillList` | [List](GFF-File-Format#gff-data-types) | Skill ranks (index + rank) |
| `FeatList` | [List](GFF-File-Format#gff-data-types) | Acquired feats |
| `SpecialAbilityList` | [List](GFF-File-Format#gff-data-types) | Special abilities/powers |

**ClassList Struct fields:**

- `Class` ([int32](GFF-File-Format#gff-data-types)): Index into [`classes.2da`](2DA-classes) ([class definitions](2DA-classes))
- `ClassLevel` ([int16](GFF-File-Format#gff-data-types)): Levels in this class

**SkillList Struct fields:**

- `Rank` ([byte](GFF-File-Format#gff-data-types)): Skill rank value

**FeatList Struct fields:**

- `Feat` ([word](GFF-File-Format#gff-data-types)): Index into [`feat.2da`](2DA-feat) ([feat definitions](2DA-feat))

## Combat & Behavior

| field | type | Description |
| ----- | ---- | ----------- |
| `FactionID` | [word](GFF-File-Format#gff-data-types) | Faction identifier (determines hostility) |
| `NaturalAC` | [byte](GFF-File-Format#gff-data-types) | Natural armor class bonus |
| `ChallengeRating` | float | CR for encounter calculations |
| `PerceptionRange` | [byte](GFF-File-Format#gff-data-types) | Perception distance category |
| `WalkRate` | [int32](GFF-File-Format#gff-data-types) | Row index into creaturespeed.2da; sets walk/run movement speed used for pathfinding and animation. |
| `Interruptable` | [byte](GFF-File-Format#gff-data-types) | Can be interrupted during actions |
| `NoPermDeath` | [byte](GFF-File-Format#gff-data-types) | Cannot permanently die |
| `IsPC` | [byte](GFF-File-Format#gff-data-types) | Is player character |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical (cannot die) |
| `MinOneHP` | [byte](GFF-File-Format#gff-data-types) | Cannot drop below 1 HP |
| `PartyInteract` | [byte](GFF-File-Format#gff-data-types) | Shows party selection interface |
| `Hologram` | [byte](GFF-File-Format#gff-data-types) | Rendered as hologram |

## Equipment & Inventory

| field | type | Description |
| ----- | ---- | ----------- |
| `ItemList` | [List](GFF-File-Format#gff-data-types) | Inventory items |
| `Equip_ItemList` | [List](GFF-File-Format#gff-data-types) | Equipped items with slots |
| `EquippedRes` | *ResRef* | Deprecated equipment field |

**ItemList Struct fields:**

- `InventoryRes` (*ResRef*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- `Repos_PosX` ([word](GFF-File-Format#gff-data-types)): Inventory grid X position
- `Repos_Posy` ([word](GFF-File-Format#gff-data-types)): Inventory grid Y position
- `Dropable` ([byte](GFF-File-Format#gff-data-types)): Can be dropped/removed

**Equip_ItemList Struct fields:**

- `EquippedRes` (*ResRef*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- Equipment slots reference `equipmentslots.2da`

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `ScriptAttacked` | *ResRef* | Fires when attacked |
| `ScriptDamaged` | *ResRef* | Fires when damaged |
| `ScriptDeath` | *ResRef* | Fires on death |
| `ScriptDialogue` | *ResRef* | Fires when conversation starts |
| `ScriptDisturbed` | *ResRef* | Fires when inventory disturbed |
| `ScriptEndRound` | *ResRef* | Fires at combat round end |
| `ScriptEndDialogue` | *ResRef* | Fires when conversation ends |
| `ScriptHeartbeat` | *ResRef* | Fires periodically |
| `ScriptOnBlocked` | *ResRef* | Fires when movement blocked |
| `ScriptOnNotice` | *ResRef* | Fires when notices something |
| `ScriptRested` | *ResRef* | Fires after rest |
| `ScriptSpawn` | *ResRef* | Fires on spawn |
| `ScriptSpellAt` | *ResRef* | Fires when spell cast at creature |
| `ScriptUserDefine` | *ResRef* | Fires on user-defined events |

## KotOR-Specific Features

**Alignment:**

- `GoodEvil` ([byte](GFF-File-Format#gff-data-types)): 0-100 scale (0=Dark, 100=Light)
- `LawfulChaotic` ([byte](GFF-File-Format#gff-data-types)): Unused in KotOR

**Multiplayer (Unused in KotOR):**

- `Deity` ([CExoString](GFF-File-Format#gff-data-types))
- `Subrace` ([CExoString](GFF-File-Format#gff-data-types))
- `Morale` ([byte](GFF-File-Format#gff-data-types))
- `MorealBreak` ([byte](GFF-File-Format#gff-data-types))

**Special Abilities:**

- Stored in `SpecialAbilityList` referencing `spells.2da` or feat-based abilities

## Editor reference (min/max and usage)

When editing UTCs in the Holocron Toolset, numeric fields use the following ranges (from GFF types and engine behavior):

- **TemplateResRef, Conversation, script ResRefs:** Max 16 characters (engine ResRef limit).
- **Tag:** No engine-enforced max length; keep unique per module for script lookups (e.g. `GetObjectByTag`).
- **FirstName, LastName, Comment:** Localized or plain string; no fixed max in GFF.
- **Appearance_Type, PortraitId, SoundSetFile, FactionID:** WORD (0–65535); use valid 2DA row indices.
- **Race, Gender, SubraceIndex, PerceptionRange, NaturalAC, ability scores (Str–Cha), skill Rank:** BYTE (0–255). **Race:** must be a valid row index in racialtypes.2da (0 to row count − 1); otherwise the creature fails to load. Save bonuses (fortbonus, refbonus, willbonus): SHORT (-32768–32767).
- **WalkRate:** INT; row index into creaturespeed.2da (0 to row count − 1). Invalid index can cause default or broken movement.
- **HitPoints, CurrentHitPoints, MaxHitPoints, CurrentForce, ForcePoints:** SHORT (0–32767 typical; game does not use negative HP/FP).
- **ChallengeRating:** Float (0–100 typical). **GoodEvil (alignment):** 0–100 (0=Dark, 100=Light).
- **ClassLevel:** SHORT (0–32767); typical level 1–20. **MultiplierSet (K2):** INT32; 0 = default.
- **BlindSpot (K2):** Float 0–360 degrees.

All script hooks store a ResRef to an NCS file; leave blank for no script. The toolset provides tooltips on each field describing how the game uses it and how modders can change it.

## Implementation Notes

[UTC](GFF-File-Format#utc-creature) files are loaded during module initialization or creature spawning. The engine:

1. **Reads template data** from the [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format) structure
2. **Applies appearance** based on [`appearance.2da`](2DA-appearance) ([appearance definitions](2DA-appearance)) lookup
3. **Calculates derived stats** (AC, saves, attack bonuses) from attributes and equipment
4. **Loads inventory** by instantiating [UTI](GFF-File-Format#uti-item) ([item templates](GFF-File-Format#uti-item)) templates
5. **Applies effects** from equipped items and active powers
6. **Registers scripts** ([NCS files](NCS-File-Format)) for the creature's event handlers

**Performance Considerations:**

- Complex creatures with many items/feats increase load time
- Script hooks fire frequently - keep handlers optimized
- Large SkillList/FeatList structures add memory overhead

**Common Use Cases:**

- **Party Members**: Full [UTC](GFF-File-Format#utc-creature) with all progression data, complex equipment
- **Plot NPCs**: Basic stats, specific appearance, dialogue scripts
- **Generic Enemies**: Minimal data, shared appearance, basic AI scripts
- **Vendors**: Specialized with store inventory, merchant scripts
- **Placeables As Creatures**: Invisible creatures for complex scripting

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying UTC
- [GFF-UTI (Item)](GFF-UTI) - Item templates in creature inventory
- [2DA appearance](2DA-appearance), [classes](2DA-classes), [feat](2DA-feat), [racialtypes](2DA-racialtypes) - Lookup tables
- [Bioware Aurora Creature Format](Bioware-Aurora-Creature) - Official creature specification
