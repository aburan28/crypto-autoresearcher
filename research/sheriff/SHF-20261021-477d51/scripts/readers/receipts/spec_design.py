#!/usr/bin/env python3
"""Check each frozen spec's arms are PROTOCOL.md's one-change design around the plan arm, and the
common workload/measurement settings (8 targets, seed 20261021, 3+1 rounds, alternate, L2, 1800 s).
(SHF-20261021-477d51 receipts reader)"""
import json, math, sys
B = sys.argv[1]
ok_all = True
for s in ["c24", "c28", "c30", "r24", "r26", "r28"]:
    sp = json.load(open(f"{B}/specs/{s}.json"))
    arms = {a["name"]: a for a in sp["arms"]}
    P = arms["plan"]["method"]["params"]
    N = int(P["factor_base"].split("size=")[1])
    def chg(**kw):
        d = dict(P); d.update(kw); return d
    expect = {
        "rho-neg": ("reference", "rho.negation", {}),
        "plan": ("candidate", "ic.pipeline", {"factor_base": f"prime-abscissa:size={N}", "oracle": "mitm-prime-blocked:m=2", "linalg": "incremental-gauss", "targets": "walk"}),
        "half-base": ("baseline", "ic.pipeline", chg(factor_base=f"prime-abscissa:size={math.ceil(N/2)}")),
        "double-base": ("baseline", "ic.pipeline", chg(factor_base=f"prime-abscissa:size={2*N}")),
        "rootfind": ("baseline", "ic.pipeline", chg(oracle="rootfind-subtract:m=2")),
        "full-rank": ("baseline", "ic.pipeline", chg(linalg="incremental-gauss-full-rank")),
        "random-targets": ("baseline", "ic.pipeline", chg(targets="random")),
        "plan-aa": ("control", "ic.pipeline", dict(P)),
    }
    res = [n for n, (role, mid, params) in expect.items()
           if not (n in arms and arms[n]["role"] == role and arms[n]["method"]["id"] == mid and arms[n]["method"].get("params", {}) == params)]
    w, m = sp["workloads"], sp["measurement"]
    common = (w["targets_per_curve"] == 8 and w["target_seed"] == 20261021 and m["rounds"] == 3 and m["warmup"] == 1
              and m["order"] == "alternate" and m["isolation_required"] == "L2" and m["timeout_seconds"] == 1800 and len(arms) == 8)
    ok = not res and common
    ok_all &= ok
    print(s, "N=%d" % N, "half=%s double=%s" % (arms["half-base"]["method"]["params"]["factor_base"].split("=")[1], arms["double-base"]["method"]["params"]["factor_base"].split("=")[1]), "arm_mismatches=%s" % res, "common_ok=%s" % common, "ok=%s" % ok)
print("all_ok", ok_all)
