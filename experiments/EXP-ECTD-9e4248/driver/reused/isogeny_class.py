"""
isogeny_class.py -- BFS construction of an ordinary F_p isogeny class: starting from
a seed curve E0 with prime #E0(F_p)=N in the requested bit range, repeatedly apply
isogeny.neighbors() (rational ell-isogenies, ell in {2,3,5,7}, restricted kernel
construction -- see isogeny.py docstring) until the class reaches the requested
minimum size or the reachable frontier is exhausted.
"""
import random
import time
from . import fp, curve, isogeny


def find_seed_curve(p, rng, target_lo_bits, target_hi_bits, max_attempts=4000):
    """Search random (a,b) over F_p for a curve with prime #E(F_p) in the requested
    bit range. Returns (a, b, N) or None."""
    for _ in range(max_attempts):
        a = rng.randrange(p)
        b = rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        N = curve.find_curve_order(a, b, p, rng, tries=6, agreement_needed=3)
        if N is None:
            continue
        if not (target_lo_bits <= N.bit_length() <= target_hi_bits):
            continue
        if not fp.is_probable_prime(N):
            continue
        return a, b, N
    return None


def build_class(p, a0, b0, N, rng, min_size=64, ells=(2, 3, 5, 7),
                 max_nodes_expand=4000, wall_budget_s=None):
    """BFS over the isogeny graph. Returns dict with:
      curves: list of (a,b) tuples (canonical order = discovery order, curves[0]=seed)
      edges: list of (i, j, ell) discovery edges (i,j indices into curves)
      exhausted: True if BFS ran out of frontier before reaching min_size
      elapsed_s, nodes_expanded
    """
    t0 = time.time()
    curves = [(a0 % p, b0 % p)]
    index_of = {curves[0]: 0}
    edges = []
    frontier = [0]
    nodes_expanded = 0
    exhausted = False
    while frontier and len(curves) < min_size:
        if wall_budget_s is not None and time.time() - t0 > wall_budget_s:
            break
        if nodes_expanded >= max_nodes_expand:
            exhausted = True
            break
        i = frontier.pop(0)
        a, b = curves[i]
        nbrs = isogeny.neighbors(a, b, p, N, rng, ells=ells)
        nodes_expanded += 1
        for ell, a2, b2 in nbrs:
            key = (a2 % p, b2 % p)
            if key not in index_of:
                index_of[key] = len(curves)
                curves.append(key)
                frontier.append(index_of[key])
            j = index_of[key]
            edges.append((i, j, ell))
    else:
        if not frontier and len(curves) < min_size:
            exhausted = True
    return {
        "curves": curves,
        "edges": edges,
        "exhausted": exhausted,
        "elapsed_s": time.time() - t0,
        "nodes_expanded": nodes_expanded,
        "N": N,
        "p": p,
    }
