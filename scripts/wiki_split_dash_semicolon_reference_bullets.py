#!/usr/bin/env python3
"""Split `- citation; citation` lines when semicolons separate reference clauses.

Only transforms a line if it starts with `- ` and matches REF_SEP (next token is a
link or known vendor word). **Broad:** can touch any top-level `- ` bullet in the
wiki—run on a clean tree and review the diff before committing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

REF_SEP = re.compile(
    r"; (?=\[|`|PyKotor\b|reone\b|Kotor\.NET\b|KotOR\.js\b|xoreos\b|Torlack\b|entry serialization\b)"
)

DASH = re.compile(r"^(- )(.+)$")


def transform_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = DASH.match(raw)
    if not m:
        return None, False
    prefix, body = m.group(1), m.group(2)
    if not REF_SEP.search(body):
        return None, False
    parts = [p.strip() for p in REF_SEP.split(body) if p.strip()]
    if len(parts) < 2:
        return None, False
    out = [f"{prefix}{p}" for p in parts]
    return out, True


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        repl, ch = transform_line(line)
        if ch and repl is not None:
            out.extend(repl)
            changed = True
        else:
            out.append(line)
    if changed:
        path.write_text("\n".join(out) + ("\n" if text.endswith("\n") else ""), encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    n = 0
    for path in sorted(WIKI.rglob("*.md")):
        if process_file(path):
            n += 1
            print(path.relative_to(ROOT))
    print(f"dash semicolon reference split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
