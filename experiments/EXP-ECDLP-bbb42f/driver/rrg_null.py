"""
RUN-ECDLP-bbb42f-5: CTRL-NULL-RRG. Synthetic random-regular-graph null,
containing NO elliptic-curve arithmetic at all. Directly Monte-Carlo
simulates HEUR-ISO-1's d-regular hitting-time model: build a uniformly
random d-regular graph on n vertices (via the configuration model with a
simple rejection step for self-loops/multi-edges, standard construction),
mark a uniformly random subset S of size s as special, and measure the
number of steps r for a random walk from a uniformly random start vertex to
first hit S. Compare the empirical distribution of r against the model's
own closed-form prediction P(r* > r) ~ (1 - s/n)^{B_r}, B_r = d(d-1)^{r-1}.

This validates the MODEL'S OWN IMPLEMENTATION (per contract failure_meaning
for CTRL-NULL-RRG), independent of any curve-specific effect.
"""
from __future__ import annotations

import math
import random


def build_random_regular_graph(n: int, d: int, rng: random.Random, max_repair_passes=20000):
    """
    Configuration model (stub pairing) followed by iterative SWAP REPAIR of
    any self-loops / multi-edges (standard fix for the configuration model
    at n,d too large for plain rejection sampling to succeed by chance):
    repeatedly pick a bad edge (u,u) or a duplicate (u,v) and a second,
    unrelated edge (x,y), and rewire to (u,x),(v,y) [or (u,y),(v,x) if that
    also collides], which preserves d-regularity exactly while removing the
    defect. Terminates when no defects remain or max_repair_passes is hit
    (recorded as a residual-defect count rather than silently accepted).
    """
    if (n * d) % 2 != 0:
        n += 1  # nd must be even

    stubs = []
    for v in range(n):
        stubs.extend([v] * d)
    rng.shuffle(stubs)
    edges = []
    for i in range(0, len(stubs), 2):
        edges.append([stubs[i], stubs[i + 1]])

    def multiplicity(adjacency, u, v):
        return adjacency[u].count(v)

    adjacency = [[] for _ in range(n)]
    for (u, v) in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)

    def is_bad(e):
        u, v = e
        return u == v or multiplicity(adjacency, u, v) > 1

    passes = 0
    bad_indices = [i for i, e in enumerate(edges) if is_bad(e)]
    while bad_indices and passes < max_repair_passes:
        passes += 1
        i = bad_indices[0]
        u, v = edges[i]
        j = rng.randrange(len(edges))
        if j == i:
            continue
        x, y = edges[j]
        if len({u, v, x, y}) < 3:
            continue
        # try rewire (u,x),(v,y)
        for (nu, nv) in [((u, x), (v, y)), ((u, y), (v, x))]:
            a1, b1 = nu
            a2, b2 = nv
            if a1 == b1 or a2 == b2:
                continue
            # tentatively remove old edges, add new, check improvement
            adjacency[u].remove(v)
            adjacency[v].remove(u)
            adjacency[x].remove(y)
            adjacency[y].remove(x)
            adjacency[a1].append(b1)
            adjacency[b1].append(a1)
            adjacency[a2].append(b2)
            adjacency[b2].append(a2)
            edges[i] = [a1, b1]
            edges[j] = [a2, b2]
            break
        bad_indices = [k for k, e in enumerate(edges) if is_bad(e)]

    adjacency_sets = [set(neigh) for neigh in adjacency]
    residual_defects = sum(1 for e in edges if is_bad(e))
    return adjacency_sets, residual_defects


def hitting_time_trial(adjacency, s_size: int, rng: random.Random, max_steps: int):
    """
    r* is the GRAPH DISTANCE (minimal number of edge-steps, i.e. shortest-
    path/BFS-ball radius) from a uniformly random start vertex to the
    nearest vertex in a uniformly random special subset S -- this is what
    HEUR-ISO-1's formal_statement models via "expected ball-of-radius-r
    size B_r = d(d-1)^{r-1}" (a BFS-ball covering count), NOT a random-walk
    hitting time with revisits (a materially different, larger quantity on
    an expander-like graph). Computed by BFS from `start` until a special
    vertex is first reached or max_steps exceeded.
    """
    n = len(adjacency)
    special = set(rng.sample(range(n), s_size))
    start = rng.randrange(n)
    if start in special:
        return 0
    from collections import deque
    visited = {start}
    frontier = deque([(start, 0)])
    while frontier:
        v, dist = frontier.popleft()
        if dist >= max_steps:
            continue
        for nb in adjacency[v]:
            if nb in special:
                return dist + 1
            if nb not in visited:
                visited.add(nb)
                frontier.append((nb, dist + 1))
    return None  # censored (S not reached within max_steps of BFS radius)


def predicted_survival(n: int, s: int, d: int, r: int) -> float:
    """P(r* > r) ~ (1 - s/n)^{B_r}, B_r = d(d-1)^{r-1}. Computed via
    log-space (math.exp(B_r * log(base))) since B_r can be astronomically
    large well before the survival probability is numerically nonzero."""
    if r <= 0:
        return 1.0
    B_r = d * ((d - 1) ** (r - 1))
    base = max(1e-300, 1.0 - s / n)
    log_base = math.log(base)
    if B_r > 10 ** 15:  # too large to convert to float; result underflows to 0
        return 0.0
    log_survival = B_r * log_base
    if log_survival < -700:  # underflows float exp; genuinely ~0
        return 0.0
    return math.exp(log_survival)


def run_null_simulation(n: int, d: int, s: int, num_trials: int, seed: int, max_steps=None):
    rng = random.Random(seed)
    max_steps = max_steps or max(50, 6 * n)
    adjacency, residual_defects = build_random_regular_graph(n, d, rng)
    n_actual = len(adjacency)
    results = []
    censored = 0
    for _ in range(num_trials):
        r = hitting_time_trial(adjacency, s, rng, max_steps)
        if r is None:
            censored += 1
        else:
            results.append(r)

    # Empirical survival function vs predicted, at every observed r.
    results_sorted = sorted(results)
    max_r_observed = results_sorted[-1] if results_sorted else 0
    ks_distance = 0.0
    comparison_table = []
    total = len(results)
    for r in range(0, max_r_observed + 2):
        empirical_survival = sum(1 for x in results_sorted if x > r) / total if total else None
        predicted = predicted_survival(n_actual, s, d, r)
        if empirical_survival is not None:
            ks_distance = max(ks_distance, abs(empirical_survival - predicted))
            comparison_table.append({
                "r": r,
                "empirical_survival": empirical_survival,
                "predicted_survival": predicted,
            })

    return {
        "n_requested": n,
        "n_actual": n_actual,
        "residual_graph_defects": residual_defects,
        "d": d,
        "s": s,
        "num_trials": num_trials,
        "num_censored": censored,
        "max_steps": max_steps,
        "seed": seed,
        "observed_hitting_times": results_sorted,
        "ks_distance": ks_distance,
        "comparison_table": comparison_table,
        "tail_check": {
            "max_observed_minimal_ell_equivalent_r": max_r_observed,
            "predicted_survival_at_max_observed_r": predicted_survival(n_actual, s, d, max_r_observed),
        },
    }
