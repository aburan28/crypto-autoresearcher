#!/usr/bin/env python3
"""pilot4.py -- LEADS PILOT #4. EXPLORATORY, hypothesis-generating; not program evidence.
Same labelled instances as pilot #3 (instances/*.json, byte-identical copies).
usage: pilot4.py <kind> <cell> <variant> [--sel unsat:U,sat:S] [--timeout s] [--mem GB]
  kind cap : variant L<k>u<d> or fullu<d>   (locality <= k, at most d u-bits per monomial)
  kind pre : variant full | L2 | L1          (two-phase: z-free closure first, then the target block)
  kind win : variant w2 | w2u<d>            (2-block windows, messages on the shared block)
"""
import json, os, resource, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
P3 = Path("/home/user/crypto-autoresearcher/analysis/ecdlp2m-iteration-20261009/block-local-closure-pilot")
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "vendor"))
import pilot3  # build_chain, blocks (pilot #3, unchanged)
INST = HERE / "instances"; RES = HERE / "results"; JOBS = HERE / "jobs"
for d in (RES, JOBS): d.mkdir(exist_ok=True)

def parse(kind, v, nb):
    Lmax, du = nb, -1
    s = v
    if s.startswith("full"): s = s[4:]
    elif s.startswith("L"):
        i = 1
        while i < len(s) and s[i].isdigit(): i += 1
        Lmax = int(s[1:i]); s = s[i:]
    elif s.startswith("w2"): s = s[2:]
    if s.startswith("u"): du = int(s[1:]); s = ""
    if s: raise SystemExit("bad variant " + v)
    return Lmax, du

def windows(n, k, m, lo, hi):
    nb = m - 1; N = len(lo); W = []
    def meets(j, a, b): return hi[j] >= a and lo[j] <= b
    for a in range(nb - 1):
        mask = sum(1 << j for j in range(N) if meets(j, a, a + 1))
        left = sum(1 << j for j in range(N) if meets(j, a, a)) if a > 0 else 0       # shared with window a-1 = block a
        right = sum(1 << j for j in range(N) if meets(j, a + 1, a + 1)) if a < nb - 2 else 0
        W.append({"mask": mask, "left": left, "right": right, "blocks": [a, a + 1]})
    return W

def run(kind, cellname, variant, sel, timeout, mem):
    cell = json.load(open(INST / f"{cellname}.json")); insts = cell["instances"]
    m = cell.get("m", 3); n, k = cell["n"], cell["k"]
    lo, hi, nb = pilot3.blocks(n, k, m)
    Lmax, du = parse(kind, variant, nb)
    U = [x for x in insts if x["nsol"] == 0 and not x["dup_target"]][: sel.get("unsat", 10**9)]
    S = [x for x in insts if x["nsol"] > 0 and not x["dup_target"]][: sel.get("sat", 10**9)]
    outp = RES / f"{kind}-{cellname}.jsonl"; done = set()
    if outp.exists():
        for line in open(outp):
            r = json.loads(line); done.add((r["id"], r["variant"]))
    umask = (1 << ((m - 2) * n)) - 1
    print(f"{kind} {cellname} {variant}: m={m} n={n} k={k} N={(m-2)*n+m*k} U={len(U)} S={len(S)}", flush=True)
    with open(outp, "a") as f:
        for x in U + S:
            if (x["id"], variant) in done: continue
            sysm = pilot3.build_chain(n, k, m, cell["basis"], cell["b"], x["z"], cell["modulus"])
            eqs = sysm["equations"]; assert sysm["N"] == x["N"]
            job = {"kind": kind, "N": x["N"], "D": 4, "equations": eqs, "lo": lo, "hi": hi, "Lmax": Lmax,
                   "du": du, "umask": umask, "ngens0": len(eqs) - n, "witnesses": x["solutions"][:16]}
            if kind == "win":
                W = windows(n, k, m, lo, hi)
                # generators of window a: the equations of blocks a and a+1 (block b = polys[b], n equations each)
                for a, w in enumerate(W):
                    w["gens"] = [i for b in w["blocks"] for i in range(b * n, (b + 1) * n)]
                job["windows"] = W
            jp, op = JOBS / f"{kind}-{x['id']}-{variant}.json", JOBS / f"{kind}-{x['id']}-{variant}.out.json"
            json.dump(job, open(jp, "w")); t0 = time.time(); lim = int(mem * (1 << 30))
            try:
                r = subprocess.run(["nice", "-n", "19", sys.executable, str(HERE / "worker4.py"), str(jp), str(op)],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout,
                                   preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (lim, lim)))
                o = json.load(open(op)) if r.returncode == 0 else {"status": f"worker_rc{r.returncode}", "stderr": r.stderr.decode()[-300:]}
            except subprocess.TimeoutExpired:
                o = {"status": "censored_timeout"}
            for p in (jp, op):
                try: p.unlink()
                except OSError: pass
            row = {"id": x["id"], "m": m, "n": n, "k": k, "N": x["N"], "label": "UNSAT" if x["nsol"] == 0 else "SAT",
                   "nsol": x["nsol"], "kind": kind, "variant": variant, "Lmax": Lmax, "du": du,
                   "timeout_s": timeout, "mem_gb": mem, "outer_wall_s": time.time() - t0, **o}
            f.write(json.dumps(row) + "\n"); f.flush()
            one = o.get("one", o.get("two_phase", {}).get("one"))
            if row["label"] == "SAT" and one:
                raise SystemExit(f"SOUNDNESS FAULT {x['id']} {variant}")
            print(f"  {x['id']} {row['label']} one={one} wall={row['outer_wall_s']:.1f}s {o.get('status','')}", flush=True)

if __name__ == "__main__":
    kind, cellname, variant = sys.argv[1:4]
    sel, timeout, mem = {}, 1200, 3.0; a = sys.argv[4:]; i = 0
    while i < len(a):
        if a[i] == "--sel":
            for kv in a[i + 1].split(","): kk, vv = kv.split(":"); sel[kk] = int(vv)
        elif a[i] == "--timeout": timeout = int(a[i + 1])
        elif a[i] == "--mem": mem = float(a[i + 1])
        i += 2
    run(kind, cellname, variant, sel, timeout, mem)
