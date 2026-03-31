# Resource formats and resolution

This page has three jobs:

1. point you to the right format page,
2. keep the canonical resource type ID table in one place,
3. give a short reminder of how file lookup works before you dive into a specific format.

For the full narrative on precedence, override behavior, module capsules, KEY/BIF, and language IDs, use [Concepts](Concepts). This page is the index and registry; Concepts is the explanation.

Use this page when you already know you need a format page or a resource type ID. Use [Home](Home) for routing and [Concepts](Concepts) for the full explanation of why the resolution order behaves the way it does.

## Verified against implementations

The container and format summaries on this page are cross-checked against:

- **PyKotor:** `pykotor.extract.installation`, `pykotor.extract.chitin`, `pykotor.resource.formats.key.io_key`, `pykotor.resource.formats.bif.io_bif`, `pykotor.resource.formats.erf.io_erf`, `pykotor.resource.formats.rim.io_rim`, `pykotor.resource.formats.tlk.io_tlk`, `pykotor.resource.formats.twoda.io_twoda`
- **reone:** `src/libs/resource/director.cpp`, `src/libs/resource/resources.cpp`, `src/libs/resource/format/keyreader.cpp`, `src/libs/resource/format/bifreader.cpp`, `src/libs/resource/format/erfreader.cpp`
- **KotOR.js:** `src/loaders/ResourceLoader.ts`, `src/resource/KEYObject.ts`, `src/resource/BIFObject.ts`, `src/managers/TwoDAManager.ts`, `src/managers/TLKManager.ts`, `src/resource/ResourceTypes.ts`
- **Kotor.NET:** `Kotor.NET/Formats/KotorKEY/KEYBinaryStructure.cs`, `Kotor.NET/Formats/KotorBIF/BIFBinaryStructure.cs`, `Kotor.NET/Formats/KotorERF/ERFBinaryStructure.cs`, `Kotor.NET/Formats/KotorTLK/TLKBinaryStructure.cs`, `Kotor.NET/Formats/Kotor2DA/TwoDABinaryReader.cs`, `Kotor.NET/ResourceContainers/Chitin.cs`, `Kotor.NET/ResourceContainers/Capsule.cs`

## Resource resolution order

Full prose (resource manager *demands*, KEY’s role, override vs MOD/ERF/[RIM](RIM-File-Format)): **[Concepts — Resource resolution order](Concepts#resource-resolution-order)**.

**Quick reference:**

1. `override/`
2. loaded [MOD](ERF-File-Format)/[ERF](ERF-File-Format)/[RIM](RIM-File-Format) for the active module
3. loaded save-side data when applicable
4. [KEY](KEY-File-Format)/[BIF](BIF-File-Format)
5. engine defaults

## ResRef and resource type

**ResRef** is the name portion of a game resource. A **resource type** is the numeric type ID that distinguishes, for example, `foo.utc` from `foo.utp` or `foo.2da`. The engine resolves the pair together.

Read [Concepts — ResRef](Concepts#resref-resource-reference) for naming rules and examples. Read [GFF File Format](GFF-File-Format#gff-data-types) for field typing inside GFF payloads.

The table below is the wiki SSOT for resource type IDs. Loose files such as `.utc`, `.2da`, `.mdl`, and `.tlk` follow the same mapping that the engine and archive formats use internally.

**Language IDs** (`dialog.tlk`, localization): [Concepts — Language IDs](Concepts#language-ids-kotor).

## Resource Type Identifiers

*KotOR* uses numeric resource type IDs inherited from the *Aurora* line and extended for *Odyssey* and *Eclipse*. The table below lists types seen across *BioWare* engines; many rows are unused in *KotOR* (marked in the **Description** column).

| Resource Name | Type ID | Description                                    |
| ------------- | ------- | ---------------------------------------------- |
| RES           | 0x0000  | Used for `.res` resources within the [save game containers](ERF-File-Format)                     |
| BMP           | 0x0001  | Bitmap image                         |
| MVE           | 0x0002  | Movie/video file       Not used in *KotOR*                   |
| [TGA](https://en.wikipedia.org/wiki/Truevision_TGA)           | 0x0003  | TarGA image format                          |
| [WAV](WAV-File-Format)           | 0x0004  | Wave audio file (see [WAV File Format](WAV-File-Format)) |
| [INI](https://en.wikipedia.org/wiki/INI_file)           | 0x0007  | Configuration file (e.g., `swkotor.ini`, `swkotor2.ini`)                          |
| BMU           | 0x0008  | Unknown  Not used in *KotOR*                                |
| MPG           | 0x0009  | MPEG video  Not used in *KotOR*                            |
| [TXT](https://en.wikipedia.org/wiki/Text_file)           | 0x000A  | Text file  Not used in *KotOR*                                  |
| PLH           | 0x07D0  | *PLaceable Header* type.  Not used in *KotOR*                      |
| TEX           | 0x07D1  | Texture. Not used in *KotOR*                      |
| [MDL](MDL-MDX-File-Format)           | 0x07D2  | 3D [model](MDL-MDX-File-Format) file (see [MDL/MDX File Format](MDL-MDX-File-Format))                                   |
| THG           | 0x07D3  | Unknown. Not used in *KotOR*                                |
| FNT           | 0x07D5  | Font file. Not used in *KotOR*                                  |
| Lua           | 0x07D7  | Lua script. Not used in *KotOR*                             |
| SLT           | 0x07D8  | Unknown. Not used in *KotOR*                               |
| [NSS](NSS-File-Format)           | 0x07D9  | *NWScript* source code (see [NSS File Format](NSS-File-Format))                            |
| [NCS](NCS-File-Format)           | 0x07DA  | *Compiled NWScript* bytecode (see [NCS File Format](NCS-File-Format))                     |
| [MOD](ERF-File-Format)           | 0x07DB  | [*Module* ERF archive/container](ERF-File-Format)                         |
| [ARE](GFF-File-Format#are-area)           | 0x07DC  | *Area* definition (see [GFF-ARE](GFF-Module-and-Area#are))                                 |
| SET           | 0x07DD  | Unknown.  Not used in *KotOR*                               |
| [IFO](GFF-File-Format#ifo-module-info)           | 0x07DE  | *Module* InFOrmation (see [GFF-IFO](GFF-Module-and-Area#ifo))                              |
| BIC           | 0x07DF  | BlueprInt Creature. *KotOR* supports these but nobody uses them, use [UTC](GFF-Creature-and-Dialogue#utc) instead.                  |
| [WOK](BWM-File-Format)           | 0x07E0  | *Walkmesh* (see [BWM File Format](BWM-File-Format))                                |
| [2DA](2DA-File-Format)           | 0x07E1  | *Two-Dimensional Array* data (see [2DA File Format](2DA-File-Format))                      |
| [TLK](TLK-File-Format)           | 0x07E2  | *Talk Table* (Localized Strings, see [TLK File Format](TLK-File-Format))                 |
| [TXI](TXI-File-Format)           | 0x07E6  | [TeXture Information](TXI-File-Format)                            |
| [GIT](GFF-File-Format#git-game-instance-template)           | 0x07E7  | [Game Instance Template](GFF-File-Format#git-game-instance-template) (see [GFF-GIT](GFF-Module-and-Area#git))                          |
| BTI           | 0x07E8  | Blueprint Template Item. *KotOR* supports these but nobody uses them, use [UTI](GFF-Items-and-Economy#uti) instead.                 |
| [UTI](GFF-File-Format#uti-item)           | 0x07E9  | [item templates](GFF-File-Format#uti-item) (see [GFF-UTI](GFF-Items-and-Economy#uti))                                   |
| BTC           | 0x07EA  | Blueprint Template Creature. *KotOR* supports these but nobody uses them, use [UTC](GFF-Creature-and-Dialogue#utc) instead.                |
| [UTC](GFF-File-Format#utc-creature)           | 0x07EB  | [Creature Template](GFF-File-Format#utc-creature) (see [GFF-UTC](GFF-Creature-and-Dialogue#utc))                               |
| [DLG](GFF-File-Format#dlg-dialogue)           | 0x07ED  | Dialogue/conversation (see [GFF-DLG](GFF-Creature-and-Dialogue#dlg))                           |
| [ITP](Bioware-Aurora-Module-and-Area#paletteitp)           | 0x07EE  | *ITP* format (see [Bioware-Aurora-PaletteITP](Bioware-Aurora-Module-and-Area#paletteitp)).                         |
| BTT           | 0x07EF  | *Blueprint Template Trigger*. *KotOR* supports these but nobody uses them, use [UTT](GFF-Spatial-Objects#utt) instead.                 |
| [UTT](GFF-File-Format#utt-trigger)           | 0x07F0  | *Trigger Template* (see [GFF-UTT](GFF-Spatial-Objects#utt)).                                |
| DDS           | 0x07F1  | *DirectDraw Surface Texture* (see [DDS File Format](DDS-File-Format)).                                |
| [UTS](GFF-File-Format#uts-sound)           | 0x07F3  | *Sound Template* (see [GFF-UTS](GFF-Spatial-Objects#uts)).                                |
| LTR           | 0x07F4  | *Letter Format* (see [LTR File Format](LTR-File-Format)). Not used in *KotOR*                                |
| [GFF](GFF-File-Format)           | 0x07F5  | Generic file format (container, see [GFF File Format](GFF-File-Format))                 |
| [FAC](GFF-File-Format#fac-faction)           | 0x07F6  | Faction                               |
| BTE           | 0x07F7  | Blueprint encounter                   |
| [UTE](GFF-File-Format#ute-encounter)           | 0x07F8  | [encounter template](GFF-File-Format#ute-encounter) (see [GFF-UTE](GFF-Spatial-Objects#ute))                              |
| BTD           | 0x07F9  | Blueprint door    Not used in *KotOR*     |
| [UTD](GFF-File-Format#utd-door)           | 0x07FA  | [door templates](GFF-File-Format#utd-door) (see [GFF-UTD](GFF-Spatial-Objects#utd))                                   |
| BTP           | 0x07FB  | Blueprint placeable   Not used in *KotOR*  |
| [UTP](GFF-File-Format#utp-placeable)           | 0x07FC  | [placeable templates](GFF-File-Format#utp-placeable) (see [GFF-UTP](GFF-Spatial-Objects#utp))                              |
| DTF           | 0x07FD  | Unknown  Not used in *KotOR*                                |
| GIC           | 0x07FE  | Unknown  Not used in *KotOR*                                |
| [GUI](GFF-File-Format#gui-graphical-user-interface)           | 0x07FF  | User interface definition (see [GFF-GUI](GFF-GUI))                       |
| CSS           | 0x0800  | Unknown  Not used in *KotOR*                                |
| CCS           | 0x0801  | Unknown  Not used in *KotOR*                                |
| BTM           | 0x0802  | Blueprint merchant.  *KotOR* supports these but nobody uses them, use [UTM](GFF-Items-and-Economy#utm) instead.              |
| [UTM](GFF-File-Format#utm-merchant)           | 0x0803  | [Merchant/store template](GFF-File-Format#utm-merchant) (see [GFF-UTM](GFF-Items-and-Economy#utm))                         |
| [DWK](BWM-File-Format)           | 0x0804  | [Door walkmesh](BWM-File-Format) (see [BWM File Format](BWM-File-Format))                                |
| [PWK](BWM-File-Format)           | 0x0805  | [Placeable walkmesh](BWM-File-Format) (see [BWM File Format](BWM-File-Format))                                |
| BTG           | 0x0806  | Blueprint trigger  Not used in *KotOR*       |
| UTG           | 0x0807  | Unknown            Not used in *KotOR*   |
| [JRL](GFF-File-Format#jrl-journal)           | 0x0808  | Journal/quest log (see [GFF-JRL](GFF-Items-and-Economy#jrl))                               |
| SAV           | 0x0809  | [Save game containers](ERF-File-Format) (see [ERF File Format](ERF-File-Format))                               |
| [UTW](GFF-File-Format#utw-waypoint)           | 0x080A  | [Waypoint Template](GFF-File-Format#utw-waypoint)                               |
| 4PC           | 0x080B  | Unknown  Not used in *KotOR*          |
| [SSF](SSF-File-Format)           | 0x080C  | [Sound Set Files](SSF-File-Format) (see [SSF File Format](SSF-File-Format))                                  |
| HAK           | 0x080D  | Hak pak container. Not used in *KotOR*                                |
| NWM           | 0x080E  | *Neverwinter Nights* module (Not used in *KotOR*)                                 |
| BIK           | 0x080F  | BInK video format                                |
| PTM           | 0x0811  | Unknown       Not used in *KotOR*         |
| PTT           | 0x0812  | Unknown       Not used in *KotOR*         |
| [ERF](ERF-File-Format)           | 0x270D  | [Encapsulated Resource File](ERF-File-Format) (see [ERF File Format](ERF-File-Format))                      |
| [BIF](BIF-File-Format)           | 0x270E  | [Bioware Index File](BIF-File-Format) (container, see [BIF File Format](BIF-File-Format))                    |
| [KEY](KEY-File-Format)           | 0x270F  | [KEY](KEY-File-Format) table ([BIF](BIF-File-Format) index, see [KEY File Format](KEY-File-Format))                          |

## File format index

### File formats

- **[MDL/MDX File Format](MDL-MDX-File-Format)** ← Complete reference for 3D [model](MDL-MDX-File-Format) files
  - **[2DA File Format](2DA-File-Format)** ← Complete reference for Two-Dimensional array format (see also [Official Bioware 2DA Documentation](Bioware-Aurora-Core-Formats#2da)). All individual 2DA file documentation has been inlined into this document.
  - [acbonus.2da](2DA-File-Format#acbonus2da)
  - [ambientmusic.2da](2DA-File-Format#ambientmusic2da)
  - [ambientsound.2da](2DA-File-Format#ambientsound2da)
  - [ammunitiontypes.2da](2DA-File-Format#ammunitiontypes2da)
  - [animations.2da](2DA-File-Format#animations2da)
  - [appearance.2da](2DA-File-Format#appearance2da)
  - [appearancesndset.2da](2DA-File-Format#appearancesndset2da)
  - [baseitems.2da](2DA-File-Format#baseitems2da)
  - [bindablekeys.2da](2DA-File-Format#bindablekeys2da)
  - [bodybag.2da](2DA-File-Format#bodybag2da)
  - [camerastyle.2da](2DA-File-Format#camerastyle2da)
  - [classes.2da](2DA-File-Format#classes2da)
  - [classpowergain.2da](2DA-File-Format#classpowergain2da)
  - [combatanimations.2da](2DA-File-Format#combatanimations2da)
  - [creaturespeed.2da](2DA-File-Format#creaturespeed2da)
  - [cursors.2da](2DA-File-Format#cursors2da)
  - [dialoganimations.2da](2DA-File-Format#dialoganimations2da)
  - [difficultyopt.2da](2DA-File-Format#difficultyopt2da)
  - [disease.2da](2DA-File-Format#disease2da)
  - [doortypes.2da](2DA-File-Format#doortypes2da)
  - [droiddischarge.2da](2DA-File-Format#droiddischarge2da)
  - [effecticon.2da](2DA-File-Format#effecticon2da)
  - [emotion.2da](2DA-File-Format#emotion2da)
  - [encdifficulty.2da](2DA-File-Format#encdifficulty2da)
  - [exptable.2da](2DA-File-Format#exptable2da)
  - [facialanim.2da](2DA-File-Format#facialanim2da)
  - [feat.2da](2DA-File-Format#feat2da)
  - [featgain.2da](2DA-File-Format#featgain2da)
  - [feedbacktext.2da](2DA-File-Format#feedbacktext2da)
  - [footstepsounds.2da](2DA-File-Format#footstepsounds2da)
  - [forceshields.2da](2DA-File-Format#forceshields2da)
  - [fractionalcr.2da](2DA-File-Format#fractionalcr2da)
  - [gender.2da](2DA-File-Format#gender2da)
  - [genericdoors.2da](2DA-File-Format#genericdoors2da)
  - [globalcat.2da](2DA-File-Format#globalcat2da)
  - [grenadesnd.2da](2DA-File-Format#grenadesnd2da)
  - [guisounds.2da](2DA-File-Format#guisounds2da)
  - [heads.2da](2DA-File-Format#heads2da)
  - [inventorysnds.2da](2DA-File-Format#inventorysnds2da)
  - [iprp_abilities.2da](2DA-File-Format#iprp_abilities2da)
  - [iprp_acmodtype.2da](2DA-File-Format#iprp_acmodtype2da)
  - [iprp_aligngrp.2da](2DA-File-Format#iprp_aligngrp2da)
  - [iprp_ammotype.2da](2DA-File-Format#iprp_ammotype2da)
  - [iprp_combatdam.2da](2DA-File-Format#iprp_combatdam2da)
  - [iprp_costtable.2da](2DA-File-Format#iprp_costtable2da)
  - [iprp_damagecost.2da](2DA-File-Format#iprp_damagecost2da)
  - [iprp_damagetype.2da](2DA-File-Format#iprp_damagetype2da)
  - [iprp_immunity.2da](2DA-File-Format#iprp_immunity2da)
  - [iprp_lightcol.2da](2DA-File-Format#iprp_lightcol2da)
  - [iprp_monstdam.2da](2DA-File-Format#iprp_monstdam2da)
  - [iprp_mosterhit.2da](2DA-File-Format#iprp_mosterhit2da)
  - [iprp_onhit.2da](2DA-File-Format#iprp_onhit2da)
  - [iprp_paramtable.2da](2DA-File-Format#iprp_paramtable2da)
  - [iprp_protection.2da](2DA-File-Format#iprp_protection2da)
  - [iprp_saveelement.2da](2DA-File-Format#iprp_saveelement2da)
  - [iprp_savingthrow.2da](2DA-File-Format#iprp_savingthrow2da)
  - [iprp_walk.2da](2DA-File-Format#iprp_walk2da)
  - [itempropdef.2da](2DA-File-Format#itempropdef2da)
  - [itemprops.2da](2DA-File-Format#itemprops2da)
  - [keymap.2da](2DA-File-Format#keymap2da)
  - [loadscreenhints.2da](2DA-File-Format#loadscreenhints2da)
  - [loadscreens.2da](2DA-File-Format#loadscreens2da)
  - [masterfeats.2da](2DA-File-Format#masterfeats2da)
  - [modulesave.2da](2DA-File-Format#modulesave2da)
  - [movies.2da](2DA-File-Format#movies2da)
  - [pazaakdecks.2da](2DA-File-Format#pazaakdecks2da)
  - [placeableobjsnds.2da](2DA-File-Format#placeableobjsnds2da)
  - [placeables.2da](2DA-File-Format#placeables2da)
  - [planetary.2da](2DA-File-Format#planetary2da)
  - [plot.2da](2DA-File-Format#plot2da)
  - [poison.2da](2DA-File-Format#poison2da)
  - [portraits.2da](2DA-File-Format#portraits2da)
  - [prioritygroups.2da](2DA-File-Format#prioritygroups2da)
  - [racialtypes.2da](2DA-File-Format#racialtypes2da)
  - [ranges.2da](2DA-File-Format#ranges2da)
  - [regeneration.2da](2DA-File-Format#regeneration2da)
  - [repute.2da](2DA-File-Format#repute2da)
  - [skills.2da](2DA-File-Format#skills2da)
  - [soundset.2da](2DA-File-Format#soundset2da)
  - [spells.2da](2DA-File-Format#spells2da)
  - [stringtokens.2da](2DA-File-Format#stringtokens2da)
  - [subrace.2da](2DA-File-Format#subrace2da)
  - [surfacemat.2da](2DA-File-Format#surfacemat2da)
  - [texpacks.2da](2DA-File-Format#texpacks2da)
  - [traps.2da](2DA-File-Format#traps2da)
  - [tutorial.2da](2DA-File-Format#tutorial2da)
  - [upcrystals.2da](2DA-File-Format#upcrystals2da)
  - [upgrade.2da](2DA-File-Format#upgrade2da)
  - [videoeffects.2da](2DA-File-Format#videoeffects2da)
  - [visualeffects.2da](2DA-File-Format#visualeffects2da)
  - [weaponsounds.2da](2DA-File-Format#weaponsounds2da)
  - [xptable.2da](2DA-File-Format#xptable2da)
- **[TLK File Format](TLK-File-Format)** ← Complete reference for [Talk Table](TLK-File-Format) format
- [BIF File Format](BIF-File-Format) ← BioWare Infinity format
- [KEY File Format](KEY-File-Format) ← [KEY](KEY-File-Format) file format
- **[BWM File Format](BWM-File-Format)** ← Complete reference for Binary [walkmesh](BWM-File-Format) format
- **[GUI File Format](GFF-GUI)** ← Complete reference for Graphical User Interface format
- [ERF File Format](ERF-File-Format) ← Encapsulated Resource format (MOD, SAV, HAK; [RIM comparison](ERF-File-Format#rim-versus-erf))
- **[Kit Structure Documentation](Kit-Structure-Documentation)** ← Complete reference for indoor kit structure and generation
- [GFF File Format](GFF-File-Format) ← Generic file Format (see also [Official Bioware GFF Documentation](Bioware-Aurora-Core-Formats#gff))
  - [ARE (Area)](GFF-Module-and-Area#are)
  - [DLG (Dialogue)](GFF-Creature-and-Dialogue#dlg)
  - [GIT (Game Instance Template)](GFF-Module-and-Area#git)
  - [GUI (Graphical User Interface)](GFF-GUI)
  - [IFO (Module Info)](GFF-Module-and-Area#ifo)
  - [JRL (Journal)](GFF-Items-and-Economy#jrl)
  - [PTH (Path)](GFF-Spatial-Objects#pth)
  - [UTC (Creature)](GFF-Creature-and-Dialogue#utc)
  - [UTD (Door)](GFF-Spatial-Objects#utd)
  - [UTE (Encounter)](GFF-Spatial-Objects#ute)
  - [UTI (Item)](GFF-Items-and-Economy#uti)
  - [UTM (Merchant)](GFF-Items-and-Economy#utm)
  - [UTP (Placeable)](GFF-Spatial-Objects#utp)
  - [UTS (Sound)](GFF-Spatial-Objects#uts)
  - [UTT (Trigger)](GFF-Spatial-Objects#utt)
  - [UTW (Waypoint)](GFF-Spatial-Objects#utw)
- [DDS File Format](DDS-File-Format) ← DirectDraw Surface texture format
- [LIP File Format](LIP-File-Format) ← [LIP](LIP-File-Format) sync format
- [LTR File Format](LTR-File-Format) ← [Letter](LTR-File-Format) format
- [LYT File Format](LYT-File-Format) ← [Layout](LYT-File-Format) format
- [NCS File Format](NCS-File-Format) ← [NwScript Compiled Script](NCS-File-Format) format
- [NSS File Format](NSS-File-Format) ← [NwScript Source](NSS-File-Format) format (*nwscript.nss*, function/constant definitions)
- [RIM File Format](RIM-File-Format) ← [Resource Image](RIM-File-Format) format
- [SSF File Format](SSF-File-Format) ← [Sound Set Files](SSF-File-Format) format
- [TPC File Format](TPC-File-Format) ← [Texture Pack Container](TPC-File-Format) format
- [TXI File Format](TXI-File-Format) ← [Texture Info](TXI-File-Format) format
- [VIS File Format](VIS-File-Format) ← [Visibility](VIS-File-Format) format
- [WAV File Format](WAV-File-Format) ← [Wave](WAV-File-Format) audio format

### See also

- [Concepts](Concepts) — Override, BIF/KEY, MOD/ERF/RIM, GFF, 2DA, language IDs
- [KEY-File-Format](KEY-File-Format) — KEY binary layout and index role
- [Mod-Creation-Best-Practices](Mod-Creation-Best-Practices#file-priority-and-where-to-put-your-files) — Where to install files
- [Home](Home) — Wiki hub
- [Reverse Engineering Findings — Resource Management System](reverse_engineering_findings#resource-management-system) — Engine `CExoResMan` / resource loading (conceptual)
