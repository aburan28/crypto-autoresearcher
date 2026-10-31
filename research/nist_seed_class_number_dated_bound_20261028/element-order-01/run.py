"""Frozen first-class witness test; preserve every per-curve form transcript."""
import datetime,hashlib,json,pathlib,platform,resource,subprocess,sys,time
P=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    for n,h in json.loads((P/'FROZEN-FILES.json').read_text()).items():assert sha(P/n)==h,n
    W=P/'runs/element-01';W.mkdir(parents=True,exist_ok=False)
    for arm in ['python','gp']:(W/arm).mkdir()
    source={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip(),'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=P,text=True)),'platform':platform.platform(),'python':sys.version}
    (W/'source.json').write_text(json.dumps(source,indent=2)+'\n')
    def call(name,cmd,failure=False):
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic();stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:r=subprocess.run(cmd,cwd=P,capture_output=True,timeout=30 if failure else 180);rc=r.returncode;out=r.stdout;err=r.stderr;timeout=False
        except subprocess.TimeoutExpired as e:rc=None;out=e.stdout or b'';err=e.stderr or b'';timeout=True
        (W/(name+'.stdout')).write_bytes(out);(W/(name+'.stderr')).write_bytes(err);after=resource.getrusage(resource.RUSAGE_CHILDREN)
        receipt={'command':cmd,'returncode':rc,'timeout':timeout,'started_at':stamp,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wall_seconds_diagnostic':time.monotonic()-start,'cpu_user_seconds':after.ru_utime-before.ru_utime,'cpu_sys_seconds':after.ru_stime-before.ru_stime,'stdout_sha256':sha(W/(name+'.stdout')),'stderr_sha256':sha(W/(name+'.stderr'))}
        (W/(name+'-receipt.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        if failure:assert rc not in (0,None) and not timeout and b'COMPLETE' not in out
        else:assert rc==0 and not timeout and not err and out.splitlines()[-1]==b'COMPLETE',name
        print(name,'returncode',rc,'wall_diagnostic',round(receipt['wall_seconds_diagnostic'],3),flush=True);return out
    for f in ['exception','early']:call('guard-'+f,[sys.executable,'-B',str(P/'forms.py'),'--fault-'+f],True)
    a=call('python',[sys.executable,'-B',str(P/'forms.py')]);b=call('gp',['/opt/homebrew/bin/gp','-q','-f','-s','67108864',str(P/'inputs.gp'),str(P/'compose.gp')])
    def parse(out):
        z=out.decode().splitlines();assert z[0].startswith('CONTROLS ') and z[-1]=='COMPLETE';return json.loads(z[0][9:]),[json.loads(x) for x in z[1:-1]]
    ca,a=parse(a);cb,b=parse(b);assert ca==cb and len(a)==len(b)==21 and a==b
    rows=[];power_count=0
    for i,(r,v) in enumerate(zip(json.loads((P/'INPUTS.json').read_text())['rows'],a)):
        assert v[0]==i;pa=W/'python'/('case-'+str(i)+'.json');pb=W/'gp'/pa.name
        va=json.loads(pa.read_text());vb=json.loads(pb.read_text());assert va==vb and [va[0],va[1],len(va[2])]==v[2:]
        assert pa.stat().st_size<65536 and pb.stat().st_size<65536
        status='UNKNOWN_D_K' if not v[1] else ('ELEMENT_ORDER_GE_200' if v[3]==0 else 'CHOSEN_ELEMENT_SMALL_ORDER')
        rows.append({'index':i,'name':r['name'],'curve_uid':r['curve_uid'],'label':r['label'],'stream':str(r['timestamp'])+':'+str(int(r['p']).bit_length()),'D_K':str(v[1]) if v[1] else None,'prime':v[2] or None,'first_identity_exponent':v[3] or None,'powers_checked':v[4],'status':status,'python_transcript_sha256':sha(pa),'gp_transcript_sha256':sha(pb)})
        power_count+=v[4]
    for arm in ['python','gp']:assert len(list((W/arm).glob('case-*.json')))==21
    result={'status':'PASS','cohort_size':21,'both_implementations_equal':True,'controls':'PASS, including complete reduced-triple agreement and exception/early-return guards','checked_powers_per_arm':power_count,'rows':rows,'counts':{label:{s:sum(r['label']==label and r['status']==s for r in rows) for s in ['ELEMENT_ORDER_GE_200','CHOSEN_ELEMENT_SMALL_ORDER','UNKNOWN_D_K']} for label in ['published','omitted']},'scope':'Single first-odd-split-prime ideal class and exact threshold200. A chosen small-order class would not prove nonexistence of another large-order class. No1997 adoption, retry policy or historical selector established.'}
    (W/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');(W/'COMPLETE').write_text('Both controls and every reduced power agree for all21 retained rows.\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
if __name__=='__main__':main()
