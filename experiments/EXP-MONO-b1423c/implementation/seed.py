"""
Seed derivation for EXP-MONO-b1423c, per specification.yaml
`inputs.seed_derivation_rule`:

    SHA-256 of domain || "|" || decimal(master_seed) || "|" ||
    "null-subset" || "|" || decimal(p) || "|" || decimal(h) || "|" ||
    decimal(draw_index) || "|" || decimal(counter)

big-endian unsigned, rejection-sampled against modulo bias -- IDENTICAL
mechanism (rejection sampling for a draw in [0, M): reject digests >=
floor(2**256 / M) * M) to EXP-MONO-b19c6b's own `controls.py::
draw_symmetric_subset` / `seed.py::Drawer`, but with THIS contract's own,
smaller preimage (no `family`/`curve_ordinal`/`m` fields, since this
contract fixes a single curve, RO3, and does not need family-keying or
per-curve-ordinal separation across a panel scan -- there is only one
curve and two h-cells here, both named directly in the preimage instead).

`seed_int` (module-level, generic form matching EXP-MONO-b19c6b's/
EXP-MONO-c819ba's `seed.seed_int` NAME only, not reused for any draw in
this contract) is kept only so that the byte-identical, unmodified
`curve.py` copied from EXP-MONO-b19c6b -- which does `from seed import
seed_int` at import time -- imports cleanly. It is never called: this
contract builds RO3 directly from its already-known, already-published
(p, A, B) rather than re-deriving a prime/curve pair from a seed, so no
code path in this contract's own `run.py` invokes `construct_prime` or
`curve_stream` (the only two functions in curve.py that call it).
"""
import hashlib


def seed_int(domain, master_seed, family, label, field_bits_or_p,
              curve_ordinal, m, draw_index, counter):
    """Unused stub, present only to satisfy curve.py's module-level import.
    Not part of this contract's own seed_derivation_rule and not called by
    any code path this contract exercises."""
    s = (f"{domain}|{master_seed}|{family}|{label}|{field_bits_or_p}|"
         f"{curve_ordinal}|{m}|{draw_index}|{counter}").encode("ascii")
    return int.from_bytes(hashlib.sha256(s).digest(), "big")


def null_subset_seed_int(domain: str, master_seed: int, p: int, h: int,
                          draw_index: int, counter: int) -> int:
    """The contract's own frozen preimage, exactly as declared in
    specification.yaml `inputs.seed_derivation_rule`."""
    s = f"{domain}|{master_seed}|null-subset|{p}|{h}|{draw_index}|{counter}".encode("ascii")
    return int.from_bytes(hashlib.sha256(s).digest(), "big")


class NullSubsetDrawer:
    """Stateful per-(domain, master_seed, p, h, draw_index) counter with
    rejection-sampled uniform draws, per this contract's own frozen
    seed_derivation_rule."""

    def __init__(self, domain: str, master_seed: int, p: int, h: int,
                 draw_index: int, start_counter: int = 0):
        self.domain = domain
        self.master_seed = master_seed
        self.p = p
        self.h = h
        self.draw_index = draw_index
        self.counter = start_counter
        self.digests_consumed = 0
        self.rejections = 0

    def draw(self, modulus: int) -> int:
        assert modulus > 0
        limit = (2 ** 256 // modulus) * modulus
        while True:
            v = null_subset_seed_int(self.domain, self.master_seed, self.p,
                                      self.h, self.draw_index, self.counter)
            self.counter += 1
            self.digests_consumed += 1
            if v < limit:
                return v % modulus
            self.rejections += 1

    def draw_bit(self) -> int:
        return self.draw(2)
