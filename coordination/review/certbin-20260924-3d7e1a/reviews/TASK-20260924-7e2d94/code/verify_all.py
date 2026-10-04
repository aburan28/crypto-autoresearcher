"""J1 author-independent certificate verification for RUN-CERTBIN-c417e0.

TASK-20260924-7e2d94 (REVIEW-CERTBIN-20260924-3d7e1a, joint J1). Zero trials.

Usage (from the repository root):
  python3 coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-7e2d94/code/verify_all.py \
      --repo . --out coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-7e2d94/verification.json

Reads only: the certificates, instance-sets.json (keys, set membership and
archived.x_R; E_hex is never touched), the Stage-1 curve.json and
targets-F-S3.jsonl.gz, and systems/null-systems.json.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bring as R          # noqa: E402
import descent as D        # noqa: E402
import gf2n as F           # noqa: E402
import selftests as ST     # noqa: E402

RUN = "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
SRC = "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
REV = "coordination/review/certbin-20260924-3d7e1a"
P_CERTS = RUN + "/certificates.jsonl.gz"
P_SETS = RUN + "/instance-sets.json"
P_CURVE = SRC + "/curve.json"
P_TARGETS = SRC + "/targets-F-S3.jsonl.gz"
P_NULLS = REV + "/systems/null-systems.json"
P_RECEIPT = REV + "/archives/TASK-20260924-a4f217/snapshot-receipt.json"

MEM_CAP = 3 * 1024 ** 3
SET_FAMILY = {"U62": "F-S3", "S62": "F-S3", "C20": "F-S3", "N-AFF62": "F-AFF-1", "N-F262": "F-NULLF2"}
CURVE_SETS = ("U62", "S62", "C20")
NULL_SETS = ("N-AFF62", "N-F262")

AMBIGUITIES = [
    {"id": "AMB-1", "question": "degree of mu",
     "reading": "deg mu = number of distinct variable indices in the tuple. The format check requires strictly ascending indices in 0..17; a repeated index would be reported and reduced by v^2 = v (none expected)."},
    {"id": "AMB-2", "question": "semantics of C (a 'sorted list of pairs')",
     "reading": "The claim is checked as the literal sum over the listed pairs. Duplicate pairs are counted and reported (a duplicate would cancel in the sum). Sortedness is checked under Python list ordering of [mu, k] and reported; it is not a verification criterion."},
    {"id": "AMB-3", "question": "key-to-instance mapping",
     "reading": "key = set:family:idx. For F-S3 keys, idx is the Stage-1 F-S3 test-target idx; targets-F-S3.jsonl.gz has one record per (idx, D in {3,4}); x_R must be unique across those records and equal instance-sets.json archived.x_R of the same key. For null keys, the equations are null-systems.json[key]; its set/family/idx fields must match the key."},
    {"id": "AMB-4", "question": "variable order and field encoding",
     "reading": "Element <-> 17-bit int, bit j = coefficient of t^j. v_i <-> bit i of an 18-bit assignment/mask; x_1 = sum_{j<9} v_j t^j is the low 9 bits, x_2 = sum_{j<9} v_{9+j} t^j the next 9 bits. Variable order v_0 > ... > v_17 does not enter the identity check."},
    {"id": "AMB-5", "question": "null systems",
     "reading": "Taken as given in null-systems.json (each monomial an ascending index list, 17 equations). Their decoding from E_hex is the opening archive's step (PD-R2). Independently I check only structure (degree <= 2, valid indices, no duplicate monomial) and, as an extra, support containment in the union support U_k of the curve's affine basis E^0, E^j that MY descent derives (the F-NULLF2 and F-AFF-1 definitions of EXP-CERTBIN-4e92d7 imply containment)."},
    {"id": "AMB-6", "question": "VC-4 (c) 'one mu changed to another monomial of the same degree'",
     "reading": "A pair with deg mu >= 1 is chosen uniformly; mu' is drawn uniformly among monomials of the same degree in v_0..v_17 with mu' != mu and (mu', k) not already in C. A draw whose change (mu + mu') f_k is identically zero in B is mathematically vacuous (a correct verifier must accept it), so it is redrawn and counted."},
    {"id": "AMB-7", "question": "VC-4 (a),(b) vacuity",
     "reading": "(a) removes a pair chosen uniformly among pairs whose row mu f_k is nonzero in B (removing a zero row changes nothing). (b) replaces k by k' != k uniformly with (mu, k') not in C and mu (f_k + f_k') nonzero in B; vacuous draws are redrawn and counted. Vacuity is decided by truth-table evaluation over all 2^18 points, not by the monomial checkers."},
    {"id": "AMB-8", "question": "what 'max deg mu against its closure label' means for W_4",
     "reading": "Recorded only (VC-3); no judgement. M_5 rows are (mu, k) with deg mu <= D - 2 = 3, so every M_5 certificate must have max deg mu <= 3."},
    {"id": "AMB-9", "question": "VC-5 solution count",
     "reading": "s = number of v in F_2^18 at which all 17 of MY f_k vanish, by evaluation of my monomial f_k over all 2^18 points; for curve instances also by direct F_2^17 evaluation of S_3(x_1(v), x_2(v), x_R) (route-2 values). Run on every certified instance (not only 20) plus the 62 S62 instances as a positive control of the counter."},
    {"id": "AMB-10", "question": "VC-4 extra control (e)",
     "reading": "Not required by the card: every certificate is also transplanted onto a uniformly drawn S62 (satisfiable-by-set-definition) instance. Soundness forbids any certificate verifying there."},
]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canon_system(f):
    return hashlib.sha256(json.dumps([sorted(R.mask_to_list(m) for m in e) for e in f],
                                     separators=(",", ":")).encode()).hexdigest()


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (MEM_CAP, MEM_CAP))
    os.chdir(args.repo)
    t_start = time.time()
    timings = {}

    def tick(name, t0):
        timings[name] = round(time.time() - t0, 2)
        print(f"[{name}] {timings[name]} s, peak RSS {rss_mb():.0f} MB", flush=True)

    out = {
        "schema": "certbin.rc1.independent_verification.v1",
        "task_id": "TASK-20260924-7e2d94",
        "joint": "J1",
        "review_plan_id": "REVIEW-CERTBIN-20260924-3d7e1a",
        "experiment_id": "EXP-CERTBIN-e94b27",
        "run_id": "RUN-CERTBIN-c417e0",
        "trials": 0,
        "started_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", P_CERTS, P_SETS, P_CURVE, P_TARGETS, P_NULLS],
                               capture_output=True, text=True).stdout.strip()
    except Exception as e:  # pragma: no cover
        head, dirty = f"unavailable: {e}", "unknown"
    out["environment"] = {
        "python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(),
        "repository_head": head, "inputs_dirty_status": dirty or "clean (git status --porcelain empty for every input)",
        "command": " ".join([os.path.basename(sys.executable)] + sys.argv),
        "memory_cap_bytes_RLIMIT_AS": MEM_CAP,
    }
    out["code_sha256"] = {fn: sha256_file(os.path.join(HERE, fn)) for fn in sorted(os.listdir(HERE)) if fn.endswith(".py")}
    out["inputs_sha256"] = {p: sha256_file(p) for p in (P_CERTS, P_SETS, P_CURVE, P_TARGETS, P_NULLS, P_RECEIPT)}
    rec = json.load(open(P_RECEIPT))
    out["inputs_sha256_vs_a4f217_receipt"] = {
        P_NULLS: rec["path_sha256"].get(P_NULLS) == out["inputs_sha256"][P_NULLS]}
    prov = {}
    for p in (P_CERTS, P_SETS, P_CURVE, P_TARGETS, P_NULLS, P_RECEIPT):
        try:
            log = subprocess.run(["git", "log", "--format=%H %s", "--", p], capture_output=True, text=True).stdout.strip().splitlines()
            blob_head = subprocess.run(["git", "rev-parse", f"HEAD:{p}"], capture_output=True, text=True).stdout.strip()
            blob_wt = subprocess.run(["git", "hash-object", p], capture_output=True, text=True).stdout.strip()
            prov[p] = {"commits_touching": log, "blob_at_HEAD": blob_head, "working_file_blob": blob_wt,
                       "working_file_equals_HEAD": blob_head == blob_wt}
        except Exception as e:  # pragma: no cover
            prov[p] = {"error": str(e)}
    out["inputs_git_provenance"] = prov
    out["procedure_notes"] = [
        "A dry run of this code (identical except for the inputs_git_provenance and procedure_notes blocks, added afterwards) was written to the session scratchpad outside the repository before this file was produced; nothing in the verification logic, seeds or controls changed between the dry run and this run.",
        "instance-sets.json is read for key, family, idx, set membership and archived.x_R only; E_hex is not read by this code.",
    ]
    out["ambiguities"] = AMBIGUITIES

    # ------------------------------------------------------------------ self-tests
    t0 = time.time()
    curve_json = json.load(open(P_CURVE))
    st = {}
    st["ST-1_modulus_irreducible"] = ST.st_modulus()
    st["ST-2_field_axioms"] = ST.st_field_axioms()
    st["ST-3_trace_halftrace"] = ST.st_trace_halftrace()
    st4, E = ST.st_archived_curve(curve_json)
    st["ST-4_archived_curve"] = st4
    st["ST-5_group_law"] = ST.st_group_law(E, curve_json["order"])
    st["ST-6_S3_vs_point_addition"] = ST.st_s3_point_addition(E, curve_json)
    st7, (E0, Ej) = ST.st_descent_random(E)
    st["ST-7_descent_two_routes_random_xR"] = st7
    st["ST-8_boolean_ring"] = ST.st_boolean_ring()
    st["ST-9_checkers_synthetic"] = ST.st_checkers_synthetic()
    out["self_tests"] = st
    tick("self_tests", t0)
    selftests_pass = all(v["passed"] for v in st.values())

    # ------------------------------------------------------------------ inputs: sets, targets, nulls
    t0 = time.time()
    sets_json = json.load(open(P_SETS))
    membership = {}          # key -> set name
    set_keys = defaultdict(list)
    archived_xR = {}
    binding_findings = []
    for sname, lst in sets_json["sets"].items():
        for e in lst:
            key = e["key"]
            parts = key.split(":")
            if len(parts) != 3 or parts[0] != sname or parts[1] != e["family"] or int(parts[2]) != e["idx"]:
                binding_findings.append({"key": key, "finding": "instance-sets record fields disagree with its key"})
            if key in membership:
                binding_findings.append({"key": key, "finding": "key listed in two sets", "sets": [membership[key], sname]})
            membership[key] = sname
            set_keys[sname].append(key)
            archived_xR[key] = e["archived"]["x_R"]          # the only archived field read
    tgt_xR = defaultdict(set)
    tgt_D = defaultdict(list)
    with gzip.open(P_TARGETS, "rt") as fh:
        for line in fh:
            r = json.loads(line)
            tgt_xR[r["idx"]].add(r["x_R"])
            tgt_D[r["idx"]].append(r["D"])
    targets_summary = {"records": sum(len(v) for v in tgt_D.values()), "distinct_idx": len(tgt_D),
                       "idx_with_non_unique_xR": sorted(i for i, s in tgt_xR.items() if len(s) != 1),
                       "idx_D_multiset_not_3_4": sorted(i for i, d in tgt_D.items() if sorted(d) != [3, 4])}
    nulls_json = json.load(open(P_NULLS))
    null_keys = sorted(k for k in nulls_json if k != "convention")
    null_summary = {"convention_string": nulls_json.get("convention"), "n_systems": len(null_keys)}
    expected_null_keys = sorted(set_keys["N-AFF62"] + set_keys["N-F262"])
    null_summary["keys_equal_instance_sets_null_keys"] = (null_keys == expected_null_keys)
    tick("load_inputs", t0)

    # ------------------------------------------------------------------ construction
    t0 = time.time()
    systems = {}         # key -> dict(f, farr, tt, ...)
    construction = {}
    U_k = [set(E0[k]).union(*[Ej[j][k] for j in range(F.N)]) for k in range(F.N)]
    for sname in CURVE_SETS:
        for key in set_keys[sname]:
            idx = int(key.split(":")[2])
            xs = tgt_xR.get(idx, set())
            rec_c = {"set": sname, "idx": idx, "kind": "curve"}
            if len(xs) != 1:
                rec_c["binding"] = "FAIL: idx not found or x_R not unique in targets-F-S3"
                binding_findings.append({"key": key, "finding": rec_c["binding"]})
                construction[key] = rec_c
                continue
            xR = next(iter(xs))
            rec_c["x_R_from_targets_F_S3"] = xR
            rec_c["x_R_matches_instance_sets_archived"] = (xR == archived_xR[key])
            if xR != archived_xR[key]:
                binding_findings.append({"key": key, "finding": "x_R mismatch", "targets": xR, "instance_sets": archived_xR[key]})
            rec_c["x_R_in_V_degenerate"] = xR < (1 << 9)
            f1, _ = D.descend_symbolic(xR, E.B)
            f2, vals = D.descend_interpolation(xR, E.B)
            rec_c["route1_equals_route2"] = (f1 == f2)
            rec_c["affine_decomposition_holds"] = (f1 == ST.affine_combination(E0, Ej, xR))
            rec_c["max_degree"] = D.max_degree(f1)
            rec_c["terms_per_equation"] = [len(e) for e in f1]
            tt_mono = R.truth_tables(f1)
            tt_direct = R.truth_tables_from_values(vals)
            rec_c["truth_tables_mono_equal_direct"] = all(np.array_equal(a, b) for a, b in zip(tt_mono, tt_direct))
            rec_c["s_by_monomial_evaluation"] = R.count_solutions(tt_mono)
            rec_c["s_by_direct_S3_evaluation"] = int(np.count_nonzero(vals == 0))
            rec_c["system_sha256"] = canon_system(f1)
            systems[key] = {"f": f1, "farr": R.f_arrays(f1), "tt": tt_direct}
            construction[key] = rec_c
    for key in null_keys:
        e = nulls_json[key]
        sname = key.split(":")[0]
        rec_c = {"set": sname, "idx": e.get("idx"), "kind": "null"}
        ok_fields = (e.get("set") == sname and e.get("family") == key.split(":")[1] and e.get("idx") == int(key.split(":")[2]))
        rec_c["entry_fields_match_key"] = ok_fields
        if not ok_fields:
            binding_findings.append({"key": key, "finding": "null-systems entry fields disagree with key"})
        rec_c["in_instance_sets_under_same_set"] = (membership.get(key) == sname)
        eqs = e["equations"]
        probs = []
        if len(eqs) != 17:
            probs.append(f"n_equations={len(eqs)}")
        f = []
        for k, eq in enumerate(eqs):
            s = set()
            for mono in eq:
                m, pr = R.mask_of(mono)
                probs += [f"eq{k}:{p}" for p in pr]
                if R.popcount(m) > 2:
                    probs.append(f"eq{k}:degree>2")
                if m in s:
                    probs.append(f"eq{k}:duplicate_monomial")
                s ^= {m}
            f.append(frozenset(s))
        rec_c["format_problems"] = sorted(set(probs))
        rec_c["max_degree"] = D.max_degree(f)
        rec_c["terms_per_equation"] = [len(x) for x in f]
        rec_c["support_within_union_support_U_k"] = all(f[k] <= U_k[k] for k in range(len(f)))
        tt = R.truth_tables(f)
        rec_c["s_by_monomial_evaluation"] = R.count_solutions(tt)
        rec_c["system_sha256"] = canon_system(f)
        systems[key] = {"f": f, "farr": R.f_arrays(f), "tt": tt}
        construction[key] = rec_c
    null_summary["union_support_sizes_U_k"] = [len(u) for u in U_k]
    null_summary["all_supports_within_U_k"] = all(construction[k]["support_within_union_support_U_k"] for k in null_keys)
    tick("construction", t0)

    # ------------------------------------------------------------------ certificates
    t0 = time.time()
    certs = []
    with gzip.open(P_CERTS, "rt") as fh:
        for line in fh:
            if line.strip():
                certs.append(json.loads(line))
    cert_records = []
    parsed = []
    seen_kc = Counter()
    for ci, c in enumerate(certs):
        key = c.get("key")
        rec = {"line": ci, "key": key, "closure": c.get("closure"), "form": c.get("form")}
        parts = key.split(":") if isinstance(key, str) else []
        sname = parts[0] if len(parts) == 3 else None
        rec["set"] = sname
        rec["key_fields_consistent"] = (len(parts) == 3 and c.get("set") == parts[0] and c.get("family") == parts[1]
                                        and c.get("idx") == int(parts[2]) and SET_FAMILY.get(parts[0]) == parts[1])
        rec["key_in_instance_sets_named_set"] = (membership.get(key) == sname)
        seen_kc[(key, c.get("closure"))] += 1
        if c.get("form") != "flat" or key not in systems:
            rec["verified"] = None
            rec["infrastructure_gap"] = ("form not flat: not supported by this verifier" if c.get("form") != "flat"
                                         else "no system constructed for key")
            cert_records.append(rec)
            parsed.append(None)
            continue
        Cm = []
        probs = []
        degs = Counter()
        for pair in c["C"]:
            mu, k = pair[0], pair[1]
            m, pr = R.mask_of(mu)
            probs += pr
            if not isinstance(k, int) or k < 0 or k > 16:
                probs.append("k_out_of_range")
                continue
            Cm.append((m, k))
            degs[R.popcount(m)] += 1
        dup = len(Cm) - len(set(Cm))
        rec["C_size"] = len(c["C"])
        rec["declared_size"] = c.get("size")
        rec["declared_size_matches"] = (c.get("size") == len(c["C"]))
        rec["max_deg_mu"] = max(degs) if degs else None
        rec["declared_max_deg_mu"] = c.get("max_deg_mu")
        rec["declared_max_deg_mu_matches"] = (c.get("max_deg_mu") == rec["max_deg_mu"])
        rec["deg_mu_histogram"] = {str(d): degs[d] for d in sorted(degs)}
        ks = sorted({k for _, k in Cm})
        rec["distinct_k_used"] = len(ks)
        rec["k_not_used"] = [k for k in range(17) if k not in ks]
        rec["duplicate_pairs"] = dup
        rec["C_sorted_python_order"] = (c["C"] == sorted(c["C"]))
        rec["format_problems"] = sorted(set(probs))
        S = systems[key]
        f, farr, tt = S["f"], S["farr"], S["tt"]
        rec["max_row_degree"] = max((max((R.popcount(mu | t) for t in f[k]), default=-1) for mu, k in Cm), default=None)
        rec["zero_rows_in_C"] = sum(1 for mu, k in Cm if R.vanishes_identically(mu, tt[k]))
        resA = R.residual_A(Cm, f)
        resB = R.residual_B(Cm, farr)
        okC, accC = R.check_C(Cm, tt)
        okA = resA == {0}
        okB = resB == {0}
        rec["checker_A_literal"] = okA
        rec["checker_B_numpy"] = okB
        rec["checker_C_pointwise_2^18"] = okC
        rec["checkers_agree"] = (okA == okB == okC) and resA == resB and np.array_equal(R.eval_poly(resA), accC)
        rec["verified"] = bool(okA and okB and okC and rec["checkers_agree"])
        if rec["closure"] == "M_5":
            rec["M5_max_deg_mu_le_3"] = (rec["max_deg_mu"] is not None and rec["max_deg_mu"] <= 3)
        if not rec["verified"]:
            res = sorted(resA, key=lambda m: (-R.popcount(m), m))
            rec["residual_size"] = len(resA)
            rec["residual_five_monomials"] = [R.mask_to_list(m) for m in res[:5]]
            rec["residual_contains_constant"] = 0 in resA
        cert_records.append(rec)
        parsed.append(Cm)
    tick("verify_certificates", t0)
    dup_kc = [{"key": k, "closure": cl, "count": n} for (k, cl), n in seen_kc.items() if n > 1]

    # ------------------------------------------------------------------ per (closure, set) table
    table = {}
    kinds = sorted({(r["closure"], r["set"]) for r in cert_records})
    for cl, sname in kinds:
        rs = [r for r in cert_records if r["closure"] == cl and r["set"] == sname]
        sizes = sorted(r.get("C_size") for r in rs if r.get("C_size") is not None)
        md = Counter(r.get("max_deg_mu") for r in rs)
        entry = {
            "submitted": len(rs),
            "verified": sum(1 for r in rs if r.get("verified") is True),
            "rejected": sum(1 for r in rs if r.get("verified") is False),
            "not_checked_infrastructure_gap": sum(1 for r in rs if r.get("verified") is None),
            "rejected_keys": [r["key"] for r in rs if r.get("verified") is False],
            "max_deg_mu_distribution": {str(k): v for k, v in sorted(md.items(), key=lambda x: (x[0] is None, x[0]))},
            "C_size_distribution": {
                "min": sizes[0] if sizes else None, "q1": sizes[len(sizes) // 4] if sizes else None,
                "median": sizes[len(sizes) // 2] if sizes else None, "q3": sizes[(3 * len(sizes)) // 4] if sizes else None,
                "max": sizes[-1] if sizes else None, "mean": round(sum(sizes) / len(sizes), 2) if sizes else None,
                "all_sorted": sizes},
            "max_row_degree_distribution": dict(Counter(str(r.get("max_row_degree")) for r in rs)),
            "distinct_k_used_distribution": dict(Counter(str(r.get("distinct_k_used")) for r in rs)),
            "declared_fields_mismatch": sum(1 for r in rs if not (r.get("declared_size_matches") and r.get("declared_max_deg_mu_matches"))),
            "format_problem_certificates": sum(1 for r in rs if r.get("format_problems")),
            "duplicate_pair_certificates": sum(1 for r in rs if r.get("duplicate_pairs")),
            "zero_rows_total": sum(r.get("zero_rows_in_C", 0) for r in rs),
            "unsorted_C_certificates": sum(1 for r in rs if r.get("C_sorted_python_order") is False),
        }
        if cl == "M_5":
            entry["M5_all_max_deg_mu_le_3"] = all(r.get("M5_max_deg_mu_le_3") for r in rs)
        table[f"{cl}|{sname}"] = entry

    # ------------------------------------------------------------------ VC-4 negative controls
    t0 = time.time()
    rng, nseed = ST.rng_for("VC-4 negative controls")
    nc_records = []

    def run_checks(Cm, S):
        a = R.residual_A(Cm, S["f"]) == {0}
        b = R.residual_B(Cm, S["farr"]) == {0}
        c = R.check_C(Cm, S["tt"])[0]
        return a, b, c

    s62_keys = set_keys["S62"]
    for ci, (c, rec) in enumerate(zip(certs, cert_records)):
        Cm = parsed[ci]
        if Cm is None or not rec.get("verified"):
            continue
        key = rec["key"]
        S = systems[key]
        tt = S["tt"]
        Cset = set(Cm)
        kind = f"{rec['closure']}|{rec['set']}"
        # (a) one pair removed
        nz = [i for i, (mu, k) in enumerate(Cm) if not R.vanishes_identically(mu, tt[k])]
        i = int(nz[int(rng.integers(0, len(nz)))])
        Ca = Cm[:i] + Cm[i + 1:]
        a, b, cc = run_checks(Ca, S)
        nc_records.append({"cert_line": ci, "key": key, "kind": kind, "type": "a_pair_removed",
                           "position": i, "pair": [R.mask_to_list(Cm[i][0]), Cm[i][1]], "redraws": 0,
                           "A_rejects": not a, "B_rejects": not b, "C_rejects": not cc})
        # (b) one k changed
        redraws = 0
        while True:
            i = int(rng.integers(0, len(Cm)))
            mu, k = Cm[i]
            k2 = int(rng.integers(0, 16))
            k2 = k2 if k2 < k else k2 + 1
            if (mu, k2) not in Cset and np.any(R.eval_mono(mu) & (tt[k] ^ tt[k2])):
                break
            redraws += 1
        Cb = list(Cm)
        Cb[i] = (mu, k2)
        a, b, cc = run_checks(Cb, S)
        nc_records.append({"cert_line": ci, "key": key, "kind": kind, "type": "b_k_changed",
                           "position": i, "pair": [R.mask_to_list(mu), k], "new_k": k2, "redraws": redraws,
                           "A_rejects": not a, "B_rejects": not b, "C_rejects": not cc})
        # (c) one mu changed to another monomial of the same degree
        redraws = 0
        pos = [j for j, (m_, _) in enumerate(Cm) if R.popcount(m_) >= 1]
        while True:
            i = int(pos[int(rng.integers(0, len(pos)))])
            mu, k = Cm[i]
            d = R.popcount(mu)
            idx = rng.choice(18, size=d, replace=False)
            mu2 = 0
            for x in idx.tolist():
                mu2 |= 1 << x
            if mu2 != mu and (mu2, k) not in Cset and np.any((R.eval_mono(mu) ^ R.eval_mono(mu2)) & tt[k]):
                break
            redraws += 1
        Cc = list(Cm)
        Cc[i] = (mu2, k)
        a, b, cc = run_checks(Cc, S)
        nc_records.append({"cert_line": ci, "key": key, "kind": kind, "type": "c_mu_changed_same_degree",
                           "position": i, "pair": [R.mask_to_list(mu), k], "new_mu": R.mask_to_list(mu2),
                           "redraws": redraws, "A_rejects": not a, "B_rejects": not b, "C_rejects": not cc})
        # (d) transplant onto a different instance of the same set
        pool = [k_ for k_ in set_keys[rec["set"]] if k_ != key and k_ in systems]
        tkey = pool[int(rng.integers(0, len(pool)))]
        a, b, cc = run_checks(Cm, systems[tkey])
        nc_records.append({"cert_line": ci, "key": key, "kind": kind, "type": "d_transplant_same_set",
                           "target_key": tkey,
                           "target_system_differs": construction[tkey]["system_sha256"] != construction[key]["system_sha256"],
                           "A_rejects": not a, "B_rejects": not b, "C_rejects": not cc})
        # (e) extra: transplant onto a satisfiable S62 instance
        tkey = s62_keys[int(rng.integers(0, len(s62_keys)))]
        a, b, cc = run_checks(Cm, systems[tkey])
        nc_records.append({"cert_line": ci, "key": key, "kind": kind, "type": "e_transplant_onto_S62_satisfiable",
                           "target_key": tkey, "target_s": construction[tkey]["s_by_monomial_evaluation"],
                           "A_rejects": not a, "B_rejects": not b, "C_rejects": not cc})
    for r in nc_records:
        r["rejected_by_all_three"] = r["A_rejects"] and r["B_rejects"] and r["C_rejects"]
        r["checkers_agree"] = r["A_rejects"] == r["B_rejects"] == r["C_rejects"]
    nc_table = {}
    for r in nc_records:
        t = nc_table.setdefault(r["kind"], {}).setdefault(r["type"], {"n": 0, "rejected_by_all_three": 0, "not_rejected": [], "redraws_total": 0})
        t["n"] += 1
        t["rejected_by_all_three"] += int(r["rejected_by_all_three"])
        t["redraws_total"] += r.get("redraws", 0)
        if not r["rejected_by_all_three"]:
            t["not_rejected"].append({"cert_line": r["cert_line"], "key": r["key"]})
    tick("negative_controls", t0)

    # ------------------------------------------------------------------ VC-5 sanity
    certified_keys = sorted({r["key"] for r in cert_records if r.get("verified")})
    vc5 = []
    for key in sorted(set(certified_keys) | set(s62_keys)):
        cr = construction[key]
        e = {"key": key, "set": cr["set"], "kind": cr["kind"], "s_monomial": cr["s_by_monomial_evaluation"],
             "has_verified_certificate": key in certified_keys}
        if cr["kind"] == "curve":
            e["s_direct_S3"] = cr["s_by_direct_S3_evaluation"]
        vc5.append(e)
    vc5_violations = [e for e in vc5 if e["has_verified_certificate"] and (e["s_monomial"] != 0 or e.get("s_direct_S3", 0) != 0)]
    s62_zero = [e["key"] for e in vc5 if e["set"] == "S62" and (e["s_monomial"] == 0 or e.get("s_direct_S3") == 0)]
    route_disagree = [e["key"] for e in vc5 if e["kind"] == "curve" and e["s_monomial"] != e["s_direct_S3"]]
    vc5_summary = {
        "certified_instances_counted": len(certified_keys),
        "certified_curve_instances": sum(1 for k in certified_keys if construction[k]["kind"] == "curve"),
        "certified_null_instances": sum(1 for k in certified_keys if construction[k]["kind"] == "null"),
        "verified_certificate_on_instance_with_s_ge_1": [e["key"] for e in vc5_violations],
        "positive_control_S62_instances": len(s62_keys),
        "positive_control_S62_with_s_zero": s62_zero,
        "curve_s_monomial_vs_direct_disagree": route_disagree,
        "per_instance": vc5,
    }

    # ------------------------------------------------------------------ binding summary
    curve_cert_keys = sorted({r["key"] for r in cert_records if r["set"] in CURVE_SETS})
    null_cert_keys = sorted({r["key"] for r in cert_records if r["set"] in NULL_SETS})
    binding = {
        "findings": binding_findings,
        "targets_F_S3": targets_summary,
        "null_systems": null_summary,
        "certificate_keys_curve": len(curve_cert_keys),
        "certificate_keys_null": len(null_cert_keys),
        "curve_keys_xR_mismatch": [k for k in curve_cert_keys if not construction.get(k, {}).get("x_R_matches_instance_sets_archived", False)],
        "curve_keys_degenerate": [k for k in curve_cert_keys if construction.get(k, {}).get("x_R_in_V_degenerate")],
        "null_keys_missing_from_null_systems": [k for k in null_cert_keys if k not in nulls_json],
        "certificate_key_fields_inconsistent": [r["key"] for r in cert_records if not r["key_fields_consistent"]],
        "certificate_key_not_in_named_set": [r["key"] for r in cert_records if not r["key_in_instance_sets_named_set"]],
        "duplicate_key_closure_lines": dup_kc,
        "E_hex_used": False,
    }
    construction_checks = {
        "curve_instances_constructed": sum(1 for v in construction.values() if v["kind"] == "curve"),
        "null_instances_constructed": sum(1 for v in construction.values() if v["kind"] == "null"),
        "curve_route1_ne_route2": [k for k, v in construction.items() if v["kind"] == "curve" and not v.get("route1_equals_route2", False)],
        "curve_affine_decomposition_fail": [k for k, v in construction.items() if v["kind"] == "curve" and not v.get("affine_decomposition_holds", False)],
        "curve_truth_tables_mono_ne_direct": [k for k, v in construction.items() if v["kind"] == "curve" and not v.get("truth_tables_mono_equal_direct", False)],
        "any_degree_above_2": [k for k, v in construction.items() if v.get("max_degree", 0) > 2],
        "null_format_problems": {k: v["format_problems"] for k, v in construction.items() if v["kind"] == "null" and v["format_problems"]},
    }

    # ------------------------------------------------------------------ VC-7 mechanical reading (pre-seal)
    n_ver = sum(1 for r in cert_records if r.get("verified") is True)
    n_rej = sum(1 for r in cert_records if r.get("verified") is False)
    n_gap = sum(1 for r in cert_records if r.get("verified") is None)
    m5_ok = all(r.get("M5_max_deg_mu_le_3", True) for r in cert_records if r["closure"] == "M_5")
    nc_ok = all(r["rejected_by_all_three"] for r in nc_records)
    nc_min = min((t["n"] for kd in nc_table.values() for t in kd.values()), default=0)
    construction_ok = (selftests_pass and not construction_checks["curve_route1_ne_route2"]
                       and not construction_checks["curve_affine_decomposition_fail"]
                       and not construction_checks["curve_truth_tables_mono_ne_direct"]
                       and not construction_checks["any_degree_above_2"] and not vc5_summary["verified_certificate_on_instance_with_s_ge_1"])
    mapping_ok = not (binding["findings"] or binding["curve_keys_xR_mismatch"] or binding["null_keys_missing_from_null_systems"]
                      or binding["certificate_key_fields_inconsistent"] or binding["certificate_key_not_in_named_set"])
    if n_rej == 0 and n_gap == 0 and m5_ok and nc_ok and construction_ok and mapping_ok:
        reading = "holds"
    elif n_rej > 0 and construction_ok and mapping_ok:
        reading = "breaks"
    else:
        reading = "inconclusive"
    out["vc7_mechanical_reading_pre_seal"] = {
        "reading": reading,
        "note": "Pre-seal mechanical reading of VC-7 from this file alone. The J1 verdict of record is in validation-report.yaml, which additionally checks, after the seal, that the certified (instance, closure) set is the one MR1-MR4 count.",
        "certificates_total": len(cert_records), "verified": n_ver, "rejected": n_rej, "infrastructure_gap": n_gap,
        "rejected_keys": [(r["key"], r["closure"]) for r in cert_records if r.get("verified") is False],
        "all_M5_max_deg_mu_le_3": m5_ok, "all_negative_controls_rejected": nc_ok,
        "min_negative_controls_per_kind_and_type": nc_min,
        "self_tests_all_pass": selftests_pass, "construction_checks_pass": construction_ok, "mapping_checks_pass": mapping_ok,
    }
    out["instance_binding"] = binding
    out["construction_checks"] = construction_checks
    out["per_closure_set"] = table
    out["certificates"] = cert_records
    out["negative_controls"] = {
        "seed_rule": "first 8 bytes (big-endian) of sha256('TASK-20260924-7e2d94|VC-4 negative controls'), numpy.random.Generator(PCG64(seed)); certificates visited in file order; per certificate one control of each type a, b, c, d, e in that order",
        "seed": nseed,
        "types": {"a_pair_removed": "AMB-7", "b_k_changed": "AMB-7", "c_mu_changed_same_degree": "AMB-6",
                  "d_transplant_same_set": "uniform over the other keys of the same set",
                  "e_transplant_onto_S62_satisfiable": "AMB-10 (extra)"},
        "per_kind_and_type": nc_table,
        "total": len(nc_records),
        "all_rejected_by_all_three_checkers": nc_ok,
        "records": nc_records,
    }
    out["vc5_sanity"] = vc5_summary
    out["construction"] = construction
    out["resources"] = {"wall_seconds_total": round(time.time() - t_start, 2), "phase_seconds": timings,
                        "peak_rss_mb": round(rss_mb(), 1), "cpu_user_seconds": round(resource.getrusage(resource.RUSAGE_SELF).ru_utime, 2)}
    out["finished_utc"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = args.out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, args.out)
    print(json.dumps(out["vc7_mechanical_reading_pre_seal"], indent=1))


if __name__ == "__main__":
    main()
