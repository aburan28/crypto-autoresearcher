"""
Seed derivation per experiments/EXP-MONO-b19c6b/specification.yaml
`inputs.seed_derivation_rule`.

Every random draw uses SHA-256 of the ASCII bytes of
    domain || "|" || decimal(master_seed) || "|" || family || "|" ||
    label || "|" || decimal(field_bits_or_p) || "|" ||
    decimal(curve_ordinal) || "|" || decimal(m) || "|" ||
    decimal(draw_index) || "|" || decimal(counter)
big-endian unsigned, with rejection sampling to avoid modulo bias: for a draw
in [0, M), reject digests >= floor(2**256 / M) * M. Labels used, and no
others: "prime", "curve-a", "curve-b", "null-subset", "null-object-pick".
`family` is one of "j0", "random-ordinary" and no others, and MUST appear in
the preimage of EVERY ONE of these five labels -- this is the single
arithmetic fix for EXP-MONO-670aa6's total panel-independence failure.
`master_seed` also appears in the preimage (fixing a second EXP-MONO-670aa6
defect: its own seed rule declared `master_seed` as an input but never used
it, so both its "independent" replication runs shared one identical panel).

This module is intentionally written FRESH for EXP-MONO-b19c6b (not copied
from EXP-MONO-670aa6's seed.py) precisely because the family/master_seed
threading is this contract's central fix and must appear at every one of
the five call sites, not two of six as before.
"""
import hashlib

ALLOWED_LABELS = {"prime", "curve-a", "curve-b", "null-subset", "null-object-pick"}
ALLOWED_FAMILIES = {"j0", "random-ordinary"}


def seed_digest(domain: str, master_seed: int, family: str, label: str,
                 field_bits_or_p: int, curve_ordinal: int, m: int,
                 draw_index: int, counter: int) -> bytes:
    assert label in ALLOWED_LABELS, f"label {label!r} not in the contract's declared label set"
    assert family in ALLOWED_FAMILIES, f"family {family!r} not in the contract's declared family set"
    s = (f"{domain}|{master_seed}|{family}|{label}|{field_bits_or_p}|"
         f"{curve_ordinal}|{m}|{draw_index}|{counter}").encode("ascii")
    return hashlib.sha256(s).digest()


def seed_int(domain: str, master_seed: int, family: str, label: str,
             field_bits_or_p: int, curve_ordinal: int, m: int,
             draw_index: int, counter: int) -> int:
    return int.from_bytes(
        seed_digest(domain, master_seed, family, label, field_bits_or_p,
                    curve_ordinal, m, draw_index, counter), "big")


class Drawer:
    """Stateful per-(domain,master_seed,family,label,field_bits_or_p,
    curve_ordinal,m,draw_index) counter with rejection-sampled uniform
    draws, per the frozen seed_derivation_rule. `family` MUST be supplied at
    every call site -- this is the contract's central fix over
    EXP-MONO-670aa6."""

    def __init__(self, domain: str, master_seed: int, family: str, label: str,
                 field_bits_or_p: int, curve_ordinal: int, m: int, draw_index: int,
                 start_counter: int = 0):
        self.domain = domain
        self.master_seed = master_seed
        self.family = family
        self.label = label
        self.field_bits_or_p = field_bits_or_p
        self.curve_ordinal = curve_ordinal
        self.m = m
        self.draw_index = draw_index
        self.counter = start_counter
        self.digests_consumed = 0
        self.rejections = 0

    def draw(self, modulus: int) -> int:
        assert modulus > 0
        limit = (2 ** 256 // modulus) * modulus
        while True:
            h = seed_int(self.domain, self.master_seed, self.family, self.label,
                         self.field_bits_or_p, self.curve_ordinal, self.m,
                         self.draw_index, self.counter)
            self.counter += 1
            self.digests_consumed += 1
            if h < limit:
                return h % modulus
            self.rejections += 1

    def draw_bit(self) -> int:
        return self.draw(2)
