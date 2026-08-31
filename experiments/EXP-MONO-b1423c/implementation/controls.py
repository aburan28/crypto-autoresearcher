"""
Null-draw and subgroup-reconstruction controls for EXP-MONO-b1423c.

`subgroup_control` below is copied VERBATIM (byte-for-byte, comments
included) from experiments/EXP-MONO-c819ba/implementation/controls.py --
this contract's own frozen requirement is to reuse that CORRECTED
subgroup-construction function exactly, not to reconstruct it from prose.
Do not modify it.

`draw_symmetric_null_subset` implements the SAME rejection-sampled,
random-+/--pair mechanism as EXP-MONO-c819ba's `draw_symmetric_null` and
EXP-MONO-b19c6b's `draw_symmetric_subset`, but keyed by THIS contract's own
`seed.NullSubsetDrawer` (see seed.py docstring for the exact preimage,
per specification.yaml `inputs.seed_derivation_rule`).
"""
from seed import NullSubsetDrawer


# ---- verbatim copy of EXP-MONO-c819ba/implementation/controls.py::subgroup_control ----
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
# ---- end verbatim copy ----


def draw_symmetric_null_subset(cs, F, domain, master_seed, h, draw_index):
    """Draw a uniformly random SYMMETRIC subset of E(F_p) affine points of
    size F, built as random +/- pairs, keyed by (domain, master_seed, cs.p,
    h, draw_index). Identical rejection-sampling mechanism to
    EXP-MONO-c819ba's draw_symmetric_null / EXP-MONO-b19c6b's
    draw_symmetric_subset; only the underlying Drawer's preimage differs
    (this contract's own frozen seed_derivation_rule, keyed on p and h
    rather than family/curve_ordinal/m, since there is a single fixed
    curve and h identifies the cell)."""
    drawer = NullSubsetDrawer(domain, master_seed, cs.p, h, draw_index)
    chosen = set()
    n_affine = len(cs.points)
    guard = 0
    while len(chosen) < F:
        guard += 1
        if guard > 200 * F + 1000:
            raise RuntimeError("draw_symmetric_null_subset: too many rejection iterations")
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
