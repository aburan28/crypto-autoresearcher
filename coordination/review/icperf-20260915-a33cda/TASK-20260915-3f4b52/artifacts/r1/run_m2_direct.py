#!/usr/bin/env python3
"""Validator's own direct M2 launch: verbatim stdout/stderr, independent peak-RSS
measurement (kernel VmHWM polled at 0.1 s + wait4 ru_maxrss), loadavg at start."""
import json, os, resource, subprocess, sys, time
from pathlib import Path

script = Path(sys.argv[1]); tag = sys.argv[2]
out_p, err_p = Path(f"{tag}.out"), Path(f"{tag}.err")
def meminfo():
    d = {}
    for ln in open('/proc/meminfo'):
        k, v = ln.split(':', 1); d[k] = int(v.split()[0])
    return d
rec = {"script": str(script), "loadavg_at_start": os.getloadavg(), "uptime_at_start": open('/proc/uptime').read().split()[0],
       "mem_available_kb_at_start": meminfo()["MemAvailable"], "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
before = resource.getrusage(resource.RUSAGE_CHILDREN)
t0 = time.monotonic()
with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
    p = subprocess.Popen(["M2", "--script", str(script)], stdout=fo, stderr=fe, stdin=subprocess.DEVNULL)
    max_vmrss = max_vmhwm = max_threads = 0; polls = 0; last_vmrss = None; last_vmhwm = None
    limits = None
    while True:
        rc = p.poll()
        try:
            st = {}
            for ln in open(f"/proc/{p.pid}/status"):
                k, v = ln.split(':', 1); st[k] = v.strip()
            if 'VmRSS' in st:
                vmrss = int(st['VmRSS'].split()[0]); vmhwm = int(st['VmHWM'].split()[0]); thr = int(st['Threads'])
                max_vmrss = max(max_vmrss, vmrss); max_vmhwm = max(max_vmhwm, vmhwm); max_threads = max(max_threads, thr)
                last_vmrss, last_vmhwm = vmrss, vmhwm
            if limits is None:
                limits = [l for l in open(f"/proc/{p.pid}/limits") if 'address space' in l or 'resident' in l]
            polls += 1
        except (OSError, ValueError):
            pass
        if rc is not None:
            break
        if time.monotonic() - t0 > 600:
            p.kill(); rc = "TIMEOUT"; break
        time.sleep(0.1)
wall = time.monotonic() - t0
after = resource.getrusage(resource.RUSAGE_CHILDREN)
rec.update({"returncode": rc, "wall_s": round(wall, 3), "cpu_s_children": round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 3),
            "ru_maxrss_kb_children": after.ru_maxrss, "sampled_max_VmRSS_kb": max_vmrss, "sampled_max_VmHWM_kb": max_vmhwm,
            "last_VmRSS_kb": last_vmrss, "last_VmHWM_kb": last_vmhwm, "max_threads": max_threads, "polls_0.1s": polls,
            "child_limits_lines": [l.strip() for l in (limits or [])], "loadavg_at_end": os.getloadavg(),
            "stdout": out_p.read_text(errors='replace'), "stderr": err_p.read_text(errors='replace')})
print(json.dumps(rec, indent=1))
Path(f"{tag}.json").write_text(json.dumps(rec, indent=1))
