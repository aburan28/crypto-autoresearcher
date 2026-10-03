"""J2 step 0: validate this reviewer's tail_rule() against the engine's TailTable.

For small generated prime-order curves (deterministic generator, seeds below),
build FactorBase.random and TailTable at arity 2 and 3 with the numpy build and
the pure-Python build, decode every stored code, and compare the multiset of
stored tails with tail_rule(s, h, L, N) where L are the base logs found by
brute force. Also checks that every stored tail's sum is a finite point whose
y-bit equals the code's low bit (stored orientation s_1 = +1), and counts
x-key deduplication (none expected), caps and identity drops.

Command (declared): nice -n 19 $PY attacks/j2/j2_validate_engine.py --out attacks/j2/out/validate.json
Seeds: curve seeds 1..6 at 12 and 14 bits; FactorBase.random seeds 101..; no RNG of ours.
"""
import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j2lib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    eng = j2lib.load_engine()
    curve, fbm, tails = eng["curve"], eng["factor_base"], eng["tails"]
    results = []
    for bits, cseed, s in ((12, 1, 6), (12, 2, 8), (14, 3, 8), (14, 4, 10), (12, 5, 7), (14, 6, 9)):
        E, P = curve.generate_prime_order_curve(bits, cseed)
        N = E.order
        # brute-force logs
        logs = {}
        R = None
        for k in range(1, N):
            R = E.add(R, P)
            logs[R] = k
        fb = fbm.FactorBase.random(E, s, seed=100 + cseed)
        L = [logs[Pt] for Pt in fb.points]
        for h in (2, 3):
            for accel in (True, False):
                tab = tails.TailTable(E, fb, h, accelerate=accel)
                stored = []
                ybit_ok = 0
                ybit_bad = 0
                xkeys = Counter()
                for x, codes in tab.iter_keys():
                    for code in codes:
                        t, yb = tab.decode(code)
                        stored.append(tuple(t))
                        xkeys[x] += 1
                        # sum on the curve (stored orientation)
                        S = None
                        for i, sg in t:
                            S = E.add(S, fb.points[i] if sg > 0 else E.neg(fb.points[i]))
                        if S is not None and S[0] == x and int(S[1] > E.p // 2) == yb:
                            ybit_ok += 1
                        else:
                            ybit_bad += 1
                rule = [t for t, _ in j2lib.tail_rule(s, h, L, N)]
                rule_formal = [t for t, _ in j2lib.tail_rule(s, h, None, None)]
                same = Counter(stored) == Counter(rule)
                n_identity_dropped = len(rule_formal) - len(rule)
                results.append({
                    "bits": bits, "curve_seed": cseed, "p": E.p, "N": N, "s": s, "h": h,
                    "numpy_build": accel, "stored_tails": len(stored), "entries": tab.entries,
                    "rule_tails": len(rule), "rule_formal_superset": len(rule_formal),
                    "identity_dropped_vs_formal": n_identity_dropped,
                    "multiset_equal_to_rule": same,
                    "stored_minus_rule": len(set(stored) - set(rule)),
                    "rule_minus_stored": len(set(rule) - set(stored)),
                    "all_s1_plus": all(t[0][1] == 1 for t in stored),
                    "ybit_ok": ybit_ok, "ybit_bad": ybit_bad,
                    "distinct_x_keys": len(xkeys), "max_tails_per_xkey": max(xkeys.values()),
                    "formula_check_h3_entries": (4 * (s + 2) * (s + 1) * s // 6 - 2 * (s + 1) * s // 2)
                    if h == 3 else s * s,
                })
    ok = all(r["multiset_equal_to_rule"] and r["ybit_bad"] == 0 and r["all_s1_plus"] for r in results)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump({"all_ok": ok, "cases": results}, open(a.out, "w"), indent=1)
    print("all_ok", ok)
    for r in results:
        print(r["bits"], r["curve_seed"], r["s"], r["h"], r["numpy_build"], r["stored_tails"],
              r["rule_tails"], r["rule_formal_superset"], r["multiset_equal_to_rule"], r["ybit_bad"])


if __name__ == "__main__":
    main()
