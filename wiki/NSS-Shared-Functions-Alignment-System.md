# Alignment System

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This hub covers NWScript alignment queries and adjustments (good/evil, law/chaos where exposed). Per-routine prose is still thin on this page; the **canonical routine list** (names + routine IDs) is in [NSS-File-Format — Shared Functions (K1 & TSL) — Alignment System](NSS-File-Format#alignment-system). Constants: [NSS-Shared-Constants-Alignment-Constants](NSS-Shared-Constants-Alignment-Constants).

## Implementation cross-reference

- **PyKotor:** NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); routine metadata — e.g. [`scriptdefs.py` L4197+ (`GetAlignmentGoodEvil`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L4197), [L4636+ (`GetFactionAverageGoodEvilAlignment`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L4636), [L4734+ (`AdjustAlignment`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L4734) (first K1 block).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetAlignmentGoodEvil` L1193+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L1193), [`AdjustAlignment` L1939+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L1939); K1 `insert` — [`GetAlignmentGoodEvil` L6974](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L6974), [`AdjustAlignment` L7027](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7027). **TSL:** `AdjustAlignment` is registered again with an **extra parameter** — see [L7583](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7583) vs K1 [L7027](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7027); always match the signature in the target game’s `nwscript.nss`.

- **KotOR.js:** [`NWScriptDefK1.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts) — [`GetAlignmentGoodEvil` L1609](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L1609), [`AdjustAlignment` L2547](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L2547).

- **Kotor.NET:** [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

## See also

- [Effects System — VersusAlignmentEffect](NSS-Shared-Functions-Effects-System) (routine 355 in master index)
- [repute.2da](2DA-repute); faction templates — [Bioware-Aurora-Faction](Bioware-Aurora-Faction), [GFF-File-Format — FAC](GFF-File-Format#fac-faction) (cross-check column meanings on those pages)
