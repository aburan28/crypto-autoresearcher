#!/usr/bin/env python3
"""C-WATCHDOG-NULL direction (ii): a synthetic null object that RESERVES address space
without making it resident.

It mmaps `--reserve-gib` of anonymous PROT_NONE memory (MAP_NORESERVE, never touched, so no
page is ever faulted in) and then touches only `--touch-mib` of ordinary memory. It reports
its own VmSize and VmRSS so both quantities are auditable from the log alone.

This is the object that distinguishes the new limit from the old one: an RLIMIT_AS cap below
the reservation refuses the mapping outright, while a RESIDENT-SET watchdog must let this
process run to completion and exit 0. Killing it would reproduce the very defect D2 removes.
"""
import argparse
import ctypes
import ctypes.util
import mmap
import os
import sys
import time

PAGE = 4096
MAP_NORESERVE = 0x4000
MAP_PRIVATE = 0x02
MAP_ANONYMOUS = 0x20
PROT_NONE = 0x0


def status_kb(field):
    for ln in open(f"/proc/{os.getpid()}/status"):
        if ln.startswith(field + ":"):
            return int(ln.split()[1])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reserve-gib", type=int, required=True)
    ap.add_argument("--touch-mib", type=int, required=True)
    ap.add_argument("--hold-s", type=float, default=5.0)
    a = ap.parse_args()
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    libc.mmap.restype = ctypes.c_void_p
    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int,
                          ctypes.c_int, ctypes.c_long]
    length = a.reserve_gib << 30
    addr = libc.mmap(None, length, PROT_NONE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0)
    if addr in (None, ctypes.c_void_p(-1).value, 2 ** 64 - 1):
        print(f"MMAP_FAILED errno={ctypes.get_errno()} reserve_gib={a.reserve_gib}", flush=True)
        return 2
    print(f"reserved_gib={a.reserve_gib} vmsize_kb={status_kb('VmSize')}"
          f" vmrss_kb={status_kb('VmRSS')} vmpeak_kb={status_kb('VmPeak')}", flush=True)
    buf = bytearray(a.touch_mib << 20)
    for off in range(0, len(buf), PAGE):
        buf[off] = 0x5A
    print(f"touched_mib={a.touch_mib} vmsize_kb={status_kb('VmSize')}"
          f" vmrss_kb={status_kb('VmRSS')} t={time.monotonic():.3f}", flush=True)
    # Hold, so the watchdog has many polling intervals in which it could wrongly kill us.
    t0 = time.monotonic()
    while time.monotonic() - t0 < a.hold_s:
        time.sleep(0.25)
    print(f"SURVIVED_TO_EXIT vmsize_kb={status_kb('VmSize')} vmrss_kb={status_kb('VmRSS')}"
          f" held_s={a.hold_s}", flush=True)
    libc.munmap(ctypes.c_void_p(addr), length)
    return 0


if __name__ == "__main__":
    sys.exit(main())
