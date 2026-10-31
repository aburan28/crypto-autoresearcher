"""Verify all signed profiles; fixed new features crossed with the prior frozen library."""
import csv,hashlib,json,pathlib,struct,time
from arithmetic import D
from features import atomize
from prior_search import fast_pair,row_pair,controls as logical_controls

def columns(cells,rows):
 levels=sorted({c['ell'] for c in cells});cols={};types={};costnames=['known_candidates_min','known_candidates_max','known_rank_min','known_rank_max','unknown_candidates_min','unknown_candidates_max','unknown_rank_min','unknown_rank_max'];lookup={(c['index'],c['ell']):c for c in cells}
 def put(name,vs,typ='threshold'):cols[name]=vs;types[name]=typ
 for l in levels:
  cc=[lookup[i,l] for i in range(21)]
  for name in ['full_order','x_order','projective_order']:
   vv=[c[name] for c in cc];put(f'signed/{l}/{name}',vv);put(f'signed/{l}/{name}_even',[int(v%2==0) for v in vv],'boolean')
  for kind in ['scalar','jordan','split','nonsplit']:put(f'signed/{l}/kind_{kind}',[int(c['kind']==kind) for c in cc],'boolean')
  for name,fn in [('min_factor_degree',lambda c:min(d for d,n in c['factor_degrees'])),('max_factor_degree',lambda c:max(d for d,n in c['factor_degrees'])),('factor_count',lambda c:sum(n for d,n in c['factor_degrees']))]:put(f'signed/{l}/{name}',[fn(c) for c in cc])
  for j,name in enumerate(costnames):put(f'signed/{l}/{name}',[c['cost'][j] for c in cc])
 for cutoff in (13,31,97,293):
  ls=[l for l in levels if l<=cutoff]
  for j,name in enumerate(costnames):put(f'signed/budget/{cutoff}/{name}',[sum(lookup[i,l]['cost'][j] for l in ls) for i in range(21)])
 return cols,types

def signature(a):
 t=sum(1<<i for i,v in enumerate(a['values']) if v==1);f=sum(1<<i for i,v in enumerate(a['values']) if v==0);u=((1<<21)-1)^(t|f)
 return (min(t,f),max(t,f),u)

def search(allatoms,oldatoms,method):
 groups={}
 for a in allatoms:
  k=signature(a);t=sum(1<<i for i,v in enumerate(a['values']) if v==1);groups.setdefault(k,[]).append({k2:v for k2,v in a.items() if k2!='values'}|{'negated_to_signature':t!=k[0]})
 oldkeys={signature(a) for a in oldatoms};sigs=[{'id':i,'true':k[0],'false':k[1],'unknown':k[2],'old':k in oldkeys,'aliases':v} for i,(k,v) in enumerate(sorted(groups.items()))];labels=[int(r['label']=='published') for r in json.loads((D/'prior-rows.json').read_text())];fn=fast_pair if method=='bitset' else row_pair;ctrl=logical_controls(fn);fits=[];witness=bytearray();pairs=0;singles=[]
 for i,a in enumerate(sigs):
  if not a['old']:
   zero={'true':0,'false':(1<<21)-1,'unknown':0};r,p,w=fn(a,zero,labels)
   if r or p:singles.append({'a':i,'robust':r,'possible':p})
  for b in sigs[i+1:]:
   if a['old'] and b['old']:continue
   r,p,w=fn(a,b,labels);pairs+=1;witness.extend(struct.pack('<H',w))
   if r or p:fits.append({'a':a['id'],'b':b['id'],'robust_functions':[f for f in range(16) if r>>f&1],'possible_functions':[f for f in range(16) if p>>f&1]})
 out={'status':'PASS','controls':ctrl,'old_signatures':len(oldkeys),'all_signatures':len(sigs),'new_signatures':sum(not s['old'] for s in sigs),'pairs':pairs,'functions':16*pairs,'fits':fits,'single_fits':singles,'witness_sha256':hashlib.sha256(witness).hexdigest()};(D/(method+'-search.json')).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');(D/(method+'-witnesses.u16le')).write_bytes(witness)
 if method=='bitset':(D/'all-signatures.json').write_text(json.dumps(sigs,indent=2,sort_keys=True)+'\n')
 return out

def main():
 a=json.loads((D/'matrix.json').read_text());b=json.loads((D/'eigen.json').read_text());assert a['cell_count']==b['cell_count']==1281
 assert a['cells']==b['cells'],'Signed Frobenius/candidate profiles disagree'
 assert a['controls']['records']==b['controls'][:4]
 prior=json.loads((D/'prior-AUDIT.json').read_text());assert prior['status']=='PASS' and prior['counts']['robust_pairs']==prior['counts']['possible_pairs']==0
 rows=json.loads((D/'prior-rows.json').read_text());cols,types=columns(a['cells'],rows);atoms,_=atomize(cols,types,[]);old=json.loads((D/'prior-bitset-atoms.json').read_text());both=old+atoms
 (D/'new-columns.json').write_text(json.dumps(cols,indent=2,sort_keys=True)+'\n');(D/'new-atoms.json').write_text(json.dumps(atoms,indent=2,sort_keys=True)+'\n')
 aa=search(both,old,'bitset');bb=search(both,old,'rowwise');assert aa==bb;assert (D/'bitset-witnesses.u16le').read_bytes()==(D/'rowwise-witnesses.u16le').read_bytes()
 summary={'status':'PASS','complete':True,'cohort':21,'streams':6,'cells':1281,'controls':a['controls'],'independent_all_cells_equal':True,'source_candidate_lists_excluding_true_eigenvalue':0,'scalar_cells':sum(c['scalar'] for c in a['cells']),'new_columns':len(cols),'new_atoms':len(atoms),'prior_atoms':len(old),'search':aa,'historical_criterion_identified':False,'limits':['Full signed action is derived from certified p,n and direct scalar tests where trace/determinant alone are ambiguous.','Factor-degree multisets are predicted from linear action, not1281 new polynomial factorizations.','Candidate lists use the later recovered source and hypothetical known/unknown projective-degree settings, not authenticated1997 program use or timing.','Old-old predicate pairs are imported from the prior complete zero-fit census; only new-only signatures crossed with the union are evaluated here.','All labels and previous observations were visible; exact fits are retrospective classifiers, not historical attribution.']};(D/'AUDIT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
 with (D/'cohort-summary.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');ks=['signed/3/full_order','signed/5/full_order','signed/13/full_order','signed/budget/293/known_rank_min','signed/budget/293/known_rank_max','signed/budget/293/unknown_rank_min','signed/budget/293/unknown_rank_max'];w.writerow(['index','name','label','curve_uid']+ks)
  for i,r in enumerate(rows):w.writerow([i,r['name'],r['label'],r['curve_uid']]+[cols[k][i] for k in ks])
 print(json.dumps({k:v for k,v in summary.items() if k not in ('controls','search')}));print(json.dumps({k:v for k,v in aa.items() if k not in ('fits','single_fits')}));print('fit pairs',len(aa['fits']))
if __name__=='__main__':main()
