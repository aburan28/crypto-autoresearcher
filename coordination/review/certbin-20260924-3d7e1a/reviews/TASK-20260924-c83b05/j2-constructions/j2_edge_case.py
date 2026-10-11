#!/usr/bin/env python3
"""J2 (3): multilinear reduction of v_j * b when v_j already divides monomials
of b. TASK-20260924-c83b05.

Checks the archived engine's three multiplication sites against the
validator's own literal multilinear arithmetic (v_i^2 = v_i, product of
monomials = union of variable sets, coefficients mod 2):
  (i)   Closure.products (the W_D products v_j * b, b in B_{<=D-1}) at
        (nv, D) = (18, 4) and (18, 5): hand-built cases where v_j divides some,
        all or none of the monomials of b, including cases whose correct product
        is 0 (full cancellation) and cases with pairs m, m u {j} (cancellation of
        one monomial), plus 200 random dense b per (D) with every j;
  (ii)  Closure.build_M (rows mu * f_k) on a hand-built system whose f_k share
        variables with the multipliers mu, so that mu * f_k reduces (and
        cancels) -- every row compared;
  (iii) the certificate multiplier push (m | v_j) in Closure._extract, by
        evaluating certificates of refutations whose trace crosses an
        iteration boundary (small systems) with own arithmetic -- done in
        j2_seminaive_stress.py; here a hand-built one is added.
Output: j2-constructions/edge_case_results.json
"""
import json
import os
import resource
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
resource.setrlimit(resource.RLIMIT_AS, (3 * 1024 ** 3, 3 * 1024 ** 3))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import own_algebra as oa  # noqa: E402


def M(*vs):
    s = 0
    for v in vs:
        s |= 1 << v
    return s


def own_product(j, masks):
    acc = {}
    for m in masks:
        x = m | (1 << j)
        acc[x] = acc.get(x, 0) ^ 1
    return sorted(x for x, p in acc.items() if p)


def engine_product(cl, j, masks):
    row = cl.vec(masks)[None, :]
    P = cl.products(row)            # j-major: row j*n + f
    d = cl.unpack(P[j:j + 1])[0]
    return sorted(int(cl.col_mask[c]) for c in np.flatnonzero(d))


def main():
    sys.path.insert(0, IMPL)
    from closure import Closure, eval_cert
    res = {"task_id": "TASK-20260924-c83b05", "joint": "J2", "construction": "multilinear reduction edge cases"}
    hand = [
        ("v0 * v0 -> v0 (v_j divides the only monomial: kept, not moved, not dropped)", 0, [M(0)], [M(0)]),
        ("v0 * (v0 + v1) -> v0 + v0v1", 0, [M(0), M(1)], [M(0), M(0, 1)]),
        ("v0 * (v1 + v0v1) -> 0 (m and m u {j} cancel)", 0, [M(1), M(0, 1)], []),
        ("v0 * (1 + v0) -> 0", 0, [0, M(0)], []),
        ("v0 * (v0v1v2 + v1v2 + v3) -> v0v3", 0, [M(0, 1, 2), M(1, 2), M(3)], [M(0, 3)]),
        ("v1 * v0v1v2 -> v0v1v2 (degree 3, v_j divides)", 1, [M(0, 1, 2)], [M(0, 1, 2)]),
        ("v17 * (v15v16v17 + v15v16) -> 0", 17, [M(15, 16, 17), M(15, 16)], []),
        ("v9 * (1 + v9 + v0 + v0v9 + v0v1v9 + v0v1) -> 0", 9, [0, M(9), M(0), M(0, 9), M(0, 1, 9), M(0, 1)], []),
        ("v5 * (1 + v5 + v6) -> v5v6", 5, [0, M(5), M(6)], [M(5, 6)]),
        ("v2 * (v2v3v4 + v3v4 + v2v5 + v5 + v2) -> v2", 2, [M(2, 3, 4), M(3, 4), M(2, 5), M(5), M(2)], [M(2)]),
    ]
    out_cases = []
    allok = True
    for D in (4, 5):
        cl = Closure(18, D, 17)
        for name, j, b, expect in hand:
            own = own_product(j, b)
            eng = engine_product(cl, j, b)
            ok = (own == sorted(expect)) and (eng == own)
            allok &= ok
            out_cases.append({"D": D, "case": name, "j": j, "b": b, "expected": sorted(expect), "own": own,
                              "engine": eng, "ok": ok})
    res["hand_cases"] = out_cases
    res["hand_cases_all_ok"] = allok
    # random dense b with every j
    rng = np.random.default_rng(2026092483051)
    rand_ok, rand_n = True, 0
    for D in (4, 5):
        cl = Closure(18, D, 17)
        low = [m for m in oa.monomials(18, D - 1)]
        for t in range(100):
            b = [m for m in low if rng.random() < 0.3]
            row = cl.vec(b)[None, :]
            P = cl.products(row)
            for j in range(18):
                d = cl.unpack(P[j:j + 1])[0]
                eng = sorted(int(cl.col_mask[c]) for c in np.flatnonzero(d))
                rand_n += 1
                if eng != own_product(j, b):
                    rand_ok = False
    res["random_dense_b"] = {"seed": 2026092483051, "products_checked": rand_n, "all_equal_own": rand_ok}
    # (ii) build_M with mu sharing variables with f_k
    eqs = [[M(0, 1), M(0), M(2)], [M(0, 1), 0], [M(3), M(3, 4), M(4)], [M(0), M(1), M(0, 1), 0]] + [[M(k)] for k in range(5, 18)]
    eqs = eqs[:17]
    ok_rows = {}
    for D in (4, 5):
        cl = Closure(18, D, 17)
        Mp = cl.build_M(eqs)
        dense = cl.unpack(Mp)
        sp = oa.Space(18, D)
        own = oa.macaulay_rows(sp, eqs, D)
        bad = 0
        cancel_rows = 0
        for r in range(cl.R):
            eng = sp.poly(int(cl.col_mask[c]) for c in np.flatnonzero(dense[r]))
            if eng != own[r]:
                bad += 1
            mu, k = cl.row_pair(r)
            if len(own_product_mu(mu, eqs[k])) < len(eqs[k]):
                cancel_rows += 1
        ok_rows[f"D{D}"] = {"rows": cl.R, "rows_differing_from_own": bad, "rows_with_reduction_cancellation": cancel_rows}
    res["build_M_with_shared_variables"] = ok_rows
    # (iii) a refutation first reached at iteration >= 2 (so its certificate
    # trace crosses two iteration boundaries and pushes v_j multipliers onto
    # rows whose mu may already contain v_j); searched deterministically among
    # sparse systems nv = 8, D = 3, neq = 6 (first attempt nv = 5, neq = 4 with
    # 1..3 monomials found none in 20000 draws; disclosed).
    found = None
    rng2 = np.random.default_rng(2026092483052)
    NV, DD, NEQ = 8, 3, 6
    cl = Closure(NV, DD, NEQ)
    sp = oa.Space(NV, DD)
    allq = oa.monomials(NV, 2)
    tries = 0
    for t in range(50000):
        tries = t + 1
        eqs5 = []
        for _ in range(NEQ):
            k = int(rng2.integers(2, 5))
            pick = rng2.choice(len(allq), size=k, replace=False)
            eqs5.append(sorted(int(allq[i]) for i in pick))
        rec, cert = cl.w_closure(eqs5, want_cert=True)
        if rec["one"] and rec["one_first_iteration"] >= 2:
            lit, _, _ = oa.literal_W(sp, eqs5, DD)
            acc = {}
            for mu, k in cert:
                for m in eqs5[k]:
                    x = mu | m
                    acc[x] = acc.get(x, 0) ^ 1
            s = sorted(x for x, p in acc.items() if p)
            divides = sum(1 for mu, k in cert for m in eqs5[k] if (mu & m))
            found = {"draw": t, "nv": NV, "D": DD, "neq": NEQ, "eqs": eqs5, "engine": rec, "literal_dims": lit["dims"],
                     "literal_one_first_iteration": lit["one_first_iteration"],
                     "certificate": [[[i for i in range(NV) if (mu >> i) & 1], k] for mu, k in cert],
                     "certificate_max_deg_mu": max(bin(mu).count("1") for mu, k in cert),
                     "certificate_pairs_where_mu_shares_a_variable_with_a_monomial_of_f_k": divides,
                     "own_sum": s, "own_sum_is_1": s == [0], "engine_eval_cert_is_1": eval_cert(cert, eqs5) == [0],
                     "literal_agrees": lit["dims"] == rec["dims"] and lit["one_first_iteration"] == rec["one_first_iteration"]}
            break
    res["search_draws"] = tries
    res["hand_found_refutation_first_at_iteration_ge2"] = found
    res["pass"] = bool(allok and rand_ok and all(v["rows_differing_from_own"] == 0 for v in ok_rows.values())
                       and found is not None and found["own_sum_is_1"] and found["literal_agrees"])
    json.dump(res, open(os.path.join(HERE, "edge_case_results.json"), "w"), indent=1)
    print(json.dumps({"hand_cases_all_ok": allok, "random": res["random_dense_b"], "build_M": ok_rows,
                      "found": None if found is None else {k: found[k] for k in ("draw", "own_sum_is_1", "literal_agrees",
                                                                                  "certificate_pairs_where_mu_shares_a_variable_with_a_monomial_of_f_k")},
                      "pass": res["pass"]}))


def own_product_mu(mu, masks):
    acc = {}
    for m in masks:
        x = m | mu
        acc[x] = acc.get(x, 0) ^ 1
    return sorted(x for x, p in acc.items() if p)


if __name__ == "__main__":
    main()
