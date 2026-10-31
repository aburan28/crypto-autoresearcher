"""Frozen label-independent feature library; imported observations are not new source executions."""
import hashlib,json,math,pathlib,subprocess
D=pathlib.Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def load():return json.loads((D/'inputs.json').read_text())
def valuation(v,l):
 assert v!=0
 k=0
 while v%l==0:v//=l;k+=1
 return k

def kronecker(a,l):
 if l==2:
  return 0 if a%2==0 else (1 if a%8 in (1,7) else -1)
 z=pow(a%l,(l-1)//2,l)
 return -1 if z==l-1 else z

def dkchar(d,l):
 if l==2:return kronecker(d,2) # odd t => odd Delta_pi and odd f_pi
 v=valuation(d,l)
 return 0 if v%2 else kronecker(d//l**v,l)

def numeric(x,levels):
 r=x['row'];p,b,c,n=[int(r[k]) for k in ('p','b','c','n')];t=p+1-n;dp=t*t-4*p
 assert t%2 and dp%4==1 and p>3 and (4-b*b)%p
 j=6912*pow((4-b*b)%p,-1,p)%p
 vals={'b':b,'c':c,'j':j,'j_minus_1728':(j-1728)%p,'modular_delta':(4-b*b)*pow(6912,-1,p)%p,'curve_delta':432*(4-b*b)%p,'E6':-b*pow(2,-1,p)%p}
 o={}
 for m in (3,4,8,12):o['p_mod_'+str(m)]=p%m
 for name,v in vals.items():
  for e in (2,3,4,6,12):o[f'power/{name}/{e}']=int(v!=0 and pow(v,(p-1)//math.gcd(e,p-1),p)==1)
  o[f'bit_deficit/{name}']=p.bit_length()-v.bit_length()
 o.update({'n_less_p':int(n<p),'width_gate':int(n.bit_length()<=p.bit_length()),'trace_positive':int(t>0),'n_prime':int(True)}) # imported certified prime cohort
 for s,v in [('n_minus_1',n-1),('n_plus_1',n+1)]:o['v2/'+s]=valuation(v,2)
 for ell in [2]+levels:
  for name,v in [('delta_pi',dp),('trace',t),('p',p),('n',n),('twist_order',2*(p+1)-n)]:o[f'character/{name}/{ell}']=kronecker(v,ell)
  o[f'character/DK/{ell}']=dkchar(dp,ell)
  o[f'valuation_delta/{ell}']=valuation(dp,ell)
 return o

def gp_source(data):
 levels=data['levels'];out=['default(parisizemax,256000000);','dkc(d,l)={my(v);if(l==2,return(kronecker(d,2)));v=valuation(d,l);if(v%2,0,kronecker(d/l^v,l))};']
 for i,x in enumerate(data['rows']):
  r=x['row'];p,b,c,n=[int(r[k]) for k in ('p','b','c','n')];out.append(f'p={p};b={b};c={c};n={n};t=p+1-n;dp=t^2-4*p;j=lift(Mod(6912,p)/Mod(4-b^2,p));')
  expr=[]
  for m in (3,4,8,12):expr.append(f'p%{m}')
  vv=['b','c','j','lift(Mod(j-1728,p))','lift(Mod(4-b^2,p)/6912)','lift(Mod(432*(4-b^2),p))','lift(-Mod(b,p)/2)']
  for v in vv:
   for e in (2,3,4,6,12):expr.append(f'if({v}==0,0,Mod({v},p)^((p-1)/gcd({e},p-1))==1)')
   expr.append(f'logint(p,2)-if({v}==0,-1,logint({v},2))')
  expr+=['n<p','logint(n,2)<=logint(p,2)','t>0','1','valuation(n-1,2)','valuation(n+1,2)']
  for ell in [2]+levels:
   expr.extend([f'kronecker({v},{ell})' for v in ('dp','t','p','n','2*(p+1)-n')]);expr+=[f'dkc(dp,{ell})',f'valuation(dp,{ell})']
  out.append(f'print([{i},['+','.join(expr)+']]);')
 out.append('quit;');return '\n'.join(out)+'\n'

def columns(data,method):
 ns=[numeric(x,data['levels']) for x in data['rows']];keys=list(ns[0]);assert all(list(x)==keys for x in ns)
 if method=='gp':
  src=gp_source(data);(D/'independent-features.gp').write_text(src)
  proc=subprocess.run(['/opt/homebrew/bin/gp','-fq',str(D/'independent-features.gp')],capture_output=True,text=True,timeout=180)
  (D/'gp.stdout').write_text(proc.stdout);(D/'gp.stderr').write_text(proc.stderr)
  (D/'gp-receipt.json').write_text(json.dumps({'returncode':proc.returncode,'binary_sha256':sha('/opt/homebrew/bin/gp'),'source_sha256':sha(D/'independent-features.gp')},indent=2)+'\n')
  assert proc.returncode==0 and proc.stderr.strip()=='***   Warning: new maximum stack size = 256000000 (244.141 Mbytes).'
  got=[json.loads(z) for z in proc.stdout.splitlines() if z.strip()];assert [x[0] for x in got]==list(range(21))
  gs=[dict(zip(keys,z[1],strict=True)) for z in got]
  assert gs==ns,'Independent GP feature disagreement'
  ns=gs
 out={k:[r[k] for r in ns] for k in keys}
 types={k:('character' if k.startswith('character/') else 'valuation' if k.startswith(('valuation_','v2/','bit_deficit/')) else 'context' if k.startswith('p_mod_') else 'boolean') for k in keys}
 for ell in data['levels']:
  k='roots/'+str(ell);out[k]=[x['roots'][str(ell)] for x in data['rows']];types[k]='roots'
 for cutoff in (13,31,97,293):
  es=[ell for ell in data['levels'] if ell<=cutoff]
  for agg in ('sum','levels_with_roots'):
   k=f'root_budget/{cutoff}/{agg}';out[k]=[sum(x['roots'][str(e)] if agg=='sum' else int(x['roots'][str(e)]>0) for e in es) for x in data['rows']];types[k]='threshold'
 for group in ('ecpp','twist','faults','expansion'):
  for name in data['rows'][0][group]:
   k=group+'/'+name;out[k]=[None if x[group][name] is None else int(x[group][name]) for x in data['rows']]
   types[k]='boolean' if group in ('faults','expansion') or name in ('original_strict_admission','source_format_checker_all_steps_pass','diagnostic_wrapped_admitted','any_k_le_20','any_k_le_1000') else 'threshold'
 return out,types

def atomize(cols,types,levels):
 atoms=[]
 for name,vs in cols.items():
  typ=types[name]
  if typ=='boolean':conditions=[('eq',1)]
  elif typ=='character':conditions=[('eq',z) for z in (-1,0,1)]
  elif typ=='context':conditions=[('eq',z) for z in sorted(set(vs))]
  elif typ=='roots':conditions=[('eq',z) for z in (0,1,2,int(name.split('/')[1])+1)]
  elif typ=='valuation':conditions=[('ge',z) for z in range(1,9) if not name.startswith('valuation_') or z<=4]
  else:conditions=[('ge',z) for z in sorted({v for v in vs if v is not None})]
  for op,value in conditions:
   vv=[None if v is None else int(v==value if op=='eq' else v>=value) for v in vs]
   atoms.append({'name':name,'operation':op,'value':value,'values':vv})
 full=(1<<21)-1;groups={}
 for a in atoms:
  t=sum(1<<i for i,v in enumerate(a['values']) if v==1);f=sum(1<<i for i,v in enumerate(a['values']) if v==0);u=full^(t|f)
  neg=t>f
  if neg:t,f=f,t
  key=(t,f,u)
  groups.setdefault(key,[]).append({'name':a['name'],'operation':a['operation'],'value':a['value'],'negated_to_signature':neg})
 sigs=[{'id':i,'true':t,'false':f,'unknown':u,'aliases':aa} for i,((t,f,u),aa) in enumerate(sorted(groups.items()))]
 return atoms,sigs
