#!/usr/bin/env python3
"""EXP-GFPN-05ff43 stage R1 -- DV-7: TOY INTEGRATION of the repair layer (addendum PS-6 DV-7; RC-3 (f), RC-6, RC-8),
with the DYNAMIC part of DV-1 (a trace of every PARI entry, development harness only).

Called as `python3 -B r1_devchecks.py dv7 --out DIR`. Everything it writes goes under DIR/toy.

Toy objects (NO ladder or fixture prime is used for any solve; precedents v2 DN-5 / DN-8, implementation-v2-a1.md 9 (a)):
  * n = m = 3 fixture data at the toy primes 1033 and 1039 (F_p[z]/(z^3 - c), y^2 = x(x^2 + 2x + c z) with b and
    a2^2 - 4b non-squares, beta the smallest non-square, two regression x_R from a declared toy stream);
  * n = m = 4 fixture data at 1033 (an irreducible quartic modulus, b = (z + 0)^2, beta = 1);
  * toy ladder rungs at 1021 (addendum role) and 1031 (v2 role), chosen by PARI in a capped child with the
    frozen a1_toy.toy_ladder, appended to the frozen ladder.json entries (which are read, never solved);
  * toy copies of BOTH r1 plans (same ids, same metadata): G1 -> fixture --p 1033, G2 -> fixture --p 1039, F-4 ->
    the toy n = 4 data, the 4111 build and its six cells -> p' = 1031 with the m = 5 / m = 4 roles played by m = 3 /
    m = 2; the addendum's controls_a1, build and six cells -> 1021. Toy-only m = 2 watchdog keys are added to both
    r1 copies AND to the toy copy of trial-plan-v2.json (so R-9 runs unmodified).
Not exercisable at toy scale (recorded, not run): `anchor-identity` (hard-codes p' = 16777291 and runs the Sage
comparator on the anchor system) and `controls` (hard-codes the fixture field at 4111 and ladder primes 4111,
262151, 16777291). Their gate roles G3, G4 are SYNTHETIC packages in the toy runs directory. The v2 cells at
262151 and 16777291 are SYNTHETIC rows (as implementation-v2-a1.md 9 (a)).
World A runs G1 once (PYTHONHASHSEED 0); world B runs the whole toy lineage (PYTHONHASHSEED 12345). REG-1 compares
world-B G1 with world-A G1 (RC-6: two processes, different PYTHONHASHSEED); a perturbed copy must fail.
In-process stubs (disclosed): r1_run_wrapper.git_tree_state returns the r1 files tracked and clean, and synthetic
TASK-20260923-b53550 phase-A / phase-B receipts in scratch bind the files as they are (RC-8 form for phase B).
"""
import copy
import json
import os
import random
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_common as R                                    # noqa: E402

TOY_A1_P, TOY_V2_P, TOY_FX3, TOY_FX4_P = 1021, 1031, (1033, 1039), 1033
SEED_A, SEED_B = "0", "12345"
SYN = "SYNTHETIC (DV-7 only): written by the check; never a measurement"
M_ROLE = {5: 3, 4: 2}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(p):
    return R.sha256_file(p)


# ============================================================================ toy data
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
            "a2^2-4b_is_square": False, "beta": A.smallest_nonsquare(p), "targets": tg, "toy_note": "DV-7 toy fixture data"}


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


TOY_V2_CANDIDATES = (1031, 1051, 1061, 1091, 1151, 1171, 1181, 1201)   # declared order; p = 1 mod 5; first complete rung is used


def toy_ladder(tdir):
    """a1_toy.toy_ladder (frozen, read-only) at 1021 for the addendum role, and at the first prime of TOY_V2_CANDIDATES whose
    three toy curves are all found by its rule, for the v2 role. Every attempt is recorded."""
    global TOY_V2_P
    sys.path.insert(0, R.A1_DIR)
    import a1_toy
    trail = []
    a1_toy.TOY_P = TOY_A1_P
    rungs = [a1_toy.toy_ladder(os.path.join(tdir, "ladder_%d" % TOY_A1_P))]
    trail.append({"p": TOY_A1_P, "role": "a1", "complete": rungs[0]["complete"], "curves_found": sorted(rungs[0]["curves"])})
    for p in TOY_V2_CANDIDATES:
        a1_toy.TOY_P = p
        rec = a1_toy.toy_ladder(os.path.join(tdir, "ladder_%d" % p))
        trail.append({"p": p, "role": "v2", "complete": rec["complete"], "curves_found": sorted(rec["curves"])})
        if rec["complete"]:
            TOY_V2_P = p
            rungs.append(rec)
            break
    return rungs, trail


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


def toy_plans(tdir, ladder_path):
    import a1_toy
    import a1_common as AC
    v2r1, a1r1, v2f = R.load_json(R.PLAN_V2_R1), R.load_json(R.PLAN_A1_R1), R.load_json(R.PLAN_V2)
    wd = toy_watchdogs(v2f)
    for pl in (v2r1, a1r1, v2f):
        pl["watchdogs"] = wd
        pl["toy_note"] = "TOY copy (DV-7): toy primes, m = 3 / 2 roles, toy-only m = 2 watchdog keys"
    by = {pk["order"]: pk for pk in v2r1["packages"]}
    by[1].update(driver_args=["fixture", "--p", str(TOY_FX3[0])], p=TOY_FX3[0])
    by[2].update(driver_args=["fixture", "--p", str(TOY_FX3[1])], p=TOY_FX3[1])
    by[6].update(driver_args=["build", "--p", str(TOY_V2_P)], p=TOY_V2_P, builds=toy_builds())
    m5 = {}
    for o, s in zip((7, 8, 9), AC.SHAPES):
        by[o].update(driver_args=["cells", "--p", str(TOY_V2_P), "--shape", s, "--m", "3"], p=TOY_V2_P, m=3, shape=s,
                     cells=a1_toy.toy_cells(s, 5, TOY_V2_P))
        m5[s] = by[o]["run_id"]
    for o, s in zip((10, 11, 12), AC.SHAPES):
        by[o].update(driver_args=["cells", "--p", str(TOY_V2_P), "--shape", s, "--m", "2", "--prior-run", m5[s]], p=TOY_V2_P, m=2, shape=s,
                     cells=a1_toy.toy_cells(s, 4, TOY_V2_P))
    v2r1["cells_enumeration"], v2r1["n_cells_enumerated"] = [], 0
    ba = {pk["order"]: pk for pk in a1r1["packages"]}
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
    a1r1["cells_enumeration"], a1r1["n_cells_enumerated"] = [], 0
    sys.path.insert(0, R.V2_DIR)
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
    a1r1["rescaling_parameters"] = dict(a1r1["rescaling_parameters"], p=TOY_A1_P, per_shape=resc)
    return v2r1, a1r1, v2f


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


# ============================================================================ shims (development only; never delivered)
HOOKS = r'''
import os, sys, json, re, traceback, importlib.abc, importlib.util
sys.dont_write_bytecode = True
CFG = json.load(open(os.environ["R1_TOY_CFG"]))
sys.path.insert(0, CFG["layer_dir"])
import r1_common as R
for k, v in CFG["R"].items():
    setattr(R, k, v)
TRACE = os.environ.get("R1_TOY_TRACE")

def _log(ev, expr=None, extra=None):
    if not TRACE:
        return
    st = ["%s:%d" % (os.path.relpath(f.filename, CFG["exp_real"]), f.lineno) for f in traceback.extract_stack()[:-2]
          if "implementation-v2" in f.filename]
    rec = {"event": ev, "pid": os.getpid(), "argv": sys.argv[1:], "stack": st[-8:]}
    if expr:
        m = re.search(r"ffgen\(Mod\(1, (\d+)\)\*\((.*?)\), 'w\)", expr)
        if m:
            rec["p"] = int(m.group(1))
            rec["field_degree"] = max(int(x) for x in re.findall(r"w\^(\d+)", m.group(2)))
        rec["expr_head"] = expr[:200]
    if extra:
        rec.update(extra)
    with open(TRACE, "a") as fh:
        fh.write(json.dumps(rec) + "\n")

sys.addaudithook(lambda ev, args: _log("import:" + args[0]) if ev == "import" and args and args[0] in ("cypari2", "sage.all", "sage") else None)
import cypari2
_Base = cypari2.Pari
class TracingPari(_Base):
    def __init__(self, *a, **k):
        _log("cypari2.Pari()")
        super().__init__(*a, **k)
    def __call__(self, s, *a, **k):
        _log("cypari2.Pari.__call__", expr=str(s))
        return super().__call__(s, *a, **k)
cypari2.Pari = TracingPari

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
            if _n == "v2_solver":
                rc = module.run_child
                def run_child(argv, *a, **k):
                    _log("child", extra={"child_argv0": os.path.basename(argv[0]), "child_argv": [os.path.basename(x) for x in argv[:4]]})
                    return rc(argv, *a, **k)
                module.run_child = run_child
        spec.loader.exec_module = exec_module
        return spec
sys.meta_path.insert(0, Hook())
'''

ENTRY_SHIM = HOOKS + r'''
import runpy
entry = CFG["entry"][os.environ["R1_TOY_ENTRY"]]
sys.argv = [entry] + sys.argv[1:]
runpy.run_path(entry, run_name="__main__")
'''

CHECK_SHIM = HOOKS + r'''
import r1_check_run as K
mode, rd = sys.argv[1], sys.argv[2]
sys.exit(K.frozen_v2(rd) if mode == "frozen-v2" else K.frozen_a1(rd))
'''


# ============================================================================ the integration
def dv7(out, rest):
    tdir = os.path.join(out, "toy")
    if os.path.exists(tdir):
        shutil.rmtree(tdir)
    os.makedirs(tdir)
    report = {"toy_primes": {"a1_role": TOY_A1_P, "v2_role": TOY_V2_P, "fixture_n3": TOY_FX3, "fixture_n4": TOY_FX4_P},
              "no_ladder_or_fixture_prime_solved": True}
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC                                                       # noqa: F401
    print("(1) toy data")
    fx3 = {"task": "DV-7 toy", "n": 3, "m": 3, "primes": [toy_fixture_n3(p) for p in TOY_FX3]}
    fx3_path = os.path.join(tdir, "toy_fixture_n3.json")
    dump(fx3_path, fx3)
    fx4_path = os.path.join(tdir, "toy_fixture_n4.json")
    dump(fx4_path, toy_fixture_n4(TOY_FX4_P))
    rungs, trail = toy_ladder(tdir)
    report["toy_ladder_selection_trail"] = trail
    report["toy_primes"]["v2_role"] = TOY_V2_P
    report["toy_ladder"] = [{k: r.get(k) for k in ("p", "cmod", "field", "complete", "curves")} for r in rungs]
    if len(rungs) != 2 or not all(r["complete"] for r in rungs):
        report["pass"] = False
        dump(os.path.join(out, "dv7.json"), report)
        print("DV-7: FAIL (toy ladder incomplete)")
        return 1
    ladder_path = os.path.join(tdir, "toy-ladder.json")
    dump(ladder_path, R.load_json(R.LADDER_PATH) + rungs)
    print("(2) toy plans")
    v2r1, a1r1, v2f = toy_plans(tdir, ladder_path)
    pv2, pa1, pv2f = (os.path.join(tdir, n) for n in ("toy-trial-plan-v2-r1.json", "toy-trial-plan-v2-a1-r1.json", "toy-trial-plan-v2.json"))
    dump(pv2, v2r1)
    dump(pa1, a1r1)
    dump(pv2f, v2f)
    G = v2r1["gate"]["blocking_packages"]
    cache = os.path.join(tdir, "cache")
    os.makedirs(cache)
    os.environ["GFPN_V2_CACHE_DIR"] = cache
    # synthetic phase-A receipt for the r1 tree (R-6) + git stub
    r1files = sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _d, fn in os.walk(os.path.join(R.REPO, R.R1_PATHS_REL[0])) for f in fn) + R.R1_PATHS_REL[1:]
    rec_a = os.path.join(tdir, "toy-b53550-phase-a-receipt.json")
    dump(rec_a, {"synthetic": SYN, "commit_sha": "dv7-synthetic-not-a-commit", "path_sha256": {p: sha(os.path.join(R.REPO, p)) for p in r1files}})
    rec_b = os.path.join(tdir, "toy-b53550-post-run-receipt.json")          # written after the v2 packages (RC-8 form)
    worlds = {}
    for w in ("A", "B"):
        exp = os.path.join(tdir, "world_%s" % w, "exp")
        os.makedirs(os.path.join(exp, "runs"))
        worlds[w] = exp
    reg_ref_receipt = os.path.join(tdir, "toy-reference-receipt.json")

    def cfg(w):
        p = os.path.join(tdir, "toy-cfg-%s.json" % w)
        dump(p, {"layer_dir": HERE, "exp_real": R.EXP_DIR,
                 "R": {"PLAN_V2_R1": pv2, "PLAN_A1_R1": pa1, "PLAN_V2": pv2f, "RECEIPT_R1_PHASE_A": rec_a, "RECEIPT_R1_PHASE_B": rec_b,
                       "RUNS_DIR": os.path.join(worlds["A"], "runs"), "REG1_REFERENCE_RUN": G[0], "RECEIPT_V2_PHASE_B": reg_ref_receipt},
                 "mods": {"v2_common": {"EXP_DIR": worlds[w], "LADDER_PATH": ladder_path, "FIXTURE_N3_JSON": fx3_path, "FIXTURE_N4_JSON": fx4_path},
                          "a1_common": {"EXP_DIR": worlds[w], "RUNS_DIR": os.path.join(worlds[w], "runs"), "LADDER_PATH": ladder_path}},
                 "entry": {"v2": os.path.join(HERE, "r1_entry_v2.py"), "a1": os.path.join(HERE, "r1_entry_a1.py")}})
        return p
    shims = os.path.join(tdir, "shims")
    os.makedirs(shims)
    for name, body in (("entry_v2_toy.py", ENTRY_SHIM), ("entry_a1_toy.py", ENTRY_SHIM), ("check_toy.py", CHECK_SHIM)):
        with open(os.path.join(shims, name), "w") as fh:
            fh.write(body)
    # ---- in-process redirection of the wrapper and checker (harness process)
    import r1_run_wrapper as W
    import r1_check_run as K
    import r1_reg1 as REG
    for k, v in {"PLAN_V2_R1": pv2, "PLAN_A1_R1": pa1, "PLAN_V2": pv2f, "RECEIPT_R1_PHASE_A": rec_a, "RECEIPT_R1_PHASE_B": rec_b,
                 "RUNS_DIR": os.path.join(worlds["A"], "runs"), "REG1_REFERENCE_RUN": G[0], "RECEIPT_V2_PHASE_B": reg_ref_receipt}.items():
        setattr(R, k, v)
    real_git = W.git_tree_state
    W.git_tree_state = lambda paths: (r1files, []) if paths == R.R1_PATHS_REL else real_git(paths)
    W.ENTRY_V2 = os.path.join(shims, "entry_v2_toy.py")
    W.ENTRY_A1 = os.path.join(shims, "entry_a1_toy.py")
    trace = os.path.join(tdir, "pari-trace.jsonl")
    os.environ["R1_TOY_TRACE"] = trace
    pkgs = []

    def run(w, rid, entry_kind, seed):
        os.environ["R1_TOY_CFG"] = cfg(w)
        os.environ["R1_TOY_ENTRY"] = entry_kind
        os.environ["PYTHONHASHSEED"] = seed
        W.RUNS = os.path.join(worlds[w], "runs")
        rc = W.main([rid])
        d = os.path.join(W.RUNS, rid)
        man = None
        if os.path.exists(os.path.join(d, "manifest.yaml")):
            import yaml
            man = yaml.safe_load(open(os.path.join(d, "manifest.yaml")))["run"]
        row = {"world": w, "run_id": rid, "entry": entry_kind, "PYTHONHASHSEED": seed, "wrapper_rc": rc, "status": man and man["status"],
               "failure_class": man and man["failure_class"], "gate_pass": man and man["result"]["gate_pass"],
               "getrlimit": man and man["resources"]["child_rlimit_as_read_back_by_getrlimit"],
               "threads": man and man["resources"]["msolve_threads_executed"],
               "pari_stack_status": man and (man["resources"]["pari_stack"] or {}).get("status"),
               "reg1_in_manifest": man and ((man.get("gate") or {}).get("regression_REG-1") or {}).get("verdict")}
        pkgs.append(row)
        print("   world %s %s %-6s rc=%s status=%s gate_pass=%s REG-1=%s" % (w, rid, entry_kind, rc, row["status"], row["gate_pass"], row["reg1_in_manifest"]))
        return row
    print("(3) world A: G1 (toy fixture 1033), PYTHONHASHSEED %s" % SEED_A)
    run("A", G[0], "v2", SEED_A)
    ga = os.path.join(worlds["A"], "runs", G[0])
    dump(reg_ref_receipt, {"synthetic": SYN, "path_sha256": {os.path.relpath(os.path.join(dp, f), R.REPO): sha(os.path.join(dp, f))
                                                             for dp, _d, fn in os.walk(ga) for f in fn}})
    print("(4) world B: G1, PYTHONHASHSEED %s; REG-1 (RC-6 probe)" % SEED_B)
    run("B", G[0], "v2", SEED_B)
    gb = os.path.join(worlds["B"], "runs", G[0])
    probe = REG.compare(ga, gb, receipt=reg_ref_receipt)
    report["rc6_probe"] = {"PYTHONHASHSEED": {"world_A": SEED_A, "world_B": SEED_B}, "verdict": probe["verdict"], "failures": probe["failures"],
                           "output": REG.render(probe)}
    print(REG.render(probe).splitlines()[-1])
    if probe["verdict"] != "PASS":
        report["STOP"] = "RC-6: a field REG-1 compares differs between two toy runs in separate processes with different PYTHONHASHSEED"
        report["pass"] = False
        dump(os.path.join(out, "dv7.json"), report)
        print("DV-7: STOP (RC-6)")
        return 3
    pert = os.path.join(tdir, "perturbed", G[0])
    shutil.copytree(gb, pert)
    rp = os.path.join(pert, "raw-result.json")
    r = json.load(open(rp))
    r["planted_targets"][0]["arms"][list(r["planted_targets"][0]["arms"])[0]]["D"] += 1
    json.dump(r, open(rp, "w"), indent=1)
    pr = REG.compare(ga, pert, receipt=reg_ref_receipt)
    report["reg1_perturbed_copy"] = {"perturbation": "planted_targets[0] first arm D + 1", "verdict": pr["verdict"], "failures": pr["failures"]}
    print("   REG-1 on a perturbed copy:", pr["verdict"])
    print("(5) world B: G2 (toy fixture 1039); G3, G4 SYNTHETIC; F-4 (toy n = 4); v2 build, cells, aggregate; addendum packages")
    run("B", G[1], "v2", SEED_B)
    runsB = os.path.join(worlds["B"], "runs")
    for g, why in ((G[2], "anchor-identity is not exercisable at toy scale (hard-coded p' = 16777291 and the Sage anchor system)"),
                   (G[3], "controls is not exercisable at toy scale (hard-coded fixture field at 4111 and ladder primes 4111, 262151, 16777291)")):
        synthetic_pkg(runsB, g, {"kind": "synthetic_gate", "run_status": "completed_valid", "gate_pass": True, "synthetic": SYN, "reason": why})
    by = {pk["order"]: pk for pk in v2r1["packages"]}
    for o in [5, 6, 7, 8, 9, 10, 11, 12]:
        run("B", by[o]["run_id"], "v2", SEED_B)
    synthetic_v2_cells(runsB, v2r1, skip_ids={by[o]["run_id"] for o in range(7, 13)})
    run("B", by[27]["run_id"], "v2", SEED_B)
    v2_read = [by[o]["run_id"] for o in range(1, 28) if by[o]["kind"] in ("cells", "aggregate")]
    dump(rec_b, {"synthetic": SYN, "commit_sha": "dv7-synthetic-not-a-commit",
                 "path_sha256": {os.path.relpath(os.path.join(runsB, i, "raw-result.json"), R.REPO): sha(os.path.join(runsB, i, "raw-result.json")) for i in v2_read}})
    ba = {pk["order"]: pk for pk in a1r1["packages"]}
    for o in range(1, 10):
        run("B", ba[o]["run_id"], "a1", SEED_B)
    agg = R.load_json(os.path.join(runsB, ba[9]["run_id"], "raw-result.json"))
    report["rc8_aggregate_a1_phase_b_check"] = (agg.get("v2_bytes_phase_B_check") or {}).get("status")
    report["packages"] = pkgs
    print("(6) the r1 checker on every toy package that ran through the wrapper")
    K.FROZEN_LAUNCHER = [sys.executable, "-B", os.path.join(shims, "check_toy.py")]
    checks = []
    import contextlib
    import io
    for x in pkgs:
        os.environ["R1_TOY_CFG"] = cfg(x["world"])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = K.main(os.path.join(worlds[x["world"]], "runs", x["run_id"]))
        checks.append({"world": x["world"], "run_id": x["run_id"], "rc": rc, "output": buf.getvalue().splitlines()})
        print("   check world %s %s rc=%s" % (x["world"], x["run_id"], rc))
    report["checker"] = checks
    # ---- forbidden task ids anywhere in the toy trees
    bad = []
    for dp, _d, fn in os.walk(tdir):
        for f in fn:
            b = open(os.path.join(dp, f), "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    bad.append({"file": os.path.relpath(os.path.join(dp, f), tdir), "id": t})
    report["forbidden_task_ids_in_toy_artifacts"] = bad
    # ---- DV-1 dynamic trace summary
    tr = [json.loads(l) for l in open(trace)] if os.path.exists(trace) else []
    calls = [t for t in tr if t["event"] == "cypari2.Pari.__call__"]
    report["dv1_dynamic"] = {
        "trace_file": trace, "n_events": len(tr),
        "in_process_pari_calls": sorted({(t["argv"][0] if t["argv"] else None, t.get("p"), t.get("field_degree"), " <- ".join(reversed(t["stack"][-3:])))
                                         for t in calls}),
        "cypari2_constructions_by_caller": sorted({(t["argv"][0] if t["argv"] else None, t["stack"][-1] if t["stack"] else None)
                                                   for t in tr if t["event"] == "cypari2.Pari()"}),
        "children": sorted({(t["argv"][0] if t["argv"] else None, t.get("child_argv0")) for t in tr if t["event"] == "child"}),
        "imports": sorted({(t["argv"][0] if t["argv"] else None, t["event"]) for t in tr if t["event"].startswith("import:")})}
    exp_ok = all(x["status"] == "completed_valid" for x in pkgs) and all(c["rc"] == 0 for c in checks)
    report["summary"] = {"packages_run": len(pkgs), "all_completed_valid": all(x["status"] == "completed_valid" for x in pkgs),
                         "all_checker_pass": all(c["rc"] == 0 for c in checks), "rc6_probe": probe["verdict"],
                         "reg1_perturbed_copy_fails": pr["verdict"] == "FAIL", "rc8_phase_b_verified": report["rc8_aggregate_a1_phase_b_check"] == "verified",
                         "no_forbidden_task_id": not bad,
                         "getrlimit_all_10737418240": all(all(g == {"soft": R.CAP_BYTES, "hard": R.CAP_BYTES} for g in (x["getrlimit"] or [])) for x in pkgs),
                         "threads_all_1": all((x["threads"] or [1]) == [1] for x in pkgs)}
    report["pass"] = exp_ok and all(v for k, v in report["summary"].items() if k not in ("packages_run", "rc6_probe")) and probe["verdict"] == "PASS"
    report["not_exercised"] = {"anchor-identity": "hard-codes p' = 16777291 and runs the Sage comparator on the anchor system; exercising it solves an anchor system at a ladder prime (forbidden in R1)",
                               "controls": "hard-codes fixture_n3(4111) and C.ladder_entry(4111 / 262151 / 16777291); every system it solves is at a fixture or ladder prime (forbidden in R1); its in-process PARI point (4111, n = 3) is covered by DV-2",
                               "contingency launches": "not launched in the toy; every R-12 refusal is exercised by DV-6"}
    dump(os.path.join(out, "dv7.json"), report)
    print(json.dumps(report["summary"], indent=1))
    print(json.dumps(report["dv1_dynamic"], indent=1, default=str)[:4000])
    print("DV-7:", "PASS" if report["pass"] else "FAIL")
    return 0 if report["pass"] else 1
