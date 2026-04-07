#!/usr/bin/env python3
"""Expand one-line **For mod developers:** paragraphs into markdown bullet lists."""

from __future__ import annotations

import re
import sys

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"

HDR = "**For mod developers:**"
LINE_RE = re.compile(r"^(\*\*For mod developers:\*\*)\s*(.+)$")


def _bullets(parts: list[str]) -> list[str]:
    out = [HDR, ""]
    for p in parts:
        p = p.strip()
        if not p.endswith("."):
            p += "."
        out.append(f"- {p}")
    return out


def split_see_and_links(sentence: str) -> list[str]:
    """Split 'see [A](u) and [B](v)' into two lines, each starting with See."""
    sentence = sentence.strip()
    parts = re.split(r"\)\s+and\s+(?=\[)", sentence)
    if len(parts) != 2:
        return [sentence]
    left = parts[0].strip() + ")"
    right = parts[1].strip()
    if not left.lower().startswith("see "):
        left = "See " + left
    else:
        left = "See " + left[4:].lstrip()
    if not left.endswith("."):
        left += "."
    if not right.lower().startswith("see "):
        right = "See " + right
    else:
        right = "See " + right[4:].lstrip()
    if not right.endswith("."):
        right += "."
    return [left, right]


def transform_body(body: str) -> list[str] | None:
    body = body.strip()
    if not body:
        return None

    # Multiline hubs: header only introduces a list or "see:" on same line
    if body.endswith("referenced from:"):
        return None
    if body.endswith("See also:"):
        intro = body[: -len("See also:")].strip()
        if not intro.endswith("."):
            intro += "."
        return [HDR, "", f"- {intro}", "", "**See also:**"]
    if body.endswith("; see:"):
        intro = body[: -len("; see:")].strip()
        if not intro.endswith("."):
            intro += "."
        return [HDR, "", f"- {intro}", "", "**See also:**"]

    # TSLPatcher + HoloPatcher (two-sentence form)
    for label in (
        "For general modding information, see ",
        "For general modding, see ",
    ):
        if f". {label}" in body:
            a, b = body.split(f". {label}", 1)
            a = a.strip()
            b = (label + b.strip()).strip()
            if not a.endswith("."):
                a += "."
            if not b.endswith("."):
                b += "."
            return _bullets([a, b])

    # "X. See Y." (DDS)
    if ". See " in body and body.count(". See ") == 1:
        a, b = body.split(". See ", 1)
        a = a.strip()
        b = "See " + b.strip()
        if not a.endswith("."):
            a += "."
        if not b.endswith("."):
            b += "."
        return _bullets([a, b])

    # ERF: *MOD*...; see A and B. Vanilla...
    if body.startswith("*MOD*") and ". Vanilla " in body:
        first, second = body.split(". Vanilla ", 1)
        first = first.strip()
        if "; see " in first:
            mod_part, see_part = first.split("; see ", 1)
            mod_part = mod_part.strip()
            if not mod_part.endswith("."):
                mod_part += "."
            segs = split_see_and_links("see " + see_part.strip())
            bullets = [mod_part]
            bullets.extend(segs)
            van = "Vanilla " + second.strip()
            if not van.endswith("."):
                van += "."
            bullets.append(van)
            return _bullets(bullets)

    # "X; see [A](u) and [B](v)." (VIS, LYT, TXI) — after ERF branch
    if "; see " in body and " and [" in body and ") and [" in body:
        before, after_see = body.split("; see ", 1)
        b0 = before.strip()
        if not b0.endswith("."):
            b0 += "."
        segs = split_see_and_links("see " + after_see.strip())
        return _bullets([b0, *segs])

    # NCS: compile source; see toolset and HoloPatcher (one semicolon)
    if body.startswith("Scripts are compiled"):
        parts = body.split("; ", 1)
        if len(parts) == 2:
            a = parts[0].strip()
            b = parts[1].strip()
            if not a.endswith("."):
                a += "."
            if not b.endswith("."):
                b += "."
            if not b.lower().startswith("see "):
                b = "See " + b[0].upper() + b[1:] if b else b
            return _bullets([a, b])

    # NSS: three clauses
    if body.startswith("NSS compiles"):
        parts = [p.strip() for p in body.split("; ") if p.strip()]
        if len(parts) >= 2:
            fixed = []
            for p in parts:
                if not p.endswith("."):
                    p += "."
                pl = p.lower()
                if pl.startswith("see "):
                    p = "See " + p[4:].lstrip()
                elif pl.startswith("use "):
                    p = "Use " + p[4:].lstrip()
                fixed.append(p)
            return _bullets(fixed)

    # GFF-PTH: ". For Holocron"
    if ". For Holocron" in body:
        a, b = body.split(". For Holocron", 1)
        a = a.strip()
        b = "For Holocron" + b.strip()
        if not a.endswith("."):
            a += "."
        if not b.endswith("."):
            b += "."
        return _bullets([a, b])

    # LYT long paragraph
    if body.startswith("Loading a **layout**") and ". For more on room crossing" in body:
        a, b = body.split(". For more on room crossing", 1)
        a = a.strip()
        if not a.endswith("."):
            a += "."
        b = ("For more on room crossing " + b.strip()).strip()
        if not b.endswith("."):
            b += "."
        return _bullets([a, b])

    # GUI / DLG
    lower = body.lower()
    if "; for mod patches see " in lower:
        idx = lower.index("; for mod patches see ")
        a = body[:idx].strip()
        rest = body[idx + len("; for mod patches see ") :].strip()
        if not a.endswith("."):
            a += "."
        if re.search(r"\)\s+and\s+(?=\[)", rest):
            left, right = re.split(r"\)\s+and\s+(?=\[)", rest, maxsplit=1)
            left = left.strip() + ")"
            right = right.strip()
            if not right.endswith("."):
                right += "."
            return _bullets([a, f"For mod patches, see {left}.", right])

    # LTR
    if "*LTR*" in body and "; see " in body and " and [" not in body:
        a, b = body.split("; see ", 1)
        a = a.strip()
        if not a.endswith("."):
            a += "."
        b = "See " + b.strip()
        if not b.endswith("."):
            b += "."
        return _bullets([a, b])

    return None


def process_line(line: str) -> tuple[list[str] | None, bool]:
    raw = line.rstrip("\r\n")
    m = LINE_RE.match(raw)
    if not m:
        return None, False
    _label, body = m.group(1), m.group(2)
    if not body.strip():
        return None, False
    repl = transform_body(body)
    if repl is None:
        return None, False
    return repl, True


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    changed = False
    for line in lines:
        repl, ch = process_line(line)
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
    print(f"for mod developers normalize: updated {n} files", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
