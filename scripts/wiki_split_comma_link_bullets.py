#!/usr/bin/env python3
"""Split wiki list items that comma-join multiple [label](url) links into separate bullets.

Only touches lines that:
  - start with '- ' (not '- **' vendor blocks);
  - contain ', [' (comma-space before another markdown link);
  - contain ' -- ' or ' — ' (stub / cross-ref gloss), so we do not split NSS reone lines
    like `...](url), [`Symbol` L1](url)` that lack a gloss separator.
"""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"


def should_split(line: str) -> bool:
    s = line.rstrip()
    if not s.startswith("- "):
        return False
    if s.startswith("- **"):
        return False
    if ", [" not in s:
        return False
    if " -- " not in s and " — " not in s:
        return False
    rest = s[2:]
    if not rest.lstrip().startswith("["):
        return False
    return True


def split_bullet(line: str) -> str:
    s = line.rstrip()
    body = s[2:]
    parts = re.split(r", (?=\[)", body)
    return "\n".join(f"- {p.strip()}" for p in parts)


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        if should_split(line):
            out.extend(split_bullet(line).splitlines())
            changed = True
        else:
            out.append(line)
    if not changed:
        return False
    path.write_text(
        "\n".join(out) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8", newline="\n"
    )
    return True


def main() -> int:
    updated = 0
    for path in sorted(WIKI.rglob("*.md")):
        if process_file(path):
            updated += 1
            print(path.relative_to(ROOT))
    print(f"wiki_split_comma_link_bullets: updated {updated} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
