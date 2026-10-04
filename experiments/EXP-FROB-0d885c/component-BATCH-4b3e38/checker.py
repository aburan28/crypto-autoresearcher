#!/usr/bin/env python3
"""Read-only independent verifier for one fixed synthetic cyclic component."""
import argparse
import copy
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path


def check(value, reason):
    if not value:
        raise ValueError(reason)


class Reference:
    """Polynomial convolution/remainder; no producer tables or imports."""
    def __init__(self):
        self.operations = {'addition': 0, 'multiplication': 0, 'inversion': 0}

    def add(self, x, y):
        self.operations['addition'] += 1
        return x ^ y

    def product(self, x, y):
        self.operations['multiplication'] += 1
        bits = [0] * 7
        for i in range(4):
            for j in range(4):
                bits[i+j] ^= ((x >> i) & 1) & ((y >> j) & 1)
        for k in range(6, 3, -1):
            if bits[k]:
                for d in (0, 1, 4):
                    bits[k-4+d] ^= 1
        return sum(bits[i] << i for i in range(4))

    def inverse(self, x):
        self.operations['inversion'] += 1
        answers = [y for y in range(16) if self.product(x, y) == 1]
        if len(answers) != 1:
            raise ValueError('noninvertible_element')
        return answers[0]

    def power(self, x, n):
        if n < 0:
            return self.power(self.inverse(x), -n)
        z = 1
        while n:
            if n & 1:
                z = self.product(z, x)
            x = self.product(x, x)
            n //= 2
        return z

    def dot(self, u, v):
        z = 0
        for x, y in zip(u, v):
            z = self.add(z, self.product(x, y))
        return z

    def mat(self, a, b):
        return [[self.dot(a[i], [row[j] for row in b]) for j in range(len(b[0]))] for i in range(len(a))]

    def reduce(self, matrix):
        # Forward elimination followed by back substitution, unlike producer Gauss-Jordan.
        a = copy.deepcopy(matrix)
        piv = []
        for col in range(len(a[0])):
            rows = [i for i in range(len(piv), len(a)) if a[i][col]]
            if not rows:
                continue
            r = len(piv)
            a[r], a[rows[0]] = a[rows[0]], a[r]
            inverse = self.inverse(a[r][col])
            a[r] = [self.product(x, inverse) for x in a[r]]
            for i in range(r+1, len(a)):
                factor = a[i][col]
                a[i] = [self.add(x, self.product(factor, y)) for x, y in zip(a[i], a[r])]
            piv.append(col)
        for r in reversed(range(len(piv))):
            for i in range(r):
                factor = a[i][piv[r]]
                a[i] = [self.add(x, self.product(factor, y)) for x, y in zip(a[i], a[r])]
        return a, piv


def matrix_sum(matrices):
    out = [[0]*3 for _ in range(3)]
    for matrix in matrices:
        for i in range(3):
            for j in range(3):
                out[i][j] ^= matrix[i][j]
    return out


def scalar_binary_rank(matrix):
    rows = [sum(v << j for j, v in enumerate(row)) for row in matrix]
    piv = 0
    for j in range(3):
        selected = next((i for i in range(piv, 3) if rows[i] & (1 << j)), None)
        if selected is None:
            continue
        rows[piv], rows[selected] = rows[selected], rows[piv]
        for i in range(3):
            if i != piv and rows[i] & (1 << j):
                rows[i] ^= rows[piv]
        piv += 1
    return [[(row >> j) & 1 for j in range(3)] for row in rows], piv


def errors(payload, ref):
    found = []
    if payload['reconstructed'] != payload['M']:
        found.append('reconstruction_identity')
    for v in payload['f2_kernel']:
        if any(ref.dot(row, v) for row in payload['M']):
            found.append('rational_kernel_residual')
            break
    return found


def verify_data(data, ref):
    # Recheck axioms in the independent quotient implementation, exhaustive domains.
    for x, y, z in itertools.product(range(16), repeat=3):
        check(ref.add(ref.add(x, y), z) == ref.add(x, ref.add(y, z)), 'reference_add_associativity')
        check(ref.product(ref.product(x, y), z) == ref.product(x, ref.product(y, z)), 'reference_mul_associativity')
        check(ref.product(x, ref.add(y, z)) == ref.add(ref.product(x, y), ref.product(x, z)), 'reference_distributivity')
    for x, y in itertools.product(range(16), repeat=2):
        check(ref.add(x,y) == ref.add(y,x) and ref.product(x,y) == ref.product(y,x), 'reference_commutativity')
    for x in range(16):
        check(ref.add(x,0) == x and ref.add(x,x) == 0 and ref.product(x,1) == x and ref.product(x,0) == 0, 'reference_identities')
    try:
        ref.inverse(0)
    except ValueError:
        pass
    else:
        raise ValueError('reference_zero_inverse')
    expected_arithmetic = {'elements': 16, 'triples': 4096, 'inverses': [[x, ref.inverse(x)] for x in range(1,16)], 'zero_inverse_rejected': True}
    check(data['arithmetic'] == expected_arithmetic, 'arithmetic_witness')
    eye = [[int(i == j) for j in range(3)] for i in range(3)]
    zero = [[0]*3 for _ in range(3)]
    shifts = [[[int(i == (j+r)%3) for j in range(3)] for i in range(3)] for r in range(3)]
    check(data['S'] == shifts[1] and ref.mat(shifts[2], shifts[1]) == eye, 'shift_witness')
    omega = min(x for x in range(2,16) if ref.power(x,3) == 1)
    check(data['omega'] == omega, 'least_order_three_element')
    check(3 % 2 != 0, 'projector_characteristic_gate')
    ps = [matrix_sum([[[ref.product(ref.power(omega,-j*r), x) for x in row] for row in shifts[r]] for r in range(3)]) for j in range(3)]
    check(data['projectors'] == ps and matrix_sum(ps) == eye, 'complete_projectors')
    selected, cols = [], []
    for j,p in enumerate(ps):
        for k,q in enumerate(ps):
            check(ref.mat(p,q) == (p if j==k else zero), 'projector_orthogonal_idempotent')
        chosen, inds = [], []
        for k in range(3):
            proposed = chosen + [[row[k] for row in p]]
            _, pivots = ref.reduce([list(row) for row in zip(*proposed)])
            if len(pivots) > len(chosen):
                chosen, inds = proposed, inds + [k]
        check(len(chosen) == 1, 'block_dimension')
        selected.append(inds)
        cols.extend(chosen)
    b = [list(row) for row in zip(*cols)]
    augmented, pivots = ref.reduce([row+e for row,e in zip(b,eye)])
    bi = [row[3:] for row in augmented]
    check(pivots == [0,1,2] and ref.mat(b,bi)==eye and ref.mat(bi,b)==eye, 'basis_inverse')
    check(data['basis_columns']==selected and data['B']==b and data['B_inverse']==bi, 'basis_witness')
    triples = list(map(list,itertools.product(range(2),repeat=3)))
    check([row['coefficients'] for row in data['fixtures']] == triples, 'complete_lexicographic_panel')
    for row, triple in zip(data['fixtures'],triples):
        m = matrix_sum([shifts[r] for r in range(3) if triple[r]])
        check(row['M'] == m, 'matrix_coefficients')
        check(ref.mat(m,shifts[1])==ref.mat(shifts[1],m), 'commutation')
        for p in ps:
            check(ref.mat(m,p)==ref.mat(p,m), 'projector_commutation')
        t = ref.mat(ref.mat(bi,m),b)
        check(all(t[i][j]==0 for i in range(3) for j in range(3) if i!=j), 'off_block_zero')
        check(row['transformed']==t and row['blocks']==[[[t[j][j]]] for j in range(3)], 'all_block_witness')
        reconstructed = ref.mat(ref.mat(b,t),bi)
        projected = matrix_sum([ref.mat(ref.mat(p,m),p) for p in ps])
        check(reconstructed==m==projected and row['reconstructed']==m and row['projected_reconstruction']==m, 'reconstruction_identity')
        check(all(ref.product(x,x)==x and x in (0,1) for r in reconstructed for x in r), 'rational_descent')
        rr, rank = scalar_binary_rank(m)
        check(row['direct_rref']==rr and row['direct_rank']==rank and row['direct_nullity']==3-rank, 'direct_rank_witness')
        block_ranks = [int(t[j][j]!=0) for j in range(3)]
        check(row['block_ranks']==block_ranks and sum(block_ranks)==rank, 'block_rank_agreement')
        kernels = [[[1]] if t[j][j]==0 else [] for j in range(3)]
        check(row['block_kernel_bases']==kernels, 'block_kernel_completeness')
        expected_transport = []
        for j in range(3):
            if kernels[j]:
                embed = [int(k==j) for k in range(3)]
                vector = [ref.dot(r,embed) for r in b]
                check(not any(ref.dot(r,vector) for r in m), 'transported_kernel_residual')
                expected_transport.append({'block':j,'embedded':embed,'vector':vector})
        check(row['transported_kernel']==expected_transport, 'transported_kernel_witness')
        kernel, membership = [], []
        for vector in triples:
            residual = [sum(x*y for x,y in zip(r,vector))%2 for r in m]
            transformed = [ref.dot(r,vector) for r in bi]
            br = [ref.product(t[j][j],transformed[j]) for j in range(3)]
            check((not any(residual))==(not any(br)), 'rational_kernel_membership')
            if not any(residual):
                kernel.append(vector)
            membership.append({'vector':vector,'direct_residual':residual,'transformed':transformed,'block_residual':br})
        check(row['f2_kernel']==kernel and row['membership']==membership and len(kernel)==2**(3-rank), 'full_binary_kernel_set')
    controls = data['controls']
    check(set(controls)=={'noncommuting','omitted_block','characteristic_gate','corrupt_reconstruction','corrupt_kernel'}, 'complete_controls')
    bad = copy.deepcopy(eye)
    bad[0][0] ^= 1
    comm = matrix_sum([ref.mat(shifts[1],bad),ref.mat(bad,shifts[1])])
    check(comm!=zero and controls['noncommuting']=={'M':bad,'commutator':comm,'rejected_by':'matrix_commutation'}, 'noncommuting_control')
    omitted = matrix_sum([ps[0],ps[2]])
    check(omitted!=eye and controls['omitted_block']=={'omitted_j':1,'reconstructed':omitted,'mismatch':matrix_sum([omitted,eye]),'rejected_by':'reconstruction_identity'}, 'omission_control')
    check(2 % 2 == 0 and controls['characteristic_gate']=={'characteristic':2,'order':2,'rejected_by':'cycle_order_not_invertible','projector_attempted':False}, 'characteristic_gate_control')
    unit = next(row for row in data['fixtures'] if row['coefficients']==[1,0,0])
    check(errors(unit,ref)==[], 'positive_control')
    for name, reason in (('corrupt_reconstruction','reconstruction_identity'),('corrupt_kernel','rational_kernel_residual')):
        payload = copy.deepcopy(unit)
        if name=='corrupt_reconstruction':
            payload['reconstructed'][0][0] ^= 1
        else:
            payload['f2_kernel'] = [[1,0,0]]
        check(controls[name]['payload']==payload, name+'_mutation')
        check(errors(payload,ref)==[reason] and controls[name]['rejected_by']==[reason], name+'_sensitivity')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__,allow_abbrev=False)
    parser.add_argument('--run-dir',required=True,type=Path)
    args=parser.parse_args()
    directory=args.run_dir.resolve()
    wall,cpu=time.perf_counter(),time.process_time()
    ref=Reference()
    try:
        read=lambda name:json.loads((directory/name).read_text())
        run=read('manifest.yaml')['run']
        env,launch=read('environment.json'),read('launch.json')
        check(run['id']==launch['run_id']=='RUN-FROB-eba655' and run['experiment_id']=='EXP-FROB-0d885c','run_identity')
        check(run['code']['commit']==env['commit']==launch['authority']['commit'],'commit_binding')
        check(run['code']['command']==(directory/'command.txt').read_text().strip(),'command_binding')
        check(json.loads(run['code']['command'])==launch['argv'],'argv_binding')
        check(run['environment']['adapter']==env,'environment_binding')
        check(run['code']['dirty']==bool(run['environment']['tracked_dirty_status']),'dirty_status_binding')
        params=run['inputs']['parameters']
        check(params['source_sha256']==env['source_sha256'] and params['specification_sha256']==env['specification_sha256'],'input_bindings')
        root=Path(__file__).resolve().parents[3]
        spec='experiments/EXP-FROB-0d885c/specification-component-BATCH-4b3e38.yaml'
        check(params['specification']==spec and sha(root/spec)==env['specification_sha256'],'specification_hash')
        expected_sources = {'experiments/EXP-FROB-0d885c/component-BATCH-4b3e38/'+name for name in ('driver.py','checker.py','dependencies.json','implementation-report.json')}
        check(set(env['source_sha256'])==expected_sources,'source_closure')
        check(params['run_id']=='RUN-FROB-eba655' and params['base_field']==2 and params['character_modulus']==19 and params['dimension']==3 and params['cycle_order']==3,'fixed_parameters')
        check(params['coefficient_triples']==list(map(list,itertools.product(range(2),repeat=3))),'input_coverage')
        for path,digest in env['source_sha256'].items():
            check(sha(root/path)==digest,'source_hash:'+path)
        names={'raw-result.json','fixtures.json','metrics.json','certificates.json','report.md','launch.json','environment.json','command.txt'}
        check(set(run['artifacts'])==names,'artifact_set')
        for name in names:
            check(run['artifacts'][name]=={'sha256':sha(directory/name),'bytes':(directory/name).stat().st_size},'artifact_hash:'+name)
        check(run['result']==read('raw-result.json'),'raw_result_agreement')
        check(run['result']['metrics']==read('metrics.json'),'metrics_agreement')
        check(run['status']=='completed_valid' and run['result']['valid'] is True and run['result']['invalid_reason'] is None,'producer_terminal_validity')
        check(run['result']['certificate']=={'kind':'none','verified':None,'verifier':None},'certificate_scope')
        check(read('certificates.json')=={'kind':'none','finite_witnesses':'fixtures.json','failure':None,'requires_independent_review':True},'certificate_companion')
        check(run['resources']['cpu_seconds']>=0 and run['resources']['peak_rss_bytes']>0 and run['timing']['wall_seconds']>=0,'resource_fields')
        metrics=read('metrics.json')
        check(metrics['fixture_count']==metrics['expected_fixture_count']==8 and metrics['control_count']==metrics['expected_control_count']==5 and metrics['failure'] is None,'coverage_metrics')
        check(set(metrics['field_operation_counts'])=={'arithmetic_and_fixtures','representation_checks','controls_and_serialization'},'stage_counts')
        for counts in metrics['field_operation_counts'].values():
            check(all(isinstance(n,int) and n>=0 for n in counts.values()),'operation_counts')
        verify_data(read('fixtures.json'),ref)
        result={'valid':True,'verified_fixtures':8,'verified_controls':5,'scope':'finite synthetic component only; independent review pending'}
    except Exception as exc:
        result={'valid':False,'reason':str(exc),'type':type(exc).__name__}
    result['checker_cost']={'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,
        'peak_rss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_unit':'KiB' if sys.platform=='linux' else 'bytes' if sys.platform=='darwin' else 'platform-dependent',
        'field_operation_counts':ref.operations,'boundary':'through verification before stdout serialization'}
    print(json.dumps(result,sort_keys=True,allow_nan=False))
    return 0 if result['valid'] else 1


if __name__=='__main__':
    sys.exit(main())
