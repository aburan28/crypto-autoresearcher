#!/usr/bin/env python3
"""EXP-MLKEM-007 run packaging.

Builds the immutable run record for one RUN-ID: summary.json, manifest.yaml,
and the byte-identical `docs/evidence-and-reproducibility.md` aliases
(raw-result.json, stdout.log, stderr.log) for the specification-named files
(raw.json, stdout.txt, stderr.txt).

Also runs the independent planted-layer re-verification: the planted p=3 layer
of every scored instance is re-derived from the recorded seed derivation path
using the sampler alone, with no access to any scoring, fusion or covariance
state, and compared against the value the scoring run recorded.

Standard library only.  Never overwrites an existing manifest.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mlwe_sampler import gen_instance, layer, derivation_path
import orbit_scoring as osc

ROOT = "/home/user/crypto-autoresearcher"
EXP = "experiments/EXP-MLKEM-007"


# ------------------------------------------------------------- tiny YAML

def _scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if s == "" or any(c in s for c in ":#{}[],&*?|-<>=!%@`\"'\n") or \
            s.strip() != s or s.lower() in ("null", "true", "false", "yes", "no"):
        return json.dumps(s)
    return s


def to_yaml(obj, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(obj, dict):
        if not obj:
            return pad + "{}\n"
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append("%s%s:\n" % (pad, k))
                out.append(to_yaml(v, indent + 1))
            elif isinstance(v, (dict, list)):
                out.append("%s%s: %s\n" % (pad, k, "{}" if isinstance(v, dict) else "[]"))
            else:
                out.append("%s%s: %s\n" % (pad, k, _scalar(v)))
        return "".join(out)
    if isinstance(obj, list):
        if not obj:
            return pad + "[]\n"
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                out.append("%s-\n" % pad)
                out.append(to_yaml(v, indent + 1))
            else:
                out.append("%s- %s\n" % (pad, _scalar(v)))
        return "".join(out)
    return pad + _scalar(obj) + "\n"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


# --------------------------------------------- independent re-verification

def verify_planted_layers(raw):
    """Re-derive planted p=3 layers from seeds using the sampler only."""
    checks = []
    side = raw.get("orbit_scores_file")
    recs = []
    if side:
        p = os.path.join(ROOT, side["path"])
        if os.path.exists(p):
            with open(p) as fh:
                blob = json.load(fh)
            recs = [("training", r) for r in blob.get("training", [])] + \
                   [("held_out", r) for r in blob.get("held_out", [])]
            cands = [tuple(c) for c in blob["candidates"]]
    if not recs:
        return {"kind": "none", "checked": 0,
                "note": "run records no per-instance planted-layer claim"}
    n = raw["config"]["ring_sizes"][0]
    d_shift = raw["config"]["d_shift"][str(n)]
    guess_block = osc.guess_block_indices(n, d_shift)
    ok = True
    for split, r in recs:
        inst = gen_instance(n, r["seed"], raw["config"]["module_rank_k"])
        expect = tuple(layer(inst.s[0][i]) for i in guess_block)
        rec_layer = tuple(r["correct_layer"])
        idx_ok = cands[r["correct_ci"]] == expect
        h = hashlib.sha256(json.dumps([inst.s[0], inst.s[1]]).encode()).hexdigest()
        good = (expect == rec_layer) and idx_ok and h == r["secret_hash"]
        ok = ok and good
        checks.append({"split": split, "seed": r["seed"],
                       "derivation_path": derivation_path(n, r["seed"], "secret_s"),
                       "recomputed_layer": list(expect),
                       "recorded_layer": list(rec_layer),
                       "candidate_index_consistent": idx_ok,
                       "secret_hash_matches": h == r["secret_hash"],
                       "pass": good})
    return {"kind": "none",
            "planted_layer_reverification": {
                "verifier": "independent-recompute (mlwe_sampler only; no "
                            "scoring, fusion or covariance state)",
                "verifier_commit": git("rev-parse", "HEAD"),
                "instances_checked": len(checks), "all_pass": ok,
                "checks": checks},
            "note": "No discrete-log solve and no factor-base relation is "
                    "claimed by this experiment, so certificate.kind is none "
                    "(docs/claims-and-verification.md).  The planted-layer "
                    "recovery statistics are nevertheless re-verified above."}


# ---------------------------------------------------------------- summary

def build_summary(stage, raw):
    s = {"experiment_id": "EXP-MLKEM-007", "run_id": raw.get("run_id"),
         "stage": stage, "claim_tier": "toy"}
    if stage == "controls":
        ka = raw.get("ctrl_known_answer", {})
        s["controls"] = {
            "CTRL-KNOWN-ANSWER": {
                "reference_vector_count": ka.get("reference_vector_count"),
                "top1_recovery_rate_training": ka.get("top1_recovery_rate"),
                "pass": ka.get("pass")},
            "CTRL-COVARIANCE-MODEL": dict(
                ("n=%s" % k, {"pass": v.get("pass"),
                              "exact_signed_permutation_structure":
                                  v.get("exact_signed_permutation_structure"),
                              "max_chi_square": max(
                                  (e["chi_square"] for e in v["per_element"]),
                                  default=None),
                              "chi_square_critical": v["per_element"][0][
                                  "chi_square_critical_alpha_0.001"]
                              if v.get("per_element") else None})
                for k, v in (raw.get("ctrl_covariance_model") or {}).items()),
            "CTRL-EXACT-EQUALITY": {
                "pass": raw.get("ctrl_exact_equality_pass"),
                "residual_checks": sum(e["residual_checks"]
                                       for e in raw.get("ctrl_exact_equality", [])),
                "phase_index_checks": sum(e["phase_index_checks"]
                                          for e in raw.get("ctrl_exact_equality", [])),
                "weight_checks": sum(e["weight_checks"]
                                     for e in raw.get("ctrl_exact_equality", [])),
                "float_max_relative_deviation": max(
                    (e["float_max_relative_deviation"]
                     for e in raw.get("ctrl_exact_equality", [])), default=None)},
            "CTRL-SEED-DISCIPLINE": raw.get("ctrl_seed_discipline"),
        }
        s["lll"] = {
            "dimension": (list(raw["lll_stats"].values())[0]["dimension"]
                          if raw.get("lll_stats") else None),
            "instances_reduced": len(raw.get("lll_stats", {})),
            "mean_seconds": (sum(v["lll_seconds"] for v in raw["lll_stats"].values())
                             / len(raw["lll_stats"])) if raw.get("lll_stats") else None,
            "independent_exact_verification":
                raw.get("lll_independent_verification_seed_1"),
        }
        s["pool_norms"] = (raw.get("ctrl_known_answer") or {}).get("pool_norm_summary")
        s["n64_feasibility_probe"] = raw.get("n64_feasibility_probe")
    elif stage == "gate32":
        s["orbit_subset_selection"] = raw.get("orbit_subset_selection")
        s["gate_decision"] = raw.get("gate_decision")
        s["m50_held_out"] = dict((k, v["m50_held_out"])
                                 for k, v in raw.get("fusion_results", {}).items())
        mref = str(raw["config"]["reference_vector_count"])
        s["effective_rank_at_reference_vector_count"] = dict(
            (k, {"training_r_eff": v[mref]["training_r_eff"],
                 "held_out_r_eff": v[mref]["held_out_r_eff"]})
            for k, v in raw.get("covariance_report", {}).items())
        import run_experiment as RE
        ctx = raw.get("charged_work_context", {})
        cwl = {}
        for k, v in raw.get("fusion_results", {}).items():
            m50 = v.get("m50_held_out")
            m_op = m50 if m50 else raw["config"]["reference_vector_count"]
            cwl[k] = {"m50_held_out": m50,
                      "reached_operating_point": m50 is not None,
                      "operating_point_vectors": m_op,
                      "total_charged_work_at_operating_point":
                          RE.charged_work(k, m_op, ctx)["total_charged_work"]}
        s["charged_work"] = cwl
        s["charged_work_note"] = (
            "Recomputed from the recorded charged_work_context with the frozen "
            "charged_work() function; RUN-MLKEM-026's raw.json lost the "
            "per-rule table to an output key collision (recorded anomaly). "
            "Cross-checked against gate_decision.criteria in the same file.")
        s["ctrl_seed_discipline"] = raw.get("ctrl_seed_discipline")
        s["heur_001_statistics"] = raw.get("heur_001_statistics")
    elif stage == "full64":
        s["n64"] = {k: raw.get(k) for k in
                    ("dimension", "elapsed_seconds", "aborted_reason",
                     "seeds_with_completed_reduction", "seeds_required",
                     "last_attempted_seed", "last_attempt_seconds")}
        s["ctrl_seed_discipline"] = raw.get("ctrl_seed_discipline")
    elif stage == "cancelled":
        s["cancellation"] = raw.get("cancellation")
    elif stage == "analysis":
        s["outcome_classification"] = raw.get("outcome_classification")
        s["ctrl_shuffled_orbit_labels"] = raw.get("ctrl_shuffled_orbit_labels")
        s["artifacts_written"] = raw.get("artifacts_written")
    s["timing"] = raw.get("timing")
    s["resources"] = raw.get("resources")
    s["charged_work_counters"] = raw.get("charged_work")\
        if stage in ("controls", "full64") else raw.get("charged_work_context")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--status", required=True)
    ap.add_argument("--reason", default=None)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--resolved-model", required=True)
    ap.add_argument("--cancellation-json", default=None)
    args = ap.parse_args()

    rd = os.path.join(ROOT, EXP, "runs", args.run_id)
    os.makedirs(rd, exist_ok=True)
    mpath = os.path.join(rd, "manifest.yaml")
    if os.path.exists(mpath):
        sys.exit("REFUSING to overwrite immutable run record: %s" % mpath)

    rawp = os.path.join(rd, "raw.json")
    if args.cancellation_json:
        with open(args.cancellation_json) as fh:
            raw = json.load(fh)
        with open(rawp, "w") as fh:
            json.dump(raw, fh, indent=1, sort_keys=True)
    else:
        with open(rawp) as fh:
            raw = json.load(fh)

    cert = verify_planted_layers(raw) if args.stage == "gate32" else {
        "kind": "none",
        "note": "pure measurement run: no discrete-log solve and no "
                "factor-base relation is claimed (docs/claims-and-verification.md)"}

    summary = build_summary(args.stage, raw)
    with open(os.path.join(rd, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True, default=str)

    # docs/evidence-and-reproducibility.md aliases (byte-identical copies)
    for src, dst in (("raw.json", "raw-result.json"),
                     ("stdout.txt", "stdout.log"),
                     ("stderr.txt", "stderr.log")):
        sp = os.path.join(rd, src)
        if os.path.exists(sp):
            shutil.copyfile(sp, os.path.join(rd, dst))

    with open(os.path.join(rd, "environment.json")) as fh:
        env = json.load(fh)

    artifacts = {}
    for fn in sorted(os.listdir(rd)):
        p = os.path.join(rd, fn)
        if os.path.isfile(p) and fn != "manifest.yaml":
            artifacts["%s/runs/%s/%s" % (EXP, args.run_id, fn)] = {
                "sha256": sha256_file(p), "bytes": os.path.getsize(p)}

    man = {
        "run": {
            "id": args.run_id,
            "experiment_id": "EXP-MLKEM-007",
            "hypothesis_id": "H-MLKEM-007",
            "goal_id": "GOAL-MLKEM-001",
            "task_id": "TASK-20260727-012",
            "purpose": args.purpose,
            "claim_tier": "toy",
            "status": args.status,
            "stage": args.stage,
            "code": {
                "commit": env["git"]["commit"],
                "branch": env["git"]["branch"],
                "dirty": env["git"]["dirty"],
                "dirty_paths": env["git"]["dirty_paths"],
                "command_file": "%s/runs/%s/command.txt" % (EXP, args.run_id),
                "command": open(os.path.join(rd, "command.txt")).read()
                    .strip().splitlines()[-1],
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": args.resolved_model,
                "reasoning_effort": None,
                "fallback_used": True,
                "fallback_reason":
                    "orchestration/model-policies.yaml names GPT-5.6 policy "
                    "aliases; this Claude Code harness cannot resolve them and "
                    "subagents run Claude models (CLAUDE.md, Model policy note). "
                    "The handoff sets fallback_allowed: false, so the "
                    "substitution is recorded as a protocol deviation rather "
                    "than treated as authorised.",
                "degraded_allowed": False,
                "degraded_requirements": [],
                "model_verified": False,
                "model_verification_note":
                    "python3 -m orchestration.adapter doctor --probe was not "
                    "run for this identifier",
                "adapter_version": None,
            },
            "environment": env,
            "inputs": {
                "parameters": raw.get("config"),
                "seed_policy": "30 frozen seeds per ring size, 1-15 training / "
                               "16-30 held-out, split before any covariance "
                               "estimation, subset selection or threshold "
                               "pinning",
                "seed_derivation": "SHA256('EXP-MLKEM-007|n=<n>|seed=<seed>|"
                                   "<purpose>') -> random.Random; purposes: "
                                   "public_matrix_A, secret_s, error_e, "
                                   "control_signed_permutations, "
                                   "shuffled_orbit_labels",
                "other_randomness_sources": "none",
            },
            "timing": raw.get("timing"),
            "resources": {
                "peak_rss_bytes": (raw.get("resources") or {}).get("peak_rss_bytes"),
                "cpu_seconds": (raw.get("resources") or {}).get("cpu_seconds"),
                "wall_clock_limit_seconds": 1800,
                "memory_limit_bytes": 4 * (1 << 30),
                "processes": 1,
                "network_operations": 0,
            },
            "result": {
                "metrics": summary,
                "valid": args.status == "completed_valid",
                "invalid_reason": args.reason,
                "certificate": cert,
            },
            "artifacts": artifacts,
        }
    }
    with open(mpath, "w") as fh:
        fh.write("# EXP-MLKEM-007 run manifest -- immutable\n")
        fh.write(to_yaml(man))
    print("wrote %s" % mpath)
    print(json.dumps({"artifacts": sorted(artifacts)}, indent=1))


if __name__ == "__main__":
    main()
