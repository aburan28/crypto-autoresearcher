#!/usr/bin/env python3
"""Null object (ii): reserve >= 64 GiB of ADDRESS SPACE (PROT_NONE, MAP_NORESERVE) and touch
< 512 MiB resident, printing own /proc/self/status at intervals.  Must SURVIVE a
resident-set limit of 8 GiB; would be killed by RLIMIT_AS <= 64 GiB."""
import ctypes, mmap, os, sys, time
reserve_gib = int(sys.argv[1]) if len(sys.argv) > 1 else 64
touch_mib = int(sys.argv[2]) if len(sys.argv) > 2 else 384
def status():
    d = {}
    for ln in open('/proc/self/status'):
        k, v = ln.split(':', 1); d[k] = v.strip()
    return f"VmRSS={d['VmRSS']} VmHWM={d['VmHWM']} VmSize={d['VmSize']} VmPeak={d['VmPeak']}"
print(f"reserve_addrspace pid={os.getpid()} pgid={os.getpgid(0)} reserve={reserve_gib} GiB touch={touch_mib} MiB", flush=True)
print("limits:", [l.strip() for l in open('/proc/self/limits') if 'address space' in l], flush=True)
libc = ctypes.CDLL(None, use_errno=True)
libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
MAP_NORESERVE = 0x4000
PROT_NONE = 0
reserved = []
for i in range(reserve_gib // 8):
    p = libc.mmap(None, 8 << 30, PROT_NONE, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS | MAP_NORESERVE, -1, 0)
    if p is None or p == ctypes.c_void_p(-1).value:
        err = ctypes.get_errno(); print(f"mmap reservation FAILED at chunk {i}: errno={err} {os.strerror(err)}", flush=True); sys.exit(3)
    reserved.append(p)
    print(f"t={time.monotonic():.3f} reserved={(i + 1) * 8} GiB {status()}", flush=True)
step = 64 << 20
blocks = []; touched = 0
while touched < touch_mib << 20:
    m = mmap.mmap(-1, step, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    for off in range(0, step, 4096):
        m[off] = 1
    blocks.append(m); touched += step
    print(f"t={time.monotonic():.3f} touched={touched >> 20} MiB {status()}", flush=True)
    time.sleep(0.3)
print("SURVIVED: reserved", reserve_gib, "GiB address space, resident", status(), flush=True)
time.sleep(1.0)
