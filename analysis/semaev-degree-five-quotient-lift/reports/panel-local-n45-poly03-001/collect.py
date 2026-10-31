from pathlib import Path
import copy,datetime,hashlib,json,shutil,tarfile
import typst
s=Path('analysis/semaev-degree-five-quotient-lift');v=s/'validation/panel-local-n45-poly03-final-001';r=s/'reports/panel-local-n45-poly03-001';r.mkdir(exist_ok=False);x=json.loads((v/'result.json').read_text());p=json.loads((s/'panel-local-n45-poly03-protocol-001.json').read_text());m=json.loads((v/'manifest.json').read_text())
with tarfile.open(v/'raw-evidence.tar.gz') as t:
 for e in m['files']:
  if e['in_raw_archive']:
   b=t.extractfile(e['path']).read();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
for a,b in [(v/'result.json','result.json'),(v/'manifest.json','manifest.json'),(v/'raw-evidence.tar.gz','raw-evidence.tar.gz'),(s/'panel-local-n45-poly03-protocol-001.json','protocol.json'),(s/'run_panel_worker_v2.py','run_panel_worker_v2.py')]:shutil.copy2(a,r/b)
sha=x['certificate_sha256'];q=x['certified_codimension_lower_bound'];count=x['exact_solutions'];assert q>count and count==6 and x['last_fall_degree_lower_bound']==5

plan=json.loads((s/'panel-local-n45-poly03-plan-001.json').read_text())
assert hashlib.sha256((s/p['links']['plan']).read_bytes()).hexdigest()==p['links']['plan_sha256']
for name in p['analysis_plan']['inputs']:
 assert (s/name).is_file(),name
inv=json.loads((s/'runtime/panel-remaining-after-local006.json').read_text())
assert inv['terminal_count']==26 and inv['certified_lfd_at_least5']==19 and len(inv['items'])==6
text=f"""# Certified n45 polynomial03: LFD at least five

The original independent checker accepted the degree-four certificate for fresh-n45-poly-03. All 46 variable multiplication checks passed. The accepted codimension lower bound is {q:,}; fresh exhaustive Boolean enumeration found {count} solutions. The strict inequality proves LFD at least five for this exact input presentation.

The certificate contains 288,550,808 bytes with SHA-256 {sha}. All {len(x['artifacts'])} worker-recorded artifact hashes and the hash-pinned request identity were verified after successful terminal return. The controls, counter, producer and checker completed without timeout. The raw archive retains the small control certificates and all closed records except the separately retained main certificate.

This is the first scientific panel use of the separately qualified RREF exporter. Its 14 prior qualification rows passed; all three per-worker controls reproduced the reference certificate bytes and exhaustive counts. Admission passed on the first sample with 48,285,126,656 bytes available against the 40 GiB child cap plus 2 GiB reserve. Both campaign locks were held. The original independent checker remains the acceptance gate. No runtime comparison is claimed.

The original 32-input panel now has {inv['terminal_count']} terminal inputs and {inv['certified_lfd_at_least5']} certified LFD-at-least-five results; {len(inv['items'])} original inputs remain. This completes an existing input, with no replacement draw. The separate n47 random02 degree-five cloud run is in progress.

Full certificate: /home/ec2-user/fall-degree-data-20261029/panel-local-n45-poly03-001/attempt-001/certificate.bin. Public hosting and full-readback receipts are recorded separately in panel-local-archive-001.

Frozen source: {p['freeze']['commit']}. Frozen protocol: {p['freeze']['protocol_sha256']}. Its analysis-input paths and hash-pinned plan identify the RREF local01 attempt. The accompanying two-row export records producer/checker and exact-count stages on this one input.
"""
(r/'report.md').write_text(text+'\n![Certificate implication](flow.svg)\n')
(r/'flow.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="170"><rect width="800" height="170" fill="white"/><g font-family="sans-serif" font-size="20" text-anchor="middle"><rect x="10" y="20" width="350" height="70" rx="8" fill="#d1fae5"/><text x="185" y="50">Original D4 checker accepted</text><text x="185" y="78">codimension ≥ {q:,}</text><rect x="440" y="20" width="350" height="70" rx="8" fill="#dbeafe"/><text x="615" y="50">Fresh exact enumeration</text><text x="615" y="78">{count} solutions</text><text x="400" y="140">{q:,} &gt; {count}: LFD ≥ 5 for fresh-n45-poly-03</text></g></svg>')
(r/'report.typ').write_text('#set page(paper: "a4", margin: 20mm)\n#set text(size: 10pt)\n#text('+json.dumps(text.replace('# ',''))+')\n#image("flow.svg", width: 100%)\n')
typst.compile(str(r/'report.typ'),output=str(r/'report.pdf'))
def art(n,kind='raw'):
 f=r/n;return dict(path=n,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size,kind=kind)
d=json.loads((s/'reports/seed-reuse-001/export.json').read_text());template=copy.deepcopy(d['runs'][0]);d.update(export_id='SEMAEV-PANEL-LOCAL-N45-POLY03-001',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=dict(repo='crypto-autoresearcher',commit=p['freeze']['commit'],dirty=False));d['protocol']=dict(path='protocol.json',sha256=p['freeze']['protocol_sha256'],protocol_id=p['protocol_id'],version=1);d['arms']=[dict(id=a['id'],role=a['role'],binary_sha256=a['instrument']['binary_sha256'],commit=a['instrument']['commit']) for a in p['arms']];d['runs']=[]
for arm in ['producer','exact-count']:
 row=copy.deepcopy(template);row.update(run_id='n45-poly03-'+arm,arm=arm,instance_id='0',seed=0);row['measurements']['counted']={'certified_codimension_lower_bound':q} if arm=='producer' else {'exact_solutions':count};row['verification']['verifier']='Original independent D4 checker' if arm=='producer' else 'Fresh pinned exact counter';row['artifacts']=[art('result.json')];d['runs'].append(row)
d['flow']=dict(planned=2,attempted=2,completed=2,not_completed=0,interrupted=0,resumed=0,excluded=[]);d['files']=[art(n) for n in ['result.json','manifest.json','raw-evidence.tar.gz']];d['analysis']=dict(script=art('run_panel_worker_v2.py','analysis'),blinded=False,blinding_key_sha256=None,outputs=[art(n,'report') for n in ['report.md','report.typ','report.pdf','flow.svg']],unmasked_at=None);d['notes']=[dict(kind='observation',by='Codex',text=f'One original panel input, two actual stages. Independently accepted D4 codimension {q} exceeds fresh count {count}, establishing named-instance LFD>=5.')];(r/'export.json').write_text(json.dumps(d,indent=2)+'\n')
