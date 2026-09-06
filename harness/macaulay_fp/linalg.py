"""Exact row echelon over F_p with Python integers (no floating point, no CAS).

Two backends behind one interface:

* ``p == 2``  rows are Python-int bitsets, pivot = highest set bit.  This is
  macaulay.py's ``GF2Basis`` ported unchanged (same pivot rule, same XOR loop),
  so p = 2 results are bit-for-bit the Boolean meter's.
* ``p > 2``   rows are ``dict[column, residue]``, pivot = highest column,
  pivot rows normalised to leading coefficient 1, incoming rows reduced by
  ``row -= row[pivot] * pivot_row (mod p)``.  Python ints give word-size
  arithmetic below 2^62 and arbitrary precision above it transparently, so the
  P-256 prime needs no special path.

Column convention.  Callers index columns so that TOP-degree columns carry the
HIGHEST indices.  Because the pivot is always the highest column of a row, the
echelon rows whose pivot lies in the top block are independent after projection
to the top block, and the echelon rows whose pivot lies below it have ZERO top
projection.  Hence one elimination yields, exactly,

    full_rank = number of echelon rows
    top_rank  = number of echelon rows with pivot in the top block
    fall_dim  = full_rank - top_rank
              = number of echelon rows with pivot below the top block,

and those latter rows form a basis of the FALL SPACE
``{v in rowspace : top(v) = 0}`` (their lower-degree content).  The Boolean meter
computed ``rank(M_D) - rank(H_D)`` with two eliminations; the identity above is
verified against that two-elimination route in the test-suite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

Row = object  # int bitset (p == 2) or dict[int, int] (p > 2)


@dataclass
class EchelonStats:
    rank: int = 0
    inserted_rows: int = 0
    zero_rows: int = 0
    reduction_ops: int = 0  # XORs at p = 2; row-axpy operations at p > 2


class Echelon:
    """Incremental exact row echelon over F_p (dependency-free)."""

    __slots__ = ("p", "pivots", "stats", "top_start")

    def __init__(self, p: int, top_start: Optional[int] = None) -> None:
        """``top_start``: first column index of the top block (None = no block)."""
        self.p = int(p)
        self.pivots: Dict[int, Row] = {}
        self.stats = EchelonStats()
        self.top_start = top_start

    # ----- construction helpers ------------------------------------------
    def encode(self, entries: Dict[int, int]) -> Row:
        """Turn ``{column: residue}`` into the backend row type."""
        p = self.p
        if p == 2:
            r = 0
            for col, c in entries.items():
                if c % 2:
                    r ^= 1 << col
            return r
        return {col: c % p for col, c in entries.items() if c % p}

    @property
    def rank(self) -> int:
        return len(self.pivots)

    # ----- reduction ------------------------------------------------------
    def reduce(self, row: Row) -> Row:
        """Fully reduce ``row`` against the current pivots (does not insert)."""
        p = self.p
        if p == 2:
            x = int(row)
            while x:
                lead = x.bit_length() - 1
                prow = self.pivots.get(lead)
                if prow is None:
                    return x
                x ^= prow
                self.stats.reduction_ops += 1
            return 0
        r: Dict[int, int] = dict(row)
        while r:
            lead = max(r)
            prow = self.pivots.get(lead)
            if prow is None:
                return r
            f = r[lead]  # pivot rows are normalised, so subtract f * prow
            for col, c in prow.items():
                v = (r.get(col, 0) - f * c) % p
                if v:
                    r[col] = v
                else:
                    r.pop(col, None)
            self.stats.reduction_ops += 1
        return r

    def add(self, row: Row) -> bool:
        """Insert a row; return True iff it increased the rank."""
        r = self.reduce(row)
        if self.p == 2:
            if r == 0:
                self.stats.zero_rows += 1
                return False
            lead = r.bit_length() - 1
            self.pivots[lead] = r
        else:
            if not r:
                self.stats.zero_rows += 1
                return False
            lead = max(r)
            inv = pow(r[lead], -1, self.p)
            self.pivots[lead] = {col: (c * inv) % self.p for col, c in r.items()}
        self.stats.inserted_rows += 1
        self.stats.rank = len(self.pivots)
        return True

    def extend(self, rows: Iterable[Row]) -> EchelonStats:
        for row in rows:
            self.add(row)
        self.stats.rank = len(self.pivots)
        return self.stats

    def contains(self, row: Row) -> bool:
        """Membership of ``row`` in the current row space."""
        r = self.reduce(row)
        return (r == 0) if self.p == 2 else (not r)

    # ----- block queries ---------------------------------------------------
    def top_rank(self) -> int:
        if self.top_start is None:
            raise ValueError("no top block declared")
        return sum(1 for lead in self.pivots if lead >= self.top_start)

    def fall_rows(self) -> List[Row]:
        """Echelon rows with pivot below the top block: a basis of the fall space."""
        if self.top_start is None:
            raise ValueError("no top block declared")
        return [self.pivots[lead] for lead in sorted(self.pivots) if lead < self.top_start]

    def basis_rows(self) -> List[Row]:
        return [self.pivots[lead] for lead in sorted(self.pivots)]


def rank_of(p: int, rows: Iterable[Row]) -> int:
    e = Echelon(p)
    e.extend(rows)
    return e.rank


def project_top(p: int, row: Row, top_mask: int, top_start: int) -> Row:
    """Restrict a row to the top block (independent route to top_rank for tests)."""
    if p == 2:
        return int(row) & top_mask
    return {col: c for col, c in row.items() if col >= top_start}


def row_to_dict(p: int, row: Row) -> Dict[int, int]:
    if p == 2:
        x = int(row)
        out = {}
        while x:
            lead = x.bit_length() - 1
            out[lead] = 1
            x ^= 1 << lead
        return out
    return dict(row)
