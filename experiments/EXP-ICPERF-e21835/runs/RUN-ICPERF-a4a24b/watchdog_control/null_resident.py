#!/usr/bin/env python3
"""C-WATCHDOG-NULL direction (i): a synthetic null object that makes memory RESIDENT.

It touches `--target-mib` of memory in `--step-mib` increments, writing one byte per 4 KiB
page so every page is faulted in and counted in VmRSS, and prints its own view of its RSS
after each step so the schedule is auditable from the log alone. The watchdog must kill it.

No randomness: the byte written is a fixed constant, so there is no seed to record.
"""
import argparse
import os
import sys
import time

PAGE = 4096


def rss_kb():
    return int(open(f"/proc/{os.getpid()}/statm").read().split()[1]) * (os.sysconf("SC_PAGE_SIZE") // 1024)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-mib", type=int, required=True)
    ap.add_argument("--step-mib", type=int, default=128)
    ap.add_argument("--hold-s", type=float, default=0.05)
    a = ap.parse_args()
    print(f"schedule target_mib={a.target_mib} step_mib={a.step_mib} hold_s={a.hold_s}"
          f" page_bytes={PAGE} rss_kb_at_start={rss_kb()}", flush=True)
    blocks = []
    touched = 0
    while touched < a.target_mib:
        b = bytearray(a.step_mib << 20)
        for off in range(0, len(b), PAGE):
            b[off] = 0x5A
        blocks.append(b)
        touched += a.step_mib
        print(f"touched_mib={touched} rss_kb={rss_kb()} t={time.monotonic():.3f}", flush=True)
        time.sleep(a.hold_s)
    print(f"COMPLETED_WITHOUT_BEING_KILLED touched_mib={touched} rss_kb={rss_kb()}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
