#!/usr/bin/env python3
"""Package source observations and explicit candidate advice; no admission test."""
from pathlib import Path
import datetime as dt
import gzip
import hashlib
import json
import subprocess
import yaml

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args], stderr=subprocess.PIPE)


def write(name, data):
    raw = (json.dumps(data, indent=2, default=str) + "\n").encode()
    payload = gzip.compress(raw, mtime=0) if name.endswith(".gz") else raw
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
    return {"path": path.relative_to(REPO).as_posix(), "bytes": len(payload), "sha256": sha(payload)}


def unwrap(doc):
    return next((v for v in doc.values() if isinstance(v, dict) and isinstance(v.get("id"), str)), doc) if isinstance(doc, dict) else doc


def main():
    evidence_raw = (ROOT / "source-evidence.json.gz").read_bytes()
    evidence = json.loads(gzip.decompress(evidence_raw))
    notes_raw = (ROOT / "candidate-assessments.json").read_bytes()
    notes = json.loads(notes_raw)
    refs = evidence["source_commits"]
    assert refs == notes["source_commits"]
    bindings = {"source_commits": refs, "source_evidence_sha256": sha(evidence_raw),
                "candidate_assessments_sha256": sha(notes_raw),
                "collector_sha256": evidence["collector_sha256"],
                "reader_sha256": evidence["reader_sha256"],
                "builder_sha256": sha(Path(__file__).read_bytes())}
    local = evidence["snapshots"]["local"]
    def source(snapshot, iid):
        if iid in snapshot["sources"]:
            return snapshot["sources"][iid]
        row = snapshot["related_source_documents"][iid]
        return {"path":row["path"], "sha256":row["sha256"], "body":row["document"]["idea"]}
    context_paths = {
        "experiments/EXP-ECRANK-73275e/specification.yaml", "experiments/EXP-ECRANK-76a70d/specification.yaml",
        "experiments/EXP-GRUMPY-eaaa12/specification.yaml", "experiments/EXP-SIG-c5d288/specification.yaml",
        "ledger/decisions/DEC-20260905-d6878d.yaml",
        "coordination/ecc-idea-refinements-20260905-7196b6/refinement-plan.json",
    }
    for row in notes["candidates"]:
        b = source(local, row["preferred_source_id"])["body"]
        q = b["question_id"]
        context_paths.update((f"ledger/questions/{q}.yaml", f"ledger/{q}.yaml"))
        goals = set(b.get("goal_ids") or [])
        if isinstance(b.get("goal_id"), str):
            goals.add(b["goal_id"])
        for goal in goals:
            context_paths.update((f"ledger/goals/{goal}/goal.yaml", f"ledger/goals/{goal}.yaml"))
    contexts = {}
    for label, commit in refs.items():
        contexts[label] = {}
        for path in sorted(context_paths):
            try:
                raw = git("show", commit + ":" + path)
            except subprocess.CalledProcessError:
                continue
            error = None
            try:
                doc = json.loads(raw) if path.endswith(".json") else yaml.safe_load(raw)
                body = unwrap(doc)
            except (ValueError, yaml.YAMLError) as exc:
                doc = body = None
                error = str(exc)
            contexts[label][path] = {"sha256": sha(raw), "bytes": len(raw),
                "parsed_document": doc, "body": body, "parse_error": error,
                "raw_text_on_parse_error": raw.decode() if error else None}
    context_ref = write("context-sources.json.gz", {"schema":"crypto.autoresearch.bounded_candidate_context.v1",
        **bindings, "snapshots": contexts, "scope":"Internal source observations only; external references are not retrieved by this audit."})
    summaries, packets = [], []
    for advice in notes["candidates"]:
        iid, preferred = advice["inventory_id"], advice["preferred_source_id"]
        selected = source(local, preferred)
        b = selected["body"]
        assert b["status"] == "proposed"
        current_sources = {}
        custody = {}
        references = {}
        for label, snapshot in evidence["snapshots"].items():
            actual = source(snapshot, preferred)
            assert actual["sha256"] == selected["sha256"], (iid,label)
            current_sources[label] = {"commit":snapshot["commit"], "path":actual["path"],
                "sha256":actual["sha256"], "status":actual["body"]["status"],
                "question_id":actual["body"]["question_id"], "source_priority":actual["body"].get("recommended_priority")}
            producer = actual["body"].get("task_id") or actual["body"].get("proposed_under_task")
            rows, refs_for_candidate = [], []
            tokens = {iid, preferred} | set(local["same_title_neighbors_not_assumed_aliases"][iid])
            for path, doc in snapshot["reference_documents"].items():
                matches = [o for o in doc["occurrences"] if o["token"] in tokens]
                if matches:
                    refs_for_candidate.append({"path":path, "sha256":doc["sha256"],
                        "record_kind":doc["record_kind"], "record_id":doc["record"].get("id") if doc["record"] else None,
                        "occurrences":matches})
                if not doc["queue"]:
                    continue
                for task in doc["queue"]["tasks"]:
                    archive = task.get("archive") or {}
                    if not producer or not (task.get("id") == producer or producer in archive.get("source_task_ids", [])):
                        continue
                    row = {"queue_path":path,"queue_sha256":doc["sha256"],"task_id":task["id"],
                        "role":task.get("role"),"recorded_state":task.get("state"),
                        "archive_kind":archive.get("kind"),"archive_commit":archive.get("commit_sha"),
                        "declared_source_sha256":archive.get("path_sha256",{}).get(actual["path"]),
                        "effective_queue_authority_selected":False}
                    if row["archive_commit"] and row["declared_source_sha256"]:
                        commit = row["archive_commit"]
                        raw = git("show",commit+":"+actual["path"])
                        parent = git("rev-parse",commit+"^").decode().strip()
                        rc = subprocess.run(["git","-C",str(REPO),"merge-base","--is-ancestor",commit,snapshot["commit"]], capture_output=True).returncode
                        row["source_blob_verification"] = {"actual_sha256":sha(raw),
                            "matches_declared_and_current":sha(raw)==actual["sha256"]==row["declared_source_sha256"],
                            "archive_ancestor_of_snapshot":rc==0,"actual_parent":parent,
                            "matches_declared_parent":parent==archive.get("parent_sha"),
                            "scope":"Only selected source blob, commit ancestry, and declared parent checked; no full archive-completion or admission verdict."}
                    rows.append(row)
            custody[label] = {"declared_origin_task":producer,"observed_queue_entries":rows,
                "current_source_intake_allowed_without_origin_task_archive":True}
            references[label] = refs_for_candidate
        hash_bound = any(r.get("source_blob_verification",{}).get("matches_declared_and_current") and
                         r["source_blob_verification"]["archive_ancestor_of_snapshot"]
                         for r in custody["local"]["observed_queue_entries"])
        question_paths = [p for p in contexts["local"] if p.endswith('/'+b['question_id']+'.yaml')]
        question_errors = [p for p in question_paths if contexts["local"][p]["parse_error"]]
        packet = {"schema":"crypto.autoresearch.source_bound_design_candidate_packet.v1",**bindings,
            "context_sources":context_ref, "candidate_advice":advice,"current_sources":current_sources,
            "source_excerpts":{k:b.get(k) for k in ["title","mechanism","minimal_test","falsification_conditions",
                "assumptions","proof_search_map","interpretation_limits","novelty_status","novelty_screen",
                "citations","source_refs","supersedes","corrects","record_bindings"]},
            "source_custody":custody, "parsed_and_text_reference_evidence":references,
            "question_source_paths":question_paths,"question_parse_impediments":question_errors,
            "ownership_observation":{"specific_design_owner_verified":False,"owner":None,
                "meaning":"No owner for this exact mechanism has been established by this bounded audit. Parsed H/EXP and handoff references, aliases, comparator-only associations and competing source-generation queues are retained; absence of an exact token is not proof of orphanhood.",
                "admission_verified":False,"recheck":"Before admission, reconcile these pinned references with fresh local/main source changes, current dispatch selection, dependencies and claims."},
            "source_blob_bound_to_historical_archive":hash_bound,"source_provenance":"internal",
            "external_citations_retrieved_by_this_audit":False,"scientific_runs":0,"experiment_approved":False,
            "status_scope":"Source packet for Coordinator design consideration only; no experiment-readiness status assigned."}
        ref = write(f"candidates/{preferred}.json",packet)
        packets.append(ref)
        summaries.append({"rank":advice["rank"],"inventory_id":iid,"preferred_source_id":preferred,
            "title":b['title'],"question_id":b['question_id'],"recorded_priority":b.get('recommended_priority'),
            "source_sha256":selected['sha256'],"source_archive_blob_verified":hash_bound,
            "question_parse_impediments":question_errors,"uncertainty":advice['uncertainty'],
            "next_design_gate":advice['technical_blockers'][0],"advice":advice['advice'],"packet":ref})
    runtime = json.loads((ROOT.parent/'current-refresh-20260908/runtime-provenance.json').read_text())
    summary = {"schema":"crypto.autoresearch.bounded_design_candidate_audit_summary.v1",**bindings,
        "recorded_at":dt.datetime.now(dt.timezone.utc).isoformat(),"candidate_family_count":len(summaries),
        "screened_existing_chain_exclusions":evidence['screened_owned_ids'],
        "source_archive_blob_verified_count":sum(r['source_archive_blob_verified'] for r in summaries),
        "direct_current_source_without_declared_origin_archive_count":sum(not r['source_archive_blob_verified'] for r in summaries),
        "preferred_corrected_successor_count":sum(r['inventory_id']!=r['preferred_source_id'] for r in summaries),
        "question_parse_impediment_packet_count":sum(bool(r['question_parse_impediments']) for r in summaries),
        "ranking_authority":notes['authority'],"ranking_basis":notes['ranking_basis'],
        "native_runtime_observation":{k:runtime[k] for k in ['session_id','agent_path','model_provider','resolved_model_id','reasoning_effort','model_verified','session_meta_sha256','first_turn_context_sha256']},
        "scientific_runs":0,"new_hypotheses":0,"approved_experiments":0,"admitted_tasks":0,
        "source_workdir":str(REPO),"candidates":summaries,
        "procedure_deviations":[{"action":"Accidental zero-byte placeholder created at coordination/pending-ideas-swarm-placeholder outside assigned scope.","correction":"Verified exactly empty and immediately removed the agent's own newly created file; parent informed. No existing record changed."}],
        "next_action":"Parent verifies artifact hashes, selects candidate designs against live ownership/priority, resolves exact question and source-correction bindings, and creates committed frozen design handoffs; no user reapproval is needed.",
        "packets":packets}
    result=write('summary.json',summary)
    print(json.dumps({'summary':result,'families':len(summaries),'archive_bound':summary['source_archive_blob_verified_count'],
                      'question_parse_impediments':summary['question_parse_impediment_packet_count']}),flush=True)


if __name__ == '__main__':
    main()
