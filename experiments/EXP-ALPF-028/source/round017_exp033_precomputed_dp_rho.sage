#!/usr/bin/env sage
# =============================================================================
# round017_exp033_precomputed_dp_rho.sage
#
# Precomputed distinguished-point Pollard-rho for toy prime-field ECDLP.
#
# This implements the generic non-uniform Bernstein-Lange mechanism from
# "Non-uniform cracks in the concrete", Section 3.2:
#   precompute target-independent walks from known multiples A*P;
#   store distinguished endpoints (D=A0*P, A0);
#   solve Q=k*P by walking from A*P + b*Q until the endpoint lands in the table.
#
# Scope: controlled toy curves only. This is not an index-calculus attack and not
# a deployment-relevant break. The point is to make the precompute/online split
# measurable and falsifiable.
# =============================================================================

import argparse
import json
import math
import os
import operator
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from sage.all import EllipticCurve, GF, ZZ, ceil, inverse_mod, is_prime, random_prime, set_random_seed, sqrt


RAW_SCRIPT_PATH = Path(sys.argv[0]).resolve()
SCRIPT_PATH = Path(str(RAW_SCRIPT_PATH)[:-3]) if str(RAW_SCRIPT_PATH).endswith(".sage.py") else RAW_SCRIPT_PATH
OUTDIR = SCRIPT_PATH.parent
RESULT_JSON = OUTDIR / "round017_exp033_precomputed_dp_rho_result.json"
RESULT_MD = OUTDIR / "round017_exp033_precomputed_dp_rho_result.md"
LOG_PATH = OUTDIR / "round017_exp033_precomputed_dp_rho.log"

log_lines = []


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] %s" % (ts, msg)
    print(line, flush=True)
    log_lines.append(line)


def flush_log():
    LOG_PATH.write_text("\n".join(log_lines) + "\n")


MASK64 = (1 << 64) - 1


def mix64(x):
    x = (int(x) + 0x9E3779B97F4A7C15) & MASK64
    x = (operator.xor(x, x >> 30) * 0xBF58476D1CE4E5B9) & MASK64
    x = (operator.xor(x, x >> 27) * 0x94D049BB133111EB) & MASK64
    return operator.xor(x, x >> 31) & MASK64


def point_key(R):
    if R == R.curve()(0):
        return ("inf", 0)
    return (int(ZZ(R[0])), int(ZZ(R[1])))


def is_distinguished(R, dp_bits):
    if R == R.curve()(0):
        return False
    return (int(ZZ(R[0])) & ((1 << int(dp_bits)) - 1)) == 0


def partition_index(R, seed, step_count):
    if R == R.curve()(0):
        return mix64(seed) % step_count
    point_word = operator.xor(int(ZZ(R[0])), int(ZZ(R[1])) << 1)
    return mix64(operator.xor(point_word, int(seed) << 17)) % step_count


def walk_to_distinguished(start_R, start_A, n, step_points, step_scalars, dp_bits, seed, max_steps, min_steps=1):
    R = start_R
    A = int(start_A) % int(n)
    ops = 0
    step_count = len(step_points)
    for _ in range(int(max_steps)):
        idx = partition_index(R, seed, step_count)
        R = R + step_points[idx]
        A = (A + step_scalars[idx]) % int(n)
        ops += 1
        if ops >= int(min_steps) and is_distinguished(R, dp_bits):
            return {
                "key": point_key(R),
                "point": R,
                "A": A,
                "steps": ops,
            }
    return {
        "key": None,
        "point": R,
        "A": A,
        "steps": ops,
    }


def find_prime_order_curve(bits, rng, seed):
    set_random_seed(int(seed))
    lower = ZZ(2) ** (int(bits) - 1)
    upper = ZZ(2) ** int(bits) - 1
    for prime_try in range(80):
        p = ZZ(random_prime(upper, lbound=lower))
        F = GF(p)
        a = F(-3)
        b_candidates = list(range(1, 40))
        b_candidates.extend(rng.randrange(1, int(p) - 1) for _ in range(160))
        for b_int in b_candidates:
            b = F(b_int)
            if 4 * a ** 3 + 27 * b ** 2 == 0:
                continue
            try:
                E = EllipticCurve(F, [a, b])
                n = ZZ(E.order())
            except Exception:
                continue
            if n.is_prime():
                P = E.random_point()
                while P == E(0):
                    P = E.random_point()
                return {
                    "bits_requested": int(bits),
                    "p": int(p),
                    "a": int(ZZ(a)),
                    "b": int(b_int % int(p)),
                    "n": int(n),
                    "E": E,
                    "P": P,
                    "prime_try": int(prime_try),
                }
    raise RuntimeError("could not find prime-order toy curve for %d bits" % int(bits))


def make_steps(P, n, rng, step_count):
    scalars = []
    points = []
    used = set()
    while len(scalars) < int(step_count):
        r = rng.randrange(1, int(n))
        if r in used:
            continue
        used.add(r)
        scalars.append(r)
        points.append(r * P)
    return points, scalars


def build_precompute_table(P, n, step_points, step_scalars, dp_bits, seed, rng, lane_count):
    t = int(dp_bits)
    wanted = 1 << t
    min_len = 1 << t
    max_len = 16 * min_len
    table = {}
    lanes = int(lane_count)
    lane_seeds = [
        operator.xor(int(seed), int(0x9E3779B97F4A7C15) * (lane + 1))
        for lane in range(lanes)
    ]
    lane_targets = [wanted // lanes for _ in range(lanes)]
    for lane in range(wanted % lanes):
        lane_targets[lane] += 1
    lane_counts = [0 for _ in range(lanes)]
    attempts = 0
    ops = 0
    reject_early = 0
    reject_duplicate = 0
    reject_timeout = 0
    t0 = time.time()

    while len(table) < wanted and attempts < wanted * 5000:
        attempts += 1
        lane = (attempts - 1) % lanes
        if lane_counts[lane] >= lane_targets[lane]:
            continue
        A0 = rng.randrange(0, int(n))
        endpoint = walk_to_distinguished(A0 * P, A0, n, step_points, step_scalars, t, lane_seeds[lane], max_len, min_len)
        ops += endpoint["steps"]
        if endpoint["key"] is None:
            reject_timeout += 1
            continue
        full_key = (int(lane), endpoint["key"])
        if full_key in table:
            reject_duplicate += 1
            continue
        table[full_key] = {
            "A": int(endpoint["A"]),
            "steps": int(endpoint["steps"]),
            "lane": int(lane),
        }
        lane_counts[lane] += 1

    if len(table) < wanted:
        raise RuntimeError(
            "precompute table only filled %d/%d entries after %d attempts; rejects early/dup/timeout=%d/%d/%d"
            % (len(table), wanted, attempts, reject_early, reject_duplicate, reject_timeout)
        )

    return {
        "table": table,
        "entries": len(table),
        "attempts": attempts,
        "ops": int(ops),
        "seconds": time.time() - t0,
        "min_walk_len": min_len,
        "max_walk_len": max_len,
        "reject_early": reject_early,
        "reject_duplicate": reject_duplicate,
        "reject_timeout": reject_timeout,
        "lane_count": int(lanes),
        "lane_counts": [int(x) for x in lane_counts],
        "lane_seeds": [int(x) for x in lane_seeds],
    }


def solve_with_precompute(P, Q, n, table, lane_seeds, step_points, step_scalars, dp_bits, rng, max_trials):
    W = 1 << int(dp_bits)
    max_steps = 2 * W
    online_ops = 0
    endpoint_hits = 0
    timeouts = 0
    t0 = time.time()

    for trial in range(1, int(max_trials) + 1):
        A0 = rng.randrange(0, int(n))
        b = rng.randrange(1, int(n))
        lane = rng.randrange(0, len(lane_seeds))
        lane_seed = lane_seeds[lane]
        R = A0 * P + b * Q
        A = int(A0)
        hit_this_trial = False
        for _ in range(int(max_steps)):
            idx = partition_index(R, lane_seed, len(step_points))
            R = R + step_points[idx]
            A = (A + step_scalars[idx]) % int(n)
            online_ops += 1
            if not is_distinguished(R, dp_bits):
                continue
            entry = table.get((int(lane), point_key(R)))
            if entry is None:
                continue
            hit_this_trial = True
            endpoint_hits += 1
            denom_inv = int(inverse_mod(ZZ(b), ZZ(n)))
            k = ((int(entry["A"]) - int(A)) * denom_inv) % int(n)
            verified = (k * P == Q)
            if verified:
                return {
                    "solved": True,
                    "k": int(k),
                    "verified": True,
                    "online_ops": int(online_ops),
                    "online_seconds": time.time() - t0,
                    "trials": int(trial),
                    "endpoint_hits": int(endpoint_hits),
                    "timeouts": int(timeouts),
                    "match_key": point_key(R),
                    "match_lane": int(lane),
                    "match_online_A": int(A),
                    "match_b": int(b),
                    "max_steps_per_trial": int(max_steps),
                }
        if not hit_this_trial:
            timeouts += 1
    return {
        "solved": False,
        "k": None,
        "verified": False,
        "online_ops": int(online_ops),
        "online_seconds": time.time() - t0,
        "trials": int(max_trials),
        "endpoint_hits": int(endpoint_hits),
        "timeouts": int(timeouts),
        "match_key": None,
        "match_lane": None,
        "match_online_A": None,
        "match_b": None,
        "max_steps_per_trial": int(max_steps),
    }


def corrupt_scalar_negative_control(P, Q, n, table, solved_row):
    if not solved_row.get("match_key"):
        return {"ran": False, "rejected": None}
    entry = table[(int(solved_row["match_lane"]), tuple(solved_row["match_key"]))]
    bad_A = (int(entry["A"]) + 1) % int(n)
    denom_inv = int(inverse_mod(ZZ(solved_row["match_b"]), ZZ(n)))
    bad_k = ((bad_A - int(solved_row["match_online_A"])) * denom_inv) % int(n)
    return {
        "ran": True,
        "bad_k": int(bad_k),
        "rejected": bool(bad_k * P != Q),
    }


def bsgs(P, Q, n):
    E = P.curve()
    m = int(ceil(sqrt(ZZ(n))))
    table = {}
    R = E(0)
    for j in range(m):
        table[point_key(R)] = j
        R = R + P
    stride = m * P
    gamma = Q
    giant_ops = 0
    for i in range(m + 1):
        key = point_key(gamma)
        if key in table:
            k = i * m + table[key]
            if k < int(n) and k * P == Q:
                return {
                    "solved": True,
                    "k": int(k),
                    "ops_estimate": int(m + giant_ops),
                    "memory_points": int(m),
                }
        gamma = gamma - stride
        giant_ops += 1
    return {
        "solved": False,
        "k": None,
        "ops_estimate": int(m + giant_ops),
        "memory_points": int(m),
    }


def fresh_dp_rho_baseline(P, Q, n, seed, rng, step_count):
    rho_dp_bits = max(2, int(math.ceil(int(ZZ(n).nbits()) / 4.0)))
    max_steps_per_walk = 32 * (1 << rho_dp_bits)
    max_walks = 20000
    step_scalars_a = []
    step_scalars_b = []
    step_points = []
    for _ in range(int(step_count)):
        da = rng.randrange(0, int(n))
        db = rng.randrange(0, int(n))
        if da == 0 and db == 0:
            da = 1
        step_scalars_a.append(da)
        step_scalars_b.append(db)
        step_points.append(da * P + db * Q)

    table = {}
    ops = 0
    t0 = time.time()
    seed = int(seed)
    for walk in range(1, max_walks + 1):
        a = rng.randrange(0, int(n))
        b = rng.randrange(0, int(n))
        R = a * P + b * Q
        for _ in range(max_steps_per_walk):
            idx = partition_index(R, seed, len(step_points))
            R = R + step_points[idx]
            a = (a + step_scalars_a[idx]) % int(n)
            b = (b + step_scalars_b[idx]) % int(n)
            ops += 1
            if not is_distinguished(R, rho_dp_bits):
                continue
            key = point_key(R)
            prev = table.get(key)
            if prev is not None:
                ap, bp = prev
                denom = (int(bp) - int(b)) % int(n)
                if denom == 0:
                    break
                k = ((int(a) - int(ap)) * int(inverse_mod(ZZ(denom), ZZ(n)))) % int(n)
                if k * P == Q:
                    return {
                        "solved": True,
                        "k": int(k),
                        "ops": int(ops),
                        "walks": int(walk),
                        "dp_bits": int(rho_dp_bits),
                        "stored_dps": int(len(table)),
                        "seconds": time.time() - t0,
                    }
                break
            table[key] = (int(a), int(b))
            break
    return {
        "solved": False,
        "k": None,
        "ops": int(ops),
        "walks": int(max_walks),
        "dp_bits": int(rho_dp_bits),
        "stored_dps": int(len(table)),
        "seconds": time.time() - t0,
    }


def percentile(values, pct):
    if not values:
        return None
    vals = sorted(values)
    idx = int(round((len(vals) - 1) * float(pct)))
    return vals[idx]


def run_cell(bits, args, base_seed):
    rng = random.Random(int(int(base_seed) + int(bits) * int(1009)))
    curve = find_prime_order_curve(bits, rng, int(base_seed) + int(bits) * 17)
    E = curve["E"]
    P = curve["P"]
    n = int(curve["n"])
    n_bits = int(ZZ(n).nbits())
    dp_bits = max(1, int(math.ceil(n_bits / 3.0)))
    step_count = int(args.step_count)
    step_seed = operator.xor(operator.xor(int(base_seed), int(bits) << 8), int(0xD15EA5E))

    log("")
    log("=== bits=%d p_bits=%d n_bits=%d n=%d dp_bits=%d ===" % (
        int(bits), int(ZZ(curve["p"]).nbits()), n_bits, n, dp_bits
    ))
    log("curve: y^2 = x^3 - 3x + %d over F_%d" % (curve["b"], curve["p"]))

    step_points, step_scalars = make_steps(P, n, rng, step_count)
    lane_count = min(int(args.lanes), 1 << int(dp_bits))
    pre = build_precompute_table(P, n, step_points, step_scalars, dp_bits, step_seed, rng, lane_count)
    table = pre["table"]
    lane_seeds = pre["lane_seeds"]
    log("precompute: entries=%d ops=%d attempts=%d lanes=%d seconds=%.3f rejects early/dup/timeout=%d/%d/%d" % (
        pre["entries"], pre["ops"], pre["attempts"], pre["lane_count"],
        pre["seconds"], pre["reject_early"], pre["reject_duplicate"], pre["reject_timeout"],
    ))

    rows = []
    fresh_rho_rows = []
    solved_count = 0
    negctrl = None
    bsgs_first = None
    for target_idx in range(int(args.targets)):
        secret = rng.randrange(1, n)
        Q = secret * P
        if target_idx == 0:
            bsgs_first = bsgs(P, Q, n)
            if not bsgs_first["solved"] or bsgs_first["k"] != secret:
                raise RuntimeError("BSGS baseline failed at bits=%d" % int(bits))
        sol = solve_with_precompute(
            P, Q, n, table, lane_seeds, step_points, step_scalars, dp_bits,
            rng, int(args.max_online_trials)
        )
        sol["target_index"] = int(target_idx)
        sol["secret_matches"] = bool(sol["solved"] and sol["k"] == secret)
        rows.append(sol)
        if sol["secret_matches"]:
            solved_count += 1
            if negctrl is None:
                negctrl = corrupt_scalar_negative_control(P, Q, n, table, sol)
        if target_idx < int(args.rho_baseline_targets):
            fresh = fresh_dp_rho_baseline(
                P, Q, n,
                operator.xor(step_seed, int(0xF00D0000 + target_idx)),
                rng,
                int(args.step_count),
            )
            fresh["target_index"] = int(target_idx)
            fresh["secret_matches"] = bool(fresh["solved"] and fresh["k"] == secret)
            fresh_rho_rows.append(fresh)
            if not fresh["secret_matches"]:
                raise RuntimeError("fresh rho baseline failed at bits=%d target=%d" % (int(bits), int(target_idx)))
        log("target=%02d solved=%s trials=%d online_ops=%d hits=%d secret_match=%s" % (
            target_idx, sol["solved"], sol["trials"], sol["online_ops"],
            sol["endpoint_hits"], sol["secret_matches"],
        ))

    online_ops = [r["online_ops"] for r in rows if r["solved"]]
    fresh_ops = [r["ops"] for r in fresh_rho_rows if r["solved"]]
    rho_sqrt_est = math.sqrt(math.pi * n / 2.0)
    rho_neg_est = 0.886 * math.sqrt(n)
    W = 1 << dp_bits
    summary = {
        "bits_requested": int(bits),
        "p": int(curve["p"]),
        "a": int(curve["a"]),
        "b": int(curve["b"]),
        "n": int(n),
        "n_bits": int(n_bits),
        "dp_bits": int(dp_bits),
        "walk_length_scale_W": int(W),
        "step_count": int(step_count),
        "precompute_entries": int(pre["entries"]),
        "precompute_ops": int(pre["ops"]),
        "precompute_seconds": float(pre["seconds"]),
        "precompute_attempts": int(pre["attempts"]),
        "lane_count": int(pre["lane_count"]),
        "lane_counts": [int(x) for x in pre["lane_counts"]],
        "precompute_reject_early": int(pre["reject_early"]),
        "precompute_reject_duplicate": int(pre["reject_duplicate"]),
        "precompute_reject_timeout": int(pre["reject_timeout"]),
        "coverage_lower_bound_points": int(pre["entries"] * W),
        "targets": int(args.targets),
        "solved": int(solved_count),
        "avg_online_ops": float(sum(online_ops) / len(online_ops)) if online_ops else None,
        "median_online_ops": int(percentile(online_ops, 0.5)) if online_ops else None,
        "p90_online_ops": int(percentile(online_ops, 0.9)) if online_ops else None,
        "rho_sqrt_estimate_ops": float(rho_sqrt_est),
        "rho_negation_estimate_ops": float(rho_neg_est),
        "bsgs_first_ops_estimate": int(bsgs_first["ops_estimate"]),
        "bsgs_first_memory_points": int(bsgs_first["memory_points"]),
        "fresh_rho_baseline_targets": int(len(fresh_rho_rows)),
        "fresh_rho_avg_ops": float(sum(fresh_ops) / len(fresh_ops)) if fresh_ops else None,
        "fresh_rho_median_ops": int(percentile(fresh_ops, 0.5)) if fresh_ops else None,
        "fresh_rho_speedup_online_avg": float((sum(fresh_ops) / len(fresh_ops)) / (sum(online_ops) / len(online_ops))) if fresh_ops and online_ops else None,
        "fresh_rho_amortized_speedup_after_setup": float((sum(fresh_ops)) / (pre["ops"] + sum(online_ops[:len(fresh_ops)]))) if fresh_ops and online_ops else None,
        "online_over_n_cuberoot": float((sum(online_ops) / len(online_ops)) / (n ** (1.0 / 3.0))) if online_ops else None,
        "precompute_over_n_twothirds": float(pre["ops"] / (n ** (2.0 / 3.0))),
        "storage_over_n_cuberoot": float(pre["entries"] / (n ** (1.0 / 3.0))),
        "negative_control": negctrl or {"ran": False, "rejected": None},
        "all_verified": bool(solved_count == int(args.targets) and all(r["secret_matches"] for r in rows)),
        "target_rows": rows,
        "fresh_rho_rows": fresh_rho_rows,
    }
    log("summary: solved=%d/%d avg_online_ops=%s fresh_rho_avg_ops=%s rho_neg_est=%.1f bsgs_ops=%d negctrl_rejected=%s" % (
        solved_count, int(args.targets), summary["avg_online_ops"], summary["fresh_rho_avg_ops"],
        rho_neg_est, bsgs_first["ops_estimate"], summary["negative_control"].get("rejected"),
    ))
    flush_log()
    return summary


def write_results(payload):
    serial = dict(payload)
    RESULT_JSON.write_text(json.dumps(serial, indent=2, sort_keys=True) + "\n")

    rows = payload["cells"]
    md = []
    md.append("# Round 017 EXP-033: Precomputed Distinguished-Point Pollard Rho")
    md.append("")
    md.append("Status: OBSERVATION / TOY-EVIDENCE / HEURISTIC.")
    md.append("")
    md.append("Candidate: use a target-independent distinguished-point rho table to reduce online target ECDLP cost below a fresh generic search, while charging setup and memory separately.")
    md.append("")
    md.append("Scope: generated prime-order toy curves only. This is a generic non-uniform precomputation demonstration, not index calculus and not a deployment-relevant break.")
    md.append("")
    md.append("## Reproduction")
    md.append("")
    md.append("```bash")
    md.append(payload["command"])
    md.append("```")
    md.append("")
    md.append("## Results")
    md.append("")
    md.append("| n_bits | n | dp_bits | table | precomp_ops | avg_online_ops | fresh_rho_avg | online_speedup | amortized_speedup | BSGS_ops | solved |")
    md.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        avg_online = "%.1f" % r["avg_online_ops"] if r["avg_online_ops"] is not None else "NA"
        fresh_avg = "%.1f" % r["fresh_rho_avg_ops"] if r["fresh_rho_avg_ops"] is not None else "NA"
        online_speed = "%.2fx" % r["fresh_rho_speedup_online_avg"] if r["fresh_rho_speedup_online_avg"] is not None else "NA"
        amort_speed = "%.2fx" % r["fresh_rho_amortized_speedup_after_setup"] if r["fresh_rho_amortized_speedup_after_setup"] is not None else "NA"
        md.append("| %d | %d | %d | %d | %d | %s | %s | %s | %s | %d | %d/%d |" % (
            r["n_bits"], r["n"], r["dp_bits"], r["precompute_entries"],
            r["precompute_ops"], avg_online, fresh_avg, online_speed, amort_speed,
            r["bsgs_first_ops_estimate"], r["solved"], r["targets"],
        ))
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("- OBSERVATION: the prototype recovers target logs from public `P,Q` and verifies `k*P == Q`; the solver does not use the planted scalar except for test bookkeeping.")
    md.append("- HEURISTIC: the online operation scale follows the expected `n^(1/3)` shape only at toy scale and with constants from the chosen distinguished-point rate.")
    md.append("- MODEL-BOUND: the speedup is non-uniform. The precomputed table is specific to the group, base point, walk function, and distinguished-point predicate.")
    md.append("- NEGATIVE CONTROL: corrupting the stored precomputed scalar for a successful endpoint hit must fail public verification; this catches bogus relation bookkeeping.")
    md.append("- LIMITATION: charging setup removes the attack value for a single target. The measured setup constants are visible here; at these toy sizes they can dominate the ideal `n^(2/3)` heuristic, while storage is around `n^(1/3)` points.")
    md.append("- SPEEDUP ACCOUNTING: `online_speedup` excludes setup and shows why the non-uniform model looks attractive; `amortized_speedup` charges setup over the measured fresh-rho baseline targets and is the practical cost comparison.")
    md.append("")
    md.append("## Handoff: precomputed DP rho prototype")
    md.append("")
    md.append("### Claim or task")
    md.append("Implement and measure the Bernstein-Lange precomputed distinguished-point rho mechanism on controlled toy ECDLP instances.")
    md.append("")
    md.append("### Status")
    md.append("OBSERVATION")
    md.append("")
    md.append("### Assumptions")
    md.append("- Prime-order toy short-Weierstrass curves over prime fields.")
    md.append("- Fixed target-independent walk adding only precomputed multiples of `P`.")
    md.append("- Random-walk heuristic for distinguished-point hit probabilities.")
    md.append("- Precomputation and online work are reported separately.")
    md.append("")
    md.append("### Evidence so far")
    for r in rows:
        md.append("- n_bits=%d solved %d/%d, avg_online_ops=%s, precompute_ops=%d." % (
            r["n_bits"], r["solved"], r["targets"],
            "%.1f" % r["avg_online_ops"] if r["avg_online_ops"] is not None else "NA",
            r["precompute_ops"],
        ))
    md.append("")
    md.append("### Failure modes")
    md.append("- Bad walk partitioning can create cycles or poor endpoint coverage.")
    md.append("- Constants dominate these tiny curves; do not fit asymptotics from this alone.")
    md.append("- The table is generic precomputation, so it gives no non-generic structure for prime-field ECDLP.")
    md.append("")
    md.append("### Next concrete action")
    md.append("Add an AT/time-memory product variant and a same-curve many-target amortization sweep comparing this table against VW94 shared-DP multi-target rho.")
    md.append("")
    md.append("### Artifact paths")
    md.append("- `%s`" % str(SCRIPT_PATH))
    md.append("- `%s`" % str(RESULT_JSON))
    md.append("- `%s`" % str(LOG_PATH))
    RESULT_MD.write_text("\n".join(md) + "\n")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260601)
    parser.add_argument("--bits", default="15,18,21")
    parser.add_argument("--targets", type=int, default=12)
    parser.add_argument("--max-online-trials", type=int, default=64)
    parser.add_argument("--step-count", type=int, default=20)
    parser.add_argument("--lanes", type=int, default=4)
    parser.add_argument("--rho-baseline-targets", type=int, default=6)
    return parser.parse_args()


def main():
    args = parse_args()
    bits_list = [int(x.strip()) for x in args.bits.split(",") if x.strip()]
    command = "sage %s --seed %d --bits %s --targets %d --lanes %d --rho-baseline-targets %d" % (
        os.path.relpath(str(SCRIPT_PATH), Path.cwd()),
        int(args.seed),
        ",".join(str(b) for b in bits_list),
        int(args.targets),
        int(args.lanes),
        int(args.rho_baseline_targets),
    )

    log("=" * 72)
    log("EXP-033 PRECOMPUTED DISTINGUISHED-POINT RHO")
    log("seed=%d bits=%s targets=%d" % (int(args.seed), bits_list, int(args.targets)))
    log("=" * 72)
    flush_log()

    cells = []
    for bits in bits_list:
        cells.append(run_cell(bits, args, int(args.seed)))

    payload = {
        "experiment": "round017_exp033_precomputed_dp_rho",
        "timestamp": datetime.now().isoformat(),
        "seed": int(args.seed),
        "bits": bits_list,
        "targets_per_size": int(args.targets),
        "command": command,
        "claim_status": "OBSERVATION / TOY-EVIDENCE / HEURISTIC",
        "cells": cells,
    }
    write_results(payload)
    log("")
    log("wrote %s" % RESULT_JSON)
    log("wrote %s" % RESULT_MD)
    flush_log()


if __name__ == "__main__":
    main()
