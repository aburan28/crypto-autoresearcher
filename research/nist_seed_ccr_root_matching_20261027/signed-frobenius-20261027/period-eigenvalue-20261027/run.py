"""Frozen source-route arms and exact audit. No original point-counter execution."""
import csv,datetime,hashlib,json,pathlib,platform,resource,subprocess,sys,time
P=pathlib.Path(__file__).resolve().parent;W=P/'.work'
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def main():
    for n,h in json.loads((P/'FROZEN-FILES.json').read_text()).items():assert digest(P/n)==h,n
    commands=[('discriminant',[sys.executable,'-B',str(P/'discriminant.py')]),('norm',['/opt/homebrew/bin/gp','-q','-f',str(P/'inputs.gp'),str(P/'norm.gp')])]
    for arm,cmd in commands:
        start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();before=resource.getrusage(resource.RUSAGE_CHILDREN)
        try:r=subprocess.run(cmd,cwd=P,capture_output=True,timeout=180);rc=r.returncode;stdout=r.stdout;stderr=r.stderr;timeout=False
        except subprocess.TimeoutExpired as e:rc=None;stdout=e.stdout or b'';stderr=e.stderr or b'';timeout=True
        after=resource.getrusage(resource.RUSAGE_CHILDREN);(W/(arm+'.stdout')).write_bytes(stdout);(W/(arm+'.stderr')).write_bytes(stderr)
        receipt={'command':cmd,'returncode':rc,'timeout':timeout,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime,'host':platform.platform(),'stdout_sha256':digest(W/(arm+'.stdout')),'stderr_sha256':digest(W/(arm+'.stderr'))};(W/(arm+'-receipt.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(arm,'returncode',rc,'stderr_bytes',len(stderr),flush=True)
        if rc!=0 or timeout or stderr:raise SystemExit('arm failure retained')
    a=[json.loads(l) for l in (W/'discriminant.stdout').read_text().splitlines()];b=[json.loads(l) for l in (W/'norm.stdout').read_text().splitlines()];assert len(a)==len(b)==21 and a==b
    source=json.loads((P/'INPUTS.json').read_text());out=[]
    for v,r in zip(a,source['rows']):
        i,p,n,t,k,ss,c3,c4,s1,m1,s2,m2=v;assert i==len(out) and (p,n)==(int(r['p']),int(r['n']))
        out.append({'index':i,'name':r['name'],'curve_uid':r['curve_uid'],'label':r['label'],'p':str(p),'A':'-3','b':r['b'],'n':str(n),'trace':str(t),'negative_discriminant':str(k),'supersingular':ss,'isogenous_j0_ordinary':c3,'isogenous_j1728_ordinary':c4,'literal_first_phase_stop_m0_1':s1,'literal_first_phase_stop_m0_2':s2,'source_special_route':bool(ss or c3 or c4)})
    with (P/'cohort.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
    result={'status':'PASS','cohort_size':len(a),'both_algorithms_equal':True,'controls':'PASS: generic nonexceptional-j curves isogenous to j0/j1728, supersingular, ordinary negative, singular/wrong-order guards, A/A','special_route_counts':{label:sum(r['source_special_route'] for r in out if r['label']==label) for label in ['published','omitted']},'max_literal_first_phase_stop':max(max(v[8],v[10]) for v in a),'rows':out,'scope':'Source-defined special-route arithmetic and literal first-phase primorial threshold only. Practical continuation threshold unspecified in thesis. No original caller, native SEA replay, new cohort point count or historical criterion identified.'};(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
