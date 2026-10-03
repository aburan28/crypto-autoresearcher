"""Lift-by-factoring: cubic X^3 + e1 X^2 + e2 X + e3 over F_{2^n}."""
from __future__ import annotations


def eval_cubic(F, e1, e2, e3, x):
    # X^3 + e1 X^2 + e2 X + e3
    x2 = F.mul(x, x)
    x3 = F.mul(x2, x)
    return x3 ^ F.mul(e1, x2) ^ F.mul(e2, x) ^ e3


def roots_in_set(F, e1, e2, e3, candidates: list[int]) -> list[int]:
    """All roots among candidates (with multiplicity not tracked beyond list)."""
    return [c for c in candidates if eval_cubic(F, e1, e2, e3, c) == 0]


def lift_e_solution(F, e1, e2, e3, V_set: set[int]) -> dict:
    """Test whether (e1,e2,e3) arises from a triple in V^3.

    Returns roots found in V and whether they reproduce the e-vector.
    """
    from symmetrised_s4 import elementary_symmetric

    roots = roots_in_set(F, e1, e2, e3, list(V_set))
    # Need 3 roots in V (counting a triple whose elementary symmetric match).
    # Search unordered triples from distinct-or-not roots.
    genuine = False
    witness = None
    # If fewer than 1 root, cannot be genuine for a split cubic over V.
    # Exhaust small root list: try all triples from roots with replacement
    # whose e-vector matches — but roots_in_set only finds roots; a cubic
    # may have 1 or 3 roots in the field. Prefer: try all ordered triples
    # from the found roots (size usually <=3).
    R = roots
    if len(R) >= 1:
        # Also allow multiple roots: try all |R|^3 small
        for x1 in R:
            for x2 in R:
                for x3 in R:
                    ee = elementary_symmetric(F, x1, x2, x3)
                    if ee == (e1, e2, e3) and x1 in V_set and x2 in V_set and x3 in V_set:
                        genuine = True
                        witness = (x1, x2, x3)
                        break
                if genuine:
                    break
            if genuine:
                break
    return {
        "roots_in_V": roots,
        "n_roots_in_V": len(roots),
        "genuine": genuine,
        "witness": witness,
    }


def independent_recheck_decomposition(F, CurveCls, A, B, x1, x2, x3, xR) -> dict:
    """Fresh-curve re-check: S4(x1,x2,x3,xR)=0 and optional point lifts.

    certificate.kind decomposition — independent of the e-space enumerator.
    """
    from symmetrised_s4 import s4_field

    F2 = type(F)(F.n, F.mod) if hasattr(F, "mod") else F  # same tables ok; new Curve
    E = CurveCls(F2, A, B)
    s4 = s4_field(F2, B, x1, x2, x3, xR)
    lifts = []
    on_curve_ok = True
    for x in (x1, x2, x3, xR):
        P = E.lift_x(x)
        lifts.append(None if P is None else [int(P[0]), int(P[1])])
        # abscissa may fail Trace test — Semaev condition is still meaningful
        # on x-coords alone; record liftability separately.
    return {
        "s4_zero": s4 == 0,
        "s4_value": int(s4),
        "point_lifts": lifts,
        "verified": s4 == 0,
        "curve_A": int(A),
        "curve_B": int(B),
        "x_triple": [int(x1), int(x2), int(x3)],
        "x_R": int(xR),
    }
