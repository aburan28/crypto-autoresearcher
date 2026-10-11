"""Run the PROTOCOL.md rho sample: shuffled jobs on 4 pinned cores, then a sequential pinned per-step bench."""
import csv, os, queue, random, subprocess, sys, threading

curves = list(csv.DictReader(open("sample.csv")))  # id,level,b
jobs = []
for c in curves:
    modes = [0, 1] if c["level"] == "crater" else [0]
    chunks = 10 if c["level"] == "crater" else 2
    for m in modes:
        for r in range(chunks):
            seed = 100000 + 1000 * int(c["id"]) + 10 * m + r
            jobs.append((c["id"], c["b"], m, r, seed))
random.Random(20261005).shuffle(jobs)
os.makedirs("raw", exist_ok=True)
q = queue.Queue()
for j in jobs: q.put(j)
lock = threading.Lock(); done = [0]

def worker(core):
    while True:
        try: cid, b, m, r, seed = q.get_nowait()
        except queue.Empty: return
        out = f"raw/c{cid}_m{m}_r{r}.csv"
        subprocess.run(["taskset", "-c", str(core), "./rho", "run", b, "0", str(m), "500", str(seed), out], check=True)
        with lock:
            done[0] += 1
            if done[0] % 25 == 0: print(f"{done[0]}/{len(jobs)} jobs", flush=True)

ts = [threading.Thread(target=worker, args=(k,)) for k in range(4)]
for t in ts: t.start()
for t in ts: t.join()
print("solves done", flush=True)

bench = [(c["id"], c["b"], 0) for c in curves] + [(c["id"], c["b"], 1) for c in curves if c["level"] == "crater"]
order = [x for rep in range(5) for x in random.Random(rep).sample(bench, len(bench))]
with open("ns_per_step.csv", "w") as f:
    f.write("id,mode,ns\n")
    for cid, b, m in order:
        o = subprocess.run(["taskset", "-c", "0", "./rho", "bench", b, "0", str(m), "1048576", "77", "1"], capture_output=True, text=True, check=True)
        f.write(f"{cid},{m},{o.stdout.split()[0]}\n")
print("bench done", flush=True)
