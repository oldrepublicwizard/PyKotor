# Using HoloPatcher: Installation and Reversion

_This page explains how to install mods with HoloPatcher. If you are packaging a mod, see [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers)._

HoloPatcher is the modern PyKotor implementation of the TSLPatcher workflow. For players, the important part is simple: point it at the right game folder, install one mod option at a time, and use its restore flow before retrying or switching variants.

## Before you install

- Point HoloPatcher at your **game root directory**: the folder containing `swkotor.exe` or `swkotor2.exe`, plus folders such as `override`, `modules`, and `lips`.
- Keep a clean backup or a disposable test install if you are testing several mods.
- Install one mod at a time when checking compatibility.
- If a mod offers multiple options, use the built-in backup/restore before changing options or reinstalling.

**Verified against source files:**

- `Libraries/PyKotor/src/pykotor/tslpatcher/` - patching semantics and install workflow
- `Tools/HoloPatcher/src/holopatcher/` - application behavior, backup/restore flow, and iOS utilities
- `Libraries/PyKotor/src/pykotor/extract/installation.py` - game-root detection context used elsewhere in the toolchain

See [Mod Creation Best Practices](Mod-Creation-Best-Practices#testing-and-compatibility) for compatibility guidance and [Concepts](Concepts) for override and resource-order background.

### Community downloads and player-oriented guides

- **HoloPatcher on Deadly Stream:** [file page + comments](https://deadlystream.com/files/file/2243-holopatcher/) — downloads and release notes
- [TOOL: HoloPatcher topic](https://deadlystream.com/topic/9807-toolholopatcher/) — install/merge Q&A (this wiki remains SSOT for patcher _behavior_; threads are _context_).
- **Large distribution example:** [KOTOR 1 Community Patch](https://deadlystream.com/files/file/1258-kotor-1-community-patch/) — real-world HoloPatcher packaging; always read the mod’s current readme for your game edition.
- **Generic PC setup (paths, widescreen, common fixes):**
  - [PCGamingWiki — KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic)
  - [KotOR II: TSL](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords)
  - [Series hub](https://www.pcgamingwiki.com/wiki/Series:Star_Wars:_Knights_of_the_Old_Republic)
  - Player-facing install notes only—**not** authoritative for KEY/BIF semantics or override resolution:
    - [KEY-File-Format](KEY-File-Format)
    - [Concepts](Concepts)
- **Historical forum context:** [LucasForums Archive — newbie tools + how to install mods](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods) (legacy tool lists; cross-check with this wiki and Deadly Stream file hubs). [Installing a mod without TSLPatcher (e.g. Mac / manual)](https://www.lucasforumsarchive.com/thread/180751-how-do-install-a-mod-without-tsl-patcher) illustrates why **merge-aware** installers remain important for many releases.
- **TSLPatcher lineage (read for history, use HoloPatcher today):** [TSLPatcher v1.2.10b1 release thread](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer) — original mod-installer design goals. [Can't get TSL Patcher to work anymore](https://www.lucasforumsarchive.com/thread/206390-argh-cant-get-tsl-patcher-to-work-for-me-anymore) — typical override/path confusion; compare with steps above and [Concepts](Concepts#override-folder).
- **2DA merge pain (why whole-file overrides fail):** [spells.2da, compatibility and TSL Patcher](https://www.lucasforumsarchive.com/thread/205823-spells2da-compatibility-and-tsl-patcher) — workflow story; wiki SSOT for syntax remains [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) / [2DA-spells](2DA-File-Format#spells2da).

## Install a mod

1. **Select the mod folder.** This is the folder that contains `tslpatchdata`.
2. **Select the game directory.** Choose your KotOR game root, not the `override` folder by itself.
3. **Choose an installation option, if present.** Mods with `namespaces.ini` expose one or more variants in the first dropdown.
4. **Run Install.** Review the log if anything fails instead of immediately retrying.

If the author ships extra instructions for Steam, GOG, Aspyr, or mobile builds, follow those too. HoloPatcher handles merge-aware patching, but it cannot correct a mod package that targets the wrong game version or wrong install path.

## KotORModSync (optional)

**KotORModSync** (**`th3w1zard1/KotORModSync`**) helps manage **many mods** or **multiple install targets** (profiles, sync between folders, team handoffs). It is **complementary** to HoloPatcher: you still need a valid TSLPatcher/HoloPatcher INI workflow for merges inside `tslpatchdata`. If you only install a handful of mods, following each mod’s readme + HoloPatcher is enough; if you maintain parallel installs or large lists, ModSync can reduce manual bookkeeping. See [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) (first-mod walkthrough section) for author-side packaging context.

- Canonical (th3w1zard1/KotORModSync): <https://github.com/th3w1zard1/KotORModSync/tree/c8b0d10ce3fd7525d593d34a3be8d151da7d3387>

## Reverting Mod Installations

To undo the most recent installation, use **Tools -> Uninstall Mod/Restore Backup**. That restores files to the state they were in immediately before that install ran.

### Why reinstalling without restoring is risky

- **Interrupted installs can duplicate changes.** If you close the app mid-install and then run the same option again, merge targets such as [appearance.2da](2DA-File-Format#appearance2da) can end up with duplicate rows or repeated edits.
- **Retrying the same option stacks changes.** HoloPatcher treats each install as a new operation and keeps a backup for each one.

If you installed the same thing twice by mistake, restore twice:

1. The first restore undoes the most recent installation.
2. The second restore undoes the earlier one and returns you to the pre-install state.

## Installing Mods on iOS Devices

iOS builds are case-sensitive in ways the desktop releases are not. If KotOR asset names keep uppercase characters where the mobile port expects lowercase, the game can crash immediately after you press Play.

HoloPatcher includes an iOS fix-up utility for this:

- Go to **Tools -> Fix iOS Case Sensitivity**.
- Point it at your KotOR install folder.
  - ! If you are instead patching the mobile TSLRCM layout, point it at the `mtslrcm` folder when the mod instructions call for that layout.

Run that fix before troubleshooting deeper compatibility issues on iOS. A surprising number of "instant crash on launch" reports turn out to be filename-case problems rather than bad mod content.

### See also

- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) -- Mod development and patching syntax
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- Preserved legacy source for original TSLPatcher behavior
- [TSLPatcher-InstallList-Syntax](TSLPatcher-InstallList-Syntax) -- Exact author-facing InstallList semantics
- [TSLPatcher-TLKList-Syntax](TSLPatcher-TLKList-Syntax) -- Exact author-facing TLKList semantics
- [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) -- Exact author-facing 2DAList semantics
- [TSLPatcher-GFFList-Syntax](TSLPatcher-GFFList-Syntax) -- Exact author-facing GFFList semantics
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) -- Workarounds and compatibility
- [KEY-File-Format](KEY-File-Format) -- Resource resolution and override order
- [2DA-File-Format](2DA-File-Format) -- Game data tables (e.g. appearance.2da)
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for troubleshooting and guides
