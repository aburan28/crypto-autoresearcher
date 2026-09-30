#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r2 / 2-a1-r2 -- the SE-3 RE-SOLVE WRAPPER of v2_driver.solve (new file).

Authority: AMD-EXP-GFPN-05ff43-20260924-seedresolve SF-1, SF-2, SF-3 with DEC-20260924-15a77a SC-8, SC-11, and the
incorporated solverevent SE-2 (1)-(7) and SE-3 (read with SSF in place of NSP).

install(v2_driver_module, run_dir) replaces the module attribute v2_driver.solve IN-PROCESS by `solve` below, which
calls the ORIGINAL frozen function object. Every call site of solve() -- v2_driver's own (module-global lookup) and
a1_driver's D.solve -- reaches the wrapper. readback() lets an entry verify, before any command, that the attribute is
the wrapper and that the wrapper's recorded original is the frozen function (SE-3; card ST-3 (d)).

For every call with gb_only false (SE-2; SF-2):
  * attempt 1 is the frozen solve(), unchanged;
  * an attempt has the SSF SIGNATURE (SF-1) iff its result has outcome degenerate_parametrisation with reason
    (i) "eliminating polynomial is not square-free", (ii) beginning "eliminating polynomial degree ",
    (iii) beginning "msolve reports square-free part degree ", (iv) ending "parsed solution(s) fail substitution
    into the descended system"; or (v) outcome positive_dimensional where the attempt's log text contains the exact
    string "[coefficients of linear form are randomly chosen]". The log text is .ms.log + "\\n" + .ms.err + "\\n",
    read exactly as solve() builds it (v2_driver.py lines 170-175);
  * on an SSF attempt k, while k < K + 1 = 6 and the SF-2 (c) cap allows: record the attempt (outcome, reason,
    dimension_of_quotient_printed, solution_info, input sha256, output sha256, argv, the child's getrlimit read-back,
    start and end UTC with microseconds, wall seconds), rename its solver/<tag>.ms.out, .ms.log and .ms.err by
    appending ".ssf-attempt<k>" (SC-11 (a)), wait until at least 2.0 s after its recorded end (SC-11 (d)), and call
    the frozen solve() again with IDENTICAL arguments;
  * CONSISTENCY (SE-2 (4); SF-2 (b)), checked after every attempt: input sha256 equal to attempt 1's; every printed
    quotient dimension equal; every attempt k >= 2 started at least 2.0 s after attempt k - 1's recorded end. A
    violation writes the records and RAISES SolverEventConsistencyError (the package ends failed,
    implementation_error; never a result);
  * CAP (SF-2 (c); SC-11 (c), (e)): attempt 2 always starts on an SSF attempt 1; attempt k + 1 (k >= 2) starts only if
    the summed wall seconds of attempts 2..k are below the timeout_s argument actually passed; otherwise the recorded
    result is attempt k's and the event records resolve_cap_reached;
  * the RECORDED result -- the dict returned to the frozen caller, from which raw-result.json is written -- is the
    last attempt's result object, unmodified (no new field).
NEVER (SE-2 (6)): any other outcome class, gb_only solves (passed straight through), the callgrind child (it runs
inside the frozen solve() only after an ok outcome), package re-runs, discretion, or a changed flag, input or cap.
RECORDING (SE-2 (5); SC-11 (b)): run-root solver-events.json, rewritten atomically after every wrapped call.
"""
import datetime
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402  (imports no v2 module)

RANDOM_FORM = "[coefficients of linear form are randomly chosen]"
EVENTS_FILE = "solver-events.json"
SCHEMA = "crypto.autoresearch.gfpn05.r2.solver_events.v1"
CLAUSES = ("i", "ii", "iii", "iv", "v")


class SolverEventConsistencyError(RuntimeError):
    """SE-2 (4) / SF-2 (b) violation: the package ends failed as implementation_error, never a result."""


# ----------------------------------------------------------------------------- the SSF signature (SF-1)
def ssf_clause(outcome, reason, log_text):
    if outcome == "degenerate_parametrisation" and isinstance(reason, str):
        if reason == "eliminating polynomial is not square-free":
            return "i"
        if reason.startswith("eliminating polynomial degree "):
            return "ii"
        if reason.startswith("msolve reports square-free part degree "):
            return "iii"
        if reason.endswith("parsed solution(s) fail substitution into the descended system"):
            return "iv"
    if outcome == "positive_dimensional" and RANDOM_FORM in (log_text or ""):
        return "v"
    return None


def log_text(solver_dir, tag):
    """Exactly v2_driver.solve lines 170-175."""
    text = ""
    for ext in (".ms.log", ".ms.err"):
        try:
            text += open(os.path.join(solver_dir, tag + ext), errors="replace").read() + "\n"
        except OSError:
            pass
    return text


# ----------------------------------------------------------------------------- module state
_STATE = {"installed": False, "original": None, "run_dir": None, "doc": None}


def _utc():
    return datetime.datetime.now(datetime.timezone.utc)


# Indirections used by the wrapper. They are plain functions in the delivered code; only the DV-12 development
# shim (never reachable from a delivered entry) replaces them, in its own scratch process.
def _now():
    return _utc()


def _sleep(seconds):
    time.sleep(seconds)


def _wait_spacing(prev_end):
    """SF-2 (a) / SC-11 (d): return only when at least SPACING_S has elapsed since prev_end (a recorded end UTC)."""
    while True:
        gap = (_now() - prev_end).total_seconds()
        if gap >= R.SPACING_S:
            return
        _sleep(R.SPACING_S - gap + 0.01)


def _call_original(original, args, kwargs):
    return original(*args, **kwargs)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _empty_doc():
    return {"schema": SCHEMA, "experiment_id": R.EXPERIMENT_ID,
            "authority": "%s SF-1, SF-2, SF-3 (%s SC-11); incorporated %s SE-2 (5)" % (R.SEEDRESOLVE_ID, R.SEEDRESOLVE_APPROVAL, R.SOLVEREVENT_ID),
            "K": R.K, "max_attempts_per_solve": R.K + 1, "spacing_s": R.SPACING_S, "cap_rule": R.RESOLVE_CAP_RULE,
            "rename_suffix": R.RENAME_SUFFIX.replace("%d", "<k>"),
            "counters": {"wrapped_calls_gb_only_false": 0, "passthrough_calls_gb_only_true": 0, "attempts_total": 0,
                         "ssf_attempts_by_clause": {c: 0 for c in CLAUSES}, "re_solves": 0, "solves_with_ssf_attempt": 0,
                         "solves_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0, "consistency_violations": 0},
            "consistency_violation": False, "events": [], "updated_at": None}


def _write(doc=None):
    doc = doc or _STATE["doc"]
    rd = _STATE["run_dir"]
    if rd is None:
        return
    doc["updated_at"] = R.now()
    txt = json.dumps(doc, indent=1, default=str)
    for f in R.FORBIDDEN_TASK_IDS:
        if f in txt:
            raise RuntimeError("refusing to write a forbidden task id into solver-events.json")
    path = os.path.join(rd, EVENTS_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(txt)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)                                # atomic rewrite (SE-2 (5))


def _sha(path):
    try:
        return R.sha256_file(path)
    except OSError:
        return None


def _attempt_record(k, res, start, end, clause, text):
    sol = res.get("solver") or {}
    return {"attempt": k, "outcome": res.get("outcome"), "reason": res.get("reason"),
            "dimension_of_quotient_printed": res.get("dimension_of_quotient_printed"),
            "solution_info": res.get("solution_info"), "input_sha256": (res.get("input") or {}).get("sha256"),
            "output_sha256": res.get("output_sha256"), "argv": sol.get("argv"),
            "child_rlimit_as_getrlimit": sol.get("rlimit_as_child_getrlimit"), "child_outcome": sol.get("outcome"),
            "start_utc": _iso(start), "end_utc": _iso(end), "wall_seconds": (end - start).total_seconds(),
            "ssf_clause": clause, "random_linear_form_string_in_log": RANDOM_FORM in (text or ""),
            "D": res.get("D"), "D_defined": res.get("D_defined")}


def _consistency(attempts, ends, starts):
    v = []
    a1 = attempts[0]
    for a in attempts[1:]:
        if a["input_sha256"] != a1["input_sha256"]:
            v.append("attempt %d input sha256 %s != attempt 1's %s (SE-2 (4))" % (a["attempt"], a["input_sha256"], a1["input_sha256"]))
    dims = sorted({a["dimension_of_quotient_printed"] for a in attempts if a["dimension_of_quotient_printed"] is not None})
    if len(dims) > 1:
        v.append("printed quotient dimensions differ across attempts: %s (SE-2 (4))" % dims)
    for i in range(1, len(attempts)):
        gap = (starts[i] - ends[i - 1]).total_seconds()
        if gap < R.SPACING_S:
            v.append("attempt %d started %.6f s after attempt %d's recorded end, < %.1f s (SF-2 (b); SC-11 (d))"
                     % (attempts[i]["attempt"], gap, attempts[i - 1]["attempt"], R.SPACING_S))
    return v


def _rename(solver_dir, tag, k):
    out = {}
    for ext in (".ms.out", ".ms.log", ".ms.err"):
        src = os.path.join(solver_dir, tag + ext)
        if os.path.exists(src):
            dst = src + (R.RENAME_SUFFIX % k)
            if os.path.exists(dst):
                raise SolverEventConsistencyError("rename target exists: %s" % dst)
            os.rename(src, dst)
            out[os.path.basename(dst)] = {"sha256": _sha(dst), "bytes": os.path.getsize(dst)}
        else:
            out[os.path.basename(src) + (R.RENAME_SUFFIX % k)] = {"absent": "not present after the attempt (frozen retention, v2_driver._retain)"}
    return out


# ----------------------------------------------------------------------------- the wrapper
def solve(ctx, names, eqs, tag, timeout_s, retain_input, gb_only=False, callgrind_timeout=None):
    original = _STATE["original"]
    doc = _STATE["doc"]
    args = (ctx, names, eqs, tag, timeout_s, retain_input)
    kwargs = {"gb_only": gb_only, "callgrind_timeout": callgrind_timeout}
    if gb_only:                                          # SE-2 (6): never for gb_only solves
        doc["counters"]["passthrough_calls_gb_only_true"] += 1
        res = _call_original(original, args, kwargs)
        _write()
        return res
    doc["counters"]["wrapped_calls_gb_only_false"] += 1
    sd = os.path.join(ctx.rd, "solver")
    attempts, starts, ends = [], [], []
    event = None
    k = 0
    res = None
    while True:
        k += 1
        if k >= 2:
            _wait_spacing(ends[-1])
        start = _now()
        res = _call_original(original, args, kwargs)
        end = _now()
        text = log_text(sd, tag)
        clause = ssf_clause(res.get("outcome"), res.get("reason"), text)
        rec = _attempt_record(k, res, start, end, clause, text)
        attempts.append(rec)
        starts.append(start)
        ends.append(end)
        doc["counters"]["attempts_total"] += 1
        if clause is not None:
            doc["counters"]["ssf_attempts_by_clause"][clause] += 1
            if event is None:
                event = {"tag": tag, "timeout_s": timeout_s, "retain_input": retain_input,
                         "callgrind_timeout": callgrind_timeout, "attempts": attempts, "renamed_files": {},
                         "resolve_cap_reached": False, "still_ssf_after_last_attempt": False,
                         "consistency": {"ok": True, "violations": []}}
                doc["events"].append(event)
                doc["counters"]["solves_with_ssf_attempt"] += 1
        if k >= 2:
            doc["counters"]["re_solves"] += 1
        viol = _consistency(attempts, ends, starts)
        if viol:
            event = event or {"tag": tag, "timeout_s": timeout_s, "attempts": attempts, "renamed_files": {}}
            if event not in doc["events"]:
                doc["events"].append(event)
            event["consistency"] = {"ok": False, "violations": viol}
            event["accepted_attempt"] = None
            event["final_outcome"] = None
            doc["consistency_violation"] = True
            doc["counters"]["consistency_violations"] += 1
            _write()
            raise SolverEventConsistencyError("; ".join(viol))
        if clause is None:                               # the first attempt without the SSF signature is recorded
            break
        if k >= R.K + 1:                                 # the (K + 1)-th SSF attempt keeps its frozen class
            event["still_ssf_after_last_attempt"] = True
            doc["counters"]["solves_still_ssf_after_last_attempt"] += 1
            break
        if k >= 2:
            spent = sum(a["wall_seconds"] for a in attempts[1:])      # attempts 2..k (SC-11 (c))
            if timeout_s is not None and spent >= timeout_s:          # SF-2 (c); SC-11 (e)
                event["resolve_cap_reached"] = True
                event["resolve_cap_detail"] = {"summed_wall_seconds_attempts_2_to_k": spent, "timeout_s_passed": timeout_s, "k": k}
                event["still_ssf_after_last_attempt"] = True
                doc["counters"]["resolve_cap_reached"] += 1
                doc["counters"]["solves_still_ssf_after_last_attempt"] += 1
                break
        event["renamed_files"]["attempt%d" % k] = _rename(sd, tag, k)
        _write()
    if event is not None:
        event["accepted_attempt"] = k
        event["final_outcome"] = res.get("outcome")
        event["final_reason"] = res.get("reason")
        event["final_ssf_clause"] = attempts[-1]["ssf_clause"]
        event["final_D"] = res.get("D")
    _write()
    return res


solve.__r2_resolve_wrapper__ = True


# ----------------------------------------------------------------------------- install / read-back (SE-3)
def install(v2_driver_module, run_dir):
    """Replace v2_driver.solve by the wrapper (SE-3). Records the ORIGINAL function object. Writes nothing: the
    initial solver-events.json is written by begin(), which the entry calls only after every read-back passed."""
    if _STATE["installed"]:
        raise RuntimeError("r2_resolve.install called twice")
    orig = v2_driver_module.solve
    _STATE.update(installed=True, original=orig, run_dir=run_dir, doc=_empty_doc(),
                  original_identity={"module": getattr(orig, "__module__", None), "qualname": getattr(orig, "__qualname__", None),
                                     "code_file": getattr(getattr(orig, "__code__", None), "co_filename", None),
                                     "code_firstlineno": getattr(getattr(orig, "__code__", None), "co_firstlineno", None)})
    solve.__r2_original__ = orig
    v2_driver_module.solve = solve
    return _STATE["original_identity"]


def begin():
    """Write the initial run-root solver-events.json (no events), immediately before dispatch, so that it exists and
    parses even if no solve() runs (SE-4: REG-1 fails if it is missing)."""
    _write()


def readback(v2_driver_module):
    """SE-3 read-back: the attribute is the wrapper; the wrapper's recorded original is the frozen function object
    defined in implementation-v2/v2_driver.py (module v2_driver, qualname solve, line 158)."""
    reasons = []
    attr = getattr(v2_driver_module, "solve", None)
    is_wrapper = attr is solve and getattr(attr, "__r2_resolve_wrapper__", False) is True
    orig = getattr(solve, "__r2_original__", None)
    code = getattr(orig, "__code__", None)
    frozen_file = os.path.join(R.V2_DIR, "v2_driver.py")
    orig_ok = (orig is not None and orig is _STATE.get("original") and getattr(orig, "__module__", None) == "v2_driver"
               and getattr(orig, "__qualname__", None) == "solve" and code is not None
               and os.path.abspath(code.co_filename) == os.path.abspath(frozen_file)
               and getattr(orig, "__r2_resolve_wrapper__", False) is not True)
    if not is_wrapper:
        reasons.append("SE-3 read-back: v2_driver.solve is not the r2 re-solve wrapper")
    if not orig_ok:
        reasons.append("SE-3 read-back: the wrapper's recorded original is not the frozen v2_driver.solve")
    rec = {"v2_driver.solve_is_r2_wrapper": is_wrapper, "wrapper_original_is_frozen_v2_driver_solve": orig_ok,
           "original_identity": {"module": getattr(orig, "__module__", None), "qualname": getattr(orig, "__qualname__", None),
                                 "code_file": os.path.relpath(code.co_filename, R.REPO) if code is not None else None,
                                 "code_firstlineno": code.co_firstlineno if code is not None else None},
           "frozen_file_sha256": R.sha256_file(frozen_file), "K": R.K, "spacing_s": R.SPACING_S}
    return rec, reasons
