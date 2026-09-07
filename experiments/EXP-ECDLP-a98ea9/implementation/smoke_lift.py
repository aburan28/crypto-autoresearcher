"""Development spot-check of the k-free lift on the c373eb instance.

p=1009, n=47 is outside the Stage 1 band. This is not a Stage 1 cell.
"""
from __future__ import annotations

import json

from curve_find import find_point_of_order_n, fp_mul
from ec_jac import Curve, affine_xy, is_infinity, scalar_mult
from kfree_transport import canonical_order_n_lift, hensel_lift_without_projection

p = 1009
A, B = 1, 1
n = 47
N = 1008  # will be checked
curve = Curve(p=p, A=A, B=B)


def main():
    from curve_find import count_points

    N_comp = count_points(A, B, p)
    S = find_point_of_order_n(A, B, p, N_comp, n)
    assert S is not None
    out = {"p": p, "A": A, "B": B, "N": N_comp, "n": n, "S": list(S), "r_checks": []}
    for r in (1, 2, 3, 4):
        hat = canonical_order_n_lift(curve, S, n, r)
        n_hat = scalar_mult(n, hat, p**r, curve)
        ax, ay = affine_xy(curve, hat, p**r)
        null = hensel_lift_without_projection(curve, S, r)
        nx, ny = affine_xy(curve, null, p**r)
        withheld = 5
        path1 = scalar_mult(withheld, hat, p**r, curve)
        T = fp_mul(withheld, S, p, A)
        path2 = canonical_order_n_lift(curve, T, n, r)
        x1, y1 = affine_xy(curve, path1, p**r)
        x2, y2 = affine_xy(curve, path2, p**r)
        cell = {
            "r": r,
            "n_times_infinity": is_infinity(n_hat, p**r),
            "reduces": (ax % p == S[0] and ay % p == S[1]),
            "null2_equals_treatment": (nx == ax and ny == ay),
            "transport_agree": (x1 == x2 and y1 == y2),
            "x_hat": ax,
        }
        out["r_checks"].append(cell)
        print(cell)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
