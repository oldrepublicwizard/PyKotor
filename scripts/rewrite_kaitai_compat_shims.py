#!/usr/bin/env python3
"""Regenerate ``pykotor.kaitai_generated`` one-line shims from ``bioware_kaitai_formats`` modules.

Run after adding or renaming Kaitai-generated modules in
``Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats/``.
"""
from __future__ import annotations

from pathlib import Path


def main() -> None:
    repo = Path(__file__).resolve().parent.parent
    src = repo / "Libraries/bioware-kaitai-formats/src/bioware_kaitai_formats"
    dest = repo / "Libraries/PyKotor/src/pykotor/kaitai_generated"
    for p in list(dest.glob("*.py")):
        p.unlink()
    init = dest / "__init__.py"
    init.write_text(
        '"""Backward compatibility: ``pykotor.kaitai_generated`` mirrors ``bioware_kaitai_formats``.\n\n'
        "Prefer ``from bioware_kaitai_formats.MOD import ...`` in new code.\n"
        '"""\n'
        "from __future__ import annotations\n\n"
        "import importlib\n"
        "from typing import Any\n\n\n"
        "def __getattr__(name: str) -> Any:\n"
        '    if name.startswith("_"):\n'
        "        raise AttributeError(name)\n"
        '    return importlib.import_module(f"bioware_kaitai_formats.{name}")\n',
        encoding="utf-8",
    )
    for p in sorted(src.glob("*.py")):
        if p.name == "__init__.py":
            continue
        mod = p.stem
        body = (
            f'"""Shim: use ``bioware_kaitai_formats.{mod}`` directly."""\n'
            f"from bioware_kaitai_formats.{mod} import *  # noqa: F403\n"
        )
        (dest / p.name).write_text(body, encoding="utf-8")
    print("wrote", len(list(dest.glob("*.py"))), "files under", dest)


if __name__ == "__main__":
    main()
