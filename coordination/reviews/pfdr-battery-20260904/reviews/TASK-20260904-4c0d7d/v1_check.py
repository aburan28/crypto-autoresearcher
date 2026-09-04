#!/usr/bin/env python3
"""V1: run-set validity, manifest schema, seed and prime integrity.

Independent re-check by the Validator for TASK-20260904-4c0d7d.
Reads only experiments/EXP-PFDR-fd901a/**; writes nothing outside stdout.
"""
import hashlib
import json
import os
import sys

import yaml

ROOT = "/home/user/crypto-autoresearcher"
EXP = os.path.join(ROOT, "experiments/EXP-PFDR-fd901a")
RUNS = os.path.join(EXP, "runs")
REQUIRED = ["manifest.yaml", "command.txt", "environment.json",
            "stdout.log", "stderr.log", "raw-result.json"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out = {}
    run_dirs = sorted(os.listdir(RUNS))
    out["run_dirs"] = run_dirs
    per_run = {}
    for rd in run_dirs:
        d = os.path.join(RUNS, rd)
        rec = {}
        present = sorted(os.listdir(d))
        rec["files_present"] = present
        rec["required_present"] = all(f in present for f in REQUIRED)
        rec["extra_files"] = [f for f in present
                              if f not in REQUIRED + ["checksums.sha256"]]
        # checksum verification
        cks = {}
        with open(os.path.join(d, "checksums.sha256")) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                digest, name = line.split(None, 1)
                cks[name.strip()] = digest
        mismatches = []
        for name, digest in cks.items():
            actual = sha256(os.path.join(d, name))
            if actual != digest:
                mismatches.append({"file": name, "recorded": digest,
                                   "recomputed": actual})
        rec["checksum_files_listed"] = sorted(cks)
        rec["checksum_mismatches"] = mismatches
        rec["files_not_in_checksums"] = [f for f in present
                                         if f not in cks
                                         and f != "checksums.sha256"]
        with open(os.path.join(d, "manifest.yaml")) as fh:
            man = yaml.safe_load(fh)["run"]
        p = man["inputs"]["parameters"]
        rec["run_id"] = man["id"]
        rec["experiment_id"] = man["experiment_id"]
        rec["status"] = man["status"]
        rec["commit"] = man["code"]["commit"]
        rec["dirty"] = man["code"].get("dirty")
        rec["command_manifest"] = man["code"]["command"]
        with open(os.path.join(d, "command.txt")) as fh:
            rec["command_txt"] = fh.read().strip()
        rec["command_matches"] = rec["command_manifest"] == rec["command_txt"]
        src = man["code"].get("source", {}).get("files", {})
        rec["run_experiment_sha256"] = src.get(
            "experiments/EXP-PFDR-fd901a/run_experiment.py", {}).get("sha256")
        rec["source_file_count"] = man["code"].get("source", {}).get("file_count")
        rec["all_pinned"] = man["code"].get("source", {}).get("all_pinned")
        rec["meter_per_file_sha256"] = p.get("meter", {}).get("per_file_sha256")
        rec["meter_snapshot_commit"] = p.get("meter", {}).get("snapshot_commit")
        rec["selftest"] = p.get("meter", {}).get("selftest_in_this_lineage")
        rec["prime"] = p.get("prime")
        rec["prime_bits"] = p.get("prime_bits")
        rec["prime_check"] = p.get("prime_check")
        rec["degrees"] = p.get("degrees")
        rec["window"] = p.get("window")
        rec["curve_seeds"] = p.get("curve_seeds")
        rec["target_seeds"] = p.get("target_seeds")
        rec["null_seeds"] = p.get("null_seeds")
        rec["secondary_curve_seeds"] = p.get("secondary_curve_seeds")
        rec["secondary_target_seeds"] = p.get("secondary_target_seeds")
        rec["secondary_B"] = p.get("secondary_B")
        rec["posctrl_curve_seeds"] = p.get("posctrl_curve_seeds")
        rec["posctrl_target_seeds"] = p.get("posctrl_target_seeds")
        rec["stage"] = p.get("stage")
        rec["timing_source"] = man["timing"].get("timing_source")
        rec["timing"] = {k: man["timing"].get(k)
                         for k in ("started_at", "finished_at", "wall_seconds")}
        rec["resources"] = man.get("resources")
        rec["inference"] = man.get("inference")
        rec["executor_session_inference"] = p.get("executor_session_inference")
        rec["environment"] = man.get("environment")
        rec["result_valid"] = man["result"].get("valid")
        rec["result_certificate"] = man["result"].get("certificate")
        rec["stderr_bytes"] = os.path.getsize(os.path.join(d, "stderr.log"))
        rec["metrics_draw_count"] = man["result"]["metrics"].get("draw_count")
        rec["metrics_valid_draws"] = man["result"]["metrics"].get("valid_draws")
        rec["metrics_draws_per_arm"] = man["result"]["metrics"].get("draws_per_arm")
        rec["planted_certificates_total"] = man["result"]["metrics"].get(
            "planted_certificates_total")
        rec["planted_certificates_failed"] = man["result"]["metrics"].get(
            "planted_certificates_failed")
        per_run[rd] = rec
    out["per_run"] = per_run

    # cross-run identity of pinned code
    out["cross_run"] = {
        "run_experiment_sha256_set": sorted(
            {r["run_experiment_sha256"] for r in per_run.values()}),
        "commit_set": sorted({r["commit"] for r in per_run.values()}),
        "dirty_set": sorted({str(r["dirty"]) for r in per_run.values()}),
        "status_set": sorted({r["status"] for r in per_run.values()}),
        "meter_hash_json_set": sorted(
            {json.dumps(r["meter_per_file_sha256"], sort_keys=True)
             for r in per_run.values()}),
        "selftest_summary_set": sorted(
            {(r["selftest"] or {}).get("summary_line", "MISSING")
             for r in per_run.values()}),
        "selftest_rc_set": sorted(
            {str((r["selftest"] or {}).get("returncode")) for r in per_run.values()}),
        "environment_json_set": sorted(
            {json.dumps(r["environment"], sort_keys=True) for r in per_run.values()}),
    }

    # environment.json file identity
    envhashes = {}
    for rd in run_dirs:
        envhashes[rd] = sha256(os.path.join(RUNS, rd, "environment.json"))
    out["environment_file_sha256"] = envhashes

    json.dump(out, sys.stdout, indent=1, sort_keys=False, default=str)
    print()


if __name__ == "__main__":
    main()
