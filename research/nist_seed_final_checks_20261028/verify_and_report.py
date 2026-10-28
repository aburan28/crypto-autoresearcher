"""Verify retained point certificates and make only the fixed closing comparisons."""
import csv,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;W=P/'runs/final-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(Pt,Q,a,p):
 if Pt is None:return Q
 if Q is None:return Pt
 x,y=Pt;u,v=Q
 if x==u and (y+v)%p==0:return None
 m=((3*x*x+a)*pow(2*y,-1,p) if x==u else (v-y)*pow(u-x,-1,p))%p
 z=(m*m-x-u)%p;return z,(m*(x-z)-y)%p
def mul(k,Pt,a,p):
 out=None
 while k:
  if k&1:out=add(out,Pt,a,p)
  Pt=add(Pt,Pt,a,p);k//=2
 return out
def verify(C,a,b,p,N,F):
 assert C[0]==N and C[3]==1 and C[2]
 M=1
 for x,y,o in C[2]:
  assert 0<=x<p and 0<=y<p and (y*y-x*x*x-a*x-b)%p==0
  assert N%o==0 and mul(N,(x,y),a,p) is None and mul(o,(x,y),a,p) is None
  for q,e in F:
   if o%q==0:assert mul(o//q,(x,y),a,p) is not None
  M=math.lcm(M,o)
 assert M==C[1]
 s=math.isqrt(4*p);L=p+1-s;H=p+1+s;first=(L+M-1)//M
 assert H//M-first+1==1 and first*M==N
 return len(C[2])
for n,h in json.loads((P/'FROZEN.json').read_text())['files'].items():assert sha(P/n)==h,n
inputs=json.loads((P/'INPUTS.json').read_text())['rows'];raw=json.loads((W/'raw.json').read_text());assert len(inputs)==len(raw)==21
out=[];witnesses=0
for i,(r,x) in enumerate(zip(inputs,raw)):
 assert x[0]==i and len(x)==23
 p,b,n,c=map(int,[r['p'],r['b'],r['n'],r['c']]);F=[(int(q),e) for q,e in r['twist_factors']];tw=2*p+2-n;nm=n if p%4==1 else tw
 assert math.prod(q**e for q,e in F)==tw and x[5]==nm and x[9]==tw
 witnesses+=verify(x[1],-3,b,p,n,[(n,1)])
 witnesses+=verify(x[7],-3,-b,p,nm,[(n,1)] if p%4==1 else F)
 d=x[8];assert pow(d,(p-1)//2,p)==p-1
 witnesses+=verify(x[11],(-3*d*d)%p,(b*d**3)%p,p,tw,F)
 assert x[2]==int(b<p-b) and x[3]==int(b%2==0) and (c*b*b+27)%p==0
 assert x[12]==max(q for q,e in F) and x[13]==x[12].bit_length()
 flags={'field_prime':bool(x[22]),'nonsingular':bool(x[20]),'b_seed_relation':bool(x[21]),'order_prime':bool(x[19]),'order_certified':bool(x[1][3]),'non_anomalous':not bool(x[16]),'order_bit_cap':bool(x[18]),'MOV20_pass':x[14]==0 or x[14]>20,'MOV100_pass':x[14]==0,'b_lower':bool(x[2]),'b_even':bool(x[3]),'b_matches_p3_exponent':None if x[4]==-1 else bool(x[4]),'opposite_b_order_prime':bool(x[6]),'opposite_b_same_order':nm==n,'quadratic_twist_order_prime':bool(x[10]),'twist_largest_prime_MOV20_pass':x[15]==0 or x[15]>20,'twist_largest_prime_MOV100_pass':x[15]==0}
 out.append({'name':r['name'],'curve_uid':r['curve_uid'],'label':r['label'],'p':r['p'],'a':'-3','b':r['b'],'n':r['n'],'seed_hex':r['seed_hex'],'ordinal':r['ordinal'],'timestamp':r['timestamp'],'field_bits':p.bit_length(),'opposite_b_order':str(nm),'twist_order':str(tw),'twist_largest_prime':str(x[12]),'twist_largest_prime_bits':x[13],'main_embedding_first_k_le_100':x[14] or None,'twist_largest_embedding_first_k_le_100':x[15] or None,'twist_anomalous':bool(x[17]),'opposite_b_order_certified':bool(x[7][3]),'twist_order_certified':bool(x[11][3]),'flags':flags})
assert len({r['curve_uid'] for r in out})==21
counts={}
for f in out[0]['flags']:
 c={label:{'true':sum(r['flags'][f] is True for r in out if r['label']==label),'false':sum(r['flags'][f] is False for r in out if r['label']==label),'na':sum(r['flags'][f] is None for r in out if r['label']==label)} for label in ['published','omitted']}
 c['full_cohort_separator']=all(c[z]['na']==0 for z in ['published','omitted']) and ((c['published']['true']==10 and c['omitted']['false']==11) or (c['published']['false']==10 and c['omitted']['true']==11));counts[f]=c
pairs=[]
for o in out:
 if o['label']!='omitted':continue
 for b in out:
  if b['label']=='published' and b['p']==o['p']:
   q,r=int(o['twist_largest_prime']),int(b['twist_largest_prime']);pairs.append({'omitted':o['name'],'published':b['name'],'field_bits':o['field_bits'],'sign_omitted_minus_published':(q>r)-(q<r),'omitted_largest_bits':o['twist_largest_prime_bits'],'published_largest_bits':b['twist_largest_prime_bits']})
assert len(pairs)==25
both_directions=any(r['sign_omitted_minus_published']==1 for r in pairs) and any(r['sign_omitted_minus_published']==-1 for r in pairs)
separators=[f for f,c in counts.items() if c['full_cohort_separator']]
result={'scope':'One fixed full-cohort pass; no retuning, pair-function search or follow-on arithmetic campaign.','rows':out,'flag_counts':counts,'perfect_fixed_flag_separators':separators,'same_field_twist_pairs':pairs,'twist_ordering_both_directions':both_directions,'verified_curve_orders':63,'verified_point_witnesses':witnesses,'full_cohort_invocations':1,'retries':0,'bounds':[20,100],'unknown_historical_rule':True,'conclusion':'These specified arithmetic checks do not identify the historical selection rule. Available evidence does not recover it without original generator source, run logs or equivalent direct historical evidence. This does not prove that no arithmetic criterion exists.','user_requested_action':'Stop the loop and pause the unresolved original goal after publishing these results.'}
(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
(P/'VERIFICATION.json').write_text(json.dumps({'status':'PASS','method':'Separate Python integer point arithmetic verifies every retained point order, factor-wise minimality and unique Hasse multiple. PARI rigorously proves p,n and imported twist factors prime.','curve_order_certificates':63,'point_witnesses':witnesses,'rows':21,'raw_sha256':sha(W/'raw.json'),'result_sha256':sha(P/'RESULT.json'),'fresh_GP_cohort_invocations':1,'cohort_retries':0},indent=2)+'\n')
fields=['name','curve_uid','label','field_bits','ordinal','twist_largest_prime_bits','opposite_b_order_certified','twist_order_certified']+list(counts)
with (P/'cohort.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for r in out:w.writerow({**{k:r[k] for k in fields if k in r},**r['flags']})
table='\n'.join('| '+f+' | '+str(c['published']['true'])+'/10 | '+str(c['omitted']['true'])+'/11 | '+str(c['published']['na']+c['omitted']['na'])+' | '+str(c['full_cohort_separator'])+' |' for f,c in counts.items())
witness_text='\n'.join('* '+str(v) for v in [next(r for r in pairs if r['sign_omitted_minus_published']==1),next(r for r in pairs if r['sign_omitted_minus_published']==-1)])
md=f'''# Final fixed arithmetic checks and requested stopping point

User-directed closing pass, 28 October2026. Exactly one fresh PARI invocation covers all21 exact curves:10 publications,11 reconstructed omissions,six streams. No retuning or further predicate/class-group/isogeny rounds.

All63 curve-order certificates pass: original, opposite-b and nontrivial quadratic twist for every curve. Separate Python arithmetic verifies {witnesses} point witnesses, exact factor-wise point orders and the unique possible multiple in the Hasse interval. This freshly certifies the supplied original and twist orders without a new SEA count. PARI rigorously rechecks the field/order/factor primalities. Full points, commands, versions, stdout/stderr and immutable hashes are retained in runs/final-01, FROZEN.json and VERIFICATION.json.

| Fixed flag | Published true | Omitted true | Not applicable | Full-cohort separator |
|---|---:|---:|---:|---|
{table}

There are {len(separators)} perfect separators among these fixed flags, including their complements. No combinations were searched. The p=3mod4 exponent-root flag is explicitly not applicable to the four224-bit rows; model/root conventions are not intrinsic curve properties. Both b roots are prime-order isomorphic models in that field; elsewhere the opposite-b model has the nontrivial quadratic-twist order. The separate nonsquare-twist check uses the first integer nonsquare d>=2, with coefficients a*d^2,b*d^3.

The25 same-field twist-factor comparisons contain both directions: an omission can have either a larger or a smaller largest twist prime than a publication. This prevents a uniform monotone twist-strength cutoff from separating the cohort. No cutoff was fitted. Two exact counterexamples:

{witness_text}

MOV bounds20 and100 were fixed before the run, checked in one modular-power pass per original order and largest twist prime. SEC1v2 AppendixB records that the historical bound20 was increased to100: https://www.secg.org/sec1-v2.pdf . A no-hit result proves only absence of embedding degrees in the stated range, not the exact embedding degree. Original ANSI PDF refresh returned502; existing source identities and factor records are pinned in INPUTS.json.

Controls use E/F101 with a=-3,b=6,N=109, an incorrect proposed N=107, a singular model and malformed point, low-embedding-degree positives and the anomalous equality detector. A control-only GP expression-precedence error was repaired before cohort execution and retained; the full cohort was run once with0 retries. No outcome-dependent code, cutoff or feature change followed the run.

## Closing conclusion

These specified arithmetic checks do not identify the historical selection rule. The available evidence cannot determine the original rule without the NIST/Certicom generator source, run logs or equivalent direct historical provenance. A finite collection of null arithmetic tests does not establish that the rule cannot depend on any arithmetic property.

The investigation loop stops here at the user's requested boundary. The original historical objective remains unresolved and will be paused, not labeled solved. No additional class-group, isogeny, predicate-library or historical-code rounds are scheduled. Reconstructed omissions remain distinct from documented original rejection events.
'''
(P/'report.md').write_text(md)
print(json.dumps({'status':'VERIFIED','rows':21,'order_certificates':63,'point_witnesses':witnesses,'fixed_separators':separators,'twist_pairs':25,'twist_ordering_both_directions':both_directions,'fresh_cohort_invocations':1,'retries':0},sort_keys=True))
