#!/usr/bin/env python3
# research/verification/commutator_kernel1_check.py
# Verification for research/THM_COMMUTATOR_KERNEL1.md (task TASK-20260718-THMNCP).
#
# Checks, against the EXP-NCP-001 run artifact (runs/RUN-NCP-001-a/raw.json):
#   (1) Corollary 2 (degree-d value-set formula): the NC reachable value set
#       S_nc(d), recomputed by DFS with the frozen affine rule of
#       experiments/EXP-NCP-001/ncp1_quiver_gb.sage, equals EXACTLY the formula
#       set  S_pred(d) = { eps + sum a_i s_i  (mod n) : |a|_1 + m(eps,a) <= d }
#       with m(+1,a)=0 if a in N^B else 2, m(-1,a)=1.
#   (2) The recomputed |S_nc| matches the recorded V_nc of the actual run
#       (ties the recomputation to the artifact, incl. the strict-inclusion
#       instance p=431, B=4, seed 20260718, n=439: 350 vs commutative 437).
#   (3) S_nc(d) subset S_comm(d) (kernel-collapse value inclusion, Corollary 1).
#   (4) Internal consistency of the shadow law (Lemma 1): incremental affine
#       normal-form reduction vs the closed positional formula for the signed
#       count vector, on random words (two independent computations).
#
# stdlib only. Command: python3 research/verification/commutator_kernel1_check.py
# Writes: research/verification/commutator_kernel1_check_results.json

import json
import os
import random
import sys
import time
import platform

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "experiments", "EXP-NCP-001", "runs", "RUN-NCP-001-a", "raw.json")
OUT = os.path.join(ROOT, "research", "verification", "commutator_kernel1_check_results.json")
DEG = 6  # frozen truncation of EXP-NCP-001


# ---------------- frozen affine rule (mirror of ncp1_quiver_gb.sage) ----------------
def nc_value_set(s, n, B, d):
    """DFS over all words of degree <= d; returns set of values (eps+beta) mod n.
    Mirrors scalar_eval_word / nc_search of the frozen instrument."""
    vals = set()
    stack = [(1, 0, 0)]  # (eps, beta, length)
    while stack:
        eps, beta, ln = stack.pop()
        vals.add((eps + beta) % n)
        if ln < d:
            for i in range(B):
                stack.append((eps, (beta + s[i]) % n, ln + 1))
            stack.append((-eps, (-beta) % n, ln + 1))
    return vals


# ---------------- shadow ball enumeration ----------------
def ball_vectors(B, R):
    """All a in Z^B with l1 norm <= R (recursive, deterministic)."""
    out = []

    def rec(i, rem, acc):
        if i == B - 1:
            for ai in range(-rem, rem + 1):
                out.append(tuple(acc + [ai]))
            return
        for ai in range(-rem, rem + 1):
            acc.append(ai)
            rec(i + 1, rem - abs(ai), acc)
            acc.pop()

    rec(0, R, [])
    return out


def m_min(eps, a):
    """Minimal number of negation letters in any word with shadow (eps, a)
    (Lemma 2(b) of THM_COMMUTATOR_KERNEL1.md)."""
    if eps == -1:
        return 1
    return 0 if all(ai >= 0 for ai in a) else 2


def formula_value_set(s, n, B, d):
    """S_pred(d) of Corollary 2."""
    vals = set()
    for a in ball_vectors(B, d):
        l1 = sum(abs(ai) for ai in a)
        sig = sum(a[i] * s[i] for i in range(B)) % n
        for eps in (1, -1):
            if l1 + m_min(eps, a) <= d:
                vals.add((eps + sig) % n)
    return vals


def comm_value_set(s, n, B, d):
    """S_comm(d): all eps + sum a_i s_i with |a|_1 <= d (both eps)."""
    vals = set()
    for a in ball_vectors(B, d):
        sig = sum(a[i] * s[i] for i in range(B)) % n
        vals.add((1 + sig) % n)
        vals.add((-1 + sig) % n)
    return vals


# ---------------- Lemma 1 internal consistency: two independent shadow computations ----------------
def shadow_incremental(w, B):
    """Affine normal-form reduction: append t_i -> a += e_i; append nu -> (a, eps) -> (-a, -eps)."""
    a = [0] * B
    eps = 1
    for L in w:
        if L < B:
            a[L] += 1
        else:
            a = [-x for x in a]
            eps = -eps
    return eps, tuple(a)


def shadow_positional(w, B):
    """Closed formula: eps = (-1)^#nu; a_i = sum over occurrences of t_i of (-1)^{#nu to the right}."""
    total_nu = sum(1 for L in w if L == B)
    eps = -1 if total_nu % 2 else 1
    a = [0] * B
    nu_right = 0
    for L in reversed(w):
        if L == B:
            nu_right += 1
        else:
            a[L] += 1 if nu_right % 2 == 0 else -1
    return eps, tuple(a)


def main():
    t0 = time.time()
    with open(RAW) as f:
        raw = json.load(f)

    per_instance = []
    all_ok = True
    for inst in raw["instances"]:
        n, B, s = inst["n"], inst["B"], inst["s"]
        S_nc = nc_value_set(s, n, B, DEG)
        S_pred = formula_value_set(s, n, B, DEG)
        S_comm = comm_value_set(s, n, B, DEG)
        rec = {
            "p": inst["p"], "B": B, "seed": inst["seed"], "n": n,
            "recorded_V_nc": inst["V_nc_distinct_values"],
            "recomputed_V_nc": len(S_nc),
            "formula_V_pred": len(S_pred),
            "recorded_V_comm_d6": inst["V_comm_d6"],
            "recomputed_V_comm": len(S_comm),
            "S_nc_eq_S_pred": S_nc == S_pred,
            "S_nc_subset_S_comm": S_nc <= S_comm,
            "V_nc_matches_recorded": len(S_nc) == inst["V_nc_distinct_values"],
            "V_comm_matches_recorded": len(S_comm) == inst["V_comm_d6"],
        }
        rec["ok"] = all([rec["S_nc_eq_S_pred"], rec["S_nc_subset_S_comm"],
                         rec["V_nc_matches_recorded"], rec["V_comm_matches_recorded"]])
        all_ok = all_ok and rec["ok"]
        per_instance.append(rec)
        print("p=%d B=%d seed=%d n=%d: |S_nc|=%d (recorded %d) |S_pred|=%d |S_comm|=%d (recorded %d) ok=%s"
              % (inst["p"], B, inst["seed"], n, len(S_nc), inst["V_nc_distinct_values"],
                 len(S_pred), len(S_comm), inst["V_comm_d6"], rec["ok"]))

    # Lemma 1 internal consistency on random words (all 12 instances' letter distributions)
    rng = random.Random("THMNCP-lemma1-check")
    lemma1_words = 0
    lemma1_mismatch = 0
    for inst in raw["instances"]:
        B = inst["B"]
        for _ in range(1000):
            ln = rng.randrange(0, 9)
            w = tuple(rng.randrange(0, B + 1) for _ in range(ln))
            if shadow_incremental(w, B) != shadow_positional(w, B):
                lemma1_mismatch += 1
            lemma1_words += 1
    print("Lemma 1 consistency: %d random words, %d mismatches" % (lemma1_words, lemma1_mismatch))
    all_ok = all_ok and (lemma1_mismatch == 0)

    result = {
        "script": "research/verification/commutator_kernel1_check.py",
        "command": "python3 research/verification/commutator_kernel1_check.py",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "artifact_checked": "experiments/EXP-NCP-001/runs/RUN-NCP-001-a/raw.json",
        "degree_bound": DEG,
        "per_instance": per_instance,
        "lemma1_random_words": lemma1_words,
        "lemma1_mismatches": lemma1_mismatch,
        "all_checks_pass": all_ok,
        "wall_seconds": time.time() - t0,
    }
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(result, f, indent=1)
    os.replace(tmp, OUT)
    print("wrote %s" % OUT)
    print("all_checks_pass=%s wall=%.2fs" % (all_ok, time.time() - t0))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
