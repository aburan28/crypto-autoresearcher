#!/usr/bin/env python3
"""TASK-20260803-e55757 -- analysis and RESULTS.json builder.

Applies ONE criterion, the strict frozen BATCH-004 rule:
    ALIVE iff X/v >= 5 AND P(K >= X | lambda = v) < 1e-6.
No second reading is computed or reported (CORR-20260803-2cefa6).
"""
import json, math, os, subprocess, sys, glob, hashlib, platform, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "../../../BATCH-006/tasks/TASK-20260803-0764fc"))

# ---------- exact-enough Poisson upper tail -------------------------------
def poisson_tail_ge(x, lam):
    """P(K >= x | lam), summed upward from k=x so no catastrophic cancellation."""
    if x <= 0:
        return 1.0
    # log term at k=x, then ratio-step upward
    logt = -lam + x * math.log(lam) - math.lgamma(x + 1)
    t = math.exp(logt)
    total = t
    k = x
    while True:
        k += 1
        t *= lam / k
        total += t
        if t < total * 1e-18 or k > x + 10000:
            break
    return total

# ---------- one-sided 95% Clopper-Pearson lower bound ---------------------
def binom_tail_ge(k, n, p):
    """sum_{j=k}^{n} C(n,j) p^j (1-p)^(n-j)."""
    if p <= 0.0:
        return 0.0 if k > 0 else 1.0
    if p >= 1.0:
        return 1.0
    s = 0.0
    for j in range(k, n + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1)
                      + j * math.log(p) + (n - j) * math.log1p(-p))
    return s

def cp_lower_95(k, n):
    """One-sided 95% lower bound: solve sum_{j=k}^{n} C(n,j) p^j (1-p)^(n-j) = 0.05."""
    if k == 0:
        return 0.0
    if k == n:
        return 0.05 ** (1.0 / n)
    lo, hi = 0.0, 1.0
    for _ in range(300):
        mid = (lo + hi) / 2.0
        if binom_tail_ge(k, n, mid) < 0.05:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0

# ---------- self-tests on the estimator, before it touches my data --------
ESTIMATOR_SELFTEST = {
    "recompute_BATCH006_bound_from_k25_n27": cp_lower_95(25, 27),
    "BATCH006_reported_value": 0.784700038857546,
    "agrees_to_1e-12": abs(cp_lower_95(25, 27) - 0.784700038857546) < 1e-12,
    "recompute_k27_n27_as_arithmetic_check_only": 0.05 ** (1.0 / 27),
    "poisson_tail_ge_9_lambda_1": poisson_tail_ge(9, 1.0),
    "BATCH006_poisson_tail_for_X9": 1.1252025979846536e-06,
    "poisson_tail_ge_6_lambda_1": poisson_tail_ge(6, 1.0),
    "BATCH006_poisson_tail_for_X6": 0.0005941848175816666,
}

def classify(x, v):
    ratio = (x / v) if v > 0 else float("inf")
    tail = poisson_tail_ge(x, v)
    alive = (ratio >= 5.0) and (tail < 1e-6)
    return ratio, tail, alive

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()

def main():
    seeds = [f"202608037{i:02d}" for i in range(1, 28)]
    draws = {}
    completed, not_completed = [], []
    for i, s in enumerate(seeds, start=1):
        name = f"B{i:02d}-RAND-{s}"
        mine_p = os.path.join(HERE, "runs", f"{name}.json")
        ref_p = os.path.join(REF, "runs", f"{name}.json")
        ref = json.load(open(ref_p))
        entry = {"arm": name, "sbox_seed": int(s)}
        if not os.path.exists(mine_p) or os.path.getsize(mine_p) == 0:
            entry["status_this_task"] = "NOT_RUN"
            entry["reason"] = "dropped on budget before start; see runs/dropped.txt"
            entry["batch006"] = {
                "W_ge1_nontrivial": ref["W_ge1_nontrivial"],
                "trivial_swaps_excluded": ref["trivial_swaps_excluded"],
                "W_ge1_by_word": ref["W_ge1_by_word"],
                "whist": ref["whist"],
            }
            not_completed.append(name)
            draws[name] = entry
            continue
        m = json.load(open(mine_p))
        completed.append(name)
        v = m["nontrivial_trials"] * 4.0 / 2 ** 32
        x = m["W_ge1_nontrivial"]
        ratio, tail, alive = classify(x, v)
        fields = ["trivial_swaps_excluded", "nontrivial_trials", "W_ge1_nontrivial",
                  "W_ge1_by_word", "whist", "key_hex", "thread_seeds", "sbox_first8"]
        per_field = {f: {"mine": m[f], "batch006": ref[f], "agree": m[f] == ref[f]}
                     for f in fields}
        entry.update({
            "status_this_task": "COMPLETED",
            "mine": {k: m[k] for k in ["trials", "nontrivial_trials", "trivial_swaps_excluded",
                                       "W_ge1_nontrivial", "W_ge1_by_word", "whist",
                                       "key_hex", "thread_seeds", "sbox_first8",
                                       "rounds", "amask", "smask", "seed", "arm_id", "threads"]},
            "batch006": {k: ref[k] for k in ["nontrivial_trials", "trivial_swaps_excluded",
                                             "W_ge1_nontrivial", "W_ge1_by_word", "whist"]},
            "per_field_agreement": per_field,
            "AGREEMENT": "EXACT_AGREEMENT" if all(d["agree"] for d in per_field.values())
                         else "DISAGREEMENT",
            "disagreeing_fields": [f for f, d in per_field.items() if not d["agree"]],
            "null_modeled_v": v,
            "X_over_v_measured_over_modeled": ratio,
            "poisson_tail_P_K_ge_X_given_v": tail,
            "criterion_conjunct_1_ratio_ge_5": ratio >= 5.0,
            "criterion_conjunct_2_tail_lt_1e-6": tail < 1e-6,
            "STRICT_BATCH004_CLASSIFICATION": "ALIVE" if alive else "NOT_ALIVE",
        })
        draws[name] = entry

    alive_arms = [n for n, e in draws.items()
                  if e["status_this_task"] == "COMPLETED"
                  and e["STRICT_BATCH004_CLASSIFICATION"] == "ALIVE"]
    not_alive = [n for n, e in draws.items()
                 if e["status_this_task"] == "COMPLETED"
                 and e["STRICT_BATCH004_CLASSIFICATION"] != "ALIVE"]
    k, n = len(alive_arms), len(completed)
    bound = cp_lower_95(k, n) if n else None

    exact = [n_ for n_, e in draws.items()
             if e["status_this_task"] == "COMPLETED" and e["AGREEMENT"] == "EXACT_AGREEMENT"]
    disagree = [n_ for n_, e in draws.items()
                if e["status_this_task"] == "COMPLETED" and e["AGREEMENT"] == "DISAGREEMENT"]
    return draws, completed, not_completed, alive_arms, not_alive, k, n, bound, exact, disagree

if __name__ == "__main__":
    print(json.dumps(ESTIMATOR_SELFTEST, indent=1))


def emit():
    (draws, completed, not_completed, alive_arms, not_alive,
     k, n, bound, exact, disagree) = main()
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    env = json.load(open(os.path.join(HERE, "environment.json")))
    pin_aes = json.load(open(os.path.join(HERE, "runs", "pin_aes_native.json")))
    sbox_checks = {}
    for i in range(1, 28):
        s = f"202608037{i:02d}"
        mp = json.load(open(os.path.join(HERE, "runs", f"pin_rand_{s}.json")))
        rp = json.load(open(os.path.join(REF, "sboxes", f"sbox_rand_{s}.json")))
        sbox_checks[s] = {
            "bijective": mp["sbox_bijective"],
            "roundtrip_checks": mp["roundtrip_checks"],
            "roundtrip_failures": mp["roundtrip_failures"],
            "pin_pass": mp["pin_pass"],
            "sbox_table_identical_to_BATCH006": mp["sbox"] == rp["sbox"],
        }
    timing = open(os.path.join(HERE, "runs", "arms_timing.txt")).read().splitlines() \
        if os.path.exists(os.path.join(HERE, "runs", "arms_timing.txt")) else []
    dropped = open(os.path.join(HERE, "runs", "dropped.txt")).read().splitlines() \
        if os.path.exists(os.path.join(HERE, "runs", "dropped.txt")) else []
    cmds = open(os.path.join(HERE, "runs", "commands.txt")).read().splitlines() \
        if os.path.exists(os.path.join(HERE, "runs", "commands.txt")) else []
    return dict(draws=draws, completed=completed, not_completed=not_completed,
                alive_arms=alive_arms, not_alive=not_alive, k=k, n=n, bound=bound,
                exact=exact, disagree=disagree, now=now, env=env, pin_aes=pin_aes,
                sbox_checks=sbox_checks, timing=timing, dropped=dropped, cmds=cmds,
                selftest=ESTIMATOR_SELFTEST,
                sha_probe_c=sha256(os.path.join(HERE, "rc8probe.c")),
                sha_probe_bin=sha256(os.path.join(HERE, "rc8probe_native")))
