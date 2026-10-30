"""Certify a target log from verified affine rows without solving all base logs.

The caller must verify curve/divisor witnesses before inserting their rows.
This module supplies linear certificates and a final public-point check, not
row provenance or a fast natural relation-generation claim.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256

from .curve import is_probable_prime
from .relation_quality import AffineRelations


class TargetRelations:
    """Snapshot Mz=b and append vz - t*k = offset as rows arrive."""

    def __init__(self, base: AffineRelations):
        self.base = AffineRelations(base.modulus, base.columns)
        self.augmented = AffineRelations(base.modulus, base.columns+1)
        for row, rhs in zip(base.rows, base.rhs):
            self.base.add(row, rhs)
            self.augmented.add(row+[0], rhs)
        self.base_row_count = len(self.base.rows)
        self.target_rows = []

    def add(self, coefficients, offset: int, target_coefficient: int):
        """Insert atomically; retain zero-target rows as such, never as successes."""
        if type(offset) is not int or type(target_coefficient) is not int:
            raise ValueError('integer offset and target coefficient required')
        values = list(coefficients)
        row = self.base._row(values)  # exact dimension/type validation
        p = self.base.modulus
        values = [row.get(i, 0) for i in range(self.base.columns)]
        coefficient = target_coefficient % p
        single = self.base.identify(values)
        single_scalar = ((single.value-offset)*pow(coefficient, -1, p) % p
                         if single.identifiable and coefficient else None)
        independent = self.augmented.add(values+[-coefficient], offset)
        record = dict(coefficients=values, offset=offset % p,
                      target_coefficient=coefficient, carries_target_information=bool(coefficient),
                      single_row_scalar=single_scalar, base_syndrome=list(single.syndrome),
                      independent_augmented_row=independent)
        self.target_rows.append(record)
        return record

    def identify(self):
        """Return k and weights on original base + target rows, or no value."""
        unit = [0]*self.base.columns+[1]
        result = self.augmented.identify(unit)
        if result.identifiable:
            p, weights = self.base.modulus, result.row_weights
            # Explicitly check both the identity and RHS against original rows.
            actual = [sum(w*row[j] for w, row in zip(weights, self.augmented.rows)) % p
                      for j in range(self.augmented.columns)]
            if actual != unit or sum(w*b for w, b in zip(weights, self.augmented.rhs)) % p != result.value:
                raise ArithmeticError('target row-combination certificate failed')
        return dict(**asdict(result), base_rank=self.base.rank,
                    base_columns=self.base.columns, base_rows=self.base_row_count,
                    target_rows=len(self.target_rows), augmented_rank=self.augmented.rank)

    def verify(self, curve, generator, target):
        """Return a certificate only if its scalar passes the public group check."""
        if generator is None or not curve.is_on_curve(generator) or not curve.is_on_curve(target):
            raise ValueError('invalid public generator/target')
        if curve.mul(self.base.modulus, generator) is not None or curve.mul(self.base.modulus, target) is not None:
            raise ValueError('public points lie outside the stated subgroup')
        result = self.identify()
        if not result['identifiable']:
            return None
        if curve.mul(result['value'], generator) != target:
            raise ValueError('target scalar failed public verification')
        return dict(**result, scalar=result['value'], verified=True)


def hash_public_target(curve, subgroup_order: int, curve_uid: str, index: int,
                       *, max_counters=10000,
                       domain='prime-field-leads/20261028/target/v1', on_attempt=None):
    """Deterministic public target recipe; no target scalar is ever generated.

    Scientific callers must freeze this source, domain, indices, counter limit,
    curve and subgroup before invoking it. Software tests use small fixtures.
    """
    if (type(index) is not int or index < 0 or type(max_counters) is not int or max_counters < 1 or
            not is_probable_prime(subgroup_order)):
        raise ValueError('nonnegative index, positive counter bound and prime subgroup required')
    if not curve_uid or not domain or '|' in curve_uid or '|' in domain:
        raise ValueError('nonempty delimiter-free domain and curve UID required')
    rejected = []
    for counter in range(max_counters):
        message = f'{domain}|{curve_uid}|{index}|{counter}'.encode('utf-8')
        digest = sha256(message).digest()
        x = int.from_bytes(digest, 'big') % curve.p
        point = curve.lift_x(x)
        reason = 'not_rational' if point is None else (
            'outside_subgroup' if curve.mul(subgroup_order, point) is not None else None)
        record = dict(counter=counter, sha256=digest.hex(), x=x)
        if on_attempt is not None:
            on_attempt(dict(**record, status=reason or 'selected'))
        if reason:
            rejected.append(dict(**record, reason=reason))
            continue
        return dict(curve_uid=curve_uid, domain=domain, index=index,
                    encoding='UTF-8 domain|curve_uid|decimal_index|decimal_counter; SHA256 big-endian mod p',
                    point=list(point), selected=record, rejected=rejected,
                    subgroup_order=subgroup_order, scalar_label_generated=False)
    raise ValueError('fixed public-target counter bound exhausted')
