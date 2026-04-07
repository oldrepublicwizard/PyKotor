#!/usr/bin/env python3
"""Strip vendor/engine narrative blocks from extract/savedata.py (archive must exist in wiki first)."""

from __future__ import annotations

import re

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PATH = REPO / "Libraries/PyKotor/src/pykotor/extract/savedata.py"

NEW_MODULE = '''"""KotOR I/II save-folder model (SAVENFO, GLOBALVARS, PARTYTABLE, SAVEGAME.sav).

Reads and writes the on-disk save layout used by retail KotOR. Long-form vendor comparisons,
engine reimplementation notes, equipment-slot bit values, and method-level vendor essays
previously in this file are **archived** in ``wiki/reverse_engineering_findings_savedata_pre_scrub.py``
(verbatim snapshot) and summarized under *extract/savedata.py* in ``wiki/reverse_engineering_findings.md``.
"""

'''


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    if not text.startswith('"""'):
        raise SystemExit("expected module docstring")
    end = text.index('"""', 3) + 3
    text = NEW_MODULE + text[end:].lstrip("\n")

    # Class-level (4 spaces): VENDOR REFERENCES + ENGINE BEHAVIOR before kept sections
    vr4 = re.compile(
        r"\n    VENDOR REFERENCES:\n    =+\n[\s\S]*?(?=\n    (?:STRUCTURE|BINARY FORMAT|STRUCTURE &|INTERNAL DATA|FILE FORMAT|USAGE:|ATTRIBUTES:|NOTE:|    \"\"\"))",
    )
    eng4 = re.compile(
        r"\n    ENGINE BEHAVIOR:\n    =+\n[\s\S]*?(?=\n    (?:STRUCTURE|BINARY FORMAT|STRUCTURE &|INTERNAL DATA|FILE FORMAT|USAGE:|ATTRIBUTES:|NOTE:))",
    )
    for _ in range(50):
        old = text
        text = vr4.sub("\n", text, count=1)
        text = eng4.sub("\n", text, count=1)
        if old == text:
            break

    # Small class docstrings: VENDOR REF / bullets + optional ENGINE (no ===)
    text = re.sub(
        r"\n    VENDOR REF:[^\n]*\n(?:    - [^\n]*\n)*(?:\n    ENGINE BEHAVIOR:\n(?:    =+\n)?(?:    [^\n]+\n)+)(?=\n    \"\"\"|\n    NOTE:)",
        "\n",
        text,
    )
    text = re.sub(
        r"\n    VENDOR REF:[^\n]*\n(?:    - [^\n]*\n)+(?=\n    \"\"\"|\n    NOTE:)",
        "\n",
        text,
    )

    # GalaxyMapEntry: ENGINE with ==== before NOTE
    text = re.sub(
        r"\n    ENGINE BEHAVIOR:\n    =+\n[\s\S]*?(?=\n    NOTE:)",
        "\n",
        text,
    )

    # Method-level (8 spaces): VENDOR IMPLEMENTATIONS + ENGINE BEHAVIOR -> keep PROCESS / etc.
    combo8 = re.compile(
        r"\n        VENDOR IMPLEMENTATIONS:\n        =+\n[\s\S]*?\n        ENGINE BEHAVIOR:\n        =+\n[\s\S]*?(?=\n        (?:PROCESS:|BOOLEAN|IMPLEMENTATION:|LOAD ORDER|COMPREHENSIVE|FIELD TYPES|Returns:|Args:|USAGE:|NOTE:|\w+ \w+ \w+:))",
    )
    for _ in range(50):
        old = text
        text = combo8.sub("\n", text, count=1)
        if old == text:
            break

    vref8 = re.compile(
        r"\n        VENDOR REFERENCE:\n        =+\n[\s\S]*?\n        ENGINE BEHAVIOR:\n        =+\n[\s\S]*?(?=\n        (?:Returns:|PROCESS:|USAGE:|STATIC|NOTE:))",
    )
    for _ in range(20):
        old = text
        text = vref8.sub("\n", text, count=1)
        if old == text:
            break

    eng_impl8 = re.compile(
        r"\n        ENGINE BEHAVIOR:\n        =+\n[\s\S]*?(?=\n        IMPLEMENTATION:\n)",
    )
    text = eng_impl8.sub("\n", text)

    # SaveInfo __init__ / similar: Vendor Implementation subsection
    text = re.sub(
        r"\n        Vendor Implementation:\n        -+\n[\s\S]*?(?=\n        \"\"\"\n|\n        ident =)",
        "\n",
        text,
    )

    # Collapse excessive blank lines inside docstrings (light touch)
    text = re.sub(r"\n{4,}", "\n\n\n", text)

    PATH.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
