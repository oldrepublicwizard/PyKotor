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
            (1, 0, 0, 1e6), (-1, 0, 0, 1e6),
            (0, 1, 0, 1e6), (0, -1, 0, 1e6),
            (0, 0, 1, 1e6), (0, 0, -1, 1e6),
        ]:
            buf.extend([nx, ny, nz, d])
        return buf.tobytes()

    def _make_tight_planes(self) -> bytes:
        """Create a tight box from -5 to +5 on all axes."""
        buf = array.array("f")
        for nx, ny, nz, d in [
            (1, 0, 0, 5), (-1, 0, 0, 5),
            (0, 1, 0, 5), (0, -1, 0, 5),
            (0, 0, 1, 5), (0, 0, -1, 5),
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
            (1, 0, 0, 1e6), (-1, 0, 0, 1e6),
            (0, 1, 0, 1e6), (0, -1, 0, 1e6),
            (0, 0, 1, 1e6), (0, 0, -1, 1e6),
        ]:
            planes.extend([nx, ny, nz, d])

        aabbs = struct.pack("6f", -1, -1, -1, 1, 1, 1)
        result = aabb_in_frustum_batch(planes.tobytes(), aabbs)
        assert result[0] == 1
