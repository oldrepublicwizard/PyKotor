# PyKotor Documentation Index

Complete guide to PyKotor documentation, organized by topic and audience.

## Knowledgebase navigation (agents & contributors)

**Start here for implementation and debugging:**

1. **[STRATEGY.md](STRATEGY.md)** — product intent, metrics, active tracks
2. **[AGENTS.md](AGENTS.md)** — KB map, canonical pytest command, tool gotchas
3. **[docs/plans/](docs/plans/)** — active execution plans
4. **[docs/solutions/](docs/solutions/)** — validated learnings (YAML frontmatter)
5. **[wiki/](wiki/)** — public format and RE specifications
6. **[docs/](docs/)** — implementation deep dives (e.g. [TSLPatchData index](docs/INDEX.md))

## Quick Navigation

### Getting Started

- **[README.md](README.md)** — Project overview, installation, quick start
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute (includes scoped pytest)
- **[AGENTS.md](AGENTS.md)** — Agent runbook and test commands

### Design & Architecture

- **[FIGMA_INTEGRATION_SUMMARY.md](FIGMA_INTEGRATION_SUMMARY.md)** — Figma integration overview
- **[FIGMA_DIAGRAMS.md](FIGMA_DIAGRAMS.md)** — Architectural diagrams
- **[Design System Rules](.cursor/rules/design_system_rules.md)** — UI design system
- **[Code Connect Examples](FIGMA_CODE_CONNECT_EXAMPLES.md)** — Figma-to-code mappings

### Development

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines
- **[CONVENTIONS.md](CONVENTIONS.md)** — Code conventions
- **[POWERSHELL.md](POWERSHELL.md)** — PowerShell setup for Windows

### Reference Documentation

- **[PyKotor Library Docs](Libraries/PyKotor/docs/)** — Core library API documentation
- **[Project Wiki](https://github.com/OpenKotOR/PyKotor/wiki)** — Community documentation
- **[File Format Documentation](wiki/)** — In-tree game file format specifications

### Validated learnings (solutions)

| Topic | Doc |
|-------|-----|
| BWM / walkmesh authority | [docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md](docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md) |
| Save/load engine parity | [docs/solutions/logic-errors/kotor-save-load-1-1-python-from-re.md](docs/solutions/logic-errors/kotor-save-load-1-1-python-from-re.md) |
| TSLPatcher parity harness | [docs/solutions/testing/tslpatcher-parity-harness-mvp.md](docs/solutions/testing/tslpatcher-parity-harness-mvp.md) |

### Tool-Specific Documentation

- **[HolocronToolset](Tools/HolocronToolset/README.md)** — GUI editor suite
- **[HoloPatcher](Tools/HoloPatcher/README.md)** — Mod installer
- **[KotorDiff](Tools/KotorDiff/README.md)** — Diff tool
- **[BatchPatcher](Tools/BatchPatcher/README.md)** — Batch processing
- **[HoloPazaak](Tools/HoloPazaak/README.md)** — Pazaak game

---

## By Audience

### For New Developers

1. Read [README.md](README.md) for project overview
2. Follow [CONTRIBUTING.md](CONTRIBUTING.md) for environment and test commands
3. Use [AGENTS.md](AGENTS.md) for scoped pytest and Linux gotchas
4. Check [FIGMA_DIAGRAMS.md](FIGMA_DIAGRAMS.md) for architecture context

### For Contributors

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) first
2. Follow [CONVENTIONS.md](CONVENTIONS.md) for code style
3. Reference [AGENTS.md](AGENTS.md) for CI-aligned test commands
4. Check [docs/solutions/](docs/solutions/) before changing documented areas

### For AI Assistants

1. Read [AGENTS.md](AGENTS.md) KB map and pytest block
2. Consult [STRATEGY.md](STRATEGY.md) for metric-linked paths
3. Check [docs/solutions/](docs/solutions/) for prefer/defer/avoid in documented domains
4. Follow [Design System Rules](.cursor/rules/design_system_rules.md) for Holocron UI work

---

## Quick Reference

### Essential test command

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  --ignore=Libraries/PyKotor/tests/resource/formats/test_mdl_ascii.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_registry_strict_typing.py \
  --ignore=Libraries/PyKotor/tests/test_utility/test_file_dialog_components.py \
  Libraries/PyKotor/tests
```

Parity harness smoke:

```bash
QT_QPA_PLATFORM=offscreen uv run pytest --import-mode=importlib -m "not gui and not slow" --timeout=120 \
  Libraries/PyKotor/tests/tslpatcher/parity/test_parity_harness.py -v
```

### Essential file locations

```
PyKotor/
├── STRATEGY.md             # Product metrics and tracks
├── AGENTS.md               # Agent KB map + pytest
├── Libraries/PyKotor/      # Core library + tests
├── Tools/                  # Holocron, HoloPatcher, KotorDiff, …
├── docs/plans/             # Execution plans
├── docs/solutions/         # Validated learnings
├── wiki/                   # Format specs
└── pyproject.toml          # Workspace config
```

---

## Removed / relocated paths

These paths are **not** maintained at the locations previously listed here:

- `docs/SETUP.md` — use [CONTRIBUTING.md](CONTRIBUTING.md) and [README.md](README.md)
- `docs/QUICK_START.md` — use [docs/INDEX.md](docs/INDEX.md) (TSLPatchData) and [AGENTS.md](AGENTS.md#tests)

---

**Last Updated**: 2026-05-23
