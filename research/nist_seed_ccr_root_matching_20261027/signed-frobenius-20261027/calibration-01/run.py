"""Frozen sequential producer/verifier, with failure receipts and completeness checks."""
import csv,datetime,hashlib,json,pathlib,platform,resource,subprocess,sys,time
P=pathlib.Path(__file__).resolve().parent;D=P/'.work'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def parse(name):return {k:int(v) for k,v in (line.split() for line in (D/name).read_text().splitlines())}
def main():
 for n,h in json.loads((P/'FROZEN-FILES.json').read_text()).items():assert digest(P/n)==h,n
 cfg=json.loads((P/'INPUTS.json').read_text())
 for n,h in cfg['input_files'].items():assert digest(D/n)==h,n
 build=json.loads((P/'BUILD.json').read_text());assert digest(D/'calibrate')==build['binary_sha256']
 for arm,timeout in [('enumerate',600),('verify',1800)]:
  start=time.monotonic();before=resource.getrusage(resource.RUSAGE_CHILDREN);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();cmd=[str(D/'calibrate'),arm,str(D)]
  with (D/(arm+'.stdout')).open('w') as stdout,(D/(arm+'.stderr')).open('w') as stderr:
   try:r=subprocess.run(cmd,cwd=P,stdout=stdout,stderr=stderr,timeout=timeout);rc=r.returncode;timedout=False
   except subprocess.TimeoutExpired:rc=None;timedout=True
  after=resource.getrusage(resource.RUSAGE_CHILDREN);receipt={'command':cmd,'returncode':rc,'timeout':timedout,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime,'host':platform.platform(),'binary_sha256':build['binary_sha256'],'stdout_sha256':digest(D/(arm+'.stdout')),'stderr_sha256':digest(D/(arm+'.stderr'))};(D/(arm+'-receipt.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(arm,'returncode',rc,'timeout',timedout,flush=True)
  if rc!=0 or timedout:raise SystemExit(1)
  marker='ENUMERATOR_COMPLETE' if arm=='enumerate' else 'VERIFIER_COMPLETE';assert marker in (D/(arm+'.stdout')).read_text()
 a=parse('enumerator-summary.txt');b=parse('verifier-summary.txt')
 for k in b:
  if k in a:assert a[k]==b[k],k
 assert a['labels']==4480 and a['endpoint_labels']==126 and a['pairs']==3252525 and a['truth_functions']==52040400
 rows=list(csv.DictReader((D/'coverage.csv').open()));assert len(rows)==4480;assert len(list(csv.DictReader((D/'level-coverage.csv').open())))==61
 result={'status':'PASS','complete':True,'enumerator':a,'verifier':b,'controls':'PASS: full four-bin coverage, XOR, collision, unknown and A/A in both modes','all_coverage_witnesses_and_absences_checked':True,'all_61_cap_coverage_bits_independently_checked':True,'limitations':['Descriptive capacity on fixed observations, not historical choice probabilities or an exchangeability assertion.','Model classes were selected with previous labels and fits already visible; no retroactive preregistration.','No new curves, point counts, torsion measurements or held-out historical choices.','Endpoint-conditioned reference fixes the P224/P256 decisions and varies only early192/239-bit publication positions.'],'historical_criterion_identified':False};(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
