"""Produce qualitative ASCII validation diagrams for a BWM (no matplotlib).

Used by the CLI when --render-png is requested but matplotlib is not installed.
Format: perimeter outline with ASCII line-drawing (- | +), transition IDs in
small rectangles, optional ANSI color. Focus on borders and numbered transitions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pykotor.resource.formats.bwm.bwm_data import BWM, BWMEdge, BWMFace

# Format version for detection; first line of file must match this.
BWM_VALIDATION_DIAGRAM_MAGIC = "# BWM validation diagram 1.0"

# Grid size for outline + transition boxes (ASCII only)
DEFAULT_WIDTH = 78
DEFAULT_HEIGHT = 38

# ANSI (16-color) by role
ANSI_RESET = "\033[0m"
ANSI_PERIMETER = "\033[36m"  # cyan
ANSI_TRANSITION_BOX = "\033[91m"  # red
ANSI_TRANSITION_ID = "\033[93m"  # yellow
ANSI_ARROW_STEM = "\033[32m"  # green
ANSI_ARROW_HEAD = "\033[1;31m"  # bold red
# Legacy aliases
ANSI_WALKABLE = "\033[34m"
ANSI_UNWALKABLE = "\033[90m"
ANSI_BORDER = ANSI_PERIMETER
ANSI_BOX = ANSI_TRANSITION_BOX
ANSI_ID = ANSI_TRANSITION_ID


def _bresenham(
    x0: int,
    y0: int,
    x1: int,
    y1: int,
) -> list[tuple[int, int, str]]:
    """Rasterize line from (x0,y0) to (x1,y1). Returns list of (c, r, char): '-' horizontal, '|' vertical, '+' corner."""
    out: list[tuple[int, int, str]] = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0
    prev_x, prev_y = x0, y0
    while True:
        if prev_x != x and prev_y != y:
            ch = "+"
        elif prev_x != x:
            ch = "-"
        else:
            ch = "|"
        out.append((x, y, ch))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            prev_x, prev_y = x, y
            x += sx
        if e2 < dx:
            err += dx
            prev_x, prev_y = x, y
            y += sy
    return out


def render_bwm_to_ascii_diagrams(
    bwm: BWM,
    *,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    use_color: bool = True,
) -> list[str]:
    """Produce ASCII validation diagram: perimeter outline + transition boxes with ID.

    Draws the walkmesh perimeter as a closed polygon using - | + and places
    each transition in a small rectangle with its number centered. No dense
    raster; focus on borders and transition IDs.

    Args:
    ----
        bwm: Rebuilt BWM in memory.
        width: Character width of the drawing area (inside frame).
        height: Character height of the drawing area.
        use_color: If True, embed ANSI color codes.

    Returns:
    -------
        List of lines (one string per line).
    """
    bbmin, bbmax = bwm.box()
    span_x = bbmax.x - bbmin.x
    span_y = bbmax.y - bbmin.y
    if span_x < 1e-9:
        span_x = 1.0
    if span_y < 1e-9:
        span_y = 1.0

    n_verts: int = len(bwm.vertices())
    walkable: list[BWMFace] = bwm.walkable_faces()
    unwalkable: list[BWMFace] = bwm.unwalkable_faces()
    n_walk: int = len(walkable)
    n_unwalk: int = len(unwalkable)
    edges: list[BWMEdge] = bwm.edges()
    n_perim = len(edges)
    trans_edges = [(i, e) for i, e in enumerate(edges) if e.transition >= 0]
    n_trans = len(trans_edges)

    def to_col(x: float) -> int:
        c = int(round((x - bbmin.x) / span_x * (width - 1)))
        return max(0, min(width - 1, c))

    def to_row(y: float) -> int:
        # Y up in game -> row 0 at top
        r = int(round((bbmax.y - y) / span_y * (height - 1)))
        return max(0, min(height - 1, r))

    # One closed polygon per loop (final=True marks end of each loop)
    loops: list[list[tuple[float, float]]] = []
    current_loop: list[tuple[float, float]] = []
    for edge in edges:
        a, b = bwm._edge_endpoints(edge.face, edge.index)
        current_loop.append((a.x, a.y))
        if edge.final:
            current_loop.append((b.x, b.y))
            loops.append(current_loop)
            current_loop = []
    if current_loop:
        _, b = bwm._edge_endpoints(edges[-1].face, edges[-1].index)
        current_loop.append((b.x, b.y))
        loops.append(current_loop)

    # Grid and color role (for ANSI)
    grid: list[list[str]] = [[" "] * width for _ in range(height)]
    color_role: list[list[str | None]] = [[None] * width for _ in range(height)]

    # Rasterize each loop only (no segment from one loop to the next)
    for loop in loops:
        n_pts = len(loop)
        for i in range(n_pts):
            x0, y0 = loop[i][0], loop[i][1]
            x1, y1 = loop[(i + 1) % n_pts][0], loop[(i + 1) % n_pts][1]
            c0, r0 = to_col(x0), to_row(y0)
            c1, r1 = to_col(x1), to_row(y1)
            for c, r, ch in _bresenham(c0, r0, c1, r1):
                if 0 <= r < height and 0 <= c < width:
                    if grid[r][c] == " " or ch == "+":
                        grid[r][c] = ch
                        color_role[r][c] = "perimeter"

    # Transition boxes: 5 wide x 3 tall, ID centered; set color roles
    def draw_box(center_c: int, center_r: int, tid: int) -> None:
        tid_str = str(tid)
        if len(tid_str) > 2:
            tid_str = tid_str[:2]
        r0 = center_r - 1
        c0 = center_c - 2
        if r0 < 0 or r0 + 3 > height or c0 < 0 or c0 + 5 > width:
            return
        grid[r0][c0 : c0 + 5] = ["+", "-", "-", "-", "+"]
        for j in range(5):
            color_role[r0][c0 + j] = "transition_box"
        grid[r0 + 1][c0] = "|"
        color_role[r0 + 1][c0] = "transition_box"
        id_line = tid_str.center(3)[:3]
        for j, ch in enumerate(id_line):
            grid[r0 + 1][c0 + 1 + j] = ch
            color_role[r0 + 1][c0 + 1 + j] = "transition_id" if ch in "0123456789" else "transition_box"
        grid[r0 + 1][c0 + 4] = "|"
        color_role[r0 + 1][c0 + 4] = "transition_box"
        grid[r0 + 2][c0 : c0 + 5] = ["+", "-", "-", "-", "+"]
        for j in range(5):
            color_role[r0 + 2][c0 + j] = "transition_box"

    for trans_num, (_, edge) in enumerate(trans_edges, start=1):
        mid, _ = type(bwm).edge_inward_direction_xy(edge.face, edge.index)
        cc, rr = to_col(mid.x), to_row(mid.y)
        draw_box(cc, rr, trans_num)

    # Arrows at each transition: stem + head, offset one cell inward
    for _, edge in trans_edges:
        mid, direction = type(bwm).edge_inward_direction_xy(edge.face, edge.index)
        dx, dy = direction.x, direction.y
        cc = to_col(mid.x)
        rr = to_row(mid.y)
        # One cell inward so arrow is visible inside boundary
        if abs(dx) >= abs(dy):
            cc += 1 if dx > 0 else -1 if dx < 0 else 0
        else:
            rr += -1 if dy > 0 else 1 if dy < 0 else 0
        # Clamp for grid
        cc = max(0, min(width - 1, cc))
        rr = max(0, min(height - 1, rr))
        # Choose direction: left <, right >, up ^, down v
        if abs(dx) >= abs(dy):
            if dx > 0:  # inward right: stem left, head right
                stem_c, head_c = cc - 1, cc
                if 0 <= stem_c < width and 0 <= rr < height:
                    grid[rr][stem_c] = "-"
                    color_role[rr][stem_c] = "arrow_stem"
                if 0 <= head_c < width:
                    grid[rr][head_c] = ">"
                    color_role[rr][head_c] = "arrow_head"
            else:  # inward left: stem right, head left
                head_c, stem_c = cc, cc + 1
                if 0 <= head_c < width and 0 <= rr < height:
                    grid[rr][head_c] = "<"
                    color_role[rr][head_c] = "arrow_head"
                if 0 <= stem_c < width and 0 <= rr < height:
                    grid[rr][stem_c] = "-"
                    color_role[rr][stem_c] = "arrow_stem"
        else:
            if dy > 0:  # inward up (smaller row): head above stem
                head_r, stem_r = rr, rr + 1
                if 0 <= head_r < height and 0 <= cc < width:
                    grid[head_r][cc] = "^"
                    color_role[head_r][cc] = "arrow_head"
                if 0 <= stem_r < height and 0 <= cc < width:
                    grid[stem_r][cc] = "|"
                    color_role[stem_r][cc] = "arrow_stem"
            else:  # inward down: stem above head
                stem_r, head_r = rr - 1, rr
                if 0 <= stem_r < height and 0 <= cc < width:
                    grid[stem_r][cc] = "|"
                    color_role[stem_r][cc] = "arrow_stem"
                if 0 <= head_r < height and 0 <= cc < width:
                    grid[head_r][cc] = "v"
                    color_role[head_r][cc] = "arrow_head"

    def ansi_for_role(role: str | None) -> str:
        if role == "perimeter":
            return ANSI_PERIMETER
        if role == "transition_box":
            return ANSI_TRANSITION_BOX
        if role == "transition_id":
            return ANSI_TRANSITION_ID
        if role == "arrow_stem":
            return ANSI_ARROW_STEM
        if role == "arrow_head":
            return ANSI_ARROW_HEAD
        return ""

    def row_str(r: int) -> str:
        if not use_color:
            return "".join(grid[r])
        out: list[str] = []
        prev_role: str | None = None
        for c_idx in range(width):
            ch: str = grid[r][c_idx]
            role: str | None = color_role[r][c_idx]
            code: str | None = ansi_for_role(role)
            if code and role != prev_role:
                out.append(code)
                prev_role = role
            elif not code and prev_role is not None:
                out.append(ANSI_RESET)
                prev_role = None
            out.append(ch)
        if prev_role is not None:
            out.append(ANSI_RESET)
        return "".join(out)

    lines: list[str] = []
    lines.append(BWM_VALIDATION_DIAGRAM_MAGIC)
    lines.append("")
    lines.append("--- Summary ---")
    lines.append(f"  Bbox:  X [{bbmin.x:.1f}, {bbmax.x:.1f}]  Y [{bbmin.y:.1f}, {bbmax.y:.1f}]  Z [{bbmin.z:.1f}, {bbmax.z:.1f}]")
    lines.append(f"  Vertices: {n_verts}  Faces: walkable={n_walk}, unwalkable={n_unwalk}")
    lines.append(f"  Perimeter edges: {n_perim}  Transitions: {n_trans}")
    lines.append("")
    lines.append("--- Outline (perimeter), transition boxes (door/area link ID in center), and inward arrows ---")
    if use_color:
        lines.append("  Legend: perimeter=cyan, box=red, ID=yellow, arrow stem=green, arrow head=red. Numbers = transition (door) IDs.")
    lines.append("  +" + "-" * width + "+")
    for r in range(height):
        lines.append("  |" + row_str(r) + "|")
    lines.append("  +" + "-" * width + "+")
    lines.append("")
    lines.append("--- Transitions ---")
    if trans_edges:
        for trans_num, (_, edge) in enumerate(trans_edges, start=1):
            mid, direction = type(bwm).edge_inward_direction_xy(edge.face, edge.index)
            dx, dy = direction.x, direction.y
            ch = "^" if (abs(dy) >= abs(dx) and dy > 0) else "v" if (abs(dy) >= abs(dx)) else ">" if dx > 0 else "<"
            lines.append(f"  [{trans_num}] ({mid.x:.1f}, {mid.y:.1f})  inward {ch}")
        lines.append("  All transitions on perimeter; arrows point inward.")
    else:
        lines.append("  No door/area links on this walkmesh.")
    lines.append("")
    lines.append("For PNG validation images, install: pip install pykotor[render]")
    lines.append("")
    return lines
