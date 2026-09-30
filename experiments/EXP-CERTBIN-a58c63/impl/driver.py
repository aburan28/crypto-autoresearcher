#!/usr/bin/env python3
"""Driver for EXP-CERTBIN-a58c63 (phase 0 pilot, phases 1-5 and 7a, phase 6
determinism, phase 8 aggregation; phase 0 self-test is selftest.py and phase
7b is verifier/verify_cert.py).

Copied from EXP-CERTBIN-4e92d7/impl/driver.py and restructured for four cells,
two regimes, the pilot and at most two workers (see impl-provenance.json).

  --phase pilot       : C-PROV (cprov.json), the timing pilot (pilot.json), the
                        schedule decision and trial-plan-v1.json. Draws no frozen stream.
  (main)              : phases 1-5 per cell (checkpointed), cells.json, the PS0'
                        certificates; then phase 8 if phase 6 and the verifier
                        output exist, else exits naming the next commands.
  --phase determinism : phase 6 (C-DET) in a SEPARATE process.
  --resume            : continue from the last complete checkpoint.
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

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from common import (EXP_ID, CELLS, cell_label, cell_seeds, FIXED_SEEDS, C_STD, C_LOW, FIXED_COUNTS, FIX_A, FIX_B,  # noqa: E402
                    STAGE1_RUN, STAGE1_CURVE_SHA256, STAGE1_RECEIPT, SPEC_SHA256_RECEIPT, TRIAL_PLAN,
                    b_elimination_count, AMENDMENT_ID, AMENDMENT_PATH, DEV_FIXED_SEEDS)
from gf2n import TableField, MODULUS17, find_pentanomial, modulus_string  # noqa: E402
from curve import Curve  # noqa: E402
from macaulay import Descent, MacaulayShape  # noqa: E402
from oracles import OracleC, s3_coeffs, oracle_A, OracleB  # noqa: E402
from regimeB import ShapeB, GFTabs, eliminate as eliminate_B  # noqa: E402
from delta import DeltaCalc  # noqa: E402
import families as fam_mod  # noqa: E402
import engineA  # noqa: E402
import engineB  # noqa: E402
from hull import family_hull_analysis  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MEM_PARENT = int(1.6 * 1024 ** 3)
MEM_CHILD = int(1.2 * 1024 ** 3)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jdefault(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(type(o))


def peak_rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024


def peak_rss_children():
    return resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024


class Run:
    def __init__(self, out):
        self.out = os.path.abspath(out)
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

    def write_new(self, name, obj=None, text=None):
        p = os.path.join(self.out, name)
        if os.path.exists(p):
            raise RuntimeError(f"{p} exists; refusing to overwrite")
        with open(p, "x") as f:
            if text is not None:
                f.write(text)
            else:
                json.dump(obj, f, indent=1, default=jdefault)
        return p


def git_state():
    try:
        head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        st = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=all"],
                            capture_output=True, text=True).stdout.splitlines()
        return {"commit": head, "dirty": bool(st), "status_porcelain": st}
    except Exception as e:  # recorded, not hidden
        return {"error": repr(e)}


# ---------------------------------------------------------------------------
# workers
_CHILD_LIMIT = [MEM_CHILD]


def _child_init():
    try:
        resource.setrlimit(resource.RLIMIT_AS, (_CHILD_LIMIT[0], _CHILD_LIMIT[0]))
    except Exception:
        pass


class Mapper:
    def __init__(self, workers):
        self.workers = workers

    def __call__(self, func, items):
        if self.workers <= 1 or len(items) < 4:
            return [func(t) for t in items]
        import multiprocessing as mp
        ctx = mp.get_context("fork")
        with ctx.Pool(self.workers, initializer=_child_init) as pool:
            return pool.map(func, items, chunksize=max(1, len(items) // (self.workers * 8)))


# ---------------------------------------------------------------------------
class CellCtx:
    pass


def load_mod19(run):
    st = json.load(open(os.path.join(run.out, "selftest.json")))
    mod19 = st["n19_modulus"]["modulus_int"]
    m2, abc, _, _ = find_pentanomial(19)
    if m2 != mod19:
        raise RuntimeError("selftest n19 modulus differs from the rule's recomputation")
    return mod19, abc


def stage1_curve(stage1_dir):
    p = os.path.join(stage1_dir, "curve.json")
    h = sha256_file(p)
    rec_ok = None
    try:
        rec = json.load(open(os.path.join(REPO, STAGE1_RECEIPT)))
        rec_ok = rec["path_sha256"].get(f"{STAGE1_RUN}/curve.json") == h
    except Exception as e:
        rec_ok = repr(e)
    if h != STAGE1_CURVE_SHA256 or rec_ok is not True:
        raise RuntimeError(f"Stage-1 curve.json sha256 {h} does not match the receipt ({rec_ok})")
    c = json.load(open(p))
    return c, h


def build_cell_ctx(run, plan, cidx, n, l, fields, curves, log):
    C = CellCtx()
    C.cidx, C.n, C.l = cidx, n, l
    C.label = cell_label(n, l)
    C.F = fields[n]
    ci = curves[n]
    C.curve_info = ci
    C.E = Curve(C.F, ci["A"], ci["B"])
    C.P, C.Q, C.q = tuple(ci["P"]), tuple(ci["Q"]), ci["q"]
    C.desc = Descent(C.F, l)
    C.shapesA = {D: MacaulayShape(D, C.desc) for D in (3, 4)}
    for D in (3, 4):
        if (C.shapesA[D].R, C.shapesA[D].C) != FIX_A[(n, l)][D]:
            raise RuntimeError(f"C-FIX mismatch regime A {C.label} D={D}")
    C.SB = ShapeB(C.F, l)
    if (C.SB.R, C.SB.C) != FIX_B[l]:
        raise RuntimeError(f"C-FIX mismatch regime B {C.label}")
    C.T = GFTabs(C.F)
    C.SB._tabs = C.T
    C.dc = DeltaCalc(C.F, l, C.SB.lam[0])
    C.oC = OracleC(C.F, l)
    C.seeds = next(c["seeds"] for c in plan["cells"] if c["cidx"] == cidx)
    return C


def curve_extras(C, cache):
    key = C.n
    if key not in cache:
        xE, x2E, ctr = fam_mod.curve_classes(C.E, C.curve_info["order"])
        sub = fam_mod.subgroup_xset(C.E, C.P, C.q)
        cache[key] = (xE, x2E, ctr, sub)
    return cache[key]


def with_coeffs(C, insts, kind):
    for t in insts:
        if kind == "curve":
            t["coeffs"] = list(s3_coeffs(C.F, C.E.B, t["x_R"]))
    return insts


# ---------------------------------------------------------------------------
def verify_spec(spec_text, spec):
    errs = []
    e = spec["experiment"]
    if e.get("status") != "approved" or not e.get("approved_by"):
        errs.append("specification not approved")
    if e.get("id") != EXP_ID or e.get("version") != 1:
        errs.append("specification id/version")
    if hashlib.sha256(spec_text).hexdigest() != SPEC_SHA256_RECEIPT:
        errs.append("specification sha256 differs from the TASK-20260924-d3a90c receipt")
    s = e["seeds"]["fixed"]
    for k, v in FIXED_SEEDS.items():
        if s.get(k) != v:
            errs.append(f"fixed seed {k}")
    cstd = e["counts"]["C_std"]
    for k in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-NULLF2", "F-NULLB"):
        if int(str(cstd[k]).split()[0]) != C_STD[k]:
            errs.append(f"C_std count {k}")
    if e["budget"]["maximum_workers"] != 2 or e["budget"]["maximum_memory_gb"] != 4:
        errs.append("budget workers/memory")
    return errs


def verify_plan(plan, spec_text, args):
    errs = []
    if plan.get("spec_sha256") != hashlib.sha256(spec_text).hexdigest():
        errs.append("plan spec_sha256")
    if plan.get("run_id") != args.run_id:
        errs.append("plan run_id")
    sched = plan.get("schedule")
    base = C_STD if sched == "C_std" else C_LOW
    for k, v in base.items():
        if plan["counts"].get(k) != v and not args.dev:
            errs.append(f"plan count {k}")
    for k, v in FIXED_COUNTS.items():
        if plan["counts"].get(k) != v and not args.dev:
            errs.append(f"plan fixed count {k}")
    if not args.dev:
        for c in plan["cells"]:
            if c["seeds"] != cell_seeds(c["cidx"]):
                errs.append(f"plan seeds cell {c['cidx']}")
        if plan["seeds_fixed"] != FIXED_SEEDS:
            errs.append("plan fixed seeds")
        if plan.get("protocol_version") != 2 or not plan.get("amendment"):
            errs.append("plan is not bound to protocol version 2 (AMD-20260924-3a9f06)")
    return errs


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--plan")
    ap.add_argument("--stage1-run")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--phase", default="main", choices=["main", "pilot", "determinism"])
    ap.add_argument("--dev", action="store_true", help="development: dev seeds/plan; output must be OUTSIDE the repository")
    ap.add_argument("--dev-scale", type=float, default=1.0)
    ap.add_argument("--dev-cells", default="")
    args = ap.parse_args()

    resource.setrlimit(resource.RLIMIT_AS, (MEM_PARENT, MEM_PARENT))
    spec_text = open(args.spec, "rb").read()
    spec = yaml.safe_load(spec_text)
    out = os.path.abspath(args.out)
    if args.dev:
        if out.startswith(REPO + os.sep):
            print("--dev output must be outside the repository", file=sys.stderr)
            return 2
    else:
        want = os.path.join(REPO, "experiments", EXP_ID, "runs", args.run_id)
        if out != want:
            print(f"--out must be {want}", file=sys.stderr)
            return 2
        errs = verify_spec(spec_text, spec)
        if errs:
            print("specification check failed: " + "; ".join(errs), file=sys.stderr)
            return 2
    run = Run(out)
    inv = {"argv": sys.argv, "phase": args.phase, "resume": args.resume, "pid": os.getpid(), "ppid": os.getppid(),
           "started_at": now(), "git": git_state(), "rlimit_as_bytes": MEM_PARENT,
           "child_rlimit_as_bytes": MEM_CHILD, "python": sys.version, "numpy": np.__version__}
    run.invocation({"event": "start", **inv})
    try:
        if args.phase == "pilot":
            rc = phase_pilot(run, args, spec, spec_text)
        elif args.phase == "determinism":
            rc = phase6(run, args, spec, spec_text)
        else:
            rc = main_phases(run, args, spec, spec_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        run.invocation({"event": "crash", "pid": os.getpid(), "at": now(), "error": repr(e),
                        "peak_rss_bytes": peak_rss()})
        return 3
    run.invocation({"event": "end", "pid": os.getpid(), "at": now(), "rc": rc,
                    "wall_seconds": time.time() - run.t0, "peak_rss_bytes": peak_rss(),
                    "peak_rss_children_bytes": peak_rss_children(),
                    "cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                    "cpu_seconds_children": resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime + resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime})
    return rc


# ---------------------------------------------------------------------------
# PHASE 0b: C-PROV, pilot, trial plan
def phase_pilot(run, args, spec, spec_text):
    st_p = os.path.join(run.out, "selftest.json")
    if not os.path.exists(st_p):
        run.log("selftest.json missing; stop (SR-2)")
        return 4
    st = json.load(open(st_p))
    if not st.get("all_pass"):
        run.log("C-SELF/C-FIX failed; stop before any frozen stream (SR-2, INV-1)")
        return 4
    plan_path = os.path.join(REPO, TRIAL_PLAN) if not args.dev else os.path.join(run.out, "trial-plan-dev.json")
    for p in ("cprov.json", "pilot.json"):
        if os.path.exists(os.path.join(run.out, p)):
            run.log(f"{p} exists; the pilot phase does not re-run")
            return 5
    if os.path.exists(plan_path):
        run.log(f"{plan_path} exists; refusing to overwrite")
        return 5
    mod19, abc = load_mod19(run)
    # ---- C-PROV
    stage1 = os.path.join(REPO, STAGE1_RUN)
    run.log("C-PROV: regression of the copied regime-A code on the archived Stage-1 instances")
    t = time.time()
    cprov = cprov_check(run, stage1)
    cprov["wall_seconds"] = time.time() - t
    run.write_new("cprov.json", cprov)
    run.log(f"C-PROV pass = {cprov['pass']} ({cprov['n_compared']} comparisons, {len(cprov['mismatches'])} mismatches)")
    # ---- timing pilot (S_selftest only; timings only)
    g = np.random.Generator(np.random.PCG64(DEV_FIXED_SEEDS["S_selftest"] if args.dev else FIXED_SEEDS["S_selftest"]))
    c17, _ = stage1_curve(stage1)
    fields = {17: TableField(17, MODULUS17), 19: TableField(19, mod19)}
    B19 = None
    per_cell = []
    T_proj = 0.0
    counts_std = b_elimination_count(C_STD)
    for cidx, n, l in CELLS:
        F = fields[n]
        if n == 19 and B19 is None:
            B19 = int(g.integers(1, F.q))
        B = c17["B"] if n == 17 else B19
        S = ShapeB(F, l)
        T = GFTabs(F)
        times = []
        for i in range(FIXED_COUNTS["pilot_instances_per_cell"]):
            x = int(g.integers(0, F.q))
            t1 = time.perf_counter()
            M = S.build(s3_coeffs(F, B, x))
            res, cpass, _ = eliminate_B(M, T)
            times.append(time.perf_counter() - t1)
            del res, cpass
        mean = sum(times) / len(times)
        T_proj += mean * counts_std["total"]
        per_cell.append({"cell": cell_label(n, l), "seconds": times, "mean_seconds": mean,
                         "regime_B_elimination_count_C_std": counts_std["total"]})
    thr = FIXED_COUNTS["pilot_threshold_single_worker_seconds"]
    rule_schedule = "C_std" if T_proj <= thr else "C_low"
    schedule = "C_std"   # AMD-20260924-3a9f06 C-16: C-PILOT recorded FAILED pre-run; its consequence applies
    pilot = {"experiment_id": EXP_ID, "run_id": args.run_id, "written_at": now(),
             "selftest_all_pass": st["all_pass"],
             "timed_unit": "build M_66 + column pass (solver) + row pass (C-PASS), one regime-B instance, single worker",
             "x_R_source": "fresh numpy PCG64(S_selftest) generator: per cell in order, 10 x integers(0, 2^n); for the n = 19 cells one B = integers(1, 2^19) drawn first (before the first n = 19 x_R); n = 17 cells use the Stage-1 B",
             "per_cell": per_cell, "C_std_count_breakdown_per_cell": counts_std,
             "T_proj_single_worker_seconds": T_proj, "threshold_seconds": thr,
             "rule": "C_std iff T_proj <= 345,600 single-worker seconds, else C_low (every cell)",
             "schedule_the_rule_would_give_(not_binding)": rule_schedule,
             "schedule": schedule,
             "schedule_basis": "C-PILOT consequence (AMD C-16): C-PILOT is recorded as FAILED pre-run because version-1 frozen streams were drawn in dev before the decision; the count schedule is C_std regardless; T_proj is reported but not binding",
             "outputs_written": "timings, self-test pass/fail and the decision only (C-PILOT)"}
    p = run.write_new("pilot.json", pilot)
    pilot_sha = sha256_file(p)
    run.log(f"pilot: T_proj = {T_proj:.0f} s (threshold {thr}); schedule {schedule}")
    # ---- trial plan
    from make_trial_plan import write_plan
    spec_rel = os.path.relpath(os.path.abspath(args.spec), REPO)
    amend = amendment_binding(args)
    plan_sha, plan = write_plan(plan_path, spec_rel, hashlib.sha256(spec_text).hexdigest(), args.run_id, schedule,
                                pilot_sha, T_proj, dev=args.dev, dev_offset=0,
                                amendment=amend, dev_exploration=dev_exploration_block())
    if args.dev and args.dev_scale != 1.0:
        # development only: shrink counts in a separate dev plan file
        os.chmod(plan_path, 0o644)
        for k in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB", "C-REV", "C-DET"):
            plan["counts"][k] = max(4, int(plan["counts"][k] * args.dev_scale))
        with open(plan_path, "w") as f:
            json.dump(plan, f, indent=1)
    run.log(f"trial plan written: {plan_path} sha256 {sha256_file(plan_path)}")
    return 0


def amendment_binding(args):
    """Protocol version 2: the amendment file must be committed and unmodified
    (non-dev). Returns its path, sha256 and git blob state."""
    p = os.path.join(REPO, AMENDMENT_PATH)
    if not os.path.exists(p):
        if args.dev:
            return None
        raise RuntimeError("amendment file missing")
    h = sha256_file(p)
    tracked = subprocess.run(["git", "-C", REPO, "ls-files", "--error-unmatch", AMENDMENT_PATH],
                             capture_output=True, text=True).returncode == 0
    clean = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--", AMENDMENT_PATH]).returncode == 0
    last = subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%H", "--", AMENDMENT_PATH],
                          capture_output=True, text=True).stdout.strip()
    if not args.dev and not (tracked and clean):
        raise RuntimeError("the amendment is not committed and clean; the frozen run may not start (hold)")
    return {"id": AMENDMENT_ID, "path": AMENDMENT_PATH, "sha256": h, "git_tracked": tracked,
            "clean_vs_HEAD": clean, "last_commit": last or None}


def dev_exploration_block():
    """AMD-20260924-3a9f06 C-13 / C-15: dev seeds listed, NO dev value recorded."""
    from common import dev_cell_seeds, DEV_FIXED_SEEDS
    return {
        "statement": "Dev outputs are outside the repository and outside runs/RUN-CERTBIN-0b8f3a/, are not cited, and those holding values of retired streams are not opened (C-15). No dev value is recorded here.",
        "dev_seeds_before_the_amendment": [
            "scratch tests: numpy default_rng(1), default_rng(3), default_rng(5); PCG64(1) (self-test negative control)",
            "selftest.py dev runs: S_selftest = 2026092420099 (self-test items and pass/fail only; before C-15 was received)",
            "dev runs 1 and 2: seed(c, s) + 7 for c = 1..4, s = 1..11 (2026092420108..2026092420118, ..208..218, ..308..318, ..408..418), S_curve19 + 7 = 2026092420008, S_pts19 + 7 = 2026092420009, S_probe + 7 = 2026092420105, S_selftest + 7 = 2026092420106",
            "dev run 3 (started before C-15 was received, stopped on receipt): seed(c, s) + 10^12 for c = 1..4, s = 1..11 (3026092420101..3026092420411), S_curve19 + 10^12 = 3026092420001, S_pts19 + 10^12 = 3026092420002, S_probe + 10^12 = 3026092420098, S_selftest + 10^12 = 3026092420099; none is a version-2 seed or in 2026092430000-2026092430999"],
        "dev_seeds_after_C-15": {"rule": "integers below 10^6, never a version-2 seed",
                                 "cell_formula": "100000 + 100*c + s", "per_cell": {c: dev_cell_seeds(c) for c in (1, 2, 3, 4)},
                                 "fixed": DEV_FIXED_SEEDS},
        "exposure_ledger_facts_(no_values)": {
            "same_routine_same_bound": [{"seed": 2026092420105, "frozen_v1_role": "cell 1 s05 randx",
                                         "dev_use": "dev S_probe, integers(0, 2^17), <= 10 draws per instantiation"}],
            "same_raw_stream_different_routine": [
                {"seeds": [2026092420000 + 100 * c + s for c in (1, 2, 3, 4) for s in (8, 9, 10, 11)],
                 "frozen_v1_roles": "s08 nullF2_test, s09 nullB_ref, s10 nullB_test, s11 affB",
                 "dev_use": "dev s01..s04 (ref, test, sat, plant): integers(0, q) or integers(0, |F_V|)"},
                {"seeds": [2026092420106], "frozen_v1_role": "cell 1 s06 nullAff",
                 "dev_use": "dev pilot generator and dev bootstrap: integers(1, 2^19), integers(0, 2^n), integers(0, len)"}],
            "disposition": "retired and replaced by old + 10000 (AMD C-14)"},
        "issues_found": ["(1) PREFIX/COLUMN precedence", "(2) C-REPLAYB premise", "(3) F-SAT termination",
                         "(4) C-TR literal statement", "(5) modal scope", "(6) probe stream", "(7) EXTRA-PIVOT"],
    }


def cprov_check(run, stage1):
    """C-PROV: the copied/generalized regime-A code, at the Stage-1 cell
    (n = 17, l = 9, Stage-1 curve and V), on the 5 archived F-S3 references and
    the 20 lowest-idx archived F-S3 targets, reproduces rank, 1 in R_D, the four
    trace hashes and the replay first-zero indices at D = 3 and 4."""
    c17, csha = stage1_curve(stage1)
    F = TableField(17, MODULUS17)
    desc = Descent(F, 9)
    B = c17["B"]
    refs_arch = json.load(open(os.path.join(stage1, "references.json")))["F-S3"]["references"]
    tarch = {}
    with gzip.open(os.path.join(stage1, "targets-F-S3.jsonl.gz"), "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["idx"] <= 20:
                tarch[(r["idx"], r["D"])] = r
    oB = OracleB(desc)

    def inst(xR, idx=None, label=None):
        E = desc.descended_E(B, xR)
        sols = oB(E)
        d = {"x_R": xR, "s": len(sols), "sols": sols, "degenerate": xR < 512}
        if idx is not None:
            d["idx"] = idx
        if label is not None:
            d["selected_as"] = label
        return d

    ref_insts = [inst(refs_arch[k]["x_R"], label=k) for k in ("U1", "U2", "U3", "S1", "S2")]
    tg = [inst(tarch[(i, 3)]["x_R"], idx=i) for i in range(1, 21)]
    E0, Ej = desc.affine_basis(B)
    mism = []
    ncmp = 0
    for D in (3, 4):
        S = MacaulayShape(D, desc)
        res, live = engineA.process_family_A(S, "F-S3", D, ref_insts, tg, lambda t: desc.descended_E(B, t["x_R"]),
                                             False, [E0] + Ej, [], run.log, Mapper(1), affine_route=True,
                                             modal_enabled=False)
        for r in res["refs"]:
            a = refs_arch[r["label"]][f"D{D}"]
            for k in ("rank", "one_in_R", "h_rank", "h_set", "h_strict", "h_ops"):
                ncmp += 1
                if r[k] != a[k]:
                    mism.append({"what": "reference", "label": r["label"], "D": D, "field": k, "got": r[k], "archived": a[k]})
        for rec in res["records"]:
            a = tarch[(rec["idx"], D)]
            for k in ("rank", "one_in_R", "h_rank", "h_set", "h_strict", "h_ops"):
                ncmp += 1
                if rec[k] != a[k]:
                    mism.append({"what": "target", "idx": rec["idx"], "D": D, "field": k, "got": rec[k], "archived": a[k]})
            for key in ("U1", "U2", "U3", "S1", "S2"):
                ncmp += 1
                g_ = rec["refs"][key]["replay_first_zero"]
                w_ = a["refs"][key]["replay_first_zero"]
                if g_ != w_:
                    mism.append({"what": "replay_first_zero", "idx": rec["idx"], "D": D, "ref": key, "got": g_, "archived": w_})
    return {"control": "C-PROV", "pass": not mism, "n_compared": ncmp, "mismatches": mism,
            "stage1_run": STAGE1_RUN, "stage1_curve_sha256": csha,
            "stage1_references_sha256": sha256_file(os.path.join(stage1, "references.json")),
            "stage1_targets_sha256": sha256_file(os.path.join(stage1, "targets-F-S3.jsonl.gz")),
            "instances": {"references": ["U1", "U2", "U3", "S1", "S2"], "targets_idx": list(range(1, 21)), "D": [3, 4]},
            "fields_compared": ["rank", "one_in_R", "h_rank", "h_set", "h_strict", "h_ops", "replay_first_zero (per reference)"]}


# ---------------------------------------------------------------------------
# MAIN phases
def load_plan(run, args, spec_text):
    if not args.plan:
        raise RuntimeError("--plan required")
    plan = json.load(open(args.plan))
    errs = verify_plan(plan, spec_text, args)
    if errs:
        raise RuntimeError("plan check failed: " + "; ".join(errs))
    pilot = json.load(open(os.path.join(run.out, "pilot.json")))
    if pilot["schedule"] != plan["schedule"]:
        raise RuntimeError("plan schedule != pilot decision")
    if not args.dev:
        cur = amendment_binding(args)
        if cur["sha256"] != plan["amendment"]["sha256"]:
            raise RuntimeError("amendment sha256 differs from the one bound in the trial plan")
    return plan


def curves_all(run, plan, fields, stage1):
    c17, csha = stage1_curve(stage1)
    curves = {17: {"A": c17["A"], "B": c17["B"], "order": c17["order"], "h": c17["h"], "q": c17["q"],
                   "P": c17["P"], "Q": c17["Q"], "k_Q": c17["k_Q"], "source": f"{STAGE1_RUN}/curve.json",
                   "source_sha256": csha, "draws_rejected": None}}
    if not run.ck_exists("curve19"):
        F = fields[19]
        t = time.time()
        E, info = fam_mod.draw_curve(F, plan["seeds_fixed"]["S_curve19"])
        P, Q, kQ, pinfo = fam_mod.draw_points(E, info["h"], info["q"], plan["seeds_fixed"]["S_pts19"])
        info.update({"P": list(P), "Q": list(Q), "k_Q": kQ, "points_draw": pinfo,
                     "source": "S_curve19 / S_pts19 (Stage-1 rules)", "wall_seconds": time.time() - t})
        run.ck_save("curve19", info)
        run.log(f"n = 19 curve: A={info['A']} B={info['B']} #E={info['order']} h={info['h']} q={info['q']}")
    curves[19] = run.ck_load("curve19")
    return curves


def main_phases(run, args, spec, spec_text):
    for p in ("selftest.json", "cprov.json", "pilot.json"):
        if not os.path.exists(os.path.join(run.out, p)):
            run.log(f"{p} missing: phase 0 incomplete; stop before any frozen stream")
            return 4
    if not json.load(open(os.path.join(run.out, "selftest.json")))["all_pass"]:
        run.log("self-test failed; stop")
        return 4
    plan = load_plan(run, args, spec_text)
    stage1 = os.path.abspath(args.stage1_run) if args.stage1_run else os.path.join(REPO, STAGE1_RUN)
    if not args.dev and stage1 != os.path.join(REPO, STAGE1_RUN):
        raise RuntimeError("--stage1-run must be the specification's Stage-1 run")
    cprov = json.load(open(os.path.join(run.out, "cprov.json")))
    regimeA_void = not cprov["pass"]
    existing = [f for f in os.listdir(run.ck) if f.endswith(".json.gz")]
    if existing and not args.resume:
        run.log(f"checkpoints exist ({len(existing)}); use --resume")
        return 5
    if not run.ck_exists("plan-bound"):
        run.ck_save("plan-bound", {"at": now(), "plan_sha256": sha256_file(args.plan), "schedule": plan["schedule"],
                                   "note": "recorded before the first frozen stream draw"})
    mod19, abc = load_mod19(run)
    fields = {17: TableField(17, MODULUS17), 19: TableField(19, mod19)}
    curves = curves_all(run, plan, fields, stage1)
    counts = plan["counts"]
    cells = [c for c in CELLS if not args.dev_cells or cell_label(c[1], c[2]) in args.dev_cells.split(",")]
    extras = {}
    workers = 1
    if run.ck_exists("workers-identity"):
        wi = run.ck_load("workers-identity")
        workers = wi["workers_enabled"]
    for cidx, n, l in cells:
        C = build_cell_ctx(run, plan, cidx, n, l, fields, curves, run.log)
        xE, x2E, ctr, sub = curve_extras(C, extras)
        C.xE, C.x2E, C.ctr = xE, x2E, ctr
        name1 = f"p1-{C.label}"
        if not run.ck_exists(name1):
            t = time.time()
            ts = now()
            run.log(f"phase 1 {C.label}: curve targets, references, oracles")
            P1 = fam_mod.run_phase1_cell(C.F, {"n": n, "l": l, "cidx": cidx, "label": C.label}, curves[n], C.E,
                                         C.P, C.Q, C.desc, C.seeds, counts, xE, x2E, sub, run.log)
            P1["C-TR"] = ctr
            P1["_meta"] = unit_meta(ts, now(), time.time() - t)
            run.ck_save(name1, P1)
        P1 = run.ck_load(name1)
        if cidx == 1 and not run.ck_exists("workers-identity"):
            wi = identity_check(run, C, P1)
            run.ck_save("workers-identity", wi)
            workers = wi["workers_enabled"]
            run.log(f"worker identity check: identical={wi['identical']}; workers = {workers}")
        mapper = Mapper(workers)
        if not regimeA_void:
            phase2_cell(run, C, P1, mapper)
        phase3_cell(run, C, P1, mapper)
        phase4_cell(run, C, P1, plan)
        phase5_cell(run, C, P1, mapper, counts, regimeA_void)
        for key in [k for k in _LIVE if k[0] == C.label]:
            del _LIVE[key]
        engineA.set_unit_globals()
        engineB.set_unit_globals()
        import gc
        gc.collect()
    if args.dev_cells:
        run.log("dev: subset of cells done")
    # cells.json and certificates
    if not os.path.exists(os.path.join(run.out, "cells.json")):
        write_cells_json(run, plan, curves, fields, mod19, abc, cells)
    if not run.ck_exists("p7a-certificates"):
        phase7a(run, plan, fields, curves, cells, counts, regimeA_void)
    if not run.ck_exists("p6-determinism"):
        run.log("phases 1-5 and 7a complete. NEXT: the determinism command (separate process), then the verify command, then --resume")
        return 0
    if not os.path.exists(os.path.join(run.out, "ps0prime-verification.json")):
        run.log("ps0prime-verification.json missing: run the verify command, then --resume")
        return 0
    if run.ck_exists("p8-done"):
        run.log("phase 8 already complete")
        return 0
    import report
    ts = now()
    t = time.time()
    run.log("phase 8: aggregation, decision rules, run report")
    report.phase8(run, args, plan, spec, spec_text, fields, curves, cells)
    run.ck_save("p8-done", unit_meta(ts, now(), time.time() - t))
    run.log("phase 8 complete")
    return 0


def unit_meta(t_start, t_end, wall):
    return {"started_at": t_start, "finished_at": t_end, "wall_seconds": wall, "peak_rss_bytes": peak_rss(),
            "peak_rss_children_bytes": peak_rss_children(), "pid": os.getpid()}


def meminfo_available():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) * 1024
    except Exception:
        return None


# ---------------------------------------------------------------------------
def curve_builder(C):
    B = C.E.B
    return lambda t: C.desc.descended_E(B, t["x_R"])


def fs3_refs_A(run, C, P1, D, live_cache):
    key = (C.label, "A", D)
    if key in live_cache:
        return live_cache[key]
    unit = run.ck_load(f"p2-{C.label}-A-F-S3-D{D}")
    S = C.shapesA[D]
    E0, Ej = C.desc.affine_basis(C.E.B)
    planesM = np.stack([S.build(x) for x in [E0] + Ej])
    bE = curve_builder(C)
    refs = []
    for inst in P1["F-S3"]["refs"]:
        refs.append(engineA.make_ref(S, S.build(bE(inst)), inst, inst["selected_as"], "F-S3", planesM))
    if unit["modal_info"]:
        midx = unit["modal_info"]["modal_idx"]
        minst = next(t for t in P1["F-S3"]["targets"] if t["idx"] == midx)
        refs.append(engineA.make_ref(S, S.build(bE(minst)), minst, "modal", "F-S3", planesM))
    want = {r["label"]: r["h_ops"] for r in unit["refs"]}
    for r in refs:
        if want[r.label] != r.res.h_ops:
            raise RuntimeError(f"rebuilt F-S3 regime-A reference {r.label} D={D} differs from checkpoint")
    live_cache[key] = refs
    return refs


def fs3_refs_B(run, C, P1, live_cache):
    key = (C.label, "B")
    if key in live_cache:
        return live_cache[key]
    unit = run.ck_load(f"p3-{C.label}-B-F-S3")
    refs = []
    insts = with_coeffs(C, [dict(x) for x in P1["F-S3"]["refs"]], "curve")
    for inst in insts:
        refs.append(engineB.make_ref_B(C.SB, C.T, C.SB.build(inst["coeffs"]), inst, inst["selected_as"], "F-S3",
                                       C.l, C.dc, C.oC))
    if unit["modal_info"]:
        midx = unit["modal_info"]["modal_idx"]
        minst = with_coeffs(C, [dict(next(t for t in P1["F-S3"]["targets"] if t["idx"] == midx))], "curve")[0]
        refs.append(engineB.make_ref_B(C.SB, C.T, C.SB.build(minst["coeffs"]), minst, "modal", "F-S3", C.l, C.dc, C.oC))
    want = {r["label"]: r["h_ops"] for r in unit["refs"]}
    for r in refs:
        if want[r.label] != r.res.h_ops:
            raise RuntimeError(f"rebuilt F-S3 regime-B reference {r.label} differs from checkpoint")
    live_cache[key] = refs
    return refs


_LIVE = {}


def run_unit_A(run, C, fam, D, ref_insts, targets, build_E, planes_E, cross, mapper, affine_route, modal_enabled,
               extra_forms=None):
    name = f"p2-{C.label}-A-{fam}-D{D}"
    if run.ck_exists(name):
        return None
    ts, t = now(), time.time()
    S = C.shapesA[D]
    res, live = engineA.process_family_A(S, fam, D, ref_insts, targets, build_E, False, planes_E, cross, run.log,
                                         mapper, affine_route=affine_route, modal_enabled=modal_enabled)
    if affine_route:
        forms = {}
        for r in res["refs"]:
            if "forms_a" in r:
                forms[r["label"]] = (r["forms_a0"], r["forms_a"], r.get("x_R"))
        for key, r in cross:
            if r.forms is not None:
                forms[key] = (r.forms[0].tolist(), r.forms[1].tolist(), r.inst.get("x_R"))
        res["_ref_forms"] = forms
        summ, hazards, cforms = family_hull_analysis(res, C.n)
        res.pop("_ref_forms")
        res["hull"] = summ
        res["hazards"] = hazards
        res["cforms_matmul"] = cforms
    res.update(unit_meta(ts, now(), time.time() - t))
    run.ck_save(name, res)
    if fam == "F-S3":
        for r in live:
            r.group = "F-S3"
        _LIVE[(C.label, "A", D)] = live
    return res


def phase2_cell(run, C, P1, mapper):
    bE = curve_builder(C)
    E0, Ej = C.desc.affine_basis(C.E.B)
    planes = [E0] + Ej
    for D in (3, 4):
        run_unit_A(run, C, "F-S3", D, P1["F-S3"]["refs"], P1["F-S3"]["targets"], bE, planes, [], mapper, True, True)
        cross = [(f"F-S3:{r.label}", r) for r in fs3_refs_A(run, C, P1, D, _LIVE)]
        run_unit_A(run, C, "F-SAT", D, [], P1["F-SAT"]["targets"], bE, planes, cross, mapper, True, False)
        run_unit_A(run, C, "F-PLANT", D, [], P1["F-PLANT"]["targets"], bE, planes, cross, mapper, True, False)
        run_unit_A(run, C, "F-RANDX", D, P1["F-RANDX"]["refs"], P1["F-RANDX"]["targets"], bE, planes, cross, mapper,
                   True, True)
        A0 = fam_mod.E_from_hex(P1["F-AFF"]["A0_hex"], len(C.desc.eq_mons))
        Aj = [fam_mod.E_from_hex(x, len(C.desc.eq_mons)) for x in P1["F-AFF"]["Aj_hex"]]

        def b_aff(inst, A0=A0, Aj=Aj):
            return C.desc.affine_combine(A0, Aj, inst["x_R"])
        run_unit_A(run, C, "F-AFF", D, P1["F-AFF"]["refs"], P1["F-AFF"]["targets"], b_aff, [A0] + Aj, [], mapper,
                   True, True)
        ncols = len(C.desc.eq_mons)
        run_unit_A(run, C, "F-NULLF2", D, P1["F-NULLF2"]["refs"], P1["F-NULLF2"]["targets"],
                   lambda inst: fam_mod.E_from_hex(inst["E_hex"], ncols), None, [], mapper, False, True)


def run_unit_B(run, C, fam, ref_insts, targets, cross, mapper, modal_enabled, reverse=False, name=None):
    name = name or f"p3-{C.label}-B-{fam}"
    if run.ck_exists(name):
        return None
    ts, t = now(), time.time()
    res, live, oplogs = engineB.process_family_B(C.SB, C.T, fam, ref_insts, targets, reverse, cross, run.log, mapper,
                                                 C.l, C.dc, C.oC, modal_enabled=modal_enabled)
    res.update(unit_meta(ts, now(), time.time() - t))
    run.ck_save(name, res)
    if fam == "F-S3" and not reverse:
        for r in live:
            r.group = "F-S3"
        _LIVE[(C.label, "B")] = live
    return res


def phase3_cell(run, C, P1, mapper):
    s3 = with_coeffs(C, [dict(x) for x in P1["F-S3"]["targets"]], "curve")
    s3r = with_coeffs(C, [dict(x) for x in P1["F-S3"]["refs"]], "curve")
    run_unit_B(run, C, "F-S3", s3r, s3, [], mapper, True)
    cross = [(f"F-S3:{r.label}", r) for r in fs3_refs_B(run, C, P1, _LIVE)]
    run_unit_B(run, C, "F-SAT", [], with_coeffs(C, [dict(x) for x in P1["F-SAT"]["targets"]], "curve"), cross, mapper, False)
    run_unit_B(run, C, "F-PLANT", [], with_coeffs(C, [dict(x) for x in P1["F-PLANT"]["targets"]], "curve"), cross, mapper, False)
    run_unit_B(run, C, "F-RANDX", with_coeffs(C, [dict(x) for x in P1["F-RANDX"]["refs"]], "curve"),
               with_coeffs(C, [dict(x) for x in P1["F-RANDX"]["targets"]], "curve"), cross, mapper, True)
    run_unit_B(run, C, "F-NULLB", P1["F-NULLB"]["refs"], P1["F-NULLB"]["targets"], [], mapper, True)
    run_unit_B(run, C, "F-AFFB", P1["F-AFFB"]["refs"], P1["F-AFFB"]["targets"], [], mapper, True)


def phase4_cell(run, C, P1, plan):
    name = f"p4-{C.label}"
    if run.ck_exists(name):
        return
    ts, t0 = now(), time.time()
    from detmod import DetField
    DF = DetField(C.n, C.F.mod)
    refs = fs3_refs_B(run, C, P1, _LIVE)
    unsat_refs = [r for r in refs if r.label.startswith("U")]
    out = {"cell": C.label, "per_ref": {}, "C-BREAK": {"checks": [], "matched_full_minor": []},
           "C-REPLAYB": {}, "row_order_replays": {}}
    # instances by family for rebuilding original matrices
    inst_by = {}
    for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX"):
        inst_by[fam] = {t["idx"]: t for t in with_coeffs(C, [dict(x) for x in P1[fam]["targets"]], "curve")}
    for fam in ("F-NULLB", "F-AFFB"):
        inst_by[fam] = {t["idx"]: t for t in P1[fam]["targets"]}
    units = {fam: run.ck_load(f"p3-{C.label}-B-{fam}") for fam in ("F-S3", "F-SAT", "F-PLANT", "F-RANDX", "F-NULLB", "F-AFFB")}
    # --- K_B probes: ONE PCG64(S_probe) stream across cells 1..4 (AMD-20260924-3a9f06 C-6)
    g, pos = probe_stream(run, plan, C.cidx)
    out["S_probe_stream_position_at_cell_start"] = pos
    draws = []
    for r in unsat_refs:
        kb = engineB.kb_probes(C.SB, C.T, r, lambda x: s3_coeffs(C.F, C.E.B, x), g, C.F.q,
                               max_draws=FIXED_COUNTS["K_B_max_draws"], want=FIXED_COUNTS["K_B_probes"],
                               draw_log=draws)
        for tr in kb["tried"]:
            tr["draw_index"] = pos + tr["draw_index"]
        out["per_ref"][r.label] = {"K_B": kb["K_B"], "probes": kb, "L": len(r.p)}
        run.log(f"    K_B {C.label} {r.label}: {kb['K_B']} ({kb['probes_accepted']} probes)")
    out["S_probe_draws"] = {"n": C.n, "bound": C.F.q, "values": draws}
    # --- C-REPLAYB (v2) and v1 replays on ROW-ORDER divergers (data)
    for r in unsat_refs:
        keys = {"F-S3": r.label}
        for fam in ("F-SAT", "F-PLANT", "F-RANDX"):
            keys[fam] = f"F-S3:{r.label}"
        ro = []
        for fam, key in keys.items():
            for rec in units[fam]["records"]:
                d = rec["refs"].get(key)
                if d and d.get("type") == "ROW-ORDER":
                    t = inst_by[fam][rec["idx"]]
                    rp = engineB.replay(C.SB.build(t["coeffs"]), C.T, r.p, r.c, r.res.X, stop_at_zero=True)
                    ro.append({"family": fam, "idx": rec["idx"], "x_R": rec["x_R"], "stratum": rec["stratum"],
                               "first_zero": rp["first_zero"], "first_invalid": rp["first_invalid"],
                               "survived": rp["survived"], "schedule_valid": rp["first_invalid"] is None})
        out["row_order_replays"][r.label] = ro
        matched = [rec for rec in units["F-S3"]["records"]
                   if not rec["degenerate"] and rec["stratum"] == "unsat"
                   and rec["refs"].get(r.label, {}).get("match", {}).get("strict")]
        matched.sort(key=lambda x: x["idx"])
        sel = [inst_by["F-S3"][rec["idx"]] for rec in matched[:FIXED_COUNTS["C-REPLAYB_matched_per_ref"]]]
        rb = engineB.replayb_v2(C.SB, C.T, DF, r, sel)
        rb["n_matched_available"] = len(matched)
        out["C-REPLAYB"][r.label] = rb
        run.log(f"    C-REPLAYB v2 {C.label} {r.label}: pass={rb['pass']} valid {rb['n_schedule_valid']}/{rb['n_matched_checked']} "
                f"label={rb['label']}")
    # --- C-BREAK: every ZERO-PIVOT first divergence against an unsat reference
    ref_tables = {}
    for fam, u in units.items():
        for rr in u["refs"]:
            ref_tables[(fam, rr["label"])] = rr
    for fam, u in units.items():
        for rec in u["records"]:
            for key, d in rec["refs"].items():
                if d.get("type") != "ZERO-PIVOT":
                    continue
                if ":" in key:
                    rfam, rlab = key.split(":")
                else:
                    rfam, rlab = fam, key
                rr = ref_tables.get((rfam, rlab))
                if rr is None or rr["s"] != 0:
                    continue
                t = inst_by[fam][rec["idx"]]
                Mo = C.SB.build(t["coeffs"])

                class _R:
                    pass
                ro_ = _R()
                ts_ = np.array(rr["T_strict"], dtype=np.int64)
                ro_.p, ro_.c = ts_[:, 0], ts_[:, 1]
                cb = engineB.cbreak_check(Mo, ro_, d["kdiv"], DF)
                cb.update({"family": fam, "idx": rec["idx"], "x_R": rec["x_R"], "ref": key, "stratum": rec["stratum"]})
                out["C-BREAK"]["checks"].append(cb)
    matched20 = []
    for r in unsat_refs:
        for rec in sorted(units["F-S3"]["records"], key=lambda x: x["idx"]):
            if len(matched20) >= FIXED_COUNTS["C-BREAK_matched_per_cell"]:
                break
            if rec["refs"].get(r.label, {}).get("match", {}).get("strict") and rec["idx"] not in [m[1] for m in matched20]:
                matched20.append((r, rec["idx"]))
    for r, idx in matched20:
        t = inst_by["F-S3"][idx]
        from detmod import minor
        d = minor(C.SB.build(t["coeffs"]), r.p, r.c, DF)
        out["C-BREAK"]["matched_full_minor"].append({"ref": r.label, "idx": idx, "minor_all_L_pivots": int(d),
                                                     "L": len(r.p), "pass": d != 0})
    cbs = out["C-BREAK"]
    cbs["pass"] = all(c["pass"] for c in cbs["checks"]) and all(c["pass"] for c in cbs["matched_full_minor"])
    out["C-REPLAYB_pass"] = all(v["pass"] for v in out["C-REPLAYB"].values())
    out.update(unit_meta(ts, now(), time.time() - t0))
    run.ck_save(name, out)
    run.log(f"  phase 4 {C.label}: C-BREAK checks {len(cbs['checks'])} + {len(cbs['matched_full_minor'])} matched; "
            f"pass={cbs['pass']} ({time.time() - t0:.0f}s)")


def probe_stream(run, plan, cidx):
    """The ONE S_probe generator, consumed in cell order 1..4. For cell cidx,
    re-create it and re-draw (and verify) the recorded draws of every earlier
    cell, so that --resume regenerates the sequence exactly."""
    g = np.random.Generator(np.random.PCG64(plan["seeds_fixed"]["S_probe"]))
    pos = 0
    for c2, n2, l2 in CELLS:
        if c2 >= cidx:
            break
        name = f"p4-{cell_label(n2, l2)}"
        if not run.ck_exists(name):
            raise RuntimeError(f"S_probe stream: {name} missing; cells must be processed in cell order")
        rec = run.ck_load(name)["S_probe_draws"]
        for v in rec["values"]:
            x = int(g.integers(0, rec["bound"]))
            if x != v:
                raise RuntimeError("S_probe stream regeneration mismatch")
            pos += 1
    return g, pos


def phase5_cell(run, C, P1, mapper, counts, regimeA_void):
    n_rev = counts["C-REV"]
    tg = [dict(t) for t in P1["F-S3"]["targets"] if t["idx"] <= n_rev]
    if not regimeA_void:
        bE = curve_builder(C)
        for D in (3, 4):
            name = f"p5-{C.label}-A-D{D}"
            if run.ck_exists(name):
                continue
            ts, t = now(), time.time()
            res, live = engineA.process_family_A(C.shapesA[D], "F-S3-REV", D, P1["F-S3"]["refs"], tg, bE, True, None,
                                                 [], run.log, mapper, affine_route=False, modal_enabled=False)
            res.update(unit_meta(ts, now(), time.time() - t))
            run.ck_save(name, res)
    name = f"p5-{C.label}-B"
    if not run.ck_exists(name):
        run_unit_B(run, C, "F-S3-REV", with_coeffs(C, [dict(x) for x in P1["F-S3"]["refs"]], "curve"),
                   with_coeffs(C, tg, "curve"), [], mapper, False, reverse=True, name=name)


# ---------------------------------------------------------------------------
def identity_check(run, C, P1):
    """Serial vs sharded byte identity on the 20 lowest-idx F-S3 targets of the
    first cell, both regimes (regime A at D = 3 and 4)."""
    tg = sorted(P1["F-S3"]["targets"], key=lambda t: t["idx"])[:20]
    out = {"cell": C.label, "targets_idx": [t["idx"] for t in tg], "comparisons": []}
    ident = True
    bE = curve_builder(C)
    E0, Ej = C.desc.affine_basis(C.E.B)
    for D in (3, 4):
        blobs = []
        for w in (1, 2):
            res, _ = engineA.process_family_A(C.shapesA[D], "F-S3", D, P1["F-S3"]["refs"], [dict(t) for t in tg], bE,
                                              False, [E0] + Ej, [], run.log, Mapper(w), affine_route=True,
                                              modal_enabled=False)
            b = json.dumps(res["records"], default=jdefault, sort_keys=True).encode()
            blobs.append(b)
        same = blobs[0] == blobs[1]
        ident &= same
        out["comparisons"].append({"regime": "A", "D": D, "serial_sha256": hashlib.sha256(blobs[0]).hexdigest(),
                                   "sharded_sha256": hashlib.sha256(blobs[1]).hexdigest(), "identical": same})
    blobs = []
    for w in (1, 2):
        res, _, _ = engineB.process_family_B(C.SB, C.T, "F-S3", with_coeffs(C, [dict(x) for x in P1["F-S3"]["refs"]], "curve"),
                                             with_coeffs(C, [dict(t) for t in tg], "curve"), False, [], run.log,
                                             Mapper(w), C.l, C.dc, C.oC, modal_enabled=False)
        blobs.append(json.dumps(res["records"], default=jdefault, sort_keys=True).encode())
    same = blobs[0] == blobs[1]
    ident &= same
    out["comparisons"].append({"regime": "B", "D": 66, "serial_sha256": hashlib.sha256(blobs[0]).hexdigest(),
                               "sharded_sha256": hashlib.sha256(blobs[1]).hexdigest(), "identical": same})
    avail = meminfo_available()
    out["identical"] = ident
    out["mem_available_bytes"] = avail
    out["workers_enabled"] = 2 if (ident and (avail is None or avail >= 6 * 1024 ** 3)) else 1
    out["rule"] = "2 workers iff serial and sharded outputs are byte-identical (and MemAvailable >= 6 GiB); else 1"
    out["at"] = now()
    return out


# ---------------------------------------------------------------------------
def write_cells_json(run, plan, curves, fields, mod19, abc, cells):
    out = {"experiment_id": EXP_ID, "cells": {}}
    for cidx, n, l in cells:
        lab = cell_label(n, l)
        P1 = run.ck_load(f"p1-{lab}")
        F = fields[n]
        SB = ShapeB(F, l)
        cu = curves[n]
        tau = [F.trace(1 << j) for j in range(n)]
        out["cells"][lab] = {
            "cidx": cidx, "n": n, "l": l, "modulus": modulus_string(F.mod), "modulus_int": F.mod,
            "modulus_rule": ("Stage-1 field t^17 + t^3 + 1" if n == 17 else
                             f"lexicographically smallest irreducible pentanomial; (a, b, c) = {list(abc)}"),
            "A": cu["A"], "B": cu["B"], "order": cu["order"], "h": cu["h"], "q": cu["q"], "P": cu["P"], "Q": cu["Q"],
            "k_Q": cu["k_Q"], "curve_source": cu.get("source"), "curve_rejections": cu.get("rejections"),
            "points_draw": cu.get("points_draw"),
            "V": f"span_F2{{1, t, ..., t^{l - 1}}} = the integers 0..{(1 << l) - 1}",
            "L_V_lambda": SB.lam, "tau": tau, "Tr_A": F.trace(cu["A"]),
            "seeds": next(c["seeds"] for c in plan["cells"] if c["cidx"] == cidx),
            "rejections": P1["rejections"],
            "E_SAT_size": P1["F-SAT"].get("E_SAT_size"), "E_PLANT_size": P1["F-PLANT"].get("E_PLANT_size"),
            "P_sat_exact": P1["F-SAT"].get("P_sat_exact"),
            "F-PLANT_draws": P1["F-PLANT"].get("draws"),
            "P_sat_draws": {"F-SAT_draws": P1["F-SAT"]["draws"], "F-SAT_kept": len(P1["F-SAT"]["targets"]),
                            "F-SAT_stop_reason": P1["F-SAT"]["stop_reason"],
                            "F-SAT_unsat_rejections": P1["F-SAT"]["unsat_rejections"],
                            "F-SAT_distinct_nondegenerate_new_x_seen": P1["F-SAT"]["distinct_nondegenerate_new_x_seen"],
                            "sat_population_subgroup": P1["F-SAT"]["population_size_sat_subgroup_nondegenerate"]},
            "F-PLANT": {"factor_base_size": P1["F-PLANT"]["factor_base_size"],
                        "achievable_distinct_z": P1["F-PLANT"]["achievable_distinct_z"],
                        "stop_reason": P1["F-PLANT"]["stop_reason"]},
            "reference_shortfalls": {f: P1[f]["ref_shortfall"] for f in ("F-S3", "F-RANDX", "F-AFF", "F-NULLF2", "F-NULLB", "F-AFFB")},
            "F-AFFB_alpha": P1["F-AFFB"]["alpha"],
            "C-TR": P1["C-TR"],
        }
    run.write_new("cells.json", out)


def phase7a(run, plan, fields, curves, cells, counts, regimeA_void):
    import certs
    ts, t0 = now(), time.time()
    lines = []
    summary = []
    N = FIXED_COUNTS["PS0prime_per_cell_regime"]
    for cidx, n, l in cells:
        lab = cell_label(n, l)
        F = fields[n]
        B = curves[n]["B"]
        desc = Descent(F, l)
        if not regimeA_void:
            chosen_D = None
            for D in (4, 3):
                u = run.ck_load(f"p2-{lab}-A-F-S3-D{D}")
                cand = [r for r in u["records"] if r["stratum"] == "unsat" and r["one_in_R"]]
                if cand:
                    chosen_D = D
                    break
            if chosen_D is not None:
                S = MacaulayShape(chosen_D, desc)
                for r in sorted(cand, key=lambda x: x["idx"])[:N]:
                    c = certs.cert_A(S, desc.descended_E(B, r["x_R"]))
                    lines.append({"cell": lab, "regime": "A", "D": chosen_D, "idx": r["idx"], "x_R": r["x_R"], **c})
            summary.append({"cell": lab, "regime": "A", "D": chosen_D,
                            "n": sum(1 for x in lines if x["cell"] == lab and x["regime"] == "A")})
        u = run.ck_load(f"p3-{lab}-B-F-S3")
        cand = [r for r in u["records"] if r["stratum"] == "unsat" and r["one_in_R"]]
        SB = ShapeB(F, l)
        T = GFTabs(F)
        for r in sorted(cand, key=lambda x: x["idx"])[:N]:
            c = certs.cert_B(SB, T, s3_coeffs(F, B, r["x_R"]))
            lines.append({"cell": lab, "regime": "B", "D": 66, "idx": r["idx"], "x_R": r["x_R"], **c})
        summary.append({"cell": lab, "regime": "B", "D": 66, "n": len(cand[:N]),
                        "unsat_with_one_in_R66": len(cand)})
        run.log(f"  PS0' certificates {lab}: {summary[-2:] if not regimeA_void else summary[-1:]}")
    p = os.path.join(run.out, "ps0prime-certificates.jsonl.gz")
    if os.path.exists(p):
        raise RuntimeError(f"{p} exists")
    with gzip.open(p + ".tmp", "wt") as f:
        for x in lines:
            f.write(json.dumps(x, default=jdefault, separators=(",", ":")) + "\n")
    os.replace(p + ".tmp", p)
    run.ck_save("p7a-certificates", {"summary": summary, "n": len(lines),
                                     "self_check_all": all(x.get("self_check") for x in lines),
                                     **unit_meta(ts, now(), time.time() - t0)})


# ---------------------------------------------------------------------------
def phase6(run, args, spec, spec_text):
    """C-DET in a separate process: re-derive the matrices from the stored
    instances and compare T_ops hashes (references + modal + C-DET targets,
    both regimes, both regime-A D)."""
    if run.ck_exists("p6-determinism"):
        run.log("phase 6 checkpoint exists; nothing to do")
        return 0
    plan = load_plan(run, args, spec_text)
    ts, t0 = now(), time.time()
    mod19, abc = load_mod19(run)
    fields = {17: TableField(17, MODULUS17), 19: TableField(19, mod19)}
    stage1 = os.path.abspath(args.stage1_run) if args.stage1_run else os.path.join(REPO, STAGE1_RUN)
    curves = curves_all(run, plan, fields, stage1)
    cprov = json.load(open(os.path.join(run.out, "cprov.json")))
    nd = plan["counts"]["C-DET"]
    out = {"process": {"pid": os.getpid(), "ppid": os.getppid(), "argv": sys.argv, "started_at": ts,
                       "note": "separate process invocation; every matrix re-derived from the stored instances"},
           "per_unit": [], "mismatches": [], "checked": 0, "matched": 0}
    cells = [c for c in CELLS if not args.dev_cells or cell_label(c[1], c[2]) in args.dev_cells.split(",")]
    from elim import eliminate as elimA
    for cidx, n, l in cells:
        C = build_cell_ctx(run, plan, cidx, n, l, fields, curves, run.log)
        P1 = run.ck_load(f"p1-{C.label}")
        targets = [t for t in P1["F-S3"]["targets"] if t["idx"] <= nd]
        units = []
        if cprov["pass"]:
            units += [("A", D) for D in (3, 4)]
        units.append(("B", 66))
        for reg, D in units:
            u = run.ck_load(f"p2-{C.label}-A-F-S3-D{D}" if reg == "A" else f"p3-{C.label}-B-F-S3")
            want_t = {r["idx"]: r["h_ops"] for r in u["records"]}
            want_r = {r["label"]: r["h_ops"] for r in u["refs"]}
            insts = [(i["selected_as"], i) for i in P1["F-S3"]["refs"]]
            if u["modal_info"]:
                insts.append(("modal", next(x for x in P1["F-S3"]["targets"] if x["idx"] == u["modal_info"]["modal_idx"])))
            m = c = 0
            for lab, inst in insts + [(None, t) for t in targets]:
                if reg == "A":
                    S = C.shapesA[D]
                    res, _, _ = elimA(S.build(C.desc.descended_E(C.E.B, inst["x_R"])), S.C, keep_ops=False,
                                      with_row_pass=False)
                else:
                    res, _, _ = eliminate_B(C.SB.build(s3_coeffs(C.F, C.E.B, inst["x_R"])), C.T, with_row_pass=False)
                want = want_r[lab] if lab else want_t[inst["idx"]]
                ok = res.h_ops == want
                c += 1
                m += ok
                if not ok:
                    out["mismatches"].append({"cell": C.label, "regime": reg, "D": D, "ref": lab, "idx": inst.get("idx")})
            out["per_unit"].append({"cell": C.label, "regime": reg, "D": D, "checked": c, "matched": m})
            out["checked"] += c
            out["matched"] += m
            run.log(f"  determinism {C.label} {reg} D={D}: {m}/{c}")
    out["pass"] = out["checked"] > 0 and out["checked"] == out["matched"]
    out.update(unit_meta(ts, now(), time.time() - t0))
    run.ck_save("p6-determinism", out)
    run.log(f"phase 6 complete: {out['matched']}/{out['checked']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
