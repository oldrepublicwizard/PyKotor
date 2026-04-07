#!/usr/bin/env python3
"""Split comma-chained markdown links in GitHub vendor bullets into nested lists.

Targets lines like:
  - **[reone](https://github.com/modawan/reone)**: [`a.cpp`](...), [`b.cpp`](...)
  - **[KotOR.js](https://github.com/...)**: [`x.ts`](...) — [`y`](...), [`z`](...)

Only **comma** + space before the next `` [` `` link is split (not semicolons: those break
parenthetical link pairs).

Skips NSS-style routine lines:
  - **reone:** [`main.cpp`](...
"""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

HEADER_RE = re.compile(
    r"^(- \*\*\[[^\]]+\]\((https://github\.com/[^)]+)\)\*\*)(:\s*|\s+\u2014\s+|\s+--\s+)(.+)$"
)

# NSS routine lines use `- **reone:** [`...` — skip those. Vendor bullets use
# `- **[Label](https://github.com/...)**:` — the `(?!\[)` avoids matching them.
NSS_STYLE = re.compile(r"^- \*\*(?!\[)([^*]+)\*\*:\s*\[`")


def _split_body_on(pattern: str, body: str) -> list[str]:
    parts = re.split(pattern, body.strip())
    if len(parts) < 2:
        return [body]
    out = [p.strip() for p in parts if p.strip()]
    return out if len(out) >= 2 else [body]


def split_body(body: str) -> list[str]:
    """Split comma-separated `` [`...`](url) `` chains.

    Semicolon splitting was removed: it breaks parenthetical pairs like
    ``([`a`], [`b`])`` on DDS/KotOR.js bullets.
    """
    b = body.strip()
    parts = _split_body_on(r", (?=\[`)", b)
    if len(parts) >= 2 and sum(1 for p in parts if "](http" in p) >= 2:
        return parts
    return [body]


def transform_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    if NSS_STYLE.match(raw):
        return None, False
    m = HEADER_RE.match(raw)
    if not m:
        return None, False
    prefix, _gh, _sep, body = m.group(1), m.group(2), m.group(3), m.group(4)
    parts = split_body(body)
    if len(parts) < 2:
        return None, False
    if sum(1 for p in parts if "](http" in p) < 2:
        return None, False
    out_lines = [prefix + ":", ""] + [f"  - {p}" for p in parts]
    return out_lines, True


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
        path.write_text(
            "\n".join(out) + ("\n" if text.endswith("\n") else ""), encoding="utf-8", newline="\n"
        )
    return changed


def main() -> int:
    n = 0
    for path in sorted(WIKI.rglob("*.md")):
        if process_file(path):
            n += 1
            print(path.relative_to(ROOT))
    print(f"github vendor comma split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
