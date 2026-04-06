# PyKotorCLI Quick Start Guide

## Installation

```bash
# With uv (recommended)
uvx pykotor --help

# Without uv: from repo root, with activated venv
cd PyKotor
python -m pip install -e Libraries/PyKotor
```

## 5-Minute Tutorial

### 1. Create a new project

```bash
python -m pykotor init mymod
cd mymod
```

This creates:

- `PyKotorCLI.cfg` - Configuration file
- `src/` - Source directory structure
- `.gitignore` - Git ignore file
- `.PyKotorCLI/` - Local config directory

### 2. Unpack an existing module (optional)

```bash
uvx PyKotor unpack --file ~/path/to/mymodule.mod
```

This extracts all files from the module into your `src/` directory, converting GFF files to JSON format.

### 3. View your targets

```bash
uvx PyKotor list  # or python -m PyKotor list
```

Shows all configured targets in your `PyKotorCLI.cfg`.

### 4. Make changes

Edit files in the `src/` directory:

- Scripts: `src/scripts/*.nss`
- Dialogs: `src/dialogs/*.dlg.json`
- Creatures: `src/blueprints/creatures/*.utc.json`
- Areas: `src/areas/*.git.json`, `*.are.json`
- etc.

### 5. Pack your module

```bash
uvx PyKotor pack
```

This will:

1. Convert JSON files to GFF
2. Compile NWScript files
3. Pack everything into a module file

### 6. Install and test

```bash
uvx PyKotor install
```

This installs the packed module to your KOTOR directory.

Or launch the game directly:

```bash
uvx PyKotor play
```

### 7. Diff installs/files with KotorDiff (headless or GUI)

Headless CLI (preferred for automation):

```bash
uvx --refresh pykotor diff --path1 "C:\Games\KOTOR" --path2 "C:\Games\KOTOR_Modded" --filter tat_m17ac --output-mode normal
# Generate incremental TSLPatcher data while diffing
uvx --refresh pykotor diff --path1 "C:\Games\KOTOR" --path2 "C:\Games\KOTOR_Modded" --tslpatchdata .\tslpatchdata --incremental
```

GUI (omit paths or pass `--gui`):

```bash
uvx --refresh kotordiff
```

### 8. Rebuild walkmesh (WOK/DWK/PWK)

From repo root, regenerate AABB/adjacency/perimeter from geometry (prefix fixed; do not change):

```bash
uvx --with-editable Libraries/PyKotor --from . pykotor walkmesh-rebuild "path/to/area.wok" -o "path/to/area_rebuilt.wok"
uvx --with-editable Libraries/PyKotor --from . pykotor walkmesh-rebuild --help
```

Compare original vs rebuilt (semantic):

```bash
uvx --with-editable Libraries/PyKotor --from . pykotor diff "path/to/original.wok" "path/to/rebuilt.wok"
```

## Common Workflows

### Starting from scratch

```bash
uvx PyKotor init mynewmod
cd mynewmod
# Create/edit source files
uvx PyKotor pack
```

### Working with an existing module

```bash
uvx PyKotor init mynewmod
cd mynewmod
uvx PyKotor unpack --file ~/modules/existing.mod
# Edit source files
uvx PyKotor install
```

### Testing changes quickly

```bash
uvx PyKotor play
```

This runs convert, compile, pack, install, and launches the game in one command.

### Building multiple targets

```toml
# In PyKotorCLI.cfg
[target]
name = "demo"
file = "demo.mod"

[target]
name = "full"
file = "full.mod"
```

```bash
uvx PyKotor pack all        # Build all targets
uvx PyKotor pack demo       # Build specific target
uvx PyKotor install full    # Install specific target
```

## Configuration

### Global settings

```bash
# Set script compiler path
uvx PyKotor config --global nssCompiler /path/to/nwnnsscomp

# Set KOTOR install directory
uvx PyKotor config --global installDir ~/Documents/KotOR

# List all settings
uvx PyKotor config --list --global
```

### Local (per-project) settings

```bash
uvx PyKotor config --local modName "My Awesome Mod"
uvx PyKotor config --list --local
```

## Tips & Tricks

### Use version control

```bash
cd mymod
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/mymod
git push -u origin main
```

### Clean builds

```bash
uvx PyKotor pack --clean
```

Clears the cache before building.

### Skip steps

```bash
uvx PyKotor pack --noConvert    # Don't convert JSON
uvx PyKotor pack --noCompile    # Don't compile scripts
uvx PyKotor install --noPack    # Just install existing file
```

### Compile specific files

```bash
uvx PyKotor compile --file myscript.nss
```

### Verbose output

```bash
uvx PyKotor pack --verbose
uvx PyKotor pack --debug
```

### Quiet mode

```bash
uvx PyKotor pack --quiet
```

## Next Steps

- Read the [README.md](README.md) for full command documentation
- Check [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) for technical details
- See [PyKotorCLI.cfg examples](https://github.com/squattingmonk/cli#clicfg) (cli-compatible)

## Getting Help

```bash
uvx PyKotor --help
uvx PyKotor <command> --help
```

For issues or questions, visit the [PyKotor repository](https://github.com/OpenKotOR/PyKotor).
