import copy,datetime,hashlib,json,shutil,tarfile
from pathlib import Path
import typst
r=Path(__file__).resolve().parent;s=r.parent.parent;v=s/'validation/rref-export-001'
manifest=json.loads((v/'raw-manifest.json').read_text());result=json.loads((v/'result.json').read_text());rows=result['rows'];assert len(rows)==14 and all(x['passed'] for x in rows)
with tarfile.open(v/'raw-evidence.tar.gz') as t:
 for f in manifest['files']:
  b=t.extractfile(f['path']).read();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
for i in range(7):
 pair=[x for x in rows if x['instance_id']==str(i)];assert len(pair)==2
 if i==3:assert all(x['contains_one'] for x in pair)
 else:assert pair[0]['certificate_sha256']==pair[1]['certificate_sha256'] and all(x['independent_check'] for x in pair)
for name in ['result.json','raw-manifest.json','raw-evidence.tar.gz','collection-environment.json']:shutil.copyfile(v/name,r/name)
for src,dst in [('rref-export-protocol-001.json','protocol.json'),('qualify_rref_export.py','qualify_rref_export.py'),('lfdclose2_rref_export.c','lfdclose2_rref_export.c')]:shutil.copyfile(s/src,r/dst)
p=json.loads((r/'protocol.json').read_text())
text=f'''# RREF certificate exporter: fourteen exact controls passed

All fourteen configurations passed: seven fixed systems, each run with the reference reverse-substitution exporter and the separate full-RREF exporter. All twelve completed certificates are byte-identical across the two exporters and satisfy independent quotient-map conditions. The three Semaev fixtures additionally pass the original standalone checker and match the retained reference hashes. Both configurations of the constant-one fixture correctly produce no certificate.

Coverage includes rank zero (codimension 42), a three-word quotient with a partial final word (130), generic quadratic relations (331), constant-one rejection, and three Semaev fixtures with codimensions 3, 1, and 1. Closure construction, column order and stopping rules are unchanged; only the export routine differs. The frozen plan pins every input, binary, checker and test script.

The archive contains {len(manifest['files'])} files with verified sizes and hashes. Each child had a 1 GiB address-space cap and 180-second watchdog. All fourteen returned zero, with no missing or failed cases. Wall times and resource usage were not recorded as performance measurements. Host metadata was collected after the controls; it is not per-stage instrumentation.

Source commit: {p['freeze']['commit']}. Protocol SHA-256: {p['freeze']['protocol_sha256']}. Candidate binary: f4a9b51354d7f6bb4ba7f8afecfacc459f78b96647411f29b0229062cbc7e844. The construction rationale and source references are in RREF-EXPORT.md.

Next: package the candidate with the unchanged worker's per-run controls and independent checker, retaining resource admission and a separately frozen scientific request. The active scientific binaries were not replaced. These controls establish exact agreement on the listed fixtures; a measured runtime comparison has not been performed.
'''
(r/'report.md').write_text(text+'\n![Recorded controls](outcomes.svg)\n')
svg='<svg xmlns="http://www.w3.org/2000/svg" width="760" height="300"><rect width="760" height="300" fill="white"/><g font-family="sans-serif" font-size="18"><text x="20" y="30">Fixture</text><text x="350" y="30">Reference</text><text x="520" y="30">RREF candidate</text>'
for i,label in enumerate(['Rank zero: q=42','Multiword: q=130','Quadratics: q=331','Constant one','Semaev 0: q=3','Semaev 1: q=1','Semaev 2: q=1']):
 y=65+30*i;status='No certificate' if i==3 else 'Verified';svg+=f'<text x="20" y="{y}">{label}</text><text x="350" y="{y}">{status}</text><text x="520" y="{y}">{status}</text>'
svg+='</g></svg>';(r/'outcomes.svg').write_text(svg)
(r/'report.typ').write_text('#set page(paper: "a4", margin: 20mm)\n#set text(size: 9pt)\n#text('+json.dumps(text.replace('# ',''))+')\n#image("outcomes.svg", width: 95%)\n');typst.compile(str(r/'report.typ'),output=str(r/'report.pdf'))
def art(name,kind='raw'):
 f=r/name;return {'path':name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'kind':kind}
d=json.loads((s/'reports/blocked-checkpoint-001/export.json').read_text());template=copy.deepcopy(d['runs'][0]);d.update(export_id='SEMAEV-RREF-EXPORT-001',created=datetime.datetime.now(datetime.timezone.utc).isoformat(),source={'repo':'crypto-autoresearcher','commit':p['freeze']['commit'],'dirty':False});d['protocol']={'path':'protocol.json','sha256':p['freeze']['protocol_sha256'],'protocol_id':p['protocol_id'],'version':p['version']};d['arms']=[{'id':a['id'],'role':a['role'],'binary_sha256':a['instrument']['binary_sha256'],'commit':a['instrument']['commit']} for a in p['arms']];d['runs']=[]
for row in rows:
 t=copy.deepcopy(template);t.update(run_id=row['arm']+'-'+row['instance_id'],arm=row['arm'],instance_id=row['instance_id']);t['verification']['verifier']='Exact constant-one rejection' if row.get('contains_one') else 'Reference byte identity and independent quotient conditions; original checker for Semaev fixtures';t['artifacts']=[art('result.json')];d['runs'].append(t)
d['flow']={'planned':14,'attempted':14,'completed':14,'not_completed':0,'interrupted':0,'resumed':0,'excluded':[]};d['files']=[art(n) for n in ['result.json','raw-manifest.json','raw-evidence.tar.gz','collection-environment.json']];d['analysis']={'script':art('qualify_rref_export.py','analysis'),'blinded':False,'blinding_key_sha256':None,'outputs':[art(n,'report') for n in ['report.md','report.typ','report.pdf','outcomes.svg']]+[art('collect.py','analysis')],'unmasked_at':None};d['notes']=[{'kind':'observation','by':'Codex','text':'Fourteen fixed exporter controls passed; twelve certificates match reference bytes and independent conditions. Host metadata was collected after controls; no performance measurements recorded.'}];(r/'export.json').write_text(json.dumps(d,indent=2)+'\n')
