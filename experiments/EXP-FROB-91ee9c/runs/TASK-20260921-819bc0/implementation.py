#!/usr/bin/env python
"""
Driver for TASK-20260921-819bc0 (EXP-FROB-91ee9c specification.yaml v1, as
amended by DEC-20260921-e81e25 [v2] and DEC-20260921-2f89d4 [v3]).

Corrects the C2_non_stable_matched_dimension construction defect documented
in ledger/corrections/CORR-20260921-9dc350.yaml (correction C2):
`non_stable_subspace_of_dim(d, M, F, n)` in the reference implementation
(experiments/EXP-FROB-91ee9c/runs/TASK-20260921-51bc02/implementation.py) is
a pure function of (d, M, F, n) alone, so the old C2 construction loop cached
ONE subspace per distinct dimension and reused it for every slot of that
dimension. On the only non-trivial partition either tested cell reaches
([2,2], two slots of dimension 2), this summed a non-stable subspace with
ITSELF.

Per DEC-20260921-2f89d4's `changes` block, the fix is: for a dimension d with
multiplicity k in a partition's slot_dims, maintain ONE canonical,
deterministic POOL per (cell, curve, dimension d), grown lazily -- via the
SAME lexicographic combinations(range(n), d) search order as before, skipping
index-tuples already in the pool -- until the pool has k entries (k = the
maximum multiplicity of d needed by any tested partition in this battery). A
partition needing k slots of dimension d takes the pool's first k entries, in
pool order. This is the ONLY change from the reference implementation:
`non_stable_subspace_of_dim` gains an `exclude` parameter, and the C2
construction loop below builds a per-dimension list instead of a single
cached value. Everything else -- the object arm, C1/C5-C8 logic (not exercised
by this scoped run), file structure, cost_ratio formula, consistency targets
-- is copied unchanged from the reference implementation.

Per the handoff and amendment, this run does NOT recompute C3 or C4 (out of
scope): their constructions do not share C2's per-dimension-cache defect and
both were independently re-verified correct by NA-1's validator and red-team
reports. Only the object-arm consistency check and C2 are computed.

Run under `sage -python implementation.py <cell> <q> <n> <A> <B> <N>
<seed1,seed2> [mem_limit_bytes]`. Writes a single JSON document to stdout
(delimited by RESULT_JSON_BEGIN/END lines) with the complete result: object
arm recompute + consistency check, and corrected C2. Seeds are accepted
(matching the reference invocation signature and command shape) but are not
consumed by any construction in this scoped run (C2 is fully deterministic;
C3/C4 are out of scope).
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


def non_stable_subspace_of_dim(d, M, F, n, exclude=None):
    """C2 (CORRECTED per DEC-20260921-2f89d4): canonical search over
    standard-basis subsets of size d, lexicographic order of index tuples,
    first one whose span is NOT pi-invariant AND whose index tuple is not in
    `exclude`. `exclude` is a set of already-assigned index tuples (combos)
    for this dimension d, so repeated calls grow a deterministic pool of
    DISTINCT non-pi-stable subspaces of dimension d, one call per new pool
    entry, over the exact same combinations(range(n), d) order as before."""
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
    """CORRECTED C2 construction: grow a per-dimension pool to exactly k
    DISTINCT, mutually independent non-pi-stable subspaces of dimension d, in
    canonical (lexicographic combinations(range(n), d)) order, per
    DEC-20260921-2f89d4's `changes` block. Returns a list of up to k pool
    entries, each {"W":..., "witness":..., "combo":...}; stops early (shorter
    list) if the search space is exhausted before reaching k."""
    pool = []
    exclude = set()
    for _ in range(k):
        W, witness, combo = non_stable_subspace_of_dim(d, M, F, n, exclude=exclude)
        if W is None:
            break
        pool.append({"W": W, "witness": witness, "combo": combo})
        exclude.add(combo)
    return pool


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
        result["cell_status_reason"] = "object_arm_mismatch_with_RUN-FROB-91ee9c-51bc02_curve_index_1"
        result["timing"] = {"wall_seconds": time.time() - t_start}
        return result

    result["cell_status"] = "ok"

    # ------------------------------------------------------------ C2 (FIXED)
    # For each dimension d appearing in any ok partition's slot_dims, the
    # multiplicity needed is the MAX multiplicity of d across all such
    # partitions in this battery (DEC-20260921-2f89d4: "grown lazily to the
    # maximum multiplicity of d needed by any tested partition in that
    # cell/curve's battery"). Build one canonical pool per dimension with
    # that many DISTINCT non-pi-stable subspaces.
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

    c2_pool_by_dim = {}
    for d, k in sorted(max_mult_by_dim.items()):
        c2_pool_by_dim[d] = build_c2_pool(d, M, F, n, k)

    # For each pool entry, compute its B_W (k-set of curve indices landing in
    # that subspace) exactly as before, once per DISTINCT subspace.
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

    result["C2_raw"] = {
        k: {"found": v["found"], "pool_size": v["pool_size"],
            "pool": [{kk: vv for kk, vv in e.items() if kk != "_ks"} for e in v["pool"]]}
        for k, v in c2_by_dim_raw.items()
    }

    # Consume the pool in order: a partition needing k slots of dimension d
    # takes the pool's first k entries, in pool order -- so two slots of the
    # SAME dimension in the SAME partition get DISTINCT pool entries (this is
    # exactly the fix: no two slots of the same dimension in the same
    # partition share a subspace).
    c2_partitions = []
    for r in obj_partitions:
        if r["status"] != "ok":
            c2_partitions.append({"partition_blocks": r["partition_blocks"],
                                   "slot_dims": r["slot_dims"], "status": r["status"]})
            continue
        block_ksets = []
        used_by_dim = {}
        missing = False
        for d in r["slot_dims"]:
            key = str(d)
            pool_entry = c2_by_dim_raw.get(key)
            idx = used_by_dim.get(d, 0)
            if pool_entry is None or not pool_entry["found"] or idx >= pool_entry["pool_size"]:
                missing = True
                break
            block_ksets.append(pool_entry["pool"][idx]["_ks"])
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
        c2_partitions.append({"partition_blocks": r["partition_blocks"],
                               "slot_dims": r["slot_dims"], "status": "ok",
                               **stats, "cost_ratio_neg": ratios,
                               "U_frob": None, "U_frob_reason": "slot set not pi-stable"})
    result["C2_arm_partitions"] = c2_partitions
    result["C2_spread_summary"] = arm_spread_summary(c2_partitions)

    # C3 and C4 are OUT OF SCOPE for this run per the handoff/amendment.

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
