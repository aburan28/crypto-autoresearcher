"""Synthetic Git fixtures only: no experiment program or inference is launched."""
import copy,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
import pytest,yaml
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(HERE),str(ROOT/'tools')]
from proposed_experiment_preapproval import assess
from experiment_preapproval import assess as ordinary_assess
from experiment_execution import load_plan,ExecutionError
spec=importlib.util.spec_from_file_location('ordinary_fixture',ROOT/'tests/test_experiment_preapproval.py');ordinary=importlib.util.module_from_spec(spec);spec.loader.exec_module(ordinary)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def git(r,*args):return subprocess.check_output(['git','-C',str(r),*args],text=True,stderr=subprocess.DEVNULL).strip()

def fixture(root,kind='transport_repair',wrapper=False):
 packet,f=ordinary.fixture(root)
 old_dec=packet['approval_decision_id'];new_dec='DEC-20261017-c0ffee'
 oldspec=json.loads(f['spec'].read_text());put(root/packet['specification'],oldspec)
 oldplan=f['plan'];put(root/packet['trial_plan'],oldplan)
 # Publish only synthetic sealed original bytes, never real ledger records.
 git(root,'add','.');git(root,'commit','-qm','synthetic approved original');git(root,'update-ref','refs/remotes/origin/main','HEAD')
 original={'trial_plan':packet['trial_plan'],'trial_plan_sha256':sha(root/packet['trial_plan']),'specification_sha256':sha(root/packet['specification'])}
 newplan=copy.deepcopy(oldplan);newplan.update(approved_by=new_dec,task_id='TASK-20261017-c0ffee',queue='coordination/repaired/queue.json')
 newplanpath=f"experiments/{packet['experiment_id']}/amendments/fixture/trial-plan.json"
 amendmentpath=f"experiments/{packet['experiment_id']}/amendments/fixture/amendment.yaml"
 am={'experiment_id':packet['experiment_id'],'approved_by':new_dec,'status':'approved','frozen':True,'scientific_parameters_changed':False,'original_trial_plan_sha256':original['trial_plan_sha256'],'kind':kind,'input_bindings':oldspec['experiment']['input_bindings']}
 if kind=='retry':
  prior=newplan['trials'][0]['run_id'];newplan['trials'][0]['run_id']='RUN-ECDLP-112233'
  rp=f"experiments/{packet['experiment_id']}/runs/{prior}/execution-receipt.json"
  put(root/rp,{'run_id':prior,'trial_id':newplan['trials'][0]['id'],'status':'infrastructure_error','scientific_conclusion':None})
  git(root,'add',rp);git(root,'commit','-qm','synthetic terminal failure');git(root,'update-ref','refs/remotes/origin/main','HEAD')
  am['retry_receipts']={prior:{'path':rp,'sha256':sha(root/rp)}}
 if wrapper:
  wp='transport.py';fp='fixture-receipt.json'
  (root/wp).write_text('# sealed transport fixture; no execution by these tests\n');put(root/fp,{'kind':'transport-fixture','scientific_trials_launched':0})
  git(root,'add',wp,fp);git(root,'commit','-qm','synthetic transport sources');git(root,'update-ref','refs/remotes/origin/main','HEAD')
  newplan['source_sha256'][wp]=sha(root/wp)
  original_checker=copy.deepcopy(newplan['trials'][0]['check_argv'])
  newplan['trials'][0]['check_argv']=['python3',wp,'--original-checker-json',json.dumps(original_checker,separators=(',',':')),'--run-dir','{run_dir}']
  newplan['trials'][0]['artifacts'].append('producer-manifest.yaml')
  am['manifest_transport']={newplan['trials'][0]['id']:{'wrapper_source':{'path':wp,'sha256':sha(root/wp)},'fixture':{'path':fp,'sha256':sha(root/fp)}}}
 amp=root/'preview/amendment.yaml';put(amp,{'protocol_amendment':am});newplan['amendment']={'path':amendmentpath,'sha256':sha(amp)}
 np=root/'preview/new-plan.json';put(np,newplan)
 queue=json.loads(f['queue'].read_text());task=queue['tasks'][0];old_id=task['id'];task['id']=newplan['task_id'];task['handoff']['id']=newplan['task_id'];queue['tasks'][1]['depends_on']=[newplan['task_id']];queue['tasks'][1]['archive']['source_task_ids']=[newplan['task_id']]
 rb=f"experiments/{packet['experiment_id']}/runs/{newplan['trials'][0]['run_id']}"
 from experiment_execution import GENERATED
 task['artifact_paths']=[f'{rb}/{name}' for name in (*GENERATED,*newplan['trials'][0]['artifacts'])]
 task['handoff']['execution'].update(trial_plan=newplanpath,trial_plan_sha256=sha(np),approved_by=new_dec)
 hp=root/'preview/new-handoff.yaml';put(hp,{'handoff':task['handoff']});qp=root/'preview/new-queue.json';put(qp,queue)
 lane=root/f"coordination/goals/{oldspec['experiment']['goal_id']}/lanes/{packet['lane_id']}.lane.json"
 ld=json.loads(lane.read_text());ld['dispatch_queue_path']=newplan['queue'];put(lane,ld);git(root,'add',str(lane.relative_to(root)));git(root,'commit','-qm','synthetic corrected lane');git(root,'update-ref','refs/remotes/origin/main','HEAD')
 packet.update(schema='crypto.autoresearch.additive_preapproval_packet.v1',approval_decision_id=new_dec,original=original,amendment=amendmentpath,trial_plan=newplanpath,queue=newplan['queue'])
 packet['preview'].update(specification=str(root/packet['specification']),amendment=str(amp),trial_plan=str(np),handoff=str(hp),queue=str(qp))
 return packet,{'plan':newplan,'planfile':np,'queue':qp,'amendment':amp,'original':oldplan,'root':root,'wrapper':wrapper}

@pytest.mark.parametrize('kind,wrapper',[('transport_repair',False),('transport_repair',True),('retry',False),('retry',True)])
def test_valid_prospective_additive_packet_never_authorizes(tmp_path,kind,wrapper):
 packet,f=fixture(tmp_path,kind,wrapper)
 before={str(p):sha(p) for p in tmp_path.rglob('*') if p.is_file()}
 result=assess(tmp_path,packet)
 assert result['approvable'],result['blockers']
 assert result['execution_authorized'] is False
 assert before=={str(p):sha(p) for p in tmp_path.rglob('*') if p.is_file()}
 # Existing production preapproval rejects this extension; production tools stay unchanged.
 assert not ordinary_assess(tmp_path,packet)['approvable']
 with pytest.raises((FileNotFoundError,ExecutionError)):load_plan(tmp_path,tmp_path/packet['trial_plan'])

@pytest.mark.parametrize('damage,fragment',[
 ('science','scientific scope'),('resource','scientific scope'),('same_decision','fresh prospective'),('old_hash','original plan hash'),('source_closure','original source_sha256'),('spec_bytes','frozen specification bytes'),('coverage','archive coverage missing'),('archive_owner','archive'),('missing_lane','no lawful open lane'),('binding','binding mismatch'),('no_route','implementation route'),('input_hash','SHA-256'),('amendment_hash','amendment hash'),('unknown_override','unsupported override'),('existing_run','destination already exists'),('retry_old_run','fresh immutable RUN'),('retry_success','eligible terminal failure'),('retry_receipt_hash','SHA-256'),('wrapper_artifact','producer manifest'),('wrapper_command','wrapper command'),('wrapper_source','wrapper command'),('unsafe_plan_path','canonical path unsafe'),('handoff_memory','memory exceeds'),('zero_runs','zero-run task')])
def test_refusals(tmp_path,damage,fragment):
 retry=damage.startswith('retry_');wrapper=damage.startswith('wrapper_')
 packet,f=fixture(tmp_path,'retry' if retry else 'transport_repair',wrapper)
 plan=f['plan'];q=json.loads(f['queue'].read_text());am=json.loads(f['amendment'].read_text())
 if damage=='science':plan['trials'][0]['argv'].append('--new-prime')
 elif damage=='resource':plan['trials'][0]['memory_mb']*=2
 elif damage=='same_decision':packet['approval_decision_id']=f['original']['approved_by']
 elif damage=='old_hash':packet['original']['trial_plan_sha256']='0'*64
 elif damage=='source_closure':plan['source_sha256'].clear()
 elif damage=='spec_bytes':Path(packet['preview']['specification']).write_bytes(Path(packet['preview']['specification']).read_bytes()+b' ')
 elif damage=='coverage':q['tasks'][0]['artifact_paths'].pop(0)
 elif damage=='archive_owner':q['tasks'][1]['archive']['source_task_ids']=[]
 elif damage=='missing_lane':packet['lane_id']='BATCH-ffffff'
 elif damage=='binding':q['tasks'][0]['handoff']['execution']['trial_plan_sha256']='0'*64
 elif damage=='no_route':packet['execution_route']['reason']=''
 elif damage=='input_hash':plan['input_sha256']['driver.py']='0'*64
 elif damage=='amendment_hash':plan['amendment']['sha256']='0'*64
 elif damage=='unknown_override':am['protocol_amendment']['new_scientific_parameters']={'p':23}
 elif damage=='existing_run':(tmp_path/f"experiments/{packet['experiment_id']}/runs/{plan['trials'][0]['run_id']}").mkdir(parents=True)
 elif damage=='retry_old_run':plan['trials'][0]['run_id']=f['original']['trials'][0]['run_id']
 elif damage=='retry_success':
  rp=next(iter(am['protocol_amendment']['retry_receipts'].values()))['path'];r=json.loads((tmp_path/rp).read_text());r['status']='output_validated';put(tmp_path/rp,r)
 elif damage=='retry_receipt_hash':next(iter(am['protocol_amendment']['retry_receipts'].values()))['sha256']='0'*64
 elif damage=='wrapper_artifact':plan['trials'][0]['artifacts'].remove('producer-manifest.yaml')
 elif damage=='wrapper_command':plan['trials'][0]['check_argv'][3]='different-checker.py'
 elif damage=='unsafe_plan_path':packet['trial_plan']=f"experiments/{packet['experiment_id']}/amendments/../trial-plan.json"
 elif damage=='handoff_memory':q['tasks'][0]['handoff']['budget']['memory_gb']=0.01
 elif damage=='zero_runs':q['tasks'][0]['handoff']['budget']['maximum_runs']=0
 elif damage=='wrapper_source':am['protocol_amendment']['manifest_transport'][plan['trials'][0]['id']]['wrapper_source']['sha256']='0'*64
 if damage not in ('amendment_hash',):
  put(f['amendment'],am);plan['amendment']['sha256']=sha(f['amendment'])
 put(f['planfile'],plan)
 # Refresh coherent plan binding except deliberate binding damage, to test actual inner refusal.
 if damage!='binding':q['tasks'][0]['handoff']['execution']['trial_plan_sha256']=sha(f['planfile'])
 put(f['queue'],q);put(Path(packet['preview']['handoff']),{'handoff':q['tasks'][0]['handoff']})
 result=assess(tmp_path,packet);assert not result['approvable']
 assert any(fragment in x for x in result['blockers']),result['blockers']
