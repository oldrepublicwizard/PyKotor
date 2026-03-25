# Archived UTP class docstring

Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/resource/generics/utp.py` (git HEAD) before this scrub.

```
Stores placeable data.

UTP files are GFF-based format files that store placeable object definitions including
lock/unlock mechanics, HP, inventory, scripts, and appearance.

References:
----------
    Based on unified K1 (swkotor.exe) and TSL (swkotor2.exe) UTP implementation.
    Addresses: (K1: swkotor.exe, TSL: swkotor2.exe). TSL addresses: resolve in REVA when
    PyKotorGhidraProject.gpr is open (project may be locked by another process).

    - CSWSPlaceable::LoadPlaceable (main UTP GFF parser)
        K1: 0x00585670, TSL: 0x006a1680 (LoadPlaceableFromGFF, legacy PC)
        Loads all placeable fields from GFF structure.
        Signature: LoadPlaceable(CSWSPlaceable* this, CResGFF* param_1, CResStruct* param_2, int param_3).
        Called from LoadPlaceables and LoadFromTemplate.

    - CSWSPlaceable::SavePlaceable (UTP GFF writer)
        K1: 0x00586a70, TSL: TODO
        Writes all placeable fields to GFF structure.

    - LoadPlaceables / LoadFromTemplate (callers)
        K1: LoadPlaceables 0x0050a7b0, LoadFromTemplate 0x00587a70; TSL: TODO

    - GFF field label string references (K1; TSL at different addresses, TODO):
        K1: "Appearance" 0x00746efc, "HasInventory" 0x007496e0, "Lockable" 0x007496f8,
        "KeyName" 0x0074979c, "OpenLockDC" 0x007497a4, "CloseLockDC" 0x007496c8.

    GFF Field Structure (from LoadPlaceable analysis):
        - Root struct fields:
            - "Tag" (CExoString) - Placeable tag identifier
            - "TemplateResRef" (CResRef) - Template resource reference
            - "LocName" (CExoLocString) - Localized placeable name
            - "AutoRemoveKey" (BYTE) - Whether key is auto-removed after use
            - "Faction" (DWORD) - Faction identifier
            - "Invulnerable" (BYTE) - Whether placeable is invulnerable
            - "Plot" (BYTE) - Whether placeable is plot-critical
            - "Min1HP" (BYTE) - Whether placeable has minimum 1 HP
            - "PartyInteract" (BYTE) - Whether party can interact
            - "OpenLockDC" (BYTE) - Open lock difficulty class
            - "KeyName" (CExoString) - Key name/ResRef
            - "TrapDisarmable" (BYTE) - Whether trap is disarmable
            - "TrapDetectable" (BYTE) - Whether trap is detectable
            - "DisarmDC" (BYTE) - Disarm difficulty class
            - "TrapDetectDC" (BYTE) - Trap detection difficulty class
            - "TrapFlag" (BYTE) - Trap flag
            - "TrapOneShot" (BYTE) - Whether trap is one-shot
            - "TrapType" (BYTE) - Trap type identifier
            - "Useable" (BYTE) - Whether placeable is usable
            - "Static" (BYTE) - Whether placeable is static
            - "Appearance" (DWORD) - Appearance type identifier
            - "HP" (SHORT) - Hit points
            - "CurrentHP" (SHORT) - Current hit points
            - "Hardness" (BYTE) - Hardness value
            - "Fort" (BYTE) - Fortitude save
            - "Will" (BYTE) - Will save
            - "Ref" (BYTE) - Reflex save
            - "Lockable" (BYTE) - Whether placeable is lockable
            - "Locked" (BYTE) - Whether placeable is locked
            - "HasInventory" (BYTE) - Whether placeable has inventory
            - "KeyRequired" (BYTE) - Whether key is required
            - "CloseLockDC" (BYTE) - Close lock difficulty class
            - "PortraitId" (WORD) - Portrait ID (0xffff = use Portrait ResRef)
            - "Portrait" (CResRef) - Portrait resource reference (if PortraitId == 0xffff)
            - "Conversation" (CResRef) - Conversation dialog ResRef
            - "BodyBag" (BYTE) - Body bag type
            - "DieWhenEmpty" (BYTE) - Whether placeable dies when inventory empty
            - "GroundPile" (BYTE) - Ground pile flag
            - "LightState" (BYTE) - Light state (on/off)
            - "Description" (CExoLocString) - Placeable description
            - "ItemList" (GFFList) - List of inventory items (if HasInventory)

    Note: UTP files are GFF format files with specific structure definitions (GFFContent.UTP)

Derivations and Other Implementations:
----------
    https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Resources/KotorUTP/UTP.cs:12-75 (UTP class definition)

Attributes:
----------
    resref: "TemplateResRef" field. The resource reference for this placeable template.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:64 (TemplateResRef property)

    tag: "Tag" field. Tag identifier for this placeable.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:63 (Tag property)

    name: "LocName" field. Localized name of the placeable.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:35 (LocName property)

    appearance_id: "Appearance" field. Placeable appearance type identifier.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:15 (Appearance property)

    has_inventory: "HasInventory" field. Whether placeable has an inventory.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:27 (HasInventory property)

    inventory: List of InventoryItem objects in this placeable's inventory.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:74 (Inventory property)

    not_blastable: "NotBlastable" field. Whether placeable cannot be blasted. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:37 (NotBlastable property)
        Reference: NorthernLights/AuroraUTP.cs:67 (NotBlastable field)

    unlock_diff: "OpenLockDiff" field. Unlock difficulty modifier. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:55 (OpenLockDiff property)
        Reference: NorthernLights/AuroraUTP.cs:68 (OpenLockDiff field)

    unlock_diff_mod: "OpenLockDiffMod" field. Additional unlock difficulty modifier. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:56 (OpenLockDiffMod property as sbyte)
        Reference: NorthernLights/AuroraUTP.cs:69 (OpenLockDiffMod field as Char)
        Note: Type discrepancy - reone uses char/int, Kotor.NET uses sbyte, PyKotor uses int

    on_open_failed: "OnFailToOpen" field. Script to run when placeable fails to open. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:43 (OnFailToOpen property)

    lock_dc: "CloseLockDC" field. Difficulty class to lock placeable. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:18 (CloseLockDC property)

    palette_id: "PaletteID" field. Palette identifier. Used in toolset only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTP.cs:57 (PaletteID property)

    Note: UTP shares many fields with UTD (door). See UTD documentation for common fields
    like auto_remove_key, conversation, faction_id, plot, min1_hp, key_required, lockable,
    locked, unlock_dc, key_name, animation_state, maximum_hp, current_hp, hardness,
    fortitude, on_closed, on_damaged, on_death, on_heartbeat, on_lock, on_melee_attack,
    on_open, on_force_power, on_unlock, on_user_defined, static, useable, party_interact,
    on_end_dialog, on_inventory, on_used, comment, description, interruptable, portrait_id,
    trap_detectable, trap_detect_dc, trap_disarmable, trap_disarm_dc, trap_flag,
    trap_one_shot, trap_type, will, on_disarm, on_trap_triggered, bodybag_id, type_id.
```
