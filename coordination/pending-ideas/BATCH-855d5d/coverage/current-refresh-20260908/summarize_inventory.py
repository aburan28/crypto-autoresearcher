#!/usr/bin/env python3
"""Project unchanged coverage outputs into an explicitly unadjudicated worklist.

The source pin and source/tool hashes are inherited from scan-receipt.json.
Raw source reads only disambiguate literal status presence, never lifecycle.
"""
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml

PIN = "3d69283a97f1cf418074da752384c9048df5a083"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def readgz(name):
    return json.loads(gzip.decompress((OUT / name).read_bytes()))


def save(name, data, compress=False):
    raw = (json.dumps(data, indent=2, default=str) + "\n").encode()
    payload = gzip.compress(raw, compresslevel=9, mtime=0) if compress else raw
    with (OUT / name).open("xb") as stream:
        stream.write(payload)
    return {"path": (OUT / name).relative_to(REPO).as_posix(), "bytes": len(payload),
            "sha256": sha(payload), "uncompressed_sha256": sha(raw)}


def main():
    receipt = json.loads((OUT / "scan-receipt.json").read_text())
    assert receipt["source_commit"] == PIN
    pending = readgz("pending-coverage.json.gz")
    broad = readgz("broader-lineage.json.gz")["tool_report_preserved"]
    for ref in receipt["reports"]:
        assert sha((REPO / ref["path"]).read_bytes()) == ref["sha256"]
    tool_path = REPO / "tools/pending_idea_coverage.py"
    assert sha(tool_path.read_bytes()) == receipt["tool_and_policy_sha256"]["tools/pending_idea_coverage.py"]
    spec = importlib.util.spec_from_file_location("verified_inventory_reader", tool_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    snap = reader.GitSnapshot(REPO, PIN, 16 * 1024 * 1024)
    policy = snap.document("orchestration/research-priority.yaml")
    classifier = reader.pinned_classifier(snap)
    # Areas are assigned only by the pinned canonical policy; never by idea IDs.
    code = snap.read("tools/ecc_priority.py")
    mod = {"__file__": str(REPO / "tools/ecc_priority.py")}
    exec(compile(code, f"{PIN}:tools/ecc_priority.py", "exec"), mod)
    included = mod["ecc_areas"](policy)
    excluded = set(policy["excluded_areas"])
    registered_statuses = {r["idea_id"]: r for r in csv.DictReader(
        io.StringIO(snap.read("ideas/idea_registry.tsv").decode()), delimiter="\t")}
    routes = {r["path"]: r["effective_path"] for r in broad["schema_routing"]}
    primary = defaultdict(list)
    for r in pending["ideas"]:
        primary[r["id"]].append(r)
    broader = {r["id"]: r for r in broad["ideas"]}
    protocols = {r["effective_path"]: r for r in pending["protocols"]}
    prior_path = "coordination/pending-ideas/BATCH-855d5d/diagnostics/next-wave-candidates.json"
    parent_six = {r["id"] for r in snap.document(prior_path)["candidates"]}
    rows = []
    for iid in sorted(set(primary) | set(broader)):
        ps = primary.get(iid, [])
        br = broader.get(iid)
        observations = []
        if br:
            for loc in br["source_locations"]:
                path = routes.get(loc["path"], loc["path"])
                raw = snap.read(path)
                assert raw is not None and sha(raw) in br["source_sha256"], (iid, path)
                ob = {**loc, "effective_path": path, "sha256": sha(raw)}
                if loc["source_type"] == "legacy_markdown":
                    state = re.search(r"^- (?:State|Status):\s*`([^`]+)`", raw.decode(), re.M)
                    ob.update(status_present=bool(state), literal_status=state.group(1) if state else None,
                              status_basis="explicit_markdown_state_or_status" if state else "no_explicit_markdown_status")
                    if not state and iid in registered_statuses:
                        ob["registry_fallback_status"] = registered_statuses[iid].get("status")
                        ob["registry_path"] = "ideas/idea_registry.tsv"
                else:
                    doc = snap.document(path)
                    match = re.fullmatch(r"(ideas|proposals)\[(\d+)\]", loc["location"])
                    body = doc[match[1]][int(match[2])] if match else doc.get("idea", doc)
                    ob.update(status_present="status" in body, literal_status=body.get("status"),
                              status_basis="parsed_status_field")
                observations.append(ob)
        for pr in ps:
            if not any(o["effective_path"] == pr["effective_path"] for o in observations):
                observations.append({"path": pr["original_path"], "effective_path": pr["effective_path"],
                    "location": "document", "source_type": "primary_only_structured_record",
                    "status_present": pr["status_present"], "literal_status": pr["recorded_status"],
                    "status_basis": "unchanged_primary_tool_exact_status_field"})
        areas = set(br["areas"] if br else []) | {r["area"] for r in ps if r["area"]}
        inc, exc, unk = areas & included, areas & excluded, areas - included - excluded
        classification = "ecc_explicit" if inc else "non_ecc_explicit" if exc and not unk else "unclassified"
        primary_links = {p for r in ps for p in r["protocol_path_candidates"]}
        broad_links = {r["effective_path"] for r in br["experiments"]} if br else set()
        links = primary_links | broad_links
        source_types = sorted({o["source_type"] for o in observations})
        statuses = {json.dumps(o["literal_status"], default=str) for o in observations if o["status_present"]}
        ownership = {t["task_key"]: t for p in links for t in protocols.get(p, {}).get("owned_task_candidates", [])}
        signals = []
        if len(statuses) > 1:
            signals.append("differing_recorded_statuses_require_lifecycle_reconciliation")
        if len(observations) > 1:
            signals.append("multiple_source_locations_require_identity_and_history_reconciliation")
        if inc and exc:
            signals.append("included_and_excluded_area_sources_require_scope_reconciliation")
        if unk:
            signals.append("areas_absent_from_both_policy_sets_remain_unknown")
        if ps and br and bool(primary_links) != bool(broad_links):
            signals.append("tools_disagree_on_link_presence_with_different_discovery_or_source_field_rules")
        if len({o["queue_path"] for o in ownership.values()}) > 1:
            signals.append("multiple_queue_ownership_candidates_require_authority_selection")
        proposed = any(o["status_present"] and o["literal_status"] == "proposed" for o in observations)
        absent = any(not o["status_present"] for o in observations)
        partition = ("parent_owned_six_candidate_review" if iid in parent_six else
                     "reconcile_recorded_status_identity_or_classification" if signals and any(
                         w in s for s in signals for w in ("differing_recorded_statuses", "included_and_excluded")) else
                     "audit_existing_experiment_link_and_authority" if links else
                     "audit_source_and_lifecycle_before_new_design" if proposed else
                     "resolve_missing_status_and_lifecycle" if absent else "reconcile_recorded_lifecycle")
        rows.append({"id": iid, "title": br["title"] if br else ps[0]["title"],
            "classification": classification, "areas": sorted(areas), "policy_unknown_areas": sorted(unk),
            "classification_conflict": bool(inc and exc),
            "primary_tool_classifications": sorted({r["classification"] for r in ps}),
            "broader_tool_ecc": br["ecc"] if br else None,
            "broader_tool_classification_unresolved": br["classification_unresolved"] if br else None,
            "source_status_observations": observations, "source_types": source_types,
            "any_explicit_proposed": proposed, "any_status_absent": absent,
            "all_status_absent": all(not o["status_present"] for o in observations),
            "source_statuses_differ": len(statuses) > 1,
            "recorded_recommended_priority": br["recommended_priority"] if br else None,
            "primary_link_paths": sorted(primary_links), "broader_link_paths": sorted(broad_links),
            "source_backed_experiment_link_present": bool(links),
            "experiment_semantic_scope_verified": False,
            "legacy_contract_candidates": br["legacy_contract_candidates"] if br else [],
            "discovered_task_ownership_candidates": list(ownership.values()),
            "task_admission_audit": "not_performed", "admitted_task_count": None,
            "reconciliation_signals": signals, "proposed_operational_partition": partition,
            "research_priority_changed": False, "readiness_verified": False,
            "pending_lifecycle_verified": False})
    rows.sort(key=lambda r: ({"ecc_explicit": 0, "unclassified": 1, "non_ecc_explicit": 2}[r["classification"]],
        {"high": 0, "medium": 1, "low": 2}.get(r["recorded_recommended_priority"], 3), r["id"]))
    bindings = {"source_commit": PIN, "tool_and_policy_sha256": receipt["tool_and_policy_sha256"],
        "scan_receipt_sha256": sha((OUT / "scan-receipt.json").read_bytes()),
        "projection_script_sha256": sha(Path(__file__).read_bytes())}
    work = save("worklist.json.gz", {"schema": "crypto.autoresearch.unadjudicated_inventory_worklist.v1",
        **bindings, "authority": "Operational partition only; Coordinator owns scientific ranking and dispatch.",
        "order": "Policy-explicit ECC first, unresolved classification for binding, then explicitly excluded areas; existing recommended_priority and ID determine stable within-class presentation only.",
        "literal_denominator": "Union of discovered idea identifiers, all recorded statuses, without semantic deduplication or excluding historical lifecycle states.",
        "rows": rows}, True)
    statusobs = [o for r in rows for o in r["source_status_observations"]]
    summary = {"schema": "crypto.autoresearch.pending_inventory_refresh_summary.v1", **bindings,
        "literal_all_pending_discovery_universe": {"discovered_identifiers": len(rows),
            "discovered_source_locations": len(statusobs), "primary_identifiers": len(primary),
            "broader_identifiers": len(broader), "primary_only_identifiers": len(set(primary) - set(broader)),
            "broader_only_identifiers": len(set(broader) - set(primary)),
            "verified_pending_work_denominator": None,
            "meaning": "All-discovered universe retained for all-pending reconciliation; it includes every recorded status. This is not a count of proven pending, orphaned, approved, or runnable work."},
        "status_counts": {"ids_with_any_explicit_proposed": sum(r["any_explicit_proposed"] for r in rows),
            "ids_with_any_absent_status": sum(r["any_status_absent"] for r in rows),
            "ids_with_all_status_absent": sum(r["all_status_absent"] for r in rows),
            "ids_with_differing_recorded_statuses": sum(r["source_statuses_differ"] for r in rows),
            "source_locations_with_explicit_proposed": sum(o["status_present"] and o["literal_status"] == "proposed" for o in statusobs),
            "source_locations_with_status_absent": sum(not o["status_present"] for o in statusobs),
            "source_locations_by_literal_status": dict(Counter(str(o["literal_status"]) for o in statusobs if o["status_present"]))},
        "classification_counts": dict(Counter(r["classification"] for r in rows)),
        "ids_with_classification_conflict": sum(r["classification_conflict"] for r in rows),
        "broader_false_ecc_with_unknown_area_ids": sum(r["broader_tool_ecc"] is False and r["classification"] == "unclassified" for r in rows),
        "link_counts": {"ids_with_source_backed_experiment_link_candidate": sum(r["source_backed_experiment_link_present"] for r in rows),
            "ids_without_discovered_experiment_link": sum(not r["source_backed_experiment_link_present"] for r in rows),
            "ids_with_legacy_contract_candidates": sum(bool(r["legacy_contract_candidates"]) for r in rows),
            "ids_with_task_ownership_candidates": sum(bool(r["discovered_task_ownership_candidates"]) for r in rows),
            "admitted_task_count": None, "task_admission_audit": "not_performed"},
        "partitions": [{"classification": cls, "partition": part, "count": len(selected),
            "sample_ids_existing_priority_order": [r["id"] for r in selected[:12]]}
            for cls, part in sorted({(r["classification"], r["proposed_operational_partition"]) for r in rows})
            if (selected := [r for r in rows if (r["classification"], r["proposed_operational_partition"]) == (cls, part)])],
        "signals": dict(Counter(s for r in rows for s in r["reconciliation_signals"])),
        "primary_diagnostics": pending["summary"]["diagnostic_count"],
        "primary_diagnostics_by_code": dict(Counter(r["code"] for r in pending["diagnostics"])),
        "broader_parse_or_discovery_errors": len(broad["errors"]),
        "broader_duplicate_record_entries": len(broad["duplicate_records"]),
        "broader_unknown_source_ids": len(broad["unknown_source_ids"]),
        "parent_owned_six_candidate_ids": sorted(parent_six),
        "scientific_runs": 0, "readiness_verified": False, "completion_verified": False,
        "worklist": work}
    summary_ref = save("summary.json", summary)
    save("projection-inputs.json.gz", {"schema": "crypto.autoresearch.inventory_projection_sources.v1",
        **bindings, "reads": list(snap.manifest.values()), "diagnostics": snap.diagnostics}, True)
    snap.close()
    print(json.dumps({"summary_file": summary_ref,
        **{k:v for k,v in summary.items() if k not in {"partitions", "tool_and_policy_sha256"}}}, indent=2))


if __name__ == "__main__":
    main()
