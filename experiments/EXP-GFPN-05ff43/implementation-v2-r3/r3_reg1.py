#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-r3 -- the REG-1 COMPARATOR (paristack PS-4 regression_REG-1 as amended by the
incorporated solverevent SE-4, with the (d) branch fixed to d-parsed by seedresolve SF-4; RC-6, RC-7; launchcover CG-4
unchanged). Started from implementation-v2-r2/r2_reg1.py: the comparison (a)-(d), the exclusion list X1..X17 and the
reference-integrity rule are unchanged; the only change is that the SE-4 (e) test reads the r3 solver-events.json
structure (DEC-20260924-e52eec VA-6 (b)).

usage: python3 -B r3_reg1.py --candidate RUN_DIR [--reference RUN_DIR] [--receipt PATH] [--json OUT]

G1 (the r3 image of RUN-GFPN-ac4487) must reproduce RUN-GFPN-ac4487 on its deterministic content. Before comparing,
EVERY reference file read is verified against the TASK-20260923-0fa03f post-run receipt path_sha256; a mismatch, or a
reference file the receipt does not bind, is FATAL (verdict FAIL). Compared:
  (a) solver/*.ms: same file set, byte-identical (unchanged);
  (b) raw-result.json, as the r1 comparator lists it (unchanged): run_status / failure_class / gate_pass; every entry
      of targets, planted_targets and replaced_fresh_targets (whole, minus the declared exclusions) and the D table;
      structure_checks; fixture_F1; fixture_F2a; fixture_F2b; fixture_F3; group; rescaling; curve_checks; fresh
      targets' k (from certificates) and x_R; the certificate block; metrics (minus X2);
  (c) certificates/*.json: same file set, equal as JSON after the declared exclusions (unchanged);
  (d) d-parsed (SF-4): solver/*.ms.out of the RECORDED attempts (renamed *.ssf-attempt<k> files do not match the
      glob): same file set, and for each file equal parse kind, header degree, eliminating-polynomial degree and
      square-free flag, F_p-rational solution set as v2_solver.rational_solutions returns it (as a set), and D (the
      quotient dimension printed in the recorded attempt's .ms.log). No tolerance on any value.
  SE-4 (e): the exclusion list is X1..X17 carried verbatim (reg1-exclusion-list.json, byte-identical to
      implementation-v2-r2/reg1-exclusion-list.json); NOTHING is added. solver-events.json and the *.ssf-attempt<k>
      files are outside the compared sets by the globs; they are not exclusions. The output lists each of them with
      its sha256 and quotes the candidate's solver-events.json in full (report only). REG-1 FAILS if the candidate's
      solver-events.json is missing or does not parse, or if it records an SE-2 (4) / HR-5 consistency violation: the
      top-level flag, or an S-1 or S-2 event whose consistency record is not ok (VA-6 (b); epsilon). The callgrind-site
      records (V-5) are quoted, never tested (VA-6 (c)).
The complete output is deterministic text meant to be quoted verbatim (RC-7). It imports the frozen v2_solver
read-only (parse functions only); no v2_common, v2_driver or v2-a1 module.
"""
import argparse
import copy
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r3_common as R                                    # noqa: E402
import r3_accounting as ACC                              # noqa: E402

B_WHOLE_ITEMS = ["structure_checks", "fixture_F1", "fixture_F2a", "fixture_F2b", "fixture_F3", "group", "rescaling", "curve_checks", "certificate"]
TARGET_LISTS = ["targets", "planted_targets", "replaced_fresh_targets"]


def load_exclusions(path=None):
    path = path or R.REG1_EXCLUSION_LIST
    raw = open(path, "rb").read()
    ex = json.loads(raw)
    never = set(ex["never_excludable"])
    for e in ex["entries"]:
        bad = [k for k in e["path"] if k in never]
        if bad:
            raise ValueError("exclusion %s names a never-excludable field %s" % (e["id"], bad))
        if e["category"] not in ex["permitted_categories"]:
            raise ValueError("exclusion %s has a category outside PS-4 (e): %s" % (e["id"], e["category"]))
    if [e["id"] for e in ex["entries"]] != ["X%d" % i for i in range(1, 18)]:
        raise ValueError("the exclusion list is not exactly X1..X17 (SE-4 (e): nothing added)")
    return ex, R.sha256_bytes(raw)


def _strip(obj, path):
    if not path:
        return
    head, rest = path[0], path[1:]
    if isinstance(obj, dict):
        keys = list(obj.keys()) if head == "*" else ([head] if head in obj else [])
        for k in keys:
            if not rest:
                del obj[k]
            else:
                _strip(obj[k], rest)
    elif isinstance(obj, list) and head == "*" and rest:
        for v in obj:
            _strip(v, rest)


def strip(obj, exclusions, scope):
    obj = copy.deepcopy(obj)
    for e in exclusions["entries"]:
        if e["scope"] == scope:
            _strip(obj, e["path"])
    return obj


def d_table(raw):
    out = {}
    for lst in TARGET_LISTS:
        for t in raw.get(lst) or []:
            out["%s:%s" % (lst, t.get("target"))] = {a: {"outcome": v.get("outcome"), "D": v.get("D"), "D_defined": v.get("D_defined")}
                                                    for a, v in sorted((t.get("arms") or {}).items())}
    return out


def fresh_k_xR(raw, certs):
    ks = {}
    for name, c in certs.items():
        if c.get("target_kind") == "fresh_random":
            ks.setdefault(c["target_index"], set()).add(c["k"])
    out = {}
    for t in raw.get("targets") or []:
        if t.get("kind") == "fresh_random":
            k = ks.get(t["target"])
            out[t["target"]] = {"x_R": t.get("x_R"), "k": sorted(k) if k else None}
    return out


class Reader:
    """Reads files of one run directory; for the reference, verifies each against the receipt (fatal)."""

    def __init__(self, rd, bound=None):
        self.rd, self.bound, self.integrity = rd, bound, []

    def path(self, rel):
        return os.path.join(self.rd, rel)

    def read(self, rel):
        p = self.path(rel)
        b = open(p, "rb").read()
        if self.bound is not None:
            key = os.path.relpath(p, R.REPO)
            want = self.bound.get(key)
            got = R.sha256_bytes(b)
            self.integrity.append({"path": key, "bound": want is not None, "matches_receipt": want == got})
        return b

    def ok(self):
        return all(x["bound"] and x["matches_receipt"] for x in self.integrity)


def parsed_key(reader, stem):
    """SF-4 d-parsed key of solver/<stem>.ms.out: parse kind, header degree, eliminating degree, square-free flag,
    F_p-rational solution set (as a set), D. Every file read goes through the reader (receipt-verified for the
    reference)."""
    import tempfile
    V = ACC._v2()
    rel_out, rel_ms, rel_log, rel_err = ("solver/" + stem + ext for ext in (".ms.out", ".ms", ".ms.log", ".ms.err"))
    ob = reader.read(rel_out)
    text = ""
    for rel in (rel_log, rel_err):
        if os.path.exists(reader.path(rel)):
            text += reader.read(rel).decode(errors="replace") + "\n"
    st = V.parse_msolve_log(text)
    with tempfile.NamedTemporaryFile("wb", suffix=".ms.out", delete=False) as fh:
        fh.write(ob)
        tmp = fh.name
    try:
        kind, payload = V.parse_msolve_param(tmp)
    finally:
        os.remove(tmp)
    key = {"parse_kind": kind, "header_degree": None, "elim_degree": None, "elim_squarefree": None,
           "rational_solution_set": None, "D": st["dimension_of_quotient"]}
    if kind == "param":
        if os.path.exists(reader.path(rel_ms)):
            head = reader.read(rel_ms).decode().split("\n", 2)
            nvars, p = len(head[0].strip().split(",")), int(head[1].strip())
        else:
            nvars = len(payload["varnames"]) - (1 if ACC.EXTRA_VAR_LINE in text else 0)
            p = int(payload["char"])
        sols, sinfo = V.rational_solutions(payload, p, nvars)
        key.update(header_degree=payload.get("degree"), elim_degree=sinfo.get("elim_degree"),
                   elim_squarefree=sinfo.get("elim_squarefree"),
                   rational_solution_set=sorted({tuple(int(x) for x in s) for s in sols}))
    return key


def solver_events_check(candidate):
    """SE-4 (e) as VA-6 (b) reads it: the file exists and parses; the top-level consistency flag; the consistency
    records of the S-1 and S-2 events and their per-site counters, each read by CONSTANT key. The S-3 (callgrind-site)
    records are never read here (VA-6 (c)); the whole file is quoted by the caller (report only)."""
    p = os.path.join(candidate, "solver-events.json")
    rep = {"path": "solver-events.json", "present": os.path.exists(p)}
    fails = []
    if not rep["present"]:
        fails.append("(SE-4) candidate solver-events.json is missing")
        return rep, fails, None
    raw = open(p, "rb").read()
    rep["sha256"] = R.sha256_bytes(raw)
    try:
        doc = json.loads(raw)
    except Exception as e:                               # noqa: BLE001
        rep["parses"] = False
        fails.append("(SE-4) candidate solver-events.json does not parse: %r" % (e,))
        return rep, fails, raw.decode(errors="replace")
    rep["parses"] = True
    sites = doc.get("sites") or {}
    s1 = sites.get(R.SITE_S1) or {}
    s2 = sites.get(R.SITE_S2) or {}
    ev_bad = [e.get("tag") for e in (s1.get("events") or []) + (s2.get("events") or []) if not (e.get("consistency") or {}).get("ok", True)]
    viol = bool(doc.get("consistency_violation")) or bool(ev_bad)
    rep["consistency_violation_recorded"] = viol
    if viol:
        fails.append("(SE-4) candidate solver-events.json records an SE-2 (4) / HR-5 consistency violation")
    rep["counters"] = {R.SITE_S1: s1.get("counters"), R.SITE_S2: s2.get("counters")}
    return rep, fails, raw.decode(errors="replace")


def compare(reference, candidate, receipt=None, exclusion_path=None):
    ex, ex_sha = load_exclusions(exclusion_path)
    receipt = receipt or R.RECEIPT_V2_PHASE_B
    bound = R.receipt_paths(R.load_json(receipt))
    ref, cand = Reader(reference, bound), Reader(candidate)
    rep = {"reg1": "REG-1", "d_branch": R.REG1_D_BRANCH, "reference": os.path.relpath(reference, R.REPO),
           "candidate": os.path.relpath(candidate, R.REPO), "reference_receipt": os.path.relpath(receipt, R.REPO),
           "exclusion_list": os.path.relpath(exclusion_path or R.REG1_EXCLUSION_LIST, R.REPO),
           "exclusion_list_sha256": ex_sha, "a": [], "b": [], "c": [], "d": []}
    fails = []
    # (a) byte-identical inputs
    rs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(reference, "solver", "*.ms")))
    cs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(candidate, "solver", "*.ms")))
    if rs != cs:
        rep["a"].append({"file_set": "differs", "only_reference": sorted(set(rs) - set(cs)), "only_candidate": sorted(set(cs) - set(rs))})
        fails.append("(a) file set differs")
    for f in sorted(set(rs) & set(cs)):
        eq = ref.read(os.path.join("solver", f)) == cand.read(os.path.join("solver", f))
        rep["a"].append({"file": "solver/" + f, "byte_identical": eq})
        if not eq:
            fails.append("(a) solver/%s differs" % f)
    # (d) d-parsed on the recorded attempts' outputs
    rs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(reference, "solver", "*.ms.out")))
    cs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(candidate, "solver", "*.ms.out")))
    if rs != cs:
        rep["d"].append({"file_set": "differs", "only_reference": sorted(set(rs) - set(cs)), "only_candidate": sorted(set(cs) - set(rs))})
        fails.append("(d) file set differs")
    for f in sorted(set(rs) & set(cs)):
        stem = f[:-len(".ms.out")]
        kr, kc = parsed_key(ref, stem), parsed_key(cand, stem)
        diff = sorted(k for k in kr if kr[k] != kc[k])
        rep["d"].append({"file": "solver/" + f, "parsed_equal": not diff, "differing_fields": diff,
                         "reference_key": {k: (v if k != "rational_solution_set" else {"n": len(v or []), "set": v}) for k, v in kr.items()},
                         "candidate_key": {k: (v if k != "rational_solution_set" else {"n": len(v or []), "set": v}) for k, v in kc.items()}})
        if diff:
            fails.append("(d) solver/%s differs in %s" % (f, diff))
    # (c)
    rc = sorted(os.path.basename(x) for x in glob.glob(os.path.join(reference, "certificates", "*.json")))
    cc = sorted(os.path.basename(x) for x in glob.glob(os.path.join(candidate, "certificates", "*.json")))
    rcert, ccert = {}, {}
    if rc != cc:
        rep["c"].append({"file_set": "differs", "only_reference": sorted(set(rc) - set(cc)), "only_candidate": sorted(set(cc) - set(rc))})
        fails.append("(c) certificate file set differs")
    for f in rc:
        rcert[f] = json.loads(ref.read(os.path.join("certificates", f)))
    for f in cc:
        ccert[f] = json.loads(cand.read(os.path.join("certificates", f)))
    for f in sorted(set(rc) & set(cc)):
        eq = strip(rcert[f], ex, "certificate") == strip(ccert[f], ex, "certificate")
        rep["c"].append({"file": "certificates/" + f, "equal_after_exclusions": eq})
        if not eq:
            fails.append("(c) certificates/%s differs" % f)
    # (b)
    rraw = json.loads(ref.read("raw-result.json"))
    craw = json.loads(cand.read("raw-result.json"))

    def b(name, rv, cv):
        eq = rv == cv
        rep["b"].append({"item": name, "equal": eq})
        if not eq:
            fails.append("(b) %s differs" % name)
    b("run_status/failure_class/gate_pass", [rraw.get(k) for k in ("run_status", "failure_class", "gate_pass")],
      [craw.get(k) for k in ("run_status", "failure_class", "gate_pass")])
    b("D_table", d_table(rraw), d_table(craw))
    for lst in TARGET_LISTS:
        rl, cl = rraw.get(lst) or [], craw.get(lst) or []
        b("%s[count]" % lst, len(rl), len(cl))
        for i in range(max(len(rl), len(cl))):
            rv = strip(rl[i], ex, "target-entry") if i < len(rl) else None
            cv = strip(cl[i], ex, "target-entry") if i < len(cl) else None
            b("%s[%d] (%s)" % (lst, i, (rl[i] if i < len(rl) else cl[i]).get("target")), rv, cv)
    for k in B_WHOLE_ITEMS:
        b(k, rraw.get(k), craw.get(k))
    b("fresh_targets_k_and_x_R", fresh_k_xR(rraw, rcert), fresh_k_xR(craw, ccert))
    b("metrics (minus X2)", strip({"metrics": rraw.get("metrics")}, ex, "raw-result"), strip({"metrics": craw.get("metrics")}, ex, "raw-result"))
    b("group.order_pari_ellcard", (rraw.get("group") or {}).get("order_pari_ellcard"), (craw.get("group") or {}).get("order_pari_ellcard"))
    # SE-4 (e): outside the compared sets, listed with sha256; solver-events.json quoted in full; its conditions
    se, se_fails, se_txt = solver_events_check(candidate)
    fails += se_fails
    rep["solver_events"] = se
    rep["solver_events_json_verbatim"] = se_txt
    rep["renamed_attempt_files"] = [{"file": os.path.relpath(x, candidate), "sha256": R.sha256_file(x)}
                                    for x in sorted(glob.glob(os.path.join(candidate, "solver", "*.ssf-attempt*")))]
    rep["reference_integrity"] = {"files_verified": len(ref.integrity), "all_bound_and_matching": ref.ok(),
                                  "failures": [x for x in ref.integrity if not (x["bound"] and x["matches_receipt"])]}
    if not ref.ok():
        fails.insert(0, "FATAL: reference bytes do not match the reference receipt")
    rep["failures"] = fails
    rep["verdict"] = "PASS" if not fails else "FAIL"
    return rep


def render(rep):
    L = ["REG-1 comparator (implementation-v2-r3/r3_reg1.py; (d) branch %s)" % rep["d_branch"],
         "reference: %s" % rep["reference"], "candidate: %s" % rep["candidate"],
         "reference receipt: %s" % rep["reference_receipt"],
         "exclusion list: %s sha256 %s" % (rep["exclusion_list"], rep["exclusion_list_sha256"]),
         "reference integrity: %d files verified against the receipt; all bound and matching: %s" % (
             rep["reference_integrity"]["files_verified"], rep["reference_integrity"]["all_bound_and_matching"])]
    for f in rep["reference_integrity"]["failures"]:
        L.append("  INTEGRITY FAILURE %s bound=%s matches=%s" % (f["path"], f["bound"], f["matches_receipt"]))
    for item, title in (("a", "(a) retained solver inputs solver/*.ms"), ("b", "(b) raw-result.json"),
                        ("c", "(c) certificates/*.json"), ("d", "(d) d-parsed solver outputs solver/*.ms.out (recorded attempts)")):
        L.append(title + ":")
        for e in rep[item]:
            if "file_set" in e:
                L.append("  file set DIFFERS: only reference %s; only candidate %s" % (e["only_reference"], e["only_candidate"]))
            elif item == "b":
                L.append("  %-58s %s" % (e["item"], "equal" if e["equal"] else "DIFFERS"))
            elif item == "d":
                k = e["candidate_key"]
                L.append("  %-58s %s  [kind %s hdeg %s edeg %s sqfree %s nsols %s D %s]" % (
                    e["file"], "parsed-equal" if e["parsed_equal"] else "DIFFERS in %s" % e["differing_fields"],
                    k["parse_kind"], k["header_degree"], k["elim_degree"], k["elim_squarefree"],
                    k["rational_solution_set"]["n"], k["D"]))
            else:
                v = e.get("byte_identical", e.get("equal_after_exclusions"))
                L.append("  %-58s %s" % (e["file"], ("byte-identical" if item == "a" else "equal after exclusions") if v else "DIFFERS"))
    se = rep["solver_events"]
    L.append("solver-events.json (outside the compared sets; SE-4 (e); VA-6 (b)): present %s parses %s consistency_violation %s sha256 %s" % (
        se.get("present"), se.get("parses"), se.get("consistency_violation_recorded"), se.get("sha256")))
    L.append("renamed attempt files (outside the compared sets): %d" % len(rep["renamed_attempt_files"]))
    for x in rep["renamed_attempt_files"]:
        L.append("  %s sha256 %s" % (x["file"], x["sha256"]))
    L.append("solver-events.json verbatim:")
    L.extend("  | " + ln for ln in (rep["solver_events_json_verbatim"] or "<absent>").splitlines())
    L.append("failures: %d" % len(rep["failures"]))
    for f in rep["failures"]:
        L.append("  - " + f)
    L.append("REG-1 VERDICT: %s" % rep["verdict"])
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--reference", default=os.path.join(R.RUNS_DIR, R.REG1_REFERENCE_RUN))
    ap.add_argument("--receipt", default=None)
    ap.add_argument("--exclusions", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    rep = compare(os.path.abspath(a.reference), os.path.abspath(a.candidate), a.receipt, a.exclusions)
    print(render(rep))
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rep, fh, indent=1)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
