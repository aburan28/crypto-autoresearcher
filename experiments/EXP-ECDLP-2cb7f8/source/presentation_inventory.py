"""Sparse symbolic compiler for the frozen full presentation grammar.

Compilation is a scientific measurement and is never called on import. Branches
are streamed without pruning unoccupied or algebraically inconsistent templates.
"""
from collections import Counter
from itertools import combinations, product
from incidence import Field, chart


class Ring:
    def __init__(self, p):
        self.field = Field(p)
        self.variables = set()

    def constant(self, value):
        return Poly(self, {(): value % self.field.p} if value % self.field.p else {})

    def variable(self, name):
        self.variables.add(name)
        return Poly(self, {(name,): 1})


class Poly:
    """Monomials are sorted variable-name tuples, retaining repeated powers."""
    def __init__(self, ring, terms):
        self.ring, self.terms = ring, terms

    def coerce(self, value):
        return value if isinstance(value, Poly) else self.ring.constant(value)

    def __add__(self, other):
        other = self.coerce(other)
        result = dict(self.terms)
        for monomial, coefficient in other.terms.items():
            value = self.ring.field.add(result.get(monomial, 0), coefficient)
            if self.ring.field.eq(value, 0):
                result.pop(monomial, None)
            else:
                result[monomial] = value
        return Poly(self.ring, result)

    __radd__ = __add__

    def __neg__(self):
        return Poly(self.ring, {m: self.ring.field.sub(0, c) for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        result = {}
        for left, a in self.terms.items():
            for right, b in other.terms.items():
                monomial = tuple(sorted(left + right))
                value = self.ring.field.add(result.get(monomial, 0), self.ring.field.mul(a, b))
                if self.ring.field.eq(value, 0):
                    result.pop(monomial, None)
                else:
                    result[monomial] = value
        return Poly(self.ring, result)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        result = self.ring.constant(1)
        for _ in range(exponent):
            result = result * self
        return result

    def normalized(self, variables):
        if not self.terms:
            return None
        # Descending conventional lexicographic exponent vectors over sorted names.
        def key(monomial):
            powers = Counter(monomial)
            return tuple(powers[v] for v in variables)
        monomials = sorted(self.terms, key=key, reverse=True)
        inverse = self.ring.field.inv(self.terms[monomials[0]])
        return tuple((monomial, self.ring.field.mul(self.terms[monomial], inverse))
                     for monomial in monomials)


def series_add(a, b):
    return [x + y for x, y in zip(a, b)]


def series_sub(a, b):
    return [x - y for x, y in zip(a, b)]


def series_mul(a, b):
    result = [a[0].ring.constant(0) for _ in range(5)]
    for i in range(5):
        for j in range(5-i):
            result[i+j] = result[i+j] + a[i]*b[j]
    return result


def partitions(total=4, ceiling=4):
    if total == 0:
        yield ()
    else:
        for first in range(min(total, ceiling), 0, -1):
            for tail in partitions(total-first, first):
                yield (first,) + tail


def branch_keys():
    for multiplicities in partitions():
        for charts in product(('Ynonzero', 'Y0', 'O'), repeat=len(multiplicities)):
            if charts.count('O') > 1:
                continue
            finite = [i for i, name in enumerate(charts) if name != 'O']
            pairs = tuple(combinations(finite, 2))
            for distinctness in product(('x_ne', 'x_eq_y_ne'), repeat=len(pairs)):
                for coefficient_chart in range(4):
                    yield multiplicities, charts, pairs, distinctness, coefficient_chart


def identifier(key):
    multiplicities, charts, pairs, distinctness, coefficient_chart = key
    return ('m=' + ','.join(map(str, multiplicities)) + ';charts=' + ','.join(charts)
            + ';distinct=' + ','.join(distinctness) + ';c=' + str(coefficient_chart))


def compile_branch(p, constant, arm, key):
    multiplicities, charts, pairs, distinctness, coefficient_chart = key
    ring = Ring(p)
    zero, one = ring.constant(0), ring.constant(1)
    t = [zero, one, zero, zero, zero]
    ones = [one, zero, zero, zero, zero]
    equations = []
    def emit(category, polynomials):
        equations.extend((category, polynomial) for polynomial in polynomials)
    c = [zero if j < coefficient_chart else one if j == coefficient_chart
         else ring.variable('c' + str(j)) for j in range(4)]
    coordinates = {}
    for i, (name, m) in enumerate(zip(charts, multiplicities)):
        prefix = 'P' + str(i) + '_'
        var = lambda suffix: ring.variable(prefix + suffix)
        if name == 'O':
            u = [zero] + [var('u' + str(j)) for j in range(1, 5)]
            if arm == 'B':
                u2 = series_mul(u, u)
                residual = series_sub(series_sub(series_sub(series_mul(t, t), u),
                                               series_mul(u2, u)),
                                      [constant * v for v in series_mul(u2, u2)])
                emit('membership_series', residual)
                basis = [u2, u, t, ones]
            else:
                w = [zero] + [var('w' + str(j)) for j in range(1, 5)]
                emit('membership_series', series_sub(w, series_mul(u, u)))
                residual = series_sub(series_sub(series_sub(series_mul(t, t), u),
                                               series_mul(u, w)),
                                      [constant * v for v in series_mul(w, w)])
                emit('membership_series', residual)
                basis = [w, u, t, ones]
        else:
            a = var('a')
            r = var('inverse_chart')
            if name == 'Ynonzero':
                b = var('b')
                x = [a, one, zero, zero, zero]
                y = [b] + [var('y' + str(j)) for j in range(1, 5)]
                emit('chart_nonzero', [r * (2*b) - 1])
            else:
                # b=0 and y=t are frozen substitutions; do not invent b or y_j.
                b = zero
                x = [a] + [var('x' + str(j)) for j in range(1, 5)]
                y = t
                emit('chart_nonzero', [r * (3*a*a + 1) - 1])
                emit('fixed_b_zero', [b])
            coordinates[i] = a, b
            x2 = series_mul(x, x)
            if arm == 'B':
                residual = series_sub(series_sub(series_sub(series_mul(y, y),
                                                           series_mul(x2, x)), x),
                                      [constant*one, zero, zero, zero, zero])
                emit('membership_series', residual)
                basis = [ones, x, y, x2]
            else:
                z = [var('z' + str(j)) for j in range(5)]
                emit('membership_series', series_sub(z, x2))
                residual = series_sub(series_sub(series_sub(series_mul(y, y),
                                                           series_mul(x, z)), x),
                                      [constant*one, zero, zero, zero, zero])
                emit('membership_series', residual)
                basis = [ones, x, y, z]
        emit('section_jet', [sum((c[k]*basis[k][j] for k in range(4)), zero) for j in range(m)])
    for pair, mode in zip(pairs, distinctness):
        i, j = pair
        a, b = coordinates[i]
        x, y = coordinates[j]
        inverse = ring.variable('distinct_' + str(i) + '_' + str(j))
        if mode == 'x_ne':
            emit('support_distinctness', [inverse*(a-x) - 1])
        else:
            emit('support_distinctness', [a-x, inverse*(b-y) - 1])
    variables = sorted(ring.variables)
    for name in variables:
        variable = ring.variable(name)
        emit('rationality', [variable**p - variable])
    unique = {}
    zero_count, duplicate_count = 0, 0
    for category, polynomial in equations:
        normal = polynomial.normalized(variables)
        if normal is None:
            zero_count += 1
        elif normal in unique:
            duplicate_count += 1
            if category not in unique[normal]:
                unique[normal].append(category)
        else:
            unique[normal] = [category]
    serialized = [{'categories': labels, 'terms': [
        {'powers': dict(sorted(Counter(m).items())), 'coefficient': v} for m, v in normal]}
        for normal, labels in unique.items()]
    def counts(include_rationality):
        selected = [(normal, labels) for normal, labels in unique.items()
                    if include_rationality or any(label != 'rationality' for label in labels)]
        return {'field_variables': len(variables), 'equations': len(selected),
                'polynomial_monomials': sum(len(normal) for normal, _ in selected),
                'maximum_degree': max((len(m) for normal, _ in selected for m, _ in normal), default=0)}
    return {'id': identifier(key), 'multiplicities': multiplicities, 'charts': charts,
            'pair_branches': [{'pair': pair, 'mode': mode} for pair, mode in zip(pairs, distinctness)],
            'coefficient_chart': coefficient_chart, 'variables': variables,
            'normalized_equations': serialized, 'full_polynomial': counts(True),
            'finite_field_typed': counts(False), 'zero_equations_omitted': zero_count,
            'exact_duplicates_omitted': duplicate_count,
            'compiler_field_operations': dict(ring.field.counts)}


def occupancy_key(divisor, points, coefficients):
    # Partition first, then ascending canonical point index among equal parts.
    support = sorted(Counter(divisor).items(), key=lambda item: (-item[1], item[0]))
    multiplicities = tuple(m for _, m in support)
    actual_points = [points[i] for i, _ in support]
    charts = tuple(chart(point) for point in actual_points)
    pairs = tuple(combinations([i for i, name in enumerate(charts) if name != 'O'], 2))
    modes = tuple('x_ne' if actual_points[i][0] != actual_points[j][0] else 'x_eq_y_ne'
                  for i, j in pairs)
    coefficient_chart = next(i for i, value in enumerate(coefficients) if value)
    return identifier((multiplicities, charts, pairs, modes, coefficient_chart))


def recovery_inventory():
    # Count concrete decision-tree branches, not a guessed single aggregate number.
    return [
        {'id': 'c2_nonzero_c3_nonzero', 'degree': 4, 'O_multiplicity': 0},
        {'id': 'c2_nonzero_c3_zero', 'degree': 3, 'O_multiplicity': 1},
        {'id': 'c2_zero_h_degree_2', 'degree': 2, 'O_multiplicity': 0},
        {'id': 'c2_zero_h_degree_1', 'degree': 1, 'O_multiplicity': 2},
        {'id': 'c2_zero_h_degree_0', 'degree': 0, 'O_multiplicity': 4},
        {'id': 'root_y_two_nonzero', 'condition': 'two rational opposite square roots', 'multiplicity': 'e each'},
        {'id': 'root_y_zero', 'condition': 'ramified rational root', 'multiplicity': '2e'},
        {'id': 'root_y_absent', 'condition': 'nonsquare right side', 'unresolved_degree': '2e'},
        {'id': 'residual_constant', 'condition': 'no unfactored polynomial support'},
        {'id': 'residual_nonconstant', 'condition': 'nonsplit polynomial support retained'},
        {'id': 'O_present', 'condition': 'positive pole deficit, verify local order'},
        {'id': 'O_absent', 'condition': 'zero pole deficit, verify local order zero'},
    ]


def write_inventory(handle, p, constant, occupancy, dumps):
    """One output JSON object; complete branch equations streamed to bound RAM."""
    vectors = {}
    recovery = recovery_inventory()
    handle.write('{"p":' + str(p) + ',"curve_constant":' + str(constant) + ',"arms":{')
    for arm_number, arm in enumerate(('B', 'I')):
        if arm_number:
            handle.write(',')
        handle.write(dumps(arm) + ':{"branches":[')
        totals = Counter(field_variables=0, polynomial_monomials=0, equations=0, branch_count=0)
        typed = Counter(field_variables=0, polynomial_monomials=0, equations=0)
        worst, compiler = Counter(), Counter()
        first = True
        for key in branch_keys():
            branch = compile_branch(p, constant, arm, key)
            branch['accepted_pair_occupancy'] = occupancy.get(branch['id'], 0)
            if not first:
                handle.write(',')
            handle.write(dumps(branch))
            first = False
            totals['branch_count'] += 1
            for metric in ('field_variables', 'polynomial_monomials', 'equations'):
                totals[metric] += branch['full_polynomial'][metric]
                typed[metric] += branch['finite_field_typed'][metric]
                worst[metric] = max(worst[metric], branch['full_polynomial'][metric])
            for version in ('full_polynomial', 'finite_field_typed'):
                worst['maximum_degree_' + version] = max(worst['maximum_degree_' + version],
                                                          branch[version]['maximum_degree'])
            compiler.update(branch['compiler_field_operations'])
        totals['recovery_case_count'] = len(recovery)
        vectors[arm] = {'primary': dict(totals), 'finite_field_typed': dict(typed),
                        'worst_branch': dict(worst), 'compiler_field_operations': dict(compiler)}
        handle.write('],"summary":' + dumps(vectors[arm]) + '}')
    handle.write('},"recovery_grammar":' + dumps(recovery) + '}\n')
    return vectors
