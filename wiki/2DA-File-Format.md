# 2DA — Two-Dimensional Array

The Two-Dimensional Array (2DA) format is one of the engine's main configuration-table formats. PyKotor's `TwoDA` model stores ordered headers, ordered row labels, and string-valued cells, while its extraction metadata enumerates large catalogs of KotOR tables such as `appearance.2da`, `baseitems.2da`, `classes.2da`, `feat.2da`, `skills.2da`, `spells.2da`, `placeables.2da`, `itemprops.2da`, `soundset.2da`, and many `iprp_*` families. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

Each 2DA file is a table: rows are identified by labels, columns are identified by header text, and the on-disk cell payload is ultimately reconstructed as strings that callers interpret as integers, floats, ResRefs, StrRefs, or sentinel values such as `****` depending on the column. PyKotor documents both binary `2DA V2.b` and ASCII `2DA V2.0` handling, and xoreos-tools ships a dedicated `convert2da` utility alongside its other BioWare reverse-engineering tools. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [xoreos-tools `README.md`](https://github.com/xoreos/xoreos-tools/blob/master/README.md)]

The layout documented below matches the same core binary structure implemented in PyKotor, reone, xoreos, Kotor.NET, KotOR.js, KotOR-Unity, and reubenduncan's standalone format notes. To modify 2DA tables in a mod without replacing the whole file, use [TSLPatcher/HoloPatcher 2DAList syntax](TSLPatcher-2DAList-Syntax). 2DA tables are also referenced widely from GFF resources and installer workflows through the schemas cataloged in PyKotor's extraction registry. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [Kotor.NET `TwoDABinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/Kotor2DA/TwoDABinaryStructure.cs), [KotOR.js `TwoDAObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TwoDAObject.ts), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md), [`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

**Important**: While the 2DA binary layout is shared across BioWare's Aurora, Odyssey, and Eclipse engines, all column structures and engine usage descriptions on this page are specific to KotOR and KotOR II.

## Table of Contents

- 2DA — Two-Dimensional Array
  - Table of Contents
  - [file structure Overview](#file-structure-overview)
  - [Format](#format)
    - [File Header](#file-header)
    - [Column headers](#column-headers)
    - [Row Count](#row-count)
    - [Row Labels](#row-labels)
    - [Cell Data Offsets](#cell-data-offsets)
    - [Cell Data String Table](#cell-data-string-table)
  - [data structure](#data-structure)
    - [TwoDA Object](#twoda-object)
    - [TwoDARow Object](#twodarow-object)
  - [Cell Value Types](#cell-value-types)
  - [Confirmed Engine Usage](#confirmed-engine-usage)
  - [Known 2DA Files](#known-2da-files)
  - [Character \& Combat 2DA Files](#character-combat-2da-files)
    - [appearance.2da](#appearance2da)
    - [baseitems.2da](#baseitems2da)
    - [classes.2da](#classes2da)
    - [feat.2da](#feat2da)
    - [skills.2da](#skills2da)
    - [spells.2da](#spells2da)
  - [Items \& Properties 2DA Files](#items-properties-2da-files)
    - [itemprops.2da](#itemprops2da)
    - [iprp\_feats.2da](#iprp_feats2da)
    - [iprp\_spells.2da](#iprp_spells2da)
    - [iprp\_ammocost.2da](#iprp_ammocost2da)
    - [iprp\_damagecost.2da](#iprp_damagecost2da)
  - [Objects \& Area 2DA Files](#objects-area-2da-files)
    - [placeables.2da](#placeables2da)
    - [genericdoors.2da](#genericdoors2da)
    - [doortypes.2da](#doortypes2da)
    - [soundset.2da](#soundset2da)
  - [Visual Effects \& Animations 2DA Files](#visual-effects-animations-2da-files)
    - [visualeffects.2da](#visualeffects2da)
    - [portraits.2da](#portraits2da)
    - [heads.2da](#heads2da)
  - [Progression Tables 2DA Files](#progression-tables-2da-files)
    - [classpowergain.2da](#classpowergain2da)
    - [cls\_atk\_\*.2da](#cls_atk_2da)
    - [cls\_savthr\_\*.2da](#cls_savthr_2da)
  - [Name Generation 2DA Files](#name-generation-2da-files)
    - [humanfirst.2da](#humanfirst2da)
    - [humanlast.2da](#humanlast2da)
    - [Other Name Generation Files](#other-name-generation-files)
  - [Additional 2DA Files](#additional-2da-files)
    - [ambientmusic.2da](#ambientmusic2da)
    - [ambientsound.2da](#ambientsound2da)
    - [ammunitiontypes.2da](#ammunitiontypes2da)
    - [camerastyle.2da](#camerastyle2da)
    - [footstepsounds.2da](#footstepsounds2da)
    - [prioritygroups.2da](#prioritygroups2da)
    - [repute.2da](#repute2da)
    - [surfacemat.2da](#surfacemat2da)
    - [loadscreenhints.2da](#loadscreenhints2da)
    - [bodybag.2da](#bodybag2da)
    - [ranges.2da](#ranges2da)
    - [regeneration.2da](#regeneration2da)
    - [animations.2da](#animations2da)
    - [combatanimations.2da](#combatanimations2da)
    - [weaponsounds.2da](#weaponsounds2da)
    - [placeableobjsnds.2da](#placeableobjsnds2da)
    - [creaturespeed.2da](#creaturespeed2da)
    - [exptable.2da](#exptable2da)
    - [guisounds.2da](#guisounds2da)
    - [dialoganimations.2da](#dialoganimations2da)
    - [tilecolor.2da](#tilecolor2da)
    - [forceshields.2da](#forceshields2da)
    - [plot.2da](#plot2da)
    - [traps.2da](#traps2da)
    - [modulesave.2da](#modulesave2da)
    - [tutorial.2da](#tutorial2da)
    - [globalcat.2da](#globalcat2da)
    - [subrace.2da](#subrace2da)
    - [gender.2da](#gender2da)
    - [racialtypes.2da](#racialtypes2da)
    - [upgrade.2da](#upgrade2da)
    - [encdifficulty.2da](#encdifficulty2da)
    - [itempropdef.2da](#itempropdef2da)
    - [emotion.2da](#emotion2da)
    - [facialanim.2da](#facialanim2da)
    - [videoeffects.2da](#videoeffects2da)
    - [planetary.2da](#planetary2da)
    - [cursors.2da](#cursors2da)
  - [Item Property Parameter \& Cost Tables 2DA Files](#item-property-parameter-cost-tables-2da-files)
    - [iprp\_paramtable.2da](#iprp_paramtable2da)
    - [iprp\_costtable.2da](#iprp_costtable2da)
    - [iprp\_abilities.2da](#iprp_abilities2da)
    - [iprp\_aligngrp.2da](#iprp_aligngrp2da)
    - [iprp\_combatdam.2da](#iprp_combatdam2da)
    - [iprp\_damagetype.2da](#iprp_damagetype2da)
    - [iprp\_protection.2da](#iprp_protection2da)
    - [iprp\_acmodtype.2da](#iprp_acmodtype2da)
    - [iprp\_immunity.2da](#iprp_immunity2da)
    - [iprp\_saveelement.2da](#iprp_saveelement2da)
    - [iprp\_savingthrow.2da](#iprp_savingthrow2da)
    - [iprp\_onhit.2da](#iprp_onhit2da)
    - [iprp\_ammotype.2da](#iprp_ammotype2da)
    - [iprp\_mosterhit.2da](#iprp_mosterhit2da)
    - [iprp\_walk.2da](#iprp_walk2da)
    - [ai\_styles.2da](#ai_styles2da)
    - [iprp\_damagevs.2da](#iprp_damagevs2da)
    - [iprp\_attackmod.2da](#iprp_attackmod2da)
    - [iprp\_bonusfeat.2da](#iprp_bonusfeat2da)
    - [iprp\_lightcol.2da](#iprp_lightcol2da)
    - [iprp\_monstdam.2da](#iprp_monstdam2da)
    - [iprp\_skillcost.2da](#iprp_skillcost2da)
    - [iprp\_weightinc.2da](#iprp_weightinc2da)
    - [iprp\_traptype.2da](#iprp_traptype2da)
    - [iprp\_damagered.2da](#iprp_damagered2da)
    - [iprp\_spellres.2da](#iprp_spellres2da)
    - [rumble.2da](#rumble2da)
    - [musictable.2da](#musictable2da)
    - [difficultyopt.2da](#difficultyopt2da)
    - [xptable.2da](#xptable2da)
    - [featgain.2da](#featgain2da)
    - [effecticon.2da](#effecticon2da)
    - [itempropsdef.2da](#itempropsdef2da)
    - [pazaakdecks.2da](#pazaakdecks2da)
    - [acbonus.2da](#acbonus2da)
    - [keymap.2da](#keymap2da)
    - [soundeax.2da](#soundeax2da)
    - [poison.2da](#poison2da)
    - [feedbacktext.2da](#feedbacktext2da)
    - [creaturesize.2da](#creaturesize2da)
    - [appearancesndset.2da](#appearancesndset2da)
    - [texpacks.2da](#texpacks2da)
    - [videoquality.2da](#videoquality2da)
    - [loadscreens.2da](#loadscreens2da)
    - [phenotype.2da](#phenotype2da)
    - [palette.2da](#palette2da)
    - [bodyvariation.2da](#bodyvariation2da)
    - [textures.2da](#textures2da)
    - [merchants.2da](#merchants2da)
    - [actions.2da](#actions2da)
    - [aiscripts.2da](#aiscripts2da)
    - [bindablekeys.2da](#bindablekeys2da)
    - [crtemplates.2da](#crtemplates2da)
    - [environment.2da](#environment2da)
    - [fractionalcr.2da](#fractionalcr2da)
    - [gamespyrooms.2da](#gamespyrooms2da)
    - [hen\_companion.2da](#hen_companion2da)
    - [hen\_familiar.2da](#hen_familiar2da)
    - [masterfeats.2da](#masterfeats2da)
    - [movies.2da](#movies2da)
    - [stringtokens.2da](#stringtokens2da)
    - [tutorial\_old.2da](#tutorial_old2da)
    - [credits.2da](#credits2da)
    - [disease.2da](#disease2da)
    - [droiddischarge.2da](#droiddischarge2da)
    - [minglobalrim.2da](#minglobalrim2da)
    - [upcrystals.2da](#upcrystals2da)
    - [chargenclothes.2da](#chargenclothes2da)
    - [aliensound.2da](#aliensound2da)
    - [alienvo.2da](#alienvo2da)
    - [grenadesnd.2da](#grenadesnd2da)
    - [inventorysnds.2da](#inventorysnds2da)
    - [areaeffects.2da](#areaeffects2da)

---

<!-- Anchors for TOC links to 2DA files that do not have a dedicated subsection -->
<a id="actions2da"></a>
<a id="ai_styles2da"></a>
<a id="aiscripts2da"></a>
<a id="aliensound2da"></a>
<a id="alienvo2da"></a>
<a id="areaeffects2da"></a>
<a id="bodyvariation2da"></a>
<a id="chargenclothes2da"></a>
<a id="cls_atk_2da"></a>
<a id="cls_savthr_2da"></a>
<a id="creaturesize2da"></a>
<a id="credits2da"></a>
<a id="crtemplates2da"></a>
<a id="environment2da"></a>
<a id="gamespyrooms2da"></a>
<a id="hen_companion2da"></a>
<a id="hen_familiar2da"></a>
<a id="humanfirst2da"></a>
<a id="humanlast2da"></a>
<a id="iprp_abilities2da"></a>
<a id="iprp_acmodtype2da"></a>
<a id="iprp_aligngrp2da"></a>
<a id="iprp_ammocost2da"></a>
<a id="iprp_ammotype2da"></a>
<a id="iprp_attackmod2da"></a>
<a id="iprp_bonusfeat2da"></a>
<a id="iprp_combatdam2da"></a>
<a id="iprp_costtable2da"></a>
<a id="iprp_damagecost2da"></a>
<a id="iprp_damagered2da"></a>
<a id="iprp_damagevs2da"></a>
<a id="iprp_damagetype2da"></a>
<a id="iprp_feats2da"></a>
<a id="iprp_immunity2da"></a>
<a id="iprp_lightcol2da"></a>
<a id="iprp_monstdam2da"></a>
<a id="iprp_mosterhit2da"></a>
<a id="iprp_onhit2da"></a>
<a id="iprp_paramtable2da"></a>
<a id="iprp_protection2da"></a>
<a id="iprp_saveelement2da"></a>
<a id="iprp_savingthrow2da"></a>
<a id="iprp_skillcost2da"></a>
<a id="iprp_spellres2da"></a>
<a id="iprp_spells2da"></a>
<a id="iprp_traptype2da"></a>
<a id="iprp_walk2da"></a>
<a id="iprp_weightinc2da"></a>
<a id="itempropsdef2da"></a>
<a id="merchants2da"></a>
<a id="minglobalrim2da"></a>
<a id="musictable2da"></a>
<a id="palette2da"></a>
<a id="phenotype2da"></a>
<a id="rumble2da"></a>
<a id="soundeax2da"></a>
<a id="textures2da"></a>
<a id="tilecolor2da"></a>
<a id="tutorial_old2da"></a>
<a id="videoquality2da"></a>

## file structure Overview

2DA files are tabular game data; role in modding and merge workflows: see the **2DA** section on [Concepts](Concepts). On disk in game archives they use binary version **`V2.b`** and the `.2da` extension. The engine loads them with the same *[resource resolution order](Concepts#resource-resolution-order)* as other resources:

- override
- module [RIM](Container-Formats#rim)
- [MOD](Container-Formats#erf)
- save
- [KEY](Container-Formats#key)
- [BIF](Container-Formats#bif)

PyKotor's 2DA implementation lives in `Libraries/PyKotor/src/pykotor/resource/formats/twoda/`, with binary `V2.b` parsing and writing in `io_twoda.py`, CSV interchange support in `io_twoda_csv.py`, and format detection/dispatch in `twoda_auto.py`. The in-memory table model itself is defined in `twoda_data.py`. Equivalent binary-layout readers or writers exist in reone, xoreos, Kotor.NET, KotOR.js, KotOR-Unity, and reubenduncan's `kotor` notes. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [`io_twoda_csv.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda_csv.py), [`twoda_auto.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py), [`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [Kotor.NET `TwoDABinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/Kotor2DA/TwoDABinaryStructure.cs), [KotOR.js `TwoDAObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TwoDAObject.ts), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

### See also

- [TSLPatcher 2DAList Syntax](TSLPatcher-Data-Syntax#2dalist-syntax) - Modding 2DA files with *TSLPatcher*
- [GFF File Format](GFF-File-Format) - Related format that often references *2DA* data
- [TLK File Format](Audio-and-Localization-Formats#tlk) - Text strings referenced by *2DA* entries

---

## format

The sections below document the **binary `V2.b`** layout used by the KotOR engine in packed resources (see overview above for PyKotor module split).

### File Header

The file header is `9` bytes in size:

| Name         | type    | offset | size | Description                                    |
| ------------ | ------- | ------ | ---- | ---------------------------------------------- |
| file type    | [char](GFF-File-Format#gff-data-types) | `0` (0x00) | `4`    | Four-byte type tag written as `"2DA "` in the parsers cited below |
| file Version | [char](GFF-File-Format#gff-data-types) | `4` (0x04) | `4`    | Always `"V2.b"`              |
| Line Break   | [uint8](GFF-File-Format#gff-data-types)   | `8` (0x08) | `1`    | Newline character (`\n`, value `0x0A`)        |

PyKotor validates a literal "2DA " file type followed by "V2.b" and a newline; reone checks for the eight-byte "2DA V2.b" signature before skipping the newline; KotOR.js and KotOR-Unity both write or read the same space-padded form; and xoreos defines both "2DA " and "2DA\t" constants in its parser code while its binary writer emits "2DA V2.b\n". The safest cross-parser statement is therefore that the normal binary header in active KotOR tooling is "2DA " + "V2.b" + "\n". [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [KotOR.js `TwoDAObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TwoDAObject.ts), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs)]

### Column Headers

Column headers immediately follow the header, terminated by a [null byte](https://en.cppreference.com/w/c/string/byte):

| Name            | type    | Description                                                      |
| --------------- | ------- | ---------------------------------------------------------------- |
  | Column Headers  | [char](GFF-File-Format#gff-data-types)[]  | [Tab-separated](https://en.wikipedia.org/wiki/Tab-separated_values) column names (e.g., `"label\tname\tdescription"`) |
| [Null Terminator](https://en.cppreference.com/w/c/string/byte) | [uint8](GFF-File-Format#gff-data-types)   | Single [null byte](https://en.cppreference.com/w/c/string/byte) (`\0`) marking end of headers                   |

Each column name is terminated by a tab character (`0x09`), and the entire header list is terminated by a [null byte](https://en.cppreference.com/w/c/string/byte) (`0x00`). PyKotor, reone, xoreos, Kotor.NET, and the reubenduncan parsers all follow that same header walk. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [Kotor.NET `TwoDABinaryStructure.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/Kotor2DA/TwoDABinaryStructure.cs), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

### Row Count

| Name      | type    | offset | size | Description                    |
| --------- | ------- | ------ | ---- | ------------------------------ |
| Row Count | UInt32  | varies | 4    | Number of data rows in the file ([little-endian](https://en.wikipedia.org/wiki/Endianness)) |

The row count is stored as a 32-bit little-endian integer, and that value determines how many row labels follow and how many cell offsets must be read. PyKotor reads it as `uint32`, reone reads it as `Uint32`, xoreos writes it as `writeUint32LE`, and the reubenduncan notes describe the same slot. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

### Row Labels

Row labels immediately follow the row count:

| Name       | type    | Description                                                      |
| ---------- | ------- | ---------------------------------------------------------------- |
| Row Labels | [char](GFF-File-Format#gff-data-types)[]  | [Tab-separated](https://en.wikipedia.org/wiki/Tab-separated_values) row labels (one per row, typically numeric)       |

Each row label is read as a [tab-terminated](#column-headers) string (tab character `0x09`). Row labels are usually numeric (`"0"`, `"1"`, `"2"`...) but can be arbitrary strings.

**Important**: The row label list is **not** terminated by a [null byte](https://en.cppreference.com/w/c/string/byte) (`0x00`), so the reader must consume exactly `row_count` labels from the count field. This differs from column headers, which do use a [null terminator](https://en.cppreference.com/w/c/string/byte). PyKotor, reone, KotOR-Unity, and the reubenduncan notes all implement or describe that bounded read. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

### Cell Data Offsets

After row labels, cell data offsets are stored:

| Name            | type     | size | Description                                                      |
| --------------- | -------- | ---- | ---------------------------------------------------------------- |
| Cell Offsets    | [uint16](GFF-File-Format#gff-data-types)[] | `2`×`N`  | [Array](https://en.wikipedia.org/wiki/Array_data_structure) of offsets into the cell data string table. Row-major size *N* uses:<br>- [row_count](#row-labels)<br>- [column_count](#column-headers)<br>Values are stored [little-endian](https://en.wikipedia.org/wiki/Endianness). |
| Cell Data Size  | [uint16](GFF-File-Format#gff-data-types)   | `2`    | Total size of cell data string table in bytes ([little-endian](https://en.wikipedia.org/wiki/Endianness))   |

Each cell has a 16-bit unsigned integer offset ([little-endian](https://en.wikipedia.org/wiki/Endianness)) pointing to its string value in the cell data string table. Offsets are stored in [row-major order](https://en.wikipedia.org/wiki/Row-_and_column-major_order) (all cells of row `0`, then all cells of row `1`, etc.). The cell data size field immediately follows the offset array and precedes the actual cell data.

**Important**: Offsets are relative to the start of the cell data string table (immediately after `cell_data_size`). Multiple cells can share one offset when they contain identical strings, enabling data *[deduplication](https://en.wikipedia.org/wiki/Data_deduplication)*, which is explicitly implemented in PyKotor's writer and described in reone, xoreos, KotOR.js, and the reubenduncan notes. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [reone `2dareader.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp), [xoreos `2dafile.cpp`](https://github.com/xoreos/xoreos/blob/master/src/aurora/2dafile.cpp), [KotOR.js `TwoDAObject.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/resource/TwoDAObject.ts), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

### Cell Data String Table

The cell data string table contains all cell values as *[null-terminated](https://en.cppreference.com/w/c/string/byte)* strings:

| Name         | type   | Description                                                      |
| ------------ | ------ | ---------------------------------------------------------------- |
| Cell strings | [char](GFF-File-Format#gff-data-types)[] | *[Null-terminated](https://en.cppreference.com/w/c/string/byte)* strings, *[deduplicated](https://en.wikipedia.org/wiki/Data_deduplication)* (same value shares offset) |

The cell data string table begins immediately after the `cell_data_size` field. Each string is *[null-terminated](https://en.cppreference.com/w/c/string/byte)* (`0x00`). PyKotor's readers return empty strings when an offset is out of range or when a cell points at an empty terminator, while `twoda_data.py` and the reubenduncan parser both preserve `"****"` as a common explicit no-value sentinel in table content. The table is *[deduplicated](https://en.wikipedia.org/wiki/Data_deduplication)*, so multiple cells can share one offset. [[`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py), [`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [KotOR-Unity `2DAObject.cs`](https://github.com/reubenduncan/KotOR-Unity/blob/master/Assets/Scripts/FileObjects/2DAObject.cs), [kotor `docs/2da.md`](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md)]

**Reading process**: For each cell, the reader retrieves the 16-bit offset from the offset array (`row_index × column_count + column_index`), seeks to `cell_data_start_position + offset`, and reads a *[null-terminated](https://en.cppreference.com/w/c/string/byte)* string at that location. This behavior and the `"****"` empty-cell convention are consistent across [reone `2dareader.cpp` L54-L65](https://github.com/seedhartha/reone/blob/master/src/libs/resource/format/2dareader.cpp#L54-L65), [xoreos `2dafile.cpp` L319-L335](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L319-L335) and [`2dafile.cpp` L63-L64](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/aurora/2dafile.cpp#L63-L64), [KotOR-Unity `2DAObject.cs` L85-L100](https://github.com/reubenduncan/KotOR-Unity/blob/da59c0e3b16e351479e543d455bb39b6811f7239/Assets/Scripts/FileObjects/2DAObject.cs#L85-L100), and [kotor `docs/2da.md` L57-L64](https://github.com/reubenduncan/kotor/blob/master/docs/2da.md#L57-L64).

---

## Data Structure

### `TwoDA` Object

PyKotor's in-memory `TwoDA` object stores rows as `list[dict[str, str]]`, headers as an ordered `list[str]`, row labels as an ordered `list[str]`, and an auxiliary `_label_to_index` dictionary for O(1) label lookup. The same class also exposes JSON serialization, row iteration that yields `TwoDARow` wrappers, structural helpers such as `shape`, `columns`, and `index`, and mutators such as `add_column`, `remove_column`, `set_label`, `add_row`, `copy_row`, and `remove_row`. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py)]

That design is intentionally string-backed: PyKotor stores every parsed cell as a Python string in the table core and layers typed conversion on top only when callers ask for it. This is consistent with the binary format described above, where cells resolve through the shared string table rather than through per-column typed storage. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py)]

### `TwoDARow` Object

`TwoDARow` is a light wrapper around one row label plus one `dict[str, str]` cell map. Its accessors expose the same underlying string data through `get_string`, `get_integer`, `get_float`, and `get_enum`, while `update_values` and `set_string` write back into the same row map. In other words, the row object is a typed access facade over string-backed storage, not a second typed copy of the table. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py)]

---

## Cell value types

At the storage level, PyKotor treats every 2DA cell as text. `TwoDARow.get_string` returns the raw string, while `get_integer`, `get_float`, and `get_enum` are opt-in conversions layered on top of that string value. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py)]

The third comparator binary confirms that this string-backed model also exists in BioWare's native runtime API: Aurora's `C2DA` class exposes `GetCExoStringEntry @ (/K1/k1_win_gog_swkotor.exe @ 0x00413de0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6730)`, `GetINTEntry @ (/K1/k1_win_gog_swkotor.exe @ 0x00414110, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6e00)`, `GetFLOATEntry @ (/K1/k1_win_gog_swkotor.exe @ 0x00413350, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6af0)`, and `SetBlankEntry @ (/K1/k1_win_gog_swkotor.exe @ TODO: Find this address, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a8830)`, which is exactly the split between raw string storage and typed interpretation. # Reference: /K1/k1_win_gog_swkotor.exe @ 0x00413de0, /K1/k1_win_gog_swkotor.exe @ 0x00414110, /K1/k1_win_gog_swkotor.exe @ 0x00413350, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6730, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6e00, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a6af0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a8830

PyKotor's extraction registry shows how that interpretation is applied in practice for KotOR data. It groups columns into StrRef-bearing tables, generic ResRef-bearing tables, and narrower model, sound, music, texture, GUI, and script-reference families, which is stronger evidence than describing 2DA cells as if the file format itself had hardcoded scalar types. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

Examples from the local registry include StrRef columns in `classes.2da`, `feat.2da`, `skills.2da`, `spells.2da`, and `itemprops.2da`; model or texture-style ResRef columns in `appearance.2da`, `baseitems.2da`, `placeables.2da`, and `heads.2da`; and audio-oriented ResRef columns in `ambientmusic.2da`, `ambientsound.2da`, `footstepsounds.2da`, `guisounds.2da`, and `inventorysnds.2da`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

`"****"` is best described as a common content-level no-value *sentinel* rather than as a separate storage type. PyKotor's `twoda_data.py` documents it as a conventional explicit empty marker, while the binary parser itself still reads the underlying payload as ordinary strings via offsets into the shared string table. [[`twoda_data.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_data.py), [`io_twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/formats/twoda/io_twoda.py)]

---

## Confirmed Engine Usage

Three analyzed binaries expose the same underlying 2DA subsystem even though symbol recovery quality differs between them. KotOR I exposes `C2DA @ (/K1/k1_win_gog_swkotor.exe @ 0x00413cc0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a62b0)`, `CRes2DA @ (/K1/k1_win_gog_swkotor.exe @ 0x0041d730, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x14019e2b0)`, `Load2DArray @ (/K1/k1_win_gog_swkotor.exe @ 0x004143b0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00621e70, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a73a0)`, and `Unload2DArray @ (/K1/k1_win_gog_swkotor.exe @ 0x004139e0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a9b10)`. KotOR II retains `Load2DArray` plus a large `Load2DArrays_*` family, while Aurora exposes the generic cache manager `CTwoDimArrays::Load2DArrays @ (/K1/k1_win_gog_swkotor.exe @ TODO: Find this address, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b3920)` together with `GetCached2DA @ (/K1/k1_win_gog_swkotor.exe @ TODO: Find this address, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b31e0)` and `ClearCached2DAs @ (/K1/k1_win_gog_swkotor.exe @ TODO: Find this address, /TSL/k2_win_gog_aspyr_swkotor2.exe @ TODO: Find this address, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b2fe0)`. # Reference: /K1/k1_win_gog_swkotor.exe @ 0x00413cc0, /K1/k1_win_gog_swkotor.exe @ 0x0041d730, /K1/k1_win_gog_swkotor.exe @ 0x004143b0, /K1/k1_win_gog_swkotor.exe @ 0x004139e0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00621e70, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a62b0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x14019e2b0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a73a0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1401a9b10, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b3920, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b31e0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x1402b2fe0

The KotOR executables also preserve many table-specific loader entry points by name. Verified examples include `Load2DArrays_Appearance @ (/K1/k1_win_gog_swkotor.exe @ 0x005c0270, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00480c10, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: KotOR-specific specialization not present)`, `Load2DArrays_Spells @ (/K1/k1_win_gog_swkotor.exe @ 0x005c3e10, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x004853f0, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`, `Load2DArrays_Placeables @ (/K1/k1_win_gog_swkotor.exe @ 0x005c1830, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00482800, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`, `Load2DArrays_SurfaceMaterial @ (/K1/k1_win_gog_swkotor.exe @ 0x005c0bb0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00481830, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`, and `Load2DArrays_VisualEffect @ (/K1/k1_win_gog_swkotor.exe @ 0x005c0c80, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00481920, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`. # Reference: /K1/k1_win_gog_swkotor.exe @ 0x005c0270, /K1/k1_win_gog_swkotor.exe @ 0x005c3e10, /K1/k1_win_gog_swkotor.exe @ 0x005c1830, /K1/k1_win_gog_swkotor.exe @ 0x005c0bb0, /K1/k1_win_gog_swkotor.exe @ 0x005c0c80, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00480c10, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x004853f0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00482800, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00481830, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00481920

For shared table names, the string evidence is also present in all three analyzed binaries. `Appearance` appears at `(/K1/k1_win_gog_swkotor.exe @ 0x00746efc, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098845c, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc50b0)`, `CLASSES` at `(/K1/k1_win_gog_swkotor.exe @ 0x007488ec, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cc58, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4cd8)`, `Skills` at `(/K1/k1_win_gog_swkotor.exe @ 0x00748a1c, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cd5c, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc51fc)`, `SPELLS` at `(/K1/k1_win_gog_swkotor.exe @ 0x0074a4d0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b8cc, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc56d8)`, `BASEITEMS` at `(/K1/k1_win_gog_swkotor.exe @ 0x0074b294, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b4c4, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc39b8)`, and `Feat` or feat-related table labels at `(/K1/k1_win_gog_swkotor.exe @ 0x00748ca0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00986500, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4958)`. # Reference: /K1/k1_win_gog_swkotor.exe @ 0x00746efc, /K1/k1_win_gog_swkotor.exe @ 0x007488ec, /K1/k1_win_gog_swkotor.exe @ 0x00748a1c, /K1/k1_win_gog_swkotor.exe @ 0x0074a4d0, /K1/k1_win_gog_swkotor.exe @ 0x0074b294, /K1/k1_win_gog_swkotor.exe @ 0x00748ca0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098845c, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cc58, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cd5c, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b8cc, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b4c4, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00986500, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc50b0, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4cd8, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc51fc, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc56d8, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc39b8, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4958

That is enough to say, conservatively, that 2DA is not merely a file-format convention in KotOR-era tooling; it is an engine-level runtime system with generic table loaders, cache-management helpers, typed accessors, and many named table consumers. It is not enough yet to keep every historic per-table claim that previously appeared in this section, so the remaining catalog below should be read as a documented table inventory unless a subsection explicitly adds its own loader evidence. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [reone `src/libs/resource/parser/2da/`](https://github.com/seedhartha/reone/tree/master/src/libs/resource/parser/2da)]

## Known 2DA Files

KotOR and TSL ship a large set of 2DA tables. The sections below group them by system and call out engine usage, column definitions, and the data each table drives. Engine usage descriptions are derived from the `Confirmed Engine Usage` loading analysis above, reone's dedicated 2DA table parsers ([`src/libs/resource/parser/2da/`](https://github.com/seedhartha/reone/tree/master/src/libs/resource/parser/2da)), and PyKotor's extraction metadata ([`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)).

---

## Character & Combat *2DA* files

### `appearance.2da`

**Engine Usage**: `appearance.2da` is the appearance-to-rendering lookup table that KotOR uses for creature presentation and related physical metadata. The table name is present as `Appearance` in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x00746efc, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098845c, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc50b0)`, and KotOR I plus KotOR II both retain dedicated appearance loaders `Load2DArrays_Appearance @ (/K1/k1_win_gog_swkotor.exe @ 0x005c0270, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00480c10, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`. PyKotor and Holocron Toolset also treat it as a first-class cached table through `TwoDARegistry.APPEARANCES` and `HTInstallation.TwoDA_APPEARANCES`, and reone ships a dedicated `appearance.cpp` parser plus downstream creature usage. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [reone `appearance.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/parser/2da/appearance.cpp), [reone `creature.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/creature.cpp)]

- 3D [model](MDL-MDX-File-Format) *ResRefs*
- [texture](Texture-Formats#tpc) assignments
- Race associations and physical properties
- Which [model](MDL-MDX-File-Format) to display
- Which [textures](Texture-Formats#tpc) to display
- Hit detection inputs
- [animations](MDL-MDX-File-Format#animation-header)

**Row index**: Appearance ID (*integer*, typically `0`-based)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* (optional) | Human-readable label for the appearance |
| `modeltype` | *String* | [model](MDL-MDX-File-Format) type identifier (e.g., "F", "B", "P") |
| `modela` through `modeln` | *ResRef* (optional) | [model](MDL-MDX-File-Format) *ResRefs* for different body parts or variations ([models](MDL-MDX-File-Format) a-n) |
| `texa` through `texn` | *ResRef* (optional) | [texture](Texture-Formats#tpc) *ResRefs* for different body parts ([textures](Texture-Formats#tpc) a-n) |
| `texaevil`, `texbevil`, `texievil`, `texlevil`, `texnevil` | *ResRef* (optional) | Dark side variant [textures](Texture-Formats#tpc) *ResRefs* |
| `race` | *ResRef* (optional) | Race identifier *ResRef* |
| `racetex` | *ResRef* (optional) | Race-specific [texture](Texture-Formats#tpc) *ResRef* |
| `racialtype` | *Integer* | Numeric racial type identifier |
| `normalhead` | *Integer* (optional) | Default head appearance ID |
| `backuphead` | *Integer* (optional) | Fallback head appearance ID |
| `portrait` | *ResRef* (optional) | Portrait image *ResRef* |
| `skin` | *ResRef* (optional) | Skin [texture](Texture-Formats#tpc) *ResRef* |
| `headtexe`, `headtexg`, `headtexve`, `headtexvg` | *ResRef* (optional) | Head [texture](Texture-Formats#tpc) *ResRefs* variations |
| `headbone` | *String* (optional) | Bone name for head attachment |
| `height` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Character height multiplier |
| `hitdist` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Hit detection distance |
| `hitradius` | [Float](https://en.wikipedia.org/wiki/Single-precision_floating-point_format) | Hit detection radius |
| `sizecategory` | *Integer* | size category (affects combat calculations) |
| `moverate` | *String* | Movement rate identifier |
| `walkdist` | *Float* | Walking distance threshold |
| `rundist` | *Float* | Running distance threshold |
| `prefatckdist` | *Float* | Preferred attack distance |
| `creperspace` | *Float* | Creature personal space radius |
| `perspace` | *Float* | Personal space radius |
| `cameraspace` | *Float* (optional) | Camera space offset |
| `cameraheightoffset` | *String* (optional) | Camera height offset |
| `targetheight` | *String* | Target height for combat |
| `perceptiondist` | *Integer* | Perception distance |
| `headArcH` | *Integer* | Head horizontal arc angle |
| `headArcV` | *Integer* | Head vertical arc angle |
| `headtrack` | *Boolean* | Whether head tracking is enabled |
| `hasarms` | *Boolean* | Whether creature has arms |
| `haslegs` | *Boolean* | Whether creature has legs |
| `groundtilt` | *Boolean* | Whether ground tilt is enabled |
| `footsteptype` | *Integer* (optional) | Footstep sound type |
| `footstepsound` | *ResRef* (optional) | Footstep sound *ResRef* |
| `footstepvolume` | *Boolean* | Whether footstep volume is enabled |
| `armorSound` | *ResRef* (optional) | Armor sound effect *ResRef* |
| `combatSound` | *ResRef* (optional) | Combat sound effect *ResRef* |
| `soundapptype` | *Integer* (optional) | Sound appearance type |
| `bloodcolr` | *String* | Blood color identifier |
| `deathvfx` | *Integer* (optional) | Death visual effect ID |
| `deathvfxnode` | *String* (optional) | Death VFX attachment [node](MDL-MDX-File-Format#node-structures) |
| `fadedelayondeath` | *Boolean* (optional) | Whether to fade on death |
| `destroyobjectdelay` | *Boolean* (optional) | Whether to delay object destruction |
| `disableinjuredanim` | *Boolean* (optional) | Whether to disable injured [animations](MDL-MDX-File-Format#animation-header) |
| `abortonparry` | *Boolean* | Whether to abort on parry |
| `freelookeffect` | *Integer* (optional) | Free look effect ID |
| `equipslotslocked` | *Integer* (optional) | Locked equipment slot flags |
| `weaponscale` | *String* (optional) | Weapon scale multiplier |
| `wingTailScale` | *Boolean* | Whether wing/tail scaling is enabled |
| `helmetScaleF` | *String* (optional) | Female helmet scale |
| `helmetScaleM` | *String* (optional) | Male helmet scale |
| `envmap` | *ResRef* (optional) | Environment map [texture](Texture-Formats#tpc) *ResRef* |
| `bodyBag` | *Integer* (optional) | Body bag appearance ID |
| `stringRef` | *Integer* (optional) | *String* reference for appearance name |
| `driveaccl` | *Integer* | Vehicle drive acceleration |
| `drivemaxspeed` | *Float* | Vehicle maximum speed |
| `driveanimwalk` | *Float* | Vehicle walk [animation](MDL-MDX-File-Format#animation-header) speed |
| `driveanimrunPc` | *Float* | PC vehicle run [animation](MDL-MDX-File-Format#animation-header) speed |
| `driveanimrunXbox` | *Float* | Xbox vehicle run [animation](MDL-MDX-File-Format#animation-header) speed |

**Column Details**:

The full row shape shown above is not guesswork from old docs; it is mirrored closely by reone's generated `parseAppearanceTwoDARow`, which explicitly reads the listed fields from a generic `TwoDA` object. That parser is not the original BioWare runtime, but it is a concrete source-backed external implementation that matches the local PyKotor registry families for appearance StrRefs, model ResRefs, texture ResRefs, and related creature-facing fields. [[reone `appearance.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/parser/2da/appearance.cpp), [`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

- [model](MDL-MDX-File-Format) columns: `modela` through `modeln` (14 [model](MDL-MDX-File-Format) variations)
- [texture](Texture-Formats#tpc) columns: `texa` through `texn` (14 [texture](Texture-Formats#tpc) variations)
- Evil [texture](Texture-Formats#tpc) columns: `texaevil`, `texbevil`, `texievil`, `texlevil`, `texnevil`
- Head [texture](Texture-Formats#tpc) columns: `headtexe`, `headtexg`, `headtexve`, `headtexvg`
- Movement: `walkdist`, `rundist`, `prefatckdist`, `moverate`
- Physical properties: `height`, `hitdist`, `hitradius`, `sizecategory`, `perceptiondist`
- Personal space: `perspace`, `creperspace`
- Camera: `cameraspace`, `cameraheightoffset`, `targetheight`
- Head tracking: `headArcH`, `headArcV`, `headtrack`
- Body parts: `hasarms`, `haslegs`, `groundtilt`, `wingTailScale`
- Footsteps: `footsteptype`, `footstepsound`, `footstepvolume`
- Sounds: `armorSound`, `combatSound`, `soundapptype`
- Visual effects: `deathvfx`, `deathvfxnode`, `fadedelayondeath`, `freelookeffect`
- Equipment: `equipslotslocked`, `weaponscale`, `helmetScaleF`, `helmetScaleM`
- [textures](Texture-Formats#tpc): `envmap`, `skin`, `portrait`, `race`, `racetex`, `racialtype`
- Heads: `normalhead`, `backuphead`, `headbone`
- Vehicle: `driveaccl`, `drivemaxspeed`, `driveanimwalk`, `driveanimrunPc`, `driveanimrunXbox`
- Other: `bloodcolr`, `bodyBag`, `stringRef`, `abortonparry`, `destroyobjectdelay`, `disableinjuredanim`

PyKotor's local registry confirms the most important appearance-facing column families directly: K1 and K2 both mark `string_ref` as the talk-table column, `race` as a generic ResRef-bearing column, `modela` through at least `modelj` as model-bearing columns, and `racetex`, `texa` through `texj`, plus the head texture variants, as texture-bearing columns. Holocron Toolset then uses the cached table as an installation-scoped selector source in creature-oriented editors such as UTC. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py)]

### [baseitems.2da](#baseitems2da)

**Engine Usage**: `baseitems.2da` is the canonical item-class table for combat, equipment, and inventory behavior. The table string `BASEITEMS` is present in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x0074b294, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b4c4, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc39b8)`, and PyKotor plus Holocron Toolset expose it as `TwoDARegistry.BASEITEMS` and `HTInstallation.TwoDA_BASEITEMS`; the toolset then consumes it directly in item and creature editors for label lookup, model selection, and base-item classification. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`uti.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/uti.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py)]

**Row index**: Base item ID (*integer*)

**Verified local column families**:

- `label`: used by Holocron Toolset for base-item display text and name lookup. [[`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py)]
- `itemclass`: used by Holocron Toolset to derive inventory icon resrefs such as `i{itemclass}_{variation}`. [[`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py)]
- `defaultmodel`: registered by PyKotor as a model-bearing column in both games. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `defaulticon`: registered by PyKotor as a texture-bearing column in both games. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `itemclass`, `baseitemstatref`: registered by PyKotor as item-reference-bearing columns in both games. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `powerupsnd`, `powerdownsnd`, `poweredsnd`: registered by PyKotor as sound-reference-bearing columns in both games. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

The previous larger base-item column table mixed solid evidence with inherited prose and needs a line-by-line rebuild before it can be trusted at the same level as the top half of this page. For now, the safer statement is that `baseitems.2da` is unquestionably engine-visible and tool-visible, but this wiki should only assert the narrower subset of columns that local registry code and live tool consumers actually expose. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`uti.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/uti.py), [`inventory.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/dialogs/inventory.py)]

---

### [classes.2da](#classes2da)

**Engine Usage**: `classes.2da` is the class-id table used by creature and savegame tooling, and the `CLASSES` table name is present in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x007488ec, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cc58, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4cd8)`. PyKotor registers it as `TwoDARegistry.CLASSES`, Holocron Toolset exposes the same file as `HTInstallation.TwoDA_CLASSES`, and reone ships a dedicated `class.cpp` loader for the same table family. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [reone `class.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/d20/class.cpp)]

**Row index**: Class ID (integer)

**Verified local column and consumer evidence**:

- `name`, `description` are the directly declared StrRef-bearing columns for `classes.2da` in both K1 and K2 within PyKotor's 2DA registry. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `label` is a live UI-facing column in Holocron Toolset: the UTC editor populates `class1Select` and `class2Select` from `classes.get_column("label")`, and the savegame editor resolves class ids back to `classes.get_cell(class_id, "label")` when present. [[`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]
- The generated UTC editor help text documents `ClassList[0].Class` and `ClassList[1].Class` as indices into `classes.2da`, and PyKotor's UTC reader consumes those values from `ClassList` as raw class ids. [[`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py)]
- Each `ClassList` entry also owns a `KnownList0` power list in the UTC structure, which is local evidence that class rows participate in power progression and lookup even though the full row schema still needs a stricter column-by-column rebuild. [[`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [reone `class.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/d20/class.cpp)]

The older large column table for `classes.2da` mixed verified content with inherited schema prose. Until that row layout is re-checked field by field against live code, this page keeps only the narrower subset above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]

---

### [feat.2da](#feat2da)

**Engine Usage**: `feat.2da` is the feat-id table used by creature blueprints, save data, and open-engine consumers, and feat-related table strings are present in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x00748ca0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00986500, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc4958)`. PyKotor exposes the file as `TwoDARegistry.FEATS`, Holocron Toolset caches it as `HTInstallation.TwoDA_FEATS`, and reone plus KotOR.js both ship explicit feat loaders or feat model types. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [reone `feats.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/d20/feats.cpp), [KotOR.js `TalentFeat.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/talents/TalentFeat.ts)]

**Row index**: Feat ID (integer)

**Verified local column and consumer evidence**:

- `name`, `description` are the explicitly declared StrRef-bearing columns for `feat.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- PyKotor's registry maps GFF `Feat` and `FeatID` references back to the feats table, which is direct local evidence that feat ids are consumed as row indices rather than as free-form constants. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- The generated UTC editor help text documents each `FeatList` row as storing a feat index that references `feats.2da`, and the UTC reader consumes `FeatList` entries as raw feat ids from creature GFF data. [[`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py)]
- Holocron Toolset populates its creature feat checklist from the cached feats table and prefers the `name` StrRef when available, falling back to a direct string column when no talktable text resolves. The savegame editor likewise resolves stored feat ids back to feat labels through the same cached table. [[`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]

The previous larger feat schema table went beyond what the current local evidence proves field by field. Until that row shape is rebuilt against live code, this page keeps the directly verified subset above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]

---

### [skills.2da](#skills2da)

**Engine Usage**: `skills.2da` is the skill-id table used by character data and skill displays, and the table string `Skills` is present in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x00748a1c, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098cd5c, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc51fc)`. PyKotor exposes it as `TwoDARegistry.SKILLS`, Holocron Toolset caches it as `HTInstallation.TwoDA_SKILLS`, and reone plus KotOR.js both carry dedicated skill-loading code. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [reone `skills.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/d20/skills.cpp), [KotOR.js `TalentSkill.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/talents/TalentSkill.ts)]

**Row index**: Skill ID (integer)

**Verified local column and consumer evidence**:

- `name`, `description` are the directly declared StrRef-bearing columns for `skills.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- PyKotor's registry maps `SkillID` references back to the skills table, which is direct local evidence that skill references in higher-level resources are intended to resolve through `skills.2da`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- Creature GFF data stores skill ranks in the fixed `SkillList` array rather than storing free-form skill names. PyKotor's UTC reader enforces and reconstructs that `SkillList`, which is the local bridge between creature data and skills table ordering. [[`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py)]
- Holocron Toolset uses the cached skills table in savegame workflows, which is enough local evidence to keep the table's role in display and editing, but not enough yet to keep a full legacy row-schema table without stricter verification. [[`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]

The previous larger `skills.2da` schema block contained many plausible fields, but the currently re-verified local evidence proves only the smaller subset above. The rest should come back only after a line-by-line rebuild against code. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`savegame.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/savegame.py)]

---

### [spells.2da](#spells2da)

**Engine Usage**: `spells.2da` remains the inherited table name, but in KotOR it is the active Force-power table. The table string `SPELLS` is present in all three analyzed binaries at `(/K1/k1_win_gog_swkotor.exe @ 0x0074a4d0, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x0098b8cc, /Other BioWare Engines/Aurora/nwmain.exe @ 0x140dc56d8)`, KotOR I and KotOR II both retain dedicated `Load2DArrays_Spells` loader names, and PyKotor plus Holocron Toolset both register the file under their power-table constants rather than under a generic D&D-only name. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py), [reone `spells.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/d20/spells.cpp)]

**Row index**: Spell or Force-power ID (integer)

**Verified local column and consumer evidence**:

- `name` and `spelldesc` are the directly declared StrRef-bearing columns for `spells.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- PyKotor maps `Spell`, `SpellId`, and `Subtype` references back to the same power table, which is direct local evidence that higher-level data refers to rows in `spells.2da` by numeric id. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- The generated UTC editor help text states that `ClassList -> KnownList0/1/2` stores `Spell` ids that reference `spells.2da`, and PyKotor's UTC reader consumes those `Spell` values from creature GFF data exactly that way. [[`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py)]
- PyKotor's NWScript definition layer independently documents `GetLastForcePowerUsed` as returning a spell number that indexes `Spells.2da`, which is local evidence that the same numeric table ids leak into script-visible runtime APIs. [[`scriptdefs.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py)]
- Holocron Toolset caches the power table and populates creature power lists from it, preferring resolved names and falling back to label-style text where needed. [[`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utc.py)]

The earlier full `spells.2da` schema table was too broad for the current evidence set. The verified local code proves the table's role, its row-id usage, and a small number of column families; the rest should return only after a stricter rebuild. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`scriptdefs.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py)]

---

## Items & Properties 2DA files

### itemprops.2da

**Engine Usage**: Master table defining all item property types available in the game. Each row represents a property type (damage bonuses, ability score bonuses, skill bonuses, etc.) with their cost calculations and effect parameters. The engine uses this file to determine item property costs, effects, and availability.

**Row index**: Item property ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for property name |
| `costtable` | *String* | Cost calculation table reference |
| `param1` | *String* | Parameter 1 label |
| `param2` | *String* | Parameter 2 label |
| `subtype` | *Integer* | Property subtype identifier |
| `costvalue` | *Integer* | Base cost value |
| `param1value` | *Integer* | Parameter 1 default value |
| `param2value` | *Integer* | Parameter 2 default value |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Property description string reference |

The item property schema and behavior are evidenced by PyKotor K1/K2 field declarations plus editor/runtime consumers that load and resolve cost/parameter data from this table ([`twoda.py` L135](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L135), [`twoda.py` L313](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L313), [`installation.py` L74](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L74), [`uti.py` L107-L111](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L107-L111), [`uti.py` L278-L287](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L278-L287), [`uti.py` L449-L465](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L449-L465)).

---


### iprp_damagecost.2da

**Engine Usage**: Defines cost calculations for damage bonus item properties. Used to determine item property costs based on damage bonus values.

**Row index**: Damage bonus value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Damage bonus label |
| `cost` | *Integer* | Cost for this damage bonus value |

This table's naming and cost schema are tracked in both K1 and K2 column maps in PyKotor ([`twoda.py` L99](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L99), [`twoda.py` L277](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L277)).

---

## Objects & Area 2DA files

### [placeables.2da](#placeables2da)

**Engine and tool usage**: `placeables.2da` is the placeable-appearance lookup table for UTPs and scene rendering. The tri-binary section above already confirms that KotOR I and KotOR II retain `Load2DArrays_Placeables @ (/K1/k1_win_gog_swkotor.exe @ 0x005c1830, /TSL/k2_win_gog_aspyr_swkotor2.exe @ 0x00482800, /Other BioWare Engines/Aurora/nwmain.exe @ TODO: generic 2DA manager only)`. Locally, PyKotor exposes the table as `TwoDARegistry.PLACEABLES`, Holocron Toolset caches it as `HTInstallation.TwoDA_PLACEABLES`, the UTP editor uses its `label` column to populate appearance selection, and scene rendering resolves each `UTP.appearance_id` through `placeables.2da` to recover `modelname`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py), [`utp.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utp.py), [`scene_cache.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/scene/scene_cache.py)]

**Row index**: Placeable appearance ID or type ID (integer)

**Verified local columns and consumers**:

- `strref` is the directly declared string-bearing column for `placeables.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `modelname` is the directly declared model-bearing column for `placeables.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `label` is a live UI-facing column in Holocron Toolset: the UTP editor loads `placeables.2da` and uses `appearances.get_column("label")` to populate the appearance selector. [[`utp.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utp.py)]
- `UTP.appearance_id` is resolved back through the same table during scene rendering, and `scene_cache.py` explicitly reads `placeables.2da[row]["modelname"]` when constructing placeable render objects. [[`scene_cache.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/scene/scene_cache.py)]

The earlier full `placeables.2da` schema table was broader than the currently verified evidence. Until the remaining fields are rechecked against code or multi-binary analysis, this page keeps only the smaller subset above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`utp.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utp.py), [`scene_cache.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/gl/scene/scene_cache.py)]

---

### [genericdoors.2da](#genericdoors2da)

**Verified local usage**: `genericdoors.2da` is a live door-appearance lookup table in Holocron Toolset and PyKotor. PyKotor exposes the file through `TwoDARegistry.DOORS`, its K1 and K2 registries declare `strref` as the table's string-bearing column and `modelname` as its model-bearing column, and the door editor caches `genericdoors.2da` immediately on startup. The same editor validates `UTD.appearance_id` against the table height, resolves the preview model through `door.get_model(..., genericdoors=...)`, and explicitly reports the lookup as `genericdoors.2da[row]['modelname']`. The generated UTD help text also documents the door `Appearance` field as an index into `doortypes.2da` or `genericdoors.2da` that picks the 3D model and behavior. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utd.py), [`toolset/uic/qtpy/editors/utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utd.py)]

**Row index**: Door type ID (integer)

**Verified local columns and consumers**:

- `strref` is the directly declared string-bearing column for `genericdoors.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `modelname` is the directly declared model-bearing column for `genericdoors.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `modelname` is also the live preview lookup used by Holocron Toolset's UTD editor when resolving the current door model from `UTD.appearance_id`. [[`utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utd.py)]

The previous full `genericdoors.2da` schema block was broader than the evidence currently rechecked in source. Until the remaining fields are re-verified against live code or binary analysis, this page keeps only the narrower subset above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/utd.py)]

---

### [doortypes.2da](#doortypes2da)

**Verified local usage**: `doortypes.2da` is the sibling door table that PyKotor's K1 and K2 registries track alongside `genericdoors.2da`. The registry declares `stringrefgame` as its string-bearing column and `model` as its model-bearing column, and the generated UTD help text explicitly describes the `Appearance` field as an index into `doortypes.2da` or `genericdoors.2da`. That is enough local evidence to keep the table's role as a door-appearance/configuration source, but not enough yet to preserve a larger inherited row-schema description without a stricter line-by-line rebuild. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`toolset/uic/qtpy/editors/utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utd.py)]

**Row index**: Door type ID (integer)

**Verified local columns**:

- `stringrefgame` is the directly declared string-bearing column for `doortypes.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `model` is the directly declared model-bearing column for `doortypes.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

The older `doortypes.2da` schema block went beyond what the currently rechecked local evidence proves. The safer statement is that `doortypes.2da` remains a documented sibling door table with string and model columns, and that higher-level door editors still acknowledge it as a valid appearance source. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`toolset/uic/qtpy/editors/utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utd.py)]

---

### [soundset.2da](#soundset2da)

**Verified local usage**: `soundset.2da` is the table that creature data uses to choose a sound-set row by numeric id. PyKotor exposes the file as `TwoDARegistry.SOUNDSETS`, declares `strref` as its string-bearing column in both K1 and K2 registries, and maps the UTC `SoundSetFile` GFF field back to `soundset.2da`. PyKotor's UTC reader stores that field as `soundset_id`, and Holocron Toolset's generated UTC help text documents it as a WORD index into `soundset.2da` that chooses creature dialogue and battle sounds. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py)]

**Row index**: Sound set ID (integer)

**Verified local columns and consumers**:

- `strref` is the directly declared string-bearing column for `soundset.2da` in PyKotor's K1 and K2 registries. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `SoundSetFile` is the GFF field that PyKotor maps back to `soundset.2da`, and the UTC reader reads and writes it as `utc.soundset_id`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py)]
- Holocron Toolset's UTC editor tooltip explicitly describes the field as an index into `soundset.2da` that changes dialogue and battle sounds. [[`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py)]

The earlier `soundset.2da` schema block was broader than the currently rechecked evidence. Until additional columns are re-verified against code or binary analysis, this page keeps only the smaller subset above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py)]

---

## Visual Effects & [animations](MDL-MDX-File-Format#animation-header) 2DA files

### [visualeffects.2da](#visualeffects2da)

**Verified local usage**: The currently rechecked local linkage for `visualeffects.2da` is PyKotor's GFF-to-2DA mapping from `VisualType` to this table. That proves the page's object-level contract: some GFF resources store a numeric `VisualType` that should be interpreted as a row index into `visualeffects.2da`. PyKotor's script library also preserves many hard-coded `SetEffectIcon(...)` calls, but those point to `effecticon.2da`, not to `visualeffects.2da`, so they are not evidence for this table's row schema. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`common/scriptlib.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptlib.py)]

**Row index**: Visual effect ID (integer)

**Verified local fields and limits**:

- `VisualType` is the rechecked field name that PyKotor binds to `visualeffects.2da`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- The current local registry pass does not enumerate a trusted column family for `visualeffects.2da`, so the inherited giant schema table was removed rather than kept as unsupported prose. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

Until a fresh parser-level or binary-backed reconstruction is completed, the only safe statement here is that `visualeffects.2da` provides row targets for `VisualType` references. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]

---

### [portraits.2da](#portraits2da)

**Verified local usage**: `portraits.2da` is the table PyKotor maps from the GFF field name `PortraitId`, and Holocron Toolset exposes it as `HTInstallation.TwoDA_PORTRAITS`. PyKotor's UTC, UTD, UTP, and UTT generic readers all preserve a numeric `portrait_id`, and the generated UTC editor help text documents the creature `PortraitId` field as a portrait-table row selector, with `65534` or `65535` delegating to the explicit `Portrait` ResRef instead. The same UI also documents the portrait preview as a display derived from `PortraitId` plus the optional `Portrait` ResRef. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`resource/generics/utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py), [`resource/generics/utp.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py), [`resource/generics/utt.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py), [`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py), [`installation.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/data/installation.py)]

**Row index**: Portrait ID (integer)

**Verified local fields and behavior**:

- `PortraitId` is the GFF field name that PyKotor maps to `portraits.2da`. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- The creature, door, placeable, and trigger generics all preserve a numeric `portrait_id`, but `UTT` explicitly documents that field as not used by the game engine, so this page should not overgeneralize portrait-table runtime use across all object classes. [[`resource/generics/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utc.py), [`resource/generics/utd.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utd.py), [`resource/generics/utp.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utp.py), [`resource/generics/utt.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/generics/utt.py)]
- For creatures specifically, Holocron Toolset documents the row-selection behavior directly in the UTC editor tooltip and preview text. [[`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py)]

The earlier `portraits.2da` schema block was broader than the currently rechecked evidence. Until individual portrait-table columns are re-verified from code or binary analysis, this page keeps only the narrower mapping and consumer behavior above. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [`toolset/uic/qtpy/editors/utc.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/uic/qtpy/editors/utc.py)]

---

### heads.2da

**Verified local and external usage**: `heads.2da` is a head-asset table tracked by PyKotor's K1 and K2 registry families, where the file contributes model and texture-bearing columns rather than a generic string column. The local registry marks `head` plus the alignment-variant `headtex*` columns as texture/model-facing resource references, and the external `reone` codebase ships a dedicated `heads.cpp` parser plus creature-side head loading that reads the same family of fields. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [reone `heads.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/parser/2da/heads.cpp), [reone `creature.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/creature.cpp)]

**Verified local columns**:

- `head` is a model-bearing column in PyKotor's K1 and K2 registry data. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `headtexe`, `headtexg`, `headtexve`, `headtexvg`, `headtexvve`, and `headtexvvve` are texture-bearing columns in PyKotor's K1 and K2 registry data. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py)]
- `reone` additionally parses `alttexture` alongside the same `head` and `headtex*` family, which is external implementation evidence for a slightly wider row shape than the local registry alone exposes. [[reone `heads.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/parser/2da/heads.cpp)]

`heads.2da` is a head-model and head-texture table with a verified `head` plus `headtex*` family, and that any larger schema should return only after a fresh line-by-line rebuild. [[`extract/twoda.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/twoda.py), [reone `heads.cpp`](https://github.com/seedhartha/reone/blob/master/src/libs/resource/parser/2da/heads.cpp)]

---

## Progression Tables 2DA Files

### classpowergain.2da

**Engine Usage**: Defines Force power progression by class and level. The engine uses this file to determine which Force powers are available to each class at each level.

**Row index**: Level (integer, typically 1-20)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `level` | *Integer* | Character level |
| `jedi_guardian` | *Integer* | Jedi Guardian power gain |
| `jedi_consular` | *Integer* | Jedi Consular power gain |
| `jedi_sentinel` | *Integer* | Jedi Sentinel power gain |
| `soldier` | *Integer* | Soldier power gain |
| `scout` | *Integer* | Scout power gain |
| `scoundrel` | *Integer* | Scoundrel power gain |
| `jedi_guardian_prestige` | *Integer* (optional) | Jedi Guardian prestige power gain |
| `jedi_consular_prestige` | *Integer* (optional) | Jedi Consular prestige power gain |
| `jedi_sentinel_prestige` | *Integer* (optional) | Jedi Sentinel prestige power gain |

---

## Name Generation 2DA Files

### Other Name Generation files

Similar name generation files exist for other species:

- `catharfirst.2da` / `catharlast.2da`: Cathar names (KotOR 2)
- `droidfirst.2da` / `droidlast.2da`: Droid names
- `miracianfirst.2da` / `miracianlast.2da`: Miraluka names (KotOR 2, alternate spelling)
- `miralukafirst.2da` / `miralukalast.2da`: Miraluka names (KotOR 2)
- `rodianfirst.2da` / `rodianlast.2da`: Rodian names
- `twilekfirst.2da` / `twileklast.2da`: Twi'lek names
- `wookieefirst.2da` / `wookieelast.2da`: Wookiee names
- `zabrakfirst.2da` / `zabraklast.2da`: Zabrak names

---

## Additional 2DA Files

### ambientmusic.2da

**Engine Usage**: Defines ambient music tracks for areas. The engine uses this file to determine which music to play in different areas based on [area properties](GFF-File-Format#are-area).

**Row index**: Music ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Music label |
| `music` | *ResRef* | Music file *ResRef* |
| `resource` | *ResRef* | Music resource *ResRef* |
| `stinger1`, `stinger2`, `stinger3` | *ResRef* (optional) | Stinger music ResRefs |

Ambient music columns and their ARE field bindings are represented in PyKotor's K1/K2 extraction maps and GFF linkage definitions ([`twoda.py` L206](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L206), [`twoda.py` L398](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L398), [`twoda.py` L545-L548](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L545-L548)).

---

### ambientsound.2da

**Engine Usage**: Defines ambient sound effects for areas. The engine uses this file to play ambient sounds in areas.

**Row index**: Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound label |
| `sound` | *ResRef* | Sound file *ResRef* |
| `resource` | *ResRef* | Sound resource *ResRef* |
| `description` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Sound description string reference |

Ambient sound column semantics are documented in PyKotor's K1/K2 schema maps and script-level API comments ([`twoda.py` L72](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L72), [`twoda.py` L184](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L184), [`twoda.py` L247](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L247), [`twoda.py` L376](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L376), [`scriptdefs.py` L6986-L6988](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6986-L6988)).

---

### ammunitiontypes.2da

**Engine Usage**: Defines ammunition types for ranged weapons, including their [models](MDL-MDX-File-Format) and sound effects. The engine uses this file when loading items to determine ammunition properties for ranged weapons.

**Row index**: Ammunition type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Ammunition type label |
| `model` | *ResRef* | Ammunition [model](MDL-MDX-File-Format) *ResRef* |
| `shotsound0` | *ResRef* (optional) | Shot sound effect ResRef (variant 1) |
| `shotsound1` | *ResRef* (optional) | Shot sound effect ResRef (variant 2) |
| `impactsound0` | *ResRef* (optional) | Impact sound effect ResRef (variant 1) |
| `impactsound1` | *ResRef* (optional) | Impact sound effect ResRef (variant 2) |

Ammunition type consumption in runtime item loading is visible in reone's object pipeline ([`item.cpp` L164-L171](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/item.cpp#L164-L171)).

---

### camerastyle.2da

**Engine Usage**: Defines camera styles for areas, including distance, pitch, view angle, and height settings. The engine uses this file to configure camera behavior in different areas.

**Row index**: Camera Style ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Camera style label |
| `name` | *String* | Camera style name |
| `distance` | *Float* | Camera distance from target |
| `pitch` | *Float* | Camera pitch angle |
| `viewangle` | *Float* | Camera view angle |
| `height` | *Float* | Camera height offset |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:497`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L497) - TwoDARegistry.CAMERAS constant definition
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:550`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L550) - [GFF](GFF-File-Format) field mapping: "CameraStyle" -> camerastyle.2da
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:37`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L37) - are camera_style field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:123`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L123) - Camera style index comment
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:442`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L442) - CameraStyle field parsing from are [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/are.py:579`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/are.py#L579) - CameraStyle field writing to are [GFF](GFF-File-Format)

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:96`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L96) - HTInstallation.TwoDA_CAMERAS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/are.py:102`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/are.py#L102) - camerastyle.2da loading in are editor

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/camerastyles.cpp:29-42`](https://github.com/seedhartha/reone/blob/master/src/libs/game/camerastyles.cpp#L29-L42) - Camera style loading from [2DA](2DA-File-Format)
- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/area.cpp:140-148`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/area.cpp#L140-L148) - Camera style usage in areas

---

### footstepsounds.2da

**Engine Usage**: Defines footstep sound effects for different surface types and footstep types. The engine uses this file to play appropriate footstep sounds based on the surface material and creature footstep type.

**Row index**: Footstep type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Footstep type label |
| `dirt0`, `dirt1`, `dirt2` | *ResRef* (optional) | Dirt surface footstep sounds |
| `grass0`, `grass1`, `grass2` | *ResRef* (optional) | Grass surface footstep sounds |
| `stone0`, `stone1`, `stone2` | *ResRef* (optional) | Stone surface footstep sounds |
| `wood0`, `wood1`, `wood2` | *ResRef* (optional) | Wood surface footstep sounds |
| `water0`, `water1`, `water2` | *ResRef* (optional) | Water surface footstep sounds |
| `carpet0`, `carpet1`, `carpet2` | *ResRef* (optional) | Carpet surface footstep sounds |
| `metal0`, `metal1`, `metal2` | *ResRef* (optional) | Metal surface footstep sounds |
| `leaves0`, `leaves1`, `leaves2` | *ResRef* (optional) | Leaves surface footstep sounds |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:188-198`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L188-L198) - Sound *ResRef* column definitions for footstepsounds.2da (K1: rolling, dirt0-2, grass0-2, stone0-2, wood0-2, water0-2, carpet0-2, metal0-2, puddles0-2, leaves0-2, force1-3)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:380-390`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L380-L390) - Sound *ResRef* column definitions for footstepsounds.2da (K2: rolling, dirt0-2, grass0-2, stone0-2, wood0-2, water0-2, carpet0-2, metal0-2, puddles0-2, leaves0-2, force1-3)

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/footstepsounds.cpp:31-57`](https://github.com/seedhartha/reone/blob/master/src/libs/game/footstepsounds.cpp#L31-L57) - Footstep sounds loading from [2DA](2DA-File-Format)
- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/creature.cpp:106`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/creature.cpp#L106) - Footstep type usage from [appearance.2da](#appearance2da)

---

### prioritygroups.2da

**Engine Usage**: Defines priority groups for sound effects, determining which sounds take precedence when multiple sounds are playing. The engine uses this file to calculate sound priority values.

**Row index**: Priority Group ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Priority group label |
| `priority` | *Integer* | Priority value (higher = more important) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/sound.cpp:92-96`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/sound.cpp#L92-L96) - Priority group loading from [2DA](2DA-File-Format)

---

### repute.2da

**Engine Usage**: Defines reputation values between different factions. The engine uses this file to determine whether creatures are enemies, friends, or neutral to each other based on their faction relationships.

**Row index**: Faction ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Faction label |
| Additional columns | *Integer* | Reputation values for each faction (column names match faction labels) |

**Note**: The `repute.2da` file is a square [matrix](Level-Layout-Formats#adjacencies-wok-only) where each row represents a faction, and each column (after `label`) represents the reputation value toward another faction. Reputation values typically range from 0-100, where values below 50 are enemies, above 50 are friends, and 50 is neutral.

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:460`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L460) - TwoDARegistry.FACTIONS constant definition (maps to "repute")
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:526-527`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L526-L527) - [GFF](GFF-File-Format) field mapping: "FactionID" and "Faction" -> repute.2da
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:92`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L92) - REPUTE.fac documentation comment
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1593`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1593) - REPUTE.fac file check comment
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1627`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1627) - REPUTE.fac documentation
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1667`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1667) - REPUTE_IDENTIFIER constant definition
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1683-1684`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1683-L1684) - repute [GFF](GFF-File-Format) field initialization
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1759-1761`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1759-L1761) - REPUTE.fac parsing
- [`Libraries/PyKotor/src/pykotor/extract/savedata.py:1795-1796`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/savedata.py#L1795-L1796) - REPUTE.fac writing

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:59`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L59) - HTInstallation.TwoDA_FACTIONS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utc.py:239`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L239) - repute.2da included in batch cache for [UTC](GFF-File-Format#utc-creature) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utc.py:253-280`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utc.py#L253-L280) - repute.2da usage in faction selection combobox
- [`Tools/HolocronToolset/src/toolset/gui/editors/utp.py:121-128`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utp.py#L121-L128) - repute.2da usage in [UTP](GFF-File-Format#utp-placeable) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utd.py:117-124`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utd.py#L117-L124) - repute.2da usage in [UTD](GFF-File-Format#utd-door) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/ute.py:106-109`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/ute.py#L106-L109) - repute.2da usage in [UTE](GFF-File-Format#ute-encounter) editor
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:72-78`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L72-L78) - repute.2da usage in [UTT](GFF-File-Format#utt-trigger) editor

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/reputes.cpp:36-62`](https://github.com/seedhartha/reone/blob/master/src/libs/game/reputes.cpp#L36-L62) - Repute [matrix](Level-Layout-Formats#adjacencies-wok-only) loading from [2DA](2DA-File-Format)

---

### surfacemat.2da

**Engine Usage**: Defines surface material properties for [walkmesh](Level-Layout-Formats#bwm) surfaces, including walkability, line of sight blocking, and grass rendering. The engine uses this file to determine surface behavior during pathfinding and rendering.

**Row index**: surface material ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | surface material label |
| `walk` | *Boolean* | Whether surface is walkable |
| `walkcheck` | *Boolean* | Whether walk check applies |
| `lineofsight` | *Boolean* | Whether surface blocks line of sight |
| `grass` | *Boolean* | Whether surface has grass rendering |
| `sound` | *String* | Sound type identifier for footstep sounds |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py:21`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/io_mdl.py#L21) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:9`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L9) - SurfaceMaterial import
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py:412`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_types.py#L412) - SurfaceMaterial.GRASS default value
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:47`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L47) - SurfaceMaterial ID per [face](MDL-MDX-File-Format#face-structure) documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py:784`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/bwm_data.py#L784) - SurfaceMaterial ID field documentation
- [`Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py:1578`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/mdl/mdl_data.py#L1578) - Comment referencing surfacemat.2da for [walkmesh](Level-Layout-Formats#bwm) surface material
- [`Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py:160`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm.py#L160) - SurfaceMaterial parsing from [BWM](Level-Layout-Formats#bwm)

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/surfaces.cpp:29-44`](https://github.com/seedhartha/reone/blob/master/src/libs/game/surfaces.cpp#L29-L44) - surface material loading from [2DA](2DA-File-Format)

---

### loadscreenhints.2da

**Engine Usage**: Defines loading screen hints displayed during area transitions. The engine uses this file to show helpful tips and hints to players while loading.

**Row index**: Loading Screen Hint ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Hint label |
| `strref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for hint text |

**References**:

**Vendor Implementations:**

- **[xoreos](https://github.com/xoreos/xoreos)**: [`src/engines/kotor/gui/loadscreen/loadscreen.cpp:45`](https://github.com/xoreos/xoreos/blob/f36b681b2a38799ddd6fce0f252b6d7fa781dfc2/src/engines/kotor/gui/loadscreen/loadscreen.cpp#L45) - Loading screen hints TODO comment (KotOR-specific)

---

### bodybag.2da

**Engine Usage**: Defines body bag appearances for creatures when they die. The engine uses this file to determine which appearance to use for the body bag container that appears when a creature is killed.

**Row index**: Body Bag ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Body bag label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for body bag name |
| `appearance` | *Integer* | Appearance ID for the body bag [model](MDL-MDX-File-Format) |
| `corpse` | *Boolean* | Whether the body bag represents a corpse |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:536`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L536) - [GFF](GFF-File-Format) field mapping: "BodyBag" -> bodybag.2da
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:296-298`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L296-L298) - [UTC](GFF-File-Format#utc-creature) bodybag_id field documentation (not used by game engine)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:438`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L438) - [UTC](GFF-File-Format#utc-creature) bodybag_id field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:555-556`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L555-L556) - BodyBag field parsing from [UTC](GFF-File-Format#utc-creature) GFF (deprecated)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:944`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L944) - BodyBag field writing to [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:105`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L105) - [UTP](GFF-File-Format#utp-placeable) bodybag_id field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:179`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L179) - [UTP](GFF-File-Format#utp-placeable) bodybag_id field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:254`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L254) - BodyBag field parsing from [UTP](GFF-File-Format#utp-placeable) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utp.py:341`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utp.py#L341) - BodyBag field writing to [UTP](GFF-File-Format#utp-placeable) [GFF](GFF-File-Format)

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/creature.cpp:1357-1366`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/creature.cpp#L1357-L1366) - Body bag loading from [2DA](2DA-File-Format)

---

### ranges.2da

**Engine Usage**: Defines perception ranges for creatures, including sight and hearing ranges. The engine uses this file to determine how far creatures can see and hear.

**Row index**: Range ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Range label |
| `primaryrange` | *Float* | Primary perception range (sight range) |
| `secondaryrange` | *Float* | Secondary perception range (hearing range) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/creature.cpp:1398-1406`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/creature.cpp#L1398-L1406) - Perception range loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:3178-3187`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L3178-L3187) - Perception range access from [2DA](2DA-File-Format)

---

### regeneration.2da

**Engine Usage**: Defines regeneration rates for creatures in combat and non-combat states. The engine uses this file to determine how quickly creatures regenerate hit points and Force points.

**Row index**: Regeneration State ID (integer, 0=combat, 1=non-combat)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Regeneration state label |
| Additional columns | float | Regeneration rates for different resource types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:759`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L759) - Regeneration rate loading from [2DA](2DA-File-Format)

---

### animations.2da

**Engine Usage**: Defines [animation](MDL-MDX-File-Format#animation-header) names and properties for creatures and objects. The engine uses this file to map [animation](MDL-MDX-File-Format#animation-header) IDs to [animation](MDL-MDX-File-Format#animation-header) names for playback.

**Row index**: [animation](MDL-MDX-File-Format#animation-header) ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [animation](MDL-MDX-File-Format#animation-header) label |
| `name` | *String* | [animation](MDL-MDX-File-Format#animation-header) name (used to look up [animation](MDL-MDX-File-Format#animation-header) in [model](MDL-MDX-File-Format)) |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1474-1482`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1474-L1482) - [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModulePlaceable.ts:1063-1103`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L1063-L1103) - Placeable [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleDoor.ts:1343-1365`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L1343-L1365) - Door [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

### combatanimations.2da

**Engine Usage**: Defines combat-specific [animation](MDL-MDX-File-Format#animation-header) properties and mappings. The engine uses this file to determine which [animations](MDL-MDX-File-Format#animation-header) to play during combat actions.

**Row index**: Combat [animation](MDL-MDX-File-Format#animation-header) ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Combat [animation](MDL-MDX-File-Format#animation-header) label |
| Additional columns | Various | Combat [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1482`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1482) - Combat [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

---

### weaponsounds.2da

**Engine Usage**: Defines sound effects for weapon attacks based on base item type. The engine uses this file to play appropriate weapon sounds during combat.

**Row index**: Base Item ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Base item label |
| Additional columns | *ResRef* | Sound effect ResRefs for different attack types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:1819-1822`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L1819-L1822) - Weapon sound lookup from [2DA](2DA-File-Format)

---

### placeableobjsnds.2da

**Engine Usage**: Defines sound effects for placeable objects based on sound appearance type. The engine uses this file to play appropriate sounds when interacting with placeables.

**Row index**: Sound Appearance type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound appearance type label |
| Additional columns | *ResRef* | Sound effect ResRefs for different interaction types |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModulePlaceable.ts:387-389`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModulePlaceable.ts#L387-L389) - Placeable sound lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleDoor.ts:239-241`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleDoor.ts#L239-L241) - Door sound lookup from [2DA](2DA-File-Format)

---

### creaturespeed.2da

**Engine Usage**: Defines movement speed rates for creatures based on walk rate ID. The engine uses this file to determine walking and running speeds.

**Row index**: Walk Rate ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Walk rate label |
| `walkrate` | *Float* | Walking speed rate |
| `runrate` | *Float* | Running speed rate |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:2875-2887`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L2875-L2887) - Creature speed lookup from [2DA](2DA-File-Format)

---

### exptable.2da

**Engine Usage**: Defines experience point requirements for each character level. The engine uses this file to determine when a character levels up based on accumulated experience.

**Row index**: Level (integer, typically 1-20)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Level label |
| Additional columns | *Integer* | Experience point requirements for leveling up |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleCreature.ts:2926-2941`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleCreature.ts#L2926-L2941) - Experience table lookup from [2DA](2DA-File-Format)

---

### guisounds.2da

**Engine Usage**: Defines sound effects for [GUI](GFF-File-Format#gui-graphical-user-interface) interactions (button clicks, mouse enter events, etc.). The engine uses this file to play appropriate sounds when the player interacts with UI elements.

**Row index**: Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound label (e.g., "Clicked_Default", "Entered_Default") |
| `soundresref` | *ResRef* | Sound effect *ResRef* |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:200`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L200) - Sound *ResRef* column definition for guisounds.2da (K1: soundresref)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:392`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L392) - Sound *ResRef* column definition for guisounds.2da (K2: soundresref)

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/gui/sounds.cpp:31-45`](https://github.com/seedhartha/reone/blob/master/src/libs/game/gui/sounds.cpp#L31-L45) - [GUI](GFF-File-Format#gui-graphical-user-interface) sound loading from [2DA](2DA-File-Format)

---

### dialoganimations.2da

**Engine Usage**: Maps dialog [animation](MDL-MDX-File-Format#animation-header) ordinals to [animation](MDL-MDX-File-Format#animation-header) names for use in conversations. The engine uses this file to determine which [animation](MDL-MDX-File-Format#animation-header) to play when a dialog line specifies an [animation](MDL-MDX-File-Format#animation-header) ordinal.

**Row index**: [animation](MDL-MDX-File-Format#animation-header) Index (integer, ordinal - 10000)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [animation](MDL-MDX-File-Format#animation-header) label |
| `name` | *String* | [animation](MDL-MDX-File-Format#animation-header) name (used to look up [animation](MDL-MDX-File-Format#animation-header) in [model](MDL-MDX-File-Format)) |

**References**:

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/gui/dialog.cpp:302-315`](https://github.com/seedhartha/reone/blob/master/src/libs/game/gui/dialog.cpp#L302-L315) - Dialog [animation](MDL-MDX-File-Format#animation-header) lookup from [2DA](2DA-File-Format)

---


### forceshields.2da

**Engine Usage**: Defines Force shield visual effects and properties. The engine uses this file to determine which visual effect to display when a Force shield is active.

**Row index**: Force Shield ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Force shield label |
| Additional columns | Various | Force shield visual effect properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:5552`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L5552) - Force shield lookup from [2DA](2DA-File-Format)

---

### plot.2da

**Engine Usage**: Defines journal/quest entries with their experience point rewards and labels. The engine uses this file to manage quest tracking, [journal entries](GFF-File-Format#jrl-journal), and experience point calculations for quest completion.

**Row index**: Plot ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Plot/quest label (used as quest identifier) |
| `xp` | *Integer* | Experience points awarded for quest completion |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:123-125`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L123-L125) - [UTC](GFF-File-Format#utc-creature) plot field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:375`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L375) - [UTC](GFF-File-Format#utc-creature) plot field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:579-580`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L579-L580) - Plot field parsing from [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/utc.py:839`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/utc.py#L839) - Plot field writing to [UTC](GFF-File-Format#utc-creature) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:71-73`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L71-L73) - [UTI](GFF-File-Format#uti-item) plot field documentation
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:129`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L129) - [UTI](GFF-File-Format#uti-item) plot field initialization
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:256-258`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L256-L258) - Plot field parsing from [UTI](GFF-File-Format#uti-item) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/uti.py:339`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/uti.py#L339) - Plot field writing to [UTI](GFF-File-Format#uti-item) [GFF](GFF-File-Format)
- [`Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py:89-92`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/generics/dlg/io/gff.py#L89-L92) - Dialog [node](MDL-MDX-File-Format#node-structures) PlotIndex and PlotXPPercentage field parsing

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/JournalManager.ts:58-64`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/JournalManager.ts#L58-L64) - Plot/quest experience lookup from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/JournalManager.ts:101-104`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/JournalManager.ts#L101-L104) - Plot existence check from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:7845-7848`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L7845-L7848) - Plot table access for quest experience

---

### [traps.2da](#traps2da)

**Engine Usage**: Defines trap properties including [models](MDL-MDX-File-Format), sounds, and scripts. The engine uses this file when loading triggers with trap types to determine trap appearance and behavior.

**Row index**: Trap type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Trap type label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for trap name |
| `model` | *ResRef* | Trap [model](MDL-MDX-File-Format) *ResRef* |
| `explosionsound` | *ResRef* | Explosion sound effect *ResRef* |
| `resref` | *ResRef* | Trap script *ResRef* |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:150`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L150) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for traps.2da (K1: trapname, name)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:328`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L328) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for traps.2da (K2: trapname, name)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:470`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L470) - TwoDARegistry.TRAPS constant definition
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:568`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L568) - [GFF](GFF-File-Format) field mapping: "TrapType" -> traps.2da
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py:6347-6348`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L6347-L6348) - VersusTrapEffect function comments
- [`Libraries/PyKotor/src/pykotor/common/scriptdefs.py:7975-7976`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L7975-L7976) - GetLastHostileActor function comment mentioning traps
- [`Libraries/PyKotor/src/pykotor/common/scriptlib.py:21692`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/common/scriptlib.py#L21692) - Trap targeting comment

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:69`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L69) - HTInstallation.TwoDA_TRAPS constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:73-87`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L73-L87) - traps.2da loading and usage in trap type selection combobox
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:167`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L167) - traps.2da usage for setting trap type index
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:216`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L216) - traps.2da usage for getting trap type index
- [`Tools/HolocronToolset/src/ui/editors/utt.ui:252`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/ui/editors/utt.ui#L252) - Trap selection combobox in [UTT](GFF-File-Format#utt-trigger) editor UI

**Vendor Implementations:**

- **[reone](https://github.com/seedhartha/reone)**: [`src/libs/game/object/trigger.cpp:75-78`](https://github.com/seedhartha/reone/blob/master/src/libs/game/object/trigger.cpp#L75-L78) - Trap type loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleTrigger.ts:605-611`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleTrigger.ts#L605-L611) - Trap loading from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleObject.ts:1822`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleObject.ts#L1822) - Trap lookup from [2DA](2DA-File-Format)

---

### modulesave.2da

**Engine Usage**: Defines which modules should be included in save games. The engine uses this file to determine whether a module's state should be persisted when saving the game.

**Row index**: Module Index (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Module label |
| `modulename` | *String* | Module filename (e.g., "001ebo") |
| `includeInSave` | *Boolean* | Whether module state should be saved (0 = false, 1 = true) |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/Module.ts:663-669`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/Module.ts#L663-L669) - Module save inclusion check from [2DA](2DA-File-Format)

---

### tutorial.2da

**Engine Usage**: Defines tutorial window tracking entries. The engine uses this file to track which tutorial windows have been shown to the player.

**Row index**: Tutorial ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Tutorial label |
| Additional columns | Various | Tutorial window properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/PartyManager.ts:180-187`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/PartyManager.ts#L180-L187) - Tutorial window tracker initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/managers/PartyManager.ts:438`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/managers/PartyManager.ts#L438) - Tutorial table access

---

### globalcat.2da

**Engine Usage**: Defines global variables and their types for the game engine. The engine uses this file to initialize global variables at game start, determining which variables are integers, floats, or strings.

**Row index**: Global Variable Index (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Global variable label |
| `name` | *String* | Global variable name |
| `type` | *String* | Variable type ("Number", "Boolean", "string", etc.) |

**References**:

**Vendor Implementations:**

- [`NorthernLights/Assets/Scripts/Systems/StateSystem.cs:282-294`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/Assets/Scripts/Systems/StateSystem.cs#L282-L294) - Global variable initialization from [2DA](2DA-File-Format)

---

### subrace.2da

**Engine Usage**: Defines subrace types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine subrace properties and restrictions.

**Row index**: Subrace ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Subrace label |
| Additional columns | Various | Subrace properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:457`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L457) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:56`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L56) - HTInstallation constant

---

### gender.2da

**Engine Usage**: Defines gender types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine gender-specific properties and restrictions.

**Row index**: Gender ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Gender label |
| Additional columns | Various | Gender properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:461`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L461) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:60`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L60) - HTInstallation constant

---

### [racialtypes.2da](#racialtypes2da)

**Engine Usage**: Defines racial types for character creation and [creature templates](GFF-File-Format#utc-creature). The engine uses this file to determine race-specific properties, restrictions, and bonuses.

**Row index**: Race ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Race label |
| Additional columns | Various | Race properties and bonuses |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:471`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L471) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:70`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L70) - HTInstallation constant

---

### upgrade.2da

**Engine Usage**: Defines item upgrade types and properties. The engine uses this file to determine which upgrades can be applied to items and their effects.

**Row index**: Upgrade type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Upgrade type label |
| Additional columns | Various | Upgrade properties and effects |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:473`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L473) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:72`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L72) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:632-639`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L632-L639) - Upgrade selection in item editor

---

### encdifficulty.2da

**Engine Usage**: Defines encounter difficulty levels for area encounters. The engine uses this file to determine encounter scaling and difficulty modifiers.

**Row index**: Difficulty ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Difficulty label |
| Additional columns | Various | Difficulty modifiers and properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:474`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L474) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:73`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L73) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/ute.py:101-104`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/ute.py#L101-L104) - Encounter difficulty selection

---

### [itempropdef.2da](#itempropdef2da)

**Engine Usage**: Defines item property definitions and their base properties. This is the master table for all item properties in the game. The engine uses this file to determine item property types, costs, and effects.

**Row index**: Item Property ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property label |
| Additional columns | Various | Property definitions, costs, and parameters |

**Note**: This file may be the same as or related to `itemprops.2da` documented earlier. The exact relationship between these files may vary between KotOR 1 and 2.

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:475`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L475) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:74`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L74) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:107-111`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L107-L111) - Item property loading in item editor

---

### emotion.2da

**Engine Usage**: Defines emotion [animations](MDL-MDX-File-Format#animation-header) for dialog conversations (KotOR 2 only). The engine uses this file to determine which emotion [animation](MDL-MDX-File-Format#animation-header) to play during dialog lines.

**Row index**: Emotion ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Emotion label |
| Additional columns | Various | Emotion [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:491`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L491) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:90`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L90) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1267-1319`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1267-L1319) - Emotion loading in dialog editor (KotOR 2 only)

---

### facialanim.2da

**Engine Usage**: Defines facial [animation](MDL-MDX-File-Format#animation-header) expressions for dialog conversations (KotOR 2 only). The engine uses this file to determine which facial expression [animation](MDL-MDX-File-Format#animation-header) to play during dialog lines.

**Row index**: Expression ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Expression label |
| Additional columns | Various | Facial [animation](MDL-MDX-File-Format#animation-header) properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:492`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L492) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:91`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L91) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1267-1325`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1267-L1325) - Expression loading in dialog editor (KotOR 2 only)

---

### videoeffects.2da

**Engine Usage**: Defines video/camera effects for dialog conversations. The engine uses this file to determine which visual effect to apply during dialog camera shots.

**Row index**: Video Effect ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Video effect label |
| Additional columns | Various | Video effect properties |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:493`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L493) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:92`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L92) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py:1263-1298`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/dlg/editor.py#L1263-L1298) - Video effect loading in dialog editor

---

### planetary.2da

**Engine Usage**: Defines planetary information for the galaxy map and travel system. The engine uses this file to determine planet names, descriptions, and travel properties.

**Row index**: Planet ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Planet label |
| Additional columns | Various | Planet properties and travel information |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:495`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L495) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:94`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L94) - HTInstallation constant

---

### cursors.2da

**Engine Usage**: Defines cursor types for different object interactions. The engine uses this file to determine which cursor to display when hovering over different object types.

**Row index**: Cursor ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Cursor label |
| Additional columns | Various | Cursor properties and ResRefs |

**References**:

**PyKotor:**

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:469`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L469) - TwoDARegistry definition

**HolocronToolset:**

- [`Tools/HolocronToolset/src/toolset/data/installation.py:68`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L68) - HTInstallation constant
- [`Tools/HolocronToolset/src/toolset/gui/editors/utt.py:71-76`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/utt.py#L71-L76) - Cursor selection in trigger editor

---

## Item Property Parameter & Cost Tables 2DA Files

The following 2DA files are used for item property parameter and cost calculations:

### iprp_paramtable.2da

**Engine Usage**: Master table listing all item property parameter tables. The engine uses this file to look up which parameter table to use for a specific item property type.

**Row index**: Parameter Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Parameter table label |
| Additional columns | Various | Parameter table ResRefs and properties |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_PARAMTABLE` L698](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L698) — `iprp_paramtable` (`LoadIPRPParamTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_PARAMTABLE` L99](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L99)
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:517-558`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L517-L558) - Parameter table lookup in item editor

---

### iprp_costtable.2da

**Engine Usage**: Master table listing all item property cost calculation tables. The engine uses this file to look up which cost table to use for calculating item property costs.

**Row index**: Cost Table ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Cost table label |
| Additional columns | Various | Cost table ResRefs and properties |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_COSTTABLE` L693](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L693) — `iprp_costtable` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_COSTTABLE` L94](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L94)
- [`Tools/HolocronToolset/src/toolset/gui/editors/uti.py:486-496`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/gui/editors/uti.py#L486-L496) - Cost table lookup in item editor

---

### iprp_abilities.2da

**Engine Usage**: Maps item property values to ability score bonuses. The engine uses this file to determine which ability score is affected by an item property.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Ability score mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ABILITIES` L688](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L688) — `iprp_abilities` (`Load2DArrays_IPRPAbilities()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ABILITIES` L89](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L89)

---

### iprp_aligngrp.2da

**Engine Usage**: Maps item property values to alignment group restrictions. The engine uses this file to determine alignment restrictions for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Alignment group mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ALIGNGRP` L690](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L690) — `iprp_aligngrp` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ALIGNGRP` L91](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L91)

---

### iprp_combatdam.2da

**Engine Usage**: Maps item property values to combat damage bonuses. The engine uses this file to determine damage bonus calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Combat damage mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_COMBATDAM` L692](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L692) — canonical `iprp_combatdam` resref (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_COMBATDAM` L93](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L93)

---

### iprp_damagetype.2da

**Engine Usage**: Maps item property values to damage type flags. The engine uses this file to determine damage type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Damage type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_DAMAGETYPE` L694](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L694) — `iprp_damagetype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_DAMAGETYPE` L95](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L95)

---

### iprp_protection.2da

**Engine Usage**: Maps item property values to protection/immunity types. The engine uses this file to determine protection calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Protection type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_PROTECTION` L699](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L699) — `iprp_protection` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_PROTECTION` L100](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L100)

---

### iprp_acmodtype.2da

**Engine Usage**: Maps item property values to armor class modifier types. The engine uses this file to determine AC modifier calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | AC modifier type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ACMODTYPE` L689](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L689) — `iprp_acmodtype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ACMODTYPE` L90](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L90)

---

### iprp_immunity.2da

**Engine Usage**: Maps item property values to immunity types. The engine uses this file to determine immunity calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Immunity type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_IMMUNITY` L695](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L695) — `iprp_immunity` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_IMMUNITY` L96](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L96)

---

### iprp_saveelement.2da

**Engine Usage**: Maps item property values to saving throw element types. The engine uses this file to determine saving throw element calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Saving throw element mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_SAVEELEMENT` L700](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L700) — `iprp_saveelement` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_SAVEELEMENT` L101](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L101)

---

### iprp_savingthrow.2da

**Engine Usage**: Maps item property values to saving throw types. The engine uses this file to determine saving throw calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Saving throw type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_SAVINGTHROW` L701](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L701) — `iprp_savingthrow` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_SAVINGTHROW` L102](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L102)

---

### iprp_onhit.2da

**Engine Usage**: Maps item property values to on-hit effect types. The engine uses this file to determine on-hit effect calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | On-hit effect mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_ONHIT` L697](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L697) — `iprp_onhit` (`Load2DArrays_OnHit()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_ONHIT` L98](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L98)

---

### iprp_ammotype.2da

**Engine Usage**: Maps item property values to ammunition type restrictions. The engine uses this file to determine ammunition type calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Ammunition type mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_AMMOTYPE` L691](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L691) — `iprp_ammotype` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_AMMOTYPE` L92](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L92)

---

### iprp_mosterhit.2da

**Engine Usage**: Maps item property values to monster hit effect types. The engine uses this file to determine monster hit effect calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Monster hit effect mappings |

**Note**: The filename contains a typo ("mosterhit" instead of "monsterhit") which is preserved in the game files.

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_MONSTERHIT` L696](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L696) — `iprp_mosterhit` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_MONSTERHIT` L97](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L97)

---

### iprp_walk.2da

**Engine Usage**: Maps item property values to movement/walk speed modifiers. The engine uses this file to determine movement speed calculations for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Movement speed mappings |

**References**:

**PyKotor:**

- [`TwoDARegistry.IPRP_WALK` L702](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L702) — `iprp_walk` (`LoadIPRPCostTables()`)

**HolocronToolset:**

- [`HTInstallation.TwoDA_IPRP_WALK` L103](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L103)

---

### iprp_lightcol.2da

**Engine Usage**: Maps item property values to light color configurations. The engine uses this file to determine light color settings for item properties.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Light color mappings |

**References**:

**PyKotor:**

- [`_GFF_FIELD_TO_2DA` — `"LightColor"` -> `iprp_lightcol` L774](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L774) — [GFF](GFF-File-Format) field wiring (UTI / item property context)
- [`TwoDARegistry` docstring — `iprp_lightcol` / `Load2DArrays_LightColor()` L600](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L600)

**HolocronToolset:**

- No `HTInstallation.TwoDA_IPRP_LIGHTCOL` in [`installation.py`](https://github.com/OpenKotOR/HolocronToolset/src/toolset/data/installation.py); cite PyKotor `twoda.py` above for resref proof.

---

### iprp_monstdam.2da

**Engine Usage**: Maps item property values to monster damage bonuses. The engine uses this file to determine damage bonus calculations for monster weapons.

**Row index**: Item Property Value (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Property value label |
| Additional columns | Various | Monster damage mappings |

**References**:

**PyKotor:**

- [`twoda.py` `_GFF_FIELD_TO_2DA` — `"MonsterDamage"` -> `iprp_monstdam` L779](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L779)
- [`read_2da` L67+](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/resource/formats/twoda/twoda_auto.py#L67) — generic 2DA reader

**Note:** Unlike `iprp_combatdam`, there is no separate `TwoDARegistry.IPRP_MONSTDAM` constant—the file is reached via the **MonsterDamage** GFF field mapping above and via **[itemprops.2da](#itemprops2da)** cost-table wiring.

**See:** [2DA-iprp_monstdam](#iprp_monstdam2da) — expanded stub page (combat vs monster damage, cross-links).

---

### difficultyopt.2da

**Engine Usage**: Defines difficulty options and their properties. The engine uses this file to determine difficulty settings, modifiers, and descriptions.

**Row index**: Difficulty Option ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Difficulty option label |
| `desc` | *String* | Difficulty description (e.g., "Default") |
| Additional columns | Various | Difficulty modifiers and properties |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:66-74`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L66-L74) - Difficulty options initialization from [2DA](2DA-File-Format)

---

### xptable.2da

**Engine Usage**: Defines experience point reward calculations for defeating enemies. The engine uses this file to calculate how much XP to grant when a creature is defeated, based on the defeated creature's level and properties.

**Row index**: XP Table Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | XP table entry label |
| Additional columns | Various | XP calculation parameters |

**Note**: This is different from `exptable.2da` which defines XP requirements for leveling up. `xptable.2da` defines XP rewards for defeating enemies.

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:89-95`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L89-L95) - XP table initialization from [2DA](2DA-File-Format)

---

### featgain.2da

**Engine Usage**: Defines feat gain progression by class and level. The engine uses this file to determine which feats are available to each class at each level.

**Row index**: Feat Gain Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Feat gain entry label |
| Additional columns | Various | Feat gain progression by class and level |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:101-105`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L101-L105) - Feat gain initialization from [2DA](2DA-File-Format)

---

### effecticon.2da

**Engine Usage**: Defines effect icons displayed on character portraits and character sheets. The engine uses this file to determine which icon to display for status effects, buffs, and debuffs.

**Row index**: Effect Icon ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Effect icon label |
| Additional columns | Various | Effect icon properties and ResRefs |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:143-150`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L143-L150) - Effect icon initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:6441-6446`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L6441-L6446) - SetEffectIcon function
- [`NorthernLights/nwscript.nss:4678`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L4678) - Comment referencing effecticon.2da

---

### pazaakdecks.2da

**Engine Usage**: Defines Pazaak card decks for the Pazaak mini-game. The engine uses this file to determine which cards are available in opponent decks and player decks.

**Row index**: Pazaak Deck ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Deck label |
| Additional columns | Various | Deck card definitions and properties |

**References**:

**Vendor Implementations:**

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/engine/rules/SWRuleSet.ts:178-185`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/engine/rules/SWRuleSet.ts#L178-L185) - Pazaak decks initialization from [2DA](2DA-File-Format)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:4438`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L4438) - StartPazaakGame function comment
- [`NorthernLights/nwscript.nss:3847`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L3847) - Comment referencing PazaakDecks.2da

---

### acbonus.2da

**Engine Usage**: Defines armor class bonus calculations. The engine uses this file to determine AC bonus values for different scenarios and calculations.

**Row index**: AC Bonus Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | AC bonus entry label |
| Additional columns | Various | AC bonus calculation parameters |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/combat/CreatureClass.ts:302-304`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/combat/CreatureClass.ts#L302-L304) - AC bonus loading from [2DA](2DA-File-Format)
- [`Tools/HolocronToolset/src/toolset/data/installation.py:63`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Tools/HolocronToolset/src/toolset/data/installation.py#L63) - HTInstallation.ACBONUS constant

---

### keymap.2da

**Engine Usage**: Defines keyboard and [controller](MDL-MDX-File-Format#controllers) key mappings for different game contexts (in-game, [GUI](GFF-File-Format#gui-graphical-user-interface), dialog, minigame, etc.). The engine uses this file to determine which keys trigger which actions in different contexts.

**Row index**: Keymap Entry ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Keymap entry label |
| Additional columns | Various | key mappings for different contexts (ingame, [GUI](GFF-File-Format#gui-graphical-user-interface), dialog, minigame, freelook, movie) |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/controls/KeyMapper.ts:293-299`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/controls/KeyMapper.ts#L293-L299) - Keymap initialization from [2DA](2DA-File-Format)

---

### poison.2da

**Engine Usage**: Defines poison effect types and their properties. The engine uses this file to determine poison effects, durations, and damage calculations.

**Row index**: Poison type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Poison type label |
| Additional columns | Various | Poison effect properties, damage, and duration |

**References**:

- [`NorthernLights/nwscript.nss:949`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L949) - Comment referencing poison.2da constants
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:3194-3199`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L3194-L3199) - EffectPoison function

---

### feedbacktext.2da

**Engine Usage**: Defines feedback text strings displayed to the player for various game events and actions. The engine uses this file to provide contextual feedback messages.

**Row index**: Feedback Text ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Feedback text label |
| Additional columns | Various | Feedback text strings and properties |

**References**:

- [`NorthernLights/nwscript.nss:3858`](https://github.com/lachjames/NorthernLights/blob/8dcfd2aee28546db7e42f2ab894a5127f4130021/nwscript.nss#L3858) - Comment referencing FeedBackText.2da
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/nwscript/NWScriptDefK1.ts:4464-4465`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/nwscript/NWScriptDefK1.ts#L4464-L4465) - DisplayFeedBackText function

---

### appearancesndset.2da

**Engine Usage**: Defines sound appearance types for creature appearances. The engine uses this file to determine which sound appearance type to use based on the creature's appearance.

**Row index**: Sound Appearance type ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Sound appearance type label |
| Additional columns | Various | Sound appearance type properties |

**References**:

- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)**: [`Appearance.cs` L56–L60](https://github.com/NickHugi/Kotor.NET/blob/6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2/Kotor.NET/Tables/Appearance.cs#L56-L60) — `SoundAppTypeID` maps into `appearancesndset.2da`

---

### texpacks.2da

**Engine Usage**: Defines [texture](Texture-Formats#tpc) pack configurations for graphics settings (KotOR 2 only). The engine uses this file to determine available [texture](Texture-Formats#tpc) pack options in the graphics menu.

**Row index**: [texture](Texture-Formats#tpc) Pack ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | [texture](Texture-Formats#tpc) pack label |
| `strrefname` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for [texture](Texture-Formats#tpc) pack name |
| Additional columns | Various | [texture](Texture-Formats#tpc) pack properties and settings |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/game/tsl/menu/MenuGraphicsAdvanced.ts:51-122`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/game/tsl/menu/MenuGraphicsAdvanced.ts#L51-L122) - [texture](Texture-Formats#tpc) pack loading from [2DA](2DA-File-Format) for graphics menu (KotOR 2 only)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/game/kotor/menu/MenuGraphicsAdvanced.ts:63-121`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/game/kotor/menu/MenuGraphicsAdvanced.ts#L63-L121) - [texture](Texture-Formats#tpc) pack usage in KotOR 1 graphics menu

---

### loadscreens.2da

**Engine Usage**: Defines loading screen configurations for area transitions. The engine uses this file to determine which loading screen image, music, and hints to display when transitioning between areas.

**Row index**: Loading Screen ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Loading screen label |
| `bmpresref` | *ResRef* | Loading screen background image *ResRef* |
| `musicresref` | *ResRef* | Music track *ResRef* to play during loading |
| Additional columns | Various | Other loading screen properties |

**References**:

- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)**: [`src/module/ModuleArea.ts:210`](https://github.com/KobaltBlu/KotOR.js/blob/ea9491d5c783364cf285f178434b84405bee3608/src/module/ModuleArea.ts#L210) - Comment referencing loadscreens.2da for area loading screen index
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:549`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L549) - [GFF](GFF-File-Format) field mapping: "LoadScreenID" -> loadscreens.2da

---

### fractionalcr.2da

**Engine Usage**: Defines fractional challenge rating configurations. The engine uses this file to determine fractional CR display strings.

**Row index**: Fractional CR ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Fractional CR label |
| `displaystrref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for fractional CR display text |
| Additional columns | Various | Fractional CR properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:84`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L84) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for fractionalcr.2da

---

### bindablekeys.2da

**Engine Usage**: Defines bindable key actions and their string references. The engine uses this file to determine key action names for the key binding interface.

**Row index**: Bindable key ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Bindable key label |
| `keynamestrref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for key name |
| Additional columns | Various | key binding properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:74`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L74) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for bindablekeys.2da

---

### masterfeats.2da

**Engine Usage**: Defines master feat configurations. The engine uses this file to determine master feat names and properties.

**Row index**: Master Feat ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Master feat label |
| `strref` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for master feat name |
| Additional columns | Various | Master feat properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:138`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L138) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for masterfeats.2da

---

### movies.2da

**Engine Usage**: Defines movie/cutscene configurations. The engine uses this file to determine movie names and descriptions.

**Row index**: Movie ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Movie label |
| `strrefname` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for movie name |
| `strrefdesc` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for movie description |
| Additional columns | Various | Movie properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:140`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L140) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for movies.2da

---

### stringtokens.2da

**Engine Usage**: Defines string token configurations. The engine uses this file to determine string token values for various game systems.

**Row index**: string Token ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | string token label |
| `strref1` through `strref4` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | string references for token values |
| Additional columns | Various | string token properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:144`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L144) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definitions for stringtokens.2da

---

### disease.2da

**Engine Usage**: Defines disease effect configurations. The engine uses this file to determine disease names, scripts, and properties.

**Row index**: Disease ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Disease label |
| `name` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | *String* reference for disease name (KotOR 2) |
| `end_incu_script` | *ResRef* | Script *ResRef* for end incubation period |
| `24_hour_script` | *ResRef* | Script *ResRef* for 24-hour disease effect |
| Additional columns | Various | Disease properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:255`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L255) - [StrRef](Audio-and-Localization-Formats#string-references-strref) column definition for disease.2da (KotOR 2)
- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:238,431`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L238) - Script *ResRef* column definitions for disease.2da

---

### droiddischarge.2da

**Engine Usage**: Defines droid discharge effect configurations. The engine uses this file to determine droid discharge properties.

**Row index**: Droid Discharge ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Droid discharge label |
| `>>##HEADER##<<` | *ResRef* | header [resource reference](GFF-File-Format#gff-data-types) |
| Additional columns | Various | Droid discharge properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:156`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L156) - *ResRef* column definition for droiddischarge.2da

---

### upcrystals.2da

**Engine Usage**: Defines upgrade crystal configurations. The engine uses this file to determine crystal [model](MDL-MDX-File-Format) variations for lightsaber upgrades.

**Row index**: Upgrade Crystal ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Upgrade crystal label |
| `shortmdlvar` | *ResRef* | Short [model](MDL-MDX-File-Format) variation *ResRef* |
| `longmdlvar` | *ResRef* | Long [model](MDL-MDX-File-Format) variation *ResRef* |
| `doublemdlvar` | *ResRef* | double-bladed [model](MDL-MDX-File-Format) variation *ResRef* |
| Additional columns | Various | Crystal properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:172`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L172) - [model](MDL-MDX-File-Format) *ResRef* column definitions for upcrystals.2da

---

### grenadesnd.2da

**Engine Usage**: Defines grenade sound configurations. The engine uses this file to determine grenade sound effects.

**Row index**: Grenade Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Grenade sound label |
| `sound` | *ResRef* | Sound *ResRef* for grenade |
| Additional columns | Various | Grenade sound properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:199`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L199) - Sound *ResRef* column definition for grenadesnd.2da

---

### inventorysnds.2da

**Engine Usage**: Defines inventory sound configurations. The engine uses this file to determine inventory sound effects for item interactions.

**Row index**: Inventory Sound ID (integer)

**Column structure**:

| Column Name | type | Description |
|------------|------|-------------|
| `label` | *String* | Inventory sound label |
| `inventorysound` | *ResRef* | Inventory sound *ResRef* |
| Additional columns | Various | Inventory sound properties |

**References**:

- [`Libraries/PyKotor/src/pykotor/extract/twoda.py:201`](https://github.com/OpenKotOR/PyKotor/blob/a8daa4091b067e8424ae537793224e6b178ee9d8/Libraries/PyKotor/src/pykotor/extract/twoda.py#L201) - Sound *ResRef* column definition for inventorysnds.2da

