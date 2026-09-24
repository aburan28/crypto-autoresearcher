"""Driver for the blind re-derivation TASK-20260924-1f6a3c (joint J5 of
REVIEW-CERTBIN-20260924-3d7e1a). Written from the two specifications' object
blocks, KN-TECH-b18366 and the task card alone.

Order of work (card BR-2, BR-6, BR-9):
  1. BR-2 self-tests (stop on any failure; nothing is computed on the inputs).
  2. Per instance: Q1-Q5 plus instrument cross-checks; one checkpoint file per
     instance under work/checkpoints/ (resume skips completed instances).
  3. wcerts.jsonl.gz, then the SEPARATE-PROCESS checker run over it, then
     rederivation.json, then seal.txt (sha256 of both + UTC time). report.yaml and
     attestation.yaml are written afterwards, by hand, never by this program.
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import boolsys as BS  # noqa: E402
import closure as CL  # noqa: E402
import gf2lin as GL  # noqa: E402
import selftest as ST  # noqa: E402
import sroutes as SR  # noqa: E402
import wcert_check as WC  # noqa: E402
import xcheck as XC  # noqa: E402

TASK = "TASK-20260924-1f6a3c"
Q5_LABELS = ["BI-00%d" % i for i in range(1, 9)]

ELIMINATION_METHOD = (
    "Primary engine (gf2lin.Space): incremental echelon basis over F_2 with Python-int "
    "bit vectors, keyed by leading bit; bit b = the monomial of rank b in ASCENDING "
    "degrevlex over all multilinear monomials (constant = bit 0), i.e. column c of M_D "
    "is bit C_D-1-c and the leading bit is the leading monomial in the spec's "
    "descending-degrevlex column order. Echelon (not reduced); rank = basis size; "
    "dim(X cap B_{<=d}) = #basis vectors with leading bit < N(d) (valid because the "
    "order is degree-graded); 1 in X iff a basis vector has leading bit 0. W_4 by the "
    "literal rule (closure.literal_closure): at every iteration the FULL echelon basis "
    "of W^(i) cap B_{<=3} (snapshotted at the start of the iteration) is multiplied by "
    "every v_j (numpy gather with multilinear reduction) and inserted. "
    "Independent cross-check (xcheck.XCheck, no shared code): packed uint64 numpy "
    "vectorised Gauss-Jordan to full RREF, own column order (degree descending, reverse "
    "combinations order within a degree), rows from the checker's hand-expanded "
    "equations; recomputes rank_3, rank_4, 1 in R_3/R_4, dim(R_4 cap B_{<=d}), the W_4 "
    "iterate dimensions, fixpoint index, first-one iteration and dim(W_4 cap B_{<=d}). "
    "Second cross-check (closure.complement_closure): same engine, different generating "
    "set (only vectors independent modulo rowspace(M_3)+previously multiplied); must "
    "reproduce every literal iterate dimension. M_5 (Q5): primary engine only.")

AMBIGUITIES = [
    {"id": "AMB-1", "clause": "card Q3 'the list dim W^(0), dim W^(1), ... up to the fixpoint; the fixpoint index'",
     "readings": ["list ends at dim W^(fix)", "list also contains dim W^(fix+1), the first repeated value"],
     "chosen": "the list contains dim W^(0) .. dim W^(fix+1); fixpoint_index = fix = the first i with dim W^(i+1) = dim W^(i), so W_4 = W^(fix)",
     "why": "keeps the stopping evidence in the record; either reading is recoverable from the other"},
    {"id": "AMB-2", "clause": "e94b27 object.mutant_closure_W_D 'A basis of W^(i) intersected with B_{<=D-1} is the set of RREF rows ... whose leading monomial has degree <= D-1' vs card BR-4 'b in a basis of W^(i) cap B_{<=3}'",
     "readings": ["RREF basis", "any basis"],
     "chosen": "echelon (non-reduced) basis rows with leading monomial of degree <= 3",
     "why": "both are bases of the same subspace W^(i) cap B_{<=3} (degree-graded order), so span{v_j b} and hence every W^(i+1) and every recorded quantity are identical; BR-1 allows any correct elimination"},
    {"id": "AMB-3", "clause": "card BR-4 'At EVERY iteration multiply a full basis of W^(i) cap B_{<=3}'",
     "readings": ["basis taken at the start of iteration i", "basis updated while products are being inserted"],
     "chosen": "snapshot at the start of iteration i; products of vectors that enter during iteration i are formed at iteration i+1",
     "why": "this is the definition W^(i+1) = W^(i) + span{v_j b : b in a basis of W^(i) cap B_{<=3}}; the fixpoint W_4 is the same either way, the per-iteration dimensions are those of the definition"},
    {"id": "AMB-4", "clause": "explicit-kind instances (blind-inputs.json kind 'explicit'); neither specification defines this kind",
     "readings": ["equations[k] is the set of monomials of f_k, summed over F_2, k = list position", "other encodings"],
     "chosen": "f_k = sum over F_2 of the monomials listed at position k (k = 0..16), each monomial an ascending variable-index list per blind-inputs 'monomial_encoding'; M_D, W_D and s built from these f_k with the identical conventions",
     "why": "the only reading consistent with the file's field names and monomial_encoding; checked: 17 lists per instance, ascending distinct indices in 0..17, no duplicate monomial, max degree 2"},
    {"id": "AMB-5", "clause": "card Q3 'the first iteration i with 1 in W^(i), or null'",
     "readings": ["counting from W^(0)", "counting from W^(1)"],
     "chosen": "counting from W^(0): i = 0 means 1 is already in rowspace(M_4)",
     "why": "matches the index of the dims list"},
    {"id": "AMB-6", "clause": "4e92d7 object.constant_in_row_space '1 in R_D iff the constant column (the last one) is a pivot column'",
     "readings": ["pivot column of the Stage-1 column pass", "1 in rowspace(M_D)"],
     "chosen": "1 in rowspace(M_D), computed as: the echelon basis has a vector with leading monomial 1",
     "why": "equivalent: the constant column is last, so it is a pivot column of any column-ordered forward elimination iff some row-space vector has its first nonzero column there, i.e. equals 1 (card BR-1: pivot rule does not affect membership of 1)"},
    {"id": "AMB-7", "clause": "card BR-5 validity 'every parent p in products is an EARLIER id'",
     "readings": ["earlier in the elements list", "numerically smaller id"],
     "chosen": "earlier in the elements list; ids are 0..n-1 in list order so both readings coincide; the checker enforces list order",
     "why": "list order is what a sequential verifier can check"},
    {"id": "AMB-8", "clause": "card BR-5 'every g_id has degree <= 4', 'every g_p used as a parent has degree <= 3'",
     "readings": ["degree of the zero polynomial undefined"],
     "chosen": "the zero polynomial has degree -1 (passes both bounds); no emitted element is zero",
     "why": "convention only"},
    {"id": "AMB-9", "clause": "card BR-3 route 2 'count solutions lying in V'",
     "readings": ["count of x_2 roots summed over x_1 in V", "count of distinct x_2"],
     "chosen": "s = #{(x_1, x_2) in V x V : S_3(x_1, x_2, x_R) = 0} = sum over x_1 in V of the number of roots x_2 in V; compared with route 1 as a set of assignments v = x_1 + 2^9 x_2",
     "why": "s is defined as a count of v in F_2^18, and v <-> (x_1, x_2) is a bijection"},
    {"id": "AMB-10", "clause": "curve coefficient A",
     "readings": ["A enters S_3", "A does not enter S_3"],
     "chosen": "A does not enter S_3 or the descended system (the formula has only B); A is used only in the BR-2 point-addition self-test on E_{A,B}",
     "why": "S_3 as written in KN-TECH-b18366 and 4e92d7 object.summation_polynomial; verified against point addition on E_{A,B}"},
    {"id": "AMB-11", "clause": "card Q5 'For BI-001..BI-008 only'",
     "readings": ["only curve-kind labels in that range", "every label in that range"],
     "chosen": "every label BI-001..BI-008, whatever its kind",
     "why": "the card names labels, not kinds"},
]

CONVENTIONS = {
    "field": "F_2[t]/(t^17 + t^3 + 1); element = 17-bit integer, bit j = coefficient of t^j",
    "variables": "v_0..v_17; x_1 = sum_{j<9} v_j t^j, x_2 = sum_{j<9} v_{9+j} t^j",
    "assignment_encoding": "an assignment v is the 18-bit integer with bit i = v_i, so x_1 = v & 511 and x_2 = v >> 9",
    "monomial_encoding": "ascending variable-index list; [] is the constant 1 (as blind-inputs.json)",
    "Macaulay_rows": "(mu, k), mu of degree <= D-2 ordered by (degree, lexicographic index tuple), row index = mu_index*17 + k, zero rows retained",
    "Macaulay_columns": "all multilinear monomials of degree <= D, descending degrevlex, constant last",
    "W4_dims": "dims[i] = dim W^(i) for i = 0..fixpoint_index+1; dims[fixpoint_index+1] == dims[fixpoint_index]",
}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, sort_keys=True, separators=(",", ":"))
    os.replace(tmp, path)


def eval_vector(MI, v, nbits):
    ev = 0
    for b in range(nbits):
        m = MI.mono[b]
        if m & v == m:
            ev |= 1 << b
    return ev


def nonvanishing(space, evs):
    bad = 0
    for ev in evs:
        for w in space.basis.values():
            if bin(w & ev).count("1") & 1:
                bad += 1
    return bad


def process_instance(inst, B, ctx):
    MI, M3, M4, M5, mult, X = ctx["MI"], ctx["M3"], ctx["M4"], ctx["M5"], ctx["mult"], ctx["X"]
    rec = {"label": inst["label"], "kind": inst["kind"]}
    T = {}
    checks = {}
    t0 = time.time()
    if inst["kind"] == "curve":
        xR = inst["x_R"]
        rec["x_R"] = xR
        eqs = BS.descended_equations(xR, B)
        heqs = WC.equations_curve(xR, B)
    else:
        eqs = BS.explicit_equations(inst["equations"])
        heqs = WC.equations_explicit(inst["equations"])
        checks["explicit_max_monomial_degree"] = max((BS.popcount(m) for e in eqs for m in e), default=-1)
    checks["engine_equations_equal_checker_equations"] = [set(e) for e in heqs] == eqs
    T["equations"] = time.time() - t0

    # ---- Q1
    t0 = time.time()
    s1, sols1 = SR.route1_exhaustive(eqs)
    q1 = {"s_route1_exhaustive": s1, "solutions_route1": sols1}
    if inst["kind"] == "curve":
        s2, sols2, bad = SR.route2_rootfinding(xR, B)
        q1.update({"s_route2_rootfinding": s2, "solutions_route2": sols2,
                   "routes_agree": (s1 == s2), "solution_sets_equal": (sols1 == sols2),
                   "route2_roots_failing_direct_S3_check": bad,
                   "degenerate": xR < 512})
    else:
        q1.update({"s_route2_rootfinding": None, "routes_agree": None, "degenerate": None,
                   "note": "explicit kind: exhaustive search only (card BR-3)"})
    rec["Q1"] = q1
    T["Q1"] = time.time() - t0

    # ---- Q2
    t0 = time.time()
    rows3 = M3.rows(eqs)
    rows4 = M4.rows(eqs)
    checks["M3_rows_equal_first_323_M4_rows"] = rows3 == rows4[:len(rows3)]
    S3 = GL.rank_of(rows3)
    S4 = GL.rank_of(rows4)
    rec["Q2"] = {"rank_3": S3.dim, "rank_4": S4.dim, "one_in_R3": S3.has_one(), "one_in_R4": S4.has_one(),
                 "dim_R4_cap_B_le_d": [S4.dim_below(MI.N[d]) for d in range(4)],
                 "shape_M3": [M3.R, M3.C], "shape_M4": [M4.R, M4.C]}
    T["Q2"] = time.time() - t0

    # ---- Q3 (literal)
    t0 = time.time()
    lit = CL.literal_closure(rows4, MI, 4, mult)
    rec["Q3"] = {"dims": lit["dims"], "fixpoint_index": lit["fixpoint_index"],
                 "first_one_iteration": lit["first_one_iteration"], "final_dim": lit["final_dim"],
                 "dim_W4_cap_B_le_d": lit["dim_cap"], "one_in_W4": lit["one_in_W"],
                 "multiplied_basis_sizes": lit["multiplied_basis_sizes"]}
    T["Q3"] = time.time() - t0

    # ---- cross-checks of Q2/Q3
    t0 = time.time()
    comp = CL.complement_closure(rows4, M4, MI, 4, mult)
    checks["complement_closure_dims_equal_literal"] = (comp["dims"] == lit["dims"]
                                                       and comp["first_one_iteration"] == lit["first_one_iteration"]
                                                       and comp["dim_cap"] == lit["dim_cap"])
    T["complement_closure"] = time.time() - t0
    t0 = time.time()
    x = X.run(heqs)
    eng = {"rank_3": S3.dim, "one_in_R3": S3.has_one(), "rank_4": S4.dim, "one_in_R4": S4.has_one(),
           "R4_cap_dims": rec["Q2"]["dim_R4_cap_B_le_d"], "W4_dims": lit["dims"],
           "W4_fixpoint_index": lit["fixpoint_index"], "W4_first_one_iteration": lit["first_one_iteration"],
           "W4_final_dim": lit["final_dim"], "W4_cap_dims": lit["dim_cap"]}
    checks["xcheck_independent_equal"] = (x == eng)
    if x != eng:
        checks["xcheck_values"] = x
    T["xcheck"] = time.time() - t0

    # soundness: every element of R_3, R_4, W_4 vanishes at every Boolean solution
    t0 = time.time()
    evs4 = [eval_vector(MI, v, MI.N[4]) for v in sols1]
    checks["nonvanishing_pairs_R3"] = nonvanishing(S3, evs4)
    checks["nonvanishing_pairs_R4"] = nonvanishing(S4, evs4)
    checks["nonvanishing_pairs_W4"] = nonvanishing(lit["space"], evs4)
    T["soundness"] = time.time() - t0

    # ---- Q4
    t0 = time.time()
    cert_rec = None
    if lit["one_in_W"]:
        ext = CL.extract_certificate(rows4, M4, MI, 4, mult)
        if ext["certificate"] is None:
            rec["Q4"] = {"status": "refuted, unwitnessed", "reason": "extraction reached a fixpoint without 1"}
        else:
            cert_rec = {"schema": "certbin.wcert.v1", "label": inst["label"], **ext["certificate"]}
            ok, reason, stats = WC.check(cert_rec, heqs)
            checks["certificate_level_dims_equal_literal_prefix"] = (
                ext["level_dims"] == lit["dims"][:len(ext["level_dims"])]
                and ext["levels_used"] == lit["first_one_iteration"])
            rec["Q4"] = {"status": "refuted, witnessed" if ok else "refuted, unwitnessed",
                         "check_in_process": {"accepted": ok, "reason": reason, **stats},
                         "certificate_levels": ext["levels_used"],
                         "elements_before_prune": ext["elements_before_prune"],
                         "elements_after_prune": ext["elements_after_prune"]}
    else:
        rec["Q4"] = {"status": "not refuted by W_4", "certificate": None}
    T["Q4"] = time.time() - t0

    # ---- Q5 (optional)
    if M5 is not None and inst["label"] in Q5_LABELS:
        t0 = time.time()
        S5 = GL.rank_of(M5.rows(eqs))
        rec["Q5"] = {"rank_5": S5.dim, "one_in_R5": S5.has_one(), "shape_M5": [M5.R, M5.C]}
        evs5 = [eval_vector(MI, v, MI.N[5]) for v in sols1]
        checks["nonvanishing_pairs_R5"] = nonvanishing(S5, evs5)
        T["Q5"] = time.time() - t0

    sat = s1 >= 1
    refuted_any = (rec["Q2"]["one_in_R3"] or rec["Q2"]["one_in_R4"] or rec["Q3"]["one_in_W4"]
                   or rec.get("Q5", {}).get("one_in_R5", False))
    checks["satisfiable_implies_not_refuted"] = (not sat) or (not refuted_any)
    checks["monotone_R3_R4_W4"] = ((not rec["Q2"]["one_in_R3"] or rec["Q2"]["one_in_R4"])
                                   and (not rec["Q2"]["one_in_R4"] or rec["Q3"]["one_in_W4"])
                                   and rec["Q3"]["dims"][0] == rec["Q2"]["rank_4"])
    rec["checks"] = checks
    rec["timings_s"] = {k: round(v, 3) for k, v in T.items()}
    return rec, cert_rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--no-q5", action="store_true")
    a = ap.parse_args()
    started = utcnow()
    t_start = time.time()
    out = os.path.abspath(a.outdir)
    work = os.path.join(out, "work")
    ckdir = os.path.join(work, "checkpoints")
    os.makedirs(ckdir, exist_ok=True)
    for f in ("rederivation.json", "wcerts.jsonl.gz", "seal.txt"):
        if os.path.exists(os.path.join(out, f)):
            sys.exit("refusing: %s already exists (sealed files are never overwritten)" % f)

    inp = json.load(open(a.inputs))
    assert inp["schema"] == "certbin.rc1.blind_inputs.v1"
    assert inp["field"]["n"] == 17 and inp["m"] == 2 and inp["l"] == 9
    A, B = inp["curve"]["A"], inp["curve"]["B"]

    # 1. self-tests
    MI = BS.MonomialIndex(4 if a.no_q5 else 5)
    print("[%s] self-tests start" % utcnow(), flush=True)
    st = ST.run_all(A, B, MI)
    atomic_json(os.path.join(work, "selftest-attempt-%d.json" % a.attempt), st)
    if not st["all_pass"]:
        print("SELF-TEST FAILURE: stopping before any instance (card BR-2)", flush=True)
        sys.exit(2)

    ctx = {"MI": MI, "M3": BS.Macaulay(3, MI), "M4": BS.Macaulay(4, MI),
           "M5": None if a.no_q5 else BS.Macaulay(5, MI),
           "mult": CL.Multiplier(MI, 4), "X": XC.XCheck(4)}

    # 2. instances
    labels = [i["label"] for i in inp["instances"]]
    missing = []
    for inst in inp["instances"]:
        lab = inst["label"]
        ck = os.path.join(ckdir, lab + ".json")
        if a.resume and os.path.exists(ck):
            continue
        t0 = time.time()
        try:
            rec, cert = process_instance(inst, B, ctx)
        except Exception as exc:  # infrastructure/implementation failure: never a result
            print("[%s] %s FAILED: %r" % (utcnow(), lab, exc), flush=True)
            missing.append({"label": lab, "reason": "exception: %r" % (exc,)})
            continue
        rec["wall_s"] = round(time.time() - t0, 3)
        rec["certificate"] = cert
        rec["attempt"] = a.attempt
        atomic_json(ck, rec)
        print("[%s] %s done in %.1fs" % (utcnow(), lab, rec["wall_s"]), flush=True)

    # 3. assemble
    instances = {}
    certs = []
    for lab in labels:
        ck = os.path.join(ckdir, lab + ".json")
        if not os.path.exists(ck):
            if not any(m["label"] == lab for m in missing):
                missing.append({"label": lab, "reason": "no checkpoint"})
            continue
        rec = json.load(open(ck))
        cert = rec.pop("certificate")
        if cert is not None:
            certs.append(cert)
        instances[lab] = rec

    wpath = os.path.join(out, "wcerts.jsonl.gz")
    with open(wpath, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            for c in certs:
                gz.write((json.dumps(c, separators=(",", ":")) + "\n").encode())

    # separate-process checker over the written file
    sep_out = os.path.join(work, "wcert-check-separate-process.json")
    cmd = [sys.executable, os.path.join(HERE, "wcert_check.py"), "--certs", wpath,
           "--inputs", os.path.abspath(a.inputs), "--out", sep_out]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    sep = json.load(open(sep_out)) if cp.returncode == 0 else {}
    for lab, rec in instances.items():
        if lab in sep:
            rec["Q4"]["check_separate_process"] = sep[lab]
            if not sep[lab]["accepted"]:
                rec["Q4"]["status"] = "refuted, unwitnessed"

    peak_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    import sympy
    env = {"python": sys.version, "numpy": np.__version__, "sympy": sympy.__version__,
           "platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count(),
           "address_space_limit_bytes": resource.getrlimit(resource.RLIMIT_AS)[0]}
    code_hashes = {f: sha256_file(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE)) if f.endswith(".py")}
    red = {
        "schema": "certbin.rc1.rederivation.v1",
        "task_id": TASK,
        "review_id": inp["review_id"],
        "joint": "J5",
        "inputs": {"path": os.path.relpath(os.path.abspath(a.inputs), os.path.abspath(os.path.join(HERE, "../../../../../.."))),
                   "sha256": sha256_file(a.inputs), "schema": inp["schema"]},
        "statement_sources": [
            "experiments/EXP-CERTBIN-e94b27/specification.yaml (object.ring, macaulay_M_D, mutant_closure_W_D)",
            "experiments/EXP-CERTBIN-4e92d7/specification.yaml (object.field, factor_base_subspace, unknowns, curve, summation_polynomial, descended_system, macaulay_matrix, constant_in_row_space)",
            "knowledge/techniques/KN-TECH-b18366.md (S_3 formula)",
            "ledger/handoffs/TASK-20260924-1f6a3c.yaml (quantities Q1-Q5, BR-1..BR-10)"],
        "conventions": CONVENTIONS,
        "elimination_method": ELIMINATION_METHOD,
        "ambiguities": AMBIGUITIES,
        "self_tests": st,
        "self_test_seed": ST.SELFTEST_SEED,
        "environment": env,
        "code_sha256": code_hashes,
        "command": " ".join(sys.argv),
        "attempt": a.attempt,
        "started_utc": started,
        "finished_utc": utcnow(),
        "wall_seconds_this_invocation": round(time.time() - t_start, 1),
        "peak_rss_mb": round(peak_rss_mb, 1),
        "instance_labels": labels,
        "missing_instances": missing,
        "wcert_separate_process_checker": {"command": " ".join(cmd), "returncode": cp.returncode,
                                           "stdout": cp.stdout.strip(), "stderr": cp.stderr.strip()[-2000:],
                                           "output": os.path.relpath(sep_out, out)},
        "instances": instances,
    }
    rpath = os.path.join(out, "rederivation.json")
    with open(rpath, "w") as fh:
        json.dump(red, fh, indent=1, sort_keys=False)

    # 4. seal
    seal = ("TASK-20260924-1f6a3c seal (card BR-6)\n"
            "sealed_utc: %s\n"
            "rederivation.json sha256: %s\n"
            "wcerts.jsonl.gz sha256: %s\n") % (utcnow(), sha256_file(rpath), sha256_file(wpath))
    with open(os.path.join(out, "seal.txt"), "w") as fh:
        fh.write(seal)
    print(seal, flush=True)
    print("missing instances:", len(missing), flush=True)


if __name__ == "__main__":
    main()
