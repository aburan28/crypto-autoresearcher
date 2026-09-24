#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r2 / 2-a1-r2 -- the r2 COMPLETION-GATE CHECKER (paristack PS-5 checker re-pointed;
RC-3 (e); solverevent SE-4, SE-6 as incorporated; DEC-20260924-15a77a SC-4, SC-11). Started from
implementation-v2-r1/r1_check_run.py.

usage: python3 -B r2_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID> [--accounting-json OUT]
       python3 -B r2_check_run.py reg1 --candidate RUN_DIR [...]      (the REG-1 comparator, = r2_reg1.py)

1. Runs the frozen checks UNCHANGED in a SEPARATE PROCESS (RC-3 (e)): v2_check_run.main on a repaired v2 package with
   v2_common.PLAN_PATH -> trial-plan-v2-r2.json; a1_check_run.main on a repaired addendum package with the a1_common
   constants set as r2_entry_a1.py sets them BEFORE a1_check_run is imported (its line 30 calls redirect_v2 at
   import). This process imports neither checker, so no v2 check can be redirected by an a1 import.
2. Adds the r2 checks: protocol label; amendment / addendum blocks; the repair block naming paristack, seedresolve and
   solverevent with their sha256; run card; derived_from; the phase-A commits (0fa03f and 4ff597 literal, 689d2f
   recorded); clean flags for the three implementation trees; resources.pari_stack (P-A read-backs as in r1, the RC-3
   redirections and the SE-3 replacement read back as required); the SE-6 PYTHONHASHSEED read-back "0" from the
   driver process; the solver_events block (SC-11 (b)) present and equal to what run-root solver-events.json gives,
   the file parsing and recording no consistency violation; gate.regression_REG-1 recorded PASS with the d-parsed
   branch and the plan's exclusion-list sha256 from G2 on; no file of the package carries any of the four forbidden
   task ids; watchdogs recorded equal; the inference block.
3. SC-4 ACCOUNTING: the SC-3 quantities (r2_accounting) for the retained solver/<tag>.ms.out of every RECORDED attempt
   the frozen classifier called ok (raw-result.json records), tabulated per tag. A violation is PRINTED VERBATIM and
   routed to SJ-5; it triggers no re-solve, reclassification, exclusion or change, is never evidence about D, and does
   not change this checker's exit status. A tag whose .ms.out was not retained (> 50 MiB, v2_driver.py lines 224-228)
   is listed as such. Nothing is written into the run directory.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402

FROZEN_LAUNCHER = [sys.executable, "-B", os.path.abspath(__file__)]   # redirected only in development checks
# DV-1: driver commands whose code path reaches an IN-PROCESS PARI call (v2_common.curve_order_pari).
IN_PROCESS_PARI_COMMANDS = {"v2r2": {"fixture", "controls", "fixture4"}, "a1r2": set()}
SE3_KEY = "v2_driver.solve (SE-3 replacement)"


def frozen_v2(rd):
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    C.PLAN_PATH = R.PLAN_V2_R2
    import v2_check_run as K
    if C.PLAN_PATH != R.PLAN_V2_R2:
        print("REFUSING: v2_common.PLAN_PATH read-back differs")
        return 2
    return K.main(rd)


def frozen_a1(rd):
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC
    AC.PLAN_A1_PATH = R.PLAN_A1_R2
    AC.V2_PLAN_PATH = R.PLAN_V2_R2
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R2_PHASE_B
    AC.V2_GATE_PACKAGES = tuple(R.load_json(R.PLAN_V2_R2)["gate"]["blocking_packages"])
    AC.TASK_ID_RUNS = R.TASK_RUNS_A1
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R2
    import a1_check_run as K                             # redirect_v2() at import: v2_common.PLAN_PATH -> PLAN_A1_R2
    import v2_common as C
    C.TASK_ID = R.TASK_RUNS_A1
    if C.PLAN_PATH != R.PLAN_A1_R2 or AC.PROTOCOL_VERSION != R.PROTOCOL_A1_R2 or AC.TASK_ID_RUNS != R.TASK_RUNS_A1:
        print("REFUSING: redirection read-back differs")
        return 2
    return K.main(rd)


def which_plan(rid):
    for key, path in (("v2r2", R.PLAN_V2_R2), ("a1r2", R.PLAN_A1_R2)):
        plan = R.load_json(path)
        if any(p["run_id"] == rid for p in plan["packages"]):
            return key, plan
    return None, None


def find_solver_records(o):
    if isinstance(o, dict):
        s = o.get("solver")
        if isinstance(s, dict) and s.get("argv"):
            yield o
        for v in o.values():
            yield from find_solver_records(v)
    elif isinstance(o, list):
        for v in o:
            yield from find_solver_records(v)


def sc4_accounting(rd):
    """SC-4: SC-3 quantities for every recorded ok attempt with a retained .ms.out (never acted on)."""
    import r2_accounting as ACC
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    rows = []
    for o in find_solver_records(raw):
        argv = o["solver"]["argv"]
        if "-g" in argv or o.get("outcome") != "ok":
            continue
        inp = argv[argv.index("-f") + 1]
        tag = os.path.basename(inp)[:-len(".ms")]
        out = os.path.join(rd, "solver", tag + ".ms.out")
        row = {"tag": tag, "recorded_outcome": o.get("outcome"), "recorded_D": o.get("D")}
        if not os.path.exists(out):
            row["status"] = "not retained (v2_driver._retain: > 50 MiB or absent)" if o.get("output_retained") is False else "absent"
            rows.append(row)
            continue
        a = ACC.accounting(out, ms_path=os.path.join(rd, "solver", tag + ".ms"), log_path=os.path.join(rd, "solver", tag + ".ms.log"))
        row.update(a)
        rows.append(row)
    viol = [r for r in rows if r.get("applicable") and not r.get("invariant_holds")]
    return {"rows": rows, "n_ok_recorded_with_output": sum(1 for r in rows if r.get("applicable")),
            "violations": viol, "rule": "SC-4: recorded, never acted on; a violation is routed to SJ-5 and is never evidence about D"}


def r2_checks(rd, which, plan):
    import yaml
    errs, notes = [], []
    rid = os.path.basename(rd.rstrip("/"))
    man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    label, task = (R.PROTOCOL_V2_R2, R.TASK_RUNS_V2) if which == "v2r2" else (R.PROTOCOL_A1_R2, R.TASK_RUNS_A1)
    if man.get("protocol_version") != label:
        errs.append("manifest protocol_version != %s" % label)
    if man.get("task_id") != task or plan.get("task_id") != task:
        errs.append("manifest / plan task_id != %s" % task)
    rp = man.get("repair") or {}
    for key, want in (("paristack", (R.PARISTACK_ID, R.PARISTACK_SHA256, R.PARISTACK_APPROVAL)),
                      ("seedresolve", (R.SEEDRESOLVE_ID, R.SEEDRESOLVE_SHA256, R.SEEDRESOLVE_APPROVAL))):
        b = rp.get(key) or {}
        if (b.get("id"), b.get("sha256"), b.get("approval_decision")) != want:
            errs.append("repair.%s block id / sha256 / approval wrong" % key)
    sv = rp.get("solverevent") or {}
    if (sv.get("id"), sv.get("sha256"), sv.get("standing")) != (R.SOLVEREVENT_ID, R.SOLVEREVENT_SHA256, R.SOLVEREVENT_STANDING):
        errs.append("repair.solverevent block wrong")
    am = man.get("amendment") or {}
    if (am.get("id"), am.get("sha256"), am.get("approval_decision")) != (R.V2_AMENDMENT_ID, R.V2_AMENDMENT_SHA256, R.V2_APPROVAL):
        errs.append("v2 amendment block wrong")
    ad = man.get("addendum")
    if which == "a1r2" and (not ad or (ad.get("id"), ad.get("sha256"), ad.get("approval_decision")) != (R.A1_ADDENDUM_ID, R.A1_ADDENDUM_SHA256, R.A1_APPROVAL)):
        errs.append("v2-a1 addendum block wrong or missing")
    inv = {v: k for k, v in plan["id_map"].items()}
    if man.get("derived_from") != inv.get(rid):
        errs.append("derived_from %s != frozen id %s" % (man.get("derived_from"), inv.get(rid)))
    code = man.get("code") or {}
    pac = code.get("phase_a_commits") or {}
    if pac.get("TASK-20260923-0fa03f") != R.PHASE_A_COMMIT_0FA03F:
        errs.append("phase_a_commits TASK-20260923-0fa03f != %s" % R.PHASE_A_COMMIT_0FA03F)
    if not pac.get(R.ARCHIVE_TASK):
        errs.append("phase_a_commits %s not recorded" % R.ARCHIVE_TASK)
    if which == "a1r2" and pac.get("TASK-20260923-4ff597") != R.PHASE_A_COMMIT_4FF597:
        errs.append("phase_a_commits TASK-20260923-4ff597 != %s" % R.PHASE_A_COMMIT_4FF597)
    if not (pac.get("sources") or {}):
        errs.append("phase_a_commits sources not recorded")
    for k in ("implementation_v2_clean", "implementation_v2_a1_clean", "implementation_v2_r2_clean"):
        if code.get(k) is not True:
            errs.append("%s not recorded true" % k)
    res = man.get("resources") or {}
    ps = res.get("pari_stack") or {}
    stack = ps.get("pari_stack") or {}
    if ps.get("status") in (None, "refused_before_any_command") or str(ps.get("status", "")).startswith("absent"):
        errs.append("pari_stack status %s" % ps.get("status"))
    red = ps.get("redirections") or {}
    for key, v in red.items():
        if v.get("equal") is not True:
            errs.append("RC-3 / SE-3 read-back %s not as required" % key)
    if not red:
        errs.append("RC-3 redirection read-back not recorded")
    se3 = red.get(SE3_KEY) or {}
    if not (se3.get("v2_driver.solve_is_r2_wrapper") is True and se3.get("wrapper_original_is_frozen_v2_driver_solve") is True):
        errs.append("SE-3 replacement read-back not recorded as wrapper-with-frozen-original")
    st = stack.get("start_readback") or {}
    for h in ("fresh_handle_1", "fresh_handle_2"):
        r = st.get(h) or {}
        if r.get("parisize") != R.PARISIZE or r.get("parisizemax") != R.PARISIZEMAX:
            errs.append("RC-2 (a) start read-back %s %s" % (h, r))
    ex = stack.get("exit_readback") or {}
    if ex.get("parisizemax") != R.PARISIZEMAX:
        errs.append("RC-2 (b) exit parisizemax %s != %d" % (ex.get("parisizemax"), R.PARISIZEMAX))
    ok_size = ex.get("parisize") == R.PARISIZE if R.PARISIZE_EXIT_SEMANTICS == "requested" else (R.PARISIZE <= (ex.get("parisize") or 0) <= R.PARISIZEMAX)
    if not ok_size:
        errs.append("RC-2 (b) exit parisize %s (semantics %s)" % (ex.get("parisize"), R.PARISIZE_EXIT_SEMANTICS))
    if stack.get("configured_before_first_v2_or_a1_import") is not True:
        errs.append("RC-2 (c) configuration not made before the first v2 / v2-a1 import")
    if not (stack.get("versions") or {}).get("cypari2") or not ((man.get("environment") or {}).get("dependencies") or {}).get("cypari2"):
        errs.append("cypari2 version not recorded")
    if stack.get("branch") != R.PS1_BRANCH:
        errs.append("pari_stack branch %s != %s" % (stack.get("branch"), R.PS1_BRANCH))
    hs = (man.get("environment") or {}).get("PYTHONHASHSEED_driver_readback") or {}
    if hs.get("PYTHONHASHSEED_env") != R.DRIVER_PYTHONHASHSEED:
        errs.append("SE-6: the driver process read back PYTHONHASHSEED %r, not %r" % (hs.get("PYTHONHASHSEED_env"), R.DRIVER_PYTHONHASHSEED))
    cmd = (man.get("code") or {}).get("command", "").split()
    sub = next((c for c in cmd if c in IN_PROCESS_PARI_COMMANDS[which] or c in ("anchor-identity", "build", "cells", "aggregate",
                                                                                  "controls-a1", "aggregate-a1")), None)
    notes.append("command %s reaches in-process PARI per DV-1: %s" % (sub, sub in IN_PROCESS_PARI_COMMANDS[which]))
    # solver events (SE-2 (5); SC-11 (b))
    sev = man.get("solver_events") or {}
    sp = os.path.join(rd, "solver-events.json")
    if not os.path.exists(sp):
        errs.append("solver-events.json missing")
    else:
        try:
            doc = json.load(open(sp))
            if doc.get("consistency_violation"):
                errs.append("solver-events.json records an SE-2 (4) consistency violation")
            c = doc.get("counters") or {}
            if (sev.get("K"), sev.get("spacing_s")) != (R.K, R.SPACING_S):
                errs.append("manifest solver_events K / spacing != %s / %s" % (R.K, R.SPACING_S))
            for k in ("ssf_attempts_by_clause", "re_solves", "solves_still_ssf_after_last_attempt", "resolve_cap_reached"):
                if sev.get(k) != c.get(k):
                    errs.append("manifest solver_events.%s disagrees with solver-events.json" % k)
            if sev.get("sha256") != R.sha256_file(sp):
                errs.append("manifest solver_events sha256 disagrees with solver-events.json")
            if "watchdog_after_resolve" not in sev:
                errs.append("manifest solver_events.watchdog_after_resolve not recorded")
        except Exception as e:                           # noqa: BLE001
            errs.append("solver-events.json does not parse: %r" % (e,))
    gate_ids = R.load_json(R.PLAN_V2_R2)["gate"]["blocking_packages"]
    if rid != gate_ids[0]:
        rg = (man.get("gate") or {}).get("regression_REG-1") or {}
        if rg.get("verdict") != "PASS":
            errs.append("gate.regression_REG-1 not recorded PASS: %s" % rg.get("verdict"))
        if rg.get("d_branch") != R.REG1_D_BRANCH:
            errs.append("gate.regression_REG-1 d_branch %s != %s" % (rg.get("d_branch"), R.REG1_D_BRANCH))
        if rg.get("exclusion_list_sha256") != plan["gate"]["regression"]["exclusion_list_sha256"]:
            errs.append("gate.regression_REG-1 exclusion-list sha256 differs from the plan's")
    for root, _d, files in os.walk(rd):
        for f in files:
            b = open(os.path.join(root, f), "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    errs.append("forbidden task id %s present in %s" % (t, os.path.relpath(os.path.join(root, f), rd)))
    if ((res.get("watchdogs_declared") or {}).get("equal_to_trial_plan_v2")) is not True:
        errs.append("watchdogs not recorded equal to trial-plan-v2.json's")
    inf = man.get("inference") or {}
    if inf.get("requested_policy") != "executor-implementation" or inf.get("resolved_model_id") is not None \
            or inf.get("fallback_used") is not False or inf.get("bedrock_used") is not False:
        errs.append("inference block not as required")
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man.get("status") != raw.get("run_status") and not (raw.get("run_status") == "completed_valid" and man.get("status") == "failed"):
        errs.append("manifest status disagrees with raw-result")
    return errs, notes


def main(rd, accounting_json=None):
    rd = os.path.abspath(rd)
    rid = os.path.basename(rd.rstrip("/"))
    which, plan = which_plan(rid)
    if which is None:
        print("%s: FAIL; run id not reserved in either r2 plan" % rd)
        return 1
    mode = "frozen-v2" if which == "v2r2" else "frozen-a1"
    pr = subprocess.run(FROZEN_LAUNCHER + [mode, rd], capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    print("frozen checker (%s, separate process, unchanged): %s" % ("v2_check_run" if which == "v2r2" else "a1_check_run",
                                                                     "PASS" if pr.returncode == 0 else "FAIL rc=%s" % pr.returncode))
    print(pr.stdout.rstrip())
    if pr.stderr.strip():
        print(pr.stderr.rstrip())
    errs, notes = r2_checks(rd, which, plan)
    print("%s: r2 checks %s; %s" % (rd, "PASS" if not errs else "FAIL", notes))
    for e in errs:
        print("  -", e)
    try:
        acc = sc4_accounting(rd)
    except Exception as e:                               # noqa: BLE001
        acc = {"error": repr(e), "rows": [], "violations": []}
    print("SC-4 accounting (recorded, never acted on): %s ok recorded attempts with a retained output; violations %d"
          % (acc.get("n_ok_recorded_with_output"), len(acc.get("violations") or [])))
    for r in acc.get("rows") or []:
        if r.get("applicable"):
            print("  %-40s n_roots %s n_den_zero %s n_arity %s n_points %s n_distinct %s invariant %s"
                  % (r["tag"], r["n_roots"], r["n_den_zero"], r["n_arity"], r["n_points"], r["n_distinct"], r["invariant_holds"]))
        else:
            print("  %-40s %s" % (r["tag"], r.get("status") or ("parse kind %s" % r.get("parse_kind"))))
    for v in acc.get("violations") or []:
        print("  SC-4 VIOLATION (recorded verbatim; routed to SJ-5; not a check failure): %s" % json.dumps(v, default=str))
    if accounting_json:
        with open(accounting_json, "w") as fh:
            json.dump(acc, fh, indent=1, default=str)
    return 1 if (errs or pr.returncode) else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "reg1":
        import r2_reg1
        sys.exit(r2_reg1.main(sys.argv[2:]))
    if len(sys.argv) == 3 and sys.argv[1] == "frozen-v2":
        sys.exit(frozen_v2(sys.argv[2]))
    if len(sys.argv) == 3 and sys.argv[1] == "frozen-a1":
        sys.exit(frozen_a1(sys.argv[2]))
    aj = None
    args = sys.argv[1:]
    if "--accounting-json" in args:
        i = args.index("--accounting-json")
        aj = args[i + 1]
        args = args[:i] + args[i + 2:]
    sys.exit(main(args[0], aj))
