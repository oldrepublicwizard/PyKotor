"""Regression tests for Scene.select (GITObject vs RenderObject, selection list semantics)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from utility.common.geometry import Vector3

try:
    from pykotor.gl.scene import RenderObject
    from pykotor.gl.scene.scene import Scene
    from pykotor.resource.generics.git import GITWaypoint
except ImportError:
    import pytest

    pytest.skip("pykotor.gl not available", allow_module_level=True)


class _StubShader:
    """Avoid compiling real GLSL when no GL context exists (CI / headless)."""

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self._id = 0

    def use(self) -> None:
        return

    def set_matrix4(self, *_a: object, **_k: object) -> None:
        return

    def set_vector3(self, *_a: object, **_k: object) -> None:
        return

    def set_vector4(self, *_a: object, **_k: object) -> None:
        return


class _StubAxisGizmo:
    def __init__(self) -> None:
        return


class TestSceneSelect(unittest.TestCase):
    def setUp(self) -> None:
        self._patch_shader = patch("pykotor.gl.scene.scene.Shader", _StubShader)
        self._patch_gizmo = patch("pykotor.gl.scene.scene.AxisGizmo", _StubAxisGizmo)
        self._patch_shader.start()
        self._patch_gizmo.start()

    def tearDown(self) -> None:
        self._patch_gizmo.stop()
        self._patch_shader.stop()

    def _scene(self) -> Scene:
        scene = Scene()
        self.addCleanup(scene.shutdown, wait=True)
        return scene

    def test_select_git_instance_resolves_render_object(self) -> None:
        scene = self._scene()
        waypoint = GITWaypoint()
        ro = RenderObject("waypoint", Vector3(1.0, 2.0, 3.0), data=waypoint)
        scene.objects[waypoint] = ro

        scene.select(waypoint)

        self.assertEqual(scene.selection, [ro])

    def test_select_render_object_direct(self) -> None:
        scene = self._scene()
        ro = RenderObject("trigger", data=None)
        scene.select(ro)
        self.assertEqual(scene.selection, [ro])

    def test_select_unknown_git_object_clears_but_does_not_append(self) -> None:
        scene = self._scene()
        orphan = GITWaypoint()
        scene.selection.append(RenderObject("sound"))

        scene.select(orphan, clear_existing=True)

        self.assertEqual(scene.selection, [])

    def test_clear_existing_false_appends(self) -> None:
        scene = self._scene()
        first = RenderObject("sound")
        second = RenderObject("encounter")
        scene.select(first)
        scene.select(second, clear_existing=False)
        self.assertEqual(scene.selection, [first, second])
