"""Regression tests for camera yaw/pitch wrapping (orbit continuity across ±π)."""

from __future__ import annotations

import math
import unittest

try:
    from pykotor.gl.scene.camera import Camera
except ImportError:
    import pytest

    pytest.skip("pykotor.gl not available", allow_module_level=True)


class TestCameraAngleWrapping(unittest.TestCase):
    """Yaw must stay in [-π, π] after unconstrained rotates; pitch wraps the same way."""

    def test_yaw_wraps_across_positive_pi_boundary(self) -> None:
        camera = Camera()
        camera.yaw = math.pi - 0.05
        camera.rotate(0.1, 0.0, clamp=False)
        self.assertGreater(camera.yaw, -math.pi - 1e-6)
        self.assertLessEqual(camera.yaw, math.pi + 1e-6)
        self.assertAlmostEqual(camera.yaw, -math.pi + 0.05, places=5)

    def test_yaw_wraps_across_negative_pi_boundary(self) -> None:
        camera = Camera()
        camera.yaw = -math.pi + 0.05
        camera.rotate(-0.1, 0.0, clamp=False)
        self.assertGreater(camera.yaw, -math.pi - 1e-6)
        self.assertLessEqual(camera.yaw, math.pi + 1e-6)
        self.assertAlmostEqual(camera.yaw, math.pi - 0.05, places=5)

    def test_pitch_wraps_when_not_clamped(self) -> None:
        camera = Camera()
        camera.pitch = math.pi - 0.02
        camera.rotate(0.0, 0.05, clamp=False)
        self.assertAlmostEqual(camera.pitch, -math.pi + 0.03, places=5)

    def test_clamped_pitch_does_not_wrap(self) -> None:
        camera = Camera()
        camera.pitch = math.pi / 2 + 0.2
        camera.rotate(0.0, 5.0, clamp=True, lower_limit=0.0, upper_limit=math.pi)
        self.assertLess(camera.pitch, math.pi)
        self.assertGreater(camera.pitch, math.pi / 2)
