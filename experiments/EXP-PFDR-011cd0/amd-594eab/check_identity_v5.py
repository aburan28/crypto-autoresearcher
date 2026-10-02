"""AMD-20261002-594eab D-2 harness (TASK-20261002-1069c1): CR-4 (AMD-20261002-f3fa33 C-1, unchanged),
C-2 as made exact by D-3, and control_table (D-1), and nothing else.

Derived from the archived amd-f3fa33/check_identity_v4.py (sha256 3f23bd6e...), copied and changed.
Changes against v4: the control list is replaced by the 18-row control_table of AMD-20261002-594eab
(B0, P1-P6, N1-N11) with every parameter fixed and each row's plantability_check re-verified before
planting; a row behaves as stated only under the control_table_rules; the archived mode writes a new
file (compare-v5-archived.json); sx31 also records and checks the SX-31 stdout file; every output is
written once.  CR-4 functions (canon, record, tails, log level) and the C-2 checks are unchanged
from v4.

Modes: controls, archived, rerun, sx31, pcases, curves, p0x.

CR-4 (C-1) record comparison of two exercise-step records X (reference) and Y (candidate):
  (1) key sets equal; (2) step, exit_code, expected_exit, expectation_met with == (strict types);
  (3) check as parsed JSON after canon() on every string leaf and dict key;
  (4) cmd after canon() (H3 on), and H7 at steps 35 and 38 only;
  (5) stdout_tail / stderr_tail after canon(), as lists of lines (keepends), under H8 and H9.
canon(): H2 (log's own fx -> <FX>), H3 (cmd only: first whitespace token -> <PY>),
  H4 (only against fixtures/exercise-log-after-D7.json), H1 (TS, STAMP), H5 (pid), H6 (wall, cpu,
  peak_rss).  The H1, H4, H6 patterns and the PID pattern are those of the archived
  amd-c7ccde/check_exercise_v3.py.  H10 (p0x only), H11 (curves only).  Nothing else is excluded.
C-2 for step 31: (i) exit 1 / expected 1; (ii) the stop line and the '{"p0_stop"' JSON line, with
  the completeness values read from selection.completeness_table (D-3); (iii) and (iv) for SX-31 only.

No verdict mode runs unless --controls names amd-594eab/compare-v5-controls.json written by THIS
file (same sha256) recording all 18 control_table rows behaving as stated.  Standard library only.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import os
import re
import sys

TS = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+00:00|Z)?")
STAMP = re.compile(r"\d{8}T\d{6}Z")
WALL = re.compile(r"\bwall \d+(\.\d+)? s\b")
CPU = re.compile(r"\bcpu \d+(\.\d+)? s\b", re.I)
RSS = re.compile(r"\bpeak_rss \d+\b")
PID = re.compile(r"\bpid \d+\b")
FIRST_TOKEN = re.compile(r"\S+")
A3_PATH = "experiments/EXP-PFDR-011cd0/amd-280481/analyze_relcensus.py"
ORIG_PATH = "experiments/EXP-PFDR-011cd0/analyze_relcensus.py"
H7_RE = re.compile(r"(--calibration-sha256 )[0-9a-f]{64}")
H8_HEADER = re.compile(r"^\[<TS>\] attempt .*: \d+ jobs, max (\d+) processes,")
REPO_PREFIX = "/home/user/crypto-autoresearcher/"
STOP_LINE = ("P0 stop (AMD-20261002-280481 A-1 (b)): selection [30, 32] is not exactly [22, 24]; "
             "design.json and power.json not written")
EX_CUT = 1500
PC_CUT = 2000
SELF = os.path.abspath(__file__)
A3_LOG = "experiments/EXP-PFDR-011cd0/amd-280481/fixtures/exercise-log-a3.json"
A3_LOG_SHA256 = "f823814b81f38e03f4c77e8d3d061075b6475bcfd1a4d3954262a6dcaa4f325e"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_new(path, obj):
    if os.path.exists(path):
        raise SystemExit(f"refusing: {path} exists")
    with open(path, "x") as f:
        json.dump(obj, f, indent=1)


# ----------------------------------------------------------------------------- canon (CR-4, unchanged)
def canon(s, fx, fired, *, cmd=False, h4=False, h3=None):
    if fx and fx in s:
        s = s.replace(fx, "<FX>"); fired.add("H2")
    if (cmd if h3 is None else h3):
        m = FIRST_TOKEN.search(s)
        if m:
            s = s[:m.start()] + "<PY>" + s[m.end():]; fired.add("H3")
    if h4 and A3_PATH in s:
        s = s.replace(A3_PATH, ORIG_PATH); fired.add("H4")
    for rx, rep, cls in ((TS, "<TS>", "H1"), (STAMP, "<STAMP>", "H1"), (PID, "pid <PID>", "H5"),
                         (WALL, "wall <SEC> s", "H6"), (CPU, "cpu <SEC> s", "H6"), (RSS, "peak_rss <RSS>", "H6")):
        s, n = rx.subn(rep, s)
        if n:
            fired.add(cls)
    return s


def canon_json(o, fx, fired, *, keys=True, h4=False, cmd_key=None):
    if isinstance(o, str):
        return canon(o, fx, fired, h4=h4)
    if isinstance(o, list):
        return [canon_json(v, fx, fired, keys=keys, h4=h4, cmd_key=cmd_key) for v in o]
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            kk = canon(k, fx, fired, h4=h4) if keys else k
            if cmd_key is not None and k == cmd_key and isinstance(v, str):
                out[kk] = canon(v, fx, fired, h4=h4, h3=True)
            else:
                out[kk] = canon_json(v, fx, fired, keys=keys, h4=h4, cmd_key=cmd_key)
        return out
    return o


def strict_eq(a, b):
    """Parsed-JSON equality: dict key order ignored, list order kept, numbers with ==, booleans
    distinct from numbers, None only equal to None."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(strict_eq(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(strict_eq(x, y) for x, y in zip(a, b))
    if type(a) is not type(b):
        return False
    return a == b


def json_diffs(a, b, path="$", out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append({"path": f"{path}.{k}", "ref": a.get(k, "<absent>"), "cand": b.get(k, "<absent>")})
            else:
                json_diffs(a[k], b[k], f"{path}.{k}", out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            json_diffs(x, y, f"{path}[{i}]", out)
    elif not strict_eq(a, b):
        out.append({"path": path, "ref": a, "cand": b})
    return out


# ----------------------------------------------------------------------------- tails (H8, H9)
def compare_tail(x_raw, y_raw, fx_x, fx_y, fired, rules, *, cut, h8_allowed, h4):
    x = canon(x_raw or "", fx_x, fired, h4=h4).splitlines(keepends=True)
    y = canon(y_raw or "", fx_y, fired, h4=h4).splitlines(keepends=True)
    h8 = False
    if h8_allowed and x and y:
        mx, my = H8_HEADER.match(x[0]), H8_HEADER.match(y[0])
        h8 = bool(mx and my and int(mx.group(1)) >= 2 and int(my.group(1)) >= 2)
    h9 = cut is not None and (len(x_raw or "") == cut or len(y_raw or "") == cut)
    if h9:
        rules.add("H9")
        x, y = x[1:], y[1:]
        k = min(len(x), len(y))
        if k < 1:
            return False, {"reason": "H9: no line left to compare", "ref": x, "cand": y}
        x, y = x[-k:], y[-k:]
        if h8:
            rules.add("H8")
            ok = x[-1] == y[-1] and sorted(x[:-1]) == sorted(y[:-1])
        else:
            ok = x == y
    elif h8:
        rules.add("H8")
        ok = (len(x) == len(y) and len(x) >= 2 and x[0] == y[0] and x[-1] == y[-1]
              and sorted(x[1:-1]) == sorted(y[1:-1]))
    else:
        ok = x == y
    if ok:
        return True, None
    return False, {"ref_only": sorted(set(x) - set(y)), "cand_only": sorted(set(y) - set(x)),
                   "ref_lines": len(x), "cand_lines": len(y),
                   "note": "order difference" if sorted(x) == sorted(y) else "content difference"}


# ----------------------------------------------------------------------------- CR-4 record
def compare_record(X, Y, step_no, fx_x, fx_y, *, h4):
    fired, rules, fails = set(), set(), {}
    if set(X) != set(Y):
        fails["keys"] = {"ref": sorted(X), "cand": sorted(Y)}
    for k in ("step", "exit_code", "expected_exit", "expectation_met"):
        if k in X or k in Y:
            if not strict_eq(X.get(k), Y.get(k)):
                fails[k] = {"ref": X.get(k), "cand": Y.get(k)}
    if "check" in X or "check" in Y:
        cx = canon_json(X.get("check"), fx_x, fired, h4=h4)
        cy = canon_json(Y.get("check"), fx_y, fired, h4=h4)
        if not strict_eq(cx, cy):
            fails["check"] = json_diffs(cx, cy)
    if "cmd" in X or "cmd" in Y:
        sx = canon(X.get("cmd") or "", fx_x, fired, cmd=True, h4=h4)
        sy = canon(Y.get("cmd") or "", fx_y, fired, cmd=True, h4=h4)
        if step_no in (35, 38) and all(R.get("exit_code") == 0 and R.get("expected_exit") == 0 for R in (X, Y)):
            sx, nx = H7_RE.subn(r"\1<VOLATILE-SHA256>", sx)
            sy, ny = H7_RE.subn(r"\1<VOLATILE-SHA256>", sy)
            if nx or ny:
                fired.add("H7")
        if sx != sy:
            fails["cmd"] = {"ref": sx, "cand": sy}
    for k in ("stdout_tail", "stderr_tail"):
        if k in X or k in Y:
            ok, d = compare_tail(X.get(k), Y.get(k), fx_x, fx_y, fired, rules, cut=EX_CUT,
                                 h8_allowed=(k == "stdout_tail"), h4=h4)
            if not ok:
                fails[k] = d
    return {"step": step_no, "label": Y.get("step"), "h_classes_fired": sorted(fired),
            "rules_fired": sorted(rules), "failing_fields": sorted(fails), "failures": fails, "pass": not fails}


# ----------------------------------------------------------------------------- C-2 (D-3)
def c2_i(rec):
    return {"exit_code": rec.get("exit_code"), "expected_exit": rec.get("expected_exit"),
            "pass": strict_eq(rec.get("exit_code"), 1) and strict_eq(rec.get("expected_exit"), 1)}


def c2_ii(stderr_text):
    lines = (stderr_text or "").splitlines()
    res = {"stop_line_present": STOP_LINE in lines}
    js = [l for l in lines if l.startswith('{"p0_stop"')]
    res["p0_stop_json_lines"] = len(js)
    checks = {}
    if len(js) == 1:
        try:
            o = json.loads(js[0])
            sel = o.get("selection", {})
            comp = sel.get("completeness_table", {})   # D-3: selection.completeness_table
            checks["p0_stop"] = o.get("p0_stop") == "AMD-20261002-280481 A-1 (b)"
            checks["expected_rungs"] = strict_eq(sel.get("expected_rungs"), [22, 24])
            checks["qualifying_rungs"] = strict_eq(sel.get("qualifying_rungs"), [30, 32])
            checks["selected_rungs"] = strict_eq(sel.get("selected_rungs"), [30, 32])
            full = {"complete": 12, "completed_valid": 12, "total": 12}
            zero = {"complete": 0, "completed_valid": 0, "total": 0}
            for b in (30, 32):
                checks[f"completeness_{b}"] = strict_eq(comp.get(str(b)), full)
            for b in range(12, 29, 2):
                checks[f"completeness_{b}"] = strict_eq(comp.get(str(b)), zero)
        except ValueError as exc:
            checks["json_parses"] = False
            res["parse_error"] = str(exc)
    res["checks"] = checks
    res["pass"] = res["stop_line_present"] and len(js) == 1 and bool(checks) and all(checks.values())
    return res


# ----------------------------------------------------------------------------- log level
def compare_logs(ref, cand, *, h4, step31_mode, a3_ref=None):
    """step31_mode: 'c2' (C-2 (i)-(ii) only), 'c2+a3' (C-2 (i)-(ii) and CR-4 with a3_ref step 31,
    H4 off), 'cr4' (step 31 compared by CR-4 like every other step; controls)."""
    out = {"log_level": {}, "steps": []}
    ll = out["log_level"]
    ll["steps_total_38_both"] = ref.get("steps_total") == 38 and cand.get("steps_total") == 38 \
        and len(ref["steps"]) == 38 and len(cand["steps"]) == 38
    ll["labels_pairwise_equal"] = [s.get("step") for s in ref["steps"]] == [s.get("step") for s in cand["steps"]]
    ll["what_equal"] = ref.get("what") == cand.get("what")
    if step31_mode == "cr4":
        ll["expectation_state_ok"] = strict_eq(ref.get("steps_expectation_met"), cand.get("steps_expectation_met"))
    else:
        false_steps = [i for i, s in enumerate(cand["steps"], 1) if s.get("expectation_met") is not True]
        ll["candidate_steps_expectation_met"] = cand.get("steps_expectation_met")
        ll["candidate_false_expectations"] = false_steps
        ll["expectation_state_ok"] = cand.get("steps_expectation_met") == 37 and false_steps == [31]
    for i, (x, y) in enumerate(zip(ref["steps"], cand["steps"]), 1):
        if i == 31 and step31_mode != "cr4":
            ent = {"step": 31, "label": y.get("step"), "rule": "C-2 (i)-(ii)",
                   "c2_i": c2_i(y), "c2_ii": c2_ii(y.get("stderr_tail"))}
            ok = ent["c2_i"]["pass"] and ent["c2_ii"]["pass"]
            if step31_mode == "c2+a3":
                a3s = a3_ref["steps"][30]
                ent["cr4_vs_archived_a3_step31"] = compare_record(a3s, y, 31, a3_ref["fx"], cand["fx"], h4=False)
                ok = ok and ent["cr4_vs_archived_a3_step31"]["pass"]
            ent["pass"] = ok
        else:
            ent = compare_record(x, y, i, ref["fx"], cand["fx"], h4=h4)
            if i == 31:
                ent["c2_ii_on_candidate"] = c2_ii(y.get("stderr_tail"))
        out["steps"].append(ent)
    out["failing_steps"] = [s["step"] for s in out["steps"] if not s["pass"]]
    out["pass"] = all(v for k, v in ll.items() if isinstance(v, bool)) and not out["failing_steps"]
    return out


# ----------------------------------------------------------------------------- D-1 control_table
_FX_CE = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/ce5403/fx"
_FX_P6 = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/ctlp6x/fx"
CONTROL_TABLE = [
    {"control_id": "B0", "kind": "baseline", "step_index_1based": None, "step_label": None, "field": None,
     "operation": "none", "expected_outcome": "PASS", "expected_failing_steps": []},
    {"control_id": "P1", "kind": "positive", "step_index_1based": 3, "step_label": "dummy run ok",
     "field": "stdout_tail", "operation": "replace_substring", "from_substring": "pid 7679;",
     "to_substring": "pid 7680;", "expected_from_count": 1, "expected_outcome": "PASS",
     "expected_failing_steps": [], "class_that_absorbs_it": "H5"},
    {"control_id": "P2", "kind": "positive", "step_index_1based": 5,
     "step_label": "dummy run planted failures (max-procs 1: invalid stops the run)", "field": "stdout_tail",
     "operation": "replace_substring", "from_substring": "2026-10-02T05:46:03.170034+00:00",
     "to_substring": "2027-10-02T05:46:03.170034+00:00", "expected_from_count": 1, "expected_outcome": "PASS",
     "expected_failing_steps": [], "class_that_absorbs_it": "H1"},
    {"control_id": "P3", "kind": "positive", "step_index_1based": 7,
     "step_label": "dummy run missing/crash/badcert (no invalid row)", "field": "stdout_tail",
     "operation": "replace_two_substrings", "from_substring": "wall 0.067 s", "to_substring": "wall 9.999 s",
     "expected_from_count": 1, "second_from_substring": "peak_rss 43827200", "second_to_substring": "peak_rss 12345",
     "second_expected_from_count": 1, "expected_outcome": "PASS", "expected_failing_steps": [],
     "class_that_absorbs_it": "H6"},
    {"control_id": "P4", "kind": "positive", "step_index_1based": 3, "step_label": "dummy run ok",
     "field": "stdout_tail", "operation": "swap_lines", "line_a_1based": 6, "line_b_1based": 7,
     "line_a_selector": "job 3-b14-c0 ended: ", "line_b_selector": "job 3-b14-c1 ended: ",
     "expected_outcome": "PASS", "expected_failing_steps": [],
     "class_that_absorbs_it": 'H8 (step 3 header reads "max 4 processes")'},
    {"control_id": "P5", "kind": "positive", "step_index_1based": 35,
     "step_label": "unmask B: the planted excess (subgroup TT3, kappa 1.5) exceeds t*; planted arm detected; known-null not",
     "field": "cmd", "operation": "replace_substring",
     "from_substring": "--calibration-sha256 7ca4e90dc5e6dda98e51f14ec022b6c15fc8e6b85a5a0f31c28caa65ea013f5a",
     "to_substring": "--calibration-sha256 ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
     "expected_from_count": 1, "expected_outcome": "PASS", "expected_failing_steps": [],
     "class_that_absorbs_it": "H7 (step 35, exit_code 0 = expected_exit 0)"},
    {"control_id": "P6", "kind": "positive", "step_index_1based": None, "step_label": None, "field": "*",
     "operation": "replace_everywhere", "from_substring": _FX_CE, "to_substring": _FX_P6,
     "expected_from_count": "at least 1, and the top-level fx equals from_substring exactly",
     "expected_outcome": "PASS", "expected_failing_steps": [], "class_that_absorbs_it": "H2"},
    {"control_id": "N1", "kind": "negative", "step_index_1based": 3, "step_label": "dummy run ok",
     "field": "stdout_tail", "operation": "replace_in_selected_line", "line_selector": "job 3-b14-c0 ended: ",
     "from_substring": "rows 20", "to_substring": "rows 21", "expected_from_count": 1,
     "expected_outcome": "FAIL", "expected_failing_steps": [3]},
    {"control_id": "N2", "kind": "negative", "step_index_1based": 5,
     "step_label": "dummy run planted failures (max-procs 1: invalid stops the run)", "field": "stdout_tail",
     "operation": "swap_lines", "line_a_1based": 2, "line_b_1based": 3,
     "line_a_selector": "job 3-b14-c0 started (pid ", "line_b_selector": "job 3-b14-c0 ended: ",
     "expected_outcome": "FAIL", "expected_failing_steps": [5]},
    {"control_id": "N3", "kind": "negative", "step_index_1based": 34,
     "step_label": "unmask refuses a wrong calibration sha256", "field": "cmd", "operation": "replace_substring",
     "from_substring": "--calibration-sha256 0000000000000000000000000000000000000000000000000000000000000000",
     "to_substring": "--calibration-sha256 1000000000000000000000000000000000000000000000000000000000000000",
     "expected_from_count": 1, "expected_outcome": "FAIL", "expected_failing_steps": [34]},
    {"control_id": "N4", "kind": "negative", "step_index_1based": 4,
     "step_label": "dummy finalize ok -> completed_valid, discrete_log verified true", "field": "check",
     "json_path": "certificates_sha256", "operation": "set_value",
     "from_value": "1649de71b82a431fc82a9aff6694e68e146430b5a84d5ab94422e51318ae7965",
     "to_value": "0649de71b82a431fc82a9aff6694e68e146430b5a84d5ab94422e51318ae7965",
     "expected_outcome": "FAIL", "expected_failing_steps": [4]},
    {"control_id": "N5", "kind": "negative", "step_index_1based": 14,
     "step_label": "merge reports the missing key (exit 1)", "field": "exit_code", "operation": "set_value",
     "from_value": 1, "to_value": 2, "expected_outcome": "FAIL", "expected_failing_steps": [14]},
    {"control_id": "N6", "kind": "negative", "step_index_1based": 35,
     "step_label": "unmask B: the planted excess (subgroup TT3, kappa 1.5) exceeds t*; planted arm detected; known-null not",
     "field": "check", "json_path": "kappa_subgroup_TT3", "operation": "set_value",
     "from_value": 1.5345364032358433, "to_value": 1.5345364032358434,
     "expected_outcome": "FAIL", "expected_failing_steps": [35]},
    {"control_id": "N7", "kind": "negative", "step_index_1based": 13,
     "step_label": "dummy attempt with a missing key only", "field": "stdout_tail",
     "operation": "replace_in_selected_line", "line_selector": "job 3-b12-c0 ended: ",
     "from_substring": "missing 1", "to_substring": "missing 0", "expected_from_count": 1,
     "expected_outcome": "FAIL", "expected_failing_steps": [13]},
    {"control_id": "N8", "kind": "negative", "step_index_1based": 19, "step_label": "tabcompare A1 (G-TAB) passes",
     "field": "stdout_tail", "operation": "replace_substring", "from_substring": '"matched": 44',
     "to_substring": '"matched": 43', "expected_from_count": 1, "expected_outcome": "FAIL",
     "expected_failing_steps": [19]},
    {"control_id": "N9", "kind": "negative", "step_index_1based": 1, "step_label": "jobs R10 list", "field": "step",
     "operation": "set_value", "from_value": "jobs R10 list", "to_value": "jobs R10 list (changed)",
     "expected_outcome": "FAIL", "expected_failing_steps": [1],
     "expected_extra": "the log-level check labels_pairwise_equal is false"},
    {"control_id": "N10", "kind": "negative", "step_index_1based": 31,
     "step_label": "p0 on synthetic inputs: P0X detects the planted count (exit 1), design written",
     "field": "stderr_tail", "operation": "replace_substring", "from_substring": '"selected_rungs": [30, 32]',
     "to_substring": '"selected_rungs": [28, 30]', "expected_from_count": 1, "expected_outcome": "FAIL",
     "expected_failing_steps": [31],
     "expected_extra": "C-2 (ii), as made exact by D-3, evaluated on the candidate's step 31 stderr_tail, fails"},
    {"control_id": "N11", "kind": "negative", "step_index_1based": 11,
     "step_label": "dummy attempt-2 resumes both jobs", "field": "stdout_tail",
     "operation": "replace_in_selected_line", "line_selector": "job 3-b12-c1 ended: ",
     "from_substring": "missing 0", "to_substring": "missing 1", "expected_from_count": 1,
     "expected_outcome": "FAIL", "expected_failing_steps": [11]},
]
CONTROL_IDS = ["B0", "P1", "P2", "P3", "P4", "P5", "P6"] + [f"N{i}" for i in range(1, 12)]


def _lines(s):
    return s.splitlines(keepends=True)


def _line1_contains(step, token):
    ls = _lines(step["stdout_tail"])
    return bool(ls) and token in ls[0]


def _hex64(s):
    return re.fullmatch(r"--calibration-sha256 ([0-9a-f]{64})", s) is not None


def plantability(log, row):
    """Re-verify the row's plantability_check on the loaded log.  Returns (ok, list of (check, bool))."""
    chk = []
    cid, n, op = row["control_id"], row["step_index_1based"], row["operation"]
    if cid == "B0":
        chk.append(("the file parses and has 38 steps", isinstance(log.get("steps"), list) and len(log["steps"]) == 38))
        return all(v for _, v in chk), chk
    if n is not None:
        st = log["steps"][n - 1]
        chk.append((f"steps[{n - 1}]['step'] equals step_label", st.get("step") == row["step_label"]))
    if op == "replace_substring":
        f = st[row["field"]]
        chk.append((f"from_substring occurs exactly {row['expected_from_count']} time(s) in step {n} {row['field']}",
                     f.count(row["from_substring"]) == row["expected_from_count"]))
    elif op == "replace_two_substrings":
        f = st[row["field"]]
        chk.append((f"from_substring occurs exactly {row['expected_from_count']} time(s)",
                     f.count(row["from_substring"]) == row["expected_from_count"]))
        chk.append((f"second_from_substring occurs exactly {row['second_expected_from_count']} time(s)",
                     f.count(row["second_from_substring"]) == row["second_expected_from_count"]))
    elif op == "replace_in_selected_line":
        ls = _lines(st[row["field"]])
        sel = [i for i, l in enumerate(ls) if row["line_selector"] in l]
        chk.append(("exactly one line contains line_selector", len(sel) == 1))
        if len(sel) == 1:
            chk.append((f"from_substring occurs exactly {row['expected_from_count']} time(s) in the selected line",
                         ls[sel[0]].count(row["from_substring"]) == row["expected_from_count"]))
    elif op == "swap_lines":
        ls = _lines(st[row["field"]])
        for which in ("a", "b"):
            sel = [i + 1 for i, l in enumerate(ls) if row[f"line_{which}_selector"] in l]
            chk.append((f"line {row[f'line_{which}_1based']} is the only line containing line_{which}_selector",
                         sel == [row[f"line_{which}_1based"]]))
    elif op == "set_value":
        if row["field"] == "check":
            c = st.get("check")
            cur = c.get(row["json_path"], KeyError) if isinstance(c, dict) else KeyError
        else:
            cur = st.get(row["field"], KeyError)
        fv, tv = row["from_value"], row["to_value"]
        chk.append(("current value == from_value with the same JSON type",
                     cur is not KeyError and type(cur) is type(fv) and cur == fv))
        if isinstance(fv, float):
            chk.append(("float(to_value) != float(from_value)", float(tv) != float(fv)))
    elif op == "replace_everywhere":
        chk.append(("log['fx'] equals from_substring", log.get("fx") == row["from_substring"]))
        chk.append(("len(from_substring) == len(to_substring) == 82",
                     len(row["from_substring"]) == len(row["to_substring"]) == 82))
        chk.append(("from_substring occurs at least once", count_everywhere(log, row["from_substring"]) >= 1))
    # row-specific clauses of plantability_check
    if cid == "P4":
        chk.append(("step 3 stdout_tail has 10 lines", len(_lines(st["stdout_tail"])) == 10))
        chk.append(("line 1 contains 'max 4 processes,'", _line1_contains(st, "max 4 processes,")))
    if cid == "P5":
        chk.append(("step 35 exit_code is 0 and expected_exit is 0",
                     strict_eq(st.get("exit_code"), 0) and strict_eq(st.get("expected_exit"), 0)))
        chk.append(("hex part of to_substring is 64 characters", _hex64(row["to_substring"])))
    if cid == "N2":
        chk.append(("line 1 contains 'max 1 processes,' (H8 not eligible)", _line1_contains(st, "max 1 processes,")))
    if cid == "N3":
        chk.append(("hex parts of from_ and to_substring are each 64 characters",
                     _hex64(row["from_substring"]) and _hex64(row["to_substring"])))
    if cid in ("N7", "N11"):
        chk.append(("line 1 contains 'max 4 processes,'", _line1_contains(st, "max 4 processes,")))
    return all(v for _, v in chk), chk


def count_everywhere(o, sub):
    if isinstance(o, str):
        return o.count(sub)
    if isinstance(o, list):
        return sum(count_everywhere(v, sub) for v in o)
    if isinstance(o, dict):
        return sum(k.count(sub) + count_everywhere(v, sub) for k, v in o.items())
    return 0


def replace_everywhere(o, old, new):
    if isinstance(o, str):
        return o.replace(old, new)
    if isinstance(o, list):
        return [replace_everywhere(v, old, new) for v in o]
    if isinstance(o, dict):
        return {k.replace(old, new): replace_everywhere(v, old, new) for k, v in o.items()}
    return o


def plant(log, row):
    """Apply the row's one planted change to log (in place).  Returns a description of what was done."""
    op, n = row["operation"], row["step_index_1based"]
    if op == "none":
        return "no change"
    if op == "replace_everywhere":
        nl = replace_everywhere(log, row["from_substring"], row["to_substring"])
        log.clear(); log.update(nl)
        return f"every occurrence in every string (keys and values) replaced; top-level fx now {log['fx']}"
    st = log["steps"][n - 1]
    f = row["field"]
    if op == "replace_substring":
        st[f] = st[f].replace(row["from_substring"], row["to_substring"], 1)
        return f"first occurrence in step {n} {f} replaced"
    if op == "replace_two_substrings":
        st[f] = st[f].replace(row["from_substring"], row["to_substring"], 1)
        st[f] = st[f].replace(row["second_from_substring"], row["second_to_substring"], 1)
        return f"first occurrence of each substring in step {n} {f} replaced"
    if op == "replace_in_selected_line":
        ls = _lines(st[f])
        i = [j for j, l in enumerate(ls) if row["line_selector"] in l][0]
        ls[i] = ls[i].replace(row["from_substring"], row["to_substring"], 1)
        st[f] = "".join(ls)
        return f"first occurrence in step {n} {f} line {i + 1} replaced"
    if op == "swap_lines":
        ls = _lines(st[f])
        a, b = row["line_a_1based"] - 1, row["line_b_1based"] - 1
        ls[a], ls[b] = ls[b], ls[a]
        st[f] = "".join(ls)
        return f"step {n} {f} lines {a + 1} and {b + 1} swapped"
    if op == "set_value":
        if f == "check":
            st["check"][row["json_path"]] = row["to_value"]
        else:
            st[f] = row["to_value"]
        return f"step {n} {f}{'.' + row['json_path'] if f == 'check' else ''} set to to_value"
    raise SystemExit(f"unknown operation {op}")


def run_controls(a):
    if a.out_check_exists and os.path.exists(a.out):
        raise SystemExit(f"refusing: {a.out} exists")
    if sha256_file(a.a3) != A3_LOG_SHA256:
        raise SystemExit("refusing: reference log sha256 is not the D-1 value f823814b...")
    base = json.load(open(a.a3))
    if [r["control_id"] for r in CONTROL_TABLE] != CONTROL_IDS:
        raise SystemExit("internal: control table ids")
    res = {"what": "AMD-20261002-594eab D-1 control_table: CR-4 applied to in-memory copies of the archived "
                   "exercise-log-a3.json against itself, each carrying exactly one planted change "
                   "(18 rows: B0, P1-P6, N1-N11)",
           "harness": "experiments/EXP-PFDR-011cd0/amd-594eab/check_identity_v5.py",
           "harness_sha256": sha256_file(SELF), "reference_log": A3_LOG, "reference_sha256": sha256_file(a.a3),
           "comparison": "CR-4 record comparison on all 38 steps (H4 off) plus the log-level checks; "
                         "C-2 (ii) (D-3) evaluated on the candidate's step 31",
           "rows": []}
    stop = None
    for row in CONTROL_TABLE:
        ent = {"control_id": row["control_id"], "applied_parameters": copy.deepcopy(row),
               "log_file": A3_LOG}
        ent["applied_parameters"]["log_file"] = A3_LOG
        cand = copy.deepcopy(base)
        ok, chk = plantability(cand, row)
        ent["plantability_check"] = [{"check": c, "holds": v} for c, v in chk]
        ent["constructed"] = ok
        if not ok:
            ent["behaved_as_stated"] = False
            ent["outcome"] = "NOT CONSTRUCTIBLE: plantability_check fails on the loaded log; stop and return"
            res["rows"].append(ent)
            stop = row["control_id"]
            break
        ent["planted"] = plant(cand, row)
        r = compare_logs(base, cand, h4=False, step31_mode="cr4")
        ent["comparison_pass"] = r["pass"]
        ent["failing_steps"] = r["failing_steps"]
        ent["log_level"] = r["log_level"]
        ent["h_classes_fired"] = sorted({h for s in r["steps"] for h in s.get("h_classes_fired", [])})
        ent["rules_fired"] = sorted({h for s in r["steps"] for h in s.get("rules_fired", [])})
        ent["failures"] = {str(s["step"]): s["failures"] for s in r["steps"] if not s["pass"]}
        ent["per_step"] = {str(s["step"]): {"h_classes_fired": s.get("h_classes_fired"),
                                            "rules_fired": s.get("rules_fired"), "pass": s["pass"]}
                           for s in r["steps"]}
        c2 = c2_ii(cand["steps"][30]["stderr_tail"])
        ent["c2_ii_on_candidate"] = c2
        extra = {}
        if row["expected_outcome"] == "PASS":
            behaved = r["pass"] and r["failing_steps"] == []
        else:
            behaved = (not r["pass"]) and r["failing_steps"] == row["expected_failing_steps"]
            if row["control_id"] == "N9":
                extra["labels_pairwise_equal_is_false"] = r["log_level"]["labels_pairwise_equal"] is False
            if row["control_id"] == "N10":
                extra["c2_ii_on_candidate_fails"] = c2["pass"] is False
            behaved = behaved and all(extra.values())
        ent["expected_extra_results"] = extra
        ent["behaved_as_stated"] = behaved
        res["rows"].append(ent)
    res["rows_run"] = len(res["rows"])
    res["not_constructible"] = [e["control_id"] for e in res["rows"] if not e["constructed"]]
    res["misbehaved"] = [e["control_id"] for e in res["rows"] if e["constructed"] and not e["behaved_as_stated"]]
    res["stopped_at"] = stop
    res["all_18_rows_behaved_as_stated"] = (stop is None and len(res["rows"]) == 18
                                            and [e["control_id"] for e in res["rows"]] == CONTROL_IDS
                                            and all(e["behaved_as_stated"] for e in res["rows"]))
    res["verdict_rendering_enabled"] = res["all_18_rows_behaved_as_stated"]
    write_new(a.out, {"controls": res})
    print(json.dumps({"rows_run": res["rows_run"], "not_constructible": res["not_constructible"],
                      "misbehaved": res["misbehaved"], "all_18_behaved": res["all_18_rows_behaved_as_stated"],
                      "harness_sha256": res["harness_sha256"]}))
    return 0 if res["all_18_rows_behaved_as_stated"] else 1


def require_controls(path):
    c = json.load(open(path))["controls"]
    if not (c.get("all_18_rows_behaved_as_stated") is True and c.get("harness_sha256") == sha256_file(SELF)
            and [e["control_id"] for e in c.get("rows", [])] == CONTROL_IDS
            and all(e.get("behaved_as_stated") is True for e in c["rows"])):
        raise SystemExit("refusing: no controls output of this harness (same sha256) in which all 18 control_table "
                         "rows behaved as stated")
    return c


# ----------------------------------------------------------------------------- verdict modes
def run_archived(a):
    ctl = require_controls(a.controls)
    d7, a3 = json.load(open(a.after_d7)), json.load(open(a.a3))
    r = compare_logs(d7, a3, h4=True, step31_mode="c2")
    write_new(a.out, {"what": "D-4 (2): archived exercise-log-a3.json vs fixtures/exercise-log-after-D7.json "
                              "under CR-4 (37 non-31 steps, H4 on), C-2 (i)-(ii) for step 31",
                      "harness_sha256": ctl["harness_sha256"], **r})
    print(json.dumps({"failing_steps": r["failing_steps"], "pass": r["pass"]}))
    return 0 if r["pass"] else 1


def run_rerun(a):
    ctl = require_controls(a.controls)
    d7, a3, rr = json.load(open(a.after_d7)), json.load(open(a.a3)), json.load(open(a.rerun))
    r = compare_logs(d7, rr, h4=True, step31_mode="c2+a3", a3_ref=a3)
    write_new(a.out, {"what": "D-4 (3): re-run log vs after-D7 under CR-4 (37 non-31 steps); step 31 by C-2 "
                              "(i)-(ii) and CR-4 identity with archived a3 step 31 (H4 off)",
                      "harness_sha256": ctl["harness_sha256"], **r})
    print(json.dumps({"failing_steps": r["failing_steps"], "pass": r["pass"]}))
    return 0 if r["pass"] else 1


def run_sx31(a):
    ctl = require_controls(a.controls)
    d7 = json.load(open(a.after_d7)); rr = json.load(open(a.rerun))
    s31 = d7["steps"][30]["check"]
    stderr = open(a.stderr, encoding="utf-8").read()
    stdout = open(a.stdout, encoding="utf-8").read()
    rec = {"exit_code": a.exit_code, "expected_exit": rr["steps"][30].get("expected_exit")}
    res = {"c2_i": c2_i(rec), "c2_ii": c2_ii(stderr)}
    res["c2_iii"] = {"design_json_exists": os.path.exists(os.path.join(a.out_dir, "design.json")),
                     "power_json_exists": os.path.exists(os.path.join(a.out_dir, "power.json")),
                     "stdout_bytes": len(stdout.encode("utf-8"))}
    res["c2_iii"]["pass"] = not res["c2_iii"]["design_json_exists"] and not res["c2_iii"]["power_json_exists"] \
        and stdout == ""
    pr_path = os.path.join(a.out_dir, "p0x-report.json")
    iv = {"p0x_report_exists": os.path.exists(pr_path)}
    if iv["p0x_report_exists"]:
        pr = json.load(open(pr_path))
        iv["compared_equal"] = strict_eq(pr.get("compared"), s31["p0x_compared"])
        iv["difference_count_is_1"] = strict_eq(pr.get("difference_count"), 1)
        iv["differences_equal"] = strict_eq(pr.get("differences"), s31["differences"])
        iv["copied_report_sha256_equal"] = sha256_file(pr_path) == sha256_file(a.p0x_copy)
    iv["pass"] = iv["p0x_report_exists"] and all(v for k, v in iv.items() if k != "pass")
    res["c2_iv"] = iv
    res["pass"] = all(res[k]["pass"] for k in ("c2_i", "c2_ii", "c2_iii", "c2_iv"))
    write_new(a.out, {"what": "D-4 (3) SX-31: C-2 (i)-(iv)", "harness_sha256": ctl["harness_sha256"],
                      "sx31_exit_code": a.exit_code, **res})
    print(json.dumps({"pass": res["pass"]}))
    return 0 if res["pass"] else 1


def run_pcases(a):
    ctl = require_controls(a.controls)
    ref, cand = json.load(open(a.ref)), json.load(open(a.rerun))
    fired, rules = set(), set()
    tails = {}

    def prep(o, fx):
        o = copy.deepcopy(o)
        for c in o.get("cases", []):
            if "stderr_tail" in c:
                tails.setdefault(c.get("case"), []).append(c.pop("stderr_tail"))
        return canon_json(o, fx, fired, keys=False, cmd_key="cmd")
    cr, cc = prep(ref, ref["fx"]), prep(cand, cand["fx"])
    diffs = json_diffs(cr, cc)
    tail_fail = {}
    for case, pair in tails.items():
        if len(pair) != 2:
            tail_fail[case] = "stderr_tail present on one side only"; continue
        ok, d = compare_tail(pair[0], pair[1], ref["fx"], cand["fx"], fired, rules, cut=PC_CUT, h8_allowed=False, h4=False)
        if not ok:
            tail_fail[case] = d
    res = {"h_classes_fired": sorted(fired), "rules_fired": sorted(rules), "json_differences": diffs,
           "stderr_tail_failures": tail_fail, "pass": not diffs and not tail_fail}
    write_new(a.out, {"what": "D-4 (4): p-cases re-run log vs archived p-cases-log.json",
                      "harness_sha256": ctl["harness_sha256"], **res})
    print(json.dumps({"pass": res["pass"]}))
    return 0 if res["pass"] else 1


def run_curves(a):
    ctl = require_controls(a.controls)
    entry = None
    for line in open(os.path.join(a.attempt2, "checksums.sha256")):
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("*").removeprefix("./") == "curves.jsonl.gz":
            entry = parts[0]
    new = sha256_file(os.path.join(a.attempt3, "curves.jsonl.gz"))
    res = {"attempt2_checksums_entry": entry, "attempt3_sha256": new, "container_equal": entry == new}
    if entry is None:
        res.update({"pass": False, "reason": "no curves.jsonl.gz entry in attempt-2/checksums.sha256"})
    elif entry == new:
        res["pass"] = True
    else:
        def dsha(p):
            h = hashlib.sha256()
            with gzip.open(p, "rb") as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
            return h.hexdigest()
        d3, d2 = dsha(os.path.join(a.attempt3, "curves.jsonl.gz")), dsha(os.path.join(a.attempt2, "curves.jsonl.gz"))
        res.update({"H11_applied": True, "attempt3_decompressed_sha256": d3, "attempt2_decompressed_sha256": d2,
                    "pass": d3 == d2})
    write_new(a.out, {"what": "C-5 (2) / D-5: R11 attempt-3 curves.jsonl.gz vs attempt-2",
                      "harness_sha256": ctl["harness_sha256"], **res})
    print(json.dumps({"pass": res["pass"]}))
    return 0 if res["pass"] else 1


def run_p0x(a):
    ctl = require_controls(a.controls)
    listed = []

    def h10(o, path="$"):
        if isinstance(o, dict):
            out = {}
            for k, v in o.items():
                if k in ("created_at", "timing"):
                    listed.append(f"{path}.{k}"); continue
                kk = k[len(REPO_PREFIX):] if isinstance(k, str) and k.startswith(REPO_PREFIX) else k
                out[kk] = h10(v, f"{path}.{k}")
            return out
        if isinstance(o, list):
            return [h10(v, f"{path}[{i}]") for i, v in enumerate(o)]
        if isinstance(o, str) and o.startswith(REPO_PREFIX):
            return o[len(REPO_PREFIX):]
        return o
    r2, r3 = h10(json.load(open(a.attempt2_report))), h10(json.load(open(a.attempt3_report)))
    diffs = json_diffs(r2, r3)
    res = {"listed_and_excluded_fields": listed, "differing_paths": [d["path"] for d in diffs],
           "difference_count": len(diffs), "pass": not diffs}
    write_new(a.out, {"what": "C-5 (3) / D-5: attempt-3 p0x-report.json vs attempt-2 after H10 (values not printed)",
                      "harness_sha256": ctl["harness_sha256"], **res})
    print(json.dumps({"pass": res["pass"], "difference_count": len(diffs)}))
    return 0 if res["pass"] else 1


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    p = sp.add_parser("controls"); p.add_argument("--a3", required=True); p.add_argument("--out", required=True)
    p.set_defaults(out_check_exists=True)
    p = sp.add_parser("archived")
    for k in ("--controls", "--after-d7", "--a3", "--out"):
        p.add_argument(k, required=True)
    p = sp.add_parser("rerun")
    for k in ("--controls", "--after-d7", "--a3", "--rerun", "--out"):
        p.add_argument(k, required=True)
    p = sp.add_parser("sx31")
    for k in ("--controls", "--after-d7", "--rerun", "--stderr", "--stdout", "--out-dir", "--p0x-copy", "--out"):
        p.add_argument(k, required=True)
    p.add_argument("--exit-code", type=int, required=True)
    p = sp.add_parser("pcases")
    for k in ("--controls", "--ref", "--rerun", "--out"):
        p.add_argument(k, required=True)
    p = sp.add_parser("curves")
    for k in ("--controls", "--attempt2", "--attempt3", "--out"):
        p.add_argument(k, required=True)
    p = sp.add_parser("p0x")
    for k in ("--controls", "--attempt2-report", "--attempt3-report", "--out"):
        p.add_argument(k, required=True)
    a = ap.parse_args()
    return {"controls": run_controls, "archived": run_archived, "rerun": run_rerun, "sx31": run_sx31,
            "pcases": run_pcases, "curves": run_curves, "p0x": run_p0x}[a.mode](a)


if __name__ == "__main__":
    sys.exit(main())
