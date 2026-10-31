from pathlib import Path
import hashlib
import json
import shutil

import typst


study = Path('analysis/semaev-degree-five-quotient-lift')
validation = study / 'validation/n49-poly00-retained-check-001'
archive = study / 'n49-retained-archive-001'
report = study / 'reports/n49-retained-d4-001'
report.mkdir(parents=True, exist_ok=True)
result = json.loads((validation / 'result.json').read_text())
publication = json.loads((archive / 'fresh-n49-poly-00-D4-retained01.publication.json').read_text())
assert result['status'] == 'certificate_verified'
assert (result['certified_codimension_lower_bound'], result['exact_solutions'], result['last_fall_degree_lower_bound']) == (32291, 2, 5)
assert publication['certificate_sha256'] == result['certificate_sha256']
assert publication['checks'] == ['anonymous HTTPS GET and SHA256 for every asset',
                                  'gzip decompression and original certificate SHA256',
                                  'S3 GET and SHA256 for each store-backed asset']
checker = (validation / 'check4.stdout.txt').read_text()
assert 'variable 50/50 ok' in checker
assert 'VALID: 1 is not in W_4(F), and codim W_4(F) >= 32291' in checker
assert (validation / 'count.stdout.txt').read_text().strip() == '2'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for name in ['result.json', 'check4.stdout.txt', 'check4.stderr.txt', 'count.stdout.txt', 'count.stderr.txt']:
    shutil.copy2(validation / name, report / name)
shutil.copy2(study / 'verify_retained_n49_poly00.py', report / 'verify_retained_n49_poly00.py')
cert_url = next(item['anonymous_url'] for item in publication['files'] if item['name'].endswith('.D4.cert.gz'))
text = f'''# Certified n49 polynomial-basis input: LFD at least five

The original independent checker accepted the retained D4 certificate for `fresh-n49-poly-00`. It checked all 50 variable multiplications and established `1 ∉ W_4(F)` with codimension at least **32,291**. A fresh exhaustive count returned **2** solutions. The strict inequality certifies **last fall degree ≥ 5** for this named Boolean presentation.

The certificate was produced during the earlier frozen frontier cascade and retained when that run was interrupted. Its SHA-256 is `{result['certificate_sha256']}`. The later [independent recheck](../../validation/n49-poly00-retained-check-001/result.json) first matched the certificate, input-system, original-plan, and recovery-plan hashes, then ran the original checker and pinned exact counter. The checker took {result['steps']['check4']['elapsed_seconds']:.3f} seconds and the counter took {result['steps']['count']['elapsed_seconds']:.3f} seconds. These are execution records for this input.

The [public readback receipt](../../n49-retained-archive-001/fresh-n49-poly-00-D4-retained01.publication.json) verifies anonymous download, gzip decompression to the retained certificate hash, and canonical object-store readback. [Download the certificate]({cert_url}). The degree-five stage for this input has not been certified, so its LFD-six status remains unknown.

The original source plan SHA-256 is `{result['original_plan_sha256']}` and the frozen recovery protocol SHA-256 is `{result['protocol_sha256']}`. The [verification script](verify_retained_n49_poly00.py) records the exact checker and counter commands and their return codes.

![Checked inequality for the n49 input](flow.svg)
'''
(report / 'report.md').write_text(text)
(report / 'flow.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="205" viewBox="0 0 900 205" role="img" aria-label="n49 D4 certificate: checked codimension 32291 exceeds exact count 2">
<rect width="900" height="205" fill="white"/>
<g font-family="sans-serif"><text x="25" y="38" font-size="20" fill="#17222f">n49 polynomial-basis input: independent D4 check</text>
<text x="25" y="67" font-size="14" fill="#526273">50 of 50 variable checks passed; one frozen input</text>
<rect x="25" y="88" width="785" height="44" fill="#276b9a"/><text x="38" y="116" font-size="16" fill="white">Checked codimension lower bound = 32,291</text>
<text x="25" y="164" font-size="16" fill="#17222f">Fresh exact solutions = 2</text>
<text x="25" y="195" font-size="15" fill="#276b9a">32,291 &gt; 2 ⇒ named-instance LFD ≥ 5</text></g></svg>''')
typ = f'''#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
= Certified n49 polynomial-basis input: LFD at least five
The original independent checker accepted all 50 variable multiplication checks for fresh-n49-poly-00. It certified *1 not in W4* and codimension at least *32,291*. A fresh exhaustive count found *2* solutions. Thus the strict inequality establishes *LFD at least 5* for this named Boolean presentation.

#image("flow.svg", width: 100%)

The D4 candidate came from the interrupted frozen frontier run. Its SHA-256 is {result['certificate_sha256']}. The later recheck matched the certificate, input system, and frozen plan hashes, then ran the original checker and pinned counter. Checker and counter elapsed times were {result['steps']['check4']['elapsed_seconds']:.3f} and {result['steps']['count']['elapsed_seconds']:.3f} seconds. Public and canonical-store readback of the certificate and evidence passed.

The D5 stage is unknown. Original plan SHA-256: {result['original_plan_sha256']}. Recovery protocol SHA-256: {result['protocol_sha256']}.
'''
(report / 'report.typ').write_text(typ)
typst.compile(str(report / 'report.typ'), output=str(report / 'report.pdf'))
manifest = {'schema': 'semaev.retained-check-report/v1', 'result_sha256': digest(validation / 'result.json'),
            'publication_sha256': digest(archive / 'fresh-n49-poly-00-D4-retained01.publication.json'),
            'files': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size}
                      for p in report.iterdir() if p.is_file() and p.name != 'manifest.json'}}
(report / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
