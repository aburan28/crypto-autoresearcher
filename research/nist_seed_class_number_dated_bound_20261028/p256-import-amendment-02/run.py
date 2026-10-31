"""Frozen two-arm calculation, failure guards, complete identity-bound audit."""
import datetime,hashlib,json,os,pathlib,platform,resource,subprocess,sys,time
P=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for n,h in json.loads((P/'FROZEN-FILES.json').read_text()).items():assert sha(P/n)==h,n
    W=P/'runs'/'certificate-01';W.mkdir(parents=True,exist_ok=False)
    (W/'source.json').write_text(json.dumps({'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip(),'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=P,text=True)),'platform':platform.platform(),'python':sys.version},indent=2)+'\n')
    def call(name,cmd,expected_failure=False):
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:r=subprocess.run(cmd,cwd=P,capture_output=True,timeout=(30 if expected_failure else 180));code=r.returncode;out=r.stdout;err=r.stderr;timed=False
        except subprocess.TimeoutExpired as e:code=None;out=e.stdout or b'';err=e.stderr or b'';timed=True
        (W/(name+'.stdout')).write_bytes(out);(W/(name+'.stderr')).write_bytes(err)
        after=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt={'command':cmd,'returncode':code,'timeout':timed,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime,'stdout_sha256':sha(W/(name+'.stdout')),'stderr_sha256':sha(W/(name+'.stderr'))}
        (W/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        if expected_failure:assert code not in (0,None) and b'COMPLETE' not in out and not timed
        else:assert code==0 and not timed and not err and out.splitlines()[-1]==b'COMPLETE',name
        print(name,'returncode',code,'wall_diagnostic',round(receipt['wall_seconds_diagnostic'],3),flush=True)
        return out
    for fault in ['exception','early']:call('guard-'+fault,[sys.executable,'-B',str(P/'certificate.py'),'--fault-'+fault],True)
    a=call('python',[sys.executable,'-B',str(P/'certificate.py')]);b=call('gp',['/opt/homebrew/bin/gp','-q','-f','-s','67108864',str(P/'inputs.gp'),str(P/'verify.gp')])
    def parse(out):
        lines=out.decode().splitlines();assert lines[0]=='CONTROLS PASS' and lines[-1]=='COMPLETE';return [json.loads(x) for x in lines[1:-1]]
    a,b=parse(a),parse(b);assert len(a)==len(b)==21 and a==b
    rows=[]
    for i,(r,v) in enumerate(zip(json.loads((P/'INPUTS.json').read_text())['rows'],a)):
        assert v[0]==i and v[2]==24
        rows.append({'index':i,'name':r['name'],'curve_uid':r['curve_uid'],'label':r['label'],'stream':str(r['timestamp'])+':'+str(int(r['p']).bit_length()),'D_K':str(v[1]) if v[1] else None,'split_primes':v[3],'product':str(v[4]),'lower_bound':16777216 if v[5] else None,'status':'CERTIFIED' if v[5] else ('UNKNOWN_D_K' if not v[1] else 'NOT_CERTIFIED')})
    result={'status':'PASS','cohort_size':21,'two_implementations_equal':True,'controls':'PASS: two positive, noncertifying, nonfundamental, A/A, exception/early-return guards','rows':rows,'counts':{label:{s:sum(r['label']==label and r['status']==s for r in rows) for s in ['CERTIFIED','UNKNOWN_D_K','NOT_CERTIFIED']} for label in ['published','omitted']},'scope':'Maximal-order class-number lower-bound certificates. No exact class number, 1997 use or original seed visitation established.'}
    (W/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (W/'COMPLETE').write_text('Both implementations, all controls and full cohort identity audit passed.\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
