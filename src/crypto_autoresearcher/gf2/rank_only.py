"""Rank-profile-only GF(2) solver — a *new instrument*, not a drop-in for
``column_pass``.

Most CERTBIN questions (is 1 in M_D, rank, dimensions by degree) need the
pivot-column set, not the full op log. This module answers those with a
sparse / hybrid elimination that:

* drops rows that reduce to zero instead of carrying them as dense words;
* records its own checkable certificate (pivot rows + sparse combination
  of original rows), not the dense op log;
* is required to match the dense column-major solver on ``rank`` and
  ``pivcols`` (same pivot rule: smallest remaining row index with a 1 in
  the current column).

It deliberately does **not** claim bit-identical op logs or final matrices.
Experiments that need those must keep ``kernels.column_pass``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import kernels, reference


# When a sparse row's support exceeds this many columns, densify the remainder
# and finish with the dense blocked pass (keep_ops=False). Measured crossover
# on CERTBIN-shaped random systems: past ~256 ones a sorted-list XOR loses to
# a packed word XOR.
DENSE_NNZ = int(__import__("os").environ.get("CRYPTO_AR_GF2_RANK_DENSE_NNZ", "256"))
# Pure-Python sparse GE is the correctness scaffold for the new instrument.
# Past this many packed words ``auto`` uses the dense blocked pass (already
# 3-5x from the OpenMP work). Force ``algorithm="sparse"`` to exercise the
# sparse path; a native sparse kernel is the next speed step.
SPARSE_MAX_WORDS = int(__import__("os").environ.get("CRYPTO_AR_GF2_RANK_SPARSE_MAX_WORDS", "4096"))


@dataclass(frozen=True)
class RankCertificate:
    """Checkable rank certificate for this instrument.

    ``pivot_rows[k]`` is the (post-permutation) row that produced
    ``pivcols[k]``. ``comb[k]`` is the sorted list of *original* row indices
    whose XOR equals the pivot row at the moment it was chosen — enough to
    re-derive the pivot column set from the input matrix without trusting
    the solver's internal state.
    """

    pivcols: tuple[int, ...]
    pivot_rows: tuple[int, ...]
    comb: tuple[tuple[int, ...], ...]

    def to_json(self) -> dict:
        return {
            "instrument": "gf2.rank_only",
            "pivcols": list(self.pivcols),
            "pivot_rows": list(self.pivot_rows),
            "comb": [list(c) for c in self.comb],
        }


@dataclass(frozen=True)
class RankResult:
    rank: int
    pivcols: tuple[int, ...]
    pivot_rows: tuple[int, ...]
    ops_xor: int
    certificate: RankCertificate | None
    backend: str  # "sparse" | "sparse_then_dense" | "dense" | "reference"


def _row_support(row: np.ndarray, C: int) -> list[int]:
    """Sorted column indices of the 1-bits in a packed uint64 row."""
    out: list[int] = []
    for w, word in enumerate(row.tolist()):
        x = int(word)
        base = w * 64
        while x:
            b = (x & -x).bit_length() - 1
            c = base + b
            if c < C:
                out.append(c)
            x &= x - 1
    return out


def _xor_sorted(a: list[int], b: list[int]) -> list[int]:
    """Symmetric difference of two ascending column lists."""
    i = j = 0
    out: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        elif a[i] < b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    if i < len(a):
        out.extend(a[i:])
    if j < len(b):
        out.extend(b[j:])
    return out


def _sparse_rank(M: np.ndarray, C: int, want_cert: bool) -> RankResult | None:
    """Pure-Python sparse GE. Returns None if the matrix densifies past the
    threshold before finishing (caller falls back to dense)."""
    R = M.shape[0]
    rows: list[list[int] | None] = [_row_support(M[r], C) for r in range(R)]
    # comb[r]: original rows XORed into the current content of rows[r]
    comb: list[list[int] | None] = [[r] for r in range(R)] if want_cert else None
    # bucket: lead column -> list of active row indices
    buckets: dict[int, list[int]] = {}
    for r, cols in enumerate(rows):
        if cols:
            buckets.setdefault(cols[0], []).append(r)

    pivcols: list[int] = []
    pivot_rows: list[int] = []
    cert_combs: list[tuple[int, ...]] = []
    ops = 0
    densified = False

    for c in range(C):
        cand = buckets.pop(c, None)
        if not cand:
            continue
        # Same pivot rule as the dense column pass: smallest row index.
        cand.sort()
        live = []
        for r in cand:
            cols = rows[r]
            if cols is None or not cols or cols[0] != c:
                continue
            live.append(r)
        if not live:
            continue
        p = live[0]
        pivcols.append(c)
        pivot_rows.append(p)
        prow = rows[p]
        assert prow is not None and prow[0] == c
        pcomb = tuple(comb[p]) if want_cert else ()  # type: ignore[index]
        if want_cert:
            cert_combs.append(pcomb)
        rows[p] = None  # consumed as pivot
        if want_cert:
            comb[p] = None  # type: ignore[index]
        for r in live[1:]:
            new = _xor_sorted(rows[r], prow)  # type: ignore[arg-type]
            ops += 1
            if want_cert:
                comb[r] = _xor_sorted(comb[r], list(pcomb))  # type: ignore[index]
            if not new:
                rows[r] = None
                if want_cert:
                    comb[r] = None  # type: ignore[index]
                continue
            if len(new) > DENSE_NNZ:
                densified = True
                break
            rows[r] = new
            buckets.setdefault(new[0], []).append(r)
        if densified:
            break

    if densified:
        return None

    cert = None
    if want_cert:
        cert = RankCertificate(
            pivcols=tuple(pivcols),
            pivot_rows=tuple(pivot_rows),
            comb=tuple(cert_combs),
        )
    return RankResult(
        rank=len(pivcols),
        pivcols=tuple(pivcols),
        pivot_rows=tuple(pivot_rows),
        ops_xor=ops,
        certificate=cert,
        backend="sparse",
    )


def _dense_rank(M: np.ndarray, C: int, want_cert: bool) -> RankResult:
    """Finish with the dense column pass (no op-log X sets). Pivot rows come
    from the log; combination certificates are not rebuilt here — callers that
    need them must stay on the sparse path or call ``verify_certificate`` on a
    sparse result."""
    Mc = M.copy()
    log = kernels.column_pass(Mc, C, keep_ops=False, algorithm="auto", threads=None)
    pivcols = tuple(int(x) for x in log.cs.tolist())
    pivot_rows = tuple(int(x) for x in log.ps.tolist())
    cert = None
    if want_cert:
        # Dense path: certificate is the pivot set alone; combination vectors
        # would require keep_ops=True (the old instrument). Mark comb empty so
        # verify_certificate refuses rather than silently passing.
        cert = RankCertificate(pivcols=pivcols, pivot_rows=pivot_rows, comb=tuple())
    return RankResult(
        rank=int(log.K),
        pivcols=pivcols,
        pivot_rows=pivot_rows,
        ops_xor=int(log.ops_strict),
        certificate=cert,
        backend="dense",
    )


def rank_profile(M: np.ndarray, C: int, *, want_cert: bool = True,
                 algorithm: str = "auto") -> RankResult:
    """Compute rank and pivot columns of packed GF(2) matrix ``M``.

    ``algorithm``:
      * ``"sparse"`` — sparse GE only; raises if densification threshold hits;
      * ``"dense"`` — dense ``column_pass(keep_ops=False)``;
      * ``"auto"`` (default) — sparse, falling back to dense on densification.

    ``M`` is not modified. Output ``pivcols`` must equal the dense column-major
    solver's (tested).
    """
    kernels._need(M, np.uint64, "M")
    if algorithm not in ("auto", "sparse", "dense"):
        raise ValueError(f"unknown algorithm {algorithm!r}")
    if algorithm == "dense":
        return _dense_rank(M, C, want_cert)
    if algorithm == "auto" and M.size > SPARSE_MAX_WORDS:
        return _dense_rank(M, C, want_cert)
    sparse = _sparse_rank(M, C, want_cert)
    if sparse is not None:
        return sparse
    if algorithm == "sparse":
        raise RuntimeError(
            f"sparse rank densified past CRYPTO_AR_GF2_RANK_DENSE_NNZ={DENSE_NNZ}"
        )
    # Hybrid: start over on a copy with the dense engine. (A true mid-stream
    # handoff is a later optimisation; correctness first.)
    out = _dense_rank(M, C, want_cert)
    return RankResult(
        rank=out.rank,
        pivcols=out.pivcols,
        pivot_rows=out.pivot_rows,
        ops_xor=out.ops_xor,
        certificate=out.certificate,
        backend="sparse_then_dense",
    )


# Bound the advanced-indexing gather; the accumulator and reduction workspace
# each hold only the checked prefix. Small combinations avoid batching overhead.
_CERT_BATCH_BYTES = 1 << 20
_CERT_BATCH_ROWS = 256
_CERT_BATCH_MIN_ROWS = 8


def _certificate_prefix(M: np.ndarray, rows: tuple[int, ...], words: int) -> np.ndarray:
    """XOR a validated combination through the word containing its pivot.

    Later words cannot affect the leading-column assertion. Duplicate source
    rows deliberately remain in the reduction: their contributions cancel.
    """
    acc = np.zeros(words, dtype=np.uint64)
    if len(rows) < _CERT_BATCH_MIN_ROWS or acc.nbytes > _CERT_BATCH_BYTES:
        for r in rows:
            acc ^= M[r, :words]
        return acc
    batch_rows = min(_CERT_BATCH_ROWS, max(1, _CERT_BATCH_BYTES // acc.nbytes))
    reduced = np.empty_like(acc)
    for start in range(0, len(rows), batch_rows):
        indices = np.asarray(rows[start:start + batch_rows], dtype=np.intp)
        block = M[indices, :words]
        np.bitwise_xor.reduce(block, axis=0, out=reduced)
        acc ^= reduced
    return acc


def verify_certificate(M: np.ndarray, C: int, cert: RankCertificate) -> bool:
    """Recompute each claimed pivot row from ``cert.comb`` and check that its
    leading 1 sits at ``cert.pivcols[k]`` and that earlier pivots are already
    eliminated from it. Refuses empty ``comb`` (dense-path placeholder).

    Reconstructs only the prefix needed for that assertion, using bounded
    batched XOR for longer combinations. This verifies the supplied independent
    rows; it does not prove that they span every row of ``M``.
    """
    if not cert.comb:
        return False
    if len(cert.comb) != len(cert.pivcols):
        return False
    seen = set()
    for c, rows in zip(cert.pivcols, cert.comb):
        if not rows or c in seen or c < 0 or c >= C:
            return False
        words = (c >> 6) + 1
        if len(rows) < _CERT_BATCH_MIN_ROWS or words * 8 > _CERT_BATCH_BYTES:
            # Preserve the low-overhead scalar path for short combinations.
            # For a few rows, constructing prefix views costs more than the
            # avoided XORs on typical small matrices. Keep the original loop.
            acc = np.zeros(M.shape[1], dtype=np.uint64)
            for r in rows:
                if r < 0 or r >= M.shape[0]:
                    return False
                acc ^= M[r]
        else:
            for r in rows:
                # Advanced indexing casts to intp; never truncate floats or
                # reinterpret booleans as row numbers during that conversion.
                if type(r) is not int and (
                    not isinstance(r, (int, np.integer)) or isinstance(r, bool)
                ):
                    return False
                if r < 0 or r >= M.shape[0]:
                    return False
            acc = _certificate_prefix(M, rows, words)
        # Leading bit must be c; bits left of c must be 0.
        if words > 1 and np.any(acc[:words - 1]):
            return False
        word = int(acc[words - 1])
        low = c & 63
        if (word & ((1 << low) - 1)) != 0:
            return False
        if ((word >> low) & 1) != 1:
            return False
        seen.add(c)
    return True


def macaulay_rank(eqs, nv: int, D: int, neq: int, *, want_cert: bool = True,
                  algorithm: str = "auto") -> dict:
    """Rank-profile of M_D for quadratic eqs — the common CERTBIN question.

    Returns a record with ``rank``, ``one`` (constant column is a pivot),
    ``dims_by_deg``, ``pivcols``, ``instrument: gf2.rank_only``, and optional
    ``certificate``. Does not produce an op-log certificate.
    """
    from .closure import Closure

    cl = Closure(nv, D, neq)
    M = cl.build_M(eqs)
    res = rank_profile(M, cl.C, want_cert=want_cert, algorithm=algorithm)
    leads = np.array(res.pivcols, dtype=np.int64)
    one = bool(cl.const_col in res.pivcols)
    out = {
        "instrument": "gf2.rank_only",
        "backend": res.backend,
        "rank": res.rank,
        "one": one,
        "pivcols": list(res.pivcols),
        "dims_by_deg": [int((cl.col_deg[leads] <= d).sum()) if leads.size else 0
                        for d in range(D + 1)],
        "ops_xor": res.ops_xor,
    }
    if want_cert and res.certificate is not None:
        out["certificate"] = res.certificate.to_json()
        if res.certificate.comb:
            out["certificate_ok"] = verify_certificate(M, cl.C, res.certificate)
    return out


def dense_reference_pivcols(M: np.ndarray, C: int) -> tuple[int, ...]:
    """Pivot columns of the numpy reference column pass (for tests)."""
    Mc = M.copy()
    _ps, cs, _Xs, _tot = reference.column_pass(Mc, C, keep_ops=False)
    return tuple(int(x) for x in cs)
