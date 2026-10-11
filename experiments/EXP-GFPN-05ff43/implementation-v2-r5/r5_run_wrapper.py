#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r5 / 2-a1-r5 -- the r5 RUN WRAPPER (paristack PS-5 re-pointed; solverevent SE-6, SE-7 as
incorporated; seedresolve SF-7; healthresolve HR-8; launchcover CG-3; consumercover CC-4; valueclose VC-4;
DEC-20260924-e52eec VA-1, VA-3, VA-6, VA-7 (a) re-pointed; readbackcover RB-2, RB-4, RB-8; readbackfull RL-3, RL-4;
readbackclose RK-2, RK-3; failclosed RF-0 (b), RF-3, RF-5; childend RG-2; gapattr RH-2; launchkind RJ-8;
DEC-20260924-daf670 LKA-1, LKA-3, LKA-13; card R5S-6). Started from implementation-v2-r4/r4_run_wrapper.py (see implementation-v2-r5.md); that r4 file itself started from implementation-v2-r3/r3_run_wrapper.py.

usage: python3 -B r5_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]
launch form (RB-8; LKA-13), recorded verbatim with the status by the run card:
    ( setsid -w python3 -B <this wrapper> <RUN-ID> > <out> 2>&1 < /dev/null; echo "wrapper_exit=$?" >> <out> ) &
no outer guard (no timeout, ulimit, nice, taskset or wrapper script).

The command is NOT given on the command line: it is read from the package's entry in the r5 plan that reserves RUN-ID
(trial-plan-v2-r5.json or trial-plan-v2-a1-r5.json). Before ANY directory is created the wrapper evaluates EVERY check
below and REFUSES (exit 2, nothing written, every failing reason printed) unless all hold:
  R-1  EIGHTEEN hashes (LKA-1; RJ-8; AD-3 (b)): the v2 amendment, the v2-a1 addendum and the sixteen repair
       amendments (fifteen launchkind-lineage plus admitdev);
  R-2  RUN-ID is reserved in the r5 plan it belongs to and is none of: a v1 id, a v2 id, a v2-a1 id, an r1, r2, r3 or r4 id,
       or any of the 204 retired ids (LKA-3; RB-6 (c) as AD-3 re-points it);
  R-3  runs/RUN-ID does not exist;
  R-4  implementation-v2/, implementation-v2.md, trial-plan-v2.json match the TASK-20260923-0fa03f phase-A receipt
       file by file, are tracked and clean, with no unbound file;
  R-5  the same for implementation-v2-a1/ (+ .md, plan) against the TASK-20260923-4ff597 phase-A receipt;
  R-6  the same for implementation-v2-r5/, implementation-v2-r5.md and both r5 plans against the TASK-20260925-0ed1be
       phase-A receipt;
  R-7  the gate (PS-4 read with RB-4, RL-4, RK-3, RF-3, RF-5): for every gate_required v2-r5 package and every v2-a1-r5
       package, for EACH of G1..G4 (a) raw-result run_status completed_valid and gate_pass true AND (b) the r5 checker,
       run by this wrapper at admission time on that gate package, exits 0 with verdict PASS (RB-4); REG-1 (d-parsed)
       passed (evaluated before G2 and before every later package); addendum packages 2-11 additionally need the
       controls_a1 image to satisfy (a) and (b);
  R-8  every package this one `requires` has a manifest (existence test kept) AND (RL-4 with RK-3 (a), (d)) the r5
       checker verdict PASS or PASS_ZL on EACH r5-lineage package this one reads or is required to follow: every
       `requires` entry except the F-4 package (whose verdict is recorded and gates nothing, RK-3 (d)); G1 as read by
       REG-1 (X-03) for every package after G1; the build package a cells package loads (X-07); the prior m = 5 package
       an m = 4 cells package reads (X-08); every package the aggregate (X-09) and aggregate_a1 (X-10) read; every
       contingency package of a plan whose manifests resolve_replacement / _resolve read (X-11). A FAIL refuses the
       package with the RF-3 (b) stop class; it is never evidence;
  R-9  the plan's watchdogs object equals trial-plan-v2.json's exactly;
  R-10 no other solver-like process is running (v2_solver.other_solver_processes);
  R-11 the ceiling: existing run directories under any id of the TWELVE plans (frozen v2 and v2-a1, both r1, both r2, both
       r3, both r4, both r5), plus one, <= 48; and the plan's own count + 1 <= its package_count;
  R-12 contingency_rule verbatim (trial-plan-v2.json line 185) within one r5 plan;
  R-13 the plan records its protocol_version label, the ids and sha256 of the sixteen repair amendments and its run card;
       none of the TEN forbidden task ids appears in it; and no r5 constant or redirected attribute value carries one.
THE r5 CHECKER (r5_check_run) is run IN THIS PROCESS (its frozen checker in its own process, RC-3 (e)); its command,
exit status, verdict and output are recorded verbatim under gate.gate_package_checker / gate.required_package_checker
of the admitted package's manifest, and the package's OWN verdict (RK-3 (b)) is recorded in its manifest after the
package ran.
SE-6: the driver child's environment carries PYTHONHASHSEED="0"; the entry reads it back inside the driver process.
GFPN_V2_CAP_BYTES (LKA-13): whether it is set in this wrapper's environment is recorded (environment.json, manifest).
"""
import contextlib
import datetime
import io
import json
import os
import platform
import resource
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402

sys.path.insert(0, R.V2_DIR)
import yaml                                              # noqa: E402

import v2_solver as V                                    # noqa: E402  (other_solver_processes only)
import r5_reg1 as REG                                    # noqa: E402
import r5_resolve as RS                                  # noqa: E402  (constants only)
import r5_gaps as GAPS                                   # noqa: E402  (RL-3 accounting; records only in the wrapper)

ENTRY_V2 = os.path.join(HERE, "r5_entry_v2.py")
ENTRY_A1 = os.path.join(HERE, "r5_entry_a1.py")
RUNS = R.RUNS_DIR                                        # module-level: redirected only in development checks
DRIVER_PYTHONHASHSEED = R.DRIVER_PYTHONHASHSEED          # SE-6 "0"; changed only in-process by a development check (SE-5)
F4_KIND = "fixture4"


def git(*args):
    return subprocess.run(["git", "-C", R.REPO] + list(args), capture_output=True, text=True,
                          env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).stdout.strip()


def git_tree_state(paths_rel):
    """(tracked files, dirty porcelain lines including untracked) for repo-relative paths."""
    return git("ls-files", "--", *paths_rel).splitlines(), git("status", "--porcelain", "--untracked-files=all", "--", *paths_rel).splitlines()


def disk_files(dir_rel):
    d = os.path.join(R.REPO, dir_rel)
    return sorted(os.path.relpath(os.path.join(dp, f), R.REPO) for dp, _dn, fn in os.walk(d) for f in fn)


def phase_a_commit(receipt_path):
    """receipt commit_sha if backfilled, else git log -1 of the receipt (CORR-20260923-fb1be8 XD-1)."""
    if not os.path.exists(receipt_path):
        return None, "receipt absent"
    rc = R.load_json(receipt_path)
    if rc.get("commit_sha"):
        return rc["commit_sha"], "receipt commit_sha (backfilled)"
    sha = git("log", "-1", "--format=%H", "--", os.path.relpath(receipt_path, R.REPO))
    return (sha or None), ("git log -1 of the receipt file" if sha else "not determinable: receipt not committed")


def _raw(rid):
    rp = os.path.join(RUNS, rid, "raw-result.json")
    if not os.path.exists(rp):
        return None
    try:
        return json.load(open(rp))
    except Exception:                                    # noqa: BLE001
        return {"run_status": "unparseable"}


def _manifest(rid):
    mp = os.path.join(RUNS, rid, "manifest.yaml")
    if not os.path.exists(mp):
        return None
    return yaml.safe_load(open(mp))["run"]


def tree_check(tag, paths_rel, receipt_path, receipt_label, ref):
    """R-4 / R-5 / R-6: receipt file-by-file, tracked and clean, no unbound file (git and disk)."""
    tr, dirty = git_tree_state(paths_rel)
    d0 = paths_rel[0]
    if not any(t.startswith(d0 + "/") for t in tr) or any(p not in tr for p in paths_rel[1:]):
        ref.append("%s %s are not all tracked by git" % (tag, ", ".join(paths_rel)))
    if dirty:
        ref.append("%s paths are dirty: %s" % (tag, dirty))
    if not os.path.exists(receipt_path):
        ref.append("%s %s receipt absent: %s" % (tag, receipt_label, os.path.relpath(receipt_path, R.REPO)))
        return tr, dirty
    bound = R.receipt_paths(R.load_json(receipt_path))
    bad = [p for p, h in bound.items() if (p == d0 or p.startswith(d0 + "/") or p in paths_rel)
           and (not os.path.exists(os.path.join(R.REPO, p)) or R.sha256_file(os.path.join(R.REPO, p)) != h)]
    if bad:
        ref.append("%s paths differ from the %s receipt: %s" % (tag, receipt_label, bad))
    rb = sorted(p for p in bound if p.startswith(d0 + "/"))
    if sorted(t for t in tr if t.startswith(d0 + "/")) != rb:
        ref.append("%s %s/ file list differs between git and the %s receipt" % (tag, d0, receipt_label))
    unbound_disk = sorted(set(disk_files(d0)) - set(rb))
    if unbound_disk:
        ref.append("%s files under %s/ not bound by the %s receipt: %s" % (tag, d0, receipt_label, unbound_disk))
    for p in paths_rel[1:]:
        if p not in bound:
            ref.append("%s %s not bound by the %s receipt" % (tag, p, receipt_label))
    return tr, dirty


def plans():
    return {"v2r5": R.load_json(R.PLAN_V2_R5), "a1r5": R.load_json(R.PLAN_A1_R5),
            "v2": R.load_json(R.PLAN_V2), "a1": R.load_json(R.PLAN_A1),
            "v2r1": R.load_json(R.PLAN_V2_R1), "a1r1": R.load_json(R.PLAN_A1_R1),
            "v2r2": R.load_json(R.PLAN_V2_R2), "a1r2": R.load_json(R.PLAN_A1_R2),
            "v2r3": R.load_json(R.PLAN_V2_R3), "a1r3": R.load_json(R.PLAN_A1_R3),
            "v2r4": R.load_json(R.PLAN_V2_R4), "a1r4": R.load_json(R.PLAN_A1_R4)}


def g1_id(P):
    return P["v2r5"]["gate"]["blocking_packages"][0]


def reg1(P):
    """Evaluate REG-1 (reference RUN-GFPN-ac4487 vs the r5 image G1; d-parsed). Returns the manifest block."""
    g1 = g1_id(P)
    cand = os.path.join(RUNS, g1)
    if not os.path.exists(os.path.join(cand, "raw-result.json")):
        return {"verdict": "NOT_EVALUABLE", "reason": "G1 %s has not run" % g1}
    ref = os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN)
    rep = REG.compare(ref, cand)
    return {"verdict": rep["verdict"], "d_branch": R.REG1_D_BRANCH, "candidate": g1, "reference": R.REG1_REFERENCE_RUN,
            "exclusion_list_sha256": rep["exclusion_list_sha256"], "failures": rep["failures"], "output": REG.render(rep)}


def refuse_forbidden_ids(plan, ref):
    """R-13 with VA-7 (a): plan text (no site value), r5 constants and redirected attribute values."""
    if plan is not None and R.forbidden_ids_in_text(json.dumps(plan)):
        ref.append("R-13 the plan carries a forbidden task id")
    if R.forbidden_ids_in_values(R.r5_constant_values()):
        ref.append("R-13 (VA-7 (a)) an r5 constant or redirected attribute value carries a forbidden task id")


# ----------------------------------------------------------------------------- the r5 checker verdict (V-4; RB-4 (b); RL-4; RK-3 (b))
_VERDICTS = {}


def checker_verdict(rid):
    """Run the r5 checker IN THIS PROCESS on runs/<rid> (its frozen checker runs in its own process, RC-3 (e)) and
    return {command, exit_status, verdict, stop_classes, output}. Memoized per preflight. Consumer of V-4 with effect
    E2 (RB-4 (b); RK-3 (b); RK-5; RF-7): disposition RB-4 / RK-3 (b) / RF-2 / RF-3 closed rules only."""
    if rid in _VERDICTS:
        return _VERDICTS[rid]
    import r5_check_run as K
    rd = os.path.join(RUNS, rid)
    buf = io.StringIO()
    res = {}
    with contextlib.redirect_stdout(buf):
        try:
            rc = K.main(rd, verdict_out=res)
        except Exception as e:                           # noqa: BLE001
            rc = 1
            res = {"verdict": "FAIL", "stop_classes": ["another checker item: the r5 checker raised %s" % type(e).__name__]}
    out = {"command": "r5_check_run.main(<runs directory>/%s) in the r5 run wrapper's process (frozen checker in its own process, "
                      "cwd <runs directory>: %s <mode> %s)" % (rid, " ".join(K.FROZEN_LAUNCHER), rid),
           "exit_status": rc, "verdict": res.get("verdict", "FAIL"), "stop_classes": res.get("stop_classes", []),
           "frozen_checker_exit": res.get("frozen_checker_exit"), "output": buf.getvalue()}
    _VERDICTS[rid] = out
    return out


def r7_gate_packages(gate_ids, ref, recs):
    """R-7 with RB-4: every repaired gate package (a) completed_valid with gate_pass true (alpha) AND (b) the r5 checker
    exits 0 with verdict PASS (V-4, E2). PASS_ZL never applies to a gate package (RK-3 (b) (i))."""
    for g in gate_ids:
        r = _raw(g)
        if r is None:
            ref.append("R-7 repaired gate package %s has not run" % g)
            continue
        if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
            ref.append("R-7 repaired gate package %s did not pass: status %s gate_pass %s (PS-4)" % (g, r.get("run_status"), r.get("gate_pass")))
        v = checker_verdict(g)
        recs[g] = v
        if v["exit_status"] != 0 or v["verdict"] != "PASS":
            ref.append("R-7 (RB-4 (b)) the r5 checker on gate package %s: exit %s verdict %s; stop %s" % (g, v["exit_status"], v["verdict"], v["stop_classes"]))


def r7_reg1_verdict(rg, ref):
    """R-7: REG-1 passed before G2 and every later package (V-2; disposition CG-4)."""
    if rg["verdict"] != "PASS":
        ref.append("R-7 REG-1 did not pass (%s): %s" % (rg["verdict"], rg.get("reason") or rg.get("failures")))


def r7_controls_a1_image(cid, ref, recs):
    """R-7 with RB-4: addendum packages 2-11 need the image of controls_a1 (a) completed_valid with gate_pass true
    (alpha) and (b) the r5 checker exit 0 with verdict PASS (V-4, E2)."""
    r = _raw(cid)
    if r is None:
        ref.append("R-7 controls_a1 image %s has not run" % cid)
        return None
    if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
        ref.append("R-7 controls_a1 image %s did not pass: status %s gate_pass %s" % (cid, r.get("run_status"), r.get("gate_pass")))
    v = checker_verdict(cid)
    recs[cid] = v
    if v["exit_status"] != 0 or v["verdict"] != "PASS":
        ref.append("R-7 (RB-4 (b)) the r5 checker on the controls_a1 image %s: exit %s verdict %s; stop %s" % (cid, v["exit_status"], v["verdict"], v["stop_classes"]))
    return {"run_status": r.get("run_status"), "gate_pass": r.get("gate_pass")}


def r8_requires(pk, by_id, ref):
    """R-8: every package this one requires has a manifest (existence only; no site value)."""
    for req in pk.get("requires", []):
        if not os.path.exists(os.path.join(RUNS, req, "manifest.yaml")):
            ref.append("R-8 required earlier package %s (%s) has no manifest" % (req, by_id.get(req, {}).get("label")))


def read_packages(rid, pk, which, P):
    """RL-4 with RK-3 (a): the r5-lineage packages this package reads or is required to follow, by name of read
    (reads no site value: plan text and manifest existence only). Returns {run_id: [read names]}; the F-4 image is
    returned under 'f4_not_blocking'."""
    plan = P["v2r5"] if which == "v2r5" else P["a1r5"]
    by_id = {p["run_id"]: p for p in plan["packages"]}
    reads, f4 = {}, []

    def add(r, why):
        reads.setdefault(r, [])
        if why not in reads[r]:
            reads[r].append(why)
    for req in pk.get("requires", []):
        if (by_id.get(req) or {}).get("kind") == F4_KIND:
            f4.append(req)                                  # RK-3 (d): F-4 stays not blocking
        else:
            add(req, "X-04 requires")
    g1 = g1_id(P)
    if rid != g1:
        add(g1, "X-03 G1 read by REG-1")
    args = list(pk.get("driver_args") or [])
    cont = [p["run_id"] for p in plan["packages"] if p["kind"] == "contingency" and os.path.exists(os.path.join(RUNS, p["run_id"], "manifest.yaml"))]
    if pk.get("kind") == "cells":
        p = int(args[args.index("--p") + 1])
        for b in plan["packages"]:
            if b["kind"] == "build" and b.get("p") == p:
                add(b["run_id"], "X-07 _load_build")
        if "--prior-run" in args:
            add(args[args.index("--prior-run") + 1], "X-08 _prior_cells / _condition_met")
        for c in cont:
            add(c, "X-11 resolve_replacement (contingency manifest)")
    if pk.get("kind") == "aggregate":
        for r in args[args.index("--runs") + 1].split(","):
            add(r, "X-09 cmd_aggregate")
        for c in cont:
            add(c, "X-11 resolve_replacement (contingency manifest)")
    if pk.get("kind") == "aggregate_a1":
        for flag, why in (("--v2-runs", "X-10 cmd_aggregate_a1 (--v2-runs)"), ("--a1-runs", "X-10 cmd_aggregate_a1 (--a1-runs)"),
                          ("--v2-aggregate", "X-10 cmd_aggregate_a1 (--v2-aggregate)")):
            if flag in args:
                for r in [x for x in args[args.index(flag) + 1].split(",") if x]:
                    add(r, why)
        v2cont = [p["run_id"] for p in P["v2r5"]["packages"] if p["kind"] == "contingency" and os.path.exists(os.path.join(RUNS, p["run_id"], "manifest.yaml"))]
        for c in cont + v2cont:
            add(c, "X-11 a1_driver._resolve (contingency manifest)")
    return reads, f4


def rl4_read_packages(reads, ref, recs):
    """RL-4 with RK-3 (b), (c) replaced by RF-3 (b): each read package's r5 verdict must be PASS or PASS_ZL (V-4, E2)."""
    for r, why in sorted(reads.items()):
        if not os.path.exists(os.path.join(RUNS, r, "manifest.yaml")):
            ref.append("R-8 (RL-4) read package %s (%s) has no manifest" % (r, ", ".join(why)))
            continue
        v = checker_verdict(r)
        recs[r] = dict(v, reads=why)
        if v["verdict"] not in ("PASS", "PASS_ZL"):
            ref.append("R-8 (RL-4; RF-3 (b) designed stop) read package %s (%s): r5 verdict %s; stop %s" % (r, ", ".join(why), v["verdict"], v["stop_classes"]))


def f4_recorded(f4, recs):
    """RK-3 (d): the F-4 package's r5 verdict is recorded under gate.required_package_checker and gates nothing."""
    for r in f4:
        if os.path.exists(os.path.join(RUNS, r, "manifest.yaml")):
            recs[r] = dict(checker_verdict(r), reads=["X-04 requires (F-4: NOT blocking, recorded only; RK-3 (d))"])


def r12_contingency(rid, replaces, plan, by_id, ref):
    """R-12 contingency_rule verbatim within one r5 plan (reads the replaced package's recorded failure_class: alpha)."""
    if not replaces:
        ref.append("R-12 a contingency package must name the package it replaces (--replaces)")
    elif replaces not in by_id:
        ref.append("R-12 --replaces must name a package of the SAME r5 plan (never across plans): %s" % replaces)
    elif by_id[replaces]["kind"] == "contingency":
        ref.append("R-12 --replaces must name a planned, non-contingency package")
    else:
        tgt = by_id[replaces]
        if tgt.get("blocking"):
            ref.append("R-12 %s is a gate package and is never replaced (contingency_rule; PS-4)" % replaces)
        man = _manifest(replaces)
        if man is None:
            ref.append("R-12 replaced package has no manifest")
        elif man.get("failure_class") != "infrastructure_error":
            ref.append("R-12 only an infrastructure_error package may be replaced (never implementation_error, resource_exhaustion, "
                       "invalid_measurement or a result): %s is %s" % (replaces, man.get("failure_class")))
        for p2 in plan["packages"]:
            if p2["kind"] == "contingency" and p2["run_id"] != rid:
                m2 = _manifest(p2["run_id"])
                if m2 and (m2.get("package") or {}).get("replaces") == replaces:
                    ref.append("R-12 %s was already replaced once by %s" % (replaces, p2["run_id"]))


def preflight(rid, replaces=None):
    """Evaluate every refusal. Returns (refusals, info). Writes nothing."""
    _VERDICTS.clear()
    ref, info = [], {"rid": rid, "replaces": replaces, "gate_package_checker": {}, "required_package_checker": {}}
    # R-1 (seventeen hashes)
    info["amendment_sha256"] = {}
    for path, want in R.BOUND_HASHES:
        got = R.sha256_file(path) if os.path.exists(path) else None
        info["amendment_sha256"][os.path.basename(path)] = got
        if got != want:
            ref.append("R-1 %s sha256 %s != bound %s" % (os.path.basename(path), got, want))
    try:
        P = plans()
    except Exception as e:                               # noqa: BLE001
        return ref + ["R-2 a plan is unreadable: %r" % (e,)], info
    info["plans"] = P
    v2_frozen = {p["run_id"] for p in P["v2"]["packages"]}
    a1_frozen = {p["run_id"] for p in P["a1"]["packages"]}
    r1_ids = {p["run_id"] for p in P["v2r1"]["packages"]} | {p["run_id"] for p in P["a1r1"]["packages"]}
    r2_ids = {p["run_id"] for p in P["v2r2"]["packages"]} | {p["run_id"] for p in P["a1r2"]["packages"]}
    r3_ids = {p["run_id"] for p in P["v2r3"]["packages"]} | {p["run_id"] for p in P["a1r3"]["packages"]}
    r4_ids = {p["run_id"] for p in P["v2r4"]["packages"]} | {p["run_id"] for p in P["a1r4"]["packages"]}
    v1 = set(P["v2"].get("v1_ids_never_reused", [])) | set(P["a1"].get("v1_ids_never_reused", []))
    which = "v2r5" if rid in {p["run_id"] for p in P["v2r5"]["packages"]} else (
        "a1r5" if rid in {p["run_id"] for p in P["a1r5"]["packages"]} else None)
    info["plan_key"] = which
    plan = P[which] if which else None
    by_id = {p["run_id"]: p for p in plan["packages"]} if plan else {}
    pk = by_id.get(rid)
    # R-2
    if rid in v1:
        ref.append("R-2 %s is a v1 run id" % rid)
    if rid in v2_frozen:
        ref.append("R-2 %s is a v2 run id (trial-plan-v2.json); retired or kept as a record, never run under the r5 wrapper" % rid)
    if rid in a1_frozen:
        ref.append("R-2 %s is a v2-a1 run id (trial-plan-v2-a1.json); retired, never run under the r5 wrapper" % rid)
    if rid in r1_ids:
        ref.append("R-2 %s is an r1 run id (trial-plan-v2-r1.json / trial-plan-v2-a1-r1.json); retired, never run" % rid)
    if rid in r2_ids:
        ref.append("R-2 %s is an r2 run id (trial-plan-v2-r2.json / trial-plan-v2-a1-r2.json); retired, never run" % rid)
    if rid in r3_ids:
        ref.append("R-2 %s is an r3 run id (trial-plan-v2-r3.json / trial-plan-v2-a1-r3.json); kept as a record or retired, never run" % rid)
    if rid in r4_ids:
        ref.append("R-2 %s is an r4 run id (trial-plan-v2-r4.json / trial-plan-v2-a1-r4.json); TERMINAL FAILED lineage, retired, never run" % rid)
    if rid in set(R.RETIRED_ALL):
        ref.append("R-2 %s is a retired run id (the 162 retired ids)" % rid)
    if pk is None:
        ref.append("R-2 %s is not reserved in trial-plan-v2-r5.json or trial-plan-v2-a1-r5.json" % rid)
    # R-3
    if os.path.exists(os.path.join(RUNS, rid)):
        ref.append("R-3 run directory exists (immutable): %s" % os.path.join(RUNS, rid))
    # R-4, R-5, R-6
    info["v2_tree"] = tree_check("R-4", R.V2_PATHS_REL, R.RECEIPT_V2_PHASE_A, "TASK-20260923-0fa03f phase-A", ref)
    info["a1_tree"] = tree_check("R-5", R.A1_PATHS_REL, R.RECEIPT_A1_PHASE_A, "TASK-20260923-4ff597 phase-A", ref)
    info["r4_tree"] = tree_check("R-6", R.R5_PATHS_REL, R.RECEIPT_R5_PHASE_A, "%s phase-A" % R.ARCHIVE_TASK, ref)
    info["reg1"] = None
    info["x13_admission_values"] = None
    if pk is not None:
        gate_ids = P["v2r5"]["gate"]["blocking_packages"]
        need_gate = (which == "v2r5" and pk.get("gate_required")) or which == "a1r5"
        if need_gate:
            r7_gate_packages(gate_ids, ref, info["gate_package_checker"])            # R-7 (alpha; V-4 E2)
        if rid != gate_ids[0]:
            info["reg1"] = reg1(P)
            r7_reg1_verdict(info["reg1"], ref)                                       # R-7 (V-2)
        if which == "a1r5" and pk.get("controls_a1_gate_required"):
            info["x13_admission_values"] = r7_controls_a1_image(plan["gate"]["addendum_blocking_package"], ref, info["gate_package_checker"])
        r8_requires(pk, by_id, ref)                                                  # R-8 (existence)
        reads, f4 = read_packages(rid, pk, which, P)                                 # RL-4 / RK-3 (a) (plan text)
        info["reads"] = {"reads": reads, "f4_not_blocking": f4}
        rl4_read_packages(reads, ref, info["required_package_checker"])              # RL-4 (V-4 E2)
        f4_recorded(f4, info["required_package_checker"])                            # RK-3 (d) (recorded only)
    # R-9
    if plan is not None and plan.get("watchdogs") != P["v2"].get("watchdogs"):
        ref.append("R-9 the plan's watchdogs differ from trial-plan-v2.json lines 95-177")
    # R-10
    others = V.other_solver_processes()
    if others:
        ref.append("R-10 another solver-like process is running (EC-10): %s" % others)
    # R-11 (twelve plans)
    all_ids = (v2_frozen | a1_frozen | r1_ids | r2_ids | r3_ids | r4_ids | {p["run_id"] for p in P["v2r5"]["packages"]}
               | {p["run_id"] for p in P["a1r5"]["packages"]})
    existing = sorted(i for i in all_ids if os.path.exists(os.path.join(RUNS, i)))
    info["existing_dirs"] = existing
    if len(existing) + 1 > R.MAX_PACKAGES_SHARED:
        ref.append("R-11 ceiling: %d run directories exist under ids of the ten plans; one more exceeds 48 -- an impediment for a new Coordinator decision" % len(existing))
    if plan is not None:
        own = [p["run_id"] for p in plan["packages"] if os.path.exists(os.path.join(RUNS, p["run_id"]))]
        if len(own) + 1 > int(plan.get("package_count", 0)):
            ref.append("R-11 the plan's own package_count %s would be exceeded" % plan.get("package_count"))
    # R-12
    if pk is not None and pk["kind"] == "contingency":
        r12_contingency(rid, replaces, plan, by_id, ref)
    elif replaces:
        ref.append("R-12 --replaces is only valid for a contingency id")
    # R-13
    if plan is not None:
        want_label, want_task = (R.PROTOCOL_V2_R5, R.TASK_RUNS_V2) if which == "v2r5" else (R.PROTOCOL_A1_R5, R.TASK_RUNS_A1)
        rp = (plan.get("repair") or {}).get("amendments") or {}
        want_rep = R.repair_amendments()
        bad_rep = [k for k in R.REPAIR_KEYS if ((rp.get(k) or {}).get("id"), (rp.get(k) or {}).get("sha256")) != (want_rep[k]["id"], want_rep[k]["sha256"])]
        if plan.get("protocol_version") != want_label or bad_rep or plan.get("task_id") != want_task:
            ref.append("R-13 the plan does not record protocol_version %s, the repair amendments' ids/sha256 (%s) and run card %s"
                       % (want_label, bad_rep or "ok", want_task))
    refuse_forbidden_ids(plan, ref)
    info["pk"], info["plan"] = pk, plan
    return ref, info


# ----------------------------------------------------------------------------- RB-2 collector with RL-3 (d), (e); RK-2 accounting
def collect(obj, key, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                out.append(v)
            collect(v, key, out)
    elif isinstance(obj, list):
        for v in obj:
            collect(v, key, out)
    return out


def _pair_key(v):
    return json.dumps(v, sort_keys=True) if isinstance(v, dict) else None


def readback_sources(rd, raw, doc):
    """RB-2 (a)-(c) with RL-3 (d), (e): every read-back pair found per source, BEFORE de-duplication (K-2 derivative,
    E5; records only; builds V-3)."""
    src = {"a_raw_result_key_name": [v for v in collect(raw, "rlimit_as_child_getrlimit", []) if v],
           "b_child_meta_json": [], "c_attempt_records": [], "d_launch_records": [], "e_passthrough_records": []}
    cd = os.path.join(rd, "child")
    if os.path.isdir(cd):
        for f in sorted(os.listdir(cd)):
            if f.endswith(".meta.json"):
                try:
                    v = json.load(open(os.path.join(cd, f))).get("rlimit_as_child_getrlimit")
                except Exception:                        # noqa: BLE001
                    v = None
                if v:
                    src["b_child_meta_json"].append(v)
    sites = (doc or {}).get("sites") or {}
    for site in (R.SITE_S1, R.SITE_S2):
        for a in (sites.get(site) or {}).get("attempt_records") or []:
            v = (a.get("rb1") or {}).get("rlimit_as_child_getrlimit")
            if isinstance(v, dict):
                src["c_attempt_records"].append(v)
    for r in (doc or {}).get("launch_records") or []:
        if isinstance(r.get("rlimit_as_child_getrlimit"), dict):
            src["d_launch_records"].append(r["rlimit_as_child_getrlimit"])
    for p in (sites.get(R.SITE_S1) or {}).get("passthrough_records") or []:
        v = (p.get("rb1") or {}).get("rlimit_as_child_getrlimit")
        if isinstance(v, dict):
            src["e_passthrough_records"].append(v)
    return src


def threads_sources(raw, doc):
    """RB-2: msolve_threads_executed from (a) raw-result.json by key name and (c) every attempt record (RB-1 (c))."""
    vals = [v for v in collect(raw, "threads_executed", []) if v is not None]
    for site in (R.SITE_S1, R.SITE_S2):
        for a in ((((doc or {}).get("sites") or {}).get(site) or {}).get("attempt_records") or []):
            v = (a.get("rb1") or {}).get("threads_executed")
            if v is not None and v != "absent":
                vals.append(v)
    return vals


def launch_class_accounting(records, sources):
    """RL-3 per launch with RK-2 (i)-(iii) and RF-1 (c) (ii), (iv): records and reports; gates nothing by itself
    (the r5 checker reads the launch records itself). K-2 derivative / epsilon reader, E5."""
    pairs = {k: {_pair_key(v) for v in vals} for k, vals in sources.items()}
    per, raised, nopair, notcreated, undet, absent_named = [], [], [], [], [], []
    for r in records:
        pk = _pair_key(r.get("rlimit_as_child_getrlimit"))
        row = {"ordinal": r.get("ordinal"), "tag": r.get("tag"), "child_created": r.get("child_created"), "readback_from": r.get("readback_from"),
               "pair_read_by_parent": r.get("pair_read_by_parent"), "child_end": r.get("child_end"), "raised": r.get("raised"),
               "sources_with_its_pair": sorted(k for k, s in pairs.items() if pk is not None and pk in s)}
        per.append(row)
        if r.get("raised") is not None:
            raised.append({"ordinal": r.get("ordinal"), "raised": r.get("raised"), "child_created": r.get("child_created"),
                           "pair_read_by_parent": r.get("pair_read_by_parent")})
        if r.get("child_created") is True and r.get("pair_read_by_parent") is False:
            rep = r.get("child_rlimit_report")
            if not r.get("child_rlimit_report_carried"):
                cls = "report not read"
            elif isinstance(rep, str) and rep.startswith("ERR setrlimit"):
                cls = "ERR setrlimit report"
            elif rep == "":
                cls = "empty report"
            elif isinstance(rep, str) and rep.startswith("OK"):
                cls = "OK report, pair not read"
            else:
                cls = "report not read"
            nopair.append({"ordinal": r.get("ordinal"), "class": cls, "child_rlimit_report": rep})
            absent_named.append({"ordinal": r.get("ordinal"), "tag": r.get("tag"), "child_rlimit_report": rep})
        if r.get("child_created") is False:
            notcreated.append({"ordinal": r.get("ordinal"), "raised": r.get("raised"), "refusal_reason": r.get("refusal_reason")})
        if r.get("child_created") == "undetermined":
            undet.append({"ordinal": r.get("ordinal"), "raised": r.get("raised")})
    return {"per_launch": per, "n_capped_children_evidenced_child_created_true": sum(1 for r in records if r.get("child_created") is True),
            "created_with_pair_absent": absent_named, "i_raised": raised, "ii_created_pair_not_read": nopair,
            "iii_child_created_false": notcreated, "iv_child_created_undetermined": undet}


def child_readback_accounting(rd, raw, doc):
    """RB-2 / RL-3 / RK-2: resources.child_readback_accounting. Recorded and reported, gating nothing by itself."""
    src = readback_sources(rd, raw, doc)
    records = list((doc or {}).get("launch_records") or [])
    acc = {"per_source_entries_before_dedup": {k: len(v) for k, v in src.items()}}
    acc.update(launch_class_accounting(records, src))
    gaps = GAPS.recorder_gaps(rd)
    acc["recorder_gaps"] = {"named_gaps": gaps["named_gaps"], "gap_files": gaps["gap_files"], "non_launch_files": gaps["non_launch_files"],
                            "run_directory_recorded": gaps["run_directory_recorded"], "n_files": gaps["n_files"],
                            "n_launch_records": gaps["n_launch_records"], "note": "RL-3: recorded and reported here; the r5 checker gates on it (RF-3 (a))"}
    return acc, src


def raw_result_writer(driver_parse):
    """RF-0 (b) with RG-6 (a): "driver" if raw-result.json exists and parses after the driver exits; "wrapper" if this
    wrapper writes the fallback; `undetermined` otherwise. epsilon, written by the wrapper (RF-7)."""
    return driver_parse


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:                               # noqa: BLE001
        return "ERROR: %r" % (e,)


def inference_block():
    return {"requested_policy": "executor-implementation", "resolved_model_id": None,
            "resolved_by": "not recorded by the executor; the dispatching session records the resolved binding",
            "backend": os.environ.get("AUTORESEARCH_BACKEND"), "policy_env": os.environ.get("AUTORESEARCH_POLICY"),
            "fallback_used": False, "fallback_reason": None, "bedrock_used": False,
            "note": "every number in this package comes from deterministic code (msolve, python-flint, PARI, pure Python); no model is in the arithmetic loop"}


def watchdog_after_resolve(raw, events):
    """SF-2 (d): cells whose per-cell watchdog fired after a target with at least one re-solve (S-1 events)."""
    resolved_tags = {e["tag"] for e in events if len(e.get("attempts") or []) >= 2}
    out = []
    for cell in (raw or {}).get("cells") or []:
        rows = cell.get("targets") or []
        fired = next((i for i, r in enumerate(rows) if r.get("status") == "not_attempted"
                      and str(r.get("reason", "")).startswith("per-cell watchdog")), None)
        if fired is None:
            continue
        before = ["%s_t%d" % (cell.get("arm"), r.get("target")) for r in rows[:fired] if r.get("target") is not None]
        hit = sorted(t for t in before if t in resolved_tags)
        if hit:
            out.append({"arm": cell.get("arm"), "m": cell.get("m"), "first_not_attempted_row": fired, "resolved_targets_before": hit})
    return out


def _site_block(sec):
    c = sec.get("counters") or {}
    ev = sec.get("events") or []
    return {"counters": c, "ssf_attempts_by_clause": c.get("ssf_attempts_by_clause"), "re_solves": c.get("re_solves"),
            "calls_still_ssf_after_last_attempt": c.get("calls_still_ssf_after_last_attempt"),
            "resolve_cap_reached": c.get("resolve_cap_reached"),
            "resolve_cap_reached_tags": [e.get("tag") for e in ev if e.get("resolve_cap_reached")],
            "event_tags": [e.get("tag") for e in ev], "n_attempt_records": len(sec.get("attempt_records") or [])}


def solver_events_block(rd, raw):
    """SC-11 (b) with HR-8, CG-3 and CC-4: the manifest block, recomputed from the run-root solver-events.json by
    constant key. The callgrind-site counts are COPIED (recorded and reported only; VA-6 (c))."""
    p = os.path.join(rd, RS.EVENTS_FILE)
    if not os.path.exists(p):
        return {"status": "absent: the entry point wrote no solver-events.json", "K": R.K, "spacing_s": R.SPACING_S}
    try:
        doc = json.load(open(p))
    except Exception as e:                               # noqa: BLE001
        return {"status": "unparseable: %r" % (e,), "K": R.K, "spacing_s": R.SPACING_S, "sha256": R.sha256_file(p)}
    sites = doc.get("sites") or {}
    s1, s2, s3 = sites.get(R.SITE_S1) or {}, sites.get(R.SITE_S2) or {}, sites.get(R.SITE_S3) or {}
    b1 = _site_block(s1)
    b1["watchdog_after_resolve"] = watchdog_after_resolve(raw, s1.get("events") or [])
    b1["n_passthrough_records"] = len(s1.get("passthrough_records") or [])
    return {"status": "present", "file": RS.EVENTS_FILE, "sha256": R.sha256_file(p), "K": doc.get("K"), "spacing_s": doc.get("spacing_s"),
            "cap_rule": doc.get("cap_rule"), "consistency_violation": doc.get("consistency_violation"),
            "recording_failures": doc.get("recording_failures"), "n_launch_records": len(doc.get("launch_records") or []),
            "watchdog_after_resolve": b1["watchdog_after_resolve"],
            "sites": {R.SITE_S1: b1, R.SITE_S2: _site_block(s2),
                      R.SITE_S3: {"recorded_and_reported_only": "VA-6 (c): no r5 function gates on these counts",
                                  "counters_copied": s3.get("counters")}}}


def listing(rd):
    """RL-3 / RGL-7: the post-completion listing with every file's sha256 (manifest.yaml itself excluded)."""
    out = {}
    for dp, _dn, fn in os.walk(rd):
        for f in fn:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, rd)
            if rel == "manifest.yaml":
                continue
            out[rel] = {"sha256": R.sha256_file(p), "bytes": os.path.getsize(p)}
    return dict(sorted(out.items()))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) not in (1, 3) or (len(argv) == 3 and argv[1] != "--replaces"):
        print("REFUSING (nothing written): usage: r4_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]", file=sys.stderr)
        return 2
    rid = argv[0]
    replaces = argv[2] if len(argv) == 3 else None
    refusals, info = preflight(rid, replaces)
    if refusals:
        for r in refusals:
            print("REFUSING (nothing written): " + r, file=sys.stderr)
        return 2
    if dry:
        print("DRY RUN: every R-1..R-13 check passes for %s; nothing written" % rid)
        return 0
    return launch(rid, replaces, info)


def launch(rid, replaces, info):
    P, plan, pk, which = info["plans"], info["plan"], info["pk"], info["plan_key"]
    by_id = {p["run_id"]: p for p in plan["packages"]}
    driver_args = pk.get("driver_args")
    if pk["kind"] == "contingency":
        tgt = by_id[replaces]
        driver_args = tgt["driver_args"]
        pk = dict(pk, replaces=replaces, replaced_label=tgt["label"], replaced_kind=tgt["kind"], watchdogs=tgt.get("watchdogs"))
    entry = ENTRY_V2 if which == "v2r5" else ENTRY_A1
    inv = {v: k for k, v in plan["id_map"].items()}
    rd = os.path.join(RUNS, rid)
    cmd = [sys.executable, "-B", entry] + list(driver_args)
    os.makedirs(os.path.join(rd, "certificates"))
    import v2_common as C                                # host_record only (unchanged v2 code)
    trees = {k: git_tree_state(p) for k, p in (("v2", R.V2_PATHS_REL), ("a1", R.A1_PATHS_REL), ("r5", R.R5_PATHS_REL))}
    rec_0fa03f, src_0fa03f = phase_a_commit(R.RECEIPT_V2_PHASE_A)
    rec_4ff597, src_4ff597 = phase_a_commit(R.RECEIPT_A1_PHASE_A)
    cf5, src_f5 = phase_a_commit(R.RECEIPT_R5_PHASE_A)
    pac = {"TASK-20260923-0fa03f": R.PHASE_A_COMMIT_0FA03F, R.ARCHIVE_TASK: cf5,
           "sources": {"TASK-20260923-0fa03f": "literal (PS-5; CORR-20260923-fb1be8 XD-1); receipt reading %s via %s" % (rec_0fa03f, src_0fa03f),
                       R.ARCHIVE_TASK: "read from its phase-A receipt at run time: %s" % src_f5}}
    if which == "a1r5":
        pac["TASK-20260923-4ff597"] = R.PHASE_A_COMMIT_4FF597
        pac["sources"]["TASK-20260923-4ff597"] = "literal (PS-5); receipt reading %s via %s" % (rec_4ff597, src_4ff597)
    env_rec = {
        "operating_system": platform.platform(), "python_version": platform.python_version(), "host": C.host_record(),
        "dependencies": {"msolve": sh("dpkg-query -W -f='${Version}' msolve"), "python_flint": sh("python3 -c 'import flint;print(flint.__version__)'"),
                         "numpy": sh("python3 -c 'import numpy;print(numpy.__version__)'"), "pyyaml": sh("python3 -c 'import yaml;print(yaml.__version__)'"),
                         "pari_gp": sh("gp --version-short 2>&1 | head -1"),
                         "cypari2": sh("python3 -c 'import importlib.metadata as m;print(m.version(\"cypari2\"))'"),
                         "valgrind": sh("valgrind --version"), "callgrind_annotate": sh("callgrind_annotate --version 2>&1 | head -1"),
                         "callgrind_annotate_path": sh("command -v callgrind_annotate"), "sage_python": C.SAGE_PYTHON},
        "PYTHONHASHSEED_set_for_driver": DRIVER_PYTHONHASHSEED,
        "GFPN_V2_CAP_BYTES_in_wrapper_environment": R.cap_env_readback(),
        "git": {"head": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
                "implementation_v2_last_commit": git("log", "-1", "--format=%H", "--", *R.V2_PATHS_REL),
                "implementation_v2_a1_last_commit": git("log", "-1", "--format=%H", "--", *R.A1_PATHS_REL),
                "implementation_v2_r5_last_commit": git("log", "-1", "--format=%H", "--", *R.R5_PATHS_REL),
                "dirty_paths": {k: v[1] for k, v in trees.items()}, "repo_dirty_paths": git("status", "--porcelain").splitlines()},
        "phase_a_commits": pac,
        "amendment_sha256": info["amendment_sha256"],
        "plan_sha256": {os.path.basename(p): R.sha256_file(p) for p in (R.PLAN_V2_R5, R.PLAN_A1_R5, R.PLAN_V2, R.PLAN_A1)},
        "ladder_json_sha256": R.sha256_file(R.LADDER_PATH),
    }
    with open(os.path.join(rd, "environment.json"), "w") as fh:
        json.dump(env_rec, fh, indent=2)
    with open(os.path.join(rd, "command.txt"), "w") as fh:
        fh.write("# cwd: %s\n# GFPN_RUN_DIR=%s\n# PYTHONDONTWRITEBYTECODE=1\n# PYTHONHASHSEED=%s (SE-6)\n# launched by: python3 -B %s %s%s (no outer guard; RB-8)\n%s\n"
                 % (R.REPO, rd, DRIVER_PYTHONHASHSEED, os.path.relpath(os.path.abspath(__file__), R.REPO), rid,
                    (" --replaces " + replaces) if replaces else "", " ".join(cmd)))
    child_env = dict(os.environ, GFPN_RUN_DIR=rd, GFPN_V2_PACKAGE=rid, GFPN_V2_REPLACES=replaces or "",
                     PYTHONHASHSEED=DRIVER_PYTHONHASHSEED, PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1")
    started = datetime.datetime.now(datetime.timezone.utc)
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        proc = subprocess.run(cmd, cwd=R.REPO, env=child_env, stdout=so, stderr=se)
    wall = time.time() - t0
    finished = datetime.datetime.now(datetime.timezone.utc)
    ru = resource.getrusage(resource.RUSAGE_CHILDREN)
    ps_path = os.path.join(rd, "pari-stack.json")
    pstack = json.load(open(ps_path)) if os.path.exists(ps_path) else None
    raw_path = os.path.join(rd, "raw-result.json")
    raw = None
    writer = "undetermined"
    if os.path.exists(raw_path):
        try:
            raw = json.load(open(raw_path))
            writer = "driver"                             # RF-0 (b): exists and parses after the driver exits
        except Exception as e:                           # noqa: BLE001
            raw = {"run_status": "failed", "failure_class": "implementation_error", "note": "raw-result.json unparseable: %r" % (e,)}
            writer = "undetermined"
    violation = consistency_flag(rd)
    if raw is None:
        note = "driver exited %s without writing raw-result.json" % proc.returncode
        fclass = "infrastructure_error"
        if pstack and pstack.get("status") == "refused_before_any_command":
            note = "the entry point refused before any command (PARI stack, redirection, SE-3, HR-3 or RL-5 read-back): %s" % pstack.get("refusal_reasons")
        elif violation:
            fclass = "implementation_error"
            note = ("the r5 layer raised on an SE-2 (4) / SF-2 (b) / HR-5 consistency violation or a recording failure "
                    "(solver-events.json); the package ends failed as implementation_error and is never a result")
        raw = {"run_status": "failed", "failure_class": fclass, "note": note}
        with open(raw_path, "w") as fh:
            json.dump(raw, fh, indent=2)
        writer = "wrapper"                                # RF-0 (b): the wrapper wrote the fallback (W-1, W-2)
        for f in ("ladder-table.yaml", "heur-dflat.yaml", "cost-band-p64.yaml"):
            with open(os.path.join(rd, f), "w") as fh:
                yaml.safe_dump({"note": "driver produced no result; see stderr.log"}, fh)
    status = raw.get("run_status", "failed")
    fclass = raw.get("failure_class")
    if proc.returncode != 0 and status == "completed_valid":
        status, fclass = "failed", fclass or "infrastructure_error"
    doc = None
    try:
        doc = json.load(open(os.path.join(rd, RS.EVENTS_FILE)))
    except Exception:                                    # noqa: BLE001
        doc = None
    acc, src = child_readback_accounting(rd, raw, doc)
    union = sorted({json.dumps(v, sort_keys=True) for vals in src.values() for v in vals if v})
    threads = sorted({v for v in threads_sources(raw, doc) if v is not None})
    wd_equal = plan["watchdogs"] == P["v2"]["watchdogs"]
    sev = solver_events_block(rd, raw)
    hs = (pstack or {}).get("python_hash_seed_driver_readback")
    man = {"run": {
        "id": rid, "experiment_id": R.EXPERIMENT_ID, "protocol_version": R.PROTOCOL_V2_R5 if which == "v2r5" else R.PROTOCOL_A1_R5,
        "amendment": {"id": R.V2_AMENDMENT_ID, "sha256": R.V2_AMENDMENT_SHA256, "approval_decision": R.V2_APPROVAL,
                      "conditions": ["AC-1", "AC-2", "AC-3", "AC-4", "AC-5", "AC-6"]},
    }}
    run = man["run"]
    if which == "a1r5":
        run["addendum"] = {"id": R.A1_ADDENDUM_ID, "sha256": R.A1_ADDENDUM_SHA256, "approval_decision": R.A1_APPROVAL,
                           "conditions": ["AA-1", "AA-2", "AA-3", "AA-4", "AA-5", "AA-6", "AA-7", "AA-8"]}
    run["repair"] = R.repair_amendments()
    run.update({
        "task_id": plan["task_id"], "hypothesis_id": R.HYPOTHESIS_ID, "heuristic_under_test": R.HEURISTIC_ID,
        "status": status, "failure_class": fclass, "claim_tier": "toy",
        "raw_result_writer": raw_result_writer(writer),
        "derived_from": inv.get(rid),
        "package": {k: pk.get(k) for k in ("order", "label", "kind", "blocking", "gate_required", "controls_a1_gate_required",
                                            "requires", "replaces", "replaced_label", "replaced_kind")},
        "code": {"commit": env_rec["git"]["head"],
                 "implementation_v2_last_commit": env_rec["git"]["implementation_v2_last_commit"],
                 "implementation_v2_a1_last_commit": env_rec["git"]["implementation_v2_a1_last_commit"],
                 "implementation_v2_r5_last_commit": env_rec["git"]["implementation_v2_r5_last_commit"],
                 "phase_a_commits": pac,
                 "implementation_v2_clean": not trees["v2"][1], "implementation_v2_a1_clean": not trees["a1"][1],
                 "implementation_v2_r5_clean": not trees["r5"][1],
                 "command": " ".join(cmd), "entry_point": os.path.relpath(entry, R.REPO),
                 "wrapper": "experiments/EXP-GFPN-05ff43/implementation-v2-r5/r5_run_wrapper.py"},
        "inference": inference_block(),
        "environment": {"operating_system": env_rec["operating_system"], "python_version": env_rec["python_version"],
                        "dependencies": env_rec["dependencies"], "PYTHONHASHSEED_set_for_driver": DRIVER_PYTHONHASHSEED,
                        "PYTHONHASHSEED_driver_readback": hs,
                        "GFPN_V2_CAP_BYTES_in_wrapper_environment": env_rec["GFPN_V2_CAP_BYTES_in_wrapper_environment"],
                        "GFPN_V2_CAP_BYTES_in_driver_environment": (pstack or {}).get("cap_env_readback")},
        "host": env_rec["host"],
        "inputs": {"seeds": raw.get("seeds"), "parameters": {k: raw.get(k) for k in ("p", "n", "m", "curve_shape", "field", "curve") if k in raw},
                   "plan_sha256": env_rec["plan_sha256"], "ladder_json_sha256": env_rec["ladder_json_sha256"], "data_source": raw.get("data_source")},
        "timing": {"started_at": started.isoformat(), "finished_at": finished.isoformat(), "wall_seconds": round(wall, 3)},
        "resources": {
            "child_rlimit_as_read_back_by_getrlimit": [json.loads(c) for c in union],
            "child_rlimit_as_requested_bytes": (raw.get("envelope") or {}).get("cap_bytes"),
            "msolve_threads_executed": threads,
            "child_readback_accounting": acc,
            "host_mem_total_kB": env_rec["host"]["mem_total_kB"], "host_swap_total_kB": env_rec["host"]["swap_total_kB"],
            "driver_and_children_maxrss_bytes_rusage": ru.ru_maxrss * 1024, "cpu_seconds_children": round(ru.ru_utime + ru.ru_stime, 3),
            "watchdogs_declared": {"package_scope": pk.get("watchdogs"), "values": plan["watchdogs"], "equal_to_trial_plan_v2": wd_equal},
            "pari_stack": pstack if pstack is not None else {"status": "absent: the entry point wrote no pari-stack.json"},
            "note": "the cap recorded is the value each child read back with getrlimit after setting it (DC-6 R-1), never a wrapper default; "
                    "the union is de-duplicated over RB-2 sources (a)-(c) and RL-3 sources (d)-(e)"},
        "solver_events": sev,
        "listing": listing(rd),
        "result": {"metrics": raw.get("metrics", {}), "valid": status == "completed_valid", "gate_pass": raw.get("gate_pass"),
                   "exit_code": proc.returncode, "certificate": raw.get("certificate") or {"kind": "none", "verified": None, "verifier": None},
                   "F3": "undecidable (AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii DC-4)"},
        "artifacts": {"raw_result": "raw-result.json", "ladder_table": "ladder-table.yaml", "heur_dflat": "heur-dflat.yaml",
                      "cost_band_p64": "cost-band-p64.yaml", "certificates_dir": "certificates/", "stdout": "stdout.log", "stderr": "stderr.log",
                      "solver_inputs": "solver/ (R-10)", "pari_stack": "pari-stack.json", "solver_events": RS.EVENTS_FILE},
    })
    gate = {}
    if info.get("reg1") is not None:
        gate["regression_REG-1"] = info["reg1"]
    if info.get("gate_package_checker"):
        gate["gate_package_checker"] = info["gate_package_checker"]
    if info.get("required_package_checker"):
        gate["required_package_checker"] = info["required_package_checker"]
    if info.get("x13_admission_values") is not None:
        gate["controls_a1_image_admission_values"] = info["x13_admission_values"]
    if info.get("reads") is not None:
        gate["reads"] = info["reads"]
    if gate:
        run["gate"] = gate
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(man, fh, sort_keys=False, width=110)   # forbidden ids are tested by r4_check_run (VA-7 (b))
    # RK-3 (b): the package's OWN verdict, the frozen checker's exit status and its output, recorded in its manifest
    _VERDICTS.pop(rid, None)
    v = checker_verdict(rid)
    run["verdict"] = {"r4_verdict": v["verdict"], "stop_classes": v["stop_classes"], "r4_checker_exit_status": v["exit_status"],
                      "frozen_checker_exit_status": v["frozen_checker_exit"], "r4_checker_command": v["command"],
                      "r4_checker_output_verbatim": v["output"]}
    with open(os.path.join(rd, "manifest.yaml"), "w") as fh:
        yaml.safe_dump(man, fh, sort_keys=False, width=110)
    print("%s: status=%s wall=%.1fs exit=%s r4_verdict=%s dir=%s" % (rid, status, wall, proc.returncode, v["verdict"], rd))
    return 0


def consistency_flag(rd):
    """SE-2 (4) / HR-5 failure classing (epsilon consistency reader; VA-6 (b)): the top-level flag of the run-root
    solver-events.json, read by constant key."""
    try:
        return bool(json.load(open(os.path.join(rd, RS.EVENTS_FILE))).get("consistency_violation"))
    except Exception:                                    # noqa: BLE001
        return False


if __name__ == "__main__":
    sys.exit(main())
