"""When is the Frobenius-orbit factor base available, and is it a net win?

Setting: Gaudry/Diem index calculus on E(F_{q^n}) with factor base
F_V = {P : x(P) in V}, V an F_q-subspace of dimension l, decomposing each target
into m summands.  A decomposition exists with probability ~ q^(ml-n)/m!, so the
unconstrained choice is l* = ceil(n/m).

If E is defined over F_q then pi(x, y) = (x^q, y^q) is an endomorphism of E, so
F_V is pi-stable exactly when V is sigma-stable.  Quotienting by pi-orbits
divides both the number of relations needed and the linear-algebra dimension by
the mean orbit size.

Two constraints bite:
  (1) ATTAINABILITY -- l must lie in the stable-dimension spectrum, which is the
      set of subset sums of the degrees of the irreducible factors of T^n - 1.
  (2) FAITHFULNESS  -- sigma must act on V with orbits longer than 1.  Its fixed
      space is exactly F_q, so the unique stable LINE over F_q is fixed
      pointwise: the dimension a small-m attack would most like to use buys
      nothing.  V must be cut by a divisor of T^n - 1 other than 1 and T - 1.

NET VERDICT.  Stability inflates the factor base from q^l* to q^l', inflating
the sparse linear algebra by q^(2(l'-l*)), while Frobenius deflates it by
(mean orbit size)^2.  The orbit trick is a net win exactly when

        q^(l' - l*)  <  mean orbit size   ( <= n ).

That inequality, not the mere existence of a stable subspace, is the decision.
"""
from math import gcd, log2

from lattice import attainable_dimensions, cyclotomic_cosets
from orbits import all_stable_subspaces, orbit_census_burnside


def spectrum(q, n):
    """dimension -> best (largest mean orbit size) stable subspace of that dimension.

    For n prime the structure is closed-form: T^n - 1 = (T-1) * s factors of
    degree d = ord_n(q), every non-fixed orbit has length exactly n, and a stable
    subspace of dimension a + b*d (a in {0,1}) has q^a fixed points and all the
    rest in n-orbits.  For composite n the subsets are enumerated.
    """
    assert gcd(q, n) == 1, "scoped to gcd(q, n) = 1"
    if _is_prime(n):
        d = _ord(q, n)
        s = (n - 1) // d
        out = {}
        for a in (0, 1):
            for b in range(s + 1):
                dim = a + b * d
                fixed = q ** a
                elements = q ** dim
                orbits = fixed + (elements - fixed) // n
                assert (elements - fixed) % n == 0, "non-fixed points must fall into full n-orbits"
                cur = dict(dimension=dim, elements=elements, orbits=orbits,
                           reduction_factor=elements / orbits,
                           max_orbit_size=(n if dim > a else 1),
                           fixed_points=fixed)
                if dim not in out or cur["reduction_factor"] > out[dim]["reduction_factor"]:
                    out[dim] = cur
        assert sorted(out) == attainable_dimensions(q, n), "closed form disagrees with lattice"
        return out
    out = {}
    for sub in all_stable_subspaces(q, n):
        c = orbit_census_burnside(q, n, sub)
        d = c["dimension"]
        if d not in out or c["reduction_factor"] > out[d]["reduction_factor"]:
            out[d] = c
    assert sorted(out) == attainable_dimensions(q, n), "enumeration disagrees with lattice"
    return out


def min_faithful_dimension(q, n, spec=None):
    """Smallest stable dimension carrying an orbit longer than 1."""
    spec = spec or spectrum(q, n)
    c = [d for d, v in spec.items() if v["max_orbit_size"] > 1]
    return min(c) if c else None


def verdict(q, n, m, spec=None):
    """Attainability and net-win verdict for m-summand decomposition."""
    spec = spec or spectrum(q, n)
    l_star = -(-n // m)                              # ceil(n/m)
    usable = [d for d, v in spec.items()
              if d >= l_star and v["max_orbit_size"] > 1 and d < n]
    base = dict(q=q, n=n, m=m, l_star=l_star)
    if not usable:
        return dict(base, l_prime=None, available=False, penalty_dims=None,
                    basis_inflation_log2=None, mean_orbit_size=None,
                    net_win=False, margin_log2=None,
                    reason="no faithful stable subspace of index-calculus dimension")
    l_prime = min(usable)
    v = spec[l_prime]
    penalty = l_prime - l_star
    infl = penalty * log2(q)
    orb = log2(v["reduction_factor"])
    return dict(base, l_prime=l_prime, available=True, penalty_dims=penalty,
                basis_inflation_log2=infl, mean_orbit_size=v["reduction_factor"],
                net_win=infl < orb, margin_log2=orb - infl, reason=None)


def max_usable_m(q, n, spec=None, m_cap=None):
    """Largest m for which the orbit trick is a net win (None if never)."""
    spec = spec or spectrum(q, n)
    cap = m_cap or n
    good = [m for m in range(2, cap + 1) if verdict(q, n, m, spec)["net_win"]]
    return max(good) if good else None


def _ord(q, n):
    x, k = q % n, 1
    while x != 1:
        x = (x * q) % n
        k += 1
        if k > n:
            raise ValueError("q is not invertible mod n")
    return k


def _is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True
