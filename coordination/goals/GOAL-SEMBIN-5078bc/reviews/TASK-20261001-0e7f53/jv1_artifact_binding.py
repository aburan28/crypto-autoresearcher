"""JV-1: bind the bytes this review diffed to RUN-SEMBIN-be48b7.

sha256 of every path listed in the run's artifact-digests.json, read from commit
b8019a6fb via `git show` (never the working tree), compared with the digest the
run recorded. A mismatch would mean the reviewed bytes are not the run's bytes.
"""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SNAP = "b8019a6fb"
RUN = "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-be48b7"


def blob(path):
    return subprocess.check_output(["git", "-C", str(REPO), "show", f"{SNAP}:{path}"])


dig = json.loads(blob(f"{RUN}/artifact-digests.json"))
rows = []
for section, entries in dig.items():
    if not isinstance(entries, dict) or section == "v1_unchanged_check":
        continue
    for p, want in entries.items():
        full = f"{RUN}/{p}" if section == "run_directory" else p
        try:
            got = hashlib.sha256(blob(full)).hexdigest()
        except subprocess.CalledProcessError:
            got = None
        rows.append(dict(section=section, path=full, recorded=want, at_snapshot=got, match=(got == want)))
out = dict(snapshot=SNAP, checked=len(rows), mismatches=[r for r in rows if not r["match"]],
           matched=sum(r["match"] for r in rows))
(HERE / "jv1_artifact_binding_output.json").write_text(json.dumps(dict(out, rows=rows), indent=1))
print(json.dumps(out, indent=1))
