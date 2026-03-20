#!/usr/bin/env python3
"""Apply MDL AABB fix into the *current* Python env's pykotor package.

Copies from the repo:
  - ``pykotor/__init__.py`` — patches every ``io_mdl.py`` on **first import pykotor**
    (before Holocron can load ``io_mdl``).
  - ``io_mdl.py``, ``mdl_auto.py``, ``mdl/__init__.py``, ``_install_mdl_io_aabb.py``.
  - ``sitecustomize.py`` (from ``scripts/sitecustomize_koq_mdl.py``) into **site-packages**
    so uv/Holocron venvs still get the KOQ200 AABB fix even when disk-patch is read-only.

Usage::

    uv run python scripts/apply_pykotor_mdl_aabb_fix.py

    G:\\cache\\uv\\...\\Scripts\\python.exe C:\\GitHub\\PyKotor\\scripts\\apply_pykotor_mdl_aabb_fix.py

Restart HolocronToolset after running.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import site
import stat
import subprocess
import sys
import time
from pathlib import Path


def _force_install_file(src: Path, dst: Path) -> bool:
    """Write dst from src; clears read-only (uv archive)."""
    data = src.read_text(encoding="utf-8")
    p = Path(dst)
    for _ in range(8):
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["cmd", "/c", "attrib", "-R", str(p)],
                    capture_output=True,
                    timeout=25,
                    check=False,
                )
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
            tmp = p.parent / f".{p.name}.koq_inst"
            tmp.write_text(data.replace("\r\n", "\n"), encoding="utf-8")
            os.replace(tmp, p)
            return True
        except OSError:
            time.sleep(0.25)
    return False


def _patch_all_io_mdl_before_import() -> None:
    """Run sitecustomize KOQ disk patch without importing pykotor (fixes uv read-only io_mdl)."""
    script = Path(__file__).resolve()
    sc = script.parent / "sitecustomize_koq_mdl.py"
    if not sc.is_file():
        return
    spec = importlib.util.spec_from_file_location("_pykotor_koq_sitecustomize", sc)
    if spec is None or spec.loader is None:
        return
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        pass


def main() -> int:
    _patch_all_io_mdl_before_import()
    try:
        import pykotor
        import pykotor.resource.formats.mdl.io_mdl as io_mdl
        import pykotor.resource.formats.mdl.mdl_auto as mdl_auto
    except ImportError:
        print("ERROR: pykotor is not installed for this Python.", file=sys.stderr)
        print(f"  executable: {sys.executable}", file=sys.stderr)
        return 1

    script = Path(__file__).resolve()
    repo_root = script.parent.parent
    pyk_pkg = repo_root / "Libraries/PyKotor/src/pykotor"
    mdl = pyk_pkg / "resource/formats/mdl"
    pairs = [
        (pyk_pkg / "__init__.py", Path(pykotor.__file__).resolve()),
        (mdl / "io_mdl.py", Path(io_mdl.__file__).resolve()),
        (mdl / "mdl_auto.py", Path(mdl_auto.__file__).resolve()),
        (mdl / "__init__.py", Path(io_mdl.__file__).resolve().parent / "__init__.py"),
        (mdl / "_install_mdl_io_aabb.py", Path(io_mdl.__file__).resolve().parent / "_install_mdl_io_aabb.py"),
    ]
    for src, dst in pairs:
        if not src.is_file():
            print(f"ERROR: missing source {src}", file=sys.stderr)
            return 1
        if not _force_install_file(src, dst):
            try:
                shutil.copy2(src, dst)
            except OSError as e:
                print(f"ERROR: could not write {dst}: {e}", file=sys.stderr)
                print("Close HolocronToolset, then re-run.", file=sys.stderr)
                return 1
        print(f"Patched: {dst}")

    sc_src = repo_root / "scripts/sitecustomize_koq_mdl.py"
    if sc_src.is_file():
        try:
            roots = list(site.getsitepackages())
        except Exception:
            roots = []
        for sp in roots:
            dst = Path(sp) / "sitecustomize.py"
            try:
                if dst.is_file():
                    old = dst.read_text(encoding="utf-8", errors="replace")
                    if "_apply_koq_mdl_fix" not in old:
                        bak = dst.with_suffix(".py.bak_before_koq_mdl")
                        shutil.copy2(dst, bak)
                        print(f"Backed up prior sitecustomize -> {bak}")
                shutil.copy2(sc_src, dst)
                print(f"Installed sitecustomize: {dst}")
                break
            except OSError as e:
                print(f"WARN: could not write sitecustomize {dst}: {e}", file=sys.stderr)

    print("Restart HolocronToolset.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
