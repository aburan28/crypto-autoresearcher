#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r4 / 2-a1-r4 -- the r4 COMPLETION-GATE CHECKER and the r4 VERDICT (paristack PS-5 checker
re-pointed; RC-3 (e); solverevent SE-4, SE-6; SC-4 with readbackcover RB-3; healthresolve HR-8; launchcover CG-3;
consumercover CC-4; DEC-20260924-e52eec VA-6, VA-7 re-pointed; readbackfull RL-3, RL-5; readbackclose RK-3 (b);
failclosed RF-0, RF-1 (b), RF-2, RF-3, RF-5; childend RG-1 (d), RG-2; gapattr RH-1, RH-2; attcount RI-1; launchkind
RJ-1..RJ-4; DEC-20260924-daf670 LKA-8..LKA-10; card R4S-4, R4S-6). Started from implementation-v2-r3/r3_check_run.py.

usage: python3 -B r4_check_run.py experiments/EXP-GFPN-05ff43/runs/<RUN-ID> [--accounting-json OUT]
       python3 -B r4_check_run.py reg1 --candidate RUN_DIR [...]      (the REG-1 comparator, = r4_reg1.py)

1. Runs the frozen checks UNCHANGED in a SEPARATE PROCESS (RC-3 (e)): v2_check_run.main on a repaired v2 package with
   v2_common.PLAN_PATH -> trial-plan-v2-r4.json; a1_check_run.main on a repaired addendum package with the a1_common
   constants set as r4_entry_a1.py sets them BEFORE a1_check_run is imported. This module imports neither checker.
2. The r4 checks: the r3 checks re-pointed (protocol label; amendment / addendum blocks; the repair block naming the
   fifteen repair amendments; run card; derived_from; the phase-A commits; clean flags; resources.pari_stack with the
   RC-3, SE-3, HR-3 and RL-5 read-backs; the SE-6 PYTHONHASHSEED read-back "0"; VA-6 (a), (b); gate.regression_REG-1
   recorded PASS from G2 on; VA-7 (b) with the eight R-13 ids; status agreement) AND the r4 verdict layer:
   RL-3 RECORDER GAPS as launchkind's reading_rule words them (r4_gaps.recorder_gaps); every launch record one of the
   positive classes (A), (B), (C) of RF-3 (a) read with RG-1 (d); raw_result_writer "driver" (RF-0 (b)); no
   recorder-foreign file (RF-1 (b)); no `undetermined` value (RF-0 (c)); X-13 (RF-5).
3. THE r4 VERDICT (RK-3 (b) with RF-2 and RF-3): PASS iff the frozen checker exits 0 and every r4 check passes.
   PASS_ZL iff RK-3 (b) (i)-(v) and RF-2 (vi)-(viii) all hold. Otherwise FAIL, with its RF-3 (b) stop classes (an
   infrastructure launch; a wrapper-recorded outcome; an `undetermined` value; a recorder-foreign file; a recorder gap;
   a cap read-back mismatch (RH-2); another checker item, quoted) and the RG-2 / RH-2 outcome labels. A FAIL is never
   evidence. Exit status 0 for PASS and PASS_ZL, 1 for FAIL.
4. SC-4 ACCOUNTING at both wrapped sites with RB-3 (attempt records of solver-events.json, raw-result.json solve
   records and health reports, de-duplicated by (site, tag)): recorded, never acted on; it does not change the exit
   status. Nothing is written into the run directory.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_common as R                                    # noqa: E402
import r4_gaps as GAPS                                   # noqa: E402

FROZEN_LAUNCHER = [sys.executable, "-B", os.path.abspath(__file__)]   # redirected only in development checks
# DV-1: driver commands whose code path reaches an IN-PROCESS PARI call (v2_common.curve_order_pari).
IN_PROCESS_PARI_COMMANDS = {"v2r4": {"fixture", "controls", "fixture4"}, "a1r4": set()}
SE3_KEY = "v2_driver.solve (SE-3 replacement)"
HR3_KEY_A1 = "a1_health.run_system (HR-3 replacement)"
HR3_KEY_V2 = "a1_health (HR-3: not imported in the v2 entry)"
RL1_KEY = "v2_solver.run_child (RL-1 launch recorder; RL-5 install read-back)"
# VA-7 (b): the task-id-bearing keys, tested by CONSTANT key, and the files byte-swept (none carries a site value).
TASK_ID_KEYS = ("task_id", "run_card", "written_by_task", "archived_by")
SWEPT_FILES = ("command.txt", "stdout.log", "stderr.log", "environment.json", "pari-stack.json")
# the per-site SC-11 (b) counts compared between the manifest block and solver-events.json (epsilon; VA-6 (b))
SITE_COUNT_KEYS = ("ssf_attempts_by_clause", "re_solves", "calls_still_ssf_after_last_attempt", "resolve_cap_reached")
ZL_ITEM = "no child RLIMIT_AS read-back recorded"
CAP_MISMATCH_PREFIX = "child RLIMIT_AS read-back "
ZL_KINDS = ("cells", "fixture4")
UNDET = "undetermined"


def frozen_v2(rd):
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C
    C.PLAN_PATH = R.PLAN_V2_R4
    import v2_check_run as K
    if C.PLAN_PATH != R.PLAN_V2_R4:
        print("REFUSING: v2_common.PLAN_PATH read-back differs")
        return 2
    return K.main(rd)


def frozen_a1(rd):
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC
    AC.PLAN_A1_PATH = R.PLAN_A1_R4
    AC.V2_PLAN_PATH = R.PLAN_V2_R4
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R4_PHASE_B
    AC.V2_GATE_PACKAGES = tuple(R.load_json(R.PLAN_V2_R4)["gate"]["blocking_packages"])
    AC.TASK_ID_RUNS = R.TASK_RUNS_A1
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R4
    import a1_check_run as K                             # redirect_v2() at import: v2_common.PLAN_PATH -> PLAN_A1_R4
    import v2_common as C
    C.TASK_ID = R.TASK_RUNS_A1
    if C.PLAN_PATH != R.PLAN_A1_R4 or AC.PROTOCOL_VERSION != R.PROTOCOL_A1_R4 or AC.TASK_ID_RUNS != R.TASK_RUNS_A1:
        print("REFUSING: redirection read-back differs")
        return 2
    return K.main(rd)


def which_plan(rid):
    for key, path in (("v2r4", R.PLAN_V2_R4), ("a1r4", R.PLAN_A1_R4)):
        plan = R.load_json(path)
        if any(p["run_id"] == rid for p in plan["packages"]):
            return key, plan
    return None, None


# ----------------------------------------------------------------------------- SC-4 accounting with RB-3 (both sites; report only)
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


def _acc_row(ACC, site, tag, file_dir, recorded_outcome, recorded_D, retained_flag, source):
    out = os.path.join(file_dir, tag + ".ms.out")
    row = {"site": site, "tag": tag, "recorded_outcome": recorded_outcome, "recorded_D": recorded_D, "source": source}
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


def recorded_attempts(rd):
    """RB-3: the RECORDED attempt of every wrapped call (the last attempt record of each call_index) at S-1 and S-2,
    from the solver-events.json attempt records (RB-1 (a); epsilon read, E6)."""
    try:
        doc = json.load(open(os.path.join(rd, "solver-events.json")))
    except Exception:                                    # noqa: BLE001
        return {}
    out = {}
    for site in (R.SITE_S1, R.SITE_S2):
        last = {}
        for a in (((doc.get("sites") or {}).get(site) or {}).get("attempt_records") or []):
            last[a.get("call_index")] = a
        for a in last.values():
            out[(site, a.get("tag"))] = a
    return out


def sc4_accounting(rd):
    """SC-4 (re-pointed to both sites by VA-3) with RB-3: SC-3 quantities for every recorded ok attempt with a retained
    output, enumerated from the attempt records AND from raw-result.json solve records and health reports, de-duplicated
    by (site, tag). Recorded, never acted on."""
    import r4_accounting as ACC
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    src_raw = {}
    for o in find_solver_records(raw):
        argv = o["solver"]["argv"]
        if "-g" in argv:
            continue
        inp = argv[argv.index("-f") + 1]
        tag = os.path.basename(inp)[:-len(".ms")]
        src_raw[(R.SITE_S1, tag)] = {"outcome": o.get("outcome"), "D": o.get("D"), "retained": o.get("output_retained")}
    for h in health_records(rd):
        src_raw[(R.SITE_S2, h.get("tag"))] = {"outcome": h.get("v2_outcome_class"), "D": h.get("dimension_of_quotient_printed"), "retained": None}
    src_att = recorded_attempts(rd)
    rows, not_retained, coverage_gaps = [], [], []
    for key in sorted(set(src_raw) | set(src_att), key=lambda k: (k[0], str(k[1]))):
        site, tag = key
        a, r = src_att.get(key), src_raw.get(key)
        outcome = (a.get("rb1") or {}).get("outcome_class") if a else r.get("outcome")
        D = (a.get("D") if site == R.SITE_S1 else a.get("dimension_of_quotient_printed")) if a else r.get("D")
        source = "attempt record and %s" % ("raw-result" if site == R.SITE_S1 else "health report") if (a and r) else (
            "attempt record only" if a else "raw-result / health report only")
        if not (a and r):
            coverage_gaps.append({"site": site, "tag": tag, "in": source})
        if outcome != "ok":
            continue
        fdir = os.path.join(rd, "solver" if site == R.SITE_S1 else "health")
        row = _acc_row(ACC, site, tag, fdir, outcome, D, (r or {}).get("retained"), source)
        if row.get("status"):
            not_retained.append({"site": site, "tag": tag, "status": row["status"]})
        rows.append(row)
    viol = [r for r in rows if r.get("applicable") and not r.get("invariant_holds")]
    return {"rows": rows, "n_ok_recorded_with_output": sum(1 for r in rows if r.get("applicable")),
            "n_by_site": {s: sum(1 for r in rows if r.get("applicable") and r["site"] == s) for s in (R.SITE_S1, R.SITE_S2)},
            "recorded_attempts_without_retained_output": not_retained, "coverage_gaps_named": coverage_gaps,
            "violations": viol, "rule": "SC-4 with RB-3: recorded, never acted on; a violation is routed to SJ-5 and is never evidence about D"}


# ----------------------------------------------------------------------------- VA-6 (a), (b): solver-events.json checks
def events_file_integrity(rd, sev, errs):
    """VA-6 (a): the whole-file sha256 of solver-events.json against the sha256 the manifest's solver_events block
    records for the SAME file (V-7; epsilon integrity reader)."""
    sp = os.path.join(rd, "solver-events.json")
    if os.path.exists(sp) and sev.get("sha256") != R.sha256_file(sp):
        errs.append("manifest solver_events sha256 disagrees with solver-events.json (V-7 integrity)")


def events_file_epsilon(rd, sev, errs):
    """VA-6 (b): solver-events.json exists and parses; its top-level consistency flag; the S-1 and S-2 per-site
    counters against the manifest block; K and spacing; the launch_records key -- all by CONSTANT key (epsilon). The S-3
    (callgrind-site) records and counts are never read here (VA-6 (c))."""
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
        errs.append("solver-events.json records an SE-2 (4) / HR-5 consistency violation or a recording failure")
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
    if not isinstance(doc.get("launch_records"), list):
        errs.append("solver-events.json carries no launch_records list (RL-1 (c))")


# ----------------------------------------------------------------------------- VA-7 (b): the forbidden-task-id requirement
def forbidden_id_keys(rd, plan, errs):
    """VA-7 (b): every task-id-bearing key the r4 layer and the frozen drivers write (task_id, run card,
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
    environment.json and pari-stack.json."""
    for f in SWEPT_FILES:
        p = os.path.join(rd, f)
        if os.path.exists(p):
            b = open(p, "rb").read()
            for t in R.FORBIDDEN_TASK_IDS:
                if t.encode() in b:
                    errs.append("forbidden task id %s present in %s" % (t, f))


# ----------------------------------------------------------------------------- the carried checks (re-pointed)
def manifest_protocol_checks(man, which, plan, rid, errs):
    """Labels, run card, repair / amendment / addendum blocks, derived_from, phase-A commits, clean flags, inference,
    watchdogs: manifest fields that carry no site value."""
    label, task = (R.PROTOCOL_V2_R4, R.TASK_RUNS_V2) if which == "v2r4" else (R.PROTOCOL_A1_R4, R.TASK_RUNS_A1)
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
    if which == "a1r4" and (not ad or (ad.get("id"), ad.get("sha256"), ad.get("approval_decision")) != (R.A1_ADDENDUM_ID, R.A1_ADDENDUM_SHA256, R.A1_APPROVAL)):
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
    if which == "a1r4" and pac.get("TASK-20260923-4ff597") != R.PHASE_A_COMMIT_4FF597:
        errs.append("phase_a_commits TASK-20260923-4ff597 != %s" % R.PHASE_A_COMMIT_4FF597)
    if not (pac.get("sources") or {}):
        errs.append("phase_a_commits sources not recorded")
    for k in ("implementation_v2_clean", "implementation_v2_a1_clean", "implementation_v2_r4_clean"):
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
    redirections, the SE-3, HR-3 and RL-5 read-backs, the SE-6 hash-seed read-back and cypari2 versions."""
    res = man.get("resources") or {}
    ps = res.get("pari_stack") or {}
    stack = ps.get("pari_stack") or {}
    if ps.get("status") in (None, "refused_before_any_command") or str(ps.get("status", "")).startswith("absent"):
        errs.append("pari_stack status %s" % ps.get("status"))
    red = ps.get("redirections") or {}
    for key, v in red.items():
        if v.get("equal") is not True:
            errs.append("RC-3 / SE-3 / HR-3 / RL-5 read-back %s not as required" % key)
    if not red:
        errs.append("RC-3 redirection read-back not recorded")
    se3 = red.get(SE3_KEY) or {}
    if not (se3.get("v2_driver.solve_is_r4_wrapper") is True and se3.get("wrapper_original_is_frozen_v2_driver_solve") is True):
        errs.append("SE-3 replacement read-back not recorded as wrapper-with-frozen-original")
    rl1 = red.get(RL1_KEY) or {}
    if not (rl1.get("v2_solver.run_child_is_r4_launch_recorder") is True and rl1.get("recorder_original_is_frozen_v2_solver_run_child") is True
            and rl1.get("captured_run_child_locked_code_is_frozen") is True and rl1.get("rg1_callback_registered_in_installing_process") is True
            and rl1.get("one_v2_solver_module_object") is True):
        errs.append("RL-5 install read-back not recorded as recorder-with-frozen-original, frozen code objects, RG-1 callback and one v2_solver module")
    if which == "a1r4":
        hr3 = red.get(HR3_KEY_A1) or {}
        if not (hr3.get("a1_health.run_system_is_r4_wrapper") is True and hr3.get("wrapper_original_is_frozen_a1_health_run_system") is True
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
    gate_ids = R.load_json(R.PLAN_V2_R4)["gate"]["blocking_packages"]
    if rid != gate_ids[0]:
        rg = (man.get("gate") or {}).get("regression_REG-1") or {}
        if rg.get("verdict") != "PASS":
            errs.append("gate.regression_REG-1 not recorded PASS: %s" % rg.get("verdict"))
        if rg.get("d_branch") != R.REG1_D_BRANCH:
            errs.append("gate.regression_REG-1 d_branch %s != %s" % (rg.get("d_branch"), R.REG1_D_BRANCH))
        if rg.get("exclusion_list_sha256") != plan["gate"]["regression"]["exclusion_list_sha256"]:
            errs.append("gate.regression_REG-1 exclusion-list sha256 differs from the plan's")


def status_agreement(rd, man, errs):
    """The manifest status agrees with raw-result.json's run_status (alpha)."""
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    if man.get("status") != raw.get("run_status") and not (raw.get("run_status") == "completed_valid" and man.get("status") == "failed"):
        errs.append("manifest status disagrees with raw-result")


# ----------------------------------------------------------------------------- the r4 verdict layer (epsilon readers; E2)
def launch_record_class(r):
    """RF-3 (a) read with RG-1 (d): "A", "B", "C" or None (no class)."""
    if r.get("readback_from") != "returned_record" or r.get("raised") is not None:
        return None
    if r.get("child_created") is False and r.get("child_end") == "no_child":
        return "A"
    if r.get("child_created") is True and r.get("pair_read_by_parent") is True:
        if r.get("child_end") == "exec" or (r.get("child_end") == "frozen_pre_exec_exit" and r.get("returncode") in (98, 99)):
            return "B"
        return None
    if r.get("child_created") is True and r.get("pair_read_by_parent") is False:
        rep = r.get("child_rlimit_report")
        if (r.get("child_rlimit_report_carried") is True and isinstance(rep, str) and (rep == "" or rep.startswith("ERR setrlimit"))
                and "returncode" in r and r.get("child_end") == "frozen_pre_exec_exit"):
            return "C"
    return None


def launch_class_check(doc, errs):
    """RF-3 (a): every launch record is one of the positive classes (A), (B), (C) read with RG-1 (d)."""
    for r in (doc or {}).get("launch_records") or []:
        if launch_record_class(r) is None:
            errs.append("launch record %s (tag %s) is no positive class (RF-3 (a); RG-1 (d)): child_created %s raised %s pair_read_by_parent %s child_end %s"
                        % (r.get("ordinal"), r.get("tag"), r.get("child_created"), r.get("raised"), r.get("pair_read_by_parent"), r.get("child_end")))


def undetermined_check(man, doc, errs):
    """RF-0 (c): an `undetermined` value in any verdict input yields FAIL."""
    if man.get("raw_result_writer") == UNDET:
        errs.append("raw_result_writer is undetermined (RF-0 (b), (c))")
    for r in (doc or {}).get("launch_records") or []:
        for k in ("child_created", "child_end"):
            if r.get(k) == UNDET:
                errs.append("launch record %s %s is undetermined (RF-0 (c))" % (r.get("ordinal"), k))
        if r.get("frame_inspection") == "not_found":
            errs.append("launch record %s frame_inspection not_found (RK-1 (b); RF-1 (a))" % r.get("ordinal"))


def writer_check(man, errs):
    """RF-3 (a) / RF-0 (b): raw_result_writer "driver"."""
    if man.get("raw_result_writer") != "driver":
        errs.append("raw_result_writer %s, not driver (a wrapper-recorded or undetermined outcome; RF-0 (b); RF-3 (a))" % man.get("raw_result_writer"))


def foreign_files(rd):
    return sorted(f for f in os.listdir(rd) if f.startswith("recorder-foreign-"))


def foreign_check(rd, errs):
    """RF-1 (b): any recorder-foreign file makes the verdict FAIL."""
    for f in foreign_files(rd):
        errs.append("recorder-foreign file %s present (RF-1 (b))" % f)


def gaps_check(gaps, errs):
    """RL-3 as launchkind's reading_rule words it; RF-3 (a): a named gap or a recorder gap makes the verdict FAIL."""
    for g in gaps["named_gaps"]:
        errs.append("RL-3 named gap %s: %s" % (g.get("kind"), json.dumps({k: v for k, v in g.items() if k != "kind"}, default=str, sort_keys=True)))
    for g in gaps["gap_files"]:
        errs.append("RL-3 recorder gap %s: %s" % (g["file"], "; ".join(g["why"])))


def x13_check(man, which, plan, rid, rd, errs):
    """RF-5: the a1 checker's read of the controls_a1 image (X-13) against the values the admission read (X-02)."""
    if which != "a1r4":
        return
    pk = next((p for p in plan["packages"] if p["run_id"] == rid), {})
    if not pk.get("controls_a1_gate_required"):
        return
    cid = plan["gate"]["addendum_blocking_package"]
    # the image in the package's OWN runs directory (in a package: R.RUNS_DIR), the file the frozen X-13 read opens
    rp = os.path.join(os.path.dirname(os.path.abspath(rd).rstrip("/")), cid, "raw-result.json")
    try:
        r = json.load(open(rp))
    except Exception:                                    # noqa: BLE001
        r = {}
    now = {"run_status": r.get("run_status"), "gate_pass": r.get("gate_pass")}
    adm = (man.get("gate") or {}).get("controls_a1_image_admission_values")
    if adm != now:
        errs.append("RF-5 X-13: the controls_a1 image values read now %s differ from the admission values %s" % (now, adm))


def r4_checks(rd, which, plan):
    """The carried checks and the r4 verdict-layer checks. This function reads no site value itself: it calls the
    single-class checks above and collects their findings (VA-8 (b) model)."""
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
    doc = GAPS.load_doc(rd)
    gaps = GAPS.recorder_gaps(rd)
    v_errs = []
    gaps_check(gaps, v_errs)                             # RL-3; RF-3 (a)
    launch_class_check(doc, v_errs)                      # RF-3 (a) with RG-1 (d)
    writer_check(man, v_errs)                            # RF-0 (b); RF-3 (a)
    foreign_check(rd, v_errs)                            # RF-1 (b)
    undetermined_check(man, doc, v_errs)                 # RF-0 (c)
    x13_check(man, which, plan, rid, rd, v_errs)         # RF-5
    return errs + v_errs, notes, man, doc, gaps


def zl_child_files(files):
    """RK-3 (b) (iii): child/*.meta.json, solver/*.ms.log, and any file under health/, comparator/ or pari/."""
    return [f for f in files if (f.startswith("child/") and f.endswith(".meta.json")) or (f.startswith("solver/") and f.endswith(".ms.log"))
            or f.startswith(("health/", "comparator/", "pari/"))]


def frozen_items(output):
    """RF-2 (iv): the frozen checker's failing item lines, excluding its header line and the a1 checker's summary lines."""
    return [l[4:] for l in (output or "").splitlines() if l.startswith("  - ")]


def verdict(rd, which, plan, frozen_rc, frozen_out, errs, man, doc, gaps):
    """RK-3 (b) with RF-2 and RF-3; stop classes RF-3 (b); outcome labels RG-2, RH-2. Consumer of V-4, E2."""
    rid = os.path.basename(rd.rstrip("/"))
    records = list((doc or {}).get("launch_records") or [])
    items = frozen_items(frozen_out)
    gate_ids = R.load_json(R.PLAN_V2_R4)["gate"]["blocking_packages"]
    ctl_image = R.load_json(R.PLAN_A1_R4)["gate"]["addendum_blocking_package"]
    pk = next((p for p in plan["packages"] if p["run_id"] == rid), {})
    kind = pk.get("kind")
    if kind == "contingency":
        rep = ((man.get("package") or {}).get("replaces"))
        kind = next((p["kind"] for p in plan["packages"] if p["run_id"] == rep), None)
    if frozen_rc == 0 and not errs:
        v = "PASS"
    else:
        zl = {"i_not_gate_not_controls_a1_image": rid not in gate_ids and rid != ctl_image,
              "ii_launch_records_empty_recorder_read_back": (isinstance((doc or {}).get("launch_records"), list) and not records
                                                             and (((man.get("resources") or {}).get("pari_stack") or {}).get("redirections") or {}).get(RL1_KEY, {}).get("equal") is True),
              "iii_no_recorder_gap_no_child_file": not gaps["any_gap"] and not zl_child_files(gaps["files"]),
              "iv_frozen_exit_1_single_ZL_item": frozen_rc == 1 and items == [ZL_ITEM],
              "v_every_r4_check_passes": not errs,
              "vi_raw_result_writer_driver": man.get("raw_result_writer") == "driver",
              "vii_kind_cells_or_fixture4": kind in ZL_KINDS,
              "viii_no_recorder_foreign_file": not foreign_files(rd)}
        v = "PASS_ZL" if all(zl.values()) else "FAIL"
    stops, labels = [], []
    if v == "FAIL":
        infra = [r.get("ordinal") for r in records if r.get("child_created") is False or r.get("raised") is not None or r.get("pair_read_by_parent") is False]
        if infra:
            stops.append("an infrastructure launch (RK-3 (c); ordinals %s)" % infra)
        if man.get("raw_result_writer") == "wrapper":
            stops.append("a wrapper-recorded outcome (RF-0 (b))")
        if any(UNDET in e or "not_found" in e for e in errs):
            stops.append("an `undetermined` value (RF-0 (c))")
        if foreign_files(rd):
            stops.append("a recorder-foreign file (RF-1 (b))")
        if gaps["any_gap"]:
            stops.append("a recorder gap (RL-3)")
        cap_items = [i for i in items if i.startswith(CAP_MISMATCH_PREFIX) and "!= requested" in i]
        if cap_items:
            stops.append("a cap read-back mismatch (RH-2): %s" % cap_items)
        other = [i for i in items if i not in cap_items] + [e for e in errs if not (UNDET in e or "not_found" in e or e.startswith("RL-3 ")
                                                                                   or e.startswith("recorder-foreign"))]
        if other:
            stops.append("another checker item: %s" % other)
        if (man.get("raw_result_writer") == "driver" and records and ZL_ITEM in items
                and all(r.get("child_created") is False or r.get("raised") is not None or r.get("pair_read_by_parent") is False for r in records)):
            labels.append("infrastructure-stop outcome (RG-2)")
        if man.get("raw_result_writer") == "driver" and cap_items:
            labels.append("cap-mismatch stop outcome (RH-2)")
    return v, stops, labels


def main(rd, accounting_json=None, verdict_out=None):
    rd = os.path.abspath(rd)
    rid = os.path.basename(rd.rstrip("/"))
    which, plan = which_plan(rid)
    if which is None:
        print("%s: FAIL; run id not reserved in either r4 plan" % rid)
        print("R4 VERDICT: FAIL")
        if verdict_out is not None:
            verdict_out.update(verdict="FAIL", stop_classes=["another checker item: run id not reserved in either r4 plan"], frozen_checker_exit=None)
        return 1
    mode = "frozen-v2" if which == "v2r4" else "frozen-a1"
    # the frozen checker runs in its own process (RC-3 (e)) with cwd = the runs directory, on the run directory's NAME
    # (it joins every path to that argument and reads the run id from its basename), so its printed text names the run
    # directory's name, never its absolute path
    pr = subprocess.run(FROZEN_LAUNCHER + [mode, rid], cwd=os.path.dirname(rd), capture_output=True, text=True,
                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    frozen_out = pr.stdout.rstrip()
    print("frozen checker (%s, separate process, unchanged): %s" % ("v2_check_run" if which == "v2r4" else "a1_check_run",
                                                                     "PASS" if pr.returncode == 0 else "FAIL rc=%s" % pr.returncode))
    print(frozen_out)
    if pr.stderr.strip():
        print(pr.stderr.rstrip())
    errs, notes, man, doc, gaps = r4_checks(rd, which, plan)
    print("%s: r4 checks %s; %s" % (rid, "PASS" if not errs else "FAIL", notes))
    for e in errs:
        print("  -", e)
    v, stops, labels = verdict(rd, which, plan, pr.returncode, frozen_out, errs, man, doc, gaps)
    try:
        acc = sc4_accounting(rd)
    except Exception as e:                               # noqa: BLE001
        acc = {"error": repr(e), "rows": [], "violations": []}
    print("SC-4 accounting with RB-3 (recorded, never acted on): %s ok recorded attempts with a retained output %s; violations %d; "
          "coverage gaps named %d" % (acc.get("n_ok_recorded_with_output"), acc.get("n_by_site"), len(acc.get("violations") or []),
                                      len(acc.get("coverage_gaps_named") or [])))
    for r in acc.get("rows") or []:
        if r.get("applicable"):
            print("  %-22s %-40s n_roots %s n_den_zero %s n_arity %s n_points %s n_distinct %s invariant %s"
                  % (r["site"], r["tag"], r["n_roots"], r["n_den_zero"], r["n_arity"], r["n_points"], r["n_distinct"], r["invariant_holds"]))
        else:
            print("  %-22s %-40s %s" % (r["site"], r["tag"], r.get("status") or ("parse kind %s" % r.get("parse_kind"))))
    for g in acc.get("coverage_gaps_named") or []:
        print("  SC-4 COVERAGE GAP (RB-3; recorded, not a check failure): %s" % json.dumps(g, default=str))
    for x in acc.get("violations") or []:
        print("  SC-4 VIOLATION (recorded verbatim; routed to SJ-5; not a check failure): %s" % json.dumps(x, default=str))
    print("stop classes (RF-3 (b)): %s" % (stops or "none"))
    print("outcome labels (RG-2; RH-2): %s" % (labels or "none"))
    print("R4 VERDICT: %s" % v)
    if accounting_json:
        with open(accounting_json, "w") as fh:
            json.dump(acc, fh, indent=1, default=str)
    if verdict_out is not None:
        verdict_out.update(verdict=v, stop_classes=stops, outcome_labels=labels, frozen_checker_exit=pr.returncode, r4_errors=errs)
    return 0 if v in ("PASS", "PASS_ZL") else 1


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "reg1":
        import r4_reg1
        sys.exit(r4_reg1.main(sys.argv[2:]))
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
