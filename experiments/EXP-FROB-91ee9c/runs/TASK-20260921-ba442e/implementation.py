#!/usr/bin/env python
"""
Driver for TASK-20260921-ba442e (EXP-FROB-91ee9c specification.yaml v1, as
amended by DEC-20260921-e81e25 [v2], DEC-20260921-2f89d4 [v3], and
DEC-20260921-f93b43 [v4]).

FULL COMPLETION attempt of FROB-EXT-q13n7 (q=13, n=7), curve index 0 only:
  - independent object-curve search/verification (object_search from
    work/core.py, which performs the FULL object_selection eligibility test
    including the Frobenius scalar condition ord_N(mu)=n verified by
    exhaustive charged lookup against independent point arithmetic --
    something RUN-FROB-91ee9c-7119f2's probe explicitly did NOT do)
  - object arm across all achievable partitions ([6], [4,2], [2,2,2])
  - C1 (closed-form baseline), C2 (corrected per-slot-independent pool
    construction from TASK-20260921-819bc0/DEC-20260921-2f89d4), C3 (random
    matched-cardinality, both declared seeds), C4 (matched null curve, its
    own point-counting call), C5 (trace identity), C6 (known-false configs),
    C7 (denominator-zero rule), C8 is satisfied by this run's separate
    checker.py (not part of this driver).

This file is a superset merge of:
  - TASK-20260921-819bc0/implementation.py (object arm + CORRECTED C2 pool)
  - TASK-20260921-51bc02/implementation.py (C3, C4)
  - TASK-20260914-7119f2/implementation.py (C1, C5, C6)
No logic in any of those three is changed; this file only adds C1/C5/C6 (from
the third) on top of the already-corrected C2 (from the first) and the
already-present C3/C4 (from the second), applied to a single named
(cell, curve) target instead of a multi-cell/multi-curve sweep.

Run under `sage -python implementation.py <cell> <q> <n> <A> <B> <N>
<seed1,seed2> [mem_limit_bytes]`. Writes a single JSON document to stdout
(delimited by RESULT_JSON_BEGIN/END lines) with the complete result. All
ratios are represented as [num, den] integer pairs (exact rationals).
"""
import sys, os, json, time, random, resource, itertools
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "work"))
from sage.all import GF, PolynomialRing, EllipticCurve, matrix, Integer, Zmod, factor, vector as svector
from core import (find_first_irreducible, field_setup, elt_to_vec_list, enc_elt,
                   order_ext_trace, frobenius_matrix, object_search)
from lattice import (all_set_partitions, build_kernels, build_change_of_basis,
                      cinv_to_pylist, vec_signature)


def frac(n, d):
    return [int(n), int(d)]


def frval(pair):
    return Fraction(int(pair[0]), int(pair[1]))


def build_field_and_frobenius(q, n):
    K, g = field_setup(q, n)
    z = K.gen()
    F = GF(q)
    M = frobenius_matrix(K, z, q, n)
    return K, g, z, F, M


def atomic_and_kernels(q, n, M, F):
    R = PolynomialRing(F, 'x')
    xx = R.gen()
    h = xx ** n - 1
    sqfree = h.is_squarefree()
    facs = list(h.factor())
    xminus1 = xx - 1
    atomic = sorted([f for f, e in facs if f != xminus1], key=lambda f: f.list())
    exps_ok = all(e == 1 for f, e in facs)
    kers, ker_x1 = build_kernels(atomic, xminus1, M, F, n)
    return {
        "xx": xx, "h": h, "squarefree": bool(sqfree), "facs_all_exp1": bool(exps_ok),
        "factor_list": [str(f) for f, e in facs],
        "atomic": atomic, "xminus1": xminus1, "kers": kers, "ker_x1": ker_x1,
    }


def poly_of_matrix(coeffs_const_first, M, F):
    n = M.nrows()
    from sage.all import matrix as smatrix
    result = smatrix.zero(F, n, n)
    Mp = smatrix.identity(F, n)
    for c in coeffs_const_first:
        result += c * Mp
        Mp = Mp * M
    return result


def c5_trace_identity(q, n, M, F, atomic_info):
    """C5: verbatim from TASK-20260914-7119f2/implementation.py."""
    kers = atomic_info["kers"]
    ker_x1 = atomic_info["ker_x1"]
    from sage.all import matrix as smatrix
    T = smatrix.zero(F, n, n)
    Mp = smatrix.identity(F, n)
    for i in range(n):
        T += Mp
        Mp = Mp * M
    kerT = T.right_kernel()
    hpoly_coeffs = [F(1)] * n
    hM = poly_of_matrix(hpoly_coeffs, M, F)
    T_eq_hM = bool(T == hM)
    sumspace = kers[0]
    for k in kers[1:]:
        sumspace = sumspace + k
    dim_sum = sum(k.dimension() for k in kers)
    is_direct = (dim_sum == sumspace.dimension())
    set_equal = bool(sumspace == kerT)
    x1_in_kerT = all(v in kerT for v in ker_x1.basis()) if ker_x1.dimension() > 0 else True
    return {
        "T_equals_hM": T_eq_hM,
        "dim_sum_nontrivial_kernels": int(sumspace.dimension()),
        "dim_sum_via_addition": int(dim_sum),
        "direct_sum_certified": bool(is_direct),
        "dim_ker_T": int(kerT.dimension()),
        "set_equality_sum_eq_kerT": set_equal,
        "expected_dim_n_minus_1": n - 1,
        "dim_matches_n_minus_1": bool(sumspace.dimension() == n - 1 and kerT.dimension() == n - 1),
        "dim_ker_x1": int(ker_x1.dimension()),
        "ker_x1_subset_kerT": bool(x1_in_kerT),
        "p_divides_n": bool(n % int(F.characteristic()) == 0),
    }, kerT


def achievable_multiset_table(atomic):
    labels = list(range(len(atomic)))
    degs = [int(f.degree()) for f in atomic]
    table = []
    for P in all_set_partitions(labels):
        multiset = sorted([sum(degs[i] for i in block) for block in P], reverse=True)
        table.append({"partition_blocks": [list(b) for b in P], "slot_dims": multiset})
    return table


def divisor_lattice_dims(atomic):
    labels = list(range(len(atomic)))
    degs = [int(f.degree()) for f in atomic]
    dims = set()
    for r in range(0, len(labels) + 1):
        for combo in itertools.combinations(labels, r):
            dims.add(sum(degs[i] for i in combo))
    return sorted(dims)


def build_partition_blocks_masks(P):
    return [sum(1 << i for i in block) for block in P]


def enumerate_subgroup_signatures(EK, Gpt, N, q, n, cinv_py, blocks):
    by_mask = {}
    pt = Gpt
    for k in range(1, N):
        xcoord = pt[0]
        vec_ints = elt_to_vec_list(xcoord, q, n)
        v0, mask = vec_signature(vec_ints, cinv_py, blocks, q)
        if not v0:
            by_mask.setdefault(mask, []).append(k)
        pt = pt + Gpt
    return by_mask


def sumset_mod_N(list_of_ksets, N):
    cur = set(list_of_ksets[0])
    for nxt in list_of_ksets[1:]:
        newcur = set()
        nxt_list = list(nxt)
        for a in cur:
            for b in nxt_list:
                newcur.add((a + b) % N)
        cur = newcur
    return cur


def compute_pm_Uneg(block_ksets, N):
    prod_sizes = 1
    for b in block_ksets:
        prod_sizes *= len(b)
    sumset = sumset_mod_N(block_ksets, N)
    sumset.discard(0)
    distinct = len(sumset)
    p_num, p_den = distinct, (N - 1)
    B_union = set()
    for b in block_ksets:
        B_union.update(b)
    Uneg_num = len(B_union)
    return {
        "p_m": frac(p_num, p_den),
        "distinct_targets": distinct,
        "prod_tuple_count": prod_sizes,
        "U_neg": frac(Uneg_num, 2),
        "B_union_size": Uneg_num,
        "block_sizes": [len(b) for b in block_ksets],
    }


def cost_ratio(U_num_den, p_num_den, extra):
    """C7: p_m=0 -> None (never 0, never infinity). Caller wraps this with an
    explicit denominator_zero flag and retains the exact numerator (see
    run_arm_partitions / c7_check below)."""
    Un, Ud = U_num_den
    pn, pd = p_num_den
    if pn == 0:
        return None
    numer = Un + (1 + extra) * Ud
    denom = Ud * pn
    numer2 = numer * pd
    denom2 = denom
    from math import gcd
    g = gcd(numer2, denom2)
    if g == 0:
        g = 1
    return frac(numer2 // g, denom2 // g)


def run_arm_partitions(by_mask, N, atomic, extra_values=(0, 8, 32)):
    labels = list(range(len(atomic)))
    degs = [int(f.degree()) for f in atomic]
    records = []
    for P in all_set_partitions(labels):
        block_masks = build_partition_blocks_masks(P)
        block_ksets = []
        empty_block = False
        for bm in block_masks:
            ks = []
            for mask, klist in by_mask.items():
                if (mask & ~bm) == 0:
                    ks.extend(klist)
            block_ksets.append(ks)
            if len(ks) == 0:
                empty_block = True
        block_dims = [sum(degs[i] for i in block) for block in P]
        rec = {"partition_blocks": [list(b) for b in P],
               "slot_count_m": len(P),
               "slot_dims": sorted(block_dims, reverse=True)}
        if empty_block:
            rec["status"] = "empty_base"
            rec["block_sizes"] = [len(b) for b in block_ksets]
            records.append(rec)
            continue
        stats = compute_pm_Uneg(block_ksets, N)
        rec.update(stats)
        pm = stats["p_m"]
        ratios = {}
        for extra in extra_values:
            if pm[0] == 0:
                ratios[str(extra)] = {"denominator_zero": True, "numerator": stats["U_neg"]}
            else:
                ratios[str(extra)] = {"denominator_zero": False,
                                       "value": cost_ratio(stats["U_neg"], pm, extra)}
        rec["cost_ratio_neg"] = ratios
        rec["status"] = "ok"
        records.append(rec)
    return records


def c1_check(by_mask, N, atomic):
    """C1: verbatim from TASK-20260914-7119f2/implementation.py."""
    B = []
    for mask, klist in by_mask.items():
        B.extend(klist)
    Bsize = len(B)
    closed_U = frac(Bsize, 2)
    closed_p1 = frac(Bsize, N - 1)
    enum_stats = compute_pm_Uneg([B], N)
    agree = (enum_stats["p_m"] == closed_p1) and (enum_stats["U_neg"] == closed_U)
    return {"closed_form_U_neg": closed_U, "closed_form_p_1": closed_p1,
            "enumerator_U_neg": enum_stats["U_neg"], "enumerator_p_1": enum_stats["p_m"],
            "agree": bool(agree)}


def c6_checks(by_mask, N, atomic, kers, F, n):
    """C6: verbatim from TASK-20260914-7119f2/implementation.py."""
    out = {}
    labels = list(range(len(atomic)))
    if len(labels) >= 1:
        blocks = [(0,), (0,)]
        index_sets = [set(b) for b in blocks]
        is_partition = (index_sets[0].isdisjoint(index_sets[1]) and
                         set().union(*index_sets) == set(labels[:1]))
        out["repeated_subspace_refused"] = not is_partition
    if len(labels) >= 2:
        blocks = [(0, 1), (1,)]
        index_sets = [set(b) for b in blocks]
        overlap = not index_sets[0].isdisjoint(index_sets[1])
        out["overlapping_index_sets_refused"] = bool(overlap)
    empty_block_ksets = [[]]
    stats0 = compute_pm_Uneg(empty_block_ksets, N)
    out["V_empty_p_m"] = stats0["p_m"]
    out["V_empty_denominator_zero_triggered"] = (stats0["p_m"][0] == 0)
    full_block = list(range(1, N))
    stats_full = compute_pm_Uneg([full_block], N)
    out["V_full_p_1"] = stats_full["p_m"]
    out["V_full_equals_one"] = (stats_full["p_m"][0] == stats_full["p_m"][1])
    return out


def c7_check(N):
    """C7: explicit re-demonstration of the denominator-zero rule using
    cost_ratio()/run_arm_partitions()'s own ratio-object convention (never 0,
    never infinity, numerator retained, never silently dropped from min/max)."""
    empty_stats = compute_pm_Uneg([[]], N)
    pm = empty_stats["p_m"]
    ratio_direct = cost_ratio(empty_stats["U_neg"], pm, 0)
    ratio_object = ({"denominator_zero": True, "numerator": empty_stats["U_neg"]}
                     if pm[0] == 0 else
                     {"denominator_zero": False, "value": cost_ratio(empty_stats["U_neg"], pm, 0)})
    return {
        "p_m_zero_config": pm,
        "cost_ratio_raw_return": ratio_direct,
        "cost_ratio_raw_is_None": ratio_direct is None,
        "ratio_object_reported": ratio_object,
        "numerator_retained_exact": ratio_object.get("numerator"),
        "never_reported_as_zero": (ratio_object.get("value") != [0, 1]),
        "never_reported_as_finite_placeholder": ("value" not in ratio_object),
        "rule_satisfied": bool(ratio_direct is None and ratio_object["denominator_zero"] is True
                                and "value" not in ratio_object),
    }


def find_generator(EK, K, q, n, cofactor):
    zgen = K.gen()
    for xvec in itertools.product(range(q), repeat=n):
        elt = K(0); pw = K(1)
        for i in range(n):
            if xvec[i]:
                elt += xvec[i] * pw
            pw *= zgen
        rhs = elt ** 3 + EK.a4() * elt + EK.a6()
        if rhs.is_square():
            y0 = rhs.sqrt()
            ys = sorted([y0, -y0], key=lambda e: enc_elt(e, q, n))
            for y in ys:
                P = EK(elt, y)
                cP = cofactor * P
                if not cP.is_zero():
                    return cP
    return None


def non_stable_subspace_of_dim(d, M, F, n, exclude=None):
    """C2 (CORRECTED per DEC-20260921-2f89d4), verbatim from
    TASK-20260921-819bc0/implementation.py."""
    from sage.all import VectorSpace
    if exclude is None:
        exclude = set()
    V = VectorSpace(F, n)
    stdbasis = [svector(F, [1 if i == j else 0 for i in range(n)]) for j in range(n)]
    for combo in itertools.combinations(range(n), d):
        if combo in exclude:
            continue
        W = V.subspace([stdbasis[i] for i in combo])
        stable = all((M * b) in W for b in W.basis())
        if not stable:
            witness = None
            for b in W.basis():
                if (M * b) not in W:
                    witness = b
                    break
            return W, witness, combo
    return None, None, None


def build_c2_pool(d, M, F, n, k):
    """CORRECTED C2 construction, verbatim from
    TASK-20260921-819bc0/implementation.py."""
    pool = []
    exclude = set()
    for _ in range(k):
        W, witness, combo = non_stable_subspace_of_dim(d, M, F, n, exclude=exclude)
        if W is None:
            break
        pool.append({"W": W, "witness": witness, "combo": combo})
        exclude.add(combo)
    return pool


def random_matched_subset(orig_ksets_per_slot, N, seed):
    """C3: verbatim from TASK-20260921-51bc02/implementation.py."""
    rng = random.Random(seed)
    all_pairs = list(range(1, (N - 1) // 2 + 1))
    result = []
    for ks in orig_ksets_per_slot:
        size = len(ks)
        npairs = size // 2
        odd = size % 2
        chosen_pairs = rng.sample(all_pairs, npairs) if npairs > 0 else []
        newset = []
        for r in chosen_pairs:
            newset.append(r)
            newset.append((N - r) % N)
        if odd:
            extra_r = rng.choice([p for p in all_pairs if p not in chosen_pairs])
            newset.append(extra_r)
        result.append(newset)
    return result


def c4_null_curve_search(q, n, K, N_object, log_rejected):
    """C4: verbatim from TASK-20260921-51bc02/implementation.py."""
    zgen = K.gen()
    for a in range(q):
        for b in range(q):
            Ap = zgen + a
            Bp = zgen + b
            disc = 4 * Ap ** 3 + 27 * Bp ** 2
            if disc == 0:
                log_rejected.append({"a": a, "b": b, "reason": "singular"})
                continue
            EK = EllipticCurve(K, [Ap, Bp])
            jp = EK.j_invariant()
            if jp ** q == jp:
                log_rejected.append({"a": a, "b": b, "reason": "j_in_subfield"})
                continue
            t0 = time.time()
            order = EK.order()
            order_wall = time.time() - t0
            fac = factor(order)
            primes_exp1 = [int(p) for p, e in fac if e == 1]
            cand = [p for p in primes_exp1 if N_object // 2 <= p <= 2 * N_object]
            if not cand:
                log_rejected.append({"a": a, "b": b, "reason": "no_matching_N", "order": int(order)})
                continue
            Np = max(cand)
            cofactor = order // Np
            return {"a": a, "b": b, "A": str(Ap), "B": str(Bp), "EK": EK, "N": Np,
                    "cofactor": int(cofactor), "order": int(order), "j_invariant": str(jp),
                    "order_count_wall_seconds": order_wall}
    return None


def object_arm_summary(obj_partitions):
    ok = [r for r in obj_partitions if r["status"] == "ok"]
    m1 = [r for r in ok if r["slot_count_m"] == 1]
    assert len(m1) == 1, "expected exactly one m=1 (coarsest) partition"
    coarsest = m1[0]
    coarsest_ratio = frval(coarsest["cost_ratio_neg"]["0"]["value"])
    vals = [(r, frval(r["cost_ratio_neg"]["0"]["value"])) for r in ok]
    argmax_r, argmax_v = max(vals, key=lambda t: t[1])
    argmin_r, argmin_v = min(vals, key=lambda t: t[1])
    I_val = coarsest_ratio / argmin_v
    spread_val = argmax_v / argmin_v
    return {
        "n_ok_partitions": len(ok),
        "coarsest": {"partition_blocks": coarsest["partition_blocks"], "slot_dims": coarsest["slot_dims"],
                     "ratio": [coarsest_ratio.numerator, coarsest_ratio.denominator]},
        "argmax": {"partition_blocks": argmax_r["partition_blocks"], "slot_dims": argmax_r["slot_dims"],
                   "ratio": [argmax_v.numerator, argmax_v.denominator]},
        "argmin": {"partition_blocks": argmin_r["partition_blocks"], "slot_dims": argmin_r["slot_dims"],
                   "ratio": [argmin_v.numerator, argmin_v.denominator]},
        "I": [I_val.numerator, I_val.denominator],
        "spread": [spread_val.numerator, spread_val.denominator],
    }


def arm_spread_summary(arm_partitions):
    ok = [r for r in arm_partitions if r.get("status") == "ok"]
    if not ok:
        return {"n_ok_partitions": 0, "spread": None, "reason": "no_ok_partitions"}
    vals = [(r, frval(r["cost_ratio_neg"]["0"]["value"])) for r in ok]
    argmax_r, argmax_v = max(vals, key=lambda t: t[1])
    argmin_r, argmin_v = min(vals, key=lambda t: t[1])
    spread_val = argmax_v / argmin_v
    return {
        "n_ok_partitions": len(ok),
        "argmax": {"partition_blocks": argmax_r["partition_blocks"], "slot_dims": argmax_r["slot_dims"],
                   "ratio": [argmax_v.numerator, argmax_v.denominator]},
        "argmin": {"partition_blocks": argmin_r["partition_blocks"], "slot_dims": argmin_r["slot_dims"],
                   "ratio": [argmin_v.numerator, argmin_v.denominator]},
        "spread": [spread_val.numerator, spread_val.denominator],
    }


def main(cell_name, q, n, A_expected, B_expected, N_expected, seeds, extra_values=(0, 8, 32)):
    t_start = time.time()
    timings = {}
    result = {"cell": cell_name, "q": q, "n": n, "seeds": list(seeds),
               "expected_target_curve": {"A": A_expected, "B": B_expected, "N": N_expected}}

    K, g, z, F, M = build_field_and_frobenius(q, n)
    result["field_modulus"] = str(g)
    atomic_info = atomic_and_kernels(q, n, M, F)
    result["factorisation"] = {
        "squarefree": atomic_info["squarefree"],
        "all_exponents_1": atomic_info["facs_all_exp1"],
        "factor_list": atomic_info["factor_list"],
        "atomic_factors": [str(f) for f in atomic_info["atomic"]],
    }
    c5, kerT = c5_trace_identity(q, n, M, F, atomic_info)
    result["C5"] = c5
    C, Cinv, blocks = build_change_of_basis(atomic_info["kers"], atomic_info["ker_x1"], F, n)
    cinv_py = cinv_to_pylist(Cinv, q)
    result["achievable_multiset_table"] = achievable_multiset_table(atomic_info["atomic"])
    result["divisor_lattice_dims"] = divisor_lattice_dims(atomic_info["atomic"])

    # ----------------------------------- independent object-curve search
    # object_search performs the FULL object_selection eligibility test,
    # including the Frobenius scalar condition ord_N(mu)=n verified by
    # exhaustive charged lookup against independent point arithmetic
    # (piG == mu*Gpt), which the prior probe (FROB-EXT-q13n7.probe.json)
    # explicitly did NOT perform. want_curves=1 stops the search after the
    # FIRST eligible curve is found and fully verified -- curve index 1 is
    # out of scope for this run per the amendment.
    t0 = time.time()
    acc, rejected = object_search(q, n, K, M, F, want_curves=1)
    timings["object_search_wall_seconds"] = time.time() - t0
    result["object_search_rejected_count"] = len(rejected)
    result["object_search_rejected_sample"] = rejected[:5]
    if len(acc) == 0:
        result["cell_status"] = "ineligible"
        result["cell_status_reason"] = "pool_exhausted_no_eligible_curve_on_independent_search"
        result["timing"] = {"wall_seconds": time.time() - t_start, **timings}
        return result

    found = acc[0]
    result["object_curve_found"] = found
    curve_matches_expected = (found["A"] == A_expected and found["B"] == B_expected and
                               found["N"] == N_expected)
    result["curve_search_matches_prior_probe"] = bool(curve_matches_expected)
    if not curve_matches_expected:
        result["cell_status"] = "instrument_finding_curve_mismatch"
        result["cell_status_reason"] = (
            "Independent object_search found a DIFFERENT curve than the prior probe's "
            f"recorded (A={A_expected},B={B_expected},N={N_expected}): found "
            f"A={found['A']},B={found['B']},N={found['N']}. Reported as an instrument "
            "finding per DEC-20260921-f93b43's explicit instruction, not silently "
            "preferring either value."
        )
        result["timing"] = {"wall_seconds": time.time() - t_start, **timings}
        return result

    A, B, N = found["A"], found["B"], found["N"]
    mu_verified = found["mu"]
    ord_mu_verified = found["ord_mu"]
    result["mu_scalar_condition"] = {
        "mu": mu_verified, "ord_N_mu": ord_mu_verified, "expected_n": n,
        "ord_N_mu_equals_n": bool(ord_mu_verified == n),
        "verification_method": (
            "exhaustive charged lookup: for every root mu of x^2 - a*x + q = 0 mod N with "
            "multiplicative_order()==n, independently verify pi(G) == mu*G by direct point "
            "arithmetic (Frobenius applied coordinatewise vs. scalar multiplication), per "
            "object_selection's text. This is the check the prior probe explicitly skipped "
            "(\"object-search-only probe\")."
        ),
    }

    # -------------------------------------------------- recompute the curve
    EK = EllipticCurve(K, [A, B])
    order = EK.order()
    fac = factor(order)
    exps = {int(p): int(e) for p, e in fac}
    if N not in exps or exps[N] != 1:
        result["cell_status"] = "instrument_invalidation"
        result["cell_status_reason"] = "target_N_not_exponent1_divisor_of_recomputed_order"
        result["recomputed_order"] = int(order)
        result["timing"] = {"wall_seconds": time.time() - t_start, **timings}
        return result
    cofactor = order // N
    j_inv = EK.j_invariant()
    result["curve_recomputed"] = {"A": A, "B": B, "N": N, "cofactor": int(cofactor),
                                   "order": int(order), "j_invariant": str(j_inv)}

    t0 = time.time()
    Gpt = find_generator(EK, K, q, n, cofactor)
    timings["find_generator_wall_seconds"] = time.time() - t0
    if Gpt is None or Gpt.order() != N:
        result["cell_status"] = "instrument_invalidation"
        result["cell_status_reason"] = "generator_not_found_or_order_mismatch"
        result["timing"] = {"wall_seconds": time.time() - t_start, **timings}
        return result
    result["generator_point"] = {"x": str(Gpt[0]), "y": str(Gpt[1]), "order_verified": int(Gpt.order())}

    t0 = time.time()
    by_mask = enumerate_subgroup_signatures(EK, Gpt, N, q, n, cinv_py, blocks)
    timings["object_arm_enumeration_wall_seconds"] = time.time() - t0

    obj_partitions = run_arm_partitions(by_mask, N, atomic_info["atomic"], extra_values)
    result["object_arm_partitions"] = obj_partitions
    obj_summary = object_arm_summary(obj_partitions)
    result["object_arm_summary"] = obj_summary
    result["cell_status"] = "ok"

    # ---------------------------------------------------------------- C1
    result["C1"] = c1_check(by_mask, N, atomic_info["atomic"])

    # ---------------------------------------------------------------- C6
    result["C6"] = c6_checks(by_mask, N, atomic_info["atomic"], atomic_info["kers"], F, n)

    # ---------------------------------------------------------------- C7
    result["C7"] = c7_check(N)

    # ---------------------------------------------------------------- C2 (FIXED)
    ok_partitions = [r for r in obj_partitions if r["status"] == "ok"]
    max_mult_by_dim = {}
    for r in ok_partitions:
        counts = {}
        for d in r["slot_dims"]:
            counts[d] = counts.get(d, 0) + 1
        for d, c in counts.items():
            if d == 0:
                continue
            max_mult_by_dim[d] = max(max_mult_by_dim.get(d, 0), c)
    result["C2_max_multiplicity_by_dim"] = {str(d): k for d, k in max_mult_by_dim.items()}

    c2_pool_by_dim = {}
    t0 = time.time()
    for d, k in sorted(max_mult_by_dim.items()):
        c2_pool_by_dim[d] = build_c2_pool(d, M, F, n, k)
    timings["c2_pool_search_wall_seconds"] = time.time() - t0

    t0 = time.time()
    c2_by_dim_raw = {}
    for d, pool in c2_pool_by_dim.items():
        entries = []
        for entry in pool:
            W = entry["W"]
            ks_in_W = []
            pt = Gpt
            for k in range(1, N):
                xcoord = pt[0]
                vec_ints = elt_to_vec_list(xcoord, q, n)
                v = svector(F, vec_ints)
                if v in W:
                    ks_in_W.append(k)
                pt = pt + Gpt
            entries.append({"basis_indices": list(entry["combo"]),
                             "witness_not_stable": str(entry["witness"]),
                             "size_B_W": len(ks_in_W), "_ks": ks_in_W})
        c2_by_dim_raw[str(d)] = {"found": len(entries) > 0, "pool_size": len(entries),
                                  "pool": entries}
    timings["c2_membership_passes_wall_seconds"] = time.time() - t0

    result["C2_raw"] = {
        k: {"found": v["found"], "pool_size": v["pool_size"],
            "pool": [{kk: vv for kk, vv in e.items() if kk != "_ks"} for e in v["pool"]]}
        for k, v in c2_by_dim_raw.items()
    }

    # [2,2,2] distinctness check: all pool entries for dim 2 pairwise distinct
    dim2_combos = [e["basis_indices"] for e in c2_by_dim_raw.get("2", {}).get("pool", [])]
    result["C2_dim2_pool_combos"] = dim2_combos
    result["C2_dim2_pool_pairwise_distinct"] = (len(dim2_combos) == len(set(map(tuple, dim2_combos))))

    c2_partitions = []
    for r in obj_partitions:
        if r["status"] != "ok":
            c2_partitions.append({"partition_blocks": r["partition_blocks"],
                                   "slot_dims": r["slot_dims"], "status": r["status"]})
            continue
        block_ksets = []
        used_by_dim = {}
        missing = False
        used_combos_this_partition = []
        for d in r["slot_dims"]:
            key = str(d)
            pool_entry = c2_by_dim_raw.get(key)
            idx = used_by_dim.get(d, 0)
            if pool_entry is None or not pool_entry["found"] or idx >= pool_entry["pool_size"]:
                missing = True
                break
            block_ksets.append(pool_entry["pool"][idx]["_ks"])
            used_combos_this_partition.append((d, tuple(pool_entry["pool"][idx]["basis_indices"])))
            used_by_dim[d] = idx + 1
        if missing:
            c2_partitions.append({"partition_blocks": r["partition_blocks"],
                                   "slot_dims": r["slot_dims"], "status": "no_matched_subspace"})
            continue
        stats = compute_pm_Uneg(block_ksets, N)
        pm = stats["p_m"]
        ratios = {}
        for extra in extra_values:
            if pm[0] == 0:
                ratios[str(extra)] = {"denominator_zero": True, "numerator": stats["U_neg"]}
            else:
                ratios[str(extra)] = {"denominator_zero": False,
                                       "value": cost_ratio(stats["U_neg"], pm, extra)}
        rec = {"partition_blocks": r["partition_blocks"],
               "slot_dims": r["slot_dims"], "status": "ok",
               **stats, "cost_ratio_neg": ratios,
               "U_frob": None, "U_frob_reason": "slot set not pi-stable",
               "c2_subspaces_used": [{"dim": d, "combo": list(c)} for d, c in used_combos_this_partition],
               "c2_subspaces_pairwise_distinct": (
                   len(used_combos_this_partition) ==
                   len(set(used_combos_this_partition)))}
        c2_partitions.append(rec)
    result["C2_arm_partitions"] = c2_partitions
    result["C2_spread_summary"] = arm_spread_summary(c2_partitions)

    # explicit [2,2,2]-partition three-subspace distinctness confirmation
    two_two_two = [r for r in c2_partitions if r.get("slot_dims") == [2, 2, 2] and r.get("status") == "ok"]
    if two_two_two:
        r222 = two_two_two[0]
        combos = [tuple(u["combo"]) for u in r222["c2_subspaces_used"]]
        result["C2_222_three_subspaces_distinct"] = {
            "combos_used": [list(c) for c in combos],
            "all_three_pairwise_distinct": len(combos) == len(set(combos)) == 3,
        }
    else:
        result["C2_222_three_subspaces_distinct"] = {"status": "no_ok_222_partition_found"}

    # ---------------------------------------------------------------- C3
    c3_by_seed = {}
    c3_spread_by_seed = {}
    for seed in seeds:
        c3_partitions = []
        for r in obj_partitions:
            if r["status"] != "ok":
                c3_partitions.append({"partition_blocks": r["partition_blocks"],
                                       "slot_dims": r["slot_dims"], "status": r["status"]})
                continue
            orig_block_ksets = []
            block_masks = build_partition_blocks_masks(r["partition_blocks"])
            for bm in block_masks:
                ks = []
                for mask, klist in by_mask.items():
                    if (mask & ~bm) == 0:
                        ks.extend(klist)
                orig_block_ksets.append(ks)
            rand_ksets = random_matched_subset(
                orig_block_ksets, N,
                seed=seed + hash(tuple(tuple(b) for b in r["partition_blocks"])) % 100000)
            stats = compute_pm_Uneg(rand_ksets, N)
            pm = stats["p_m"]
            ratios = {}
            for extra in extra_values:
                if pm[0] == 0:
                    ratios[str(extra)] = {"denominator_zero": True, "numerator": stats["U_neg"]}
                else:
                    ratios[str(extra)] = {"denominator_zero": False,
                                           "value": cost_ratio(stats["U_neg"], pm, extra)}
            c3_partitions.append({"partition_blocks": r["partition_blocks"],
                                   "slot_dims": r["slot_dims"], "status": "ok",
                                   **stats, "cost_ratio_neg": ratios})
        c3_by_seed[str(seed)] = c3_partitions
        c3_spread_by_seed[str(seed)] = arm_spread_summary(c3_partitions)
    result["C3_arm_by_seed"] = c3_by_seed
    result["C3_spread_by_seed"] = c3_spread_by_seed

    # ---------------------------------------------------------------- C4
    t0 = time.time()
    rejected_c4 = []
    c4info = c4_null_curve_search(q, n, K, N, rejected_c4)
    timings["c4_null_curve_search_wall_seconds"] = time.time() - t0
    result["C4_rejected"] = rejected_c4
    if c4info is None:
        result["C4"] = {"status": "no_eligible_null_curve"}
    else:
        EKp = c4info["EK"]
        Gp = find_generator(EKp, K, q, n, c4info["cofactor"])
        c4_result = {"a": c4info["a"], "b": c4info["b"], "A": c4info["A"], "B": c4info["B"],
                     "N": c4info["N"], "j_invariant": c4info["j_invariant"],
                     "cofactor": c4info["cofactor"],
                     "order_count_wall_seconds": c4info["order_count_wall_seconds"]}
        if Gp is None:
            c4_result["status"] = "generator_not_found"
        else:
            Np = c4info["N"]
            c4_partitions_by_seed = {}
            c4_spread_by_seed = {}
            for seed in seeds:
                c4_partitions = []
                for r in obj_partitions:
                    if r["status"] != "ok":
                        c4_partitions.append({"partition_blocks": r["partition_blocks"],
                                               "slot_dims": r["slot_dims"], "status": r["status"]})
                        continue
                    sizes = r["block_sizes"]
                    pairs_avail = list(range(1, (Np - 1) // 2 + 1))
                    rng = random.Random(seed + 7919 * len(pairs_avail) +
                                         hash(tuple(tuple(b) for b in r["partition_blocks"])) % 100000)
                    block_ksets = []
                    used = set()
                    ok_flag = True
                    for sz in sizes:
                        npairs = sz // 2
                        avail = [p for p in pairs_avail if p not in used]
                        if npairs > len(avail):
                            ok_flag = False
                            break
                        chosen = rng.sample(avail, npairs)
                        used.update(chosen)
                        ks = []
                        for pchosen in chosen:
                            ks.append(pchosen)
                            ks.append((Np - pchosen) % Np)
                        block_ksets.append(ks)
                    if not ok_flag:
                        c4_partitions.append({"partition_blocks": r["partition_blocks"],
                                               "slot_dims": r["slot_dims"], "status": "cardinality_infeasible"})
                        continue
                    stats = compute_pm_Uneg(block_ksets, Np)
                    pm = stats["p_m"]
                    ratios = {}
                    for extra in extra_values:
                        if pm[0] == 0:
                            ratios[str(extra)] = {"denominator_zero": True, "numerator": stats["U_neg"]}
                        else:
                            ratios[str(extra)] = {"denominator_zero": False,
                                                   "value": cost_ratio(stats["U_neg"], pm, extra)}
                    c4_partitions.append({"partition_blocks": r["partition_blocks"],
                                           "slot_dims": r["slot_dims"], "status": "ok",
                                           **stats, "cost_ratio_neg": ratios})
                c4_partitions_by_seed[str(seed)] = c4_partitions
                c4_spread_by_seed[str(seed)] = arm_spread_summary(c4_partitions)
            c4_result["status"] = "ok"
            c4_result["partitions_by_seed"] = c4_partitions_by_seed
            c4_result["spread_by_seed"] = c4_spread_by_seed
        result["C4"] = c4_result

    result["timing"] = {"wall_seconds": time.time() - t_start, **timings}
    return result


if __name__ == "__main__":
    cell_name = sys.argv[1]
    q = int(sys.argv[2])
    n = int(sys.argv[3])
    A = int(sys.argv[4])
    B = int(sys.argv[5])
    N = int(sys.argv[6])
    seeds = [int(s) for s in sys.argv[7].split(",")]
    mem_limit_bytes = int(sys.argv[8]) if len(sys.argv) > 8 else None
    if mem_limit_bytes:
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, mem_limit_bytes))
        except Exception as e:
            sys.stderr.write(f"WARNING: could not set RLIMIT_AS: {e}\n")
    try:
        res = main(cell_name, q, n, A, B, N, seeds)
        res["worker_status"] = "ok"
    except MemoryError:
        res = {"cell": cell_name, "worker_status": "resource_exhausted", "reason": "MemoryError"}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["peak_rss_bytes_self"] = ru.ru_maxrss * 1024
    res["cpu_seconds_self"] = ru.ru_utime + ru.ru_stime
    print("RESULT_JSON_BEGIN")
    print(json.dumps(res, default=str))
    print("RESULT_JSON_END")
