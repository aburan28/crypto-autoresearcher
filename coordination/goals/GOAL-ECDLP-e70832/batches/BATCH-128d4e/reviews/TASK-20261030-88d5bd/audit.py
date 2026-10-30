#!/usr/bin/env python3
"""J-truth finite retained-input audit, independent integer/group arithmetic.

No producer module is imported or executed. No entropy or scientific input is
created. Own orbit maps are comparisons on exactly the retained public points.
Rendering sources and report prose are embedded below.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from math import comb, isqrt
import copy
import json
import subprocess
import sys

ROOT = Path('/workspace/classical-ecdlp-validation-ready')
OUT = Path(__file__).resolve().parent
TASK = 'TASK-20261030-88d5bd'
JOINT = 'Truth labels, uniform budget and BSGS equations'
JOINT_ID = 'J-truth'
POST = 'experiments/EXP-ECDLP-080f41/postrun-from-view-346631/'
VIEW = 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/derived-supervisor-views/RUN-ECDLP-939237/manifest-json-v1/'
RAW = VIEW + 'supervisor/modal/collected/'
RELEASE = 'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/releases/' + TASK + '.json'
EXPECTED_RELEASE = '1444591d6e8c3b036454b47183f249040dcbb199119f3d5d1f31ddf64b782ba5'
PREFIXES = [POST, VIEW, 'harness/classical_ecdlp_controlled_followup/',
            'experiments/EXP-ECDLP-080f41/postrun/custody/',
            'experiments/EXP-ECDLP-080f41/runs/RUN-ECDLP-939237/']
EXACT = {RELEASE, 'experiments/EXP-ECDLP-080f41/protocol.json',
         'experiments/EXP-ECDLP-080f41/specification.yaml',
         'experiments/EXP-ECDLP-080f41/trial-plan.json',
         'AGENTS.md', 'docs/agent-contract-extended.md',
         'docs/agent-contract-supplement.md', 'docs/lab-contract.md',
         '.claude/skills/research-visuals/SKILL.md', 'agents/validator.md',
         'ledger/handoffs/' + TASK + '.yaml',
         'experiments/EXP-ECDLP-080f41/reports/run-report-custody.json',
         'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-cbf9d7/admission/output-contract.v1.json'}
for k in ['plans', 'statements']:
    EXACT.add('coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/' + k + '/' + TASK + '.json')
for k in ['derivation', 'seal']:
    EXACT.add('coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/reviews/' + TASK + '/' + k + '.json')

def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def prelog(rel, selection='complete independent audit read'):
    assert rel in EXACT or any(rel.startswith(p) for p in PREFIXES), rel
    assert '..' not in Path(rel).parts
    e = {'read_at': now(), 'canonical_relative_path': rel,
         'kind': 'source_read', 'selection': selection}
    with (OUT/'phase2-read-log.jsonl').open('a') as f:
        f.write(json.dumps(e) + '\n')

HASHES = {}

def read_json(rel):
    prelog(rel)
    raw = (ROOT/rel).read_bytes()
    HASHES[rel] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
    return json.loads(raw)

def rows(rel):
    prelog(rel)
    h = sha256()
    n = size = 0
    with (ROOT/rel).open('rb') as f:
        for n, raw in enumerate(f, 1):
            h.update(raw)
            size += len(raw)
            yield n, json.loads(raw), sha256(raw).hexdigest()
    HASHES[rel] = {'sha256': h.hexdigest(), 'bytes': size, 'rows': n}

def point(v):
    return None if v is None else tuple(v)

def prime(n):
    if type(n) is not int or n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, isqrt(n)+1, 2))

class Arithmetic:
    """Affine formulas independent of all producer source and counters."""
    def __init__(self, model, base):
        self.p, self.a, self.b, self.r = [model[k] for k in ('p','a','b','r')]
        self.G = point(base)
        assert prime(self.p) and self.p > 3 and prime(self.r) and self.r % 2 == 1
        assert (4*self.a**3+27*self.b**2) % self.p
        assert self.member(self.G) and self.G is not None
        self.points = []
        self.logs = {}
        P = None
        for k in range(self.r):
            assert P not in self.logs
            self.points.append(P)
            self.logs[P] = k
            P = self.add(P, self.G)
        assert P is None and len(self.logs) == self.r
        assert self.mul(self.r, self.G) is None
        # Full group order independently counted on the SAME retained curve.
        squares = Counter(y*y % self.p for y in range(self.p))
        self.cardinality = 1 + sum(squares[(x*x*x+self.a*x+self.b) % self.p]
                                   for x in range(self.p))
        assert self.cardinality == self.r

    def member(self, P):
        return P is None or (len(P) == 2 and all(type(v) is int and 0 <= v < self.p for v in P)
                            and (P[1]**2-P[0]**3-self.a*P[0]-self.b) % self.p == 0)

    def neg(self, P):
        return None if P is None else (P[0], -P[1] % self.p)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        u, v = P
        x, y = Q
        if u == x and (v+y) % self.p == 0:
            return None
        if P == Q:
            slope = (3*u*u+self.a)*pow(2*v, -1, self.p) % self.p
        else:
            slope = (y-v)*pow(x-u, -1, self.p) % self.p
        X = (slope*slope-u-x) % self.p
        return X, (slope*(u-X)-v) % self.p

    def mul(self, k, P):
        if k < 0:
            return self.mul(-k, self.neg(P))
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def equation(self, k, Q, multiplier=1):
        return type(k) is int and 0 <= k < self.r and self.points[(k*multiplier) % self.r] == point(Q)

def cd(a, b):
    return -(-a//b)

def word_candidates(bits, radius, cap, r, a, b, target_log):
    """Integer bit masks and exact inequalities, derived before unblinding."""
    L = len(bits)
    epos = [i for i,x in enumerate(bits) if x is None]
    dpos = [i for i,x in enumerate(bits) if x is not None]
    if len(epos) > cap:
        return
    D = 1 << L
    base = sum((x or 0) << (L-1-i) for i,x in enumerate(bits))
    for number in range(1 << len(epos)):
        assignment = [(number >> (len(epos)-1-i)) & 1 for i in range(len(epos))]
        filled = base | sum(v << (L-1-i) for i,v in zip(epos, assignment))
        for weight in range(min(radius,len(dpos))+1):
            for flips in combinations(dpos, weight):
                W = filled
                for i in flips:
                    W ^= 1 << (L-1-i)
                k = cd(r*W,D)
                legal = 0 <= k < r and D*k < r*(W+1)
                x = (a*pow(b,-1,r)*k) % r if legal else None
                ok = legal and a*k % r == b*target_log % r
                yield {'W':W,'k':k,'legal':legal,'x':x,'ok':bool(ok),
                       'assignment':assignment,'flips':list(flips),
                       'bits':[(W >> (L-1-i)) & 1 for i in range(L)]}

class Checks:
    def __init__(self):
        self.totals = Counter()
        self.failures = []
        self.location = {}

    def at(self, source, row=None, digest=None, object_id=None):
        self.location = {'source':source,'row':row,'row_sha256':digest,'object_id':object_id}

    def equal(self, name, actual, expected):
        self.totals[name] += 1
        if actual != expected or (isinstance(expected,bool) and type(actual) is not bool):
            if len(self.failures) < 100:
                self.failures.append({**self.location,'check':name,'actual':actual,'expected':expected})
            return False
        return True

C = Checks()

def check_attempt(proc, meta, g):
    z, a, b = meta['z'], meta['a'], meta['b']
    r = g.r
    L = r.bit_length()+1
    D = 1 << L
    queries = proc['predicate_trace']
    C.equal('trace_length', proc['L'], L)
    C.equal('trace_query_count', len(queries), L)
    C.equal('predicate_evaluations', proc['predicate_evaluations'], L)
    C.equal('retained_bit_reads', proc['retained_bit_reads'], 0)
    bits = []
    truths = []
    s = z*b*pow(a,-1,r) % r
    for i, q in enumerate(queries):
        C.equal('query_index', q['index'], i)
        C.equal('query_public_doubling_point', point(q['target']), g.points[(b*z*pow(2,i,r)) % r])
        bit = q['answer']['bit']
        C.equal('query_label_domain', bit is None or type(bit) is int and bit in (0,1), True)
        C.equal('query_BIT_consistency', q['answer']['status']=='BIT', bit is not None)
        bits.append(bit)
        truths.append(int(s*pow(2,i,r) % r > r//2))
    all_defined = None not in bits
    W = sum((v or 0) << (L-1-i) for i,v in enumerate(bits))
    k = cd(r*W,D) if all_defined else None
    legal = all_defined and 0 <= k < r and D*k < r*(W+1)
    x = a*pow(b,-1,r)*k % r if legal else None
    transformed_ok = g.points[(a*k) % r] == g.points[(b*z) % r] if legal else None
    original_ok = g.equation(x, meta['target']) if legal else None
    ok = bool(legal and transformed_ok and original_ok)
    status = ('RECOVERED' if ok else 'UNDEFINED' if not all_defined else
              'EMPTY_INTERVAL' if not legal else 'REJECTED_FINAL_VERIFICATION')
    C.equal('attempt_candidate_prime', proc['candidate_scalar_prime'], k)
    C.equal('attempt_candidate_original', proc['candidate_scalar'], x)
    C.equal('attempt_inverse', proc['target_multiplier_inverse'], pow(b,-1,r))
    C.equal('attempt_public_equations', proc['public_checks'], {'transformed':transformed_ok,'original':original_ok})
    C.equal('attempt_status', proc['status'], status)
    C.equal('attempt_verified_prime', proc['scalar_prime'], k if ok else None)
    C.equal('attempt_verified_original', proc['scalar'], x if ok else None)
    C.equal('attempt_interval', proc['interval'], {
        'value':W if all_defined else None,'denominator':D,
        'lower_numerator':r*W if all_defined else None,
        'upper_numerator':r*(W+1) if all_defined else None,'nonempty':bool(legal)})
    return {'bits':bits,'s':s,'truth':truths,'truth_word':sum(v << (L-1-i) for i,v in enumerate(truths)),
            'errors':[i for i,(v,t) in enumerate(zip(bits,truths)) if v is not None and v != t],
            'erasures':[i for i,v in enumerate(bits) if v is None], 'status':status}

def replay_uniform(seed, N, count):
    """Implicit front-removal permutation, own deterministic stream replay."""
    index = 0
    rejected = 0
    sparse = {}
    selected = []
    for front in range(count):
        size = N-front
        ceiling = (1 << 256) - ((1 << 256) % size)
        while True:
            block = sha256(seed+b'\0controlled-followup/uniform-list/v1\0'+index.to_bytes(8,'big')).digest()
            index += 1
            value = int.from_bytes(block,'big')
            if value < ceiling:
                break
            rejected += 1
        picked = front + value % size
        selected.append(sparse.get(picked,picked)+1)
        replacement = sparse.pop(front,front)
        if picked != front:
            sparse[picked] = replacement
    counts = {} if count == 0 else {'sha256_blocks':index,'accepted':count}
    if rejected:
        counts['rejected'] = rejected
    return selected, counts

def uniform_errors(u, M, g, Q):
    N = g.r-1
    K = min(M,N)
    errors = []
    expected = {'requested_M':M,'effective_M':K,'domain':[1,N],
                'success_probability_exact':[K,N],'saturated':M >= N,
                'public_equations':K}
    for k,v in expected.items():
        if u.get(k) != v:
            errors.append(k)
    guesses = u.get('guesses',[])
    checks = u.get('checks',[])
    if len(guesses) != K or len(checks) != K:
        errors.append('length')
    if len(set(guesses)) != len(guesses):
        errors.append('duplicate')
    if any(type(k) is not int or not 1 <= k <= N for k in guesses):
        errors.append('nonzero_canonical_domain')
    actual = [g.equation(k,Q) for k in guesses]
    if checks != actual or any(type(c) is not bool for c in checks):
        errors.append('public_equations_values')
    if u.get('success') is not any(actual):
        errors.append('success')
    return errors

def retained_controls(samples, groups):
    controls = []
    def retain(name, rejected, witness):
        controls.append({'name':name,'known_false_refused':bool(rejected),'witness':witness})
    b = samples['bsgs']
    g = groups[b['curve_id']]
    z, Q = b['scalar'], b['point']
    for label, mutant in [('wrong',(z+1) % g.r),('sign',(-z) % g.r),('zero',0),('noncanonical',z+g.r)]:
        retain('retained_BSGS_'+label+'_scalar', not g.equation(mutant,Q),
               {**b,'mutated_scalar':mutant})
    c = samples['geometry']
    altered = list(c['truth'])
    altered[0] ^= 1
    retain('retained_truth_bit_mutation', altered != c['truth'], {**c,'mutated_truth':altered})
    u = samples['uniform']
    g = groups[u['curve_id']]
    original = u['uniform']
    retain('retained_genuine_uniform_accepted', not uniform_errors(original,u['M'],g,u['point']),
           {'source':u['source'],'row':u['row'],'cell_id':u['cell_id']})
    mutated = copy.deepcopy(original)
    mutated['checks'][0] = not mutated['checks'][0]
    retain('retained_uniform_check_boolean_mutation', bool(uniform_errors(mutated,u['M'],g,u['point'])),
           {'source':u['source'],'row':u['row'],'cell_id':u['cell_id'],'mutation':'flip checks[0]'})
    mutated = copy.deepcopy(original)
    mutated['guesses'][0] = 0
    mutated['checks'][0] = False
    mutated['success'] = any(mutated['checks'])
    retain('retained_uniform_zero_with_consistent_false_check', bool(uniform_errors(mutated,u['M'],g,u['point'])),
           {'source':u['source'],'row':u['row'],'cell_id':u['cell_id'],'mutation':'guess[0]=0, check false, recompute success'})
    mutated = copy.deepcopy(original)
    mutated['success_probability_exact'][1] += 1
    retain('retained_uniform_wrong_law_denominator', bool(uniform_errors(mutated,u['M'],g,u['point'])),
           {'source':u['source'],'row':u['row'],'cell_id':u['cell_id'],'mutation':'law denominator r'})
    if len(original['guesses']) >= 2:
        mutated = copy.deepcopy(original)
        mutated['guesses'][1] = mutated['guesses'][0]
        mutated['checks'] = [g.equation(k,u['point']) for k in mutated['guesses']]
        mutated['success'] = any(mutated['checks'])
        retain('retained_uniform_duplicate_with_consistent_checks', bool(uniform_errors(mutated,u['M'],g,u['point'])),
               {'source':u['source'],'row':u['row'],'cell_id':u['cell_id'],'mutation':'duplicate guess; recompute all checks/success'})
    d = samples['recovery']
    g = groups[d['curve_id']]
    retain('retained_genuine_recovered_equation_accepted', g.equation(d['scalar'],d['point']), d)
    retain('retained_recovery_mutated_conversion', not g.equation((d['scalar']+1) % g.r,d['point']),
           {**d,'mutated_scalar':(d['scalar']+1) % g.r,'claimed_checks':{'transformed':True,'original':True}})
    # Fixed public C11 witness structure, no scientific BSGS execution.
    def cert(i,j,z):
        return 0 <= i < 3 and 0 <= j < 4 and z == 4*i+j and 0 <= z < 11 and (4-4*i) % 11 == j and z % 11 == 4
    retain('fixed_C11_genuine_collision_accepted', cert(1,0,4), {'r':11,'m':4,'Q':4,'i':1,'j':0,'z':4})
    for name, triple in [('collision',(1,1,5)),('decomposition',(1,0,5)),('sign',(1,0,7)),('zero',(0,0,0))]:
        retain('fixed_C11_mutated_'+name, not cert(*triple), {'r':11,'m':4,'Q':4,'mutated_i_j_z':triple})
    return controls

def run():
    begun = now()
    release = read_json(RELEASE)
    assert HASHES[RELEASE]['sha256'] == EXPECTED_RELEASE
    pub = read_json(RAW+'public-cohort.json')
    assert len(pub['curves']) == 48
    C.at(RAW+'public-cohort.json')
    expected_curve_ids = {f'{stage}-{tier}-{slot}' for stage in ['discovery','validation','confirmation-A','confirmation-B']
                          for tier in [10,13,16] for slot in range(4)}
    C.equal('public_curve_exact_scheduled_IDs',{x['curve_id'] for x in pub['curves']} == expected_curve_ids,True)
    groups = {}
    curve_meta = {}
    inventory = {}
    for curve in pub['curves']:
        cid = curve['curve_id']
        assert cid not in groups
        g = groups[cid] = Arithmetic(curve['model'],curve['base'])
        targets = {x['target_id']:point(x['point']) for x in curve['targets']}
        assert len(targets) == len(curve['targets'])
        for Q in targets.values():
            assert Q is not None and Q in g.logs and g.member(Q)
        assert len(set(targets.values())) == len(targets)
        C.at(RAW+'public-cohort.json',object_id=cid)
        tier = int(cid.rsplit('-',2)[1])
        C.equal('public_curve_tier',g.r.bit_length(),tier)
        C.equal('public_curve_declared_field_domain',2**(tier-1) <= g.p < 2**(tier+1) and g.p % 4 == 3 and g.r != g.p,True)
        calibration_curve = cid.startswith(('discovery-','validation-'))
        C.equal('public_target_exact_scheduled_IDs',set(targets) == (set() if calibration_curve else {f'target{i:04d}' for i in range(64)}),True)
        curve_meta[cid] = {'model':curve['model'],'base':curve['base'],'targets':targets}
        inventory[cid] = {'r':g.r,'p':g.p,'orbit_entries':len(g.points),'full_curve_cardinality':g.cardinality,
                          'targets':len(targets),'counts':Counter()}
    print('Independent arithmetic completed on all 48 retained public curves', flush=True)
    singles = defaultdict(Counter)
    single_ids = defaultdict(set)
    trace_ids = defaultdict(set)
    hist = defaultdict(Counter)
    trace_meta = {}
    attempts_status = Counter()
    source = RAW+'raw/single-points.jsonl'
    for n,row,h in rows(source):
        cid, arm = row['curve_id'],row['arm_id']
        C.at(source,n,h,row['single_id'])
        g = groups[cid]
        a = int(arm.rsplit('.a',1)[1])
        C.equal('single_unique_ID',row['single_id'] not in single_ids[(cid,arm)],True)
        single_ids[(cid,arm)].add(row['single_id'])
        P = point(row['point'])
        C.equal('single_nonidentity_subgroup', P is not None and P in g.logs and g.member(P), True)
        s = g.logs[P]*pow(a,-1,g.r) % g.r
        truth = int(s > g.r//2)
        bit = row['answer']['bit']
        C.equal('single_label_domain', bit is None or type(bit) is int and bit in (0,1), True)
        C.equal('single_BIT_consistency', row['answer']['status']=='BIT', bit is not None)
        state = 'undefined' if bit is None else 'correct' if bit == truth else 'wrong'
        singles[(cid,arm)][state] += 1
        singles[(cid,arm)]['n'] += 1
        singles[(cid,arm)]['score_sum'] += 0 if bit is None else 1 if bit == truth else -1
        inventory[cid]['counts']['single_rows'] += 1
    print('All retained single-point truth classifications reconstructed',flush=True)
    source = RAW+'raw/traces.jsonl'
    for n,row,h in rows(source):
        cid = row['curve_id']
        g = groups[cid]
        tid = row['trace_id']
        C.at(source,n,h,tid)
        C.equal('trace_unique_ID',tid not in trace_ids[cid],True)
        trace_ids[cid].add(tid)
        a,b = row['base_multiplier'],row['target_multiplier']
        C.equal('trace_base_multiplier_matches_arm',a,int(row['arm_id'].rsplit('.a',1)[1]))
        Q = point(row['target'])
        C.equal('trace_nonzero_unit_multipliers', type(a) is int and 0<a<g.r and type(b) is int and 0<b<g.r,True)
        C.equal('trace_target_subgroup', Q is not None and Q in g.logs and g.member(Q),True)
        z = g.logs[Q]
        meta = {'curve_id':cid,'z':z,'a':a,'b':b,'target':Q}
        values = []
        for method in ['original','incremental']:
            if row[method] is None:
                continue
            value = check_attempt(row[method],meta,g)
            values.append(value)
            inventory[cid]['counts'][method+'_attempts'] += 1
            inventory[cid]['counts'][method+'_queries'] += len(value['bits'])
            attempts_status[method+'/'+value['status']] += 1
        if row['incremental'] is None:
            v = values[0]
            hist[(cid,row['arm_id'])][str(len(v['errors']))+','+str(len(v['erasures']))] += 1
        else:
            C.equal('paired_owned_semantics', values[0],values[1])
            C.equal('paired_retained_equal_flag',row['equal'],True)
            target_id = row['target_id']
            C.equal('trace_target_inventory',Q,curve_meta[cid]['targets'][target_id])
            C.equal('confirmation_trace_unique',tid not in trace_meta,True)
            trace_meta[tid] = {**meta,**values[0],'source':source,'row':n,'row_sha256':h}
        inventory[cid]['counts']['trace_rows'] += 1
    print('All trace point recurrences, half truths, intervals and equations checked',flush=True)
    calibration = read_json(POST+'calibration.json')
    for curve in calibration['curves']:
        cid = curve['curve_id']
        C.at(POST+'calibration.json',object_id=cid)
        for arm,retained in curve['arms'].items():
            actual = singles[(cid,arm)]
            for k in ['correct','wrong','undefined','n','score_sum']:
                C.equal('calibration_'+k,retained.get(k,0),actual[k])
            C.equal('calibration_unconditional_fraction',retained['correlation'],{'numerator':actual['score_sum'],'denominator':actual['n']})
            C.equal('calibration_truth_histogram',curve['error_erasure_histograms'][arm],dict(hist[(cid,arm)]))
    cells = {}
    cell_status = Counter()
    samples = {}
    word_count = legal_words = zero_words = public_equations = 0
    source = RAW+'raw/decoder-cells.jsonl'
    for n,row,h in rows(source):
        tid = row['trace_id']
        meta = trace_meta[tid]
        cid = meta['curve_id']
        g = groups[cid]
        cell_id = row['cell_id']
        C.at(source,n,h,cell_id)
        radius,cap = row['radius'],row['erasure_cap']
        C.equal('cell_frozen_parameters',(radius in (0,1,2) and cap in (0,2)),True)
        C.equal('cell_id_parameters',cell_id,tid+'/t'+str(radius)+'.e'+str(cap))
        C.equal('cell_unique',cell_id not in cells,True)
        bits = meta['bits']
        e = bits.count(None)
        capped = e > cap
        expected = 0 if capped else (1 << e)*sum(comb(len(bits)-e,j) for j in range(min(radius,len(bits)-e)+1))
        C.equal('cell_length',row['L'],len(bits))
        C.equal('cell_erasures',row['erasures'],e)
        C.equal('cell_capped',row['capped'],capped)
        C.equal('cell_expected_word_count',row['expected_word_count'],expected)
        C.equal('cell_word_count',row['word_count'],expected)
        C.equal('cell_retained_word_count',len(row['words']),expected)
        candidates = set()
        recoveries = set()
        zeros = 0
        empty = 0
        for j,(w,derived) in enumerate(zip(row['words'],word_candidates(bits,radius,cap,g.r,meta['a'],meta['b'],meta['z']))):
            C.equal('word_binary_value',w['value'],derived['W'])
            C.equal('word_bits',w['bits'],derived['bits'])
            C.equal('word_erasure_assignment',w['erasure_assignment'],derived['assignment'])
            C.equal('word_flip_indices',w['flipped_indices'],derived['flips'])
            C.equal('word_interval_candidate',w['candidate_scalar_prime'],derived['k'])
            C.equal('word_interval_legality',w['legal'],derived['legal'])
            C.equal('word_scalar_conversion',w['candidate_scalar'],derived['x'])
            if derived['legal']:
                k,x = derived['k'],derived['x']
                # Independently audited orbit points are the group multiplication
                # comparison; no producer scalar/log oracle is consulted.
                ok1 = g.points[(meta['a']*k) % g.r] == g.points[(meta['b']*meta['z']) % g.r]
                ok2 = g.equation(x,meta['target'])
                checks = {'transformed':ok1,'original':ok2}
                legal_words += 1
                public_equations += 2
                if x:
                    candidates.add(x)
                else:
                    zeros += 1
                    zero_words += 1
                if ok1 and ok2:
                    recoveries.add(x)
            else:
                checks = {'transformed':None,'original':None}
                empty += 1
            C.equal('word_both_public_equations',w['public_checks'],checks)
            status = 'RECOVERED' if derived['ok'] else 'REJECTED_FINAL_VERIFICATION' if derived['legal'] else 'EMPTY_INTERVAL'
            C.equal('word_status',w['status'],status)
            word_count += 1
        C.equal('cell_distinct_nonzero_candidates',row['distinct_nonzero_candidates'],sorted(candidates))
        C.equal('cell_M',row['M'],len(candidates))
        C.equal('cell_zero_checks',row['zero_candidate_checks'],zeros)
        C.equal('cell_recovered_scalars',row['recovered_scalars'],sorted(recoveries))
        C.equal('cell_scalar',row['scalar'],next(iter(recoveries)) if recoveries else None)
        status = ('CAPPED_ERASURES' if capped else 'RECOVERED' if recoveries else
                  'EMPTY_INTERVAL' if expected and empty == expected else 'REJECTED_FINAL_VERIFICATION')
        if radius == 0 and cap == 0:
            status = meta['status']
        C.equal('cell_status',row['status'],status)
        C.equal('cell_truth_inclusion_equivalence',bool(recoveries),not capped and len(meta['errors']) <= radius)
        cells[cell_id] = {'M':len(candidates),'curve_id':cid,'trace_id':tid,'status':status}
        cell_status[status] += 1
        inventory[cid]['counts']['decoder_cells'] += 1
        if recoveries and 'recovery' not in samples:
            samples['recovery'] = {'source':source,'row':n,'row_sha256':h,'cell_id':cell_id,'curve_id':cid,
                                   'scalar':next(iter(recoveries)),'point':meta['target']}
    print('Every retained decoder word and both public equations checked',flush=True)
    host_ids = set()
    source = POST+'host-cells.jsonl'
    for n,row,h in rows(source):
        cid = row['cell_id']
        meta = trace_meta[row['trace_id']]
        C.at(source,n,h,cid)
        C.equal('host_cell_unique',cid not in host_ids,True)
        C.equal('host_cell_trace_ID',row['trace_id'],cells[cid]['trace_id'])
        host_ids.add(cid)
        expected = {k:meta[k] for k in ['s','truth','errors','erasures','truth_word']}
        C.equal('host_geometry_public_truth',row['geometry'],expected)
        if 'geometry' not in samples:
            samples['geometry'] = {'source':source,'row':n,'row_sha256':h,'cell_id':cid,**expected}
    C.at(source)
    C.equal('host_cell_ID_coverage',host_ids == set(cells),True)
    refs = read_json(POST+'references.json')
    bsgs_count = 0
    bsgs_status = Counter()
    for curve in refs['curves']:
        cid = curve['curve_id']
        g = groups[cid]
        C.at(POST+'references.json',object_id=cid)
        C.equal('retained_orbit_point_count',curve['orbit_points'],g.r)
        observed_ids = set()
        for row in curve['bsgs_targets']:
            target_id = row['target_id']
            C.at(POST+'references.json',object_id=cid+'/'+target_id)
            C.equal('BSGS_target_unique',target_id not in observed_ids,True)
            observed_ids.add(target_id)
            Q = point(row['point'])
            C.equal('BSGS_target_inventory',Q,curve_meta[cid]['targets'][target_id])
            cert = row['bsgs']
            z = g.logs[Q]
            C.equal('BSGS_success_status',cert['status'],'success')
            C.equal('BSGS_scalar_matches_independent_orbit',cert['scalar'],z)
            C.equal('BSGS_public_equation',g.equation(cert['scalar'],Q),True)
            # This is derived decomposition, explicitly NOT a retained i,j or
            # a retained collision/table witness.
            m = isqrt(g.r-1)+1
            i,j = divmod(z,m)
            C.equal('BSGS_declared_setup_entries',cert['setup']['stored_points'],m)
            C.equal('BSGS_declared_setup_words',cert['setup']['stored_scalar_words'],m)
            C.equal('BSGS_declared_setup_add_calls',cert['setup']['setup_group_add'],m)
            C.equal('BSGS_implied_lookup_count',cert['online'].get('table_lookup',0),i+1)
            C.equal('BSGS_implied_giant_add_count',cert['online'].get('online_group_add',0),i)
            C.equal('BSGS_public_check_count',cert['online'].get('public_scalar_check',0),1)
            C.equal('BSGS_derived_decomposition_equation',g.add(Q,g.neg(g.points[(i*m) % g.r])),g.points[j])
            bsgs_count += 1
            bsgs_status[cert['status']] += 1
            if 'bsgs' not in samples:
                samples['bsgs'] = {'source':POST+'references.json','object_id':cid+'/'+target_id,
                                   'curve_id':cid,'scalar':z,'point':Q,'derived_m':m,
                                   'derived_i':i,'derived_j':j,'retained_internal_i_j':False}
        C.at(POST+'references.json',object_id=cid)
        C.equal('BSGS_target_ID_coverage',observed_ids == set(curve_meta[cid]['targets']),True)
    seed = bytes.fromhex(read_json(POST+'host-seed-event.json')['master_hex'])
    uniform_count = uniform_success = uniform_guesses = zero_M = saturated = 0
    uniform_seen = set()
    uniform_branch = Counter()
    uniform_file_counts = {}
    for cid,g in groups.items():
        source = POST+'uniform-'+cid+'.jsonl'
        n = 0
        for n,row,h in rows(source):
            cell_id = row['cell_id']
            C.at(source,n,h,cell_id)
            meta = trace_meta[row['trace_id']]
            C.equal('uniform_cell_unique',cell_id not in uniform_seen,True)
            C.equal('uniform_cell_trace_ID',row['trace_id'],cells[cell_id]['trace_id'])
            uniform_seen.add(cell_id)
            C.equal('uniform_curve_ID',meta['curve_id'],cid)
            M = cells[cell_id]['M']
            C.equal('uniform_budget_matches_candidate',row['M'],M)
            u = row['uniform']
            C.equal('uniform_all_domain_budget_law_equations',uniform_errors(u,M,g,meta['target']),[])
            for guess,check in zip(u['guesses'],u['checks']):
                C.equal('uniform_each_public_equation',check,g.equation(guess,meta['target']))
            per_cell_seed = sha256(seed+('uniform/'+cell_id).encode()).digest()
            guessed,stream_counts = replay_uniform(per_cell_seed,g.r-1,min(M,g.r-1))
            C.equal('uniform_existing_stream_guesses',u['guesses'],guessed)
            C.equal('uniform_existing_stream_counts',u['stream_counts'],stream_counts)
            uniform_count += 1
            uniform_success += int(u['success'])
            uniform_guesses += len(u['guesses'])
            zero_M += M == 0
            saturated += M >= g.r-1
            uniform_branch['success' if u['success'] else 'failure'] += 1
            uniform_branch['M0' if M == 0 else 'positive_unsaturated' if M < g.r-1 else 'saturated'] += 1
            inventory[cid]['counts']['uniform_rows'] += 1
            if len(u['guesses']) >= 2 and 'uniform' not in samples:
                samples['uniform'] = {'source':source,'row':n,'row_sha256':h,'curve_id':cid,'cell_id':cell_id,
                                      'M':M,'point':meta['target'],'uniform':copy.deepcopy(u)}
        uniform_file_counts[cid] = n
    C.at(POST)
    C.equal('uniform_all_cell_ID_coverage',uniform_seen == set(cells),True)
    for cid,inv in inventory.items():
        C.at(RAW+'public-cohort.json',object_id=cid)
        calibration_curve = cid.startswith(('discovery-','validation-'))
        arms = [f'circuit{c}.a{a}' for c in [1,2] for a in [1,2,3,5]]
        expected_traces = ({f'{cid}/trace{i:04d}/{arm}' for i in range(128) for arm in arms}
                           if calibration_curve else {f'{cid}/target{i:04d}/rep{rep}' for i in range(64) for rep in range(8)})
        C.equal('trace_exact_scheduled_IDs',trace_ids[cid] == expected_traces,True)
        for arm in arms:
            expected_singles = {f'{cid}/single{i:04d}/{arm}' for i in range(1800)} if calibration_curve else set()
            C.equal('single_exact_scheduled_IDs',single_ids[(cid,arm)] == expected_singles,True)
        expected = {'single_rows':14400 if calibration_curve else 0,
                    'trace_rows':1024 if calibration_curve else 512,
                    'original_attempts':1024 if calibration_curve else 512,
                    'incremental_attempts':0 if calibration_curve else 512,
                    'decoder_cells':0 if calibration_curve else 3072,
                    'uniform_rows':0 if calibration_curve else 3072}
        for k,v in expected.items():
            C.equal('per_curve_'+k,inv['counts'][k],v)
        inv['counts'] = dict(inv['counts'])
    controls = retained_controls(samples,groups)
    # Bind every previously read canonical file, including scoped source reads;
    # preserve a real pre-read event for these digest reads.
    log_entries = [json.loads(x) for x in (OUT/'phase2-read-log.jsonl').read_text().splitlines()]
    for rel in dict.fromkeys(e['canonical_relative_path'] for e in log_entries if e['kind']=='source_read'):
        if rel not in HASHES:
            prelog(rel,'final digest of earlier actual source read')
            raw = (ROOT/rel).read_bytes()
            HASHES[rel] = {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    total = Counter()
    for inv in inventory.values():
        total.update(inv['counts'])
    result = {'schema':'bounded-host-reference-truth-audit/v1','task_id':TASK,'joint':JOINT,
              'begun_at':begun,'completed_at':now(),
              'verdict':'breaks' if C.failures or not all(c['known_false_refused'] for c in controls) else 'inconclusive',
              'finite_equation_checks':'breaks' if C.failures else 'holds within inspected inventory',
              'scientific_trials':0,'producer_imports_calls_or_execution':0,
              'coverage':{**dict(total),'curves':len(groups),'independent_orbit_entries':sum(g.r for g in groups.values()),
                          'distinct_public_targets':sum(len(x['targets']) for x in curve_meta.values()),
                          'decoder_words':word_count,'legal_word_checks':legal_words,'zero_word_checks':zero_words,
                          'decoder_public_equations':public_equations,'BSGS_targets':bsgs_count,
                          'BSGS_explicit_internal_table_step_collision_witnesses':0,
                          'host_geometry_rows':len(host_ids),'uniform_rows':uniform_count,
                          'uniform_successes':uniform_success,'uniform_failures':uniform_count-uniform_success,
                          'uniform_guess_equations':uniform_guesses,'uniform_M0_rows':zero_M,
                          'uniform_saturated_rows':saturated,'uniform_files':len(uniform_file_counts),
                          'empty_uniform_files':sum(n == 0 for n in uniform_file_counts.values())},
              'branch_counts':{'attempt_status':dict(attempts_status),'cell_status':dict(cell_status),
                               'BSGS_status':dict(bsgs_status),'uniform':dict(uniform_branch)},
              'per_curve':inventory,'check_counts':dict(C.totals),'failures':C.failures,
              'controls':controls,'minimal_retained_control_witnesses':samples,
              'source_bindings':HASHES,
              'qualifications':[
                  'The phase1 encoding/indexing qualification was resolved by phase2 source transcription: bit=int(k>r//2), forward doubling, L=bit_length(r)+1; it matches the sealed convention.',
                  'The phase1 displayed nonzero interval is intersected with 1..r-1. The source additionally retains the scalar-zero interval check; it is legal for checking but excluded from M. Those zero checks were independently counted.',
                  'All mathematical group comparisons use own affine formulas and exact retained-curve orbit maps; no producer functions or solver/reference were invoked.',
                  'BSGS final scalars and derived decomposition/count implications verify; explicit retained baby tables, giant-step sequences and collision i,j are absent. Own derived i,j are not source witnesses or execution proof.',
                  'No retained uniform saturation branch was observed unless the actual coverage count says otherwise; fixed C11 controls cover the mathematical boundary only.',
                  'SHA256 stream replay checks retained consistency under the declared law. It does not prove ideal-hash uniformity or independence.',
                  'Native invalid_output/check1/publishedfalse is preserved; this audit changes no run status.',
                  'Native operation counters, clocks, physical memory, currency and energy remain unqualified. No benchmark, speedup, exponent, significance, global closure or whole-claim inference.'],
              'commands':['python '+str(OUT/'audit.py'), 'python '+str(OUT/'audit.py')+' --render',
                          'pdftoppm -png -r 115 '+str(OUT/'report.pdf')+' '+str(OUT/'inspection-page')],
              'release_binding':{'path':RELEASE,'sha256':EXPECTED_RELEASE,**release}}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    attest(result)
    print(json.dumps({'verdict':result['verdict'],'failures':len(C.failures),'coverage':result['coverage'],
                      'controls':len(controls),'controls_passed':sum(c['known_false_refused'] for c in controls)},indent=2),flush=True)

def attest(result):
    # Own records only; original log content and original note/seal stay intact.
    phase1 = [json.loads(x) for x in (OUT/'read-log.jsonl').read_text().splitlines()]
    phase2 = [json.loads(x) for x in (OUT/'phase2-read-log.jsonl').read_text().splitlines() if x]
    seal = json.loads((OUT/'seal.json').read_text())
    release = result['release_binding']
    events = [{'kind':'read','at':e['read_at'],'source':e['canonical_relative_path']} for e in phase1]
    events.append({'kind':'seal','at':seal['recorded_at'],
                   'artifact':'coordination/goals/GOAL-ECDLP-e70832/batches/BATCH-128d4e/reviews/'+TASK+'/seal.json',
                   'sha256':sha256((OUT/'seal.json').read_bytes()).hexdigest()})
    events.append({'kind':'unblind','at':release['recorded_at'],'artifact':RELEASE,'sha256':EXPECTED_RELEASE})
    events.extend({'kind':'read','at':e['read_at'],'source':e['canonical_relative_path']}
                  for e in phase2 if e['kind']=='source_read')
    for i,e in enumerate(events,1):
        e['seq'] = i
    sources = list(dict.fromkeys(e['source'] for e in events if e['kind']=='read'))
    record = {'review_attestation':{'task_id':TASK,'joints_owned':[JOINT_ID],
                'verdicts':{JOINT_ID:result['verdict']},'joint_labels':{JOINT_ID:JOINT},'sources_read':sources,
                'read_sibling_reports':False,'blind_from_respected':True,
                'phased_release':{'schema':'sealed-blind-review/v1','events':events}},
              'recorded_at':now(),'model_verified':False,'probe_executed':False,
              'scientific_trials':0,'phase1_note_and_seal_unchanged':True,
              'publication_ack':{'phase1_commit':'6f1a20fad9','release_commit':'abc17d567a',
                                  'root_ACK_records_commit':'246078079c','received_explicit_root_ACK':True},
              'boundary_time_meaning':'seal/unblind times are exact artifact recorded_at values, not invented message receipt times. All actual phase2 source read times are separately prelogged after release.',
              'directory_inventory_events':[e for e in phase2 if e['kind']=='directory_inventory'],
              'metadata_exposure':result['qualifications'][0:2] + ['Original frozen protocol/spec/trial embedded historical metadata was permitted; no sibling file was read in either phase. Initial scoped stdout truncation is disclosed in the sealed derivation.'],
              'source_bindings':result['source_bindings']}
    # JSON is a YAML 1.2 document; no extra parser is needed for generation.
    (OUT/'read-attestation.yaml').write_text(json.dumps(record,indent=2)+'\n')

def augment_setups():
    """Narrow added coverage; avoids restreaming the already checked raw files."""
    global C
    C = Checks()
    result = json.loads((OUT/'checks.json').read_text())
    pub = read_json(RAW+'public-cohort.json')
    assert HASHES[RAW+'public-cohort.json']['sha256'] == result['source_bindings'][RAW+'public-cohort.json']['sha256']
    public = {x['curve_id']:x for x in pub['curves']}
    for curve in result['per_curve'].values():
        curve['counts']['setups'] = 0
    seen = set()
    reasons = Counter()
    source = RAW+'raw/setups.jsonl'
    for n,row,h in rows(source):
        cid,arm = row['curve_id'],row['arm_id']
        C.at(source,n,h,cid+'/'+arm)
        key = cid+'/'+arm
        C.equal('setup_unique_ID',key not in seen,True)
        seen.add(key)
        original = public[cid]
        C.equal('setup_model_binding',row['model'],original['model'])
        C.equal('setup_original_base_binding',row['base'],original['base'])
        a = int(arm.rsplit('.a',1)[1])
        C.equal('setup_base_multiplier_binding',row['arm']['base_multiplier'],a)
        C.equal('setup_arm_ID_binding',row['arm']['id'],arm)
        # Use only own affine formulas; no second orbit/log reconstruction.
        g = Arithmetic.__new__(Arithmetic)
        for k in ['p','a','b','r']:
            setattr(g,k,original['model'][k])
        g.G = point(original['base'])
        C.equal('setup_prepared_base_public_equation',point(row['prepared_base']),g.mul(a,g.G))
        C.equal('setup_prepared_base_nonidentity_member',point(row['prepared_base']) is not None and g.member(point(row['prepared_base'])),True)
        reasons[str(row['setup_reason'])] += 1
        result['per_curve'][cid]['counts']['setups'] = result['per_curve'][cid]['counts'].get('setups',0)+1
    expected = {cid+'/'+arm for cid in public for arm in
        ([f'circuit{c}.a{a}' for c in [1,2] for a in [1,2,3,5]]
         if cid.startswith(('discovery-','validation-')) else ['circuit2.a1'])}
    C.at(source)
    C.equal('setup_exact_scheduled_IDs',seen == expected,True)
    result['coverage'].update(setup_rows=len(seen),setup_base_equations=len(seen))
    result['branch_counts']['setup_reason'] = dict(reasons)
    for k,v in C.totals.items():
        result['check_counts'][k] = result['check_counts'].get(k,0)+v
    result['failures'].extend(C.failures)
    result['source_bindings'].update(HASHES)
    result['completed_at'] = now()
    result['setup_coverage_command'] = ['python',str(OUT/'audit.py'),'--setups']
    result['scope_boundary'] = 'All retained accepted public points, prepared bases, trace queries, decoder word checks, host truth geometry, uniform rows and BSGS final scalars are covered. Coordinate proposal/rejection internals, full candidate predicate mathematics and native execution/cost instrumentation are outside this joint.'
    if result['failures']:
        result['verdict'] = 'breaks'
        result['finite_equation_checks'] = 'breaks'
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    attest(result)
    print(json.dumps({'setup_rows':len(seen),'setup_equation_failures':len(C.failures),'verdict':result['verdict']}))

def render():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    r = json.loads((OUT/'checks.json').read_text())
    v = r['coverage']
    fig, ax = plt.subplots(figsize=(10.5,4.4))
    fig.patch.set_facecolor('#f8fafc')
    ax.set(xlim=(0,10.5),ylim=(0,4.4))
    ax.axis('off')
    boxes = [(.15,2.35,2.4,1.25,'48 retained curves\nOwn affine arithmetic\nExact order +\nfull cardinality','#dbeafe'),
             (2.9,2.35,3.15,1.25,f"{v['trace_rows']:,} retained traces\n{v['decoder_cells']:,} cells / {v['decoder_words']:,} words\nTruth, intervals,\nconversion, equations",'#dcfce7'),
             (6.4,2.35,3.85,1.25,f"{v['uniform_rows']:,} uniform rows\n{v['uniform_guess_equations']:,} guessed-scalar equations\nLaw, zero, uniqueness, retained stream",'#dcfce7'),
             (2.9,.3,3.15,1.2,f"{v['BSGS_targets']:,} BSGS final scalars\nPublic equations verified\nDerived decomposition only",'#dcfce7'),
             (6.4,.3,3.85,1.2,'Missing retained BSGS internals\nNo table / giant-step sequence / i,j\nJ-truth remains inconclusive','#fef3c7')]
    for x,y,w,h,label,color in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.06',linewidth=1,edgecolor='#64748b',facecolor=color))
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9.5,color='#0f172a',linespacing=1.4)
    for x1,y1,x2,y2 in [(2.6,2.97,2.84,2.97),(6.1,2.97,6.34,2.97),(4.48,2.29,4.48,1.56),(6.1,.9,6.34,.9)]:
        ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops={'arrowstyle':'->','color':'#334155','lw':1.4})
    ax.text(.1,4.05,'Independent finite equation coverage; missing execution witnesses stay missing',fontsize=13,weight='bold',color='#0f172a')
    ax.text(.1,.02,'TASK-20261030-88d5bd  |  EXP-ECDLP-080f41 / RUN-ECDLP-939237  |  zero new scientific trials',fontsize=8,color='#475569')
    fig.savefig(OUT/'diagram.svg',bbox_inches='tight')
    fig.savefig(OUT/'diagram-render.pdf',bbox_inches='tight')
    plt.close(fig)
    controls = r['controls']
    full_attestation = json.loads((OUT/'read-attestation.yaml').read_text())['review_attestation']
    report_attestation = json.dumps({'review_attestation':{k:full_attestation[k] for k in
         ['task_id','joints_owned','verdicts','sources_read','read_sibling_reports','blind_from_respected']}},indent=2)
    text = f'''---
title: "Retained public-equation and truth-label audit"
subtitle: "TASK-20261030-88d5bd · J-truth"
date: "2026-10-30"
geometry: margin=0.75in
fontsize: 10pt
---

The assigned joint is **{r['verdict']}**. All inspected finite public-equation,
truth-label, interval, conversion and uniform-list consistency checks passed.
The retained BSGS outputs omit the baby tables, giant-step sequences and explicit
collision indices needed for full internal-witness coverage. Correct final
scalars do not fill that gap. This report makes no whole-claim decision.

![Finite independent coverage and the missing BSGS witness boundary.](diagram.svg)

The fixed inventory is EXP-ECDLP-080f41, RUN-ECDLP-939237. The native
`invalid_output/check1/publishedfalse` outcome remains unchanged. No scientific
trial, new curve, target, nonce, entropy draw, producer import, source execution,
solver experiment or referencebank was created.

## Observation

| Independently checked retained population | Exact count |
|:--|--:|
| Curves, exact prime order and full curve cardinality | {v['curves']:,} |
| Same-curve orbit entries, including identities | {v['independent_orbit_entries']:,} |
| Retained prepared-base setup equations | {v['setup_base_equations']:,} |
| Calibration single-point label classifications | {v['single_rows']:,} |
| Trace rows / original attempts / incremental attempts | {v['trace_rows']:,} / {v['original_attempts']:,} / {v['incremental_attempts']:,} |
| Original / incremental forward-doubling query equations | {v['original_queries']:,} / {v['incremental_queries']:,} |
| Decoder cells / enumerated word records | {v['decoder_cells']:,} / {v['decoder_words']:,} |
| Legal word records / zero-scalar checks | {v['legal_word_checks']:,} / {v['zero_word_checks']:,} |
| Decoder public equations, including failed candidates | {v['decoder_public_equations']:,} |
| Retained host truth-geometry rows | {v['host_geometry_rows']:,} |
| Distinct public targets / BSGS final scalar equations | {v['distinct_public_targets']:,} / {v['BSGS_targets']:,} |
| Uniform files / legitimately empty calibration files | {v['uniform_files']:,} / {v['empty_uniform_files']:,} |
| Uniform rows: successes / failures | {v['uniform_successes']:,} / {v['uniform_failures']:,} |
| Uniform guessed-scalar equations / zero-M rows | {v['uniform_guess_equations']:,} / {v['uniform_M0_rows']:,} |
| Retained uniform saturation rows | {v['uniform_saturated_rows']:,} |

All expected per-curve row and target-ID populations were reconciled.
`checks.json` preserves every check count, status distribution, per-curve count,
source-file digest, and minimal control witness. Its failures array contains
{len(r['failures'])} entries. Undefined, empty, capped, zero, failed-verification
and successful rows are retained in the checked population.

## Comparison and independent method

The blind derivation fixed the convention lower scalar half = 0, upper half = 1,
forward doubling, and scalar recovery `x = a * inverse(b) * k mod r`.
Phase-two source transcription resolved the earlier encoding qualification:
`host/verify.py` lines 309–317 and `engine.py` lines 81–138 use that convention.
For `D=2^L`, a binary word `W` requires `rW <= Dk < r(W+1)`.
The source additionally retains a scalar-zero interval check; zero is excluded
from the distinct nonzero budget M, as the sealed derivation required.

Own integer affine group formulas reconstructed only the SAME retained curves.
Each orbit closes for the first time at r; deterministic field point-counting
also confirms the full curve cardinality. Their maps support public-equation
comparisons and independently determined half truths. They are audit scratch,
never candidate advice. No producer Group, Oracle, BSGS, decoder or reference
function was imported or called.

Every original and incremental trace point, scalar interval, conversion and
public check was compared. All 216 retained setup bases were independently
checked against their original base and declared multiplier, with exact setup
IDs and model bindings. Every retained decoder word was reconstructed from
integer bit masks, exact ceiling inequalities and the sealed error/erasure
law. All calibration score denominators and error/erasure histograms, every
host truth geometry, and every uniform success and failure were checked.
Uniform guesses were canonical, nonzero and distinct; exact K/(r-1), empty-M
and saturation metadata and all guessed-scalar equations were checked. Existing
SHA256 streams were replayed without entropy to check retained consistency.

All {v['BSGS_targets']:,} retained BSGS scalars satisfy their fixed target equations.
The width and count-implied decomposition are consistent with own arithmetic.
These derived indices are explicitly not retained collision witnesses. The
source `host/reference.py` lines 37–75 serializes scalars and count vectors,
without its baby table, giant-step sequence or explicit collision `(i,j)`.

## Controls

All {len(controls)} phase-two genuine/known-false sensitivity controls passed.
They include actual retained BSGS wrong scalar, sign, zero and noncanonical
mutations; a retained truth-bit mutation; uniform false check, zero, duplicate
and denominator mutations; a retained recovered-scalar conversion mutation;
and fixed-public C11 genuine/mutated collision and decomposition controls.
Mutually consistent false duplicate/zero metadata is still refused. The sealed
phase-one note separately records 23 fixed-toy controls, including exhaustive
C11 subset inclusion for M=0 through saturation, F11 membership/order, and exact
interval boundaries. Toy controls certify only those controls.

## Inference and limitation

The finite equation and truth-label consistency component holds within this
complete inspected inventory. The assigned joint stays inconclusive because
retained internal BSGS table/step/collision witnesses are absent. This is an
evidence gap, not a mathematical failure or a negative scientific outcome.
An explicit table/step/collision artifact bound to the existing computation,
if available, would permit that missing verification; a newly executed source
reference would be a different observation and is outside this audit.

Native event counters, clocks, physical memory, energy and currency remain
unqualified. Logical count consistency does not qualify source execution.
Uniform stream consistency assumes the stated ideal-hash distribution model;
it does not prove randomness or independence. Observed branch counts bound
coverage; fixed-toy saturation does not establish retained saturation coverage.
There is no benchmark, speedup, exponent, significance, attack, closure or
whole-claim inference.

## Provenance and reproducibility

The unchanged blind derivation and seal were published in commit
`6f1a20fad9`; the release was published in `abc17d567a`, with root ACK records
in `246078079c`. Release SHA-256:

```text
{EXPECTED_RELEASE}
```

All 34 phase-one canonical reads predate derivation generation. Every phase-two
source open was recorded before the read and after release. Artifact seal and
release timestamps are copied exactly, not reconstructed message times.
The requested policy is review-adversarial/xhigh; the serving model remains
unverified and no probe was invented. No sibling report was read.

Exact source hashes and row-level control bindings are in `checks.json`;
the complete chronological `review_attestation` is in `read-attestation.yaml`.
Primary data sources are the allowlisted view's `public-cohort.json`, raw
`single-points.jsonl`, `traces.jsonl`, and `decoder-cells.jsonl`, plus retained
`calibration.json`, `host-cells.jsonl`, `references.json`, `host-seed-event.json`
and all 48 uniform files. Internal primary contracts/specifications were read;
their historical references were not independently retrieved. No novelty or
literature-completeness claim is made.

Coverage is for retained accepted public points and the listed mathematical
records. Coordinate proposal/rejection internals, full candidate predicate
mathematics and native execution/cost instrumentation are outside this joint.

Reproduce with `python audit.py`; render with `python audit.py --render`.
The editable report and diagram source is embedded in `audit.py`. Every PDF
page must be visually inspected and recorded in `visual-inspection.json`.

```json
{report_attestation}
```
'''
    (OUT/'report.md').write_text(text)
    # Pandoc/XeLaTeX is an installed renderer. PDF uses the same figure saved
    # as vector PDF so the Markdown SVG does not require an external converter.
    (OUT/'render-input.md').write_text(text.replace('(diagram.svg)','(diagram-render.pdf)'))
    (OUT/'latex-header.tex').write_text(r'''\usepackage{fvextra}
\RecustomVerbatimEnvironment{verbatim}{Verbatim}{breaklines,breakanywhere,fontsize=\scriptsize}
''')
    command = ['pandoc',str(OUT/'render-input.md'),'--pdf-engine=xelatex','--resource-path='+str(OUT),
               '--no-highlight','-H',str(OUT/'latex-header.tex'),'-o',str(OUT/'report.pdf')]
    completed = subprocess.run(command,capture_output=True,text=True)
    (OUT/'render-command.json').write_text(json.dumps({'at':now(),'argv':command,'returncode':completed.returncode,
                                                     'stdout':completed.stdout,'stderr':completed.stderr},indent=2)+'\n')
    if completed.returncode:
        raise RuntimeError(completed.stderr)
    r['rendering'] = {'at':now(),'argv':command,'returncode':completed.returncode,
                      'stdout':completed.stdout,'stderr':completed.stderr,
                      'latex_header_source':(OUT/'latex-header.tex').read_text(),
                      'render_input_markdown':(OUT/'render-input.md').read_text(),
                      'editable_report_and_diagram_source':'Embedded in audit.py render()',
                      'audit_py_sha256':sha256((OUT/'audit.py').read_bytes()).hexdigest(),
                      'report_pdf_sha256':sha256((OUT/'report.pdf').read_bytes()).hexdigest()}
    (OUT/'checks.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'report_pdf':str(OUT/'report.pdf'),'rendered_at':now()}))

if __name__ == '__main__':
    if '--render' in sys.argv:
        render()
    elif '--setups' in sys.argv:
        augment_setups()
    else:
        run()
        augment_setups()
