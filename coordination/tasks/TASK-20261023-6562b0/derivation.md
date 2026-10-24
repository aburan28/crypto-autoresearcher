# Independent held-out balanced-slot derivation

Task TASK-20261023-6562b0; review-adversarial / xhigh requested. Published HEAD 90b2a9e2a13415e59ef1cd5e7b6eb1f18d90e436. This initial section was written 2026-10-23T17:11:41.393869+00:00 before reading the successor driver, historical audits, or any generated summary. No blind_from path was read.

I independently keyed every row by (bits, curve seed, solver seed, repetition, arm), required the exact 162-row grid and raw-result/arms equality, and calculated r=(A+B)/(2C). The estimate is exp(mean(log r)); A/A is max(exp(mean(log(A/B))), its reciprocal). A Python random.Random(3065) stream makes 5,000 draws: in ascending bits order, independently choose three of curve seeds (3,4,5) with replacement; append all six log ratios for each chosen curve. Each resample therefore has 54 paired ratios with the within-curve solver/repetition dependence intact. Sort resample estimates. The primary empirical endpoint uses sorted index floor((5000-1)*q); inverse-CDF and linearly interpolated alternatives are also recorded to expose percentile-convention sensitivity. The conclusion is invariant to these conventions.

```json
{
  "created_before_reading_successor_source_or_historical_reports": true,
  "raw_rows": 162,
  "pairs": 54,
  "geometric_speedup": 1.160582357766089,
  "aa_signed_geomean": 1.0441708205043603,
  "aa_factor": 1.0441708205043603,
  "bootstrap_seed": 3065,
  "bootstrap_resamples": 5000,
  "interval_floor_nminus1": [
    1.1267519846188838,
    1.1974121252256216
  ],
  "interval_linear_nminus1": [
    1.1267519846188838,
    1.1974183448945268
  ],
  "interval_empirical_inverse_cdf": [
    1.1267519846188838,
    1.1974121252256216
  ],
  "strict_numerical_gate": true,
  "by_bits": {
    "12": 1.2766544988264144,
    "14": 1.1291810603858188,
    "16": 1.0844035441064377
  },
  "by_candidate_slot": {
    "0": 1.1583105993789575,
    "1": 1.1801829285691063,
    "2": 1.1435457251592789
  },
  "by_curve": {
    "12:3": 1.2483990788569232,
    "12:4": 1.3615696023225503,
    "12:5": 1.2241280607666098,
    "14:3": 1.2187084352062292,
    "14:4": 1.0445842757485186,
    "14:5": 1.1309605452266123,
    "16:3": 1.0540753373837972,
    "16:4": 1.11903462876802,
    "16:5": 1.081079436815493
  },
  "ratio_range": [
    0.7081882627771514,
    1.5411927270330632
  ],
  "sum_full_seconds": 5.833392212
}
```

| bits | curve seed | solver seed | repetition | reference A seconds | reference B seconds | candidate seconds | ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 3 | 0 | 0 | 0.001967341 | 0.002208693 | 0.001727321 | 1.2088181640818356 |
| 12 | 3 | 0 | 1 | 0.002419269 | 0.002484336 | 0.001796115 | 1.3650587518059814 |
| 12 | 3 | 0 | 2 | 0.002291618 | 0.002372729 | 0.002429184 | 0.9600645731241437 |
| 12 | 3 | 1 | 0 | 0.002347091 | 0.00227356 | 0.002151848 | 1.073647162810756 |
| 12 | 3 | 1 | 1 | 0.002431928 | 0.002685217 | 0.00174662 | 1.4648707217368404 |
| 12 | 3 | 1 | 2 | 0.002683946 | 0.002031628 | 0.001551878 | 1.519312085099473 |
| 12 | 4 | 0 | 0 | 0.002948974 | 0.003396695 | 0.002457846 | 1.290900446976743 |
| 12 | 4 | 0 | 1 | 0.003239639 | 0.002972128 | 0.002405468 | 1.2911763947805583 |
| 12 | 4 | 0 | 2 | 0.003041612 | 0.002893952 | 0.00256007 | 1.1592581452850899 |
| 12 | 4 | 1 | 0 | 0.004994302 | 0.00375966 | 0.002857396 | 1.5318076318438187 |
| 12 | 4 | 1 | 1 | 0.005583386 | 0.003957346 | 0.003095243 | 1.5411927270330632 |
| 12 | 4 | 1 | 2 | 0.004523876 | 0.00339345 | 0.002834191 | 1.3967523713116017 |
| 12 | 5 | 0 | 0 | 0.003597997 | 0.003222634 | 0.002797556 | 1.2190338638440124 |
| 12 | 5 | 0 | 1 | 0.003498538 | 0.00311298 | 0.002656034 | 1.244622245046562 |
| 12 | 5 | 0 | 2 | 0.003489144 | 0.003199189 | 0.003337536 | 1.0019866452376842 |
| 12 | 5 | 1 | 0 | 0.002011688 | 0.0013268 | 0.001134442 | 1.4714229550739482 |
| 12 | 5 | 1 | 1 | 0.001531297 | 0.001372099 | 0.001420952 | 1.0216376063371597 |
| 12 | 5 | 1 | 2 | 0.002089214 | 0.001288893 | 0.001147181 | 1.4723513551915521 |
| 14 | 3 | 0 | 0 | 0.018062414 | 0.019901342 | 0.014095083 | 1.3467021088134068 |
| 14 | 3 | 0 | 1 | 0.018640326 | 0.020391568 | 0.01680647 | 1.1612163053871514 |
| 14 | 3 | 0 | 2 | 0.017822444 | 0.020365458 | 0.015401803 | 1.2397218039991809 |
| 14 | 3 | 1 | 0 | 0.013500711 | 0.012367571 | 0.011818008 | 1.0944434121215691 |
| 14 | 3 | 1 | 1 | 0.012210908 | 0.0120263 | 0.010354362 | 1.1703863550453422 |
| 14 | 3 | 1 | 2 | 0.017801203 | 0.012642595 | 0.011537226 | 1.319372525076652 |
| 14 | 4 | 0 | 0 | 0.026558769 | 0.026178149 | 0.021297687 | 1.2380902677365857 |
| 14 | 4 | 0 | 1 | 0.025293131 | 0.023915033 | 0.03474229 | 0.7081882627771514 |
| 14 | 4 | 0 | 2 | 0.022236326 | 0.025430556 | 0.026131969 | 0.9120415304334701 |
| 14 | 4 | 1 | 0 | 0.023579931 | 0.02301923 | 0.019856406 | 1.1734037116283782 |
| 14 | 4 | 1 | 1 | 0.025190748 | 0.02280551 | 0.020528955 | 1.1689893128997555 |
| 14 | 4 | 1 | 2 | 0.023121955 | 0.022586341 | 0.019296466 | 1.184369614622698 |
| 14 | 5 | 0 | 0 | 0.040050898 | 0.040851069 | 0.033603849 | 1.2037604233967365 |
| 14 | 5 | 0 | 1 | 0.036977008 | 0.039887093 | 0.032229455 | 1.192451144457764 |
| 14 | 5 | 0 | 2 | 0.038950107 | 0.036702977 | 0.037249375 | 1.015494676085169 |
| 14 | 5 | 1 | 0 | 0.032083637 | 0.031913852 | 0.03133244 | 1.0212656435311132 |
| 14 | 5 | 1 | 1 | 0.048423829 | 0.034424418 | 0.031273933 | 1.3245575316670277 |
| 14 | 5 | 1 | 2 | 0.03275208 | 0.032490707 | 0.03073871 | 1.0612479671398052 |
| 16 | 3 | 0 | 0 | 0.115636691 | 0.134819642 | 0.119398114 | 1.0488286816657757 |
| 16 | 3 | 0 | 1 | 0.12487188 | 0.119429091 | 0.115441018 | 1.0581203078094823 |
| 16 | 3 | 0 | 2 | 0.124846208 | 0.120818404 | 0.11096096 | 1.1069866915354734 |
| 16 | 3 | 1 | 0 | 0.167820683 | 0.171172601 | 0.17404118 | 0.9738881453228484 |
| 16 | 3 | 1 | 1 | 0.158780642 | 0.172344338 | 0.150111438 | 1.102930544173456 |
| 16 | 3 | 1 | 2 | 0.174356456 | 0.162738052 | 0.162155251 | 1.0394190318264809 |
| 16 | 4 | 0 | 0 | 0.082738674 | 0.077052884 | 0.067537841 | 1.1829779841496562 |
| 16 | 4 | 0 | 1 | 0.081543581 | 0.080999625 | 0.071368527 | 1.138759708463648 |
| 16 | 4 | 0 | 2 | 0.073812435 | 0.091995721 | 0.074907371 | 1.106754607634007 |
| 16 | 4 | 1 | 0 | 0.065358222 | 0.069656344 | 0.058948697 | 1.1451870259320576 |
| 16 | 4 | 1 | 1 | 0.059529568 | 0.057769716 | 0.056695006 | 1.0344763346528265 |
| 16 | 4 | 1 | 2 | 0.06249847 | 0.061389336 | 0.055717867 | 1.1117421813724493 |
| 16 | 5 | 0 | 0 | 0.017152372 | 0.019429248 | 0.016620965 | 1.1004661883350333 |
| 16 | 5 | 0 | 1 | 0.01772456 | 0.019513985 | 0.020286754 | 0.9178044205593462 |
| 16 | 5 | 0 | 2 | 0.018909055 | 0.016980505 | 0.016701713 | 1.0744275153093579 |
| 16 | 5 | 1 | 0 | 0.039759983 | 0.039059772 | 0.036861825 | 1.0691244261509025 |
| 16 | 5 | 1 | 1 | 0.042516198 | 0.042321315 | 0.034161274 | 1.2417205663933963 |
| 16 | 5 | 1 | 2 | 0.037256648 | 0.041249978 | 0.035423117 | 1.1081270177325164 |

Raw input SHA-256:

- `experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af/raw-result.json`: `c2bd00bd9d90cbac5978d622f8f5fab4b335bd86c51a685f747fce2124792914`
- `experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af/arms.jsonl`: `6b1f420b7529d9de0e4a5def8c8f40716b48db7a9599087a31570f2184ccc1e9`
- `experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af/instances.json`: `4184998ef4eca9d78284c17f72ebb566b47a64f2fd6cedbea21318a33b64b1fb`

## Independent arithmetic and coverage replay

The following code adapts the prior independent reviewer arithmetic (TASK-20261023-18b489), not producer arithmetic. It imports no native curve/solver/checker and performs no solve performance trial. I reused the independent affine group law, geometric decomposition reconstruction and dense elimination after saving my own timing derivation. The code regenerates the new nine public instances, 18 seed streams, all target and relation digests, first recovery/rank/LA counts, setup/query/full group costs, and all 162 recovery witnesses. Exhaustive group point counts verify the prime orders.

```python
from pathlib import Path
import collections,copy,hashlib,itertools,json,math,random,statistics,subprocess,sys,tempfile
ROOT=Path('/workspace/crypto-autoresearcher')
RUN=ROOT/'experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af'
# No scientific run or scratch output needed for independent arithmetic.
raw=json.loads((RUN/'raw-result.json').read_text())
cfg=json.loads((ROOT/'config/ic-target-balanced-benchmark.json').read_text())
def H(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def filehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(A,B,p,a):
    if A is None:return B
    if B is None:return A
    x,y=A;u,v=B
    if x==u and (y+v)%p==0:return None
    slope=((3*x*x+a)*pow(2*y,-1,p) if x==u else (v-y)*pow(u-x,-1,p))%p
    z=(slope*slope-x-u)%p
    return z,(slope*(x-z)-y)%p
# Scalar multiplication uses a Montgomery-style two-register ladder;
# no producer group class, target engine, S3 polynomial or checker is imported.
def mul(n,A,p,a):
    L,R=None,A
    for bit in format(n,'b'):
        if bit=='0':R=add(L,R,p,a);L=add(L,L,p,a)
        else:L=add(L,R,p,a);R=add(R,R,p,a)
    return L
def neg(A,p):return None if A is None else (A[0],-A[1]%p)
def prime(n):return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))
assert raw['config']==cfg and raw['config_sha256']==H(cfg)
assert raw['instances']==json.loads((RUN/'instances.json').read_text())
assert raw['rows']==[json.loads(x) for x in (RUN/'arms.jsonl').read_text().splitlines()]
expected=list(itertools.product(cfg['bits'],cfg['curve_seeds'],cfg['solver_seeds'],range(cfg['repetitions']),cfg['arms']))
assert len(raw['rows'])==len(expected)==162
assert set(expected)=={tuple(r[k] for k in ('bits','curve_seed','solver_seed','repetition','arm')) for r in raw['rows']}
# Independently require the full held-out sequential schedule and crossing.
from collections import Counter
for i,coords in enumerate(itertools.product(cfg['bits'],cfg['curve_seeds'],cfg['solver_seeds'],range(cfg['repetitions']))):
    rows=raw['rows'][3*i:3*i+3]
    sequence=list(cfg['arms'])
    if coords[2]==1:sequence=sequence[::-1]
    sequence=sequence[coords[3]:]+sequence[:coords[3]]
    assert [r['arm'] for r in rows]==sequence
    assert all(tuple(r[k] for k in ('bits','curve_seed','solver_seed','repetition'))==coords and r['order']==j for j,r in enumerate(rows))
for bits,curve,seed,arm in itertools.product(cfg['bits'],cfg['curve_seeds'],cfg['solver_seeds'],cfg['arms']):
    assert sorted(r['order'] for r in raw['rows'] if (r['bits'],r['curve_seed'],r['solver_seed'],r['arm'])==(bits,curve,seed,arm))==[0,1,2]
for bits,curve in itertools.product(cfg['bits'],cfg['curve_seeds']):
    permutations=[tuple(r['arm'] for r in raw['rows'][i:i+3]) for i in range(0,162,3) if (raw['rows'][i]['bits'],raw['rows'][i]['curve_seed'])==(bits,curve)]
    assert set(permutations)==set(itertools.permutations(cfg['arms'])) and len(permutations)==6
base={};identities=[]
for key,I in raw['instances'].items():
    p,a,b,N=(I[k] for k in ('p','a','b','order'));P,Q=tuple(I['P']),tuple(I['Q'])
    assert prime(p) and prime(N) and N!=p and (4*a**3+27*b*b)%p
    assert I['bits']==p.bit_length() and key==f"{I['bits']}:{I['curve_seed']}"
    count=1+sum(1 if (v:=(x**3+a*x+b)%p)==0 else (2 if pow(v,(p-1)//2,p)==1 else 0) for x in range(p))
    assert count==N
    for point in (P,Q):
        assert all(0<=c<p for c in point) and (point[1]**2-point[0]**3-a*point[0]-b)%p==0
        assert mul(N,point,p,a) is None
    assert I['public_expected_k']==random.Random(f"target|{I['bits']}|{I['curve_seed']}|0").randrange(1,N)
    assert mul(I['public_expected_k'],P,p,a)==Q
    roots={y*y%p:y for y in range(1,(p+1)//2)}
    F=[]
    for x in range(p):
        y=roots.get((x**3+a*x+b)%p)
        if y is not None:F.append((x,y))
        if len(F)==max(4,math.ceil(math.sqrt(N)/2)):break
    base[key]=F
    identities.append(dict(key=key,p=p,a=a,b=b,order=N,P=P,Q=Q,fb_size=len(F)))
pairs=collections.defaultdict(dict);streams={};counts=[]
core=('k','verified','m','engine','accelerated','factor_base','relations','rank','attempts','s3_solves','membership_tests','la_ops','la_pivot','msolve_calls','msolve_seconds','censored_attempts','table_arity','table_entries','table_s3_solves','harvest')
for row in raw['rows']:
    d=row['result'];I=raw['instances'][row['instance_key']];p,a,b,N=(I[k] for k in ('p','a','b','order'));P,Q=tuple(I['P']),tuple(I['Q'])
    assert row['status']=='completed' and d['verified'] is True and d['censored_attempts']==0
    assert type(d['k']) is int and 0<=d['k']<N and mul(d['k'],P,p,a)==Q
    assert row['pair']==f"{row['instance_key']}:{row['solver_seed']}:{row['repetition']}"
    assert row['recorded_targets']==d['attempts'] and d['m']==2 and d['engine']=='mitm' and d['accelerated'] is False and d['harvest'] is None
    assert row['factor_base_points']==[list(x) for x in base[row['instance_key']]] and row['factor_base_sha256']==H(base[row['instance_key']])
    F=base[row['instance_key']];assert d['factor_base']==dict(kind='small_x',size=len(F),bound=F[-1][0]+1)
    key=(row['instance_key'],row['solver_seed'],d['attempts'])
    if key not in streams:
        rng=random.Random(f"ic|{p}|{a}|{b}|2|small_x|{row['solver_seed']}")
        T=[];S=[];AB=[];ref=win=0;s3=membership=decompops=0
        idx={V[0]:j for j,V in enumerate(F)}
        for z in range(d['attempts']):
            alpha,beta=rng.randrange(N),rng.randrange(1,N);AB.append((alpha,beta))
            R=add(mul(alpha,P,p,a),mul(beta,Q,p,a),p,a);T.append(R)
            ref+=alpha.bit_length()+alpha.bit_count()+beta.bit_length()+beta.bit_count()+1
            win+=1+sum(bool((n>>q)&15) for n in (alpha,beta) for q in range(0,n.bit_length(),4))
            found=None
            if R is not None:
                for i,V in enumerate(F):
                    s3+=1
                    # Geometrically derive S3 root x values by actual group sums.
                    roots=sorted({Z[0] for Z in (add(R,V,p,a),add(R,neg(V,p),p,a)) if Z is not None})
                    for x in roots:
                        membership+=1;j=idx.get(x)
                        if j is None or j<i:continue
                        for sign in (1,-1):
                            Z=add(R,neg(V,p) if sign==1 else V,p,a);decompops+=1
                            if Z is not None and Z[0]==x:
                                found=[(i,sign),(j,1 if Z==F[j] else -1)];break
                        if found is not None:break
                    if found is not None:break
            if found is not None:
                Z=None
                for j,s in found:Z=add(Z,F[j] if s==1 else neg(F[j],p),p,a)
                assert Z==R;decompops+=2
            S.append(found)
        streams[key]=dict(relation_rows=S,scalars=AB,target_digest=H(T),relation_digest=H(S),reference_ops=ref,window_query_ops=win,s3=s3,membership=membership,decompops=decompops,relations=sum(x is not None for x in S))
    st=streams[key]
    assert row['targets_sha256']==st['target_digest']
    assert row['relations_sha256']==st['relation_digest']
    assert d['s3_solves']==st['s3'] and d['membership_tests']==st['membership'] and d['relations']==st['relations']
    rem=N-1;setup=slots=nonzero=0
    while rem:
        m=min(15,rem);setup+=2*(m-1);slots+=2*(m+1);nonzero+=2*m;rem>>=4
        if rem:setup+=8
    if row['arm']=='fixed_window':
        assert d['target_engine']=='fixed_window' and d['target_window']==4
        assert d['target_setup_ops']==setup and d['target_table_entries']==slots
        assert d['target_table_coordinate_bytes']==2*((p.bit_length()+7)//8)*nonzero
        assert d['target_ops']==setup+st['window_query_ops'] and 0<d['seconds_target_setup']<row['seconds_full_solve']
    else:
        assert d['target_engine']=='reference' and d['target_window'] is None
        assert d['target_ops']==st['reference_ops'] and d['target_setup_ops']==d['target_table_entries']==d['target_table_coordinate_bytes']==d['seconds_target_setup']==0
    assert d['group_ops']==d['target_ops']+st['decompops']
    assert row['full_curve_group_ops']==d['group_ops']+d['k'].bit_length()+d['k'].bit_count()
    assert d['table_arity']==1 and d['table_entries']==len(F) and d['table_s3_solves']==0
    for k in ('seconds_full_solve','cpu_seconds_full_solve','peak_rss_bytes'):assert math.isfinite(row[k]) and row[k]>0
    assert row['seconds_full_solve']>d['seconds_total']>0
    assert abs(sum(d[k] for k in ('seconds_factor_base','seconds_table','seconds_relations','seconds_linalg'))-d['seconds_total'])<1e-12
    pairs[row['pair']][row['arm']]=row
for key,A in pairs.items():
    R=A['reference_a']
    for C in (A['reference_b'],A['fixed_window']):
        assert all(R['result'][k]==C['result'][k] for k in core)
        assert R['full_curve_group_ops']-R['result']['target_ops']==C['full_curve_group_ops']-C['result']['target_ops']

for key,st in streams.items():
    I=raw['instances'][key[0]];N=I['order'];width=len(base[key[0]])
    pivots=[];seen=[0]*width;fill=[0]*width;laops=0;recovered=None;relcount=0
    for attempt,(rel,(alpha,beta)) in enumerate(zip(st['relation_rows'],st['scalars']),1):
        if rel is None:continue
        relcount+=1;v=[0]*(width+2)
        for i,sign in rel:v[i]=(v[i]+sign)%N
        v[-2]=(-beta)%N;v[-1]=alpha
        for i,x in enumerate(v[:-2]):seen[i]+=bool(x)
        for col,u in pivots:
            scale=v[col]
            if scale:
                v=[(x-scale*y)%N for x,y in zip(v,u)]
                laops+=sum(bool(x) for x in u[:-2])+2
        nonzero=[i for i,x in enumerate(v[:-2]) if x]
        if nonzero:
            col=min(nonzero,key=lambda i:(fill[i],seen[i],i))
            inv=pow(v[col],-1,N);u=[x*inv%N for x in v]
            pivots.append((col,u));laops+=len(nonzero)+2
            for i,x in enumerate(u[:-2]):fill[i]+=bool(x)
        elif v[-2]:
            recovered=v[-1]*pow(v[-2],-1,N)%N
            break
    R=next(r['result'] for r in raw['rows'] if r['instance_key']==key[0] and r['solver_seed']==key[1])
    assert attempt==key[2] and recovered==R['k'] and len(pivots)==R['rank'] and laops==R['la_ops'] and relcount==R['relations'],key

lock=json.loads((ROOT/cfg['environment_lock']).read_text())
assert raw['environment_lock']==raw['environment']==lock and raw['environment_sha256']==H(lock)
assert all(r['worker_affinity']==[0] and r['environment_sha256']==H(lock) and all(len(r[x])==3 and all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in r[x]) for x in ('load_before','load_after')) for r in raw['rows'])
summary=dict(curves=len(identities),streams=len(streams),rows=len(raw['rows']),pair_cells=len(pairs),all_six_permutations_per_curve=True,all_slots_per_exact_curve_solver_arm=True,prime_orders_point_counted=True,independent_kP_equals_Q_certificates=162,unique_target_observations=sum(k[2] for k in streams),worker_target_observations=sum(r['result']['attempts'] for r in raw['rows']),attempt_range=[min(r['result']['attempts'] for r in raw['rows']),max(r['result']['attempts'] for r in raw['rows'])],affinity_and_environment_match=162,full_group_ops_by_arm={a:sum(r['full_curve_group_ops'] for r in raw['rows'] if r['arm']==a) for a in cfg['arms']},target_ops_by_arm={a:sum(r['result']['target_ops'] for r in raw['rows'] if r['arm']==a) for a in cfg['arms']},load_range={x:[[min(r[x][j] for r in raw['rows']),max(r[x][j] for r in raw['rows'])] for j in range(3)] for x in ('load_before','load_after')},worker_time_minus_internal_microseconds=[min((r['seconds_full_solve']-r['result']['seconds_total'])*1e6 for r in raw['rows']),max((r['seconds_full_solve']-r['result']['seconds_total'])*1e6 for r in raw['rows'])],setup_microseconds=[min(r['result']['seconds_target_setup']*1e6 for r in raw['rows'] if r['arm']=='fixed_window'),max(r['result']['seconds_target_setup']*1e6 for r in raw['rows'] if r['arm']=='fixed_window')],rss_range=[min(r['peak_rss_bytes'] for r in raw['rows']),max(r['peak_rss_bytes'] for r in raw['rows'])],target_entries_range=[min(r['result']['target_table_entries'] for r in raw['rows'] if r['arm']=='fixed_window'),max(r['result']['target_table_entries'] for r in raw['rows'] if r['arm']=='fixed_window')],target_payload_range=[min(r['result']['target_table_coordinate_bytes'] for r in raw['rows'] if r['arm']=='fixed_window'),max(r['result']['target_table_coordinate_bytes'] for r in raw['rows'] if r['arm']=='fixed_window')])

```

Observed stdout/result:

```json
{
  "curves": 9,
  "streams": 18,
  "rows": 162,
  "pair_cells": 54,
  "all_six_permutations_per_curve": true,
  "all_slots_per_exact_curve_solver_arm": true,
  "prime_orders_point_counted": true,
  "independent_kP_equals_Q_certificates": 162,
  "unique_target_observations": 1549,
  "worker_target_observations": 13941,
  "attempt_range": [
    10,
    178
  ],
  "affinity_and_environment_match": 162,
  "full_group_ops_by_arm": {
    "reference_a": 200856,
    "fixed_window": 50490,
    "reference_b": 200856
  },
  "target_ops_by_arm": {
    "reference_a": 193698,
    "fixed_window": 43332,
    "reference_b": 193698
  },
  "load_range": {
    "load_before": [
      [
        0.0,
        0.55078125
      ],
      [
        0.015625,
        0.15673828125
      ],
      [
        0.0,
        0.04833984375
      ]
    ],
    "load_after": [
      [
        0.0,
        0.55078125
      ],
      [
        0.015625,
        0.15673828125
      ],
      [
        0.0,
        0.04833984375
      ]
    ]
  },
  "worker_time_minus_internal_microseconds": [
    64.07699975212715,
    1248.8540004310482
  ],
  "setup_microseconds": [
    78.27799981896533,
    325.8990000176709
  ],
  "rss_range": [
    29749248,
    31322112
  ],
  "target_entries_range": [
    82,
    118
  ],
  "target_payload_range": [
    304,
    440
  ]
}
```

## Actual offline checker controls

The real successor check_directory was called on scratch copies of raw/arms/instances. Each mutated journal was synchronized with its raw rows, so a journal mismatch could not mask the intended refusal. All generated checker stdout was captured and left semantically unread, and no generated validation file was opened. Runtime imports of the unchanged base checker are necessary for these task-required controls; the protected base source was never displayed or examined. Exceptions were caught without tracebacks, so traceback source lines could not leak protected implementation.

```json
[
  {
    "mutation": "unaltered_positive",
    "accepted": true,
    "exception": null,
    "captured_output_sha256_unread": "5db988c7d81a2341271f7634a1d5efdd3d17350c35067490b79cdd1769355f82",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/unaltered_positive"
  },
  {
    "mutation": "old_always_middle",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "execution slot changed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/old_always_middle"
  },
  {
    "mutation": "wrong_k",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "independent recovered-log certificate failed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/wrong_k"
  },
  {
    "mutation": "target_digest",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "target stream changed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/target_digest"
  },
  {
    "mutation": "config_digest",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "workload changed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/config_digest"
  },
  {
    "mutation": "missing_row",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "treatment is not crossed with all execution slots"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/missing_row"
  },
  {
    "mutation": "wrong_affinity",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "worker CPU affinity changed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/wrong_affinity"
  },
  {
    "mutation": "missing_affinity",
    "accepted": false,
    "exception": {
      "type": "KeyError",
      "message": "'worker_affinity'"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/missing_affinity"
  },
  {
    "mutation": "wrong_environment",
    "accepted": false,
    "exception": {
      "type": "ValueError",
      "message": "worker dependency/environment changed"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/wrong_environment"
  },
  {
    "mutation": "missing_load",
    "accepted": false,
    "exception": {
      "type": "KeyError",
      "message": "'load_before'"
    },
    "captured_output_sha256_unread": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "scratch_directory": "/tmp/ic-review-6562b0-jbmb5ah6/missing_load"
  }
]
```

Known-false strict advantage:

```json
{
  "mutation": "candidate_time_equals_reference_mean",
  "independent_speedup": 1.0,
  "independent_interval": [
    1.0,
    1.0
  ],
  "independent_gate": false,
  "actual_checker_strict_gate": false
}
```

## Custody, percentile convention and heterogeneity

After saving my raw-only result, I read the explicitly permitted prior independent audit and its arithmetic derivation. Its empirical convention uses zero-based indices124 and4875. Applying those indices to the already independently generated bootstrap yields the interval below. The new frozen statement says empirical percentiles without an explicit rounding convention, so the initial section exposes the small upper-endpoint convention difference rather than silently replacing it. All conventions leave the same numerical gate.

All source/config digests match the frozen plan, the runtime source hashes and the published HEAD. Protected source/validation/check-summary bytes were consumed only by opaque hash comparison, never displayed, parsed or interpreted. Runtime metadata and exact raw rows were examined. Source hash997602d5... matches the previously audited unchanged base worker. Pre-dispatch GitRepositoryVerifier acceptance is coordinator-supplied custody context, not independently rerun here.

```json
{
  "source_hashes_match": 20,
  "input_hashes_match": 2,
  "receipt_artifact_hashes_match": 13,
  "snapshot_heldout_files_equal_head": 12,
  "base_source_opaque_sha256": "997602d584b3425461d3486c192a106813139722de70c99844309737757d2ddd",
  "recipe_historical_empirical_indices": [
    124,
    4875
  ],
  "interval_same_indices_as_prior_independent_recipe": [
    1.1267519846188838,
    1.1976609119818378
  ],
  "pairs_slower_than_reference_mean": 5,
  "per_solver_seed_geomean": {
    "0": 1.1191720823916607,
    "1": 1.2035248469381679
  },
  "per_repetition_geomean": {
    "0": 1.1801829285691063,
    "1": 1.1583105993789575,
    "2": 1.1435457251592789
  },
  "by_arm_slot_geomean_seconds": {
    "reference_a": {
      "0": 0.016597625191290825,
      "1": 0.01649157674889799,
      "2": 0.016589979212078106
    },
    "fixed_window": {
      "0": 0.014178005683473643,
      "1": 0.01375695730487237,
      "2": 0.014087214694589624
    },
    "reference_b": {
      "0": 0.015803828461522767,
      "1": 0.015562635879488905,
      "2": 0.016217871456240325
    }
  },
  "census": {
    "environment_before": {
      "load_average": [
        0.0,
        0.015625,
        0.0
      ],
      "process_count": 508,
      "names_counts": {
        "tail": 1,
        "git": 496,
        "dockerd": 1,
        "codex-linux-san": 1,
        "bwrap": 1,
        "codex": 2,
        "bash": 1,
        "python": 2,
        "containerd": 1,
        "cloud-agent-log": 1,
        "caas-prefix-tra": 1
      }
    },
    "environment_after": {
      "load_average": [
        0.55078125,
        0.15673828125,
        0.04833984375
      ],
      "process_count": 508,
      "names_counts": {
        "tail": 1,
        "git": 496,
        "dockerd": 1,
        "codex-linux-san": 1,
        "bwrap": 1,
        "codex": 2,
        "bash": 1,
        "python": 2,
        "containerd": 1,
        "cloud-agent-log": 1,
        "caas-prefix-tra": 1
      }
    }
  },
  "harness_seconds": 40.32456387300044,
  "driver_seconds": 40.642481,
  "supervisor_envelope_seconds": 41.215345
}
```

## Reproduction of the blind timing calculation

The following directly implements the initial raw-only calculation. The original
result and54-pair table above were saved before successor source or historical
report reads. The final line adds the later disclosed historical endpoint
convention without changing the bootstrap samples.

```python
import collections, json, math, random, statistics
from pathlib import Path
raw = json.loads(Path("experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af/raw-result.json").read_text())
pairs = collections.defaultdict(dict)
for row in raw["rows"]:
    key = tuple(row[k] for k in ("bits", "curve_seed", "solver_seed", "repetition"))
    pairs[key][row["arm"]] = row["seconds_full_solve"]
assert len(pairs) == 54 and len(raw["rows"]) == 162
logs = {}
aa = []
for key, times in sorted(pairs.items()):
    a, b, c = [times[k] for k in ("reference_a", "reference_b", "fixed_window")]
    logs[key] = math.log((a + b) / (2 * c))
    aa.append(math.log(a / b))
point = math.exp(statistics.mean(logs.values()))
aa_signed = math.exp(statistics.mean(aa))
aa_factor = max(aa_signed, 1 / aa_signed)
clusters = {(b, c): [v for (bb, cc, seed, rep), v in sorted(logs.items())
                      if (bb, cc) == (b, c)]
            for b in (12, 14, 16) for c in (3, 4, 5)}
rng = random.Random(3065)
bootstrap = []
for _ in range(5000):
    sampled = []
    for bits in (12, 14, 16):
        for _ in range(3):
            sampled.extend(clusters[bits, rng.choice((3, 4, 5))])
    assert len(sampled) == 54
    bootstrap.append(math.exp(statistics.mean(sampled)))
bootstrap.sort()
print(point, aa_factor, bootstrap[124], bootstrap[4874])
print("Historical empirical-index convention:", bootstrap[124], bootstrap[4875])
```

The actual checker controls call
`tools.ic_target_balanced_benchmark.check_directory(scratch_directory)` after
writing synchronized raw-result.json, arms.jsonl and instances.json copies.
The control names above specify each mutation exactly: force orders A0/C1/B2;
change first recovered k by+1; set first target digest or raw config digest to64
zeroes; remove the last row; change first affinity to[1] or remove it; replace
first row environment digest with64 zeroes; remove first load_before. The clean
copy must return; each tampered copy must raise the recorded exception. Stdout
is redirected to an uninspected StringIO and only hashed, and exceptions are
caught without source-bearing tracebacks. For identical timings, replace each
candidate time by(A+B)/2, establish all54 independent ratios exactly1, and query
only `driver.base.summarize(copy)["protocol_criterion_met"]` inside
`driver.successor_config()`; its observed value was false.

## Review outcome and limits

J-integrity **holds** and J-inference **holds** at the observed exact toy scope.
The main reported interval uses the already published independent empirical
recipe[124,4875], giving[1.1267519846188838,1.1976609119818378]; the blind
floor-index result and the rounding ambiguity remain visible above.

One AMD EPYC9V74 host, one session, nine curves (three per size), m2/small_x/
mitm, acceleration false, harvest off, window4, solver seeds0/1, three
repetitions are the measured scope. The54 pairs are not54 independently
sampled curves. The estimate is conditional on these curves, the native solve
instrumentation and this machine; five pairs regress. Root Coordinator reports
no known competing scientific producer during17:06:26–17:07:07UTC and only the
approved successor supervisor in that window. This is supplied orchestration
context; pre/post visible process snapshots and smoothed loads cannot establish
host-wide isolation or rule out transient/invisible activity. Source/receipt
hashing and finite certificates do not constitute an execution proof.

Complete-solve setup and final verification are charged; the internal timer and
operation count exclude final verification and must not replace the full
measurements. Target setup is a subset, not an added phase. CPU, wall, group
counts, S3/LA counts, payload and RSS stay distinct; harness/driver/supervisor
envelopes overlap. No matched rho/Bernstein-Lange, production-curve,
asymptotic, frontier, default or attack-cost-bound conclusion follows.

Own YAML parsed. The exact-plan independence command returned exit0:
`PASS: 1 report(s), every joint owned and attested, blindness respected, controls declared`.
This checks declared composition, not actual identity, scientific correctness or
execution authenticity. Requested policy/effort are review-adversarial/xhigh;
no exact serving model is exposed, no probe/API call or diversity claim is made.
Only these two authorized review artifacts are written in the repository, with
no performance rerun, source/protocol/raw edit, commit or scientific transition.
