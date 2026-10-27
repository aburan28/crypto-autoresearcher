#!/usr/bin/env python3
"""Independent finite audit of the archived BINSTD n=17 field Frobenius.

This certifies concrete finite premises, not the general invariant-subspace
classification in Lean or any empirical yield claim.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

COMMIT = 'c03b34d71ca81ac630eed25dc92db10cfe5bb5b5'
SOURCE = 'experiments/EXP-BINSTD-8bdf86/implementation/gf2.py'
EXPECTED_SHA = '402cf41f4d528346798eb873d09bd1a2f1f204ed6ea654a2d2bfb668c8b3d955'
MOD = (1 << 17) | (1 << 3) | 1
N = 17


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rem(a: int, p: int) -> int:
    d = p.bit_length() - 1
    while a.bit_length() > d:
        a ^= p << (a.bit_length() - d - 1)
    return a


def square(a: int) -> int:
    expanded = sum(1 << (2 * j) for j in range(N) if (a >> j) & 1)
    return rem(expanded, MOD)


def rank(vectors: list[int]) -> int:
    pivots: dict[int, int] = {}
    for v in vectors:
        while v:
            b = v.bit_length() - 1
            if b not in pivots:
                pivots[b] = v
                break
            v ^= pivots[b]
    return len(pivots)


def apply(columns: list[int], a: int) -> int:
    out = 0
    for j, col in enumerate(columns):
        if (a >> j) & 1:
            out ^= col
    return out


def poly_mul(a: int, b: int) -> int:
    out = 0
    for j in range(b.bit_length()):
        if (b >> j) & 1:
            out ^= a << j
    return out


def irreducible_by_trial(p: int) -> tuple[bool, int]:
    d = p.bit_length() - 1
    checked = 0
    for k in range(1, d // 2 + 1):
        for q in range(1 << k, 1 << (k + 1)):
            checked += 1
            if rem(p, q) == 0:
                return False, checked
    return True, checked


def poly_on_map(columns: list[int], p: int, v: int) -> int:
    power = v
    out = 0
    for j in range(p.bit_length()):
        if (p >> j) & 1:
            out ^= power
        power = apply(columns, power)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--revision', default=COMMIT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    commit = subprocess.check_output(['git', 'rev-parse', f'{args.revision}^{{commit}}'], cwd=args.repo).decode().strip()
    source = subprocess.check_output(['git', 'show', f'{commit}:{SOURCE}'], cwd=args.repo)
    source_sha = hashlib.sha256(source).hexdigest()
    demand(source_sha == EXPECTED_SHA, 'runner source differs from archived hash')
    with tempfile.TemporaryDirectory(prefix='binstd-source-') as temp:
        path = Path(temp) / 'gf2.py'
        path.write_bytes(source)
        spec = importlib.util.spec_from_file_location('archived_binstd_gf2', path)
        demand(spec is not None and spec.loader is not None, 'cannot load source')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        field = module.Field(N, MOD)
        demand(module.MODULI[N] == MOD, 'modulus mismatch')
        columns = [square(1 << j) for j in range(N)]
        for a in range(1 << N):
            demand(field.sqr(a) == square(a), f'square differs at {a}')
            demand(field.sqr(a) == apply(columns, a), f'linearity differs at {a}')
    modulus_irred, modulus_checks = irreducible_by_trial(MOD)
    demand(modulus_irred, 'archived field modulus reducible')
    factors = [3, 313, 471]
    product = 1
    factor_checks = {}
    for p in factors:
        irred, checks = irreducible_by_trial(p)
        demand(irred, f'factor {p} reducible')
        factor_checks[str(p)] = checks
        product = poly_mul(product, p)
    demand(product == (1 << N) | 1, 'factor product mismatch')
    order = None
    powered = [1 << j for j in range(N)]
    for k in range(1, N + 1):
        powered = [apply(columns, x) for x in powered]
        if powered == [1 << j for j in range(N)]:
            order = k
            break
    demand(order == N, 'Frobenius order differs')
    normal = None
    for v in range(1, 1 << N):
        orbit = []
        x = v
        for _ in range(N):
            orbit.append(x)
            x = apply(columns, x)
        if rank(orbit) == N:
            normal = v
            break
    demand(normal is not None, 'no cyclic/normal witness found')
    kernel_dims = {}
    for p in factors:
        images = [poly_on_map(columns, p, 1 << j) for j in range(N)]
        kernel_dims[str(p)] = N - rank(images)
    demand(kernel_dims == {'3': 1, '313': 8, '471': 8}, 'factor kernel dimensions differ')
    dims = {0}
    for d in kernel_dims.values():
        dims |= {v + d for v in dims}
    result = {
        'schema': 'crypto.validation.binstd_concrete_frobenius/v1',
        'source_commit': commit,
        'source_path': SOURCE,
        'source_sha256': source_sha,
        'modulus_bitmask': MOD,
        'modulus_irreducible_by_trial': True,
        'modulus_trial_divisors_checked': modulus_checks,
        'factor_bitmasks': factors,
        'factor_trial_divisors_checked': factor_checks,
        'factor_product_bitmask': product,
        'field_values_compared': 1 << N,
        'frobenius_columns': columns,
        'frobenius_order': order,
        'normal_basis_generator_bitmask': normal,
        'normal_basis_orbit_rank': N,
        'factor_kernel_dimensions': kernel_dims,
        'factor_degree_subset_sums': sorted(dims),
        'limit': 'Finite source-bound code audit. The all-invariant-subspace classification and runner-to-canonical bridge remain unproved in Lean; empirical yields and performance are not audited here.',
    }
    out = args.out
    demand(not out.exists(), 'refusing to overwrite result')
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('field_values_compared', 'modulus_trial_divisors_checked', 'frobenius_order', 'normal_basis_generator_bitmask', 'factor_kernel_dimensions', 'factor_degree_subset_sums')}, indent=2))


if __name__ == '__main__':
    main()
