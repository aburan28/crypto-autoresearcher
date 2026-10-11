#!/usr/bin/env python3
"""TASK-20260924-b2c7f1 CP-1/CP-2/CP-3 aggregation: builds comparison.json.

Reads ARCHIVED bytes only (verified against the TASK-20260924-a4f217,
TASK-20260924-60b4ea and TASK-20260924-e27f93 receipts at the start):
  - blind-inputs.json, blind-inputs-key.json, null-systems.json
  - reviews/TASK-20260924-1f6a3c/rederivation.json (J5)
  - reviews/TASK-20260924-7e2d94/verification.json (J1)
  - RUN-CERTBIN-c417e0: instance-sets.json, closures.jsonl.gz,
    certificates.jsonl.gz, certificate-verification.json, cell-summary.json,
    decision-rules.json
  - checks/wcert-check-output.json (this task's own CP-3 checker output)
Imports from the archived impl/ only macaulay.EQ_MONS / mu_order (the E_hex
decoding convention named in PD-R2). Bytecode writing disabled.

Nothing here re-runs a closure. The CP-4 third check is a separate script.
"""
import gzip
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from math import comb

sys.dont_write_bytecode = True
REPO = sys.argv[1]
OUT = sys.argv[2]
RV = "coordination/review/certbin-20260924-3d7e1a"
RUN = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
J5 = f"{RV}/reviews/TASK-20260924-1f6a3c"
J1 = f"{RV}/reviews/TASK-20260924-7e2d94"
ME = f"{RV}/reviews/TASK-20260924-b2c7f1"
sys.path.insert(0, os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl"))
import macaulay  # noqa: E402  (EQ_MONS convention only)


def P(p):
    return os.path.join(REPO, p)


def sha(p):
    return hashlib.sha256(open(P(p), "rb").read()).hexdigest()


def head_sha(p):
    b = subprocess.run(["git", "-C", REPO, "show", "HEAD:" + p], capture_output=True).stdout
    return hashlib.sha256(b).hexdigest()


out = {"schema": "certbin.b2c7f1.comparison.v1", "task_id": "TASK-20260924-b2c7f1",
       "review_plan_id": "REVIEW-CERTBIN-20260924-3d7e1a", "joint": "J6",
       "run_id": "RUN-CERTBIN-c417e0",
       "repository_head": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()}

# ------------------------------------------------------------------ CP-1
cp1 = {}
r60 = json.load(open(P(f"{RV}/archives/TASK-20260924-60b4ea/snapshot-receipt.json")))
bad = [p for p, h in r60["path_sha256"].items() if not (sha(p) == h == head_sha(p))]
ondisk = []
for d in (J5, J1):
    for root, _, files in os.walk(P(d)):
        for f in files:
            q = os.path.relpath(os.path.join(root, f), REPO)
            if "__pycache__" not in q:
                ondisk.append(q)
cp1["1_reviewer_dirs_vs_60b4ea_path_sha256"] = {
    "paths_in_receipt": len(r60["path_sha256"]), "mismatch_disk_or_HEAD": bad,
    "files_on_disk_not_in_receipt": sorted(set(ondisk) - set(r60["path_sha256"])),
    "receipt_paths_missing_on_disk": sorted(set(r60["path_sha256"]) - set(ondisk)),
    "pass": not bad and set(ondisk) == set(r60["path_sha256"])}
seal5 = open(P(f"{J5}/seal.txt")).read()
seal1 = open(P(f"{J1}/seal.txt")).read()
s5 = {"rederivation.json": sha(f"{J5}/rederivation.json"), "wcerts.jsonl.gz": sha(f"{J5}/wcerts.jsonl.gz")}
s1 = {"verification.json": sha(f"{J1}/verification.json")}
cp1["2_seals"] = {
    "TASK-20260924-1f6a3c": {"computed": s5, "pass": all(h in seal5 for h in s5.values())},
    "TASK-20260924-7e2d94": {"computed": s1, "pass": all(h in seal1 for h in s1.values())}}
ra4 = json.load(open(P(f"{RV}/archives/TASK-20260924-a4f217/snapshot-receipt.json")))
bip = f"{RV}/blind/blind-inputs.json"
cp1["3_blind_inputs_vs_a4f217"] = {"sha256": sha(bip), "receipt": ra4["path_sha256"][bip],
                                   "HEAD": head_sha(bip), "pass": sha(bip) == ra4["path_sha256"][bip] == head_sha(bip)}
a4bad = [p for p, h in ra4["path_sha256"].items() if not (sha(p) == h == head_sha(p))]
cp1["3b_all_a4f217_paths"] = {"n": len(ra4["path_sha256"]), "mismatch": a4bad}
cp1["4_60b4ea_no_blocking_defect"] = {"sc1_defects": r60["sc1_defects"], "comparator_blocked": r60["comparator_blocked"],
                                      "pass": (not r60["sc1_defects"]) and r60["comparator_blocked"] is False}
re27 = json.load(open(P("coordination/design/certbin-followups-20260924/archives/TASK-20260924-e27f93/snapshot-receipt.json")))
e27bad = [p for p, h in re27["path_sha256"].items() if not (sha(p) == h == head_sha(p))]
cp1["5_run_package_vs_e27f93"] = {"n": len(re27["path_sha256"]), "mismatch": e27bad, "pass": not e27bad}
cp1["pass"] = all(v.get("pass", True) for v in cp1.values() if isinstance(v, dict)) and not a4bad
out["cp1"] = cp1

# ------------------------------------------------------------------ load
bi = json.load(open(P(bip)))
key = json.load(open(P(f"{RV}/blind-inputs-key.json")))
nulls = json.load(open(P(f"{RV}/systems/null-systems.json")))
red = json.load(open(P(f"{J5}/rederivation.json")))
ver = json.load(open(P(f"{J1}/verification.json")))
iset = json.load(open(P(f"{RUN}/instance-sets.json")))
clos = [json.loads(l) for l in gzip.open(P(f"{RUN}/closures.jsonl.gz"), "rt")]
certs = [json.loads(l) for l in gzip.open(P(f"{RUN}/certificates.jsonl.gz"), "rt")]
cver = json.load(open(P(f"{RUN}/certificate-verification.json")))
dr = json.load(open(P(f"{RUN}/decision-rules.json")))
cs = json.load(open(P(f"{RUN}/cell-summary.json")))
wchk = json.load(open(P(f"{ME}/checks/wcert-check-output.json")))
out["inputs_sha256"] = {p: sha(p) for p in [bip, f"{RV}/blind-inputs-key.json", f"{RV}/systems/null-systems.json",
                                            f"{J5}/rederivation.json", f"{J5}/wcerts.jsonl.gz", f"{J1}/verification.json",
                                            f"{RUN}/instance-sets.json", f"{RUN}/closures.jsonl.gz",
                                            f"{RUN}/certificates.jsonl.gz", f"{RUN}/certificate-verification.json",
                                            f"{RUN}/cell-summary.json", f"{RUN}/decision-rules.json",
                                            f"{ME}/checks/wcert-check-output.json"]}

inst_by_key = {}
for sname, lst in iset["sets"].items():
    for x in lst:
        inst_by_key[x["key"]] = dict(x, set=sname)
clos_by = {(r["key"], r["closure"]): r for r in clos}
binp = {x["label"]: x for x in bi["instances"]}

# ------------------------------------------------------------------ key mapping
km = {}
exp_pool = []
for sname, nmax in (("U62", None), ("S62", 10), ("C20", 5), ("N-AFF62", 10), ("N-F262", 10)):
    lst = sorted(iset["sets"][sname], key=lambda x: x["idx"])
    lst = lst if nmax is None else lst[:nmax]
    exp_pool += [x["key"] for x in lst]
pool = [key[l]["key"] for l in sorted(key)]
km["pool_equals_plan_rule"] = sorted(exp_pool) == sorted(pool) and len(set(pool)) == 97
order = sorted(pool, key=lambda k: hashlib.sha256(("REVIEW-CERTBIN-20260924-3d7e1a|" + k).encode()).hexdigest())
km["labels_in_sha256_order"] = order == pool
km["key_fields_consistent"] = all(v["key"] == f'{v["set"]}:{v["family"]}:{v["idx"]}' for v in key.values())
EQM = macaulay.EQ_MONS


def decode_hex(hx):
    eqs = []
    for h in hx:
        v = int(h, 16)
        eqs.append(sorted([list(EQM[j]) for j in range(len(EQM)) if (v >> j) & 1]))
    return eqs


bind_bad = []
kinds = {}
for lab in sorted(key):
    k = key[lab]["key"]
    inst = inst_by_key[k]
    b = binp[lab]
    kinds[lab] = b["kind"]
    if b["kind"] == "curve":
        if not (inst["family"] == "F-S3" and b["x_R"] == inst["archived"]["x_R"]):
            bind_bad.append([lab, k, "x_R"])
    else:
        if inst["family"] == "F-S3":
            bind_bad.append([lab, k, "explicit kind on F-S3"])
        mine = [sorted(eq) for eq in b["equations"]]
        if mine != decode_hex(inst["E_hex"]):
            bind_bad.append([lab, k, "equations != decode(E_hex)"])
        ns = nulls.get(k)
        if ns is None or [sorted(eq) for eq in ns["equations"]] != mine:
            bind_bad.append([lab, k, "equations != null-systems.json"])
    # E_hex hash self-consistency
    if hashlib.sha256(json.dumps(inst["E_hex"]).encode()).hexdigest() != inst["E_sha256"]:
        bind_bad.append([lab, k, "E_sha256"])
km["content_binding_failures"] = bind_bad
km["kind_counts"] = {"curve": sum(1 for v in kinds.values() if v == "curve"),
                     "explicit": sum(1 for v in kinds.values() if v == "explicit")}
km["note"] = ("curve kind: blind x_R equals instance-sets.json archived.x_R of the mapped key; explicit kind: "
              "blind equations equal the decoding of that key's E_hex with macaulay.EQ_MONS; E_sha256 recomputed.")
km["pass"] = km["pool_equals_plan_rule"] and km["labels_in_sha256_order"] and km["key_fields_consistent"] and not bind_bad
out["key_mapping"] = km

# ------------------------------------------------------------------ CP-2 per instance
ITEMS = ["s_route1", "s_route2", "arm", "degenerate", "rank_3", "rank_4", "one_in_R3", "one_in_R4",
         "W4_dims_per_iteration", "W4_fixpoint_index", "W4_first_one_iteration", "W4_final_dim",
         "W4_dim_cap_B_le_0", "W4_dim_cap_B_le_1", "W4_dim_cap_B_le_2", "W4_dim_cap_B_le_3", "W4_dim_cap_B_le_4",
         "one_in_W4", "W4_low_basis_size_per_iteration",
         "R4_fall_d0", "R4_fall_d1", "R4_fall_d2", "R4_fall_d3",
         "rank_5", "one_in_R5",
         "xrun_M3_rank_vs_closure_record", "xrun_M4_rank_vs_closure_record", "xrun_W4_dim0_vs_rank4"]
ITEM_SOURCE = {
    "s_route1": "instance-sets.json archived.s vs J5 Q1.s_route1_exhaustive",
    "s_route2": "instance-sets.json archived.s vs J5 Q1.s_route2_rootfinding (curve kind only)",
    "arm": "archived.stratum vs ('unsat' iff J5 s = 0, both routes)",
    "degenerate": "archived.degenerate vs J5 Q1.degenerate (curve kind only)",
    "rank_3": "archived.rank_3 vs J5 Q2.rank_3", "rank_4": "archived.rank_4 vs J5 Q2.rank_4",
    "one_in_R3": "archived.one_in_R_3 vs J5 Q2.one_in_R3", "one_in_R4": "archived.one_in_R_4 vs J5 Q2.one_in_R4",
    "W4_dims_per_iteration": "closures W_4 dims (dim W^(0)..dim W^(fix)) vs J5 Q3.dims[:fix+1]; J5 lists one more (dim W^(fix+1) = dim W^(fix)) per its AMB-1, checked separately",
    "W4_fixpoint_index": "closures W_4 iterations_to_fixpoint vs J5 Q3.fixpoint_index (both: first i with dim W^(i+1) = dim W^(i); producer closure.py _w_closure, J5 AMB-1)",
    "W4_first_one_iteration": "closures W_4 one_first_iteration vs J5 Q3.first_one_iteration (both count from W^(0))",
    "W4_final_dim": "closures W_4 final_dim vs J5 Q3.final_dim",
    "W4_dim_cap_B_le_0": "closures W_4 dims_by_deg[0] vs J5 Q3.dim_W4_cap_B_le_d[0]",
    "W4_dim_cap_B_le_1": "dims_by_deg[1]", "W4_dim_cap_B_le_2": "dims_by_deg[2]",
    "W4_dim_cap_B_le_3": "dims_by_deg[3]", "W4_dim_cap_B_le_4": "dims_by_deg[4]",
    "one_in_W4": "closures W_4 one vs J5 Q3.one_in_W4",
    "W4_low_basis_size_per_iteration": "DERIVED: cumulative sum of closures W_4 new_fallen_per_iteration (= dim W^(i) cap B_{<=3} under producer closure.py semantics) vs J5 Q3.multiplied_basis_sizes",
    "R4_fall_d0": "dim(R_4 cap B_{<=0}): run value only where W_4 fixpoint index is 0 (then W_4 = R_4 and dims_by_deg[0] is it); else re-deriver only",
    "R4_fall_d1": "as R4_fall_d0 with d = 1", "R4_fall_d2": "as R4_fall_d0 with d = 2",
    "R4_fall_d3": "DERIVED: closures W_4 new_fallen_per_iteration[0] (= number of W^(0) echelon rows with lead degree <= 3 = dim R_4 cap B_{<=3}) vs J5 Q2.dim_R4_cap_B_le_d[3]",
    "rank_5": "closures M_5 rank vs J5 Q5.rank_5 (BI-001..BI-008 only)",
    "one_in_R5": "closures M_5 one vs J5 Q5.one_in_R5 (BI-001..BI-008 only)",
    "xrun_M3_rank_vs_closure_record": "EXTRA: closures M_3 (rank, one) vs J5 (rank_3, one_in_R3)",
    "xrun_M4_rank_vs_closure_record": "EXTRA: closures M_4 (rank, one) vs J5 (rank_4, one_in_R4)",
    "xrun_W4_dim0_vs_rank4": "EXTRA: closures W_4 dims[0] vs J5 Q2.rank_4",
}


def cmp(run, re):
    return {"run": run, "rederiver": re, "status": "agree" if run == re else "DISAGREE"}


def only(re, why):
    return {"run": None, "rederiver": re, "status": "rederiver_only", "why": why}


def na(why):
    return {"status": "not_applicable", "why": why}


per = {}
for lab in sorted(key):
    k = key[lab]["key"]
    inst = inst_by_key[k]
    a = inst["archived"]
    R = red["instances"][lab]
    q1, q2, q3 = R["Q1"], R["Q2"], R["Q3"]
    w = clos_by[(k, "W_4")]
    it = {}
    it["s_route1"] = cmp(a["s"], q1.get("s_route1_exhaustive", q1.get("s")))
    it["s_route2"] = cmp(a["s"], q1["s_route2_rootfinding"]) if R["kind"] == "curve" else na("explicit kind: exhaustive route only (card BR-3)")
    s_re = q1.get("s_route1_exhaustive", q1.get("s"))
    it["arm"] = cmp(a["stratum"], "unsat" if s_re == 0 else "sat")
    it["degenerate"] = cmp(a["degenerate"], q1["degenerate"]) if R["kind"] == "curve" else na("explicit kind: no x_R given to the re-deriver (PD-R2)")
    it["rank_3"] = cmp(a["rank_3"], q2["rank_3"])
    it["rank_4"] = cmp(a["rank_4"], q2["rank_4"])
    it["one_in_R3"] = cmp(a["one_in_R_3"], q2["one_in_R3"])
    it["one_in_R4"] = cmp(a["one_in_R_4"], q2["one_in_R4"])
    fix = q3["fixpoint_index"]
    d = cmp(w["dims"], q3["dims"][:fix + 1])
    d["rederiver_extra_tail"] = q3["dims"][fix + 1:]
    d["rederiver_tail_is_repeat"] = (len(q3["dims"]) == fix + 2 and q3["dims"][-1] == q3["dims"][-2])
    if not d["rederiver_tail_is_repeat"]:
        d["status"] = "DISAGREE"
    it["W4_dims_per_iteration"] = d
    it["W4_fixpoint_index"] = cmp(w["iterations_to_fixpoint"], fix)
    it["W4_first_one_iteration"] = cmp(w["one_first_iteration"], q3["first_one_iteration"])
    it["W4_final_dim"] = cmp(w["final_dim"], q3["final_dim"])
    for dd in range(5):
        it[f"W4_dim_cap_B_le_{dd}"] = cmp(w["dims_by_deg"][dd], q3["dim_W4_cap_B_le_d"][dd])
    it["one_in_W4"] = cmp(w["one"], q3["one_in_W4"])
    cum, t = [], 0
    for x in w["new_fallen_per_iteration"]:
        t += x
        cum.append(t)
    it["W4_low_basis_size_per_iteration"] = cmp(cum, q3.get("multiplied_basis_sizes"))
    it["W4_low_basis_size_per_iteration"]["derived"] = True
    for dd in range(3):
        if w["iterations_to_fixpoint"] == 0:
            it[f"R4_fall_d{dd}"] = cmp(w["dims_by_deg"][dd], q2["dim_R4_cap_B_le_d"][dd])
            it[f"R4_fall_d{dd}"]["derived"] = "W_4 = R_4 (fixpoint index 0)"
        else:
            it[f"R4_fall_d{dd}"] = only(q2["dim_R4_cap_B_le_d"][dd], "run records no R_4 fall profile; W_4 != R_4 here")
    it["R4_fall_d3"] = cmp(w["new_fallen_per_iteration"][0], q2["dim_R4_cap_B_le_d"][3])
    it["R4_fall_d3"]["derived"] = True
    if "Q5" in R and R["Q5"]:
        m5 = clos_by.get((k, "M_5"))
        if m5 is None:
            it["rank_5"] = only(R["Q5"]["rank_5"], "M_5 not run on this set")
            it["one_in_R5"] = only(R["Q5"]["one_in_R5"], "M_5 not run on this set")
        else:
            it["rank_5"] = cmp(m5["rank"], R["Q5"]["rank_5"])
            it["one_in_R5"] = cmp(m5["one"], R["Q5"]["one_in_R5"])
    else:
        it["rank_5"] = na("Q5 optional; J5 computed it on BI-001..BI-008 only")
        it["one_in_R5"] = na("Q5 optional; J5 computed it on BI-001..BI-008 only")
    m3, m4 = clos_by[(k, "M_3")], clos_by[(k, "M_4")]
    it["xrun_M3_rank_vs_closure_record"] = cmp([m3["rank"], m3["one"]], [q2["rank_3"], q2["one_in_R3"]])
    it["xrun_M4_rank_vs_closure_record"] = cmp([m4["rank"], m4["one"]], [q2["rank_4"], q2["one_in_R4"]])
    it["xrun_W4_dim0_vs_rank4"] = cmp(w["dims"][0], q2["rank_4"])
    per[lab] = {"key": k, "set": inst["set"], "kind": R["kind"], "items": it,
                "j5_internal_checks_all_pass": all(
                    (v <= 2) if kk == "explicit_max_monomial_degree" else
                    (v is True or (isinstance(v, int) and not isinstance(v, bool) and v == 0))
                    for kk, v in R["checks"].items())}
out["per_instance"] = per

# per-item summary and floor/ceiling
summ = {}
for itn in ITEMS:
    c = {"agree": 0, "DISAGREE": 0, "rederiver_only": 0, "not_applicable": 0}
    dis = []
    per_set_vals = {}
    for lab, v in per.items():
        x = v["items"][itn]
        c[x["status"]] += 1
        if x["status"] == "DISAGREE":
            dis.append(lab)
        if x["status"] in ("agree", "DISAGREE", "rederiver_only"):
            val = x["rederiver"] if x["status"] == "rederiver_only" else x["run"]
            per_set_vals.setdefault(v["set"], set()).add(json.dumps(val))
    summ[itn] = {"source": ITEM_SOURCE[itn], "counts": c, "disagreeing_labels": dis,
                 "distinct_values_per_set": {s: sorted(vals)[:12] + (["..."] if len(vals) > 12 else [])
                                             for s, vals in sorted(per_set_vals.items())},
                 "n_distinct_values_per_set": {s: len(vals) for s, vals in sorted(per_set_vals.items())}}
out["per_item_summary"] = summ
tot = {"agree": 0, "DISAGREE": 0, "rederiver_only": 0, "not_applicable": 0}
for itn in ITEMS:
    for kk in tot:
        tot[kk] += summ[itn]["counts"][kk]
out["totals_instance_item_cells"] = tot
out["totals_note"] = ("Counted over 97 instances x %d items, including three EXTRA run-internal items (xrun_*). "
                      "'derived' items read a run field through the producer's documented semantics." % len(ITEMS))

# ------------------------------------------------------------------ J1 vs run
cv_by = {(c["key"], c["closure"]): c for c in cver["certificates"]}
j1_by = {}
for c in ver["certificates"]:
    j1_by.setdefault((c["key"], c["closure"]), []).append(c)
file_keys = [(c.get("key"), c.get("closure")) for c in certs]


def j1_verdict(c):
    for f in ("verified", "accepted", "verdict"):
        if f in c:
            return c[f]
    return None


j1rows = []
for i, c in enumerate(ver["certificates"]):
    kk = (c["key"], c["closure"])
    rv = cv_by.get(kk)
    jv = j1_verdict(c)
    j1rows.append({"line": c.get("line", i), "key": c["key"], "closure": c["closure"], "set": c.get("set"),
                   "J1": jv, "run": rv["verified"] if rv else None,
                   "J1_size": c.get("C_size"), "run_size": rv["size"] if rv else None,
                   "J1_max_deg_mu": c.get("max_deg_mu"), "run_max_deg_mu": rv["max_deg_mu"] if rv else None,
                   "agree": (rv is not None and jv == rv["verified"] and c.get("C_size") == rv["size"]
                             and c.get("max_deg_mu") == rv["max_deg_mu"])})
j1 = {"n_J1": len(ver["certificates"]), "n_run": len(cver["certificates"]), "n_file_lines": len(certs),
      "J1_keys_equal_run_keys": sorted(j1_by) == sorted(cv_by) and all(len(v) == 1 for v in j1_by.values()),
      "J1_keys_equal_certificate_file_keys": sorted(j1_by) == sorted(file_keys),
      "J1_input_certs_sha256_equals_run_verifier_certs_sha256":
          ver["inputs_sha256"].get(f"{RUN}/certificates.jsonl.gz") == cver["certs_sha256"] == sha(f"{RUN}/certificates.jsonl.gz"),
      "per_certificate_agree": sum(1 for r in j1rows if r["agree"]),
      "per_certificate_disagree": [r for r in j1rows if not r["agree"]],
      "J1_verified": sum(1 for r in j1rows if r["J1"] is True),
      "J1_rejected": sum(1 for r in j1rows if r["J1"] is False),
      "J1_other": sum(1 for r in j1rows if r["J1"] not in (True, False)),
      "per_certificate": j1rows}
# which J1 field holds the verdict
j1["J1_verdict_field_note"] = "J1 per-certificate verdict read from field 'verified' (first of verified/accepted/verdict present)."

# recount from J1 verdicts only
def vkeys(closure, sname):
    return sorted({c["key"] for c in ver["certificates"] if c["closure"] == closure and
                   inst_by_key.get(c["key"], {}).get("set") == sname and j1_verdict(c) is True})


a = len(vkeys("W_4", "U62"))
b = len(vkeys("M_5", "U62"))
r = len(set(vkeys("W_4", "U62")) | set(vkeys("M_5", "U62")) | set(vkeys("W_5", "U62")))
mr4 = {s: {cl: len(vkeys(cl, s)) for cl in ("W_4", "M_5", "W_5")} for s in ("N-AFF62", "N-F262")}
s62 = {cl: len(vkeys(cl, "S62")) for cl in ("W_4", "M_5", "W_5")}
# engine-reported refutations (for L1/L2: reported but not verified = UNCERTIFIED)
rep = {s: {cl: sorted(x["key"] for x in clos if x["set"] == s and x["closure"] == cl and x.get("one") is True)
           for cl in ("W_4", "M_5", "W_5")} for s in ("U62", "S62", "C20", "N-AFF62", "N-F262")}
rep_U = set(rep["U62"]["W_4"]) | set(rep["U62"]["M_5"]) | set(rep["U62"]["W_5"])
ver_U = set(vkeys("W_4", "U62")) | set(vkeys("M_5", "U62")) | set(vkeys("W_5", "U62"))
uncert = sorted(rep_U - ver_U)
two = {"W4+M5+": 0, "W4+M5-": 0, "W4-M5+": 0, "W4-M5-": 0}
for x in iset["sets"]["U62"]:
    kx = x["key"]
    w4 = kx in vkeys("W_4", "U62")
    m5 = kx in vkeys("M_5", "U62")
    two[("W4+" if w4 else "W4-") + ("M5+" if m5 else "M5-")] += 1


# exact Clopper-Pearson 95% by rational bisection (independent of analysis.py/stats_exact.py)
def tail_ge(x, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x, n + 1))


def tail_le(x, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1))


def cp95(x, n, bits=70):
    al = Fraction(1, 40)
    if x == 0:
        lo = Fraction(0)
    else:
        l, h = Fraction(0), Fraction(1)
        for _ in range(bits):
            m = (l + h) / 2
            (l, h) = (m, h) if tail_ge(x, n, m) < al else (l, m)
            l, h = Fraction(l).limit_denominator(1 << 90), Fraction(h).limit_denominator(1 << 90)
        lo = l
    if x == n:
        up = Fraction(1)
    else:
        l, h = Fraction(0), Fraction(1)
        for _ in range(bits):
            m = (l + h) / 2
            (l, h) = (m, h) if tail_le(x, n, m) > al else (l, m)
            l, h = Fraction(l).limit_denominator(1 << 90), Fraction(h).limit_denominator(1 << 90)
        up = h
    return lo, up


n = 62
dr1 = "ARTIFACT (predominant)" if a >= 56 else ("GENUINE D*_W > 4 (predominant)" if a <= 6 else "MIXED")
L1_den, L1_nr = n, n - r
L2_den = n - len(uncert)
L2_nr = L2_den - len(ver_U & {x["key"] for x in iset["sets"]["U62"]})


def lab_dr2(nr):
    return "CLEAN" if nr == 0 else ("NEAR-CLEAN" if nr <= 3 else "RESIDUE")


L1, L2 = lab_dr2(L1_nr), lab_dr2(L2_nr)
dr2 = L1 if L1 == L2 else "UNDETERMINED (budget or certification)"
dr3 = "M_5 SUFFICES" if b == 62 else str(b)
dr4 = {}
cpU = {cl: cp95(len(vkeys(cl, "U62")), n) for cl in ("W_4", "M_5")}
for cl in ("W_4", "M_5"):
    sep = {}
    for s in ("N-AFF62", "N-F262"):
        cpn = cp95(mr4[s][cl], n)
        sep[s] = {"U62_lower": float(cpU[cl][0]), "null_upper": float(cpn[1]), "U62_lower_exceeds": cpU[cl][0] > cpn[1]}
    dr4[cl] = {"separation": sep,
               "verdict": ("S_3-SPECIFIC at " + cl) if all(v["U62_lower_exceeds"] for v in sep.values()) else ("NOT DISTINGUISHED at " + cl)}
recorded = {"RC1-DR-1": dr["rules"]["RC1-DR-1"]["verdict"], "RC1-DR-2": dr["rules"]["RC1-DR-2"]["verdict"],
            "RC1-DR-2_L1": dr["rules"]["RC1-DR-2"]["L1"], "RC1-DR-2_L2": dr["rules"]["RC1-DR-2"]["L2"],
            "RC1-DR-3": dr["rules"]["RC1-DR-3"]["verdict"],
            "RC1-DR-4_W_4": dr["rules"]["RC1-DR-4"]["W_4"]["verdict"], "RC1-DR-4_M_5": dr["rules"]["RC1-DR-4"]["M_5"]["verdict"]}
reapplied = {"RC1-DR-1": dr1, "RC1-DR-2": dr2, "RC1-DR-2_L1": L1, "RC1-DR-2_L2": L2, "RC1-DR-3": dr3,
             "RC1-DR-4_W_4": dr4["W_4"]["verdict"], "RC1-DR-4_M_5": dr4["M_5"]["verdict"]}
cs_rec = {"a": cs["MR1_w4_refuted_U62"]["a"], "b": cs["MR2_m5_refuted_U62"]["b"], "r": cs["MR3_refuted_at_D_le_5_U62"]["r"],
          "MR4": {s: {cl: cs["MR4_null_refutation_rates"][s][cl]["verified_refuted"] for cl in ("W_4", "M_5")}
                  for s in ("N-AFF62", "N-F262")},
          "two_by_two_U62": dr["rules"]["RC1-DR-3"]["inputs"]["two_by_two_U62"]}
j1["recount_from_J1_verdicts_only"] = {
    "MR1_a": a, "MR2_b": b, "MR3_r": r, "MR4": mr4, "S62_refuted_verified": s62,
    "engine_reported_U62_refutations_not_J1_verified (UNCERTIFIED under L1/L2)": uncert,
    "two_by_two_U62": two,
    "CP95_exact_rational": {"U62_x62_n62_lower": str(float(cp95(62, 62)[0])),
                            "x0_n62_upper": str(float(cp95(0, 62)[1]))},
    "RC1_DR_L1": {"denominator": L1_den, "not_refuted": L1_nr}, "RC1_DR_L2": {"denominator": L2_den, "not_refuted": L2_nr},
    "reapplied_verdicts": reapplied, "recorded_verdicts": recorded, "cell_summary_counts": cs_rec,
    "counts_equal_recorded": (a == cs_rec["a"] and b == cs_rec["b"] and r == cs_rec["r"] and
                              all(mr4[s][cl] == cs_rec["MR4"][s][cl] for s in mr4 for cl in ("W_4", "M_5")) and
                              two == cs_rec["two_by_two_U62"]),
    "any_verdict_changes": reapplied != recorded,
    "note": ("MR4 W_5 is 0/0 (W_5 not run on null sets); RC1-DR-4 evaluates W_4 and M_5 only (spec). "
             "RC1-DR-5 is not a count rule; its C-CERT input agrees because J1 rejected none.")}
out["J1_vs_run"] = j1

# ------------------------------------------------------------------ CP-3 W-certification status per key
wc = {}
for lab in sorted(key):
    k = key[lab]["key"]
    w = clos_by[(k, "W_4")]
    st = wchk["per_label"][lab]["status"]
    re1 = red["instances"][lab]["Q3"]["one_in_W4"]
    if w["one"] is True:
        if st == "valid":
            ws = "W-certified"
        elif re1 is False:
            ws = "contradicted"
        else:
            ws = "engine-reported only"
    else:
        ws = "no W_4 refutation claimed by the run" + ("; J5 also finds none" if re1 is False else "; J5 FINDS ONE")
    wc[lab] = {"key": k, "set": key[lab]["set"], "run_one_in_W4": w["one"], "J5_one_in_W4": re1,
               "J5_certificate_status_by_b2c7f1_checker": st,
               "J5_first_one_iteration": red["instances"][lab]["Q3"]["first_one_iteration"],
               "J5_Q4_status": red["instances"][lab].get("Q4", {}).get("status") if red["instances"][lab].get("Q4") else None,
               "W_certification_status": ws}
from collections import Counter
out["W_certification"] = {
    "checker": "checks/wcert_check_b2c7f1.py (written before any read of reviews/TASK-20260924-1f6a3c/code/)",
    "per_label": wc,
    "counts_by_set": {s: dict(Counter(v["W_certification_status"] for v in wc.values() if v["set"] == s))
                      for s in ("U62", "S62", "C20", "N-AFF62", "N-F262")},
    "checker_status_counts": wchk["counts"],
    "run_claimed_W4_refutations_in_pool": sum(1 for v in wc.values() if v["run_one_in_W4"] is True),
    "run_claimed_W4_refutations_in_pool_W_certified": sum(1 for v in wc.values() if v["W_certification_status"] == "W-certified"),
    "out_of_pool_note": ("15 C20 run W_4 refutations are outside the pool; no J5 W-certificate exists for them. "
                         "Their flat run certificates have max deg mu = 2 per J1 (recorded below), i.e. consist of M_4 rows only; "
                         "a J1-verified flat certificate with max deg mu <= 2 is itself a degree-disciplined W_4 witness. "
                         "Not checked by this task's checker (out of pool)."),
    "out_of_pool_C20_J1_max_deg_mu": sorted({(c["key"], c["max_deg_mu"], j1_verdict(c)) for c in ver["certificates"]
                                             if c["closure"] == "W_4" and c["key"].startswith("C20:")
                                             and c["key"] not in {key[l]["key"] for l in key}}),
}

# ------------------------------------------------------------------ CP-3 f_k binding (curve kind)
import gf2n  # noqa: E402  (archived TableField, the construction CP-3 names)
F = gf2n.TableField()
fk_bad = []
for lab in sorted(key):
    if binp[lab]["kind"] != "curve":
        continue
    k = key[lab]["key"]
    E = macaulay.descended_E(F, bi["curve"]["B"], binp[lab]["x_R"])
    mine = [sorted([list(EQM[j]) for j in range(len(EQM)) if E[kk, j]]) for kk in range(17)]
    if mine != decode_hex(inst_by_key[k]["E_hex"]):
        fk_bad.append(lab)
out["W_certification"]["fk_construction_binding"] = {
    "what": ("for every curve-kind pool instance, macaulay.descended_E(TableField(), B, x_R) (the f_k the CP-3 checker "
             "uses) equals the decoding of the run's instance-sets.json E_hex (the system the run's closures used). "
             "J1 post-seal PS-2 found its independently built f_k equal to that E_hex on 144/144 curve instances, so "
             "the checker's f_k is also J1's."),
    "n_checked": sum(1 for l in key if binp[l]["kind"] == "curve"), "mismatch": fk_bad, "pass": not fk_bad}

# ------------------------------------------------------------------ EXTRA: three-way s (archived, J5, J1)
j1s = {x["key"]: x for x in ver["vc5_sanity"]["per_instance"]}
s3 = []
for lab in sorted(key):
    k = key[lab]["key"]
    x = j1s.get(k)
    arch = inst_by_key[k]["archived"]["s"]
    q1 = red["instances"][lab]["Q1"]
    s3.append({"label": lab, "key": k, "archived": arch, "J5_route1": q1.get("s_route1_exhaustive"),
               "J5_route2": q1.get("s_route2_rootfinding"),
               "J1_monomial": x.get("s_monomial") if x else None, "J1_direct_S3": x.get("s_direct_S3") if x else None})
out["extra_three_way_s"] = {
    "rows": s3,
    "J1_covers": sum(1 for r in s3 if r["J1_monomial"] is not None),
    "all_present_values_equal": all(len({v for kk, v in r.items() if kk not in ("label", "key") and v is not None}) == 1 for r in s3)}

# ------------------------------------------------------------------ gaps (completion gate)
out["gaps"] = [
    {"item": "R4_fall_d0..d2 (dim R_4 cap B_{<=d}, d = 0..2)", "instances": 77,
     "reason": ("the run records no R_4 fall profile; it records dims_by_deg of W_4 only. On the 20 null-set pool instances "
                "the W_4 fixpoint index is 0, so W_4 = R_4 and the run value exists; on the 77 others (U62, C20, S62) "
                "the value is re-deriver only. d = 3 is compared on all 97 through new_fallen_per_iteration[0].")},
    {"item": "W_4 dims: dim W^(fix+1)", "instances": 97,
     "reason": ("J5 lists dim W^(fix+1) (= dim W^(fix)) per its AMB-1; the run's dims list stops at W^(fix) and records the "
                "stopping step only as iterations_to_fixpoint (closure.py _w_closure breaks before appending). Encoding "
                "difference; J5's tail is re-deriver only and equals its last run-comparable entry on all 97.")},
    {"item": "Q5 rank_5 and 1 in R_5", "instances": 89,
     "reason": "optional quantity; J5 computed it on BI-001..BI-008 only (review plan Q5; J5 AMB-11)."},
    {"item": "s_route2 and degenerate", "instances": 20,
     "reason": "explicit-kind inputs (null sets): no x_R given to J5 (PD-R2); exhaustive route only (card BR-3)."},
    {"item": "M_5 dims_by_deg", "instances": 8,
     "reason": "recorded by the run; not a J5 quantity (Q5 asks rank_5 and 1 in R_5 only). Not compared."},
]

# ------------------------------------------------------------------ ambiguities vs run resolution
out["ambiguities_vs_run"] = [
    {"id": "J5 AMB-1", "topic": "W_4 dims list end; fixpoint index",
     "run": "dims ends at W^(fix); iterations_to_fixpoint = first i with dim W^(i+1) = dim W^(i) (impl/closure.py _w_closure; impl/README.md 'W_D, exactly')",
     "same_quantity": True, "effect": "encoding only; reconciled by comparing run dims with J5 dims[:fix+1]"},
    {"id": "J5 AMB-2", "topic": "RREF vs echelon basis of W^(i) cap B_{<=3}",
     "run": "echelon (non-reduced) rows of the column pass with low-degree lead (impl/README.md; implementation.md deviation 1; closure.py echelon)",
     "same_quantity": True, "effect": "both sides depart from the word 'RREF' in the same way; same span, so same W^(i+1). Not read differently."},
    {"id": "J5 AMB-3", "topic": "basis snapshot per iteration",
     "run": "basis = echelon rows of W^(i) at loop start; products stacked then eliminated (closure.py)", "same_quantity": True,
     "effect": "same iterates"},
    {"id": "J5 AMB-4", "topic": "explicit-kind encoding",
     "run": "run reads E_hex (instances.E_from_hex, EQ_MONS); the explicit encoding is the opening archive's decoding (PD-R2)",
     "same_quantity": True, "effect": "checked here: blind equations == decode(E_hex) == null-systems.json on all 20 explicit pool instances"},
    {"id": "J5 AMB-5", "topic": "first-one iteration counts from W^(0)",
     "run": "one_first_iteration = 0 if 1 in W^(0) (closure.py)", "same_quantity": True, "effect": "none"},
    {"id": "J5 AMB-6", "topic": "'1 in R_D' as row-space membership",
     "run": "constant (last) column is a pivot column of the column pass (elim.py for C-BASE; closure.py macaulay_closure)",
     "same_quantity": True, "effect": "equivalent; agree on 97 x {R_3, R_4} and 8 x R_5"},
    {"id": "J5 AMB-7", "topic": "'earlier id' in W-certificates", "run": "not applicable (W-certificates are a review artifact)",
     "same_quantity": None, "effect": "the b2c7f1 checker enforces both readings (list position and p < id)"},
    {"id": "J5 AMB-8", "topic": "degree of the zero polynomial", "run": "not applicable",
     "same_quantity": None, "effect": "the b2c7f1 checker uses -1; bounds unaffected"},
    {"id": "J5 AMB-9", "topic": "route-2 counting of s",
     "run": "oracle A returns the set of v = x_1 | x_2 << 9 over V x V (impl/oracles_rc1.py); archived s from Stage 1",
     "same_quantity": True, "effect": "none; agree on 77"},
    {"id": "J5 AMB-10", "topic": "A does not enter S_3",
     "run": "macaulay.s3_multilinear uses B only", "same_quantity": True, "effect": "none"},
    {"id": "J5 AMB-11", "topic": "Q5 label range", "run": "not applicable (M_5 ran on every U62, S62 and null instance)",
     "same_quantity": None, "effect": "Q5 compared on BI-001..BI-008 (7 U62, 1 N-F262)"},
    {"id": "J1 AMB-1", "topic": "deg mu = number of distinct indices",
     "run": "cert_to_json emits the ascending index list of a bit mask (distinct by construction)", "same_quantity": True, "effect": "none"},
    {"id": "J1 AMB-2", "topic": "C as a literal sum; duplicates",
     "run": "closure._extract keeps pairs of odd parity only (no duplicates)", "same_quantity": True, "effect": "J1 found 0 duplicates"},
    {"id": "J1 AMB-3", "topic": "key-to-instance mapping", "run": "key = set:family:idx (instances.select_sets)",
     "same_quantity": True, "effect": "J1 keys == run keys == certificate file keys (268)"},
    {"id": "J1 AMB-4", "topic": "variable and field encoding", "run": "identical (macaulay.py docstring)", "same_quantity": True, "effect": "none"},
    {"id": "J1 AMB-5", "topic": "null systems taken from null-systems.json",
     "run": "run uses E_hex directly", "same_quantity": True,
     "effect": "J1 PS-3: null E_hex decoding == null-systems.json 124/124; checked here on the 20 pool nulls"},
    {"id": "J1 AMB-6, AMB-7", "topic": "negative-control construction", "run": "run's C-VERIFIER controls: pair removed / k changed on 20 W_4|U62 certificates (implementation.md deviation 6)",
     "same_quantity": None, "effect": "J1's controls cover every (closure, set) kind; not a compared quantity"},
    {"id": "J1 AMB-8", "topic": "max deg mu vs the W_4 label", "run": "run records max_deg_mu per certificate",
     "same_quantity": True, "effect": "J1 and run max_deg_mu agree on 268/268 (W_4|U62: 3; W_4|C20: 2; M_5: 3)"},
    {"id": "J1 AMB-9", "topic": "s by evaluation", "run": "archived s (Stage 1), re-checked by C-ORACLE", "same_quantity": True,
     "effect": "three-way s agreement recorded in extra_three_way_s"},
    {"id": "J1 AMB-10", "topic": "extra transplant control onto S62", "run": "not applicable", "same_quantity": None, "effect": "none"},
    {"id": "J1 AMB-11 (post-seal)", "topic": "E_hex bit layout", "run": "instances.E_from_hex: bit j (LSB first) of row k = column j of EQ_MONS",
     "same_quantity": True, "effect": "J1's empirically identified layout equals the run's function; also used here"},
]

# ------------------------------------------------------------------ floor / ceiling
out["floor_ceiling"] = {
    "rule": ("An item is weak evidence about the implementation when it takes one value on every compared instance of a set "
             "and that value is a structural extreme or is fixed by the set's definition: s = 0 and arm 'unsat' on the unsat "
             "sets (floor; set definition); one_in_R3 / one_in_R4 (fixed by the set rules); W_4 on U62 and C20 at the ceiling "
             "B_{<=4} (final_dim 4048, dims_by_deg [1, 19, 172, 988, 4048], dims ending 4048); W_4 on the nulls at the "
             "floor W_4 = R_4 (fixpoint index 0); 1 in R_5 true on all 8."),
    "weak_items_by_set": {
        "U62": ["s_route1", "s_route2", "arm", "degenerate", "one_in_R3", "one_in_R4", "W4_fixpoint_index (1)",
                "W4_first_one_iteration (1)", "W4_final_dim (4048, ceiling)", "W4_dim_cap_B_le_0..4 (ceiling)", "one_in_W4 (true)",
                "W4_dims_per_iteration last entry (4048, ceiling)", "one_in_R5 (true)"],
        "C20": ["s", "arm", "degenerate", "one_in_R3", "one_in_R4", "W4 final/dims_by_deg (ceiling)", "first_one_iteration (0)", "one_in_W4"],
        "N-AFF62/N-F262": ["s", "arm", "one_in_R3", "one_in_R4", "rank_3 (323)", "rank_4 (2771)", "W4 fixpoint index 0 (floor W_4 = R_4)",
                           "W4 final_dim/dims_by_deg (= R_4)", "R4 fall profile (0, 0, 17, 323)", "one_in_W4 (false)"],
        "S62": ["arm", "degenerate", "one_in_R3", "one_in_R4", "one_in_W4 (false)", "W4_dim_cap_B_le_0 (0)", "W4_fixpoint_index (1)"]},
    "informative_items": [
        "rank_3 on U62 (320 or 321) and rank_4 on U62, S62, C20 (9, 4 and 4 distinct values)",
        "W4 dims[0] and the R_4 fall profile d = 1..3 on U62, S62, C20 (vary per instance)",
        "the W^(i) cap B_{<=3} basis sizes per iteration (vary on U62, S62, C20)",
        "s on S62 (2 or 4, both routes) and the S62 W_4 final dimension and dims_by_deg (4044/4046; 15/17, 168/170, 984/986): codim(W_4) = s on all 10 pool S62 instances, and dim(W_4 cap B_{<=1}) = 19 - s",
        "rank_5 on U62 (10614) versus N-F262 (12364), BI-001..BI-008 only",
        "the stopping step on S62: the literal rule (J5 multiplies all 976..986 low basis rows at iteration 1) and the run's semi-naive rule (only the new ones) both find W^(2) = W^(1); this is the only place in the pool where the two rules could differ",
    ],
    "semi_naive_exercise_note": ("Every pool instance reaches its fixpoint at index <= 1. The semi-naive and literal rules are identical at "
                                 "iteration 1 by construction, so the per-iteration comparison exercises the semi-naive exactness argument "
                                 "only at the stopping step, and there non-vacuously only on the 10 S62 instances (U62/C20 are already at "
                                 "B_{<=4}; nulls stop at iteration 0)."),
}

json.dump(out, open(OUT, "w"), indent=1, sort_keys=False, default=str)
print("fk binding", out["W_certification"]["fk_construction_binding"]["pass"], "three-way s",
      out["extra_three_way_s"]["all_present_values_equal"], out["extra_three_way_s"]["J1_covers"])
print("cp1 pass", cp1["pass"], "keymap pass", km["pass"])
print("totals", tot)
for itn in ITEMS:
    print(f"{itn:36s}", summ[itn]["counts"], summ[itn]["disagreeing_labels"][:10])
print("J1 agree", j1["per_certificate_agree"], "of", j1["n_J1"], "keys equal", j1["J1_keys_equal_run_keys"],
      j1["J1_keys_equal_certificate_file_keys"], j1["J1_input_certs_sha256_equals_run_verifier_certs_sha256"])
print("recount", json.dumps({k: v for k, v in j1["recount_from_J1_verdicts_only"].items() if k != "note"}, default=str)[:1500])
print("wcert", json.dumps(out["W_certification"]["counts_by_set"]))
