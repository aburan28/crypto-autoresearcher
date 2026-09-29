"""V1, beyond the attack plan: how often IS a uniformly random target
decomposable over the subspace V?  The Coordinator's V1 prior estimates
~4% / 8% / 2% at n15l5 / n17l6 / n19l6 from a counting heuristic.  This
measures a lower bound exactly, per cell, and checks it against all 60
shipped instances.

Construction.  Let phi be the 2^n-power Frobenius on E(F_{2^{2n}}).  For a
point P with x(P) in F_{2^n}, phi(P) = P (P in E(F_{2^n})) or phi(P) = -P
(P in the twist part).  For S = P1+P2+P3 to have x(S) in F_{2^n} we need
phi(S) = +-S, and expanding gives three generic families plus 2-torsion
corrections:

  F1  all three on E(F_{2^n})      -> x(P1+P2+P3)
  F2  all three on the twist       -> x(Q1+Q2+Q3)
  F3  a cancelling pair P, -P      -> x(P3) for x(P3) in V, i.e. all of V

The remaining cases require a pair summing to the unique 2-torsion point
(0, sqrt(b)), so D_lower = F1 | F2 | V is a LOWER bound, not the exact set.
It is checked against the 60 shipped instances: every shipped target must be
classified correctly or the bound is not usable.
"""
from __future__ import annotations

import glob
import json
import os

from valgf import GF2n, BinaryCurve, INF, parse_info

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.dirname(os.path.abspath(__file__))


def sums_over_subspace(curve, l):
    """All x(P1+P2+P3) with x(Pi) in V = {0,...,2^l-1} and Pi on `curve`."""
    reps = {}
    for x in range(1 << l):
        p = curve.points_with_x(x)
        if p:
            reps[x] = p[0]
    xs = sorted(reps)
    out = set()
    # pair sums, memoised: P_a + s*P_b for s in {+1,-1}
    pairs = {}
    for i, a in enumerate(xs):
        Pa = reps[a]
        for b in xs[i:]:
            Pb = reps[b]
            pairs[(a, b, 1)] = curve.add(Pa, Pb)
            pairs[(a, b, -1)] = curve.add(Pa, curve.neg(Pb))
    for i, a in enumerate(xs):
        for j in range(i, len(xs)):
            b = xs[j]
            for s2 in (1, -1):
                Q = pairs[(a, b, s2)]
                for k in range(j, len(xs)):
                    c = xs[k]
                    Pc = reps[c]
                    for s3 in (1, -1):
                        S = curve.add(Q, Pc if s3 == 1 else curve.neg(Pc))
                        if S is not INF:
                            out.add(S[0])
    return out


def main():
    cells = {}
    for nl in ((15, 5), (17, 6), (19, 6)):
        n, l = nl
        info = parse_info(os.path.join(BENCH, f"INFOn{n}l{l}-1-S.dimacs"))
        F = GF2n(n, info["modulus_bits"])
        E = BinaryCurve(F, 1, 1)
        TW = BinaryCurve(F, 0, 1)
        f1 = sums_over_subspace(E, l)
        f2 = sums_over_subspace(TW, l)
        f3set = set(range(1 << l))
        D = f1 | f2 | f3set
        cells[f"n{n}l{l}"] = {
            "n": n, "l": l, "F": F, "E": E, "TW": TW,
            "F1_all_on_E": len(f1), "F2_all_on_twist": len(f2),
            "F3_subspace": len(f3set),
            "D_lower_size": len(D), "field_size": 1 << n,
            "density_lower_bound": len(D) / (1 << n),
            "expected_decomposable_U_in_10": 10 * len(D) / (1 << n),
            "_D": D,
        }
        print(f"n{n}l{l}: |F1|={len(f1)} |F2|={len(f2)} |V|={len(f3set)} "
              f"|D_lower|={len(D)} / 2^{n}={1<<n} = {len(D)/(1<<n):.5f}")

    # cross-check against the 60 shipped instances
    rows = []
    mis = 0
    for path in sorted(glob.glob(os.path.join(BENCH, "INFO*.dimacs"))):
        info = parse_info(path)
        name = os.path.basename(path)[4:-7]
        cell = f"n{info['n']}l{info['l']}"
        c = cells[cell]
        xr = c["F"].from_bits_lsb_first(info["xr_bits"])
        inD = xr in c["_D"]
        rows.append({"instance": name, "cell": cell, "label": info["label"],
                     "xr_hex": hex(xr), "in_D_lower": bool(inD)})
        expected_sat = info["label"] == "S" or name == "n19l6-19-U"
        if inD != expected_sat:
            mis += 1
            print("  MISCLASSIFIED", name, info["label"], "in_D_lower", inD)
    print(f"  shipped-instance misclassifications by D_lower: {mis}/60")
    nU_in_D = sum(1 for r in rows if r["label"] == "U" and r["in_D_lower"])
    print(f"  U instances whose target lies in D_lower: {nU_in_D}/30")

    out = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")
               and kk not in ("F", "E", "TW")}
           for k, v in cells.items()}
    out["shipped_targets"] = rows
    out["shipped_misclassifications"] = mis
    with open(os.path.join(OUT, "v1_density.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
