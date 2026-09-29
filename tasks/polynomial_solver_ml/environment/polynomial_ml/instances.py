"""Deterministic synthetic inputs and an independent scalar root oracle."""

from __future__ import annotations

import hashlib
import json
import math
import random

MAX_PRIME = 31
ALLOWED_PRIMES = (7, 11, 13, 17, 19, 23, 29, 31)
FAMILIES = ("dense_quadratic", "sparse_cubic", "triangular")
FEATURE_NAMES = (
    "log_prime", "terms", "mean_degree", "max_degree", "mixed_fraction",
    "linear_fraction", "constant_fraction", "coefficient_mean",
    "coefficient_std", "x_degree", "y_degree", "term_imbalance",
)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _poly(rng, support, p, root):
    terms = [[rng.randrange(1, p), x, y] for x, y in support]
    constant = -sum(c * pow(root[0], x, p) * pow(root[1], y, p) for c, x, y in terms) % p
    if constant:
        terms.append([constant, 0, 0])
    return sorted(terms, key=lambda t: (t[1], t[2]), reverse=True)


def make_case(p: int, family: str, seed: int, index: int, split: str):
    if p not in ALLOWED_PRIMES or family not in (*FAMILIES, "dense_cubic"):
        raise ValueError("unsupported generated system family or prime")
    digest = hashlib.sha256(canonical([seed, p, family, index])).digest()
    rng = random.Random(int.from_bytes(digest, "big"))
    root = [rng.randrange(p), rng.randrange(p)]
    quadratic = [(2, 0), (1, 1), (0, 2), (1, 0), (0, 1)]
    cubic = [(x, y) for x in range(4) for y in range(4 - x) if 0 < x + y <= 3]
    if family == "dense_quadratic":
        supports = [quadratic, quadratic]
    elif family == "sparse_cubic":
        supports = [[(3, 0), (0, 3), (1, 1), (1, 0)], [(2, 1), (1, 2), (1, 0), (0, 1)]]
    elif family == "triangular":
        supports = [[(2, 0), (1, 0)], [(0, 2), (1, 1), (1, 0), (0, 1)]]
    else:
        supports = [cubic, cubic]
    polynomials = [_poly(rng, support, p, root) for support in supports]
    identity = {"prime": p, "polynomials": polynomials}
    return {**identity, "id": hashlib.sha256(canonical(identity)).hexdigest(),
            "family": family, "split": split, "planted_root": root, "index": index}


def generate_cases(profile="quick", seed=20260904):
    if profile == "quick":
        schedule = [("train", (7, 11), FAMILIES, 2),
                    ("validation", (13,), FAMILIES, 1),
                    ("test", (17, 19), FAMILIES, 1),
                    ("test_unseen_family", (17, 19), ("dense_cubic",), 1)]
    elif profile == "standard":
        schedule = [("train", (7, 11, 13), FAMILIES, 4),
                    ("validation", (17,), FAMILIES, 2),
                    ("test", (19, 23), FAMILIES, 2),
                    ("test_unseen_family", (19, 23), ("dense_cubic",), 2)]
    else:
        raise ValueError("profile must be quick or standard")
    cases = [make_case(p, family, seed, i, split)
             for split, primes, families, count in schedule
             for p in primes for family in families for i in range(count)]
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("duplicate generated cases; choose a different seed")
    return cases


def validate_case(case):
    p = case["prime"]
    if type(p) is not int or p not in ALLOWED_PRIMES:
        raise ValueError("prime is outside the bounded benchmark")
    polys = case["polynomials"]
    if len(polys) != 2:
        raise ValueError("exactly two polynomials required")
    for poly in polys:
        if not 1 <= len(poly) <= 10:
            raise ValueError("invalid support size")
        seen = set()
        for term in poly:
            if len(term) != 3 or any(type(v) is not int for v in term):
                raise ValueError("invalid polynomial term")
            c, x, y = term
            if not (0 < c < p and x >= 0 and y >= 0 and x + y <= 3):
                raise ValueError("term exceeds benchmark limits")
            if (x, y) in seen:
                raise ValueError("duplicate monomial")
            seen.add((x, y))


def original_roots(case):
    """No SymPy, no producer basis, no planted-root shortcut."""
    validate_case(case)
    p = case["prime"]
    return [[x, y] for x in range(p) for y in range(p)
            if all(sum(c * pow(x, a, p) * pow(y, b, p) for c, a, b in poly) % p == 0
                   for poly in case["polynomials"])]


def features(case):
    validate_case(case)
    p = case["prime"]
    polys = case["polynomials"]
    terms = [t for poly in polys for t in poly]
    degrees = [a + b for _, a, b in terms]
    coeffs = [min(c, p - c) / p for c, _, _ in terms]
    avg = sum(coeffs) / len(coeffs)
    return [math.log(p), float(len(terms)), sum(degrees) / len(terms), float(max(degrees)),
            sum(a > 0 and b > 0 for _, a, b in terms) / len(terms),
            sum(d == 1 for d in degrees) / len(terms),
            sum(d == 0 for d in degrees) / len(terms), avg,
            math.sqrt(sum((v - avg) ** 2 for v in coeffs) / len(coeffs)),
            float(max(a for _, a, _ in terms)), float(max(b for _, _, b in terms)),
            float(abs(len(polys[0]) - len(polys[1])))]
