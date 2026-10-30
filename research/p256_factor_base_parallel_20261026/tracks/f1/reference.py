"""Finite reference for the continuation; no producer arithmetic imports.

This is an enumerative correctness oracle, not an implicit decomposition engine
or an independent scientific review. It handles all coordinate multiplicities.
"""
from itertools import combinations_with_replacement, product

from crypto_autoresearcher.index_calculus.curve import Curve, sqrt_mod


def domain(depth, terminal, p):
    roots = {terminal % p}
    for _ in range(depth):
        previous = set()
        for value in roots:
            root = sqrt_mod(value+2, p)
            if root is not None:
                previous.update((root, -root % p))
        roots = previous
    return sorted(roots)


def s3_coefficients(x, y, a, b, p):
    return ((x-y)**2 % p, -2*((x+y)*(x*y+a)+2*b) % p,
            ((x*y-a)**2-4*b*(x+y)) % p)


def s4_zero(xs, target_x, a, b, p):
    A, B, C = s3_coefficients(xs[0], xs[1], a, b, p)
    D, E, F = s3_coefficients(xs[2], target_x, a, b, p)
    return ((A*F-C*D)**2-(A*E-B*D)*(B*F-C*E)) % p == 0


def exhaustive(parameters, depth, terminal, target, arity=3):
    p = parameters['p']
    curve = Curve(p, parameters['a'], parameters['b'], parameters['r'])
    roots = domain(depth, terminal, p)
    states, solutions = set(), set()
    for xs in combinations_with_replacement(roots, arity):
        if arity == 3 and s4_zero(xs, target[0], curve.a, curve.b, p):
            x, y, z = xs
            states.add(((x+y+z) % p, (x*y+x*z+y*z) % p, x*y*z % p))
        choices = []
        for x in xs:
            point = curve.lift_x(x)
            choices.append([] if point is None else sorted({point, curve.neg(point)}))
        for points in product(*choices):
            if any(curve.mul(parameters['r'], point) is not None for point in points):
                continue
            total = None
            for point in points:
                total = curve.add(total, point)
            if total == tuple(target):
                solutions.add(tuple(sorted(points)))
    return dict(domain=roots, states=sorted(states), solutions=sorted(solutions),
                reference_kind='complete finite enumeration; no performance claim')
