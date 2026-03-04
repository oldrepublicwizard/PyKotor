"""Wiki INI fix: replace # with ; inside ```ini code blocks for valid INI syntax."""

from __future__ import annotations

import os
import re

from pathlib import Path


_MD_BLOCK_START_RE = re.compile(r"^(\s*)```ini", re.IGNORECASE)
_HASH_START_COMMENT_RE = re.compile(r"^(\s*)# (.+)$")
_INLINE_HASH_COMMENT_RE = re.compile(r"(\S)\s+# ([^#]+)$")


def fix_ini_comments(content: str) -> str:
    """Replace # comments with ; comments within ```ini blocks."""
    lines = content.split("\n")
    new_lines: list[str] = []
    in_ini_block = False

    for line in lines:
        this_line = line.rstrip()
        if _MD_BLOCK_START_RE.match(this_line):
            in_ini_block = True
            new_lines.append(this_line)
        elif this_line.strip() == "```" and in_ini_block:
            in_ini_block = False
            new_lines.append(this_line)
        elif in_ini_block:
            # Replace # at start of line (with optional whitespace) with ;
            if _HASH_START_COMMENT_RE.match(this_line):
                this_line = _HASH_START_COMMENT_RE.sub(r"\1; ", this_line)
            # Replace inline # comments (but be careful not to match markdown headers)
            elif "#" in this_line and not this_line.startswith("#"):
                # Replace inline # comments (where # is followed by space and text)
                this_line = _INLINE_HASH_COMMENT_RE.sub(r"\1  ; \2", this_line)
            new_lines.append(this_line)
        else:
            new_lines.append(this_line)

    return "\n".join(new_lines)


def process_wiki_files():
    """Process all markdown files in the wiki directory."""
    wiki_dir = Path("wiki")

    # Use scandir for full case-insensitive .md match (cross platform)
    for entry in os.scandir(wiki_dir):
        entry_path: Path = Path(entry.path)
        if not entry.is_file():
            print(f"  Skipping {entry_path.name} (not a file)")
            continue
        if entry_path.suffix.lower() != ".md":
            print(f"  Skipping {entry_path.name} (not markdown)")
            continue
        print(f"Processing {entry_path.name}...")
        content: str = entry_path.read_text(encoding="utf-8")
        new_content: str = fix_ini_comments(content)

        entry_path.write_text(new_content, encoding="utf-8")

        print(f"  Done: {entry_path.name}")


if __name__ == "__main__":
    process_wiki_files()
