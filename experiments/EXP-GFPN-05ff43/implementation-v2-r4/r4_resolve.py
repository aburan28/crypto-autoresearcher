#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r4 / 2-a1-r4 -- the two RE-SOLVE WRAPPERS, their per-attempt RECORDING, the pass-through
records, the callgrind-site RECORDING, and the layer's SINGLE EVENT WRITER.
Started from implementation-v2-r3/r3_resolve.py (see implementation-v2-r4.md, file table).

Authority: solverevent SE-2 (1)-(7) and SE-3 (incorporated, read with SSF in place of NSP); seedresolve SF-1, SF-2,
SF-3 with DEC-20260924-15a77a SC-11; healthresolve HR-1..HR-8; launchcover CG-2, CG-3; consumercover CC-4; valueclose
VC-1 (a), (b); DEC-20260924-e52eec VA-6, VA-7 (c), VA-8; readbackcover RB-1 (a)-(d) with launchkind RJ-1 (a) adding
RB-1 (e) at S-1, read with DEC-20260924-daf670 LKA-9; readbackfull RL-2; the launch records of readbackfull RL-1 are
written through this module's single event writer (r4_recorder.py).

S-1 (install): replaces the module attribute v2_driver.solve IN-PROCESS by `solve` below (SE-3), which calls the
    ORIGINAL frozen function object with identical arguments. Both entries.
S-2 (install_health): replaces the module attribute a1_health.run_system IN-PROCESS by `run_system` below (HR-3),
    which calls the ORIGINAL frozen function object with identical arguments. a1 entry only, after `import a1_driver`.
S-3: NOT re-solved (CG-2). After every call of the ORIGINAL solve() whose result carries instructions_callgrind, the
    CG-3 fields (with CC-4) are RECORDED under site "v2_driver.solve/callgrind". Recording only: it triggers nothing
    (VA-6 (c)).

The bounded re-solve rule is UNCHANGED from r3 (HR-1): attempt 1 is the frozen call; an attempt with the SSF SIGNATURE
(SF-1 (i)-(v); HR-2), while fewer than K + 1 = 6 attempts were made and the cap allows (SF-2 (c) with SC-11 (c), (e);
HR-6), is recorded, its <tag>.ms.out / .ms.log / .ms.err renamed by appending ".ssf-attempt<k>" (SC-11 (a); HR-4 (b)),
and after at least 2.0 s from its recorded end (SC-11 (d)) the frozen function is called again with identical
arguments. CONSISTENCY (SE-2 (4); SF-2 (b); HR-5) after every attempt; a violation writes the records and RAISES (the
package ends failed as implementation_error, never a result). The RECORDED result is the last attempt's result object,
returned UNMODIFIED to the frozen caller. NEVER (SE-2 (6)): another class, gb_only solves (passed through), the
callgrind child, package re-runs, discretion, or a changed flag, input or cap.

RB-1 (r4): EVERY attempt of EVERY wrapped call at S-1 and S-2 gets an ATTEMPT RECORD in its site's `attempt_records`
list (in call order; at an event tag the event's `attempts` list holds the same records), carrying under `rb1`, copied
from the result the frozen function RETURNED for that attempt and from nothing else: (a) the tag and whether
<tag>.ms.out is retained under its original name (the recorded attempt) or renamed (.ssf-attempt<k>); (b) the child's
RLIMIT_AS read-back pair (S-1 result["solver"]["rlimit_as_child_getrlimit"]; S-2 result["child"]
["rlimit_as_child_getrlimit"]) or the literal "absent"; (c) threads executed (result["threads_executed"]) or "absent";
(d) the frozen outcome class; and at S-1 only (e) callgrind_result_present, the KEY-MEMBERSHIP test
"instructions_callgrind" in the returned mapping (LKA-9: no value inside it, no CG-3 field, no V-5 record and no
callgrind-site count is read). RL-2: every call reaching the SE-3 entry with gb_only true gets a PASS-THROUGH RECORD
under `passthrough_records` with RB-1 (a)-(d); it is not an attempt record. It RECORDS ONLY: no value selects a
result, triggers a re-solve, or changes a class. A recording failure is an SE-2 (4) consistency violation.

RECORDING: run-root solver-events.json, rewritten atomically (write, fsync, rename) by `_write`, the layer's single
event writer, after every wrapped call, attempt, pass-through call, callgrind record and launch record. The event-record
writer carries NO substring guard over the serialized record (VA-7 (c)).
"""
import datetime
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_common as R                                    # noqa: E402  (imports no v2 / v2-a1 module)

RANDOM_FORM = "[coefficients of linear form are randomly chosen]"
EVENTS_FILE = "solver-events.json"
SCHEMA = "crypto.autoresearch.gfpn05.r4.solver_events.v1"
CLAUSES = ("i", "ii", "iii", "iv", "v")
CONSISTENCY_MESSAGE = ("SE-2 (4) / SF-2 (b) / HR-5 consistency violation at site %s; the violations are recorded in the "
                       "run-root solver-events.json")
RECORDING_FAILURE_MESSAGE = ("SE-2 (4) consistency violation: a recording failure (RB-1 / RL-1 / RL-2); recorded in the "
                             "run-root solver-events.json where it could still be written")
# CG-3 REG-1-compared callgrind fields (launchcover definitions: every key of an instructions_callgrind record and of its
# child mapping that X14-X17 do not remove).
CG_RECORD_KEYS = ("method", "label", "reason", "f4_core_function", "f4_core_note")
CG_CHILD_KEYS = ("outcome", "returncode", "rlimit_as_child_getrlimit")
MS_OUT_ORIGINAL = "retained under its original name (the recorded attempt)"
MS_OUT_RENAMED = "renamed (%s)"


class SolverEventConsistencyError(RuntimeError):
    """SE-2 (4) / SF-2 (b) / HR-5 violation, or a recording failure: the package ends failed as implementation_error,
    never a result. The message names the site only; the violations are recorded in solver-events.json (VA-7 (b):
    stderr.log carries no site value written by the layer)."""


# ----------------------------------------------------------------------------- the SSF signature (SF-1; HR-2)
def ssf_clause(outcome, reason, log_text):
    """SF-1 (i)-(v), applied unchanged at S-1 (outcome, reason) and at S-2 (v2_outcome_class, v2_outcome_reason)."""
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


def log_text(file_dir, tag):
    """<tag>.ms.log + "\\n" + <tag>.ms.err + "\\n", exactly as v2_driver.py lines 170-175 and a1_health.py lines
    157-162 build it (SF-1 (v); HR-2 (v))."""
    text = ""
    for ext in (".ms.log", ".ms.err"):
        try:
            text += open(os.path.join(file_dir, tag + ext), errors="replace").read() + "\n"
        except OSError:
            pass
    return text


# ----------------------------------------------------------------------------- module state
_STATE = {"installed": False, "original": None, "health_installed": False, "health_original": None,
          "health_module": None, "v2_solver": None, "run_dir": None, "doc": None, "calls": {R.SITE_S1: 0, R.SITE_S2: 0}}


def _utc():
    return datetime.datetime.now(datetime.timezone.utc)


# Indirections used by the wrappers. They are plain functions in the delivered code; only a development shim (never
# reachable from a delivered entry) replaces them, in its own scratch process.
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


def _site_counters(with_passthrough):
    c = {"wrapped_calls": 0, "attempts_total": 0, "ssf_attempts_by_clause": {x: 0 for x in CLAUSES}, "re_solves": 0,
         "calls_with_ssf_attempt": 0, "calls_still_ssf_after_last_attempt": 0, "resolve_cap_reached": 0,
         "consistency_violations": 0}
    if with_passthrough:
        c["passthrough_calls_gb_only_true"] = 0
    return c


def _empty_doc():
    return {"schema": SCHEMA, "experiment_id": R.EXPERIMENT_ID,
            "authority": ("%s SF-1, SF-2, SF-3 (%s SC-11); incorporated %s SE-2 (5); %s HR-1..HR-8; %s CG-3; %s CC-4; "
                          "%s VC-1; %s VA-6, VA-7, VA-8; readbackcover RB-1 with launchkind RJ-1 (a) (RB-1 (e) at S-1; %s LKA-9); "
                          "readbackfull RL-1, RL-2; readbackclose RK-1; failclosed RF-1; childend RG-1, RG-4 (a)"
                          % (R.SEEDRESOLVE_ID, R.SEEDRESOLVE_APPROVAL, R.SOLVEREVENT_ID, R.HEALTHRESOLVE_ID, R.LAUNCHCOVER_ID,
                             R.CONSUMERCOVER_ID, R.VALUECLOSE_ID, R.VALUECLOSE_APPROVAL, R.LAUNCHKIND_APPROVAL)),
            "K": R.K, "max_attempts_per_call": R.K + 1, "spacing_s": R.SPACING_S, "cap_rule": R.RESOLVE_CAP_RULE,
            "rename_suffix": R.RENAME_SUFFIX.replace("%d", "<k>"),
            "sites": {
                R.SITE_S1: {"disposition": "WRAPPED BY SE-3", "counters": _site_counters(True), "events": [],
                            "attempt_records": [], "passthrough_records": []},
                R.SITE_S2: {"disposition": "WRAPPED BY HR-3", "counters": _site_counters(False), "events": [],
                            "attempt_records": []},
                R.SITE_S3: {"disposition": "NOT RE-SOLVED (CG-2); RECORDED ONLY (CG-3, CC-4); triggers nothing (VA-6 (c))",
                            "counters": {"callgrind_children_observed": 0, "with_log_visible_ssf_indicator": 0,
                                         "with_quotient_dimension_mismatch": 0, "with_readback_differing_from_requested_cap": 0},
                            "records": []}},
            "launch_records": [],
            "recording_failures": [],
            "consistency_violation": False, "updated_at": None}


def _write():
    """SE-2 (5) / HR-8 / CG-3 / RB-1 / RL-1 / RL-2 recording: atomic rewrite of the run-root solver-events.json (the
    layer's single event writer). No guard (VA-7 (c))."""
    doc = _STATE["doc"]
    rd = _STATE["run_dir"]
    if rd is None or doc is None:
        return
    doc["updated_at"] = R.now()
    txt = json.dumps(doc, indent=1, default=str)
    path = os.path.join(rd, EVENTS_FILE)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        fh.write(txt)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _recording_failure(where, exc):
    """RB-1 / RL-1 / RL-2: a recording failure is an SE-2 (4) consistency violation. Records what it can, then raises
    SolverEventConsistencyError (the package ends failed as implementation_error, never a result)."""
    doc = _STATE["doc"]
    if doc is not None:
        doc["consistency_violation"] = True
        doc["recording_failures"].append({"where": where, "exception_type": type(exc).__name__, "at": R.now()})
        try:
            _write()
        except Exception:                                # noqa: BLE001
            pass
    raise SolverEventConsistencyError(RECORDING_FAILURE_MESSAGE) from exc


def append_launch_record(rec):
    """RL-1 (c): append one launch record under the top-level key launch_records, in call order, and make it durable
    (the single event writer) before the recorder returns. Called only by r4_recorder.launch_recorder."""
    doc = _STATE["doc"]
    if doc is None:
        raise RuntimeError("no solver-events record: the recorder was installed without the event writer")
    doc["launch_records"].append(rec)
    _write()


def _sha(path):
    try:
        return R.sha256_file(path)
    except OSError:
        return None


# ----------------------------------------------------------------------------- RB-1 fields (gamma; clause RB-1 (a)-(e))
def _rb1_pair(mapping, key):
    """RB-1 (b): the RLIMIT_AS read-back pair where the frozen result carries it, else the literal "absent"."""
    v = (mapping or {}).get(key) if isinstance(mapping, dict) else None
    return v if isinstance(v, dict) else "absent"


def _rb1_callgrind_result_present(res):
    """RB-1 (e) at S-1, EXACTLY as DEC-20260924-daf670 LKA-9 words it: the result of a key-membership test
    ("instructions_callgrind" in the mapping the frozen solve RETURNED for that attempt), computed before the unmodified
    result is returned and from nothing else. It reads no value inside res["instructions_callgrind"], no CG-3 field, no
    V-5 record and no callgrind-site count."""
    return "instructions_callgrind" in res


def _rb1_s1(res, tag):
    """RB-1 (a)-(e) at S-1, copied from the result the frozen solve() RETURNED for this attempt."""
    return {"tag": tag, "ms_out": MS_OUT_ORIGINAL,
            "rlimit_as_child_getrlimit": _rb1_pair(res.get("solver"), "rlimit_as_child_getrlimit"),
            "threads_executed": res["threads_executed"] if res.get("threads_executed") is not None else "absent",
            "outcome_class": res.get("outcome"),
            "callgrind_result_present": _rb1_callgrind_result_present(res)}


def _rb1_s2(res, tag):
    """RB-1 (a)-(d) at S-2, copied from the result the frozen run_system() RETURNED for this attempt (the field paths
    the read-back census finds: result["child"]["rlimit_as_child_getrlimit"], result["threads_executed"])."""
    return {"tag": tag, "ms_out": MS_OUT_ORIGINAL,
            "rlimit_as_child_getrlimit": _rb1_pair(res.get("child"), "rlimit_as_child_getrlimit"),
            "threads_executed": res["threads_executed"] if res.get("threads_executed") is not None else "absent",
            "outcome_class": res.get("v2_outcome_class")}


def _passthrough_record(res, tag, call_index):
    """RL-2: RB-1 (a)-(d) of a gb_only call, copied from the result the frozen solve() returned."""
    return {"site": R.SITE_S1, "call_index": call_index, "tag": tag, "gb_only": True,
            "rb1": {"tag": res.get("tag", tag),
                    "ms_out": {"output_retained": res["output_retained"] if "output_retained" in res else "absent"},
                    "rlimit_as_child_getrlimit": _rb1_pair(res.get("solver"), "rlimit_as_child_getrlimit"),
                    "threads_executed": res["threads_executed"] if res.get("threads_executed") is not None else "absent",
                    "outcome_class": res.get("outcome")}}


# ----------------------------------------------------------------------------- attempt records (SE-2 (2)(a); HR-4 (a); RB-1)
def _attempt_record_s1(k, res, start, end, clause, text, tag, call_index):
    """SE-2 (2)(a) with SC-11 (c); RB-1 (a)-(e): the S-1 attempt record."""
    sol = res.get("solver") or {}
    return {"site": R.SITE_S1, "call_index": call_index, "tag": tag, "attempt": k,
            "outcome": res.get("outcome"), "reason": res.get("reason"),
            "dimension_of_quotient_printed": res.get("dimension_of_quotient_printed"),
            "solution_info": res.get("solution_info"), "input_sha256": (res.get("input") or {}).get("sha256"),
            "output_sha256": res.get("output_sha256"), "argv": sol.get("argv"),
            "child_rlimit_as_getrlimit": sol.get("rlimit_as_child_getrlimit"), "child_outcome": sol.get("outcome"),
            "start_utc": _iso(start), "end_utc": _iso(end), "wall_seconds": (end - start).total_seconds(),
            "ssf_clause": clause, "random_linear_form_string_in_log": RANDOM_FORM in (text or ""),
            "D": res.get("D"), "D_defined": res.get("D_defined"),
            "rb1": _rb1_s1(res, tag)}


def _attempt_record_s2(k, res, start, end, clause, text, out_dir, tag, call_index):
    """HR-4 (a); RB-1 (a)-(d): the S-2 attempt record."""
    child = res.get("child") or {}
    return {"site": R.SITE_S2, "call_index": call_index, "attempt": k, "tag": tag, "p": res.get("p"), "pattern": res.get("degrees"),
            "v2_outcome_class": res.get("v2_outcome_class"), "v2_outcome_reason": res.get("v2_outcome_reason"),
            "dimension_of_quotient_printed": res.get("dimension_of_quotient_printed"),
            "solution_info": res.get("solution_info"), "input_sha256": (res.get("input") or {}).get("sha256"),
            "output_sha256": _sha(os.path.join(out_dir, tag + ".ms.out")), "command": res.get("command"),
            "child_rlimit_as_getrlimit": child.get("rlimit_as_child_getrlimit"), "checks": res.get("checks"),
            "pass": res.get("pass"), "start_utc": _iso(start), "end_utc": _iso(end),
            "wall_seconds": (end - start).total_seconds(), "ssf_clause": clause,
            "random_linear_form_string_in_log": RANDOM_FORM in (text or ""),
            "rb1": _rb1_s2(res, tag)}


# ----------------------------------------------------------------------------- consistency, rename, cap
def _consistency(attempts, ends, starts):
    """SE-2 (4) with SF-2 (b) and SC-11 (d); HR-5: returns the violations (recorded verbatim in the event)."""
    v = []
    a1 = attempts[0]
    for a in attempts[1:]:
        if a["input_sha256"] != a1["input_sha256"]:
            v.append("attempt %d input sha256 %s != attempt 1's %s (SE-2 (4); HR-5)" % (a["attempt"], a["input_sha256"], a1["input_sha256"]))
    dims = sorted({a["dimension_of_quotient_printed"] for a in attempts if a["dimension_of_quotient_printed"] is not None})
    if len(dims) > 1:
        v.append("printed quotient dimensions differ across attempts: %s (SE-2 (4); HR-5)" % dims)
    for i in range(1, len(attempts)):
        gap = (starts[i] - ends[i - 1]).total_seconds()
        if gap < R.SPACING_S:
            v.append("attempt %d started %.6f s after attempt %d's recorded end, < %.1f s (SF-2 (b); SC-11 (d); HR-5)"
                     % (attempts[i]["attempt"], gap, attempts[i - 1]["attempt"], R.SPACING_S))
    return v


def _rename(file_dir, tag, k):
    """SE-2 (2)(b) with SC-11 (a); HR-4 (b): append ".ssf-attempt<k>" to the full names of the attempt's three files,
    recording each renamed file's sha256 and size. A pre-existing rename target is a consistency failure."""
    out = {}
    for ext in (".ms.out", ".ms.log", ".ms.err"):
        src = os.path.join(file_dir, tag + ext)
        if os.path.exists(src):
            dst = src + (R.RENAME_SUFFIX % k)
            if os.path.exists(dst):
                raise SolverEventConsistencyError("SE-2 (2)(b) rename target exists: %s" % os.path.basename(dst))
            os.rename(src, dst)
            out[os.path.basename(dst)] = {"sha256": _sha(dst), "bytes": os.path.getsize(dst)}
        else:
            out[os.path.basename(src) + (R.RENAME_SUFFIX % k)] = {"absent": "not present after the attempt (frozen retention)"}
    return out


def _cap_reached(attempts, timeout):
    """SF-2 (c) with SC-11 (c), (e); HR-6: True when the summed wall seconds of attempts 2..k reach the call's timeout."""
    spent = sum(a["wall_seconds"] for a in attempts[1:])
    return (timeout is not None and spent >= timeout), spent


# ----------------------------------------------------------------------------- the bounded loop (both sites; HR-1)
def _bounded(site, original, args, kwargs, tag, file_dir, timeout, outcome_key, reason_key, make_record, after_call, event_head):
    """SE-2 (1)-(5) with SF-1..SF-3 and SC-11; at S-2 the same rule as HR-1..HR-6 state it; RB-1 recording."""
    doc = _STATE["doc"]
    sec = doc["sites"][site]
    cnt = sec["counters"]
    cnt["wrapped_calls"] += 1
    _STATE["calls"][site] += 1
    call_index = _STATE["calls"][site]
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
        if after_call is not None:
            after_call(res, k)
        text = log_text(file_dir, tag)
        clause = ssf_clause(res.get(outcome_key), res.get(reason_key), text)
        try:
            rec = make_record(k, res, start, end, clause, text, call_index)
        except Exception as e:                           # noqa: BLE001  (RB-1: a recording failure)
            cnt["consistency_violations"] += 1
            _recording_failure("attempt record at %s" % site, e)
        attempts.append(rec)
        sec["attempt_records"].append(rec)
        starts.append(start)
        ends.append(end)
        cnt["attempts_total"] += 1
        if clause is not None:
            cnt["ssf_attempts_by_clause"][clause] += 1
            if event is None:
                event = dict(event_head, site=site, tag=tag, call_index=call_index, attempts=attempts, renamed_files={},
                             resolve_cap_reached=False, still_ssf_after_last_attempt=False, consistency={"ok": True, "violations": []})
                sec["events"].append(event)
                cnt["calls_with_ssf_attempt"] += 1
        if k >= 2:
            cnt["re_solves"] += 1
        viol = _consistency(attempts, ends, starts)
        if viol:
            if event is None:
                event = dict(event_head, site=site, tag=tag, call_index=call_index, attempts=attempts, renamed_files={})
                sec["events"].append(event)
            event["consistency"] = {"ok": False, "violations": viol}
            event["accepted_attempt"] = None
            event["final_outcome"] = None
            doc["consistency_violation"] = True
            cnt["consistency_violations"] += 1
            _write()
            raise SolverEventConsistencyError(CONSISTENCY_MESSAGE % site)
        if clause is None:                               # the first attempt without the SSF signature is recorded
            break
        if k >= R.K + 1:                                 # the (K + 1)-th SSF attempt keeps its frozen class
            event["still_ssf_after_last_attempt"] = True
            cnt["calls_still_ssf_after_last_attempt"] += 1
            break
        if k >= 2:
            hit, spent = _cap_reached(attempts, timeout)
            if hit:
                event["resolve_cap_reached"] = True
                event["resolve_cap_detail"] = {"summed_wall_seconds_attempts_2_to_k": spent, "timeout_s": timeout, "k": k}
                event["still_ssf_after_last_attempt"] = True
                cnt["resolve_cap_reached"] += 1
                cnt["calls_still_ssf_after_last_attempt"] += 1
                break
        renamed = _rename(file_dir, tag, k)
        event["renamed_files"]["attempt%d" % k] = renamed
        rec["rb1"]["ms_out"] = MS_OUT_RENAMED % (tag + ".ms.out" + (R.RENAME_SUFFIX % k))       # RB-1 (a)
        _write()
    if event is not None:
        event["accepted_attempt"] = k
        event["final_outcome"] = res.get(outcome_key)
        event["final_reason"] = res.get(reason_key)
        event["final_ssf_clause"] = attempts[-1]["ssf_clause"]
        event["final_D"] = res.get("D") if site == R.SITE_S1 else res.get("dimension_of_quotient_printed")
    _write()
    return res


# ----------------------------------------------------------------------------- S-3: the callgrind-site recording (CG-3; CC-4)
def _record_callgrind(res, solver_dir, tag, k, cap_bytes):
    """CG-3 with CC-4: after a call of the ORIGINAL solve() whose result carries instructions_callgrind, record the
    CG-3 fields under site "v2_driver.solve/callgrind". RECORDS ONLY: nothing reads these values to decide anything
    (VA-6 (c)); no field is added to raw-result.json; no file other than solver-events.json changes."""
    if "instructions_callgrind" not in res:
        return
    V = _STATE["v2_solver"]
    cg = res["instructions_callgrind"] or {}
    files, text, missing = {}, "", False
    for ext in (".callgrind.stdout", ".callgrind.stderr"):
        p = os.path.join(solver_dir, tag + ext)
        if os.path.exists(p):
            files[tag + ext] = {"sha256": _sha(p), "bytes": os.path.getsize(p)}
            text += open(p, errors="replace").read() + "\n"
        else:
            files[tag + ext] = "absent"
            missing = True
    st = V.parse_msolve_log(text) if not missing else None
    dq = st["dimension_of_quotient"] if st is not None else "absent (a log file is absent)"
    sq = (st["fglm"]["squarefree_degree"] if "squarefree_degree" in st["fglm"] else "absent") if st is not None else "absent (a log file is absent)"
    pdr = st["positive_dimension_reported"] if st is not None else "absent (a log file is absent)"
    rf = (RANDOM_FORM in text) if not missing else "absent (a log file is absent)"
    indicator = bool(rf is True or (isinstance(sq, int) and isinstance(dq, int) and sq != dq))
    recorded_dim = res.get("dimension_of_quotient_printed")
    dim_equal = (dq == recorded_dim)
    child = cg.get("child") or {}
    rb = child.get("rlimit_as_child_getrlimit")
    rb_equal = isinstance(rb, dict) and rb.get("soft") == cap_bytes and rb.get("hard") == cap_bytes
    fields = {"present": {kk: (kk in cg) for kk in CG_RECORD_KEYS},
              "values": {kk: cg.get(kk) for kk in CG_RECORD_KEYS if kk in cg},
              "child_present": {kk: (kk in child) for kk in CG_CHILD_KEYS},
              "child_values": {kk: child.get(kk) for kk in CG_CHILD_KEYS if kk in child}}
    rec = {"site": R.SITE_S3, "tag": tag, "attempt_recorded_by_the_wrapper": k, "files": files,
           "dimension_of_quotient": dq, "fglm_squarefree_degree": sq, "positive_dimension_reported": pdr,
           "random_linear_form_string_in_log": rf, "log_visible_ssf_indicator": indicator,
           "printed_quotient_dimension_equals_recorded_attempt": dim_equal,
           "recorded_attempt_dimension_of_quotient_printed": recorded_dim,
           "reg1_compared_fields_verbatim": fields,
           "child_readback_equals_requested_cap": rb_equal, "requested_cap_bytes": cap_bytes}
    sec = _STATE["doc"]["sites"][R.SITE_S3]
    sec["records"].append(rec)
    c = sec["counters"]
    c["callgrind_children_observed"] += 1
    c["with_log_visible_ssf_indicator"] += int(indicator)
    c["with_quotient_dimension_mismatch"] += int(not dim_equal)
    c["with_readback_differing_from_requested_cap"] += int(not rb_equal)
    _write()


# ----------------------------------------------------------------------------- the SE-3 wrapper (S-1)
def solve(ctx, names, eqs, tag, timeout_s, retain_input, gb_only=False, callgrind_timeout=None):
    """SE-2 with SF-1..SF-3 and SC-11 at S-1; CG-3 after every original call; RB-1 per attempt; RL-2 on gb_only."""
    original = _STATE["original"]
    args = (ctx, names, eqs, tag, timeout_s, retain_input)
    kwargs = {"gb_only": gb_only, "callgrind_timeout": callgrind_timeout}
    sd = os.path.join(ctx.rd, "solver")

    def after(res, k):
        _record_callgrind(res, sd, tag, k, ctx.cap)
    if gb_only:                                          # SE-2 (6): never for gb_only solves; RL-2 pass-through record
        sec = _STATE["doc"]["sites"][R.SITE_S1]
        sec["counters"]["passthrough_calls_gb_only_true"] += 1
        _STATE["calls"][R.SITE_S1] += 1
        call_index = _STATE["calls"][R.SITE_S1]
        res = _call_original(original, args, kwargs)
        after(res, 1)
        try:
            prec = _passthrough_record(res, tag, call_index)
        except Exception as e:                           # noqa: BLE001  (RL-2: a recording failure)
            sec["counters"]["consistency_violations"] += 1
            _recording_failure("pass-through record", e)
        sec["passthrough_records"].append(prec)
        _write()
        return res
    head = {"timeout_s": timeout_s, "retain_input": retain_input, "callgrind_timeout": callgrind_timeout}

    def make(k, res, start, end, clause, text, call_index):
        return _attempt_record_s1(k, res, start, end, clause, text, tag, call_index)
    return _bounded(R.SITE_S1, original, args, kwargs, tag, sd, timeout_s, "outcome", "reason", make, after, head)


solve.__r4_resolve_wrapper__ = True


# ----------------------------------------------------------------------------- the HR-3 wrapper (S-2)
def run_system(p, eqs, degs, tag, out_dir, cap):
    """HR-1..HR-8 at S-2: the bounded rule on a1_health.run_system; the cap reads a1_health.DEV_TIMEOUT_S at call
    time (HR-6); the recorded result is returned UNMODIFIED to the frozen caller a1_health.run (HR-4); RB-1 per attempt."""
    original = _STATE["health_original"]
    args = (p, eqs, degs, tag, out_dir, cap)
    timeout = getattr(_STATE["health_module"], "DEV_TIMEOUT_S", None)
    head = {"p": p, "pattern": list(degs), "timeout_s_DEV_TIMEOUT_S_at_call": timeout,
            "out_dir": os.path.relpath(out_dir, _STATE["run_dir"]) if _STATE["run_dir"] else out_dir}

    def make(k, res, start, end, clause, text, call_index):
        return _attempt_record_s2(k, res, start, end, clause, text, out_dir, tag, call_index)
    return _bounded(R.SITE_S2, original, args, {}, tag, out_dir, timeout, "v2_outcome_class", "v2_outcome_reason",
                    make, None, head)


run_system.__r4_health_wrapper__ = True


# ----------------------------------------------------------------------------- install / read-back (SE-3; HR-3)
def _identity(fn):
    code = getattr(fn, "__code__", None)
    return {"module": getattr(fn, "__module__", None), "qualname": getattr(fn, "__qualname__", None),
            "code_file": os.path.relpath(code.co_filename, R.REPO) if code is not None else None,
            "code_firstlineno": code.co_firstlineno if code is not None else None}


def _ensure_doc(run_dir):
    if _STATE["doc"] is None:
        _STATE["doc"] = _empty_doc()
        _STATE["run_dir"] = run_dir


def install(v2_driver_module, run_dir):
    """SE-3: replace v2_driver.solve by the wrapper; record the ORIGINAL function object. Writes nothing."""
    if _STATE["installed"]:
        raise RuntimeError("r4_resolve.install called twice")
    _ensure_doc(run_dir)
    orig = v2_driver_module.solve
    _STATE.update(installed=True, original=orig, v2_solver=getattr(v2_driver_module, "V", None))
    solve.__r4_original__ = orig
    v2_driver_module.solve = solve
    return _identity(orig)


def install_health(a1_health_module, run_dir):
    """HR-3: replace a1_health.run_system by the wrapper (a1 entry, after `import a1_driver`). Writes nothing."""
    if _STATE["health_installed"]:
        raise RuntimeError("r4_resolve.install_health called twice")
    _ensure_doc(run_dir)
    orig = a1_health_module.run_system
    _STATE.update(health_installed=True, health_original=orig, health_module=a1_health_module)
    run_system.__r4_original__ = orig
    a1_health_module.run_system = run_system
    return _identity(orig)


def begin():
    """Write the initial run-root solver-events.json (no events) immediately before dispatch, only after every entry
    read-back passed, so that it exists and parses even if no wrapped call runs (SE-4 (e))."""
    _write()


def readback(v2_driver_module):
    """SE-3 read-back: v2_driver.solve is the wrapper; the wrapper's recorded original is the frozen function object
    (module v2_driver, qualname solve, code file implementation-v2/v2_driver.py, first line 158, captured at install)."""
    reasons = []
    attr = getattr(v2_driver_module, "solve", None)
    is_wrapper = attr is solve and getattr(attr, "__r4_resolve_wrapper__", False) is True
    orig = getattr(solve, "__r4_original__", None)
    code = getattr(orig, "__code__", None)
    frozen_file = os.path.join(R.V2_DIR, "v2_driver.py")
    orig_ok = (orig is not None and orig is _STATE.get("original") and getattr(orig, "__module__", None) == "v2_driver"
               and getattr(orig, "__qualname__", None) == "solve" and code is not None
               and os.path.abspath(code.co_filename) == os.path.abspath(frozen_file) and code.co_firstlineno == 158
               and getattr(orig, "__r4_resolve_wrapper__", False) is not True)
    if not is_wrapper:
        reasons.append("SE-3 read-back: v2_driver.solve is not the r4 re-solve wrapper")
    if not orig_ok:
        reasons.append("SE-3 read-back: the wrapper's recorded original is not the frozen v2_driver.solve")
    rec = {"v2_driver.solve_is_r4_wrapper": is_wrapper, "wrapper_original_is_frozen_v2_driver_solve": orig_ok,
           "original_identity": _identity(orig) if orig is not None else None,
           "frozen_file_sha256": R.sha256_file(frozen_file), "K": R.K, "spacing_s": R.SPACING_S}
    return rec, reasons


def readback_health(a1_health_module, a1_driver_module):
    """HR-3 read-back (a1 entry): a1_health.run_system is the HR-3 wrapper; its recorded original is the frozen
    function (module a1_health, qualname run_system, code file implementation-v2-a1/a1_health.py, first line 140,
    the object captured at install); a1_driver.H is the a1_health module object."""
    reasons = []
    attr = getattr(a1_health_module, "run_system", None)
    is_wrapper = attr is run_system and getattr(attr, "__r4_health_wrapper__", False) is True
    orig = getattr(run_system, "__r4_original__", None)
    code = getattr(orig, "__code__", None)
    frozen_file = os.path.join(R.A1_DIR, "a1_health.py")
    orig_ok = (orig is not None and orig is _STATE.get("health_original") and getattr(orig, "__module__", None) == "a1_health"
               and getattr(orig, "__qualname__", None) == "run_system" and code is not None
               and os.path.abspath(code.co_filename) == os.path.abspath(frozen_file) and code.co_firstlineno == 140
               and getattr(orig, "__r4_health_wrapper__", False) is not True)
    h_ok = getattr(a1_driver_module, "H", None) is a1_health_module and _STATE.get("health_module") is a1_health_module
    if not is_wrapper:
        reasons.append("HR-3 read-back: a1_health.run_system is not the r4 health wrapper")
    if not orig_ok:
        reasons.append("HR-3 read-back: the health wrapper's recorded original is not the frozen a1_health.run_system")
    if not h_ok:
        reasons.append("HR-3 read-back: a1_driver.H is not the a1_health module object")
    rec = {"a1_health.run_system_is_r4_wrapper": is_wrapper, "wrapper_original_is_frozen_a1_health_run_system": orig_ok,
           "a1_driver.H_is_a1_health_module": h_ok, "original_identity": _identity(orig) if orig is not None else None,
           "frozen_file_sha256": R.sha256_file(frozen_file), "K": R.K, "spacing_s": R.SPACING_S}
    return rec, reasons


def readback_no_health():
    """HR-3 read-back (v2 entry): no module named a1_health is imported."""
    loaded = "a1_health" in sys.modules
    reasons = ["HR-3 read-back: a module named a1_health is imported in the v2 entry"] if loaded else []
    return {"a1_health_imported": loaded}, reasons
