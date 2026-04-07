from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


class _DummyShader:
    def __init__(self) -> None:
        self.float_values: dict[str, float] = {}
        self.float_history: list[tuple[str, float]] = []

    def use(self) -> None:
        return

    def uniform(self, _name: str) -> int:
        return 0

    def set_matrix4(self, _name: str, _value) -> None:
        return

    def set_float(self, name: str, value: float) -> None:
        self.float_values[name] = value
        self.float_history.append((name, value))


class _DummyTexture:
    def __init__(self, *, blend_mode: int, alpha_cutoff: float, has_alpha: bool, _id: int = 1) -> None:
        self.blend_mode: int = blend_mode
        self.alpha_cutoff: float = alpha_cutoff
        self.has_alpha: bool = has_alpha
        self._id: int = _id

    def use(self) -> None:
        return


class _DummyScene:
    def __init__(self, diffuse: _DummyTexture) -> None:
        self._diffuse: _DummyTexture = diffuse
        self._lightmap: _DummyTexture = _DummyTexture(
            blend_mode=0, alpha_cutoff=0.0, has_alpha=False
        )
        self.textures: dict[str, _DummyTexture] = {"diffuse": diffuse, "NULL": self._lightmap}

    def texture(self, name: str, *, lightmap: bool = False):
        _ = name
        return self._lightmap if lightmap else self._diffuse


def _build_mesh(diffuse: _DummyTexture):
    from pykotor.gl.models import mdl

    mesh = mdl.Mesh.__new__(mdl.Mesh)
    mesh.scene = _DummyScene(diffuse)  # pyright: ignore[reportAttributeAccessIssue]
    mesh.texture = "diffuse"
    mesh.lightmap = "NULL"
    mesh._vao = 1
    mesh._face_count = 3
    mesh._cached_diffuse_tex = None
    mesh._cached_diffuse_name = ""
    mesh._cached_lightmap_tex = None
    mesh._cached_lightmap_name = ""
    mesh._cached_tex_gen = -1
    return mesh


def test_default_alpha_texture_renders_opaque(monkeypatch: pytest.MonkeyPatch):
    from pykotor.gl.models import mdl
    from pykotor.gl.models.mdl import Mesh

    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(mdl, "HAS_PYOPENGL", True)
    monkeypatch.setattr(mdl, "glEnable", lambda value: calls.append(("enable", value)))
    monkeypatch.setattr(mdl, "glDisable", lambda value: calls.append(("disable", value)))
    monkeypatch.setattr(mdl, "glBlendFunc", lambda src, dst: calls.append(("blend", (src, dst))))
    monkeypatch.setattr(mdl, "glDepthMask", lambda value: calls.append(("depth", value)))
    monkeypatch.setattr(mdl, "glActiveTexture", lambda value: calls.append(("active", value)))
    monkeypatch.setattr(mdl, "glBindVertexArray", lambda value: calls.append(("vao", value)))
    monkeypatch.setattr(mdl, "glDrawElements", lambda *_args: calls.append(("draw", None)))
    monkeypatch.setattr(mdl, "glUniformMatrix4fv", lambda *_args: calls.append(("uniform_mat4", None)))
    monkeypatch.setattr(mdl, "glBindTexture", lambda *_args: calls.append(("bind_tex", None)))
    monkeypatch.setattr(mdl, "value_ptr", lambda _v: None)

    shader = _DummyShader()
    diffuse = _DummyTexture(blend_mode=0, alpha_cutoff=0.0, has_alpha=True)
    mesh = _build_mesh(diffuse)

    # Reset draw state tracking (as the render loop does at frame start)
    Mesh.reset_draw_state()
    mesh.draw(shader, object())  # pyright: ignore[reportArgumentType]

    assert ("disable", mdl.GL_BLEND) in calls
    assert ("alphaCutoff", 0.0) in shader.float_history
    assert shader.float_values["alphaCutoff"] == 0.0


def test_cutout_texture_disables_regular_blending(monkeypatch: pytest.MonkeyPatch):
    from pykotor.gl.models import mdl
    from pykotor.gl.models.mdl import Mesh

    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(mdl, "HAS_PYOPENGL", True)
    monkeypatch.setattr(mdl, "glEnable", lambda value: calls.append(("enable", value)))
    monkeypatch.setattr(mdl, "glDisable", lambda value: calls.append(("disable", value)))
    monkeypatch.setattr(mdl, "glBlendFunc", lambda src, dst: calls.append(("blend", (src, dst))))
    monkeypatch.setattr(mdl, "glDepthMask", lambda value: calls.append(("depth", value)))
    monkeypatch.setattr(mdl, "glActiveTexture", lambda value: calls.append(("active", value)))
    monkeypatch.setattr(mdl, "glBindVertexArray", lambda value: calls.append(("vao", value)))
    monkeypatch.setattr(mdl, "glDrawElements", lambda *_args: calls.append(("draw", None)))
    monkeypatch.setattr(mdl, "glUniformMatrix4fv", lambda *_args: calls.append(("uniform_mat4", None)))
    monkeypatch.setattr(mdl, "glBindTexture", lambda *_args: calls.append(("bind_tex", None)))
    monkeypatch.setattr(mdl, "value_ptr", lambda _v: None)

    shader = _DummyShader()
    diffuse = _DummyTexture(blend_mode=0, alpha_cutoff=0.01, has_alpha=True)
    mesh = _build_mesh(diffuse)

    # Reset draw state tracking (as the render loop does at frame start)
    Mesh.reset_draw_state()
    mesh.draw(shader, object())  # pyright: ignore[reportArgumentType]

    assert ("disable", mdl.GL_BLEND) in calls
    assert ("alphaCutoff", 0.01) in shader.float_history
