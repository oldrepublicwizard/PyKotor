from __future__ import annotations

import os
import re


def read_file(fname: str) -> str:
    try:
        return open(fname, encoding="utf-8").read()
    except Exception:
        return open(fname, encoding="latin-1").read()


def write_file(fname: str, content: str) -> None:
    with open(fname, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def fix_wrong_keys(text: str) -> str:
    # Table header "| key |" used as column headers, not the KEY file format
    text = re.sub(r"(\|\s*)\[KEY\]\(Container-Formats#key\)(\s*\|)", r"\1key\2", text)
    # "key format |" column header
    text = text.replace("[KEY](Container-Formats#key) format |", "key format |")
    # "the key:" key-value pair context
    text = text.replace("the [KEY](Container-Formats#key):", "the key:")
    # "key Rules Summary" - "key" as in primary/important
    text = text.replace("[KEY](Container-Formats#key) Rules", "key Rules")
    # "folder key" - dictionary key concept
    text = text.replace("folder [KEY](Container-Formats#key)", "folder key")
    # "ReplaceFile key" - config key concept
    text = text.replace("ReplaceFile [KEY](Container-Formats#key)", "ReplaceFile key")
    # "[edge](...) Cases" - edge cases, not WoK edge
    text = text.replace("[edge](Level-Layout-Formats#edges-wok-only) Cases", "edge Cases")
    # "R key", "F key", etc. - keyboard keys
    text = re.sub(r"\b([A-Z]) \[KEY\]\(Container-Formats#key\)\b", r"\1 key", text)
    # "time key" - animation keyframe
    text = text.replace("time [KEY](Container-Formats#key)", "time key")
    # "Cannot parse 'key=value'" - literal syntax
    text = text.replace("parse '[KEY](Container-Formats#key)=value'", "parse 'key=value'")
    return text


def resolve_conflict(head: str, remote: str) -> str:
    head, remote = head.strip(), remote.strip()
    if head == remote:
        return remote
    if not head:
        return fix_wrong_keys(remote)
    if not remote:
        return head

    # Keyboard/animation key mislinks in remote - keep HEAD
    if re.search(r"\b[A-Z] \[KEY\]\(Container-Formats#key\)", remote):
        return head
    if "time [KEY](Container-Formats#key)" in remote:
        return head

    # Table header key: | key | → keep HEAD
    if re.search(r"\|\s*\[KEY\]\(Container-Formats#key\)\s*\|", remote) and re.search(r"\|\s*key\s*\|", head):
        return head

    # "the key:" key-value pair → keep HEAD
    if "the [KEY](Container-Formats#key):" in remote and "the key:" in head:
        return head

    # "key Rules Summary" → keep HEAD
    if "[KEY](Container-Formats#key) Rules" in remote and "key Rules" in head:
        return head

    # Folder key, ReplaceFile key → keep HEAD
    if "folder [KEY](Container-Formats#key)" in remote and "folder key" in head:
        return head
    if "ReplaceFile [KEY](Container-Formats#key)" in remote and "ReplaceFile key" in head:
        return head

    # Edge cases wrongly linked → keep HEAD
    if "[edge](Level-Layout-Formats#edges-wok-only) Cases" in remote:
        return head

    # "parse 'key=value'" syntax error → keep HEAD
    if "parse '[KEY](Container-Formats#key)=value'" in remote:
        return head

    # Default: use REMOTE (more comprehensive reorganization) with wrong-KEY fixes
    return fix_wrong_keys(remote)


def resolve_file(fname: str) -> tuple[str, int]:
    content = read_file(fname)
    pattern = r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> \S+\n"
    conflicts = list(re.finditer(pattern, content, re.DOTALL))
    if not conflicts:
        return content, 0
    result = content
    for m in reversed(conflicts):
        resolved = resolve_conflict(m.group(1), m.group(2)) + "\n"
        result = result[: m.start()] + resolved + result[m.end() :]
    return result, len(conflicts)


files = [
    "docs/archive/TSLPatcher_Thread_Complete.md",
    "wiki/2DA-File-Format.md",
    "wiki/Bioware-Aurora-Items-Economy-and-Narrative.md",
    "wiki/Concepts.md",
    "wiki/GFF-File-Format.md",
    "wiki/Holocron-Toolset-Core-Resources.md",
    "wiki/Home.md",
    "wiki/Indoor-Map-Builder-User-Guide.md",
    "wiki/Kit-Structure-Documentation.md",
    "wiki/KotorDiff-Integration.md",
    "wiki/MDL-MDX-File-Format.md",
    "wiki/NSS-File-Format.md",
    "wiki/TSLPatcher's-Official-Readme.md",
    "wiki/TSLPatcher-2DAList-Syntax.md",
    "wiki/TSLPatcher-GFFList-Syntax.md",
    "wiki/TSLPatcher-HACKList-Syntax.md",
    "wiki/TSLPatcher-InstallList-Syntax.md",
    "wiki/TSLPatcher-SSFList-Syntax.md",
    "wiki/TSLPatcher-TLKList-Syntax.md",
]

for fname in files:
    if not os.path.exists(fname):
        print(f"SKIP (missing): {fname}")
        continue
    resolved, count = resolve_file(fname)
    if count > 0:
        write_file(fname, resolved)
        print(f"RESOLVED {count}: {fname}")
    else:
        print(f"NO CONFLICTS: {fname}")

print("Done.")
