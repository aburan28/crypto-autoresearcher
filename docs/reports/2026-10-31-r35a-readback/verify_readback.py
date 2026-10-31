#!/usr/bin/env python3
"""Verify the published R35a bytes against the tracked publication record.

Usage: python3 verify_readback.py RELEASE_DIR > readback.json
The directory must contain the four R35a.* assets from the named GitHub release.
This checks custody and packaging, not the certificate's algebraic predicates.
"""

import gzip
import hashlib
import json
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "analysis/semaev-m2-last-fall-degree/submission-20261029/archive"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def digest(stream):
    sha = hashlib.sha256()
    size = 0
    while True:
        block = stream.read(1024 * 1024)
        if not block:
            break
        sha.update(block)
        size += len(block)
    return size, sha.hexdigest()


def main(release_dir):
    release_dir = Path(release_dir)
    publication_file = ARCHIVE / "R35a.publication.json"
    receipt_file = ARCHIVE / "R35a.receipt.json"
    for source in (publication_file, receipt_file):
        remote = release_dir / source.name
        require(remote.read_bytes() == source.read_bytes(), source.name)

    publication = json.loads(publication_file.read_text())
    receipt = json.loads(receipt_file.read_text())
    require(publication["schema"] == "semaev.publication-readback/v1", "publication schema")
    require(receipt["schema"] == "semaev.published-certificate/v1", "receipt schema")
    require(publication["id"] == receipt["result"]["id"] == "R35a", "record identity")

    assets = {}
    for item in publication["files"]:
        path = release_dir / item["name"]
        with path.open("rb") as stream:
            size, sha = digest(stream)
        require((size, sha) == (item["bytes"], item["sha256"]), item["name"])
        assets[item["name"]] = {"bytes": size, "sha256": sha}

    expected = receipt["result"]["artifacts"]
    with gzip.open(release_dir / "R35a.D4.cert.gz", "rb") as stream:
        cert_size, cert_sha = digest(stream)
    require((cert_size, cert_sha) == (
        expected["certificate.bin"]["bytes"],
        expected["certificate.bin"]["sha256"],
    ), "decompressed certificate")

    seen = set()
    extra = []
    with tarfile.open(release_dir / "R35a.evidence.tar.gz", "r:gz") as archive:
        for member in archive:
            require(member.isfile() and member.name.startswith("attempt/"), "tar member type/path")
            name = member.name.removeprefix("attempt/")
            require("/" not in name and name not in seen, "tar member path/duplicate")
            if name not in expected:
                extra.append(name)
                continue
            with archive.extractfile(member) as stream:
                size, sha = digest(stream)
            require((size, sha) == (expected[name]["bytes"], expected[name]["sha256"]), name)
            seen.add(name)
    require(seen == set(expected) - {"certificate.bin"}, "missing receipted members")
    require(extra == ["result.json"], "unexpected unreceipted members: " + repr(extra))

    return {
        "schema": "r35a.publication-readback-audit/v1",
        "release": "semaev-closure-certificates-20261029",
        "assets": assets,
        "receipt_byte_identical": True,
        "publication_byte_identical": True,
        "certificate_uncompressed": {"bytes": cert_size, "sha256": cert_sha},
        "receipted_evidence_members_verified": sorted(seen),
        "unreceipted_evidence_members": extra,
        "certificate_predicates_replayed": False,
        "result": "custody_bytes_verified",
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(json.dumps(main(sys.argv[1]), indent=2, sort_keys=True))
