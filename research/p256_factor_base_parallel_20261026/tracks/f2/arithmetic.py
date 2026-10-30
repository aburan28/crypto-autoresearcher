"""Affine producer arithmetic; importing this file runs no panel."""
from hashlib import sha256

P = 2**256 - 2**224 + 2**192 + 2**96 - 1
B = int("5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b", 16)
R = int("ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551", 16)
G = (
    int("6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296", 16),
    int("4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5", 16),
)


def tick(counts, name, n=1):
    if counts is not None:
        counts[name] = counts.get(name, 0) + n


def rhs(x, a=-3, b=B):
    return (x*x*x + a*x + b) % P


def on_curve(point, a=-3, b=B):
    return point is None or (point[1]*point[1] - rhs(point[0], a, b)) % P == 0


def neg(point):
    return None if point is None else (point[0], -point[1] % P)


def add(left, right, a=-3, counts=None):
    tick(counts, "affine_add_calls")
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    z, w = right
    if x == z:
        if (y+w) % P == 0:
            return None
        tick(counts, "affine_double_branches")
        numerator, denominator = (3*x*x+a) % P, 2*y % P
    else:
        numerator, denominator = (w-y) % P, (z-x) % P
    tick(counts, "field_inversions")
    slope = numerator*pow(denominator, -1, P) % P
    xx = (slope*slope-x-z) % P
    return xx, (slope*(x-xx)-y) % P


def mul(n, point, a=-3, counts=None):
    if n < 0:
        return mul(-n, neg(point), a, counts)
    acc = None
    while n:
        if n & 1:
            acc = add(acc, point, a, counts)
        point = add(point, point, a, counts)
        n >>= 1
    return acc


def root_with_witness(value, counts=None):
    """For p=3 mod4, a nonlift gets w with w²=-value, an exact nonsquare proof."""
    value %= P
    tick(counts, "root_exponentiations")
    candidate = pow(value, (P+1)//4, P)
    square = candidate*candidate % P
    if square == value:
        return min(candidate, -candidate % P), candidate
    if not value or square != -value % P:
        raise ArithmeticError("root witness does not satisfy either character branch")
    return None, candidate


def point_from_seed(label, counts=None, cap=10000):
    rejected = []
    for counter in range(cap):
        tick(counts, "hash_to_point_draws")
        x = int.from_bytes(sha256(f"{label}:{counter}".encode()).digest(), "big") % P
        y, witness = root_with_witness(rhs(x), counts)
        if y is not None and y:
            return (x, y), rejected
        rejected.append({"counter": counter, "x": x, "witness": witness,
                         "reason": "nonlift" if y is None else "zero-y"})
    raise RuntimeError("fixed hash-to-point cap exhausted")


def map_x_chain(x, edges, counts=None):
    """None is the projective infinity value; all encountered poles are explicit."""
    for index, edge in enumerate(edges):
        if x is None:
            return None, index
        tick(counts, "rational_map_steps")
        u = (x-edge["r"]) % P
        if not u:
            return None, index
        tick(counts, "field_inversions")
        x = (u + edge["a"] + edge["b"]*pow(u, -1, P)) % P
    return x, None


def map_point_chain(point, edges, counts=None):
    for edge in edges:
        if point is None:
            return None
        x, y = point
        u = (x-edge["r"]) % P
        if not u:
            return None
        tick(counts, "rational_map_steps")
        tick(counts, "field_inversions")
        inverse = pow(u, -1, P)
        point = ((u + edge["a"] + edge["b"]*inverse) % P,
                 y*(1-edge["b"]*inverse*inverse) % P)
    return point


def raw_membership(x, family, metadata, edges, counts=None):
    if family == "Dickson_generic":
        value = x
        for _ in range(metadata["composition_depth"]):
            tick(counts, "dickson_steps")
            value = (value*value-2) % P
        return value == metadata["terminal"]
    value, _pole = map_x_chain(x, edges[:metadata["chain_length"]], counts)
    if family == "elliptic_kernel":
        return value is None
    return value is not None and value == metadata["endpoint"][0]


def signed_base(canonical):
    points = []
    for point in canonical:
        points.extend((point, neg(point)))
    if len(set(points)) != len(points):
        raise ValueError("signed base contains duplicates")
    return points


def pair_table(points, counts=None):
    """All unordered pairs, including repeats and inverse pairs."""
    table = {}
    for i, left in enumerate(points):
        for j in range(i, len(points)):
            tick(counts, "pair_table_states")
            value = add(left, points[j], counts=counts)
            table.setdefault(value, []).append((i, j))
    return table


def solve_three(target, points, table, counts=None):
    if target is None or not on_curve(target):
        raise ValueError("target must be a nonzero point on P-256")
    solutions = set()
    for k, point in enumerate(points):
        tick(counts, "third_point_lookups")
        residual = add(target, neg(point), counts=counts)
        for i, j in table.get(residual, ()):
            if j <= k:
                solutions.add((i, j, k))
    return sorted(solutions)


def classify_solutions(solutions, points):
    repeated_x = cancellation = 0
    for triple in solutions:
        values = [points[i] for i in triple]
        repeated_x += len({point[0] for point in values}) < 3
        cancellation += any(values[i] == neg(values[j])
                            for i in range(3) for j in range(i+1, 3))
    return {"solutions": len(solutions), "repeated_coordinate_solutions": repeated_x,
            "cancellation_solutions": cancellation}
