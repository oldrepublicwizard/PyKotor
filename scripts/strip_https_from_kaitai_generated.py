#!/usr/bin/env python3
"""Remove third-party https:// / http:// lines from generated Kaitai Python (docstrings).

Targets ``Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats/``.
Run after ``scripts/rewrite_kaitai_generated_imports.py`` (or use
``Libraries/bioware-kaitai-formats/scripts/postprocess_generated.py`` from the package).

Prefer editing upstream ``.ksy`` long-term so docstrings need less scrubbing.
"""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = (
    Path(__file__).resolve().parent.parent
    / "Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats"
)

INIT_SOURCE_REPLACEMENT = (
    "Upstream: bioware-kaitai-formats (Kaitai `.ksy` specs; community link list: wiki Home.md).\n"
)

# Exact former class docstring (including References block) -> URL-free replacement
BIOWARE_TYPE_IDS_OLD = '''    """This file provides **exhaustive enum mappings** for resource/type identifiers used across
    BioWare-family games and their tooling ecosystems.
    
    Why two enums?
    - `xoreos_file_type_id` mirrors `https://github.com/xoreos/xoreos/blob/master/src/aurora/types.h` (`enum FileType`) and is the
      canonical set of **engine-facing** numeric type IDs found in archives (KEY/BIF/ERF/RIM, etc).
    - `bioware_resource_type_id` mirrors `https://github.com/oldrepublicwizard/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py` (`class ResourceType`)
      and includes additional **toolset-only** IDs (e.g. XML/JSON abstractions).
    
    Important notes:
    - **Duplicates / aliases** exist in upstream definitions (e.g., `DFT`/`DTF` share `2045`,
      `FXR`/`FXT` share `22033`). Kaitai enums cannot represent multiple names for the same numeric key,
      so this file keeps a single canonical name per value.
    - **Conflicts between ecosystems** exist: PyKotor assigns `25015` to `wav_deob` for toolset use,
      while xoreos uses `25015` for `pck` (Dragon Age II). Keeping the enums separate preserves both.
    
    References:
    - https://github.com/xoreos/xoreos/blob/master/src/aurora/types.h
    - https://github.com/oldrepublicwizard/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py
    """'''

BIOWARE_TYPE_IDS_NEW = '''    """This file provides **exhaustive enum mappings** for resource/type identifiers used across
    BioWare-family games and their tooling ecosystems.

    Why two enums?
    - `xoreos_file_type_id` aligns with xoreos ``enum FileType`` (``src/aurora/types.h``) and is the
      canonical set of **engine-facing** numeric type IDs found in archives (KEY/BIF/ERF/RIM, etc).
    - `bioware_resource_type_id` aligns with PyKotor ``class ResourceType`` (``resource/type.py``)
      and includes additional **toolset-only** IDs (e.g. XML/JSON abstractions).

    Important notes:
    - **Duplicates / aliases** exist in upstream definitions (e.g., `DFT`/`DTF` share `2045`,
      `FXR`/`FXT` share `22033`). Kaitai enums cannot represent multiple names for the same numeric key,
      so this file keeps a single canonical name per value.
    - **Conflicts between ecosystems** exist: PyKotor assigns `25015` to `wav_deob` for toolset use,
      while xoreos uses `25015` for `pck` (Dragon Age II). Keeping the enums separate preserves both.
    """'''


def _should_drop_line(line: str) -> bool:
    if "https://" not in line and "http://" not in line:
        return False
    s = line.lstrip()
    if s.startswith("- "):
        return True
    if "Reference:" in line:
        return True
    if re.search(r"Source\s+-\s+https?://", line):
        return True
    if re.match(r"^Reference:\s+https?://", s):
        return True
    return False


def _cleanup_after_strip(text: str) -> str:
    # Remove empty "Reference implementations:" / "References:" blocks before docstring close.
    # Do not use (?:\n[ \t]*)* — it can eat the indentation spaces before closing """.
    text = re.sub(
        r"\n    Reference implementations:\s*\n(?:[ \t]*\n)*(?=\s*\"\"\")",
        "\n",
        text,
    )
    text = re.sub(
        r"\n    References:\s*\n(?:[ \t]*\n)*(?=\s*\"\"\")",
        "\n",
        text,
    )
    text = re.sub(
        r"\n    \.\. seealso::\s*\n(?=\s+\"\"\")",
        "\n",
        text,
    )
    return text


def strip_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    if path.name == "bioware_type_ids.py":
        if BIOWARE_TYPE_IDS_OLD not in raw:
            return False
        new = raw.replace(BIOWARE_TYPE_IDS_OLD, BIOWARE_TYPE_IDS_NEW, 1)
        new = _cleanup_after_strip(new)
        path.write_text(new, encoding="utf-8")
        return True

    lines = raw.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        if path.name == "__init__.py" and line.strip().startswith("Source:") and "https://" in line:
            out.append(INIT_SOURCE_REPLACEMENT)
            continue
        if _should_drop_line(line):
            continue
        out.append(line)
    new = "".join(out)
    new = _cleanup_after_strip(new)
    if new != raw:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> None:
    if not ROOT.is_dir():
        print(f"Missing {ROOT}", file=sys.stderr)
        sys.exit(1)
    n = 0
    for path in sorted(ROOT.glob("*.py")):
        if strip_file(path):
            print("stripped", path.relative_to(ROOT))
            n += 1
    print(f"done: {n} file(s) updated")


if __name__ == "__main__":
    main()
