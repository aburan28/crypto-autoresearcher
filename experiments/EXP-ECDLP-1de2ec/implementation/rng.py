"""SplitMix-style seed streams. Seeds are never re-drawn."""

from __future__ import annotations

MASK64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15
MUL1 = 0xBF58476D1CE4E5B9
MUL2 = 0x94D049BB133111EB


def splitmix64(x: int) -> int:
    z = (int(x) + GOLDEN) & MASK64
    z = ((z ^ (z >> 30)) * MUL1) & MASK64
    z = ((z ^ (z >> 27)) * MUL2) & MASK64
    return z ^ (z >> 31)


def derive_u64(base: int, tag: int) -> int:
    """Deterministic 64-bit child of (base, tag). Never re-drawn."""
    return splitmix64((int(base) ^ ((int(tag) * GOLDEN) & MASK64)) & MASK64)


class SplitMixStream:
    """Write-once sequential stream from a frozen seed."""

    def __init__(self, seed: int) -> None:
        self._state = int(seed) & MASK64
        self.n_drawn = 0

    def next_u64(self) -> int:
        self._state = (self._state + GOLDEN) & MASK64
        self.n_drawn += 1
        return splitmix64(self._state)

    def next_mod(self, modulus: int) -> int:
        if modulus <= 0:
            raise ValueError("modulus must be positive")
        # Rejection-free when modulus is a power of two; otherwise rejection.
        if (modulus & (modulus - 1)) == 0:
            return self.next_u64() & (modulus - 1)
        limit = (MASK64 // modulus) * modulus
        while True:
            v = self.next_u64()
            if v < limit:
                return v % modulus
