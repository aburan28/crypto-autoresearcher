"""Factor the open 4q-t^2 composites: ECM (tiers, 4 parallel) then CADO-NFS (smallest first, <= CADO_MAX digits).
Resumable: state in state.json (composite -> {"factors": [...primes], "open": [...composites], "ecm_done": tier}).
Every event appended to events.log."""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import cypari2
pari = cypari2.Pari()
D = os.path.dirname(os.path.abspath(__file__))
ST = os.path.join(D, "state.json"); LOG = os.path.join(D, "events.log")
CADO = os.path.join(D, "..", "cado-nfs", "cado-nfs.py")
TIERS = [(11000, 90), (50000, 240), (250000, 500), (1000000, 900)]
CADO_MAX = int(os.environ.get("CADO_MAX", "121"))
def log(msg):
    with open(LOG, "a") as f: f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ ", time.gmtime()) + msg + "\n")
    print(msg, flush=True)
def isprime(n): return bool(pari.isprime(n))
def load():
    if os.path.exists(ST): return json.load(open(ST))
    jobs = json.load(open(os.path.join(D, "jobs.json")))
    done = {}
    for l in open("/home/user/wt/native-export/research/endosweep_nist_20261006/factorizations.jsonl"):
        r = json.loads(l); done[int(r["N"])] = r
    st = {}
    for j in jobs:
        c = int(j["N"]); pre = [N for N in done if N % c == 0]
        e = {"curve": j["curve"], "C": j["N"], "primes": [], "open": [j["N"]], "ecm_tier": 0, "log": []}
        if pre:
            fs = [int(p) for p, k in done[pre[0]]["factors"] for _ in range(k) if c % int(p) == 0]
            e["primes"] = [str(p) for p in fs]; e["open"] = []; e["log"].append(f"already factored in endosweep_nist factorizations.jsonl ({done[pre[0]]['curve']})")
        st[j["N"]] = e
    json.dump(st, open(ST, "w"), indent=1); return st
def save(st): json.dump(st, open(ST + ".tmp", "w"), indent=1); os.replace(ST + ".tmp", ST)
def split(e, n, f, how):
    """n = f * (n//f): replace n in open by its parts, primes moved to primes."""
    e["open"].remove(str(n)); e["log"].append(f"{how}: {len(str(n))}-digit -> {len(str(f))} x {len(str(n//f))}")
    for part in (f, n // f):
        (e["primes"] if isprime(part) else e["open"]).append(str(part))
def ecm_run(n, B1, curves):
    p = subprocess.run(["nice", "-n", "5", "ecm", "-q", "-one", "-c", str(curves), str(B1)], input=str(n), capture_output=True, text=True)
    nums = [int(x) for x in p.stdout.split()]
    # -q prints the factor(s) found then cofactor; no factor -> just n
    fs = [x for x in nums if 1 < x < n and n % x == 0]
    return min(fs) if fs else None
def ecm_stage(st, tier_max):
    work = [(k, e) for k, e in st.items() if e["open"]]
    for ti in range(tier_max):
        B1, curves = TIERS[ti]
        todo = [(k, e, int(n)) for k, e in work for n in list(e["open"]) if e["ecm_tier"] <= ti]
        if not todo: continue
        log(f"ECM tier B1={B1} x{curves}: {len(todo)} composites")
        import threading; lock = threading.Lock()
        def one(t):
            k, e, n = t; f = ecm_run(n, B1, curves)
            with lock:
                if f:
                    split(e, n, f, f"ECM B1={B1}"); log(f"{e['curve']}: ECM B1={B1} found {len(str(f))}-digit factor of C{len(str(n))}")
                e.setdefault("ecm_done", {})[str(n)] = ti + 1
                save(st)
        todo = [t for t in todo if st[t[0]].get("ecm_done", {}).get(str(t[2]), 0) <= ti]
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(one, todo))
        for k, e in work: e["ecm_tier"] = max(e["ecm_tier"], ti + 1)
        save(st)
def small(st):
    for k, e in st.items():
        for n in [n for n in e["open"] if len(n) <= 60]:
            t0 = time.time(); F = pari.factorint(int(n)); ps = [int(p) for p in F[0]]
            split(e, int(n), ps[0], f"PARI factorint ({time.time()-t0:.0f} s)")
            log(f"{e['curve']}: PARI split C{len(n)}")
    save(st)
def cado(st):
    failed = set()
    while True:
        small(st)
        cands = sorted(((len(n), k, n) for k, e in st.items() for n in e["open"] if len(n) <= CADO_MAX and n not in failed))
        if not cands: return
        _, k, n = cands[0]; e = st[k]
        wd = os.path.join(D, "cado", f"c{len(n)}_{n[:8]}"); os.makedirs(wd, exist_ok=True)
        log(f"{e['curve']}: CADO-NFS on C{len(n)} (workdir {wd})")
        t0 = time.time()
        snaps = sorted((os.path.join(wd, f) for f in os.listdir(wd) if ".parameters_snapshot." in f), key=os.path.getmtime)
        if snaps:   # resume an interrupted run: stop orphaned clients, set stuck workunits aside
            for line in subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True).stdout.splitlines():
                if "cado-nfs-client.py" in line and "ps -eo" not in line:
                    subprocess.run(["kill", line.split()[0]])
            time.sleep(2)
            subprocess.run(["python3", os.path.join(D, "..", "cado_c130", "clean_uploads.py"), wd, os.path.join(wd, "stale")])
            args = [snaps[-1]]; log(f"  resuming from {os.path.basename(snaps[-1])}")
        else:
            args = [n, "-t", "4", "-w", wd]
        with open(os.path.join(wd, "cado.log"), "a") as lf:
            p = subprocess.run(["nice", "-n", "5", "python3", CADO] + args, stdout=subprocess.PIPE, stderr=lf, text=True)
        out = p.stdout.split()
        fs = [int(x) for x in out if x.isdigit() and 1 < int(x) < int(n) and int(n) % int(x) == 0]
        if not fs:
            log(f"{e['curve']}: CADO failed on C{len(n)} rc={p.returncode}: see cado.log"); failed.add(n); continue
        split(e, int(n), fs[0], f"CADO-NFS ({time.time()-t0:.0f} s wall)")
        log(f"{e['curve']}: CADO split C{len(n)} into {len(str(fs[0]))} x {len(str(int(n)//fs[0]))} in {time.time()-t0:.0f} s")
        save(st)
if __name__ == "__main__":
    st = load()
    ecm_stage(st, 3)                       # to t30 for everything
    cado(st)                               # NFS for <= CADO_MAX digits
    ecm_stage(st, 4)                       # t35 on what is left (the big ones)
    left = [(e["curve"], [len(n) for n in e["open"]]) for e in st.values() if e["open"]]
    log(f"DONE stage; still open: {left}")
