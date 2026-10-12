"""Conway polynomials C(2,n) computed from the definition (lexicographically
least monic primitive polynomial, coefficients compared from x^(n-1) down with
0 < 1, compatible with C(2,d) for every proper divisor d of n). Used to supply
the field modulus Sage chooses by default for GF(2^n) (verified in Stage 1 by
hash match against EXP-DREG-001)."""
from functools import lru_cache
from semaev_core import is_irreducible


def pmulmod(a, b, poly, n):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> n:
            a ^= poly
    return r


def ppow(a, e, poly, n):
    r = 1
    while e:
        if e & 1:
            r = pmulmod(r, a, poly, n)
        a = pmulmod(a, a, poly, n)
        e >>= 1
    return r


def factors(m):
    f, d = set(), 2
    while d * d <= m:
        while m % d == 0:
            f.add(d); m //= d
        d += 1
    if m > 1:
        f.add(m)
    return f


def is_primitive(poly, n):
    if not is_irreducible(poly, n):
        return False
    order = (1 << n) - 1
    return all(ppow(2, order // q, poly, n) != 1 for q in factors(order))


def eval_poly_at(c, x, poly, n):
    """evaluate polynomial c (int, bit i = coeff of X^i) at field element x mod poly."""
    r, pw = 0, 1
    i = 0
    while c >> i:
        if (c >> i) & 1:
            r ^= pw
        pw = pmulmod(pw, x, poly, n)
        i += 1
    return r


@lru_cache(None)
def conway(n):
    if n == 1:
        return 0b11
    divs = [d for d in range(1, n) if n % d == 0]
    # enumerate candidates in Conway order: compare coefficient of x^(n-1) first, 0 < 1
    for idx in range(1 << n):
        # idx bits from MSB: coefficient x^(n-1) is the most significant bit of idx
        low = 0
        for i in range(n):
            if (idx >> (n - 1 - i)) & 1:
                low |= 1 << (n - 1 - i)
        poly = (1 << n) | low
        if not (poly & 1):
            continue
        if not is_primitive(poly, n):
            continue
        ok = True
        for d in divs:
            e = ((1 << n) - 1) // ((1 << d) - 1)
            xe = ppow(2, e, poly, n)
            if eval_poly_at(conway(d), xe, poly, n) != 0:
                ok = False
                break
        if ok:
            return poly
    raise RuntimeError(n)


if __name__ == "__main__":
    for n in (2, 3, 4, 6, 8, 12, 5, 15):
        c = conway(n)
        print(n, bin(c), " + ".join(f"x^{i}" for i in range(n, -1, -1) if (c >> i) & 1))
