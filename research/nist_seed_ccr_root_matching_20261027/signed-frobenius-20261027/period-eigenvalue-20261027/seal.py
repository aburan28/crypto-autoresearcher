"""Seal declared source-route evidence, excluding all third-party source bytes."""
import hashlib,json,pathlib,shutil,subprocess,tarfile
P=pathlib.Path(__file__).resolve().parent;E=P/'.work/evidence';E.mkdir()
names=['PLAN.md','INPUTS.json','CONTROLS.json','inputs.gp','discriminant.py','norm.gp','run.py','FROZEN-FILES.json','experiment.protocol.json','LMFDB-CONTROLS.json','BROWSER-RETRIEVAL.json','RETRIEVAL.json','RESULT.json','cohort.csv','export.json','export-check.txt']
names+=['raw/'+f.name for f in sorted((P/'raw').iterdir())]
for n in names:
    (E/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(P/n,E/n)
m={n:hashlib.sha256((E/n).read_bytes()).hexdigest() for n in sorted(names)}
(E/'MANIFEST.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
tar=P/'.work/evidence.tar'
with tarfile.open(tar,'w',format=tarfile.PAX_FORMAT) as t:
    for f in sorted(E.rglob('*')):
        if f.is_file():
            info=t.gettarinfo(str(f),'evidence/'+str(f.relative_to(E)));info.uid=info.gid=info.mtime=0;info.uname=info.gname=''
            with f.open('rb') as stream:t.addfile(info,stream)
a=P/'evidence.tar.zst';subprocess.run(['/opt/homebrew/bin/zstd','-19','-T1',str(tar),'-o',str(a)],check=True)
b={'archive':a.name,'bytes':a.stat().st_size,'sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((E/'MANIFEST.json').read_bytes()).hexdigest(),'payload_files':len(m),'sealed_files':len(m)+1,'excluded':'Third-party PDFs, extracted text, source page images and runtime binaries. Source URLs/hashes retained.'};(P/'BUNDLE.json').write_text(json.dumps(b,indent=2,sort_keys=True)+'\n');print(json.dumps(b))
