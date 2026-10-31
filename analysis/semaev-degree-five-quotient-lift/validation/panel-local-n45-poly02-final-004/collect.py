from pathlib import Path
import json,hashlib,re,tarfile,shutil,os
D=Path('analysis/semaev-degree-five-quotient-lift');raw=Path('/home/ec2-user/fall-degree-data-20261029/panel-local-n45-poly02-004');a=raw/'attempt-001';plan=json.loads((D/'panel-local-n45-poly02-plan-004.json').read_text());req=json.loads((a/'request.json').read_text());res=json.loads((a/'result.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
assert json.loads((raw/'terminal.json').read_text())['returncode']==0
assert res['status']=='certificate_verified' and res['id']==req['id']
assert h(a/'request.json')==plan['hashes'][plan['request']]
for name,sha in res['artifacts'].items():assert h(a/name)==sha,name
for name in ['controls','count','produce','check']:
 st=res['steps'][name];assert st['returncode']==0 and st['timeout'] is False
argv=json.loads((a/'check.argv.json').read_text());r=req['record'];assert argv[3:]==list(map(str,[r['n'],r['modulus_hex'],r['a2'],r['a6_hex'],r['z_hex'],*r['V_basis_hex']]))
accepted=re.search(r'VALID: 1 is not in W_4\(F\), and codim W_4\(F\) >= (\d+)',(a/'check.stdout.txt').read_text());assert accepted;assert int(accepted[1])==res['certified_codimension_lower_bound'];assert res['certified_codimension_lower_bound']>6;assert int((a/'count.stdout.txt').read_text())==res['exact_solutions']==6;assert res['last_fall_degree_lower_bound']==5
v=D/'validation/panel-local-n45-poly02-final-004';v.mkdir(exist_ok=False);shutil.copy2(a/'result.json',v/'result.json');shutil.copy2(raw/'terminal.json',v/'terminal.json')
manifest=[]
with tarfile.open(v/'raw-evidence.tar.gz','w:gz') as t:
 for p in sorted(raw.rglob('*')):
  if p.is_file():
   rel=str(p.relative_to(raw));manifest.append({'path':rel,'bytes':p.stat().st_size,'sha256':h(p),'in_raw_archive':p != a/'certificate.bin'})
   if p != a/'certificate.bin':t.add(p,arcname=rel,recursive=False)
save(v/'manifest.json',{'files':manifest,'certificate_location':str(a/'certificate.bin'),'scope':'Closed local run, original independent checker and exact count accepted; public certificate publication recorded separately.'})
nroot=Path('/home/ec2-user/fall-degree-data-20261029/panel-local-publication-001');dst=nroot/req['id']/'attempt-001';dst.mkdir(parents=True,exist_ok=False)
for p in a.iterdir():
 if p.is_file() and p.name not in ['result.json','certificate.bin']:shutil.copy2(p,dst/p.name)
os.link(a/'certificate.bin',dst/'certificate.bin');shutil.copy2(a/'result.json',dst/'worker-result.json');shutil.copy2(v/'raw-evidence.tar.gz',dst/'complete-raw-evidence.tar.gz')
origin={'original_result':str(a/'result.json'),'original_result_sha256':h(a/'result.json'),'original_request_sha256':h(a/'request.json'),'frozen_plan_sha256':h(D/'panel-local-n45-poly02-plan-004.json'),'scope':'Publication-format projection only; original worker evidence unchanged'};save(dst/'origin.json',origin)
normalized=dict(schema='semaev.panel-publication/v1',id=req['id'],status='certificate_verified',parameters={'degree':4,'chain':False,'record':req['record']},certificate_sha256=res['certificate_sha256'],certified_codimension_lower_bound=res['certified_codimension_lower_bound'],exact_solutions=res['exact_solutions'],last_fall_degree_lower_bound=5,provenance=origin,artifacts={p.name:{'bytes':p.stat().st_size,'sha256':h(p)} for p in dst.iterdir() if p.is_file()});save(dst/'result.json',normalized)
print(json.dumps({'artifacts_verified':len(res['artifacts']),'certificate_bytes':(a/'certificate.bin').stat().st_size,'certificate_sha256':res['certificate_sha256'],'checked_codimension':res['certified_codimension_lower_bound'],'exact_solutions':6,'lfd_lower_bound':5,'archive_bytes':(v/'raw-evidence.tar.gz').stat().st_size}))
