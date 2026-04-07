"""Benchmark Round 4 optimizations: error checking, generation cache, shader/GL state tracking."""

from __future__ import annotations

import os
import sys
import time


def bench_pyopengl_error_checking():
    """Simulate the overhead of PyOpenGL error checking wrapper."""

    # Measure the wrapper overhead with a no-op function
    def noop(*_a, **_kw):
        return 0

    # Simulate error-checking wrapper (what PyOpenGL does with ERROR_CHECKING=True)
    def error_checking_wrapper(fn):
        def wrapped(*args, **kw):
            result = fn(*args, **kw)
            # This is what glGetError() does - forces GPU sync
            noop()  # simulate glGetError
            return result

        return wrapped

    raw = noop
    wrapped = error_checking_wrapper(noop)

    N = 500_000
    t0 = time.perf_counter()
    for _ in range(N):
        raw()
    raw_time = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(N):
        wrapped()
    wrapped_time = time.perf_counter() - t0

    overhead_ns = (wrapped_time - raw_time) / N * 1e9
    print(f"  Error-check wrapper overhead: {overhead_ns:.0f} ns/call")
    print(f"  With ~700 GL calls/frame: {overhead_ns * 700 / 1e6:.2f} ms/frame saved")
    return overhead_ns


def bench_case_insensitive_dict_generation():
    """Compare identity-check vs generation-check for cache validation."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "Utility", "src"))
    from utility.common.more_collections import CaseInsensitiveDict

    d: CaseInsensitiveDict[int] = CaseInsensitiveDict()
    for i in range(200):
        d[f"texture_{i}"] = i

    key = "Texture_100"  # needs .lower()
    cached = d[key]
    cached_gen = d._generation

    N = 500_000

    # Old way: identity check via .get() (calls .lower() internally)
    t0 = time.perf_counter()
    for _ in range(N):
        val = d.get(key)
        if val is cached:
            pass
    old_time = time.perf_counter() - t0

    # New way: generation check (no .lower())
    t0 = time.perf_counter()
    for _ in range(N):
        if cached is not None and cached_gen == d._generation:
            pass
    new_time = time.perf_counter() - t0

    old_ns = old_time / N * 1e9
    new_ns = new_time / N * 1e9
    speedup = old_time / new_time if new_time > 0 else float("inf")
    print(f"  Identity check (old): {old_ns:.0f} ns/call")
    print(f"  Generation check (new): {new_ns:.0f} ns/call")
    print(f"  Speedup: {speedup:.1f}x")
    print(f"  With ~500 lookups/frame: {(old_ns - new_ns) * 500 / 1e6:.2f} ms/frame saved")
    return old_ns, new_ns


def bench_shader_tracking():
    """Simulate shader use() with and without active-ID tracking."""
    calls = [0]

    def glUseProgram(_id):
        calls[0] += 1

    class OldShader:
        def __init__(self, id):
            self._id = id

        def use(self):
            glUseProgram(self._id)

    class NewShader:
        _active_id = -1

        def __init__(self, id):
            self._id = id

        def use(self):
            if NewShader._active_id != self._id:
                glUseProgram(self._id)
                NewShader._active_id = self._id

    # Typical scene: 3 shaders, 200 meshes, shader changes ~3 times
    shaders_old = [OldShader(i) for i in range(3)]
    shaders_new = [NewShader(i) for i in range(3)]
    # Pattern: shader 0 for 100 meshes, shader 1 for 50, shader 2 for 50
    pattern = [0] * 100 + [1] * 50 + [2] * 50

    N = 5000
    calls[0] = 0
    t0 = time.perf_counter()
    for _ in range(N):
        for idx in pattern:
            shaders_old[idx].use()
    old_time = time.perf_counter() - t0
    old_calls = calls[0]

    calls[0] = 0
    t0 = time.perf_counter()
    for _ in range(N):
        NewShader._active_id = -1
        for idx in pattern:
            shaders_new[idx].use()
    new_time = time.perf_counter() - t0
    new_calls = calls[0]

    print(f"  Old: {old_calls} glUseProgram calls in {N} frames ({old_calls // N}/frame)")
    print(f"  New: {new_calls} glUseProgram calls in {N} frames ({new_calls // N}/frame)")
    print(f"  Time: {old_time * 1000 / N:.3f} ms/frame → {new_time * 1000 / N:.3f} ms/frame")
    print(
        f"  Calls eliminated: {(old_calls - new_calls) // N}/frame ({(1 - new_calls / old_calls) * 100:.0f}%)"
    )


def bench_gl_state_tracking():
    """Simulate mesh draw with/without GL state tracking."""
    calls = [0]

    def gl_call(*_a):
        calls[0] += 1

    # Old: every mesh sets + restores blend state (4 extra calls per mesh)
    def old_mesh_draw(has_blend):
        if has_blend:
            gl_call()  # glEnable(GL_BLEND)
            gl_call()  # glBlendFunc
            gl_call()  # glDepthMask(False)
        else:
            gl_call()  # glDisable(GL_BLEND)
        gl_call()  # shader.set_float alphaCutoff
        # ... actual draw ...
        # restore defaults:
        gl_call()  # glEnable(GL_BLEND)
        gl_call()  # glDepthMask(True)
        gl_call()  # glBlendFunc default
        gl_call()  # shader.set_float alphaCutoff 0.0

    # New: state tracking, no restore
    blend_state = [-1]
    last_cutoff = [-1.0]

    def new_mesh_draw(has_blend):
        desired = 1 if has_blend else 0
        if blend_state[0] != desired:
            if has_blend:
                gl_call()  # glEnable(GL_BLEND)
                gl_call()  # glBlendFunc
                gl_call()  # glDepthMask(False)
            else:
                gl_call()  # glDisable(GL_BLEND)
            blend_state[0] = desired
        cutoff = 0.5 if has_blend else 0.0
        if last_cutoff[0] != cutoff:
            gl_call()  # shader.set_float alphaCutoff
            last_cutoff[0] = cutoff

    # Typical scene: 200 meshes, 20% with alpha blending, sorted by shader
    pattern = [False] * 160 + [True] * 40

    N = 5000
    calls[0] = 0
    t0 = time.perf_counter()
    for _ in range(N):
        for b in pattern:
            old_mesh_draw(b)
    old_time = time.perf_counter() - t0
    old_calls = calls[0]

    calls[0] = 0
    t0 = time.perf_counter()
    for _ in range(N):
        blend_state[0] = -1
        last_cutoff[0] = -1.0
        for b in pattern:
            new_mesh_draw(b)
    new_time = time.perf_counter() - t0
    new_calls = calls[0]

    print(f"  Old: {old_calls // N} GL calls/frame ({old_time * 1000 / N:.3f} ms/frame)")
    print(f"  New: {new_calls // N} GL calls/frame ({new_time * 1000 / N:.3f} ms/frame)")
    print(
        f"  GL calls eliminated: {(old_calls - new_calls) // N}/frame ({(1 - new_calls / old_calls) * 100:.0f}%)"
    )
    print(f"  Time: {old_time * 1000 / N:.3f} ms/frame → {new_time * 1000 / N:.3f} ms/frame")


if __name__ == "__main__":
    print("=" * 60)
    print("Round 4 Optimization Benchmarks")
    print("=" * 60)

    print("\n1. PyOpenGL Error-Checking Overhead:")
    bench_pyopengl_error_checking()

    print("\n2. CaseInsensitiveDict Generation Cache:")
    bench_case_insensitive_dict_generation()

    print("\n3. Shader Active-ID Tracking:")
    bench_shader_tracking()

    print("\n4. GL State Tracking (Blend/Cutoff):")
    bench_gl_state_tracking()

    print("\n" + "=" * 60)
    print("Round 4 Summary: Python-level overhead eliminated from render loop")
    print("=" * 60)
