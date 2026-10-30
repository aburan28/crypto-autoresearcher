#!/usr/bin/env python3
"""E1 / E1-R / E2 (SHF-20261016-3caa6f, SHF-20261017-e4d7f6): status fields of
every committed ecbench.session/v1 session in crypto at a pinned commit.

Reads blobs with `git cat-file --batch` only; executes nothing from the
crypto clone. Usage:
  python3 -I e1_session_status.py /home/user/crypto 669809d5c6110796b36b32fe26073376a605911d
"""
import collections
import json
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]


def git(*args, inp=None):
    return subprocess.run(["git", "-C", repo, *args], input=inp,
                          capture_output=True, check=True).stdout


tree = git("ls-tree", "-r", rev).decode().splitlines()
paths = []
for line in tree:
    meta, path = line.split("\t", 1)
    if path == "session.json" or path.endswith("/session.json"):
        paths.append((meta.split()[2], path))

files_by_dir = collections.defaultdict(set)
for line in tree:
    path = line.split("\t", 1)[1]
    d, _, name = path.rpartition("/")
    files_by_dir[d].add(name)

blob = git("cat-file", "--batch", inp="".join(f"{oid}\n" for oid, _ in paths).encode())
pos = 0
docs = {}
for oid, path in paths:
    hdr_end = blob.index(b"\n", pos)
    hdr = blob[pos:hdr_end].split()
    size = int(hdr[2])
    body = blob[hdr_end + 1:hdr_end + 1 + size]
    pos = hdr_end + 1 + size + 1
    try:
        docs[path] = json.loads(body)
    except Exception as exc:  # noqa: BLE001
        docs[path] = {"_parse_error": str(exc)}

schemas = collections.Counter()
eb = []
for path, d in docs.items():
    s = d.get("schema") if isinstance(d, dict) else None
    schemas[s] += 1
    if s == "ecbench.session/v1":
        eb.append(path)

print(f"commit {rev}")
print(f"session.json files in tree: {len(paths)}")
print("schemas:")
for s, c in schemas.most_common():
    print(f"  {c:5d}  {s}")
print(f"ecbench.session/v1 sessions: {len(eb)}")

status = collections.Counter()
rows = []
for path in sorted(eb):
    d = docs[path]
    st = d.get("status")
    status[st] += 1
    rows.append((path, st, sorted(k for k in d.keys())))
print("status of ecbench.session/v1 sessions:")
for s, c in status.most_common():
    print(f"  {c:5d}  {s!r}")

glob_dirs = ("research/ecbench_",)
fixed = ("research/ghs_curve_comparison_20261009/sessions/",
         "research/notes/ecc2k130/cold_compact_orbit_ic_20261003/sessions/",
         "research/notes/ecc2k130/full_rank_compact_orbit_ic_20261003/sessions/")
outside_old = [p for p in eb
               if not (p.startswith(glob_dirs) and "/sessions/" in p)
               and not p.startswith(fixed)]
outside_research = [p for p in eb if not p.startswith("research/")]
print(f"ecbench sessions outside the four directory globs of the exhaustive lane: {len(outside_old)}")
print(f"ecbench sessions outside research/ (ci-scope trigger covers research/ only): {len(outside_research)}")
for p in outside_research:
    print(f"    {p}")

print("non-terminal ecbench sessions (status not complete):")
for path, st, keys in rows:
    if st != "complete":
        d = path.rpartition("/")[0]
        has_final = {k: (k in keys) for k in ("finished_at", "records_sha256", "interruption", "final_seal", "seal")}
        print(f"  {st!r:14} {d}  files={sorted(files_by_dir[d])}")
        print(f"      keys={keys}")
