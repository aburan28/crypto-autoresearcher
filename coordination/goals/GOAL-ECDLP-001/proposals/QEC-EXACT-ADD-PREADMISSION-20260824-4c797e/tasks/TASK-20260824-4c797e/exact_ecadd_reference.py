#!/usr/bin/env python3
"""Deterministic semantic reference for TASK-20260824-4c797e.

This is deliberately not a resource estimator.  ``complete_add`` is the
independent oracle.  ``candidate_translate`` is a line-by-line model of the
amended (v2) totalized Fig.14 schedule and its exceptional router.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Sequence, Tuple

Point = Optional[Tuple[int, int]]
WordPair = Tuple[int, int]
OMEGA: WordPair = (0, 0)


@dataclass(frozen=True)
class Curve:
    p: int
    b: int
    order: int
    generator: Tuple[int, int]

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return 0 <= x < self.p and 0 <= y < self.p and (y * y - x * x * x - self.b) % self.p == 0

    def encode(self, point: Point) -> WordPair:
        return OMEGA if point is None else point

    def decode(self, word: WordPair) -> Point:
        return None if word == OMEGA else word


@dataclass
class Scratch:
    z: int = 0
    effective_enable: int = 0
    flags: Dict[str, int] = field(default_factory=lambda: {k: 0 for k in ("fO", "fA", "fNA", "fN2A")})
    qrom_x: int = 0
    qrom_y: int = 0
    arithmetic: int = 0

    def clean(self) -> bool:
        return (
            self.z == 0
            and self.effective_enable == 0
            and not any(self.flags.values())
            and self.qrom_x == 0
            and self.qrom_y == 0
            and self.arithmetic == 0
        )


@dataclass(frozen=True)
class CandidateResult:
    output: WordPair
    scratch_clean: bool
    address: int
    sign: int
    enable: int
    selected_addend: WordPair
    exceptional_branch: Optional[str]
    effective_enable: int


def inv_mod(x: int, p: int) -> int:
    if x % p == 0:
        raise ZeroDivisionError("division by zero in F_p")
    return pow(x % p, -1, p)


def negate(curve: Curve, point: Point) -> Point:
    if point is None:
        return None
    return (point[0], (-point[1]) % curve.p)


def complete_add(curve: Curve, left: Point, right: Point) -> Point:
    """Independent complete affine group-law oracle."""
    if not curve.on_curve(left) or not curve.on_curve(right):
        raise ValueError("oracle accepts only the curve code space")
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % curve.p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1) * inv_mod(2 * y1, curve.p) % curve.p
    else:
        slope = (y2 - y1) * inv_mod(x2 - x1, curve.p) % curve.p
    x3 = (slope * slope - x1 - x2) % curve.p
    y3 = (slope * (x1 - x3) - y1) % curve.p
    result = (x3, y3)
    if not curve.on_curve(result):
        raise AssertionError("complete oracle produced an off-curve point")
    return result


def scalar_mul(curve: Curve, scalar: int, point: Point) -> Point:
    result: Point = None
    addend = point
    k = scalar
    while k:
        if k & 1:
            result = complete_add(curve, result, addend)
        addend = complete_add(curve, addend, addend)
        k >>= 1
    return result


def subgroup(curve: Curve) -> Tuple[Point, ...]:
    return tuple(scalar_mul(curve, k, curve.generator) for k in range(curve.order))


def total_idiv(x: int, y: int, p: int, scratch: Scratch) -> Tuple[int, int]:
    """Wrapper semantics including compute/toggle/primitive/undo/uncompute."""
    if scratch.z:
        raise ValueError("z must enter clean")
    scratch.z ^= int(x == 0)
    wrapped_x = x ^ scratch.z  # X_LSB toggle: zero becomes one.
    if wrapped_x == 0:
        raise AssertionError("wrapped divisor promise was not established")
    y = y * inv_mod(wrapped_x, p) % p
    wrapped_x ^= scratch.z
    scratch.z ^= int(wrapped_x == 0)
    return wrapped_x, y


def total_imul(x: int, y: int, p: int, scratch: Scratch) -> Tuple[int, int]:
    if scratch.z:
        raise ValueError("z must enter clean")
    scratch.z ^= int(x == 0)
    wrapped_x = x ^ scratch.z
    if wrapped_x == 0:
        raise AssertionError("wrapped multiplicand promise was not established")
    y = y * wrapped_x % p
    wrapped_x ^= scratch.z
    scratch.z ^= int(wrapped_x == 0)
    return wrapped_x, y


def partial_idiv(x: int, y: int, p: int) -> Tuple[int, int]:
    """Known-defective source-like promise primitive used only as a control."""
    return x, y * inv_mod(x, p) % p


def xor_pair(word: WordPair, before: WordPair, after: WordPair) -> WordPair:
    return (word[0] ^ before[0] ^ after[0], word[1] ^ before[1] ^ after[1])


def selected_addend(curve: Curve, table: Sequence[Tuple[int, int]], address: int, sign: int) -> Point:
    point: Point = table[address]
    return negate(curve, point) if sign else point


def candidate_translate(
    curve: Curve,
    table: Sequence[Tuple[int, int]],
    accumulator: WordPair,
    address: int,
    sign: int,
    enable: int,
    *,
    omit_totalization: bool = False,
    premature_flag_cleanup: bool = False,
) -> CandidateResult:
    """Basis-state model of the frozen v2 candidate and two negative controls."""
    if enable not in (0, 1) or sign not in (0, 1):
        raise ValueError("enable and sign are bits")
    if not 0 <= address < len(table):
        raise ValueError("address outside table")
    x, y = accumulator
    if not (0 <= x < curve.p and 0 <= y < curve.p):
        raise ValueError("field words must be canonical representatives")
    scratch = Scratch()

    # A coherent qROM load is represented explicitly and later cleared.
    addend = selected_addend(curve, table, address, sign)
    if addend is None:
        raise ValueError("table addends must be nonzero")
    a, b = addend
    scratch.qrom_x, scratch.qrom_y = a, b

    neg_a = negate(curve, addend)
    neg_2a = negate(curve, scalar_mul(curve, 2, addend))
    branch_words = {
        "fO": OMEGA,
        "fA": curve.encode(addend),
        "fNA": curve.encode(neg_a),
        "fN2A": curve.encode(neg_2a),
    }
    for name, word in branch_words.items():
        scratch.flags[name] = int(bool(enable) and accumulator == word)
    branch = next((name for name, value in scratch.flags.items() if value), None)
    if sum(scratch.flags.values()) > 1:
        raise AssertionError("exception flags collided")
    scratch.effective_enable = int(bool(enable) and not any(scratch.flags.values()))
    effective = scratch.effective_enable

    # v2: both Y translations are controlled by effective enable.
    x = (x - a) % curve.p
    if effective:
        y = (y - b) % curve.p
    if omit_totalization:
        x, y = partial_idiv(x, y, curve.p)
    else:
        x, y = total_idiv(x, y, curve.p, scratch)
    if effective:
        x = (x - y * y + 3 * a) % curve.p
    x, y = total_imul(x, y, curve.p, scratch)
    if effective:
        x = (-x) % curve.p
    x = (x + a) % curve.p
    if effective:
        y = (y - b) % curve.p
    word = (x, y)

    exceptional_outputs = {
        "fO": curve.encode(addend),
        "fA": curve.encode(scalar_mul(curve, 2, addend)),
        "fNA": OMEGA,
        "fN2A": curve.encode(neg_a),
    }
    if premature_flag_cleanup:
        for name, before in branch_words.items():
            scratch.flags[name] ^= int(bool(enable) and word == before)
    for name, before in branch_words.items():
        if scratch.flags[name]:
            word = xor_pair(word, before, exceptional_outputs[name])

    # e is uncomputed while the original branch flags remain available.
    scratch.effective_enable ^= int(bool(enable) and not any(scratch.flags.values()))
    if not premature_flag_cleanup:
        for name, after in exceptional_outputs.items():
            scratch.flags[name] ^= int(bool(enable) and word == after)

    scratch.qrom_x ^= a
    scratch.qrom_y ^= b
    return CandidateResult(
        output=word,
        scratch_clean=scratch.clean(),
        address=address,
        sign=sign,
        enable=enable,
        selected_addend=curve.encode(addend),
        exceptional_branch=branch,
        effective_enable=effective,
    )


TINY_CURVE = Curve(p=13, b=7, order=7, generator=(7, 5))
TINY_TABLE = (
    TINY_CURVE.generator,
    scalar_mul(TINY_CURVE, 3, TINY_CURVE.generator),
)

