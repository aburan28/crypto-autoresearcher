"""Serialize retained two-arm observations; does not evaluate new witnesses."""
import copy,datetime,hashlib,json,platform,sys
from pathlib import Path
P=Path(sys.argv[1]).resolve();R=next(x for x in P.parents if (x/'schemas/experiment-export.v1.json').exists())
T=R/'research/nist_seed_ccr_root_matching_20261027/signed-frobenius-20261027/period-eigenvalue-20261027/export.json'
e=json.loads(T.read_text());protocol=json.loads((P/'experiment.protocol.json').read_text());W=P/'runs/certificate-01';source=json.loads((W/'source.json').read_text())
def file(p,kind='raw'):
    b=p.read_bytes();return {'path':str(p.relative_to(P)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'kind':kind}
e['export_id']=protocol['protocol_id']+'-v'+str(protocol['version'])+'-export';e['created']=datetime.datetime.now(datetime.timezone.utc).isoformat()
e['protocol']={'path':'experiment.protocol.json','sha256':protocol['freeze']['protocol_sha256'],'protocol_id':protocol['protocol_id'],'version':protocol['version']}
e['analysis']={'blinded':False,'blinding_key_sha256':None,'unmasked_at':None,'script':file(P/'run.py','analysis'),'outputs':[file(W/'RESULT.json','analysis')]}
e['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':a['instrument']['binary_sha256'],'commit':source['commit']} for a in protocol['arms']]
e['source']={'repo':'crypto-autoresearcher','commit':source['commit'],'dirty':source['dirty']}
e['host'].update(path=str((W/'source.json').relative_to(P)),sha256=file(W/'source.json')['sha256'],class_id='macos-arm64-class-number-certificate')
e['host']['summary']['kernel']=platform.release()
e['files']=[file(p) for p in sorted(W.iterdir()) if p.is_file()]+[file(P/n,'other') for n in ['INPUTS.json','inputs.gp','FROZEN-FILES.json']]
template=e['runs'][0];e['runs']=[]
for a in protocol['arms']:
    arm=a['id'];r=json.loads((W/(arm+'-receipt.json')).read_text());x=copy.deepcopy(template)
    x.update(arm=arm,run_id=protocol['protocol_id']+'-v'+str(protocol['version'])+'-'+arm,backend_ref=str((W/(arm+'-receipt.json')).relative_to(P)),started_at=r['started_at'],finished_at=r['finished_at'])
    x['artifacts']=[file(W/(arm+s)) for s in ['.stdout','.stderr','-receipt.json']]
    x['measurements'].update(wall_seconds=r['wall_seconds_diagnostic'],cpu_user_seconds=r['cpu_user_seconds'],cpu_sys_seconds=r['cpu_sys_seconds'],counted={'cohort_rows':21})
    x['isolation']['blockers']=['Shared desktop; exact counted certificate records only; no timing inference']
    x['verification']['verifier']='Exact agreement of both full21 outputs; embedded controls and source factor prime proofs passed. See retained guard receipts.'
    e['runs'].append(x)
e['backend_record']={'status':'complete','note':'Two whole-cohort evaluations. Two deliberate failure-guard invocations are embedded controls, with original failure stdout/stderr/receipts retained.'}
e['notes']=[{'by':'Codex T-5518','kind':'observation','text':'All21 rows retained, including missing-D_K unknowns. Result contains sufficient class-number lower-bound certificates, not exact class numbers or historical-use evidence.'}]
(P/'export.json').write_text(json.dumps(e,indent=2,sort_keys=True)+'\n')
print(e['export_id'])
