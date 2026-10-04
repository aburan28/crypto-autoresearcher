"""
EXP-MONO-e102a3 -- Stage 0 / Stage 1 (CORRECTED exact tolerance) / Stage R8.

Adapts EXP-MONO-bb6fa1's own already-independently-verified pipeline
(experiments/EXP-MONO-bb6fa1/implementation/run_galois_cubic_census.py)
to a SECOND curve/point at the SAME prime p=101, per
ledger/handoffs/TASK-20260904-fe2988.yaml and the frozen contract
experiments/EXP-MONO-e102a3/specification.yaml.

TWO changes from the original script, and ONLY these two:

  (1) CURVE/POINT SELECTION: the identical ascending (A,B) scan rule
      (A=0..100 outer, B=0..100 inner; first nonsingular, ordinary,
      j-not-in-{0,1728} curve taken) is continued PAST the first
      admissible curve already found by EXP-MONO-bb6fa1 (A=1,B=1) --
      i.e. this script re-derives that same first hit (to confirm it
      lands on A=1,B=1, verifying the scan is genuinely a continuation
      of the identical declared order, not a different rule), then
      keeps scanning and takes the NEXT admissible (A,B) pair after it.
      Both are disclosed. Point R' is selected by the identical rule
      (R'=kG', smallest k>=2 giving a point of TRUE order not dividing
      2, order computed by factoring, never assumed).

  (2) STAGE 1 TOLERANCE, CORRECTED per CORR-20260904-8cc20f: the two
      nearby-object controls (synthetic A_3 object, unconstrained
      object) are exhaustive deterministic censuses of the ENTIRE
      finite population of monic cubics over F_p, not statistical
      samples -- so they are compared against their EXACT closed-form
      finite-p triples using EXACT FRACTION arithmetic (Python's
      fractions.Fraction, zero tolerance), not an asymptotic-plus-
      standard-error band. Any mismatch is a specification_error (stop,
      per S1/S2 of the frozen contract).

Everything else -- the symmetric-coordinate (e1,e2,e3) enumeration
(never solve-for-e3), the cubic classifier, the S_4-via-Q_e(T0) fast
path (reusing EXP-MONO-815525's own already-proven exact symmetric
descent, read-only), and the R8 m=3 baseline check -- is REUSED
UNMODIFIED IN LOGIC from EXP-MONO-bb6fa1's own script; only the driver
(main()) differs, per the two points above plus the new R3=17/101
exact check.

No CAS at runtime. Standard library only.
"""
import json
import os
import resource
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
S815525 = os.path.join(
    os.path.dirname(os.path.dirname(HERE)), "EXP-MONO-815525", "implementation"
)

T0_WALL = time.time()

P = 101
SEED = 20260904009  # specification.yaml replication.seeds[0]


# ---------------------------------------------------------------- curve arithmetic
# (identical to EXP-MONO-bb6fa1's own script, reused unmodified)
def j_invariant(p, A, B):
    d = (4 * A ** 3 + 27 * B ** 2) % p
    if d == 0:
        return None
    return 1728 * 4 * A ** 3 % p * pow(d, -1, p) % p


def curve_order(p, A, B):
    n = p + 1
    for x in range(p):
        v = (x * x * x + A * x + B) % p
        if v == 0:
            continue
        n += 1 if pow(v, (p - 1) // 2, p) == 1 else -1
    return n


def pt_add(p, A, P_, Q_):
    if P_ is None:
        return Q_
    if Q_ is None:
        return P_
    x1, y1 = P_
    x2, y2 = Q_
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P_ == Q_:
        lam = (3 * x1 * x1 + A) * pow(2 * y1 % p, -1, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def pt_neg(p, P_):
    return None if P_ is None else (P_[0], (-P_[1]) % p)


def pt_mul(p, A, k, P_):
    R = None
    Q_ = P_
    while k:
        if k & 1:
            R = pt_add(p, A, R, Q_)
        Q_ = pt_add(p, A, Q_, Q_)
        k >>= 1
    return R


def point_order(p, A, n, P_):
    """TRUE order of P_ (n = #E(F_p)); divides n. Computed by factoring n
    and reducing the exponent at each prime, not assumed."""
    order = n
    d = 2
    nn = n
    factors = []
    while d * d <= nn:
        while nn % d == 0:
            factors.append(d)
            nn //= d
        d += 1
    if nn > 1:
        factors.append(nn)
    for q in sorted(set(factors)):
        while order % q == 0 and pt_mul(p, A, order // q, P_) is None:
            order //= q
    return order


def find_points(p, A, B, lo, hi):
    out = []
    for x in range(lo, hi):
        v = (x * x * x + A * x + B) % p
        if v == 0:
            out.append((x, 0))
            continue
        y = None
        for c in range(1, p):
            if c * c % p == v:
                y = c
                break
        if y is not None:
            out.append((x, y))
    return out


# ---------------------------------------------------------------- cubic classifier
# (identical to EXP-MONO-bb6fa1's own script, reused unmodified)
def classify_cubic(p, e1, e2, e3):
    """g(X) = X^3 - e1 X^2 + e2 X - e3, monic depressed to b,c,d form
    X^3+bX^2+cX+d.  Returns dict with 'type' in
    {'split','one_plus_two','irreducible','degenerate'} plus disc data."""
    b, c, d = (-e1) % p, e2 % p, (-e3) % p
    disc = (18 * b * c * d - 4 * b ** 3 * d + b ** 2 * c ** 2
            - 4 * c ** 3 - 27 * d ** 2) % p
    if disc == 0:
        roots = [x for x in range(p) if (x ** 3 + b * x * x + c * x + d) % p == 0]
        return {"type": "degenerate", "disc": 0, "roots_found": roots}
    disc_is_square = pow(disc, (p - 1) // 2, p) == 1
    root = None
    for x in range(p):
        if (x ** 3 + b * x * x + c * x + d) % p == 0:
            root = x
            break
    if root is None:
        return {"type": "irreducible", "disc": disc,
                "disc_is_square": disc_is_square}
    q1 = (b + root) % p
    q0 = (c + root * q1) % p
    disc_q = (q1 * q1 - 4 * q0) % p
    if disc_q == 0:
        return {"type": "anomaly_disc_q_zero", "disc": disc, "root": root}
    q_is_square = pow(disc_q, (p - 1) // 2, p) == 1
    ctype = "split" if q_is_square else "one_plus_two"
    return {"type": ctype, "disc": disc, "disc_is_square": disc_is_square,
            "root": root, "quadratic_disc": disc_q}


# ---------------------------------------------------------------- Q_e(T0) fast path
# (identical to EXP-MONO-bb6fa1's own script, reused unmodified)
def load_symmetric_terms(p, A, B):
    SYMT = json.load(open(os.path.join(S815525, "s4_symmetric_coeffs.json")))
    assert SYMT["gens"] == ["e1", "e2", "e3", "A", "B"]
    return SYMT


def specialize_at_T0(SYMT, p, A, B, T0v):
    T0pow = [pow(T0v, k, p) for k in range(5)]
    merged = {}
    for k, terms in SYMT["coeffs"].items():
        k = int(k)
        w = T0pow[k]
        if w == 0:
            continue
        for key, co in terms.items():
            i, j, l, ia, ib = [int(t) for t in key.split(",")]
            v = co % p * pow(A, ia, p) % p * pow(B, ib, p) % p * w % p
            if v:
                merged[(i, j, l)] = (merged.get((i, j, l), 0) + v) % p
    return [(i, j, l, v) for (i, j, l), v in merged.items() if v]


def find_VR_points(terms, p):
    """Exhaustive zero set of F(e1,e2,e3) over F_p^3, DIRECT symmetric
    coordinate enumeration (never solve-for-e3)."""
    bucket_i = {}
    for i, j, l, v in terms:
        bucket_i.setdefault(i, []).append((j, l, v))

    hits = []
    for e1 in range(p):
        pow1 = [pow(e1, i, p) for i in range(5)]
        bucket_j = {}
        for i, lst in bucket_i.items():
            w1 = pow1[i]
            if w1 == 0:
                continue
            for j, l, v in lst:
                bucket_j.setdefault(j, []).append((l, v * w1 % p))
        if not bucket_j:
            continue
        for e2 in range(p):
            pow2 = [pow(e2, j, p) for j in range(5)]
            coeff_l = [0, 0, 0, 0, 0]
            for j, lst in bucket_j.items():
                w2 = pow2[j]
                if w2 == 0:
                    continue
                for l, w in lst:
                    coeff_l[l] = (coeff_l[l] + w * w2) % p
            if all(c == 0 for c in coeff_l):
                for e3 in range(p):
                    hits.append((e1, e2, e3))
                continue
            c0, c1, c2, c3, c4 = coeff_l
            for e3 in range(p):
                val = c4
                val = (val * e3 + c3) % p
                val = (val * e3 + c2) % p
                val = (val * e3 + c1) % p
                val = (val * e3 + c0) % p
                if val == 0:
                    hits.append((e1, e2, e3))
    return hits


# ---------------------------------------------------------------- stage runners
def stage0_VR_census(p, A, B, T0v, log):
    """Identical logic to EXP-MONO-bb6fa1's own stage0_VR_census."""
    SYMT = load_symmetric_terms(p, A, B)
    terms = specialize_at_T0(SYMT, p, A, B, T0v)
    log("  Q_e(T0) specialized trivariate poly F(e1,e2,e3): %d monomials"
        % len(terms))
    t0 = time.time()
    hits = find_VR_points(terms, p)
    dt = time.time() - t0
    log("  |V_R(F_%d)| = %d  (enumeration wall %.2fs)" % (p, len(hits), dt))

    type_counts = {"split": 0, "one_plus_two": 0, "irreducible": 0,
                   "degenerate": 0, "anomaly_disc_q_zero": 0}
    disc_square_count = 0
    degenerate_instances = []
    anomaly_instances = []
    for (e1, e2, e3) in hits:
        cl = classify_cubic(p, e1, e2, e3)
        type_counts[cl["type"]] = type_counts.get(cl["type"], 0) + 1
        if cl["type"] == "degenerate":
            degenerate_instances.append({"e": [e1, e2, e3], **cl})
        elif cl["type"] == "anomaly_disc_q_zero":
            anomaly_instances.append({"e": [e1, e2, e3], **cl})
        else:
            if cl["disc_is_square"]:
                disc_square_count += 1

    n_nondeg = len(hits) - type_counts["degenerate"] - type_counts["anomaly_disc_q_zero"]
    R1 = disc_square_count / n_nondeg if n_nondeg else None
    R2 = type_counts["one_plus_two"] / n_nondeg if n_nondeg else None
    R3 = type_counts["split"] / n_nondeg if n_nondeg else None
    irred_density = type_counts["irreducible"] / n_nondeg if n_nondeg else None

    R3_exact = Fraction(type_counts["split"], n_nondeg) if n_nondeg else None
    R1_exact = Fraction(disc_square_count, n_nondeg) if n_nondeg else None
    R2_exact = Fraction(type_counts["one_plus_two"], n_nondeg) if n_nondeg else None
    irred_exact = Fraction(type_counts["irreducible"], n_nondeg) if n_nondeg else None

    return {
        "p": p, "T0": T0v,
        "n_VR_total": len(hits),
        "n_VR_nondegenerate": n_nondeg,
        "n_degenerate": type_counts["degenerate"],
        "n_anomaly_disc_q_zero": type_counts["anomaly_disc_q_zero"],
        "type_counts": type_counts,
        "R1_disc_square_rate": R1,
        "R1_disc_square_rate_exact": str(R1_exact) if R1_exact is not None else None,
        "R2_one_plus_two_density": R2,
        "R2_one_plus_two_density_exact": str(R2_exact) if R2_exact is not None else None,
        "R3_split_density": R3,
        "R3_split_density_exact": str(R3_exact) if R3_exact is not None else None,
        "irreducible_density": irred_density,
        "irreducible_density_exact": str(irred_exact) if irred_exact is not None else None,
        "lang_weil_expectation_p2": p * p,
        "lang_weil_envelope_3p_1.5": round(3 * p ** 1.5, 1),
        "within_lang_weil_envelope": bool(
            abs(len(hits) - p * p) <= 3 * p ** 1.5),
        "degenerate_instances_sample": degenerate_instances[:20],
        "anomaly_instances_sample": anomaly_instances[:20],
        "enumeration_wall_seconds": round(dt, 2),
    }


def stage1_controls_corrected(p, log):
    """(a) synthetic A_3 object: ALL (e1,e2,e3) with disc(g) a nonzero
    square, DIRECTLY enumerated (never filtered from V_R).
    (b) unconstrained object: ALL (e1,e2,e3), no condition at all.

    CORRECTED per CORR-20260904-8cc20f / this contract's stage_1
    description: both are exhaustive deterministic censuses, so they
    are compared against their EXACT closed-form finite-p triples using
    Fraction arithmetic and ZERO TOLERANCE, not an asymptotic-plus-
    standard-error band."""
    t0 = time.time()
    a_counts = {"split": 0, "one_plus_two": 0, "irreducible": 0,
                "degenerate": 0, "anomaly_disc_q_zero": 0}
    b_counts = {"split": 0, "one_plus_two": 0, "irreducible": 0,
                "degenerate": 0, "anomaly_disc_q_zero": 0}
    a_total = 0
    b_total = p ** 3
    for e1 in range(p):
        for e2 in range(p):
            for e3 in range(p):
                b_, c_, d_ = (-e1) % p, e2 % p, (-e3) % p
                disc = (18 * b_ * c_ * d_ - 4 * b_ ** 3 * d_
                        + b_ ** 2 * c_ ** 2 - 4 * c_ ** 3 - 27 * d_ ** 2) % p
                is_sq = disc != 0 and pow(disc, (p - 1) // 2, p) == 1
                cl = classify_cubic(p, e1, e2, e3)
                b_counts[cl["type"]] += 1
                if is_sq:
                    a_total += 1
                    a_counts[cl["type"]] += 1
    dt = time.time() - t0
    log("  Stage 1 direct enumeration wall %.2fs" % dt)

    def triple_exact(counts, total):
        nondeg = total - counts["degenerate"] - counts["anomaly_disc_q_zero"]
        if nondeg == 0:
            return None
        return {
            "n_total": total,
            "n_nondegenerate": nondeg,
            "split_density": counts["split"] / nondeg,
            "one_plus_two_density": counts["one_plus_two"] / nondeg,
            "irreducible_density": counts["irreducible"] / nondeg,
            "split_density_exact": Fraction(counts["split"], nondeg),
            "one_plus_two_density_exact": Fraction(counts["one_plus_two"], nondeg),
            "irreducible_density_exact": Fraction(counts["irreducible"], nondeg),
            "counts": counts,
        }

    a_res = triple_exact(a_counts, a_total)
    b_res = triple_exact(b_counts, b_total)

    # Exact closed-form finite-p triples, per CORR-20260904-8cc20f and the
    # frozen specification's stage_1_tolerance_correction, as Fractions.
    a_exact = (Fraction(p - 2, 3 * p), Fraction(0), Fraction(2 * (p + 1), 3 * p))
    b_exact = (Fraction(p - 2, 6 * p), Fraction(1, 2), Fraction(p + 1, 3 * p))

    def exact_equal(observed_triple, expected_triple):
        return all(observed_triple[i] == expected_triple[i] for i in range(3))

    a_observed_exact = (a_res["split_density_exact"],
                         a_res["one_plus_two_density_exact"],
                         a_res["irreducible_density_exact"]) if a_res else None
    b_observed_exact = (b_res["split_density_exact"],
                         b_res["one_plus_two_density_exact"],
                         b_res["irreducible_density_exact"]) if b_res else None

    a_pass = a_res is not None and exact_equal(a_observed_exact, a_exact)
    b_pass = b_res is not None and exact_equal(b_observed_exact, b_exact)

    log("  synthetic A_3 object EXACT check: observed=(%s,%s,%s) expected=(%s,%s,%s) match=%s"
        % (a_observed_exact + a_exact + (a_pass,) if a_observed_exact else (None,) * 7))
    log("  unconstrained object EXACT check: observed=(%s,%s,%s) expected=(%s,%s,%s) match=%s"
        % (b_observed_exact + b_exact + (b_pass,) if b_observed_exact else (None,) * 7))

    def jsonify(res):
        if res is None:
            return None
        out = dict(res)
        out["split_density_exact"] = str(out["split_density_exact"])
        out["one_plus_two_density_exact"] = str(out["one_plus_two_density_exact"])
        out["irreducible_density_exact"] = str(out["irreducible_density_exact"])
        return out

    return {
        "tolerance_model": "CORRECTED per CORR-20260904-8cc20f: exact "
                            "Fraction equality against the exact finite-p "
                            "closed-form triple, zero tolerance (both "
                            "objects are exhaustive deterministic censuses, "
                            "not statistical samples).",
        "synthetic_A3_object": {
            "enumeration": "ALL (e1,e2,e3) in F_p^3 with disc(g) a nonzero "
                           "square, direct enumeration (not filtered from V_R)",
            "result": jsonify(a_res),
            "expected_triple_exact_finite_p": [str(x) for x in a_exact],
            "matches_exact_finite_p_formula": bool(a_pass),
            "pass": bool(a_pass),
        },
        "unconstrained_object": {
            "enumeration": "ALL (e1,e2,e3) in F_p^3, no condition",
            "result": jsonify(b_res),
            "expected_triple_exact_finite_p": [str(x) for x in b_exact],
            "matches_exact_finite_p_formula": bool(b_pass),
            "pass": bool(b_pass),
        },
        "both_pass": bool(a_pass and b_pass),
        "wall_seconds": round(dt, 2),
    }


def stage_r8(p, A, B, log):
    """m=3 baseline reproduction: disc_{x2} S_3(x1,x2,T0) = 16 f(x1) f(T0)
    identically. Identical to EXP-MONO-bb6fa1's own stage_r8."""
    S3T = json.load(open(os.path.join(S815525, "s3_monomials.json")))
    assert S3T["gens"] == ["x1", "x2", "x3", "A", "B"]

    def f(x):
        return (x ** 3 + A * x + B) % p

    def s3_as_poly_in_x2(x1v, x3v):
        coeff = [0, 0, 0]
        for key, co in S3T["terms"].items():
            a, b, c, i, j = [int(t) for t in key.split(",")]
            v = (co % p) * pow(x1v, a, p) % p * pow(x3v, c, p) % p \
                * pow(A, i, p) % p * pow(B, j, p) % p
            coeff[b] = (coeff[b] + v) % p
        return coeff

    samples = []
    all_pass = True
    for x1v in range(0, p, 17):
        for x3v in range(1, p, 23):
            c0, c1, c2 = s3_as_poly_in_x2(x1v, x3v)
            disc = (c1 * c1 - 4 * c2 * c0) % p
            rhs = (16 * f(x1v) % p * f(x3v)) % p
            ok = bool(disc == rhs)
            all_pass = all_pass and ok
            samples.append({"x1": x1v, "T0": x3v, "disc_x2_S3": disc,
                            "16_f_x1_f_T0": rhs, "match": ok})
    log("  R8 identity checked on %d sample (x1,T0) pairs, all match: %s"
        % (len(samples), all_pass))
    return {"n_samples": len(samples), "samples": samples, "pass": bool(all_pass)}


def find_admissible_curve(p, log, skip_first_hit=False):
    """Ascending (A,B) scan: A outer 0..p-1, B inner 0..p-1; first
    nonsingular, ordinary, j-not-in-{0,1728} curve. If skip_first_hit,
    continues PAST the first admissible pair found and returns the NEXT
    one, disclosing both the first hit and the additional pairs examined
    to reach the second. This re-derives EXP-MONO-bb6fa1's own first hit
    (to confirm the scan order is identical) before continuing."""
    first_hit = None
    second_hit = None
    examined_to_first = 0
    examined_after_first = 0
    for A in range(p):
        for B in range(p):
            if first_hit is None:
                examined_to_first += 1
            elif second_hit is None:
                examined_after_first += 1
            if (4 * A ** 3 + 27 * B ** 2) % p == 0:
                continue
            j = j_invariant(p, A, B)
            if j is None or j in (0, 1728 % p):
                continue
            n = curve_order(p, A, B)
            t = p + 1 - n
            if t % p == 0:
                continue
            hit = {"A": A, "B": B, "j": j, "order": n, "trace": t}
            if first_hit is None:
                first_hit = hit
                if not skip_first_hit:
                    return first_hit, examined_to_first, None, None
                continue
            second_hit = hit
            break
        if second_hit:
            break
    return first_hit, examined_to_first, second_hit, examined_after_first


# ---------------------------------------------------------------- main
def main(outpath):
    report = {"seed": SEED, "p": P}

    def log(m):
        print(m, flush=True)

    log("=== EXP-MONO-e102a3 RUN-MONO-e102a3-1 ===")

    # ---- SETUP: curve selection -- resume the IDENTICAL ascending
    #      (A,B) scan EXP-MONO-bb6fa1 used, continuing PAST its first
    #      hit (A=1,B=1) to the NEXT admissible pair.
    log("\n--- SETUP: curve selection (resume ascending (A,B) scan, take NEXT admissible curve) ---")
    first_hit, examined_to_first, second_hit, examined_after_first = \
        find_admissible_curve(P, log, skip_first_hit=True)

    if first_hit is None or first_hit["A"] != 1 or first_hit["B"] != 1:
        report["disposition"] = "specification_error"
        report["fatal"] = (
            "Re-deriving the scan's first hit did NOT reproduce "
            "EXP-MONO-bb6fa1's own recorded (A=1,B=1) -- the scan order "
            "or admissibility conditions do not match the prior script. "
            "first_hit found: %r" % (first_hit,))
        json.dump(report, open(outpath, "w"), indent=1)
        return 2
    log("  re-derived first hit (confirms identical scan order to "
        "EXP-MONO-bb6fa1): A=%d, B=%d, j=%d, order=%d, trace=%d "
        "(%d pairs examined to reach it)"
        % (first_hit["A"], first_hit["B"], first_hit["j"], first_hit["order"],
           first_hit["trace"], examined_to_first))

    if second_hit is None:
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "no second admissible curve found continuing the scan"
        json.dump(report, open(outpath, "w"), indent=1)
        return 2

    found = second_hit
    A, B = found["A"], found["B"]
    n = found["order"]
    log("  CONTINUING scan past first hit: %d additional (A,B) pairs "
        "examined after the first hit to reach the NEXT admissible curve"
        % examined_after_first)
    log("  FOUND (second, new curve): E': y^2 = x^3 + %d x + %d over F_%d,  "
        "j=%d  #E'(F_%d)=%d  trace=%d"
        % (A, B, P, found["j"], P, n, found["trace"]))
    report["curve_selection"] = {
        "selection_rule": "resume the identical ascending A outer, B inner "
                           "scan from EXP-MONO-bb6fa1; take the NEXT "
                           "admissible (A,B) pair after the first hit, "
                           "not a re-run from scratch",
        "first_hit_reconfirmed": dict(first_hit, curves_examined_to_reach=examined_to_first),
        "second_hit_new_curve": dict(found, p=P,
                                      additional_pairs_examined_after_first_hit=examined_after_first),
    }

    # ---- generator G': first point (by ascending x) whose TRUE order is n
    log("\n--- generator selection ---")
    G = None
    g_order = None
    for x in range(P):
        pts = find_points(P, A, B, x, x + 1)
        for cand in pts:
            ordc = point_order(P, A, n, cand)
            if ordc == n:
                G = cand
                g_order = ordc
                break
        if G:
            break
    if G is None:
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "no generator of full order n found (group may not be cyclic)"
        json.dump(report, open(outpath, "w"), indent=1)
        return 2
    log("  generator G' = %s, true order verified = %d (== #E'(F_%d) = %d)"
        % (G, g_order, P, n))
    report["generator"] = {"G": list(G), "true_order": g_order}

    # ---- point R' = kG', k smallest >=2 such that R' is not in E'[2]
    #      (R''s TRUE order computed directly and asserted, not assumed)
    log("\n--- point R' = kG' selection ---")
    k = 2
    R = None
    r_order = None
    while k < n:
        cand = pt_mul(P, A, k, G)
        if cand is None:
            k += 1
            continue
        ordr = point_order(P, A, n, cand)
        if ordr > 2:
            R = cand
            r_order = ordr
            break
        k += 1
    if R is None:
        report["disposition"] = "failed_infrastructure"
        report["fatal"] = "no k found with R'=kG' outside E'[2]"
        json.dump(report, open(outpath, "w"), indent=1)
        return 2
    T0v = R[0]
    log("  k=%d, R' = kG' = %s, TRUE order of R' (computed directly) = %d "
        "(> 2, so R' is NOT in E'[2])" % (k, R, r_order))
    log("  T0 = x(R') = %d" % T0v)
    report["point_R"] = {"k": k, "R": list(R), "true_order": r_order, "T0": T0v}

    # ================================================== STAGE R8 (gate 2, run first: free/cheap)
    log("\n--- STAGE R8: m=3 baseline reproduction (free, symbolic/numeric) ---")
    r8 = stage_r8(P, A, B, log)
    report["stage_r8"] = r8
    log("STAGE R8: %s" % ("PASS" if r8["pass"] else "FAIL"))
    if not r8["pass"]:
        report["disposition"] = "specification_error"
        report["stop_reason"] = ("R8 (m=3 baseline reproduction check) FAILED "
                                 "on the new curve. No m=4 output may be read (S2).")
        log("STOPPING per S2: pipeline does not reproduce the baseline on this curve.")
        ru = resource.getrusage(resource.RUSAGE_SELF)
        report["wall_seconds"] = round(time.time() - T0_WALL, 1)
        report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
        report["peak_rss_bytes"] = int(ru.ru_maxrss)
        json.dump(report, open(outpath, "w"), indent=1)
        return 3

    # ================================================== STAGE 1 (mandatory gate, CORRECTED exact tolerance)
    log("\n--- STAGE 1: mandatory nearby-object controls, CORRECTED EXACT tolerance ---")
    s1 = stage1_controls_corrected(P, log)
    report["stage_1"] = s1
    log("  synthetic A_3 object EXACT match: %s" % s1["synthetic_A3_object"]["pass"])
    log("  unconstrained object EXACT match: %s" % s1["unconstrained_object"]["pass"])
    log("STAGE 1 BOTH CONTROLS EXACT MATCH: %s" % s1["both_pass"])

    if not s1["both_pass"]:
        report["disposition"] = "specification_error"
        report["stop_reason"] = (
            "STAGE 1 (corrected exact-tolerance gate) FAILED: at least "
            "one nearby-object control did not match its exact closed-form "
            "finite-p triple exactly. Since both the classifier and the "
            "closed forms were already independently verified correct on "
            "EXP-MONO-bb6fa1, this indicates a NEW bug in this run's own "
            "adaptation. STOPPING per the frozen contract's stopping rule; "
            "no Stage 0 interpretation follows.")
        log("\nSTOPPING per corrected S1: control mismatch -- specification_error.")
        ru = resource.getrusage(resource.RUSAGE_SELF)
        report["wall_seconds"] = round(time.time() - T0_WALL, 1)
        report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
        report["peak_rss_bytes"] = int(ru.ru_maxrss)
        json.dump(report, open(outpath, "w"), indent=1)
        return 4

    # ================================================== STAGE 0
    log("\n--- STAGE 0: exhaustive V_R'(F_101) census on the new curve ---")
    s0 = stage0_VR_census(P, A, B, T0v, log)
    report["stage_0"] = s0
    log("  |V_R'| = %d  (Lang-Weil ~p^2=%d, envelope +/-%.1f, within=%s)"
        % (s0["n_VR_total"], s0["lang_weil_expectation_p2"],
           s0["lang_weil_envelope_3p_1.5"], s0["within_lang_weil_envelope"]))
    log("  non-degenerate: %d, degenerate: %d, anomaly: %d"
        % (s0["n_VR_nondegenerate"], s0["n_degenerate"],
           s0["n_anomaly_disc_q_zero"]))
    log("  R1 (disc-square rate) = %s (exact %s)" % (s0["R1_disc_square_rate"], s0["R1_disc_square_rate_exact"]))
    log("  R2 (1+2 density)      = %s (exact %s)" % (s0["R2_one_plus_two_density"], s0["R2_one_plus_two_density_exact"]))
    log("  R3 (split density)    = %s (exact %s)" % (s0["R3_split_density"], s0["R3_split_density_exact"]))
    log("  irreducible density   = %s (exact %s)" % (s0["irreducible_density"], s0["irreducible_density_exact"]))

    # ---- THE KEY NEW CHECK: R3 == 17/101 exactly?
    seventeen_over_101 = Fraction(17, 101)
    r3_exact_frac = (Fraction(s0["type_counts"]["split"], s0["n_VR_nondegenerate"])
                      if s0["n_VR_nondegenerate"] else None)
    r3_matches_17_over_101 = bool(r3_exact_frac is not None
                                   and r3_exact_frac == seventeen_over_101)
    log("\n--- KEY CHECK: does R3 equal EXACTLY 17/101? ---")
    log("  observed R3 = %s ; target 17/101 = %s ; EXACT MATCH = %s"
        % (r3_exact_frac, seventeen_over_101, r3_matches_17_over_101))
    report["r3_equals_17_over_101_exact"] = {
        "observed_R3_exact": str(r3_exact_frac) if r3_exact_frac is not None else None,
        "target": "17/101",
        "matches_exactly": r3_matches_17_over_101,
    }

    # ---- interpretation (both gates passed): S_3-consistency reading,
    #      identical asymptotic-vs-observed check as EXP-MONO-bb6fa1's
    #      own interpretation block (this compares Stage 0's OWN R1/R2/R3,
    #      an exhaustive census of the curve's own V_R -- not the Stage-1
    #      control objects -- against the idealized Chebotarev asymptote,
    #      which remains the specification's own literal comparison target
    #      for THIS quantity; only the Stage-1 CONTROL tolerance was
    #      corrected).
    R1, R2, R3 = s0["R1_disc_square_rate"], s0["R2_one_plus_two_density"], s0["R3_split_density"]
    n_nondeg = s0["n_VR_nondegenerate"]
    se = (0.5 * 0.5 / n_nondeg) ** 0.5 if n_nondeg else None
    outcome_I = (n_nondeg > 0 and abs(R1 - 0.5) <= 3 * se
                 and abs(R2 - 0.5) <= 3 * se and abs(R3 - 1 / 6) <= 3 * se)
    outcome_II = (n_nondeg > 0 and abs(R1 - 1.0) <= 1e-9 and R2 == 0.0)
    if outcome_I:
        outcome = "outcome_I_s3_confirmed"
    elif outcome_II:
        outcome = "outcome_II_a3_found"
    else:
        outcome = "outcome_neither_anomaly"
    report["interpretation"] = {
        "standard_error_approx": se,
        "outcome_I_s3_confirmed": bool(outcome_I),
        "outcome_II_a3_found": bool(outcome_II),
        "final_outcome": outcome,
    }
    log("\n--- INTERPRETATION (both gates passed) ---")
    log("  outcome: %s" % outcome)

    report["disposition"] = "completed_valid"
    ru = resource.getrusage(resource.RUSAGE_SELF)
    report["wall_seconds"] = round(time.time() - T0_WALL, 1)
    report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
    report["peak_rss_bytes"] = int(ru.ru_maxrss)
    report["python_version"] = sys.version.split()[0]
    log("\ntotal wall seconds: %.1f  cpu %.1f  peak RSS %d bytes"
        % (report["wall_seconds"], report["cpu_seconds"], report["peak_rss_bytes"]))
    json.dump(report, open(outpath, "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
