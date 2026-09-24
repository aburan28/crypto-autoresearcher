"""Incremental sparse Gaussian elimination modulo a prime N.

Each relation is  sum_i c_i L_i + c_k k = r  (mod N), with L_i the unknown
logarithms of factor-base elements and k the target logarithm.  Rows are
reduced as they arrive against the pivots found so far, in pivot-creation
order; a pivot row only ever contains columns that had no pivot when it was
created, so one pass in creation order clears every pivoted column.  A row
left with no L-column determines k as soon as its k-coefficient is non-zero,
so linear algebra stops at the first relation that pins k down.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EliminationState:
    N: int
    pivots: dict[int, tuple[dict[int, int], int, int]] = field(default_factory=dict)
    order: list[int] = field(default_factory=list)
    ops: int = 0  # modular multiply-adds

    def add_row(self, coeffs: dict[int, int], kcoef: int, rhs: int) -> int | None:
        """Insert one relation; return k if it is now determined."""
        N = self.N
        row = {c: v % N for c, v in coeffs.items() if v % N}
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
            c = min(row)
            inv = pow(row[c], -1, N)
            self.pivots[c] = ({cc: vv * inv % N for cc, vv in row.items()},
                              kcoef * inv % N, rhs * inv % N)
            self.order.append(c)
            self.ops += len(row) + 2
            return None
        if kcoef:
            return rhs * pow(kcoef, -1, N) % N
        return None  # dependent relation

    @property
    def rank(self) -> int:
        return len(self.order)
