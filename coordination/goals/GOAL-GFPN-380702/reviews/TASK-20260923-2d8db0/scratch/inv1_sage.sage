# INVOCATION 1, part 2 (TASK-20260923-2d8db0): third-opinion check of the J1 point certificates
# in Sage 10.9, over the quotient ring GF(p)[t]/(t^5 - 3) (GMP/NTL backend, generic Sage
# point arithmetic), deliberately NOT GF(p^5) -- Sage's GF(p^5) is PARI FFELT and Sage's
# finite-field point multiplication calls pari.ellmul (checked in dev/sage_toy.sage).
import json, os, sys
here = os.getcwd()          # run_inv1.sh cds into scratch/ first
# E(x, y) raises unless (x, y) satisfies the curve equation, so construction success == on-curve.
cur = json.load(open(os.path.join(here, "inv1", "curves.json")))
p = 2**64 - 2**32 + 1
R = PolynomialRing(GF(p), 't'); t = R.gen()
K = R.quotient(t**5 - 3, 'w'); w = K.gen()
def el(c): return sum(K(int(ci)) * w**i for i, ci in enumerate(c))
out = {"ring": str(K), "ring_type": type(K).__name__, "base_elt_type": type(GF(p)(1)).__name__}
for name, c in cur.items():
    E = EllipticCurve(K, [el(c["A"]), el(c["B"])])
    P = E(el(c["P"][0]), el(c["P"][1]))
    n = Integer(c["n"]); h = Integer(c["h"])
    res = {"curve_class": type(E).__name__, "point_class": type(P).__name__,
           "P_on_curve": True, "P_nonzero": not P.is_zero(),
           "nP_zero": (n * P).is_zero(), "neg_control_(n+2)P_zero": ((n + 2) * P).is_zero()}
    if h == 2:
        x2 = K(2) / 3
        res["X=2/3_root_of_cubic"] = (x2**3 + el(c["A"]) * x2 + el(c["B"])) == 0
        T = E(x2, 0)
        res["T_has_order_2"] = (2 * T).is_zero() and not T.is_zero()
    q = p**5
    s = isqrt(4 * q)
    hn = h * n
    res["hasse_unique_multiple"] = len([k for k in range((q + 1 - s) // hn, (q + 1 + s) // hn + 2) if q + 1 - s <= k * hn <= q + 1 + s]) == 1
    out[name] = res
json.dump(out, open(os.path.join(here, "inv1", "sage_third_opinion.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
