#!/usr/bin/env sage
# Independent public replay for PO-transfer-006's unramified affine probe.

import hashlib
import json
import math
import os
import random
import sys


BASE = "/Volumes/Volume/autolab/experiments/ecdlp_isogeny"
DEFAULT_RESULT = os.path.join(BASE, "po_transfer_006_result.json")
DEFAULT_OUT = os.path.join(BASE, "po_transfer_006_verify.json")
SOURCE = os.path.join(BASE, "po_transfer_006_trielliptic_cofiber.sage")


def arg(flag, default):
    args = list(sys.argv[1:])
    return args[args.index(flag) + 1] if flag in args else default


def file_hash(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def score(*parts):
    return hashlib.sha256("|".join(str(x) for x in parts).encode("ascii")).hexdigest()


def pkey(P):
    if P == P.curve()(0):
        return ("O",)
    return (int(P[0]), int(P[1]))


def from_key(E, key):
    return E(0) if len(key) == 1 else E(key[0], key[1])


def csqrt(v):
    if v == 0:
        return v
    if not v.is_square():
        return None
    r = v.sqrt()
    return r if int(r) <= int(-r) else -r


def edge_key(edge):
    return tuple(sorted(tuple(k) for k in edge))


def build(cell_json):
    p = int(cell_json["p"])
    F = GF(p)
    R = PolynomialRing(F, "x")
    X = R.gen()
    a = F(cell_json["parameters"]["a"])
    b = F(cell_json["parameters"]["b"])
    c = F(cell_json["parameters"]["c"])
    d1 = a**2*b**2 - 4*b**3 - 4*a**3*c + 18*a*b*c - 27*c**2
    d2 = b**3 - 27*c**2
    P = X**3 + a*X**2 + b*X + c
    Q = 4*c*X**3 + b**2*X**2 + 2*b*c*X + c**2
    H = P*Q

    s1 = F(1)/d1
    A2 = 2*(-a*b**2 + 6*a**2*c - 9*b*c)/d1
    A4 = (b**2 - 12*a*c)/d1
    A6 = 4*c/d1
    E1 = EllipticCurve(F, [0, s1*A2, 0, s1**2*A4, s1**3*A6])
    s2 = d2
    B2 = a*b**3 - 27*b**2*c + 54*a*c**2
    B4 = (b**7 - 18*a*b**5*c + 54*a**2*b**3*c**2 +
          189*b**4*c**2 - 972*a*b**2*c**3 + 729*a**2*c**4 + 729*b*c**4)
    B6 = -c*(2*b**3 - 9*a*b*c + 27*c**2)**3
    E2 = EllipticCurve(F, [0, s2*B2, 0, s2**2*B4, s2**3*B6])

    FF = FractionField(R)
    z = FF.gen()
    Pz = z**3 + a*z**2 + b*z + c
    Qz = 4*c*z**3 + b**2*z**2 + 2*b*c*z + c**2
    f1 = z**2/Pz
    f2 = ((b*z+3*c)**2 *
          ((b**3-4*a*b*c+9*c**2)*z+c*(b**2-3*a*c))/Qz)
    return {
        "p": p, "F": F, "H": H, "P": P, "Q": Q, "a": a, "b": b,
        "c": c, "d1": d1, "d2": d2, "E1": E1, "E2": E2,
        "s1": s1, "s2": s2, "f1": f1, "f2": f2,
        "df1": f1.derivative(), "df2": f2.derivative(),
    }


def enumerate_records(cell):
    records = []
    affine = 0
    exceptions = 0
    map_failures = 0
    F, E1, E2 = cell["F"], cell["E1"], cell["E2"]
    b, c = cell["b"], cell["c"]
    for xi in range(cell["p"]):
        x = F(xi)
        r = csqrt(cell["H"](x))
        if r is None:
            continue
        ys = [r] if r == 0 else [r, -r]
        for y in ys:
            affine += 1
            if x == 0 or cell["P"](x) == 0 or cell["Q"](x) == 0 or b*x+3*c == 0:
                exceptions += 1
                continue
            try:
                u1 = cell["f1"](x)
                v1 = y*cell["df1"](x)/x
                A = E1(cell["s1"]*u1, cell["s1"]**2*v1)
                u2 = cell["f2"](x)
                v2 = y*cell["df2"](x)/(b*x+3*c)
                B = E2(cell["s2"]*u2, cell["s2"]**2*v2)
            except Exception:
                map_failures += 1
                continue
            records.append({"x": int(x), "y": int(y), "e1": pkey(A), "e2": pkey(B)})
    return records, affine, exceptions, map_failures


def hist(fibers):
    return {str(s): sum(1 for v in fibers.values() if len(v) == s)
            for s in sorted(set(len(v) for v in fibers.values()))}


def rank_edges(edges, E, order, K):
    kkey = pkey(K)
    vertices = sorted(set(key for edge in edges for key in edge) |
                      ({kkey} if kkey != ("O",) else set()))
    ci = {key: i for i, key in enumerate(vertices)}
    M = matrix(GF(order), len(edges), len(vertices), sparse=True)
    for i, edge in enumerate(edges):
        for key in edge:
            M[i, ci[key]] += 1
        if kkey != ("O",):
            M[i, ci[kkey]] -= 1
    return len(vertices), int(M.rank()), len(vertices)-int(M.rank())


def generic_edges(E, K, count, seed):
    rng = random.Random(int(seed))
    points = [P for P in E if P != E(0)]
    out = []
    for _ in range(count):
        A = points[rng.randrange(len(points))]
        B = points[rng.randrange(len(points))]
        C = K-A-B
        out.append((pkey(A), pkey(B), pkey(C)))
    return out


def shuffled(records, E, K, count, seed):
    rng = random.Random(int(seed))
    labels = [tuple(r["e1"]) for r in records]
    rng.shuffle(labels)
    triples = [tuple(labels[3*i:3*i+3]) for i in range(min(count, len(labels)//3))]
    hits = 0
    for edge in triples:
        total = E(0)
        for key in edge:
            total += from_key(E, key)
        hits += int(total == K)
    return len(triples), hits


def fb_replay(cell, edges, generic, K, G, result_rows, seed):
    E = cell["E1"]
    order = int(E.order())
    keys = [pkey(P) for P in E if P != E(0)]
    keys.sort(key=lambda key: score("fb", seed, key))
    pairs = {}
    for edge in edges:
        for i, target in enumerate(edge):
            if edge.count(target) == 1:
                pair = tuple(sorted([edge[(i+1) % 3], edge[(i+2) % 3]]))
                pairs.setdefault(target, set()).add(pair)
    replay = []
    for expected in result_rows:
        B = int(expected["B"])
        fb_list = list(keys[:B])
        if pkey(G) not in fb_list:
            fb_list[-1] = pkey(G)
        fb = set(fb_list)
        pe = [edge for edge in edges if all(key in fb for key in edge)]
        ge = [edge for edge in generic if all(key in fb for key in edge)]
        allowed = set(fb)
        if K != E(0):
            allowed.add(pkey(K))
        pv, prank, _ = rank_edges(pe, E, order, K)

        targets = [key for key in keys if key not in fb]
        targets.sort(key=lambda key: score("target", seed, B, key))
        targets = targets[:min(32, len(targets))]
        attempts = hits = mattempts = mhits = 0
        rng = random.Random(int(int(seed) + 7919*B))
        points = [from_key(E, key) for key in keys]
        for target_key in targets:
            target = from_key(E, target_key)
            target_pairs = sorted(pairs.get(target_key, set()))
            attempts += len(target_pairs)
            hits += sum(1 for pair in target_pairs if pair[0] in fb and pair[1] in fb)
            for _ in range(len(target_pairs)):
                A = points[rng.randrange(len(points))]
                C = K-target-A
                mattempts += 1
                mhits += int(pkey(A) in fb and pkey(C) in fb)
        replay.append({
            "B": B, "production_all_in_fb_edges": len(pe),
            "generic_all_in_fb_edges": len(ge), "production_rank": prank,
            "columns_including_K": len(allowed), "cofiber_pair_attempts": attempts,
            "cofiber_fb_hits": hits, "matched_ec_addition_attempts": mattempts,
            "matched_ec_addition_fb_hits": mhits,
        })
    return replay


def main():
    result_path = arg("--result", DEFAULT_RESULT)
    out_path = arg("--out", DEFAULT_OUT)
    with open(result_path) as handle:
        result = json.load(handle)
    checks = []
    rows = []
    source_ok = file_hash(SOURCE) == result["source_sha256"]
    checks.append({"name": "source_hash", "ok": source_ok})

    for expected in result["cells"]:
        cell = build(expected)
        records, affine, exceptions, map_failures = enumerate_records(cell)
        f1 = {}
        f2 = {}
        for record in records:
            f1.setdefault(tuple(record["e1"]), []).append(record)
            f2.setdefault(tuple(record["e2"]), []).append(record)
        complete = []
        sums = {}
        for records2 in f2.values():
            if len(records2) != 3:
                continue
            edge = tuple(tuple(r["e1"]) for r in records2)
            total = cell["E1"](0)
            for key in edge:
                total += from_key(cell["E1"], key)
            sums[pkey(total)] = sums.get(pkey(total), 0) + 1
            complete.append((edge, pkey(total)))
        mode = max(sums, key=lambda key: (sums[key], key))
        K = from_key(cell["E1"], mode)
        edges = [edge for edge, total in complete if total == mode]
        wrong = 0
        for edge in edges:
            A, B, C = [from_key(cell["E1"], key) for key in edge]
            wrong += int(-A+B+C == K)
        N = int(cell["E1"].order())
        G = cell["E1"].gens()[0]
        generic = generic_edges(cell["E1"], K, len(edges), int(result["seed"])+cell["p"])
        pv, pr, pn = rank_edges(edges, cell["E1"], N, K)
        gv, gr, gn = rank_edges(generic, cell["E1"], N, K)
        st, sh = shuffled(records, cell["E1"], K, len(edges), int(result["seed"])+17*cell["p"])
        replay_fb = fb_replay(cell, edges, generic, K, G,
                              expected["factor_base_profiles"], int(result["seed"])+cell["p"])
        fb_ok = True
        fields = ["B", "production_all_in_fb_edges", "generic_all_in_fb_edges",
                  "production_rank", "columns_including_K", "cofiber_pair_attempts",
                  "cofiber_fb_hits", "matched_ec_addition_attempts",
                  "matched_ec_addition_fb_hits"]
        for got, exp in zip(replay_fb, expected["factor_base_profiles"]):
            fb_ok = fb_ok and all(got[name] == exp[name] for name in fields)

        cell_checks = {
            "orders": N == expected["E1_order"] and int(cell["E2"].order()) == expected["E2_order"],
            "discriminants": int(cell["d1"]) == expected["delta1"] and int(cell["d2"]) == expected["delta2"],
            "map_failures_zero": map_failures == 0,
            "affine_counts": affine == expected["affine_cover_points"] and
                             len(records) == expected["mapped_unexceptional_points"],
            "exception_count": exceptions == sum(expected["exception_counts"].values()),
            "fiber_histograms": hist(f1) == expected["phi1_fiber_size_histogram"] and
                                hist(f2) == expected["phi2_fiber_size_histogram"],
            "relation_count": len(edges) == expected["production_relations"],
            "constant_sum": mode == tuple(expected["fiber_sum_K"]) and
                            len(complete) == len(edges),
            "wrong_sign": wrong == expected["wrong_sign_equal_K"] == 0,
            "production_rank": (pv, pr, pn) == (
                expected["production_graph"]["vertices"],
                expected["production_graph"]["rank"],
                expected["production_graph"]["nullity"],
            ),
            "generic_rank": (gv, gr, gn) == (
                expected["ec_addition_synthetic_cofiber"]["vertices"],
                expected["ec_addition_synthetic_cofiber"]["rank"],
                expected["ec_addition_synthetic_cofiber"]["nullity"],
            ),
            "shuffled_control": (st, sh) == (
                expected["shuffled_label_control"]["triples"],
                expected["shuffled_label_control"]["constant_sum_hits"],
            ),
            "factor_base_profiles": fb_ok,
        }
        ok = all(cell_checks.values())
        rows.append({"p": cell["p"], "ok": ok, "checks": cell_checks})
        checks.append({"name": "cell_%d" % cell["p"], "ok": ok})

    verified = all(item["ok"] for item in checks)
    output = {
        "experiment": "PO-transfer-006 independent affine replay",
        "result_path": result_path,
        "result_sha256": file_hash(result_path),
        "source_path": SOURCE,
        "source_sha256": file_hash(SOURCE),
        "checks": checks,
        "cells": rows,
        "verified": verified,
        "scope": "unramified affine fibers only; not a projective verifier",
    }
    with open(out_path, "w") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("VERIFIED" if verified else "FAILED", out_path)
    if not verified:
        raise SystemExit(1)


main()
