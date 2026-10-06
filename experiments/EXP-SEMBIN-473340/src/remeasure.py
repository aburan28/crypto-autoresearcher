"""EXP-SEMBIN-473340 -- re-measure FFD_SEMAEV_MEASUREMENT1 with the corrected
Boolean product (CORR-20260929-616d03).

Same cells, same RNG streams, same draw counts as
research/verification/ffd_semaev_measure.py (commit on main). Each system's
first fall degree is computed three ways:
  reduced : corrected product, rows kept iff reduced degree <= D
  formal  : corrected product, rows kept iff deg m + deg f <= D (field-equation form)
  legacy  : the superseded OR-row instrument -- CONTROL ONLY, must reproduce
            the published MEASUREMENT1 table exactly
Usage:  python3 remeasure.py OUTDIR      exit 0 executed, 3 infrastructure failure
"""
import sys, os, json, time, random, hashlib, platform
from collections import Counter
from statistics import median
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from boolean_macaulay import fall_profile, first_fall, legacy_or_fall_profile, popcount
from ffd_semaev_core_v1 import build_system, random_matched, on_curve

SEM_DRAWS, NULL_DRAWS = 10, 25
CELLS = [(n, npr) for n in (4, 5, 6, 7) for npr in (3, 4)]
# MEASUREMENT1 section 2, transcribed: (semaev dist, null dist) per cell
PUBLISHED = {
 (4,3): ({2:9,3:1},{2:3,3:22}), (4,4): ({2:6,3:4},{3:1,4:24}),
 (5,3): ({2:10},{2:3,3:22}),    (5,4): ({2:7,3:3},{3:1,4:24}),
 (6,3): ({2:10},{3:25}),        (6,4): ({2:10},{3:2,4:23}),
 (7,3): ({2:9,3:1},{2:13,3:12}),(7,4): ({2:9,3:1},{3:22,4:3}),
}

def indep_basis(n, nprime, rng):          # verbatim from ffd_semaev_measure.py
    for _ in range(400):
        b=[rng.randrange(1,1<<n) for _ in range(nprime)]
        rows=list(b); r=0
        for bit in range(n):
            p=None
            for i in range(r,len(rows)):
                if (rows[i]>>bit)&1: p=i;break
            if p is None: continue
            rows[r],rows[p]=rows[p],rows[r]
            for i in range(len(rows)):
                if i!=r and ((rows[i]>>bit)&1): rows[i]^=rows[r]
            r+=1
        if r==nprime: return b
    return None

def ffd(eqs, N, Dmax, conv):
    if conv == "legacy": return first_fall(legacy_or_fall_profile(eqs, N, Dmax))
    return first_fall(fall_profile(eqs, N, Dmax, conv))

def med(c):
    xs=[k for k,v in c.items() if k is not None for _ in range(v)]
    return median(xs) if xs else None

def main(out):
    os.makedirs(out, exist_ok=True); logf=open(os.path.join(out,"log.txt"),"w")
    def log(*a):
        s=" ".join(map(str,a)); print(s,flush=True); logf.write(s+"\n"); logf.flush()
    t0=time.time(); convs=("reduced","formal","legacy"); rows=[]
    for n,npr in CELLS:
        N=2*npr; a2=a6=1; Dmax=min(N,6)
        sem={c:Counter() for c in convs}; nul={c:Counter() for c in convs}
        for s in range(SEM_DRAWS):             # loop structure verbatim from the original
            rng=random.Random(n*7919+npr*131+s)
            xs=[x for x in range(1<<n) if any(on_curve(x,y,a2,a6,n) for y in range(1<<n))]
            if not xs: continue
            xR=rng.choice(xs); basis=indep_basis(n,npr,rng)
            if basis is None: continue
            eqs=build_system(n,npr,a6,xR,basis)
            if not eqs: continue
            for c in convs: sem[c][ffd(eqs,N,Dmax,c)]+=1
            if s==0:
                for t in range(NULL_DRAWS):
                    r2=random.Random(n*31+npr*7+t); nl=random_matched(eqs,N,r2)
                    for c in convs: nul[c][ffd(nl,N,Dmax,c)]+=1
        row=dict(n=n,nprime=npr,N=N)
        for c in convs:
            row[c]=dict(semaev={str(k):v for k,v in sorted(sem[c].items(),key=lambda kv:(kv[0] is None,kv[0]))},
                        null={str(k):v for k,v in sorted(nul[c].items(),key=lambda kv:(kv[0] is None,kv[0]))},
                        semaev_median=med(sem[c]), null_median=med(nul[c]))
        ps,pn=PUBLISHED[(n,npr)]
        row["legacy_reproduces_published"]=(dict(sem["legacy"])==ps and dict(nul["legacy"])==pn)
        rows.append(row); log(json.dumps(row))
    res=dict(cells=rows, control_C1_legacy_reproduces_all=all(r["legacy_reproduces_published"] for r in rows),
             elapsed_seconds=round(time.time()-t0,1))
    log("C1 legacy reproduces published MEASUREMENT1 =", res["control_C1_legacy_reproduces_all"])
    json.dump(res,open(os.path.join(out,"results.json"),"w"),indent=1)
    src={f:hashlib.sha256(open(os.path.join(HERE,f),"rb").read()).hexdigest() for f in sorted(os.listdir(HERE)) if f.endswith(".py")}
    json.dump(dict(experiment_id="EXP-SEMBIN-473340",command=" ".join(sys.argv),python=platform.python_version(),
                   platform=platform.platform(),source_sha256=src,started_unix=t0,elapsed_seconds=res["elapsed_seconds"]),
              open(os.path.join(out,"manifest.json"),"w"),indent=1)

if __name__=="__main__":
    try: main(sys.argv[1])
    except Exception:
        import traceback; traceback.print_exc(); sys.exit(3)
