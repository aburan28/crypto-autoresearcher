"""JV-1 attack step 2: price the v2 oracle table as FREE PRECOMPUTATION and as a
cost AMORTISED OVER T TARGETS, and compare each v2 row against the baseline for
THAT reading (not single-instance vOW).

Readings, evaluated on every in-domain v2 primary cell (bound n, ENUM / MITM /
MITM_CAPPED, every budget; v2 oracle laws, s <= floor(m/2)):

  P1  free table. The s-sum table depends only on (E, F) and is precomputed for
      free. Per-target ONLINE cost = log2(2^PROBE + 2^LA) (the relation phase
      involves the target, so it is per target). Advice a = s*d log2 entries.
  P2  free table AND free factor-base logarithms (relations among F and P, and
      the linear algebra, are target-independent). Per-target ONLINE cost = one
      descent = max(TPR, 0) + o (at least one oracle call). Advice
      a = log2(2^(s d) + 2^d).
  P3a T targets, table built once and charged, relation phase + LA per target:
      amortised = log2(2^FILL + T 2^(log2(2^PROBE+2^LA))) - t.
  P3b T targets, table + factor-base logs + LA built once and charged, one
      descent per target: amortised = log2(2^FILL + 2^PROBE + 2^LA + T 2^ON_P2) - t.

Baselines (log2 group operations; provenance in the validation report):
  VOW        log2 0.886 + N/2 (single instance; rho may ignore advice)
  BL_on(a)   log2 1.77 + (N - a)/2, floored at 0 -- Bernstein-Lange 2012 online
             cost with a table of 2^a distinguished points (KN-LIT-7cc07f anchor
             1.77 l^(1/3) at table l^(1/3); sqrt(N/A) scaling assumed off-anchor)
  CGK(a)     (N - a)/2 -- shape of the Corrigan-Gibbs-Kogan generic preprocessing
             lower bound S T^2 ~ N (KN-LIT-013), S taken as ENTRIES (IC-favourable:
             real advice bits >= entries), epsilon = 1, polylog factors dropped
  BLopt(t)   log2(2 sqrt(1.24*1.77)) + (N - t)/2 -- BL precomputation 1.24 sqrt(N A)
             plus T online 1.77 sqrt(N/A), table A optimised, amortised per target
  KS(t)      0.5 + (N - t)/2 -- Kuhn-Struik, about sqrt(2 T N) total for T logs
             (KN-LIT-f47b10; constant marked there as not re-verified)
  Free-precomputation baseline  = min(VOW, BL_on(a))
  Multi-instance baseline        = min(VOW, KS(t), BLopt(t))

Also evaluated (EXPLORATORY, OUTSIDE the v2 oracle laws, never a v2 row): EXT,
the IC-favourable precomputation oracle -- table side s in 1..m-1, distinct
s-multiset table (FILL = log2 binom(2^d+s-1, s)), each probe one group op hitting
with probability 2^(FILL - N); descent ON = max(N - FILL, 0); relation phase
PRE = d + max(N - FILL, 0). It is baby-step giant-step with baby steps drawn from
s-sums of F, and is reported only so that prior item (c) is closed on the
strongest reading this reviewer could construct.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import jv1_header_model as hm  # noqa: E402
from jv1_diff_primary import COMBOS, MS, PRIMARY, grid, log2B  # noqa: E402
from jv1_fill_charge_variants import log2_multisets  # noqa: E402

C_BL_ON = math.log2(1.77)
C_BL_OPT = math.log2(2.0 * math.sqrt(1.24 * 1.77))
LSE = hm.log2sumexp2


def t_values(N):
    return [0.0, 10.0, 20.0, 30.0, 40.0, round(N / 4, 3), round(N / 3, 3), round(N / 2, 3)]


def base_online(N, a):
    return min(hm.log2sumexp2(math.log2(0.886)) + N / 2.0 if False else math.log2(0.886) + N / 2.0,
               max(0.0, C_BL_ON + (N - a) / 2.0))


def base_multi(N, t):
    vow = math.log2(0.886) + N / 2.0
    ks = 0.5 + (N - t) / 2.0
    blopt = C_BL_OPT + (N - t) / 2.0
    return dict(VOW=vow, KS=ks, BLopt=blopt, best=min(vow, ks, blopt))


def new_tracker():
    return dict(min_margin=math.inf, argmin=None, negatives=0, cells=0)


def upd(tr, margin, info):
    tr["cells"] += 1
    if margin < 0:
        tr["negatives"] += 1
    if margin < tr["min_margin"]:
        tr["min_margin"], tr["argmin"] = margin, info


def main():
    out = {"v2_rows": {}, "EXT_exploratory": {}}
    for n in hm.DEGREES:
        N = hm.N_of(n)
        V = hm.vow(n)
        ts = t_values(N)
        R = {k: new_tracker() for k in ("P1_vs_best_online", "P1_vs_CGK", "P1_vs_VOW",
                                         "P2_vs_best_online", "P2_vs_CGK", "P2_vs_VOW")}
        R3 = {f"P3a_t{t}": new_tracker() for t in ts}
        R3.update({f"P3b_t{t}": new_tracker() for t in ts})
        R3.update({f"P3a_t{t}_vs_BLopt": new_tracker() for t in ts})
        R3.update({f"P3b_t{t}_vs_BLopt": new_tracker() for t in ts})
        min_online_P1 = math.inf
        min_online_P2 = math.inf
        for model, b in COMBOS:
            if model not in PRIMARY:
                continue
            for m in MS:
                for d in grid(float(n)):
                    c = hm.cell(n, m, d, model, log2B(b))
                    if c["out_of_domain"]:
                        continue
                    s = c["s"]
                    has_table = model in ("MITM", "MITM_CAPPED") and s >= 1
                    info = dict(model=model, B=b, m=m, d=d, s=s)
                    # P1
                    on1 = LSE(c["PROBE"], c["LA"])
                    a1 = s * d if has_table else 0.0
                    min_online_P1 = min(min_online_P1, on1)
                    upd(R["P1_vs_best_online"], on1 - base_online(N, a1), info)
                    upd(R["P1_vs_CGK"], on1 - (N - a1) / 2.0, info)
                    upd(R["P1_vs_VOW"], on1 - V, info)
                    # P2
                    on2 = max(c["TPR"], 0.0) + c["o"]
                    a2 = LSE(s * d, d) if has_table else d
                    min_online_P2 = min(min_online_P2, on2)
                    upd(R["P2_vs_best_online"], on2 - base_online(N, a2), info)
                    upd(R["P2_vs_CGK"], on2 - (N - a2) / 2.0, info)
                    upd(R["P2_vs_VOW"], on2 - V, info)
                    # P3
                    fill_terms = [c["FILL"]] if has_table else []
                    for t in ts:
                        bm = base_multi(N, t)
                        am_a = LSE(*(fill_terms + [on1 + t])) - t
                        am_b = LSE(*(fill_terms + [c["PROBE"], c["LA"], on2 + t])) - t
                        upd(R3[f"P3a_t{t}"], am_a - bm["best"], info)
                        upd(R3[f"P3b_t{t}"], am_b - bm["best"], info)
                        upd(R3[f"P3a_t{t}_vs_BLopt"], am_a - bm["BLopt"], info)
                        upd(R3[f"P3b_t{t}_vs_BLopt"], am_b - bm["BLopt"], info)
        R.update(R3)
        out["v2_rows"][str(n)] = dict(
            N=N, VOW=V, min_online_P1=min_online_P1, min_online_P2=min_online_P2,
            analytic_floor_online=(N + 1.0) / 2.0,  # (N + L)/2 with L >= 1 at m >= 2
            readings={k: dict(min_margin=v["min_margin"], negatives=v["negatives"], cells=v["cells"],
                              argmin=v["argmin"]) for k, v in R.items()})
        print(n, "v2 rows: min online P1 %.2f  P2 %.2f  VOW %.2f | negatives:" % (min_online_P1, min_online_P2, V),
              {k: v["negatives"] for k, v in R.items() if v["negatives"]} or 0,
              "| min margins P1 %.2f P2 %.2f P3b(t=N/2) %.2f" % (
                  R["P1_vs_best_online"]["min_margin"], R["P2_vs_best_online"]["min_margin"],
                  R[f"P3b_t{ts[-1]}"]["min_margin"]))

        # ---------------- EXT (exploratory) ----------------
        E = {}
        for t in ts:
            E[f"t{t}"] = dict(best=new_tracker(), BLopt=new_tracker(), KS=new_tracker(), VOW=new_tracker())
        E["online_vs_BL_on_a_le_N_over_2"] = new_tracker()
        E["online_vs_CGK"] = new_tracker()
        for m in MS:
            for s in range(1, m):
                for d in grid(float(n)):
                    fill = log2_multisets(d, s)
                    if fill > N:  # table larger than the group: outside any sensible regime
                        continue
                    on = max(N - fill, 0.0)
                    pre = d + max(N - fill, 0.0)
                    la = 2.0 * d
                    info = dict(m=m, s=s, d=d, FILL=fill)
                    if fill <= N / 2.0:
                        upd(E["online_vs_BL_on_a_le_N_over_2"], on - base_online(N, LSE(fill, d)), info)
                    upd(E["online_vs_CGK"], on - (N - LSE(fill, d)) / 2.0, info)
                    for t in ts:
                        am = LSE(fill, pre, la, on + t) - t
                        bm = base_multi(N, t)
                        for k in ("best", "BLopt", "KS", "VOW"):
                            upd(E[f"t{t}"][k], am - bm[k], info)
        out["EXT_exploratory"][str(n)] = {
            k: ({kk: dict(min_margin=vv["min_margin"], negatives=vv["negatives"], argmin=vv["argmin"])
                 for kk, vv in v.items()} if "best" in v else
                dict(min_margin=v["min_margin"], negatives=v["negatives"], argmin=v["argmin"]))
            for k, v in E.items()}
        print("   EXT: online vs BL_on (a<=N/2) min %.2f neg %d | vs CGK min %.2f | multi t=N/2: vs best %.2f, vs KS %.2f, vs BLopt %.2f (neg %d)" % (
            E["online_vs_BL_on_a_le_N_over_2"]["min_margin"], E["online_vs_BL_on_a_le_N_over_2"]["negatives"],
            E["online_vs_CGK"]["min_margin"],
            E[f"t{ts[-1]}"]["best"]["min_margin"], E[f"t{ts[-1]}"]["KS"]["min_margin"],
            E[f"t{ts[-1]}"]["BLopt"]["min_margin"], E[f"t{ts[-1]}"]["BLopt"]["negatives"]))
    (HERE / "jv1_precomputation_readings_output.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
