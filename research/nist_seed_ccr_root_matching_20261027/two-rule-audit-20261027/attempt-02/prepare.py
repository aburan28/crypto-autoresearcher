"""Import existing observations by exact UID/seed; no classifier fit."""
import csv,hashlib,json,pathlib,shutil
D=pathlib.Path(__file__).resolve().parent
H=D.parent
R=pathlib.Path('/Volumes/SSD990/llm/tmp/nist-ecpp-cohort-admission-20261026/repository')
files={'cohort':H/'validation-02/rows.json','fibers':H/'canonical-equations-01/FIBER-AUDIT.json','ecpp':R/'research/nist_seed_ecpp_full_cohort_20261027/comparison.csv','twist':R/'research/nist_seed_twist_embedding_20261023/analysis.json','faults':pathlib.Path('/Volumes/data/workspaces/nist-seed-criteria-20261022/workflow/workflow-results.json'),'expansion':R/'research/nist_seed_selection_20261016/raw/candidates.jsonl'}
rows=json.loads(files['cohort'].read_text());assert len(rows)==21
fib=json.loads(files['fibers'].read_text());ecpp={x['curve_uid']:x for x in csv.DictReader(files['ecpp'].open())};twist={x['curve_uid']:x for x in json.loads(files['twist'].read_text())['rows']};faults=json.loads(files['faults'].read_text())['sign_faults']
seeds={r['seed_hex'].removeprefix('0x').lower() for r in rows};expanded={}
for line in files['expansion'].open():
 x=json.loads(line);s=x['seed'].removeprefix('0x').lower()
 if s in seeds:
  if s in expanded:
   assert expanded[s]['variants']==x['variants'] and expanded[s]['index']==x['index']
  else:expanded[s]=x
assert len(expanded)==21
levels=sorted({x['ell'] for x in fib['cells'] if x['index']<21});assert len(levels)==61
out=[]
for i,r in enumerate(rows):
 x={'row':r,'roots':{},'ecpp':{},'faults':{}}
 for c in fib['cells']:
  if c['index']==i:
   assert int(r['p'])==c['p'];x['roots'][str(c['ell'])]=len(c['roots'])
 assert len(x['roots'])==61
 e=ecpp[r['curve_uid']];assert (int(e['p']),int(e['n']),e['seed_hex'])==(int(r['p']),int(r['n']),r['seed_hex'])
 for k in ['certificate_steps','cm_steps','printed_positive_D_entries','distinct_positive_D','largest_positive_D']:x['ecpp'][k]=int(e[k])
 for k in ['original_strict_admission','source_format_checker_all_steps_pass','diagnostic_wrapped_admitted']:x['ecpp'][k]=int(e[k]=='True')
 t=twist[r['curve_uid']];assert int(t['p_hex'],16)==int(r['p']);assert int(t['twist_order_hex'],16)==2*(int(r['p'])+1)-int(r['n'])
 x['twist']={k:t[k] for k in ['factor_count','large_factor_count','largest_factor_bits','any_k_le_20','any_k_le_1000']}
 for f in faults:
  matches=[z for z in f['rows'] if z['name']==r['name']]
  assert len(matches)<=1
  x['faults'][f['position']+'_'+f['sign']]=int(matches[0]['truth_retained']) if matches else None
 v=expanded[r['seed_hex'].removeprefix('0x').lower()]['variants']
 x['expansion']={k:int(int(v[k]['c'],0)==int(r['c'])) for k in ['ansi_x9_62_1998','nist_fips_186_2']}
 out.append(x)
source={'schema':'nist-two-rule-inputs/v1','cohort_sha256':hashlib.sha256(files['cohort'].read_bytes()).hexdigest(),'sources':{k:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in files.items()},'levels':levels,'rows':out,'restrictions':['No row identity, ordinal, timestamp, seed bytes, base-point metadata or publication-membership predicate.','Modern modular-table observations and later LiDIA fault models do not authenticate the original 1997 caller.','Unknowns remain null. Imported twist largest-factor metric is source-reported; this search does not add a factorization certificate.']}
(D/'inputs.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n');shutil.copyfile(files['cohort'],D/'rows.json')
print('Imported',len(out),'identities;',len(levels),'levels; no fit performed.')
