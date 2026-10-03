"""Semaev chained system (5) for t = 3 over F_{2^n}: variables u_0..u_{n-1} (u = sum u_i t^i),
x1_j, x2_j, x3_j (X_r = sum x_{r,j} v_j), j < k.  Equations: coordinates of S3(u,X1,X2) and S3(u,X3,z).
usage: gen3.py n k count seed basis(poly|rand) want(unsat|sat|any) outdir"""
import sys, random, json, os, subprocess
from gf2n import Field, find_modulus
from s3sys import Subspace, poly_basis, random_basis, write_system
n, k, count, seed = map(int, sys.argv[1:5]); basis, want, outdir = sys.argv[5:8]
os.makedirs(outdir, exist_ok=True); rng = random.Random(seed); F = Field(n, find_modulus(n))
U = [(1 << i, 1 << i) for i in range(n)]            # (variable bit, field element t^i)
def X(r, Vb): return [(1 << (n + r * k + j), Vb[j]) for j in range(k)]
def descent(Vb, z, a6):
    coef = {}
    def add(m, c):
        if c: coef[m] = coef.get(m, 0) ^ c
    sqv = lambda L: [(m, F.sq(c)) for m, c in L]      # X^2 = sum x v^2 (Boolean)
    def bil(A, B, scale=1):
        for ma, ca in A:
            for mb, cb in B: add(ma | mb, F.mul(scale, F.mul(ca, cb)))
    X1, X2, X3 = X(0, Vb), X(1, Vb), X(2, Vb)
    # S3(u,X1,X2) = u^2X1^2 + u^2X2^2 + X1^2X2^2 + u X1 X2 + a6
    e1 = {}
    coef = e1
    bil(sqv(U), sqv(X1)); bil(sqv(U), sqv(X2)); bil(sqv(X1), sqv(X2))
    for mu, cu in U:
        for m1, c1 in X1:
            for m2, c2 in X2: add(mu | m1 | m2, F.mul(cu, F.mul(c1, c2)))
    add(0, a6)
    # S3(u,X3,z) = u^2X3^2 + u^2 z^2 + X3^2 z^2 + u X3 z + a6
    e2 = {}
    coef = e2
    bil(sqv(U), sqv(X3)); 
    for mu, cu in sqv(U): add(mu, F.mul(cu, F.sq(z)))
    for mx, cx in sqv(X3): add(mx, F.mul(cx, F.sq(z)))
    bil(U, X3, z); add(0, a6)
    polys = []
    for e in (e1, e2):
        for b in range(n): polys.append(sorted(m for m, c in e.items() if (c >> b) & 1))
    return polys
meta = []; got = 0; tries = 0
while got < count:
    tries += 1
    a6 = rng.randrange(1, 1 << n); a2 = rng.randrange(2)
    Vb = poly_basis(F, k) if basis == 'poly' else random_basis(F, k, rng)
    z = rng.randrange(1, 1 << n)
    s = int(subprocess.check_output(['./s3c3count', str(n), format(F.f, 'x'), format(z, 'x'), format(a6, 'x'), str(k)] + [format(b, 'x') for b in Vb]))
    if (want == 'unsat' and s) or (want == 'sat' and not s): continue
    name = f"{outdir}/c3_n{n}_k{k}_{basis}_{seed}_{got}.sys"
    with open(name, 'w') as fh: write_system(descent(Vb, z, a6), n + 3 * k, fh)
    meta.append(dict(file=name, n=n, k=k, f=F.f, a2=a2, a6=a6, z=z, basis=Vb, nsol=s, t=3)); got += 1
json.dump(meta, open(f"{outdir}/meta_c3_n{n}_k{k}_{basis}_{seed}_{want}.json", 'w'))
print('generated', count, 'tries', tries)
