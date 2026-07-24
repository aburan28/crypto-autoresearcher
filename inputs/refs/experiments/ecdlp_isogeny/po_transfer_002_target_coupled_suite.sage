#!/usr/bin/env sage
# PO-transfer-002: target-coupled transfer/relation source.
#
# Candidate: use a Sym^d(E) / Abel-Jacobi style correspondence as a target-coupled
# relation source.  Enumerate sparse signed effective-divisor differences over a
# public factor base and search directly for:
#
#     Q + P(v_left) - P(v_right) = O
#
# This is intentionally charged like a meet-in-the-middle map into the Jacobian
# J(E)=E.  A success must recover the original target scalar from public
# relations and beat Pollard rho after map/probe/memory costs.  If it merely
# behaves like BSGS with poor constants, the result is a reusable negative.

import itertools
import json
import sys
import time


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


def point_key(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def add_vec(E, fb_points, vec):
    S = E(0)
    ops = 0
    for c, P in zip(vec, fb_points):
        if c == 0:
            continue
        S += P if c > 0 else -P
        ops += abs(c)
    return S, ops


def sparse_signed_vectors(n, max_weight):
    zero = tuple([0] * n)
    yield zero
    for w in range(1, max_weight + 1):
        for inds in itertools.combinations(range(n), w):
            for signs in itertools.product([-1, 1], repeat=w):
                v = [0] * n
                for i, s in zip(inds, signs):
                    v[i] = s
                yield tuple(v)


def public_factor_base(E, fb_size, seed):
    # Logs are kept only for verifier-side correctness checks; the relation
    # source uses the public points and group law only.
    set_random_seed(seed)
    N = Integer(E.order())
    G = E.gens()[0]
    points = [G]
    hidden_logs = [Integer(1)]
    seen = {point_key(G)}
    for i in range(1, fb_size):
        # Deterministic pseudo-random scalars keep the artifact reproducible.
        k = Integer((seed * (i + 17) * 7919 + i * i * 104729) % N)
        if k == 0:
            k = Integer(i + 2)
        P = k * G
        while point_key(P) in seen or P == E(0):
            k = (k + 37) % N
            if k == 0:
                k = 1
            P = k * G
        points.append(P)
        hidden_logs.append(k)
        seen.add(point_key(P))
    return G, points, hidden_logs


def solve_relation_system(N, fb_size, relations, secret):
    K = GF(Integer(N))
    variables = fb_size - 1 + 1  # factor-base logs except G, plus target k.
    if not relations:
        return {
            "variables": variables,
            "relations": 0,
            "rank": 0,
            "augmented_rank": 0,
            "consistent": True,
            "target_recovered": False,
            "recovered_secret": None,
        }

    rows = []
    rhs = []
    for rel in relations:
        coeffs = rel["coefficients"]
        target_coeff = rel["target_coeff"]
        c0 = coeffs[0]
        row = [K(c) for c in coeffs[1:]] + [K(target_coeff)]
        rows.append(row)
        rhs.append(K(-c0))
    A = matrix(K, rows)
    b = vector(K, rhs)
    rank = A.rank()
    aug_rank = A.augment(b).rank()
    consistent = rank == aug_rank
    recovered_secret = None
    target_recovered = False
    if consistent and rank == variables:
        sol = A.solve_right(b)
        recovered_secret = Integer(sol[-1]) % N
        target_recovered = recovered_secret == Integer(secret) % N
    return {
        "variables": variables,
        "relations": len(relations),
        "rank": int(rank),
        "augmented_rank": int(aug_rank),
        "consistent": bool(consistent),
        "target_recovered": bool(target_recovered),
        "recovered_secret": int(recovered_secret) if recovered_secret is not None else None,
    }


def target_coupled_source(E, fb_size=10, max_weight=2, secret=137, seed=20260624):
    N = Integer(E.order())
    G, fb_points, hidden_logs = public_factor_base(E, fb_size, seed)
    Q = Integer(secret) * G
    vectors = list(sparse_signed_vectors(fb_size, max_weight))

    table = {}
    map_ops = 0
    for v in vectors:
        P, ops = add_vec(E, fb_points, v)
        map_ops += ops
        table.setdefault(point_key(P), []).append((v, P))

    relations = []
    seen = set()
    target_probes = 0
    zero_probes = 0
    collision_candidates = 0

    for v_left in vectors:
        P_left, ops = add_vec(E, fb_points, v_left)
        map_ops += ops

        # Zero-target relations are useful for factor-base rank.
        zero_probes += 1
        for v_right, _P_right in table.get(point_key(P_left), []):
            coeff = tuple(a - b for a, b in zip(v_left, v_right))
            if all(c == 0 for c in coeff):
                continue
            key = (coeff, 0)
            if key not in seen:
                seen.add(key)
                collision_candidates += 1
                relations.append({"coefficients": coeff, "target_coeff": 0, "kind": "zero"})

        # Target-coupled relations: Q + P(left) - P(right) = O.
        target_probes += 1
        target_point = Q + P_left
        for v_right, _P_right in table.get(point_key(target_point), []):
            coeff = tuple(a - b for a, b in zip(v_left, v_right))
            key = (coeff, 1)
            if key not in seen:
                seen.add(key)
                collision_candidates += 1
                relations.append({"coefficients": coeff, "target_coeff": 1, "kind": "target_plus"})

        # Also check -Q + P(left) - P(right) = O for symmetry.
        target_probes += 1
        target_point = -Q + P_left
        for v_right, _P_right in table.get(point_key(target_point), []):
            coeff = tuple(a - b for a, b in zip(v_left, v_right))
            key = (coeff, -1)
            if key not in seen:
                seen.add(key)
                collision_candidates += 1
                relations.append({"coefficients": coeff, "target_coeff": -1, "kind": "target_minus"})

    solve = solve_relation_system(N, fb_size, relations, secret)
    target_relations = [r for r in relations if r["target_coeff"] != 0]
    zero_relations = [r for r in relations if r["target_coeff"] == 0]
    rho = float(rho_ops(N))
    # Map/probe charge is intentionally conservative but simple: divisor maps
    # plus one group lookup/probe per tested target/zero condition.
    charged_ops = map_ops + zero_probes + target_probes
    memory_entries = len(table)
    charged_ops_over_rho = float(charged_ops / rho)
    memory_over_sqrt_n = float(memory_entries / sqrt(N))

    if not target_relations:
        classification = "projection_only"
    elif solve["rank"] < solve["variables"]:
        classification = "rank_deficient"
    elif not solve["target_recovered"]:
        classification = "target_descent_deficient"
    elif charged_ops > rho:
        classification = "baseline_lost"
    else:
        classification = "candidate"

    return {
        "order": int(N),
        "fb_size": fb_size,
        "max_weight": max_weight,
        "vector_count": len(vectors),
        "map_ops": int(map_ops),
        "zero_probes": int(zero_probes),
        "target_probes": int(target_probes),
        "charged_ops": int(charged_ops),
        "rho_ops": rho,
        "charged_ops_over_rho": charged_ops_over_rho,
        "memory_entries": int(memory_entries),
        "memory_over_sqrt_n": memory_over_sqrt_n,
        "relations": int(len(relations)),
        "zero_relations": int(len(zero_relations)),
        "target_relations": int(len(target_relations)),
        "rank": int(solve["rank"]),
        "variables": int(solve["variables"]),
        "consistent": bool(solve["consistent"]),
        "target_recovered": bool(solve["target_recovered"]),
        "recovered_secret": solve["recovered_secret"],
        "secret_for_verifier": int(secret),
        "hidden_fb_logs_for_verifier": [int(x) for x in hidden_logs],
        "classification": classification,
    }


def run_suite():
    p = 4099
    Fp = GF(p)
    E = EllipticCurve(Fp, [Fp(4041), Fp(4067)])
    configs = [
        {"fb_size": 8, "max_weight": 1},
        {"fb_size": 8, "max_weight": 2},
        {"fb_size": 8, "max_weight": 3},
        {"fb_size": 10, "max_weight": 2},
        {"fb_size": 10, "max_weight": 3},
        {"fb_size": 12, "max_weight": 2},
        {"fb_size": 12, "max_weight": 3},
    ]
    rows = []
    for cfg in configs:
        t0 = time.time()
        row = target_coupled_source(E, seed=20260624, secret=137, **cfg)
        row["elapsed_seconds"] = time.time() - t0
        rows.append(row)
    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_or_task": "PO-transfer-002 target-coupled Abel-Jacobi/Sym^d relation source",
        "status": "OBSERVATION",
        "parameters": {
            "p": p,
            "curve": {"a4": int(E.a4()), "a6": int(E.a6()), "order": int(E.order())},
            "target": "Q = 137*G, secret used only for verifier-side recovery check",
            "source": "Sparse signed divisor differences in Sym^d(E), mapped by Abel-Jacobi sum to J(E)=E",
        },
        "rows": rows,
        "best_by_rank": max(rows, key=lambda r: (r["target_recovered"], r["rank"], -r["charged_ops_over_rho"])),
    }


def main():
    out_path = parse_out("experiments/ecdlp_isogeny/po_transfer_002_result.json")
    result = run_suite()
    with open(out_path, "w") as f:
        json.dump(json_clean(result), f, indent=2, sort_keys=True)
    print("wrote", out_path)
    for row in result["rows"]:
        print(
            "fb=%d weight=%d target_rel=%d rank=%d/%d recovered=%s ops/rho=%.2f class=%s"
            % (
                row["fb_size"],
                row["max_weight"],
                row["target_relations"],
                row["rank"],
                row["variables"],
                row["target_recovered"],
                row["charged_ops_over_rho"],
                row["classification"],
            )
        )


main()
