"""
Seed derivation per experiments/EXP-MONO-12ce1c/specification.yaml `inputs.seed_derivation_rule`.

Every random draw uses SHA-256 of the ASCII bytes of
    domain || "|" || label || "|" || decimal(p) || "|" || decimal(m) || "|" || decimal(counter)
big-endian unsigned, with rejection sampling to avoid modulo bias: for a draw in
[0, M), reject digests >= floor(2**256 / M) * M. Labels used, and no others:
"prime", "curve-a", "curve-b", "spec-x", "fb-x", "quartic", "crosscurve", "plant".
Counters start at 0 and advance once per digest consumed, per label, per (p, m) cell.

This module is deliberately literal and self-contained: a third party reproduces
every instance bit-for-bit from (master_seed placed inside `domain`, domain,
label, p, m, counter).
"""
import hashlib

ALLOWED_LABELS = {
    "prime", "curve-a", "curve-b", "spec-x", "fb-x", "quartic", "crosscurve", "plant",
}


def seed_digest(domain: str, label: str, p: int, m: int, counter: int) -> bytes:
    assert label in ALLOWED_LABELS, f"label {label!r} not in the contract's declared label set"
    s = f"{domain}|{label}|{p}|{m}|{counter}".encode("ascii")
    return hashlib.sha256(s).digest()


def seed_int(domain: str, label: str, p: int, m: int, counter: int) -> int:
    return int.from_bytes(seed_digest(domain, label, p, m, counter), "big")


class Drawer:
    """Stateful per-(domain,label,p,m) counter with rejection-sampled uniform draws."""

    def __init__(self, domain: str, label: str, p: int, m: int, start_counter: int = 0):
        self.domain = domain
        self.label = label
        self.p = p
        self.m = m
        self.counter = start_counter
        self.digests_consumed = 0
        self.rejections = 0

    def draw(self, modulus: int) -> int:
        """Uniform integer in [0, modulus) via rejection sampling on SHA-256(...) mod 2**256."""
        assert modulus > 0
        limit = (2 ** 256 // modulus) * modulus
        while True:
            h = seed_int(self.domain, self.label, self.p, self.m, self.counter)
            self.counter += 1
            self.digests_consumed += 1
            if h < limit:
                return h % modulus
            self.rejections += 1

    def draw_bit(self) -> int:
        """Uniform bit in {0,1} via draw(2)."""
        return self.draw(2)
