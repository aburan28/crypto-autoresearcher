"""J6 (named breaking artifact 2): Proposition 7 of KN-LIT-4fe9d2 instantiated
IN FULL at integer m for n = 131, carrying m!, m^5.188 and 3^{kappa m^2} -- the
factors the m >> 1 asymptotic form of Proposition 8 drops."""
import math
n=131; kappa=4.876; RHO=60.9
def bits(npr,m,beta):
    al=npr*m/n
    A=(math.lgamma(m+1)/math.log(2) + 5.188*math.log2(m) + kappa*m*m*math.log2(3)
       + n*(1 + kappa*beta*al*al - al) + npr)
    B=math.log2(m)+2*npr
    return max(A,B)
best=None; rows=[]
for npr in range(2,131):
    if n%npr==0: continue
    q,r=divmod(n,npr); beta=n/(n+npr-r)
    bm=min((bits(npr,m,beta),m) for m in range(2,60))
    rows.append((npr,beta,bm[0],bm[1]))
    if best is None or bm[0]<best[0]: best=(bm[0],npr,bm[1])
print("Proposition 7 in FULL at integer m, n=131, kappa=4.876, beta at (B)'s bound:")
print("  minimum over all n' and m in 2..59 : 2^%.2f at n'=%d, m=%d"%(best[0],best[1],best[2]))
print("  M7's idealised (m>>1) figure       : 2^117.67")
print("  rho, KN-LIT-096                    : 2^%.2f"%RHO)
print("  any (n', m) beats rho?             : %s"%(best[0]<RHO))
print("  => the m>>1 idealisation is GENEROUS TO THE ATTACKER by ~%.0f bits,"%(best[0]-117.67))
print("     which is the conservative direction for a non-existence claim.")
def noexp(npr,m,beta):
    al=npr*m/n; return n*(1+kappa*beta*al*al-al)+npr
b2=min((noexp(npr,m,n/(n+npr-(131%npr))),npr,m) for npr in range(2,131) if n%npr for m in range(2,400))
print()
print("dropping 3^{kappa m^2} entirely: min = 2^%.2f at n'=%d m=%d -> still %s rho"
      %(b2[0],b2[1],b2[2],"BELOW" if b2[0]<RHO else "ABOVE"))
for npr,beta,b,m in [x for x in rows if x[0] in (2,3,33,44,66,130)]:
    print("   n'=%-4d beta=%.6f best m=%-3d cost=2^%.2f"%(npr,beta,m,b))
