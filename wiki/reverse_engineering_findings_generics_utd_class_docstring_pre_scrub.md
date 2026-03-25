# Archived UTD class docstring

Verbatim ast.get_docstring from `Libraries/PyKotor/src/pykotor/resource/generics/utd.py` (git HEAD) before this scrub.

```
Stores door data.

UTD files are GFF-based format files that store door definitions including
lock/unlock mechanics, HP, scripts, and appearance.

References:
----------
    CSWSDoor::LoadDoor @ (K1: 0x0058a1f0, TSL: 0x006531e0 legacy PC / 0x00765620 Aspyr)
    Main UTD GFF parser; called from LoadDoorExternal (K1: 0x0058c5f0, TSL: 0x00765270) and LoadFromTemplate (K1: 0x0058b3d0, TSL: 0x007672c0). LoadDoors (K1: 0x0050a0e0, TSL: 0x0071b8a0) loads area doors.
    Defaults when field missing: Static 0, Conversation ""; other root fields use object state or 0/""/0.0. Omit OK.

    GFF Field Structure (from LoadDoor analysis):
        - Root struct fields:
            - "Appearance" (DWORD) - Door appearance type identifier
            - "GenericType" (BYTE) - Generic door type
            - "OpenState" (BYTE) - Initial open state (0=closed, 1=opened, 2=locked, 3=unlocked)
            - "AutoRemoveKey" (BYTE) - Whether key is auto-removed after use
            - "Bearing" (FLOAT) - Door bearing/rotation
            - "Faction" (DWORD) - Faction identifier
            - "Fort" (BYTE) - Fortitude save
            - "Will" (BYTE) - Will save
            - "Ref" (BYTE) - Reflex save
            - "HP" (SHORT) - Hit points
            - "CurrentHP" (SHORT) - Current hit points
            - "Invulnerable" (BYTE) - Whether door is invulnerable
            - "Plot" (BYTE) - Whether door is plot-critical
            - "Static" (BYTE) - Whether door is static
            - "Min1HP" (BYTE) - Whether door has minimum 1 HP
            - "KeyName" (CExoString) - Key name/ResRef
            - "KeyRequired" (BYTE) - Whether key is required
            - "OpenLockDC" (BYTE) - Open lock difficulty class
            - "CloseLockDC" (BYTE) - Close lock difficulty class
            - "SecretDoorDC" (BYTE) - Secret door detection difficulty class
            - "Tag" (CExoString) - Door tag identifier
            - "Conversation" (CResRef) - Conversation dialog ResRef
            - "PortraitId" (WORD) - Portrait ID (0xffff = use Portrait ResRef)
            - "Portrait" (CResRef) - Portrait resource reference (if PortraitId == 0xffff)
            - "Hardness" (BYTE) - Hardness value
            - "LocName" (CExoLocString) - Localized door name
            - "Description" (CExoLocString) - Door description
            - Script fields:
                - "OnClosed" (CResRef) - Script executed when door closes
                - "OnDamaged" (CResRef) - Script executed when door is damaged
                - "OnDeath" (CResRef) - Script executed when door is destroyed
                - "OnDisarm" (CResRef) - Script executed when trap is disarmed
                - "OnHeartbeat" (CResRef) - Script executed on heartbeat

    Note: UTD files are GFF format files with specific structure definitions (GFFContent.UTD)

Derivations and Other Implementations:
----------
    https://github.com/th3w1zard1/Kotor.NET/tree/master/Kotor.NET/Resources/KotorUTD/UTD.cs:11-68 (UTD class definition)
    https://github.com/th3w1zard1/KotOR.js/tree/master/src/module/ModuleDoor.ts:55-167 (Door module object)

Attributes:
----------
    resref: "TemplateResRef" field. The resource reference for this door template.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:59 (TemplateResRef property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:144 (templateResRef field)

    tag: "Tag" field. Tag identifier for this door.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:58 (Tag property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:143 (tag field)

    name: "LocName" field. Localized name of the door.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:33 (LocName property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:133 (locName field)

    auto_remove_key: "AutoRemoveKey" field. Whether key is removed after use.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:15 (AutoRemoveKey property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:120 (autoRemoveKey field)

    conversation: "Conversation" field. ResRef to dialog file for this door.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:18 (Conversation property)

    faction_id: "Faction" field. Faction identifier.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:22 (Faction property)

    plot: "Plot" field. Whether door is plot-critical.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:54 (Plot property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:139 (plot field)

    min1_hp: "Min1HP" field. Whether door HP cannot go below 1. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:34 (Min1HP property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:136 (min1HP field)

    key_required: "KeyRequired" field. Whether a key is required to unlock.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:29 (KeyRequired property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:131 (keyRequired field)

    lockable: "Lockable" field. Whether door can be locked.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:31 (Lockable property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:134 (lockable field)

    locked: "Locked" field. Whether door is currently locked.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:32 (Locked property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:135 (locked field)

    unlock_dc: "OpenLockDC" field. Difficulty class to unlock door.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:49 (OpenLockDC property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:137 (openLockDC field)

    key_name: "KeyName" field. Tag of the key item required.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:28 (KeyName property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:130 (keyName field)

    animation_state: "AnimationState" field. Current animation state. Always 0 in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:13 (AnimationState property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:118 (animationState field)
        Note: This field is always 0 in files (verified against engine binaries)

    maximum_hp: "HP" field. Maximum hit points.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:26 (HP property)

    current_hp: "CurrentHP" field. Current hit points.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:19 (CurrentHP property)

    hardness: "Hardness" field. Damage reduction value.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:25 (Hardness property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:128 (hardness field)

    fortitude: "Fort" field. Fortitude save value. Always 0 in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:23 (Fort property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:125 (fort field)

    appearance_id: "GenericType" field. Door appearance type identifier.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:24 (GenericType property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:126 (genericType field)

    static: "Static" field. Whether door is static (non-interactive).
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:57 (Static property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:142 (static field)

    on_closed: "OnClosed" field. Script to run when door closes. Always empty in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:36 (OnClosed property)
        Note: Verified against engine binaries

    on_damaged: "OnDamaged" field. Script to run when door is damaged. Always empty in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:37 (OnDamaged property)
        Note: Verified against engine binaries

    on_death: "OnDeath" field. Script to run when door is destroyed.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:38 (OnDeath property)

    on_heartbeat: "OnHeartbeat" field. Script to run on heartbeat.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:41 (OnHeartbeat property)

    on_lock: "OnLock" field. Script to run when door is locked. Always empty in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:42 (OnLock property)
        Note: Verified against engine binaries

    on_melee: "OnMeleeAttacked" field. Script to run when door is melee attacked. Always empty in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:43 (OnMeleeAttacked property)
        Note: Verified against engine binaries

    on_open: "OnOpen" field. Script to run when door opens.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:44 (OnOpen property)

    on_unlock: "OnUnlock" field. Script to run when door is unlocked. Always empty in files.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:47 (OnUnlock property)
        Note: Verified against engine binaries

    on_user_defined: "OnUserDefined" field. Script to run on user-defined event.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:48 (OnUserDefined property)

    on_click: "OnClick" field. Script to run when door is clicked.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:35 (OnClick property)

    on_open_failed: "OnFailToOpen" field. Script to run when door fails to open. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:40 (OnFailToOpen property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:390 (used in unlock failure handling)

    comment: "Comment" field. Developer comment. Used in toolset only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:17 (Comment property)
        Note: Verified against engine binaries

    unlock_diff: "OpenLockDiff" field. Unlock difficulty modifier. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:50 (OpenLockDiff property)
        Reference: NorthernLights/AuroraUTD.cs:65 (OpenLockDiff field)

    unlock_diff_mod: "OpenLockDiffMod" field. Additional unlock difficulty modifier. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:51 (OpenLockDiffMod property as sbyte)
        Reference: NorthernLights/AuroraUTD.cs:66 (OpenLockDiffMod field as Char)
        Note: Type discrepancy - reone uses char/int, Kotor.NET uses sbyte, PyKotor uses int

    open_state: "OpenState" field. Current open state (closed/open1/open2). KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:52 (OpenState property)
        Reference: NorthernLights/AuroraUTD.cs:67 (OpenState field)
        Reference: sotor/src/save/read.rs:488 (OpenState in save games)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:56 (openState field)

    not_blastable: "NotBlastable" field. Whether door cannot be blasted. KotOR 2 Only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:67 (NotBlastable property)
        Reference: NorthernLights/AuroraUTD.cs:64 (NotBlastable field)

    palette_id: "PaletteID" field. Palette identifier. Used in toolset only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:53 (PaletteID property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:138 (paletteID field)
        Note: Verified against engine binaries

    description: "Description" field. Localized description. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:20 (Description property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:123 (description field)
        Note: Verified against engine binaries

    lock_dc: "CloseLockDC" field. Difficulty class to lock door. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:16 (CloseLockDC property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:121 (closeLockDC field)
        Note: Verified against engine binaries

    interruptable: "Interruptable" field. Whether door can be interrupted. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:27 (Interruptable property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:129 (interruptable field)
        Note: Verified against engine binaries

    portrait_id: "PortraitId" field. Portrait identifier. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:55 (PortraitId property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:140 (portraitId field)
        Note: Verified against engine binaries

    trap_detectable: "TrapDetectable" field. Whether trap is detectable. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:60 (TrapDetectable property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:146 (trapDetectable field)
        Note: Verified against engine binaries

    trap_detect_dc: "TrapDetectDC" field. Difficulty class to detect trap. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:61 (TrapDetectDC property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:145 (trapDetectDC field)
        Note: Verified against engine binaries

    trap_disarmable: "TrapDisarmable" field. Whether trap is disarmable. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:62 (TrapDisarmable property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:147 (trapDisarmable field)
        Note: Verified against engine binaries

    trap_disarm_dc: "DisarmDC" field. Difficulty class to disarm trap. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:21 (DisarmDC property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:124 (disarmDC field)
        Note: Verified against engine binaries

    trap_flag: "TrapFlag" field. Whether door has a trap. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:63 (TrapFlag property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:148 (trapFlag field)
        Note: Verified against engine binaries

    trap_one_shot: "TrapOneShot" field. Whether trap fires once. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:64 (TrapOneShot property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:149 (trapOneShot field)
        Note: Verified against engine binaries

    trap_type: "TrapType" field. Type of trap. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:65 (TrapType property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:150 (trapType field)
        Note: Verified against engine binaries

    unused_appearance: "Appearance" field. Appearance identifier. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:14 (Appearance property)
        Note: Verified against engine binaries

    reflex: "Ref" field. Reflex save value. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:56 (Ref property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:141 (ref field)
        Note: Verified against engine binaries

    willpower: "Will" field. Will save value. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:66 (Will property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:151 (will field)
        Note: Verified against engine binaries

    on_disarm: "OnDisarm" field. Script to run when trap is disarmed. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:39 (OnDisarm property)
        Note: Verified against engine binaries

    on_power: "OnSpellCastAt" field. Script to run when spell is cast at door. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:45 (OnSpellCastAt property)
        Note: Verified against engine binaries

    on_trap_triggered: "OnTrapTriggered" field. Script to run when trap triggers. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:46 (OnTrapTriggered property)
        Note: Verified against engine binaries

    loadscreen_id: "LoadScreenID" field. Load screen identifier. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTD.cs:30 (LoadScreenID property)
        Reference: https://github.com/th3w1zard1/KotOR.js/tree/master/ModuleDoor.ts:132 (loadScreenID field)
        Note: Verified against engine binaries
```
