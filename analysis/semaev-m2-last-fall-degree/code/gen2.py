"""Generator v2: any n (even or odd); z either a curve x-coordinate ('curve') or uniform ('rand', as in Semaev 2015 Sec. 4.5.1).
usage: gen2.py n l count seed basis(poly|rand|tr0) want(unsat|sat|any) zmode(curve|rand) outdir"""
import sys, random, json, os, subprocess
from gf2n import Field, find_modulus
from s3sys import Subspace, poly_basis, random_basis, s3_descent, write_system, random_curve_point_x
n, l, count, seed = map(int, sys.argv[1:5]); basis, want, zmode, outdir = sys.argv[5:9]
os.makedirs(outdir, exist_ok=True)
rng = random.Random(seed); F = Field(n, find_modulus(n))
def tr0_basis():
    while True:
        B = []
        while len(B) < l:
            x = rng.randrange(1, 1 << n)
            if F.trace(x) == 0: B.append(x)
        try:
            Subspace(F, B); return B
        except AssertionError:
            pass
meta = []; k = 0; tries = 0
while k < count:
    tries += 1
    a6 = rng.randrange(1, 1 << n); a2 = rng.randrange(2)
    Vb = poly_basis(F, l) if basis == 'poly' else (tr0_basis() if basis == 'tr0' else random_basis(F, l, rng))
    xR = random_curve_point_x(F, a2, a6, rng) if zmode == 'curve' else rng.randrange(1, 1 << n)
    # skip trivially unsatisfiable draws: V inside ker Tr and Tr(a6/z^2) = 1 put 1 in span(F) (Thm 2.1(c))
    if all(F.trace(v) == 0 for v in Vb) and F.trace(F.mul(a6, F.inv(F.sq(xR)))) == 1:
        continue
    s = int(subprocess.check_output(['./s3count2', str(n), format(F.f, 'x'), format(xR, 'x'), format(a6, 'x'), str(l)] + [format(b, 'x') for b in Vb]))
    if (want == 'unsat' and s) or (want == 'sat' and not s):
        continue
    name = f"{outdir}/n{n}_l{l}_{basis}_{zmode}_{seed}_{k}.sys"
    with open(name, 'w') as fh:
        write_system(s3_descent(F, Subspace(F, Vb), xR, a6), 2 * l, fh)
    meta.append(dict(file=name, n=n, l=l, f=F.f, a2=a2, a6=a6, xR=xR, basis=Vb, nsol=s, zmode=zmode))
    k += 1
with open(f"{outdir}/meta_n{n}_l{l}_{basis}_{zmode}_{seed}_{want}.json", 'w') as fh:
    json.dump(meta, fh)
print('generated', count, 'tries', tries)
