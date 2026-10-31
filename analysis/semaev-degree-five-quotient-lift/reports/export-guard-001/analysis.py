#!/usr/bin/env python3
"""Build an exact software-control report from immutable raw rows."""
import copy,hashlib,json,shutil,tarfile,datetime
from pathlib import Path
r=Path(__file__).resolve().parent;s=r.parent.parent;v=s/'validation/export-guard-001'
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def artifact(name,kind='raw'):
 p=r/name;return dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,kind=kind)
manifest=json.loads((v/'raw-manifest.json').read_text())
with tarfile.open(v/'raw-evidence.tar.gz') as t:
 for e in manifest['files']:
  b=t.extractfile(e['path']).read();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
for name in ['result.json','raw-manifest.json','raw-evidence.tar.gz']:shutil.copyfile(v/name,r/name)
shutil.copyfile(s/'export-guard-protocol-001.json',r/'protocol.json')
shutil.copyfile(s/'qualify_export_guard.py',r/'qualify_export_guard.py')
p=json.loads((r/'protocol.json').read_text());rows=json.loads((r/'result.json').read_text())['rows']
assert len(rows)==20 and all(x['passed'] for x in rows)
text='''# Export admission guard controls

All 20 actual local software controls passed: ten fresh-path and ten restored-path cases. Allowed native exports match the frozen 1616-byte reference certificate. Fresh refusal publishes and verifies the phase-2 checkpoint before deferring export; restored refusal prevents native execution. The exact byte boundary allows export and one byte below refuses. Corrupt checkpoints, mismatched identities and existing output paths are rejected. Phase-1 handling and certificate word-count arithmetic also pass.

Storage is a local fake AWS service. The boundary arithmetic cases use the same direct prelaunch path in both configurations, as preregistered. This is not a large-file, cloud-worker or mathematical qualification. No new LFD lower bound follows. Frontier worker integration and end-to-end controls remain required before the next large run.

All 169 archived files were verified against their recorded sizes and SHA-256 hashes. Both configurations ran once with no retries; no outcomes were excluded. Timings are diagnostic only on a shared host.

![Actual case outcomes](outcomes.svg)
'''
(r/'report.md').write_text(text)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="380" viewBox="0 0 720 380"><rect width="720" height="380" fill="white"/><g font-family="sans-serif" font-size="15" fill="#172b4d"><text x="20" y="28">Export guard: 20 / 20 fixed software controls passed</text><text x="375" y="58">Fresh</text><text x="500" y="58">Restored</text>']
for i,x in enumerate(rows[:10]):
 y=85+i*26;svg.append(f'<text x="20" y="{y}">{x["case"]}</text><text x="375" y="{y}" fill="#176341">PASS</text><text x="500" y="{y}" fill="#176341">PASS</text>')
svg.append('<text x="20" y="365">Local fake storage; no new LFD bound; no performance claim.</text></g></svg>');(r/'outcomes.svg').write_text(''.join(svg))
d=json.loads((r.parent/'checkpoint-matrix-cloud-001/export.json').read_text());template=copy.deepcopy(d['runs'][0]);d.update(export_id='SEMAEV-EXPORT-GUARD-001',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),backend='local',source=dict(repo='crypto-autoresearcher',commit=p['freeze']['commit'],dirty=False));d['protocol']=dict(path='protocol.json',sha256=p['freeze']['protocol_sha256'],protocol_id=p['protocol_id'],version=1)
d['arms']=[dict(id=a['id'],role=a['role'],binary_sha256=a['instrument']['binary_sha256'],commit=a['instrument']['commit']) for a in p['arms']];d['runs']=[]
for row in rows:
 t=copy.deepcopy(template);t.update(run_id=row['arm']+'-'+row['instance_id'],arm=row['arm'],instance_id=row['instance_id'],resumed=0,checkpoint=None);t['verification']['verifier']='Frozen export guard scenario assertions and retained reference bytes';t['isolation']['blockers']=['Shared local host; no performance claim'];t['artifacts']=[artifact('result.json')];d['runs'].append(t)
d['flow']=dict(planned=20,attempted=20,completed=20,not_completed=0,interrupted=0,resumed=0,excluded=[]);d['files']=[artifact(n) for n in ['result.json','raw-manifest.json','raw-evidence.tar.gz']];d['analysis']=dict(script=artifact('qualify_export_guard.py','analysis'),blinded=False,blinding_key_sha256=None,outputs=[artifact('report.md','report'),artifact('outcomes.svg','report'),artifact('analysis.py','analysis')],unmasked_at=None);d['notes']=[dict(kind='observation',by='Codex',text='Twenty fixed local software controls pass. No cloud, frontier, performance or new LFD bound inference.')];write(r/'export.json',d)
print('Verified',len(manifest['files']),'raw files and',len(rows),'actual rows')
