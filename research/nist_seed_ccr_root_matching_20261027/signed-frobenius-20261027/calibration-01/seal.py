"""Seal only declared calibration records; no third-party paper bytes or binaries."""
import hashlib,json,pathlib,shutil,subprocess,tarfile
P=pathlib.Path(__file__).resolve().parent
E=P/'.work/evidence'
E.mkdir()
names=['BUILD.json','INPUTS.json','FROZEN-FILES.json','PLAN.md','calibrate.cc','prepare.py','run.py','experiment.protocol.json','RESULT.json','export.json','export-check.txt']
names+=['inputs/'+f.name for f in sorted((P/'inputs').iterdir())]
names+=['raw/'+f.name for f in sorted((P/'raw').iterdir())]
for n in names:
    (E/n).parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(P/n,E/n)
manifest={n:hashlib.sha256((E/n).read_bytes()).hexdigest() for n in sorted(names)}
(E/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
tar=P/'.work/evidence.tar'
with tarfile.open(tar,'w',format=tarfile.PAX_FORMAT) as t:
    for f in sorted(E.rglob('*')):
        if f.is_file():
            info=t.gettarinfo(str(f),'evidence/'+str(f.relative_to(E)))
            info.uid=info.gid=info.mtime=0;info.uname=info.gname=''
            with f.open('rb') as stream:t.addfile(info,stream)
archive=P/'evidence.tar.zst'
subprocess.run(['/opt/homebrew/bin/zstd','-19','-T1',str(tar),'-o',str(archive)],check=True)
bundle={'archive':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((E/'MANIFEST.json').read_bytes()).hexdigest(),'payload_files':len(manifest),'sealed_files':len(manifest)+1,'scope':'Exact calibration source, frozen inputs and original two-mode records. Third-party PDFs/text/images, compiler binary and source-search scratch are excluded.'}
(P/'BUNDLE.json').write_text(json.dumps(bundle,indent=2,sort_keys=True)+'\n')
print(json.dumps(bundle))
