#!/usr/bin/env python3
"""PROBE G (red team, TASK-20260809-444fe7): independent verification of the
COORDINATOR CLAIMS ABOUT THE GIT RECORD for BATCH-9e3584.

Not pre-registered. Re-executable from the repository root:
    python3 <this file>

Checks, all against the live git object database (never against the working
tree alone):
  G1  the three-way commit split 1aa7db53 / c034ef38 / 502d15a0 and their
      declared file counts and parent chain;
  G2  the "30 of 30 declared artifacts match their recorded sha256 at HEAD"
      claim, recomputed from `git show HEAD:<path>`;
  G2b the same hashes recomputed at the DECLARED commit rather than HEAD;
  G3  the D3 table: every artifact_path declared in the ORIGINAL
      dispatch_queue.json for the four producer tasks, marked
      EXISTS / DANGLING at HEAD, plus committed-but-undeclared files.
"""
import hashlib, json, subprocess, sys, os

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True, check=True).stdout.strip()
os.chdir(ROOT)
B = "coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584"

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout

def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return None if r.returncode else r.stdout

out = {"probe": "PROBE-G", "task": "TASK-20260809-444fe7", "checks": {}}

# ---------- G1: commit split ----------
split = {}
for short in ["1aa7db53", "c034ef38", "502d15a0"]:
    full = git("rev-parse", short).strip()
    parents = git("log", "-1", "--format=%P", full).strip().split()
    names = [l.split("\t") for l in
             git("diff-tree", "--no-commit-id", "--name-status", "-r", full).strip().splitlines()]
    anc = subprocess.run(["git", "merge-base", "--is-ancestor", full, "HEAD"]).returncode == 0
    split[short] = {
        "full_sha": full,
        "parents": parents,
        "subject": git("log", "-1", "--format=%s", full).strip(),
        "n_paths": len(names),
        "status_counts": {s: sum(1 for x, _ in names if x == s) for s in sorted({x for x, _ in names})},
        "paths": [p for _, p in names],
        "ancestor_of_HEAD": anc,
        "message_contains_goal": "GOAL-MLKEM-005" in git("log", "-1", "--format=%B", full),
    }
out["checks"]["G1_commit_split"] = split
out["checks"]["G1_verdict"] = {
    "1aa7db53_is_2_prereg_files": (split["1aa7db53"]["n_paths"] == 2 and
        all(p.endswith(("prereg.md", "prereg_sha256.txt")) for p in split["1aa7db53"]["paths"])),
    "c034ef38_is_28_producer_files": (split["c034ef38"]["n_paths"] == 28 and
        all("/tasks/TASK-20260809-" in p for p in split["c034ef38"]["paths"])),
    "502d15a0_is_2_receipts_plus_queue": (split["502d15a0"]["n_paths"] == 3 and
        sum(1 for p in split["502d15a0"]["paths"] if p.endswith("snapshot-receipt.json")) == 2 and
        sum(1 for p in split["502d15a0"]["paths"] if p.endswith("dispatch_queue.json")) == 1),
    "chain_is_linear_1aa->c034->502d": (
        split["c034ef38"]["parents"] == [split["1aa7db53"]["full_sha"]] and
        split["502d15a0"]["parents"] == [split["c034ef38"]["full_sha"]]),
}

# ---------- G2: 30-for-30 content match ----------
recs = {}
for t in ["TASK-20260809-91cf76", "TASK-20260809-4d928d"]:
    recs[t] = json.loads(blob("502d15a0", f"{B}/archives/{t}/snapshot-receipt.json"))

rows = []
for t, r in recs.items():
    declared_commit = r["archive"]["commit_sha"]
    for path, want in r["archive"]["path_sha256"].items():
        b_head = blob("HEAD", path)
        b_decl = blob(declared_commit, path)
        rows.append({
            "receipt_task": t, "path": path, "declared_sha256": want,
            "at_HEAD": None if b_head is None else hashlib.sha256(b_head).hexdigest(),
            "at_declared_commit": None if b_decl is None else hashlib.sha256(b_decl).hexdigest(),
        })
for row in rows:
    row["match_at_HEAD"] = row["at_HEAD"] == row["declared_sha256"]
    row["match_at_declared_commit"] = row["at_declared_commit"] == row["declared_sha256"]
out["checks"]["G2_declared_artifact_hashes"] = rows
out["checks"]["G2_verdict"] = {
    "n_declared": len(rows),
    "n_match_at_HEAD": sum(r["match_at_HEAD"] for r in rows),
    "n_match_at_declared_commit": sum(r["match_at_declared_commit"] for r in rows),
    "mismatches": [r["path"] for r in rows if not r["match_at_HEAD"]],
}

# ---------- G3: D3 dangling artifact-path table ----------
q = json.loads(blob("502d15a0", f"{B}/dispatch_queue.json").decode())
producers = ["TASK-20260809-cda2f6", "TASK-20260809-311784",
             "TASK-20260809-97d6cf", "TASK-20260809-3eb72c"]
d3 = {}
committed = set(split["c034ef38"]["paths"])
declared_all = set()
for task in q["tasks"]:
    if task["id"] not in producers:
        continue
    dec = list(task.get("artifact_paths", []))
    declared_all |= set(dec)
    d3[task["id"]] = {
        "declared": [{"path": p, "exists_at_HEAD": blob("HEAD", p) is not None,
                      "in_c034ef38": p in committed} for p in dec],
        "n_declared": len(dec),
        "n_dangling_at_HEAD": sum(1 for p in dec if blob("HEAD", p) is None),
    }
undeclared = sorted(p for p in committed
                    if p.split("/")[-2] in producers and p not in declared_all)
out["checks"]["D3_per_task"] = d3
out["checks"]["D3_verdict"] = {
    "n_declared_total": len(declared_all),
    "n_dangling_total": sum(v["n_dangling_at_HEAD"] for v in d3.values()),
    "n_committed_producer_files": len([p for p in committed]),
    "n_committed_but_undeclared": len(undeclared),
    "undeclared_committed_files": undeclared,
    "dangling_names": sorted(p for p in declared_all if blob("HEAD", p) is None),
}
json.dump(out, sys.stdout, indent=1)
print()
