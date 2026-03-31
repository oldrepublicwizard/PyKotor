#!/usr/bin/env python3
"""Rewrite wiki GitHub URL archives: canonical upstream permalink, then th3w1zard1 mirror.

Targets `wiki/reverse_engineering_findings_*github_urls_pre_scrub.md` (and optional extra globs)
that cite https://github.com/th3w1zard1/.../tree/....

Skips `reverse_engineering_findings_resource_formats_mdl_io_mdl_github_urls_pre_scrub.md` once migrated.

**Prefer** `uv run python scripts/wiki_th3_canonical_mirror.py` for wiki-wide `th3w1zard1` URL expansion using live `gh api` SHAs.

Run (legacy pre_scrub-only rewrite): `uv run python scripts/rewrite_wiki_th3_mirror_archives.py`
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

WIKI = Path(__file__).resolve().parents[1] / "wiki"

# (mirror_owner, mirror_repo) -> upstream (owner, repo), or None if mirror is the canonical project home
UPSTREAM: Dict[Tuple[str, str], Optional[Tuple[str, str]]] = {
    ("th3w1zard1", "KotOR.js"): ("KobaltBlu", "KotOR.js"),
    ("th3w1zard1", "Kotor.NET"): ("NickHugi", "Kotor.NET"),
    ("th3w1zard1", "kotorblender"): ("OldRepublicDevs", "kotorblender"),
    ("th3w1zard1", "mdlops"): ("ndixUR", "mdlops"),
    ("th3w1zard1", "KotOR-Bioware-Libs"): ("Fair-Strides", "KotOR-Bioware-Libs"),
    ("th3w1zard1", "tga2tpc"): ("ndixUR", "tga2tpc"),
    ("th3w1zard1", "KotOR-dotNET"): ("NickHugi", "Kotor.NET"),
    ("th3w1zard1", "KotOR_IO"): ("Fair-Strides", "KotOR-Bioware-Libs"),
    ("th3w1zard1", "TSLPatcher"): None,
    ("th3w1zard1", "HoloPatcher.NET"): None,
}

# Fallback SHAs when `gh` is unavailable. Prefer `wiki_th3_canonical_mirror.py` + `gh api` for current tips.
STATIC_SHA: Dict[Tuple[str, str], str] = {
    ("KobaltBlu", "KotOR.js"): "ea9491d5c783364cf285f178434b84405bee3608",
    ("th3w1zard1", "KotOR.js"): "0067b672a124bbbdaf4006dd0a5d6c2751523195",
    ("NickHugi", "Kotor.NET"): "6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2",
    ("th3w1zard1", "Kotor.NET"): "6dca4a6a1af2fee6e36befb9a6f127c8ba04d3e2",
    ("OldRepublicDevs", "kotorblender"): "404c42bc4f36b1f60b643eda0cd17c81ba5ca7d4",
    ("th3w1zard1", "kotorblender"): "afae04c9172f30ab765891315d9d11224ab57426",
    ("ndixUR", "mdlops"): "7e40846d36acb5118e2e9feb2fd53620c29be540",
    ("th3w1zard1", "mdlops"): "7e40846d36acb5118e2e9feb2fd53620c29be540",
    ("Fair-Strides", "KotOR-Bioware-Libs"): "90ade1cace418f8e1130c53938d22e8acaa8bc41",
    ("th3w1zard1", "KotOR-Bioware-Libs"): "90ade1cace418f8e1130c53938d22e8acaa8bc41",
    ("ndixUR", "tga2tpc"): "758f3dbd155356408abc36508b1e10fa4a83f22a",
    ("th3w1zard1", "tga2tpc"): "758f3dbd155356408abc36508b1e10fa4a83f22a",
    ("th3w1zard1", "HoloPatcher.NET"): "600630e55e2b6a62e3ed84f8cd84a413baf7795d",
    ("th3w1zard1", "TSLPatcher"): "ad04700a47086c25e1c6ef4b4961f76dfa8cc6a5",
    ("th3w1zard1", "KotOR_IO"): "8788712d037614f342e586b053b4645db19ff7a9",
}

_SHA_CACHE: Dict[Tuple[str, str], str] = {}


def _fetch_default_branch_sha(owner: str, repo: str) -> str:
    key = (owner, repo)
    if key in STATIC_SHA:
        return STATIC_SHA[key]
    if key in _SHA_CACHE:
        return _SHA_CACHE[key]
    raise KeyError("Add STATIC_SHA entry for {0}/{1} in scripts/rewrite_wiki_th3_mirror_archives.py".format(owner, repo))


def _prefetch_shas() -> None:
    """Populate cache from STATIC_SHA; API fallback only for unknown (owner, repo)."""
    for key, sha in STATIC_SHA.items():
        _SHA_CACHE[key] = sha


# Optional path after branch (repo root: .../tree/master with no further path)
TREE_URL_RE = re.compile(
    r"https://github\.com/(?P<owner>[^/\s\)]+)/(?P<repo>[^/\s\)]+)/tree/(?P<branch>[^/\s\)]+)(?:/(?P<rest>[^\s\)`]*))?"
)


def _parse_path_and_lines(rest: Optional[str]) -> Tuple[str, Optional[str]]:
    if not rest:
        return "", None
    rest = rest.rstrip(").,;")
    if ":" not in rest:
        return rest.rstrip("/"), None
    path_part, suffix = rest.rsplit(":", 1)
    if re.fullmatch(r"[\d\s,\-]+", suffix):
        nums = [int(x) for x in re.findall(r"\d+", suffix)]
        if not nums:
            return rest.rstrip("/"), None
        lo, hi = min(nums), max(nums)
        frag = "L{0}".format(lo) if lo == hi else "L{0}-L{1}".format(lo, hi)
        return path_part.rstrip("/"), frag
    return rest.rstrip("/"), None


def _is_probably_file(path: str) -> bool:
    if not path or path.endswith("/"):
        return False
    base = path.rsplit("/", 1)[-1]
    return "." in base


def _permalink(owner: str, repo: str, sha: str, path: str, frag: Optional[str]) -> str:
    path = path.lstrip("/")
    if not path:
        return "https://github.com/{0}/{1}/tree/{2}".format(owner, repo, sha)
    if _is_probably_file(path):
        base = "https://github.com/{0}/{1}/blob/{2}/{3}".format(owner, repo, sha, path)
        return "{0}#{1}".format(base, frag) if frag else base
    return "https://github.com/{0}/{1}/tree/{2}/{3}".format(owner, repo, sha, path)


def _transform_tree_url(full_url: str) -> List[str]:
    m = TREE_URL_RE.search(full_url)
    if not m:
        return [full_url]
    owner = m.group("owner")
    repo = m.group("repo")
    rest = m.group("rest")
    key = (owner, repo)
    path, frag = _parse_path_and_lines(rest)
    if owner != "th3w1zard1" or key not in UPSTREAM:
        return [full_url]
    mirror_sha = _fetch_default_branch_sha(owner, repo)
    mirror_link = _permalink(owner, repo, mirror_sha, path, frag)
    upstream_spec = UPSTREAM[key]
    lines: List[str] = []
    if upstream_spec is None:
        lines.append("  - Canonical ({0}/{1}): {2}".format(owner, repo, mirror_link))
        return lines
    u_owner, u_repo = upstream_spec
    try:
        up_sha = _fetch_default_branch_sha(u_owner, u_repo)
    except Exception:
        up_sha = mirror_sha
    up_link = _permalink(u_owner, u_repo, up_sha, path, frag)
    lines.append("  - Upstream ({0}/{1}): {2}".format(u_owner, u_repo, up_link))
    lines.append("  - Mirror ({0}/{1}): {2}".format(owner, repo, mirror_link))
    return lines


def _line_description(raw: str, url: str) -> str:
    s = raw.replace(url, "").strip()
    s = re.sub(r"^\#\s*", "", s)
    s = re.sub(r"^Reference:\s*", "", s, flags=re.I)
    s = re.sub(r"^-\s*", "", s)
    s = re.sub(r"^KotOR\.js:\s*", "", s, flags=re.I)
    s = s.strip(" -—:").strip()
    if s.startswith("(tool)"):
        s = s[6:].strip()
    return s.strip() or "(reference)"


def _should_skip_file(text: str, path: Path) -> bool:
    if "th3w1zard1" not in text:
        return True
    if path.name == "reverse_engineering_findings_resource_formats_mdl_io_mdl_github_urls_pre_scrub.md":
        if "Upstream (ndixUR" in text:
            return True
    # Already migrated to list + permalinks (avoid double-rewrite)
    if "Upstream (" in text and "Mirror (th3w1zard1" in text and "/tree/master/" not in text:
        return True
    return False


def _extract_url_lines(content: str) -> List[str]:
    out: List[str] = []
    in_fence = False
    for line in content.splitlines():
        t = line.strip()
        if t.startswith("```"):
            in_fence = not in_fence
            continue
        if "github.com/th3w1zard1" in line and "tree/" in line:
            out.append(line)
        elif "github.com/th3w1zard1" in line and in_fence and "/tree/" in line:
            out.append(line)
    return out


def rewrite_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if _should_skip_file(text, path):
        return False
    lines = text.splitlines()
    if not lines:
        return False
    h1 = lines[0] if lines[0].startswith("# ") else "# {0}".format(path.stem)
    intro: List[str] = []
    i = 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    while i < len(lines) and not lines[i].startswith("```"):
        intro.append(lines[i])
        i += 1
    url_lines = _extract_url_lines(text)
    if not url_lines:
        return False

    out: List[str] = [h1, ""]
    out.extend(intro)
    if intro and intro[-1].strip():
        out.append("")
    out.append(
        "Canonical upstream and **th3w1zard1** mirror/fork permalinks (`blob` / `tree` + commit) follow "
        "[Home](Home) cross-references. Resolved via GitHub API (`master` / `main` tip) on "
        "{0}.".format(date.today().isoformat())
    )
    out.append("")
    out.append("When upstream and mirror SHAs differ, line anchors may not match both trees.")

    for raw in url_lines:
        stripped = raw.strip()
        found: List[str] = []
        for m in TREE_URL_RE.finditer(stripped):
            found.append(m.group(0).rstrip(").,;"))
        if not found:
            continue
        desc = _line_description(stripped, found[0])
        for u in found[1:]:
            if u in desc:
                desc = _line_description(desc, u)
        out.append("")
        out.append("- {0}".format(desc))
        for u in found:
            out.extend(_transform_tree_url(u))

    out.append("")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return True


def main() -> int:
    _prefetch_shas()
    patterns = [
        "reverse_engineering_findings_*github_urls_pre_scrub.md",
        "reverse_engineering_findings_*url*_pre_scrub.md",
    ]
    changed = 0
    seen: Set[Path] = set()
    for pat in patterns:
        for md in sorted(WIKI.glob(pat)):
            if md in seen:
                continue
            seen.add(md)
            try:
                if rewrite_file(md):
                    print("rewrote {0}".format(md.relative_to(WIKI)))
                    changed += 1
            except Exception as e:
                print("FAIL {0}: {1}".format(md, e), file=sys.stderr)
    print("done, {0} files".format(changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
