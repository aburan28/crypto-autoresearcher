"""
Post-processing: builds results/summary.json, results/baseline_manifests/,
results/seed_env_manifest.yaml, and runs/RUN-ECDLP-bbb42f-4/certificates/
from the six runs' results.json files. Required artifacts per
specification.yaml. Computes NOTHING outside cost_model.py's charging
convention; this script only aggregates numbers the runs already measured.
"""
from __future__ import annotations
import json
import os
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS = os.path.join(BASE, "runs")
RESULTS = os.path.join(BASE, "results")


def load(run_id):
    with open(os.path.join(RUNS, run_id, "results.json")) as f:
        return json.load(f)


def build_certificates():
    r4 = load("RUN-ECDLP-bbb42f-4")
    cert_dir = os.path.join(RUNS, "RUN-ECDLP-bbb42f-4", "certificates")
    os.makedirs(cert_dir, exist_ok=True)
    for outcome in r4["outcomes"]:
        bit_size = outcome["bit_size"]
        s = outcome["sssa_solve"]
        cert = {
            "certificate": {
                "kind": "discrete_log",
                "bit_size": bit_size,
                "curve": {"a": outcome["e_rand"]["a"], "b": outcome["e_rand"]["b"], "p": outcome["p"]},
                "N": outcome["special_curve"]["N"],
                "k_claimed": s["k_computed"],
                "k_true_planted": s["k_true"],
                "verified": s["certificate_verified"],
                "solved_correctly": s["solved_correctly"],
                "verifier": "driver.certificate.verify_certificate",
                "achieved_chain_len": outcome["achieved_chain_len"],
                "requested_chain_len": outcome["requested_chain_len"],
                "fallback_to_chain_len_0": outcome["fallback_to_chain_len_0"],
            }
        }
        with open(os.path.join(cert_dir, f"planted_bit{bit_size}.yaml"), "w") as f:
            yaml.safe_dump(cert, f, sort_keys=False)
    print(f"wrote {len(r4['outcomes'])} certificates to {cert_dir}")


def build_baseline_manifests():
    os.makedirs(os.path.join(RESULTS, "baseline_manifests"), exist_ok=True)
    for run_id, bit_size in [("RUN-ECDLP-bbb42f-1", 20), ("RUN-ECDLP-bbb42f-2", 24), ("RUN-ECDLP-bbb42f-3", 28)]:
        d = load(run_id)
        entries = []
        for c in d["per_curve_results"]:
            entries.append({
                "curve": {"a": c["a"], "b": c["b"], "N": c["N"], "p": d["p"]},
                "bsgs": c["baseline"]["bsgs"],
                "rho": c["baseline"]["rho"],
            })
        out_path = os.path.join(RESULTS, "baseline_manifests", f"bit{bit_size}_baselines.json")
        with open(out_path, "w") as f:
            json.dump(entries, f, indent=2, default=str)
        print(f"wrote {len(entries)} baseline entries to {out_path}")


def build_seed_env_manifest():
    seeds = {
        "RUN-ECDLP-bbb42f-1": {"description": "20-bit unplanted census", "master_seed": 20260902001},
        "RUN-ECDLP-bbb42f-2": {"description": "24-bit unplanted census", "master_seed": 20260902002},
        "RUN-ECDLP-bbb42f-3": {"description": "28-bit unplanted census", "master_seed": 20260902003},
        "RUN-ECDLP-bbb42f-4": {"description": "planted-path positive controls, all bit sizes", "master_seed": 20260902004},
        "RUN-ECDLP-bbb42f-5": {"description": "synthetic random-regular-graph null", "master_seed": 20260902005},
        "RUN-ECDLP-bbb42f-6": {"description": "exit-map consistency spot-check", "master_seed": 20260902006},
    }
    import sys
    import platform
    manifest = {
        "seeds": seeds,
        "environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "dependencies": {"sympy": __import__("sympy").__version__, "pyyaml": yaml.__version__},
        },
        "note": (
            "isogeny_step_primes = {2, 3} throughout (specification.yaml "
            "inputs.isogeny_step_primes); K_MAX (E2 embedding-degree threshold) "
            "= 6 (predicates.py); I_OVER_M modeled inversion/multiplication "
            "ratio = 8 (cost_model.py)."
        ),
    }
    out_path = os.path.join(RESULTS, "seed_env_manifest.yaml")
    with open(out_path, "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    print(f"wrote {out_path}")


def build_summary():
    summary = {"experiment_id": "EXP-ECDLP-bbb42f", "runs": {}}

    pooled_ratios = []
    pooled_certs = []
    for run_id, bit_size in [("RUN-ECDLP-bbb42f-1", 20), ("RUN-ECDLP-bbb42f-2", 24), ("RUN-ECDLP-bbb42f-3", 28)]:
        d = load(run_id)
        below_07 = 0
        found_count = 0
        for c in d["per_curve_results"]:
            r = c["min_charged_transfer_ratio"]
            if isinstance(r, (int, float)):
                pooled_ratios.append({"bit_size": bit_size, "a": c["a"], "b": c["b"], "ratio": r,
                                       "anomaly": c["anomaly"]})
                found_count += 1
                if r < 0.7:
                    below_07 += 1
        summary["runs"][run_id] = {
            "bit_size": bit_size,
            "p": d["p"],
            "curves_sampled": len(d["accepted_curves"]),
            "curves_processed": len(d["per_curve_results"]),
            "found_special_within_budget": found_count,
            "not_found_count": len(d["per_curve_results"]) - found_count,
            "ratio_below_0.7_count": below_07,
            "wall_seconds": d["wall_seconds"],
            "status": d["status"],
        }

    r4 = load("RUN-ECDLP-bbb42f-4")
    planted_all_pass = all(o["ctrl_planted_path_status"] == "PASS" for o in r4["outcomes"])
    summary["runs"]["RUN-ECDLP-bbb42f-4"] = {
        "outcomes": [
            {"bit_size": o["bit_size"], "status": o["ctrl_planted_path_status"],
             "achieved_chain_len": o["achieved_chain_len"], "requested_chain_len": o["requested_chain_len"],
             "fallback_to_chain_len_0": o["fallback_to_chain_len_0"]}
            for o in r4["outcomes"]
        ],
        "all_bit_sizes_pass": planted_all_pass,
        "wall_seconds": r4["wall_seconds"],
    }

    r5 = load("RUN-ECDLP-bbb42f-5")
    summary["runs"]["RUN-ECDLP-bbb42f-5"] = {
        "configs": r5["configs"],
        "wall_seconds": r5["wall_seconds"],
    }

    r6 = load("RUN-ECDLP-bbb42f-6")
    summary["runs"]["RUN-ECDLP-bbb42f-6"] = {
        "positive_pass": r6["result"]["metrics"]["positive_pass"],
        "negative_pass": r6["result"]["metrics"]["negative_pass"],
        "wall_seconds": r6["wall_seconds"],
    }

    # primary metrics per specification.yaml metrics.primary
    total_pooled = len(pooled_ratios)
    n_below_07 = sum(1 for r in pooled_ratios if r["ratio"] < 0.7)
    summary["primary_metrics"] = {
        "min_charged_transfer_ratio_distribution": pooled_ratios,
        "pooled_unplanted_curves": (
            summary["runs"]["RUN-ECDLP-bbb42f-1"]["curves_processed"]
            + summary["runs"]["RUN-ECDLP-bbb42f-2"]["curves_processed"]
            + summary["runs"]["RUN-ECDLP-bbb42f-3"]["curves_processed"]
        ),
        "pooled_curves_with_ratio_below_0.7": n_below_07,
        "planted_path_control_pass_all_bit_sizes": planted_all_pass,
        "note": (
            "NOT_FOUND (no ratio computed) is the outcome for every unplanted "
            "curve where no special curve was reached within the degree "
            "budget; these are excluded from the ratio distribution above by "
            "construction (there is no ratio to report), consistent with "
            "specification.yaml's own 'or NOT_FOUND' clause. Observations "
            "only; S1/F1 judgment belongs to /review-evidence, not this report."
        ),
    }

    out_path = os.path.join(RESULTS, "summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    build_certificates()
    build_baseline_manifests()
    build_seed_env_manifest()
    build_summary()
