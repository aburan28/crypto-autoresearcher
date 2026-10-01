#!/usr/bin/env python3
"""CP-1 of TASK-20260926-f50294: VERIFY BEFORE COMPARING.

(1) both reviewer directories match the TASK-20260926-e8779d receipt's
    path_sha256 (every file, both directions: no missing and no extra file);
(2) each seal.txt matches its sealed files;
(3) blind-inputs.json (and blind-inputs-key.json) match the
    TASK-20260926-5d1557 receipt;
(4) the e8779d receipt reports no blocking defect.
Also: the worktree HEAD is the e8779d archive commit and the bytes on disk equal
the committed blobs (git hash-object vs ls-tree).

Run from the dedicated worktree root. Stdlib only. Writes JSON to stdout.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROUND = "coordination/review/certbin-20260926-d7249d"
E8 = f"{ROUND}/archives/TASK-20260926-e8779d/snapshot-receipt.json"
D5 = f"{ROUND}/archives/TASK-20260926-5d1557/snapshot-receipt.json"
DIRS = [f"{ROUND}/reviews/TASK-20260926-f0736e/", f"{ROUND}/reviews/TASK-20260926-401771/"]
E8_COMMIT = "f88fc611965247a1561e9254cd80c729c0e5f077"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    out = {"checks": {}, "all_pass": True}
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out["worktree_head"] = head
    out["checks"]["head_is_e8779d_commit"] = head == E8_COMMIT
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True)
    out["worktree_clean"] = status.strip() == ""

    e8 = json.load(open(E8))
    ps = e8["path_sha256"]
    # (1) reviewer directories vs receipt
    r1 = {}
    for d in DIRS:
        on_disk = set()
        for root, _, files in os.walk(d):
            for f in files:
                on_disk.add(os.path.join(root, f))
        in_receipt = {p for p in ps if p.startswith(d)}
        mism = [p for p in sorted(in_receipt & on_disk) if sha(p) != ps[p]]
        r1[d] = {
            "files_in_receipt": len(in_receipt),
            "files_on_disk": len(on_disk),
            "missing_on_disk": sorted(in_receipt - on_disk),
            "extra_on_disk": sorted(on_disk - in_receipt),
            "sha256_mismatch": mism,
            "pass": not mism and in_receipt == on_disk,
        }
    out["checks"]["(1)_dirs_match_e8779d_path_sha256"] = r1
    # committed blobs equal bytes on disk (content-first binding)
    tree = subprocess.check_output(["git", "ls-tree", "-r", E8_COMMIT, "--", *DIRS], text=True)
    blob_bad = []
    for line in tree.splitlines():
        meta, path = line.split("\t", 1)
        blob = meta.split()[2]
        ho = subprocess.check_output(["git", "hash-object", path], text=True).strip()
        if ho != blob:
            blob_bad.append(path)
    out["checks"]["(1b)_disk_equals_committed_blobs"] = {"mismatch": blob_bad, "pass": not blob_bad}

    # (2) seals
    r2 = {}
    for d in DIRS:
        txt = open(d + "seal.txt").read()
        rows = re.findall(r"^\s*([0-9a-f]{64})\s+(\S+)\s*$", txt, re.M)
        bad = [(f, h, sha(d + f)) for h, f in rows if sha(d + f) != h]
        r2[d] = {"sealed_files": len(rows), "mismatch": bad, "pass": bool(rows) and not bad}
    out["checks"]["(2)_seal_txt_matches"] = r2

    # (3) blind inputs vs 5d1557 receipt
    d5 = json.load(open(D5))
    r3 = {}
    for p in (f"{ROUND}/blind/blind-inputs.json", f"{ROUND}/blind-inputs-key.json"):
        r3[p] = {"receipt": d5["path_sha256"].get(p), "disk": sha(p)}
        r3[p]["pass"] = r3[p]["receipt"] == r3[p]["disk"]
    out["checks"]["(3)_blind_inputs_match_5d1557"] = r3

    # (4) no blocking defect
    sc1 = e8["SC-1"]
    defects = sc1.get("defects", [])
    blocking = [x for x in defects if "non-blocking" not in x]
    out["checks"]["(4)_no_blocking_defect"] = {
        "defects": defects,
        "blocking_defects": blocking,
        "comparator_blocked_flag": sc1.get("comparator_TASK-20260926-f50294_blocked"),
        "pass": not blocking and sc1.get("comparator_TASK-20260926-f50294_blocked") is False,
    }
    flat = [out["checks"]["head_is_e8779d_commit"],
            all(v["pass"] for v in r1.values()),
            out["checks"]["(1b)_disk_equals_committed_blobs"]["pass"],
            all(v["pass"] for v in r2.values()),
            all(v["pass"] for v in r3.values()),
            out["checks"]["(4)_no_blocking_defect"]["pass"]]
    out["all_pass"] = all(flat)
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
