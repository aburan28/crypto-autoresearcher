#!/usr/bin/env python3
"""Independent re-verification of certified_curves.json.

Deliberately does NOT reuse the solver (ellrank) that produced the points, and
cross-checks the on-curve test two ways: this file's own Fraction arithmetic
and PARI's ellisoncurve.  Independence of the exhibited points is re-derived
from a freshly computed height matrix.
"""
import json, sys
from fractions import Fraction
from cypari import pari
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import pipeline as P

def main():
    src, out, topn = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cc = json.load(open(src))
    res = []
    for rec in cc["curves"][:topn]:
        A, B = int(rec["a_invariants"][3]), int(rec["a_invariants"][4])
        pts = [(Fraction(x), Fraction(y)) for x, y in rec["exhibited_points"]]
        own = [ (y*y == x**3 + A*x + B) for x, y in pts ]
        E = pari.ellinit("[0,0,0,%d,%d]" % (A, B))
        pari_ok = [bool(E.ellisoncurve(pari("[%s,%s]" % (P.frac_str(x), P.frac_str(y))))) for x, y in pts]
        c = P.certify_rank([0, 0, 0, A, B], pts)
        res.append({
            "t": rec["t"], "claimed_rank": rec["certified_rank"],
            "recomputed_rank": c["rank"],
            "agrees": c["rank"] == rec["certified_rank"],
            "n_points": len(pts),
            "own_exact_arithmetic_all_on_curve": all(own),
            "pari_ellisoncurve_all_true": all(pari_ok),
            "cross_check_agrees": own == pari_ok,
            "regulator_det": {str(k): v["regulator_det"] for k, v in c["by_precision"].items()},
            "least_eigenvalue": {str(k): v["least_eigenvalue"] for k, v in c["by_precision"].items()},
            "discriminant_nonzero": (-16 * (4 * A**3 + 27 * B**2)) != 0,
        })
    o = {"source": src, "n_checked": len(res),
         "all_agree": all(r["agrees"] and r["own_exact_arithmetic_all_on_curve"]
                          and r["pari_ellisoncurve_all_true"] for r in res),
         "checks": res}
    json.dump(o, open(out, "w"), indent=2)
    print(json.dumps({"n_checked": o["n_checked"], "all_agree": o["all_agree"],
                      "top": res[0]}, indent=2))

main()
