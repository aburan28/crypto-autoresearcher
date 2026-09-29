#!/usr/bin/env python3
"""Verify and seal this bounded operational packet set; no research decisions."""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], stderr=subprocess.PIPE)


def write(name, data):
    with (ROOT / name).open("xb") as stream:
        stream.write((json.dumps(data, indent=2, default=str) + "\n").encode())


def main():
    summary = json.loads((ROOT / "summary.json").read_text())
    evidence = json.loads(gzip.decompress((ROOT / "source-evidence.json.gz").read_bytes()))
    contexts = json.loads(gzip.decompress((ROOT / "context-sources.json.gz").read_bytes()))
    pins = summary["source_commits"]
    binding = {"source_commits": pins, "summary_sha256": sha((ROOT / "summary.json").read_bytes()),
               "source_evidence_sha256": sha((ROOT / "source-evidence.json.gz").read_bytes()),
               "finalizer_sha256": sha(Path(__file__).read_bytes())}
    before = {ref: git("rev-parse", ref).decode().strip() for ref in ["HEAD", "origin/main"]}
    checked = []
    for label, snapshot in evidence["snapshots"].items():
        manifest = {row["path"]: row["sha256"] for row in snapshot["input_manifest"]}
        manifest.update({p: d["sha256"] for p, d in contexts["snapshots"][label].items()})
        for path, expected in sorted(manifest.items()):
            actual = sha(git("show", pins[label] + ":" + path))
            assert actual == expected, (label, path)
        checked.append({"snapshot": label, "source_commit": pins[label], "verified_source_path_count": len(manifest)})
    tool_path = "tools/ecc_priority.py"
    tool_bytes = git("show", pins["local"] + ":" + tool_path)
    assert tool_bytes == (REPO / tool_path).read_bytes()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("audit_ecc_priority", REPO / tool_path)
    ecc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ecc)
    qualifications, corrections, tokens = [], [], set()
    for row in summary["candidates"]:
        path = REPO / row["packet"]["path"]
        assert sha(path.read_bytes()) == row["packet"]["sha256"]
        packet = json.loads(path.read_text())
        tokens.update((row["inventory_id"], row["preferred_source_id"]))
        tokens.update(evidence["snapshots"]["local"]["same_title_neighbors_not_assumed_aliases"][row["inventory_id"]])
        classes = {}
        for label, src in packet["current_sources"].items():
            raw = git("show", pins[label] + ":" + src["path"])
            b = yaml.safe_load(raw)["idea"]
            assert sha(raw) == src["sha256"] and b["status"] == "proposed"
            policy_raw = git("show", pins[label] + ":orchestration/research-priority.yaml")
            policy = yaml.safe_load(policy_raw)
            assert ecc.is_ecc(b["question_id"], policy)
            classes[label] = {"status": b["status"], "question_id": b["question_id"],
                "area": ecc.area_of(b["question_id"]), "classification": "explicit_ecc",
                "policy_sha256": sha(policy_raw), "canonical_reader_sha256": sha(tool_bytes)}
            for observed in packet["source_custody"][label]["observed_queue_entries"]:
                v = observed.get("source_blob_verification")
                if v:
                    assert v["matches_declared_and_current"] and v["archive_ancestor_of_snapshot"] and v["matches_declared_parent"]
        qualifications.append({"inventory_id": row["inventory_id"], "preferred_source_id": row["preferred_source_id"], "snapshots": classes})
        rb = packet["source_excerpts"].get("record_bindings") or {}
        if rb.get("predecessor_path"):
            checks = {}
            for label, commit in pins.items():
                checks[label] = {
                    "predecessor_hash_matches": sha(git("show", commit + ":" + rb["predecessor_path"])) == rb["predecessor_sha256"],
                    "predecessor_snapshot_hash_matches": sha(git("show", rb["predecessor_snapshot_commit"] + ":" + rb["predecessor_path"])) == rb["predecessor_sha256"],
                    "refinement_plan_hash_matches": sha(git("show", commit + ":" + rb["refinement_plan_path"])) == rb["refinement_plan_sha256"]}
                assert all(checks[label].values())
            corrections.append({"selected_source_id": row["preferred_source_id"], "bindings": rb, "checks": checks})
    assert len(qualifications) == 12 and len({r["preferred_source_id"] for r in qualifications}) == 12
    excluded = []
    for iid, eid in evidence["screened_owned_ids"].items():
        snapshots = {}
        for label, snapshot in evidence["snapshots"].items():
            refs = []
            for path, doc in snapshot["reference_documents"].items():
                if doc["record_kind"] not in ("hypothesis", "experiment"):
                    continue
                occurrences = [o for o in doc["occurrences"] if o["token"] == iid]
                if occurrences:
                    refs.append({"path": path, "sha256": doc["sha256"], "record_kind": doc["record_kind"],
                                 "record_id": doc["record"].get("id"), "occurrences": occurrences})
            assert any(r["record_id"] == eid for r in refs)
            snapshots[label] = refs
        excluded.append({"idea_id": iid, "existing_experiment_id": eid, "references": snapshots,
            "disposition": "Exclude from new candidate designs; preserve the existing chain. Effective admission is not evaluated."})
    write("excluded-existing-chains.json", {"schema": "crypto.autoresearch.bounded_chain_exclusions.v1", **binding,
        "excluded_count": len(excluded), "exclusions": excluded, "scientific_runs": 0})
    deltas = {}
    for label, ref in [("local", "HEAD"), ("origin_main", "origin/main")]:
        current = before[ref]
        paths = git("diff", "--name-only", pins[label], current, "--", "ledger", "experiments", "coordination", "ideas").decode().splitlines()
        relevant = []
        for path in paths:
            try:
                raw = git("show", current + ":" + path)
            except subprocess.CalledProcessError:
                relevant.append({"path": path, "status": "deleted_or_unreadable", "requires_reconciliation": True})
                continue
            hits = [t for t in sorted(tokens) if t.encode() in raw]
            if hits:
                relevant.append({"path": path, "sha256": sha(raw), "matched_candidate_or_alias_tokens": hits,
                                 "requires_reconciliation": True})
        deltas[label] = {"pinned_commit": pins[label], "observed_commit": current, "changed_paths": paths,
                         "candidate_or_alias_matches_in_changed_sources": relevant,
                         "limit": "Exact token screening of intervening changes only; semantic aliases or undeclared ownership may be missed."}
    after = {ref: git("rev-parse", ref).decode().strip() for ref in ["HEAD", "origin/main"]}
    assert after == before, "Ref moved during final delta screen; inspect and retry in a new receipt."
    parsed = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".json.gz"):
            json.loads(gzip.decompress(path.read_bytes()))
            parsed.append(path.relative_to(ROOT).as_posix())
        elif path.suffix == ".json":
            json.loads(path.read_text())
            parsed.append(path.relative_to(ROOT).as_posix())
        elif path.suffix == ".py":
            compile(path.read_text(), str(path), "exec")
    write("verification.json", {"schema": "crypto.autoresearch.bounded_candidate_packet_verification.v1", **binding,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(), "source_paths_rehashed": checked,
        "candidate_qualifications": qualifications, "correction_lineage_checks": corrections,
        "source_bound_archive_checks": "All recorded source-blob, ancestry and parent checks are true on both pins; no full archive/admission verification.",
        "parsed_artifacts": parsed, "refs_before": before, "refs_after": after, "intervening_changes": deltas,
        "scientific_runs": 0, "tests_added": 0, "research_status_changes": 0,
        "limitation": "Mechanical artifact/source verification only; source predictions, quoted citation provenance, and mathematical arguments are not independently validated."})
    rows = []
    for row in summary["candidates"]:
        iid = row["preferred_source_id"]
        short_title = row["title"] if iid != "IDEA-20260906-a3d6ae" else "Batch-grown table with relation-graph accounting"
        alias = "" if row["inventory_id"] == iid else f" (corrects `{row['inventory_id']}`)"
        rows.append(f"| {row['rank']} | [{iid}](candidates/{iid}.json){alias} | {short_title} | {row['next_design_gate']} |")
    readme = f"""# Bounded source packets for Coordinator design consideration

Twelve explicitly ECC, literally `proposed` source families were traced from the earlier 452-item source/lifecycle-audit partition. These are advisory design inputs. This report creates zero hypotheses, approvals, admitted tasks, scientific runs, or status changes. The directory name does not assign readiness.

The source pins are local `{pins['local']}` and fetched `origin/main` `{pins['origin_main']}`. Every source was read from committed Git objects. Dirty/untracked work was excluded. The prior inventory remains pinned to `3d69283a97f1cf418074da752384c9048df5a083`; 452 is that historical partition, not a fresh all-pending denominator. The retained original denominator evidence is in the prior inventory. [summary.json](summary.json) binds every candidate packet, [verification.json](verification.json) records current-source hashes and final ref deltas, and [artifact-manifest.json](artifact-manifest.json) seals this directory.

| Advisory order | Preferred current source | Mechanism | First design gate |
| --- | --- | --- | --- |
{chr(10).join(rows)}

This ordering is source/design-input advice. It does not override existing research priorities or authorize dispatch. Every packet preserves the source's recorded priority, uncertainty, controls, proof-map inputs, technical blockers, explicit neighboring records, and ownership observations. In particular, `9f7bc1` needs comparison with GOAL-ECRANK-002's existing coset optimizer and closure-candidate machinery before a new implementation. `ae1cfa` must preserve ownership of EXP-ECRANK-76a70d and EXP-ECRANK-73275e. The batch-table source `a3d6ae` explicitly requires a Stage0 primary-literature read; this audit retrieved no paper.

Two inventory IDs have explicit hash-bound corrected successors: `fbe4a0` to `f9df88` and `f31728` to `d8c55f`. Treat each as one family. Selected `d76d38` already corrects `66cf9a`. Correction bindings were rechecked against both source pins and their declared predecessor snapshots. No alias is inferred merely from equal titles.

Eleven selected source blobs match declared historical snapshot hashes, parent commits, and ancestry on both pins. This verifies source custody only, not every artifact in the original archive or current admission. `a3d6ae` declares no originating task archive; current-source intake can legitimately proceed without one. EXP-ECDLP-612fb1 explicitly describes this idea as cited, not designed. The report does not turn an absent token into an orphan verdict.

[excluded-existing-chains.json](excluded-existing-chains.json) preserves seven positive source-to-experiment chains screened out of this worklist: c8f2f6, 9f56ad, a77711, 86cd30, b1f9f0, 3e4bf0 and 5d2fd9. The parent's current 4dff7b/bf8898 and next c37df9/40aa90 are excluded separately by assignment. Source-generation authority queues still show queued entries beside completed, snapshot-bound dispatch copies; those are competing historical records requiring reconciliation, not permission to rerun generation.

Two legacy question files fail YAML parsing: `ledger/RQ-DREG-001.yaml` and `ledger/RQ-SIG-001.yaml`. This affects four packets (6b84ec, d76d38, d8c55f and f9df88). Their raw text and parser errors are retained in [context-sources.json.gz](context-sources.json.gz). A Coordinator must resolve canonical question routing or additive source repair before admission; this audit changes no question file. Explicit ECC classification uses the proposal's question identifier through the canonical policy reader and is separately verified despite the question parse defect.

The collector reuses the unchanged `pending_idea_coverage.py` GitSnapshot and scalar readers. Exact identifier, declared origin-task and same-title comparison queries yielded 351 reference documents on each pin, with no parse diagnostics inside that matched set. This is a bounded source search, not a semantic search over every possible alias. The separate context pass found the two question parse defects above. [source-evidence.json.gz](source-evidence.json.gz) contains source bodies, typed and text references, queue evidence and input hashes; copied citation claims retain their source authors' provenance and are not new retrieval claims by this audit. The finalizer rehashes inputs and screens intervening committed changes without changing the original pins.

Native runtime metadata observed OpenAI `gpt-6-astra`, reasoning effort `ultra`, session `01a07eb5-ae50-7c61-bcde-4697efe05c7c`. `model_verified` remains false. Actual command working directory was `/Volumes/SSD990/1083/pending-ideas-swarm-20260907`; metadata's initial cwd was the original checkout. No model-serving probe or Bedrock call was made.

All retained deliverables are within this assigned new directory. One accidental zero-byte placeholder outside scope was immediately verified empty and removed; the parent was informed, and no existing file was changed. The procedure deviation is retained in the summary.

The parent can select designs from these packets, reconcile question/alias/current ownership gates, and write committed frozen handoffs under standing authorization. No repeated user approval is needed. Fresh live dispatch, dependency and claim verification remains necessary before execution.
"""
    with (ROOT / "README.md").open("x") as stream:
        stream.write(readme)
    files = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_file():
            raw = path.read_bytes()
            files.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(raw), "sha256": sha(raw)})
    write("artifact-manifest.json", {"schema": "crypto.autoresearch.bounded_candidate_audit_manifest.v1", **binding,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(), "write_scope": ROOT.relative_to(REPO).as_posix(),
        "files": files, "file_count_excluding_manifest": len(files), "total_bytes_excluding_manifest": sum(r["bytes"] for r in files),
        "self_hash_policy": "Manifest excludes itself; its SHA256 is reported to the parent.",
        "scientific_runs": 0, "model_verified": False,
        "scope": "Internal source/custody packet generation and mechanical verification. Candidate advice only, not admission or scientific evidence."})
    print(json.dumps({"manifest_sha256": sha((ROOT / "artifact-manifest.json").read_bytes()),
        "files": len(files) + 1, "candidate_families": 12, "source_paths_rehashed": checked,
        "delta_candidate_matches": {k: v['candidate_or_alias_matches_in_changed_sources'] for k, v in deltas.items()}}), flush=True)


if __name__ == "__main__":
    main()
