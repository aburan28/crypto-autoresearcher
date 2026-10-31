"""Explicit sparse prime-field circuits; fixture values never specialize equations."""
from copy import deepcopy

SCHEMA = 'prime-rationality-field-circuit/v1'


def constant(n, p):
    n %= p
    return {(): n} if n else {}


def variable(name):
    return {(name,): 1}


def add(p, *polys):
    result = {}
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] = (result.get(monomial, 0) + coefficient) % p
    return {m: c for m, c in result.items() if c}


def scale(poly, n, p):
    return {m: c*n % p for m, c in poly.items() if c*n % p}


def sub(left, right, p):
    return add(p, left, scale(right, -1, p))


def mul(left, right, p):
    result = {}
    for a, ac in left.items():
        for b, bc in right.items():
            monomial = tuple(sorted(a+b))
            result[monomial] = (result.get(monomial, 0) + ac*bc) % p
    return {m: c for m, c in result.items() if c}


def polynomial_product(left, right, p):
    result = [{} for _ in range(len(left)+len(right)-1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i+j] = add(p, result[i+j], mul(a, b, p))
    return result


class Builder:
    """Builder arithmetic is deliberately separate from the exported-IR checker."""
    def __init__(self, p, a, b, kind, k):
        self.p = p
        self.document = {'schema': SCHEMA, 'p': p, 'curve': {'a': a, 'b': b},
                         'kind': kind, 'k': k, 'inputs': [], 'auxiliaries': [],
                         'projection': [], 'equations': [], 'metadata': {'blocks': []}}
        self.assignment = {}

    def register(self, name, value, role):
        if name in self.assignment or type(value) is not int or not 0 <= value < self.p:
            raise ValueError('unique variable and canonical field value required')
        self.document[role].append(name)
        self.assignment[name] = value
        return variable(name)

    def input(self, name, value):
        return self.register(name, value, 'inputs')

    def aux(self, name, value):
        return self.register(name, value, 'auxiliaries')

    def eq(self, label, expression):
        if any(eq['label'] == label for eq in self.document['equations']):
            raise ValueError('duplicate obligation label')
        self.document['equations'].append({'label': label, 'terms': [
            {'coefficient': c, 'variables': list(m)} for m, c in sorted(expression.items())]})

    def value(self, expression):
        total = 0
        for m, c in expression.items():
            for name in m:
                c = c*self.assignment[name] % self.p
            total = (total+c) % self.p
        return total

    def export(self):
        self.document['projection'] = self.document['inputs'][:]
        self.document['metadata']['blocks'] = [{
            'name': self.document['kind'], 'auxiliaries': self.document['auxiliaries'][:],
            'equations': [eq['label'] for eq in self.document['equations']]}]
        return {'circuit': deepcopy(self.document), 'assignment': dict(self.assignment)}
