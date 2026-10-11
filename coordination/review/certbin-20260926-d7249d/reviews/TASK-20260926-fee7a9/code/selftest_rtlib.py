"""Self-tests of rtlib19 (own code). Seed 777 for random tests (my own; not a frozen seed)."""
import sys, json, random, time
sys.path.insert(0, sys.argv[1])
import numpy as np
from rtlib19 import *
random.seed(777)
out = {}
# 1 field
MODI = MOD19
# irreducibility: t^(2^19) == t and gcd(t^(2^i)-t, f)=1 for i=1..9 via polynomial gcd
def pgcd(a, b):
    while b:
        while a and a.bit_length() >= b.bit_length():
            a ^= b << (a.bit_length() - b.bit_length())
        a, b = b, a
    return a
x = 2
for i in range(19):
    x = fmul(x, x)
ok_frob = (x == 2)
ok_gcd = True
y = 2
for i in range(1, 10):
    y = fmul(y, y)
    if pgcd(MODI, y ^ 2) != 1:
        ok_gcd = False
out['field_irreducible'] = ok_frob and ok_gcd
ok = True
for _ in range(2000):
    a, b, c = (random.randrange(1 << 19) for _ in range(3))
    if fmul(a, fmul(b, c)) != fmul(fmul(a, b), c) or fmul(a, b ^ c) != fmul(a, b) ^ fmul(a, c):
        ok = False
    if a and fmul(a, finv(a)) != 1:
        ok = False
out['field_axioms_2000'] = ok
out['tau'] = [ftr(1 << j) for j in range(19)]
# 2 descent vs direct evaluation
Bc = 306147
ok = True
for _ in range(20):
    xR = random.randrange(1024, 1 << 19)
    P = s3_descent(xR, Bc)
    for _ in range(50):
        u = random.randrange(1 << 20)
        v = s3_value(xR, Bc, u)
        for k in range(19):
            if eval_poly(P[k], u) != (v >> k & 1):
                ok = False
out['descent_vs_direct_1000'] = ok
# E codec roundtrip
P = s3_descent(123457, Bc)
out['codec_roundtrip'] = decode_E_hex(encode_E(P)) == P
# 3 small-system closure tests vs naive dense implementation
def naive_rank_rows(rows, C):
    # rows: list of 0/1 lists; own dense elimination on numpy (independent of Echelon)
    if not rows:
        return np.zeros((0, C), dtype=np.uint8)
    A = np.array(rows, dtype=np.uint8) % 2
    r = 0
    piv_cols = []
    for col in range(C - 1, -1, -1):
        nz = np.nonzero(A[r:, col])[0]
        if len(nz) == 0:
            continue
        p = r + nz[0]
        A[[r, p]] = A[[p, r]]
        mask = A[:, col].copy(); mask[r] = 0
        A[mask == 1] ^= A[r]
        piv_cols.append(col)
        r += 1
        if r == A.shape[0]:
            break
    return A[:r], piv_cols
def naive_W(polys, mono, D):
    C = mono.C
    def vec(masks):
        v = [0] * C
        for m in masks:
            v[mono.index[m]] ^= 1
        return v
    rows = []
    for mu in [m for m in mono.masks if bin(m).count('1') <= D - 2]:
        for f in polys:
            rows.append(vec(mul_masks({mu}, f)))
    basis, pc = naive_rank_rows(rows, C)
    dims = [len(pc)]
    while True:
        # basis elements of degree <= D-1: reduced rows whose pivot (highest) col has deg <= D-1
        low = [basis[i] for i, c in enumerate(pc) if mono.deg[c] <= D - 1]
        new = [list(b) for b in basis]
        for b in low:
            masks = {mono.masks[i] for i in np.nonzero(b)[0]}
            for j in range(mono.nv):
                new.append(vec(mul_masks({1 << j}, masks)))
        basis, pc = naive_rank_rows(new, C)
        dims.append(len(pc))
        if dims[-1] == dims[-2]:
            break
    one = 0 in pc
    return dims[:-1], one, len(pc)
mismatch = 0; tested = 0; deep = 0
for trial in range(300):
    nv = 6; D = random.choice([3, 4])
    mono = Mono(nv, D)
    neq = random.randint(3, 7)
    polys = []
    for k in range(neq):
        f = set()
        for m in mono.masks:
            if bin(m).count('1') <= 2 and random.random() < random.choice([0.15, 0.3, 0.5]):
                f.add(m)
        # sometimes add an affine equation to create falls
        polys.append(f)
    if trial % 3 == 0:
        polys.append({1 << random.randrange(nv), 1 << random.randrange(nv), 0} if random.random() < 0.5 else {1 << random.randrange(nv)})
    rec, E = literal_W(polys, mono, D)
    nd, none, nfin = naive_W(polys, mono, D)
    tested += 1
    if rec['dims'] != nd or rec['one'] != none or rec['final_dim'] != nfin:
        mismatch += 1
    if rec['iterations_to_fixpoint'] >= 2:
        deep += 1
    # soundness: every basis element vanishes on every solution
    sols = [u for u in range(1 << nv) if all(eval_poly(f, u) == 0 for f in polys)]
    for p, r in E.piv.items():
        for u in sols:
            if eval_poly(set(mono.masks_of(r)), u) != 0:
                mismatch += 1000
out['small_W_tests'] = {'tested': tested, 'mismatch': mismatch, 'fixpoint_ge2': deep}
# 4 quad kernel and substitution on real S_3 systems
ok_k = True; ok_s = True
for _ in range(10):
    xR = random.randrange(1024, 1 << 19)
    P = s3_descent(xR, Bc)
    K = quad_kernel(P)
    for c in K:
        ell = combo(P, c)
        if any(bin(m).count('1') == 2 for m in ell):
            ok_k = False
    if len(K) != 1:
        ok_k = False
    c = K[0]
    cexp = [ftr(fmul(1 << k, finv(fmul(xR, xR)))) for k in range(19)]
    if c != cexp:
        ok_k = False
    ell = combo(P, c)
    Ps, js, L, rel = substitute(P, ell)
    for _ in range(200):
        up = random.randrange(1 << 19)
        # extend
        u = 0
        for i in range(20):
            if i == js:
                continue
            ii = i if i < js else i - 1
            if up >> ii & 1:
                u |= 1 << i
        Lval = eval_poly(L, u)
        if Lval:
            u |= 1 << js
        if eval_poly(ell, u) != 0:
            ok_s = False
        for k in range(19):
            if eval_poly(Ps[k], up) != eval_poly(P[k], u):
                ok_s = False
out['quad_kernel_and_C-ELL_identity_10'] = ok_k
out['substitution_vs_direct_2000'] = ok_s
print(json.dumps(out))
json.dump(out, open(sys.argv[2], 'w'), indent=1)
