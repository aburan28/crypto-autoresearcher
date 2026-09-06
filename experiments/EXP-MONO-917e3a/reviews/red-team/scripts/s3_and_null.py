import sympy as sp
x1,x2,x3,A,B,y1,y2,y3=sp.symbols('x1 x2 x3 A B y1 y2 y3')
f=lambda t:t**3+A*t+B
F={y1:f(x1),y2:f(x2),y3:f(x3)}

def add(P,Q):
    if P is None: return Q
    if Q is None: return P
    a1,b1=P; a2,b2=Q
    lam=(b2-b1)/(a2-a1)
    a3=sp.together(lam**2-a1-a2)
    b3=sp.together(lam*(a1-a3)-b1)
    return (sp.cancel(a3),sp.cancel(b3))

P1=(x1,y1);P2=(x2,y2);P3=(x3,y3)
Q=add(add(P1,P2),P3)
num,den=sp.fraction(sp.cancel(sp.together(Q[1])))
num=sp.expand(num)

def reduce_y(expr):
    P=sp.Poly(expr,y1,y2,y3); out=0
    for (i,j,k),c in P.terms():
        out+= c*F[y1]**(i//2)*y1**(i%2)*F[y2]**(j//2)*y2**(j%2)*F[y3]**(k//2)*y3**(k%2)
    return sp.expand(out)

red=reduce_y(num)
# iterate until stable (reduction can raise degrees via substitution? no, degrees only drop)
Pr=sp.Poly(red,y1,y2,y3)
basis={}
for (i,j,k),c in Pr.terms():
    basis[(i,j,k)]=sp.expand(basis.get((i,j,k),0)+c)
print("y(P1+P2+P3) numerator, reduced; monomial support over k[x1,x2,x3] basis {y1^a y2^b y3^c, a,b,c in 0,1}:")
nonzero=0
for k in sorted(basis):
    c=sp.expand(basis[k])
    if c!=0:
        nonzero+=1
        print(f"  y1^{k[0]} y2^{k[1]} y3^{k[2]} : nonzero, deg = {sp.total_degree(c)}")
print("number of nonzero basis coefficients:",nonzero)
print("=> y(P1+P2+P3) identically zero?", nonzero==0)
# print one explicit nonzero coefficient
for k in sorted(basis):
    c=sp.expand(basis[k])
    if c!=0:
        print(f"\nexample coefficient at y1^{k[0]}y2^{k[1]}y3^{k[2]}:")
        print("  ",sp.factor(c))
        break

# null-object probabilities for the witness test
import math
for (p,n,m) in [(101,4,4),(211,4,4),(101,8,5)]:
    pr=1.0
    for i in range(1,n): pr*= (1-i/p)
    print(f"\nNULL: random map of {n} sign classes into F_{p}: P(all {n} distinct) = {pr:.4f}")
