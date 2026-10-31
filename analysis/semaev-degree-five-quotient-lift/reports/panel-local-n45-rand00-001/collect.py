from pathlib import Path
import copy
import datetime
import hashlib
import json
import shutil
import tarfile

import typst

study = Path('analysis/semaev-degree-five-quotient-lift')
validation = study / 'validation/panel-local-n45-rand00-final-001'
report = study / 'reports/panel-local-n45-rand00-001'
report.mkdir(parents=True, exist_ok=True)
result = json.loads((validation / 'result.json').read_text())
manifest = json.loads((validation / 'manifest.json').read_text())
protocol_path = study / 'panel-local-n45-rand00-protocol-001.json'
protocol = json.loads(protocol_path.read_text())
plan_path = study / 'panel-local-n45-rand00-plan-001.json'
request = json.loads((study / 'runtime/panel-local-n45-rand00-001/request.json').read_text())
admission = json.loads(Path('/home/ec2-user/fall-degree-data-20261029/panel-local-n45-rand00-001/admission.json').read_text())
publication = json.loads((study / 'panel-local-archive-001/fresh-n45-rand-00-rref-local01.publication.json').read_text())
inventory = json.loads((study / 'runtime/panel-remaining-after-local008.json').read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert result['id'] == 'fresh-n45-rand-00-rref-local01'
assert result['status'] == 'certificate_verified'
assert result['last_fall_degree_lower_bound'] == 5
assert result['certified_codimension_lower_bound'] == 46472
assert result['exact_solutions'] == 2
assert result['certificate_sha256'] == publication['certificate_sha256']
assert manifest['verified_artifact_count'] == 47
assert sha(plan_path) == protocol['links']['plan_sha256']
assert inventory['terminal_count'] == 28 and inventory['certified_lfd_at_least5'] == 21
assert inventory['terminal_inputs']['fresh-n45-rand-00']['result_sha256'] == sha(validation / 'result.json')
assert admission['admitted'] and admission['available_bytes'] >= admission['process_cap_bytes'] + admission['reserve_bytes']
with tarfile.open(validation / 'raw-evidence.tar.gz') as archive:
    for item in manifest['files']:
        if item['in_raw_archive']:
            data = archive.extractfile(item['path']).read()
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']

for source, name in [
    (validation / 'result.json', 'result.json'),
    (validation / 'manifest.json', 'manifest.json'),
    (validation / 'raw-evidence.tar.gz', 'raw-evidence.tar.gz'),
    (protocol_path, 'protocol.json'),
    (study / 'run_panel_worker_v2.py', 'run_panel_worker_v2.py'),
]:
    shutil.copy2(source, report / name)

cert_url = next(item['anonymous_url'] for item in publication['files'] if item['name'].endswith('.D4.cert.gz'))
text = f'''# Certified n45 random00: LFD at least five

The original independent checker accepted the D4 certificate for the unchanged `fresh-n45-rand-00` Boolean presentation. All 46 variable multiplication checks passed. It proved `1 ∉ W_4(F)` with codimension at least **46,472**. Fresh exhaustive enumeration found **2** solutions, so the strict inequality certifies **last fall degree ≥ 5** for this named instance.

The certificate is **1,045,099,360 bytes**, SHA-256 `{result['certificate_sha256']}`. The [terminal collector](../../validation/panel-local-n45-rand00-final-001/manifest.json) checked all 47 worker artifacts, the frozen request and protocol, and successful return. Three per-worker controls passed. The certificate and evidence have [public readback receipts](../../panel-local-archive-001/fresh-n45-rand-00-rref-local01.publication.json); [download the certificate]({cert_url}).

Admission passed on sample {admission['sample']} after {admission['wait_seconds']:.3f} seconds with {admission['available_bytes']:,} bytes available against a 40 GiB child cap plus 2 GiB reserve. Producer and checker took {result['steps']['produce']['elapsed_seconds']:.3f} and {result['steps']['check']['elapsed_seconds']:.3f} seconds on a shared host. These are execution records for this input.

The original 32-input D4 panel now has **28 terminal inputs**, **21 certified lower bounds of at least 5**, and **four remaining original n45 random-subspace inputs**. No new input was drawn. The separate n47 random02 D5 search is running from a verified checkpoint; it has no degree-five certificate yet.

The frozen input uses n={request['record']['n']}, k={request['record']['k']}, seed {request['record']['seed']}, and degree {request['degree']}. The command was `python3 analysis/semaev-degree-five-quotient-lift/launch_local_panel.py --plan analysis/semaev-degree-five-quotient-lift/panel-local-n45-rand00-plan-001.json --protocol analysis/semaev-degree-five-quotient-lift/panel-local-n45-rand00-protocol-001.json`; the plan pins the runtime Python and worker paths. CPU time was not recorded.

Frozen source commit: `{protocol['freeze']['commit']}`. Frozen protocol SHA-256: `{protocol['freeze']['protocol_sha256']}`.
'''
(report / 'report.md').write_text(text + '\n![Checked codimension and exact solution count](flow.svg)\n')
(report / 'flow.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="210" viewBox="0 0 900 210" role="img" aria-label="Checked D4 codimension 46472 exceeds exact solution count 2">
<rect width="900" height="210" fill="white"/>
<text x="25" y="36" font-family="sans-serif" font-size="20" fill="#17222f">fresh-n45-rand-00: independent D4 check</text>
<text x="25" y="65" font-family="sans-serif" font-size="14" fill="#526273">46 of 46 variable checks passed; one fixed input</text>
<rect x="25" y="88" width="790" height="45" fill="#276b9a"/>
<text x="38" y="117" font-family="sans-serif" font-size="16" fill="white">Checked codimension lower bound = 46,472</text>
<text x="25" y="163" font-family="sans-serif" font-size="16" fill="#17222f">Fresh exact solutions = 2</text>
<text x="25" y="195" font-family="sans-serif" font-size="15" fill="#276b9a">46,472 &gt; 2 ⇒ named-instance LFD ≥ 5</text>
</svg>''')
typ = f'''#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
= Certified n45 random00: LFD at least five
The independent D4 checker accepted all 46 variable multiplication checks for fresh-n45-rand-00. It certified codimension at least *46,472* and fresh exhaustive enumeration found *2* solutions. Thus the strict inequality establishes *LFD at least 5* for this named Boolean presentation.

The certificate is 1,045,099,360 bytes with SHA-256 {result['certificate_sha256']}. The collector checked all 47 worker artifacts and successful terminal return; three controls passed. Public certificate and evidence readback were verified.

#image("flow.svg", width: 100%)

Admission passed after {admission['wait_seconds']:.3f} seconds at {admission['available_bytes']:,} bytes available. Producer and checker took {result['steps']['produce']['elapsed_seconds']:.3f} and {result['steps']['check']['elapsed_seconds']:.3f} seconds. The original panel now has 28 terminal, 21 certified LFD-at-least-five, and four remaining inputs. Frozen source {protocol['freeze']['commit']}; protocol {protocol['freeze']['protocol_sha256']}.

Input n={request['record']['n']}, k={request['record']['k']}, seed {request['record']['seed']}, degree {request['degree']}. Runtime command and paths are in report.md and the frozen plan. CPU time was not recorded.
'''
(report / 'report.typ').write_text(typ)
typst.compile(str(report / 'report.typ'), output=str(report / 'report.pdf'))

def artifact(name, kind='raw'):
    path = report / name
    return {'path': name, 'sha256': sha(path), 'bytes': path.stat().st_size, 'kind': kind}

template_export = json.loads((study / 'reports/seed-reuse-001/export.json').read_text())
template_run = copy.deepcopy(template_export['runs'][0])
export = template_export
export.update(export_id='SEMAEV-PANEL-LOCAL-N45-RAND00-001',
              created=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              source={'repo': 'crypto-autoresearcher', 'commit': protocol['freeze']['commit'], 'dirty': False})
export['protocol'] = {'path': 'protocol.json', 'sha256': protocol['freeze']['protocol_sha256'],
                      'protocol_id': protocol['protocol_id'], 'version': 1}
export['arms'] = [{'id': arm['id'], 'role': arm['role'],
                   'binary_sha256': arm['instrument']['binary_sha256'],
                   'commit': arm['instrument']['commit']} for arm in protocol['arms']]
export['runs'] = []
for arm, measurement, verifier in [
    ('producer', {'certified_codimension_lower_bound': 46472}, 'Original independent D4 checker'),
    ('exact-count', {'exact_solutions': 2}, 'Fresh pinned exact counter'),
]:
    row = copy.deepcopy(template_run)
    row.update(run_id='n45-rand00-' + arm, arm=arm, instance_id='0', seed=0)
    row['measurements']['counted'] = measurement
    row['verification']['verifier'] = verifier
    row['artifacts'] = [artifact('result.json')]
    export['runs'].append(row)
export['flow'] = {'planned': 2, 'attempted': 2, 'completed': 2, 'not_completed': 0,
                  'interrupted': 0, 'resumed': 0, 'excluded': []}
export['files'] = [artifact(name) for name in ['result.json', 'manifest.json', 'raw-evidence.tar.gz']]
export['analysis'] = {'script': artifact('run_panel_worker_v2.py', 'analysis'), 'blinded': False,
                      'blinding_key_sha256': None,
                      'outputs': [artifact(name, 'report') for name in ['report.md', 'report.typ', 'report.pdf', 'flow.svg']],
                      'unmasked_at': None}
export['notes'] = [{'kind': 'observation', 'by': 'Codex',
                    'text': 'One original panel input. Independently accepted D4 codimension 46472 exceeds fresh count 2, certifying named-instance LFD>=5.'}]
(report / 'export.json').write_text(json.dumps(export, indent=2) + '\n')
