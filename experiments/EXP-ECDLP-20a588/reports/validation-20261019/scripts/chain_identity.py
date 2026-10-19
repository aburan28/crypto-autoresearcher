import importlib.util, json, random, hashlib, glob
HERE="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588"
spec=importlib.util.spec_from_file_location("bog",HERE+"/block_order_grid.py"); bog=importlib.util.module_from_spec(spec); spec.loader.exec_module(bog)
pkm=bog.pkm
plan=json.load(open(HERE+"/trial-plan.json"))
old={}
for l in open(glob.glob("/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-502ae2/runs/*/raw-result.jsonl")[0]):
    r=json.loads(l); old[(r['L'],r['inst'])]=r
match=tot=0
for L in range(3,8):
    for inst in range(6):
        seed=int(hashlib.sha256(f"{plan['seed']}|3|{L}|{inst}".encode()).hexdigest()[:12],16)
        rng=random.Random(seed); p=pkm.find_prime(3,L); a=p-3
        while True:
            b=rng.randrange(1,p)
            if (4*a**3+27*b*b)%p: break
        ch=pkm.build_chain(p,L,rng)
        o=old[(L,inst)]
        tot+=1; match+= (o['chain_c']==ch['c'] and o['b']==b and o['p']==p and o['seed']==seed)
print("chain constant c, b, p, seed identical to EXP-ECDLP-502ae2 on",match,"/",tot,"(L=3..7, inst 0..5)")
