"""Fixed sequential implementation attempts; watchdogs are resource stops."""
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STUDY=ROOT.parents[2]
PY=sys.executable

def main():
    out=ROOT/'attempts-01';out.mkdir(exist_ok=False);records=[]
    # Prove reduction in fixed membership cases, then join the old public target.
    # Each stratum is separate: stopping one never substitutes an empty set.
    specs=[(3,'distinct','positive',True),(2,'distinct','positive',False),
           (3,'distinct','positive',False),(4,'distinct','positive',False)]
    specs += [(k,s,'positive',False) for k in [2,3,4] for s in ['twoequal','allequal']]
    specs += [(3,s,t,False) for t in ['twoequal','allequal','base','generator']
              for s in ['distinct','twoequal','allequal']]
    for k,stratum,target,member in specs:
        case=ROOT.parent/'checks-02'/('generic-k4.json' if k==4 else 'generic-k3.json')
        label=f'{stratum}-k{k}-{target}'+('-membership' if member else '')
        result=out/(label+'.json')
        cmd=[PY,str(ROOT/'solve.py'),'--case',str(case),'--out',str(result),
             '--depth',str(k),'--stratum',stratum,'--target',target]
        if member:cmd.append('--membership-only')
        rec={'label':label,'command':cmd,'watchdog_seconds':30,'memory_limit_bytes':2*1024**3}
        def limits():resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:
            try:
                proc=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=30,env=env,preexec_fn=limits)
                rec.update(status='PASS' if proc.returncode==0 else 'FAILED_IMPLEMENTATION',returncode=proc.returncode)
            except subprocess.TimeoutExpired:rec.update(status='WATCHDOG_STOP_UNKNOWN',returncode=None)
        if result.exists():rec['result_sha256']=hashlib.sha256(result.read_bytes()).hexdigest()
        records.append(rec);(out/'receipt.json').write_text(json.dumps(records,indent=2)+'\n')
        print(label,rec['status'],flush=True)

if __name__=='__main__':main()
