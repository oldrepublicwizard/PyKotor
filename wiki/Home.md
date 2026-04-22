# Welcome to the PyKotor Wiki

<a id="documentation"></a>

PyKotor is a monorepo that currently packages the `pykotor`, `holopatcher`, `holocron-toolset`, and `kotordiff` tools, and the wiki content shipped with Holocron Toolset is copied from the repo-root `wiki/` tree during packaging rather than being maintained as a separate website-only documentation set. [[PyKotor `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/pyproject.toml), [HoloPatcher `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/pyproject.toml), [Holocron Toolset `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/pyproject.toml), [KotorDiff `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/KotorDiff/pyproject.toml), [Holocron Toolset `setup.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/setup.py)]

The entry table below is therefore a routing layer over concrete package and wiki content that already exists in this repository: install and troubleshooting pages under the HoloPatcher docs, tool-start pages under the Holocron Toolset docs, format-reference pages under the resource-format docs, and deeper reverse-engineering material under the findings pages. [[Holocron Toolset `SOURCES.txt`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/holocrontoolset.egg-info/SOURCES.txt), [PyKotor `CLI_QUICKSTART.md`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md)]

This wiki is part of the shipped Holocron Toolset help payload rather than website-only prose: the Toolset build step copies the repo-root `wiki/` directory into `src/toolset/help/wiki`, setuptools package-data includes `help/wiki/**/*.md`, `MANIFEST.in` includes the same tree for source distributions, and the generated source manifest lists concrete copied pages such as `Home.md`, `2DA-File-Format.md`, and `GFF-File-Format.md`. [[Holocron Toolset `setup.py`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/setup.py), [Holocron Toolset `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/pyproject.toml), [Holocron Toolset `MANIFEST.in`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/MANIFEST.in), [Holocron Toolset `SOURCES.txt`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/holocrontoolset.egg-info/SOURCES.txt)]

## Start here

| If you need to... | Start here | Then read |
| ----------------- | ---------- | --------- |
| Install or troubleshoot a mod | [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) | [Concepts](Concepts), [Mod Creation Best Practices](Mod-Creation-Best-Practices) |
| Author a patcher-based mod | [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) | [TSLPatcher 2DAList Syntax Guide](TSLPatcher-Data-Syntax#2dalist-syntax), [TSLPatcher TLKList Syntax Guide](TSLPatcher-Data-Syntax#tlklist-syntax), [TSLPatcher GFFList Syntax Guide](TSLPatcher-GFF-Syntax#gfflist-syntax) |
| Edit resources in a GUI | [Holocron Toolset: Getting Started](Holocron-Toolset-Getting-Started) | [Holocron Toolset: Core resources](Holocron-Toolset-Core-Resources), [Holocron Toolset: Module resources](Holocron-Toolset-Module-Resources) |
| Work headlessly or automate a workflow | [CLI quickstart](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/CLI_QUICKSTART.md) | [KotorDiff Integration](KotorDiff-Integration), [Explanations on HoloPatcher Internal Logic](HoloPatcher#internal-logic) |
| Understand why a file wins in-game | [Concepts](Concepts) | [Resource formats and resolution](Resource-Formats-and-Resolution), [KEY File Format](Container-Formats#key) |
| Look up a binary format or game resource type | [Resource formats and resolution](Resource-Formats-and-Resolution) | The relevant format page for that extension |

## Toolchain map

- **PyKotor** is the library and CLI layer: its package metadata exposes the `pykotor` and `pykotorcli` commands, and its source tree contains the extract, resource-format, and diff-tool modules that the other packages build on. [[PyKotor `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/pyproject.toml), [`pykotor.extract`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/extract), [`pykotor.resource.formats`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats), [`pykotor.diff_tool`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/diff_tool)]
- **HoloPatcher** is the installer layer: its package metadata exposes the `holopatcher` command, and its entrypoint dispatches `install`, `uninstall`, and `validate` through the CLI code path before attempting GUI startup. [[HoloPatcher `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/pyproject.toml), [`holopatcher.__main__`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/src/holopatcher/__main__.py)]
- **Holocron Toolset** is the GUI editing layer: its package metadata exposes the main `holocron-toolset` application plus standalone editor entry points, and its source tree contains editor, dialog, and renderer packages for module and resource editing. [[Holocron Toolset `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/pyproject.toml), [`toolset/gui/editors`](https://github.com/OpenKotOR/PyKotor/tree/master/Tools/HolocronToolset/src/toolset/gui/editors), [`toolset/gui/dialogs`](https://github.com/OpenKotOR/PyKotor/tree/master/Tools/HolocronToolset/src/toolset/gui/dialogs), [`toolset/gui/widgets/renderer`](https://github.com/OpenKotOR/PyKotor/tree/master/Tools/HolocronToolset/src/toolset/gui/widgets/renderer)]
- **KotorDiff** is the comparison layer: its package metadata exposes the `kotordiff` command, and its runtime is a thin package wrapper over the shared `pykotor.diff_tool` code. [[KotorDiff `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/KotorDiff/pyproject.toml), [`pykotor.diff_tool.app`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/diff_tool/app.py)]

## Workspace packages

- **PyKotor** publishes the `pykotor` package, exposes `pykotor` and `pykotorcli` console scripts, and declares `bioware-kaitai-formats`, `defusedxml`, `kaitaistruct`, and `ply` as core dependencies. [[PyKotor `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/pyproject.toml)]
- **PyKotor** implements installation discovery and resource search in `pykotor.extract.installation`, defines engine/resource typing in `pykotor.resource.type`, and keeps format readers and writers under `pykotor.resource.formats`. [[`pykotor.extract.installation`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/extract/installation.py), [`pykotor.resource.type`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py), [`pykotor.resource.formats`](https://github.com/OpenKotOR/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats)]
- **HoloPatcher** publishes the `holopatcher` console script, depends on `pykotor[encodings,updater]`, and describes itself as a faster, cross-platform alternative to TSLPatcher. [[HoloPatcher `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/pyproject.toml)]
- **HoloPatcher** routes `install`, `uninstall`, and `validate` requests through its CLI path, otherwise attempts to launch the GUI application and falls back to a warning when GUI execution is unavailable. [[`holopatcher.__main__`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HoloPatcher/src/holopatcher/__main__.py)]
- **Holocron Toolset** publishes the `holocron-toolset` application, standalone editor entry points such as `are-editor`, `mdl-editor`, `utc-editor`, `tpc-editor`, and `twoda-editor`, and standalone applications such as `module-designer` and `indoor-builder`. [[Holocron Toolset `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/pyproject.toml)]
- **Holocron Toolset** keeps its standalone editor registry in `toolset.gui.editors.standalone`, where file extensions such as `.2da`, `.utc`, `.dlg`, `.mdl`, `.mdx`, `.tlk`, `.tpc`, `.dds`, `.rim`, and `.erf` are mapped to concrete editor classes and launcher names. [[`toolset.gui.editors.standalone`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/HolocronToolset/src/toolset/gui/editors/standalone.py)]
- **KotorDiff** publishes the `kotordiff` console script as a thin package over shared `pykotor.diff_tool` functionality. [[KotorDiff `pyproject.toml`](https://github.com/OpenKotOR/PyKotor/blob/master/Tools/KotorDiff/pyproject.toml)]
- **KotorDiff** drives diff generation through `pykotor.diff_tool.app`, which imports installation loading, GFF handling, resource typing, reference caches, TSLPatcher diff generation, and incremental writer support from the shared PyKotor codebase. [[`pykotor.diff_tool.app`](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/diff_tool/app.py)]
- **bioware-kaitai-formats** is a workspace package of generated Python parsers, while the authoritative `.ksy` specifications are maintained in the upstream `OpenKotOR/bioware-kaitai-formats` repository; that split matches Kaitai Struct's own documented model, where `.ksy` specifications are compiled into language-specific parsers by the Kaitai compiler and loaded through target-language runtime libraries. [[workspace `bioware-kaitai-formats` README](https://github.com/OpenKotOR/PyKotor/blob/master/Libraries/bioware-kaitai-formats/README.md), [upstream `OpenKotOR/bioware-kaitai-formats`](https://github.com/OpenKotOR/bioware-kaitai-formats), [Context7: Kaitai Struct overview](https://context7.com/kaitai-io/kaitai_struct/llms.txt)]

## Core reference pages

- [Concepts](Concepts)
- [Resource formats and resolution](Resource-Formats-and-Resolution)
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods)
- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [Reverse Engineering Findings](reverse_engineering_findings)

## Learning paths

- **New player:** [Installing Mods with HoloPatcher](HoloPatcher#installing-mods) -> [Concepts](Concepts#resource-resolution-order) -> [Resource formats and resolution](Resource-Formats-and-Resolution)
- **First mod author:** [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) -> [Mod Creation Best Practices](Mod-Creation-Best-Practices) -> [TSLPatcher data syntax](TSLPatcher-Data-Syntax)
- **Tool author or contributor:** [Resource formats and resolution](Resource-Formats-and-Resolution) -> [Reverse Engineering Findings](reverse_engineering_findings)

## Workflow guides

- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods)
- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers)
- [TSLPatcher data syntax](TSLPatcher-Data-Syntax)
- [TSLPatcher GFF syntax](TSLPatcher-GFF-Syntax)
- [TSLPatcher install and hack syntax](TSLPatcher-Install-and-Hack-Syntax)

## Community guides

- [How to Avoid Killing Mission After Joining the Dark Side](how-to-avoid-killing-mission-after-joining-the-dark-side) — step-by-step K1 gameplay guide covering companion UTC preparation, party management, and dark-side-ending edge cases

## Preserved source documents

- **Bioware Aurora**:
  - [Core Formats](Bioware-Aurora-Core-Formats)
  - [Module & Area](Bioware-Aurora-Module-and-Area)
  - [Creature](Bioware-Aurora-Creature)
  - [Items, Economy & Narrative](Bioware-Aurora-Items-Economy-and-Narrative)
  - [Spatial & Interactive](Bioware-Aurora-Spatial-and-Interactive)
  - [Conversation](Bioware-Aurora-Conversation)
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme)

## Cross-reference: other tools and engines

- **Engine reimplementations:** xoreos keeps dedicated `kotor`, `kotor2`, `kotorbase`, and `odyssey` engine directories; reone documents itself as a KotOR and TSL engine project in its README; and KotOR.js exposes launcher, game, forge, debugger, resource, and odyssey-engine trees directly in source. [[`xoreos/src/engines`](https://github.com/xoreos/xoreos/tree/master/src/engines), [reone README](https://github.com/seedhartha/reone/blob/master/README.md), [`KotOR.js/src/apps`](https://github.com/KobaltBlu/KotOR.js/tree/master/src/apps), [`KotOR.js/src/resource`](https://github.com/KobaltBlu/KotOR.js/tree/master/src/resource), [`KotOR.js/src/odyssey`](https://github.com/KobaltBlu/KotOR.js/tree/master/src/odyssey)]
- **Format and archive stacks:** xoreos-tools publishes CLI converters and extractors in its `src/` tree, Kotor.NET ships a multi-project solution plus explicit resource-type and model-loading code, and xoreos-docs, phaethon, and bioware-kaitai-formats remain useful cross-check repositories for file-format and archive work. [[`xoreos-tools/src`](https://github.com/xoreos/xoreos-tools/tree/master/src), [`Kotor.NET.sln`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET.sln), [`Kotor.NET/Common/Data/ResourceType.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Common/Data/ResourceType.cs), [`Kotor.NET.Graphics/KotorModelLoader.cs`](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET.Graphics/KotorModelLoader.cs), [`xoreos-docs/specs`](https://github.com/xoreos/xoreos-docs/tree/master/specs), [`phaethon/src/aurora/erffile.h`](https://github.com/xoreos/phaethon/blob/master/src/aurora/erffile.h), [upstream `OpenKotOR/bioware-kaitai-formats`](https://github.com/OpenKotOR/bioware-kaitai-formats)]
- **OpenKotOR-side companion tools:** KotorMCP's `src/kotormcp/tools/` tree currently exposes archive, conversion, discovery, gamedata, installation, module, reference, script, walkmesh, and writing modules; ToolsetData currently publishes only `available_kits.json` plus a `kits/` tree at the repository root; HoloPazaak ships a concrete `src/holopazaak` package; and KOTORMax exposes its MaxScript entrypoint plus plugin, script, name, and conversion subtrees under `KOTORMax/`. [[`KotorMCP/src/kotormcp/tools`](https://github.com/OpenKotOR/KotorMCP/tree/master/src/kotormcp/tools), [`ToolsetData` repository root](https://github.com/NickHugi/ToolsetData/tree/master), [`HoloPazaak/src/holopazaak`](https://github.com/OpenKotOR/HoloPazaak/tree/master/src/holopazaak), [`KOTORMax/KOTORMax`](https://github.com/OpenKotOR/KOTORMax/tree/master/KOTORMax)]
- **Save-editor lineage and related asset tools:** SotOR is a Rust save editor repository, the Fair-Strides KotOR-Save-Editor repository contains a `kse.pl` entry script plus packaged assets and distro folders, and kotorblender keeps its Blender add-on under `io_scene_kotor`. [[SotOR README](https://github.com/StarfishXeno/sotor/blob/master/README.md), [`SotOR/Cargo.toml`](https://github.com/StarfishXeno/sotor/blob/master/Cargo.toml), [`KotOR-Save-Editor` repository root](https://github.com/Fair-Strides/KotOR-Save-Editor/tree/main), [`KotOR-Save-Editor/kse.pl`](https://github.com/Fair-Strides/KotOR-Save-Editor/blob/main/kse.pl), [`kotorblender/io_scene_kotor`](https://github.com/seedhartha/kotorblender/tree/master/io_scene_kotor)]

### See also

- [Concepts](Concepts)
- [Resource formats and resolution](Resource-Formats-and-Resolution)
- [Installing Mods with HoloPatcher](HoloPatcher#installing-mods)
- [Mod Creation Best Practices](Mod-Creation-Best-Practices)
- [Reverse Engineering Findings](reverse_engineering_findings)
