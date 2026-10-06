"""Imaginary quadratic orders as endomorphism rings: exact, dependency-free.

Everything an ordinary elliptic curve E/F_q can offer a scalar-multiplication
decomposition is visible in End(E) tensor Q = K = Q(sqrt(D_K)), a rank-2 ring.
This module answers the questions the sweeper asks of that ring:

* which fundamental discriminant D_K the Frobenius discriminant t^2 - 4q
  hides, WITHOUT factoring (``small_discriminant_scan``): every D_K with
  |D_K| <= bound is tested by one perfect-square check, so "no CM by a field
  of discriminant above -bound" is a certificate, not a heuristic;
* the minimum degree of any non-integer endomorphism (``min_nonscalar_degree``),
  which is >= |D_K| / 4 and so tells you at once that a curve with a huge
  D_K has no cheap endomorphism at all;
* the elements of a given small norm (``elements_of_norm``), i.e. the
  candidate cheap endomorphisms, with their height in the basis {1, omega};
* the shortest "isogeny cycle" through a split prime ell
  (``smallest_principal_power``): the least k such that a primitive element
  of norm ell^k exists, which is the cheapest endomorphism of ell-power
  degree that is a chain of k ell-isogenies starting and ending at E.

Conventions.  D is any negative discriminant (D = 0,1 mod 4); the order of
discriminant D is Z[omega] with omega = (tau + sqrt(D)) / 2, tau = D mod 2,
so Tr(omega) = tau in {0, 1} and N(omega) = (tau^2 - D) / 4.  (For D = -3
this is omega = zeta_6; for D = -4 it is i.)  An element a + b*omega has
    N(a + b*omega) = a^2 + a*b*tau + b^2 * (tau^2 - D) / 4,
and its *height* is max(|a|, |b|).  The height is what a scalar decomposition
sees: a + b*omega acts on a prime-order subgroup as a + b*lambda, so a
relation between generators of height H is a lattice vector of length ~H.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isqrt


# ---------------------------------------------------------------------------
# basic order arithmetic
# ---------------------------------------------------------------------------

def is_discriminant(D: int) -> bool:
    return D < 0 and D % 4 in (0, 1)


def omega_trace_norm(D: int) -> tuple[int, int]:
    """(Tr omega, N omega) for omega = (tau + sqrt D)/2, tau = D mod 2."""
    if not is_discriminant(D):
        raise ValueError(f"not a negative discriminant: {D}")
    tau = D % 2
    return tau, (tau * tau - D) // 4


def norm(D: int, a: int, b: int) -> int:
    """N(a + b*omega) in the order of discriminant D."""
    tau, nw = omega_trace_norm(D)
    return a * a + a * b * tau + b * b * nw


def trace(D: int, a: int, b: int) -> int:
    """Tr(a + b*omega) = 2a + b*tau."""
    return 2 * a + b * omega_trace_norm(D)[0]


def conjugate(D: int, a: int, b: int) -> tuple[int, int]:
    """Coordinates of the conjugate of a + b*omega: a + b*tau - b*omega."""
    return a + b * omega_trace_norm(D)[0], -b


def multiply(D: int, x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    """(a1 + b1 w)(a2 + b2 w) using w^2 = tau*w - N(w)."""
    a1, b1 = x
    a2, b2 = y
    tau, nw = omega_trace_norm(D)
    a = a1 * a2 - b1 * b2 * nw
    b = a1 * b2 + a2 * b1 + b1 * b2 * tau
    return a, b


def power(D: int, x: tuple[int, int], k: int) -> tuple[int, int]:
    r = (1, 0)
    base = x
    while k:
        if k & 1:
            r = multiply(D, r, base)
        base = multiply(D, base, base)
        k >>= 1
    return r


def height(a: int, b: int) -> int:
    return max(abs(a), abs(b))


def eigenvalue(D: int, a: int, b: int, lam_omega: int, n: int) -> int:
    """Action of a + b*omega on a subgroup where omega acts as lam_omega."""
    return (a + b * lam_omega) % n


def omega_eigenvalues(D: int, n: int) -> list[int]:
    """Roots of x^2 - tau x + N(omega) modulo a prime n (0, 1 or 2 of them).

    These are the two possible scalars by which omega can act on a cyclic
    subgroup of prime order n.  Which one a given curve/point realises is a
    property of the curve, not of the ring; the lattice geometry is the same
    for both, so the sweeper may use either.
    """
    from sympy.ntheory import sqrt_mod
    tau, nw = omega_trace_norm(D)
    if n == 2:
        return [r for r in (0, 1) if (r * r - tau * r + nw) % 2 == 0]
    s = sqrt_mod(D % n, n)      # discriminant of x^2 - tau x + nw is D
    if s is None:
        return []
    inv2 = pow(2, -1, n)
    return sorted({(tau + s) * inv2 % n, (tau - s) * inv2 % n})


# ---------------------------------------------------------------------------
# discriminant identification
# ---------------------------------------------------------------------------

def frobenius_discriminant(q: int, t: int) -> int:
    return t * t - 4 * q


def is_fundamental(D: int) -> bool:
    """D is a fundamental discriminant (field discriminant).

    Exact for |D| up to the limits of sympy factorisation; the scan below only
    ever calls this on small |D|, where it is instant.
    """
    from sympy import factorint
    if not is_discriminant(D):
        return False
    m = -D
    if D % 4 == 1:
        # squarefree and = 1 mod 4
        return all(e == 1 for e in factorint(m).values())
    # D = 0 mod 4: D/4 = 2 or 3 mod 4 and squarefree
    m4 = m // 4
    if (-m4) % 4 not in (2, 3):
        return False
    return all(e == 1 for e in factorint(m4).values())


def fundamental_discriminants(bound: int):
    """Yield every fundamental discriminant D with -bound <= D < 0, ascending |D|."""
    # Sieve squarefree parts rather than factoring each candidate.
    limit = bound
    sqfree = bytearray([1]) * (limit + 1)
    i = 2
    while i * i <= limit:
        sq = i * i
        for m in range(sq, limit + 1, sq):
            sqfree[m] = 0
        i += 1
    for m in range(1, limit + 1):
        D = -m
        if m % 4 == 3 and sqfree[m]:            # D = 1 mod 4, squarefree
            yield D
        elif m % 4 == 0:
            m4 = m // 4
            if sqfree[m4] and (-m4) % 4 in (2, 3):
                yield D


@dataclass(frozen=True)
class DiscriminantScan:
    frobenius_discriminant: int
    bound: int
    found: int | None          # the fundamental discriminant D_K if |D_K| <= bound
    conductor: int | None      # f with t^2 - 4q = D_K f^2 when found
    certificate: str

    @property
    def cm_field_small(self) -> bool:
        return self.found is not None


def small_discriminant_scan(D_frob: int, bound: int) -> DiscriminantScan:
    """Decide whether t^2 - 4q = D_K f^2 for some fundamental |D_K| <= bound.

    One exact perfect-square test per candidate D_K; no factoring of D_frob.
    A negative answer is a proof: every endomorphism of E not in Z then has
    degree >= bound / 4 (see ``min_nonscalar_degree``).
    """
    if D_frob >= 0:
        raise ValueError("ordinary curves over a finite field have t^2 - 4q < 0")
    for DK in fundamental_discriminants(bound):
        if D_frob % DK:
            continue
        m = D_frob // DK
        if m <= 0:
            continue
        f = isqrt(m)
        if f * f == m:
            return DiscriminantScan(D_frob, bound, DK, f,
                                    f"t^2-4q = ({DK}) * {f}^2; CM field Q(sqrt({DK}))")
    return DiscriminantScan(
        D_frob, bound, None, None,
        f"no fundamental discriminant D_K with |D_K| <= {bound} divides t^2-4q "
        f"with square cofactor; hence |D_K| > {bound} and every non-scalar "
        f"endomorphism has degree >= {bound // 4}")


def fundamental_discriminant_exact(D: int) -> tuple[int, int]:
    """(D_K, f) with D = D_K f^2, by full factorisation -- toy-sized |D| only."""
    from sympy import factorint
    if not is_discriminant(D):
        raise ValueError(D)
    m = -D
    f = 1
    core = 1
    for pr, e in factorint(m).items():
        f *= pr ** (e // 2)
        if e % 2:
            core *= pr
    if (-core) % 4 == 1:
        return -core, f
    # -core = 2, 3 mod 4: the field discriminant is -4*core, and D = 0 mod 4
    # forces f even.
    assert f % 2 == 0, (D, core, f)
    return -4 * core, f // 2


# ---------------------------------------------------------------------------
# cheap-endomorphism inventory
# ---------------------------------------------------------------------------

def min_nonscalar_degree(D: int) -> int:
    """Smallest degree of an endomorphism not in Z, in the order of disc D.

    deg(a + b w) = N(a + b w) with b != 0.  Completing the square,
    4N = (2a + b tau)^2 + b^2 |D| >= |D| (b = 1, 2a + tau = 0 or +-1), so
    the minimum is attained at b = 1 and equals (|D| + (D mod 2)) / 4.
    """
    if not is_discriminant(D):
        raise ValueError(D)
    best = None
    for a in range(-abs(D) // 2 - 2, abs(D) // 2 + 3):
        nv = norm(D, a, 1)
        if best is None or nv < best:
            best = nv
    return best


@dataclass(frozen=True)
class RingElement:
    D: int
    a: int
    b: int

    @property
    def norm(self) -> int:
        return norm(self.D, self.a, self.b)

    @property
    def trace(self) -> int:
        return trace(self.D, self.a, self.b)

    @property
    def height(self) -> int:
        return height(self.a, self.b)

    @property
    def primitive(self) -> bool:
        """Not divisible by any rational integer > 1 (i.e. a cyclic isogeny)."""
        from math import gcd
        return gcd(self.a, self.b) == 1

    def eigenvalue(self, lam_omega: int, n: int) -> int:
        return eigenvalue(self.D, self.a, self.b, lam_omega, n)

    def __str__(self) -> str:
        return f"({self.a} + {self.b}*w | D={self.D}, N={self.norm}, H={self.height})"


def elements_of_norm(D: int, N: int, *, primitive_only: bool = True,
                     up_to_units_and_conjugation: bool = True) -> list[RingElement]:
    """All a + b*omega of norm exactly N with b != 0 (exact search).

    4N = (2a + b tau)^2 + b^2 |D|, so |b| <= sqrt(4N/|D|) and for each b the
    value (2a + b tau)^2 = 4N - b^2|D| must be a perfect square.
    """
    if not is_discriminant(D) or N <= 0:
        return []
    out: list[RingElement] = []
    absD = -D
    tau = omega_trace_norm(D)[0]
    bmax = isqrt(4 * N // absD)
    for b in range(1, bmax + 1):
        rem = 4 * N - b * b * absD
        if rem < 0:
            break
        s = isqrt(rem)
        if s * s != rem:
            continue
        for sgn in ((s,) if s == 0 else (s, -s)):
            twice_a = sgn - b * tau
            if twice_a % 2:
                continue
            a = twice_a // 2
            el = RingElement(D, a, b)
            if primitive_only and not el.primitive:
                continue
            out.append(el)
    if up_to_units_and_conjugation:
        # Keep one representative per {units} x {conjugation} orbit: the
        # scalar decomposition cannot tell them apart (same lattice up to a
        # unimodular change), and the sweeper counts cost per distinct map.
        seen: dict[tuple[int, int], RingElement] = {}
        for el in out:
            key = _orbit_key(el)
            if key not in seen:
                seen[key] = el
        out = list(seen.values())
    out.sort(key=lambda e: (e.height, abs(e.a), abs(e.b)))
    return out


def units(D: int) -> list[tuple[int, int]]:
    """The unit group of the order of discriminant D (as (a, b) coordinates)."""
    us = [(1, 0), (-1, 0)]
    if D == -4:
        us += [(x, y) for x in range(-2, 3) for y in range(-2, 3)
               if (x, y) not in ((1, 0), (-1, 0)) and norm(D, x, y) == 1]
    elif D == -3:
        us += [(x, y) for x in range(-3, 4) for y in range(-3, 4)
               if (x, y) not in ((1, 0), (-1, 0)) and norm(D, x, y) == 1]
    return us


def minimal_representative(el: RingElement) -> RingElement:
    """The least-height element in the {units} x {conjugation} orbit of el."""
    best = el
    for base in ((el.a, el.b), conjugate(el.D, el.a, el.b)):
        for u in units(el.D):
            a, b = multiply(el.D, base, u)
            cand = RingElement(el.D, a, b)
            if (cand.height, abs(cand.a), abs(cand.b)) < (best.height, abs(best.a), abs(best.b)):
                best = cand
    return best


def _orbit_key(el: RingElement) -> tuple[int, int]:
    cands = []
    for base in ((el.a, el.b), conjugate(el.D, el.a, el.b)):
        for u in units(el.D):
            cands.append(multiply(el.D, base, u))
    return min(cands)


def smallest_principal_power(D: int, ell: int, kmax: int = 64) -> RingElement | None:
    """Least k <= kmax with a PRIMITIVE element of norm ell^k, and that element.

    Such an element is a cyclic endomorphism of degree ell^k: a closed walk of
    k steps on the ell-isogeny graph that starts and ends at the curve, i.e.
    the generator of the first principal power of a prime ideal above ell.
    k is the order of that ideal class (computed by composition of binary
    quadratic forms); the generator is then found by Cornacchia's algorithm,
    never by brute force.  Returns None if ell is inert or k > kmax.
    """
    chi = kronecker_symbol_disc(D, ell)
    if chi == -1:
        return None
    if chi == 0:
        # ramified: the prime above ell squares to (ell); primitive powers
        # exist only at k = 1 (if principal) -- check directly.
        els = elements_of_norm(D, ell, primitive_only=True)
        return min(els, key=lambda e: e.height) if els else None
    k = prime_ideal_class_order(D, ell, kmax)
    if k is None:
        return None
    el = cornacchia_element(D, ell ** k)
    if el is not None:
        el = minimal_representative(el)
    if el is None or not el.primitive:
        # The class order says a primitive element of this norm exists; if the
        # search did not surface one, fall back to the exhaustive search for
        # small norms only, else report the gap honestly.
        if ell ** k < 10 ** 12:
            els = elements_of_norm(D, ell ** k, primitive_only=True)
            return min(els, key=lambda e: e.height) if els else None
        return None
    return el


# ---------------------------------------------------------------------------
# binary quadratic forms: class order of a prime ideal
# ---------------------------------------------------------------------------

def reduce_form(a: int, b: int, c: int) -> tuple[int, int, int]:
    """Reduced representative of the positive definite form (a, b, c)."""
    while True:
        if c < a or (c == a and b < 0):
            a, b, c = c, -b, a
            continue
        if -a < b <= a:
            if a == c and b < 0:
                b = -b
            return a, b, c
        # normalise b into (-a, a]
        r = b % (2 * a)
        if r > a:
            r -= 2 * a
        c = (r * r - (b * b - 4 * a * c)) // (4 * a)
        b = r


def _ext_gcd(x: int, y: int) -> tuple[int, int, int]:
    if y == 0:
        return (abs(x), 1 if x >= 0 else -1, 0)
    g, u, v = _ext_gcd(y, x % y)
    return g, v, u - (x // y) * v


def compose_forms(f1: tuple[int, int, int], f2: tuple[int, int, int]) -> tuple[int, int, int]:
    """Gauss composition of primitive forms of the same discriminant (Cohen 5.4.7)."""
    a1, b1, c1 = f1
    a2, b2, c2 = f2
    D = b1 * b1 - 4 * a1 * c1
    assert D == b2 * b2 - 4 * a2 * c2
    if a1 > a2:
        a1, b1, c1, a2, b2, c2 = a2, b2, c2, a1, b1, c1
    s = (b1 + b2) // 2
    nn = b2 - s
    d, u, v = _ext_gcd(a1, s)     # d = u a1 + v s
    if a2 % d == 0:
        y1 = 0
        y2 = -1
        x2 = 0
        dd = d
    else:
        dd, x2, y2 = _ext_gcd(a2, d)   # dd = x2 a2 + y2 d
        y1 = 0
    # Follow Cohen: d1 = gcd(a1, a2, s); d1 = u a1 + v a2 + w s.
    g1, u1, v1 = _ext_gcd(a1, a2)
    d1, x, w = _ext_gcd(g1, s)
    u = x * u1
    v = x * v1
    a3 = (a1 * a2) // (d1 * d1)
    # b3 = b2 + 2 (a2/d1) * ( ... ) -- use the standard formula
    # b3 = (u a1 b2 + v a2 b1 + w (b1 b2 + D)/2) / d1  (mod 2 a3)
    b3 = (u * a1 * b2 + v * a2 * b1 + w * ((b1 * b2 + D) // 2)) // d1
    b3 %= 2 * a3
    c3 = (b3 * b3 - D) // (4 * a3)
    return reduce_form(a3, b3, c3)


def principal_form(D: int) -> tuple[int, int, int]:
    if D % 4 == 0:
        return reduce_form(1, 0, -D // 4)
    return reduce_form(1, 1, (1 - D) // 4)


def prime_form(D: int, ell: int) -> tuple[int, int, int] | None:
    """A form (ell, b, c) of discriminant D, i.e. a prime ideal above ell."""
    for b in range(0, 2 * ell):
        if (b * b - D) % (4 * ell) == 0:
            return reduce_form(ell, b, (b * b - D) // (4 * ell))
    return None


def prime_ideal_class_order(D: int, ell: int, kmax: int = 64) -> int | None:
    f = prime_form(D, ell)
    if f is None:
        return None
    one = principal_form(D)
    g = f
    for k in range(1, kmax + 1):
        if g == one:
            return k
        g = compose_forms(g, f)
    return None


# ---------------------------------------------------------------------------
# Cornacchia: an element of prescribed norm without brute force
# ---------------------------------------------------------------------------

def _sqrt_mod_prime_power(a: int, ell: int, k: int) -> list[int]:
    """All square roots of a modulo ell^k (ell prime), by Hensel lifting."""
    from sympy.ntheory import sqrt_mod
    a %= ell ** k
    if ell == 2:
        roots = {r for r in range(8) if (r * r - a) % 8 == 0} if k >= 3 else \
                {r for r in range(2 ** k) if (r * r - a) % (2 ** k) == 0}
        mod = 8 if k >= 3 else 2 ** k
        j = 3 if k >= 3 else k
        while j < k:
            nxt = set()
            for r in roots:
                for cand in (r, r + mod):
                    if (cand * cand - a) % (2 * mod) == 0:
                        nxt.add(cand % (2 * mod))
            roots, mod, j = nxt, 2 * mod, j + 1
        return sorted(roots)
    r0 = sqrt_mod(a % ell, ell, all_roots=True)
    if not r0:
        return []
    roots = set(r0)
    mod = ell
    for _ in range(1, k):
        nxt = set()
        for r in roots:
            # r' = r - (r^2 - a) / (2r) mod ell*mod
            if r % ell == 0:
                continue
            inv = pow(2 * r, -1, ell * mod)
            nxt.add((r - (r * r - a) * inv) % (ell * mod))
        roots, mod = nxt, ell * mod
    return sorted(roots)


def cornacchia_element(D: int, N: int) -> RingElement | None:
    """An element of norm N in the order of discriminant D (modified Cornacchia).

    Cohen, Algorithm 1.5.3, applied to N = ell^k: with x0 a square root of D
    modulo N whose parity matches D, the Euclidean reduction of (2N, x0) down
    to 2*sqrt(N) yields x with x^2 + |D| y^2 = 4N when a solution with
    gcd(y, ell) = 1 exists; the element is then (x + y*sqrt(D))/2, i.e.
    a + b*omega with b = y and a = (x - y*tau)/2.  Every square root mod N is
    tried, so a principal ideal of norm N is found whenever one exists and
    N is coprime to D (for a prime dividing D use ``elements_of_norm``,
    which is what ``smallest_principal_power`` does in the ramified case).
    """
    from sympy import factorint
    from sympy.ntheory.modular import crt
    fac = factorint(N)
    root_sets, moduli = [], []
    for pr, e in fac.items():
        rs = _sqrt_mod_prime_power(D, pr, e)
        if not rs:
            return None
        root_sets.append(rs)
        moduli.append(pr ** e)
    import itertools
    absD = -D
    tau = omega_trace_norm(D)[0]
    lim = isqrt(4 * N)
    for combo in itertools.product(*root_sets):
        r = int(crt(moduli, list(combo))[0]) if len(moduli) > 1 else int(combo[0])
        for x0 in {r % N, (-r) % N}:
            if (x0 - D) % 2:
                x0 = N - x0
            a_, b_ = 2 * N, x0
            while b_ > lim:
                a_, b_ = b_, a_ % b_
            x = b_
            rem = 4 * N - x * x
            if rem < 0 or rem % absD:
                continue
            y2 = rem // absD
            y = isqrt(y2)
            if y * y != y2 or y == 0:
                continue
            for sx in (x, -x):
                twice_a = sx - y * tau
                if twice_a % 2 == 0:
                    el = RingElement(D, twice_a // 2, y)
                    if el.norm == N:
                        return el
    return None


def kronecker_symbol_disc(D: int, ell: int) -> int:
    """(D / ell): +1 split, -1 inert, 0 ramified, for an odd or even prime ell."""
    from sympy import jacobi_symbol
    if ell == 2:
        r = D % 8
        if r in (1,):
            return 1
        if r in (5,):
            return -1
        return 0
    return int(jacobi_symbol(D % ell, ell))
