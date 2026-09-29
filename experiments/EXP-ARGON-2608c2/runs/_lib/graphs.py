"""
EXP-ARGON-2608c2 core graph library.

Implements, per the frozen specification (experiments/EXP-ARGON-2608c2/specification.yaml):
  - the two independent-known-family calibration graphs (family_A_doubling_graph,
    family_B_pure_chain);
  - the frozen greedy eps-depth-reducing-set heuristic (topological longest-path
    DP; remove the node nearest the current longest path's midpoint; repeat
    until target depth reached);
  - an exact ILP solver (independent method from the greedy heuristic, used
    ONLY on the two calibration families at exact_tier_sizes {16,32,64}, never
    on G_real/G_unif, per DEC-20260812-03fa10's calibration_design_ruling).

All node indices are 0-indexed internally; the doubling-graph construction
comment in the spec uses 1-indexed j -- the mapping is j = i+1.
"""
from __future__ import annotations
import math
import os
import sys


# ---------------------------------------------------------------------------
# Calibration reference families
# ---------------------------------------------------------------------------

def family_A_doubling_graph(q: int):
    """Power-of-two doubling graph, per specification.yaml controls.
    bcf891_independent_known_family_calibration.reference_families[0].

    IMPLEMENTATION NOTE (documented interpretation, per implementation.md):
    the spec text "reference edge to j - 2^k for every k such that
    1 <= 2^k < j" is read here as k >= 1 (back-distances 2, 4, 8, ...),
    excluding k=0 (back-distance 1), because that distance is already the
    chain edge to j-1 and including it again would only add a harmless
    duplicate parallel edge with no effect on longest-path depth. This
    choice is disclosed, not silent.
    """
    in_edges = [[] for _ in range(q)]
    for i in range(q):
        j = i + 1  # 1-indexed position, per spec text
        if i > 0:
            in_edges[i].append(i - 1)
        k = 1
        while (1 << k) < j:
            pred = j - (1 << k) - 1  # back to 0-indexed
            if pred >= 0:
                in_edges[i].append(pred)
            k += 1
    return in_edges


def family_B_pure_chain(q: int):
    """Trivial chain: node j has only the chain edge to j-1."""
    in_edges = [[] for _ in range(q)]
    for i in range(1, q):
        in_edges[i].append(i - 1)
    return in_edges


# ---------------------------------------------------------------------------
# Frozen greedy eps-depth-reducing-set heuristic
# ---------------------------------------------------------------------------

def _dp_range(n, in_edges, removed, d, pred, start):
    """Recompute longest-path DP for indices [start, n) in place.
    Correct because every edge in these graphs points from a strictly
    lower index to a strictly higher index (index-monotone DAG), so nodes
    < start are unaffected by any removal at index >= start."""
    for v in range(start, n):
        if v in removed:
            d[v] = -1
            pred[v] = -1
            continue
        best = 0
        bp = -1
        for u in in_edges[v]:
            if u not in removed and d[u] >= 0 and d[u] + 1 > best:
                best = d[u] + 1
                bp = u
        d[v] = best
        pred[v] = bp


def _argmax_depth(n, removed, d):
    best_v, best_d = -1, -1
    for v in range(n):
        if v not in removed and d[v] > best_d:
            best_d = d[v]
            best_v = v
    return best_v, best_d


def _backtrack(pred, v):
    path = [v]
    while pred[v] != -1:
        v = pred[v]
        path.append(v)
    path.reverse()
    return path


def native_depth(n, in_edges):
    d = [-1] * n
    pred = [-1] * n
    _dp_range(n, in_edges, set(), d, pred, 0)
    _, best_d = _argmax_depth(n, set(), d)
    return best_d


def greedy_reduce(n, in_edges, target_depth, max_iters=None):
    """Frozen declared algorithm (specification.yaml invalidation_rules,
    first entry): topological longest-path DP; remove the node nearest the
    current longest path's midpoint; repeat until target depth reached.

    Incremental optimization (documented, does not change the algorithm's
    semantics): after removing node `mid`, only indices >= mid can have
    changed depth, since the DAG is index-monotone; nodes < mid are
    provably unaffected and are not recomputed.
    """
    removed = set()
    d = [-1] * n
    pred = [-1] * n
    _dp_range(n, in_edges, removed, d, pred, 0)
    max_iters = max_iters if max_iters is not None else n
    iters = 0
    while True:
        best_v, best_d = _argmax_depth(n, removed, d)
        if best_v == -1 or best_d <= target_depth:
            return removed, best_d, iters
        path = _backtrack(pred, best_v)
        mid = path[len(path) // 2]
        removed.add(mid)
        _dp_range(n, in_edges, removed, d, pred, mid)
        iters += 1
        if iters > max_iters:
            raise RuntimeError(
                f"greedy_reduce exceeded max_iters={max_iters} without reaching target_depth={target_depth}"
            )


# ---------------------------------------------------------------------------
# Exact solver (independent method: MILP via pulp/CBC, lazy-free single-shot
# formulation -- NOT a DP-based search, so it is methodologically independent
# of the greedy heuristic it calibrates).
# ---------------------------------------------------------------------------

def exact_min_removal_ilp(n, in_edges, target_depth, time_limit_seconds=120):
    """Exact minimum |S| such that removing S brings longest-path depth of
    the induced subgraph on the surviving nodes to <= target_depth.

    Formulation (single-shot MILP, no lazy constraint generation needed):
      x_v in {0,1}: 1 if v is removed.
      d_v in {0,...,v}: depth variable for v (tight per-node bound: at most
        v predecessor slots exist before index v, so the longest path ending
        at v can never exceed v edges).
      For every edge (u,v) in the graph, with M_uv = v (tight, since
        d_v <= v and d_u+1 <= v when u<v):
          d_v >= d_u + 1 - M_uv*(x_u + x_v)   (big-M relaxation if either endpoint removed)
      For every node v, with M_v = max(v - target_depth, 0):
          d_v <= target_depth + M_v*x_v        (binds only if v survives)
          d_v >= 0
      minimize sum(x_v)

    This is exact PROVIDED CBC closes the optimality gap within
    time_limit_seconds. CBC (open-source, no commercial solver available in
    this environment) does not always close this gap for the adversarially
    depth-robust family_A_doubling_graph at exact_tier_sizes 32/64 within
    reasonable wall-clock, even with this tightened (non-uniform, per-node)
    M -- the LP relaxation of this big-M DAG-interdiction formulation is
    fundamentally weak. This function DETECTS that case explicitly (by
    inspecting the captured CBC log for "Stopped on time limit") rather than
    trusting pulp's LpStatus alone, which reports "Optimal" for the best
    INCUMBENT found even when CBC exits on the time limit with an open gap
    -- verified empirically in this session (see implementation.md
    "Exact-computation tractability finding"). Returns status
    'proven_optimal' only when CBC's own log confirms the search completed
    (no time-limit exit); otherwise 'time_limit_incumbent' and the returned
    count is a best-found UPPER BOUND on the true minimum, not a certified
    exact value.
    """
    import contextlib
    import io
    import pulp

    prob = pulp.LpProblem("depth_reduce", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x_{v}", cat="Binary") for v in range(n)]
    d = [pulp.LpVariable(f"d_{v}", lowBound=0, upBound=v, cat="Integer") for v in range(n)]

    prob += pulp.lpSum(x)

    for v in range(n):
        for u in in_edges[v]:
            M_uv = v
            prob += d[v] >= d[u] + 1 - M_uv * (x[u] + x[v])
        M_v = max(v - target_depth, 0)
        prob += d[v] <= target_depth + M_v * x[v]

    solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=time_limit_seconds)
    # NOTE: CBC runs as an external subprocess writing directly to OS file
    # descriptor 1, so contextlib.redirect_stdout (which only redirects
    # Python's sys.stdout object) does NOT capture it -- verified empirically
    # in this session (an earlier version of this function using
    # redirect_stdout alone produced an empty solver_log and a false
    # "proven_optimal" for a run that CBC's own terminal output showed had
    # actually hit "Stopped on time limit"; see implementation.md). This
    # redirects the real OS-level fd 1 to a temp file for the duration of
    # the solve.
    import tempfile

    fd_backup = os.dup(1)
    with tempfile.TemporaryFile(mode="w+") as tf:
        os.dup2(tf.fileno(), 1)
        try:
            status = prob.solve(solver)
        finally:
            sys.stdout.flush()
            os.dup2(fd_backup, 1)
            os.close(fd_backup)
        tf.seek(0)
        solver_log = tf.read()
    status_name = pulp.LpStatus[status]
    removed = {v for v in range(n) if x[v].value() is not None and x[v].value() > 0.5}
    obj = len(removed)
    proven = ("Stopped on time limit" not in solver_log) and status_name == "Optimal"
    exact_status = "proven_optimal" if proven else "time_limit_incumbent"
    return removed, obj, exact_status, solver_log


def verify_removal(n, in_edges, removed, target_depth):
    """Independent re-check: recompute longest-path depth after applying a
    given removal set from scratch, confirming it is <= target_depth."""
    d = [-1] * n
    pred = [-1] * n
    _dp_range(n, in_edges, removed, d, pred, 0)
    _, best_d = _argmax_depth(n, removed, d)
    return best_d <= target_depth, best_d
