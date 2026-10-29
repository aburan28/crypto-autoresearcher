"""Write review candidates only; never modify archived records or registry."""
from pathlib import Path
from copy import deepcopy
import json,hashlib
import yaml
P=Path(__file__).resolve().parent
inputs=json.loads((P/'sources.json').read_text())
records={r['path']:r for r in inputs['records']}
ids=['KR-IC-f5c584','KR-IC-5765d2','KR-IC-73db3f','KR-IC-5a43e5','KR-IC-1fcdbc','KR-IC-9e610d']
review={'kind':'retrospective_repository_card_comparison','read_on':'2026-10-29','reader':'Codex coordinator, T-782 / TASK-20261029-8b1359','source_commit':inputs['source_commit'],'report':'docs/reports/2026-10-29-binstd-prior-art-correction/REPORT.md','scope':'Read the six named committed KR cards and the four effective proposal claim/prior-art/citation blocks. This is a retrospective metadata comparison, not evidence of a pre-proposal literature search.','literature_verification':'No new full-text literature verification. The KR cards retain their own status and citation verification labels; KR-IC-73db3f is heuristic and its cited papers are abstract_read.','scientific_effect':'No change to experiment approval, hypothesis status, quantitative results, novelty status, thresholds, seeds, scope, or performance claims.'}
out=[]
(P/'candidates').mkdir(exist_ok=True)
for selected in inputs['selected']:
 source=records[selected['effective_path']];old=yaml.safe_load(source['text']);doc=deepcopy(old);body=doc['idea'];rid=body['id'];prior=body.get('prior_art')
 if prior:
  internal=[r for r in prior['nearest'] if r['ref'].startswith('IDEA-')]
  assert len(internal)==1
  prior['nearest']=[r for r in prior['nearest'] if not r['ref'].startswith('IDEA-')]
  assert 'internal_lineage' not in prior
  prior['internal_lineage']=internal
 else:
  if rid.endswith('94078e'):
   delta='The frozen proposal adds a new catalog intended to satisfy diversity floors and a separately scoped (17,4) replication arm. The factor-base V mechanism is prior context; the heuristic card does not prove the catalog meets its floors or establish a package result.'
  else:
   delta='The frozen proposal adds a product-rank-seeking catalog, an explicit (17,3) instrument-boundary outcome, and a cell-scoped (17,4) rule. These are proposed protocol changes, not consequences proved by the factor-base V card or an already established package result.'
  prior={'frontier_map':'knowledge/frontiers/ecdlp','frontier_map_commit':inputs['source_commit'],'rows_checked':ids,'nearest':[{'ref':'KR-IC-73db3f','provenance':'kb','relation':'adjacent','delta':delta}], 'searched':{'corpus_grep':[], 'web':[], 'blocked':[], 'note':'Retrospective direct reading of the six committed cards named in rows_checked on 2026-10-29; no search log at proposal time is asserted.'}}
  body['prior_art']=prior
 prior['retrospective_review']=deepcopy(review)
 a=deepcopy(old);b=deepcopy(doc);a['idea'].pop('prior_art',None);b['idea'].pop('prior_art',None);assert a==b
 data=yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=100).encode()
 path=P/'candidates'/f'{rid}.yaml'
 with path.open('xb') as f:f.write(data)
 version='v3' if selected['route'] else 'v2'
 proposed='ledger/corrections/schema-supersessions/20261029-binstd-prior-art/ledger__proposals__'+rid+'.'+version+'.yaml'
 original=records[selected['original_path']]
 out.append({'id':rid,'candidate':path.relative_to(P).as_posix(),'candidate_sha256':hashlib.sha256(data).hexdigest(),'original_path':selected['original_path'],'original_sha256':original['sha256'],'effective_path':selected['effective_path'],'effective_sha256':source['sha256'],'prior_registry_entry':selected['route'],'proposed_destination':proposed,'proposed_registry_entry':{'kind':'ledger','superseded_path':selected['original_path'],'superseded_sha256':original['sha256'],'superseding_path':proposed,'superseding_sha256':hashlib.sha256(data).hexdigest(),'defect':'Retrospective attribution-only correction: internal idea lineage is not a typed nearest KR reference; missing comparisons are dated2026-10-29 and retain heuristic/literature limitations. Prior originals and replacements remain immutable. No scientific or execution claim is newly established.','registered':'2026-10-29'}})
with (P/'candidates.json').open('x') as f:json.dump({'status':'review_candidates_only_not_applied','source_commit':inputs['source_commit'],'archival_task':'TASK-20261029-8b1359','conductor_task':'T-782','blocked_application':'Conductor ledger and registry scopes overlap T650/T673 migration reservations. Only the report directory is admitted.','records':out},f,indent=2);f.write('\n')
print('Prepared',len(out),'review candidates; ledger and registry unchanged.')
