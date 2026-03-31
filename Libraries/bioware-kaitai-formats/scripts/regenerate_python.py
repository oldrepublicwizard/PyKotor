#!/usr/bin/env python3
r"""Compile all ``.ksy`` under a root into ``src/bioware_kaitai_formats`` and post-process.

Requires ``kaitai-struct-compiler`` on PATH or pass ``--ksc``.

Example::

    uv run python scripts/regenerate_python.py --ksy-root ..\vendor\bioware-kaitai-formats
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _find_ksc(explicit: str | None) -> list[str]:
    if explicit:
        p = Path(explicit)
        if p.suffix.lower() == ".bat" and p.is_file():
            return [str(p)]
        return [str(p)]
    return ["kaitai-struct-compiler"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate bioware_kaitai_formats from .ksy tree.")
    parser.add_argument(
        "--ksy-root",
        type=Path,
        required=True,
        help="Directory containing .ksy files (recursive).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Root of bioware-kaitai-formats package (contains pyproject.toml).",
    )
    parser.add_argument(
        "--ksc",
        default=None,
        help="Path to kaitai-struct-compiler executable or .bat.",
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or _default_repo_root()).resolve()
    ksy_root = args.ksy_root.resolve()
    out_pkg = repo_root / "src" / "bioware_kaitai_formats"

    if not ksy_root.is_dir():
        print(f"Not a directory: {ksy_root}", file=sys.stderr)
        return 1

    ksy_files = sorted(ksy_root.rglob("*.ksy"))
    if not ksy_files:
        print(f"No .ksy files under {ksy_root}", file=sys.stderr)
        return 1

    ksc_cmd = _find_ksc(args.ksc)
    # KSC resolves imports across all specs passed in one invocation.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        cmd = [
            *ksc_cmd,
            "-t",
            "python",
            "-d",
            str(tmp_path),
            "--python-package",
            "bioware_kaitai_formats",
        ]
        # Windows: bat needs shell if not direct exe
        use_shell = len(ksc_cmd) == 1 and ksc_cmd[0].lower().endswith(".bat")
        env = os.environ.copy()
        # Help KSC resolve imports between specs
        env.setdefault("SRC_DIR", str(ksy_root))
        try:
            subprocess.run(
                cmd + [str(p) for p in ksy_files],
                check=True,
                env=env,
                shell=use_shell,
            )
        except FileNotFoundError:
            print(
                "kaitai-struct-compiler not found. Install KSC 0.11.x or pass --ksc.",
                file=sys.stderr,
            )
            return 1
        except subprocess.CalledProcessError as e:
            print(f"KSC failed with exit {e.returncode}", file=sys.stderr)
            return e.returncode

        gen_root = tmp_path / "bioware_kaitai_formats"
        if not gen_root.is_dir():
            # Some KSC versions emit flat under -d
            flat_py = list(tmp_path.glob("*.py"))
            if flat_py:
                out_pkg.mkdir(parents=True, exist_ok=True)
                for p in tmp_path.iterdir():
                    if p.is_file():
                        shutil.copy2(p, out_pkg / p.name)
            else:
                print(f"Expected output under {gen_root} or flat .py in {tmp_path}", file=sys.stderr)
                return 1
        else:
            if out_pkg.exists():
                shutil.rmtree(out_pkg)
            shutil.copytree(gen_root, out_pkg)

    pp_path = repo_root / "scripts" / "postprocess_generated.py"
    spec = importlib.util.spec_from_file_location("postprocess_generated", pp_path)
    if spec is None or spec.loader is None:
        print(f"Cannot load {pp_path}", file=sys.stderr)
        return 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.postprocess(out_pkg)
    print(f"Wrote {out_pkg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
