#!/usr/bin/env python3
"""Independent static replay of the frozen N7 public-synthetic raw records.

Reads only the frozen protocol, selected manifests, receipts and raw archives.
Does not import experiment implementation or run a solver/pipeline/benchmark.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
import statistics
import tarfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/EXP-KIC-424885/runs/RUN-KIC-c2b1b7"
DESIGN = ROOT / "research/golden_factor_base_sat_20260921/design_completion.json"
SPEC = ROOT / "experiments/EXP-KIC-424885/specification.yaml"
OUT = Path(__file__).with_name("blind_only_rederivation.json")
READS = set()


def read_bytes(path):
    path = Path(path)
    READS.add(str(path.relative_to(ROOT)))
    return path.read_bytes()


def read_json(path):
    return json.loads(read_bytes(path))


def read_jsonl(path):
    return [json.loads(s) for s in read_bytes(path).splitlines() if s]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def digest_mask(label):
    return int.from_bytes(hashlib.sha256(label.encode()).digest(), "little") & 127


def fm(a, b):
    v = 0
    while b:
        if b & 1:
            v ^= a
        a <<= 1
        if a & 128:
            a ^= 131
        b >>= 1
    return v


def fp(a, n):
    v = 1
    while n:
        if n & 1:
            v = fm(v, a)
        a = fm(a, a)
        n >>= 1
    return v


def fi(a):
    assert a
    return fp(a, 126)


def padd(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u:
        if y != v or x == 0:
            return None
        lam = x ^ fm(y, fi(x))
        X = fm(lam, lam) ^ lam ^ 1
        return (X, fm(x, x) ^ fm(lam ^ 1, X))
    lam = fm(y ^ v, fi(x ^ u))
    X = fm(lam, lam) ^ lam ^ x ^ u ^ 1
    return (X, fm(lam, x ^ X) ^ X ^ y)


def pmul(P, k):
    Q = None
    while k:
        if k & 1:
            Q = padd(Q, P)
        P = padd(P, P)
        k >>= 1
    return Q


def neg(P):
    return None if P is None else (P[0], P[0] ^ P[1])


def curve_points():
    return [(x, y) for x in range(128) for y in range(128)
            if fm(y, y) ^ fm(x, y) == fm(fm(x, x), x) ^ fm(x, x) ^ 1]


def normal_basis():
    for beta in range(1, 128):
        cols = [fp(beta, 1 << j) for j in range(7)]
        span = {0}
        for c in cols:
            span |= {x ^ c for x in tuple(span)}
        if len(span) == 128:
            return beta, cols
    raise AssertionError("no normal basis")


def apply_cols(cols, mask):
    v = 0
    for j in range(7):
        if mask >> j & 1:
            v ^= cols[j]
    return v


def orbit(x):
    out = []
    for _ in range(7):
        if x in out:
            break
        out.append(x)
        x = fm(x, x)
    return out


def derive_bases(points, subgroup, cols):
    by_x = defaultdict(list)
    for P in subgroup:
        if P is not None:
            by_x[P[0]].append(P)
    candidate = None
    for c in range(64):
        flats = []
        for t in range(2):
            flats.append(tuple(apply_cols(cols, digest_mask(f"GFB-SAT-N7-v1-flat-{c:02d}-{t}-{z}"))
                               for z in "abc"))
        if any(b == 0 or z == 0 or b == z for _, b, z in flats):
            continue
        raw = set()
        mappings = []
        for t, (a, b, z) in enumerate(flats):
            for j, u, v in itertools.product(range(7), range(2), range(2)):
                x = a ^ (b if u else 0) ^ (z if v else 0)
                for _ in range(j):
                    x = fm(x, x)
                raw.add(x)
                mappings.append(((t, j, u, v), x))
        X = {x for x in raw if x != 0 and len(by_x[x]) == 2}
        reps = sorted({min(orbit(x)) for x in X})
        if len(reps) == 2 and len(X) == 14 and all(len(orbit(x)) == 7 for x in X):
            inverse = {}
            for sel, x in mappings:
                if x in X and x not in inverse:
                    inverse[x] = sel
            candidate = {"index": c, "flats": flats, "x": sorted(X),
                         "reps": reps, "raw": sorted(raw), "inverse": inverse,
                         "points": sorted(P for x in X for P in by_x[x])}
            break
    assert candidate is not None
    seen = []
    null = None
    for i in range(256):
        x = digest_mask(f"GFB-SAT-N7-v1-null-{i:03d}")
        if x == 0 or len(by_x[x]) != 2 or len(orbit(x)) != 7:
            continue
        rep = min(orbit(x))
        if rep in seen:
            continue
        for earlier in seen:
            if set((earlier, rep)) != set(candidate["reps"]):
                X = sorted(set(orbit(earlier)) | set(orbit(rep)))
                null = {"arrival_index": i, "reps": sorted((earlier, rep)),
                        "x": X, "points": sorted(P for xx in X for P in by_x[xx])}
                break
        if null is not None:
            break
        seen.append(rep)
    assert null is not None
    return candidate, null, by_x


def triples_for_q(Q, base):
    """Exact canonical x1<=x2<=x3 group completions, no SAT data."""
    pts = sorted(base)
    for a, P in enumerate(pts):
        for T in pts[a:]:
            if P[0] > T[0]:
                continue
            U = padd(P, T)
            need = padd(Q, neg(U))
            if need in base and T[0] <= need[0]:
                yield (P, T, need)


def parse_model(raw, nvars):
    lines = raw.decode().splitlines()
    statuses = [s[2:] for s in lines if s.startswith("s ")]
    vals = {}
    for s in lines:
        if s.startswith("v "):
            for n in map(int, s[2:].split()):
                if n:
                    assert abs(n) <= nvars and abs(n) not in vals
                    vals[abs(n)] = n > 0
    return statuses, vals


def parse_dimacs(raw):
    """Parse the archived extended DIMACS, including CMS native XOR lines.

    CMS x-lines assert XOR of signed literals = 1; a negative literal toggles
    the corresponding variable parity. The manifest is checked, not trusted.
    """
    header = None
    clauses = []
    rows = []
    for line in raw.decode().splitlines():
        if not line or line.startswith('c'):
            continue
        if line.startswith('p '):
            parts = line.split()
            assert parts[1]=='cnf' and len(parts)==4 and header is None
            header = (int(parts[2]),int(parts[3]))
            continue
        if line.startswith('x '):
            lits = [int(s) for s in line[2:].split()]
            assert lits[-1]==0
            lits = lits[:-1]
            assert lits and all(v for v in lits)
            rows.append({'vars':sorted(abs(v) for v in lits),
                         'rhs':1 ^ (sum(v<0 for v in lits)&1)})
        else:
            lits = [int(s) for s in line.split()]
            assert lits[-1]==0
            clauses.append(lits[:-1])
    assert header is not None and header[1]==len(clauses)+len(rows)
    return header[0],clauses,rows


def archive_data(path, manifest):
    b = read_bytes(path)
    out = {}
    with tarfile.open(fileobj=__import__('io').BytesIO(b), mode="r:gz") as tf:
        for member in tf.getmembers():
            assert member.isfile() and member.name not in out
            out[member.name] = tf.extractfile(member).read()
    listed = {e['path']: e for e in manifest['files']}
    assert set(out) == set(listed), (len(out), len(listed), set(out)^set(listed))
    for name, data in out.items():
        assert len(data) == listed[name]['bytes'] and sha(data) == listed[name]['sha256'], name
    return out, sha(b)


def quantile7(sorted_values, p):
    z = (len(sorted_values)-1)*p
    lo = int(z)
    return sorted_values[lo]*(1-(z-lo)) + sorted_values[min(lo+1,len(sorted_values)-1)]*(z-lo)


def bootstrap(vectors):
    rng = random.Random("GFB-SAT-N7-v1-bootstrap")
    samples = [[] for _ in vectors]
    for _ in range(10000):
        idx = [rng.randrange(8) for _ in range(8)]
        for j, v in enumerate(vectors):
            samples[j].append(statistics.median(v[i] for i in idx))
    return [(quantile7(sorted(a), .025),quantile7(sorted(a), .975)) for a in samples]


def propagate(clauses, xor_rows, nvars, units):
    assign = {}
    contradiction = False
    def put(v, bit):
        nonlocal contradiction
        if v in assign:
            if assign[v] != bit:
                contradiction = True
            return False
        assign[v] = bit
        return True
    for v, bit in units:
        put(v, bit)
    rounds = 0
    while not contradiction:
        rounds += 1
        old = len(assign)
        for clause in clauses:
            remaining = []
            satisfied = False
            for lit in clause:
                v = abs(lit)
                if v in assign:
                    if assign[v] == (lit > 0):
                        satisfied = True
                        break
                else:
                    remaining.append(lit)
            if satisfied:
                continue
            if not remaining:
                contradiction = True
                break
            if len(remaining) == 1:
                put(abs(remaining[0]), remaining[0] > 0)
                if contradiction:
                    break
        if contradiction:
            break
        # Full reduced echelon form over GF(2), least-variable pivot.
        pivots = {}
        for row in xor_rows:
            mask = 0
            rhs = row['rhs']
            for v in row['vars']:
                if v in assign:
                    rhs ^= int(assign[v])
                else:
                    mask ^= 1 << v
            while mask:
                pivot = (mask & -mask).bit_length()-1
                if pivot not in pivots:
                    pivots[pivot] = (mask, rhs)
                    break
                m, b = pivots[pivot]
                mask ^= m
                rhs ^= b
            if mask == 0 and rhs:
                contradiction = True
                break
        if contradiction:
            break
        for pivot in sorted(pivots, reverse=True):
            m, b = pivots[pivot]
            for other in list(pivots):
                if other < pivot:
                    mm, bb = pivots[other]
                    if mm >> pivot & 1:
                        pivots[other] = (mm ^ m, bb ^ b)
        for mask, rhs in pivots.values():
            if mask.bit_count() == 1:
                put(mask.bit_length()-1, bool(rhs))
                if contradiction:
                    break
        if len(assign) == old:
            break
    return {'contradiction':contradiction,'assigned':len(assign),'rounds':rounds}


def main():
    design_bytes = read_bytes(DESIGN)
    read_bytes(SPEC)
    assert sha(design_bytes) == '1419bc2107601476c4fd44f90d67475ec15e98eef68a35888df9abfaed0aa3e5'
    basis = read_json(RUN/'basis_manifest.json')
    cases = read_json(RUN/'case_manifest.json')
    science = read_jsonl(RUN/'receipts.jsonl')
    controls = read_jsonl(RUN/'control_receipts.jsonl')
    sci_manifest = read_json(RUN/'raw_manifest.json')
    ctl_manifest = read_json(RUN/'control_manifest.json')
    cnf_manifest = read_json(RUN/'cnf_xor_manifest.json')
    native_controls = read_json(RUN/'native_controls.json')
    control_replay = read_json(RUN/'control_replay.json')
    science_replay = read_json(RUN/'replay.json')
    sci_raw,sci_tar_hash = archive_data(RUN/'raw_outputs.tar.gz',sci_manifest)
    ctl_raw,ctl_tar_hash = archive_data(RUN/'control_outputs.tar.gz',ctl_manifest)
    beta, cols = normal_basis()
    E = curve_points()
    subgroup = {P for P in E if pmul(P,71) is None}
    subgroup.add(None)
    G = next(P for P in E if P[0] != 0 and pmul(P,71) is None)
    # Independent schoolbook polynomial multiplication and remainder check.
    for a in range(128):
        assert fm(a,a)==fp(a,2)
        for b in range(128):
            unreduced=0
            for j in range(7):
                if b>>j&1:
                    unreduced ^= a<<j
            while unreduced.bit_length()>7:
                unreduced ^= 131 << (unreduced.bit_length()-8)
            assert fm(a,b)==unreduced
        if a:
            assert fm(a,fi(a))==1
    for P in E:
        assert padd(P,neg(P)) is None
        assert (fm(P[0],P[0]),fm(P[1],P[1])) in E
    assert all(padd(P,Q) in subgroup for P in subgroup for Q in subgroup)
    assert all(fm(cols[j],cols[j])==cols[(j+1)%7] for j in range(7))
    cand,null,by_x = derive_bases(E,subgroup,cols)
    assert len(E) == 141 and len(subgroup) == 71  # affine points exclude infinity
    assert len(set(pmul(G,k) for k in range(71))) == 71
    assert beta == basis['candidate']['beta'] == basis['field']['normal_beta']
    assert cols == basis['candidate']['columns'] == basis['field']['normal_columns']
    assert list(G) == basis['field']['generator']
    assert cand['index'] == basis['candidate']['candidate_index']
    assert [list(x) for x in cand['flats']] == basis['candidate']['flats']
    assert cand['x'] == basis['candidate']['x_values'] and cand['reps'] == basis['candidate']['orbit_representatives']
    assert cand['raw'] == basis['candidate']['raw_x_values']
    assert [list(P) for P in cand['points']] == basis['candidate']['points']
    assert {str(x):list(sel) for x,sel in cand['inverse'].items()} == basis['candidate']['canonical_inverse']
    for item in basis['candidate']['all_mappings']:
        t,j,u,v=item['selector']
        if j==7:
            assert not item['valid'] and item['reason']=='j_7_forbidden' and item['x'] is None
            continue
        a,b,z=cand['flats'][t]
        x=a^(b if u else 0)^(z if v else 0)
        for _ in range(j):
            x=fm(x,x)
        assert x==item['x']
        should_valid=x in cand['inverse'] and cand['inverse'][x]==(t,j,u,v)
        assert item['valid']==should_valid
        assert item['reason']==('canonical' if should_valid else 'x_not_admitted')
    assert null['arrival_index'] == basis['null']['arrival_index']
    assert null['x'] == basis['null']['x_values'] and null['reps'] == basis['null']['orbit_representatives']
    assert [list(P) for P in null['points']] == basis['null']['points']
    ranked = sorted(range(1,71),key=lambda d:(hashlib.sha256(f'GFB-SAT-N7-v1-target-{d}'.encode()).digest(),d))[:16]
    assert ranked == cases['target_scalars']
    assert len(science)==64 and len(controls)==70
    assert native_controls['status']=='passed' and native_controls['target_workers']==0 and native_controls['solver_instances']==0
    assert native_controls['field_and_group']['curve_points']==142
    assert native_controls['field_and_group']['subgroup_points']==71
    assert control_replay['valid'] and control_replay['workers']==70 and control_replay['cms_descendants']==68
    assert science_replay['valid'] and len(science_replay['worker_replays'])==64
    assert len(cnf_manifest['cases'])==64
    assert {x['id'] for x in cnf_manifest['cases']}=={x['case_id'] for x in science}
    assert [x['id'] for x in cases['science_cases']] == [x['case_id'] for x in science]
    assert [x['id'] for x in cases['control_cases']] == [x['case_id'] for x in controls]
    for row in cases['science_cases']+cases['control_cases']:
        assert tuple(row['Q']) == pmul(G,row['scalar'])

    # Recompute all exact target outcomes and coverage from group law.
    bases = {'candidate':set(cand['points']),'null':set(null['points']),
             'small':{G,neg(G)}}
    oracle = {}
    for recipe,base in bases.items():
        oracle[recipe]={d:next(triples_for_q(pmul(G,d),base),None) for d in range(1,71)}
    coverage={recipe:sum(w is not None for w in rows.values()) for recipe,rows in oracle.items()}
    assert coverage['small']==4
    all_receipt_details=[]
    for phase,rows,raw in [('science',science,sci_raw),('controls',controls,ctl_raw)]:
        for rec in rows:
            ordinal=rec['ordinal']; cid=rec['case_id']; recipe=rec['worker_result']['base_recipe']
            base=f'raw/{phase}/{ordinal:03d}_{cid}'
            inp=raw[f'{base}/cwd/input.json']; res=raw[f'{base}/cwd/result.json']
            assert sha(inp)==rec['input_sha256'] and sha(res)==rec['result_sha256']
            assert sha(raw[f'{base}/worker.stdout'])==rec['stdout_sha256']
            assert sha(raw[f'{base}/worker.stderr'])==rec['stderr_sha256']
            assert rec['valid'] and rec['classification']=='completed_valid' and not rec['cap_reached'] and not rec['watchdog_reached']
            assert rec['outer_wait4']['exit_code']==0 and rec['outer_wait4']['rss_unit']=='bytes'
            assert rec['outer_wait4']['peak_rss']>0 and rec['outer_wait4']['user_seconds']>=0 and rec['outer_wait4']['system_seconds']>=0
            assert rec['wall_seconds']>0 and rec['worker_result']['Q']==rec['Q']
            assert rec['scalar_driver_only'] in (range(1,71)) and tuple(rec['Q'])==pmul(G,rec['scalar_driver_only'])
            w=oracle[recipe][rec['scalar_driver_only']]
            expected='SAT' if w else 'UNSAT'
            assert rec['expected_status']==expected==rec['worker_result']['status']
            assert rec['worker_result']['shortcut']==(tuple(rec['Q']) in bases[recipe])
            if w:
                witness=tuple(tuple(P) for P in rec['worker_result']['witness'])
                assert len(witness)==3 and all(P in bases[recipe] for P in witness)
                assert padd(padd(witness[0],witness[1]),witness[2])==tuple(rec['Q'])
            else:
                assert rec['worker_result'].get('witness') is None
            cms=rec['worker_result']['cms']
            if cms is not None:
                assert cms['exit_code']==(10 if w else 20)
                assert cms['wait4_peak_rss']>0 and cms['wait4_peak_rss_unit']=='bytes'
                assert cms['wait4_user_seconds']>=0 and cms['wait4_system_seconds']>=0
                assert sha(raw[f'{base}/cwd/cms.stdout'])==cms['stdout_sha256']
                assert sha(raw[f'{base}/cwd/cms.stderr'])==cms['stderr_sha256']
                instance=json.loads(raw[f'{base}/cwd/INSTANCE.manifest.json'])
                cnf=raw[f'{base}/cwd/INSTANCE.cnf']
                assert sha(cnf)==rec['worker_result']['instance']['cnf_sha256']
                assert sha(raw[f'{base}/cwd/INSTANCE.manifest.json'])==rec['worker_result']['instance']['manifest_sha256']
                assert len(instance['clauses'])==rec['worker_result']['instance']['clauses']
                assert len(instance['xor_rows'])==rec['worker_result']['instance']['xor_rows']
                assert instance['nvars']==rec['worker_result']['instance']['nvars']
                dimacs_nvars,dimacs_clauses,dimacs_rows=parse_dimacs(cnf)
                assert dimacs_nvars==instance['nvars']
                assert dimacs_clauses==instance['clauses']
                assert dimacs_rows==instance['xor_rows']
                statuses,model=parse_model(raw[f'{base}/cwd/cms.stdout'],instance['nvars'])
                assert statuses==(['SATISFIABLE'] if w else ['UNSATISFIABLE'])
                if w:
                    assert len(model)==instance['nvars']
                    assert all(any(model[abs(lit)]==(lit>0) for lit in clause) for clause in instance['clauses'])
                    assert all((sum(model[v] for v in row['vars'])&1)==row['rhs'] for row in instance['xor_rows'])
                    xv=[sum(int(model[v])<<j for j,v in enumerate(instance['inputs'][f'x{i}'])) for i in (1,2,3)]
                    assert xv==sorted(xv) and all(x in {P[0] for P in bases[recipe]} for x in xv)
                    assert any(tuple(P[0] for P in triple)==tuple(xv) for triple in triples_for_q(tuple(rec['Q']),bases[recipe]))
            else:
                assert rec['worker_result']['shortcut'] or rec['arm']=='direct_mitm'
            all_receipt_details.append({'case_id':cid,'oracle':expected,'shortcut':rec['worker_result']['shortcut'],
                                        'cms':cms is not None,'model_checked':cms is not None and w is not None})
    assert sum(x['cms'] for x in all_receipt_details if x['case_id'].startswith('control'))==68
    assert sum(x['cms'] for x in all_receipt_details if x['case_id'].startswith('case'))==cases['counts']['science_cms']
    assert science_replay['counts']['actual_cms']==cases['counts']['science_cms']
    assert control_replay['control_archive_sha256']==ctl_tar_hash
    for item in cnf_manifest['cases']:
        rec=next(x for x in science if x['case_id']==item['id'])
        assert item['arm']==rec['arm']
        assert item['instance']==rec['worker_result'].get('instance')
    indexed=defaultdict(dict)
    for r in science:
        indexed[r['case_index']][r['arm']]=r
    ratios={name:[] for name in ('flat_explicit','flat_direct','flat_null')}
    for i in range(9,17):
        r=indexed[i]
        assert len(r)==4
        f=r['flat_sat']['wall_seconds']
        ratios['flat_explicit'].append(f/r['explicit_same_B']['wall_seconds'])
        ratios['flat_direct'].append(f/r['direct_mitm']['wall_seconds'])
        ratios['flat_null'].append(f/r['null_sat']['wall_seconds'])
    ci=bootstrap(list(ratios.values()))
    ratio_out={name:{'per_case':dict(zip(range(9,17),values)),'median':statistics.median(values),
                     'bootstrap_type7_95':list(interval)} for (name,values),interval in zip(ratios.items(),ci)}

    # Prefixes are selected anew from frozen SHA256 ordering, not read from
    # producer's prefix summary. Only non-shortcut held-out Q are eligible.
    prefix_cases={}
    for i in range(9,17):
        row=indexed[i]['flat_sat']
        if row['worker_result']['shortcut']:
            continue
        d=row['scalar_driver_only']; Q=tuple(row['Q']); X=cand['x']
        pairs=sorted(itertools.combinations_with_replacement(X,2),
                     key=lambda p:(hashlib.sha256(f'GFB-SAT-N7-v1-prefix-{d}-{p[0]}-{p[1]}'.encode()).digest(),p))[:32]
        prefixes=[(x,None) for x in X]+pairs
        assert len(prefixes)==46
        arms={}
        oracle_bits=[]
        completions=list(triples_for_q(Q,bases['candidate']))
        for x,y in prefixes:
            oracle_bits.append(any(T[0][0]==x and (y is None or T[1][0]==y) for T in completions))
        for arm in ('flat_sat','explicit_same_B'):
            rec=indexed[i][arm]; base=f"raw/science/{rec['ordinal']:03d}_{rec['case_id']}"
            inst=json.loads(sci_raw[f'{base}/cwd/INSTANCE.manifest.json'])
            _,raw_clauses,raw_rows=parse_dimacs(sci_raw[f'{base}/cwd/INSTANCE.cnf'])
            entries=[]
            for (x,y),extendible in zip(prefixes,oracle_bits):
                units=[(v,bool(x>>j&1)) for j,v in enumerate(inst['inputs']['x1'])]
                if y is not None:
                    units.extend((v,bool(y>>j&1)) for j,v in enumerate(inst['inputs']['x2']))
                z=propagate(raw_clauses,raw_rows,inst['nvars'],units)
                assert not (z['contradiction'] and extendible), (i,arm,x,y)
                entries.append({'x1':x,'x2':y,'extendible':extendible,**z})
            arms[arm]={'entries':entries,'contradictions':sum(e['contradiction'] for e in entries),
                       'fraction':sum(e['contradiction'] for e in entries)/46}
        prefix_cases[i]={'scalar':d,'arms':arms,'oracle_extendible':sum(oracle_bits),
                         'paired_fraction_difference':arms['flat_sat']['fraction']-arms['explicit_same_B']['fraction']}
    prefix_effect=statistics.median(v['paired_fraction_difference'] for v in prefix_cases.values()) if prefix_cases else None
    # This permitted progress stream is consulted only after independent
    # derivation; no value from it enters the calculation above.
    progress=read_jsonl(RUN/'prefix_progress.jsonl')
    own={(int(i),entry['x1'],entry['x2']):{'arm':arm,'value':entry}
         for i,case in prefix_cases.items() for arm,summary in case['arms'].items()
         for entry in summary['entries']}
    assert len(progress)==46*len(prefix_cases)
    for row in progress:
        case=prefix_cases[row['case_index']]
        for arm in ('flat_sat','explicit_same_B'):
            e=next(e for e in case['arms'][arm]['entries']
                   if e['x1']==row['x1'] and e['x2']==row['x2'])
            assert e['extendible']==row['oracle_extendible']
            assert all(e[k]==row['arms'][arm][k] for k in ('assigned','rounds','contradiction'))
    output={'schema':'crypto.autoresearch.gfb_blind_only_rederivation.v1',
            'task_id':'TASK-20260921-4160c9','protocol_sha256':sha(design_bytes),
            'archive_sha256':{'science':sci_tar_hash,'controls':ctl_tar_hash},
            'field':{'curve_points_including_infinity':len(E)+1,'subgroup_points_including_infinity':len(subgroup),
                     'generator':G,'normal_beta':beta,'normal_columns':cols},
            'bases':{'candidate':{'index':cand['index'],'x':cand['x'],'reps':cand['reps'],'points':len(cand['points'])},
                     'null':{'arrival_index':null['arrival_index'],'x':null['x'],'reps':null['reps'],'points':len(null['points'])}},
            'coverage':coverage,'targets':ranked,
            'receipt_checks':{'science':len(science),'controls':len(controls),
                              'science_cms':sum(x['cms'] for x in all_receipt_details if x['case_id'].startswith('case')),
                              'control_cms':sum(x['cms'] for x in all_receipt_details if x['case_id'].startswith('control')),
                              'models_checked':sum(x['model_checked'] for x in all_receipt_details),
                              'details':all_receipt_details},
            'heldout_ratios':ratio_out,
            'prefix':{'eligible_cases':len(prefix_cases),'cases':prefix_cases,
                      'paired_median_fraction_difference':prefix_effect,
                      'all_refutations_sound':True,
                      'progress_rows_exact_match':len(progress)},
            'sources_read':sorted(READS)}
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'coverage':coverage,'heldout_ratios':{k:{'median':v['median'],'CI':v['bootstrap_type7_95']} for k,v in ratio_out.items()},
                      'prefix_eligible':len(prefix_cases),'prefix_effect':prefix_effect,
                      'models_checked':output['receipt_checks']['models_checked']}))


if __name__=='__main__':
    main()
