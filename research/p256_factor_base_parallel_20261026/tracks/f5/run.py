"""F5 fixed matched-transport panel. Import and --help collect no data."""
import hashlib
import itertools
import json
from pathlib import Path
from panel_io import HERE, REPO, run_main

TASK = 'TASK-20261026-26de77'
PRIOR = REPO/'research/p256_factor_base_parallel_20261025'


def panel(log, seed):
    import field as f
    log.set_arm('reference')
    E = f.Curve(-3, f.B)
    source = json.loads((PRIOR/'tracks/f1/checks-02/generic-k4.json').read_text())
    canonical = sorted(tuple(point) for point in source['signed_base'] if point[1] <= f.P//2)[:8]
    log.check(len(canonical) == 8 and len({p[0] for p in canonical}) == 8, 'eight fixed canonical source points')
    base = [point for p in canonical for point in (p, E.neg(p))]
    log.check(len(set(base)) == 16, 'sixteen signed points')
    log.check(all(E.on(p) and E.mul(f.R, p) is None for p in base), 'source curve and subgroup checks')
    queries = [E.add(E.add(canonical[0], canonical[1]), canonical[2]),
               E.add(E.add(canonical[0], canonical[0]), canonical[1]), canonical[1]]
    query_names = ['constructed_distinct', 'constructed_twoequal', 'constructed_cancellation']
    draws = []
    for query in range(2):
        for attempt in range(1024):
            data = f'F5-pass2/{seed}/query/{query}/attempt/{attempt}'.encode()
            x = int.from_bytes(hashlib.sha256(data).digest(), 'big') % f.P
            rhs = (x**3-3*x+f.B) % f.P
            y = pow(rhs, (f.P+1)//4, f.P)
            accepted = y*y % f.P == rhs
            draws.append({'query': query, 'attempt': attempt, 'x': x, 'accepted': accepted})
            if accepted:
                queries.append((x, min(y, f.P-y)))
                query_names.append('unplanted_hash_'+str(query))
                break
        else:
            raise RuntimeError('Fixed bounded hash-to-point search did not finish')
    queries.append(None)
    query_names.append('identity')
    log.check(all(E.on(q) and E.mul(f.R, q) is None for q in queries), 'all queries on source subgroup')
    for start in range(0, len(draws), 64):
        log.case(f'hash-draws-{start//64:03d}', draws[start:start+64])
    log.case('source-domain', {'selection_rule': 'first eight x-ordered y<=p/2 points of old generic-k4 signed base',
              'source_file': str((PRIOR/'tracks/f1/checks-02/generic-k4.json').relative_to(REPO)),
              'canonical': canonical, 'signed_base': base, 'queries': list(zip(query_names, queries)), 'hash_draw_count': len(draws), 'hash_draw_files': 'hash-draws-*.json'})
    # Exhaustive affine oracle, independent of the pair-lookup extraction below.
    table = {}
    for indices in itertools.combinations_with_replacement(range(len(base)), 3):
        q = E.add(E.add(base[indices[0]], base[indices[1]]), base[indices[2]])
        table.setdefault(q, []).append(indices)
    source_solutions = [sorted(table.get(q, [])) for q in queries]
    log.check(all(source_solutions[i] for i in range(3)), 'three constructed source positives detected')

    def recover_relations(points, target, a):
        lookup = {point: i for i, point in enumerate(points)}
        relations = []
        visits = 0
        for i, point in enumerate(points):
            for j in range(i, len(points)):
                visits += 1
                pair = f.independent_add(point, points[j], a)
                pair_negative = None if pair is None else (pair[0], -pair[1] % f.P)
                residual = f.independent_add(target, pair_negative, a)
                k = lookup.get(residual)
                if k is not None and k >= j:
                    relations.append((i, j, k))
        return sorted(relations), visits

    log.mark_arm('reference', {'checked_objects': len(queries), 'oracle_triples': len(list(itertools.combinations_with_replacement(range(len(base)), 3)))})
    log.set_arm('candidate')

    class Map:
        def __init__(self, entry):
            self.degree = int(entry['degree'])
            self.target = f.Curve(int(entry['codomain_ainvs'][3]), int(entry['codomain_ainvs'][4]))
            self.x = f.parse_rat(entry['rational_maps'][0], 0)
            self.y = f.parse_rat(entry['rational_maps'][1], 1)
            self.dx = f.parse_rat(entry['dual_maps'][0], 0)
            self.dy = f.parse_rat(entry['dual_maps'][1], 1)
            self.kernel = f.poly([int(c) for c in entry['kernel']])
            self.inverse_scalar = pow(self.degree, -1, f.R)

        @staticmethod
        def evaluate(point, xmap, ymap, domain, codomain):
            if not domain.on(point):
                raise ValueError('Point is not on map domain')
            if point is None:
                return None
            if f.evaluate(xmap.d, point[0]) == 0 or f.evaluate(ymap.d, point[0]) == 0:
                return None
            image = (xmap.at(point[0]), point[1]*ymap.at(point[0]) % f.P)
            if not codomain.on(image):
                raise ValueError('Map output is not on codomain')
            return image

        def forward(self, point):
            return self.evaluate(point, self.x, self.y, E, self.target)

        def dual(self, point):
            return self.evaluate(point, self.dx, self.dy, self.target, E)

        def inverse(self, point):
            return E.mul(self.inverse_scalar, self.dual(point))

    maps = []
    for ell in [3, 5, 11]:
        receipt = json.loads((PRIOR/f'tracks/f5/attempt02-kernel-screen-{ell}.json').read_text())
        for index, entry in enumerate(receipt['candidates']):
            if entry['status'] == 'certified_map':
                maps.append((ell, index, entry))
    log.check([ell for ell, _, _ in maps] == [3, 5, 11, 11], 'all four predeclared maps loaded')
    relation_queries, membership_queries, pole_certificates = 0, 0, 0
    map_counts = []
    for ell, index, entry in maps:
        phi = Map(entry)
        prefix = f'ell{ell}-candidate{index}'
        image = [phi.forward(point) for point in base]
        log.check(None not in image and len(set(image)) == len(base), prefix+' signed image bijection')
        log.check(all(phi.inverse(point) == original for point, original in zip(image, base)), prefix+' source membership recovery')
        log.check(all(phi.dual(phi.forward(point)) == E.mul(ell, point) for point in canonical), prefix+' dual composition on base')
        xpoly = [1]
        image_xs = sorted({point[0] for point in image})
        for x in image_xs:
            xpoly = f.mul(xpoly, [-x, 1])
        log.check(len(image_xs) == 8 and len(xpoly) == 9, prefix+' exact degree-eight image membership')
        target_rows = []
        for name, query, expected in zip(query_names, queries, source_solutions):
            endpoint_query = phi.forward(query)
            log.check(phi.inverse(endpoint_query) == query, prefix+' query inverse '+name)
            actual, visits = recover_relations(image, endpoint_query, phi.target.a)
            log.check(actual == expected, prefix+' complete signed relation set '+name)
            target_rows.append({'name': name, 'source_target': query, 'endpoint_target': endpoint_query,
                                'source_solution_indices': expected, 'endpoint_solution_indices': actual,
                                'pair_visits': visits, 'scope': 'fixed finite-domain complete result only'})
            relation_queries += 1
        for candidate in image+[phi.forward(q) for q in queries]:
            direct = candidate in image
            pulled_back = phi.inverse(candidate) in base
            polynomial_member = candidate is not None and f.evaluate(xpoly, candidate[0]) == 0
            log.check(direct == pulled_back == polynomial_member, prefix+' point and x-membership agreement')
            membership_queries += 1
        h = f.monic(phi.kernel)
        log.check(phi.x.d == f.power(h, 2), prefix+' x denominator is h squared')
        log.check(phi.y.d == f.power(h, 3), prefix+' y multiplier denominator is h cubed')
        log.check(f.gcd(phi.x.n, h) == [1], prefix+' x poles are not removable')
        log.check(f.gcd(phi.y.n, h) == [1], prefix+' y poles are not removable')
        log.check(f.gcd(h, [f.B, -3, 0, 1]) == [1], prefix+' kernel excludes geometric two-torsion')
        pole_certificates += 1
        wrong = E.mul((phi.inverse_scalar+1) % f.R, phi.dual(image[0]))
        log.check(wrong != base[0], prefix+' wrong inverse scalar rejected')
        refused = False
        try:
            f.parse_rat('x/0', 0)
        except ZeroDivisionError:
            refused = True
        log.check(refused, prefix+' zero denominator rejected by actual parser')
        malformed = next((base[0][0], (base[0][1]+delta) % f.P) for delta in [1, 2]
                         if not E.on((base[0][0], (base[0][1]+delta) % f.P)))
        refused_point = False
        try:
            phi.forward(malformed)
        except ValueError:
            refused_point = True
        log.check(refused_point, prefix+' off-curve input rejected by actual map path')
        log.case(prefix, {'degree': ell, 'candidate_index': index, 'source_uid': json.loads((PRIOR/'tracks/f5/identities.json').read_text())['source']['curve_uid'],
                         'endpoint_ainvs': entry['codomain_ainvs'], 'source_base': base, 'endpoint_base': image,
                         'image_x_membership_polynomial': xpoly, 'queries': target_rows,
                         'pole_certificate': {'kernel_h': h, 'x_numerator': phi.x.n, 'x_denominator': phi.x.d,
                                              'y_multiplier_numerator': phi.y.n, 'y_multiplier_denominator': phi.y.d,
                                              'type': 'exact algebraic denominator/copricimality; no extension-point enumeration'},
                         'subgroup_inverse_scalar': phi.inverse_scalar,
                         'normalization_note': 'Vélu differential scale1; dual scale ell; finite subgroup inverse [ell^-1 mod r]dual',
                         'native_target_group_counters': dict(phi.target.counters)})
        map_counts.append({'ell': ell, 'candidate_index': index, 'relation_queries': len(queries), 'membership_candidates': len(image)+len(queries)})
    # A coordinate-isomorphism receives precisely the same points, labels and queries.
    scale = 2
    iso_E = f.Curve(-3*scale**4, f.B*scale**6)
    iso = lambda point: None if point is None else (point[0]*scale**2 % f.P, point[1]*scale**3 % f.P)
    iso_base = [iso(point) for point in base]
    iso_rows = []
    for name, target, expected in zip(query_names, queries, source_solutions):
        got, visits = recover_relations(iso_base, iso(target), iso_E.a)
        log.check(got == expected, 'coordinate-isomorphism relation control '+name)
        iso_rows.append({'name': name, 'solutions': got, 'pair_visits': visits})
    log.case('coordinate-isomorphism', {'scale': scale, 'a': iso_E.a, 'b': iso_E.b, 'queries': iso_rows})
    log.case('native-counters', {'source_group_across_both_arms': dict(E.counters), 'excluded_costs': ['map discovery inherited, not timed', 'complete ECDLP pipeline absent', 'no field-operation tariff']})
    log.mark_arm('candidate', {'checked_objects': relation_queries+membership_queries+pole_certificates+len(queries), 'relation_queries': relation_queries, 'membership_queries': membership_queries, 'pole_certificates': pole_certificates})
    return {'_completion_sentinel': TASK, 'relation_queries': relation_queries,
            'membership_queries': membership_queries, 'pole_certificates': pole_certificates,
            'maps': map_counts, 'source_solution_counts': dict(zip(query_names, map(len, source_solutions))),
            'source_oracle_triples': len(list(itertools.combinations_with_replacement(range(len(base)), 3))),
            'scope_limits': ['No degree-ell extension kernel point enumeration; exact algebraic pole certificates only.',
                             'Finite transported-base relation equality is not a comparative solving-cost result.',
                             'Source order and global map identities inherit the exact prior certificates.']}


if __name__ == '__main__':
    raise SystemExit(run_main(panel, TASK, ['checked_objects', 'oracle_triples', 'relation_queries', 'membership_queries', 'pole_certificates']))
