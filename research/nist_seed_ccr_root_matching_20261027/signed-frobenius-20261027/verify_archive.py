"""Relocation replay: both math arms and bitset pairs; original rowwise proof is hash-bound."""
import hashlib,json,pathlib,subprocess,sys,tarfile,tempfile,time
P=pathlib.Path(__file__).resolve().parent
b=json.loads((P/'BUNDLE.json').read_text());a=P/b['archive'];assert hashlib.sha256(a.read_bytes()).hexdigest()==b['sha256'];root=pathlib.Path(sys.argv[1]);root.mkdir();tar=root/'evidence.tar'
with tar.open('wb') as f:subprocess.run(['/opt/homebrew/bin/zstd','-dc',str(a)],stdout=f,check=True)
with tarfile.open(tar) as f:f.extractall(root,filter='data')
E=root/'evidence';manifest=json.loads((E/'MANIFEST.json').read_text());assert hashlib.sha256((E/'MANIFEST.json').read_bytes()).hexdigest()==b['manifest_sha256'];assert all(hashlib.sha256((E/n).read_bytes()).hexdigest()==h for n,h in manifest.items())
for n,h in json.loads((E/'FROZEN-FILES.json').read_text()).items():assert hashlib.sha256((E/n).read_bytes()).hexdigest()==h
expected={n:(E/n).read_bytes() for n in ['matrix.json','eigen.json','rowwise-search.json','rowwise-witnesses.u16le','policy-check-01/RESULT.json']};receipts=[]
for name in ['arithmetic.py','independent.py']:
 s=time.monotonic();r=subprocess.run([sys.executable,'-B',str(E/name)],cwd=E,capture_output=True,text=True,timeout=600);receipts.append({'script':name,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'elapsed_seconds_diagnostic':time.monotonic()-s});assert r.returncode==0,r.stderr
for n in ['matrix.json','eigen.json']:assert (E/n).read_bytes()==expected[n]
sys.path.insert(0,str(E));import audit
cells=json.loads((E/'matrix.json').read_text())['cells'];rows=json.loads((E/'prior-rows.json').read_text());cols,types=audit.columns(cells,rows);atoms,_=audit.atomize(cols,types,[]);old=json.loads((E/'prior-bitset-atoms.json').read_text());result=audit.search(old+atoms,old,'bitset');assert result==json.loads(expected['rowwise-search.json']);assert (E/'bitset-witnesses.u16le').read_bytes()==expected['rowwise-witnesses.u16le']
r=subprocess.run([sys.executable,'-B',str(E/'policy-check-01/policy.py')],cwd=E,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr;assert (E/'policy-check-01/RESULT.json').read_bytes()==expected['policy-check-01/RESULT.json']
out={'status':'PASS','archive_sha256':b['sha256'],'payload_files_verified':len(manifest),'both_1281_cell_arithmetic_arms_recomputed':True,'all_bitset_pairs_recomputed':result['pairs'],'recomputed_fits_and_witnesses_equal_original_rowwise':True,'policy_result_recomputed':True,'rowwise_pair_enumeration_repeated':False,'note':'Original complete rowwise enumeration is hash-bound and matched by the relocated bitset replay; it is not rerun here. Replays are same-data validation, not new independent cohorts.','producer_receipts':receipts};(P/'PORTABLE-REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='producer_receipts'}))
