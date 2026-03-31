# GFF Types: Spatial Objects

This page groups related GFF-based resource types for convenient reference. Each section below documents a specific GFF type used in KotOR I and II.

## Contents

- [UTD — Door](#utd)
- [UTP — Placeable](#utp)
- [UTT — Trigger](#utt)
- [UTE — Encounter](#ute)
- [UTS — Sound](#uts)
- [UTW — Waypoint](#utw)
- [PTH — Path](#pth)

---

<a id="utd"></a>

# UTD (Door)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTD files define [door templates](GFF-File-Format#utd-door) for all interactive doors in the game world. Doors can be locked, require keys, have hit points, conversations, and various gameplay interactions. UTD files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Door/Placeable format specification, see [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-Spatial-and-Interactive#doorplaceablegff).

**For mod developers:**

- To modify door templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:**

- [genericdoors.2da](2DA-File-Format)
- [traps.2da](2DA-File-Format#traps2da)
- [GFF-UTP](GFF-Spatial-Objects#utp)
- [KEY](KEY-File-Format)
- [NCS](NCS-File-Format)
- [DLG](GFF-Creature-and-Dialogue#dlg)
- [MDL](MDL-MDX-File-Format)

## References

**PyKotor:**

- [`utd.py` `UTD` L18+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py#L18) — in-memory door template (locks, keys, traps, scripts)
- [`construct_utd` L396+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py#L396)
- [`read_utd` L546+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py#L546)
- [`write_utd` L555+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py#L555) — GFF ↔ `UTD` round-trip
- [`gff_data.py` `GFFContent.UTD` L151](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L151) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTD shares door/placeable patterns with UTP):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Door scripting and trap wiring appear in mod threads. See:

- [NSS — Actions](NSS-File-Format#actions) (door scripting functions)
- [Home — Community sources](Home#community-sources-and-archives)

**UTD fields** stay anchored here + BioWare + PyKotor.

## Core Identity fields

| field | type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this door |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique tag for script references |
| `LocName` | [CExoLocString](GFF-File-Format#gff-data-types) | Door name (localized) |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | Door description |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Door Appearance & type

| field | type | Description |
| ----- | ---- | ----------- |
| `Appearance` | UInt32 | Index into `genericdoors.2da` |
| `GenericType` | UInt32 | Generic door type category |
| `AnimationState` | [byte](GFF-File-Format#gff-data-types) | Current [animation](MDL-MDX-File-Format#animation-header) state (always 0 in templates) |

**Appearance System:**

- `genericdoors.2da` defines door assets including:

  - [models](MDL-MDX-File-Format)
  - [animations](MDL-MDX-File-Format#animation-header)
- Different appearance types support different behaviors
- Opening [animation](MDL-MDX-File-Format#animation-header) determined by appearance entry

## Locking & Security

| field | type | Description |
| ----- | ---- | ----------- |
| `Locked` | [byte](GFF-File-Format#gff-data-types) | Door is currently locked |
| `Lockable` | [byte](GFF-File-Format#gff-data-types) | Door can be locked/unlocked |
| `KeyRequired` | [byte](GFF-File-Format#gff-data-types) | Requires specific [KEY](KEY-File-Format) item |
| `KeyName` | [CExoString](GFF-File-Format#gff-data-types) | Tag of required [KEY](KEY-File-Format) item |
| `AutoRemoveKey` | [byte](GFF-File-Format#gff-data-types) | [KEY](KEY-File-Format) consumed on use |
| `OpenLockDC` | [byte](GFF-File-Format#gff-data-types) | Security skill DC to pick lock |
| `CloseLockDC` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Security skill DC to lock door |

**Lock Mechanics:**

- **Locked**: Door cannot be opened normally
- **KeyRequired**: Must have [KEY](KEY-File-Format) in inventory
- **OpenLockDC**: Player rolls Security skill vs. DC
- **AutoRemoveKey**: [KEY](KEY-File-Format) destroyed after successful use

## Hit Points & Durability

| field | type | Description |
| ----- | ---- | ----------- |
| `HP` | [int16](GFF-File-Format#gff-data-types) | Maximum hit points |
| `CurrentHP` | [int16](GFF-File-Format#gff-data-types) | Current hit points |
| `Hardness` | [byte](GFF-File-Format#gff-data-types) | Damage reduction |
| `Min1HP` (KotOR2) | [byte](GFF-File-Format#gff-data-types) | Cannot drop below 1 HP |
| `Fort` | [byte](GFF-File-Format#gff-data-types) | Fortitude save (always 0) |
| `Ref` | [byte](GFF-File-Format#gff-data-types) | Reflex save (always 0) |
| `Will` | [byte](GFF-File-Format#gff-data-types) | Will save (always 0) |

**Destructible Doors:**

- Doors with HP can be attacked and destroyed
- **Hardness** reduces each hit's damage
- **Min1HP** prevents destruction (plot doors)
- Save values unused in KotOR

## Interaction & Behavior

| field | type | Description |
| ----- | ---- | ----------- |
| `Plot` | [byte](GFF-File-Format#gff-data-types) | Plot-critical (cannot be destroyed) |
| `Static` | [byte](GFF-File-Format#gff-data-types) | Door is static geometry (no interaction) |
| `Interruptable` | [byte](GFF-File-Format#gff-data-types) | Opening can be interrupted |
| `Conversation` | *ResRef* | Dialog file when used |
| `Faction` | [word](GFF-File-Format#gff-data-types) | Faction identifier |
| `AnimationState` | [byte](GFF-File-Format#gff-data-types) | Starting animation (0=closed, other values unused) |

**Conversation Doors:**

- When clicked, triggers dialogue instead of opening
- Useful for password entry, NPC interactions
- Dialog can conditionally open door via script

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `OnOpen` | *ResRef* | Fires when door opens |
| `OnClose` | *ResRef* | Fires when door closes |
| `OnClosed` | *ResRef* | Fires after door finishes closing |
| `OnDamaged` | *ResRef* | Fires when door takes damage |
| `OnDeath` | *ResRef* | Fires when door is destroyed |
| `OnDisarm` | *ResRef* | Fires when trap is disarmed |
| `OnHeartbeat` | *ResRef* | Fires periodically |
| `OnLock` | *ResRef* | Fires when door is locked |
| `OnMeleeAttacked` | *ResRef* | Fires when attacked in melee |
| `OnSpellCastAt` | *ResRef* | Fires when spell cast at door |
| `OnUnlock` | *ResRef* | Fires when door is unlocked |
| `OnUserDefined` | *ResRef* | Fires on user-defined events |
| `OnClick` | *ResRef* | Fires when clicked |
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
| `TrapType` | [byte](GFF-File-Format#gff-data-types) | Index into `traps.2da` |

**Trap Mechanics:**

1. **Detection**: Player rolls Awareness vs. `TrapDetectDC`
2. **Disarm**: Player rolls Security vs. `DisarmDC`
3. **Trigger**: If not detected/disarmed, trap fires on door use
4. **One-Shot**: Trap disabled after first trigger

## Load-Bearing Doors (KotOR2)

| field | type | Description |
| ----- | ---- | ----------- |
| `LoadScreenID` (KotOR2) | Word | Loading screen to show |
| `LinkedTo` (KotOR2) | [CExoString](GFF-File-Format#gff-data-types) | Destination module tag |
| `LinkedToFlags` (KotOR2) | [byte](https://en.wikipedia.org/wiki/Byte) | Transition behavior flags |
| `LinkedToModule` (KotOR2) | *ResRef* | Destination module *ResRef* |
| `TransitionDestin` (KotOR2) | [CExoLocString](GFF-File-Format#gff-data-types) | Destination label |

**Transition System:**

- Doors can load new modules/areas
- Loading screen displayed during transition
- Linked destination defines spawn point

## Appearance Customization

| field | type | Description |
| ----- | ---- | ----------- |
| `PortraitId` | [word](GFF-File-Format#gff-data-types) | Portrait icon identifier |
| `PaletteID` | [byte](GFF-File-Format#gff-data-types) | Toolset palette category |

**Visual Representation:**

- `Appearance` determines 3D [model](MDL-MDX-File-Format)
- Some doors have customizable [textures](TPC-File-Format)
- Portrait used in UI elements

## Implementation Notes

**Door State Machine:**

Doors maintain runtime state:

1. **Closed**: Default state, blocking
2. **Opening**: [animation](MDL-MDX-File-Format#animation-header) playing, becoming non-blocking
3. **Open**: Fully open, non-blocking
4. **Closing**: [animation](MDL-MDX-File-Format#animation-header) playing, becoming blocking
5. **Locked**: Closed and cannot open
6. **Destroyed**: Hit points depleted, permanently open

**Opening Sequence:**

1. Player clicks door
2. If conversation set, start dialog
3. If locked, check for [KEY](KEY-File-Format) or Security skill
4. If trapped, check for detection/disarm
5. Fire `OnOpen` script
6. Play opening [animation](MDL-MDX-File-Format#animation-header)
7. Transition to "open" state

**Locking System:**

- **Lockable=0**: Door cannot be locked (always opens)
- **Locked=1, KeyRequired=1**: Must have specific [KEY](KEY-File-Format)
- **Locked=1, OpenLockDC>0**: Can pick lock with Security skill
- **Locked=1, KeyRequired=0, OpenLockDC=0**: Locked via script only

**Common Door types:**

**Standard Doors:**

- Simple open/close
- No lock, HP, or trap
- Used for interior navigation

**Locked Doors:**

- Requires [KEY](KEY-File-Format) or Security skill
- Quest progression gates
- May have conversation for passwords

**Destructible Doors:**

- Have HP and Hardness
- Can be bashed down
- Alternative to lockpicking

**Trapped Doors:**

- Trigger trap on opening
- Require detection and disarming
- Often in hostile areas

**Transition Doors:**

- Load new modules/areas
- Show loading screens
- Used for major location changes

**Conversation Doors:**

- Trigger dialog on click
- May open after conversation
- Used for password entry, riddles

## See also

- [GFF File Format](GFF-File-Format) - Generic format underlying UTD
- [GFF-UTP (Placeable)](GFF-Spatial-Objects#utp) - Placeable templates (shared lock/trap behavior)
- [2DA traps](2DA-File-Format#traps2da) - Trap definitions; genericdoors.2da for door appearance
- [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-Spatial-and-Interactive#doorplaceablegff) - Official specification


---

<a id="utp"></a>

# UTP (Placeable)

Part of the [GFF File Format Documentation](GFF-File-Format).

[UTP files](GFF-File-Format#utp-placeable) define [placeable object templates](GFF-File-Format#utp-placeable) including containers, furniture, switches, workbenches, and interactive environmental objects. [Placeables](GFF-File-Format#utp-placeable) can have inventories, be destroyed, locked, trapped, and trigger [scripts](NCS-File-Format). UTP files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Door/Placeable format specification, see [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-Spatial-and-Interactive#doorplaceablegff).

**For mod developers:**

- To modify placeable templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:**

- [2DA placeables](2DA-File-Format#placeables2da)
- [2DA traps](2DA-File-Format#traps2da)
- [GFF-UTI](GFF-Items-and-Economy#uti)
- [GFF-UTD](GFF-Spatial-Objects#utd)
- [KEY](KEY-File-Format)
- [NCS](NCS-File-Format)
- [DLG](GFF-Creature-and-Dialogue#dlg)
- [MDL](MDL-MDX-File-Format)

## References

**PyKotor:**

- [`utp.py` `UTP` L19+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L19) — in-memory placeable template (inventory, traps, HP, scripts)
- [`construct_utp` L227+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L227)
- [`read_utp` L405+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L405)
- [`write_utp` L414+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L414) — GFF ↔ `UTP` round-trip
- [`gff_data.py` `GFFContent.UTP` L154](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L154) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTP shares door/placeable patterns with UTD):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Placeable and container modding threads on Deadly Stream complement [GFF-GIT](GFF-Module-and-Area#git) placement—see [Home — Community sources](Home#community-sources-and-archives). **UTP fields** follow this page + BioWare + PyKotor.

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
| `Appearance` | UInt32 | Index into [`placeables.2da`](2DA-File-Format#placeables2da) |
| `Type` | [byte](GFF-File-Format#gff-data-types) | Placeable type category |
| `AnimationState` | [byte](GFF-File-Format#gff-data-types) | Current [animation](MDL-MDX-File-Format#animation-header) state |

**Appearance System:**

- [`placeables.2da`](2DA-File-Format#placeables2da) defines [models](MDL-MDX-File-Format), lighting, and sounds
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
| `Conversation` | *ResRef* | [Dialog](GFF-Creature-and-Dialogue#dlg) file when used |
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
| `TrapType` | [byte](GFF-File-Format#gff-data-types) | Index into [`traps.2da`](2DA-File-Format#traps2da) ([trap definitions](2DA-File-Format#traps2da)) |

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
- Light properties defined in [`placeables.2da`](2DA-File-Format#placeables2da)

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
2. **Appearance Setup**: [model](MDL-MDX-File-Format) loaded from [`placeables.2da`](2DA-File-Format#placeables2da)
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
- Conversation property set to [DLG](GFF-Creature-and-Dialogue#dlg) file
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
- [GFF-UTD (Door)](GFF-Spatial-Objects#utd) - Door templates (shared lock/trap behavior)
- [GFF-UTI (Item)](GFF-Items-and-Economy#uti) - Item templates in placeable inventory
- Lookup tables:

  - [2DA placeables](2DA-File-Format#placeables2da)
  - [2DA traps](2DA-File-Format#traps2da)
- [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-Spatial-and-Interactive#doorplaceablegff) - Official specification


---

<a id="utt"></a>

# UTT (Trigger)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTT files define [trigger templates](GFF-File-Format#utt-trigger) for invisible volumes that fire scripts when entered, exited, or used. Triggers are essential for area transitions, cutscenes, traps, and game logic. UTT files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Trigger format specification, see [Bioware Aurora Trigger Format](Bioware-Aurora-Spatial-and-Interactive#trigger).

**For mod developers:**

- To modify trigger templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`utt.py` `UTT` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L17) — in-memory trigger model (transitions, traps, script hooks)
- [`construct_utt` L148+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L148)
- [`read_utt` L265+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L265)
- [`write_utt` L274+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py#L274) — GFF ↔ `UTT` round-trip
- [`gff_data.py` `GFFContent.UTT` L157](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L157) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTT as GFF):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Area transitions and trap behavior are discussed across forums. See:

- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)
- [Home — Community sources](Home#community-sources-and-archives)

Use community write-ups for **playtesting and tooling**; **UTT fields** follow this page + BioWare + PyKotor.

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
- [GFF-GIT](GFF-Module-and-Area#git) - Game instance template (trigger placement)
- [GFF-UTD](GFF-Spatial-Objects#utd) - Doors often linked to triggers
- [NCS File Format](NCS-File-Format) - Scripts referenced by trigger hooks
- [Bioware Aurora Trigger](Bioware-Aurora-Spatial-and-Interactive#trigger) - Official trigger specification


---

<a id="ute"></a>

# UTE (Encounter)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTE files define [encounter templates](GFF-File-Format#ute-encounter) which spawn creatures when triggered by the player. Encounters handle spawning logic, difficulty scaling, respawning, and faction settings for groups of enemies or neutral creatures. UTE files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Encounter format specification, see [Bioware Aurora Encounter Format](Bioware-Aurora-Spatial-and-Interactive#encounter).

**For mod developers:**

- To modify encounter templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`ute.py` `UTE` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L17) — in-memory encounter model (creature list, spawn options, scripts)
- [`construct_ute` L219+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L219)
- [`read_ute` L329+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L329)
- [`write_ute` L338+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/ute.py#L338) — GFF ↔ `UTE` round-trip
- [`gff_data.py` `GFFContent.UTE` L152](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L152) — four-character GFF type id (see also `GFFListSemanticConfig` for `CreatureList` in the same file)
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTE as GFF):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
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

- [GFF File Format](GFF-File-Format) -- Parent GFF container
- [UTE encounter](GFF-File-Format#ute-encounter) -- Field glossary inside the parent format page
- [GFF-GIT](GFF-Module-and-Area#git) - Game instance template (encounter placement)
- [GFF-UTW](GFF-Spatial-Objects#utw) - Waypoints used as spawn points
- [GFF-UTC](GFF-Creature-and-Dialogue#utc) - Creature templates spawned by encounters
- [Bioware Aurora Encounter](Bioware-Aurora-Spatial-and-Interactive#encounter) - Official encounter specification


---

<a id="uts"></a>

# UTS (Sound)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTS files define [sound object templates](GFF-File-Format#uts-sound) for ambient and environmental audio. These can be positional 3D sounds or global stereo sounds, with looping, randomization, and volume control. UTS files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Sound Object format specification, see [Bioware Aurora Sound Object Format](Bioware-Aurora-Spatial-and-Interactive#soundobject).

**For mod developers:**

- To modify sound blueprints in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`uts.py` `UTS` L18+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L18) — in-memory sound-object model (playback, 3D params, sound list)
- [`construct_uts` L187+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L187)
- [`read_uts` L286+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L286)
- [`write_uts` L295+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uts.py#L295) — GFF ↔ `UTS` round-trip
- [`gff_data.py` `GFFContent.UTS` L155](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L155) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTS as GFF):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Ambient audio and WAV/MP3 packaging threads appear on Deadly Stream and archives. See:

- [WAV-File-Format](WAV-File-Format)
- [Home — Community sources](Home#community-sources-and-archives)

Forum posts explain **workflow**; **UTS field tables** stay anchored here + BioWare + PyKotor.

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
| `Sounds` | List | List of audio files to play ([WAV](WAV-File-Format) or MP3) |

**Sounds Struct fields:**

- `Sound` (*ResRef*): Audio file resource

**Randomization:**

- If `Random=1`, engine picks one sound from list each interval
- Allows for varied ambience (e.g., 5 different bird calls)

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [Bioware-Aurora-SoundObject](Bioware-Aurora-Spatial-and-Interactive#soundobject) -- Aurora sound spec
- [WAV-File-Format](WAV-File-Format) -- Audio resources
- [GFF-GIT](GFF-Module-and-Area#git) -- Sound instances in areas
- [KEY-File-Format](KEY-File-Format) -- Resource resolution


---

<a id="utw"></a>

# UTW (Waypoint)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTW files define [waypoint templates](GFF-File-Format#utw-waypoint). Waypoints are invisible markers used for spawn points, navigation targets, map notes, and reference points for scripts. UTW files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Waypoint format specification, see [Bioware Aurora Waypoint Format](Bioware-Aurora-Spatial-and-Interactive#waypoint).

**For mod developers:**

- To modify waypoint templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding information, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

## References

**PyKotor:**

- [`utw.py` `UTW` L17+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L17) — in-memory waypoint model (map notes, tags, links)
- [`construct_utw` L115+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L115)
- [`read_utw` L183+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L183)
- [`write_utw` L192+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utw.py#L192) — GFF ↔ `UTW` round-trip
- [`gff_data.py` `GFFContent.UTW` L158](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L158) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (UTW as GFF):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community context (workflow):** Waypoint and map-pin behavior is a common module-design topic. See:

- [GFF-GIT](GFF-Module-and-Area#git)
- [Home — Community sources](Home#community-sources-and-archives)

Treat forum threads as **workflow** context; **UTW fields** follow this page + BioWare + PyKotor.

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
- [GFF-GIT](GFF-Module-and-Area#git) - Game instance template (waypoint placement)
- [GFF-UTE](GFF-Spatial-Objects#ute) - Encounters use waypoints as spawn points
- [GFF-UTD](GFF-Spatial-Objects#utd) - Doors can link to waypoint tags
- [Bioware Aurora Waypoint](Bioware-Aurora-Spatial-and-Interactive#waypoint) - Official waypoint specification


---

<a id="pth"></a>

# PTH (Path)

Part of the [GFF File Format Documentation](GFF-File-Format).

PTH files define pathfinding data for modules, distinct from the navigation mesh ([walkmesh](BWM-File-Format)). They store a network of waypoints and connections used for high-level AI navigation planning. PTH files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**For mod developers:**

- General GFF patching uses the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For Holocronworkflows, start from [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) and module/path tooling pages linked from [Home](Home).

## References

**PyKotor:**

- [`pth.py` `PTH` L19+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L19)
- [`PTHEdge` L125+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L125) — path graph model (points + connections)
- [`construct_pth` L151+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L151)
- [`read_pth` L223+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L223)
- [`write_pth` L232+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/pth.py#L232) — GFF ↔ `PTH` round-trip
- [`gff_data.py` `GFFContent.PTH` L167](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L167) — four-character GFF type id
- [`io_gff.py` `GFFBinaryReader.load` L82+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L82) — binary GFF decode (shared with other GFF types)

**Cross-reference (other implementations):**

- **[reone](https://github.com/modawan/reone)** — generic GFF reader (PTH as GFF):

  - [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp)
  - [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) — managed GFF reader/writer
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF pipeline

**Community / engine context:** PTH is **not** the walkmesh; normative walkmesh discussion stays on [BWM-File-Format](BWM-File-Format) and repo `docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md`. For player movement and AI pathing **workflow**, see [Home — Community sources](Home#community-sources-and-archives).

## Path Points

| field | type | Description |
| ----- | ---- | ----------- |
| `Path_Points` | List | List of navigation [nodes](MDL-MDX-File-Format#node-structures) |

**Path_Points Struct fields:**

- `X` (Float): X coordinate
- `Y` (Float): Y coordinate
- `Z` (Float): Z Coordinate (unused/flat)

## Path Connections

| field | type | Description |
| ----- | ---- | ----------- |
| `Path_Connections` | List | List of [edges](BWM-File-Format#edges-wok-only) between [nodes](MDL-MDX-File-Format#node-structures) |

**Path_Connections Struct fields:**

- `Path_Source` (Int): index of source point
- `Path_Dest` (Int): index of destination point

## Usage

- **AI Navigation**: Used by NPCs to plot paths across large distances or complex areas where straight-line [walkmesh](BWM-File-Format) navigation fails.
- **Legacy Support**: Often redundant in modern engines with navigation [meshes](MDL-MDX-File-Format#trimesh-header), but used in Aurora/Odyssey for optimization.
- **Editor**: Visualized as a web of lines connecting [nodes](MDL-MDX-File-Format#node-structures).

### See also

- [GFF-File-Format](GFF-File-Format) -- GFF structure
- [GFF-ARE](GFF-Module-and-Area#are) -- Area and path resolution
- [BWM-File-Format](BWM-File-Format) -- Walkmesh and edges
- [GFF-UTW](GFF-Spatial-Objects#utw) -- Waypoints
- [KEY-File-Format](KEY-File-Format) -- Resource resolution

---


---
