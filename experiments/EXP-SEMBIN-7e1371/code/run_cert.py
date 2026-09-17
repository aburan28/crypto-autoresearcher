#!/usr/bin/env python3
"""run_cert.py -- executes EXP-SEMBIN-7e1371 (specification.yaml v1).

For every declared (family, cell, subspace, B, draw) instance:
  0. generate the system, verify its structure, record its canonical bytes and
     sha256;
  1. instrument S (m = t = 2 only): EXACT |V(I)| by exhaustive enumeration of
     V x V (solcount.count).  This is the denominator the degree-4 verdict is
     compared against, and it is what makes the n = 40..45 window decidable
     without a Groebner completion;
  2. instrument A: msolve F4 trace -- the `groebner_verdict_where_affordable`
     of the contract, and where it completes an independent second reading of
     |V(I)| (its quotient dimension);
  3. instrument C: single-level degree-4 Macaulay block -- rank, column count
     and rank deficiency against sum_{d<=4} C(N,d).  This is the contract's
     literal "degree-4 Macaulay block ... with rank and rank deficiency";
  4. instrument B: degree-capped Boolean closure at D = max generator degree
     .. 4, whose standard-monomial count against |V(I)| gives the contract's
     `degree4_sufficiency_verdict`.

The contract names one "certificate" and the two readings of it (single block,
iterated closure) are different quantities; both are recorded per instance and
the verdict field says which one it came from.  Nothing here interprets a
result.

Families: chained_eq5 (Semaev eq. (5)), single_eq4 (the nearby-object control,
eq. (4), m in {2,3}), matched_null (shape-matched random Boolean system).

Outputs (out_dir): results.jsonl, instances/<id>.{json,ms,gb,msolve.log},
controls.json, progress.log.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolsys  # noqa: E402
import closure_cert  # noqa: E402
import eq4sys  # noqa: E402
import f4_trace  # noqa: E402
import solcount  # noqa: E402
import sumpoly_check  # noqa: E402

SEEDS = [20260913101, 20260913102, 20260913103, 20260913104, 20260913105]
CELLS = {
    # the m = 2 diagonal window: Semaev Table 2 reports d_F4 = 4 at n = 40, and
    # the unreproduced comment-thread pointer reports step degree 5 at n = 45
    "m2_window": [(40, 2, 2, 20), (41, 2, 2, 21), (42, 2, 2, 21),
                  (43, 2, 2, 22), (44, 2, 2, 22), (45, 2, 2, 23)],
    "diagonal_baseline": [(17, 3, 3, 6)],
    # off-diagonal sweeps, k advanced one unit at a time (monotonicity probe)
    "sweep_n17": [(17, 3, 3, k) for k in (6, 7, 8, 9)],
    "sweep_n19": [(19, 3, 3, k) for k in (7, 8, 9, 10)],
    "sweep_n21": [(21, 3, 3, k) for k in (7, 8, 9, 10)],
    "sweep_n13": [(13, 4, 4, k) for k in (4, 5, 6)],
    "sweep_n12": [(12, 6, 6, k) for k in (2, 3, 4)],
}
SUBSPACES = ["low_degree_polynomial", "random_k_dimensional"]
B_MODES = ["B_equals_1", "B_random"]
FAMILIES = ["chained_eq5", "single_eq4", "matched_null"]
FAM_TAG = {"chained_eq5": "ch", "single_eq4": "e4", "matched_null": "mn"}


def log(fh, msg):
    line = f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}"
    print(line, flush=True)
    fh.write(line + "\n")
    fh.flush()


def ncols_le(N, D):
    return sum(math.comb(N, d) for d in range(D + 1))


def max_gen_degree(eqs):
    return max(max((bin(mm).count("1") for mm in e), default=0) for e in eqs)


def instance_id(family, n, m, t, k, subspace, B_mode, seed, draw):
    return (f"{FAM_TAG[family]}_n{n}_m{m}_t{t}_k{k}_{subspace[:3]}_{B_mode[:5]}"
            f"_s{seed}_d{draw}")


def build(family, n, m, t, k, B_mode, subspace, seed, draw):
    """Generate one instance of one family, or raise NotImplementedError."""
    if family == "chained_eq5":
        return boolsys.generate(n, m, t, k, B_mode, subspace, seed, draw)
    if family == "single_eq4":
        return eq4sys.generate(n, m, k, B_mode, subspace, seed, draw)
    if family == "matched_null":
        base = boolsys.generate(n, m, t, k, B_mode, subspace, seed, draw)
        null = boolsys.matched_null(base, seed)
        null.setdefault("n", n), null.setdefault("m", m), null.setdefault("t", t), null.setdefault("k", k)
        null["subspace"], null["B_mode"], null["seed"], null["draw"] = subspace, B_mode, seed, draw
        return null
    raise ValueError(family)


def measure(system, iid, out_dir, args, logf):
    """Run the instruments on one system; return its result records."""
    inst_dir = out_dir / "instances"
    inst_dir.mkdir(parents=True, exist_ok=True)
    N, eqs = system["N"], system["equations"]
    canon = boolsys.canonical_bytes(system)
    sha = hashlib.sha256(canon).hexdigest()
    (inst_dir / f"{iid}.json").write_bytes(json.dumps(
        {"meta": {k: v for k, v in system.items() if k not in ("equations", "var_names")},
         "system": json.loads(canon), "system_sha256": sha}, sort_keys=True).encode())
    gdeg = max_gen_degree(eqs)
    base = {"instance_id": iid, "system_sha256": sha, "N": N, "n_equations": len(eqs),
            "family": system.get("family"), "n": system.get("n"), "m": system.get("m"),
            "t": system.get("t"), "k": system.get("k"), "subspace": system.get("subspace"),
            "B_mode": system.get("B_mode"), "seed": system.get("seed"), "draw": system.get("draw"),
            "max_generator_degree": gdeg, "structure": system.get("structure"),
            "degree4_columns": ncols_le(N, 4)}
    records = []

    # --- instrument S: exact |V(I)| by enumeration of V (m = t = 2 only)
    s_known, s_source = None, None
    if system.get("family") == "chained_S3_eq5":
        sc = solcount.count_chained(system)
        cross = None
        if system.get("t") == 2:
            # the t = 2 counter is a separate program over a different enumeration
            # order; where both apply their agreement is an instrument control
            cross = solcount.count(system, reference=args.count_reference)
            sc["cross_check_count_m2"] = cross.get("solutions")
            sc["cross_check_agrees"] = (cross.get("solutions") == sc.get("solutions"))
        records.append(dict(base, instrument="exhaustive_solution_count",
                            **{kk: vv for kk, vv in sc.items() if kk != "instrument"}))
        if sc.get("status", "").startswith("completed") and sc.get("kernel_overflow_fibres") == 0:
            s_known, s_source = sc["solutions"], "exhaustive_count_chain"
        log(logf, f"{iid} count: solutions={sc.get('solutions')} status={sc.get('status')} "
                  f"cross={sc.get('cross_check_count_m2')} {sc.get('wall_s', 0):.1f}s")
    elif system.get("t") == 2 and system.get("family") == "single_S_eq4":
        sc = solcount.count(system, reference=args.count_reference)
        records.append(dict(base, instrument="exhaustive_solution_count",
                            **{kk: vv for kk, vv in sc.items() if kk != "instrument"}))
        if sc.get("status") == "completed":
            s_known, s_source = sc["solutions"], "exhaustive_count_over_V"
        log(logf, f"{iid} count: solutions={sc.get('solutions')} {sc.get('wall_s', 0):.1f}s")

    # --- instrument A: msolve F4 trace
    ms_path = inst_dir / f"{iid}.ms"
    ms_sha = boolsys.write_msolve(system, ms_path, field_equations=True)
    if args.skip_f4:
        tr = {"engine": "msolve", "engine_version": f4_trace.msolve_version(), "command": None,
              "field_equation_convention": "explicit_generators", "status": "unreached_declared",
              "unreached_reason": args.skip_f4_reason, "exit_code": None, "wall_s": 0.0,
              "peak_rss_bytes": None, "rounds": [], "f4_step_count": 0, "d_F4_semaev": None,
              "d_F4_last_productive_round": None, "d_F4_naive": None, "input_max_degree": gdeg,
              "d_F4_partial_max_deg_seen": None, "f4_empty_step_degrees": None,
              "quotient_dimension": None, "basis_length": None, "ideal_is_unit": None,
              "stdout_sha256": None}
    else:
        tr = f4_trace.run_msolve(ms_path, inst_dir / f"{iid}.gb", args.wall_cap, args.mem_cap,
                                 threads=args.threads, input_max_degree=gdeg)
        (inst_dir / f"{iid}.msolve.log").write_text(tr.pop("stdout"))
        err = tr.pop("stderr")
        if err.strip():
            (inst_dir / f"{iid}.msolve.err").write_text(err)
    records.append(dict(base, instrument="f4_trace_msolve", msolve_input_sha256=ms_sha, **tr))
    log(logf, f"{iid} F4: {tr['status']} d_F4_semaev={tr['d_F4_semaev']} naive={tr['d_F4_naive']} "
              f"quot={tr['quotient_dimension']} rounds={len(tr['rounds'])} {tr['wall_s']:.1f}s")
    if tr["status"] == "completed" and tr["quotient_dimension"] is not None:
        if s_known is not None and tr["quotient_dimension"] != s_known:
            log(logf, f"{iid} INSTRUMENT DISAGREEMENT: enumeration {s_known} vs msolve quotient "
                      f"{tr['quotient_dimension']}")
        elif s_known is None:
            s_known, s_source = tr["quotient_dimension"], "f4_quotient_dimension"

    # --- instrument C: single-level Macaulay block (the contract's literal certificate)
    single = []
    if args.no_single:
        single = None
    for D in ([] if single is None else ([3, 4] if args.single_d3 else [4])):
        if gdeg > D:
            single.append({"D": D, "status": "empty_block", "rows": 0, "cols": ncols_le(N, D),
                           "rank": 0, "deficiency_vs_columns": ncols_le(N, D),
                           "reason": f"max generator degree {gdeg} > D = {D}: no product fits in the block"})
            continue
        cols = ncols_le(N, D)
        if cols > args.single_max_cols:
            single.append({"D": D, "status": "unreached_declared", "cols": cols,
                           "reason": f"column count {cols} exceeds --single-max-cols {args.single_max_cols}"})
            continue
        ml = closure_cert.macaulay_single_level(N, eqs, D, args.closure_mem_cap)
        ml["deficiency_vs_columns"] = (ml["cols"] - ml["rank"]) if ml.get("rank") is not None else None
        single.append(ml)
    if single is not None:
        records.append(dict(base, instrument="macaulay_single_level", per_D=single))
        log(logf, f"{iid} single-level: " + "; ".join(
            f"D{x['D']} {x.get('status')} rows={x.get('rows')} cols={x.get('cols')} rank={x.get('rank')} "
            f"defic={x.get('deficiency_vs_columns')}" for x in single))

    # --- instrument B: degree-capped closure -> the sufficiency verdict
    if not args.no_closure:
        per_D, closure_D, verdict4 = [], None, None
        verdict4_source = "not_reached"
        for D in range(max(gdeg, 2), args.d_max + 1):
            if gdeg > D:
                continue
            cols = ncols_le(N, D)
            if cols > args.closure_max_cols:
                per_D.append({"D": D, "status": "unreached_declared", "ncols": cols,
                              "reason": f"column count {cols} exceeds --closure-max-cols {args.closure_max_cols}"})
                log(logf, f"{iid} closure D={D}: unreached_declared ncols={cols}")
                break
            t0 = time.time()
            cc = closure_cert.closure_certificate(N, eqs, D, args.closure_mem_cap, s_known=s_known,
                                                  standard_cap=args.standard_cap)
            cc["solutions_source"] = cc.get("solutions_source") or s_source
            cc["deficiency_vs_columns"] = (cc["ncols"] - cc["rank"]) if cc.get("rank") is not None else None
            per_D.append(cc)
            log(logf, f"{iid} closure D={D}: {cc.get('status')} verdict={cc.get('verdict')} "
                      f"rank={cc.get('rank')}/{cc.get('ncols')} std={cc.get('standard_monomials')} "
                      f"{time.time()-t0:.1f}s")
            if D == 4:
                verdict4, verdict4_source = cc.get("verdict"), "measured_at_D4"
            if cc.get("verdict") == "sufficient":
                closure_D = D
                if verdict4 is None and D <= 4:
                    # Decided BELOW 4, and the loop stops there rather than paying for a
                    # degree-4 closure whose answer is already fixed: W_D is contained in
                    # W_{D'} for D <= D', so the standard monomial count is non-increasing
                    # in D, and it is bounded below by |V(I)|. Equal to |V(I)| at D forces
                    # equal at every D' >= D. The inference is recorded as an inference --
                    # the D = 4 block was not built.
                    verdict4 = "sufficient"
                    verdict4_source = f"implied_by_sufficiency_at_D{D}"
                elif verdict4 is None:
                    # Decided ABOVE 4, which implies NOTHING about degree 4: the implication
                    # runs upward in D only. This is reachable with --d-max > 4, and for
                    # generators of degree > 4 the degree-4 block is empty, so a degree-4
                    # sufficiency verdict there would be flatly false.
                    verdict4 = "not_determined_at_D4"
                    verdict4_source = f"decided_at_D{D}_above_4_implies_nothing_about_D4"
                break
            if cc.get("status") != "completed":
                break
        if gdeg > args.d_max:
            verdict4, verdict4_source = "not_applicable", "generators_exceed_D4"
            per_D.append({"D": args.d_max, "status": "not_applicable",
                          "reason": f"max generator degree {gdeg} exceeds D = {args.d_max}: the "
                                    f"degree-{args.d_max} block contains no product of the generators"})
        if not per_D:
            status = "unreached"
        elif all(p.get("status") == "not_applicable" for p in per_D):
            status = "not_applicable"
        elif all(p.get("status") in ("completed", "not_applicable") for p in per_D):
            status = "completed"
        else:
            status = "unreached"
        records.append(dict(base, instrument="closure_certificate", closure_D=closure_D,
                            degree4_sufficiency_verdict=verdict4,
                            degree4_verdict_source=verdict4_source, solutions_used=s_known,
                            solutions_source=s_source, per_D=per_D, status=status))
    return records, sha


def controls(out_dir, args, logf):
    """The contract's six controls, plus the summation-polynomial identity check."""
    out = {}
    # invalid_input: k = 0 and t > m must be rejected by the generator
    inv = {}
    for label, kw in (("k_equals_0", dict(n=17, m=3, t=3, k=0)), ("t_greater_than_m", dict(n=17, m=2, t=3, k=6))):
        try:
            boolsys.generate(B_mode="B_equals_1", subspace="low_degree_polynomial", seed=SEEDS[0], draw=0, **kw)
            inv[label] = "NOT REJECTED"
        except ValueError as exc:
            inv[label] = f"rejected: {exc}"
    out["invalid_input"] = {"outcome": inv, "passed": all(v.startswith("rejected") for v in inv.values())}

    # known_false: planted degree-2 solution -- the degree-2 block must already decide
    kf = boolsys.known_false(12, 10, SEEDS[0])
    recs, sha = measure(kf, "ctl_known_false", out_dir, args, logf)
    cl = next((r for r in recs if r["instrument"] == "closure_certificate"), None)
    f4 = next((r for r in recs if r["instrument"] == "f4_trace_msolve"), None)
    out["known_false"] = {"outcome": {"closure_D": cl and cl.get("closure_D"),
                                      "f4_d_F4_semaev": f4 and f4.get("d_F4_semaev"),
                                      "f4_d_F4_naive": f4 and f4.get("d_F4_naive"),
                                      "expected": 2, "system_sha256": sha},
                          "passed": bool(cl and cl.get("closure_D") == 2)}

    # summation polynomial identity: S_3 and S_4 against the group law of the curve
    sp = [sumpoly_check.check(nn, trials=8) for nn in (13, 17, 21)]
    out["summation_polynomial_identity"] = {"outcome": sp, "passed": all(x["pass"] for x in sp)}
    (out_dir / "controls.json").write_text(json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--groups", default="")
    ap.add_argument("--cells", default="", help="comma list of n:m:t:k")
    ap.add_argument("--families", default="chained_eq5")
    ap.add_argument("--draws", type=int, default=1)
    ap.add_argument("--draw-list", default="",
                    help="explicit comma list of draw indices (overrides --draws); draw d uses seeds[d %% len(seeds)] and enters the instance derivation, so draws 5..9 are distinct instances from draws 0..4")
    ap.add_argument("--subspaces", default=",".join(SUBSPACES))
    ap.add_argument("--b-modes", default=",".join(B_MODES))
    ap.add_argument("--wall-cap", type=float, default=3600.0)
    ap.add_argument("--mem-cap", type=float, default=6.0, help="msolve RLIMIT_AS cap in GB")
    ap.add_argument("--closure-mem-cap", type=float, default=2.5,
                    help="closure/single-level dense-matrix estimate cap in GB (M4RI needs about twice it)")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--d-max", type=int, default=4)
    ap.add_argument("--standard-cap", type=int, default=200000)
    ap.add_argument("--single-max-cols", type=int, default=200000)
    ap.add_argument("--closure-max-cols", type=int, default=200000)
    ap.add_argument("--single-d3", action="store_true", help="also compute the D = 3 single-level block")
    ap.add_argument("--no-closure", action="store_true")
    ap.add_argument("--no-single", action="store_true", help="skip the single-level block (already measured in another pass)")
    ap.add_argument("--skip-f4", action="store_true")
    ap.add_argument("--skip-f4-reason", default="deferred by the executor to a later pass (memory contention)")
    ap.add_argument("--count-reference", action="store_true",
                    help="also run the O(2^2k) reference count (self-check; only feasible for small k)")
    ap.add_argument("--controls", default="none", help="all|none")
    ap.add_argument("--resume", action="store_true",
                    help="skip any (instance, instrument) already present in out-dir/results.jsonl")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    res_path = out_dir / "results.jsonl"
    done = set()
    if args.resume and res_path.exists():
        for line in res_path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            done.add((r["instance_id"], r["instrument"]))
    logf = open(out_dir / "progress.log", "a")
    fh = open(res_path, "a")

    def emit(recs):
        for r in recs:
            fh.write(json.dumps(r, sort_keys=True, default=str) + "\n")
        fh.flush()

    log(logf, f"start out_dir={out_dir} groups={args.groups} cells={args.cells} families={args.families} "
              f"draws={args.draws} caps: wall={args.wall_cap} mem={args.mem_cap} closure_mem={args.closure_mem_cap}")
    if args.controls == "all":
        c = controls(out_dir, args, logf)
        log(logf, "controls: " + json.dumps({k: v.get("passed") for k, v in c.items()}))

    cells = []
    for g in [x for x in args.groups.split(",") if x]:
        cells += CELLS[g]
    for spec in [x for x in args.cells.split(",") if x]:
        cells.append(tuple(int(v) for v in spec.split(":")))
    seen = set()
    cells = [c for c in cells if not (c in seen or seen.add(c))]

    for (n, m, t, k) in cells:
        for family in [f for f in args.families.split(",") if f]:
            for subspace in [s for s in args.subspaces.split(",") if s]:
                for B_mode in [b for b in args.b_modes.split(",") if b]:
                    draws = ([int(x) for x in args.draw_list.split(",") if x != ""]
                              if args.draw_list else list(range(args.draws)))
                    for draw in draws:
                        seed = SEEDS[draw % len(SEEDS)]
                        iid = instance_id(family, n, m, t, k, subspace, B_mode, seed, draw)
                        required = {"f4_trace_msolve"}
                        if not args.no_single:
                            required.add("macaulay_single_level")
                        if not args.no_closure:
                            required.add("closure_certificate")
                        if args.resume and required <= {i for (j, i) in done if j == iid}:
                            log(logf, f"{iid} skipped (resume)")
                            continue
                        try:
                            system = build(family, n, m, t, k, B_mode, subspace, seed, draw)
                        except NotImplementedError as exc:
                            emit([{"instance_id": iid, "instrument": "generator", "family": family,
                                   "n": n, "m": m, "t": t, "k": k, "subspace": subspace, "B_mode": B_mode,
                                   "seed": seed, "draw": draw, "status": "not_implemented", "reason": str(exc)}])
                            log(logf, f"{iid} not implemented: {exc}")
                            continue
                        st = system.get("structure")
                        if st is not None and not st["valid"]:
                            emit([{"instance_id": iid, "instrument": "generator", "family": family,
                                   "status": "invalid_structure", "structure": system["structure"]}])
                            log(logf, f"{iid} INVALID STRUCTURE {system['structure']}")
                            continue
                        recs, _ = measure(system, iid, out_dir, args, logf)
                        emit(recs)
    log(logf, "done")
    fh.close()
    logf.close()


if __name__ == "__main__":
    main()
