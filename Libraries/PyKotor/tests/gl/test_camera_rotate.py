"""Tests for Camera.rotate angle wrapping and clamp edge cases.

Regression coverage for orbit-style rotation: yaw must stay in [-pi, pi],
optional pitch clamping must handle inverted limits safely, and unclamped
pitch must wrap like yaw.
"""

from __future__ import annotations

import math
import unittest

try:
    from pykotor.gl.scene.camera import Camera, _wrap_angle_pi
except ImportError:
    import pytest

    pytest.skip("pykotor.gl not available", allow_module_level=True)


def _angles_equivalent_mod_2pi(a: float, b: float) -> bool:
    """True if ``a`` and ``b`` differ by a multiple of 2π (within float tolerance)."""
    delta = (a - b + math.pi) % (2 * math.pi) - math.pi
    return math.isclose(delta, 0.0, abs_tol=1e-9)


class TestWrapAnglePi(unittest.TestCase):
    def test_wrap_angle_pi_range(self):
        for angle, expected in (
            (0.0, 0.0),
            (math.pi, -math.pi),  # π maps to −π (same heading modulo 2π)
            (-math.pi, -math.pi),
            (3 * math.pi, -math.pi),
            (-3 * math.pi, -math.pi),
            (2 * math.pi, 0.0),
            (2.5 * math.pi, 0.5 * math.pi),
        ):
            with self.subTest(angle=angle):
                got = _wrap_angle_pi(angle)
                self.assertTrue(
                    _angles_equivalent_mod_2pi(expected, got),
                    msg=f"expected {expected!r} ≡ {got!r} (mod 2π)",
                )


class TestCameraRotate(unittest.TestCase):
    def setUp(self):
        self.cam = Camera(pitch=0.0, yaw=0.0)

    def test_rotate_yaw_wraps_to_minus_pi_pi(self):
        self.cam.rotate(4 * math.pi, 0.0, clamp=False)
        self.assertGreaterEqual(self.cam.yaw, -math.pi)
        self.assertLessEqual(self.cam.yaw, math.pi)
        self.assertAlmostEqual(0.0, self.cam.yaw, places=9)

    def test_rotate_yaw_fractional_turn(self):
        self.cam.rotate(2.5 * math.pi, 0.0, clamp=False)
        self.assertAlmostEqual(0.5 * math.pi, self.cam.yaw, places=9)

    def test_rotate_pitch_wraps_when_not_clamped(self):
        self.cam.rotate(0.0, 3 * math.pi, clamp=False)
        self.assertTrue(
            _angles_equivalent_mod_2pi(math.pi, self.cam.pitch),
            msg=f"expected pitch ≡ π (mod 2π), got {self.cam.pitch!r}",
        )

    def test_rotate_clamp_respects_limits(self):
        self.cam.pitch = math.pi / 2
        self.cam.rotate(0.0, 10.0, clamp=True, lower_limit=0.0, upper_limit=math.pi)
        self.assertLessEqual(self.cam.pitch, math.pi - 0.01)
        self.assertGreaterEqual(self.cam.pitch, 0.01)

    def test_rotate_clamp_inverted_limits_uses_midpoint(self):
        """If lower > upper, pitch snaps to the midpoint (degenerate range)."""
        lower = 1.0
        upper = 0.5
        self.cam.pitch = 0.25
        self.cam.rotate(0.0, 0.0, clamp=True, lower_limit=lower, upper_limit=upper)
        midpoint = (lower + upper) * 0.5
        self.assertAlmostEqual(midpoint, self.cam.pitch, places=9)
