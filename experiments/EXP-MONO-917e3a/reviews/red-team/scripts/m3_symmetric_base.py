import sympy as sp
x1,x2,A,B,e1,e2=sp.symbols('x1 x2 A B e1 e2')
f=lambda t:t**3+A*t+B
D=sp.expand(f(x1)*f(x2))
# express in e1,e2
Dsym=sp.simplify(sp.symmetrize if False else 0)
# manual: rewrite via power sums
poly=sp.Poly(D,x1,x2)
Ds=sp.symbols('Ds')
sub=sp.simplify(D)
# use sympy's symmetric reduction
from sympy.polys.polyfuncs import symmetrize
sym,rem,_=symmetrize(D,[x1,x2],formal=True)
print("f(x1)f(x2) is symmetric (remainder should be 0):", sp.simplify(rem)==0)
s1,s2=sp.symbols('s1 s2')
Dsym=sym.subs({sp.Symbol('s1'):e1,sp.Symbol('s2'):e2})
Dsym=sp.expand(Dsym)
print("f(x1)f(x2) =", sp.factor(Dsym), " in e1,e2")
Delta=e1**2-4*e2
prod=sp.expand(Dsym*Delta)
print("\nIs f1*f2 a square in k(e1,e2)?  squarefree part check:")
print("  factor(f1f2)      =", sp.factor(Dsym))
print("  factor(f1f2*Delta)=", sp.factor(prod))
for name,expr in (("f1*f2",Dsym),("Delta",Delta),("f1*f2*Delta",prod)):
    pf=sp.factor_list(sp.Poly(expr,e1,e2))
    odd=[ (str(fa.as_expr()),mu) for fa,mu in pf[1] if mu%2==1 ]
    print(f"  {name}: square in k(e1,e2)? {len(odd)==0}   odd-multiplicity factors: {odd}")
