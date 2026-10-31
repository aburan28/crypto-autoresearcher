"""All Boolean functions of two frozen atoms. No identity/seed-label features."""
import hashlib,itertools,json,pathlib,struct,sys,time
from features import D,load,columns,atomize
ALL_FUNCTIONS=(1<<16)-1

def allowed(s,accept,universal):
 return sum(1<<f for f in range(16) if (all if universal else any)(bool(f&(1<<b))==bool(accept) for b in range(4) if s&(1<<b)))
ROB=[[allowed(s,a,True) for s in range(16)] for a in (0,1)]
POS=[[allowed(s,a,False) for s in range(16)] for a in (0,1)]
def masks(a,b):return [x&y for x in (a['false']|a['unknown'],a['true']|a['unknown']) for y in (b['false']|b['unknown'],b['true']|b['unknown'])]
def fast_pair(a,b,labels):
 n=len(labels);full=(1<<n)-1;pub=sum(1<<i for i,v in enumerate(labels) if v);omit=full^pub;bs=masks(a,b)
 ps=sum(1<<j for j,m in enumerate(bs) if m&pub);os=sum(1<<j for j,m in enumerate(bs) if m&omit)
 robust=ROB[1][ps]&ROB[0][os];possible=robust
 if a['unknown'] or b['unknown']:
  possible=ALL_FUNCTIONS
  for i,v in enumerate(labels):
   rs=sum(1<<j for j,m in enumerate(bs) if m&(1<<i));possible&=POS[v][rs]
 witness=65535
 if not robust:
  conflict=ps&os;assert conflict
  j=(conflict&-conflict).bit_length()-1;p=(bs[j]&pub);o=(bs[j]&omit)
  witness=(j<<10)|(((p&-p).bit_length()-1)<<5)|((o&-o).bit_length()-1)
 return robust,possible,witness

def row_pair(a,b,labels):
 robust=ALL_FUNCTIONS;possible=ALL_FUNCTIONS;bins=[{0:[],1:[]} for _ in range(4)]
 n=len(labels)
 for i,y in enumerate(labels):
  av=[0,1] if a['unknown']>>i&1 else [int(bool(a['true']>>i&1))]
  bv=[0,1] if b['unknown']>>i&1 else [int(bool(b['true']>>i&1))]
  observed=[2*x+z for x in av for z in bv]
  for z in observed:bins[z][y].append(i)
  r=0;p=0
  for f in range(16):
   values=[(f>>z)&1 for z in observed]
   if all(v==y for v in values):r|=1<<f
   if any(v==y for v in values):p|=1<<f
  robust&=r;possible&=p
 witness=65535
 if not robust:
  z=next(z for z,v in enumerate(bins) if v[0] and v[1]);witness=(z<<10)|(min(bins[z][1])<<5)|min(bins[z][0])
 return robust,possible,witness

def sig(v):return {'true':sum(1<<i for i,x in enumerate(v) if x==1),'false':sum(1<<i for i,x in enumerate(v) if x==0),'unknown':sum(1<<i for i,x in enumerate(v) if x is None)}
def controls(fn):
 a=sig([0,0,1,1]);b=sig([0,1,0,1]);y=[0,1,1,0];r,p,_=fn(a,b,y);assert r==p==1<<6
 r,p,_=fn(sig([0,0]),sig([1,1]),[0,1]);assert r==p==0
 r,p,_=fn(sig([None,1]),sig([0,0]),[1,0]);assert r==0 and p!=0
 first=fn(a,b,y);assert fn(a,b,y)==first
 return {'xor_two_required':'PASS','collision_negative':'PASS','unknown_not_rejected':'PASS','aa_repeat':'PASS'}

def main(method):
 started=time.monotonic();data=load();fn=fast_pair if method=='bitset' else row_pair;ctrl=controls(fn)
 cols,types=columns(data,'python' if method=='bitset' else 'gp');atoms,sigs=atomize(cols,types,data['levels']);labels=[int(x['row']['label']=='published') for x in data['rows']]
 outputs={'columns.json':cols,'atoms.json':atoms,'signatures.json':sigs}
 for name,thing in outputs.items():
  path=D/(method+'-'+name);path.write_text(json.dumps(thing,sort_keys=True,indent=2)+'\n')
 fits=[];witness=bytearray();pair_count=0;robust_pairs=possible_pairs=robust_functions=possible_functions=0
 for i,a in enumerate(sigs):
  for j in range(i+1,len(sigs)):
   r,p,w=fn(a,sigs[j],labels);pair_count+=1;witness.extend(struct.pack('<H',w))
   if r or p:
    rr=[f for f in range(16) if r>>f&1];pp=[f for f in range(16) if p>>f&1];fits.append({'a':i,'b':j,'robust_functions':rr,'possible_functions':pp})
    robust_pairs+=bool(r);possible_pairs+=bool(p);robust_functions+=len(rr);possible_functions+=len(pp)
  if i%50==0:print(method,'signature',i,'of',len(sigs),flush=True)
 single=[]
 for a in sigs:
  zero=sig([0]*21);r,p,w=fn(a,zero,labels)
  if r or p:single.append({'a':a['id'],'robust_functions':[f for f in range(16) if r>>f&1],'possible_functions':[f for f in range(16) if p>>f&1]})
 (D/(method+'-witnesses.u16le')).write_bytes(witness)
 result={'status':'PASS','method':method,'controls':ctrl,'cohort':21,'published':sum(labels),'omitted':len(labels)-sum(labels),'streams':len({x['row']['timestamp'] for x in data['rows']}),'atoms':len(atoms),'signatures':len(sigs),'pairs':pair_count,'truth_functions_examined':16*pair_count,'robust_pairs':robust_pairs,'possible_pairs':possible_pairs,'robust_functions':robust_functions,'possible_functions':possible_functions,'fits':fits,'single_fits':single,'witness_sha256':hashlib.sha256(witness).hexdigest(),'elapsed_seconds_diagnostic':time.monotonic()-started,'historical_criterion_identified':False}
 (D/(method+'-result.json')).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('fits','single_fits')},sort_keys=True))
if __name__=='__main__':main(sys.argv[1])
