"""Public synthetic signed-three-sum collectors, with disjoint stage accounting."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys
from time import perf_counter, process_time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
from arithmetic import Field, Elliptic

PARAMETERS = {'arms':['enumeration','pair_table'], 'max_retained_rows':2048,
              'max_pair_entries':4096, 'distinct_atoms':True, 'signs':[1,-1]}
_NATIVE_CAPABILITY = object()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def row_key(row):
    return (row['source_scalar'], tuple(row['triple']), tuple(row['signs']))


class Meter:
    def __init__(self, fixture):
        self.f = Field(fixture['p']); self.ring = Field(fixture['r'])
        self.e = Elliptic(self.f, 0, fixture['a'], fixture['b'])
        self.other = Counter(); self.phases = []

    def counters(self):
        return dict(Counter({'Fp.'+k:v for k,v in self.f.counts.items()}) +
                    Counter({'Fr.'+k:v for k,v in self.ring.counts.items()}) + self.other)

    def stage(self, name, operation):
        before = Counter(self.counters()); wall, cpu = perf_counter(), process_time()
        record = dict(phase=name, status='complete', wall_valid=False)
        try:
            return operation()
        except BaseException as error:
            record.update(status='failed', error_type=type(error).__name__, error=str(error))
            raise
        finally:
            record.update(wall_seconds=perf_counter()-wall, cpu_seconds=process_time()-cpu,
                          counters=dict(Counter(self.counters())-before))
            self.phases.append(record)

    def neg(self, point):
        self.other['point_negations'] += 1
        return None if point is None else (point[0], self.f.sub(0, point[1]))

    def equal(self, a, b):
        self.other['point_comparisons'] += 1
        return a == b


def make_row(fixture, scalar, triple, signs):
    coefficients = [0]*len(fixture['factor_base'])
    for j, sign in zip(triple, signs, strict=True): coefficients[j] = sign % fixture['r']
    return dict(schema='direct-three-sum-row/v1', curve_uid=fixture['uid'],
                source_scalar=scalar, triple=list(triple), signs=list(signs), coefficients=coefficients)


def public_projection(cell, sources, meter):
    p, r = cell['fixture']['p'], cell['fixture']['r']
    known, derivations = {}, []
    for scalar in cell['source_order']:
        point = sources[scalar]; opposite = meter.neg(point)
        key = min(point, opposite); sign = 1 if point == key else -1
        value = scalar if sign == 1 else meter.ring.sub(0, scalar)
        if key in known and known[key] != value: raise ValueError('inconsistent public sources')
        if key not in known:
            known[key] = value
            derivations.append(dict(point=list(key), scalar=value, public_source=scalar, sign=sign))
    base = [tuple(a['point']) for a in cell['fixture']['factor_base']]
    keys = [min(q, meter.neg(q)) for q in base]
    unknown = sorted(set(keys)-known.keys())
    mapping = []
    for q, key in zip(base, keys):
        sign = 1 if q == key else -1
        mapping.append(['known', known[key] if sign == 1 else meter.ring.sub(0, known[key])]
                       if key in known else ['unknown', unknown.index(key), sign])
    return dict(U=len(unknown), unknown_points=[list(q) for q in unknown], native_to_projected=mapping,
                public_derivations=[d for d in derivations if tuple(d['point']) in keys])


def project(row, projection, meter):
    vector, rhs = [0]*projection['U'], row['source_scalar']; f = meter.ring
    if len(row['coefficients']) != len(projection['native_to_projected']): raise ValueError('wrong native width')
    for c, m in zip(row['coefficients'], projection['native_to_projected'], strict=True):
        if m[0] == 'known': rhs = f.sub(rhs, f.mul(c, m[1]))
        elif m[0] == 'unknown': vector[m[1]] = f.add(vector[m[1]], f.mul(c, m[2]))
    return vector, rhs


def normalize(projected, meter):
    equations = set(); f = meter.ring
    for vector, rhs in projected:
        affine = vector+[rhs]; first = next((x for x in affine if x), None)
        inverse = f.inv(first) if first else None
        key = tuple(f.mul(x, inverse) for x in affine) if first else tuple(affine)
        meter.other['affine_set_insertions'] += 1; equations.add(key)
    return [list(v) for v in sorted(equations)]


def eliminate(projected, width, meter):
    """Forward elimination with explicit pivot-row indices, affine consistency."""
    f = meter.ring; pivots = {}; indices = []
    for index, (vector, rhs) in enumerate(projected):
        row = vector+[rhs]
        for pivot, old in sorted(pivots.items()):
            if row[pivot]:
                scale = row[pivot]; row = [f.sub(x, f.mul(scale, y)) for x,y in zip(row, old)]
        pivot = next((j for j in range(width) if row[j]), None)
        if pivot is None:
            if row[-1]: raise ValueError('inconsistent affine relation')
        else:
            inverse = f.inv(row[pivot]); pivots[pivot] = [f.mul(x, inverse) for x in row]; indices.append(index)
    return dict(rank=len(pivots), columns=width, nullity=width-len(pivots),
                pivots={str(k):v for k,v in sorted(pivots.items())}, independent_row_indices=indices)


def kernel(elimination, meter):
    pivots = {int(k):v for k,v in elimination['pivots'].items()}; f = meter.ring; result = []
    for free in range(elimination['columns']):
        if free in pivots: continue
        vector = [0]*elimination['columns']; vector[free] = 1
        for pivot, row in sorted(pivots.items(), reverse=True):
            value = 0
            for j in range(pivot+1, len(vector)): value = f.add(value, f.mul(row[j], vector[j]))
            vector[pivot] = f.sub(0, value)
        result.append(vector)
    return result


def collect(cell, arm, event, *, capability=None):
    fixture = cell['fixture']; n = len(fixture['factor_base'])
    if capability is not _NATIVE_CAPABILITY and not (fixture.get('software_control') is True and fixture['p'] <= 211):
        raise ValueError('scientific direct collection requires native admission')
    if arm not in PARAMETERS['arms']: raise ValueError('unknown arm')
    order = cell['source_order']
    if len(order) != len(set(order)) or any(type(s) is not int or not 0<s<fixture['r'] for s in order):
        raise ValueError('invalid public source schedule')
    meter = Meter(fixture); e = meter.e; base = [tuple(a['point']) for a in fixture['factor_base']]
    def setup():
        for point in [tuple(fixture['P'])]+base:
            if not e.on(point) or e.mul(fixture['r'], point) is not None: raise ValueError('invalid subgroup point')
    meter.stage('setup', setup)
    signed = meter.stage('sign_construction', lambda:{(j,s):q if s==1 else meter.neg(q)
                                                    for j,q in enumerate(base) for s in (1,-1)})
    sources = meter.stage('source_construction', lambda:{s:e.mul(s,tuple(fixture['P'])) for s in order})
    rows, blocks, pairs = [], [], []; digest = sha256(); attempts = 0
    def accept(scalar, triple, signs):
        row = make_row(fixture, scalar, triple, signs); event(dict(kind='accepted', arm=arm, row=row)); rows.append(row)
        if len(rows)>PARAMETERS['max_retained_rows']: raise ValueError('retained-row size gate exceeded; prefix retained')
    if arm == 'enumeration':
        def enumerate_all():
            nonlocal attempts
            for scalar in order:
                statuses = []; source_digest = sha256()
                for triple in combinations(range(n),3):
                    for signs in product((1,-1),repeat=3):
                        attempts += 1; meter.other['descriptors'] += 1
                        total = e.add(e.add(signed[triple[0],signs[0]], signed[triple[1],signs[1]]), signed[triple[2],signs[2]])
                        hit = meter.equal(total, sources[scalar]); statuses.append('+' if hit else '.')
                        if hit: accept(scalar,triple,signs)
                        encoded = encode([scalar,triple,signs,hit]).encode()+b'\n'
                        digest.update(encoded); source_digest.update(encoded); meter.other['branch_sha256_updates'] += 2
                block = dict(scalar=scalar, attempts=attempts, statuses=''.join(statuses), branch_sha256=source_digest.hexdigest())
                blocks.append(block); event(dict(kind='source_complete', arm=arm, **block))
        meter.stage('enumeration', enumerate_all)
    else:
        table = defaultdict(list)
        def build():
            for (j,k), signs in product(combinations(range(n),2), product((1,-1),repeat=2)):
                point = e.add(signed[j,signs[0]],signed[k,signs[1]])
                pair = dict(indices=[j,k], signs=list(signs), point=None if point is None else list(point))
                meter.other['pair_table_insertions'] += 1; table[point].append(len(pairs)); pairs.append(pair)
                event(dict(kind='pair_entry', arm=arm, index=len(pairs)-1, **pair))
                if len(pairs)>PARAMETERS['max_pair_entries']: raise ValueError('pair-table size gate exceeded; prefix retained')
        meter.stage('pair_construction', build)
        def query():
            nonlocal attempts
            for scalar in order:
                queries = []; source_digest = sha256()
                for third, sign in product(range(n),(1,-1)):
                    attempts += 1; meter.other['queries'] += 1
                    wanted = e.add(sources[scalar], meter.neg(signed[third,sign]))
                    meter.other['pair_table_lookups'] += 1; bucket = table.get(wanted, [])
                    accepted = []
                    for index in bucket:
                        meter.other['bucket_entries_inspected'] += 1; pair = pairs[index]
                        if pair['indices'][1] < third:
                            accepted.append(index); accept(scalar,pair['indices']+[third],pair['signs']+[sign])
                    record = dict(third=third,sign=sign,wanted=None if wanted is None else list(wanted),bucket=list(bucket),accepted=accepted)
                    queries.append(record); encoded = encode([scalar,record]).encode()+b'\n'
                    digest.update(encoded); source_digest.update(encoded); meter.other['branch_sha256_updates'] += 2
                block = dict(scalar=scalar,attempts=attempts,queries=queries,branch_sha256=source_digest.hexdigest())
                blocks.append(block); event(dict(kind='source_complete', arm=arm, **block))
        meter.stage('query_and_extraction',query)
    rows = meter.stage('canonical_row_order',lambda:sorted(rows,key=row_key))
    def certify():
        for row in rows:
            total = None
            for j,s in zip(row['triple'],row['signs']): total = e.add(total,signed[j,s])
            if not meter.equal(total,sources[row['source_scalar']]): raise ValueError('false extracted relation')
            meter.other['relation_certificates'] += 1
    meter.stage('certification',certify)
    projection = meter.stage('public_projection',lambda:public_projection(cell,sources,meter))
    return dict(schema='direct-three-sum/v1',curve_uid=fixture['uid'],arm=arm,source_order=order,complete=True,
                attempts=attempts,rows=rows,status_blocks=blocks,branch_sha256=digest.hexdigest(),pair_entries=pairs,
                projection=projection,collection_phases=list(meter.phases),collection_counters=meter.counters(),analysis=None,
                not_applicable=['C lifting','polynomial extraction','outside-column cancellation'],
                cost_scope='Stage Fp/Fr/group and logical counters plus diagnostic clocks; no complete S or Python machine-cost model.'), meter


def analyze(cell,result,meter):
    projection = result['projection']; width = projection['U']; start = len(meter.phases)
    def project_all():
        return ([project(row,projection,meter) for row in cell['preprocessing_rows']],
                [project(row,projection,meter) for row in result['rows']])
    old,new = meter.stage('row_projection',project_all)
    equations = meter.stage('affine_normalization',lambda:normalize(new,meter))
    before = meter.stage('old_elimination',lambda:eliminate(old,width,meter))
    fresh = meter.stage('new_elimination',lambda:eliminate(new,width,meter))
    combined = meter.stage('combined_elimination',lambda:eliminate(old+new,width,meter))
    old_kernel = meter.stage('old_kernel',lambda:kernel(before,meter))
    new_kernel = meter.stage('combined_kernel',lambda:kernel(combined,meter))
    def syndromes():
        values = []
        for vector,rhs in new:
            output = []
            for k in old_kernel:
                value = 0
                for x,y in zip(vector,k): value = meter.ring.add(value,meter.ring.mul(x,y))
                output.append(value)
            values.append(output)
        return values
    action = meter.stage('old_kernel_action',syndromes)
    return dict(rows=len(new),distinct_equations=len(equations),normalized_equations=equations,
                preprocessing=before,new=fresh,combined=combined,rank_gain=combined['rank']-before['rank'],
                old_kernel=old_kernel,kernel=new_kernel,old_kernel_syndromes=action,
                nonzero_old_kernel_syndromes=sum(any(v) for v in action),
                analysis_phases=meter.phases[start:],total_counters=meter.counters())
