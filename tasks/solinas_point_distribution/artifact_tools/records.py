"""Losslessly store field JSON as four small Git-friendly shards; restore safely."""
import argparse
import gzip
import hashlib
import json
import re
from pathlib import Path


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pack(run):
    receipt = json.loads((run / "receipt.json").read_text())
    if receipt["status"] != "complete":
        raise ValueError("incomplete measurement")
    entries = receipt["fields"]
    directory = run / "record-shards"
    directory.mkdir(exist_ok=True)
    archives = []
    for case in sorted({r["case"] for r in entries}):
        path = directory / ("field-records-" + case + ".jsonl.gz")
        count = curves = 0
        with path.open("xb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as out:
                for entry in entries:
                    if entry["case"] != case:
                        continue
                    source = run / "fields" / (entry["field_id"] + ".json")
                    payload = source.read_bytes()
                    if hashlib.sha256(payload).hexdigest() != entry["json_sha256"]:
                        raise ValueError("field JSON checksum failed")
                    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
                        raise ValueError("unexpected JSONL encoding")
                    out.write(payload)
                    count += 1
                    curves += entry["curves"]
        archives.append({"case": case, "path": str(path.relative_to(run)), "bytes": path.stat().st_size,
                         "sha256": sha(path), "fields": count, "curves": curves})
    result = {"schema": 1, "status": "lossless_shards", "archives": archives,
              "encoding": "Each line is the exact original field JSON bytes including its newline; original SHA256s remain in receipt.json.",
              "binary_arrays": "Available in the complete dataset ZIP; NPZ checksums are in each field record and receipt."}
    with (run / "record-shards.json").open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    return result


def unpack(run):
    manifest = json.loads((run / "record-shards.json").read_text())
    receipt = json.loads((run / "receipt.json").read_text())
    expected = {r["field_id"]: r["json_sha256"] for r in receipt["fields"]}
    directory = run / "fields"
    directory.mkdir(exist_ok=True)
    seen = set()
    for archive in manifest["archives"]:
        source = run / archive["path"]
        if sha(source) != archive["sha256"]:
            raise ValueError("shard checksum failed")
        with gzip.open(source, "rb") as stream:
            for payload in stream:
                field = json.loads(payload)
                identifier = field["field_id"]
                if not re.fullmatch(r"[A-Za-z0-9-]+", identifier) or identifier in seen:
                    raise ValueError("invalid or duplicate field ID")
                seen.add(identifier)
                if hashlib.sha256(payload).hexdigest() != expected[identifier]:
                    raise ValueError("original JSON bytes not preserved")
                destination = directory / (identifier + ".json")
                if destination.exists():
                    if sha(destination) != expected[identifier]:
                        raise ValueError("existing record differs; refusing overwrite")
                else:
                    with destination.open("xb") as out:
                        out.write(payload)
    if seen != set(expected):
        raise ValueError("missing or unexpected records")
    return {"status": "exact_bytes_verified", "fields": len(seen)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["pack", "unpack"])
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(pack(args.run) if args.action == "pack" else unpack(args.run), indent=2))
