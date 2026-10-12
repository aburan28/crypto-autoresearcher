"""Public EC decomposition systems and a bounded algebra-to-relation bridge."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tasks/polynomial_solver_ml/environment"))
from polynomial_ml.solver import ACTIONS, basis_roots  # noqa: E402
from tools.curve_identity import curve_identity  # noqa: E402
from ec import Curve, RelationSystem, is_prime  # noqa: E402

FEATURE_NAMES = ("field_bits", "subgroup_bits", "factor_base_size", "terms",
                 "mean_degree", "max_degree", "mixed_fraction", "coefficient_mean",
                 "coefficient_std", "x_degree", "y_degree", "support_imbalance")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def from_case(case):
    c = case["curve"]
    return Curve(c["p"], c["a"], c["b"], c["n"], c["h"], tuple(c["g"]))


def identities(curve):
    return curve_identity(
        {"characteristic": curve.p, "degree": 1, "representation": "prime",
         "element_encoding": "canonical_integer"},
        {"model": {"a1": 0, "a2": 0, "a3": 0, "a4": curve.a, "a6": curve.b},
         "subgroup_order": curve.n, "cofactor": curve.h, "generator": list(curve.g),
         "target_group": "prime_order_subgroup"}, "mltoy")


def all_points(p, a, b):
    return [(x, y) for x in range(p) for y in range(p)
            if (y*y - x*x*x - a*x - b) % p == 0]


def largest_prime_factor(n):
    factors = []
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            factors.append(d)
            while n % d == 0:
                n //= d
    if n > 1:
        factors.append(n)
    return max(factors, default=1)


def summation_polynomial(x, y, z, a, b):
    return (x-y)**2*z**2 - 2*((x+y)*(x*y+a)+2*b)*z + (x*y-a)**2 - 4*b*(x+y)


def equations(curve, target, factor_x):
    x, y = sp.symbols("x y")
    values = [summation_polynomial(x, y, target[0], curve.a, curve.b),
              sp.prod(x-v for v in factor_x), sp.prod(y-v for v in factor_x)]
    return [[[int(c) % curve.p, i, j] for (i, j), c in
             sp.Poly(poly, x, y, modulus=curve.p).terms() if int(c) % curve.p]
            for poly in values]


def generate(profile, seed):
    if profile == "quick":
        groups = {"train": [7,11,13,17,19,23], "validation": [29,31], "test": [37,41,43,47]}
        target_count = 1
    elif profile == "standard":
        primes = [p for p in range(7, 252) if is_prime(p)][:48]
        groups = {"train": primes[:28], "validation": primes[28:36], "test": primes[36:48]}
        target_count = 2
    else:
        raise ValueError("unknown profile")
    cases = []
    for split, primes in groups.items():
        for p in primes:
            seen_models = set()
            for model in range(2):
                rng = random.Random(int.from_bytes(hashlib.sha256(canonical([seed,p,model])).digest(), "big"))
                curve = None
                for attempt in range(1000):
                    a, b = rng.randrange(p), rng.randrange(p)
                    if (a,b) in seen_models or (4*a**3+27*b**2) % p == 0:
                        continue
                    points = all_points(p, a, b)
                    order = len(points) + 1
                    n = largest_prime_factor(order)
                    if n < 5 or order % (n*n) == 0:
                        continue
                    for g in points:
                        try:
                            curve = Curve(p, a, b, n, order//n, g)
                            break
                        except ValueError:
                            continue
                    if curve is not None:
                        break
                if curve is None:
                    raise ValueError("no admitted toy curve after fixed generation watchdog")
                seen_models.add((a,b))
                subgroup = [pt for pt in points if curve.mul(n, pt) is None]
                others = sorted({pt[0] for pt in subgroup} - {curve.g[0]})
                rng.shuffle(others)
                factor_x = sorted([curve.g[0], *others[:min(3, len(others))]])
                chosen = rng.sample(subgroup, target_count)
                for target in chosen:
                    public = {"curve": {"p":p,"a":a,"b":b,"n":n,"h":order//n,"g":list(curve.g)},
                              "target":list(target), "factor_x":factor_x,
                              "polynomials":equations(curve, target, factor_x)}
                    cases.append({**public, **identities(curve), "split":split,
                                  "field_block":f"Fp:{p}", "id":hashlib.sha256(canonical(public)).hexdigest(),
                                  "generation_attempts":attempt+1})
    validate_splits(cases)
    return cases


def validate_splits(cases):
    owners = {}
    ids = set()
    for case in cases:
        if case["split"] not in ("train", "validation", "test") or case["id"] in ids:
            raise ValueError("invalid split or duplicate input")
        ids.add(case["id"])
        # Derive identities from mathematics, never trust a supplied alias.
        curve = from_case(case)
        for key in (f"field:{curve.p}", identities(curve)["curve_uid"],
                    hashlib.sha256(canonical([curve.p,curve.a,curve.b,case["target"]])).hexdigest()):
            previous = owners.setdefault(key, case["split"])
            if previous != case["split"]:
                raise ValueError("field/curve/target leaks across splits")


def validate_case(case):
    curve = from_case(case)
    target = tuple(case["target"])
    curve.check_subgroup(target)
    xs = case["factor_x"]
    if (target is None or not isinstance(xs, list) or not 1 <= len(xs) <= 4
            or xs != sorted(set(xs)) or any(type(v) is not int or not 0 <= v < curve.p for v in xs)):
        raise ValueError("invalid public factor base")
    if any(not lift(curve, x) for x in xs):
        raise ValueError("factor-base x does not lift to subgroup")
    if case["polynomials"] != equations(curve, target, xs):
        raise ValueError("system is not the declared EC decomposition problem")
    if any(case.get(k) != v for k,v in identities(curve).items()):
        raise ValueError("curve metadata does not match exact EC1 preimage")
    if len(all_points(curve.p,curve.a,curve.b))+1 != curve.n*curve.h:
        raise ValueError("incorrect curve order/cofactor")
    return curve


def features(case):
    # Explicit allowlist. Metadata and post-solve quantities are not read.
    c = case["curve"]
    terms = [t for poly in case["polynomials"] for t in poly]
    degrees = [i+j for _,i,j in terms]
    values = [min(v,c["p"]-v)/c["p"] for v,_,_ in terms]
    average = sum(values)/len(values)
    return [c["p"].bit_length(), c["n"].bit_length(), len(case["factor_x"]), len(terms),
            sum(degrees)/len(terms), max(degrees), sum(i>0 and j>0 for _,i,j in terms)/len(terms),
            average, math.sqrt(sum((v-average)**2 for v in values)/len(values)),
            max(i for _,i,_ in terms), max(j for _,_,j in terms),
            max(map(len,case["polynomials"]))-min(map(len,case["polynomials"]))]


def scalar_roots(case):
    p = case["curve"]["p"]
    return [[x,y] for x in range(p) for y in range(p)
            if all(sum(c*pow(x,i,p)*pow(y,j,p) for c,i,j in poly) % p == 0
                   for poly in case["polynomials"])]


def lift(curve, x):
    return [(x,y) for y in range(curve.p)
            if curve.on_curve((x,y)) and curve.mul(curve.n,(x,y)) is None]


def relation_evaluation(case, roots):
    curve = from_case(case)
    target = tuple(case["target"])
    seeds = [pt for x in case["factor_x"] for pt in lift(curve,x)]
    system = RelationSystem(curve, seeds, {"q":target})
    no_witness = 0
    for x,y in roots:
        found = False
        for left in lift(curve,x):
            for right in lift(curve,y):
                if curve.add(left,right) == target:
                    system.insert([(1,left),(1,right),(-1,target)])
                    found = True
        no_witness += not found
    return {**system.summary(), "roots_without_base_field_witness":no_witness,
            "scope":"Rank per verification call excludes discovery, subgroup admission and symbolic operations."}


def worker(case, action, repetitions):
    curve = validate_case(case)
    if type(action) is not int or not 0 <= action < len(ACTIONS) or repetitions not in (1,2):
        raise ValueError("invalid action or repetitions")
    if sys.platform.startswith("linux"):
        resource.setrlimit(resource.RLIMIT_AS, (2*1024**3,2*1024**3))
    x,y = sp.symbols("x y")
    timings, roots = [], None
    for _ in range(repetitions):
        start = time.perf_counter()
        polys = [sum(c*x**i*y**j for c,i,j in poly) for poly in case["polynomials"]]
        built = time.perf_counter()
        basis = sp.groebner(polys, x,y, modulus=curve.p, **ACTIONS[action])
        reduced = time.perf_counter()
        current = basis_roots(basis,curve.p)
        extracted = time.perf_counter()
        relations = relation_evaluation(case,current)
        end = time.perf_counter()
        if roots is not None and current != roots:
            raise ValueError("root set changed between repetitions")
        roots = current
        timings.append({"construction_seconds":built-start,"groebner_seconds":reduced-built,
                        "root_seconds":extracted-reduced,"relation_verification_seconds":end-extracted,
                        "total_seconds":end-start})
    return {"case_id":case["id"],"action":action,"status":"completed","roots":roots,
            "relations":relations,"timings":timings,
            "solver_seconds":float(np.median([t["total_seconds"] for t in timings])),
            "basis_size":len(basis.polys),
            "peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
