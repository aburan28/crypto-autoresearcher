"""Prepare the pinned large-input command only after blocked cloud qualification."""
import ast,hashlib,json
from pathlib import Path
s=Path(__file__).resolve().parent.parent
request=s/'runtime/rand02-blocked-frontier-request-001.json'
protocol=s/'rand02-blocked-frontier-protocol-001.json'
p=json.loads(protocol.read_text());assert p['freeze']['status']=='frozen'
qualification=s/p['links']['qualification_export'];assert hashlib.sha256(qualification.read_bytes()).hexdigest()==p['links']['qualification_export_sha256']
e=json.loads(qualification.read_text());assert e['flow']['completed']==9 and e['flow']['not_completed']==0
r=json.loads(request.read_text());assert hashlib.sha256(request.read_bytes()).hexdigest()==p['links']['request_sha256s'][0]
assert r['worker_manifest_sha256']==p['links']['worker_manifest_sha256']
job=json.loads((s/'runtime/checkpoint-frontier-job-001.json').read_text());code=''.join(job['command'][3:])
values={'URL':p['links']['worker_url'],'ARCHIVE_SHA':p['links']['worker_archive_sha256'],'REQUEST':request.read_text(),'REQUEST_SHA':hashlib.sha256(request.read_bytes()).hexdigest(),'PROTOCOL':protocol.read_text(),'PROTOCOL_BYTES_SHA':hashlib.sha256(protocol.read_bytes()).hexdigest()}
lines=code.splitlines(keepends=True)
for key,value in values.items():
 indices=[i for i,line in enumerate(lines) if line.startswith(key+'=')];assert len(indices)==1;lines[indices[0]]=key+'='+repr(value)+'\n'
code=''.join(lines);compile(code,'frontier-command','exec');job['command']=job['command'][:3]+[code[i:i+6000] for i in range(0,len(code),6000)];assert all(len(x.encode())<=8192 for x in job['command'])
job['job_name']='semaev-n47-rand02-d5-blocked-20261030-2120'
output=s/'runtime/rand02-blocked-frontier-job-001.json'
with output.open('x') as f:json.dump(job,f,indent=2);f.write('\n')
print(output)
