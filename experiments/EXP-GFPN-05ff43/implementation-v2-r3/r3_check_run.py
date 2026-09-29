#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r3 / 2-a1-r3 -- the r3 COMPLETION-GATE CHECKER (paristack PS-5 checker re-pointed;
RC-3 (e); solverevent SE-4, SE-6 as incorporated; DEC-20260924-15a77a SC-4, SC-11; healthresolve HR-8; launchcover
CG-3; consumercover CC-4; DEC-20260924-e52eec VA-6, VA-7; card R3S-8). Started from implementation-v2-r2/r2_check_run.py.

usage: python3 -B r3_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID> [--accounting-json OUT]
       python3 -B r3_check_run.py reg1 --candidate RUN_DIR [...]      (the REG-1 comparator, = r3_reg1.py)

1. Runs the frozen checks UNCHANGED in a SEPARATE PROCESS (RC-3 (e)): v2_check_run.main on a repaired v2 package with
   v2_common.PLAN_PATH -> trial-plan-v2-r3.json; a1_check_run.main on a repaired addendum package with the a1_common
   constants set as r3_entry_a1.py sets them BEFORE a1_check_run is imported. This process imports neither checker.
2. Adds the r3 checks: protocol label; amendment / addendum blocks; the repair block naming the seven repair
   amendments with their sha256 and standing; run card; derived_from; the phase-A commits (0fa03f and 4ff597 literal,
   f1fb0e recorded); clean flags for the three implementation trees; resources.pari_stack (P-A read-backs; the RC-3
   redirections, the SE-3 replacement and the HR-3 read-back as required); the SE-6 PYTHONHASHSEED read-back "0" from
   the driver process; the solver-events checks of VA-6 (a), (b) (whole-file sha256 against the manifest's recorded
   sha256 = V-7; exists / parses, top-level consistency flag, S-1 and S-2 per-site counts = epsilon); the callgrind-site
   counts are NOT read here (VA-6 (c)); gate.regression_REG-1 recorded PASS with the d-parsed branch and the plan's
   exclusion-list sha256 from G2 on; the forbidden-task-id requirement as VA-7 (b) states it (task-id-bearing keys by
   constant key; a byte sweep of command.txt, stdout.log, stderr.log, environment.json and pari-stack.json only);
   watchdogs recorded equal; the inference block.
3. SC-4 ACCOUNTING at both wrapped sites (VA-3): the SC-3 quantities (r3_accounting) for the retained <tag>.ms.out of
   every RECORDED attempt the frozen classifier called ok -- S-1 from raw-result.json's solve records, S-2 from the
   health report health/health-<p>.json. A violation is PRINTED VERBATIM and routed to SJ-5; it triggers nothing, is
   never evidence about D, and does not change this checker's exit status. Nothing is written into the run directory.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_common as R                                    # noqa: E402

FROZEN_LAUNCHER = [sys.executable, "-B", os.path.abspath(__file__)]   # redirected only in development checks
# DV-1: driver commands whose code path reaches an IN-PROCESS PARI call (v2_common.curve_order_pari).
IN_PROCESS_PARI_COMMANDS = {"v2r3": {"fixture", "controls", "fixture4"}, "a1r3": set()}
SE3_KEY = "v2_driver.solve (SE-3 replacement)"
HR3_KEY_A1 = "a1_health.run_system (HR-3 replacement)"
HR3_KEY_V2 = "a1_health (HR-3: not imported in the v2 entry)"
# VA-7 (b): the task-id-bearing keys, tested by CONSTANT key, and the files byte-swept (none carries a site value).
TASK_ID_KEYS = ("task_id", "run_card", "written_by_task", "archived_by")
SWEPT_FILES = ("command.txt", "stdout.log", "stderr.log", "environment.json", "pari-stack.json")
# the per-site SC-11 (b) counts compared between the manifest block and solver-events.json (epsilon; VA-6 (b))
SITE_COUNT_KEYS = ("ssf_attempts_by_clause", "re_solves", "calls_still_ssf_after_last_attempt", "resolve_cap_reached")


def frozen_v2(rd):
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    C.PLAN_PATH = R.PLAN_V2_R3
    import v2_check_run as K
    if C.PLAN_PATH != R.PLAN_V2_R3:
        print("REFUSING: v2_common.PLAN_PATH read-back differs")
        return 2
    return K.main(rd)


def frozen_a1(rd):
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC
    AC.PLAN_A1_PATH = R.PLAN_A1_R3
    AC.V2_PLAN_PATH = R.PLAN_V2_R3
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R3_PHASE_B
    AC.V2_GATE_PACKAGES = tuple(R.load_json(R.PLAN_V2_R3)["gate"]["blocking_packages"])
    AC.TASK_ID_RUNS = R.TASK_RUNS_A1
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R3
    import a1_check_run as K                             # redirect_v2() at import: v2_common.PLAN_PATH -> PLAN_A1_R3
    import v2_common as C
    C.TASK_ID = R.TASK_RUNS_A1
    if C.PLAN_PATH != R.PLAN_A1_R3 or AC.PROTOCOL_VERSION != R.PROTOCOL_A1_R3 or AC.TASK_ID_RUNS != R.TASK_RUNS_A1:
        print("REFUSING: redirection read-back differs")
        return 2
    return K.main(rd)


def which_plan(rid):
    for key, path in (("v2r3", R.PLAN_V2_R3), ("a1r3", R.PLAN_A1_R3)):
        plan = R.load_json(path)
        if any(p["run_id"] == rid for p in plan["packages"]):
            return key, plan
    return None, None


# ----------------------------------------------------------------------------- SC-4 accounting (both sites; report only)
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


def _acc_row(ACC, site, tag, file_dir, recorded_outcome, recorded_D, retained_flag):
    out = os.path.join(file_dir, tag + ".ms.out")
    row = {"site": site, "tag": tag, "recorded_outcome": recorded_outcome, "recorded_D": recorded_D}
    if not os.path.exists(out):
        row["status"] = "not retained (v2_driver._retain: > 50 MiB or absent)" if retained_flag is False else "absent"
        return row
    row.update(ACC.accounting(out, ms_path=os.path.join(file_dir, tag + ".ms"), log_path=os.path.join(file_dir, tag + ".ms.log")))
    return row


def health_records(rd):
    """The recorded S-2 results as the frozen a1_health.run wrote them (health/health-<p>.json): the results the HR-3
    wrapper RETURNED (alpha)."""
    hd = os.path.join(rd, "health")
    out = []
    if not os.path.isdir(hd):
        return out
    for f in sorted(os.listdir(hd)):
        if f.startswith("health-") and f.endswith(".json"):
            rep = json.load(open(os.path.join(hd, f)))
            for e in rep.get("systems") or []:
                for k in ("first", "reinvocation", "retry_seed2", "retry_seed2_reinvocation"):
                    if k in e:
                        out.append(e[k])
    return out


def sc4_accounting(rd):
    """SC-4 (re-pointed to both sites by VA-3): SC-3 quantities for every recorded ok attempt with a retained output.
    Recorded, never acted on."""
    import r3_accounting as ACC
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    rows = []
    for o in find_solver_records(raw):
        argv = o["solver"]["argv"]
        if "-g" in argv or o.get("outcome") != "ok":
            continue
        inp = argv[argv.index("-f") + 1]
        tag = os.path.basename(inp)[:-len(".ms")]
        rows.append(_acc_row(ACC, R.SITE_S1, tag, os.path.join(rd, "solver"), o.get("outcome"), o.get("D"), o.get("output_retained")))
    for h in health_records(rd):
        if h.get("v2_outcome_class") != "ok":
            continue
        rows.append(_acc_row(ACC, R.SITE_S2, h.get("tag"), os.path.join(rd, "health"), h.get("v2_outcome_class"),
                             h.get("dimension_of_quotient_printed"), None))
    viol = [r for r in rows if r.get("applicable") and not r.get("invariant_holds")]
    return {"rows": rows, "n_ok_recorded_with_output": sum(1 for r in rows if r.get("applicable")),
            "n_by_site": {s: sum(1 for r in rows if r.get("applicable") and r["site"] == s) for s in (R.SITE_S1, R.SITE_S2)},
            "violations": viol, "rule": "SC-4: recorded, never acted on; a violation is routed to SJ-5 and is never evidence about D"}


# ----------------------------------------------------------------------------- VA-6 (a), (b): solver-events.json checks
def events_file_integrity(rd, sev, errs):
    """VA-6 (a): the whole-file sha256 of solver-events.json against the sha256 the manifest's solver_events block
    records for the SAME file (V-7; epsilon integrity reader)."""
    sp = os.path.join(rd, "solver-events.json")
    if os.path.exists(sp) and sev.get("sha256") != R.sha256_file(sp):
        errs.append("manifest solver_events sha256 disagrees with solver-events.json (V-7 integrity)")


def events_file_epsilon(rd, sev, errs):
    """VA-6 (b): solver-events.json exists and parses; its top-level consistency flag; the S-1 and S-2 per-site
    counters against the manifest block; K and spacing -- all by CONSTANT key (epsilon). The S-3 (callgrind-site)
    records and counts are never read here (VA-6 (c))."""
    sp = os.path.join(rd, "solver-events.json")
    if not os.path.exists(sp):
        errs.append("solver-events.json missing")
        return
    try:
        doc = json.load(open(sp))
    except Exception as e:                               # noqa: BLE001
        errs.append("solver-events.json does not parse: %r" % (e,))
        return
    if doc.get("consistency_violation"):
        errs.append("solver-events.json records an SE-2 (4) / HR-5 consistency violation")
    if (sev.get("K"), sev.get("spacing_s")) != (R.K, R.SPACING_S) or (doc.get("K"), doc.get("spacing_s")) != (R.K, R.SPACING_S):
        errs.append("solver_events K / spacing != %s / %s" % (R.K, R.SPACING_S))
    for site in (R.SITE_S1, R.SITE_S2):
        c = ((doc.get("sites") or {}).get(site) or {}).get("counters") or {}
        m = ((sev.get("sites") or {}).get(site) or {})
        for k in SITE_COUNT_KEYS:
            if m.get(k) != c.get(k):
                errs.append("manifest solver_events %s.%s disagrees with solver-events.json" % (site, k))
    if "watchdog_after_resolve" not in sev:
        errs.append("manifest solver_events.watchdog_after_resolve not recorded")


# ----------------------------------------------------------------------------- VA-7 (b): the forbidden-task-id requirement
def forbidden_id_keys(rd, plan, errs):
    """VA-7 (b): every task-id-bearing key the r3 layer and the frozen drivers write (task_id, run card,
    written_by_task, archived_by) of manifest.yaml, raw-result.json, pari-stack.json, solver-events.json and the plan,
    tested by CONSTANT key. A key a site record does not carry reads no site data."""
    import yaml
    docs = {}
    for f in ("manifest.yaml", "raw-result.json", "pari-stack.json", "solver-events.json"):
        p = os.path.join(rd, f)
        if not os.path.exists(p):
            continue
        try:
            d = yaml.safe_load(open(p)) if f.endswith(".yaml") else json.load(open(p))
        except Exception:                                # noqa: BLE001
            continue
        docs[f] = (d or {}).get("run", d) if f == "manifest.yaml" else d
    docs["plan"] = plan
    for f, d in docs.items():
        if not isinstance(d, dict):
            continue
        for k in TASK_ID_KEYS:
            v = d.get(k)
            if isinstance(v, str) and R.forbidden_ids_in_text(v):
                errs.append("forbidden task id in %s key %s" % (f, k))


def forbidden_id_sweep(rd, errs):
    """VA-7 (b): a byte sweep of ONLY the files that carry no site value: command.txt, stdout.log, stderr.log,
    environment.json and pari-stack.json. No other file of the package is swept (site-carrying bytes are swept by the
    snapshot archives, VA-7 (d), report only)."""
    for f in SWEPT_FILES:
        p = os.path.join(rd, f)
        if os.path.exists(p):
            b = open(p, "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    errs.append("forbidden task id %s present in %s" % (t, f))


# ----------------------------------------------------------------------------- the r3 checks
def manifest_protocol_checks(man, which, plan, rid, errs):
    """Labels, run card, repair / amendment / addendum blocks, derived_from, phase-A commits, clean flags, inference,
    watchdogs: manifest fields that carry no site value."""
    label, task = (R.PROTOCOL_V2_R3, R.TASK_RUNS_V2) if which == "v2r3" else (R.PROTOCOL_A1_R3, R.TASK_RUNS_A1)
    if man.get("protocol_version") != label:
        errs.append("manifest protocol_version != %s" % label)
    if man.get("task_id") != task or plan.get("task_id") != task:
        errs.append("manifest / plan task_id != %s" % task)
    rp = man.get("repair") or {}
    want = R.repair_amendments()
    for key in R.REPAIR_KEYS:
        b, w = rp.get(key) or {}, want[key]
        if (b.get("id"), b.get("sha256"), b.get("approval_decision"), b.get("standing")) != (w.get("id"), w.get("sha256"), w.get("approval_decision"), w.get("standing")):
            errs.append("repair.%s block id / sha256 / approval / standing wrong" % key)
    am = man.get("amendment") or {}
    if (am.get("id"), am.get("sha256"), am.get("approval_decision")) != (R.V2_AMENDMENT_ID, R.V2_AMENDMENT_SHA256, R.V2_APPROVAL):
        errs.append("v2 amendment block wrong")
    ad = man.get("addendum")
    if which == "a1r3" and (not ad or (ad.get("id"), ad.get("sha256"), ad.get("approval_decision")) != (R.A1_ADDENDUM_ID, R.A1_ADDENDUM_SHA256, R.A1_APPROVAL)):
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
    if which == "a1r3" and pac.get("TASK-20260923-4ff597") != R.PHASE_A_COMMIT_4FF597:
        errs.append("phase_a_commits TASK-20260923-4ff597 != %s" % R.PHASE_A_COMMIT_4FF597)
    if not (pac.get("sources") or {}):
        errs.append("phase_a_commits sources not recorded")
    for k in ("implementation_v2_clean", "implementation_v2_a1_clean", "implementation_v2_r3_clean"):
        if code.get(k) is not True:
            errs.append("%s not recorded true" % k)
    if (((man.get("resources") or {}).get("watchdogs_declared") or {}).get("equal_to_trial_plan_v2")) is not True:
        errs.append("watchdogs not recorded equal to trial-plan-v2.json's")
    inf = man.get("inference") or {}
    if inf.get("requested_policy") != "executor-implementation" or inf.get("resolved_model_id") is not None \
            or inf.get("fallback_used") is not False or inf.get("bedrock_used") is not False:
        errs.append("inference block not as required")


def pari_stack_checks(man, which, errs, notes):
    """resources.pari_stack (a copy of pari-stack.json, which carries no site value): RC-2 read-backs, RC-3
    redirections, the SE-3 and HR-3 read-backs, the SE-6 hash-seed read-back and cypari2 versions."""
    res = man.get("resources") or {}
    ps = res.get("pari_stack") or {}
    stack = ps.get("pari_stack") or {}
    if ps.get("status") in (None, "refused_before_any_command") or str(ps.get("status", "")).startswith("absent"):
        errs.append("pari_stack status %s" % ps.get("status"))
    red = ps.get("redirections") or {}
    for key, v in red.items():
        if v.get("equal") is not True:
            errs.append("RC-3 / SE-3 / HR-3 read-back %s not as required" % key)
    if not red:
        errs.append("RC-3 redirection read-back not recorded")
    se3 = red.get(SE3_KEY) or {}
    if not (se3.get("v2_driver.solve_is_r3_wrapper") is True and se3.get("wrapper_original_is_frozen_v2_driver_solve") is True):
        errs.append("SE-3 replacement read-back not recorded as wrapper-with-frozen-original")
    if which == "a1r3":
        hr3 = red.get(HR3_KEY_A1) or {}
        if not (hr3.get("a1_health.run_system_is_r3_wrapper") is True and hr3.get("wrapper_original_is_frozen_a1_health_run_system") is True
                and hr3.get("a1_driver.H_is_a1_health_module") is True):
            errs.append("HR-3 replacement read-back not recorded as wrapper-with-frozen-original and a1_driver.H the module")
    else:
        hr3 = red.get(HR3_KEY_V2) or {}
        if hr3.get("a1_health_imported") is not False:
            errs.append("HR-3 read-back of the v2 entry (no a1_health imported) not recorded")
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


def reg1_recorded_check(man, plan, rid, errs):
    """gate.regression_REG-1 recorded PASS, d-parsed, with the plan's exclusion-list sha256, from G2 on (V-2; CG-4)."""
    gate_ids = R.load_json(R.PLAN_V2_R3)["gate"]["blocking_packages"]
    if rid != gate_ids[0]:
        rg = (man.get("gate") or {}).get("regression_REG-1") or {}
        if rg.get("verdict") != "PASS":
            errs.append("gate.regression_REG-1 not recorded PASS: %s" % rg.get("verdict"))
        if rg.get("d_branch") != R.REG1_D_BRANCH:
            errs.append("gate.regression_REG-1 d_branch %s != %s" % (rg.get("d_branch"), R.REG1_D_BRANCH))
        if rg.get("exclusion_list_sha256") != plan["gate"]["regression"]["exclusion_list_sha256"]:
            errs.append("gate.regression_REG-1 exclusion-list sha256 differs from the plan's")


def status_agreement(rd, man, errs):
    """The manifest status agrees with raw-result.json's run_status (alpha: the result recorded from the wrappers'
    returns)."""
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man.get("status") != raw.get("run_status") and not (raw.get("run_status") == "completed_valid" and man.get("status") == "failed"):
        errs.append("manifest status disagrees with raw-result")


def r3_checks(rd, which, plan):
    """The r3 checks. This function reads no site value itself: it calls the single-class checks above and collects
    their findings (DEC-20260924-e52eec VA-8 (b) model)."""
    import yaml
    errs, notes = [], []
    rid = os.path.basename(rd.rstrip("/"))
    man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    manifest_protocol_checks(man, which, plan, rid, errs)
    pari_stack_checks(man, which, errs, notes)
    sev = man.get("solver_events") or {}
    events_file_epsilon(rd, sev, errs)                   # VA-6 (b)
    events_file_integrity(rd, sev, errs)                 # VA-6 (a)
    reg1_recorded_check(man, plan, rid, errs)            # V-2
    forbidden_id_keys(rd, plan, errs)                    # VA-7 (b)
    forbidden_id_sweep(rd, errs)                         # VA-7 (b)
    status_agreement(rd, man, errs)                      # alpha
    return errs, notes


def main(rd, accounting_json=None):
    rd = os.path.abspath(rd)
    rid = os.path.basename(rd.rstrip("/"))
    which, plan = which_plan(rid)
    if which is None:
        print("%s: FAIL; run id not reserved in either r3 plan" % rd)
        return 1
    mode = "frozen-v2" if which == "v2r3" else "frozen-a1"
    pr = subprocess.run(FROZEN_LAUNCHER + [mode, rd], capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    print("frozen checker (%s, separate process, unchanged): %s" % ("v2_check_run" if which == "v2r3" else "a1_check_run",
                                                                     "PASS" if pr.returncode == 0 else "FAIL rc=%s" % pr.returncode))
    print(pr.stdout.rstrip())
    if pr.stderr.strip():
        print(pr.stderr.rstrip())
    errs, notes = r3_checks(rd, which, plan)
    print("%s: r3 checks %s; %s" % (rd, "PASS" if not errs else "FAIL", notes))
    for e in errs:
        print("  -", e)
    try:
        acc = sc4_accounting(rd)
    except Exception as e:                               # noqa: BLE001
        acc = {"error": repr(e), "rows": [], "violations": []}
    print("SC-4 accounting (recorded, never acted on): %s ok recorded attempts with a retained output %s; violations %d"
          % (acc.get("n_ok_recorded_with_output"), acc.get("n_by_site"), len(acc.get("violations") or [])))
    for r in acc.get("rows") or []:
        if r.get("applicable"):
            print("  %-22s %-40s n_roots %s n_den_zero %s n_arity %s n_points %s n_distinct %s invariant %s"
                  % (r["site"], r["tag"], r["n_roots"], r["n_den_zero"], r["n_arity"], r["n_points"], r["n_distinct"], r["invariant_holds"]))
        else:
            print("  %-22s %-40s %s" % (r["site"], r["tag"], r.get("status") or ("parse kind %s" % r.get("parse_kind"))))
    for v in acc.get("violations") or []:
        print("  SC-4 VIOLATION (recorded verbatim; routed to SJ-5; not a check failure): %s" % json.dumps(v, default=str))
    if accounting_json:
        with open(accounting_json, "w") as fh:
            json.dump(acc, fh, indent=1, default=str)
    return 1 if (errs or pr.returncode) else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "reg1":
        import r3_reg1
        sys.exit(r3_reg1.main(sys.argv[2:]))
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
