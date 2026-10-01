"""J1(g) BI-1 remainder: README.md, the 7 results/ files, function-diff.json and source.diff
against their implementation-notes-amd1de84f pins, at a32e70808 and via git show dc61c5e1e."""
import hashlib, json, os, subprocess, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks")); import rl
WT = rl.WT
notes = yaml.safe_load(open(os.path.join(WT, "experiments/EXP-PFDR-1b78f7/implementation-notes-amd1de84f.yaml")))
found = {}
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and len(v) == 64 and isinstance(k, str) and (k.endswith(("index_calculus/README.md", "function-diff.json", "source.diff")) or "/results/" in k):
                found[k] = v
            walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(notes)
res = {}
for path, pin in sorted(found.items()):
    wt = hashlib.sha256(open(os.path.join(WT, path), "rb").read()).hexdigest()
    r = subprocess.run(["git", "-C", WT, "--no-optional-locks", "show", f"dc61c5e1e:{path}"], capture_output=True)
    dc = hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None
    res[path] = {"pin": pin, "a32e70808": wt, "dc61c5e1e": dc, "ok": pin == wt == dc}
rl.log(os.path.join(WT, "src/crypto_autoresearcher/index_calculus/results"), "J1(g) BI-1: README, 7 results files, function-diff.json, source.diff hashed at a32e70808 and dc61c5e1e")
json.dump(res, open(os.path.join(W, "checks/out/j1g-bi1-extra.json"), "w"), indent=1, sort_keys=True)
for k, v in res.items(): print(v["ok"], k)
print("files", len(res), "all ok", all(v["ok"] for v in res.values()))
