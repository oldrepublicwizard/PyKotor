"""Tests for the walkmesh-rebuild CLI command.

What "arrows" are
-----------------
In WOK files, each face has up to three edges. An edge can have a "transition" (trans1/trans2/trans3):
a door/area-link ID used by the engine. We visualize these as arrows: one arrow per edge that has
a transition. The arrow direction is not stored in the file; it is defined by convention as
"inward" (from the edge toward the face interior).

Transition-arrows invariant
---------------------------------------------------------------------------------------------------------
1. Arrows exist EXCLUSIVELY on perimeter (outer) edges.
   - Perimeter = edges that have no adjacent walkable face (the boundary of the walkable area).
   - Internal edges (shared by two faces) must have ZERO transitions.

2. Arrows point EXCLUSIVELY inward.
   - "Inward" = from the edge midpoint toward the face centroid (same as KotOR.js WalkmeshEdge.updateNormal).
   - So every transition is on an edge that borders "outside", and the logical arrow points into the face.

3. ZERO transitions on internal edges; ZERO arrows doing anything else.
   - If an edge is not on the perimeter, trans1/trans2/trans3 for that edge must be None.
   - The tests below assert this exhaustively and also that the inward direction matches the convention.
"""

from __future__ import annotations

import pathlib

import pytest

from pykotor.cli.dispatch import cli_main
from pykotor.resource.formats.bwm import read_bwm
from pykotor.resource.formats.bwm.bwm_data import BWM, BWMFace, BWMType
from utility.common.geometry import SurfaceMaterial, Vector3

THIS_DIR = pathlib.Path(__file__).resolve().parent
# THIS_DIR = Libraries/PyKotor/tests/cli; parent = tests; parents[3] = repo root
REPO_ROOT = THIS_DIR.parents[3]
MODEL_203TELL_WOK = REPO_ROOT / "models" / "203tell.wok"
ASCII_203TEL = REPO_ROOT / "203tel.wok.ascii"
TESTS_DIR = THIS_DIR.parent
TEST_WOK_FILE = TESTS_DIR / "test_files" / "test.wok"


def _run_cli(argv: list[str]) -> int:
    """Run the PyKotor CLI with the given argv; returns exit code."""
    return cli_main(argv)


def _assert_transition_arrows_exclusive(bwm: BWM) -> None:
    """Assert the full transition-arrows invariant: perimeter-only, inward-only, zero elsewhere.

    This is the exhaustive check that:
    (1) Every edge that has a transition is a perimeter edge (arrows only on outer edges).
    (2) No internal edge has any transition (ZERO arrows on non-perimeter edges).
    (3) The "inward" direction for each such edge points from edge toward face centroid (arrow points in).

    PWK/DWK (placeable/door walkmeshes) are skipped; the invariant applies to AreaModel (WOK) only.
    """
    if bwm.walkmesh_type != BWMType.AreaModel:
        return  # PWK/DWK have no perimeter/transitions in the same way

    # --- (1) Build the set of edges that have a transition (these are "arrows" in the file) ---
    perimeter = bwm.perimeter_edge_set()  # (face_index, edge_index) for every outer boundary edge
    edges_with_trans: set[tuple[int, int]] = set()
    for i, face in enumerate(bwm.faces):
        if face.trans1 is not None:
            edges_with_trans.add((i, 0))
        if face.trans2 is not None:
            edges_with_trans.add((i, 1))
        if face.trans3 is not None:
            edges_with_trans.add((i, 2))

    # --- Assert: every transition is on a perimeter edge (arrows ONLY on outer edges) ---
    non_perimeter_with_trans = edges_with_trans - perimeter
    assert not non_perimeter_with_trans, (
        f"Transitions on non-perimeter edges (arrows must be EXCLUSIVELY on outer edges): {non_perimeter_with_trans}"
    )

    # --- Assert: ZERO transitions on any non-perimeter edge (redundant but explicit per-face) ---
    for i, face in enumerate(bwm.faces):
        assert (i, 0) in perimeter or face.trans1 is None, (
            f"Face {i} edge 0: transition on internal edge"
        )
        assert (i, 1) in perimeter or face.trans2 is None, (
            f"Face {i} edge 1: transition on internal edge"
        )
        assert (i, 2) in perimeter or face.trans3 is None, (
            f"Face {i} edge 2: transition on internal edge"
        )

    # --- Assert: inward direction = from edge toward face centroid (arrow points into the face) ---
    # BWM.edge_inward_direction_xy(face, edge_idx) returns (midpoint, normalized direction toward centroid).
    # We verify that direction actually points toward the centroid by dot product with (centroid - midpoint).
    for i, face in enumerate(bwm.faces):
        for edge_idx, trans in [(0, face.trans1), (1, face.trans2), (2, face.trans3)]:
            if trans is not None:
                mid, direction = BWM.edge_inward_direction_xy(face, edge_idx)
                # Vector from midpoint to face centroid (XY); same direction as "inward"
                to_centroid_x = (face.v1.x + face.v2.x + face.v3.x) / 3.0 - mid.x
                to_centroid_y = (face.v1.y + face.v2.y + face.v3.y) / 3.0 - mid.y
                dot = direction.x * to_centroid_x + direction.y * to_centroid_y
                # dot > 0 means direction points toward centroid; allow small numerical error
                assert dot >= -1e-6, (
                    f"Face {i} edge {edge_idx}: inward direction points away from centroid (dot={dot})"
                )

    # --- Final check: BWM's own invariant assertion (perimeter-only) ---
    bwm.assert_transition_arrows_invariant()


def test_walkmesh_rebuild_binary_to_file(tmp_path: pathlib.Path) -> None:
    """Run walkmesh-rebuild on a binary WOK; output must exist and match face/vertex counts.

    Also asserts the transition-arrows invariant on the rebuilt mesh (arrows only on perimeter,
    pointing inward; zero elsewhere).
    """
    if not TEST_WOK_FILE.exists():
        pytest.skip(f"Test file not found: {TEST_WOK_FILE}")
    out = tmp_path / "rebuilt.wok"
    exit_code = _run_cli(["walkmesh-rebuild", str(TEST_WOK_FILE), "-o", str(out)])
    assert exit_code == 0
    assert out.exists()
    bwm = read_bwm(out.read_bytes())
    orig = read_bwm(TEST_WOK_FILE.read_bytes())
    assert len(bwm.faces) == len(orig.faces)
    assert len(list(bwm.vertices())) == len(list(orig.vertices()))
    # Arrow invariant: transitions only on perimeter edges, inward direction
    _assert_transition_arrows_exclusive(bwm)


def test_walkmesh_rebuild_overwrite(tmp_path: pathlib.Path) -> None:
    """walkmesh-rebuild without -o overwrites input when input is binary."""
    if not TEST_WOK_FILE.exists():
        pytest.skip(f"Test file not found: {TEST_WOK_FILE}")
    copy = tmp_path / "copy.wok"
    copy.write_bytes(TEST_WOK_FILE.read_bytes())
    exit_code = _run_cli(["walkmesh-rebuild", str(copy)])
    assert exit_code == 0
    bwm = read_bwm(copy.read_bytes())
    orig = read_bwm(TEST_WOK_FILE.read_bytes())
    assert len(bwm.faces) == len(orig.faces)
    _assert_transition_arrows_exclusive(bwm)


def test_walkmesh_rebuild_ascii_input_to_wok(tmp_path: pathlib.Path) -> None:
    """walkmesh-rebuild with ASCII input writes binary WOK to the given -o path.

    Rebuilt mesh must have faces and satisfy the transition-arrows invariant.
    """
    if not ASCII_203TEL.exists():
        pytest.skip(f"ASCII test file not found: {ASCII_203TEL}")
    out = tmp_path / "from_ascii.wok"
    exit_code = _run_cli(["walkmesh-rebuild", str(ASCII_203TEL), "-o", str(out)])
    assert exit_code == 0
    assert out.exists()
    bwm = read_bwm(out.read_bytes())
    assert len(bwm.faces) > 0
    _assert_transition_arrows_exclusive(bwm)


def test_walkmesh_rebuild_with_ascii_flag(tmp_path: pathlib.Path) -> None:
    """walkmesh-rebuild --ascii writes both .wok and .wok.ascii; both must pass arrow invariant."""
    if not TEST_WOK_FILE.exists():
        pytest.skip(f"Test file not found: {TEST_WOK_FILE}")
    out = tmp_path / "rebuilt.wok"
    exit_code = _run_cli(["walkmesh-rebuild", str(TEST_WOK_FILE), "-o", str(out), "--ascii"])
    assert exit_code == 0
    assert out.exists()
    ascii_path = out.with_suffix(out.suffix + ".ascii")
    assert ascii_path.exists()
    bwm = read_bwm(out.read_bytes())
    _assert_transition_arrows_exclusive(bwm)
    # ASCII output is loadable by read_bwm (auto-detect); must also satisfy invariant
    bwm_from_ascii = read_bwm(ascii_path.read_bytes())
    assert len(bwm_from_ascii.faces) > 0
    _assert_transition_arrows_exclusive(bwm_from_ascii)


def test_walkmesh_rebuild_transition_arrows_invariant(tmp_path: pathlib.Path) -> None:
    """Dedicated test for the full transition-arrows invariant after rebuild.

    After rebuilding a WOK we assert exhaustively:
    1. Every edge that has a transition is in the perimeter set (arrows only on outer edges).
    2. Every (face, edge) not in the perimeter has no transition (ZERO arrows on internal edges).
    3. For every edge with a transition, the inward direction points toward the face centroid.
    4. BWM.assert_transition_arrows_invariant() passes (via _assert_transition_arrows_exclusive).

    This is the same logic as _assert_transition_arrows_exclusive; we also assert (1) and (2)
    explicitly here so the test name and docstring make the "arrow thing" obvious.
    """
    if not TEST_WOK_FILE.exists():
        pytest.skip(f"Test file not found: {TEST_WOK_FILE}")
    out = tmp_path / "rebuilt.wok"
    exit_code = _run_cli(["walkmesh-rebuild", str(TEST_WOK_FILE), "-o", str(out)])
    assert exit_code == 0
    assert out.exists()
    bwm = read_bwm(out.read_bytes())
    assert bwm.walkmesh_type == BWMType.AreaModel

    perimeter = bwm.perimeter_edge_set()
    edges_with_trans: set[tuple[int, int]] = set()
    for i, face in enumerate(bwm.faces):
        if face.trans1 is not None:
            edges_with_trans.add((i, 0))
        if face.trans2 is not None:
            edges_with_trans.add((i, 1))
        if face.trans3 is not None:
            edges_with_trans.add((i, 2))
    assert edges_with_trans <= perimeter, "Every transition must be on a perimeter edge"
    for i, face in enumerate(bwm.faces):
        for e, trans in [(0, face.trans1), (1, face.trans2), (2, face.trans3)]:
            assert (i, e) in perimeter or trans is None, "ZERO transitions on non-perimeter edges"

    # Full exhaustive check: perimeter-only + inward direction + BWM.assert_transition_arrows_invariant
    _assert_transition_arrows_exclusive(bwm)


def test_walkmesh_rebuild_missing_input_returns_nonzero() -> None:
    """walkmesh-rebuild with missing input file returns non-zero."""
    exit_code = _run_cli(["walkmesh-rebuild", "/nonexistent/path.wok"])
    assert exit_code != 0


def test_render_bwm_to_pngs_writes_four_views(tmp_path: pathlib.Path) -> None:
    """render_bwm_to_pngs writes 4 PNGs when matplotlib is available."""
    pytest.importorskip("matplotlib")
    from pykotor.tools.walkmesh_render import render_bwm_to_pngs

    bwm = BWM()
    bwm.walkmesh_type = BWMType.AreaModel
    face = BWMFace(
        Vector3(0.0, 0.0, 0.0),
        Vector3(2.0, 0.0, 0.0),
        Vector3(0.0, 2.0, 0.0),
    )
    face.material = SurfaceMaterial.DIRT
    bwm.faces = [face]
    output_stem = tmp_path / "out"
    paths = render_bwm_to_pngs(bwm, output_stem)
    assert len(paths) == 4
    for p in paths:
        assert p.exists(), f"Expected file {p}"
        assert p.stat().st_size > 0, f"Expected non-empty file {p}"
