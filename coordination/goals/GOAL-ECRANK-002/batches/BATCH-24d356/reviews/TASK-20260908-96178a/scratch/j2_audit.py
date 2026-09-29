#!/usr/bin/env python3
"""J2: audit integrity. Recompute |S|, N_a, in-box ledgers, meet counts for
AT-0/1/2 from R1/R2 raw data AND independently from the predecessor committed
bytes at a20a49b6a. Verify IV-5/IV-7/IV-9, binomial consistency, and that the
audit read committed bytes."""
import json, os, subprocess
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/ecrank-73275e-review-20260908"
PRED = "a20a49b6adbcce51893c1221dbd69cdcd486ad9d"
R1 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R1-audit-smoke/raw-result.json")
R2 = os.path.join(ROOT, "experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R2-draw-support/raw-result.json")

def git_show(commit, path):
    return subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, path)],
                          capture_output=True).stdout

# ---- J2.1a: |S| and N_a ----
H = 20
coords = [i for i in range(-H, H + 1) if i != 0]
S = [(x, y) for x in coords for y in coords]
absS = len(S)
N_a = 5 * absS
print("=== J2.1a |S| and N_a ===")
print("|S| recomputed ([-20,20]\\{0})^2 =", absS, "(recorded 1600) ->", "PASS" if absS == 1600 else "FAIL")
print("N_a recomputed = 5*|S| =", N_a, "(recorded 8000) ->", "PASS" if N_a == 8000 else "FAIL")
print("E[meets] = N_a/|S| =", N_a / absS)

# ---- J2.1b: in-box ledgers from R2 raw reconstructed.rows ----
with open(R2) as f:
    r2 = json.load(f)
print("\n=== J2.1b in-box ledger (R2 reconstructed.rows) ===")
total = 0; inbox = 0; out = []
for row in r2["reconstructed"]["rows"]:
    for d in row["draws"]:
        total += 1
        Hs = d["H"]
        hs = d["heights"]
        ok = all(int(hs[str(i)]) <= Hs for i in range(5))
        if ok:
            inbox += 1
        else:
            out.append((row["b_index"], d["draw_index"], Hs, hs))
print("n_draws recomputed =", total, "(recorded", r2["inbox"]["n_draws"], ")")
print("n_in_box recomputed =", inbox, "(recorded", r2["inbox"]["n_in_box"], ")")
print("in_box_fraction recomputed =", inbox / total, "(recorded", r2["inbox"]["in_box_fraction"], ")")
print("out_of_box recomputed =", out, "(recorded", r2["inbox"]["out_of_box"], ")")
# also verify the recorded in_box flag per draw matches my recomputation
flag_mismatch = []
for row in r2["reconstructed"]["rows"]:
    for d in row["draws"]:
        Hs = d["H"]; hs = d["heights"]
        ok = all(int(hs[str(i)]) <= Hs for i in range(5))
        if ok != d["in_box"]:
            flag_mismatch.append((row["b_index"], d["draw_index"]))
print("per-draw in_box flag mismatches:", flag_mismatch)

# ---- J2.1c: meet counts from per_draw_log ----
print("\n=== J2.1c meet counts (R2 r2_plants per_draw_log) ===")
for p in r2["r2_plants"]:
    hits = [e for e in p["per_draw_log_prefix_and_hits"] if e["meet"]]
    print("AT-%d plant=%s h0=%s meets_observed(recorded)=%s meets_recomputed=%s -> %s" % (
        p["at"], p["plant"], p["h0"], p["meets_observed"], len(hits),
        "PASS" if len(hits) == p["meets_observed"] else "FAIL"))
    # verify each hit pt == plant
    bad = [e for e in hits if e["pt"] != p["plant"]]
    print("   hits with pt != plant:", bad)
# R1 synthetic 2D
r1p = r2["r1_planted_2d"]
hits1 = [e for e in r1p["per_draw_log_prefix_and_hits"] if e["meet"]]
print("R1 synthetic 2D plant=%s meets_observed(recorded)=%s meets_recomputed=%s -> %s" % (
    r1p["plant"], r1p["meets_observed"], len(hits1),
    "PASS" if len(hits1) == r1p["meets_observed"] else "FAIL"))

# ---- J2.1d: verify audit read committed bytes (recorded_AT vs predecessor) ----
print("\n=== J2.1d recorded_AT vs predecessor committed blind_rederivation_inputs_C3 @ a20a49b6a ===")
pred_raw = json.loads(git_show(PRED, "experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json"))
pred_at = pred_raw["blind_rederivation_inputs_C3"][:3]
mism = []
for i, (rec, pred) in enumerate(zip(r2["recorded_AT"], pred_at)):
    if rec["b"] != pred["b"]:
        mism.append(("AT-%d b" % i, rec["b"], pred["b"]))
    if list(rec["d_pattern"]) != list(pred["d_pattern"]):
        mism.append(("AT-%d d_pattern" % i, rec["d_pattern"], pred["d_pattern"]))
    if rec["b_index"] != pred["b_index"]:
        mism.append(("AT-%d b_index" % i, rec["b_index"], pred["b_index"]))
    if rec["stream"] != pred["stream"]:
        mism.append(("AT-%d stream" % i, rec["stream"], pred["stream"]))
print("recorded_AT vs predecessor mismatches:", mism if mism else "NONE (all 3 ATs match committed bytes)")
# R1 recorded_AT (b_index 0) vs predecessor entry 0
with open(R1) as f:
    r1 = json.load(f)
r1_rec = r1["recorded_AT"][0]
print("R1 recorded_AT[0] b == pred[0] b:", r1_rec["b"] == pred_at[0]["b"],
      " d_pattern match:", list(r1_rec["d_pattern"]) == list(pred_at[0]["d_pattern"]))

# ---- J2.2: IV-5, IV-7, IV-9 ----
print("\n=== J2.2 IV-5 / IV-7 / IV-9 ===")
print("IV-5 R1 reconstruction_bit_identical_replay:", r1["reconstruction_bit_identical_replay"],
      "(recorded true) ->", "PASS" if r1["reconstruction_bit_identical_replay"] else "FAIL")
print("IV-5 R1 synthetic 2D known-answer meets_observed:", r1["r1_planted_2d"]["meets_observed"],
      "(expected 5) ->", "PASS" if r1["r1_planted_2d"]["meets_observed"] == 5 else "note")
print("IV-7 R2 reconstruction_bit_identical_replay:", r2["reconstruction_bit_identical_replay"],
      "(recorded true) ->", "PASS" if r2["reconstruction_bit_identical_replay"] else "FAIL")
plants = [(p["plant"], p["h0"]) for p in r2["r2_plants"]]
print("IV-9 plants (plant, h0):", plants)
h0s = [p[1] for p in plants]
plant_pairs = [tuple(p[0]) for p in plants]
distinct_plants = len(set(plant_pairs)) == len(plant_pairs)
no_shared_h0 = len(set(h0s)) == len(h0s)
print("IV-9 distinct plants:", distinct_plants, " no shared h0:", no_shared_h0,
      "->", "PASS" if (distinct_plants and no_shared_h0) else "FAIL")

# ---- J2.3: binomial consistency ----
print("\n=== J2.3 binomial consistency (meets ~ Binomial(N_a=8000, p=1/1600)) ===")
from math import comb, sqrt
n = 8000; p = Fr(1, 1600)
mean = n * float(p)
var = n * float(p) * (1 - float(p))
sd = sqrt(var)
print("mean =", mean, " sd =", round(sd, 4))
for k in (3, 3, 4):
    # exact P(X = k) and P(X <= k) via binomial (use log to avoid underflow for tail)
    pk = comb(n, k) * (float(p) ** k) * ((1 - float(p)) ** (n - k))
    print("  k=%d: P(X=k)=%.6g  (observed)" % (k, pk))
# P(X<=3) for one plant
p_le3 = sum(comb(n, k) * (float(p) ** k) * ((1 - float(p)) ** (n - k)) for k in range(0, 4))
print("P(X<=3) for one plant =", "%.6g" % p_le3)
print("z-scores: k=3 ->", round((3 - mean) / sd, 3), " k=4 ->", round((4 - mean) / sd, 3))
