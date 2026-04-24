"""Resource format subpackages (binary/XML readers live under ``gff``, ``tlk``, ``ncs``, etc.)."""

from __future__ import annotations

from ._base import BiowareResource, ComparableMixin

__all__ = [
    "BiowareResource",
    "ComparableMixin",
]