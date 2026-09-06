"""
Stage 3: factor-base-sublocus root-coincidence census
(specification.yaml arms_and_controls.treatment_b), m in {4,5}.

Uses genuine E(F_p) group arithmetic (real rational points -- no F_{p^2}
needed since every factor-base point IS F_p-rational by construction), via
fields.Fp2 with the imaginary component held at 0 throughout (a plain F_p
embedding; reusing the same tested point-addition code as Path 1 rather than
duplicating it).
"""
from fields import Fp2, ec_add_fp2, ec_neg_fp2
from seed import Drawer


def draw_distinct_fb_tuple(F: Fp2, fb, drawer: Drawer):
    """Draws (m-1) DISTINCT factor-base points via rejection sampling on
    indices into `fb` (label already bound in `drawer`). Returns list of
    (x,y) integer pairs."""
    idxs = []
    while len(idxs) < drawer.arity:
        i = drawer.draw(len(fb))
        if i in idxs:
            continue
        idxs.append(i)
    return [fb[i] for i in idxs]


class ArityDrawer(Drawer):
    """A Drawer additionally carrying its target tuple arity, for readability
    at the call site of draw_distinct_fb_tuple."""

    def __init__(self, arity, *a, **kw):
        super().__init__(*a, **kw)
        self.arity = arity


def signed_sum_x_coords(F: Fp2, A_fp2, points_xy):
    """points_xy: list of (x,y) integer pairs (real, F_p-rational).
    Returns dict key(eps_2..eps_{m-1}) -> x-coordinate value in F_p, or the
    sentinel 'INF' for the point at infinity."""
    pts = [((F.from_fp(x), F.from_fp(y))) for x, y in points_xy]
    P1 = pts[0]
    partial = {(): P1}
    for Pi in pts[1:]:
        negPi = ec_neg_fp2(F, Pi)
        new_partial = {}
        for key, pt in partial.items():
            new_partial[key + (1,)] = ec_add_fp2(F, pt, Pi, A_fp2)
            new_partial[key + (-1,)] = ec_add_fp2(F, pt, negPi, A_fp2)
        partial = new_partial
    out = {}
    for key, pt in partial.items():
        out[key] = "INF" if pt is None else pt[0][0]
    return out


def collision_count(x_coords: dict):
    """D = (#sign classes) - (#distinct x-coordinate values, where 'INF' is
    its own distinct value)."""
    values = list(x_coords.values())
    n_total = len(values)
    n_distinct = len(set(values))
    return n_total - n_distinct
