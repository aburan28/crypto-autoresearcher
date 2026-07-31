"""EXP-ENDO-001 run driver (frozen protocol, TASK-20260727-002).

Usage: python3 experiments/EXP-ENDO-001/code/run_ENDO.py --run-id RUN-ENDO-001

Executes exactly one planned run of replication.planned_runs and writes the
immutable run record (spec required_artifacts + byte-identical docs-style
duplicates). Runs are sequential and depend on earlier runs' frozen outputs.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import endo_common as ec  # noqa: E402

EXP_DIR = ec.EXP_DIR


# ------------------------------------------------------------------ helpers
def cell_key(family: str, bits: int) -> str:
    return f"{family}-{bits}"


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_side(run_dir: str, name: str, obj):
    with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=False, default=str)


def phi_fn_for(inst: dict):
    fam = inst["family"]
    if fam in ("j0", "j1728"):
        return lambda pt: ec.phi_image_point(fam, pt, inst) if pt is not None else None
    p = inst["p"]
    return lambda pt: (pt[0], (-pt[1]) % p) if pt is not None else None


class Ctx:
    def __init__(self, run_id: str, out_root: str | None):
        self.run_id = run_id
        self.out_root = out_root
        self.t0 = time.time()
        self.guard = ec.BudgetGuard(self.t0)
        self.logs: list[str] = []
        self.deviations: list[str] = []
        self.anomalies: list[str] = []

    def log(self, msg: str):
        line = f"[{self.run_id} {time.time() - self.t0:8.2f}s] {msg}"
        self.logs.append(line)
        print(line, flush=True)


# ---------------------------------------------------------------- RUN-ENDO-001
def run_001(ctx: Ctx):
    """Instance generation and freeze (9 curves, GLV filters, seeds), SHA-256."""
    cells = []
    for family in ec.FAMILIES:
        for seed in ec.SEEDS:
            bits = ec.SEED_TO_BITS[seed]
            ctx.guard.check("instance-generation")
            t_gen = time.time()
            if family == "j0":
                rec = ec.gen_j0(seed, bits)
            elif family == "j1728":
                rec = ec.gen_j1728(seed, bits)
            else:
                rec = ec.gen_generic(seed, bits)
            checks = ec.instance_checks(rec)
            n = rec["n"]
            B = math.isqrt(n) + (1 if math.isqrt(n) ** 2 < n else 0)
            cid = ec.curve_id(rec["p"], rec["a"], rec["b"], bits)
            cell = {"cell_id": cell_key(family, bits), **rec, "B": B,
                    "curve_id": cid, "j_invariant": checks["j_invariant"],
                    "checks": checks, "generation_seconds": round(time.time() - t_gen, 3)}
            cell["sha256"] = ec.sha256_obj(cell)
            cells.append(cell)
            ctx.log(f"cell {cell['cell_id']}: p={rec['p']} n={n} B={B} "
                    f"j={checks['j_invariant']} gen={cell['generation_seconds']}s")
    # integrity cross-check: naive order vs order_bsgs at 16 bits
    xcheck = {}
    for cell in cells:
        if cell["field_bits"] == 16:
            E = ec.EllipticCurve(cell["p"], cell["a"], cell["b"])
            naive = E.order()
            bsgs = E.order_bsgs()
            xcheck[cell["cell_id"]] = {"naive_order": naive, "bsgs_order": bsgs,
                                       "match": naive == bsgs}
            ctx.guard.check("order-xcheck")
    doc = {"experiment_id": ec.EXP_ID, "run_id": "RUN-ENDO-001",
           "created_at": ec.iso(time.time()),
           "seed_policy": ("seeds {1,2,3} mapped one-to-one to sizes {16,20,24} "
                           "within each family (EXP-MTIC-001 amendment precedent)"),
           "seed_to_bits": ec.SEED_TO_BITS, "families": ec.FAMILIES,
           "cells": cells}
    doc["content_sha256"] = ec.sha256_obj([c["sha256"] for c in cells])
    ec.write_yaml(ec.FROZEN_INSTANCES, doc)
    all_ok = all(all(v for k, v in c["checks"].items()
                     if k in ("p_prime", "n_prime", "P_on_curve", "Q_on_curve",
                              "Q_eq_kP", "nP_eq_O", "congruence")) for c in cells)
    metrics = {"n_instances": len(cells),
               "instances": {c["cell_id"]: {"p": c["p"], "n": c["n"], "B": c["B"],
                                            "j_invariant": c["j_invariant"],
                                            "curve_id": c["curve_id"]} for c in cells},
               "all_core_checks_pass": all_ok,
               "order_crosscheck_16bit": xcheck,
               "content_sha256": doc["content_sha256"]}
    return {"metrics": metrics,
            "raw": {"cells_sha256": {c["cell_id"]: c["sha256"] for c in cells},
                    "checks": {c["cell_id"]: c["checks"] for c in cells},
                    "derivations": {c["cell_id"]: c["derivation"] for c in cells},
                    "generation_seconds": {c["cell_id"]: c["generation_seconds"]
                                           for c in cells}},
            "valid": all_ok, "invalid_reason": None if all_ok else "core instance check failed",
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "instance checks recomputed by harness/toycurve"},
            "status": "completed_valid" if all_ok else "completed_invalid",
            "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-002
def run_002(ctx: Ctx):
    """Factor-base construction, all four arms; orbit-closure audit; freeze."""
    fv = ec.verify_frozen_instances()
    ctx.log(f"frozen-instances verification: {fv}")
    if not (fv["per_cell_sha256_ok"] and fv["content_sha256_ok"]):
        return {"metrics": {"frozen_verification": fv}, "raw": {},
                "valid": False, "invalid_reason": "frozen-instances SHA-256 mismatch",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
                "status": "completed_invalid", "seed_record": ec.SEEDS}
    inst_doc = ec.read_yaml(ec.FROZEN_INSTANCES)
    bases = []
    audits = {}
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            inst = ec.get_cell(inst_doc, family, bits)
            if family == "j0":
                fb = ec.fb_phi_j0(inst)
            elif family == "j1728":
                fb = ec.fb_phi_j1728(inst)
            else:
                fb = ec.fb_neg_generic(inst)
            ctx.guard.check("structured-fb")
            audit = ec.orbit_audit(fb, inst)
            audits[f"{cell_key(family, bits)}:{fb['arm']}"] = audit
            rec = {**fb, "family": family, "field_bits": bits,
                   "cell_id": cell_key(family, bits), "audit": audit}
            rec["sha256"] = ec.sha256_obj(rec)
            bases.append(rec)
            ctx.log(f"{cell_key(family, bits)} {fb['arm']}: cols={len(fb['elements'])} "
                    f"completeness={audit['orbit_completeness_fraction']}")
            # random baseline: identical curve, column count and kind
            rfb = ec.fb_random(inst, len(fb["elements"]), fb["column_kind"])
            raudit = ec.orbit_audit(rfb, inst)
            audits[f"{cell_key(family, bits)}:random_baseline"] = raudit
            rrec = {**rfb, "family": family, "field_bits": bits,
                    "cell_id": cell_key(family, bits), "audit": raudit}
            rrec["sha256"] = ec.sha256_obj(rrec)
            bases.append(rrec)
            ctx.guard.check("random-fb")
    # AP benchmark at 20-bit cells (EV-STR-001 protocol)
    for family in ec.FAMILIES:
        inst = ec.get_cell(inst_doc, family, 20)
        afb = ec.fb_ap(inst)
        aa = ec.orbit_audit(afb, inst)
        audits[f"{cell_key(family, 20)}:ap_benchmark"] = aa
        arec = {**afb, "family": family, "field_bits": 20,
                "cell_id": cell_key(family, 20), "audit": aa}
        arec["sha256"] = ec.sha256_obj(arec)
        bases.append(arec)
        ctx.log(f"{family}-20 ap_benchmark: B={afb['B']} x_max={afb['x_max']}")
    doc = {"experiment_id": ec.EXP_ID, "run_id": "RUN-ENDO-002",
           "created_at": ec.iso(time.time()), "bases": bases}
    doc["content_sha256"] = ec.sha256_obj([b["sha256"] for b in bases])
    ec.write_yaml(ec.FROZEN_FACTORBASES, doc)
    completeness = {k: v["orbit_completeness_fraction"] for k, v in audits.items()
                    if v["orbit_completeness_fraction"] is not None}
    metrics = {"n_bases": len(bases),
               "orbit_completeness_fraction": completeness,
               "columns_per_cell_arm": {f"{b['cell_id']}:{b['arm']}": len(b["elements"])
                                        for b in bases},
               "frozen_instances_verification": fv,
               "content_sha256": doc["content_sha256"]}
    return {"metrics": metrics, "raw": {"audits": audits}, "valid": True,
            "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "orbit audits recomputed from frozen elements"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ------------------------------------------------------- collection machinery
def collect_job(ctx: Ctx, inst_doc, fb_doc, family: str, bits: int, arm: str):
    inst = ec.get_cell(inst_doc, family, bits)
    fb = ec.get_fb(fb_doc, family, bits, arm)
    E = ec.EllipticCurve(inst["p"], inst["a"], inst["b"])
    ck = cell_key(family, bits)
    targets = ec.make_targets(inst, ec.N_HIT_TARGETS, f"hit:{ck}")
    pool = ec.make_targets(inst, ec.N_HARVEST_POOL, f"harv:{ck}")
    need_rows = len(fb["elements"])
    r = fb["r"]
    membership = set((e[0], e[1]) for e in fb["elements"]) \
        if fb["column_kind"] == "point" else None
    t0 = time.time()
    # harvest >= 3.2xB fresh base relations: the surplus feeds the greedy
    # full-rank square subsystem used for Wiedemann calibration (EV-STR-001
    # precedent; weight-3 0/1 matrices are generically ~5% rank deficient and
    # full rank needs ~3xB rows -- measured; recorded in RUN-ENDO-009)
    base_quota = max(ec.ceil_div(need_rows, r) if r else need_rows,
                     need_rows * 16 // 5 + 1)
    harvest_need = base_quota * (r if r else 1)
    res = ec.enumeration_engine(E, inst["n"], fb["elements"], targets, pool,
                                harvest_need, r, None,
                                ec.EVAL_CAP_PER_CELL, ec.CELL_TIME_CAP_S, t0,
                                ctx.guard, ctx.log, membership=membership)
    phi_fn = phi_fn_for(inst) if r else None
    matrix = ec.assemble_matrix(E, inst, fb, res["base_relations"], need_rows,
                                ctx.log, phi_fn=phi_fn)
    cert = ec.verify_matrix_relations(inst, matrix)
    # surplus = FRESH (non-orbit-closed) rows from all harvested base
    # relations, for the full-rank calibration subsystem; certificate-verified
    col_index = {}
    for c, e in enumerate(fb["elements"]):
        col_index[e[0] if fb["column_kind"] == "x" else (e[0], e[1])] = c
    surplus_rows = []
    for rel in res["base_relations"]:
        idx = []
        ok = True
        for s in rel["summands"]:
            key = s[0] if fb["column_kind"] == "x" else (s[0], s[1])
            if key not in col_index:
                ok = False
                break
            idx.append(col_index[key])
        if ok and len(set(idx)) == len(idx):
            surplus_rows.append(sorted(idx))
    surplus_cert = ec.verify_matrix_relations(
        inst, {"row_targets": [rel["target"] for rel in res["base_relations"]],
               "row_summands": [rel["summands"] for rel in res["base_relations"]]})
    cert = {"rows_checked": cert["rows_checked"] + surplus_cert["rows_checked"],
            "rows_failed": cert["rows_failed"] + surplus_cert["rows_failed"],
            "all_verified": cert["all_verified"] and surplus_cert["all_verified"],
            "kind": "decomposition", "verifier": "independent-recompute"}
    evals = dict(res["evals"])
    evals["total_tuple_evaluations"] = (evals["pair_x_evaluations"] +
                                        evals["probe_x_evaluations"])
    ctx.log(f"{ck}:{arm} cols={need_rows} evals={evals['total_tuple_evaluations']} "
            f"hit_rate={res['hit_test']['hit_rate']} base_rel={res['harvest']['base_relations']} "
            f"R={matrix['R']} square={matrix['square']} cert_ok={cert['all_verified']}")
    stats = {
        "cell_id": ck, "arm": arm, "curve_id": inst["curve_id"], "seed": inst["seed"],
        "B": fb["B"], "n_columns": need_rows, "n": inst["n"],
        "evals": evals, "censored": res["censored"],
        "skipped_same_x_pairs": res["skipped_same_x_pairs"],
        "resolve_stats": res["resolve_stats"],
        "pair_table": res["pair_table"],
        "hit_test": {"n_targets": res["hit_test"]["n_targets"],
                     "hits": res["hit_test"]["hits"],
                     "hit_rate": res["hit_test"]["hit_rate"],
                     "wilson95": ec.wilson_ci(res["hit_test"]["hits"],
                                              res["hit_test"]["n_targets"]),
                     "per_target_probe_hits": [t["probe_hits"]
                                               for t in res["hit_test"]["per_target"]]},
        "harvest": res["harvest"],
        "matrix": {"R": matrix["R"], "B": matrix["B"], "row_blocks": matrix["row_blocks"],
                   "square": matrix["square"], "nnz": sum(len(r_) for r_ in matrix["rows"]),
                   "surplus_rows": len(surplus_rows)},
        "certificate_verification": cert,
        "collection_seconds": round(time.time() - t0, 3),
    }
    matrix_out = {"cell_id": ck, "arm": arm, "n": inst["n"], "r": r,
                  "column_kind": fb["column_kind"], "column_xs": matrix["column_xs"],
                  "R": matrix["R"], "B": matrix["B"], "rows": matrix["rows"],
                  "row_targets": matrix["row_targets"],
                  "row_summands": matrix["row_summands"],
                  "surplus_rows": surplus_rows}
    return stats, matrix_out


def collection_run(ctx: Ctx, jobs: list[tuple[str, int, str]], run_label: str):
    fv1 = ec.verify_frozen_instances()
    fv2 = ec.verify_frozen_factorbases()
    ctx.log(f"frozen verification: instances={fv1['content_sha256_ok']} "
            f"factorbases={fv2['content_sha256_ok']}")
    if not (fv1["content_sha256_ok"] and fv1["per_cell_sha256_ok"]
            and fv2["content_sha256_ok"] and fv2["per_base_sha256_ok"]):
        return {"metrics": {"frozen_verification": {"instances": fv1, "factorbases": fv2}},
                "raw": {}, "valid": False,
                "invalid_reason": "frozen-artifact SHA-256 mismatch",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
                "status": "completed_invalid", "seed_record": ec.SEEDS}
    inst_doc = ec.read_yaml(ec.FROZEN_INSTANCES)
    fb_doc = ec.read_yaml(ec.FROZEN_FACTORBASES)
    all_stats, matrices = {}, {}
    all_valid = True
    for family, bits, arm in jobs:
        ctx.guard.check(f"{family}-{bits}-{arm}")
        try:
            stats, matrix = collect_job(ctx, inst_doc, fb_doc, family, bits, arm)
        except ec.ResourceExhaustion:
            raise
        except Exception as e:  # per-cell infrastructure failure: record, continue
            ctx.log(f"CELL FAILURE {family}-{bits}-{arm}: {e!r}")
            all_stats[cell_key(family, bits) + ":" + arm] = {
                "cell_id": cell_key(family, bits), "arm": arm,
                "cell_status": "failed_infrastructure", "error": repr(e)}
            ctx.anomalies.append(f"cell {family}-{bits}-{arm} failed_infrastructure: {e!r}")
            continue
        key = cell_key(family, bits) + ":" + arm
        all_stats[key] = stats
        matrices[key] = matrix
        if not stats["certificate_verification"]["all_verified"]:
            all_valid = False
    metrics = {
        "cells": {k: {kk: v[kk] for kk in ("cell_id", "arm", "B", "n_columns",
                                           "hit_test", "harvest", "matrix", "evals",
                                           "censored", "collection_seconds")
                      if kk in v}
                  for k, v in all_stats.items()},
        "frozen_verification": {"instances": fv1, "factorbases": fv2},
        "all_relation_certificates_verified": all_valid,
    }
    return {"metrics": metrics, "raw": {"cells": all_stats},
            "side_files": {"matrices.json": matrices},
            "valid": all_valid,
            "invalid_reason": None if all_valid else "relation certificate failure",
            "certificate": {"kind": "decomposition", "verified": all_valid,
                            "verifier": "independent-recompute (harness/toycurve)"},
            "status": "completed_valid" if all_valid else "completed_invalid",
            "seed_record": ec.SEEDS}


def run_003(ctx: Ctx):
    """Relation collection on phi-invariant bases, j=0 cells."""
    return collection_run(ctx, [("j0", 16, "phi_invariant"),
                                ("j0", 20, "phi_invariant"),
                                ("j0", 24, "phi_invariant")], "RUN-ENDO-003")


def run_004(ctx: Ctx):
    """Relation collection on phi-invariant j=1728 cells and generic negation cells."""
    return collection_run(ctx, [("j1728", 16, "phi_invariant"),
                                ("j1728", 20, "phi_invariant"),
                                ("j1728", 24, "phi_invariant"),
                                ("generic", 16, "negation_orbit_generic"),
                                ("generic", 20, "negation_orbit_generic"),
                                ("generic", 24, "negation_orbit_generic")], "RUN-ENDO-004")


def run_005(ctx: Ctx):
    """Relation collection on random-baseline bases, all cells."""
    jobs = [(fam, bits, "random_baseline")
            for fam in ec.FAMILIES for bits in ec.BITS_LIST]
    return collection_run(ctx, jobs, "RUN-ENDO-005")


# ---------------------------------------------------------------- RUN-ENDO-006
def run_006(ctx: Ctx):
    """Relation collection on AP-benchmark bases, 20-bit cells (EV-STR-001 protocol)."""
    fv1 = ec.verify_frozen_instances()
    fv2 = ec.verify_frozen_factorbases()
    if not (fv1["content_sha256_ok"] and fv2["content_sha256_ok"]):
        return {"metrics": {"frozen_verification": {"instances": fv1, "factorbases": fv2}},
                "raw": {}, "valid": False,
                "invalid_reason": "frozen-artifact SHA-256 mismatch",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
                "status": "completed_invalid", "seed_record": ec.SEEDS}
    inst_doc = ec.read_yaml(ec.FROZEN_INSTANCES)
    fb_doc = ec.read_yaml(ec.FROZEN_FACTORBASES)
    cells_out, matrices = {}, {}
    for family in ec.FAMILIES:
        bits = 20
        ck = cell_key(family, bits)
        inst = ec.get_cell(inst_doc, family, bits)
        fb = ec.get_fb(fb_doc, family, bits, "ap_benchmark")
        E = ec.EllipticCurve(inst["p"], inst["a"], inst["b"])
        p, n = inst["p"], inst["n"]
        pts = [tuple(e) for e in fb["elements"]]
        xs = fb["column_xs"]
        x_to_idx = {x: i for i, x in enumerate(xs)}
        x_max = fb["x_max"]
        B = fb["B"]
        t0 = time.time()
        # enumerate AP supports {x, x+d, x+2d} subseteq FB, d in {1..64}
        supports = []  # (i0, i1, i2), key (x_start, d)
        for d in range(1, ec.AP_D_MAX + 1):
            span = 2 * d
            if span > x_max:
                break
            for x in xs:
                if x + span > x_max:
                    break
                j1 = x_to_idx.get(x + d)
                if j1 is None:
                    continue
                j2 = x_to_idx.get(x + 2 * d)
                if j2 is None:
                    continue
                supports.append((x_to_idx[x], j1, j2))
        supply = len(supports)
        # sums: 4 sign-x variants per support + canonical EV-STR-001 sum
        sum_x_table: dict[int, list[int]] = {}
        canon_sums: dict = {}
        evals = 0
        for si, (i0, i1, i2) in enumerate(supports):
            A, Bp, C = pts[i0], pts[i1], pts[i2]
            T1 = E.add(A, Bp)
            T2 = E.add(A, E.negate(Bp))
            evals += 2
            for T in (T1, T2):
                if T is None:
                    continue
                Sp = E.add(T, C)
                Sm = E.add(T, E.negate(C))
                evals += 2
                for S in (Sp, Sm):
                    if S is not None:
                        sum_x_table.setdefault(S[0], []).append(si)
            full = E.add(T1, C)
            evals += 1
            if full is not None:
                canon_sums.setdefault(full, 0)
                canon_sums[full] += 1
        targets = ec.make_targets(inst, ec.N_HIT_TARGETS, f"hit:{ck}")
        xwise_hits = 0
        canon_hits = 0
        per_target = []
        for t in targets:
            R = tuple(t["R"])
            xh = R[0] in sum_x_table
            ch = R in canon_sums
            xwise_hits += 1 if xh else 0
            canon_hits += 1 if ch else 0
            per_target.append({"target_index": t["index"], "xwise_hit": xh,
                               "canonical_exact_hit": ch})
        ctx.guard.check("ap-hit-test")
        total_comb = math.comb(B, 3)
        stats = {
            "cell_id": ck, "arm": "ap_benchmark", "curve_id": inst["curve_id"],
            "seed": inst["seed"], "B": B, "n": n, "x_max": x_max,
            "ap_supply": supply, "supply_ratio_supply_over_B": supply / B,
            "yield_penalty_C_B_3_over_supply": total_comb / supply if supply else None,
            "sum_x_table_entries": sum(len(v) for v in sum_x_table.values()),
            "distinct_canonical_sums": len(canon_sums),
            "coverage_canonical_sums_over_n": len(canon_sums) / n,
            "evals": {"sum_evaluations": evals},
            "hit_test": {"n_targets": len(targets),
                         "xwise_hits": xwise_hits,
                         "xwise_hit_rate": xwise_hits / len(targets),
                         "xwise_wilson95": ec.wilson_ci(xwise_hits, len(targets)),
                         "canonical_exact_hits": canon_hits,
                         "canonical_exact_hit_rate_per_target": canon_hits / len(targets),
                         "canonical_exact_hit_rate_per_tuple":
                             canon_hits / (len(targets) * supply) if supply else None,
                         "per_target": per_target},
            "collection_seconds": round(time.time() - t0, 3),
        }
        cells_out[ck + ":ap_benchmark"] = stats
        # matrix rows = AP supports (EV-STR-001 row keys (x_start, d))
        row_keys = []
        for (i0, i1, i2) in supports:
            dd = (xs[i2] - xs[i0]) // 2
            row_keys.append([xs[i0], dd])
        matrices[ck + ":ap_benchmark"] = {
            "cell_id": ck, "arm": "ap_benchmark", "n": n,
            "column_kind": "x_interval", "column_xs": xs,
            "R": supply, "B": B, "rows": [sorted(s) for s in supports],
            "row_keys": row_keys}
        ctx.log(f"{ck} AP: supply={supply} xwise_rate={stats['hit_test']['xwise_hit_rate']:.4f} "
                f"canon_hits={canon_hits} yield_penalty={stats['yield_penalty_C_B_3_over_supply']:.1f}")
    metrics = {"cells": {k: {kk: v[kk] for kk in
                             ("ap_supply", "supply_ratio_supply_over_B",
                              "yield_penalty_C_B_3_over_supply",
                              "coverage_canonical_sums_over_n", "hit_test",
                              "collection_seconds") if kk in v}
                         for k, v in cells_out.items()},
               "frozen_verification": {"instances": fv1, "factorbases": fv2}}
    return {"metrics": metrics, "raw": {"cells": cells_out},
            "side_files": {"matrices.json": matrices},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "AP sums recomputed by harness/toycurve adds"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-007
def load_matrix(ctx_run: str, key: str) -> dict:
    path = os.path.join(ec.READ_EXP_DIR, "runs", ctx_run, "matrices.json")
    return load_json(path)[key]


def run_007(ctx: Ctx):
    """Displacement-rank measurement I: phi-invariant GLV matrices, phi-shift."""
    out = {}
    jobs = [("RUN-ENDO-003", "j0", bits) for bits in ec.BITS_LIST] + \
           [("RUN-ENDO-004", "j1728", bits) for bits in ec.BITS_LIST]
    for src, family, bits in jobs:
        ck = cell_key(family, bits)
        key = f"{ck}:phi_invariant"
        m = load_matrix(src, key)
        r = m["r"]
        B = m["B"]
        pi = ec.block_cyclic_perm(B, r)
        t0 = time.time()
        disp = ec.displacement_rank(m["rows"], B, m["n"], pi)
        resid = ec.commutation_residual(m["rows"], B, pi)
        ctx.guard.check(f"displacement {ck}")
        out[key] = {**disp, **{"commutation_residual_l0": resid["residual_l0"],
                               "commutation_sample": resid["sample_entries"],
                               "r": r, "operator": "phi_shift_block_cyclic",
                               "source_run": src,
                               "measure_seconds": round(time.time() - t0, 3)}}
        ctx.log(f"{key}: alpha={disp['alpha']} min(R,B)={disp['min_R_B']} "
                f"residual_l0={resid['residual_l0']}")
    metrics = {"alpha_per_cell": {k: {"alpha": v["alpha"], "min_R_B": v["min_R_B"],
                                      "alpha_over_min": v["alpha_over_min"],
                                      "R": v["R"], "B": v["B"], "r": v["r"],
                                      "commutation_residual_l0": v["commutation_residual_l0"],
                                      "displacement_nnz": v["displacement_nnz"]}
                                  for k, v in out.items()},
               "median_alpha": float(np.median([v["alpha"] for v in out.values()])),
               "max_commutation_residual_l0": max(v["commutation_residual_l0"]
                                                  for v in out.values())}
    return {"metrics": metrics, "raw": {"measurements": out},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "exact modular Gaussian elimination (int64)"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-008
def run_008(ctx: Ctx):
    """Displacement-rank measurement II: random baselines, phi-ablation,
    negation-orbit generic arm, AP benchmark at 20-bit cells."""
    out = {"random_baseline": {}, "phi_ablation": {}, "negation_generic": {},
           "ap_benchmark": {}}
    r_of_family = {"j0": 3, "j1728": 2, "generic": 2}
    # --- random baselines (9): same block-cyclic operator as the cell's phi arm
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            key = f"{ck}:random_baseline"
            m = load_matrix("RUN-ENDO-005", key)
            B = m["B"]
            pi = ec.block_cyclic_perm(B, r_of_family[family])
            t0 = time.time()
            disp = ec.displacement_rank(m["rows"], B, m["n"], pi)
            ctx.guard.check(f"rand {ck}")
            out["random_baseline"][key] = {
                **disp, "operator": f"block_cyclic_r{r_of_family[family]}_same_as_phi_arm",
                "measure_seconds": round(time.time() - t0, 3)}
            ctx.log(f"{key}: alpha={disp['alpha']} ({disp['alpha_over_min']:.3f} of min)")
    # --- phi-ablation (6 GLV): random (non-phi) shift on phi-invariant matrices
    for src, family, bits in [("RUN-ENDO-003", "j0", b) for b in ec.BITS_LIST] + \
                             [("RUN-ENDO-004", "j1728", b) for b in ec.BITS_LIST]:
        ck = cell_key(family, bits)
        key = f"{ck}:phi_invariant"
        m = load_matrix(src, key)
        B = m["B"]
        seed = int(ec._seed_int(bits, f"ablate:{family}") % (2 ** 31))
        rng = np.random.RandomState(seed)
        pi = rng.permutation(B).astype(np.int64)
        t0 = time.time()
        disp = ec.displacement_rank(m["rows"], B, m["n"], pi)
        ctx.guard.check(f"ablation {ck}")
        out["phi_ablation"][key] = {
            **disp, "operator": "seeded_random_permutation", "operator_seed": seed,
            "measure_seconds": round(time.time() - t0, 3)}
        ctx.log(f"ablation {key}: alpha={disp['alpha']} ({disp['alpha_over_min']:.3f})")
    # --- negation-orbit generic arm (3): block-cyclic r=2 on neg matrices
    for bits in ec.BITS_LIST:
        ck = cell_key("generic", bits)
        key = f"{ck}:negation_orbit_generic"
        m = load_matrix("RUN-ENDO-004", key)
        B = m["B"]
        pi = ec.block_cyclic_perm(B, 2)
        t0 = time.time()
        disp = ec.displacement_rank(m["rows"], B, m["n"], pi)
        resid = ec.commutation_residual(m["rows"], B, pi)
        ctx.guard.check(f"neg {ck}")
        out["negation_generic"][key] = {
            **disp, "operator": "negation_shift_block_cyclic_r2",
            "commutation_residual_l0": resid["residual_l0"],
            "measure_seconds": round(time.time() - t0, 3)}
        ctx.log(f"{key}: alpha={disp['alpha']} ({disp['alpha_over_min']:.3f}) "
                f"residual={resid['residual_l0']}")
    # --- AP benchmark (3 at 20-bit): EV-STR-001 x-translation displacement
    for family in ec.FAMILIES:
        ck = cell_key(family, 20)
        key = f"{ck}:ap_benchmark"
        m = load_matrix("RUN-ENDO-006", key)
        n = m["n"]
        xs = m["column_xs"]
        B = m["B"]
        x_to_idx = {x: i for i, x in enumerate(xs)}
        row_keys = [tuple(k) for k in m["row_keys"]]
        row_set = {rk: i for i, rk in enumerate(row_keys)}
        R = m["R"]
        t0 = time.time()
        # row shift (x_start -> x_start+1, same d) and column shift (x -> x+1)
        row_shift = {}
        for i, (x0, d) in enumerate(row_keys):
            tgt = row_set.get((x0 + 1, d))
            if tgt is not None:
                row_shift[i] = tgt
        col_shift = {}
        for j, x in enumerate(xs):
            j1 = x_to_idx.get(x + 1)
            if j1 is not None:
                col_shift[j] = j1
        D = np.zeros((R, B), dtype=np.int64)
        for i, rr in enumerate(m["rows"]):
            rt = row_shift.get(i)
            if rt is not None:
                for j in rr:
                    D[rt, j] += 1          # (Z_r M)[rt][j]
            for j in rr:
                ct = col_shift.get(j)
                if ct is not None:
                    D[i, ct] -= 1          # (M Z_c)[i][ct]
        D %= n
        alpha_ap = ec.rank_mod(D, n)
        ctx.guard.check(f"ap displacement {ck}")
        # classic (Z, Z^T) displacement, rows in (d, x_start) harvest order
        order = sorted(range(R), key=lambda i: (row_keys[i][1], row_keys[i][0]))
        M = np.zeros((R, B), dtype=np.int64)
        for new_i, old_i in enumerate(order):
            for j in m["rows"][old_i]:
                M[new_i, j] = 1
        D2 = M.copy()
        D2[1:, 1:] = (D2[1:, 1:] - M[:R - 1, :B - 1]) % n
        alpha_classic = ec.rank_mod(D2, n) if R >= 2 else None
        ctx.guard.check(f"ap classic {ck}")
        out["ap_benchmark"][key] = {
            "alpha": int(alpha_ap), "R": R, "B": B, "min_R_B": min(R, B),
            "alpha_over_min": alpha_ap / min(R, B),
            "operator": "x_translation_plus1 (EV-STR-001)",
            "alpha_classic_Z_ZT": None if alpha_classic is None else int(alpha_classic),
            "measure_seconds": round(time.time() - t0, 3)}
        ctx.log(f"{key}: alpha_AP={alpha_ap} ({alpha_ap/min(R,B):.3f}) "
                f"classic={alpha_classic}")
    # medians for control gates
    rand_ratios = [v["alpha_over_min"] for v in out["random_baseline"].values()]
    abl_ratios = [v["alpha_over_min"] for v in out["phi_ablation"].values()]
    metrics = {
        "random_baseline": {k: {"alpha": v["alpha"], "min_R_B": v["min_R_B"],
                                "alpha_over_min": v["alpha_over_min"]}
                            for k, v in out["random_baseline"].items()},
        "random_baseline_median_alpha_over_min": float(np.median(rand_ratios)),
        "phi_ablation": {k: {"alpha": v["alpha"], "min_R_B": v["min_R_B"],
                             "alpha_over_min": v["alpha_over_min"],
                             "operator_seed": v["operator_seed"]}
                         for k, v in out["phi_ablation"].items()},
        "phi_ablation_median_alpha_over_min": float(np.median(abl_ratios)),
        "negation_generic": {k: {"alpha": v["alpha"], "min_R_B": v["min_R_B"],
                                 "alpha_over_min": v["alpha_over_min"],
                                 "commutation_residual_l0": v["commutation_residual_l0"]}
                             for k, v in out["negation_generic"].items()},
        "ap_benchmark": {k: {"alpha": v["alpha"], "min_R_B": v["min_R_B"],
                             "alpha_over_min": v["alpha_over_min"],
                             "alpha_classic_Z_ZT": v["alpha_classic_Z_ZT"]}
                         for k, v in out["ap_benchmark"].items()},
    }
    return {"metrics": metrics, "raw": {"measurements": out},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "exact modular Gaussian elimination (int64)"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-009
def run_009(ctx: Ctx):
    """CTRL-WIEDEMANN-CALIBRATION: verified solves at the largest B per family;
    structured-solve model evaluation alpha^2*B*ceil(log2 B)."""
    # alphas from RUN-ENDO-007 (GLV) and RUN-ENDO-008 (generic negation)
    r007 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-007", "raw.json"))
    r008 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-008", "raw.json"))
    out = {}
    jobs = [("j0", "RUN-ENDO-003", "phi_invariant"),
            ("j1728", "RUN-ENDO-004", "phi_invariant"),
            ("generic", "RUN-ENDO-004", "negation_orbit_generic")]
    for family, src, arm in jobs:
        ck = cell_key(family, 24)
        key = f"{ck}:{arm}"
        m = load_matrix(src, key)
        B = m["B"]
        n = m["n"]
        alpha = r007["metrics"]["alpha_per_cell"][key]["alpha"] if family != "generic" \
            else r008["metrics"]["negation_generic"][key]["alpha"]
        # greedy full-rank square subsystem from the fresh harvested-relation
        # pool (EV-STR-001 precedent); solve on the subsystem with random RHS
        # (full rank => solvable). Raw square-matrix rank recorded as observation.
        square_rank = None
        if m["R"] == B:
            _, square_rank, _ = ec.full_rank_row_selection(m["rows"], B, n)
        pool_rows = [list(r_) for r_ in m.get("surplus_rows", [])]
        sel, pool_rank, pool_size = ec.full_rank_row_selection(pool_rows, B, n)
        ctx.log(f"{key}: square_rank={square_rank}/{B} pool={pool_size} "
                f"subsystem_rank={pool_rank}")
        ctx.guard.check(f"rank-select {ck}")
        seed = int(ec._seed_int(24, f"wiedemann:{family}") % (2 ** 31))
        t0 = time.time()
        if pool_rank == B:
            sub_rows = [pool_rows[i] for i in sel]
            x, info = ec.wiedemann_solve(sub_rows, B, n, seed)
        else:
            # frozen stop rule: report uncalibrated and flagged
            x, info = None, {"converged": False, "attempts": 0, "seconds": 0.0,
                             "verified": False, "nnz": sum(len(r_) for r_ in pool_rows[:B]),
                             "field_ops": {"matvec_field_ops": 0, "dot_field_ops": 0,
                                           "bm_mul_add": 0, "combine_field_ops": 0,
                                           "matvecs": 0, "total_field_ops": 0},
                             "wiedemann_model_ops": 2 * B * B * 3,
                             "entry_status": "resource_exhaustion",
                             "note": f"subsystem rank {pool_rank} < B={B}: "
                                     "uncalibrated and flagged (frozen stop rule)"}
        ctx.guard.check(f"wiedemann {ck}")
        # independent re-verification of the solution by a second code path:
        # numpy matvec Mx must equal the solver's returned b
        indep_verified = None
        if x is not None:
            Mx = np.zeros(B, dtype=np.int64)
            for i, rr in enumerate(m["rows"]):
                acc = 0
                for j in rr:
                    acc += x[j]
                Mx[i] = acc % n
            indep_verified = bool((Mx == np.array([bb % n for bb in info["b"]],
                                                  dtype=np.int64)).all())
        model_ops = info["wiedemann_model_ops"]          # 2*B*nnz = 2*B^2*m
        measured_matvec = info["field_ops"]["matvec_field_ops"]
        measured_total = info["field_ops"]["total_field_ops"]
        calib_matvec = measured_matvec / model_ops
        calib_total = measured_total / model_ops
        m_arity = 3
        structured_ops = (alpha ** 2) * B * math.ceil(math.log2(B)) if alpha >= 0 else None
        wiedemann_model = 2 * B * B * m_arity
        model_ratio = structured_ops / wiedemann_model if structured_ops is not None else None
        calibrated_ratio = (structured_ops / (wiedemann_model * calib_matvec)
                            if structured_ops is not None else None)
        out[key] = {
            "B": B, "n": n, "alpha_used": alpha, "converged": info["converged"],
            "attempts": info["attempts"],
            "solve_seconds": round(info["seconds"], 3),
            "verified_in_solve": info["verified"],
            "independent_recheck": indep_verified,
            "square_matrix_rank": square_rank,
            "square_matrix_rank_deficiency": None if square_rank is None else B - square_rank,
            "subsystem_pool_rows": pool_size,
            "subsystem_rank": pool_rank,
            "subsystem_note": info.get("note"),
            "field_ops": info["field_ops"],
            "wiedemann_model_ops_2B2m": wiedemann_model,
            "measured_over_model_matvec": calib_matvec,
            "measured_over_model_total": calib_total,
            "structured_model_ops_alpha2BlogB": structured_ops,
            "model_ratio_structured_over_wiedemann": model_ratio,
            "calibrated_ratio_under_matvec_calibration": calibrated_ratio,
            "measure_seconds": round(time.time() - t0, 3),
        }
        ctx.log(f"{key}: B={B} alpha={alpha} converged={info['converged']} "
                f"calib={calib_matvec:.3f} ratio={model_ratio:.4g}")
    ratios = [v["measured_over_model_matvec"] for v in out.values() if v["converged"]]
    metrics = {
        "calibrations": {k: {"B": v["B"], "converged": v["converged"],
                             "measured_over_model_matvec": v["measured_over_model_matvec"],
                             "measured_over_model_total": v["measured_over_model_total"],
                             "model_ratio_structured_over_wiedemann":
                                 v["model_ratio_structured_over_wiedemann"],
                             "calibrated_ratio_under_matvec_calibration":
                                 v["calibrated_ratio_under_matvec_calibration"],
                             "solve_seconds": v["solve_seconds"],
                             "square_matrix_rank": v["square_matrix_rank"],
                             "square_matrix_rank_deficiency":
                                 v["square_matrix_rank_deficiency"],
                             "subsystem_pool_rows": v["subsystem_pool_rows"]}
                         for k, v in out.items()},
        "median_measured_over_model_matvec": float(np.median(ratios)) if ratios else None,
        "all_converged": all(v["converged"] for v in out.values()),
        "observation_weight3_matrix_rank": (
            "harvested weight-3 0/1 relation matrices are generically ~4-6% rank "
            "deficient at these sizes (uniform random weight-3 0/1 matrices show "
            "the same deficiency in a control computation, ~6% at R=B, closing to "
            "full rank only near R=3xB); plain Wiedemann on the raw square matrix "
            "hits a singular sequence minpoly (X factor); verified solves "
            "therefore run on greedy full-rank B x B subsystems of freshly "
            "harvested relations (EV-STR-001 precedent), solution verified by "
            "M*x == b; raw square-matrix ranks recorded"),
    }
    return {"metrics": metrics, "raw": {"solves": out},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "in-solve verification matvec + numpy recheck"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-010
def run_010(ctx: Ctx):
    """Relation-density penalty: hit rates, Wilson CIs, supply ratios, penalty
    versus B/alpha threshold."""
    r003 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-003", "raw.json"))
    r004 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-004", "raw.json"))
    r005 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-005", "raw.json"))
    r006 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-006", "raw.json"))
    r007 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-007", "raw.json"))
    r008 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-008", "raw.json"))

    def hit(coll, key):
        return coll["raw"]["cells"][key]["hit_test"]

    alpha_phi = r007["metrics"]["alpha_per_cell"]
    alpha_neg = r008["metrics"]["negation_generic"]
    cells = {}
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            skey = f"{ck}:phi_invariant" if family != "generic" \
                else f"{ck}:negation_orbit_generic"
            rkey = f"{ck}:random_baseline"
            scoll = r003 if family == "j0" else r004
            s_hit = hit(scoll, skey)
            r_hit = hit(r005, rkey)
            alpha = alpha_phi[skey]["alpha"] if family != "generic" \
                else alpha_neg[skey]["alpha"]
            B = alpha_phi[skey]["B"] if family != "generic" \
                else alpha_neg[skey]["min_R_B"]
            s_rate = s_hit["hit_rate"]
            r_rate = r_hit["hit_rate"]
            penalty = (r_rate / s_rate) if s_rate else None
            threshold = (B / alpha) if alpha else None  # alpha=0 -> infinite threshold
            cells[ck] = {
                "structured_arm": skey, "structured_hit_rate": s_rate,
                "structured_wilson95": s_hit.get("wilson95"),
                "random_hit_rate": r_rate, "random_wilson95": r_hit.get("wilson95"),
                "n_tests_per_arm": s_hit["n_targets"],
                "penalty_random_over_structured": penalty,
                "alpha": alpha, "B": B,
                "B_over_alpha_threshold": threshold,
                "threshold_infinite_because_alpha_zero": alpha == 0,
                "penalty_below_threshold": (penalty < threshold) if
                    (penalty is not None and threshold is not None) else
                    (True if alpha == 0 and penalty is not None else None),
                "structured_supply": scoll["raw"]["cells"][skey]["pair_table"],
                "random_supply": r005["raw"]["cells"][rkey]["pair_table"],
            }
    # AP cells vs random at 20 bits
    ap_cells = {}
    for family in ec.FAMILIES:
        ck = cell_key(family, 20)
        akey = f"{ck}:ap_benchmark"
        rkey = f"{ck}:random_baseline"
        a = r006["raw"]["cells"][akey]
        r_rate = hit(r005, rkey)["hit_rate"]
        ap_rate = a["hit_test"]["xwise_hit_rate"]
        ap_cells[ck] = {
            "ap_xwise_hit_rate": ap_rate,
            "ap_xwise_wilson95": a["hit_test"]["xwise_wilson95"],
            "random_hit_rate_same_cell": r_rate,
            "ap_supply": a["ap_supply"],
            "supply_ratio_over_B": a["supply_ratio_supply_over_B"],
            "yield_penalty_C_B_3_over_supply": a["yield_penalty_C_B_3_over_supply"],
            "ap_vs_random_hit_rate_gap": (r_rate / ap_rate) if ap_rate else None,
        }
    glv_penalties = [cells[cell_key(f, b)]["penalty_random_over_structured"]
                     for f in ("j0", "j1728") for b in ec.BITS_LIST
                     if cells[cell_key(f, b)]["penalty_random_over_structured"] is not None]
    metrics = {
        "cells": cells, "ap_cells": ap_cells,
        "median_glv_penalty": float(np.median(glv_penalties)) if glv_penalties else None,
        "n_glv_cells_penalty_below_threshold": sum(
            1 for f in ("j0", "j1728") for b in ec.BITS_LIST
            if cells[cell_key(f, b)]["penalty_below_threshold"] is True),
    }
    return {"metrics": metrics, "raw": {"cells": cells, "ap_cells": ap_cells},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "rates recomputed from raw per-target records"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-011
def run_011(ctx: Ctx):
    """CTRL-MATCHED-RHO-BSGS baselines; fully-charged totals per arm."""
    fv1 = ec.verify_frozen_instances()
    if not fv1["content_sha256_ok"]:
        return {"metrics": {"frozen_verification": fv1}, "raw": {}, "valid": False,
                "invalid_reason": "frozen-instances SHA-256 mismatch",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
                "status": "completed_invalid", "seed_record": ec.SEEDS}
    inst_doc = ec.read_yaml(ec.FROZEN_INSTANCES)
    r010 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-010", "raw.json"))
    r009 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-009", "raw.json"))
    calib = r009["metrics"]["median_measured_over_model_matvec"]
    coll = {}
    for rid in ("RUN-ENDO-003", "RUN-ENDO-004", "RUN-ENDO-005"):
        coll[rid] = load_json(os.path.join(ec.READ_EXP_DIR, "runs", rid, "raw.json"))
    out = {}
    all_certs_ok = True
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            inst = ec.get_cell(inst_doc, family, bits)
            E = ec.EllipticCurve(inst["p"], inst["a"], inst["b"])
            targets = ec.make_targets(inst, ec.N_HIT_TARGETS, f"hit:{ck}")
            t0 = time.time()
            rho_results = []
            for t in targets:
                rr = ec.rho_solve_target(inst, t)
                rho_results.append(rr)
                if rr.get("certificate") and not rr["certificate"]["verified"]:
                    all_certs_ok = False
                ctx.guard.check(f"rho {ck}")
            solved = [r for r in rho_results if r["solved"]]
            rho_median = float(np.median([r["total_group_operations"] for r in solved])) \
                if solved else None
            bsgs = ec.bsgs_solve(E, tuple(inst["P"]), tuple(inst["Q"]), inst["n"])
            ctx.guard.check(f"bsgs {ck}")
            out[ck] = {
                "rho": {"n_targets": len(rho_results), "n_solved": len(solved),
                        "median_total_group_operations": rho_median,
                        "all_certificates_verified": all(
                            r.get("certificate", {}).get("verified", True)
                            for r in rho_results),
                        "seconds": round(time.time() - t0, 3)},
                "bsgs": bsgs,
                "per_target_rho": [{"i": r["target_index"], "solved": r["solved"],
                                    "total_ops": r["total_group_operations"],
                                    "verified": r.get("verified_recompute"),
                                    "crosscheck": r.get("crosscheck_ab")}
                                   for r in rho_results],
            }
            ctx.log(f"{ck}: rho median={rho_median} solved={len(solved)}/"
                    f"{len(rho_results)} bsgs_ops={bsgs['group_operations']}")
    # fully-charged totals per arm
    charged = {}
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            pen_cell = r010["metrics"]["cells"][ck]
            rho_med = out[ck]["rho"]["median_total_group_operations"]
            arms = {}
            for arm_label, src in (("structured", "RUN-ENDO-003" if family == "j0"
                                    else "RUN-ENDO-004"),
                                   ("random_baseline", "RUN-ENDO-005")):
                skey = (f"{ck}:phi_invariant" if (family != "generic" and arm_label == "structured")
                        else f"{ck}:negation_orbit_generic" if arm_label == "structured"
                        else f"{ck}:random_baseline")
                cell = coll[src]["raw"]["cells"][skey]
                B = cell["n_columns"]
                evals = cell["evals"]["total_tuple_evaluations"]
                penalty = (pen_cell["penalty_random_over_structured"]
                           if arm_label == "structured" else 1.0)
                alpha = pen_cell["alpha"] if arm_label == "structured" else None
                s_rel = evals * 1.0   # 1 group op per tuple evaluation (conservative)
                s_rel_adj = s_rel * (penalty if penalty else 1.0)
                la_field_ops = 2 * B * B * 3 * (calib if calib else 1.0)
                s_la = la_field_ops / ec.MULS_PER_EC_ADD
                t_desc = B * 1.0      # B probes per target, 1 group op each
                t_verify = 3 + 1.5 * math.log2(inst["n"])
                total = s_rel_adj + s_la + t_desc + t_verify
                arms[arm_label] = {
                    "S_rel_group_ops": s_rel, "penalty_factor": penalty,
                    "S_rel_penalty_adjusted": s_rel_adj,
                    "S_LA_group_ops_calibrated": s_la,
                    "T_desc_group_ops": t_desc, "T_verify_group_ops": t_verify,
                    "fully_charged_total_group_ops": total,
                    "alpha": alpha,
                    "rho_median_per_target": rho_med,
                    "total_over_rho": (total / rho_med) if rho_med else None,
                }
            charged[ck] = arms
    metrics = {
        "rho_baselines": {ck: out[ck]["rho"] for ck in out},
        "bsgs_baselines": {ck: {"group_operations": out[ck]["bsgs"]["group_operations"],
                                "table_entries": out[ck]["bsgs"]["table_entries"],
                                "solved": out[ck]["bsgs"]["solved"]} for ck in out},
        "fully_charged_per_arm": charged,
        "all_rho_certificates_verified": all_certs_ok,
        "wiedemann_calibration_used": calib,
        "accounting_formulas": {
            "S_rel": "total_tuple_evaluations * 1 group op (x-only evals charged as full EC adds: conservative over-estimate)",
            "penalty_adjustment": "S_rel * measured penalty (structured arms); 1.0 random",
            "S_LA": "2*B^2*m * median measured/model calibration / 19 muls-per-EC-add",
            "T_desc": "B probes per target * 1 group op",
            "T_verify": "3 EC adds + 1.5*log2(n) EC adds",
            "units": "group-operation equivalents; F_n op = 1 F_p mul (EV-STR-001 charging)"},
    }
    return {"metrics": metrics, "raw": {"baselines": out, "fully_charged": charged},
            "valid": all_certs_ok,
            "invalid_reason": None if all_certs_ok else "rho certificate failure",
            "certificate": {"kind": "discrete_log", "verified": all_certs_ok,
                            "verifier": "independent-recompute + (a+bk) cross-check"},
            "status": "completed_valid" if all_certs_ok else "completed_invalid",
            "seed_record": ec.SEEDS}


# ---------------------------------------------------------------- RUN-ENDO-012
def run_012(ctx: Ctx):
    """Aggregation and analysis: per-instance alpha separation, penalty table,
    model ratios, two-claim decision matrix, analysis.md (observations only)."""
    r007 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-007", "raw.json"))
    r008 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-008", "raw.json"))
    r009 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-009", "raw.json"))
    r010 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-010", "raw.json"))
    r011 = load_json(os.path.join(ec.READ_EXP_DIR, "runs", "RUN-ENDO-011", "raw.json"))

    alpha_phi = r007["metrics"]["alpha_per_cell"]
    rand = r008["metrics"]["random_baseline"]
    abl = r008["metrics"]["phi_ablation"]
    neg = r008["metrics"]["negation_generic"]
    ap = r008["metrics"]["ap_benchmark"]
    pen = r010["metrics"]
    cal = r009["metrics"]
    fc = r011["metrics"]

    # --- per-instance alpha separation table (6 GLV instances)
    separation = {}
    for family, r in (("j0", 3), ("j1728", 2)):
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            skey = f"{ck}:phi_invariant"
            a_phi = alpha_phi[skey]["alpha"]
            minRB = alpha_phi[skey]["min_R_B"]
            a_rand = rand[f"{ck}:random_baseline"]["alpha"]
            resid = alpha_phi[skey]["commutation_residual_l0"]
            separation[ck] = {
                "r": r, "alpha_phi": a_phi, "alpha_rand": a_rand,
                "min_R_B": minRB, "alpha_phi_le_r": a_phi <= r,
                "separation_complete": (a_phi <= r < 0.5 * minRB <= a_rand),
                "commutation_residual_l0": resid,
                "alpha_rand_over_min": a_rand / minRB,
            }
    n_alpha_le_r = sum(1 for v in separation.values() if v["alpha_phi_le_r"])
    n_sep_complete = sum(1 for v in separation.values() if v["separation_complete"])
    fams_with = {f: any(separation[cell_key(f, b)]["alpha_phi_le_r"]
                        for b in ec.BITS_LIST) for f in ("j0", "j1728")}

    # --- largest-B model ratios (calibrated and uncalibrated)
    model_rows = {}
    for family, arm in (("j0", "phi_invariant"), ("j1728", "phi_invariant"),
                        ("generic", "negation_orbit_generic")):
        key = f"{family}-24:{arm}"
        c = cal["calibrations"][key]
        model_rows[key] = c

    decision_matrix = {
        "C1_clauses": {
            "alpha_phi<=r on >=4/6 GLV instances": {
                "measured": f"{n_alpha_le_r}/6", "threshold": ">=4/6"},
            "at least one instance of each family with alpha<=r": {
                "measured": fams_with, "threshold": "both families"},
            "complete separation alpha<=r<0.5*min(R,B)<=alpha_rand on those instances": {
                "measured": f"{n_sep_complete}/6", "threshold": ">=4/6"},
            "zero unexplained commutation residuals": {
                "measured": max(v["commutation_residual_l0"] for v in separation.values()),
                "threshold": 0},
            "generic arm alpha_neg<=2": {
                "measured": {k: v["alpha"] for k, v in neg.items()},
                "threshold": "<=2 (prediction, not a gate)"},
        },
        "C2_clauses": {
            "median GLV penalty < B/alpha": {
                "measured": pen["median_glv_penalty"],
                "per_cell": {ck: {"penalty": pen["cells"][ck]["penalty_random_over_structured"],
                                  "B_over_alpha": pen["cells"][ck]["B_over_alpha_threshold"],
                                  "below": pen["cells"][ck]["penalty_below_threshold"]}
                             for ck in pen["cells"] if not ck.startswith("generic")},
                "threshold": "penalty < B/alpha per cell"},
            "calibrated model ratio <= 0.5 at largest B on >=4/6 GLV": {
                "measured": {k: model_rows[k]["calibrated_ratio_under_matvec_calibration"]
                             for k in model_rows if not k.startswith("generic")},
                "threshold": "<=0.5"},
        },
        "control_gates": {
            "CTRL-RANDOM-BASELINE median alpha_rand/min(R,B)>=0.5": {
                "measured": r008["metrics"]["random_baseline_median_alpha_over_min"]},
            "CTRL-PHI-ABLATION median ablated/min>=0.5": {
                "measured": r008["metrics"]["phi_ablation_median_alpha_over_min"]},
            "CTRL-AP-BENCHMARK alpha_AP>=0.5*min + supply-side penalty": {
                "measured": {k: {"alpha_over_min": ap[k]["alpha_over_min"],
                                 "yield_penalty": pen["ap_cells"][k.replace(':ap_benchmark', '')]["yield_penalty_C_B_3_over_supply"]}
                             for k in ap}},
            "CTRL-NON-GLV-ARM executed and comparable": {
                "measured": {k: v["alpha"] for k, v in neg.items()}},
            "CTRL-WIEDEMANN-CALIBRATION median in [0.5,2]": {
                "measured": cal["median_measured_over_model_matvec"]},
            "CTRL-MATCHED-RHO-BSGS measured": {
                "measured": "rho/BSGS medians recorded per cell (see RUN-ENDO-011)"},
        },
    }

    # --- analysis.md (observation / comparison / limitation; no conclusion)
    lines = []
    lines.append("# EXP-ENDO-001 analysis (executor observations only)\n")
    lines.append("Protocol: experiments/EXP-ENDO-001/specification.yaml (frozen v1). "
                 "12 planned runs executed under TASK-20260727-002. This document "
                 "reports measurements and comparisons against the frozen thresholds "
                 "only; it makes no support/refute claim about H-ENDO-001 (that "
                 "transition belongs to the Coordinator).\n")
    lines.append("## 1 Observation\n")
    lines.append("### Displacement rank alpha per instance/arm (over F_n, exact GE)\n")
    lines.append("| cell | arm | R | B | alpha | alpha/min(R,B) | residual ||M Phi-Phi M||_0 |")
    lines.append("|---|---|---|---|---|---|---|")
    for family in ec.FAMILIES:
        for bits in ec.BITS_LIST:
            ck = cell_key(family, bits)
            skey = f"{ck}:phi_invariant" if family != "generic" else f"{ck}:negation_orbit_generic"
            src = alpha_phi if family != "generic" else neg
            v = src[skey]
            resid = v.get("commutation_residual_l0", 0)
            vR = v.get("R", v.get("min_R_B"))
            vB = v.get("B", v.get("min_R_B"))
            lines.append(f"| {skey} | structured | {vR} | {vB} | {v['alpha']} "
                         f"| {v['alpha_over_min']:.4f} | {resid} |")
            rv = rand[f"{ck}:random_baseline"]
            lines.append(f"| {ck}:random_baseline | random | {rv['min_R_B']} | {rv['min_R_B']} "
                         f"| {rv['alpha']} | {rv['alpha_over_min']:.4f} | - |")
    for k, v in abl.items():
        lines.append(f"| {k} (ablated) | phi-matrix, random shift | {v['min_R_B']} | "
                     f"{v['min_R_B']} | {v['alpha']} | {v['alpha_over_min']:.4f} | - |")
    for k, v in ap.items():
        lines.append(f"| {k} | AP (EV-STR-001 protocol) | - | {v['min_R_B']} | {v['alpha']} "
                     f"| {v['alpha_over_min']:.4f} | - |")
    lines.append("")
    lines.append("### Hit rates and relation-density penalty (200 decomposition tests/arm/cell)\n")
    lines.append("| cell | structured rate [Wilson95] | random rate [Wilson95] | penalty rand/phi | B/alpha threshold |")
    lines.append("|---|---|---|---|---|")
    for ck, v in pen["cells"].items():
        thr = v["B_over_alpha_threshold"]
        thr_s = f"{thr:.1f}" if thr is not None else "infinite (alpha=0)"
        lines.append(f"| {ck} | {v['structured_hit_rate']:.4f} {v['structured_wilson95']} "
                     f"| {v['random_hit_rate']:.4f} {v['random_wilson95']} "
                     f"| {v['penalty_random_over_structured']:.4f} | {thr_s} |")
    lines.append("")
    lines.append("### AP benchmark (20-bit cells, EV-STR-001 protocol)\n")
    for ck, v in pen["ap_cells"].items():
        lines.append(f"- {ck}: AP supply {v['ap_supply']} (supply/B "
                     f"{v['supply_ratio_over_B']:.2f}), yield penalty C(B,3)/supply "
                     f"{v['yield_penalty_C_B_3_over_supply']:.1f}, x-wise hit rate "
                     f"{v['ap_xwise_hit_rate']:.4f} vs random {v['random_hit_rate_same_cell']:.4f} "
                     f"(gap {v['ap_vs_random_hit_rate_gap']:.1f}x)")
    lines.append("")
    lines.append("### Wiedemann calibration (largest B per family, verified solves)\n")
    for k, v in cal["calibrations"].items():
        lines.append(f"- {k}: B={v['B']}, converged={v['converged']}, "
                     f"measured/model (matvec ops)={v['measured_over_model_matvec']:.3f}, "
                     f"(total ops)={v['measured_over_model_total']:.3f}, "
                     f"structured/Wiedemann model ratio={v['model_ratio_structured_over_wiedemann']:.4g}, "
                     f"calibrated={v['calibrated_ratio_under_matvec_calibration']:.4g}")
    lines.append("")
    lines.append("### Fully-charged totals vs measured rho (group-operation equivalents)\n")
    for ck, arms in fc["fully_charged_per_arm"].items():
        for label, v in arms.items():
            lines.append(f"- {ck} {label}: total {v['fully_charged_total_group_ops']:.3g} "
                         f"group-ops vs rho median {v['rho_median_per_target']:.0f} "
                         f"(ratio {v['total_over_rho']:.3g})")
    lines.append("")
    lines.append("## 2 Comparison vs frozen thresholds (measured values only)\n")
    lines.append("```json")
    lines.append(json.dumps(decision_matrix, indent=1, default=str))
    lines.append("```\n")
    lines.append("## 3 Limitation\n")
    lines.append("- Toy scale only (16-24-bit prime fields, B <= ~4100, GLV families "
                 "j=0/j=1728 + one generic arm). No statement above claim_tier toy; "
                 "nothing is implied for crypto-scale or generic curves.\n"
                 "- The structured-solve advantage is model-evaluated "
                 "(alpha^2*B*ceil(log2 B)) with the Wiedemann side calibrated by "
                 "verified solves; it is not a measured superfast solve.\n"
                 "- Relation matrices are assembled from enumeration-harvested "
                 "relations with orbit closure by construction; the displacement "
                 "measurement verifies the invariance exactly (it does not by itself "
                 "prove the mechanism at other scales).\n"
                 "- Hit rates near 1.0 on both structured and random arms at these "
                 "sizes make the penalty measurement a near-census of the tested "
                 "distribution; wider-aperture regimes are untested.\n")
    analysis_path = os.path.join(ec.READ_EXP_DIR, "analysis.md")
    with open(analysis_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    metrics = {"separation": separation,
               "n_glv_alpha_le_r": n_alpha_le_r,
               "n_glv_separation_complete": n_sep_complete,
               "families_with_alpha_le_r": fams_with,
               "decision_matrix": decision_matrix,
               "analysis_md": "experiments/EXP-ENDO-001/analysis.md"}
    return {"metrics": metrics,
            "raw": {"decision_matrix": decision_matrix},
            "valid": True, "invalid_reason": None,
            "certificate": {"kind": "none", "verified": None,
                            "verifier": "tables regenerated from run raw.json files"},
            "status": "completed_valid", "seed_record": ec.SEEDS}


RUN_FUNCTIONS = {
    "RUN-ENDO-001": run_001, "RUN-ENDO-002": run_002, "RUN-ENDO-003": run_003,
    "RUN-ENDO-004": run_004, "RUN-ENDO-005": run_005, "RUN-ENDO-006": run_006,
    "RUN-ENDO-007": run_007, "RUN-ENDO-008": run_008, "RUN-ENDO-009": run_009,
    "RUN-ENDO-010": run_010, "RUN-ENDO-011": run_011, "RUN-ENDO-012": run_012,
}

PURPOSES = {
    "RUN-ENDO-001": "Instance generation and freeze (9 curves, GLV filters, seeds), SHA-256",
    "RUN-ENDO-002": "Factor-base construction for all four arms; orbit-closure audit; freeze",
    "RUN-ENDO-003": "Relation collection on phi-invariant bases, j=0 cells",
    "RUN-ENDO-004": "Relation collection on phi-invariant j=1728 cells and generic negation cells",
    "RUN-ENDO-005": "Relation collection on random-baseline bases, all cells",
    "RUN-ENDO-006": "Relation collection on AP-benchmark bases, 20-bit cells (EV-STR-001)",
    "RUN-ENDO-007": "Displacement-rank measurement I: phi-invariant GLV matrices",
    "RUN-ENDO-008": "Displacement-rank measurement II: random, ablation, negation, AP",
    "RUN-ENDO-009": "CTRL-WIEDEMANN-CALIBRATION verified solves + structured model evaluation",
    "RUN-ENDO-010": "Relation-density penalty computation with Wilson intervals",
    "RUN-ENDO-011": "CTRL-MATCHED-RHO-BSGS baselines; fully-charged totals",
    "RUN-ENDO-012": "Aggregation and analysis; analysis.md",
}


class Tee(io.TextIOBase):
    def __init__(self, stream):
        self.stream = stream
        self.buf = io.StringIO()

    def write(self, s):
        self.stream.write(s)
        self.buf.write(s)
        return len(s)

    def flush(self):
        self.stream.flush()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True, choices=sorted(RUN_FUNCTIONS))
    ap.add_argument("--out-root", default=None,
                    help="scratch output root (smoke tests only; recorded in command)")
    args = ap.parse_args()
    run_id = args.run_id
    out_root = args.out_root
    command = f"python3 experiments/EXP-ENDO-001/code/run_ENDO.py --run-id {run_id}" + \
              (f" --out-root {out_root}" if out_root else "")
    if out_root:
        ec.FROZEN_INSTANCES = os.path.join(out_root, "frozen-instances.yaml")
        ec.FROZEN_FACTORBASES = os.path.join(out_root, "frozen-factorbases.yaml")
        ec.READ_EXP_DIR = out_root
    ctx = Ctx(run_id, out_root)
    started = time.time()
    tee_out, tee_err = Tee(sys.stdout), Tee(sys.stderr)
    sys.stdout, sys.stderr = tee_out, tee_err
    status, valid, invalid_reason = "failed_implementation", False, None
    metrics, raw, summary_metrics = {}, {}, {}
    certificate = {"kind": "none", "verified": None, "verifier": None}
    side_files = {}
    seed_record = None
    try:
        res = RUN_FUNCTIONS[run_id](ctx)
        status = res.get("status", "completed_valid")
        metrics = res["metrics"]
        raw = res.get("raw", {})
        summary_metrics = metrics
        valid = res.get("valid", True)
        invalid_reason = res.get("invalid_reason")
        certificate = res.get("certificate", certificate)
        side_files = res.get("side_files", {})
        seed_record = res.get("seed_record")
    except ec.ResourceExhaustion as e:
        status = "resource_exhaustion"
        invalid_reason = str(e)
        valid = False
        ctx.log(f"RESOURCE EXHAUSTION: {e}")
    except Exception:
        status = "failed_implementation"
        invalid_reason = "unexpected exception (see stderr)"
        valid = False
        traceback.print_exc()
    finally:
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
    finished = time.time()
    rss = ec.peak_rss_bytes()
    if rss > ec.RSS_LIMIT_BYTES and status != "resource_exhaustion":
        status = "resource_exhaustion"
        valid = False
        invalid_reason = (invalid_reason or "") + \
            f"; post-hoc peak RSS {rss} > 4 GB cap"
        ctx.anomalies.append(f"post-hoc memory cap exceeded: peak RSS {rss} bytes")
    raw["_stdout"] = tee_out.buf.getvalue()
    raw["_stderr"] = tee_err.buf.getvalue()
    params = {"run_purpose": PURPOSES[run_id],
              "budget": {"wall_clock_seconds_per_run": 1800,
                         "memory_gb": 4, "self_cap_seconds": ec.RUN_SELF_CAP_S},
              "frozen_protocol": "experiments/EXP-ENDO-001/specification.yaml v1"}
    run_dir = ec.write_run_record(
        run_id, status, command, started, finished, seed_record, params,
        metrics, raw, summary_metrics, valid, invalid_reason, certificate,
        ctx.deviations, ctx.anomalies, out_root=out_root)
    for name, obj in side_files.items():
        write_side(run_dir, name, obj)
    print(f"[{run_id}] terminal status: {status}; record at {run_dir}", flush=True)
    return 0 if status in ("completed_valid",) else 1


if __name__ == "__main__":
    raise SystemExit(main())
