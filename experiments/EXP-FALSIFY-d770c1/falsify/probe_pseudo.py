"""Probe 3: the H-PSEUDO character-sum constant C(p).

The corpus records THREE mutually inconsistent characterisations of the same
quantity, none superseding the others:

  KN-FIND-d4f820  C(p) ~ p^0.055   (title, "4-point scaling")
  KN-FIND-e7a3b1  C(p) ~ p^0.079   ("empirically", used to frame the conjecture)
  KN-FIND-4c9e71  max C ~ O(1) ~ 4 across all tested primes p = 1009..9001

C is defined by      max_{k != 0} |sum_{P in F} e^{2 pi i k DL_G(P) / N}| <= C(p) sqrt(B)
for the small-x factor base F = {P : x(P) < t}, |F| = B.

Two things are tested, and they are different:

  (i)  IDENTIFIABILITY.  All three numbers are fitted over p in 1009..9001,
       a range of 8.9x -- well under one decade.  Across that range p^0.055
       varies by 13% and p^0.079 by 19%.  If the measurement's own scatter is
       of that order, the exponent is not identifiable and all three published
       characterisations are consistent with the same data.  That would make
       the disagreement an artifact of fitting, not a contradiction to resolve.

  (ii) NULL OBJECT.  H-PSEUDO asserts the small-x factor base behaves
       pseudorandomly.  The control is a genuinely random subset of the same
       size in the same group.  Standard probability puts its max character sum
       near sqrt(B log N), so its C is near sqrt(log N) -- which GROWS, slowly,
       and over 1009..9001 grows by about 15%, indistinguishable from p^0.06.
       If the factor base and the random null give the same C to within scatter,
       then C's apparent power law is the random baseline and carries no
       information about the factor base's arithmetic structure.
"""

import cmath
import math
import random

from . import ec


def cyclic_generator(a, b, p, rng):
    """A point generating the whole group, plus the group order, or None."""
    pts = ec.affine_points(a, b, p)
    N = len(pts) + 1
    for _ in range(60):
        P = rng.choice(pts)
        Q, order = P, 1
        while Q is not None and order <= N:
            Q = ec.add_points(Q, P, a, p)
            order += 1
        if order == N:
            return P, N, pts
    return None


def dlog_table(G, a, p, N):
    """d -> point, and point -> d, by walking the subgroup once."""
    table = {}
    Q = None
    for d in range(N):
        table[Q] = d
        Q = ec.add_points(Q, G, a, p)
    return table


def max_character_sum(dls, N):
    """max over k != 0 of |sum_{d in dls} omega^{k d}|, omega = e^{2 pi i / N}."""
    base = 2j * math.pi / N
    best = 0.0
    for k in range(1, N):
        s = 0j
        kb = k * base
        for d in dls:
            s += cmath.exp(kb * d)
        m = abs(s)
        if m > best:
            best = m
    return best


def probe_pseudo(primes, b_frac, seed):
    rng = random.Random(seed)
    rows = []
    for p in primes:
        found = None
        for _ in range(300):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            g = cyclic_generator(a, b, p, rng)
            if g:
                found = (a, b) + g
                break
        if not found:
            continue
        a, b, G, N, pts = found
        table = dlog_table(G, a, p, N)

        B = max(8, int(round(b_frac * N)))
        # factor base: the B points of smallest x-coordinate
        by_x = sorted((P for P in pts), key=lambda P: (P[0], P[1]))[:B]
        fb_dls = [table[P] for P in by_x if P in table]

        # NULL OBJECT: a uniformly random subset of the same size
        null_dls = rng.sample(range(N), len(fb_dls))

        rb = math.sqrt(len(fb_dls))
        c_fb = max_character_sum(fb_dls, N) / rb
        c_null = max_character_sum(null_dls, N) / rb
        rows.append({
            'p': p, 'N': N, 'a': a, 'b': b, 'B': len(fb_dls),
            'C_factorbase': c_fb,
            'C_random_null': c_null,
            'sqrt_log_N': math.sqrt(math.log(N)),
        })
    return rows


def fit_exponent(rows, key):
    """Least-squares slope of log C against log p."""
    n = len(rows)
    if n < 2:
        return None
    xs = [math.log(r['p']) for r in rows]
    ys = [math.log(r[key]) for r in rows]
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
