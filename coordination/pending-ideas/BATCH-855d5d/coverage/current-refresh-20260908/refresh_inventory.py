#!/usr/bin/env python3
"""Package the existing coverage tools against one immutable source revision.

This wrapper copies committed inputs, calls the unchanged tools, hashes their
outputs, and removes its own temporary copy. It implements no coverage logic.
Run with Python 3.11+ and PyYAML, from the owning repository. Existing reports
are refused. The literal source pin is intentional and must not be rewritten.
"""
from __future__ import annotations

import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PIN = "3d69283a97f1cf418074da752384c9048df5a083"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
CODE_PATHS = (
    "tools/pending_idea_coverage.py", "tools/idea_experiment_coverage.py",
    "tools/ecc_priority.py", "tools/validate_ledger.py",
)
POLICY_PATHS = (
    "tools/schema_supersession_registry.yaml",
    "orchestration/research-priority.yaml",
)
sys.dont_write_bytecode = True


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def encoded(data):
    return (json.dumps(data, indent=2, ensure_ascii=True, default=str) + "\n").encode()


def output(name, data, compressed=False):
    raw = encoded(data)
    payload = gzip.compress(raw, compresslevel=9, mtime=0) if compressed else raw
    path = OUT / name
    with path.open("xb") as stream:
        stream.write(payload)
    return {"path": path.relative_to(REPO).as_posix(), "bytes": len(payload),
            "sha256": digest(payload), "uncompressed_bytes": len(raw),
            "uncompressed_sha256": digest(raw), "encoding": "gzip" if compressed else "json"}


def main():
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    assert git("rev-parse", "--show-toplevel").decode().strip() == str(REPO)
    assert git("rev-parse", f"{PIN}^{{commit}}").decode().strip() == PIN
    for name in ("pending-coverage.json.gz", "broader-lineage.json.gz",
                 "materialized-inputs.json.gz", "scan-receipt.json"):
        if (OUT / name).exists():
            raise FileExistsError(OUT / name)
    materialized = OUT / ".committed-inputs"
    materialized.mkdir()
    before = {ref: git("rev-parse", ref).decode().strip() for ref in ("HEAD", "origin/main")}
    entries = {}
    for item in git("ls-tree", "-r", "-l", "-z", PIN).split(b"\0"):
        if not item:
            continue
        meta, raw_path = item.split(b"\t", 1)
        mode, kind, oid, size = meta.decode().split()
        path = raw_path.decode()
        entries[path] = {"git_blob_id": oid, "mode": mode, "kind": kind,
                         "size_bytes": int(size) if size != "-" else None}

    def selected(path):
        p = Path(path)
        ledger = p.parts[0] == "ledger" and p.suffix == ".yaml" and (
            len(p.parts) == 2 or (len(p.parts) == 3 and p.parts[1] in
            {"proposals", "ideas", "hypotheses"}) or
            path.startswith("ledger/corrections/schema-supersessions/"))
        return ledger or (path.startswith("coordination/") and p.suffix in {".yaml", ".yml"}) or (
            path.startswith("ideas/") and p.suffix in {".md", ".yaml", ".yml", ".tsv"}) or (
            len(p.parts) == 3 and p.parts[0] == "experiments" and p.name == "specification.yaml") or (
            path in CODE_PATHS + POLICY_PATHS)

    selected_paths = {p for p in entries if selected(p)}
    import yaml
    registry = yaml.safe_load(git("show", f"{PIN}:tools/schema_supersession_registry.yaml"))
    for item in registry.get("records", []):
        selected_paths.update((item["superseded_path"], item["superseding_path"]))
    manifest = []
    process = subprocess.Popen(["git", "-C", str(REPO), "cat-file", "--batch"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for path in sorted(selected_paths):
            entry = entries[path]
            assert entry["kind"] == "blob" and entry["mode"] in {"100644", "100755"}, path
            process.stdin.write((entry["git_blob_id"] + "\n").encode())
            process.stdin.flush()
            header = process.stdout.readline().decode().split()
            assert len(header) == 3 and header[1] == "blob", path
            raw = process.stdout.read(int(header[2]))
            assert len(raw) == entry["size_bytes"] and process.stdout.read(1) == b"\n", path
            target = materialized / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(raw)
            manifest.append({"path": path, **entry, "sha256": digest(raw)})
    finally:
        process.stdin.close()
        process.stdout.close()
        assert process.wait() == 0
        process.stderr.close()
    tool_hashes = {p: digest((materialized / p).read_bytes()) for p in CODE_PATHS + POLICY_PATHS}
    wrapper_hash = digest(Path(__file__).read_bytes())
    provenance = {"source_commit": PIN, "tool_and_policy_sha256": tool_hashes,
                  "wrapper_sha256": wrapper_hash,
                  "source_policy": "Only Git blobs at the literal source commit; no worktree records or untracked inputs."}
    print(json.dumps({"stage": "materialized", "files": len(manifest),
                      "bytes": sum(r["size_bytes"] for r in manifest), **provenance}), flush=True)

    spec = importlib.util.spec_from_file_location("pinned_pending_coverage", materialized / CODE_PATHS[0])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    pending = module.build_inventory(REPO, PIN)
    assert pending["source_commit"] == PIN and pending["generator"]["sha256"] == tool_hashes[CODE_PATHS[0]]
    reports = [output("pending-coverage.json.gz", pending, True)]
    print(json.dumps({"stage": "pending_complete", "summary": pending["summary"]}), flush=True)

    raw_output = materialized / "broader-output.json"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               GIT_CEILING_DIRECTORIES=str(OUT))
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    result = subprocess.run([sys.executable, str(materialized / CODE_PATHS[1]),
                             "--repo", str(materialized), "--output", str(raw_output)],
                            cwd=materialized, env=env, capture_output=True, text=True)
    if result.returncode not in (0, 1) or not raw_output.exists():
        raise RuntimeError(f"Broader tool failed: {result.returncode}: {result.stderr}")
    broader = json.loads(raw_output.read_text())
    assert broader["source_commit"] is None, "Copied tree must not inherit live HEAD provenance"
    reports.append(output("broader-lineage.json.gz", {
        "schema": "crypto.autoresearch.committed_tool_output_capsule.v1", **provenance,
        "tool_report_preserved": broader,
        "git_metadata_note": "Tool reports null source_commit because the temporary committed input copy has no Git metadata; this capsule binds its independently hashed materialization.",
        "tool_exit_code": result.returncode, "tool_stdout": result.stdout,
        "tool_stderr": result.stderr}, True))
    checked = []
    for row in manifest:
        if digest((materialized / row["path"]).read_bytes()) != row["sha256"]:
            checked.append(row["path"])
    if checked:
        raise RuntimeError(f"Materialized input changed during traversal: {checked}")
    reports.append(output("materialized-inputs.json.gz", {
        "schema": "crypto.autoresearch.committed_input_manifest.v1", **provenance,
        "selection": "Existing broader scanner globs and dependency files, with all declared schema-supersession endpoints included; coordination YAML and legacy idea files conservatively copied.",
        "all_input_hashes_rechecked_after_scan": True, "files": manifest}, True))
    after = {ref: git("rev-parse", ref).decode().strip() for ref in ("HEAD", "origin/main")}
    live_changes = git("diff", "--name-only", PIN, after["HEAD"]).decode().splitlines()
    shutil.rmtree(materialized)
    receipt = {"schema": "crypto.autoresearch.pending_inventory_scan_receipt.v1", **provenance,
               "started_at": started, "finished_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "refs_before": before, "refs_after": after, "live_paths_changed_from_pin": live_changes,
               "source_drift_policy": "Pinned Git objects are immutable; all copied inputs rehashed after traversal. Live ref movement is disclosed and does not alter the pin.",
               "copied_source_bytes": sum(r["size_bytes"] for r in manifest),
               "copied_source_files": len(manifest), "temporary_copy_removed": not materialized.exists(),
               "primary_summary": pending["summary"], "broader_counts": broader["counts"],
               "broader_errors": len(broader["errors"]),
               "broader_duplicate_records": len(broader["duplicate_records"]),
               "broader_unknown_source_ids": len(broader["unknown_source_ids"]),
               "broader_tool_exit_code": result.returncode, "scientific_runs": 0,
               "completion_verified": False, "readiness_verified": False, "reports": reports}
    output("scan-receipt.json", receipt)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
