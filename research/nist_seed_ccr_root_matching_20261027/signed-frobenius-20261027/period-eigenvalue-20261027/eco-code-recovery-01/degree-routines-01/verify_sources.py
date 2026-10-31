"""Verify metadata custody and all21 input bindings; no native code executes."""
import csv,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((P/'SOURCE-SEAL.json').read_text())
for n,h in seal['files'].items():assert sha(P/n)==h,n
rows=json.loads((P/'prior-rows.json').read_text());cross=list(csv.DictReader((P/'cohort-crosswalk.csv').open()));assert len(rows)==len(cross)==21 and len({r['curve_uid'] for r in rows})==21
for a,b in zip(rows,cross):
 for k in ['name','curve_uid','label','p','b','n','seed_hex','ordinal','timestamp']:assert str(a[k])==b[k],(a['name'],k)
 assert b['A']=='-3' and b['historical_prediction']=='UNDETERMINED'
 assert all(b[k]=='UNKNOWN' for k in ['original_caller','original_polynomial_degree','degree_routine_invoked','original_error_policy'])
assert sha(P/'prior-rows.json')==json.loads((P/'INPUT-BINDING.json').read_text())['sha256']
n=json.loads((P/'NORMALIZATION.json').read_text());assert sum(x['normalized_equal'] for x in n['functions'].values())==4
assert json.loads((P/'SOURCE-REVIEW.json').read_text())['new_scientific_trials']==0
source_count=0
if '--sources' in sys.argv:
 for s in json.loads((P/'SOURCE-MANIFEST.json').read_text())['sources']:
  p=P/s['private_file'];b=p.read_bytes();assert len(b)==s['bytes'] and sha(p)==s['sha256']
  if 'git_blob' in s:assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==s['git_blob']
  source_count+=1
print(json.dumps({'status':'PASS','sealed_metadata_files':len(seal['files']),'input_rows':21,'publications':sum(r['label']=='published' for r in rows),'omissions':sum(r['label']=='omitted' for r in rows),'streams':len({r['timestamp'] for r in rows}),'private_sources_checked':source_count,'native_programs_executed':0,'historical_criterion_identified':False},sort_keys=True))
