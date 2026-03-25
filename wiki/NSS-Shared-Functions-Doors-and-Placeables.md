# Doors and Placeables

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This document provides detailed documentation for NWScript door and placeable functions. These functions allow scripts to open/close doors, interact with placeables, check lock states, and manage door/placeable interactions.

## Implementation cross-reference

Door **templates** on disk are [UTD](GFF-UTD) resources (GFF); placeables use [UTP](GFF-UTP). **Runtime** APIs below query or queue actions on instantiated objects. Queued open/close actions also appear under [NSS-Shared-Functions-Actions](NSS-Shared-Functions-Actions) (`ActionOpenDoor`, `ActionCloseDoor`, etc.).

- **PyKotor:** binary GFF I/O — [`io_gff.py` L79+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L79); NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); [`scriptdefs.py` L6528+ (`GetIsOpen`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6528) (first K1 block).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetIsOpen` L4008+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L4008); K1 `insert` — [`GetIsOpen` L7231](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7231) (TSL second block [L7787](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7787)).

- **KotOR.js:** [`NWScriptDefK1.ts` — `GetIsOpen` L5317](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L5317); search the same file for `ActionOpenDoor` / `ActionCloseDoor`.

- **Kotor.NET:** GFF types — [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18); NCS bytecode — [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

- **Community (workflow):** Deadly Stream — [Couple of Scripts [TSL]](https://deadlystream.com/topic/8048-couple-of-scripts-tsl/) (2009) — dialogue-driven door unlock patterns and scripting questions; **historical**—verify behavior against your game build and [Concepts](Concepts).

---

## Doors and Placeables Fundamentals

### Understanding Doors

Doors are objects that:

- Can be opened and closed
- Can be locked or unlocked
- May require keys or skill checks to open
- Can link to other areas or modules (area transitions)
- Have open/closed states

### Understanding Placeables

Placeables are interactive objects in the game world:

- **Containers** - Have inventories (chests, crates)
- **Interactive Objects** - Trigger scripts when used (terminals, switches)
- **Conversation Objects** - Start dialogues when used
- Can be locked or unlocked
- Can be destroyed or disabled

---

## Door Functions

### ActionOpenDoor

**Routine:** 43

#### Function Signature

```c
void ActionOpenDoor(object oDoor);
```

#### Description

Queues an action to open a door. The creature will move to the door and open it if possible (not locked, has key, etc.).

#### Parameters

- `oDoor`: Door object to open

#### Usage Examples

```c
// Open door
object oDoor = GetObjectByTag("door_01");
ActionOpenDoor(oDoor);
```

```c
// Open door for another creature
object oNPC = GetObjectByTag("guard");
object oDoor = GetObjectByTag("gate");
AssignCommand(oNPC, ActionOpenDoor(oDoor));
```

**Pattern: Conditional Door Opening**

```c
// Open door if unlocked
object oDoor = GetObjectByTag("secret_door");
if (!GetLocked(oDoor)) {
    ActionOpenDoor(oDoor);
} else {
    // Door is locked - need key or skill check
}
```

#### Notes

- Door must be unlocked or creature must have key
- Creature will move to door if not in range
- Locked doors cannot be opened without key or skill check

---

### ActionCloseDoor

**Routine:** 44

#### Function Signature

```c
void ActionCloseDoor(object oDoor);
```

#### Description

Queues an action to close a door. The creature will move to the door and close it.

#### Parameters

- `oDoor`: Door object to close

#### Usage Examples

```c
// Close door
object oDoor = GetObjectByTag("door_01");
ActionCloseDoor(oDoor);
```

```c
// Close all doors in area
object oDoor1 = GetObjectByTag("door_01");
object oDoor2 = GetObjectByTag("door_02");
ActionCloseDoor(oDoor1);
ActionCloseDoor(oDoor2);
```

---

## Lock Functions

### GetLocked

**Routine:** 325

#### Function Signature

```c
int GetLocked(object oTarget);
```

#### Description

Gets the locked state of a door or placeable object.

#### Parameters

- `oTarget`: Door or placeable to check

#### Returns

- `TRUE` (1) if the object is locked
- `FALSE` (0) if the object is unlocked or invalid

#### Usage Examples

```c
// Check if door is locked
object oDoor = GetObjectByTag("treasure_door");
if (GetLocked(oDoor)) {
    // Door is locked - need key or skill
} else {
    // Door is unlocked - can open
    ActionOpenDoor(oDoor);
}
```

**Pattern: Conditional Based on Lock State**

```c
// Different behavior based on lock state
object oContainer = GetObjectByTag("chest");
if (GetLocked(oContainer)) {
    // Locked - show message or attempt unlock
    SpeakString("This chest is locked!", TALKVOLUME_TALK);
} else {
    // Unlocked - open container
    ActionInteractObject(oContainer);
}
```

---

### SetLocked

**Routine:** 324

#### Function Signature

```c
void SetLocked(object oTarget, int bLocked);
```

#### Description

Sets the locked state of a door or placeable object.

#### Parameters

- `oTarget`: Door or placeable to lock/unlock
- `bLocked`: `TRUE` to lock, `FALSE` to unlock

#### Usage Examples

```c
// Lock a door
object oDoor = GetObjectByTag("vault_door");
SetLocked(oDoor, TRUE);
```

```c
// Unlock a door
object oDoor = GetObjectByTag("prison_door");
SetLocked(oDoor, FALSE);
```

**Pattern: Lock After Event**

```c
// Lock door after player enters
void main() {
    object oEntering = GetEnteringObject();
    if (GetIsPC(oEntering)) {
        // Player entered - lock door behind them
        object oDoor = GetObjectByTag("entrance_door");
        SetLocked(oDoor, TRUE);
    }
}
```

---

## Placeable Functions

### ActionInteractObject

**Routine:** 329

#### Function Signature

```c
void ActionInteractObject(object oPlaceable);
```

#### Description

Queues an action to interact with (use) a placeable object. The behavior depends on the placeable type:

- **Containers**: Opens inventory
- **Conversation Objects**: Starts dialogue
- **Script Objects**: Runs OnUsed script

#### Parameters

- `oPlaceable`: Placeable object to interact with

#### Usage Examples

```c
// Interact with placeable
object oTerminal = GetObjectByTag("computer_terminal");
ActionInteractObject(oTerminal);
```

```c
// Open container
object oChest = GetObjectByTag("treasure_chest");
if (!GetLocked(oChest)) {
    ActionInteractObject(oChest);
}
```

**Pattern: Conditional Placeable Interaction**

```c
// Interact if unlocked
object oContainer = GetObjectByTag("locked_box");
if (!GetLocked(oContainer)) {
    ActionInteractObject(oContainer);
} else {
    SpeakString("This container is locked!", TALKVOLUME_TALK);
}
```

#### Notes

- Creature will move to placeable if not in range
- Locked containers cannot be opened
- Different placeable types have different behaviors

---

## Event Functions

### GetLastUsedBy

**Routine:** 330

#### Function Signature

```c
object GetLastUsedBy();
```

#### Description

Gets the last object that used the placeable or door that is calling this function. This is typically used in `OnUsed` event scripts.

#### Returns

- Object that last used the caller
- `OBJECT_INVALID` if called by something other than a placeable or door, or if no object has used it

#### Usage Examples

```c
// In a placeable's OnUsed script
void main() {
    object oUser = GetLastUsedBy();
    if (GetIsPC(oUser)) {
        // Player used this placeable
        SpeakString("You activated the terminal!", TALKVOLUME_TALK);
    }
}
```

**Pattern: User-Specific Behavior**

```c
// Different behavior based on who used it
void main() {
    object oUser = GetLastUsedBy();
    if (GetIsPC(oUser)) {
        // Player used - grant reward
        GiveXPToCreature(oUser, 100);
    } else {
        // NPC used - different behavior
        SpeakString("Access denied!", TALKVOLUME_TALK);
    }
}
```

#### Notes

- Only works in event scripts (OnUsed, etc.)
- Returns the last object that used the caller
- Always validate the returned object

---

### GetClickingObject

**Routine:** 326

#### Function Signature

```c
object GetClickingObject();
```

#### Description

Gets the object that last clicked on the caller. This is identical to `GetEnteringObject()` and is typically used in trigger `OnClick` event scripts.

#### Returns

- Object that clicked on the caller
- `OBJECT_INVALID` if no object clicked or caller is invalid

#### Usage Examples

```c
// In a trigger's OnClick script
void main() {
    object oClicker = GetClickingObject();
    if (GetIsPC(oClicker)) {
        // Player clicked trigger
        // Do something
    }
}
```

#### Notes

- Only works in event scripts (OnClick, etc.)
- Identical to `GetEnteringObject()`
- Always validate the returned object

---

## Door Action Functions

### GetIsDoorActionPossible

**Routine:** 337

#### Function Signature

```c
int GetIsDoorActionPossible(object oTargetDoor, int nDoorAction);
```

#### Description

Checks if a specific door action can be performed on a door. Useful for checking if a door can be opened, closed, locked, etc.

#### Parameters

- `oTargetDoor`: Door to check
- `nDoorAction`: Door action constant (see Door Action Constants below)

#### Returns

- `TRUE` (1) if the action can be performed
- `FALSE` (0) if the action cannot be performed or door is invalid

#### Usage Examples

```c
// Check if door can be opened
object oDoor = GetObjectByTag("door_01");
if (GetIsDoorActionPossible(oDoor, DOOR_ACTION_OPEN)) {
    ActionOpenDoor(oDoor);
}
```

---

### DoDoorAction

**Routine:** 338

#### Function Signature

```c
void DoDoorAction(object oTargetDoor, int nDoorAction);
```

#### Description

Performs a specific door action on a door. This is a direct action (not queued) that executes immediately.

#### Parameters

- `oTargetDoor`: Door to perform action on
- `nDoorAction`: Door action constant (see Door Action Constants below)

#### Usage Examples

```c
// Open door directly
object oDoor = GetObjectByTag("door_01");
DoDoorAction(oDoor, DOOR_ACTION_OPEN);
```

```c
// Lock door directly
DoDoorAction(oDoor, DOOR_ACTION_LOCK);
```

---

## Door Action Constants

Standard door action constants:

- `DOOR_ACTION_OPEN` (0) - Open door
- `DOOR_ACTION_UNLOCK` (1) - Unlock door
- `DOOR_ACTION_BASH` (2) - Bash door (attempt to break it)
- `DOOR_ACTION_IGNORE` (3) - Ignore door (if available)
- `DOOR_ACTION_KNOCK` (4) - Knock on door (if available)

**Note:** Not all door actions may be available in all contexts. Use `GetIsDoorActionPossible()` to check if an action can be performed.

---

## Common Patterns and Best Practices

### Pattern: Locked Door Check

```c
// Check lock state before opening
object oDoor = GetObjectByTag("door_01");
if (GetLocked(oDoor)) {
    // Door is locked - check for key or skill
    object oPC = GetFirstPC();
    int nSecurity = GetSkillRank(SKILL_SECURITY, oPC);
    if (nSecurity >= 10) {
        // High security skill - unlock door
        SetLocked(oDoor, FALSE);
        ActionOpenDoor(oDoor);
    } else {
        SpeakString("This door is locked and you lack the skill to open it.", TALKVOLUME_TALK);
    }
} else {
    // Door is unlocked - open it
    ActionOpenDoor(oDoor);
}
```

### Pattern: Placeable OnUsed Script

```c
// In placeable's OnUsed script
void main() {
    object oUser = GetLastUsedBy();
    if (GetIsPC(oUser)) {
        // Player used placeable
        if (GetLocked(OBJECT_SELF)) {
            SpeakString("This is locked!", TALKVOLUME_TALK);
        } else {
            // Unlocked - grant reward
            CreateItemOnObject("reward_item", oUser);
        }
    }
}
```

### Pattern: Conditional Container Access

```c
// Check container state before opening
object oChest = GetObjectByTag("treasure_chest");
if (GetLocked(oChest)) {
    // Try to unlock
    object oPC = GetFirstPC();
    int nSecurity = GetSkillRank(SKILL_SECURITY, oPC);
    if (nSecurity >= 15) {
        SetLocked(oChest, FALSE);
        ActionInteractObject(oChest);
    }
} else {
    ActionInteractObject(oChest);
}
```

### Pattern: Door State Management

```c
// Manage door state based on events
void main() {
    object oEntering = GetEnteringObject();
    if (GetIsPC(oEntering)) {
        // Player entered - lock door behind them
        object oDoor = GetObjectByTag("entrance");
        SetLocked(oDoor, TRUE);
        ActionCloseDoor(oDoor);
    }
}
```

### Best Practices

1. **Check Lock State**: Always check `GetLocked()` before attempting to open doors/containers
2. **Validate Objects**: Check `GetIsObjectValid()` before using door/placeable objects
3. **Use Actions for Movement**: Use `ActionOpenDoor()` and `ActionInteractObject()` so creatures move to the object
4. **Event Scripts**: Use `GetLastUsedBy()` and `GetClickingObject()` only in event scripts
5. **Lock Management**: Use `SetLocked()` to control access to areas/containers
6. **Check Door Actions**: Use `GetIsDoorActionPossible()` before attempting door actions

---

## Related Functions

- `GetEnteringObject()` - Get object that entered (see [Module & Area](NSS-Shared-Functions-Module-and-Area))
- `GetObjectByTag()` - Find doors/placeables by tag (see [Object Query](NSS-Shared-Functions-Object-Query-and-Manipulation))
- `ActionMoveToObject()` - Move to door/placeable before interaction (see [Actions](NSS-Shared-Functions-Actions))

---

## Additional Notes

### Door States

Doors can be in multiple states:

- **Open/Closed**: Physical state of the door
- **Locked/Unlocked**: Whether the door requires a key or skill to open
- **Key Required**: Some doors require specific items (keys) to open

### Placeable Types

Placeables can have different behaviors:

- **Containers**: Have inventories that can be accessed
- **Conversation Objects**: Start dialogues when used
- **Script Objects**: Run custom scripts when used
- **Interactive Objects**: Trigger various game events

### Lock Mechanics

Locks can be:

- **Key-Based**: Require a specific item to unlock
- **Skill-Based**: Can be unlocked with Security skill
- **Script-Based**: Unlocked through script events
- **Permanent**: Cannot be unlocked (plot doors)

### Area Transitions

Some doors link to other areas or modules:

- When clicked, they trigger area/module transitions
- These doors may not use standard open/close actions
- Transition behavior is defined in the door's properties

### See also

- [NSS-File-Format](NSS-File-Format) -- Script format; [NCS-File-Format](NCS-File-Format) -- Compiled scripts
- [GFF-UTD](GFF-UTD) -- Door instances; [GFF-UTP](GFF-UTP) -- Placeable instances; [GFF-DLG](GFF-DLG) -- Conversation triggers
- [NSS-Shared-Functions-Object-Query-and-Manipulation](NSS-Shared-Functions-Object-Query-and-Manipulation) -- Object handles and queries
