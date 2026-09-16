#!/usr/bin/env python3
"""R4 controlled reproduction.  Launch <tree>/bench.environment() in a child whose STDIN IS AN
OPEN PIPE NOBODY WRITES TO (the inherited-stdin condition), under the validator's own wall
bound, and record the process tree (pid, ppid, pgid, sid, state, comm, wchan) while it hangs.
Usage: probe_repro.py <tree> <label> <wall_bound_s>"""
import json, os, subprocess, sys, time
TREE, LABEL, BOUND = sys.argv[1], sys.argv[2], float(sys.argv[3])
child_code = f"""
import sys, json, time; sys.path.insert(0, {TREE!r}); import bench
t0=time.monotonic(); env=bench.environment(); dt=time.monotonic()-t0
print(json.dumps({{'took_s': round(dt,3), 'M2': env.get('M2'), 'Singular': env.get('Singular'), 'cadical': env.get('cadical'), 'cryptominisat5': env.get('cryptominisat5'), 'gcc': env.get('gcc'), 'version_probe_seconds': env.get('version_probe_seconds') }}, default=str))
"""
r, w = os.pipe()  # w stays open in THIS process and is never written: the inherited-stdin condition
p = subprocess.Popen([sys.executable, "-c", child_code], stdin=r, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
os.close(r)
t0 = time.monotonic()

def tree(root):
    procs = {}
    for e in os.listdir('/proc'):
        if not e.isdigit(): continue
        try:
            st = open(f'/proc/{e}/stat', 'rb').read(); comm = st[st.index(b'(') + 1:st.rindex(b')')].decode(errors='replace')
            rest = st[st.rindex(b')') + 2:].split()
            wchan = open(f'/proc/{e}/wchan').read().strip() if os.path.exists(f'/proc/{e}/wchan') else ''
            fd0 = os.readlink(f'/proc/{e}/fd/0') if os.path.exists(f'/proc/{e}/fd/0') else ''
            procs[int(e)] = {"pid": int(e), "ppid": int(rest[1]), "pgid": int(rest[2]), "sid": int(rest[3]), "state": rest[0].decode(), "comm": comm, "wchan": wchan, "fd0": fd0}
        except (OSError, ValueError): pass
    out, todo = [], [root]
    while todo:
        x = todo.pop(0)
        if x in procs: out.append(procs[x])
        todo += [q for q in procs if procs[q]["ppid"] == x]
    return out

snaps = {}
rc = None
while True:
    rc = p.poll()
    el = time.monotonic() - t0
    if rc is not None: break
    for mark in (5, 30, 65, 90):
        if el >= mark and mark not in snaps:
            snaps[mark] = tree(p.pid)
    if el > BOUND:
        p.kill(); rc = "VALIDATOR_BOUND_KILL"; break
    time.sleep(0.5)
wall = time.monotonic() - t0
try:
    so, se = p.communicate(timeout=10)
except subprocess.TimeoutExpired:
    so, se = "<communicate timed out: a descendant still holds the pipe>", ""
    # find survivors in the child's original pgid
res = {"label": LABEL, "tree": TREE, "returncode": rc, "wall_s": round(wall, 3), "stdout": so[-3000:], "stderr": se[-3000:],
       "process_tree_snapshots": {str(k): v for k, v in snaps.items()}, "parent_pid": os.getpid(), "child_pid": p.pid}
print(json.dumps(res, indent=1))
json.dump(res, open(f"probe_repro_{LABEL}.json", "w"), indent=1)
