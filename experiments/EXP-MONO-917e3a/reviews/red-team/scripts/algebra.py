import sympy as sp

x1,x2,A,B,u,v = sp.symbols('x1 x2 A B u v')   # u=y1, v=y2
f = lambda t: t**3 + A*t + B
f1, f2 = f(x1), f(x2)

# ---- |S|=2, signs (+,+): Q = P1+P2 ----
d   = x2 - x1
lam = (v-u)/d
x3  = lam**2 - x1 - x2
y3  = lam*(x1-x3) - u

Y3 = sp.simplify(sp.together(y3))
num, den = sp.fraction(sp.cancel(Y3))
num = sp.expand(num)
print("denominator of y(P1+P2):", sp.factor(den))

# reduce numerator modulo u^2 - f1, v^2 - f2  (basis 1,u,v,uv over k[x1,x2])
P = sp.Poly(num, u, v)
red = 0
for (i,j), c in P.terms():
    term = c
    # u^i -> f1^(i//2) * u^(i%2)
    term *= f1**(i//2) * u**(i % 2)
    term *= f2**(j//2) * v**(j % 2)
    red += term
red = sp.expand(red)
Pr = sp.Poly(red, u, v)
coeffs = {k: sp.expand(c) for k,c in Pr.terms()}
print("\nreduced numerator, coefficients on basis {1,u,v,uv}:")
for k in [(0,0),(1,0),(0,1),(1,1)]:
    c = coeffs.get(k, sp.Integer(0))
    print("  ", {(0,0):'1',(1,0):'u=y1',(0,1):'v=y2',(1,1):'u*v'}[k], "->", sp.factor(sp.expand(c)))

Cv = sp.expand(coeffs.get((0,1), sp.Integer(0)))
print("\nC_v  =", sp.expand(Cv))
print("C_v  - ( -(x1**3 + 3*x1**2*x2 + 3*A*x1 + A*x2 + 4*B) ) =",
      sp.simplify(Cv + (x1**3 + 3*x1**2*x2 + 3*A*x1 + A*x2 + 4*B)))
print("C_v identically zero? ", sp.simplify(Cv) == 0)

Cu = sp.expand(coeffs.get((1,0), sp.Integer(0)))
print("C_u  =", sp.factor(Cu))

# ---- signs (+,-): Q = P1 - P2  (v -> -v) ----
Cv_m = sp.expand(Cv.subs(v, -v))   # coefficient structure: just check the whole thing
lam2 = (-v-u)/d
x3b  = lam2**2 - x1 - x2
y3b  = lam2*(x1-x3b) - u
num2, den2 = sp.fraction(sp.cancel(sp.together(y3b)))
P2p = sp.Poly(sp.expand(num2), u, v)
red2 = 0
for (i,j), c in P2p.terms():
    red2 += c * f1**(i//2) * u**(i % 2) * f2**(j//2) * v**(j % 2)
c2 = {k: sp.expand(cc) for k,cc in sp.Poly(sp.expand(red2), u, v).terms()}
print("\n[P1 - P2] coefficient on v:", sp.expand(c2.get((0,1), sp.Integer(0))))
print("[P1 - P2] coefficient on u:", sp.expand(c2.get((1,0), sp.Integer(0))))
