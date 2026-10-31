from pathlib import Path
import hashlib,json,re,collections,math
from arithmetic import *
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text())
def parsed(data):
 out={'roots':[],'complete':False};current=None
 for raw in data.decode().splitlines():
  if not raw.startswith('AUDIT '):continue
  w=raw.split();kind=w[1]
  if kind=='POLY':
   degree=int(w[3]);coeff=tuple(map(int,w[4:]));assert len(coeff)==degree+1
   if w[2]=='modular':assert 'modular' not in out;out['modular']=coeff
   else:assert current is not None and w[2]=='kernel' and 'kernel' not in current;current['kernel']=coeff
  elif kind=='SPLIT':assert 'split' not in out;out['split']=dict(zip(['ell','elkies','root_count','transformation_type'],map(int,w[2:])))
  elif kind=='ROOT_BEGIN':assert current is None;current={'index':int(w[2]),'profile':int(w[3]),'root':int(w[4])}
  elif kind=='QUOTIENT':current['quotient']=list(map(int,w[2:]))
  elif kind=='DIVISION_ZERO':current['native_division_zero']=bool(int(w[2]))
  elif kind=='REL':
   values=list(map(int,w[3:]));assert len(values)==int(w[2]);target=current if current is not None else out;assert 'relation' not in target;target['relation']=values
  elif kind=='ROOT_COMPLETE':assert current is not None and (current['index'],current['profile'])==(int(w[2]),int(w[3]));current['complete']=True;out['roots'].append(current);current=None
  elif kind=='COMPLETE':assert not out['complete'];out['complete']=True
  elif kind=='SOURCE_ERROR':out['source_error']=True
  elif kind=='ATKIN_COMPLETE':out['atkin_complete']=True
 assert current is None or not out['complete']
 return out

def audit_one(job,trace,expected_trace):
 p=int(job['p']);A=int(job['a']);B=int(job['b']);ell=job['ell'];f=tuple(x%p for x in trace['modular']);assert len(f)==ell+2 and trace['split']['ell']==ell and trace['split']['transformation_type']==1
 tokens=list(map(int,(HERE/'source'/('meq'+str(ell))).read_text().split()));size=2*(ell+2);assert all(t==0 for t in tokens[size:]);N=tuple(tokens[k]%p for k in range(0,size,2));D=tuple(tokens[k]%p for k in range(1,size,2));j=j_invariant(A,B,p)
 assert f==trim([(n+j*d)%p for n,d in zip(N,D)])
 assert gcd(f,derivative(f,p),p)==(1,)
 linear=gcd(f,sub(power((0,1),p,f,p),(0,1),p),p)
 root_values=sorted({r['root'] for r in trace['roots']});assert trace['split']['root_count']==len(root_values)==len(linear)-1
 product=(1,)
 for root in root_values:assert evaluate(f,root,p)==0;product=mul(product,((-root)%p,1),p)
 assert monic(product,p)==linear and bool(trace['split']['elkies'])==bool(root_values)
 if not root_values:
  assert trace.get('atkin_complete') and expected_trace%ell in trace['relation']
  return {'roots':0,'profile_checks':0,'atkin':True,'relation_contains_trace':True}
 assert len(trace['roots'])==2*len(root_values) and {(r['index'],r['profile']) for r in trace['roots']}=={(i,k) for i in range(len(root_values)) for k in [0,1]}
 kernels={}
 for r in trace['roots']:
  assert r['root']==root_values[r['index']];kernel=tuple(x%p for x in r['kernel']);assert len(kernel)==(ell-1)//2+1 and r['native_division_zero']
  assert division_remainder(ell,A,B,kernel,p)==()
  qa,qb=r['quotient'];va,vb=velu(A,B,kernel,p)
  assert (4*pow(qa,3,p)+27*qb*qb)%p!=0
  assert j_invariant(qa,qb,p)==j_invariant(va,vb,p)
  paired=pow(ell,12//math.gcd(12,ell-1),p)*pow(r['root'],-1,p)%p;quotient_j=j_invariant(qa,qb,p)
  assert (evaluate(N,paired,p)+quotient_j*evaluate(D,paired,p))%p==0
  if r['index'] in kernels:assert kernels[r['index']]==monic(kernel,p)
  else:kernels[r['index']]=monic(kernel,p)
  assert isomorphic(va,vb,qa,qb,p) is True
  if r['profile']==0:assert r['relation']==[expected_trace%ell]
  else:assert expected_trace%ell in r['relation'] and set(r['relation']).issubset({expected_trace%ell,(-expected_trace)%ell})
 assert len(set(kernels.values()))==len(root_values)
 return {'roots':len(root_values),'profile_checks':len(trace['roots']),'atkin':False,'division_polynomial_checks':len(trace['roots']),'velu_and_isomorphism_checks':len(trace['roots']),'root_quotient_fricke_checks':len(trace['roots']),'distinct_kernels':len(kernels),'relation_contains_trace':True}

plan=load(HERE/'PROTOCOL.json');start=load(HERE/'STARTED.json');assert start['protocol_sha256']==sha((HERE/'PROTOCOL.json').read_bytes()) and start['driver_sha256']==sha((HERE/'run.py').read_bytes())
for name,want in plan['source_sha256'].items():assert sha((HERE/name).read_bytes())==want
assert load(HERE/'CAPTURE_COMPLETE.json')['named_specializations']==63
rows=[]
for job in plan['jobs']:
 out=HERE/'runs'/job['id'];record=load(out/'RESULT.json');raw=(out/'stdout.raw').read_bytes();err=(out/'stderr.raw').read_bytes();assert record['job']==job and record['stdout_sha256']==sha(raw) and record['stderr_sha256']==sha(err)
 assert (out/'input.txt').read_bytes()==(job['p']+' '+job['a']+' '+job['b']+'\n').encode()
 if not record['native_complete']:rows.append({'id':job['id'],'status':'INDETERMINATE','record':record});continue
 trace=parsed(raw);assert trace['complete'];audit=audit_one(job,trace,int(job['p'])+1-int(job['curve']['n']));rows.append({'id':job['id'],'curve':job['curve'],'ell':job['ell'],'status':'PASS','audit':audit})
# Constructed generic control point count is independent of LiDIA.
p=1000003;squares=bytearray(p)
for y in range(p):squares[y*y%p]+=1
control_traces={}
for name,A,B in [('generic',p-3,1),('j0',0,1),('j1728',p-1,0)]:control_traces[name]=p+1-(1+sum(squares[(x*x%p*x+A*x+B)%p] for x in range(p)))
control_rows=[]
for job in plan['controls']:
 out=HERE/'runs'/job['id'];record=load(out/'RESULT.json');trace=parsed((out/'stdout.raw').read_bytes())
 if job['model']=='generic':assert record['native_complete'];control_rows.append({'id':job['id'],'status':'PASS','audit':audit_one(job,trace,control_traces['generic'])})
 else:control_rows.append({'id':job['id'],'status':'SOURCE_EXCEPTION' if record['source_error'] else 'COMPLETE','stderr':(out/'stderr.raw').read_text(),'trace':control_traces[job['model']]})
result={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'PARTIAL','scope':'All rational roots at level3/5/13 in the available later-lineage LiDIA build; no authenticated historical-use claim.','arithmetic_controls':arithmetic_controls(),'specializations':63,'successful_specializations':sum(r['status']=='PASS' for r in rows),'rational_modular_roots':sum(r.get('audit',{}).get('roots',0) for r in rows),'kernel_profile_checks':sum(r.get('audit',{}).get('profile_checks',0) for r in rows),'atkin_specializations':sum(r.get('audit',{}).get('atkin',False) for r in rows),'rows':rows,'controls':control_rows,'historical_criterion_identified':False}
print(json.dumps(result,indent=2,sort_keys=True))
