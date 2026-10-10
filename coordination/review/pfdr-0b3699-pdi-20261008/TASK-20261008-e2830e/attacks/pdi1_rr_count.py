"""TASK-20261008-e2830e Q1 / PDI-1: exact |RR| of Lemma L1 for the arity-2 TT table under the
uniform model, against the generic-multiplicity-3 count 2 C(T, 2) / 3 = T (T - 1) / 3 that
PDI-1's mu_model uses (T = s^2 stored tails). Synthetic and symbolic only; reads no data file.

Stored set V at h = 2 (tails.py docstring: orderings i_1 <= i_2 with s_1 = +1, every suffix
nonzero; "|F|^2 at h = 2"): e_a + e_b and e_a - e_b for a < b, and 2 e_a (F_a - F_a is the
identity and is not stored). |V| = s(s - 1) + s = s^2.

L1: every signed pair (u, w, sigma), u != w in V linearly independent, maps to the projective
class [u - sigma w]; RR is the set of classes hit; E[R] = |RR| / N. For integer vectors with
coefficients in [-4, 4] and a prime N > 64, proportionality mod N equals proportionality over Q
(every 2 x 2 minor has absolute value < N), so classes are counted over Q: divide by the gcd of the
coefficients and make the first nonzero coefficient (indices ascending) positive. All
coefficients are base indices only (TT rows carry kcoef = rhs = 0).

Usage: python -I pdi1_rr_count.py OUT_JSON s [s ...]
"""
import json
import math
import sys
import time
from collections import Counter


def tails(s):
    V = []
    for a in range(s):
        for b in range(a + 1, s):
            V.append(((a, 1), (b, 1)))
            V.append(((a, 1), (b, -1)))
        V.append(((a, 2),))
    return V


def norm(d):
    items = sorted((i, c) for i, c in d.items() if c)
    if not items:
        return None
    g = 0
    for _, c in items:
        g = math.gcd(g, abs(c))
    sgn = 1 if items[0][1] > 0 else -1
    return tuple((i, sgn * c // g) for i, c in items)


def count(s):
    V = tails(s)
    T = len(V)
    mult = Counter()
    dependent = 0
    for x in range(T):
        u = dict(V[x])
        for y in range(x + 1, T):
            w = dict(V[y])
            # dependent mod N <=> proportional over Q (small coefficients); excluded by L1
            if norm(u) == norm(w):
                dependent += 1
                continue
            for sigma in (1, -1):
                d = dict(u)
                for i, c in w.items():
                    d[i] = d.get(i, 0) - sigma * c
                k = norm(d)
                if k is not None:
                    mult[k] += 1
    RR = len(mult)
    generic = T * (T - 1) / 3.0
    hist = Counter(mult.values())

    # classes that cannot occur on a real base: [e_a] (F_a = O) and [e_a +- e_b] (F_a = -+F_b,
    # excluded because base x-coordinates are distinct)
    def unrealizable(k):
        return (len(k) == 1) or (len(k) == 2 and all(abs(c) == 1 for _, c in k))

    n_unreal = sum(1 for k in mult if unrealizable(k))
    RR_real = RR - n_unreal
    return {"s": s, "T": T, "T_equals_s2": T == s * s, "signed_pairs_mapped": int(sum(mult.values())),
            "signed_pairs_equal_T(T-1)": int(sum(mult.values())) == T * (T - 1),
            "dependent_pairs_excluded": dependent, "RR_exact": RR, "generic3_count_T(T-1)/3": generic,
            "RR_equals_T(T+2)/3": RR * 3 == T * (T + 2),
            "ratio_RR_over_generic3": RR / generic, "relative_error_generic3": (generic - RR) / RR,
            "unrealizable_classes": n_unreal, "RR_realizable": RR_real,
            "RR_realizable_equals_T(T-1)/3": RR_real * 3 == T * (T - 1),
            "multiplicity_histogram": {str(k): v for k, v in sorted(hist.items())}}


def main(argv):
    out = argv[1]
    res = {"what": "PDI-1 exact |RR| vs T(T-1)/3 (synthetic, symbolic)", "rows": []}
    t0 = time.time()
    for s in [int(x) for x in argv[2:]]:
        r = count(s)
        res["rows"].append(r)
        print(json.dumps({k: r[k] for k in ("s", "T", "RR_exact", "generic3_count_T(T-1)/3", "RR_equals_T(T+2)/3", "RR_realizable_equals_T(T-1)/3",
                                             "relative_error_generic3")}), flush=True)
    res["elapsed_seconds"] = round(time.time() - t0, 1)
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
