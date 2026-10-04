"""J6 (b): the exact kappa threshold for the closure (E), and the margin of (E)
over H1's own assumption.  Proposition 8 of KN-LIT-4fe9d2: alpha_beta =
1/(2 kappa beta); beating generic needs alpha_beta > 1, i.e. kappa < 1/(2 beta)."""
from fractions import Fraction as F
n=131
rows=[]
for npr in range(2,131):
    if n%npr==0: continue
    q,r=divmod(n,npr)
    beta=F(n,n+npr-r); rows.append((npr,q,r,beta,1/(2*beta)))
mn=min(rows,key=lambda t:t[3]); mx=max(rows,key=lambda t:t[3])
print("min beta over n'=2..130 :",mn[3],float(mn[3]),"at n'=%d (q=%d,r=%d)"%(mn[0],mn[1],mn[2]))
print("  => (E) needs kappa >= 1/(2 beta_min) =",max(x[4] for x in rows),float(max(x[4] for x in rows)))
print("max beta :",mx[3],float(mx[3]),"at n'=%d"%mx[0])
print()
print("general worst case n'=n-1 (q=1,r=1): beta = n/(2n-2), kappa_crit = (n-1)/n")
for N in (7,31,131,257,1021,10**6):
    print("   n=%-8d beta_min=%.9f  kappa_crit=%.9f"%(N,N/(2*N-2),(N-1)/N))
print()
print("H1's formal_statement assumes kappa >= 1.  Margin of (E) beyond H1:")
print("   (E) needs kappa >= 130/131 = %.6f ; H1 gives kappa >= 1"%(130/131))
print("   margin = 1/n = %.6f  (%.3f%%) at n=131, and -> 0 as n -> infinity"%(1/131,100/131))
print()
k=F(4876,1000)
for lab,beta in [("beta_min=131/260",F(131,260)),("beta=131/132",F(131,132)),("beta=3/4",F(3,4))]:
    ab=1/(2*k*beta)
    print("%-18s kappa=4.876 -> alpha_beta=%.7f exponent(m>>1)=%.7f bits=%.2f"%(lab,float(ab),float(1-ab/2),float(1-ab/2)*131))
print()
print("ADJUDICATING the discrepancy KN-LIT-4fe9d2 flags in its source:")
ab=1/(2*F(3,2)*F(3,4))
print("   paper Section 4.4: 'kappa < 1.5 at beta=3/4 gives alpha_beta > 1'")
print("   alpha_beta(kappa=1.5, beta=3/4) =",ab,float(ab),"-> > 1 ?",ab>1)
print("   correct threshold at beta=3/4 : kappa < 1/(2*3/4) =",F(2,3),float(F(2,3)))
print("   => the knowledge record is RIGHT and the paper's 1.5 is wrong.")
