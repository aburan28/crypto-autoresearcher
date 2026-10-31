"""Read-only binding of reused later-counter observations to their exact native logs."""
import hashlib,json,pathlib,re,sys
P=pathlib.Path(__file__).resolve().parent;obs=json.loads(pathlib.Path(sys.argv[1]).read_text());W=pathlib.Path('/Volumes/data/workspaces/nist-seed-criteria-20261022/workflow');models={r['name']:r for r in json.loads((P/'prior-rows.json').read_text())};out=[]
for r in obs['results']:
 if r['profile']!='y_direct':continue
 assert r['status']=='verified_order'
 f=W/r.get('log_directory','runs')/(r['name']+'__'+r['profile']+'.log');raw=f.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['stdout_sha256'],f;s=raw.decode();primes=list(map(int,re.findall(r'Working on prime l\s*=\s*(\d+)',s)));assert max(primes)==r['max_auxiliary_prime'];order=int(re.search(r'NIST_WORKFLOW_ORDER\s+(\d+)',s).group(1));m=models[r['name']];assert order==int(r['order'])==int(r['expected_order'])==int(m['n']);assert list(map(int,r['input'].split()))==[int(m['p']),int(m['p'])-3,int(m['b'])]
 out.append({'name':r['name'],'curve_uid':m['curve_uid'],'label':m['label'],'path':str(f),'stdout_sha256':r['stdout_sha256'],'working_prime_count':len(primes),'max_reported_working_prime':max(primes),'reported_working_on_199':199 in primes,'order_model_bound':True})
assert len(out)==21
record={'status':'PASS','native_log_hashes_verified':21,'exact_curve_models_and_orders_bound':True,'rows':out,'interpretation':'Working-prime markers from the measured later LiDIA replay; not original1997 execution. All log bytes checked; absence concerns these reported markers.'};(P/'COUNTER-TRACE-BINDING.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');print('21 exact-model/order log hashes and prime markers verified')
