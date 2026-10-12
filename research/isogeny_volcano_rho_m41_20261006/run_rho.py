"""PROTOCOL.md phases 1-3 (m = 41): shuffled solves on 4 pinned cores; sequential per-step bench; idle timing test."""
import csv, os, queue, random, subprocess, threading

curves = list(csv.DictReader(open("sample.csv")))  # id,level,b
jobs = []
for c in curves:
    if c["level"] == "crater":
        for m in (0, 1):
            for r in range(15):
                jobs.append((c["id"], c["b"], m, r, 200, 100000 + 10 * m + r))
    else:
        jobs.append((c["id"], c["b"], 0, 0, 200, 100000 + 1000 * int(c["id"])))
random.Random(20261006).shuffle(jobs)
os.makedirs("raw", exist_ok=True)
q = queue.Queue()
for j in jobs: q.put(j)
lock = threading.Lock(); done = [0]

def worker(core):
    while True:
        try: cid, b, m, r, n, seed = q.get_nowait()
        except queue.Empty: return
        subprocess.run(["taskset", "-c", str(core), "./rho", "run", b, "0", str(m), str(n), str(seed), f"raw/c{cid}_m{m}_r{r}.csv"], check=True)
        with lock:
            done[0] += 1
            print(f"{done[0]}/{len(jobs)} jobs", flush=True)

ts = [threading.Thread(target=worker, args=(k,)) for k in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("phase 1 done", flush=True)

bench = [(c["id"], c["b"], 0) for c in curves] + [("0", "1", 1)]
order = [x for rep in range(3) for x in random.Random(rep).sample(bench, len(bench))]
with open("ns_per_step.csv", "w") as f:
    f.write("id,mode,ns\n")
    for cid, b, m in order:
        o = subprocess.run(["taskset", "-c", "0", "./rho", "bench", b, "0", str(m), "1048576", "77", "1"], capture_output=True, text=True, check=True)
        f.write(f"{cid},{m},{o.stdout.split()[0]}\n"); f.flush()
print("phase 2 done", flush=True)

byid = {c["id"]: c for c in curves}
arms = [("0", 0), ("0", 1)] + [(c["id"], 0) for lev in ("floor409", "floor1721", "bottom")
                               for c in [x for x in curves if x["level"] == lev][:2]]
os.makedirs("raw_idle", exist_ok=True)
for r in range(15):
    for cid, m in arms:
        subprocess.run(["taskset", "-c", "0", "./rho", "run", byid[cid]["b"], "0", str(m), "20", str(500000 + 100 * int(cid) + 10 * m + r),
                        f"raw_idle/c{cid}_m{m}_r{r}.csv"], check=True)
    print(f"idle round {r} done", flush=True)
print("phase 3 done", flush=True)
