#!/usr/bin/env python3
"""Driver for EXP-CERTBIN-3f06d1 (phases 1-9; phase 0 is cprov.py + selftest.py).

Copied from EXP-CERTBIN-4e92d7/impl/driver.py and generalised to three cells
(R1, R2, R3) and the v2 phases (impl-provenance.json).

  main invocation        : phases 1-6 for R1, R2, R3 (checkpointed per cell,
                           phase, family and D); then, if phase 7 is complete,
                           phase 8 (PS0' certificate extraction + cells.json);
                           then, once ps0prime-verification.json exists (the
                           verifier, a separate process), phase 9.
  --phase determinism    : phase 7 in a SEPARATE process (C-DET).
  --resume               : continue from the last complete checkpoint.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import resource
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from gf2n import TableField  # noqa: E402
from macaulay import MacaulayShape, descended_E, affine_combine, affine_basis, NEQ  # noqa: E402
from families import run_phase1_cell, E_from_hex  # noqa: E402
from engine import process_family, make_ref  # noqa: E402
from elim import eliminate, column_pass  # noqa: E402
from vspace import VBasis, affine_hull  # noqa: E402

EXP_ID = "EXP-CERTBIN-3f06d1"
MEM_LIMIT = 4 * 1024 ** 3
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CELLS = ["R1", "R2", "R3"]
STAGE1_RECEIPT = "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json"

# Counts transcribed from the frozen specification text (version 1).
SPEC_COUNTS = {"test_targets": 1000, "planted_targets": 200, "rev_targets": 200, "reference_scan_max_draws": 500,
               "references_unsat": 3, "references_sat": 2, "D": [3, 4], "modal_window": [1, 100],
               "modal_scored": [101, 1000], "bootstrap_resamples": 10000, "c_aff_direct_replay_targets": 20,
               "c_det_targets": 200, "ps0prime_certificates_per_cell": 30, "ts1r_min_survivors": 100,
               "maximum_workers": 1}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jdefault(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))


class Run:
    def __init__(self, args):
        self.args = args
        self.out = os.path.abspath(args.out)
        self.ck = os.path.join(self.out, "checkpoint")
        os.makedirs(self.ck, exist_ok=True)
        self.t0 = time.time()

    def log(self, msg):
        print(f"[{now()}] {msg}", flush=True)

    def ck_path(self, name):
        return os.path.join(self.ck, name + ".json.gz")

    def ck_exists(self, name):
        return os.path.exists(self.ck_path(name))

    def ck_save(self, name, obj):
        p = self.ck_path(name)
        if os.path.exists(p):
            raise RuntimeError(f"checkpoint {p} exists; refusing to overwrite")
        tmp = p + ".tmp"
        with gzip.open(tmp, "wt") as f:
            json.dump(obj, f, default=jdefault, separators=(",", ":"))
        os.replace(tmp, p)

    def ck_load(self, name):
        with gzip.open(self.ck_path(name), "rt") as f:
            return json.load(f)

    def invocation(self, rec):
        with open(os.path.join(self.ck, "invocations.jsonl"), "a") as f:
            f.write(json.dumps(rec, default=jdefault) + "\n")


def git_state():
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True).stdout.splitlines()
        return {"commit": head, "dirty": bool(st), "status_porcelain": st}
    except Exception as e:  # recorded, not hidden
        return {"error": repr(e)}


def verify_plan(spec_text, spec, plan, args):
    errs = []
    ex = spec["experiment"]
    table = ex["seeds"]["table"]
    for cell in CELLS:
        want = table[cell]
        got = plan["cells"][cell]["seeds"]
        if got != want:
            errs.append(f"{cell} seeds: plan {got} != spec {want}")
    if plan.get("S_selftest") != ex["seeds"]["S_selftest"]:
        errs.append("S_selftest differs")
    for k, v in SPEC_COUNTS.items():
        if plan["counts"].get(k) != v:
            errs.append(f"count {k}: plan {plan['counts'].get(k)} != spec {v}")
    if plan.get("spec_sha256") != hashlib.sha256(spec_text).hexdigest():
        errs.append("plan spec_sha256 does not match the specification file")
    if ex["status"] != "approved" or not ex.get("approved_by"):
        errs.append("specification not approved")
    if plan.get("run_id") != args.run_id:
        errs.append("plan run_id != --run-id")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--stage1-run", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--phase", default="main", choices=["main", "determinism"])
    ap.add_argument("--dev", action="store_true",
                    help="development mode: non-frozen plan allowed; output must be OUTSIDE the repository")
    args = ap.parse_args()

    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    spec_text = open(args.spec, "rb").read()
    spec = yaml.safe_load(spec_text)
    plan = json.load(open(args.plan))
    out = os.path.abspath(args.out)
    if args.dev:
        if out.startswith(REPO + os.sep):
            print("--dev output must be outside the repository", file=sys.stderr)
            return 2
        if not plan.get("dev"):
            print("--dev requires a development plan", file=sys.stderr)
            return 2
    else:
        if plan.get("dev"):
            print("development plan refused without --dev", file=sys.stderr)
            return 2
        errs = verify_plan(spec_text, spec, plan, args)
        if errs:
            print("specification/plan mismatch: " + "; ".join(errs), file=sys.stderr)
            return 2
        want = os.path.join(REPO, "experiments", EXP_ID, "runs", args.run_id)
        if out != want:
            print(f"--out must be {want}", file=sys.stderr)
            return 2

    run = Run(args)
    inv = {"argv": sys.argv, "phase": args.phase, "resume": args.resume, "pid": os.getpid(), "ppid": os.getppid(),
           "started_at": now(), "git": git_state(), "rlimit_as_bytes": MEM_LIMIT,
           "python": sys.version, "numpy": np.__version__}
    run.invocation({"event": "start", **inv})
    try:
        if args.phase == "determinism":
            rc = phase7(run, plan)
        else:
            rc = main_phases(run, plan, spec, spec_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        run.invocation({"event": "crash", "pid": os.getpid(), "at": now(), "error": repr(e),
                        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024})
        return 3
    ru = resource.getrusage(resource.RUSAGE_SELF)
    run.invocation({"event": "end", "pid": os.getpid(), "at": now(), "rc": rc,
                    "wall_seconds": time.time() - run.t0, "peak_rss_bytes": ru.ru_maxrss * 1024,
                    "cpu_seconds": ru.ru_utime + ru.ru_stime})
    return rc


# ---------------------------------------------------------------------------
def setup(plan):
    F = TableField()
    return {"F": F, "shapes": {D: MacaulayShape(D) for D in plan["counts"]["D"]}}


def unit_meta(t_start, t_end, wall):
    return {"started_at": t_start, "finished_at": t_end, "wall_seconds": wall,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "pid": os.getpid()}


def cell_config(plan, cell, stage1_run):
    c = dict(plan["cells"][cell])
    if c["curve_mode"] == "stage1":
        rec = json.load(open(os.path.join(REPO, STAGE1_RECEIPT)))
        rel = os.path.relpath(os.path.join(os.path.abspath(stage1_run), "curve.json"), REPO)
        c["stage1_curve_json"] = os.path.join(os.path.abspath(stage1_run), "curve.json")
        c["stage1_curve_sha256"] = rec["path_sha256"][rel]
    c["cell"] = cell
    return c


def load_V(P1):
    return VBasis(P1["V"]["basis_b0_to_b8"], P1["V"]["label"])


def main_phases(run, plan, spec, spec_text):
    selftest_p = os.path.join(run.out, "selftest.json")
    cprov_p = os.path.join(run.out, "cprov.json")
    if not os.path.exists(cprov_p) or not json.load(open(cprov_p)).get("pass"):
        run.log("C-PROV missing or failed: stopping before any frozen stream is drawn (SR-2, INV-2)")
        return 4
    if not os.path.exists(selftest_p):
        run.log("phase 0 missing: selftest.json not found; stopping before any draw (SR-2)")
        return 4
    st = json.load(open(selftest_p))
    if not st.get("all_pass"):
        run.log("phase 0 FAILED (C-SELF/C-FIX); stopping before phase 1 (SR-2, INV-1)")
        return 4
    existing = [f for f in os.listdir(run.ck) if f.endswith(".json.gz")]
    if existing and not run.args.resume:
        run.log(f"checkpoints exist ({len(existing)}); use --resume")
        return 5
    ctx = setup(plan)
    F = ctx["F"]
    for D, (R, C) in ((3, (323, 988)), (4, (2924, 4048))):
        S = ctx["shapes"][D]
        if (S.R, S.C) != (R, C):
            run.log(f"C-FIX mismatch at D={D}: {(S.R, S.C)}; stop (INV-1)")
            return 4
    Ds = plan["counts"]["D"]
    NREV = plan["counts"]["rev_targets"]

    for cell in CELLS:
        cfg = cell_config(plan, cell, run.args.stage1_run)
        name1 = f"p1-{cell}-instances"
        if not run.ck_exists(name1):
            if not run.ck_exists("first-draw"):
                run.ck_save("first-draw", {"at": now(), "pid": os.getpid(), "cell": cell})
            ts = now()
            t = time.time()
            run.log(f"phase 1 [{cell}]: curve / V, points, per-cell C-SELF, C-TR, references, targets, oracles, witnesses")
            from selftest import cell_selftest
            P1, _cls = run_phase1_cell(F, cfg, plan["counts"], run.log, cell_selftest)
            P1["_meta"] = unit_meta(ts, now(), time.time() - t)
            run.ck_save(name1, P1)
        P1 = run.ck_load(name1)
        if P1.get("stopped"):
            run.log(f"[{cell}] phase 1 stopped: {P1['stopped']}; the run stops (SR-2)")
            return 4
        V = load_V(P1)
        B = P1["curve"]["B"]
        E0, Ej = affine_basis(F, B, V.basis)
        planes_curve = [E0] + Ej

        def build_curve(inst, B=B, V=V):
            return descended_E(F, B, inst["x_R"], V.basis)

        fs3_live = {}

        def get_fs3_live(D, cell=cell, P1=P1, planes_curve=planes_curve, build_curve=build_curve, fs3_live=fs3_live):
            if D in fs3_live:
                return fs3_live[D]
            unit = run.ck_load(f"p2-{cell}-F-S3-D{D}")
            S = ctx["shapes"][D]
            planesM = np.stack([S.build(x) for x in planes_curve])
            refs = []
            for inst in P1["F-S3"]["refs"]:
                refs.append(make_ref(S, S.build(build_curve(inst)), inst, inst["selected_as"], "F-S3", planesM))
            midx = unit["modal_info"]["modal_idx"]
            minst = next(t for t in P1["F-S3"]["targets"] if t["idx"] == midx)
            refs.append(make_ref(S, S.build(build_curve(minst)), minst, "modal", "F-S3", planesM))
            want = {r["label"]: r["h_ops"] for r in unit["refs"]}
            for r in refs:
                if want[r.label] != r.res.h_ops:
                    raise RuntimeError(f"rebuilt F-S3 reference {r.label} {cell} D={D} differs from checkpoint")
            fs3_live[D] = refs
            return refs

        def do_unit(phase, fam, D, cell=cell, fs3_live=fs3_live, **kw):
            name = f"p{phase}-{cell}-{fam}-D{D}"
            if run.ck_exists(name):
                return None
            ts = now()
            t = time.time()
            run.log(f"phase {phase} [{cell}]: {fam} D={D}")
            result, live, oplogs = process_family(ctx, fam, D, log=run.log, **kw)
            result.update(unit_meta(ts, now(), time.time() - t))
            result["cell"] = cell
            if oplogs is not None:
                p = os.path.join(run.out, f"F-S3-reference-oplogs-{cell}-D{D}.jsonl.gz")
                if os.path.exists(p):
                    raise RuntimeError(f"{p} exists; refusing to overwrite")
                tmp = p + ".tmp"
                with gzip.open(tmp, "wt") as f:
                    for label, inst, ops in oplogs:
                        for k, (pp, cc, X) in enumerate(ops):
                            f.write(json.dumps({"cell": cell, "ref": label, "x_R": inst["x_R"], "k": k, "p": pp,
                                                "c": cc, "X": X}, separators=(",", ":")) + "\n")
                os.replace(tmp, p)
            run.ck_save(name, result)
            if fam == "F-S3" and not kw.get("reverse"):
                refs = list(live["own"]) + ([live["modal"]] if live["modal"] is not None else [])
                for r in refs:
                    r.group = "F-S3"
                fs3_live[D] = refs
            return result

        s3 = P1["F-S3"]
        for D in Ds:
            do_unit(2, "F-S3", D, ref_insts=s3["refs"], targets=s3["targets"], build_E=build_curve, reverse=False,
                    planes_E=planes_curve, cross_groups={}, affine_route=True, keep_oplogs=True)
        for D in Ds:
            if run.ck_exists(f"p2-{cell}-F-PLANT-D{D}"):
                continue
            do_unit(2, "F-PLANT", D, ref_insts=[], targets=P1["F-PLANT"]["targets"], build_E=build_curve,
                    reverse=False, planes_E=planes_curve, cross_groups={"F-S3": get_fs3_live(D)}, affine_route=True)
        for D in Ds:
            if run.ck_exists(f"p3-{cell}-F-RANDX-D{D}"):
                continue
            do_unit(3, "F-RANDX", D, ref_insts=P1["F-RANDX"]["refs"], targets=P1["F-RANDX"]["targets"],
                    build_E=build_curve, reverse=False, planes_E=planes_curve,
                    cross_groups={"F-S3": get_fs3_live(D)}, affine_route=True)
        fs3_live.clear()
        fam = "F-AFF-1"
        A0 = E_from_hex(P1[fam]["A0_hex"])
        Aj = [E_from_hex(x) for x in P1[fam]["Aj_hex"]]

        def build_aff(inst, A0=A0, Aj=Aj):
            return affine_combine(A0, Aj, inst["x_R"])

        for D in Ds:
            do_unit(4, fam, D, ref_insts=P1[fam]["refs"], targets=P1[fam]["targets"], build_E=build_aff,
                    reverse=False, planes_E=[A0] + Aj, cross_groups={}, affine_route=True)
        for D in Ds:
            do_unit(5, "F-NULLF2", D, ref_insts=P1["F-NULLF2"]["refs"], targets=P1["F-NULLF2"]["targets"],
                    build_E=lambda inst: E_from_hex(inst["E_hex"]), reverse=False, planes_E=None,
                    cross_groups={}, affine_route=False)
        rev_targets = sorted(s3["targets"], key=lambda t: t["idx"])[:NREV]
        for D in Ds:
            do_unit(6, "F-S3-REV", D, ref_insts=s3["refs"], targets=rev_targets, build_E=build_curve, reverse=True,
                    planes_E=planes_curve, cross_groups={}, affine_route=True)
        run.log(f"[{cell}] phases 1-6 complete")
    run.log("phases 1-6 complete for every cell")
    if not run.ck_exists("p7-determinism"):
        run.log("phase 7 (determinism) not yet run: launch the determinism command in a separate process, then --resume")
        return 0
    if not run.ck_exists("p8-certificates"):
        ts = now()
        t = time.time()
        run.log("phase 8: PS0' certificate extraction and cells.json")
        info = phase8(run, plan, ctx)
        info.update(unit_meta(ts, now(), time.time() - t))
        run.ck_save("p8-certificates", info)
    ver = os.path.join(run.out, "ps0prime-verification.json")
    if not os.path.exists(ver):
        run.log("phase 8 complete: run the verify_command (separate process), then --resume")
        return 0
    if run.ck_exists("p9-done"):
        run.log("phase 9 already complete")
        return 0
    import report
    ts = now()
    t = time.time()
    run.log("phase 9: aggregation, decision rules, run report")
    report.phase9(run, plan, spec, spec_text, ctx)
    run.ck_save("p9-done", unit_meta(ts, now(), time.time() - t))
    run.log("phase 9 complete")
    return 0


# ---------------------------------------------------------------------------
def phase7(run, plan):
    """C-DET: the references (5 + modal) and the 200 lowest-idx F-S3 targets of
    each cell, re-eliminated at both D in this separate process."""
    if run.ck_exists("p7-determinism"):
        run.log("phase 7 checkpoint exists; nothing to do")
        return 0
    for cell in CELLS:
        for D in plan["counts"]["D"]:
            if not run.ck_exists(f"p2-{cell}-F-S3-D{D}"):
                run.log("phase 2 incomplete; run the main driver first")
                return 6
    ts = now()
    t0 = time.time()
    ctx = setup(plan)
    F = ctx["F"]
    NT = plan["counts"]["c_det_targets"]
    out = {"process": {"pid": os.getpid(), "ppid": os.getppid(), "argv": sys.argv, "started_at": ts,
                       "note": "separate process invocation; re-derives every matrix from the stored x_R, the curve and the V basis"},
           "per_cell_D": {}, "mismatches": [], "targets_checked": 0, "targets_matched": 0,
           "refs_checked": 0, "refs_matched": 0}
    for cell in CELLS:
        P1 = run.ck_load(f"p1-{cell}-instances")
        V = load_V(P1)
        B = P1["curve"]["B"]
        tg = sorted(P1["F-S3"]["targets"], key=lambda x: x["idx"])[:NT]
        for D in plan["counts"]["D"]:
            S = ctx["shapes"][D]
            unit = run.ck_load(f"p2-{cell}-F-S3-D{D}")
            want_t = {r["idx"]: r["h_ops"] for r in unit["records"]}
            want_r = {r["label"]: r["h_ops"] for r in unit["refs"]}
            insts = [(inst["selected_as"], inst) for inst in P1["F-S3"]["refs"]]
            if unit.get("modal_info"):
                midx = unit["modal_info"]["modal_idx"]
                insts.append(("modal", next(x for x in P1["F-S3"]["targets"] if x["idx"] == midx)))
            rm = 0
            for lab, inst in insts:
                res, _, _ = eliminate(S.build(descended_E(F, B, inst["x_R"], V.basis)), S.C, keep_ops=False,
                                      with_row_pass=False)
                ok = res.h_ops == want_r[lab]
                rm += ok
                if not ok:
                    out["mismatches"].append({"cell": cell, "D": D, "ref": lab})
            tm = 0
            for t in tg:
                res, _, _ = eliminate(S.build(descended_E(F, B, t["x_R"], V.basis)), S.C, keep_ops=False,
                                      with_row_pass=False)
                ok = res.h_ops == want_t[t["idx"]]
                tm += ok
                if not ok:
                    out["mismatches"].append({"cell": cell, "D": D, "idx": t["idx"]})
            run.log(f"  determinism [{cell}] D={D}: targets {tm}/{len(tg)}, refs {rm}/{len(insts)}")
            out["per_cell_D"][f"{cell}/D{D}"] = {"targets_matched": tm, "targets_checked": len(tg),
                                                "refs_matched": rm, "refs_checked": len(insts)}
            out["targets_checked"] += len(tg)
            out["targets_matched"] += tm
            out["refs_checked"] += len(insts)
            out["refs_matched"] += rm
    out.update(unit_meta(ts, now(), time.time() - t0))
    run.ck_save("p7-determinism", out)
    run.log(f"phase 7 complete: targets {out['targets_matched']}/{out['targets_checked']}, refs {out['refs_matched']}/{out['refs_checked']}")
    return 0


# ---------------------------------------------------------------------------
def certificate_rows(M, C, R):
    """Column pass with a row-combination tracker: returns (rows, ok) where rows
    is the set of ORIGINAL row indices whose XOR is the row that pivots in the
    constant column (the constant 1 itself, since every unused row is zero in
    all earlier columns), or None if 1 is not in R_D."""
    Mw = M.copy()
    ps, cs, Xs = column_pass(Mw, C, keep_ops=True)
    if C - 1 not in cs:
        return None, None
    Wt = (R + 63) // 64
    T = np.zeros((R, Wt), dtype=np.uint64)
    idx = np.arange(R)
    T[idx, idx >> 6] = np.left_shift(np.uint64(1), (idx & 63).astype(np.uint64))
    k_const = cs.index(C - 1)
    for k in range(k_const):
        X = Xs[k]
        if X.size:
            T[X] ^= T[ps[k]]
    p = ps[k_const]
    bits = np.unpackbits(T[p].view(np.uint8), bitorder="little")[:R]
    rows = [int(i) for i in np.flatnonzero(bits)]
    # internal check (the separate verifier re-checks independently)
    acc = np.bitwise_xor.reduce(M[rows], axis=0)
    one = np.zeros_like(acc)
    one[(C - 1) >> 6] = np.uint64(1) << np.uint64((C - 1) & 63)
    return rows, bool(np.array_equal(acc, one))


def phase8(run, plan, ctx):
    F = ctx["F"]
    S = ctx["shapes"][4]
    NC = plan["counts"]["ps0prime_certificates_per_cell"]
    cells = {"experiment_id": EXP_ID, "run_id": run.args.run_id,
             "field": {"n": 17, "modulus_int": (1 << 17) | (1 << 3) | 1, "modulus": "t^17 + t^3 + 1",
                       "element_encoding": "17-bit integer, bit j = coefficient of t^j"},
             "conventions": {
                 "variables": "Boolean v_0..v_17; x_1 = sum_{j<9} v_j b_j, x_2 = sum_{j<9} v_{9+j} b_j (b = the cell's V basis)",
                 "S_3": "(x_1 x_2 + x_1 x_R + x_2 x_R)^2 + x_1 x_2 x_R + B",
                 "equations": "f_k = coefficient of t^k of S_3(x_1, x_2, x_R) after multilinear reduction (v^2 = v), k = 0..16",
                 "macaulay_row": "row (mu, k) = multilinear reduction of mu * f_k; mu a multilinear monomial given as a sorted list of variable indices, deg mu <= D - 2",
                 "certificate": "a set of rows (mu, k) of M_4 whose XOR is the constant polynomial 1"},
             "cells": {}}
    certs_path = os.path.join(run.out, "ps0prime-certificates.jsonl.gz")
    cells_path = os.path.join(run.out, "cells.json")
    for p in (certs_path, cells_path):
        if os.path.exists(p):
            raise RuntimeError(f"{p} exists; refusing to overwrite")
    info = {"per_cell": {}}
    lines = []
    for cell in CELLS:
        P1 = run.ck_load(f"p1-{cell}-instances")
        V = load_V(P1)
        B = P1["curve"]["B"]
        unit = run.ck_load(f"p2-{cell}-F-S3-D4")
        cand = sorted((r for r in unit["records"] if r["stratum"] == "unsat" and r["one_in_R"]), key=lambda r: r["idx"])
        chosen = cand[:NC]
        internal_ok = 0
        for r in chosen:
            M = S.build(descended_E(F, B, r["x_R"], V.basis))
            rows, ok = certificate_rows(M, S.C, S.R)
            internal_ok += bool(ok)
            mus = [[list(S.mus[i // NEQ]), i % NEQ] for i in rows]
            lines.append(json.dumps({"cell": cell, "family": "F-S3", "idx": r["idx"], "x_R": r["x_R"], "D": 4,
                                     "n_rows": len(rows), "row_indices": rows, "rows_mu_k": mus,
                                     "impl_internal_check": ok}, separators=(",", ":")))
        info["per_cell"][cell] = {"eligible": len(cand), "extracted": len(chosen), "shortfall": max(0, NC - len(cand)),
                                  "impl_internal_check_pass": internal_ok, "idx": [r["idx"] for r in chosen]}
        # hull data per family (non-degenerate test targets, idx order)
        hulls = {}
        fam_targets = {"F-S3": P1["F-S3"]["targets"], "F-PLANT": P1["F-PLANT"]["targets"],
                       "F-RANDX": P1["F-RANDX"]["targets"], "F-AFF-1": P1["F-AFF-1"]["targets"],
                       "F-S3-REV": sorted(P1["F-S3"]["targets"], key=lambda t: t["idx"])[:plan["counts"]["rev_targets"]]}
        for fam, tg in fam_targets.items():
            rs = [t["x_R"] for t in sorted(tg, key=lambda t: t["idx"]) if not t["degenerate"]]
            h0, Wb, z = affine_hull(rs)
            hulls[fam] = {"n_points": len(rs), "h0": h0, "h0_idx": min(t["idx"] for t in tg if not t["degenerate"]),
                          "dim_W": len(Wb), "W_basis": Wb, "zero_in_H": z}
        hulls["F-NULLF2"] = {"note": "no r-vector (no x_R): hull not defined"}
        cv = P1["curve"]
        cells["cells"][cell] = {
            "curve": {k: cv.get(k) for k in ("A", "B", "order", "h", "q", "P", "Q", "k_Q", "source", "draws",
                                              "draws_rejected", "rejections", "rejected_draws", "points_draw")},
            "V": P1["V"], "tau_j_Tr_t^j": P1["tau"], "C-TR": P1["C-TR"], "rejections": P1["rejections"],
            "hulls": hulls,
            "factor_base_size_F_V": P1["F-PLANT"]["factor_base_size"],
        }
    tmp = certs_path + ".tmp"
    with gzip.open(tmp, "wt") as f:
        for ln in lines:
            f.write(ln + "\n")
    os.replace(tmp, certs_path)
    tmp = cells_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cells, f, indent=1, default=jdefault)
    os.replace(tmp, cells_path)
    info["certificates_sha256"] = sha256_file(certs_path)
    info["cells_sha256"] = sha256_file(cells_path)
    return info


if __name__ == "__main__":
    sys.exit(main())
