#!/usr/bin/env python3
"""Expand th3w1zard1 GitHub URLs across wiki/*.md: upstream permalink, then mirror (list syntax).

Uses `gh api` for default-branch tip SHAs. Run from repo root:

    uv run python scripts/wiki_th3_canonical_mirror.py

Optional: WIKI_TH3_DRY_RUN=1 for no writes.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI = REPO_ROOT / "wiki"

UPSTREAM: Dict[Tuple[str, str], Optional[Tuple[str, str]]] = {
    ("th3w1zard1", "KotOR.js"): ("KobaltBlu", "KotOR.js"),
    ("th3w1zard1", "Kotor.NET"): ("NickHugi", "Kotor.NET"),
    ("th3w1zard1", "kotorblender"): ("OpenKotOR", "kotorblender"),
    ("th3w1zard1", "mdlops"): ("ndixUR", "mdlops"),
    ("th3w1zard1", "KotOR-Bioware-Libs"): ("Fair-Strides", "KotOR-Bioware-Libs"),
    ("th3w1zard1", "tga2tpc"): ("ndixUR", "tga2tpc"),
    ("th3w1zard1", "KotOR-dotNET"): ("NickHugi", "Kotor.NET"),
    ("th3w1zard1", "KotOR_IO"): ("Fair-Strides", "KotOR-Bioware-Libs"),
    ("th3w1zard1", "kotor"): ("marfsama", "kotor"),
    ("th3w1zard1", "KotOR-Scripting-Tool"): ("KobaltBlu", "KotOR-Scripting-Tool"),
    ("th3w1zard1", "nwscript-ts-mode"): ("implicit-image", "nwscript-ts-mode"),
    ("th3w1zard1", "xoreos"): ("xoreos", "xoreos"),
    ("th3w1zard1", "TSLPatcher"): None,
    ("th3w1zard1", "HoloPatcher.NET"): None,
    ("th3w1zard1", "HoloLSP"): None,
    ("th3w1zard1", "KotORModSync"): None,
    ("th3w1zard1", "StarForge"): None,
    ("th3w1zard1", "BioWare.NET"): None,
}

KOTOR_NET_PATH_FIX: Dict[str, str] = {
    "UTD.cs": "Kotor.NET/Resources/KotorUTD/UTD.cs",
    "UTW.cs": "Kotor.NET/Resources/KotorUTW/UTW.cs",
    "UTP.cs": "Kotor.NET/Resources/KotorUTP/UTP.cs",
    "UTE.cs": "Kotor.NET/Resources/KotorUTE/UTE.cs",
    "DLG.cs": "Kotor.NET/Resources/KotorDLG/DLG.cs",
    "DLGDecompiler.cs": "Kotor.NET/Resources/KotorDLG/DLGDecompiler.cs",
    "GFFBinaryStructure.cs": "Kotor.NET/Formats/GFF/GFFBinaryStructure.cs",
    "GFFBinaryWriter.cs": "Kotor.NET/Formats/GFF/GFFBinaryWriter.cs",
    "AuroraFile.cs": "Kotor.NET/Formats/AuroraFile.cs",
}

_SHA_CACHE: Dict[Tuple[str, str], str] = {}


def _gh_tip_sha(owner: str, repo: str) -> str:
    key = (owner, repo)
    if key in _SHA_CACHE:
        return _SHA_CACHE[key]
    br = subprocess.run(
        ["gh", "api", "repos/{0}/{1}".format(owner, repo), "-q", ".default_branch"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if br.returncode != 0:
        raise RuntimeError("gh repos {0}/{1}: {2}".format(owner, repo, br.stderr.strip()))
    branch = br.stdout.strip()
    sh = subprocess.run(
        ["gh", "api", "repos/{0}/{1}/commits/{2}".format(owner, repo, branch), "-q", ".sha"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if sh.returncode != 0:
        raise RuntimeError("gh commits {0}/{1}@{2}: {3}".format(owner, repo, branch, sh.stderr.strip()))
    sha = sh.stdout.strip()
    _SHA_CACHE[key] = sha
    return sha


def _is_probably_file(path: str) -> bool:
    if not path or path.endswith("/"):
        return False
    base = path.rsplit("/", 1)[-1]
    return "." in base


def _line_fragment(suffix: str) -> Optional[str]:
    nums = [int(x) for x in re.findall(r"\d+", suffix)]
    if not nums:
        return None
    lo, hi = min(nums), max(nums)
    return "L{0}".format(lo) if lo == hi else "L{0}-L{1}".format(lo, hi)


def _kotor_net_canonical_path(path: str) -> str:
    if path in KOTOR_NET_PATH_FIX:
        return KOTOR_NET_PATH_FIX[path]
    bn = path.rsplit("/", 1)[-1]
    if bn in KOTOR_NET_PATH_FIX:
        return KOTOR_NET_PATH_FIX[bn]
    return path


def _permalink(owner: str, repo: str, sha: str, path: str, frag: Optional[str]) -> str:
    path = path.lstrip("/")
    if not path:
        return "https://github.com/{0}/{1}/tree/{2}".format(owner, repo, sha)
    if _is_probably_file(path):
        u = "https://github.com/{0}/{1}/blob/{2}/{3}".format(owner, repo, sha, path)
        return "{0}#{1}".format(u, frag) if frag else u
    return "https://github.com/{0}/{1}/tree/{2}/{3}".format(owner, repo, sha, path)


TREE_RE = re.compile(
    r"https://github\.com/th3w1zard1/(?P<repo>[^/\s\)`]+)/tree/(?P<branch>[^/\s\)`]+)/(?P<rest>[^\s\)`]+)"
)

BLOB_RE = re.compile(
    r"https://github\.com/th3w1zard1/(?P<repo>[^/\s\)`]+)/blob/(?P<branch>[^/\s\)`]+)/(?P<path>[^\s\)`#]+)(?:#(?P<frag>L\d+(?:-L\d+)?))?"
)

# Repo home: https://github.com/th3w1zard1/Repo (no /blob/ or /tree/)
ROOT_RE = re.compile(r"https://github\.com/th3w1zard1/(?P<repo>[^/\s\)`]+)/?$")


def _parse_tree_path(rest: str) -> Tuple[str, Optional[str]]:
    rest = rest.rstrip(").,;")
    if ":" not in rest:
        return rest, None
    path_part, suffix = rest.rsplit(":", 1)
    if re.fullmatch(r"[\d\s,\-]+", suffix):
        return path_part, _line_fragment(suffix)
    return rest, None


def _expand_tree_url(url: str) -> Optional[str]:
    m = TREE_RE.search(url)
    if not m:
        return None
    repo = m.group("repo")
    key = ("th3w1zard1", repo)
    if key not in UPSTREAM:
        return None
    rest = m.group("rest")
    path, frag = _parse_tree_path(rest)
    if repo == "Kotor.NET":
        path = _kotor_net_canonical_path(path)
    msha = _gh_tip_sha("th3w1zard1", repo)
    mir = _permalink("th3w1zard1", repo, msha, path, frag)
    spec = UPSTREAM[key]
    if spec is None:
        return "- Canonical (th3w1zard1/{0}): {1}".format(repo, mir)
    uo, ur = spec
    up_path = _kotor_net_canonical_path(path) if ur == "Kotor.NET" else path
    usha = _gh_tip_sha(uo, ur)
    up = _permalink(uo, ur, usha, up_path, frag)
    return "- Upstream ({0}/{1}): {2}\n- Mirror (th3w1zard1/{3}): {4}".format(uo, ur, up, repo, mir)


def _expand_root_url(url: str) -> Optional[str]:
    u = url.rstrip("/")
    m = ROOT_RE.fullmatch(u)
    if not m:
        return None
    repo = m.group("repo")
    key = ("th3w1zard1", repo)
    if key not in UPSTREAM:
        return None
    msha = _gh_tip_sha("th3w1zard1", repo)
    mir = "https://github.com/th3w1zard1/{0}/tree/{1}".format(repo, msha)
    spec = UPSTREAM[key]
    if spec is None:
        return "- Canonical (th3w1zard1/{0}): {1}".format(repo, mir)
    uo, ur = spec
    usha = _gh_tip_sha(uo, ur)
    up = "https://github.com/{0}/{1}/tree/{2}".format(uo, ur, usha)
    return "- Upstream ({0}/{1}): {2}\n- Mirror (th3w1zard1/{3}): {4}".format(uo, ur, up, repo, mir)


def _expand_blob_url(url: str) -> Optional[str]:
    m = BLOB_RE.search(url)
    if not m:
        return None
    repo = m.group("repo")
    key = ("th3w1zard1", repo)
    if key not in UPSTREAM:
        return None
    branch = m.group("branch")
    path = m.group("path").rstrip(").,;")
    frag = m.group("frag")
    if repo == "Kotor.NET":
        path = _kotor_net_canonical_path(path)
    msha = _gh_tip_sha("th3w1zard1", repo)
    if re.fullmatch(r"[a-f0-9]{40}", branch):
        msha = branch
    mir = _permalink("th3w1zard1", repo, msha, path, frag)
    spec = UPSTREAM[key]
    if spec is None:
        return "- Canonical (th3w1zard1/{0}): {1}".format(repo, mir)
    uo, ur = spec
    up_path = _kotor_net_canonical_path(path) if ur == "Kotor.NET" else path
    usha = _gh_tip_sha(uo, ur)
    up = _permalink(uo, ur, usha, up_path, frag)
    return "- Upstream ({0}/{1}): {2}\n- Mirror (th3w1zard1/{3}): {4}".format(uo, ur, up, repo, mir)


def _line_indent(line: str) -> str:
    m = re.match(r"^(\s*)", line)
    return m.group(1) if m else ""


def _skip_line(stripped: str) -> bool:
    if re.match(r"^\s*-\s*Upstream\s+\(", stripped):
        return True
    if re.match(r"^\s*-\s*Mirror\s+\(", stripped):
        return True
    if re.match(r"^\s*-\s*Canonical\s+\(", stripped):
        return True
    return False


def _apply_expand_to_line(line: str) -> Tuple[str, int]:
    raw = line.rstrip("\n\r")
    nl = line[len(raw) :]
    if "github.com/th3w1zard1" not in raw or _skip_line(raw):
        return line, 0
    indent = _line_indent(raw)

    # Markdown [label](url)
    lm = re.search(r"\[([^\]]*)\]\((https://github\.com/th3w1zard1/[^)]+)\)", raw)
    if lm:
        u = lm.group(2)
        expanded = None
        if "/tree/" in u:
            expanded = _expand_tree_url(u)
        elif "/blob/" in u:
            expanded = _expand_blob_url(u)
        else:
            expanded = _expand_root_url(u)
        if expanded:
            # `[Label](url)` starts at lm.start(). If preceded by `**`, this was `**[Label](url)**`.
            lb = lm.start()
            prefix = raw[:lb]
            suffix = raw[lm.end() :]
            label = lm.group(1)
            bold_wrap = lb >= 2 and raw[lb - 2 : lb] == "**"
            if bold_wrap and suffix.startswith("**"):
                suffix = suffix[2:]
            if bold_wrap:
                head = "{0}{1}**{2}".format(prefix, label, suffix).rstrip()
            else:
                head = "{0}**{1}**{2}".format(prefix, label, suffix).rstrip()
            # Markdown table row: do not inject newline+sub-bullets (breaks the table).
            if re.match(r"^\s*\|", raw):
                urls = re.findall(r"https://github\.com/[^\s\)`|]+", expanded)
                if len(urls) >= 2:
                    tail = " — upstream {0} — mirror {1}".format(urls[0], urls[1])
                elif urls:
                    tail = " — {0}".format(urls[0])
                else:
                    tail = ""
                return head + tail + nl, 1
            block = head + "\n" + "\n".join(indent + "  " + x for x in expanded.splitlines())
            return block + nl, 1

    tm = TREE_RE.search(raw)
    if tm:
        u = tm.group(0).rstrip(").,;")
        expanded = _expand_tree_url(u)
        if expanded:
            before = raw[: tm.start()].rstrip()
            after = raw[tm.end() :].lstrip()
            mid = "\n".join(indent + x for x in expanded.splitlines())
            parts = [p for p in (before, mid, after) if p]
            return "\n".join(parts) + nl, 1

    bm = BLOB_RE.search(raw)
    if bm:
        u = raw[bm.start() : bm.end()].rstrip(").,;")
        expanded = _expand_blob_url(u)
        if expanded:
            before = raw[: bm.start()].rstrip()
            after = raw[bm.end() :].lstrip()
            mid = "\n".join(indent + x for x in expanded.splitlines())
            parts = [p for p in (before, mid, after) if p]
            return "\n".join(parts) + nl, 1

    return line, 0


def process_text(content: str) -> Tuple[str, int]:
    total = 0
    out: List[str] = []
    for line in content.splitlines(keepends=True):
        if line.endswith("\n"):
            core, n = _apply_expand_to_line(line[:-1])
            out.append(core + "\n")
        else:
            core, n = _apply_expand_to_line(line)
            out.append(core)
        total += n
    # Multi-pass for lines that contained multiple URLs (e.g. prose lists)
    text = "".join(out)
    for _ in range(8):
        out2: List[str] = []
        sub = 0
        for line in text.splitlines(keepends=True):
            if line.endswith("\n"):
                c, n = _apply_expand_to_line(line[:-1])
                out2.append(c + "\n")
            else:
                c, n = _apply_expand_to_line(line)
                out2.append(c)
            sub += n
        text = "".join(out2)
        total += sub
        if sub == 0:
            break
    return text, total


def _refresh_blob_shas(content: str) -> Tuple[str, int]:
    pat = re.compile(
        r"https://github\.com/(?P<o>[^/]+)/(?P<r>[^/]+)/blob/(?P<sha>[a-f0-9]{40})/(?P<path>[^\s\)`#]+)(?P<frag>#[^\s\)`]*)?"
    )
    changes = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changes
        o, r, old_sha, path, frag = m.group("o"), m.group("r"), m.group("sha"), m.group("path"), m.group("frag") or ""
        try:
            new_sha = _gh_tip_sha(o, r)
        except Exception:
            return m.group(0)
        if new_sha == old_sha:
            return m.group(0)
        changes += 1
        return "https://github.com/{0}/{1}/blob/{2}/{3}{4}".format(o, r, new_sha, path, frag)

    return pat.sub(repl, content), changes


def main() -> int:
    dry = os.environ.get("WIKI_TH3_DRY_RUN", "").strip() in ("1", "true", "yes")
    n_files = 0
    n_ops = 0
    for md in sorted(WIKI.rglob("*.md")):
        try:
            raw = md.read_text(encoding="utf-8")
            updated, n = process_text(raw)
            updated, n2 = _refresh_blob_shas(updated)
            n += n2
        except Exception as e:
            print("FAIL {0}: {1}".format(md.relative_to(REPO_ROOT), e), file=sys.stderr)
            return 1
        if n:
            n_files += 1
            n_ops += n
            rel = md.relative_to(REPO_ROOT)
            print("{0}: {1}".format(rel.as_posix(), n))
            if not dry:
                md.write_text(updated, encoding="utf-8", newline="\n")
    print("wiki_th3_canonical_mirror: {0} files, {1} ops".format(n_files, n_ops))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
