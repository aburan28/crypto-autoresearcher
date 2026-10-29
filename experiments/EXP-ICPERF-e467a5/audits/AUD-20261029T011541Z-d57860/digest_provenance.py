#!/usr/bin/env python3
"""Provenance of the S02-trials.attempt-1.supervisor.stderr digest mismatch.

Audit reader script (validator, claude-opus-5-5). Read-only on the repository:
it reads blobs with `git show`, and reproduces merge 0186e97db6 with
`git merge-tree` inside a throwaway `--shared` clone under <scratch_dir>, so
no object, ref or file is written to the audited repository.

Usage: python3 -I digest_provenance.py <repo_root> <scratch_dir>
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, scratch = Path(sys.argv[1]), Path(sys.argv[2])
S = "experiments/EXP-ICPERF-e467a5/runbook-sessions/RBS-ICPERF-b7e41c"
F = f"{S}/steps/S02-trials.attempt-1.supervisor.stderr"
EXEC_A = "93b87120f68801ce4a70e678067b33d661623117"  # 2026-10-19 execution
EXEC_B = "2d3948be7f787567cd27bc13f6e348eb8528b06b"  # 2026-10-21 execution (main via PR #2452)
MERGE = "0186e97db6997dc3e049ab23154d97c743fa5dc6"   # first commit holding the composite


def git(*args, cwd=repo):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True)


def blob(commit, path):
    r = git("show", f"{commit}:{path}")
    return r.stdout if r.returncode == 0 else None


def consistency(commit):
    journal = blob(commit, f"{S}/journal.jsonl").decode()
    entries = [json.loads(line) for line in journal.splitlines()]
    mismatches, n, recorded = [], 0, None
    for e in entries:
        for item in e.get("logs", []) + e.get("outputs", []):
            n += 1
            data = blob(commit, item["path"])
            if data is None or hashlib.sha256(data).hexdigest() != item["sha256"]:
                mismatches.append(item["path"].rsplit("/", 1)[-1])
            if item["path"] == F:
                recorded = item["sha256"]
    first = entries[0]
    seq5 = [e for e in entries if e["type"] == "step_finished" and e["step_id"] == "S02-trials"][0]
    content = blob(commit, F)
    return {
        "commit": commit,
        "session_started": first["time"], "owner": first["owner"],
        "preflight_commit": first["preflight"]["commit"],
        "preflight_tool_sha256": first["preflight"]["tool_sha256"],
        "journal_tip": entries[-1]["hash"],
        "s02_exit_code": seq5["exit_code"], "s02_detail": seq5["detail"],
        "stderr_recorded_sha256": recorded,
        "stderr_actual_sha256": hashlib.sha256(content).hexdigest(),
        "stderr_bytes": len(content),
        "digests_checked": n, "mismatches": mismatches,
    }


out = {"A": consistency(EXEC_A), "B": consistency(EXEC_B), "HEAD": consistency("HEAD")}

parents = git("show", "-s", "--format=%P", MERGE).stdout.decode().split()
clone = scratch / "merge-repro"
if not clone.exists():
    subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", str(repo), str(clone)], check=True)
mt = git("merge-tree", "--write-tree", "--messages", *parents, cwd=clone)
lines = mt.stdout.decode().splitlines()
tree = lines[0]
auto = {}
for name in ("supervisor.stderr", "supervisor.stdout"):
    p = f"{S}/steps/S02-trials.attempt-1.{name}"
    auto[name] = git("rev-parse", f"{tree}:{p}", cwd=clone).stdout.decode().strip()
out["merge_reproduction"] = {
    "merge": MERGE, "parents": parents,
    "merge_base": git("merge-base", *parents).stdout.decode().strip(),
    "session_messages": [l for l in lines if "RBS-ICPERF-b7e41c" in l and ("CONFLICT" in l or "Auto-merging" in l)],
    "auto_merged_blobs": auto,
    "stderr_blob_at_A": git("rev-parse", f"{EXEC_A}:{F}").stdout.decode().strip(),
    "stderr_blob_at_B": git("rev-parse", f"{EXEC_B}:{F}").stdout.decode().strip(),
    "stderr_blob_at_merge": git("rev-parse", f"{MERGE}:{F}").stdout.decode().strip(),
}
print(json.dumps(out, indent=1, sort_keys=True))
