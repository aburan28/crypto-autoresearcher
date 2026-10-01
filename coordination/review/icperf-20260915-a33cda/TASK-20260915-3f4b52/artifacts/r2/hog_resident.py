#!/usr/bin/env python3
"""Null object (i): touch TARGET GiB RESIDENT in <= 256 MiB increments, printing own
/proc/self/status at intervals.  Must be KILLED by a resident-set limit below TARGET."""
import mmap, os, sys, time
target_gib = float(sys.argv[1]) if len(sys.argv) > 1 else 12.0
step = 256 << 20
pause = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
def status():
    d = {}
    for ln in open('/proc/self/status'):
        k, v = ln.split(':', 1); d[k] = v.strip()
    return f"VmRSS={d['VmRSS']} VmHWM={d['VmHWM']} VmSize={d['VmSize']} VmPeak={d['VmPeak']} Threads={d['Threads']}"
print(f"hog_resident pid={os.getpid()} pgid={os.getpgid(0)} target={target_gib} GiB step=256MiB", flush=True)
print("limits:", [l.strip() for l in open('/proc/self/limits') if 'address space' in l], flush=True)
blocks = []
touched = 0
while touched < target_gib * (1 << 30):
    m = mmap.mmap(-1, step, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    for off in range(0, step, 4096):
        m[off] = 1
    blocks.append(m); touched += step
    print(f"t={time.monotonic():.3f} touched={touched >> 20} MiB {status()}", flush=True)
    time.sleep(pause)
print("SURVIVED: reached target resident", status(), flush=True)
time.sleep(1.0)
