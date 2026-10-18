from pathlib import Path
import hashlib, json, re
import yaml

root=Path(__file__).resolve().parent.parent
art=root/'artifacts'
claims=json.loads((root/'claims.json').read_text())
att=yaml.safe_load((root/'review_attestation.yaml').read_text())['review_attestation']
expected=set()
for repo in ('crypto','cryptanalysis'):
    p=Path('/workspace/lean-review-inputs')/repo/'research/lean_retrospective_20261018/proof-map.json'
    expected.update(x['declaration'] for x in json.loads(p.read_text())['declarations'])
assert len(claims['claims'])==9
assert {c['declaration'] for c in claims['claims']}==expected
controls=(art/'Controls.lean').read_text()
control_names={'ReviewerControls.'+n for n in re.findall(r'^theorem (\w+)',controls,re.M)}
assert len(control_names)==24
assert not re.search(r'\b(sorry|axiom|native_decide)\b',controls)
for c in claims['claims']:
    assert (c['machine_status'],c['fidelity'],c['review_outcome'],c['verdict'])==('passed','faithful_scoped','validated_scoped','holds')
    assert all(n in control_names for n in c['positive_controls']+c['boundary_controls'])
    assert all((root/x).is_file() for x in c['machine_evidence']+c['control_evidence'])
assert 'audited 9 theorems' in (art/'axiom-audit.log').read_text()
assert '0 failing, 0 trusted' in (art/'axiom-audit.log').read_text()
assert 'audited 27 theorems' in (art/'controls-axiom-audit.log').read_text()
assert '0 failing, 0 trusted' in (art/'controls-axiom-audit.log').read_text()
commands=json.loads((art/'commands.json').read_text())
assert len(commands)==14
for n in range(1,9):
    label=f'controls-attempt-{n}'
    entries=[c for c in commands if c['label']==label]
    assert len(entries)==1
    assert entries[0]['exit_status']==(0 if n==8 else 1)
    assert (art/f'Controls-attempt-{n}.lean').exists()
    assert (art/f'{label}.log').exists()
for r in json.loads((art/'input-hash-checks.json').read_text()):
    assert r['matches'] and r.get('cache_workspace_matches',True)
for r in json.loads((art/'historical-binding-checks.json').read_text()):
    assert r['same_bytes']
for r in json.loads((art/'dependency-checks.json').read_text()):
    assert r['expected_rev']==r['actual_rev'] and r['tracked_clean']
assert att['task_id']=='TASK-20261018-63a7cc'
assert att['joints_owned']==['J1-transport-and-rho-fidelity']
assert att['verdict']=='holds' and att['read_sibling_reports'] is False
assert att['communicated_with_sibling_reviewers'] is False
for source in att['sources_read']:
    assert isinstance(source,str) and source
    taskparts=re.findall(r'/reports/(TASK-[^/]+)',source)
    assert not any(t!='TASK-20261018-63a7cc' for t in taskparts)
summary={'status':'passed','exact_mapped_declarations':9,'explicit_control_theorems':24,
    'audited_control_theorem_constants':27,'producer_axiom_failures':0,'control_axiom_failures':0,
    'compiler_trusted_proofs':0,'checks':'Own packet only: names, evidence references, control references, source/pin/hash bindings, command outcomes and declared own-joint scope. No sibling reports read.'}
(art/'own-validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
