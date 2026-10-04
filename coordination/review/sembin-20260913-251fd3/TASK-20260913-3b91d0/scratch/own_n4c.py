#!/usr/bin/env python3
"""N4(4) follow-up: CHARACTERISE every one of the 194 crossover_surface entries
flagged `monotone_for_200_beyond: false`.  The task-report attributes the
non-monotonicity to "T4 grows linearly in m at fixed small C_0".  My first 14
samples (all C_0 = 2) re-crossed at exactly crossover + 1, which looks like the
ceiling in m = ceil(n / C_0) rather than a drift.  So for each flagged entry:
step-1 margins over [crossover, crossover + 200]; the largest positive
re-excursion in bits; the last offset at which the margin is positive; and the
same margin recomputed with REAL m = n / C_0 (no ceiling) to separate the
ceiling saw-tooth from any genuine T4-driven re-crossing."""
import json
from math import ceil, exp, lgamma, log, log2
import math

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
_d = {}


def deficit(c0):  # same as own_n4b.py (inlined to avoid re-running that script on import)
    if c0 in _d:
        return _d[c0]
    t = 2 ** c0
    if t > 131072:
        _d[c0] = 1.0 / (2 * t * log(2))
        return _d[c0]
    p0 = exp(-t * log(2))
    acc = sum(exp(lgamma(t + 1) - lgamma(j + 1) - lgamma(t - j + 1) - t * log(2)) * log2(2 * j)
              for j in range(1, t + 1))
    _d[c0] = c0 - acc / (1 - p0)
    return _d[c0]


def lchoose2(a, b):
    return (lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)) / log(2)


def log2W(n):
    return log2(0.886) + n / 2.0


def vow(n, metric):
    if metric == "time_only":
        return log2W(n)
    if metric == "equal_rate_max":
        return 0.5 * (log2(6.0 * n) + log2W(n))
    return log2(6.0 * n) + log2W(n)


def margin_m(n, m, omega, c0, reading, metric, memr, d_F=4):
    """Margin with m supplied explicitly (integer or real)."""
    N = n * (m - 1)
    t1 = d_F * log2(N) if reading == "nagao_loose_N_to_the_d" else lchoose2(N + d_F, d_F)
    t3 = log2(m * 2 ** c0 + 1)
    log2lam = m * c0 - n - m * deficit(c0)
    lam = 2.0 ** log2lam if log2lam < 500 else float("inf")
    t4 = 0.0 if lam == float("inf") else -log2(-math.expm1(-lam))
    t5 = lchoose2(N + 4, 4) * (1 if memr == "frozen_width_C_N_plus_4_4" else 2)
    t6 = omega * t3
    dec = omega * t1 + t3 + t4
    time = dec + log2(1 + 2 ** (t6 - dec)) if t6 - dec > -1000 else dec
    nag = {"time_only": time, "time_memory_product": time + t5,
           "area_time_AT": time + t5, "equal_rate_max": max(time, t5)}[metric]
    return nag - vow(n, metric)


cs = json.load(open(RUN + "cost-surface.json"))
surf = cs["crossover_surface"]
nm = [e for e in surf if e.get("monotone_for_200_beyond") is False]
rows = []
for e in nm:
    n0 = e["crossover_n"]
    args = (e["omega"], e["C_0"], e["monomial_count_reading"], e["metric"], e["memory_reading"])
    ceil_m = [margin_m(n0 + d, ceil((n0 + d) / e["C_0"]), *args) for d in range(0, 201)]
    real_m = [margin_m(n0 + d, (n0 + d) / e["C_0"], *args) for d in range(0, 201)]
    pos = [d for d in range(1, 201) if ceil_m[d] > 0]
    # real m: find ITS OWN first negative offset, then look for a positive AFTER it
    d_neg = next((d for d in range(0, 201) if real_m[d] < 0), None)
    pos_real = [] if d_neg is None else [d for d in range(d_neg + 1, 201) if real_m[d] > 0]
    rows.append(dict(
        omega=e["omega"], C_0=e["C_0"], reading=e["monomial_count_reading"][:8],
        metric=e["metric"], memr=e["memory_reading"][:6], crossover_n=n0,
        margin_at_crossover=ceil_m[0],
        n_positive_offsets_ceil_m=len(pos), last_positive_offset_ceil_m=max(pos) if pos else None,
        max_positive_reexcursion_bits_ceil_m=max([ceil_m[d] for d in pos], default=None),
        n_positive_offsets_real_m_after_its_own_crossing=len(pos_real),
        real_m_margin_at_crossover=real_m[0],
        real_m_first_negative_offset=d_neg,
        # the saw-tooth mechanism: yield slack m*C_0 - n oscillates in [0, C_0) under the ceiling
        slack_at_crossover=ceil((n0) / e["C_0"]) * e["C_0"] - n0))

from collections import Counter

# ---- the JSON's `monotone_for_200_beyond` flag, recomputed for ALL 512 entries ----
# (own_monotone.json was produced earlier in this attempt by an inline one-off whose
#  script was not preserved; this re-does that full check under a preserved script.)
flag_rows, flag_disagreements = [], []
for e in surf:
    n0 = e["crossover_n"]
    if n0 is None:
        continue
    args = (e["omega"], e["C_0"], e["monomial_count_reading"], e["metric"], e["memory_reading"])
    mine_monotone = all(margin_m(n0 + d, ceil((n0 + d) / e["C_0"]), *args) < 0 for d in range(1, 201))
    flag_rows.append(mine_monotone)
    if mine_monotone != bool(e["monotone_for_200_beyond"]):
        flag_disagreements.append(dict(omega=e["omega"], C_0=e["C_0"], reading=e["monomial_count_reading"],
                                       metric=e["metric"], memr=e["memory_reading"], crossover_n=n0,
                                       json=e["monotone_for_200_beyond"], mine=mine_monotone))
print(f"monotone_for_200_beyond recomputed for {len(flag_rows)} entries: "
      f"my monotone={sum(flag_rows)}, my non-monotone={len(flag_rows) - sum(flag_rows)}; "
      f"disagreements with JSON: {len(flag_disagreements)}")

out = dict(
    monotone_flag_full_check=dict(entries=len(flag_rows), my_monotone=sum(flag_rows),
                                  my_non_monotone=len(flag_rows) - sum(flag_rows),
                                  disagreements=flag_disagreements),
    flagged=len(nm),
    by_C0=dict(Counter(r["C_0"] for r in rows)),
    last_positive_offset_distribution=dict(Counter(r["last_positive_offset_ceil_m"] for r in rows)),
    max_reexcursion_bits_overall=max(r["max_positive_reexcursion_bits_ceil_m"] for r in rows),
    max_reexcursion_by_C0={c: max(r["max_positive_reexcursion_bits_ceil_m"] for r in rows if r["C_0"] == c)
                           for c in sorted(set(r["C_0"] for r in rows))},
    max_last_offset_by_C0={c: max(r["last_positive_offset_ceil_m"] for r in rows if r["C_0"] == c)
                           for c in sorted(set(r["C_0"] for r in rows))},
    entries_still_reexcursing_under_real_m=sum(1 for r in rows if r["n_positive_offsets_real_m_after_its_own_crossing"] > 0),
    real_m_crossing_offset_distribution=dict(Counter(r["real_m_first_negative_offset"] for r in rows)),
    rows=rows)
print(f"flagged non-monotone entries: {len(nm)}; by C_0: {out['by_C0']}")
print(f"largest positive re-excursion after the crossover (ceil m): {out['max_reexcursion_bits_overall']:.4f} bits")
print(f"  by C_0: {{ {', '.join(f'{c}: {v:.4f}' for c, v in out['max_reexcursion_by_C0'].items())} }}")
print(f"last offset at which margin > 0, by C_0 (max): {out['max_last_offset_by_C0']}")
print(f"distribution of last positive offset: {out['last_positive_offset_distribution']}")
print(f"entries whose margin re-excurses positive AFTER ITS OWN CROSSING under REAL m = n/C_0 (no ceiling): "
      f"{out['entries_still_reexcursing_under_real_m']} / {len(nm)}")
print(f"real-m first-negative offset (relative to the ceil-m crossover) distribution: "
      f"{out['real_m_crossing_offset_distribution']}")
worst = max(rows, key=lambda r: r["max_positive_reexcursion_bits_ceil_m"])
print("worst re-excursion entry:", {k: v for k, v in worst.items()})
# a couple of C_0 = 3 and 4 entries for the report
for c in (3, 4, 6, 8, 12):
    ex = [r for r in rows if r["C_0"] == c][:2]
    for r in ex:
        print(f"  C_0={c} ω={r['omega']} {r['metric']}|{r['memr']} [{r['reading']}] x={r['crossover_n']} "
              f"m(x)={r['margin_at_crossover']:+.4f}  positives={r['n_positive_offsets_ceil_m']} "
              f"last={r['last_positive_offset_ceil_m']} maxpos={r['max_positive_reexcursion_bits_ceil_m']:+.4f}  "
              f"real-m re-excursions={r['n_positive_offsets_real_m_after_its_own_crossing']} real-m first neg offset={r['real_m_first_negative_offset']}")
json.dump(out, open("own_n4c.json", "w"), indent=1, default=str)
print("wrote own_n4c.json")
