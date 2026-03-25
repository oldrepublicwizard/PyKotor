# Player Character Functions

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This hub lists NWScript routines that target the **player** (PC), dialog speaker resolution, and turret minigame (`SWMG_*`) player accessors. The **master index** is under [NSS-File-Format — Player Character Functions](NSS-File-Format#player-character-functions). Many `GetIsPC`-style helpers appear under [Other Functions](NSS-Shared-Functions-Other-Functions) in the same TOC—behavior is identical; those pages cross-link. TSL-only additions: [NSS-TSL-Only-Functions-Player-Character-Functions](NSS-TSL-Only-Functions-Player-Character-Functions).

## Implementation cross-reference

- **PyKotor:** NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); routine metadata — e.g. [`scriptdefs.py` L5037+ (`GetPCSpeaker`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L5037) (first K1 block; search for `SWMG_GetPlayer`, `SWMG_SetPlayerSpeed`, etc.).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetPCSpeaker` L2295+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L2295); K1 `insert` — [`GetPCSpeaker` L7055](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7055).

- **KotOR.js:** [`NWScriptDefK1.ts` — `GetPCSpeaker` L2986](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L2986); search the same file for `SWMG_` symbols.

- **Kotor.NET:** [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

## See also

- [Dialog and Conversation Functions](NSS-Shared-Functions-Dialog-and-Conversation-Functions) — `GetPCSpeaker` and conversation flow
- [Party Management](NSS-Shared-Functions-Party-Management) — `GetFirstPC`, party iteration (indexed under other NSS sections; search [NSS-File-Format](NSS-File-Format))
