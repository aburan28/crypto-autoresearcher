"""Artifact inventory of the TASK-20261029-11526b directory: repo-relative path, bytes and sha256 of every file
except report.yaml (which carries this inventory and cannot hash itself; its sha256 is returned in the hand-off).
Writes outputs/artifact-inventory.json and prints a YAML list for report.yaml."""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    rows = []
    for d, _, files in os.walk(ROOT):
        for f in sorted(files):
            p = os.path.join(d, f)
            rp = C.rel(p)
            if f == "report.yaml" and d == ROOT:
                continue
            if f == "artifact-inventory.json":
                continue
            b = open(p, "rb").read()
            rows.append({"path": rp, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    rows.sort(key=lambda r: r["path"])
    big = [r["path"] for r in rows if r["bytes"] > 64 * 1024 and r["path"].endswith((".json", ".jsonl", ".csv"))]
    with open(os.path.join(ROOT, "outputs", "artifact-inventory.json"), "w") as fh:
        json.dump({"files": rows, "data_files_over_64KiB": big}, fh, indent=1, sort_keys=True)
        fh.write("\n")
    for r in rows:
        print(f"  - {{path: {r['path']}, bytes: {r['bytes']}, sha256: {r['sha256']}}}")
    print("# data files over 64 KiB:", big)


if __name__ == "__main__":
    main()
