"""JV-1 domain checks on the C-2 exclusion (CALLS < 0) and the in-domain set.

  K1  On every in-domain table cell (MITM, MITM_CAPPED with s >= 1, bound n):
      max (FILL - PROBE). Analytic claim: <= 0, i.e. in domain the construction
      charge never dominates, so it moves any in-domain TOTAL by < 1 bit.
  K2  Small-d yield. The header uses |F|^m / m! decompositions per target. At
      small d the true count of m-multisets, binom(2^d + m - 1, m), exceeds it.
      Recompute TPR with the multiset count (an IC-favourable correction) on every
      cell and count in-domain sub-rho cells vs VOW / PUB. Also count in-domain
      cells where 2^d < m (no m distinct elements exist).
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402
from jv1_diff_primary import COMBOS, MS, PRIMARY, grid, log2B  # noqa: E402


def log2_binom_multiset(d, m):
    # log2 binom(2^d + m - 1, m) = sum_{i<m} log2(2^d + i) - log2 m!
    acc = 0.0
    for i in range(m):
        acc += d + math.log2(1.0 + i * 2.0 ** (-d)) if d < 1000 else d
    return acc - hm.L_of(m)


k1_max = -math.inf
k1_arg = None
k2_sub_vow = 0
k2_sub_pub = 0
k2_min_margin = math.inf
k2_arg = None
tiny = 0
tiny_in_domain_argmin_candidates = 0
for n in hm.DEGREES:
    V = hm.vow(n)
    N = hm.N_of(n)
    for model, b in COMBOS:
        if model not in PRIMARY:
            continue
        for m in MS:
            for d in grid(float(n)):
                c = hm.cell(n, m, d, model, log2B(b))
                if not c["out_of_domain"]:
                    if model in ("MITM", "MITM_CAPPED") and c["s"] >= 1:
                        if c["FILL"] - c["PROBE"] > k1_max:
                            k1_max = c["FILL"] - c["PROBE"]
                            k1_arg = dict(n=n, model=model, B=b, m=m, d=d, s=c["s"])
                    if 2.0 ** d < m:
                        tiny += 1
                # K2: multiset yield, guard recomputed with the corrected TPR
                TPRc = N - log2_binom_multiset(d, m)
                CALLSc = d + TPRc
                if CALLSc < 0:
                    continue
                PROBEc = CALLSc + c["o"]
                Tc = hm.log2sumexp2(PROBEc, c["FILL"], c["LA"])
                if Tc - V < k2_min_margin:
                    k2_min_margin, k2_arg = Tc - V, dict(n=n, model=model, B=b, m=m, d=d)
                if Tc < V:
                    k2_sub_vow += 1
                if n == 131 and Tc < hm.PUB_131:
                    k2_sub_pub += 1
out = dict(K1_max_FILL_minus_PROBE_in_domain=k1_max, K1_argmax=k1_arg,
           K2_multiset_yield_in_domain_subrho_vs_VOW=k2_sub_vow, K2_subrho_vs_PUB_131=k2_sub_pub,
           K2_min_margin_vs_VOW=k2_min_margin, K2_argmin=k2_arg,
           in_domain_primary_cells_with_2_pow_d_below_m=tiny)
(HERE / "jv1_domain_checks_output.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
