"""Positive/graded/calibration controls for EXP-MONO-c819ba, built on a
CurveState (groupstate.py) and using the shared seed.Drawer for the
"null-subset" and "coset-pick" labels."""
import math
from seed import Drawer
from fields import ec_neg


def draw_symmetric_null(cs, F, domain, m, draw_index):
    """Draw a uniformly random SYMMETRIC subset of E(F_p) affine points of
    size F, built as random +/- pairs (label 'null-subset'). Returns list of
    points (len == F, unless F is odd and a self-negating (2-torsion) point
    was drawn, in which case len may be F exactly by construction below)."""
    drawer = Drawer(domain, "null-subset", cs.p, m, draw_index)
    chosen = set()
    n_affine = len(cs.points)
    guard = 0
    while len(chosen) < F:
        guard += 1
        if guard > 200 * F + 1000:
            raise RuntimeError("draw_symmetric_null: too many rejection iterations")
        idx = drawer.draw(n_affine)
        P = cs.points[idx]
        Q = cs.negate(P)
        if P in chosen:
            continue
        if P == Q:  # self-negating (2-torsion) point: only take it when it is
            # the exact remaining odd slot, else it would parity-lock the loop
            # out of ever reaching an even-sized target using only +2 pair draws.
            if F - len(chosen) == 1:
                chosen.add(P)
            else:
                continue
        else:
            if len(chosen) + 2 > F:
                continue  # would overshoot; try another draw
            chosen.add(P)
            chosen.add(Q)
    return list(chosen)


def subgroup_control(cs, k):
    """FB = H_k = {(a,b) in Z/n1 x Z/n2 : b == 0 mod k}, order n1*(n2/k) = N/k
    exactly. Requires k | n2. NOTE: the naive "image of scalar mult-by-k" (which
    has order N/gcd(k,N) only for CYCLIC groups) is WRONG here whenever E(F_p)
    is non-cyclic with even n1 (its kernel -- the full k-torsion -- is larger
    than gcd(k,N), so its image is smaller than N/k); this coordinate
    construction is exact regardless of cyclic/non-cyclic structure."""
    if cs.n2 % k != 0:
        return None, None
    h = cs.n1 * (cs.n2 // k)
    coords = [(a, b) for a in range(cs.n1) for b in range(0, cs.n2, k)]
    assert len(coords) == h
    return coords, h


def coset_union_control(cs, domain, m, draw_index):
    """FB = H4 U gH4, H4 = {(a,b): b==0 mod 4} (order N/4, requires 4|n2),
    entirely in (k1,k2) coordinate space (see subgroup_control note on why
    coordinate construction, not scalar-mult image, is used). g's coordinate
    is drawn (label 'coset-pick') from coordinates NOT in H4. Returns dict
    with coords, h, and g's *point* (for the forced-spectrum FFT check)."""
    H4_coords, h = subgroup_control(cs, 4)
    if H4_coords is None:
        return None
    H4_set = set(H4_coords)
    # g must have order 4 in G/H4 (equivalently 2g not in H4): a class of order 2
    # would make H4 U gH4 the index-2 subgroup, collapsing C/F to 1 and silently
    # duplicating positive control 1 instead of testing the C/F = 1/sqrt(2) case.
    outside_coords = [(a, b) for a in range(cs.n1) for b in range(cs.n2)
                      if (a, b) not in H4_set and (2 * b) % 4 != 0]
    if not outside_coords:
        return None
    drawer = Drawer(domain, "coset-pick", cs.p, m, draw_index)
    idx = drawer.draw(len(outside_coords))
    ga, gb = outside_coords[idx]
    coset_coords = [((a + ga) % cs.n1, (b + gb) % cs.n2) for (a, b) in H4_coords]
    fb_coords = sorted(set(H4_coords) | set(coset_coords))
    g_point = cs.coord_grid[ga][gb]
    return {"coords": fb_coords, "h": h, "g": g_point, "g_coord": (ga, gb),
            "H4_size": h, "fb_size": len(fb_coords)}
