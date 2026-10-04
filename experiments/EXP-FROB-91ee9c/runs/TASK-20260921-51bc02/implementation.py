#!/usr/bin/env python
"""
Driver for TASK-20260921-51bc02 (EXP-FROB-91ee9c amendment DEC-20260921-e81e25,
version 2). Computes the ALREADY-DEFINED C2_non_stable_matched_dimension,
C3_random_matched_cardinality and C4_matched_null_curve controls -- verbatim,
unchanged designs from specification.yaml -- against the SECOND eligible
object curve of FROB-SPLIT-q11n5 (A=1,B=2,N=10061) and FROB-EQDEG-q19n5
(A=1,B=1,N=117991). Also recomputes the object arm for each curve as an
internal consistency check against RUN-FROB-91ee9c-7119f2's recorded values.

Structural template: experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/
implementation.py (same core.py/lattice.py support modules, byte-identical
copies under work/). This script differs only in scope: it targets ONE named
(cell, curve) pair per invocation instead of running the full object search,
because the object curve is already identified and eligible per this task's
handoff and amendment (do not re-run the object-curve search).

Run under `sage -python implementation.py <cell> <q> <n> <A> <B> <N>
<seed1,seed2> [mem_limit_bytes]`. Writes a single JSON document to stdout
(delimited by RESULT_JSON_BEGIN/END lines) with the complete result: object
arm recompute + consistency check, C2, C3 (both seeds), C4 (both seeds).
All ratios are represented as [num, den] integer pairs (exact rationals).
"""
import sys, os, json, time, random, resource, itertools
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "work"))
from sage.all import GF, PolynomialRing, EllipticCurve, matrix, Integer, Zmod, factor, vector as svector
from core import (find_first_irreducible, field_setup, elt_to_vec_list, enc_elt,
                   order_ext_trace, frobenius_matrix)
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
    """Identical logic to TASK-20260914-7119f2/implementation.py's
    run_arm_partitions: slot dimension of a block is the SUM OF DEGREES of the
    atomic factors merged into it (not the popcount of the block), matching
    the post-bugfix version used for the reported FROB-NOLATTICE/FROB-EQDEG
    numbers in that run."""
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


def non_stable_subspace_of_dim(d, M, F, n):
    """C2: canonical search over standard-basis subsets of size d, lexicographic
    order of index tuples, first one whose span is NOT pi-invariant."""
    from sage.all import VectorSpace
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


def random_matched_subset(orig_ksets_per_slot, N, seed):
    """C3: for each slot, draw a negation-closed random subset of <G>\\{O} of the
    same cardinality, using pairs (k, N-k)."""
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
    """Scan A'=z+a, B'=z+b lexicographically over a,b in {0..q-1}; reject
    singular, reject j' in F_q; accept first with prime N' exponent 1 and
    N_object/2 <= N' <= 2*N_object. N_object here is THIS curve's N (the
    curve under test in this task), per specification.yaml controls.C4's
    design ("N/2 <= N' <= 2N" where N is the object curve's order), matching
    each control battery to the specific curve it is run against."""
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
    """Same spread computation (max/min of cost_ratio_neg at extra=0) applied
    to any control arm's partition list, restricted to status=='ok' entries."""
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


CONSISTENCY_TARGETS = {
    "FROB-SPLIT-q11n5": {
        "I": [2055, 451],
        "m1_ratio": [206733, 41],
        "m2_ratio": [5533, 5],
        "m2_slot_dims": [2, 2],
    },
    "FROB-EQDEG-q19n5": {
        "I": [6152, 861],
        "m1_ratio": [12097908, 205],
        "m2_ratio": [82593, 10],
        "m2_slot_dims": [2, 2],
    },
}


def check_object_arm_consistency(cell_name, summary):
    target = CONSISTENCY_TARGETS[cell_name]
    checks = {}
    checks["I_matches"] = (summary["I"] == target["I"])
    checks["coarsest_ratio_matches"] = (summary["coarsest"]["ratio"] == target["m1_ratio"])
    checks["argmin_ratio_matches"] = (summary["argmin"]["ratio"] == target["m2_ratio"])
    checks["argmin_slot_dims_matches"] = (sorted(summary["argmin"]["slot_dims"], reverse=True) ==
                                           sorted(target["m2_slot_dims"], reverse=True))
    checks["all_match"] = all(checks.values())
    return checks


def main(cell_name, q, n, A, B, N, seeds, extra_values=(0, 8, 32)):
    t_start = time.time()
    result = {"cell": cell_name, "q": q, "n": n, "seeds": list(seeds),
              "target_curve": {"A": A, "B": B, "N": N}}

    K, g, z, F, M = build_field_and_frobenius(q, n)
    result["field_modulus"] = str(g)
    atomic_info = atomic_and_kernels(q, n, M, F)
    result["factorisation"] = {
        "squarefree": atomic_info["squarefree"],
        "all_exponents_1": atomic_info["facs_all_exp1"],
        "factor_list": atomic_info["factor_list"],
        "atomic_factors": [str(f) for f in atomic_info["atomic"]],
    }
    C, Cinv, blocks = build_change_of_basis(atomic_info["kers"], atomic_info["ker_x1"], F, n)
    cinv_py = cinv_to_pylist(Cinv, q)
    result["achievable_multiset_table"] = achievable_multiset_table(atomic_info["atomic"])
    result["divisor_lattice_dims"] = divisor_lattice_dims(atomic_info["atomic"])

    # -------------------------------------------------- recompute the curve
    EK = EllipticCurve(K, [A, B])
    order = EK.order()
    fac = factor(order)
    exps = {int(p): int(e) for p, e in fac}
    if N not in exps or exps[N] != 1:
        result["cell_status"] = "instrument_invalidation"
        result["cell_status_reason"] = "target_N_not_exponent1_divisor_of_recomputed_order"
        result["recomputed_order"] = int(order)
        result["timing"] = {"wall_seconds": time.time() - t_start}
        return result
    cofactor = order // N
    j_inv = EK.j_invariant()
    result["curve_recomputed"] = {"A": A, "B": B, "N": N, "cofactor": int(cofactor),
                                   "order": int(order), "j_invariant": str(j_inv)}

    Gpt = find_generator(EK, K, q, n, cofactor)
    if Gpt is None or Gpt.order() != N:
        result["cell_status"] = "instrument_invalidation"
        result["cell_status_reason"] = "generator_not_found_or_order_mismatch"
        result["timing"] = {"wall_seconds": time.time() - t_start}
        return result

    by_mask = enumerate_subgroup_signatures(EK, Gpt, N, q, n, cinv_py, blocks)
    obj_partitions = run_arm_partitions(by_mask, N, atomic_info["atomic"], extra_values)
    result["object_arm_partitions"] = obj_partitions
    obj_summary = object_arm_summary(obj_partitions)
    result["object_arm_summary"] = obj_summary

    consistency = check_object_arm_consistency(cell_name, obj_summary)
    result["object_arm_consistency_check"] = consistency

    if not consistency["all_match"]:
        result["cell_status"] = "instrument_invalidation"
        result["cell_status_reason"] = "object_arm_mismatch_with_RUN-FROB-91ee9c-7119f2_curve_index_1"
        result["timing"] = {"wall_seconds": time.time() - t_start}
        return result

    result["cell_status"] = "ok"

    # ---------------------------------------------------------------- C2
    dims_present = sorted(set(d for r in obj_partitions if r["status"] == "ok" for d in r["slot_dims"]))
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
            v = svector(F, vec_ints)
            if v in W:
                ks_in_W.append(k)
            pt = pt + Gpt
        c2_by_dim[str(d)] = {"found": True, "basis_indices": list(combo),
                              "witness_not_stable": str(witness),
                              "size_B_W": len(ks_in_W), "_ks": ks_in_W}
    result["C2_raw"] = {k: {kk: vv for kk, vv in v.items() if kk != "_ks"} for k, v in c2_by_dim.items()}

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
    result["C2_arm_partitions"] = c2_partitions
    result["C2_spread_summary"] = arm_spread_summary(c2_partitions)

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
    rejected_c4 = []
    c4info = c4_null_curve_search(q, n, K, N, rejected_c4)
    result["C4_rejected"] = rejected_c4
    if c4info is None:
        result["C4"] = {"status": "no_eligible_null_curve"}
    else:
        EKp = c4info["EK"]
        Gp = find_generator(EKp, K, q, n, c4info["cofactor"])
        c4_result = {"a": c4info["a"], "b": c4info["b"], "A": c4info["A"], "B": c4info["B"],
                     "N": c4info["N"], "j_invariant": c4info["j_invariant"],
                     "cofactor": c4info["cofactor"]}
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

    result["timing"] = {"wall_seconds": time.time() - t_start}
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
