"""The PATH OBJECT SCHEMA -- what a "differential path" IS, machine-readably.

Binding schema: EXP-DIFFP-fe894e `path_object_schema`.  The census, the
verifier, the equivalence generators and the adjudicator all read THIS object;
it is deliberately not forked per primitive beyond the two declared variants,
because a per-primitive fork is how a canonical form silently stops being
comparable.

MODULAR DIFFERENCES ARE CANONICAL.  Signed-bit-difference representations are
DERIVED and are recorded so that a representation change is visible rather than
silent (contract md5_variant, and generator E4).

A `quarantined_not_read` or `acquisition_gap` entry has path_data None and is a
POINTER: it is never canonicalised, never counted in an orbit, and contributes
to no covering number.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from . import primitives as P

MASK32 = P.MASK32


# ---------------------------------------------------------------------------
# signed-digit representation of a modular difference (generator E4)
# ---------------------------------------------------------------------------

def bsdr_encode(delta: int, width: int = 32) -> tuple[tuple[int, int], ...]:
    """Non-adjacent-form signed-digit representation of delta mod 2**32.

    Returns a tuple of (bit_index, sign) with sign in {+1, -1}.  This is ONE
    representation among many; `bsdr_decode` recovers the modular difference
    from ANY of them, which is exactly the content of E4.
    """
    d = delta & ((1 << width) - 1)
    out: list[tuple[int, int]] = []
    i = 0
    while d and i < width + 2:
        if d & 1:
            z = 2 - (d & 3)          # NAF digit in {-1, +1}
            out.append((i, 1 if z > 0 else -1))
            d -= z
        d >>= 1
        i += 1
    return tuple(out)


def bsdr_decode(digits, width: int = 32) -> int:
    v = 0
    for (i, s) in digits:
        v += s * (1 << i)
    return v & ((1 << width) - 1)


def bsdr_alternative(delta: int, width: int = 32) -> tuple[tuple[int, int], ...]:
    """A DIFFERENT signed-digit representation of the same modular difference.

    Uses the identity 2**j = 2**(j+1) - 2**j on the lowest digit.  E4's second
    clause requires that two DISTINCT signed representations of one modular
    difference canonicalise identically; this function manufactures the second
    one so that requirement can be tested rather than asserted.
    """
    digits = list(bsdr_encode(delta, width))
    if not digits:
        return ((0, 1), (0, -1))
    (i, s) = digits[0]
    rest = digits[1:]
    expanded = [(i + 1, s), (i, -s)]
    return tuple(sorted(expanded + rest))


def signed_bit_diff(x: int, xp: int) -> tuple[tuple[int, int], ...]:
    """Signed BIT difference of an observed pair: +1 where 0->1, -1 where 1->0."""
    out = []
    diff = (x ^ xp) & MASK32
    for j in range(32):
        if (diff >> j) & 1:
            out.append((j, 1 if (xp >> j) & 1 else -1))
    return tuple(out)


# ---------------------------------------------------------------------------
# the sufficient-condition set
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Condition:
    """One sufficient condition: a pinned bit of an unprimed addend.

    step      step index the condition applies at
    operand   't' (the pre-rotation modular sum) or 'q' (the outer addend)
    bit       bit index 0..31
    value     the required bit value in the UNPRIMED message's computation
    value_p   the corresponding bit value in the PRIMED computation

    value_p is stored so that the global sign flip E3 -- which swaps which
    member of the pair is "unprimed" -- is a total, invertible operation on the
    condition set rather than something the canonicaliser has to guess.
    """
    step: int
    operand: str
    bit: int
    value: int
    value_p: int

    def key(self):
        return (self.step, self.operand, self.bit, self.value)

    def swapped(self) -> "Condition":
        return Condition(self.step, self.operand, self.bit, self.value_p, self.value)


def carry_window_conditions(step: int, operand: str, x: int, xp: int) -> list[Condition]:
    """Pin exactly the bits of the unprimed addend that fix the carry chain.

    x' = x + delta (mod 2**32).  Let lo be the lowest set bit of delta and hi
    the highest bit at which x and x' differ.  Bits of x below lo do not enter
    the addition at all, and bits of x in [lo, hi] determine the whole carry
    chain, whose carry out of hi is zero because x and x' agree above hi.  So
    pinning x on [lo, hi] is SUFFICIENT for the observed bit-difference pattern
    to reproduce.  Bits above hi are deliberately NOT pinned: over-pinning
    would make the condition set look stronger than the path needs.
    """
    delta = (xp - x) & MASK32
    if delta == 0:
        return []
    lo = (delta & -delta).bit_length() - 1
    diff = (x ^ xp) & MASK32
    if diff == 0:
        return []
    hi = diff.bit_length() - 1
    return [Condition(step, operand, j, (x >> j) & 1, (xp >> j) & 1)
            for j in range(lo, hi + 1)]


# ---------------------------------------------------------------------------
# the path object
# ---------------------------------------------------------------------------

@dataclass
class PathObject:
    # --- common (contract path_object_schema.common) ---
    id: str
    primitive: str                       # md5 | sha1
    step_range: tuple[int, int]          # inclusive, 0-indexed
    provenance: str                      # recalled | retrieved | kb | internal
    source_ref: str
    status: str                          # readable | quarantined_not_read | acquisition_gap
    conditions: tuple[Condition, ...] = ()

    # --- path data; None for pointer entries ---
    path_data: dict | None = None

    # md5_variant: delta_m (16 modular differences) + derived signed digits
    delta_m: tuple[int, ...] | None = None
    delta_m_signed: tuple | None = None
    # sha1_variant: dv words over step_range + seed window + computed flag
    dv: tuple[int, ...] | None = None
    dv_seed_window: tuple[int, ...] | None = None
    in_linearized_code: bool | None = None

    # per-step state differences over step_range: modular is CANONICAL,
    # signed is DERIVED.
    step_delta: tuple[int, ...] = ()
    step_delta_signed: tuple = ()

    # the generating witness (present for every object this task constructs;
    # absent for pointer entries).  Recorded so that every generator can be
    # applied by RE-DERIVING from a transformed pair rather than by asserting
    # what the transformed path "would" be.
    cv: tuple[int, ...] | None = None
    m: tuple[int, ...] | None = None
    mp: tuple[int, ...] | None = None

    block_index: int = 0                 # E6: never read by the conformance predicate
    notes: dict = field(default_factory=dict)

    @property
    def length(self) -> int:
        return self.step_range[1] - self.step_range[0] + 1

    def is_pointer(self) -> bool:
        return self.status in ("quarantined_not_read", "acquisition_gap")


def plant_from_pair(obj_id: str, primitive: str, cv, m, mp,
                    step_range: tuple[int, int],
                    source_ref: str = "TASK-20260824-c6625a",
                    provenance: str = "internal",
                    block_index: int = 0) -> PathObject:
    """Build the path object a message pair ACTUALLY induces.

    A planted path is the real differential of a real pair, so it is conforming
    by construction and needs no literature -- which is exactly why CTL-PLANT
    can be run at census size zero.
    """
    comp = P.COMPRESS[primitive]
    tr = comp(tuple(cv), list(m))
    trp = comp(tuple(cv), list(mp))
    a, b = step_range
    step_delta = tuple(P.sub32(trp.q[i], tr.q[i]) for i in range(a, b + 1))
    step_signed = tuple(signed_bit_diff(tr.q[i], trp.q[i]) for i in range(a, b + 1))

    conds: list[Condition] = []
    for i in range(a, b + 1):
        conds += carry_window_conditions(i, "t", tr.t[i], trp.t[i])
        if primitive == "md5":
            prev = tr.q[i - 1] if i >= 1 else cv[1]
            prevp = trp.q[i - 1] if i >= 1 else cv[1]
            conds += carry_window_conditions(i, "q", prev, prevp)

    obj = PathObject(
        id=obj_id, primitive=primitive, step_range=(a, b),
        provenance=provenance, source_ref=source_ref, status="readable",
        conditions=tuple(sorted(conds, key=lambda c: c.key())),
        path_data={"kind": "planted_from_pair"},
        step_delta=step_delta, step_delta_signed=step_signed,
        cv=tuple(cv), m=tuple(m), mp=tuple(mp), block_index=block_index,
    )
    if primitive == "md5":
        obj.delta_m = tuple(P.sub32(mp[j], m[j]) for j in range(16))
        obj.delta_m_signed = tuple(bsdr_encode(d) for d in obj.delta_m)
    else:
        w = P.sha1_expand(list(m), 80)
        wp = P.sha1_expand(list(mp), 80)
        full_dv = [(w[i] ^ wp[i]) & MASK32 for i in range(80)]
        obj.dv = tuple(full_dv[a:b + 1])
        obj.dv_seed_window = tuple(full_dv[:16])
        obj.in_linearized_code = P.sha1_in_linearized_code(list(full_dv))
    return obj


def seeded_pair(rng: random.Random, primitive: str, delta_m: list[int] | None = None,
                cv=None):
    """A seeded random message pair, optionally at a prescribed delta_m."""
    m = [rng.getrandbits(32) for _ in range(16)]
    if delta_m is None:
        delta_m = [0] * 16
        delta_m[rng.randrange(16)] = 1 << rng.randrange(32)
    if primitive == "md5":
        mp = [P.add32(m[j], delta_m[j]) for j in range(16)]
    else:
        mp = [(m[j] ^ delta_m[j]) & MASK32 for j in range(16)]
    if cv is None:
        cv = P.DEFAULT_IV[primitive]
    return tuple(cv), m, mp
