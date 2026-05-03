"""Merge and generate BWM walkmeshes for v2 tile-based indoor maps."""

from __future__ import annotations

from copy import deepcopy

from pykotor.common.tilekit import QuaternionWXYZ
from pykotor.resource.formats.bwm.bwm_data import BWM, BWMFace, BWMType
from utility.common.geometry import SurfaceMaterial, Vector3


def rotate_bwm_at_origin(bwm: BWM, rotation: QuaternionWXYZ) -> BWM:
    """Deep-copy *bwm* and rotate all face vertices about the origin by *rotation*."""
    out = deepcopy(bwm)
    if not out.faces:
        return out
    for face in out.faces:
        face.v1 = rotation.rotate_vector(face.v1)
        face.v2 = rotation.rotate_vector(face.v2)
        face.v3 = rotation.rotate_vector(face.v3)
    return out


def merge_translated_bwms(sources: list[tuple[BWM, float, float, float]]) -> BWM:
    """Merge BWMs into one area walkmesh; each piece translated by (tx, ty, tz)."""
    out = BWM()
    out.walkmesh_type = BWMType.AreaModel
    for bwm, tx, ty, tz in sources:
        if not bwm.faces:
            continue
        b = deepcopy(bwm)
        b.translate(tx, ty, tz)
        out.faces.extend(b.faces)
    return out


def generate_flat_floor_quad(
    *,
    min_x: float,
    min_y: float,
    size_x: float,
    size_y: float,
    z: float = 0.0,
    material: SurfaceMaterial = SurfaceMaterial.STONE,
) -> BWM:
    """Two walkable triangles on the X/Y plane at fixed Z (no template WOK fallback)."""
    b = BWM()
    b.walkmesh_type = BWMType.AreaModel
    v0 = Vector3(min_x, min_y, z)
    v1 = Vector3(min_x + size_x, min_y, z)
    v2 = Vector3(min_x + size_x, min_y + size_y, z)
    v3 = Vector3(min_x, min_y + size_y, z)
    f1 = BWMFace(v0, v1, v2)
    f2 = BWMFace(v0, v2, v3)
    f1.material = material
    f2.material = material
    b.faces.append(f1)
    b.faces.append(f2)
    return b
