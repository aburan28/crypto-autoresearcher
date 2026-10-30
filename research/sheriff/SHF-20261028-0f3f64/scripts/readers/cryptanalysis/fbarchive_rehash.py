#!/usr/bin/env python3
"""Independent re-hash of cryptanalysis:experiments/fb-archive/index.csv against the archive files.

Does not import or run fbarchive.py (or any code from the clone). For every index row it checks:
  storage=git        file bytes and sha256 against `bytes` / `file_sha256`, and the sha256 of the
                     decompressed payload (gzip or xz, by suffix) against `content_sha256`;
                     if the file is an artifact-store pointer (`.artifacts.json` in its directory),
                     the pointer's sha256/bytes against the index, then (for files up to
                     --recover-max-bytes) the bytes recovered from git history before the S3 move
                     (cryptanalysis 5569ba6e^), hash-checked against the pointer;
  storage=git-chunks the `.chunks.json` manifest's bytes/sha256 against the index and each part's
                     pointer against the manifest (parts are off disk: not_covered).
It also lists files under bases/ that no index row or chunk manifest accounts for (the X2 question),
takes the gzip OS-byte census over indexed `.json.gz` archives it has bytes for (the K-N3 claim),
and re-compresses the three formerly unindexed archives with gzip level 9, mtime 0.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import lzma
import subprocess
from pathlib import Path

PRE_S3 = "5569ba6e^"
X2_FILES = ["bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l12-s1-52255f249712.json.gz",
            "bases/EC1N23Ckb1h32a1300cea95/geomtraceu-l13-s1-3765b6511827.json.gz",
            "bases/EC1N41Ckb1h9d49bc0affd2/geomtraceu-l15-s1-9207924c70d0.json.gz"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--recover-max-bytes", type=int, default=1_100_000)
    args = ap.parse_args()
    root = args.clone / "experiments/fb-archive"
    rows = list(csv.DictReader((root / "index.csv").open()))
    pointers = {}
    for f in root.glob("bases/*/.artifacts.json"):
        for name, meta in json.loads(f.read_text())["files"].items():
            pointers[str(f.parent.relative_to(root) / name)] = meta
    stats = collections.Counter()
    problems, not_covered, recovered = [], [], []
    have_bytes = {}
    accounted = set()

    def get_bytes(rel, expect_sha=None, expect_bytes=None):
        p = root / rel
        if p.exists():
            return p.read_bytes(), "disk"
        meta = pointers.get(rel)
        if meta is None:
            return None, "absent"
        if expect_sha is not None and (meta["sha256"] != expect_sha or meta["bytes"] != expect_bytes):
            problems.append("%s: pointer %s/%s != index %s/%s" % (rel, meta["sha256"], meta["bytes"], expect_sha, expect_bytes))
        if meta["bytes"] > args.recover_max_bytes:
            return None, "pointer_only"
        b = subprocess.run(["git", "-C", str(args.clone), "show", "%s:experiments/fb-archive/%s" % (PRE_S3, rel)],
                           capture_output=True).stdout
        if sha(b) != meta["sha256"] or len(b) != meta["bytes"]:
            problems.append("%s: bytes recovered from %s do not match the pointer" % (rel, PRE_S3))
            return None, "recovery_failed"
        recovered.append(rel)
        return b, "git_history"

    for r in rows:
        rel, storage = r["path"], r["storage"]
        accounted.add(rel)
        want_sha, want_bytes = r["file_sha256"], int(r["bytes"])
        if storage == "git":
            b, src = get_bytes(rel, want_sha, want_bytes)
            stats["git_rows"] += 1
            if b is None:
                stats["git_rows_bytes_not_on_disk_" + src] += 1
                not_covered.append(rel)
                continue
            stats["git_rows_bytes_from_" + src] += 1
            if sha(b) != want_sha or len(b) != want_bytes:
                problems.append("%s: file sha/bytes mismatch" % rel)
                continue
            if rel.endswith(".gz"):
                payload = gzip.decompress(b)
            elif rel.endswith(".xz"):
                payload = lzma.decompress(b)
            else:
                payload = b
            if sha(payload) != r["content_sha256"]:
                problems.append("%s: content_sha256 mismatch" % rel)
                continue
            stats["git_rows_file_and_content_verified"] += 1
            have_bytes[rel] = b
        elif storage == "git-chunks":
            stats["chunk_rows"] += 1
            man = json.loads((root / rel).read_text())
            if man["bytes"] != want_bytes or man["sha256"] != want_sha or sum(p["bytes"] for p in man["parts"]) != want_bytes:
                problems.append("%s: manifest bytes/sha differ from index" % rel)
            for part in man["parts"]:
                prel = str(Path(rel).parent / part["name"])
                accounted.add(prel)
                meta = pointers.get(prel)
                if (root / prel).exists():
                    if sha((root / prel).read_bytes()) != part["sha256"]:
                        problems.append("%s: part sha mismatch" % prel)
                elif meta is None:
                    problems.append("%s: part absent and no pointer" % prel)
                elif meta["sha256"] != part["sha256"] or meta["bytes"] != part["bytes"]:
                    problems.append("%s: pointer differs from manifest" % prel)
                else:
                    stats["chunk_parts_pointer_consistent_bytes_off_disk"] += 1
                    not_covered.append(prel)
        else:
            stats["rows_storage_" + storage] += 1
            not_covered.append(rel)

    # Unindexed files (X2): everything under bases/ on disk or behind a pointer
    present = set()
    for p in (root / "bases").rglob("*"):
        if p.is_file() and p.name not in (".artifacts.json", ".gitignore"):
            present.add(str(p.relative_to(root)))
    present |= set(pointers)
    unindexed = sorted(present - accounted)
    missing = sorted(r["path"] for r in rows if r["storage"] == "git" and r["path"] not in present)

    # OS byte census over indexed .json.gz with bytes available
    os_bytes = collections.Counter(b[9] for rel, b in have_bytes.items() if rel.endswith(".json.gz"))

    # X2 three files: indexed? recompress
    x2 = {}
    for rel in X2_FILES:
        b = have_bytes.get(rel)
        entry = {"indexed": rel in accounted, "bytes_available": b is not None}
        if b is not None:
            payload = gzip.decompress(b)
            re = gzip.compress(payload, compresslevel=9, mtime=0)
            diff = [i for i in range(min(len(re), len(b))) if re[i] != b[i]]
            entry.update(os_byte=b[9], recompressed_os_byte=re[9], same_length=len(re) == len(b),
                         differing_byte_offsets=diff[:10], n_differing=len(diff))
            xz_rel = rel[:-3] + ".xz"
            xb = have_bytes.get(xz_rel)
            if xb is not None:
                entry["content_equals_indexed_xz"] = lzma.decompress(xb) == payload
        x2[rel] = entry

    gz_rows = sum(1 for r in rows if r["path"].endswith(".json.gz"))
    result = {"index_rows": len(rows), "stats": dict(stats), "problems": problems,
              "unindexed_files": unindexed, "indexed_git_rows_missing_from_tree": missing,
              "not_covered_count": len(not_covered), "not_covered": not_covered,
              "recovered_from_git_history": recovered,
              "gzip_os_byte_census": {"indexed_json_gz_rows": gz_rows, "with_bytes": sum(os_bytes.values()),
                                      "by_os_byte": {str(k): v for k, v in sorted(os_bytes.items())}},
              "x2_files": x2}
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("not_covered", "recovered_from_git_history")}, indent=1))


if __name__ == "__main__":
    main()
