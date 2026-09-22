#!/usr/bin/env python3
"""Blind static replay of N19 affine SAT pilot raw streams and paired gate.

No experiment source is imported; this launches no solver, native control,
benchmark or target worker. The paired estimator is computed only when all
32 frozen science receipts independently pass completed-valid checks.
"""
from __future__ import annotations

import hashlib
import io
import json
import random
import statistics
import tarfile
import time
from collections import Counter, defaultdict
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT/'research/n19_affine_sat_20260921'
R = ROOT/'experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34'
MOD = 524327
ORDER = 262543
READS = []


def source(path):
    path=Path(path)
    READS.append(str(path.relative_to(ROOT)))
    return path.read_bytes()


def load_json(path):
    b=source(path)
    return json.loads(b),hashlib.sha256(b).hexdigest()


def load_lines(path):
    b=source(path)
    return [json.loads(line) for line in b.splitlines() if line],hashlib.sha256(b).hexdigest()


def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


def gf_mul(x,y):
    z=0
    while y:
        if y&1:
            z^=x
        y>>=1
        x<<=1
        if x&(1<<19):
            x^=MOD
    return z


def gf_square(x):
    return gf_mul(x,x)


@cache
def gf_inv(x):
    assert x
    a,b=x,MOD
    s,t=1,0
    while a!=1:
        if a==0:
            raise AssertionError('zero divisor')
        shift=a.bit_length()-b.bit_length()
        if shift<0:
            a,b=b,a
            s,t=t,s
            shift=-shift
        a^=b<<shift
        s^=t<<shift
    while s.bit_length()>19:
        s^=MOD<<(s.bit_length()-20)
    assert gf_mul(s,x)==1
    return s


def point_neg(p):
    return None if p is None else (p[0],p[0]^p[1])


def point_add(p,q):
    if p is None:
        return q
    if q is None:
        return p
    x,y=p;u,v=q
    if x==u:
        if y!=v or x==0:
            return None
        slope=x^gf_mul(y,gf_inv(x))
        xx=gf_square(slope)^slope^1
        return (xx,gf_square(x)^gf_mul(slope^1,xx))
    slope=gf_mul(y^v,gf_inv(x^u))
    xx=gf_square(slope)^slope^x^u^1
    return (xx,gf_mul(slope,x^xx)^xx^y)


def scalar_mul(p,k):
    out=None
    while k:
        if k&1:
            out=point_add(out,p)
        p=point_add(p,p)
        k>>=1
    return out


def on_curve(p):
    if p is None:
        return True
    x,y=p
    return gf_square(y)^gf_mul(x,y)==gf_mul(gf_square(x),x)^gf_square(x)^1


def build_base(base):
    g=tuple(base['generator'])
    assert on_curve(g) and scalar_mul(g,ORDER) is None
    assert len(base['seed_points'])==4
    assert tuple(sorted(x['point'][0] for x in base['seed_points']))==tuple(base['plane_key'])
    a,b,c=base['affine_coordinates']
    assert tuple(sorted((a,a^b,a^c,a^b^c)))==tuple(base['plane_key'])
    pts=set()
    orbits=[]
    for row in base['seed_points']:
        p=tuple(row['point'])
        assert on_curve(p) and scalar_mul(p,ORDER) is None
        orbit=set()
        q=p
        for _ in range(19):
            orbit.add(q);orbit.add(point_neg(q))
            q=(gf_square(q[0]),gf_square(q[1]))
        assert q==p and len(orbit)==38
        assert not orbit.intersection(pts)
        for t in orbit:
            assert on_curve(t) and scalar_mul(t,ORDER) is None
        pts.update(orbit)
        orbits.append(orbit)
    assert len(pts)==152 and len({x for x,_ in pts})==76
    assert len({min(p[0] for p in orbit) for orbit in orbits})==4
    assert len({p[0] for p in pts})==base['expected_x_values']
    assert len(pts)==base['expected_signed_points']
    return g,sorted(pts)


def pair_table(base_points):
    table={}
    for j,p in enumerate(base_points):
        for q in base_points[j:]:
            table.setdefault(point_add(p,q),(p,q))
    return table


def exact_oracle(q,base_points,pairs):
    for p in base_points:
        w=pairs.get(point_add(q,point_neg(p)))
        if w is not None:
            triple=(p,*w)
            assert point_add(point_add(*triple[:2]),triple[2])==q
            return triple
    return None


def archive_verified(archive_path,manifest):
    b=source(archive_path)
    digest=hash_bytes(b)
    assert digest==manifest['archive_sha256']
    raw={}
    with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as tf:
        for member in tf.getmembers():
            assert member.isfile() and member.name not in raw
            raw[member.name]=tf.extractfile(member).read()
    expected={row['path']:row for row in manifest['files']}
    assert set(raw)==set(expected)
    for name,data in raw.items():
        row=expected[name]
        assert len(data)==row['bytes'] and hash_bytes(data)==row['sha256'],name
    return raw,digest


def parse_extended_dimacs(data):
    header=None
    clauses=[]
    xor=[]
    for line in data.decode().splitlines():
        if not line or line.startswith('c '):
            continue
        if line.startswith('p '):
            words=line.split()
            assert len(words)==4 and words[1]=='cnf' and header is None
            header=(int(words[2]),int(words[3]))
            continue
        if line.startswith('x '):
            lits=[int(s) for s in line[2:].split()]
            assert lits[-1]==0 and all(lits[:-1])
            lits=lits[:-1]
            xor.append({'variables':sorted(abs(lit) for lit in lits),
                        'rhs':1^(sum(lit<0 for lit in lits)&1)})
        else:
            lits=[int(s) for s in line.split()]
            assert lits[-1]==0
            clauses.append(lits[:-1])
    assert header is not None and header[1]==len(clauses)+len(xor)
    return header[0],clauses,xor


def parse_solver_output(data,nvars):
    statuses=[]
    assignment={}
    for line in data.decode(errors='replace').splitlines():
        if line.startswith('s '):
            statuses.append(line[2:].strip())
        elif line.startswith('v '):
            for signed in (int(x) for x in line[2:].split()):
                if signed==0:
                    continue
                v=abs(signed)
                assert 1<=v<=nvars and v not in assignment
                assignment[v]=signed>0
    assert len(statuses)==1
    return statuses[0],assignment


def verify_model(model,clauses,xor,inst,base_x,base_points,q):
    n=inst['nvars']
    assert len(model)==n and set(model)==set(range(1,n+1))
    assert all(any(model[abs(lit)]==(lit>0) for lit in clause) for clause in clauses)
    assert all((sum(model[v] for v in row['variables'])&1)==row['rhs'] for row in xor)
    xs=[]
    for name in ('x1','x2','x3'):
        bits=inst['inputs'][name]
        xs.append(sum(int(model[v])<<i for i,v in enumerate(bits)))
    assert xs==sorted(xs) and all(x in base_x for x in xs)
    lifts=defaultdict(list)
    for p in base_points:
        lifts[p[0]].append(p)
    assert all(len(lifts[x])==2 for x in xs)
    group_witness=None
    for p in lifts[xs[0]]:
        for r in lifts[xs[1]]:
            for t in lifts[xs[2]]:
                if point_add(point_add(p,r),t)==q:
                    group_witness=(p,r,t)
                    break
            if group_witness:
                break
        if group_witness:
            break
    assert group_witness is not None
    return {'decoded_x':xs,'group_witness':[list(x) for x in group_witness]}


def q_from_scalar(g,k):
    q=scalar_mul(g,k)
    assert q is not None and on_curve(q) and scalar_mul(q,ORDER) is None
    return q


def type7(sorted_values,p):
    position=(len(sorted_values)-1)*p
    i=int(position)
    fract=position-i
    return sorted_values[i]*(1-fract)+sorted_values[min(i+1,len(sorted_values)-1)]*fract


def stratified_bootstrap(ratios,cases):
    sat=[i for i,c in enumerate(cases) if c['stratum']=='SAT']
    unsat=[i for i,c in enumerate(cases) if c['stratum']=='UNSAT']
    assert len(sat)==len(unsat)==4
    rng=random.Random('N19-AFFINE-SAT-v1-bootstrap')
    draws=[]
    for _ in range(10000):
        idx=[sat[rng.randrange(4)] for _ in range(4)]+[unsat[rng.randrange(4)] for _ in range(4)]
        draws.append(statistics.median(ratios[i] for i in idx))
    draws.sort()
    return [type7(draws,.025),type7(draws,.975)]


def main():
    t0=time.perf_counter()
    protocol,protocol_hash=load_json(P/'protocol.json')
    base,base_hash=load_json(P/'inputs/base.json')
    cases,cases_hash=load_json(P/'inputs/cases.json')
    bindings,bindings_hash=load_json(P/'inputs/bindings.json')
    assert protocol['inputs']['base_sha256']==base_hash
    assert protocol['inputs']['cases_sha256']==cases_hash
    assert bindings['sha256']['research/n19_affine_sat_20260921/inputs/base.json']==base_hash
    assert bindings['sha256']['research/n19_affine_sat_20260921/inputs/cases.json']==cases_hash
    base_manifest,_=load_json(R/'base_manifest.json')
    case_manifest,_=load_json(R/'case_manifest.json')
    cnf_manifest,_=load_json(R/'cnf_xor_model_manifest.json')
    native_controls,_=load_json(R/'native_controls.json')
    control_receipts,controls_hash=load_lines(R/'control_receipts.jsonl')
    science_receipts,science_hash=load_lines(R/'science_receipts.jsonl')
    raw_manifest,_=load_json(R/'raw_manifest.json')
    raw,archive_hash=archive_verified(R/'raw_outputs.tar.gz',raw_manifest)
    assert base_manifest['base_input_sha256']==base_hash
    assert base_manifest['binding_sha256']==bindings_hash
    assert base_manifest['plane_key']==base['plane_key']
    assert case_manifest['cases']==cases['cases']
    assert native_controls['status']=='passed' and native_controls['CMS_instances']==0
    assert len(control_receipts)==12 and len(science_receipts)==32
    assert len(case_manifest['control_cases'])==12 and len(case_manifest['science_cases'])==32
    assert len(cnf_manifest['rows'])==32
    g,selected_points=build_base(base)
    selected_set=set(selected_points)
    selected_x={p[0] for p in selected_points}
    selected_pairs=pair_table(selected_points)
    small_points=sorted({g,point_neg(g)})
    small_set=set(small_points)
    small_x={g[0]}
    small_pairs=pair_table(small_points)
    assert len(selected_pairs)==11097
    for case in cases['cases']:
        assert tuple(case['Q'])==q_from_scalar(g,case['public_scalar'])
        assert len(case['arm_order'])==4 and set(case['arm_order'])==set(protocol['arms'])
        expected='SAT' if exact_oracle(tuple(case['Q']),selected_points,selected_pairs) else 'UNSAT'
        assert case['stratum']==expected
        assert tuple(case['Q']) not in selected_set
    manifest_rows={x['case_id']:x for x in cnf_manifest['rows']}
    observed=[]
    model_replays=[]
    case_receipts=defaultdict(dict)
    counts=defaultdict(Counter)
    spent=defaultdict(list)
    for phase,receipts,expected_rows in (
        ('controls',control_receipts,case_manifest['control_cases']),
        ('science',science_receipts,case_manifest['science_cases'])):
        assert [x['case_id'] for x in receipts]==[x['id'] for x in expected_rows]
        for rec,planned in zip(receipts,expected_rows):
            cid=rec['case_id']; arm=rec['arm']; key=f"raw/{phase}/{rec['ordinal']:03d}_{cid}"
            assert rec['ordinal']==planned['ordinal'] and arm==planned['arm']
            assert rec['planned_child']==planned['planned_child']
            assert tuple(rec['Q'])==q_from_scalar(g,rec['scalar_driver_only'])==tuple(planned['Q'])
            assert rec['stratum']==planned['stratum']
            assert rec['phase']==phase and rec['case_index']==planned.get('case_index')
            assert rec['wall_seconds']>0 and rec['exit_code']==0 and rec['popen_error'] is None
            assert rec['wait4']['rss_unit']=='bytes' and rec['wait4']['peak_rss']>0
            assert rec['wait4']['user_seconds']>=0 and rec['wait4']['system_seconds']>=0
            assert rec['telemetry_valid'] and not rec['watchdog_reached'] and not rec['memory_cap_reached']
            assert hash_bytes(raw[f'{key}/input.json'])==rec['input_sha256']
            assert hash_bytes(raw[f'{key}/result.json'])==rec['result_sha256']
            assert hash_bytes(raw[f'{key}/stdout.log'])==rec['stdout_sha256']
            assert hash_bytes(raw[f'{key}/stderr.log'])==rec['stderr_sha256']
            inp=json.loads(raw[f'{key}/input.json'])
            result=json.loads(raw[f'{key}/result.json'])
            assert inp['Q']==rec['Q'] and inp['arm']==arm and inp['case_id']==cid
            assert inp['base_recipe']==base and inp['base_kind']==planned['base_kind']
            assert 'public_scalar' not in inp and 'scalar_driver_only' not in inp
            assert result==rec['worker_result']
            assert result['Q']==rec['Q'] and result['case_id']==cid and result['arm']==arm
            assert result['shortcut'] is False
            q=tuple(rec['Q'])
            points=small_points if phase=='controls' else selected_points
            point_set=small_set if phase=='controls' else selected_set
            pairs=small_pairs if phase=='controls' else selected_pairs
            bx=small_x if phase=='controls' else selected_x
            oracle_w=exact_oracle(q,points,pairs)
            oracle_status='SAT' if oracle_w else 'UNSAT'
            assert oracle_status==rec['stratum']
            assert rec['sampling']['method']=='proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint'
            child=result['child']
            assert child['wait4_peak_rss']>0 and child['wait4_rss_unit']=='bytes'
            assert child['wait4_user_seconds']>=0 and child['wait4_system_seconds']>=0
            assert child['wall_seconds']>0
            if arm=='native_mitm':
                assert phase=='science' and child==json.loads(raw[f'{key}/native.receipt.json'])
                assert child['exit_code']==0 and rec['classification']=='completed_valid'
                assert result['native_details']==json.loads(raw[f'{key}/native_result.json'])
                assert result['native_details']['pair_sum_keys']==len(selected_pairs)
                assert result['native_details']['status']==oracle_status
                assert result['status']==oracle_status and rec['replay']['status']==oracle_status
                assert rec['valid'] and rec['replay']['valid']
                assert hash_bytes(raw[f'{key}/native.stdout'])==child['stdout_sha256']
                assert hash_bytes(raw[f'{key}/native.stderr'])==child['stderr_sha256']
            else:
                assert child==json.loads(raw[f'{key}/cms.receipt.json'])
                assert child['argv'][1:]==protocol['solver']['argv']
                assert hash_bytes(raw[f'{key}/cms.stdout'])==child['stdout_sha256']
                assert hash_bytes(raw[f'{key}/cms.stderr'])==child['stderr_sha256']
                inst_bytes=raw[f'{key}/INSTANCE.manifest.json']
                cnf_bytes=raw[f'{key}/INSTANCE.cnf']
                inst=json.loads(inst_bytes)
                assert hash_bytes(inst_bytes)==result['instance']['manifest_sha256']
                assert hash_bytes(cnf_bytes)==result['instance']['cnf_sha256']
                assert result['instance']['domain_arm']==arm
                assert inst['public_q']==rec['Q']
                n,clauses,xor=parse_extended_dimacs(cnf_bytes)
                assert n==inst['nvars']==result['instance']['nvars']
                assert clauses==inst['clauses'] and xor==inst['xor_rows']
                assert len(clauses)==result['instance']['clauses']
                assert len(xor)==result['instance']['xor_rows']
                status,model=parse_solver_output(raw[f'{key}/cms.stdout'],n)
                if child['exit_code']==10:
                    assert status=='SATISFIABLE' and oracle_status=='SAT'
                    assert rec['classification']=='completed_valid' and rec['valid']
                    assert result['status']=='SAT' and rec['replay']['status']=='SAT'
                    model_data=verify_model(model,clauses,xor,inst,bx,points,q)
                    model_replays.append({'case_id':cid,'nvars':n,'clauses':len(clauses),
                                          'xor_rows':len(xor),**model_data})
                elif child['exit_code']==20:
                    assert status=='UNSATISFIABLE' and not model and oracle_status=='UNSAT'
                    assert rec['classification']=='completed_valid' and rec['valid']
                    assert result['status']=='UNSAT' and rec['replay']['status']=='UNSAT'
                elif child['exit_code']==15:
                    assert phase=='science' and status=='INDETERMINATE' and not model
                    assert rec['classification']=='censored_CMS15' and result['status']=='UNKNOWN'
                    assert rec['censored_reason']=='CMS_exit_15_INDETERMINATE'
                    assert not rec['valid'] and rec['replay'] is None
                else:
                    raise AssertionError(('unexpected child exit',cid,child['exit_code']))
                if phase=='science':
                    man=manifest_rows[cid]
                    assert man['arm']==arm and man['instance']==result['instance']
                    assert man['raw_result_sha256']==rec['result_sha256']
            witness=result.get('witness')
            if witness is not None:
                w=tuple(tuple(p) for p in witness)
                assert len(w)==3 and all(p in point_set for p in w)
                assert point_add(point_add(w[0],w[1]),w[2])==q
                assert oracle_status=='SAT'
            else:
                assert result['status']!='SAT'
            if phase=='science':
                case_receipts[rec['case_index']][arm]=rec
            counts[(phase,arm,rec['stratum'])][(rec['classification'],result['status'])]+=1
            spent[(phase,arm,rec['stratum'])].append(rec['wall_seconds'])
            observed.append({'phase':phase,'case_id':cid,'case_index':rec['case_index'],
                             'arm':arm,'stratum':rec['stratum'],'oracle':oracle_status,
                             'raw_child_exit':child['exit_code'],
                             'raw_status':result['status'],'classification':rec['classification'],
                             'censored_reason':rec['censored_reason'],
                             'wall_seconds_spent':rec['wall_seconds'],
                             'outer_wait4_user_seconds':rec['wait4']['user_seconds'],
                             'outer_wait4_system_seconds':rec['wait4']['system_seconds'],
                             'outer_wait4_peak_rss_bytes':rec['wait4']['peak_rss'],
                             'child_wall_seconds_spent':child['wall_seconds'],
                             'child_wait4_user_seconds':child['wait4_user_seconds'],
                             'child_wait4_system_seconds':child['wait4_system_seconds'],
                             'child_wait4_peak_rss_bytes':child['wait4_peak_rss']})
    assert len(model_replays)==4
    assert all(len(case_receipts[i])==4 for i in range(1,9))
    eligible=all(rec['classification']=='completed_valid' and rec['valid']
                 for rec in science_receipts)
    paired={'eligible':eligible,'required_complete_valid':32,
            'observed_complete_valid':sum(r['classification']=='completed_valid' and r['valid'] for r in science_receipts),
            'primary_median_flat_onehot_over_explicit_onehot':None,
            'stratified_bootstrap_type7_95':None,
            'all_pair_ratios':None,'secondary_ratios':None}
    if eligible:
        ordered=cases['cases']
        pair_ratio=[]
        for case in ordered:
            rows=case_receipts[case['case_id']]
            pair_ratio.append(rows['flat_onehot']['wall_seconds']/rows['explicit_onehot']['wall_seconds'])
        paired['all_pair_ratios']=pair_ratio
        paired['primary_median_flat_onehot_over_explicit_onehot']=statistics.median(pair_ratio)
        paired['stratified_bootstrap_type7_95']=stratified_bootstrap(pair_ratio,ordered)
    else:
        paired['reason']='Frozen all-32 complete-valid gate fails; capped INDETERMINATE workers are censored.'
    count_rows=[]
    for key,values in sorted(counts.items()):
        phase,arm,stratum=key
        count_rows.append({'phase':phase,'arm':arm,'stratum':stratum,
                           'outcomes':[{'classification':c,'raw_status':s,'count':n}
                                       for (c,s),n in sorted(values.items())],
                           'observed_spent_outer_wall_seconds':sum(spent[key]),
                           'minimum_spent_outer_wall_seconds':min(spent[key]),
                           'maximum_spent_outer_wall_seconds':max(spent[key])})
    output={'schema':'crypto.autoresearch.n19_affine_sat_blind_replay.v1',
            'task_id':'TASK-20260921-447fa1',
            'input_sha256':{'protocol':protocol_hash,'base':base_hash,'cases':cases_hash,
                            'bindings':bindings_hash},
            'raw_archive_sha256':archive_hash,'raw_files_verified':len(raw),
            'receipt_sha256':{'controls':controls_hash,'science':science_hash},
            'base':{'points':len(selected_points),'x_values':len(selected_x),
                    'pair_sums_including_infinity':len(selected_pairs)},
            'control_models_original_rows_and_group_checked':len(model_replays),
            'control_model_replays':model_replays,
            'counts':count_rows,'individual_receipts':observed,
            'observed_spent_cost_totals':{
                phase:{'outer_wall_seconds':sum(x['wall_seconds_spent'] for x in observed if x['phase']==phase),
                       'separate_child_wall_seconds':sum(x['child_wall_seconds_spent'] for x in observed if x['phase']==phase)}
                for phase in ('controls','science')},
            'paired_math':paired,
            'own_arithmetic_static_replay_elapsed_seconds':time.perf_counter()-t0,
            'sources_read':READS}
    out=P/'review/blind_results.json'
    out.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'science_completed_valid':paired['observed_complete_valid'],
                      'science_censored':32-paired['observed_complete_valid'],
                      'control_models_checked':len(model_replays),
                      'paired_eligible':eligible,
                      'outer_spent_science_wall_seconds':sum(r['wall_seconds'] for r in science_receipts)}))


if __name__=='__main__':
    main()
