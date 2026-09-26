"""Index calculus for the ECDLP on elliptic curves over prime fields E(F_p).

A self-contained implementation of the Semaev point-decomposition route to
index calculus, with Pollard rho as the matched baseline:

* :mod:`.curve`       -- short-Weierstrass arithmetic over F_p and a certified
  generator of prime-order toy curves (optionally with a filter on p);
* :mod:`.semaev`      -- the summation polynomial S_3 and its root-finding;
* :mod:`.factor_base` -- pluggable factor bases (small-x, multiplicative
  subgroup coset, random) and their membership polynomials;
* :mod:`.decompose`   -- point decomposition for any arity m: exhaustive, or
  meet-in-the-middle against a table of precomputed tails (:mod:`.tails`),
  which finds the same relations; an optional numpy scan (:mod:`._accel`)
  changes speed, not results;
* :mod:`.msolve`      -- algebraic decomposition through the msolve Groebner
  basis solver (external binary);
* :mod:`.linalg`      -- incremental sparse elimination modulo N;
* :mod:`.rho`         -- Pollard rho with distinguished points;
* :mod:`.solver`      -- the end-to-end solver with charged cost accounting;
* :mod:`.stats`       -- exponent fits with bootstrap confidence intervals.

``python -m crypto_autoresearcher.index_calculus`` runs single solves, sweeps
against rho, and the msolve-versus-enumeration comparison; see README.md in
this directory.  Every recovered logarithm is verified by scalar
multiplication.  The code is meant for toy parameters (p up to about 2^32);
nothing here threatens any deployed curve.
"""

from .curve import Curve, generate_prime_order_curve
from .decompose import decompose, decompose_all
from .tails import TailTable, default_table_arity
from .factor_base import FactorBase, default_fb_size, subgroup_prime_filter
from .rho import RhoResult, pollard_rho
from .solver import ICResult, solve_index_calculus

__all__ = [
    "Curve",
    "FactorBase",
    "ICResult",
    "RhoResult",
    "TailTable",
    "decompose",
    "decompose_all",
    "default_fb_size",
    "default_table_arity",
    "generate_prime_order_curve",
    "pollard_rho",
    "solve_index_calculus",
    "subgroup_prime_filter",
]
