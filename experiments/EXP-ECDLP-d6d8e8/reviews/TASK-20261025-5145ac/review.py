#!/usr/bin/env python3
"""Independent observation-integrity review. Phase1 uses only specification inputs.
No producer/checker arithmetic is imported. No new scientific trial is run.
"""
import json,hashlib,math,datetime,sys,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
FROZEN='research/prym_rank_census_20261025/'
SPEC='experiments/EXP-ECDLP-d6d8e8/specification.yaml'
def sha(b):return hashlib.sha256(b).hexdigest()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def readj(p):return json.loads((ROOT/p).read_text())
def dump(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def prime(n):return n>1 and all(n%d for d in range(2,math.isqrt(n)+1))
def neg(q,p):return None if q is None else (q[0],-q[1]%p)
def add(q,t,p,A,a2=0):
 if q is None:return t
 if t is None:return q
 x,y=q;u,v=t
 if x==u and (y+v)%p==0:return None
 m=((3*x*x+2*a2*x+A)*pow(2*y,-1,p) if q==t else (v-y)*pow(u-x,-1,p))%p
 z=(m*m-a2-x-u)%p
 return z,(m*(x-z)-y)%p

def mul(n,q,p,A,a2=0):
 if n<0:return mul(-n,neg(q,p),p,A,a2)
 z=None
 while n:
  if n&1:z=add(z,q,p,A,a2)
  q=add(q,q,p,A,a2);n//=2
 return z

def norm(q,p):return None if q is None else min(q,neg(q,p))
def phase1():
 cfg=readj(FROZEN+'config.json');fset=readj(FROZEN+'fixtures.json')['fixtures'];out=[]
 for f in fset:
  p,A,B,r=f['p'],f['a'],f['b'],f['r'];P=tuple(f['P'])
  sq={}
  for y in range(p):sq.setdefault(y*y%p,[]).append(y)
  pts=[(x,y) for x in range(p) for y in sq.get((x*x*x+A*x+B)%p,[])]
  assert len(pts)+1==r and prime(r) and r!=p and prime(p)
  assert P==pts[0] and mul(r,P,p,A) is None
  fb=[];seen=set()
  for x in range(p):
   for y in sq.get((pow(x,6,p)+A*x*x+B)%p,[]):
    F=(x*x%p,y);N=norm(F,p)
    if N not in seen:
     seen.add(N);fb.append({'point':list(N),'lift':[x,min(y,-y%p)]})
   if len(fb)>=8:break
  assert fb[:8]==f['factor_base']
  publics=[mul(a,P,p,A) for a in range(1,65)]
  anchor={}
  for a,Q in enumerate(publics,1):
   N=norm(Q,p);sgn=1 if Q==N else -1
   anchor.setdefault(N,(sgn*a)%r)
  unknown=[];mapping=[]
  for atom in f['factor_base']:
   q=tuple(atom['point']);N=norm(q,p);sgn=1 if q==N else -1
   if N is None:mapping.append({'kind':'zero'})
   elif N in anchor:mapping.append({'kind':'known','scalar':sgn*anchor[N]%r,'canonical_point':list(N),'sign':sgn})
   else:
    if N not in unknown:unknown.append(N)
    mapping.append({'kind':'unknown','column':unknown.index(N),'canonical_point':list(N),'sign':sgn})
  # Hash conventions deferred until unblinding; mathematical EC1 fields checked here.
  ec=f['ec1'];assert ec['field']['characteristic']==p and ec['field']['degree']==1
  assert ec['curve']['a4']==A and ec['curve']['a6']==B and ec['curve']['subgroup_order']==r and ec['curve']['generator']==list(P)
  out.append({'p':p,'A':A,'B':B,'r':r,'order_recount':len(pts)+1,'generator':list(P),'uid':f['uid'],'curve_uid':ec['curve_uid'],'public_source_images':[list(q) if q else None for q in publics],'native_projection':mapping,'unknown_points':[list(q) for q in unknown],'U':len(unknown),'public_anchor_classes':len(anchor),'base_regenerated':True})
 result={'schema':'prym-observation-blinded-derivation/v1','task_id':'TASK-20261025-5145ac','sealed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allowed_scientific_sources':[SPEC,FROZEN+'config.json',FROZEN+'fixtures.json'],'input_sha256':{p:sha((ROOT/p).read_bytes()) for p in [SPEC,FROZEN+'config.json',FROZEN+'fixtures.json']},'blind_from_respected':True,'producer_outputs_or_code_read':False,'protocol_administrative_sources':['AGENTS.md','agents/validator.md','docs/lab-contract.md','docs/agent-contract-extended.md','ledger/handoffs/TASK-20261025-5145ac.yaml','.claude/skills/research-visuals/SKILL.md'],'counts':{'branch_support_per_source':math.comb(8,3)*4**3,'sample_per_source':64,'fixtures':8,'sources_per_fixture':64,'sample_attempts':8*64*64,'full_attempts':8*64*3584,'total_attempts':8*64*(64+3584)},'fixtures':out,'derived_conventions':{'E1':'(U,Y)=(x^2,y), Y^2=U^3+A*U+B','E2':'(W,Z)=(B/x^2,B*y/x^3), Z^2=W^3+A*W^2+B^2; a2=A,a4=0,a6=B^2','infinity_E1':'both infinity branches map to O','infinity_E2':'infinity branch y/x^3 -> epsilon maps to (0,epsilon*B); x=0 maps to O','function_valuation':'With t=1/x, y=epsilon*t^-3*(1+(A/2)*t^4+(B/2)*t^6+...). For v=sum(v_i*x^i), first nonzero Laurent coefficient of y-v gives signed ord at each epsilon=+/-1. Generic v3 unequal +/-1 has ord=-3 at both; if epsilon=v3 and v2!=0 ord=-2, else v1!=0 ord=-1, else v0!=0 ord=0, else A!=0 ord=+1. Retain zeros as well as poles. Finite divisor has roots of f-v^2 with multiplicity and y=v; norm its full signed divisor including infinity.','projection':'canonical point min((U,Y),(U,-Y)); transport signs; known anchors only among +/-[a]P for a=1..64; choose earliest public representative; subtract known terms from c*a modulo r','hash_identity_scope':'EC1 numerical metadata checked; exact UID/EC1 serialization/hash convention deferred until phase2 because its source is not phase1 allowed.'},'procedure_deviations':[]}
 p=OUT/'blinded-input-derivation.json';assert not p.exists();dump(p,result);print(result['sealed_at'],sha(p.read_bytes()));print([(x['p'],x['B'],x['U']) for x in out])
if __name__=='__main__' and sys.argv[-1]=='phase1':phase1()

# Phase2 independently implemented polynomial, curve and matrix checks.
def pm(a,b,p):
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]=(c[i+j]+x*y)%p
 return c

def pe(v,x,p):
 z=0
 for c in reversed(v):z=(z*x+c)%p
 return z

def interpol(points,p):
 v=[0]*4
 for i,(x,y) in enumerate(points):
  b=[1];d=1
  for j,(u,w) in enumerate(points):
   if i!=j:b=pm(b,[-u%p,1],p);d=d*(x-u)%p
  a=y*pow(d,-1,p)%p
  for j,c in enumerate(b):v[j]=(v[j]+a*c)%p
 while len(v)>1 and v[-1]==0:v.pop()
 return v

def quotient(v,points,f):
 p=f['p'];poly=pm(v,v,p)+[0]*7;poly=poly[:7]
 for j,c in enumerate([f['b'],0,f['a'],0,0,0,1]):poly[j]=(poly[j]-c)%p
 b=[1]
 for x,y in points:b=pm(b,[-x%p,1],p)
 out=[0]*3
 for i in range(6,3,-1):
  c=poly[i];out[i-4]=c
  for j,z in enumerate(b):poly[i-4+j]=(poly[i-4+j]-c*z)%p
 if any(poly):raise ValueError('residual division')
 return out

def dense(rows,p):
 if not rows:return []
 a=[[x%p for x in v] for v in rows];k=0
 for j in range(len(a[0])):
  pivot=next((i for i in range(k,len(a)) if a[i][j]),None)
  if pivot is None:continue
  a[k],a[pivot]=a[pivot],a[k];s=pow(a[k][j],-1,p);a[k]=[x*s%p for x in a[k]]
  for i in range(len(a)):
   if i!=k and a[i][j]:
    s=a[i][j];a[i]=[(x-s*y)%p for x,y in zip(a[i],a[k])]
  k+=1
  if k==len(a):break
 return a[:k]

def equation(f,row):
 p,A,r=f['p'],f['a'],f['r'];z=None
 for e,atom in zip(row['coefficients'],f['factor_base']):
  # Signed reduction keeps public EC arithmetic short; no logarithm lookup.
  e=e if e<=r//2 else e-r;z=add(z,mul(e,tuple(atom['point']),p,A),p,A)
 if z!=mul(row['source_scalar'],tuple(f['P']),p,A):raise ValueError('false public source equation')
 return True

def witness(f,row):
 p,A,B,r=[f[k] for k in ['p','a','b','r']];points=[tuple(q) for q in row['constraints']]
 if row['curve_uid']!=f['uid'] or row['schema']!='prym-principal-row/v1':raise ValueError('row identity')
 if row['source_locator']!='explicit interpolation and residual quadratic; no post-hoc kernel':raise ValueError('source locator')
 if len(points)!=4 or len({q[0] for q in points})!=4:raise ValueError('constraint multiplicity')
 Q=neg(mul(row['source_scalar'],tuple(f['P']),p,A),p)
 if Q!=(points[0][0]**2%p,points[0][1]):raise ValueError('source lift label')
 v=interpol(points,p)
 if v!=row['v_coefficients']:raise ValueError('interpolation')
 if (v[3] if len(v)>3 else 0)**2%p==1 or row['pole_orders_at_infinity']!=[3,3]:raise ValueError('infinity divisor')
 q=quotient(v,points,f)
 if q!=row['residual_coefficients']:raise ValueError('residual coefficients')
 roots=row['residual_roots']
 if len(roots)!=2 or len(set(roots+[z[0] for z in points]))!=6 or any(pe(q,x,p) for x in roots):raise ValueError('intersection multiplicity')
 allpts=points+[(x,pe(v,x,p)) for x in roots];co=[0]*8
 for point,(j,sgn,op) in zip(points[1:],row['base_labels']):
  x,y=f['factor_base'][j]['lift']
  if sgn!=(-1 if op&1 else 1) or point!=((-x if op&2 else x)%p,sgn*y%p):raise ValueError('base sign label')
  co[j]+=sgn
 for x,y in allpts[4:]:
  found=[(j,s) for j,atom in enumerate(f['factor_base']) for s in [1,-1] if (x*x%p,y)==(atom['point'][0],s*atom['point'][1]%p)]
  if len(found)!=1:raise ValueError('residual base endpoint')
  j,s=found[0];co[j]+=s
 if [x%r for x in co]!=row['coefficients']:raise ValueError('witness coefficient')
 aux=None
 for x,y in allpts:
  if (y*y-pow(x,6,p)-A*x*x-B)%p:raise ValueError('point off C')
  if x:
   t=pow(x,-1,p);w=B*t*t%p;z=B*y*t**3%p
   if (z*z-w**3-A*w*w-B*B)%p:raise ValueError('auxiliary quotient equation')
   aux=add(aux,(w,z),p,0,A)
 # infinity poles3*(0,B)+3*(0,-B)=O, explicitly retained.
 pole=add(mul(3,(0,B%p),p,0,A),mul(3,(0,-B%p),p,0,A),p,0,A)
 if aux!=pole:raise ValueError('E2 full divisor norm')
 equation(f,row);return True

def schedule(f,cfg):
 import random
 src=list(range(1,65));random.Random(f"{cfg['domain']}|sources|{f['uid']}|0").shuffle(src)
 rng=random.Random(f"{cfg['domain']}|tuples|{f['uid']}|0")
 return src,{a:rng.sample(range(3584),64) for a in src}

def ident(f,a,tri,ops,pts):
 p,r=f['p'],f['r'];candidates=[]
 for dx,dy in itertools.product([1,-1],repeat=2):
  trans=[(dx*x%p,dy*y%p) for x,y in pts]
  labels=sorted([j,dy*(-1 if op&1 else 1),*point] for j,op,point in zip(tri,ops,trans[1:]))
  candidates.append(canon({'curve_uid':f['uid'],'source_scalar':dy*a%r,'lambda':1,'signed_fb_lift_ids':{'source_lift':trans[0],'base_lifts':labels}}))
 return sha(min(candidates))

def replay_cell(f,c,cfg,blocks):
 from collections import Counter
 p,r=f['p'],f['r'];src,samples=schedule(f,cfg);triples=list(itertools.combinations(range(8),3));roots={}
 for x in range(p):roots.setdefault(x*x%p,x)
 points_by_a={}
 for a in src:
  q=neg(mul(a,tuple(f['P']),p,f['a']),p)
  points_by_a[a]=None if q is None or q[0]==0 or q[0] not in roots else (roots[q[0]],q[1])
 seen=set();counts=Counter();attempt=0;accepted=[];attempts=[];digest_all=hashlib.sha256()
 for block_index,(a,block) in enumerate(zip(src,blocks)):
  if block['checkpoint']!=c['source_checkpoints'][block_index]:raise ValueError('checkpoint cross-artifact mismatch')
  if (block['curve_uid'],block['arm'],block['seed'],block['scalar'])!=(f['uid'],c['arm'],0,a):raise ValueError('source block order')
  branches=samples[a] if c['arm']=='sample64' else range(3584)
  if len(block['statuses'])!=len(branches):raise ValueError('missing attempted status')
  digest=hashlib.sha256()
  for off,b in enumerate(branches):
   attempt+=1;key=None;pts=None;status='S'
   if points_by_a[a] is not None:
    tri=triples[b//64];o=b%64;ops=(o//16,(o//4)%4,o%4);pts=[points_by_a[a]]
    for j,op in zip(tri,ops):
     x,y=f['factor_base'][j]['lift'];pts.append(((-x if op&2 else x)%p,(-y if op&1 else y)%p))
    status='D'
    if all(x for x,y in pts) and len({x for x,y in pts})==4:
     key=ident(f,a,tri,ops,pts)
     if key in seen:status='A'
     else:
      seen.add(key);v=interpol(pts,p);lead=v[3] if len(v)>3 else 0;status='P'
      if lead*lead%p!=1:
       q=quotient(v,pts,f);disc=(q[1]**2-4*q[0]*q[2])%p;status='R'
       if q[2] and disc and disc in roots:
        inv=pow(2*q[2],-1,p);rr=sorted([(-q[1]-roots[disc])*inv%p,(-q[1]+roots[disc])*inv%p]);status='X'
        if len(set(rr+[x for x,y in pts]))==6:
         co=[0]*8
         for j,op in zip(tri,ops):co[j]+=(-1 if op&1 else 1)
         status='+'
         for x in rr:
          y=pe(v,x,p);matches=[(j,s) for j,atom in enumerate(f['factor_base']) for s in [1,-1] if (x*x%p,y)==(atom['point'][0],s*atom['point'][1]%p)]
          if len(matches)!=1:status='B';break
          j,s=matches[0];co[j]+=s
         if status=='+':
          row=c['rows'][len(accepted)]
          if row['source_scalar']!=a or row['coefficients']!=[x%r for x in co] or row['constraints']!=[list(z) for z in pts] or row['v_coefficients']!=v or row['residual_roots']!=rr or row['residual_coefficients']!=q:raise ValueError('accepted row replay')
          accepted.append(row);attempts.append(attempt)
   if status!=block['statuses'][off]:raise ValueError(f'attempt outcome {attempt}: expected {status}, stored {block["statuses"][off]}')
   digest.update(json.dumps([a,b,key,status],separators=(',',':')).encode()+b'\n');counts[status]+=1
  if digest.hexdigest()!=block['attempt_digest']:raise ValueError('attempt digest')
  digest_all.update(digest.digest())
  cp=block['checkpoint']
  if (cp['source_scalar'],cp['attempt'],cp['accepted_rows'])!=(a,attempt,len(accepted)):raise ValueError('block checkpoint')
 if attempts!=c['row_attempts'] or len(accepted)!=len(c['rows']) or attempt!=c['attempts'] or counts!=Counter(c['reasons']) or len(seen)!=c['distinct_candidates']:raise ValueError('finite coverage totals')
 return {'attempts':attempt,'accepted':len(accepted),'reasons':dict(counts),'canonical_candidates':len(seen),'source_blocks':len(blocks),'block_digest_chain':digest_all.hexdigest()}

def matrix(f,c,blind):
 p=f['r'];mapping=blind['native_projection'];known={j:v['scalar'] for j,v in enumerate(mapping) if v['kind']=='known'};unknown=[j for j,v in enumerate(mapping) if v['kind']=='unknown'];U=blind['U']
 pr=c['projection'];declared={v['column']:v['scalar'] for v in pr['public_derivations']}
 if pr['U']!=U or declared!=known or pr['unknown_columns']!=unknown:raise ValueError('projected U or public anchor map')
 for d in pr['public_derivations']:
  a=d['derived_from_public_source_scalar'];sgn=d['sign']
  if not 1<=a<=64 or sgn*a%p!=d['scalar'] or mul(a,tuple(f['P']),f['p'],f['a'])!=mul(sgn,tuple(f['factor_base'][d['column']]['point']),f['p'],f['a']):raise ValueError('public derivation')
 M=[];aug=[];basis=[];progress=[];ind=[]
 for i,row in enumerate(c['rows']):
  equation(f,row);v=[row['coefficients'][j] for j in unknown];b=(row['source_scalar']-sum(row['coefficients'][j]*k for j,k in known.items()))%p
  M.append(v);aug.append(v+[b]);new=dense(basis+[v],p)
  if len(new)>len(basis):basis=new;progress.append((c['row_attempts'][i],i+1,len(new)));ind.append(i)
 rank=len(dense(M,p));arank=len(dense(aug,p))
 if (pr['rank'],pr['augmented_rank'])!=(rank,arank):raise ValueError('rank or augmented rank')
 if pr['independent_row_indices']!=ind or progress!=[(q['attempt'],q['accepted_rows'],q['rank']) for q in c['rank_progress']]:raise ValueError('rank progression')
 first=next((q for q in progress if U and q[2]==U),None);stored=c['first_full_rank']
 if first!=(tuple(stored[k] for k in ['attempt','accepted_rows','rank']) if stored else None):raise ValueError('first full rank')
 kernel=c['nullspace']
 if len(kernel)!=U-rank or any(len(v)!=U for v in kernel) or len(dense(kernel,p))!=U-rank or any(sum(x*y for x,y in zip(v,z))%p for v in M for z in kernel):raise ValueError('right kernel')
 piv=[pr['pivots'][k] for k in sorted(pr['pivots'],key=int)]
 if len(piv)!=rank or dense(piv,p)!=dense(aug,p):raise ValueError('pivot certificate')
 for k,v in pr['pivots'].items():
  j=int(k)
  if v[j]!=1 or any(v[:j]):raise ValueError('pivot location')
 if pr['solution'] is not None:
  if len(pr['solution'])!=U or any(sum(x*y for x,y in zip(v,pr['solution']))%p!=z[-1] for v,z in zip(M,aug)):raise ValueError('solution')
 elif rank==U:raise ValueError('missing full-rank solution')
 for cp in c['source_checkpoints']:
  n=cp['accepted_rows']
  if len(dense(M[:n],p))!=cp['rank']:raise ValueError('checkpoint rank')
 return {'U':U,'rank':rank,'augmented_rank':arank,'kernel_dimension':len(kernel),'first_full_rank':list(first) if first else None,'equations_checked':len(M)}

def expect_reject(name,mutated,check):
 try:check(mutated)
 except Exception as e:return {'control':name,'rejected':True,'rejection':str(e),'mutation':mutated}
 raise AssertionError('mutation falsely accepted: '+name)

def phase2():
 import os,time,copy,random,subprocess,yaml,gzip
 os.environ['CRYPTO_AR_BLOB_CACHE']='/tmp/prym-native-blob-cache'
 sys.path.insert(0,str(ROOT));from tools.artifact_store import read_bytes,resolve
 started=time.time();cfg=readj(FROZEN+'config.json');panel=readj(FROZEN+'fixtures.json');blind=readj(str(OUT.relative_to(ROOT)/'blinded-input-derivation.json'))
 run=ROOT/'experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6';delivery=run.parents[1]/'artifact-deliveries/RUN-ECDLP-ea49a6'
 rb=read_bytes(run/'raw-result.json');eb=read_bytes(run/'events.jsonl');result=json.loads(rb);blocks=list(map(json.loads,eb.splitlines()))
 expected=[(f['uid'],0,arm) for f in panel['fixtures'] for arm in cfg['arms']]
 assert [(c['curve_uid'],c['seed'],c['arm']) for c in result['cells']]==expected
 assert result['complete'] and not result['secret_labels_present'] and result['config_sha256']==sha((ROOT/(FROZEN+'config.json')).read_bytes())
 cells=[];sample_audits=[]
 for ci,c in enumerate(result['cells']):
  f=panel['fixtures'][ci//2];b=blind['fixtures'][ci//2]
  # Exact native and EC1 hashes implemented from their declared canonical JSON.
  assert sha(canon({k:f[k] for k in ['p','a','b','r','P','factor_base']}))==f['uid']
  ec=f['ec1'];ecsha=sha(canon({'field':ec['field'],'curve':{k:v for k,v in ec['curve'].items() if k!='curve_id'}}))
  assert ecsha==ec['curve_sha256'] and ec['curve_uid']=='urn:ec-record:1:sha256:'+ecsha and ec['field_sha256']==sha(canon(ec['field'])) and ec['curve_id']==f"EC1P{f['p'].bit_length()}Cprymtoyh{ecsha[:12]}"
  cov=replay_cell(f,c,cfg,blocks[ci*64:(ci+1)*64]);met=matrix(f,c,b)
  n=len(c['rows']);idx=set(range(min(4,n)))|set(range(max(0,n-4),n))
  if n<16:idx=set(range(n))
  else:
   ranked=sorted(range(n),key=lambda i:sha(canon({'domain':'TASK-20261025-5145ac-principal-v1','cell':list(expected[ci]),'index':i,'row':c['rows'][i]})))
   idx.update(ranked[:8])
  for i in sorted(idx):witness(f,c['rows'][i])
  # Every A/A transported witness hash is checked without importing transport code.
  perm=list(range(8));random.Random('prym-W-reencode-v1|0').shuffle(perm);inv={old:new for new,old in enumerate(perm)}
  for i,row in enumerate(c['rows']):
   trans=copy.deepcopy(row);trans['coefficients']=[row['coefficients'][j] for j in perm];trans['base_labels']=[[inv[j],s,o] for j,s,o in row['base_labels']]
   assert sha(canon(trans))==c['transported_witness_hashes'][i]
  rec={'p':f['p'],'B':f['b'],'curve_uid':f['uid'],'arm':c['arm'],**cov,**met,'principal_E2_sample_indices':sorted(idx),'principal_E2_checked':len(idx),'all_AA_hashes_checked':n}
  cells.append(rec);print('cell',ci,f['p'],f['b'],c['arm'],cov['attempts'],n,met['rank'],'/',met['U'],flush=True)
 assert len(blocks)==1024 and sum(c['attempts'] for c in cells)==1867776
 nesting=[]
 for i,f in enumerate(panel['fixtures']):
  s,t=result['cells'][2*i:2*i+2];r=f['r']
  def equations(c):return {min(tuple(v['coefficients']+[v['source_scalar']]),tuple(-x%r for x in v['coefficients']+[v['source_scalar']])) for v in c['rows']}
  S,T=equations(s),equations(t);assert S<=T and cells[2*i]['rank']<=cells[2*i+1]['rank']
  nesting.append({'p':f['p'],'B':f['b'],'sample_unique_equations':len(S),'full_unique_equations':len(T),'sample_in_full':True})
 # Native custody: no remote GET is attempted; local cache bytes independently rehashed.
 receipt=json.loads((run/'execution-receipt.json').read_text());cust=json.loads((delivery/'custody.json').read_text());manifest=yaml.safe_load((run/'manifest.yaml').read_text())['run'];env=json.loads((run/'environment.json').read_text());launch=json.loads((run/'launch.json').read_text());plan=readj('experiments/EXP-ECDLP-d6d8e8/trial-plan.json');spec=yaml.safe_load((ROOT/SPEC).read_text())['experiment']
 artifact_checks=[]
 for name,digest in receipt['artifact_sha256'].items():
  data=read_bytes(run/name);forms=[p for p in [run/name,run/(name+'.gz'),run/(name+'.gz.blob.json')] if p.exists()];assert len(forms)==1 and sha(data)==digest
  artifact_checks.append({'logical':name,'stored_path':str(forms[0].relative_to(ROOT)),'content_sha256':digest,'bytes':len(data),'stored_file_sha256':sha(forms[0].read_bytes())})
 assert cust['artifact_sha256']==receipt['artifact_sha256'] and cust['artifact_storage']==receipt['artifact_storage'] and cust['execution_receipt_sha256']==sha((run/'execution-receipt.json').read_bytes())
 am=json.loads((delivery/'.artifacts.json').read_text());ptrchecks=[]
 for name,storage in receipt['artifact_storage'].items():
  ptr=json.loads((run/storage['path']).read_text());assert all(ptr[k]==storage[k] for k in ptr if k!='schema')
  cached=Path('/tmp/prym-native-blob-cache')/'sha256'/ptr['sha256'][:2]/ptr['sha256'];assert cached.exists()
  stored=cached.read_bytes();raw=gzip.decompress(stored)
  assert sha(stored)==ptr['sha256'] and len(stored)==ptr['size'] and sha(raw)==ptr['content_sha256'] and len(raw)==ptr['content_size']
  assert am['files'][ptr['sha256']+'.bin']=={'sha256':ptr['sha256'],'bytes':ptr['size']}
  obj=next(x for x in cust['objects'] if x['sha256']==ptr['sha256']);assert obj['uri']==ptr['uri'] and obj['bytes']==ptr['size']
  assert ptr['uri']==f"s3://setec-astronomy-artifacts/store/sha256/{ptr['sha256'][:2]}/{ptr['sha256']}"
  ptrchecks.append({'logical':name,'stored_sha256':ptr['sha256'],'content_sha256':ptr['content_sha256'],'stored_bytes':len(stored),'raw_bytes':len(raw),'own_cached_readback':True,'own_remote_GET':False})
 assert receipt['status']=='output_validated' and receipt['returncode']==receipt['check_returncode']==0
 assert receipt['authority']==launch['authority'] and receipt['plan_sha256']==sha((ROOT/'experiments/EXP-ECDLP-d6d8e8/trial-plan.json').read_bytes())
 assert env['commit']==manifest['code']['commit']==receipt['authority']['commit'] and manifest['code']['dirty_tree']==''
 assert env['specification_sha256']==manifest['inputs']['specification_sha256']==sha((ROOT/SPEC).read_bytes())
 assert plan['source_sha256']==env['source_sha256']==manifest['code']['source_sha256'] and plan['input_sha256']==manifest['inputs']['sha256']
 boundchecks=[]
 for path,digest in {**plan['source_sha256'],**plan['input_sha256']}.items():
  actual=sha((ROOT/path).read_bytes());gitbytes=subprocess.check_output(['git','show',receipt['authority']['commit']+':'+path],cwd=ROOT)
  assert actual==digest==sha(gitbytes)
  assert spec['input_bindings'][path]['sha256']==digest
  boundchecks.append({'path':path,'sha256':digest,'committed_source_matches':True})
 assert plan['specification_sha256']==sha((ROOT/SPEC).read_bytes())
 claimpath='coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/claims/TASK-20261025-e5efb3.1.claim.json';claim=readj(claimpath)
 claimbytes=subprocess.check_output(['git','show',receipt['authority']['commit']+':'+claimpath],cwd=ROOT);assert json.loads(claimbytes)==claim
 # Fresh checks deliberately reject actual-item mutations. Copies live in verification only.
 f=panel['fixtures'][0];row=copy.deepcopy(result['cells'][0]['rows'][0]);row['source_scalar']=(row['source_scalar']+1)%f['r']
 controls=[expect_reject('false_scalar_a_plus_one',row,lambda x:equation(f,x))]
 ci=4;c=copy.deepcopy(result['cells'][ci]);c['projection']['U']+=1
 controls.append(expect_reject('altered_projected_U',{'cell_index':ci,'changed_U':c['projection']['U']},lambda _:matrix(panel['fixtures'][ci//2],c,blind['fixtures'][ci//2])))
 c=copy.deepcopy(result['cells'][ci]);pk=next(iter(c['projection']['pivots']));c['projection']['pivots'][pk][int(pk)]=(c['projection']['pivots'][pk][int(pk)]+1)%panel['fixtures'][ci//2]['r']
 controls.append(expect_reject('altered_pivot',{'cell_index':ci,'pivot':pk,'changed':c['projection']['pivots'][pk]},lambda _:matrix(panel['fixtures'][ci//2],c,blind['fixtures'][ci//2])))
 block=copy.deepcopy(blocks[0]);block['statuses']=block['statuses'][:-1]
 controls.append(expect_reject('missing_attempt_status',block,lambda x:replay_cell(panel['fixtures'][0],result['cells'][0],cfg,[x]+blocks[1:64])))
 ptr=json.loads((run/'raw-result.json.gz.blob.json').read_text());ptr['content_sha256']='0'+ptr['content_sha256'][1:] if ptr['content_sha256'][0]!='0' else '1'+ptr['content_sha256'][1:]
 def checkptr(x):
  data=gzip.decompress((Path('/tmp/prym-native-blob-cache')/'sha256'/x['sha256'][:2]/x['sha256']).read_bytes())
  if sha(data)!=x['content_sha256']:raise ValueError('raw content digest mismatch')
 controls.append(expect_reject('changed_raw_digest',ptr,checkptr))
 ptr2=copy.deepcopy(ptr);ptr2['content_sha256']=receipt['artifact_storage']['raw-result.json']['content_sha256'];ptr2['sha256']='0'*64
 def checkstored(x):
  rawptr=receipt['artifact_storage']['raw-result.json'];data=(Path('/tmp/prym-native-blob-cache')/'sha256'/rawptr['sha256'][:2]/rawptr['sha256']).read_bytes()
  if sha(data)!=x['sha256']:raise ValueError('stored digest mismatch')
 controls.append(expect_reject('changed_stored_digest',ptr2,checkstored))
 f=panel['fixtures'][0];good=copy.deepcopy(result['cells'][0]['rows'][0]);assert witness(f,good)
 for name,mut in [('missing_infinity_term',lambda q:q.update(pole_orders_at_infinity=[3,0])),('malformed_multiplicity',lambda q:q.update(residual_roots=[q['residual_roots'][0]]*2)),('wrong_sign',lambda q:q['base_labels'][0].__setitem__(1,-q['base_labels'][0][1]))]:
  q=copy.deepcopy(good);mut(q);controls.append(expect_reject(name,q,lambda x:witness(f,x)))
 oldverify=json.loads((run/'verification.json').read_text());assert oldverify['status']=='passed' and oldverify['raw_result_sha256']==sha(rb)
 outcome={'schema':'prym-observation-independent-verification/v1','task_id':'TASK-20261025-5145ac','run_id':'RUN-ECDLP-ea49a6','started_at':datetime.datetime.fromtimestamp(started,datetime.timezone.utc).isoformat(),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'review_wall_seconds':time.time()-started,'blind_seal_sha256':sha((OUT/'blinded-input-derivation.json').read_bytes()),'raw_result_sha256':sha(rb),'events_sha256':sha(eb),'cells':cells,'nested_support':nesting,'artifact_checks':artifact_checks,'pointer_checks':ptrchecks,'source_binding_checks':boundchecks,'native_claim':claim,'negative_mutation_controls':controls,'inherited_controls':result['controls'],'borrowed_validation':{'existing_checker_receipt_read':True,'existing_checker_status':oldverify['status'],'fresh_checker_replay_by_this_reviewer':False,'role':'corroborating existing software validation; not blind derivation or independent fresh code'},'complete_attempts':sum(c['attempts'] for c in cells),'all_E1_equations':sum(c['accepted'] for c in cells),'sampled_principal_E2_witnesses':sum(c['principal_E2_checked'] for c in cells),'native_receipt_sha256':sha((run/'execution-receipt.json').read_bytes()),'custody_sha256':sha((delivery/'custody.json').read_bytes()),'operation_counters_independently_recomputed':False,'prescribed_execution_proof':False,'complete_weighted_S':False}
 dump(OUT/'verification.json',outcome);print('VERIFIED',outcome['all_E1_equations'],outcome['sampled_principal_E2_witnesses'],flush=True)
if __name__=='__main__' and sys.argv[-1]=='phase2':phase2()

def finish():
 import os,copy,subprocess,yaml
 from xml.sax.saxutils import escape
 from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
 from reportlab.lib.styles import getSampleStyleSheet
 from reportlab.lib import colors
 from reportlab.graphics.shapes import Drawing,Rect,String,Line
 from reportlab.graphics import renderSVG
 os.environ['CRYPTO_AR_BLOB_CACHE']='/tmp/prym-native-blob-cache'
 sys.path.insert(0,str(ROOT));from tools.artifact_store import read_bytes,resolve
 V=json.loads((OUT/'verification.json').read_text());blind=json.loads((OUT/'blinded-input-derivation.json').read_text());panel=readj(FROZEN+'fixtures.json');cfg=readj(FROZEN+'config.json')
 run=ROOT/'experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6';result=json.loads(read_bytes(run/'raw-result.json'));receipt=readj(str((run/'execution-receipt.json').relative_to(ROOT)));manifest=yaml.safe_load((run/'manifest.yaml').read_text())['run'];oldverify=readj(str((run/'verification.json').relative_to(ROOT)))
 archivepath='coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/archives/TASK-20261025-5de6df.json';archive=readj(archivepath);archives=[]
 for logical,digest in archive['source_path_sha256'].items():
  path=resolve(ROOT/logical);assert path and sha(path.read_bytes())==digest
  stored=path.relative_to(ROOT).as_posix();commitbytes=subprocess.check_output(['git','show','a6fe1b471:'+stored],cwd=ROOT);assert sha(commitbytes)==digest
  archives.append({'logical':logical,'stored':stored,'stored_sha256':digest,'snapshot_matches':True})
 # The archive file itself is the twentieth snapshot logical path.
 assert subprocess.check_output(['git','show','a6fe1b471:'+archivepath],cwd=ROOT)==(ROOT/archivepath).read_bytes()
 V['raw_snapshot_check']={'commit':'a6fe1b471','logical_artifacts':len(archives),'plus_archive_record':1,'checks':archives,'archive_sha256':sha((ROOT/archivepath).read_bytes())}
 decision=readj('experiments/EXP-ECDLP-d6d8e8/packaging/admission-20261025/preapproval.json');dec=yaml.safe_load((ROOT/'ledger/decisions/DEC-20261025-1bd76a.yaml').read_text())['coordinator_decision']
 assert decision['approvable'] and not decision['blockers'] and decision['prospective_sha256']==dec['prospective_sha256']
 prechecks=[]
 for key,p in decision['canonical_paths'].items():
  # Queue has legitimate later dispatch updates; compare prospective committed source snapshot.
  data=subprocess.check_output(['git','show',receipt['authority']['commit']+':'+p],cwd=ROOT)
  assert sha(data)==decision['prospective_sha256'][key]
  prechecks.append({'kind':key,'path':p,'sha256':sha(data),'committed_matches':True})
 V['preapproval_binding_checks']=prechecks
 # Full permutation equation transport, independently checked after hash replay.
 import random
 perm=list(range(8));random.Random('prym-W-reencode-v1|0').shuffle(perm)
 for ci,c in enumerate(result['cells']):
  f=copy.deepcopy(panel['fixtures'][ci//2]);f['factor_base']=[f['factor_base'][j] for j in perm]
  for row in c['rows']:
   q=copy.deepcopy(row);q['coefficients']=[row['coefficients'][j] for j in perm];equation(f,q)
 V['AA_transported_E1_equations_checked']=V['all_E1_equations']
 # Independent synthetic normal-form/rank controls, no scientific sampling.
 def project_synthetic(points,public,p):
  normals=[];mapping=[]
  for q in points:
   n=norm(q,p)
   if n is None:mapping.append(('zero',0))
   elif n in public:mapping.append(('known',public[n]*(1 if n==q else -1)))
   else:
    if n not in normals:normals.append(n)
    mapping.append(('unknown',normals.index(n),1 if n==q else -1))
  return len(normals),mapping
 pp=101;Q=(1,23);Z=(36,17)
 synU,synmap=project_synthetic([None,Q,neg(Q,pp),Q,Z],{norm(Z,pp):7},pp)
 assert synU==1 and synmap==[('zero',0),('unknown',0,1),('unknown',0,-1),('unknown',0,1),('known',7)]
 assert project_synthetic([Q,neg(Q,pp)],{norm(Q,pp):3},pp)[0]==0
 assert len(dense([[0,0],[1,2],[2,4]],107))==1
 V['additional_positive_controls']=[{'control':'valid_recorded_principal_divisor','passed':True},{'control':'duplicate_sign_zero_columns','U':synU,'mapping':synmap,'passed':True},{'control':'all_public_U_zero','passed':True},{'control':'dependent_and_zero_row_rank','expected_rank':1,'passed':True}]
 V['negative_mutation_controls']=[x for x in V['negative_mutation_controls'] if x['control'] not in ['post_hoc_locator','unknown_tuple_source']]
 for label,locator in [('post_hoc_locator','post-hoc residue'),('unknown_tuple_source','unknown tuple scalar')]:
  f=panel['fixtures'][0];q=copy.deepcopy(result['cells'][0]['rows'][0]);q['source_locator']=locator
  V['negative_mutation_controls'].append(expect_reject(label,q,lambda x:witness(f,x)))
 V['review_execution_notes']=['First fresh replay checked all 16 cells; its custody stage stopped on a reviewer-only cache path assumption. Corrected cache layout to sha256/<prefix>/<digest>, repeated complete checks successfully. No immutable input or output changed.','Exact UID/EC1 serialization checks were deferred until phase2; phase1 independently checked numerical EC1 fields and mathematical identities.','No producer or existing checker arithmetic imported; tools.artifact_store is used only for transport.','Existing generic independence checker has an all-session blind_from intersection check and cannot represent this same-task phase1-seal-phase2 plan. Its exact diagnostic is retained below after checker invocation.']
 V['resource_and_cost_scope']={'producer_wall_seconds':manifest['timing']['wall_seconds'],'producer_cpu_seconds':manifest['timing']['cpu_seconds'],'producer_peak_self_RSS_bytes':manifest['timing']['producer_peak_rss_bytes'],'existing_checker_wall_seconds':oldverify['wall_seconds'],'existing_checker_cpu_seconds':oldverify['cpu_seconds'],'existing_checker_peak_self_RSS_bytes':oldverify['peak_rss_bytes'],'input_search_records':len(panel['search_trace']),'input_search_matches':result['input_construction_costs']==panel['search_trace'],'collector_counter_names':sorted({k for c in result['cells'] for k in c['attack_operation_vector']}),'exclusions':['pow internals','Python bookkeeping','comparison/enumeration/serialization overhead not exhaustively metered','byte movement','independent verification work in collector vector','storage work has custody outcomes but no separate comprehensive timed/counted ledger','process-group peak RSS and peak live algebraic words/table entries not supplied'],'consequence':'Partial operation vectors and diagnostic times; no complete weighted S, complete construction cost, prescribed-computation proof or settlement.'}
 assert V['resource_and_cost_scope']['input_search_matches']
 dump(OUT/'verification.json',V)
 joints=['fixture_public_source_projection','complete_support_and_alias_law','source_witness_and_exact_rank','native_custody_and_cost_scope']
 limitations=['Finite panel of eight deterministically selected toy curves over four prime fields; seed0 is ordering nuisance, not an independent curve.','Explicit full principal-divisor/E2 audit covers 144 deterministic accepted rows; every 4257 accepted interpolation/residual/row and E1 equation is replayed. Existing native checker reports every principal witness verified; that receipt is borrowed corroboration.','Own custody readback is from the public cache only. The immutable producer/custody records assert fresh remote GET; no independent reviewer remote GET or remote availability conclusion is supplied.','Operation counters were not independently recomputed; input search/checker/storage costs remain separately scoped, with no complete weighted S or execution proof.','UID/EC1 exact hash serialization checked after blind seal; mathematical input/order/base/public projection derived before unblinding.','Generic independence checker cannot represent this exact same-task phased blind plan; report retains complete source disclosure and diagnostic rather than claiming its static whole-session gate passed.']
 observations=[
 {'joint':joints[0],'verdict':'holds','checked_scope':'Eight fixture order/prime/generator/base recounts and all 64 declared public images each, signed canonical anchor maps/U; UID/EC1 numerical identity before seal, exact serialization hashes after seal.','observations':'U=[0,0,2,3,4,3,7,7]; identical projection in both arms; no truth-log table computed.','limits':['Exact identity serialization deliberately deferred to phase2.']},
 {'joint':joints[1],'verdict':'holds','checked_scope':'All 1024 ordered source blocks and 1,867,776 descriptors; fresh lift/rejection/alias/interpolation/residual/acceptance outcome and attempt-digest regeneration; all A/A witness hashes and transported E1 equations; sampled canonical equations nested in full up to global sign.','observations':'All stored outcomes, source checkpoints, candidate counts and accepted row locations match. No rejected work omitted; all fixed work continues beyond first full rank.','limits':['Canonicalizer implements the declared finite geometric deck/hyperelliptic orbit, not a global equivalence theorem.']},
 {'joint':joints[2],'verdict':'holds','checked_scope':'All 4257 public E1 equations and 16 matrices/rank/augmented rank/pivots/solutions/right-kernel/progress/first-full certificates; 144 fixed principal/E2 witness samples (first 4,last 4,SHA-ranked 8,deduplicated; all below 16).','observations':'Exact matrix values match stored results; full ranks by fixture 0,0,2,3,4,3,0,0 versus U 0,0,2,3,4,3,7,7.','limits':['Explicit E2 norm and full principal witness check is the preregistered deterministic sample, not every accepted row.']},
 {'joint':joints[3],'verdict':'holds','checked_scope':'Approved spec/plan/source/input committed bindings, native claim/source/clean-tree receipt state,19 logical outputs plus archive record, native two-pointer/stored/raw hashes and canonical manifest/custody, own cache readback, partial-counter scope.','observations':'Committed snapshot bytes and every digest bridge match; all 20 logical snapshot paths accounted. Source commit reachable in cached origin/lane/prym-census-run and origin/lane/prym-rank-census refs. Native published:false is recorded runner publication state; archival commits supply durable bytes.','limits':['Own remote GET and independent operation-counter recomputation not performed.','No complete weighted S, process-group memory trace, prescribed-computation proof or settlement.']}
 ]
 # Sources actually read include bytes hashed and committed snapshots inspected.
 admin=['AGENTS.md','agents/validator.md','docs/lab-contract.md','docs/agent-contract-extended.md','.claude/skills/research-visuals/SKILL.md','templates/research-records.md','ledger/handoffs/TASK-20261025-5145ac.yaml','ledger/decisions/DEC-20261025-1bd76a.yaml','tools/check_review_independence.py','tools/allocate_id.py','coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/dispatch_queue.json','coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/publication-checks.json',archivepath,'coordination/goals/GOAL-ECDLP-001/batches/BATCH-a00184/claims/TASK-20261025-e5efb3.1.claim.json','experiments/EXP-ECDLP-d6d8e8/trial-plan.json','experiments/EXP-ECDLP-d6d8e8/packaging/admission-20261025/preapproval.json','experiments/EXP-ECDLP-d6d8e8/packaging/admission-20261025/prospective-handoff.yaml','ledger/handoffs/TASK-20261025-e5efb3.yaml']
 paths=set(admin+blind['allowed_scientific_sources']+[x['path'] for x in V['source_binding_checks']])
 paths.update(str(p.relative_to(ROOT)) for p in run.iterdir() if p.is_file())
 paths.update(str(p.relative_to(ROOT)) for p in (run.parents[1]/'artifact-deliveries/RUN-ECDLP-ea49a6').iterdir() if p.is_file())
 paths.update(str(run.relative_to(ROOT)/p) for p in ['raw-result.json','events.jsonl'])
 att={'task_id':'TASK-20261025-5145ac','joints_owned':joints,'sources_read':sorted(paths),'read_sibling_reports':False,'blind_from_respected':True,'blind_from_respected_scope':'Phase1 only, through sealed_at and the published blind artifact hash. Phase2 sources deliberately unblinded exactly as this handoff permits. This boolean does not mean no protected path was ever read during phase2.','phase1_sources_read':blind['allowed_scientific_sources'],'phase1_sealed_at':blind['sealed_at'],'phase1_sha256':V['blind_seal_sha256'],'separate_session':True,'producer_authorship':False,'unblinding_order':'After blinded-input-derivation.json was written, hashed, and its timestamp/hash messaged to Coordinator, before reading result/source. Exact first-read timestamp not independently captured.','verdict':'holds','verdict_scope':'Assigned observation-integrity joints only, with stated deterministic witness sample and custody/cost limitations.'}
 report={'schema':'prym-observation-integrity-review/v1','task_id':'TASK-20261025-5145ac','run_ids':['RUN-ECDLP-ea49a6'],'experiment_id':'EXP-ECDLP-d6d8e8','archived_by':'TASK-20261025-50defd','finding_scope':'Observation integrity only; no scientific hypothesis verdict or state transition.','per_joint_findings':observations,'limitations':limitations,'procedure_deviations':[{'kind':'timing_scope','description':'Exact native UID/EC1 hash serialization was checked in phase2; phase1 numerical EC1/arithmetic/projection checks were independent.'},{'kind':'tool_representation_gap','description':'Static independence checker applies blind_from to union of phase1+phase2 reads despite plan permission. All reads are disclosed; no whole-session blindness is asserted.'}],'visuals':{'source':'graph-source.json','rendering':'graph.svg','canonical_graph_update':'No external canonical graph changed: no scientific decision or new relationship is authorized; only finite review data are graphed.'},'validation_report':{'id':'TASK-20261025-5145ac-observation-integrity','task_id':'TASK-20261025-5145ac','run_ids':['RUN-ECDLP-ea49a6'],'artifact_checks':V['artifact_checks'],'metric_recomputations':V['cells'],'control_checks':V['negative_mutation_controls']+V['additional_positive_controls'],'heuristic_validation_checks':[],'cost_model_checks':[V['resource_and_cost_scope']],'proof_architecture_checks':[{'execution_proof':False,'complete_weighted_S':False}],'verdict':'passed','verdict_scope':'Assigned checks and deterministic witness sample only; not a scientific verdict.','limitations':limitations,'artifact_paths':[str((OUT/p).relative_to(ROOT)) for p in ['blinded-input-derivation.json','review.py','verification.json','report.json','report.md','graph-source.json','graph.svg','report.pdf']]},'review_attestation':att}
 graph={'schema':'prym-observation-review-graph/v1','run_id':'RUN-ECDLP-ea49a6','task_id':'TASK-20261025-5145ac','data_source':'verification.json','quantity':'Exact projected matrix rank modulo each prime r; U after public anchors','units':'rank dimensions','sample_size':{'fixtures':8,'arms':2,'attempts':1867776},'uncertainty':'Exact finite census/recomputation; no population confidence interval.','cells':[{k:c[k] for k in ['p','B','arm','accepted','U','rank','augmented_rank']} for c in V['cells']]}
 dump(OUT/'graph-source.json',graph)
 drawing=Drawing(475,220)
 drawing.add(String(0,207,'Exact projected rank after public anchors',fontSize=12))
 for i in range(8):
  s,t=V['cells'][2*i:2*i+2];x=34+i*54;scale=17
  for dx,c,col in [(0,s,'#2666a4'),(15,t,'#e78a29')]:
   drawing.add(Rect(x+dx,58,11,c['U']*scale,fillColor=colors.HexColor('#e1e5e9'),strokeWidth=0))
   drawing.add(Rect(x+dx,58,11,c['rank']*scale,fillColor=colors.HexColor(col),strokeWidth=0))
   drawing.add(String(x+dx,44,str(c['rank']),fontSize=8))
  drawing.add(String(x-6,29,f"{s['p']}/{s['B']}",fontSize=7));drawing.add(String(x-3,17,'U='+str(s['U']),fontSize=7))
 for j in range(8):drawing.add(String(12,56+j*17,str(j),fontSize=7))
 drawing.add(Line(27,58,465,58,strokeColor=colors.gray,strokeWidth=.5))
 drawing.add(String(34,192,'Blue: sample64; orange: full3584; grey: U. Exact dimensions, n=8 fixtures.',fontSize=8))
 drawing.add(String(34,3,'Labels p/B; sources a=1..64, seed0. RUN-ECDLP-ea49a6.',fontSize=8))
 renderSVG.drawToFile(drawing,str(OUT/'graph.svg'))
 report['component_sha256']={p:sha((OUT/p).read_bytes()) for p in ['blinded-input-derivation.json','review.py','verification.json','graph-source.json','graph.svg']}
 dump(OUT/'report.json',report)
 md=['# Observation integrity review — TASK-20261025-5145ac','', 'EXP-ECDLP-d6d8e8 / RUN-ECDLP-ea49a6. Assigned-joint integrity findings only; no scientific verdict or state transition.','',f"Blind input derivation sealed {blind['sealed_at']}; SHA256 `{V['blind_seal_sha256']}`. Only approved specification/config/fixtures supplied mathematical inputs before deliberate unblinding.",'',f"Fresh code replayed **{V['complete_attempts']:,} attempts**, **{V['all_E1_equations']:,} E1 equations**, every matrix certificate in 16 cells, and the fixed sample of **{V['sampled_principal_E2_witnesses']} principal/E2 witnesses**. The stored statuses, digests, row positions, nested support, projection, rank/augmented rank, kernels, pivots and checkpoints match. Nine core mutations plus two locator mutations reject as expected.",'','| p | B | r | U | sample rows | full rows | sample rank | full rank |','|---:|---:|---:|---:|---:|---:|---:|---:|']
 for i,f in enumerate(panel['fixtures']):
  s,t=V['cells'][2*i:2*i+2];md.append(f"| {f['p']} | {f['b']} | {f['r']} | {s['U']} | {s['accepted']} | {t['accepted']} | {s['rank']} | {t['rank']} |")
 md+=['','![Exact recomputed ranks](graph.svg)','','All counts/ranks above are independently derived from the finite receipts. Seeds describe ordering only; U=0 cells remain all-public calibration.']
 for finding in observations:md+=['',f"**{finding['joint']}: {finding['verdict']}.** {finding['checked_scope']} {finding['observations']} Limits: "+' '.join(finding['limits'])]
 md+=['','**Custody and cost scope.** The reviewer rehashed both public cache objects, decompressed raw content, verified pointer/stored/raw SHA bridges, canonical .artifacts metadata, custody and snapshot bytes. Producer fresh remote GET claims remain producer evidence. Producer diagnostics: '+str(manifest['timing']['wall_seconds'])+' wall seconds, '+str(manifest['timing']['cpu_seconds'])+' CPU seconds, '+str(manifest['timing']['producer_peak_rss_bytes'])+' peak self RSS bytes. Existing checker: '+str(oldverify['wall_seconds'])+' wall seconds. Input search is separately retained. Storage has delivery/readback outcomes, without complete work/timing accounting. Counters exclude pow internals, Python bookkeeping, byte movement and verifier work; operation counts were not independently recomputed. No complete weighted S, process-group memory trace or prescribed-computation proof is supplied.','','**Controls.** `verification.json` retains exact mutated copies, item locations and rejection text. Valid principal witness; duplicate/sign/zero projection; all-public U=0; and dependent/zero-row rank controls pass. Inherited 11 planted controls match their declared outcomes; the existing checker receipt is borrowed corroboration.','', '**Method limits and deviations.**']
 md+=['- '+x for x in limitations]
 md+=['','First reviewer replay completed all cells before a cache-path assumption stopped custody checks; correcting the reviewer path and repeating succeeded. No immutable artifact changed. The generic independence check cannot encode this same-task staged plan; exact diagnostics are recorded in report.json. No sibling report, credential file/value, process memory or parent branch log was read.','','**Sources and provenance.** All scientific support is internal immutable experiment evidence, independently read by reviewer TASK-20261025-5145ac. Sources read as bytes for hashing are included in the complete attestation. No recalled external literature is load-bearing. External canonical graphs were left unchanged because this task authorizes observation review only.','','**Review attestation**','','```yaml',yaml.safe_dump({'review_attestation':att},sort_keys=False).rstrip(),'```','']
 (OUT/'report.md').write_text('\n'.join(md))
 style=getSampleStyleSheet();style['BodyText'].fontSize=9;style['BodyText'].leading=12
 def para(s,kind='BodyText'):return Paragraph(escape(s),style[kind])
 story=[para('Prym census observation integrity','Title'),para('TASK-20261025-5145ac | EXP-ECDLP-d6d8e8 | RUN-ECDLP-ea49a6'),Spacer(1,10),para('Assigned-joint integrity findings only. No scientific hypothesis verdict or state transition.'),Spacer(1,8),para(f"Blind derivation sealed {blind['sealed_at']}. SHA256 {V['blind_seal_sha256']}."),Spacer(1,8),para(f"Fresh code checked {V['complete_attempts']:,} attempted outcomes and digests, {V['all_E1_equations']:,} E1 source equations, all 16 projected and augmented ranks, pivots, solutions, kernels and rank checkpoints. Fixed principal/E2 sample: {V['sampled_principal_E2_witnesses']} accepted rows."),Spacer(1,12)]
 tab=[['p','B','r','U','sample rows','full rows','sample rank','full rank']]
 for i,f in enumerate(panel['fixtures']):
  s,t=V['cells'][i*2:i*2+2];tab.append([f['p'],f['b'],f['r'],s['U'],s['accepted'],t['accepted'],s['rank'],t['rank']])
 table=Table(tab,repeatRows=1);table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e1e5e9')),('GRID',(0,0),(-1,-1),.3,colors.lightgrey),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story+=[table,Spacer(1,10),drawing,para('Exact finite counts over 8 fixtures and 16 cells; no population interval. U=0 cells are all-public calibration. Seed0 is ordering nuisance.')]
 story += [PageBreak(),para('Findings by assigned joint','Title')]
 for f in observations:story += [para(f['joint']+': '+f['verdict'],'Heading2'),para(f['checked_scope']),Spacer(1,5),para(f['observations']),Spacer(1,5),para('Limits: '+' '.join(f['limits']))]
 story += [PageBreak(),para('Controls, custody and limits','Title'),para('All 11 reviewer negative mutations are rejected: scalar a+1, altered U, altered pivot, missing attempted status, changed raw digest, changed stored digest, omitted infinity term, repeated residual root, wrong atom sign, post-hoc locator and unknown tuple source. Exact mutations and rejection messages are retained in verification.json.'),Spacer(1,8),para('Every 4257 accepted interpolation/residual/row is recomputed in the complete attempted-stream replay. Explicit complete principal/E2 checks use first 4, last 4 and 8 SHA-ranked accepted rows per cell, deduplicated; all rows if fewer 16. Domain: TASK-20261025-5145ac-principal-v1. Existing checker receipt is corroboration only.'),Spacer(1,8)]
 for lim in limitations:story += [para(lim),Spacer(1,6)]
 costs=V['resource_and_cost_scope'];story += [para('Producer diagnostics: %.6f wall seconds, %.6f CPU seconds, %d peak self RSS bytes. Existing checker: %.6f wall seconds, %.6f CPU seconds, %d peak self RSS bytes.'%(costs['producer_wall_seconds'],costs['producer_cpu_seconds'],costs['producer_peak_self_RSS_bytes'],costs['existing_checker_wall_seconds'],costs['existing_checker_cpu_seconds'],costs['existing_checker_peak_self_RSS_bytes'])),Spacer(1,8),para('Review attestation: separate reviewer session; no producer authorship; no sibling report read; phase1 blind-from respected through sealed derivation; phase2 deliberately unblinded. Complete source-read list, per-joint scope and deviations: report.json and report.md. Exact output/recomputation records: verification.json; executable reviewer source: review.py.'),Spacer(1,8),para('No external canonical graph changes: task authorizes finite observation-integrity review only. Internal source provenance: reviewer TASK-20261025-5145ac read committed snapshot a6fe1b471 and bound sources. No new scientific trial, credential access, source edit or state transition.')]
 def footer(canvas,doc):canvas.setFont('Helvetica',7);canvas.drawString(42,24,'TASK-20261025-5145ac | RUN-ECDLP-ea49a6 | page '+str(doc.page))
 SimpleDocTemplate(str(OUT/'report.pdf'),rightMargin=38,leftMargin=38,topMargin=36,bottomMargin=38).build(story,onFirstPage=footer,onLaterPages=footer)
 print('REPORT_BUILT',len(V['negative_mutation_controls']),len(archives)+1)
if __name__=='__main__' and sys.argv[-1]=='finish':finish()

def finalize_records():
 """Preserve actual static-check diagnostic and the manually inspected PDF facts."""
 import subprocess,yaml,fitz
 V=json.loads((OUT/'verification.json').read_text());R=json.loads((OUT/'report.json').read_text());B=json.loads((OUT/'blinded-input-derivation.json').read_text())
 cmd=['python3','tools/check_review_independence.py','--plan','ledger/handoffs/TASK-20261025-5145ac.yaml','--reports',str((OUT/'report.json').relative_to(ROOT))]
 proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 check={'command':cmd,'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'interpretation':'Actual static checker failed its union-of-sources blind_from test on six paths. The frozen plan expressly allows these reads after the seal; no formal independence-gate pass is claimed. No tool or plan edit performed.'}
 assert proc.returncode==1 and '6 blind_from path(s)' in proc.stdout+proc.stderr
 interval={'first_deliberate_unblind_time':None,'exact_first_read_timestamp_recorded':False,'strictly_after':B['sealed_at'],'before':V['started_at'],'event_order':'Wrote and SHA-hashed blind derivation; messaged Coordinator seal; then read result/source. First read was earlier than the successful replay start. No exact wall timestamp was captured.','predeclared_allowance':'ledger/handoffs/TASK-20261025-5145ac.yaml review_plan.blindness.phase2_allowed and rationale explicitly authorize deliberate unblinding after blind-input seal.'}
 V['independence_checker']=check;V['phase_order']=interval
 R['independence_checker']=check;R['phase_order']=interval;R['formal_independence_gate_passed']=False
 R['review_attestation']['unblinding_time']=interval
 deviation={'kind':'timestamp_missing','description':'Exact first deliberate-unblind wall timestamp was not separately recorded; it is bounded after the blind seal and before successful fresh replay start. Phase order and the original seal/hash message are recorded.'}
 R['procedure_deviations']=[x for x in R['procedure_deviations'] if x['kind']!='timestamp_missing']+[deviation]
 inspection={'review_pdf_pages':3,'all_review_pdf_pages_visually_inspected':True,'original_run_pdf_pages':1,'all_original_run_pdf_pages_visually_inspected':True,'method':'PyMuPDF render at1.2x, followed by view_image on each page; table, graph, run IDs, source references and limitations legible.','review_pdf_sha256':sha((OUT/'report.pdf').read_bytes()),'original_run_pdf_sha256':sha((ROOT/'experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6/report.pdf').read_bytes())}
 assert len(fitz.open(OUT/'report.pdf'))==3
 V['pdf_inspection']=inspection;R['pdf_inspection']=inspection
 dump(OUT/'verification.json',V)
 R['component_sha256']={p:sha((OUT/p).read_bytes()) for p in ['blinded-input-derivation.json','review.py','verification.json','graph-source.json','graph.svg','report.pdf']}
 dump(OUT/'report.json',R)
 md=(OUT/'report.md').read_text();md=md.split('**Review attestation**')[0]
 md+='**Recorded phase timing and static check.** Exact first deliberate-unblind timestamp was not captured. It occurred after '+B['sealed_at']+' and before '+V['started_at']+'. The plan expressly authorizes post-seal phase2 source/output reads. Actual generic checker exit code: '+str(proc.returncode)+'. It reported one independence problem on six protected paths; it cannot represent this same-task phased allowance. No formal independence-gate pass is claimed. Full command/output are retained in verification.json and report.json.\n\n'
 md+='All three review PDF pages and the one-page original run PDF were visually inspected. Tables, graph, run IDs and limitations are legible.\n\n**Review attestation**\n\n```yaml\n'+yaml.safe_dump({'review_attestation':R['review_attestation']},sort_keys=False).rstrip()+'\n```\n'
 (OUT/'report.md').write_text(md)
 print(json.dumps({'checker_exit':proc.returncode,'outputs':{p.name:sha(p.read_bytes()) for p in sorted(OUT.iterdir()) if p.is_file()}},indent=2))
if __name__=='__main__' and sys.argv[-1]=='finalize':finalize_records()
