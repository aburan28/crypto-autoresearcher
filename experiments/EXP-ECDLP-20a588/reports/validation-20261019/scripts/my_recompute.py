#!/usr/bin/env python3
"""Independent recomputation of the frozen criteria of EXP-ECDLP-20a588 from raw-result.jsonl.
Written without reading analyze.py. Usage: my_recompute.py RUNDIR [RUNDIR ...]"""
import json, sys, statistics as st, collections
rows=[]
for d in sys.argv[1:]:
    for ln,line in enumerate(open(d.rstrip('/')+'/raw-result.jsonl')):
        r=json.loads(line); r['_src']=d.rstrip('/').split('/')[-1]; rows.append(r)
print("rows:",len(rows), "by run:", dict(collections.Counter(r['_src'] for r in rows)))
# duplicates (L,inst,arm)?
seen=collections.Counter()
for r in rows:
    for a in r['results']: seen[(r['L'],r['inst'],a)]+=1
print("duplicate (L,inst,arm) keys:", [k for k,v in seen.items() if v>1])
Ls=sorted({r['L'] for r in rows})
ARMS=["A_elim_ms","A_drl_ms","B_ms","A_block_sg","B_sg"]
# primes
print("\nprime per L:")
for L in Ls:
    ps={(r['p'],r['p_bits'],r['p'].bit_length()) for r in rows if r['L']==L}
    print(" L=%d"%L, ps)
# per (L,arm): n_total n_ok n_timeout median wall of ok; all-timeout
tab={}
for L in Ls:
    for a in ARMS:
        vs=[r['results'][a] for r in rows if r['L']==L and a in r['results']]
        if not vs: continue
        ok=[v for v in vs if v['status']=='ok']
        tab[(L,a)]=dict(n=len(vs),ok=len(ok),to=sum(v['status']=='timeout' for v in vs),
            other=sum(v['status'] not in('ok','timeout') for v in vs),
            med=st.median([v['wall_s'] for v in ok]) if ok else None,
            allto=all(v['status']=='timeout' for v in vs))
print("\n(L,arm): n ok timeout other median_wall_s(ok)")
for k,v in sorted(tab.items()): print(k, v['n'],v['ok'],v['to'],v['other'], v['med'])
# retirement: smallest L where every instance timed out
ret={}
for a in ARMS:
    for L in Ls:
        t=tab.get((L,a))
        if t and t['allto']: ret[a]=L; break
print("\nretirement L (every instance timed out):",ret)
# largest L with >=1 ok (and all ok)
for a in ARMS:
    okL=[L for L in Ls if tab.get((L,a)) and tab[(L,a)]['ok']>0]
    allok=[L for L in Ls if tab.get((L,a)) and tab[(L,a)]['ok']==tab[(L,a)]['n']]
    print(a,"largest L with >=1 ok:",max(okL) if okL else None,"; largest L all ok:",max(allok) if allok else None)
def pair(A,B):
    print("\n== pair",A,"vs",B)
    joint=[L for L in Ls if tab.get((L,A)) and tab.get((L,B)) and tab[(L,A)]['ok']>0 and tab[(L,B)]['ok']>0]
    print(" jointly completed L (both >=1 ok):",joint)
    jointall=[L for L in Ls if tab.get((L,A)) and tab.get((L,B)) and tab[(L,A)]['ok']==tab[(L,A)]['n'] and tab[(L,B)]['ok']==tab[(L,B)]['n']]
    print(" jointly completed L (both all ok):",jointall)
    ge=0
    for L in joint:
        a,b=tab[(L,A)]['med'],tab[(L,B)]['med']
        print("  L=%d medA=%.4f medB=%.4f ratio A/B=%.3f  A>=B:%s"%(L,a,b,a/b,a>=b))
        ge+= a>=b
    print(" share cells A>=B: %d/%d = %.2f"%(ge,len(joint),ge/len(joint) if joint else float('nan')))
    print(" share cells A<B: %d/%d"%(len(joint)-ge,len(joint)))
    print(" retirement L: A",ret.get(A),"B",ret.get(B))
    return joint,ge
pair("A_elim_ms","B_ms"); pair("A_block_sg","B_sg")
# dynamic range control
print("\n== dynamic range: median(A_drl_ms)/median(A_elim_ms) per L both complete")
for L in Ls:
    if tab.get((L,'A_drl_ms')) and tab[(L,'A_drl_ms')]['ok'] and tab[(L,'A_elim_ms')]['ok']:
        print(" L=%d ratio=%.2f"%(L, tab[(L,'A_drl_ms')]['med']/tab[(L,'A_elim_ms')]['med']))
# per-instance ratios (paired)
print("\n== per-instance A_elim/B_ms (ok both)")
for L in Ls:
    rs=[(r['inst'], r['results']['A_elim_ms']['wall_s']/r['results']['B_ms']['wall_s']) for r in rows if r['L']==L and r['results'].get('A_elim_ms',{}).get('status')=='ok' and r['results'].get('B_ms',{}).get('status')=='ok']
    if rs: print(" L=%d"%L, [round(x,2) for _,x in rs], "min %.2f max %.2f"%(min(x for _,x in rs),max(x for _,x in rs)))
# controls
print("\n== controls")
for a in ARMS:
    okp=[(r['L'],r['inst']) for r in rows if r['results'].get(a,{}).get('status')=='ok' and r['kind']=='planted']
    t=sum(1 for r in rows if r['results'].get(a,{}).get('status')=='ok' and r['kind']=='planted' and r['results'][a].get('planted_in_variety') is True)
    f=[(r['L'],r['inst']) for r in rows if r['results'].get(a,{}).get('status')=='ok' and r['kind']=='planted' and r['results'][a].get('planted_in_variety') is not True]
    okr=sum(1 for r in rows if r['results'].get(a,{}).get('status')=='ok' and r['kind']=='random')
    print(" %s: ok planted=%d planted_in_variety True=%d  non-True=%s ; ok random(no planted)=%d"%(a,len(okp),t,f,okr))
eqs=collections.Counter()
bothok=0
for r in rows:
    A=r['results'].get('A_elim_ms',{}).get('status'); B=r['results'].get('B_ms',{}).get('status')
    both = A=='ok' and B=='ok'
    bothok+=both
    eqs[(both, r.get('elim_equals_B','MISSING'))]+=1
print(" (both msolve ok, elim_equals_B value) counts:",dict(eqs), " both-ok instances:",bothok)
# msolve ok with 17-bit prime?
print("\n== msolve ok results by prime bit-length")
c=collections.Counter()
for r in rows:
    for a,v in r['results'].items():
        if a.endswith('_ms'): c[(r['p'].bit_length() if isinstance(r['p'],int) else r['p_bits'], a, v['status'])]+=1
for k,v in sorted(c.items()): print(" ",k,v)
