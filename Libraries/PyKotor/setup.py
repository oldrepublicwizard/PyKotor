from __future__ import annotations

import os
import sys

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class OptionalBuildExt(build_ext):
    """Build C extensions but don't fail if compilation is unavailable.

    On platforms without a C compiler (or when headers are missing), the
    package still installs — the C accelerators simply won't be available
    and the Python fallbacks will be used instead.
    """

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception:
            print(
                f"WARNING: Failed to build C extension '{ext.name}'. Falling back to pure-Python implementation.",
                file=sys.stderr,
            )

# C extensions for GL acceleration.
ext_modules = [
    Extension(
        "pykotor.gl.native._gl_accel",
        sources=[os.path.join("src", "pykotor", "gl", "native", "_gl_accel.c")],
    ),
    Extension(
        "pykotor.gl.native._render2d_accel",
        sources=[os.path.join("src", "pykotor", "gl", "native", "_render2d_accel.c")],
    ),
]


setup(
    # Project metadata, dependencies, and scripts are defined in pyproject.toml.
    ext_modules=ext_modules,
    cmdclass={"build_ext": OptionalBuildExt},
)
