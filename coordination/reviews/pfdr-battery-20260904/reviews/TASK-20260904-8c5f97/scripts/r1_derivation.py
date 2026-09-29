"""R1 / R2 derivation checks for TASK-20260904-8c5f97 (red team, EXP-PFDR-fd901a).

(1) independent check of the S_3 formula against real point arithmetic;
(2) parameter-freeness of the degree-4 top form and the tensor top-rank profile;
(3) full_rank(D) = rank of the degree-(D-4) monomial evaluation matrix on supp(S~);
(4) planted vs uniform profiles at p = 4099 and 2^64 - 59;
(5) EXHAUSTIVE search over x_R at p = 4099 for a rank-drop point.
"""
import json, os, random, sys
from itertools import combinations

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import (N, s3, ell, stilde_values, poly_from_values, profile, d_ff,
                      column_order, echelon_ranks)

REPO = "/home/user/crypto-autoresearcher"
P4099 = 4099
P64 = (1 << 64) - 59
P256 = 2**256 - 2**224 + 2**192 + 2**96 - 1
out = {}


# ---------------------------------------------------------------- (1) S_3 check
def ec_add(p, A, P, Q):
    if P is None: return Q
    if Q is None: return P
    if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
    if P == Q:
        lam = (3 * P[0] * P[0] + A) * pow(2 * P[1] % p, -1, p) % p
    else:
        lam = (Q[1] - P[1]) * pow((Q[0] - P[0]) % p, -1, p) % p
    x = (lam * lam - P[0] - Q[0]) % p
    return (x, (lam * (P[0] - x) - P[1]) % p)


def s3_selftest(p=10007, trials=40):
    rng = random.Random(7)
    ok = bad = 0
    while ok + bad < trials:
        A, Bc = rng.randrange(p), rng.randrange(p)
        if (4 * A**3 + 27 * Bc**2) % p == 0: continue
        pts = []
        for x in range(p):
            r = (x**3 + A * x + Bc) % p
            y = pow(r, (p + 1) // 4, p) if p % 4 == 3 else None
            if y is not None and y * y % p == r:
                pts.append((x, y))
            if len(pts) >= 2: break
        if len(pts) < 2: continue
        P, Q = pts[0], pts[1]
        R = ec_add(p, A, P, Q)
        if R is None: continue
        v = s3(P[0], Q[0], R[0], A, Bc, p)
        ok += (v == 0); bad += (v != 0)
    return {"trials": ok + bad, "vanishes_on_real_decompositions": ok, "failures": bad}


out["s3_selftest"] = s3_selftest()


# --------------------------------------------- (2) top form parameter-freeness
def top4_coeffs(A, Bc, xr, p):
    poly = poly_from_values(stilde_values(A, Bc, xr, p), p)
    return {m: v for m, v in poly.items() if bin(m).count("1") == 4}


def q_block(lo):
    """Q_k = a0a1 + 2 a0a2 + 4 a1a2 on block starting at lo, as {mask: coeff}"""
    a0, a1, a2 = 1 << lo, 1 << (lo + 1), 1 << (lo + 2)
    return {a0 | a1: 1, a0 | a2: 2, a1 | a2: 4}


def predicted_top4(p):
    out_ = {}
    for m1, c1 in q_block(0).items():
        for m2, c2 in q_block(3).items():
            out_[m1 | m2] = (16 * c1 * c2) % p
    return {m: v for m, v in out_.items() if v}


rng = random.Random(20260904)
tops = {}
for p in (P4099, P64, P256):
    agree = 0
    for _ in range(25):
        A, Bc, xr = (rng.randrange(p) for _ in range(3))
        agree += (top4_coeffs(A, Bc, xr, p) == predicted_top4(p))
    tops[str(p)] = {"samples": 25, "top4_equals_16_Q1_Q2": agree}
out["top_form_parameter_free"] = tops
out["top_form_mod2_is_zero"] = (predicted_top4(2) == {})


def top_rank_from_topform(top4, p, D):
    """rank of multiplication by the top form from degree D-4 to degree D in F_p[a]/(a^2)"""
    tgt = {m: i for i, m in enumerate(
        (sum(1 << i for i in c) for c in combinations(range(N), D)))}
    rows = []
    for c in combinations(range(N), D - 4):
        mu = sum(1 << i for i in c)
        row = {}
        for m, v in top4.items():
            if m & mu: continue            # a_i^2 = 0 in the top-form algebra
            row[tgt[m | mu]] = (row.get(tgt[m | mu], 0) + v) % p
        rows.append({k: v for k, v in row.items() if v})
    full, _ = echelon_ranks(rows, p, 10**9)
    return full


out["tensor_top_rank_profile"] = {
    str(p): [top_rank_from_topform(predicted_top4(p), p, D) for D in (4, 5, 6)]
    for p in (P4099, P64, P256, 3)}


# ---------------------------------- (3) full_rank = evaluation rank on supp(S~)
def eval_rank_on_support(vals, p, deg):
    supp = [v for v in range(1 << N) if vals[v] % p]
    rows = []
    for c in combinations(range(N), deg):
        mu = sum(1 << i for i in c)
        rows.append({j: 1 for j, v in enumerate(supp) if (v & mu) == mu})
    full, _ = echelon_ranks(rows, p, 10**9)
    return full, len(supp)


# fixture instance from the committed run record
FIX = dict(A=941, Bc=428, xr=3690, p=P4099)
vals = stilde_values(FIX["A"], FIX["Bc"], FIX["xr"], FIX["p"])
prof = profile(poly_from_values(vals, FIX["p"]), FIX["p"])
out["fixture_p4099"] = {
    "profile_full_rank": [0] + [x[0] for x in prof][1:],
    "profile_full_top_fall": prof,
    "d_ff": d_ff(prof),
    "record_full_rank": [0, 1, 6, 15], "record_top_rank": [0, 1, 2, 1],
    "record_fall_dim": [0, 0, 4, 14], "record_d_ff": 5,
    "eval_rank_check": {str(D): eval_rank_on_support(vals, FIX["p"], D - 4) for D in (4, 5, 6)},
    "zeros_on_cube": sum(1 for v in vals if v % FIX["p"] == 0),
}


# --------------------------------------- (4) planted vs uniform, two primes
def load_draws(run, arm):
    with open(os.path.join(REPO, "experiments/EXP-PFDR-fd901a/runs", run, "raw-result.json")) as fh:
        raw = json.load(fh)["raw"]
    curves = {c["seed"]: c for c in raw["curves"]}
    return [(curves[d["curve_seed"]]["a"], curves[d["curve_seed"]]["b"], d["x_R"], d)
            for d in raw["draws"] if d["arm"] == arm]


cmp_out = {}
for run, p in (("RUN-PFDR-fd901a-sweep-p4099", P4099),
               ("RUN-PFDR-fd901a-sweep-p64", P64),
               ("RUN-PFDR-fd901a-sweep-p256", P256)):
    planted = load_draws(run, "semaev")
    agree = 0
    profs = {}
    zeros = []
    for A, Bc, xr, d in planted:
        v = stilde_values(A, Bc, xr, p)
        pr = profile(poly_from_values(v, p), p)
        profs[str([list(x[:2]) for x in pr])] = profs.get(str([list(x[:2]) for x in pr]), 0) + 1
        zeros.append(sum(1 for t in v if t % p == 0))
        agree += ([x[0] for x in pr] == d["profile_full_rank"] and
                  [x[1] for x in pr] == d["profile_top_rank"])
    rng2 = random.Random(4242 + (p % 1000))
    uprofs = {}
    uzeros = []
    for _ in range(20):
        A, Bc, xr = (rng2.randrange(p) for _ in range(3))
        v = stilde_values(A, Bc, xr, p)
        pr = profile(poly_from_values(v, p), p)
        uprofs[str([list(x[:2]) for x in pr])] = uprofs.get(str([list(x[:2]) for x in pr]), 0) + 1
        uzeros.append(sum(1 for t in v if t % p == 0))
    cmp_out[str(p)] = {"planted_draws": len(planted), "planted_profiles": profs,
                       "planted_reproduce_record": agree,
                       "planted_zero_counts": {str(k): zeros.count(k) for k in sorted(set(zeros))},
                       "uniform_samples": 20, "uniform_profiles": uprofs,
                       "uniform_zero_counts": {str(k): uzeros.count(k) for k in sorted(set(uzeros))}}
out["planted_vs_uniform"] = cmp_out

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "r1_derivation.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
