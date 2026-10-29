"""Exact affine relation diagnostics over a prime subgroup field.

Rows here must already have passed the caller's point/witness verifier. These
algebraic certificates do not establish curve membership or performance.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .curve import is_probable_prime


@dataclass(frozen=True)
class IdentifiedValue:
    identifiable: bool
    value: int | None
    row_weights: tuple[int, ...] | None
    syndrome: tuple[int, ...]


class AffineRelations:
    """Sparse elimination with original-row certificates and consistency checks."""

    def __init__(self, modulus: int, columns: int):
        if not is_probable_prime(modulus) or columns < 0:
            raise ValueError("prime modulus and nonnegative column count required")
        self.modulus, self.columns = modulus, columns
        self.rows: list[list[int]] = []
        self.rhs: list[int] = []
        self.pivots: dict[int, tuple[dict[int, int], int, dict[int, int]]] = {}
        self.equations: set[tuple[int, ...]] = set()
        self.duplicates = 0

    def _row(self, row):
        values = list(row)
        if len(values) != self.columns or any(type(x) is not int for x in values):
            raise ValueError("row must contain exactly columns integer entries")
        return {i: x % self.modulus for i, x in enumerate(values) if x % self.modulus}

    def _reduce(self, row, rhs=0, weights=None):
        p = self.modulus
        weights = {} if weights is None else dict(weights)
        for pivot, (old, value, certificate) in sorted(self.pivots.items()):
            scale = row.get(pivot, 0)
            if not scale:
                continue
            for j, x in old.items():
                new = (row.get(j, 0) - scale*x) % p
                if new:
                    row[j] = new
                else:
                    row.pop(j, None)
            rhs = (rhs-scale*value) % p
            for j, x in certificate.items():
                new = (weights.get(j, 0)-scale*x) % p
                if new:
                    weights[j] = new
                else:
                    weights.pop(j, None)
        return row, rhs, weights

    def add(self, coefficients, rhs: int) -> bool:
        """Insert atomically; reject inconsistent rows without changing state."""
        if type(rhs) is not int:
            raise ValueError("integer rhs required")
        p = self.modulus
        row = self._row(coefficients)
        original = [row.get(i, 0) for i in range(self.columns)]
        affine = original + [rhs % p]
        first = next((v for v in affine if v), None)
        key = tuple(v*pow(first, -1, p) % p for v in affine) if first else tuple(affine)
        index = len(self.rows)
        reduced, value, weights = self._reduce(dict(row), rhs % p, {index: 1})
        if not reduced and value:
            raise ValueError("inconsistent affine relation system")
        independent = bool(reduced)
        if reduced:
            pivot = min(reduced)
            inverse = pow(reduced[pivot], -1, p)
            self.pivots[pivot] = (
                {i: x*inverse % p for i, x in reduced.items()}, value*inverse % p,
                {i: x*inverse % p for i, x in weights.items()})
        self.rows.append(original)
        self.rhs.append(rhs % p)
        self.duplicates += key in self.equations
        self.equations.add(key)
        return independent

    @property
    def rank(self):
        return len(self.pivots)

    def kernel(self) -> list[list[int]]:
        """A complete right-kernel basis, one vector for each free column."""
        basis = []
        for free in range(self.columns):
            if free in self.pivots:
                continue
            vector = [0]*self.columns
            vector[free] = 1
            for pivot, (row, _, _) in sorted(self.pivots.items(), reverse=True):
                vector[pivot] = -sum(x*vector[j] for j, x in row.items() if j != pivot) % self.modulus
            basis.append(vector)
        return basis

    def identify(self, coefficients) -> IdentifiedValue:
        row = self._row(coefficients)
        syndrome = tuple(sum(row.get(i, 0)*x for i, x in enumerate(v)) % self.modulus
                         for v in self.kernel())
        residual, value, weights = self._reduce(row)
        if residual:
            return IdentifiedValue(False, None, None, syndrome)
        # Reduction computes v - sum(lambda_i M_i)=0 and -sum(lambda_i b_i).
        certificate = tuple(-weights.get(i, 0) % self.modulus for i in range(len(self.rows)))
        return IdentifiedValue(True, -value % self.modulus, certificate, syndrome)

    def summary(self):
        return dict(rows=len(self.rows), unique_affine_equations=len(self.equations),
                    duplicate_equations=self.duplicates, rank=self.rank,
                    columns=self.columns, nullity=self.columns-self.rank)


def cancel_outside(base: AffineRelations, base_rows, outside_rows, rhs):
    """Return base-only equations, each with weights on the new partial rows.

    Eliminating U while carrying B and b constructs the image of ker(U^T).
    The rank gain equals rank([[M,0],[B,U]])-rank(U)-rank(M).
    """
    B, U, values = [list(row) for row in base_rows], [list(row) for row in outside_rows], list(rhs)
    if not (len(B) == len(U) == len(values)):
        raise ValueError("partial row counts differ")
    width = len(U[0]) if U else 0
    count, p = len(B), base.modulus
    elimination = AffineRelations(p, width)
    for row in U:
        elimination._row(row)
    for row in B:
        base._row(row)
    if any(type(value) is not int for value in values):
        raise ValueError('integer partial rhs required')
    # Homogeneous U^T kernel gives all cancellation weights, without solving logs.
    transposed = AffineRelations(p, count)
    for j in range(width):
        transposed.add([row[j] for row in U], 0)
    combined = AffineRelations(p, base.columns)
    for row, value in zip(base.rows, base.rhs):
        combined.add(row, value)
    certificates = []
    for weights in transposed.kernel():
        row = [sum(w*B[i][j] for i, w in enumerate(weights)) % p for j in range(base.columns)]
        value = sum(w*values[i] for i, w in enumerate(weights)) % p
        independent = combined.add(row, value)
        certificates.append(dict(coefficients=row, rhs=value, partial_row_weights=weights,
                                 independent_of_base_and_previous=independent))
    return dict(outside_rank=transposed.rank, base_rank_before=base.rank,
                base_rank_after=combined.rank, rank_gain=combined.rank-base.rank,
                cancellations=certificates)


def rank_per_cost(rank_gain: int, charged_cost: int):
    """Exact comparable rate; zero cost is unmeasured, never infinite throughput."""
    if type(rank_gain) is not int or type(charged_cost) is not int or min(rank_gain, charged_cost) < 0:
        raise ValueError("nonnegative integer gain and counted cost required")
    return None if charged_cost == 0 else Fraction(rank_gain, charged_cost)


def recover_target(curve, generator, target, relations: AffineRelations, coefficients,
                   *, offset=0, target_coefficient=1):
    """Recover k from v*z = offset + target_coefficient*k, then verify [k]P=Q.

    The caller supplies a verified natural decomposition row. No individual
    factor-base logarithms or known target scalar are required.
    """
    p = relations.modulus
    if target_coefficient % p == 0:
        raise ValueError('zero target coefficient carries no target information')
    if generator is None or not curve.is_on_curve(generator) or not curve.is_on_curve(target):
        raise ValueError('invalid public generator/target')
    if curve.mul(p, generator) is not None or curve.mul(p, target) is not None:
        raise ValueError('generator/target not in the stated subgroup')
    identified = relations.identify(coefficients)
    if not identified.identifiable:
        return None
    scalar = (identified.value-offset)*pow(target_coefficient % p, -1, p) % p
    if curve.mul(scalar, generator) != target:
        raise ValueError('recovered scalar fails public verification')
    return dict(scalar=scalar, row_weights=list(identified.row_weights),
                value=identified.value, verified=True)
