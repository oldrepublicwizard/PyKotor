#!/usr/bin/env python3
"""Split `reone / KotOR.js / Kotor.NET` slash bullets in 2DA-iprp stubs into separate lines."""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

TRIPLE = re.compile(
    r"^(- )\*\*\[reone\]\(([^)]+)\)\*\* / \*\*\[KotOR\.js\]\(([^)]+)\)\*\* / "
    r"\*\*\[Kotor\.NET\]\(([^)]+)\)\*\*( .*)$",
)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        m = TRIPLE.match(line)
        if m:
            pre, u1, u2, u3, tail = m.groups()
            out.append(f"{pre}**[reone]({u1})**{tail}")
            out.append(f"{pre}**[KotOR.js]({u2})**{tail}")
            out.append(f"{pre}**[Kotor.NET]({u3})**{tail}")
            changed = True
        else:
            out.append(line)
    if changed:
        path.write_text(
            "\n".join(out) + ("\n" if text.endswith("\n") else ""), encoding="utf-8", newline="\n"
        )
    return changed


def main() -> int:
    n = 0
    for path in sorted(WIKI.glob("2DA-iprp*.md")):
        if process_file(path):
            n += 1
            print(path.relative_to(ROOT))
    print(f"2da iprp triple vendor split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
