"""AMD-20261002-f3fa33 C-3 harness (TASK-20261002-e5139f): CR-4 (C-1) and C-2, nothing else.

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
C-2 for step 31: (i) exit 1 / expected 1; (ii) the stop line and the '{"p0_stop"' JSON line
  (the C-2 "completeness" values are read from the selection's only completeness field,
  completeness_table); (iii) and (iv) for SX-31 only.

No verdict mode runs unless --controls names a controls output of THIS file (same sha256) in which
every control behaved as C-3 states.  Standard library only.
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


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ----------------------------------------------------------------------------- canon
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


# ----------------------------------------------------------------------------- tails
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


# ----------------------------------------------------------------------------- C-2
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
            comp = sel.get("completeness_table", {})
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


# ----------------------------------------------------------------------------- controls
def _replace_once(s, old, new):
    if old not in s:
        return s, False
    return s.replace(old, new, 1), True


def build_controls(base):
    """Each control: (id, kind, description, mutate(log) -> (ok_constructed, detail))."""
    C = []

    def st(log, n):
        return log["steps"][n - 1]

    def p1(log):
        s = st(log, 3); m = re.search(r"\bpid (\d+)", s["stdout_tail"])
        if not m:
            return False, "no pid in step 3"
        new = str(int(m.group(1)) + 1)
        s["stdout_tail"] = s["stdout_tail"][:m.start(1)] + new + s["stdout_tail"][m.end(1):]
        return True, f"pid {m.group(1)} -> {new}"
    C.append(("P1", "positive", "change one pid in step 3", p1))

    def p2(log):
        s = st(log, 5)
        for f in ("stdout_tail", "stderr_tail"):
            m = TS.search(s[f])
            if m:
                old = m.group(0); new = "2027" + old[4:]
                s[f] = s[f][:m.start()] + new + s[f][m.end():]
                return True, f"{f}: {old} -> {new}"
        return False, "no timestamp in step 5"
    C.append(("P2", "positive", "change one timestamp in step 5", p2))

    def p3(log):
        s = st(log, 7); t = s["stdout_tail"]
        m = WALL.search(t)
        if not m:
            return False, "no wall in step 7"
        t = t[:m.start()] + "wall 9.999 s" + t[m.end():]
        m2 = RSS.search(t)
        if not m2:
            return False, "no peak_rss in step 7"
        t = t[:m2.start()] + "peak_rss 12345" + t[m2.end():]
        s["stdout_tail"] = t
        return True, f"{m.group(0)} -> wall 9.999 s; {m2.group(0)} -> peak_rss 12345"
    C.append(("P3", "positive", 'change one "wall ... s" and one "peak_rss" value in step 7', p3))

    def p4(log):
        s = st(log, 3); lines = s["stdout_tail"].splitlines(keepends=True)
        idx = [i for i, l in enumerate(lines) if " ended: " in l]
        if len(idx) < 2:
            return False, "fewer than two ended lines in step 3"
        a, b = idx[0], idx[1]
        lines[a], lines[b] = lines[b], lines[a]
        s["stdout_tail"] = "".join(lines)
        return True, f"swapped stdout lines {a} and {b}"
    C.append(("P4", "positive", 'swap two "ended" lines in step 3', p4))

    def p5(log):
        s = st(log, 35); m = re.search(r"--calibration-sha256 ([0-9a-f]{64})", s["cmd"])
        if not m:
            return False, "no --calibration-sha256 in step 35"
        new = "f" * 64 if m.group(1) != "f" * 64 else "e" * 64
        s["cmd"] = s["cmd"][:m.start(1)] + new + s["cmd"][m.end(1):]
        return True, f"{m.group(1)} -> {new}"
    C.append(("P5", "positive", "change the --calibration-sha256 value in step 35", p5))

    def p6(log):
        fx = log["fx"]
        tail = "ctlp6x/fx"
        new = fx[: len(fx) - len("ce5403/fx")] + tail if fx.endswith("ce5403/fx") else None
        if new is None or len(new) != len(fx) or new == fx:
            return False, "cannot form an equal-length replacement path"
        txt = json.dumps(log).replace(fx, new)
        nl = json.loads(txt)
        log.clear(); log.update(nl)
        return True, f"{fx} -> {new} (equal length {len(new)}), throughout the log"
    C.append(("P6", "positive", "replace the fx value throughout the log by another path of equal length", p6))

    def n1(log):
        s = st(log, 3); lines = s["stdout_tail"].splitlines(keepends=True)
        for i, l in enumerate(lines):
            if " ended: " in l and "rows 20" in l:
                lines[i] = l.replace("rows 20", "rows 21", 1); s["stdout_tail"] = "".join(lines)
                return True, f"line {i}: rows 20 -> rows 21"
        return False, 'no ended line with "rows 20" in step 3'
    C.append(("N1", "negative", 'change "rows 20" to "rows 21" in one ended line of step 3', n1))

    def n2(log):
        s = st(log, 5); lines = s["stdout_tail"].splitlines(keepends=True)
        if len(lines) < 3 or lines[1] == lines[2]:
            return False, "cannot swap two distinct lines of step 5 stdout"
        lines[1], lines[2] = lines[2], lines[1]; s["stdout_tail"] = "".join(lines)
        return True, "swapped stdout lines 1 and 2"
    C.append(("N2", "negative", "swap two lines of step 5's stdout_tail", n2))

    def n3(log):
        s = st(log, 34); z = "--calibration-sha256 " + "0" * 64
        if z not in s["cmd"]:
            return False, "no all-zero digest in step 34"
        s["cmd"] = s["cmd"].replace(z, "--calibration-sha256 1" + "0" * 63, 1)
        return True, "first digit 0 -> 1"
    C.append(("N3", "negative", "change one digit of step 34's all-zero digest", n3))

    def n4(log):
        s = st(log, 4); c = s.get("check")
        if not isinstance(c, dict) or "certificates_sha256" not in c:
            return False, "no check certificates_sha256 in step 4"
        v = c["certificates_sha256"]; nv = ("0" if v[0] != "0" else "1") + v[1:]
        c["certificates_sha256"] = nv
        return True, f"{v[:8]}... -> {nv[:8]}..."
    C.append(("N4", "negative", "change one hex digit of step 4's check certificates_sha256", n4))

    def n5(log):
        s = st(log, 14); old = s["exit_code"]; s["exit_code"] = old + 1
        return True, f"exit_code {old} -> {old + 1}"
    C.append(("N5", "negative", "change step 14's exit_code", n5))

    def n6(log):
        s = st(log, 35); c = s.get("check")
        if not isinstance(c, dict) or "kappa_subgroup_TT3" not in c:
            return False, "no check kappa_subgroup_TT3 in step 35"
        old = c["kappa_subgroup_TT3"]; r = repr(old)
        for d in range(1, 10):
            nd = str((int(r[-1]) + d) % 10)
            nv = float(r[:-1] + nd)
            if nv != old:
                c["kappa_subgroup_TT3"] = nv
                return True, f"{r} -> {r[:-1] + nd} (last digit; first digit change giving a different double)"
        return False, "no last-digit change yields a different double"
    C.append(("N6", "negative", "change step 35's check kappa_subgroup_TT3 in its last digit", n6))

    def n7(log):
        s = st(log, 13)
        fields = [k for k in ("stdout_tail", "stderr_tail", "cmd") if isinstance(s.get(k), str) and "missing 0" in s[k]]
        if "check" in s and "missing 0" in json.dumps(s["check"]):
            fields.append("check")
        if not fields:
            return False, ('step 13 contains no "missing 0" token in any field (its stdout_tail ended line reads '
                           '"missing 1"); the planted change cannot be made as C-3 states')
        f = fields[0]; s[f] = s[f].replace("missing 0", "missing 1", 1)
        return True, f"{f}: missing 0 -> missing 1"
    C.append(("N7", "negative", 'change "missing 0" to "missing 1" in step 13', n7))

    def n8(log):
        s = st(log, 19); ok = '"matched": 44' in s["stdout_tail"]
        if not ok:
            return False, 'no "matched": 44 in step 19 stdout'
        s["stdout_tail"] = s["stdout_tail"].replace('"matched": 44', '"matched": 43', 1)
        return True, '"matched": 44 -> 43'
    C.append(("N8", "negative", 'change step 19\'s stdout "matched": 44 to 43', n8))

    def n9(log):
        s = st(log, 1); old = s["step"]; s["step"] = old + " (changed)"
        return True, f"step 1 label {old!r} -> {s['step']!r}"
    C.append(("N9", "negative", "change a step label", n9))

    def n10(log):
        s = st(log, 31); old = '"selected_rungs": [30, 32]'
        if old not in s["stderr_tail"]:
            return False, "no selected_rungs [30, 32] in step 31 stderr JSON"
        s["stderr_tail"] = s["stderr_tail"].replace(old, '"selected_rungs": [28, 30]', 1)
        return True, "selected_rungs [30, 32] -> [28, 30]"
    C.append(("N10", "negative", "in step 31, change selected_rungs in the stderr JSON (C-2 (ii) must fail)", n10))
    return C


def run_controls(a):
    base = json.load(open(a.a3))
    res = {"what": "AMD-20261002-f3fa33 C-3 controls: CR-4 applied to in-memory copies of the archived "
                   "exercise-log-a3.json against itself, each with one planted change",
           "harness": "experiments/EXP-PFDR-011cd0/amd-f3fa33/check_identity_v4.py",
           "harness_sha256": sha256_file(SELF), "reference_log": a.a3, "reference_sha256": sha256_file(a.a3),
           "comparison": "CR-4 record comparison on all 38 steps (H4 off: not against after-D7) plus log-level "
                         "checks; C-2 (ii) evaluated on the candidate's step 31",
           "controls": []}
    bl = compare_logs(base, copy.deepcopy(base), h4=False, step31_mode="cr4")
    res["baseline_unmodified_pass"] = bl["pass"]
    for cid, kind, desc, mut in build_controls(base):
        cand = copy.deepcopy(base)
        constructed, detail = mut(cand)
        ent = {"id": cid, "kind": kind, "planted_change": desc, "constructed": constructed, "detail": detail}
        if not constructed:
            ent["behaved_as_stated"] = False
            ent["outcome"] = "NOT CONSTRUCTIBLE: the planted change cannot be made as C-3 states; not run"
            res["controls"].append(ent); continue
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
        if kind == "positive":
            ent["behaved_as_stated"] = r["pass"]
        elif cid == "N10":
            c2 = c2_ii(cand["steps"][30]["stderr_tail"])
            ent["c2_ii_on_candidate"] = c2
            ent["behaved_as_stated"] = (not r["pass"]) and (not c2["pass"])
        else:
            ent["behaved_as_stated"] = not r["pass"]
        res["controls"].append(ent)
    res["not_constructible"] = [c["id"] for c in res["controls"] if not c["constructed"]]
    res["misbehaved"] = [c["id"] for c in res["controls"] if c["constructed"] and not c["behaved_as_stated"]]
    res["all_controls_behaved_as_stated"] = res["baseline_unmodified_pass"] and all(
        c["behaved_as_stated"] for c in res["controls"]) and len(res["controls"]) == 16
    res["verdict_rendering_enabled"] = res["all_controls_behaved_as_stated"]
    write_new(a.out, {"controls": res})
    print(json.dumps({"baseline": res["baseline_unmodified_pass"], "not_constructible": res["not_constructible"],
                      "misbehaved": res["misbehaved"], "all_behaved": res["all_controls_behaved_as_stated"]}))
    return 0 if res["all_controls_behaved_as_stated"] else 1


def require_controls(path):
    c = json.load(open(path))["controls"]
    if not (c.get("all_controls_behaved_as_stated") is True and c.get("harness_sha256") == sha256_file(SELF)):
        raise SystemExit("refusing: no controls output of this harness in which every C-3 control behaved as stated")
    return c


# ----------------------------------------------------------------------------- verdict modes
def write_new(path, obj):
    if os.path.exists(path):
        raise SystemExit(f"refusing: {path} exists")
    json.dump(obj, open(path, "w"), indent=1)


def run_archived(a):
    ctl = require_controls(a.controls)
    d7, a3 = json.load(open(a.after_d7)), json.load(open(a.a3))
    r = compare_logs(d7, a3, h4=True, step31_mode="c2")
    body = json.load(open(a.controls))
    body["archived"] = {"what": "C-4 (2): archived exercise-log-a3.json vs fixtures/exercise-log-after-D7.json "
                                "under CR-4 (37 non-31 steps), C-2 (i)-(ii) for step 31",
                        "harness_sha256": ctl["harness_sha256"], **r}
    json.dump(body, open(a.controls, "w"), indent=1)
    print(json.dumps({"failing_steps": r["failing_steps"], "pass": r["pass"]}))
    return 0 if r["pass"] else 1


def run_rerun(a):
    ctl = require_controls(a.controls)
    d7, a3, rr = json.load(open(a.after_d7)), json.load(open(a.a3)), json.load(open(a.rerun))
    r = compare_logs(d7, rr, h4=True, step31_mode="c2+a3", a3_ref=a3)
    write_new(a.out, {"what": "C-4 (3): re-run log vs after-D7 under CR-4 (37 non-31 steps); step 31 by C-2 "
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
                     "stdout_bytes": len(stdout)}
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
    write_new(a.out, {"what": "C-4 (3) SX-31: C-2 (i)-(iv)", "harness_sha256": ctl["harness_sha256"], **res})
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
    write_new(a.out, {"what": "C-4 (4): p-cases re-run log vs archived p-cases-log.json",
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
    write_new(a.out, {"what": "C-5 (2): R11 attempt-3 curves.jsonl.gz vs attempt-2", "harness_sha256": ctl["harness_sha256"], **res})
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
    write_new(a.out, {"what": "C-5 (3): attempt-3 p0x-report.json vs attempt-2 after H10",
                      "harness_sha256": ctl["harness_sha256"], **res})
    print(json.dumps({"pass": res["pass"], "difference_count": len(diffs)}))
    return 0 if res["pass"] else 1


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="mode", required=True)
    p = sp.add_parser("controls"); p.add_argument("--a3", required=True); p.add_argument("--out", required=True)
    p = sp.add_parser("archived")
    for k in ("--controls", "--after-d7", "--a3"):
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
