"""Frozen one-attempt EXP-FROB-b8cf21 instrument.

Execution requires the Coordinator's published source-bound execution lock.
Only the declared thirteen task paths may be created. No retries or parameter
substitution. The imported checker uses no Sage arithmetic or producer code.
"""
import argparse
import collections
import contextlib
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
import pathlib
import platform
import resource
import shlex
import subprocess
import sys
import time
import traceback

TASK = 'TASK-20260907-ee1e3c'
EXP = 'EXP-FROB-b8cf21'
RUN = 'RUN-FROB-b8cf21-ee1e3c'
REL = pathlib.Path('experiments') / EXP / 'runs' / TASK
SPEC = pathlib.Path('experiments') / EXP / 'specification.yaml'
SEEDS = (2026090701, 2026090702)
MEMORY = 8 * 1024 ** 3
SERIALIZATION = {'calls': 0, 'wall_seconds': 0.0, 'cpu_seconds': 0.0}
NAMES = ('implementation.py', 'checker.py', 'manifest.yaml', 'fixtures.json', 'raw.jsonl', 'metrics.json', 'certificates.json', 'report.md', 'stdout.log', 'stderr.log', 'command.txt', 'environment.json', 'raw-result.json')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def rss():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == 'darwin' else value * 1024)


def load_checker():
    spec = importlib.util.spec_from_file_location('frob_integer_checker', REL / 'checker.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Instrument:
    def __init__(self, raw, checker, sage):
        self.raw, self.checker, self.sage = raw, checker, sage
        self.counts = collections.Counter()
        self.stages = collections.defaultdict(lambda: {'calls': 0, 'cpu_seconds': 0.0, 'wall_seconds': 0.0})
        self.fixtures = {'fields': [], 'cells': [], 'structural_rejections': []}
        self.metrics = {'covers': [], 'cells': [], 'costs': {}}
        self.certificates = {'fields': [], 'groups': [], 'modules': [], 'controls': [], 'pivots': [], 'anomalies': []}
        self.fields = {}
        self.first_calibration = set()

    def check_memory(self):
        if rss() > MEMORY:
            raise MemoryError('8 GiB resident high-water checkpoint threshold exceeded')

    def emit(self, kind, **data):
        self.check_memory()
        sw, sc = time.monotonic(), time.process_time()
        self.raw.write(json.dumps({'kind': kind, **data}, sort_keys=True, separators=(',', ':')) + '\n')
        self.stages['raw_serialization']['calls'] += 1
        self.stages['raw_serialization']['wall_seconds'] += time.monotonic() - sw
        self.stages['raw_serialization']['cpu_seconds'] += time.process_time() - sc
        self.counts['raw_records'] += 1
        if self.counts['raw_records'] % 256 == 0 or kind != 'pair_attempt':
            self.raw.flush()

    @contextlib.contextmanager
    def stage(self, name):
        start, cpu = time.monotonic(), time.process_time()
        try:
            yield
        finally:
            d = self.stages[name]
            d['calls'] += 1
            d['cpu_seconds'] += time.process_time() - cpu
            d['wall_seconds'] += time.monotonic() - start
            self.check_memory()

    def field(self, q, n):
        S = self.sage
        with self.stage('field_construction'):
            R = S.PolynomialRing(S.GF(q), 'z')
            chosen = None
            for coeff in itertools.product(range(q), repeat=n):
                self.counts['irreducible_polynomials_tested'] += 1
                f = R(list(coeff) + [1])
                good = bool(f.is_irreducible())
                self.emit('field_polynomial_candidate', q=q, n=n, coefficients=list(coeff) + [1], irreducible=good)
                if good:
                    chosen = f
                    break
            assert chosen is not None
            F = S.GF(q ** n, name='z', modulus=chosen)
            modulus = [int(x) for x in chosen.list()]
            independent = self.checker.Field(q, modulus)
            assert independent.irreducible(), 'independent irreducibility mismatch'
            values = [F(independent.digits(i)) for i in range(q ** n)]
            lookup = {v: i for i, v in enumerate(values)}
            assert len(lookup) == q ** n
            self.counts['field_elements_constructed'] += len(values)
            squares = collections.defaultdict(list)
            for i, v in enumerate(values):
                squares[lookup[v * v]].append(i)
                if i % 2048 == 0:
                    self.check_memory()
            pi = S.matrix(S.GF(q), [independent.digits(lookup[(F.gen() ** j) ** q]) for j in range(n)]).transpose()
            assert pi ** n == S.identity_matrix(S.GF(q), n)
            self.counts['frobenius_matrices'] += 1
            T = S.PolynomialRing(S.GF(q), 'T')
            factors = list((T.gen() ** n - 1).factor())
            assert all(int(e) == 1 for f, e in factors)
            hs = []
            for mask in range(1, 1 << len(factors)):
                h = T.one()
                for j, (fac, exponent) in enumerate(factors):
                    if mask & (1 << j):
                        h *= fac
                if int(h.degree()) in (1, 2):
                    hs.append(h)
            hs.sort(key=lambda h: (int(h.degree()), tuple(int(v) for v in h.list())))
            modules = []
            I = S.identity_matrix(S.GF(q), n)
            for h in hs:
                M = S.zero_matrix(S.GF(q), n)
                for i, coeff in enumerate(h.list()):
                    M += coeff * pi ** i
                K = M.right_kernel()
                assert K.dimension() == h.degree()
                for vector in K.basis():
                    assert (M * (pi * vector)).is_zero()
                entry = {'h': [int(x) for x in h.list()], 'degree': int(h.degree()), 'dimension': int(K.dimension()), 'kernel_basis': [[int(x) for x in v] for v in K.basis()]}
                modules.append((entry, M))
            field = {'q': q, 'n': n, 'F': F, 'values': values, 'lookup': lookup, 'squares': squares, 'pi': pi, 'modules': modules, 'independent': independent}
            self.fields[(q, n)] = field
            fixture = {'q': q, 'n': n, 'modulus': modulus, 'frobenius_matrix': [[int(x) for x in row] for row in pi.rows()], 'factors': [[int(x) for x in h.list()] for h, e in factors], 'modules': [x[0] for x in modules]}
            self.fixtures['fields'].append(fixture)
            self.certificates['fields'].append({'q': q, 'n': n, 'sage_irreducibility': True, 'integer_polynomial_irreducibility': True, 'pi_power_n_identity': True})
            self.emit('field_constructed', **fixture)
            return field

    def encoded(self, field, Q):
        if Q.is_zero():
            return None
        return (field['lookup'][Q[0]], field['lookup'][Q[1]])

    def add(self, P, Q):
        self.counts['sage_group_additions'] += 1
        return P + Q

    def mul(self, k, P):
        self.counts['scalar_multiplications'] += 1
        out = P.curve()(0)
        while k:
            if k & 1:
                out = self.add(out, P)
            P = self.add(P, P)
            k >>= 1
        return out

    def enumerate_affine(self, field, E):
        A, B = E.a4(), E.a6()
        for x_enc, x in enumerate(field['values']):
            rhs = x * x * x + A * x + B
            for y_enc in field['squares'].get(field['lookup'][rhs], []):
                self.counts['affine_points_scanned'] += 1
                yield E(x, field['values'][y_enc])
            if x_enc % 1024 == 0:
                self.check_memory()

    def make_group(self, field, E, order, N, tag, object_arm):
        with self.stage('subgroup_generator_search'):
            generator = None
            scanned = 0
            for Q in self.enumerate_affine(field, E):
                scanned += 1
                P = self.mul(order // N, Q)
                self.emit('generator_candidate', tag=tag, prime=N, scan_index=scanned - 1, point=self.encoded(field, Q), cofactor_image=self.encoded(field, P))
                if not P.is_zero():
                    generator = P
                    break
            if generator is None:
                return None, 'no_nonzero_cofactor_image'
            assert self.mul(N, generator).is_zero()
            E2 = self.checker.Curve(field['independent'], field['lookup'][E.a4()], field['lookup'][E.a6()])
            encP = self.encoded(field, generator)
            assert self.checker.is_prime(N) and E2.valid(encP) and E2.mul(N, encP) is None
            group_sage, group = [E(0)], [None]
            P = generator
            for i in range(1, N):
                group_sage.append(P)
                group.append(self.encoded(field, P))
                P = self.add(P, generator)
                if i % 1024 == 0:
                    self.check_memory()
            assert P.is_zero() and len(set(group)) == N
            points = dict(zip(group, group_sage))
            logs = {Q: k for k, Q in enumerate(group)}
            mu = None
            if object_arm:
                q, n = field['q'], field['n']
                piP = E(generator[0] ** q, generator[1] ** q)
                # Exhaustive lookup is charged and recorded; never used to construct a relation.
                for k, Q in enumerate(group_sage):
                    self.counts['mu_exhaustive_lookup_comparisons'] += 1
                    if Q == piP:
                        mu = k
                        break
                if mu is None or pow(mu, n, N) != 1 or any(pow(mu, k, N) == 1 for k in range(1, n)):
                    return None, 'frobenius_eigenvalue_order_not_n'
                for i, Q in enumerate(group_sage[1:], 1):
                    piQ = E(Q[0] ** q, Q[1] ** q)
                    assert piQ == self.mul(mu, Q)
                    encQ = group[i]
                    other = (field['independent'].power(encQ[0], q), field['independent'].power(encQ[1], q))
                    assert E2.mul(mu, encQ) == other
            self.counts['subgroup_points_enumerated'] += N
            data = {'field': field, 'E': E, 'E2': E2, 'order': order, 'N': N, 'generator': encP, 'group': group, 'points': points, 'logs': logs, 'mu': mu, 'bases': [], 'arm': 'object' if object_arm else 'null', 'tag': tag}
            self.certificates['groups'].append({'tag': tag, 'N': N, 'generator': encP, 'order_N_sage': True, 'order_N_integer_arithmetic': True, 'mu': mu, 'point_scan_count': scanned})
            return data, None

    def quotient(self, cell, union, presentation):
        field, N = cell['field'], cell['N']
        object_frob = presentation == 'frobenius_negation'
        representatives = {}
        for Q in union:
            options = []
            S = cell['points'][Q]
            for k in range(field['n'] if object_frob else 1):
                for sign in (1, -1):
                    target = S if sign == 1 else -S
                    rep = self.encoded(field, target)
                    # rep = sign * mu^k * Q; invert to express Q in the rep column.
                    inverse = pow((sign * pow(cell['mu'], k, N)) % N, -1, N) if object_frob else sign % N
                    options.append((rep, inverse))
                    self.counts['orbit_canonicalization_candidates'] += 1
                if object_frob:
                    S = cell['E'](S[0] ** field['q'], S[1] ** field['q'])
            rep, weight = min(options, key=lambda x: x[0])
            assert cell['E2'].mul(weight, rep) == Q
            assert self.encoded(field, self.mul(weight, cell['points'][rep])) == Q
            representatives[Q] = (rep, weight)
        columns = sorted({r for r, w in representatives.values()})
        indices = {Q: i for i, Q in enumerate(columns)}
        weights = {Q: (indices[r], w) for Q, (r, w) in representatives.items()}
        return weights, [{'point': Q, 'column': indices[r], 'representative': r, 'weight': w} for Q, (r, w) in sorted(representatives.items())]

    def rank_data(self, cell, rows, columns, tag):
        N, S = cell['N'], self.sage
        same_rows = [r for r, same in rows if same]
        basis = self.checker.Basis(N)
        for r in same_rows:
            basis.insert(dict(r))
        same_rank = len(basis.pivots)
        pivots = []
        for r, same in rows:
            witness = basis.insert(dict(r))
            if witness is not None:
                pivots.append({'source_row': [list(x) for x in r], 'residual': witness})
        all_rank = len(basis.pivots)
        all_matrix = S.matrix(S.GF(N), len(rows), columns, {(i, j): value for i, (row, _) in enumerate(rows) for j, value in row}, sparse=True)
        same_matrix = S.matrix(S.GF(N), len(same_rows), columns, {(i, j): value for i, row in enumerate(same_rows) for j, value in row}, sparse=True)
        assert int(all_matrix.rank()) == all_rank and int(same_matrix.rank()) == same_rank
        self.counts['modular_rank_insertions'] += basis.updates
        self.counts['sage_matrix_rank_calls'] += 2
        self.counts['matrix_nonzero_entries_processed'] += sum(len(r) for r, _ in rows)
        self.certificates['pivots'].append({'tag': tag, 'same_rank': same_rank, 'all_rank': all_rank, 'added': pivots})
        # Every unique nonzero reduced row receives the scalar-multiple null.
        mu = cell['mu'] if cell['mu'] is not None else 1
        for row, same in rows:
            rb = self.checker.Basis(N)
            first = rb.insert(dict(row))
            for k in range(cell['field']['n']):
                mult = {j: value * pow(mu, k, N) % N for j, value in row}
                assert rb.insert(mult) is None
            assert len(rb.pivots) == int(bool(row))
            self.counts['scalar_rank_null_rows_checked'] += 1
            self.counts['modular_rank_insertions'] += rb.updates
        return {'U': columns, 'all_rank': all_rank, 'same_rank': same_rank, 'Delta_rank': all_rank - same_rank, 'rank_deficit': columns - all_rank, 'unique_rows': len(rows), 'matrix_nonzero_entries': sum(len(r) for r, _ in rows), 'maximum_coefficient_bits': max((v.bit_length() for r, _ in rows for j, v in r), default=0), 'added_pivot_witnesses': len(pivots)}

    def calibration(self, cell, base):
        """Run on first nonempty candidate before remaining candidate enumeration."""
        tag = cell['tag'] + ':precompute'
        self.emit('calibration_start', tag=tag, points=sorted(base))
        for presentation in ('negation', 'frobenius_negation'):
            w, entries = self.quotient(cell, base, presentation)
            rows = {}
            for index, (Q1, Q2) in enumerate(itertools.product(sorted(base), repeat=2)):
                Q3 = self.encoded(cell['field'], -self.add(cell['points'][Q1], cell['points'][Q2]))
                accepted = Q3 is not None and Q3 in base
                self.emit('calibration_pair', tag=tag, presentation=presentation, index=index, Q1=Q1, Q2=Q2, Q3=Q3, accepted=accepted)
                self.counts['calibration_ordered_pairs'] += 1
                if accepted:
                    assert cell['E2'].add(cell['E2'].add(Q1, Q2), Q3) is None
                    r = tuple(sorted(self.checker.row_from_triple((Q1, Q2, Q3), w, cell['N']).items()))
                    rows[r] = True
            m = self.rank_data(cell, list(rows.items()), len({e['column'] for e in entries}), tag + ':' + presentation)
            assert m['Delta_rank'] == 0
            self.certificates['controls'].append({'tag': tag, 'presentation': presentation, 'kind': 't1_precompute', 'passed': True, 'nonempty_base_size': len(base), **m})
        self.first_calibration.add((cell['field']['q'], cell['field']['n']))

    def candidates(self, cell):
        with self.stage('module_candidate_enumeration'):
            field = cell['field']
            sets = {}
            for module, matrix in field['modules']:
                base = set()
                for Q in sorted(cell['group'][1:]):
                    vec = self.sage.vector(self.sage.GF(field['q']), field['independent'].digits(Q[0]))
                    self.counts['module_membership_tests'] += 1
                    if (matrix * vec).is_zero():
                        base.add(Q)
                # Independent linearized-polynomial membership arithmetic.
                for Q in cell['group'][1:]:
                    xx, value = Q[0], 0
                    for coeff in module['h']:
                        value = field['independent'].add(value, field['independent'].mul(coeff, xx))
                        xx = field['independent'].power(xx, field['q'])
                    assert (value == 0) == (Q in base)
                assert all(self.encoded(field, -cell['points'][Q]) in base for Q in base)
                key = tuple(sorted(base))
                if key not in sets:
                    sets[key] = {'labels': [], 'points': sorted(base)}
                sets[key]['labels'].append(module['h'])
                self.emit('module_candidate', tag=cell['tag'], module=module, points=sorted(base), duplicate=len(sets[key]['labels']) > 1)
                if base and (field['q'], field['n']) not in self.first_calibration:
                    self.calibration(cell, base)
            cell['bases'] = list(sets.values())
            eligible = [set(map(tuple, b['points'])) for b in cell['bases'] if len(b['points']) >= 2 * field['n']]
            union = set().union(*(set(map(tuple, b['points'])) for b in cell['bases']))
            orbits = 0
            if union:
                weights, entries = self.quotient(cell, union, 'frobenius_negation')
                orbits = len({e['column'] for e in entries})
            return len(eligible) >= 2 and orbits >= 2, {'distinct_sets_size_at_least_2n': len(eligible), 'full_union_size': len(union), 'frobenius_negation_orbits': orbits, 'all_candidates': cell['bases']}

    def cardinality_check(self, cell):
        with self.stage('independent_cardinality_verification'):
            independent = cell['E2'].cardinality(self.check_memory)
            assert independent == cell['order'], 'curve cardinality mismatch'
            self.certificates['groups'].append({'tag': cell['tag'], 'sage_order': cell['order'], 'integer_polynomial_direct_count': independent, 'passed': True})
            self.counts['independent_full_curve_counts'] += 1

    def objects(self, q, n):
        field, S = self.field(q, n), self.sage
        chosen, seen_j = [], set()
        for A, B in itertools.product(range(q), repeat=2):
            tag = f'q{q}-n{n}-A{A}-B{B}'
            event = {'q': q, 'n': n, 'A': A, 'B': B, 'tag': tag}
            self.counts['object_curve_candidates'] += 1
            if (4 * A ** 3 + 27 * B ** 2) % q == 0:
                self.emit('object_curve_rejected', **event, reason='singular')
                continue
            with self.stage('curve_count_and_factor_search'):
                E0 = S.EllipticCurve(S.GF(q), [A, B])
                base_order = int(E0.cardinality())
                self.counts['sage_point_count_calls'] += 1
                trace = q + 1 - base_order
                if trace % q == 0:
                    self.emit('object_curve_rejected', **event, base_order=base_order, reason='supersingular')
                    continue
                E = S.EllipticCurve(field['F'], [A, B])
                j = field['lookup'][E.j_invariant()]
                if j in seen_j:
                    self.emit('object_curve_rejected', **event, j=j, reason='already_selected_j')
                    continue
                order = int(E.cardinality())
                self.counts['sage_point_count_calls'] += 1
                t0, t1 = 2, trace
                for k in range(2, n + 1):
                    t0, t1 = t1, trace * t1 - q * t0
                assert order == q ** n + 1 - t1, 'base trace recurrence mismatch'
                factors = [(int(p), int(e)) for p, e in S.factor(order)]
                self.counts['integer_factorizations'] += 1
                eligible_primes = sorted([p for p, e in factors if p >= 17 and e == 1 and base_order % p != 0], reverse=True)
                self.emit('object_curve_order', **event, base_order=base_order, order=order, factorization=factors, eligible_primes=eligible_primes)
            if not eligible_primes:
                self.emit('object_curve_rejected', **event, reason='no_eligible_prime')
                continue
            # Largest declared eligible prime; a failed mu gate rejects this curve.
            N = eligible_primes[0]
            cell, reason = self.make_group(field, E, order, N, tag, True)
            if cell is None:
                self.emit('object_curve_rejected', **event, N=N, reason=reason)
                continue
            self.cardinality_check(cell)
            eligible, structure = self.candidates(cell)
            if not eligible:
                rejection = {**event, 'N': N, 'reason': 'candidate_structure', **structure}
                self.fixtures['structural_rejections'].append(rejection)
                self.emit('object_curve_rejected', **rejection)
                continue
            cell['id'] = f'FROB-q{q}-n{n}-object{len(chosen) + 1:02d}'
            cell['j'] = j
            cell['base_order'] = base_order
            chosen.append(cell)
            seen_j.add(j)
            self.emit('object_curve_selected', id=cell['id'], **event, N=N, structure=structure)
            if len(chosen) == 2:
                break
        return field, chosen

    def null(self, object_cell):
        field, S = object_cell['field'], self.sage
        q, N = field['q'], object_cell['N']
        union = set().union(*(set(map(tuple, b['points'])) for b in object_cell['bases']))
        for a, b in itertools.product(range(q), repeat=2):
            A, B = field['F'].gen() + a, field['F'].gen() + b
            tag = object_cell['id'] + f'-null-a{a}-b{b}'
            event = {'object': object_cell['id'], 'a': a, 'b': b, 'tag': tag}
            self.counts['null_curve_candidates'] += 1
            if 4 * A ** 3 + 27 * B ** 2 == 0:
                self.emit('null_curve_rejected', **event, reason='singular')
                continue
            E = S.EllipticCurve(field['F'], [A, B])
            if E.j_invariant() ** q == E.j_invariant():
                self.emit('null_curve_rejected', **event, reason='subfield_j')
                continue
            with self.stage('null_curve_count_and_factor_search'):
                order = int(E.cardinality())
                self.counts['sage_point_count_calls'] += 1
                factors = [(int(p), int(e)) for p, e in S.factor(order)]
                self.counts['integer_factorizations'] += 1
                primes = sorted([p for p, e in factors if e == 1 and N <= 2 * p and p <= 2 * N and p - 1 >= len(union)], reverse=True)
                self.emit('null_curve_order', **event, order=order, factorization=factors, eligible_primes=primes)
            if not primes:
                self.emit('null_curve_rejected', **event, reason='no_matched_prime')
                continue
            cell, reason = self.make_group(field, E, order, primes[0], tag, False)
            assert cell is not None, 'selected prime subgroup could not be generated: ' + str(reason)
            self.cardinality_check(cell)
            cell['j'] = field['lookup'][E.j_invariant()]
            return cell
        return None

    def null_labels(self, object_cell, null_cell, seed):
        field = object_cell['field']
        object_union = set().union(*(set(map(tuple, b['points'])) for b in object_cell['bases']))
        opairs = sorted({min(Q, object_cell['E2'].neg(Q)) for Q in object_union})
        npairs = {min(Q, null_cell['E2'].neg(Q)) for Q in null_cell['group'][1:]}
        npairs = sorted(npairs, key=lambda Q: self.checker.label(seed, Q))
        assert len(npairs) >= len(opairs)
        mapping = {}
        for Q, R in zip(opairs, npairs):
            mapping[Q] = R
            mapping[object_cell['E2'].neg(Q)] = null_cell['E2'].neg(R)
        cell = dict(null_cell)
        cell['id'] = object_cell['id'] + f'-null-seed{seed}'
        cell['seed'] = seed
        cell['object_id'] = object_cell['id']
        cell['bases'] = [{'labels': b['labels'], 'points': sorted(mapping[tuple(Q)] for Q in b['points'])} for b in object_cell['bases']]
        cell['membership_transport'] = [{'object': Q, 'null': R} for Q, R in sorted(mapping.items())]
        for subset in itertools.chain.from_iterable(itertools.combinations(range(len(cell['bases'])), t) for t in range(1, len(cell['bases']) + 1)):
            lhs = set.intersection(*(set(map(tuple, object_cell['bases'][i]['points'])) for i in subset))
            rhs = set.intersection(*(set(map(tuple, cell['bases'][i]['points'])) for i in subset))
            assert len(lhs) == len(rhs)
        self.counts['null_membership_points_transported'] += len(mapping)
        return cell

    def record_cell(self, cell):
        field = cell['field']
        union = set().union(*(set(map(tuple, b['points'])) for b in cell['bases']))
        presentations = ('negation', 'frobenius_negation') if cell['arm'] == 'object' else ('negation',)
        cell['weights'], maps = {}, {}
        for p in presentations:
            cell['weights'][p], maps[p] = self.quotient(cell, union, p)
        fixture = {'id': cell['id'], 'status': 'selected', 'q': field['q'], 'n': field['n'], 'A': field['lookup'][cell['E'].a4()], 'B': field['lookup'][cell['E'].a6()], 'j': cell['j'], 'N': cell['N'], 'order': cell['order'], 'generator': cell['generator'], 'group': cell['group'], 'mu': cell['mu'], 'bases': cell['bases'], 'arm': cell['arm'], 'quotient_maps': maps}
        for key in ('seed', 'object_id', 'membership_transport', 'base_order'):
            if key in cell:
                fixture[key] = cell[key]
        self.fixtures['cells'].append(fixture)
        self.emit('cell_fixture', **fixture)
        return fixture

    def covers(self, cell):
        field, N = cell['field'], cell['N']
        bases = [set(map(tuple, b['points'])) for b in cell['bases']]
        nonempty = [i for i, B in enumerate(bases) if B]
        # Generic representation uses only the already charged subgroup table.
        generic = {}
        for seed in SEEDS:
            ordered = sorted(cell['group'][1:], key=lambda Q: self.checker.label(seed, Q))
            encode = {Q: i for i, Q in enumerate(ordered, 1)}
            encode[None] = 0
            decode = {v: Q for Q, v in encode.items()}
            generic[seed] = (encode, decode)
            self.counts['generic_label_table_entries'] += len(encode)
        for t in (1, 2, 3):
            for cover in itertools.combinations(nonempty, t):
                with self.stage('cover_incidence_rank_verification'):
                    coverid = ','.join(map(str, cover))
                    union = sorted(set().union(*(bases[i] for i in cover)))
                    union_set = set(union)
                    # Compress presentation columns to this exact cover's union.
                    weights = {}
                    for name, wm in cell['weights'].items():
                        used = sorted({wm[Q][0] for Q in union})
                        relabel = {j: k for k, j in enumerate(used)}
                        weights[name] = {Q: (relabel[wm[Q][0]], wm[Q][1]) for Q in union}
                    rows = {p: {} for p in weights}
                    generic_rows = {seed: {p: {} for p in weights} for seed in SEEDS}
                    accepted_count = same_count = 0
                    unique_single_pairs = len(set().union(*(set(itertools.product(bases[i], repeat=2)) for i in cover)))
                    altered_checked = False
                    for index, (Q1, Q2) in enumerate(itertools.product(union, repeat=2)):
                        Q3 = self.encoded(field, -self.add(cell['points'][Q1], cell['points'][Q2]))
                        accepted = Q3 is not None and Q3 in union_set
                        same = accepted and any(Q1 in bases[i] and Q2 in bases[i] and Q3 in bases[i] for i in cover)
                        self.counts['ordered_pairs_including_failures'] += 1
                        self.emit('pair_attempt', cell=cell['id'], cover=coverid, base_indices=list(cover), index=index, Q1=Q1, Q2=Q2, Q3=Q3, accepted=accepted, same_base=bool(same))
                        # Relabel every accepted/rejected attempt and use calibration table solely in this control.
                        for seed, (enc, dec) in generic.items():
                            a, b = enc[Q1], enc[Q2]
                            scalar_sum = (cell['logs'][dec[a]] + cell['logs'][dec[b]]) % N
                            third_label = enc[cell['group'][(-scalar_sum) % N]]
                            G3 = dec[third_label]
                            assert G3 == Q3 and (G3 is not None and G3 in union_set) == accepted
                            self.counts['generic_relabel_attempt_checks'] += 1
                        if not accepted:
                            continue
                        accepted_count += 1
                        same_count += int(same)
                        triple = (Q1, Q2, Q3)
                        assert cell['E2'].add(cell['E2'].add(Q1, Q2), Q3) is None
                        self.counts['independent_relation_checks'] += 1
                        if not altered_checked:
                            # Add one to the first point coefficient, retaining any accidental validity.
                            altered = cell['E2'].add(cell['E2'].add(cell['E2'].add(Q1, Q1), Q2), Q3)
                            accidental = altered is None
                            self.certificates['controls'].append({'cell': cell['id'], 'cover': coverid, 'kind': 'altered_point_coefficient', 'triple': triple, 'coefficients': [2, 1, 1], 'accidentally_valid': accidental, 'rejected': not accidental})
                            if accidental:
                                assert cell['E2'].mul(1, cell['generator']) is not None
                                self.certificates['controls'].append({'cell': cell['id'], 'cover': coverid, 'kind': 'synthetic_generator_row_one', 'rejected': True})
                            altered_checked = True
                        for name, wm in weights.items():
                            row = self.checker.row_from_triple(triple, wm, N)
                            r = tuple(sorted(row.items()))
                            rows[name][r] = rows[name].get(r, False) or bool(same)
                            # Known calibration logs are checks, never row construction inputs.
                            column_logs = {}
                            for Q in union:
                                col, weight = wm[Q]
                                column_logs[col] = cell['logs'][Q] * pow(weight, -1, N) % N
                            assert sum(v * column_logs[j] for j, v in row.items()) % N == 0
                            for seed, (enc, dec) in generic.items():
                                transported = {enc[Q]: value for Q, value in wm.items()}
                                rr = collections.Counter()
                                for Q in triple:
                                    col, weight = transported[enc[Q]]
                                    rr[col] = (rr[col] + weight) % N
                                rr = tuple(sorted((j, v) for j, v in rr.items() if v))
                                assert rr == r
                                generic_rows[seed][name][rr] = generic_rows[seed][name].get(rr, False) or bool(same)
                    if not altered_checked:
                        assert cell['E2'].mul(1, cell['generator']) is not None
                        self.certificates['controls'].append({'cell': cell['id'], 'cover': coverid, 'kind': 'synthetic_generator_row_one_no_accepted_relation', 'rejected': True})
                    presentations = {}
                    for name, unique_rows in rows.items():
                        row_list = sorted(unique_rows.items())
                        U = len({col for col, weight in weights[name].values()})
                        result = self.rank_data(cell, row_list, U, cell['id'] + ':' + coverid + ':' + name)
                        if t == 1:
                            assert result['Delta_rank'] == 0 and all(same for row, same in row_list)
                        for seed in SEEDS:
                            assert generic_rows[seed][name] == unique_rows
                            self.certificates['controls'].append({'cell': cell['id'], 'cover': coverid, 'presentation': name, 'seed': seed, 'kind': 'generic_relabel', 'incidence_rows_weights_identical': True, 'same_rank': result['same_rank'], 'all_rank': result['all_rank'], 'table_entries': len(cell['group'])})
                        delta = result['Delta_rank']
                        result['denominator_zero'] = delta == 0
                        result['ordered_pairs_per_Delta_rank_exact'] = None if delta == 0 else {'numerator': len(union) ** 2, 'denominator': delta}
                        presentations[name] = result
                    record = {'cell': cell['id'], 'cover': coverid, 'base_indices': list(cover), 't': t, 'union_size': len(union), 'ordered_pairs': len(union) ** 2, 'unique_single_base_pairs': unique_single_pairs, 'accepted_pairs': accepted_count, 'same_base_accepted_pairs': same_count, 'mixed_accepted_pairs': accepted_count - same_count, 'presentations': presentations}
                    self.metrics['covers'].append(record)
                    self.emit('cover_summary', **record)
        self.metrics['cells'].append({'id': cell['id'], 'status': 'completed', 'arm': cell['arm'], 'N': N, 'cover_count': sum(c['cell'] == cell['id'] for c in self.metrics['covers'])})

    def panel(self):
        for q, n in ((7, 3), (11, 5)):
            field, objects = self.objects(q, n)
            for object_cell in objects:
                self.record_cell(object_cell)
                self.covers(object_cell)
                null = self.null(object_cell)
                for seed in SEEDS:
                    cid = object_cell['id'] + f'-null-seed{seed}'
                    if null is None:
                        self.metrics['cells'].append({'id': cid, 'status': 'unmatched_control', 'reason': 'fixed_null_curve_pool_exhausted'})
                        self.fixtures['cells'].append({'id': cid, 'status': 'unmatched_control'})
                        self.emit('cell_terminal', id=cid, status='unmatched_control')
                    else:
                        cell = self.null_labels(object_cell, null, seed)
                        self.record_cell(cell)
                        self.covers(cell)
            for k in range(len(objects) + 1, 3):
                cid = f'FROB-q{q}-n{n}-object{k:02d}'
                for missing in [cid] + [cid + f'-null-seed{seed}' for seed in SEEDS]:
                    status = 'ineligible_object' if missing == cid else 'not_run_no_eligible_object'
                    self.metrics['cells'].append({'id': missing, 'status': status, 'reason': 'fixed_object_curve_pool_exhausted'})
                    self.fixtures['cells'].append({'id': missing, 'status': status})
                    self.emit('cell_terminal', id=missing, status=status)


def validate_lock(lock_path, command):
    lock = json.loads(lock_path.read_text())
    assert lock.get('task_id') == TASK and lock.get('scientific_execution_authorized') is True, 'no execution authorization'
    assert lock.get('command') == command, 'exact command mismatch'
    sources = lock.get('source_sha256', {})
    assert set(sources) == {str(REL / 'implementation.py'), str(REL / 'checker.py')}, 'source binding set mismatch'
    for path, digest in {**sources, **lock.get('input_sha256', {})}.items():
        assert sha(path) == digest, 'bound input/source hash mismatch: ' + path
    assert str(SPEC) in lock.get('input_sha256', {}), 'specification must be lock-bound'
    assert lock.get('environment', {}).get('DOT_SAGE') == '/private/tmp/frobenius-sage-runtime-20260909', 'Sage cache lock absent'
    assert os.environ.get('DOT_SAGE') == lock['environment']['DOT_SAGE'], 'Sage cache environment mismatch'
    for key in ('configured_model', 'served_model_id', 'served_provider'):
        assert 'bedrock' not in str(lock.get(key, '')).lower(), 'prohibited backend'
    for name in NAMES:
        if name not in ('implementation.py', 'checker.py'):
            assert not (REL / name).exists(), 'immutable first-attempt output collision: ' + name
    return lock


def write_json(path, value):
    wall, cpu = time.monotonic(), time.process_time()
    with open(path, 'x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')
    SERIALIZATION['calls'] += 1
    SERIALIZATION['wall_seconds'] += time.monotonic() - wall
    SERIALIZATION['cpu_seconds'] += time.process_time() - cpu


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execution-lock', required=True)
    args = parser.parse_args()
    assert pathlib.Path.cwd().joinpath('AGENTS.md').exists(), 'run from the bound checkout root'
    command = shlex.join([sys.executable, '-B', str(REL / 'implementation.py'), '--execution-lock', args.execution_lock])
    lock_path = pathlib.Path(args.execution_lock)
    lock = validate_lock(lock_path, command)
    started, wall0, cpu0 = utc(), time.monotonic(), time.process_time()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    dirty_status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=all'], text=True)
    diff = subprocess.check_output(['git', 'diff', '--', str(REL / 'implementation.py'), str(REL / 'checker.py')], text=True)
    with open(REL / 'command.txt', 'x') as f:
        f.write(command + '\n')
    checker = load_checker()
    status, error, inst = 'completed_valid', None, None
    environment = {'operating_system': platform.platform(), 'architecture': platform.machine(), 'python_version': sys.version, 'python_executable': sys.executable, 'DOT_SAGE': os.environ.get('DOT_SAGE'), 'sage_version': None, 'dependencies': {}, 'native_runtime_lock': lock, 'execution_lock_path': str(lock_path), 'execution_lock_sha256': sha(lock_path), 'git_status_at_start': dirty_status, 'relevant_tracked_diff': diff, 'source_sha256': lock['source_sha256'], 'memory_protection': {'limit_bytes': MEMORY, 'measurement': 'resource.getrusage(RUSAGE_SELF).ru_maxrss; Darwin bytes, other platforms KiB converted to bytes', 'checkpoints': 'raw records, stage boundaries and large arithmetic loops', 'hard_virtual_memory_limit': None}}
    out = open(REL / 'stdout.log', 'x', buffering=1)
    err = open(REL / 'stderr.log', 'x', buffering=1)
    raw = open(REL / 'raw.jsonl', 'x', buffering=1)
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            import sage.all as sage
            from sage.env import SAGE_VERSION
            environment['sage_version'] = SAGE_VERSION
            assert SAGE_VERSION == '10.9', 'locked Sage version mismatch'
            inst = Instrument(raw, checker, sage)
            print(json.dumps({'event': 'aggregate_started', 'run': RUN, 'timestamp': started, 'head': revision}), flush=True)
            inst.panel()
        except MemoryError as exc:
            status, error = 'resource_exhaustion', repr(exc)
            traceback.print_exc()
        except (ImportError, OSError) as exc:
            status, error = 'failed_infrastructure', repr(exc)
            traceback.print_exc()
        except Exception as exc:
            status, error = 'failed_implementation', repr(exc)
            traceback.print_exc()
        if inst is None:
            fixtures, metrics, certificates = {'fields': [], 'cells': []}, {'covers': [], 'cells': []}, {'anomalies': []}
        else:
            fixtures, metrics, certificates = inst.fixtures, inst.metrics, inst.certificates
        spec = json.loads(SPEC.read_text())['experiment']
        planned = spec['inputs']['cell_ids'] + spec['inputs']['null_cell_ids']
        observed = {c['id'] for c in metrics['cells']}
        for cid in planned:
            if cid not in observed:
                metrics['cells'].append({'id': cid, 'status': 'not_run_after_operational_failure', 'reason': error})
        write_json(REL / 'fixtures.json', fixtures)
        # These are the immutable replay inputs. Aggregate costs are finalized in raw-result/manifest.
        write_json(REL / 'metrics.json', metrics)
        raw.flush()
        if status == 'completed_valid':
            try:
                cwall, ccpu = time.monotonic(), time.process_time()
                audit = checker.audit_package(REL, inst.check_memory)
                audit['cpu_seconds'] = time.process_time() - ccpu
                audit['wall_seconds'] = time.monotonic() - cwall
                certificates['package_checker'] = audit
            except Exception as exc:
                status, error = 'completed_invalid', 'independent checker: ' + repr(exc)
                traceback.print_exc()
        if error:
            certificates.setdefault('anomalies', []).append({'failure': error, 'status': status, 'scientific_interpretation': None})
        print(json.dumps({'event': 'aggregate_terminal', 'run': RUN, 'status': status, 'error': error}), flush=True)
    raw.close()
    out.close()
    err.close()
    timing = {'started_at': started, 'finished_at': utc(), 'wall_seconds': time.monotonic() - wall0, 'cpu_seconds': time.process_time() - cpu0, 'boundary': 'aggregate start through raw/fixture/metric generation and checker plus log close; final envelope serialization separately timed'}
    costs = {'measured': True, 'artifact_serialization_through_checker_input': dict(SERIALIZATION), 'stages': {} if inst is None else dict(inst.stages), 'counts': {} if inst is None else dict(inst.counts), 'instrument_cpu_seconds': timing['cpu_seconds'], 'instrument_wall_seconds': timing['wall_seconds'], 'peak_rss_bytes': rss(), 'arithmetic_checker_counts': {} if inst is None else {f'q{q}-n{n}': dict(f['independent'].ops) for (q, n), f in inst.fields.items()}, 'unmeasured_attack_phases': ['Groebner solving', 'sparse attack linear algebra', 'target descent', 'rho', 'BSGS'], 'no_attack_timings_inferred': True}
    normalized = []
    for cover in metrics['covers']:
        for presentation, value in cover['presentations'].items():
            delta = value['Delta_rank']
            normalized.append({'cell': cover['cell'], 'cover': cover['cover'], 'presentation': presentation, 'Delta_rank': delta, 'denominator_zero': delta == 0, 'total_aggregate_instrument_cpu_per_Delta_rank': None if delta == 0 else timing['cpu_seconds'] / delta, 'charging_scope': 'Entire aggregate instrument including unsuccessful candidate search, all other cells and checker; no selective amortization'})
    complete_panel = all(c['status'] == 'completed' for c in metrics['cells']) and len(metrics['cells']) == 12
    result = {'status': status, 'valid': status == 'completed_valid', 'invalid_reason': error, 'panel_complete': complete_panel, 'diagnostic_disposition': 'finite_panel_observations_pending_independent_review' if complete_panel else 'inconclusive_incomplete_selection_or_execution', 'metrics': metrics, 'costs': costs, 'normalization': normalized, 'certificate': {'kind': 'none', 'verified': None, 'verifier': None}, 'claims': [], 'frozen_prediction_reference': str(SPEC) + '#experiment/preregistered_prediction', 'interpretation': 'Exact finite signed-incidence instrument only. No hypothesis verdict, exponent gain, attack-cost improvement or Frobenius causality claimed.'}
    write_json(REL / 'certificates.json', certificates)
    write_json(REL / 'environment.json', environment)
    write_json(REL / 'raw-result.json', result)
    report = ['# Executor report', '', f'Experiment: {EXP}; task: {TASK}; run: {RUN}.', '', f'Terminal execution status: `{status}`. Complete 12-cell panel: `{complete_panel}`.', '', 'Only frozen q=7,n=3 and q=11,n=5 cells, fixed curve pools and seeds 2026090701/2026090702 were admitted.', 'DEC-20260909-b56f39 supplies prospective null-prime and label-byte definitions. No additional protocol deviations intended.', '', '| Cell | Terminal status |', '| --- | --- |']
    report += [f"| {c['id']} | {c['status']} |" for c in metrics['cells']]
    report += ['', f'Measured aggregate CPU: {timing["cpu_seconds"]:.9f} seconds; wall: {timing["wall_seconds"]:.9f} seconds; peak RSS: {costs["peak_rss_bytes"]} bytes.', 'These costs belong to the exhaustive instrument. Individual internal Sage cardinality/factorization primitive operations are opaque; call counts and measured stage costs are retained.', 'No Groebner, sparse attack linear algebra, target descent, rho or BSGS timing was measured.', '', 'Every pair attempt, including rejections, is in raw.jsonl. Exact fixtures, ranks, pivot and control checks remain separate from interpretation. The checker uses independent integer-polynomial arithmetic and affine formulas; it is producer-local verification and does not replace the scheduled independent session.', '', 'Selection exhaustion or operational failure is inconclusive and carries no mathematical verdict.', 'Source files are frozen before execution; actual executing revision and dirty state are recorded, including unrelated concurrent scratch.', '', 'The final manifest cannot hash itself; its final bytes are bound by the Coordinator snapshot. All twelve other declared artifacts are hash-bound in the manifest.', '', f'Anomalies: {error!r}.', 'Independent integrity review and Coordinator snapshot/archive remain required.', '']
    with open(REL / 'report.md', 'x') as f:
        f.write('\n'.join(report))
    artifacts = {name: {'path': str(REL / name), 'sha256': sha(REL / name), 'bytes': (REL / name).stat().st_size} for name in NAMES if name != 'manifest.yaml'}
    inference = {'requested_policy': 'executor-implementation', 'canonical_policy': 'executor-implementation', 'backend': 'native_codex', 'provider': None, 'resolved_model_id': None, 'model_provenance': 'operator-supplied', 'model_verified': False, 'requested_reasoning_effort': None, 'reasoning_effort': 'medium', 'configured_model_id': 'gpt-6-astra', 'serving_reasoning_effort': None, 'fallback_used': False, 'fallback_reason': None, 'degraded_requirements': [], 'independent_session': False, 'native_thread_id': lock.get('thread_id'), 'native_turn_id': lock.get('turn_id')}
    manifest = {'run': {'id': RUN, 'experiment_id': EXP, 'status': status, 'code': {'commit': revision, 'dirty': bool(dirty_status.strip()), 'command': command, 'source_sha256': lock['source_sha256'], 'relevant_diff': diff, 'execution_lock_sha256': sha(lock_path)}, 'inference': inference, 'environment': environment, 'inputs': {'seed': list(SEEDS), 'parameters': {'field_cells': [{'q': 7, 'n': 3}, {'q': 11, 'n': 5}], 'field_bits': [9, 18], 'planned_cell_ids': planned, 'maximum_runs': 1}, 'specification_sha256': sha(SPEC), 'effective_definition_decision': 'DEC-20260909-b56f39', 'controls': spec['controls'], 'actual_fixture_sha256': sha(REL / 'fixtures.json')}, 'timing': timing, 'resources': costs, 'result': result, 'artifacts': artifacts, 'manifest_self_hash': 'Excluded to avoid recursive hash; Coordinator snapshot binds final manifest bytes.', 'artifact_stored_bytes_excluding_manifest': sum(x['bytes'] for x in artifacts.values()), 'execution_report': {'experiment_id': EXP, 'implementation_commit': revision, 'protocol_deviations': [], 'runs': {'completed': [RUN] if status == 'completed_valid' else [], 'invalid': [RUN] if status == 'completed_invalid' else [], 'failed': [RUN] if status not in ('completed_valid', 'completed_invalid') else []}, 'observations': metrics['cells'], 'anomalies': [] if error is None else [error], 'artifact_paths': [str(REL / n) for n in NAMES], 'executor_assessment': {'protocol_complete': True, 'data_quality': 'good' if status == 'completed_valid' else 'invalid', 'requires_rerun': status != 'completed_valid'}}}}
    manifest['run']['final_envelope_serialization_before_manifest'] = dict(SERIALIZATION)
    manifest['run']['finalization_boundary'] = {'wall_seconds_through_pre_manifest': time.monotonic() - wall0, 'cpu_seconds_through_pre_manifest': time.process_time() - cpu0, 'peak_rss_bytes': rss(), 'excluded': 'Manifest serialization/write and interpreter shutdown; self-referential timing cannot be measured within its own bytes.'}
    write_json(REL / 'manifest.yaml', manifest)
    print(json.dumps({'run': RUN, 'status': status, 'panel_complete': complete_panel, 'manifest': str(REL / 'manifest.yaml'), 'error': error}), flush=True)
    return 0 if status == 'completed_valid' else 1


if __name__ == '__main__':
    sys.exit(main())
