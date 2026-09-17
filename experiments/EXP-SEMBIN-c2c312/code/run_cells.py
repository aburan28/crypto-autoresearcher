#!/usr/bin/env python3
"""run_cells.py -- executes EXP-SEMBIN-c2c312 (specification.yaml v1).

For every declared cell x subspace variant x B mode x draw:
  1. generate the chained-S_3 Boolean system ONCE (boolsys.generate), record its
     sha256 (canonical bytes) and structural check;
  2. instrument A: msolve F4 trace (f4_trace.run_msolve) on the msolve file
     derived from those bytes; record d_F4 (Semaev reading and naive reading),
     the per-round profile, and the quotient dimension;
  3. instrument B: degree-capped closure certificate (closure_cert) for
     D = max generator degree .. D_max, stopping at the first SUFFICIENT; record
     the per-iteration rank profile and the verdict basis;
  4. instrument C: single-level Macaulay rank at D = 3, 4 (the GOAL-DREG-001
     statistic) with the archived semi-regular prediction;
  5. byte identity: both instruments' recorded input hashes are compared.

Controls (run once per seed unless stated): baseline = the two reproduction
cells; matched_null = shape-matched random system per reproduction instance;
known_false = planted point (both instruments must return 2); invalid_input =
t = 1 and k = 0 must be rejected; instrument_identity = the first instance of
each reproduction cell is measured twice by each instrument and the profiles
compared.

Outputs (out_dir):
  results.jsonl        one record per (instance, instrument) keyed by the contract's
                       (n, m, t, k, subspace, B, convention, seed, draw)
  instances/<id>.json  the generated system (canonical bytes) + metadata
  instances/<id>.ms    the msolve input derived from it
  controls.json        the control outcomes
  progress.log         human-readable progress
Nothing here interprets a result; the verdict fields are instrument outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolsys  # noqa: E402
import closure_cert  # noqa: E402
import f4_trace  # noqa: E402

SEEDS = [20260913001, 20260913002, 20260913003, 20260913004, 20260913005]
CELLS = {
    "reproduction": [(13, 4, 4, 4), (17, 3, 3, 6)],
    "separation": [(15, 5, 3, 3), (19, 3, 3, 7), (21, 3, 3, 7), (12, 6, 6, 2)],
    "off_diagonal": [(17, 3, 3, 7), (17, 3, 3, 8)],
}
SUBSPACES = ["low_degree_polynomial", "random_k_dimensional"]
B_MODES = ["B_equals_1", "B_random"]


def log(fh, msg):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1 << 20)


def instance_id(n, m, t, k, subspace, B_mode, seed, draw, family="sem"):
    return f"{family}_n{n}_m{m}_t{t}_k{k}_{subspace[:3]}_{B_mode[:5]}_s{seed}_d{draw}"


def measure(system, iid, out_dir, args, logf, s_hint=None, want_closure=True, want_single=True):
    """Run all instruments on one system; return the list of result records."""
    inst_dir = out_dir / "instances"
    inst_dir.mkdir(exist_ok=True)
    N = system["N"]
    eqs = system["equations"]
    canon = boolsys.canonical_bytes(system)
    sha = hashlib.sha256(canon).hexdigest()
    (inst_dir / f"{iid}.json").write_bytes(json.dumps({"meta": {k: v for k, v in system.items() if k not in ("equations", "var_names")},
                                                         "system": json.loads(canon), "system_sha256": sha}, indent=None, sort_keys=True).encode())
    ms_path = inst_dir / f"{iid}.ms"
    ms_sha = boolsys.write_msolve(system, ms_path, field_equations=True)
    base = {"instance_id": iid, "system_sha256": sha, "N": N,
            "n_equations": len(eqs), "family": system.get("family"),
            "n": system.get("n"), "m": system.get("m"), "t": system.get("t"), "k": system.get("k"),
            "subspace": system.get("subspace"), "B_mode": system.get("B_mode"), "seed": system.get("seed"), "draw": system.get("draw")}
    records = []
    # --- instrument A: msolve F4 trace
    t0 = time.time()
    tr = f4_trace.run_msolve(ms_path, inst_dir / f"{iid}.gb", args.wall_cap, args.mem_cap, threads=args.threads)
    (inst_dir / f"{iid}.msolve.log").write_text(tr.pop("stdout"))
    stderr = tr.pop("stderr")
    if stderr.strip():
        (inst_dir / f"{iid}.msolve.err").write_text(stderr)
    recA = dict(base, instrument="f4_trace_msolve", input_sha256=sha, msolve_input_sha256=ms_sha, **tr)
    records.append(recA)
    log(logf, f"{iid} F4: {tr['status']} d_F4_semaev={tr['d_F4_semaev']} naive={tr['d_F4_naive']} quot={tr['quotient_dimension']} rounds={len(tr['rounds'])} {time.time()-t0:.1f}s")
    s_known = tr["quotient_dimension"] if tr["status"] == "completed" else s_hint
    # --- instrument B: closure certificate
    if want_closure:
        max_gen_deg = max(max((bin(mm).count("1") for mm in e), default=0) for e in eqs)
        closure_D = None
        per_D = []
        for D in range(max_gen_deg, args.d_max + 1):
            t0 = time.time()
            cc = closure_cert.closure_certificate(N, eqs, D, args.mem_cap, s_known=s_known, standard_cap=args.standard_cap)
            per_D.append(cc)
            log(logf, f"{iid} closure D={D}: {cc.get('status')} verdict={cc.get('verdict')} rank={cc.get('rank')} ncols={cc.get('ncols')} iters={len(cc.get('iterations', []))} {time.time()-t0:.1f}s")
            if cc.get("verdict") == "sufficient":
                closure_D = D
                break
            if cc.get("status") != "completed":
                break
        recB = dict(base, instrument="closure_certificate", input_sha256=sha, closure_D=closure_D,
                    max_generator_degree=max_gen_deg, per_D=per_D,
                    D_macaulay_rank_statistic=closure_D,
                    status="completed" if closure_D is not None or all(p.get("status") == "completed" for p in per_D) else "unreached")
        records.append(recB)
    # --- instrument C: single-level Macaulay (DREG statistic)
    if want_single:
        single = []
        for D in (3, 4):
            cols = sum(__import__("math").comb(N, d) for d in range(D + 1))
            if cols > args.single_max_cols:
                single.append({"D": D, "status": "unreached_declared", "cols": cols})
                continue
            ml = closure_cert.macaulay_single_level(N, eqs, D, args.mem_cap)
            single.append(ml)
        recC = dict(base, instrument="macaulay_single_level_DREG", input_sha256=sha, per_D=single)
        records.append(recC)
        log(logf, f"{iid} single-level: " + "; ".join(f"D{x['D']} rank={x.get('rank')} rows={x.get('rows')} cols={x.get('cols')} deficit={x.get('deficit_vs_semiregular')}" for x in single))
    return records, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--groups", default="reproduction,off_diagonal,separation")
    ap.add_argument("--draws", type=int, default=20)
    ap.add_argument("--subspaces", default=",".join(SUBSPACES))
    ap.add_argument("--b-modes", default=",".join(B_MODES))
    ap.add_argument("--wall-cap", type=float, default=3600.0)
    ap.add_argument("--mem-cap", type=float, default=8.0)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--d-max", type=int, default=5)
    ap.add_argument("--standard-cap", type=int, default=100000)
    ap.add_argument("--single-max-cols", type=int, default=200000)
    ap.add_argument("--controls", default="all", help="all|none")
    ap.add_argument("--cells", default="", help="override: comma list of n:m:t:k")
    ap.add_argument("--no-closure", action="store_true")
    ap.add_argument("--closure-draws", type=int, default=None,
                    help="run the closure instrument only for draw < K (F4 trace and single-level run on every draw); "
                         "the identity-repeat and matched-null controls always run every instrument")
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    logf = open(out / "progress.log", "a")
    results = open(out / "results.jsonl", "a")
    started = time.time()
    log(logf, f"start pid={os.getpid()} args={vars(args)}")

    def emit(recs):
        for r in recs:
            results.write(json.dumps(r, sort_keys=True, default=str) + "\n")
        results.flush()

    controls = {}
    if args.controls == "all":
        # invalid_input
        inv = {}
        for bad, label in (((17, 3, 1, 6), "t_equals_1"), ((17, 3, 3, 0), "k_equals_0")):
            try:
                boolsys.generate(*bad, "B_equals_1", "low_degree_polynomial", SEEDS[0], 0)
                inv[label] = "NOT REJECTED"
            except ValueError as exc:
                inv[label] = f"rejected: {exc}"
        controls["invalid_input"] = inv
        log(logf, f"control invalid_input: {inv}")
        # known_false: planted point, N = 35 (the n=17 cell's N), 34 quadratics
        kf = boolsys.known_false(35, 34, SEEDS[0])
        recs, sha = measure(kf, "ctrl_known_false_N35", out, args, logf)
        emit(recs)
        controls["known_false"] = {"system_sha256": sha,
                                   "f4_d_F4_semaev": recs[0]["d_F4_semaev"], "f4_d_F4_naive": recs[0]["d_F4_naive"],
                                   "closure_D": recs[1]["closure_D"] if len(recs) > 1 else None,
                                   "expected": 2}
        log(logf, f"control known_false: {controls['known_false']}")

    cells = []
    if args.cells:
        for spec in args.cells.split(","):
            n, m, t, k = (int(x) for x in spec.split(":"))
            cells.append(("override", (n, m, t, k)))
    else:
        for g in args.groups.split(","):
            for c in CELLS[g]:
                cells.append((g, c))
    subspaces = args.subspaces.split(",")
    b_modes = args.b_modes.split(",")
    identity_done = set()
    null_done = set()
    for group, (n, m, t, k) in cells:
        for subspace in subspaces:
            for B_mode in b_modes:
                for draw in range(args.draws):
                    seed = SEEDS[draw % len(SEEDS)]
                    iid = instance_id(n, m, t, k, subspace, B_mode, seed, draw)
                    if (out / "instances" / f"{iid}.json").exists() and any(iid in line for line in open(out / "results.jsonl")):
                        continue  # resume
                    sysd = boolsys.generate(n, m, t, k, B_mode, subspace, seed, draw)
                    if not sysd["structure"]["valid"]:
                        log(logf, f"{iid} STRUCTURE INVALID {sysd['structure']}")
                        emit([{"instance_id": iid, "instrument": "structure", "status": "invalid", **sysd["structure"]}])
                        continue
                    want_cl = (not args.no_closure) and (args.closure_draws is None or draw < args.closure_draws)
                    recs, sha = measure(sysd, iid, out, args, logf, want_closure=want_cl)
                    for r in recs:
                        r["group"] = group
                        r["structure"] = sysd["structure"]
                    emit(recs)
                    # instrument identity + matched null on the first instance of each reproduction cell
                    if args.controls == "all" and group == "reproduction" and (n, m, t, k) not in identity_done and draw == 0:
                        identity_done.add((n, m, t, k))
                        recs2, sha2 = measure(sysd, iid + "_repeat", out, args, logf, want_closure=not args.no_closure)
                        for r in recs2:
                            r["group"] = "instrument_identity_repeat"
                        emit(recs2)
                        ident = {"system_sha256_first": sha, "system_sha256_repeat": sha2,
                                 "f4_rounds_equal": [x["rounds"] for x in recs if x["instrument"] == "f4_trace_msolve"] == [x["rounds"] for x in recs2 if x["instrument"] == "f4_trace_msolve"],
                                 "closure_profiles_equal": [[(p.get("D"), p.get("rank"), p.get("basis_lm_sha256"), [(i["rows"], i["rank_after"]) for i in p.get("iterations", [])]) for p in x["per_D"]] for x in recs if x["instrument"] == "closure_certificate"]
                                                           == [[(p.get("D"), p.get("rank"), p.get("basis_lm_sha256"), [(i["rows"], i["rank_after"]) for i in p.get("iterations", [])]) for p in x["per_D"]] for x in recs2 if x["instrument"] == "closure_certificate"]}
                        controls.setdefault("instrument_identity", {})[iid] = ident
                        log(logf, f"control instrument_identity {iid}: {ident}")
                    if args.controls == "all" and group == "reproduction" and (n, m, t, k, subspace, B_mode) not in null_done:
                        null_done.add((n, m, t, k, subspace, B_mode))
                        nul = boolsys.matched_null(sysd, seed)
                        nul["source_sha256"] = sha
                        recs3, sha3 = measure(nul, iid.replace("sem_", "null_"), out, args, logf, want_closure=not args.no_closure)
                        for r in recs3:
                            r["group"] = "matched_null"
                            r["source_instance"] = iid
                        emit(recs3)
                        controls.setdefault("matched_null", {})[iid] = {
                            "null_sha256": sha3,
                            "f4_d_F4_semaev": recs3[0]["d_F4_semaev"], "f4_status": recs3[0]["status"],
                            "closure_D": recs3[1]["closure_D"] if len(recs3) > 1 else None,
                            "structured_f4_d_F4_semaev": recs[0]["d_F4_semaev"],
                            "structured_closure_D": recs[1]["closure_D"] if len(recs) > 1 else None}
                        log(logf, f"control matched_null {iid}: {controls['matched_null'][iid]}")
                    (out / "controls.json").write_text(json.dumps(controls, indent=2, sort_keys=True))
    (out / "controls.json").write_text(json.dumps(controls, indent=2, sort_keys=True))
    log(logf, f"done wall={time.time()-started:.1f}s peak_rss_gb={peak_rss_gb():.2f}")


if __name__ == "__main__":
    main()
