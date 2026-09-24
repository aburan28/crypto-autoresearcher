#!/usr/bin/env python3
"""J3 control checks, TASK-20260924-c83b05 (read-only on the archived package;
writes only j3-checks/controls_results.json). No closure is recomputed here.

K1  SET RULES: U62, S62, C20, N-AFF62, N-F262 recomputed by own code from the
    Stage-1 targets-*.jsonl.gz (D = 4 records) and compared with
    instance-sets.json (idx lists, order, sizes).
K2  C-ORACLE and C-BASE inputs: instance-sets.json "archived" fields equal the
    Stage-1 target records (D = 4 and D = 3) for all 268; the phase-1
    checkpoint's s_B, stratum_B, s_A, oracle_A_equals_B, M_4, M_3 against those
    archived values; closures.jsonl.gz M_3/M_4 rows equal the checkpoint.
K3  E CONSTRUCTION (third construction, for C-VERIFIER's agreement and
    C-NULLS): own S_3 descent (evaluation at all 2^18 points with own
    F_{2^17} arithmetic + own Moebius transform) for all 144 curve instances,
    compared with instance-sets.json E_hex; own union support U_k from own
    E^0 = E(0), E^j = E(t^j) + E^0, sizes against p1-instances
    union_support_size_per_eq; every N-F262 instance inside U; every N-AFF62
    E_hex equal to own A0 + sum_j r_j Aj; every N-F262 E_hex equal to p1.
    certificate-verification.json construction[]: own_sha256 against
    instance-sets E_sha256.
K4  C-DET: pid of determinism.json against the --phase determinism
    invocation and against the main, resume and verifier pids; the instance
    list against the rule; recomputed values against closures.jsonl.gz.
K5  C-MONO: for every clause of analysis.instrument_checks, the number of
    instances whose ANTECEDENT is true (a clause with 0 such instances cannot
    fail); plus own dimension-level monotonicity checks that can fail:
    W_4 dims[0] = rank M_4; M_5 dims_by_deg[4] >= rank M_4; W_5 dims[0] =
    rank M_5; W_5 dims_by_deg[4] >= final dim W_4.
K6  C-PS1 and C-CERT consistency: every reported refutation (one = true) has
    certificate "emitted", exactly one certificates.jsonl.gz line and one
    certificate-verification.json entry with equal size and max deg mu; no
    UNCERTIFIED / UNDETERMINED record; engine self-check true; certificates
    equal the checkpoint certificate lists; S62 records carry no refutation.
K7  W_5 SELECTION re-derived from VERIFIED outcomes (certificate-verification
    .json) and compared with checkpoint/w5-selection.json and with the W_5
    records present.
K8  ASSEMBLY: every W_4 / M_5 / W_5 row of closures.jsonl.gz equals its
    checkpoint record.
"""
import gzip
import json
import os
import resource
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
SRC = os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, os.path.join(HERE, "..", "j2-constructions"))
import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402

EQM = oa.eq_masks(18)
EQPOS = {m: j for j, m in enumerate(EQM)}


def gz(p):
    return json.load(gzip.open(p, "rt"))


def own_E_rows(B, xR):
    S = oa.s3_all_points(B, xR)
    rows = []
    for k in range(17):
        a = ((S >> k) & 1).astype(np.uint8)
        for i in range(18):
            v = a.reshape(-1, 2, 1 << i)
            v[:, 1, :] ^= v[:, 0, :]
        ms = np.flatnonzero(a)
        r = 0
        for m in ms.tolist():
            if bin(m).count("1") > 2:
                raise ValueError("degree > 2")
            r |= 1 << EQPOS[m]
        rows.append(r)
    return rows


def main():
    t0 = time.time()
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J3"}
    inst = json.load(open(os.path.join(RUN, "instance-sets.json")))
    sets = inst["sets"]
    tg = {}
    for fam in ("F-S3", "F-AFF-1", "F-NULLF2"):
        by = {}
        for line in gzip.open(os.path.join(SRC, f"targets-{fam}.jsonl.gz"), "rt"):
            r = json.loads(line)
            by.setdefault(r["idx"], {})[r["D"]] = r
        tg[fam] = by
    # K1
    s3 = tg["F-S3"]
    rule = {
        "U62": [i for i in sorted(s3) if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is False],
        "S62": [i for i in sorted(s3) if s3[i][4]["stratum"] == "sat" and not s3[i][4]["degenerate"]][:62],
        "C20": [i for i in sorted(s3) if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is True][:20],
        "N-AFF62": [i for i in sorted(tg["F-AFF-1"]) if tg["F-AFF-1"][i][4]["stratum"] == "unsat" and not tg["F-AFF-1"][i][4]["degenerate"]][:62],
        "N-F262": [i for i in sorted(tg["F-NULLF2"]) if tg["F-NULLF2"][i][4]["stratum"] == "unsat"][:62],
    }
    k1 = {s: {"own_rule_size": len(rule[s]), "archived_size": len(sets[s]),
              "equal": rule[s] == [x["idx"] for x in sets[s]]} for s in rule}
    k1["U62_all_one_in_R_3_false"] = all(s3[i][3]["one_in_R"] is False for i in rule["U62"])
    k1["U62_all_nondegenerate"] = all(not s3[i][4]["degenerate"] for i in rule["U62"])
    k1["S62_degenerate_count_in_stratum_sat_prefix"] = sum(1 for i in sorted(s3) if s3[i][4]["stratum"] == "sat" and s3[i][4]["degenerate"])
    k1["C20_nondegenerate"] = all(not s3[i][4]["degenerate"] for i in rule["C20"])
    k1["N_F262_nondegenerate"] = all(not tg["F-NULLF2"][i][4]["degenerate"] for i in rule["N-F262"])
    k1["F-S3_unsat_nondeg_total_D4"] = sum(1 for i in s3 if s3[i][4]["stratum"] == "unsat" and not s3[i][4]["degenerate"])
    k1["F-S3_unsat_oneR_true_D4"] = sum(1 for i in s3 if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is True)
    k1["F-S3_unsat_oneR_false_D4"] = sum(1 for i in s3 if s3[i][4]["stratum"] == "unsat" and s3[i][4]["one_in_R"] is False)
    res["K1_set_rules"] = k1
    # K2
    fam_of = {"U62": "F-S3", "S62": "F-S3", "C20": "F-S3", "N-AFF62": "F-AFF-1", "N-F262": "F-NULLF2"}
    p1 = gz(os.path.join(RUN, "checkpoint", "p1-sets-oracles-base.json.gz"))["records"]
    crow = {}
    for line in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"):
        r = json.loads(line)
        crow[(r["key"], r["closure"])] = r
    bad_arch, bad_p1, bad_rows = [], [], []
    for s, lst in sets.items():
        for x in lst:
            r3, r4 = tg[fam_of[s]][x["idx"]][3], tg[fam_of[s]][x["idx"]][4]
            a = x["archived"]
            want = {"s": r4["s"], "stratum": r4["stratum"], "degenerate": r4["degenerate"], "x_R": r4["x_R"],
                    "rank_4": r4["rank"], "one_in_R_4": r4["one_in_R"], "rank_3": r3["rank"], "one_in_R_3": r3["one_in_R"],
                    "stratum_D3": r3["stratum"], "s_D3": r3["s"]}
            if a != want:
                bad_arch.append(x["key"])
            q = p1[x["key"]]
            ok = (q["s_B"] == r4["s"] and q["stratum_B"] == r4["stratum"] and q["M_4"]["rank"] == r4["rank"]
                  and q["M_4"]["one"] == r4["one_in_R"] and q["M_3"]["rank"] == r3["rank"] and q["M_3"]["one"] == r3["one_in_R"]
                  and q["oracle_agree_archive"] and q["base_agree_archive"])
            if fam_of[s] == "F-S3":
                ok = ok and q["s_A"] == r4["s"] and q["oracle_A_equals_B"] is True and q.get("ell_identity_holds") is True
            if not ok:
                bad_p1.append(x["key"])
            for D in (3, 4):
                cr = crow[(x["key"], f"M_{D}")]
                if cr["rank"] != q[f"M_{D}"]["rank"] or cr["one"] != q[f"M_{D}"]["one"]:
                    bad_rows.append((x["key"], D))
    res["K2_oracle_base_inputs"] = {"instances": sum(len(v) for v in sets.values()),
                                    "instance_sets_archived_fields_differ_from_stage1": bad_arch,
                                    "p1_checkpoint_disagrees_with_stage1": bad_p1,
                                    "closures_M3_M4_rows_disagree_with_checkpoint": bad_rows,
                                    "strata_in_sets": {s: sorted(set(x["archived"]["stratum"] for x in v)) for s, v in sets.items()},
                                    "s_range_S62": [min(x["archived"]["s"] for x in sets["S62"]), max(x["archived"]["s"] for x in sets["S62"])]}
    # K3
    curve = json.load(open(os.path.join(SRC, "curve.json")))
    B = curve["B"]
    E0 = own_E_rows(B, 0)
    Ej = [[a ^ b for a, b in zip(own_E_rows(B, 1 << j), E0)] for j in range(17)]
    U = list(E0)
    for e in Ej:
        U = [u | x for u, x in zip(U, e)]
    p1src = gz(os.path.join(SRC, "checkpoint", "p1-instances.json.gz"))
    Usizes = [bin(u).count("1") for u in U]
    cur_bad = []
    tstart = time.time()
    for s in ("U62", "S62", "C20"):
        for x in sets[s]:
            rows = own_E_rows(B, x["archived"]["x_R"])
            if rows != [int(h, 16) for h in x["E_hex"]]:
                cur_bad.append(x["key"])
    t_cur = time.time() - tstart
    A0 = [int(h, 16) for h in p1src["F-AFF-1"]["A0_hex"]]
    Aj = [[int(h, 16) for h in row] for row in p1src["F-AFF-1"]["Aj_hex"]]
    aff_bad = []
    for x in sets["N-AFF62"]:
        r = x["archived"]["x_R"]
        rows = list(A0)
        for j in range(17):
            if (r >> j) & 1:
                rows = [a ^ b for a, b in zip(rows, Aj[j])]
        if rows != [int(h, 16) for h in x["E_hex"]]:
            aff_bad.append(x["key"])
    nfp = {t["idx"]: t for t in p1src["F-NULLF2"]["targets"]}
    nf_bad, nf_out = [], []
    for x in sets["N-F262"]:
        rows = [int(h, 16) for h in x["E_hex"]]
        if rows != [int(h, 16) for h in nfp[x["idx"]]["E_hex"]]:
            nf_bad.append(x["key"])
        if any(r & ~u for r, u in zip(rows, U)):
            nf_out.append(x["key"])
    # F-AFF-1 supports (same-support null): A0 inside supp(E^0), Aj inside supp(E^j)
    aff_supp_ok = all((a & ~e) == 0 for a, e in zip(A0, E0)) and all(all((a & ~e) == 0 for a, e in zip(Aj[j], Ej[j])) for j in range(17))
    ver = json.load(open(os.path.join(RUN, "certificate-verification.json")))
    esha = {x["key"]: x["E_sha256"] for v in sets.values() for x in v}
    cons = ver["construction"]
    res["K3_E_construction_third_route"] = {
        "own_curve_E_equals_instance_sets_E_hex": {"checked": 144, "disagree": cur_bad, "seconds": round(t_cur, 1)},
        "own_union_support_sizes": Usizes, "archived_union_support_sizes": p1src["F-NULLF2"]["union_support_size_per_eq"],
        "union_sizes_equal": Usizes == p1src["F-NULLF2"]["union_support_size_per_eq"],
        "N-F262_outside_own_U": nf_out, "N-F262_E_hex_differs_from_p1": nf_bad,
        "N-AFF62_E_hex_differs_from_own_A0_plus_sum": aff_bad,
        "F-AFF-1_A0_Aj_inside_curve_supports": aff_supp_ok,
        "verifier_construction_entries": len(cons),
        "verifier_construction_keys_equal_curve_keys": sorted(c["key"] for c in cons) == sorted(x["key"] for s in ("U62", "S62", "C20") for x in sets[s]),
        "verifier_own_sha256_equals_engine_E_sha256": all(c["own_sha256"] == esha[c["key"]] for c in cons),
        "verifier_agree_flags_all_true": all(c["agree_with_engine_E"] for c in cons),
    }
    # K4
    det = json.load(open(os.path.join(RUN, "determinism.json")))
    invs = [json.loads(line) for line in open(os.path.join(RUN, "checkpoint", "invocations.jsonl"))]
    neg = json.load(open(os.path.join(RUN, "negative-controls-verification.json")))
    want_keys = [x["key"] for x in sorted(sets["U62"], key=lambda z: z["idx"])[:10]] + \
                [x["key"] for x in sorted(sets["S62"], key=lambda z: z["idx"])[:5]]
    mism = []
    for r in det["instances"]:
        w, m = crow[(r["key"], "W_4")], crow[(r["key"], "M_5")]
        if not (r["W_4"]["final_dim"] == w["final_dim"] and r["W_4"]["iterations_to_fixpoint"] == w["iterations_to_fixpoint"]
                and r["W_4"]["one"] == w["one"] and r["M_5"]["rank"] == m["rank"] and r["M_5"]["one"] == m["one"]):
            mism.append(r["key"])
    det_inv = [i for i in invs if "--phase" in i["argv"]]
    res["K4_C_DET"] = {"determinism_pid": det["pid"], "phase_determinism_invocation_pids": [i["pid"] for i in det_inv],
                       "main_pid": invs[0]["pid"], "resume_pid": invs[-1]["pid"], "verifier_pids": [ver["pid"], neg["pid"]],
                       "pid_matches_determinism_invocation": det["pid"] in [i["pid"] for i in det_inv],
                       "pid_distinct_from_main": det["pid"] != invs[0]["pid"],
                       "instances_equal_rule": [r["key"] for r in det["instances"]] == want_keys,
                       "recomputed_vs_closures_jsonl_mismatch": mism, "recorded_mismatches": det["mismatches"],
                       "recomputed_not_reread": "driver.determinism() calls load_instances() and Closure.w_closure / macaulay_closure afresh; checkpoints are read only as the comparand (code reading, driver.py lines 304-349)"}
    # K5
    s_of = {x["key"]: s for s, v in sets.items() for x in v}
    ante = {"C20: 1 in W_4 required": 0, "M_4 refutes (W_4 ran)": 0, "dim W_4 vs rank M_4 (applies to every W_4 record)": 0,
            "W_4 refutes and W_5 ran": 0, "M_5 refutes and W_5 ran": 0, "M_4 refutes and W_5 ran": 0}
    dimviol = []
    for key, s in s_of.items():
        m4 = crow[(key, "M_4")]
        w4 = crow.get((key, "W_4"))
        m5 = crow.get((key, "M_5"))
        w5 = crow.get((key, "W_5"))
        if s == "C20":
            ante["C20: 1 in W_4 required"] += 1
        if w4 is not None:
            ante["dim W_4 vs rank M_4 (applies to every W_4 record)"] += 1
            if m4["one"]:
                ante["M_4 refutes (W_4 ran)"] += 1
            if w4["dims"][0] != m4["rank"]:
                dimviol.append((key, "W_4 dims[0] != rank M_4"))
        if m5 is not None and m5["dims_by_deg"][4] < m4["rank"]:
            dimviol.append((key, "M_5 cap B_<=4 smaller than rank M_4"))
        if w5 is not None:
            if w4 is not None and w4.get("one"):
                ante["W_4 refutes and W_5 ran"] += 1
            if m5 is not None and m5.get("one"):
                ante["M_5 refutes and W_5 ran"] += 1
            if m4["one"]:
                ante["M_4 refutes and W_5 ran"] += 1
            if w5["dims"][0] != m5["rank"]:
                dimviol.append((key, "W_5 dims[0] != rank M_5"))
            if w5["dims_by_deg"][4] < w4["final_dim"]:
                dimviol.append((key, "W_5 cap B_<=4 smaller than W_4"))
    res["K5_C_MONO"] = {"instances_with_true_antecedent_per_clause": ante,
                        "own_dimension_monotonicity_checks": {"W_4_records": sum(1 for k in s_of if (k, "W_4") in crow),
                                                              "M_5_records": sum(1 for k in s_of if (k, "M_5") in crow),
                                                              "W_5_records": sum(1 for k in s_of if (k, "W_5") in crow),
                                                              "violations": dimviol}}
    # K6
    certs = {}
    dup = []
    for line in gzip.open(os.path.join(RUN, "certificates.jsonl.gz"), "rt"):
        c = json.loads(line)
        k = (c["key"], c["closure"])
        if k in certs:
            dup.append(k)
        certs[k] = c
    vmap = {}
    for r in ver["certificates"]:
        vmap.setdefault((r["key"], r["closure"]), []).append(r)
    rep = [(k, c) for (k, c), r in crow.items() if c in ("W_4", "M_5", "W_5") and r.get("one")]
    missing_cert = [x for x in rep if x not in certs]
    extra_cert = [x for x in certs if x not in set(rep)]
    not_emitted = [x for x in rep if crow[x].get("certificate") != "emitted"]
    selfcheck_bad = [x for x in rep if crow[x].get("engine_self_check_sum_is_1") is not True]
    vmiss = [x for x in certs if len(vmap.get(x, [])) != 1]
    size_bad = [x for x in certs if vmap.get(x) and (vmap[x][0]["size"] != certs[x]["size"] or vmap[x][0]["max_deg_mu"] != certs[x]["max_deg_mu"])]
    undet = [k for k, r in crow.items() if r.get("label") in ("UNDETERMINED(budget)",) or r.get("certificate") == "UNCERTIFIED"]
    ckc = {}
    for f in sorted(os.listdir(os.path.join(RUN, "checkpoint"))):
        if f.startswith("p-") and f.endswith(".json.gz"):
            d = gz(os.path.join(RUN, "checkpoint", f))
            for c in d["certificates"]:
                ckc[(c["key"], c["closure"])] = c
    cert_vs_ck = [k for k in set(ckc) | set(certs) if ckc.get(k) != certs.get(k)]
    s62_ref = [k for k, r in crow.items() if s_of.get(k[0]) == "S62" and k[1] in ("W_4", "M_5", "W_5") and r.get("one")]
    kinds = {}
    for (k, c) in certs:
        kk = f"{c}/{s_of[k]}"
        kinds[kk] = kinds.get(kk, 0) + 1
    res["K6_C_CERT_C_PS1_consistency"] = {
        "reported_refutations": len(rep), "certificate_lines": len(certs), "duplicate_certificate_lines": dup,
        "reported_without_certificate": missing_cert, "certificate_without_reported_refutation": extra_cert,
        "reported_not_marked_emitted": not_emitted, "engine_self_check_not_true": selfcheck_bad,
        "certificates_without_exactly_one_verification_entry": vmiss, "size_or_maxdeg_mismatch_engine_vs_verifier": size_bad,
        "undetermined_or_uncertified_records": undet, "certificates_differ_from_checkpoint_lists": cert_vs_ck,
        "S62_records_reporting_a_refutation": s62_ref, "certificate_kinds_present": kinds,
        "note": "counts of verified certificates per set are J4's; here only one-to-one consistency is checked"}
    # K7
    vok = {(r["key"], r["closure"]) for r in ver["certificates"] if r["verified"]}
    sel_verified = {}
    for s in ("U62", "S62", "N-AFF62", "N-F262"):
        lst = sorted(sets[s], key=lambda z: z["idx"])
        if s == "S62":
            sel_verified[s] = [x["key"] for x in lst[:10]]
        else:
            resid = [x["key"] for x in lst if (x["key"], "W_4") not in vok and (x["key"], "M_5") not in vok]
            sel_verified[s] = resid if s == "U62" else resid[:10]
    sel_rec = json.load(open(os.path.join(RUN, "checkpoint", "w5-selection.json")))
    w5_present = {s: sorted([k for (k, c) in crow if c == "W_5" and s_of[k] == s], key=lambda z: int(z.split(":")[-1])) for s in sel_rec}
    res["K7_W5_selection"] = {"from_verified_outcomes": sel_verified, "recorded_w5_selection": sel_rec,
                              "equal": sel_verified == sel_rec,
                              "W_5_records_present_equal_selection": all(w5_present[s] == sel_rec[s] for s in sel_rec),
                              "reported_but_unverified_W4_or_M5_refutations": sorted(set(rep) - vok)}
    # K8
    diffs = []
    for f in sorted(os.listdir(os.path.join(RUN, "checkpoint"))):
        if f.startswith("p-") and f.endswith(".json.gz"):
            d = gz(os.path.join(RUN, "checkpoint", f))
            for key, r in d["records"].items():
                row = dict(crow.get((key, d["closure"]), {}))
                for extra in ("key", "set", "idx", "closure"):
                    row.pop(extra, None)
                if row != r:
                    diffs.append((key, d["closure"]))
    n_ck = sum(len(gz(os.path.join(RUN, "checkpoint", f))["records"]) for f in os.listdir(os.path.join(RUN, "checkpoint"))
               if f.startswith("p-") and f.endswith(".json.gz"))
    res["K8_assembly"] = {"closure_rows_W4_M5_W5": sum(1 for (k, c) in crow if c in ("W_4", "M_5", "W_5")),
                          "checkpoint_records": n_ck, "rows_differing_from_checkpoint": diffs,
                          "total_rows": len(crow)}
    res["wall_seconds"] = round(time.time() - t0, 1)
    res["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    json.dump(res, open(os.path.join(HERE, "controls_results.json"), "w"), indent=1, default=str)
    short = {"K1": {s: k1[s]["equal"] for s in rule}, "K2": [len(bad_arch), len(bad_p1), len(bad_rows)],
             "K3": {k: v for k, v in res["K3_E_construction_third_route"].items() if k not in ("own_union_support_sizes", "archived_union_support_sizes")},
             "K4": {k: v for k, v in res["K4_C_DET"].items() if k != "recomputed_not_reread"},
             "K5": res["K5_C_MONO"], "K6": {k: (v if not isinstance(v, list) else len(v)) for k, v in res["K6_C_CERT_C_PS1_consistency"].items()},
             "K7": [res["K7_W5_selection"]["equal"], res["K7_W5_selection"]["W_5_records_present_equal_selection"]],
             "K8": {k: (v if not isinstance(v, list) else len(v)) for k, v in res["K8_assembly"].items()}}
    print(json.dumps(short, indent=1, default=str))


if __name__ == "__main__":
    main()
