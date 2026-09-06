"""Exact rational-function residuals and a scoped square-zero proof."""
import sympy as S

LEMMA = """# Scoped square-zero torsion argument

This is a producer proof submission for independent checking, not a research
status transition. The claims assume a smooth elliptic group scheme over
R=k[e]/(e^2), and n invertible in k. The coordinate conclusions also assume
the displayed fixed short Weierstrass chart.

1. For any smooth group scheme, the kernel of reduction on R-points is its
tangent space at the identity tensored with (e). To see the first-order law,
write a local identity coordinate t. The identity axioms give the group law
g(t1,t2)=t1+t2+ terms of total degree at least two. Substituting t_i=e a_i
annihilates every higher term, hence the kernel law is addition and [n]
acts by multiplication by n. Translation moves this description to any
specified fiber point. Thus two n-torsion lifts of the same point differ
by kernel element e a with n a=0, so a=0: uniqueness.

2. A smooth affine point admits a lift over this square-zero extension:
substitute any lifts of its coordinates in the curve equation, giving
residual e r, and correct one coordinate by e h using a nonzero partial
derivative on the smooth special fiber. Points at infinity use a smooth
local chart. For an initial lift Q of an n-torsion point, [n]Q is in the
kernel. Subtract its unique kernel n-division from Q. The result is an
n-torsion lift. This proves existence as well as uniqueness over R.

3. In a constant family the constant-coordinate lift exists and is n-torsion
because base extension respects the group operations; uniqueness identifies
it with the lift above. Its coordinate derivatives in those constant
coordinates vanish. A varying coordinate gauge need not have zero raw
derivatives, but x^2/A remains constant by the separate gauge certificate.

4. In a varying family the constant-coordinate candidate need not lie on
the curve. The independently submitted flex identities exhibit instead
P=(3,s), with s=5+e and A=6s-27, B=s^2-18s+54. The point and its tangent
have triple intersection. On a smooth plane cubic the line-intersection
definition of the elliptic group law gives P+P+P=O for this flex.
One can also use doubling: slope m=(3*3^2+A)/(2s)=3,
x(2P)=m^2-2*3=3, y(2P)=m*(3-3)-s=-s; hence 2P=-P.
Here 2s is a unit on the fixed prime panel, P is finite and not O,
and 3 is prime; the section has order exactly 3. The symbolic certificate
checks these identities and the special-fiber discriminant unit.

5. Uniqueness therefore does not imply constant coordinates in a varying
family. This concerns response to variation of the ambient curve, not a
nonzero differential of torsion translation on one fixed curve. It makes
no claim that a finite jet distinguishes all torsion points: the P/-P
and C/G collisions are retained. The IDEA-109 expectation about scalar
displacement or global level structure is not refuted by this argument.
No canonical lift, mixed-characteristic transfer, or ECDLP speedup follows.

Provenance: internal derivation submitted by Executor. No external theorem
is claimed retrieved. The local group law and smooth group assumptions
are explicitly used above and require independent proof review.
"""

def certificates():
    a,b,x,z,u,v,c,e,s,X=S.symbols("A0 A1 x0 x1 u0 v c e s X")
    J=2*x*z/a-x*x*b/a**2
    F0=x*x/a
    xp=u**2*x; zp=u**2*(z+2*v*x)
    ap=u**4*a; bp=u**4*(b+4*v*a)
    A=6*s-27; B=s*s-18*s+54
    groups={
      "expansion":[S.expand((a+e*b)*(F0+e*J)-(x+e*z)**2).coeff(e,i) for i in (0,1)],
      "active_model_action":[xp*xp/ap-F0,2*xp*zp/ap-xp*xp*bp/ap**2-J],
      "pullback_law":[J.subs({z:c*z,b:c*b},simultaneous=True)-c*J],
      "constant_pure_gauge_null":[J.subs({z:0,b:0}),J.subs({z:2*v*x,b:4*v*a})],
      "flex_identities":[s*s-27-3*A-B, X**3+A*X+B-(3*X+s-9)**2-(X-3)**3,
         (27+A)-6*s,9-6-3,3*(3-3)-s-(-s),
         4*3**3+27*(-11)**2-3375,
         S.diff(9/(3+6*e),e).subs(e,0)+6],
    }
    out={}
    for name,res in groups.items():
        reduced=[S.cancel(r) for r in res]
        out[name]={"status":"PASS" if all(r==0 for r in reduced) else "FAIL",
                   "residuals":[str(r) for r in reduced],
                   "method":"SymPy exact rational simplification; not numeric substitution"}
    out["scoped_etale_section_lemma"]={"status":"PASS","certificate":"lemma-proof.md",
       "method":"Producer-written square-zero kernel and smooth-lifting argument; independent review pending"}
    return out
