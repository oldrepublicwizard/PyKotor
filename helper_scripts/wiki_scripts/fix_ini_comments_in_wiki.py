#!/usr/bin/env python3
"""Replace # comments with ; comments inside ```ini fenced blocks in wiki/*.md.

Run from repository root: python helper_scripts/wiki_scripts/fix_ini_comments_in_wiki.py
"""

from __future__ import annotations

import os
import re

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WIKI_DIR = REPO_ROOT / "wiki"


def fix_ini_comments(content: str) -> str:
    """Replace # comments with ; comments within ```ini blocks."""
    lines = content.split("\n")
    new_lines: list[str] = []
    in_ini_block = False

    for line in lines:
        this_line = line.rstrip()
        if this_line.strip().startswith("```ini"):
            in_ini_block = True
            new_lines.append(this_line)
        elif this_line.strip().startswith("```") and in_ini_block:
            in_ini_block = False
            new_lines.append(this_line)
        elif in_ini_block:
            if re.match(r"^(\s*)# (.+)$", this_line):
                this_line = re.sub(r"^(\s*)# ", r"\1; ", this_line)
            elif "#" in line and not line.strip().startswith("#"):
                this_line = re.sub(r"(\S)\s+# ([^#]+)$", r"\1  ; \2", this_line)
            new_lines.append(this_line)
        else:
            new_lines.append(this_line)

    return "\n".join(new_lines)


def process_wiki_files() -> None:
    """Process all markdown files in the wiki directory."""
    if not WIKI_DIR.is_dir():
        raise SystemExit(f"Wiki directory not found: {WIKI_DIR} (init submodule?)")

    for entry in os.scandir(WIKI_DIR):
        entry_path = Path(entry.path)
        if not entry.is_file():
            print(f"  Skipping {entry_path.name} (not a file)")
            continue
        if entry_path.suffix.lower() != ".md":
            print(f"  Skipping {entry_path.name} (not markdown)")
            continue
        print(f"Processing {entry_path.name}...")
        content = entry_path.read_text(encoding="utf-8")
        new_content = fix_ini_comments(content)
        entry_path.write_text(new_content, encoding="utf-8")
        print(f"  Done: {entry_path.name}")


if __name__ == "__main__":
    process_wiki_files()
