"""
Seed derivation per experiments/EXP-MONO-670aa6/specification.yaml
`inputs.seed_derivation_rule`.

Every random draw uses SHA-256 of the ASCII bytes of
    domain || "|" || label || "|" || decimal(field_bits_or_p) || "|" ||
    decimal(curve_ordinal) || "|" || decimal(m) || "|" || decimal(draw_index) ||
    "|" || decimal(counter)
big-endian unsigned, with rejection sampling to avoid modulo bias: for a draw
in [0, M), reject digests >= floor(2**256 / M) * M. Labels used, and no
others: "prime", "curve-a", "curve-b", "null-subset", "null-object-pick",
"coset-pick". Counters start at 0 and advance once per digest consumed, per
label, per (field_bits_or_p, curve_ordinal, m, draw_index).
"""
import hashlib

ALLOWED_LABELS = {"prime", "curve-a", "curve-b", "null-subset", "null-object-pick", "coset-pick"}


def seed_digest(domain: str, label: str, field_bits_or_p: int, curve_ordinal: int,
                 m: int, draw_index: int, counter: int) -> bytes:
    assert label in ALLOWED_LABELS, f"label {label!r} not in the contract's declared label set"
    s = f"{domain}|{label}|{field_bits_or_p}|{curve_ordinal}|{m}|{draw_index}|{counter}".encode("ascii")
    return hashlib.sha256(s).digest()


def seed_int(domain: str, label: str, field_bits_or_p: int, curve_ordinal: int,
             m: int, draw_index: int, counter: int) -> int:
    return int.from_bytes(
        seed_digest(domain, label, field_bits_or_p, curve_ordinal, m, draw_index, counter), "big")


class Drawer:
    """Stateful per-(domain,label,field_bits_or_p,curve_ordinal,m,draw_index) counter
    with rejection-sampled uniform draws, per the frozen seed_derivation_rule."""

    def __init__(self, domain: str, label: str, field_bits_or_p: int, curve_ordinal: int,
                 m: int, draw_index: int, start_counter: int = 0):
        self.domain = domain
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
            h = seed_int(self.domain, self.label, self.field_bits_or_p, self.curve_ordinal,
                         self.m, self.draw_index, self.counter)
            self.counter += 1
            self.digests_consumed += 1
            if h < limit:
                return h % modulus
            self.rejections += 1

    def draw_bit(self) -> int:
        return self.draw(2)
