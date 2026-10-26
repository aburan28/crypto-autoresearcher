#!/usr/bin/env python3
"""Export actual endpoint-reuse child executions; never launch or pad a run.

One export row represents one fresh (curve, replicate, arm) child that holds
64 sequential targets. wait4 rusage is recorded once. Native counter sequences
remain exact JSON-encoded arrays by event kind/field; nested snapshots are not
silently priced or summed. Unattempted children remain in the backend record
with attempts=0 and are not relabelled as executed to satisfy the v1 schema.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

import analysis
from seed_rules import public_seed

FAMILIES = ("counters", "auxiliary_work", "upstream_stats", "rng", "fill", "reuse", "memory")
STATE_FIELDS = ("known_count", "pending_count", "endpoint_cap", "accepted_count", "precompute_reported_ops_total")

def numeric_fields(value, prefix):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from numeric_fields(child, prefix + "." + key)
    elif isinstance(value, int) and not isinstance(value, bool):
        yield prefix, value

def counter_sequences(rows):
    sequences = defaultdict(list)
    for row in rows:
        kind = row["row_kind"]
        for family in FAMILIES:
            if family in row:
                for key, value in numeric_fields(row[family], "native." + kind + "." + family):
                    sequences[key].append(value)
        for name in STATE_FIELDS:
            if name in row:
                sequences["native." + kind + ".state." + name].append(row[name])
    return {key: json.dumps(values, separators=(",", ":")) for key, values in sorted(sequences.items())}

def file_entry(path, base, kind="raw"):
    return {"path": os.path.relpath(path.resolve(), base.resolve()), "sha256": analysis.sha(path),
            "bytes": path.stat().st_size, "kind": kind}

def metadata_files(root, manifest):
    for item in manifest["files"]:
        if item["path"].startswith("cells/") and item["path"].endswith("/execution.json"):
            path = root / item["path"]
            analysis.require(path.is_file() and analysis.sha(path) == item["sha256"] and path.stat().st_size == item["bytes"],
                             "child metadata missing/hash mismatch")
            record = analysis.read_json(path)
            analysis.require(record.get("schema") == "classical.ecdlp.endpoint-reuse.child-execution.v1",
                             "unexpected child metadata schema")
            yield path, record

def target_metrics(rows):
    setup = [r for r in rows if r["row_kind"] == "setup"]
    targets = sorted((r for r in rows if r["row_kind"] == "target"), key=lambda r: r["target_ordinal"])
    result = {"observed_target_cases": len(targets), "observed_verified_scalar_claims": sum(r.get("verified_scalar") is not None for r in targets)}
    if len(setup) != 1:
        return result
    total = analysis.exact_counters(setup[0]["counters"])
    verified = 0
    for ordinal, row in enumerate(targets):
        if row["target_ordinal"] != ordinal:
            break
        total = analysis.add_vectors(total, analysis.exact_counters(row["counters"]))
        verified += row["status"] == "solved" and row.get("verified_scalar") is not None
        if ordinal + 1 in analysis.PREFIXES:
            result["group_additions_m" + str(ordinal + 1)] = total["group_additions"]
        if ordinal == 63:
            result["verified_targets_m64"] = verified
    memory = setup[0].get("memory", {})
    if "endpoint_allocated_bytes" in memory:
        result["endpoint_arena_bytes"] = memory["endpoint_allocated_bytes"]
    return result

def native_status(record):
    return {"completed": "succeeded", "timed_out": "timeout", "interrupted": "interrupted",
            "native_nonzero": "failed", "invalid_output": "infra_error", "infrastructure_error": "infra_error"}.get(record["status"], "infra_error")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("protocol", "raw_manifest", "verification", "out", "repo_root"):
        p.add_argument("--" + key.replace("_", "-"), required=True, type=Path)
    p.add_argument("--analysis-summary", type=Path)
    p.add_argument("--export-id", required=True)
    p.add_argument("--external-nonce", required=True)
    p.add_argument("--producer-runtime")
    p.add_argument("--producer-model")
    p.add_argument("--producer-session")
    p.add_argument("--producer-role")
    args = p.parse_args()
    if args.out.exists():
        p.error("exports are write-once; use a new output path")
    raw_root = args.raw_manifest.parent.resolve()
    if args.out.resolve().is_relative_to(raw_root):
        p.error("the export belongs beside raw records, never inside a sealed raw directory")
    sys.path.insert(0, str(args.repo_root.resolve() / "tools"))
    import experiment_protocol as ep
    protocol = ep.read_json(args.protocol)
    findings = ep.schema_errors(protocol, "experiment.protocol/v1") or ep.lint_protocol(protocol, args.protocol.parent)
    if findings or protocol["freeze"]["status"] != "frozen":
        p.error("an actual frozen valid protocol is required: " + "; ".join(findings))
    manifest, raw_files = analysis.raw_files(args.raw_manifest)
    child_items = list(metadata_files(raw_root, manifest))
    actual = [(path, rec) for path, rec in child_items if rec.get("attempts", 0) >= 1]
    unattempted = [file_entry(path, args.out.parent, "receipt") for path, rec in child_items if rec.get("attempts", 0) == 0]
    analysis.require(len({(r["fixture_id"], r["replicate"], r["arm"]) for _, r in child_items}) == len(child_items),
                     "duplicate child execution identity")
    verification = analysis.read_json(args.verification)
    analysis.require(verification.get("schema") == "classical.ecdlp.endpoint-reuse.public-verification.v1", "actual independent public-verification summary required")
    if args.analysis_summary is not None:
        analysis.read_json(args.analysis_summary)
    native_by_path = {item["path"]: item for item in raw_files}
    observed_arm_ids = {}
    runs = []
    first_host = None
    total_target_rows = 0
    for metadata_path, record in actual:
        arm, cell, fixture, replicate = record["arm"], record["cell_id"], record["fixture_id"], record["replicate"]
        analysis.require(arm in analysis.ARMS and record["protocol_sha256"] == protocol["freeze"]["protocol_sha256"], "unplanned arm/protocol")
        expected_seed = public_seed(protocol["freeze"]["protocol_sha256"], args.external_nonce, fixture, replicate, "solver_cell")
        analysis.require(record["solver_seed"] == expected_seed, "observed common solver seed differs from frozen custom law")
        arm_pins = next(a["instrument"] for a in protocol["arms"] if a["id"] == arm)
        for field, observed_key in (("commit", "source_revision"), ("binary_sha256", "binary_sha256")):
            if arm_pins[field] is not None:
                analysis.require(record[observed_key] == arm_pins[field], "actual source/binary differs from protocol")
        identity = (record["source_revision"], record["binary_sha256"])
        analysis.require(arm not in observed_arm_ids or observed_arm_ids[arm] == identity, "one arm used different instruments")
        observed_arm_ids[arm] = identity
        raw_path = record.get("raw_output")
        rows = list(analysis.stream_parts(args.raw_manifest, manifest, native_by_path[raw_path])) if raw_path in native_by_path else []
        for row in rows:
            analysis.require((row["cell_id"], row["fixture"], row["replicate"], row["arm"]) == (cell, fixture, replicate, arm), "native child identity mismatch")
        counted = target_metrics(rows)
        total_target_rows += counted["observed_target_cases"]
        counters = counter_sequences(rows)
        counters["native_trace_rows"] = len(rows)
        if raw_path in native_by_path:
            counters["native_trace_bytes"] = native_by_path[raw_path]["bytes"]
        usage = record.get("rusage") or {}
        for key, value in usage.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                counters["rusage." + key] = value
        clock, host = record.get("clock") or {}, record.get("host_before") or {}
        first_host = first_host or host
        status = native_status(record)
        equation_pass = verification.get("status") == "public_equations_and_trace_pass"
        excluded = status != "succeeded" or not equation_pass
        prefix = metadata_path.parent.relative_to(raw_root).as_posix() + "/"
        artifacts = []
        for item in manifest["files"]:
            file_path = raw_root / item["path"]
            if item["path"].startswith(prefix) and file_path.is_file():
                artifacts.append(file_entry(file_path, args.out.parent, "receipt" if file_path.name == "execution.json" else "raw"))
        runs.append({"run_id": cell + "." + arm, "arm": arm, "instance_id": fixture, "seed": str(record["solver_seed"]),
                     "replicate": replicate, "warmup": False, "status": status,
                     "outcome_class": "completed" if status in ep.COMPLETED else "not_completed",
                     "attempts": record["attempts"], "resumed": int(record.get("resumed", False)), "checkpoint": None,
                     "measurements": {"counted": counted, "wall_seconds": clock.get("wall_seconds"),
                                      "wall_valid": False, "cpu_user_seconds": usage.get("user_seconds"),
                                      "cpu_sys_seconds": usage.get("system_seconds"), "max_rss_bytes": usage.get("maxrss_bytes"), "counters": counters},
                     "isolation": {"tier": host.get("isolation_level"), "contended": host.get("contended"),
                                   "blockers": host.get("isolation_blockers", ["No observed isolation receipt in this actual child record."])},
                     "verification": {"status": "verified" if equation_pass else "error", "verifier": verification.get("verifier_sha256")},
                     "exclusion": {"excluded": excluded, "rule": "incomplete child or independent public witness/trace check did not pass" if excluded else None},
                     "artifacts": artifacts, "started_at": record.get("started_at"), "finished_at": record.get("finished_at"),
                     "worker": host.get("job_id"), "backend_ref": str(metadata_path.relative_to(raw_root))})
    first_host = first_host or {}
    memory = first_host.get("memory_max")
    host_summary = {"cpu_model": first_host.get("cpu_model"), "logical_cpus": len(first_host["affinity_cpus"]) if "affinity_cpus" in first_host else None,
                    "memory_bytes": int(memory) if str(memory).isdigit() else None, "kernel": first_host.get("kernel"),
                    "hypervisor": None, "isolation_tier_max": first_host.get("isolation_level")}
    files = [file_entry(args.raw_manifest, args.out.parent, "receipt"), file_entry(args.verification, args.out.parent, "receipt")]
    if args.analysis_summary is not None:
        files.append(file_entry(args.analysis_summary, args.out.parent, "analysis"))
    for item in manifest["files"]:
        path = raw_root / item["path"]
        if path.is_file():
            analysis.require(analysis.sha(path) == item["sha256"] and path.stat().st_size == item["bytes"], "actual archived file differs from raw manifest")
            files.append(file_entry(path, args.out.parent))
    script_path = Path(__file__).with_name("analysis.py")
    analysis.require(analysis.sha(script_path) == protocol["analysis_plan"]["script"]["sha256"], "analysis code differs from protocol")
    arms = []
    for planned in protocol["arms"]:
        observed = observed_arm_ids.get(planned["id"], (None, None))
        arms.append({"id": planned["id"], "role": planned["role"], "commit": observed[0], "binary_sha256": observed[1]})
    source_ids = {value[0] for value in observed_arm_ids.values()}
    analysis.require(len(source_ids) <= 1, "multiple observed source commits")
    export = {"schema": "experiment.export/v1", "export_id": args.export_id,
              "created": datetime.now(timezone.utc).isoformat(),
              "protocol": {"path": os.path.relpath(args.protocol, args.out.parent), "sha256": protocol["freeze"]["protocol_sha256"],
                           "protocol_id": protocol["protocol_id"], "version": protocol["version"], "seed_nonce": args.external_nonce},
              "producer": {"runtime": args.producer_runtime, "model": args.producer_model, "session": args.producer_session, "role": args.producer_role},
              "source": {"repo": "isogeny-labs/crypto-autoresearcher", "commit": next(iter(source_ids)) if source_ids else None, "dirty": None},
              "backend": "isolab-k8s", "host": {"path": os.path.relpath(args.raw_manifest, args.out.parent), "sha256": analysis.sha(args.raw_manifest),
                                               "class_id": None, "summary": host_summary},
              "arms": arms, "runs": runs, "flow": ep.compute_flow(runs), "files": files,
              "analysis": {"script": file_entry(script_path, args.out.parent, "analysis"), "blinded": False, "blinding_key_sha256": None,
                           "outputs": [file_entry(args.analysis_summary, args.out.parent, "analysis")] if args.analysis_summary is not None else [], "unmasked_at": None},
              "notes": [{"kind": "observation", "by": "endpoint-reuse export adapter", "text": "One row is one actual child execution with64sequential targetslots. Rusage is not duplicated pertarget. Native counter sequences are JSON-encoded exact arrays by eventkind/field; nested values are not summed into a runtime price."},
                        {"kind": "observation", "by": "endpoint-reuse export adapter", "text": "Whole-child CPU includes parsing, common validation, setup, alltargetwork, traceI/O and teardown; tracevolume differs byarm. All clocks remain invalid in this unqualified worker adapter. Independent public verification does not attest native counters, timing, scientific review or the complete curve order."}],
              "reviews_dir": "reviews",
              "backend_record": {"planned_execution_flow": manifest.get("flow"), "unattempted_execution_metadata": unattempted,
                                 "planned_target_cases": 49152, "observed_target_cases": total_target_rows,
                                 "public_target_ids": 8192, "analysis_summary_sha256": analysis.sha(args.analysis_summary) if args.analysis_summary is not None else None,
                                 "format_scope": "v1 attempts requires>=1; unattempted children remain outside runs. Incomplete actual coverage is not padded and officialcheck-export may report it."}}
    findings = ep.schema_errors(export, "experiment.export/v1") or ep.lint_export(export, protocol, args.out.parent, True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        stream.write(json.dumps(export, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n")
    diagnostic = args.out.with_name(args.out.name + ".validation.json")
    with diagnostic.open("x") as stream:
        json.dump({"findings": findings, "actual_execution_rows": len(runs), "unattempted_metadata_records": len(unattempted),
                   "planned_execution_rows": 768, "export_bytes": args.out.stat().st_size,
                   "canonical_storage_required_before_publication": args.out.stat().st_size > 1048576}, stream, indent=2)
        stream.write("\n")
    if findings:
        print("Export retained with actual findings; no execution or counter rows were fabricated:", *findings, sep="\n")
    raise SystemExit(1 if findings else 0)

if __name__ == "__main__":
    main()
