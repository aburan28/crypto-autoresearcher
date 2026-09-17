"""J4 (c): AN INDEPENDENT DETERMINATION OF N AT n = 131, the one thing the
producer's census never had.  Two independent routes, neither of which shares
a line with i3_injection_f2:

 R1  Proposition 2 of KN-LIT-4fe9d2 (via qspcore.c6_linearized_N): for
     LINEARIZED lambda over F_2, N = 2^{deg gcd(f, T^n - 1)}.
 R2  LINEAR ALGEBRA, written here from scratch: x -> x^{2^{n'}} + lin(x) is
     F_2-linear on K = F_2^131; build its 131x131 matrix over F_2 by images of
     the basis z^i and take the kernel dimension by Gaussian elimination.
     For AFFINE lambda = lin + b, solve the inhomogeneous system: N = 2^{dim ker}
     if b is in the image, else N = 0.

R2 reaches the FOUR AFFINE candidates that are INSIDE the Stage 3 census
(exact degree 4, X^4 + aX^2 + bX + 1), so this is an independent determination
on real census rows, not only on the excluded linearized slice."""
import sys, random, json
sys.path.insert(0,"/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
from qspcore import (KField, deg, poly_str, i3_injection_f2, c6_linearized_N,
                     is_linearized, is_affine, verify_roots_f2, difference_poly_f2)

N = 131
MOD = (1<<131)|(1<<13)|(1<<2)|(1<<1)|1

# --- R2: independent field arithmetic, written here (no qspcore primitive) ---
def fmod(a):
    while a.bit_length() > N:
        a ^= MOD << (a.bit_length()-1-N)
    return a
def fsq(a):
    r=0; i=0; x=a
    while x:
        if x&1: r |= 1<<(2*i)
        x >>= 1; i += 1
    return fmod(r)
def fpow2k(a,k):
    for _ in range(k): a = fsq(a)
    return a
def fmul(a,b):
    r=0
    while a:
        if a&1: r ^= b
        a >>= 1; b <<= 1
    return fmod(r)
def lam_eval_lin(lam, x):
    """lambda linearized/affine over F_2: sum over set bits i of lam of x^i,
    computed as repeated squaring for i a power of two; constant term separate."""
    r=0; i=0; l=lam
    while l:
        if l&1:
            if i==0: r ^= 1
            else:
                e = i.bit_length()-1
                assert 1<<e == i, "not a power of two exponent"
                r ^= fpow2k(x,e)
        l >>= 1; i += 1
    return r

def rref_kernel_and_solve(cols, rhs=None):
    """cols: list of N ints, column j = image of basis vector e_j, as a bitmask
    over rows.  Returns (dim ker, solvable(rhs))."""
    # build augmented system M x = rhs, M[i][j] = bit i of cols[j]
    rows = []
    for i in range(N):
        r = 0
        for j in range(N):
            if (cols[j] >> i) & 1: r |= 1 << j
        b = ((rhs >> i) & 1) if rhs is not None else 0
        rows.append((r, b))
    rank = 0; piv = []
    r_idx = 0
    for col in range(N):
        sel = None
        for i in range(r_idx, N):
            if (rows[i][0] >> col) & 1: sel = i; break
        if sel is None: continue
        rows[r_idx], rows[sel] = rows[sel], rows[r_idx]
        pr, pb = rows[r_idx]
        for i in range(N):
            if i != r_idx and ((rows[i][0] >> col) & 1):
                rows[i] = (rows[i][0] ^ pr, rows[i][1] ^ pb)
        piv.append(col); r_idx += 1; rank += 1
    inconsistent = any(rows[i][0] == 0 and rows[i][1] == 1 for i in range(N))
    return N - rank, (not inconsistent)

def linalg_N(lam, npr):
    lin = lam & ~1              # drop the constant term
    const = lam & 1
    cols = []
    for i in range(N):
        x = 1 << i
        cols.append(fpow2k(x, npr) ^ lam_eval_lin(lin, x))
    b = 1 if const else 0        # L(x) = x^{2^n'} + lin(x) + const  = 0  <=> Lx = const
    dimker, solvable = rref_kernel_and_solve(cols, b)
    return (1 << dimker) if solvable else 0, dimker, solvable

rng = random.Random(20260917)
K = KField(131)
rows=[]
CANDS = []
# linearized (EXCLUDED from the census -- the plan's named test)
for lam in [0b110,                 # X^2 + X
            0b10110,               # X^4 + X^2 + X
            0b10010,               # X^4 + X
            0b10100,               # X^4 + X^2
            0b100000010,           # X^8 + X
            0b100010010,           # X^8 + X^4 + X
            0b10000000000000010,   # X^16 + X
            (1<<64)|(1<<8)|0b10,   # X^64 + X^8 + X
            (1<<128)|(1<<2)|0b10]: # X^128 + X^2 + X
    CANDS.append(("linearized (outside census)", lam))
# affine, exact degree 4 -- INSIDE the Stage 3 census
for a in (0,1):
    for b in (0,1):
        lam = (1<<4) | (a<<2) | (b<<1) | 1
        CANDS.append(("affine (INSIDE census)", lam))

for npr in (33,44,66):
    for (tag, lam) in CANDS:
        d = lam.bit_length()-1
        if d >= (1<<npr): continue
        q = 131 // npr
        if d**(q+1) > 1000000:
            print("%-4d %-26s %-26s SKIPPED: deg D = %d > 10^6 (AMD-20260917-001 cap)"
                  % (npr, tag, poly_str(lam), d**(q+1)))
            continue
        la_N, dk, solv = linalg_N(lam, npr)
        c6 = c6_linearized_N(lam, npr, 131) if is_linearized(lam) else None
        D = difference_poly_f2(lam, 131, npr)
        res = i3_injection_f2(K, lam, npr, rng, want_roots=True)
        i3N = None if res.get("degenerate") else res["N"]
        ver = None
        if not res.get("degenerate") and res.get("root_orbits"):
            flat=[x for o in res["root_orbits"] for x in o]
            ver = verify_roots_f2(K, lam, npr, flat)["all_roots_verified"]
        rows.append(dict(npr=npr, tag=tag, lam=poly_str(lam), lam_bits=lam,
                         linalg_N=la_N, dim_ker=dk, solvable=solv,
                         c6_N=(c6[0] if c6 else None), c6_splits=(c6[2] if c6 else None),
                         I3_N=i3N, deg_D=res.get("deg_D"), slack=res.get("slack"),
                         verified=ver, agree=(la_N==i3N and (c6 is None or c6[0]==la_N))))
print("%-4s %-26s %-26s %-9s %-8s %-8s %-8s %-7s %-6s"%("n'","class","lambda","linalg N","C6 (P2)","I3 N","deg D","rootver","agree"))
for r in rows:
    print("%-4d %-26s %-26s %-9s %-8s %-8s %-8s %-7s %-6s"%(
        r["npr"], r["tag"], r["lam"], r["linalg_N"], r["c6_N"], r["I3_N"], r["deg_D"], r["verified"], r["agree"]))
print()
print("rows:", len(rows), " disagreements:", sum(1 for r in rows if not r["agree"]))
print("DISAGREEING:", [r for r in rows if not r["agree"]])
json.dump(rows, open("scratch/j4_n131_out.json","w"), indent=1)
