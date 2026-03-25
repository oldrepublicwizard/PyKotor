# Using HoloPatcher: Installation and Reversion

_This page explains how to install mods with HoloPatcher. If you are a mod developer, you may be looking for [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers)_

HoloPatcher aims to offer a user experience identical to TSLPatcher. Follow these steps for a smooth mod installation:

**Before you install:** Point HoloPatcher at your **game root directory** (the folder that contains `swkotor.exe` or `swkotor2.exe` and the `override` folder). Ensure you have a clean backup or know how to restore if something goes wrong. Install one mod at a time when testing compatibility; use the patcher’s backup/restore before switching options or reinstalling. See [Mod Creation Best Practices](Mod-Creation-Best-Practices#testing-and-compatibility) for testing and [Concepts](Concepts) for override and resource order.

### Community downloads and player-oriented guides

- **HoloPatcher on Deadly Stream:** [file page + comments](https://deadlystream.com/files/file/2243-holopatcher/) — downloads and release notes; [TOOL: HoloPatcher topic](https://deadlystream.com/topic/9807-toolholopatcher/) — install/merge Q&A (this wiki remains SSOT for patcher _behavior_; threads are _context_).
- **Large distribution example:** [KOTOR 1 Community Patch](https://deadlystream.com/files/file/1258-kotor-1-community-patch/) — real-world HoloPatcher packaging; always read the mod’s current readme for your game edition.
- **Generic PC setup (paths, widescreen, common fixes):** [PCGamingWiki — KotOR](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic) · [KotOR II: TSL](https://www.pcgamingwiki.com/wiki/Star_Wars:_Knights_of_the_Old_Republic_II_-_The_Sith_Lords) · [Series hub](https://www.pcgamingwiki.com/wiki/Series:Star_Wars:_Knights_of_the_Old_Republic). Player-facing install notes only—**not** authoritative for KEY/BIF semantics or override resolution ([KEY-File-Format](KEY-File-Format), [Concepts](Concepts)).
- **Historical forum context:** [LucasForums Archive — newbie tools + how to install mods](https://www.lucasforumsarchive.com/thread/129789-guide-for-the-newbie-what-tools-do-i-need-to-mod-kotor-how-to-install-mods) (legacy tool lists; cross-check with this wiki and Deadly Stream file hubs). [Installing a mod without TSLPatcher (e.g. Mac / manual)](https://www.lucasforumsarchive.com/thread/180751-how-do-install-a-mod-without-tsl-patcher) illustrates why **merge-aware** installers remain important for many releases.
- **TSLPatcher lineage (read for history, use HoloPatcher today):** [TSLPatcher v1.2.10b1 release thread](https://www.lucasforumsarchive.com/thread/149285-tslpatcher-v1210b1-mod-installer) — original mod-installer design goals. [Can't get TSL Patcher to work anymore](https://www.lucasforumsarchive.com/thread/206390-argh-cant-get-tsl-patcher-to-work-for-me-anymore) — typical override/path confusion; compare with steps above and [Concepts](Concepts#override-folder).
- **2DA merge pain (why whole-file overrides fail):** [spells.2da, compatibility and TSL Patcher](https://www.lucasforumsarchive.com/thread/205823-spells2da-compatibility-and-tsl-patcher) — workflow story; wiki SSOT for syntax remains [TSLPatcher-2DAList-Syntax](TSLPatcher-2DAList-Syntax) / [2DA-spells](2DA-spells).

**Select Mod Folder:** Direct HoloPatcher to the mod folder containing the 'tslpatchdata' folder.
**Select Game Directory:** Point HoloPatcher to your KotOR game directory. These paths are often pre-populated in dropdown menus for convenience.
**Choose Installation Option:** If the mod provides multiple installation options (indicated by a namespaces.ini file), select your preferred option from the first dropdown menu.
After configuring, click 'install' to initiate the patching process.

## KotORModSync (optional)

**KotORModSync** ([`th3w1zard1/KotORModSync`](https://github.com/th3w1zard1/KotORModSync)) helps manage **many mods** or **multiple install targets** (profiles, sync between folders, team handoffs). It is **complementary** to HoloPatcher: you still need a valid TSLPatcher/HoloPatcher INI workflow for merges inside `tslpatchdata`. If you only install a handful of mods, following each mod’s readme + HoloPatcher is enough; if you maintain parallel installs or large lists, ModSync can reduce manual bookkeeping. See [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) (first-mod walkthrough section) for author-side packaging context.

## Reverting Mod Installations

To undo the modifications made by a recent mod installation:

**Navigate to Tools -> Uninstall Mod/Restore Backup from the top menu.** This action restores your game files to their state just before the latest mod installation, effectively undoing all recent changes.
Important: Avoid Multiple Installations
Do not reinstall the same mod using the same option without first reverting previous changes. This is crucial for several reasons:

**Partial Installations:** If an installation is interrupted (for example, if the app is closed prematurely) and then restarted, the mod is reapplied over partially modified files. This can result in duplication within critical game files, such as [appearance.2da](2DA-File-Format#appearance2da), leading to potential game-breaking issues.

**Correcting Mistakes:** If you inadvertently install a mod multiple times without reverting, the game files may contain redundant modifications. However, HoloPatcher keeps backups for each installation. To correct this, you must use the Uninstall Mod/Restore Backup feature twice:

The first execution removes the modifications from the most recent (second) installation, reverting files to their state after the first (interrupted) installation.
The second execution then removes the remaining modifications, fully reverting your game files to their original state before any installation attempts.

## Installing Mods on iOS Devices

For iOS installations, it's critical to ensure that all KotOR file names are in lowercase. If file names retain uppercase characters, the game will crash immediately after tapping the 'play' button on the main menu.

To prevent this issue, HoloPatcher includes a specific utility designed to address iOS's case sensitivity:

- **Navigate to Tools -> Fix iOS Case Sensitivity within HoloPatcher.**
- **Direct the tool to your KotOR directory or install folder.** If you're applying mods specifically for the mobile version of The Sith Lords Restored Content Mod (TSLRCM), point the tool to the 'mtslrcm' directory.
This step is essential for a successful mod installation on iOS devices, ensuring stability and preventing crashes due to case sensitivity conflicts.

### See also

- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) -- Mod development and patching syntax
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) -- Workarounds and compatibility
- [KEY-File-Format](KEY-File-Format) -- Resource resolution and override order
- [2DA-File-Format](2DA-File-Format) -- Game data tables (e.g. appearance.2da)
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, forums for troubleshooting and guides
