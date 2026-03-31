# TSLPatcher Install and Hack Syntax

TSLPatcher’s `changes.ini` can copy files into the game directory and binary-patch executables alongside the GFF, 2DA, and TLK operations covered on sibling pages. The sections below document the `[InstallList]` and `[HACKList]` directive syntax that HoloPatcher and TSLPatcher both support.

## Contents

- [InstallList Syntax — File Installation](#installlist-syntax)
- [HACKList Syntax — Binary Patching](#hacklist-syntax)

---

<a id="installlist-syntax"></a>

# TSLPatcher InstallList Syntax Documentation

This guide explains how to install files using TSLPatcher syntax. For general TSLPatcher information, see [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). For HoloPatcher-specific information, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

**Implementation:** [`Libraries/PyKotor/src/pykotor/tslpatcher/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/tslpatcher/)

**Cross-reference:**

- **th3w1zard1/TSLPatcher** — original Perl TSLPatcher (stoffe lineage)

  - Canonical (th3w1zard1/TSLPatcher): <https://github.com/th3w1zard1/TSLPatcher/tree/ad04700a47086c25e1c6ef4b4961f76dfa8cc6a5>
- [`Tools/HolocronToolset/src/toolset/gui/dialogs/install_mod.py`](https://github.com/OldRepublicDevs/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/dialogs/install_mod.py) - HoloPatcher [GUI](GFF-File-Format#gui-graphical-user-interface) implementation
- [`KotOR.js/src/manager/`](https://github.com/KobaltBlu/KotOR.js/tree/master/src/manager) - TypeScript mod management (different approach)

### See also

- [TSLPatcher 2DAList Syntax](TSLPatcher-Data-Syntax#2dalist-syntax) - Patching [2DA files](2DA-File-Format)
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) - Patching [GFF files](GFF-File-Format)
- [TSLPatcher TLKList Syntax](TSLPatcher-Data-Syntax#tlklist-syntax) - Patching [TLK files](Audio-and-Localization-Formats#tlk)
- [TSLPatcher SSFList Syntax](TSLPatcher-GFF-Syntax#ssflist-syntax) - Patching [SSF files](Audio-and-Localization-Formats#ssf)
- [TSLPatcher HACKList Syntax](TSLPatcher-Install-and-Hack-Syntax#hacklist-syntax) - Binary patching [NCS files](NCS-File-Format)
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) - HoloPatcher extensions

## Overview

The `[InstallList]` section in TSLPatcher's changes.ini file enables you to copy files from your mod's `tslpatchdata` folder to their proper location in the game installation. This includes installing files to folders (such as `Override`, `Modules`, `StreamVoice`, etc.) or directly into module capsules ([MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim)). Unlike other patch lists, InstallList is designed for copying files that haven't been modified by other sections.

**Important:** Do **not** add any files that have been modified by any of the other sections ([GFFList](TSLPatcher-GFF-Syntax#gfflist-syntax), CompileList, [2DAList](TSLPatcher-Data-Syntax#2dalist-syntax), etc.) to the InstallList, or the modified files might be overwritten! The other sections already handle saving files to their proper locations. The only exception to this is [ERF files](Container-Formats#erf) which have had files added to them by those sections. They must still be added to the InstallList to be put in their proper places.

## Table of Contents

- [Basic Structure](#basic-structure)
- [Processing Order](#processing-order)
- [Folder-Level Configuration](#folder-level-configuration)
- [File-Level Configuration](#file-level-configuration)
- [File Replacement Behavior](#file-replacement-behavior)
- [Installing to Folders](#installing-to-folders)
- [Installing to Containers](#installing-to-containers)
- [Renaming Files](#renaming-files)
- [Source Folder Configuration](#source-folder-configuration)
- [Override Type Handling](#override-type-handling)
- [Examples](#examples)
- [Special Cases and Edge Cases](#special-cases-and-edge-cases)
- [Troubleshooting](#troubleshooting)

## Basic structure

The InstallList uses a two-level hierarchical structure:

```ini
[InstallList]
Folder0=Override
Folder1=Modules
Folder2=StreamVoice\AVO\_HuttHap

[Override]
File0=my_texture.tpc
File1=my_script.ncs
Replace0=existing_file.tpc

[Modules]
!SourceFolder=modules
File0=new_module.mod

[StreamVoice\AVO\_HuttHap]
File0=sound1.wav
File1=sound2.wav
```

### structure Explanation

1. **`[InstallList]` section**: Contains keys that map to folder destination names. Each key (like `Folder0`, `Folder1`, etc.) should reference a section with the same name as the value (the destination folder).

2. **Folder sections** (e.g., `[Override]`, `[Modules]`): Contain the list of files to install to that folder, along with optional folder-level configuration.

3. **file sections** (optional): Individual files can have their own sections for per-file configuration options.

## Processing Order

In **HoloPatcher**, the InstallList runs **first** in the patch execution order:

1. **[InstallList]** - files are installed first
2. **[TLKList]** - [TLK](Audio-and-Localization-Formats#tlk) modifications
3. **[2DAList]** - [2DA file](2DA-File-Format) modifications
4. **[GFFList]** - [GFF file](GFF-File-Format) modifications
5. **[CompileList]** - Script compilation
6. **[HACKList]** - Binary hacking
7. **[SSFList]** - Sound set modifications

**Note:** In original TSLPatcher, InstallList executes **after** TLKList, but HoloPatcher changed this order to allow installing a whole [dialog.tlk](Audio-and-Localization-Formats#tlk) file before [TLK](Audio-and-Localization-Formats#tlk) modifications are applied. This priority change should not affect the output of mods.

## Folder-Level Configuration

Each folder section (e.g., `[Override]`) supports the following configuration keys:

| [KEY](Container-Formats#key) | type | Default | Description |
|-----|------|---------|-------------|
| `!SourceFolder` | string | `.` (tslpatchdata folder) | Relative path from `mod_path` (typically the `tslpatchdata` folder, the parent directory of `changes.ini` or `namespaces.ini`) where files should be sourced from. The default value `.` refers to the `tslpatchdata` folder itself, not its parent directory. Path resolution: `mod_path / !SourceFolder / filename`. **HoloPatcher extension** - allows subfolder organization within tslpatchdata. |

### Folder Section file List Keys

The folder section contains the list of files to install. Each file entry uses one of two syntaxes:

| [KEY](Container-Formats#key) format | Replace Behavior | Description |
|------------|-----------------|-------------|
| `File#=filename.ext` | No replacement | Install the file only if it doesn't already exist at the destination. If the file exists, it will be skipped (warning logged). |
| `Replace#=filename.ext` | Replacement enabled | Install the file and overwrite any existing file at the destination. |

**Syntax Notes:**

- `#` is a sequential number starting from 0 (File0, File1, File2, ..., Replace0, Replace1, etc.)
- Numbers can be sequential, but gaps are allowed (File0, File2, File5 is valid)
- Case-insensitive matching is used for the prefix (file, replace, file, Replace all work)
- The filename can include subdirectories if using `!SourceFolder`

**Examples:**

```ini
[Override]
File0=texture1.tpc
File1=texture2.tpc
Replace0=existing.tpc
Replace1=another_existing.tpc
File2=subfolder\texture3.tpc
```

## file-Level Configuration

Each file can optionally have its own section (e.g., `[my_texture.tpc]`) for per-file configuration:

| [KEY](Container-Formats#key) | type | Default | Description |
|-----|------|---------|-------------|
| `!SourceFile` | string | Same as filename in file#/Replace# entry | Alternative source filename to load from tslpatchdata. The file will be installed with the name specified in the file#/Replace# entry (or `!SaveAs`/`!Filename` if specified). |
| `!SaveAs` | string | Same as `!SourceFile` | The final filename to save the file as at the destination. Allows renaming during installation. |
| `!Filename` | string | Same as `!SaveAs` | Alias for `!SaveAs`. Both keys are equivalent. |
| `!Destination` | string | Inherited from folder section name | Override the destination folder for this specific file. Can specify a different folder or container path. |
| `!ReplaceFile` | 0/1 | Determined by file#/Replace# prefix | Whether to replace existing files. Takes priority over the file#/Replace# prefix syntax. `1` = replace, `0` = don't replace. |
| `!SourceFolder` | string | Inherited from folder section `!SourceFolder` | Override the source folder for this specific file. Relative path within tslpatchdata. |
| `!OverrideType` | `ignore`/`warn`/`rename` | `warn` (HoloPatcher) / `ignore` (TSLPatcher) | How to handle conflicts when installing to containers. See [Override Type Handling](#override-type-handling) section. |

### Example with file-Level Configuration

```ini
[InstallList]
Folder0=Override

[Override]
File0=source_texture.tpc
File1=renamed_script.ncs

[source_texture.tpc]
!SourceFile=original_name.tpc
!SaveAs=final_texture.tpc
!Destination=textures

[renamed_script.ncs]
!Filename=custom_name.ncs
!ReplaceFile=1
```

## file Replacement Behavior

InstallList has special behavior regarding file replacement that differs from other patch lists:

### Skip If Not Replace

InstallList (and CompileList) use `skip_if_not_replace=True`, which means:

- If `!ReplaceFile=0` (or using `File#=` syntax) **and** the file already exists at the destination:
  - The file will be **skipped** (not installed)
  - A note is logged: `'filename.ext' already exists in the 'destination' folder. Skipping file...`
  - No error is raised - this is expected behavior

- If `!ReplaceFile=1` (or using `Replace#=` syntax) **and** the file already exists:
  - The file will be **replaced** (overwritten)
  - A note is logged: `Copying 'filename.ext' and replacing existing file in the 'destination' folder`

- If the file does **not** exist:
  - The file will be installed normally
  - A note is logged: `Copying 'filename.ext' and saving to the 'destination' folder`

### Replacement Priority

1. **`!ReplaceFile`** key (if present) takes **highest priority**
2. **`Replace#=`** prefix syntax (if `!ReplaceFile` not specified)
3. **`File#=`** prefix syntax (default, no replacement)

**Example:**

```ini
[Override]
Replace0=example.tpc

[example.tpc]
!ReplaceFile=0
```

In this case, even though `Replace0=` was used, `!ReplaceFile=0` takes priority, so the file will NOT replace existing files.

## Installing to Folders

### Standard Game Folders

The most common use case is installing files to standard game folders:

```ini
[InstallList]
Folder0=Override
Folder1=Modules
Folder2=StreamVoice
Folder3=StreamMusic
Folder4=StreamWaves

[Override]
File0=my_texture.tpc
File1=my_item.uti

[Modules]
File0=custom_module.mod

[StreamVoice]
File0=voice_line.wav

[StreamMusic]
File0=background_music.mp3

[StreamWaves]
File0=sound_effect.wav
```

### Subdirectories

You can install files into subdirectories by specifying the relative path with backslashes:

```ini
[InstallList]
Folder0=StreamVoice\AVO\_HuttHap

[StreamVoice\AVO\_HuttHap]
File0=conversation1.wav
File1=conversation2.wav
```

**Important Notes:**

- Use **backslashes** (`\`) for path separators (TSLPatcher convention)
- HoloPatcher/PyKotor will normalize both forward slashes (`/`) and backslashes (`\`)
- If the specified folder path does not exist, it will be **automatically created**
- Folder creation happens recursively (parent folders are created as needed)

### Game Root Folder

To install files directly into the game root folder, use `.\` as the folder name:

```ini
[InstallList]
Folder0=.\

[.\]
File0=readme.txt
File1=config.ini
```

**Note:** In logs, `.\` is reported as the "Game" folder for clarity.

### Default Destination

You can set a default destination for all files in InstallList using `!DefaultDestination`:

```ini
[InstallList]
!DefaultDestination=Override
Folder0=Override
Folder1=Modules

[Override]
File0=file1.tpc

[Modules]
File0=file2.mod
```

**Note:** `!DefaultDestination` is highly undocumented in TSLPatcher. In PyKotor/HoloPatcher, it is believed to take priority over folder section destinations, except when `!Destination` is explicitly set in a file section.

## Installing to Containers

InstallList supports installing files directly into [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim) container files. This is done by specifying the container file path (relative to the game folder) as the destination.

### Container file Syntax

```ini
[InstallList]
Folder0=Modules\901myn.mod
Folder1=Modules\custom_module.rim

[Modules\901myn.mod]
File0=new_resource.uti
File1=new_texture.tpc
Replace0=existing_resource.uti

[Modules\custom_module.rim]
File0=another_resource.2da
```

### Container Behavior

- If the container **does not exist** at the specified path:
  - An error is logged: `The capsule 'Modules\901myn.mod' did not exist when attempting to copy 'filename.ext'. Skipping file...`
  - The patch is skipped (no error is raised, execution continues)

- If the container **exists**:
  - The file is added to the container
  - If a resource with the same name already exists in the container:
    - If `!ReplaceFile=1` or `Replace#=`: The existing resource is overwritten
    - If `!ReplaceFile=0` or `File#=`: The file is skipped (see [File Replacement Behavior](#file-replacement-behavior))

- **Container types Supported:**
  - `.mod` (MOD/[ERF](Container-Formats#erf) format)
  - `.erf` ([ERF](Container-Formats#erf) format)
  - `.rim` ([RIM](Container-Formats#rim) format)
  - `.sav` (Save game [ERF](Container-Formats#erf) format)

### Installing Modified Containers

If you've modified an container using GFFList or CompileList (e.g., added resources to it), you **must** include that container in InstallList to save it to its proper location:

```ini
[GFFList]
File0=Modules\901myn.mod

[Modules\901myn.mod]
; ... GFF modifications ...

[InstallList]
Folder0=Modules

[Modules]
Replace0=901myn.mod  ; Must include to save the modified container
```

## Renaming files

You can rename files during installation using `!SaveAs` or `!Filename`:

```ini
[InstallList]
Folder0=Override

[Override]
File0=source_name.tpc

[source_name.tpc]
!SourceFile=original_filename.tpc
!SaveAs=final_filename.tpc
```

This will:

1. Load `original_filename.tpc` from tslpatchdata
2. Install it as `final_filename.tpc` to the Override folder

**Notes:**

- `!SaveAs` and `!Filename` are equivalent - use either one
- If `!SourceFile` is not specified, the filename from the file#/Replace# entry is used as the source
- The source file must exist in the tslpatchdata folder (or `!SourceFolder` if specified)

## Source Folder Configuration

### Folder-Level Source Folder

You can specify a source folder for all files in a folder section:

```ini
[InstallList]
Folder0=Override

[Override]
!SourceFolder=textures
File0=texture1.tpc
File1=texture2.tpc
```

This will look for files in `tslpatchdata\textures\` instead of `tslpatchdata\`.

### file-Level Source Folder

You can override the source folder for individual files:

```ini
[InstallList]
Folder0=Override

[Override]
!SourceFolder=default_folder
File0=file1.tpc
File1=file2.tpc

[file1.tpc]
!SourceFolder=custom_folder
```

In this example:

- `file1.tpc` is loaded from `tslpatchdata\custom_folder\`
- `file2.tpc` is loaded from `tslpatchdata\default_folder\`

### Source Folder Notes

- `!SourceFolder` is a **HoloPatcher extension** - original TSLPatcher may not support this feature
- Paths are relative to the `tslpatchdata` folder
- Use `.` (period) to reference the root tslpatchdata folder explicitly
- Supports subdirectory paths: `!SourceFolder=subfolder\deeper\folder`
- Backslashes and forward slashes are both normalized

## Override type Handling

When installing files to containers ([MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim)), there's a potential conflict: a file might already exist in the Override folder with the same name. The `!OverrideType` setting controls how this conflict is handled:

| value | Behavior | Description |
|-------|----------|-------------|
| `ignore` | No action | Do nothing - don't even check for conflicts. This is the TSLPatcher default. |
| `warn` | Log warning | Check for conflicts and log a warning if found, but continue with installation. This is the HoloPatcher default. |
| `rename` | Rename override file | If a conflicting file exists in Override, rename it with an `old_` prefix (e.g., `old_filename.ext`) and log a warning. |

**Example:**

```ini
[Modules\901myn.mod]
File0=resource.uti
!OverrideType=warn
```

**Why This Matters:**

The game's resource loading system checks folders in this order:

1. Override folder (highest priority)
2. Module containers (.mod files)
3. [RIM](Container-Formats#rim) files (`.rim` / `_s.rim`)
4. Other containers

If a file exists in both Override and an container, the Override version takes precedence. The `!OverrideType` setting helps manage this shadowing behavior.

## Examples

### Example 1: Basic Installation to Override

```ini
[InstallList]
Folder0=Override

[Override]
File0=my_texture.tpc
File1=my_item.uti
File2=my_script.ncs
Replace0=existing_file.tpc
```

### Example 2: Installing to Multiple Folders with Source Folders

```ini
[InstallList]
Folder0=Override
Folder1=StreamVoice\AVO\_HuttHap
Folder2=Modules

[Override]
!SourceFolder=override_files
File0=texture1.tpc
File1=texture2.tpc

[StreamVoice\AVO\_HuttHap]
!SourceFolder=voice_files
File0=conv1.wav
File1=conv2.wav

[Modules]
!SourceFolder=modules
File0=custom.mod
```

### Example 3: Renaming files During Installation

```ini
[InstallList]
Folder0=Override

[Override]
File0=renamed_texture.tpc
File1=renamed_item.uti

[renamed_texture.tpc]
!SourceFile=original_texture.tpc
!SaveAs=final_texture_name.tpc

[renamed_item.uti]
!SourceFile=source_item.uti
!Filename=custom_item_name.uti
```

### Example 4: Installing to Containers

```ini
[InstallList]
Folder0=Modules\901myn.mod
Folder1=Modules\custom.rim

[Modules\901myn.mod]
File0=new_creature.utc
File1=new_dialog.dlg
Replace0=existing_item.uti
!OverrideType=warn

[Modules\custom.rim]
File0=custom_2da.2da
!ReplaceFile=1
```

### Example 5: Complex Example with All Features

```ini
[InstallList]
!DefaultDestination=Override
Folder0=Override
Folder1=Modules
Folder2=Modules\901myn.mod
Folder3=StreamVoice\AVO\_HuttHap

[Override]
!SourceFolder=textures
File0=texture1.tpc
File1=texture2.tpc
Replace0=existing_texture.tpc

[texture1.tpc]
!SourceFile=original_name.tpc
!SaveAs=final_texture.tpc
!Destination=textures
!OverrideType=rename

[Modules]
!SourceFolder=modules
Replace0=modified_module.mod

[Modules\901myn.mod]
File0=new_resource.uti
File1=new_texture.tpc
Replace0=modified_resource.utc
!SourceFolder=container_resources

[new_resource.uti]
!Filename=custom_name.uti
!ReplaceFile=1

[StreamVoice\AVO\_HuttHap]
!SourceFolder=voice
File0=line1.wav
File1=line2.wav
```

## Special Cases and [edge](Level-Layout-Formats#edges-wok-only) Cases

### Empty InstallList

An empty `[InstallList]` section is valid and will be skipped:

```ini
[InstallList]
```

No files will be installed, and a note will be logged: `[InstallList] section missing from ini.` (if the section doesn't exist) or no error if the section exists but is empty.

### Missing Folder Sections

If a folder [KEY](Container-Formats#key) in `[InstallList]` references a section that doesn't exist, a `KeyError` is raised:

```ini
[InstallList]
Folder0=NonExistentFolder
; Error: Section [NonExistentFolder] not found
```

### Missing Source files

If a source file specified in a file#/Replace# entry doesn't exist in tslpatchdata (or the specified `!SourceFolder`), an error is logged:

```
Could not locate resource to copy: 'missing_file.tpc'
```

The patcher will continue with the next file.

### Automatic Folder Creation

Folders are automatically created if they don't exist:

```ini
[InstallList]
Folder0=NewFolder\SubFolder\DeepFolder

[NewFolder\SubFolder\DeepFolder]
File0=file.tpc
```

All parent folders (`NewFolder`, `SubFolder`, `DeepFolder`) will be created automatically.

### Container file Handling

- **Container doesn't exist**: Error logged, patch skipped
- **Container exists but is read-only**: Permission error logged, patch skipped
- **Container exists, file already in container**: See [File Replacement Behavior](#file-replacement-behavior)
- **Container exists, file doesn't exist in container**: file is added normally

### Case Sensitivity

- Folder and file keys are **case-insensitive**: `File0`, `file0`, `FILE0` all work
- `Replace#` prefix detection is **case-insensitive**: `Replace0`, `replace0`, `REPLACE0` all work
- file paths on Windows are case-insensitive, but PyKotor uses `CaseAwarePath` to preserve case when possible

### Path Separators

- TSLPatcher convention: Use backslashes (`\`) for Windows paths
- PyKotor/HoloPatcher: Normalizes both backslashes (`\`) and forward slashes (`/`)
- Container paths: Use backslashes: `Modules\901myn.mod`

### nwscript.nss Automatic Installation

If the mod contains `nwscript.nss` in the tslpatchdata folder and there are scripts to compile (`[CompileList]`), HoloPatcher will automatically append an InstallFile entry to install `nwscript.nss` to the Override folder. This is required for some versions of nwnnsscomp.exe that expect nwscript.nss to be in Override rather than tslpatchdata.

This happens during the `_prepare_compilelist` phase before the main patch loop runs.

## Troubleshooting

### file Not Installing

**Problem:** file listed in InstallList but not being installed.

**Possible Causes:**

1. file already exists and `Replace#=` or `!ReplaceFile=1` not set
   - **Solution:** Check logs for "already exists... Skipping file" message
   - **Fix:** Use `Replace#=` or set `!ReplaceFile=1`

2. Source file doesn't exist in tslpatchdata
   - **Solution:** Check logs for "Could not locate resource" error
   - **Fix:** Ensure file exists in tslpatchdata (or specified `!SourceFolder`)

3. Container doesn't exist
   - **Solution:** Check logs for "capsule did not exist" error
   - **Fix:** Create the container first or ensure the path is correct

4. Permission errors
   - **Solution:** Check logs for permission/access denied errors
   - **Fix:** Run with appropriate permissions, check file/folder permissions

### Wrong Destination

**Problem:** file installing to wrong location.

**Possible Causes:**

1. `!Destination` override in file section
2. `!DefaultDestination` set incorrectly
3. Folder section name typo

**Solution:** Check file section for `!Destination`, verify folder section names match destination paths.

### Container Not Updating

**Problem:** file not appearing in container after installation.

**Possible Causes:**

1. Container doesn't exist (error logged)
2. file already exists and replacement not enabled
3. Container is read-only or locked

**Solution:** Check logs for errors, ensure `Replace#=` or `!ReplaceFile=1` is set, verify container permissions.

### files Being Skipped Unexpectedly

**Problem:** files that should install are being skipped.

**Possible Causes:**

1. `File#=` syntax used with existing files (expected behavior - use `Replace#=`)
2. `!ReplaceFile=0` explicitly set
3. file already exists in container without replacement enabled

**Solution:** Review [File Replacement Behavior](#file-replacement-behavior) section, use `Replace#=` or `!ReplaceFile=1` to enable replacement.

## Reference: Complete Syntax Summary

### Top-Level [InstallList] Section

```ini
[InstallList]
!DefaultDestination=<folder_path>  ; Optional: default destination for all files
Folder#=<destination_path>          ; Required: map to folder section
```

### Folder Section (e.g., [Override])

```ini
[<destination_path>]
!SourceFolder=<relative_path>        ; Optional: source folder within tslpatchdata
File#=<filename.ext>                ; Install file (skip if exists)
Replace#=<filename.ext>             ; Install file (replace if exists)
```

### file Section (e.g., [filename.ext])

```ini
[<filename.ext>]
!SourceFile=<source_filename.ext>  ; Optional: alternative source file
!SaveAs=<final_filename.ext>       ; Optional: rename during installation
!Filename=<final_filename.ext>      ; Optional: alias for !SaveAs
!Destination=<destination_path>     ; Optional: override folder destination
!ReplaceFile=<0|1>                  ; Optional: override replacement behavior
!SourceFolder=<relative_path>      ; Optional: override source folder
!OverrideType=<ignore|warn|rename> ; Optional: conflict resolution mode
```

## Additional Notes

- All paths in TSLPatcher use backslashes (`\`) by convention, but HoloPatcher/PyKotor normalizes both slashes
- Folder paths are created automatically if they don't exist
- Container paths must exist before files can be installed to them
- InstallList runs before other patch lists in HoloPatcher (but after TLKList in original TSLPatcher)
- files are backed up before installation (if they exist)
- Uninstall scripts are generated automatically in the backup folder

### See also

- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) - Original TSLPatcher documentation
- [Explanations on HoloPatcher Internal Logic](HoloPatcher#internal-logic) - Internal implementation details
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Documentation for [GFF](GFF-File-Format) modifications
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) - Best practices for mod development
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for install workflows


---

<a id="hacklist-syntax"></a>

# TSLPatcher HACKList Syntax Documentation

This guide explains how to modify [NCS files](NCS-File-Format) directly using TSLPatcher syntax. For the complete [NCS file](NCS-File-Format) format specification, see [NCS File Format](NCS-File-Format). For general TSLPatcher information, see [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). For HoloPatcher-specific information, see [HoloPatcher README for Mod Developers](HoloPatcher#hacklist-editing-ncs-directly).

## Overview

The `[HACKList]` section in TSLPatcher's changes.ini file enables you to modify compiled [NCS files](NCS-File-Format) (NWScript bytecode, historically called "Neverwinter Compiled Script" but used identically in **KotOR**) directly at the binary level. This advanced feature allows precise [byte](https://en.wikipedia.org/wiki/Byte)-level modifications to script files without recompiling from [NSS](NSS-File-Format) source code, making it ideal for:

- Patching numerical values in existing compiled scripts
- Injecting dynamically-generated string references (StrRefs) and [2DA](2DA-File-Format) memory values
- Performing surgical modifications to hardcoded constants
- Updating scripts to reference new [TLK entries](TSLPatcher-Data-Syntax#tlklist-syntax) or [2DA row numbers](TSLPatcher-Data-Syntax#2dalist-syntax)

**Important:** HACKList is executed **after** `[CompileList]` during patcher execution, allowing compiled scripts to be modified after compilation if needed.

## Table of Contents

- Basic Structure
- [File-Level Configuration](#file-level-configuration)
- [Token Types and Data Sizes](#token-types-and-data-sizes)
- [Memory Token Integration](#memory-token-integration)
- [Offset Calculation](#offset-calculation)
- [Examples](#examples)
- [DeNCS Reference](#dencs-reference)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

## Basic structure

```ini
[HACKList]
!DefaultDestination=override
!DefaultSourceFolder=.  ; Note: `.` refers to the tslpatchdata folder (where changes.ini is located)
File0=myscript.ncs
Replace0=otherscript.ncs

[myscript.ncs]
!Destination=override
!SourceFile=source.ncs
!SaveAs=mypatched.ncs
ReplaceFile=0

; Byte-level modifications
0x15=12345
32=u16:2DAMEMORY1
64=u8:255
0x100=StrRef5
0x200=u32:2DAMEMORY10
```

The `[HACKList]` section declares [NCS files](NCS-File-Format) to modify. Each entry references another section with the same name as the filename.

## file-Level Configuration

### Top-Level Keys in [HACKList]

| [KEY](Container-Formats#key) | type | Default | Description |
|-----|------|---------|-------------|
| `!DefaultDestination` | string | `override` | Default destination for all [NCS files](NCS-File-Format) in this section |
| `!DefaultSourceFolder` | string | `.` | Default source folder for [NCS files](NCS-File-Format). This is a relative path from `mod_path`, which is typically the `tslpatchdata` folder (the parent directory of the `changes.ini` file). The default value `.` refers to the `tslpatchdata` folder itself. Path resolution: `mod_path / !DefaultSourceFolder / filename` |

### file Section Configuration

Each [NCS file](NCS-File-Format) requires its own section (e.g., `[myscript.ncs]`).

| Key | type | Default | Description |
|-----|------|---------|-------------|
| `!Destination` | string | Inherited from `!DefaultDestination` | Where to save the modified file (`override` or `path\to\file.mod`) |
| `!SourceFolder` | string | Inherited from `!DefaultSourceFolder` | Source folder for the [NCS file](NCS-File-Format). Relative path from `mod_path` (typically the tslpatchdata folder). When `.`, refers to the tslpatchdata folder itself. |
| `!SourceFile` | string | Same as section name | Alternative source filename to load |
| `!SaveAs` or `!Filename` | string | Same as section name | Final filename to save as |
| `ReplaceFile` | 0/1 | 0 | **Note:** Unlike other patch lists, HACKList uses `ReplaceFile` (without exclamation point) |

**Destination values:**

- `override` or empty: Save to the Override folder
- `Modules\module.mod`: Insert into an [ERF](Container-Formats#erf)/MOD/[RIM](Container-Formats#rim) container
- Use backslashes for path separators

**Important:** The `ReplaceFile` [KEY](Container-Formats#key) in HACKList does NOT use an exclamation point prefix. This is unique to HACKList compared to other patch lists.

## Token types and data Sizes

Each modification requires specifying an offset and a value. values can include type specifiers to control data size.

### Syntax

```ini
offset=value
offset=type:value
```

- **offset**: Decimal number (e.g., `32`) or hexadecimal (e.g., `0x20`)
- **type** (optional): One of `u8`, `u16`, or `u32` to specify data width
- **value**: Numeric value, token reference, or hex literal

### Supported value types

| value format | type | size | Description |
|--------------|------|------|-------------|
| Numeric (no prefix) | u16 | 2 bytes | 16-bit unsigned integer (default) |
| `u8:123` | u8 | 1 [byte](https://en.wikipedia.org/wiki/Byte) | 8-bit unsigned integer (0-255) |
| `u16:12345` | u16 | 2 bytes | 16-bit unsigned integer (0-65535) |
| `u32:123456` | u32 | 4 bytes | 32-bit unsigned integer |
| `StrRef0` | [StrRef](Audio-and-Localization-Formats#string-references-strref) | Varies* | Reference to [TLK](Audio-and-Localization-Formats#tlk) string from memory |
| `StrRefN` | strref32 | 4 bytes | 32-bit signed [TLK](Audio-and-Localization-Formats#tlk) reference (CONSTI) |
| `2DAMEMORY1` | 2damemory | Varies* | Reference to [2DA](2DA-File-Format) memory value |
| `2DAMEMORYN` | 2damemory32 | 4 bytes | 32-bit signed [2DA](2DA-File-Format) reference (CONSTI) |

*`strref` and `2damemory` without explicit sizes default to `strref32` and `2damemory32` respectively in PyKotor's implementation.

### Endianness

All multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written in **[big-endian](https://en.wikipedia.org/wiki/Endianness)** (network [byte](https://en.wikipedia.org/wiki/Byte) order), which is standard for KOTOR's binary formats.

### type Compatibility Notes

**Historical Background:** TSLPatcher originally distinguished between `strref` and `strref32` (and `2damemory` vs `2damemory32`), but PyKotor's implementation unifies these:

- `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` tokens are automatically handled as 32-bit values
- `2DAMEMORY#` tokens are automatically handled as 32-bit values

If you need legacy 16-bit compatibility, use explicit type specifiers like `u16:StrRef5`, though this is not typically necessary.

## Memory Token Integration

HACKList integrates seamlessly with TSLPatcher's memory token system, allowing dynamic value injection from other patch sections.

### [StrRef](Audio-and-Localization-Formats#string-references-strref) Tokens

Reference values stored in TLKList memory:

```ini
; In TLKList section, this would define StrRef5
StrRef5=123456

; In HACKList, inject it into bytecode
[HACKList]
File0=myscript.ncs

[myscript.ncs]
; At offset 0x100, write the StrRef value
0x100=StrRef5
```

**Use Cases:**

- Injecting dynamically-added [dialog.tlk](Audio-and-Localization-Formats#tlk) string references
- Patching scripts to reference custom text entries
- Updating hardcoded string IDs to mod-added entries

### [2DA](2DA-File-Format) Memory Tokens

Reference values stored in 2DAList memory:

```ini
; In 2DAList section, this would store a row number
Add2DALine1=appearance.2da
[Add2DALine1]
2DAMEMORY1=RowIndex

; In HACKList, inject it into bytecode
[HACKList]
File0=myscript.ncs

[myscript.ncs]
; At offset 0x50, write the 2DA memory value
0x50=2DAMEMORY1
```

**Use Cases:**

- Injecting dynamically-added [2DA](2DA-File-Format) row numbers
- Patching appearance/spell IDs to reference new rows
- Updating hardcoded IDs to mod-added entries

**Important Limitation:** `!FieldPath` values are NOT supported in HACKList. Only numeric memory values can be used.

## offset Calculation

Determining the correct [byte](https://en.wikipedia.org/wiki/Byte) offset is the most critical aspect of HACKList usage.

### [NCS files](NCS-File-Format) structure

```ncs
Byte Offset  Description
-----------  --------------------------------------------
0x00-0x03    File signature: "NCS " (ASCII)
0x04-0x07    Version: "V1.0" (ASCII)
0x08         Magic byte: 0x42
0x09-0x0C    Total file size (4 bytes, big-endian)
0x0D+        Compiled bytecode instructions
```

The header is 13 bytes (0x0D), so the first instruction [byte](https://en.wikipedia.org/wiki/Byte) is at offset 0x0D.

### Finding offsets with DeNCS

**DeNCS** (Decompiler for [NCS](NCS-File-Format)) is a Java-based disassembler that can help you locate exact [byte](https://en.wikipedia.org/wiki/Byte) offsets in [NCS files](NCS-File-Format).

#### Using DeNCS

1. Load your [NCS file](NCS-File-Format) in DeNCS
2. Disassemble to view instruction-level operations
3. Identify the target instruction and note its [byte](https://en.wikipedia.org/wiki/Byte) offset
4. If modifying an instruction's operand, add to the instruction's offset:
   - For CONSTI operands: offset + 1 (skip the opcode [byte](https://en.wikipedia.org/wiki/Byte))
   - For other operands: depends on instruction type

#### Example Disassembly

```ncs
Offset  Inst                Args
------  ----                ----
0x0D    NOP
0x0E    CONSTI              10000
        (opcode at 0x0E, operand at 0x0F-0x12)
0x13    CPDOWNSP            -4
0x15    CONSTS              "Hello World"
        (opcode at 0x15, string offset at 0x16-0x19)
```

To modify the CONSTI value at 0x0E, you'd patch bytes 0x0F-0x12.

### Common Instruction Layouts

| Instruction | Opcode size | Operand size | Example offset to Patch |
|-------------|-------------|--------------|-------------------------|
| `CONSTI` | 1 byte | 4 bytes | offset + 1 |
| `CONSTF` | 1 byte | 4 bytes | offset + 1 |
| `CONSTS` | 1 byte | 4 bytes | offset + 1 |
| `CPDOWNSP` | 1 byte | 4 bytes | offset + 1 |
| `ACTION` | 1 byte | 4 bytes | offset + 1 |
| `JMP` | 1 byte | 4 bytes | offset + 1 |
| `JZ` | 1 byte | 4 bytes | offset + 1 |

### Hex vs Decimal offsets

Both formats are supported:

- **Hexadecimal**: `0x20`, `0x100`, `0xFF`
- **Decimal**: `32`, `256`, `255`

Use hexadecimal for convenience when working with [byte](https://en.wikipedia.org/wiki/Byte)-aligned operations.

## Examples

### Example 1: Modifying a Hardcoded Integer

Replace a hardcoded constant in a compiled script:

```ini
[HACKList]
File0=combat_script.ncs

[combat_script.ncs]
; At offset 0x50, change a damage value from 10 to 50
0x50=u16:50
```

### Example 2: Injecting Dynamic [TLK](Audio-and-Localization-Formats#tlk) Reference

Inject a dynamically-added string reference:

```ini
[TLKList]
StrRef1=My New Dialog Entry

[HACKList]
File0=dialog_script.ncs

[dialog_script.ncs]
; At offset 0x100, inject the StrRef value
0x100=StrRef1
```

### Example 3: Patching Multiple values

Modify several offsets in the same file:

```ini
[HACKList]
File0=spell_script.ncs

[spell_script.ncs]
; Patch spell ID at 0x30
0x30=u16:123

; Patch damage amount at 0x50
0x50=u32:999

; Patch duration at 0x70
0x70=u16:60
```

### Example 4: Using [2DA](2DA-File-Format) Memory values

Inject a dynamically-added [2DA](2DA-File-Format) row number:

```ini
[2DAList]
Add2DALine1=spells.2da

[Add2DALine1]
2DAMEMORY5=RowIndex

[HACKList]
File0=spell_handler.ncs

[spell_handler.ncs]
; Inject the row number at offset 0x88
0x88=2DAMEMORY5
```

### Example 5: Advanced Multi-type Patching

Combine different data sizes and token types:

```ini
[HACKList]
File0=complex_script.ncs
Replace0=old_script.ncs

[complex_script.ncs]
ReplaceFile=1

; 8-bit flag value
0x20=u8:1

; 16-bit numeric literal
0x30=u16:4096

; 32-bit StrRef from memory
0x40=StrRef10

; 32-bit 2DA memory reference
0x50=2DAMEMORY3

; Direct hex value
0x60=u32:0xDEADBEEF
```

### Example 6: Saving to Container

Save modified scripts to a [module container](Container-Formats#erf):

```ini
[HACKList]
!DefaultDestination=Modules\mymod.mod
File0=modified_script.ncs

[modified_script.ncs]
!Destination=Modules\mymod.mod
ReplaceFile=1

; Multiple modifications
0x50=u16:100
0x60=StrRef5
```

## DeNCS Reference

*DeNCS* provides comprehensive [NCS](NCS-File-Format) disassembly capabilities for locating exact [byte](https://en.wikipedia.org/wiki/Byte) offsets. Understanding its output is essential for `[HACKList]` usage.

### [KEY](Container-Formats#key) DeNCS Features

- **Instruction-level disassembly**: See each bytecode instruction
- **offset mapping**: Exact [byte](https://en.wikipedia.org/wiki/Byte) positions for each instruction
- **Operand extraction**: View data embedded in instructions
- **Jump resolution**: Understand control flow

### Reading DeNCS Output

```ncs
Offset  Instruction    Args
------  -------------  ----
0x0D    NOP
0x0E    CONSTI         0x00002710 (10000)
0x13    CPDOWNSP       -4
0x15    CONSTI         0x00000064 (100)
0x1A    CPDOWNSP       -4
0x1B    ACTION         0x00401048 (AddObjectToInventory)
0x20    MOVSP          -4
0x22    RETN

Stack:
Before NOP: []
After NOP: []
...
```

To modify the `CONSTI` at `0x0E`, you'd patch bytes `0x0F-0x12` (the 4-[byte](https://en.wikipedia.org/wiki/Byte) operand).

### Common Instruction Patterns

Many scripts follow predictable patterns you can target:

**Setting a constant value:**

```ncs
CONSTI <value>
CPDOWNSP -4
```

This pushes a 4-[byte](https://en.wikipedia.org/wiki/Byte) integer onto the stack. The value is at **offset +1**.

**Calling a function:**

```ncs
ACTION <function_pointer>
```

The function pointer is a 4-[byte](https://en.wikipedia.org/wiki/Byte) address at **offset +1**.

**Conditional jumps:**

```ncs
JZ <offset>
```

The jump offset is a 4-[byte](https://en.wikipedia.org/wiki/Byte) signed integer at **offset +1**.

## Common Use Cases

### 1. Updating Hardcoded string References

Many vanilla scripts have hardcoded [StrRef](Audio-and-Localization-Formats#string-references-strref) values. HACKList lets you redirect them to mod-added entries:

```ini
[TLKList]
; Add your custom string
StrRef99=New Dialog Text

[HACKList]
File0=old_dialog.ncs

[old_dialog.ncs]
; Replace hardcoded StrRef 12345 with your new one
0x100=StrRef99
```

### 2. Patching Spell/Item IDs

When adding new spells or items, existing scripts may need to reference them:

```ini
[2DAList]
Add2DALine1=spells.2da

[Add2DALine1]
2DAMEMORY7=RowIndex

[HACKList]
File0=spell_handler.ncs

[spell_handler.ncs]
; Inject the new spell's row number
0x88=2DAMEMORY7
```

### 3. Adjusting Combat values

Modify damage, duration, or other gameplay values without recompiling (e.g. `0x30=u16:50` is the damage value, `0x50=u16:60` is the duration value, `0x70=u16:10` is the cooldown value):

```ini
[HACKList]
File0=combat_init.ncs

[combat_init.ncs]
; Change damage from 10 to 50
0x30=u16:50

; Change duration from 30 to 60 seconds
0x50=u16:60

; Change cooldown from 5 to 10 seconds
0x70=u16:10
```

### 4. Enabling Debug Features

Some scripts have debug flags that can be enabled:

```ini
[HACKList]
File0=debug_script.ncs

[debug_script.ncs]
; Enable debug flag (assuming it's a boolean at 0x20)
0x20=u8:1
```

### 5. Fixing Known Bugs

Patch bugs in vanilla scripts without distributing modified source:

```ini
[HACKList]
File0=buggy_script.ncs

[buggy_script.ncs]
; Fix incorrect check value
0x50=u16:1

; Fix incorrect comparison
0x70=u32:1000
```

## Troubleshooting

### Offset Calculation Errors

**Problem:** The patched value doesn't seem to take effect

**Solutions:**

1. Verify the offset using *DeNCS*
2. Check if you're modifying the correct bytes (instruction vs operand) (e.g. `CONSTI` is an opcode, `-4` is an operand)
3. Ensure you're not overwriting opcodes accidentally (e.g. `CONSTI` is an opcode, not a value, so `0x0E=u16:100` is incorrect, it should be `0x0E=u16:100`)
4. Verify big-endian [byte](https://en.wikipedia.org/wiki/Byte) order for multi-[byte](https://en.wikipedia.org/wiki/Byte) values (e.g. `u16:0x1234` is `0x12 0x34`, not `0x34 0x12`)

### Memory Token Not Defined

**Problem:** `StrRefN was not defined before use`

**Solutions:**

1. Ensure the token is defined in `[TLKList]`/`[2DAList]` **before** `[HACKList]` execution
2. Check the token number for typos (e.g. `StrRef1` instead of `StrRef10`)
3. Verify token definition syntax in the appropriate section

**Important:** `[HACKList]` executes **after** `[CompileList]` and **after** `[TLKList]` and `[2DAList]` in HoloPatcher, so memory tokens should be available.

### Wrong data size

**Problem:** Script crashes or behaves unexpectedly after patching

**Solutions:**

1. Verify you're using the correct data size (`u8`/`u16`/`u32`)
2. Check *DeNCS* output to confirm the operand size
3. Ensure you're not truncating large values with `u8`/`u16`
4. Verify signed vs unsigned behavior for large values (e.g. `u32:0x80000000` is a negative number)

### File Not Found

**Problem:** `File not found` error during patching

**Solutions:**

1. Verify `!SourceFile` points to the correct filename (e.g. `source.ncs`)
2. Check `!DefaultSourceFolder` and `!SourceFolder` paths (e.g. `tslpatchdata\source.ncs`)
3. Ensure the source file exists in the tslpatchdata folder (e.g. `tslpatchdata\source.ncs`)
4. Verify the file extension is `.ncs`

### Archival Insertion Issues

**Problem:** Modified script not appearing in [ERF](Container-Formats#erf)/MOD/[RIM](Container-Formats#rim) container

**Solutions:**

1. Verify `!Destination` path uses backslashes
2. Check the bioware container exists before insertion (e.g. `Modules\mymod.mod`)
3. Ensure the destination folder structure is correct
4. Verify the `ReplaceFile` setting (0 = skip if exists, 1 = overwrite) (0 = skip if the file exists, 1 = overwrite the existing file)

## Technical Details

### Execution Order

**HoloPatcher** processes patch lists in this order:

1. `[InstallList]` (install files)
2. `[TLKList]` (add dialog entries)
3. `[2DAList]` (modify [2DA files](2DA-File-Format))
4. `[GFFList]` (modify [GFF](GFF-File-Format) files)
5. `[CompileList]` (compile [NSS](NSS-File-Format) to [NCS](NCS-File-Format))
6. `[HACKList]` (modify [NCS](NCS-File-Format) bytecode) ← **You are here**
7. `[SSFList]` (modify soundset files)

**Important:** This differs from TSLPatcher's original order, where `[HACKList]` executes before `[CompileList]`. HoloPatcher runs `[CompileList]` first to allow scripts to be compiled and then potentially edited. This order change is intentional and should not affect mod compatibility in practice.

All memory tokens from `[TLKList]` and `[2DAList]` are available during `[HACKList]` processing.

### Byte-Level Writing

All multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written in **[big-endian](https://en.wikipedia.org/wiki/Endianness)** format:

- `u16:0x1234` writes `12 34`
- `u32:0x12345678` writes `12 34 56 78`
- Bytes are written from most significant to least significant

### `ReplaceFile` Key Behavior

Unlike other patch lists, `[HACKList]`'s `ReplaceFile` key does **not** use an exclamation point:

```ini
; CORRECT (`[HACKList]` syntax)
ReplaceFile=1

; INCORRECT (this is for other sections)
!ReplaceFile=1
```

`ReplaceFile=0` means **"skip if file exists"**, while `ReplaceFile=1` means ***"overwrite existing file"***.

I have no idea why this is the exclusive instance of Stoffe's variables that doesn't use exclamation-point syntax but whatever.

### Compatibility Notes

- PyKotor's HACKList implementation is compatible with TSLPatcher v1.2.10b+
- All [NCS](NCS-File-Format) versions V1.0 are supported
- Container insertion works for [ERF](Container-Formats#erf), MOD, and [RIM](Container-Formats#rim) formats
- Memory tokens from TLKList and 2DAList are fully supported
- `!FieldPath` is **not** supported (only numeric values)

### See also

- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) - [GFF file](GFF-File-Format) modifications
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) - General TSLPatcher documentation
- [DeNCS Documentation](http://nwvault.ign.com/View.php?view=Other.Detail&id=416) - [NCS](NCS-File-Format) disassembler
- [NCS Instruction Reference](https://nwn.wiki/compiler/instructions) - Detailed bytecode documentation
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for HACKList/binary patching

## Advanced Topics

### Offset Alignment

When working with [NCS](NCS-File-Format) bytecode, be aware of alignment requirements:

- Instructions start on any [byte](https://en.wikipedia.org/wiki/Byte) boundary (no alignment enforced)
- Operands follow immediately after opcodes
- Multi-[byte](https://en.wikipedia.org/wiki/Byte) values are written as-is without padding

### *Inserting* vs *Modifying*

**Important:** `[HACKList]` can only **modify existing bytes**. It cannot:

- Insert new bytes (files would shift offsets)
- Delete bytes (files would shrink)
- Resize instruction arrays

It can *only* overwrite existing bytes.

For structural changes, use `[CompileList]` to recompile from [NSS](NSS-File-Format) source.

### Debugging Tips

Enable verbose logging to see `[HACKList]` operations:

```ini
[Settings]
LogLevel=4
```

This will show detailed output like:

```shell
Loading `[HACKList]` patches from ini...
`[HACKList]` myscript.ncs: seeking to offset 0x20
`[HACKList]` myscript.ncs: writing unsigned WORD (16-bit) 12345 at offset 0x20
```

## Conclusion

`[HACKList]` provides powerful [byte](https://en.wikipedia.org/wiki/Byte)-level control over compiled [NCS](NCS-File-Format) scripts, enabling surgical modifications without source code access. While it requires understanding [NCS](NCS-File-Format) bytecode structure and careful offset calculation, it's essential for advanced modding scenarios involving dynamic value injection and hardcoded constant patching.

For most modding needs, `[CompileList]` ([NSS](NSS-File-Format) source compilation) is preferred. `[HACKList]` should be reserved for cases where source code is unavailable or where [byte](https://en.wikipedia.org/wiki/Byte)-level precision is required.


---
