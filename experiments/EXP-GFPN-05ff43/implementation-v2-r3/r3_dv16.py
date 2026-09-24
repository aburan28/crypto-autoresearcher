#!/usr/bin/env python3
"""EXP-GFPN-05ff43 r3 successor stage -- DV-16 (healthresolve HR-9, as launchcover and consumercover incorporate it;
card R3S-9): the HR-3 health re-solve path, FORCED, in a scratch toy copy through a development shim that no delivered
entry can reach. Development only. New file (the case runner is r3_dv12.run_cases; the toy environment is DV-7's).

Called as `python3 -B r3_devchecks.py dv16 --out DIR DV7_TOY_DIR`. Everything it writes goes under DIR.

TOY PRIME, declared in implementation-v2-r3.md before this check runs: p' = 1021 (the DV-7 addendum-role toy rung;
never 4111, 262151, 16777291 or 1073741831). The package is DV-7's toy copy of the addendum's controls_a1 package
(`controls-a1 --p 1021`), run by the DELIVERED r3_run_wrapper.main and the DELIVERED r3_entry_a1.py through the shim
below; each case has its own scratch runs directory, holding byte copies of DV-7's world-A toy gate packages (R-7), with
REG-1 evaluated against DV-7's world-B toy G1 exactly as in the DV-7 lineage. PYTHONHASHSEED is the delivered "0".
Declared forced system: the first draw of pattern (2, 2, 2), run_system tag health_p1021_d222.
Cases (HR-9 DV-16):
  U   unforced (the reference for (a));
  (a) attempt 1 forced to SSF clause (ii)                  -> the recorded result must equal U's (pass, checks, D);
  (b) all K + 1 attempts forced SSF                        -> the recorded result is the (K + 1)-th, and the frozen seed-':2'
                                                              re-draw then runs, itself wrapped, exactly as frozen;
  (c) an input-sha mismatch forced (attempt 2)             -> the package ends failed as implementation_error;
  (d) wall times shimmed so that the HR-6 cap binds after attempt 2 -> the recorded result is attempt 2's, with
                                                              resolve_cap_reached;
  (e) attempt 2 forced to start less than 2 s after attempt 1's end -> the package ends failed.
A FORCED attempt is a real frozen run_system() whose returned result dict the shim rewrites after the call. Each forcing
is logged, with the real result, in DIR/<case>/shim-log.jsonl.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_common as R                                    # noqa: E402
import r3_dv7 as T                                       # noqa: E402  (development only)
import r3_dv12 as D12                                    # noqa: E402  (the case runner; development only)

TOY_P = 1021
TARGET_TAG = "health_p1021_d222"
CASES = ["U", "a", "b", "c", "d", "e"]

FORCING = r'''
# ---- DV-16 forcing (HR-9 (a)-(e)) on the r3_resolve indirections, at a1_health.run_system (development only)
CASE = os.environ.get("R3_FORCE_CASE") or "U"
SHIMLOG = CFG["shim_log"]
TARGET = CFG["target_tag"]
OFFSET = [datetime.timedelta(0)]
calls = {}
def slog(rec):
    with open(SHIMLOG, "a") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
if CASE != "U":
    _inner = RS._call_original
    def forced(original, args, kwargs):
        tag = args[3]
        if tag != TARGET or getattr(original, "__name__", "") != "run_system":
            return _inner(original, args, kwargs)
        k = calls[tag] = calls.get(tag, 0) + 1
        res = _inner(original, args, kwargs)
        out_dir = args[4]
        osha = None
        try:
            import hashlib
            osha = hashlib.sha256(open(os.path.join(out_dir, tag + ".ms.out"), "rb").read()).hexdigest()
        except OSError:
            pass
        real = {"v2_outcome_class": res.get("v2_outcome_class"), "v2_outcome_reason": res.get("v2_outcome_reason"), "pass": res.get("pass"),
                "D": res.get("dimension_of_quotient_printed"), "output_sha256": osha, "nvars": 3, "p": res.get("p")}
        force = (CASE in ("a", "c", "e") and k == 1) or CASE in ("b", "d")
        if force:
            si = res.get("solution_info") or {}
            res["v2_outcome_class"] = "degenerate_parametrisation"
            res["v2_outcome_reason"] = ("eliminating polynomial degree %s != quotient dimension %s (DV-16 FORCED by the development shim)"
                                        % (si.get("elim_degree"), res.get("dimension_of_quotient_printed")))
            res["pass"] = False
        if CASE == "c" and k == 2:
            res["input"]["sha256"] = "0" * 64
        if CASE == "d" and k == 2:
            OFFSET[0] += datetime.timedelta(seconds=float(RS._STATE["health_module"].DEV_TIMEOUT_S) + 1.0)
        slog({"case": CASE, "site": "a1_health.run_system", "tag": tag, "attempt": k, "forced": force, "clause_forced": "ii" if force else None,
              "real_result": real, "recorded_as": {"v2_outcome_class": res.get("v2_outcome_class"), "pass": res.get("pass")},
              "input_sha_forced": CASE == "c" and k == 2, "clock_offset_s": OFFSET[0].total_seconds()})
        return res
    RS._call_original = forced
    if CASE == "d":
        RS._now = lambda: RS._utc() + OFFSET[0]
    if CASE == "e":
        RS._wait_spacing = lambda prev_end: slog({"case": CASE, "wait_spacing_shimmed_away_after": str(prev_end)})
'''


def s2_events(doc):
    return ((doc or {}).get("sites") or {}).get(R.SITE_S2, {}).get("events") or []


def health_entry(rd, pattern):
    hp = os.path.join(rd, "health", "health-%d.json" % TOY_P)
    if not os.path.exists(hp):
        return None, None
    rep = json.load(open(hp))
    e = next((x for x in rep.get("systems") or [] if x.get("pattern") == pattern), None)
    return e, rep


def dv16(out, rest):
    os.makedirs(out, exist_ok=True)
    toy_dir = rest[0]
    cases = [c for c in CASES if len(rest) < 2 or c in rest[1:]]
    worldA = os.path.join(toy_dir, "world_A", "exp", "runs")
    worldB = os.path.join(toy_dir, "world_B", "exp", "runs")

    def prereq(env):
        G = R.load_json(env["plan_v2r3"])["gate"]["blocking_packages"]
        return [(os.path.join(worldA, g), g) for g in G]

    def extract(rd, raw, sev):
        e, rep = health_entry(rd, [2, 2, 2])
        ev = [x for x in s2_events(sev) if x.get("tag") == TARGET_TAG]
        s2c = (((sev or {}).get("sites") or {}).get(R.SITE_S2) or {}).get("counters")
        first = (e or {}).get("first") or {}
        chk_d = next((c for c in (raw or {}).get("checks") or [] if c.get("check") == "d_msolve_characteristic_check_synthetic"), None)
        hd = os.path.join(rd, "health")
        tp = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(rd))), "trace.jsonl")
        tr = [json.loads(l) for l in open(tp)] if os.path.exists(tp) else []
        wrapped = {}
        for t in tr:
            if t.get("event") == "original_call_end" and t.get("site") == R.SITE_S2:
                wrapped[t.get("tag")] = wrapped.get(t.get("tag"), 0) + 1
        return {"wrapped_original_calls_by_tag_S2": wrapped, "target_event": ev[0] if ev else None, "s2_counters": s2c, "s2_event_tags": [x.get("tag") for x in s2_events(sev)],
                "health_first_222": {"pass": first.get("pass"), "checks": first.get("checks"), "D": first.get("dimension_of_quotient_printed"),
                                     "v2_outcome_class": first.get("v2_outcome_class"), "tag": first.get("tag")} if e else None,
                "health_retry_seed2_222": {k: ((e or {}).get("retry_seed2") or {}).get(k) for k in ("tag", "pass", "v2_outcome_class", "dimension_of_quotient_printed")} if e and e.get("retry_seed2") else None,
                "health_pattern_pass_222": (e or {}).get("pattern_pass"), "health_overall_pass": (rep or {}).get("pass"),
                "controls_a1_check_d": chk_d and chk_d.get("pass"),
                "renamed_files": sorted(x for x in os.listdir(hd) if ".ssf-attempt" in x) if os.path.isdir(hd) else []}
    rep = {"extract": extract, "prerequisites": prereq, "reg_runs": worldB,
           "reg_receipt": os.path.join(toy_dir, "toy-reference-receipt-worldB-G1.json"),
           "receipt_b": os.path.join(toy_dir, "toy-f1fb0e-post-run-receipt.json"),
           "brief": lambda r: "health_first=%s retry=%s events=%s" % (r.get("health_first_222") and {k: r["health_first_222"][k] for k in ("pass", "D", "v2_outcome_class")},
                                                                     r.get("health_retry_seed2_222"), r.get("s2_event_tags"))}
    # DV-16 attempt 2 fix: the in-process wrapper's REG-1 reference is the toy G1 (same id in the toy and the real r3 plan);
    # run_cases sets it only in the child configuration, and DV-12's G1 packages never evaluate REG-1
    R.REG1_REFERENCE_RUN = R.load_json(T.Toy(toy_dir).load()["plan_v2r3"])["gate"]["blocking_packages"][0]
    report = D12.run_cases(out, toy_dir, cases, FORCING, "entry_a1_dv16.py", TARGET_TAG,
                           lambda env: R.load_json(env["plan_a1r3"])["gate"]["addendum_blocking_package"], "a1", rep)
    report["toy_prime"] = TOY_P
    return evaluate(out, report)


def evaluate(out, report):
    cs = report["cases"]
    res = {}
    U = cs.get("U") or {}
    c = cs.get("a")
    if c:
        ev = c["target_event"] or {}
        uf, cf = U.get("health_first_222") or {}, c.get("health_first_222") or {}
        chk = {"attempt1_ssf_clause_ii": (ev.get("attempts") or [{}])[0].get("ssf_clause") == "ii",
               "re_solved": len(ev.get("attempts") or []) >= 2,
               "renamed_attempt1_files": all(f in c["renamed_files"] for f in (TARGET_TAG + ".ms.out.ssf-attempt1", TARGET_TAG + ".ms.log.ssf-attempt1", TARGET_TAG + ".ms.err.ssf-attempt1")),
               "spacing_ge_2s": all(g >= 2.0 for g in D12.spacing(ev)) if ev else False,
               "recorded_equals_U_pass_checks_D": bool(uf) and (cf.get("pass"), cf.get("checks"), cf.get("D")) == (uf.get("pass"), uf.get("checks"), uf.get("D")),
               "no_seed2_redraw": c.get("health_retry_seed2_222") is None,
               "package_completed_as_U": (c["status"], c["gate_pass"]) == (U.get("status"), U.get("gate_pass"))}
        res["a"] = {"checks": chk, "pass": all(chk.values()), "spacing_s": D12.spacing(ev) if ev else None}
    c = cs.get("b")
    if c:
        ev = c["target_event"] or {}
        cf = c.get("health_first_222") or {}
        rs = c.get("health_retry_seed2_222") or {}
        chk = {"six_attempts": len(ev.get("attempts") or []) == R.K + 1,
               "all_clause_ii": bool(ev) and all(a.get("ssf_clause") == "ii" for a in ev.get("attempts") or []),
               "still_ssf_after_last_attempt": ev.get("still_ssf_after_last_attempt") is True and ev.get("accepted_attempt") == R.K + 1,
               "recorded_is_the_6th_forced_result": cf.get("v2_outcome_class") == "degenerate_parametrisation" and cf.get("pass") is False,
               "frozen_seed2_redraw_ran": rs.get("tag") == TARGET_TAG + "_seed2",
               "seed2_redraw_itself_wrapped": (c.get("wrapped_original_calls_by_tag_S2") or {}).get(TARGET_TAG + "_seed2", 0) >= 1
                                              and (c.get("s2_counters") or {}).get("wrapped_calls") == 3,
               "renamed_attempts_1_to_5": all((TARGET_TAG + ".ms.out.ssf-attempt%d" % k) in c["renamed_files"] for k in range(1, 6)),
               "spacing_ge_2s": all(g >= 2.0 for g in D12.spacing(ev)) if ev else False}
        res["b"] = {"checks": chk, "pass": all(chk.values()), "retry_seed2": rs, "s2_counters": c.get("s2_counters"),
                    "package": [c["status"], c["failure_class"], c["gate_pass"]]}
    for case, needle in (("c", "input sha256"), ("e", "s after attempt 1's recorded end")):
        c = cs.get(case)
        if not c:
            continue
        ev = c["target_event"] or {}
        viol = (ev.get("consistency") or {}).get("violations") or []
        chk = {"package_failed": c["status"] == "failed", "implementation_error": c["failure_class"] == "implementation_error",
               "violation_recorded": any(needle in v for v in viol),
               "manifest_block_records_violation": ((c["solver_events_block"] or {}).get("consistency_violation") is True)}
        res[case] = {"checks": chk, "pass": all(chk.values()), "violations": viol}
    c = cs.get("d")
    if c:
        ev = c["target_event"] or {}
        cf = c.get("health_first_222") or {}
        b2 = ((c["solver_events_block"] or {}).get("sites") or {}).get(R.SITE_S2) or {}
        chk = {"two_attempts": len(ev.get("attempts") or []) == 2, "resolve_cap_reached": ev.get("resolve_cap_reached") is True,
               "recorded_is_attempt2": ev.get("accepted_attempt") == 2 and cf.get("v2_outcome_class") == "degenerate_parametrisation",
               "cap_compared_with_DEV_TIMEOUT_S_1800": (ev.get("resolve_cap_detail") or {}).get("timeout_s") == 1800,
               "manifest_block_counts_cap": (b2.get("resolve_cap_reached") or 0) >= 1}
        res["d"] = {"checks": chk, "pass": all(chk.values()), "cap_detail": ev.get("resolve_cap_detail"), "retry_seed2": c.get("health_retry_seed2_222")}
    report["evaluation"] = res
    report["all_cases_pass"] = all(v["pass"] for v in res.values()) and len(res) == 5 and U.get("status") is not None
    report["STOP"] = None if report["all_cases_pass"] else "HR-9: a DV-16 case failed: %s" % sorted(k for k, v in res.items() if not v["pass"])
    T.dump(os.path.join(out, "dv16.json"), report)
    for k in sorted(res):
        print("  DV-16 (%s): %s %s" % (k, "PASS" if res[k]["pass"] else "FAIL", json.dumps(res[k]["checks"])))
    print("DV-16:", "PASS" if report["all_cases_pass"] else "FAIL/STOP")
    return 0 if report["all_cases_pass"] else 3
