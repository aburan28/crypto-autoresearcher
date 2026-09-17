"""J2 (a)+(d): CONSTRUCT degenerate instances, EXERCISE the never-fired
degenerate instrument, and check N <= p^{n'-j} < p^{n'} on every one.
Read-only against the producer's implementation; the only mutation is adding
field polynomials for n the contract never used, to an in-memory dict copy."""
import sys, random, json
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-QSP-33b442/implementation")
import qspcore as Q
from qspcore import (KField, deg, poly_str, deg_D_and_degenerate, difference_poly_f2,
                     i1_brute_f2, i2_gcd_f2, i3_injection_f2, verify_roots_f2,
                     polymod, square, is_irreducible)

# extra irreducible field polynomials (verified below), for n the contract omits
EXTRA = {5:0b100101, 6:0b1000011, 8:0b100011011, 9:0b1000010001, 10:0b10000001001,
         14:0b100000000101011, 15:0b1000000000000011, 16:0b10001000000001011}
for n,f in EXTRA.items():
    assert deg(f)==n and is_irreducible(f), (n,f)
    Q.FIELD_POLY.setdefault(n, f)
print("extra field polys verified irreducible:", sorted(EXTRA))

rng = random.Random(20260917)

def admits(n, npr):
    q, r = divmod(n, npr)
    if n % (q+1): return None
    j = npr - n//(q+1)
    return (q, r, j) if j >= 1 else None

CELLS = [(4,3),(6,4),(6,5),(8,5),(8,6),(8,7),(9,4),(10,6),(10,7),(10,8),(10,9),
         (12,5),(12,7),(12,8),(12,9),(12,10),(12,11),(14,8),(14,9),(15,6),(15,7),
         (16,5),(6,3),(12,4),(12,6),(8,8),(9,9)]
rows=[]
for (n,npr) in CELLS:
    a = admits(n,npr)
    if a is None: print("SKIP (no degeneracy possible):",(n,npr)); continue
    q,r,j = a
    d = 1<<j
    if d >= (1<<npr): continue
    K = KField(n)
    lam = 1 << d                                  # lambda = X^{2^j}
    D = difference_poly_f2(lam, n, npr)
    degD, isdeg = deg_D_and_degenerate(lam, n, npr)
    i3 = i3_injection_f2(K, lam, npr, rng)
    # L == M^{2^j} with M = X^{2^{n'-j}} + X
    M = (1 << (1 << (npr-j))) ^ 0b10
    Mp = M
    for _ in range(j): Mp = square(Mp)
    L = (1 << (1 << npr)) ^ lam
    # independent brute distinct-root count (written here, no gcd, no ddf)
    cnt = 0
    for x in range(1<<n):
        a1 = x
        for _ in range(npr): a1 = polymod(square(a1), K.mod)
        b1 = x
        for _ in range(j): b1 = polymod(square(b1), K.mod)
        if a1 == b1: cnt += 1
    i1 = i1_brute_f2(K, lam, npr)[0]
    i2 = i2_gcd_f2(n, npr, lam)
    # theory: root set of M = F_{2^{n'-j}} cap K = F_{2^gcd(n'-j,n)}
    import math
    theo = 1 << math.gcd(npr-j, n)
    rows.append(dict(n=n,npr=npr,q=q,r=r,j=j,d=d,rzero=(r==0),
        D0=(D==0), flag=isdeg, i3deg=i3.get("degenerate"), LMp=(L==Mp),
        N=cnt, I1=i1, I2=i2, theo=theo, bnd=1<<(npr-j), pn=1<<npr))
hdr=("n","n'","q","r","j","d","D==0","degflag","i3deg","L=M^2j","N","2^(gcd)","2^(n'-j)","2^n'","N<=bnd","splits?")
print("\n%-3s %-3s %-2s %-2s %-2s %-4s %-6s %-8s %-7s %-7s %-6s %-8s %-9s %-7s %-7s %-6s"%hdr)
bad=[]
for x in rows:
    ok = x["N"]<=x["bnd"]; sp = (x["N"]==x["pn"])
    print("%-3d %-3d %-2d %-2d %-2d %-4d %-6s %-8s %-7s %-7s %-6d %-8d %-9d %-7d %-7s %-6s"%(
        x["n"],x["npr"],x["q"],x["r"],x["j"],x["d"],x["D0"],x["flag"],x["i3deg"],x["LMp"],
        x["N"],x["theo"],x["bnd"],x["pn"],ok,sp))
    if not (x["D0"] and x["flag"] and x["i3deg"] and x["LMp"] and ok and not sp
            and x["N"]==x["I1"]==x["I2"]==x["theo"]): bad.append(x)
print("\ncells exercised:",len(rows)," anomalies:",len(bad), bad)
print("instrument fired (D==0 detected) on ALL:", all(r["D0"] and r["flag"] and r["i3deg"] for r in rows))
print("N <= 2^{n'-j} on ALL:", all(r["N"]<=r["bnd"] for r in rows))
print("N == 2^{n'} (complete split) on ANY:", any(r["N"]==r["pn"] for r in rows))
print("bound 2^{n'-j} ATTAINED on:", [(r["n"],r["npr"]) for r in rows if r["N"]==r["bnd"]])
json.dump(rows, open("scratch/j2_construct_out.json","w"), indent=1)
