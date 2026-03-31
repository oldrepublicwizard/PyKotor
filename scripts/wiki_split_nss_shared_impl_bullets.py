#!/usr/bin/env python3
"""Split chained implementation links in NSS-Shared-Functions-* hub bullets into nested lists.

- Hub lines: ``- **Label:** body``
- Semicolon + space first (all labels) when the line has 2+ markdown links overall
- Then comma-before-``[`` split (``r', (?=\[)'``) on the hub line when multiple links remain
- Peer bullets at ``  - `` may be comma-split in further passes (same ``](http`` guards)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

# `- **reone:** body` → bold text includes the colon (`**reone:**`).
HUB = re.compile(r"^(- \*\*[^*]+:\*\*)( .+)$")
# Exactly one level of indent under a hub (not `    -`).
PEER = re.compile(r"^(  - )(.+)$")
MD_LINK = re.compile(r"\]\([^)]+\)")


def _split_parts(body: str, sep: str) -> list[str] | None:
    parts = [p.strip() for p in re.split(sep, body) if p.strip()]
    if len(parts) < 2:
        return None
    if sum(1 for p in parts if "](http" in p) < 2:
        return None
    return parts


def transform_hub_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = HUB.match(raw)
    if not m:
        return None, False
    prefix, body = m.group(1), m.group(2).lstrip()
    parts: list[str] | None = None
    if "; " in body:
        cand = [p.strip() for p in body.split("; ") if p.strip()]
        if len(cand) >= 2 and len(MD_LINK.findall(body)) >= 2:
            parts = cand
    if parts is None and re.search(r", (?=\[)", body):
        parts = _split_parts(body, r", (?=\[)")
    if parts is None:
        return None, False
    out = [prefix, ""] + [f"  - {p}" for p in parts]
    return out, True


def transform_peer_comma_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = PEER.match(raw)
    if not m:
        return None, False
    body = m.group(2)
    if not re.search(r", (?=\[)", body):
        return None, False
    parts = _split_parts(body, r", (?=\[)")
    if parts is None:
        return None, False
    out = [f"  - {p}" for p in parts]
    return out, True


def process_lines(lines: list[str]) -> tuple[list[str], bool]:
    out: list[str] = []
    changed = False
    for line in lines:
        repl, ch = transform_hub_line(line)
        if ch and repl is not None:
            out.extend(repl)
            changed = True
            continue
        repl2, ch2 = transform_peer_comma_line(line)
        if ch2 and repl2 is not None:
            out.extend(repl2)
            changed = True
            continue
        out.append(line)
    return out, changed


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    original = list(lines)
    while True:
        lines, changed = process_lines(lines)
        if not changed:
            break
    if lines != original:
        path.write_text("\n".join(lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8", newline="\n")
        return True
    return False


def main() -> int:
    n = 0
    for path in sorted(WIKI.glob("NSS-Shared-Functions-*.md")):
        if process_file(path):
            n += 1
            print(path.relative_to(ROOT))
    print(f"nss shared impl split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
