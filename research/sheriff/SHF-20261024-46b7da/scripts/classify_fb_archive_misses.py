#!/usr/bin/env python3
"""Source-pin the unresolved cryptanalysis factor-base citation digests.

Usage: python3 classify_fb_archive_misses.py CRYPTANALYSIS_GIT_DIR
Reads fb-refs-recheck.json beside this script and writes a deterministic JSON
receipt. A matching cited hash is not an independent point-set reconstruction.
"""

import base64
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


HERE = Path(__file__).resolve().parent
SOURCE = json.loads((HERE / "fb-refs-recheck.json").read_text())
HEAD = SOURCE["source_head"]


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def pinned(repo, path):
    return subprocess.check_output(["git", "show", f"{HEAD}:{path}"],
                                   cwd=repo, stderr=subprocess.DEVNULL)


def occurrences(value, digest, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from occurrences(child, digest, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from occurrences(child, digest, path + (str(index),))
    elif value == digest:
        yield "/".join(path)


def containing_records(value, digest, path=()):
    if isinstance(value, dict):
        if digest in value.values():
            yield path, value
        for key, child in value.items():
            yield from containing_records(child, digest, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from containing_records(child, digest, path + (str(index),))


def checked_relative(parent, value):
    candidate = parent / value
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"nonlocal cited path: {value}")
    return str(candidate)


def main(repo):
    assert len(SOURCE["missing"]) == 32
    cache = {}

    def blob(path):
        if path not in cache:
            cache[path] = pinned(repo, path)
        return cache[path]

    rows = []
    direct = set()
    owners = Counter()
    for item in SOURCE["missing"]:
        digest = item["sha256"]
        citations = []
        owners["/".join(item["sample_citations"][0].split("/")[:2])] += 1
        for relative in item["sample_citations"]:
            packed = blob(relative)
            text = gzip.decompress(packed) if relative.endswith(".gz") else packed
            data = json.loads(text)
            pointers = list(occurrences(data, digest))
            assert pointers, (digest, relative)
            citations.append({"path": relative, "file_sha256": sha(packed),
                              "json_pointers": pointers})
            for pointer, record in containing_records(data, digest):
                for key, value in record.items():
                    if not isinstance(value, str):
                        continue
                    if key.endswith("_base64"):
                        candidate = base64.b64decode(value, validate=True)
                        source = f"{relative}:{'/'.join(pointer + (key,))}"
                    elif key.endswith("_file"):
                        source = checked_relative(PurePosixPath(relative).parent, value)
                        try:
                            candidate = blob(source)
                        except subprocess.CalledProcessError:
                            continue
                    else:
                        continue
                    if sha(candidate) == digest:
                        direct.add((digest, source, len(candidate)))
        assert any(p.endswith("enumerated_set_sha256")
                   for citation in citations for p in citation["json_pointers"]), digest
        rows.append({"digest": digest, "sample_citations": citations})

    sample_files = {citation["path"] for row in rows
                    for citation in row["sample_citations"]}
    assert len(sample_files) == 64 and len(direct) == 3, (len(sample_files), direct)
    receipt = {
        "schema": "fb-missing-digest-classification/v1",
        "source_head": HEAD,
        "recheck_receipt_sha256": sha((HERE / "fb-refs-recheck.json").read_bytes()),
        "missing_count": len(rows),
        "unique_sample_citation_files": len(sample_files),
        "unique_pinned_blobs_read": len(cache),
        "first_citation_owner_counts": dict(sorted(owners.items())),
        "all_are_enumerated_point_set_digest_references": True,
        "direct_blob_hash_matches": [
            {"digest": digest, "source": source, "bytes": size}
            for digest, source, size in sorted(direct)
        ],
        "archive_status": "not archived; no debt-list promotion or result validation",
        "limit": "Direct blob hashes and citation pointers do not independently reconstruct point sets.",
        "rows": rows,
    }
    out = HERE / "fb-missing-digest-classification.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"{len(rows)} missing digests; {len(direct)} direct blobs; {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: classify_fb_archive_misses.py CRYPTANALYSIS_GIT_DIR")
    main(Path(sys.argv[1]))
