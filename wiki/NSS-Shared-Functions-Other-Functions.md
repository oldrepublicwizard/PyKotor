# Other Functions

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This page is a **catch-all hub** for NWScript routines grouped under “Other” in the master index: area iterators, locals listed in the TOC under Other, PC checks, timing helpers, and miscellaneous engine hooks. **Important:** [GetLocalNumber](NSS-Shared-Functions-Local-Variables) / [SetLocalNumber](NSS-Shared-Functions-Local-Variables) (and related local APIs) are fully documented on [Local Variables](NSS-Shared-Functions-Local-Variables)—the [NSS-File-Format](NSS-File-Format) TOC still links some of those lines here for historical layout.

**Master index:** [NSS-File-Format — Shared Functions (K1 & TSL)](NSS-File-Format#shared-functions-k1--tsl) → scroll to **Other Functions** and related sub-bullets. K1-only / TSL-only “Other” pages: [NSS-K1-Only-Functions-Other-Functions](NSS-K1-Only-Functions-Other-Functions), [NSS-TSL-Only-Functions-Other-Functions](NSS-TSL-Only-Functions-Other-Functions).

## Implementation cross-reference

Use the same toolchain as other NSS categories; below are anchors for a representative high-traffic symbol (`GetIsPC`).

- **PyKotor:** NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); [`scriptdefs.py` L4869+ (`GetIsPC`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L4869).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetIsPC` L2054+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L2054); K1 `insert` — [L7036](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7036).

- **KotOR.js:** [`NWScriptDefK1.ts` — `GetIsPC` L2744](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L2744).

- **Kotor.NET:** [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

## See also

- [Object Query and Manipulation](NSS-Shared-Functions-Object-Query-and-Manipulation) — object validity and tagging
- [Module and Area](NSS-Shared-Functions-Module-and-Area) — iterators such as `GetFirstObjectInArea` (indexed under Other in some TOCs)
