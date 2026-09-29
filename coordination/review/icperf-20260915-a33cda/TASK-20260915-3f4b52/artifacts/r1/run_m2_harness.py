#!/usr/bin/env python3
"""Validator's run of the REPAIRED harness's own phase_C path (bench.Runner.run + regex) on
n15l5-1-S, in a scratch run dir, with an EXTERNAL watcher that (a) reads the live child's
/proc/<pid>/limits and (b) independently polls kernel VmHWM / VmRSS / Threads of the child
so the harness's reported peak_rss_kb can be compared to a kernel high-water mark."""
import json, os, sys, threading, time
from pathlib import Path

TREE = sys.argv[1]  # path to code tree copy (repaired or frozen)
RUN_DIR = Path(sys.argv[2]); RUN_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, TREE)
import bench  # noqa

watch = {"limits": None, "max_vmhwm": 0, "max_vmrss": 0, "max_threads": 0, "last_vmrss": None, "polls": 0,
         "pgid_members_max": 0, "pid": None, "oom_score_adj_child": None}
stop = threading.Event()

def watcher(mypid):
    while not stop.is_set():
        try:
            if watch["pid"] is None:
                for e in os.listdir('/proc'):
                    if not e.isdigit(): continue
                    try:
                        st = open(f'/proc/{e}/stat', 'rb').read()
                        rest = st[st.rindex(b')') + 2:].split()
                        comm = st[st.index(b'(') + 1:st.rindex(b')')]
                        if int(rest[1]) == mypid and comm.startswith(b'M2'):
                            watch["pid"] = int(e); break
                    except (OSError, ValueError):
                        pass
            pid = watch["pid"]
            if pid is not None:
                if watch["limits"] is None:
                    watch["limits"] = [l.strip() for l in open(f'/proc/{pid}/limits') if 'address space' in l or 'resident' in l]
                    watch["oom_score_adj_child"] = open(f'/proc/{pid}/oom_score_adj').read().strip()
                    watch["cmdline"] = open(f'/proc/{pid}/cmdline','rb').read().replace(b'\0', b' ').decode()
                st = {}
                for ln in open(f'/proc/{pid}/status'):
                    k, v = ln.split(':', 1); st[k] = v.strip()
                if 'VmRSS' in st:
                    r = int(st['VmRSS'].split()[0]); h = int(st['VmHWM'].split()[0]); t = int(st['Threads'])
                    watch["max_vmrss"] = max(watch["max_vmrss"], r); watch["max_vmhwm"] = max(watch["max_vmhwm"], h)
                    watch["max_threads"] = max(watch["max_threads"], t); watch["last_vmrss"] = r
                # count process-group members (should be 1 for M2: threads are not listed in /proc)
                n = 0
                for e in os.listdir('/proc'):
                    if e.isdigit():
                        try:
                            s = open(f'/proc/{e}/stat', 'rb').read(); rest = s[s.rindex(b')') + 2:].split()
                            if int(rest[2]) == pid: n += 1
                        except (OSError, ValueError): pass
                watch["pgid_members_max"] = max(watch["pgid_members_max"], n)
                watch["polls"] += 1
        except (OSError, ValueError):
            pass
        time.sleep(0.1)

inst = [i for i in bench.instances() if i["stem"] == "n15l5-1-S"][0]
R = bench.Runner(RUN_DIR, dry=False)
pre = {"loadavg": os.getloadavg(), "mem_available_kb": [int(l.split()[1]) for l in open('/proc/meminfo') if l.startswith('MemAvailable')][0],
       "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tree": TREE}
th = threading.Thread(target=watcher, args=(os.getpid(),), daemon=True); th.start()
t0 = time.monotonic()
bench.phase_C(R, [inst])
stop.set(); th.join(timeout=2)
rows = [json.loads(l) for l in (RUN_DIR / "results.jsonl").read_text().splitlines()]
out = {"pre_launch": pre, "driver_wall_s": round(time.monotonic() - t0, 3), "watcher": watch, "rows": rows,
       "m2_stdout": (RUN_DIR / rows[-1]["stdout"]).read_text(errors='replace'),
       "m2_stderr": (RUN_DIR / rows[-1]["stderr"]).read_text(errors='replace')[-3000:],
       "loadavg_end": os.getloadavg()}
print(json.dumps(out, indent=1))
(RUN_DIR / "validator_capture.json").write_text(json.dumps(out, indent=1))
