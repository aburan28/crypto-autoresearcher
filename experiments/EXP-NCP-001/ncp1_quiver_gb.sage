# EXP-NCP-001 / NCP -- ncp1_quiver_gb.sage
# Minimal falsifying experiment for candidate C3 (handoff TASK-20260717-C3).
# Truncated (degree <= 6) noncommutative word search on the single-vertex
# correspondence quiver {T_{P_i}, i=1..B} + {neg} acting on formal point-sums of
# E(F_p) via the affine normal form X -> eps*X + beta*P (eps in {+1,-1},
# beta in Z/n), vs a commutative signed-subset-sum baseline at equal op budget.
# Deterministic: all randomness from random.Random with fixed string seeds.
#
# Usage: sage experiments/EXP-NCP-001/ncp1_quiver_gb.sage
# Writes: experiments/EXP-NCP-001/runs/RUN-NCP-001-a/raw.json (atomic replace)

import os
import sys
import json
import math
import time
import resource
import platform
import datetime
import random
from sage.all import EllipticCurve, GF, factor

# ---------------- frozen protocol constants (specification.yaml) ----------------
EXP_ID = "EXP-NCP-001"
RUN_ID = "RUN-NCP-001-a"
PRIMES = [101, 431]
B_GRID = [4, 8]
SEEDS = [20260717, 20260718, 20260719]
DEG = int(6)
# Sage preparser turns literals into sage Integers; coerce to plain Python ints
# (needed for JSON serialization and clean modulo arithmetic).
PRIMES = [int(x) for x in PRIMES]
B_GRID = [int(x) for x in B_GRID]
SEEDS = [int(x) for x in SEEDS]
ENGINE_SAMPLE = int(200)          # positive control (a): random words per instance
QWORD_POINT_CHECK_CAP = int(200)  # positive control (b): Q-reaching words point-checked
QWORD_STORE_CAP = int(20000)      # stored Q-reaching words for shadow replay
N_FLOOR = int(13)                 # minimum prime subgroup order accepted
R_MATCH = int(6)             # commutative baseline degree bound (matches NC truncation)
R_SAFETY = int(64)           # hard stop for the equal-budget radius loop

t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
rusage0 = resource.getrusage(resource.RUSAGE_SELF)


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ---------------- instance generation (deterministic per (p, seed)) ----------------
def setup_instance(p, seed):
    """Seeded curve over F_p with subgroup of prime order n >= N_FLOOR; point P of
    exact order n. Returns (E, N_curve, n, cofactor, P)."""
    rng = random.Random("NCP1-curve-%d-%d" % (p, seed))
    F = GF(p)
    while True:
        a = F(rng.randrange(int(p)))
        b = F(rng.randrange(int(p)))
        if (4 * a ** 3 + 27 * b ** 2) == 0:
            continue
        E = EllipticCurve(F, [a, b])
        N = int(E.order())
        n = max(int(q) for q, _e in factor(N))
        if n < N_FLOOR:
            continue
        cof = N // n
        rng2 = random.Random("NCP1-point-%d-%d" % (p, seed))
        while True:
            x = F(rng2.randrange(int(p)))
            rhs = x ** 3 + a * x + b
            if rhs.is_square():
                G = E(x, rhs.sqrt())
                P = cof * G
                if (not P.is_zero()) and (n * P).is_zero():
                    return E, N, n, cof, P


def gen_params(p, B, seed, n):
    """Seeded target scalar k in [2, n-2] and distinct nonzero factor-base scalars."""
    rng = random.Random("NCP1-inst-%d-%d-%d" % (p, B, seed))
    k = rng.randrange(2, n - 1)
    ss = set()
    while len(ss) < B:
        ss.add(rng.randrange(1, n - 1))
    return k, sorted(ss)


# ---------------- evaluation engines ----------------
def scalar_eval_word(w, s, B, n):
    """Affine bookkeeping: state (eps, beta); T_i: beta += s_i; N: (eps,beta)->(-eps,-beta).
    Returns v = eps + beta mod n, i.e. eval(w, P) = v*P."""
    eps, beta = 1, 0
    for L in w:
        if L < B:
            beta = (beta + s[L]) % n
        else:
            eps, beta = -eps, (-beta) % n
    return (eps + beta) % n


def point_eval_word(P, Pi, w, B):
    """Independent point-arithmetic evaluation: apply arrows left to right."""
    X = P
    for L in w:
        X = X + Pi[L] if L < B else -X
    return X


def shadow_of_word(w, B):
    """Commutative shadow: eps = (-1)^#N; a_i = signed count of T_i occurrences,
    sign of an occurrence = (-1)^{#N to its right}. v(w) = eps + sum a_i s_i."""
    totalN = sum(1 for L in w if L == B)
    eps = -1 if totalN % 2 else 1
    a = [0] * B
    neg_right = 0
    for L in reversed(w):
        if L == B:
            neg_right += 1
        else:
            a[L] += 1 if neg_right % 2 == 0 else -1
    return eps, a


# ---------------- noncommutative truncated search (degree <= DEG) ----------------
def nc_search(s, k, n, B):
    """Exhaustive DFS over all (B+1)^d words, d <= DEG; every word reduced to its
    affine normal form (the relation set found equals the set a truncated
    Bergman/NC-GB search certifies at this degree bound).
    Returns (ops, hist, qcount, qwords_stored)."""
    ops = 0
    hist = {}
    qcount = 0
    qwords = []
    stack = [(1, 0, ())]
    while stack:
        eps, beta, w = stack.pop()
        ops += 1
        v = (eps + beta) % n
        hist[v] = hist.get(v, 0) + 1
        if v == k:
            qcount += 1
            if len(qwords) < QWORD_STORE_CAP:
                qwords.append(w)
        if len(w) < DEG:
            for i in range(B):
                stack.append((eps, (beta + s[i]) % n, w + (i,)))
            stack.append((-eps, (-beta) % n, w + (B,)))  # letter B = negation
    return ops, hist, qcount, qwords


# ---------------- commutative signed-subset-sum baseline ----------------
def comm_shell_vectors(B, r):
    """All a in Z^B with sum |a_i| == r (shell), deterministic order."""
    if r == 0:
        return [tuple([0] * B)]
    out = []

    def rec(i, rem, acc):
        if i == B - 1:
            if rem == 0:
                out.append(tuple(acc + [0]))
            else:
                out.append(tuple(acc + [rem]))
                out.append(tuple(acc + [-rem]))
            return
        for ai in range(-rem, rem + 1):
            acc.append(ai)
            rec(i + 1, rem - abs(ai), acc)
            acc.pop()

    rec(0, r, [])
    return out


def comm_baseline(s, k, n, B, ops_budget):
    """Enumerate (a, eps) pairs by increasing l1 radius r. Charge 1 op per
    evaluation (2 per vector: eps = +1 and eps = -1). Record degree<=R_MATCH stats
    and continue until the op budget (ops_nc) is exhausted; record radius reached."""
    S_comm = set()       # values reached with r <= R_MATCH
    vec_set_d6 = set()   # vectors with r <= R_MATCH (for shadow membership)
    ops_d6 = 0
    R_d6 = 0
    ops_eq = 0
    R_eq = 0
    r_reached = -1
    r = 0
    while True:
        for a in comm_shell_vectors(B, r):
            sig = 0
            for i in range(B):
                if a[i]:
                    sig = (sig + a[i] * s[i]) % n
            vpos = (1 + sig) % n
            vneg = (-1 + sig) % n
            if r <= R_MATCH:
                ops_d6 += 2
                S_comm.add(vpos)
                S_comm.add(vneg)
                vec_set_d6.add(a)
                if vpos == k:
                    R_d6 += 1
                if vneg == k:
                    R_d6 += 1
            ops_eq += 2
            if vpos == k:
                R_eq += 1
            if vneg == k:
                R_eq += 1
            if ops_eq >= ops_budget and r >= R_MATCH:
                # stop at vector granularity so the commutative baseline is
                # charged an op budget equal to ops_nc (final shell may be partial)
                r_reached = r
                return {"ops_d6": ops_d6, "R_d6": R_d6, "S_comm": S_comm,
                        "vec_set_d6": vec_set_d6, "ops_eq": ops_eq, "R_eq": R_eq,
                        "r_reached": r_reached, "final_shell_partial": True,
                        "radius_safety_hit": False}
        r_reached = r
        r += 1
        if r > R_SAFETY:
            break
    return {"ops_d6": ops_d6, "R_d6": R_d6, "S_comm": S_comm,
            "vec_set_d6": vec_set_d6, "ops_eq": ops_eq, "R_eq": R_eq,
            "r_reached": r_reached, "final_shell_partial": False,
            "radius_safety_hit": bool(r > R_SAFETY)}


# ---------------- main loop over the 12 instances ----------------
instances = []
for p in PRIMES:
    for seed in SEEDS:
        E, N, n, cof, P = setup_instance(p, seed)
        for B in B_GRID:
            ti = time.time()
            k, s = gen_params(p, B, seed, n)
            Q = k * P
            Pi = [si * P for si in s]
            print("instance p=%d B=%d seed=%d: n=%d k=%d ..." % (p, B, seed, n, k))
            sys.stdout.flush()

            # --- NC truncated search ---
            ops_nc, hist, R_nc, qwords = nc_search(s, k, n, B)
            ops_expected = sum((B + 1) ** d for d in range(DEG + 1))
            selfcheck_ok = (ops_nc == ops_expected)
            V_nc = len(hist)
            collisions = sum(c * (c - 1) // 2 for c in hist.values())
            hist_max = max(hist.values())
            hist_mean = float(ops_nc) / float(V_nc)

            # --- commutative baseline at equal op budget ---
            comm = comm_baseline(s, k, n, B, ops_nc)
            S_comm = comm["S_comm"]

            # --- positive control: engine verified on known k ---
            rngc = random.Random("NCP1-ctl-%d-%d-%d" % (p, B, seed))
            engine_mismatch = 0
            for _ in range(ENGINE_SAMPLE):
                ell = rngc.randrange(0, DEG + 1)
                w = tuple(rngc.randrange(0, B + 1) for _ in range(ell))
                v = scalar_eval_word(w, s, B, n)
                if point_eval_word(P, Pi, w, B) != v * P:
                    engine_mismatch += 1
            qword_point_bad = 0
            qword_point_checked = 0
            for w in qwords[:QWORD_POINT_CHECK_CAP]:
                qword_point_checked += 1
                if (point_eval_word(P, Pi, w, B) != Q) or (scalar_eval_word(w, s, B, n) != k):
                    qword_point_bad += 1
            if R_nc > 0:
                k_recovered = scalar_eval_word(qwords[0], s, B, n)
                k_recovery_ok = bool(k_recovered == k)
            else:
                k_recovered = None
                k_recovery_ok = None  # not testable: no Q-reaching word at this budget

            # --- negative control: commutative quotient reproduces all NC relations ---
            S_nc = set(hist.keys())
            value_violations = len(S_nc - S_comm)
            shadow_checked = 0
            shadow_violations = 0
            for w in qwords:
                eps, a = shadow_of_word(w, B)
                shadow_checked += 1
                l1 = sum(abs(ai) for ai in a)
                val = (eps + sum(a[i] * s[i] for i in range(B))) % n
                if l1 > DEG or val != k or tuple(a) not in comm["vec_set_d6"]:
                    shadow_violations += 1

            inst = {
                "p": int(p), "B": int(B), "seed": int(seed),
                "curve": {"a": int(E.a4()), "b": int(E.a6())},
                "N_curve": int(N), "n": int(n), "cofactor": int(cof),
                "P": [int(P[0]), int(P[1])], "Q": [int(Q[0]), int(Q[1])],
                "k": int(k), "s": [int(x) for x in s],
                "ops_nc": int(ops_nc), "ops_nc_expected": int(ops_expected),
                "selfcheck_ops_formula": bool(selfcheck_ok),
                "R_nc_qreaching": int(R_nc),
                "V_nc_distinct_values": int(V_nc),
                "collisions_nc_word_pairs": int(collisions),
                "hist_max_bucket": int(hist_max), "hist_mean_bucket": hist_mean,
                "cost_nc_per_rel": (float(ops_nc) / float(R_nc)) if R_nc > 0 else None,
                "ops_comm_d6": int(comm["ops_d6"]), "R_comm_d6": int(comm["R_d6"]),
                "V_comm_d6": int(len(S_comm)),
                "cost_comm_d6_per_rel": (float(comm["ops_d6"]) / float(comm["R_d6"])) if comm["R_d6"] > 0 else None,
                "comm_equal_budget": {
                    "ops": int(comm["ops_eq"]), "R_comm_eq": int(comm["R_eq"]),
                    "radius_reached": int(comm["r_reached"]),
                    "radius_safety_hit": comm["radius_safety_hit"],
                    "cost_comm_eq_per_rel": (float(comm["ops_eq"]) / float(comm["R_eq"])) if comm["R_eq"] > 0 else None,
                },
                "positive_control": {
                    "engine_words_checked": ENGINE_SAMPLE,
                    "engine_mismatches": int(engine_mismatch),
                    "qwords_point_checked": int(qword_point_checked),
                    "qwords_point_mismatches": int(qword_point_bad),
                    "k_recovered": (int(k_recovered) if k_recovered is not None else None),
                    "k_recovery_ok": k_recovery_ok,
                },
                "negative_control": {
                    "Snc_subset_Scomm": bool(value_violations == 0),
                    "value_violations": int(value_violations),
                    "shadow_words_checked": int(shadow_checked),
                    "shadow_violations": int(shadow_violations),
                    "shadow_sample_capped": bool(R_nc > QWORD_STORE_CAP),
                },
                "qword_examples_first10": [list(w) for w in qwords[:10]],
                "wall_seconds_instance": time.time() - ti,
            }
            instances.append(inst)
            print("  ops_nc=%d R_nc=%d | comm_eq ops=%d R=%d r=%d | ctl: eng_bad=%d qw_bad=%d val_viol=%d sh_viol=%d"
                  % (ops_nc, R_nc, comm["ops_eq"], comm["R_eq"], comm["r_reached"],
                     engine_mismatch, qword_point_bad, value_violations, shadow_violations))
            sys.stdout.flush()

# ---------------- gate arithmetic (frozen metric definitions) ----------------
def fmean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


gate = []
for B in B_GRID:
    row = {"B": int(B)}
    per_p = {}
    for p in PRIMES:
        sel = [i for i in instances if i["p"] == p and i["B"] == B]
        per_p[str(p)] = {
            "cost_nc_per_rel_mean": fmean([i["cost_nc_per_rel"] for i in sel]),
            "cost_comm_d6_per_rel_mean": fmean([i["cost_comm_d6_per_rel"] for i in sel]),
            "cost_comm_eq_per_rel_mean": fmean([i["comm_equal_budget"]["cost_comm_eq_per_rel"] for i in sel]),
            "n_mean": fmean([float(i["n"]) for i in sel]),
            "R_nc_mean": fmean([float(i["R_nc_qreaching"]) for i in sel]),
            "R_comm_eq_mean": fmean([float(i["comm_equal_budget"]["R_comm_eq"]) for i in sel]),
            "instances_with_zero_R_nc": sum(1 for i in sel if i["R_nc_qreaching"] == 0),
        }
    row["per_p"] = per_p
    c1 = per_p[str(PRIMES[0])]
    c2 = per_p[str(PRIMES[1])]
    for key, label in [("cost_nc_per_rel_mean", "charged_exponent_nc"),
                       ("cost_comm_eq_per_rel_mean", "charged_exponent_comm_eq"),
                       ("cost_comm_d6_per_rel_mean", "charged_exponent_comm_d6")]:
        if c1[key] and c2[key] and c1["n_mean"] and c2["n_mean"]:
            row[label] = math.log(c2[key] / c1[key]) / math.log(c2["n_mean"] / c1["n_mean"])
        else:
            row[label] = None
    row["ratio_nc_over_comm_eq_at_equal_size"] = {
        p: (per_p[p]["cost_nc_per_rel_mean"] / per_p[p]["cost_comm_eq_per_rel_mean"])
        if per_p[p]["cost_nc_per_rel_mean"] and per_p[p]["cost_comm_eq_per_rel_mean"] else None
        for p in [str(PRIMES[0]), str(PRIMES[1])]
    }
    row["gate_threshold_exponent"] = float(0.49)
    gate.append(row)

# ---------------- secondary: log-log scatter fit over all instances ----------------
# The frozen two-point trend uses seed-mean n per prime; subgroup orders vary
# widely across seeds (13..439), so supplement with an OLS fit of
# log(cost per relation) vs log(n) across all 12 instances (n spans ~1.5 decades).
def loglog_fit(points):
    xs = [math.log(x) for x, _y in points]
    ys = [math.log(y) for _x, y in points]
    m = len(xs)
    mx = sum(xs) / m
    my = sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return {"slope": None, "r_squared": None, "points": m}
    return {"slope": sxy / sxx, "r_squared": (sxy * sxy) / (sxx * syy), "points": m}


scatter = {
    "nc_cost_per_rel_vs_n": loglog_fit(
        [(float(i["n"]), i["cost_nc_per_rel"]) for i in instances if i["cost_nc_per_rel"]]),
    "comm_eq_cost_per_rel_vs_n": loglog_fit(
        [(float(i["n"]), i["comm_equal_budget"]["cost_comm_eq_per_rel"])
         for i in instances if i["comm_equal_budget"]["cost_comm_eq_per_rel"]]),
    "comm_d6_cost_per_rel_vs_n": loglog_fit(
        [(float(i["n"]), i["cost_comm_d6_per_rel"]) for i in instances if i["cost_comm_d6_per_rel"]]),
    "note": "Secondary metric: OLS slope of log(cost per Q-reaching relation) vs log(n) across all 12 instances; supplements the frozen two-point charged-exponent trend.",
}

# ---------------- controls summary and validity ----------------
all_engine_ok = all(i["positive_control"]["engine_mismatches"] == 0 for i in instances)
all_qword_point_ok = all(i["positive_control"]["qwords_point_mismatches"] == 0 for i in instances)
all_krec_ok = all(i["positive_control"]["k_recovery_ok"] in (True, None) for i in instances)
all_value_incl = all(i["negative_control"]["Snc_subset_Scomm"] for i in instances)
all_shadow_ok = all(i["negative_control"]["shadow_violations"] == 0 for i in instances)
all_selfcheck = all(i["selfcheck_ops_formula"] for i in instances)
controls_pass = all([all_engine_ok, all_qword_point_ok, all_krec_ok,
                     all_value_incl, all_shadow_ok, all_selfcheck])

rusage1 = resource.getrusage(resource.RUSAGE_SELF)
result = {
    "experiment_id": EXP_ID,
    "run_id": RUN_ID,
    "hypothesis_id": "H-NCP-001",
    "handoff_id": "TASK-20260717-C3",
    "script": "experiments/EXP-NCP-001/ncp1_quiver_gb.sage",
    "command": "sage experiments/EXP-NCP-001/ncp1_quiver_gb.sage",
    "sage_version": str(__import__("sage.version", fromlist=["version"]).version),
    "python_version": platform.python_version(),
    "platform": platform.platform(),
    "machine": platform.machine(),
    "started_at": started_at,
    "finished_at": utc_now(),
    "wall_seconds_total": time.time() - t_start,
    "cpu_seconds_total": (rusage1.ru_utime + rusage1.ru_stime) - (rusage0.ru_utime + rusage0.ru_stime),
    "peak_rss_bytes_macos": int(rusage1.ru_maxrss),
    "protocol": {"primes": PRIMES, "B_grid": B_GRID, "seeds": SEEDS,
                 "max_word_degree": DEG, "n_floor": N_FLOOR,
                 "engine_sample_words": ENGINE_SAMPLE,
                 "qword_point_check_cap": QWORD_POINT_CHECK_CAP,
                 "qword_store_cap": QWORD_STORE_CAP,
                 "comm_degree_match": R_MATCH},
    "instances": instances,
    "gate_arithmetic": gate,
    "secondary_scatter_fit": scatter,
    "controls_summary": {
        "engine_ok": bool(all_engine_ok),
        "qword_point_ok": bool(all_qword_point_ok),
        "k_recovery_ok_all": bool(all_krec_ok),
        "value_inclusion_ok": bool(all_value_incl),
        "shadow_replay_ok": bool(all_shadow_ok),
        "ops_formula_selfcheck_ok": bool(all_selfcheck),
        "controls_pass": bool(controls_pass),
    },
}

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", RUN_ID)
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "raw.json")
tmp_path = out_path + ".tmp"
with open(tmp_path, "w") as f:
    json.dump(result, f, indent=1)
os.replace(tmp_path, out_path)
print("wrote %s" % out_path)
print("controls_pass=%s wall=%.1fs" % (controls_pass, time.time() - t_start))
