"""Small exact EC arithmetic and relation rank; no ML or hidden-log oracle."""
from __future__ import annotations

from dataclasses import dataclass
import math

Point = tuple[int, int] | None


def is_prime(n):
    return type(n) is int and n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int
    n: int
    h: int
    g: Point

    def __post_init__(self):
        if not 3 < self.p <= 251 or not is_prime(self.p) or not is_prime(self.n) or self.n < 5:
            raise ValueError("prime field of characteristic >3 and prime subgroup >=5 required")
        if not (0 <= self.a < self.p and 0 <= self.b < self.p) or self.h < 1:
            raise ValueError("noncanonical curve parameters")
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular curve")
        # With n occurring once in #E(Fp), n-torsion is a unique cyclic subgroup.
        order = 1
        for x in range(self.p):
            rhs = (x*x*x + self.a*x + self.b) % self.p
            order += 1 if rhs == 0 else 2 if pow(rhs, (self.p-1)//2, self.p) == 1 else 0
        if order != self.n*self.h or self.h % self.n == 0:
            raise ValueError("incorrect cofactor or ambiguous full n-torsion subgroup")
        if self.g is None or not self.on_curve(self.g) or self.mul(self.n, self.g) is not None:
            raise ValueError("invalid prime-order generator")

    def on_curve(self, point):
        if point is None:
            return True
        return (isinstance(point, tuple) and len(point) == 2
                and all(type(v) is int and 0 <= v < self.p for v in point)
                and (point[1]**2 - point[0]**3 - self.a * point[0] - self.b) % self.p == 0)

    def neg(self, point):
        return None if point is None else (point[0], -point[1] % self.p)

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        if x == u and (y + v) % self.p == 0:
            return None
        slope = ((3*x*x + self.a) * pow(2*y, -1, self.p) if left == right
                 else (v-y) * pow(u-x, -1, self.p)) % self.p
        xx = (slope*slope - x - u) % self.p
        return xx, (slope*(x-xx) - y) % self.p

    def mul(self, scalar, point):
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result = None
        while scalar:
            if scalar & 1:
                result = self.add(result, point)
            point = self.add(point, point)
            scalar >>= 1
        return result

    def check_subgroup(self, point):
        if not self.on_curve(point) or self.mul(self.n, point) is not None:
            raise ValueError("point is outside the declared prime subgroup")

    def key(self, point):
        if point is None:
            return None, 1
        opposite = self.neg(point)
        return (point, 1) if point <= opposite else (opposite, -1)


class RelationSystem:
    """Verify point equations, then solve unknown logs modulo prime n.

    Terms are (coefficient, point); constant is the coefficient of G.
    Equal points and negatives share a log variable. Recovery needs a singleton
    row in reduced echelon form, not just a large total rank.
    """
    def __init__(self, curve, seeds, targets):
        self.curve = curve
        self.targets = targets
        self.known_key, self.known_sign = curve.key(curve.g)
        keys = set()
        for point in [*seeds, *targets.values()]:
            curve.check_subgroup(point)
            key, _ = curve.key(point)
            if key is not None and key != self.known_key:
                keys.add(key)
        self.columns = {key: i for i, key in enumerate(sorted(keys))}
        self.basis = {}
        self.verified = 0
        self.dependent = 0
        self.group_calls = 0
        self._recovery_cache = None

    def _mul(self, scalar, point):
        # Count explicit double-and-add calls, including identity additions.
        result = None
        if scalar < 0:
            scalar, point = -scalar, self.curve.neg(point)
        while scalar:
            if scalar & 1:
                result = self.curve.add(result, point)
                self.group_calls += 1
            point = self.curve.add(point, point)
            self.group_calls += 1
            scalar >>= 1
        return result

    def insert(self, terms, constant=0):
        if type(constant) is not int or any(type(c) is not int for c, _ in terms):
            raise ValueError("integer point coefficients required")
        witness = self._mul(constant, self.curve.g)
        row = [0] * (len(self.columns) + 1)
        known = constant
        for coefficient, point in terms:
            self.curve.check_subgroup(point)
            key, sign = self.curve.key(point)
            if key is not None and key != self.known_key and key not in self.columns:
                raise ValueError("unregistered unknown point")
            witness = self.curve.add(witness, self._mul(coefficient, point))
            self.group_calls += 1
            if key == self.known_key:
                known += coefficient * sign * self.known_sign
            elif key is not None:
                row[self.columns[key]] += coefficient * sign
        if witness is not None:
            raise ValueError("false elliptic-curve relation")
        self.verified += 1
        n = self.curve.n
        row[-1] = -known
        row = [v % n for v in row]
        for pivot, old in sorted(self.basis.items()):
            factor = row[pivot]
            row = [(x - factor*y) % n for x, y in zip(row, old)]
        pivot = next((i for i, v in enumerate(row[:-1]) if v), None)
        if pivot is None:
            if row[-1]:
                raise ValueError("inconsistent log relation")
            self.dependent += 1
            return 0
        inverse = pow(row[pivot], -1, n)
        row = [v * inverse % n for v in row]
        for i, old in list(self.basis.items()):
            factor = old[pivot]
            self.basis[i] = [(x - factor*y) % n for x, y in zip(old, row)]
        self.basis[pivot] = row
        self._recovery_cache = None
        return 1

    def recoveries(self):
        if self._recovery_cache is not None:
            return dict(self._recovery_cache)
        result = {}
        for name, point in self.targets.items():
            key, sign = self.curve.key(point)
            if key is None:
                scalar = 0
            elif key == self.known_key:
                scalar = sign * self.known_sign % self.curve.n
            else:
                row = self.basis.get(self.columns[key])
                if row is None or sum(v != 0 for v in row[:-1]) != 1:
                    continue
                scalar = row[-1] * sign % self.curve.n
            if self._mul(scalar, self.curve.g) != point:
                raise ValueError("identified scalar does not verify")
            result[name] = scalar
        self._recovery_cache = dict(result)
        return result

    def summary(self):
        recovered = self.recoveries()
        return {"verified_relation_count": self.verified, "independent_rank": len(self.basis),
                "dependent_relation_count": self.dependent, "unknown_log_count": len(self.columns),
                "verified_target_scalars": recovered, "target_recoveries": len(recovered),
                "verification_group_calls": self.group_calls,
                "rank_per_1000_verification_calls": 1000*len(self.basis)/max(1, self.group_calls)}


def bsgs(curve, target):
    """Exact generic comparator; calls count explicit group additions."""
    curve.check_subgroup(target)
    m = math.isqrt(curve.n) + 1
    table, point, calls = {}, None, 0
    for j in range(m):
        table.setdefault(point, j)
        point = curve.add(point, curve.g)
        calls += 1
    step = curve.neg(point)
    point = target
    for i in range(m):
        if point in table:
            scalar = (i*m + table[point]) % curve.n
            if curve.mul(scalar, curve.g) != target:
                raise ValueError("BSGS scalar failed verification")
            return {"scalar": scalar, "search_group_calls": calls, "table_entries": len(table),
                    "scope": "Search calls exclude scalar verification and subgroup admission."}
        point = curve.add(point, step)
        calls += 1
    raise ValueError("no discrete log in admitted prime subgroup")
