"""Sequential correctness supervisor; resource watchdog is not a performance trial."""
import hashlib,json,os,resource,subprocess,sys
from pathlib import Path
from f1 import write
ROOT=Path(__file__).resolve().parent

def constrain():
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))

def main():
    out=ROOT/'forward-01';out.mkdir(exist_ok=False)
    records=[]
    # Fixed small exact elimination cases. Three increasing depths, no timing comparison.
    for mode,k in [('membership',1),('membership',2),('joint',1),('joint',2),('joint',3)]:
        label=f'{mode}-k{k}';dest=out/(label+'.json')
        command=[sys.executable,str(ROOT/'forward.py'),'--case',str(ROOT/'checks-02/generic-k3.json'),
                 '--out',str(dest),'--mode',mode,'--depth',str(k)]
        rec={'command':command,'watchdog_seconds':30,'memory_limit_bytes':2*1024**3}
        with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:
            try:
                proc=subprocess.run(command,stdout=stdout,stderr=stderr,timeout=30,preexec_fn=constrain)
                rec.update(returncode=proc.returncode,status='PASS' if proc.returncode==0 else 'FAILED_IMPLEMENTATION')
            except subprocess.TimeoutExpired:rec.update(status='WATCHDOG_STOP_NO_COMPLETENESS',returncode=None)
        if dest.exists():rec['result_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
        records.append(rec);write(out/'receipt.json',records)
        print(label,rec['status'],flush=True)

if __name__=='__main__':main()
