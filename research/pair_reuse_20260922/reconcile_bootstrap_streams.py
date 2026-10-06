#!/usr/bin/env python3
"""Explain two sealed Monte Carlo stream choices from unchanged raw receipts."""
from pathlib import Path
import json,hashlib,statistics,random,math
root=Path(__file__).resolve().parents[2];p=root/'research/pair_reuse_20260922';r=root/'experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9'
rows=[json.loads(x) for x in (r/'benchmark_receipts.jsonl').read_text().splitlines()]
a=json.loads((r/'analysis.json').read_text());b=json.loads((p/'review/blind_results.json').read_text())
assert len(rows)==384 and all(x['valid'] for x in rows)
def q7(values,p):
 s=sorted(values);h=(len(s)-1)*p;lo=math.floor(h);hi=math.ceil(h)
 return s[lo] if lo==hi else s[lo]*(hi-h)+s[hi]*(h-lo)
def interval(ratios,rng):
 draws=[statistics.median([ratios[rng.randrange(8)] for _ in range(8)]) for _ in range(10000)]
 return [q7(draws,.025),q7(draws,.975)]
def close(a,b):return len(a)==len(b) and all(abs(x-y)<1e-15 for x,y in zip(a,b))
stream=random.Random('PAIR-REUSE-v1-bootstrap');cells=[]
for regime in ('n19_k4','n23_k16'):
 for m in (1,32,512):
  ratios=[]
  for panel in range(8):
   med={arm:statistics.median(x['wall_seconds'] for x in rows if x['regime']==regime and x['M']==m and x['panel']==panel and x['arm']==arm) for arm in ('expanded','canonical_normal_x')}
   ratios.append(med['canonical_normal_x']/med['expanded'])
  reset=interval(ratios,random.Random('PAIR-REUSE-v1-bootstrap'));continuous=interval(ratios,stream)
  prod=next(c for c in a['cells'] if c['regime']==regime and c['M']==m)
  blind=next(c for c in b['statistics']['cells'] if c['regime']==regime and c['M']==m)
  pc=[prod['bootstrap_95']['lower'],prod['bootstrap_95']['upper']];bc=blind['bootstrap']['ci_95']
  assert close(reset,pc) and close(continuous,bc)
  assert statistics.median(ratios)==prod['median_of_8_paired_ratios']==blind['median_ratio']
  cells.append({'regime':regime,'M':m,'median_ratio':statistics.median(ratios),'fresh_seed_each_cell':reset,'one_stream_in_regime_M_order':continuous,'matches_producer_frozen_source':True,'matches_blind_sealed_method':True})
primary=next(c for c in cells if c['regime']=='n23_k16' and c['M']==512)
files=[r/'benchmark_receipts.jsonl',r/'analysis.json',root/'experiments/EXP-KIC-d9c828/code/analyze.py',p/'review/blind_rederive.py',p/'review/blind_results.json',p/'review/blind_report.yaml']
out={'kind':'additive deterministic reconciliation of Monte Carlo stream allocation','experiment_reruns':0,'raw_or_review_artifacts_modified':False,'sources_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'finding':'The producer initializes Random(seed) inside each cell interval; the blind reviewer initializes one Random(seed) before the six-cell loop. The different stream position fully explains every endpoint difference. Point estimates and all underlying receipts agree.','preregistration_boundary':'Protocol states the seed, resampling unit, count and quantile method; cross-cell stream reset is not explicit in prose. Producer per-cell reset is bound by source frozen before all scientific processes. Do not retroactively replace either sealed result.','canonical_recorded_interval':primary['fresh_seed_each_cell'],'blind_stream_interval':primary['one_stream_in_regime_M_order'],'primary_upper_endpoint_difference':primary['one_stream_in_regime_M_order'][1]-primary['fresh_seed_each_cell'][1],'finite_effect_predicate_true_under_both':primary['median_ratio']<=.90 and all(ci[1]<1 for ci in [primary['fresh_seed_each_cell'],primary['one_stream_in_regime_M_order']]),'cells':cells,'future_protocol_requirement':'Specify RNG initialization/reset scope per cell and exact sampling primitive, in addition to seed and resample count.'}
(p/'bootstrap_stream_reconciliation.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['canonical_recorded_interval','blind_stream_interval','primary_upper_endpoint_difference','finite_effect_predicate_true_under_both']}))
