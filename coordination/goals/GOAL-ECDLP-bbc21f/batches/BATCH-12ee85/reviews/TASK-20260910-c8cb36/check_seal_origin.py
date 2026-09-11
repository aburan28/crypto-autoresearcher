import hashlib, subprocess
def blob(commit, path):
    return subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, check=True).stdout

SEAL_DIR = "coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-4433c1/reviews/TASK-20260907-7afa98"
seal = __import__("json").loads(blob("818b7a142", f"{SEAL_DIR}/seal.json"))
live_seal = __import__("json").load(open(f"{SEAL_DIR}/seal.json"))
mm = []
for f, decl in seal["sha256"].items():
    actual = hashlib.sha256(blob("818b7a142", f"{SEAL_DIR}/{f}")).hexdigest()
    if actual != decl:
        mm.append({"file": f, "declared": decl, "at_818b7a142": actual})
print("seal.json at 818b7a142 (origin commit) equals live seal.json:", seal == live_seal)
print("sealed-file hashes at 818b7a142 all match seal declarations:", not mm, mm)
# also check the ordering claim: seal.json timestamp vs commit time
import subprocess as sp
t = sp.run(["git","show","-s","--format=%cI","818b7a14250a7497f6ae6728958aefb6d5f267cf"],capture_output=True,text=True).stdout.strip()
print("origin commit time:", t, "| seal sealed_at_utc:", seal["sealed_at_utc"])
# Was any of the 4 packet files or contract material committed BEFORE 818b7a142?
for path, label in [("experiments/EXP-ECDLP-6ac801/specification.v3.yaml","spec v3"),
                    ("experiments/EXP-ECDLP-6ac801/amendments/v2_to_v3.yaml","amend v2->v3"),
                    ("experiments/EXP-ECDLP-6ac801/runs/RUN-ECDLP-6ac801-001/summary.json","v1 run 001")]:
    r = sp.run(["git","log","--format=%H %cI","-n1","--",path],capture_output=True,text=True).stdout.strip()
    print(f"first/last commit touching {label}: {r}")
