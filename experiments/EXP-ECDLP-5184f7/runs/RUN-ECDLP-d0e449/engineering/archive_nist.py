"""Archive exact own run/source/receipt bytes, without caches or unrelated records."""
import argparse,datetime,hashlib,json,subprocess,zipfile
from pathlib import Path

repo=Path('/workspace/solinas-run')
run=repo/'experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449'
ext=repo/'experiments/EXP-ECDLP-5184f7/extensions/nist-fullsize-20261011'
ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--raw-commit',required=True);ap.add_argument('--archive',type=Path,required=True);a=ap.parse_args()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((run/'manifest.json').read_text());entries=[]
for base in [run,ext]:
    entries.extend(p for p in sorted(base.rglob('*'))if p.is_file()and '__pycache__'not in p.parts)
entries.append(a.receipt.resolve())
assert len(set(entries))==len(entries)and all(p.is_relative_to(repo)for p in entries)
hashes={str(p.relative_to(repo)):sha(p)for p in entries}
identity={'experiment_id':'EXP-ECDLP-5184f7','run_id':run.name,'source_commit':manifest['source_commit'],'raw_commit':a.raw_commit,
  'head_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'files':len(entries),
  'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exact_bytes_SHA256':hashes,
  'boundary':'Own P-192/P-224 run and committed extension plus own session receipt only; previous Solinas archives stay separate'}
archive=a.archive.resolve()
with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
    for p in entries:z.write(p,str(p.relative_to(repo)))
    z.writestr('ARCHIVE-IDENTITY.json',json.dumps(identity,indent=2)+'\n')
with zipfile.ZipFile(archive)as z:
    assert z.testzip()is None
    for name,want in hashes.items():assert hashlib.sha256(z.read(name)).hexdigest()==want
checksum=sha(archive);side=archive.with_name(archive.name+'.sha256')
with side.open('x')as f:f.write(checksum+'  '+archive.name+'\n')
metadata=archive.with_name(archive.name+'.archive.json')
with metadata.open('x')as f:json.dump({k:v for k,v in identity.items()if k!='exact_bytes_SHA256'}|{'archive':str(archive),'bytes':archive.stat().st_size,'sha256':checksum,'CRC_and_per_file_SHA256_verified':True},f,indent=2);f.write('\n')
print(json.dumps({'archive':str(archive),'MiB':archive.stat().st_size/(1<<20),'files':len(entries),'SHA256':checksum,'all_integrity_checks_pass':True},indent=2))
