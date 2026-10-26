"""Check delivery custody and scope; this does not certify execution or science."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def check_blob(data, record):
    if len(data) != record["bytes"] or digest(data) != record["sha256"]:
        raise ValueError("Payload bytes do not match manifest: "+record["path"])


def verify():
    audit = json.loads((ROOT/"archive/payload-audit.json").read_text())
    rows = []
    for manifest in audit["manifest_sha256"]:
        path = REPO/manifest["path"]
        assert digest(path.read_bytes()) == manifest["sha256"]
        rows.extend(json.loads(path.read_text()))
    assert len(rows) == audit["files"] == 716
    assert sum(r["bytes"] for r in rows) == audit["bytes"]
    amendments_path = ROOT/"archive/metadata-amendments.json"
    amendments = {r["path"]: r for r in json.loads(amendments_path.read_text())} if amendments_path.exists() else {}
    metadata_changes = 0
    parsed_json = parsed_svg = 0
    for row in rows:
        path = REPO/row["path"]
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert not path.is_symlink()
        data = path.read_bytes()
        if digest(data) == row["sha256"]:
            check_blob(data, row)
        else:
            # Only communication/publication metadata may be amended here.
            # Scientific source and outcome changes require a new snapshot.
            assert path in {ROOT/".gitignore", ROOT/"publication-scope.json"}
            amendment = amendments[row["path"]]
            assert amendment["old_sha256"] == row["sha256"]
            check_blob(amendment["original_content"].encode(), row)
            assert digest(data) == amendment["new_sha256"]
            assert len(data) == amendment["new_bytes"]
            metadata_changes += 1
        if path.suffix == ".json":
            json.loads(data)
            parsed_json += 1
        elif path.suffix == ".svg":
            ET.fromstring(data)
            parsed_svg += 1
    # Fail closed on corruption, without changing the actual evidence bytes.
    sample = next(r for r in rows if r["bytes"])
    altered = (REPO/sample["path"]).read_bytes()+b"x"
    try:
        check_blob(altered, sample)
    except ValueError:
        pass
    else:
        raise AssertionError("Corrupted content accepted")
    continuation = json.loads((ROOT/"tracks/f1/cubic-divisor/result.json").read_text())
    assert continuation["checks"]["fresh_watchdog_outcomes"] == len(continuation["watchdogs"]) == 3
    assert all("unknown" in w["status"] for w in continuation["watchdogs"])
    pdfs = json.loads((ROOT/"pdf-delivery-manifest.json").read_text())
    for item in pdfs:
        data = (ROOT/item["pdf"]).read_bytes()
        assert len(data) <= 65536 and len(data) == item["bytes"]
        assert digest(data) == item["sha256"]
    return {
        "status": "PASS", "scope": "custody, parsing, explicit unknowns and delivery bytes only",
        "payload_files": len(rows), "payload_bytes": audit["bytes"],
        "json_files_parsed": parsed_json, "svg_files_parsed": parsed_svg,
        "declared_metadata_amendments": metadata_changes,
        "corruption_control": "rejected", "retained_watchdog_unknowns_checked": 3,
        "compact_track_pdfs": len(pdfs),
        "not_established": ["prescribed execution", "independent scientific review", "mathematical claim promotion", "performance advantage"],
    }


if __name__ == "__main__":
    result = verify()
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            raise SystemExit("Refusing to overwrite earlier delivery verification")
        path.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
