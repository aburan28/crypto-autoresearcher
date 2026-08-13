#!/usr/bin/env python3
"""TASK-20260802-4500d4 -- independent GF(2^8) linear algebra.

Written from scratch for this task. It does NOT read BATCH-002's matrices.json;
the matrix is supplied as a 32-hex-character row-major string on the command
line and every derived quantity (rank, determinant, inverse, M*Minv) is computed
here. Field: GF(2^8) with the AES modulus x^8+x^4+x^3+x+1 (0x11b).

Determinant is computed two independent ways:
  (a) by the Leibniz formula over all 24 permutations of S_4 (char 2, so signs
      are irrelevant and the sum is an XOR of products), and
  (b) as the product of the pivots found during Gauss-Jordan elimination,
      corrected for the row swaps (in char 2 a swap does not change the sign, so
      no correction is needed).
Agreement of the two is reported explicitly.
"""
import json
import sys
from itertools import permutations


def mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def inv(a):
    if a == 0:
        raise ZeroDivisionError("no inverse of 0 in GF(2^8)")
    for x in range(1, 256):
        if mul(a, x) == 1:
            return x
    raise AssertionError("unreachable")


def matmul(A, B):
    return [[
        mul(A[i][0], B[0][j]) ^ mul(A[i][1], B[1][j]) ^
        mul(A[i][2], B[2][j]) ^ mul(A[i][3], B[3][j])
        for j in range(4)] for i in range(4)]


def det_leibniz(M):
    acc = 0
    for perm in permutations(range(4)):
        prod = 1
        for i, j in enumerate(perm):
            prod = mul(prod, M[i][j])
        acc ^= prod  # char 2: sign is irrelevant
    return acc


def gauss_jordan(M):
    """Return (rank, det_from_pivots, inverse_or_None, swap_count)."""
    n = 4
    A = [row[:] for row in M]
    I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    rank = 0
    detp = 1
    swaps = 0
    for col in range(n):
        piv = None
        for r in range(rank, n):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            detp = 0
            continue
        if piv != rank:
            A[piv], A[rank] = A[rank], A[piv]
            I[piv], I[rank] = I[rank], I[piv]
            swaps += 1
        p = A[rank][col]
        detp = mul(detp, p)
        pinv = inv(p)
        A[rank] = [mul(pinv, v) for v in A[rank]]
        I[rank] = [mul(pinv, v) for v in I[rank]]
        for r in range(n):
            if r != rank and A[r][col] != 0:
                f = A[r][col]
                A[r] = [A[r][k] ^ mul(f, A[rank][k]) for k in range(n)]
                I[r] = [I[r][k] ^ mul(f, I[rank][k]) for k in range(n)]
        rank += 1
    is_id = all(A[i][j] == (1 if i == j else 0) for i in range(n) for j in range(n))
    return rank, detp, (I if (rank == n and is_id) else None), swaps


def analyse(name, hexstr):
    b = bytes.fromhex(hexstr)
    assert len(b) == 16
    M = [[b[4 * r + c] for c in range(4)] for r in range(4)]
    rank, detp, Minv, swaps = gauss_jordan(M)
    dl = det_leibniz(M)
    out = {
        "name": name,
        "hex": hexstr,
        "rows": M,
        "field": "GF(2^8), modulus 0x11b (x^8+x^4+x^3+x+1)",
        "rank_over_GF256": rank,
        "determinant_leibniz": dl,
        "determinant_gauss_pivot_product": detp,
        "determinant_methods_agree": dl == detp,
        "determinant": dl,
        "non_singular": dl != 0 and rank == 4,
        "row_swaps_during_elimination": swaps,
        "inverse": Minv,
        "zero_entries": [[r, c] for r in range(4) for c in range(4) if M[r][c] == 0],
    }
    if Minv is not None:
        P = matmul(M, Minv)
        Q = matmul(Minv, M)
        out["M_times_Minv"] = P
        out["Minv_times_M"] = Q
        out["M_times_Minv_is_identity"] = P == [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        out["Minv_times_M_is_identity"] = Q == [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    out["is_MDS"] = False if out["zero_entries"] else None
    out["MDS_note"] = ("contains a zero entry, therefore NOT MDS; it is an "
                       "MDS-SUBSTITUTE: non-singular and column-preserving only"
                       ) if out["zero_entries"] else \
                      ("no zero entry; MDS-ness not tested here (only "
                       "non-singularity is)")
    return out


if __name__ == "__main__":
    res = [analyse(n, h) for n, h in (p.split("=") for p in sys.argv[1:])]
    print(json.dumps(res, indent=1))
