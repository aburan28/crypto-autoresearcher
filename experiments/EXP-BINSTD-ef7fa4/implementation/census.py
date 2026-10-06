"""E-space census: enumerate / sample solutions of S4_sym=0 over prod V^{(k)}."""
from __future__ import annotations

import time

import numpy as np

from lift import lift_e_solution, independent_recheck_decomposition
from product_space import (
    coords_to_field,
    enumerate_subspace,
    explicit_product_dim,
    poly_basis,
    predicted_dim,
    random_basis,
)
from symmetrised_s4 import elementary_symmetric, s4_field, s4_sym, verify_s4_sym_identity


def product_basis_for_Vk(poly_l_basis: list[int], k: int, F) -> list[int]:
    """F2-basis for V^{(k)} via Gaussian elim on k-fold basis products."""
    from product_space import product_space_elements, f2_span_dim

    elems = product_space_elements(poly_l_basis, k, F)
    used = []
    basis = []
    for v in elems:
        x = int(v)
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        basis.append(int(v))
    assert len(basis) == f2_span_dim(elems, F.n)
    return basis


def build_Vk_bases(V_basis: list[int], F, m: int = 3):
    return [product_basis_for_Vk(V_basis, k, F) for k in range(1, m + 1)]


def measure_P2(F, l_values=range(4, 10)) -> list[dict]:
    rows = []
    for l in l_values:
        V = poly_basis(l)
        dims = []
        for k in range(1, 4):
            d = explicit_product_dim(V, k, F)
            dims.append(d)
            pred = predicted_dim(l, k, F.n)
            if d != pred:
                raise AssertionError(f"P2 fail l={l} k={k}: {d} != {pred}")
        rows.append(
            {
                "l": l,
                "dims_measured": dims,
                "dims_predicted": [predicted_dim(l, k, F.n) for k in range(1, 4)],
                "match": True,
                "sum_dims": sum(dims),
                "ml": 3 * l,
            }
        )
    return rows


def genuine_decompositions(F, B, V_list: list[int], xR: int) -> list[tuple]:
    """Exact enumeration over V^3 of triples with S4=0.

    Counts ordered triples; callers may divide by symmetries if needed.
    Protocol: exact enumeration ground truth.
    """
    hits = []
    V = V_list
    for x1 in V:
        for x2 in V:
            for x3 in V:
                if s4_field(F, B, x1, x2, x3, xR) == 0:
                    hits.append((x1, x2, x3))
    return hits


def _is_poly_window_basis(basis: list[int]) -> bool:
    """True iff basis is {1,t,...,t^{l-1}} (coordinate window)."""
    l = len(basis)
    return basis == [1 << j for j in range(l)]


def e_space_exhaustive(F, B, bases_Vk: list[list[int]], xR: int, V_set: set[int], store_solutions: bool = False):
    """Exhaustive assignment over prod V^{(k)}; return e-solution counts (+ optional list)."""
    import numpy as np
    from symmetrised_s4 import s4_sym_batch_e3

    b1, b2, b3 = bases_Vk
    d1, d2, d3 = len(b1), len(b2), len(b3)
    n_assign = 1 << (d1 + d2 + d3)
    e_solutions = []
    n_e = 0
    t0 = time.time()
    poly_fast = all(b == [1 << j for j in range(len(b))] for b in bases_Vk)

    if poly_fast:
        e3_all = np.arange(1 << d3, dtype=np.int64)
        for c1 in range(1 << d1):
            e1 = c1
            for c2 in range(1 << d2):
                e2 = c2
                vals = s4_sym_batch_e3(F, B, e1, e2, e3_all, xR)
                hits = np.flatnonzero(vals == 0)
                n_e += int(hits.size)
                if store_solutions and hits.size:
                    for e3 in hits.tolist():
                        e_solutions.append((e1, e2, int(e3)))
    else:
        for c1 in range(1 << d1):
            e1 = coords_to_field(c1, b1)
            for c2 in range(1 << d2):
                e2 = coords_to_field(c2, b2)
                e3s = [coords_to_field(c3, b3) for c3 in range(1 << d3)]
                # batch via numpy if possible
                arr = np.array(e3s, dtype=np.int64)
                vals = s4_sym_batch_e3(F, B, e1, e2, arr, xR)
                hits = np.flatnonzero(vals == 0)
                n_e += int(hits.size)
                if store_solutions and hits.size:
                    for i in hits.tolist():
                        e_solutions.append((e1, e2, int(e3s[i])))
    return {
        "enumeration_mode": "exhaustive",
        "n_assignments": n_assign,
        "e_space_solution_count": n_e,
        "lift_genuine_count": None,  # filled by caller via V^3 + lift_agreement
        "e_solutions": e_solutions,
        "genuine_lifts": [],
        "wall_s": time.time() - t0,
        "censoring_flag": False,
        "sampled_assignment_count": n_assign,
        "poly_window_fastpath": poly_fast,
    }


def e_space_sampled(F, B, bases_Vk, xR, V_set, n_samples: int, rng: np.random.Generator):
    """Sample assignments; report lower-bound style counts + censoring."""
    import numpy as np

    b1, b2, b3 = bases_Vk
    d1, d2, d3 = len(b1), len(b2), len(b3)
    n_total = 1 << (d1 + d2 + d3)
    n_e = 0
    t0 = time.time()
    poly_fast = all(b == [1 << j for j in range(len(b))] for b in bases_Vk)
    # Precompute coordinate tables for non-window bases
    if poly_fast:
        tab1 = np.arange(1 << d1, dtype=np.int64)
        tab2 = np.arange(1 << d2, dtype=np.int64)
        tab3 = np.arange(1 << d3, dtype=np.int64)
    else:
        tab1 = np.array([coords_to_field(i, b1) for i in range(1 << d1)], dtype=np.int64)
        tab2 = np.array([coords_to_field(i, b2) for i in range(1 << d2)], dtype=np.int64)
        tab3 = np.array([coords_to_field(i, b3) for i in range(1 << d3)], dtype=np.int64)

    batch = min(1 << 16, n_samples)
    done = 0
    B2 = F.mul(B, B)
    xR_2 = F.mul(xR, xR)
    xR_3 = F.mul(xR_2, xR)
    xR_4 = F.mul(xR_2, xR_2)
    while done < n_samples:
        m = min(batch, n_samples - done)
        c1 = rng.integers(0, 1 << d1, size=m, dtype=np.int64)
        c2 = rng.integers(0, 1 << d2, size=m, dtype=np.int64)
        c3 = rng.integers(0, 1 << d3, size=m, dtype=np.int64)
        e1 = tab1[c1]
        e2 = tab2[c2]
        e3 = tab3[c3]
        e1_2 = F.vmul(e1, e1)
        e1_4 = F.vmul(e1_2, e1_2)
        e2_2 = F.vmul(e2, e2)
        e2_4 = F.vmul(e2_2, e2_2)
        e3_2 = F.vmul(e3, e3)
        e3_3 = F.vmul(e3_2, e3)
        e3_4 = F.vmul(e3_2, e3_2)
        acc = F.vmul(np.full(m, B2, dtype=np.int64), e1_4)
        acc ^= F.vmul(np.full(m, B2, dtype=np.int64), np.full(m, xR_4, dtype=np.int64))
        acc ^= F.vmul(F.vmul(np.full(m, B, dtype=np.int64), e1_2), F.vmul(e3, np.full(m, xR, dtype=np.int64)))
        acc ^= F.vmul(e1_2, F.vmul(e3_2, np.full(m, xR_2, dtype=np.int64)))
        acc ^= F.vmul(F.vmul(np.full(m, B, dtype=np.int64), e2_2), np.full(m, xR_2, dtype=np.int64))
        acc ^= F.vmul(e2_2, F.vmul(e3, np.full(m, xR_3, dtype=np.int64)))
        acc ^= F.vmul(e2_4, np.full(m, xR_4, dtype=np.int64))
        acc ^= F.vmul(np.full(m, B, dtype=np.int64), e3_2)
        acc ^= F.vmul(F.vmul(np.full(m, B, dtype=np.int64), e3), np.full(m, xR_3, dtype=np.int64))
        acc ^= F.vmul(e3_2, np.full(m, xR_4, dtype=np.int64))
        acc ^= F.vmul(e3_3, np.full(m, xR, dtype=np.int64))
        acc ^= e3_4
        n_e += int(np.count_nonzero(acc == 0))
        done += m
    return {
        "enumeration_mode": "sampled",
        "n_assignments_total": n_total,
        "sampled_assignment_count": n_samples,
        "e_space_solution_count_sampled": n_e,
        "e_space_solution_count_lower_bound": n_e,
        "lift_genuine_count_sampled": None,
        "e_solutions_sampled": [],
        "genuine_lifts": [],
        "wall_s": time.time() - t0,
        "censoring_flag": True,
        "censoring_fraction": 1.0 - (n_samples / n_total),
        "label": "LOWER_BOUND_sampled",
    }


def census_cell(F, B, A, CurveCls, V_basis, targets, l, mode, seed, sample_cap=1 << 24):
    bases = build_Vk_bases(V_basis, F, m=3)
    dims = [len(b) for b in bases]
    V_list = enumerate_subspace(V_basis, F)
    V_set = set(V_list)
    rng = np.random.default_rng(seed + l * 1009)

    total_e = 0
    total_genuine_enum = 0
    total_lift_genuine = 0
    lift_agreement_num = 0
    lift_agreement_den = 0
    certificates = []
    per_target = []
    smoothest = None  # fewest e-solutions among targets with >=1

    for t in targets:
        xR = t["x_R"]
        genuine = genuine_decompositions(F, B, V_list, xR)
        # Unique up to S3 permutation for reporting optional; keep ordered count
        n_gen = len(genuine)
        total_genuine_enum += n_gen

        if mode == "exhaustive":
            rec = e_space_exhaustive(F, B, bases, xR, V_set, store_solutions=False)
            n_e = rec["e_space_solution_count"]
        else:
            rec = e_space_sampled(F, B, bases, xR, V_set, sample_cap, rng)
            n_e = rec["e_space_solution_count_sampled"]

        total_e += n_e

        # lift_agreement: every enumerated genuine must appear as a lift
        recovered = 0
        n_lift_g = 0
        for trip in genuine:
            e = elementary_symmetric(F, *trip)
            lift = lift_e_solution(F, *e, V_set)
            if lift["genuine"]:
                recovered += 1
                n_lift_g += 1
                chk = independent_recheck_decomposition(
                    F, CurveCls, A, B, trip[0], trip[1], trip[2], xR
                )
                if chk["verified"]:
                    certificates.append(
                        {
                            "kind": "decomposition",
                            "verified": True,
                            "target_idx": t["idx"],
                            "witness": [int(x) for x in trip],
                            "e": [int(z) for z in e],
                            "recheck": chk,
                        }
                    )
            lift_agreement_den += 1
            lift_agreement_num += int(lift["genuine"])
        total_lift_genuine += n_lift_g

        per_target.append(
            {
                "idx": t["idx"],
                "x_R": int(xR),
                "genuine_ordered_count": n_gen,
                "e_space_solution_count": n_e,
                "lift_genuine_count": n_lift_g,
                "enumeration_mode": rec["enumeration_mode"],
                "wall_s": rec["wall_s"],
            }
        )
        if n_e >= 1 and (smoothest is None or n_e < smoothest["e_space_solution_count"]):
            smoothest = per_target[-1]

    spurious = None
    if total_genuine_enum > 0:
        spurious = total_e / total_genuine_enum
    elif total_e > 0:
        spurious = float("inf")

    return {
        "l": l,
        "dims_Vk": dims,
        "sum_dims": sum(dims),
        "ml": 3 * len(V_basis),
        "mode": mode,
        "n_targets": len(targets),
        "e_space_solution_count_pooled": total_e,
        "genuine_decomposition_count_pooled_ordered": total_genuine_enum,
        "lift_genuine_pooled": total_lift_genuine,
        "spurious_factor": spurious,
        "spurious_factor_label": (
            "MEASURED_exhaustive"
            if mode == "exhaustive"
            else "LOWER_BOUND_sampled_e_over_exact_genuine"
        ),
        "lift_agreement": (
            1.0
            if lift_agreement_den == 0
            else lift_agreement_num / lift_agreement_den
        ),
        "lift_agreement_counts": {"recovered": lift_agreement_num, "genuine": lift_agreement_den},
        "per_target": per_target,
        "smoothest_e_solution_target": smoothest,
        "decomposition_certificates": certificates,
        "identity_check": verify_s4_sym_identity(F, B, trials=100, seed=seed),
        "V_basis": [int(b) for b in V_basis],
        "Vk_bases": [[int(x) for x in b] for b in bases],
    }
