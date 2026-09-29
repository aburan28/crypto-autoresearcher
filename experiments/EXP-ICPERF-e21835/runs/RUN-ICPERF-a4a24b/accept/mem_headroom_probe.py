#!/usr/bin/env python3
"""Epoch-2 machine-protection probe (NOT an acceptance criterion, NOT part of the instrument).

Question it answers: can THIS guest make ~7 GiB resident at all?  /proc/meminfo reports
MemTotal 15.6 GiB but MemAvailable ~6.6 GiB with ~8.7 GiB held by virtio_balloon
(feature bits STATS_VQ, DEFLATE_ON_OOM, REPORTING negotiated).  The Macaulay2 acceptance
invocation is expected to peak at 6.7-6.8 GiB resident, so whether the balloon deflates
under pressure decides whether A3 can be run at its declared magnitude.

Safety: the process marks ITSELF as the OOM killer's first victim (oom_score_adj 1000),
touches memory in 256 MiB steps, and releases everything and exits if MemAvailable falls
under --floor-mib.  No RLIMIT_AS is set.  Schedule is fixed; no randomness.
"""
import argparse, json, mmap, os, sys, time

def meminfo():
    d = {}
    for ln in open("/proc/meminfo"):
        k, v = ln.split(":")
        d[k] = int(v.split()[0])
    return d

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-mib", type=int, default=7680)
    ap.add_argument("--step-mib", type=int, default=256)
    ap.add_argument("--floor-mib", type=int, default=400)
    ap.add_argument("--hold-s", type=float, default=0.2)
    a = ap.parse_args()
    open("/proc/self/oom_score_adj", "w").write("1000\n")
    m0 = meminfo()
    log = {"schedule": vars(a), "oom_score_adj": 1000, "meminfo_start": {k: m0[k] for k in ("MemTotal", "MemFree", "MemAvailable", "Cached", "AnonPages")},
           "steps": [], "outcome": None}
    blocks = []
    touched = 0
    page = mmap.PAGESIZE
    try:
        while touched < a.target_mib:
            b = mmap.mmap(-1, a.step_mib << 20, flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
            for off in range(0, a.step_mib << 20, page):
                b[off] = 1
            blocks.append(b)
            touched += a.step_mib
            time.sleep(a.hold_s)
            m = meminfo()
            rss_kb = int(open("/proc/self/statm").read().split()[1]) * (page // 1024)
            used_unaccounted_kb = m["MemTotal"] - m["MemFree"] - m["Cached"] - m["Buffers"] - m["AnonPages"] - m["Slab"]
            step = {"touched_mib": touched, "self_rss_kb": rss_kb, "MemFree_kb": m["MemFree"],
                    "MemAvailable_kb": m["MemAvailable"], "Cached_kb": m["Cached"],
                    "unaccounted_kb_balloon_proxy": used_unaccounted_kb, "t": round(time.monotonic(), 3)}
            log["steps"].append(step)
            print(json.dumps(step), flush=True)
            if m["MemAvailable"] < (a.floor_mib << 10):
                log["outcome"] = f"STOPPED_AT_FLOOR: MemAvailable {m['MemAvailable']} kB < floor {a.floor_mib} MiB after {touched} MiB touched"
                break
        else:
            log["outcome"] = f"REACHED_TARGET: {touched} MiB resident with MemAvailable {meminfo()['MemAvailable']} kB remaining"
    finally:
        for b in blocks:
            b.close()
        log["meminfo_end_after_release"] = {k: v for k, v in meminfo().items() if k in ("MemTotal", "MemFree", "MemAvailable", "Cached", "AnonPages")}
        print(json.dumps({"outcome": log["outcome"], "end": log["meminfo_end_after_release"]}), flush=True)
        out = os.environ.get("PROBE_JSON")
        if out:
            open(out, "w").write(json.dumps(log, indent=1))

if __name__ == "__main__":
    main()
