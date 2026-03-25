# UTP (Placeable)

Part of the [GFF File Format Documentation](GFF-File-Format).

[UTP files](GFF-File-Format#utp-placeable) define [placeable object templates](GFF-File-Format#utp-placeable) including containers, furniture, switches, workbenches, and interactive environmental objects. [Placeables](GFF-File-Format#utp-placeable) can have inventories, be destroyed, locked, trapped, and trigger [scripts](NCS-File-Format). UTP files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Door/Placeable format specification, see [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-DoorPlaceableGFF).

**For mod developers:** To modify placeable templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax). For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:** UTP references [2DA placeables](2DA-placeables), [2DA traps](2DA-traps), [GFF-UTI](GFF-UTI), [GFF-UTD](GFF-UTD), [KEY](KEY-File-Format), [NCS](NCS-File-Format), [DLG](GFF-DLG), and [MDL](MDL-MDX-File-Format).

## References

**PyKotor:**

- [`utp.py` `UTP` L19+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L19) — in-memory placeable template (inventory, traps, HP, scripts)
- [`construct_utp` L227+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L227), [`read_utp` L405+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L405), [`write_utp` L414+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L414) — GFF ↔ `UTP` round-trip
- [`gff_data.py` `GFFContent.UTP` L154](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L154) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)**: [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp), [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp) — generic GFF reader (UTP shares door/placeable patterns with UTD)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Placeable and container modding threads on Deadly Stream complement [GFF-GIT](GFF-GIT) placement—see [Home — Community sources](Home#community-sources-and-archives). **UTP fields** follow this page + BioWare + PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this placeable |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocName` | [CExoLocString](GFF-File-Format#gff-data-types) | Placeable name (localized) |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | Placeable description |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Appearance & type

| field | type | Description |
| ----- | ---- | ----------- |
| `Appearance` | UInt32 | Index into [`placeables.2da`](2DA-placeables) |
| `Type` | [byte](GFF-File-Format#gff-data-types) | Placeable type category |
| `AnimationState` | [byte](GFF-File-Format#gff-data-types) | Current [animation](MDL-MDX-File-Format#animation-header) state |

**Appearance System:**

- [`placeables.2da`](2DA-placeables) defines [models](MDL-MDX-File-Format), lighting, and sounds
- Appearance determines visual [model](MDL-MDX-File-Format) and interaction [animation](MDL-MDX-File-Format#animation-header)
- type influences behavior (container, switch, generic)

## Inventory System

| field | type | Description |
| ----- | ---- | ----------- |
| `HasInventory` | [byte](GFF-File-Format#gff-data-types) | Placeable contains items |
| `ItemList` | [List](GFF-File-Format#gff-data-types) | Items in inventory |
| `BodyBag` | [byte](GFF-File-Format#gff-data-types) | Container for corpse loot |

**ItemList Struct fields:**

- `InventoryRes` (*ResRef*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- `Repos_PosX` ([word](GFF-File-Format#gff-data-types)): Grid X position (optional)
- `Repos_Posy` ([word](GFF-File-Format#gff-data-types)): Grid Y position (optional)
- `Dropable` ([byte](GFF-File-Format#gff-data-types)): Can drop item

**Container Behavior:**

- **HasInventory=1**: Can be looted
- **BodyBag=1**: Corpse container (special loot rules)
- ItemList populated on placeable instantiation
- Empty containers can still be interacted with

## Locking & Security

| field | type | Description |
| ----- | ---- | ----------- |
| `Locked` | [byte](GFF-File-Format#gff-data-types) | Placeable is currently locked |
| `Lockable` | [byte](GFF-File-Format#gff-data-types) | Can be locked/unlocked |
| `KeyRequired` | [byte](GFF-File-Format#gff-data-types) | Requires specific [KEY](KEY-File-Format) item |
| `KeyName` | [CExoString](GFF-File-Format#gff-data-types) | Tag of required [KEY](KEY-File-Format) [item](GFF-File-Format#uti-item) |
| `AutoRemoveKey` | [byte](GFF-File-Format#gff-data-types) | [KEY](KEY-File-Format) consumed on use |
| `OpenLockDC` | [byte](GFF-File-Format#gff-data-types) | Security skill DC to pick lock |
| `CloseLockDC` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Security DC to lock |
| `OpenLockDiff` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Additional difficulty modifier |
| `OpenLockDiffMod` (KotOR2) | [int32](GFF-File-Format#gff-data-types) | Modifier to difficulty |

**Lock Mechanics:**

- Identical to [UTD](GFF-File-Format#utd-door) door locking system
- Prevents access to inventory
- Can be picked or opened with [KEY](KEY-File-Format)

## Hit Points & Durability

| field | type | Description |
| ----- | ---- | ----------- |
| `HP` | [int16](GFF-File-Format#gff-data-types) | Maximum hit points |
| `CurrentHP` | [int16](GFF-File-Format#gff-data-types) | Current hit points |
| `Hardness` | [byte](GFF-File-Format#gff-data-types) | Damage reduction |
| `Min1HP` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Cannot drop below 1 HP |
| `Fort` | [byte](GFF-File-Format#gff-data-types) | Fortitude save (usually 0) |
| `Ref` | [byte](GFF-File-Format#gff-data-types) | Reflex save (usually 0) |
| `Will` | [byte](GFF-File-Format#gff-data-types) | Will save (usually 0) |

**Destructible Placeables:**

- Containers, crates, and terminals can have HP
- Some placeables reveal items when destroyed
- Hardness reduces incoming damage

## Interaction & Behavior

| field | type | Description |
| ----- | ---- | ----------- |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical (cannot be destroyed) |
| `Static` | [byte](GFF-File-Format#gff-data-types) | Static geometry (no interaction) |
| `Useable` | [byte](GFF-File-Format#gff-data-types) | Can be clicked/used |
| `Conversation` | *ResRef* | [Dialog](GFF-DLG) file when used |
| `Faction` | [word](GFF-File-Format#gff-data-types) | Faction identifier |
| `PartyInteract` | [byte](GFF-File-Format#gff-data-types) | Requires party member selection |
| `NotBlastable` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Immune to area damage |

**Usage Patterns:**

- **Useable=0**: Cannot be directly interacted with
- **Conversation**: Triggers dialog on use (terminals, panels)
- **PartyInteract**: Shows party selection [GUI](GFF-File-Format#gui-graphical-user-interface)
- **Static**: Pure visual element, no gameplay

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `OnClosed` | *ResRef* | Fires when container closes |
| `OnDamaged` | *ResRef* | Fires when placeable takes damage |
| `OnDeath` | *ResRef* | Fires when placeable is destroyed |
| `OnDisarm` | *ResRef* | Fires when trap is disarmed |
| `OnEndDialogue` | *ResRef* | Fires when conversation ends |
| `OnHeartbeat` | *ResRef* | Fires periodically |
| `OnInvDisturbed` | *ResRef* | Fires when inventory changed |
| `OnLock` | *ResRef* | Fires when locked |
| `OnMeleeAttacked` | *ResRef* | Fires when attacked in melee |
| `OnOpen` | *ResRef* | Fires when opened |
| `OnSpellCastAt` | *ResRef* | Fires when spell cast at placeable |
| `OnUnlock` | *ResRef* | Fires when unlocked |
| `OnUsed` | *ResRef* | Fires when used/clicked |
| `OnUserDefined` | *ResRef* | Fires on user-defined events |
| `OnFailToOpen` (KotOR2) | *ResRef* | Fires when opening fails |

## Trap System

| field | type | Description |
| ----- | ---- | ----------- |
| `TrapDetectable` | [byte](GFF-File-Format#gff-data-types) | Trap can be detected |
| `TrapDetectDC` | [byte](GFF-File-Format#gff-data-types) | Awareness DC to detect trap |
| `TrapDisarmable` | [byte](GFF-File-Format#gff-data-types) | Trap can be disarmed |
| `DisarmDC` | [byte](GFF-File-Format#gff-data-types) | Security DC to disarm trap |
| `TrapFlag` | [byte](GFF-File-Format#gff-data-types) | Trap is active |
| `TrapOneShot` | [byte](GFF-File-Format#gff-data-types) | Trap triggers only once |
| `TrapType` | [byte](GFF-File-Format#gff-data-types) | Index into [`traps.2da`](2DA-traps) ([trap definitions](2DA-traps)) |

**Trap Behavior:**

- Identical to door trap system
- Triggers on placeable use
- Common on containers and terminals

## Visual Customization

| field | type | Description |
| ----- | ---- | ----------- |
| `PortraitId` | [word](GFF-File-Format#gff-data-types) | Portrait icon identifier |
| `PaletteID` | [byte](GFF-File-Format#gff-data-types) | Toolset palette category |

**[model](MDL-MDX-File-Format) & Lighting:**

- Appearance determines [model](MDL-MDX-File-Format) and light color
- Some placeables have animated components
- Light properties defined in [`placeables.2da`](2DA-placeables)

## Implementation Notes

**Placeable Categories:**

**Containers:**

- Footlockers, crates, corpses
- Have inventory (ItemList populated)
- Can be locked, trapped, destroyed
- `HasInventory=1`, `BodyBag` flag for corpses

**Switches & Terminals:**

- Trigger scripts or conversations
- No inventory typically
- `Useable=1`, `Conversation` or scripts set
- Common for puzzle activation

**Workbenches:**

- Special placeable type for crafting
- Opens crafting interface on use
- Defined by type or Appearance

**Furniture:**

- Non-interactive decoration
- `Static=1` or `Useable=0`
- Pure visual elements

**Environmental Objects:**

- Explosive containers, power generators
- Can be destroyed with effects
- Often have HP and OnDeath scripts

**Instantiation Flow:**

1. **Template Load**: [GFF](GFF-File-Format) parsed from [UTP](GFF-File-Format#utp-placeable)
2. **Appearance Setup**: [model](MDL-MDX-File-Format) loaded from [`placeables.2da`](2DA-placeables)
3. **Inventory Population**: ItemList instantiated
4. **Lock State**: Locked status applied
5. **Trap Activation**: Trap armed if configured
6. **Script Registration**: Event handlers registered

**Container Loot:**

- ItemList defines initial inventory
- Random loot can be added via script
- OnInvDisturbed fires when items taken
- BodyBag containers have special loot rules

**Conversation Placeables:**

- Terminals, control panels, puzzle interfaces
- Conversation property set to [DLG](GFF-DLG) file
- Use triggers dialog instead of direct interaction
- Dialog can have conditional responses

**Common Placeable types:**

**Storage Containers:**

- Footlockers, crates, bins
- Standard inventory interface
- Often locked or trapped

**Corpses:**

- BodyBag flag set
- Contain enemy loot
- Disappear when looted (usually)

**Terminals:**

- Computer interfaces
- Trigger conversations or scripts
- May require Computer Use skill checks

**Switches:**

- Activate doors, puzzles, machinery
- Fire OnUsed script
- Visual feedback [animation](MDL-MDX-File-Format#animation-header)

**Workbenches:**

- Crafting interface activation
- Lab stations, upgrade benches
- Special type value

**Decorative Objects:**

- No gameplay interaction
- Static or non-useable
- Environmental detail

**Mines (Special Case):**

- Placed as placeable or creature
- Trap properties define behavior
- Can be detected and disarmed
- Trigger on proximity or interaction

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying UTP
- [GFF-UTD (Door)](GFF-UTD) - Door templates (shared lock/trap behavior)
- [GFF-UTI (Item)](GFF-UTI) - Item templates in placeable inventory
- [2DA placeables](2DA-placeables), [2DA traps](2DA-traps) - Lookup tables
- [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-DoorPlaceableGFF) - Official specification
