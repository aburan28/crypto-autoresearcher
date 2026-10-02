"""J1(g): BI-1 -- hash every file pinned in R11 attempt-1 execution.json source_sha256
(summarize_run.py under the DEV-4 hash 68165e09...) plus README.md, every results/ file,
function-diff.json and source.diff (implementation-notes-amd1de84f pins), at a32e70808
and at dc61c5e1e (git show). IE-1 -- the invocation-check rows, staircase records and
harvest rows vs attempt 1's for keys (main, 4, 26, 0, *, *), my own comparator, M-3
exclusions (keys named seconds, ending _seconds, worker_maxrss_bytes, ru_maxrss_bytes at
any depth), record by record in emission order."""
import gzip, hashlib, json, os, subprocess, sys
import yaml
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
R11 = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-census-m4")
DEV4 = "68165e094c51f90c2aafd4e51510f414622b53b2145a0af6c279c32af93f5e68"


def h(b):
    return hashlib.sha256(b).hexdigest()


def git_show(rev, path):
    r = subprocess.run(["git", "-C", WT, "--no-optional-locks", "show", f"{rev}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items()
                if not (k == "seconds" or k.endswith("_seconds") or k in ("worker_maxrss_bytes", "ru_maxrss_bytes"))}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def load_gz(p, note):
    rl.opened(p, note)
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


def main():
    out = {}
    ex = json.load(open(rl.opened(os.path.join(R11, "execution.json"), "J1(g) BI-1: R11 attempt-1 execution.json (source_sha256)")))
    pins = ex.get("source_sha256") or {}
    notes = yaml.safe_load(open(rl.opened(os.path.join(WT, "experiments/EXP-PFDR-1b78f7/implementation-notes-amd1de84f.yaml"), "J1(g) BI-1: implementation-notes-amd1de84f pins")))
    flat = {}

    def walk(o, pre=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{pre}/{k}")
        elif isinstance(o, str) and len(o) == 64 and all(ch in "0123456789abcdef" for ch in o):
            flat[pre] = o
    walk(notes)
    extra = {}
    for key, v in flat.items():
        leaf = key.split("/")[-1]
        if leaf.endswith(("README.md", "function-diff.json", "source.diff")) or "/results/" in leaf or leaf.startswith("src/crypto_autoresearcher/index_calculus/results/"):
            extra[leaf] = v
    res = {}
    for path, pin in sorted(pins.items()):
        pin = pin["sha256"] if isinstance(pin, dict) else pin
        pin_used = DEV4 if path.endswith("summarize_run.py") else pin
        wt = h(open(os.path.join(WT, path), "rb").read()) if os.path.exists(os.path.join(WT, path)) else None
        dc = git_show("dc61c5e1e", path)
        res[path] = {"pin": pin_used, "pin_in_execution_json": pin, "a32e70808": wt, "dc61c5e1e": h(dc) if dc is not None else None}
        res[path]["ok"] = (wt == pin_used == res[path]["dc61c5e1e"])
    for path, pin in sorted(extra.items()):
        if path in res:
            continue
        wt = h(open(os.path.join(WT, path), "rb").read()) if os.path.exists(os.path.join(WT, path)) else None
        dc = git_show("dc61c5e1e", path)
        res[path] = {"pin": pin, "a32e70808": wt, "dc61c5e1e": h(dc) if dc is not None else None}
        res[path]["ok"] = (wt == pin == res[path]["dc61c5e1e"])
    rl.log(os.path.join(WT, "src"), "J1(g) BI-1: hashed the BI-1 file set at a32e70808 and via git show dc61c5e1e:<path>")
    out["BI1"] = {"files": len(res), "all_ok": all(v["ok"] for v in res.values()),
                  "failures": {k: v for k, v in res.items() if not v["ok"]}, "detail": res,
                  "summarize_run_pin_in_execution_json_vs_DEV4": {k: v["pin_in_execution_json"] for k, v in res.items() if k.endswith("summarize_run.py")}}
    # IE-1
    sel = lambda r: r.get("bits") == 26 and r.get("curve") == 0 and (r.get("m") == 4 or str(r.get("method", "")) == "ic_m4")
    a1 = {"rows": [r for r in load_gz(os.path.join(R11, "rows.jsonl.gz"), "J1(g) IE-1: attempt-1 rows") if sel(r)],
          "staircase": [r for r in load_gz(os.path.join(R11, "staircase.jsonl.gz"), "J1(g) IE-1: attempt-1 staircase") if sel(r)]}
    hr = []
    p = os.path.join(R11, "harvest-rows.jsonl.gz")
    rl.opened(p, "J1(g) IE-1: attempt-1 harvest rows, streamed (b26 c0 selected)")
    with gzip.open(p, "rt") as f:
        for l in f:
            r = json.loads(l)
            if sel(r):
                hr.append(r)
    a1["harvest"] = hr
    ic = os.path.join(R11, "attempt-2/invocation-check/b26-c0")
    chk = {"rows": load_gz(os.path.join(ic, "rows.jsonl.gz"), "J1(g) IE-1: invocation-check rows"),
           "staircase": load_gz(os.path.join(ic, "staircase.jsonl.gz"), "J1(g) IE-1: invocation-check staircase"),
           "harvest": load_gz(os.path.join(ic, "harvest-rows.jsonl.gz"), "J1(g) IE-1: invocation-check harvest rows")}
    ie = {}
    for k in ("rows", "staircase", "harvest"):
        A = [json.dumps(strip(r), sort_keys=True) for r in a1[k]]
        B = [json.dumps(strip(r), sort_keys=True) for r in chk[k]]
        diffs = [i for i, (x, y) in enumerate(zip(A, B)) if x != y]
        dk = set()
        for i in diffs[:20]:
            x, y = json.loads(A[i]), json.loads(B[i])
            dk |= {kk for kk in set(x) | set(y) if x.get(kk) != y.get(kk)}
        ie[k] = {"attempt1": len(A), "check": len(B), "equal_in_order": A == B, "differing_records": len(diffs),
                 "differing_top_level_keys": sorted(dk)}
    out["IE1"] = ie
    with open(os.path.join(W, "checks", "out", "j1g-bi1-ie1.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("BI-1 files", out["BI1"]["files"], "all_ok", out["BI1"]["all_ok"], "failures", list(out["BI1"]["failures"])[:10])
    print("summarize_run pin in execution.json:", out["BI1"]["summarize_run_pin_in_execution_json_vs_DEV4"])
    print("IE-1", ie)


if __name__ == "__main__":
    main()
