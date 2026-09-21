#!/usr/bin/env python3
"""TASK-20260901-5174ca VALIDATOR fresh re-derivation (blind: written from the
definitions in IDEA-20260901-026d6a.repaired_statistic / null_model / PR-1 / PR-2
and PREREGISTRATION.md sections 1-3 only; producer src/xstat.py NOT read, no
producer code reused). All arithmetic exact rational (fractions.Fraction)."""
import json, sys
from fractions import Fraction as F

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831"
B2F = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs"
B5E = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-ed281d/runs"

def load(p):
    with open(p) as f:
        return json.load(f)

def binom_pmf(n, p):
    """pmf of Bin(n, p) as dict k -> Fraction."""
    from math import comb
    q = F(1) - p
    return {k: F(comb(n, k)) * p**k * q**(n - k) for k in range(n + 1)}

def convolve(a, b):
    out = {}
    for ka, va in a.items():
        for kb, vb in b.items():
            out[ka + kb] = out.get(ka + kb, F(0)) + va * vb
    return out

def dp_sum(pmfs):
    dist = {F(0): F(1)}
    dist = {0: F(1)}
    for pmf in pmfs:
        dist = convolve(dist, pmf)
    return dist

def tail(dist, s_obs):
    p_extra = sum(v for k, v in dist.items() if k >= s_obs)
    p_deficit = sum(v for k, v in dist.items() if k <= s_obs)
    mean = sum(F(k) * v for k, v in dist.items())
    var = sum(F(k) * k * v for k, v in dist.items()) - mean * mean
    return p_extra, p_deficit, mean, var

NAIVE = F(1, 256)

def per_hit_X(h):
    """F = 4*popcount(m & 0b1110); Ze = 16 - wt_e_byte; X = Ze - F."""
    m = h["vanishing_word_mask"]
    Fforced = 4 * bin(m & 0b1110).count("1")
    Ze = 16 - h["wt_e_byte"]
    return Ze, Fforced, Ze - Fforced, m

def hit_pmf_naive(h):
    Ze, Fforced, X, m = per_hit_X(h)
    return binom_pmf(16 - Fforced, NAIVE)

def hit_pmf_empirical(h, p_diag, p_off):
    """Class partition per proposal: m&1 -> 4 diagonal bytes D0 @1/256 exact,
    12 off-diagonal O @p_off; else 4 diagonal D1 @p_diag + 8 off-diagonal O @p_off
    (W=1 single-word masks only observed; popcount(m&0b1110)==1 for all hits here)."""
    m = h["vanishing_word_mask"]
    assert h["W"] == 1 and bin(m).count("1") == 1, "multi-word hit: extend per proposal W>=2 clause"
    if m & 1:
        pmf = convolve(binom_pmf(4, NAIVE), binom_pmf(12, p_off))
    else:
        pmf = convolve(binom_pmf(4, p_diag), binom_pmf(8, p_off))
    return pmf

def analyze(receipt, hits, pmfs, label):
    S_obs = sum(per_hit_X(h)[2] for h in hits)
    dist = dp_sum(pmfs)
    p_extra, p_deficit, mean, var = tail(dist, S_obs)
    return {"label": label, "n_hits": len(hits), "S_obs": S_obs,
            "p_extra_exact": str(p_extra), "p_extra_float": float(p_extra),
            "p_deficit_exact": str(p_deficit), "p_deficit_float": float(p_deficit),
            "null_mean_exact": str(mean), "null_mean_float": float(mean),
            "null_variance_exact": str(var), "dist_support_max": max(dist)}

out = {"task_id": "TASK-20260901-5174ca", "role": "validator",
       "method": "fresh code, exact Fraction DP, definitions from IDEA-20260901-026d6a only",
       "checks": []}

def chk(name, ok, detail=""):
    out["checks"].append({"check": name, "pass": bool(ok), "detail": detail})

# ---------------- receipt internal consistency ----------------
for tag, path in [("R4", B2F + "/R4_gate0_j5.json"), ("R5", B2F + "/R5_r6_reference.json"),
                  ("G3", B5E + "/G3_gate0x.json"), ("G4", B5E + "/G4_anchor_r6.json"),
                  ("G5", B5E + "/G5_j5_2.json")]:
    r = load(path)
    counted = r["trials"] - r.get("trivial_swaps_excluded", 0)
    chk(f"{tag} whist sums to trials-trivial_excluded", sum(r["whist"]) == counted,
        f"sum={sum(r['whist'])} counted={counted}")
    chk(f"{tag} W_ge1_nontrivial == whist[1:]", r["W_ge1_nontrivial"] == sum(r["whist"][1:]))
    ea, em, eh = r["ewhist_all"], r["ewhist_miss"], r["ewhist_hit"]
    chk(f"{tag} ewhist_all == miss+hit", all(ea[i] == em[i] + eh[i] for i in range(17)))
    chk(f"{tag} ewhist sums to trials-trivial_excluded", sum(ea) == counted)
    chk(f"{tag} hit_e_detail count == W_ge1", len(r["hit_e_detail"]) == r["W_ge1_nontrivial"])
    hw = [0] * 17
    for h in r["hit_e_detail"]:
        hw[h["wt_e_byte"]] += 1
    chk(f"{tag} hit weights match ewhist_hit", hw == eh)
    if "ezdiag_all" in r:
        chk(f"{tag} ezdiag_all == miss+hit", r["ezdiag_all"] == r["ezdiag_miss"] + r["ezdiag_hit"])
        chk(f"{tag} ezoff_all == miss+hit", r["ezoff_all"] == r["ezoff_miss"] + r["ezoff_hit"])
        zsum = sum(16 - i for i in range(17)) if False else None
        zeros_miss = sum((16 - i) * em[i] for i in range(17))
        chk(f"{tag} ezdiag_miss+ezoff_miss == zeros(e) over miss",
            r["ezdiag_miss"] + r["ezoff_miss"] == zeros_miss,
            f"zeros_miss={zeros_miss}")
        zeros_hit = sum((16 - i) * eh[i] for i in range(17))
        chk(f"{tag} ezdiag_hit+ezoff_hit == zeros(e) over hit",
            r["ezdiag_hit"] + r["ezoff_hit"] == zeros_hit, f"zeros_hit={zeros_hit}")
    chk(f"{tag} n_miss = nontrivial - hits", r["whist"][0] == r["nontrivial_trials"] - r["W_ge1_nontrivial"],
        f"whist0={r['whist'][0]} nontrivial={r['nontrivial_trials']}")

# ---------------- zero_mask_e / word-layout cross-checks ----------------
diag = {0, 5, 10, 15}
layout = {}
# derive forced-word byte layout from X==0 hits only (their zero_mask_e == forced set)
for tag, path in [("G3", B5E + "/G3_gate0x.json"), ("G4", B5E + "/G4_anchor_r6.json"),
                  ("G5", B5E + "/G5_j5_2.json")]:
    r = load(path)
    for h in r["hit_e_detail"]:
        m, zm = h["vanishing_word_mask"], h["zero_mask_e"]
        Ze, Ff, X, _ = per_hit_X(h)
        if m != 1 and X == 0:
            bits = frozenset(i for i in range(16) if zm >> i & 1)
            if m in layout:
                assert layout[m] == bits, f"word {m} layout conflict: {layout[m]} vs {bits}"
            else:
                layout[m] = bits
for m, bits in layout.items():
    chk(f"forced word {m} set disjoint from diagonal, size 4", not (bits & diag) and len(bits) == 4,
        f"word{m}={sorted(bits)}")
for tag, path in [("G3", B5E + "/G3_gate0x.json"), ("G4", B5E + "/G4_anchor_r6.json"),
                  ("G5", B5E + "/G5_j5_2.json")]:
    r = load(path)
    for h in r["hit_e_detail"]:
        m, zm = h["vanishing_word_mask"], h["zero_mask_e"]
        bits = frozenset(i for i in range(16) if zm >> i & 1)
        chk(f"{tag} popcount(zero_mask_e) == Ze", len(bits) == 16 - h["wt_e_byte"],
            f"mask={m} zm={zm} wt={h['wt_e_byte']}")
        if m != 1:
            chk(f"{tag} forced word {m} bits subset of zero_mask_e", layout[m] <= bits,
                f"forced={sorted(layout[m])} zm={sorted(bits)}")
words_union = frozenset().union(*layout.values()) if layout else frozenset()
chk("words 1,2,3 + diagonal partition all 16 bytes",
    words_union | diag == frozenset(range(16)) and not (words_union & diag),
    f"union={sorted(words_union)}")
# X from zero_mask_e equals X from wt_e_byte (active: X=len(bits); inactive: X=len(bits)-4)
for tag, path in [("G4", B5E + "/G4_anchor_r6.json"), ("G5", B5E + "/G5_j5_2.json")]:
    r = load(path)
    okall = True
    for h in r["hit_e_detail"]:
        Ze, Ff, X, m = per_hit_X(h)
        bits = bin(h["zero_mask_e"]).count("1")
        okall &= (bits - Ff == X)
    chk(f"{tag} X_from_zero_mask_e == X for all hits", okall)

# ---------------- Stage r0 ANCHOR (committed r=6, seed 531001) ----------------
r5 = load(B2F + "/R5_r6_reference.json")
hits_r5 = r5["hit_e_detail"]
res_anchor = analyze(r5, hits_r5, [hit_pmf_naive(h) for h in hits_r5], "r0_anchor_naive_null")
out["r0_anchor"] = res_anchor
chk("r0 anchor S_obs == 0", res_anchor["S_obs"] == 0)
chk("r0 anchor p_extra == 1 exact", F(res_anchor["p_extra_exact"]) == 1)
chk("r0 anchor null mean == 11/64", res_anchor["null_mean_exact"] == "11/64")
chk("r0 anchor p_deficit == (255/256)^44",
    res_anchor["p_deficit_exact"] == str(F(255**44, 256**44)))
prod = {1: 1}
sub_in = analyze(r5, [h for h in hits_r5 if h["vanishing_word_mask"] != 1],
                 [hit_pmf_naive(h) for h in hits_r5 if h["vanishing_word_mask"] != 1], "r0_anchor_inactive")
sub_ac = analyze(r5, [h for h in hits_r5 if h["vanishing_word_mask"] == 1],
                 [hit_pmf_naive(h) for h in hits_r5 if h["vanishing_word_mask"] == 1], "r0_anchor_active")
out["r0_anchor_inactive"] = sub_in
out["r0_anchor_active"] = sub_ac
chk("r0 anchor inactive p_deficit == (255/256)^12",
    sub_in["p_deficit_exact"] == str(F(255**12, 256**12)))
chk("r0 anchor active p_deficit == (255/256)^32",
    sub_ac["p_deficit_exact"] == str(F(255**32, 256**32)))
chk("r0 ANCHOR RULE: p_extra > 0.05 -> R0-ANCHOR-PASS", res_anchor["p_extra_float"] > 0.05)

# ---------------- Stage r0 RESTATEMENT (committed seed 531001, r=5) ----------------
r4 = load(B2F + "/R4_gate0_j5.json")
hits_r4 = r4["hit_e_detail"]
res_rest = analyze(r4, hits_r4, [hit_pmf_naive(h) for h in hits_r4], "r0_restatement_naive_null")
out["r0_restatement"] = res_rest
n_miss_r4 = r4["whist"][0]
zeros_miss_r4 = sum((16 - i) * r4["ewhist_miss"][i] for i in range(17))
pooled = F(zeros_miss_r4, 16 * n_miss_r4)
out["r0_restatement_pooled_miss_zero_rate"] = {"exact": str(pooled), "float": float(pooled)}
chk("restatement S_obs == 3", res_rest["S_obs"] == 3)
chk("restatement null mean == 23/32", res_rest["null_mean_exact"] == "23/32")
hits_in = [h for h in hits_r4 if h["vanishing_word_mask"] != 1]
hits_ac = [h for h in hits_r4 if h["vanishing_word_mask"] == 1]
sub_in = analyze(r4, hits_in, [hit_pmf_naive(h) for h in hits_in], "r0_rest_inactive")
sub_ac = analyze(r4, hits_ac, [hit_pmf_naive(h) for h in hits_ac], "r0_rest_active")
out["r0_restatement_inactive"] = sub_in
out["r0_restatement_active"] = sub_ac
chk("restatement subclass split 10 inactive / 4 active", len(hits_in) == 10 and len(hits_ac) == 4)
chk("restatement active p_deficit == (255/256)^64",
    sub_ac["p_deficit_exact"] == str(F(255**64, 256**64)))

# ---------------- G4 fresh anchor (seed 531002, r=6, run-internal null) ----------------
g4 = load(B5E + "/G4_anchor_r6.json")
n_miss_g4 = g4["whist"][0]
p_diag_g4 = F(g4["ezdiag_miss"], 4 * n_miss_g4)
p_off_g4 = F(g4["ezoff_miss"], 12 * n_miss_g4)
hits_g4 = g4["hit_e_detail"]
res_g4 = analyze(g4, hits_g4, [hit_pmf_empirical(h, p_diag_g4, p_off_g4) for h in hits_g4], "G4_anchor_empirical")
out["G4"] = dict(res_g4, p_diag_exact=str(p_diag_g4), p_diag_float=float(p_diag_g4),
                 p_off_exact=str(p_off_g4), p_off_float=float(p_off_g4), n_miss=n_miss_g4)
sub_g4_in = analyze(g4, [h for h in hits_g4 if h["vanishing_word_mask"] != 1],
                    [hit_pmf_empirical(h, p_diag_g4, p_off_g4) for h in hits_g4 if h["vanishing_word_mask"] != 1],
                    "G4_inactive")
out["G4_inactive"] = sub_g4_in
chk("G4 hits == 2 (<=8 band, tripwire >=9 false)", len(hits_g4) == 2)
chk("G4 p_extra == 1 exact", F(res_g4["p_extra_exact"]) == 1)
chk("G4 anchor gate: p_extra > 0.05 AND hits <= 8", res_g4["p_extra_float"] > 0.05 and len(hits_g4) <= 8)
chk("G4 p_deficit == (1-pd)^8 (1-po)^16",
    res_g4["p_deficit_exact"] == str((1 - p_diag_g4)**8 * (1 - p_off_g4)**16))

# ---------------- G5 confirmatory (seed 531002, r=5, run-internal null) ----------------
g5 = load(B5E + "/G5_j5_2.json")
n_miss_g5 = g5["whist"][0]
p_diag_g5 = F(g5["ezdiag_miss"], 4 * n_miss_g5)
p_off_g5 = F(g5["ezoff_miss"], 12 * n_miss_g5)
hits_g5 = g5["hit_e_detail"]
res_g5 = analyze(g5, hits_g5, [hit_pmf_empirical(h, p_diag_g5, p_off_g5) for h in hits_g5], "G5_empirical")
out["G5"] = dict(res_g5, p_diag_exact=str(p_diag_g5), p_diag_float=float(p_diag_g5),
                 p_off_exact=str(p_off_g5), p_off_float=float(p_off_g5), n_miss=n_miss_g5,
                 trivial_swaps_excluded=g5["trivial_swaps_excluded"])
hits_g5_in = [h for h in hits_g5 if h["vanishing_word_mask"] != 1]
hits_g5_ac = [h for h in hits_g5 if h["vanishing_word_mask"] == 1]
sub_g5_in = analyze(g5, hits_g5_in, [hit_pmf_empirical(h, p_diag_g5, p_off_g5) for h in hits_g5_in], "G5_inactive")
sub_g5_ac = analyze(g5, hits_g5_ac, [hit_pmf_empirical(h, p_diag_g5, p_off_g5) for h in hits_g5_ac], "G5_active")
out["G5_inactive"] = sub_g5_in
out["G5_active"] = sub_g5_ac
chk("G5 hits == 19 (7 active / 12 inactive)", len(hits_g5) == 19 and len(hits_g5_ac) == 7 and len(hits_g5_in) == 12)
chk("G5 S_obs == 0", res_g5["S_obs"] == 0)
chk("G5 p_extra == 1 exact", F(res_g5["p_extra_exact"]) == 1)
chk("G5 p_deficit == (255/256)^28 (1-pd)^48 (1-po)^180",
    res_g5["p_deficit_exact"] == str(F(255, 256)**28 * (1 - p_diag_g5)**48 * (1 - p_off_g5)**180))
chk("G5 inactive p_deficit == (1-pd)^48 (1-po)^96",
    sub_g5_in["p_deficit_exact"] == str((1 - p_diag_g5)**48 * (1 - p_off_g5)**96))
chk("G5 active p_deficit == (255/256)^28 (1-po)^84",
    sub_g5_ac["p_deficit_exact"] == str(F(255, 256)**28 * (1 - p_off_g5)**84))
mean_manual = F(7 * 4, 256) + 48 * p_diag_g5 + 180 * p_off_g5
chk("G5 null mean manual formula == DP", mean_manual == F(res_g5["null_mean_exact"]))

# ---------------- compare vs producer-reported values ----------------
r0a = load(B5E + "/r0_analysis.json")
g4a = load(B5E + "/G4_anchor_analysis.json")["analysis"]
g5a = load(B5E + "/G5_analysis.json")["analysis"]
RESULTS = load(ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-ed281d/RESULTS.json")

def feq(a, b):
    """compare exact rational strings as values"""
    try:
        return F(a) == F(b)
    except Exception:
        return a == b

cmps = [
    ("r0 anchor S_obs", res_anchor["S_obs"], r0a["anchor"]["S_obs"]),
    ("r0 anchor p_extra exact", res_anchor["p_extra_exact"], r0a["anchor"]["test_all_hits"]["p_extra"]["exact"]),
    ("r0 anchor p_deficit exact", res_anchor["p_deficit_exact"], r0a["anchor"]["test_all_hits"]["p_deficit"]["exact"]),
    ("r0 anchor null mean", res_anchor["null_mean_exact"], r0a["anchor"]["test_all_hits"]["null_mean"]["exact"]),
    ("r0 anchor null var", res_anchor["null_variance_exact"], r0a["anchor"]["test_all_hits"]["null_variance"]["exact"]),
    ("r0 restatement S_obs", res_rest["S_obs"], r0a["restatement"]["S_obs"]),
    ("r0 restatement p_extra EXACT fraction", res_rest["p_extra_exact"], r0a["restatement"]["test_all_hits"]["p_extra"]["exact"]),
    ("r0 restatement p_extra float", res_rest["p_extra_float"], r0a["restatement"]["test_all_hits"]["p_extra"]["float"]),
    ("r0 restatement p_deficit float", res_rest["p_deficit_float"], r0a["restatement"]["test_all_hits"]["p_deficit"]["float"]),
    ("r0 restatement null mean", res_rest["null_mean_exact"], r0a["restatement"]["test_all_hits"]["null_mean"]["exact"]),
    ("r0 restatement null var", res_rest["null_variance_exact"], r0a["restatement"]["test_all_hits"]["null_variance"]["exact"]),
    ("r0 restatement inactive p_extra EXACT", out["r0_restatement_inactive"]["p_extra_exact"],
     r0a["restatement"]["test_inactive_subclass"]["p_extra"]["exact"]),
    ("r0 restatement inactive p_extra float", out["r0_restatement_inactive"]["p_extra_float"],
     r0a["restatement"]["test_inactive_subclass"]["p_extra"]["float"]),
    ("r0 restatement active p_extra", out["r0_restatement_active"]["p_extra_exact"],
     r0a["restatement"]["test_active_subclass"]["p_extra"]["exact"]),
    ("r0 restatement pooled miss zero rate", str(pooled), r0a["pooled_miss_zero_rate_restatement"]["exact"]),
    ("RESULTS r0 restatement p_extra float", res_rest["p_extra_float"],
     RESULTS["stage_r0"]["restatement"]["p_extra_float"]),
    ("RESULTS r0 restatement p_extra EXACT", res_rest["p_extra_exact"],
     RESULTS["exact_p_values"]["r0_restatement_p_extra"]),
    ("RESULTS r0 anchor p_extra", res_anchor["p_extra_exact"], RESULTS["exact_p_values"]["r0_anchor_p_extra"]),
    ("G4 p_diag exact", str(p_diag_g4), g4a["p_diag"]["exact"]),
    ("G4 p_off exact", str(p_off_g4), g4a["p_off"]["exact"]),
    ("G4 S_obs", res_g4["S_obs"], g4a["S_obs"]),
    ("G4 p_extra", res_g4["p_extra_exact"], g4a["test_all_hits"]["p_extra"]["exact"]),
    ("G4 p_deficit EXACT", res_g4["p_deficit_exact"], g4a["test_all_hits"]["p_deficit"]["exact"]),
    ("G4 null mean EXACT", res_g4["null_mean_exact"], g4a["test_all_hits"]["null_mean"]["exact"]),
    ("G4 null mean float", res_g4["null_mean_float"], RESULTS["stage_r1"]["decision_rule_inputs"]["g4_anchor"]["null_mean_float"]),
    ("G4 n_miss", n_miss_g4, g4a["n_miss"]),
    ("G5 p_diag exact", str(p_diag_g5), g5a["p_diag"]["exact"]),
    ("G5 p_off exact", str(p_off_g5), g5a["p_off"]["exact"]),
    ("G5 S_obs", res_g5["S_obs"], g5a["S_obs"]),
    ("G5 p_extra", res_g5["p_extra_exact"], g5a["test_all_hits"]["p_extra"]["exact"]),
    ("G5 p_deficit EXACT fraction", res_g5["p_deficit_exact"], g5a["test_all_hits"]["p_deficit"]["exact"]),
    ("G5 p_deficit float", res_g5["p_deficit_float"], g5a["test_all_hits"]["p_deficit"]["float"]),
    ("G5 null mean EXACT", res_g5["null_mean_exact"], g5a["test_all_hits"]["null_mean"]["exact"]),
    ("G5 null mean float", res_g5["null_mean_float"], RESULTS["stage_r1"]["decision_rule_inputs"]["g5_confirmatory"]["null_mean_float"]),
    ("G5 null mean RESULTS exact", res_g5["null_mean_exact"], RESULTS["exact_p_values"]["g5_null_mean"]),
    ("G5 null var EXACT", res_g5["null_variance_exact"], g5a["test_all_hits"]["null_variance"]["exact"]),
    ("G5 inactive p_deficit EXACT", sub_g5_in["p_deficit_exact"], g5a["test_inactive_subclass"]["p_deficit"]["exact"]),
    ("G5 inactive null mean EXACT", sub_g5_in["null_mean_exact"], g5a["test_inactive_subclass"]["null_mean"]["exact"]),
    ("G5 active p_deficit EXACT", sub_g5_ac["p_deficit_exact"], g5a["test_active_subclass"]["p_deficit"]["exact"]),
    ("G5 active null mean EXACT", sub_g5_ac["null_mean_exact"], g5a["test_active_subclass"]["null_mean"]["exact"]),
    ("G5 n_miss", n_miss_g5, g5a["n_miss"]),
    ("G5 RESULTS p_deficit float", res_g5["p_deficit_float"],
     RESULTS["stage_r1"]["decision_rule_inputs"]["g5_confirmatory"]["p_deficit_float"]),
]
mism = []
for name, mine, theirs in cmps:
    ok = feq(mine, theirs)
    out["checks"].append({"check": f"PRODUCER-MATCH {name}", "pass": bool(ok),
                          "validator_value": str(mine)[:400], "producer_value": str(theirs)[:400]})
    if not ok:
        mism.append(name)
out["producer_mismatches"] = mism

# decision-rule inputs re-derived
r0p = res_rest["p_extra_float"]
g5p = res_g5["p_extra_float"]
g5mean = res_g5["null_mean_float"]
g5above = res_g5["S_obs"] > g5mean
out["decision_inputs_validator"] = {
    "r0_anchor_pass": res_anchor["p_extra_float"] > 0.05,
    "g4_anchor_pass": res_g4["p_extra_float"] > 0.05 and len(hits_g4) <= 8,
    "g5_p_extra": g5p, "g5_S_obs": res_g5["S_obs"], "g5_null_mean": g5mean,
    "g5_above_null_mean": g5above,
    "r0_restatement_p_extra": r0p,
    "rx_alive": (res_g4["p_extra_float"] > 0.05 and len(hits_g4) <= 8) and g5p <= 0.05 and g5above,
    "rx_weak_b1": 0.05 < g5p <= 0.15,
    "rx_weak_b2": r0p <= 0.05 and g5p > 0.15,
    "rx_dead": (res_g4["p_extra_float"] > 0.05 and len(hits_g4) <= 8) and g5p > 0.15 and res_g5["S_obs"] <= g5mean,
}

with open(ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-5174ca/vruns/xstat_rederivation.json", "w") as f:
    json.dump(out, f, indent=1)
print("FAILS:", [c["check"] for c in out["checks"] if not c["pass"]])
print("n_checks:", len(out["checks"]))
print("r0 restatement p_extra:", res_rest["p_extra_float"])
print("G5 p_deficit:", res_g5["p_deficit_float"], "G5 null mean:", res_g5["null_mean_float"])
print("decision:", json.dumps(out["decision_inputs_validator"], indent=1))
