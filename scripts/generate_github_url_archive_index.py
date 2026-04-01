"""Generate wiki/reverse_engineering_findings_library_github_url_archives_index.md from archive pages."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
WIKI = ROOT / "wiki"
OUT = WIKI / "reverse_engineering_findings_library_github_url_archives_index.md"

INTRO_RE = re.compile(
    r"Verbatim lines removed from `Libraries/PyKotor/src/pykotor/(.+?)`(?:\s|\)|\.)",
)
TITLE_BT_RE = re.compile(r"^# Archived GitHub URL lines — `(.+?)`\s*$", re.MULTILINE)
TITLE_PLAIN_RE = re.compile(r"^# Archived GitHub URL lines — ([^\n`]+?)\s*$", re.MULTILINE)


def lib_path_from_archive(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    m = INTRO_RE.search(text)
    if m:
        return m.group(1)
    m = TITLE_BT_RE.search(text)
    if m:
        return m.group(1).strip()
    m = TITLE_PLAIN_RE.search(text)
    if m:
        return m.group(1).strip()
    return path.stem


def main() -> None:
    rows: list[tuple[str, str]] = []
    for p in sorted(WIKI.glob("reverse_engineering_findings_*_github_urls_pre_scrub.md")):
        lib = lib_path_from_archive(p)
        rows.append((lib, p.name))

    lines = [
        "# Library GitHub URL line archives (index)",
        "",
        "Verbatim `https://github.com/...` lines removed from hand-maintained modules under "
        "`Libraries/PyKotor/src/pykotor/` (excluding `kaitai_generated/`, which is regenerated from `.ksy`). "
        "Re-scrub one file: `uv run python scripts/archive_github_url_lines.py scrub "
        "<path-from-repo-root> <wiki_filename.md> --title ... --intro ...`. "
        "Bulk scrub: `uv run python scripts/archive_github_url_lines.py batch`.",
        "",
        "| Library path (under `pykotor/`) | Archive |",
        "|----------------------------------|---------|",
    ]
    for lib, name in rows:
        lines.append(f"| `{lib}` | [{name}]({name}) |")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT), "rows", len(rows))


if __name__ == "__main__":
    main()
