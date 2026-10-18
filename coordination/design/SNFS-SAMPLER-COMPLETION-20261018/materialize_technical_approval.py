#!/usr/bin/env python3
"""Materialize a passed exact prospective packet; no trials or git mutations."""
from pathlib import Path
import hashlib,json,sys,datetime,yaml
R=Path(__file__).resolve().parents[3]; B=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'tools'))
from experiment_preapproval import assess
from research_dispatch import validate_queue
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
packet=json.loads((B/'preapproval-preserve-partials.json').read_text())
receipt_path=B/'preapproval-ready-6f9cbde91c59be4c323804d3c5fb58f7b083ede1.json'
receipt=json.loads(receipt_path.read_text());fresh=assess(R,packet)
assert receipt==fresh and fresh['approvable'] is True,fresh
D='DEC-20261018-5bc740'; exp='EXP-ECDLP-00e491';decision_path=R/f'ledger/decisions/{D}.yaml'
assert not decision_path.exists(),'Do not overwrite an approval decision'
lane=yaml.safe_load((R/'ledger/decisions/DEC-20261018-70aee7.yaml').read_text())['coordinator_decision']
body={'id':D,'decided_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decided_by':'coordinator','decision':'approve','scope':'Technical readiness approval for exactly two fresh descriptive sampler trials; no scientific interpretation or status transition.','target_ids':[exp],'context':'Owner requested all remaining sampler observations. A fresh ordinary protocol binds complete finite support and fixed archived-input searches without rewriting frozen G3.','rationale':['Standing authorization applies after complete prospective protocol passes unchanged ordinary preapproval.','Exact revised packet is approvable:true with no blockers at published source commit 6f9cbde91c59be4c323804d3c5fb58f7b083ede1.','The final wrapper retains and indexes partial scratch artifacts before propagating child failure; incomplete runs are not relabeled complete.','Complete raw bundles, independent arithmetic checker, exact source/input hashes, memory/concurrency protection, archive coverage and published ownership remain mandatory.'],'evidence_refs':[],'limitations':['No scientific trial has been launched by this Coordinator and no measurements or mathematical outcomes are asserted.','The two finite trials cover 3232 coefficient patterns and 102 archived-input searches only; no broader sampling or independence claim is authorized.','Exact source/seed/input changes require the existing new-record/amendment path.','Approval is not durable until real isolated archival verification and publication; ordinary selector, claims and supervisor gates remain mandatory.'],'next_actions':['Archive these exact approval/source/input bytes via TASK-20261018-a0d0c0, verify the real Git receipt, publish and confirm ordinary selector execution_state ready.','Executor alone may acquire/publish the exact claim then launch the two fixed trials under TASK-20261018-49157c, retaining every failure and using new immutable retry identities where required.'],'knowledge_promotion':{'promoted':[],'not_warranted':'Technical readiness approval only; no scientific evidence or interpretation.'},'standing_user_authorization':'AGENTS.md standing authorization 2026-09-06; observe-first owner instruction 2026-10-17; current explicit request to finish all remaining sampler tasks.','technical_execution_authorized':True,'preapproval':{'packet':str((B/'preapproval-preserve-partials.json').relative_to(R)),'receipt':str(receipt_path.relative_to(R)),'receipt_sha256':sha(receipt_path),'approvable':True,'blockers':[],'prospective_sha256':fresh['prospective_sha256'],'published_source_commit':'6f9cbde91c59be4c323804d3c5fb58f7b083ede1'},'runtime_provenance':lane['runtime_provenance']}
for k,path in packet.items():
 if k in fresh['canonical_paths']:
  dst=R/path;src=Path(packet['preview'][k]);assert sha(src)==fresh['prospective_sha256'][k];dst.write_bytes(src.read_bytes())
decision_path.write_text(yaml.safe_dump({'coordinator_decision':body},sort_keys=False))
validate_queue(json.loads((R/packet['queue']).read_text()))
for k,path in fresh['canonical_paths'].items():assert sha(R/path)==fresh['prospective_sha256'][k]
print(json.dumps({'technical_approval':D,'exact_materialization_verified':True,'scientific_trials_launched':0},indent=2))
