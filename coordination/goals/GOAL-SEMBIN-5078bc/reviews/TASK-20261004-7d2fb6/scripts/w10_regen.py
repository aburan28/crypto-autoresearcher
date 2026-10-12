#!/usr/bin/env python3
"""w10_regen.py -- joint W10: regenerate hash-listed (untracked) instance files of RUN-SEMBIN-9bb990 from the generator at the manifest's code hashes
(git blob with the recorded sha256) and compare sha256 with excluded-large-instances.json byte-for-byte. Mirrors run_cert.measure()'s two writes:
  <iid>.json = json.dumps({"meta": {k: v for k, v in system.items() if k not in ("equations","var_names")}, "system": json.loads(canonical_bytes), "system_sha256": sha}, sort_keys=True).encode()
  <iid>.ms   = boolsys.write_msolve(system, path, field_equations=True)
Usage: w10_regen.py LISTINDEX...   (indices into the size-sorted list) | all-sample"""
import sys, os, json, hashlib, time, subprocess, re, tempfile, pathlib
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]; SP = os.environ["SP"]
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"
CODE = f"{REPO}/experiments/EXP-SEMBIN-7e1371/code"
# generator at the recorded hashes: take git blobs with those sha256 (history has exactly one version of each; verify)
import yaml
rec = yaml.safe_load(open(f"{RUN}/manifest.yaml"))["run"]["code"]["code_sha256"]
gen_dir = f"{SP}/work/gen_at_recorded_hash"; os.makedirs(gen_dir, exist_ok=True)
for fn in ("boolsys.py", "eq4sys.py"):
    blob = None
    for c in subprocess.run(["git", "-C", REPO, "log", "--format=%H", "--", f"experiments/EXP-SEMBIN-7e1371/code/{fn}"], capture_output=True, text=True).stdout.split():
        b = subprocess.run(["git", "-C", REPO, "show", f"{c}:experiments/EXP-SEMBIN-7e1371/code/{fn}"], capture_output=True).stdout
        if hashlib.sha256(b).hexdigest() == rec[fn]: blob = (c, b); break
    assert blob, f"no git blob with sha256 {rec[fn]} for {fn}"
    open(f"{gen_dir}/{fn}", "wb").write(blob[1]); print(f"{fn}: git blob sha256 {rec[fn][:16]} found in commit {blob[0][:10]}; written to scratch")
sys.path.insert(0, gen_dir); sys.path.insert(0, f"{REPO}/harness/macaulay_fp/fixtures")
import boolsys, eq4sys
assert hashlib.sha256(open(boolsys.__file__, "rb").read()).hexdigest() == rec["boolsys.py"]
SEEDS = [20260913101, 20260913102, 20260913103, 20260913104, 20260913105]
ex = json.load(open(f"{RUN}/excluded-large-instances.json"))["files"]
ex = sorted(ex, key=lambda f: f["bytes"])
def parse(path):
    m = re.fullmatch(r"light_controls/cells/instances/e4_n(\d+)_m(\d+)_t(\d+)_k(\d+)_(low|ran)_B_(equ|ran)_s(\d+)_d(\d+)\.(ms|json)", path)
    n, mm, t, k, sub, b, seed, draw, ext = m.groups()
    return dict(n=int(n), m=int(mm), t=int(t), k=int(k), subspace={"low": "low_degree_polynomial", "ran": "random_k_dimensional"}[sub],
                B_mode={"equ": "B_equals_1", "ran": "B_random"}[b], seed=int(seed), draw=int(draw), ext=ext)
def sel(args):
    if args and args[0] == "sample":
        n = len(ex); idx = sorted({0, n - 1, n // 2, n // 4, 3 * n // 4} | set(range(0, n, 9)))
        return idx
    return [int(a) for a in args]
out = []
cache = {}
for i in sel(sys.argv[1:]):
    f = ex[i]; p = parse(f["path"]); t0 = time.time()
    key = (p["n"], p["m"], p["k"], p["subspace"], p["B_mode"], p["seed"], p["draw"])
    if key not in cache:
        system = eq4sys.generate(p["n"], p["m"], p["k"], p["B_mode"], p["subspace"], p["seed"], p["draw"])
        canon = boolsys.canonical_bytes(system); sha = hashlib.sha256(canon).hexdigest()
        jbytes = json.dumps({"meta": {k: v for k, v in system.items() if k not in ("equations", "var_names")}, "system": json.loads(canon), "system_sha256": sha}, sort_keys=True).encode()
        with tempfile.TemporaryDirectory(dir=f"{SP}/work") as td:
            msha = boolsys.write_msolve(system, pathlib.Path(td) / "x.ms", field_equations=True)
            msize = os.path.getsize(pathlib.Path(td) / "x.ms")
        cache = {key: (sha, hashlib.sha256(jbytes).hexdigest(), len(jbytes), msha, msize)}
    sha, jsha, jlen, msha, msize = cache[key]
    got, glen = (jsha, jlen) if p["ext"] == "json" else (msha, msize)
    row = {"index": i, "path": f["path"], "listed_sha256": f["sha256"], "listed_bytes": f["bytes"], "regenerated_sha256": got, "regenerated_bytes": glen,
           "sha256_equal": got == f["sha256"], "bytes_equal": glen == f["bytes"], "system_sha256_regenerated": sha, "seconds": round(time.time() - t0, 1)}
    out.append(row)
    print(f"[{i:2d}] {f['path'].split('/')[-1]:62s} listed {f['bytes']:>9d} B  regenerated {glen:>9d} B  sha256 equal: {row['sha256_equal']}  ({row['seconds']}s)", flush=True)
suffix = "_".join(sys.argv[1:])[:40]
json.dump(out, open(f"{WS}/outputs/w10_regen_{suffix}.json", "w"), indent=1)
