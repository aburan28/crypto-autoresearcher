"""
EXP-MONO-0e6e8f -- UNCONDITIONED five-class Chebotarev census of the m=4
symmetric-base Semaev cover.

Relationship to EXP-MONO-815525
-------------------------------
This script contains NO new Q_e(T) construction.  It imports
EXP-MONO-815525's own `run_census.py` BY FILE PATH (read-only, unmodified,
never copied) and uses its already-independently-verified primitives:

    compile_s4 / compile_s3 / compile_sym   S_4, S_3, Q_e monomial tables
    qe_from_sym                             symmetric-base Q_e(T) (fast path)
    qe_from_ordered                         ordered-base S_4 path
    qe_from_resultant                       runtime Sylvester elimination path
    F3, pt_add, pt_neg, points_with_x,      F_{p^3} + curve arithmetic
    curve_order, j_invariant
    factor_pattern, pgcd, pnorm, pdeg, ...  F_p[T] toolkit (DDF/Yun)

EXP-MONO-815525's `derive_s4.py` is NOT imported: importing it re-executes the
sympy derivation and REWRITES files inside EXP-MONO-815525/implementation/,
which this task forbids.  It is instead bound by sha256 and its outputs are
re-verified at runtime (Stage 0) through three mutually independent paths and
against ordinary elliptic-curve point arithmetic.

THE CRITICAL DESIGN DIFFERENCE FROM EXP-MONO-815525
---------------------------------------------------
EXP-MONO-815525 conditioned on "g is irreducible over F_p", which its own
red-team null-object control proved has zero discriminating power.  THIS
SCRIPT APPLIES NO FILTER ON g's FACTORIZATION TYPE.  The one and only
exclusion is the degenerate case Res(g, f) = 0 (g and f = X^3 + A X + B share
a root), which is counted and disclosed, never silently dropped.

Stage 0  re-verify the reused construction (loads, degree law, symmetry,
         split-g point-arithmetic baseline, three-path agreement).
Stage 1  unconditioned census: exhaustive over ALL of F_p^3 at p = 101,
         uniform seeded random sampling at p = 1009.
Stage 2  five-class distribution, chi-square against the pre-registered full
         S_4 Chebotarev density, and the per-subgroup existence checks --
         reported as SEPARATE results, never merged into one verdict.

No CAS at runtime.  No network.  Single worker.
"""
import hashlib
import json
import os
import random
import resource
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.abspath(os.path.join(
    HERE, "..", "..", "EXP-MONO-815525", "implementation"))

sys.path.insert(0, PRIOR)
import run_census as RC  # noqa: E402  (EXP-MONO-815525's own module, unmodified)

# ------------------------------------------------------------------ constants
SEED = 20260904003                     # specification.yaml replication.seeds[0]
RANDOM_SAMPLES_PER_CURVE = 100000      # spec minimum is 10000
BUDGET_WALL_S = 1200.0
EXAMPLES_PER_CLASS = 60                # bounded per-instance record retention

# 2 primes in [101, 2000]; 2 curves per prime, pairwise non-isogenous within a
# prime (distinct traces of Frobenius).  All ordinary, j not in {0, 1728}.
CURVES = [
    {"id": "C1", "p": 101,  "A": 2, "B": 3,  "mode": "exhaustive"},
    {"id": "C2", "p": 101,  "A": 1, "B": 35, "mode": "exhaustive"},
    {"id": "C3", "p": 1009, "A": 5, "B": 7,  "mode": "random"},
    {"id": "C4", "p": 1009, "A": 2, "B": 30, "mode": "random"},
]

# Pre-registered full-S_4 Chebotarev density (specification.yaml stage_2).
S4_DENSITY = {"1^4": 1.0 / 24, "2+2": 1.0 / 8, "2+1+1": 1.0 / 4,
              "4": 1.0 / 4, "3+1": 1.0 / 3}
CLASSES = ["1^4", "2+2", "2+1+1", "4", "3+1"]

# Cycle types realised by each transitive subgroup of S_4, as partitions of 4.
# (The transitive subgroups of S_4 are exactly C_4, V_4, D_4, A_4, S_4.)
SUBGROUPS = {
    "S_4": {"order": 24, "realised": {"1^4", "2+2", "2+1+1", "4", "3+1"}},
    "A_4": {"order": 12, "realised": {"1^4", "2+2", "3+1"}},
    "D_4": {"order": 8,  "realised": {"1^4", "2+2", "2+1+1", "4"}},
    "C_4": {"order": 4,  "realised": {"1^4", "2+2", "4"}},
    "V_4": {"order": 4,  "realised": {"1^4", "2+2"}},
}

PARTITION_LABEL = {
    (1, 1, 1, 1): "1^4",
    (1, 1, 2): "2+1+1",
    (2, 2): "2+2",
    (1, 3): "3+1",
    (4,): "4",
}


def log(m):
    print(m, flush=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


# --------------------------------------------------------------- resultant
def resultant(a, b, p):
    """Res(a, b) in F_p for a, b in F_p[X], by the Euclidean algorithm with
    full leading-coefficient bookkeeping.  Independent of RC.pgcd; the two are
    cross-checked against each other on every draw (Res == 0 <=> deg gcd > 0).
    """
    a = RC.pnorm(a[:], p)
    b = RC.pnorm(b[:], p)
    if not a or not b:
        return 0
    res = 1
    while RC.pdeg(b) > 0:
        da, db = RC.pdeg(a), RC.pdeg(b)
        r = RC.pdivmod(a, b, p)[1]
        if da % 2 and db % 2:
            res = (-res) % p
        if not r:
            return 0
        res = res * pow(b[-1], da - RC.pdeg(r), p) % p
        a, b = b, r
    if RC.pdeg(b) < 0 or not b:
        return 0
    return res * pow(b[0], RC.pdeg(a), p) % p


# --------------------------------------------------------------- classification
def classify_fibre(qe, p):
    """Five-class label for one specialised Q_e(T).

    `affine`      literal F_p-irreducible factor degrees of Q_e(T).
    `projective`  the same, with (4 - deg Q_e) roots at T = infinity restored
                  as F_p-rational points of the degree-4 fibre.  Because
                  Q_e's leading coefficient c_4(e1,e2,e3) can vanish (a
                  measure-zero locus already disclosed as an anomaly by
                  EXP-MONO-815525), the AFFINE degree is not always 4 while
                  the FIBRE always has 4 points in P^1.  The Frobenius cycle
                  type of the cover is the PROJECTIVE one, so that is the
                  primary five-class label; the affine one is reported too.
    `squarefree`  False => the fibre is ramified at this base point and does
                  not carry a well-defined Frobenius conjugacy class.  Counted
                  and disclosed separately; never dropped.
    """
    deg = RC.pdeg(qe)
    if deg < 0:                       # Q_e identically zero
        return None
    aff = RC.factor_pattern(qe, p) if deg > 0 else []
    proj = tuple(sorted([1] * max(0, 4 - deg) + aff))
    sqfree = None
    if deg > 0:
        d = RC.pderiv(qe, p)
        sqfree = bool(d) and RC.pdeg(RC.pgcd(qe, d, p)) == 0
    else:
        sqfree = True
    return {
        "degree_in_T": deg,
        "roots_at_infinity": max(0, 4 - deg),
        "affine_degrees": aff,
        "affine_pattern": "+".join(str(x) for x in aff) if aff else "(none)",
        "projective_degrees": list(proj),
        "class": PARTITION_LABEL[proj],
        "squarefree": sqfree,
    }


# --------------------------------------------------------------- chi-square
def chisq(counts, total):
    """Pearson goodness-of-fit against S4_DENSITY.  4 degrees of freedom
    (5 classes, no fitted parameters)."""
    terms = {}
    stat = 0.0
    for c in CLASSES:
        exp = S4_DENSITY[c] * total
        obs = counts.get(c, 0)
        t = (obs - exp) ** 2 / exp if exp > 0 else float("nan")
        terms[c] = {"observed": obs, "expected": round(exp, 4),
                    "term": round(t, 6)}
        stat += t
    return {"statistic": round(stat, 6), "degrees_of_freedom": 4,
            "terms": terms, "n": total,
            "critical_value_0.05_df4": 9.4877,
            "critical_value_0.01_df4": 13.2767}


# ================================================================== STAGE 0
def stage_0(meta, compiled, rng):
    """Re-run EXP-MONO-815525's OWN construction-verification checks, on this
    experiment's curves, using its own imported code."""
    log("\n--- STAGE 0: re-verification of the reused EXP-MONO-815525 construction ---")
    s0 = {"reused_files": {}, "checks": {}}

    for fn in ("derive_s4.py", "run_census.py", "derivation_checks.json",
               "s3_monomials.json", "s4_monomials.json",
               "s4_symmetric_coeffs.json"):
        s0["reused_files"][fn] = sha256(os.path.join(PRIOR, fn))
    s0["prior_derivation_checks"] = json.load(
        open(os.path.join(PRIOR, "derivation_checks.json")))
    log("  reused artifact sha256: %s" % json.dumps(s0["reused_files"], indent=2))
    log("  prior derivation_checks.json: %s" % s0["prior_derivation_checks"])

    # (0a) the STORED S_4 monomial table itself: total degree 4 in each x_i,
    # and invariance under all 24 permutations of x1..x4.  This re-verifies
    # derive_s4.py's own symbolic claims WITHOUT re-running sympy and WITHOUT
    # trusting derivation_checks.json.
    terms = {tuple(int(t) for t in k.split(",")): co
             for k, co in RC.S4T["terms"].items()}
    degs = [max(k[i] for k in terms) for i in range(4)]
    import itertools
    sym_ok = True
    for perm in itertools.permutations(range(4)):
        permuted = {}
        for k, co in terms.items():
            nk = tuple(k[perm[i]] for i in range(4)) + k[4:]
            permuted[nk] = permuted.get(nk, 0) + co
        permuted = {k: v for k, v in permuted.items() if v}
        if permuted != {k: v for k, v in terms.items() if v}:
            sym_ok = False
    s0["checks"]["a_stored_S4_table_degree_4_in_each_x"] = {
        "degrees": degs, "pass": bool(degs == [4, 4, 4, 4])}
    s0["checks"]["a2_stored_S4_table_symmetric_under_all_24_perms"] = {
        "pass": bool(sym_ok), "n_terms": len(terms)}
    log("  (0a) stored S_4 table degrees in x1..x4 = %s -> %s" % (degs, degs == [4, 4, 4, 4]))
    log("  (0a2) stored S_4 table invariant under all 24 permutations: %s" % sym_ok)

    # (0b) S_3 vanishes on x(P +- Q) computed by ordinary point arithmetic.
    inst = []
    for C in meta:
        p, A, B = C["p"], C["A"], C["B"]
        s3tab = compiled[C["id"]][1]
        pts = [q for q in RC.points_with_x(p, A, B, range(2, min(p, 400)))
               if q is not None and q[1] != 0][:6]
        ok = True
        n = 0
        for i in range(len(pts)):
            for k in range(i + 1, len(pts)):
                P, Q = pts[i], pts[k]
                for sgn in (1, -1):
                    R = RC.pt_add(p, A, P, Q if sgn == 1 else RC.pt_neg(p, Q))
                    if R is None:
                        continue
                    v = 0
                    for (a, b, c), co in s3tab:
                        v += co * pow(P[0], a, p) % p * pow(Q[0], b, p) % p \
                             * pow(R[0], c, p)
                    n += 1
                    if v % p != 0:
                        ok = False
        inst.append({"curve": C["id"], "pass": ok, "n_relations": n})
        log("  (0b) S_3 vanishes on all x(P +- Q) for %s: %s (%d relations)"
            % (C["id"], ok, n))
    s0["checks"]["b_S3_against_group_law"] = {
        "instances": inst, "pass": all(i["pass"] for i in inst)}

    # (0c) split-g baseline: on base points whose three x's are x-coordinates of
    # real curve points, Q_e's roots are exactly the finite sign-class sums
    # x(P1 +- P2 +- P3); and deg Q_e = 4 - #(sign classes at infinity).
    binst, ainst = [], []
    for C in meta:
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        pts = [q for q in RC.points_with_x(p, A, B, range(2, p))
               if q is not None and q[1] != 0]
        tested, idx = 0, 0
        while tested < 60 and idx + 3 <= len(pts):
            P1, P2, P3 = pts[idx], pts[idx + 1], pts[idx + 2]
            idx += 1
            xs = [P1[0], P2[0], P3[0]]
            if len(set(xs)) != 3:
                continue
            e1 = sum(xs) % p
            e2 = (xs[0] * xs[1] + xs[0] * xs[2] + xs[1] * xs[2]) % p
            e3 = (xs[0] * xs[1] * xs[2]) % p
            sums = []
            for s2 in (1, -1):
                for s3 in (1, -1):
                    Rk = RC.pt_add(p, A, P1, P2 if s2 == 1 else RC.pt_neg(p, P2))
                    Rk = RC.pt_add(p, A, Rk, P3 if s3 == 1 else RC.pt_neg(p, P3))
                    sums.append("INF" if Rk is None else Rk[0])
            qe = RC.qe_from_sym(symtab, p, e1, e2, e3)
            n_inf = sums.count("INF")
            deg = RC.pdeg(qe)
            ainst.append({"curve": C["id"], "e": [e1, e2, e3],
                          "degree_in_T": deg, "n_at_infinity": n_inf,
                          "pass": bool(deg == 4 - n_inf)})
            finite = [r for r in sums if r != "INF"]
            target = [1]
            for r in finite:
                target = RC.pmul(target, [(-r) % p, 1], p)
            if deg != len(finite):
                bpass = False
            else:
                lead = qe[-1]
                monic = [c * pow(lead, -1, p) % p for c in qe]
                bpass = bool(monic == target)
            # split-g cross-check of the ordered-base path against the
            # symmetric-base path, with the three F_p roots embedded as
            # constants of F_p[X]/(g).
            F = RC.F3(p, e1, e2, e3)
            ordered = RC.qe_from_ordered(
                s4tab, F, (xs[0], 0, 0), (xs[1], 0, 0), (xs[2], 0, 0))
            ofp = RC.to_fp(ordered, p)
            xpass = bool(ofp is not None and RC.pnorm(ofp[:], p) == qe)
            binst.append({"curve": C["id"], "e": [e1, e2, e3], "xs": xs,
                          "signed_sums": sums, "pass": bpass,
                          "ordered_path_agrees": xpass})
            tested += 1
        log("  (0c) split-g baseline probes on %s: %d" % (C["id"], tested))
    s0["checks"]["c_specialised_degree_law"] = {
        "n": len(ainst), "pass": all(i["pass"] for i in ainst),
        "n_with_a_sign_class_at_infinity":
            sum(1 for i in ainst if i["n_at_infinity"] > 0),
        "instances": ainst}
    s0["checks"]["d_split_g_root_baseline"] = {
        "n": len(binst), "pass": all(i["pass"] for i in binst),
        "ordered_path_agrees_pass": all(i["ordered_path_agrees"] for i in binst),
        "instances": binst}
    log("  (0c) deg Q_e == 4 - #(sign classes at infinity) on %d probes: %s"
        % (len(ainst), s0["checks"]["c_specialised_degree_law"]["pass"]))
    log("  (0d) Q_e roots == finite sign-class sums on %d probes: %s "
        "(ordered-base path agrees: %s)"
        % (len(binst), s0["checks"]["d_split_g_root_baseline"]["pass"],
           s0["checks"]["d_split_g_root_baseline"]["ordered_path_agrees_pass"]))

    # (0e) symmetry + three-path agreement on g-irreducible probes.  This uses
    # a SEPARATE random stream and is a Stage-0 probe only: it is NOT a
    # Stage-1 filter and no Stage-1 base point is selected by it.
    einst = []
    for C in meta:
        p, A, B = C["p"], C["A"], C["B"]
        s4tab, s3tab, symtab = compiled[C["id"]]
        got, tries = 0, 0
        while got < 10 and tries < 20000:
            tries += 1
            e1, e2, e3 = rng.randrange(p), rng.randrange(p), rng.randrange(p)
            g = [(-e3) % p, e2 % p, (-e1) % p, 1]
            if not RC.is_irreducible_cubic(g, p):
                continue
            got += 1
            F = RC.F3(p, e1, e2, e3)
            X1 = (0, 1, 0)
            X2 = F.pw(X1, p)
            X3 = F.pw(X2, p)
            perms = [(X1, X2, X3), (X2, X3, X1), (X3, X1, X2),
                     (X2, X1, X3), (X1, X3, X2), (X3, X2, X1)]
            vals = [RC.qe_from_ordered(s4tab, F, *pm) for pm in perms]
            perm_ok = all(v == vals[0] for v in vals)
            rational = RC.to_fp(vals[0], p)
            fast = RC.qe_from_sym(symtab, p, e1, e2, e3)
            resu = RC.to_fp(RC.qe_from_resultant(s3tab, F, X1, X2, X3), p)
            agree = bool(rational is not None
                         and RC.pnorm(rational[:], p) == fast
                         and resu is not None
                         and RC.pnorm(resu[:], p) == fast)
            einst.append({"curve": C["id"], "e": [e1, e2, e3],
                          "permutation_invariant": bool(perm_ok),
                          "lands_in_Fp": bool(rational is not None),
                          "three_paths_agree": agree})
        log("  (0e) symmetry / three-path probes on %s: %d" % (C["id"], got))
    s0["checks"]["e_symmetry_and_three_path_agreement"] = {
        "n": len(einst),
        "pass": all(i["permutation_invariant"] and i["lands_in_Fp"]
                    and i["three_paths_agree"] for i in einst),
        "instances": einst}
    log("  (0e) permutation-invariant, F_p-rational, three paths agree: %s"
        % s0["checks"]["e_symmetry_and_three_path_agreement"]["pass"])

    # (0f) the local resultant implementation, cross-checked against RC.pgcd.
    ok = True
    for C in meta:
        p, A, B = C["p"], C["A"], C["B"]
        f = RC.pnorm([B, A, 0, 1], p)
        for _ in range(2000):
            e1, e2, e3 = rng.randrange(p), rng.randrange(p), rng.randrange(p)
            g = [(-e3) % p, e2 % p, (-e1) % p, 1]
            if (resultant(g, f, p) == 0) != (RC.pdeg(RC.pgcd(g, f, p)) > 0):
                ok = False
    s0["checks"]["f_resultant_agrees_with_gcd_test"] = {"pass": bool(ok),
                                                        "n_per_curve": 2000}
    log("  (0f) Res(g,f)==0  <=>  deg gcd(g,f)>0 on 2000 probes/curve: %s" % ok)

    s0["all_pass"] = bool(
        s0["checks"]["a_stored_S4_table_degree_4_in_each_x"]["pass"]
        and s0["checks"]["a2_stored_S4_table_symmetric_under_all_24_perms"]["pass"]
        and s0["checks"]["b_S3_against_group_law"]["pass"]
        and s0["checks"]["c_specialised_degree_law"]["pass"]
        and s0["checks"]["d_split_g_root_baseline"]["pass"]
        and s0["checks"]["d_split_g_root_baseline"]["ordered_path_agrees_pass"]
        and s0["checks"]["e_symmetry_and_three_path_agreement"]["pass"]
        and s0["checks"]["f_resultant_agrees_with_gcd_test"]["pass"])
    log("STAGE 0 OVERALL: %s" % ("PASS" if s0["all_pass"] else "FAIL"))
    return s0


# ================================================================== STAGE 1
def census_curve(C, compiled, rng):
    p, A, B = C["p"], C["A"], C["B"]
    s4tab, s3tab, symtab = compiled[C["id"]]
    f = RC.pnorm([B, A, 0, 1], p)

    counts = {c: 0 for c in CLASSES}
    affine_counts = {}
    g_type_counts = {}
    joint = {}
    ramified = {c: 0 for c in CLASSES}
    deg_counts = {}
    examples = {c: [] for c in CLASSES}
    excluded = []
    n_excluded = 0
    n_zero_qe = 0
    n_kept = 0
    n_drawn = 0

    def handle(e1, e2, e3):
        nonlocal n_excluded, n_zero_qe, n_kept
        g = [(-e3) % p, e2 % p, (-e1) % p, 1]
        r = resultant(g, f, p)
        if r == 0:
            n_excluded += 1
            if len(excluded) < 400:
                excluded.append({"e": [e1, e2, e3],
                                 "gcd_degree": RC.pdeg(RC.pgcd(g, f, p))})
            return
        qe = RC.qe_from_sym(symtab, p, e1, e2, e3)
        cl = classify_fibre(qe, p)
        if cl is None:
            n_zero_qe += 1
            return
        n_kept += 1
        k = cl["class"]
        counts[k] += 1
        affine_counts[cl["affine_pattern"]] = \
            affine_counts.get(cl["affine_pattern"], 0) + 1
        deg_counts[cl["degree_in_T"]] = deg_counts.get(cl["degree_in_T"], 0) + 1
        if not cl["squarefree"]:
            ramified[k] += 1
        gt = "+".join(str(d) for d in RC.factor_pattern(g, p))
        g_type_counts[gt] = g_type_counts.get(gt, 0) + 1
        jk = gt + " | " + k
        joint[jk] = joint.get(jk, 0) + 1
        if len(examples[k]) < EXAMPLES_PER_CLASS:
            rec = dict(cl)
            rec.update({"e1": e1, "e2": e2, "e3": e3,
                        "Qe_coeffs_low_to_high": qe,
                        "g_factor_type": gt, "resultant_g_f": r})
            examples[k].append(rec)

    if C["mode"] == "exhaustive":
        for e1 in range(p):
            for e2 in range(p):
                for e3 in range(p):
                    n_drawn += 1
                    handle(e1, e2, e3)
    else:
        for _ in range(RANDOM_SAMPLES_PER_CURVE):
            n_drawn += 1
            handle(rng.randrange(p), rng.randrange(p), rng.randrange(p))

    return {
        "curve": C["id"], "p": p, "A": A, "B": B, "mode": C["mode"],
        "n_base_points_drawn": n_drawn,
        "n_excluded_resultant_zero": n_excluded,
        "n_Qe_identically_zero": n_zero_qe,
        "n_classified": n_kept,
        "class_counts": counts,
        "class_counts_ramified_subset": ramified,
        "affine_pattern_counts": affine_counts,
        "degree_in_T_counts": {str(k): v for k, v in sorted(deg_counts.items())},
        "g_factor_type_counts": g_type_counts,
        "joint_g_type_by_class_counts": joint,
        "excluded_examples": excluded,
        "class_examples": examples,
    }


# ================================================================== main
def main():
    out_path = sys.argv[1]
    rng = random.Random(SEED)
    report = {"experiment_id": "EXP-MONO-0e6e8f",
              "run_id": "RUN-MONO-0e6e8f-1",
              "seed": SEED,
              "reused_construction_from": "EXP-MONO-815525/implementation",
              "sampling_rule": (
                  "UNCONDITIONED: (e1,e2,e3) taken exhaustively over all of "
                  "F_p^3 (p=101 curves) or drawn uniformly and independently "
                  "from F_p^3 (p=1009 curves). NO filter on g's factorization "
                  "type. The sole exclusion is Res(g,f)=0."),
              }
    log("=== EXP-MONO-0e6e8f / RUN-MONO-0e6e8f-1 ===")
    log("seed=%d  samples_per_random_curve=%d" % (SEED, RANDOM_SAMPLES_PER_CURVE))

    # ---- curve admissibility + isogeny disclosure
    meta = []
    for C in CURVES:
        p, A, B = C["p"], C["A"], C["B"]
        disc = (4 * A ** 3 + 27 * B ** 2) % p
        j = RC.j_invariant(p, A, B)
        n = RC.curve_order(p, A, B)
        t = p + 1 - n
        meta.append(dict(C, j_invariant=j, order=n, trace=t,
                         cm_discriminant_t2_minus_4p=t * t - 4 * p,
                         nonsingular=bool(disc != 0),
                         ordinary=bool(t % p != 0),
                         j_not_special=bool(j not in (0, 1728 % p))))
        log("curve %s: p=%d A=%d B=%d j=%s #E=%d t=%d t^2-4p=%d ordinary=%s j_ok=%s"
            % (C["id"], p, A, B, j, n, t, t * t - 4 * p,
               meta[-1]["ordinary"], meta[-1]["j_not_special"]))
    report["curves"] = meta

    # Tate: two curves over the SAME F_p are isogenous iff #E is equal
    # (equivalently equal trace).  Curves over different primes are over
    # different fields and are not isogenous at all.
    iso = []
    for i in range(len(meta)):
        for k in range(i + 1, len(meta)):
            a, b = meta[i], meta[k]
            same_field = a["p"] == b["p"]
            isog = bool(same_field and a["trace"] == b["trace"])
            iso.append({"pair": [a["id"], b["id"]], "same_field": same_field,
                        "traces": [a["trace"], b["trace"]],
                        "orders": [a["order"], b["order"]],
                        "cm_discriminants": [a["cm_discriminant_t2_minus_4p"],
                                             b["cm_discriminant_t2_minus_4p"]],
                        "isogenous_over_Fp": isog})
    report["isogeny_check"] = {
        "criterion": ("Tate: E1 ~ E2 over F_p  <=>  #E1(F_p) = #E2(F_p)  <=>  "
                      "equal trace of Frobenius. Curves over different primes "
                      "live over different fields and are not isogenous."),
        "pairs": iso,
        "any_isogenous_pair": any(x["isogenous_over_Fp"] for x in iso)}
    for x in iso:
        log("isogeny check %s-%s: same_field=%s traces=%s -> isogenous=%s"
            % (x["pair"][0], x["pair"][1], x["same_field"], x["traces"],
               x["isogenous_over_Fp"]))

    if not all(m["ordinary"] and m["j_not_special"] and m["nonsingular"]
               for m in meta):
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "curve_admissibility"
        json.dump(report, open(out_path, "w"), indent=1)
        return 2
    if report["isogeny_check"]["any_isogenous_pair"]:
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "isogenous_curve_pair_declared"
        json.dump(report, open(out_path, "w"), indent=1)
        return 2

    compiled = {C["id"]: (RC.compile_s4(C["p"], C["A"], C["B"]),
                          RC.compile_s3(C["p"], C["A"], C["B"]),
                          RC.compile_sym(C["p"], C["A"], C["B"]))
                for C in meta}

    # ---------------- STAGE 0
    s0 = stage_0(meta, compiled, rng)
    report["stage_0"] = s0
    if not s0["all_pass"]:
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "stage_0_reverification_failed"
        json.dump(report, open(out_path, "w"), indent=1)
        return 3

    # ---------------- STAGE 1
    log("\n--- STAGE 1: UNCONDITIONED five-class census ---")
    per_curve = []
    for C in meta:
        t = time.time()
        r = census_curve(C, compiled, rng)
        r["wall_seconds"] = round(time.time() - t, 2)
        per_curve.append(r)
        log("  %s (p=%d, %s): drawn=%d excluded_Res0=%d classified=%d  [%.1fs]"
            % (C["id"], C["p"], C["mode"], r["n_base_points_drawn"],
               r["n_excluded_resultant_zero"], r["n_classified"],
               r["wall_seconds"]))
        log("      classes: %s" % json.dumps(
            {k: r["class_counts"][k] for k in CLASSES}))
        log("      g factor types: %s" % json.dumps(r["g_factor_type_counts"]))
        log("      deg_T Q_e: %s" % json.dumps(r["degree_in_T_counts"]))
        log("      ramified (non-squarefree Q_e): %s"
            % json.dumps(r["class_counts_ramified_subset"]))
        if time.time() - T0 > BUDGET_WALL_S:
            log("  WALL BUDGET EXCEEDED -- stopping")
            report["budget_exceeded"] = True
            break
    report["stage_1"] = {"per_curve": per_curve}

    pooled = {c: sum(r["class_counts"][c] for r in per_curve) for c in CLASSES}
    pooled_ram = {c: sum(r["class_counts_ramified_subset"][c] for r in per_curve)
                  for c in CLASSES}
    n_tot = sum(pooled.values())
    n_exc = sum(r["n_excluded_resultant_zero"] for r in per_curve)
    n_drawn = sum(r["n_base_points_drawn"] for r in per_curve)
    n_zero = sum(r["n_Qe_identically_zero"] for r in per_curve)
    report["stage_1"]["pooled"] = {
        "n_base_points_drawn": n_drawn,
        "n_excluded_resultant_zero": n_exc,
        "n_Qe_identically_zero": n_zero,
        "n_classified": n_tot,
        "class_counts": pooled,
        "class_frequencies": {c: round(pooled[c] / n_tot, 8) for c in CLASSES},
        "class_counts_ramified_subset": pooled_ram,
        "accounting_check": bool(n_drawn == n_tot + n_exc + n_zero),
    }
    log("\n  POOLED: drawn=%d excluded=%d zeroQe=%d classified=%d  accounting=%s"
        % (n_drawn, n_exc, n_zero, n_tot,
           report["stage_1"]["pooled"]["accounting_check"]))
    for c in CLASSES:
        log("    %-6s %10d  freq=%.6f   (S_4 predicts %.6f)"
            % (c, pooled[c], pooled[c] / n_tot, S4_DENSITY[c]))

    # ---------------- STAGE 2
    log("\n--- STAGE 2: pre-registered comparison ---")
    s2 = {"predicted_S4_density": S4_DENSITY}

    # (M3) chi-square -- REPORTED SEPARATELY FROM (M1).
    s2["M3_chi_square_pooled"] = chisq(pooled, n_tot)
    s2["M3_chi_square_per_curve"] = {
        r["curve"]: chisq(r["class_counts"], r["n_classified"])
        for r in per_curve}
    log("  M3 chi-square (pooled, df=4): %.6f   [0.05 crit 9.4877, 0.01 crit 13.2767]"
        % s2["M3_chi_square_pooled"]["statistic"])
    for k, v in s2["M3_chi_square_per_curve"].items():
        log("     %s: chi2=%.6f  n=%d" % (k, v["statistic"], v["n"]))

    # descriptive secondary: the squarefree (unramified) subset only.
    sqf = {c: pooled[c] - pooled_ram[c] for c in CLASSES}
    n_sqf = sum(sqf.values())
    s2["M3b_chi_square_squarefree_subset_descriptive"] = chisq(sqf, n_sqf)
    s2["M3b_note"] = ("Descriptive secondary, NOT the pre-registered statistic. "
                      "Chebotarev density is a statement about unramified "
                      "fibres; the pre-registered M3 above is computed on ALL "
                      "classified instances and is the one that scores the "
                      "contract.")
    log("  M3b chi-square on the squarefree (unramified) subset only "
        "[DESCRIPTIVE]: %.6f  n=%d"
        % (s2["M3b_chi_square_squarefree_subset_descriptive"]["statistic"], n_sqf))

    # Descriptive diagnostic, declared before the full-scale run was executed.
    # RATIONALE: two of the four curves are censused EXHAUSTIVELY over all of
    # F_p^3, so their chi-square is not a sampling test at all -- it measures
    # the Chebotarev ERROR TERM at a small prime, which is O(p^{-1/2}) by
    # Weil, and grows without bound as n grows for any fixed nonzero bias.
    # The pre-registered M3 above is reported unchanged and unadjusted; this
    # block is an additional disclosure, not a substitute for it.
    s2["M3c_frequency_deviation_diagnostic"] = {
        "note": ("Descriptive. |observed - predicted| per class, pooled and "
                 "per curve, with the deviation rescaled by sqrt(p) to show "
                 "it against the Weil-size Chebotarev error term. Does NOT "
                 "replace or adjust the pre-registered M3."),
        "pooled": {c: {"observed_frequency": round(pooled[c] / n_tot, 8),
                       "predicted": round(S4_DENSITY[c], 8),
                       "abs_deviation": round(abs(pooled[c] / n_tot
                                                  - S4_DENSITY[c]), 8)}
                   for c in CLASSES},
        "per_curve": {
            r["curve"]: {
                "p": r["p"], "n": r["n_classified"], "mode": r["mode"],
                "classes": {
                    c: {"observed_frequency":
                            round(r["class_counts"][c] / r["n_classified"], 8),
                        "abs_deviation":
                            round(abs(r["class_counts"][c] / r["n_classified"]
                                      - S4_DENSITY[c]), 8),
                        "abs_deviation_times_sqrt_p":
                            round(abs(r["class_counts"][c] / r["n_classified"]
                                      - S4_DENSITY[c]) * r["p"] ** 0.5, 6)}
                    for c in CLASSES}}
            for r in per_curve}}
    log("  M3c deviation diagnostic [DESCRIPTIVE]: %s"
        % json.dumps({c: s2["M3c_frequency_deviation_diagnostic"]["pooled"][c]
                      ["abs_deviation"] for c in CLASSES}))

    # (M1) per-subgroup existence checks -- REPORTED SEPARATELY FROM (M3).
    subs = {}
    for name, G in SUBGROUPS.items():
        impossible = [c for c in CLASSES if c not in G["realised"]]
        found = {c: pooled[c] for c in impossible if pooled[c] > 0}
        subs[name] = {
            "order": G["order"],
            "cycle_types_realised": sorted(G["realised"]),
            "classes_this_subgroup_predicts_impossible": impossible,
            "observed_counts_in_predicted_impossible_classes":
                {c: pooled[c] for c in impossible},
            "falsified_by_observed_presence": bool(found),
            "witness_classes": sorted(found),
            "witness_examples": {
                c: [{k: ex[k] for k in ("e1", "e2", "e3",
                                        "Qe_coeffs_low_to_high",
                                        "projective_degrees", "class",
                                        "squarefree", "g_factor_type")}
                    for r in per_curve for ex in r["class_examples"][c][:1]][:2]
                for c in sorted(found)},
        }
        log("  M1 %-4s (order %2d): impossible classes %-20s observed %-28s -> falsified=%s"
            % (name, G["order"], impossible,
               json.dumps({c: pooled[c] for c in impossible}), bool(found)))
    s2["M1_per_subgroup_existence_checks"] = subs
    s2["M1_note"] = ("Each entry is an INDEPENDENT existence check. A subgroup "
                     "is falsified as the monodromy group iff at least one "
                     "observed instance lies in a class that subgroup cannot "
                     "realise. This is logically separate from the M3 "
                     "frequency-match statistic and must not be merged with it.")

    # full-S_4 systematic-absence check
    empty = [c for c in CLASSES if pooled[c] == 0]
    s2["full_S4_systematic_absence_check"] = {
        "classes_with_zero_observed_instances": empty,
        "expected_counts_under_S4": {c: round(S4_DENSITY[c] * n_tot, 2)
                                     for c in CLASSES},
        "full_S4_falsified_by_systematic_absence": bool(empty)}
    log("  classes with ZERO observed instances: %s" % (empty if empty else "none"))

    # (M4) exclusions
    s2["M4_exclusions"] = {
        "criterion": "Res(g, f) == 0 with g = X^3-e1X^2+e2X-e3, f = X^3+AX+B",
        "n_excluded_pooled": n_exc,
        "per_curve": {r["curve"]: r["n_excluded_resultant_zero"]
                      for r in per_curve},
        "n_Qe_identically_zero_pooled": n_zero}
    log("  M4 Res(g,f)=0 exclusions: %d pooled (%s)"
        % (n_exc, {r["curve"]: r["n_excluded_resultant_zero"] for r in per_curve}))

    report["stage_2"] = s2
    report["disposition"] = "completed_valid"
    report["certificate"] = {
        "kind": "none",
        "note": ("Pure measurement run. No discrete-log solve and no "
                 "factor-base relation is claimed.")}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    report["wall_seconds"] = round(time.time() - T0, 1)
    report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
    report["peak_rss_bytes"] = int(ru.ru_maxrss)
    report["python_version"] = sys.version.split()[0]
    log("\nwall %.1fs  cpu %.1fs  peak RSS %d bytes"
        % (report["wall_seconds"], report["cpu_seconds"],
           report["peak_rss_bytes"]))
    json.dump(report, open(out_path, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
