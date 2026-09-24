"""Index calculus for the ECDLP on elliptic curves over prime fields E(F_p).

A self-contained, standard-library implementation of the Semaev point-
decomposition route to index calculus:

* :mod:`.curve`      -- short-Weierstrass arithmetic over F_p and a certified
  generator of prime-order toy curves;
* :mod:`.semaev`     -- the summation polynomial S_3 and the root-finding it
  needs;
* :mod:`.factor_base` -- pluggable factor bases (small-x interval, multiplicative
  subgroup coset, random subset);
* :mod:`.decompose`  -- point decomposition over a factor base for any arity m;
* :mod:`.linalg`     -- sparse structured Gaussian elimination modulo N;
* :mod:`.rho`        -- Pollard rho baseline on the same curves;
* :mod:`.solver`     -- the end-to-end index-calculus solver with charged cost
  accounting.

Every returned logarithm is verified by scalar multiplication.  The code is
meant for toy parameters (p up to roughly 2^32); nothing here threatens any
deployed curve.
"""

from .curve import Curve, generate_prime_order_curve
from .factor_base import FactorBase
from .solver import ICResult, solve_index_calculus
from .rho import RhoResult, pollard_rho

__all__ = [
    "Curve",
    "FactorBase",
    "ICResult",
    "RhoResult",
    "generate_prime_order_curve",
    "pollard_rho",
    "solve_index_calculus",
]
