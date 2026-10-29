#!/usr/bin/env python3
"""E1-R (SHF-20261017-e4d7f6): for every committed ecbench.session/v1 whose
status is not `complete`, print the fields that would bind its records file
(records_sha256, records_written, finished_unix_ms, status_counts) and, for
uncompressed records.jsonl, compare records_sha256 with the blob's sha256 and
records_written with its line count. Also report when each such session was
added (first commit touching its session.json) so post-fix additions show.

Reads git objects only. Usage:
  python3 -I e1r_running_fields.py /home/user/crypto <rev>
"""
import hashlib
import json
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]


def git(*args, inp=None):
    return subprocess.run(["git", "-C", repo, "-c", "gc.auto=0", *args], input=inp,
                          capture_output=True, check=True).stdout


tree = {}
for line in git("ls-tree", "-r", rev).decode().splitlines():
    meta, path = line.split("\t", 1)
    tree[path] = meta.split()[2]


def cat(oid):
    return git("cat-file", "blob", oid)


rows = []
for path, oid in sorted(tree.items()):
    if not (path == "session.json" or path.endswith("/session.json")):
        continue
    try:
        d = json.loads(cat(oid))
    except Exception:  # noqa: BLE001
        continue
    if not isinstance(d, dict) or d.get("schema") != "ecbench.session/v1":
        continue
    if d.get("status") == "complete":
        continue
    rows.append((path, d))

print(f"commit {rev}")
print(f"non-complete ecbench.session/v1 sessions: {len(rows)}")
for path, d in rows:
    sdir = path.rpartition("/")[0]
    rec = tree.get(f"{sdir}/records.jsonl")
    line = {
        "status": d.get("status"),
        "records_sha256": d.get("records_sha256"),
        "records_written": d.get("records_written"),
        "executions_planned": d.get("executions_planned"),
        "finished_unix_ms": d.get("finished_unix_ms"),
        "status_counts": d.get("status_counts"),
    }
    if rec is not None:
        body = cat(rec)
        line["records_file_sha256"] = hashlib.sha256(body).hexdigest()
        line["records_file_lines"] = body.count(b"\n")
        line["records_sha256_matches_file"] = (d.get("records_sha256") == line["records_file_sha256"])
    else:
        line["records_file"] = "records.jsonl.gz (not hashed here)"
    first = git("log", "--diff-filter=A", "--format=%h %cI", rev, "--", path).decode().strip().splitlines()
    line["added"] = first[-1] if first else None
    print(f"- {sdir}")
    print("    " + json.dumps(line, sort_keys=True))
