"""J1 author-independent verification for REVIEW-CERTBIN-20260926-089841
(TASK-20260926-f0e5a4). Verifies every certificate line of
RUN-CERTBIN-6ebb0e certificates.jsonl.gz against systems decoded by own code,
checks every system's kept part against own construction, re-decides s,
builds own negative controls. Writes verification.json
(schema certbin.nconv.independent_verification.v1).

Imports: Python stdlib, numpy (container and vector ops), and the sibling
modules of this directory only. Nothing from this repository.

Invocation used (inputs extracted read-only with `git show c7f5e3dfa:<path>`
into <root>, same relative paths):
  cd code && PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
    bash -c 'ulimit -v 3145728; python3 run_j1.py --root <root> \
      --commit c7f5e3dfa76be62a43f5f689c11bf55eba9bfa0c --out ../verification.json'
"""
import argparse
import collections
import datetime
import gzip
import hashlib
import json
import os
import platform
import random
import resource
import sys
import time

import numpy as np

import bring
import certcheck as CC
import curve as CV
import descent as DS
import evaluator as EV
import gf2_17 as F
import layout as LY
import truthcheck as TT

SCHEMA = "certbin.nconv.independent_verification.v1"
SEED_SELFTEST = 20260926100001
SEED_NEGCTL = 20260926100002
N_NEG_PER_TYPE = 5

RUN = "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
P_CERTS = RUN + "/certificates.jsonl.gz"
P_INST = RUN + "/instances.jsonl.gz"
P_ISETS = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"
P_CURVE = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json"
P_RECEIPT = "coordination/design/certbin-nconv-20260924/archives/TASK-20260924-40b2ca/snapshot-receipt.json"
P_SPECS = ["experiments/EXP-CERTBIN-ddfe75/specification.yaml",
           "experiments/EXP-CERTBIN-e94b27/specification.yaml",
           "experiments/EXP-CERTBIN-4e92d7/specification.yaml",
           "knowledge/techniques/KN-TECH-b18366.md"]

FRESH_ARMS = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]
S3_ARMS = {"S3-U62": "U62", "S3-S62": "S62", "S3-C20": "C20"}
NULL_ARMS = {"NULL-F262": "N-F262", "NULL-AFF62": "N-AFF62"}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def log(msg):
    print("[%s] %s" % (utcnow(), msg), flush=True)


def row_subset(row, allowed):
    return (row & ~allowed) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="root holding the archived input paths")
    ap.add_argument("--commit", required=True, help="commit the root was extracted from (recorded)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    t_start = time.time()
    started = utcnow()
    R = lambda p: os.path.join(args.root, p)

    out = collections.OrderedDict()
    out["schema"] = SCHEMA
    out["task_id"] = "TASK-20260926-f0e5a4"
    out["review_plan_id"] = "REVIEW-CERTBIN-20260926-089841"
    out["joint"] = "J1"
    out["run_id"] = "RUN-CERTBIN-6ebb0e"
    out["experiment_id"] = "EXP-CERTBIN-ddfe75"
    ambiguities = []

    # ------------------------------------------------------------ inputs
    log("hashing inputs")
    receipt = json.load(open(R(P_RECEIPT)))
    rh = receipt["path_sha256"]
    inputs = []
    for p in [P_CERTS, P_INST, P_ISETS, P_CURVE, P_RECEIPT] + P_SPECS:
        h = sha256_file(R(p))
        inputs.append({"path": p, "sha256": h, "receipt_sha256": rh.get(p),
                       "receipt_match": (rh.get(p) == h) if p in rh else None})
    out["inputs"] = {"extracted_from_commit": args.commit,
                     "method": "git show <commit>:<path> into a scratch root (read-only; no worktree created)",
                     "files": inputs,
                     "run_files_match_receipt": all(i["receipt_match"] for i in inputs if i["receipt_match"] is not None)}

    curvej = json.load(open(R(P_CURVE)))
    A, Bc = curvej["A"], curvej["B"]
    isets = json.load(open(R(P_ISETS)))
    insts = [json.loads(l) for l in gzip.open(R(P_INST), "rt")]
    certs = [json.loads(l) for l in gzip.open(R(P_CERTS), "rt")]

    # ------------------------------------------------------------ self-tests
    rng = random.Random(SEED_SELFTEST)
    st = collections.OrderedDict()
    log("self-tests: field")
    st["field_irreducibility"] = F.irreducibility_test()
    st["field_axioms"] = F.field_axioms_test(rng, 10000)
    log("self-tests: curve")
    cv = CV.Curve(A, Bc)
    Pp = tuple(curvej["P"])
    Qp = tuple(curvej["Q"])
    rand_orders = 0
    rand_order_fail = 0
    while rand_orders < 20:
        x = rng.randrange(1, 1 << 17)
        y = cv.lift(x)
        if y is None:
            continue
        rand_orders += 1
        if cv.smul(curvej["order"], (x, y)) is not CV.O:
            rand_order_fail += 1
    st["curve_arithmetic"] = {
        "P_on_curve": cv.on_curve(Pp), "Q_on_curve": cv.on_curve(Qp),
        "qP_is_O": cv.smul(curvej["q"], Pp) is CV.O,
        "kQ_P_equals_Q": cv.smul(curvej["k_Q"], Pp) == Qp,
        "random_points_times_order_is_O": {"points": rand_orders, "failures": rand_order_fail},
    }
    st["curve_arithmetic"]["pass"] = (st["curve_arithmetic"]["P_on_curve"] and st["curve_arithmetic"]["Q_on_curve"]
                                      and st["curve_arithmetic"]["qP_is_O"] and st["curve_arithmetic"]["kQ_P_equals_Q"]
                                      and rand_order_fail == 0)
    log("self-tests: S_3 against point addition")
    st["S3_vs_point_addition"] = CV.s3_point_addition_selftest(cv, rng, 1000)
    log("self-tests: ring, evaluator, layout")
    st["boolean_ring"] = bring.selftest(rng, 200)
    st["evaluator_vs_naive"] = EV.selftest(rng, 200)
    lay = {"ncol": LY.NCOL, "col0_const": LY.COL_TUPLES[0] == (),
           "cols_1_18_linear": [LY.COL_TUPLES[1 + i] for i in range(18)] == [(i,) for i in range(18)],
           "col19": list(LY.COL_TUPLES[19]), "col171": list(LY.COL_TUPLES[171]),
           "n_pairs": sum(1 for t in LY.COL_TUPLES if len(t) == 2)}
    lay["pass"] = (lay["ncol"] == 172 and lay["col0_const"] and lay["cols_1_18_linear"]
                   and lay["col19"] == [0, 1] and lay["col171"] == [16, 17] and lay["n_pairs"] == 153)
    st["E_layout"] = lay
    st["checker_hand_cases"] = checker_hand_cases()
    out["self_tests"] = st

    # ------------------------------------------------------------ constructions
    log("constructions: xr144 table")
    xr144 = []
    order_ok = {}
    for sname in ("U62", "S62", "C20"):
        lst = isets["sets"][sname]
        idxs = [e["idx"] for e in lst]
        order_ok[sname] = idxs == sorted(idxs)
        for e in lst:
            xr144.append({"set": sname, "idx": e["idx"], "x_R": e["archived"]["x_R"], "key": e["key"]})
    out["xr144"] = {"n": len(xr144), "sizes": {s: len(isets["sets"][s]) for s in ("U62", "S62", "C20")},
                    "listed_order_is_ascending_idx": order_ok}

    log("constructions: E_S3 by two routes at 144 x_R, 0 and t^j")
    es3 = {}
    es3_direct_vals = {}
    route_disagree = []
    deg_gt2 = []
    for e in xr144:
        xR = e["x_R"]
        if xR in es3:
            continue
        ra = DS.descent_symbolic(xR, Bc)
        rb, vals = DS.descent_interpolated(xR, Bc)
        if ra != rb:
            route_disagree.append(xR)
        es3[xR] = ra
        es3_direct_vals[xR] = int(np.count_nonzero(vals == 0))
    for xR in [0] + [1 << j for j in range(17)]:
        ra = DS.descent_symbolic(xR, Bc)
        rb, _ = DS.descent_interpolated(xR, Bc)
        if ra != rb:
            route_disagree.append(xR)
    # archived E_hex vs own construction (S_3 sets)
    arch_vs_own = {"checked": 0, "mismatch": []}
    for sname in ("U62", "S62", "C20"):
        for e in isets["sets"][sname]:
            arch_vs_own["checked"] += 1
            if LY.decode_rows(e["E_hex"]) != es3[e["archived"]["x_R"]]:
                arch_vs_own["mismatch"].append(e["key"])
    out["descent"] = {"x_R_count": len(es3), "extra_points": 18, "routes_disagree": route_disagree,
                      "archived_instance_sets_E_hex_vs_own": arch_vs_own,
                      "pass": not route_disagree and not arch_vs_own["mismatch"]}

    log("constructions: union support, S_L, Q_k")
    U, E0, Ej = DS.union_support(Bc, DS.descent_symbolic)
    U_b, _, _ = DS.union_support(Bc, lambda x, b: DS.descent_interpolated(x, b)[0])
    SL = DS.S_L_positions(U)
    SLrow = [U[k] & LY.LOW_MASK for k in range(17)]
    Qr = DS.Q_rows()
    bits_B = [(Bc >> k) & 1 for k in range(17)]
    reading = all(((U[k] & LY.BILINEAR_MASK) == LY.BILINEAR_MASK) and ((U[k] & LY.LINEAR_MASK) == LY.LINEAR_MASK)
                  and (((U[k] & 1) == 1) == (bits_B[k] == 1)) for k in range(17))
    reading_exact = reading and all((U[k] & ~(LY.BILINEAR_MASK | LY.LINEAR_MASK | LY.CONST_MASK)) == 0 for k in range(17))
    out["union_support"] = {
        "U_sizes_per_eq": [bin(u).count("1") for u in U],
        "U_equal_by_both_descent_routes": U == U_b,
        "S_L_size": len(SL), "S_L_const_positions": [k for k in range(17) if SLrow[k] & 1],
        "popcount_B": bin(Bc).count("1"),
        "coordinator_reading_true": reading,
        "coordinator_reading_note": "U_k contains all 81 bilinear and all 18 linear columns, plus the constant iff bit k of B is 1",
        "U_has_columns_beyond_bilinear_linear_const": not reading_exact,
        "expected_S_L_size_17x18_plus_popcount_B": 17 * 18 + bin(Bc).count("1"),
        "E_S3_quadratic_columns_bilinear_only": all((r & LY.QUAD_MASK & ~LY.BILINEAR_MASK) == 0 for rows in es3.values() for r in rows),
    }

    # ------------------------------------------------------------ VC-2 construction checks
    log("VC-2: kept parts, keys, E_sha256, x_R binding")
    key_count = collections.Counter(r["key"] for r in insts)
    by_key = {}
    for r in insts:
        by_key.setdefault(r["key"], []).append(r)
    iset_by_key = {}
    for sname, lst in isets["sets"].items():
        for e in lst:
            iset_by_key[e["key"]] = (sname, e)
    sysrec = {}
    per_arm = collections.OrderedDict()
    violations_all = []
    sha_serial_mismatch = 0
    noncanon_hex = 0
    dup_sha_by_arm = collections.defaultdict(collections.Counter)
    for r in insts:
        arm = r["arm"]
        key = r["key"]
        v = []
        try:
            rows = LY.decode_rows(r["E_hex"])
        except Exception as ex:  # noqa
            v.append("decode failed: %s" % ex)
            rows = None
        h = hashlib.sha256(json.dumps(r["E_hex"]).encode("utf-8")).hexdigest()
        if h != r["E_sha256"]:
            sha_serial_mismatch += 1
            v.append("E_sha256 mismatch")
        dup_sha_by_arm[arm][r["E_sha256"]] += 1
        if rows is not None and [LY.encode_hex(x) for x in rows] != r["E_hex"]:
            noncanon_hex += 1
        if key_count[key] != 1:
            v.append("key occurs %d times" % key_count[key])
        slot = r["slot"]
        if rows is not None:
            if arm in FRESH_ARMS:
                if key != "%s:%d:%s" % (arm, slot, r["role"]):
                    v.append("fresh key not <ARM>:<slot>:<role>")
                if not (0 <= slot < 144):
                    v.append("slot out of range")
            if arm in ("N-CONV", "N-CONVL"):
                t = xr144[slot]
                if (r["source_set"], r["idx"], r["x_R"]) != (t["set"], t["idx"], t["x_R"]):
                    v.append("x_R binding differs from xr144 slot table")
                ref = es3[t["x_R"]]
                if arm == "N-CONV":
                    for k in range(17):
                        if (rows[k] & LY.QUAD_MASK) != (ref[k] & LY.QUAD_MASK):
                            v.append("row %d quadratic columns differ from own E_S3(x_R)" % k)
                        if not row_subset(rows[k] & LY.LOW_MASK, SLrow[k]):
                            v.append("row %d low-column bit outside S_L" % k)
                    if rows == ref:
                        v.append("system equals E_S3(x_R) (identity draw kept)")
                else:
                    keep = LY.QUAD_MASK | LY.LINEAR_MASK
                    for k in range(17):
                        if (rows[k] & keep) != (ref[k] & keep):
                            v.append("row %d quadratic/linear columns differ from own E_S3(x_R)" % k)
                    const_bits = [rows[k] & 1 for k in range(17)]
                    for k in range(17):
                        if const_bits[k] and not (SLrow[k] & 1):
                            v.append("row %d constant bit outside S_L cap column 0" % k)
                    if const_bits == bits_B:
                        v.append("constant bits equal B's own bits")
                    if not any(const_bits):
                        v.append("constant bits all zero")
                    bp = sum(b << k for k, b in enumerate(const_bits))
                    if r.get("bprime") != bp:
                        v.append("bprime field %r != constant-column value %d" % (r.get("bprime"), bp))
                    if DS.descent_symbolic(t["x_R"], bp) != rows:
                        v.append("system != own E_S3(x_R) with curve constant b'")
            elif arm == "N-CONV17":
                if r["x_R"] is not None:
                    v.append("x_R not null")
                for k in range(17):
                    if (rows[k] & LY.QUAD_MASK) != Qr[k]:
                        v.append("row %d quadratic columns != Q_k" % k)
                    if not row_subset(rows[k] & LY.LOW_MASK, SLrow[k]):
                        v.append("row %d low-column bit outside S_L" % k)
            elif arm in ("N-ELL144", "NELL-A20"):
                for k in range(16):
                    if not row_subset(rows[k], U[k]):
                        v.append("row %d outside U" % k)
                c = rows[16] & 1
                want = (1 << LY.MASK_TO_COL[1 << 0]) | (1 << LY.MASK_TO_COL[1 << 9]) | c
                if rows[16] != want:
                    v.append("row 16 != v_0 + v_9 + c")
                if arm == "N-ELL144" and r.get("c") != c:
                    v.append("c field %r != row-16 constant %d" % (r.get("c"), c))
            elif arm in S3_ARMS:
                sname = S3_ARMS[arm]
                if key not in iset_by_key or iset_by_key[key][0] != sname:
                    v.append("key not in instance-sets %s" % sname)
                else:
                    e = iset_by_key[key][1]
                    if e["E_hex"] != r["E_hex"]:
                        v.append("E_hex differs from instance-sets.json")
                    if e["archived"]["x_R"] != r["x_R"]:
                        v.append("x_R differs from instance-sets.json")
                    if e["archived"]["s"] != r["s"]:
                        v.append("s differs from instance-sets archived s")
                t = xr144[slot] if 0 <= slot < 144 else None
                if t is None or t["key"] != key or t["x_R"] != r["x_R"] or t["set"] != sname:
                    v.append("x_R/slot binding differs from xr144 slot table")
                if rows != es3.get(r["x_R"]):
                    v.append("system != own E_S3(x_R)")
            elif arm in NULL_ARMS:
                sname = NULL_ARMS[arm]
                if key not in iset_by_key or iset_by_key[key][0] != sname:
                    v.append("key not in instance-sets %s" % sname)
                else:
                    e = iset_by_key[key][1]
                    if e["E_hex"] != r["E_hex"]:
                        v.append("E_hex differs from instance-sets.json")
                    if e["archived"]["s"] != r["s"]:
                        v.append("s differs from instance-sets archived s")
                for k in range(17):
                    if not row_subset(rows[k], U[k]):
                        v.append("row %d outside U" % k)
            else:
                v.append("unknown arm")
        rec = {"key": key, "arm": arm, "role": r["role"], "slot": slot, "x_R": r["x_R"],
               "kept_part_ok": not v, "violations": v}
        sysrec[key] = {"rec": r, "rows": rows, "vc2": rec}
        pa = per_arm.setdefault(arm, {"systems_checked": 0, "systems_with_violation": 0, "violation_count": 0})
        pa["systems_checked"] += 1
        if v:
            pa["systems_with_violation"] += 1
            pa["violation_count"] += len(v)
            violations_all.append(rec)
    dups = {arm: sum(1 for c in cnt.values() if c > 1) for arm, cnt in dup_sha_by_arm.items()}
    out["construction_VC2"] = {
        "systems_total": len(insts),
        "per_arm": per_arm,
        "violations": violations_all,
        "E_sha256_serialization": "sha256(json.dumps(E_hex).encode('utf-8')), Python default separators",
        "E_sha256_mismatches": sha_serial_mismatch,
        "noncanonical_hex_rows_systems": noncanon_hex,
        "duplicate_E_sha256_within_arm": dups,
        "NELL_A20_source_note": ("NELL-A20 source n-ell-instances.json lies under coordination/review/certbin-20260924-3d7e1a/reviews/, "
                                 "which is must_not_read for this task; checked only structurally (rows 0..15 in U, row 16 = v_0 + v_9 + c)."),
        "pass": not violations_all and sha_serial_mismatch == 0,
    }

    # ------------------------------------------------------------ VC-5 satisfiability
    log("VC-5: exhaustive s on all 1440 systems")
    sat = collections.OrderedDict()
    sat_fail = []
    conv_counts = collections.Counter()
    sol_list_checked = 0
    for r in insts:
        key = r["key"]
        rows = sysrec[key]["rows"]
        s, idx = EV.solutions(rows)
        solset = set(idx.tolist())
        entry = {"s_mine": s, "s_record": r["s"], "s_match": s == r["s"],
                 "role_consistent": (r["role"] == "unsat") == (s == 0)}
        if r["arm"] in S3_ARMS or r["arm"] == "N-CONVL":
            b = Bc if r["arm"] in S3_ARMS else r.get("bprime")
            vals = DS.eval_S3_all(r["x_R"], b)
            entry["s_direct_field_eval"] = int(np.count_nonzero(vals == 0))
            entry["s_direct_match"] = entry["s_direct_field_eval"] == s
        if "solutions" in r:
            listed = r["solutions"]
            sol_list_checked += 1
            direct_ok = all(not any(EV.naive_eval(rows, u)) for u in listed)
            rev = lambda u: int(format(u, "018b")[::-1], 2)
            rev_ok = all(not any(EV.naive_eval(rows, rev(u))) for u in listed)
            entry["listed_solutions"] = len(listed)
            entry["listed_solutions_check_bit_i_is_v_i"] = direct_ok
            entry["listed_solutions_check_reversed_bits"] = rev_ok
            entry["listed_equals_exhaustive_set"] = sorted(listed) == sorted(solset)
            conv_counts[(direct_ok, rev_ok)] += 1
        ok = entry["s_match"] and entry["role_consistent"] and entry.get("s_direct_match", True) \
            and entry.get("listed_solutions_check_bit_i_is_v_i", True) and entry.get("listed_equals_exhaustive_set", True)
        entry["ok"] = ok
        sat[key] = entry
        if not ok:
            sat_fail.append(key)
    out["satisfiability_VC5"] = {
        "systems": len(sat), "failures": sat_fail,
        "solution_lists_checked": sol_list_checked,
        "solution_encoding_outcomes": {"%s/%s" % k: v for k, v in conv_counts.items()},
        "per_arm": summarize_sat(insts, sat),
        "pass": not sat_fail,
    }

    # ------------------------------------------------------------ VC-3 certificates
    log("VC-3: verifying %d certificate lines" % len(certs))
    polys_cache = {}

    def F_of(key):
        if key not in polys_cache:
            rows = sysrec[key]["rows"]
            polys_cache[key] = CC.system_polys([LY.row_monomials(x) for x in rows])
        return polys_cache[key]

    tt_cache = collections.OrderedDict()

    def FT_of(key):
        if key in tt_cache:
            tt_cache.move_to_end(key)
            return tt_cache[key]
        t = TT.system_truth(sysrec[key]["rows"])
        tt_cache[key] = t
        if len(tt_cache) > 48:
            tt_cache.popitem(last=False)
        return t

    lines = []
    for ln_no, c in enumerate(certs):
        key = c.get("key")
        res = {"line": ln_no, "cid": c.get("cid"), "key": key, "closure": c.get("closure"),
               "format": c.get("format"), "source": c.get("source"), "arm_declared": c.get("arm"),
               "role_declared": c.get("role")}
        matches = by_key.get(key, [])
        res["systems_found"] = len(matches)
        if len(matches) != 1:
            res.update(verified=False, first_violated_rule="key", reason="key names %d systems" % len(matches))
            lines.append(res)
            continue
        srec = matches[0]
        res["arm"] = srec["arm"]
        res["role"] = srec["role"]
        res["arm_matches"] = srec["arm"] == c.get("arm")
        res["role_matches"] = srec["role"] == c.get("role")
        res["system_s_mine"] = sat[key]["s_mine"]
        res["system_kept_part_ok"] = sysrec[key]["vc2"]["kept_part_ok"]
        Fk = F_of(key)
        if c.get("format") == "flat-v1":
            r = CC.check_flat(c.get("body"), Fk)
            res.update(verified=r["verified"], reason=r.get("reason"), size=r.get("size"), max_mu=r.get("max_mu"),
                       residual_size=r.get("residual_size"), residual_sample=r.get("residual_sample"),
                       format_notes=r.get("format_notes"), first_violated_rule=None if r["verified"] else "identity")
            res["node_count"] = None
            res["max_child_degree"] = None
        elif c.get("format") == "wdag-v1":
            r = CC.check_wdag(c.get("body"), Fk)
            res.update(verified=r["verified"], reason=r.get("reason"), size=r.get("size"), max_mu=r.get("max_mu"),
                       node_count=r.get("node_count"), n_prods=r.get("n_prods"),
                       max_child_degree=r.get("max_child_degree"), node_degrees=r.get("node_degrees"),
                       rules=r.get("rules"), first_violated_rule=r.get("first_violated_rule"),
                       violations=r.get("violations"), residual_size=r.get("residual_size"),
                       residual_sample=r.get("residual_sample"), format_notes=r.get("format_notes"))
        else:
            res.update(verified=False, first_violated_rule="format", reason="unknown format")
        # second route (truth tables): identity, and degrees via Moebius
        res.update(route_T(c.get("format"), c.get("body"), res, FT_of(key)))
        # producer-declared fields vs own
        res["producer_max_mu"] = c.get("max_mu")
        res["producer_size"] = c.get("size")
        res["producer_node_count"] = c.get("node_count")
        # frozen counting rule
        fmt = c.get("format")
        ver = bool(res.get("verified"))
        res["counts_toward_M4"] = ver and fmt == "flat-v1" and c.get("closure") == "M_4" and (res.get("max_mu") is not None and res["max_mu"] <= 2)
        res["counts_toward_w"] = ver and fmt == "wdag-v1" and c.get("closure") == "W_4"
        res["flat_W4_eligible_maxmu_le2"] = (ver and fmt == "flat-v1" and c.get("closure") == "W_4"
                                            and res.get("max_mu") is not None and res["max_mu"] <= 2)
        res["one_node_wdag_no_prods"] = (fmt == "wdag-v1" and res.get("node_count") == 1 and res.get("n_prods") == 0)
        res["verified_on_satisfiable_system"] = ver and sat[key]["s_mine"] >= 1
        lines.append(res)
        if ln_no % 200 == 0:
            log("  line %d" % ln_no)

    # tables
    kinds = collections.OrderedDict()
    for res in lines:
        k = (res.get("closure"), res.get("arm", res.get("arm_declared")), res.get("format"))
        t = kinds.setdefault(k, {"closure": k[0], "arm": k[1], "format": k[2], "submitted": 0, "verified": 0,
                                 "rejected": 0, "counted_frozen_rule": 0, "roles": collections.Counter(),
                                 "max_mu_dist": collections.Counter(), "node_count_dist": collections.Counter(),
                                 "max_child_degree_dist": collections.Counter(),
                                 "producer_fields_match_own": 0, "producer_fields_mismatch": 0})
        t["submitted"] += 1
        t["roles"][res.get("role")] += 1
        if res.get("verified"):
            t["verified"] += 1
        else:
            t["rejected"] += 1
        if res.get("counts_toward_M4") or res.get("counts_toward_w"):
            t["counted_frozen_rule"] += 1
        t["max_mu_dist"][str(res.get("max_mu"))] += 1
        if res.get("format") == "wdag-v1":
            t["node_count_dist"][str(res.get("node_count"))] += 1
            t["max_child_degree_dist"][str(res.get("max_child_degree"))] += 1
        pm = [res.get("producer_max_mu") == res.get("max_mu") if res.get("producer_max_mu") is not None else True,
              res.get("producer_size") == res.get("size") if res.get("producer_size") is not None else True,
              res.get("producer_node_count") == res.get("node_count") if res.get("producer_node_count") is not None else True]
        if all(pm):
            t["producer_fields_match_own"] += 1
        else:
            t["producer_fields_mismatch"] += 1
    kind_table = []
    for t in kinds.values():
        t = dict(t)
        for f in ("roles", "max_mu_dist", "node_count_dist", "max_child_degree_dist"):
            t[f] = dict(sorted(t[f].items()))
        kind_table.append(t)

    # per-arm systems
    arm_sys = collections.OrderedDict()
    arms_order = ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144", "S3-U62", "S3-C20", "S3-S62",
                  "NULL-AFF62", "NULL-F262", "NELL-A20"]
    for arm in arms_order:
        keys_unsat = [r["key"] for r in insts if r["arm"] == arm and r["role"] == "unsat"]
        keys_sat = [r["key"] for r in insts if r["arm"] == arm and r["role"] == "sat"]
        m4 = set(x["key"] for x in lines if x.get("counts_toward_M4") and x.get("arm") == arm)
        wd = set(x["key"] for x in lines if x.get("counts_toward_w") and x.get("arm") == arm)
        anyflat_le2 = set(x["key"] for x in lines if x.get("verified") and x.get("format") == "flat-v1"
                          and x.get("max_mu") is not None and x["max_mu"] <= 2 and x.get("arm") == arm)
        onenode = set(x["key"] for x in lines if x.get("verified") and x.get("one_node_wdag_no_prods") and x.get("arm") == arm)
        certified_any = set(x["key"] for x in lines if x.get("arm") == arm)
        arm_sys[arm] = {
            "unsat_systems": len(keys_unsat), "sat_systems": len(keys_sat),
            "systems_with_verified_counted_M4_certificate": len(m4),
            "systems_with_verified_wdag_v1": len(wd),
            "of_which_unsat": {"M4": len(m4 & set(keys_unsat)), "wdag": len(wd & set(keys_unsat))},
            "of_which_sat": {"M4": len(m4 & set(keys_sat)), "wdag": len(wd & set(keys_sat))},
            "alt_any_verified_flat_maxmu_le2_any_closure_label": len(anyflat_le2),
            "alt_verified_one_node_wdag_no_prods": len(onenode),
            "systems_named_by_any_certificate_line": len(certified_any),
        }
    counted_rejected = [x for x in lines if not x.get("verified") and (
        (x.get("format") == "wdag-v1" and x.get("closure") == "W_4") or
        (x.get("format") == "flat-v1" and x.get("closure") == "M_4"))]
    out["certificates_VC3"] = {
        "lines_total": len(lines),
        "verified": sum(1 for x in lines if x.get("verified")),
        "rejected": sum(1 for x in lines if not x.get("verified")),
        "rejected_lines": [{"line": x["line"], "key": x["key"], "closure": x.get("closure"), "format": x.get("format"),
                            "first_violated_rule": x.get("first_violated_rule"), "reason": x.get("reason"),
                            "max_mu": x.get("max_mu")} for x in lines if not x.get("verified")],
        "rejected_lines_that_would_count_if_verified": [x["key"] for x in counted_rejected],
        "keys_not_resolving_to_exactly_one_system": [x["key"] for x in lines if x.get("systems_found") != 1],
        "arm_or_role_field_mismatch": [x["line"] for x in lines if x.get("systems_found") == 1 and not (x.get("arm_matches") and x.get("role_matches"))],
        "verified_on_satisfiable_system": [x["key"] for x in lines if x.get("verified_on_satisfiable_system")],
        "certified_systems_with_s_ge_1": sorted(set(x["key"] for x in lines if x.get("systems_found") == 1 and x.get("system_s_mine", 0) >= 1)),
        "certified_systems_with_kept_part_violation": sorted(set(x["key"] for x in lines if x.get("systems_found") == 1 and not x.get("system_kept_part_ok"))),
        "counting_rule": ("M_4: verified flat-v1 line with closure M_4 and max |mu| <= 2. "
                          "w: verified wdag-v1 line with closure W_4. flat-v1 never counts toward w; a W_4 flat-v1 with max |mu| <= 2 is "
                          "flagged flat_W4_eligible_maxmu_le2 (certifies 1 in M_4, a subset of W_4) but is not a w count."),
        "per_kind": kind_table,
        "per_arm_systems": arm_sys,
        "per_line": lines,
    }

    # ------------------------------------------------------------ VC-4 negative controls
    log("VC-4: negative controls")
    out["negative_controls_VC4"] = negative_controls(certs, lines, insts, sysrec, F_of, sat, FT_of)

    # ------------------------------------------------------------ ambiguities
    out["ambiguities"] = ambiguity_list()

    # ------------------------------------------------------------ summary
    vc3 = out["certificates_VC3"]
    vc4 = out["negative_controls_VC4"]
    selftests_pass = all(v.get("pass", False) for v in st.values())
    out["summary"] = {
        "self_tests_pass": selftests_pass,
        "descent_two_routes_agree_and_match_archived": out["descent"]["pass"],
        "run_files_match_receipt": out["inputs"]["run_files_match_receipt"],
        "VC2_all_kept_parts_ok": out["construction_VC2"]["pass"],
        "VC5_all_s_ok": out["satisfiability_VC5"]["pass"],
        "VC3_lines": vc3["lines_total"], "VC3_verified": vc3["verified"], "VC3_rejected": vc3["rejected"],
        "VC3_counted_lines_rejected": vc3["rejected_lines_that_would_count_if_verified"],
        "VC3_certified_systems_with_s_ge_1": vc3["certified_systems_with_s_ge_1"],
        "VC3_certified_systems_with_kept_part_violation": vc3["certified_systems_with_kept_part_violation"],
        "VC4_controls": vc4["total"], "VC4_rejected": vc4["rejected"], "VC4_accepted": vc4["accepted"],
        "VC4_all_kinds_covered_min5_per_type": vc4["all_kinds_covered_min5_per_type"],
        "VC3_route_T_lines_agree": sum(1 for x in vc3["per_line"] if x.get("routes_agree")),
        "VC3_route_T_lines_disagree": [x["line"] for x in vc3["per_line"] if not x.get("routes_agree")],
        "VC3_route_T_node_degree_mismatch": [x["line"] for x in vc3["per_line"] if x.get("route_T_node_degrees_equal") is False],
        "VC4_rejected_by_both_routes": sum(1 for r in vc4["records"] if not r["type"].startswith("h") and r.get("rejected_by_both_routes")),
    }
    ru = resource.getrusage(resource.RUSAGE_SELF)
    out["meta"] = {
        "started_utc": started, "finished_utc": utcnow(), "wall_seconds": round(time.time() - t_start, 1),
        "peak_rss_mb": round(ru.ru_maxrss / 1024.0, 1),
        "python": sys.version, "numpy": np.__version__, "platform": platform.platform(),
        "seeds": {"selftest_python_random": SEED_SELFTEST, "negative_controls_python_random": SEED_NEGCTL},
        "argv": sys.argv,
        "code_sha256": {f: sha256_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), f))
                        for f in sorted(os.listdir(os.path.dirname(os.path.abspath(__file__)))) if f.endswith(".py")},
        "repository_modules_loaded": repo_modules_loaded(),
        "env": {k: os.environ.get(k) for k in ("PYTHONDONTWRITEBYTECODE", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False, default=_jdefault)
        fh.write("\n")
    log("wrote %s" % args.out)
    log("summary: %s" % json.dumps(out["summary"], default=_jdefault))


def _jdefault(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, set):
        return sorted(o)
    raise TypeError(type(o))


def repo_modules_loaded():
    """Every loaded module whose file lies outside this code/ directory and
    outside the Python installation: must be empty of repository modules."""
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for name, m in list(sys.modules.items()):
        f = getattr(m, "__file__", None)
        if not f:
            continue
        f = os.path.abspath(f)
        if f.startswith(here):
            continue
        if "crypto_autoresearcher" in f or "/impl/" in f or "/verifier/" in f or "crypto-autoresearcher" in f:
            out.append({"module": name, "file": f})
    return out


def summarize_sat(insts, sat):
    pa = collections.OrderedDict()
    for r in insts:
        e = sat[r["key"]]
        a = pa.setdefault(r["arm"] + ":" + r["role"], {"systems": 0, "s_match": 0, "role_consistent": 0,
                                                     "s_zero": 0, "s_ge1": 0, "solution_lists_ok": 0,
                                                     "direct_field_eval_match": 0})
        a["systems"] += 1
        a["s_match"] += int(e["s_match"])
        a["role_consistent"] += int(e["role_consistent"])
        a["s_zero"] += int(e["s_mine"] == 0)
        a["s_ge1"] += int(e["s_mine"] >= 1)
        if "listed_solutions" in e:
            a["solution_lists_ok"] += int(e["listed_solutions_check_bit_i_is_v_i"] and e["listed_equals_exhaustive_set"])
        if "s_direct_match" in e:
            a["direct_field_eval_match"] += int(e["s_direct_match"])
    return pa


# ---------------------------------------------------------------------------
def checker_hand_cases():
    """Hand-built systems and certificates whose validity is known by hand."""
    M = lambda *idx: sum(1 << i for i in idx)
    # f_0 = v_0 + 1, f_1 = v_0, f_2 = v_0 v_1 + v_2, others 0
    rows = [[] for _ in range(17)]
    rows[0] = [M(0), 0]
    rows[1] = [M(0)]
    rows[2] = [M(0, 1), M(2)]
    Fk = CC.system_polys(rows)
    cases = []

    def add(name, fmt, body, expect_verified, expect_first=None):
        if fmt == "flat":
            r = CC.check_flat(body, Fk)
            first = None if r["verified"] else "identity"
        else:
            r = CC.check_wdag(body, Fk)
            first = r.get("first_violated_rule")
        ok = (r["verified"] == expect_verified) and (expect_first is None or first == expect_first)
        cases.append({"case": name, "expect_verified": expect_verified, "got_verified": r["verified"],
                      "expect_first": expect_first, "got_first": first, "ok": ok})

    add("flat f0+f1=1", "flat", [[[], 0], [[], 1]], True)
    add("flat f0=1? no", "flat", [[[], 0]], False)
    add("flat v1*f1 + f2 + v1*... (v0v1 + v0v1 + v2) != 1", "flat", [[[1], 1], [[], 2]], False)
    add("flat duplicated row cancels", "flat", [[[], 0], [[], 1], [[5], 2], [[5], 2]], True)
    # wdag: node0 = f1 (= v0), node1 = f0 + v0*node0 = v0 + 1 + v0 = 1
    good = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 1]], "prods": []},
                                         {"id": 1, "rows": [[[], 0]], "prods": [[0, 0]]}], "output": 1}
    add("wdag 2-node valid", "wdag", good, True)
    bad_a = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 0]], "prods": [[0, 1]]},
                                          {"id": 1, "rows": [[[], 1]], "prods": []}], "output": 0}
    add("wdag forward reference", "wdag", bad_a, False, "a")
    bad_b = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 1]], "prods": []},
                                          {"id": 1, "rows": [[[], 0], [[3, 4, 5], 2], [[3, 4, 5], 2]], "prods": [[0, 0]]}], "output": 1}
    add("wdag |mu|=3 doubled row", "wdag", bad_b, False, "b")
    # child of degree 4: node0 = v3v4*f2 = v0v1v3v4 + v2v3v4 (deg 4); used twice -> cancels
    bad_c = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[3, 4], 2]], "prods": []},
                                          {"id": 1, "rows": [[[], 1]], "prods": []},
                                          {"id": 2, "rows": [[[], 0]], "prods": [[0, 1], [7, 0], [7, 0]]}], "output": 2}
    add("wdag degree-4 child", "wdag", bad_c, False, "c")
    # node of degree 5: v7 * node0 (deg 4) once
    bad_d = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[3, 4], 2]], "prods": []},
                                          {"id": 1, "rows": [], "prods": [[7, 0]]},
                                          {"id": 2, "rows": [[[], 0], [[], 1]], "prods": []}], "output": 2}
    add("wdag degree-5 node (rule c and d)", "wdag", bad_d, False, "c")
    bad_e = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": [[[], 1]], "prods": []},
                                          {"id": 1, "rows": [[[], 0]], "prods": []}], "output": 1}
    add("wdag output != 1", "wdag", bad_e, False, "e")
    return {"cases": cases, "pass": all(c["ok"] for c in cases)}


# ---------------------------------------------------------------------------
def negative_controls(certs, lines, insts, sysrec, F_of, sat, FT_of):
    rng = random.Random(SEED_NEGCTL)
    arm_keys = collections.defaultdict(list)
    for r in insts:
        arm_keys[r["arm"]].append(r["key"])
    for a in arm_keys:
        arm_keys[a].sort()
    # flat |mu|=3 bodies per key (for wdag rule-(b) rewrite)
    flat3_by_key = {}
    for c, ln in zip(certs, lines):
        if c.get("format") == "flat-v1" and ln.get("verified") and ln.get("max_mu") == 3:
            flat3_by_key.setdefault(c["key"], c["body"])
    kinds = collections.OrderedDict()
    for c, ln in zip(certs, lines):
        if ln.get("systems_found") != 1:
            continue
        kinds.setdefault((c["closure"], ln["arm"], c["format"]), []).append((c, ln))
    records = []
    coverage = []

    def nonzero_row_positions(body_rows, Fk):
        return [p for p, (mu, k) in enumerate(body_rows) if Fk[k].size]

    def contrib(mu, k, Fk):
        m = sum(1 << i for i in mu)
        return bring.times_monomial(Fk[k], m)

    for kind, items in kinds.items():
        closure, arm, fmt = kind
        pool = [it for it in items if it[1].get("verified")]
        source_note = "verified certificates of the kind"
        if not pool:
            pool = items
            source_note = "no verified certificate in kind; submitted ones used"
        pool = sorted(pool, key=lambda it: (it[0]["key"], it[0].get("cid") or 0))
        if len(pool) >= N_NEG_PER_TYPE:
            picks = rng.sample(pool, N_NEG_PER_TYPE)
        else:
            picks = [pool[i % len(pool)] for i in range(N_NEG_PER_TYPE)]
        types = ["a_row_removed", "b_k_changed", "c_mu_changed_same_degree", "d_transplant_same_arm"]
        if fmt == "wdag-v1":
            types += ["e_rule_b_mu3_sum_still_1", "f_rule_c_degree4_child", "g_rule_a_forward_reference"]
        cov = {"closure": closure, "arm": arm, "format": fmt, "source_pool": len(pool), "source_note": source_note,
               "per_type": {}}
        for typ in types:
            n_rej = 0
            n_tot = 0
            for (c, ln) in picks:
                rec = build_and_check(typ, c, ln, fmt, rng, arm_keys[arm], F_of, flat3_by_key, FT_of)
                rec.update({"closure": closure, "arm": arm, "format": fmt, "type": typ,
                            "source_key": c["key"], "source_cid": c.get("cid")})
                records.append(rec)
                n_tot += 1
                n_rej += int(rec["rejected"])
            cov["per_type"][typ] = {"built": n_tot, "rejected": n_rej}
        # extra classification control for M_4 kinds: a verified flat with max|mu| = 3 relabelled M_4
        if closure == "M_4" and fmt == "flat-v1":
            cands = sorted([(c, ln) for (c, ln) in zip(certs, lines) if ln.get("arm") == arm and c.get("format") == "flat-v1"
                            and ln.get("verified") and ln.get("max_mu") == 3], key=lambda it: it[0]["key"])
            nb = 0
            ncount = 0
            for (c, ln) in (rng.sample(cands, N_NEG_PER_TYPE) if len(cands) >= N_NEG_PER_TYPE else cands):
                r = CC.check_flat(c["body"], F_of(c["key"]))
                rtv = route_T("flat-v1", c["body"], {"verified": r["verified"]}, FT_of(c["key"]))
                counts = r["verified"] and r["max_mu"] <= 2
                records.append({"closure": "M_4", "arm": arm, "format": "flat-v1", "type": "h_maxmu3_flat_submitted_as_M4",
                                "source_key": c["key"], "source_cid": c.get("cid"), "identity_verified": r["verified"],
                                "route_T_identity": rtv.get("route_T_verified"),
                                "max_mu": r["max_mu"], "counts_toward_M4": counts, "rejected": not counts,
                                "expect": "identity may hold; must NOT count toward M_4"})
                nb += 1
                ncount += int(counts)
            cov["per_type"]["h_maxmu3_flat_submitted_as_M4"] = {"built": nb, "rejected_from_count": nb - ncount,
                                                                 "note": "extra; constructible only where a verified max|mu|=3 flat exists in the arm"}
            # h2: always constructible -- a verified M_4 flat of the kind with a doubled |mu| = 3 row appended
            nb2 = 0
            ncount2 = 0
            for (c, ln) in picks:
                mu3 = sorted(rng.sample(range(18), 3))
                k3 = rng.randrange(17)
                body = _deepcopy_body(c["body"]) + [[mu3, k3], [mu3, k3]]
                r = CC.check_flat(body, F_of(c["key"]))
                rtv = route_T("flat-v1", body, {"verified": r["verified"]}, FT_of(c["key"]))
                counts = r["verified"] and r["max_mu"] <= 2
                records.append({"closure": "M_4", "arm": arm, "format": "flat-v1", "type": "h2_doubled_mu3_row_flat_as_M4",
                                "source_key": c["key"], "source_cid": c.get("cid"), "position": {"mu3": mu3, "k": k3},
                                "identity_verified": r["verified"], "route_T_identity": rtv.get("route_T_verified"),
                                "max_mu": r["max_mu"], "counts_toward_M4": counts, "rejected": not counts,
                                "expect": "identity holds; max|mu| = 3; must NOT count toward M_4"})
                nb2 += 1
                ncount2 += int(counts)
            cov["per_type"]["h2_doubled_mu3_row_flat_as_M4"] = {"built": nb2, "rejected_from_count": nb2 - ncount2,
                                                                "note": "extra counting-rule control; always constructible"}
        cov["min5_per_required_type"] = all(cov["per_type"][t]["built"] >= N_NEG_PER_TYPE for t in types)
        cov["all_rejected"] = all(cov["per_type"][t]["rejected"] == cov["per_type"][t]["built"] for t in types)
        coverage.append(cov)
    total = sum(1 for r in records if not r["type"].startswith("h"))
    rej = sum(1 for r in records if not r["type"].startswith("h") and r["rejected"])
    return {"seed_python_random": SEED_NEGCTL,
            "position_rule": ("Per kind: sources = rng.sample of the kind's verified certificates sorted by (key, cid) "
                              "(cyclic reuse if fewer than 5). Row positions, replacement k, replacement mu and transplant targets "
                              "are drawn with the same rng; a row is eligible only if its contribution mu*f_k is nonzero, a k-change only "
                              "if mu*(f_k + f_k') != 0, a mu-change only if (mu + mu')*f_k != 0, so the corrupted sum provably changes at "
                              "that node. Transplant target: another system of the same arm, rng-chosen."),
            "constructions": {
                "e_rule_b_mu3_sum_still_1": ("If the same system has a verified flat-v1 with max|mu| = 3, it is rewritten as a one-node "
                                             "wdag-v1 (sum 1, rule (b) violated). Otherwise a row (mu3, k) with |mu3| = 3 is added TWICE to "
                                             "the output node (cancels; sum still 1; rule (b) violated)."),
                "f_rule_c_degree4_child": ("A node with rows [(mu2, k)] and deg(mu2*f_k) = 4 is prepended (ids shifted by 1) and "
                                           "[[j, 0], [j, 0]] is appended to the output node's prods (cancels; sum still 1; only rule (c) violated)."),
                "g_rule_a_forward_reference": ("Multi-node: node ids reversed (id -> n-1-id, children and output remapped; every "
                                               "child reference becomes forward; algebra unchanged). One-node: a node with rows [([], k)] is "
                                               "appended with id 1 and [[j, 1], [j, 1]] is added to node 0's prods (cancels)."),
            },
            "coverage": coverage,
            "total": total, "rejected": rej, "accepted": total - rej,
            "accepted_records": [r for r in records if not r["type"].startswith("h") and not r["rejected"]],
            "counting_rule_controls": {"built": sum(1 for r in records if r["type"].startswith("h")),
                                       "excluded_from_M4_count": sum(1 for r in records if r["type"].startswith("h") and r["rejected"]),
                                       "note": "extra (not required by VC-4): flat-v1 with max|mu| = 3 whose identity holds, submitted as M_4; must not count"},
            "all_kinds_covered_min5_per_type": all(c["min5_per_required_type"] for c in coverage),
            "records": records}


def _deepcopy_body(b):
    return json.loads(json.dumps(b))


def build_and_check(typ, c, ln, fmt, rng, arm_keys, F_of, flat3_by_key, FT_of):
    key = c["key"]
    Fk = F_of(key)
    body = _deepcopy_body(c["body"])
    rec = {"expect": "reject"}
    target_key = key

    def all_rows():
        if fmt == "flat-v1":
            return [(None, p, body[p]) for p in range(len(body))]
        out = []
        for ni, nd in enumerate(body["nodes"]):
            for p, rw in enumerate(nd.get("rows", [])):
                out.append((ni, p, rw))
        return out

    def row_contrib_nonzero(mu, k):
        m = sum(1 << i for i in mu)
        return bring.times_monomial(Fk[k], m).size > 0

    def set_row(ni, p, new):
        if fmt == "flat-v1":
            body[p] = new
        else:
            body["nodes"][ni]["rows"][p] = new

    def del_row(ni, p):
        if fmt == "flat-v1":
            del body[p]
        else:
            del body["nodes"][ni]["rows"][p]

    rows = all_rows()
    if typ == "a_row_removed":
        cands = [(ni, p) for (ni, p, (mu, k)) in rows if row_contrib_nonzero(mu, k)]
        ni, p = rng.choice(cands)
        rec["position"] = {"node": ni, "row": p, "removed": rows_lookup(rows, ni, p)}
        del_row(ni, p)
    elif typ == "b_k_changed":
        for _ in range(1000):
            ni, p, (mu, k) = rng.choice(rows)
            k2 = rng.choice([x for x in range(17) if x != k])
            m = sum(1 << i for i in mu)
            if bring.times_monomial(bring.add(Fk[k], Fk[k2]), m).size:
                break
        rec["position"] = {"node": ni, "row": p, "mu": mu, "k_from": k, "k_to": k2}
        set_row(ni, p, [mu, k2])
    elif typ == "c_mu_changed_same_degree":
        cands = [(ni, p, rw) for (ni, p, rw) in rows if len(rw[0]) >= 1]
        for _ in range(1000):
            ni, p, (mu, k) = rng.choice(cands)
            mu2 = sorted(rng.sample(range(18), len(mu)))
            if mu2 == sorted(mu):
                continue
            m1 = sum(1 << i for i in mu)
            m2 = sum(1 << i for i in mu2)
            d = bring.add(bring.times_monomial(Fk[k], m1), bring.times_monomial(Fk[k], m2))
            if d.size:
                break
        rec["position"] = {"node": ni, "row": p, "k": k, "mu_from": mu, "mu_to": mu2}
        set_row(ni, p, [mu2, k])
    elif typ == "d_transplant_same_arm":
        others = [x for x in arm_keys if x != key]
        target_key = rng.choice(others)
        rec["position"] = {"target_key": target_key}
    elif typ == "e_rule_b_mu3_sum_still_1":
        if key in flat3_by_key:
            body = {"D": 4, "nv": 18, "nodes": [{"id": 0, "rows": _deepcopy_body(flat3_by_key[key]), "prods": []}], "output": 0}
            rec["construction"] = "flat max|mu|=3 of same system rewritten as one-node wdag"
        else:
            mu3 = sorted(rng.sample(range(18), 3))
            k = rng.randrange(17)
            out_id = body["output"]
            nd = [n for n in body["nodes"] if n["id"] == out_id][0]
            nd["rows"] = nd.get("rows", []) + [[mu3, k], [mu3, k]]
            rec["construction"] = "doubled |mu|=3 row added to output node"
            rec["position"] = {"mu3": mu3, "k": k}
    elif typ == "f_rule_c_degree4_child":
        for _ in range(1000):
            mu2 = sorted(rng.sample(range(18), 2))
            k = rng.randrange(17)
            P = bring.times_monomial(Fk[k], sum(1 << i for i in mu2))
            if bring.degree(P) == 4:
                break
        j = rng.randrange(18)
        shift = {n["id"]: n["id"] + 1 for n in body["nodes"]}
        new_nodes = [{"id": 0, "rows": [[mu2, k]], "prods": []}]
        for n in body["nodes"]:
            new_nodes.append({"id": shift[n["id"]], "rows": n.get("rows", []),
                              "prods": [[jj, shift[cc]] for jj, cc in n.get("prods", [])]})
        out_id = shift[body["output"]]
        for n in new_nodes:
            if n["id"] == out_id:
                n["prods"] = n["prods"] + [[j, 0], [j, 0]]
        body = {"D": 4, "nv": 18, "nodes": new_nodes, "output": out_id}
        rec["position"] = {"child_rows": [[mu2, k]], "j": j, "child_degree": bring.degree(P)}
    elif typ == "g_rule_a_forward_reference":
        n = len(body["nodes"])
        if n >= 2:
            remap = {nd["id"]: n - 1 - nd["id"] for nd in body["nodes"]}
            new_nodes = [{"id": remap[nd["id"]], "rows": nd.get("rows", []),
                          "prods": [[jj, remap[cc]] for jj, cc in nd.get("prods", [])]} for nd in body["nodes"]]
            new_nodes.sort(key=lambda x: x["id"])
            body = {"D": 4, "nv": 18, "nodes": new_nodes, "output": remap[body["output"]]}
            rec["construction"] = "node ids reversed"
        else:
            k = rng.randrange(17)
            j = rng.randrange(18)
            body["nodes"].append({"id": 1, "rows": [[[], k]], "prods": []})
            body["nodes"][0]["prods"] = body["nodes"][0].get("prods", []) + [[j, 1], [j, 1]]
            rec["construction"] = "appended node referenced forward twice (cancels)"
    Ft = F_of(target_key)
    if fmt == "flat-v1":
        r = CC.check_flat(body, Ft)
        rec.update(verified=r["verified"], first_violated_rule=None if r["verified"] else "identity",
                   residual_size=r.get("residual_size"))
    else:
        r = CC.check_wdag(body, Ft)
        rec.update(verified=r["verified"], first_violated_rule=r.get("first_violated_rule"),
                   residual_size=r.get("residual_size"))
        # for the discipline controls, also record whether the algebra alone still reaches 1
        if typ in ("e_rule_b_mu3_sum_still_1", "f_rule_c_degree4_child", "g_rule_a_forward_reference"):
            r2 = CC.check_wdag(body, Ft, evaluate_even_if_a_fails=True)
            rec["algebra_output_is_1"] = r2["rules"].get("e") is True
            rec["rules"] = r2["rules"]
    rt = route_T(fmt, body, rec_primary_view(rec, fmt, body), FT_of(target_key))
    rec["route_T_verified"] = rt.get("route_T_verified")
    rec["routes_agree"] = rt.get("routes_agree")
    rec["rejected"] = not rec["verified"]
    rec["rejected_by_both_routes"] = (not rec["verified"]) and (rt.get("route_T_verified") is False)
    return rec


def rec_primary_view(rec, fmt, body):
    """Primary-route fields needed by route_T for a control record."""
    return {"verified": rec["verified"], "first_violated_rule": rec.get("first_violated_rule")}


def route_T(fmt, body, primary, FT):
    """Independent truth-table verdict; syntactic rules (a), (b) and format are
    re-derived here from the body, not taken from the primary route."""
    out = {}
    try:
        if fmt == "flat-v1":
            wf = isinstance(body, list) and all(
                isinstance(e, list) and len(e) == 2 and isinstance(e[1], int) and 0 <= e[1] < 17
                and isinstance(e[0], list) and len(set(e[0])) == len(e[0]) and all(isinstance(i, int) and 0 <= i < 18 for i in e[0])
                for e in body)
            ok = wf and TT.flat_identity(body, FT)
            out["route_T_verified"] = bool(ok)
        elif fmt == "wdag-v1":
            ids = [nd["id"] for nd in body["nodes"]]
            fmt_ok = body.get("D") == 4 and body.get("nv") == 18 and len(set(ids)) == len(ids) and body.get("output") in set(ids)
            a_ok = all(c < nd["id"] for nd in body["nodes"] for _, c in nd.get("prods", []))
            b_ok = all(len(mu) <= 2 and 0 <= k < 17 for nd in body["nodes"] for mu, k in nd.get("rows", []))
            sem = TT.wdag_semantic(body, FT) if a_ok else {"evaluated": False}
            ok = fmt_ok and a_ok and b_ok and sem.get("evaluated") and sem["rule_c_ok"] and sem["rule_d_ok"] and sem["output_is_1"]
            out["route_T_verified"] = bool(ok)
            if sem.get("evaluated"):
                out["route_T_node_degrees"] = sem.get("node_degrees")
                out["route_T_max_child_degree"] = sem.get("max_child_degree")
                if primary.get("node_degrees") is not None:
                    out["route_T_node_degrees_equal"] = sem.get("node_degrees") == primary.get("node_degrees")
        else:
            out["route_T_verified"] = False
    except Exception as ex:  # noqa
        out["route_T_verified"] = None
        out["route_T_error"] = repr(ex)
    out["routes_agree"] = out.get("route_T_verified") == bool(primary.get("verified"))
    return out


def ambiguity_list():
    """Every point where the frozen text left a choice, and the reading used."""
    return [
        {"id": "AMB-1", "topic": "fresh instance key format",
         "text": "specification instance_record says key \"<ARM>:<slot>\"; the task card says fresh keys are \"<ARM>:<slot>:<role>\"",
         "reading": "card's format. Two systems (unsat, sat) share a slot, so \"<ARM>:<slot>\" cannot be unique; every fresh key is checked to equal arm:slot:role and to resolve to exactly one system."},
        {"id": "AMB-2", "topic": "E_sha256 serialization",
         "text": "card: sha256(json.dumps(E_hex))",
         "reading": "Python json.dumps with default separators (', ') and default ensure_ascii, UTF-8 encoded; the E_hex list exactly as stored."},
        {"id": "AMB-3", "topic": "solution encoding",
         "text": "specification: solutions as 18-bit integers (bit order not stated)",
         "reading": "bit i of the integer = v_i (the evaluator's own assignment convention). Both this and the reversed order are tested and recorded per system."},
        {"id": "AMB-4", "topic": "flat-v1 sortedness and duplicates",
         "text": "C = sorted list of (mu as sorted index list, k)",
         "reading": "the certificate is verified iff every entry is well formed (mu distinct indices in 0..17, k in 0..16) and sum mu*f_k = 1 exactly in B. Unsorted C, unsorted mu or duplicate entries are recorded as format notes, not rejections (duplicates cancel mod 2 and do not change the identity)."},
        {"id": "AMB-5", "topic": "wdag-v1 D and nv",
         "text": "body carries \"D\": 4, \"nv\": 18; rules are stated with D",
         "reading": "D must equal 4 and nv 18 (the frozen values); otherwise format failure. Rules use D = 4 regardless of the body."},
        {"id": "AMB-6", "topic": "wdag-v1 node identity",
         "text": "nodes [{\"id\": i, ...}]; rule (a) child id c < i",
         "reading": "ids must be unique integers and output must be an id; rule (a) compares ids, not list positions; ids != 0..n-1 is recorded as a format note."},
        {"id": "AMB-7", "topic": "wdag-v1 rule (c) scope",
         "text": "every child c used in prods has deg poly(c) <= 3",
         "reading": "every node id that appears as c in any prods entry of any node; degree of the reduced multilinear polynomial; the zero polynomial has degree -1 and satisfies every bound."},
        {"id": "AMB-8", "topic": "what counts toward M_4",
         "text": "flat-v1 counts toward M_4 only with max |mu| <= 2; the plan's composition also names a one-node wdag-v1",
         "reading": "primary tally: verified flat-v1 lines with closure M_4 and max |mu| <= 2. Alternative tallies (any verified flat-v1 with max |mu| <= 2 regardless of closure label; any verified one-node wdag-v1 without prods) are reported beside it."},
        {"id": "AMB-9", "topic": "W_4 flat-v1 lines",
         "text": "flat-v1 never counts toward W_4 unless max |mu| <= 2; only wdag-v1 counts toward w",
         "reading": "W_4 flat-v1 lines are verified as identities and never counted toward w; those with max |mu| <= 2 are flagged flat_W4_eligible_maxmu_le2."},
        {"id": "AMB-10", "topic": "N-CONVL 'differ from B's own bits'",
         "reading": "the 17-bit constant column of the system differs from the constant column of E_S3(x_R) (= the bits of B). Additionally checked: the record's bprime equals the constant column, and the whole system equals own E_S3(x_R) with curve constant b'."},
        {"id": "AMB-11", "topic": "N-ELL144 'rows 0..15 inside U'",
         "reading": "support of row k (all 172 columns) is a subset of U_k for k = 0..15; row 16 equals exactly v_0 + v_9 + c with c the row's own constant, and c equals the record's c field. NELL-A20 is checked by the same structural rule (its source file is must_not_read here)."},
        {"id": "AMB-12", "topic": "xr144 order",
         "text": "U62 (listed order, ascending idx), then S62, then C20",
         "reading": "slots are the listed order of instance-sets.json sets U62, S62, C20; whether the listed order is ascending idx is checked and recorded."},
        {"id": "AMB-13", "topic": "multilinear reduction",
         "reading": "product of monomials = union of variable sets (v^2 = v); sums reduce multiplicities mod 2."},
        {"id": "AMB-14", "topic": "reading 'archived bytes at the archive commit'",
         "text": "reviewers read from a dedicated worktree at the archive commit",
         "reading": "VC-8 forbids git writes, so no worktree was created. Every input was read with `git show c7f5e3dfa:<path>` into a scratch root, and the run files' sha256 were compared with the TASK-20260924-40b2ca receipt."},
        {"id": "AMB-15", "topic": "negative control (e) where no max|mu|=3 flat exists for the system",
         "reading": "a row (mu3, k) with |mu3| = 3 is added twice to the output node, so the sum still reaches 1 and only rule (b) is violated."},
        {"id": "AMB-16", "topic": "VC-4 'at least 5 each'",
         "reading": "at least 5 corrupted certificates of EACH required type per (closure, arm, format) kind."},
    ]


def rows_lookup(rows, ni, p):
    for (a, b, rw) in rows:
        if a == ni and b == p:
            return rw
    return None


if __name__ == "__main__":
    main()
