"""Remove inline executable cross-reference comments from ASCII BWM I/O (one-off cleanup)."""

from __future__ import annotations

import re

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "Libraries/PyKotor/src/pykotor/resource/formats/bwm/io_bwm_ascii.py"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    drop = re.compile(
        r"^\s*# Reference:.*(?:swkotor|0x005|0x004|LoadMeshText|FUN_0)",
        re.IGNORECASE,
    )
    out = [ln for ln in lines if not drop.match(ln)]
    TARGET.write_text("".join(out), encoding="utf-8")
    print("stripped", TARGET)


if __name__ == "__main__":
    main()
