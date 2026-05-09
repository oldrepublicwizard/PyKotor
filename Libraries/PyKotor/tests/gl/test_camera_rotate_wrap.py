"""Regression tests for Camera.rotate angle wrapping (yaw/pitch normalization)."""

from __future__ import annotations

import math
import unittest

try:
    from pykotor.gl.scene.camera import Camera
except ImportError:
    import pytest

    pytest.skip("pykotor.gl not available", allow_module_level=True)


class TestCameraRotateAngleWrap(unittest.TestCase):
    """Covers _wrap_angle_pi behavior via public Camera.rotate(clamp=False)."""

    def setUp(self) -> None:
        self.camera = Camera()
        self.camera.yaw = 0.0
        self.camera.pitch = math.pi / 2

    def test_yaw_wraps_large_positive_to_minus_pi_pi(self) -> None:
        self.camera.yaw = 3.0
        self.camera.rotate(yaw=4.0, pitch=0.0, clamp=False)
        self.assertGreater(self.camera.yaw, -math.pi)
        self.assertLessEqual(self.camera.yaw, math.pi)

    def test_yaw_wraps_large_negative(self) -> None:
        self.camera.yaw = -3.0
        self.camera.rotate(yaw=-4.0, pitch=0.0, clamp=False)
        self.assertGreater(self.camera.yaw, -math.pi)
        self.assertLessEqual(self.camera.yaw, math.pi)

    def test_pitch_wraps_without_clamp(self) -> None:
        self.camera.pitch = 0.5
        self.camera.rotate(yaw=0.0, pitch=2.0 * math.pi + 0.1, clamp=False)
        self.assertGreater(self.camera.pitch, -math.pi)
        self.assertLessEqual(self.camera.pitch, math.pi)

    def test_rotate_with_clamp_respects_pitch_limits(self) -> None:
        self.camera.pitch = math.pi / 2
        self.camera.rotate(
            yaw=0.0,
            pitch=10.0,
            clamp=True,
            lower_limit=0.0,
            upper_limit=math.pi,
        )
        self.assertLess(self.camera.pitch, math.pi)
        self.assertGreater(self.camera.pitch, 0.0)


if __name__ == "__main__":
    unittest.main()
