"""JV-1 attack step 3 (and the FILL / domain sub-claims of the joint).

Question: is FILL = s*d a LOWER bound on building the oracle's table, neither
over- nor under-charged; and what does each of C-1 (construction charge) and
C-2 (CALLS >= 0 domain guard) contribute?

The v2 oracle tabulates ORDERED s-tuples of F: |F|^s entries. A table is keyed
by the SUM, which is symmetric in the tuple, so the ordered table holds each
distinct key ~s! times. A table of s-MULTISETS of F (binom(|F|+s-1, s) entries,
which includes every repeated-element sum, so it is a superset of the distinct
keys) serves the SAME probe law o = (m-s)d with identical success: every
decomposition found through an ordered table entry is found through the
multiset entry with the same sum. It is built at one group addition per entry by
depth-first enumeration of non-decreasing index tuples (each node = parent sum
+ one element; internal nodes are a 1/|F| fraction), plus one write.

Variants evaluated on the full v2 grid (d = 1.0 .. n step 0.25, m 2..16, every
primary model and budget):
  V2       the v2 header block (reference)
  VD       FILL_D = log2 binom(2^d + s - 1, s); budget law unchanged (s*d <= log2 B)
  VDB      FILL_D, and the budget law applied to the distinct entries:
           s = max{s' <= S : log2 binom(2^d + s' - 1, s') <= log2 B}
  VNOFILL  FILL removed entirely, C-2 domain guard kept       (C-2 alone)
  VNOGUARD FILL kept, C-2 guard removed, CALLS < 0 cells kept unclamped as in v1
           (C-1 alone)
  VNEITHER FILL removed and guard removed (= v1 probe-only, store-free reading)
For each: in-domain (where the variant has a domain) sub-rho counts vs VOW and
vs PUB at n = 131, per-degree minimum TOTAL and its margin vs VOW, and the
largest in-domain |TOTAL_variant - TOTAL_v2|.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402
from jv1_diff_primary import BUDGETS, COMBOS, MS, PRIMARY, grid, log2B  # noqa: E402


def log2_multisets(d: float, s: int) -> float:
    """log2 binom(2^d + s - 1, s) = sum_{i<s} log2(2^d + i) - log2 s!."""
    if s <= 0:
        return -math.inf
    acc = 0.0
    for i in range(s):
        acc += d + math.log2(1.0 + i * 2.0 ** (-d)) if d < 1000 else d
    return acc - hm.L_of(s)


def variant_cell(n, m, d, model, b, variant):
    lb = log2B(b)
    N, L, S = hm.N_of(n), hm.L_of(m), m // 2
    if model in ("FREE", "ENUM"):
        s = 0
    elif model == "MITM" or lb is None:
        s = S
    else:
        if variant == "VDB":
            s = 0
            for sp in range(S, 0, -1):
                if log2_multisets(d, sp) <= lb + 1e-12:
                    s = sp
                    break
        else:
            s = min(S, int(math.floor(lb / d)))
    TPR = N + L - m * d
    CALLS = d + TPR
    o = 0.0 if model == "FREE" else ((m - 1) * d if model == "ENUM" else (m - s) * d)
    PROBE = CALLS + o
    has_table = model in ("MITM", "MITM_CAPPED") and s >= 1
    if variant in ("V2", "VNOGUARD"):
        FILL = s * d if has_table else 0.0
    elif variant in ("VD", "VDB"):
        FILL = log2_multisets(d, s) if has_table else 0.0
    elif variant in ("VNOFILL", "VNEITHER"):
        FILL = -math.inf
    else:
        raise ValueError(variant)
    LA = 2.0 * d
    terms = [PROBE, LA] + ([FILL] if FILL != -math.inf else [])
    TOTAL = hm.log2sumexp2(*terms)
    guarded = variant not in ("VNOGUARD", "VNEITHER")
    in_domain = (CALLS >= 0) if guarded else True
    return TOTAL, in_domain, s


VARIANTS = ("V2", "VD", "VDB", "VNOFILL", "VNOGUARD", "VNEITHER")


def main():
    out = {}
    for var in VARIANTS:
        sub_vow = 0
        sub_pub = 0
        per_deg = {}
        per_budget = {}
        maxdelta = 0.0
        maxdelta_cell = None
        for n in hm.DEGREES:
            V = hm.vow(n)
            best = None
            for model, b in COMBOS:
                if model not in PRIMARY:
                    continue
                for m in MS:
                    for d in grid(float(n)):
                        T, ind, s = variant_cell(n, m, d, model, b, var)
                        if not ind:
                            continue
                        if T < V:
                            sub_vow += 1
                        if n == 131 and T < hm.PUB_131:
                            sub_pub += 1
                        if var in ("VD", "VDB", "VNOFILL"):
                            T2, ind2, _ = variant_cell(n, m, d, model, b, "V2")
                            if ind2 and abs(T - T2) > maxdelta:
                                maxdelta = abs(T - T2)
                                maxdelta_cell = dict(n=n, model=model, B=b, m=m, d=d, s=s, v2=T2, variant=T)
                        if best is None or T < best[0]:
                            best = (T, model, b, m, d, s)
                        if model == "MITM_CAPPED":
                            key = f"{n}|{b}"
                            if key not in per_budget or T < per_budget[key][0]:
                                per_budget[key] = (T, m, d, s, T - V)
            per_deg[str(n)] = dict(TOTAL=best[0], margin_vs_VOW=best[0] - V,
                                   margin_vs_PUB=(best[0] - hm.PUB_131) if n == 131 else None,
                                   argmin=dict(model=best[1], B=best[2], m=best[3], d=best[4], s=best[5]))
        out[var] = dict(subrho_vs_VOW=sub_vow, subrho_vs_PUB_131=sub_pub, per_degree_min=per_deg,
                        max_abs_in_domain_delta_vs_v2=maxdelta, max_delta_cell=maxdelta_cell,
                        per_budget_min_MITM_CAPPED={k: dict(TOTAL=v[0], m=v[1], d=v[2], s=v[3], margin_vs_VOW=v[4])
                                                   for k, v in per_budget.items()})
        print(var, "subrho VOW", sub_vow, "PUB131", sub_pub, "max|delta|", round(maxdelta, 4))
        print("   per-degree margin vs VOW:",
              {k: round(v["margin_vs_VOW"], 3) for k, v in per_deg.items()})
    (HERE / "jv1_fill_charge_variants_output.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
