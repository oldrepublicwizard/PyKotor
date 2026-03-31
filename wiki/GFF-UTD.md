# UTD (Door)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTD files define [door templates](GFF-File-Format#utd-door) for all interactive doors in the game world. Doors can be locked, require keys, have hit points, conversations, and various gameplay interactions. UTD files are loaded with the same [resource resolution order](Concepts#resource-resolution-order) as other resources (override, MOD/SAV, KEY/BIF).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Door/Placeable format specification, see [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-DoorPlaceableGFF).

**For mod developers:**

- To modify door templates in your mods, see the [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax).
- For general modding, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers).

**Related formats:**

- [genericdoors.2da](2DA-File-Format)
- [traps.2da](2DA-File-Format#traps2da)
- [GFF-UTP](GFF-UTP)
- [KEY](KEY-File-Format)
- [NCS](NCS-File-Format)
- [DLG](GFF-DLG)
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
- [GFF-UTP (Placeable)](GFF-UTP) - Placeable templates (shared lock/trap behavior)
- [2DA traps](2DA-File-Format#traps2da) - Trap definitions; genericdoors.2da for door appearance
- [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-DoorPlaceableGFF) - Official specification
