"""Seal closed files and cross-check canonical identities with repository tool."""
import hashlib,importlib.util,json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
tool=ROOT.parents[3]/'tools'/'curve_identity.py'
spec=importlib.util.spec_from_file_location('canonical_identity',tool)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
checks=[]
for path in sorted((ROOT/'certificates').glob('*-domain.json')):
    value=json.loads(path.read_text());identity=value['identity']
    tag='p224' if value['parameters']['name']=='P-224' else 'curve448short'
    actual=module.curve_identity(identity['field'],identity['curve'],tag)
    assert all(actual[k]==identity[k] for k in ('curve_id','curve_uid'))
    checks.append(dict(certificate=str(path.relative_to(ROOT)),curve_id=actual['curve_id'],curve_uid=actual['curve_uid'],pass_=True))
(ROOT/'certificates'/'identity-check.json').write_text(json.dumps(dict(checks=checks,
    canonical_tool_sha256=hashlib.sha256(tool.read_bytes()).hexdigest(),arithmetic_imported=False),indent=2)+'\n')
files={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(ROOT.rglob('*'))
       if path.is_file() and path.name!='manifest-final.json'}
out=dict(schema='local-content-sha256/v1',supersedes='manifest.json',
         reason='Preliminary manifest hashed logs/finalize.stdout.log before that active stream closed. All original files retained.',
         scope='Files present at seal time; coordinator PDF and later snapshot receipts are outside this manifest.',files=files)
(ROOT/'manifest-final.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected for name,expected in files.items())
print(json.dumps(dict(status='PASS',canonical_curve_identities_checked=len(checks),sealed_files=len(files),
 largest_file_bytes=max(p.stat().st_size for p in ROOT.rglob('*') if p.is_file()))))
