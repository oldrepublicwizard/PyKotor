# bioware-kaitai-formats

Installable Python package containing **Kaitai Struct**–generated parsers for BioWare / KotOR binary and text-derived formats.

Canonical **`.ksy` specifications** live in the upstream repository: [KotORPublicDomain/bioware-kaitai-formats](https://github.com/KotORPublicDomain/bioware-kaitai-formats). This PyKotor workspace copy vendors the **generated Python** under `src/bioware_kaitai_formats/` so consumers (PyKotor, KotorBlender, etc.) depend on this package instead of copying parsers into each project.

## Install

From the PyKotor monorepo (workspace):

```bash
uv sync --all-packages --all-extras
```

From PyPI (once published):

```bash
pip install bioware-kaitai-formats
```

## Regenerating Python from `.ksy`

1. Clone or sync the upstream spec tree (for example `vendor/bioware-kaitai-formats` with all `.ksy` files).
2. Install a [Kaitai Struct compiler](https://kaitai.io/#download) (0.11.x matches this tree).
3. Run:

```bash
uv run python scripts/regenerate_python.py --ksy-root PATH_TO_KSY_DIR
```

Optional:

- `--ksc` — path to `kaitai-struct-compiler` (or `.bat` on Windows); otherwise `kaitai-struct-compiler` must be on `PATH`.
- `--repo-root` — root of this package (defaults to the directory containing `pyproject.toml`).

The script compiles into `src/bioware_kaitai_formats/`, then runs post-processing (relative imports, URL scrub) so the tree matches packaging expectations.

## Versioning

Keep this package version aligned with PyKotor releases when wire layouts change. Patch bumps for regenerated-only updates; minor bumps when new specs are added.

## Publishing to PyPI

Before uploading a new **pykotor** release that lists `bioware-kaitai-formats>=0.1.0`, publish this package (same version or compatible range) to PyPI so plain `pip install pykotor` resolves the dependency. Monorepo consumers continue to use the workspace member via `uv sync`.
