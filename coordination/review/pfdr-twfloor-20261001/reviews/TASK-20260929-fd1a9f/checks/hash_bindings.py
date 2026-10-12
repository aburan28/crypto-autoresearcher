"""F1(e): BI-1 engine pins and run-file receipts, re-hashed at the detached worktree.
TASK-20260929-fd1a9f (post-seal). Reads the census-m4 attempt-1 execution.json
source_sha256 pins and the f15632 / 599b4b / 0f66ef snapshot receipts."""
import hashlib, json, os, sys
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
ARCH = WT + "/coordination/design/TASK-20260928-102217/archives"
DEV4 = "68165e094c51f90c2aafd4e51510f414622b53b2145a0af6c279c32af93f5e68"
PRR6 = {"src/crypto_autoresearcher/index_calculus/curve.py", "src/crypto_autoresearcher/index_calculus/__main__.py",
        "tests/test_index_calculus_harvest.py", "experiments/EXP-PFDR-1b78f7/analyze_census.py"}
PRR1 = {"experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m3/manifest.yaml",
        "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m4/manifest.yaml"}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


out = {}
pins = json.load(open(WT + "/experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m4/execution.json"))["source_sha256"]
bi1 = {}
for path, d in sorted(pins.items()):
    want = DEV4 if path.endswith("amd-1de84f/summarize_run.py") else d["sha256"]
    got = sha(os.path.join(WT, path))
    bi1[path] = {"pin": want, "at_66d6eab71": got, "equal": got == want}
out["BI-1"] = {"files": len(bi1), "equal": sum(v["equal"] for v in bi1.values()), "detail": bi1}
rec = {}
for t in ("TASK-20260928-f15632", "TASK-20260929-599b4b", "TASK-20260929-0f66ef"):
    r = json.load(open(f"{ARCH}/{t}/snapshot-receipt.json"))
    res = {"paths": len(r["path_sha256"]), "match": 0, "mismatch": [], "missing": []}
    for path, want in sorted(r["path_sha256"].items()):
        fp = os.path.join(WT, path)
        if not os.path.exists(fp):
            res["missing"].append(path)
            continue
        got = sha(fp)
        if got == want:
            res["match"] += 1
        else:
            res["mismatch"].append({"path": path, "receipt": want, "at_66d6eab71": got,
                                    "known": "PRR-6" if (t.endswith("f15632") and path in PRR6) else ("PRR-1" if path in PRR1 else None)})
    rec[t] = res
out["receipts"] = rec
# which receipt binds each run file this task read (from rederivation/out/inputs.json) and the post-seal files
inp = json.load(open(sys.argv[2]))
read_files = sorted(set(p for grp in inp.values() for p in grp))
read_files += ["experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-analysis/analysis.json",
               "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-stage-r/analysis.json",
               "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m4/execution.json"]
binding = {}
allmaps = {t: json.load(open(f"{ARCH}/{t}/snapshot-receipt.json"))["path_sha256"]
           for t in ("TASK-20260928-f15632", "TASK-20260929-599b4b", "TASK-20260929-0f66ef")}
for path in read_files:
    got = sha(os.path.join(WT, path))
    hits = {t: (m[path] == got) for t, m in allmaps.items() if path in m}
    binding[path] = {"sha256": got, "bound_by": hits, "status": ("bound_and_equal" if hits and all(hits.values()) else
                                                                ("MISMATCH" if hits else "UNBOUND"))}
out["read_run_files"] = {"n": len(binding), "bound_and_equal": sum(1 for v in binding.values() if v["status"] == "bound_and_equal"),
                         "not_ok": {k: v for k, v in binding.items() if v["status"] != "bound_and_equal"}, "detail": binding}
json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
print(json.dumps({"BI-1": {k: v for k, v in out["BI-1"].items() if k != "detail"},
                  "receipts": {t: {k: (v if k != "mismatch" else [(m["path"], m["known"]) for m in v]) for k, v in r.items()} for t, r in rec.items()},
                  "read_run_files": {k: v for k, v in out["read_run_files"].items() if k != "detail"}}, indent=1))
