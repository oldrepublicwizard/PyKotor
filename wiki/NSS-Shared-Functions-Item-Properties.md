# Item Properties

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

KotOR exposes item property checks via NWScript (e.g. `GetItemHasItemProperty`). **Item templates** use [UTI](GFF-UTI) (GFF); property *definitions* and cost tables live in [2DA](2DA-File-Format) tables such as [itempropdef.2da](2DA-itempropdef) and related `iprp_*` pages linked from [2DA-File-Format](2DA-File-Format). Full inventory API: [NSS-Shared-Functions-Item-Management](NSS-Shared-Functions-Item-Management). Routine index: [NSS-File-Format — Item Properties](NSS-File-Format#item-properties).

## Implementation cross-reference

- **PyKotor:** GFF I/O for UTI — [`io_gff.py` L79+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L79), [`resource/generics/uti.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/uti.py); NSS metadata — [`scriptdefs.py` L6208+ (`GetItemHasItemProperty`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6208).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetItemHasItemProperty` L3648+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L3648); K1 `insert` — [L7191](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7191).

- **KotOR.js:** [`NWScriptDefK1.ts` — `GetItemHasItemProperty` L4779](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L4779).

- **Kotor.NET:** [`GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18); [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

## See also

- [Effects System](NSS-Shared-Functions-Effects-System) — on-hit and property-like gameplay effects
- [2DA-itemprops](2DA-itemprops) — item property enumeration table (if present in your game data set)
