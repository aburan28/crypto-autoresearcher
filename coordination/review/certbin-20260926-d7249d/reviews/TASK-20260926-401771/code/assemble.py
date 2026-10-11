"""Assemble verification.json (schema certbin.n19.independent_verification.v1)
from the work/ outputs. Usage: assemble.py <outdir> <scratch_inputs_dir> <libpath>"""
import collections
import glob
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

import numpy as np

OUT, INP, LIB = sys.argv[1:4]
W = OUT + "/work"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    return [json.loads(l) for l in gzip.open(p, "rt")]


RECEIPT = {
    "instances.jsonl.gz": "a3947992c152bdb112e5a60cb58a7a2c9bb54bd195041aab995441efa68fc068",
    "certificates.jsonl.gz": "37999fbffcb9fcaf682aef34027785f37f215712efa7be5077d2d4a064687e03",
    "annihilators.jsonl.gz": "06e48e15b958deb725c3c4687773791cbd7953f1d86d044c9ed75619a4c353c7",
    "annihilators-nonarchived.json": "750e28b5c70c5a784fedd3e14513902c519c4bb2096e48a495672d0da715f311",
}
RUN = "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/"
inputs = []
for f, h in RECEIPT.items():
    got = sha(os.path.join(INP, f))
    inputs.append({"path": RUN + f, "sha256": got,
                   "receipt_sha256_TASK-20260924-d0f80c": h, "match": got == h})
inputs.append({"path": "experiments/EXP-CERTBIN-060020/specification.yaml",
               "sha256": sha(os.path.join(INP, "specification.yaml")),
               "frozen_v1_sha256": "7da73ae8d55f5997bee0ccead0e77514b32c5c2e93941e147c58e0f8c69a83e0"})
inputs[-1]["match"] = inputs[-1]["sha256"] == inputs[-1]["frozen_v1_sha256"]

recs = {r["key"]: r for r in jl(os.path.join(INP, "instances.jsonl.gz"))}
reb = {o["key"]: o for o in jl(W + "/rebuild.jsonl.gz")}
crt = jl(W + "/certs.jsonl.gz")
ann = jl(W + "/ann.jsonl.gz")
neg = json.load(open(W + "/negctl.json"))
st = json.load(open(W + "/selftest.json"))
ctx = json.load(open(W + "/rebuild-context.json"))
ARMS = ["S3-U400", "S3-SAT100", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"]
m4 = {arm: jl(W + "/m4-%s.jsonl.gz" % arm) for arm in ARMS}

# ------------------------------------------------------------------ VC-2 / VC-3
vc2 = {"context": ctx, "per_arm": {}, "per_system_records": "work/rebuild.jsonl.gz", "mismatches": []}
vc3 = {"per_arm": {}, "mismatches": []}
for arm in ARMS:
    rows = [o for o in reb.values() if o["arm"] == arm]
    a2 = {"systems_decoded": len(rows),
          "codec_round_trip": sum(o["codec_round_trip"] for o in rows),
          "E_hex_canonical_form": sum(o["E_hex_canonical_form"] for o in rows),
          "E_sha256_match": sum(o["E_sha256_match"] for o in rows),
          "E_sha256_of_own_reencoding_match": sum(o["E_sha256_of_canonical_reencoding_match"] for o in rows)}
    if arm in ("S3-U400", "S3-SAT100", "F-RANDX19"):
        a2.update(systems_rebuilt_from_x_R=len(rows),
                  descent_route_A_eq_route_B=sum(o["route_A_eq_route_B"] for o in rows),
                  E_hex_reproduced=sum(o["rebuild_eq_archived"] for o in rows),
                  rebuilt_E_sha256_match=sum(o["rebuild_sha256_match"] for o in rows),
                  affine_decomposition_ok=sum(o["affine_decomposition_ok"] for o in rows),
                  first_differing_row_col=[[o["key"], o["first_diff_row_col"]] for o in rows
                                           if o["first_diff_row_col"] is not None])
    if arm == "N-CONV19":
        a2.update(quadratic_columns_rebuilt_from_slot_x_R=len(rows),
                  quadratic_part_eq_E_S3=sum(o["quadratic_part_eq_E_S3"] for o in rows),
                  slot_s3_key_x_R_consistent=sum(o["s3_key_consistent"] for o in rows),
                  linear_constant_part_inside_S_L=sum(o["lower_part_inside_S_L"] for o in rows),
                  not_equal_to_E_S3=sum(o["not_identity_draw"] for o in rows))
    if arm == "N-ELL19":
        a2.update(rows_0_17_inside_U=sum(o["rows_0_17_inside_U"] for o in rows),
                  row18_eq_ell_lin_plus_c=sum(o["row18_eq_ell_lin_plus_c"] for o in rows),
                  row18_c_distribution=dict(collections.Counter(str(o["row18_c"]) for o in rows)))
    if arm == "N-F219":
        a2.update(inside_U=sum(o["inside_U"] for o in rows))
    if arm == "N-AFF19":
        a2.update(inside_U=sum(o["inside_U"] for o in rows),
                  inside_affine_support_at_record_x_R=sum(o["inside_affine_support_at_x_R"] for o in rows))
    vc2["per_arm"][arm] = a2
    sat = [o for o in rows if o["role"] == "sat"]
    a3 = {"systems": len(rows), "s_by_own_exhaustive_2^20": len(rows),
          "s_match": sum(o["s_match"] for o in rows),
          "role_consistent_with_own_s": sum(o["role_consistent"] for o in rows),
          "own_s_distribution": dict(sorted(collections.Counter(str(o["s_mine"]) for o in rows).items()))}
    if arm in ("S3-U400", "S3-SAT100", "F-RANDX19"):
        a3["s_second_route_direct_S3_zero_count_match"] = sum(o["s_direct_match"] for o in rows)
    if sat:
        a3.update(satisfiable_controls=len(sat),
                  listed_solutions_total=sum(o["listed_solutions"] for o in sat),
                  listed_solutions_all_satisfy=sum(o["listed_solutions_all_satisfy"] for o in sat),
                  listed_equals_full_solution_set=sum(o["listed_equals_full_solution_set"] for o in sat))
    vc3["per_arm"][arm] = a3
    for o in rows:
        bad = [k for k, v in o.items() if isinstance(v, bool) and not v]
        if bad:
            (vc3 if any(b.startswith("s_") or b.startswith("listed") or b.startswith("role") for b in bad)
             else vc2)["mismatches"].append({"key": o["key"], "failed": bad})

# ------------------------------------------------------------------ VC-4
vc4_rows = []
for o in crt:
    keep = {k: o.get(k) for k in ("key", "closure", "format", "verified", "first_violated", "violated", "max_mu",
                                  "n_nodes", "max_prods_depth", "max_node_degree", "n_terms", "identity_holds",
                                  "counts_toward_M4", "counts_toward_W4", "sorted", "duplicates", "residual_size",
                                  "residual_monomials_first5", "rule_details", "line") if k in o}
    keep["own_s_of_key"] = reb[o["key"]]["s_mine"] if o["key"] in reb else None
    vc4_rows.append(keep)
verified_on_sat = [r["key"] for r in vc4_rows if r["verified"] and r["own_s_of_key"] != 0]
tt = {o["line"]: o for o in jl(W + "/certs-tt.jsonl.gz")}
tt_agree = 0
for r in vc4_rows:
    t = tt[r["line"]]
    ok = t["tt_output_is_one"]
    if r["format"] == "wdag-v1":
        ok = ok and t["tt_rule_c_ok"] and t["tt_rule_d_ok"] and max(t["tt_node_degrees"]) == r["max_node_degree"]
    r["second_route_truth_table_agrees"] = bool(ok == r["verified"])
    tt_agree += int(ok == r["verified"])
second_route = {"method": "each node evaluated as a function {0,1}^20 -> F_2 (tt(mu f_k) = tt(mu) AND tt(f_k), "
                          "tt(v_j p) = tt(v_j) AND tt(p)); output must be the all-ones function; node degrees "
                          "from the Moebius transform (ANF) of each node's truth table (code/run_certs_tt.py)",
                "certificates": len(vc4_rows), "agree_with_first_route": tt_agree,
                "file": "work/certs-tt.jsonl.gz"}

# ------------------------------------------------------------------ VC-8 tables
tab = {}
for r in vc4_rows:
    kind = "%s|%s|%s" % (r["closure"], r["key"].split(":")[0], r["format"])
    t = tab.setdefault(kind, {"submitted": 0, "verified": 0, "rejected": 0, "max_mu": collections.Counter(),
                              "node_count": collections.Counter(), "max_prods_depth": collections.Counter(),
                              "max_node_degree": collections.Counter(), "counts_toward_M4": 0,
                              "counts_toward_W4": 0})
    t["submitted"] += 1
    t["verified" if r["verified"] else "rejected"] += 1
    t["max_mu"][str(r.get("max_mu"))] += 1
    if r["format"] == "wdag-v1":
        t["node_count"][str(r["n_nodes"])] += 1
        t["max_prods_depth"][str(r["max_prods_depth"])] += 1
        t["max_node_degree"][str(r["max_node_degree"])] += 1
        t["counts_toward_W4"] += int(r["verified"])
    else:
        t["counts_toward_M4"] += int(r["counts_toward_M4"])
        t["counts_toward_W4"] += int(r["counts_toward_W4"])
for o in ann:
    kind = "%s|%s|%s" % (o["closure"], o["key"].split(":")[0], o["format"])
    t = tab.setdefault(kind, {"submitted": 0, "verified": 0, "rejected": 0, "size_L": collections.Counter(),
                              "dim_S": collections.Counter()})
    t["submitted"] += 1
    t["verified" if o["verified"] else "rejected"] += 1
    t["size_L"][str(o["size_L"])] += 1
    t["dim_S"][str(o["dim_S"])] += 1
for t in tab.values():
    for k, v in list(t.items()):
        if isinstance(v, collections.Counter):
            t[k] = dict(sorted(v.items()))
per_arm = {}
for arm in ARMS:
    a2, a3 = vc2["per_arm"][arm], vc3["per_arm"][arm]
    per_arm[arm] = {"systems_decoded": a2["systems_decoded"],
                    "systems_rebuilt_from_x_R": a2.get("systems_rebuilt_from_x_R",
                                                       a2.get("quadratic_columns_rebuilt_from_slot_x_R", 0)),
                    "E_hex_matches_own_rebuild": a2.get("E_hex_reproduced", a2.get("quadratic_part_eq_E_S3")),
                    "E_sha256_matches": a2["E_sha256_match"], "s_matches": a3["s_match"],
                    "rebuild_scope": ("full E_S3(x_R) from x_R (two descent routes)"
                                      if arm in ("S3-U400", "S3-SAT100", "F-RANDX19") else
                                      "quadratic columns 21..210 from the slot's x_R; columns 0..20 checked "
                                      "inside S_L" if arm == "N-CONV19" else
                                      "synthetic: decoded from E_hex and structure-checked (see vc2_rebuild)")}
cover = collections.defaultdict(collections.Counter)
for r in vc4_rows:
    cover["%s|%s" % (recs[r["key"]]["arm"], recs[r["key"]]["role"])][r["format"] + "_submitted"] += 1
    if r["verified"]:
        cover["%s|%s" % (recs[r["key"]]["arm"], recs[r["key"]]["role"])][r["format"] + "_verified"] += 1
for o in ann:
    cover["%s|%s" % (recs[o["key"]]["arm"], recs[o["key"]]["role"])]["ann-v1_submitted"] += 1
    cover["%s|%s" % (recs[o["key"]]["arm"], recs[o["key"]]["role"])]["ann-v1_verified"] += int(o["verified"])
arm_role_sizes = collections.Counter("%s|%s" % (r["arm"], r["role"]) for r in recs.values())
coverage = {k: dict({"systems": n}, **dict(cover.get(k, {}))) for k, n in sorted(arm_role_sizes.items())}

# ------------------------------------------------------------------ VC-6
w_path = OUT + "/m4-witnesses.jsonl.gz"
wit = jl(w_path)
vc6 = {"arm": "S3-U400", "systems": len(m4["S3-U400"]),
       "one_in_M4_count": sum(o["one_in_M4"] for o in m4["S3-U400"]),
       "witnesses_written": sum(1 for w in wit if w["kind"] == "M4_non_refutation_witness"),
       "witnesses_checked": sum(1 for w in wit if w["kind"] == "M4_non_refutation_witness" and w["checked"]),
       "own_flat_certificates_written": sum(1 for w in wit if w["kind"] == "M4_refutation_own_flat_v1"),
       "own_flat_certificates_checked": sum(1 for w in wit if w["kind"] == "M4_refutation_own_flat_v1"
                                            and w["checked"]),
       "witness_file": "m4-witnesses.jsonl.gz",
       "rank_M4_distribution": dict(sorted(collections.Counter(str(o["rank_M4"]) for o in m4["S3-U400"]).items())),
       "dims_by_deg_M4_distribution": dict(collections.Counter(json.dumps(o["dims_by_deg_M4"])
                                                               for o in m4["S3-U400"]).most_common()),
       "per_system": [{k: o[k] for k in ("key", "rank_M4", "dims_by_deg_M4", "one_in_M4", "witness_checked")
                       if k in o} for o in m4["S3-U400"]],
       "method": "RREF of own M_4 (4009 x 6196, columns in ann-v1 order, constant last); 1 in rowspace iff the "
                 "constant column is a pivot; lambda: lambda(1) = 1, lambda(pivot col of RREF row r) = R[r][const], "
                 "other free coordinates 0; checked by parity against every UNREDUCED M_4 row.",
       "supplementary_other_arms": {arm: {"systems": len(m4[arm]),
                                          "one_in_M4": sum(o["one_in_M4"] for o in m4[arm]),
                                          "witness_checked": sum(bool(o.get("witness_checked")) for o in m4[arm]),
                                          "by_role": dict(collections.Counter(
                                              "%s:one_in_M4=%s" % (recs[o["key"]]["role"], o["one_in_M4"])
                                              for o in m4[arm])),
                                          "witness_file": "work/m4-supp-witnesses-%s.jsonl.gz" % arm}
                                    for arm in ARMS if arm != "S3-U400"}}

# ------------------------------------------------------------------ VC-7
nc = neg["controls"]
nctab = collections.defaultdict(lambda: collections.defaultdict(lambda: {"built": 0, "rejected": 0,
                                                                            "reasons": collections.Counter()}))
for c in nc:
    kind = "|".join(c["kind"])
    t = nctab[kind][c["type"]]
    t["built"] += 1
    t["rejected"] += int(c["rejected"])
    t["reasons"][str(c["checker_verdict"].get("first_violated"))] += 1
nctab = {k: {ty: dict(v, reasons=dict(v["reasons"])) for ty, v in d.items()} for k, d in nctab.items()}
not_applicable = [{"kinds": "every ann-v1 kind", "types": ["a", "b", "c", "d"],
                   "reason": "ann-v1 has no rows, k or mu to corrupt and no degree discipline; removing a "
                             "functional from L does not guarantee an invalid certificate, so it cannot be a "
                             "must-reject control. ann-v1 kinds carry (e), (f), (g), (h) instead."},
                  {"kinds": "every refutation kind", "types": ["f", "g", "h"],
                   "reason": "(f)-(h) are defined for ann-v1 only."}]
vc7 = {"position_rule": "numpy.random.Generator(numpy.random.PCG64(%d)), consumed in code/run_negctl.py order; "
                        "5 base certificates per kind drawn without replacement from the kind's certificates my "
                        "checker verified; (a)-(c) modify the OUTPUT node (wdag-v1) or C (flat-v1), each change "
                        "required to be a nonzero element of B" % neg["seed"],
       "table": nctab, "total_built": len(nc), "total_rejected": sum(c["rejected"] for c in nc),
       "all_rejected": all(c["rejected"] for c in nc), "vacuous": neg["vacuous"],
       "not_applicable": not_applicable, "positive_controls": neg["positive_controls"],
       "controls": nc}

# ------------------------------------------------------------------ environment and hashes
code_files = sorted(glob.glob(OUT + "/code/*"))
work_files = sorted(glob.glob(W + "/*"))
env = {"python": platform.python_version(), "numpy": np.__version__,
       "gcc": subprocess.run(["gcc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
       "libgf2k_so_sha256": sha(LIB), "platform": platform.platform(), "nproc": os.cpu_count(),
       "PYTHONDONTWRITEBYTECODE": os.environ.get("PYTHONDONTWRITEBYTECODE"),
       "checkout": "main checkout /home/user/crypto-autoresearcher at a832d63ac7e566bcf7e78f8523742e5af4dd7c8a "
                   "(TASK-20260926-5d1557 archive commit; clean tree; pushed to "
                   "origin/claude/macaulay-matrix-gpu-vu82ew). NOT a dedicated worktree (dispatch precondition); "
                   "inputs copied to a scratch directory and re-hashed against the d0f80c receipt before use.",
       "imports": "numpy and the Python standard library only; no module of the repository src/ package tree",
       "code_sha256": {os.path.relpath(p, OUT): sha(p) for p in code_files},
       "resources": [json.loads(l) for l in open(W + "/resources.jsonl")]}

ambiguities = json.load(open(OUT + "/code/ambiguities.json"))

V = {
    "schema": "certbin.n19.independent_verification.v1",
    "task_id": "TASK-20260926-401771",
    "joint": "J1 (REVIEW-CERTBIN-20260926-d7249d)",
    "experiment_id": "EXP-CERTBIN-060020", "run_id": "RUN-CERTBIN-a3fc60",
    "status": "complete; sealed by seal.txt",
    "started_utc": "2026-09-26T03:26:11Z",
    "assembled_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "sessions": ["session 1: validator subagent (claude-opus-5-5), the only session that wrote this output"],
    "authorship_statement": "Every line of code/ was written in this session from the specification texts named "
                            "in inputs; no producer code base (impl/, verifier/, the src/ engine package, "
                            "tools/gf2_replay_rc1.py, tests/test_gf2_kernels.py, archived engines, earlier "
                            "reviewers' code, the archive's extract_and_validate.py) was read, and no "
                            "module of the repository src/ package tree is imported.",
    "inputs": inputs,
    "environment": env,
    "self_tests": st,
    "ambiguities": ambiguities,
    "vc2_rebuild": vc2,
    "vc3_satisfiability": vc3,
    "vc4_refutation_certificates": {
        "submitted": len(vc4_rows), "verified": sum(r["verified"] for r in vc4_rows),
        "rejected": sum(not r["verified"] for r in vc4_rows),
        "rejected_keys": [r["key"] for r in vc4_rows if not r["verified"]],
        "verified_on_a_system_with_own_s_ge_1": verified_on_sat,
        "keys_not_in_instances": [r["key"] for r in vc4_rows if r["key"] not in recs],
        "second_route": second_route,
        "note_flat_v1": "flat-v1 'verified' = the identity sum mu*f_k = 1 holds in B (certifies unsatisfiability "
                        "and 1 in rowspace(M_{2+max|mu|})). counts_toward_M4 / counts_toward_W4 are true only at "
                        "max |mu| <= 2 (FORMAT flat-v1).",
        "per_certificate": vc4_rows},
    "vc5_ann_v1": {"submitted": len(ann), "verified": sum(o["verified"] for o in ann),
                   "rejected": sum(not o["verified"] for o in ann),
                   "nonarchived": json.load(open(W + "/ann-nonarchived.json")),
                   "per_certificate": [{k: o.get(k) for k in ("key", "closure", "format", "verified", "size_L",
                                                              "rank_L", "dim_S", "dim_S_cap_B3", "A1", "A2", "A3",
                                                              "first_violated")} for o in ann]},
    "vc6_m4_witnesses": vc6,
    "vc7_negative_controls": vc7,
    "vc8_tables": {"per_closure_arm_format": tab, "per_arm": per_arm,
                   "vc6_witness_count": vc6["witnesses_checked"],
                   "certificate_coverage_per_arm_role": coverage},
    "work_file_sha256": {os.path.relpath(p, OUT): sha(p) for p in work_files},
}
json.dump(V, open(OUT + "/verification.json", "w"), indent=1, sort_keys=False)
print("written", os.path.getsize(OUT + "/verification.json"))
