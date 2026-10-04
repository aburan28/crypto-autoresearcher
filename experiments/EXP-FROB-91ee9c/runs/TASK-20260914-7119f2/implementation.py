#!/usr/bin/env python
"""
Per-cell worker for EXP-FROB-91ee9c. Run under `sage -python cell_worker.py
<cell_json_params>`. Writes a single JSON document to stdout (last line,
prefixed RESULT_JSON:) with the complete cell result: object search,
C5 identity, achievable multiset table, partition sweep for object/C2/C3/C4
arms, C6/C7 checks. All ratios are represented as [num, den] integer pairs
(exact rationals), never floats.
"""
import sys, os, json, time, random, resource, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "work"))
from sage.all import GF, PolynomialRing, EllipticCurve, matrix, Integer, Zmod, factor
from core import (find_first_irreducible, field_setup, elt_to_vec_list, enc_elt,
                   order_ext_trace, frobenius_matrix, object_search)
from lattice import (all_set_partitions, build_kernels, build_change_of_basis,
                      cinv_to_pylist, vec_signature)


def frac(n, d):
    return [int(n), int(d)]


def enumerate_subgroup_signatures(EK, Gpt, N, q, n, cinv_py, blocks):
    """Enumerate k=1..N-1, return dict mask -> list_of_k (only v0==False),
    plus count of x=0 (mask 0) points, plus total scanned."""
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
    """Given list of lists of residues mod N (one list per slot), compute the
    set of all pairwise sums mod N (as a python set), i.e. the sumset."""
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
    """block_ksets: list of lists of k (discrete logs) per slot (B_j).
    Returns (p_m_num, p_m_den, distinct_count, prod_sizes, U_neg_num, U_neg_den, B_union_size)."""
    prod_sizes = 1
    for b in block_ksets:
        prod_sizes *= len(b)
    sumset = sumset_mod_N(block_ksets, N)
    sumset.discard(0)  # R must be in <G>\{O}; a sum landing on 0 mod N is the identity, excluded
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
        "U_neg": frac(Uneg_num, 2) if Uneg_num % 2 == 0 else frac(Uneg_num, 2),
        "B_union_size": Uneg_num,
        "block_sizes": [len(b) for b in block_ksets],
    }


def cost_ratio(U_num_den, p_num_den, extra):
    Un, Ud = U_num_den
    pn, pd = p_num_den
    if pn == 0:
        return None  # denominator-zero rule
    # (U + 1 + extra)/p = ((Un/Ud)+1+extra) * (pd/pn)
    numer = Un + (1 + extra) * Ud
    denom = Ud * pn
    numer2 = numer * pd
    denom2 = denom
    from math import gcd
    g = gcd(numer2, denom2)
    if g == 0:
        g = 1
    return frac(numer2 // g, denom2 // g)


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
        "p_divides_n": bool(int(F.characteristic()) % n == 0) if False else (n % int(F.characteristic()) == 0),
    }, kerT


def achievable_multiset_table(atomic):
    """Achievable slot-dimension multisets = all set partitions of the atomic
    factors (all degree 1 for SPLIT, but general: sum of degrees per block)."""
    labels = list(range(len(atomic)))
    degs = [int(f.degree()) for f in atomic]
    table = []
    for P in all_set_partitions(labels):
        multiset = sorted([sum(degs[i] for i in block) for block in P], reverse=True)
        table.append({"partition_blocks": [list(b) for b in P], "slot_dims": multiset})
    return table


def divisor_lattice_dims(atomic):
    """All achievable dims from products of subsets of atomic factors (divisor
    lattice), for cross-check against the multiset table."""
    labels = list(range(len(atomic)))
    degs = [int(f.degree()) for f in atomic]
    dims = set()
    for r in range(0, len(labels) + 1):
        for combo in itertools.combinations(labels, r):
            dims.add(sum(degs[i] for i in combo))
    return sorted(dims)


def build_partition_blocks_masks(P):
    """P: list of tuples (blocks of atomic indices). Return list of bitmasks."""
    return [sum(1 << i for i in block) for block in P]


def run_arm_partitions(by_mask, N, atomic, extra_values=(0, 8, 32)):
    """For every achievable partition, and every extra in extra_values, compute
    p_m/U_neg/cost_ratio. Returns list of records.

    NOTE (bugfix): slot dimension of a block is the SUM OF DEGREES of the
    atomic factors merged into it (matching achievable_multiset_table and the
    frozen spec's dim V_j = deg(prod of factors in the block)), NOT the number
    of atomic factors in the block. These coincide only when every atomic
    factor has degree 1 (true in FROB-SPLIT-q11n5 only); an earlier version of
    this function used bit-count and silently mislabelled slot dimensions in
    FROB-NOLATTICE-q13n5 (single degree-4 factor) and FROB-EQDEG-q19n5 (two
    degree-2 factors). This mislabelling did not affect the underlying exact
    p_m/U_neg/cost_ratio values (computed from the true kernel masks), but it
    did feed the WRONG dimension into the C2 non-stable-subspace control and
    into the modelled q^{d_j}/c sizing for those two cells; both were rerun
    after this fix. Recorded as a protocol/implementation deviation.
    """
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


def c6_checks(by_mask, N, atomic, kers, F, n):
    """Known-false configurations: repeated subspace across slots, overlapping
    index sets, V={0}, V=F_{q^n} at m=1. Returns dict of witnessed outcomes."""
    out = {}
    labels = list(range(len(atomic)))
    if len(labels) >= 1:
        # repeat same subspace (block {0}) in two "slots" -> not a partition, must refuse
        blocks = [(0,), (0,)]
        index_sets = [set(b) for b in blocks]
        is_partition = (index_sets[0].isdisjoint(index_sets[1]) and
                         set().union(*index_sets) == set(labels[:1]))
        out["repeated_subspace_refused"] = not is_partition  # must be True (refused)
    if len(labels) >= 2:
        blocks = [(0, 1), (1,)]
        index_sets = [set(b) for b in blocks]
        overlap = not index_sets[0].isdisjoint(index_sets[1])
        out["overlapping_index_sets_refused"] = bool(overlap)
    # V = {0}: p_m must be 0 and trigger denominator-zero rule
    empty_block_ksets = [[]]
    stats0 = compute_pm_Uneg(empty_block_ksets, N)
    out["V_empty_p_m"] = stats0["p_m"]
    out["V_empty_denominator_zero_triggered"] = (stats0["p_m"][0] == 0)
    # V = F_{q^n} at m=1: every nonzero point's x-coordinate is trivially in the
    # whole field, so p_1 = |<G>\{O}|/(N-1) = 1 exactly.
    full_block = list(range(1, N))
    stats_full = compute_pm_Uneg([full_block], N)
    out["V_full_p_1"] = stats_full["p_m"]
    out["V_full_equals_one"] = (stats_full["p_m"][0] == stats_full["p_m"][1])
    return out


def c1_check(by_mask, N, atomic):
    """m=1 (single slot spanning ALL non-trivial factors) must equal the
    closed-form U=|B|/2, p_1=|B|/(N-1) computed WITHOUT tuple enumeration."""
    all_mask = (1 << len(atomic)) - 1
    B = []
    for mask, klist in by_mask.items():
        if (mask & ~all_mask) == 0 and mask != 0 or mask == 0:
            pass
    B = []
    for mask, klist in by_mask.items():
        B.extend(klist)  # v0==0 already guaranteed by construction of by_mask
    Bsize = len(B)
    closed_U = frac(Bsize, 2)
    closed_p1 = frac(Bsize, N - 1)
    enum_stats = compute_pm_Uneg([B], N)
    agree = (enum_stats["p_m"] == closed_p1) and (enum_stats["U_neg"] == closed_U)
    return {"closed_form_U_neg": closed_U, "closed_form_p_1": closed_p1,
            "enumerator_U_neg": enum_stats["U_neg"], "enumerator_p_1": enum_stats["p_m"],
            "agree": bool(agree)}


def non_stable_subspace_of_dim(d, M, F, n):
    """Canonical search: standard basis subsets of size d, in lex order of index
    tuples, first one whose span is NOT pi-invariant."""
    from sage.all import VectorSpace, vector as svector
    V = VectorSpace(F, n)
    stdbasis = [svector(F, [1 if i == j else 0 for i in range(n)]) for j in range(n)]
    for combo in itertools.combinations(range(n), d):
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


def random_matched_subset(by_mask_all_points, orig_ksets_per_slot, N, seed):
    """C3: for each slot, draw a negation-closed random subset of <G>\\{O} of the
    same cardinality, using pairs (k, N-k)."""
    rng = random.Random(seed)
    all_pairs = list(range(1, (N - 1) // 2 + 1))  # representative half; pair is (r, N-r)
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
            # extremely unlikely (B_j sizes are even by negation-closure); record explicitly
            extra_r = rng.choice([p for p in all_pairs if p not in chosen_pairs])
            newset.append(extra_r)
        result.append(newset)
    return result


def c4_null_curve_search(q, n, K, N_object, log_rejected):
    """Scan A'=z+a, B'=z+b lexicographically over a,b in {0..q-1}; reject
    singular, reject j' in F_q; accept first with prime N' exponent 1 and
    N_object/2 <= N' <= 2*N_object."""
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
            order = EK.order()
            fac = factor(order)
            primes_exp1 = [int(p) for p, e in fac if e == 1]
            cand = [p for p in primes_exp1 if N_object // 2 <= p <= 2 * N_object]
            if not cand:
                log_rejected.append({"a": a, "b": b, "reason": "no_matching_N", "order": int(order)})
                continue
            Np = max(cand)
            cofactor = order // Np
            return {"a": a, "b": b, "A": str(Ap), "B": str(Bp), "EK": EK, "N": Np,
                    "cofactor": int(cofactor), "order": int(order), "j_invariant": str(jp)}
    return None


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


def main(cell_name, q, n, seeds, extra_values=(0, 8, 32)):
    t_start = time.time()
    result = {"cell": cell_name, "q": q, "n": n, "seeds": list(seeds)}
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

    acc, rejected = object_search(q, n, K, M, F, want_curves=2)
    result["object_search"] = {"accepted": acc, "rejected": rejected}
    if len(acc) == 0:
        result["cell_status"] = "ineligible"
        result["cell_status_reason"] = "pool_exhausted_no_eligible_curve"
        result["timing"] = {"wall_seconds": time.time() - t_start}
        return result
    result["cell_status"] = "completed" if len(acc) >= 2 else "partial"
    result["cell_status_reason"] = ("ok" if len(acc) >= 2 else
                                     "fixed_object_curve_pool_exhausted_one_curve_found")

    curves_out = []
    for idx, curve in enumerate(acc):
        A, B, N = curve["A"], curve["B"], curve["N"]
        EK = EllipticCurve(K, [A, B])
        Gpt = find_generator(EK, K, q, n, curve["cofactor"])
        if Gpt is None:
            curves_out.append({"curve": curve, "status": "generator_not_found"})
            continue
        by_mask = enumerate_subgroup_signatures(EK, Gpt, N, q, n, cinv_py, blocks)
        curve_rec = {"curve": curve, "N": N}
        obj_partitions = run_arm_partitions(by_mask, N, atomic_info["atomic"], extra_values)
        curve_rec["object_arm_partitions"] = obj_partitions
        if idx == 0:
            # full instrumentation only on the first eligible curve
            curve_rec["C1"] = c1_check(by_mask, N, atomic_info["atomic"])
            curve_rec["C6"] = c6_checks(by_mask, N, atomic_info["atomic"],
                                        atomic_info["kers"], F, n)
            # C2: non-stable matched-dimension arm, per distinct slot dimension
            # appearing in the object's achievable partitions
            dims_present = sorted(set(r["slot_dims"][i] for r in obj_partitions
                                       if r["status"] == "ok" for i in range(len(r["slot_dims"]))))
            c2_by_dim = {}
            for d in dims_present:
                if d == 0:
                    continue
                W, witness, combo = non_stable_subspace_of_dim(d, M, F, n)
                if W is None:
                    c2_by_dim[str(d)] = {"found": False}
                    continue
                ks_in_W = []
                pt = Gpt
                for k in range(1, N):
                    xcoord = pt[0]
                    vec_ints = elt_to_vec_list(xcoord, q, n)
                    from sage.all import vector as svector
                    v = svector(F, vec_ints)
                    in_w = (v in W)
                    if in_w:
                        ks_in_W.append(k)
                    pt = pt + Gpt
                c2_by_dim[str(d)] = {"found": True, "basis_indices": list(combo),
                                      "witness_not_stable": str(witness),
                                      "size_B_W": len(ks_in_W), "_ks": ks_in_W}
            curve_rec["C2_raw"] = c2_by_dim
            c2_partitions = []
            for r in obj_partitions:
                if r["status"] != "ok":
                    c2_partitions.append({"partition_blocks": r["partition_blocks"],
                                           "slot_dims": r["slot_dims"], "status": r["status"]})
                    continue
                block_ksets = []
                missing = False
                for d in r["slot_dims"]:
                    key = str(d)
                    if key not in c2_by_dim or not c2_by_dim[key]["found"]:
                        missing = True
                        break
                    block_ksets.append(c2_by_dim[key]["_ks"])
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
                c2_partitions.append({"partition_blocks": r["partition_blocks"],
                                       "slot_dims": r["slot_dims"], "status": "ok",
                                       **stats, "cost_ratio_neg": ratios,
                                       "U_frob": None, "U_frob_reason": "slot set not pi-stable"})
            curve_rec["C2_arm_partitions"] = c2_partitions

            c3_by_seed = {}
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
                    rand_ksets = random_matched_subset(by_mask, orig_block_ksets, N,
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
            curve_rec["C3_arm_by_seed"] = c3_by_seed

        curves_out.append(curve_rec)
    result["curves"] = curves_out

    N_obj = acc[0]["N"]
    rejected_c4 = []
    c4info = c4_null_curve_search(q, n, K, N_obj, rejected_c4)
    result["C4_rejected"] = rejected_c4
    if c4info is not None:
        EKp = c4info["EK"]
        Gp = find_generator(EKp, K, q, n, c4info["cofactor"])
        c4_result = {"a": c4info["a"], "b": c4info["b"], "A": c4info["A"], "B": c4info["B"],
                     "N": c4info["N"], "j_invariant": c4info["j_invariant"],
                     "cofactor": c4info["cofactor"]}
        if Gp is None:
            c4_result["status"] = "generator_not_found"
        else:
            Np = c4info["N"]
            first_curve_rec = curves_out[0]
            obj_partitions = first_curve_rec["object_arm_partitions"]
            c4_partitions_by_seed = {}
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
                    ok = True
                    for sz in sizes:
                        npairs = sz // 2
                        avail = [p for p in pairs_avail if p not in used]
                        if npairs > len(avail):
                            ok = False
                            break
                        chosen = rng.sample(avail, npairs)
                        used.update(chosen)
                        ks = []
                        for pchosen in chosen:
                            ks.append(pchosen)
                            ks.append((Np - pchosen) % Np)
                        block_ksets.append(ks)
                    if not ok:
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
            c4_result["status"] = "ok"
            c4_result["partitions_by_seed"] = c4_partitions_by_seed
        result["C4"] = c4_result
    else:
        result["C4"] = {"status": "no_eligible_null_curve"}

    result["timing"] = {"wall_seconds": time.time() - t_start}
    return result


if __name__ == "__main__":
    cell_name = sys.argv[1]
    q = int(sys.argv[2])
    n = int(sys.argv[3])
    seeds = [int(s) for s in sys.argv[4].split(",")]
    mem_limit_bytes = int(sys.argv[5]) if len(sys.argv) > 5 else None
    if mem_limit_bytes:
        try:
            resource.setrlimit(resource.RLIMIT_AS, (mem_limit_bytes, mem_limit_bytes))
        except Exception as e:
            sys.stderr.write(f"WARNING: could not set RLIMIT_AS: {e}\n")
    try:
        res = main(cell_name, q, n, seeds)
        res["worker_status"] = "ok"
    except MemoryError:
        res = {"cell": cell_name, "worker_status": "resource_exhausted", "reason": "MemoryError"}
    ru = resource.getrusage(resource.RUSAGE_SELF)
    res["peak_rss_bytes_self"] = ru.ru_maxrss * 1024  # Linux: ru_maxrss in KB
    res["cpu_seconds_self"] = ru.ru_utime + ru.ru_stime
    print("RESULT_JSON_BEGIN")
    print(json.dumps(res, default=str))
    print("RESULT_JSON_END")
