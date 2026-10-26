"""Verify prepared-byte custody and protocol metadata, never run mathematics."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    snapshot = json.loads((ROOT / "archive/source-snapshot.json").read_text())
    rows = []
    for part in snapshot["parts"]:
        data = (REPO / part["path"]).read_bytes()
        assert sha(data) == part["sha256"]
        rows.extend(json.loads(data))
    assert len(rows) == snapshot["records"]
    scope = json.loads((ROOT / "archive/source-inventory-scope.json").read_text())
    excluded = {r["path"]: r for r in scope["not_distributed_primary_sources"]}
    assert set(excluded) == {
        str(ROOT.relative_to(REPO) / "tracks/f3/local-sources/sec2-v2.pdf"),
        str(ROOT.relative_to(REPO) / "tracks/f3/local-sources/sec2-v2.txt")}
    amendment = json.loads((ROOT / "archive/status-freeze-addendum.json").read_text())
    changed = []
    for row in rows:
        path = REPO / row["path"]
        assert path.resolve().is_relative_to(ROOT.resolve())
        if row["path"] in excluded:
            assert row == excluded[row["path"]]
            continue  # Optional public literature cache, absent from Git/delivery.
        data = path.read_bytes()
        if sha(data) != row["sha256"]:
            assert row["path"] == amendment["path"]
            assert row["sha256"] == amendment["old_sha256"]
            assert sha(data) == amendment["new_sha256"]
            original = subprocess.check_output([
                "git", "show", amendment["source_snapshot_commit"] + ":" + row["path"]], cwd=REPO)
            assert sha(original) == row["sha256"]
            changed.append(row["path"])
        else:
            assert len(data) == row["bytes"]
    for row in json.loads((ROOT / "tracks/f1/partial-source-manifest.json").read_text())["files"]:
        assert sha((ROOT / row["path"]).read_bytes()) == row["sha256"]
    protocols = []
    for track in range(2, 9):
        directory = ROOT / "tracks" / f"f{track}"
        protocol = json.loads((directory / "protocol.json").read_text())
        freeze = protocol["freeze"]
        assert freeze["status"] == "frozen" and freeze["filed_before_affected_data"] is True
        body = {k: v for k, v in protocol.items() if k != "freeze"}
        raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                         allow_nan=False).encode()
        assert sha(raw) == freeze["protocol_sha256"]
        script = protocol["analysis_plan"]["script"]
        assert sha((directory / script["path"]).read_bytes()) == script["sha256"]
        protocols.append(freeze["protocol_sha256"])
        assert not (directory / "runs").exists()
    for source in ROOT.rglob("*.py"):
        ast.parse(source.read_text(), filename=str(source))
    assert not list(ROOT.rglob("phase-b-release.json"))
    assert not (ROOT / "runtime/releases").exists()
    pdfs = json.loads((ROOT / "archive/preparation-pdf-inspection.json").read_text())["reports"]
    for record in pdfs:
        data = (ROOT / record["pdf"]).read_bytes()
        assert len(data) == record["bytes"] <= 65536 and sha(data) == record["sha256"]
    return {"status": "PASS", "scope": "byte custody, static parsing and frozen metadata only",
            "workspace_inventory_rows": len(rows), "optional_unpublished_literature_caches": len(excluded),
            "declared_communication_changes": changed, "frozen_protocols": len(protocols),
            "inspected_track_pdfs": len(pdfs), "run_or_release_records_supplied": False,
            "not_established": ["arithmetic execution", "source algorithm correctness",
                                "scientific review", "performance or ECDLP advantage"]}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
