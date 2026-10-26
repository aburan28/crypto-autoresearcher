#!/usr/bin/env python3
"""Exploratory aggregation of already-sealed BL rows; launches no experiment."""
from pathlib import Path
import argparse,collections,hashlib,json,statistics
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
parts=[];rows=[]
for f in sorted(a.source_run.glob('rows-part-*.jsonl')):
 data=f.read_bytes();parts.append({'name':f.name,'bytes':len(data),'sha256':sha(data)})
 for line in data.splitlines():
  if not line:continue
  d=json.loads(line)
  if d.get('row_kind')=='baseline_target' and d.get('method')=='bernstein_lange_precomp':
   rows.append((d['fixture'],d['target_id'],d['upstream_stats']['iterations']))
assert len(parts)==2560
assert len(rows)==768 and len(set((f,t) for f,t,_ in rows))==768
manifest={'raw_publication_commit':'c4b940ac5360e17cb221772f968bab20f67266c3','archive_commit':'1822ae0b7247c08dd9062eba62358b8bf19ff728','files':parts}
manifest_bytes=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()
mp=a.output/'source-parts-manifest.json';assert not mp.exists();mp.write_bytes(manifest_bytes)
counts=collections.Counter(n for _,_,n in rows);attempts=sum(n for _,_,n in rows)
result={'kind':'exploratory_existing_record_aggregation','source_experiment':'EXP-ECDLP-9f7772','source_run':'RUN-ECDLP-dba66e','new_experiment_executed':False,'source_parts':len(parts),'matched_unique_targets':len(rows),'total_online_attempts':attempts,'unsuccessful_attempts_before_success':sum(max(0,n-1) for _,_,n in rows),'mean_attempts':statistics.mean(n for _,_,n in rows),'median_attempts':statistics.median(n for _,_,n in rows),'targets_with_retries':sum(n>1 for _,_,n in rows),'max_attempts':max(n for _,_,n in rows),'attempt_distribution':dict(sorted(counts.items())),'harvestable_unmatched_dp_count':None,'scope':'Unsuccessful-attempt count is an UPPER BOUND on harvestable terminal observations. Old rows do not distinguish unmatched DP endpoints from chain-limit restarts or exact-duplicate endpoints. No improvement, novelty, or asymptotic inference is made.','source_parts_manifest_sha256':sha(manifest_bytes),'analysis_script_sha256':sha(Path(__file__).read_bytes()),'source_metadata':{f:{'sha256':sha((a.source_run/f).read_bytes()),'bytes':(a.source_run/f).stat().st_size} for f in ['execution-receipt.json','parts-manifest.json','verification-manifest.json']}}
out=a.output/'motivation.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['matched_unique_targets','total_online_attempts','unsuccessful_attempts_before_success','targets_with_retries','source_parts_manifest_sha256']},indent=2))
