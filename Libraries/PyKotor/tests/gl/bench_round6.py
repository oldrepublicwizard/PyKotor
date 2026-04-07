"""Round 6 benchmark: Mesh.draw() per-call overhead reduction.

Measures the per-mesh overhead eliminated by:
  1. Direct glUniformMatrix4fv with cached uniform location (skip dict lookup)
  2. Redundant texture bind elimination (track last-bound diffuse/lightmap ID)
  3. Redundant VAO bind elimination (track last-bound VAO)
  4. Redundant glActiveTexture elimination (track last active texture unit)
  5. Reordered blend_mode checks (opaque fast-path first)
"""

from __future__ import annotations

import timeit


def bench_uniform_dict_vs_direct():
    """Compare shader.set_matrix4 (dict lookup + method call) vs cached loc + direct call."""
    # Simulate the old path: dict.get("model") each call
    uniform_cache: dict[str, int] = {"model": 42}

    def old_path():
        for _ in range(10_000):
            loc = uniform_cache.get("model")  # noqa: F841

    # Simulate the new path: class-level cached int
    cached_loc = 42

    def new_path():
        _loc = cached_loc
        for _ in range(10_000):
            _ = _loc  # noqa: F841  # Direct int access — no dict lookup

    t_old = min(timeit.repeat(old_path, number=100, repeat=5))
    t_new = min(timeit.repeat(new_path, number=100, repeat=5))
    print(f"uniform lookup (10k calls × 100): dict.get={t_old*1000:.2f}ms  cached_int={t_new*1000:.2f}ms  speedup={t_old/t_new:.1f}x")


def bench_redundant_bind_check():
    """Compare unconditional bind vs tracked-state conditional skip."""
    # Simulate 500 meshes where ~80% share the same texture
    import random
    random.seed(42)
    tex_ids = [random.choice([1, 1, 1, 1, 2]) for _ in range(500)]

    def old_path():
        for tid in tex_ids:
            _ = tid  # Always "bind" (call overhead)

    def new_path():
        last = -1
        for tid in tex_ids:
            if last != tid:
                _ = tid  # "bind" only when changed
                last = tid

    t_old = min(timeit.repeat(old_path, number=5000, repeat=5))
    t_new = min(timeit.repeat(new_path, number=5000, repeat=5))
    skipped = sum(1 for i in range(1, len(tex_ids)) if tex_ids[i] == tex_ids[i - 1])
    print(f"texture bind skip (500 meshes × 5000): always={t_old*1000:.2f}ms  tracked={t_new*1000:.2f}ms  speedup={t_old/t_new:.1f}x  skipped={skipped}/499")


def bench_blend_mode_branching():
    """Compare old branching (additive first) vs new (opaque first)."""
    # 99% opaque, 0.5% additive, 0.5% punchthrough
    blend_modes = [0] * 990 + [1] * 5 + [2] * 5
    import random
    random.seed(42)
    random.shuffle(blend_modes)

    def old_order():
        count = 0
        for bm in blend_modes:
            if bm == 1:
                count += 1
            elif bm == 2:
                count += 2
            else:
                count += 3
        return count

    def new_order():
        count = 0
        for bm in blend_modes:
            if bm == 0:
                count += 3
            elif bm == 1:
                count += 1
            else:
                count += 2
        return count

    t_old = min(timeit.repeat(old_order, number=5000, repeat=5))
    t_new = min(timeit.repeat(new_order, number=5000, repeat=5))
    print(f"blend branch order (1000 meshes × 5000): additive_first={t_old*1000:.2f}ms  opaque_first={t_new*1000:.2f}ms  speedup={t_old/t_new:.1f}x")


def bench_getattr_lazy():
    """Compare eagerly reading 3 attrs vs reading only what's needed (opaque fast path)."""

    class FakeTex:
        blend_mode = 0
        alpha_cutoff = 0.0
        has_alpha = True

    tex = FakeTex()

    def old_path():
        for _ in range(10_000):
            _ = int(getattr(tex, "blend_mode", 0))
            _ = float(getattr(tex, "alpha_cutoff", 0.0))
            _ = bool(getattr(tex, "has_alpha", True))

    def new_path():
        for _ in range(10_000):
            bm = int(getattr(tex, "blend_mode", 0))
            if bm == 0:
                ac = float(getattr(tex, "alpha_cutoff", 0.0))
                _ = ac  # noqa: F841
                # Skip has_alpha entirely for opaque path

    t_old = min(timeit.repeat(old_path, number=100, repeat=5))
    t_new = min(timeit.repeat(new_path, number=100, repeat=5))
    print(f"getattr lazy eval (10k calls × 100): eager_3={t_old*1000:.2f}ms  lazy_2={t_new*1000:.2f}ms  speedup={t_old/t_new:.1f}x")


if __name__ == "__main__":
    print("=== Round 6: Mesh.draw() Per-Call Overhead Reduction ===\n")
    bench_uniform_dict_vs_direct()
    bench_redundant_bind_check()
    bench_blend_mode_branching()
    bench_getattr_lazy()
    print("\nNote: Real-world gains are larger because each 'call' above stands in for")
    print("a PyOpenGL C-bridge call (~1-5µs each) that is now skipped entirely.")
