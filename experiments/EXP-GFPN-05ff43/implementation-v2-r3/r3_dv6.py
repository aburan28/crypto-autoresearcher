#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r3 successor stage -- DV-6: r3 wrapper refusals R-1..R-13 (dry-runs), the entry points' PARI
read-back refusal, the RC-3 redirection read-back refusal, the SE-3 and HR-3 replacement read-back refusals (attribute
rebound after install; recorded original replaced), a v2-entry case with a1_health imported, and the VA-7 (a) refusals
(an r3 constant, a redirected attribute or a plan string carrying a forbidden task id). Started from
implementation-v2-r2/r2_dv6.py. Development only; everything simulated lives in --out.

Simulation (precedent implementation-v2-a1.md X-4): module-level constants of r3_common / r3_run_wrapper are
redirected IN THIS PROCESS to scratch copies; git state and the solver-process scan are replaced by stubs where a
case needs a state that cannot be produced for real. Two stubs are used throughout so that each case shows its OWN
reason: r3_run_wrapper.git_tree_state returns the r3 files as tracked and clean (the r3 tree is not committed in
this stage) and a synthetic TASK-20260924-f1fb0e phase-A receipt in scratch binds the r3 files as they are. The real
R-6 refusal (uncommitted tree, absent receipt) is its own case. A synthetic G1 made from a byte copy of
RUN-GFPN-ac4487 also carries a structurally valid no-event solver-events.json, so that REG-1 passes on it wherever a
case label says so (the r2 SD-4 disclosure). Every case must exit 2 with its expected reason and write nothing (the
real and scratch runs directories and the r3 tree are compared before and after).
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_common as R                                    # noqa: E402


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def snapshot(dirs):
    out = {}
    for d in dirs:
        for dp, dn, fn in os.walk(d):
            for n in dn + fn:
                out[os.path.join(dp, n)] = None if n in dn else sha(os.path.join(dp, n))
    return out


@contextlib.contextmanager
def patched(obj, **kw):
    old = {k: getattr(obj, k) for k in kw}
    for k, v in kw.items():
        setattr(obj, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(obj, k, v)


def r3_files():
    d = os.path.join(R.REPO, R.R3_PATHS_REL[0])
    return sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _dn, fn in os.walk(d) for f in fn) + R.R3_PATHS_REL[1:]


def synthetic_r3_receipt(path):
    dump(path, {"synthetic": "DV-6 only: binds the r3 layer files as they are now; never a receipt", "commit_sha": "dv6-synthetic-not-a-commit",
                "path_sha256": {p: sha(os.path.join(R.REPO, p)) for p in r3_files()}})


def no_event_doc():
    return {"schema": "crypto.autoresearch.gfpn05.r3.solver_events.v1", "synthetic": "DV-6 only: a structurally valid no-event file",
            "K": 5, "spacing_s": 2.0, "consistency_violation": False,
            "sites": {R.SITE_S1: {"counters": {}, "events": []}, R.SITE_S2: {"counters": {}, "events": []}, R.SITE_S3: {"counters": {}, "records": []}}}


def write_pkg(runs, rid, status="completed_valid", gate_pass=True, manifest=True, failure_class=None, replaces=None, copy_from=None):
    d = os.path.join(runs, rid)
    if copy_from:
        shutil.copytree(copy_from, d)
        dump(os.path.join(d, "solver-events.json"), no_event_doc())
    else:
        os.makedirs(d, exist_ok=True)
        dump(os.path.join(d, "raw-result.json"), {"kind": "synthetic", "run_status": status, "gate_pass": gate_pass, "synthetic": "DV-6"})
    if manifest:
        import yaml
        with open(os.path.join(d, "manifest.yaml"), "w") as fh:
            yaml.safe_dump({"run": {"id": rid, "status": status, "failure_class": failure_class, "package": {"replaces": replaces},
                                    "synthetic": "DV-6"}}, fh)
    elif os.path.exists(os.path.join(d, "manifest.yaml")):
        os.remove(os.path.join(d, "manifest.yaml"))
    return d


def dv6(out, rest):
    os.makedirs(out, exist_ok=True)
    sys.path.insert(0, R.V2_DIR)
    import r3_run_wrapper as W
    import v2_solver as V
    P = {"v2r3": R.load_json(R.PLAN_V2_R3), "a1r3": R.load_json(R.PLAN_A1_R3)}
    m2, m1 = P["v2r3"]["id_map"], P["a1r3"]["id_map"]
    G = P["v2r3"]["gate"]["blocking_packages"]           # G1..G4 (r3 ids)
    F4, BUILD4111, CONT1, CONT2 = m2["RUN-GFPN-a07776"], m2["RUN-GFPN-1ad09b"], m2["RUN-GFPN-e26e4b"], m2["RUN-GFPN-9da048"]
    CTL_A1, BUILD_A1 = m1["RUN-GFPN-0d91bf"], m1["RUN-GFPN-8c772a"]
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)
    rec_path = os.path.join(out, "synthetic-f1fb0e-phase-a-receipt.json")
    synthetic_r3_receipt(rec_path)
    real_git = W.git_tree_state
    tracked_r3 = r3_files()

    def git_ok(paths):
        if paths == R.R3_PATHS_REL:
            return tracked_r3, []
        return real_git(paths)
    watched = [R.RUNS_DIR, os.path.join(R.REPO, R.R3_PATHS_REL[0])]
    results = []

    def case(name, argv, expect, runs=None, attrs_R=None, attrs_W=None, attrs_V=None, real_r6=False):
        scratch = runs or R.RUNS_DIR
        before = snapshot(watched + ([scratch] if runs else []))
        ctx = contextlib.ExitStack()
        wr = {"git_tree_state": real_git if real_r6 else git_ok, "RUNS": scratch}
        wr.update(attrs_W or {})
        rr = {} if real_r6 else {"RECEIPT_R3_PHASE_A": rec_path}
        rr.update(attrs_R or {})
        ctx.enter_context(patched(W, **wr))
        ctx.enter_context(patched(R, **rr))
        if attrs_V:
            ctx.enter_context(patched(V, **attrs_V))
        err = io.StringIO()
        with ctx, contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = W.main(list(argv) + ["--dry-run"])
        after = snapshot(watched + ([scratch] if runs else []))
        lines = [l for l in err.getvalue().splitlines() if l.strip()]
        hit = [l for l in lines if expect in l]
        ok = rc == 2 and bool(hit) and before == after
        results.append({"case": name, "argv": list(argv) + ["--dry-run"], "rc": rc, "expected_reason": expect, "matched": hit,
                        "all_reasons": lines, "nothing_written": before == after, "pass": ok})
        print("  %-78s rc=%s %s" % (name, rc, "PASS" if ok else "FAIL"))
        return ok

    def scratch_runs(tag):
        d = os.path.join(out, "runs", tag)
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
        return d

    # ---- baseline: G1 passes every check with the two declared stubs (proves each later case isolates its reason)
    err = io.StringIO()
    with patched(W, git_tree_state=git_ok), patched(R, RECEIPT_R3_PHASE_A=rec_path), contextlib.redirect_stdout(err), contextlib.redirect_stderr(err):
        rc0 = W.main([G[0], "--dry-run"])
    baseline = {"argv": [G[0], "--dry-run"], "rc": rc0, "output": err.getvalue().splitlines()}
    print("  baseline G1 dry-run with the declared stubs: rc=%s %s" % (rc0, err.getvalue().strip()))
    # ---- R-1 (altered copies of each of the NINE bound files)
    for i, (path, want) in enumerate(R.BOUND_HASHES):
        alt = os.path.join(out, "altered", os.path.basename(path))
        os.makedirs(os.path.dirname(alt), exist_ok=True)
        shutil.copy(path, alt)
        with open(alt, "a") as fh:
            fh.write("# altered copy (DV-6)\n")
        bh = list(R.BOUND_HASHES)
        bh[i] = (alt, want)
        case("R-1 altered %s" % os.path.basename(path), [G[0]], "R-1 %s sha256" % os.path.basename(path), attrs_R={"BOUND_HASHES": tuple(bh)})
    # ---- R-2
    for rid, what in (("RUN-GFPN-ac4487", "a v2 run id"), ("RUN-GFPN-3377f1", "a v2 run id"), ("RUN-GFPN-76420e", "a v2 run id"),
                      ("RUN-GFPN-e26e4b", "a v2 run id"), ("RUN-GFPN-0d91bf", "a v2-a1 run id"), ("RUN-GFPN-61bba9", "a v1 run id"),
                      ("RUN-GFPN-a61a10", "an r1 run id"), ("RUN-GFPN-51e56b", "an r1 run id"), ("RUN-GFPN-a09162", "an r2 run id"),
                      ("RUN-GFPN-0fa6cd", "an r2 run id"), ("RUN-GFPN-0f0f0f", "not reserved")):
        case("R-2 %s (%s)" % (rid, what), [rid], "R-2 %s is %s" % (rid, what))
    case("R-2 RUN-GFPN-c8c1f8 (an r2 contingency id: on the 124-id retired list)", ["RUN-GFPN-c8c1f8"], "R-2 RUN-GFPN-c8c1f8 is a retired run id (the 124 retired ids)")
    # exhaustive: every one of the 124 retired ids, every frozen v2 / v2-a1 id and every v1 id is refused by R-2
    v1ids = sorted(set(R.load_json(R.PLAN_V2)["v1_ids_never_reused"]) | set(R.load_json(R.PLAN_A1)["v1_ids_never_reused"]))
    frozen_all = [x["run_id"] for x in R.load_json(R.PLAN_V2)["packages"]] + [x["run_id"] for x in R.load_json(R.PLAN_A1)["packages"]]
    sweep = []
    for rid in sorted(set(R.RETIRED_ALL) | set(frozen_all) | set(v1ids)):
        with patched(W, git_tree_state=git_ok), patched(R, RECEIPT_R3_PHASE_A=rec_path), contextlib.redirect_stdout(io.StringIO()):
            refs, _info = W.preflight(rid)
        r2hits = [x for x in refs if x.startswith("R-2 ")]
        sweep.append({"id": rid, "refused_by_R2": bool(r2hits) and any("not reserved" not in x for x in r2hits), "reasons": r2hits})
    sweep_ok = all(x["refused_by_R2"] for x in sweep)
    print("  R-2 exhaustive sweep: %d ids (124 retired, 42 frozen, v1), all refused by R-2 with an id-class reason: %s" % (len(sweep), sweep_ok))
    # ---- R-3
    s = scratch_runs("r3")
    os.makedirs(os.path.join(s, G[0]))
    case("R-3 run directory exists", [G[0]], "R-3 run directory exists", runs=s)
    # ---- R-4 / R-5 receipt mismatch and dirty tree (simulated)
    for tag, attr, paths in (("R-4", "RECEIPT_V2_PHASE_A", R.V2_PATHS_REL), ("R-5", "RECEIPT_A1_PHASE_A", R.A1_PATHS_REL)):
        rc = R.load_json(getattr(R, attr))
        k = sorted(R.receipt_paths(rc))[0]
        rc["path_sha256"][k] = "0" * 64
        alt = os.path.join(out, "altered", "%s-receipt.json" % tag)
        dump(alt, rc)
        case("%s receipt mismatch" % tag, [G[0]], "%s paths differ from" % tag, attrs_R={attr: alt})

        def git_dirty(p, _paths=paths):
            if p == R.R3_PATHS_REL:
                return tracked_r3, []
            tr, _ = real_git(p)
            return tr, ([" M %s/simulated.py" % _paths[0]] if p == _paths else [])
        case("%s dirty tree (simulated git state)" % tag, [G[0]], "%s paths are dirty" % tag, attrs_W={"git_tree_state": git_dirty})
    # ---- R-6: the REAL state (tree uncommitted, receipt absent), and a synthetic receipt mismatch
    case("R-6 real state: r3 tree uncommitted, f1fb0e phase-A receipt absent", [G[0]], "R-6", real_r6=True)
    rc = R.load_json(rec_path)
    k = sorted(rc["path_sha256"])[0]
    rc["path_sha256"][k] = "0" * 64
    alt = os.path.join(out, "altered", "R-6-receipt.json")
    dump(alt, rc)
    case("R-6 receipt mismatch (synthetic receipt)", [G[0]], "R-6 paths differ from", attrs_R={"RECEIPT_R3_PHASE_A": alt})
    # ---- R-7
    case("R-7 gate not run (F-4 image, real runs directory)", [F4], "R-7 repaired gate package %s has not run" % G[0])
    s = scratch_runs("r7_failed")
    write_pkg(s, G[0], copy_from=ref)
    write_pkg(s, G[1], status="failed", gate_pass=False, failure_class="infrastructure_error")
    write_pkg(s, G[2])
    write_pkg(s, G[3])
    case("R-7 gate failed (G2 failed; REG-1 passes on the synthetic G1)", [F4], "R-7 repaired gate package %s did not pass" % G[1], runs=s)
    s = scratch_runs("r7_reg1")
    g1 = write_pkg(s, G[0], copy_from=ref)
    rp = os.path.join(g1, "raw-result.json")
    r = json.load(open(rp)); r["targets"][0]["arms"]["raw_x"]["D"] = 383; json.dump(r, open(rp, "w"), indent=1)
    case("R-7 REG-1 failed on a synthetic pair (G1 copy with one D perturbed)", [G[1]], "R-7 REG-1 did not pass", runs=s)
    s = scratch_runs("r7_ctl")
    write_pkg(s, G[0], copy_from=ref)
    for g in G[1:]:
        write_pkg(s, g)
    write_pkg(s, CTL_A1, status="completed_valid", gate_pass=False)
    case("R-7 controls_a1 image not passed", [BUILD_A1], "R-7 controls_a1 image %s did not pass" % CTL_A1, runs=s)
    # ---- R-8
    s = scratch_runs("r8")
    write_pkg(s, G[0], copy_from=ref, manifest=False)
    case("R-8 predecessor without manifest (G2 requires G1)", [G[1]], "R-8 required earlier package %s" % G[0], runs=s)
    # ---- R-9
    p = copy.deepcopy(P["v2r3"])
    p["watchdogs"]["comparator_timeout_s"] = 3601
    alt = os.path.join(out, "altered", "trial-plan-v2-r3.watchdog.json")
    dump(alt, p)
    case("R-9 watchdog value changed (plan copy)", [G[0]], "R-9", attrs_R={"PLAN_V2_R3": alt})
    # ---- R-10
    case("R-10 other solver process (simulated scan)", [G[0]], "R-10 another solver-like process",
         attrs_V={"other_solver_processes": lambda own_pids=(): [{"pid": 1, "argv0": "msolve", "cmdline": "msolve (DV-6 simulated)"}]})
    # ---- R-11
    s = scratch_runs("r11")
    frozen = [x["run_id"] for x in R.load_json(R.PLAN_V2)["packages"]] + [x["run_id"] for x in R.load_json(R.PLAN_A1)["packages"]]
    extra = R.RETIRED_R1[:3] + R.RETIRED_R2[:3]                # r1 and r2 ids count toward the eight-plan ceiling (HR-10)
    for i in frozen + extra:
        os.makedirs(os.path.join(s, i))
    case("R-11 shared ceiling: 48 synthetic run directories (42 frozen + 3 r1 + 3 r2 ids)", [G[0]], "R-11 ceiling: 48 run directories", runs=s)
    q = copy.deepcopy(P["a1r3"])
    q["package_count"] = 1
    alt = os.path.join(out, "altered", "trial-plan-v2-a1-r3.count.json")
    dump(alt, q)
    s = scratch_runs("r11own")
    os.makedirs(os.path.join(s, CTL_A1))
    case("R-11 the plan's own package_count (plan copy with 1)", [BUILD_A1], "R-11 the plan's own package_count", runs=s, attrs_R={"PLAN_A1_R3": alt})
    # ---- R-12
    s = scratch_runs("r12")
    write_pkg(s, G[0], copy_from=ref)
    write_pkg(s, G[1], status="failed", gate_pass=False, failure_class="infrastructure_error")
    write_pkg(s, G[2])
    write_pkg(s, G[3])
    write_pkg(s, BUILD4111, status="failed", gate_pass=None, failure_class="implementation_error")
    case("R-12 contingency on a gate package", [CONT1, "--replaces", G[1]], "is a gate package", runs=s)
    case("R-12 contingency across plans", [CONT1, "--replaces", BUILD_A1], "SAME r3 plan", runs=s)
    case("R-12 contingency on a non-infrastructure class", [CONT1, "--replaces", BUILD4111], "only an infrastructure_error package", runs=s)
    s2 = scratch_runs("r12twice")
    for g in (G[0],):
        write_pkg(s2, g, copy_from=ref)
    for g in G[1:]:
        write_pkg(s2, g)
    write_pkg(s2, BUILD4111, status="failed", gate_pass=None, failure_class="infrastructure_error")
    write_pkg(s2, CONT2, replaces=BUILD4111)
    case("R-12 contingency twice (already replaced once)", [CONT1, "--replaces", BUILD4111], "was already replaced once", runs=s2)
    case("R-12 --replaces on a non-contingency id", [F4, "--replaces", BUILD4111], "only valid for a contingency id", runs=s2)
    # ---- R-13
    p = copy.deepcopy(P["v2r3"])
    p["protocol_version"] = 2
    alt = os.path.join(out, "altered", "trial-plan-v2-r3.label.json")
    dump(alt, p)
    case("R-13 wrong protocol label (plan copy)", [G[0]], "R-13 the plan does not record", attrs_R={"PLAN_V2_R3": alt})
    for key in R.REPAIR_KEYS:
        p = copy.deepcopy(P["v2r3"])
        p["repair"]["amendments"][key]["sha256"] = "0" * 64
        alt = os.path.join(out, "altered", "trial-plan-v2-r3.%s-sha.json" % key)
        dump(alt, p)
        case("R-13 wrong %s sha256 in the repair block (plan copy)" % key, [G[0]], "R-13 the plan does not record", attrs_R={"PLAN_V2_R3": alt})
    for j, fid in enumerate(R.FORBIDDEN_TASK_IDS):
        p = copy.deepcopy(P["v2r3"])
        p["dv6_note"] = "carries " + fid
        alt = os.path.join(out, "altered", "trial-plan-v2-r3.forbidden%d.json" % j)
        dump(alt, p)
        case("R-13 forbidden task id #%d in the plan (plan copy)" % (j + 1), [G[0]], "R-13 the plan carries a forbidden task id", attrs_R={"PLAN_V2_R3": alt})
    case("R-13 / VA-7 (a): an r3 constant (the stage card constant, patched in this process) carries a forbidden task id", [G[0]],
         "R-13 (VA-7 (a)) an r3 constant or redirected attribute value carries a forbidden task id",
         attrs_R={"TASK_STAGE": R.FORBIDDEN_TASK_IDS[4]})
    # ---- entry points: PARI read-back refusal and RC-3 (f) redirection read-back refusal (fresh processes)
    entries = []
    shim = os.path.join(out, "entry_refusal_shim.py")
    with open(shim, "w") as fh:
        fh.write(ENTRY_SHIM % {"here": HERE})
    for entry, mode, expect, nothing in (
            ("r3_entry_v2.py", "pari", "RC-2 (a)", False), ("r3_entry_a1.py", "pari", "RC-2 (a)", False),
            ("r3_entry_v2.py", "redirect", "RC-3 (d) redirection read-back v2_common.PLAN_PATH", False),
            ("r3_entry_a1.py", "redirect", "RC-3 (d) redirection read-back a1_common.PROTOCOL_VERSION", False),
            ("r3_entry_v2.py", "se3_attr", "SE-3 read-back: v2_driver.solve is not the r3 re-solve wrapper", False),
            ("r3_entry_a1.py", "se3_attr", "SE-3 read-back: v2_driver.solve is not the r3 re-solve wrapper", False),
            ("r3_entry_v2.py", "se3_orig", "SE-3 read-back: the wrapper's recorded original is not the frozen v2_driver.solve", False),
            ("r3_entry_a1.py", "se3_orig", "SE-3 read-back: the wrapper's recorded original is not the frozen v2_driver.solve", False),
            ("r3_entry_a1.py", "hr3_attr", "HR-3 read-back: a1_health.run_system is not the r3 health wrapper", False),
            ("r3_entry_a1.py", "hr3_orig", "HR-3 read-back: the health wrapper's recorded original is not the frozen a1_health.run_system", False),
            ("r3_entry_a1.py", "hr3_H", "HR-3 read-back: a1_driver.H is not the a1_health module object", False),
            ("r3_entry_v2.py", "v2_with_a1_health", "HR-3 read-back: a module named a1_health is imported in the v2 entry", False),
            ("r3_entry_v2.py", "va7_redirect", "refusing to write a forbidden task id into pari-stack.json", True)):
        rd = os.path.join(out, "entry", "%s_%s" % (entry.replace(".py", ""), mode))
        if os.path.exists(rd):
            shutil.rmtree(rd)
        os.makedirs(rd)
        args = ["fixture", "--p", "4111"] if "v2" in entry else ["controls-a1", "--p", "1073741831"]
        env = dict(os.environ, GFPN_RUN_DIR=rd, PYTHONDONTWRITEBYTECODE="1", R3_DV6_MODE=mode, R3_DV6_ENTRY=os.path.join(HERE, entry))
        pr = subprocess.run([sys.executable, "-B", shim] + args, env=env, capture_output=True, text=True)
        files = sorted(os.listdir(rd))
        ps = json.load(open(os.path.join(rd, "pari-stack.json"))) if "pari-stack.json" in files else None
        if nothing:
            # VA-7 (a) in the entry: check_redirections flags the value and the pari-stack.json guard refuses to record
            # it; the entry stops before any command and writes NOTHING (exit status of the uncaught RuntimeError).
            ok = pr.returncode != 0 and expect in pr.stderr and files == []
        else:
            ok = (pr.returncode == 2 and expect in pr.stderr and files == ["pari-stack.json"] and ps and ps["status"] == "refused_before_any_command")
        entries.append({"entry": entry, "mode": mode, "argv": args, "rc": pr.returncode, "expected": expect, "stderr": pr.stderr.splitlines()[-6:],
                        "files_in_run_dir": files, "pari_stack_status": ps and ps["status"], "refusal_reasons": ps and ps["refusal_reasons"],
                        "start_readback": ps and ps["pari_stack"].get("start_readback"), "pass": ok})
        print("  entry %-16s %-17s rc=%s files=%s %s" % (entry, mode, pr.returncode, files, "PASS" if ok else "FAIL"))
    ok = all(r["pass"] for r in results) and all(e["pass"] for e in entries) and rc0 == 0 and sweep_ok
    rep = {"baseline": baseline, "wrapper_cases": results, "r2_exhaustive_sweep": sweep, "entry_cases": entries,
           "n_wrapper_cases": len(results), "n_entry_cases": len(entries), "pass": ok}
    dump(os.path.join(out, "dv6.json"), rep)
    print("DV-6: %d wrapper cases, %d entry cases: %s" % (len(results), len(entries), "PASS" if ok else "FAIL"))
    return 0 if ok else 1


ENTRY_SHIM = r'''
# DV-6 development shim (never delivered): runs a delivered entry point with ONE simulated fault.
#   pari:     the configuring call does not reach PARI (configure() skips allocatemem) -> the RC-2 (a) start read-back
#             through fresh cypari2.Pari() handles must refuse;
#   redirect: an import-time hook re-redirects a module constant after the driver module is imported -> the RC-3 (d)
#             read-back must refuse;
#   se3_attr / hr3_attr: after install, the module attribute is rebound to the frozen function -> the read-back refuses;
#   se3_orig / hr3_orig: the wrapper's recorded original is replaced by a non-frozen function -> the read-back refuses;
#   hr3_H: after install, a1_driver.H is rebound to another module object -> the HR-3 read-back refuses;
#   v2_with_a1_health: a1_health is imported into the v2 entry process after v2_driver -> the HR-3 read-back refuses;
#   va7_redirect: the r3 run-card constant the v2 entry redirects v2_common.TASK_ID to is replaced by a forbidden id ->
#             check_redirections flags it and the pari-stack.json guard refuses to record it (nothing written).
import os, sys, runpy, types, importlib.abc, importlib.util
sys.dont_write_bytecode = True
sys.path.insert(0, %(here)r)
import r3_common as R
import r3_resolve as RS
mode, entry = os.environ["R3_DV6_MODE"], os.environ["R3_DV6_ENTRY"]
if mode == "se3_attr":
    _inst = RS.install
    def install(mod, rd):
        rec = _inst(mod, rd)
        mod.solve = RS.solve.__r3_original__
        return rec
    RS.install = install
elif mode == "se3_orig":
    _inst = RS.install
    def install(mod, rd):
        rec = _inst(mod, rd)
        def solve(*a, **k):
            return RS._STATE["original"](*a, **k)
        RS.solve.__r3_original__ = solve
        return rec
    RS.install = install
elif mode == "hr3_attr":
    _insth = RS.install_health
    def install_health(mod, rd):
        rec = _insth(mod, rd)
        mod.run_system = RS.run_system.__r3_original__
        return rec
    RS.install_health = install_health
elif mode == "hr3_orig":
    _insth = RS.install_health
    def install_health(mod, rd):
        rec = _insth(mod, rd)
        def run_system(*a, **k):
            return RS._STATE["health_original"](*a, **k)
        RS.run_system.__r3_original__ = run_system
        return rec
    RS.install_health = install_health
elif mode == "hr3_H":
    _insth = RS.install_health
    def install_health(mod, rd):
        rec = _insth(mod, rd)
        sys.modules["a1_driver"].H = types.ModuleType("a1_health_stand_in")
        return rec
    RS.install_health = install_health
elif mode == "va7_redirect":
    R.TASK_RUNS_V2 = R.FORBIDDEN_TASK_IDS[4]
elif mode == "pari":
    def configure(self):
        self.rec["configured_before_first_v2_or_a1_import"] = True
        self.rec["dv6_simulated_fault"] = "allocatemem not called"
        import cypari2
        cypari2.Pari()
        return self.rec
    R.PariStack.configure = configure
else:
    class Hook(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name != ("a1_driver" if entry.endswith("r3_entry_a1.py") else "v2_driver"):
                return None
            sys.meta_path.remove(self)
            spec = importlib.util.find_spec(name)
            sys.meta_path.insert(0, self)
            orig = spec.loader.exec_module
            def exec_module(module, _o=orig, _n=name):
                _o(module)
                if mode == "v2_with_a1_health":
                    sys.path.insert(0, R.A1_DIR)
                    import a1_health
                elif _n == "v2_driver":
                    sys.modules["v2_common"].PLAN_PATH = os.path.join(R.EXP_DIR, "trial-plan-v2.json")
                else:
                    sys.modules["a1_common"].PROTOCOL_VERSION = "2-a1"
            spec.loader.exec_module = exec_module
            return spec
    sys.meta_path.insert(0, Hook())
sys.argv = [entry] + sys.argv[1:]
runpy.run_path(entry, run_name="__main__")
'''
