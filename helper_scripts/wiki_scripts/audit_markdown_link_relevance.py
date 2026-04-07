#!/usr/bin/env python3
"""Audit markdown hyperlink quality across repository documentation.

This script complements broken-link validation by flagging low-signal hyperlinks
that are likely to be irrelevant, underspecified, or hard for readers to audit.

The intent is not to prove semantics automatically. Instead, it catches the most
common weak-link patterns so maintainers can keep links descriptive and relevant.
"""

from __future__ import annotations

import argparse
import re

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ROOT_MARKDOWN_FILES = {
    "AGENTS.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "DOCUMENTATION_INDEX.md",
    "NEW_FEATURES_GUIDE.md",
    "README.md",
}
ROOT_MARKDOWN_DIRS = {
    ".github",
    "docs",
    "wiki",
}
IGNORED_PATH_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "Tools/_HolocronToolset_backup",
    "vendor",
}
GENERIC_LINK_TEXT = {
    "click here",
    "docs",
    "documentation",
    "here",
    "link",
    "more",
    "read more",
    "source",
    "this",
    "website",
}
MARKDOWN_LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)"]+)(?:\s+"[^"]*")?\)')
FENCE_RE = re.compile(r"^```")
LIST_ITEM_RE = re.compile(r"^(?:[-*+]\s+|\d+\.\s+)")


@dataclass(frozen=True)
class WarningRecord:
    file_path: Path
    line_number: int
    link_text: str
    link_url: str
    message: str


def iter_markdown_files() -> list[Path]:
    """Return repo markdown files that should be audited."""
    files: list[Path] = []

    for file_name in ROOT_MARKDOWN_FILES:
        file_path = REPO_ROOT / file_name
        if file_path.exists():
            files.append(file_path)

    for dir_name in ROOT_MARKDOWN_DIRS:
        root_dir = REPO_ROOT / dir_name
        if not root_dir.exists():
            continue
        for file_path in root_dir.rglob("*.md"):
            rel_path = file_path.relative_to(REPO_ROOT).as_posix()
            if any(part in rel_path for part in IGNORED_PATH_PARTS):
                continue
            files.append(file_path)

    return sorted(set(files))


def is_external_link(link_url: str) -> bool:
    parsed = urlparse(link_url)
    return parsed.scheme in {"http", "https"}


def normalize_link_text(link_text: str) -> str:
    normalized = re.sub(r"\s+", " ", link_text).strip().lower()
    normalized = normalized.strip("`*_ ")
    return normalized


def is_descriptive_link_text(link_text: str) -> bool:
    normalized = normalize_link_text(link_text)
    if not normalized:
        return False
    if normalized in GENERIC_LINK_TEXT:
        return False
    if "/" in normalized:
        return True
    words = [word for word in re.split(r"\s+", normalized) if word]
    if len(words) >= 2:
        return True
    return len(normalized) >= 12


def strip_markdown_links(line_text: str) -> str:
    return MARKDOWN_LINK_RE.sub("", line_text)


def has_non_link_context(line_text: str) -> bool:
    stripped = strip_markdown_links(line_text).strip()
    stripped = LIST_ITEM_RE.sub("", stripped)
    stripped = stripped.strip("-:;| ")
    return bool(stripped)


def collect_warnings(file_path: Path) -> list[WarningRecord]:
    """Collect hyperlink relevance warnings for one markdown file."""
    warnings: list[WarningRecord] = []
    in_fence = False
    content = file_path.read_text(encoding="utf-8")

    for line_number, line_text in enumerate(content.splitlines(), 1):
        if FENCE_RE.match(line_text.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in MARKDOWN_LINK_RE.finditer(line_text):
            link_text = match.group(1)
            link_url = match.group(2)
            if not is_external_link(link_url):
                continue

            normalized_text = normalize_link_text(link_text)
            if normalized_text in GENERIC_LINK_TEXT:
                warnings.append(
                    WarningRecord(
                        file_path=file_path,
                        line_number=line_number,
                        link_text=link_text,
                        link_url=link_url,
                        message="generic link text; use a title or short descriptive phrase",
                    )
                )

            if (
                LIST_ITEM_RE.match(line_text.strip())
                and not has_non_link_context(line_text)
                and not is_descriptive_link_text(link_text)
            ):
                warnings.append(
                    WarningRecord(
                        file_path=file_path,
                        line_number=line_number,
                        link_text=link_text,
                        link_url=link_url,
                        message="external list link lacks surrounding context; add a short explanation of why it is relevant",
                    )
                )

    return warnings


def audit_markdown_link_relevance() -> list[WarningRecord]:
    """Audit repo markdown files and return all hyperlink relevance warnings."""
    warnings: list[WarningRecord] = []
    for file_path in iter_markdown_files():
        warnings.extend(collect_warnings(file_path))
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit markdown hyperlink relevance across repository documentation."
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit with status 1 when warnings are found.",
    )
    args = parser.parse_args()

    warnings = audit_markdown_link_relevance()
    if warnings:
        print("Hyperlink relevance warnings found:\n")
        for warning in warnings:
            rel_path = warning.file_path.relative_to(REPO_ROOT).as_posix()
            print(
                f"{rel_path}:{warning.line_number}: [{warning.link_text}]({warning.link_url}) - {warning.message}"
            )
        print(f"\nTotal warnings: {len(warnings)}")
        return 1 if args.fail_on_warnings else 0

    print("No hyperlink relevance warnings found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
