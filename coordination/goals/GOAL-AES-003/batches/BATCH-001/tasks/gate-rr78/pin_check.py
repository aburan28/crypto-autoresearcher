import sys,subprocess,hashlib,json,random
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import AES, key_expansion, MODULE_SHA256
rng=random.Random(20260801)
cases=[]; lines=[]
# FIPS-197 known answer (appendix B / C.1)
kat_key=bytes.fromhex("000102030405060708090a0b0c0d0e0f")
kat_pt =bytes.fromhex("00112233445566778899aabbccddeeff")
kat_ct ="69c4e0d86a7b0430d8cdb78070b4c55a"
for r in range(1,11):
    for fmc in (0,1):
        for t in range(6):
            key=bytes(rng.randrange(256) for _ in range(16))
            pt =bytes(rng.randrange(256) for _ in range(16))
            cases.append((key,r,fmc,pt))
cases.append((kat_key,10,0,kat_pt))
# independent-random-round-key case: round keys NOT from a schedule
indep=[]
for r in (4,6):
    rks=[bytes(rng.randrange(256) for _ in range(16)) for _ in range(r+1)]
    pt=bytes(rng.randrange(256) for _ in range(16))
    indep.append((rks,r,0,pt))
for key,r,fmc,pt in cases:
    rks=key_expansion(key,r+1)
    lines.append(b"".join(rks).hex()+f" {r} {fmc} "+pt.hex())
for rks,r,fmc,pt in indep:
    lines.append(b"".join(rks).hex()+f" {r} {fmc} "+pt.hex())
out=subprocess.run(["./pin"],input="\n".join(lines)+"\n",capture_output=True,text=True)
got=out.stdout.split()
fails=[];n=0
for i,(key,r,fmc,pt) in enumerate(cases):
    ref=AES(key,rounds=r,final_mix_columns=bool(fmc)).encrypt_block(pt).hex(); n+=1
    if ref!=got[i]: fails.append(("sched",i,r,fmc,ref,got[i]))
for j,(rks,r,fmc,pt) in enumerate(indep):
    i=len(cases)+j
    a=AES(bytes(16),rounds=r,final_mix_columns=bool(fmc)); a.round_keys=list(rks)
    ref=a.encrypt_block(pt).hex(); n+=1
    if ref!=got[i]: fails.append(("indep",i,r,fmc,ref,got[i]))
kat_i=len(cases)-1
res={"module_sha256":MODULE_SHA256,"vectors_compared":n,"failures":fails,
     "fips197_kat_expected":kat_ct,"fips197_kat_c_path":got[kat_i],
     "fips197_kat_ok":got[kat_i]==kat_ct,"pin_ok":(not fails) and got[kat_i]==kat_ct}
print(json.dumps(res,indent=1))
sys.exit(0 if res["pin_ok"] else 1)
