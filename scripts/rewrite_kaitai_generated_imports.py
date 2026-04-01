#!/usr/bin/env python3
"""Rewrite flat `import foo` to `from . import foo` for generated ``bioware_kaitai_formats``."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> None:
    root = (
        Path(__file__).resolve().parent.parent
        / "Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats"
    )
    if not root.is_dir():
        print(f"Missing {root} (use bioware-kaitai-formats package)", file=sys.stderr)
        sys.exit(1)
    local_mods = {
        p.stem
        for p in root.glob("*.py")
        if p.name != "__init__.py"
    }
    import_re = re.compile(r"^import ([a-zA-Z_][a-zA-Z0-9_]*)\s*(#.*)?$", re.MULTILINE)

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
            print("updated", path.relative_to(root))


if __name__ == "__main__":
    main()
