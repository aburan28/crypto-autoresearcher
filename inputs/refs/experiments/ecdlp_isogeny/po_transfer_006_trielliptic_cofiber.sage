#!/usr/bin/env sage
# PO-transfer-006: exact-map affine falsification probe for Trielliptic
# Cofiber Decomposition (TCD).  This probe cannot claim structural success:
# it enumerates affine cover points and omits exceptional/projective fibers.

import hashlib
import json
import math
import os
import random
import sys
import time


DEFAULT_OUT = "/Volumes/Volume/autolab/experiments/ecdlp_isogeny/po_transfer_006_result.json"
PRIMES = [101, 211, 431]
SEED = 20260713


def parse_out():
    args = list(sys.argv[1:])
    if "--out" in args:
        return args[args.index("--out") + 1]
    return DEFAULT_OUT


def source_path():
    path = os.path.abspath(sys.argv[0])
    if path.endswith(".sage.py") and os.path.exists(path[:-3]):
        return path[:-3]
    return path


def source_hash():
    with open(source_path(), "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [clean(v) for v in value]
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


def score(*parts):
    raw = "|".join(str(x) for x in parts).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def point_key(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def point_from_key(E, key):
    if len(key) == 1:
        return E(0)
    return E(key[0], key[1])


def canonical_sqrt(v):
    if v == 0:
        return v
    if not v.is_square():
        return None
    r = v.sqrt()
    return r if int(r) <= int(-r) else -r


def rho_ops(order):
    return 0.886 * math.sqrt(int(order))


def edge_key(edge):
    return tuple(sorted(tuple(k) for k in edge))


def row_dict(edge, k_key, modulus):
    row = {}
    for key in edge:
        row[key] = (row.get(key, 0) + 1) % modulus
    if k_key != ("O",):
        row[k_key] = (row.get(k_key, 0) - 1) % modulus
    return {key: value for key, value in row.items() if value % modulus}


def add_to_basis(row, basis, col_index, modulus):
    vec = {col_index[key]: int(value) % modulus for key, value in row.items()}
    while vec:
        pivot = min(vec)
        if pivot not in basis:
            inv = inverse_mod(vec[pivot], modulus)
            vec = {j: (v * inv) % modulus for j, v in vec.items() if v % modulus}
            basis[pivot] = vec
            return True
        factor = vec[pivot]
        b = basis[pivot]
        for j, v in b.items():
            nv = (vec.get(j, 0) - factor * v) % modulus
            if nv:
                vec[j] = nv
            elif j in vec:
                del vec[j]
    return False


def dsu_components(edges):
    vertices = sorted(set(k for edge in edges for k in edge))
    parent = {v: v for v in vertices}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for edge in edges:
        unique = list(dict.fromkeys(edge))
        for v in unique[1:]:
            union(unique[0], v)
    sizes = {}
    for v in vertices:
        sizes[find(v)] = sizes.get(find(v), 0) + 1
    return sorted(sizes.values(), reverse=True)


def two_core(edges):
    incidence = {}
    live_edges = set(range(len(edges)))
    for i, edge in enumerate(edges):
        for v in set(edge):
            incidence.setdefault(v, set()).add(i)
    degree = {v: len(ix) for v, ix in incidence.items()}
    queue = [v for v, d in degree.items() if d < 2]
    live_vertices = set(incidence)
    while queue:
        v = queue.pop()
        if v not in live_vertices:
            continue
        live_vertices.remove(v)
        for i in list(incidence[v]):
            if i not in live_edges:
                continue
            live_edges.remove(i)
            for u in set(edges[i]):
                if u in live_vertices:
                    degree[u] -= 1
                    if degree[u] == 1:
                        queue.append(u)
    return {"vertices": len(live_vertices), "edges": len(live_edges)}


def graph_profile(edges, E, order, K, G, label):
    modulus = int(order)
    k_key = point_key(K)
    vertices = sorted(set(k for edge in edges for k in edge) |
                      ({k_key} if k_key != ("O",) else set()))
    col_index = {key: i for i, key in enumerate(vertices)}
    ordered = sorted(edges, key=lambda e: score(label, edge_key(e)))
    basis = {}
    active = set([k_key]) if k_key != ("O",) else set()
    first_closure = None
    checkpoints = []
    checkpoint_at = set(max(1, int(math.ceil(len(ordered) * f)))
                        for f in [0.1, 0.25, 0.5, 0.75, 1.0])
    rows = []
    for i, edge in enumerate(ordered, start=1):
        active.update(edge)
        row = row_dict(edge, k_key, modulus)
        rows.append(row)
        add_to_basis(row, basis, col_index, modulus)
        if (first_closure is None and point_key(G) in active and
                len(basis) >= len(active) - 1):
            first_closure = {
                "prefix_edges": i,
                "active_columns": len(active),
                "rank": len(basis),
            }
        if i in checkpoint_at:
            checkpoints.append({
                "prefix_edges": i,
                "active_columns": len(active),
                "rank": len(basis),
                "nullity_upper": len(active) - len(basis),
            })

    degrees = {}
    for edge in edges:
        for key in set(edge):
            degrees[key] = degrees.get(key, 0) + 1
    actual_kernel_failures = 0
    verifier_logs = {}
    if vertices:
        for key in vertices:
            P = point_from_key(E, key)
            verifier_logs[key] = 0 if P == E(0) else int(
                discrete_log(P, G, ord=order, operation="+")
            )
        for row in rows:
            if sum(int(coeff) * verifier_logs[key]
                   for key, coeff in row.items()) % modulus:
                actual_kernel_failures += 1

    components = dsu_components(edges)
    return {
        "label": label,
        "edges": len(edges),
        "unique_edges": len(set(edge_key(e) for e in edges)),
        "vertices": len(vertices),
        "rank": len(basis),
        "nullity": len(vertices) - len(basis),
        "generator_present": point_key(G) in vertices,
        "first_prefix_rank_columns_minus_1": first_closure,
        "checkpoints": checkpoints,
        "degree_min": min(degrees.values()) if degrees else 0,
        "degree_max": max(degrees.values()) if degrees else 0,
        "degree_mean": (sum(degrees.values()) / float(len(degrees))) if degrees else 0.0,
        "components": len(components),
        "largest_component": components[0] if components else 0,
        "two_core": two_core(edges),
        "actual_log_kernel_failures_posthoc": actual_kernel_failures,
        "posthoc_kernel_is_not_target_recovery": True,
    }


def standard_elliptic_curves(field, a, b, c, delta1, delta2):
    s1 = field(1) / delta1
    A2 = 2 * (-a*b**2 + 6*a**2*c - 9*b*c) / delta1
    A4 = (b**2 - 12*a*c) / delta1
    A6 = 4*c / delta1
    E1 = EllipticCurve(field, [0, s1*A2, 0, s1**2*A4, s1**3*A6])

    s2 = delta2
    B2 = a*b**3 - 27*b**2*c + 54*a*c**2
    B4 = (b**7 - 18*a*b**5*c + 54*a**2*b**3*c**2 +
          189*b**4*c**2 - 972*a*b**2*c**3 +
          729*a**2*c**4 + 729*b*c**4)
    B6 = -c * (2*b**3 - 9*a*b*c + 27*c**2)**3
    E2 = EllipticCurve(field, [0, s2*B2, 0, s2**2*B4, s2**3*B6])
    return E1, E2, s1, s2


def find_cell(p, seed):
    field = GF(p)
    R = PolynomialRing(field, "x")
    X = R.gen()
    rng = random.Random(int(int(seed) + 1000003 * int(p)))
    for attempt in range(1, 30000):
        a = field(rng.randrange(p))
        b = field(rng.randrange(1, p))
        c = field(rng.randrange(1, p))
        delta1 = (a**2*b**2 - 4*b**3 - 4*a**3*c +
                  18*a*b*c - 27*c**2)
        delta2 = b**3 - 27*c**2
        if delta1 == 0 or delta2 == 0:
            continue
        Ppoly = X**3 + a*X**2 + b*X + c
        Qpoly = 4*c*X**3 + b**2*X**2 + 2*b*c*X + c**2
        Fpoly = Ppoly * Qpoly
        if Fpoly.gcd(Fpoly.derivative()).degree() != 0:
            continue
        try:
            E1, E2, s1, s2 = standard_elliptic_curves(
                field, a, b, c, delta1, delta2
            )
        except Exception:
            continue
        order1 = Integer(E1.order())
        if not order1.is_prime(proof=False):
            continue
        if int(E1.j_invariant()) in (0, int(field(1728))):
            continue
        if E1.trace_of_frobenius() % p == 0:
            continue

        FF = FractionField(R)
        z = FF.gen()
        Pz = z**3 + a*z**2 + b*z + c
        Qz = 4*c*z**3 + b**2*z**2 + 2*b*c*z + c**2
        f1 = z**2 / Pz
        f2 = ((b*z + 3*c)**2 *
              ((b**3 - 4*a*b*c + 9*c**2)*z + c*(b**2 - 3*a*c)) / Qz)
        return {
            "p": p,
            "field": field,
            "ring": R,
            "X": X,
            "a": a,
            "b": b,
            "c": c,
            "delta1": delta1,
            "delta2": delta2,
            "Ppoly": Ppoly,
            "Qpoly": Qpoly,
            "Fpoly": Fpoly,
            "E1": E1,
            "E2": E2,
            "s1": s1,
            "s2": s2,
            "f1": f1,
            "f2": f2,
            "df1": f1.derivative(),
            "df2": f2.derivative(),
            "order1": order1,
            "order2": Integer(E2.order()),
            "attempt": attempt,
        }
    raise RuntimeError("no generic prime-order degree-3 cell found for p=%d" % p)


def map_cover_point(cell, x, y):
    b, c = cell["b"], cell["c"]
    if (x == 0 or cell["Ppoly"](x) == 0 or
            cell["Qpoly"](x) == 0 or b*x + 3*c == 0):
        return None, "exceptional_denominator"
    try:
        u1 = cell["f1"](x)
        v1 = y * cell["df1"](x) / x
        P1 = cell["E1"](cell["s1"]*u1, cell["s1"]**2*v1)
        u2 = cell["f2"](x)
        v2 = y * cell["df2"](x) / (b*x + 3*c)
        P2 = cell["E2"](cell["s2"]*u2, cell["s2"]**2*v2)
        return {"x": int(x), "y": int(y), "e1": point_key(P1), "e2": point_key(P2)}, None
    except Exception as exc:
        return None, "map_failure:%s" % exc


def enumerate_affine_cover(cell):
    field = cell["field"]
    records = []
    exceptions = {}
    affine_points = 0
    for x_int in range(int(field.order())):
        x = field(x_int)
        rhs = cell["Fpoly"](x)
        root = canonical_sqrt(rhs)
        if root is None:
            continue
        ys = [root] if root == 0 else [root, -root]
        for y in ys:
            affine_points += 1
            record, error = map_cover_point(cell, x, y)
            if error is not None:
                exceptions[error] = exceptions.get(error, 0) + 1
            else:
                records.append(record)
    return records, affine_points, exceptions


def full_fibers(records, label):
    fibers = {}
    for record in records:
        fibers.setdefault(tuple(record[label]), []).append(record)
    return fibers, {str(size): sum(1 for values in fibers.values() if len(values) == size)
                    for size in sorted(set(len(v) for v in fibers.values()))}


def relation_edges(cell, fibers2):
    E1 = cell["E1"]
    complete = []
    sums = {}
    for key, records in fibers2.items():
        if len(records) != 3:
            continue
        edge = tuple(tuple(record["e1"]) for record in records)
        total = E1(0)
        for e1_key in edge:
            total += point_from_key(E1, e1_key)
        total_key = point_key(total)
        sums[total_key] = sums.get(total_key, 0) + 1
        complete.append({"e2": key, "edge": edge, "sum": total_key})
    if not sums:
        return [], E1(0), {}, 0, 0
    mode_key = max(sums, key=lambda key: (sums[key], key))
    K = point_from_key(E1, mode_key)
    production = [item["edge"] for item in complete if item["sum"] == mode_key]
    mismatch = len(complete) - len(production)
    wrong_sign_equal = 0
    for edge in production:
        points = [point_from_key(E1, key) for key in edge]
        if -points[0] + points[1] + points[2] == K:
            wrong_sign_equal += 1
    return production, K, sums, mismatch, wrong_sign_equal


def generic_edges(E, K, count, seed):
    rng = random.Random(int(seed))
    points = [P for P in E if P != E(0)]
    edges = []
    for _ in range(count):
        A = points[rng.randrange(len(points))]
        B = points[rng.randrange(len(points))]
        C = K - A - B
        edges.append((point_key(A), point_key(B), point_key(C)))
    return edges


def shuffled_control(records, E, K, count, seed):
    rng = random.Random(int(seed))
    labels = [tuple(record["e1"]) for record in records]
    rng.shuffle(labels)
    triples = [tuple(labels[3*i:3*i+3]) for i in range(min(count, len(labels)//3))]
    hits = 0
    for edge in triples:
        if sum((point_from_key(E, key) for key in edge), E(0)) == K:
            hits += 1
    return {"triples": len(triples), "constant_sum_hits": hits}


def factor_base_profiles(cell, edges, generic, K, G, seed):
    E = cell["E1"]
    order = int(cell["order1"])
    all_keys = [point_key(P) for P in E if P != E(0)]
    all_keys.sort(key=lambda key: score("fb", seed, key))
    pairs_by_vertex = {}
    for edge in edges:
        for i, target in enumerate(edge):
            if edge.count(target) != 1:
                continue
            pair = tuple(sorted([edge[(i + 1) % 3], edge[(i + 2) % 3]]))
            pairs_by_vertex.setdefault(target, set()).add(pair)

    sizes = sorted(set(max(2, min(len(all_keys), int(round(order**alpha))))
                       for alpha in [1.0/3.0, 0.5, 2.0/3.0]))
    rows = []
    for B in sizes:
        fb_list = list(all_keys[:B])
        g_key = point_key(G)
        if g_key not in fb_list:
            fb_list[-1] = g_key
        fb = set(fb_list)
        prod_edges = [edge for edge in edges if all(key in fb for key in edge)]
        gen_edges = [edge for edge in generic if all(key in fb for key in edge)]

        target_keys = [key for key in all_keys if key not in fb]
        target_keys.sort(key=lambda key: score("target", seed, B, key))
        target_keys = target_keys[:min(32, len(target_keys))]
        prod_attempts = 0
        prod_hits = 0
        matched_attempts = 0
        matched_hits = 0
        rng = random.Random(int(int(seed) + 7919 * int(B)))
        points = [point_from_key(E, key) for key in all_keys]
        for target_key in target_keys:
            target = point_from_key(E, target_key)
            pairs = sorted(pairs_by_vertex.get(target_key, set()))
            prod_attempts += len(pairs)
            prod_hits += sum(1 for pair in pairs if pair[0] in fb and pair[1] in fb)
            for _ in range(len(pairs)):
                A = points[rng.randrange(len(points))]
                C = K - target - A
                matched_attempts += 1
                if point_key(A) in fb and point_key(C) in fb:
                    matched_hits += 1

        allowed = set(fb)
        if K != E(0):
            allowed.add(point_key(K))
        col_index = {key: i for i, key in enumerate(sorted(allowed))}
        basis = {}
        for edge in prod_edges:
            add_to_basis(row_dict(edge, point_key(K), order), basis, col_index, order)
        needed = max(0, len(allowed) - 1)
        rows.append({
            "B": B,
            "production_all_in_fb_edges": len(prod_edges),
            "generic_all_in_fb_edges": len(gen_edges),
            "production_rank": len(basis),
            "columns_including_K": len(allowed),
            "rank_needed_for_scale_only": needed,
            "rank_gate": bool(len(basis) >= needed),
            "blind_targets": len(target_keys),
            "cofiber_pair_attempts": prod_attempts,
            "cofiber_fb_hits": prod_hits,
            "matched_ec_addition_attempts": matched_attempts,
            "matched_ec_addition_fb_hits": matched_hits,
            "expected_hit_probability_per_pair": (B / float(order - 1))**2,
            "public_target_recovered": False,
            "target_recovery_reason": "no augmented K/G/Q public solve in affine falsification probe",
        })
    return rows


def run_cell(p, seed):
    started = time.time()
    cell = find_cell(p, seed)
    records, affine_points, exceptions = enumerate_affine_cover(cell)
    fibers1, hist1 = full_fibers(records, "e1")
    fibers2, hist2 = full_fibers(records, "e2")
    edges, K, sum_hist, mismatches, wrong_sign_equal = relation_edges(cell, fibers2)
    E1 = cell["E1"]
    order = cell["order1"]
    G = E1.gens()[0]
    generic = generic_edges(E1, K, len(edges), seed + p)

    production_profile = graph_profile(edges, E1, order, K, G, "tcd-%d" % p)
    generic_profile = graph_profile(generic, E1, order, K, G, "generic-%d" % p)
    fb_profiles = factor_base_profiles(cell, edges, generic, K, G, seed + p)
    shuffle = shuffled_control(records, E1, K, len(edges), seed + 17*p)

    cover_cost_floor = affine_points + 2*len(records) + 3*len(edges)
    result = {
        "p": p,
        "parameters": {"a": int(cell["a"]), "b": int(cell["b"]), "c": int(cell["c"])},
        "cell_search_attempt": cell["attempt"],
        "delta1": int(cell["delta1"]),
        "delta2": int(cell["delta2"]),
        "E1_order": int(order),
        "E2_order": int(cell["order2"]),
        "E1_j": int(E1.j_invariant()),
        "E2_j": int(cell["E2"].j_invariant()),
        "E1_generator": point_key(G),
        "affine_cover_points": affine_points,
        "mapped_unexceptional_points": len(records),
        "exception_counts": exceptions,
        "phi1_fiber_size_histogram": hist1,
        "phi2_fiber_size_histogram": hist2,
        "complete_phi2_fibers": sum(1 for values in fibers2.values() if len(values) == 3),
        "production_relations": len(edges),
        "fiber_sum_K": point_key(K),
        "fiber_sum_histogram": {str(key): value for key, value in sum_hist.items()},
        "constant_sum_mismatches": mismatches,
        "wrong_sign_equal_K": wrong_sign_equal,
        "shuffled_label_control": shuffle,
        "production_graph": production_profile,
        "ec_addition_synthetic_cofiber": generic_profile,
        "factor_base_profiles": fb_profiles,
        "rho_ops": rho_ops(order),
        "affine_enumeration_charged_floor": cover_cost_floor,
        "charged_floor_over_rho": cover_cost_floor / rho_ops(order),
        "public_label_generation_implemented": False,
        "projective_verifier_passed": False,
        "augmented_public_target_solve_passed": False,
        "runtime_seconds": time.time() - started,
    }
    result["affine_correctness_pass"] = bool(
        len(edges) > 0 and mismatches == 0 and wrong_sign_equal == 0 and
        production_profile["actual_log_kernel_failures_posthoc"] == 0
    )
    return result


def fit_exponent(cells, field):
    pairs = [(math.log(float(c["E1_order"])), math.log(float(c[field])))
             for c in cells if c.get(field, 0) > 0]
    if len(pairs) < 2:
        return None
    mx = sum(x for x, _ in pairs) / len(pairs)
    my = sum(y for _, y in pairs) / len(pairs)
    den = sum((x - mx)**2 for x, _ in pairs)
    if den == 0:
        return None
    return sum((x - mx)*(y - my) for x, y in pairs) / den


def main():
    out_path = parse_out()
    cells = []
    errors = []
    print("PO-transfer-006 TCD affine falsification probe")
    for p in PRIMES:
        try:
            cell = run_cell(p, SEED)
            cells.append(cell)
            print("p=%d N=%d edges=%d rank=%d generic_rank=%d floor/rho=%.2f" % (
                p, cell["E1_order"], cell["production_relations"],
                cell["production_graph"]["rank"],
                cell["ec_addition_synthetic_cofiber"]["rank"],
                cell["charged_floor_over_rho"],
            ))
        except Exception as exc:
            errors.append({"p": p, "error": str(exc)})
            print("p=%d ERROR %s" % (p, exc))

    correctness = bool(len(cells) == len(PRIMES) and
                       all(c["affine_correctness_pass"] for c in cells))
    any_rank_gate = any(row["rank_gate"] for c in cells for row in c["factor_base_profiles"])
    any_target_hit_excess = any(
        row["cofiber_fb_hits"] >= 4*max(1, row["matched_ec_addition_fb_hits"])
        and row["cofiber_fb_hits"] > 0
        for c in cells for row in c["factor_base_profiles"]
    )
    if not correctness:
        verdict = "inconclusive_correctness_failure"
    elif any_rank_gate or any_target_hit_excess:
        verdict = "inconclusive_affine_signal_requires_projective_verifier"
    else:
        verdict = "negative_fixed_degree_affine_gate"

    result = {
        "experiment": "PO-transfer-006 Trielliptic Cofiber Decomposition",
        "status": "TOY-EVIDENCE / UNRAMIFIED-AFFINE / MODEL-BOUND",
        "timestamp": time.asctime(),
        "source_path": source_path(),
        "source_sha256": source_hash(),
        "seed": SEED,
        "primes": PRIMES,
        "cells": cells,
        "errors": errors,
        "all_affine_correctness_pass": correctness,
        "any_small_factor_base_rank_gate": any_rank_gate,
        "any_four_x_target_hit_excess": any_target_hit_excess,
        "charged_floor_exponent_fit": fit_exponent(cells, "affine_enumeration_charged_floor"),
        "verdict": verdict,
        "structural_success": False,
        "algorithmic_success": False,
        "fail_closed_reasons": [
            "full affine cover enumeration is a toy oracle",
            "exceptional and projective fibers are not replayed",
            "K is inferred from unramified affine fibers",
            "no augmented public K/G/Q target solve",
            "no separately charged cubic quotient-label inversion",
        ],
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w") as handle:
        json.dump(clean(result), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("verdict=%s out=%s" % (verdict, out_path))


main()
