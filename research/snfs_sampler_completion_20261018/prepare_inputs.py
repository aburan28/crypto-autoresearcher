"""Freeze a deterministic panel from saved inputs; draws no new curve/search samples."""
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-e89532/raw-result.json"


def canonical_key(c):
    return (tuple(c["field"]["g"]), c["field"]["p"], c["root_mod_p"],c["curve"]["A"],c["curve"]["B"])


def main():
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == "aca946ae4f12f9d73ff3d255d0f14305a65b964326801751057c432d4a47efd6"
    raw=json.loads(RAW.read_text())["cells"]
    groups=defaultdict(list)
    for i,c in enumerate(raw): groups[canonical_key(c)].append((i,c))
    selected=[rows for rows in groups.values() if len({c["seed"] for _,c in rows})>1]
    assert len(selected)==4
    for d in (7,8,12):
        candidates=[(key,rows) for key,rows in groups.items() if any(c["seed"]==1 and c["field"]["kind"]=="random_g" and c["field"]["d"]==d for _,c in rows)]
        selected.append(min(candidates,key=lambda kv:json.dumps(kv[0]))[1])
    inputs=[];jobs=[];seeds=set()
    for index,rows in enumerate(selected):
        source_index,c=next((i,c) for i,c in rows if c["seed"]==1)
        ident="fixed-"+hashlib.sha256(json.dumps(canonical_key(c)).encode()).hexdigest()[:16]
        assert all(r["aux_primes"]==c["aux_primes"] for _,r in rows)
        legacy=[1,3] if index<4 else [1]
        inp=dict(id=ident,g=c["field"]["g"],p=c["field"]["p"],root=c["root_mod_p"],A=c["curve"]["A"],B=c["curve"]["B"],aux_primes=c["aux_primes"],
                 source_row=source_index,source_shape=c["field"]["shape"],source_seeds=legacy)
        inputs.append(inp)
        for seed in legacy:
            old_index,_=next((i,r) for i,r in rows if r["seed"]==seed)
            jobs.append(dict(id=f"legacy-{index}-{seed}",input_id=ident,role="legacy_control",search_seed=str(seed),source_row=old_index))
        for rep in range(12):
            seed=f"snfs-sampler-completion-20261018:{ident}:rep-{rep:02d}"
            assert seed not in seeds;seeds.add(seed)
            jobs.append(dict(id=f"fresh-{index}-{rep:02d}",input_id=ident,role="fresh",search_seed=seed))
        jobs.append(dict(id=f"replay-{index}",input_id=ident,role="same_seed_replay",search_seed=f"snfs-sampler-completion-20261018:{ident}:rep-00",replay_of=f"fresh-{index}-00"))
    assert len(inputs)==7 and len(jobs)==102 and len(seeds)==84
    panel=dict(schema="snfs.fixed_input_panel.v1",source_raw=str(RAW.relative_to(ROOT)),source_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
               selection="All four incidental cross-seed overlaps, then minimum canonical-JSON key among seed-1 random_g rows per degree 7/8/12; no outcome filter.",
               ladder=[300,1000,3000,10000,30000,100000],denominators=[1,2,3,4],inputs=inputs,jobs=jobs)
    coefficients=[]
    for shape,d,w in [("P-192",3,3),("P-224",7,3),("P-256",8,5),("P-384",12,5)]:
        for positions in combinations(range(1,d),w-2):
            for signs in product((-1,1),repeat=w-1):
                g=[0]*(d+1);g[0]=signs[0];g[d]=1
                for pos,sign in zip(positions,signs[1:]):g[pos]=sign
                coefficients.append(dict(shape=shape,g=g))
    assert len(coefficients)==3232
    for name,value in [("panel.json",panel),("coefficients.json",coefficients)]:
        with (HERE/name).open("x") as h:json.dump(value,h,indent=2);h.write("\n")
    print(json.dumps(dict(inputs=len(inputs),fresh_seeds=len(seeds),jobs=len(jobs),coefficients=len(coefficients))))


if __name__=="__main__":main()
