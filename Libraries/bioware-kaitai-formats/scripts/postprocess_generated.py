#!/usr/bin/env python3
"""Post-process Kaitai-generated Python: relative imports and URL scrub."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Reuse bioware_type_ids docstring swap from PyKotor strip script (URL-free).
BIOWARE_TYPE_IDS_OLD = '''    """This file provides **exhaustive enum mappings** for resource/type identifiers used across
    BioWare-family games and their tooling ecosystems.
    
    Why two enums?
    - `xoreos_file_type_id` mirrors `https://github.com/xoreos/xoreos/blob/master/src/aurora/types.h` (`enum FileType`) and is the
      canonical set of **engine-facing** numeric type IDs found in archives (KEY/BIF/ERF/RIM, etc).
    - `bioware_resource_type_id` mirrors `https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py` (`class ResourceType`)
      and includes additional **toolset-only** IDs (e.g. XML/JSON abstractions).
    
    Important notes:
    - **Duplicates / aliases** exist in upstream definitions (e.g., `DFT`/`DTF` share `2045`,
      `FXR`/`FXT` share `22033`). Kaitai enums cannot represent multiple names for the same numeric key,
      so this file keeps a single canonical name per value.
    - **Conflicts between ecosystems** exist: PyKotor assigns `25015` to `wav_deob` for toolset use,
      while xoreos uses `25015` for `pck` (Dragon Age II). Keeping the enums separate preserves both.
    
    References:
    - https://github.com/xoreos/xoreos/blob/master/src/aurora/types.h
    - https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/resource/type.py
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

INIT_SOURCE_REPLACEMENT = (
    "Upstream: OldRepublicDevs/bioware-kaitai-formats ``.ksy`` specs; see package README for regeneration.\n"
)


def rewrite_relative_imports(root: Path) -> int:
    local_mods = {
        p.stem
        for p in root.glob("*.py")
        if p.name != "__init__.py"
    }
    import_re = re.compile(r"^import ([a-zA-Z_][a-zA-Z0-9_]*)\s*(#.*)?$", re.MULTILINE)
    n = 0
    for path in sorted(root.glob("*.py")):
        if path.name == "__init__.py":
            continue
        text = path.read_text(encoding="utf-8")
        original = text

        def repl(m: re.Match[str]) -> str:
            mod = m.group(1)
            comment = m.group(2) or ""
            if mod == "kaitaistruct" or mod in {"enum", "typing", "struct", "json", "io", "os", "sys"}:
                return m.group(0)
            if mod in local_mods:
                return f"from . import {mod}{comment}"
            return m.group(0)

        text = import_re.sub(repl, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            n += 1
    return n


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


def strip_urls(path: Path) -> bool:
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


def postprocess(root: Path) -> None:
    n_rel = rewrite_relative_imports(root)
    n_strip = 0
    for path in sorted(root.glob("*.py")):
        if strip_urls(path):
            n_strip += 1
    print(f"postprocess: relative-import files={n_rel}, url-scrub files={n_strip}")


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    if root is None or not root.is_dir():
        print("usage: postprocess_generated.py PATH_TO/bioware_kaitai_formats", file=sys.stderr)
        sys.exit(1)
    postprocess(root)


if __name__ == "__main__":
    main()
