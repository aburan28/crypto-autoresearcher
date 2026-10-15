#!/usr/bin/env python3
"""Single entrypoint for the eight trials of EXP-CMFB-cea1d2.

    python3 experiments/EXP-CMFB-cea1d2/implementation/driver.py --trial <trial-id> --run-dir {run_dir}

Every trial recomputes the whole instance list from the seeds (curves.build_instances), requires its
sha256 to equal the one recorded by t1-inventory in the sibling run directory
(<run_dir>/../RUN-CMFB-2373be), writes manifest.yaml and raw-result.json, and exits 0 even when a
control gate fails (the failure is recorded; check.py turns it into a nonzero checker exit, which the
supervisor reads as invalid_output and which blocks the dependent trials).

--dev-limit N (development only) shrinks K and marks the output official = false; check.py refuses it.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"  # one thread per process: the address-space guard counts thread arenas

import argparse
import json
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

import numpy as np  # noqa: E402

import analyze  # noqa: E402
import count  # noqa: E402
import curves  # noqa: E402
from crypto_autoresearcher import parallel  # noqa: E402

HIST_BASES = ("member", "rand1", "rand2")


def cap_address_space(memory_mb: int) -> None:
    """Per-process RLIMIT_AS cap (the supervisor sets the same value from the plan's memory_mb)."""
    cap = int(memory_mb) * 1024 * 1024
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    if soft == resource.RLIM_INFINITY or soft > cap:
        resource.setrlimit(resource.RLIMIT_AS, (cap, hard if hard != resource.RLIM_INFINITY and hard < cap else cap))


def worker_rss() -> int:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


# --------------------------------------------------------------------------- member task
def member_task(index: int, item: dict) -> tuple[dict, dict]:
    """Everything measured for one member (or one planted-control curve): a pure function of
    (index, item); returns (deterministic record, timing record)."""
    inst, K = item["inst"], item["K"]
    p, N, A, Bc = inst["p"], inst["N"], inst["A"], inst["B"]
    cell, arm, idx = inst["cell"], inst["arm"], inst["index"]
    planted = arm == "N-B-ctrl"
    B = count.base_size(N)
    size = B + 1 if planted else B
    rec = {k: inst[k] for k in ("arm", "stratum", "cell", "index", "p", "N", "A", "B", "d", "twisted", "t", "a", "b")}
    rec.update({"p_mod_120": p % 120, "base_size": B, "T": count.binom3(B),
                "base_kind": "planted" if planted else "small_x", "member_base_size": size,
                "member_T": count.binom3(size)})
    t_start = time.perf_counter()
    rec["validity"] = curves.verify_instance(inst)
    pts, W = curves.small_x_base(A, Bc, p, size)
    t0 = time.perf_counter()
    labels = curves.bsgs_labels(pts, A, p, N)
    bsgs_s = time.perf_counter() - t0
    rec["labels"] = labels
    rec["label_check"] = curves.verify_labels(pts, labels, A, p, N, curves.rng(
        curves.SEEDS["labels_points"], cell, arm, idx, curves.STREAM_TRIPLES))
    rec["distinct_classes"] = len({min(x, N - x) for x in labels}) == size
    rec["window_W"] = W
    seen = np.zeros(N, dtype=np.uint8)
    count_s, triples = 0.0, 0
    loop_failures = 0

    t0 = time.perf_counter()
    cov, enum = count.count_coverage(labels, N, seen)
    count_s += time.perf_counter() - t0
    triples += enum
    loop_failures += int(enum != rec["member_T"])
    rec["member_seen"] = cov
    hist_records, hist_failures = [], 0

    def recount(name: str, lbls, expected_seen: int, expected_total: int) -> None:
        nonlocal hist_failures
        h = count.histogram(lbls, N)
        h.pop("vector")
        h.update({"base": name, "seen": expected_seen})
        h["ok"] = h["total"] == expected_total and h["nonzero"] == expected_seen
        hist_failures += int(not h["ok"])
        hist_records.append(h)

    if item.get("hist", True):
        recount("member", labels, cov, rec["member_T"])
    random_seen, distinct_failures = [], 0
    for k in range(1, K + 1):
        lbls = count.random_labels(N, B, curves.rng(curves.SEEDS["random_bases"], cell, arm, idx, k + 1))
        distinct_failures += int(len({min(x, N - x) for x in lbls}) != B)
        t0 = time.perf_counter()
        c, e = count.count_coverage(lbls, N, seen)
        count_s += time.perf_counter() - t0
        triples += e
        loop_failures += int(e != rec["T"])
        random_seen.append(c)
        if item.get("hist", True) and k in (1, 2):
            recount(f"rand{k}", lbls, c, rec["T"])
    rec["random_seen"] = random_seen
    rec["random_distinct_failures"] = distinct_failures
    rec["hist"] = hist_records
    rec["m0"] = {"bases": K + 1, "loop_failures": loop_failures,
                 "hist_checked": len(hist_records), "hist_failures": hist_failures}
    S = min(curves.S_M2_CAP, p // 2)
    rec["scan"] = curves.scan_stats(A, Bc, p, S)
    timing = {"bsgs_seconds": bsgs_s, "count_seconds": count_s, "triples": triples,
              "member_seconds": time.perf_counter() - t_start, "worker_rss_bytes": worker_rss()}
    return rec, timing


def member_task_det(index: int, item: dict) -> dict:
    return member_task(index, item)[0]


def run_members(items: list[dict], workers: int) -> tuple[list[dict], list[dict]]:
    """Fan the members over `workers` processes; heaviest first, results restored to input order."""
    order = sorted(range(len(items)), key=lambda i: -items[i]["inst"]["N"])
    out = parallel.sharded_map(member_task, [items[i] for i in order], workers=workers, chunk_size=1)
    recs, tims = [None] * len(items), [None] * len(items)
    for pos, i in enumerate(order):
        recs[i], tims[i] = out[pos]
    return recs, tims


# ------------------------------------------------------------------------ trial bodies
def sibling_run(run_dir: Path, trial_id: str) -> Path:
    return run_dir.parent / curves.TRIALS[trial_id][0]


def t1_reference(run_dir: Path) -> dict | None:
    f = sibling_run(run_dir, "t1-inventory") / "raw-result.json"
    return json.loads(f.read_text()) if f.is_file() else None


def build(run_dir: Path, trial_id: str) -> dict:
    inv = curves.build_instances()
    if trial_id != "t1-inventory":
        ref = t1_reference(run_dir)
        if ref is not None and ref["instance_list_sha256"] != inv["sha256"]:
            raise SystemExit("instance-list sha256 differs from t1-inventory (I8): refusing to run")
        inv["t1_sha_checked"] = ref is not None
    return inv


def trial_t1(inv: dict, args) -> dict:
    fam = curves.fam_sieve()
    counts = inv["counts"]
    octaves: dict[str, int] = {}
    for m in fam:
        if curves.cell_of(m["p"]) is not None:
            octaves[str(m["t"].bit_length() - 1)] = octaves.get(str(m["t"].bit_length() - 1), 0) + 1
    vprime = {c: sum(1 for m in curves.fam_members_for(fam, c) if curves.is_prime(m["v"]))
              for c in ("C16", "C20", "C24")}
    bh = {}
    for c in ("C16", "C20", "C24"):
        lo, hi = curves.CELL_EDGES[c]
        e = curves.bateman_horn_cell(lo, hi)
        bh[c] = {"expected": e["expected"], "c_odd": e["c_odd"], "exact": counts[c],
                 "ratio_exact_to_expected": counts[c] / e["expected"],
                 "within_factor_2": 0.5 <= counts[c] / e["expected"] <= 2.0}
    instances = []
    for i in inv["instances"]:
        v = curves.verify_instance(i)
        instances.append({**i, "p_mod_120": i["p"] % 120, "validity": v})
    return {"inventory": {"fam_sieve_t_max": curves.T_MAX_SIEVE, "fam_members": fam, "counts": counts,
                          "per_octave_of_t": octaves, "t_ranges": curves.t_ranges(), "v_prime_counts": vprime, "bateman_horn": bh,
                          "pooling": inv["plan"]},
            "instances": instances}


def spread_members(instances: list[dict], arm: str, cell: str, k: int) -> list[dict]:
    mem = [i for i in instances if i["arm"] == arm and i["cell"] == cell]
    return [mem[j] for j in curves.spread(len(mem), k)]


def trial_t2(inv: dict, args) -> dict:
    ins = [i for i in inv["instances"] if i["arm"] != "N-B-ctrl"]
    K_det = 20
    controls: dict = {}
    # 1. brute-force counter check (60 cases, seed 7009)
    cases, failures = [], 0
    for N in (211, 307, 401, 503, 1009):
        for B in (5, 8, 13, 20):
            for kind_id, kind in enumerate(("random_classes", "arithmetic_progression", "random_coset")):
                g = np.random.Generator(np.random.PCG64(np.random.SeedSequence([curves.SEEDS["brute"] + curves.SEED_OFFSET, N, B, kind_id, 0])))
                if kind == "random_classes":
                    lab = count.random_labels(N, B, g)
                elif kind == "arithmetic_progression":
                    lab = list(range(1, B + 1))
                else:
                    a = int(g.integers(2, N))
                    lab = [a * i % N for i in range(1, B + 1)]
                brute = count.brute_force_counts(lab, N)
                h = count.histogram(lab, N)
                cov, enum = count.count_coverage(lab, N)
                ok = (bool(np.array_equal(h["vector"], brute)) and cov == int(np.count_nonzero(brute))
                      and enum == count.binom3(B) and h["nonzero"] == cov and h["total"] == count.binom3(B))
                failures += int(not ok)
                cases.append({"N": N, "B": B, "kind": kind, "labels": lab, "coverage": cov, "ok": ok})
    controls["brute_force"] = {"cases": len(cases), "failures": failures, "detail": cases}
    # 2. curve / twist / trace / formula validity for every instance (incl. controls)
    bad = [{"arm": i["arm"], "cell": i["cell"], "index": i["index"]} for i in inv["instances"]
           if not curves.verify_instance(i)["ok"]]
    controls["instances"] = {"checked": len(inv["instances"]), "failures": bad}
    # 3 + 4. labelling check (4 per arm per cell) and M0 histogram recount (2 per arm per cell)
    lab_items, rec_items = [], []
    for cell in inv["plan"]["cells"]:
        for arm in ("FAM", "N-A", "N-B"):
            lab_items += spread_members(inv["instances"], arm, cell, 4)
            rec_items += spread_members(inv["instances"], arm, cell, 2)
    lab_out = []
    for i in lab_items:
        B = count.base_size(i["N"])
        pts, _ = curves.small_x_base(i["A"], i["B"], i["p"], B)
        labels = curves.bsgs_labels(pts, i["A"], i["p"], i["N"])
        lab_out.append({"arm": i["arm"], "cell": i["cell"], "index": i["index"],
                        "check": curves.verify_labels(pts, labels, i["A"], i["p"], i["N"], curves.rng(
                            curves.SEEDS["labels_points"], i["cell"], i["arm"], i["index"], curves.STREAM_TRIPLES))})
    controls["labelling"] = lab_out
    recs, tims = run_members([{"inst": i, "K": 2, "hist": True} for i in rec_items], args.workers)
    controls["m0_recount"] = [{"arm": r["arm"], "cell": r["cell"], "index": r["index"], "m0": r["m0"],
                               "hist": r["hist"], "member_seen": r["member_seen"], "random_seen": r["random_seen"]}
                              for r in recs]
    controls["recount_timing"] = tims
    # 5. qr_window positive and negative control, per instance (pooled per arm and cell by analysis/check)
    scans = []
    for i in ins:
        S = min(curves.S_M2_CAP, i["p"] // 2)
        scans.append({"arm": i["arm"], "cell": i["cell"], "index": i["index"], "stratum": i["stratum"],
                      "p": i["p"], "scan": curves.scan_stats(i["A"], i["B"], i["p"], S)})
    controls["qr_scans"] = scans
    # 6. full-period point-count identity: 2 curves per arm per cell with p <= 2^20, 1 per arm above
    fp, chosen = [], []
    for arm in ("FAM", "N-A", "N-B"):
        for cell in inv["plan"]["cells"]:
            low = [i for i in ins if i["arm"] == arm and i["cell"] == cell and i["p"] <= 2 ** 20]
            chosen += [low[j] for j in curves.spread(len(low), 2)]
        high = [i for i in ins if i["arm"] == arm and i["p"] > 2 ** 20]
        if high:
            chosen.append(max(high, key=lambda i: i["p"]))
    for i in chosen:
        r = curves.full_period_identity(i["A"], i["B"], i["p"])
        fp.append({"arm": i["arm"], "cell": i["cell"], "index": i["index"], "p": i["p"], "N": i["N"], **r,
                   "expected_L": (i["N"] - 1) // 2, "expected_chi_sum": i["N"] - i["p"] - 1,
                   "ok": r["L"] == (i["N"] - 1) // 2 and r["zero"] == 0 and r["chi_sum"] == i["N"] - i["p"] - 1})
    controls["full_period"] = fp
    # 7. parallel.verify_determinism on the member task: serial == 4 workers
    small = sorted(inv["instances"], key=lambda i: i["N"])[:6]
    items = [{"inst": i, "K": K_det, "hist": True} for i in small]
    try:
        out = parallel.verify_determinism(member_task_det, items, workers=4)
        det = {"passed": True, "items": len(items), "workers": 4, "K": K_det,
               "result_sha256": __import__("hashlib").sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()}
    except RuntimeError as error:
        det = {"passed": False, "items": len(items), "workers": 4, "K": K_det, "error": str(error)}
    controls["determinism"] = det
    gates = analyze.gates_from_t2(controls)
    return {"controls": controls, "gates": gates, "gate_passed": all(gates.values())}


def trial_t3(inv: dict, args) -> dict:
    ctrl = [i for i in inv["instances"] if i["arm"] == "N-B-ctrl"]
    recs, tims = run_members([{"inst": i, "K": args.K, "hist": False} for i in ctrl], args.workers)
    out = analyze.sensitivity_from_records(recs, inv["plan"]["cells"])
    return {"members": recs, "sensitivity": out["cells"], "gates": out["gates"],
            "gate_passed": all(out["gates"].values()), "_timings": tims}


def trial_measure(trial_id: str, inv: dict, args) -> dict:
    sel = curves.select_for_trial(trial_id, inv["instances"])
    recs, tims = run_members([{"inst": i, "K": args.K, "hist": True} for i in sel], args.workers)
    return {"members": recs, "_timings": tims}


# -------------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trial", required=True, choices=sorted(curves.TRIALS))
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--memory-mb", type=int, default=None)
    ap.add_argument("--dev-limit", action="store_true", help="development: K=20, official=false")
    ap.add_argument("--k-random", type=int, default=None, help="development only (with --dev-limit): number of random bases")
    args = ap.parse_args(argv)
    run_id, workers, memory_mb, role = curves.TRIALS[args.trial]
    args.workers = workers if args.workers is None else args.workers
    args.K = (args.k_random or 20) if args.dev_limit else curves.K_RANDOM
    if args.k_random and not args.dev_limit:
        raise SystemExit("--k-random requires --dev-limit (the official K is 200)")
    cap_address_space(memory_mb if args.memory_mb is None else args.memory_mb)
    run_dir = Path(args.run_dir)
    if args.trial != "t8-analysis" and run_dir.name != run_id and not args.dev_limit:
        raise SystemExit(f"run directory {run_dir.name} is not the planned {run_id}")
    started = time.time()
    stages: dict = {}
    if args.trial == "t8-analysis":
        raw = analyze.run_analysis(run_dir.parent, official=not args.dev_limit)
        timings = {"stages": {"analysis_seconds": time.time() - started}}
    else:
        t0 = time.time()
        inv = build(run_dir, args.trial)
        stages["instances_seconds"] = time.time() - t0
        t0 = time.time()
        if args.trial == "t1-inventory":
            body = trial_t1(inv, args)
        elif args.trial == "t2-gate-instrument":
            body = trial_t2(inv, args)
        elif args.trial == "t3-gate-sensitivity":
            body = trial_t3(inv, args)
        else:
            body = trial_measure(args.trial, inv, args)
        stages["trial_seconds"] = time.time() - t0
        tims = body.pop("_timings", None) or []
        count_s = sum(t["count_seconds"] for t in tims)
        triples = sum(t["triples"] for t in tims)
        timings = {"stages": stages, "bsgs_seconds_total": sum(t["bsgs_seconds"] for t in tims),
                   "count_seconds_total": count_s, "triples_total": triples,
                   "tau_seconds_per_triple": (count_s / triples) if triples else None,
                   "per_member": tims,
                   "worker_rss_bytes_max": max([t["worker_rss_bytes"] for t in tims] or [0])}
        raw = {"schema": "crypto.autoresearch.cmfb.raw.v1", "experiment_id": curves.EXPERIMENT_ID,
               "trial_id": args.trial, "run_id": run_id, "role": role, "official": not args.dev_limit,
               "seeds": curves.FROZEN_SEEDS, "K": args.K, "workers": args.workers,
               "instance_list_sha256": inv["sha256"], "t1_sha_checked": inv.get("t1_sha_checked"),
               "pooling": inv["plan"], "member_counts": inv["counts"], **body}
    analyze.write_run_outputs(run_dir, trial_id=args.trial, run_id=run_id, role=role, raw=raw,
                              timings=timings, workers=args.workers, started=started,
                              memory_mb=memory_mb if args.memory_mb is None else args.memory_mb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
