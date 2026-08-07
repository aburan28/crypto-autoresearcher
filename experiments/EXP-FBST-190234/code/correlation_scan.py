"""Zero-new-compute correlation scan, requested by red-team review RT-20260807-f01b3c.

EV-FBST-8949fc / EV-FBST-394e55 state "cannot predict without measuring" as a
scope boundary. The red-team review pointed out this was ASSERTED, not TESTED,
and that the already-collected RUN-FBST-190234-002 dataset (280 curves, each
with its (A,B) Weierstrass coefficients and a rank-deficiency label at B=16)
could be mined for correlation against cheap curve invariants at zero
additional cost -- no new curve sampling, no new relation search.

This script does exactly that: it loads the existing raw-result.json, derives
a handful of cheap, well-defined invariants for each curve (quadratic-residue
class of A, of the Weierstrass B-coefficient, and of the j-invariant; parity
of each coefficient's canonical [0,p) representative), and tests each against
the smallest_x rank-deficiency label at B=16 via a 2x2 contingency table and
Fisher's exact test.

Honesty note, stated before any result is seen: with only 14 deficient cases
among 280 and roughly a handful of candidate invariants, this is a small,
likely underpowered, multiple-comparisons-prone scan. A "hit" here is a lead
to flag, not a discovery to promote -- consistent with red-team's framing
("report a null result plainly if none is found").
"""

from __future__ import annotations

import json
import math


def qr(v: int, p: int) -> bool:
    v %= p
    return v == 0 or pow(v, (p - 1) // 2, p) == 1


def j_invariant(A: int, B: int, p: int) -> int:
    denom = (4 * A**3 + 27 * B**2) % p
    num = (1728 * 4 * A**3) % p
    return num * pow(denom, p - 2, p) % p


def fisher_exact_2x2(a: int, b: int, c: int, d: int) -> float:
    """Two-sided Fisher exact test p-value for a 2x2 table, via exact
    hypergeometric enumeration (n is small here, so no approximation needed).
    """
    def log_choose(n, k):
        if k < 0 or k > n:
            return float("-inf")
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)

    n = a + b + c + d
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    log_p_obs = log_choose(row1, a) + log_choose(row2, c) - log_choose(n, col1)
    total = 0.0
    lo = max(0, col1 - row2)
    hi = min(row1, col1)
    for a2 in range(lo, hi + 1):
        c2 = col1 - a2
        b2 = row1 - a2
        d2 = row2 - c2
        log_p = log_choose(row1, a2) + log_choose(row2, c2) - log_choose(n, col1)
        if log_p <= log_p_obs + 1e-9:
            total += math.exp(log_p)
    return min(1.0, total)


def main() -> None:
    r = json.load(open("../runs/RUN-FBST-190234-002/raw-result.json"))
    p = r["p"]
    B_FB = 16  # the factor-base size where deficiency was observed

    rows = []
    for g in r["groups"].values():
        for c in g["curves"]:
            A, Bw = c["A"], c["B"]
            st = c["stats"].get(str(B_FB), {}).get("smallest_x")
            if st is None:
                continue
            deficient = st["relation_rank"] < B_FB
            j = j_invariant(A, Bw, p)
            rows.append({
                "N": g["target_N"], "A": A, "Bw": Bw, "j": j,
                "deficient": deficient,
                "QR_A": qr(A, p), "QR_Bw": qr(Bw, p), "QR_j": qr(j, p),
                "A_odd": A % 2 == 1, "Bw_odd": Bw % 2 == 1,
                "A_gt_Bw": A > Bw,
            })

    n_total = len(rows)
    n_deficient = sum(r["deficient"] for r in rows)
    print(f"n_curves={n_total} n_deficient={n_deficient} "
          f"(rate={n_deficient/n_total:.4f})")

    invariants = ["QR_A", "QR_Bw", "QR_j", "A_odd", "Bw_odd", "A_gt_Bw"]
    results = {}
    for inv in invariants:
        a = sum(1 for r in rows if r[inv] and r["deficient"])
        b = sum(1 for r in rows if r[inv] and not r["deficient"])
        c = sum(1 for r in rows if not r[inv] and r["deficient"])
        d = sum(1 for r in rows if not r[inv] and not r["deficient"])
        pval = fisher_exact_2x2(a, b, c, d)
        odds = (a * d) / (b * c) if b * c else float("inf")
        results[inv] = {"table": {"inv_true_deficient": a, "inv_true_ok": b,
                                   "inv_false_deficient": c, "inv_false_ok": d},
                         "fisher_p": pval, "odds_ratio": odds}
        print(f"{inv:10s} table=({a},{b},{c},{d})  fisher_p={pval:.4f}  "
              f"odds_ratio={odds if odds != float('inf') else 'inf':>8}")

    out = {"n_curves": n_total, "n_deficient": n_deficient,
           "B_factor_base": B_FB, "invariants_tested": results}
    json.dump(out, open("correlation_scan_result.json", "w"), indent=2)
    print("\nBonferroni threshold at alpha=0.05 over", len(invariants),
          "tests:", 0.05 / len(invariants))


if __name__ == "__main__":
    main()
