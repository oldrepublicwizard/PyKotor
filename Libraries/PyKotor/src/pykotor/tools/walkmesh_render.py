"""Render BWM walkmesh to validation PNGs using matplotlib 3D.

Used by the CLI when --render-png is passed to walkmesh-rebuild. Importing this
module requires matplotlib; the CLI catches ImportError and instructs the user
to install pykotor[render].
"""

from __future__ import annotations

import math
import pathlib

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  # registers 3D projection
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection

from pykotor.resource.formats.bwm.bwm_data import BWM

# Palette (RGBA)
WALKABLE_COLOR = (0.1, 0.2, 0.5, 0.6)
UNWALKABLE_COLOR = (0.2, 0.2, 0.2, 0.6)
ARROW_COLOR = (1.0, 0.3, 0.0, 1.0)
GRID_COLOR = (0.5, 0.5, 0.5, 0.4)
EDGE_COLOR = (0.1, 0.1, 0.1, 1.0)
NORMAL_COLOR = (0.0, 0.8, 0.8, 0.8)


def render_bwm_to_pngs(
    bwm: BWM,
    output_stem: pathlib.Path,
    *,
    dpi: int = 300,
    size_inches: tuple[float, float] = (6.4, 3.6),
) -> list[pathlib.Path]:
    """Render the walkmesh to 3–4 validation PNGs (views) next to output_stem.

    Writes {output_stem}_view1.png … _view4.png. No logging; caller logs paths.

    Args:
    ----
        bwm: Rebuilt BWM in memory.
        output_stem: Directory + stem (e.g. output_dir / "203tell_rebuild").
        dpi: DPI for saved figures.
        size_inches: Figure size (width, height) in inches.

    Returns:
    -------
        List of paths to the written PNG files.
    """
    verts_list = [(v.x, v.y, v.z) for v in bwm.vertices()]
    walkable = bwm.walkable_faces()
    unwalkable = bwm.unwalkable_faces()
    faces = walkable + unwalkable
    bbmin, bbmax = bwm.box()
    diag = math.sqrt(
        (bbmax.x - bbmin.x) ** 2
        + (bbmax.y - bbmin.y) ** 2
        + (bbmax.z - bbmin.z) ** 2,
    )
    arrow_scale = max(0.25, 0.07 * diag)
    gizmo_scale = 0.05 * diag
    normal_scale = 0.08 * diag

    # Build triangle verts and face colors (identity-based vertex lookup)
    verts_by_id = {id(v): i for i, v in enumerate(bwm.vertices())}
    tri_verts: list[np.ndarray] = []
    face_colors: list[tuple[float, float, float, float]] = []
    for face in faces:
        i1 = verts_by_id[id(face.v1)]
        i2 = verts_by_id[id(face.v2)]
        i3 = verts_by_id[id(face.v3)]
        tri_verts.append(
            np.array([
                verts_list[i1],
                verts_list[i2],
                verts_list[i3],
            ]),
        )
        face_colors.append(
            WALKABLE_COLOR if face.material.walkable() else UNWALKABLE_COLOR,
        )

    # Arrows: perimeter edges with transition >= 0
    arrow_segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    for edge in bwm.edges():
        if edge.transition < 0:
            continue
        mid, direction = BWM.edge_inward_direction_xy(edge.face, edge.index)
        end = (
            mid.x + arrow_scale * direction.x,
            mid.y + arrow_scale * direction.y,
            mid.z,
        )
        arrow_segments.append(((mid.x, mid.y, mid.z), end))

    # Grid at Z = bbmin.z, XY
    gx = np.linspace(bbmin.x, bbmax.x, max(2, int((bbmax.x - bbmin.x) / 1.0) + 1))
    gy = np.linspace(bbmin.y, bbmax.y, max(2, int((bbmax.y - bbmin.y) / 1.0) + 1))
    z_grid = bbmin.z
    grid_lines: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    for x in gx:
        grid_lines.append(((x, gy[0], z_grid), (x, gy[-1], z_grid)))
    for y in gy:
        grid_lines.append(((gx[0], y, z_grid), (gx[-1], y, z_grid)))

    # Axis gizmo at corner (bbmin)
    gizmo_lines = [
        ((bbmin.x, bbmin.y, bbmin.z), (bbmin.x + gizmo_scale, bbmin.y, bbmin.z)),  # X red
        ((bbmin.x, bbmin.y, bbmin.z), (bbmin.x, bbmin.y + gizmo_scale, bbmin.z)),  # Y green
        ((bbmin.x, bbmin.y, bbmin.z), (bbmin.x, bbmin.y, bbmin.z + gizmo_scale)),  # Z blue
    ]

    # Face normals (every 10th face)
    normal_segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    for i, face in enumerate(faces):
        if i % 10 != 0:
            continue
        c = face.centre()
        n = face.normal()
        normal_segments.append(
            ((c.x, c.y, c.z), (c.x + normal_scale * n.x, c.y + normal_scale * n.y, c.z + normal_scale * n.z)),
        )

    extent = (
        bbmax.x - bbmin.x,
        bbmax.y - bbmin.y,
        bbmax.z - bbmin.z,
    )
    aspect = (max(extent[0], 1e-6), max(extent[1], 1e-6), max(extent[2], 1e-6))

    views = [
        ("view1", 90, 0, True, True),   # top-down
        ("view2", 35, 30, True, True),  # perspective 1
        ("view3", 35, 210, True, True), # perspective 2
        ("view4", 35, 30, False, True), # wireframe emphasis (edges only over solid)
    ]

    written: list[pathlib.Path] = []
    for view_name, elev, azim, draw_faces, draw_edges in views:
        fig = plt.figure(figsize=size_inches)
        ax = fig.add_subplot(111, projection="3d")
        ax.set_box_aspect(aspect)
        ax.view_init(elev=elev, azim=azim)

        if draw_faces:
            coll = Poly3DCollection(tri_verts, facecolors=face_colors, alpha=0.6, edgecolors="none")
            ax.add_collection3d(coll)
        if draw_edges:
            edge_verts = [t for t in tri_verts]
            edge_coll = Poly3DCollection(edge_verts, facecolors="none", edgecolors=EDGE_COLOR, linewidths=0.8)
            ax.add_collection3d(edge_coll)
        if grid_lines:
            lc = Line3DCollection(grid_lines, colors=GRID_COLOR, linewidths=0.5)
            ax.add_collection3d(lc)
        if arrow_segments:
            ac = Line3DCollection(arrow_segments, colors=ARROW_COLOR, linewidths=1.2)
            ax.add_collection3d(ac)
        if gizmo_lines:
            ax.plot(
                [gizmo_lines[0][0][0], gizmo_lines[0][1][0]],
                [gizmo_lines[0][0][1], gizmo_lines[0][1][1]],
                [gizmo_lines[0][0][2], gizmo_lines[0][1][2]],
                color="red",
                linewidth=2,
            )
            ax.plot(
                [gizmo_lines[1][0][0], gizmo_lines[1][1][0]],
                [gizmo_lines[1][0][1], gizmo_lines[1][1][1]],
                [gizmo_lines[1][0][2], gizmo_lines[1][1][2]],
                color="green",
                linewidth=2,
            )
            ax.plot(
                [gizmo_lines[2][0][0], gizmo_lines[2][1][0]],
                [gizmo_lines[2][0][1], gizmo_lines[2][1][1]],
                [gizmo_lines[2][0][2], gizmo_lines[2][1][2]],
                color="blue",
                linewidth=2,
            )
        if normal_segments:
            nc = Line3DCollection(normal_segments, colors=NORMAL_COLOR, linewidths=0.5)
            ax.add_collection3d(nc)

        ax.set_xlim(bbmin.x, bbmax.x)
        ax.set_ylim(bbmin.y, bbmax.y)
        ax.set_zlim(bbmin.z, bbmax.z)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        path = output_stem.parent / f"{output_stem.name}_{view_name}.png"
        fig.savefig(path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        written.append(path)

    return written
