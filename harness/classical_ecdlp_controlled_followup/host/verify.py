#!/usr/bin/env python3
"""Host-only independent checker. Never import or stage this module on worker.

All labelled work is reachable through an explicit verified-custody capability.
No SDK, sampler, timing, feedback, scientific launcher or producer import exists.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
from functools import lru_cache
from math import comb, isqrt
from pathlib import Path
import hashlib
import json
import re

PREFIX = 'classical.ecdlp.controlled-followup.'
FILES = ('attempt-intents.jsonl', 'decoder-cells.jsonl', 'engine-completion.json',
         'engine-summary.json', 'setups.jsonl', 'single-points.jsonl', 'traces.jsonl')
CELLS = ((0,0),(0,2),(1,0),(1,2),(2,0),(2,2))
ARMS={f'circuit{c}.a{a}':{'id':f'circuit{c}.a{a}','alpha':alpha,'beta':beta,
      'base_multiplier':a,'kind':'candidate'}
      for c,(alpha,beta) in enumerate(((1,-4),(-2,-1)),1) for a in (1,2,3,5)}
Point = tuple[int,int] | None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def tree_digest(entries):
    """Digest of canonical list of {path,sha256,size}, sorted by relative path."""
    return digest(canonical(sorted(entries, key=lambda x: x['path'])))


@dataclass(frozen=True)
class SealedInput:
    files: dict[str, Path]
    digest: str
    evidence: dict
    max_line_bytes: int = 64 << 20


def open_sealed(root, evidence, max_line_bytes=64 << 20):
    """Validate transport assertions and ALL collected bytes before parsing labels.

    Caller must authenticate the transport-owned evidence independently. Boolean
    fields are assertions, not a process-isolation proof. Symlinks, extra files,
    path traversal, missing bytes and mismatched hashes are rejected.
    """
    require(type(max_line_bytes) is int and 0 < max_line_bytes <= 64 << 20, 'JSON line byte cap')
    require(evidence.get('schema') == PREFIX+'host-custody/v1', 'custody schema')
    require(evidence.get('collection_complete') is True, 'incomplete collection')
    require(evidence.get('uid1000_quiescent') is True, 'UID1000 not quiescent')
    ack = evidence.get('termination_ack', {})
    require(ack.get('acknowledged') is True and ack.get('uid') == 1000,
            'missing termination ACK')
    require(type(ack.get('transport_id')) is str and bool(ack['transport_id']),
            'missing authenticated transport reference')
    require(evidence.get('sealed') is True, 'not sealed')
    rows = evidence.get('files')
    require(type(rows) is list and rows, 'missing sealed file manifest')
    names = [x.get('path') for x in rows]
    require(len(set(names)) == len(names), 'duplicate sealed path')
    require(set(names) == set(FILES), 'unexpected or missing engine files')
    require(tree_digest(rows) == evidence.get('tree_sha256'), 'sealed tree mismatch')
    root = Path(root)
    require(not root.is_symlink() and root.is_dir(), 'invalid collection root')
    require(all(not x.is_symlink() for x in root.rglob('*')),'collection symlink forbidden')
    actual = {x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    require(actual == set(names), 'collection file set mismatch')
    files = {}
    for row in rows:
        name = row['path']
        require(type(name) is str and '/' not in name and name not in ('.','..'), 'unsafe path')
        file = root/name
        require(not file.is_symlink(), 'symlink forbidden')
        require(type(row.get('size')) is int and file.stat().st_size == row['size'], 'size mismatch')
        h=hashlib.sha256()
        with file.open('rb') as source:
            for chunk in iter(lambda:source.read(1048576),b''):h.update(chunk)
        require(h.hexdigest() == row.get('sha256'), 'file digest mismatch')
        files[name] = file
    return SealedInput(files, evidence['tree_sha256'], evidence, max_line_bytes)


def prime(n):
    if type(n) is not int or not 2 <= n < 2**64:
        return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % q == 0:
            return n == q
    d, s = n-1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2,325,9375,28178,450775,9780504,1795265022):
        if a % n == 0:
            continue
        v = pow(a,d,n)
        if v in (1,n-1):
            continue
        for _ in range(s-1):
            v = v*v % n
            if v == n-1:
                break
        else:
            return False
    return True


def point(value, p):
    require(value is None or (type(value) in (list,tuple) and len(value)==2 and
        all(type(c) is int and 0<=c<p for c in value)), 'noncanonical point')
    return None if value is None else tuple(value)


class Group:
    """Independent affine group with separately disclosed host abstract counts."""
    def __init__(self, model):
        self.p,self.a,self.b,self.r = (model[k] for k in ('p','a','b','r'))
        p,r = self.p,self.r
        require(prime(p) and p>3 and p%4==3, 'field domain')
        require(prime(r) and r>2 and r!=p, 'order domain')
        require(type(self.a) is int and 0<=self.a<p and type(self.b) is int and 0<=self.b<p,
                'coefficient domain')
        require((4*self.a**3+27*self.b**2)%p != 0, 'singular curve')
        self.counts = Counter()

    def member(self, P):
        self.counts['point_equation'] += 1
        if P is not None:self.counts.update(field_square=2,field_mul=2,field_sub=3)
        return P is None or (0<=P[0]<self.p and 0<=P[1]<self.p and
            (P[1]**2-P[0]**3-self.a*P[0]-self.b)%self.p==0)

    def neg(self,P):
        self.counts['group_negation'] += 1
        if P is not None:self.counts['field_negation']+=1
        return None if P is None else (P[0],-P[1]%self.p)

    def slope(self,P,Q):
        self.counts['slope_call'] += 1
        if P is None or Q is None or (P[0]==Q[0] and (P[1]+Q[1])%self.p==0):
            return 0
        self.counts.update(field_square=1,field_mul=2,field_add=1) if P==Q else self.counts.update(field_sub=2)
        num,den = ((3*P[0]*P[0]+self.a,2*P[1]) if P==Q else (Q[1]-P[1],Q[0]-P[0]))
        self.counts['field_mul']+=1
        self.counts['field_inverse'] += 1
        return num*pow(den,-1,self.p)%self.p

    def add(self,P,Q):
        self.counts['group_add_call'] += 1
        if P is None: return Q
        if Q is None: return P
        if P[0]==Q[0] and (P[1]+Q[1])%self.p==0: return None
        z = self.slope(P,Q)
        self.counts.update(field_square=1,field_sub=4,field_mul=1)
        x = (z*z-P[0]-Q[0])%self.p
        return x,(z*(P[0]-x)-P[1])%self.p

    def mul(self,n,P):
        require(type(n) is int, 'integer scalar')
        self.counts['scalar_multiply_call'] += 1
        if n<0: return self.mul(-n,self.neg(P))
        acc = None
        for b in bin(n)[2:]:
            self.counts['scalar_bit']+=1
            acc = self.add(acc,acc)
            if b=='1': acc = self.add(acc,P)
        return acc

    def certify(self,P):
        require(P is not None and self.member(P) and self.mul(self.r,P) is None, 'base/order')
        h=isqrt(4*self.p)
        lo,hi=self.p+1-h,self.p+1+h
        require((lo+self.r-1)//self.r == hi//self.r == 1, 'full order not certified by Hasse')
        require((self.p+1-self.r)%self.p != 0, 'ordinary required')

    def orbit(self,P):
        self.certify(P)
        out,current=[None],None
        for _ in range(1,self.r):
            current=self.add(current,P)
            out.append(current)
        require(len(set(out))==self.r and self.add(current,P) is None,'bad orbit')
        self.counts['orbit_stored_points'] += len(out)
        return out


def need_seal(seal):
    require(isinstance(seal,SealedInput),'verified post-termination seal required')


class Oracle:
    """Cumulative P addition derives Z; unlike producer binary seed/transport.

    Shares only stipulated slope-cocycle identity. Full orbit is paid host work.
    """
    def __init__(self,seal,model,base):
        need_seal(seal)
        self.group=Group(model)
        self.base=point(base,self.group.p)
        self.points=self.group.orbit(self.base)
        self.logs={P:k for k,P in enumerate(self.points)}
        p,r=self.group.p,self.group.r
        self.group.counts.update(oracle_order_inverse=1,oracle_field_inverse=1)
        defects=[0]
        for k in range(r):
            self.group.counts['oracle_field_add']+=1
            defects.append((defects[-1]+self.group.slope(self.points[k],self.base))%p)
        zp=-defects[r]*pow(r,-1,p)%p
        self.z={P:(k*zp+defects[k])%p for k,P in enumerate(self.points)}
        self.group.counts.update(oracle_field_mul=r+1,oracle_field_add=r,oracle_stored_values=r,oracle_log_entries=r)
        require(self.z[None]==0,'Z identity')

    def slope_sum_check(self):
        """Independent sum-over-group construction, charged all-r diagnostic."""
        g=self.group
        for R in self.points:
            z=-sum(g.slope(R,T) for T in self.points)*pow(g.r,-1,g.p)%g.p
            require(z==self.z[R],'slope-sum oracle mismatch')

    def evaluate(self,R,alpha,beta,a):
        g=self.group
        B=g.mul(a,self.base)
        require(B is not None and R in self.z,'predicate membership/base')
        if R is None: return {'status':'BIT0','reason':'identity','bit':0}
        zp=self.z[B]
        c=zp*pow(B[1],-1,g.p)%g.p
        anchor=(1+alpha)*zp%g.p
        if not zp or not c or not anchor:
            return {'status':'UNDEFINED','reason':'setup','bit':None}
        raw=(self.z[R]+c*R[1]*(alpha+beta*c*(R[0]-B[0])))%g.p
        if not raw: return {'status':'UNDEFINED','reason':'numerator','bit':None}
        normalized=raw*pow(anchor,-1,g.p)%g.p
        chi=pow(normalized,(g.p-1)//2,g.p)
        bit=0 if chi==1 else 1
        return {'status':'BIT'+str(bit),'reason':'defined','bit':bit,
                'z':self.z[R],'raw':raw,'normalized':normalized}


def words(bits,radius):
    require(type(radius) is int and radius>=0,'radius')
    require(all(type(b) is int and b in (0,1) or b is None for b in bits),'bits')
    erased=[i for i,b in enumerate(bits) if b is None]
    defined=[i for i,b in enumerate(bits) if b is not None]
    # Published data contract: assignment outermost, then distance/flips.
    for assignment in product((0,1),repeat=len(erased)):
        for distance in range(min(radius,len(defined))+1):
            for flips in combinations(defined,distance):
                v=list(bits)
                for i in flips: v[i]^=1
                for i,b in zip(erased,assignment): v[i]=b
                yield sum(b<<(len(v)-1-i) for i,b in enumerate(v))


def interval(r,L,V):
    D=1<<L
    k=(r*V+D-1)//D
    return k if 0<=k<r and D*k<r*(V+1) else None


def decode(g,G,Q,a,b,bits,radius,cap):
    require(0<a<g.r and 0<b<g.r,'nonzero a,b')
    e=bits.count(None)
    out={'erasures':e,'radius':radius,'erasure_cap':cap,'words':[], 'legal':[],
         'verified':[],'M':0,'zero_checked':0,'status':'capped' if e>cap else 'complete',
         'host_counts':{},'expected_word_count':0}
    if e>cap: return out
    B,T=g.mul(a,G),g.mul(b,Q)
    inv=pow(b,-1,g.r)
    counts=Counter({'scalar_inverse':1,'point_preparation':2})
    out['expected_word_count']=(1<<e)*sum(comb(len(bits)-e,j) for j in range(min(radius,len(bits)-e)+1))
    nonzero=set()
    for V in words(bits,radius):
        counts['word']+=1
        k=interval(g.r,len(bits),V)
        row={'word':V,'k':k}
        if k is None:
            counts['empty_interval']+=1
        else:
            x=a*inv*k%g.r
            counts['scalar_conversion']+=1
            ok1=g.mul(k,B)==T
            ok2=g.mul(x,G)==Q # no short circuit: both checks always paid
            counts['public_equations']+=2
            row.update(x=x,transformed_ok=ok1,original_ok=ok2)
            out['legal'].append(x)
            if x: nonzero.add(x)
            else: out['zero_checked']+=1
            if ok1 and ok2: out['verified'].append(x)
        out['words'].append(row)
    out['M']=len(nonzero)
    out['host_counts']=dict(counts)
    require(len(out['words'])==out['expected_word_count'],'enumeration count')
    return out


def geometry(oracle,Q,a,b,bits):
    r=oracle.group.r
    require(Q in oracle.logs and Q is not None,'target subgroup')
    s=oracle.logs[Q]*b*pow(a,-1,r)%r
    truth=[int((s*pow(2,i,r)%r)>r//2) for i in range(len(bits))]
    errors=[i for i,(v,t) in enumerate(zip(bits,truth)) if v is not None and v!=t]
    erasures=[i for i,v in enumerate(bits) if v is None]
    return {'s':s,'truth':truth,'errors':errors,'erasures':erasures,
            'truth_word':sum(v<<(len(bits)-i-1) for i,v in enumerate(truth))}


def exact_ids(rows,key,expected):
    found=[row[key] for row in rows]
    require(len(found)==len(set(found)),'duplicate '+key)
    require(set(found)==set(expected),'schedule mismatch '+key)


def validate_counter_vector(value):
    require(type(value) is dict,'counter object')
    def walk(x):
        if type(x) is dict:
            for v in x.values(): walk(v)
        else:
            require(type(x) is int and x>=0,'nonnegative integer counter')
    walk(value)
    return value # preserve exact vector; no claim of replay


def check_cell(g,G,Q,a,b,bits,reported):
    wanted=decode(g,G,Q,a,b,bits,reported['radius'],reported['erasure_cap'])
    for key in ('status','M','zero_checked','expected_word_count','words','legal','verified'):
        require(reported.get(key)==wanted[key], 'cell mismatch '+key)
    return wanted


def strict_loads(raw, limit):
    require(type(raw) is bytes and len(raw)<=limit, 'bounded JSON required')
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result, 'duplicate JSON key: '+key)
            result[key]=value
        return result
    def nonfinite(value):
        raise ValueError('nonfinite JSON')
    result=json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)
    # JSON exponent overflow (1e999) also produces an IEEE infinity.
    def finite(value):
        if type(value) is float:
            from math import isfinite
            require(isfinite(value),'nonfinite JSON')
        elif type(value) is dict:
            for child in value.values():finite(child)
        elif type(value) is list:
            for child in value:finite(child)
    finite(result)
    return result


def read_json(path, limit):
    require(path.stat().st_size<=limit,'bounded JSON required')
    with path.open('rb') as source:
        return strict_loads(source.read(limit+1),limit)


def iter_records(seal,name):
    need_seal(seal)
    with seal.files[name].open('rb') as source:
        while True:
            raw=source.readline(seal.max_line_bytes+1)
            if not raw:break
            require(len(raw)<=seal.max_line_bytes,'JSONL line byte cap')
            require(raw.endswith(b'\n'),'partial final JSONL row')
            require(bool(raw.strip()),'blank JSONL row')
            yield strict_loads(raw,seal.max_line_bytes)


@lru_cache(maxsize=32)
def compiled_validator(schema_bytes):
    """Compile each exact schema once; keep jsonschema.validate's chosen draft."""
    import jsonschema
    schema=strict_loads(schema_bytes,64<<20)
    cls=jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    return cls(schema)


def public_curve_identity(model,bits,excluded):
    """Check a retained model's tier and global exclusion key without labels."""
    p,a,b,r=(model[k] for k in ('p','a','b','r'))
    require(all(type(x) is int for x in (p,a,b,r)) and r.bit_length()==bits,'actual production r tier')
    require((1<<(bits-1))<=p<(1<<(bits+1)) and prime(p) and p%4==3 and 0<=a<p and 0<=b<p,'production field range')
    den=(4*a**3+27*b*b)%p
    require(den!=0 and prime(r) and r!=p and (p+1-r)%p!=0,'production ordinary prime order domain')
    ident=(p,1728*4*a**3*pow(den,-1,p)%p)
    require(ident not in excluded,'production duplicate/excluded (p,j)')
    return ident


def frozen_schedule(cohort, authenticated_inputs):
    """Host-owned law; no import of cohort/worker planning or worker authority.

    The caller authenticates static inputs before calling. A fixture law is an
    explicit invocation capability, never inferred from labels or worker plan.
    """
    require(type(authenticated_inputs) is dict,'independently authenticated workload law required')
    law=authenticated_inputs.get('workload_law')
    curves=cohort['curves']
    setups={};singles={};traces={};paired=set()
    def setup(cid,arm):setups[cid+'/'+arm]={'curve_id':cid,'arm_id':arm}
    def single(cid,arm,ident):singles[ident]={'curve_id':cid,'arm_id':arm}
    def trace(cid,arm,ident,target_id=None,target=None):
        traces[ident]={'curve_id':cid,'arm_id':arm}
        if target_id is not None:traces[ident].update(target_id=target_id,target=target)
    if law in ('fixed-F11-calibration/v1','fixed-F23-calibration/v1'):
        name=law.split('-')[1]
        model,base=({'p':11,'a':1,'b':6,'r':13},[2,7]) if name=='F11' else ({'p':23,'a':11,'b':5,'r':17},[5,22])
        cid='fixture-'+name
        # Q=[7]P is the disclosed deterministic known-answer target.
        require(len(curves)==1 and curves[0]['curve_id']==cid,'fixed fixture curve ID')
        require(curves[0]['model']==model and curves[0]['base']==base,'fixed fixture model/base')
        target=[7,2] if name=='F11' else [15,7]
        require(curves[0]['targets']==[{'target_id':'target7','point':target}],'fixed fixture public target')
        arm='circuit1.a5'
        setup(cid,arm);single(cid,arm,cid+'/single0000/'+arm)
        setups[cid+'/'+arm].update(model=model,base=base,arm=ARMS[arm])
        singles[cid+'/single0000/'+arm]['point']=target
        trace(cid,arm,cid+'/target7/rep0','target7',target)
        traces[cid+'/target7/rep0']['target_multiplier']=1
        expected={'setups':1,'singles':1,'traces':1,'intents':1,'cells':0}
        return {'setup_ids':setups,'single_ids':singles,'trace_ids':traces,'paired_trace_ids':paired,'expected':expected}
    require(law=='production/v1','unknown workload law')
    schedule=production_schedule()
    slots=schedule.pop('slots')
    require(len(curves)==48 and {c['curve_id'] for c in curves}==set(slots),'exact 48 production slots')
    exclusions=authenticated_inputs.get('prior_exclusions',{}).get('excluded_p_j')
    require(type(exclusions) is list and all(type(x) is list and len(x)==2 and all(type(v) is int and v>=0 for v in x) for x in exclusions),'frozen exposed exclusions required')
    excluded={tuple(x) for x in exclusions}
    require(len(excluded)==len(exclusions),'duplicate frozen exclusions')
    for curve in curves:
        cid=curve['curve_id'];stage,bits=slots[cid];model=curve['model']
        excluded.add(public_curve_identity(model,bits,excluded))
        targets=curve['targets']
        if stage in ('discovery','validation'):
            require(targets==[],'calibration public targets must be empty')
        else:
            require(len(targets)==64 and [t['target_id'] for t in targets]==[f'target{i:04d}' for i in range(64)],'exact production targets/IDs')
            require(all(type(t['point']) is list and len(t['point'])==2 for t in targets),'public target coordinates')
            require(len({tuple(t['point']) for t in targets})==64,'unique production public targets')
            for t in targets:
                for rep in range(8):schedule['trace_ids'][f"{cid}/{t['target_id']}/rep{rep}"]['target']=t['point']
        for arm in (ARMS if stage in ('discovery','validation') else ('circuit2.a1',)):
            schedule['setup_ids'][cid+'/'+arm].update(model=model,base=curve['base'],arm=ARMS[arm])
    schedule.pop('physical_calls')
    return schedule


def production_schedule():
    """Pure no-draw host construction, independent of all worker plan outputs."""
    slots={f'{stage}-{bits}-{index}':(stage,bits)
           for stage in ('discovery','validation','confirmation-A','confirmation-B')
           for bits in (10,13,16) for index in range(4)}
    setups={};singles={};traces={};paired=set();physical_calls=0
    for cid,(stage,bits) in slots.items():
        if stage in ('discovery','validation'):
            for arm in ARMS:
                metadata={'curve_id':cid,'arm_id':arm}
                setups[cid+'/'+arm]=dict(metadata)
                for i in range(1800):singles[f'{cid}/single{i:04d}/{arm}']=dict(metadata)
                for i in range(128):traces[f'{cid}/trace{i:04d}/{arm}']={**metadata,'target_id':None}
            physical_calls+=1800*8+128*8*(bits+1)
        else:
            metadata={'curve_id':cid,'arm_id':'circuit2.a1'}
            setups[cid+'/circuit2.a1']=dict(metadata)
            for i in range(64):
                target=f'target{i:04d}'
                for rep in range(8):
                    ident=f'{cid}/{target}/rep{rep}'
                    traces[ident]={**metadata,'target_id':target};paired.add(ident)
            physical_calls+=64*8*2*(bits+1)
    expected={'setups':216,'singles':345600,'traces':36864,'intents':36864,'cells':73728}
    require(physical_calls==1033728 and len(singles)+len(traces)==382464,'host frozen construction counts')
    require(len(setups)==216 and len(singles)==345600 and len(traces)==36864 and len(paired)==12288,'host schedule counts')
    return {'slots':slots,'setup_ids':setups,'single_ids':singles,'trace_ids':traces,
            'paired_trace_ids':paired,'expected':expected,'physical_calls':physical_calls}


def preflight_records(seal, schedule, check):
    """Validate every retained syntax/schema/ID before constructing a label oracle."""
    for filename,kind,key,ids in [('setups.jsonl','setup',None,'setup_ids'),
        ('single-points.jsonl','single-point','single_id','single_ids'),
        ('traces.jsonl','trace','trace_id','trace_ids'),
        ('attempt-intents.jsonl','intent','trace_id','trace_ids')]:
        seen=set()
        for row in iter_records(seal,filename):
            check(kind,row)
            ident=row['curve_id']+'/'+row['arm_id'] if key is None else row[key]
            require(ident not in seen and ident in schedule[ids],'independent schedule '+kind)
            seen.add(ident)
            want=schedule[ids][ident]
            require(all(row[k]==v for k,v in want.items()),'frozen row metadata '+kind)
            if kind=='trace':require((row['incremental'] is not None)==(ident in schedule['paired_trace_ids']),'independent paired schedule')
            if kind in ('trace','intent'):
                require(row['base_multiplier']==ARMS[row['arm_id']]['base_multiplier'],'frozen base multiplier')
        require(seen==set(schedule[ids]),'independent complete '+kind+' schedule')
    seen=set()
    for row in iter_records(seal,'decoder-cells.jsonl'):
        check('decoder-cell',row)
        ident=row['cell_id'];trace=row['trace_id'];cell=(row['radius'],row['erasure_cap'])
        require(trace in schedule['paired_trace_ids'] and cell in CELLS,'independent six-cell schedule')
        require(ident==trace+f'/t{cell[0]}.e{cell[1]}' and ident not in seen,'independent cell ID')
        seen.add(ident)
    require(len(seen)==schedule['expected']['cells'],'independent complete cell schedule')


def engine_answer(oracle,R,arm):
    g=oracle.group
    B=g.mul(arm['base_multiplier'],oracle.base)
    zp=oracle.z[B]
    anchor=(1+arm['alpha'])*zp%g.p
    result={'anchor':anchor,'bit':None,'g':None,'normalized':None,
            'reason':None,'status':'UNDEFINED','z':None}
    if B[1]==0:result.update(reason='ZERO_BASE_Y',anchor=None);return result
    if zp==0:result.update(reason='ZERO_BASE_Z',anchor=None);return result
    if anchor==0:result['reason']='ZERO_ANCHOR';return result
    if R is None:
        result.update(status='BIT',bit=0,z=0,g=None,normalized=None)
        return result
    result['z']=oracle.z[R]
    c=zp*pow(B[1],-1,g.p)%g.p
    raw=(oracle.z[R]+c*R[1]*(arm['alpha']+arm['beta']*c*(R[0]-B[0])))%g.p
    result['g']=raw
    if raw==0:result['reason']='ZERO_NUMERATOR';return result
    normalized=raw*pow(anchor,-1,g.p)%g.p
    result.update(status='BIT',bit=int(pow(normalized,(g.p-1)//2,g.p)!=1),normalized=normalized)
    return result


def check_engine_cell(oracle,trace,bits,row):
    g=oracle.group
    G=oracle.base
    Q=point(trace['target'],g.p)
    radius,cap=row['radius'],row['erasure_cap']
    require((radius,cap) in CELLS,'unregistered cell')
    require(row['cell_id']==trace['trace_id']+f'/t{radius}.e{cap}','cell ID')
    require(row['trace_id']==trace['trace_id'],'cell trace ID')
    expected=decode(g,G,Q,trace['base_multiplier'],trace['target_multiplier'],bits,radius,cap)
    require(row['L']==len(bits) and row['erasures']==bits.count(None),'cell geometry')
    require(row['capped']==(expected['status']=='capped'),'cell cap')
    require(row['M']==expected['M'] and row['zero_candidate_checks']==expected['zero_checked'],'cell nonzero M')
    require(row['word_count']==len(expected['words']) and row['expected_word_count']==expected['expected_word_count'],'word counts')
    require(row['distinct_nonzero_candidates']==sorted(set(x for x in expected['legal'] if x)),'distinct candidates')
    require(row['recovered_scalars']==sorted(set(expected['verified'])),'recovered set')
    require(row['scalar']==(min(expected['verified']) if expected['verified'] else None),'cell scalar')
    require(len(row['words'])==len(expected['words']),'list truncation')
    for got,want in zip(row['words'],expected['words']):
        V=want['word'];D=1<<len(bits);rawk=(g.r*V+D-1)//D
        wordbits=[(V>>(len(bits)-i-1))&1 for i in range(len(bits))]
        require(got['value']==V and got['bits']==wordbits,'word order/value')
        require(got['flipped_indices']==[i for i,b in enumerate(bits) if b is not None and b!=wordbits[i]],'flip geometry')
        require(got['erasure_assignment']==[wordbits[i] for i,b in enumerate(bits) if b is None],'erasure assignment')
        legal=want['k'] is not None
        require(got['legal']==legal and got['candidate_scalar_prime']==rawk,'strict interval')
        require(got['candidate_scalar']==want.get('x'),'conversion')
        checks={'original':want.get('original_ok'),'transformed':want.get('transformed_ok')}
        require(got['public_checks']==checks,'both public equations')
        status=('EMPTY_INTERVAL' if not legal else 'RECOVERED' if all(checks.values()) else 'REJECTED_FINAL_VERIFICATION')
        require(got['status']==status,'word status')
    if expected['status']=='capped':
        status='UNDEFINED' if radius==0 and cap==0 else 'CAPPED_ERASURES'
    elif expected['verified']:status='RECOVERED'
    elif not expected['legal']:status='EMPTY_INTERVAL'
    else:status='REJECTED_FINAL_VERIFICATION'
    require(row['status']==status,'cell status')
    validate_counter_vector(row['counts'])
    return expected


def check_engine_trace(oracle,arm,row):
    g=oracle.group
    a,b=row['base_multiplier'],row['target_multiplier']
    require(a==arm['base_multiplier'] and 0<a<g.r and 0<b<g.r,'trace multipliers')
    Q=point(row['target'],g.p)
    require(Q in oracle.logs and Q is not None,'trace target membership')
    L=g.r.bit_length()+1
    bits=[]
    for mode in ('original','incremental'):
        proc=row[mode]
        if proc is None:
            require(mode=='incremental','missing original')
            continue
        require(proc['L']==L and proc['predicate_evaluations']==L,'all L queries required')
        require(proc['retained_bit_reads']==0,'no label-based candidate digit read')
        require(len(proc['predicate_trace'])==L,'trace truncation')
        require(proc['target_multiplier_inverse']==pow(b,-1,g.r),'inverse conversion')
        R=g.mul(b,Q)
        modebits=[]
        for i,query in enumerate(proc['predicate_trace']):
            require(query['index']==i and point(query['target'],g.p)==R,'query schedule')
            require(query['answer']==engine_answer(oracle,R,arm),'predicate answer')
            validate_counter_vector(query['counters'])
            modebits.append(query['answer']['bit'])
            R=g.add(R,R)
        validate_counter_vector(proc['counts'])
        if mode=='original':bits=modebits
        else:require(bits==modebits,'original/incremental bits')
        strict=decode(g,oracle.base,Q,a,b,modebits,0,0)
        if None in modebits:
            require(proc['status']=='UNDEFINED','undefined attempt retained')
            require(all(proc[k] is None for k in ('candidate_scalar','candidate_scalar_prime','scalar','scalar_prime')),'undefined scalars')
            require(proc['public_checks']=={'transformed':None,'original':None},'undefined checks')
            require(proc['interval']=={'denominator':1<<L,'lower_numerator':None,'upper_numerator':None,'value':None,'nonempty':False},'undefined interval')
            reasons=sorted(set(q['answer']['reason'] for q in proc['predicate_trace'] if q['answer']['reason'] is not None))
            require(proc['reason']==','.join(reasons),'undefined reasons')
        else:
            V=next(words(modebits,0));k=(g.r*V+(1<<L)-1)//(1<<L)
            x=a*pow(b,-1,g.r)*k%g.r
            require(proc['candidate_scalar_prime']==k,'attempt k')
            require(proc['candidate_scalar']==(x if interval(g.r,L,V) is not None else None),'attempt converted scalar')
            interval_data={'denominator':1<<L,'lower_numerator':g.r*V,
                'upper_numerator':g.r*(V+1),'value':V,'nonempty':interval(g.r,L,V) is not None}
            require(proc['interval']==interval_data,'attempt interval')
            if interval_data['nonempty']:
                checks={'transformed':g.mul(k,g.mul(a,oracle.base))==g.mul(b,Q), 'original':g.mul(x,oracle.base)==Q}
                require(proc['public_checks']==checks,'attempt public equations')
                status='RECOVERED' if all(checks.values()) else 'REJECTED_FINAL_VERIFICATION'
            else:
                status='EMPTY_INTERVAL'
                require(proc['public_checks']=={'original':None,'transformed':None},'empty attempt checks')
            require(proc['status']==status,'attempt status')
            expected_reason={'RECOVERED':None,'EMPTY_INTERVAL':'EMPTY_BINARY_INTERVAL','REJECTED_FINAL_VERIFICATION':'FINAL_VERIFICATION_FAILED'}[status]
            require(proc['reason']==expected_reason,'attempt reason')
            require(proc['scalar']==(x if strict['verified'] else None),'attempt scalar')
            require(proc['scalar_prime']==(k if strict['verified'] else None),'attempt recovered prime scalar')
    if row['incremental'] is not None:
        # Compare every semantic field; price vectors deliberately excluded.
        def semantics(proc):
            return {k:v for k,v in proc.items() if k not in ('counts','predicate_trace')}
        require(semantics(row['original'])==semantics(row['incremental']),'exact original/incremental semantics')
        require(row['equal'] is True,'paired equality flag')
    return bits,geometry(oracle,Q,a,b,bits)


def verify_bundle(root,evidence,plan,interface,emit=None,authenticated_inputs=None):
    """Streaming checker. Frozen plan contains exact scheduled row IDs and pins.

    emit receives host diagnostic rows; it must never feed the terminated worker.
    Original raw files and all their counters are retained as immutable inputs.
    Unknown/invalid rows raise; caller retains the exception and entire bundle.
    No function here launches or approves scientific work.
    """
    require(type(authenticated_inputs) is dict,'independently authenticated workload law required')
    max_line=authenticated_inputs.get('max_jsonl_line_bytes',64<<20)
    seal=open_sealed(root,evidence,max_line) # MUST precede any labelled arithmetic
    require(digest(canonical(interface))==plan['engine_interface_canonical_sha256'],'interface binding')
    cohort_raw=bytes.fromhex(plan['public_cohort_bytes_hex'])
    require(digest(cohort_raw)==plan['provenance']['cohort_sha256'],'public cohort bytes binding')
    cohort=strict_loads(cohort_raw,64<<20)
    require(set(cohort)=={'curves','nonce'},'public cohort allowlist')
    require(type(cohort['nonce']) is str and re.fullmatch('[0-9a-f]{64}',cohort['nonce']) is not None,'public nonce')
    for curve in cohort['curves']:
        require(set(curve)=={'curve_id','model','base','targets'},'public curve allowlist')
        require(set(curve['model'])=={'p','a','b','r'},'public model allowlist')
        require(all(set(t)=={'target_id','point'} for t in curve['targets']),'public target allowlist')
        require(len(set(t['target_id'] for t in curve['targets']))==len(curve['targets']),'duplicate public target IDs')
    public_curves={row['curve_id']:row for row in cohort['curves']}
    require(len(public_curves)==len(cohort['curves']),'duplicate cohort curve IDs')
    schemas=interface['record_schemas']
    validators={kind:compiled_validator(canonical(schema)) for kind,schema in schemas.items()}
    def check(kind,row):
        validators[kind].validate(row)
        require(row['schema']==PREFIX+kind+'/v1','record schema name')
        return row
    completion=check('completion',read_json(seal.files['engine-completion.json'],max_line))
    summary=check('summary',read_json(seal.files['engine-summary.json'],max_line))
    require(completion['provenance']==summary['provenance']==plan['provenance'],'source/protocol/cohort pins')
    require(completion['wall_valid'] is False and summary['wall_valid'] is False,'clock must remain unqualified')
    require(completion['termination_ack'] is False,'engine cannot assert transport ACK')
    counts=Counter()
    for name,item in completion['files'].items():
        require(name in seal.files and name!='engine-completion.json','completion file set')
        rawhash=next(x for x in evidence['files'] if x['path']==name)
        require(item['sha256']==rawhash['sha256'] and item['bytes']==rawhash['size'],'completion byte binding')
    require(set(completion['files'])==set(FILES)-{'engine-completion.json'},'completion coverage')
    schedule=frozen_schedule(cohort,authenticated_inputs)
    for key in ('setup_ids','single_ids','trace_ids','paired_trace_ids'):
        require(type(plan[key]) is list and len(plan[key])==len(set(plan[key])) and set(plan[key])==set(schedule[key]),'worker plan differs from independent '+key)
    require(plan['expected']==schedule['expected'],'worker expected differs from independent workload')
    require(summary['observed']==summary['expected']==schedule['expected'],'independent summary workload counts')
    require(completion['status']==summary['status']=='complete' and not summary['errors'],'operational incomplete: retain raw failures')
    for name,key in [('setups.jsonl','setups'),('single-points.jsonl','singles'),('traces.jsonl','traces'),('decoder-cells.jsonl','cells'),('attempt-intents.jsonl','intents')]:
        require(completion['files'][name]['records']==schedule['expected'][key],'independent completion record count')
    preflight_records(seal,schedule,check)
    # All subsequent expected IDs originate in the independent host law.
    plan={**plan,**{k:list(schedule[k]) for k in ('setup_ids','single_ids','trace_ids','paired_trace_ids')},'expected':schedule['expected']}
    setups={}
    oracles={}
    total_points=0
    for row in iter_records(seal,'setups.jsonl'):
        check('setup',row)
        require(row['arm_id'] in ARMS and row['arm']==ARMS[row['arm_id']],'fixed unfitted arm')
        key=row['curve_id']+'/'+row['arm_id']
        require(key not in setups,'duplicate setup')
        cid=row['curve_id']
        require(cid in public_curves,'setup not in public cohort')
        public=public_curves[cid]
        require(row['model']==public['model'] and row['base']==public['base'],'setup public cohort model/base')
        if cid not in oracles:
            total_points+=row['model']['r']
            require(total_points<=plan.get('max_total_orbit_points',1196032),'host orbit memory plan exceeded')
            oracle=Oracle(seal,row['model'],row['base'])
            targetpoints=[point(t['point'],oracle.group.p) for t in public['targets']]
            require(len(set(targetpoints))==len(targetpoints),'duplicate public target points')
            require(all(P is not None and P in oracle.logs for P in targetpoints),'public target subgroup')
            oracles[cid]=(row['model'],row['base'],oracle)
        else:
            model,base,oracle=oracles[cid]
            require(model==row['model'] and base==row['base'],'curve identity drift')
        require(point(row['prepared_base'],oracle.group.p)==oracle.group.mul(row['arm']['base_multiplier'],oracle.base),'prepared base')
        anchor_answer=engine_answer(oracle,None,row['arm'])
        require(row['setup_reason']==anchor_answer['reason'],'setup reason')
        validate_counter_vector(row['counts'])
        setups[key]=(row,oracle)
        counts['setups']+=1
    require(set(setups)==set(plan['setup_ids']),'setup schedule')
    seen=set()
    for row in iter_records(seal,'single-points.jsonl'):
        check('single-point',row)
        require(row['single_id'] not in seen,'duplicate single')
        seen.add(row['single_id'])
        setup,oracle=setups[row['curve_id']+'/'+row['arm_id']]
        R=point(row['point'],oracle.group.p)
        require(R in oracle.logs and R is not None,'single point subgroup')
        require(row['answer']==engine_answer(oracle,R,setup['arm']),'single answer')
        validate_counter_vector(row['counts']);counts['singles']+=1
    require(seen==set(plan['single_ids']),'single schedule')
    # Both iterators advance together: no decoder lists retained across traces.
    cell_iter=iter(iter_records(seal,'decoder-cells.jsonl'))
    intents=iter(iter_records(seal,'attempt-intents.jsonl'))
    seen=set()
    for trace in iter_records(seal,'traces.jsonl'):
        check('trace',trace)
        require(trace['trace_id'] not in seen,'duplicate trace');seen.add(trace['trace_id'])
        intent=check('intent',next(intents))
        require(all(intent[k]==trace[k] for k in intent if k!='schema'),'intent/trace mismatch')
        counts['intents']+=1
        require((trace['incremental'] is not None)==(trace['trace_id'] in plan['paired_trace_ids']),'paired/calibration schedule')
        setup,oracle=setups[trace['curve_id']+'/'+trace['arm_id']]
        if trace['incremental'] is not None:
            require(trace['arm_id']=='circuit2.a1','confirmation primary arm only')
            targets=public_curves[trace['curve_id']]['targets']
            public_targets={t['target_id']:t['point'] for t in targets}
            require(len(public_targets)==len(targets),'duplicate cohort target IDs')
            require(trace['target_id'] in public_targets and trace['target']==public_targets[trace['target_id']],'confirmation public target binding')
        bits,geom=check_engine_trace(oracle,setup['arm'],trace)
        if trace['incremental'] is not None:
            for radius,cap in CELLS:
                cell=check('decoder-cell',next(cell_iter))
                require((cell['radius'],cell['erasure_cap'])==(radius,cap),'cell schedule order')
                checked=check_engine_cell(oracle,trace,bits,cell)
                counts['cells']+=1
                if emit:emit({'trace_id':trace['trace_id'],'cell_id':cell['cell_id'],
                    'geometry':geom,'host_decoder_counts':checked['host_counts'],
                    'worker_counts':cell['counts'],'wall_valid':False})
        counts['traces']+=1
    require(next(intents,None) is None and next(cell_iter,None) is None,'extra intents/cells')
    require(seen==set(plan['trace_ids']),'trace schedule')
    observed={k:counts[k] for k in ('setups','singles','traces','cells','intents')}
    require(summary['observed']==observed,'summary observed counts')
    require(summary['expected']==plan['expected'],'frozen expected counts')
    for name,key in [('setups.jsonl','setups'),('single-points.jsonl','singles'),('traces.jsonl','traces'),('decoder-cells.jsonl','cells'),('attempt-intents.jsonl','intents')]:
        require(completion['files'][name]['records']==counts[key],'completion record count')
    require(completion['status']==summary['status']=='complete' and not summary['errors'],'operational incomplete: retain raw failures')
    require(observed==plan['expected'],'incomplete scheduled workload')
    return {'status':'checked','observed':observed,'tree_sha256':seal.digest,'wall_valid':False,
            'counter_replay_qualified':False,'retained_files':[str(p) for p in seal.files.values()]}
