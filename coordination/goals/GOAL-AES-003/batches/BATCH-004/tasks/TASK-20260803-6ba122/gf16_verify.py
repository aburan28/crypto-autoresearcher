#!/usr/bin/env python3
"""TASK-20260803-6ba122 : independent Gauss-Jordan over GF(2^4), modulus x^4+x+1 (0x13).

Written from scratch for this task.  Does NOT import or reuse any campaign code.
For each candidate 4x4 mixing matrix it reports:
  determinant (computed TWICE by independent methods: Gaussian elimination with
  pivot-product, and the full 4! = 24-term Leibniz permutation expansion),
  rank, explicit inverse, and M*Minv AND Minv*M checked BOTH ways against I.
"""
import json, itertools, sys

MOD = 0x13  # x^4 + x + 1


def gmul(a, b):
    p = 0
    for _ in range(4):
        if b & 1:
            p ^= a
        hi = a & 8
        a = (a << 1) & 0xF
        if hi:
            a ^= (MOD & 0xF)   # 0x13 & 0xF = 0x3  => x^4 = x + 1
        b >>= 1
    return p


def ginv(a):
    if a == 0:
        raise ZeroDivisionError("no inverse of 0 in GF(2^4)")
    for z in range(1, 16):
        if gmul(a, z) == 1:
            return z
    raise ArithmeticError("field table broken: no inverse found for %d" % a)


def matmul(A, B):
    return [[
        _xorsum(gmul(A[i][k], B[k][j]) for k in range(4))
        for j in range(4)] for i in range(4)]


def _xorsum(it):
    v = 0
    for x in it:
        v ^= x
    return v


def det_leibniz(M):
    """Full 24-term permutation expansion.  In characteristic 2 the sign is
    irrelevant, so det = XOR over permutations of the product of entries."""
    tot = 0
    for perm in itertools.permutations(range(4)):
        prod = 1
        for i in range(4):
            prod = gmul(prod, M[i][perm[i]])
        tot ^= prod
    return tot


def gauss_jordan(M):
    """Returns (det_via_pivots, rank, inverse_or_None).  Independent of Leibniz."""
    A = [row[:] for row in M]
    I = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    det = 1
    rank = 0
    swaps = 0
    for c in range(4):
        p = -1
        for i in range(rank, 4):
            if A[i][c]:
                p = i
                break
        if p < 0:
            det = 0
            continue
        if p != rank:
            A[p], A[rank] = A[rank], A[p]
            I[p], I[rank] = I[rank], I[p]
            swaps += 1
        piv = A[rank][c]
        det = gmul(det, piv)
        iv = ginv(piv)
        A[rank] = [gmul(x, iv) for x in A[rank]]
        I[rank] = [gmul(x, iv) for x in I[rank]]
        for i in range(4):
            if i != rank and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][k] ^ gmul(f, A[rank][k]) for k in range(4)]
                I[i] = [I[i][k] ^ gmul(f, I[rank][k]) for k in range(4)]
        rank += 1
    # sign is +1 in characteristic 2, swaps recorded only for the record
    inv = I if rank == 4 else None
    return det, rank, inv, swaps


IDENT = [[1 if i == j else 0 for j in range(4)] for i in range(4)]


def report(name, M, note=""):
    d1, rank, inv, swaps = gauss_jordan(M)
    d2 = det_leibniz(M)
    out = {
        "name": name,
        "note": note,
        "rows": M,
        "field": "GF(2^4), modulus x^4+x+1 (0x13)",
        "determinant_gauss_pivot_product": d1,
        "determinant_leibniz_24_term": d2,
        "determinant_methods_agree": d1 == d2,
        "rank": rank,
        "non_singular": rank == 4 and d1 != 0,
        "zero_entries": [[i, j] for i in range(4) for j in range(4) if M[i][j] == 0],
        "n_zero_entries": sum(1 for i in range(4) for j in range(4) if M[i][j] == 0),
    }
    if inv is not None:
        MM = matmul(M, inv)
        MM2 = matmul(inv, M)
        out["inverse"] = inv
        out["M_times_Minv"] = MM
        out["Minv_times_M"] = MM2
        out["M_times_Minv_is_identity"] = (MM == IDENT)
        out["Minv_times_M_is_identity"] = (MM2 == IDENT)
        out["both_ways_verified"] = (MM == IDENT and MM2 == IDENT)
    else:
        out["inverse"] = None
        out["both_ways_verified"] = False
    # MDS check: every square submatrix non-singular  => equivalently no zero entry
    # and all 2x2/3x3/4x4 minors nonzero.  Reported for honesty, not used as a gate.
    mds = True
    for k in (1, 2, 3, 4):
        for rowsel in itertools.combinations(range(4), k):
            for colsel in itertools.combinations(range(4), k):
                sub = [[M[i][j] for j in colsel] for i in rowsel]
                if k == 1:
                    dd = sub[0][0]
                else:
                    dd = _minor_det(sub, k)
                if dd == 0:
                    mds = False
    out["is_MDS"] = mds
    return out


def _minor_det(sub, k):
    tot = 0
    for perm in itertools.permutations(range(k)):
        prod = 1
        for i in range(k):
            prod = gmul(prod, sub[i][perm[i]])
        tot ^= prod
    return tot


def circ(row):
    """Same construction as the campaign's nibble instrument: MCM[i][t] = row[(t-i) mod 4]."""
    return [[row[(t - i) % 4] for t in range(4)] for i in range(4)]


def main():
    res = {}
    res["field_sanity"] = {
        "gmul_2_times_9": gmul(2, 9),
        "inverse_table": {str(a): ginv(a) for a in range(1, 16)},
        "all_inverses_check": all(gmul(a, ginv(a)) == 1 for a in range(1, 16)),
    }

    cands = []
    # control: AES-shaped circulant, NO zero entry
    cands.append(("NZ", circ([2, 3, 1, 1]), "no-zero-entry control layer, AES-shaped circulant over GF(2^4)"))
    # the BATCH-001 validator's aborted substitute -- reproduced to confirm it IS singular
    cands.append(("BATCH001_ABORTED_CIRC_2301", circ([2, 3, 0, 1]),
                  "the BATCH-001 validator's substitute circulant that aborted; reproduced here to confirm the abort was correct"))
    # Z1: NZ with entry [0][0] zeroed -- the nibble analogue of GF(2^8) M0
    Z1 = circ([2, 3, 1, 1])
    Z1[0][0] = 0
    cands.append(("Z1", Z1, "nibble analogue of GF(2^8) M0: AES-shaped circulant with entry [0][0] set to 0 (ONE zero)"))
    # Z4: nibble analogue of GF(2^8) M1 -- zeros at (0,0),(1,3),(2,2),(3,1)
    Z4 = circ([2, 3, 1, 1])
    for (i, j) in [(0, 0), (1, 3), (2, 2), (3, 1)]:
        Z4[i][j] = 0
    cands.append(("Z4", Z4, "nibble analogue of GF(2^8) M1: zeros at (0,0),(1,3),(2,2),(3,1) (FOUR zeros)"))

    res["candidates"] = [report(n, M, note) for (n, M, note) in cands]

    # exhaustive fallback search over one-zero circulants, recorded regardless of need
    search = []
    for row in itertools.product(range(16), repeat=4):
        if sum(1 for x in row if x == 0) != 1:
            continue
        M = circ(list(row))
        d, rk, inv, _ = gauss_jordan(M)
        if rk == 4:
            search.append({"row": list(row), "det": d})
    res["one_zero_circulant_search"] = {
        "total_rows_with_exactly_one_zero": 4 * 15 ** 3,
        "non_singular_count": len(search),
        "first_10": search[:10],
    }
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
