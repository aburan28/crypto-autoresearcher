#!/usr/bin/env sage
# PO-transfer-001: first transfer-channel falsification suite.
#
# This is a controlled toy experiment.  It compares a flat-volcano base curve,
# same-order horizontal isogeny neighbors, and a different-order control on:
#   - m=3/S4 decomposition solving profile via the audited gated meter;
#   - public relation-rank and target-descent linear algebra;
#   - charged relation enumeration cost versus Pollard rho.
#
# It does NOT claim a native Jacobian/correspondence breakthrough.  The point is
# to make failures precise: bridge-only, rank-deficient, target-descent-deficient,
# or baseline-lost.

import itertools
import json
import sys
import time

load("experiments/ecdlp_prime_field/round016_gated_meter.sage")


def json_clean(value):
    if isinstance(value, dict):
        return {str(k): json_clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_clean(v) for v in value]
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    try:
        if value in ZZ:
            return int(value)
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return str(value)


def parse_out(default_path):
    args = list(sys.argv[1:])
    if "--out" in args:
        i = args.index("--out")
        return args[i + 1]
    return default_path


def rho_ops(order):
    return 0.886 * sqrt(Integer(order))


def semaev4(Rbig, a, b):
    F = Rbig.base_ring()
    T = PolynomialRing(F, 5, names=["x1", "x2", "x3", "x4", "X"])
    x1, x2, x3, x4, X = T.gens()

    def S3(u, v, w):
        return (
            (u - v) ** 2 * w**2
            - 2 * ((u + v) * (u * v + F(a)) + 2 * F(b)) * w
            + ((u * v - F(a)) ** 2 - 4 * F(b) * (u + v))
        )

    r = S3(x1, x2, X).resultant(S3(x3, x4, X), X)
    return Rbig(r.subs({x1: Rbig.gen(0), x2: Rbig.gen(1), x3: Rbig.gen(2), x4: Rbig.gen(3), X: 0}))


def verify_S4(E, S4poly, Rbig, ntest=8):
    F = E.base_field()
    zero_ok = 0
    nonzero_ok = 0
    for _ in range(ntest):
        pts = [E.random_point() for _ in range(3)]
        p4 = -(pts[0] + pts[1] + pts[2])
        if any(P == E(0) for P in pts + [p4]):
            continue
        val = Rbig(S4poly).subs(
            {
                Rbig.gen(0): pts[0][0],
                Rbig.gen(1): pts[1][0],
                Rbig.gen(2): pts[2][0],
                Rbig.gen(3): p4[0],
            }
        )
        if val == 0:
            zero_ok += 1
    for _ in range(ntest):
        xs = [F.random_element() for _ in range(4)]
        val = Rbig(S4poly).subs({Rbig.gen(i): xs[i] for i in range(4)})
        if val != 0:
            nonzero_ok += 1
    return zero_ok, nonzero_ok


def first_unique_multiples(E, count):
    G = E.gens()[0]
    points = []
    xs = set()
    k = 1
    while len(points) < count and k < 20 * E.base_field().cardinality():
        P = k * G
        if P != E(0) and P[0] not in xs:
            points.append(P)
            xs.add(P[0])
        k += 1
    if len(points) < count:
        raise RuntimeError("could not build factor base")
    return G, points


def decomposition_profile(E, fb_size=3):
    F = E.base_field()
    G, fb_points = first_unique_multiples(E, fb_size)
    xR = (fb_points[0] + fb_points[1] + fb_points[2])[0]
    Rbig = PolynomialRing(F, 4, names=["x1", "x2", "x3", "x4"])
    S4 = semaev4(Rbig, E.a4(), E.a6())
    zero_ok, nonzero_ok = verify_S4(E, S4, Rbig)

    R3 = PolynomialRing(F, 3, names=["x1", "x2", "x3"], order="degrevlex")
    x1, x2, x3 = R3.gens()
    S4sub = R3(
        S4.subs({Rbig.gen(3): F(xR)}).subs({Rbig.gen(0): x1, Rbig.gen(1): x2, Rbig.gen(2): x3})
    )
    fb_x = [P[0] for P in fb_points]
    fb_polys = [prod([R3.gen(i) - F(c) for c in fb_x]) for i in range(3)]
    polys = [S4sub] + fb_polys
    I = R3.ideal(polys)
    GB = I.groebner_basis()
    max_gb_degree = max(g.degree() for g in GB)
    try:
        nsols = I.vector_space_dimension()
    except Exception:
        nsols = -1
    meter = meter_gated(polys, R3, [0], Dmax=14)
    found_planted = S4sub.subs({x1: fb_x[0], x2: fb_x[1], x3: fb_x[2]}) == 0
    return {
        "fb_size": fb_size,
        "S4_degree": int(S4.degree()),
        "S4_zero_ok": int(zero_ok),
        "S4_nonzero_ok": int(nonzero_ok),
        "max_gb_degree": int(max_gb_degree),
        "nsols": int(nsols),
        "found_planted": bool(found_planted),
        "d_ff": meter["d_ff"],
        "D_reg": meter["D_reg"],
        "fires": meter["fires"],
        "gate_meaningful": meter["gate_meaningful"],
    }


def add_signed(points):
    total = points[0][0].parent()(0)
    for s, P in points:
        total += P if s > 0 else -P
    return total


def relation_rank_and_descent(E, fb_size=8, arity=3, secret=137):
    N = Integer(E.order())
    K = GF(N)
    G, fb_points = first_unique_multiples(E, fb_size)
    Q = Integer(secret) * G
    variables = fb_size - 1 + 1  # FB logs except G, plus target scalar k.
    relation_seen = set()
    rows = []
    rhs = []
    attempts = 0
    zero_relations = 0
    target_relations = 0

    for target_coeff in [0, 1, -1]:
        for inds in itertools.product(range(fb_size), repeat=arity):
            for signs in itertools.product([-1, 1], repeat=arity):
                attempts += 1
                S = E(0)
                coeff_g = 0
                coeffs = [0] * variables
                for idx, sign in zip(inds, signs):
                    P = fb_points[idx]
                    S += P if sign > 0 else -P
                    if idx == 0:
                        coeff_g += sign
                    else:
                        coeffs[idx - 1] += sign
                if target_coeff:
                    S += Q if target_coeff > 0 else -Q
                    coeffs[-1] += target_coeff
                if S != E(0):
                    continue
                key = (tuple(Integer(c) % N for c in coeffs), Integer(-coeff_g) % N)
                if key in relation_seen:
                    continue
                relation_seen.add(key)
                rows.append([K(c) for c in coeffs])
                rhs.append(K(-coeff_g))
                if target_coeff:
                    target_relations += 1
                else:
                    zero_relations += 1

    if rows:
        A = matrix(K, rows)
        b = vector(K, rhs)
        rank = A.rank()
        aug_rank = A.augment(b).rank()
        consistent = rank == aug_rank
    else:
        A = matrix(K, 0, variables)
        b = vector(K, [])
        rank = 0
        aug_rank = 0
        consistent = True

    target_recovered = False
    recovered_secret = None
    if rows and consistent and rank == variables:
        sol = A.solve_right(b)
        recovered_secret = Integer(sol[-1]) % N
        target_recovered = recovered_secret == Integer(secret) % N

    charged_ops = attempts
    rho = float(rho_ops(N))
    if target_recovered and charged_ops <= rho / 2**10:
        classification = "candidate"
    elif rank < variables:
        classification = "rank_deficient"
    elif not target_recovered:
        classification = "target_descent_deficient"
    elif charged_ops > rho:
        classification = "baseline_lost"
    else:
        classification = "candidate_needs_baseline_audit"

    return {
        "fb_size": fb_size,
        "arity": arity,
        "secret_for_verifier": int(secret),
        "attempts": int(attempts),
        "charged_ops": int(charged_ops),
        "rho_ops": rho,
        "charged_ops_over_rho": float(charged_ops / rho),
        "variables": int(variables),
        "relations": int(len(rows)),
        "zero_relations": int(zero_relations),
        "target_relations": int(target_relations),
        "rank": int(rank),
        "augmented_rank": int(aug_rank),
        "consistent": bool(consistent),
        "target_recovered": bool(target_recovered),
        "recovered_secret": int(recovered_secret) if recovered_secret is not None else None,
        "classification": classification,
    }


def flat_control_curve(Fp, exclude_order):
    for a in range(1, 200):
        for b in range(1, 200):
            if Fp(4 * a**3 + 27 * b**2) == 0:
                continue
            E = EllipticCurve(Fp, [Fp(a), Fp(b)])
            N = Integer(E.order())
            if N.is_prime() and N != exclude_order:
                D = (Fp.cardinality() + 1 - N) ** 2 - 4 * Fp.cardinality()
                if D == fundamental_discriminant(D):
                    return E
    raise RuntimeError("no control curve found")


def collect_horizontal_neighbors(E0, N, max_neighbors=6):
    curves = [("base", E0)]
    for ell in [2, 3, 5, 7, 11, 13]:
        for phi in E0.isogenies_prime_degree(ell):
            C = phi.codomain().short_weierstrass_model()
            key = (C.a4(), C.a6())
            if C.order() == N and all((E.a4(), E.a6()) != key for _, E in curves):
                curves.append(("horizontal_l%s" % ell, C))
                if len(curves) >= max_neighbors:
                    return curves
    return curves


def main():
    out_path = parse_out("experiments/ecdlp_isogeny/po_transfer_001_result.json")
    set_random_seed(20260624)
    start_time = time.time()

    p = 4099
    Fp = GF(p)
    E0 = EllipticCurve(Fp, [Fp(4041), Fp(4067)])
    N = Integer(E0.order())
    D = (p + 1 - N) ** 2 - 4 * p
    curves = collect_horizontal_neighbors(E0, N, max_neighbors=7)
    curves.append(("nonisogenous_control", flat_control_curve(Fp, N)))

    rows = []
    for tag, E in curves:
        t0 = time.time()
        row = {
            "tag": tag,
            "a4": int(E.a4()),
            "a6": int(E.a6()),
            "order": int(E.order()),
            "same_order_as_base": bool(E.order() == N),
            "decomposition_profile": decomposition_profile(E, fb_size=3),
            "rank_target_descent": relation_rank_and_descent(E, fb_size=8, arity=3, secret=137),
            "elapsed_seconds": time.time() - t0,
        }
        rows.append(row)

    same = [r for r in rows if r["same_order_as_base"]]
    max_degrees = sorted(set(r["decomposition_profile"]["max_gb_degree"] for r in same))
    dffs = sorted(set(-1 if r["decomposition_profile"]["d_ff"] is None else r["decomposition_profile"]["d_ff"] for r in same))
    gates = sorted(set(r["decomposition_profile"]["gate_meaningful"] for r in same))
    classifications = sorted(set(r["rank_target_descent"]["classification"] for r in rows))

    result = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_or_task": "PO-transfer-001 first falsification suite",
        "status": "OBSERVATION",
        "parameters": {
            "p": p,
            "base_curve": {"a4": int(E0.a4()), "a6": int(E0.a6()), "order": int(N), "D": int(D), "flat_volcano": bool(D == fundamental_discriminant(D))},
            "decomposition": "m=3/S4 with fb_size=3",
            "rank_target_descent": "signed arity-3 public relation enumeration with fb_size=8",
        },
        "rows": rows,
        "same_order_invariance": {
            "max_gb_degree_set": max_degrees,
            "d_ff_set": dffs,
            "gate_meaningful_set": gates,
            "falsified": bool(len(max_degrees) > 1 or len(dffs) > 1 or len(gates) > 1),
        },
        "classifications": classifications,
        "wall_seconds": time.time() - start_time,
    }
    with open(out_path, "w") as f:
        json.dump(json_clean(result), f, indent=2, sort_keys=True)
    print(json.dumps(json_clean(result["same_order_invariance"]), indent=2, sort_keys=True))
    print("classifications:", ", ".join(classifications))
    print("wrote", out_path)


main()
