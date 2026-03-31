#!/usr/bin/env python3
"""Split `**Reference:**` one-liners with comma-chained markdown links into bullet lists."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

LINE_RE = re.compile(r"^(\*\*Reference:\*\*) (.+)$")
SPLIT_RE = re.compile(r", (?=\[`)")


def transform_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = LINE_RE.match(raw)
    if not m:
        return None, False
    body = m.group(2).strip()
    parts = [p.strip() for p in SPLIT_RE.split(body) if p.strip()]
    if len(parts) < 2:
        return None, False
    if sum(1 for p in parts if "](http" in p) < 2:
        return None, False
    out = ["**Reference:**", ""] + [f"- {p}" for p in parts]
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
    print(f"reference colon comma split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
