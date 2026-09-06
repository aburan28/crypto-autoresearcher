"""Null/null-object draws and legacy-panel positive/graded controls for
EXP-MONO-670aa6, built on a CurveState (groupstate.py) and using the shared
seed.Drawer. The coset-union control excludes order-2 cosets from the start
(CORR-20260830-2b6706), matching the corrected logic -- there is no reason
to reintroduce the known EXP-MONO-c819ba bug when building fresh here."""
from seed import Drawer


def draw_symmetric_subset(cs, F, domain, curve_ordinal, m, draw_index, label):
    """Draw a uniformly random SYMMETRIC subset of E(F_p) affine points of
    size F, built as random +/- pairs. `label` is either 'null-subset' (the
    200-draw matched-null reference population) or 'null-object-pick' (the
    single Stage-2 held-out draw standing in for 'treatment')."""
    drawer = Drawer(domain, label, cs.p, curve_ordinal, m, draw_index)
    chosen = set()
    n_affine = len(cs.points)
    guard = 0
    while len(chosen) < F:
        guard += 1
        if guard > 200 * F + 1000:
            raise RuntimeError("draw_symmetric_subset: too many rejection iterations")
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
                continue
            chosen.add(P)
            chosen.add(Q)
    return list(chosen)


def subgroup_control(cs, k):
    """FB = H_k = {(a,b) in Z/n1 x Z/n2 : b == 0 mod k}, order n1*(n2/k) = N/k
    exactly. Requires k | n2. Coordinate construction (not scalar-mult image)
    is exact regardless of cyclic/non-cyclic structure -- see
    EXP-MONO-c819ba's controls.py note, unchanged reasoning here."""
    if cs.n2 % k != 0:
        return None, None
    h = cs.n1 * (cs.n2 // k)
    coords = [(a, b) for a in range(cs.n1) for b in range(0, cs.n2, k)]
    assert len(coords) == h
    return coords, h


def coset_union_control(cs, domain, curve_ordinal, m, draw_index):
    """FB = H4 U gH4, H4 = {(a,b): b==0 mod 4} (order N/4, requires 4|n2),
    entirely in (k1,k2) coordinate space. g's coordinate is drawn (label
    'coset-pick') from coordinates NOT in H4 AND excluding order-2 cosets of
    G/H4 (2*b mod 4 != 0), per CORR-20260830-2b6706: an order-2 g would
    silently collapse H4 U gH4 to the index-2 subgroup, duplicating
    positive_control_1 instead of testing the intended C/F = 1/sqrt(2) case.
    This exclusion is present from the start in this contract, not
    retrofitted."""
    H4_coords, h = subgroup_control(cs, 4)
    if H4_coords is None:
        return None
    H4_set = set(H4_coords)
    outside_coords = [(a, b) for a in range(cs.n1) for b in range(cs.n2)
                      if (a, b) not in H4_set and (2 * b) % 4 != 0]
    if not outside_coords:
        return None
    drawer = Drawer(domain, "coset-pick", cs.p, curve_ordinal, m, draw_index)
    idx = drawer.draw(len(outside_coords))
    ga, gb = outside_coords[idx]
    coset_coords = [((a + ga) % cs.n1, (b + gb) % cs.n2) for (a, b) in H4_coords]
    fb_coords = sorted(set(H4_coords) | set(coset_coords))
    g_point = cs.coord_grid[ga][gb]
    return {"coords": fb_coords, "h": h, "g": g_point, "g_coord": (ga, gb),
            "H4_size": h, "fb_size": len(fb_coords)}
