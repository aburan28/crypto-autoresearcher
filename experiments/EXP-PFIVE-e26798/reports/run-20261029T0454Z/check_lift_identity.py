"""Exact symbolic identity check; no curve trials or performance measurement."""
import hashlib
import json
from pathlib import Path
import sympy as sp

a, b, r, u, v, X = sp.symbols('a b r u v X')
f = lambda x: x**3 + a*x + b
T, V = u+v, u*v
N = V-r*T-2*r*r-a
S3 = (u-v)**2*r*r-2*(T*(V+a)+2*b)*r+(V-a)**2-4*b*T
identities = {
    'slope_numerator': N**2-4*f(r)*(T+r)-S3,
    'intersection_identity_denominators_cleared':
        4*f(r)*(f(X)-(X-u)*(X-v)*(X-r))
        -(N*(X-r)-2*f(r))**2+S3*(X-r)**2,
}
results = {name: sp.Poly(sp.expand(expr), a,b,r,u,v,X).is_zero
           for name, expr in identities.items()}
assert all(results.values())
print(json.dumps({
    'schema': 'prime-five-symbolic-identity/v1',
    'scope': 'Universal integer polynomial identities; algebraic verification only. '
             'Rational witness inference assumes nonsingular short Weierstrass curve, '
             'characteristic greater than three and nonzero target y.',
    'sympy_version': sp.__version__,
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'identities': results,
    'formal_proof_assistant_checked': False,
    'performance_claim': False,
}, indent=2))
