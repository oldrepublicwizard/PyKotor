from __future__ import annotations

import os
import sys

from pathlib import Path

from setuptools import Extension, find_packages, setup
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


def read_requirements() -> list[str]:
    """Read requirements from requirements.txt file."""
    requirements_path = Path(__file__).parent / "requirements.txt"
    if not requirements_path.exists():
        return []

    requirements: list[str] = []
    with open(requirements_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                requirements.append(line)
    return requirements


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
    name="pykotor",
    version="2.1.0",
    description="Read, modify and write files used by KotOR's game engine.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=read_requirements(),
    python_requires=">=3.8",
    ext_modules=ext_modules,
    cmdclass={"build_ext": OptionalBuildExt},
    entry_points={
        "console_scripts": [
            "pykotor=pykotor.cli.__main__:main",
            "pykotorcli=pykotor.cli.__main__:main",
        ],
    },
)
