#!/usr/bin/env python3
"""TASK-20260926-59169c CP-2: compare the archived J7 output (TASK-20260926-83cebf)
and the archived J1 output (TASK-20260926-f0e5a4) with RUN-CERTBIN-6ebb0e.

Own code, standard library only. Reads only archived bytes (git archive of
a524be32e into --snap). Writes comparison-core.json (merged into
comparison.json by assemble.py).

Encoding conventions applied (each is reported, and never counted as a
disagreement unless the decoded content differs):
  * rows: compared as decoded integers (bit j = column j), not as strings;
  * E_sha256: sha256(json.dumps(E_hex)) with canonical lowercase unpadded hex
    (convention established on the run's own 1440 instances first);
  * W_4 dims: the run lists W^(0)..W^(fixpoint); J7 lists W^(0)..W^(fixpoint+1),
    whose last entry repeats. Agreement = run.dims == j7.dims[:-1] and
    j7.dims[-1] == j7.dims[-2];
  * fallen per iteration: run new_fallen_per_iteration are increments, J7
    fallen_basis_size_per_iteration are cumulative sizes;
  * rc_b c: run int with bit k = c_k, J7 list of 17 bits.
"""
import argparse, gzip, hashlib, json, math, os, sys
from collections import Counter, defaultdict
from decimal import Decimal, getcontext

REV = "coordination/review/certbin-20260926-089841"
RUNREL = "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"


def jl(p):
    return [json.loads(l) for l in gzip.open(p, "rt")]


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ints(rows):
    return [int(h, 16) for h in rows]


def canon(rows):
    return [format(int(h, 16), "x") for h in rows]


def esha(rows):
    return hashlib.sha256(json.dumps(rows).encode("utf-8")).hexdigest()


def item(agree, j7=None, run=None, note=None):
    d = {"agree": bool(agree)}
    if not agree:
        d["j7"] = j7
        d["run"] = run
    if note:
        d["note"] = note
    return d


# --------------------------------------------------------------- CP95 exact
getcontext().prec = 80


def binom_cdf_le(x, n, p):
    """P(X <= x), X ~ Bin(n, p), p Decimal; exact sum at 80 digits."""
    q = 1 - p
    s = Decimal(0)
    for k in range(0, x + 1):
        s += Decimal(math.comb(n, k)) * (p ** k) * (q ** (n - k))
    return s


def cp95(x, n, alpha=Decimal("0.05")):
    a2 = alpha / 2
    if n == 0:
        return (Decimal(0), Decimal(1))
    if x == 0:
        lo = Decimal(0)
    else:
        # lower: P(X >= x | p) = a2  <=> 1 - P(X <= x-1 | p) = a2
        l, h = Decimal(0), Decimal(1)
        for _ in range(200):
            m = (l + h) / 2
            if 1 - binom_cdf_le(x - 1, n, m) < a2:
                l = m
            else:
                h = m
        lo = (l + h) / 2
    if x == n:
        hi = Decimal(1)
    else:
        l, h = Decimal(0), Decimal(1)
        for _ in range(200):
            m = (l + h) / 2
            if binom_cdf_le(x, n, m) > a2:
                l = m
            else:
                h = m
        hi = (l + h) / 2
    return (lo, hi)


def r6(v):
    return float(round(v, 6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S = a.snap
    rev = os.path.join(S, REV)
    j7d = os.path.join(rev, "reviews/TASK-20260926-83cebf")
    j1d = os.path.join(rev, "reviews/TASK-20260926-f0e5a4")
    run = os.path.join(S, RUNREL)

    d7 = json.load(open(os.path.join(j7d, "rederivation.json")))
    sr = jl(os.path.join(j7d, "stream-replay.jsonl.gz"))
    v1 = json.load(open(os.path.join(j1d, "verification.json")))
    keymap = json.load(open(os.path.join(rev, "blind-inputs-key.json")))
    inst = {r["key"]: r for r in jl(os.path.join(run, "instances.jsonl.gz"))}
    cl = defaultdict(dict)
    for r in jl(os.path.join(run, "closures.jsonl.gz")):
        cl[r["key"]][r["closure"]] = r
    sup = json.load(open(os.path.join(run, "support.json")))
    cv = json.load(open(os.path.join(run, "certificate-verification.json")))
    dr = json.load(open(os.path.join(run, "decision-rules.json")))
    cs = json.load(open(os.path.join(run, "cell-summary.json")))
    ic = json.load(open(os.path.join(run, "instrument-checks.json")))
    draws = {arm: jl(os.path.join(run, "draws-%s.jsonl.gz" % arm)) for arm in ("N-CONV", "N-CONVL", "N-CONV17", "N-ELL144")}

    out = {"inputs_sha256": {}}
    for p in [os.path.join(j7d, "rederivation.json"), os.path.join(j7d, "stream-replay.jsonl.gz"),
              os.path.join(j7d, "wcerts.jsonl.gz"), os.path.join(j1d, "verification.json"),
              os.path.join(rev, "blind-inputs-key.json"), os.path.join(rev, "blind/blind-inputs.json")] + \
             [os.path.join(run, f) for f in ("instances.jsonl.gz", "closures.jsonl.gz", "support.json",
                                              "certificate-verification.json", "certificates.jsonl.gz",
                                              "decision-rules.json", "cell-summary.json", "instrument-checks.json",
                                              "draws-N-CONV.jsonl.gz", "draws-N-CONVL.jsonl.gz",
                                              "draws-N-CONV17.jsonl.gz", "draws-N-ELL144.jsonl.gz")]:
        out["inputs_sha256"][os.path.relpath(p, S)] = sha_file(p)

    # ---------------------------------------------------- E_sha256 convention
    conv_ok = sum(esha(r["E_hex"]) == r["E_sha256"] for r in inst.values())
    canon_ok = sum(canon(r["E_hex"]) == r["E_hex"] for r in inst.values())
    out["E_sha256_convention"] = {
        "rule_tested": "sha256(json.dumps(E_hex).encode('utf-8')), Python default separators, E_hex rows canonical lowercase unpadded hex",
        "run_instances_matching": conv_ok, "run_instances_total": len(inst),
        "run_E_hex_rows_canonical": canon_ok,
    }

    # ================================================================ Q0
    q0 = {}
    c7 = d7["construction"]
    run_U = ints(sup["U_hex"])
    j7_U = ints(c7["U_rows_hex"])
    q0["construction"] = {
        "U_rows_decoded": item(run_U == j7_U, c7["U_rows_hex"], sup["U_hex"]),
        "U_sizes_per_equation": item(sup["sizes_per_eq"] == c7["U_sizes_per_equation"] == d7["Q0"]["U_S_L"]["U_sizes_per_equation"],
                                     c7["U_sizes_per_equation"], sup["sizes_per_eq"]),
        "S_L_positions_row_major": item([list(x) for x in sup["S_L"]] == [list(x) for x in c7["S_L_positions_row_major"]],
                                        None, None),
        "S_L_size": item(sup["S_L_size"] == c7["S_L_size"] == d7["Q0"]["U_S_L"]["S_L_size"], c7["S_L_size"], sup["S_L_size"]),
        "S_L_constant_positions": item(sup["S_L_constant_positions"] == c7["S_L_constant_positions"],
                                       c7["S_L_constant_positions"], sup["S_L_constant_positions"]),
        "coordinator_reading_true": item(sup["coordinator_reading_true"] == c7["coordinator_reading_of_U_k_holds"],
                                         c7["coordinator_reading_of_U_k_holds"], sup["coordinator_reading_true"]),
    }

    def stream_compare(arm, slots, j7slots):
        """Compare one arm's stream on the given slots. j7slots: dict str(slot)->record."""
        sr_arm = defaultdict(dict)
        for r in sr:
            if r["arm"] == arm:
                sr_arm[r["slot"]][r["attempt"]] = r
        rd = defaultdict(dict)
        for r in draws[arm]:
            rd[r["slot"]][r["attempt"]] = r
        per_slot = []
        att_tot = Counter()
        att_agree = Counter()
        for s in slots:
            js = j7slots[str(s)]
            J = sr_arm[s]
            Rr = rd[s]
            ku = inst["%s:%d:unsat" % (arm, s)]
            ks = inst["%s:%d:sat" % (arm, s)]
            rec = {"slot": s}
            rec["n_attempts"] = item(js["attempts"] == len(J) == len(Rr), [js["attempts"], len(J)], len(Rr))
            rec["unsat_attempt"] = item(js["unsat"]["attempt"] == ku["attempt"], js["unsat"]["attempt"], ku["attempt"])
            rec["sat_attempt"] = item(js["sat"]["attempt"] == ks["attempt"], js["sat"]["attempt"], ks["attempt"])
            rec["unsat_rows_decoded"] = item(ints(js["unsat"]["row_hex"]) == ints(ku["E_hex"]))
            rec["sat_rows_decoded"] = item(ints(js["sat"]["row_hex"]) == ints(ks["E_hex"]))
            rec["unsat_s"] = item(js["unsat"]["s"] == ku["s"] == 0, js["unsat"]["s"], ku["s"])
            rec["sat_s"] = item(js["sat"]["s"] == ks["s"], js["sat"]["s"], ks["s"])
            rec["sat_solutions"] = item(sorted(js["sat"].get("solutions", [])) == sorted(ks.get("solutions", [])),
                                        js["sat"].get("solutions"), ks.get("solutions"))
            rec["exhausted"] = item(js["exhausted"] == [] and ku["attempt"] is not None and ks["attempt"] is not None,
                                    js["exhausted"], None)
            rec["rejections"] = item(js["rejections"] == [] and not any(str(r["outcome"]).startswith("rej") for r in Rr.values()),
                                     js["rejections"], [r for r in Rr.values() if str(r["outcome"]).startswith("rej")])
            # every attempt
            dis = []
            for at in sorted(set(J) | set(Rr)):
                jr, rr = J.get(at), Rr.get(at)
                for fld in ("s", "outcome", "E_sha256_convention", "E_sha256_raw_j7_strings"):
                    att_tot[fld] += 1
                    if jr is None or rr is None:
                        dis.append({"attempt": at, "field": fld, "j7": jr is not None, "run": rr is not None})
                        continue
                    if fld == "s":
                        ok = jr["s"] == rr["s"]
                    elif fld == "outcome":
                        ok = jr["outcome"] == rr["outcome"]
                    elif fld == "E_sha256_convention":
                        ok = esha(canon(jr["row_hex"])) == rr["E_sha256"]
                    else:
                        ok = esha(jr["row_hex"]) == rr["E_sha256"]
                    if ok:
                        att_agree[fld] += 1
                    else:
                        dis.append({"attempt": at, "field": fld})
                # arm-specific drawn quantities
                if arm == "N-CONVL" and jr and rr:
                    att_tot["bprime"] += 1
                    if jr.get("b_prime") == rr.get("bprime"):
                        att_agree["bprime"] += 1
                    else:
                        dis.append({"attempt": at, "field": "bprime", "j7": jr.get("b_prime"), "run": rr.get("bprime")})
                if arm == "N-ELL144" and jr and rr:
                    att_tot["c"] += 1
                    if jr.get("c") == rr.get("c"):
                        att_agree["c"] += 1
                    else:
                        dis.append({"attempt": at, "field": "c", "j7": jr.get("c"), "run": rr.get("c")})
            rec["every_attempt"] = {"agree": not dis, "disagreements": dis}
            if arm == "N-CONVL":
                rec["unsat_bprime"] = item(ku.get("bprime") == J[js["unsat"]["attempt"]].get("b_prime"), J[js["unsat"]["attempt"]].get("b_prime"), ku.get("bprime"))
            if arm == "N-ELL144":
                rec["unsat_c"] = item(ku.get("c") == J[js["unsat"]["attempt"]].get("c"), J[js["unsat"]["attempt"]].get("c"), ku.get("c"))
            per_slot.append(rec)
        items = [k for k in per_slot[0] if k != "slot"]
        summ = {k: {"agree": sum(r[k]["agree"] for r in per_slot), "of": len(per_slot)} for k in items}
        summ["attempt_fields"] = {k: {"agree": att_agree[k], "of": att_tot[k]} for k in att_tot}
        return per_slot, summ

    per_slot, summ = stream_compare("N-CONV", range(144), d7["Q0"]["slots"])
    tot = d7["Q0"]["totals"]
    rcount = Counter(r["outcome"] for r in draws["N-CONV"])
    summ["totals"] = item(tot["attempts"] == len(draws["N-CONV"]) and tot["kept_unsat"] == rcount["kept_unsat"]
                          and tot["kept_sat"] == rcount["kept_sat"] and tot["discarded"] == rcount["discarded"]
                          and tot["rejections"] == 0 and not tot["exhausted"],
                          tot, dict(rcount, attempts=len(draws["N-CONV"])))
    summ["seed"] = item(d7["Q0"]["seed"] == 2026092450101, d7["Q0"]["seed"], 2026092450101)
    q0["N-CONV"] = {"summary": summ, "per_slot": per_slot}
    q0opt = {}
    seeds = {"N-CONVL": 2026092450102, "N-CONV17": 2026092450103, "N-ELL144": 2026092450104}
    for arm in ("N-CONVL", "N-CONV17", "N-ELL144"):
        ps, sm = stream_compare(arm, range(10), d7["Q0_opt"][arm]["slots"])
        sm["seed"] = item(d7["Q0_opt"][arm]["seed"] == seeds[arm], d7["Q0_opt"][arm]["seed"], seeds[arm])
        q0opt[arm] = {"summary": sm, "per_slot": ps}
    q0["Q0_opt"] = q0opt
    out["Q0"] = q0

    # ================================================================ Q1
    def m4_compare(j, r, s_run):
        return {
            "rank": item(j["rank_4"] == r["rank"], j["rank_4"], r["rank"]),
            "one_in_rowspace_M4": item(j["one_in_R_4"] == r["one"], j["one_in_R_4"], r["one"]),
            "dims_by_deg_0_3": item(j["dims_by_deg_M4"] == r["dims_by_deg"][:4], j["dims_by_deg_M4"], r["dims_by_deg"][:4]),
            "P": item(j["P"] == r["P"], j["P"], r["P"]),
            "s": item(j["s"] == s_run, j["s"], s_run),
        }

    q1 = {"unsat": [], "sat_optional": []}
    for role, bucket in (("unsat", "unsat"), ("sat", "sat_optional")):
        for s in range(144):
            j = d7["Q1"][bucket]["NCONV-REPLAY:%d:%s" % (s, role)]
            rk = "N-CONV:%d:%s" % (s, role)
            rec = {"slot": s, "run_key": rk}
            rec.update(m4_compare(j, cl[rk]["M_4"], inst[rk]["s"]))
            q1[bucket].append(rec)
    q1sum = {}
    for bucket in q1:
        ks = [k for k in q1[bucket][0] if k not in ("slot", "run_key")]
        q1sum[bucket] = {k: {"agree": sum(r[k]["agree"] for r in q1[bucket]), "of": len(q1[bucket])} for k in ks}
    out["Q1"] = {"summary": q1sum, "per_system": q1}

    # ============================================================ Q2-Q5
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import wdag_check as WC  # own decoder (E_layout), written before any reviewer code was read
    blind = json.load(open(os.path.join(rev, "blind/blind-inputs.json")))
    beqs = {x["label"]: x["equations"] for x in blind["systems"]}
    pool = []
    for lab in sorted(keymap):
        km = keymap[lab]
        rk = km["key"]
        R = cl[rk]
        rec = {"label": lab, "run_key": rk, "arm": km["arm"], "role": km["role"], "slot": km["slot"], "group": km["group"]}
        q2, q3, q5 = d7["Q2"][lab], d7["Q3"][lab], d7["Q5"][lab]
        # key mapping check: the pool system's explicit equations equal the run's rows of the mapped key
        rec["map.pool_equations_equal_run_E_hex"] = item(WC.system_to_colbits(WC.system_from_monomial_lists(beqs[lab])) == ints(inst[rk]["E_hex"]))
        rec["map.arm_role_slot_from_key_equal_run_record"] = item(inst[rk]["arm"] == km["arm"] and inst[rk]["role"] == km["role"] and inst[rk]["slot"] == km["slot"],
                                                                  km, {k: inst[rk][k] for k in ("arm", "role", "slot")})
        # Q2
        rec["Q2.s"] = item(q2["s"] == inst[rk]["s"], q2["s"], inst[rk]["s"])
        if "M_3" in R:
            rec["Q2.rank_3"] = item(q2["rank_3"] == R["M_3"]["rank"], q2["rank_3"], R["M_3"]["rank"])
            rec["Q2.one_in_R_3"] = item(q2["one_in_R_3"] == R["M_3"]["one"], q2["one_in_R_3"], R["M_3"]["one"])
        else:
            rec["Q2.rank_3"] = {"agree": None, "gap": "run computes M_3 only on archived arms (object.closures_run); no run record", "j7": q2["rank_3"]}
            rec["Q2.one_in_R_3"] = {"agree": None, "gap": "run computes M_3 only on archived arms; no run record", "j7": q2["one_in_R_3"]}
        rec["Q2.rank_4"] = item(q2["rank_4"] == R["M_4"]["rank"], q2["rank_4"], R["M_4"]["rank"])
        rec["Q2.one_in_R_4"] = item(q2["one_in_R_4"] == R["M_4"]["one"], q2["one_in_R_4"], R["M_4"]["one"])
        rec["Q2.dims_by_deg_M4_0_3"] = item(q2["dims_by_deg_M4"] == R["M_4"]["dims_by_deg"][:4], q2["dims_by_deg_M4"], R["M_4"]["dims_by_deg"][:4])
        rec["Q2.P"] = item(q2["P"] == R["M_4"]["P"], q2["P"], R["M_4"]["P"])
        # Q3
        W = R["W_4"]
        jd, rd_ = q3["dims"], W["dims"]
        enc_ok = (len(jd) == len(rd_) + 1 and jd[:-1] == rd_ and jd[-1] == jd[-2])
        rec["Q3.dims_per_iteration"] = item(enc_ok, jd, rd_, note="encoding: run omits the repeated terminal W^(fixpoint+1)")
        rec["Q3.fixpoint_index"] = item(q3["fixpoint_index"] == W["iterations_to_fixpoint"], q3["fixpoint_index"], W["iterations_to_fixpoint"])
        rec["Q3.one_first_iteration"] = item(q3["one_first_iteration"] == W["one_first_iteration"], q3["one_first_iteration"], W["one_first_iteration"])
        rec["Q3.one"] = item(q3["one"] == W["one"], q3["one"], W["one"])
        rec["Q3.final_dim"] = item(q3["final_dim"] == W["final_dim"], q3["final_dim"], W["final_dim"])
        rec["Q3.dims_by_deg_W4"] = item(q3["dims_by_deg"] == W["dims_by_deg"], q3["dims_by_deg"], W["dims_by_deg"])
        cum = []
        acc = 0
        for x in W["new_fallen_per_iteration"]:
            acc += x
            cum.append(acc)
        rec["Q3.fallen_per_iteration"] = item(cum == q3["fallen_basis_size_per_iteration"], q3["fallen_basis_size_per_iteration"],
                                              W["new_fallen_per_iteration"], note="encoding: run increments vs J7 cumulative sizes (extra item)")
        # Q4 (presence only here; validity from CP-3)
        rec["Q4.witness_present_iff_one_in_W4"] = item((d7["Q4"][lab].get("one_in_W4") is True) == W["one"]
                                                       and ((d7["Q4"][lab].get("certificate") == "in wcerts.jsonl.gz") == bool(W["one"])),
                                                       d7["Q4"][lab], W["one"])
        # Q5
        rb = R["rc_b"]
        rec["Q5.kernel_dim"] = item(q5["kernel_dim"] == rb["kernel_dim"], q5["kernel_dim"], rb["kernel_dim"])
        rec["Q5.label"] = item(q5["label"] == rb["label"], q5["label"], rb["label"])
        if rb["kernel_dim"] == 1 and q5["kernel_dim"] == 1:
            cint = sum(b << k for k, b in enumerate(q5["c"]))
            rec["Q5.c"] = item(cint == rb["c"], q5["c"], rb["c"], note="encoding: run int bit k = c_k")
            rec["Q5.ell_linear_support"] = item(q5["ell_linear_support"] == rb["ell_linear_support"], q5["ell_linear_support"], rb["ell_linear_support"])
            rec["Q5.ell_constant"] = item(q5["ell_constant"] == rb["ell_const"], q5["ell_constant"], rb["ell_const"])
            if rb.get("substituted"):
                rec["Q5.j_star"] = item(q5["j_star"] == rb["j_star"], q5["j_star"], rb["j_star"])
                rec["Q5.rank_R3"] = item(q5["rank_R3"] == R["R'_3"]["rank"], q5["rank_R3"], R["R'_3"]["rank"])
                rec["Q5.rank_R4"] = item(q5["rank_R4"] == R["R'_4"]["rank"], q5["rank_R4"], R["R'_4"]["rank"])
                rec["Q5.one_R4"] = item(q5["one_in_R4"] == R["R'_4"]["one"], q5["one_in_R4"], R["R'_4"]["one"])
                rec["Q5.dims_by_deg_R4"] = item(q5["dims_by_deg_R4"] == R["R'_4"]["dims_by_deg"], q5["dims_by_deg_R4"], R["R'_4"]["dims_by_deg"])
                rec["Q5.T5_applicable(extra)"] = item(q5["T5_applicable"] == rb["T5_applicable"], q5["T5_applicable"], rb["T5_applicable"])
                rec["Q5.one_R3(extra)"] = item(q5["one_in_R3"] == R["R'_3"]["one"], q5["one_in_R3"], R["R'_3"]["one"])
        pool.append(rec)
    items = sorted({k for r in pool for k in r if "." in k})
    psum = {}
    for k in items:
        vals = [r[k]["agree"] for r in pool if k in r]
        psum[k] = {"agree": sum(v is True for v in vals), "disagree": sum(v is False for v in vals),
                   "no_counterpart": sum(v is None for v in vals), "systems_with_item": len(vals)}
    out["Q2_Q5_pool"] = {"summary": psum, "per_system": pool}

    # ============================================== J1 vs run, per line
    j1lines = {pl["cid"]: pl for pl in v1["certificates_VC3"]["per_line"]}
    runlines = {c["cid"]: c for c in cv["certificates"]}
    cmp_lines = []
    fields_tot = Counter()
    fields_agree = Counter()
    for cid in sorted(set(j1lines) | set(runlines)):
        J, Rn = j1lines.get(cid), runlines.get(cid)
        rec = {"cid": cid}
        if J is None or Rn is None:
            rec["missing"] = "j1" if J is None else "run"
            cmp_lines.append(rec)
            continue
        pairs = {
            "key": (J["key"], Rn["key"]),
            "closure": (J["closure"], Rn["closure"]),
            "format": (J["format"], Rn["format"]),
            "arm": (J["arm"], Rn["arm"]),
            "verified": (J["verified"], Rn["verified"]),
            "size": (J["size"], Rn["size"]),
            "max_mu": (J["max_mu"], Rn["max_mu"]),
            "counts_M4": (J["counts_toward_M4"], Rn.get("counts_for_M4", False)),
            "counts_W4": (J["counts_toward_w"], Rn.get("counts_for_W4", False)),
        }
        if J["format"] == "wdag-v1":
            pairs["node_count"] = (J["node_count"], Rn["node_count"])
            pairs["max_child_degree"] = (J["max_child_degree"], Rn["max_child_degree"])
        bad = {}
        for f, (x, y) in pairs.items():
            fields_tot[f] += 1
            if x == y:
                fields_agree[f] += 1
            else:
                bad[f] = {"j1": x, "run": y}
        if bad:
            rec["disagree"] = bad
            cmp_lines.append(rec)
    out["J1_vs_run_certificate_verification"] = {
        "lines_j1": len(j1lines), "lines_run": len(runlines),
        "fields": {f: {"agree": fields_agree[f], "of": fields_tot[f]} for f in fields_tot},
        "lines_with_any_disagreement": cmp_lines,
        "note": "run counts_for_M4 absent on W_4 lines and on wdag lines is read as false; run counts_for_W4 absent on flat lines read as false",
    }

    # ================================== MN recount from J1 verdicts only
    arms_unsat = {}
    arms_sat = {}
    for k, r in inst.items():
        (arms_unsat if r["role"] == "unsat" else arms_sat).setdefault(r["arm"], []).append(k)
    j1_wdag = set()
    j1_m4 = set()
    for pl in j1lines.values():
        if pl["verified"] and pl["format"] == "wdag-v1" and pl["closure"] == "W_4":
            j1_wdag.add(pl["key"])
        if pl["verified"] and pl["format"] == "flat-v1" and pl["closure"] == "M_4" and pl["max_mu"] <= 2:
            j1_m4.add(pl["key"])
    # engine-reported refutations (for UNCERTIFIED and C-PS)
    eng_w = {k for k, c in cl.items() if c.get("W_4", {}).get("one")}
    eng_m = {k for k, c in cl.items() if c.get("M_4", {}).get("one")}
    # EXHAUSTED: none iff every N-CONV slot has a kept unsat system in the run and in J7
    exhausted = [s for s in range(144) if "N-CONV:%d:unsat" % s not in inst]
    nC = 144 - len(exhausted)
    w_L1 = sum(1 for s in range(144) if "N-CONV:%d:unsat" % s in j1_wdag)
    uncert = sorted(k for k in eng_w if k.startswith("N-CONV:") and k.endswith(":unsat") and k not in j1_wdag)
    w_L2, nC_L2 = w_L1, nC - len(uncert)

    def label(w, n):
        if n < 120:
            return "NOT EVALUABLE (sample)"
        if w >= math.ceil(0.9 * n):
            return "TENSOR"
        if w <= math.floor(0.1 * n):
            return "LINEAR"
        return "MIXED"

    ci = {}

    def CI(x, n):
        if (x, n) not in ci:
            ci[(x, n)] = cp95(x, n)
        return ci[(x, n)]

    mn = {}
    lo, hi = CI(w_L1, nC)
    mn["MN1"] = {"w_L1": w_L1, "n_C_L1": nC, "w_L2": w_L2, "n_C_L2": nC_L2, "uncertified": uncert, "exhausted_slots": exhausted,
                 "cp95_L1": [r6(lo), r6(hi)],
                 "run": {"L1": dr["NC-DR-1"]["L1_uncertified_as_not_refuted"], "L2": dr["NC-DR-1"]["L2_uncertified_excluded"]}}
    mn["MN1"]["agree"] = (w_L1 == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["w"] and nC == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["n_C"]
                          and [r6(lo), r6(hi)] == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["cp95"]
                          and w_L2 == dr["NC-DR-1"]["L2_uncertified_excluded"]["w"] and nC_L2 == dr["NC-DR-1"]["L2_uncertified_excluded"]["n_C"])
    mn2 = {}
    for arm in ("N-CONV", "N-CONVL", "N-CONV17", "N-ELL144", "S3-U62", "S3-C20", "NULL-AFF62", "NULL-F262", "NELL-A20"):
        ks = arms_unsat[arm]
        x = sum(k in j1_wdag for k in ks)
        m4x = sum(k in j1_m4 for k in ks)
        lo, hi = CI(x, len(ks))
        mlo, mhi = CI(m4x, len(ks))
        mn2[arm] = {"W4_x": x, "n": len(ks), "W4_cp95": [r6(lo), r6(hi)], "M4_x": m4x, "M4_cp95": [r6(mlo), r6(mhi)],
                    "engine_W4_refuted": sum(k in eng_w for k in ks), "engine_M4_refuted": sum(k in eng_m for k in ks)}
    s3 = arms_unsat["S3-U62"] + arms_unsat["S3-C20"]
    x = sum(k in j1_wdag for k in s3)
    lo, hi = CI(x, len(s3))
    m4x = sum(k in j1_m4 for k in s3)
    mlo, mhi = CI(m4x, len(s3))
    mn2["S_3 (82)"] = {"W4_x": x, "n": len(s3), "W4_cp95": [r6(lo), r6(hi)], "M4_x": m4x, "M4_cp95": [r6(mlo), r6(mhi)]}
    # compare with run NC-DR-3 intervals and NC-DR-6 M_4 intervals
    ivr = dr["NC-DR-3"]["intervals"]
    m6 = dr["NC-DR-6"]["per_arm_M4"]
    mn2_cmp = {}
    for arm, v in mn2.items():
        c = {}
        if arm in ivr:
            c["W4"] = item(v["W4_x"] == ivr[arm]["x"] and v["n"] == ivr[arm]["n"] and v["W4_cp95"] == ivr[arm]["cp95"],
                           [v["W4_x"], v["n"], v["W4_cp95"]], [ivr[arm]["x"], ivr[arm]["n"], ivr[arm]["cp95"]])
        if arm in m6:
            c["M4"] = item(v["M4_x"] == m6[arm]["x"] and v["n"] == m6[arm]["n"] and v["M4_cp95"] == m6[arm]["cp95"],
                           [v["M4_x"], v["n"], v["M4_cp95"]], [m6[arm]["x"], m6[arm]["n"], m6[arm]["cp95"]])
        mn2_cmp[arm] = c
    mn["MN2"] = {"per_arm": mn2, "vs_run": mn2_cmp}
    # MN3: C-PS from J1 (no certificate line on a satisfiable system; J1 s) and engine flags; per-kind table
    kinds = defaultdict(Counter)
    for pl in j1lines.values():
        k = "%s|%s|%s" % (pl["closure"], pl["arm"], pl["format"])
        kinds[k]["submitted"] += 1
        kinds[k]["verified" if pl["verified"] else "failed"] += 1
    runkinds = cv["summary"]
    kcmp = {k: item(kinds[k]["submitted"] == runkinds.get(k, {}).get("submitted") and kinds[k]["verified"] == runkinds.get(k, {}).get("verified")
                    and kinds[k].get("failed", 0) == runkinds.get(k, {}).get("failed"), dict(kinds[k]), runkinds.get(k))
            for k in sorted(set(kinds) | set(runkinds))}
    sat_cert_lines = [pl["cid"] for pl in j1lines.values() if pl.get("verified_on_satisfiable_system") or pl.get("system_s_mine", 0) != 0]
    sat_keys = [k for k, r in inst.items() if r["role"] == "sat"]
    cps_eng = [k for k in sat_keys if k in eng_w or k in eng_m]
    codim_viol = []
    for k in sat_keys:
        s = inst[k]["s"]
        if s <= 31:
            codim = 4048 - cl[k]["W_4"]["final_dim"]
            if codim < s:
                codim_viol.append(k)
    cps_arm = defaultdict(lambda: {"sat_controls": 0, "M4_refuted": 0, "W4_refuted": 0, "codim_eq_s": 0, "codim_checked": 0})
    for k in sat_keys:
        arm = inst[k]["arm"]
        cps_arm[arm]["sat_controls"] += 1
        cps_arm[arm]["M4_refuted"] += k in eng_m
        cps_arm[arm]["W4_refuted"] += k in eng_w
        if inst[k]["s"] <= 31:
            cps_arm[arm]["codim_checked"] += 1
            cps_arm[arm]["codim_eq_s"] += (4048 - cl[k]["W_4"]["final_dim"]) == inst[k]["s"]
    j1_s_ok = v1["satisfiability_VC5"]["pass"] and not v1["satisfiability_VC5"]["failures"]
    mn["MN3"] = {
        "per_kind_J1_vs_run": kcmp,
        "uncertified_per_arm_from_J1": {arm: sorted(k for k in arms_unsat[arm] if k in eng_w and k not in j1_wdag) for arm in arms_unsat},
        "C-PS": {"certificate_lines_on_satisfiable_or_s_ge_1_per_J1": sat_cert_lines,
                 "engine_refutations_of_satisfiable_controls": cps_eng,
                 "codim_lt_s_violations": codim_viol, "per_arm": dict(cps_arm),
                 "J1_s_all_equal_record": j1_s_ok,
                 "run_C-PS": ic["checks"]["C-PS"]},
    }
    # ---- against cell-summary.json (MN1, MN2, MN3 as the run states them)
    c1 = cs["MN1_w4_refuted_NCONV"]
    mn["MN1"]["vs_cell_summary"] = item(c1["w"] == w_L1 and c1["n_C"] == nC and c1["cp95"] == mn["MN1"]["cp95_L1"] and c1["uncertified"] == len(uncert),
                                        {"w": w_L1, "n_C": nC, "cp95": mn["MN1"]["cp95_L1"], "uncertified": len(uncert)}, c1)
    c2 = cs["MN2_w4_refuted_by_arm"]
    mn["MN2"]["vs_cell_summary"] = {arm: item(c2[arm]["x"] == mn2[arm]["W4_x"] and c2[arm]["n"] == mn2[arm]["n"] and c2[arm]["cp95"] == mn2[arm]["W4_cp95"],
                                              [mn2[arm]["W4_x"], mn2[arm]["n"], mn2[arm]["W4_cp95"]], c2[arm]) for arm in c2}
    c3 = cs["MN3_soundness_and_certificates"]
    mn["MN3"]["cell_summary_certificates_vs_J1"] = {k: item(
        (c3["certificates"].get(k, {}).get("submitted"), c3["certificates"].get(k, {}).get("verified"), c3["certificates"].get(k, {}).get("failed"))
        == (kinds[k]["submitted"], kinds[k]["verified"], kinds[k].get("failed", 0)), dict(kinds[k]), c3["certificates"].get(k))
        for k in sorted(set(kinds) | set(c3["certificates"]))}
    mn["MN3"]["cell_summary_uncertified_vs_J1"] = item(not c3["uncertified"] and not uncert, uncert, c3["uncertified"])
    j1_sat_cert = defaultdict(int)
    for pl in j1lines.values():
        if pl["verified"] and inst[pl["key"]]["role"] == "sat":
            j1_sat_cert[inst[pl["key"]]["arm"]] += 1
    scmp = {}
    for arm, v in c3["satisfiable_controls"].items():
        mine = cps_arm[arm]
        ks = arms_sat[arm]
        s31 = [k for k in ks if inst[k]["s"] <= 31]
        cge = sum((4048 - cl[k]["W_4"]["final_dim"]) >= inst[k]["s"] for k in s31)
        scmp[arm] = item(v["n"] == mine["sat_controls"] and v["M4_refuted_engine"] == mine["M4_refuted"] and v["W4_refuted_engine"] == mine["W4_refuted"]
                         and v["certificates_verified"] == j1_sat_cert[arm] and v["s_le_31"] == len(s31) and v["codim_ge_s"] == cge
                         and v["codim_eq_s"] == mine["codim_eq_s"],
                         dict(mine, certificates_verified_J1=j1_sat_cert[arm], s_le_31=len(s31), codim_ge_s=cge), v)
    mn["MN3"]["cell_summary_satisfiable_controls_vs_recount"] = scmp
    # reading invariance of the counting rule over ALL systems, from J1's verdicts only:
    # R-CF: verified flat-v1 with max|mu| <= 2 is eligible for M_4 and W_4 (any closure label); valid wdag-v1 for W_4.
    # R-MN: M_4 = verified M_4-labelled flat-v1 with max|mu| <= 2; w = verified W_4 wdag-v1.
    cf_m4, cf_w4 = set(), set()
    for pl in j1lines.values():
        if pl["verified"] and pl["format"] == "flat-v1" and pl["max_mu"] <= 2:
            cf_m4.add(pl["key"])
            cf_w4.add(pl["key"])
        if pl["verified"] and pl["format"] == "wdag-v1":
            cf_w4.add(pl["key"])
    inv = {}
    for arm in sorted(set(arms_unsat) | set(arms_sat)):
        ks = arms_unsat.get(arm, []) + arms_sat.get(arm, [])
        inv[arm] = {"M4_R-CF": sum(k in cf_m4 for k in ks), "M4_R-MN": sum(k in j1_m4 for k in ks),
                    "W4_R-CF": sum(k in cf_w4 for k in ks), "W4_R-MN": sum(k in j1_wdag for k in ks)}
        inv[arm]["same"] = inv[arm]["M4_R-CF"] == inv[arm]["M4_R-MN"] and inv[arm]["W4_R-CF"] == inv[arm]["W4_R-MN"]
    mn["counting_reading_invariance_all_systems"] = {
        "per_arm": inv, "all_same": all(v["same"] for v in inv.values()),
        "system_sets_equal": {"M4": cf_m4 == j1_m4, "W4": cf_w4 == j1_wdag},
        "note": "R-CF = object.certificate_format sentences read as eligibility (the run verifier's per-line counts_for_* flags); R-MN = MN1 and the M_4 secondary metric (the run's analysis.py and J1). Computed from J1's per-line verdicts."}
    out["MN_recount_from_J1"] = mn

    # ================================ NC-DR-1..4 re-applied (frozen text)
    rer = {}
    l1 = label(w_L1, nC)
    l2 = label(w_L2, nC_L2)
    verdict1 = l1 if l1 == l2 else "UNDETERMINED (certification)"
    rer["NC-DR-1"] = {"L1": l1, "L2": l2, "verdict": verdict1,
                      "E_TENSOR_falsified": w_L1 <= nC // 2, "E_LINEAR_falsified": w_L1 > nC // 2,
                      "thresholds": {"tensor": math.ceil(0.9 * nC), "linear": math.floor(0.1 * nC), "half": nC // 2}}
    rer["NC-DR-1"]["agree_with_run"] = (verdict1 == dr["NC-DR-1"]["verdict"] and l1 == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["label"]
                                        and l2 == dr["NC-DR-1"]["L2_uncertified_excluded"]["label"]
                                        and rer["NC-DR-1"]["E_TENSOR_falsified"] == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["E_TENSOR_falsified"]
                                        and rer["NC-DR-1"]["E_LINEAR_falsified"] == dr["NC-DR-1"]["L1_uncertified_as_not_refuted"]["E_LINEAR_falsified"]
                                        and rer["NC-DR-1"]["thresholds"] == dr["NC-DR-1"]["thresholds_at_n_C"])
    nlo, nhi = CI(w_L1, nC)
    s386 = CI(386, 386)
    s82 = CI(mn2["S_3 (82)"]["W4_x"], 82)
    ov = lambda A, B: not (A[1] < B[0] or B[1] < A[0])
    lab2 = "AT S_3's RATE" if ov((nlo, nhi), s386) else "BELOW S_3"
    lab2b = "AT S_3's RATE" if ov((nlo, nhi), s82) else "BELOW S_3"
    rer["NC-DR-2"] = {"N-CONV_cp95": [r6(nlo), r6(nhi)], "S3_386_cp95": [r6(s386[0]), r6(s386[1])], "label": lab2,
                      "in_run_S3_82_cp95": [r6(s82[0]), r6(s82[1])], "in_run_label": lab2b}
    rer["NC-DR-2"]["agree_with_run"] = (lab2 == dr["NC-DR-2"]["label"] and lab2b == dr["NC-DR-2"]["in_run_S3_82"]["label"]
                                        and rer["NC-DR-2"]["S3_386_cp95"] == dr["NC-DR-2"]["S3_386_cp95"]
                                        and rer["NC-DR-2"]["in_run_S3_82_cp95"] == dr["NC-DR-2"]["in_run_S3_82"]["cp95"])
    order = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144", "NULL-F262", "NULL-AFF62", "S_3 (82)"]
    ivs = {a: CI(mn2[a]["W4_x"], mn2[a]["n"]) for a in order}
    nm = lambda a: a + " [one affine draw]" if a == "NULL-AFF62" else a
    pairs = {}
    for X in order:
        for Y in order:
            if X == Y:
                continue
            pairs["%s vs %s" % (nm(X), nm(Y))] = ("%s ABOVE %s" % (nm(X), nm(Y))) if ivs[X][0] > ivs[Y][1] else "NOT DISTINGUISHED"
    pd = {k: item(v == dr["NC-DR-3"]["pairs"].get(k), v, dr["NC-DR-3"]["pairs"].get(k)) for k, v in pairs.items()}
    rer["NC-DR-3"] = {"pairs_agree": sum(v["agree"] for v in pd.values()), "pairs": len(pd),
                      "run_pairs": len(dr["NC-DR-3"]["pairs"]),
                      "disagreements": {k: v for k, v in pd.items() if not v["agree"]}}
    above = lambda X, Y: ivs[X][0] > ivs[Y][1]
    lvl = lambda arm: {"TENSOR": "TENSOR-level", "LINEAR": "LINEAR-level"}.get(label(mn2[arm]["W4_x"], mn2[arm]["n"]), "otherwise")
    if verdict1 == "TENSOR" and above("N-CONV", "N-ELL144") and above("N-CONV", "NULL-F262"):
        v4, sub = "CONVOLUTION TENSOR", None
    elif verdict1 == "LINEAR":
        v4 = "LOWER-DEGREE PART REQUIRED"
        sub = {"TENSOR-level": "SEMAEV LINEAR PART SUFFICES (curve constant not required)",
               "LINEAR-level": "CURVE CONSTANT REQUIRED (with the confound that the drawn curves' targets are not x(2E))"}.get(lvl("N-CONVL"), "MIXED")
    else:
        v4, sub = "MIXED", None
    l17 = lvl("N-CONV17")
    if l17 == "TENSOR-level":
        app = "CONVOLUTION FORMS SUFFICE WITHOUT THE COKERNEL FALL"
    elif l17 == "LINEAR-level" and v4 == "CONVOLUTION TENSOR":
        app = "THE RANK-16 COKERNEL IS NEEDED"
    else:
        app = "descriptive"
    rer["NC-DR-4"] = {"verdict": v4, "sub_label": sub, "appended_N-CONV17_reading": app,
                      "N-CONVL_level": lvl("N-CONVL"), "N-CONV17_level": l17}
    rer["NC-DR-4"]["agree_with_run"] = (v4 == dr["NC-DR-4"]["verdict"] and sub == dr["NC-DR-4"]["sub_label"]
                                        and app == dr["NC-DR-4"]["appended_N-CONV17_reading"]
                                        and lvl("N-CONVL") == dr["NC-DR-4"]["N-CONVL_level"] and l17 == dr["NC-DR-4"]["N-CONV17_level"])
    rer["any_verdict_changes"] = not all(rer[k]["agree_with_run"] for k in ("NC-DR-1", "NC-DR-2", "NC-DR-4")) or bool(rer["NC-DR-3"]["disagreements"])
    out["NC-DR_reapplied_from_J1"] = rer

    # =============================== J1 VC-2 kept-part vs C-CONSTRUCT etc.
    us = v1["union_support"]
    vc2 = v1["construction_VC2"]
    out["J1_VC2_vs_run_controls"] = {
        "C-CONSTRUCT_vs_J1_descent": item(ic["checks"]["C-CONSTRUCT"]["pass"] and v1["descent"]["pass"]
                                          and ic["checks"]["C-CONSTRUCT"]["detail"]["checked"] == 144,
                                          v1["descent"], ic["checks"]["C-CONSTRUCT"]),
        "C-SUPPORT_sizes": item(us["U_sizes_per_eq"] == sup["sizes_per_eq"], us["U_sizes_per_eq"], sup["sizes_per_eq"]),
        "C-SUPPORT_S_L_size_and_constants": item(us["S_L_size"] == sup["S_L_size"] and us["S_L_const_positions"] == sup["S_L_constant_positions"],
                                                 [us["S_L_size"], us["S_L_const_positions"]], [sup["S_L_size"], sup["S_L_constant_positions"]]),
        "C-SUPPORT_coordinator_reading": item(us["coordinator_reading_true"] == sup["coordinator_reading_true"] == ic["checks"]["C-SUPPORT"]["detail"]["coordinator_reading_true"],
                                              us["coordinator_reading_true"], sup["coordinator_reading_true"]),
        "C-SUPPORT_null_f262_inside_U": item(ic["checks"]["C-SUPPORT"]["detail"]["null_f262_inside_U"] and vc2["per_arm"]["NULL-F262"]["systems_with_violation"] == 0,
                                             vc2["per_arm"]["NULL-F262"], ic["checks"]["C-SUPPORT"]["detail"]),
        "kept_part_all_arms": item(vc2["pass"] and not vc2["violations"], vc2["per_arm"], None),
        "C-ELL": {"agree": None, "note": "J1 did not compute the left kernel / ell (not in its VC-2 list); C-ELL has no J1 counterpart. J7 Q5 c/ell compared per pool system in Q2_Q5_pool; the run's C-ELL record: %s" % json.dumps(ic["checks"]["C-ELL"]["detail"])},
    }

    json.dump(out, open(a.out, "w"), indent=1, sort_keys=False)
    # console digest
    print("E_sha256 convention:", out["E_sha256_convention"])
    print("Q0 construction:", {k: v["agree"] for k, v in q0["construction"].items()})
    print("Q0 N-CONV:", json.dumps(q0["N-CONV"]["summary"]))
    for arm in q0opt:
        print("Q0-opt", arm, json.dumps(q0opt[arm]["summary"]))
    print("Q1:", json.dumps(q1sum))
    print("Q2-Q5:", json.dumps(psum, indent=0))
    print("J1 vs run lines:", json.dumps(out["J1_vs_run_certificate_verification"]["fields"]), len(cmp_lines))
    print("MN1:", json.dumps({k: v for k, v in mn["MN1"].items() if k != "run"}))
    print("MN2 vs run:", json.dumps({a: {k: x["agree"] for k, x in c.items()} for a, c in mn2_cmp.items()}))
    print("MN3 kinds:", sum(v["agree"] for v in kcmp.values()), "/", len(kcmp), "C-PS:", len(cps_eng), len(codim_viol), len(sat_cert_lines))
    print("NC-DR:", json.dumps({k: (v.get("agree_with_run") if isinstance(v, dict) else v) for k, v in rer.items()}), rer["NC-DR-3"]["pairs_agree"], "/", rer["NC-DR-3"]["pairs"])
    print("VC2 vs controls:", {k: v["agree"] for k, v in out["J1_VC2_vs_run_controls"].items()})


if __name__ == "__main__":
    main()
