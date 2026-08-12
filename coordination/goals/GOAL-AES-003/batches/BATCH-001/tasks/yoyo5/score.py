import json,math
ZP=[math.comb(16,k)*(1/256)**k*(255/256)**(16-k) for k in range(17)]
PW1=1-(1-2**-32)**4
rows=[]
for f in ["sweep_a1_s1.jsonl","diag_seed2.jsonl","masks_seed3.jsonl"]:
    for l in open(f):
        if l.startswith("{"): rows.append(json.loads(l))
print("%-3s %-3s %-3s %-6s %-10s %-6s %-11s %-7s %-6s %-6s %-8s"%("r","A","S","log2N","seed","resbit","Zchi2/dof","Wnt>=1","exp","ratio","log10p"))
out=[]
for d in rows:
    N=d["trials"];zh=d["zhist"]
    obs=[];exp=[];o=e=0.0
    for k in range(17):
        o+=zh[k];e+=N*ZP[k]
        if e>=25: obs.append(o);exp.append(e);o=e=0.0
    if e and obs: obs[-1]+=o;exp[-1]+=e
    x2=sum((a-b)**2/b for a,b in zip(obs,exp))
    wh=d["whist"];triv=d.get("trivial_swaps",0)
    nt=d.get("whist_nontrivial",wh)
    o1=sum(nt[1:]); e1=(N-triv)*PW1
    lp=(-e1+o1*math.log(e1)-math.lgamma(o1+1))/math.log(10) if o1>e1 else 0.0
    print("%-3d %-3d %-3d 2^%-4.0f %-10d %-6.1f %9.1f/%-2d %-7d %-6.1f %-6.2f %-8.1f"%(
        d["rounds"],d["amask"],d["smask"],math.log2(N),d["seed"],math.log2(N/3),x2,len(obs)-1,o1,e1,o1/e1,lp))
    out.append(dict(rounds=d["rounds"],amask=d["amask"],smask=d["smask"],trials=N,seed=d["seed"],
        resolution_bits=round(math.log2(N/3),2),Z_chi2=round(x2,2),Z_dof=len(obs)-1,
        Z_observed_pooled=[int(x) for x in obs],Z_expected_pooled=[round(x,1) for x in exp],
        zhist=zh,whist=wh,trivial_swaps=triv,whist_nontrivial=nt,
        W_ge1_nontrivial=o1,W_ge1_expected_PRPnull=round(e1,2),excess_factor=round(o1/e1,2),
        log10_poisson_tail_p=round(lp,1),
        ct_zero_words_hist=d.get("ct_zero_words_hist"),W1_word_index=d.get("W1_word_index"),
        seconds=d["seconds"]))
json.dump(out,open("analysis.json","w"),indent=1)
