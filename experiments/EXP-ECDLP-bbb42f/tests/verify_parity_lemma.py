import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny2 import two_torsion_roots
from sympy import nextprime, randprime

random_primes = [97, 1009, 10007, 100003, 1048583, int(nextprime(1 << 24)), int(nextprime(1 << 28))]
for p in random_primes:
    # anomalous curve has t=1; construct one directly is expensive, but the
    # lemma only depends on p being odd, not on a specific a,b -- verify the
    # polynomial-level claim directly:
    # X^2 - 1*X + p mod 2 should have no root for any odd p
    import sympy
    x = sympy.symbols("x")
    poly = (x**2 - 1*x + p)
    roots_mod2 = [r for r in (0, 1) if (r*r - r + p) % 2 == 0]
    print(f"p={p} (odd={p%2==1}) roots of X^2-X+p mod 2: {roots_mod2}")
