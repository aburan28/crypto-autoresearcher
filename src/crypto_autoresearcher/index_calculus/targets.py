"""Charged fixed-base tables for repeated IC targets (public toy curves).

The table contains ``d * 2**(window*j) * P`` for each digit position.
Scalars are exact nonnegative integers below the declared limit: no order
reduction, change to the RNG, or reuse between independent solves is hidden
here. All table construction uses the caller's instrumented curve.
"""

from __future__ import annotations

from .curve import Curve, Point

TARGET_ENGINES = ("reference", "fixed_window")


class FixedBaseMultiplier:
    """Multiply one fixed point using a bounded, positional digit table."""

    def __init__(self, curve: Curve, point: Point, limit: int, window: int = 4):
        if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= 8:
            raise ValueError("target window must be an integer in [1, 8]")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("scalar limit must be a positive integer")
        self.curve = curve
        self.limit = limit
        self.window = window
        self.mask = (1 << window) - 1
        self.tables: list[list[Point]] = []
        remaining = limit - 1
        base = point
        while remaining:
            # The final position needs only the reachable leading digits.
            largest = min(self.mask, remaining)
            digits: list[Point] = [None, base]
            for _ in range(2, largest + 1):
                digits.append(curve.add(digits[-1], base))
            self.tables.append(digits)
            remaining >>= window
            if remaining:
                for _ in range(window):
                    base = curve.add(base, base)

    @property
    def entries(self) -> int:
        """Stored slots, including the zero digit at every position."""
        return sum(map(len, self.tables))

    @property
    def coordinate_bytes(self) -> int:
        """Packed affine-coordinate payload; excludes Python/container overhead."""
        width = (self.curve.p.bit_length() + 7) // 8
        return 2 * width * sum(point is not None for table in self.tables for point in table)

    def mul(self, scalar: int) -> Point:
        if isinstance(scalar, bool) or not isinstance(scalar, int) or not 0 <= scalar < self.limit:
            raise ValueError("scalar outside fixed-base table range")
        result = None
        position = 0
        while scalar:
            digit = scalar & self.mask
            if digit:
                result = self.curve.add(result, self.tables[position][digit])
            scalar >>= self.window
            position += 1
        return result
