#!/usr/bin/env python3
"""Recompute worker-control report from frozen actual rows and hashed archive."""
import copy,datetime,hashlib,json,shutil,tarfile
from pathlib import Path
import typst
r=Path(__file__).resolve().parent;s=r.parent.parent;v=s/'validation/blocked-checkpoint-worker-cloud-002'
def art(n,kind='raw'):
 p=r/n;return dict(path=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size,kind=kind)
source_status=json.loads((s/'runs/blocked-worker-cloud-source-terminal-002.json').read_text())
restore_status=json.loads((s/'runs/blocked-worker-cloud-restore-terminal-002.json').read_text())
assert source_status['job']['state']=='succeeded' and restore_status['job']['state']=='succeeded'
source_pod=source_status['pods'][0]['uid'];restore_pod=restore_status['pods'][0]['uid'];assert source_pod!=restore_pod
for label in ['source','restore']:shutil.copyfile(s/f'runs/blocked-worker-cloud-{label}-terminal-002.json',r/f'{label}-terminal.json')
manifest=json.loads((v/'raw-manifest.json').read_text())
with tarfile.open(v/'raw-evidence.tar.gz') as t:
 for e in manifest['files']:
  data=t.extractfile(e['path']).read();assert len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256']
 generations={str(i):sum(1 for e in manifest['files'] if e['path'].startswith(f'restored/worker-controls/{i}/restored/lift/checkpoints/manifests/') and e['path'].endswith('.json')) for i in range(3)}
 restores={str(i):json.load(t.extractfile(f'restored/worker-controls/{i}/restored/lift/restore.json')) for i in range(3)}
 results={f'{i}-{m}':json.load(t.extractfile(f'{"restored" if m=="restored" else "source"}/worker-controls/{i}/{m}/lift/result.json')) for i in range(3) for m in ['fresh','source','restored']}
fixtures=json.loads((s/'runtime/blocked-checkpoint-worker-cloud-001/manifest.json').read_text())['fixtures']
for i,f in enumerate(fixtures):
 for mode in ['fresh','source','restored']:
  d=results[f'{i}-{mode}'];assert d['exact_solutions']==f['count'] and 'last_fall_degree_lower_bound' not in d
  assert d['steps']['check4']['returncode']==0 and d['steps']['count']['returncode']==0
  if mode=='source':assert d['status']=='checkpointed_control' and d['steps']['produce5']['returncode']==75
  else:assert d['status']=='certificate_verified' and d['steps']['check5']['returncode']==0 and d['certificate_sha256']==f['expected_sha256'] and d['certified_codimension_lower_bound']==f['count']
for name in ['result.json','raw-manifest.json','raw-evidence.tar.gz']:shutil.copyfile(v/name,r/name)
shutil.copyfile(s/'blocked-checkpoint-worker-cloud-protocol-002.json',r/'protocol.json');shutil.copyfile(s/'qualify_checkpoint_worker_cloud.py',r/'qualify_checkpoint_worker_cloud.py')
p=json.loads((r/'protocol.json').read_text());rows=json.loads((r/'result.json').read_text())['rows'];assert len(rows)==9 and all(x['passed'] for x in rows)
text=f'''# Blocked checkpoint worker cloud controls

Observations only. All nine actual cloud controls passed: fresh completion, deliberate checkpoint stop, and restored completion for each of three retained Semaev fixtures. The six completed exports match the retained certificate hashes, and the original independent checker accepts each. Fresh exact solution counts and accepted codimensions are 3, 1, and 1 for fixtures 0, 1, and 2. The fixture counts equal their accepted codimensions.

The three source controls intentionally stop after checkpoint publication; they are not completed certificates. Restored workers use the same request and verified source state, and complete the original checker and exact count again. Seed inputs are streamed from fixed gzip files through the URL transfer interface. Storage is real S3 with conditional publication and full readback. Source and restore use distinct pods. These small controls do not establish frontier memory/disk admission. The separate export-guard controls cover explicit refusals and corruption. The first blocked cloud source attempt reached its scheduling deadline without executing controls; its terminal evidence remains preserved. Version 2 keeps the same fixtures, bundle, and resource limits.

Source pod: `{source_pod}`. Restore pod: `{restore_pod}`.

All {len(manifest['files'])} archived file sizes and hashes verify. Nine actual rows, one attempt each, no exclusions. Logs are bounded and timings are diagnostic only. Frozen source commit: {p['freeze']['commit']}. Frozen protocol: {p['freeze']['protocol_sha256']}.

![Recorded worker outcomes](outcomes.svg)

Next: admit the retained n=47 frontier request using this qualified worker. The 40 unfinished high-memory inputs and eight unfinished panel inputs remain in scope. The next large-input run is n47 random02, using its retained D4 seed and fresh exact count.
''';(r/'report.md').write_text(text)
svg='<svg xmlns="http://www.w3.org/2000/svg" width="720" height="230"><rect width="720" height="230" fill="white"/><g font-family="sans-serif" font-size="15" fill="#172b4d"><text x="20" y="30">Worker controls: 9 / 9 passed; 6 checked certificates</text><text x="180" y="65">Fresh</text><text x="330" y="65">Checkpoint stop</text><text x="525" y="65">Restored</text>'
for i in range(3):
 y=100+35*i;svg+=f'<text x="20" y="{y}">Fixture {i}</text><text x="180" y="{y}">Verified</text><text x="330" y="{y}">Checkpointed</text><text x="525" y="{y}">Verified</text>'
svg+='<text x="20" y="215">Distinct cloud pods; exact checks; diagnostic clocks.</text></g></svg>';(r/'outcomes.svg').write_text(svg)
typ='''#set page(paper: "a4", margin: 22mm)
#set text(size: 10pt)
= Blocked checkpoint worker cloud controls
Observations only. All nine actual cloud controls passed: fresh completion, deliberate checkpoint stop, and restored completion for three retained Semaev fixtures. Six completed certificates match their retained references and pass the original independent checker. Accepted codimension and fresh exact solution count agree: 3, 1, and 1 for fixtures 0, 1, and 2. These fixtures verify the worker and recovery path.

#image("outcomes.svg", width: 100%)

Three source controls intentionally stop after durable publication. They are not completed certificates. All restored workers verify source state, rerun the checker and count, and complete the certificate.

Seeds are streamed through the URL transfer interface from fixed gzip files. Storage is real S3 with conditional publication and full readback. Source and restore use distinct pods. These small controls do not qualify large-file recovery or frontier resource admission. Timings are diagnostic only.

The archive contains FILECOUNT individually verified files. Nine actual rows ran once each with no exclusions. The frozen protocol, raw manifest, exact launch commands, capped logs, request files and result records accompany the report.

Next: admit the retained n=47 frontier request. Forty high-memory inputs and eight panel inputs remain unfinished.
'''.replace('FILECOUNT',str(len(manifest['files'])));(r/'report.typ').write_text(typ);typst.compile(str(r/'report.typ'),output=str(r/'report.pdf'))
d=json.loads((r.parent/'export-guard-001/export.json').read_text());template=copy.deepcopy(d['runs'][0]);d['backend']='isolab-k8s';d.update(export_id='SEMAEV-BLOCKED-WORKER-CLOUD-002',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=dict(repo='crypto-autoresearcher',commit=p['freeze']['commit'],dirty=False));d['protocol']=dict(path='protocol.json',sha256=p['freeze']['protocol_sha256'],protocol_id=p['protocol_id'],version=p['version']);d['arms']=[dict(id=a['id'],role=a['role'],binary_sha256=a['instrument']['binary_sha256'],commit=a['instrument']['commit']) for a in p['arms']];d['runs']=[]
for row in rows:
 t=copy.deepcopy(template);t.update(run_id=row['arm']+'-'+row['instance_id'],arm=row['arm'],instance_id=row['instance_id']);t['verification']['verifier']='Frozen worker assertions, original checker, retained certificate bytes and fresh exact count';t['artifacts']=[art('result.json')]
 if row['arm']=='restored':t.update(resumed=1,checkpoint=dict(policy='application',generations_written=generations[row['instance_id']],restored_from_generation=restores[row['instance_id']]['snapshot']['sequence']))
 d['runs'].append(t)
d['flow']=dict(planned=9,attempted=9,completed=9,not_completed=0,interrupted=0,resumed=3,excluded=[]);d['files']=[art(n) for n in ['result.json','raw-manifest.json','raw-evidence.tar.gz','source-terminal.json','restore-terminal.json']];d['analysis']=dict(script=art('qualify_checkpoint_worker_cloud.py','analysis'),blinded=False,blinding_key_sha256=None,outputs=[art(n,'report') for n in ['report.md','report.typ','report.pdf','outcomes.svg']]+[art('collect.py','analysis')],unmasked_at=None);d['notes']=[dict(kind='observation',by='Codex',text='Nine real-cloud worker controls pass across distinct pods; source rows deliberately stop at checkpoints. No frontier resource qualification or new LFD lower bound.')];(r/'export.json').write_text(json.dumps(d,indent=2)+'\n');print(len(manifest['files']),'files;',len(rows),'rows')
