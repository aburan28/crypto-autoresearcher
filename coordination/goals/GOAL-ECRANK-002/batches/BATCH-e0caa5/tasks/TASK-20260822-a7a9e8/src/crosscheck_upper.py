#!/usr/bin/env python3
"""Falsification cross-check for TASK-20260822-a7a9e8.

For the top curves, ask PARI's 2-descent (ellrank) for an UPPER bound r_high.
This is used ONLY as a falsification test: if r_high were strictly below the
number of points we certified independent, our independence claim would be
WRONG. The upper bound is never reported as a rank and never contributes to any
claim. An alarm timeout is an infrastructure outcome and decides nothing.

usage: crosscheck_upper.py <pool.json> <out.json> <min_rank> <alarm_s>
"""
import json, sys, time
import cypari
pari = cypari.pari

def main():
    pool = json.load(open(sys.argv[1])); minr = int(sys.argv[3]); al = int(sys.argv[4])
    res = []
    for c in pool["curves"]:
        if c["certified_rank"] < minr:
            continue
        ai = [int(z) for z in c["min_ainv"]]
        t0 = time.time()
        try:
            r = pari("iferr(alarm(%d,ellrank(ellinit(%s))),E,[-1,-1,0,[]])" % (al, str(ai)))
            rl, rh = int(r[0]), int(r[1])
            status = "timeout_or_error" if (rl == -1 and rh == -1) else "ok"
        except Exception as ex:
            rl, rh, status = None, None, "exception:" + repr(ex)[:120]
        e = dict(curve_id=c["curve_id"], certified_rank=c["certified_rank"],
                 pari_r_low=rl, pari_r_high=rh, status=status,
                 seconds=time.time() - t0,
                 contradicts_certified_rank=(status == "ok" and rh is not None
                                             and rh < c["certified_rank"]))
        res.append(e)
        print(e, flush=True)
    bad = [e for e in res if e["contradicts_certified_rank"]]
    json.dump(dict(note="upper bounds are a falsification test only; never a "
                        "reported rank. timeouts decide nothing.",
                   alarm_seconds=al, results=res,
                   contradictions=len(bad)),
              open(sys.argv[2], "w"), indent=1)
    print("checked=%d contradictions=%d timeouts=%d" % (
        len(res), len(bad), sum(1 for e in res if e["status"] != "ok")))

if __name__ == "__main__":
    main()
