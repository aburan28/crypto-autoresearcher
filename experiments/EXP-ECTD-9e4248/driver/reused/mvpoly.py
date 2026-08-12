"""
mvpoly.py -- minimal sparse multivariate polynomial arithmetic over F_p, and a
from-scratch Buchberger Groebner-basis algorithm with degree-of-computation
tracking, plus a Macaulay-matrix rank-defect scanner. No external CAS dependency:
this is the actual instrument whose correctness the CTRL-PLANTED-OUTLIER control
gates (see spec decision_table / stopping_rules).

Monomial order: graded reverse lexicographic (grevlex) on a fixed variable tuple.
Polynomial representation: dict {monomial_exponent_tuple: coeff mod p}, coeff != 0.
"""
from itertools import combinations_with_replacement


class MPoly:
    __slots__ = ("terms", "nvars", "p")

    def __init__(self, terms, nvars, p):
        self.terms = {m: (c % p) for m, c in terms.items() if (c % p) != 0}
        self.nvars = nvars
        self.p = p

    @staticmethod
    def zero(nvars, p):
        return MPoly({}, nvars, p)

    @staticmethod
    def constant(c, nvars, p):
        return MPoly({(0,) * nvars: c % p}, nvars, p)

    @staticmethod
    def var(i, nvars, p, coeff=1):
        e = [0] * nvars
        e[i] = 1
        return MPoly({tuple(e): coeff % p}, nvars, p)

    def is_zero(self):
        return len(self.terms) == 0

    def add(self, other):
        p = self.p
        out = dict(self.terms)
        for m, c in other.terms.items():
            out[m] = (out.get(m, 0) + c) % p
        return MPoly(out, self.nvars, p)

    def sub(self, other):
        p = self.p
        out = dict(self.terms)
        for m, c in other.terms.items():
            out[m] = (out.get(m, 0) - c) % p
        return MPoly(out, self.nvars, p)

    def scale(self, c):
        p = self.p
        c %= p
        if c == 0:
            return MPoly.zero(self.nvars, p)
        return MPoly({m: (co * c) % p for m, co in self.terms.items()}, self.nvars, p)

    def mul(self, other):
        p = self.p
        out = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                m = tuple(a + b for a, b in zip(m1, m2))
                out[m] = (out.get(m, 0) + c1 * c2) % p
        return MPoly(out, self.nvars, p)

    def total_degree(self):
        if not self.terms:
            return -1
        return max(sum(m) for m in self.terms)

    def leading_monomial(self, order):
        return order.max_monomial(self.terms.keys())

    def leading_term(self, order):
        lm = self.leading_monomial(order)
        return lm, self.terms[lm]

    def evaluate(self, values):
        """values: tuple of field elements, same length as nvars."""
        p = self.p
        s = 0
        for m, c in self.terms.items():
            term = c
            for e, v in zip(m, values):
                if e:
                    term = (term * pow(v, e, p)) % p
            s = (s + term) % p
        return s

    def copy(self):
        return MPoly(dict(self.terms), self.nvars, self.p)


class GrevlexOrder:
    """Graded reverse-lexicographic order on fixed-length exponent tuples."""

    def compare(self, m1, m2):
        d1, d2 = sum(m1), sum(m2)
        if d1 != d2:
            return -1 if d1 < d2 else 1
        # reverse lex: compare from the LAST variable, SMALLER exponent wins "larger" monomial
        for e1, e2 in zip(reversed(m1), reversed(m2)):
            if e1 != e2:
                return 1 if e1 < e2 else -1
        return 0

    def max_monomial(self, monomials):
        best = None
        for m in monomials:
            if best is None or self.compare(m, best) > 0:
                best = m
        return best


def monomial_divides(m1, m2):
    return all(a <= b for a, b in zip(m1, m2))


def monomial_div(m2, m1):
    return tuple(b - a for a, b in zip(m1, m2))


def monomial_lcm(m1, m2):
    return tuple(max(a, b) for a, b in zip(m1, m2))


def monomials_up_to_degree(nvars, D):
    """All exponent tuples in `nvars` variables with total degree <= D, generated via
    stars-and-bars combinations, sorted by total degree then lexicographically."""
    out = []
    for d in range(D + 1):
        if nvars == 1:
            out.append((d,))
            continue
        # compositions of d into nvars nonnegative parts
        for cuts in combinations_with_replacement(range(d + 1), nvars - 1):
            exps = []
            prev = 0
            for c in cuts:
                exps.append(c - prev)
                prev = c
            exps.append(d - prev)
            out.append(tuple(exps))
    return out
