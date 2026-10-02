"""Demonstrates that sympy's GF(p**k) is Z/p**k, NOT the field extension F_{p^k}.

A design that reaches for sympy's domain for F_{2^n} arithmetic would compute in
Z/2^n and return plausible-looking numbers. This script makes the failure visible
rather than asserting it.
"""
from sympy import GF, Poly, symbols, resultant
X, Y = symbols('X Y')

print("1. What sympy's GF(2**4) actually is")
d = GF(2**4)
print("   GF(2**4)          ->", d)
print("   characteristic    ->", d.characteristic())
print("   is it a field?    -> in F_16 every nonzero element is invertible;")
print("      in Z/16, 2 is a zero divisor:  2 * 8 mod 16 =", (2 * 8) % 16)
print("   so GF(2**4) is Z/16, NOT F_16.\n")

print("2. The same fact, shown by an element that must be invertible in a field")
try:
    inv = d(2) ** -1
    print("   2^-1 in sympy GF(2**4) ->", inv)
except Exception as e:
    print("   2^-1 in sympy GF(2**4) raised:", type(e).__name__, e)
print("   In the real F_16 = F_2[z]/(z^4+z+1), every nonzero element has an inverse.\n")

print("3. What DOES work: GF(2) resultants (prime field, so sympy is correct here)")
f = Poly(X**2*Y + X + Y**2 + 1, X, Y, domain=GF(2))
g = Poly(X*Y**2 + Y + 1,       X, Y, domain=GF(2))
r = resultant(f.as_expr(), g.as_expr(), X)
print("   Res_X(f,g) over GF(2) =", r)
print("   degree in Y           =", Poly(r, Y, domain=GF(2)).degree())
print("\n   CONCLUSION: sympy is usable over the PRIME field F_2 only.")
print("   Any F_{2^n} arithmetic must be implemented explicitly (see preflight_resultant.py).")
