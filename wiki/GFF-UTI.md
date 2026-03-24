# UTI (Item)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTI files define [item templates](GFF-File-Format#uti-item) for all objects in creature inventories, containers, and stores. Items range from weapons and armor to quest items, upgrades, and consumables. UTI files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Item format specification, see [Bioware Aurora Item Format](Bioware-Aurora-Item).

**For mod developers:** To modify GFF/UTI files in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** UTI fields reference [2DA files](2DA-File-Format) ([baseitems.2da](2DA-File-Format#baseitems2da), [itempropdef.2da](2DA-File-Format#itempropdef2da)), [TLK](TLK-File-Format) for localized names, and [MDL](MDL-MDX-File-Format)/[TPC](TPC-File-Format) for [model](MDL-MDX-File-Format) and [texture](TPC-File-Format) variants.

## References

**PyKotor:**

- [`uti.py` `UTI` L22+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L22) — UTI [GFF](GFF-File-Format) field model and `read_uti` / `write_uti` helpers in the same module

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/uti.py) - Item (UTI) editor

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — C++ GFF reader (UTI uses generic GFF structure)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — .NET GFF reader/writer (UTI uses generic GFF structure)
- **[PyKotor](https://github.com/OldRepublicDevs/PyKotor)** (binary GFF): [`GFFBinaryReader.load` L79+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L79) — same pipeline as other GFF types
- **[xoreos](https://github.com/xoreos/xoreos)** — generic Aurora GFF; UTI loaded as GFF in engine

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this item |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocalizedName` | [CExoLocString](GFF-File-Format#gff-data-types) | Item name (localized) |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | Generic description |
| `DescIdentified` | [CExoLocString](GFF-File-Format#gff-data-types) | Description when identified |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Base Item Configuration

| field | type | Description |
| ----- | ---- | ----------- |
| `BaseItem` | [int32](GFF-File-Format#gff-data-types) | Index into [`baseitems.2da`](2DA-File-Format#baseitems2da) (defines item type) |
| `Cost` | UInt32 | Base value in credits |
| `AddCost` | UInt32 | Additional cost from properties |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical item (cannot be sold/destroyed) |
| `Charges` | [byte](GFF-File-Format#gff-data-types) | Number of uses remaining |
| `StackSize` | [word](GFF-File-Format#gff-data-types) | Current stack quantity |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) variation index (1-99) |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body variation for armor (1-9) |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](TPC-File-Format) variation for armor (1-9) |

**BaseItem types** (from [`baseitems.2da`](2DA-baseitems)):

- **0-10**: Various weapon types (shortsword, longsword, blaster, etc.)
- **11-30**: Armor types and shields
- **31-50**: Quest items, grenades, medical supplies
- **51-70**: Upgrades, armbands, belts
- **71-90**: Droid equipment, special items
- **91+**: KotOR2-specific items

## Item Properties

| field | type | Description |
| ----- | ---- | ----------- |
| `PropertiesList` | [List](GFF-File-Format#gff-data-types) | Item properties and enchantments |
| `Upgradable` | [byte](GFF-File-Format#gff-data-types) | Can accept upgrades (KotOR1 only) |
| `UpgradeLevel` | [byte](GFF-File-Format#gff-data-types) | Current upgrade tier (KotOR2 only) |

**PropertiesList Struct fields:**

- `PropertyName` ([word](GFF-File-Format#gff-data-types)): Index into [`itempropdef.2da`](2DA-File-Format#itempropdef2da)
- `Subtype` ([word](GFF-File-Format#gff-data-types)): Property subtype/category
- `CostTable` ([byte](GFF-File-Format#gff-data-types)): Cost table index
- `CostValue` ([word](GFF-File-Format#gff-data-types)): Cost value
- `Param1` ([byte](GFF-File-Format#gff-data-types)): First parameter
- `Param1Value` ([byte](GFF-File-Format#gff-data-types)): First parameter value
- `ChanceAppear` ([byte](GFF-File-Format#gff-data-types)): Percentage chance to appear (random loot)
- `UsesPerDay` ([byte](GFF-File-Format#gff-data-types)): Daily usage limit (0 = unlimited)
- `UsesLeft` ([byte](GFF-File-Format#gff-data-types)): Remaining uses for today

**Common Item Properties:**

- **Attack Bonus**: +1 to +12 attack rolls
- **Damage Bonus**: Additional damage dice
- **Ability Bonus**: +1 to +12 to ability scores
- **Damage Resistance**: Reduce damage by amount/percentage
- **Saving Throw Bonus**: +1 to +20 to saves
- **Skill Bonus**: +1 to +50 to skills
- **Immunity**: Immunity to damage type or condition
- **On Hit**: Cast spell/effect on successful hit
- **Keen**: Expanded critical threat range
- **Massive Criticals**: Bonus damage on critical hit

## Weapon-Specific fields

| field | type | Description |
| ----- | ---- | ----------- |
| `WeaponColor` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Blade color for lightsabers |
| `WeaponWhoosh` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Whoosh sound type |

**Lightsaber colors** (KotOR2 `WeaponColor`):

- 0: Blue, 1: Yellow, 2: Green, 3: Red
- 4: Violet, 5: Orange, 6: Cyan, 7: Silver
- 8: White, 9: Viridian, 10: Bronze

## Armor-Specific fields

| field | type | Description |
| ----- | ---- | ----------- |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) variation (1-9) |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](TPC-File-Format) variation (1-9) |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | [model](MDL-MDX-File-Format) type (typically 1-3) |
| `ArmorRulesType` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Armor class category |

**Armor [model](MDL-MDX-File-Format) Variations:**

- **Body + [texture](TPC-File-Format) Variation**: Creates visual diversity
- Armor adapts to wearer's body type and gender
- `appearance.2da` defines valid combinations

## Quest & Special Items

| field | type | Description |
| ----- | ---- | ----------- |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Cannot be sold or destroyed |
| `Stolen` | [byte](GFF-File-Format#gff-data-types) | Marked as stolen |
| `Cursed` | [byte](GFF-File-Format#gff-data-types) | Cannot be unequipped |
| `Identified` | [byte](GFF-File-Format#gff-data-types) | Player has identified the item |

**Plot Item Behavior:**

- Immune to destruction/selling
- Often required for quest completion
- Can have special script interactions

## Upgrade System (KotOR1)

| field | type | Description |
| ----- | ---- | ----------- |
| `Upgradable` | [byte](GFF-File-Format#gff-data-types) | Item accepts upgrade items |

**Upgrade Mechanism:**

- Weapon/armor can have upgrade slots
- Player applies upgrade items to base item
- Properties from upgrade merge into base
- Referenced in `upgradetypes.2da`

## Upgrade System (KotOR2 Enhanced)

| field | type | Description |
| ----- | ---- | ----------- |
| `UpgradeLevel` | [byte](GFF-File-Format#gff-data-types) | Current upgrade tier (0-2) |
| `WeaponColor` | [byte](GFF-File-Format#gff-data-types) | Lightsaber blade color |
| `WeaponWhoosh` | [byte](GFF-File-Format#gff-data-types) | Swing sound type |
| `ArmorRulesType` | [byte](GFF-File-Format#gff-data-types) | Armor restriction category |

**KotOR2 Upgrade Slots:**

- Weapons can have multiple upgrade slots
- Each slot has specific type restrictions
- Lightsabers get color customization
- Armor upgrades affect appearance

## Visual & Audio

| field | type | Description |
| ----- | ---- | ----------- |
| `ModelVariation` | [byte](GFF-File-Format#gff-data-types) | Base [model](MDL-MDX-File-Format) index |
| `BodyVariation` | [byte](GFF-File-Format#gff-data-types) | Body [model](MDL-MDX-File-Format) for armor |
| `TextureVar` | [byte](GFF-File-Format#gff-data-types) | [texture](TPC-File-Format) variant |

**[model](MDL-MDX-File-Format) Resolution:**

1. Engine looks up `BaseItem` in [`baseitems.2da`](2DA-baseitems)
2. Retrieves [model](MDL-MDX-File-Format) prefix (e.g., `w_lghtsbr`)
3. Appends variations: `w_lghtsbr_001.mdl`
4. [textures](TPC-File-Format) follow similar pattern

## Palette & Editor

| field | type | Description |
| ----- | ---- | ----------- |
| `PaletteID` | [byte](GFF-File-Format#gff-data-types) | Toolset palette category |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Designer notes/documentation |

**Toolset Integration:**

- `PaletteID` organizes items in editor
- Does not affect gameplay
- Used for content creation workflow

## Implementation Notes

**Item Instantiation:**

1. **Template Loading**: [GFF](GFF-File-Format) structure parsed from [UTI](GFF-File-Format#uti-item)
2. **Property Application**: PropertiesList merged into item
3. **Cost Calculation**: Base cost + AddCost + property costs
4. **Visual Setup**: [model](MDL-MDX-File-Format)/[texture](TPC-File-Format) variants resolved
5. **Stack Handling**: StackSize determines inventory behavior

**Property System:**

- Properties defined in [`itempropdef.2da`](2DA-itempropdef)
- Each property has cost formula
- Properties stack or override based on type
- Engine recalculates effects when equipped

**Performance Optimization:**

- Simple items (no properties) load fastest
- Complex property lists increase spawn time
- Stack-based items share template data
- Unique items (non-stackable) require instance data

**Common Item Categories:**

**Weapons:**

- Melee: lightsabers, swords, vibroblades
- Ranged: blasters, rifles, heavy weapons
- Properties: damage, attack bonus, critical

**Armor:**

- Light, Medium, Heavy classes
- Robes (Force user specific)
- Properties: AC bonus, resistance, ability boosts

**Upgrades:**

- Weapon: Power crystals, energy cells, lens
- Armor: Overlays, underlays, plates
- Applied via crafting interface

**Consumables:**

- Medpacs: Restore health
- Stimulants: Temporary bonuses
- Grenades: Area damage/effects
- Single-use or limited charges

**Quest Items:**

- Plot-flagged, cannot be lost
- Often no combat value
- Trigger scripted events

**Droid Equipment:**

- Special items for droid party members
- Sensors, shields, weapons
- Different slot types than organic characters

## See also

- [GFF File Format](GFF-File-Format) - Binary layout and data types
- [baseitems.2da](2DA-File-Format#baseitems2da) - Item type definitions
- [itempropdef.2da](2DA-File-Format#itempropdef2da) - Item property definitions
- [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax) - Modding GFF/UTI with TSLPatcher
- [Bioware Aurora Item Format](Bioware-Aurora-Item) - Official BioWare specification
