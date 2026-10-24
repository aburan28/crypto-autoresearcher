import json, statistics as st, collections
base="/home/user/crypto-autoresearcher/experiments/EXP-ECDLP-20a588/runs/"
rows=[]
for f in ("RUN-ECDLP-20a588-01","RUN-ECDLP-20a588-03"):
    rows+=[json.loads(l) for l in open(base+f+"/raw-result.jsonl")]
# nontrivial equivalence checks (B basis size > 1)
nt=[(r['L'],r['inst']) for r in rows if 'elim_equals_B' in r and r['results']['B_ms']['gb_size']>1]
tr=[(r['L'],r['inst']) for r in rows if 'elim_equals_B' in r and r['results']['B_ms']['gb_size']==1]
print("elim_equals_B true & B basis non-trivial (size>1):",len(nt), "; trivial unit-ideal ([1]) instances:",len(tr), tr)
print("A_elim basis sizes vs B sizes on nontrivial:",[(r['L'],r['inst'],r['results']['A_elim_ms']['gb_size'],r['results']['B_ms']['gb_size']) for r in rows if (r['L'],r['inst']) in nt])
# Singular std_ms vs wall_s ratio
for L in (3,4):
    for A,B in (("A_block_sg","B_sg"),):
        a=[r['results'][A]['std_ms']/1000 for r in rows if r['L']==L and r['results'].get(A,{}).get('status')=='ok']
        b=[r['results'][B]['std_ms']/1000 for r in rows if r['L']==L and r['results'].get(B,{}).get('status')=='ok']
        aw=[r['results'][A]['wall_s'] for r in rows if r['L']==L and r['results'].get(A,{}).get('status')=='ok']
        bw=[r['results'][B]['wall_s'] for r in rows if r['L']==L and r['results'].get(B,{}).get('status')=='ok']
        print("Singular L=%d: median std_ms ratio A/B = %.3f ; median wall ratio = %.3f"%(L,st.median(a)/st.median(b),st.median(aw)/st.median(bw)))
# planted counts per arm
for a in ("A_elim_ms","A_drl_ms","B_ms","A_block_sg","B_sg"):
    ok=[r for r in rows if r['results'].get(a,{}).get('status')=='ok' and r['kind']=='planted']
    print(a,"ok planted:",len(ok),"planted_in_variety True:",sum(r['results'][a].get('planted_in_variety') is True for r in ok))
# A_drl_ms / A_elim_ms wall at L3,4
# instance position effect: ratio inst0-3 vs inst4-5
for L in (3,4,5,6):
    r03=[r['results']['A_elim_ms']['wall_s']/r['results']['B_ms']['wall_s'] for r in rows if r['L']==L and r['inst']<4]
    r45=[r['results']['A_elim_ms']['wall_s']/r['results']['B_ms']['wall_s'] for r in rows if r['L']==L and r['inst']>=4]
    print("L=%d A_elim/B median ratio planted(inst0-3) %.2f ; random(inst4-5) %.2f"%(L,st.median(r03),st.median(r45)))
# growth factors per L
for a in ("A_elim_ms","B_ms"):
    med={L:st.median(r['results'][a]['wall_s'] for r in rows if r['L']==L and r['results'][a]['status']=='ok') for L in range(3,8) if any(r['L']==L and r['results'][a]['status']=='ok' for r in rows)}
    print(a,"median s:",med,"growth x per L:",{L+1:round(med[L+1]/med[L],1) for L in med if L+1 in med})
