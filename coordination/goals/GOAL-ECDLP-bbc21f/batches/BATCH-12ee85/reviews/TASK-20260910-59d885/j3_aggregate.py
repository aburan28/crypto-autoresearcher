"""J3 (TASK-20260910-59d885) aggregation for the proves-too-much pass.

Reads:
  - experiments/EXP-ECDLP-6ac801/runs/RUN-ECDLP-6ac801-v3-n*/summary.json  (Stage B'', 200 cells)
  - coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98/{summary.json,cells.jsonl} (Stage A'')
  - coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/TASK-20260910-19bd7b/results.json (J1 frozen)

No files are written. Every printed number is traceable to one of these files.
"""
import json
import glob
from collections import defaultdict

BASE = "/Volumes/SSD990/llm/tmp/opencode/ecdlp-20260910"
A_PATH = BASE + "/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98"
J1_PATH = BASE + "/coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-12ee85/reviews/TASK-20260910-19bd7b"


def f(s):
    num, den = s.split("/")
    return int(num) / int(den)


# ---------------------------------------------------------------- Stage B''
prod = {}
param_check = defaultdict(set)
margin_id = []
acct_fail = []
rf_mismatch = []
selfcheck_fail = defaultdict(int)
for path in sorted(glob.glob(BASE + "/experiments/EXP-ECDLP-6ac801/runs/RUN-ECDLP-6ac801-v3-n*/summary.json")):
    d = json.load(open(path))
    p = d["params"]
    for _key, c in d["cells"].items():
        prod[(c["N"], c["a"], c["seed"])] = c
        param_check[(c["N"])].add(
            (c["T"], c["T_sel"], c["T4"], c["T8"], c["r"], p["kind"])
        )
        r = c["margin"] - (c["exact_top_T_sel_share"] - c["static_T_r2_exact_coverage"])
        margin_id.append(abs(r))
        if c["basin_mass_accounting_sum"] != c["N"]:
            acct_fail.append((c["N"], c["a"], c["seed"]))
        if c["residual_fraction"] != (c["cycle_mass"] + c["capped_mass"]) / c["N"]:
            rf_mismatch.append((c["N"], c["a"], c["seed"]))
        for k in ("self_check_o1_basin_mass_accounting", "self_check_o2_exact_coverage_nesting", "self_check_o3_margin_nesting"):
            if c[k] != "SATISFIED":
                selfcheck_fail[k] += 1

pagg = defaultdict(list)
for (N, a, s), c in prod.items():
    pagg[(N, a)].append(c["margin"])

print("=== STAGE B'' (production, %d cells) ===" % len(prod))
print("params (T, T_sel, T4, T8, r, kind) per N:", {k: sorted(v) for k, v in sorted(param_check.items())})
print("margin identity margin == top_Tsel - static_cov: max|residual| =", max(margin_id),
      "| exact-zero cells:", sum(1 for r in margin_id if r == 0), "/", len(margin_id))
print("accounting sum != N:", acct_fail)
print("residual_fraction != (cycle+capped)/N:", rf_mismatch)
print("self-check failures:", dict(selfcheck_fail))
print("per (N,a):  mean margin / k_geq0 / min / max")
for (N, a) in sorted(pagg, key=lambda t: (t[0], t[1])):
    ms = pagg[(N, a)]
    print("  N=%d a=%s mean=%r k_geq0=%d/25 min=%r max=%r"
          % (N, a, sum(ms) / len(ms), sum(1 for m in ms if m >= 0), min(ms), max(ms)))

# ---------------------------------------------------------------- Stage A''
A_sum = json.load(open(A_PATH + "/summary.json"))
A_cells = [json.loads(line) for line in open(A_PATH + "/cells.jsonl")]
print("\n=== STAGE A'' (summary.json, %d (N,a) summaries; %d cells) ===" % (len(A_sum["summaries"]), len(A_cells)))
aagg = defaultdict(list)
for c in A_cells:
    aagg[(c["N"], (c["a_num"], c["a_den"]))].append(c)
for s in A_sum["summaries"]:
    key = (s["N"], (s["a_num"], s["a_den"]))
    cs = aagg[key]
    mk = [c["margin"] for c in cs]
    k25_re = sum(1 for m in mk if m >= 0)
    k5_re = sum(1 for m in mk[:5] if m >= 0)
    mean_re = sum(mk) / len(mk)
    match = (k25_re == s["k_25"] and k5_re == s["k_5"]
             and abs(mean_re - s["mean_margin"]) < 1e-12
             and sum(1 for c in cs if c["accounting_identity_holds"] is not True) == 0)
    print("  N=%d a=%s/%s: summary k_25=%s verdict=%s mean=%r ci=[%r,%r] straddles=%s"
          % (s["N"], s["a_num"], s["a_den"], s["k_25"], s["verdict_25"], s["mean_margin"],
             s["ci_lo"], s["ci_hi"], s["ci_straddles_zero"]))
    print("      recomputed-from-cells.jsonl: k_25=%d k_5=%d mean=%r | consistent_with_summary=%s"
          % (k25_re, k5_re, mean_re, match))
    print("      per-cell margins: min=%r max=%r" % (min(mk), max(mk)))

# ---------------------------------------------------------------- J1 frozen cells
j1 = json.load(open(J1_PATH + "/results.json"))
frozen = [(1048576, "1/8", 1), (1048576, "1/8", 7), (1048576, "1/8", 13),
          (16777216, "1/8", 3), (16777216, "1/8", 11), (16777216, "1/8", 25),
          (1048576, "1/16", 5), (16777216, "1/16", 17)]
j1c = {(c["params"]["N"], c["params"]["a"], c["params"]["seed"]): c for c in j1["frozen_cells"]}
print("\n=== FROZEN-CELL TRIANGULATION (J1 vs Stage A'' vs Stage B'') ===")
for (N, a, seed) in frozen:
    J = j1c[(N, a, seed)]
    A = next(c for c in A_cells if c["N"] == N and (c["a_num"], c["a_den"]) == {
        "1/8": (1, 8), "1/16": (1, 16)}[a] and c["seed"] == seed)
    P = prod.get((N, f(a), seed))
    print("-- (N=%d, a=%s, seed=%d)" % (N, a, seed))
    # partition-level fields (key-exact, implementation-independent given shared K/K_dp)
    j_sh = f(J["shares"]["share_top_Tsel"]["__fraction__"])
    a_sh = A["share_top_Tsel"]
    p_sh = P["exact_top_T_sel_share"] if P else None
    print("   share_top_Tsel:   J1=%s  A''=%.17g  B''=%s" % (J["shares"]["share_top_Tsel"]["__fraction__"], a_sh, p_sh))
    print("     agree J1==A'':%s  J1==B'':%s" % (abs(j_sh - a_sh) < 1e-18,
                                                  p_sh is not None and abs(j_sh - p_sh) < 1e-18))
    print("   n_dps:            J1=%s  A''=%s" % (J["partition"]["n_dps"], A["n_dps"]))
    print("   cycle_mass:       J1=%s  A''=%s  B''=%s" % (J["partition"]["cycle_mass"], A["cycle_mass"], P["cycle_mass"] if P else None))
    print("   capped_mass:      J1=%s  A''=%s  B''=%s" % (J["partition"]["capped_mass"], A["capped_mass"], P["capped_mass"] if P else None))
    print("   residual_fraction J1=%s  A''=%.17g  B''=%s" % (J["partition"]["residual_fraction"]["__fraction__"], A["residual_fraction"], P["residual_fraction"] if P else None))
    # pool-dependent fields
    j_m = f(J["margin"]["__fraction__"])
    print("   margin:           J1=%s  A''=%.17g  B''=%.17g" % (J["margin"]["__fraction__"], A["margin"], P["margin"] if P else 0))
    print("     signs: J1=%s A''=%s B''=%s" % (J["margin_sign"], "+" if A["margin"] >= 0 else "-", P["margin_geq_0"] if P else None))
    print("   cov/cov_static:   J1=%s  A''=%.17g  B''=%.17g" % (J["cov_static"]["__fraction__"], A["cov_static"], P["static_T_r2_exact_coverage"] if P else 0))
    print("   rho_ORACLE:       J1=%s  A''=%.17g  B''=%s" % (J["rho_ORACLE"]["__fraction__"], A["rho_ORACLE"], P["rho_oracle"] if P else None))
    print("   capped_walks:     J1=%s  A''=%s  B''=%s" % (J["pool"]["capped_walks"], A["capped_walks"], P["capped_walks"] if P else None))
    print("   ties at T-th wt:  J1=%s  A''=%s  B''=%s" % (J["pool"]["n_tied_at_Tth_weight"], A["n_tied_at_Tth_weight"], P["tie_count_at_T_th_weight"] if P else None))

# ---------------------------------------------------------------- a=1/8 per-seed sign pattern
print("\n=== a=1/8 per-seed margin signs, seeds 1..25 ===")
for N in (1048576, 16777216):
    rowA = "".join("+ " if next(c for c in A_cells if c["N"] == N and c["a_den"] == 8 and c["a_num"] == 1 and c["seed"] == s)["margin"] >= 0 else "- "
                   for s in range(1, 26))
    rowB = "".join("+ " if prod[(N, 0.125, s)]["margin"] >= 0 else "- " for s in range(1, 26))
    kA = sum(1 for s in range(1, 26) if next(c for c in A_cells if c["N"] == N and c["a_den"] == 8 and c["a_num"] == 1 and c["seed"] == s)["margin"] >= 0)
    kB = sum(1 for s in range(1, 26) if prod[(N, 0.125, s)]["margin"] >= 0)
    print("  N=%d A'': %s (k=%d/25)" % (N, rowA, kA))
    print("  N=%d B'': %s (k=%d/25)" % (N, rowB, kB))

# a=1/16 and a=3/16, a=1/4 sign patterns (context for object 4)
print("\n=== sign patterns for other a values ===")
for (num, den, akey) in ((1, 16, 0.0625), (3, 16, 0.1875), (1, 4, 0.25)):
    for N in (1048576, 16777216):
        kA = sum(1 for s in range(1, 26) if next(c for c in A_cells if c["N"] == N and c["a_num"] == num and c["a_den"] == den and c["seed"] == s)["margin"] >= 0)
        kB = sum(1 for s in range(1, 26) if prod[(N, akey, s)]["margin"] >= 0)
        print("  N=%d a=%d/%d: A'' k_geq0=%d/25  B'' k_geq0=%d/25" % (N, num, den, kA, kB))
