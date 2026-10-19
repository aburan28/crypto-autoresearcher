#!/usr/bin/env python3
"""Statement-only exact arithmetic audit, TASK-20261015-5fd82c.

No repository imports. Run from any cwd; the only mathematical input is the
assigned fixtures.json. The output is write-once unless --output names a new
scratch path. O is None internally and "O" in JSON. Counts use actual group
points, never a presumed cyclic log or a Poisson approximation.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent / 'blind-group' / 'fixtures.json'
STATEMENT = HERE.parent / 'blind-group' / 'statement.md'
OPS = Counter()


def encode(p):
    if p is None:
        return 'O'
    return [encode_coord(v) for v in p]


def encode_coord(v):
    return list(v) if isinstance(v, tuple) else v


def key(p):
    return (0,) if p is None else (1, p)


class Fp:
    def __init__(self, p):
        self.p = p
        self.zero, self.one = 0, 1
        self.elements = list(range(p))

    def const(self, n): return n % self.p
    def add(self, a, b): return (a+b) % self.p
    def neg(self, a): return -a % self.p
    def sub(self, a, b): return (a-b) % self.p
    def mul(self, a, b): return a*b % self.p
    def inv(self, a):
        assert a
        OPS['field_inverse'] += 1
        return pow(a, -1, self.p)


class F25:
    """(a,b)=a+b*z, z^2=-z-1, with fixed p=5."""
    zero, one = (0, 0), (1, 0)
    elements = list(product(range(5), repeat=2))
    def const(self, n): return (n % 5, 0)
    def add(self, a, b): return ((a[0]+b[0]) % 5, (a[1]+b[1]) % 5)
    def neg(self, a): return (-a[0] % 5, -a[1] % 5)
    def sub(self, a, b): return self.add(a, self.neg(b))
    def mul(self, a, b):
        return ((a[0]*b[0]-a[1]*b[1]) % 5,
                (a[0]*b[1]+a[1]*b[0]-a[1]*b[1]) % 5)
    def inv(self, a):
        assert a != self.zero
        OPS['field_inverse'] += 1
        # Norm (a+b*z)(a+b*z^2)=a^2-a*b+b^2.
        norm = (a[0]*a[0]-a[0]*a[1]+a[1]*a[1]) % 5
        ni = pow(norm, -1, 5)
        return ((a[0]-a[1])*ni % 5, -a[1]*ni % 5)


class Curve:
    def __init__(self, f, a, b):
        self.f, self.a, self.b = f, f.const(a), f.const(b)
        self.points = [None] + [(x, y) for x in f.elements for y in f.elements
                                if self.on((x, y))]
        self.pointset = set(self.points)

    def on(self, p):
        if p is None: return True
        x, y = p
        f = self.f
        return f.mul(y, y) == f.add(f.add(f.mul(f.mul(x, x), x),
                                           f.mul(self.a, x)), self.b)

    def neg(self, p):
        return None if p is None else (p[0], self.f.neg(p[1]))

    def add(self, p, q):
        OPS['group_add_call'] += 1
        if p is None: return q
        if q is None: return p
        f = self.f
        x, y = p
        u, v = q
        if x == u:
            if f.add(y, v) == f.zero: return None
            assert p == q
            slope = f.mul(f.add(f.mul(f.const(3), f.mul(x, x)), self.a),
                          f.inv(f.mul(f.const(2), y)))
        else:
            slope = f.mul(f.sub(v, y), f.inv(f.sub(u, x)))
        xx = f.sub(f.sub(f.mul(slope, slope), x), u)
        yy = f.sub(f.mul(slope, f.sub(x, xx)), y)
        return xx, yy

    def mul(self, n, p):
        if n < 0: return self.mul(-n, self.neg(p))
        q = None
        while n:
            if n & 1: q = self.add(q, p)
            p = self.add(p, p)
            n >>= 1
        return q


def factors(n):
    ans = []
    d = 2
    while d*d <= n:
        k = 0
        while n % d == 0:
            n //= d
            k += 1
        if k: ans.append([d, k])
        d += 1
    if n > 1: ans.append([n, 1])
    return ans


def group_checks(c, exhaustive_associativity=False):
    pts = c.points
    assert all(c.add(p, c.neg(p)) is None for p in pts)
    assert all(c.add(p, q) in c.pointset and c.add(p, q) == c.add(q, p)
               for p in pts for q in pts)
    assert all(c.mul(len(pts), p) is None for p in pts)
    if exhaustive_associativity:
        triples = product(pts, repeat=3)
        count = len(pts)**3
    else:
        # Fixed deterministic schedule, with all boundary points included.
        n = len(pts)
        indices = sorted(set([0, 1, n-1] + list(range(0, n, max(1, n//8)))))
        triples = ((pts[i], pts[j], pts[k]) for i, j, k in product(indices, repeat=3))
        count = len(indices)**3
    for p, q, r in triples:
        assert c.add(c.add(p, q), r) == c.add(p, c.add(q, r))
    return {'closure_pairs': len(pts)**2, 'inverse_points': len(pts),
            'commutativity_pairs': len(pts)**2, 'order_annihilation_points': len(pts),
            'associativity_triples': count, 'passed': True}


def brute_counts(c, base, m):
    counts = Counter()
    for tup in product(base, repeat=m):
        s = None
        for p in tup: s = c.add(s, p)
        counts[s] += 1
    return counts


def distributions(c, group, base, lengths, brute_lengths=(2, 3)):
    base = sorted(set(base), key=key)
    assert None not in base and set(base) <= set(group)
    counts, witnesses = {None: 1}, {None: ()}
    out = {}
    for m in range(1, max(lengths)+1):
        new, wit = Counter(), {}
        for s in sorted(counts, key=key):
            for p in base:
                t = c.add(s, p)
                new[t] += counts[s]
                wit.setdefault(t, witnesses[s]+(p,))
        counts, witnesses = new, wit
        if m not in lengths: continue
        values = [counts.get(p, 0) for p in group]
        assert sum(values) == len(base)**m
        mean = Fraction(sum(values), len(group))
        assert mean == Fraction(len(base)**m, len(group))
        if m in brute_lengths:
            bc = brute_counts(c, base, m)
            assert all(bc.get(p, 0) == counts.get(p, 0) for p in group)
        target_rows = []
        for p, n in zip(group, values):
            witness = witnesses.get(p)
            assert (witness is not None) == (n > 0)
            if witness is not None:
                s = None
                for b in witness:
                    assert b in base
                    s = c.add(s, b)
                assert len(witness) == m and s == p
            target_rows.append({'target': encode(p), 'count': n,
                                'witness': None if witness is None else [encode(x) for x in witness]})
        out[str(m)] = {'total': sum(values), 'base_size_power': len(base)**m,
                       'exact_first_moment': [mean.numerator, mean.denominator],
                       'minimum': min(values), 'maximum': max(values),
                       'zero_targets': sum(v == 0 for v in values),
                       'coverage': [sum(v > 0 for v in values), len(group)],
                       'brute_force_checked': m in brute_lengths,
                       'targets': target_rows}
    return out


def subgroup(c, explicit_r=None):
    ff = factors(len(c.points))
    candidates = [p for p, v in ff if p >= 5 and v == 1]
    r = explicit_r if explicit_r is not None else max(candidates, default=None)
    if r is None:
        return {'admitted': False, 'reason': 'no prime r>=5 with valuation one',
                'order': len(c.points), 'factorization': ff}, None
    assert r in candidates
    gen = next(p for p in c.points[1:] if c.mul(r, p) is None)
    g = [c.mul(i, gen) for i in range(r)]
    assert len(set(g)) == r
    assert all(c.add(p, q) in set(g) for p in g for q in g)
    return {'admitted': True, 'order': len(c.points), 'factorization': ff,
            'r': r, 'generator': encode(gen), 'points': [encode(p) for p in g],
            'explicit_r11_applied': explicit_r == 11}, g


def poly_add(a, b, p):
    c = [0]*max(len(a), len(b))
    for i, v in enumerate(a): c[i] += v
    for i, v in enumerate(b): c[i] += v
    return [v % p for v in c]


def poly_mul(a, b, p):
    c = [0]*(len(a)+len(b)-1)
    for i, u in enumerate(a):
        for j, v in enumerate(b): c[i+j] = (c[i+j]+u*v) % p
    return c


def poly_derivative(a, p): return [i*a[i] % p for i in range(1, len(a))] or [0]


def poly_eval(a, x, p):
    s = 0
    for v in reversed(a): s = (s*x+v) % p
    return s


def audit():
    t0 = time.monotonic()
    cpu0 = time.process_time()
    fixture_bytes = FIXTURES.read_bytes()
    fx = json.loads(fixture_bytes)
    result = {'task_id': 'TASK-20261015-5fd82c', 'phase': 'blind independent derivation only',
              'schema': 'lattice-ic.blind-group-independent-predictions.v1',
              'fixtures': fx, 'fixture_sha256': hashlib.sha256(fixture_bytes).hexdigest(),
              'statement_sha256': hashlib.sha256(STATEMENT.read_bytes()).hexdigest(),
              'software_controls': [], 'prime_curves': []}
    # Predetermined software controls are small non-study fields, not new study arms.
    for p, a, b in [(5, 1, 1), (7, 0, 3)]:
        c = Curve(Fp(p), a, b)
        checks = group_checks(c, True)
        base = c.points[1:4]
        dist = distributions(c, c.points, base, [2, 3, 5], (2, 3, 5))
        result['software_controls'].append({'curve': [p, a, b], 'order': len(c.points),
                                             'checks': checks, 'base': [encode(x) for x in base],
                                             'tuple_counts': dist})
    target = target_group = None
    for curve_tuple in fx['prime_curves']:
        p, a, b = curve_tuple
        assert (4*a**3+27*b*b) % p != 0
        c = Curve(Fp(p), a, b)
        # This is the named pairing fixture and its explicit r=11 instruction.
        sg, group = subgroup(c, 11 if curve_tuple == [43, 1, 0] else None)
        row = {'curve': curve_tuple, 'points': [encode(x) for x in c.points],
               'group_checks': group_checks(c), 'subgroup': sg, 'windows': []}
        for width in fx['window_bounds']:
            wr = {'W': width, 'admissible': group is not None}
            if group is None:
                wr.update({'base': None, 'base_size': None, 'tuple_counts': None,
                           'reason': sg['reason']})
            else:
                base = [v for v in group if v is not None and v[0] < width]
                wr.update({'base': [encode(x) for x in sorted(base, key=key)], 'base_size': len(base),
                           'tuple_counts': distributions(c, group, base, fx['tuple_lengths'])})
            row['windows'].append(wr)
        result['prime_curves'].append(row)
        if curve_tuple == fx['factorbase']['target']:
            target, target_group = c, group
    assert target is not None and target_group is not None
    p, a0, _ = fx['factorbase']['auxiliary']
    coeffs = [a0]
    for _ in range(max(fx['factorbase']['depths'])): coeffs.append(-4*coeffs[-1] % p)
    auxiliaries = [Curve(Fp(p), a, 0) for a in coeffs]
    source = auxiliaries[0]
    alpha_x = fx['factorbase']['alpha_x']

    def alpha(v): return None if v is None else (alpha_x*v[0] % p, v[1])

    assert alpha_x != 1 and pow(alpha_x, 3, p) == 1
    assert target.a == 0
    assert all(alpha(v) in target.pointset for v in target.points)
    assert all(alpha(target.add(u, v)) == target.add(alpha(u), alpha(v))
               for u in target.points for v in target.points)
    stable = all(alpha(v) in set(target_group) for v in target_group)
    scalars = [i for i in range(len(target_group))
               if all(target.mul(i, v) == alpha(v) for v in target_group)] if stable else []
    result['target_action'] = {'alpha_x': alpha_x, 'field_cube_root_checked': True,
                               'all_curve_points_checked': len(target.points),
                               'homomorphism_pairs': len(target.points)**2,
                               'subgroup_stable': stable, 'scalar_candidates': scalars,
                               'unique_lambda': scalars[0] if len(scalars) == 1 else None,
                               'all_G_actions': [{'point': encode(v), 'image': encode(alpha(v))} for v in target_group]}
    assert stable

    def complete(base):
        done = set(base)
        for v in base:
            w = alpha(v)
            while w not in done:
                done.add(w)
                w = alpha(w)
        assert all(alpha(v) in done for v in done)
        return sorted(done, key=key)

    result['auxiliary_curves'] = [{'curve': [p, a, 0], 'order': len(c.points),
                                   'factorization': factors(len(c.points)),
                                   'points': [encode(v) for v in c.points],
                                   'checks': group_checks(c)} for a, c in zip(coeffs, auxiliaries)]
    result['auxiliary_depths'] = []
    npoly, dpoly = [0, 1], [1]
    for depth in fx['factorbase']['depths']:
        if depth:
            oldn, oldd = npoly, dpoly
            npoly = poly_add(poly_mul(oldn, oldn, p),
                             [coeffs[depth-1]*v % p for v in poly_mul(oldd, oldd, p)], p)
            dpoly = poly_mul(oldn, oldd, p)
        dst = auxiliaries[depth]

        def chain(v, trace=False):
            path = [v]
            for j in range(depth):
                if v is None or v == (0, 0):
                    v = None
                else:
                    x, y = v
                    inv = pow(x, -1, p)
                    v = ((x+coeffs[j]*inv) % p,
                         y*(1-coeffs[j]*inv*inv) % p)
                assert auxiliaries[j+1].on(v)
                path.append(v)
            return path if trace else v

        nd = poly_derivative(npoly, p)
        dd = poly_derivative(dpoly, p)
        yn = poly_add(poly_mul(nd, dpoly, p), [-v % p for v in poly_mul(npoly, dd, p)], p)

        def expanded(v):
            if v is None: return None
            x, y = v
            n, d = poly_eval(npoly, x, p), poly_eval(dpoly, x, p)
            assert not (n == 0 and d == 0)
            if d == 0: return None
            di = pow(d, -1, p)
            return n*di % p, y*poly_eval(yn, x, p)*di*di % p

        images = {v: chain(v) for v in source.points}
        assert all(expanded(v) == w for v, w in images.items())
        assert all(images[source.add(v, w)] == dst.add(images[v], images[w])
                   for v in source.points for w in source.points)
        fibers = defaultdict(list)
        for v, image in images.items(): fibers[image].append(v)
        kernel = sorted(fibers[None], key=key)
        assert all(source.add(v, w) in set(kernel) for v in kernel for w in kernel)
        original = next(v for v in source.points if v is not None and images[v] is not None)
        rows, histogram, completed_histogram = [], Counter(), Counter()
        adverse = []
        for image in sorted((v for v in fibers if v is not None), key=key):
            fiber = sorted(fibers[image], key=key)
            rep = fiber[0]
            assert set(fiber) == {source.add(rep, k) for k in kernel}
            assert len(fiber) == len(kernel)
            # Independently solve expanded x equation and require an actual y lift.
            roots = [x for x in range(p) if poly_eval(dpoly, x, p) != 0 and
                     (poly_eval(npoly, x, p)-image[0]*poly_eval(dpoly, x, p)) % p == 0]
            rational_lifts = [v for v in source.points[1:] if v[0] in roots and expanded(v) == image]
            assert set(rational_lifts) == set(fiber)
            for v in rational_lifts:
                tr = chain(v, True)
                assert tr[-1] == image and all(t is not None for t in tr)
                assert all(tr[j][0]*tr[j+1][0] % p == (tr[j][0]**2+coeffs[j]) % p
                           for j in range(depth))
            xs = sorted(set(v[0] for v in fiber))
            base = sorted([v for v in target_group if v is not None and v[0] in xs], key=key)
            # Full rational lift, not a projective-line-only root.
            lifted_base = sorted([v for v in target_group if v is not None and
                                  any(u[0] == v[0] for u in rational_lifts)], key=key)
            assert base == lifted_base
            chain_xs = set()
            for x in range(p):
                ys = [y for y in range(p) if source.on((x, y))]
                for y in ys:
                    tr = chain((x, y), True)
                    if tr[-1] == image:
                        assert all(v is not None for v in tr)
                        chain_xs.add(x)
            assert chain_xs == set(xs)
            no_lift = [x for x in roots if not any(v[0] == x for v in source.points[1:])]
            if no_lift:
                adverse.append({'image': encode(image), 'P1_only_x': no_lift,
                                'would_be_target_points': [encode(v) for v in target_group if v is not None and v[0] in no_lift]})
            done = complete(base)
            bkey = tuple(base)
            histogram[bkey] += 1
            completed_histogram[tuple(done)] += 1
            rows.append({'ordinal': len(rows), 'image': encode(image), 'representative': encode(rep),
                         'is_original_first_source_slice': images[original] == image,
                         'source_fiber': [encode(v) for v in fiber], 'source_x': xs,
                         'expanded_x_roots': roots, 'P1_only_no_rational_lift_x': no_lift,
                         'base': [encode(v) for v in base], 'base_size': len(base),
                         'tuple_counts': distributions(target, target_group, base, [2, 3, 5]),
                         'orbit_completed_base': [encode(v) for v in done],
                         'orbit_completed_size': len(done),
                         'orbit_completed_tuple_counts': distributions(target, target_group, done, [2, 3, 5])})
        assert sum(len(v) for v in fibers.values()) == len(source.points)
        assert len(fibers)*len(kernel) == len(source.points)
        ks = [None] + [v for v in source.points[1:] if poly_eval(dpoly, v[0], p) == 0]
        assert set(ks) == set(kernel)
        # The P1 adversary has only an image x, possibly with no rational
        # auxiliary image point at all. Keep the entire fixed F97 coordinate
        # census, rather than postselecting a successful adverse example.
        p1_census = []
        for image_x in range(p):
            roots = [x for x in range(p) if poly_eval(dpoly, x, p) != 0 and
                     (poly_eval(npoly, x, p)-image_x*poly_eval(dpoly, x, p)) % p == 0]
            lifts = [v for v in source.points[1:] if expanded(v) is not None and expanded(v)[0] == image_x]
            false_x = [x for x in roots if not any(v[0] == x for v in source.points[1:])]
            assert set(roots)-set(false_x) == {v[0] for v in lifts}
            p1_census.append({'image_x': image_x, 'expanded_x_roots': roots,
                              'rational_source_lifts': [encode(v) for v in lifts],
                              'rational_auxiliary_image_points': [encode(v) for v in dst.points[1:] if v[0] == image_x],
                              'P1_only_no_rational_lift_x': false_x,
                              'false_target_membership_if_lift_omitted':
                                  [encode(v) for v in target_group if v is not None and v[0] in false_x]})
        assert any(row['false_target_membership_if_lift_omitted'] for row in p1_census)
        result['auxiliary_depths'].append({
            'depth': depth, 'degree': 2**depth, 'target_auxiliary_curve': [p, coeffs[depth], 0],
            'expanded_x_numerator_coeffs_low_first': npoly,
            'expanded_x_denominator_coeffs_low_first': dpoly,
            'expanded_y_derivative_numerator_coeffs_low_first': yn,
            'rational_kernel': [encode(v) for v in kernel], 'rational_kernel_size': len(kernel),
            'complete_rational_kernel': len(kernel) == 2**depth,
            'kernel_O_fiber': [encode(v) for v in kernel],
            'rational_image_points': [encode(v) for v in sorted(fibers, key=key)],
            'total_rational_fibers_including_O': len(fibers),
            'finite_fiber_denominator': len(rows), 'finite_fiber_source_total': sum(len(r['source_fiber']) for r in rows),
            'empty_base_fibers': sum(r['base_size'] == 0 for r in rows),
            'actual_base_size_histogram': dict(sorted(Counter(r['base_size'] for r in rows).items())),
            'duplicate_actual_base_histogram': [{'base': [encode(v) for v in b], 'fiber_multiplicity': n}
                                               for b, n in sorted(histogram.items(), key=lambda t: t[0])],
            'duplicate_completed_base_histogram': [{'base': [encode(v) for v in b], 'fiber_multiplicity': n}
                                                  for b, n in sorted(completed_histogram.items(), key=lambda t: t[0])],
            'original_lex_first_nonkernel_source': encode(original),
            'original_first_coset_ordinal': next(r['ordinal'] for r in rows if r['is_original_first_source_slice']),
            'original_first_coset_image': encode(images[original]),
            'P1_only_adverse_controls': adverse,
            'complete_P1_coordinate_census': p1_census,
            'complete_P1_adverse_controls': [row for row in p1_census if row['P1_only_no_rational_lift_x']],
            'checks': {'all_rational_point_map_checks': len(source.points),
                       'expanded_vs_chain_checks': len(source.points),
                       'homomorphism_pairs': len(source.points)**2,
                       'all_image_fibers_are_kernel_cosets': True,
                       'all_finite_fibers_rational_lift_and_chain_checked': True,
                       'projective_kernel_exceptions_checked': len(kernel), 'passed': True},
            'finite_fibers': rows})
    # The specified noncyclic rank-two control is independent of the prime G.
    f = F25()
    assert all(f.mul(v, f.inv(v)) == f.one for v in f.elements if v != f.zero)
    assert f.add(f.add(f.mul((0, 1), (0, 1)), (0, 1)), f.one) == f.zero
    c = Curve(f, 0, 1)
    checks = group_checks(c)
    torsion = [v for v in c.points if c.mul(3, v) is None]
    line_sets = {frozenset([None, v, c.mul(2, v)]) for v in torsion if v is not None}
    lines = sorted([sorted(line, key=key) for line in line_sets], key=lambda line: tuple(key(v) for v in line))
    def az(v): return None if v is None else (f.mul((0, 1), v[0]), v[1])
    assert all(az(v) in c.pointset for v in c.points)
    assert all(az(c.add(v, w)) == c.add(az(v), az(w)) for v in c.points for w in c.points)
    records = []
    for i, line in enumerate(lines):
        stable = all(az(v) in line for v in line)
        scalars = [k for k in range(3) if all(c.mul(k, v) == az(v) for v in line)] if stable else []
        image_set = {az(v) for v in line}
        records.append({'ordinal': i, 'points': [encode(v) for v in line], 'stable': stable,
                        'image_line_ordinal': next(j for j, other in enumerate(lines) if set(other) == image_set),
                        'scalar_candidates': scalars, 'unique_lambda': scalars[0] if len(scalars) == 1 else None,
                        'nonstable_witness': next(({'point': encode(v), 'image': encode(az(v))}
                                                  for v in line if az(v) not in line), None)})
    result['F25_control'] = {'field': 'F5[z]/(z^2+z+1)', 'curve': 'y^2=x^3+1',
                             'order': len(c.points), 'factorization': factors(len(c.points)),
                             'points': [encode(v) for v in c.points], 'checks': checks,
                             'homomorphism_pairs': len(c.points)**2,
                             'rational_3_torsion_size': len(torsion), 'torsion_is_cyclic': len(torsion) == 3,
                             'torsion_points': [encode(v) for v in torsion],
                             'all_torsion_actions': [{'point': encode(v), 'image': encode(az(v))} for v in torsion],
                             'cyclic_order3_lines': records, 'stable_line_count': sum(r['stable'] for r in records)}
    result['checks_and_scope'] = {'all_assertions_passed': True, 'arithmetic_dependencies': 'Python standard library only',
                                 'factorbase_tuple_schedule': [2, 3, 5],
                                 'schedule_note': 'Statement explicitly requires 2,3,5 for every fiber; fixtures factorbase 2,3 retained and 5 also supplied.',
                                 'producer_comparison_performed': False, 'full_joint_completed': False,
                                 'operation_counters': dict(OPS), 'elapsed_seconds': time.monotonic()-t0,
                                 'cpu_seconds': time.process_time()-cpu0,
                                 'peak_RSS_KiB_Linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                 'maximum_workers': 1, 'memory_limit_GiB': 2,
                                 'python_version': sys.version, 'python_executable': sys.executable,
                                 'platform': platform.platform()}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=HERE/'predicted-counts.json')
    args = parser.parse_args()
    assert not args.output.exists(), 'write-once audit output already exists'
    answer = audit()
    with args.output.open('x') as stream:
        json.dump(answer, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'output': str(args.output), 'sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
                      'checks': answer['checks_and_scope']}, indent=2))
