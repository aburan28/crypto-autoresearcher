"""Null/null-object draws for EXP-MONO-b19c6b, built on a CurveState
(groupstate.py) and using the shared seed.Drawer. Written FRESH (not copied
from EXP-MONO-670aa6's controls.py) because `family` and `master_seed` must
be threaded through every "null-subset"/"null-object-pick" draw -- the two
call sites this contract's family-keying fix must reach, in addition to
"prime"/"curve-a"/"curve-b" in curve.py. The legacy subgroup/coset-union
controls are NOT reimplemented here: this contract's legacy panel is
optional/non-gating and explicitly relies on EXP-MONO-c819ba's own already-
reviewed positive controls instead (see specification.yaml
`inputs.legacy_panel`)."""
from seed import Drawer


def draw_symmetric_subset(cs, F, domain, master_seed, family, curve_ordinal, m, draw_index, label):
    """Draw a uniformly random SYMMETRIC subset of E(F_p) affine points of
    size F, built as random +/- pairs. `label` is either 'null-subset' (the
    20000-draw matched-null reference population) or 'null-object-pick' (the
    single Stage-2 held-out draw standing in for 'treatment')."""
    drawer = Drawer(domain, master_seed, family, label, cs.p, curve_ordinal, m, draw_index)
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
