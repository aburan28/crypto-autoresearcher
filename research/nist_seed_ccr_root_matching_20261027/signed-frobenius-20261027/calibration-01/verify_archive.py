"""Verify sealed bytes, rebuild native code and replay both exact modes after relocation."""
import hashlib,json,pathlib,subprocess,sys,tarfile,time
P=pathlib.Path(__file__).resolve().parent
b=json.loads((P/'BUNDLE.json').read_text());a=P/b['archive']
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
assert digest(a)==b['sha256']
R=pathlib.Path(sys.argv[1]);R.mkdir();t=R/'evidence.tar'
with t.open('wb') as f:subprocess.run(['/opt/homebrew/bin/zstd','-dc',str(a)],stdout=f,check=True)
with tarfile.open(t) as f:f.extractall(R,filter='data')
E=R/'evidence';m=E/'MANIFEST.json';assert digest(m)==b['manifest_sha256'];manifest=json.loads(m.read_text())
assert all(digest(E/n)==h for n,h in manifest.items())
assert {str(f.relative_to(E)) for f in E.rglob('*') if f.is_file()}==set(manifest)|{'MANIFEST.json'}
assert all(digest(E/n)==h for n,h in json.loads((E/'FROZEN-FILES.json').read_text()).items())
W=R/'replay';W.mkdir()
for f in (E/'inputs').iterdir():(W/f.name).write_bytes(f.read_bytes())
binary=R/'calibrate';build=subprocess.run(['/usr/bin/clang++','-O3','-std=c++17','-Wall','-Wextra','-pedantic',str(E/'calibrate.cc'),'-o',str(binary)],capture_output=True,text=True)
assert build.returncode==0,build.stderr
receipts=[]
for arm,timeout in [('enumerate',600),('verify',1800)]:
    start=time.monotonic();r=subprocess.run([str(binary),arm,str(W)],capture_output=True,text=True,timeout=timeout)
    receipts.append({'arm':arm,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'wall_seconds_diagnostic':time.monotonic()-start})
    assert r.returncode==0,r.stderr
for n in ['coverage.csv','cap-models.csv','level-coverage.csv','absence-checks.csv','enumerator-summary.txt','verifier-summary.txt']:
    assert (W/n).read_bytes()==(E/'raw'/n).read_bytes(),n
out={'status':'PASS','archive_sha256':b['sha256'],'sealed_files_verified':len(manifest)+1,'both_modes_replayed':True,'all_six_result_files_byte_identical':True,'new_independent_cohort':False,'source_sha256':digest(E/'calibrate.cc'),'rebuilt_binary_sha256':digest(binary),'build_stdout':build.stdout,'build_stderr':build.stderr,'receipts':receipts}
(P/'PORTABLE-REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='receipts'}))
