import sys,os,json,hashlib,subprocess,random
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import AES, key_expansion, MODULE_SHA256
from Crypto.Cipher import AES as PCAES
D='/tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad/count5'
def rkhex(key):
    return b''.join(key_expansion(key,11)).hex()
def cenc(r,rk,pt):
    return subprocess.run([D+'/pin',str(r),rk,pt.hex()],capture_output=True,text=True).stdout.strip()
res={'module_sha256':MODULE_SHA256,'checks':[],'failures':0}
rnd=random.Random(20260802)
# FIPS-197 KAT
k=bytes(range(16)); p=bytes.fromhex('00112233445566778899aabbccddeeff')
kat=PCAES.new(k,PCAES.MODE_ECB).encrypt(p).hex()
res['checks'].append({'kind':'fips197_kat','expect':'69c4e0d86a7b0430d8cdb78070b4c55a','pycrypto':kat,
                      'c':cenc(10,rkhex(k),p),'aes_reduced':AES(k,rounds=10).encrypt_block(p).hex()})
for c in res['checks']:
    if len({c['expect'],c['pycrypto'],c['c'],c['aes_reduced']})!=1: res['failures']+=1
nv=0
for t in range(8):
    key=bytes(rnd.randrange(256) for _ in range(16)); pt=bytes(rnd.randrange(256) for _ in range(16))
    rk=rkhex(key)
    for r in range(1,11):
        a=AES(key,rounds=r,final_mix_columns=False).encrypt_block(pt).hex()
        b=cenc(r,rk,pt); nv+=1
        if a!=b: res['failures']+=1; res['checks'].append({'kind':'mismatch','r':r,'key':key.hex(),'pt':pt.hex(),'aes_reduced':a,'c':b})
# independent round keys path (11 uniform round keys)
for t in range(3):
    rkb=[bytes(rnd.randrange(256) for _ in range(16)) for _ in range(11)]
    rk=b''.join(rkb).hex(); pt=bytes(rnd.randrange(256) for _ in range(16))
    for r in (4,5,6):
        # emulate in python directly
        from aes_reduced import sub_bytes,shift_rows,mix_columns,add_round_key,aes_sbox,AES_MIX
        S=aes_sbox(); OFF=(0,1,2,3)
        s=bytes(x^y for x,y in zip(pt,rkb[0]))
        for i in range(1,r): s=add_round_key(mix_columns(shift_rows(sub_bytes(s,S),OFF),AES_MIX),rkb[i])
        s=add_round_key(shift_rows(sub_bytes(s,S),OFF),rkb[r])
        b=cenc(r,rk,pt); nv+=1
        if s.hex()!=b: res['failures']+=1; res['checks'].append({'kind':'indep_rk_mismatch','r':r,'py':s.hex(),'c':b})
res['n_vectors']=nv+1
json.dump(res,open(D+'/pin_result.json','w'),indent=1)
print(json.dumps({'n_vectors':res['n_vectors'],'failures':res['failures'],'kat':res['checks'][0]}))
