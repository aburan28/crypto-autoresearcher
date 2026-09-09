#!/usr/bin/env python3
"""TASK-20260909-9e06b1 PHASE 2 comparison (v2).

Reads ONLY the two declared comparison-envelope paths:
  experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json
  experiments/EXP-ECRANK-73275e/execution-report-v2.yaml
and compares against the frozen phase-1 derivation (scratch/q1_dump.json).
Exact rational arithmetic; implied exponents via decimal prec=50.
Arithmetic agreement only; no interpretation.
"""
import json
from fractions import Fraction as F
from decimal import Decimal, getcontext, ROUND_HALF_EVEN

getcontext().prec = 50
getcontext().rounding = ROUND_HALF_EVEN

BASE = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
RAW = f"{BASE}/experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json"
DUMP = f"{BASE}/coordination/goals/GOAL-ECRANK-002/batches/BATCH-2f2b56/reviews/TASK-20260909-9e06b1/scratch/q1_dump.json"

def fr(s):
    return F(s)

def fmt(q):
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"

def log10_dec(r):
    """log10 of a positive Fraction at 50-digit precision (decimal, correctly rounded)."""
    return (Decimal(r.numerator) / Decimal(r.denominator)).log10()

def main():
    raw = json.load(open(RAW))
    derived = json.load(open(DUMP))

    def rkey(r):
        return tuple(fr(x) for x in r)
    derived_by_b = {}
    for pair in derived:
        bi = pair["b_index"]
        for root in pair["roots"]:
            derived_by_b.setdefault(bi, []).append(root)

    found = raw["found"]
    target = {649, 1299, 4995}
    recorded = [e for e in found if e["b_index"] in target]

    print("=" * 72)
    print("Q1: per-recorded-entry comparison")
    print("=" * 72)
    print(f"recorded entries at target b_indices: {len(recorded)}")
    print(f"derived nondegeneracy-passing roots at target b_indices: "
          f"{sum(len(v) for v in derived_by_b.values())}")

    xtab = raw["n2r"]["reconciliation"]["cross_tabulation"]
    xtab_by_b = {}
    for row in xtab:
        if row["b_index"] in target:
            xtab_by_b.setdefault(row["b_index"], []).append(row)

    all_r_match = True
    all_rh_match = True
    all_hA_match = True
    all_hB_match = True
    all_s_match = True
    all_deg_match = True
    disc_match_flags = []

    for e in recorded:
        bi = e["b_index"]
        inst = e["instance"]
        rec_r = [fr(x) for x in inst["r"]]
        rec_rh = inst["r_height"]
        rec_s = [fr(x) for x in inst["s"]]
        rec_disc = fr(inst["disc_s"])
        rec_deg = inst["deg_s"]
        match = None
        for root in derived_by_b.get(bi, []):
            if [fr(x) for x in root["r_vector"]] == rec_r:
                match = root
                break
        print(f"\n--- b_index {bi} ---")
        if match is None:
            print(f"  recorded r={rec_r} r_height={rec_rh}")
            print("  MATCH: NONE (no derived root with this r vector)")
            all_r_match = False
            continue
        my_r = [fr(x) for x in match["r_vector"]]
        my_hA = match["h_A"]; my_hB = match["h_B"]
        my_s = [fr(x) for x in match["s_at_c_coefficients_ascending"]]
        my_disc = fr(match["disc_s"]); my_deg = match["deg_s"]
        r_ok = my_r == rec_r
        rh_ok = my_hA == rec_rh
        s_ok = my_s == rec_s
        deg_ok = my_deg == rec_deg
        disc_ok = my_disc == rec_disc
        all_r_match &= r_ok; all_rh_match &= rh_ok
        all_s_match &= s_ok; all_deg_match &= deg_ok
        disc_match_flags.append(disc_ok)
        print(f"  derived c={match['c']} (num {match['numerator']}, den {match['denominator']})")
        print(f"  r:        derived={my_r}")
        print(f"             recorded={rec_r}   MATCH={r_ok}")
        print(f"  r_height: derived h_A={my_hA}  recorded={rec_rh}  MATCH={rh_ok}")
        print(f"  s:        MATCH={s_ok}")
        if not s_ok:
            print(f"             derived ={my_s}")
            print(f"             recorded={rec_s}")
        print(f"  deg_s:    derived={my_deg} recorded={rec_deg} MATCH={deg_ok}")
        print(f"  disc_s:   derived ={fmt(my_disc)}")
        print(f"             recorded={fmt(rec_disc)}  MATCH={disc_ok}")
        if not disc_ok:
            print(f"             ratio recorded/derived = {fmt(rec_disc / my_disc)}")
        # cross_tabulation row
        rows = xtab_by_b.get(bi, [])
        row_ok = False
        for row in rows:
            if row["h_A"] == my_hA and row["h_B"] == my_hB:
                hA_ok = row["h_A"] == my_hA
                hB_ok = row["h_B"] == my_hB
                all_hA_match &= hA_ok; all_hB_match &= hB_ok
                row_ok = True
                print(f"  xtab row: h_A={row['h_A']} (MATCH={hA_ok})  h_B={row['h_B']} (MATCH={hB_ok})  "
                      f"lvlA={row['membership_level_A']} lvlB={row['membership_level_B']}")
                print(f"             my h_A<=10000={my_hA <= 10000}  my h_B<=10000={my_hB <= 10000}")
                break
        if not row_ok:
            all_hA_match = False; all_hB_match = False
            print(f"  xtab row: NO row with (h_A={my_hA}, h_B={my_hB}); rows present={rows}")
        print(f"  derived per-threshold membership: {match['membership']}")

    print("\n--- Q1 summary ---")
    print(f"all r vectors match:        {all_r_match}")
    print(f"all r_height (h_A) match:   {all_rh_match}")
    print(f"all s polynomials match:    {all_s_match}")
    print(f"all deg_s match:            {all_deg_match}")
    print(f"all disc_s match:           {all(disc_match_flags)}  (per-entry: {disc_match_flags})")
    print(f"all xtab h_A match:         {all_hA_match}")
    print(f"all xtab h_B match:         {all_hB_match}")
    rec_keys = sorted(rkey(e["instance"]["r"]) for e in recorded)
    der_keys = sorted(rkey(r["r_vector"]) for bi in target for r in derived_by_b.get(bi, []))
    print(f"one-to-one r-multiset:      {rec_keys == der_keys}  (rec={len(rec_keys)}, der={len(der_keys)})")

    # ============================ Q2 ============================
    print("\n" + "=" * 72)
    print("Q2: decade-ratio comparison")
    print("=" * 72)
    recon = raw["n2r"]["reconciliation"]
    convA = recon["N_per_H_convention_A"]
    convB = recon["N_per_H_convention_B"]

    def analyze(name, N):
        a = F(N["100"]); b = F(N["1000"]); c = F(N["10000"])
        R1 = b / a; R2 = c / b; tot = c / a
        t1 = b < F(100) * a
        t2 = c < F(100) * b
        t3 = c < F(10000) * a
        k1 = log10_dec(R1); k2 = log10_dec(R2); kt = log10_dec(tot)
        print(f"\n--- convention {name}: a={a} b={b} c={c} ---")
        print(f"  R1=b/a={fmt(R1)}  R2=c/b={fmt(R2)}  total=c/a={fmt(tot)}")
        print(f"  b/a<100 (b<100a={100*a}): {t1}")
        print(f"  c/b<100 (c<100b={100*b}): {t2}")
        print(f"  c/a<10000 (c<10000a={10000*a}): {t3}")
        print(f"  k1=log10(R1)={k1}")
        print(f"  k2=log10(R2)={k2}")
        print(f"  kt=log10(total)={kt}")
        return dict(a=a, b=b, c=c, R1=R1, R2=R2, tot=tot, k1=k1, k2=k2, kt=kt,
                    t1=t1, t2=t2, t3=t3)

    A = analyze("A", convA)
    B = analyze("B", convB)

    # recorded blocks (from execution-report-v2.yaml, read directly as JSON doubles)
    # We re-read the yaml values as the exact doubles the producer recorded.
    # The raw-result.json decade_ratios block carries the same numbers with exact N_from/N_to.
    dr = recon["decade_ratios"]
    print("\n--- compare vs raw-result.json n2r.decade_ratios (exact N_from/N_to + recorded doubles) ---")
    for cname, mine in [("convention_A", A), ("convention_B", B)]:
        blk = dr[cname]
        print(f"\n  {cname}:")
        my_ratios = [mine["R1"], mine["R2"]]
        for i, d in enumerate(blk["decade_ratios"]):
            exact = F(d["N_to"]) / F(d["N_from"])
            rec_double = d["ratio"]  # JSON double
            my_double = float(my_ratios[i])
            agree = (my_double == rec_double)
            print(f"    ratio[{i}] {d['from_H']}->{d['to_H']}: N_from={d['N_from']} N_to={d['N_to']}")
            print(f"       my exact={fmt(exact)}  my double={my_double!r}  recorded double={rec_double!r}  AGREE={agree}")
        my_smallest = min(mine["R1"], mine["R2"]); my_largest = max(mine["R1"], mine["R2"])
        for label, mv in [("smallest", my_smallest), ("largest", my_largest),
                          ("two_decade_total", mine["tot"])]:
            rec_key = {"smallest": "smallest_ratio", "largest": "largest_ratio",
                       "two_decade_total": "two_decade_total_ratio"}[label]
            rec_double = blk[rec_key]
            my_double = float(mv)
            agree = (my_double == rec_double)
            print(f"    {label}: my exact={fmt(mv)}  my double={my_double!r}  "
                  f"recorded double={rec_double!r}  AGREE={agree}")

    # also compare vs execution-report-v2.yaml quoted blocks (transcribed exact decimals)
    print("\n--- compare vs execution-report-v2.yaml n2r_decade_ratios blocks ---")
    recA = dict(ratios=[1.4, 1.1785714285714286], smallest=1.1785714285714286,
                largest=1.4, two_decade_total=1.65)
    recB = dict(ratios=[1.2692307692307692, 1.0], smallest=1.0,
                largest=1.2692307692307692, two_decade_total=1.2692307692307692)
    for name, mine, rec in [("A", A, recA), ("B", B, recB)]:
        print(f"\n  convention {name}:")
        for i, rk in enumerate(rec["ratios"]):
            mv = [mine["R1"], mine["R2"]][i]
            print(f"    ratio[{i}]: my exact={fmt(mv)} my double={float(mv)!r} recorded={rk!r} AGREE={float(mv)==rk}")
        for label, mv in [("smallest", min(mine["R1"], mine["R2"])),
                          ("largest", max(mine["R1"], mine["R2"])),
                          ("two_decade_total", mine["tot"])]:
            print(f"    {label}: my exact={fmt(mv)} my double={float(mv)!r} recorded={rec[label]!r} AGREE={float(mv)==rec[label]}")

if __name__ == "__main__":
    main()
