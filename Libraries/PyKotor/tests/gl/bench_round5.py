"""Round 5 micro-benchmarks: measure savings from Python-level overhead elimination.

Run: uv run python Libraries/PyKotor/tests/gl/bench_round5.py
"""

from __future__ import annotations

import time


def bench_should_hide_precomputed():
    """Compare isinstance-chain vs precomputed attribute lookup for should_hide."""

    class FakeObj:
        __slots__ = ("_hide_attr",)

        def __init__(self, attr: str):
            self._hide_attr = attr

    class FakeScene:
        hide_creatures = True
        hide_placeables = False
        hide_doors = False

    scene = FakeScene()

    # Old approach: isinstance chain (simulated with type checks)
    class GITCreature:
        pass

    class GITPlaceable:
        pass

    class GITDoor:
        pass

    class GITWaypoint:
        pass

    class GITStore:
        pass

    class GITSound:
        pass

    class GITEncounter:
        pass

    class GITTrigger:
        pass

    class GITCamera:
        pass

    HIDE_MAP = [
        (GITCreature, "hide_creatures"),
        (GITPlaceable, "hide_placeables"),
        (GITDoor, "hide_doors"),
        (GITWaypoint, "hide_creatures"),
        (GITStore, "hide_placeables"),
        (GITSound, "hide_doors"),
        (GITEncounter, "hide_creatures"),
        (GITTrigger, "hide_placeables"),
        (GITCamera, "hide_doors"),
    ]

    data_items = [GITCreature()] * 200  # 200 objects of one type

    def old_should_hide(scene_obj, data):
        for cls, attr in HIDE_MAP:
            if isinstance(data, cls):
                return getattr(scene_obj, attr, False)
        return False

    # Benchmark old
    N = 10000
    t0 = time.perf_counter()
    for _ in range(N):
        for d in data_items:
            old_should_hide(scene, d)
    old_ms = (time.perf_counter() - t0) * 1000

    # New approach: precomputed _hide_attr
    objs = [FakeObj("hide_creatures") for _ in range(200)]

    def new_should_hide(scene_obj, obj):
        ha = obj._hide_attr
        return bool(ha and getattr(scene_obj, ha, False))

    t0 = time.perf_counter()
    for _ in range(N):
        for o in objs:
            new_should_hide(scene, o)
    new_ms = (time.perf_counter() - t0) * 1000

    print(f"should_hide (200 objs x {N} frames):")
    print(f"  Old (isinstance chain): {old_ms:.1f} ms")
    print(f"  New (precomputed attr): {new_ms:.1f} ms")
    print(f"  Speedup: {old_ms / new_ms:.1f}x")
    print()


def bench_sync_positions_local_var():
    """Compare scene.objects.get vs local var objects_get."""

    class FakeObj:
        __slots__ = ("_pos", "_rot")

        def __init__(self):
            self._pos = (0, 0, 0)
            self._rot = (0, 0, 0)

        def set_position(self, x, y, z):
            self._pos = (x, y, z)

        def set_rotation(self, x, y, z):
            self._rot = (x, y, z)

    class FakeInstance:
        __slots__ = ("position", "bearing")

        def __init__(self):
            self.position = type("V", (), {"x": 1.0, "y": 2.0, "z": 3.0})()
            self.bearing = 0.5

    objs = {}
    instances = []
    for i in range(300):
        inst = FakeInstance()
        obj = FakeObj()
        objs[inst] = obj
        instances.append(inst)

    class FakeObjects:
        def __init__(self, d):
            self._d = d

        def get(self, key):
            return self._d.get(key)

    scene_objects = FakeObjects(objs)

    N = 10000

    # Old: scene.objects.get per call
    t0 = time.perf_counter()
    for _ in range(N):
        for inst in instances:
            o = scene_objects.get(inst)
            if o is not None:
                o.set_position(inst.position.x, inst.position.y, inst.position.z)
                o.set_rotation(0, 0, inst.bearing)
    old_ms = (time.perf_counter() - t0) * 1000

    # New: hoist .get to local
    t0 = time.perf_counter()
    for _ in range(N):
        _get = scene_objects.get
        for inst in instances:
            o = _get(inst)
            if o is not None:
                o.set_position(inst.position.x, inst.position.y, inst.position.z)
                o.set_rotation(0, 0, inst.bearing)
    new_ms = (time.perf_counter() - t0) * 1000

    print(f"sync_positions (300 instances x {N} frames):")
    print(f"  Old (scene.objects.get): {old_ms:.1f} ms")
    print(f"  New (local objects_get): {new_ms:.1f} ms")
    print(f"  Speedup: {old_ms / new_ms:.1f}x")
    print()


def bench_tex_gen_cache():
    """Compare getattr per mesh vs class-var frame cache for texture generation."""

    class FakeTextures:
        _generation = 42

    class FakeScene:
        textures = FakeTextures()

    scene = FakeScene()
    N = 1000000

    # Old: getattr per call
    t0 = time.perf_counter()
    for _ in range(N):
        _ = getattr(scene.textures, "_generation", -1)
    old_ms = (time.perf_counter() - t0) * 1000

    # New: class var (simulating Mesh._frame_tex_gen)
    frame_gen = [scene.textures._generation]  # set once per frame

    t0 = time.perf_counter()
    for _ in range(N):
        _ = frame_gen[0]
    new_ms = (time.perf_counter() - t0) * 1000

    print(f"tex_gen lookup ({N} calls):")
    print(f"  Old (getattr per mesh): {old_ms:.1f} ms")
    print(f"  New (class var cache):  {new_ms:.1f} ms")
    print(f"  Speedup: {old_ms / new_ms:.1f}x")
    print()


def bench_qcolor_creation():
    """Compare per-frame QColor/QPen creation vs pre-created constants."""
    try:
        from qtpy.QtGui import QColor, QPen
    except ImportError:
        print("QPen/QColor benchmark: skipped (no Qt available)")
        return

    N = 100000
    color_tuple = (255, 80, 80, 255)
    pen_width = 0.05

    # Old: create per call
    t0 = time.perf_counter()
    for _ in range(N):
        c = QColor(color_tuple[0], color_tuple[1], color_tuple[2], color_tuple[3])
        p = QPen(c, pen_width)
    old_ms = (time.perf_counter() - t0) * 1000

    # New: pre-created
    cached_color = QColor(*color_tuple)
    cached_pen = QPen(cached_color, pen_width)

    t0 = time.perf_counter()
    for _ in range(N):
        c = cached_color
        p = cached_pen
    new_ms = (time.perf_counter() - t0) * 1000

    print(f"QColor+QPen creation ({N} calls):")
    print(f"  Old (create each time): {old_ms:.1f} ms")
    print(f"  New (pre-created):      {new_ms:.1f} ms")
    print(f"  Speedup: {old_ms / new_ms:.1f}x")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Round 5 Micro-Benchmarks")
    print("=" * 60)
    print()
    bench_should_hide_precomputed()
    bench_sync_positions_local_var()
    bench_tex_gen_cache()
    bench_qcolor_creation()
    print("Done.")
