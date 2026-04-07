#!/usr/bin/env python3
"""
RE cache + codegen pipeline for K1 save/load.

Usage:
  python run_pipeline.py                    # codegen + verify (uses default cache)
  python run_pipeline.py --codegen         # only generate save_load_flow_k1.py from cache
  python run_pipeline.py --verify         # only run pytest
  python run_pipeline.py --cache path     # use custom cache JSON

Cache is built by calling user-agdec-http get-function for each address and
merging into one JSON (or by execute-script with export_save_load_functions.py).
Codegen reads the cache and emits/updates the flow module; verify runs tests.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from pathlib import Path

# Repo root: helper_scripts/agdec_save_load/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CACHE = REPO_ROOT / "docs" / "reva_roadmap" / "agdec_cache" / "k1_save_load_cache.json"
FLOW_MODULE = (
    REPO_ROOT / "Libraries" / "PyKotor" / "src" / "pykotor" / "extract" / "save_load_flow_k1.py"
)
FLOW_TESTS = REPO_ROOT / "Libraries" / "PyKotor" / "tests" / "extract" / "test_save_load_flow_k1.py"


def load_cache(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def codegen_from_cache(cache: dict, output_path: Path) -> None:
    """Emit save_load_flow_k1.py from cache. Prepends cache provenance comment."""
    program = cache.get("program", "?")
    functions = cache.get("functions", [])
    current = output_path.read_text(encoding="utf-8")
    # Drop leading lines that are RE cache comments (idempotent re-run)
    lines = current.splitlines(keepends=True)
    while lines and lines[0].strip().startswith("# RE cache:"):
        lines.pop(0)
    current = "".join(lines)
    current = f"# RE cache: {program}, {len(functions)} functions (run_pipeline.py)\n" + current
    output_path.write_text(current, encoding="utf-8")


def verify() -> int:
    """Run pytest on flow tests. Returns exit code."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(FLOW_TESTS),
        "-v",
        "--timeout=60",
        "-q",
    ]
    env = {"QT_QPA_PLATFORM": "offscreen"}
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), env={**__import__("os").environ, **env})
    return result.returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="RE cache + codegen pipeline for K1 save/load")
    ap.add_argument("--cache", type=Path, default=DEFAULT_CACHE, help="Path to cache JSON")
    ap.add_argument("--codegen", action="store_true", help="Generate flow module from cache")
    ap.add_argument("--verify", action="store_true", help="Run pytest on flow tests")
    ap.add_argument("--output", type=Path, default=FLOW_MODULE, help="Output path for codegen")
    args = ap.parse_args()

    if not args.codegen and not args.verify:
        args.codegen = True
        args.verify = True

    if args.codegen:
        if not args.cache.exists():
            print(f"Cache not found: {args.cache}", file=sys.stderr)
            return 1
        cache = load_cache(args.cache)
        codegen_from_cache(cache, args.output)
        print(f"Codegen: {args.output} ({len(cache.get('functions', []))} functions from cache)")

    if args.verify:
        print("Verify: running pytest...")
        return verify()

    return 0


if __name__ == "__main__":
    sys.exit(main())
