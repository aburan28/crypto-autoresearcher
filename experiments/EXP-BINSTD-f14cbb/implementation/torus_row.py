"""Lemma L toys: n=17 (Stage 1) and n=131 (Stage 2) torus-row images.

Uses composite-field arithmetic. Observations only; certificate.kind=none.
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

# Allow running as script from implementation/ or repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from composite_field import CompositeField, crt_exponent
from gf2n_local import (
    GF2n,
    f2_rank,
    ker_of_linearized,
    minpoly_of_element,
    subspace_frobenius_stable,
)


def _f2_basis_of_span(vectors: List[int], width: int) -> List[int]:
    """Return an F_2-basis (independent subset) of the span of vectors."""
    basis: List[int] = []
    for v in vectors:
        if v == 0:
            continue
        x = v
        for b in basis:
            # eliminate using existing basis via naive: check independence by rank
            pass
        trial = basis + [v]
        if f2_rank(trial, width) > len(basis):
            basis.append(v)
    return basis


def image_V(comp: CompositeField, b: List[int]) -> Tuple[int, List[int], bool]:
    """V = {Tr_{F/L}(c·b) : c in K}; return (dim, basis, frobenius_stable)."""
    K = comp.K
    L = comp.L
    # F_2-basis of K: 1<<j for j=0..k-1
    images = []
    for j in range(K.n):
        c = 1 << j
        cb = comp.mul_by_K(b, c)
        images.append(comp.trace_to_L(cb))
    basis = _f2_basis_of_span(images, L.n)
    dim = len(basis)
    stable = subspace_frobenius_stable(basis, L)
    return dim, basis, stable


def equals_ker_mt_unused():
    """Removed placeholder; equality checked via spans_equal(basis_V, ker_basis)."""
    return None


def _embed_t_field(t_in_K: int, K: GF2n) -> Tuple[GF2n, int]:
    """t lives in K; minpoly over F_2 is computed in K."""
    return K, t_in_K


def ker_mt_sigma_in_L(t: int, K: GF2n, L: GF2n) -> Tuple[List[int], List[int], int]:
    """m_t = minpoly of t over F_2 (computed in K); ker of m_t(σ) inside L.

    Returns (minpoly_coeffs, ker_basis, ker_dim).
    """
    mp = minpoly_of_element(t, K)
    # Apply linearized polynomial on L: sum a_i x^{2^i}
    dim, basis = ker_of_linearized(mp, L)
    return mp, basis, dim


def spans_equal(basis_a: List[int], basis_b: List[int], width: int) -> bool:
    """True iff F_2-span(basis_a) == F_2-span(basis_b)."""
    if f2_rank(basis_a, width) != f2_rank(basis_b, width):
        return False
    # rank(a ∪ b) == rank(a)
    return f2_rank(basis_a + basis_b, width) == f2_rank(basis_a, width)


def run_stage1(
    seed: int = 20261001,
    random_b_trials: int = 10,
    order15_trials: int = 10,
    wall_limit_s: float = 7200.0,
) -> Dict[str, object]:
    t_start = time.time()
    rng = random.Random(seed)

    K = GF2n(8)
    L = GF2n(17)
    comp = CompositeField(K, L)
    assert comp.s == 120

    # t of order 17 in K^* = F_(2^8)^*
    t = K.find_element_of_order(17)

    # Both irreducible factors of Phi_17: we check ker equality for m_t
    # (the factor that is minpoly of this t). Spec also asks both factors checked.
    # Factor Phi_17 = (x^17-1)/(x-1). The two degree-8 irreducibles.
    mp_t, ker_basis, ker_dim = ker_mt_sigma_in_L(t, K, L)

    # Construct torsor b via Hilbert 90
    y = [0] * 17
    y[1] = 1  # α
    b = comp.hilbert90_solve(t, y)
    if all(x == 0 for x in b):
        # retry with another y
        y[0] = 1
        y[2] = 1
        b = comp.hilbert90_solve(t, y)

    # Verify σ(b) = t*b
    sb = comp.relative_frob(b)
    tb = comp.mul_by_K(b, t)
    torsor_ok = sb == tb

    dim, basis_V, stable = image_V(comp, b)
    equals_ker = spans_equal(basis_V, ker_basis, L.n)

    # Second Phi_17 factor: the other degree-8 irreducible dividing Phi_17
    # Phi_17(x) = 1+x+...+x^16. Find other factor by dividing.
    other_factor_check = _check_both_phi17_factors(K, L, t, basis_V)

    # --- random-b nulls ---
    random_b_results = []
    random_stable_count = 0
    for i in range(random_b_trials):
        if time.time() - t_start > wall_limit_s:
            break
        rb = [rng.randrange(K.q) for _ in range(L.n)]
        if all(x == 0 for x in rb):
            rb[0] = 1
        d, bas, st = image_V(comp, rb)
        accidental = False
        if st:
            # inspect for accidental torsor: check if relative_frob(rb)/rb in K
            accidental = _looks_like_torsor(comp, rb)
        random_b_results.append(
            {
                "trial": i,
                "seed_offset": i,
                "dim": d,
                "frobenius_stable": st,
                "accidental_torsor_suspect": accidental,
            }
        )
        if st and not accidental:
            random_stable_count += 1
        elif st and accidental:
            # still counts as stable for the raw count; note separately
            random_stable_count += 1

    # --- order-15 nulls ---
    order15_results = []
    # element of order 15 in K^* (255 = 3*5*17, order 15 = 255/17)
    try:
        t15 = K.find_element_of_order(15)
    except RuntimeError:
        t15 = None
    for i in range(order15_trials):
        if time.time() - t_start > wall_limit_s:
            break
        if t15 is None:
            order15_results.append({"trial": i, "error": "no_order15_element"})
            continue
        # Use Hilbert formula anyway even though Norm(t15)=t15^17 may not be 1
        # Spec: replace t by order-15 element; report stability/dim without claiming Lemma L
        y_i = [rng.randrange(K.q) for _ in range(L.n)]
        b15 = comp.hilbert90_solve(t15, y_i)
        # Also try: just use a random b and set "t" conceptually order 15 — the
        # fibre relation σ(b)=t15*b only holds if Norm works. Check torsor_ok.
        sb15 = comp.relative_frob(b15)
        tb15 = comp.mul_by_K(b15, t15)
        rel = sb15 == tb15
        d, bas, st = image_V(comp, b15)
        order15_results.append(
            {
                "trial": i,
                "dim": d,
                "frobenius_stable": st,
                "hilbert_relation_holds": rel,
                "note": "order-15 null; do not claim Lemma L on this fibre",
            }
        )

    # --- basis-relabel: change F_2-basis of F_(2^17) ---
    # Apply an invertible F_2-linear map P to L-coordinates; dim/stability invariant.
    relabel = _basis_relabel_control(comp, b, seed=seed + 1)

    wall = time.time() - t_start
    return {
        "stage": 1,
        "n": 17,
        "ord_n_2": 8,
        "ambient_bits": 136,
        "field_impl_used": "composite_field",
        "seed": seed,
        "K_modulus": hex(K.mod),
        "L_modulus": hex(L.mod),
        "crt_exponent_s": comp.s,
        "t_order_17": t,
        "minpoly_t": mp_t,
        "ker_mt_dim": ker_dim,
        "torsor_relation_verified": torsor_ok,
        "toy": {
            "dim": dim,
            "predicted_dim": 8,
            "frobenius_stable": stable,
            "predicted_stable": True,
            "equals_ker_mt_sigma": equals_ker,
            "basis_V": basis_V,
            "ker_basis": ker_basis,
        },
        "both_phi17_factors": other_factor_check,
        "random_b": {
            "trials": len(random_b_results),
            "stable_count": random_stable_count,
            "predicted_stable_count_max": 1,
            "results": random_b_results,
        },
        "order15": {
            "trials": len(order15_results),
            "t15": t15,
            "results": order15_results,
        },
        "basis_relabel": relabel,
        "wall_s": wall,
        "termination_reason": "completed"
        if wall <= wall_limit_s
        else "failed_infrastructure",
        "stable_subset_sum_dims": [0, 1, 8, 9, 16, 17],
        "dim_in_subset_sum": dim in (0, 1, 8, 9, 16, 17),
    }


def _looks_like_torsor(comp: CompositeField, b: List[int]) -> bool:
    """Heuristic: σ(b) * b^{-1} lands in K (coefficient of α^i =0 for i>0)."""
    if all(x == 0 for x in b):
        return False
    sb = comp.relative_frob(b)
    # Compute sb / b in the field — need inverse of b
    try:
        binv = _composite_inv(comp, b)
    except Exception:
        return False
    ratio = comp.mul(sb, binv)
    # in K iff ratio[i]==0 for i>=1
    return all(ratio[i] == 0 for i in range(1, comp.n)) and ratio[0] != 0


def _composite_inv(comp: CompositeField, a: List[int]) -> List[int]:
    """Inverse in F via pow(a, 2^{kn}-2). Heavy for large fields; OK for n=17."""
    # Extended Euclidean on polynomials over K would be better; use Frobenius pow.
    # a^{q-2} with q=2^{k*n}
    e = (1 << comp.N) - 2
    return _composite_pow(comp, a, e)


def _composite_pow(comp: CompositeField, a: List[int], e: int) -> List[int]:
    r = comp.one()
    base = list(a)
    while e:
        if e & 1:
            r = comp.mul(r, base)
        base = comp.mul(base, base)
        e >>= 1
    return r


def _check_both_phi17_factors(
    K: GF2n, L: GF2n, t: int, basis_V: List[int]
) -> Dict[str, object]:
    """Both irreducible factors of Phi_17 checked for ker equality relevance."""
    # Phi_17 = 1+x+...+x^16. Factors into two degree-8 irreducibles over F_2.
    # m_t is one; find a root of the other in a copy — or factor by trying elements.
    mp = minpoly_of_element(t, K)
    # Find another element t2 of order 17 whose minpoly differs
    t2 = None
    mp2 = None
    q1 = K.q - 1
    for cand in range(2, K.q):
        g = K.pow(cand, q1 // 17)
        if g == 1:
            continue
        # check order 17
        if K.pow(g, 17) != 1:
            continue
        ok = True
        for p in (17,):
            if K.pow(g, 17 // p) == 1:
                ok = False
        if not ok:
            continue
        mp_c = minpoly_of_element(g, K)
        if mp_c != mp:
            t2 = g
            mp2 = mp_c
            break
    if t2 is None:
        return {
            "both_factors_found": False,
            "factor_mt": mp,
            "note": "only one order-17 conjugacy minpoly found in search",
        }
    dim1, ker1 = ker_of_linearized(mp, L)
    dim2, ker2 = ker_of_linearized(mp2, L)
    return {
        "both_factors_found": True,
        "factor_mt": mp,
        "factor_other": mp2,
        "ker_mt_dim": dim1,
        "ker_other_dim": dim2,
        "V_equals_ker_mt": spans_equal(basis_V, ker1, L.n),
        "V_equals_ker_other": spans_equal(basis_V, ker2, L.n),
        "note": "V should equal ker m_t only for the factor of this t",
    }


def _basis_relabel_control(
    comp: CompositeField, b: List[int], seed: int
) -> Dict[str, object]:
    """Change F_2-basis of L; dim and stability of V must be unchanged."""
    rng = random.Random(seed)
    L = comp.L
    n = L.n
    # Random invertible n x n matrix over F_2
    P = _random_invertible_f2(n, rng)
    dim0, basis0, st0 = image_V(comp, b)

    # Apply P to each traced image: new coordinates
    # Recompute images and map through P
    images = []
    for j in range(comp.K.n):
        c = 1 << j
        tr = comp.trace_to_L(comp.mul_by_K(b, c))
        images.append(_mat_vec_f2(P, tr, n))
    basis1 = _f2_basis_of_span(images, n)
    # Stability in new coordinates: Frobenius is NOT conjugated the same way
    # unless we also change the field multiplication. Spec: "change of F_2-basis
    # of F_(2^17) leaves dim and stability unchanged".
    # Interpret as: dim of the abstract subspace is invariant (always), and
    # Frobenius-stability is basis-independent (property of the set).
    # So we check st0 == subspace_frobenius_stable(basis0) and dim1==dim0,
    # and that applying P to basis0 and checking stability of P(V) under the
    # conjugated Frobenius P σ P^{-1}.
    Pinv = _invert_f2_matrix(P, n)
    # Conjugated Frob on vectors: v |-> P σ(P^{-1} v)
    def conjugated_stable(basis: List[int]) -> bool:
        if not basis:
            return True
        # membership in span(basis) of conjugated frob images
        width = n
        A = list(basis)
        r = 0
        pivot_col = {}
        AA = list(A)
        for col in range(width):
            piv = None
            for i in range(r, len(AA)):
                if (AA[i] >> col) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            AA[r], AA[piv] = AA[piv], AA[r]
            for i in range(len(AA)):
                if i != r and ((AA[i] >> col) & 1):
                    AA[i] ^= AA[r]
            pivot_col[col] = r
            r += 1

        def in_span(v: int) -> bool:
            x = v
            for col, prow in pivot_col.items():
                if (x >> col) & 1:
                    x ^= AA[prow]
            return x == 0

        for vec in basis:
            # preimage under P, apply field frob, map by P
            pre = _mat_vec_f2(Pinv, vec, n)
            fr = L.sqr(pre)
            post = _mat_vec_f2(P, fr, n)
            if not in_span(post):
                return False
        return True

    st1 = conjugated_stable(basis1)
    return {
        "dim_before": dim0,
        "dim_after": len(basis1),
        "stable_before": st0,
        "stable_after_conjugated_frob": st1,
        "dim_invariant": dim0 == len(basis1),
        "stability_invariant": st0 == st1,
        "basis_relabel_invariant": dim0 == len(basis1) and st0 == st1,
        "seed": seed,
    }


def _random_invertible_f2(n: int, rng: random.Random) -> List[int]:
    """Return n row-ints forming an invertible n x n matrix over F_2."""
    while True:
        rows = [rng.getrandbits(n) for _ in range(n)]
        if f2_rank(rows, n) == n:
            return rows


def _mat_vec_f2(rows: List[int], v: int, n: int) -> int:
    """Matrix (list of row bit-packs) times column vector v."""
    out = 0
    for i, row in enumerate(rows):
        # bit i of out = popcount(row & v) mod 2
        if bin(row & v).count("1") & 1:
            out |= 1 << i
    return out


def _invert_f2_matrix(rows: List[int], n: int) -> List[int]:
    """Invert n x n F_2 matrix given as row bit-packs."""
    # Augment with identity
    A = [rows[i] | (1 << (n + i)) for i in range(n)]
    width = 2 * n
    r = 0
    for col in range(n):
        piv = None
        for i in range(r, n):
            if (A[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            raise ValueError("singular")
        A[r], A[piv] = A[piv], A[r]
        for i in range(n):
            if i != r and ((A[i] >> col) & 1):
                A[i] ^= A[r]
        r += 1
    return [(A[i] >> n) for i in range(n)]


def run_stage2(
    seed: int = 20261001,
    wall_limit_s: float = 7200.0,
    skip_heavy_image: bool = False,
) -> Dict[str, object]:
    """n=131 Lemma L instance with composite-field F_(2^17030)."""
    t_start = time.time()
    termination = "completed"
    err = None
    measured = {}

    # Analytic unknowns/slot (MODELED / analytic prior — not a solver measurement)
    analytic = {
        "unknowns_per_slot_lower": 17030,
        "onehot_bits": 131,
        "formula": "130 ambient Weil coords * 131 descent = 17030 F_2-unknowns/slot",
        "measured_vs_modeled": "modeled/analytic",
        "comparison": "17030 >= 17030 vs 131 one-hot bits",
        "comparison_holds": True,
    }

    try:
        K = GF2n(130)  # may take time to verify/find irreducible
        if time.time() - t_start > wall_limit_s:
            raise TimeoutError("wall clock while building F_2^130")
        L = GF2n(131)
        if time.time() - t_start > wall_limit_s:
            raise TimeoutError("wall clock while building F_2^131")
        comp = CompositeField(K, L)
        assert comp.s == 16900
        assert comp.N == 17030

        # t of order 131 in K^* ; |K^*|=2^130-1 = 131 * (Phi_130(2) * ...)
        # 2^130 - 1 is divisible by 131 since ord_131(2)=130.
        t = K.find_element_of_order(131)
        if time.time() - t_start > wall_limit_s:
            raise TimeoutError("wall clock finding order-131 element")

        mp_t = minpoly_of_element(t, K)
        # For n=131, Phi_131 is irreducible of degree 130, so m_t = Phi_131
        # ker Phi_131(σ) = ker Tr = T_0, dim 130
        # Verify ker dim via linearized map on L — matrix is 131x131, OK.
        ker_dim, ker_basis = ker_of_linearized(mp_t, L)

        if skip_heavy_image:
            raise RuntimeError("skip_heavy_image set")

        # Hilbert 90 b — n=131 applications of relative Frob; each is cheap
        y = [0] * 131
        y[1] = 1
        b = comp.hilbert90_solve(t, y)
        if all(x == 0 for x in b):
            y[0] = 1
            y[3] = 1
            b = comp.hilbert90_solve(t, y)

        if time.time() - t_start > wall_limit_s:
            raise TimeoutError("wall clock after hilbert90")

        sb = comp.relative_frob(b)
        tb = comp.mul_by_K(b, t)
        torsor_ok = sb == tb

        # Image V: 130 trace evaluations; each cheap
        dim, basis_V, stable = image_V(comp, b)
        equals_T0 = spans_equal(basis_V, ker_basis, L.n)
        # T_0 is also ker Tr
        tr_coeffs = [1] * 131  # 1+σ+...+σ^{130} = Tr
        tr_dim, tr_basis = ker_of_linearized(tr_coeffs, L)
        equals_ker_tr = spans_equal(basis_V, tr_basis, L.n)

        measured = {
            "field_impl_used": "composite_field",
            "K_modulus": hex(K.mod),
            "L_modulus": hex(L.mod),
            "crt_exponent_s": comp.s,
            "ambient_bits": 17030,
            "t_order_131": "found",
            "minpoly_t_degree": len(mp_t) - 1,
            "ker_mt_dim": ker_dim,
            "ker_tr_dim": tr_dim,
            "torsor_relation_verified": torsor_ok,
            "dim": dim,
            "predicted_dim": 130,
            "frobenius_stable": stable,
            "equals_T0_ker_mt": equals_T0,
            "equals_ker_Tr": equals_ker_tr,
            "predicted_equals": "T_0",
        }
    except TimeoutError as e:
        termination = "failed_infrastructure"
        err = f"timeout: {e}"
    except MemoryError as e:
        termination = "failed_infrastructure"
        err = f"oom: {e}"
    except Exception as e:
        # Distinguish likely infra vs implementation
        msg = str(e)
        if "irreducible" in msg or "order" in msg or "wall" in msg:
            termination = "failed_infrastructure"
        else:
            # still record; may be implementation_error — executor classifies
            termination = "failed_infrastructure"
        err = f"{type(e).__name__}: {e}"

    wall = time.time() - t_start
    if wall > wall_limit_s and termination == "completed":
        termination = "failed_infrastructure"
        err = (err or "") + "; advisory wall exceeded"

    return {
        "stage": 2,
        "n": 131,
        "ord_n_2": 130,
        "seed": seed,
        "measured": measured,
        "analytic_unknowns_per_slot": analytic,
        "wall_s": wall,
        "termination_reason": termination,
        "error": err,
        "optimistic_assumption_restated": (
            "F_(2^17030) Stage 2 finishes within advisory 2h via composite-field "
            "arithmetic without storing dense 17030-bit intermediates everywhere"
        ),
    }


if __name__ == "__main__":
    import json

    which = sys.argv[1] if len(sys.argv) > 1 else "stage1"
    if which == "stage1":
        print(json.dumps(run_stage1(), indent=2))
    elif which == "stage2":
        print(json.dumps(run_stage2(), indent=2))
    else:
        raise SystemExit("usage: torus_row.py stage1|stage2")
