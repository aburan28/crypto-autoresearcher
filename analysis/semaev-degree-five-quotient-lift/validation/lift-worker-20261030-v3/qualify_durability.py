import importlib.util,json,os,sys,subprocess,shutil
from pathlib import Path
from unittest.mock import patch
source=Path('analysis/semaev-degree-five-quotient-lift/run_lift_worker_durable.py')
spec=importlib.util.spec_from_file_location('worker',source); w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
root=Path('/home/ec2-user/fall-degree-data-20261029/lift-durability-control-003');root.mkdir()
remote=root/'mock-upload';remote.mkdir()
realrun=subprocess.run; realpopen=subprocess.Popen
uploads=[]
def run(argv,**kwargs):
 if argv[0]=='aws':
  src=Path(argv[3]);dest=remote/src.name;assert src.exists();shutil.copyfile(src,dest);uploads.append(src.name)
  return subprocess.CompletedProcess(argv,0)
 return realrun(argv,**kwargs)
def popen(argv,**kwargs):
 if any(str(x).endswith('cert_check.py') for x in argv) and str(root/'out/seed.bin') in argv:
  assert (remote/'check4.started.json').exists()
  assert (remote/'seed-transfer.finished.json').exists()
  raise SystemExit('simulated abrupt termination before check4 child')
 return realpopen(argv,**kwargs)
args=['worker','--bundle','/home/ec2-user/fall-degree-runtime-20261029/bounded-lift-worker-003','--request','/tmp/bounded-lift-control-request-003.json','--out',str(root/'out'),'--upload']
with patch.object(sys,'argv',args),patch.dict(os.environ,{'ISOLAB_RESULTS_URI':'s3://mock-test/'}),patch.object(w,'placement',return_value={'memory.max':str(3<<30),'memory.current':'0'}),patch.object(w.subprocess,'run',side_effect=run),patch.object(w.subprocess,'Popen',side_effect=popen):
 try:w.main()
 except SystemExit as e:assert str(e)=='simulated abrupt termination before check4 child'
 else:raise AssertionError('interruption not exercised')
assert not (remote/'check4.finished.json').exists()
assert not (remote/'result.json').exists()
assert not (remote/'seed.bin').exists()
(root/'verification.json').write_text(json.dumps({'status':'passed','scope':'Mock S3 and placement; real small-fixture children. Not cloud qualification.','injected_failure':'before check4 Popen','started_event_uploaded_before_child':True,'seed_hash_event_uploaded':True,'no_false_completion_or_partial_seed_uploaded':True,'uploaded_files':uploads},indent=2)+'\n')
print('durability interruption control PASS')
