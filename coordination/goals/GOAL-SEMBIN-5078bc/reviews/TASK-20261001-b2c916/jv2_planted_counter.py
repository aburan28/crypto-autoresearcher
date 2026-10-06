#!/usr/bin/env python3
"""TASK-20261001-b2c916 / JV-2 side control: PLANTED-CELL positive control for the
UNGATED counting code (run_v2.DataPass), which C-IMPL-GATE never exercises.

The committed driver is wrapped so that a known set of cells reports
TOTAL = VOW - 0.5 (sub-rho, but above the C-3 threshold N/2 - 2, so the flag
should not fire on them). One planted cell is OUT of domain (CALLS < 0) and must
NOT be counted. The committed DataPass is then run over the committed sweep, and
its per-(n, model, B) sub-rho counts at bound n are compared with the plant.

A pass means the counter can see a sub-rho cell when one exists; it says nothing
about whether any exist in the real model.
"""
from __future__ import annotations

import sys as _sys
_sys.dont_write_bytecode = True  # never write __pycache__ into committed code dirs

import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
CODE = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c", "code", "v2")
RUN = os.path.join(REPO, "experiments", "EXP-SEMBIN-04ec3c", "runs", "RUN-SEMBIN-be48b7")
DIG = json.load(open(os.path.join(RUN, "artifact-digests.json")))


def load(name):
    p = os.path.join(CODE, name)
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != DIG["code_v2"][os.path.relpath(p, REPO)]:
        raise SystemExit(f"{name}: hash mismatch")
    sys.path.insert(0, CODE)
    spec = importlib.util.spec_from_file_location(name[:-3] + "_pc", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    drv = load("model_v2.py")
    rv = load("run_v2.py")
    raw = json.load(open(os.path.join(RUN, "raw-result.json")))
    drv.set_subgroup_order_log2(raw["inputs"]["subgroup_order_131"]["log2_r"])
    # (n, model, B, m, d); all in-domain except the last
    plant = [(97, "MITM", None, 6, 21.0), (131, "ENUM", None, 2, 30.0), (131, "MITM_CAPPED", 60.0, 8, 15.0),
             (131, "MITM_CAPPED", None, 8, 20.5), (233, "MITM", None, 10, 28.0), (571, "MITM_CAPPED", 30.0, 4, 100.0),
             (163, "MITM", None, 16, 60.0)]
    orig = drv.evaluate
    planted_in, planted_ood = [], []
    for (n, model, B, m, d) in plant:
        c = orig(n, model, m, d, B)
        (planted_ood if c[2] < 0 else planted_in).append((n, model, B, m, d))

    def evaluate(n, model, m, d, B):
        c = orig(n, model, m, d, B)
        if (n, model, B, m, d) in plant:
            c = list(c)
            c[6] = drv.vow_column(n) - 0.5
            c = tuple(c)
        return c

    drv.evaluate = evaluate
    dp = rv.DataPass(drv)
    drv.sweep(drv.DEGREES, range(2, 17), drv.MODELS, dp.visit)
    # primary models only: FREE is a control with an oracle charged at zero and has sub-rho cells by design
    got = {k: v["subrho_vs_VOW"] for k, v in dp.counts.items()
           if k[3] == "n" and k[1] in drv.PRIMARY_MODELS and v["subrho_vs_VOW"]}
    want = {}
    for (n, model, B, m, d) in planted_in:
        k = (n, model, "unlimited" if B is None else f"{int(B)}", "n")
        want[k] = want.get(k, 0) + 1
    pub = {k: v["subrho_vs_PUB"] for k, v in dp.counts.items()
           if k[0] == 131 and k[3] == "n" and k[1] in drv.PRIMARY_MODELS and v["subrho_vs_PUB"]}
    out = {"planted_in_domain": [list(map(str, p)) for p in planted_in],
           "planted_out_of_domain": [list(map(str, p)) for p in planted_ood],
           "counted": {"|".join(map(str, k)): v for k, v in got.items()},
           "expected": {"|".join(map(str, k)): v for k, v in want.items()},
           "pub_counted_at_131": {"|".join(map(str, k)): v for k, v in pub.items()},
           "C3_fired": dp.flag["fired_in_domain"] + dp.flag["fired_out_of_domain"],
           "passed": got == want and dp.flag["fired_in_domain"] + dp.flag["fired_out_of_domain"] == 0}
    with open(os.path.join(HERE, "jv2_out", "jv2_planted_counter.json"), "w") as fh:
        fh.write(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
