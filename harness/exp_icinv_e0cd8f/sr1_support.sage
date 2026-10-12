## EXP-ICINV-e0cd8f -- SR1 SUPPORT GATE, computed in SageMath.
##
## Run as:  sage harness/exp_icinv_e0cd8f/sr1_support.sage <in.json> <out.json>
##
## Sage is NOT importable from the host python3 on this execution host, so the
## driver shells out to the `sage` CLI and this file is a separate source
## artifact whose sha256 the driver pins into the run manifest by hand (it
## cannot appear in the driver's sys.modules).
##
## WHAT THIS FILE DOES, AND ONLY THIS:
##   (1) C-SUPPORT: re-derives the monomial support counts of S_3 SYMBOLICALLY,
##       over QQ[a, b, x1, x2, x3] with a and b as free indeterminates, then in
##       the two specialisations a = 0 and b = 0. No count is transcribed from
##       any record; the driver compares these against reference counts it reads
##       from a committed record at run time.
##   (2) computes the S_3 and S_4 monomial support of every supplied curve over
##       GF(p), from that curve's own (a, b).
##   (3) C-GAUGE: recomputes both on (u^4 a, u^6 b) for the driver-supplied u,
##       and additionally checks the exact weighted identity
##           S_3^{(u^4 a, u^6 b)}(u^2 x1, u^2 x2, u^2 x3) == u^8 * S_3^{(a,b)}
##       which holds because S_3 is weighted-homogeneous of weight 8 for
##       wt(x_i) = 2, wt(a) = 4, wt(b) = 6.
##
## NO IDEAL IS BUILT AND NO RESOLUTION IS COMPUTED HERE. The contract's SR3
## backend gate runs before any resolution, and this script runs before SR3.
##
## NO f_V ANYWHERE.

import json
import sys
import time


def s3_poly(A, B, u, v, w):
    """S_3 for y^2 = x^3 + A x + B, in the ring variables u, v, w."""
    return ((u - v) ** 2 * w ** 2
            - 2 * ((u + v) * (u * v + A) + 2 * B) * w
            + ((u * v - A) ** 2 - 4 * B * (u + v)))


def derive_support_symbolically():
    """C-SUPPORT: generic / a=0 / b=0 monomial support of S_3, over QQ[a,b,x]."""
    R = PolynomialRing(QQ, ['a', 'b', 'x1', 'x2', 'x3'])
    a, b, x1, x2, x3 = R.gens()
    S3 = s3_poly(a, b, x1, x2, x3)
    generic = S3.monomials()
    at_a0 = S3.subs({a: R(0)}).monomials()
    at_b0 = S3.subs({b: R(0)}).monomials()
    return {
        "ring": str(R),
        "s3_expression": str(S3),
        "generic_count": len(generic),
        "generic_monomials": sorted(str(m) for m in generic),
        "a_eq_0_count": len(at_a0),
        "a_eq_0_monomials": sorted(str(m) for m in at_a0),
        "b_eq_0_count": len(at_b0),
        "b_eq_0_monomials": sorted(str(m) for m in at_b0),
        "method": ("symbolic expansion over QQ[a,b,x1,x2,x3] with a and b free "
                   "indeterminates; counts are len(poly.monomials())"),
    }


def curve_supports(p, a, b, S4_ring, S3_ring):
    """S_3 and S_4 monomial support over GF(p) for one curve (a, b)."""
    F = GF(p)
    z1, z2, z3 = S3_ring.gens()
    S3 = s3_poly(F(a), F(b), z1, z2, z3)
    y1, y2, y3, y4, tt = S4_ring.gens()
    left = s3_poly(F(a), F(b), y1, y2, tt)
    right = s3_poly(F(a), F(b), y3, y4, tt)
    S4 = left.resultant(right, tt)
    return len(S3.monomials()), len(S4.monomials()), S3


def main():
    with open(sys.argv[1]) as fh:
        spec = json.load(fh)
    p = int(spec["p"])
    F = GF(p)
    S3_ring = PolynomialRing(F, ['x1', 'x2', 'x3'], order='degrevlex')
    S4_ring = PolynomialRing(F, ['y1', 'y2', 'y3', 'y4', 'tt'])
    z1, z2, z3 = S3_ring.gens()

    t0 = time.time()
    derivation = derive_support_symbolically()
    derivation["seconds"] = time.time() - t0

    per_curve = []
    gauge = []
    for rec in spec["curves"]:
        a, b, u = int(rec["a"]), int(rec["b"]), int(rec["gauge_u"])
        c0 = time.time()
        s3n, s4n, S3 = curve_supports(p, a, b, S4_ring, S3_ring)
        per_curve.append({
            "curve_id": rec["curve_id"], "a": a, "b": b,
            "j_invariant": int(rec["j_invariant"]),
            "s3_support": int(s3n),
            "s4_support": int(s4n),
            "seconds": time.time() - c0,
        })
        # C-GAUGE on the same two invariants.
        ag = int(F(u) ** 4 * F(a))
        bg = int(F(u) ** 6 * F(b))
        g3n, g4n, S3g = curve_supports(p, ag, bg, S4_ring, S3_ring)
        lhs = S3g.subs({z1: F(u) ** 2 * z1, z2: F(u) ** 2 * z2,
                        z3: F(u) ** 2 * z3})
        rhs = F(u) ** 8 * S3
        gauge.append({
            "curve_id": rec["curve_id"], "u": u,
            "gauged_a": ag, "gauged_b": bg,
            "s3_support": int(g3n), "s4_support": int(g4n),
            "s3_support_agrees": bool(g3n == s3n),
            "s4_support_agrees": bool(g4n == s4n),
            "weighted_identity_holds": bool(lhs == rhs),
        })

    out = {
        "backend": "sagemath",
        "sage_version": str(version()),
        "p": p,
        "support_derivation": derivation,
        "per_curve": per_curve,
        "gauge_recheck": gauge,
        "ideal_built": False,
        "resolution_computed": False,
        "f_V_present": False,
        "note": ("SR1 stage only. No ideal is constructed and no free "
                 "resolution is computed in this script; the contract's SR3 "
                 "backend gate runs before any resolution."),
    }
    with open(sys.argv[2], "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print("SR1 sage stage complete: %d curves" % len(per_curve))


main()
