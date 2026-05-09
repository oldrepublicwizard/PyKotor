"""Optional DXT1/DXT5 compression via vendored ndixUR Compressonator (Node.js).

Set ``PYKOTOR_DXT_COMPRESSOR=ndix`` to match the default encoder in ndixUR/tga2tpc
(Electron app) for byte-identical block output vs that toolchain.

Requires ``node`` on ``PATH``. Each call writes a temporary RGBA file and runs
``ndix_compress_cli.cjs`` (one Node process per invocation).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

_VENDOR_DIR = Path(__file__).resolve().parent / "vendor_ndix_compressonator"
NDIX_COMPRESS_CLI = _VENDOR_DIR / "ndix_compress_cli.cjs"


def ndix_compressor_available() -> bool:
    return shutil.which("node") is not None and NDIX_COMPRESS_CLI.is_file()


def use_ndix_compressor() -> bool:
    return os.environ.get("PYKOTOR_DXT_COMPRESSOR", "").strip().lower() in {"ndix", "1", "yes", "true"}


def _run_ndix(enc: int, width: int, height: int, rgba: bytes | bytearray) -> bytes:
    node = shutil.which("node")
    if not node or not NDIX_COMPRESS_CLI.is_file():
        msg = "ndix DXT compressor requires node and ndix_compress_cli.cjs"
        raise RuntimeError(msg)
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA length mismatch")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(bytes(rgba))
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            [node, str(NDIX_COMPRESS_CLI), str(enc), str(width), str(height), tmp_path],
            check=False,
            capture_output=True,
            timeout=600,
        )
        if proc.returncode != 0:
            err = proc.stderr.decode("utf-8", errors="replace") if proc.stderr else ""
            msg = f"ndix_compress_cli failed ({proc.returncode}): {err}"
            raise RuntimeError(msg)
        return proc.stdout
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def rgba_to_dxt5_ndix(rgba_data: bytes | bytearray, width: int, height: int) -> bytes:
    return bytes(_run_ndix(5, width, height, rgba_data))


def rgba_to_dxt1_ndix(rgba_data: bytes | bytearray, width: int, height: int) -> bytes:
    return bytes(_run_ndix(1, width, height, rgba_data))
