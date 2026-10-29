"""Fresh fixed resource-bounded F5B attempts; no timing comparison."""
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'attempts-02';out.mkdir(exist_ok=False);records=[]
    for target in ['positive','generator']:
        label=f'distinct-k4-{target}';result=out/(label+'.json')
        cmd=[sys.executable,str(ROOT/'solve_f5b.py'),'--case',str(ROOT.parent/'checks-02/generic-k4.json'),
             '--out',str(result),'--depth','4','--stratum','distinct','--target',target]
        rec={'label':label,'command':cmd,'watchdog_seconds':30,'memory_limit_bytes':2*1024**3,
             'basis_adapter':'SymPy 1.14.0 F5B, grevlex'}
        def limits():resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
        with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:
            try:
                proc=subprocess.run(cmd,stdout=stdout,stderr=stderr,timeout=30,
                    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),preexec_fn=limits)
                rec.update(status='PASS' if proc.returncode==0 else 'FAILED_IMPLEMENTATION',returncode=proc.returncode)
            except subprocess.TimeoutExpired:rec.update(status='WATCHDOG_STOP_UNKNOWN',returncode=None)
        if result.exists():rec['result_sha256']=hashlib.sha256(result.read_bytes()).hexdigest()
        records.append(rec);(out/'receipt.json').write_text(json.dumps(records,indent=2)+'\n')
        print(label,rec['status'],flush=True)

if __name__=='__main__':main()
