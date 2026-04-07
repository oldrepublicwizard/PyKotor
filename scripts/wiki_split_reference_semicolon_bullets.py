#!/usr/bin/env python3
"""Split **Reference:** / **References:** one-liners into markdown lists.

Splits on reference-style semicolons (before another link or known vendor clause),
then splits `` a](url) / [`b` `` style PyKotor dual paths. Falls back to
comma-before-[ splits. Skips lines that already yield a single bullet.
"""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

# Body must be on the same line as the header (not already expanded).
REF_HDR = re.compile(r"^(\*\*References?:\*\*)\s+(.+)$")

# Semicolon is a reference separator when the next token looks like a new citation.
REF_SEP = re.compile(
    r"; (?=\[|`|PyKotor\b|reone\b|Kotor\.NET\b|KotOR\.js\b|xoreos\b|Torlack\b|entry serialization\b)"
)


def _split_slash_paths(segment: str) -> list[str]:
    s = segment.strip()
    if " / Kaitai path [`" in s:
        parts = [p.strip() for p in re.split(r" / (?=Kaitai path \[`)", s) if p.strip()]
        if len(parts) >= 2:
            return parts
    if " / [`" not in s and not re.search(r"\]\([^)]+\) / \[", s):
        return [s]
    parts = [p.strip() for p in re.split(r" / (?=\[`)", s) if p.strip()]
    if len(parts) < 2:
        return [s]
    return parts


def _comma_split(body: str) -> list[str] | None:
    if not re.search(r", (?=\[)", body):
        return None
    parts = [p.strip() for p in re.split(r", (?=\[)", body) if p.strip()]
    if len(parts) < 2:
        return None
    if sum(1 for p in parts if "](" in p) < 2:
        return None
    return parts


def expand_reference_body(body: str) -> list[str] | None:
    body = body.strip()
    if not body:
        return None
    segments: list[str] = []
    if REF_SEP.search(body):
        segments = [s.strip() for s in REF_SEP.split(body) if s.strip()]
    else:
        segments = [body]

    out: list[str] = []
    for seg in segments:
        out.extend(_split_slash_paths(seg))

    if len(out) < 2:
        alt = _comma_split(body)
        if alt is not None:
            out = alt
    if len(out) < 2:
        return None
    return out


def transform_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = REF_HDR.match(raw)
    if not m:
        return None, False
    label, body = m.group(1), m.group(2)
    parts = expand_reference_body(body)
    if parts is None:
        return None, False
    out = [label, ""] + [f"- {p}" for p in parts]
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
    print(f"reference semicolon split: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
