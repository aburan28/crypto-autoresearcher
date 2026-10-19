import json, statistics as st
base="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588/runs/"
rows=[]
for f in ("RUN-ECDLP-20a588-01","RUN-ECDLP-20a588-03"):
    rows+=[json.loads(l) for l in open(base+f+"/raw-result.jsonl")]
crit=json.load(open("replay_HEAD/criteria.json")); summ=json.load(open("replay_HEAD/summary.json"))
bad=0
# medians
for s in summ:
    ok=[r['results'][s['arm']]['wall_s'] for r in rows if r['L']==s['L'] and r['results'].get(s['arm'],{}).get('status')=='ok']
    if ok:
        mine=1000*st.median(ok)
        if abs(mine-s['median_ms'])>1e-6: bad+=1; print("median differs",s['L'],s['arm'],mine,s['median_ms'])
    else:
        if 'median_ms' in s: bad+=1; print("unexpected median",s)
print("per-(L,arm) medians compared:",len(summ),"differences:",bad)
# ratios
def med(L,a): return st.median(r['results'][a]['wall_s'] for r in rows if r['L']==L and r['results'].get(a,{}).get('status')=='ok')
for name,(a,b) in {"msolve A_elim vs B":("A_elim_ms","B_ms"),"Singular A_block vs B":("A_block_sg","B_sg"),"dynamic range A_drl vs A_elim (msolve)":("A_drl_ms","A_elim_ms")}.items():
    c=crit[name]
    for Lk,v in c['ratio'].items():
        L=int(Lk[1:]); mine=round(med(L,a)/med(L,b),2)
        if mine!=v: bad+=1; print("ratio differs",name,Lk,mine,v)
print("total differences vs analyze.py criteria/summary:",bad)
