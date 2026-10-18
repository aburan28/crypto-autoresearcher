"""Retained discriminating follow-ups to review_controls.py, new output names."""
from pathlib import Path
source=Path(__file__).with_name('review_controls.py').read_text()
exec(compile(source.split('# J3-F1:')[0],str(Path(__file__).with_name('review_controls.py')),'exec'))
original_setup=setup_cli
def setup_cli(name,false=False,hidden=False):
    repo,helper,target=original_setup(name,false=false,hidden=hidden)
    for p in [helper,target]:p.write_text(p.read_text().replace('namespace Control','namespace CryptoResearch.Control').replace('end Control','end CryptoResearch.Control'))
    data=json.loads((repo/'spec.json').read_text());data['theorem_name']='CryptoResearch.Control.good'
    (repo/'spec.json').write_text(json.dumps(data,indent=2)+'\n')
    return repo,helper,target

positive_repo,positive=cli_case('followup-cli-positive',0)
cli_case('followup-cli-false-before',1,false=True)
cli_case('followup-cli-loadbearing-mutated',3,false=True,
         hook=after_version(lambda r,h,t:h.write_text('namespace CryptoResearch.Control\ndef P : Prop := True\nend CryptoResearch.Control\n')))

# Worker runner defaults retain a reference to the original subprocess.run.
# Invoke the original real worker and delete only after it finishes successfully.
original_verify=cli.LeanWorker.verify
delete_observed={}
def verify_then_delete(self,task):
    result=original_verify(self,task)
    delete_observed.update(real_worker_machine_verified=result.machine_verified,
        real_worker_build_log=result.build_log,real_worker_audit_log=result.audit_log)
    (self.repo_root/task.workspace/'CryptoResearch/Helper.lean').unlink()
    delete_observed['deleted']=True
    return result
cli.LeanWorker.verify=verify_then_delete
try:cli_case('followup-cli-deleted-import',3)
finally:cli.LeanWorker.verify=original_verify
save_json(ART/'controls/followup-cli-deleted-import/deletion-hook.json',delete_observed)

# Bind verifier software itself: mutate its scratch source bytes, retain both.
verifier=RUNTIME/'orchestration/formal/receipts.py';verifier_before=verifier.read_bytes()
try:
    cli_case('followup-cli-verifier-mutated',3,hook=after_version(lambda r,h,t:verifier.write_bytes(verifier_before+b'\n# persistent verifier-source control\n')))
    (ART/'controls/followup-cli-verifier-mutated/verifier-after.py').write_bytes(verifier.read_bytes())
finally:verifier.write_bytes(verifier_before)

cli_case('followup-hidden-positive',0,hidden=True)
cli_case('followup-hidden-false-before',1,false=True,hidden=True)
hidden_repo,hidden=cli_case('followup-hidden-loadbearing-mutated',3,false=True,hidden=True,
         hook=after_version(lambda r,h,t:h.write_text('namespace CryptoResearch.Control\ndef P : Prop := True\nend CryptoResearch.Control\n')))
spec=positive_repo/'spec.json';task=task_from_spec(load_spec(spec))
attacks=[('verification','theorem_name','Wrong.name'),('verification','theorem_file','Wrong.lean'),
 ('verification','task_id','wrong-task'),('verification','forbidden_constructs',['sorry:forged']),
 ('verification','status','formalization_blocked'),('verification','build_passed',1),
 ('verification','axiom_audit_passed',1),('verification','blocking_reason','failure'),
 ('provenance','lean_version','bogus'),('provenance','workspace_inputs',{}),
 ('provenance','verifier_inputs',{}),(None,'build_log',''),(None,'audit_log',''),
 (None,'schema','wrong'),(None,'infrastructure_failure','failed')]
receipt_rows=[]
for section,key,value in [(None,'baseline',None),*attacks]:
    data=copy.deepcopy(positive)
    if key!='baseline':(data[section] if section else data)[key]=value
    errors=receipt_errors(data,repo=positive_repo,spec=spec,task=task)
    dest=ART/'followup-receipt-attacks'/key;dest.mkdir(parents=True)
    save_json(dest/'receipt.json',data)
    row={'id':'followup-receipt-'+key,'errors':errors,'expected_accepted':key=='baseline',
         'expectation_met':bool(errors)==(key!='baseline')}
    save_json(dest/'result.json',row);receipt_rows.append(row)
helper=positive_repo/'formal/CryptoResearch/Helper.lean';before=helper.read_bytes()
helper.write_bytes(before+b'\n-- stale helper control\n')
errors=receipt_errors(positive,repo=positive_repo,spec=spec,task=task)
receipt_rows.append({'id':'followup-receipt-stale-helper','errors':errors,
                     'expected_accepted':False,'expectation_met':'local source inputs' in errors})
helper.write_bytes(before)
hspec=hidden_repo/'spec.json';htask=task_from_spec(load_spec(hspec))
hidden_errors=receipt_errors(hidden,repo=hidden_repo,spec=hspec,task=htask)
save_json(ART/'hidden-counterexample.json',{
    'interface':'real CLI plus strict receipt validator',
    'claim':'Persistent mutation of configured hidden local imported proof source remains undetected',
    'source_dir':'.hidden','lake_library':'Helper','source':'formal/.hidden/Helper.lean',
    'initial_source':'def P : Prop := False','verified_source':'def P : Prop := True',
    'target_unchanged':True,'receipt_errors':hidden_errors,
    'bound_input_manifest':hidden['provenance']['workspace_inputs'],
    'new_source_mutation_expected_exit_code':3,
    'actual_cli_exit_code':rows[-1]['exit_code'],
    'not_a_kernel_refutation':'Lean checked True; no proof of the original False proposition is claimed'})

study=positive_repo/'research/lean_retrospective_20261018';study.mkdir(parents=True)
shutil.copy2(FROZEN/'crypto-autoresearcher/research/lean_retrospective_20261018/summarize.mjs',study/'summarize.mjs')
save_json(study/'inventory.json',{'revision':'engineering-control','targets':[{'spec':'spec.json'}]})
receipts=study/'receipts-v2';receipts.mkdir();save_json(receipts/'control.json',positive)
env={**os.environ,'PYTHON':sys.executable,'PYTHONPATH':str(RUNTIME)}
run('followup-summary-positive',['node',str(study/'summarize.mjs'),'--min-verified','1','--output',str(ART/'followup-summary-positive.json')],positive_repo,0,env)
forged=copy.deepcopy(positive)
forged['verification'].update(theorem_name='Wrong.name',forbidden_constructs=['sorry:forged'])
forged['build_log']='';forged['audit_log']='';forged['provenance']['lean_version']='bogus'
(receipts/'control.json').write_text(json.dumps(forged,indent=2)+'\n')
run('followup-summary-original-forgery',['node',str(study/'summarize.mjs'),'--min-verified','1','--output',str(ART/'followup-summary-forgery.json')],positive_repo,1,env)

# Explicit ownership/exclusion control: nested Lake project's source belongs to
# its own discovered project; declared gate-fixture directories are excluded.
repo=SCRATCH/'gate-ownership';repo.mkdir();tools=repo/'tools';tools.mkdir()
shutil.copy2(FROZEN/'crypto-lean/tools/proof-gate.sh',tools/'proof-gate.sh');(tools/'proof-gate.sh').chmod(0o755)
shutil.copy2(FROZEN/'crypto-lean/tools/AuditAxioms.lean',tools/'AuditAxioms.lean')
outer=repo/'project';nested=outer/'nested';nested.mkdir(parents=True)
for project,name in [(outer,'Root'),(nested,'Nested')]:
    (project/'lean-toolchain').write_text('leanprover/lean4:v4.35.0\n')
    (project/'lakefile.toml').write_text(f'name = "{name}"\ndefaultTargets = ["{name}"]\n[[lean_lib]]\nname = "{name}"\n')
    (project/(name+'.lean')).write_text('theorem rootTrue : True := by trivial\n' if name=='Root' else 'theorem nestedFalse : False := by sorry\n')
fixtures=outer/'tools/lean';fixtures.mkdir(parents=True)
(fixtures/'Fixture.lean').write_text('theorem excludedFixture : False := by sorry\n')
real_run(['git','init','-q'],cwd=repo,check=True);real_run(['git','add','.'],cwd=repo,check=True)
snapshot(repo,ART/'control-sources/gate-ownership')
run('gate-ownership-list',['bash','tools/proof-gate.sh','--list'],repo,0)
run('gate-ownership-outer',['bash','tools/proof-gate.sh','--out',str(ART/'gate-receipts/ownership-outer'),'project'],repo,0)
run('gate-ownership-nested',['bash','tools/proof-gate.sh','--out',str(ART/'gate-receipts/ownership-nested'),'project/nested'],repo,1)
save_json(ART/'followup-results.json',{'controls':rows,'receipt_controls':receipt_rows,'hidden_receipt_errors':hidden_errors})
print(json.dumps({'controls':len(rows),'unexpected':[r['id'] for r in rows if not r['expectation_met']],
    'receipt_controls':len(receipt_rows),'receipt_unexpected':[r['id'] for r in receipt_rows if not r['expectation_met']],
    'hidden_receipt_errors':hidden_errors}))
