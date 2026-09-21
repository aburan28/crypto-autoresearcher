"""
Main entry point for EXP-ECDLP-bbb42f. Required artifact per
specification.yaml required_artifacts. Invoke as:

    python3 -m driver.isogeny_transfer_census <RUN-ID>

from experiments/EXP-ECDLP-bbb42f/, where <RUN-ID> is one of
RUN-ECDLP-bbb42f-{1..6}. Each invocation is bounded independently by the
declared per-run wall-clock budget (specification.yaml budget.
wall_clock_seconds_per_run = 3600) and writes its own immutable run
directory under runs/<RUN-ID>/.
"""
from __future__ import annotations
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from driver.sampler import sample_unplanted_curves
from driver.graph_search import bounded_isogeny_search, degree_budget_steps
from driver.baselines import pollard_rho_negation, bsgs_dlp
from driver.certificate import verify_certificate
from driver.cost_model import opcounter_to_group_ops, to_group_op_equivalents
from driver.ecc import seeded_rng, random_point, scalar_mult
from driver.predicates import K_MAX
from driver.planted import construct_planted_instance
from driver.sssa import sssa_solve
from driver.rrg_null import run_rrg_null
from driver.exitmap import is_self_map
from driver.sampler import j_invariant
from driver.manifest import write_manifest, write_command_txt, write_environment_json, write_results_json

import math

EXPERIMENT_ID = "EXP-ECDLP-bbb42f"
RUNS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs")
CERTS_DIR_NAME = "certificates"

MATCHED_RHO_MODEL = lambda N: 0.886 * math.sqrt(N)  # noqa: E731  (modeled, per spec)
MATCHED_BSGS_MODEL = lambda N: 2 * math.sqrt(N)     # noqa: E731  (modeled, per spec)


def _log(lines, msg):
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"[{ts}] {msg}"
    print(line)
    lines.append(line)


def per_curve_baseline(a, b, p, N, rng):
    P = random_point(a, b, p, rng)
    while P == (0, 0) or P[1] == 0:
        P = random_point(a, b, p, rng)
    k_true = rng.randrange(1, N)
    Q = scalar_mult(k_true, P, a, p)

    k_bsgs, ctr_bsgs, m = bsgs_dlp(P, Q, a, N, p)
    bsgs_ok = verify_certificate(k_bsgs, P, Q, a, p) and k_bsgs == k_true

    k_rho, steps_rho, ctr_rho = pollard_rho_negation(P, Q, a, N, p, seeded_rng(a, b, p, "rho"))
    rho_ok = verify_certificate(k_rho, P, Q, a, p)

    return {
        "P": P, "Q": Q, "k_true": k_true,
        "bsgs": {"k": k_bsgs, "certificate_verified": bool(bsgs_ok),
                 "measured_group_ops": opcounter_to_group_ops(ctr_bsgs),
                 "measured_field_mults": ctr_bsgs.field_mults, "measured_field_invs": ctr_bsgs.field_invs,
                 "modeled_2sqrtN": MATCHED_BSGS_MODEL(N)},
        "rho": {"k": k_rho, "certificate_verified": bool(rho_ok),
                "steps": steps_rho,
                "measured_group_ops": opcounter_to_group_ops(ctr_rho),
                "measured_field_mults": ctr_rho.field_mults, "measured_field_invs": ctr_rho.field_invs,
                "modeled_0p886sqrtN": MATCHED_RHO_MODEL(N)},
    }


def run_unplanted_census(run_id: str, bit_size: int, master_seed: int, count: int,
                          run_time_budget: float, per_curve_search_budget: float = 90.0):
    t_start = time.time()
    log_lines = []
    _log(log_lines, f"{run_id}: sampling >= {count} unplanted curves at {bit_size} bits, master_seed={master_seed}")

    p, accepted, tally, attempts = sample_unplanted_curves(bit_size, master_seed, count, K_MAX)
    _log(log_lines, f"{run_id}: sampled p={p}, accepted={len(accepted)}, attempts={attempts}, tally={tally}")

    per_curve_results = []
    halted = False
    dropped_curves = []
    for idx, c in enumerate(accepted):
        if time.time() - t_start > run_time_budget - 30:
            _log(log_lines, f"{run_id}: HALTED_ON_BUDGET before curve {idx} (a={c['a']},b={c['b']})")
            dropped_curves.append({"index": idx, "a": c["a"], "b": c["b"], "reason": "run_time_budget exhausted"})
            halted = True
            continue

        max_steps = degree_budget_steps(c["N"])
        search = bounded_isogeny_search(
            c["a"], c["b"], p, c["N"], K_MAX,
            max_steps=max_steps, max_nodes=20000,
            time_budget_seconds=per_curve_search_budget,
        )
        baseline = per_curve_baseline(c["a"], c["b"], p, c["N"], seeded_rng(master_seed, bit_size, "baseline", idx))

        ratio = None
        c_path_group_ops = None
        c_special_note = None
        anomaly = None
        if search["status"] == "FOUND":
            ell = search["min_ell"]
            c_path_group_ops = to_group_op_equivalents(
                search["field_ops"]["field_mults"], search["field_ops"]["field_invs"]
            )
            cls = search["hit"]["classification"]
            if cls["e1_anomalous"]:
                anomaly = ("IMPOSSIBLE_PER_TATE: an unplanted E1 hit occurred; sampling rule "
                           "explicitly excludes N==p, so this indicates a sampler or predicate bug "
                           "and must be investigated before any ratio is trusted")
            elif cls["e2_low_embedding_degree"]:
                c_special_note = (
                    "MODELED (not measured): no MOV/Frey-Ruck pairing solver is implemented in this "
                    "driver (see implementation.md protocol_deviations); C_special is estimated only "
                    f"as a placeholder order-of-magnitude via L_p^k(1/3), k={cls['embedding_degree_k']}, "
                    "and this instance is flagged for Coordinator attention rather than silently "
                    "counted toward S1/F1."
                )
                anomaly = "E2_HIT_WITHOUT_SOLVER: " + c_special_note
            matched_rho = MATCHED_RHO_MODEL(c["N"])
            if c_special_note is None and c_path_group_ops is not None:
                ratio = c_path_group_ops / matched_rho
        else:
            ratio = "NOT_FOUND"

        per_curve_results.append({
            "index": idx, "a": c["a"], "b": c["b"], "N": c["N"],
            "classification_at_ell0": c["classification"],
            "search": {k: v for k, v in search.items() if k != "hit"} | {"hit": search.get("hit")},
            "baseline": {k: v for k, v in baseline.items() if k in ("bsgs", "rho")},
            "min_charged_transfer_ratio": ratio,
            "anomaly": anomaly,
        })

    wall = time.time() - t_start
    status = "halted_on_budget" if halted else "completed_valid"
    result = {
        "status": status,
        "valid": not halted or len(per_curve_results) > 0,
        "invalid_reason": None,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "metrics": {
            "curves_sampled": len(accepted),
            "curves_processed": len(per_curve_results),
            "curves_dropped_for_budget": len(dropped_curves),
            "fraction_ratio_below_1": None,
        },
    }
    return {
        "p": p, "accepted_curves": accepted, "tally": tally, "attempts": attempts,
        "per_curve_results": per_curve_results, "dropped_curves": dropped_curves,
        "wall_seconds": wall, "status": status, "log_lines": log_lines, "result": result,
    }


def run_planted_controls(run_id: str, master_seed: int, bit_sizes, run_time_budget: float):
    t_start = time.time()
    log_lines = []
    outcomes = []
    for bit_size in bit_sizes:
        if time.time() - t_start > run_time_budget - 60:
            outcomes.append({"bit_size": bit_size, "status": "HALTED_ON_BUDGET"})
            continue
        _log(log_lines, f"{run_id}: constructing planted E1 instance at {bit_size} bits (requesting chain_len=4; see planted.py lemmas for when this falls back to 0)")
        inst = construct_planted_instance(bit_size, master_seed, chain_len=4, k_max=K_MAX)
        _log(log_lines, f"{run_id}: bit_size={bit_size} achieved_chain_len={inst['achieved_chain_len']} fallback={inst['fallback_to_chain_len_0']}")
        p = inst["p"]
        e_rand = inst["e_rand"]
        special_N = inst["special_curve"]["N"]

        # harness: run it blind, as if E_rand were an unplanted-looking curve
        max_steps = degree_budget_steps(special_N)
        search = bounded_isogeny_search(e_rand["a"], e_rand["b"], p, special_N, K_MAX,
                                         max_steps=max_steps, max_nodes=20000, time_budget_seconds=60)
        recovered = search["status"] == "FOUND" and search["min_ell"] == 0 and search["hit"]["classification"]["e1_anomalous"]

        rng = seeded_rng(master_seed, bit_size, "planted-dlp")
        P = random_point(e_rand["a"], e_rand["b"], p, rng)
        while P[1] == 0:
            P = random_point(e_rand["a"], e_rand["b"], p, rng)
        k_true = rng.randrange(1, special_N)
        Q = scalar_mult(k_true, P, e_rand["a"], p)

        solved = False
        cert_ok = False
        k_computed = None
        diag = None
        try:
            k_computed, diag = sssa_solve(P[0], P[1], Q[0], Q[1], e_rand["a"], e_rand["b"], p)
            cert_ok = verify_certificate(k_computed, P, Q, e_rand["a"], p)
            solved = cert_ok and k_computed == k_true
        except Exception as e:
            diag = {"error": str(e)}

        outcomes.append({
            "bit_size": bit_size, "p": p,
            "special_curve": inst["special_curve"], "e_rand": e_rand,
            "requested_chain_len": inst["requested_chain_len"], "achieved_chain_len": inst["achieved_chain_len"],
            "fallback_to_chain_len_0": inst["fallback_to_chain_len_0"],
            "forward_degree": inst["forward_degree"],
            "restarts_used": inst["restarts_used"],
            "harness_recovered_path": recovered, "min_ell_recovered": search.get("min_ell"),
            "sssa_solve": {"k_true": k_true, "k_computed": k_computed, "certificate_verified": cert_ok,
                           "solved_correctly": solved, "diagnostics": diag},
            "ctrl_planted_path_status": "PASS" if (recovered and solved) else "FAIL",
        })
        _log(log_lines, f"{run_id}: bit_size={bit_size} recovered={recovered} solved={solved}")

    wall = time.time() - t_start
    all_pass = all(o.get("ctrl_planted_path_status") == "PASS" for o in outcomes)
    status = "completed_valid" if all_pass and len(outcomes) == len(bit_sizes) else \
        ("halted_on_budget" if len(outcomes) < len(bit_sizes) else "completed_invalid")
    result = {
        "status": status, "valid": status == "completed_valid",
        "invalid_reason": None if status == "completed_valid" else
        "CTRL-PLANTED-PATH did not pass at every tested bit size (INV-PLANTED-VOID applies to the whole harness)",
        "certificate": {"kind": "discrete_log", "verified": all_pass, "verifier": "certificate.verify_certificate"},
        "metrics": {"all_planted_controls_pass": all_pass},
    }
    return {"outcomes": outcomes, "wall_seconds": wall, "status": status, "log_lines": log_lines, "result": result}


def run_null_rrg(run_id: str, master_seed: int, run_time_budget: float):
    t_start = time.time()
    log_lines = []
    configs = [
        {"n": 2000, "s": 3, "d": 3, "num_starts": 2000},
        {"n": 8000, "s": 5, "d": 3, "num_starts": 2000},
        {"n": 30000, "s": 8, "d": 3, "num_starts": 2000},
    ]
    results = []
    for cfg in configs:
        rng = seeded_rng(master_seed, cfg["n"], cfg["s"])
        res = run_rrg_null(cfg["n"], cfg["s"], cfg["d"], cfg["num_starts"], rng)
        results.append(res)
        _log(log_lines, f"{run_id}: n={cfg['n']} s={cfg['s']} ks_distance={res['ks_distance']:.4f}")
    wall = time.time() - t_start
    result = {
        "status": "completed_valid", "valid": True, "invalid_reason": None,
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "metrics": {"configs": len(results), "ks_distances": [r["ks_distance"] for r in results]},
    }
    return {"configs": results, "wall_seconds": wall, "status": "completed_valid", "log_lines": log_lines, "result": result}


def run_exitmap_spotcheck(run_id: str, master_seed: int, run_time_budget: float):
    """Dedicated exit-map consistency spot-check: positive controls (known
    isomorphic curves via the standard twist scaling (a,b) -> (u^4 a, u^6 b),
    which MUST be flagged as self-maps) and negative controls (independently
    sampled distinct curves, which MUST NOT)."""
    t_start = time.time()
    log_lines = []
    from driver.sampler import field_prime_for_bits
    p = field_prime_for_bits(20)
    rng = seeded_rng(master_seed, "exitmap-spotcheck")

    positive_checks = []
    for i in range(30):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * a**3 + 27 * b * b) % p == 0:
            continue
        u = rng.randrange(2, p)
        a2 = (pow(u, 4, p) * a) % p
        b2 = (pow(u, 6, p) * b) % p
        flagged = is_self_map(a, b, a2, b2, p)
        positive_checks.append({"a": a, "b": b, "a2": a2, "b2": b2, "u": u, "correctly_flagged": flagged})

    negative_checks = []
    for i in range(30):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        a2 = rng.randrange(1, p)
        b2 = rng.randrange(1, p)
        if (4 * a**3 + 27 * b * b) % p == 0 or (4 * a2**3 + 27 * b2 * b2) % p == 0:
            continue
        if j_invariant(a, b, p) == j_invariant(a2, b2, p):
            continue  # accidental collision; not a valid negative control instance
        flagged = is_self_map(a, b, a2, b2, p)
        negative_checks.append({"a": a, "b": b, "a2": a2, "b2": b2, "correctly_not_flagged": not flagged})

    pos_pass = all(c["correctly_flagged"] for c in positive_checks)
    neg_pass = all(c["correctly_not_flagged"] for c in negative_checks)
    _log(log_lines, f"{run_id}: positive controls {sum(c['correctly_flagged'] for c in positive_checks)}/{len(positive_checks)}, "
                     f"negative controls {sum(c['correctly_not_flagged'] for c in negative_checks)}/{len(negative_checks)}")

    wall = time.time() - t_start
    status = "completed_valid" if (pos_pass and neg_pass) else "completed_invalid"
    result = {
        "status": status, "valid": pos_pass and neg_pass,
        "invalid_reason": None if (pos_pass and neg_pass) else "exit-map classifier failed a positive or negative control",
        "certificate": {"kind": "none", "verified": None, "verifier": None},
        "metrics": {"positive_pass": pos_pass, "negative_pass": neg_pass,
                    "n_positive": len(positive_checks), "n_negative": len(negative_checks)},
    }
    return {"positive_checks": positive_checks, "negative_checks": negative_checks,
            "wall_seconds": wall, "status": status, "log_lines": log_lines, "result": result}


RUN_TABLE = {
    "RUN-ECDLP-bbb42f-1": lambda: run_unplanted_census("RUN-ECDLP-bbb42f-1", 20, 20260902001, 20, 3600),
    "RUN-ECDLP-bbb42f-2": lambda: run_unplanted_census("RUN-ECDLP-bbb42f-2", 24, 20260902002, 20, 3600),
    "RUN-ECDLP-bbb42f-3": lambda: run_unplanted_census("RUN-ECDLP-bbb42f-3", 28, 20260902003, 20, 3600),
    "RUN-ECDLP-bbb42f-4": lambda: run_planted_controls("RUN-ECDLP-bbb42f-4", 20260902004, (20, 24, 28), 3600),
    "RUN-ECDLP-bbb42f-5": lambda: run_null_rrg("RUN-ECDLP-bbb42f-5", 20260902005, 3600),
    "RUN-ECDLP-bbb42f-6": lambda: run_exitmap_spotcheck("RUN-ECDLP-bbb42f-6", 20260902006, 3600),
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in RUN_TABLE:
        print(f"usage: python3 -m driver.isogeny_transfer_census <{'|'.join(RUN_TABLE)}>")
        sys.exit(1)
    run_id = sys.argv[1]
    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    command = f"python3 -m driver.isogeny_transfer_census {run_id}"
    write_command_txt(run_dir, command)
    write_environment_json(run_dir)

    t0 = time.time()
    started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    outcome = RUN_TABLE[run_id]()
    finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    wall = time.time() - t0

    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write("\n".join(outcome["log_lines"]) + "\n")
    open(os.path.join(run_dir, "stderr.log"), "w").close()

    write_results_json(run_dir, {k: v for k, v in outcome.items() if k != "log_lines"})

    write_manifest(
        run_dir, run_id, EXPERIMENT_ID, command,
        inputs={"run_id": run_id},
        timing={"started_at": started_at, "finished_at": finished_at, "wall_seconds": wall},
        resources={"peak_rss_bytes": None, "cpu_seconds": wall},
        result=outcome["result"],
        artifacts={"results_json": "results.json", "stdout_log": "stdout.log"},
    )
    print(f"{run_id}: status={outcome['status']} wall={wall:.1f}s -> {run_dir}")


if __name__ == "__main__":
    main()
