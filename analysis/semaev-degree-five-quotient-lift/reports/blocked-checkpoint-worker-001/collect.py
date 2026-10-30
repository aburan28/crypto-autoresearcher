#!/usr/bin/env python3
"""Recompute worker-control report from frozen actual rows and hashed archive."""
import copy,datetime,hashlib,json,shutil,tarfile
from pathlib import Path
import typst
r=Path(__file__).resolve().parent;s=r.parent.parent;v=s/'validation/blocked-checkpoint-worker-001'
def art(n,kind='raw'):
 p=r/n;return dict(path=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,kind=kind)
manifest=json.loads((v/'raw-manifest.json').read_text())
with tarfile.open(v/'raw-evidence.tar.gz') as t:
 for e in manifest['files']:
  data=t.extractfile(e['path']).read();assert len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256']
 generations={str(i):sum(1 for e in manifest['files'] if e['path'].startswith(f'{i}-restored/work/snapshots/') and e['path'].endswith('.publication.json')) for i in range(3)}
 restores={str(i):json.load(t.extractfile(f'{i}-restored/work/restore.json')) for i in range(3)}
 results={f'{i}-{m}':json.load(t.extractfile(f'{i}-{m}/work/result.json')) for i in range(3) for m in ['fresh','source','restored']}
for name in ['result.json','raw-manifest.json','raw-evidence.tar.gz']:shutil.copyfile(v/name,r/name)
shutil.copyfile(s/'blocked-checkpoint-worker-protocol-001.json',r/'protocol.json');shutil.copyfile(s/'qualify_checkpoint_worker.py',r/'qualify_checkpoint_worker.py')
p=json.loads((r/'protocol.json').read_text());rows=json.loads((r/'result.json').read_text())['rows'];assert len(rows)==9 and all(x['passed'] for x in rows)
text=f'''# Blocked producer worker integration controls

Observations only. The new blocked native binary is exercised through the unchanged actual worker. Restored publication counts are derived from archived acknowledgments. All nine actual local controls passed: fresh completion, deliberate checkpoint stop, and restored completion for each of three retained Semaev fixtures. The six completed exports match the retained certificate hashes, and the original independent checker accepts each. Fresh exact solution counts and accepted codimensions are 3, 1, and 1 for fixtures 0, 1, and 2. No inequality supporting LFD at least 6 occurs.

The three source controls intentionally stop after checkpoint publication; they are not completed certificates. Restored workers use the same request and verified source state, and complete the original checker and exact count again. Seed inputs are streamed from fixed gzip files through the URL transfer interface. Storage is local fake AWS; these controls do not establish cloud permissions or frontier memory/disk admission. The separate export-guard controls cover explicit refusals and corruption.

All {len(manifest['files'])} archived file sizes and hashes verify. Nine actual rows, one attempt each, no exclusions. Logs are bounded and timings are diagnostic only. Frozen source commit: {p['freeze']['commit']}. Frozen protocol: {p['freeze']['protocol_sha256']}.

![Recorded worker outcomes](outcomes.svg)

The running frontier worker is unchanged. These small controls are not frontier memory admission or a timing comparison. Forty original high-memory inputs and ten panel inputs remain unfinished. No new mathematical bound is claimed.
''';(r/'report.md').write_text(text)
svg='<svg xmlns="http://www.w3.org/2000/svg" width="720" height="230"><rect width="720" height="230" fill="white"/><g font-family="sans-serif" font-size="15" fill="#172b4d"><text x="20" y="30">Worker controls: 9 / 9 passed; 6 checked certificates</text><text x="180" y="65">Fresh</text><text x="330" y="65">Checkpoint stop</text><text x="525" y="65">Restored</text>'
for i in range(3):
 y=100+35*i;svg+=f'<text x="20" y="{y}">Fixture {i}</text><text x="180" y="{y}">Verified</text><text x="330" y="{y}">Checkpointed</text><text x="525" y="{y}">Verified</text>'
svg+='<text x="20" y="215">Local fake storage; no new LFD bound; no timing inference.</text></g></svg>';(r/'outcomes.svg').write_text(svg)
typ='''#set page(paper: "a4", margin: 22mm)
#set text(size: 10pt)
= Blocked producer worker integration controls
Observations only. The new blocked native binary is exercised through the unchanged actual worker. Restored publication counts are derived from archived acknowledgments. All nine actual local controls passed: fresh completion, deliberate checkpoint stop, and restored completion for three retained Semaev fixtures. Six completed certificates match their retained references and pass the original independent checker. Accepted codimension and fresh exact solution count agree: 3, 1, and 1 for fixtures 0, 1, and 2. No new LFD lower bound follows.

#image("outcomes.svg", width: 100%)

Three source controls intentionally stop after durable publication. They are not completed certificates. All restored workers verify source state, rerun the checker and count, and complete the certificate.

Seeds are streamed through the URL transfer interface from fixed gzip files. Storage is a local fake AWS service. These controls do not qualify cloud permissions, large-file recovery, or frontier resource admission. Timings are diagnostic only.

The archive contains FILECOUNT individually verified files. Nine actual rows ran once each with no exclusions. The frozen protocol, raw manifest, exact launch commands, capped logs, request files and result records accompany the report.

The running frontier worker is unchanged. Forty original high-memory inputs and ten panel inputs remain unfinished. The new binary cannot restore the old binary checkpoints. No new mathematical bound is claimed.
'''.replace('FILECOUNT',str(len(manifest['files'])));(r/'report.typ').write_text(typ);typst.compile(str(r/'report.typ'),output=str(r/'report.pdf'))
d=json.loads((r.parent/'export-guard-001/export.json').read_text());template=copy.deepcopy(d['runs'][0]);d.update(export_id='SEMAEV-BLOCKED-CHECKPOINT-WORKER-001',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=dict(repo='crypto-autoresearcher',commit=p['freeze']['commit'],dirty=False));d['protocol']=dict(path='protocol.json',sha256=p['freeze']['protocol_sha256'],protocol_id=p['protocol_id'],version=1);d['arms']=[dict(id=a['id'],role=a['role'],binary_sha256=a['instrument']['binary_sha256'],commit=a['instrument']['commit']) for a in p['arms']];d['runs']=[]
for row in rows:
 t=copy.deepcopy(template);t.update(run_id=row['arm']+'-'+row['instance_id'],arm=row['arm'],instance_id=row['instance_id']);t['verification']['verifier']='Frozen worker assertions, original checker, retained certificate bytes and fresh exact count';t['artifacts']=[art('result.json')]
 if row['arm']=='restored':t.update(resumed=1,checkpoint=dict(policy='application',generations_written=generations[row['instance_id']],restored_from_generation=restores[row['instance_id']]['snapshot']['sequence']))
 d['runs'].append(t)
d['flow']=dict(planned=9,attempted=9,completed=9,not_completed=0,interrupted=0,resumed=3,excluded=[]);d['files']=[art(n) for n in ['result.json','raw-manifest.json','raw-evidence.tar.gz']];d['analysis']=dict(script=art('qualify_checkpoint_worker.py','analysis'),blinded=False,blinding_key_sha256=None,outputs=[art(n,'report') for n in ['report.md','report.typ','report.pdf','outcomes.svg']]+[art('collect.py','analysis')],unmasked_at=None);d['notes']=[dict(kind='observation',by='Codex',text='Nine local worker controls pass; source rows are deliberate checkpoint stops. No cloud or frontier qualification and no new LFD lower bound.')];(r/'export.json').write_text(json.dumps(d,indent=2)+'\n');print(len(manifest['files']),'files;',len(rows),'rows')
