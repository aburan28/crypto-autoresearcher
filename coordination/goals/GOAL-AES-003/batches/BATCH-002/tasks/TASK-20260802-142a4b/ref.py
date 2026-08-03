#!/usr/bin/env python3
"""Independent reference for TASK-20260802-142a4b.

Pure-Python AES-shaped SPN with a CONFIGURABLE GF(2^8) mixing matrix.
S-box is DERIVED here (GF(2^8) multiplicative inverse + FIPS-197 affine map),
not copied from the C engine, so the pin is a genuine cross-check.

Convention C1 (same as BATCH-001 count5 PREREGISTRATION section 1):
    s = P ^ RK[0]
    for i in 1..r-1:  s = ARK_i(M(SR(SB(s))))
    s = ARK_r(SR(SB(s)))          # final round, no mixing layer

Also: GF(2^8) matrix rank / inverse / determinant, and an MDS check.
"""
import sys, json

def xt(a):
    a <<= 1
    return (a ^ 0x1b) & 0xff if a & 0x100 else a

def gmul(a, b):
    p = 0
    while b:
        if b & 1: p ^= a
        a = xt(a); b >>= 1
    return p

def ginv(a):
    if a == 0: return 0
    for x in range(1, 256):
        if gmul(a, x) == 1: return x
    raise AssertionError

def rotl8(x, n): return ((x << n) | (x >> (8 - n))) & 0xff

SBOX = []
for a in range(256):
    b = ginv(a)
    SBOX.append(b ^ rotl8(b, 1) ^ rotl8(b, 2) ^ rotl8(b, 3) ^ rotl8(b, 4) ^ 0x63)

AES_MC = [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]]

def key_expand(key):
    w = [list(key[4*i:4*i+4]) for i in range(4)]
    rcon = 1
    for i in range(4, 44):
        t = list(w[i-1])
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[x] for x in t]
            t[0] ^= rcon
            rcon = xt(rcon)
        w.append([w[i-4][j] ^ t[j] for j in range(4)])
    return [bytes(b for word in w[4*r:4*r+4] for b in word) for r in range(11)]

def encrypt(pt, rk, r, M):
    s = [pt[i] ^ rk[0][i] for i in range(16)]   # state[4c+row]
    for rnd in range(1, r + 1):
        s = [SBOX[x] for x in s]
        # ShiftRows: new[row][col] = old[row][(col+row)%4]
        t = [0]*16
        for col in range(4):
            for row in range(4):
                t[4*col+row] = s[4*((col+row) % 4)+row]
        s = t
        if rnd != r:
            t = [0]*16
            for col in range(4):
                for row in range(4):
                    t[4*col+row] = 0
                    for k in range(4):
                        t[4*col+row] ^= gmul(M[row][k], s[4*col+k])
            s = t
        s = [s[i] ^ rk[rnd][i] for i in range(16)]
    return bytes(s)

def proj(c, j0):
    return sum(c[4*((j0-t) % 4)+t] << (8*t) for t in range(4))

# ---- GF(2^8) linear algebra ----
def mat_det_rank(M):
    """Gauss-Jordan over GF(2^8); returns (rank, det)."""
    A = [row[:] for row in M]
    n = 4
    det = 1
    for c in range(n):
        piv = None
        for r_ in range(c, n):
            if A[r_][c]: piv = r_; break
        if piv is None:
            return (sum(1 for r_ in range(n) if any(A[r_])), 0)
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            # row swap does not change det over char 2
        det = gmul(det, A[c][c])
        inv = ginv(A[c][c])
        A[c] = [gmul(inv, x) for x in A[c]]
        for r_ in range(n):
            if r_ != c and A[r_][c]:
                f = A[r_][c]
                A[r_] = [A[r_][k] ^ gmul(f, A[c][k]) for k in range(n)]
    return (4, det)

def mat_inverse(M):
    n = 4
    A = [M[r][:] + [1 if i == r else 0 for i in range(n)] for r in range(n)]
    for c in range(n):
        piv = None
        for r_ in range(c, n):
            if A[r_][c]: piv = r_; break
        if piv is None: return None
        A[c], A[piv] = A[piv], A[c]
        inv = ginv(A[c][c])
        A[c] = [gmul(inv, x) for x in A[c]]
        for r_ in range(n):
            if r_ != c and A[r_][c]:
                f = A[r_][c]
                A[r_] = [A[r_][k] ^ gmul(f, A[c][k]) for k in range(2*n)]
    return [row[n:] for row in A]

def mat_mul(A, B):
    return [[__import__('functools').reduce(lambda x, y: x ^ y,
             [gmul(A[i][k], B[k][j]) for k in range(4)]) for j in range(4)]
            for i in range(4)]

def is_mds(M):
    """MDS iff every square submatrix is non-singular."""
    from itertools import combinations
    for k in (1, 2, 3, 4):
        for rows in combinations(range(4), k):
            for cols in combinations(range(4), k):
                sub = [[M[r][c] for c in cols] for r in rows]
                if k == 1:
                    if sub[0][0] == 0: return False
                else:
                    S = [row[:] + [0]*(4-k) for row in sub]
                    for i in range(k, 4): S.append([0]*4)
                    for i in range(k, 4): S[i][i] = 1
                    if mat_det_rank(S)[1] == 0: return False
    return True

if __name__ == "__main__":
    print(json.dumps({"note": "import as a module"}))
