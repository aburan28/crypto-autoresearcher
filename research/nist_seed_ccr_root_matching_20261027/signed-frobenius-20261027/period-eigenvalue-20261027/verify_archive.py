"""Extract/hash-check and replay both route methods in a separate fresh directory."""
import hashlib,json,pathlib,shutil,subprocess,sys,tarfile
P=pathlib.Path(__file__).resolve().parent;b=json.loads((P/'BUNDLE.json').read_text());a=P/b['archive']
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert h(a)==b['sha256'];R=pathlib.Path(sys.argv[1]);R.mkdir();t=R/'evidence.tar'
with t.open('wb') as f:subprocess.run(['/opt/homebrew/bin/zstd','-dc',str(a)],stdout=f,check=True)
with tarfile.open(t) as f:f.extractall(R,filter='data')
E=R/'evidence';m=json.loads((E/'MANIFEST.json').read_text());assert h(E/'MANIFEST.json')==b['manifest_sha256'];assert all(h(E/n)==v for n,v in m.items());assert {str(f.relative_to(E)) for f in E.rglob('*') if f.is_file()}==set(m)|{'MANIFEST.json'}
W=R/'replay';W.mkdir();(W/'.work').mkdir()
for n in ['FROZEN-FILES.json','run.py']+list(json.loads((E/'FROZEN-FILES.json').read_text())):
    if not (W/n).exists():shutil.copyfile(E/n,W/n)
r=subprocess.run([sys.executable,'-B',str(W/'run.py')],capture_output=True,text=True,timeout=360);assert r.returncode==0,r.stderr
for n in ['RESULT.json','cohort.csv']:assert (E/n).read_bytes()==(W/n).read_bytes(),n
for arm in ['discriminant','norm']:assert (E/'raw'/(arm+'.stdout')).read_bytes()==(W/'.work'/(arm+'.stdout')).read_bytes()
x={'status':'PASS','archive_sha256':b['sha256'],'sealed_files_verified':len(m)+1,'both_arms_replayed':True,'results_csv_and_both_raw_vectors_byte_identical':True,'new_cohort':False,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};(P/'PORTABLE-REPLAY.json').write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='stdout'}))
