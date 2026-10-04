#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r4 stage (TASK-20260924-d91a96) -- DV-7: TOY INTEGRATION of the DELIVERED r4 layer (paristack PS-6
DV-7 with RC-3, RC-8; solverevent SE-5 (the probe) and SE-8; healthresolve HR-9 (controls-a1 through the r4 a1 entry);
DEC-20260924-15a77a SC-11 (f); DEC-20260924-daf670 LKA-11 (a)), with the dynamic part of DV-1 (every PARI entry), the
dynamic part of DV-11 (every fork of the frozen run_child, with its launching site and the wrapped-call intervals),
DV-13 and DV-14. Development only: never imported by an entry point, the wrapper or the checker. Started from
implementation-v2-r3/r3_dv7.py (the toy construction of stage R1's DV-7, reproduced; no r1, r2 or r3 module is
imported).

Called as `python3 -B r5_devchecks.py dv7 --out DIR`. Everything it writes goes under DIR.

Toy objects (NO ladder or fixture prime is solved; toy primes only):
  * n = m = 3 fixture data at 1033 and 1039 (stage R1's construction and declared stream label), n = m = 4 data at 1033;
  * toy ladder rungs chosen by the frozen a1_toy.toy_ladder (gp in capped children, launched through the DELIVERED r4
    launch recorder installed over the frozen run_child in this development process): 1021 (addendum role) and the
    first complete prime of a declared candidate list (v2 role);
  * toy copies of BOTH r4 plans (same ids, same metadata, same repair block): G1 -> fixture --p 1033, G2 -> fixture
    --p 1039, F-4 -> the toy n = 4 data, the 4111 build and its six cells -> the v2-role toy prime with the m = 5 / m = 4
    roles played by m = 3 / m = 2; controls_a1, the addendum build and its six cells -> 1021. Toy-only m = 2 watchdog
    keys are added to both toy copies AND to the toy copy of trial-plan-v2.json (so R-9 runs unmodified).
SYNTHETIC PACKAGES, DECLARED HERE BEFORE ANY LAUNCH: G3 (anchor-identity) and G4 (controls) are synthetic in the toy
(their frozen commands hard-code 16777291 / 4111 and are run instead by DV-18 (a), (b) at those parameters, RB-5); the
v2 builds and cells at 262151 and 16777291 are synthetic rows. A synthetic package carries no launch record and no
r4-conforming manifest, so the r4 checker FAILs it; under RB-4 (b) / RL-4 every later package that requires or reads
one is REFUSED by preflight. Each toy package is therefore run as RK-4 (a) / RF-4 (a) word the development method:
the wrapper's preflight first, its refusals recorded verbatim; the refusals that name a DECLARED SYNTHETIC package
("R-7 (RB-4 (b)) the r5 checker on gate package <synthetic>" and "R-8 (RL-4; RF-3 (b) designed stop) read package
<synthetic>") are EXPECTED and listed; ANY OTHER refusal is a DV-7 failure and the package is not launched; then the
wrapper's `launch` for the package in this process. No bypass flag, mode or argument is added to the r4 wrapper.
Contingency launches are not exercised here (every R-12 refusal is exercised by DV-6).

SE-5 PROBE (run ONCE): world A runs toy G1 with PYTHONHASHSEED "0" (the delivered condition, SE-6); world B runs the
SAME toy G1 in a separate process with PYTHONHASHSEED "12345", set by the development-only in-process override of
r5_run_wrapper.DRIVER_PYTHONHASHSEED (SC-11 (f)); both under SE-2 with K = 5. REG-1 (d-parsed) compares world B's
RECORDED results with world A's. Any difference in a REG-1-compared field STOPS the stage.
The rest of the lineage runs in world A (delivered condition), with REG-1 in R-7 evaluated against world B's G1.
In-process stubs (disclosed): r5_run_wrapper.git_tree_state returns the r4 files tracked and clean; a synthetic
TASK-20260924-4a47e5 phase-A receipt in scratch binds the r4 files as they are (commit_sha: the repository HEAD) and a
synthetic phase-B receipt binds the toy v2 packages (RC-8 form).
DEVELOPMENT TRACE (entry and checker child processes, via the shim; never delivered): (1) the module global `os` of
v2_solver is a delegating proxy whose `fork` calls the real os.fork and, in the PARENT only, appends one trace line
(pid, argv[0] and tag read from the frozen _run_child_locked frame, the launching site from the stack, whether a
wrapped call is in progress); it sits BENEATH the RL-1 recorder (the recorder, its RG-1 callback and the RL-5
read-back are untouched); (2) r5_resolve._call_original (the documented development indirection) is wrapped to log
each wrapped call's interval; (3) cypari2.Pari is subclassed to log PARI entries (DV-1 dynamic).
"""
import contextlib
import copy
import datetime
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402

TOY_A1_P, TOY_FX3, TOY_FX4_P = 1021, (1033, 1039), 1033
TOY_V2_CANDIDATES = (1031, 1051, 1061, 1091, 1151, 1171, 1181, 1201)   # declared order; the first complete rung is used
SEED_A, SEED_B = "0", "12345"
SYN = "SYNTHETIC (DV-7 only): written by the check; never a measurement"
M_ROLE = {5: 3, 4: 2}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(p):
    return R.sha256_file(p)


# ============================================================================ toy data (stage R1 DV-7 construction)
def toy_fixture_n3(p):
    sys.path.insert(0, R.V2_DIR)
    from v2_field import Fq, Curve
    import v2_arms as A
    cmod = next(c for c in range(2, p) if pow(c, (p - 1) // 3, p) != 1)
    F = Fq.binomial(p, 3, cmod)
    for c in range(1, p):
        E = Curve(F, 2, c * F.z, 0, "fixture_n3")
        if not F.is_square(E.a4) and not F.is_square(E.a2 * E.a2 - 4 * E.a4):
            break
    rng = random.Random("r1-dv7:toy-fixture-n3:%d:regression" % p)
    tg = []
    while len(tg) < 2:
        P = E.random_point(rng)
        if P is None or P[0] == 0:
            continue
        cs = F.coeffs(P[0])
        tg.append({"target": len(tg), "x_R": "%d*z^2 + %d*z + %d" % (cs[2], cs[1], cs[0])})
    return {"p": p, "field": "F_%d[z]/(z^3 - %d)" % (p, cmod), "curve": "y^2 = x(x^2 + 2x + %d*z)" % c, "b_is_square": False,
            "a2^2-4b_is_square": False, "beta": A.smallest_nonsquare(p), "targets": tg, "toy_note": "DV-7 toy fixture data (stage R1 construction)"}


def toy_fixture_n4(p):
    import flint
    for a in range(1, p):
        for b in range(1, 20):
            for c in range(1, 20):
                f = flint.nmod_poly([c, b, a, 0, 1], p)
                fac = f.factor()[1]
                if len(fac) == 1 and fac[0][1] == 1 and fac[0][0].degree() == 4:
                    return {"result": {"p": p, "field": "GF(%d^4) modulus x^4 + %d*x^2 + %d*x + %d" % (p, a, b, c),
                                       "curve": "y^2 = x(x^2 + 2x + (z+0)^2)", "b_is_square": True, "beta": 1,
                                       "S4": {"D_msolve": None}, "product": {"D_msolve": None}, "D4type": {"D_msolve": None},
                                       "toy_note": "DV-7 toy n = 4 fixture data; no red-team values exist at a toy prime"}}
    raise RuntimeError("no irreducible quartic found")


def toy_ladder(tdir):
    """The frozen a1_toy.toy_ladder (read-only import; gp in capped children via a1_pari) at 1021 for the addendum role,
    and at the first prime of TOY_V2_CANDIDATES whose three toy curves are all found, for the v2 role. Every attempt is
    recorded."""
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import r5_devchecks as DC
    DC.recorder_in_this_process(os.path.join(tdir, "ladder_recorder_rundir"))   # the RL-1 installation (r5_recorder.install)
    import a1_toy
    trail = []
    a1_toy.TOY_P = TOY_A1_P
    rungs = [a1_toy.toy_ladder(os.path.join(tdir, "ladder_%d" % TOY_A1_P))]
    trail.append({"p": TOY_A1_P, "role": "a1", "complete": rungs[0]["complete"], "curves_found": sorted(rungs[0]["curves"])})
    v2p = None
    for p in TOY_V2_CANDIDATES:
        a1_toy.TOY_P = p
        rec = a1_toy.toy_ladder(os.path.join(tdir, "ladder_%d" % p))
        trail.append({"p": p, "role": "v2", "complete": rec["complete"], "curves_found": sorted(rec["curves"])})
        if rec["complete"]:
            v2p = p
            rungs.append(rec)
            break
    return rungs, trail, v2p


def toy_watchdogs(v2):
    wd = copy.deepcopy(v2["watchdogs"])
    for arm in ("raw", "S2", "S2_rescaled", "torsion_S2_rq", "torsion_S2_norm"):
        wd["per_arm_m"]["%s|m2" % arm] = {"per_target_timeout_s": 1800, "per_cell_no_measurement_watchdog_s": None, "note": "TOY-ONLY key (DV-7)"}
    wd["per_arm_m"]["raw|m3"] = {"per_target_timeout_s": None, "per_cell_no_measurement_watchdog_s": None, "note": "TOY-ONLY key: raw at the m = 5 role is not_attempted"}
    wd["builder_timeout_s"]["m2"] = 1800
    return wd


def toy_builds():
    import a1_common as AC
    return [{"shape": s, "arm": a % m, "m": m} for m in (3, 2) for s in AC.SHAPES for a in ("S%d", "S%d_rescaled", "torsion_S%d_rq", "torsion_S%d_norm")]


def toy_plans(ladder_path, v2p):
    import a1_toy
    import a1_common as AC
    v2r4, a1r4, v2f = R.load_json(R.PLAN_V2_R5), R.load_json(R.PLAN_A1_R5), R.load_json(R.PLAN_V2)
    wd = toy_watchdogs(v2f)
    for pl in (v2r4, a1r4, v2f):
        pl["watchdogs"] = wd
        pl["toy_note"] = "TOY copy (DV-7): toy primes, m = 3 / 2 roles, toy-only m = 2 watchdog keys"
    by = {pk["order"]: pk for pk in v2r4["packages"]}
    by[1].update(driver_args=["fixture", "--p", str(TOY_FX3[0])], p=TOY_FX3[0])
    by[2].update(driver_args=["fixture", "--p", str(TOY_FX3[1])], p=TOY_FX3[1])
    by[6].update(driver_args=["build", "--p", str(v2p)], p=v2p, builds=toy_builds())
    m5 = {}
    for o, s in zip((7, 8, 9), AC.SHAPES):
        by[o].update(driver_args=["cells", "--p", str(v2p), "--shape", s, "--m", "3"], p=v2p, m=3, shape=s, cells=a1_toy.toy_cells(s, 5, v2p))
        m5[s] = by[o]["run_id"]
    for o, s in zip((10, 11, 12), AC.SHAPES):
        by[o].update(driver_args=["cells", "--p", str(v2p), "--shape", s, "--m", "2", "--prior-run", m5[s]], p=v2p, m=2, shape=s,
                     cells=a1_toy.toy_cells(s, 4, v2p))
    v2r4["cells_enumeration"], v2r4["n_cells_enumerated"] = [], 0
    ba = {pk["order"]: pk for pk in a1r4["packages"]}
    ba[1].update(driver_args=["controls-a1", "--p", str(TOY_A1_P)], p=TOY_A1_P)
    ba[2].update(driver_args=["build", "--p", str(TOY_A1_P)], p=TOY_A1_P, builds=toy_builds())
    m5 = {}
    for o, s in zip((3, 4, 5), AC.SHAPES):
        ba[o].update(driver_args=["cells", "--p", str(TOY_A1_P), "--shape", s, "--m", "3"], p=TOY_A1_P, m=3, shape=s,
                     cells=a1_toy.toy_cells(s, 5, TOY_A1_P))
        m5[s] = ba[o]["run_id"]
    for o, s in zip((6, 7, 8), AC.SHAPES):
        ba[o].update(driver_args=["cells", "--p", str(TOY_A1_P), "--shape", s, "--m", "2", "--prior-run", m5[s]], p=TOY_A1_P, m=2, shape=s,
                     cells=a1_toy.toy_cells(s, 4, TOY_A1_P))
    a1r4["cells_enumeration"], a1r4["n_cells_enumerated"] = [], 0
    import v2_common as C
    import v2_arms as A
    old = C.LADDER_PATH
    C.LADDER_PATH = ladder_path
    try:
        rung = C.ladder_entry(TOY_A1_P)
        F = C.ladder_field(rung)
        resc = {s: A.public_rescaling(A.rescaling(C.ladder_curve(F, rung, s)[0])) for s in AC.SHAPES}
    finally:
        C.LADDER_PATH = old
    a1r4["rescaling_parameters"] = dict(a1r4["rescaling_parameters"], p=TOY_A1_P, per_shape=resc)
    return v2r4, a1r4, v2f


def synthetic_pkg(runs, rid, raw, manifest_extra=None):
    import yaml
    d = os.path.join(runs, rid)
    os.makedirs(d, exist_ok=True)
    dump(os.path.join(d, "raw-result.json"), raw)
    with open(os.path.join(d, "manifest.yaml"), "w") as fh:
        yaml.safe_dump({"run": dict({"id": rid, "status": raw.get("run_status"), "failure_class": None, "synthetic": SYN}, **(manifest_extra or {}))}, fh)


def synthetic_v2_cells(runs, plan, skip_ids):
    import a1_toy
    import v2_arms as A
    for pk in plan["packages"]:
        if pk["kind"] != "cells" or pk["run_id"] in skip_ids:
            continue
        cells = []
        for c in pk["cells"]:
            kind = A.parse_arm(c["arm"])[0]
            cell = {"arm": c["arm"], "kind": kind, "curve_shape": pk["shape"], "p": pk["p"], "p_bits": pk["p"].bit_length(), "m": pk["m"], "n": 5,
                    "target_kind": "random", "group": A.group_label(kind, pk["m"]), "group_order": A.group_order(kind, pk["m"]), "planned_as": c,
                    "targets": [], "synthetic": SYN}
            D = a1_toy.synthetic_D(pk["p"], pk["shape"], c["arm"]) if (pk["m"] == 5 and c["disposition"] == "run") else None
            if c["disposition"] != "run":
                cell["terminal"] = {"status": "not_attempted", "reason": c.get("reason")}
            elif c.get("expected_refusal"):
                cell["terminal"] = {"status": "refused", "reason": c["expected_refusal"], "synthetic": SYN}
            elif pk["m"] == 5 and D:
                cell["metrics"] = {"targets_planned": 20, "targets_attempted": 3, "targets_measured": 3, "outcome_counts": {"ok": 3}, "ideal_degree_D": D,
                                   "D_reason": None, "D_per_target": {"0": D, "1": D, "2": D}, "decomposition_success_rate": 0.0,
                                   "targets_with_verified_relation": 0}
                cell["terminal"] = {"status": "measured", "reason": None}
            else:
                cell["terminal"] = {"status": "not_attempted", "reason": "SYNTHETIC toy row"}
            cells.append(cell)
        synthetic_pkg(runs, pk["run_id"], {"kind": "cells", "p": pk["p"], "curve_shape": pk["shape"], "m": pk["m"], "n": 5, "cells": cells,
                                           "run_status": "completed_valid", "synthetic": SYN})


# ============================================================================ the shim (development only; never delivered)
HOOKS = r'''
import os, sys, json, re, time, traceback, datetime, importlib.abc, importlib.util, runpy
sys.dont_write_bytecode = True
CFG = json.load(open(os.environ["R4_TOY_CFG"]))
sys.path.insert(0, CFG["layer_dir"])
import r5_common as R
for k, v in CFG["R"].items():
    setattr(R, k, v)
import r5_resolve as RS
TRACE = CFG.get("trace")
PKG = os.environ.get("R4_TOY_PACKAGE")
DEPTH = [0]

def _stack():
    return traceback.extract_stack()[:-2]

def _launcher(st):
    names = [(os.path.basename(f.filename), f.name) for f in st]
    if ("a1_health.py", "run_system") in names:
        return "a1_health.run_system"
    if ("v2_solver.py", "callgrind_instructions") in names:
        return "v2_solver.callgrind_instructions"
    if ("v2_driver.py", "solve") in names:
        return "v2_driver.solve"
    if ("a1_pari.py", "curve_facts") in names:
        return "a1_pari.curve_facts"
    if ("v2_driver.py", "child_job") in names:
        return "v2_driver.child_job"
    return "other:" + ",".join("%s:%s" % n for n in names if n[0].startswith(("v2_", "a1_", "r5_")))[-160:]

def _log(ev, extra=None):
    if not TRACE:
        return
    st = _stack()
    rec = {"event": ev, "pid": os.getpid(), "package": PKG, "argv": sys.argv[1:4],
           "stack": ["%s:%d:%s" % (os.path.basename(f.filename), f.lineno, f.name) for f in st if "implementation-v2" in f.filename][-10:]}
    if extra:
        rec.update(extra)
    with open(TRACE, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")

sys.addaudithook(lambda ev, args: _log("import:" + args[0]) if ev == "import" and args and args[0] in ("cypari2", "sage.all", "sage") else None)
import cypari2
_Base = cypari2.Pari
class TracingPari(_Base):
    def __init__(self, *a, **k):
        _log("cypari2.Pari()")
        super().__init__(*a, **k)
    def __call__(self, s, *a, **k):
        m = re.search(r"ffgen\(Mod\(1, (\d+)\)\*\((.*?)\), 'w\)", str(s))
        ex = {"expr_head": str(s)[:160]}
        if m:
            ex["p"] = int(m.group(1))
            ex["field_degree"] = max(int(x) for x in re.findall(r"w\^(\d+)", m.group(2)))
        _log("cypari2.Pari.__call__", ex)
        return super().__call__(s, *a, **k)
cypari2.Pari = TracingPari

def _tag_of(argv):
    for i, x in enumerate(argv):
        if x == "-f" and i + 1 < len(argv):
            b = os.path.basename(argv[i + 1])
            return b[:-3] if b.endswith(".ms") else b
    return None

class Hook(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name not in CFG["mods"] and name != "v2_solver":
            return None
        sys.meta_path.remove(self)
        spec = importlib.util.find_spec(name)
        sys.meta_path.insert(0, self)
        orig = spec.loader.exec_module
        def exec_module(module, _o=orig, _n=name):
            _o(module)
            for k, v in CFG["mods"].get(_n, {}).items():
                setattr(module, k, v)
            if _n == "v2_solver" and TRACE:
                module.os = _OsProxy()
        spec.loader.exec_module = exec_module
        return spec
sys.meta_path.insert(0, Hook())

class _OsProxy(object):
    """Development fork tracer (DV-7 / DV-11 only): delegates every attribute to the real os module; fork() calls the
    real os.fork (so every os.register_at_fork callback, the RG-1 observer included, runs as without the proxy) and, in
    the PARENT only, appends one trace line. It sits beneath the RL-1 recorder and replaces no function the RL-5
    read-back names."""
    def __getattr__(self, name):
        return getattr(os, name)
    def fork(self):
        pid = os.fork()
        if pid > 0:
            argv = None
            f = sys._getframe(1)
            while f is not None:
                if f.f_code.co_name == "_run_child_locked":
                    argv = f.f_locals.get("argv")
                    break
                f = f.f_back
            st = _stack()
            _log("fork", {"child_pid": pid, "t": time.time(), "child_argv0": os.path.basename(argv[0]) if argv else None,
                          "tag": _tag_of(argv) if argv else None, "launcher": _launcher(st),
                          "inside_wrapper_original_call": DEPTH[0] > 0,
                          "msolve_in_argv": bool(argv) and any(os.path.basename(x) == "msolve" for x in argv)})
        return pid

_orig_call_original = RS._call_original
def _traced_call_original(original, args, kwargs):
    site = R.SITE_S2 if getattr(original, "__name__", "") == "run_system" else R.SITE_S1
    tag = args[3] if len(args) > 3 else None
    t0 = time.time()
    DEPTH[0] += 1
    try:
        res = _orig_call_original(original, args, kwargs)
    finally:
        DEPTH[0] -= 1
    t1 = time.time()
    out = res.get("outcome") if site == R.SITE_S1 else res.get("v2_outcome_class")
    _log("original_call_end", {"site": site, "tag": tag, "t_start": t0, "t_end": t1, "gb_only": kwargs.get("gb_only"),
                                "callgrind_timeout": kwargs.get("callgrind_timeout"), "outcome": out,
                                "recorded_attempt_ok_with_callgrind_timeout": bool(site == R.SITE_S1 and kwargs.get("callgrind_timeout") and out == "ok"),
                                "has_instructions_callgrind": "instructions_callgrind" in res})
    return res
RS._call_original = _traced_call_original
'''

ENTRY_TAIL = r'''
entry = CFG["entry"][os.environ["R4_TOY_ENTRY"]]
sys.argv = [entry] + sys.argv[1:]
runpy.run_path(entry, run_name="__main__")
'''

CHECK_SHIM = HOOKS + r'''
import r5_check_run as K
mode, rd = sys.argv[1], sys.argv[2]
sys.exit(K.frozen_v2(rd) if mode == "frozen-v2" else K.frozen_a1(rd))
'''


class Toy:
    """The scratch toy environment shared by DV-7, DV-12 and DV-16 (built once by DV-7; the others reuse it)."""

    def __init__(self, tdir):
        self.tdir = tdir
        self.state = os.path.join(tdir, "toy-env.json")

    def build(self):
        report = {}
        sys.path.insert(0, R.V2_DIR)
        sys.path.insert(0, R.A1_DIR)
        import a1_common as AC                                                   # noqa: F401
        fx3 = {"task": "DV-7 toy", "n": 3, "m": 3, "primes": [toy_fixture_n3(p) for p in TOY_FX3]}
        fx3_path = os.path.join(self.tdir, "toy_fixture_n3.json")
        dump(fx3_path, fx3)
        fx4_path = os.path.join(self.tdir, "toy_fixture_n4.json")
        dump(fx4_path, toy_fixture_n4(TOY_FX4_P))
        rungs, trail, v2p = toy_ladder(self.tdir)
        report["toy_ladder_selection_trail"] = trail
        report["toy_ladder"] = [{k: r.get(k) for k in ("p", "cmod", "field", "complete", "curves")} for r in rungs]
        if v2p is None or not all(r["complete"] for r in rungs):
            return None, report
        ladder_path = os.path.join(self.tdir, "toy-ladder.json")
        dump(ladder_path, R.load_json(R.LADDER_PATH) + rungs)
        v2r4, a1r4, v2f = toy_plans(ladder_path, v2p)
        pv2, pa1, pv2f = (os.path.join(self.tdir, n) for n in ("toy-trial-plan-v2-r5.json", "toy-trial-plan-v2-a1-r5.json", "toy-trial-plan-v2.json"))
        dump(pv2, v2r4)
        dump(pa1, a1r4)
        dump(pv2f, v2f)
        r4files = sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _d, fn in os.walk(os.path.join(R.REPO, R.R5_PATHS_REL[0])) for f in fn) + R.R5_PATHS_REL[1:]
        rec_a = os.path.join(self.tdir, "toy-4a47e5-phase-a-receipt.json")
        head = subprocess.run(["git", "-C", R.REPO, "rev-parse", "HEAD"], capture_output=True, text=True,
                              env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).stdout.strip()
        dump(rec_a, {"synthetic": SYN, "commit_sha": head, "path_sha256": {p: sha(os.path.join(R.REPO, p)) for p in r4files}})
        env = {"fx3": fx3_path, "fx4": fx4_path, "ladder": ladder_path, "v2_role_prime": v2p, "a1_role_prime": TOY_A1_P,
               "plan_v2r4": pv2, "plan_a1r4": pa1, "plan_v2": pv2f, "receipt_a": rec_a, "r4files": r4files, "report": report}
        dump(self.state, env)
        return env, report

    def load(self):
        return R.load_json(self.state)


def cfg_for(tdir, env, world_exp, runs_for_reg1, ref_receipt, receipt_b, trace):
    """The shim configuration of one world (entry and checker processes)."""
    p = os.path.join(tdir, "cfg-%s.json" % os.path.basename(os.path.dirname(world_exp)))
    dump(p, {"layer_dir": HERE, "exp_real": R.EXP_DIR, "trace": trace,
             "R": {"PLAN_V2_R5": env["plan_v2r4"], "PLAN_A1_R5": env["plan_a1r4"], "PLAN_V2": env["plan_v2"],
                   "RECEIPT_R5_PHASE_A": env["receipt_a"], "RECEIPT_R5_PHASE_B": receipt_b,
                   "RUNS_DIR": runs_for_reg1, "REG1_REFERENCE_RUN": R.load_json(env["plan_v2r4"])["gate"]["blocking_packages"][0],
                   "RECEIPT_V2_PHASE_B": ref_receipt},
             "mods": {"v2_common": {"EXP_DIR": world_exp, "LADDER_PATH": env["ladder"], "FIXTURE_N3_JSON": env["fx3"], "FIXTURE_N4_JSON": env["fx4"]},
                      "a1_common": {"EXP_DIR": world_exp, "RUNS_DIR": os.path.join(world_exp, "runs"), "LADDER_PATH": env["ladder"]}},
             "entry": {"v2": os.path.join(HERE, "r5_entry_v2.py"), "a1": os.path.join(HERE, "r5_entry_a1.py")}})
    return p


def write_shims(sdir, extra=""):
    os.makedirs(sdir, exist_ok=True)
    paths = {}
    for name, body in (("entry_toy.py", HOOKS + extra + ENTRY_TAIL), ("check_toy.py", CHECK_SHIM)):
        paths[name] = os.path.join(sdir, name)
        with open(paths[name], "w") as fh:
            fh.write(body)
    return paths


def tree_receipt(path, run_dir):
    dump(path, {"synthetic": SYN, "path_sha256": {os.path.relpath(os.path.join(dp, f), R.REPO): sha(os.path.join(dp, f))
                                                  for dp, _d, fn in os.walk(run_dir) for f in fn}})


def manifest_row(runs, rid):
    import yaml
    mp = os.path.join(runs, rid, "manifest.yaml")
    if not os.path.exists(mp):
        return None
    return yaml.safe_load(open(mp))["run"]


# ============================================================================ DV-7
def dv7(out, rest):
    tdir = os.path.join(out, "toy")
    if os.path.exists(tdir):
        raise SystemExit("REFUSING: %s exists (DV-7 runs once; a re-run needs a recorded harness reason)" % tdir)
    os.makedirs(tdir)
    report = {"no_ladder_or_fixture_prime_solved": True, "started": R.now()}
    print("(1) toy data, toy ladder (gp children through the frozen a1_toy / a1_pari), toy plans")
    toy = Toy(tdir)
    env, rep0 = toy.build()
    report.update(rep0)
    if env is None:
        report["pass"] = False
        report["harness_failure"] = "toy ladder incomplete"
        dump(os.path.join(out, "dv7.json"), report)
        print("DV-7: harness FAIL (toy ladder incomplete)")
        return 1
    report["toy_primes"] = {"a1_role": TOY_A1_P, "v2_role": env["v2_role_prime"], "fixture_n3": TOY_FX3, "fixture_n4": TOY_FX4_P}
    v2r4, a1r4 = R.load_json(env["plan_v2r4"]), R.load_json(env["plan_a1r4"])
    G = v2r4["gate"]["blocking_packages"]
    cache = os.path.join(tdir, "cache")
    os.makedirs(cache)
    os.environ["GFPN_V2_CACHE_DIR"] = cache
    worlds = {}
    for w in ("A", "B"):
        exp = os.path.join(tdir, "world_%s" % w, "exp")
        os.makedirs(os.path.join(exp, "runs"))
        worlds[w] = exp
    runsA, runsB = os.path.join(worlds["A"], "runs"), os.path.join(worlds["B"], "runs")
    rec_ref_A = os.path.join(tdir, "toy-reference-receipt-worldA-G1.json")      # SE-5: world A's G1 is the reference
    rec_ref_B = os.path.join(tdir, "toy-reference-receipt-worldB-G1.json")      # lineage R-7: world B's G1 is the reference
    rec_b = os.path.join(tdir, "toy-4a47e5-post-run-receipt.json")               # RC-8 form, written after the v2 packages
    trace = os.path.join(tdir, "trace.jsonl")
    shims = write_shims(os.path.join(tdir, "shims"))
    import r5_run_wrapper as W
    import r5_check_run as K
    import r5_reg1 as REG
    K.FROZEN_LAUNCHER = [sys.executable, "-B", shims["check_toy.py"]]        # the wrapper's admission checks use it too
    real_git = W.git_tree_state
    W.git_tree_state = lambda paths: (env["r4files"], []) if paths == R.R5_PATHS_REL else real_git(paths)
    W.ENTRY_V2 = W.ENTRY_A1 = shims["entry_toy.py"]
    base_R = {"PLAN_V2_R5": env["plan_v2r4"], "PLAN_A1_R5": env["plan_a1r4"], "PLAN_V2": env["plan_v2"], "RECEIPT_R5_PHASE_A": env["receipt_a"],
              "RECEIPT_R5_PHASE_B": rec_b, "REG1_REFERENCE_RUN": G[0]}
    for k, v in base_R.items():
        setattr(R, k, v)
    pkgs = []
    by0 = {pk["order"]: pk for pk in v2r4["packages"]}
    SYNTH = {G[2], G[3]} | {by0[o]["run_id"] for o in range(13, 27)}      # declared synthetic (DV-7 docstring), before any launch
    report["declared_synthetic_packages"] = sorted(SYNTH)
    # DECLARED BEFORE ANY LAUNCH (r4 DV-7 attempts 1-2; the r3 stage's attempt 2): the toy G2 (fixture --p 1039) is known
    # to keep the SSF signature on all six attempts of two toy systems and to end failed; if it does not pass, it STAYS
    # the toy lineage's G2 (it is not replaced) and the refusal "R-7 repaired gate package <toy G2> did not pass" is
    # EXPECTED for every later package. R-7's admission of a PASSING toy G2 is then not exercised (stated in the report).
    FAILED_G2 = []
    report["declared_failed_toy_G2_rule"] = "if the toy G2 does not pass, its R-7 'did not pass' refusal is expected for every later package"
    pat = re.compile(r"(?:gate package|read package) (RUN-GFPN-[0-9a-f]{6})")

    def classify(refusals):
        exp, unexp = [], []
        for r in refusals:
            m = pat.search(r)
            if FAILED_G2 and r.startswith("R-7 repaired gate package %s did not pass" % FAILED_G2[0]):
                exp.append(r)
            elif (r.startswith("R-7 (RB-4 (b)) the r5 checker on gate package ") or r.startswith("R-8 (RL-4; RF-3 (b) designed stop) read package ")) \
                    and m and m.group(1) in SYNTH:
                exp.append(r)
            else:
                unexp.append(r)
        return exp, unexp

    def run(w, rid, entry_kind, seed, reg_runs, reg_receipt):
        os.environ["R4_TOY_CFG"] = cfg_for(tdir, env, worlds[w], reg_runs, reg_receipt, rec_b, trace)
        os.environ["R4_TOY_ENTRY"] = entry_kind
        os.environ["R4_TOY_PACKAGE"] = "%s/%s" % (w, rid)
        R.RUNS_DIR, R.RECEIPT_V2_PHASE_B = reg_runs, reg_receipt
        W.RUNS = os.path.join(worlds[w], "runs")
        W.DRIVER_PYTHONHASHSEED = seed                   # the delivered "0"; "12345" only for the SE-5 world B (SC-11 (f))
        t0 = datetime.datetime.now(datetime.timezone.utc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            refusals, info = W.preflight(rid)
        exp_ref, unexp_ref = classify(refusals)
        rc = None
        if not unexp_ref:
            with contextlib.redirect_stdout(buf):
                rc = W.launch(rid, None, info)
        t1 = datetime.datetime.now(datetime.timezone.utc)
        man = manifest_row(W.RUNS, rid)
        row = {"world": w, "run_id": rid, "entry": entry_kind, "PYTHONHASHSEED_set": seed, "wrapper_launch_rc": rc,
               "preflight_refusals_expected": exp_ref, "preflight_refusals_unexpected": unexp_ref, "launched": rc is not None,
               "wrapper_output": buf.getvalue().splitlines(),
               "r4_verdict": man and (man.get("verdict") or {}).get("r4_verdict"),
               "r4_stop_classes": man and (man.get("verdict") or {}).get("stop_classes"),
               "raw_result_writer": man and man.get("raw_result_writer"),
               "gate_package_checker": man and {k: (v.get("exit_status"), v.get("verdict")) for k, v in ((man.get("gate") or {}).get("gate_package_checker") or {}).items()},
               "required_package_checker": man and {k: (v.get("exit_status"), v.get("verdict")) for k, v in ((man.get("gate") or {}).get("required_package_checker") or {}).items()},
               "run_dir": os.path.join(W.RUNS, rid), "started": t0.isoformat(), "finished": t1.isoformat(),
               "status": man and man["status"], "failure_class": man and man["failure_class"], "gate_pass": man and man["result"]["gate_pass"],
               "getrlimit": man and man["resources"]["child_rlimit_as_read_back_by_getrlimit"],
               "threads": man and man["resources"]["msolve_threads_executed"],
               "pari_stack_status": man and (man["resources"]["pari_stack"] or {}).get("status"),
               "hashseed_readback": man and ((man.get("environment") or {}).get("PYTHONHASHSEED_driver_readback") or {}).get("PYTHONHASHSEED_env"),
               "reg1_in_manifest": man and ((man.get("gate") or {}).get("regression_REG-1") or {}).get("verdict"),
               "solver_events_block": man and man.get("solver_events")}
        pkgs.append(row)
        dump(os.path.join(out, "dv7-progress.json"), dict(report, packages=pkgs))
        print("   world %s %s %-4s launched=%s status=%s gate_pass=%s REG-1=%s verdict=%s hashseed=%s expected-refusals=%d unexpected=%s (%.0fs)" % (
            w, rid, entry_kind, rc is not None, row["status"], row["gate_pass"], row["reg1_in_manifest"], row["r4_verdict"], row["hashseed_readback"],
            len(exp_ref), unexp_ref, (t1 - t0).total_seconds()))
        return row
    # ---- (2) the SE-5 probe, run ONCE
    print("(2) SE-5 probe: toy G1 (fixture --p %d) in world A (PYTHONHASHSEED %s) and world B (%s)" % (TOY_FX3[0], SEED_A, SEED_B))
    rA = run("A", G[0], "v2", SEED_A, runsB, rec_ref_B)
    ga = os.path.join(runsA, G[0])
    tree_receipt(rec_ref_A, ga)
    rB = run("B", G[0], "v2", SEED_B, runsA, rec_ref_A)
    gb = os.path.join(runsB, G[0])
    if rA["status"] is None or rB["status"] is None:
        report["harness_failure"] = ("a toy G1 package was refused before launch or wrote no manifest; no SE-5 comparison is made: %s"
                                     % [x["wrapper_output"] for x in (rA, rB)])
        report["packages"] = pkgs
        report["pass"] = False
        dump(os.path.join(out, "dv7.json"), report)
        print("DV-7: harness FAIL (no SE-5 verdict)")
        return 1
    tree_receipt(rec_ref_B, gb)
    probe = REG.compare(ga, gb, receipt=rec_ref_A)
    report["se5_probe"] = {"PYTHONHASHSEED": {"world_A": SEED_A, "world_B": SEED_B}, "reference": "world A G1", "candidate": "world B G1",
                           "verdict": probe["verdict"], "failures": probe["failures"], "output": REG.render(probe),
                           "ssf_per_world": {w: (r["solver_events_block"] or {}).get("sites") for w, r in (("A", rA), ("B", rB))}}
    with open(os.path.join(out, "se5_probe_reg1_output.txt"), "w") as fh:
        fh.write(REG.render(probe) + "\n")
    print("   SE-5 probe:", probe["verdict"], probe["failures"][:5])
    if probe["verdict"] != "PASS":
        report["STOP"] = ("SE-5: a field REG-1 compares differs between the RECORDED results of world A (PYTHONHASHSEED 0) and world B "
                          "(12345) -- the stage STOPS for a new Coordinator decision")
        report["packages"] = pkgs
        report["pass"] = False
        dump(os.path.join(out, "dv7.json"), report)
        print("DV-7: STOP (SE-5)")
        return 3
    pert = os.path.join(tdir, "perturbed", G[0])
    shutil.copytree(gb, pert)
    rp = os.path.join(pert, "raw-result.json")
    r = json.load(open(rp))
    r["planted_targets"][0]["arms"][list(r["planted_targets"][0]["arms"])[0]]["D"] = (r["planted_targets"][0]["arms"][list(r["planted_targets"][0]["arms"])[0]].get("D") or 0) + 1
    json.dump(r, open(rp, "w"), indent=1)
    pr = REG.compare(ga, pert, receipt=rec_ref_A)
    report["reg1_perturbed_copy"] = {"perturbation": "world B G1 copy: planted_targets[0] first arm D + 1", "verdict": pr["verdict"], "failures": pr["failures"]}
    print("   REG-1 on a perturbed copy:", pr["verdict"])
    # ---- (3) the rest of the lineage in world A (delivered PYTHONHASHSEED "0"); R-7's REG-1 against world B's G1
    print("(3) world A: G2; G3, G4 SYNTHETIC; F-4; v2 build, cells, aggregate; the addendum packages")
    g2 = run("A", G[1], "v2", SEED_A, runsB, rec_ref_B)
    if g2["status"] != "completed_valid" or g2["gate_pass"] is not True:
        FAILED_G2.append(G[1])
        report["toy_G2_did_not_pass"] = {"run_id": G[1], "status": g2["status"], "failure_class": g2["failure_class"], "gate_pass": g2["gate_pass"]}
    for g, why in ((G[2], "anchor-identity is not run at toy scale (hard-coded p' = 16777291 and the Sage anchor system; DV-18 (b) runs it)"),
                   (G[3], "controls is not run at toy scale (hard-coded fixture field at 4111 and ladder primes 4111, 262151, 16777291; DV-18 (a) runs it)")):
        synthetic_pkg(runsA, g, {"kind": "synthetic_gate", "run_status": "completed_valid", "gate_pass": True, "synthetic": SYN, "reason": why})
    by = {pk["order"]: pk for pk in v2r4["packages"]}
    for o in [5, 6, 7, 8, 9, 10, 11, 12]:
        run("A", by[o]["run_id"], "v2", SEED_A, runsB, rec_ref_B)
    synthetic_v2_cells(runsA, v2r4, skip_ids={by[o]["run_id"] for o in range(7, 13)})
    for o in (13, 20):
        synthetic_pkg(runsA, by[o]["run_id"], {"kind": "build", "run_status": "completed_valid", "synthetic": SYN,
                                               "reason": "SYNTHETIC toy row: builds at 262151 / 16777291 are not run at toy scale"})
    run("A", by[27]["run_id"], "v2", SEED_A, runsB, rec_ref_B)
    v2_read = [by[o]["run_id"] for o in range(1, 28) if by[o]["kind"] in ("cells", "aggregate")]
    dump(rec_b, {"synthetic": SYN, "commit_sha": "dv7-synthetic-not-a-commit",
                 "path_sha256": {os.path.relpath(os.path.join(runsA, i, "raw-result.json"), R.REPO): sha(os.path.join(runsA, i, "raw-result.json"))
                                 for i in v2_read if os.path.exists(os.path.join(runsA, i, "raw-result.json"))}})
    ba = {pk["order"]: pk for pk in a1r4["packages"]}
    for o in range(1, 10):
        run("A", ba[o]["run_id"], "a1", SEED_A, runsB, rec_ref_B)
    agg_path = os.path.join(runsA, ba[9]["run_id"], "raw-result.json")
    agg = R.load_json(agg_path) if os.path.exists(agg_path) else {}
    report["rc8_aggregate_a1_phase_b_check"] = (agg.get("v2_bytes_phase_B_check") or {}).get("status")
    report["packages"] = pkgs
    # ---- (4) the r4 checker on every toy package that ran through the wrapper (again, standalone; the wrapper already
    #          recorded each package's own verdict in its manifest)
    print("(4) the r4 checker on every toy package that ran through the wrapper")
    os.makedirs(os.path.join(tdir, "accounting"), exist_ok=True)
    checks = []
    for x in pkgs:
        if not x["launched"]:
            continue
        os.environ["R4_TOY_CFG"] = cfg_for(tdir, env, worlds[x["world"]], runsB if x["world"] == "A" else runsA,
                                           rec_ref_B if x["world"] == "A" else rec_ref_A, rec_b, None)
        os.environ.pop("R4_TOY_PACKAGE", None)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = K.main(x["run_dir"], os.path.join(tdir, "accounting", "%s_%s.json" % (x["world"], x["run_id"])))
        lines = buf.getvalue().splitlines()
        checks.append({"world": x["world"], "run_id": x["run_id"], "rc": rc, "output": lines,
                       "failing_items": [l.strip()[2:] for l in lines if l.startswith("  - ")],
                       "r4_verdict": next((l.split(": ", 1)[1] for l in lines if l.startswith("R5 VERDICT: ")), None)})
        print("   check world %s %s rc=%s %s" % (x["world"], x["run_id"], rc, [l.strip()[2:] for l in lines if l.startswith("  - ")][:3]))
    report["checker"] = checks
    # ---- (5) DV-13, DV-14, forbidden ids, DV-1 dynamic
    report["dv13"] = {"per_package": [{"world": x["world"], "run_id": x["run_id"], "set": x["PYTHONHASHSEED_set"], "driver_readback": x["hashseed_readback"]} for x in pkgs]}
    report["dv13"]["pass"] = all((x["hashseed_readback"] == SEED_A) if x["world"] == "A" else (x["hashseed_readback"] == SEED_B) for x in pkgs)
    gaps = []
    for x in pkgs:
        sp = os.path.join(x["run_dir"], "solver-events.json")
        if not os.path.exists(sp):
            continue
        doc = R.load_json(sp)
        for site in (R.SITE_S1, R.SITE_S2):
            for e in ((doc.get("sites") or {}).get(site) or {}).get("events") or []:
                a = e.get("attempts") or []
                for i in range(1, len(a)):
                    s = datetime.datetime.strptime(a[i]["start_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    en = datetime.datetime.strptime(a[i - 1]["end_utc"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    gaps.append({"package": "%s/%s" % (x["world"], x["run_id"]), "site": site, "tag": e.get("tag"), "attempt": a[i]["attempt"],
                                 "gap_s": (s - en).total_seconds()})
    report["dv14"] = {"re_solve_gaps": gaps, "n_re_solves": len(gaps), "pass": all(g["gap_s"] >= R.SPACING_S for g in gaps)}
    bad = []
    for dp, _d, fn in os.walk(tdir):
        for f in fn:
            b = open(os.path.join(dp, f), "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    bad.append({"file": os.path.relpath(os.path.join(dp, f), tdir), "id": t})
    report["forbidden_task_ids_in_toy_artifacts_report_only"] = bad
    tr = [json.loads(l) for l in open(trace)] if os.path.exists(trace) else []
    calls = [t for t in tr if t["event"] == "cypari2.Pari.__call__"]
    report["dv1_dynamic"] = {
        "trace_file": "dv7/toy/trace.jsonl", "n_events": len(tr),
        "in_process_pari_calls": sorted({json.dumps([t.get("package"), t.get("p"), t.get("field_degree"), " <- ".join(reversed(t["stack"][-3:]))]) for t in calls}),
        "cypari2_constructions_by_caller": sorted({json.dumps([t.get("package", "").split("/")[0], t["stack"][-1] if t["stack"] else None]) for t in tr if t["event"] == "cypari2.Pari()"}),
        "children_by_launcher": sorted({json.dumps([t.get("launcher"), t.get("child_argv0")]) for t in tr if t["event"] == "fork"}),
        "gp_children": [{"package": t.get("package"), "launcher": t.get("launcher"), "pid": t.get("child_pid")} for t in tr
                        if t["event"] == "fork" and t.get("child_argv0") == "gp"],
        "imports": sorted({json.dumps([t.get("package", "").split("/")[0], t["event"]]) for t in tr if t["event"].startswith("import:")})}
    # ---- (6) evaluation
    def check_ok(c):
        if c["world"] == "B":
            return c["failing_items"] == ["SE-6: the driver process read back PYTHONHASHSEED '12345', not '0'"]
        return c["rc"] == 0 and c["r4_verdict"] in ("PASS", "PASS_ZL")
    exp_ok = {"no_unexpected_preflight_refusal": all(not x["preflight_refusals_unexpected"] for x in pkgs),
              "every_package_launched": all(x["launched"] for x in pkgs),
              "every_world_A_manifest_verdict_PASS_or_PASS_ZL": all(x["r4_verdict"] in ("PASS", "PASS_ZL") for x in pkgs if x["world"] == "A"),
              "all_run_packages_completed_valid_except_a_declared_failed_toy_G2": all(x["status"] == "completed_valid" for x in pkgs
                                                                                      if not (x["world"] == "A" and x["run_id"] in FAILED_G2)),
              "checker_passes_every_world_A_package": all(check_ok(c) for c in checks if c["world"] == "A"),
              "checker_on_world_B_G1_fails_only_on_the_declared_SE6_override": all(check_ok(c) for c in checks if c["world"] == "B"),
              "se5_probe_pass": probe["verdict"] == "PASS", "reg1_perturbed_copy_fails": pr["verdict"] == "FAIL",
              "rc8_phase_b_verified": report["rc8_aggregate_a1_phase_b_check"] == "verified",
              "dv13_pass": report["dv13"]["pass"], "dv14_pass": report["dv14"]["pass"],
              "getrlimit_all_10737418240": all(all(g == {"soft": R.CAP_BYTES, "hard": R.CAP_BYTES} for g in (x["getrlimit"] or [])) for x in pkgs),
              "threads_all_1": all((x["threads"] or [1]) == [1] for x in pkgs),
              "every_package_pari_stack_command_returned": all(x["pari_stack_status"] == "command_returned" for x in pkgs)}
    report["summary"] = exp_ok
    report["packages_run"] = len(pkgs)
    report["pass"] = all(exp_ok.values())
    report["not_exercised"] = {"anchor-identity": "hard-codes p' = 16777291 and the Sage comparator; not run at toy scale; run ONCE by DV-18 (b) at its hard-coded parameters (RB-5)",
                               "controls": "hard-codes fixture_n3(4111) and C.ladder_entry(4111 / 262151 / 16777291); not run at toy scale; run ONCE by DV-18 (a) at its hard-coded parameters (RB-5)",
                               "contingency launches": "not launched in the toy; every R-12 refusal is exercised by DV-6"}
    report["finished"] = R.now()
    dump(os.path.join(out, "dv7.json"), report)
    print(json.dumps(report["summary"], indent=1))
    print("DV-7:", "PASS" if report["pass"] else "FAIL")
    return 0 if report["pass"] else 1
