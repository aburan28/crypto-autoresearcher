#!/usr/bin/env python3
"""Diagnostic for the analyze-main / analyze-final replay mismatch. Read-only; writes nothing.

This is NOT the blind re-derivation (that is blind_rederive.py). It deliberately imports the
producer's bound run.py and calls analyze_records() in-process on the RECORDED input files, under
controlled perturbations, to locate the cause of the ulp-level differences:

  native      : run.py as is, under whatever interpreter runs this script
  naive-sum   : run.py with its module-global `sum` replaced by a strict left-to-right fold
                (functools.reduce(operator.add)), i.e. the builtin float sum() of CPython <= 3.11
  neumaier    : run.py with `sum` replaced by a pure-Python Neumaier compensated sum, i.e. the
                builtin float sum() of CPython >= 3.12 (gh-100425)
  shuffle     : native, with the main jobs records shuffled (fixed seed) before analysis, to test
                sensitivity to jobs-record order
  sorted      : native, with the main jobs records sorted by (cell, c)

It prints, per stage (main, final), the sha256 of the bytes run.py would write
(json.dump(indent=1, sort_keys=True) + newline) and whether they equal the recorded file and the
audit replay file, plus calibration mean/sd.

Run with -B so no __pycache__ is written into the bound implementation directory:
  python3.X -B -I cause_probe.py <mode>
"""
import functools
import hashlib
import json
import operator
import os
import random
import sys

EXP_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
IMPL = os.path.join(EXP_DIR, "implementation")
RUNS = os.path.join(EXP_DIR, "runs")
REPLAY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "replay")
sys.dont_write_bytecode = True
sys.path.insert(0, IMPL)
import run  # noqa: E402  (the bound producer driver; imported only for this diagnostic)

_builtin_sum = sum


def naive_sum(it, start=0):
    return functools.reduce(operator.add, it, start)


def neumaier_sum(it, start=0):
    """Pure-Python model of CPython 3.12+ builtin sum(): exact int prefix, then Neumaier on floats."""
    it = iter(it)
    total = start
    for x in it:  # int fast path
        if isinstance(x, int) and isinstance(total, int):
            total += x
            continue
        s, c = float(total), 0.0
        x = float(x)
        t = s + x
        c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
        s = t
        for x in it:
            x = float(x)
            t = s + x
            c += (s - t) + x if abs(s) >= abs(x) else (x - t) + s
            s = t
        return s + c if c else s
    return total


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main():
    mode = sys.argv[1]
    if mode == "naive-sum":
        run.sum = naive_sum
    elif mode == "neumaier":
        run.sum = neumaier_sum
    design = json.load(open(os.path.join(RUNS, "RUN-PFDR-e44a19", "design.json")))["toy_cells"]
    main_recs = run.load_jsonl(os.path.join(RUNS, "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl"))
    rep_path = os.path.join(RUNS, "RUN-PFDR-cd03e2", "toy-rep-jobs.jsonl")
    rep_recs = run.load_jsonl(rep_path) if os.path.exists(rep_path) else None
    if mode == "shuffle":
        random.Random(20261029).shuffle(main_recs)
    elif mode == "sorted":
        main_recs.sort(key=lambda r: (r["cell"], r["c"]))
    out = {"python": sys.version.split()[0], "mode": mode}
    for stage, rid, fn, rep in (("main", "RUN-PFDR-243425", "analysis-main.json", None),
                                ("final", "RUN-PFDR-089edc", "analysis.json", rep_recs)):
        an = run.analyze_records(design, main_recs, rep, stage)
        b = (json.dumps(an, indent=1, sort_keys=True) + "\n").encode()
        rec = open(os.path.join(RUNS, rid, fn), "rb").read()
        rpl = open(os.path.join(REPLAY, rid, fn), "rb").read()
        out[stage] = {"sha256": sha(b), "equals_recorded": b == rec, "equals_replay": b == rpl,
                      "calibration": an["calibration"], "outcome": an["outcome"],
                      "headline": an["headline"], "flagged_cells": an["flagged_cells"]}
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
