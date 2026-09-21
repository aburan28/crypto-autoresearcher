"""Draw the objects `walk.py` and `kangaroo.py` produce, as standalone SVG.

Three pictures, matching how the rho family is usually shown (and how the
ECC2K-130 campaign showed it):

* `render_functional_graph_svg` -- the whole iteration map on a small
  subgroup: every element is a node, every node points at its walk successor.
  One trajectory is highlighted, its tail in one colour and the cycle it falls
  into in another. That is the rho, drawn inside the graph it lives in.
* `render_dp_forest_svg` -- many short walks, each ending at a distinguished
  point (drawn large). Two walks that reach the same DP are the golden
  collision and are highlighted.
* `render_kangaroo_svg` -- tame and wild herds, coloured by herd, with the
  meeting point marked.

Layout is Fruchterman-Reingold, seeded, so the same walk always draws the same
picture. No plotting dependency: the output is SVG text. numpy is used when
present and a slower pure-Python path is used when it is not.

These are visualisations of exactly the states that were computed. Nothing
here smooths, samples, or reconstructs a walk that was not run.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .kangaroo import KangarooResult
from .toycurve import EllipticCurve, Point
from .walk import AddingWalk, Collision, DPWalk, RhoTrace

# Node keys are hashable stand-ins for points (None is the point at infinity).
NodeKey = tuple[int, int] | None

PALETTE = {
    "bg": "#ffffff",
    "edge": "#b0b0b0",
    "node": "#202020",
    "tail": "#cc0000",      # rho's tail
    "cycle": "#000000",     # rho's cycle
    "dp": "#000000",
    "hit_a": "#1f6fd0",     # the two walks that collide
    "hit_b": "#e07000",
    "tame": "#1f6fd0",
    "wild": "#e07000",
}


@dataclass
class Layout:
    pos: dict[NodeKey, tuple[float, float]]
    width: float
    height: float


# -- graph construction -----------------------------------------------------

def subgroup_points(E: EllipticCurve, P: Point, n: int) -> list[Point]:
    """All of <P>, as [O, P, 2P, ..., (n-1)P]. Toy scale only."""
    pts: list[Point] = [None]
    cur: Point = None
    for _ in range(n - 1):
        cur = E.add(cur, P)
        pts.append(cur)
    return pts


def functional_graph(walk: AddingWalk, points: list[Point]
                     ) -> dict[NodeKey, NodeKey]:
    """The walk's iteration map restricted to `points`: node -> successor."""
    succ: dict[NodeKey, NodeKey] = {}
    for R in points:
        T, _, _ = walk.steps[walk.branch(R)]
        succ[R] = walk.E.add(R, T)
    return succ


# -- layout -----------------------------------------------------------------

def spring_layout(nodes: list[NodeKey], edges: list[tuple[NodeKey, NodeKey]],
                  seed: int = 0, iterations: int = 300,
                  size: float = 1000.0) -> Layout:
    """Deterministic Fruchterman-Reingold layout."""
    m = len(nodes)
    if m == 0:
        return Layout({}, size, size)
    index = {node: i for i, node in enumerate(nodes)}
    pairs = [(index[u], index[v]) for u, v in edges
             if u in index and v in index and u != v]
    rng = random.Random(seed)
    xy0 = [(rng.random(), rng.random()) for _ in range(m)]
    k = math.sqrt(1.0 / m)

    try:
        import numpy as np
    except ImportError:                                    # pragma: no cover
        pos = _spring_python(xy0, pairs, k, iterations)
    else:
        pos = _spring_numpy(np, xy0, pairs, k, iterations)

    xs = [p[0] for p in pos]
    ys = [p[1] for p in pos]
    lo_x, hi_x, lo_y, hi_y = min(xs), max(xs), min(ys), max(ys)
    sx = (hi_x - lo_x) or 1.0
    sy = (hi_y - lo_y) or 1.0
    scale = size / max(sx, sy)
    out = {node: ((pos[i][0] - lo_x) * scale, (pos[i][1] - lo_y) * scale)
           for node, i in index.items()}
    return Layout(out, sx * scale, sy * scale)


def _spring_numpy(np, xy0, pairs, k, iterations):
    pos = np.array(xy0, dtype=float)
    m = len(pos)
    src = np.array([p[0] for p in pairs], dtype=int) if pairs else None
    dst = np.array([p[1] for p in pairs], dtype=int) if pairs else None
    temp = 0.1
    for it in range(iterations):
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.sqrt((delta ** 2).sum(-1))
        np.fill_diagonal(dist, np.inf)      # self-repulsion contributes nothing
        rep = (delta / dist[..., None]) * (k * k / dist)[..., None]
        disp = rep.sum(axis=1)
        if pairs:
            d = pos[src] - pos[dst]
            dl = np.sqrt((d ** 2).sum(-1))
            dl[dl == 0] = 1e-9
            att = (d / dl[:, None]) * (dl * dl / k)[:, None]
            np.add.at(disp, src, -att)
            np.add.at(disp, dst, att)
        length = np.sqrt((disp ** 2).sum(-1))
        length[length == 0] = 1e-9
        pos += (disp / length[:, None]) * np.minimum(length, temp)[:, None]
        temp *= 0.99
    return [tuple(p) for p in pos]


def _spring_python(xy0, pairs, k, iterations):             # pragma: no cover
    pos = [list(p) for p in xy0]
    m = len(pos)
    temp = 0.1
    for _ in range(iterations):
        disp = [[0.0, 0.0] for _ in range(m)]
        for i in range(m):
            for j in range(i + 1, m):
                dx = pos[i][0] - pos[j][0]
                dy = pos[i][1] - pos[j][1]
                d = math.hypot(dx, dy) or 1e-9
                f = k * k / d
                ux, uy = dx / d * f, dy / d * f
                disp[i][0] += ux; disp[i][1] += uy
                disp[j][0] -= ux; disp[j][1] -= uy
        for i, j in pairs:
            dx = pos[i][0] - pos[j][0]
            dy = pos[i][1] - pos[j][1]
            d = math.hypot(dx, dy) or 1e-9
            f = d * d / k
            ux, uy = dx / d * f, dy / d * f
            disp[i][0] -= ux; disp[i][1] -= uy
            disp[j][0] += ux; disp[j][1] += uy
        for i in range(m):
            d = math.hypot(*disp[i]) or 1e-9
            step = min(d, temp)
            pos[i][0] += disp[i][0] / d * step
            pos[i][1] += disp[i][1] / d * step
        temp *= 0.99
    return [tuple(p) for p in pos]


# -- SVG --------------------------------------------------------------------

def _svg(layout: Layout, edges, nodes, title: str, pad: float = 30.0) -> str:
    """edges: (u, v, colour, width); nodes: (key, colour, radius)."""
    w, h = layout.width + 2 * pad, layout.height + 2 * pad
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" '
        f'height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">',
        f'<title>{title}</title>',
        f'<rect width="{w:.0f}" height="{h:.0f}" fill="{PALETTE["bg"]}"/>',
        '<g stroke-linecap="round">',
    ]
    pos = layout.pos
    for u, v, colour, width in edges:
        if u not in pos or v not in pos:
            continue
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        parts.append(f'<line x1="{x1 + pad:.1f}" y1="{y1 + pad:.1f}" '
                     f'x2="{x2 + pad:.1f}" y2="{y2 + pad:.1f}" '
                     f'stroke="{colour}" stroke-width="{width:.2f}"/>')
    parts.append('</g><g>')
    for key, colour, radius in nodes:
        if key not in pos:
            continue
        x, y = pos[key]
        parts.append(f'<circle cx="{x + pad:.1f}" cy="{y + pad:.1f}" '
                     f'r="{radius:.2f}" fill="{colour}"/>')
    parts.append('</g></svg>')
    return "\n".join(parts)


def render_functional_graph_svg(walk: AddingWalk, trace: RhoTrace,
                                points: list[Point] | None = None,
                                n: int | None = None, seed: int = 0,
                                iterations: int = 300, size: float = 1000.0) -> str:
    """The iteration map on the whole subgroup, with one rho highlighted."""
    if points is None:
        if n is None:
            raise ValueError("pass either the point list or the subgroup order")
        points = subgroup_points(walk.E, walk.P, n)
    succ = functional_graph(walk, points)
    nodes = list(succ)
    edges = [(u, v) for u, v in succ.items()]
    layout = spring_layout(nodes, edges, seed=seed, iterations=iterations, size=size)

    tail_edges, cycle_edges = set(), set()
    if trace.closed:
        seq = [s.R for s in trace.states]
        for i in range(len(seq) - 1):
            (cycle_edges if i >= trace.tail_length else tail_edges).add(
                (seq[i], seq[i + 1]))
    drawn = []
    for u, v in edges:
        if (u, v) in cycle_edges:
            drawn.append((u, v, PALETTE["cycle"], 2.0))
        elif (u, v) in tail_edges:
            drawn.append((u, v, PALETTE["tail"], 2.0))
        else:
            drawn.append((u, v, PALETTE["edge"], 0.7))
    drawn.sort(key=lambda e: e[3])          # highlighted edges on top

    on_tail = {u for u, _ in tail_edges} | {v for _, v in tail_edges}
    on_cycle = {u for u, _ in cycle_edges} | {v for _, v in cycle_edges}
    node_marks = []
    for key in nodes:
        if key in on_cycle:
            node_marks.append((key, PALETTE["cycle"], 2.2))
        elif key in on_tail:
            node_marks.append((key, PALETTE["tail"], 2.2))
        else:
            node_marks.append((key, PALETTE["node"], 1.6))
    start = trace.states[0].R
    node_marks.append((start, PALETTE["tail"], 4.5))
    return _svg(layout, drawn, node_marks,
                f"walk functional graph, {len(nodes)} elements "
                f"(tail {trace.tail_length}, cycle {trace.cycle_length})")


def render_dp_forest_svg(walk: AddingWalk, walks: list[DPWalk],
                         collision: Collision | None = None, seed: int = 0,
                         iterations: int = 300, size: float = 1000.0) -> str:
    """Short walks merging into distinguished points, collision highlighted."""
    edges: list[tuple[NodeKey, NodeKey]] = []
    nodes: list[NodeKey] = []
    seen: set[NodeKey] = set()
    hit_labels = set()
    if collision is not None:
        for w in walks:
            if w.hit_dp and w.end.R == collision.second.R:
                hit_labels.add(w.label)
    colour_of: dict[str, str] = {}
    for i, label in enumerate(sorted(hit_labels)):
        colour_of[label] = PALETTE["hit_a"] if i == 0 else PALETTE["hit_b"]

    edge_colour: dict[tuple[NodeKey, NodeKey], tuple[str, float]] = {}
    for w in walks:
        if not w.path:
            raise ValueError("render_dp_forest_svg needs walks recorded with "
                             "record_path=True")
        colour = colour_of.get(w.label)
        for a, b in zip(w.path, w.path[1:]):
            ka, kb = a.R, b.R
            for key in (ka, kb):
                if key not in seen:
                    seen.add(key)
                    nodes.append(key)
            edges.append((ka, kb))
            if colour is not None or (ka, kb) not in edge_colour:
                edge_colour[(ka, kb)] = ((colour or PALETTE["edge"]),
                                         2.2 if colour else 0.8)
    layout = spring_layout(nodes, edges, seed=seed, iterations=iterations, size=size)
    drawn = [(u, v, *edge_colour[(u, v)]) for u, v in dict.fromkeys(edges)]
    drawn.sort(key=lambda e: e[3])

    dp_nodes = {w.end.R for w in walks if w.hit_dp}
    node_marks = []
    for key in nodes:
        if key in dp_nodes:
            node_marks.append((key, PALETTE["dp"], 6.0))
        else:
            node_marks.append((key, PALETTE["node"], 1.6))
    return _svg(layout, drawn, node_marks,
                f"{len(walks)} walks to distinguished points "
                f"(dp_bits={walk.dp_bits}, {len(dp_nodes)} DPs)")


def render_kangaroo_svg(res: KangarooResult, seed: int = 0,
                        iterations: int = 300, size: float = 1000.0) -> str:
    """Tame and wild herds, coloured by herd, meeting point enlarged."""
    edges: list[tuple[NodeKey, NodeKey]] = []
    nodes: list[NodeKey] = []
    seen: set[NodeKey] = set()
    edge_colour: dict[tuple[NodeKey, NodeKey], tuple[str, float]] = {}
    for roo in res.kangaroos:
        if not roo.path:
            raise ValueError("render_kangaroo_svg needs record_paths=True")
        colour = PALETTE[roo.herd]
        for a, b in zip(roo.path, roo.path[1:]):
            for key in (a, b):
                if key not in seen:
                    seen.add(key)
                    nodes.append(key)
            edges.append((a, b))
            edge_colour.setdefault((a, b), (colour, 1.8))
    layout = spring_layout(nodes, edges, seed=seed, iterations=iterations, size=size)
    drawn = [(u, v, *edge_colour[(u, v)]) for u, v in dict.fromkeys(edges)]
    ends = {roo.R for roo in res.kangaroos}
    node_marks = [(key, PALETTE["node"], 5.0 if key in ends else 1.8)
                  for key in nodes]
    lo, hi = res.interval
    return _svg(layout, drawn, node_marks,
                f"kangaroo herds on [{lo}, {hi}]: "
                f"{'solved' if res.solved else 'unsolved'} in {res.jumps} jumps")
