"""Exact sigma-orbit census on a Frobenius-stable subspace of F_{q^n}.

A stable subspace is an ideal of R = F_q[T]/(T^n - 1); write it as the ideal
whose quotient cogenerator is h | T^n - 1, so V = F_q[T]/(h) as an R-module and
dim_{F_q} V = deg h, with sigma acting as multiplication by T.

For v in V the annihilator is (a) with a = h / gcd(v, h), and the sigma-orbit of
v has size ord(a) := min{k > 0 : a | T^k - 1}.  The number of v with annihilator
exactly (a) is the F_q[T] totient Phi(a) = q^deg a * prod_{f | a} (1 - q^-deg f).
Hence the orbit count on V is sum_{a | h} Phi(a) / ord(a), exactly.

Scope: gcd(q, n) = 1, so that T^n - 1 is squarefree and its irreducible factors
are in bijection with the q-cyclotomic cosets mod n.  The p | n case is excluded
here and is covered only by the lattice module.
"""
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm

from lattice import cyclotomic_cosets


def _coset_order(coset, n):
    """ord of the irreducible factor whose roots are {zeta^i : i in coset}."""
    return lcm(*[n // gcd(n, i) for i in coset]) if coset else 1


def orbit_census(q, n, subset):
    """Census for the stable V cut by the cosets in `subset` (a tuple of cosets).

    Returns dict with dimension, orbit counts by size, total orbits, and the
    exact reduction factor |V| / #orbits.
    """
    assert gcd(q, n) == 1
    dim = sum(len(c) for c in subset)
    by_size = {}
    # divisors a of h <-> sub-multisets of the cosets of h (squarefree case)
    for r in range(len(subset) + 1):
        for sub in combinations(subset, r):
            deg_a = sum(len(c) for c in sub)
            # F_q[T] totient of a
            phi = q ** deg_a
            for c in sub:
                phi = phi // (q ** len(c)) * (q ** len(c) - 1)
            order = lcm(*[_coset_order(c, n) for c in sub]) if sub else 1
            if phi % order:
                raise AssertionError(f"orbit size {order} does not divide class {phi}")
            by_size[order] = by_size.get(order, 0) + phi
    total_orbits = sum(cnt // size for size, cnt in by_size.items())
    size = q ** dim
    assert sum(by_size.values()) == size, "orbit census must partition V"
    return dict(
        dimension=dim,
        elements=size,
        orbits=total_orbits,
        elements_by_orbit_size={int(k): int(v) for k, v in sorted(by_size.items())},
        orbits_by_size={int(k): int(v // k) for k, v in sorted(by_size.items())},
        reduction_factor=float(Fraction(size, total_orbits)),
        max_orbit_size=max(by_size),
    )


def all_stable_subspaces(q, n):
    """Every sigma-stable subspace of F_{q^n}, as a subset of cyclotomic cosets."""
    cos = cyclotomic_cosets(q, n)
    out = []
    for r in range(len(cos) + 1):
        out.extend(combinations(cos, r))
    return out


def best_stable_basis(q, n, target_dim):
    """Among stable V with dim >= target_dim, the smallest; tie-break on reduction.

    Returns (census, penalty_dims) where penalty_dims = dim(V) - target_dim is the
    number of extra F_q-dimensions stability forces on the factor base, i.e. the
    factor base is q^penalty_dims times larger than the unconstrained optimum.
    """
    best = None
    for sub in all_stable_subspaces(q, n):
        dim = sum(len(c) for c in sub)
        if dim < target_dim:
            continue
        cen = orbit_census(q, n, sub)
        key = (dim, -cen["reduction_factor"])
        if best is None or key < best[0]:
            best = (key, cen)
    if best is None:
        return None, None
    return best[1], best[1]["dimension"] - target_dim


# ---------------------------------------------------------------------------
# A second, independent derivation of the same census, by Burnside's lemma.
#
# <sigma> is cyclic of order n acting on V.  The fixed space of sigma^j on
# F_{q^n} is the subfield F_{q^gcd(j,n)}, so
#
#     #orbits(V) = (1/n) * sum_{j<n} |Fix(sigma^j) ∩ V|
#                = (1/n) * sum_{e | n} phi(n/e) * q^D(e),
#
# where D(e) = dim(V ∩ F_{q^e}) = total size of the cosets of V whose order
# divides e.  Möbius inversion over the divisor lattice then gives the exact
# number of elements of each orbit length.  This shares no step with the
# annihilator/totient argument above: no divisors of h, no F_q[T] totient.
# ---------------------------------------------------------------------------

def _divisors(n):
    return sorted(d for d in range(1, n + 1) if n % d == 0)


def _phi(n):
    r, m = n, n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def _mobius(n):
    m, res, p = n, 1, 2
    while p * p <= m:
        if m % p == 0:
            m //= p
            if m % p == 0:
                return 0
            res = -res
        p += 1
    return -res if m > 1 else res


def orbit_census_burnside(q, n, subset):
    """Same census as orbit_census(), derived by Burnside instead."""
    assert gcd(q, n) == 1
    dim = sum(len(c) for c in subset)
    orders = [(_coset_order(c, n), len(c)) for c in subset]
    D = {e: sum(sz for o, sz in orders if e % o == 0) for e in _divisors(n)}
    total = sum(_phi(n // e) * q ** D[e] for e in _divisors(n))
    assert total % n == 0, "Burnside sum must be divisible by the group order"
    orbits = total // n
    by_size = {}
    for t in _divisors(n):
        cnt = sum(_mobius(t // e) * q ** D[e] for e in _divisors(t))
        if cnt:
            by_size[t] = cnt
    assert sum(by_size.values()) == q ** dim, "orbit-length census must partition V"
    return dict(
        dimension=dim,
        elements=q ** dim,
        orbits=orbits,
        elements_by_orbit_size={int(k): int(v) for k, v in sorted(by_size.items())},
        orbits_by_size={int(k): int(v // k) for k, v in sorted(by_size.items())},
        reduction_factor=float(Fraction(q ** dim, orbits)),
        max_orbit_size=max(by_size),
    )
