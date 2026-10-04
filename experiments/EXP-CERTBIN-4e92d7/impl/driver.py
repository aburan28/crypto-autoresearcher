#!/usr/bin/env python3
"""Driver for EXP-CERTBIN-4e92d7 (phases 1-8; phase 0 is selftest.py).

  main invocation            : phases 1-6 (checkpointed), then phase 8 if the
                               phase-7 checkpoint exists, else exits asking for
                               the determinism phase.
  --phase determinism        : phase 7 in a SEPARATE process (C-DET).
  --resume                   : continue from the last complete checkpoint
                               (and run phase 8 once phase 7 is complete).
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
from macaulay import MacaulayShape, descended_E, affine_basis, affine_combine  # noqa: E402
from families import run_phase1, E_from_hex  # noqa: E402
from engine import process_family, make_ref  # noqa: E402
from elim import eliminate  # noqa: E402

EXP_ID = "EXP-CERTBIN-4e92d7"
MEM_LIMIT = 4 * 1024 ** 3
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

SPEC_SEED_KEYS = ["S_curve", "S_pts", "S_ref", "S_test", "S_plant", "S_randx_ref", "S_randx_test",
                  "S_nullF2_ref", "S_nullF2_test", "S_nullAff_draw1", "S_nullAff_draw2",
                  "S_nullAff_draw3", "S_selftest"]
# Counts transcribed from the frozen specification text (version 1).
SPEC_COUNTS = {"test_targets": 1000, "planted_targets": 200, "reference_scan_max_draws": 500,
               "references_unsat": 3, "references_sat": 2, "D": [3, 4], "modal_window": [1, 100],
               "modal_scored": [101, 1000], "bootstrap_resamples": 10000, "c_aff_direct_replay_targets": 20,
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

    # --- checkpoints (gzipped JSON, atomic) ---
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
    seeds = spec["experiment"]["seeds"]
    for k in SPEC_SEED_KEYS:
        if plan["seeds"].get(k) != seeds.get(k):
            errs.append(f"seed {k}: plan {plan['seeds'].get(k)} != spec {seeds.get(k)}")
    if sorted(plan["seeds"]) != sorted(SPEC_SEED_KEYS):
        errs.append("plan seed key set differs from the 13 declared seeds")
    for k, v in SPEC_COUNTS.items():
        if plan["counts"].get(k) != v:
            errs.append(f"count {k}: plan {plan['counts'].get(k)} != spec {v}")
    if plan.get("spec_sha256") != hashlib.sha256(spec_text).hexdigest():
        errs.append("plan spec_sha256 does not match the specification file")
    if spec["experiment"]["status"] != "approved" or not spec["experiment"].get("approved_by"):
        errs.append("specification not approved")
    if plan.get("run_id") != args.run_id:
        errs.append("plan run_id != --run-id")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan", required=True)
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
    else:
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
            rc = phase7(run, plan, spec, inv)
        else:
            rc = main_phases(run, plan, spec, spec_text, inv)
    except Exception as e:
        import traceback
        traceback.print_exc()
        run.invocation({"event": "crash", "pid": os.getpid(), "at": now(), "error": repr(e),
                        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024})
        return 3
    run.invocation({"event": "end", "pid": os.getpid(), "at": now(), "rc": rc,
                    "wall_seconds": time.time() - run.t0,
                    "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                    "cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime})
    return rc


# ---------------------------------------------------------------------------
class Ctx(dict):
    pass


def setup(run, plan):
    F = TableField()
    ctx = Ctx()
    ctx["F"] = F
    ctx["shapes"] = {D: MacaulayShape(D) for D in plan["counts"]["D"]}
    return ctx


def unit_meta(t_start, t_end, wall):
    return {"started_at": t_start, "finished_at": t_end, "wall_seconds": wall,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "pid": os.getpid()}


def main_phases(run, plan, spec, spec_text, inv):
    selftest_p = os.path.join(run.out, "selftest.json")
    if not os.path.exists(selftest_p):
        run.log("phase 0 missing: selftest.json not found; stopping before any draw (SR-2)")
        return 4
    st = json.load(open(selftest_p))
    if not st.get("all_pass"):
        run.log("phase 0 FAILED (C-SELF/C-FIX); stopping before phase 1 (SR-2, INV-1/INV-2)")
        return 4
    existing = [f for f in os.listdir(run.ck) if f.endswith(".json.gz")]
    if existing and not run.args.resume:
        run.log(f"checkpoints exist ({len(existing)}); use --resume")
        return 5
    ctx = setup(run, plan)
    F = ctx["F"]
    # C-FIX re-check in the driver
    for D, (R, C) in ((3, (323, 988)), (4, (2924, 4048))):
        S = ctx["shapes"][D]
        if (S.R, S.C) != (R, C):
            run.log(f"C-FIX mismatch at D={D}: {(S.R, S.C)}; stop (INV-1)")
            return 4

    # ---------------- phase 1
    if not run.ck_exists("p1-instances"):
        ts = now()
        t = time.time()
        run.log("phase 1: curve, points, references, targets, oracles, witnesses")
        P1 = run_phase1(F, plan, run.log)
        P1["_meta"] = unit_meta(ts, now(), time.time() - t)
        run.ck_save("p1-instances", P1)
    P1 = run.ck_load("p1-instances")
    ctx["phase1"] = P1
    B = P1["curve"]["B"]
    E0, Ej = affine_basis(F, B)
    planes_curve = [E0] + Ej

    def build_curve(inst):
        return descended_E(F, B, inst["x_R"])

    fs3_live = {}

    def get_fs3_live(D):
        if D in fs3_live:
            return fs3_live[D]
        unit = run.ck_load(f"p2-F-S3-D{D}")
        S = ctx["shapes"][D]
        planesM = np.stack([S.build(x) for x in planes_curve])
        refs = []
        for inst in P1["F-S3"]["refs"]:
            r = make_ref(S, S.build(build_curve(inst)), inst, inst["selected_as"], "F-S3", planesM)
            refs.append(r)
        midx = unit["modal_info"]["modal_idx"]
        minst = next(t for t in P1["F-S3"]["targets"] if t["idx"] == midx)
        m = make_ref(S, S.build(build_curve(minst)), minst, "modal", "F-S3", planesM)
        refs.append(m)
        want = {r["label"]: r["h_ops"] for r in unit["refs"]}
        for r in refs:
            if want[r.label] != r.res.h_ops:
                raise RuntimeError(f"rebuilt F-S3 reference {r.label} D={D} differs from checkpoint")
        fs3_live[D] = refs
        return refs

    def do_unit(phase, fam, D, **kw):
        name = f"p{phase}-{fam}-D{D}"
        if run.ck_exists(name):
            run.log(f"{name}: checkpoint present, skipping")
            return None
        if phase == 2 and fam == "F-S3" and D == min(plan["counts"]["D"]) and not run.ck_exists("first-elimination"):
            run.ck_save("first-elimination", {"at": now(), "pid": os.getpid()})
        ts = now()
        t = time.time()
        run.log(f"phase {phase}: {fam} D={D}")
        result, live, oplogs = process_family(ctx, fam, D, log=run.log, **kw)
        result.update(unit_meta(ts, now(), time.time() - t))
        if oplogs is not None:
            p = os.path.join(run.out, f"F-S3-reference-oplogs-D{D}.jsonl.gz")
            if os.path.exists(p):
                raise RuntimeError(f"{p} exists; refusing to overwrite")
            tmp = p + ".tmp"
            with gzip.open(tmp, "wt") as f:
                for label, inst, ops in oplogs:
                    for k, (pp, cc, X) in enumerate(ops):
                        f.write(json.dumps({"ref": label, "x_R": inst["x_R"], "k": k, "p": pp, "c": cc, "X": X},
                                           separators=(",", ":")) + "\n")
            os.replace(tmp, p)
        run.ck_save(name, result)
        if fam == "F-S3" and not kw.get("reverse"):
            refs = list(live["own"]) + ([live["modal"]] if live["modal"] is not None else [])
            for r in refs:
                r.group = "F-S3"
            fs3_live[D] = refs
        return result

    Ds = plan["counts"]["D"]
    s3 = P1["F-S3"]
    # ---------------- phase 2: F-S3 then F-PLANT
    for D in Ds:
        do_unit(2, "F-S3", D, ref_insts=s3["refs"], targets=s3["targets"], build_E=build_curve, reverse=False,
                planes_E=planes_curve, cross_groups={}, affine_route=True, keep_oplogs=True)
    for D in Ds:
        if run.ck_exists(f"p2-F-PLANT-D{D}"):
            continue
        do_unit(2, "F-PLANT", D, ref_insts=[], targets=P1["F-PLANT"]["targets"], build_E=build_curve,
                reverse=False, planes_E=planes_curve, cross_groups={"F-S3": get_fs3_live(D)}, affine_route=True)
    # ---------------- phase 3: F-RANDX
    for D in Ds:
        if run.ck_exists(f"p3-F-RANDX-D{D}"):
            continue
        do_unit(3, "F-RANDX", D, ref_insts=P1["F-RANDX"]["refs"], targets=P1["F-RANDX"]["targets"],
                build_E=build_curve, reverse=False, planes_E=planes_curve,
                cross_groups={"F-S3": get_fs3_live(D)}, affine_route=True)
    fs3_live.clear()
    # ---------------- phase 4: F-AFF-1..3
    for d in (1, 2, 3):
        fam = f"F-AFF-{d}"
        A0 = E_from_hex(P1[fam]["A0_hex"])
        Aj = [E_from_hex(x) for x in P1[fam]["Aj_hex"]]

        def build_aff(inst, A0=A0, Aj=Aj):
            return affine_combine(A0, Aj, inst["x_R"])

        for D in Ds:
            do_unit(4, fam, D, ref_insts=P1[fam]["refs"], targets=P1[fam]["targets"], build_E=build_aff,
                    reverse=False, planes_E=[A0] + Aj, cross_groups={}, affine_route=True)
    # ---------------- phase 5: F-NULLF2
    for D in Ds:
        do_unit(5, "F-NULLF2", D, ref_insts=P1["F-NULLF2"]["refs"], targets=P1["F-NULLF2"]["targets"],
                build_E=lambda inst: E_from_hex(inst["E_hex"]), reverse=False, planes_E=None,
                cross_groups={}, affine_route=False)
    # ---------------- phase 6: F-S3-REV
    for D in Ds:
        do_unit(6, "F-S3-REV", D, ref_insts=s3["refs"], targets=s3["targets"], build_E=build_curve, reverse=True,
                planes_E=planes_curve, cross_groups={}, affine_route=True)
    run.log("phases 1-6 complete")
    # ---------------- phase 7 is a separate process
    if not run.ck_exists("p7-determinism"):
        run.log("phase 7 (determinism) not yet run: launch the determinism command in a separate process, then --resume")
        return 0
    # ---------------- phase 8
    if run.ck_exists("p8-done"):
        run.log("phase 8 already complete")
        return 0
    import report
    ts = now()
    t = time.time()
    run.log("phase 8: aggregation, decision rules, run report")
    report.phase8(run, plan, spec, spec_text, ctx)
    run.ck_save("p8-done", unit_meta(ts, now(), time.time() - t))
    run.log("phase 8 complete")
    return 0


# ---------------------------------------------------------------------------
def phase7(run, plan, spec, inv):
    if run.ck_exists("p7-determinism"):
        run.log("phase 7 checkpoint exists; nothing to do")
        return 0
    for D in plan["counts"]["D"]:
        if not run.ck_exists(f"p2-F-S3-D{D}"):
            run.log("phase 2 incomplete; run the main driver first")
            return 6
    ts = now()
    t0 = time.time()
    ctx = setup(run, plan)
    F = ctx["F"]
    P1 = run.ck_load("p1-instances")
    B = P1["curve"]["B"]
    out = {"process": {"pid": os.getpid(), "ppid": os.getppid(), "argv": sys.argv, "started_at": ts,
                       "note": "separate process invocation; re-derives every matrix from the stored x_R and the curve"},
           "per_D": {}, "mismatches": [], "targets_checked": 0, "targets_matched": 0,
           "refs_checked": 0, "refs_matched": 0}
    for D in plan["counts"]["D"]:
        S = ctx["shapes"][D]
        unit = run.ck_load(f"p2-F-S3-D{D}")
        want_t = {r["idx"]: r["h_ops"] for r in unit["records"]}
        want_r = {r["label"]: r["h_ops"] for r in unit["refs"]}
        insts = [(inst["selected_as"], inst) for inst in P1["F-S3"]["refs"]]
        midx = unit["modal_info"]["modal_idx"]
        insts.append(("modal", next(x for x in P1["F-S3"]["targets"] if x["idx"] == midx)))
        rm = 0
        for lab, inst in insts:
            res, _, _ = eliminate(S.build(descended_E(F, B, inst["x_R"])), S.C, keep_ops=False, with_row_pass=False)
            ok = res.h_ops == want_r[lab]
            rm += ok
            if not ok:
                out["mismatches"].append({"D": D, "ref": lab})
        tm = 0
        for t in P1["F-S3"]["targets"]:
            res, _, _ = eliminate(S.build(descended_E(F, B, t["x_R"])), S.C, keep_ops=False, with_row_pass=False)
            ok = res.h_ops == want_t[t["idx"]]
            tm += ok
            if not ok:
                out["mismatches"].append({"D": D, "idx": t["idx"]})
            if t["idx"] % 200 == 0:
                run.log(f"  determinism D={D}: {t['idx']}/{len(P1['F-S3']['targets'])}")
        out["per_D"][f"D{D}"] = {"targets_matched": tm, "targets_checked": len(P1["F-S3"]["targets"]),
                                 "refs_matched": rm, "refs_checked": len(insts)}
        out["targets_checked"] += len(P1["F-S3"]["targets"])
        out["targets_matched"] += tm
        out["refs_checked"] += len(insts)
        out["refs_matched"] += rm
    out.update(unit_meta(ts, now(), time.time() - t0))
    run.ck_save("p7-determinism", out)
    run.log(f"phase 7 complete: targets {out['targets_matched']}/{out['targets_checked']}, refs {out['refs_matched']}/{out['refs_checked']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
