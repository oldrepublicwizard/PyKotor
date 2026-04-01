#!/usr/bin/env python3
"""Split reone cross-ref lines that comma-join gff.cpp and gffreader.cpp into nested bullets."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

LINE_RE = re.compile(
    r"^(- \*\*\[reone\]\(https://github\.com/modawan/reone\)\*\*:\s*)"
    r"(\[`gff\.cpp`\]\([^)]+\)),\s*"
    r"(\[`gffreader\.cpp`\]\([^)]+\))\s*"
    r"(\u2014|--)\s*(.+)$"
)


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        m = LINE_RE.match(line)
        if m:
            gff_cpp, gff_reader, tail = m.group(2), m.group(3), m.group(5)
            out.append("- **[reone](https://github.com/modawan/reone)** — " + tail + ":")
            out.append("")
            out.append("  - " + gff_cpp)
            out.append("  - " + gff_reader)
            changed = True
        else:
            out.append(line)
    if changed:
        path.write_text("\n".join(out) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    n = 0
    for path in sorted(WIKI.glob("GFF-*.md")):
        if process_file(path):
            n += 1
            print(path.relative_to(ROOT))
    print(f"wiki_split_reone_gffreader_bullets: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
