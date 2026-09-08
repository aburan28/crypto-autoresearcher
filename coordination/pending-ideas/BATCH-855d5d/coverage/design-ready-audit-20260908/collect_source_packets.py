#!/usr/bin/env python3
"""Read-only, bounded source/custody evidence collection for twelve candidates.

Uses the existing pinned GitSnapshot and scalar parser. Exact-ID searches are
discovery inputs, never an orphanhood or admission test. No scientific runs.
"""
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
REFS = {"local": "359a5f68019dd60ef7a507c47b96f537ade7eb63",
        "origin_main": "e8161aa34f8ea33142742bddbc228c7c98643fc6"}
CANDIDATES = [
    "IDEA-20260906-a3d6ae", "IDEA-20260905-9f7bc1",
    "IDEA-20260905-fbe4a0", "IDEA-20260905-f31728",
    "IDEA-20260905-d76d38", "IDEA-20260906-a7270e",
    "IDEA-20260906-ae1cfa", "IDEA-20260906-a056ea",
    "IDEA-20260906-69b3fc", "IDEA-20260906-f9f8c8",
    "IDEA-20260906-b1a568", "IDEA-20260906-6b84ec",
]
SCREENED_OWNED = {
    "IDEA-20260906-c8f2f6": "EXP-SATIC-201dea",
    "IDEA-20260906-9f56ad": "EXP-SATIC-6951b0",
    "IDEA-20260906-a77711": "EXP-FROB-d8aa37",
    "IDEA-20260906-86cd30": "EXP-RELN-164ad3",
    "IDEA-20260905-b1f9f0": "EXP-CRYPTO-5e8beb",
    "IDEA-20260905-3e4bf0": "EXP-CRYPTO-6505c6",
    "IDEA-20260906-5d2fd9": "EXP-FROB-0d885c",
}
sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def write(name, obj):
    raw = (json.dumps(obj, indent=2, default=str) + "\n").encode()
    payload = gzip.compress(raw, mtime=0) if name.endswith(".gz") else raw
    with (ROOT / name).open("xb") as stream:
        stream.write(payload)
    return {"path": (ROOT / name).relative_to(REPO).as_posix(), "bytes": len(payload),
            "sha256": sha(payload), "uncompressed_sha256": sha(raw)}


def main():
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    prior_path = ROOT.parent / "current-refresh-20260908/worklist.json.gz"
    prior_raw = prior_path.read_bytes()
    prior = json.loads(gzip.decompress(prior_raw))
    prior_rows = {r["id"]: r for r in prior["rows"]}
    assert len(CANDIDATES) == len(set(CANDIDATES)) == 12
    for iid in CANDIDATES:
        row = prior_rows[iid]
        assert row["classification"] == "ecc_explicit" and row["any_explicit_proposed"]
        assert row["proposed_operational_partition"] == "audit_source_and_lifecycle_before_new_design"
        assert not row["source_backed_experiment_link_present"]
    reader_path = REPO / "tools/pending_idea_coverage.py"
    code = reader_path.read_bytes()
    assert code == git("show", REFS["local"] + ":tools/pending_idea_coverage.py")
    spec = importlib.util.spec_from_file_location("bounded_source_reader", reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    refs_before = {r: git("rev-parse", r).decode().strip() for r in ("HEAD", "origin/main")}
    aliases = {iid: [r["id"] for r in prior["rows"] if r["id"] != iid and
                      r["title"] == prior_rows[iid]["title"]] for iid in CANDIDATES}
    snapshots = {}
    for label, commit in REFS.items():
        snap = reader.GitSnapshot(REPO, commit, 16 * 1024 * 1024)
        sources = {}
        origin_tasks = set()
        neighbors = set()
        classify = reader.pinned_classifier(snap)
        for iid in CANDIDATES + list(SCREENED_OWNED):
            path = f"ledger/proposals/{iid}.yaml"
            doc = snap.document(path)
            assert isinstance(doc, dict) and isinstance(doc.get("idea"), dict), path
            body = doc["idea"]
            assert body["id"] == iid and body.get("status") == "proposed", iid
            cl = classify(body.get("question_id"))
            assert cl["classification"] == "ecc", (iid, cl)
            task = body.get("task_id") or body.get("proposed_under_task")
            if task:
                origin_tasks.add(task)
            screen = body.get("novelty_screen", {})
            for _, value in reader.scalars(screen):
                neighbors.update(reader.IDEA_TOKEN.findall(value))
            sources[iid] = {"path": path, "sha256": snap.manifest[path]["sha256"],
                            "classification": cl, "body": body, "declared_origin_task": task}
        tokens = set(CANDIDATES) | set(SCREENED_OWNED) | origin_tasks | set(
            a for group in aliases.values() for a in group)
        command = ["git", "-C", str(REPO), "grep", "-I", "-l", "-z", "-F"]
        for token in sorted(tokens):
            command += ["-e", token]
        command += [commit, "--", "ledger", "experiments", "coordination", "ideas"]
        result = subprocess.run(command, capture_output=True)
        assert result.returncode in (0, 1), result.stderr
        paths = [p.decode().split(":", 1)[1] for p in result.stdout.split(b"\0") if p]
        documents = {}
        for path in sorted(set(paths)):
            raw = snap.read(path, cache=False)
            if raw is None:
                continue
            if Path(path).suffix not in {".yaml", ".yml", ".json", ".md", ".txt", ".py", ".tsv"}:
                continue
            try:
                text = raw.decode()
            except UnicodeError:
                continue
            doc = snap.document(path, cache=False) if Path(path).suffix in {".yaml", ".yml", ".json"} else None
            occurrences = [{"token": token, "field": field, "exact_scalar": token == value,
                            "value": value} for field, value in reader.scalars(doc)
                           for token in sorted(tokens) if token in value] if doc is not None else []
            line_hits = [{"line": n, "text": line} for n, line in enumerate(text.splitlines(), 1)
                         if any(t in line for t in tokens)]
            body_kind = next((k for k in ("experiment", "hypothesis", "handoff", "decision")
                              if isinstance(doc, dict) and isinstance(doc.get(k), dict)), None)
            documents[path] = {"sha256": sha(raw), "parsed": doc is not None,
                "schema": doc.get("schema") if isinstance(doc, dict) else None,
                "record_kind": body_kind, "record": doc.get(body_kind) if body_kind else None,
                "occurrences": occurrences, "matching_lines": line_hits,
                "queue": doc if isinstance(doc, dict) and doc.get("schema") == reader.QUEUE_SCHEMA else None}
        related = {}
        for iid in sorted(neighbors | set(a for group in aliases.values() for a in group)):
            path = f"ledger/proposals/{iid}.yaml"
            if path in snap.entries:
                doc = snap.document(path)
                related[iid] = {"path": path, "sha256": snap.manifest[path]["sha256"], "document": doc}
        registry = snap.document("tools/schema_supersession_registry.yaml")
        candidate_registry = [r for r in registry.get("records", []) if any(
            iid in json.dumps(r) for iid in tokens)]
        snapshots[label] = {"commit": commit, "sources": sources,
            "same_title_neighbors_not_assumed_aliases": aliases,
            "explicit_schema_registry_matches": candidate_registry,
            "query": {"method": "Committed git grep -I -l -z -F over exact identifiers and declared origin tasks.",
                      "tokens": sorted(tokens), "scopes": ["ledger", "experiments", "coordination", "ideas"],
                      "exit_code": result.returncode, "matched_paths": paths,
                      "stdout_sha256": sha(result.stdout), "stderr": result.stderr.decode()},
            "reference_documents": documents, "related_source_documents": related,
            "input_manifest": list(snap.manifest.values()), "diagnostics": snap.diagnostics}
        print(json.dumps({"snapshot": label, "commit": commit, "matched_paths": len(paths),
                          "parsed_or_text_documents": len(documents), "diagnostics": len(snap.diagnostics)}), flush=True)
        snap.close()
    bindings = {"source_commits": REFS, "reader_sha256": sha(code),
        "collector_sha256": sha(Path(__file__).read_bytes()),
        "prior_inventory": {"path": prior_path.relative_to(REPO).as_posix(), "sha256": sha(prior_raw),
                            "source_commit": prior["source_commit"]}}
    data = {"schema": "crypto.autoresearch.bounded_candidate_source_evidence.v1", **bindings,
        "candidate_ids": CANDIDATES, "screened_owned_ids": SCREENED_OWNED,
        "snapshots": snapshots, "scientific_runs": 0,
        "scope": "Source/custody diagnostic; exact-reference absence proves neither orphanhood nor admission."}
    output = write("source-evidence.json.gz", data)
    write("collection-receipt.json", {"schema": "crypto.autoresearch.bounded_candidate_collection_receipt.v1",
        **bindings, "started_at": started, "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "refs_before": refs_before, "refs_after": {r:git("rev-parse",r).decode().strip() for r in ("HEAD", "origin/main")},
        "candidate_ids": CANDIDATES, "screened_owned_ids": SCREENED_OWNED, "output": output,
        "scientific_runs": 0, "write_scope": str(ROOT.relative_to(REPO)),
        "limitations": ["Only the selected source identifiers, declared origin tasks, and same-title candidates were searched.",
                        "Same title is a comparison cue, not a canonical alias or duplicate verdict.",
                        "Queue and source status fields are observed markers; effective authority requires separate reconciliation.",
                        "No external citation retrieval, scientific experiment, or research-state decision occurred."]})
    print(json.dumps(output), flush=True)


if __name__ == "__main__":
    main()
