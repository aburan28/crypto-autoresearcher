#!/usr/bin/env python3
"""Frozen finite audit TASK-20260911-1b89d4; no target/log solving.

All arithmetic below is local and deterministic. Output files are write-once.
CNF auxiliary variables are eliminated exactly from their defining clauses.
"""
import argparse
import array
import collections
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import signal
import struct
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

TASK='TASK-20260911-1b89d4'
PROTOCOL_SHA='97da73662f6c76fc06591493fb9fdcd7936ab72b3ab47dab00fd2f933d96a8cc'
FROZEN_COMMIT='6ede5f8b9b70f4525f5b60807fa03cad6320b79e'
MEMORY_CAP=2147483648
WATCHDOG=1800
OUT=Path(__file__).resolve().parent
PACKAGE=OUT.parent
REPO=PACKAGE.parents[1]
ISOLATED=REPO/'.worktrees/factor-base-followups-20260911-d069d0'


def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(name,value):
    with (OUT/name).open('x') as f:
        json.dump(value,f,indent=2,sort_keys=True); f.write('\n')
def log(message): print(f'{utc()} {message}',flush=True)
def require(ok,message,**witness):
    if not ok: raise AssertionError(json.dumps({'check':message,'witness':witness},sort_keys=True))
def rss():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform=='darwin' else value*1024)
def checkpoint(label):
    require(rss()<=MEMORY_CAP,'memory_protection',phase=label,peak_rss_bytes=rss())
    log(f'checkpoint {label}; peak_rss_bytes={rss()}')
def timed(fn,*args):
    wall,cpu=time.perf_counter(),time.process_time()
    value=fn(*args)
    return value,{'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,'kind':'measured'}
def git_info(path):
    return {name:subprocess.check_output(['git','-C',str(path),*args],text=True).strip() for name,args in [('commit',['rev-parse','HEAD']),('dirty_porcelain',['status','--porcelain','--untracked-files=normal'])]}


def poly_mod(x,m):
    while x.bit_length()>=m.bit_length(): x^=m<<(x.bit_length()-m.bit_length())
    return x

def poly_gcd(x,y):
    while y: x,y=y,poly_mod(x,y)
    return x

class Field:
    def __init__(self,n,terms):
        self.n=n; self.q=1<<n; self.mask=self.q-1; self.modulus=self.q|sum(1<<i for i in terms)
        self.ops=collections.Counter()
    def mul(self,a,b):
        self.ops['multiplication']+=1
        v=0
        while b:
            if b&1:v^=a
            b>>=1;a<<=1
            if a&self.q:a^=self.modulus
        return v
    def sq(self,a):
        self.ops['squaring']+=1
        v=0;bit=0
        while a:
            if a&1:v|=1<<bit
            a>>=1;bit+=2
        return poly_mod(v,self.modulus)
    def inv(self,a):
        self.ops['inversion']+=1
        if not a:raise ZeroDivisionError('field inverse of zero')
        u,v=a,self.modulus;g,h=1,0
        while u!=1:
            shift=u.bit_length()-v.bit_length()
            if shift<0:u,v=v,u;g,h=h,g;shift=-shift
            u^=v<<shift;g^=h<<shift
        return poly_mod(g,self.modulus)
    def mul_replay(self,a,b):
        # Independently form the unreduced polynomial, then long-divide.
        product=0
        for i in range(self.n):
            if b&(1<<i):product^=a<<i
        return poly_mod(product,self.modulus)
    def irreducibility(self):
        z=2;checks=[]
        for k in range(1,self.n+1):
            z=self.sq(z)
            if k<=self.n//2:
                g=poly_gcd(z^2,self.modulus)
                checks.append({'degree':k,'gcd':g})
                require(g==1,'modulus_reducible',degree=k,gcd=g)
        require(z==2,'frobenius_field_identity',value=z)
        return {'modulus':self.modulus,'gcd_checks':checks,'x_power_2n':z,'irreducible':True}
    def equation(self,p,replay=False):
        if p is None:return True
        x,y=p;m=self.mul_replay if replay else self.mul
        return m(y,y)^m(x,y)==m(m(x,x),x)^m(x,x)^1
    def add(self,p,q):
        self.ops['group_addition']+=1
        if p is None:return q
        if q is None:return p
        x,y=p;u,v=q
        if x==u:
            if y!=v or x==0:return None
            slope=x^self.mul(y,self.inv(x))
            xx=self.sq(slope)^slope^1
            return (xx,self.sq(x)^self.mul(slope^1,xx))
        slope=self.mul(y^v,self.inv(x^u))
        xx=self.sq(slope)^slope^x^u^1
        return (xx,self.mul(slope,x^xx)^xx^y)
    def scalar(self,p,k):
        # Public fixed subgroup-order test only; never searches for a scalar.
        out=None
        while k:
            if k&1:out=self.add(out,p)
            k>>=1
            if k:p=self.add(p,p)
        return out
    def ys(self,x):
        self.ops['rational_x_test']+=1
        if x==0:return [1]
        inv=self.inv(x);rhs=x^1^self.sq(inv)
        z=rhs;term=rhs
        for _ in range((self.n-1)//2):term=self.sq(self.sq(term));z^=term
        if self.sq(z)^z!=rhs:return []
        y=self.mul(x,z)
        return sorted([y,y^x])


def inverse_columns(columns,n):
    rows=[sum(((columns[j]>>i)&1)<<j for j in range(n))|(1<<(n+i)) for i in range(n)]
    for j in range(n):
        pivot=next((i for i in range(j,n) if rows[i]&(1<<j)),None)
        if pivot is None:return None
        rows[j],rows[pivot]=rows[pivot],rows[j]
        for i in range(n):
            if i!=j and rows[i]&(1<<j):rows[i]^=rows[j]
    inverse_rows=[row>>n for row in rows]
    return [sum(((inverse_rows[i]>>j)&1)<<i for i in range(n)) for j in range(n)]

def linear_table(columns,n):
    table=array.array('I',[0])*(1<<n)
    for c in range(1,1<<n):
        low=c&-c;table[c]=table[c^low]^columns[low.bit_length()-1]
    return table

def linear_replay(columns,c):
    answer=0
    for j,value in enumerate(columns):
        if (c>>j)&1:answer^=value
    return answer

def rot(c,s,n):
    s%=n
    return ((c<<s)|(c>>(n-s)))&((1<<n)-1) if s else c

def prepare_basis(f):
    failures=[]
    for beta in range(1,f.q):
        columns=[beta]
        for _ in range(f.n-1):columns.append(f.sq(columns[-1]))
        inv=inverse_columns(columns,f.n)
        if inv is not None:break
        failures.append(beta)
    forward=linear_table(columns,f.n);backward=linear_table(inv,f.n)
    require(all(backward[forward[c]]==c for c in range(f.q)),'basis_roundtrip')
    wrong=columns.copy();wrong[1],wrong[2]=wrong[2],wrong[1]
    wi=inverse_columns(wrong,f.n)
    wf=linear_table(wrong,f.n);wb=linear_table(wi,f.n)
    require(all(wb[wf[c]]==c for c in range(f.q)),'wrong_basis_roundtrip')
    mismatch=None
    for c in [1<<j for j in range(f.n)]:
        require(f.sq(forward[c])==forward[rot(c,1,f.n)],'normal_frobenius',c=c)
        left=f.sq(wf[c]);right=wf[rot(c,1,f.n)]
        if left!=right and mismatch is None:mismatch={'coordinate_word':c,'wrong_map_square':left,'wrong_map_rotation':right}
    require(mismatch is not None,'wrong_basis_negative_control_did_not_fail')
    return forward,{'beta':beta,'ordered_columns':columns,'inverse_columns':inv,'smaller_positive_candidates_rejected':failures,'roundtrip_assignment_count':f.q,'frobenius_basis_vector_checks':f.n}, {'wrong_columns':wrong,'inverse_columns':wi,'roundtrip_passed_assignments':f.q,'frobenius_mismatch':mismatch}


def make_union(n,d):
    multiplicity=collections.Counter()
    for word in range(1<<d):
        for s in range(n):multiplicity[rot(word,s,n)]+=1
    # Independent set construction places each active bit at a modular index.
    replay=set()
    for s in range(n):
        for assignment in range(1<<d):
            replay.add(sum(((assignment>>j)&1)<<((s+j)%n) for j in range(d)))
    require(set(multiplicity)==replay,'union_replay')
    return multiplicity


def emit_cnf(n,d):
    clauses=[]
    for s in range(n):
        outside=[i+1 for i in range(n) if (i-s)%n>=d]
        selector=n+s+1
        clauses.extend([[-selector,-v] for v in outside])
        clauses.append([selector,*outside])
    clauses.append(list(range(n+1,2*n+1)))
    return {'input_variables':n,'auxiliary_variables':n,'variables':2*n,'clauses':clauses,
            'dimacs':'p cnf %s %s\n%s\n'%(2*n,len(clauses),'\n'.join(' '.join(map(str,c))+' 0' for c in clauses))}


def compile_exact_elimination(cnf):
    """Check emitted definitional CNF then eliminate every selector exactly.

    (-A or -x_i) forces A=0 when any outside x_i=1.
    (A or x_1 ... x_k) forces A=1 when all outside x_i=0.
    Thus each selector is uniquely fixed for every c; the final clause accepts
    iff some fixed selector is true. This computes existence over all 2^n
    selector assignments, not just a chosen satisfying extension.
    """
    n=cnf['input_variables'];forbid={a:0 for a in range(n+1,2*n+1)};bindings={}
    ors=[]
    for clause in cnf['clauses']:
        if len(clause)==2 and clause[0]<-n and -n<=clause[1]<0:
            forbid[-clause[0]]|=1<<(-clause[1]-1)
        elif clause[0]>n and all(1<=v<=n for v in clause[1:]):
            require(clause[0] not in bindings,'duplicate_selector_binding')
            bindings[clause[0]]=sum(1<<(v-1) for v in clause[1:])
        else:ors.append(clause)
    require(ors==[list(range(n+1,2*n+1))],'unexpected_residual_cnf',clauses=ors)
    require(forbid==bindings,'selector_definition_mismatch',forbid=forbid,bindings=bindings)
    return list(forbid.values())


def emit_trie(words,n):
    nodes=[[-1,-1,False]]
    for word in sorted(words):
        node=0
        for j in range(n):
            b=(word>>j)&1
            if nodes[node][b]==-1:nodes[node][b]=len(nodes);nodes.append([-1,-1,False])
            node=nodes[node][b]
        nodes[node][2]=True
    return {'bit_order':'least-significant first','root':0,'missing_edge':-1,'nodes':nodes}


def trie_accept(trie,c,n):
    node=trie['root'];nodes=trie['nodes']
    for j in range(n):
        node=nodes[node][(c>>j)&1]
        if node==-1:return False
    return nodes[node][2]


def membership_case(n,d):
    mult,union_cost=timed(make_union,n,d)
    cnf,cnf_cost=timed(emit_cnf,n,d)
    masks=compile_exact_elimination(cnf)
    trie,trie_cost=timed(emit_trie,mult,n)
    outside=[((1<<n)-1)^sum(1<<((s+j)%n) for j in range(d)) for s in range(n)]
    tables={k:bytearray(1<<n) for k in ['support_containment','enumerated_union','existential_cnf','emitted_trie']}
    multiplicity_all=collections.Counter();selector_hist=collections.Counter();check_wall=time.perf_counter();check_cpu=time.process_time()
    for c in range(1<<n):
        direct=any(c&m==0 for m in outside)
        union=c in mult
        selectors=sum(c&m==0 for m in masks)
        cnf_exists=selectors>0
        trie_truth=trie_accept(trie,c,n)
        require(direct==union==cnf_exists==trie_truth,'membership_mismatch',n=n,width=d,c=c,direct=direct,union=union,cnf=cnf_exists,trie=trie_truth)
        require(selectors==mult.get(c,0),'multiplicity_selector_mismatch',c=c)
        for key,val in zip(tables,(direct,union,cnf_exists,trie_truth)):tables[key][c]=val
        multiplicity_all[mult.get(c,0)]+=1;selector_hist[selectors]+=1
    truth_cost={'wall_seconds':time.perf_counter()-check_wall,'cpu_seconds':time.process_time()-check_cpu,'kind':'measured'}
    hashes={key:hashlib.sha256(value).hexdigest() for key,value in tables.items()}
    unseen=set(mult);orbits=[]
    while unseen:
        leader=min(unseen);orbit=sorted({rot(leader,s,n) for s in range(n)})
        require(set(orbit)<=set(mult),'orbit_closure')
        unseen.difference_update(orbit);orbits.append(orbit)
    witness=min(c for c in mult if c>>d)
    require(not (witness & ~((1<<d)-1)==0),'single_window_negative_control_failed')
    raw=sum(mult.values());require(raw==n*(1<<d),'rotation_draw_count')
    count={'n':n,'width':d,'assignments_checked':1<<n,'raw_cardinality':len(mult),'rotation_construction_draws':raw,
           'membership_multiplicity_histogram_all_inputs':dict(multiplicity_all),'positive_multiplicity_histogram':dict(collections.Counter(mult.values())),
           'unique_rotation_orbits':len(orbits),'orbit_length_histogram':dict(collections.Counter(map(len,orbits))),
           'raw_predicate_mismatches':0,'unique_satisfying_auxiliary_extension_when_accepted':True,
           'raw_construction_cost':union_cost,'truth_check_cost':truth_cost}
    representation={'n':n,'width':d,'scope':'raw coordinate-window membership only; rationality and subgroup constraints are separate',
       'cnf':cnf,'cnf_clause_count':len(cnf['clauses']),'cnf_literal_count':sum(map(len,cnf['clauses'])),
       'cnf_dimacs_bytes':len(cnf['dimacs'].encode()),'cnf_construction_cost':cnf_cost,
       'exact_existential_elimination':{'selector_definition':'A_s iff all outside-window bits are zero','structural_clause_check':True,'selector_count_histogram':dict(selector_hist),'satisfying_auxiliary_assignments_per_accepted_input':1,'satisfying_auxiliary_assignments_per_rejected_input':0},
       'trie':trie,'trie_node_count':len(trie['nodes']),'trie_edge_count':sum(child>=0 for node in trie['nodes'] for child in node[:2]),
       'trie_terminal_count':sum(node[2] for node in trie['nodes']),'trie_json_bytes':len(json.dumps(trie,separators=(',',':')).encode()),'trie_construction_cost':trie_cost,
       'general_circuit_gate_count':None,'general_circuit_gate_reason':'Actual CNF and trie emitted; no separate generic Boolean circuit synthesized.'}
    pointdata={'n':n,'width':d,'raw_coordinate_words':sorted(mult),'coordinate_multiplicities':[[c,mult[c]] for c in sorted(mult)],'rotation_orbits':orbits}
    negative={'n':n,'width':d,'single_unrotated_window':{'true_union_word':witness,'incorrect_predicate_accepts':False,'true_union_accepts':True}}
    return count,representation,pointdata,negative,{'n':n,'width':d,'encoding':'one byte 0/1 per ascending coordinate word; no header','assignments':1<<n,'sha256':hashes}


def public_oracle(f,g,r):
    """Independent public group cycle; never retain any point->scalar mapping."""
    require(g is not None and f.equation(g,replay=True),'public_generator_curve')
    require(f.scalar(g,r) is None,'public_generator_order')
    require(all(r%q for q in range(2,int(r**0.5)+1)),'declared_subgroup_order_not_prime')
    mul=f.mul_replay
    def next_point(point):
        # Separate addition implementation with polynomial-product reduction.
        if point is None:return g
        x,y=point;u,v=g
        if x==u:
            if y^v==x:return None
            require(y==v,'invalid_equal_x_group_pair')
            if x==0:return None
            t=x^mul(y,f.inv(x));xx=mul(t,t)^t^1
            return xx,mul(x,x)^mul(t^1,xx)
        t=mul(y^v,f.inv(x^u));xx=mul(t,t)^t^x^u^1
        return xx,mul(t,x^xx)^xx^y
    points=set();point=None
    for _ in range(r-1):
        point=next_point(point)
        require(point is not None and point not in points,'public_cycle_early_repeat')
        require(f.equation(point,replay=True),'public_oracle_curve',point=point)
        points.add(point)
        if len(points)%16384==0:checkpoint(f'n{f.n} public subgroup points={len(points)}')
    require(next_point(point) is None,'public_cycle_not_closed')
    digest=hashlib.sha256()
    for x,y in sorted(points):digest.update(struct.pack('<II',x,y))
    return points,{'method':'full public-generator group cycle using separate addition and polynomial-product reduction; no scalar labels retained','nonidentity_point_count':len(points),'identity_included_in_group_order':True,'group_order_with_identity':len(points)+1,'sorted_affine_pairs_u32le_sha256':digest.hexdigest(),'prime_subgroup_order_trial_division_pass':True,'closed_at_declared_order':True,'curve_checks':len(points)}


def filter_points(f,params,forward,basis,raw,oracle):
    start_wall,start_cpu=time.perf_counter(),time.process_time();before=f.ops.copy()
    entries=[];rational=[];subgroup=[];rejected=[];exhaustive_count=0
    for c in raw['raw_coordinate_words']:
        x=forward[c]
        require(x==linear_replay(basis['ordered_columns'],c),'independent_basis_mapping',c=c)
        require(f.sq(x)==forward[rot(c,1,f.n)],'member_frobenius',c=c)
        require(f.sq(x)==f.mul_replay(x,x),'square_multiplication_replay',x=x)
        ys=f.ys(x)
        if f.n==7:
            y_oracle=[y for y in range(f.q) if f.equation((x,y),replay=True)]
            exhaustive_count+=f.q
            require(ys==y_oracle,'exhaustive_y_mismatch',x=x,ys=ys,oracle=y_oracle)
        admitted=[]
        for y in ys:
            p=(x,y)
            require(f.equation(p) and f.equation(p,replay=True),'rational_equation',point=p)
            rational.append([c,x,y]);test=f.scalar(p,params['subgroup_order']) is None
            if oracle is not None:require(test==(p in oracle),'subgroup_oracle_mismatch',point=p)
            if test:admitted.append(y);subgroup.append([c,x,y])
            else:rejected.append({'coordinate_word':c,'x':x,'y':y,'reason':'nonidentity fixed-r multiplication'})
        if not ys:rejected.append({'coordinate_word':c,'x':x,'reason':'no rational affine y'})
        entries.append({'coordinate_word':c,'polynomial_x':x,'rational_y':ys,'subgroup_y':admitted})
    rational_x=sum(bool(e['rational_y']) for e in entries);subgroup_x=sum(bool(e['subgroup_y']) for e in entries)
    metrics={'raw_field_values':len(entries),'rational_x_values':rational_x,'rational_affine_points':len(rational),
             'subgroup_x_values':subgroup_x,'subgroup_affine_points':len(subgroup),'excluded_nonrational_x_values':len(entries)-rational_x,
             'rational_x_excluded_by_subgroup':rational_x-subgroup_x,'rational_points_excluded_by_subgroup':len(rational)-len(subgroup),
             'x_zero':next(e for e in entries if e['polynomial_x']==0),'additional_curve_subgroup_cost':{
                 'kind':'measured','wall_seconds':time.perf_counter()-start_wall,'cpu_seconds':time.process_time()-start_cpu,'field_and_group_operations':dict(f.ops-before),
                 'normal_conversion_lookups':len(entries),'independent_mapping_checks':len(entries),'frobenius_checks':len(entries),
                 'rational_y_candidates_equation_checked':len(rational),'fixed_r_subgroup_tests':len(rational),'independent_n7_y_assignments':exhaustive_count,
                 'rational_or_subgroup_cnf_variables':None,'rational_or_subgroup_cnf_clauses':None,'unavailable_reason':'No rationality/subgroup CNF synthesized by this finite enumeration audit; raw membership encoding is not complete factor-base membership.'},
             'rational_membership_mismatches':0,'subgroup_membership_mismatches':0}
    raw.update({'field_entries':entries,'rational_points_c_x_y':rational,'subgroup_points_c_x_y':subgroup,'rejected_examples_all':rejected})
    return metrics


class WatchdogExpired(Exception): pass

def watchdog_handler(signum,frame):raise WatchdogExpired('1800-second process liveness watchdog expired')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true',required=True);parser.parse_args()
    terminal_names=['results.json','truth_table_hashes.json','point_sets.json','negative_controls.json','representations.json','receipt.json','stdout.log','stderr.log','report.md']
    require(not any((OUT/name).exists() for name in terminal_names),'terminal_output_exists; never overwrite')
    sys.stdout=(OUT/'stdout.log').open('x',buffering=1);sys.stderr=(OUT/'stderr.log').open('x',buffering=1)
    started=utc();wall,cpu=time.perf_counter(),time.process_time()
    receipt={'task_id':TASK,'started_at':started,'protocol_sha256':PROTOCOL_SHA,'approval_commit':FROZEN_COMMIT,
             'command_argv':[sys.executable,*sys.argv],'cwd':str(Path.cwd()),'source_code_path':str(Path(__file__).resolve()),'source_code_sha256':sha(__file__),
             'implementation_commit':None,'implementation_commit_reason':'Executor code is hash-bound here; Coordinator producer snapshot follows terminal artifacts.',
             'model_provenance':{'runtime':'native Codex','requested_policy':'executor-implementation','resolved_model_id':None,'model_verified':False,'reasoning_effort':None,'fallback_used':False,'degraded_requirements':[]},
             'environment':{'python':sys.version,'platform':platform.platform(),'machine':platform.machine()},'randomness':{'seeds':[],'policy':'deterministic exhaustive enumeration'},
             'resource_protection':{'memory_bytes':MEMORY_CAP,'watchdog_seconds':WATCHDOG,'method':'Bounded field/truth arrays and subgroup set; self peak-RSS checks between each stage and each 16384 public-oracle insertions; SIGALRM liveness watchdog.',
                                    'os_hard_memory_limit':False,'limitation':'Self checkpoints detect overruns after bounded allocation intervals; no claim of hard OS enforcement. Darwin RLIMIT_AS and process-list sampling are not used.',
                                    'largest_dynamic_domains':{'truth_words':524288,'tables_per_case':4,'field_map_entries_each':524288,'subgroup_set_points_maximum':262542}},
             'network_requests':0,'direct_inputs':[],'protocol_deviations':[],'independent_review':'pending Coordinator snapshot and independent review',
             'dependent_105_partition_gate':{'status':'unrun','execution_authorized':False}}
    results={'task_id':TASK,'scope':'finite raw membership and rational/subgroup filtering; no SAT decomposition or asymptotic/cryptanalytic claim','curves':[],'cases':[]}
    truth=[];pointsets=[];negatives={'basis_controls':[],'case_controls':[]};representations=[]
    terminal='failed_implementation';error=None
    signal.signal(signal.SIGALRM,watchdog_handler);signal.alarm(WATCHDOG)
    try:
        log('Starting frozen finite membership audit')
        receipt['isolated_worktree']=git_info(ISOLATED)
        receipt['source_repository']=git_info('/Volumes/SSD990/crypto-hybrid-rank-wt')
        receipt['working_repository']=git_info(REPO)
        for name in ['protocol.json','approval.md','handoffs/membership.json','source_bindings.json','archive_audit.json','dispatch_plan.json']:
            path=PACKAGE/name;receipt['direct_inputs'].append({'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size})
        require(sha(PACKAGE/'protocol.json')==PROTOCOL_SHA,'protocol_hash_changed')
        protocol=json.loads((PACKAGE/'protocol.json').read_text())
        require(json.loads((PACKAGE/'archive_audit.json').read_text())['all_hashes_match'],'source_archive_gate')
        dispatch=json.loads((PACKAGE/'dispatch_plan.json').read_text())
        require(all(dispatch['gates'].values()),'dispatch_gate_failed')
        require(TASK in [t['id'] for t in dispatch['dispatches']],'task_not_dispatched')
        for relative in ['protocol.json','approval.md','handoffs/membership.json']:
            committed=subprocess.check_output(['git','-C',str(ISOLATED),'show',FROZEN_COMMIT+':research/factor_base_followup_20260911_d069d0/'+relative])
            require(committed==(PACKAGE/relative).read_bytes(),'committed_contract_mismatch',path=relative)
        source=protocol['source'];source_root=Path(source['repository'])/source['evidence_root']
        for pin in source['pins']:
            path=source_root/pin['path'];actual=sha(path)
            receipt['direct_inputs'].append({'path':str(path),'sha256':actual,'bytes':path.stat().st_size})
            require(actual==pin['sha256'],'source_pin_mismatch',path=str(path))
        public=json.loads((source_root/'autolab_n19_k4_balanced_frontier_fresh/frozen/base/prefix_k3.json').read_text())['base']
        for params in protocol['parameters']['curves']:
            n=params['n'];require(n in (7,19),'unexpected_field_size')
            require(params['a']==params['b']==1 and params['cofactor']==2,'unexpected_curve_parameters')
            f=Field(n,params['field_modulus_low_terms']);irreducible,field_cost=timed(f.irreducibility)
            basis_output,basis_cost=timed(prepare_basis,f);forward,basis,wrong=basis_output
            negatives['basis_controls'].append({'n':n,**wrong})
            curve={'parameters':params,'irreducibility':irreducible,'basis':basis,'field_check_cost':field_cost,'basis_preparation_cost':basis_cost}
            oracle=None
            if n==19:
                require(all(public[k]==params[k] for k in ['n','a','b','subgroup_order','cofactor','field_modulus_low_terms']),'public_generator_parameter_mismatch')
                oracle_output,oracle_cost=timed(public_oracle,f,tuple(public['generator']),params['subgroup_order'])
                oracle,oracle_report=oracle_output;curve['independent_subgroup_oracle']={**oracle_report,'construction_cost':oracle_cost,'public_generator':public['generator']}
            else:
                # Exhaust the complete affine curve independently for the group-order control.
                all_points=[(x,y) for x in range(f.q) for y in range(f.q) if f.equation((x,y),replay=True)]
                require(len(all_points)+1==params['group_order'],'n7_full_curve_order')
                all_subgroup=[p for p in all_points if f.scalar(p,params['subgroup_order']) is None]
                require(len(all_subgroup)+1==params['subgroup_order'],'n7_full_subgroup_order')
                curve['complete_curve_enumeration']={'xy_assignments':f.q*f.q,'affine_points':len(all_points),'subgroup_affine_points':len(all_subgroup),'all_affine_points':all_points,'all_subgroup_affine_points':all_subgroup}
            results['curves'].append(curve);checkpoint(f'n{n} field and group prerequisites')
            for d in params['window_widths']:
                require((n==7 and 1<=d<=3) or (n==19 and 1<=d<=5),'unexpected_width')
                count,representation,raw,negative,hashes=membership_case(n,d)
                filters=filter_points(f,params,forward,basis,raw,oracle);count.update(filters)
                count['terminal_state']='completed_valid'
                results['cases'].append(count);representations.append(representation);pointsets.append(raw);negatives['case_controls'].append(negative);truth.append(hashes)
                log(json.dumps({'case':[n,d],'raw':count['raw_cardinality'],'rational_x':count['rational_x_values'],'rational_points':count['rational_affine_points'],'subgroup_x':count['subgroup_x_values'],'subgroup_points':count['subgroup_affine_points'],'cnf_clauses':representation['cnf_clause_count'],'trie_nodes':representation['trie_node_count']},sort_keys=True))
                checkpoint(f'n{n} width{d} terminal')
            del oracle,forward
        require(len(results['cases'])==8,'case_count')
        terminal='completed_valid'
    except WatchdogExpired as exc:
        terminal='resource_exhaustion';error=str(exc);traceback.print_exc()
    except (FileNotFoundError,OSError) as exc:
        terminal='failed_infrastructure';error=str(exc);traceback.print_exc()
    except BaseException as exc:
        terminal='failed_implementation';error=str(exc);traceback.print_exc()
    finally:
        signal.alarm(0)
        results.update({'terminal_state':terminal,'error':error,'completed_cases':len(results['cases']),'missing_cases':[list(pair) for pair in [(7,1),(7,2),(7,3),(19,1),(19,2),(19,3),(19,4),(19,5)] if not any((c['n'],c['width'])==pair for c in results['cases'])]})
        put('results.json',results);put('truth_table_hashes.json',truth);put('point_sets.json',pointsets);put('negative_controls.json',negatives);put('representations.json',representations)
        lines=[f'# Membership audit {TASK}', '',f'Terminal state: `{terminal}`. Completed {len(results["cases"])}/8 frozen cases.','',
               'Observed finite raw membership is tested separately from rational-point and prime-subgroup eligibility. Every truth table enumerates all coordinate words. The emitted CNF uses exact definitional selectors; its checker verifies that each input uniquely determines every selector before evaluating the final disjunction. No solver or target logarithm is computed.','',
               '| n | width | assignments | raw words | rational x | rational points | subgroup x | subgroup points | CNF clauses | trie nodes |',
               '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
        for c,r in zip(results['cases'],representations):lines.append(f'| {c["n"]} | {c["width"]} | {c["assignments_checked"]} | {c["raw_cardinality"]} | {c["rational_x_values"]} | {c["rational_affine_points"]} | {c["subgroup_x_values"]} | {c["subgroup_affine_points"]} | {r["cnf_clause_count"]} | {r["trie_node_count"]} |')
        lines+=['','`point_sets.json` retains every raw coordinate word, multiplicity, rotation orbit, rational/subgroup point and rejection. `negative_controls.json` retains a rejected single-window witness for every width and the invertible wrong-basis witnesses. `truth_table_hashes.json` hashes every ascending full-domain 0/1 table. `representations.json` contains the actual CNF clauses, DIMACS text and complete tries.','',
                'Construction and validation times are measured producer implementation costs, not SAT-solving or attack costs. Normal-coordinate conversion and the additional rational/subgroup work have separate measurements and operation counts. Rational/subgroup CNF sizes remain unavailable: raw membership CNF/trie sizes do not represent complete factor-base membership. Public subgroup enumeration has a separate construction cost; no point-to-scalar labels are retained.','',
                'The degree-7 control independently enumerates every y, and the degree-19 control compares against a complete public-generator cycle built with a separate addition and polynomial multiplication implementation. These internal implementation controls do not replace independent review.','',
                'The dependent 105-partition SAT integration gate is **unrun and not authorized** by this protocol. There is no full decomposition PASS, scientific status transition, asymptotic transfer, novelty claim, or fixed-target free-rotation assumption.','',
                'Implementation deviations: none to the scientific protocol. Memory protection uses bounded allocations and self peak-RSS checkpoints; no hard OS memory limit is asserted. Exact resolved model identity is unavailable and recorded null/unverified. Producer snapshot and independent review remain Coordinator work.']
        if error:lines+=['',f'Failure retained: `{error}`. This is not mathematical negative evidence.']
        with (OUT/'report.md').open('x') as report:report.write('\n'.join(lines)+'\n')
        log(f'Terminal {terminal}; cases={len(results["cases"])}/8')
        sys.stdout.flush();sys.stderr.flush()
        receipt.update({'terminal_state':terminal,'valid':terminal=='completed_valid','validity_reason':'All eight finite cases and required controls completed without mismatch' if terminal=='completed_valid' else error,
                        'completed_at':utc(),'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,'peak_rss_bytes':rss(),
                        'completed_case_count':len(results['cases']),'failure':error,'artifact_sha256':{name:sha(OUT/name) for name in terminal_names if name!='receipt.json'},
                        'observations_only':True,'executor_assessment':{'protocol_complete':terminal=='completed_valid','data_quality':'good' if terminal=='completed_valid' else 'invalid','requires_rerun':terminal!='completed_valid'}})
        put('receipt.json',receipt)
    return 0 if terminal=='completed_valid' else 1

if __name__=='__main__':sys.exit(main())
