#!/usr/bin/env python3
"""Insert pre-rewrite 'Verbatim…' intro (from git HEAD) after H1 in archive pages that lost it."""

from __future__ import annotations

import subprocess

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def head_body(rel: str) -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:{0}".format(rel)],
        cwd=str(REPO),
        text=True,
        stderr=subprocess.DEVNULL,
    )


def extract_intro(old: str) -> list[str]:
    lines = old.splitlines()
    if not lines:
        return []
    out: list[str] = []
    i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and not lines[i].startswith("```"):
        out.append(lines[i])
        i += 1
    return out


def main() -> int:
    wiki = REPO / "wiki"
    fixed = 0
    for path in sorted(wiki.glob("reverse_engineering_findings_*github_urls_pre_scrub.md")):
        rel = "wiki/{0}".format(path.name)
        try:
            old = head_body(rel)
        except subprocess.CalledProcessError:
            continue
        intro = extract_intro(old)
        if not intro or not any("Verbatim" in x for x in intro):
            continue
        cur = path.read_text(encoding="utf-8")
        if "Verbatim lines removed" in cur:
            continue
        lines = cur.splitlines()
        if not lines or not lines[0].startswith("# "):
            continue
        new_lines = [lines[0], ""] + intro + [""] + lines[1:]
        path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print("fixed intro {0}".format(path.name))
        fixed += 1
    ifo = wiki / "reverse_engineering_findings_generics_ifo_init_url_comments_pre_scrub.md"
    if ifo.exists():
        rel = "wiki/{0}".format(ifo.name)
        try:
            old = head_body(rel)
        except subprocess.CalledProcessError:
            return 0
        intro = extract_intro(old)
        cur = ifo.read_text(encoding="utf-8")
        if intro and "Verbatim" not in cur and any("Verbatim" in x for x in intro):
            lines = cur.splitlines()
            if lines and lines[0].startswith("# "):
                new_lines = [lines[0], ""] + intro + [""] + lines[1:]
                ifo.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                print("fixed intro {0}".format(ifo.name))
                fixed += 1
    print("done, {0} files".format(fixed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
