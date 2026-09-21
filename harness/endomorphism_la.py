"""Endomorphism-invariant factor base LA experiment for GLV (j=0) curves.

Tests IDEA-20260726-002: does a phi-invariant factor base (union of phi-orbits)
induce a relation matrix with O(1) displacement rank, unlike the failed AP
approach (EV-STR-001)?

phi(x,y) = (zeta_3 * x, y) for j=0 curves (a=0), where zeta_3 is a primitive
cube root of unity mod p (p ≡ 1 mod 3). phi has order 3.
"""
from __future__ import annotations

import argparse
import io
import math
import time
from contextlib import redirect_stdout

import sympy

from . import rho, semaev
from .runner import RunResult, curve_id, write_run
from .toycurve import generate_instance, ECDLPInstance, EllipticCurve, Point, _seed_int

EXP_ID = "EXP-STR-002"
EXP_AREA = "STR"


def _find_zeta3(p: int) -> int | None:
    """Find a primitive cube root of unity mod p (requires p ≡ 1 mod 3)."""
    if p % 3 != 1:
        return None
    # zeta_3 = g^((p-1)/3) for a generator g
    for g in range(2, min(p, 1000)):
        z = pow(g, (p - 1) // 3, p)
        if z != 1 and pow(z, 3, p) == 1:
            return z
    return None


def _generate_j0_instance(seed: int, field_bits: int) -> ECDLPInstance | None:
    """Generate a j=0 curve (a=0) with p ≡ 1 mod 3. Returns None if not found."""
    for offset in range(50):
        s = seed * 100 + offset
        inst = generate_instance(seed=s, field_bits=field_bits)
        p = inst.p
        if p % 3 != 1:
            continue
        zeta3 = _find_zeta3(p)
        if zeta3 is None:
            continue
        # Regenerate with a=0 (j=0 curve). We need a non-singular y^2 = x^3 + b.
        # Find b from the seed.
        for t in range(1, 200):
            b = _seed_int(s, f"j0b{t}") % p
            if (27 * b * b) % p == 0:
                continue
            E = EllipticCurve(p, 0, b)
            order = E.order() if field_bits <= 24 else E.order_bsgs()
            factors = sympy.factorint(order)
            n = int(max(factors))
            if n.bit_length() < 3 or n < 5:
                continue
            cofactor = order // n
            # Find a point of order n
            for j in range(1, 4000):
                x = _seed_int(s, f"j0x{t}.{j}") % p
                R = E.lift_x(x)
                if R is None:
                    continue
                P = E.mul(cofactor, R)
                if P is not None and E.mul(n, P) is None:
                    k = _seed_int(s, f"j0k{t}") % (n - 2) + 2
                    Q = E.mul(k, P)
                    return ECDLPInstance(p, 0, b, P, Q, n, k, field_bits, s)
    return None


def _phi_point(pt: Point, zeta3: int, p: int) -> Point:
    """Apply phi(x,y) = (zeta_3 * x, y)."""
    if pt is None:
        return None
    return ((zeta3 * pt[0]) % p, pt[1])


def _build_phi_invariant_factor_base(inst: ECDLPInstance, B: int, zeta3: int) -> list[int]:
    """Build a factor base of B x-coordinates as a union of phi-orbits of length 3.

    Each orbit: {x, zeta3*x, zeta3^2*x}. We need B/3 orbits (rounded up).
    Returns a list of B x-coordinates (may be slightly more if B not divisible by 3).
    """
    E = inst.curve()
    p = E.p
    xs = []
    j = 0
    while len(xs) < B and j < 50 * B + 1000:
        x = _seed_int(inst.seed, f"phifb{j}") % p
        j += 1
        # Compute the orbit
        orbit = [x, (zeta3 * x) % p, (zeta3 * zeta3 * x) % p]
        # Check all are distinct and on the curve
        if len(set(orbit)) < 3:
            continue
        all_on = True
        for ox in orbit:
            if ox in xs:
                all_on = False
                break
            if E.lift_x(ox) is None:
                all_on = False
                break
        if not all_on:
            continue
        xs.extend(orbit)
    return xs[:B] if len(xs) >= B else xs


def _build_random_factor_base(inst: ECDLPInstance, B: int) -> list[int]:
    """Build a random factor base of B x-coordinates (not phi-invariant)."""
    return semaev.build_factor_base(inst, B, inst.seed)


def _measure_displacement_rank(relation_matrix_rows: list[list[int]], B: int,
                                shift_type: str, zeta3: int, p: int, n: int,
                                seed: int = 0) -> int:
    """Measure displacement rank alpha = rank([M, Z*M]) - rank(M).

    For 'phi' shift_type: Z is the phi-shift (block-circulant order 3).
    For 'random' shift_type: Z is a random permutation (control).
    """
    import numpy as np
    import hashlib

    if not relation_matrix_rows:
        return 0

    rows = len(relation_matrix_rows)
    cols = B

    # Build M over F_n as integer matrix
    M = np.zeros((rows, cols), dtype=object)
    for i, row in enumerate(relation_matrix_rows):
        for j, val in enumerate(row):
            M[i, j] = val % n

    def matrix_rank_mod(mat, mod):
        mat = mat.copy()
        r, c = mat.shape
        rank = 0
        for col in range(c):
            pivot = -1
            for row in range(rank, r):
                if int(mat[row, col]) % mod != 0:
                    pivot = row
                    break
            if pivot == -1:
                continue
            if pivot != rank:
                mat[[rank, pivot]] = mat[[pivot, rank]]
            inv = pow(int(mat[rank, col]), -1, mod)
            for j in range(c):
                mat[rank, j] = (int(mat[rank, j]) * inv) % mod
            for row in range(r):
                if row == rank:
                    continue
                factor = int(mat[row, col])
                if factor % mod != 0:
                    for j in range(c):
                        mat[row, j] = (int(mat[row, j]) - factor * int(mat[rank, j])) % mod
            rank += 1
        return rank

    # Build Z (shift permutation matrix)
    Z = np.zeros((cols, cols), dtype=object)
    if shift_type == "phi":
        # Block-circulant: orbit j, position k -> orbit j, position (k+1)%3
        num_orbits = B // 3
        for j in range(num_orbits):
            base = j * 3
            Z[base][base + 1] = 1
            Z[base + 1][base + 2] = 1
            Z[base + 2][base] = 1
        for k in range(num_orbits * 3, B):
            Z[k][k] = 1
    else:
        # Random permutation from seed
        indices = list(range(cols))
        rng_state = seed
        for i in range(cols):
            rng_state = (rng_state * 1103515245 + 12345) & 0x7fffffff
            j = rng_state % (i + 1)
            indices[i], indices[j] = indices[j], indices[i]
        for i in range(cols):
            Z[i][indices[i]] = 1

    # Displacement rank: alpha = rank(M - Z * M * Z^{-1})
    # For phi-invariant M (commutes with Z): M - ZMZ^{-1} = 0, alpha = 0.
    # For random M: M - ZMZ^{-1} != 0, alpha ~ min(rows, B).
    # Z^{-1} is the inverse permutation of Z.
    Z_inv = np.zeros((cols, cols), dtype=object)
    for i in range(cols):
        for j in range(cols):
            if int(Z[i][j]) == 1:
                Z_inv[j][i] = 1  # inverse permutation

    # Z * M * Z^{-1}: first M*Z^{-1} (rows x cols), then Z*(that) (cols x rows)
    # But Z is (cols x cols) and M is (rows x cols).
    # Z * M doesn't work dimensionally. The correct formula for column displacement:
    # alpha = rank(M * Z^{-1} - Z * M) doesn't work either.
    # The standard definition for Toeplitz-like matrices uses:
    # alpha = rank(Z1 * M - M * Z2) where Z1, Z2 are shift operators.
    # For our case: Z1 = Z (left shift on rows), Z2 = Z (right shift on cols).
    # But M is rectangular. Let's use the column-only displacement:
    # alpha = rank(M * Z - Z * M) if M were square.
    # For rectangular M (rows x cols), use:
    # alpha = rank(M * Z_col - M) where Z_col shifts columns
    # This measures how much the column space changes under the shift.

    # Simpler correct approach: take the first B relations (square matrix),
    # then compute alpha = rank(M - Z * M * Z^{-1}).
    sq_rows = min(rows, cols)
    M_sq = M[:sq_rows]  # (sq_rows x cols), take square if possible

    if sq_rows < cols:
        # Not enough relations for a square matrix; use what we have
        # alpha = rank(M*Z - M) measures column displacement
        MZ = M @ Z
        diff = (MZ - M) % n
        # Clean up negative values
        for i in range(rows):
            for j in range(cols):
                diff[i][j] = int(diff[i][j]) % n
        alpha = matrix_rank_mod(diff, n)
    else:
        # Square matrix: alpha = rank(M - Z*M*Z^{-1})
        M_sq = M[:cols]  # (cols x cols) square
        ZM = Z @ M_sq  # (cols x cols)
        ZMZ_inv = ZM @ Z_inv  # (cols x cols)
        diff = np.zeros((cols, cols), dtype=object)
        for i in range(cols):
            for j in range(cols):
                diff[i][j] = (int(M_sq[i][j]) - int(ZMZ_inv[i][j])) % n
        alpha = matrix_rank_mod(diff, n)

    return alpha


def _collect_relations(inst: ECDLPInstance, factor_base: list[int], m: int,
                        num_targets: int, zeta3: int = 0,
                        include_phi_orbits: bool = False) -> tuple[list[list[int]], int, int]:
    """Collect relations by attempting S_{m+1} decomposition on random targets.

    If include_phi_orbits and zeta3 are provided, for each found relation,
    also add the phi-shifted relations (applying phi to each summand).
    This ensures the relation matrix has the block-circulant structure.

    Returns (relation_rows, hit_count, attempt_count).
    """
    E = inst.curve()
    p, a, b = E.p, E.a, E.b
    B = len(factor_base)
    n = inst.n
    P = inst.P

    relations = []
    hits = 0
    attempts = 0
    seen_targets = set()

    for t_idx in range(num_targets * 5):
        if len(relations) >= num_targets:
            break
        k = (t_idx + 1) * max(2, inst.seed % max(2, n - 3)) % (n - 1) + 1
        target = E.mul(k, P)
        target_x = target[0]
        if target_x in seen_targets:
            continue
        seen_targets.add(target_x)
        attempts += 1

        if m == 2:
            found, summands, cert = semaev._find_decomposition(E, factor_base, target, a, b, p)
            if found:
                hits += 1
                row = [0] * B
                for s in summands:
                    sx = s[0]
                    if sx in factor_base:
                        row[factor_base.index(sx)] = 1
                if sum(row) > 0:
                    relations.append(row)

                    # If phi-orbits requested, add shifted versions
                    if include_phi_orbits and zeta3:
                        for shift in range(1, 3):  # phi, phi^2
                            shifted_row = [0] * B
                            for idx in range(B):
                                if row[idx]:
                                    # Find the phi-shifted index
                                    x = factor_base[idx]
                                    shifted_x = pow(zeta3, shift, p) * x % p
                                    if shifted_x in factor_base:
                                        shifted_row[factor_base.index(shifted_x)] = 1
                            if sum(shifted_row) > 0 and shifted_row not in relations:
                                relations.append(shifted_row)
        elif m == 3:
            found = False
            for i, v1 in enumerate(factor_base):
                if found:
                    break
                A = E.lift_x(v1)
                if A is None:
                    continue
                for sA in (A, E.negate(A)):
                    if found:
                        break
                    for j, v2 in enumerate(factor_base):
                        if found:
                            break
                        B_pt = E.lift_x(v2)
                        if B_pt is None:
                            continue
                        for sB in (B_pt, E.negate(B_pt)):
                            if found:
                                break
                            partial = E.add(sA, sB)
                            if partial is None:
                                continue
                            remainder = E.add(target, E.negate(partial))
                            if remainder is None:
                                continue
                            rx = remainder[0]
                            if rx in factor_base:
                                hits += 1
                                row = [0] * B
                                row[factor_base.index(v1)] = 1
                                row[factor_base.index(v2)] = 1
                                row[factor_base.index(rx)] = 1
                                relations.append(row)
                                found = True

                                if include_phi_orbits and zeta3:
                                    for shift in range(1, 3):
                                        shifted_row = [0] * B
                                        for idx in range(B):
                                            if row[idx]:
                                                x = factor_base[idx]
                                                shifted_x = pow(zeta3, shift, p) * x % p
                                                if shifted_x in factor_base:
                                                    shifted_row[factor_base.index(shifted_x)] = 1
                                        if sum(shifted_row) > 0 and shifted_row not in relations:
                                            relations.append(shifted_row)

    return relations, hits, attempts


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run endomorphism-invariant factor base LA experiment."
    )
    ap.add_argument("--bits", default="8,12,16,20,24")
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--arity", default="2,3")
    ap.add_argument("--targets", type=int, default=10)
    ap.add_argument("--exp-id", default=EXP_ID)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    bits_list = [int(b) for b in args.bits.split(",") if b]
    seeds = [int(s) for s in args.seeds.split(",") if s]
    arities = [int(m) for m in args.arity.split(",") if m]
    written = []

    for bits in bits_list:
        for seed in seeds:
            # Generate j=0 instance with p ≡ 1 mod 3
            inst = _generate_j0_instance(seed, bits)
            if inst is None:
                print(f"SKIP: no j=0 p≡1mod3 curve for bits={bits} seed={seed}")
                continue

            p = inst.p
            n = inst.n
            B = math.ceil(math.isqrt(n))
            zeta3 = _find_zeta3(p)
            if zeta3 is None:
                print(f"SKIP: no zeta3 for p={p}")
                continue

            print(f"\n=== bits={bits} seed={seed} p={p} n={n} B={B} zeta3={zeta3} ===")

            # Build factor bases
            phi_fb = _build_phi_invariant_factor_base(inst, B, zeta3)
            rand_fb = _build_random_factor_base(inst, B)
            print(f"phi-invariant FB: {len(phi_fb)} pts, random FB: {len(rand_fb)} pts")

            # Rho baseline
            log = io.StringIO()
            started = time.time()
            with redirect_stdout(log):
                res = rho.solve(inst)
            finished = time.time()

            if res.solved:
                cert = {"kind": "discrete_log",
                        "statement": {"curve": {"p": p, "a": inst.a, "b": inst.b},
                                      "P": list(inst.P), "Q": list(inst.Q), "k": res.k}}
                status = "completed_valid"
                valid = True
            else:
                cert = {"kind": "none"}
                status = "cancelled_by_budget"
                valid = False

            rr = RunResult(
                run_suffix=f"rho-b{bits}-s{seed}",
                curve_id=curve_id(p, inst.a, inst.b, bits),
                seed=seed,
                parameters={"field_bits": bits, "prime_order_n": n, "solver": "pollard_rho"},
                metrics={"group_operations": res.group_operations,
                         "total_group_operations": res.total_group_operations,
                         "iterations": res.iterations, "solved": res.solved},
                certificate=cert, valid=valid,
                stdout=log.getvalue(), raw={"n": n, "recovered_k": res.k},
            )
            written.append(write_run(args.exp_id, EXP_AREA, rr, status=status,
                                     command=f"rho-control bits={bits} seed={seed}",
                                     started=started, finished=finished, out_root=args.out))

            for m in arities:
                # Phi-invariant factor base — collect with phi-orbits for block-circulant structure
                phi_rels, phi_hits, phi_attempts = _collect_relations(
                    inst, phi_fb, m, max(args.targets, B + 10),
                    zeta3=zeta3, include_phi_orbits=True)
                phi_alpha = _measure_displacement_rank(phi_rels, len(phi_fb), "phi", zeta3, p, n) if phi_rels else -1

                # Random factor base — no phi-orbits
                rand_rels, rand_hits, rand_attempts = _collect_relations(
                    inst, rand_fb, m, max(args.targets, B + 10))
                rand_alpha = _measure_displacement_rank(rand_rels, len(rand_fb), "random", zeta3, p, n, seed=inst.seed) if rand_rels else -1

                # Check commutation M*Phi == Phi*M (simplified: check if phi-shift of a relation is also a relation)
                commutation = True
                if phi_rels and len(phi_fb) >= 3:
                    # Take first relation, shift it by phi, check if shifted row exists
                    test_row = phi_rels[0]
                    shifted = [0] * len(phi_fb)
                    for idx in range(len(phi_fb)):
                        orbit_start = (idx // 3) * 3
                        pos_in_orbit = idx % 3
                        shifted_idx = orbit_start + ((pos_in_orbit + 1) % 3)
                        shifted[shifted_idx] = test_row[idx]
                    commutation = shifted in phi_rels

                metrics = {
                    "mode": "phi_invariant" if m == 2 else "phi_invariant_m3",
                    "field_bits": bits,
                    "arity": m,
                    "B": len(phi_fb),
                    "n": n,
                    "zeta3": zeta3,
                    "phi_hits": phi_hits,
                    "phi_attempts": phi_attempts,
                    "phi_hit_rate": phi_hits / phi_attempts if phi_attempts > 0 else 0,
                    "phi_alpha": phi_alpha,
                    "rand_hits": rand_hits,
                    "rand_attempts": rand_attempts,
                    "rand_hit_rate": rand_hits / rand_attempts if rand_attempts > 0 else 0,
                    "rand_alpha": rand_alpha,
                    "density_penalty": (rand_hits / rand_attempts) / (phi_hits / phi_attempts)
                        if phi_attempts > 0 and phi_hits > 0 and rand_attempts > 0 and rand_hits > 0 else -1,
                    "commutation_holds": commutation,
                    "structured_cost": phi_alpha ** 2 * len(phi_fb) * math.ceil(math.log2(len(phi_fb))) if phi_alpha > 0 else -1,
                    "wiedemann_cost": 2 * len(phi_fb) ** 2,
                    "cost_ratio": (phi_alpha ** 2 * len(phi_fb) * math.ceil(math.log2(len(phi_fb)))) / (2 * len(phi_fb) ** 2)
                        if phi_alpha > 0 and len(phi_fb) > 0 else -1,
                }

                rr = RunResult(
                    run_suffix=f"phi-b{bits}-s{seed}-m{m}",
                    curve_id=curve_id(p, inst.a, inst.b, bits),
                    seed=seed,
                    parameters={"field_bits": bits, "arity": m, "B": len(phi_fb), "fb_type": "phi_invariant"},
                    metrics=metrics,
                    certificate={"kind": "none"},
                    valid=True, stdout="", raw={},
                )
                written.append(write_run(args.exp_id, EXP_AREA, rr, status="completed_valid",
                                         command=f"phi-invariant bits={bits} seed={seed} m={m}",
                                         started=started, finished=finished, out_root=args.out))

                # Random FB run
                rr2 = RunResult(
                    run_suffix=f"rand-b{bits}-s{seed}-m{m}",
                    curve_id=curve_id(p, inst.a, inst.b, bits),
                    seed=seed,
                    parameters={"field_bits": bits, "arity": m, "B": len(rand_fb), "fb_type": "random"},
                    metrics={k: v for k, v in metrics.items() if k != "mode"},
                    certificate={"kind": "none"},
                    valid=True, stdout="", raw={},
                )
                written.append(write_run(args.exp_id, EXP_AREA, rr2, status="completed_valid",
                                         command=f"random bits={bits} seed={seed} m={m}",
                                         started=started, finished=finished, out_root=args.out))

    print(f"\nwrote {len(written)} run records:")
    for run_id in written:
        print(f"  {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
