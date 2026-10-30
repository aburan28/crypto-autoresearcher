"""Run a command, sample the RSS of its process tree every 0.5 s, report peaks.

Kills the tree if MemAvailable drops below a floor, so the container survives;
the peak observed up to the kill is then a lower bound.
usage: measure.py LABEL LOGDIR -- cmd...
"""
import os, resource, signal, subprocess, sys, time

label, logdir = sys.argv[1], sys.argv[2]
cmd = sys.argv[sys.argv.index("--") + 1:]
FLOOR_KB = 600 * 1024

def meminfo():
    d = {}
    for line in open("/proc/meminfo"):
        k, v = line.split(":", 1)
        d[k] = int(v.split()[0])
    return d

def tree(root):
    kids = {}
    for p in os.listdir("/proc"):
        if p.isdigit():
            try:
                ppid = int(open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()[1])
                kids.setdefault(ppid, []).append(int(p))
            except OSError:
                pass
    out, stack = [], [root]
    while stack:
        q = stack.pop(); out.append(q); stack += kids.get(q, [])
    return out

def status(pid):
    d = {}
    try:
        for line in open(f"/proc/{pid}/status"):
            if line.startswith(("Name:", "VmRSS:", "VmHWM:", "Threads:")):
                k, v = line.split(":", 1); d[k] = v.split()[0]
    except OSError:
        pass
    return d

env = dict(os.environ)
t0 = time.time()
p = subprocess.Popen(cmd, env=env, start_new_session=True,
                     stdout=open(f"{logdir}/{label}.stdout", "w"), stderr=subprocess.STDOUT)
peak_tree = peak_lean_hwm = 0; min_avail = 1 << 62; killed = False; max_threads = 0
samples = open(f"{logdir}/{label}.samples.tsv", "w")
samples.write("t_s\ttree_rss_kb\tlean_hwm_kb\tlean_threads\tmem_available_kb\n")
while p.poll() is None:
    rss = hwm = thr = 0
    for q in tree(p.pid):
        s = status(q)
        rss += int(s.get("VmRSS", 0))
        if s.get("Name") == "lean":
            hwm = max(hwm, int(s.get("VmHWM", 0))); thr = max(thr, int(s.get("Threads", 0)))
    avail = meminfo()["MemAvailable"]
    peak_tree = max(peak_tree, rss); peak_lean_hwm = max(peak_lean_hwm, hwm)
    min_avail = min(min_avail, avail); max_threads = max(max_threads, thr)
    samples.write(f"{time.time()-t0:.1f}\t{rss}\t{hwm}\t{thr}\t{avail}\n"); samples.flush()
    if avail < FLOOR_KB and not killed:
        killed = True
        os.killpg(p.pid, signal.SIGKILL)
    time.sleep(0.5)
rc = p.wait()
ru = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
summary = (f"label={label} exit={rc} killed_by_watchdog={killed} wall_s={time.time()-t0:.0f} "
           f"peak_tree_rss_kb={peak_tree} peak_lean_VmHWM_kb={peak_lean_hwm} "
           f"rusage_children_maxrss_kb={ru} max_lean_threads={max_threads} min_MemAvailable_kb={min_avail}")
print(summary)
open(f"{logdir}/{label}.summary", "w").write(summary + "\n")
