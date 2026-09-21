import sys,os,json,hashlib,subprocess,time
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import key_expansion
D=os.path.dirname(os.path.abspath(__file__))
MASTER=b'20260802'
def kdf(tag,n):
    out=b''; i=0
    while len(out)<n:
        out+=hashlib.sha256(MASTER+b'|'+tag.encode()+b'|'+str(i).encode()).digest(); i+=1
    return out[:n]
def rkhex_from_key(k): return b''.join(key_expansion(k,11)).hex()
def run(arm,tag,r,j0,rk,base,pimode='id',ptmode='coset',scrrk=None):
    cmd=[D+'/count5',str(r),str(j0),rk,base.hex(),pimode,ptmode]+([scrrk] if scrrk else [])
    t=time.time()
    p=subprocess.run(cmd,capture_output=True,text=True)
    rec=json.loads(p.stdout.strip())
    rec.update({'arm':arm,'tag':tag,'rk_sha256':hashlib.sha256(bytes.fromhex(rk)).hexdigest(),
                'base':base.hex(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
    with open(D+'/raw.jsonl','a') as f: f.write(json.dumps(rec)+'\n')
    with open(D+'/commands.txt','a') as f: f.write(' '.join(cmd)+'\n')
    print(json.dumps({k:rec[k] for k in ('arm','tag','r','j0','pimode','ptmode','N','n','agree','n_mod8','max_occ','overflow','seconds')}),flush=True)
    return rec
def params(tag):
    b=kdf(tag,33); key=b[:16]; base=b[16:32]; j0=b[32]%4
    return key,base,j0
if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='pc':
        key,base,j0=params('pc0')
        rk=rkhex_from_key(key)
        run('control_r2_j0eq0','pc0',2,0,rk,base)
        run('control_r2_j0ne0','pc0',2,1,rk,base)
        run('control_r3','pc0',3,j0,rk,base)
        run('control_r4','pc0',4,j0,rk,base)
    elif stage in ('r5','r6','r3','r4'):
        r=int(stage[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
        for i in range(a,b):
            key,base,j0=params(f'trial{r}_{i}')
            run(f'aes_r{r}',f'trial{r}_{i}',r,j0,rkhex_from_key(key),base)
    elif stage=='nulls':
        which=sys.argv[2]; a=int(sys.argv[3]); b=int(sys.argv[4])
        for i in range(a,b):
            key,base,j0=params(f'null{which}_{i}')
            rk=rkhex_from_key(key)
            if which=='indeprk':
                rk=kdf(f'irk{i}',176).hex()
                run('null_indep_roundkeys',f'irk{i}',5,j0,rk,base)
            elif which=='sibling':
                run('null_sibling_fwd_diag',f'sib{i}',5,j0,rk,base,pimode='fd')
            elif which=='randperm':
                run('null_randperm_aes10',f'rp{i}',10,j0,rk,base)
            elif which=='randpt':
                run('null_random_plaintexts',f'rpt{i}',5,j0,rk,base,ptmode='scr',
                    scrrk=rkhex_from_key(kdf(f'scr{i}',16)))
