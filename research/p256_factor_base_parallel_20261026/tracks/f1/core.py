"""Pure definitions for the released F1 computation; importing runs no panel."""
import ast
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parents[1]
REPO = HERE.parents[3]
OLD = REPO / "research/p256_factor_base_parallel_20261025"


class ExtractionUnknown(RuntimeError):
    pass


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_once(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True)
        stream.write("\n")


def expression(text, names):
    """Read the frozen arithmetic-only S4 coefficient expressions."""
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Pow) and type(right) is int and 0 <= right <= 12:
                return left ** right
        raise ValueError("Unadmitted coefficient expression")
    return walk(ast.parse(text, mode="eval"))


def poly_add(left, right, p):
    result = dict(left)
    for exponent, coefficient in right.items():
        value = (result.get(exponent, 0) + coefficient) % p
        if value:
            result[exponent] = value
        else:
            result.pop(exponent, None)
    return result


def poly_scale(poly, coefficient, p):
    return {e: v * coefficient % p for e, v in poly.items() if v * coefficient % p}


def poly_multiply(left, right, p):
    result = {}
    for a, av in left.items():
        for b, bv in right.items():
            exponent = tuple(x + y for x, y in zip(a, b))
            result[exponent] = (result.get(exponent, 0) + av * bv) % p
    return {e: v for e, v in result.items() if v}


def poly_power(poly, exponent, p, width):
    result = {(0,) * width: 1}
    for _ in range(exponent):
        result = poly_multiply(result, poly, p)
    return result


def elementary_polynomials(slot_map, p):
    width = max(slot_map) + 1
    slots = [{tuple(int(j == index) for j in range(width)): 1} for index in slot_map]
    result = []
    for degree in range(1, 4):
        total = {}
        for indices in itertools.combinations(range(3), degree):
            term = {(0,) * width: 1}
            for i in indices:
                term = poly_multiply(term, slots[i], p)
            total = poly_add(total, term, p)
        result.append(total)
    return result


def relation_polynomial(parameters, target_x, slot_map):
    p = parameters["p"]
    width = max(slot_map) + 1
    generators = elementary_polynomials(slot_map, p)
    source = json.loads((OLD / "baseline/s4-symmetric.json").read_text())
    result = {}
    names = {"a": parameters["a"], "b": parameters["b"], "t": target_x}
    for exponents, text in source["terms"]:
        term = {(0,) * width: expression(text, names) % p}
        for variable, exponent in zip(generators, exponents):
            term = poly_multiply(term, poly_power(variable, exponent, p, width), p)
        result = poly_add(result, term, p)
    return result, generators


def elementary(values, p):
    x, y, z = values
    return ((x + y + z) % p, (x * y + x * z + y * z) % p, x * y * z % p)


def multiplicity(values):
    return tuple(sorted(Counter(values).values(), reverse=True))


class AffineCurve:
    """Producer arithmetic; the reference has separate Jacobian formulas."""
    def __init__(self, parameters):
        self.p, self.a, self.b = (parameters[k] for k in ("p", "a", "b"))
        self.counts = Counter()

    def add(self, point, other):
        self.counts["affine_add_calls"] += 1
        if point is None:
            return other
        if other is None:
            return point
        x, y = point
        u, v = other
        if x == u:
            if (y + v) % self.p == 0:
                return None
            numerator, denominator = 3 * x * x + self.a, 2 * y
        else:
            numerator, denominator = v - y, u - x
        self.counts["affine_inversions"] += 1
        slope = numerator * pow(denominator, -1, self.p) % self.p
        X = (slope * slope - x - u) % self.p
        return X, (slope * (x - X) - y) % self.p

    def multiply(self, n, point):
        value = None
        while n:
            if n & 1:
                value = self.add(value, point)
            point = self.add(point, point)
            n >>= 1
        return value

    def lifts(self, x):
        self.counts["sqrt_requests"] += 1
        f = (x ** 3 + self.a * x + self.b) % self.p
        y = pow(f, (self.p + 1) // 4, self.p)
        if y * y % self.p != f:
            return []
        return sorted({(x % self.p, y), (x % self.p, -y % self.p)})

    def valid(self, point):
        return point is None or ((point[1] ** 2 - point[0] ** 3 - self.a * point[0] - self.b) % self.p == 0)


def chain_value(x, depth, p):
    for _ in range(depth):
        x = (x * x - 2) % p
    return x


def primary_domain(depth, terminal, p):
    """Used only by the explicitly enumerative arity-four control."""
    roots = {terminal}
    for _ in range(depth):
        next_roots = set()
        for value in roots:
            radicand = (value + 2) % p
            x = pow(radicand, (p + 1) // 4, p)
            if x * x % p == radicand:
                next_roots.update((x, -x % p))
        roots = next_roots
    return sorted(roots)


def signed_recovery(states, depth, terminal, target, parameters, wanted):
    curve = AffineCurve(parameters)
    p = parameters["p"]
    solutions = set()
    recovered = []
    from flint import fmpz_mod_poly_ctx
    polynomial = fmpz_mod_poly_ctx(p)
    for state in states:
        u, v, w = state
        factors = polynomial([-w, v, -u, 1]).roots()
        roots = tuple(sorted(int(x) for x, count in factors for _ in range(count)))
        if len(roots) != 3 or multiplicity(roots) != wanted:
            raise ExtractionUnknown("A rational character did not recover its claimed cubic stratum")
        if any(chain_value(x, depth, p) != terminal for x in roots):
            raise AssertionError("Recovered coordinate does not satisfy the original chain")
        assert elementary(roots, p) == tuple(state)
        for x in set(roots):
            for point in curve.lifts(x):
                assert curve.valid(point)
                assert curve.multiply(parameters["r"], point) is None
        choices = [curve.lifts(x) for x in roots]
        for points in itertools.product(*choices):
            value = None
            for point in points:
                value = curve.add(value, point)
            if value == target:
                solutions.add(tuple(sorted(points)))
        recovered.append({"symmetric": list(state), "roots": list(roots), "multiplicity": list(wanted)})
    return sorted(solutions), recovered, dict(curve.counts)
