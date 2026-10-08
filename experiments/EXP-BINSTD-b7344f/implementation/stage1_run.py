#!/usr/bin/env python3
"""Stage 1 for EXP-BINSTD-b7344f: W4 controlled-null CV on RC-1 (TASK-20261001-8c14b5).

Wraps EXP-CERTBIN-e94b27 closure (read-only import). Observations only.
certificate.kind: none for cost-shape; no CDCL / break / portfolio claim.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
CERT_IMPL = REPO / "experiments" / "EXP-CERTBIN-e94b27" / "impl"
SRC_RUN = REPO / "experiments" / "EXP-CERTBIN-4e92d7" / "runs" / "RUN-CERTBIN-3b7e05"
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(CERT_IMPL))

from runpack import (  # noqa: E402
    EXP_ID,
    TASK_ID,
    EXP_ROOT,
    dump_yaml,
    peak_rss_bytes,
    utc_now,
    write_run_package,
)

import closure as closure_mod  # noqa: E402
from closure import Closure, WatchdogExpired  # noqa: E402
from gf2n import TableField  # noqa: E402
from instances import eqs_of, load_source, select_sets, build_instances  # noqa: E402
from macaulay import NEQ, descended_E  # noqa: E402

RUN_UNSAT = "RUN-BINSTD-03a5cd"
RUN_SAT = "RUN-BINSTD-23a5c3"
RUN_RAND_V = "RUN-BINSTD-1c1589"
RUN_RAND_DENSE = "RUN-BINSTD-a67dbf"

OPCOUNT = {"n": 0}


def counting_echelon(M, C, keep_log=True):
    """Mirror of closure.echelon that counts int32 row-XOR ops (sum |X|)."""
    R, W = M.shape
    unused = np.ones(R, dtype=bool)
    ps, cs, Xs = [], [], []
    ONE = np.uint64(1)
    shifts = [np.uint64(b) for b in range(64)]
    for c in range(C):
        w = c >> 6
        col = ((M[:, w] >> shifts[c & 63]) & ONE).astype(bool)
        col &= unused
        idx = np.flatnonzero(col)
        if idx.size == 0:
            continue
        p = int(idx[0])
        X = idx[1:]
        if X.size:
            M[X, w:] ^= M[p, w:]
            OPCOUNT["n"] += int(X.size)  # one int32-logged XOR per target row
        unused[p] = False
        ps.append(p)
        cs.append(c)
        if keep_log:
            Xs.append(X.astype(np.int32))
    return (
        np.array(ps, dtype=np.int64),
        np.array(cs, dtype=np.int64),
        Xs if keep_log else None,
    )


def install_opcount_hook():
    closure_mod.echelon = counting_echelon


def cv(xs):
    if not xs:
        return float("nan")
    m = float(np.mean(xs))
    if m == 0:
        return float("nan")
    return float(np.std(xs, ddof=1) / m)


def max_over_median(xs):
    if not xs:
        return float("nan")
    med = float(np.median(xs))
    if med == 0:
        return float("nan")
    return float(np.max(xs) / med)


def hill_alpha(xs, k=None):
    """Hill tail index on upper order stats; returns None if undefined."""
    xs = np.asarray(sorted(xs), dtype=float)
    n = len(xs)
    if n < 10:
        return None
    if k is None:
        k = max(5, n // 10)
    k = min(k, n - 1)
    if k < 2:
        return None
    x_n_k = xs[n - k - 1]
    if x_n_k <= 0:
        return None
    top = xs[n - k :]
    if np.any(top <= 0):
        return None
    logs = np.log(top) - math.log(x_n_k)
    mean_log = float(np.mean(logs))
    if mean_log <= 0:
        return None
    return 1.0 / mean_log


def hill_bootstrap_ci(xs, n_boot=10000, seed=2026100101):
    rng = random.Random(seed)
    base = hill_alpha(xs)
    if base is None:
        return {"alpha": None, "ci_low": None, "ci_high": None, "n_boot": n_boot}
    boots = []
    n = len(xs)
    for _ in range(n_boot):
        sample = [xs[rng.randrange(n)] for _ in range(n)]
        a = hill_alpha(sample)
        if a is not None:
            boots.append(a)
    if len(boots) < 100:
        return {"alpha": base, "ci_low": None, "ci_high": None, "n_boot": len(boots)}
    boots.sort()
    lo = boots[int(0.025 * len(boots))]
    hi = boots[int(0.975 * len(boots)) - 1]
    return {"alpha": base, "ci_low": lo, "ci_high": hi, "n_boot": len(boots)}


def summarize(xs, infra_n, finished_n):
    return {
        "n_finished": finished_n,
        "n_infra_excluded": infra_n,
        "infra_exclusion_rate": infra_n / max(infra_n + finished_n, 1),
        "opcount_mean": float(np.mean(xs)) if xs else None,
        "opcount_median": float(np.median(xs)) if xs else None,
        "opcount_std": float(np.std(xs, ddof=1)) if len(xs) > 1 else None,
        "cv_per_attempt": cv(xs),
        "max_over_median": max_over_median(xs),
        "hill": hill_bootstrap_ci(xs),
        "wall_s_mean": None,  # filled by caller if available
    }


def run_w4_on_eqs(eqs, deadline_s=120):
    OPCOUNT["n"] = 0
    t0 = time.time()
    cl = Closure(nv=18, D=4, neq=NEQ)
    try:
        rec, _cert = cl.w_closure(eqs, want_cert=False, deadline_s=deadline_s)
        wall = time.time() - t0
        return {
            "ok": True,
            "opcount_int32": int(OPCOUNT["n"]),
            "wall_seconds": wall,
            "iterations_to_fixpoint": rec["iterations_to_fixpoint"],
            "final_dim": rec["final_dim"],
            "one": rec["one"],
            "infra": False,
        }
    except WatchdogExpired:
        return {
            "ok": False,
            "opcount_int32": int(OPCOUNT["n"]),
            "wall_seconds": time.time() - t0,
            "infra": True,
            "termination_reason": "watchdog",
        }


def load_unsat_and_sat(F, B):
    """All 386 archived unsat F-S3 D=4 + 100 archived sat (planted-set proxy).

    Equations rebuilt via descended_E(F, B, x_R) — same path as CERTBIN
    build_instances for F-S3 (targets jsonl has no E_hex).
    """
    import gzip

    by_idx = {}
    for line in gzip.open(SRC_RUN / "targets-F-S3.jsonl.gz", "rt"):
        r = json.loads(line)
        by_idx.setdefault(r["idx"], {})[r["D"]] = r
    unsat = []
    sat = []
    for idx, ds in sorted(by_idx.items()):
        if 4 not in ds:
            continue
        r4 = ds[4]
        if r4.get("degenerate"):
            continue
        E = descended_E(F, B, r4["x_R"])
        row = {
            "idx": idx,
            "x_R": r4["x_R"],
            "E": E,
            "stratum": r4["stratum"],
            "one_in_R": r4["one_in_R"],
        }
        if r4["stratum"] == "unsat":
            unsat.append(row)
        elif r4["stratum"] == "sat":
            sat.append(row)
    # HOLD-U asked 400 unsat; archive has 386 — use all, disclose shortfall
    sat100 = sat[:100]
    return unsat, sat100


def eqs_from_inst(inst):
    return eqs_of(inst["E"])


def random_dense_eqs(rng: random.Random, n_eq=NEQ, n_vars=18, dens=0.35):
    """Dense random multilinear system of matched (neq, nv) shape — control."""
    eqs = []
    for _ in range(n_eq):
        terms = []
        # constant + linears + some quadratics to mimic Semaev support size ~15
        if rng.random() < 0.5:
            terms.append(0)  # constant
        for i in range(n_vars):
            if rng.random() < dens:
                terms.append(1 << i)
        for _ in range(rng.randint(3, 8)):
            a, b = rng.sample(range(n_vars), 2)
            terms.append((1 << a) | (1 << b))
        # unique
        terms = sorted(set(terms))
        eqs.append(terms)
    return eqs


def measure_set(label, instances, eqs_fn, seed_tag):
    finished = []
    walls = []
    infra = []
    details = []
    for i, inst in enumerate(instances):
        eqs = eqs_fn(inst)
        r = run_w4_on_eqs(eqs)
        row = {"i": i, "key": inst.get("key", f"{label}:{i}"), **r}
        details.append(row)
        if r["infra"]:
            infra.append(row)
        elif r["ok"]:
            finished.append(r["opcount_int32"])
            walls.append(r["wall_seconds"])
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  [{label}] {i+1}/{len(instances)} finished={len(finished)} infra={len(infra)}", flush=True)
    summary = summarize(finished, len(infra), len(finished))
    summary["wall_s_mean"] = float(np.mean(walls)) if walls else None
    summary["set"] = label
    summary["seed_tag"] = seed_tag
    return summary, details, infra


def stage1():
    assert (EXP_ROOT / "stage0" / "v-beta-table.yaml").exists(), "Stage 0 must complete first"
    install_opcount_hook()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    started_all = utc_now()
    t_all = time.time()

    F = TableField()
    curve, p1, tg = load_source(str(SRC_RUN))
    B = curve["B"]
    unsat, sat100 = load_unsat_and_sat(F, B)
    print(f"Loaded unsat={len(unsat)} sat100={len(sat100)}", flush=True)

    # --- unsat ---
    s_unsat, d_unsat, i_unsat = measure_set(
        "unsat_archived",
        [{"key": f"U:{u['idx']}", **u} for u in unsat],
        eqs_from_inst,
        "archived-3b7e05",
    )
    write_run_package(
        RUN_UNSAT,
        stage=1,
        arm="unsat_archived",
        seed=None,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage1_run.py",
        parameters={
            "curve_id": "CERTBIN-RC-1",
            "n": 17,
            "l": 9,
            "n_requested": 400,
            "n_available_archived": len(unsat),
            "source_run": str(SRC_RUN),
        },
        metrics=s_unsat,
        valid=s_unsat["n_finished"] > 0 and s_unsat["infra_exclusion_rate"] < 1.0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({"summary": s_unsat, "n_details": len(d_unsat)}, indent=2),
        started_at=started_all,
        finished_at=utc_now(),
        wall_seconds=time.time() - t_all,
        certificate={"kind": "none", "verified": True, "note": "Cost-shape; certificate.kind none."},
    )

    # --- sat ---
    t_sat = time.time()
    s_sat, d_sat, i_sat = measure_set(
        "sat_archived_100",
        [{"key": f"S:{u['idx']}", **u} for u in sat100],
        eqs_from_inst,
        "archived-sat-first-100",
    )
    write_run_package(
        RUN_SAT,
        stage=1,
        arm="sat_archived_100",
        seed=2026100101,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage1_run.py",
        parameters={"curve_id": "CERTBIN-RC-1", "n_sat": len(sat100)},
        metrics=s_sat,
        valid=s_sat["n_finished"] > 0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({"summary": s_sat}, indent=2),
        started_at=utc_now(),
        finished_at=utc_now(),
        wall_seconds=time.time() - t_sat,
        certificate={"kind": "none", "verified": True, "note": "Cost-shape; certificate.kind none."},
    )

    # --- random-V control: archived N-AFF62 (matched-dim affine null) ---
    sets = select_sets(tg)
    build_instances(F, curve, p1, sets)  # mutates sets[*] with E / E_hex
    naff_inst = [{"key": inst["key"], "E": inst["E"]} for inst in sets["N-AFF62"]]

    t_rv = time.time()
    s_rv, d_rv, i_rv = measure_set(
        "random_V_N-AFF62",
        naff_inst,
        eqs_from_inst,
        "N-AFF62-control",
    )
    write_run_package(
        RUN_RAND_V,
        stage=1,
        arm="random_V_N-AFF62",
        seed=2026100102,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage1_run.py",
        parameters={"curve_id": "CERTBIN-RC-1", "control": "N-AFF62", "n": len(naff_inst)},
        metrics=s_rv,
        valid=s_rv["n_finished"] > 0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({"summary": s_rv}, indent=2),
        started_at=utc_now(),
        finished_at=utc_now(),
        wall_seconds=time.time() - t_rv,
        certificate={"kind": "none", "verified": True, "note": "Cost-shape control; certificate.kind none."},
    )

    # --- random-dense ---
    rng = random.Random(2026100103)
    dense_inst = [{"key": f"RD:{i}", "i": i} for i in range(100)]
    t_rd = time.time()
    s_rd, d_rd, i_rd = measure_set(
        "random_dense",
        dense_inst,
        lambda inst: random_dense_eqs(random.Random(2026100103 + inst["i"])),
        "random-dense-100",
    )
    write_run_package(
        RUN_RAND_DENSE,
        stage=1,
        arm="random_dense",
        seed=2026100103,
        command="python3 experiments/EXP-BINSTD-b7344f/implementation/stage1_run.py",
        parameters={"curve_id": "synthetic-random-dense", "n": 100, "neq": NEQ, "nv": 18},
        metrics=s_rd,
        valid=s_rd["n_finished"] > 0,
        invalid_reason=None,
        termination_reason="completed",
        stdout_text=json.dumps({"summary": s_rd}, indent=2),
        started_at=utc_now(),
        finished_at=utc_now(),
        wall_seconds=time.time() - t_rd,
        certificate={"kind": "none", "verified": True, "note": "Cost-shape control; certificate.kind none."},
    )

    all_infra = i_unsat + i_sat + i_rv + i_rd
    dump_yaml(
        EXP_ROOT / "stage1" / "cv-by-set.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "sets": {
                "unsat_archived": s_unsat,
                "sat_archived_100": s_sat,
                "random_V_N-AFF62": s_rv,
                "random_dense": s_rd,
            },
            "cv_null_threshold": 0.1,
            "cv_anomaly_threshold": 1.0,
            "disclosure": {
                "n_unsat_requested": 400,
                "n_unsat_available": len(unsat),
                "sat_source": "first 100 archived F-S3 sat (not freshly planted)",
                "IMP_no_cdcl": True,
            },
        },
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "controls-summary.yaml",
        {
            "experiment_id": EXP_ID,
            "random_V": s_rv,
            "random_dense": s_rd,
            "note": "N-AFF62 stands in for matched-dim random-V null from CERTBIN archive; random_dense is synthetic matched-shape GF(2).",
        },
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "infra-exclusions.yaml",
        {
            "experiment_id": EXP_ID,
            "n_infra": len(all_infra),
            "exclusions": [
                {"key": r.get("key"), "termination_reason": r.get("termination_reason"), "set": r.get("key", "").split(":")[0]}
                for r in all_infra
            ],
            "note": "Infra exclusions never folded into finished CV sample.",
        },
    )
    dump_yaml(
        EXP_ROOT / "stage1" / "cost-shape-summary.yaml",
        {
            "experiment_id": EXP_ID,
            "task_id": TASK_ID,
            "stage": 1,
            "primary_cv": {
                "unsat": s_unsat["cv_per_attempt"],
                "sat": s_sat["cv_per_attempt"],
            },
            "max_over_median": {
                "unsat": s_unsat["max_over_median"],
                "sat": s_sat["max_over_median"],
            },
            "hill": {
                "unsat": s_unsat["hill"],
                "sat": s_sat["hill"],
            },
            "controls_cv": {
                "random_V_N-AFF62": s_rv["cv_per_attempt"],
                "random_dense": s_rd["cv_per_attempt"],
            },
            "HEUR_H1_cv_lt_0_1": {
                "unsat": (s_unsat["cv_per_attempt"] is not None and s_unsat["cv_per_attempt"] < 0.1),
                "sat": (s_sat["cv_per_attempt"] is not None and s_sat["cv_per_attempt"] < 0.1),
            },
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_seconds_total": time.time() - t_all,
            "no_break_claim": True,
            "no_cdcl_claim": True,
            "controlled_null_only": True,
        },
    )
    print("Stage 1 complete", flush=True)
    return {
        "unsat": s_unsat,
        "sat": s_sat,
        "random_V": s_rv,
        "random_dense": s_rd,
    }


if __name__ == "__main__":
    stage1()
