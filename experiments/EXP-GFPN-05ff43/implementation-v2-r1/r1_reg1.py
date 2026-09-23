#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-r1 -- the REG-1 COMPARATOR (addendum PS-4 regression_REG-1; RC-6; RC-7).

usage: python3 -B r1_reg1.py --candidate RUN_DIR [--reference RUN_DIR] [--receipt PATH] [--json OUT]

G1 (the r1 image of RUN-GFPN-ac4487) must reproduce RUN-GFPN-ac4487 on its deterministic content.
Before comparing, EVERY reference file read is verified against the TASK-20260923-0fa03f post-run receipt
path_sha256; a mismatch, or a reference file the receipt does not bind, is FATAL (verdict FAIL).
Compared:
  (a) solver/*.ms: same file set, byte-identical;
  (b) raw-result.json: run_status / failure_class / gate_pass; every entry of targets, planted_targets and
      replaced_fresh_targets (whole, minus the declared exclusions), and the D table derived from them;
      structure_checks; fixture_F1; fixture_F2a; fixture_F2b; fixture_F3; group (order_pari_ellcard,
      N_times_G_is_O); rescaling (beta, lam, b_is_square_in_Fq, ...); curve_checks; every fresh target's k
      (from its certificates) and x_R; the certificate block (kind, verified, count); metrics (minus X2);
  (c) certificates/*.json: same file set, equal as JSON after removing only the declared exclusions;
  (d) solver/*.ms.out: byte-identical (no exclusion is declared for msolve output).
The exclusion list is reg1-exclusion-list.json (sha256 printed); it may never exclude k, x_R, relation,
beta, lam, u_values, relation_mod_T, D, solutions, verified or lifted_points (checked here).
The complete output is deterministic text meant to be quoted verbatim (RC-7). This module imports no v2 or
v2-a1 module.
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
import r1_common as R                                    # noqa: E402

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

    def read(self, rel):
        p = os.path.join(self.rd, rel)
        b = open(p, "rb").read()
        if self.bound is not None:
            key = os.path.relpath(p, R.REPO)
            want = self.bound.get(key)
            got = R.sha256_bytes(b)
            self.integrity.append({"path": key, "bound": want is not None, "matches_receipt": want == got})
        return b

    def ok(self):
        return all(x["bound"] and x["matches_receipt"] for x in self.integrity)


def compare(reference, candidate, receipt=None, exclusion_path=None):
    ex, ex_sha = load_exclusions(exclusion_path)
    receipt = receipt or R.RECEIPT_V2_PHASE_B
    bound = R.receipt_paths(R.load_json(receipt))
    ref, cand = Reader(reference, bound), Reader(candidate)
    rep = {"reg1": "REG-1", "reference": os.path.relpath(reference, R.REPO), "candidate": os.path.relpath(candidate, R.REPO),
           "reference_receipt": os.path.relpath(receipt, R.REPO), "exclusion_list": os.path.relpath(exclusion_path or R.REG1_EXCLUSION_LIST, R.REPO),
           "exclusion_list_sha256": ex_sha, "a": [], "b": [], "c": [], "d": []}
    fails = []
    # (a) and (d)
    for item, pat in (("a", "*.ms"), ("d", "*.ms.out")):
        rs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(reference, "solver", pat)))
        cs = sorted(os.path.basename(x) for x in glob.glob(os.path.join(candidate, "solver", pat)))
        if rs != cs:
            rep[item].append({"file_set": "differs", "only_reference": sorted(set(rs) - set(cs)), "only_candidate": sorted(set(cs) - set(rs))})
            fails.append("(%s) file set differs" % item)
        for f in sorted(set(rs) & set(cs)):
            eq = ref.read(os.path.join("solver", f)) == cand.read(os.path.join("solver", f))
            rep[item].append({"file": "solver/" + f, "byte_identical": eq})
            if not eq:
                fails.append("(%s) solver/%s differs" % (item, f))
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
    rep["reference_integrity"] = {"files_verified": len(ref.integrity), "all_bound_and_matching": ref.ok(),
                                  "failures": [x for x in ref.integrity if not (x["bound"] and x["matches_receipt"])]}
    if not ref.ok():
        fails.insert(0, "FATAL: reference bytes do not match the TASK-20260923-0fa03f post-run receipt")
    rep["failures"] = fails
    rep["verdict"] = "PASS" if not fails else "FAIL"
    return rep


def render(rep):
    L = ["REG-1 comparator (implementation-v2-r1/r1_reg1.py)",
         "reference: %s" % rep["reference"], "candidate: %s" % rep["candidate"],
         "reference receipt: %s" % rep["reference_receipt"],
         "exclusion list: %s sha256 %s" % (rep["exclusion_list"], rep["exclusion_list_sha256"]),
         "reference integrity: %d files verified against the receipt; all bound and matching: %s" % (
             rep["reference_integrity"]["files_verified"], rep["reference_integrity"]["all_bound_and_matching"])]
    for f in rep["reference_integrity"]["failures"]:
        L.append("  INTEGRITY FAILURE %s bound=%s matches=%s" % (f["path"], f["bound"], f["matches_receipt"]))
    for item, title in (("a", "(a) retained solver inputs solver/*.ms"), ("b", "(b) raw-result.json"),
                        ("c", "(c) certificates/*.json"), ("d", "(d) solver outputs solver/*.ms.out")):
        L.append(title + ":")
        for e in rep[item]:
            if "file_set" in e:
                L.append("  file set DIFFERS: only reference %s; only candidate %s" % (e["only_reference"], e["only_candidate"]))
            elif item == "b":
                L.append("  %-58s %s" % (e["item"], "equal" if e["equal"] else "DIFFERS"))
            else:
                v = e.get("byte_identical", e.get("equal_after_exclusions"))
                L.append("  %-58s %s" % (e["file"], ("byte-identical" if item in "ad" else "equal after exclusions") if v else "DIFFERS"))
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
