import os
import re

WIKI = r"c:\GitHub\PyKotor\wiki"


def gh_slug(text):
    # Strip HTML tags (rendered output from markdown)
    text = re.sub(r"<[^>]+>", "", text)
    # Strip markdown links [text](url) -> text (GitHub renders then strips HTML)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Strip markdown images
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Strip bold/italic markers
    text = re.sub(r"\*+", "", text)
    # Strip backticks
    text = re.sub(r"`", "", text)
    text = text.strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


anchor_map = {}
for fname in os.listdir(WIKI):
    if not fname.endswith(".md"):
        continue
    base = fname[:-3]
    anchors = set()
    with open(os.path.join(WIKI, fname), encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.search(r"<a\s+id=['\"]([^'\"]+)['\"]", line)
            if m:
                anchors.add(m.group(1).lower())
            m = re.match(r"^(#{1,6})\s+(.+?)(?:\s*#+\s*)?$", line.rstrip())
            if m:
                anchors.add(gh_slug(m.group(2)))
    anchor_map[base] = anchors

print(f"Indexed {len(anchor_map)} files")

broken = []
for fname in os.listdir(WIKI):
    if not fname.endswith(".md"):
        continue
    with open(os.path.join(WIKI, fname), encoding="utf-8", errors="replace") as f:
        content = f.read()
    for m in re.finditer(r"\]\(([^)#\s]+)#([^)\s]+)\)", content):
        tgt, anc = m.group(1), m.group(2).lower()
        if re.match(r"https?://", tgt):
            continue
        if tgt not in anchor_map:
            broken.append(f"FILE_MISSING: {fname} -> {tgt}#{anc}")
        elif anc not in anchor_map[tgt]:
            broken.append(f"ANCHOR_MISSING: {fname} -> {tgt}#{anc}")

broken = sorted(set(broken))
print(f"Broken: {len(broken)}")
for b in broken:
    print(b)
