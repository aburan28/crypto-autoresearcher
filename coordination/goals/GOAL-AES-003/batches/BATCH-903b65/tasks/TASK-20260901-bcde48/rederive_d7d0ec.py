import json
import math
import os

TASKDIR = os.path.dirname(os.path.abspath(__file__))
BASE = "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-d7d0ec/"
ARMS = ["raw_M1_r4.jsonl", "raw_M1_r5.jsonl", "raw_M1_r6.jsonl", "raw_M1_r6_rand.jsonl",
        "raw_CTRL_r4.jsonl", "raw_CTRL_r5.jsonl", "raw_CTRL_r6.jsonl", "raw_CTRL_r6_rand.jsonl"]
SEED = 88172645463325252
STEP = 2654435761

# --- fresh GF(2^4) arithmetic, modulus x^4+x+1 (0b10011 = 0x13) ---
def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x10:
            a ^= 0x13
        b >>= 1
    return r & 0xF

def gf_inv(a):
    for x in range(1, 16):
        if gf_mul(a, x) == 1:
            return x
    raise ZeroDivisionError

def mat_mul(A, B):
    out = []
    for i in range(4):
        row = []
        for j in range(4):
            acc = 0
            for k in range(4):
                acc ^= gf_mul(A[i][k], B[k][j])  # char 2: addition is XOR
            row.append(acc)
        out.append(row)
    return out

def gauss_rank_det(M):
    A = [row[:] for row in M]
    rank, det = 0, 1
    for col in range(4):
        piv = None
        for r in range(rank, 4):
            if A[r][col]:
                piv = r
                break
        if piv is None:
            continue
        if piv != rank:
            A[rank], A[piv] = A[piv], A[rank]  # char 2: row swap leaves det unchanged
        det = gf_mul(det, A[rank][col])
        invp = gf_inv(A[rank][col])
        A[rank] = [gf_mul(v, invp) for v in A[rank]]
        for r in range(4):
            if r != rank and A[r][col]:
                f = A[r][col]
                A[r] = [(A[r][c] ^ gf_mul(f, A[rank][c])) & 0xF for c in range(4)]
        rank += 1
    return rank, det

IDENT = [[1 if i == j else 0 for j in range(4)] for i in range(4)]

def check_matrix_line(line, name):
    m = json.loads(line)
    M = {"M1": [[0, 3, 1, 1], [1, 2, 3, 0], [1, 1, 0, 3], [3, 0, 1, 2]],
         "CTRL": None}[m["matrix"]]
    res = {"matrix": m["matrix"]}
    if M is None:
        # circulant (2,3,1,1), right-circulant: M[i][j] = first[(j-i) mod 4]
        first = [2, 3, 1, 1]
        M = [[first[(j - i) % 4] for j in range(4)] for i in range(4)]
    rank, det = gauss_rank_det(M)
    res["fresh_rank"] = rank
    res["fresh_det"] = det
    res["claimed_rank"] = m["rank"]
    res["claimed_det"] = m["det"]
    res["rank_match"] = rank == m["rank"]
    res["det_match"] = det == m["det"]
    res["non_singular_fresh"] = rank == 4
    prod = mat_mul(M, m["inverse"])
    res["M_times_claimed_inverse_is_I"] = prod == IDENT
    return res

out = {"arms": {}, "matrix_checks": {}, "verdict_rule": None, "seed_checks": {}}
m1r6 = None
for arm in ARMS:
    lines = [l.rstrip("\n") for l in open(BASE + arm)]
    assert len(lines) == 42, (arm, len(lines))
    trials = [json.loads(l) for l in lines[1:41]]
    summary_committed = json.loads(lines[41])["summary"]
    matrix_check = check_matrix_line(lines[0], arm)
    out["matrix_checks"][arm] = matrix_check

    n_0mod8 = n_eq0 = occ16 = 0
    internal_ok = True
    seed_ok = True
    details = []
    for t, tr in enumerate(trials):
        if tr["trial"] != t or tr["seed"] != SEED + t * STEP:
            seed_ok = False
        occ = tr["occ_hist"]
        n_recon = sum(c * (o * (o - 1) // 2) for o, c in
                      ((int(k), v) for k, v in occ.items()))
        max_occ_fresh = max((int(k) for k in occ), default=0)
        mult16_fresh = all(int(k) % 16 == 0 for k in occ) if occ else True
        ok = (n_recon == tr["n"] and tr["n_mod8"] == tr["n"] % 8 and
              tr["n_mod16"] == tr["n"] % 16 and
              max_occ_fresh == tr["max_occ"] and
              bool(tr["all_occ_multiple_of_16"]) == mult16_fresh)
        if not ok:
            internal_ok = False
            details.append({"trial": t, "n_recorded": tr["n"], "n_recon": n_recon})
        if tr["n"] % 8 == 0:
            n_0mod8 += 1
        if tr["n"] == 0:
            n_eq0 += 1
        if mult16_fresh:
            occ16 += 1
    fresh_summary = {"matrix": summary_committed["matrix"], "r": summary_committed["r"],
                     "j0": summary_committed["j0"],
                     "rand_sbox": summary_committed["rand_sbox"],
                     "trials": len(trials),
                     "trials_n_0mod8": n_0mod8,
                     "trials_n_eq_0": n_eq0,
                     "trials_all_occ_multiple_of_16": occ16}
    match = all(fresh_summary[k] == summary_committed[k] for k in fresh_summary)
    out["arms"][arm] = {
        "committed_summary": summary_committed,
        "fresh_summary": fresh_summary,
        "summary_match": match,
        "per_trial_internal_consistency": internal_ok,
        "seed_progression_ok": seed_ok,
        "internal_issues": details,
    }
    out["seed_checks"][arm] = seed_ok
    if arm == "raw_M1_r6.jsonl":
        m1r6 = fresh_summary

# preregistered exact predictions
m1r4 = out["arms"]["raw_M1_r4.jsonl"]["fresh_summary"]
ctrlr4 = out["arms"]["raw_CTRL_r4.jsonl"]["fresh_summary"]
C2_16 = math.comb(2**16, 2)
r4_lines = [json.loads(l) for l in open(BASE + "raw_M1_r4.jsonl")][1:41]
out["prereg_checks"] = {
    "M1_r4_n_expected": C2_16,
    "M1_r4_all_trials_n_eq_expected": all(t["n"] == C2_16 for t in r4_lines),
    "M1_r4_single_fiber_65536": all(t["occ_hist"] == {"65536": 1} for t in r4_lines),
    "CTRL_r4_all_trials_n_eq_0": all(json.loads(l)["n"] == 0
                                     for l in open(BASE + "raw_CTRL_r4.jsonl").read().splitlines()[1:41]),
    "M1_r5_40_of_40_mod8_zero": m1r6 is not None and out["arms"]["raw_M1_r5.jsonl"]["fresh_summary"]["trials_n_0mod8"] == 40,
    "CTRL_r5_40_of_40_mod8_zero": out["arms"]["raw_CTRL_r5.jsonl"]["fresh_summary"]["trials_n_0mod8"] == 40,
}

# verdict rule 4.3 on M1 r=6
zero_rate = m1r6["trials_n_0mod8"]
div16 = m1r6["trials_all_occ_multiple_of_16"]
if zero_rate >= 15 or div16 >= 39:
    verdict = "FALSIFIED"
elif zero_rate <= 7 and div16 <= 2:
    verdict = "SURVIVES"
else:
    verdict = "UNDECIDED"
out["verdict_rule"] = {"M1_r6_zero_rate": zero_rate, "M1_r6_div16_trials": div16,
                       "prereg_rule": "FALSIFIED if zeros>=15 or div16>=39; SURVIVES if zeros<=7 and div16<=2; else UNDECIDED",
                       "verdict_fresh": verdict}

v_first = [2, 3, 0, 1]
v_M = [[v_first[(j - i) % 4] for j in range(4)] for i in range(4)]
v_rank, v_det = gauss_rank_det(v_M)
out["validator_substitute_2301_check"] = {
    "matrix": "circulant (2,3,0,1), right-circulant convention",
    "rank_fresh": v_rank,
    "singular": v_rank < 4,
    "prereg_claim": "singular, rank 3",
    "match": v_rank == 3,
}

print(json.dumps(out, indent=1))
with open(os.path.join(TASKDIR, "d7d0ec_result.json"), "w") as f:
    json.dump(out, f, indent=1)
