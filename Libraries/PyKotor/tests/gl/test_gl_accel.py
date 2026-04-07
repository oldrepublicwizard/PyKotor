"""Tests for the _gl_accel C extension and gl_accel Python wrapper."""

from __future__ import annotations

import array
import math
import struct

import pytest

from pykotor.gl.native.gl_accel import c_available

# Skip all tests if C extension is not available.
pytestmark = pytest.mark.skipif(not c_available(), reason="C extension _gl_accel not compiled")


class TestExtractFrustumPlanes:
    def test_identity_matrix(self):
        from pykotor.gl.native._gl_accel import extract_frustum_planes

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        result = extract_frustum_planes(identity)
        assert len(result) == 96  # 24 floats × 4 bytes

    def test_planes_are_normalized(self):
        from pykotor.gl.native._gl_accel import extract_frustum_planes

        # Use a non-trivial matrix
        m = struct.pack("16f", 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, -1, -1, 0, 0, -0.2, 0)
        result = extract_frustum_planes(m)
        floats = struct.unpack("24f", result)
        for i in range(6):
            nx, ny, nz = floats[i * 4], floats[i * 4 + 1], floats[i * 4 + 2]
            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            assert abs(length - 1.0) < 0.01 or length < 1e-8  # normalized or degenerate

    def test_rejects_wrong_size(self):
        from pykotor.gl.native._gl_accel import extract_frustum_planes

        with pytest.raises((ValueError, TypeError)):
            extract_frustum_planes(b"\x00" * 10)


class TestBatchFrustumCull:
    def _make_open_planes(self) -> bytes:
        """Create planes that accept everything (normals pointing inward, huge d)."""
        buf = array.array("f")
        for nx, ny, nz, d in [
            (1, 0, 0, 1e6),
            (-1, 0, 0, 1e6),
            (0, 1, 0, 1e6),
            (0, -1, 0, 1e6),
            (0, 0, 1, 1e6),
            (0, 0, -1, 1e6),
        ]:
            buf.extend([nx, ny, nz, d])
        return buf.tobytes()

    def _make_tight_planes(self) -> bytes:
        """Create a tight box from -5 to +5 on all axes."""
        buf = array.array("f")
        for nx, ny, nz, d in [
            (1, 0, 0, 5),
            (-1, 0, 0, 5),
            (0, 1, 0, 5),
            (0, -1, 0, 5),
            (0, 0, 1, 5),
            (0, 0, -1, 5),
        ]:
            buf.extend([nx, ny, nz, d])
        return buf.tobytes()

    def test_all_visible(self):
        from pykotor.gl.native._gl_accel import batch_frustum_cull

        planes = self._make_open_planes()
        spheres = struct.pack("8f", 0, 0, 0, 1.0, 100, 200, 300, 10.0)
        result = batch_frustum_cull(planes, spheres)
        assert list(result) == [1, 1]

    def test_mixed_visibility(self):
        from pykotor.gl.native._gl_accel import batch_frustum_cull

        planes = self._make_tight_planes()
        # Sphere at origin (visible), sphere far away (culled)
        spheres = struct.pack("8f", 0, 0, 0, 1.0, 100, 100, 100, 1.0)
        result = batch_frustum_cull(planes, spheres)
        assert result[0] == 1  # at origin, visible
        assert result[1] == 0  # far away, culled

    def test_empty_spheres(self):
        from pykotor.gl.native._gl_accel import batch_frustum_cull

        planes = self._make_open_planes()
        result = batch_frustum_cull(planes, b"")
        assert len(result) == 0


class TestTransformBounds:
    def test_identity_transform(self):
        from pykotor.gl.native._gl_accel import transform_bounds

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        verts = struct.pack("6f", 1, 2, 3, -1, -2, -3)
        result = transform_bounds(verts, 2, 12, 0, identity)
        assert len(result) == 2
        assert abs(result[0][0] - (-1.0)) < 1e-5
        assert abs(result[0][1] - (-2.0)) < 1e-5
        assert abs(result[0][2] - (-3.0)) < 1e-5
        assert abs(result[1][0] - 1.0) < 1e-5
        assert abs(result[1][1] - 2.0) < 1e-5
        assert abs(result[1][2] - 3.0) < 1e-5

    def test_translation_transform(self):
        from pykotor.gl.native._gl_accel import transform_bounds

        # Column-major translation: translate by (10, 20, 30)
        mat = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 20, 30, 1)
        verts = struct.pack("3f", 0, 0, 0)
        result = transform_bounds(verts, 1, 12, 0, mat)
        assert abs(result[0][0] - 10.0) < 1e-5
        assert abs(result[0][1] - 20.0) < 1e-5
        assert abs(result[0][2] - 30.0) < 1e-5

    def test_zero_vertices(self):
        from pykotor.gl.native._gl_accel import transform_bounds

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        result = transform_bounds(b"", 0, 12, 0, identity)
        for v in result[0] + result[1]:
            assert v == 0.0


class TestMat4MultiplyBatch:
    def test_identity_multiply(self):
        from pykotor.gl.native._gl_accel import mat4_multiply_batch

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        # Two identity matrices
        transforms = identity + identity
        result = mat4_multiply_batch(transforms, identity)
        floats = struct.unpack("32f", result)
        # Each should still be identity
        for i in range(2):
            for row in range(4):
                for col in range(4):
                    expected = 1.0 if row == col else 0.0
                    assert abs(floats[i * 16 + col * 4 + row] - expected) < 1e-5


class TestAabbInFrustumBatch:
    def test_visible_aabb(self):
        from pykotor.gl.native._gl_accel import aabb_in_frustum_batch

        # Open frustum
        planes = array.array("f")
        for nx, ny, nz, d in [
            (1, 0, 0, 1e6),
            (-1, 0, 0, 1e6),
            (0, 1, 0, 1e6),
            (0, -1, 0, 1e6),
            (0, 0, 1, 1e6),
            (0, 0, -1, 1e6),
        ]:
            planes.extend([nx, ny, nz, d])

        aabbs = struct.pack("6f", -1, -1, -1, 1, 1, 1)
        result = aabb_in_frustum_batch(planes.tobytes(), aabbs)
        assert result[0] == 1


class TestComputeNodeWorldTransforms:
    """Tests for the compute_node_world_transforms C function."""

    def test_single_root_node_identity(self):
        """Single root node with identity local and root transforms -> identity result."""
        from pykotor.gl.native._gl_accel import compute_node_world_transforms

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        parents = struct.pack("i", -1)  # root node
        result = compute_node_world_transforms(identity, parents, identity)
        out = struct.unpack("16f", result)
        # Should be identity * identity = identity
        expected = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        for a, b in zip(out, expected):
            assert abs(a - b) < 1e-6

    def test_root_translation_propagates(self):
        """Root transform with translation should propagate to all nodes."""
        from pykotor.gl.native._gl_accel import compute_node_world_transforms

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        # Root transform: translate by (10, 20, 30): column-major
        root = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 10, 20, 30, 1)
        parents = struct.pack("i", -1)
        result = compute_node_world_transforms(identity, parents, root)
        out = struct.unpack("16f", result)
        # out should be root * identity = root
        assert abs(out[12] - 10) < 1e-6
        assert abs(out[13] - 20) < 1e-6
        assert abs(out[14] - 30) < 1e-6

    def test_parent_child_chain(self):
        """3 nodes: root -> child -> grandchild. Translations should accumulate."""
        from pykotor.gl.native._gl_accel import compute_node_world_transforms

        # Node 0: root with identity local
        # Node 1: child of 0, local translate (5, 0, 0)
        # Node 2: child of 1, local translate (0, 3, 0)
        node0 = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)  # identity
        node1 = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 5, 0, 0, 1)  # tx=5
        node2 = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 3, 0, 1)  # ty=3

        locals_bytes = node0 + node1 + node2
        parents = struct.pack("3i", -1, 0, 1)
        root = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)

        result = compute_node_world_transforms(locals_bytes, parents, root)
        assert len(result) == 3 * 64  # 3 nodes × 16 floats × 4 bytes

        # Node 0: root * identity = identity
        out0 = struct.unpack_from("16f", result, 0)
        assert abs(out0[12]) < 1e-6
        assert abs(out0[13]) < 1e-6

        # Node 1: root * identity * translate(5,0,0) = translate(5,0,0)
        out1 = struct.unpack_from("16f", result, 64)
        assert abs(out1[12] - 5) < 1e-6
        assert abs(out1[13]) < 1e-6

        # Node 2: translate(5,0,0) * translate(0,3,0) = translate(5,3,0)
        out2 = struct.unpack_from("16f", result, 128)
        assert abs(out2[12] - 5) < 1e-6
        assert abs(out2[13] - 3) < 1e-6

    def test_rejects_mismatched_sizes(self):
        """Should raise ValueError if parent_indices size doesn't match node count."""
        from pykotor.gl.native._gl_accel import compute_node_world_transforms

        identity = struct.pack("16f", 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)
        wrong_parents = struct.pack("2i", -1, 0)  # 2 parents but only 1 node
        with pytest.raises(ValueError):
            compute_node_world_transforms(identity, wrong_parents, identity)


class TestBatchTransformVertices2D:
    """Tests for batch_transform_vertices_2d C function."""

    def test_identity_transform(self):
        """No flip, no rotation, no translation -> vertices unchanged."""
        from pykotor.gl.native._gl_accel import batch_transform_vertices_2d

        verts = struct.pack("6f", 1.0, 2.0, 3.0, 4.0, 5.0, 6.0)  # 3 vertices
        result_bytes, bounds = batch_transform_vertices_2d(verts, 1.0, 0.0, False, False, 0.0, 0.0)
        out = struct.unpack("6f", result_bytes)
        assert abs(out[0] - 1.0) < 1e-6
        assert abs(out[1] - 2.0) < 1e-6
        assert abs(out[2] - 3.0) < 1e-6
        assert abs(out[3] - 4.0) < 1e-6
        assert abs(out[4] - 5.0) < 1e-6
        assert abs(out[5] - 6.0) < 1e-6
        # Bounds: min(1,3,5)=1, min(2,4,6)=2, max(1,3,5)=5, max(2,4,6)=6
        assert abs(bounds[0] - 1.0) < 1e-6
        assert abs(bounds[1] - 2.0) < 1e-6
        assert abs(bounds[2] - 5.0) < 1e-6
        assert abs(bounds[3] - 6.0) < 1e-6

    def test_translation_only(self):
        """Translation shifts all vertices and bounds."""
        from pykotor.gl.native._gl_accel import batch_transform_vertices_2d

        verts = struct.pack("4f", 0.0, 0.0, 1.0, 1.0)  # 2 vertices
        result_bytes, bounds = batch_transform_vertices_2d(
            verts, 1.0, 0.0, False, False, 10.0, 20.0
        )
        out = struct.unpack("4f", result_bytes)
        assert abs(out[0] - 10.0) < 1e-6
        assert abs(out[1] - 20.0) < 1e-6
        assert abs(out[2] - 11.0) < 1e-6
        assert abs(out[3] - 21.0) < 1e-6

    def test_90_degree_rotation(self):
        """90-degree rotation: (1,0) -> (0,1)."""
        from pykotor.gl.native._gl_accel import batch_transform_vertices_2d

        cos_r = math.cos(math.radians(90.0))
        sin_r = math.sin(math.radians(90.0))
        verts = struct.pack("2f", 1.0, 0.0)
        result_bytes, _ = batch_transform_vertices_2d(verts, cos_r, sin_r, False, False, 0.0, 0.0)
        out = struct.unpack("2f", result_bytes)
        assert abs(out[0] - 0.0) < 1e-5  # x ~ 0
        assert abs(out[1] - 1.0) < 1e-5  # y ~ 1

    def test_flip_x(self):
        """flip_x negates x before rotation."""
        from pykotor.gl.native._gl_accel import batch_transform_vertices_2d

        verts = struct.pack("2f", 3.0, 5.0)
        result_bytes, _ = batch_transform_vertices_2d(verts, 1.0, 0.0, True, False, 0.0, 0.0)
        out = struct.unpack("2f", result_bytes)
        assert abs(out[0] - (-3.0)) < 1e-6
        assert abs(out[1] - 5.0) < 1e-6

    def test_flip_y(self):
        """flip_y negates y before rotation."""
        from pykotor.gl.native._gl_accel import batch_transform_vertices_2d

        verts = struct.pack("2f", 3.0, 5.0)
        result_bytes, _ = batch_transform_vertices_2d(verts, 1.0, 0.0, False, True, 0.0, 0.0)
        out = struct.unpack("2f", result_bytes)
        assert abs(out[0] - 3.0) < 1e-6
        assert abs(out[1] - (-5.0)) < 1e-6


class TestBatchHookSnapDistances:
    """Tests for batch_hook_snap_distances C function."""

    def test_no_snap_when_far(self):
        """All hooks far from position -> returns None."""
        from pykotor.gl.native._gl_accel import batch_hook_snap_distances

        existing = struct.pack("2f", 100.0, 100.0)  # 1 hook at (100, 100)
        test_local = struct.pack("2f", 0.0, 0.0)  # 1 hook at origin in local
        result = batch_hook_snap_distances(existing, test_local, 0.0, 0.0, 5.0)
        assert result is None

    def test_snap_found(self):
        """Hook within snap threshold -> returns best snap."""
        from pykotor.gl.native._gl_accel import batch_hook_snap_distances

        # Existing hook at (10, 0), test hook local offset (0, 0)
        # Position at (9.5, 0) -> snap_pos = (10-0, 0-0) = (10, 0)
        # Distance = |9.5-10| = 0.5, < threshold 5.0
        existing = struct.pack("2f", 10.0, 0.0)
        test_local = struct.pack("2f", 0.0, 0.0)
        result = batch_hook_snap_distances(existing, test_local, 9.5, 0.0, 5.0)
        assert result is not None
        dist, test_idx, existing_idx, snap_x, snap_y = result
        assert abs(dist - 0.5) < 1e-5
        assert test_idx == 0
        assert existing_idx == 0
        assert abs(snap_x - 10.0) < 1e-6
        assert abs(snap_y - 0.0) < 1e-6

    def test_picks_closest(self):
        """Multiple hooks -> picks closest one."""
        from pykotor.gl.native._gl_accel import batch_hook_snap_distances

        # Two existing hooks: (2, 0) and (1, 0)
        existing = struct.pack("4f", 2.0, 0.0, 1.0, 0.0)
        test_local = struct.pack("2f", 0.0, 0.0)
        # Position at (0.8, 0) -> distances: |0.8-2|=1.2, |0.8-1|=0.2
        result = batch_hook_snap_distances(existing, test_local, 0.8, 0.0, 5.0)
        assert result is not None
        dist, test_idx, existing_idx, snap_x, snap_y = result
        assert abs(dist - 0.2) < 1e-5
        assert existing_idx == 1  # second hook is closer
        assert abs(snap_x - 1.0) < 1e-6

    def test_local_offset_applied(self):
        """Test that test hook local offset is applied."""
        from pykotor.gl.native._gl_accel import batch_hook_snap_distances

        # Existing hook at (10, 0), test hook local offset (3, 0)
        # snap_pos = (10-3, 0-0) = (7, 0). Position at (7, 0) -> distance 0
        existing = struct.pack("2f", 10.0, 0.0)
        test_local = struct.pack("2f", 3.0, 0.0)
        result = batch_hook_snap_distances(existing, test_local, 7.0, 0.0, 5.0)
        assert result is not None
        dist, _, _, snap_x, snap_y = result
        assert abs(dist) < 1e-5
        assert abs(snap_x - 7.0) < 1e-6


class TestBatchVerticesInRect:
    """Tests for batch_vertices_in_rect C function."""

    def test_vertex_inside(self):
        """Vertex that lands inside rect -> returns 1."""
        from pykotor.gl.native._gl_accel import batch_vertices_in_rect

        verts = struct.pack("2f", 5.0, 5.0)
        result = batch_vertices_in_rect(
            verts, 1.0, 0.0, False, False, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0
        )
        assert result == 1

    def test_vertex_outside(self):
        """All vertices outside rect -> returns 0."""
        from pykotor.gl.native._gl_accel import batch_vertices_in_rect

        verts = struct.pack("2f", 50.0, 50.0)
        result = batch_vertices_in_rect(
            verts, 1.0, 0.0, False, False, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0
        )
        assert result == 0

    def test_translation_brings_inside(self):
        """Vertex at (5,5) + translate (10,10) = (15,15) inside rect (10,10,20,20)."""
        from pykotor.gl.native._gl_accel import batch_vertices_in_rect

        verts = struct.pack("2f", 5.0, 5.0)
        result = batch_vertices_in_rect(
            verts, 1.0, 0.0, False, False, 10.0, 10.0, 10.0, 10.0, 20.0, 20.0
        )
        assert result == 1

    def test_flip_moves_outside(self):
        """flip_x negates x: (5,5) -> (-5,5), outside (0,0,10,10)."""
        from pykotor.gl.native._gl_accel import batch_vertices_in_rect

        verts = struct.pack("2f", 5.0, 5.0)
        result = batch_vertices_in_rect(
            verts, 1.0, 0.0, True, False, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0
        )
        assert result == 0

    def test_early_termination(self):
        """Multiple vertices: first outside, second inside -> returns 1."""
        from pykotor.gl.native._gl_accel import batch_vertices_in_rect

        verts = struct.pack("4f", 50.0, 50.0, 5.0, 5.0)
        result = batch_vertices_in_rect(
            verts, 1.0, 0.0, False, False, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0
        )
        assert result == 1
