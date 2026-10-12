"""Retain the complete binary dataset without adding gigabytes of Git objects."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
TASK = REPO / "tasks/solinas_point_distribution"
OUTPUT = Path("/workspace/solinas-point-distribution-20261012.zip")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    if OUTPUT.exists():
        raise SystemExit("bundle exists; immutable archive cannot be overwritten")
    files = [p for root in (TASK, HERE) for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
             and p.name not in ("dataset-bundle.json", "dataset-inventory.json", "progress.json", "progress.tmp")]
    inventory = {str(p.relative_to(REPO)): {"bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(files)}
    manifest = HERE / "dataset-inventory.json"
    manifest.write_text(json.dumps({"schema": 1, "files": inventory}, sort_keys=True, indent=2) + "\n")
    with zipfile.ZipFile(OUTPUT, "x", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for path in sorted(files) + [manifest]:
            archive.write(path, path.relative_to(REPO))
    with zipfile.ZipFile(OUTPUT) as archive:
        failed = archive.testzip()
        if failed:
            raise RuntimeError("bundle CRC failure: " + failed)
        entries = len(archive.infolist())
    summary = {"schema": 1, "path": str(OUTPUT), "bytes": OUTPUT.stat().st_size, "sha256": sha(OUTPUT),
               "entries": entries, "crc_verification": "passed", "payload_sha256_verification": "all input files hashed into dataset-inventory.json",
               "raw_arrays_git_policy": "NPZ arrays are retained in this complete archive and the execution workspace; every field JSON is retained in lossless Git-tracked shards, with original raw checksums."}
    (HERE / "dataset-bundle.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
