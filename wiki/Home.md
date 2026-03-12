# Welcome to the PyKotor Wiki

## Documentation

**Start here:** New to modding? [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) → [Mod Creation Best Practices](Mod-Creation-Best-Practices) → [File formats and specifications](#file-formats-and-specifications) or [TSLPatcher guides](TSLPatcher's-Official-Readme) as needed. Core terms: [Concepts](Concepts). Binary and engine-level detail: [Low-level structures and implementations](#low-level-structures-and-implementations). [Community sources and archives](#community-sources-and-archives). Contributing: [Wiki Conventions](Wiki-Conventions).

### For End Users

- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher)

### Guides and tutorials

Installation, tool use, and step-by-step guides:

- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers.)
- [HoloPatcher Feature Coverage Overview](Explanations-on-HoloPatcher-Internal-Logic)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)
- [TSLPatcher Thread Complete Container](TSLPatcher_Thread_Complete)
- **[TSLPatcher InstallList Syntax Guide](TSLPatcher-InstallList-Syntax)** — File installation
- **[TSLPatcher TLKList Syntax Guide](TSLPatcher-TLKList-Syntax)** — TLK ([TalkTable](TLK-File-Format)) modifications
- **[TSLPatcher 2DAList Syntax Guide](TSLPatcher-2DAList-Syntax)** — [2DA](2DA-File-Format) patches
- **[TSLPatcher GFFList Syntax Guide](TSLPatcher-GFFList-Syntax)** — [GFF](GFF-File-Format) modifications
- **[TSLPatcher SSFList Syntax Guide](TSLPatcher-SSFList-Syntax)** — SSF ([sound set files](SSF-File-Format))
- **[TSLPatcher HACKList Syntax Guide](TSLPatcher-HACKList-Syntax)** — Binary patches
- [Blender Integration](Blender-Integration)
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) — Build indoor modules from kits
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) — Understanding why room crossing fails and what must agree: layout, walkmesh, roomlinks, LYT/VIS
- [Indoor Area Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide) — Complete modder workflow for indoor rooms, walkmeshes, roomlinks, doors, LYT, and VIS
- [KotorDiff Integration in PyKotorCLI](KotorDiff-Integration)

**Holocron Toolset (in-app help):**

- [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started)
- [Holocron Toolset: New Features Quick Guide](Holocron-Toolset-New-Features-Guide) — Favorites, batch ops, rename, Open With, etc.
- [Holocron Toolset: Core resources](Holocron-Toolset-Core-Resources) — Core tab (KEY/BIF)
- [Holocron Toolset: Module resources](Holocron-Toolset-Module-Resources)
- [Holocron Toolset: Override resources](Holocron-Toolset-Override-Resources)
- [Holocron Toolset: Module Editor](Holocron-Toolset-Module-Editor) — Module Designer controls
- [Holocron Toolset: Map Builder](Holocron-Toolset-Map-Builder) — Indoor Map Builder controls

**Tutorials:**

- [Tutorial: Creating custom robes](Tutorial-Creating-Custom-Robes)
- [Tutorial: Creating a new store](Tutorial-Creating-a-New-Store)
- [Tutorial: Area transitions](Tutorial-Area-Transitions)
- [Tutorial: Creating static cameras](Tutorial-Creating-Static-Cameras)

**Scripting (NWScript):** Function and constant reference for writing scripts. Full index and all routine/constant pages: [NSS File Format](NSS-File-Format). Quick links to major categories:

- [NSS Shared Functions: Actions](NSS-Shared-Functions-Actions) · [Combat](NSS-Shared-Functions-Combat-Functions) · [Dialog and conversation](NSS-Shared-Functions-Dialog-and-Conversation-Functions) · [Effects](NSS-Shared-Functions-Effects-System) · [Item management](NSS-Shared-Functions-Item-Management) · [Module and area](NSS-Shared-Functions-Module-and-Area-Functions) · [Party](NSS-Shared-Functions-Party-Management) · [Skills and feats](NSS-Shared-Functions-Skills-and-Feats)
- [NSS Shared Constants: Ability](NSS-Shared-Constants-Ability-Constants) · [Object type](NSS-Shared-Constants-Object-Type-Constants) · [Class type](NSS-Shared-Constants-Class-Type-Constants) · [Visual effects](NSS-Shared-Constants-Visual-Effects-(VFX))
- [NSS K1-Only constants and functions](NSS-K1-Only-Constants-NPC-Constants) (see [NSS File Format](NSS-File-Format) for full K1 index)
- [NSS TSL-Only constants and functions](NSS-TSL-Only-Functions-Combat-Functions) (see [NSS File Format](NSS-File-Format) for full TSL index)

### File formats and specifications

Reference for binary layout, field definitions, and format behaviour. For scripting usage see [Scripting (NWScript)](#guides-and-tutorials) above; for implementation details see [Low-level structures and implementations](#low-level-structures-and-implementations).

### Official Bioware Aurora Documentation

The following documents are official Bioware Aurora Engine file format specifications. These are authoritative references for the underlying file formats used by KotOR:

- **[2DA File Format](Bioware-Aurora-2DA)** - Official 2DA (Two-Dimensional array) format specification
- **[GFF File Format](Bioware-Aurora-GFF)** - Official Generic file format specification
- **[Common GFF Structs](Bioware-Aurora-CommonGFFStructs)** - Common [GFF](GFF-File-Format) structure definitions
- **[Area File Format](Bioware-Aurora-AreaFile)** - Official ARE (Area) file format
- **[Creature Format](Bioware-Aurora-Creature)** - Official UTC (Creature) format
- **[Item Format](Bioware-Aurora-Item)** - Official UTI (Item) format
- **[Door/Placeable Format](Bioware-Aurora-DoorPlaceableGFF)** - Official [UTD](GFF-File-Format#utd-door)/[UTP](GFF-File-Format#utp-placeable) formats
- **[Encounter Format](Bioware-Aurora-Encounter)** - Official UTE (Encounter) format
- **[Trigger Format](Bioware-Aurora-Trigger)** - Official UTT (Trigger) format
- **[Waypoint Format](Bioware-Aurora-Waypoint)** - Official UTW (Waypoint) format
- **[Store Format](Bioware-Aurora-Store)** - Official UTM (Store) format
- **[Sound Object Format](Bioware-Aurora-SoundObject)** - Official UTS (Sound) format
- **[Journal Format](Bioware-Aurora-Journal)** - Official JRL (Journal) format
- **[Conversation Format](Bioware-Aurora-Conversation)** - Official DLG (Dialogue) format
- **[IFO Format](Bioware-Aurora-IFO)** - Official [module info](GFF-File-Format#ifo-module-info) format
- **[ERF Format](Bioware-Aurora-ERF)** - Official Encapsulated Resource format
- **[Key/BIF Format](Bioware-Aurora-KeyBIF)** - Official [KEY](KEY-File-Format) and [BIF file](BIF-File-Format) formats
- **[TalkTable Format](Bioware-Aurora-TalkTable)** - Official TLK ([Talk Table](TLK-File-Format)) format
- **[SSF Format](Bioware-Aurora-SSF)** - Official [sound set files](SSF-File-Format) format
- **[Localized Strings Format](Bioware-Aurora-LocalizedStrings)** - Official localized strings format
- **[Faction Format](Bioware-Aurora-Faction)** - Official faction data format
- **[Palette/ITP Format](Bioware-Aurora-PaletteITP)** - Official palette and ITP formats

### Odyssey Engine Basics (KotOR)

The following information describes the resource system used by **KotOR and TSL**. While KotOR is derived from the Aurora engine (Neverwinter Nights) and shares the same resource system, this section focuses on **KotOR-specific** behavior and file locations. Some details (like `nwn.ini`) are NWN-specific and are noted as such.

#### Application lifecycle (KotOR and TSL)

Both games use the same high-level flow: the executable initializes an application manager, creates a server (game world) and client (rendering, input, UI), then runs a main loop that pumps window messages, updates the render window, and drives the Aurora/Odyssey subsystems. Resource loading follows the resolution order below; the resource manager services requests from override, then module/ERF, then KEY/BIF. Reinitializing the Aurora engine (e.g. after resolution or display changes) reloads or refreshes core subsystems while preserving the same client/server split. Scripts (NCS) and dialogues (DLG) run in the server context; the client handles display, camera, and input and receives updates from the server.

**Client and server:** The Odyssey engine (like Aurora) separates a **server** (game world, rules, scripts, resources) from a **client** (rendering, input, UI). The server owns area state, creatures, items, and script execution; the client displays the world and sends input. This split is important for modding and for understanding [NCS execution](NCS-File-Format) and [resource resolution](KEY-File-Format).

#### Important Files

- **[`chitin.key`](KEY-File-Format)**: Master index file that maps resource names to [BIF containers](BIF-File-Format) locations. Given a resource name, [chitin.key](KEY-File-Format) can be used to locate the master data file ([BIF](BIF-File-Format)) containing the resource.
- **[`dialog.tlk`](TLK-File-Format)**: Text resource file containing localized strings referenced by [StrRef](TLK-File-Format#string-references-strref) IDs. This centralizes strings for easy localization and allows changing text without modifying or recompiling scripts. Different language versions of [dialog.tlk](TLK-File-Format) can be installed for localization support.
- **`kotor.ini`**: Configuration file with `[Alias]` section mapping logical directory names to physical paths. This allows the game to locate data files regardless of installation directory structure.

**Reference**: **[xoreos-docs](https://github.com/xoreos/xoreos-docs)** ([Mirror: th3w1zard1/xoreos-docs](https://github.com/th3w1zard1/xoreos-docs)): [`specs/torlack/basics.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html) - Tim Smith (Torlack)'s Aurora engine basics documentation (NWN-focused)

#### Resource Resolution Order

The engine satisfies every resource request (by *ResRef* and type) in this order. See [KEY File Format](KEY-File-Format#key-file-purpose) for how demand flows through the resource manager.

1. Override folder (`override/`)
2. Currently loaded MOD/[ERF files](ERF-File-Format)
3. Currently loaded SAV file (if in-game)
4. [BIF files](BIF-File-Format) via [KEY](KEY-File-Format) lookup
5. Hardcoded defaults

#### Resource Types

KotOR uses hexadecimal resource type identifiers derived from the Aurora engine and further expanded upon for its Odyssey engine. The following table lists resource types valid in the four BioWare engines. Due to this, some of these are obviously not supported in KotOR.

| Resource Name | type ID | Description                                    |
| ------------- | ------- | ---------------------------------------------- |
| RES           | 0x0000  | Used for .res within the saves                     |
| BMP           | 0x0001  | Bitmap image                         |
| MVE           | 0x0002  | Movie/video file       Not used in KotOR                   |
| TGA           | 0x0003  | TarGA image format                          |
| [WAV](WAV-File-Format)           | 0x0004  | Wave audio file (see [WAV File Format](WAV-File-Format)) |
| INI           | 0x0007  | Configuration file (e.g., `swkotor.ini`, `swkotor2.ini`)                          |
| BMU           | 0x0008  | Unknown  Not used in KotOR                                |
| MPG           | 0x0009  | MPEG video  Not used in KotOR                            |
| TXT           | 0x000A  | Text file  Not used in KotOR                                  |
| PLH           | 0x07D0  | Placeable header  Not used in KotOR                      |
| TEX           | 0x07D1  | Texture                      |
| [MDL](MDL-MDX-File-Format)           | 0x07D2  | 3D [model](MDL-MDX-File-Format) file (see [MDL/MDX File Format](MDL-MDX-File-Format))                                   |
| THG           | 0x07D3  | Unknown  Not used in KotOR                                |
| FNT           | 0x07D5  | Font file  Not used in KotOR                                  |
| Lua           | 0x07D7  | Lua script  Not used in KotOR                             |
| SLT           | 0x07D8  | Unknown  Not used in KotOR                               |
| [NSS](NSS-File-Format)           | 0x07D9  | NWScript source code (see [NSS File Format](NSS-File-Format))                            |
| [NCS](NCS-File-Format)           | 0x07DA  | Compiled NWScript bytecode (see [NCS File Format](NCS-File-Format))                     |
| [MOD](ERF-File-Format)           | 0x07DB  | Module container ([ERF](ERF-File-Format) variant, see [ERF File Format](ERF-File-Format))                          |
| [ARE](GFF-File-Format#are-area)           | 0x07DC  | Area definition (see [GFF-ARE](GFF-ARE))                                 |
| SET           | 0x07DD  | Unknown  Not used in KotOR                               |
| [IFO](GFF-File-Format#ifo-module-info)           | 0x07DE  | Module information (see [GFF-IFO](GFF-IFO))                              |
| BIC           | 0x07DF  | Character template   Not used in KotOR                  |
| [WOK](BWM-File-Format)           | 0x07E0  | Walkmesh (see [BWM File Format](BWM-File-Format))                                |
| [2DA](2DA-File-Format)           | 0x07E1  | Two-dimensional array data (see [2DA File Format](2DA-File-Format))                      |
| [TLK](TLK-File-Format)           | 0x07E2  | Talk table (localized strings, see [TLK File Format](TLK-File-Format))                 |
| [TXI](TXI-File-Format)           | 0x07E6  | [texture](TPC-File-Format) information (see [TXI File Format](TXI-File-Format))                             |
| [GIT](GFF-File-Format#git-game-instance-template)           | 0x07E7  | [game instance template](GFF-File-Format#git-game-instance-template) (see [GFF-GIT](GFF-GIT))                          |
| BTI           | 0x07E8  | Blueprint trigger    Not used in KotOR                 |
| [UTI](GFF-File-Format#uti-item)           | 0x07E9  | [item templates](GFF-File-Format#uti-item) (see [GFF-UTI](GFF-UTI))                                   |
| BTC           | 0x07EA  | Blueprint creature    Not used in KotOR                |
| [UTC](GFF-File-Format#utc-creature)           | 0x07EB  | [creature templates](GFF-File-Format#utc-creature) (see [GFF-UTC](GFF-UTC))                               |
| [DLG](GFF-File-Format#dlg-dialogue)           | 0x07ED  | Dialogue/conversation (see [GFF-DLG](GFF-DLG))                           |
| ITP           | 0x07EE  | ITP format (legacy name for [GFF](GFF-File-Format))  Not used in KotOR                         |
| BTT           | 0x07EF  | Blueprint trigger    Not used in KotOR                 |
| [UTT](GFF-File-Format#utt-trigger)           | 0x07F0  | Trigger template (see [GFF-UTT](GFF-UTT))                                |
| DDS           | 0x07F1  | DirectDraw Surface texture (see [DDS File Format](DDS-File-Format))                                |
| [UTS](GFF-File-Format#uts-sound)           | 0x07F3  | Sound template (see [GFF-UTS](GFF-UTS))                                |
| LTR           | 0x07F4  | Letter format (see [LTR File Format](LTR-File-Format))                                |
| [GFF](GFF-File-Format)           | 0x07F5  | Generic file format (container, see [GFF File Format](GFF-File-Format))                 |
| [FAC](GFF-File-Format#fac-faction)           | 0x07F6  | Faction                               |
| BTE           | 0x07F7  | Blueprint encounter                   |
| [UTE](GFF-File-Format#ute-encounter)           | 0x07F8  | [encounter template](GFF-File-Format#ute-encounter) (see [GFF-UTE](GFF-UTE))                              |
| BTD           | 0x07F9  | Blueprint door    Not used in KotOR     |
| [UTD](GFF-File-Format#utd-door)           | 0x07FA  | [door templates](GFF-File-Format#utd-door) (see [GFF-UTD](GFF-UTD))                                   |
| BTP           | 0x07FB  | Blueprint placeable   Not used in KotOR  |
| [UTP](GFF-File-Format#utp-placeable)           | 0x07FC  | [placeable templates](GFF-File-Format#utp-placeable) (see [GFF-UTP](GFF-UTP))                              |
| DTF           | 0x07FD  | Unknown  Not used in KotOR                                |
| GIC           | 0x07FE  | Unknown  Not used in KotOR                                |
| [GUI](GFF-File-Format#gui-graphical-user-interface)           | 0x07FF  | User interface definition (see [GFF-GUI](GFF-GUI))                       |
| CSS           | 0x0800  | Unknown  Not used in KotOR                                |
| CCS           | 0x0801  | Unknown  Not used in KotOR                                |
| BTM           | 0x0802  | Blueprint merchant    Not used in KotOR                |
| [UTM](GFF-File-Format#utm-merchant)           | 0x0803  | Merchant/store template (see [GFF-UTM](GFF-UTM))                         |
| [DWK](BWM-File-Format)           | 0x0804  | Door walkmesh (see [BWM File Format](BWM-File-Format))                                |
| [PWK](BWM-File-Format)           | 0x0805  | Placeable walkmesh (see [BWM File Format](BWM-File-Format))                                |
| BTG           | 0x0806  | Blueprint trigger  Not used in KotOR       |
| UTG           | 0x0807  | Unknown            Not used in KotOR   |
| [JRL](GFF-File-Format#jrl-journal)           | 0x0808  | Journal/quest log (see [GFF-JRL](GFF-JRL))                               |
| SAV           | 0x0809  | [Save game containers](ERF-File-Format) (see [ERF File Format](ERF-File-Format))                               |
| [UTW](GFF-File-Format#utw-waypoint)           | 0x080A  | [Waypoint Template](GFF-File-Format#utw-waypoint)                               |
| 4PC           | 0x080B  | Unknown  Not used in KotOR          |
| [SSF](SSF-File-Format)           | 0x080C  | [Sound Set Files](SSF-File-Format) (see [SSF File Format](SSF-File-Format))                                  |
| HAK           | 0x080D  | Hak pak container. Not used in KotOR                                |
| NWM           | 0x080E  | Neverwinter Nights module ([ERF](ERF-File-Format) variant, not used in KotOR)                                 |
| BIK           | 0x080F  | Bink video format                                |
| PTM           | 0x0811  | Unknown       Not used in KotOR         |
| PTT           | 0x0812  | Unknown       Not used in KotOR         |
| [ERF](ERF-File-Format)           | 0x270D  | Encapsulated Resource File (see [ERF File Format](ERF-File-Format))                      |
| [BIF](BIF-File-Format)           | 0x270E  | Bioware Index File (container, see [BIF File Format](BIF-File-Format))                    |
| [KEY](KEY-File-Format)           | 0x270F  | [KEY](KEY-File-Format) table ([BIF](BIF-File-Format) index, see [KEY File Format](KEY-File-Format))                          |

#### Language IDs

This language ID usually is represented as an enum. It is equivalent within all engines and all games, with some newer games specifying more formats but always staying backwards compatible with the others.

**KotOR** (odyssey) specifically can only support

**Reference**: **[xoreos-docs](https://github.com/xoreos/xoreos-docs)** ([Mirror: th3w1zard1/xoreos-docs](https://github.com/th3w1zard1/xoreos-docs)): [`specs/torlack/basics.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html) - Language ID definitions (NWN-focused but applicable to KotOR)

| Language        | ID | Notes                                |
| --------------- | -- |                                      |
| English         | 0  |                                      |
| French          | 1  |                                      |
| German          | 2  |                                      |
| Italian         | 3  |                                      |
| Spanish         | 4  |                                      |
| Polish          | 5  |  cp-1250, only released for KotOR 1  |

**Reference**: **[xoreos-docs](https://github.com/xoreos/xoreos-docs)** ([Mirror: th3w1zard1/xoreos-docs](https://github.com/th3w1zard1/xoreos-docs)): [`specs/torlack/basics.html`](https://github.com/xoreos/xoreos-docs/blob/master/specs/torlack/basics.html) - Tim Smith (Torlack)'s NWN data file Basics documentation (Aurora engine fundamentals)

### File Formats

- **[MDL/MDX File Format](MDL-MDX-File-Format)** ← Complete reference for 3D [model](MDL-MDX-File-Format) files
  - **[2DA File Format](2DA-File-Format)** ← Complete reference for Two-Dimensional array format (see also [Official Bioware 2DA Documentation](Bioware-Aurora-2DA)). All individual 2DA file documentation has been inlined into this document.
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
- [ERF File Format](ERF-File-Format) ← Encapsulated Resource format
- **[Kit Structure Documentation](Kit-Structure-Documentation)** ← Complete reference for indoor kit structure and generation
- [GFF File Format](GFF-File-Format) ← Generic file Format (see also [Official Bioware GFF Documentation](Bioware-Aurora-GFF))
  - [ARE (Area)](GFF-ARE)
  - [DLG (Dialogue)](GFF-DLG)
  - [GIT (Game Instance Template)](GFF-GIT)
  - [GUI (Graphical User Interface)](GFF-GUI)
  - [IFO (Module Info)](GFF-IFO)
  - [JRL (Journal)](GFF-JRL)
  - [PTH (Path)](GFF-PTH)
  - [UTC (Creature)](GFF-UTC)
  - [UTD (Door)](GFF-UTD)
  - [UTE (Encounter)](GFF-UTE)
  - [UTI (Item)](GFF-UTI)
  - [UTM (Merchant)](GFF-UTM)
  - [UTP (Placeable)](GFF-UTP)
  - [UTS (Sound)](GFF-UTS)
  - [UTT (Trigger)](GFF-UTT)
  - [UTW (Waypoint)](GFF-UTW)
- [DDS File Format](DDS-File-Format) ← DirectDraw Surface texture format
- [LIP File Format](LIP-File-Format) ← [LIP](LIP-File-Format) sync format
- [LTR File Format](LTR-File-Format) ← Letter format
- [LYT File Format](LYT-File-Format) ← Layout format
- [NCS File Format](NCS-File-Format) ← NwScript Compiled Script format
- [NSS File Format](NSS-File-Format) ← NwScript Source format (nwscript.nss, function/constant definitions)
- [RIM File Format](ERF-File-Format) ← Resource Index Manifest format
- [SSF File Format](SSF-File-Format) ← [sound set files](SSF-File-Format) format
- [TLK File Format](TLK-File-Format) ← [Talk Table](TLK-File-Format) format
- [TPC File Format](TPC-File-Format) ← [texture](TPC-File-Format) Pack Container format
- [TXI File Format](TXI-File-Format) ← [texture](TPC-File-Format) Info format
- [VIS File Format](VIS-File-Format) ← Visibility format
- [WAV File Format](WAV-File-Format) ← Wave audio format

### Low-level structures and implementations

Binary layout, engine behaviour, and implementation details for developers and reverse engineering:

- [Reverse Engineering Findings](reverse_engineering_findings)
- [CExoResMan](CExoResMan)
- [Game Engine BWM AABB Implementation](Game-Engine-BWM-AABB-Implementation)
- [Qt ItemView selection and RobustTableView](Qt-ItemView-Selection-and-RobustTableView)
- [UTC Editor field types (Reva)](UTC-Editor-Field-Types-Reva)
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide) — Technical details (distinct from the [user guide](Indoor-Map-Builder-User-Guide) in Guides and tutorials)
- [HoloPatcher internal logic](Explanations-on-HoloPatcher-Internal-Logic)

## Vendor Implementations

PyKotor is not the first of its kind, below you'll find other KotOR tools, resources, projects, and even full engine rewrites.

### Engine Reimplementations

Complete game engine rewrites that can load and play KotOR:

- **[xoreos](https://github.com/xoreos/xoreos)** - C++ reimplementation of BioWare's Aurora/Odyssey/Eclipse engine, supports multiple BioWare games including KotOR. ([Mirror: th3w1zard1/xoreos](https://github.com/th3w1zard1/xoreos))
- **[reone](https://github.com/seedhartha/reone)** - Modern C++ KotOR engine with OpenGL rendering. Focus on performance and clean architecture. ([Mirror: th3w1zard1/reone](https://github.com/th3w1zard1/reone))
  - **NOTE**: This project seems to be abandoned by seedhartha, but was picked up by the community here: https://github.com/modawan/reone though I can't speak to its authority)
- **[KotOR.js](https://github.com/KobaltBlu/KotOR.js)** - TypeScript/JavaScript engine running in browsers via WebGL. Enables playing KotOR directly in web browsers. ([Mirror: th3w1zard1/KotOR.js](https://github.com/th3w1zard1/KotOR.js))
- **[NorthernLights](https://github.com/lachjames/NorthernLights)** - .NET/C# engine implementation with Unity integration capabilities (based on KotOR-Unity project with further improvements) ([Mirror: th3w1zard1/NorthernLights](https://github.com/th3w1zard1/NorthernLights))
- **[KotOR-Unity](https://github.com/reubenduncan/KotOR-Unity)** - Unity-based KotOR engine rewrite. Leverages Unity's rendering and physics. ([Mirror: th3w1zard1/KotOR-Unity](https://github.com/th3w1zard1/KotOR-Unity))

### File Format Libraries

Libraries focused on reading/writing KotOR file formats:

- **[xoreos-tools](https://github.com/xoreos/xoreos-tools)** - Command-line tools for extracting and converting Aurora file formats ([Mirror: th3w1zard1/xoreos-tools](https://github.com/th3w1zard1/xoreos-tools))
- **[Kotor.NET](https://github.com/NickHugi/Kotor.NET)** - .NET library for KotOR file formats with builder APIs
- **[BioWare.NET](https://github.com/th3w1zard1/BioWare.NET)** - Another .NET library for KotOR file formats, intended to be a direct port of PyKotor
- **[Rakata](https://codeberg.org/Synchro/rakata)** - A rust-native codebase for working with the Odyssey engine.

### 3D Modeling Tools

Tools for working with KotOR 3D [models](MDL-MDX-File-Format) and [textures](TPC-File-Format):

- **[kotorblender](https://github.com/OldRepublicDevs/kotorblender)** - Blender add-on for importing/exporting KotOR [MDL files](MDL-MDX-File-Format), [LYT layouts](LYT-File-Format), [PTH paths](GFF-PTH), and [walkmeshes](BWM-File-Format) with active Holocron Toolset bridge support (see [Blender Integration](Blender-Integration))
- **[mdlops](https://github.com/ndixUR/mdlops)** - Legacy Python [MDL](MDL-MDX-File-Format) toolkit for [model](MDL-MDX-File-Format) conversions ([Mirror: th3w1zard1/mdlops](https://github.com/th3w1zard1/mdlops))
- **[tga2tpc](https://github.com/ndixUR/tga2tpc)** - Standalone TGA to [TPC](TPC-File-Format) [texture](TPC-File-Format) converter ([Mirror: th3w1zard1/tga2tpc](https://github.com/th3w1zard1/tga2tpc))
- **[DLZ-Tool](https://github.com/LaneDibello/DLZ-Tool)** - DLZ file decompression tool ([Mirror: th3w1zard1/DLZ-Tool](https://github.com/th3w1zard1/DLZ-Tool))
- **[WalkmeshVisualizer](https://github.com/glasnonck/WalkmeshVisualizer)** - [walkmesh](BWM-File-Format) viewing and debugging tool ([Mirror: th3w1zard1/WalkmeshVisualizer](https://github.com/th3w1zard1/WalkmeshVisualizer))

### Script Development

Tools and Resources for working with NWScript in KotOR:

- **[HoloLSP](https://github.com/th3w1zard1/HoloLSP)** - Language Server Protocol implementation for NWScript, complete with all kotor-specific constants and functions, as well as everything else from each game's (k1/tsl's) `nwscript.nss`
- **[nwscript-mode.el](https://github.com/implicit-image/nwscript-mode.el)** - Emacs major mode for NWScript editing ([Mirror: th3w1zard1/nwscript-mode.el](https://github.com/th3w1zard1/nwscript-mode.el))
- **[Vanilla_KOTOR_Script_Source](https://github.com/KOTORCommunityPatches/Vanilla_KOTOR_Script_Source)** - Decompiled vanilla KotOR scripts for reference ([Mirror: th3w1zard1/Vanilla_KOTOR_Script_Source](https://github.com/th3w1zard1/Vanilla_KOTOR_Script_Source))

### Modding Tools

Tools for creating and installing mods:

- **PyKotorCLI (PyKotor)** - CLI-first toolset for packing, conversion, Holocron kit generation, and [GUI](GFF-File-Format#gui-graphical-user-interface) layout scaling. `uvx --refresh pykotor kit-generate --installation <path> --module <module> --output <dir>` runs headless; launching with no arguments opens the Tkinter kit generator [GUI](GFF-File-Format#gui-graphical-user-interface) for interactive use. `uvx --refresh pykotor gui-convert --input <gui_or_folder> --output <dir> --resolution ALL` runs headless for [GUI](GFF-File-Format#gui-graphical-user-interface) resizing; omitting args opens the converter [GUI](GFF-File-Format#gui-graphical-user-interface). Developers: `uv run --directory Libraries/PyKotor/src --module pykotor` for local source. (Implementations: `kit_generator.py` wraps `Libraries/PyKotor/src/pykotor/tools/kit.py`; `Libraries/PyKotor/src/pykotor/cli/gui_converter.py` delegates to `pykotor.resource.formats.gff`.)
- **[HoloPatcher.NET](https://github.com/th3w1zard1/HoloPatcher.NET)** - .NET reimplementation of TSLPatcher
- **[Kotor-Patch-Manager](https://github.com/LaneDibello/Kotor-Patch-Manager)** - Alternative mod manager ([Mirror: th3w1zard1/Kotor-Patch-Manager](https://github.com/th3w1zard1/Kotor-Patch-Manager))
- **[ModSync](https://github.com/th3w1zard1/KotORModSync)** - Mod synchronization and installation
- **[StarForge](https://github.com/th3w1zard1/StarForge)** - Module editor and modding toolkit
- **[KotorModTools](https://github.com/Box65535/KotorModTools)** - Collection of modding utilities ([Mirror: th3w1zard1/KotorModTools](https://github.com/th3w1zard1/KotorModTools))

### Save Editors

Tools for editing KotOR save games:

- **[sotor](https://github.com/StarfishXeno/sotor)** - Terminal-based save editor ([Mirror: th3w1zard1/sotor](https://github.com/th3w1zard1/sotor))
- **[KSELinux](https://github.com/Bolche/KSELinux)** - KotOR Save Editor for Linux ([Mirror: th3w1zard1/KSELinux](https://github.com/th3w1zard1/KSELinux))
- **[KotOR-Save-Editor](https://github.com/Fair-Strides/KotOR-Save-Editor)** - [GUI](GFF-File-Format#gui-graphical-user-interface) save editor ([Mirror: th3w1zard1/KotOR-Save-Editor](https://github.com/th3w1zard1/KotOR-Save-Editor))
- **[kotor-savegame-editor](https://github.com/nadrino/kotor-savegame-editor)** - Web-based save editor ([Mirror: th3w1zard1/kotor-savegame-editor](https://github.com/th3w1zard1/kotor-savegame-editor))

### Audio Tools

Tools for working with KotOR audio:

- **[SithCodec](https://github.com/BBBrassil/SithCodec)** - KotOR audio codec implementation ([Mirror: th3w1zard1/SithCodec](https://github.com/th3w1zard1/SithCodec))
- **[SWKotOR-Audio-Encoder](https://github.com/LoranRendel/SWKotOR-Audio-Encoder)** - Audio encoding tool for KotOR ([Mirror: th3w1zard1/SWKotOR-Audio-Encoder](https://github.com/th3w1zard1/SWKotOR-Audio-Encoder))

### Community Resources

Guides, patches, and community-maintained resources:

- **[K1_Community_Patch](https://github.com/KOTORCommunityPatches/K1_Community_Patch)** - Community bug fix patch for KotOR 1 ([Mirror: th3w1zard1/K1_Community_Patch](https://github.com/th3w1zard1/K1_Community_Patch))
- **[TSL_Community_Patch](https://github.com/KOTORCommunityPatches/TSL_Community_Patch)** - Community bug fix patch for KotOR 2 ([Mirror: th3w1zard1/TSL_Community_Patch](https://github.com/th3w1zard1/TSL_Community_Patch))
- **[KOTOR-utils](https://github.com/JCarter426/KOTOR-utils)** - JCarter426's utility scripts and tools ([Mirror: th3w1zard1/KOTOR-utils](https://github.com/th3w1zard1/KOTOR-utils))
- **[KotOR-Bioware-Libs](https://github.com/Fair-Strides/KotOR-Bioware-Libs)** - BioWare library references ([Mirror: th3w1zard1/KotOR-Bioware-Libs](https://github.com/th3w1zard1/KotOR-Bioware-Libs))
- **[kotor_combat_faq](https://github.com/statsjedi/kotor_combat_faq)** - Combat mechanics documentation ([Mirror: th3w1zard1/kotor_combat_faq](https://github.com/th3w1zard1/kotor_combat_faq))
- **[ds-kotor-modding-wiki](https://github.com/DeadlyStream/ds-kotor-modding-wiki)** - DeadlyStream modding wiki container ([Mirror: th3w1zard1/ds-kotor-modding-wiki](https://github.com/th3w1zard1/ds-kotor-modding-wiki))

### Community sources and archives

For **complete, comprehensive, and accurate** wiki coverage, the following community sites and archives hold historical and ongoing KotOR/TSL modding knowledge. Use them to cross-check format behavior, tool usage, and engine quirks.

| Source | Description | Use for |
|--------|-------------|--------|
| **[DeadlyStream](https://deadlystream.com)** | Primary KotOR modding hub: mod releases, tutorials, Script Shack, tool discussions. | File format questions, TSLPatcher/HoloPatcher usage, nwscript.nss and animation references, override practices. |
| **[LucasForums Container](https://lucasforumscontainer.com)** | Archive of original LucasForums (StarWarsKnights.com) threads, reconstructed from the Wayback Machine. | TSLPatcher history and changelogs, Stoffe’s posts, format and tool discussions (2004–2007). |
| **[LucasForums Archive](https://lucasforumsarchive.com)** | Alternative archive project (Editing/Modding, Holowan Laboratories, tutorials). | TSLPatcher thread, KotOR tool docs, mod-finding threads. |
| **Holowan Laboratories / Mixmojo** | Historical KotOR modding forums (MixNMojo/Mixmojo). | Early format and tool discussions; some content may be in archives or mirrors. |
| **Reddit** (e.g. r/kotor) | General KotOR community. | Mod installation, troubleshooting, links to DeadlyStream and wiki. |

**Further reading (community):**

- [DeadlyStream: Help setting up TSLPatcher](https://deadlystream.com/topic/5785-help-setting-up-the-tslpatcher-for-mods/) — TSLPatcher setup
- [DeadlyStream: TSL Patcher, TLKEd, and accessories](https://deadlystream.com/files/file/1039-tsl-patcher-tlked-and-accessories/) — Modding tools
- [DeadlyStream: Modding tools category](https://deadlystream.com/files/category/17-modding-tools/) — Tool releases
- [LucasForums Archive: TSLPatcher v1.2.10b1](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer/) — Original TSLPatcher thread (see also [TSLPatcher Thread Complete](TSLPatcher_Thread_Complete) in this wiki)
- [LucasForums Archive: Editing / Modding](https://lucasforumsarchive.com/forum/521) — Holowan Laboratories and tutorials

**How to use these sources:**

- **DeadlyStream:** Search the forums for specific topics (e.g. "override folder", "TSLPatcher 2DA merge", "GFF struct", "nwscript"). The Script Shack and modding tools sections contain tutorials and tool releases. When the wiki documents a format or tool, DeadlyStream threads often provide real-world modder reports (e.g. which 2DA columns are safe to add, TSLPatcher setup gotchas). Cite threads in "See also" or "Further reading" when they are the best source for a given detail.
- **LucasForums Container / LucasForums Archive:** Use for historical and authoritative context. The original TSLPatcher thread (Stoffe, etc.), KotOR Tool discussions, and early GFF/2DA explanations live in these archives. Search by keyword (e.g. "2da", "GFF", "TSLPatcher") in the Editing/Modding or Holowan Laboratories sections. Content may be fragmented across Wayback reconstructions; when a thread is cited, prefer stable archive URLs.
- **Holowan / Mixmojo:** Early KotOR modding community; some content is preserved in archives or linked from LucasForums. Use for very old format or tool history when other sources do not cover it.
- **Reddit (r/kotor):** Useful for installation help, troubleshooting, and links to DeadlyStream or this wiki. For format or engine-level accuracy, prefer this wiki and the format pages; for "how do I install X" or "why does my mod conflict with Y", community posts can complement the docs.

This wiki aims to consolidate and cite that knowledge where relevant. When adding or refining format or tool pages, prefer linking to authoritative specs (e.g. [KEY-File-Format](KEY-File-Format), [GFF-File-Format](GFF-File-Format), official BioWare Aurora docs) and to PyKotor/vendor implementation paths; for community consensus or historical context, link to DeadlyStream threads or LucasForums archive threads where appropriate.

### External Documentation

Reference documentation from related projects (external sources):

- **[xoreos-docs](https://github.com/xoreos/xoreos-docs)** - Aurora engine format documentation repository containing file format specifications for reverse-engineering BioWare's Aurora engine games ([Mirror: th3w1zard1/xoreos-docs](https://github.com/th3w1zard1/xoreos-docs)). Part of the [xoreos project](https://xoreos.org/). The repository includes:
  - **Official BioWare specifications** (`specs/bioware/`): Official Aurora Engine file format PDFs from the now-defunct nwn.bioware.com developer site. These documents are authoritative references for formats used across Aurora engine games including KotOR.
  - **Torlack's reverse-engineered specs** (`specs/torlack/`): Tim Smith (Torlack)'s reverse-engineered format documentation from his now-defunct website (torlock.com). These include detailed field-by-field breakdowns for formats like BIF, KEY, ERF (MOD), GFF (ITP), NCS, and binary MDL files.
  - **KotOR-specific documentation** (`specs/kotor_mdl.html`): Partial KotOR model format specifications with detailed field descriptions.
  - **Binary templates** (`templates/`): 010 Editor binary template files for analyzing binary file structures
  
  **Note:** Much of the KotOR-relevant content from xoreos-docs has been comprehensively integrated into this wiki. See individual format documentation pages for specific source references.
- **[nwn-docs](https://github.com/kucik/nwn-docs)** - Neverwinter Nights documentation (shares Aurora formats)
- **[bioware-kaitai-formats](https://github.com/OldRepublicDevs/bioware-kaitai-formats)** - Kaitai Struct format specifications for GFF, 2DA, BIF, ERF, TLK, and other BioWare/KotOR formats; useful for parser generation and cross-tool validation.

### See also

- [KEY-File-Format](KEY-File-Format) — Resource resolution; [GFF-File-Format](GFF-File-Format), [2DA-File-Format](2DA-File-Format) — Core formats
- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) — Mod installation; [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) — Mod development
- [Wiki-Conventions](Wiki-Conventions) — Wiki structure and style
