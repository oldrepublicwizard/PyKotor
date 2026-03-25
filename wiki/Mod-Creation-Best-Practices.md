# Mod Creation Best Practices

## Philosophy: a contributable toolchain, not a tool monoculture

KotOR modding has historically been **fragmented**: different tools, version quirks, and oral tradition. [PyKotor](https://github.com/OldRepublicDevs/PyKotor) exists so formats, patchers, and editors can be **improved in the open** and documented here in one place. That does **not** mean you must stop using KotOR Tool, K-GFF, or any workflow that already ships your mod—use what works, and use **installers** (TSLPatcher INI) when you need merges instead of blind overwrites. See also the toolchain overview on [Home](Home#documentation).

This page provides common workaround strategies and community-backed guidance for KotOR/TSL mod creation. For tool syntax and installation, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) and [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). The practices below are drawn from long-standing community consensus on [DeadlyStream](https://deadlystream.com), [LucasForums archives](https://lucasforumsarchive.com), and tool documentation.

**Historical context (LucasForums Archive):** The original [TSLPatcher v1.2.10b1 release thread](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer) documents the Perl-era installer design; use **HoloPatcher** and this wiki’s TSLPatcher-syntax pages for current semantics. For early standalone GFF editing culture, see [K-GFF v1.3.0](https://www.lucasforumsarchive.com/thread/149407) (pair with [GFF-File-Format](GFF-File-Format) historical tooling paragraph and [Holocron Toolset](Holocron-Toolset-Getting-Started) today).

## File priority and where to put your files

The game resolves resources in a fixed order. Understanding this order is essential for knowing where to place your mod's files and how conflicts arise.

**Resolution order (summary):** The engine checks (1) the **override folder** (`override/`), (2) currently loaded **MOD/ERF** files (e.g. modules in the Modules folder), (3) the current **save game** when in-game, then (4) **KEY/BIF** (vanilla game data). So override and MOD content take precedence over vanilla BIFs. See [Concepts](Concepts#resource-resolution-order) for the full sequence and how the resource manager satisfies requests; [KEY-File-Format](KEY-File-Format) documents the KEY binary layout.

**Where to put files:**

- **Override folder:** Use for most standalone mod content: textures, models, scripts, 2DA edits, dialog TLK changes, and GFF-based resources (creatures, items, placeables) that are meant to replace or add to the base game globally. Files in `override/` are loaded for every module and save. If your mod only adds or replaces a few files and does not need an installer, placing files directly in `override/` is standard.
- **MOD files (ERF):** Use for module-specific content: area GFFs (ARE, GIT, etc.), module-specific 2DAs or scripts, and anything that should load only when that module is played. TSLPatcher and HoloPatcher can write into both override and MOD; when building a MOD, your installer typically packs resources into a `.mod` file and optionally copies shared files (e.g. global 2DAs) to override. Putting everything in override can work but increases the chance of overwriting or being overwritten by other mods; merging 2DAs via TSLPatcher reduces conflicts.
- **Folder priorities (community convention):** Community guidance (e.g. DeadlyStream: "Folder priorities: Where to put your mod's files") recommends: unless files differ per module, place them in override. Use MODs when content is module-specific or when you need TSLPatcher's 2DA/TLK/GFF merging. Point TSLPatcher at the **game root directory**, not directly at the override folder, so the patcher can resolve paths correctly.

**Special cases:** Some data (e.g. certain creature or trigger state) is stored in save games. Changing those after a save is loaded may require new playthroughs or script-based workarounds. See "Removing GFF structs" below for script-based removal of instances when patchers cannot delete structs.

## TSLPatcher setup and 2DA/TLK merging

**TSLPatcher setup:** Point TSLPatcher at your **main game installation directory** (the folder that contains `swkotor.exe` or `swkotor2.exe` and the `override` folder), not at the override folder itself. If you use Steam Workshop content (e.g. TSLRCM), point the patcher at that workshop folder when installing mods that need to merge with Workshop content. This ensures the patcher finds the correct 2DA, TLK, and GFF files and can merge rather than overwrite when configured to do so.

**Merging 2DA files:** When multiple mods change the same 2DA (e.g. `spells.2da`, `appearance.2da`), raw overwrites would make only one mod's changes take effect. TSLPatcher can **merge** 2DA changes: it adds or updates rows based on your 2DAList instructions so that several mods' additions coexist. Configure your mod's 2DAList (and optionally TLKList for string references) so that your rows are appended or matched by key column; the patcher then merges instead of replacing the whole file. See [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax) for exact syntax.

**Community (HoloPatcher vs TSLPatcher merges):** [Deadly Stream -- TOOL: HoloPatcher](https://deadlystream.com/topic/9807-toolholopatcher/) (release discussion) complements the wiki's [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers); treat threads as **workflow context**, not a substitute for `[2DAList]` syntax on this wiki.

**Merging TLK (dialog.tlk):** Similarly, TLKList allows adding or changing string entries without wiping the rest of the TLK. Use TLKList so that your mod's new StrRefs are appended and existing entries are updated only where intended. See [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax).

**GFF merging:** TSLPatcher GFFList can add or edit structs and fields in GFF files (e.g. adding a new item to a 2DA or editing a creature template). It cannot remove structs; for that, use a script-based workaround (see below) or a tool that supports deletion.

## Community tools and format editing (reference)

Many modders use GUI tools to edit GFF and 2DA files when building mods manually or to inspect game data. Community knowledge (including LucasForums archives) frequently references:

- **KotOR Tool:** Provides a graphical interface for editing GFF and 2DA files, reducing the need to hand-edit binary formats. It can open BIF/ERF and edit creatures, items, 2DAs, and other resources.
- **K-GFF:** A standalone GFF editor with search; useful for inspecting or editing GFF structure when you need field-level control.
- **GFF2XML / XML2GFF (tk102):** Command-line utilities to convert GFF to XML and back, enabling diff-friendly and scriptable edits.
- **2DA editing:** Historically, Werf's 2DA editor was used to convert between compiled (v2.b) and text (v2.0) 2DA formats. Modern tools (e.g. KotOR Tool, Holocron Toolset) often handle 2DA internally. When merging 2DAs by hand, copy unique rows from one file into the other and update any references in your mod's GFF/scripts that point to row indices.

When combining multiple mods that touch the same 2DA, manual merging involves copying unique lines from one 2DA into the other and updating references in affected files; using TSLPatcher 2DAList is preferred when possible for repeatable installs.

## Common Workaround Strategies

A common problem you may encounter when creating a mod, is the inability to remove a [GFF](GFF-File-Format) struct. Let's say you want to remove a [GIT](GFF-File-Format#git-game-instance-template) instance to be compatible with another mod. Both HoloPatcher and TSLPatcher do not support this. However, you can work around it.

## Removing [GFF](GFF-File-Format) structs when patchers cannot

Neither HoloPatcher nor TSLPatcher supports **removing** a GFF struct (e.g. deleting a [GIT](GFF-File-Format#git-game-instance-template) instance) from an ARE or other GFF. If you need to remove placeables, creatures, or other instances for compatibility or design reasons, you must do it at runtime with a script: locate the objects and destroy them, and run that script once (e.g. gated by a local variable) so it does not run every frame or conflict with other mods.

**Example scenario:** Remove all (20+) box placeables, remove 2 of 4 droids, and move the remaining 2 droids to new positions. I tried several possible solutions, including `GetFirstObjectInShape / GetNextObjectInShape` and `GetNearestObjectToLocation` functions. I think these functions worked well with a small number of objects, but at times left a few of the 20+ boxes placed on the level. So I switched to `GetObjectByTag / DestroyObject` functions.

The summary:

1.Write code in a script that will search for and delete the necessary objects in the module.

2.Gate the 'delete script' with a local boolean set on the area/some object to make sure it only runs once.

3.Attach the script to an object, dialog, trigger or onEnter script of the module (not recommended, bad for compatibility with other mods).

It was easy for me to remove 4 droids instead of 2, and then create 2 in new positions. But if one needs to, for example, remove 5 out of 30 instances of an object in a module, then one should probably use the `GetFirstObjectInShape/GetNextObjectInShape` functions.

Example of code:

```nwscript
void main(){
    if(GetLocalNumber( OBJECT_SELF, 32 ) != 150){
      DestroyObjectsByTag("objectTag");
      //DestroyPlaceablesAndCreaturesInArea(oLoc1, SHAPE_CUBE, 36.0f);
      SetLocalNumber(OBJECT_SELF, 32, 150);
    }
}

void DestroyObjectsByTag(string tag){
  int i = 0;
  object oPlc = GetObjectByTag(tag);
  while(GetIsObjectValid(oPlc)){
    DestroyObject(oPlc);
    i++;
    oPlc = GetObjectByTag(tag, i);
  }

void DestroyPlaceablesAndCreaturesInArea(location oLoc1, int nShape, float areaSize){
  object oPlc = GetFirstObjectInShape(nShape, areaSize, oLoc1, 0, OBJECT_TYPE_CREATURE | OBJECT_TYPE_PLACEABLE);
  while (GetIsObjectValid(oPlc))
  {
    DestroyObject(oPlc);
    oPlc = GetNextObjectInShape(nShape, areaSize, oLoc1, 0, OBJECT_TYPE_CREATURE | OBJECT_TYPE_PLACEABLE);
  }
}
```

## Testing and compatibility

- **Textures (TGA vs TPC, install order):** Players often debate override order for texture stacks—see [Deadly Stream — mod installation order and TGA vs TPC](https://deadlystream.com/topic/11056-mod-installation-order-and-tga-vs-tpc-files/) for **workflow context**; format SSOT remains [TPC-File-Format](TPC-File-Format) and [Concepts — resource resolution](Concepts#resource-resolution-order).
- **Install order:** Many mods depend on load order (override and MOD order). Document recommended order in your mod’s readme; when using TSLPatcher/HoloPatcher, merging 2DA/TLK reduces order sensitivity for those files.
- **Clean install:** Test on a clean game install or a known-good backup so conflicts are attributable to your mod or to a specific combination.
- **Reversion:** Use the patcher’s backup/restore (e.g. HoloPatcher “Uninstall Mod/Restore Backup”) before reinstalling or switching options; installing twice without reverting can duplicate 2DA rows or TLK entries and cause crashes. See [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher).
- **iOS/mobile:** For mobile (e.g. iOS), file names must be lowercase; use HoloPatcher’s “Fix iOS Case Sensitivity” when targeting mobile. See [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher#installing-mods-on-ios-devices).

## Storing 2DAMEMORY without duplicating/creating a row

The ExclusiveColumn field is perfect for this situation. Here's an example where we know the 'label' and we want to simply store the RowIndex.

```ini
[genericdoors.2da]
CopyRow0=copy_row_0
CopyRow1=copy_row_1
CopyRow2=copy_row_2
CopyRow3=copy_row_3
CopyRow4=copy_row_4

[copy_row_0]
ExclusiveColumn=label
LabelIndex=Hammerhead2
label=Hammerhead2
2DAMEMORY114=RowIndex
[copy_row_1]
ExclusiveColumn=label
LabelIndex=Hammerhead3
label=Hammerhead3
2DAMEMORY115=RowIndex
[copy_row_2]
ExclusiveColumn=label
LabelIndex=SleheyronDoor1
label=SleheyronDoor1
2DAMEMORY116=RowIndex
[copy_row_3]
ExclusiveColumn=label
LabelIndex=SleheyronDoor2
label=SleheyronDoor2
2DAMEMORY117=RowIndex
[copy_row_4]
ExclusiveColumn=label
LabelIndex=YavinHgrDoor1
label=YavinHgrDoor1
2DAMEMORY118=RowIndex
```

### See also

- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) -- Mod tooling and workflow
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- TSLPatcher installation and usage
- [GFF File Format](GFF-File-Format) -- GFF structure; [GIT](GFF-File-Format#git-game-instance-template), [UTC](GFF-File-Format#utc-creature), [UTP](GFF-UTP)
- [NSS File Format](NSS-File-Format) -- Scripting; [NCS](NCS-File-Format) bytecode
- [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher) -- End-user mod installation
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums archives for tutorials and community knowledge
- [Deadly Stream — HoloPatcher](https://deadlystream.com/files/file/2243-holopatcher/) -- User-facing tool hub and install discussions (complement [Installing Mods with HoloPatcher](Installing-Mods-with-HoloPatcher))
- [LucasForums Archive — TSLPatcher v1.2.10b1 thread](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer/) -- Historical installer context (see also [TSLPatcher Thread Complete](TSLPatcher_Thread_Complete))
- [Deadly Stream -- TOOL: HoloPatcher](https://deadlystream.com/topic/9807-toolholopatcher/) -- Release thread (2DA merge / installer workflow context)
- [Concepts](Concepts#resource-resolution-order) -- Resource resolution order; [KEY-File-Format](KEY-File-Format) -- KEY/BIF index format
- [TSLPatcher 2DAList Syntax](TSLPatcher-2DAList-Syntax), [TSLPatcher TLKList Syntax](TSLPatcher-TLKList-Syntax), [TSLPatcher GFFList Syntax](TSLPatcher-GFFList-Syntax) -- Merging and patching
