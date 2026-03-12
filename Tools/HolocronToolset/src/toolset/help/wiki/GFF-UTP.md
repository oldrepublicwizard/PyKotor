# UTP (Placeable)

Part of the [GFF File Format Documentation](GFF-File-Format).

[UTP files](GFF-File-Format#utp-placeable) define [placeable object templates](GFF-File-Format#utp-placeable) including containers, furniture, switches, workbenches, and interactive environmental objects. [Placeables](GFF-File-Format#utp-placeable) can have inventories, be destroyed, locked, trapped, and trigger [scripts](NCS-File-Format).

**Official Bioware Documentation:** For the authoritative Bioware Aurora Engine Door/Placeable format specification, see [Bioware Aurora Door/Placeable GFF Format](Bioware-Aurora-DoorPlaceableGFF).

**Reference**: [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py)

A placeable is an object that can be placed in the game world. It can be a container, a furniture, a switch, a workbench, or an interactive environmental object.

But as far as Odyssey is concerned, a door is nearly exactly the same as a placeable in memory. Probably subclasses a placeable class in their OOP src code to be honest.

## Core Identity fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TemplateResRef` | *ResRef* | Template identifier for this Placeable |
| `Tag` | [CExoString](GFF-File-Format#gff-data-types) | Unique **Tag** for script references |
| `LocName` | [CExoLocString](GFF-File-Format#gff-data-types) | *Placeable* name (localized) |
| `Description` | [CExoLocString](GFF-File-Format#gff-data-types) | *Placeable* description |
| `Comment` | [CExoString](GFF-File-Format#gff-data-types) | Developer comment/notes |

## Appearance & Type

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Appearance` | *DWord* | index into [`placeables.2da`](2DA-placeables) |
| `Type` | *Byte* | *Placeable* type category |
| `AnimationState` | *Byte* | Current [animation](MDL-MDX-File-Format#animation-header) state |

**Appearance System:**

- [`placeables.2da`](2DA-placeables) defines **[models ([MDL/MDX](MDL-MDX-File-Format))**], **[lighting](MDL-MDX-File-Format#lighting-header)**, and **[sounds](MDL-MDX-File-Format#sound-header)**
- Appearance determines visual **[model ([MDL/MDX](MDL-MDX-File-Format))**] and interaction **[animation](MDL-MDX-File-Format#animation-header)**
- Type influences behavior (container, switch, generic)

## Inventory System

| Field | Type | Description |
| ----- | ---- | ----------- |
| `HasInventory` | *[byte](GFF-File-Format#gff-data-types)* | *Placeable* contains items |
| `ItemList` | *[List](GFF-File-Format#gff-data-types)* | Items in inventory |
| `BodyBag` | *[byte](GFF-File-Format#gff-data-types)* | Container for corpse loot |

**ItemList Struct fields:**

- `InventoryRes` (*[ResRef](GFF-File-Format#gff-data-types)*): [UTI](GFF-File-Format#uti-item) template *ResRef*
- `Repos_PosX` (*[Word](GFF-File-Format#gff-data-types)*): Grid X position (optional)
- `Repos_Posy` (*[Word](GFF-File-Format#gff-data-types)*): Grid Y position (optional)
- `Dropable` (*[Byte](GFF-File-Format#gff-data-types)*): Can drop item

**Container Behavior:**

- **`HasInventory=1`**: Can be looted
- **`BodyBag=1`**: Corpse container (special loot rules)
- ItemList populated on placeable instantiation
- Empty containers can still be interacted with

## Locking & Security

| field | type | Description |
| ----- | ---- | ----------- |
| `Locked` | *[Byte](GFF-File-Format#gff-data-types)* | Placeable is currently locked |
| `Lockable` | *[Byte](GFF-File-Format#gff-data-types)* | Can be locked/unlocked |
| `KeyRequired` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Requires specific [KEY](KEY-File-Format) item |
| `KeyName` | [CExoString](GFF-File-Format#gff-data-types) | Tag of required [KEY](KEY-File-Format) item. |
| `AutoRemoveKey` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | [KEY](KEY-File-Format) consumed on use |
| `OpenLockDC` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* | Security skill DC to pick lock |
| `CloseLockDC` (KotOR2) | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | Security DC to lock |
| `OpenLockDiff` (KotOR2) | *[Int](GFF-File-Format#gff-data-types)* *Integer* (signed) | Additional difficulty modifier |
| `OpenLockDiffMod` (KotOR2) | *[Int](GFF-File-Format#gff-data-types)* *Integer* (signed) | Modifier to difficulty |

**Lock Mechanics:**

- Identical to **[UTD](GFF-UTD)** door locking system
- Prevents access to inventory
- Can be picked or opened with **[KEY](KEY-File-Format)**

## Hit Points & Durability

| Field | Type | Description |
| ----- | ---- | ----------- |
| `HP` | *[Short](GFF-File-Format#gff-data-types)* | Maximum hit points |
| `CurrentHP` | *[Short](GFF-File-Format#gff-data-types)* | Current hit points |
| `Hardness` | *[Byte](GFF-File-Format#gff-data-types)* | Damage reduction |
| `Min1HP` (KotOR2) | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Cannot drop below 1 HP |
| `Fort` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | *Fortitude* save (usually 0) |
| `Ref` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | *Reflex* save (usually 0) |
| `Will` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | *Will* save (usually 0) |

**Destructible Placeables:**

- Containers, crates, and terminals can have **HP**
- Some placeables reveal items when destroyed
- **Hardness** reduces incoming damage

## Interaction & Behavior

| Field | Type | Description |
| ----- | ---- | ----------- |
| `Plot` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Plot-critical (cannot be destroyed). |
| `Static` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Static geometry (no interaction). |
| `Useable` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Can be clicked/used. |
| `Conversation` | *ResRef* | [Dialog](GFF-DLG) file when used. |
| `Faction` | *Word* | Faction identifier. |
| `PartyInteract` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Requires party member selection. |
| `NotBlastable` (KotOR2) | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Immune to area damage. |

**Usage Patterns:**

- **`Useable=0`**: Cannot be directly interacted with
- **`Conversation`**: Triggers dialog on use (terminals, panels)
- **`PartyInteract`**: Shows party selection [GUI](GFF-File-Format#gui-graphical-user-interface)
- **`Static`**: Pure visual element, no gameplay

## Script Hooks

| field | type | Description |
| ----- | ---- | ----------- |
| `OnClosed` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when container closes. |
| `OnDamaged` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when placeable takes damage. |
| `OnDeath` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when placeable is destroyed. |
| `OnDisarm` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when trap is disarmed. |
| `OnEndDialogue` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when conversation ends. |
| `OnHeartbeat` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires periodically. |
| `OnInvDisturbed` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when inventory changed. |
| `OnLock` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when locked. |
| `OnMeleeAttacked` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when attacked in melee. |
| `OnOpen` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when opened. |
| `OnSpellCastAt` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when spell cast at placeable. |
| `OnUnlock` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when unlocked. |
| `OnUsed` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when used/clicked. |
| `OnUserDefined` | *[ResRef](GFF-File-Format#gff-data-types)* | Fires on user-defined events. |
| `OnFailToOpen` (KotOR2) | *[ResRef](GFF-File-Format#gff-data-types)* | Fires when opening fails. |

## Trap System

| Field | Type | Description |
| ----- | ---- | ----------- |
| `TrapDetectable` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Trap can be detected. |
| `TrapDetectDC` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | Awareness DC to detect trap. |
| `TrapDisarmable` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Trap can be disarmed. |
| `DisarmDC` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | Security DC to disarm trap. |
| `TrapFlag` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Trap is active. |
| `TrapOneShot` | *[Byte](GFF-File-Format#gff-data-types)* *Boolean* (0 or 1) | Trap triggers only once. |
| `TrapType` | *[Byte](GFF-File-Format#gff-data-types)* *Integer* (signed) | index into [`traps.2da`](2DA-traps) ([trap definitions](2DA-traps)). |

**Trap Behavior:**

- Identical to **[UTD](GFF-UTD)** door trap system
- Triggers on **[Placeable](GFF-UTP)** use
- Common on containers and terminals

## Visual Customization

| Field | Type | Description |
| ----- | ---- | ----------- |
| `PortraitId` | *[Word](GFF-File-Format#gff-data-types)* | Portrait icon identifier |
| `PaletteID` | *[Byte](GFF-File-Format#gff-data-types)* | Toolset palette category |

**[model](MDL-MDX-File-Format) & Lighting:**

- **Appearance** determines **[model](MDL-MDX-File-Format)** and light color
- Some placeables have animated components
- Light properties defined in **[`placeables.2da`](2DA-placeables)**

## Implementation Notes

**Placeable Categories:**

**Containers:**

- Footlockers, crates, corpses
- Have inventory **`ItemList`** populated
- Can be locked, trapped, destroyed
- **`HasInventory=1`**, **`BodyBag=1`** flag for corpses

**Switches & Terminals:**

- Trigger scripts or conversations
- No inventory typically
- **`Useable=1`**, **`Conversation`** property set to **[DLG](GFF-DLG)** file or scripts set
- Common for puzzle activation

**Workbenches:**

- Special placeable type for crafting
- Opens crafting interface on use
- Defined by **`Type`** or **`Appearance`**

**Furniture:**

- Non-interactive decoration
- **`Static=1`** *Boolean* (0 or 1) or **`Useable=0`** *Boolean* (0 or 1)
- Pure visual elements

**Environmental Objects:**

- Explosive containers, power generators
- Can be destroyed with effects
- Often have **HP** and **`OnDeath`** scripts

**Instantiation Flow:**

1. **Template Load**: **[GFF](GFF-File-Format)** parsed from **[UTP](GFF-File-Format#utp-placeable)**
2. **Appearance Setup**: **[model ([MDL/MDX](MDL-MDX-File-Format))**] loaded from **[`placeables.2da`](2DA-placeables)**
3. **Inventory Population**: **`ItemList`** instantiated
4. **Lock State**: Locked status applied
5. **Trap Activation**: Trap armed if configured
6. **Script Registration**: Event handlers registered

**Container Loot:**

- **`ItemList`** defines initial inventory
- Random loot can be added via script
- **`OnInvDisturbed`** fires when items taken
- BodyBag containers have special loot rules

**Conversation Placeables:**

- Terminals, control panels, puzzle interfaces
- **`Conversation`** property set to **[DLG](GFF-DLG)** file
- Use triggers dialog instead of direct interaction
- Dialog can have conditional responses

**Common Placeable types:**

**Storage Containers:**

- Footlockers, crates, bins
- Standard inventory interface
- Often locked or trapped

**Corpses:**

- **`BodyBag=1`** flag set
- Contain enemy loot
- Disappear when looted (usually)

**Terminals:**

- Computer interfaces
- Trigger conversations or scripts
- May require Computer Use skill checks

**Switches:**

- Activate doors, puzzles, machinery
- Fire **`OnUsed`** script
- Visual feedback **[animation](MDL-MDX-File-Format#animation-header)**

**Workbenches:**

- Crafting interface activation
- Lab stations, upgrade benches
- Special **`Type`** value

**Decorative Objects:**

- No gameplay interaction
- **`Static=1`** *Boolean* (0 or 1) or **`Useable=0`** *Boolean* (0 or 1) (Static or non-useable)
- Environmental detail

**Mines (Special Case):**

- Placed as placeable or creature
- Trap properties define behavior
- Can be detected and disarmed
- Trigger on proximity or interaction
