# UTM (Merchant)

Part of the [GFF File Format Documentation](GFF-File-Format).

UTM files are GFF resources with root content type **`UTM`** ([`GFFContent.UTM`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/gff_data.py#L156)) that define **merchant templates**: localized name, pricing (mark up / mark down), buy/sell flags, optional `OnOpenStore` script hook, and an **`ItemList`** of stock lines. Module **store instances** in the [**GIT**](GFF-GIT) reference a UTM template via the area’s store list (PyKotor maps GIT stores to [`ResourceType.UTM`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L107); instance wrapper [`GITStore` L967–L1000](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/git.py#L967-L1000)). UTMs resolve like other resources: [override → MOD/SAV → KEY/BIF](Concepts#resource-resolution-order).

**Official Bioware Documentation:** See [Bioware Aurora Store Format](Bioware-Aurora-Store) for Aurora-era store semantics; KotOR field names below match PyKotor’s `construct_utm` / `dismantle_utm` and the class docstring’s `LoadStore` notes.

**For mod developers:** [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax), [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers). Global merchant metadata also lives in **[merchants.2da](2DA-File-Format)** (data table, not the per-template GFF).

## Root struct fields

| Field | GFF type | Role |
| ----- | -------- | ---- |
| `ResRef` | ResRef | Template resref (file stem). |
| `LocName` | CExoLocString | Localized merchant name. |
| `Tag` | CExoString | Tag for scripts / identification. |
| `MarkUp` | int32 | Markup when selling **to** the player (percent). |
| `MarkDown` | int32 | Markdown when buying **from** the player (percent). |
| `OnOpenStore` | ResRef | Script executed when the store UI opens. |
| `Comment` | CExoString | Authoring comment. |
| `BuySellFlag` | byte | Bit 0 = can buy from player; bit 1 = can sell to player ([`construct_utm` L173–L174](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L173-L174)). |
| `ItemList` | List | Stock entries (see below). |
| `ID` | byte | Legacy / unused in practice; PyKotor can still emit it when `use_deprecated=True` in [`dismantle_utm` L218–L219](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L218-L219). |

## ItemList element struct

Each list element is a struct with (at minimum) the fields PyKotor reads and writes:

| Field | GFF type | Role |
| ----- | -------- | ---- |
| `InventoryRes` | ResRef | Item template ([UTI](GFF-UTI)) resref. |
| `Infinite` | byte | Infinite stock when non-zero. |
| `Dropable` | byte | Droppable flag (PyKotor writes the field only when true — [`dismantle_utm` L213–L214](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L213-L214)). |
| `Repos_PosX` | uint16 | Repository grid X (writer uses slot index — [`dismantle_utm` L211](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L211)). |
| `Repos_PosY` | uint16 | Repository grid Y (writer uses `0` — same block). |

## References

**PyKotor**

- [`utm.py` `UTM` L18+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L18) — dataclass + engine-oriented docstring (`CSWSStore::LoadStore` / `SaveStore` K1 addresses).
- [`construct_utm` L147–L185](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L147-L185), [`dismantle_utm` L188–L221](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L188-L221).
- [`read_utm` / `write_utm` / `bytes_utm` L224–L253](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utm.py#L224-L253).
- Binary GFF pipeline (same as other generics): [`io_gff.py` `GFFBinaryReader.load` L79+](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/gff/io_gff.py#L79).

**Cross-reference (other implementations)**

- **[reone](https://github.com/modawan/reone)** — [`gffreader.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/format/gffreader.cpp), [`gff.cpp`](https://github.com/modawan/reone/blob/master/src/libs/resource/gff.cpp) — generic GFF reader (UTM is a typed GFF root).
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** — [`GFFObject.ts` L24+](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/GFFObject.ts#L24) — TypeScript GFF parser for all BioWare struct types including merchant templates.
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** — [`Resources/KotorUTM/UTM.cs` L13–L35](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Resources/KotorUTM/UTM.cs#L13-L35) — `UTM` / `UTMItem` field model; pair with [`Formats/KotorGFF/GFF.cs` L18+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorGFF/GFF.cs#L18) for container I/O.
- **[xoreos](https://github.com/xoreos/xoreos)** — Aurora GFF stack; UTM treated as GFF instance like other templates.

### See also

- [GFF-File-Format](GFF-File-Format) — container layout; [GFF-GIT](GFF-GIT) — store **instances** in areas
- [GFF-UTI](GFF-UTI) — item templates referenced by `InventoryRes`
- [Bioware-Aurora-Store](Bioware-Aurora-Store) — Aurora store documentation
- [KEY-File-Format](KEY-File-Format) — resource resolution
