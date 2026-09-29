"""RED TEAM item 1a: independent symmetry audit of harness/semaev.py's s4_expr.

Written fresh; does NOT reuse experiments/EXP-MONO-805a02/implementation/run_experiment.py.
Stronger than the Executor's check in three ways:
  (i) SYMBOLIC curve coefficients a,b (Executor only tested a=37,b=57);
  (ii) ALL SIX transpositions (Executor tested two: x3<->x4, x1<->x4);
  (iii) also audits whether the resultant construction equals the true S_4
        (irreducibility / extraneous-factor check) and its degree pattern.
"""
import itertools, sys
import sympy
sys.path.insert(0, "/Volumes/SSD990/crypto-autoresearcher")
from harness.semaev import s4_expr, x1, x2, x3

a, b = sympy.symbols("a b")
x4 = sympy.symbols("x4")
V = [x1, x2, x3, x4]

S4 = sympy.expand(s4_expr(a, b))
print("s4_expr with SYMBOLIC a,b built. #terms:", len(S4.as_ordered_terms()))

# (iii) degree pattern
for v in V:
    print("  deg in", v, "=", sympy.Poly(S4, v).degree())
print("  total degree =", sympy.Poly(S4, *V, a, b).total_degree())

# (ii) all six transpositions, by DIRECT polynomial subtraction + expand
allzero = True
for u, w in itertools.combinations(V, 2):
    d = sympy.expand(S4 - S4.subs({u: w, w: u}, simultaneous=True))
    ok = (d == 0)
    allzero &= ok
    print(f"  transposition ({u},{w}): S4 - sigma(S4) == 0 ? {ok}"
          + ("" if ok else f"   RESIDUAL: {sympy.simplify(d)}"))

# full S_4 symmetric group check by random permutation composition (belt & braces)
import random
random.seed(11)
for _ in range(6):
    perm = V[:]
    random.shuffle(perm)
    d = sympy.expand(S4 - S4.subs(dict(zip(V, perm)), simultaneous=True))
    print("  random perm", [str(z) for z in perm], "-> diff==0 ?", d == 0)

print("ALL SIX TRANSPOSITIONS VANISH:", allzero)

# extraneous-factor audit: is the resultant irreducible over Q(a,b)?
fac = sympy.factor_list(S4)
print("factor_list: const =", fac[0], " n_factors =", len(fac[1]),
      " multiplicities =", [m for _, m in fac[1]])
