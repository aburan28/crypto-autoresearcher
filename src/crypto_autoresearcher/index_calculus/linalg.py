"""Incremental sparse Gaussian elimination modulo a prime N.

Each relation is  sum_i c_i L_i + c_k k = r  (mod N), with L_i the unknown
logarithms of factor-base elements and k the target logarithm.  Rows are
reduced as they arrive against the pivots found so far, in pivot-creation
order; a pivot row only ever contains columns that had no pivot when it was
created, so one pass in creation order clears every pivoted column.  A row
left with no L-column determines k as soon as its k-coefficient is non-zero,
so linear algebra stops at the first relation that pins k down.

Where it stops is a property of the rows received, not of how they are
eliminated, so the pivot rule changes the cost (``ops``) and nothing else:
the same relation stops the run and the same k comes out.

Pivot rules
-----------
``min_fill`` (the default) pivots a new row on the column that the fewest
stored pivot rows contain, then on the one that has appeared least often,
then on the lowest index.  A later row is reduced by a pivot row whenever it
holds that pivot's column, directly or through fill, so a column that pivot
rows rarely carry is one that later rows rarely need cleared.  ``min_index``
pivots on the lowest column index.  It is the rule the ``la_ops`` of every
run before this rule existed were counted with, and it reproduces them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PIVOT_RULES = ("min_fill", "min_index")


@dataclass
class EliminationState:
    N: int
    pivot: str = "min_fill"
    pivots: dict[int, tuple[dict[int, int], int, int]] = field(default_factory=dict)
    order: list[int] = field(default_factory=list)
    ops: int = 0  # modular multiply-adds
    in_pivot_rows: dict[int, int] = field(default_factory=dict, repr=False)
    seen: dict[int, int] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self.pivot not in PIVOT_RULES:
            raise ValueError(f"unknown pivot rule {self.pivot!r}; choose from {PIVOT_RULES}")

    def add_row(self, coeffs: dict[int, int], kcoef: int, rhs: int) -> int | None:
        """Insert one relation; return k if it is now determined."""
        N = self.N
        row = {c: v % N for c, v in coeffs.items() if v % N}
        for c in row:
            self.seen[c] = self.seen.get(c, 0) + 1
        kcoef %= N
        rhs %= N
        for c in self.order:
            v = row.get(c)
            if not v:
                continue
            prow, pk, pr = self.pivots[c]
            for cc, pv in prow.items():
                nv = (row.get(cc, 0) - v * pv) % N
                if nv:
                    row[cc] = nv
                else:
                    row.pop(cc, None)
            kcoef = (kcoef - v * pk) % N
            rhs = (rhs - v * pr) % N
            self.ops += len(prow) + 2
        if row:
            c = self._choose(row)
            inv = pow(row[c], -1, N)
            prow = {cc: vv * inv % N for cc, vv in row.items()}
            self.pivots[c] = (prow, kcoef * inv % N, rhs * inv % N)
            self.order.append(c)
            for cc in prow:
                self.in_pivot_rows[cc] = self.in_pivot_rows.get(cc, 0) + 1
            self.ops += len(row) + 2
            return None
        if kcoef:
            return rhs * pow(kcoef, -1, N) % N
        return None  # dependent relation

    def _choose(self, row: dict[int, int]) -> int:
        if self.pivot == "min_index":
            return min(row)
        fill, seen = self.in_pivot_rows, self.seen
        return min(row, key=lambda c: (fill.get(c, 0), seen[c], c))

    @property
    def rank(self) -> int:
        return len(self.order)
