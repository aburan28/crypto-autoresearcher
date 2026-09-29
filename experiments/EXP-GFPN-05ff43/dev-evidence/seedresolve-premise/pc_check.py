#!/usr/bin/env python3
"""TASK-20260924-0652ce -- zero-run, zero-solve premise check of the DRAFT
AMD-EXP-GFPN-05ff43-20260924-seedresolve (pre_approval_readings PR-1..PR-5).

Runs NO solver of any kind. A process guard installed before any frozen import makes every
child-process primitive (subprocess, fork, exec, spawn, system, popen) and v2_solver.run_child /
callgrind_instructions raise; the number of attempts is recorded (must be 0).

Frozen EXP-GFPN-05ff43 v2 code is imported READ-ONLY from implementation-v2/ (run with python3 -B /
PYTHONDONTWRITEBYTECODE=1, so no byte code is written under the frozen tree). Archives are extracted
only into the scratch directory given by --scratch.

Usage:
  PYTHONDONTWRITEBYTECODE=1 python3 -B pc_check.py --repo <repo> --scratch <scratch dir> --out <premise-check.json>

Order: PR-5 (integrity) first; on any integrity failure the script writes premise-check.json with the
failure and stops before any reading. Then PR-1, PR-2, PR-3, PR-4. It decides nothing.
"""
import argparse
import collections
import hashlib
import json
import os
import sys
import tarfile

# ----------------------------------------------------------------------------- process guard (PC-1)
GUARD_ATTEMPTS = []


def _blocked(name):
    def f(*a, **k):
        GUARD_ATTEMPTS.append(name)
        raise RuntimeError("pc_check process guard: %s is forbidden (zero-solve task)" % name)
    return f


def install_guard():
    import subprocess
    subprocess.Popen.__init__ = _blocked("subprocess.Popen")
    for nm in ("fork", "forkpty", "posix_spawn", "posix_spawnp", "system", "popen", "execv", "execve", "execvp",
               "execvpe", "execl", "execle", "execlp", "execlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe"):
        if hasattr(os, nm):
            setattr(os, nm, _blocked("os." + nm))


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


EXP = "experiments/EXP-GFPN-05ff43"
ARCH = "coordination/goals/GOAL-GFPN-380702/archives"
SEEDRESOLVE = EXP + "/amendments/v2_addendum_seedresolve.yaml"
SOLVEREVENT = EXP + "/amendments/v2_addendum_solverevent.yaml"
SOLVEREVENT_SHA = "011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f"
CHAR = EXP + "/dev-evidence/solver-characterization"
BUNDLE = EXP + "/dev-evidence/stageR1-dv7/stageR1-dv7-evidence.tar.gz"
AC = EXP + "/runs/RUN-GFPN-ac4487"
IMPL = EXP + "/implementation-v2"
RANDOM_FORM = "[coefficients of linear form are randomly chosen]"
MODE_A = "d2878f4f2b276162c78fd8b7fb31ae2fbc0a04984222a344fed047fef9cf07da"
MODE_B = "ec54fd1520eafb2216fc1c6606db5f660b8867f8d176631b9da950acf10248ee"
MODE_C = "7e283c2834f024429d50347a1cfb42d560b4eaf1b5643a818c96c9e58cb45f06"
EVENT_STEM = "fx_reg0_torsion_S3_norm"
TOY_PKG = "stageR1/dv7/toy/%s/exp/runs/RUN-GFPN-a61a10"


# ----------------------------------------------------------------------------- PR-5
def integrity(repo):
    R = lambda p: os.path.join(repo, p)
    checks = []

    def chk(name, path, expected, source):
        actual = sha256_file(R(path)) if os.path.exists(R(path)) else None
        checks.append({"check": name, "path": path, "expected": expected, "actual": actual, "source": source,
                       "pass": actual is not None and actual == expected})

    r = json.load(open(R(ARCH + "/TASK-20260923-df9fab/snapshot-receipt.json")))
    chk("PR-5(a) seedresolve draft == TASK-20260923-df9fab addendum_sha256", SEEDRESOLVE, r["addendum_sha256"]["sha256"],
        ARCH + "/TASK-20260923-df9fab/snapshot-receipt.json addendum_sha256")
    chk("PR-5(b) superseded draft", SOLVEREVENT, SOLVEREVENT_SHA, "card PC-2(b); df9fab receipt decided_draft_sha256 = %s"
        % r["decided_draft_sha256"]["sha256"])
    r = json.load(open(R(ARCH + "/TASK-20260923-683f34/snapshot-receipt.json")))
    for p, h in sorted(r["path_sha256"].items()):
        chk("PR-5(c) characterization file", p, h, ARCH + "/TASK-20260923-683f34/snapshot-receipt.json path_sha256")
    r = json.load(open(R(ARCH + "/TASK-20260923-53a47d/preservation-receipt.json")))
    chk("PR-5(d) DV-7 bundle", BUNDLE, r["path_sha256"][BUNDLE],
        ARCH + "/TASK-20260923-53a47d/preservation-receipt.json path_sha256 (CORR-20260923-9abefc value 70b83d61...)")
    r = json.load(open(R(ARCH + "/TASK-20260923-0fa03f/post-run-receipt.json")))["path_sha256"]
    ac_read = [AC + "/raw-result.json"] + sorted(AC + "/solver/" + f for f in os.listdir(R(AC + "/solver"))
                                                if f.endswith((".ms", ".ms.out", ".ms.log", ".ms.err")))
    for p in ac_read:
        chk("PR-5(e) RUN-GFPN-ac4487 file read", p, r.get(p), ARCH + "/TASK-20260923-0fa03f/post-run-receipt.json path_sha256")
    return checks


# ----------------------------------------------------------------------------- helpers
def safe_extract(tgz, dest):
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(tgz, "r:gz") as tf:
        tf.extractall(dest, filter="data")


def read_log_text(log, err):
    """Exactly v2_driver.solve lines 170-175."""
    text = ""
    for f in (log, err):
        try:
            text += open(f, errors="replace").read() + "\n"
        except OSError:
            pass
    return text


def ssf_clause(outcome, reason, text):
    """SF-1 (i)-(v) of the DRAFT seedresolve addendum."""
    if outcome == "degenerate_parametrisation" and isinstance(reason, str):
        if reason == "eliminating polynomial is not square-free":
            return "i"
        if reason.startswith("eliminating polynomial degree "):
            return "ii"
        if reason.startswith("msolve reports square-free part degree "):
            return "iii"
        if reason.endswith("parsed solution(s) fail substitution into the descended system"):
            return "iv"
    if outcome == "positive_dimensional" and RANDOM_FORM in text:
        return "v"
    return None


def classify(V, D_, ms, out, log, err, child_outcome):
    """v2_driver.solve lines 170-206 on archived bytes (no child). eqs from v2_driver._parse_ms_file(ms)."""
    names, p, eqs = D_._parse_ms_file(ms)
    text = read_log_text(log, err)
    st = V.parse_msolve_log(text)
    rec = {"outcome": child_outcome}
    kind = payload = None
    sols, sinfo, nfail = [], None, 0
    if rec["outcome"] == "ok":
        kind, payload = V.parse_msolve_param(out)
        if kind == "param":
            sols, sinfo = V.rational_solutions(payload, p, len(names))
            nfail = sum(1 for s in sols if not V.substitute(eqs, s, p))
    outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail)
    if outcome == "ok":
        Dq = st["dimension_of_quotient"]
        if kind == "none" or (st["no_solution"] and not Dq):
            D, kept = None, []
        else:
            D, kept = Dq, [s for s in sols if V.substitute(eqs, s, p)]
    else:
        D, kept = None, []
    solset = sorted(tuple(int(v) for v in s) for s in sols)
    res = {
        "child_outcome_as_recorded": child_outcome,
        "outcome": outcome, "reason": reason, "n_sub_fail": nfail, "D_as_driver_would_record": D,
        "parse_kind": kind, "header_degree": (payload or {}).get("degree") if kind == "param" else None,
        "elim_degree": (sinfo or {}).get("elim_degree"), "elim_squarefree": (sinfo or {}).get("elim_squarefree"),
        "n_rational_solutions": len(solset), "rational_solutions": [list(s) for s in solset],
        "n_solutions_driver_keeps": len(kept),
        "solution_set_sha256": sha256_bytes(json.dumps(solset).encode()),
        "dimension_of_quotient_printed": st["dimension_of_quotient"],
        "squarefree_degree_printed": st["fglm"].get("squarefree_degree"),
        "positive_dimension_reported": st["positive_dimension_reported"],
        "random_linear_form_string_in_log": RANDOM_FORM in text,
        "ssf_clause": ssf_clause(outcome, reason, text),
        "log_sha256": sha256_file(log) if os.path.exists(log) else None,
        "err_sha256": sha256_file(err) if os.path.exists(err) else None,
    }
    return res


def parsed_key(c):
    """SE-4 (d) d-parsed comparison (solverevent lines 326-331; seedresolve SF-4): parse kind, header degree,
    eliminating degree, square-free flag, F_p-rational solution set (as a set), D."""
    return [c["parse_kind"], c["header_degree"], c["elim_degree"], c["elim_squarefree"], c["solution_set_sha256"],
            c["D_as_driver_would_record"]]


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


def records_by_tag(raw_path):
    out = {}
    for o in find_solver_records(json.load(open(raw_path))):
        a = o["solver"]["argv"]
        tag = os.path.basename(a[a.index("-f") + 1])[:-3]
        out.setdefault(tag, []).append(o)
    return out


def code_line(repo, rel, lineno):
    with open(os.path.join(repo, rel)) as fh:
        lines = fh.read().split("\n")
    return lines[lineno - 1]


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    repo, scratch = os.path.abspath(a.repo), os.path.abspath(a.scratch)
    install_guard()
    result = {"task_id": "TASK-20260924-0652ce", "experiment_id": "EXP-GFPN-05ff43",
              "draft": "AMD-EXP-GFPN-05ff43-20260924-seedresolve (DRAFT, not approved)",
              "kind": "zero-run, zero-solve premise check; observations only; decides nothing",
              "python": sys.version, "scratch": scratch}

    impl_files = sorted(f for f in os.listdir(os.path.join(repo, IMPL)) if f.endswith(".py"))
    impl_before = {f: sha256_file(os.path.join(repo, IMPL, f)) for f in impl_files}

    # ---- PR-5 integrity FIRST
    checks = integrity(repo)
    result["PR5_integrity"] = {"checks": checks, "n_checks": len(checks), "n_fail": sum(1 for c in checks if not c["pass"])}
    if result["PR5_integrity"]["n_fail"]:
        result["status"] = "STOPPED at PR-5 integrity (card PC-2); nothing read as a result"
        result["guard_attempts"] = GUARD_ATTEMPTS
        json.dump(result, open(a.out, "w"), indent=1, sort_keys=False)
        print("STOP: integrity failure")
        return 2

    # ---- frozen imports (read-only; guard active)
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(repo, IMPL))
    import v2_solver as V          # noqa: E402
    V.run_child = _blocked("v2_solver.run_child")
    V._run_child_locked = _blocked("v2_solver._run_child_locked")
    V.callgrind_instructions = _blocked("v2_solver.callgrind_instructions")
    import v2_arms as A            # noqa: E402
    import v2_driver as D_         # noqa: E402
    result["frozen_imports"] = {m.__name__: os.path.relpath(m.__file__, repo) for m in (V, A, D_)}

    # ---- extraction (scratch only)
    bdir, ddir = os.path.join(scratch, "dv7"), os.path.join(scratch, "distinct")
    safe_extract(os.path.join(repo, BUNDLE), bdir)
    safe_extract(os.path.join(repo, CHAR, "distinct-outputs.tar.gz"), ddir)
    wB = os.path.join(bdir, TOY_PKG % "world_B")
    wA = os.path.join(bdir, TOY_PKG % "world_A")
    acd = os.path.join(repo, AC)

    # ---- PR-1 (a): 72 round trips
    rt_dir = os.path.join(scratch, "roundtrip")
    os.makedirs(rt_dir, exist_ok=True)
    ms_files = [("toy_worldB_G1", os.path.join(wB, "solver", f)) for f in sorted(os.listdir(os.path.join(wB, "solver"))) if f.endswith(".ms")]
    ms_files += [("RUN-GFPN-ac4487", os.path.join(acd, "solver", f)) for f in sorted(os.listdir(os.path.join(acd, "solver"))) if f.endswith(".ms")]
    raw_ac = records_by_tag(os.path.join(acd, "raw-result.json"))
    raw_wB = records_by_tag(os.path.join(wB, "raw-result.json"))
    raw_wA = records_by_tag(os.path.join(wA, "raw-result.json"))
    rt = []
    for setname, f in ms_files:
        stem = os.path.basename(f)[:-3]
        names, p, eqs = D_._parse_ms_file(f)
        # ADAPTER: none. _parse_ms_file returns (list[str], int, list[dict[tuple[int,...], int]]), which is the
        # representation write_msolve_input(path, names, p, eqs) consumes; the triple is passed unchanged.
        tmp = os.path.join(rt_dir, setname + "__" + stem + ".ms")
        wi = A.write_msolve_input(tmp, names, p, eqs)
        b0, b1 = open(f, "rb").read(), open(tmp, "rb").read()
        first = None
        if b0 != b1:
            first = next((i for i in range(min(len(b0), len(b1))) if b0[i] != b1[i]), min(len(b0), len(b1)))
        raw = (raw_ac if setname == "RUN-GFPN-ac4487" else raw_wB).get(stem, [{}])[0]
        coeff_range_ok = all(0 < c < p for eq in eqs for c in eq.values())
        rt.append({"set": setname, "stem": stem, "sha256": sha256_bytes(b0), "bytes": len(b0), "p": p, "nvars": len(names),
                   "n_equations_parsed": len(eqs), "n_terms_parsed": sum(len(e) for e in eqs),
                   "write_return": wi, "byte_identical": b0 == b1, "first_differing_byte_offset": first,
                   "parsed_coefficients_in_1_to_p_minus_1": coeff_range_ok,
                   "raw_result_input_sha256": (raw.get("input") or {}).get("sha256"),
                   "raw_result_input_sha256_equal": (raw.get("input") or {}).get("sha256") == sha256_bytes(b0),
                   "raw_result_n_zero_equations_dropped": (raw.get("input") or {}).get("n_zero_equations_dropped")})
    wA_ms_equal = {}
    for f in sorted(os.listdir(os.path.join(wA, "solver"))):
        if f.endswith(".ms"):
            wA_ms_equal[f[:-3]] = sha256_file(os.path.join(wA, "solver", f)) == sha256_file(os.path.join(wB, "solver", f))
    result["PR1a_roundtrip"] = {
        "n_inputs": len(rt), "n_toy": sum(1 for r in rt if r["set"] == "toy_worldB_G1"),
        "n_ac4487": sum(1 for r in rt if r["set"] == "RUN-GFPN-ac4487"),
        "n_byte_identical": sum(1 for r in rt if r["byte_identical"]),
        "mismatches": [{k: r[k] for k in ("set", "stem", "first_differing_byte_offset")} for r in rt if not r["byte_identical"]],
        "event_input_included": any(r["set"] == "toy_worldB_G1" and r["stem"] == EVENT_STEM for r in rt),
        "adapter": "none (identity: the parsed triple is passed to write_msolve_input unchanged)",
        "world_A_toy_ms_equal_world_B": {"n": len(wA_ms_equal), "n_equal": sum(wA_ms_equal.values())},
        "per_input": rt}

    # ---- PR-1 (b) / PR-3: code facts quoted by line (read, not executed)
    drv, sol, arm = IMPL + "/v2_driver.py", IMPL + "/v2_solver.py", IMPL + "/v2_arms.py"
    quote = lambda rel, lines: {str(n): code_line(repo, rel, n) for n in lines}
    result["code_quotes"] = {
        "v2_driver.py": quote(drv, [158, 159, 162, 166, 170, 171, 172, 173, 176, 184, 187, 188, 189, 190, 191, 192, 193, 194, 195,
                                    196, 197, 199, 200, 201, 204, 206, 207, 211, 217, 219, 221, 224, 227, 358, 565, 582, 597, 606,
                                    607, 608, 693, 711, 786, 787, 841, 1141, 1149, 1150, 1174]),
        "v2_solver.py": quote(sol, [473, 478, 481, 482, 483, 488, 490, 492, 494, 496, 497, 498, 500, 501, 503, 504, 505, 506, 507, 508]),
        "v2_arms.py": quote(arm, [678, 684, 686, 647, 649, 650, 691, 697, 698, 699, 701, 702, 703, 704, 706, 708, 717, 721]),
    }

    # ---- PR-2: set O, classification with substitution
    idx = json.load(open(os.path.join(ddir, "distinct-outputs", "index.json")))
    solves = collections.defaultdict(list)
    with open(os.path.join(repo, CHAR, "solves.jsonl")) as fh:
        for line in fh:
            r = json.loads(line)
            solves[(r["class"], r["input_key"], r["rep"])].append(r)
    by_key = collections.defaultdict(list)
    for (cls, key, rep), rs in solves.items():
        for r in rs:
            by_key[key].append(r)

    def modal(key):   # char_msolve.py lines 557-568: default flags, ok-exited, ties -> smallest sha256
        cnt = collections.Counter(r["output_sha256"] for r in by_key[key] if not r["flags"] and r["run_child"]["outcome"] == "ok"
                                  and r["output_sha256"])
        top = max(cnt.values())
        return sorted(s for s, v in cnt.items() if v == top)[0], dict(cnt)

    O = []   # (input_key, output sha, output path, input .ms path, [(log source label, log, err, child outcome)])

    def logsrc_pkg(label, d, stem, raw):
        recs = raw.get(stem) or [{}]
        co = (recs[0].get("solver") or {}).get("outcome")
        argv = (recs[0].get("solver") or {}).get("argv") or []
        return (label, os.path.join(d, "solver", stem + ".ms.log"), os.path.join(d, "solver", stem + ".ms.err"), co,
                {"argv_tail": argv[-2:], "raw_result_outcome": recs[0].get("outcome"), "raw_result_reason": recs[0].get("reason"),
                 "raw_result_D": recs[0].get("D"), "raw_result_substitution_failures": recs[0].get("substitution_failures")})

    def logsrc_char(cls, key, rep, tardir):
        r = solves[(cls, key, rep)][0]
        base = os.path.join(ddir, "logs", cls, key, "r%04d" % rep)
        return ("characterization %s#%d (distinct-outputs.tar.gz logs/)" % (cls, rep), base + ".ms.log", base + ".ms.err",
                r["run_child"]["outcome"],
                {"argv_tail": r["run_child"]["argv"][-2:], "flags": r["flags"], "jsonl_output_sha256": r["output_sha256"],
                 "jsonl_log_sha256": r["log_sha256"], "jsonl_err_sha256": r["err_sha256"], "start_utc": r["start_utc"]})

    event_ms = os.path.join(wB, "solver", EVENT_STEM + ".ms")
    # event input: world B (bundle), world A (bundle), mode B (distinct-outputs + logs)
    O.append(("event/" + EVENT_STEM, "world B (bundle)", os.path.join(wB, "solver", EVENT_STEM + ".ms.out"), event_ms,
              [logsrc_pkg("bundle toy world_B RUN-GFPN-a61a10 solver/" + EVENT_STEM, wB, EVENT_STEM, raw_wB)]))
    O.append(("event/" + EVENT_STEM, "world A (bundle)", os.path.join(wA, "solver", EVENT_STEM + ".ms.out"),
              os.path.join(wA, "solver", EVENT_STEM + ".ms"),
              [logsrc_pkg("bundle toy world_A RUN-GFPN-a61a10 solver/" + EVENT_STEM, wA, EVENT_STEM, raw_wA)]))
    # every distinct default-flag output in distinct-outputs.tar.gz
    for key in sorted(idx):
        setn, stem = key.split("/")
        for sha, labs in sorted(idx[key].items()):
            default_labels = [l for l in labs if not l.startswith("C-3c")]
            if not default_labels:
                continue          # flagged-only output (-c 0 / -c 1): not default-flag, not in O
            outp = os.path.join(ddir, "distinct-outputs", key, sha + ".ms.out")
            if setn == "event":
                ms = event_ms
            elif setn == "toy35":
                ms = os.path.join(wB, "solver", stem + ".ms")
            else:
                ms = os.path.join(acd, "solver", stem + ".ms")
            srcs = []
            # logs of solves that produced exactly these bytes
            for l in default_labels:
                cls, rep = l.split("#")
                base = os.path.join(ddir, "logs", cls, key, "r%04d" % int(rep))
                if os.path.exists(base + ".ms.log"):
                    srcs.append(logsrc_char(cls, key, int(rep), ddir))
            if setn == "event" and os.path.exists(os.path.join(wB, "solver", stem + ".ms.out")) and \
                    sha256_file(os.path.join(wB, "solver", stem + ".ms.out")) == sha:
                srcs.append(logsrc_pkg("bundle toy world_B RUN-GFPN-a61a10 solver/" + stem, wB, stem, raw_wB))
            if setn == "toy35":
                for lab, d, raw in (("world_B", wB, raw_wB), ("world_A", wA, raw_wA)):
                    f = os.path.join(d, "solver", stem + ".ms.out")
                    if os.path.exists(f) and sha256_file(f) == sha:
                        srcs.append(logsrc_pkg("bundle toy %s RUN-GFPN-a61a10 solver/%s" % (lab, stem), d, stem, raw))
            if setn == "ac4487":
                f = os.path.join(acd, "solver", stem + ".ms.out")
                if sha256_file(f) == sha:
                    srcs.append(logsrc_pkg("RUN-GFPN-ac4487 solver/" + stem, acd, stem, raw_ac))
            O.append((key, "distinct-outputs.tar.gz (%d default-flag solves)" % len(default_labels), outp, ms, srcs))
    # the 36 archived RUN-GFPN-ac4487 .ms.out (dedupe against the entries above by (key, sha))
    for f in sorted(os.listdir(os.path.join(acd, "solver"))):
        if f.endswith(".ms.out"):
            stem = f[:-7]
            O.append(("ac4487/" + stem, "RUN-GFPN-ac4487 archived", os.path.join(acd, "solver", f),
                      os.path.join(acd, "solver", stem + ".ms"), [logsrc_pkg("RUN-GFPN-ac4487 solver/" + stem, acd, stem, raw_ac)]))

    merged = collections.OrderedDict()
    for key, src, outp, ms, srcs in O:
        sha = sha256_file(outp)
        k = (key, sha)
        if k not in merged:
            merged[k] = {"input_key": key, "output_sha256": sha, "found_in": [], "output_path": outp, "input_ms": ms, "logs": []}
        merged[k]["found_in"].append(src)
        seen = {l[0] for l in merged[k]["logs"]}
        merged[k]["logs"] += [l for l in srcs if l[0] not in seen]

    modal_of = {}
    entries = []
    for (key, sha), e in merged.items():
        ms = e["input_ms"]
        ent = {"input_key": key, "output_sha256": sha, "found_in": e["found_in"],
               "input_ms_sha256": sha256_file(ms), "input_ms": os.path.relpath(ms, scratch) if ms.startswith(scratch) else os.path.relpath(ms, repo),
               "output_bytes": os.path.getsize(e["output_path"]), "log_available": bool(e["logs"]), "classifications": []}
        for lab, log, err, co, meta in e["logs"]:
            c = classify(V, D_, ms, e["output_path"], log, err, co)
            c["log_source"] = lab
            c["log_source_meta"] = meta
            if "jsonl_log_sha256" in meta:
                c["log_bytes_match_jsonl"] = (c["log_sha256"] == meta["jsonl_log_sha256"] and c["err_sha256"] == meta["jsonl_err_sha256"]
                                              and meta["jsonl_output_sha256"] == sha)
            ent["classifications"].append(c)
        if ent["classifications"]:
            ks = {json.dumps(parsed_key(c)) + "|" + str(c["outcome"]) + "|" + str(c["reason"]) + "|" + str(c["ssf_clause"])
                  for c in ent["classifications"]}
            ent["all_logs_agree"] = len(ks) == 1
            ent["primary"] = ent["classifications"][0]
        entries.append(ent)
        if key not in modal_of and key in by_key:
            modal_of[key] = modal(key)

    prim = {(e["input_key"], e["output_sha256"]): e.get("primary") for e in entries}
    for e in entries:
        m, cnt = modal_of.get(e["input_key"], (None, {}))
        e["modal_output_sha256"] = m
        e["default_flag_counts_by_output"] = cnt
        e["is_modal"] = e["output_sha256"] == m
        mp = prim.get((e["input_key"], m))
        if e.get("primary") and mp:
            e["parsed_equal_to_modal"] = parsed_key(e["primary"]) == parsed_key(mp)
        else:
            e["parsed_equal_to_modal"] = None
        # the characterization's own (n_sub_fail = 0) record for this output, if any
        rr = [r for r in by_key.get(e["input_key"], []) if r["output_sha256"] == e["output_sha256"] and not r["flags"]]
        if rr:
            c0 = rr[0]["classification"]
            e["characterization_record_n_sub_fail_0"] = {k: c0.get(k) for k in ("classify_outcome", "classify_reason",
                                                                                 "D_as_driver_would_record", "solution_set_sha256",
                                                                                 "n_rational_solutions")}
            e["characterization_default_flag_solves_with_this_output"] = len(rr)

    result["PR2_output_set_O"] = {"n_outputs": len(entries),
                                  "by_set": dict(collections.Counter(e["input_key"].split("/")[0] for e in entries)),
                                  "entries": entries}

    # readings PR-2 (a)-(e)
    def get(sha, key=None):
        return [e for e in entries if e["output_sha256"] == sha and (key is None or e["input_key"] == key)]

    def clauses(e):
        return sorted({c["ssf_clause"] for c in e["classifications"]}, key=str)

    rd = {}
    eB = get(MODE_B)
    rd["a"] = {"text": "ec54fd15... (mode B) must have SSF clause (iv)", "instances": [
        {"input_key": e["input_key"], "per_log": [(c["log_source"], c["outcome"], c["reason"], c["n_sub_fail"], c["ssf_clause"])
                                                  for c in e["classifications"]]} for e in eB],
        "holds": bool(eB) and all(c["ssf_clause"] == "iv" for e in eB for c in e["classifications"]) and all(e["classifications"] for e in eB)}
    eA = get(MODE_A)
    rd["b"] = {"text": "d2878f4f... (mode A) must have SSF clause (ii)", "instances": [
        {"input_key": e["input_key"], "per_log": [(c["log_source"], c["outcome"], c["reason"], c["n_sub_fail"], c["ssf_clause"])
                                                  for c in e["classifications"]]} for e in eA],
        "holds": bool(eA) and all(c["ssf_clause"] == "ii" for e in eA for c in e["classifications"]) and all(e["classifications"] for e in eA)}
    diff = [e for e in entries if e["parsed_equal_to_modal"] is False]
    rd["c"] = {"text": "every output in O whose SE-4 (d) parsed comparison differs from its input's modal output must have the SSF signature",
               "instances": [{"input_key": e["input_key"], "output_sha256": e["output_sha256"], "ssf_clauses_over_logs": clauses(e)}
                             for e in diff],
               "not_comparable": [(e["input_key"], e["output_sha256"]) for e in entries if e["parsed_equal_to_modal"] is None],
               "holds": all(all(c["ssf_clause"] for c in e["classifications"]) for e in diff)}
    dd = []
    for e in entries:
        if e["input_key"].startswith("ac4487/") and "RUN-GFPN-ac4487 archived" in e["found_in"]:
            stem = e["input_key"].split("/")[1]
            rec = raw_ac[stem][0]
            c = [c for c in e["classifications"] if c["log_source"].startswith("RUN-GFPN-ac4487")][0]
            dd.append({"tag": stem, "output_sha256": e["output_sha256"], "outcome": c["outcome"], "n_sub_fail": c["n_sub_fail"],
                       "D": c["D_as_driver_would_record"], "raw_result_D": rec.get("D"),
                       "raw_result_outcome": rec.get("outcome"), "raw_result_substitution_failures": rec.get("substitution_failures"),
                       "raw_result_n_rational_solutions": rec.get("n_rational_solutions"), "n_rational_solutions": c["n_rational_solutions"],
                       "holds": c["outcome"] == "ok" and c["n_sub_fail"] == 0 and c["D_as_driver_would_record"] == rec.get("D")})
    rd["d"] = {"text": "every archived RUN-GFPN-ac4487 output must classify ok, with substitution_failures 0 and D equal to raw-result.json's D for that tag",
               "n": len(dd), "n_hold": sum(1 for x in dd if x["holds"]), "instances": dd, "holds": len(dd) == 36 and all(x["holds"] for x in dd)}
    eC = get(MODE_C)
    rd["e"] = {"text": "7e283c28... (mode C) must classify ok with substitution_failures 0", "instances": [
        {"input_key": e["input_key"], "per_log": [(c["log_source"], c["outcome"], c["reason"], c["n_sub_fail"], c["ssf_clause"])
                                                  for c in e["classifications"]]} for e in eC],
        "holds": bool(eC) and all(c["outcome"] == "ok" and c["n_sub_fail"] == 0 for e in eC for c in e["classifications"])
        and all(e["classifications"] for e in eC)}
    rd["other_outputs_with_ssf"] = [{"input_key": e["input_key"], "output_sha256": e["output_sha256"], "clauses": clauses(e)}
                                    for e in entries if any(c["ssf_clause"] for c in e["classifications"])
                                    and e["output_sha256"] not in (MODE_A, MODE_B)]
    result["PR2_readings"] = rd

    # ---- PR-4
    result["PR4_log_availability"] = {"n_outputs": len(entries), "n_with_log": sum(1 for e in entries if e["log_available"]),
                                      "gaps": [(e["input_key"], e["output_sha256"]) for e in entries if not e["log_available"]]}

    # ---- closing checks
    impl_after = {f: sha256_file(os.path.join(repo, IMPL, f)) for f in impl_files}
    result["frozen_v2_code_sha256"] = impl_before
    result["frozen_v2_code_unchanged"] = impl_before == impl_after
    result["pycache_under_impl_v2"] = os.path.exists(os.path.join(repo, IMPL, "__pycache__"))
    result["guard_attempts"] = GUARD_ATTEMPTS
    result["msolve_children_launched"] = 0 if not GUARD_ATTEMPTS else "guard fired: %r" % GUARD_ATTEMPTS
    result["status"] = "completed"
    with open(a.out, "w") as fh:
        json.dump(result, fh, indent=1)
        fh.write("\n")
    print("done", result["PR5_integrity"]["n_checks"], "integrity checks;", len(entries), "outputs in O")
    return 0


if __name__ == "__main__":
    sys.exit(main())
