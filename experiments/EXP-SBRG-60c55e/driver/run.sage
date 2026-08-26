#!/usr/bin/env sage
"""EXP-SBRG-60c55e phase-0 structural screen.

This driver compares algebraically equivalent Semaev point-decomposition
representations over ordinary binary curves, measures Boolean Macaulay
rank/fall/syzygy structure, constructs degree-profile-matched planted controls,
and quantifies exact target-independent row-space reuse across a batch of target
points.

It intentionally stops short of claiming a faster ECDLP solver.  A positive
structural signal must survive the preregistered scaling and solver gates in
``../specification.yaml``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Sequence

from sage.all import GF, Matrix, PolynomialRing, vector

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from src.semaev_tree import (  # noqa: E402
    S3_char2,
    build_chained_system_symbolic,
    build_field_and_curve,
    gen_decomposable_R,
)
from macaulay import (  # noqa: E402
    analyze_batch_reuse,
    analyze_layer,
    degree_histogram,
    evaluate,
    first_excess_fall,
    first_nonzero_fall,
    random_matched_system,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=10, help="extension degree for F_{2^n}")
    p.add_argument("--t", type=int, default=4, choices=(3, 4), help="factor-base points")
    p.add_argument(
        "--representation",
        choices=("chain", "balanced", "direct"),
        default="chain",
        help="direct is currently supported for t=3; balanced for t=4",
    )
    p.add_argument("--basis", choices=("power", "normal"), default="power")
    p.add_argument("--orientation", choices=("prefix", "random"), default="prefix")
    p.add_argument("--k", type=int, default=None, help="factor-base subspace dimension")
    p.add_argument("--targets", type=int, default=4)
    p.add_argument("--target-mode", choices=("decomposable", "random"), default="decomposable")
    p.add_argument("--min-degree", type=int, default=2)
    p.add_argument("--max-degree", type=int, default=5)
    p.add_argument("--max-columns", type=int, default=200_000)
    p.add_argument("--max-rows", type=int, default=200_000)
    p.add_argument("--seed", type=int, default=20260824)
    p.add_argument("--output", type=Path, default=None)
    return p.parse_args()


def check_args(args: argparse.Namespace) -> None:
    if args.n < 3:
        raise ValueError("n must be >= 3")
    if args.targets < 1:
        raise ValueError("targets must be >= 1")
    if args.representation == "balanced" and args.t != 4:
        raise ValueError("balanced representation currently requires t=4")
    if args.representation == "direct" and args.t != 3:
        raise ValueError("direct representation currently requires t=3")
    if args.min_degree > args.max_degree:
        raise ValueError("min-degree must be <= max-degree")


def power_basis(Fq, alpha, n: int):
    return [Fq(alpha**j) for j in range(n)]


def element_from_bits(Fq, basis: Sequence, bits: int):
    out = Fq.zero()
    for j, b in enumerate(basis):
        if (bits >> j) & 1:
            out += b
    return out


def find_normal_basis(Fq, alpha, n: int, rng: random.Random):
    """Find a deterministic-for-seed Frobenius normal basis by random search."""
    pb = power_basis(Fq, alpha, n)
    F2 = GF(2)
    for _ in range(1024):
        beta = element_from_bits(Fq, pb, rng.randrange(1, 1 << n))
        conjugates = [beta ** (2**j) for j in range(n)]
        rows = [list(c._vector_()) for c in conjugates]
        if Matrix(F2, rows).rank() == n:
            return conjugates
    raise RuntimeError("failed to find a normal element within 1024 deterministic trials")


def orient_factor_basis(Fq, field_basis: Sequence, k: int, orientation: str, rng: random.Random):
    if orientation == "prefix":
        return list(field_basis[:k])
    F2 = GF(2)
    chosen = []
    attempts = 0
    while len(chosen) < k and attempts < 4096:
        attempts += 1
        candidate = element_from_bits(Fq, field_basis, rng.randrange(1, 1 << len(field_basis)))
        trial = chosen + [candidate]
        rows = [list(x._vector_()) for x in trial]
        if Matrix(F2, rows).rank() == len(trial):
            chosen.append(candidate)
    if len(chosen) != k:
        raise RuntimeError("could not construct random independent factor-base basis")
    return chosen


def enumerate_subspace(Fq, basis: Sequence):
    return [element_from_bits(Fq, basis, bits) for bits in range(1 << len(basis))]


def _substitute_poly(p, sub_map, target_ring):
    result = target_ring.zero()
    for expo, coeff in p.dict().items():
        term = target_ring(coeff)
        for var, exponent in zip(p.parent().gens(), expo):
            if exponent:
                term *= sub_map[var] ** exponent
        result += term
    return result


def descend_grouped(polys, n, k, R_high, field_basis, factor_basis):
    """Weil descend to F_2 while preserving one output group per high-level equation."""
    from sage.all import BooleanPolynomialRing

    var_names = list(R_high.variable_names())
    n_u = sum(name.startswith("u") for name in var_names)
    n_x = sum(name.startswith("x") for name in var_names)
    if n_u + n_x != len(var_names):
        raise ValueError(f"unexpected high-level variables: {var_names}")

    bvar_names = []
    for i in range(n_u):
        bvar_names.extend(f"u{i+1}_{j}" for j in range(n))
    for i in range(n_x):
        bvar_names.extend(f"x{i+1}_{j}" for j in range(k))

    Bring = BooleanPolynomialRing(names=bvar_names, order="degrevlex")
    bvars = Bring.gens()
    Fq = R_high.base_ring()
    Rsubs = PolynomialRing(Fq, bvar_names, order="degrevlex")
    rgens = Rsubs.gens()

    sub_map = {}
    idx = 0
    for i in range(n_u):
        expr = Rsubs.zero()
        for j in range(n):
            expr += rgens[idx] * Rsubs(field_basis[j])
            idx += 1
        sub_map[R_high.gens()[i]] = expr
    for i in range(n_x):
        expr = Rsubs.zero()
        for j in range(k):
            expr += rgens[idx] * Rsubs(factor_basis[j])
            idx += 1
        sub_map[R_high.gens()[n_u + i]] = expr

    grouped = []
    for p in polys:
        p_sub = _substitute_poly(p, sub_map, Rsubs)
        coeff_dict = p_sub.dict()
        group = []
        for coord in range(n):
            bpoly = Bring.zero()
            for expo, coefficient in coeff_dict.items():
                if coefficient._vector_()[coord] == 0:
                    continue
                mon = Bring.one()
                for vi, exponent in enumerate(expo):
                    if exponent:
                        mon *= bvars[vi]
                bpoly += mon
            if bpoly != 0:
                group.append(bpoly)
        grouped.append(group)
    return Bring, grouped


def coerce_without_auxiliary(poly, small_ring, keep: int):
    out = small_ring.zero()
    for expo, coeff in poly.dict().items():
        if any(expo[keep:]):
            raise AssertionError("resultant unexpectedly retained eliminated variable")
        term = small_ring(coeff)
        for i, exponent in enumerate(expo[:keep]):
            if exponent:
                term *= small_ring.gens()[i] ** exponent
        out += term
    return out


def build_direct_t3(Fq, B, R_X):
    big = PolynomialRing(Fq, ["x1", "x2", "x3", "z"], order="degrevlex")
    x1, x2, x3, z = big.gens()
    left = S3_char2(x1, x2, z, big(B))
    right = S3_char2(x3, big(R_X), z, big(B))
    resultant = left.resultant(right, z)
    small = PolynomialRing(Fq, ["x1", "x2", "x3"], order="degrevlex")
    direct = coerce_without_auxiliary(resultant, small, keep=3)
    return small, [direct], 0


def build_balanced_t4(Fq, B, R_X):
    ring = PolynomialRing(Fq, ["u1", "u2", "x1", "x2", "x3", "x4"], order="degrevlex")
    u1, u2, x1, x2, x3, x4 = ring.gens()
    polys = [
        S3_char2(u1, x1, x2, ring(B)),
        S3_char2(u2, x3, x4, ring(B)),
        S3_char2(u1, u2, ring(R_X), ring(B)),
    ]
    return ring, polys, 2


def build_representation(rep: str, t: int, Fq, B, R_X):
    if rep == "chain":
        ring, polys, _ = build_chained_system_symbolic(t, Fq, B, R_X)
        return ring, polys, len(polys) - 1
    if rep == "balanced":
        return build_balanced_t4(Fq, B, R_X)
    if rep == "direct":
        return build_direct_t3(Fq, B, R_X)
    raise ValueError(rep)


def sage_poly_to_mask_poly(poly, variable_index) -> frozenset[int]:
    support: set[int] = set()
    for monomial, coefficient in zip(poly.monomials(), poly.coefficients()):
        if int(coefficient) & 1 == 0:
            continue
        mask = 0
        for variable in monomial.variables():
            mask |= 1 << variable_index[str(variable)]
        if mask in support:
            support.remove(mask)
        else:
            support.add(mask)
    return frozenset(support)


def groups_to_masks(Bring, groups):
    idx = {str(v): i for i, v in enumerate(Bring.gens())}
    return [[sage_poly_to_mask_poly(p, idx) for p in group] for group in groups]


def flatten(groups):
    return [p for group in groups for p in group]


def mask_fingerprint(polys) -> str:
    payload = json.dumps([sorted(p) for p in polys], separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def basis_coordinates(value, basis: Sequence) -> list[int]:
    F2 = GF(2)
    columns = [vector(F2, list(b._vector_())) for b in basis]
    matrix = Matrix(F2, len(columns[0]), len(columns), lambda i, j: columns[j][i])
    rhs = vector(F2, list(value._vector_()))
    solution = matrix.solve_right(rhs)
    return [int(bit) for bit in solution]


def assignment_mask(values_by_name, Bring, field_basis, factor_basis) -> int:
    bits = 0
    for index, variable in enumerate(Bring.gens()):
        name = str(variable)
        stem, coord_s = name.rsplit("_", 1)
        coord = int(coord_s)
        value = values_by_name[stem]
        basis = field_basis if stem.startswith("u") else factor_basis
        coords = basis_coordinates(value, basis)
        if coords[coord]:
            bits |= 1 << index
    return bits


def values_for_known_decomposition(rep: str, points: Sequence):
    values = {f"x{i+1}": points[i][0] for i in range(len(points))}
    if rep == "direct":
        return values
    if rep == "balanced":
        pair1 = points[0] + points[1]
        pair2 = points[2] + points[3]
        if pair1.is_zero() or pair2.is_zero():
            raise ValueError("balanced internal sum hit point at infinity")
        values["u1"] = pair1[0]
        values["u2"] = pair2[0]
        return values
    running = points[0] + points[1]
    if running.is_zero():
        raise ValueError("chain internal sum hit point at infinity")
    values["u1"] = running[0]
    for j in range(2, len(points) - 1):
        running += points[j]
        if running.is_zero():
            raise ValueError("chain internal sum hit point at infinity")
        values[f"u{j}"] = running[0]
    return values


def choose_target(E, t, V, rep, mode: str, rng: random.Random):
    if mode == "random":
        for _ in range(128):
            R = E.random_point()
            if not R.is_zero():
                return R, None
        raise RuntimeError("could not draw nonzero random target")

    for _ in range(256):
        R, points = gen_decomposable_R(E, t, V, rng=rng)
        if R.is_zero():
            continue
        try:
            values_for_known_decomposition(rep, points)
        except ValueError:
            continue
        return R, points
    raise RuntimeError("could not generate nondegenerate decomposable target")


def estimate_columns(nvars: int, degree: int) -> int:
    return sum(math.comb(nvars, d) for d in range(min(nvars, degree) + 1))


def estimate_rows(polys, nvars: int, degree: int) -> int:
    total = 0
    for poly in polys:
        d = max((m.bit_count() for m in poly), default=-1)
        if 0 <= d <= degree:
            total += math.comb(nvars, degree - d)
    return total


def structural_summary(real_layers, control_layers):
    control_by_d = {layer.degree: layer for layer in control_layers}
    out = []
    for real in real_layers:
        control = control_by_d[real.degree]
        out.append(
            {
                "degree": real.degree,
                "real": real.as_dict(),
                "control": control.as_dict(),
                "excess_fall_dim": real.fall_dim - control.fall_dim,
                "excess_syzygy_dim": real.syzygy_dim - control.syzygy_dim,
                "full_rank_delta": real.full_rank - control.full_rank,
                "density_ratio": real.row_density / control.row_density if control.row_density else None,
            }
        )
    return out


def main() -> int:
    args = parse_args()
    check_args(args)
    rng = random.Random(args.seed)

    Fq, E, alpha, A, B = build_field_and_curve(args.n)
    k = args.k if args.k is not None else math.ceil(args.n / args.t) + 1
    if not (1 <= k <= args.n):
        raise ValueError("k must satisfy 1 <= k <= n")

    basis_rng = random.Random(args.seed ^ 0xB4515)
    if args.basis == "power":
        field_basis = power_basis(Fq, alpha, args.n)
    else:
        field_basis = find_normal_basis(Fq, alpha, args.n, basis_rng)
    factor_basis = orient_factor_basis(
        Fq, field_basis, k, args.orientation, random.Random(args.seed ^ 0xFAC70)
    )
    V = enumerate_subspace(Fq, factor_basis)

    target_records = []
    fixed_reference = None
    fixed_fingerprint = None
    target_poly_sets = []
    nvars_reference = None
    effective_degrees = None

    for target_index in range(args.targets):
        R, points = choose_target(E, args.t, V, args.representation, args.target_mode, rng)
        ring, high_polys, fixed_group_count = build_representation(
            args.representation, args.t, Fq, B, R[0]
        )
        Bring, groups = descend_grouped(
            high_polys, args.n, k, ring, field_basis, factor_basis
        )
        mask_groups = groups_to_masks(Bring, groups)
        fixed = flatten(mask_groups[:fixed_group_count])
        target_specific = flatten(mask_groups[fixed_group_count:])
        total = fixed + target_specific
        nvars = Bring.ngens()

        if nvars_reference is None:
            nvars_reference = nvars
        elif nvars != nvars_reference:
            raise AssertionError("variable count changed across target specializations")

        fp = mask_fingerprint(fixed)
        if fixed_reference is None:
            fixed_reference = fixed
            fixed_fingerprint = fp
        elif fixed != fixed_reference or fp != fixed_fingerprint:
            raise AssertionError("target-independent S_struct changed across targets")

        if points is not None:
            values = values_for_known_decomposition(args.representation, points)
            planted_assignment = assignment_mask(values, Bring, field_basis, factor_basis)
            failed = [i for i, p in enumerate(total) if evaluate(p, planted_assignment)]
            if failed:
                raise AssertionError(
                    f"known decomposition does not satisfy descended system; failed equations {failed[:8]}"
                )
            real_solution_verified = True
        else:
            planted_assignment = random.Random(args.seed + target_index * 7919).getrandbits(nvars)
            real_solution_verified = False

        feasible = []
        skips = []
        for degree in range(args.min_degree, args.max_degree + 1):
            cols = estimate_columns(nvars, degree)
            rows = estimate_rows(total, nvars, degree)
            if cols > args.max_columns or rows > args.max_rows:
                skips.append({"degree": degree, "columns": cols, "rows": rows, "reason": "budget"})
                continue
            feasible.append(degree)
        if effective_degrees is None:
            effective_degrees = feasible
        elif feasible != effective_degrees:
            raise AssertionError("feasible degree set changed across targets")

        real_layers = [analyze_layer(total, nvars, d) for d in feasible]
        control, control_meta = random_matched_system(
            total,
            nvars,
            seed=args.seed + 100_003 * (target_index + 1),
            planted_assignment=planted_assignment,
        )
        control_layers = [analyze_layer(control, nvars, d) for d in feasible]
        if any(evaluate(p, planted_assignment) for p in control):
            raise AssertionError("planted control does not satisfy generated null system")

        target_records.append(
            {
                "target_index": target_index,
                "R_x": str(R[0]),
                "known_decomposable": points is not None,
                "real_solution_verified": real_solution_verified,
                "nvars": nvars,
                "equations": len(total),
                "fixed_equations": len(fixed),
                "target_equations": len(target_specific),
                "fixed_fingerprint": fp,
                "equation_degree_histograms": [degree_histogram(p) for p in total],
                "control_meta": control_meta,
                "first_real_fall": first_nonzero_fall(real_layers),
                "first_excess_fall_vs_control": first_excess_fall(real_layers, control_layers),
                "layers": structural_summary(real_layers, control_layers),
                "budget_skips": skips,
            }
        )
        target_poly_sets.append(target_specific)

    batch = []
    if fixed_reference:
        for degree in effective_degrees or []:
            if estimate_rows(fixed_reference, nvars_reference, degree) > args.max_rows:
                continue
            batch.append(
                analyze_batch_reuse(
                    fixed_reference, target_poly_sets, nvars_reference, degree
                ).as_dict()
            )

    result = {
        "experiment_id": "EXP-SBRG-60c55e",
        "claim_tier": "toy-structural",
        "status": "observation-only",
        "parameters": {
            "n": args.n,
            "t": args.t,
            "k": k,
            "representation": args.representation,
            "basis": args.basis,
            "orientation": args.orientation,
            "targets": args.targets,
            "target_mode": args.target_mode,
            "requested_degree_range": [args.min_degree, args.max_degree],
            "effective_degrees": effective_degrees,
            "max_columns": args.max_columns,
            "max_rows": args.max_rows,
            "seed": args.seed,
        },
        "curve": {
            "field": f"F_2^{args.n}",
            "A": str(A),
            "B": str(B),
            "order": int(E.cardinality()),
        },
        "structural_split": {
            "fixed_fingerprint": fixed_fingerprint,
            "fixed_equations": len(fixed_reference or []),
            "target_batches": len(target_poly_sets),
        },
        "targets": target_records,
        "batch_reuse": batch,
        "interpretation_guard": (
            "fall_dim/syzygy_dim and XOR reuse are structural instrumentation only; "
            "no ECDLP speedup is claimable without scaling, actual solver, relation-probability, "
            "and end-to-end rho comparison gates"
        ),
    }

    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
