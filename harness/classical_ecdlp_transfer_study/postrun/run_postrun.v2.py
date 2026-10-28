#!/usr/bin/env python3
"""Verify and mechanically export one sealed transfer study; no scientific run.

Only the frozen independent verifier is invoked. Fresh cohort generation,
constructor evaluation, VM calls and scientific retries are never performed.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

spec = importlib.util.spec_from_file_location("_transfer_postrun_analysis", Path(__file__).with_name("analysis.py"))
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)
PREFIX = "harness/classical_ecdlp_transfer_study"
EXPERIMENT, RUN = "EXP-ECDLP-ef7323", "RUN-ECDLP-ea5986"
SOURCE_NAMES = {"curve.py", "constructor.py", "cohort.py", "compute.py", "verify.py", "controller.py", "driver.py"}


def read(path):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            analysis.need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def write(path, value):
    with Path(path).open("x") as target:
        json.dump(value, target, indent=2, sort_keys=True, allow_nan=False)
        target.write("\n")


def safe(root, relative):
    rel = PurePosixPath(relative)
    analysis.need(not rel.is_absolute() and ".." not in rel.parts and str(rel) == relative, "unsafe member path")
    path = root / relative
    analysis.need(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "member escapes root")
    return path


def locate_raw(root):
    root = Path(root).resolve()
    names = (".", "raw", "tree/raw", "collected/tree/raw", "modal/collected/tree/raw")
    signatures = ("compute-summary.json", "failure.json", "attempt-intents.jsonl", "attempts.jsonl",
                  "setups.jsonl", "diagnostics.jsonl", "control-phase.json", "cohort")
    found = {p.resolve() for name in names for p in [root / name]
             if any((p / item).exists() for item in signatures) or
             (p.name == "raw" and p.is_dir() and (p.parent / "output-manifest.json").is_file())}
    analysis.need(len(found) == 1, "expected one bounded sealed raw directory")
    return found.pop()


def invoke(name, argv, out, repo):
    started = time.time()
    write(out / (name + ".invocation.json"), {"argv": argv, "cwd": str(repo), "attempts": 1,
          "automatic_retry": False, "started_unix_seconds": started})
    stdout, stderr = out / (name + ".stdout.txt"), out / (name + ".stderr.txt")
    with stdout.open("xb") as so, stderr.open("xb") as se:
        proc = subprocess.run(argv, cwd=repo, stdout=so, stderr=se, check=False)
    result = {"argv": argv, "returncode": proc.returncode, "started_unix_seconds": started,
              "finished_unix_seconds": time.time(), "attempts": 1, "automatic_retry": False,
              "stdout_sha256": analysis.sha(stdout), "stderr_sha256": analysis.sha(stderr)}
    write(out / (name + ".result.json"), result)
    return result


def entry(path, base, kind="raw"):
    path = Path(path).resolve()
    return {"path": os.path.relpath(path, base), "bytes": path.stat().st_size,
            "sha256": analysis.sha(path), "kind": kind}


def exact_fraction(value):
    return str(value["numerator"]) + "/" + str(value["denominator"])


def bound_planned_attempts(protocol, compute_plan_path):
    """Use the actual hash-bound standalone plan, including repaired cohorts."""
    config = protocol["extensions"]["transfer_study"]
    analysis.need(analysis.sha(compute_plan_path) == config["compute_plan_sha256"],
                  "planned attempt count requires the bound actual compute plan")
    total = read(compute_plan_path)["expected"]["total_attempts_planned"]
    analysis.need(type(total) is int and total > 0 and
                  total == config["expected"]["total_attempts_planned"],
                  "standalone/official planned attempt counts differ")
    return total


def make_export(ep, protocol, protocol_path, source, raw, modal, out, export_id,
                census_path, report_path, census, sealed_files, provider):
    bundle = ep.export_skeleton(protocol, os.path.relpath(protocol_path, out), "modal", export_id)
    source_c = census["source_revision_c"]
    bundle["producer"] = {"runtime": "codex_cli", "model": None, "session": None, "role": "executor"}
    bundle["source"] = {"repo": protocol["repository"], "commit": source_c, "dirty": None}
    bundle["host"]["path"] = os.path.relpath(modal / "provider-context.json", out)
    bundle["host"]["sha256"] = analysis.sha(modal / "provider-context.json")
    bundle["arms"] = [{"id": a["id"], "role": a["role"], "commit": source_c,
                       "binary_sha256": a["instrument"]["binary_sha256"]} for a in protocol["arms"]]
    rows = []
    scalar_ids = ("verified_attempt_successes", "unique_target_ids_recovered", "small_full_bit_gate_passes",
                  "online_group_add_calls", "setup_group_add_calls", "first_success_prefix_group_work")
    for cell in census["per_curve_arm_metrics"]:
        if not cell["actual_setup_observed"] and not cell["observed_attempts"] and not cell["unresolved_attempts"]:
            continue  # The complete schedule remains in census; no padded observation.
        counted = {name: cell[name] for name in scalar_ids if cell[name] is not None}
        if cell["q_denominator"]:
            counted["attempt_success_rate"] = f"{cell['q_numerator']}/{cell['q_denominator']}"
        for name in ("batch_work_per_success_event", "cold_restart_model_group_work"):
            if cell[name] is not None:
                counted[name] = exact_fraction(cell[name])
        counters = {"observed_primary_attempts": cell["observed_attempts"],
            "reported_success_events": cell["reported_success_events"],
            "unique_target_ids_reported_recovered": cell["unique_target_ids_reported_recovered"],
            "unresolved_attempts": cell["unresolved_attempts"], "unattempted_attempts": cell["unattempted_attempts"],
            "setup_phase_vectors_json": analysis.json.dumps(cell["setup_phase_counters"], sort_keys=True),
            "online_phase_vectors_json": analysis.json.dumps(cell["online_phase_counters"], sort_keys=True),
            "diagnostic_vector_json": analysis.json.dumps(cell["diagnostic_counters"], sort_keys=True),
            "first_success_prefix_vector_json": analysis.json.dumps(cell["first_success_prefix_counters"], sort_keys=True),
            "attempt_status_counts_json": analysis.json.dumps(cell["attempt_status_counts"], sort_keys=True),
            "q_wilson95_json": analysis.json.dumps(cell["q_wilson95"]),
            "cost_over_q_vector_json": analysis.json.dumps(cell["counter_cost_over_q"], sort_keys=True),
            "cold_restart_vector_json": analysis.json.dumps(cell["cold_restart_counter_model"], sort_keys=True),
            "batch_cost_per_success_vector_json": analysis.json.dumps(cell["batch_counter_cost_per_success"], sort_keys=True)}
        valid = cell["complete"] and cell["independently_verified"]
        rows.append(ep.run_row(run_id=RUN + "." + cell["curve_id"] + "." + cell["arm_id"],
            arm=cell["arm_id"], instance_id=cell["curve_id"], replicate=0, seed=None,
            status="succeeded" if cell["complete"] else "infra_error", attempts=1, resumed=0,
            measurements={"counted": counted, "counters": counters, "wall_valid": False},
            verification={"status": "verified" if valid else "error" if report_path.is_file() else "not_run",
                          "verifier": "frozen independent transfer verify.py" if report_path.is_file() else None},
            exclusion={"excluded": not valid, "rule": "incomplete or independently invalid transfer records" if not valid else None},
            worker=provider["sandbox_id"], backend_ref=provider["sandbox_id"]+":"+cell["curve_id"]+":"+cell["arm_id"]))
    bundle["runs"], bundle["flow"] = rows, ep.compute_flow(rows)
    files = [entry(p, out, "receipt" if p.suffix == ".json" else "raw") for p in sealed_files]
    files.extend(entry(p, out, "receipt") for p in (protocol_path, modal / "compute-plan.json", modal / "source-manifest.json",
                 modal / "prior-exclusions.json", modal / "provider-context.json", census_path))
    files.extend(entry(source / name, out, "receipt") for name in sorted(SOURCE_NAMES))
    outputs = [entry(report_path, out, "analysis")] if report_path.is_file() else []
    files.extend(outputs)
    bundle["files"] = files
    bundle["analysis"] = {"script": entry(source / "verify.py", out, "analysis"), "outputs": outputs,
                          "blinded": False, "blinding_key_sha256": None, "unmasked_at": None}
    bundle["notes"] = [{"kind": "observation", "by": "transfer postrun adapter", "text":
        "One standard row is one actual curve/arm batch; all fixed target/rep attempts remain in raw streams. Four success events for one Q are not four unique recovered targets. Zero-success cells are retained with Wilson uncertainty and undefined empirical cost ratios; larger all-r bit diagnostics are not applicable, never zero failures."},
        {"kind": "observation", "by": "transfer postrun adapter", "text":
        "Ratios retain exact fractions of same-family emitted counters. Online over q is online_sum/s; cold setup reused is S+online_sum/s, never S/q. Actual batch ratio is (S+online_sum)/s. First-hit prefixes include every failed target and are derived from full records. Cohort/common validation and validator-only controls are retained once in backend_record, without arbitrary prices or duplicated observations. Clocks and candidate counter execution are unqualified."}]
    bundle["backend_record"] = {"planned_curve_arm_slots": 440, "actual_curve_arm_rows": len(rows),
        "planned_primary_attempts": bound_planned_attempts(protocol, modal / "compute-plan.json"),
        "attempt_accounting": census["attempt_accounting"],
        "common_fixture_work": census["common_work"], "per_curve_arm_metrics": census["per_curve_arm_metrics"],
        "provider_context": provider, "compute_summary": census["compute_summary"],
        "independent_verifier_report": read(report_path) if report_path.is_file() else None,
        "parse_and_mapping_findings": census["parse_and_mapping_findings"],
        "source_counters_replayed": False, "all_clocks_wall_valid": False,
        "fresh_execution_proven_by_traces": False, "scientific_validity": "not_assessed"}
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("/workspace/classical-ecdlp-validation-ready"))
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--collected", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--export-id", required=True)
    args = parser.parse_args()
    repo, out, protocol_path = args.repo_root.resolve(), args.out.resolve(), args.protocol.resolve()
    analysis.need(not out.exists(), "fresh output directory required")
    protocol = read(protocol_path)
    analysis.need(protocol.get("protocol_id") == EXPERIMENT and protocol["freeze"]["status"] == "frozen",
                  "actual final frozen official protocol required")
    official_hash = hashlib.sha256(json.dumps({k:v for k,v in protocol.items() if k != "freeze"},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()
    analysis.need(protocol["freeze"]["protocol_sha256"] == official_hash, "official frozen body differs")
    config = protocol["extensions"]["transfer_study"]
    analysis.need(protocol["sample_size"]["instances"] == 40 and protocol["sample_size"]["replicates"] == 1
                  and {a["id"] for a in protocol["arms"]} == set(analysis.ARMS), "wrong registered sample unit/arms")
    raw = locate_raw(args.collected)
    tree, modal = raw.parent, raw.parent.parent.parent
    analysis.need(not out.is_relative_to(tree), "postrun outputs must be outside sealed collection")
    seal = read(tree / "output-manifest.json")
    cleanup_path = tree / "process-cleanup.json"
    analysis.need(seal.get("schema") == "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1" and
        seal.get("study_uid1000_quiescent") is True and seal["process_cleanup_sha256"] == analysis.sha(cleanup_path)
        and read(cleanup_path).get("quiescent") is True, "sealed process quiescence required")
    seen, sealed_files = set(), [tree / "output-manifest.json"]
    for item in seal["files"]:
        path = safe(tree, item["path"])
        analysis.need(item["path"] not in seen and path.is_file() and path.stat().st_size == item["bytes"]
                      and analysis.sha(path) == item["sha256"], "sealed member missing/changed")
        seen.add(item["path"]); sealed_files.append(path)
    analysis.need(analysis.sha(modal / "protocol.json") == analysis.sha(protocol_path), "actual official launch protocol differs")
    for name, field in (("compute-plan.json", "compute_plan_sha256"), ("source-manifest.json", "source_manifest_sha256"),
                        ("prior-exclusions.json", "prior_exclusions_sha256")):
        analysis.need(analysis.sha(modal / name) == config[field], "actual launch bytes differ: " + name)
    manifest = read(modal / "source-manifest.json")
    source_c = manifest["source_revision_c"]
    analysis.need(re.fullmatch(r"[0-9a-f]{40}", source_c) is not None and source_c == config["source_revision_c"]
                  and set(manifest["files"]) == SOURCE_NAMES, "actual exact seven-module source closure required")
    source = modal / "staged-source"
    canonical_source = repo / PREFIX
    for name, digest in manifest["files"].items():
        analysis.need(analysis.sha(source / name) == digest and analysis.sha(canonical_source / name) == digest,
                      "actual staged/canonical source differs: " + name)
    analysis.need(manifest["files"]["verify.py"] == protocol["analysis_plan"]["script"]["sha256"], "frozen independent verifier source differs")
    provider = read(modal / "provider-context.json")
    analysis.need(provider.get("schema") == "classical.ecdlp.transfer-study.modal-provider-context/v1"
        and provider.get("backend") == "modal" and provider.get("runtime") == "vm" and provider.get("block_network") is True,
        "actual transfer Modal VM context required")
    for name, prefix in (("app_id", "ap-"), ("image_id", "im-"), ("sandbox_id", "sb-")):
        analysis.need(str(provider.get(name)).startswith(prefix), "actual Modal object ID required")
    for name in ("app_id", "image_id"):
        analysis.need(provider[name] == protocol["execution"]["placement"][name], "provider differs from frozen placement")
    analysis.need(provider.get("source_revision_c") == source_c and provider.get("protocol_sha256") == official_hash
        and provider.get("source_manifest_sha256") == config["source_manifest_sha256"]
        and provider.get("compute_plan_sha256") == config["compute_plan_sha256"]
        and provider.get("prior_exclusions_sha256") == config["prior_exclusions_sha256"], "actual provider closure differs")
    sys.path.insert(0, str(repo / "tools"))
    import experiment_protocol as ep
    analysis.need(not (ep.schema_errors(protocol, "experiment.protocol/v1") or ep.lint_protocol(protocol, protocol_path.parent)), "invalid official frozen protocol")
    out.mkdir(parents=True)  # Parent exists before all relative-file linting.
    write(out / "preflight.json", {"experiment_id": EXPERIMENT, "run_id": RUN, "protocol_sha256": official_hash,
        "source_revision_c": source_c, "source_files": manifest["files"], "postrun_source_sha256": analysis.sha(__file__),
        "mapper_source_sha256": analysis.sha(Path(__file__).with_name("analysis.py")), "candidate_evaluations": 0,
        "cohort_generation_calls": 0, "scientific_retry": False})
    report_dir = out / "verification"; report_dir.mkdir()
    report_path = report_dir / "report.json"
    cohort_path = raw / "cohort/cohort-public.json"
    argv = [sys.executable, str(source / "verify.py"), "--protocol", str(modal / "compute-plan.json"),
        "--cohort", str(cohort_path), "--source-manifest", str(modal / "source-manifest.json"), "--source-root", str(source),
        "--prior-exclusions", str(modal / "prior-exclusions.json"), "--attempts", str(raw / "attempts.jsonl"),
        "--setups", str(raw / "setups.jsonl"), "--diagnostics", str(raw / "diagnostics.jsonl"),
        "--controls", str(raw / "control-phase.json"), "--output", str(report_path)]
    verdict = invoke("verify", argv, out, repo)
    report = read(report_path) if report_path.is_file() else None
    if report:
        analysis.need(report.get("schema") == "classical.ecdlp.transfer-study.verification/v1"
            and report.get("protocol_sha256") == config["compute_plan_sha256"]
            and report.get("source_manifest_sha256") == config["source_manifest_sha256"], "actual verifier report binding differs")
    streams, findings = {}, []
    for name in ("attempts", "setups", "diagnostics", "attempt-intents"):
        streams[name], errors = analysis.load_jsonl(raw / (name + ".jsonl")); findings.extend(errors)
    cohort = read(cohort_path) if cohort_path.is_file() else {"fixtures": [], "generation_status": "not_retained"}
    cells, accounting, mapped_findings = analysis.aggregate(cohort, streams["attempts"], streams["setups"],
        streams["diagnostics"], streams["attempt-intents"], report if not findings else None)
    findings.extend(mapped_findings)
    summary_path = raw / "compute-summary.json"
    summary = read(summary_path) if summary_path.is_file() else None
    if summary:
        analysis.need(summary["source_fingerprint"] == config["source_manifest_sha256"]
            and summary["protocol_sha256"] == config["compute_plan_sha256"]
            and summary["official_protocol_sha256"] == official_hash, "compute summary identity differs")
    common_path = raw / "cohort/cohort-costs.json"
    common = {"cohort_generation": read(common_path) if common_path.is_file() else None,
              "common_input_validation": (summary or {}).get("common_input_validation"),
              "validator_work_counts": (report or {}).get("validator_work_counts"),
              "validator_work_counter_scope": (report or {}).get("validator_work_counter_scope"),
              "validator_odd_anchor_null_context": (report or {}).get("validator_odd_anchor_null"),
              "attribution": "Actual generation/common validation and validator work retained once, never padded or prorated over440 observations"}
    bindings = [protocol_path, modal / "compute-plan.json", modal / "source-manifest.json", modal / "prior-exclusions.json",
                modal / "provider-context.json", tree / "output-manifest.json",
                out / "verify.invocation.json", out / "verify.result.json", out / "verify.stdout.txt", out / "verify.stderr.txt"]
    bindings += [p for p in (cohort_path, summary_path, common_path, report_path,
        *(raw / (name + ".jsonl") for name in streams)) if p.is_file()]
    census = {"schema": analysis.SCHEMA, "experiment_id": EXPERIMENT, "run_id": RUN,
        "protocol_sha256": official_hash, "compute_plan_sha256": config["compute_plan_sha256"],
        "screen_plan_sha256": config["compute_plan_sha256"], "source_fingerprint": config["source_manifest_sha256"],
        "source_revision_c": source_c, "cohort_sha256": analysis.sha(cohort_path) if cohort_path.is_file() else None,
        "verification_report_sha256": analysis.sha(report_path) if report_path.is_file() else None,
        "input_bindings": {str(p): analysis.sha(p) for p in bindings}, "compute_summary": summary,
        "cohort": cohort, "fixtures": [{**{k:f.get(k) for k in ("curve_id", "p", "r", "stratum_id", "panel")},
                                       "target_count": len(f["targets"])} for f in cohort.get("fixtures", [])],
        "per_curve_arm_metrics": cells, "attempt_accounting": accounting, "common_work": common,
        "parse_and_mapping_findings": findings, "verifier_returncode": verdict["returncode"],
        "operational_status": "completed" if (summary or {}).get("completed") is True else "partial_or_failed",
        "candidate_evaluations_by_postrun": 0, "cohort_generation_calls_by_postrun": 0,
        "all_clocks_wall_valid": False, "source_counters_replayed": False, "scientific_validity": "not_assessed"}
    census_path = out / "summary-census.json"; write(census_path, census)
    bundle = make_export(ep, protocol, protocol_path, canonical_source, raw, modal, out, args.export_id,
                         census_path, report_path, census, sealed_files, provider)
    export_path = out / "export.json"
    validation = ep.schema_errors(bundle, "experiment.export/v1") or ep.lint_export(bundle, protocol, out, True)
    write(export_path, bundle)
    write(out / "export.json.validation.json", {"findings": validation, "actual_curve_arm_rows": len(bundle["runs"]),
        "observed_completed_attempt_ids": accounting["observed_completed_result_ids"],
        "unresolved_attempts": len(accounting["unresolved_attempt_ids"]), "unattempted_attempts": len(accounting["unattempted_attempt_ids"])})
    checked = invoke("check-export", [sys.executable, str(repo / "tools/experiment_protocol.py"), "check-export", str(export_path),
                                     "--protocol", str(protocol_path), "--verify-files"], out, repo)
    passed = verdict["returncode"] == 0 and not findings and not validation and checked["returncode"] == 0
    write(out / "postrun-result.json", {"schema": "classical.ecdlp.transfer-study.postrun/v1", "pipeline_passed": passed,
        "verifier_returncode": verdict["returncode"], "official_check_export_returncode": checked["returncode"],
        "export_findings": validation, "export_sha256": analysis.sha(export_path),
        "candidate_evaluations_by_postrun": 0, "cohort_generation_calls_by_postrun": 0,
        "scientific_retry": False, "scientific_validity": "not_assessed"})
    print(json.dumps({"pipeline_passed": passed, "out": str(out), "actual_curve_arm_rows": len(bundle["runs"])}))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        failure = {"status": "postrun_refused_or_failed", "type": type(error).__name__, "error": str(error),
                   "candidate_evaluations_by_postrun": 0, "cohort_generation_calls_by_postrun": 0}
        # Retain a write-once postprocessing failure if its fresh output exists.
        try:
            argv = sys.argv
            if "--out" in argv:
                out = Path(argv[argv.index("--out")+1])
                if out.is_dir() and not (out / "postrun-failure.json").exists():
                    write(out / "postrun-failure.json", failure)
        except (ValueError, OSError, IndexError):
            pass
        print(json.dumps(failure), file=sys.stderr)
        raise SystemExit(2)
