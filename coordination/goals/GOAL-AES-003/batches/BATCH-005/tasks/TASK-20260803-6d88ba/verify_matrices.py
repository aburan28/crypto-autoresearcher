# TASK-20260803-6d88ba: independent GF(2^8) matrix verification.
# Written fresh for this task. Does NOT import or read BATCH-002's ref.py.
# Field: GF(2)[x]/(x^8+x^4+x^3+x+1) (AES modulus 0x11B), FIPS-197 Sec 4.2.
import json, itertools, sys

def mul(a, b):
    p = 0
    for _ in range(8):
        if b & 1: p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi: a ^= 0x1B
        b >>= 1
    return p

# sanity pins from FIPS-197 examples
assert mul(0x57, 0x83) == 0xC1, "xtime pin failed"
assert mul(0x57, 0x13) == 0xFE, "FIPS-197 4.2.1 pin failed"
assert mul(0x02, 0x87) == 0x15

def matmul(A, B):
    n = len(A)
    return [[ _xorsum(mul(A[i][k], B[k][j]) for k in range(n)) for j in range(n)] for i in range(n)]

def _xorsum(it):
    r = 0
    for v in it: r ^= v
    return r

def det_leibniz(M):
    # char 2: determinant = permanent = XOR-sum over permutations of products
    n = len(M); acc = 0
    for perm in itertools.permutations(range(n)):
        prod = 1
        for i in range(n): prod = mul(prod, M[i][perm[i]])
        acc ^= prod
    return acc

def inv_elem(a):
    if a == 0: raise ZeroDivisionError
    for b in range(1, 256):
        if mul(a, b) == 1: return b
    raise AssertionError

def rank_and_inverse(M):
    n = len(M)
    A = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(M)]
    rank = 0
    for col in range(n):
        piv = None
        for r in range(rank, n):
            if A[r][col]: piv = r; break
        if piv is None: continue
        A[rank], A[piv] = A[piv], A[rank]
        iv = inv_elem(A[rank][col])
        A[rank] = [mul(iv, v) for v in A[rank]]
        for r in range(n):
            if r != rank and A[r][col]:
                f = A[r][col]
                A[r] = [A[r][k] ^ mul(f, A[rank][k]) for k in range(2*n)]
        rank += 1
    inv = [row[n:] for row in A] if rank == n else None
    return rank, inv

src = json.load(open(sys.argv[1]))
out = {}
I4 = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
for name in ("AES_MC", "M0", "M1"):
    M = src[name]["rows"]
    rank, inv = rank_and_inverse(M)
    d = det_leibniz(M)
    fwd = matmul(M, inv) if inv else None
    bwd = matmul(inv, M) if inv else None
    zeros = [[i, j] for i in range(4) for j in range(4) if M[i][j] == 0]
    hexs = "".join("%02x" % M[i][j] for i in range(4) for j in range(4))
    out[name] = {
        "rows": M, "hex_rowmajor": hexs,
        "determinant_leibniz_GF256": d,
        "rank_GF256": rank,
        "non_singular": (rank == 4 and d != 0),
        "inverse": inv,
        "M_times_Minv": fwd, "Minv_times_M": bwd,
        "M_Minv_is_identity": fwd == I4,
        "Minv_M_is_identity": bwd == I4,
        "both_sided_inverse_verified": (fwd == I4 and bwd == I4),
        "zero_entries": zeros, "num_zero_entries": len(zeros),
        "agrees_with_BATCH002_determinant": d == src[name]["determinant"],
        "agrees_with_BATCH002_inverse": inv == src[name]["inverse"],
        "agrees_with_BATCH002_hex": hexs == src[name]["hex"],
    }
print(json.dumps(out, indent=1))
