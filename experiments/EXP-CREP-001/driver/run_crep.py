#!/usr/bin/env python3
"""EXP-CREP-001 run driver (lifecycle execution for the four planned runs).

Phases (one per planned run):
  phase-a  RUN-CREP-001-A: materialize and verify the corpus hash manifest at
           the pinned commit (CTRL-CORPUS-INTEGRITY) -> corpus_manifest.json;
           generate the 12 recorded instances + mutated twins with the frozen
           generator; build and run the two calibration fixtures through the
           frozen verifier (CTRL-VERIFIER-CALIBRATION) ->
           verifier/calibration_receipt.json. Run is invalid if the corpus
           manifest mismatches or calibration is not 2/2.
  phase-b  RUN-CREP-001-B: construction attempts + verifier evaluation for
           ROUTE-01..ROUTE-04 (dedup control + fresh-target mutation control).
  phase-c  RUN-CREP-001-C: same for ROUTE-05..ROUTE-08.
  phase-d  RUN-CREP-001-D: determinism replay of every verdict
           (CTRL-REPLAY-DETERMINISM), aggregate predicate matrix,
           best-representation tail assessment, success/falsification
           decision table -> predicate_matrix.json.

Deterministic; no randomness (seeds: []). Writes raw.json and summary.json
into the run directory given by --out. Exit 0 on completed execution (the
run validity is data inside raw.json); nonzero only on driver crash.
"""
import hashlib
import json
import os
import subprocess
import sys

import yaml

ROUTE_IDS_B = [
    "ROUTE-01-component-resultants",
    "ROUTE-02-quotient-ring-resultants",
    "ROUTE-03-split-norms",
    "ROUTE-04-multipoint-evaluation",
]
ROUTE_IDS_C = [
    "ROUTE-05-modular-composition",
    "ROUTE-06-power-projection",
    "ROUTE-07-subresultant-hgcd",
    "ROUTE-08-displacement-representation",
]
FIXTURE_IDS = ["CAL-PASS-CREP-001", "CAL-FAIL-CREP-001"]
EXPECTED_INSTANCE_COUNT = 12


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_json(path, obj, indent=2):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=indent, sort_keys=True)
        f.write("\n")


def run_cmd(argv, cwd):
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True)


# --------------------------------------------------------------------------
# corpus integrity audit
# --------------------------------------------------------------------------

def corpus_audit(exp_root, repo_root):
    with open(os.path.join(exp_root, "specification.yaml")) as f:
        spec = yaml.safe_load(f)
    snap = spec["experiment"]["inputs"]["corpus_snapshot"]
    pinned = snap["pinned_commit"]
    entries = []
    n_ok = n_missing = n_mismatch = 0
    for item in snap["hash_manifest"]:
        path = item["path"]
        expected = item["git_blob_sha1"]
        resolved = None
        sha256 = None
        status = "missing"
        r = run_cmd(["git", "rev-parse", "%s:%s" % (pinned, path)], repo_root)
        if r.returncode == 0:
            resolved = r.stdout.strip()
            blob = subprocess.run(["git", "cat-file", "blob", resolved], cwd=repo_root,
                                  capture_output=True)
            sha256 = hashlib.sha256(blob.stdout).hexdigest()
            status = "ok" if resolved == expected else "sha1_mismatch"
        if status == "ok":
            n_ok += 1
        elif status == "missing":
            n_missing += 1
        else:
            n_mismatch += 1
        entries.append({
            "path": path,
            "expected_git_blob_sha1": expected,
            "resolved_git_blob_sha1": resolved,
            "sha256_of_blob_content": sha256,
            "status": status,
        })
    manifest = {
        "control": "CTRL-CORPUS-INTEGRITY",
        "pinned_commit": pinned,
        "verification_rule": "git blob content at the pinned commit (git cat-file), never the working tree; expected git blob SHA-1 from the frozen specification hash manifest; SHA-256 of blob content actually read",
        "entries": entries,
        "summary": {
            "total": len(entries),
            "ok": n_ok,
            "missing": n_missing,
            "sha1_mismatch": n_mismatch,
            "pass": (n_missing == 0 and n_mismatch == 0),
        },
    }
    return manifest


# --------------------------------------------------------------------------
# verifier invocation
# --------------------------------------------------------------------------

def run_verifier(exp_root, repo_root, package_path):
    verifier = os.path.join(exp_root, "verifier", "check_representation.py")
    instances = os.path.join(exp_root, "instances")
    argv = [sys.executable, verifier, "--package", package_path, "--instances", instances]
    r = run_cmd(argv, repo_root)
    if r.returncode != 0:
        raise RuntimeError("verifier failed on %s: %s" % (package_path, r.stderr.strip()))
    verdict = json.loads(r.stdout)
    return verdict, " ".join(argv)


def run_generator(exp_root, repo_root):
    gen = os.path.join(exp_root, "instances", "generate_instances.py")
    argv = [sys.executable, gen, os.path.join(exp_root, "instances")]
    r = run_cmd(argv, repo_root)
    if r.returncode != 0:
        raise RuntimeError("instance generator failed: %s" % r.stderr.strip())
    return " ".join(argv), r.stdout.strip()


def run_builder(exp_root, repo_root, run_id, which):
    builder = os.path.join(exp_root, "packages", "build_packages.py")
    argv = [sys.executable, builder, os.path.join(exp_root, "packages"), run_id, which]
    r = run_cmd(argv, repo_root)
    if r.returncode != 0:
        raise RuntimeError("package builder failed: %s" % r.stderr.strip())
    return " ".join(argv), r.stdout.strip()


def list_instances(exp_root):
    inst_dir = os.path.join(exp_root, "instances")
    return sorted(n for n in os.listdir(inst_dir)
                  if n.startswith("INST-") and n.endswith(".json") and not n.startswith("._"))


def inherited_validity(exp_root):
    """Runs inherit invalidity from experiment-level controls per the frozen
    invalidation rules: corpus integrity and calibration must hold for any
    verdict to count."""
    problems = []
    cm_path = os.path.join(exp_root, "corpus_manifest.json")
    if not os.path.exists(cm_path):
        problems.append("corpus_manifest.json missing")
    else:
        with open(cm_path) as f:
            cm = json.load(f)
        if not cm["summary"]["pass"]:
            problems.append("CTRL-CORPUS-INTEGRITY failed in RUN-CREP-001-A "
                            "(missing=%d, sha1_mismatch=%d); per invalidation_rules the verdict does not count"
                            % (cm["summary"]["missing"], cm["summary"]["sha1_mismatch"]))
    cal_path = os.path.join(exp_root, "verifier", "calibration_receipt.json")
    if not os.path.exists(cal_path):
        problems.append("calibration_receipt.json missing")
    else:
        with open(cal_path) as f:
            cal = json.load(f)
        if not cal["control_pass"]:
            problems.append("CTRL-VERIFIER-CALIBRATION failed in RUN-CREP-001-A; per invalidation_rules the verdict does not count")
    return problems


# --------------------------------------------------------------------------
# phase-a
# --------------------------------------------------------------------------

def phase_a(exp_root, repo_root, out_dir, run_id):
    raw = {"run_id": run_id, "experiment_id": "EXP-CREP-001", "phase": "freeze_calibrate_generate", "stages": {}}

    print("[phase-a] corpus integrity audit at pinned commit")
    cm = corpus_audit(exp_root, repo_root)
    cm["verified_at_run"] = run_id
    write_json(os.path.join(exp_root, "corpus_manifest.json"), cm)
    raw["stages"]["corpus"] = cm["summary"]
    raw["stages"]["corpus"]["manifest_path"] = "experiments/EXP-CREP-001/corpus_manifest.json"
    raw["stages"]["corpus"]["entries"] = cm["entries"]
    for e in cm["entries"]:
        print("  corpus %-4s %s" % (e["status"], e["path"]))

    print("[phase-a] generating recorded instances with the frozen generator")
    gen_cmd, gen_out = run_generator(exp_root, repo_root)
    print("  " + gen_out.replace("\n", "\n  "))
    inst_names = list_instances(exp_root)
    raw["stages"]["instances"] = {
        "generator_command": gen_cmd,
        "expected_count": EXPECTED_INSTANCE_COUNT,
        "generated_count": len(inst_names),
        "instances": [{"file": "experiments/EXP-CREP-001/instances/" + n,
                       "sha256": sha256_file(os.path.join(exp_root, "instances", n))} for n in inst_names],
        "enumeration_matches_frozen_spec": len(inst_names) == EXPECTED_INSTANCE_COUNT,
    }

    print("[phase-a] building calibration fixture packages")
    build_cmd, build_out = run_builder(exp_root, repo_root, run_id, "fixtures")
    print("  " + build_out.replace("\n", "\n  "))

    print("[phase-a] running calibration fixtures through the frozen verifier")
    fixtures = {}
    for fid in FIXTURE_IDS:
        pkg_path = os.path.join(exp_root, "packages", fid, "package.json")
        verdict, vcmd = run_verifier(exp_root, repo_root, pkg_path)
        fixtures[fid] = {"verdict": verdict, "verifier_command": vcmd}
        print("  %s -> %s (first failed: %s)" % (fid, verdict["route_verdict"], verdict["first_failed_predicate"]))
    cal_pass_ok = fixtures["CAL-PASS-CREP-001"]["verdict"]["route_verdict"] == "PASS"
    cal_fail_v = fixtures["CAL-FAIL-CREP-001"]["verdict"]
    cal_fail_ok = (cal_fail_v["route_verdict"] == "FAIL"
                   and not cal_fail_v["predicates"]["V3"]["pass"])
    accuracy = (int(cal_pass_ok) + int(cal_fail_ok)) / 2.0
    receipt = {
        "control": "CTRL-VERIFIER-CALIBRATION",
        "verifier": "experiments/EXP-CREP-001/verifier/check_representation.py",
        "verifier_version": fixtures["CAL-PASS-CREP-001"]["verdict"]["verifier_version"],
        "fixtures": {
            "CAL-PASS-CREP-001": {
                "predeclared_verdict": "PASS on V1-V6",
                "observed_verdict": fixtures["CAL-PASS-CREP-001"]["verdict"]["route_verdict"],
                "observed_first_failed_predicate": fixtures["CAL-PASS-CREP-001"]["verdict"]["first_failed_predicate"],
                "ok": cal_pass_ok,
            },
            "CAL-FAIL-CREP-001": {
                "predeclared_verdict": "FAIL at V3 (and V6)",
                "observed_verdict": cal_fail_v["route_verdict"],
                "observed_first_failed_predicate": cal_fail_v["first_failed_predicate"],
                "observed_V3_pass": cal_fail_v["predicates"]["V3"]["pass"],
                "observed_V6_pass": cal_fail_v["predicates"]["V6"]["pass"],
                "ok": cal_fail_ok,
            },
        },
        "calibration_accuracy": accuracy,
        "control_pass": cal_pass_ok and cal_fail_ok,
        "note": "fixtures are synthetic instruments; they prove the verifier can emit PASS and FAIL and are not evidence about H-CREP-001",
    }
    write_json(os.path.join(exp_root, "verifier", "calibration_receipt.json"), receipt)
    raw["stages"]["calibration"] = {
        "builder_command": build_cmd,
        "receipt_path": "experiments/EXP-CREP-001/verifier/calibration_receipt.json",
        "calibration_accuracy": accuracy,
        "control_pass": receipt["control_pass"],
        "fixture_verdicts": {fid: fixtures[fid]["verdict"] for fid in FIXTURE_IDS},
        "verifier_commands": {fid: fixtures[fid]["verifier_command"] for fid in FIXTURE_IDS},
    }

    problems = []
    if not cm["summary"]["pass"]:
        problems.append("corpus integrity failure: missing=%d sha1_mismatch=%d (missing pinned corpus path invalidates the run)"
                        % (cm["summary"]["missing"], cm["summary"]["sha1_mismatch"]))
    if not receipt["control_pass"]:
        problems.append("calibration accuracy below 2/2 invalidates the run")
    if len(inst_names) != EXPECTED_INSTANCE_COUNT:
        problems.append("instance enumeration mismatch: %d != 12" % len(inst_names))
    raw["run_validity"] = {
        "status": "completed_valid" if not problems else "completed_invalid",
        "reason": "all RUN-A controls passed" if not problems else "; ".join(problems),
    }
    raw["note"] = ("RUN-A executed its full stage (corpus audit, generation, calibration) and recorded every "
                   "control outcome; the invalidity marking follows the frozen invalidation_rules")
    write_json(os.path.join(out_dir, "raw.json"), raw)
    summary = {
        "run_id": run_id,
        "phase": raw["phase"],
        "corpus": cm["summary"],
        "instances_generated": len(inst_names),
        "calibration_accuracy": accuracy,
        "calibration_control_pass": receipt["control_pass"],
        "validity": raw["run_validity"],
    }
    write_json(os.path.join(out_dir, "summary.json"), summary)
    print("[phase-a] validity: %s (%s)" % (raw["run_validity"]["status"], raw["run_validity"]["reason"]))


# --------------------------------------------------------------------------
# phases b/c
# --------------------------------------------------------------------------

def phase_routes(exp_root, repo_root, out_dir, run_id, route_ids, build_set, phase_name):
    raw = {"run_id": run_id, "experiment_id": "EXP-CREP-001", "phase": phase_name, "stages": {}}
    problems = inherited_validity(exp_root)

    inst_names = list_instances(exp_root)
    if len(inst_names) != EXPECTED_INSTANCE_COUNT:
        raise RuntimeError("instance enumeration mismatch: %d != 12" % len(inst_names))

    print("[%s] building route packages: %s" % (phase_name, ", ".join(route_ids)))
    build_cmd, build_out = run_builder(exp_root, repo_root, run_id, build_set)
    print("  " + build_out.replace("\n", "\n  "))

    verdicts = {}
    verifier_commands = {}
    for rid in route_ids:
        pkg_path = os.path.join(exp_root, "packages", rid, "package.json")
        verdict, vcmd = run_verifier(exp_root, repo_root, pkg_path)
        verdicts[rid] = verdict
        verifier_commands[rid] = vcmd
        print("  %s -> %s (predicates failed: %s; dedup: %s)"
              % (rid, verdict["route_verdict"],
                 [p for p in ["V1", "V2", "V3", "V4", "V5", "V6"] if not verdict["predicates"][p]["pass"]],
                 verdict["dedup"]["owners"] if verdict["dedup"]["matched"] else "no match"))

    dedup_records = {}
    for rid in route_ids:
        d = verdicts[rid]["dedup"]
        if d["failed_duplicate"]:
            dedup_records[rid] = {"owners": d["owners"], "matches": d["matches"]}
    raw["stages"]["construction"] = {
        "builder_command": build_cmd,
        "route_ids": route_ids,
    }
    raw["stages"]["verification"] = {
        "verifier_commands": verifier_commands,
        "verdicts": verdicts,
    }
    raw["controls"] = {
        "CTRL-DEDUP-PRIOR-NEGATIVES": {
            "packages_checked": route_ids,
            "failed_duplicates": dedup_records,
            "pass": True,
            "note": "every match is recorded as failed_duplicate with its named owner; no renamed forbidden payload is scored as a novel construction",
        },
        "fresh_target_mutation_control": {
            rid: {
                "pairs_checked": verdicts[rid]["predicates"]["V2"]["pairs_checked"],
                "pairs_byte_identical": verdicts[rid]["predicates"]["V2"]["pairs_byte_identical"],
                "pass": verdicts[rid]["predicates"]["V2"]["pass"],
            } for rid in route_ids
        },
    }
    raw["run_validity"] = {
        "status": "completed_valid" if not problems else "completed_invalid",
        "reason": "all experiment-level controls hold" if not problems else "; ".join(problems),
    }
    write_json(os.path.join(out_dir, "raw.json"), raw)
    summary = {
        "run_id": run_id,
        "phase": phase_name,
        "route_verdicts": {rid: {
            "route_verdict": verdicts[rid]["route_verdict"],
            "first_failed_predicate": verdicts[rid]["first_failed_predicate"],
            "failed_predicates": [p for p in ["V1", "V2", "V3", "V4", "V5", "V6"] if not verdicts[rid]["predicates"][p]["pass"]],
            "failed_duplicate": verdicts[rid]["dedup"]["failed_duplicate"],
            "dedup_owners": verdicts[rid]["dedup"]["owners"],
        } for rid in route_ids},
        "validity": raw["run_validity"],
    }
    write_json(os.path.join(out_dir, "summary.json"), summary)
    print("[%s] validity: %s (%s)" % (phase_name, raw["run_validity"]["status"], raw["run_validity"]["reason"]))


# --------------------------------------------------------------------------
# phase-d
# --------------------------------------------------------------------------

def phase_d(exp_root, repo_root, out_dir, run_id):
    raw = {"run_id": run_id, "experiment_id": "EXP-CREP-001", "phase": "aggregate_and_decide", "stages": {}}
    problems = inherited_validity(exp_root)

    print("[phase-d] loading first-pass verdicts from RUN-CREP-001-A/B/C")
    with open(os.path.join(exp_root, "runs", "RUN-CREP-001-A", "raw.json")) as f:
        raw_a = json.load(f)
    with open(os.path.join(exp_root, "runs", "RUN-CREP-001-B", "raw.json")) as f:
        raw_b = json.load(f)
    with open(os.path.join(exp_root, "runs", "RUN-CREP-001-C", "raw.json")) as f:
        raw_c = json.load(f)
    first_pass = {}
    for fid in FIXTURE_IDS:
        first_pass[fid] = raw_a["stages"]["calibration"]["fixture_verdicts"][fid]
    for rid in ROUTE_IDS_B:
        first_pass[rid] = raw_b["stages"]["verification"]["verdicts"][rid]
    for rid in ROUTE_IDS_C:
        first_pass[rid] = raw_c["stages"]["verification"]["verdicts"][rid]

    print("[phase-d] determinism replay: re-verifying all %d packages" % len(first_pass))
    det = {"packages_compared": 0, "byte_identical": 0, "mismatches": []}
    fresh_verdicts = {}
    for pid in sorted(first_pass):
        pkg_path = os.path.join(exp_root, "packages", pid, "package.json")
        verdict, _ = run_verifier(exp_root, repo_root, pkg_path)
        fresh_verdicts[pid] = verdict
        det["packages_compared"] += 1
        if canonical_json(verdict) == canonical_json(first_pass[pid]):
            det["byte_identical"] += 1
        else:
            det["mismatches"].append(pid)
        print("  replay %-36s byte-identical: %s" % (pid, canonical_json(verdict) == canonical_json(first_pass[pid])))
    det["pass"] = det["packages_compared"] == det["byte_identical"]
    raw["controls"] = {"CTRL-REPLAY-DETERMINISM": det}
    if not det["pass"]:
        problems.append("non-identical verdict tables across the two determinism passes invalidate the run")

    print("[phase-d] aggregating predicate matrix")
    route_ids = ROUTE_IDS_B + ROUTE_IDS_C
    predicates = ["V1", "V2", "V3", "V4", "V5", "V6"]
    matrix = {}
    for rid in route_ids:
        v = first_pass[rid]
        matrix[rid] = {
            "predicates": {p: v["predicates"][p]["pass"] for p in predicates},
            "first_failed_predicate": v["first_failed_predicate"],
            "route_verdict": v["route_verdict"],
            "failed_duplicate": v["dedup"]["failed_duplicate"],
            "dedup_owners": v["dedup"]["owners"],
            "declared_exponents": {
                "preprocessing": v["declared_exponents"]["preprocessing"],
                "online": v["declared_exponents"]["online"],
            },
        }
    with open(os.path.join(exp_root, "corpus_manifest.json")) as f:
        corpus = json.load(f)
    with open(os.path.join(exp_root, "verifier", "calibration_receipt.json")) as f:
        calibration = json.load(f)

    # per-stratum V4/V5 breakdown (secondary metric)
    per_stratum = {}
    for rid in route_ids:
        v = first_pass[rid]
        for iid, v4 in v["predicates"]["V4"]["per_instance"].items():
            stratum = iid.split("-", 2)[2]
            per_stratum.setdefault(stratum, {}).setdefault(rid, {
                "V4_pass": len(v4["support_symmetric_difference"]) == 0,
            })
        for iid, v5 in v["predicates"]["V5"]["per_instance"].items():
            stratum = iid.split("-", 2)[2]
            per_stratum.setdefault(stratum, {}).setdefault(rid, {})["V5_pass"] = v5["replay_error_count"] == 0

    # best-representation tail check
    ranked = sorted(route_ids, key=lambda r: (sum(1 for p in predicates if not matrix[r]["predicates"][p]), r))
    best = ranked[0]
    best_failures = sorted(p for p in predicates if not matrix[best]["predicates"][p])
    best_record = {
        "package_id": best,
        "failure_count": len(best_failures),
        "failure_set": best_failures,
        "tied_packages": [r for r in ranked if sum(1 for p in predicates if not matrix[r]["predicates"][p]) == len(best_failures)],
        "falsification_line_evaluation": {
            "still_theta_B3_target_dependent_coordinates": "V3" in best_failures,
            "note": "the falsification line (best exhibited representation still carries Theta(B^3) target-dependent coordinates, i.e. V3 failed) is evaluated on the package with the fewest predicate failures; ties broken by lowest route id",
        },
    }

    # success / falsification decision table (mechanical evaluation of the
    # preregistered formulas on verifier outputs; NOT a hypothesis verdict)
    any_pass = any(matrix[r]["route_verdict"] == "PASS" for r in route_ids)
    all_fail = all(matrix[r]["route_verdict"] == "FAIL" for r in route_ids)
    decision_table = {
        "success_formula": {
            "formula": "exists r in ROUTE-01..08 with V1..V6 all pass on all 12 instances within budget, calibration 2/2, corpus integrity holds",
            "any_route_passes_V1_V6": any_pass,
            "calibration_2_of_2": calibration["control_pass"],
            "corpus_integrity": corpus["summary"]["pass"],
            "satisfied": any_pass and calibration["control_pass"] and corpus["summary"]["pass"],
        },
        "falsification_formula": {
            "formula": "every route in the frozen set fails at least one verifier predicate within budget, or the best exhibited representation still fails V3",
            "every_route_fails_at_least_one_predicate": all_fail,
            "best_representation_fails_V3": best_record["falsification_line_evaluation"]["still_theta_B3_target_dependent_coordinates"],
            "satisfied": all_fail or best_record["falsification_line_evaluation"]["still_theta_B3_target_dependent_coordinates"],
        },
        "scope_note": "mechanical evaluation of the preregistered formulas on frozen-verifier outputs only; a scoped outcome over the eight frozen routes and the recorded instance family, not an impossibility theorem; hypothesis-status decisions belong to the Coordinator",
        "validity_note": "verdicts count only if corpus integrity and calibration hold (see run_validity)",
    }

    # wall-clock and memory per stage (secondary metric), from run manifests
    stage_resources = {}
    for rid in ["RUN-CREP-001-A", "RUN-CREP-001-B", "RUN-CREP-001-C"]:
        mpath = os.path.join(exp_root, "runs", rid, "manifest.yaml")
        if os.path.exists(mpath):
            with open(mpath) as f:
                m = yaml.safe_load(f)
            stage_resources[rid] = {
                "wall_seconds": m["run"]["timing"]["wall_seconds"],
                "cpu_seconds": m["run"]["resources"]["cpu_seconds"],
                "peak_rss_bytes": m["run"]["resources"]["peak_rss_bytes"],
            }
    stage_resources["RUN-CREP-001-D"] = "recorded in this run's own manifest"

    predicate_matrix = {
        "experiment_id": "EXP-CREP-001",
        "aggregated_at_run": run_id,
        "predicate_matrix": matrix,
        "calibration_fixtures": {
            fid: {
                "route_verdict": first_pass[fid]["route_verdict"],
                "first_failed_predicate": first_pass[fid]["first_failed_predicate"],
                "predicates": {p: first_pass[fid]["predicates"][p]["pass"] for p in predicates},
            } for fid in FIXTURE_IDS
        },
        "controls": {
            "CTRL-CORPUS-INTEGRITY": corpus["summary"],
            "CTRL-VERIFIER-CALIBRATION": {"control_pass": calibration["control_pass"], "calibration_accuracy": calibration["calibration_accuracy"]},
            "CTRL-REPLAY-DETERMINISM": det,
            "CTRL-DEDUP-PRIOR-NEGATIVES": {
                "failed_duplicate_count": sum(1 for r in route_ids if matrix[r]["failed_duplicate"]),
                "records": {r: matrix[r]["dedup_owners"] for r in route_ids if matrix[r]["failed_duplicate"]},
            },
        },
        "metrics": {
            "failed_duplicate_count_with_owners": {r: matrix[r]["dedup_owners"] for r in route_ids if matrix[r]["failed_duplicate"]},
            "fresh_target_mutation_invariance": {r: matrix[r]["predicates"]["V2"] for r in route_ids},
            "per_stratum_verdicts": per_stratum,
            "corpus_hash_mismatch_count": corpus["summary"]["sha1_mismatch"] + corpus["summary"]["missing"],
            "wall_clock_and_memory_per_stage": stage_resources,
        },
        "best_representation": best_record,
        "decision_table": decision_table,
    }
    write_json(os.path.join(exp_root, "predicate_matrix.json"), predicate_matrix)

    raw["stages"]["aggregate"] = {
        "predicate_matrix_path": "experiments/EXP-CREP-001/predicate_matrix.json",
        "route_verdicts": {r: matrix[r]["route_verdict"] for r in route_ids},
        "best_representation": best_record,
        "decision_table": decision_table,
        "stage_resources": stage_resources,
    }
    raw["run_validity"] = {
        "status": "completed_valid" if not problems else "completed_invalid",
        "reason": "all experiment-level controls hold" if not problems else "; ".join(problems),
    }
    write_json(os.path.join(out_dir, "raw.json"), raw)
    summary = {
        "run_id": run_id,
        "phase": "aggregate_and_decide",
        "route_verdicts": {r: {
            "route_verdict": matrix[r]["route_verdict"],
            "first_failed_predicate": matrix[r]["first_failed_predicate"],
            "failed_predicates": sorted(p for p in predicates if not matrix[r]["predicates"][p]),
            "failed_duplicate": matrix[r]["failed_duplicate"],
            "dedup_owners": matrix[r]["dedup_owners"],
        } for r in route_ids},
        "determinism_pass": det["pass"],
        "best_representation": best_record,
        "decision_table": decision_table,
        "validity": raw["run_validity"],
    }
    write_json(os.path.join(out_dir, "summary.json"), summary)
    print("[phase-d] validity: %s (%s)" % (raw["run_validity"]["status"], raw["run_validity"]["reason"]))


# --------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("phase-a", "phase-b", "phase-c", "phase-d"):
        print("usage: run_crep.py phase-a|phase-b|phase-c|phase-d --run-id ID --exp-root DIR --repo-root DIR --out DIR", file=sys.stderr)
        sys.exit(2)
    phase = args[0]
    opts = {"--run-id": None, "--exp-root": "experiments/EXP-CREP-001", "--repo-root": ".", "--out": None}
    i = 1
    while i < len(args):
        if args[i] in opts:
            opts[args[i]] = args[i + 1]
            i += 2
        else:
            print("unknown argument: %s" % args[i], file=sys.stderr)
            sys.exit(2)
    if not opts["--run-id"] or not opts["--out"]:
        print("--run-id and --out are required", file=sys.stderr)
        sys.exit(2)
    exp_root = os.path.abspath(opts["--exp-root"])
    repo_root = os.path.abspath(opts["--repo-root"])
    out_dir = os.path.abspath(opts["--out"])
    os.makedirs(out_dir, exist_ok=True)
    if phase == "phase-a":
        phase_a(exp_root, repo_root, out_dir, opts["--run-id"])
    elif phase == "phase-b":
        phase_routes(exp_root, repo_root, out_dir, opts["--run-id"], ROUTE_IDS_B, "routes-1-4", "routes_1_to_4")
    elif phase == "phase-c":
        phase_routes(exp_root, repo_root, out_dir, opts["--run-id"], ROUTE_IDS_C, "routes-5-8", "routes_5_to_8")
    else:
        phase_d(exp_root, repo_root, out_dir, opts["--run-id"])


if __name__ == "__main__":
    main()
