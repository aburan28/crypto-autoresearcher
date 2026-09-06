"""Write artifact_inventory.json for TASK-20260906-d17254: every file under the
task's write_scope with its sha256 and size (the snapshot archive binds this set)."""
import hashlib, json, os, sys
from datetime import datetime, timezone
REPO = "/home/user/crypto-autoresearcher"
TASK_DIR = "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-289698/tasks/TASK-20260906-d17254"
SCOPES = ["experiments/EXP-ECDLP-869870/runs", "experiments/EXP-ECDLP-869870/source", TASK_DIR]
out_path = os.path.join(REPO, TASK_DIR, "artifact_inventory.json")
files = []
for scope in SCOPES:
    for root, dirs, names in os.walk(os.path.join(REPO, scope)):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for n in sorted(names):
            p = os.path.join(root, n); rel = os.path.relpath(p, REPO)
            if rel == os.path.relpath(out_path, REPO):
                continue
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
            files.append({"path": rel, "sha256": h, "bytes": os.path.getsize(p)})
inv = {"task_id": "TASK-20260906-d17254", "experiment_id": "EXP-ECDLP-869870", "goal_id": "GOAL-ECDLP-bbc21f", "batch_id": "BATCH-289698",
       "recorded_at": datetime.now(timezone.utc).isoformat(), "write_scope": SCOPES, "file_count": len(files),
       "note": "artifact_inventory.json itself is excluded from its own list; execution_report.yaml is included", "files": files}
json.dump(inv, open(out_path, "w"), indent=1)
print("inventory:", len(files), "files ->", out_path)
