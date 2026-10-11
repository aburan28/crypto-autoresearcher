"""J-VAL (2): recompute every checksums.sha256 of the EXP-PFDR-0b3699 run set.

TASK-20261009-33b5cf, independent re-implementation (standard library only; no
producer code imported). For every checksums.sha256 under the six run roots:
every listed file is re-hashed and compared; every file beneath the location
that the list does not name (other than the list itself) is reported as
uncovered; every listed path that does not exist is reported as missing.
No seeds (deterministic).
Usage: python check_checksums.py <runs-dir> <out.json>
"""
import hashlib
import json
import os
import sys


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    runs, out = sys.argv[1], sys.argv[2]
    report = {"lists": []}
    for root, _, files in sorted(os.walk(runs)):
        if "checksums.sha256" not in files:
            continue
        lst = os.path.join(root, "checksums.sha256")
        listed = {}
        dup = []
        for line in open(lst):
            line = line.rstrip("\n")
            if not line:
                continue
            h, rel = line[:64], line[66:]
            if line[64:66] != "  ":
                rel = line[65:]
            if rel in listed:
                dup.append(rel)
            listed[rel] = h
        mism, missing = [], []
        for rel, h in listed.items():
            p = os.path.join(root, rel)
            if not os.path.exists(p):
                missing.append(rel)
            elif sha256(p) != h:
                mism.append(rel)
        present = set()
        for r2, _, fs in os.walk(root):
            for f in fs:
                rel = os.path.relpath(os.path.join(r2, f), root)
                if rel != "checksums.sha256":
                    present.add(rel)
        uncovered = sorted(present - set(listed))
        report["lists"].append({
            "list": os.path.relpath(lst, runs), "entries": len(listed),
            "mismatches": mism, "missing": missing, "duplicates": dup,
            "uncovered_files": uncovered})
    report["total_entries"] = sum(x["entries"] for x in report["lists"])
    report["total_mismatches"] = sum(len(x["mismatches"]) for x in report["lists"])
    report["total_missing"] = sum(len(x["missing"]) for x in report["lists"])
    report["total_uncovered"] = sum(len(x["uncovered_files"]) for x in report["lists"])
    json.dump(report, open(out, "w"), indent=1)
    for x in report["lists"]:
        print(x["list"], x["entries"], "mism", len(x["mismatches"]), "missing", len(x["missing"]),
              "uncovered", x["uncovered_files"][:6], "dup", len(x["duplicates"]))
    print("TOTAL entries", report["total_entries"], "mismatches", report["total_mismatches"],
          "missing", report["total_missing"], "uncovered", report["total_uncovered"])


if __name__ == "__main__":
    main()
