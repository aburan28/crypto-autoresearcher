#!/usr/bin/env python3
"""Deterministic trial-plan generator for EXP-MONO-1a1be2 (TASK-20261029-a97206, IM-6).

Derives from the specification's rules every cell, curve, base seed, tuple seed, target seed, the
arm-C field size q_n and sample size s_n, and writes the preview trial plan with each instance's identity
fields (q, n, g, a, b, N, t2, B, |X|, seed). The identity fields are inputs of the contract, not outcomes;
no count of any convention, coverage, ratio, split frequency or rule agreement is computed here.

Point counts: exhaustive (compiled kernel) when Q < 2^27, baby-step giant-step on the Hasse interval
otherwise; on every curve with Q < 2^27 the BSGS count is also computed and must agree (recorded).

Cell ids (an implementation choice; the specification leaves the format open):
  A  : A-n<n>-q<q>-c<i>          (arm A, n = 1 anchors included)
  B1 : B1-n<n>-q<q>-c<i>         (generic tuples, second q rung)
  B2 : B2-n<n>-c<i>              (factor-base locus; two instances, first and second q rung)
  C  : C-n<n>-q<q>-c<i>
Curve seed strings follow the specification exactly ("f15270|<arm>|<n>|<q>|<i>", arm in A, B, C; arm B
instances reuse the arm-A curve of the same (n, q), i.e. the seed string with arm "A").
Replicates: 0 for the primary draw, 1 for the A/A re-draws (C-aa-baseseed on every arm-A cell,
C-aa-tupleseed on curve index 0 of each B1 (n, q)).

Usage: make_trial_plan.py [--out PATH] [--check]    (default PATH: ../implementation/trial-plan.preview.json)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from decimal import Decimal, getcontext

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import counters  # noqa: E402
import curves  # noqa: E402
import fqn  # noqa: E402

EXP_ID = "EXP-MONO-1a1be2"

ARM_A_LADDER = {1: [61, 251], 2: [61, 251, 1021, 4093], 3: [17, 41, 101, 251], 4: [11, 23, 53, 101],
                5: [7, 11, 17, 29]}
CURVES_PER_CELL = 3
B1_TUPLES = 10 ** 6
B1_SUBSAMPLE_FRACTION = 0.01
B2_MAX_TUPLES = 10 ** 4
ARM_C_NS = [2, 3, 4, 5, 6, 7]
ARM_C_MIN_Q_POWER = 2 ** 30
EXPECTED_QN = {2: 32771, 3: 1031, 4: 191, 5: 67, 6: 37, 7: 23}
SAMPLE_REL_SE = Decimal("0.03")


def contract_cells_qn():
    """The set of (q, n) pairs of arm-A (and hence arm-B) cells; used by the launcher to keep KAT cells disjoint."""
    return {(q, n) for n, qs in ARM_A_LADDER.items() for q in qs}


def q_rule(n: int) -> int:
    """Least prime p > 3 with p^n >= 2^30."""
    p = 3
    while True:
        p = fqn.next_prime_above(p)
        if p > 3 and p ** n >= ARM_C_MIN_Q_POWER:
            return p


def sample_size_rule(n: int) -> int:
    """s_n = ceil((1 - c) / (c * 0.03^2)), c = 1 - exp(-lambda_nominal), lambda_nominal = 1/n! (50-digit decimals)."""
    getcontext().prec = 60
    lam = Decimal(1) / Decimal(math.factorial(n))
    e = (-lam).exp()
    c = 1 - e
    val = (1 - c) / (c * SAMPLE_REL_SE * SAMPLE_REL_SE)
    return int(val.to_integral_value(rounding="ROUND_CEILING"))


def curve_seed(arm: str, n: int, q: int, i: int) -> str:
    return f"f15270|{arm}|{n}|{q}|{i}"


def base_seed(cell_id: str, role: str, replicate: int) -> str:
    return f"f15270|base|{cell_id}|{role}|{replicate}"


def tuple_seed(cell_id: str, replicate: int) -> str:
    return f"f15270|tuples|{cell_id}|{replicate}"


def target_seed(cell_id: str) -> str:
    return f"f15270|targets|{cell_id}"


def _seed_record(s: str) -> dict:
    return {"seed_string": s, "seed_int": str(curves.seed_int(s))}


class InstanceBuilder:
    """Builds and caches (field, curve, identity fields) per (arm-label-of-seed, n, q, i)."""

    def __init__(self, kernel):
        self.kernel = kernel
        self.cache = {}

    def get(self, arm: str, n: int, q: int, i: int):
        key = (arm, n, q, i)
        if key in self.cache:
            return self.cache[key]
        F = fqn.FQ(q, n)
        E, info = curves.generate_curve(F, curve_seed(arm, n, q, i))
        D, X, t2 = E.factor_base()
        N_exh = N_bsgs = None
        if F.Q < 2 ** 27:
            N_exh = self.kernel.count_points(E)
            N_bsgs, used = E.count_points_bsgs()
            if N_exh != N_bsgs:
                raise RuntimeError(f"point-count disagreement at {key}: exhaustive {N_exh} vs BSGS {N_bsgs}")
            N, method = N_exh, "exhaustive_kernel"
        else:
            N, used = E.count_points_bsgs()
            N_bsgs, method = N, "bsgs"
        ident = {"q": q, "n": n, "g": list(F.g), "a": list(E.a), "b": list(E.b), "N": N,
                 "N_method": method, "N_exhaustive": N_exh, "N_bsgs": N_bsgs, "t2": t2, "B": len(D),
                 "size_X": len(X), "two_torsion_points_over_FQ": len(E.two_torsion_roots()),
                 "Q": F.Q, "repeat_dominated_flag": len(D) < n * n, "curve_seed": _seed_record(curve_seed(arm, n, q, i)),
                 "curve_generation": {k: info[k] for k in ("attempts", "rejected_singular", "rejected_j_in_Fq", "generator")}}
        self.cache[key] = ident
        return ident


def build_plan(kernel, builder=None) -> dict:
    ib = builder or InstanceBuilder(kernel)
    cells = []
    # ---- arm A
    for n, qs in ARM_A_LADDER.items():
        for q in qs:
            for i in range(CURVES_PER_CELL):
                cid = f"A-n{n}-q{q}-c{i}"
                ident = ib.get("A", n, q, i)
                cells.append({
                    "cell_id": cid, "arm": "A", "n": n, "q": q, "curve_index": i, "tuple_size_m": n,
                    "anchor": n == 1, "identity": ident,
                    "base_roles": {
                        "line": None,
                        "matched_random": _seed_record(base_seed(cid, "random", 0)),
                        "half_twin": _seed_record(base_seed(cid, "twin", 0)),
                        "matched_random_reseeded_aa": _seed_record(base_seed(cid, "random", 1)),
                    },
                    "conventions": ["A", "M", "S", "X"], "targets": "all N"})
    # ---- arm B1: second rung
    for n in (2, 3, 4, 5):
        q = ARM_A_LADDER[n][1]
        for i in range(CURVES_PER_CELL):
            cid = f"B1-n{n}-q{q}-c{i}"
            cell = {"cell_id": cid, "arm": "B1", "n": n, "q": q, "curve_index": i, "tuple_size_m": n,
                    "identity": ib.get("A", n, q, i), "tuples": B1_TUPLES,
                    "group_law_subsample_fraction": B1_SUBSAMPLE_FRACTION,
                    "tuple_seed": _seed_record(tuple_seed(cid, 0))}
            if i == 0:
                cell["tuple_seed_aa"] = _seed_record(tuple_seed(cid, 1))
            cells.append(cell)
    # ---- arm B2: first and second rung, one cell per (n, curve)
    for n in (2, 3, 4, 5):
        for i in range(CURVES_PER_CELL):
            cid = f"B2-n{n}-c{i}"
            inst = []
            for rung in (0, 1):
                q = ARM_A_LADDER[n][rung]
                inst.append({"rung": rung + 1, "q": q, "identity": ib.get("A", n, q, i)})
            cells.append({"cell_id": cid, "arm": "B2", "n": n, "curve_index": i, "tuple_size_m": n,
                          "instances": inst, "max_tuples_per_instance": B2_MAX_TUPLES,
                          "tuples_rule": "unordered n-subsets of distinct elements of X: all when C(|X|,n) <= max, else max random subsets",
                          "tuple_seed": _seed_record(tuple_seed(cid, 0)),
                          "group_law_check": "all B2 tuples"})
    # ---- arm C
    qn, sn = {}, {}
    for n in ARM_C_NS:
        q = q_rule(n)
        s = sample_size_rule(n)
        qn[str(n)], sn[str(n)] = q, s
        for i in range(CURVES_PER_CELL):
            cid = f"C-n{n}-q{q}-c{i}"
            cells.append({"cell_id": cid, "arm": "C", "n": n, "q": q, "curve_index": i, "tuple_size_m": n,
                          "identity": ib.get("C", n, q, i), "sample_size_s": s,
                          "base_roles": {"line": None,
                                         "matched_random": _seed_record(base_seed(cid, "random", 0))},
                          "target_seed": _seed_record(target_seed(cid)),
                          "multiset_count": math.comb(ib.get("C", n, q, i)["B"] + n - 1, n)})
    counts = {a: sum(1 for c in cells if c["arm"] == a) for a in ("A", "B1", "B2", "C")}
    plan = {
        "plan_version": 1, "experiment_id": EXP_ID,
        "note": "Preview trial plan generated by code/make_trial_plan.py. Identity fields are inputs, not outcomes.",
        "rules": {
            "curve_seed": "f15270|<arm>|<n>|<q>|<curve_index>; PCG64(int(sha256(utf8)[:16] big-endian))",
            "base_seed": "f15270|base|<cell_id>|<role>|<replicate>", "tuple_seed": "f15270|tuples|<cell_id>|<replicate>",
            "target_seed": "f15270|targets|<cell_id>",
            "q_rule": "least prime p > 3 with p^n >= 2^30", "sample_size_rule": "ceil((1-c)/(c*0.03^2)), c = 1-exp(-1/n!)",
            "curve_draw": "rng.integers(0, q, size=2n): a then b, constant term first; redraw on rejection",
        },
        "arm_c_q_n": qn, "arm_c_q_n_expected_by_specification": {str(k): v for k, v in EXPECTED_QN.items()},
        "arm_c_q_n_matches_expected": {str(k): qn[str(k)] == v for k, v in EXPECTED_QN.items()},
        "arm_c_s_n": sn,
        "cell_counts": counts, "cell_count_total": len(cells), "cells": cells,
    }
    return plan


def dumps(plan: dict) -> str:
    return json.dumps(plan, indent=1, sort_keys=True) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    default_out = os.path.join(HERE, "..", "implementation", "trial-plan.preview.json")
    ap.add_argument("--out", default=default_out)
    ap.add_argument("--check", action="store_true", help="regenerate and compare with the existing file")
    args = ap.parse_args(argv)
    tmp = tempfile.mkdtemp(prefix="mono1a1be2-plan-")
    try:
        kernel = counters.Kernel(counters.build_kernel(tmp))
        text = dumps(build_plan(kernel))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    out = os.path.abspath(args.out)
    if args.check:
        with open(out) as fh:
            same = fh.read() == text
        print("IDENTICAL" if same else "DIFFERENT")
        return 0 if same else 1
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(text)
    print(f"wrote {out} ({len(text)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
