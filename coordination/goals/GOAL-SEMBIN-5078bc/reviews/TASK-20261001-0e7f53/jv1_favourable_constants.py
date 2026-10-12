"""JV-1 exploratory (NON-GATING, not a v2 row): the most IC-favourable CONSTANT
accounting this reviewer can justify inside the v2 s-range (s <= floor(m/2)).

  probe side  : X-1's truncated-MITM count, s! in place of m!
                PROBE = d + N + log2(s!) - s d     (relations x probes per relation)
  table side  : distinct s-multiset sums, FILL = log2 binom(2^d + s - 1, s)
  LA          : 2d
  guard G1    : X-1's own CALLS = d + N + log2 s! - m d >= 0 (full per-target enumeration)
  guard G2    : PROBE >= 0 only (at least one probe in total; IC-favourable)
Store-free (s = S) and every finite budget (distinct entries <= B).
Reports per-degree minimum margin vs VOW and PUB(131), and any sub-rho cell.
"""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402
from jv1_diff_primary import BUDGETS, MS, grid, log2B  # noqa: E402
from jv1_fill_charge_variants import log2_multisets  # noqa: E402

out = {}
for guard in ("G1", "G2"):
    per = {}
    sub = 0
    for n in hm.DEGREES:
        N, V = hm.N_of(n), hm.vow(n)
        best = None
        for b in BUDGETS:
            lb = log2B(b)
            for m in MS:
                S = m // 2
                for d in grid(float(n)):
                    s = S
                    if lb is not None:
                        s = 0
                        for sp in range(S, 0, -1):
                            if log2_multisets(d, sp) <= lb + 1e-12:
                                s = sp
                                break
                    if s < 1:
                        continue
                    ls = hm.L_of(s)
                    probe = d + N + ls - s * d
                    calls = d + N + ls - m * d
                    if guard == "G1" and calls < 0:
                        continue
                    if guard == "G2" and probe < 0:
                        continue
                    T = hm.log2sumexp2(probe, log2_multisets(d, s), 2.0 * d)
                    if T < V or (n == 131 and T < hm.PUB_131):
                        sub += 1
                    if best is None or T < best[0]:
                        best = (T, b, m, s, d)
        per[str(n)] = dict(TOTAL=best[0], margin_vs_VOW=best[0] - V,
                           margin_vs_PUB=(best[0] - hm.PUB_131) if n == 131 else None,
                           argmin=dict(B=best[1], m=best[2], s=best[3], d=best[4]),
                           analytic_store_free_s8=(N / 2 + hm.L_of(8)) / 15 + 1 - math.log2(0.886))
    out[guard] = dict(subrho_cells=sub, per_degree=per)
    print(guard, "subrho", sub, {k: (round(v["margin_vs_VOW"], 2), v["argmin"]["m"], v["argmin"]["s"]) for k, v in per.items()})
(HERE / "jv1_favourable_constants_output.json").write_text(json.dumps(out, indent=1))
