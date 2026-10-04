"""J4 Part 1 (Red Team, TASK-20260906-a6b415): independent re-run of the
actual production experiments/EXP-ECDLP-612fb1/source_v2/analysis.py
run_permanent_fixture_check() against the two red-team permanent-negative
fixtures, PLUS a deliberate reproduction of the pre-fix (v1-style) None-
unguarded code to confirm the None-guard is load-bearing (i.e. these
fixtures would genuinely crash without it, not merely happen to pass)."""
import sys
import json

sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-612fb1/source_v2")
import analysis as A

print("=== Part 1a: real v2 analysis.py run_permanent_fixture_check() ===")
try:
    out = A.run_permanent_fixture_check()
    print("NO EXCEPTION RAISED.")
    for kind in ("affine_xorshift", "permutation"):
        print(kind, "-> G1_verdict =", out[kind]["G1_verdict"])
    print("both_fixtures_scored_FAIL_no_exception:", out["both_fixtures_scored_FAIL_no_exception"])
except Exception as e:
    print("EXCEPTION RAISED:", type(e).__name__, e)

print("\n=== Part 1b: raw cutoff.n_c inspection (confirms None by construction) ===")
FIX = ("/home/user/crypto-autoresearcher/coordination/goals/GOAL-ECDLP-bbc21f/batches/"
       "BATCH-289698/tasks/TASK-20260906-90e7cf/results/j4_perm")
for kind in ("affine_xorshift", "permutation"):
    for s in (1, 2, 3):
        p = f"{FIX}/{kind}/RUN-RT-90e7cf-{kind}-s{s}/summary.json"
        d = json.load(open(p))
        c = d["basins"]["cutoff"]
        print(kind, s, "n_c=", c.get("n_c"), "note=", c.get("note"))

print("\n=== Part 1c: deliberately reproduce the PRE-FIX (v1-style) None-unguarded code ===")
print("    (direct dict indexing + no is-not-None short-circuit before the range comparison)")


def compute_g1_buggy(summaries):
    per_seed = []
    for s in summaries:
        x = s["basins"]
        nc = x["cutoff"]["n_c_theta2_over_2"]  # BUGGY: no .get()
        per_seed.append({
            "n_c_theta2_over_2": nc,
            "survival_slope_log_grid": x["survival_slope"],
            "top_T_share_over_C_max": x["top_T_share_over_C_max"],
            "static_below_top_share": bool(s["fixture"]["static_T_exact_coverage"] < x["top_T_share"]),
        })
    slope_ok = all(abs(e["survival_slope_log_grid"] + 0.5) <= 0.15 for e in per_seed)
    cutoff_ok = all(0.5 <= e["n_c_theta2_over_2"] <= 2.0 for e in per_seed)  # BUGGY: no None guard
    top_ok = all(0.85 <= e["top_T_share_over_C_max"] <= 1.05 for e in per_seed)
    static_below_ok = all(e["static_below_top_share"] for e in per_seed)
    literal = bool(slope_ok and cutoff_ok and top_ok and static_below_ok)
    return {"G1_verdict": "PASS" if literal else "FAIL"}


for kind in ("affine_xorshift", "permutation"):
    summaries = [json.load(open(f"{FIX}/{kind}/RUN-RT-90e7cf-{kind}-s{s}/summary.json")) for s in (1, 2, 3)]
    try:
        r = compute_g1_buggy(summaries)
        print(kind, "-> NO EXCEPTION (unexpected!):", r)
    except Exception as e:
        print(kind, "-> EXCEPTION (confirms the None-guard is load-bearing, matching F-J4-4):",
              type(e).__name__, e)
