# Class System

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This hub covers NWScript multi-class and level queries. The **routine index** lives under [NSS-File-Format — Class System](NSS-File-Format#class-system). Constants: [NSS-Shared-Constants-Class-Type-Constants](NSS-Shared-Constants-Class-Type-Constants). TSL-only class helpers (if any) are listed under [NSS-TSL-Only-Functions-Class-System](NSS-TSL-Only-Functions-Class-System).

## Implementation cross-reference

- **PyKotor:** NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); routine metadata — e.g. [`scriptdefs.py` L5794+ (`GetClassByPosition`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L5794), [L5808+ (`GetLevelByClass`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L5808) (first K1 block; search for `AddMultiClass`, `GetFactionMostFrequentClass`, etc.).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetClassByPosition` L3181+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L3181), [`GetLevelByClass` L3207+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L3207); K1 `insert` — [`GetClassByPosition` L7144](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7144), [`GetLevelByClass` L7146](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7146).

- **KotOR.js:** [`NWScriptDefK1.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts) — [`GetClassByPosition` L4215](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L4215), [`GetLevelByClass` L4245](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L4245).

- **Kotor.NET:** [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

## See also

- [Skills and Feats](NSS-Shared-Functions-Skills-and-Feats) — feat and skill checks often pair with class level queries
- [2DA-classes](2DA-classes) — class table data
