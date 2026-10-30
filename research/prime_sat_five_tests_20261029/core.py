"""Exact sparse arithmetic in F_p[b]/(b_i**2-b_i).

Bit masks denote squarefree monomials. All restrictions preserve variable
indices. This is a finite Boolean quotient, not a claim about homogeneous
degree of regularity. No elliptic-curve witness enters instance construction.
"""
from dataclasses import dataclass, field


@dataclass
class BoolRing:
    n: int
    p: int
    counts: dict = field(default_factory=lambda: {"coefficient_additions": 0,
                                                "coefficient_multiplications": 0})

    def clean(self, a):
        return {int(m): int(c) % self.p for m, c in a.items() if c % self.p}

    def const(self, c):
        return self.clean({0: c})

    def var(self, i):
        if not 0 <= i < self.n:
            raise ValueError("variable index outside ring")
        return {1 << i: 1}

    def add(self, a, b):
        out = dict(a)
        for m, c in b.items():
            out[m] = (out.get(m, 0) + c) % self.p
            self.counts["coefficient_additions"] += 1
        return self.clean(out)

    def scale(self, a, c):
        self.counts["coefficient_multiplications"] += len(a)
        return self.clean({m: c * v for m, v in a.items()})

    def sub(self, a, b):
        return self.add(a, self.scale(b, -1))

    def mul(self, a, b):
        out = {}
        for m, c in a.items():
            for k, v in b.items():
                out[m | k] = (out.get(m | k, 0) + c * v) % self.p
                self.counts["coefficient_additions"] += 1
                self.counts["coefficient_multiplications"] += 1
        return self.clean(out)

    def restrict(self, poly, assignments):
        ones = sum(1 << int(i) for i, v in assignments.items() if v == 1)
        zeros = sum(1 << int(i) for i, v in assignments.items() if v == 0)
        if any(v not in (0, 1) or not 0 <= int(i) < self.n for i, v in assignments.items()):
            raise ValueError("restriction must assign Boolean ring variables")
        out = {}
        for m, c in poly.items():
            if not m & zeros:
                k = m & ~ones
                out[k] = (out.get(k, 0) + c) % self.p
        return self.clean(out)

    def eval(self, poly, bits):
        if not isinstance(bits, int):
            bits = sum(int(b) << i for i, b in enumerate(bits))
        return sum(c for m, c in poly.items() if m & bits == m) % self.p

    evaluate = eval

    @staticmethod
    def degree(poly):
        return max((m.bit_count() for m in poly), default=-1)

    def from_values(self, values):
        if len(values) != 1 << self.n:
            raise ValueError("truth table size does not match ring")
        a = [int(v) % self.p for v in values]
        for i in range(self.n):
            for mask in range(1 << self.n):
                if mask & (1 << i):
                    a[mask] = (a[mask] - a[mask ^ (1 << i)]) % self.p
        return self.clean(dict(enumerate(a)))


def generate_s3(p, s, target, a=1, b=1, curve_membership=False):
    if (1 << s) > p or (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError("distinct digit values and nonsingular curve required")
    ring = BoolRing(2 * s, p)
    x, y = {}, {}
    for i in range(s):
        x = ring.add(x, ring.scale(ring.var(i), 1 << i))
        y = ring.add(y, ring.scale(ring.var(s + i), 1 << i))
    add, mul, sub, scale, const = ring.add, ring.mul, ring.sub, ring.scale, ring.const
    xy = mul(x, y)
    diff = sub(x, y)
    summ = add(x, y)
    f = add(sub(scale(mul(diff, diff), target**2),
                scale(add(mul(summ, add(xy, const(a))), const(2*b)), 2*target)),
            sub(mul(sub(xy, const(a)), sub(xy, const(a))), scale(summ, 4*b)))
    polynomials, labels = [f], ["S3"]
    if curve_membership:
        for start in (0, s):
            values = []
            for mask in range(1 << (2*s)):
                xx = (mask >> start) & ((1 << s) - 1)
                rhs = (xx**3 + a*xx + b) % p
                values.append(int(rhs != 0 and pow(rhs, (p-1)//2, p) != 1))
            polynomials.append(ring.from_values(values))
            labels.append("curve_x_membership_" + str(start // s))
    return {"ring": ring, "polynomials": polynomials,
            "variable_blocks": [list(range(s)), list(range(s, 2*s))],
            "labels": labels, "metadata": {"p": p, "s": s, "target": target,
            "a": a, "b": b, "curve_membership": curve_membership,
            "scope": "Boolean residual, not full ECDLP"}}


def refute(ring, generators, degree_cap, row_cap=4096):
    """Degree-bounded PC search with exact multiplier certificates.

    Every accepted row is recursively multiplied by every variable, so this
    is a bounded Boolean polynomial-calculus search, not just XL's initial
    generator multiples. This selected echelon-row strategy is not proved
    complete for all degree-bounded PC derivations. Exhausting its queue or
    resources returns unknown, never a non-refutability assertion.
    """
    basis, queue = {}, []
    attempted = 0
    max_degree = -1
    multipliers_degree = -1
    answer = None

    def insert(poly, cert):
        nonlocal attempted, max_degree, multipliers_degree, answer
        attempted += 1
        if attempted > row_cap:
            raise OverflowError("row cap")
        poly = ring.clean(poly)
        if ring.degree(poly) > degree_cap:
            return
        max_degree = max(max_degree, ring.degree(poly))
        while poly:
            pivot = max(poly, key=lambda m: (m.bit_count(), m))
            if pivot not in basis:
                inv = pow(poly[pivot], -1, ring.p)
                poly = ring.scale(poly, inv)
                cert = [ring.scale(c, inv) for c in cert]
                basis[pivot] = (poly, cert)
                queue.append((poly, cert))
                multipliers_degree = max(multipliers_degree, *(ring.degree(c) for c in cert))
                if pivot == 0:
                    answer = cert
                return
            old, oldcert = basis[pivot]
            c = poly[pivot]
            poly = ring.sub(poly, ring.scale(old, c))
            cert = [ring.sub(x, ring.scale(y, c)) for x, y in zip(cert, oldcert)]

    capped = False
    try:
        for i, f in enumerate(generators):
            cert = [{} for _ in generators]
            cert[i] = {0: 1}
            insert(f, cert)
            if answer is not None:
                break
        cursor = 0
        while answer is None and cursor < len(queue):
            poly, cert = queue[cursor]
            cursor += 1
            for i in range(ring.n):
                v = ring.var(i)
                insert(ring.mul(poly, v), [ring.mul(c, v) for c in cert])
                if answer is not None:
                    break
    except OverflowError:
        capped = True
    return {"status": "refuted" if answer is not None else "unknown",
            "closure_complete": not capped and answer is None,
            "closure_complete_meaning": "stored_echelon_row_strategy_exhausted_not_complete_degree_D_PC",
            "resource_capped": capped, "degree_cap": degree_cap,
            "max_accepted_row_degree": max_degree,
            "max_multiplier_degree": multipliers_degree,
            "rank": len(basis), "attempted_rows": attempted,
            "certificate": answer}


def check_refutation(p, n, generators, certificate):
    """Recompute certificate identity without elimination history."""
    if certificate is None or len(certificate) != len(generators):
        return False
    ring = BoolRing(n, p)
    total = {}
    for q, f in zip(certificate, generators):
        total = ring.add(total, ring.mul(ring.clean(q), ring.clean(f)))
    return total == {0: 1}
