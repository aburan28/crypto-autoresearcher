"""Independent integer-polynomial arithmetic and raw-attempt replay.

No Sage import and no import of the producer. This is a second arithmetic
implementation, not an independent-session research review.
"""
import collections
import hashlib
import itertools
import json
import pathlib


class Field:
    def __init__(self, q, modulus):
        self.q = q
        self.f = list(modulus)
        self.n = len(modulus) - 1
        self.size = q ** self.n
        self.ops = collections.Counter()
        assert self.f[-1] == 1

    def digits(self, a):
        out = []
        for _ in range(self.n):
            out.append(a % self.q)
            a //= self.q
        assert a == 0
        return out

    def encode(self, a):
        return sum((int(x) % self.q) * self.q ** i for i, x in enumerate(a))

    def add(self, a, b):
        self.ops['field_additions'] += 1
        return self.encode([(x + y) % self.q for x, y in zip(self.digits(a), self.digits(b))])

    def neg(self, a):
        return self.encode([-x for x in self.digits(a)])

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def mul(self, a, b):
        self.ops['field_multiplications'] += 1
        aa, bb = self.digits(a), self.digits(b)
        c = [0] * (2 * self.n - 1)
        for i, x in enumerate(aa):
            for j, y in enumerate(bb):
                c[i + j] = (c[i + j] + x * y) % self.q
        for k in range(len(c) - 1, self.n - 1, -1):
            u = c[k]
            for i in range(self.n):
                c[k - self.n + i] = (c[k - self.n + i] - u * self.f[i]) % self.q
        return self.encode(c[:self.n])

    def power(self, a, k):
        out = 1
        while k:
            if k & 1:
                out = self.mul(out, a)
            a = self.mul(a, a)
            k >>= 1
        return out

    def inv(self, a):
        assert a != 0
        return self.power(a, self.size - 2)

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def irreducible(self):
        # Rabin criterion with independent polynomial Euclidean arithmetic.
        def trim(a):
            a = [x % self.q for x in a]
            while a and not a[-1]:
                a.pop()
            return a
        def rem(a, b):
            a, b = trim(a), trim(b)
            while len(a) >= len(b) and a:
                s = len(a) - len(b)
                c = a[-1] * pow(b[-1], -1, self.q) % self.q
                for j, v in enumerate(b):
                    a[s + j] = (a[s + j] - c * v) % self.q
                a = trim(a)
            return a
        def gcd(a, b):
            while b:
                a, b = b, rem(a, b)
            return a
        x = self.q
        t = x
        for k in range(1, self.n + 1):
            t = self.power(t, self.q)
            if k <= self.n // 2 and len(gcd(self.f, self.digits(self.sub(t, x)))) > 1:
                return False
        return t == x


class Curve:
    def __init__(self, field, A, B):
        self.F, self.A, self.B = field, A, B
        self.ops = collections.Counter()

    def neg(self, P):
        return None if P is None else (P[0], self.F.neg(P[1]))

    def valid(self, P):
        if P is None:
            return True
        x, y = P
        F = self.F
        return F.mul(y, y) == F.add(F.add(F.mul(F.mul(x, x), x), F.mul(self.A, x)), self.B)

    def add(self, P, Q):
        self.ops['group_additions'] += 1
        if P is None:
            return Q
        if Q is None:
            return P
        F = self.F
        x, y = P
        u, v = Q
        if x == u and F.add(y, v) == 0:
            return None
        if P == Q:
            m = F.div(F.add(F.mul(3 % F.q, F.mul(x, x)), self.A), F.mul(2, y))
        else:
            m = F.div(F.sub(v, y), F.sub(u, x))
        xx = F.sub(F.sub(F.mul(m, m), x), u)
        yy = F.sub(F.mul(m, F.sub(x, xx)), y)
        return (xx, yy)

    def mul(self, k, P):
        out = None
        while k:
            if k & 1:
                out = self.add(out, P)
            P = self.add(P, P)
            k >>= 1
        return out

    def cardinality(self, checkpoint=lambda: None):
        F = self.F
        squares = collections.Counter()
        for y in range(F.size):
            squares[F.mul(y, y)] += 1
            if y % 2048 == 0:
                checkpoint()
        count = 1
        for x in range(F.size):
            rhs = F.add(F.add(F.mul(F.mul(x, x), x), F.mul(self.A, x)), self.B)
            count += squares[rhs]
            if x % 2048 == 0:
                checkpoint()
        return count


class Basis:
    """Sparse exact modular elimination, independent of Sage matrix.rank."""
    def __init__(self, prime):
        self.prime = prime
        self.pivots = {}
        self.updates = 0

    def insert(self, row):
        p = self.prime
        r = {int(k): int(v) % p for k, v in row.items() if int(v) % p}
        self.updates += 1
        for k, pivot in sorted(self.pivots.items()):
            if k in r:
                a = r[k]
                for j, b in pivot.items():
                    r[j] = (r.get(j, 0) - a * b) % p
                    if not r[j]:
                        del r[j]
        if not r:
            return None
        k = min(r)
        inv = pow(r[k], -1, p)
        r = {j: v * inv % p for j, v in r.items()}
        self.pivots[k] = r
        return {'pivot': k, 'row': [[j, v] for j, v in sorted(r.items())]}


def row_from_triple(triple, weights, modulus):
    r = collections.Counter()
    for Q in triple:
        col, weight = weights[tuple(Q)]
        r[col] = (r[col] + weight) % modulus
    return {k: v for k, v in r.items() if v}


def label(seed, P):
    return hashlib.sha256(f'{seed}:{P[0]},{P[1]}'.encode('ascii')).digest(), tuple(P)


def audit_package(directory, checkpoint=lambda: None):
    """Replay complete indexed pair tables and compare exact cover summaries."""
    directory = pathlib.Path(directory)
    fixtures = json.loads((directory / 'fixtures.json').read_text())
    expected = json.loads((directory / 'metrics.json').read_text())
    curves, cells, data = {}, {}, {}
    total_checks = 0
    for f in fixtures['fields']:
        F = Field(f['q'], f['modulus'])
        assert F.irreducible(), 'checker field irreducibility'
        curves[(f['q'], f['n'])] = F
    for cell in fixtures['cells']:
        if cell.get('status') != 'selected':
            continue
        F = curves[(cell['q'], cell['n'])]
        E = Curve(F, cell['A'], cell['B'])
        P = tuple(cell['generator'])
        N = cell['N']
        assert is_prime(N) and P is not None and E.valid(P) and E.mul(N, P) is None
        group = [None if Q is None else tuple(Q) for Q in cell['group']]
        assert len(group) == N and len(set(group)) == N
        assert group[0] is None
        for i, Q in enumerate(group):
            assert E.valid(Q) and E.add(Q, P) == group[(i + 1) % N]
            total_checks += 1
        if cell['arm'] == 'object':
            mu = cell['mu']
            assert pow(mu, cell['n'], N) == 1 and all(pow(mu, k, N) != 1 for k in range(1, cell['n']))
            for Q in group[1:]:
                piQ = (F.power(Q[0], F.q), F.power(Q[1], F.q))
                assert piQ == E.mul(mu, Q)
                total_checks += 1
        sets = [set(map(tuple, b['points'])) for b in cell['bases']]
        if cell['arm'] == 'object':
            for base_record, base in zip(cell['bases'], sets):
                for h in base_record['labels']:
                    independently_selected = set()
                    for Q in group[1:]:
                        power, value = Q[0], 0
                        for coefficient in h:
                            value = F.add(value, F.mul(coefficient, power))
                            power = F.power(power, F.q)
                        if value == 0:
                            independently_selected.add(Q)
                    assert independently_selected == base, 'module membership map'
            assert sum(len(B) >= 2 * cell['n'] for B in sets) >= 2
        else:
            parent = next(c for c in fixtures['cells'] if c['id'] == cell['object_id'])
            parent_curve = Curve(F, parent['A'], parent['B'])
            parent_union = set().union(*(set(map(tuple, b['points'])) for b in parent['bases']))
            opairs = sorted({min(Q, parent_curve.neg(Q)) for Q in parent_union})
            npairs = sorted({min(Q, E.neg(Q)) for Q in group[1:]}, key=lambda Q: label(cell['seed'], Q))
            transport = {}
            for Q, R in zip(opairs, npairs):
                transport[Q] = R
                transport[parent_curve.neg(Q)] = E.neg(R)
            assert len(transport) == len(parent_union)
            declared = {tuple(e['object']): tuple(e['null']) for e in cell['membership_transport']}
            assert transport == declared, 'null seed-byte/order/orientation transport'
            for source, target in zip(parent['bases'], sets):
                assert {transport[tuple(Q)] for Q in source['points']} == target

        for B in sets:
            assert None not in B and B <= set(group)
            assert all(E.neg(Q) in B for Q in B)
        weights_by = {}
        for presentation, entries in cell['quotient_maps'].items():
            weights = {tuple(e['point']): (e['column'], e['weight']) for e in entries}
            for e in entries:
                assert E.mul(e['weight'], tuple(e['representative'])) == tuple(e['point'])
            weights_by[presentation] = weights
        cells[cell['id']] = (cell, E, sets, weights_by)
    for line in (directory / 'raw.jsonl').open():
        event = json.loads(line)
        if event['kind'] != 'pair_attempt':
            continue
        cid, coverid = event['cell'], event['cover']
        cell, E, bases, weights = cells[cid]
        key = cid, coverid
        if key not in data:
            selected = event['base_indices']
            union = sorted(set().union(*(bases[i] for i in selected)))
            data[key] = {'union': union, 'base_indices': selected, 'index': 0, 'rows': {name: {} for name in weights}, 'accepted': 0, 'same': 0}
        d = data[key]
        index = d['index']
        Q1 = d['union'][index // len(d['union'])]
        Q2 = d['union'][index % len(d['union'])]
        assert event['index'] == index and tuple(event['Q1']) == Q1 and tuple(event['Q2']) == Q2
        Q3 = E.neg(E.add(Q1, Q2))
        accepted = Q3 is not None and Q3 in set(d['union'])
        assert accepted == event['accepted']
        assert (None if event['Q3'] is None else tuple(event['Q3'])) == Q3
        if accepted:
            triple = (Q1, Q2, Q3)
            assert E.add(E.add(Q1, Q2), Q3) is None
            same = any(all(Q in bases[i] for Q in triple) for i in d['base_indices'])
            assert same == event['same_base']
            d['accepted'] += 1
            d['same'] += int(same)
            for name, w in weights.items():
                row = row_from_triple(triple, w, cell['N'])
                rk = tuple(sorted(row.items()))
                old = d['rows'][name].get(rk, False)
                d['rows'][name][rk] = old or same
        d['index'] += 1
        total_checks += 1
        if total_checks % 1024 == 0:
            checkpoint()
    actual = []
    for (cid, coverid), d in data.items():
        cell, E, bases, maps = cells[cid]
        assert d['index'] == len(d['union']) ** 2, 'missing pair attempts'
        expected_cover = next(c for c in expected['covers'] if c['cell'] == cid and c['cover'] == coverid)
        assert expected_cover['ordered_pairs'] == d['index'] and expected_cover['accepted_pairs'] == d['accepted']
        for name, rows in d['rows'].items():
            basis = Basis(cell['N'])
            for r, same in rows.items():
                if same:
                    basis.insert(dict(r))
            same_rank = len(basis.pivots)
            for r, same in rows.items():
                basis.insert(dict(r))
            all_rank = len(basis.pivots)
            target = expected_cover['presentations'][name]
            assert target['same_rank'] == same_rank and target['all_rank'] == all_rank
            assert target['Delta_rank'] == all_rank - same_rank
            used_columns = {maps[name][Q][0] for Q in d['union']}
            assert target['U'] == len(used_columns)
            assert target['rank_deficit'] == len(used_columns) - all_rank
            actual.append({'cell': cid, 'cover': coverid, 'presentation': name, 'same_rank': same_rank, 'all_rank': all_rank})
    expected_keys = {(c['cell'], c['cover']) for c in expected['covers']}
    assert expected_keys == set(data), 'missing or extra cover'
    for cid, (cell, E, bases, maps) in cells.items():
        nonempty = [i for i, B in enumerate(bases) if B]
        want = {','.join(map(str, c)) for t in (1, 2, 3) for c in itertools.combinations(nonempty, t)}
        have = {cover for c, cover in data if c == cid}
        assert want == have, 'cover completeness'
    return {'status': 'pass', 'arithmetic': 'independent integer-polynomial and affine formulas', 'checks': total_checks, 'cover_presentations': actual, 'scope': 'Producer-local arithmetic/replay check; independent-session review pending'}


def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('directory')
    args = parser.parse_args()
    print(json.dumps(audit_package(args.directory), sort_keys=True))
