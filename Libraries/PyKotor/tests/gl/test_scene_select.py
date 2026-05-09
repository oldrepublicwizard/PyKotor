"""Regression tests for Scene.select GITObject vs RenderObject resolution."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from pykotor.gl.scene.render_object import RenderObject
from pykotor.resource.generics.git import GITCamera

try:
    from pykotor.gl.scene import scene as scene_module
    from pykotor.gl.scene.scene import Scene
except ImportError:
    import pytest

    pytest.skip("pykotor.gl not available", allow_module_level=True)


class TestSceneSelect(unittest.TestCase):
    """Scene.select must resolve GITObject (e.g. GITCamera) to the owning RenderObject."""

    def setUp(self) -> None:
        # Avoid compiling GLSL in environments without a valid GL context (CI/headless).
        patcher = patch.object(scene_module, "HAS_PYOPENGL", False)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.scene = Scene()
        self.scene.selection.clear()

    def test_select_git_camera_finds_render_object_by_data(self) -> None:
        cam = GITCamera(x=1.0, y=2.0, z=3.0)
        ro = RenderObject("camera", data=cam)
        self.scene.objects[cam] = ro

        self.scene.select(cam, clear_existing=True)

        self.assertEqual(len(self.scene.selection), 1)
        self.assertIs(self.scene.selection[0], ro)

    def test_select_render_object_direct(self) -> None:
        ro = RenderObject("empty")
        self.scene.select(ro, clear_existing=True)
        self.assertEqual(self.scene.selection, [ro])

    def test_select_unknown_git_object_clears_selection(self) -> None:
        orphan = GITCamera()
        self.scene.objects.clear()
        self.scene.selection.append(RenderObject("placeholder"))

        self.scene.select(orphan, clear_existing=True)

        self.assertEqual(self.scene.selection, [])

    def test_select_git_without_clear_appends(self) -> None:
        first = RenderObject("a")
        cam = GITCamera()
        second = RenderObject("camera", data=cam)
        self.scene.objects[cam] = second

        self.scene.select(first, clear_existing=True)
        self.scene.select(cam, clear_existing=False)

        self.assertEqual(self.scene.selection, [first, second])


if __name__ == "__main__":
    unittest.main()
