import sys,json,collections
sys.path.insert(0,'/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-001/tasks/TASK-20260731-602')
from aes_reduced import AES,inv_shift_rows,mix_columns,AES_INV_MIX
def pi(ct,j0):
    s=mix_columns(ct,AES_INV_MIX); s=inv_shift_rows(s,(0,1,2,3))
    return bytes(s[4*j0+r] for r in range(4))
res=[]
for line in open("raw_pin2.jsonl"):
    d=json.loads(line)
    base=bytearray(bytes.fromhex(d["base"])); fb=d["free_bytes"][:d["nbits"]//8]
    a=AES(bytes.fromhex(d["key"]),rounds=d["r"],final_mix_columns=bool(d["finalmc"]))
    c=collections.Counter()
    for i in range(1<<d["nbits"]):
        p=bytearray(base)
        for f,b in enumerate(fb): p[b]=(i>>(8*f))&0xff
        c[pi(a.encrypt_block(bytes(p)),d["j0"])]+=1
    n=sum(m*(m-1)//2 for m in c.values())
    res.append({"id":d["id"],"python_n":n,"c_n":d["n"],"match":n==d["n"],
                "python_maxocc":max(c.values()),"c_maxocc":d["max_occupancy"],
                "python_distinct":len(c),"c_distinct":d["distinct_buckets"]})
print(json.dumps({"pin2_all_match":all(r["match"] for r in res),"detail":res},indent=1))
