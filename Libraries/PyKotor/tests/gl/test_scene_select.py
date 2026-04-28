"""Tests for Scene.select GITObject resolution (editor selection path)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

try:
    from pykotor.gl.scene import RenderObject, Scene
    from pykotor.gl.scene.scene_cache import SceneCache
    from pykotor.resource.generics.git import GIT, GITWaypoint
except ImportError:
    import pytest

    pytest.skip("pykotor.gl.scene.Scene not available", allow_module_level=True)


class TestSceneSelect(unittest.TestCase):
    """Regression: select() must accept any GITObject subtype (e.g. GITWaypoint), not only GITInstance."""

    def setUp(self) -> None:
        # Avoid full module/layout resolution; we only test selection ↔ RenderObject.data matching.
        self._cache_patcher = patch.object(
            SceneCache,
            "build_cache",
            staticmethod(lambda _scene, **_kwargs: None),
        )
        self._cache_patcher.start()
        self.addCleanup(self._cache_patcher.stop)

        self.scene: Scene = Scene()
        self.scene.git = GIT()
        self.waypoint: GITWaypoint = GITWaypoint(1.0, 2.0, 3.0)
        self.scene.git.waypoints.append(self.waypoint)
        self.ro: RenderObject = RenderObject("waypoint", data=self.waypoint)
        self.scene.objects[self.waypoint] = self.ro

    def test_select_git_waypoint_resolves_to_render_object(self) -> None:
        self.scene.select(self.waypoint, clear_existing=True)
        self.assertEqual(len(self.scene.selection), 1)
        self.assertIs(self.scene.selection[0], self.ro)

    def test_select_render_object_direct(self) -> None:
        self.scene.select(self.ro, clear_existing=True)
        self.assertEqual(len(self.scene.selection), 1)
        self.assertIs(self.scene.selection[0], self.ro)

    def test_select_unknown_git_object_leaves_selection_empty(self) -> None:
        orphan: GITWaypoint = GITWaypoint(0.0, 0.0, 0.0)
        self.scene.select(orphan, clear_existing=True)
        self.assertEqual(self.scene.selection, [])

    def test_select_clear_existing_false_appends(self) -> None:
        other = RenderObject("empty", data=None)
        self.scene.selection.append(other)
        self.scene.select(self.waypoint, clear_existing=False)
        self.assertEqual(len(self.scene.selection), 2)
        self.assertIs(self.scene.selection[0], other)
        self.assertIs(self.scene.selection[1], self.ro)


if __name__ == "__main__":
    unittest.main()
