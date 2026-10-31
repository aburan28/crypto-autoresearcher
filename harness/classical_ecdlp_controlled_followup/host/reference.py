"""Host-only charged working references; no candidate advice or imports."""
from collections import Counter
import hashlib
from math import isqrt
from verify import need_seal, require

MASK_REFERENCE_COUNT = 1023
PRIMARY_ARM = 'circuit2.a1'


class Stream:
    """Deterministic SHA256 counter stream; seed must be frozen before data.

    Uniformity/fairness is under ideal independent hash-block model, not proved
    for SHA256. Domains separate uniform-list and orientation instrumentation.
    No entropy is requested here. Rejected modulo samples remain counted.
    """
    def __init__(self,seed,domain):
        require(type(seed) is bytes and len(seed)==32,'frozen 32-byte seed')
        self.seed,self.domain,self.index=seed,domain,0
        self.counts=Counter()

    def below(self,n):
        require(type(n) is int and 1<=n<=2**256,'stream range')
        limit=2**256-(2**256%n)
        while True:
            h=hashlib.sha256(self.seed+b'\0'+self.domain+b'\0'+self.index.to_bytes(8,'big')).digest()
            self.index+=1
            self.counts['sha256_blocks']+=1
            v=int.from_bytes(h,'big')
            if v<limit:
                self.counts['accepted']+=1
                return v%n
            self.counts['rejected']+=1


class BSGS:
    def __init__(self,seal,g,P):
        need_seal(seal)
        before=Counter(g.counts)
        g.certify(P)
        self.g,self.P=g,P
        self.m=isqrt(g.r-1)+1
        self.table={}
        self.counts=Counter()
        T=None
        for j in range(self.m):
            self.table.setdefault(T,j)
            T=g.add(T,P)
            self.counts['setup_group_add']+=1
        self.step=g.neg(g.mul(self.m,P))
        self.counts.update(setup_scalar_multiply=1,setup_negation=1,
                           stored_points=len(self.table),stored_scalar_words=len(self.table))
        self.setup_group_vector=dict(g.counts-before)

    def solve(self,Q):
        before=Counter(self.g.counts)
        require(self.g.member(Q) and self.g.mul(self.g.r,Q) is None,'BSGS target')
        T=Q
        cost=Counter()
        for i in range(self.m+1):
            cost['table_lookup']+=1
            if T in self.table:
                k=(i*self.m+self.table[T])%self.g.r
                cost['public_scalar_check']+=1
                if self.g.mul(k,self.P)==Q:
                    return {'status':'success','scalar':k,'online':dict(cost),
                            'setup':dict(self.counts),'setup_primitive_vector':self.setup_group_vector,
                            'online_primitive_vector':dict(self.g.counts-before),'warm_setup_increment':0,
                            'cold_includes_setup':True,'wall_valid':False}
            T=self.g.add(T,self.step)
            cost['online_group_add']+=1
        return {'status':'no_solution','scalar':None,'online':dict(cost),
                'setup':dict(self.counts),'setup_primitive_vector':self.setup_group_vector,
                'online_primitive_vector':dict(self.g.counts-before),'wall_valid':False}


def uniform_list(seal,g,P,Q,M,seed):
    """Independent distinct NONZERO guesses, saturation at r-1.

    Conditional matched-M reference only. Determining M in candidate is NOT free
    and must be added for any standalone-solver interpretation.
    """
    need_seal(seal)
    require(type(M) is int and M>=0,'M')
    before=Counter(g.counts)
    target=min(M,g.r-1)
    stream=Stream(seed,b'controlled-followup/uniform-list/v1')
    # Sparse partial Fisher-Yates: independent uniform without replacement.
    swaps={}
    guesses=[]
    checks=[]
    for i in range(target):
        j=i+stream.below(g.r-1-i)
        chosen=swaps.get(j,j)
        swaps[j]=swaps.get(i,i)
        k=chosen+1
        guesses.append(k)
        checks.append(g.mul(k,P)==Q)
    return {'requested_M':M,'effective_M':target,'domain':[1,g.r-1],
            'success_probability_exact':[target,g.r-1],
            'saturated':M>=g.r-1,'guesses':guesses,'checks':checks,
            'success':any(checks),'stream_counts':dict(stream.counts),
            'primitive_vector':dict(g.counts-before),'public_equations':target,'stored_scalar_words':len(swaps)+len(guesses),
            'conditioning':'M measured by candidate; M-determination work excluded here and must be charged',
            'wall_valid':False}


def mask_reference(seal,oracle,mask,seed,arm_id=PRIMARY_ARM):
    """1023 with-replacement orientations; preserve exact holes and ± anchors.

    mask: mapping point->defined bool in one chart. Labels stored by scalar
    index only on host; chart_view transports that SAME assignment.
    """
    need_seal(seal)
    require(arm_id==PRIMARY_ARM,'only fixed primary null arm')
    g=oracle.group
    require(set(mask)==set(oracle.points) and all(type(v) is bool for v in mask.values()),'mask domain')
    for k in range(1,g.r):
        if mask[oracle.points[k]]!=mask[oracle.points[g.r-k]]:
            return {'status':'ineligible_asymmetric_mask','draws':[]}
    if not mask[oracle.base] or not mask[g.neg(oracle.base)]:
        return {'status':'ineligible_undefined_anchor','draws':[]}
    pairs=[k for k in range(1,(g.r+1)//2) if mask[oracle.points[k]]]
    free=[k for k in pairs if k!=1]
    stream=Stream(seed,b'controlled-followup/exact-mask-odd-anchor/v1')
    draws=[]
    seen=Counter()
    for _ in range(MASK_REFERENCE_COUNT):
        orientation=[]
        for k in free:
            bit=stream.below(2)
            orientation.append(bit)
        packed=bytearray((len(free)+7)//8)
        for i,bit in enumerate(orientation):packed[i//8]|=bit<<(7-i%8)
        encoded=bytes(packed).hex()
        seen[encoded]+=1
        draws.append(encoded)
    return {'status':'degenerate' if not free else 'complete','defined_pairs':len(pairs),
            'support':{'base':2,'exponent':len(free),'exact_small':(1<<len(free)) if len(free)<63 else None},'with_replacement':True,'draw_count':MASK_REFERENCE_COUNT,
            'unique_draws':len(seen),'duplicate_draws':MASK_REFERENCE_COUNT-len(seen),
            'orientation_multiplicities':[{'packed_hex':k,'count':v} for k,v in sorted(seen.items())],
            'draws':draws,'free_pair_scalars':free,'r':g.r,'packing':'MSB first; trailing zero padding',
            'stream_counts':dict(stream.counts),
            'packed_bytes_stored':((len(free)+7)//8)*MASK_REFERENCE_COUNT,
            'memory_scope':'one curve at a time; output hex bytes plus exact multiplicities; no full label tables retained',
            'interpretation':'descriptive conditional sign ensemble; no exchangeability or p-value'}


def chart_view(oracle,labels,u):
    g=oracle.group
    require(type(u) is int and 0<u<g.p,'nonzero chart scale')
    return {None if P is None else (u*u*P[0]%g.p,u*u*u*P[1]%g.p):labels[k]
            for k,P in enumerate(oracle.points)}


def tie_counts(observed,statistics):
    return {'equal':sum(x==observed for x in statistics),
            'greater':sum(x>observed for x in statistics),
            'less':sum(x<observed for x in statistics),
            'count':len(statistics),'inferential_p_value':None}


def unpack_labels(result,index):
    require(result['status'] in ('complete','degenerate'),'eligible null required')
    raw=bytes.fromhex(result['draws'][index])
    r=result['r']
    labels=[None]*r
    labels[0],labels[1],labels[r-1]=0,0,1
    for i,k in enumerate(result['free_pair_scalars']):
        b=(raw[i//8]>>(7-i%8))&1
        labels[k],labels[r-k]=b,1-b
    return labels


def retained_bank_statistics(seal,oracle,result,bank_scalars,start_scalars,observed=None):
    """Bounded calibration-only diagnostic; no new predicate calls or all-r q.

    Primary a=1. Inputs are host logs of already retained nonzero public draws.
    Duplicate bank draws and starts remain; fixed future counts 1800 and 128
    are the protocol's job. Null labels never return to worker.
    """
    need_seal(seal)
    r=oracle.group.r
    require(all(type(k) is int and 1<=k<r for k in bank_scalars+start_scalars),'nonzero retained logs')
    require(bank_scalars and start_scalars,'nonempty retained banks')
    L=r.bit_length()+1
    results=[]
    def half(k):return int(k>r//2)
    for i in range(result['draw_count']):
        labels=unpack_labels(result,i)
        score=sum(0 if labels[k] is None else 1 if labels[k]==half(k) else -1 for k in bank_scalars)
        q0=0
        for start in start_scalars:
            k=start;ok=True
            for _ in range(L):
                if labels[k] is None or labels[k]!=half(k):ok=False
                k=2*k%r
            q0+=ok
        results.append({'score_sum':score,'score_denominator':len(bank_scalars),
                        'q0_successes':q0,'q0_denominator':len(start_scalars)})
    ties=None
    if observed is not None:
        ties={'score':tie_counts(observed['score_sum'],[x['score_sum'] for x in results]),
              'q0':tie_counts(observed['q0_successes'],[x['q0_successes'] for x in results])}
    return {'reference_statistics':results,'ties':ties,
        'bank_draws':len(bank_scalars),'bank_duplicates':len(bank_scalars)-len(set(bank_scalars)),
        'trace_starts':len(start_scalars),'start_duplicates':len(start_scalars)-len(set(start_scalars)),
        'diagnostic_label_lookups':result['draw_count']*(len(bank_scalars)+L*len(start_scalars)),
        'work_scope':'retained calibration responses and starts only; no full orbit recovery census; no p-value'}
