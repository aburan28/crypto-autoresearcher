#!/usr/bin/env python3
"""Software conformance only. Compare identities/counters, never cost ratios."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
arms=['static_full','static_small','static_filled','harvest','harvest_disabled','rho_reference'];rows={};checks=0
def check(v,message):
 global checks
 assert v,message
 checks+=1
expected=json.loads((a.case/'expected.json').read_text())['hand_selected_scalars']
for arm in arms:
 rows[arm]=[json.loads(x) for x in (a.case/(arm+'.jsonl')).read_text().splitlines()]
 ts=[d for d in rows[arm] if d['row_kind']=='target'];check(len(ts)==len(expected),arm+' complete target row coverage')
 check(all(d['arm']==arm for d in rows[arm]),arm+' identity')
 for d,k in zip(ts,expected):
  check(d['target_ordinal']==expected.index(k),arm+' ordinal')
  check(d['status']=='solved' and d['verified_scalar']==k,arm+' fixed known witness')
 for d in rows[arm]:
  if 'pending_count' in d:check(d['known_count']+d['pending_count']<=d['endpoint_cap'],arm+' arena cap')
  check('process_cpu_seconds' not in d and 'wall_seconds' not in d,arm+' no emitted performance clocks')
small=rows['static_small'];off=rows['harvest_disabled']
for kind,fields in [('setup',['status','parameters','counters','auxiliary_work','upstream_stats','rng','known_count','table_state_hash64']),('initial_endpoint',['index','fp','exponent']),('target',['status','verified_scalar','counters','auxiliary_work','upstream_stats','rng','reuse','known_count','pending_count','table_state_hash64'])]:
 aa=[d for d in small if d['row_kind']==kind];bb=[d for d in off if d['row_kind']==kind];check(len(aa)==len(bb),'A/A row cardinality '+kind)
 for left,right in zip(aa,bb):check({k:left[k] for k in fields}=={k:right[k] for k in fields},'A/A canonical bytes/vector '+kind)
setup=next(d for d in rows['static_filled'] if d['row_kind']=='setup');check(setup['status']=='ready' and setup['known_count']==setup['endpoint_cap'],'filled capacity success')
check(setup['precompute_reported_ops_total']<=setup['parameters']['max_precomp_ops'],'complete reported setup watchdog')
result={'kind':'fixed_development_software_conformance','checks_passed':checks,'scientific_cohort_run':False,'performance_analysis':False,'all_fixed_target_witnesses':len(arms)*len(expected),'arm_names':arms,'source_stream_sha256':{arm:hashlib.sha256((a.case/(arm+'.jsonl')).read_bytes()).hexdigest() for arm in arms}}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
