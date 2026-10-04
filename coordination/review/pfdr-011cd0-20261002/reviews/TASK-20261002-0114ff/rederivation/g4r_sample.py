#!/usr/bin/env python3
"""J1 G4-R sample, fixed by a declared rule and seed BEFORE any row is verified.

TASK-20261002-0114ff. Reads ONLY the two jobs-spec.json files (instance keys).
Rule:
  U12 = R12 expected keys with curve % 10 == 0 (instances whose bases are
        written, --bases-sample-mod 10); U13 = the same for R13.
  Sample = every U13 key (all SS instances with written bases)
         + every R12 known_log key in U12
         + from every other R12 stratum (m, arm, bits): ceil(0.2 * |stratum|)
           keys drawn by random.Random("G4-R|TASK-20261002-0114ff|<m>|<arm>|<bits>")
           .sample(sorted stratum keys, k).
Every harvested row of every sampled instance is verified (g4r_verify.py).
Writes the sample to OUT_JSON with its sha256-able content.
Standard library only.
"""
import json
import math
import random
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
R = WT + "/experiments/EXP-PFDR-011cd0/runs/"


def keys(run):
    js = json.load(open(R + run + "/attempt-1/jobs-spec.json"))
    out = []
    for j in js["jobs"]:
        for k in j["expected_keys"]:
            out.append(tuple(k))
    return out


def main():
    k12 = [k for k in keys("RUN-PFDR-011cd0-table") if k[1] % 10 == 0]
    k13 = [k for k in keys("RUN-PFDR-011cd0-search") if k[1] % 10 == 0]
    sample = [list(k) + ["R13"] for k in sorted(k13)]
    strata = {}
    for k in k12:
        if k[3] == "known_log":
            sample.append(list(k) + ["R12"])
            continue
        strata.setdefault((k[2], k[3], k[0]), []).append(k)
    for (m, arm, bits) in sorted(strata):
        ks = sorted(strata[(m, arm, bits)])
        n = math.ceil(0.2 * len(ks))
        rng = random.Random(f"G4-R|TASK-20261002-0114ff|{m}|{arm}|{bits}")
        for k in sorted(rng.sample(ks, n)):
            sample.append(list(k) + ["R12"])
    out = {"rule": __doc__, "U12": len(k12), "U13": len(k13), "sample_size": len(sample),
           "sample_R12": sum(1 for s in sample if s[-1] == "R12"),
           "sample_R13": sum(1 for s in sample if s[-1] == "R13"), "sample": sample}
    json.dump(out, open(sys.argv[1], "w"), indent=0)
    print({k: v for k, v in out.items() if k not in ("sample", "rule")})


if __name__ == "__main__":
    main()
