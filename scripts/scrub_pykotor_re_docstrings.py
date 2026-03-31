"""One-off helper: scrub legacy engine-binary docstring boilerplate under pykotor/."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "Libraries" / "PyKotor" / "src" / "pykotor"


def scrub(content: str) -> str:
    # Typical References block: two redundant lines
    content = re.sub(
        r"^([ \t]*)Original BioWare engine binaries \(from swkotor\.exe, swkotor2\.exe\)\r?\n\1Original BioWare engine binaries\r?\n",
        r"\1Observed retail KotOR I and KotOR II behavior.\n",
        content,
        flags=re.MULTILINE,
    )
    # Bullet variant (e.g. frustum.py)
    content = content.replace(
        "- Original BioWare engine binaries (from swkotor.exe, swkotor2.exe)",
        "- Observed retail KotOR I and KotOR II behavior",
    )
    # Standalone "Original BioWare engine binaries" reference line
    content = re.sub(
        r"^[ \t]*Original BioWare engine binaries[ \t]*\r?\n",
        "",
        content,
        flags=re.MULTILINE,
    )
    return content


def main() -> None:
    for path in sorted(ROOT.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        new = scrub(text)
        if new != text:
            path.write_text(new, encoding="utf-8", errors="replace")


if __name__ == "__main__":
    main()
