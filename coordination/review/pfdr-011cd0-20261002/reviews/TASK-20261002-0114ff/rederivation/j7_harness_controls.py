#!/usr/bin/env python3
"""J7 (a): the validator's own planted log pairs against check_identity_v5.py (CR-4, H1-H11).

TASK-20261002-0114ff. Imports the archived harness by path (sha256 checked) and calls its
own compare_record() in memory on constructed record pairs; no harness mode is run and
nothing is written by the harness. Each pair states, BEFORE running, the outcome the
CR-4 TEXT gives (spec_letter) and the outcome its INTENT gives (host provenance ignored,
result tokens detected); the harness verdict is reported beside both.

H9 cases are built as exercise.py builds tails: the last 1500 characters of a longer
stdout. Their H8 status follows the text: H8 applies to a tail 'whose first canonical
line is a run_jobs.py attempt header' (f3fa33 C-1 H8); H9 drops the first line of each
canonical value and compares the last k lines (k = smaller remaining count).
Standard library only.
"""
import copy
import hashlib
import importlib.util
import json
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e"
H = WT + "/experiments/EXP-PFDR-011cd0/amd-594eab/check_identity_v5.py"
H_SHA = "81e9d0417c6690ab464a77523327cfd9f3bdfc1affba55ef56b779d7ada0c0ad"
A3 = WT + "/experiments/EXP-PFDR-011cd0/amd-280481/fixtures/exercise-log-a3.json"
FX = "/tmp/fx-validator-0114ff"


def load():
    assert hashlib.sha256(open(H, "rb").read()).hexdigest() == H_SHA
    spec = importlib.util.spec_from_file_location("check_identity_v5", H)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def long_stdout(n_jobs, swap=None, change=None, drop=None, header_jobs=None):
    lines = [f"[2026-10-02T05:46:00.631591+00:00] attempt ../../../tmp/fx/dummy/RUN-x/attempt-1: "
             f"{header_jobs or n_jobs} jobs, max 4 processes, attempt watchdog 86400 s, per-job 21600 s, "
             f"MemAvailable gate 4.0 GB, disk floor 2.5 GB, package guard 1500000000.0 B; trigger: fixture\n"]
    for j in range(n_jobs):
        lines.append(f"[2026-10-02T05:46:00.6{j:02d}000+00:00] job 3-b{12 + 2 * (j // 2)}-c{j % 2} started (pid {7000 + j}; watchdog 21600 s)\n")
    ended = []
    for j in range(n_jobs):
        ended.append(f"[2026-10-02T05:46:01.6{j:02d}000+00:00] job 3-b{12 + 2 * (j // 2)}-c{j % 2} ended: exit 0 rows 20 "
                     f"statuses {{'completed_valid': 20}} missing 0 wall 0.07{j % 10} s peak_rss 4393{j:04d} abnormal False\n")
    if change is not None:
        i, a, b = change
        ended[i] = ended[i].replace(a, b, 1)
    if swap is not None:
        i, k = swap
        ended[i], ended[k] = ended[k], ended[i]
    if drop is not None:
        ended.pop(drop)
    lines += ended
    lines.append("[2026-10-02T05:46:02.198942+00:00] attempt done: jobs ended, not started 0 (None); wall 1.6 s\n")
    return "".join(lines)


def rec(stdout, cmd="/usr/bin/python3 run_jobs.py run --x", check=None, exit_code=0, step="t"):
    return {"step": step, "cmd": cmd, "exit_code": exit_code, "expected_exit": exit_code,
            "expectation_met": True, "check": check if check is not None else {"ok": True},
            "stdout_tail": stdout, "stderr_tail": ""}



# ---- the validator's own reading of the CR-4 tail rule (f3fa33 C-1 H1, H2, H5, H6, H8, H9), from the text
import re as _re
_TS = _re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+00:00|Z)?")
_ST = _re.compile(r"\d{8}T\d{6}Z")
_PID = _re.compile(r"\bpid \d+")
_WALL = _re.compile(r"\bwall \d+(\.\d+)? s\b")
_CPU = _re.compile(r"\bcpu \d+(\.\d+)? s\b", _re.I)
_RSS = _re.compile(r"\bpeak_rss \d+")
_HDR = _re.compile(r"^\[<TS>\] attempt .*: \d+ jobs, max (\d+) processes,")


def own_canon(s, fx):
    s = s.replace(fx, "<FX>") if fx else s
    s = _TS.sub("<TS>", s)
    s = _ST.sub("<STAMP>", s)
    s = _PID.sub("pid <PID>", s)
    s = _WALL.sub("wall <SEC> s", s)
    s = _CPU.sub("cpu <SEC> s", s)
    s = _RSS.sub("peak_rss <RSS>", s)
    return s


def own_tail_letter(xr, yr, fx, cut=1500, h8_allowed=True):
    x = own_canon(xr, fx).splitlines(keepends=True)
    y = own_canon(yr, fx).splitlines(keepends=True)
    def hdr(l):
        mm = _HDR.match(l) if l else None
        return bool(mm and int(mm.group(1)) >= 2)
    h8 = h8_allowed and bool(x) and bool(y) and hdr(x[0]) and hdr(y[0])
    if len(xr) == cut or len(yr) == cut:
        x, y = x[1:], y[1:]
        k = min(len(x), len(y))
        if k < 1:
            return "FAIL"
        x, y = x[-k:], y[-k:]
        ok = (x[-1] == y[-1] and sorted(x[:-1]) == sorted(y[:-1])) if h8 else x == y
    elif h8:
        ok = len(x) == len(y) and x[0] == y[0] and x[-1] == y[-1] and sorted(x[1:-1]) == sorted(y[1:-1])
    else:
        ok = x == y
    return "PASS" if ok else "FAIL"


def main():
    m = load()
    res = []

    def run(cid, X, Y, step_no, spec_letter, intent, note):
        r = m.compare_record(X, Y, step_no, FX, FX, h4=False)
        verdict = "PASS" if r["pass"] else "FAIL"
        if X.get("stdout_tail") != Y.get("stdout_tail") and all(X.get(k) == Y.get(k) for k in ("cmd", "check", "exit_code", "expected_exit", "step", "stderr_tail")):
            spec_letter = own_tail_letter(X["stdout_tail"], Y["stdout_tail"], FX)
        res.append({"id": cid, "note": note, "spec_letter": spec_letter, "intent": intent, "harness": verdict,
                    "harness_equals_letter": verdict == spec_letter, "harness_equals_intent": verdict == intent,
                    "false_pass_vs_intent": verdict == "PASS" and intent == "FAIL",
                    "false_fail_vs_intent": verdict == "FAIL" and intent == "PASS",
                    "rules_fired": r["rules_fired"], "h_classes_fired": r["h_classes_fired"],
                    "failing_fields": r["failing_fields"],
                    "raw_tail_lengths": [len(X["stdout_tail"]), len(Y["stdout_tail"])]})

    base = long_stdout(14)
    assert len(base) > 1500
    cut = lambda s: s[-1500:]
    # --- H9 x H8 conjunction (tails cut at 1500 by the harness capture rule)
    run("K1", rec(cut(base)), rec(cut(long_stdout(14, swap=(9, 10)))), 3, "FAIL", "PASS",
        "H9 cut tail of an H8 step; two 'ended' lines swapped inside the visible window (scheduling reorder). "
        "The header is cut away, so by the text H8 does not apply and order counts.")
    run("K2", rec(cut(base)), rec(cut(long_stdout(14, change=(10, "rows 20", "rows 21")))), 3, "FAIL", "FAIL",
        "H9 cut tail; a result token changed in a visible 'ended' line.")
    s_first = cut(base)
    first_line = s_first.splitlines(keepends=True)[0]
    tok = "rows 20" if "rows 20" in first_line else ("exit 0" if "exit 0" in first_line else None)
    if tok:
        Y = s_first.replace(first_line, first_line.replace(tok, tok[:-1] + "9"), 1)
        run("K3", rec(s_first), rec(Y), 3, "PASS", "FAIL",
            f"H9 cut tail; a result token ({tok}) changed in the partial first line, which H9 drops by text.")
    else:
        Y = s_first.replace(first_line, first_line[:-2] + "X\n", 1)
        run("K3", rec(s_first), rec(Y), 3, "PASS", "FAIL", "H9 cut tail; a change in the partial first line, which H9 drops by text.")
    full = long_stdout(14)
    Xt = cut(full)
    Xl = Xt.splitlines(keepends=True)
    header_line = full.splitlines(keepends=True)[0]
    Yt = header_line + "".join(Xl[3:])           # uncut Y: header + X's window minus its partial line and two result lines
    assert len(Yt) < 1500 and Xl[1] not in Yt and Xl[2] not in Yt
    run("K4", rec(Xt), rec(Yt), 3, "PASS", "FAIL",
        "X cut at 1500; uncut Y lacks the two 'ended' result lines at the top of X's window; H9 compares only the last "
        "k = min lines after dropping each first line, so the two missing result lines are never compared.")
    Ym = header_line + Xl[1] + Xl[2] + "".join(Xl[5:])   # two result lines missing in the middle instead
    run("K4b", rec(Xt), rec(Ym), 3, "FAIL", "FAIL", "As K4 but the two missing lines are inside the compared window.")
    # exact-length coincidence: header intact, raw length exactly 1500
    nj = max(n for n in range(1, 20) if len(long_stdout(n)) <= 1500)
    s = long_stdout(nj, header_jobs=nj)
    pad = 1500 - len(s)
    if pad > 0:
        s = s.replace("trigger: fixture", "trigger: fixture" + "x" * pad, 1)
    assert len(s) == 1500
    s_re = s.replace("abnormal False\n", "abnormal False\n", 1)
    lines = s.splitlines(keepends=True)
    lines2 = lines[:]
    e0 = 1 + nj  # first 'ended' line index
    lines2[e0 + 1], lines2[e0 + 2] = lines2[e0 + 2], lines2[e0 + 1]
    run("K5", rec(s), rec("".join(lines2)), 3, "PASS", "PASS",
        "Raw length exactly 1500 with the header intact (no truncation); two 'ended' lines swapped: H9 and H8 both apply.")
    hdr = lines[:]
    hdr[0] = hdr[0].replace(f"{nj} jobs", f"{nj - 1} jobs", 1)
    run("K6", rec(s), rec("".join(hdr)), 3, "PASS", "FAIL",
        "Raw length exactly 1500 with the header intact; the job count in the header changed: H9 drops the first line by text.")
    # --- non-H9 planted pairs beyond the 18 archived controls
    a3 = json.load(open(A3))
    st3 = a3["steps"][2]
    t = st3["stdout_tail"]

    def rec3(tail):
        r = copy.deepcopy(st3)
        r["stdout_tail"] = tail
        return r
    run("K7", rec3(t), rec3(t.replace("abnormal False", "abnormal True", 1)), 3, "FAIL", "FAIL", "H8 tail: 'abnormal False' -> 'abnormal True' in one 'ended' line.")
    ls = t.splitlines(keepends=True)
    dup = ls[:]
    dup[6] = dup[5]
    run("K8", rec3(t), rec3("".join(dup)), 3, "FAIL", "FAIL", "H8 tail: one 'ended' line duplicated in place of another (multiset changes).")
    mv = ls[:]
    mv[-1], mv[-2] = mv[-2], mv[-1]
    run("K9", rec3(t), rec3("".join(mv)), 3, "FAIL", "FAIL", "H8 tail: the last line ('attempt done') swapped with a middle line (last line is positional).")
    run("K10", rec3(t), rec3(t.replace("wall 0.074 s", "wall 0.074s", 1)), 3, "FAIL", "FAIL", "H6 near-miss: 'wall 0.074 s' -> 'wall 0.074s' (format change, not a host measurement token).")
    run("K11", rec3(t), rec3(t.replace("pid 7679;", "pid 99999;", 1)), 3, "PASS", "PASS", "H5: pid changed to a 5-digit pid.")
    run("K12", rec3(t), rec3(t.replace("(pid 7679;", "(PID 7679;", 1)), 3, "FAIL", "FAIL", "H5 near-miss: 'pid' -> 'PID' (case).")
    hd = ls[:]
    hd[0] = hd[0].replace("max 4 processes", "max 2 processes", 1)
    run("K13", rec3(t), rec3("".join(hd)), 3, "FAIL", "FAIL", "H8 header token 'max 4 processes' -> 'max 2 processes' (header compared in position).")
    st35 = a3["steps"][34]
    r35 = copy.deepcopy(st35)
    r35b = copy.deepcopy(st35)
    r35b["cmd"] = r35b["cmd"].replace("--calibration-sha256 ", "--calibration-sha256 ", 1)
    import re
    r35b["cmd"] = re.sub(r"(--calibration-sha256 )[0-9a-f]{64}", r"\g<1>" + "a" * 64, r35b["cmd"])
    run("K14", r35, r35b, 35, "PASS", "PASS", "H7 at step 35 (exit 0 both): digest replaced.")
    r35c, r35d = copy.deepcopy(st35), copy.deepcopy(r35b)
    r35c["exit_code"] = r35d["exit_code"] = 1
    r35c["expected_exit"] = r35d["expected_exit"] = 1
    run("K15", r35c, r35d, 35, "FAIL", "FAIL", "H7 not applicable when exit_code != 0: the digest change must fail.")
    r36 = copy.deepcopy(a3["steps"][35])
    r36b = copy.deepcopy(r36)
    r36b["cmd"] = re.sub(r"(--calibration-sha256 )[0-9a-f]{64}", r"\g<1>" + "b" * 64, r36b["cmd"]) if "--calibration-sha256" in r36b["cmd"] else r36b["cmd"] + " --calibration-sha256 " + "b" * 64
    run("K16", r36, r36b, 36, "FAIL", "FAIL", "H7 outside steps 35/38: a calibration digest change (or an added token) in step 36 cmd must fail.")
    r3c = copy.deepcopy(st3)
    toks = r3c["cmd"].split(" ")
    r3c["cmd"] = "/opt/other/python " + " ".join(toks[1:])
    run("K17", copy.deepcopy(st3), r3c, 3, "PASS", "PASS", "H3: interpreter path (first cmd token) changed.")
    r3d = copy.deepcopy(st3)
    r3d["cmd"] = toks[0] + " " + " ".join(toks[1:]).replace("run", "runx", 1)
    run("K18", copy.deepcopy(st3), r3d, 3, "FAIL", "FAIL", "H3 scope: a non-first cmd token changed.")
    r4 = copy.deepcopy(a3["steps"][3])
    r4b = copy.deepcopy(r4)
    if isinstance(r4b.get("check"), dict):
        r4b["check"]["validator_planted_timestamp"] = "2026-10-02T05:46:03Z"
        r4c = copy.deepcopy(r4)
        r4c["check"]["validator_planted_timestamp"] = "2027-01-01T00:00:00Z"
        run("K19", r4b, r4c, 4, "PASS", "PASS", "H1 inside a check string value: timestamp changed.")
        r4d = copy.deepcopy(r4b)
        r4d["check"]["validator_planted_timestamp"] = "2026-10-02 05:46:03"
        run("K20", r4b, r4d, 4, "FAIL", "FAIL", "H1 near-miss: ISO 'T' separator replaced by a space (not an H1 token).")
    out = {"harness": H, "harness_sha256": H_SHA, "cases": res,
           "summary": {"cases": len(res),
                       "harness_equals_spec_letter": sum(r["harness_equals_letter"] for r in res),
                       "false_pass_vs_intent": [r["id"] for r in res if r["false_pass_vs_intent"]],
                       "false_fail_vs_intent": [r["id"] for r in res if r["false_fail_vs_intent"]],
                       "harness_departs_from_letter": [r["id"] for r in res if not r["harness_equals_letter"]]}}
    json.dump(out, open(sys.argv[1], "w"), indent=1)
    for r in res:
        print(r["id"], "letter", r["spec_letter"], "intent", r["intent"], "harness", r["harness"], r["rules_fired"], r["raw_tail_lengths"])
    print(json.dumps(out["summary"]))


if __name__ == "__main__":
    main()
