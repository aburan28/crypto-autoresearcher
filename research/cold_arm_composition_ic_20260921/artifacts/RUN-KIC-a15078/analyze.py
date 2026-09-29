#!/usr/bin/env python3
"""Frozen failure-safe four-arm analysis for RUN-KIC-a15078."""
from __future__ import annotations
import argparse,hashlib,json,math,random,statistics
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parent
PROCESSES=ROOT/"receipts/processes.jsonl";CASES=ROOT/"case_manifest.json"
SEED="CSIC53-ARMCOMPOSE-BOOT-v1";RESAMPLES=10000
ARMS=("ic_baseline","ic_candidate","rho_baseline","rho_candidate")
COMPARISONS=("ic_candidate/rho_candidate","ic_candidate/ic_baseline","rho_candidate/rho_baseline","ic_candidate/rho_baseline","ic_baseline/rho_baseline")

def require(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def percentile(values:list[float],p:float)->float:
    pos=(len(values)-1)*p;lo,hi=math.floor(pos),math.ceil(pos)
    return values[lo] if lo==hi else values[lo]*(hi-pos)+values[hi]*(pos-lo)
def bootstrap(values:list[float])->dict[str,Any]|None:
    if not values:return None
    rng=random.Random(SEED);n=len(values)
    medians=sorted(statistics.median(values[rng.randrange(n)] for _ in range(n)) for _ in range(RESAMPLES))
    return {"seed":SEED,"resamples":RESAMPLES,"draws_per_resample":n,"method":"paired resampling, type-7 endpoints","lower_2_5_percent":percentile(medians,.025),"upper_97_5_percent":percentile(medians,.975),"sorted_medians_sha256":hashlib.sha256(json.dumps(medians,separators=(",",":")).encode()).hexdigest()}
def ratio(a:Any,b:Any)->float|None:
    if a is None or b in (None,0):return None
    return float(a)/float(b)
def cpu(row:dict[str,Any])->float|None:
    u,s=row.get("user_cpu_seconds"),row.get("system_cpu_seconds")
    return None if u is None or s is None else float(u)+float(s)
def point(row:dict[str,Any])->Any:
    parsed=row.get("parsed_receipt")
    return parsed.get("published_q") if isinstance(parsed,dict) else None
def pair_valid(a:dict[str,Any],b:dict[str,Any])->bool:
    return a.get("valid") is True and b.get("valid") is True and a.get("scalar")==b.get("scalar") and point(a) is not None and point(a)==point(b)
def mean_or_none(v:list[float])->float|None:return statistics.fmean(v) if v else None
def median_or_none(v:list[float])->float|None:return statistics.median(v) if v else None
def analyze()->dict[str,Any]:
    rows=[json.loads(x) for x in PROCESSES.read_text().splitlines() if x]
    manifest=json.loads(CASES.read_text());cases=manifest["cases"]
    require(len(rows)==len(cases)==96,"analysis requires 96 exact rows")
    for ordinal,(row,case) in enumerate(zip(rows,cases),1):
        require((row.get("ordinal"),row.get("case_id"),row.get("arm"),row.get("scalar"),row.get("seed"))==(ordinal,case["id"],case["arm"],case["scalar"],case["seed"]),f"schedule mismatch at {ordinal}")
    paired=[]
    for index in range(1,25):
        group=[row for row in rows if row["case_index"]==index]
        require(len(group)==4,f"case {index} arm count mismatch")
        arms={row["arm"]:row for row in group};require(set(arms)==set(ARMS),f"case {index} arms mismatch")
        prefix=arms["ic_candidate"].get("prefix_control") or arms["ic_baseline"].get("prefix_control")
        rho_sem=arms["rho_candidate"].get("rho_semantics_control") or arms["rho_baseline"].get("rho_semantics_control")
        prefix_valid=isinstance(prefix,dict) and prefix.get("valid") is True
        rho_valid=isinstance(rho_sem,dict) and rho_sem.get("valid") is True
        validity={}
        for name in COMPARISONS:
            left,right=name.split("/")
            ok=pair_valid(arms[left],arms[right])
            if "ic_candidate" in (left,right):ok=ok and prefix_valid
            if "rho_candidate" in (left,right):ok=ok and rho_valid
            validity[name]=ok
        metrics={}
        for name in COMPARISONS:
            left,right=name.split("/")
            metrics[name]={"wall":ratio(arms[left].get("wall_seconds"),arms[right].get("wall_seconds")) if validity[name] else None,
                           "cpu":ratio(cpu(arms[left]),cpu(arms[right])) if validity[name] else None,
                           "rss":ratio(arms[left].get("wait4_ru_maxrss"),arms[right].get("wait4_ru_maxrss")) if validity[name] else None,
                           "sampled_peak":ratio((arms[left].get("memory_sampling") or {}).get("sampled_peak_bytes"),(arms[right].get("memory_sampling") or {}).get("sampled_peak_bytes")) if validity[name] else None}
        paired.append({"case_index":index,"scalar":arms["ic_candidate"]["scalar"],"order":[row["arm"] for row in sorted(group,key=lambda row:row["position"])],
                       "validity":validity,"prefix_control":prefix,"rho_semantics_control":rho_sem,"metrics":metrics,
                       "terminal_state":{arm:arms[arm].get("terminal_state") for arm in ARMS},
                       "validation_error":{arm:arms[arm].get("validation_error") for arm in ARMS},
                       "raw_arm_values":{arm:{"wall_seconds":arms[arm].get("wall_seconds"),"cpu_seconds":cpu(arms[arm]),"wait4_ru_maxrss":arms[arm].get("wait4_ru_maxrss"),"sampled_peak_bytes":(arms[arm].get("memory_sampling") or {}).get("sampled_peak_bytes"),"parsed_receipt":arms[arm].get("parsed_receipt")} for arm in ARMS}})
    primary="ic_candidate/rho_candidate";values=[p["metrics"][primary]["wall"] for p in paired if p["validity"][primary]]
    interval=bootstrap(values)
    comparisons={}
    for name in COMPARISONS:
        selected=[p for p in paired if p["validity"][name]]
        comparisons[name]={"valid_pairs":len(selected),"invalid_pairs":24-len(selected),
                           "median_wall":median_or_none([p["metrics"][name]["wall"] for p in selected if p["metrics"][name]["wall"] is not None]),
                           "median_cpu":median_or_none([p["metrics"][name]["cpu"] for p in selected if p["metrics"][name]["cpu"] is not None]),
                           "median_wait4_rss":median_or_none([p["metrics"][name]["rss"] for p in selected if p["metrics"][name]["rss"] is not None]),
                           "median_sampled_peak":median_or_none([p["metrics"][name]["sampled_peak"] for p in selected if p["metrics"][name]["sampled_peak"] is not None])}
    summary={"comparisons":comparisons,"primary_arithmetic_mean_wall":mean_or_none(values),"primary_geometric_mean_wall":math.exp(statistics.fmean(math.log(x) for x in values)) if values else None,"primary_bootstrap_median_95_percentile_interval":interval,
             "valid_ic_prefix_controls":sum(isinstance(p["prefix_control"],dict) and p["prefix_control"].get("valid") is True for p in paired),
             "valid_rho_semantics_controls":sum(isinstance(p["rho_semantics_control"],dict) and p["rho_semantics_control"].get("valid") is True for p in paired),
             "failures":{arm:sum(row["arm"]==arm and row.get("valid") is not True for row in rows) for arm in ARMS}}
    eligible=len(values)==24 and summary["valid_ic_prefix_controls"]==24 and summary["valid_rho_semantics_controls"]==24 and comparisons[primary]["median_wall"]<.95 and interval is not None and interval["upper_97_5_percent"]<1
    return {"schema":"crypto.autoresearch.arm_composition_analysis.v1","experiment_id":"RUN-KIC-a15078","scope":"finite public-synthetic four-arm N53 process comparison","inputs":{"processes_sha256":sha(PROCESSES),"case_manifest_sha256":sha(CASES)},"raw_process_table":rows,"paired_cases":paired,"summary":summary,
            "primary_finite_signal_predicate":{"all_24_primary_pairs_valid":len(values)==24,"all_24_ic_prefixes_valid":summary["valid_ic_prefix_controls"]==24,"all_24_rho_semantics_valid":summary["valid_rho_semantics_controls"]==24,"median_below_0_95":comparisons[primary]["median_wall"] is not None and comparisons[primary]["median_wall"]<.95,"bootstrap_upper_below_1_00":interval is not None and interval["upper_97_5_percent"]<1,"eligible_for_independent_review":eligible},
            "no_selection_or_old_pooling":True,"claim_boundary":"observation only; no asymptotic, SOTA, security, break, hypothesis, or goal-status conclusion"}
def markdown(result:dict[str,Any])->str:
    s=result["summary"];p=result["primary_finite_signal_predicate"]
    lines=["# RUN-KIC-a15078 finite analysis","",result["claim_boundary"],"",f"Primary new IC/new rho valid pairs: {s['comparisons']['ic_candidate/rho_candidate']['valid_pairs']} of 24.",f"Primary median wall ratio: {s['comparisons']['ic_candidate/rho_candidate']['median_wall']!r}.",f"Primary bootstrap interval: {s['primary_bootstrap_median_95_percentile_interval']!r}.",f"IC prefix controls: {s['valid_ic_prefix_controls']} of 24; rho semantic controls: {s['valid_rho_semantics_controls']} of 24.",f"Finite predicate eligible: {p['eligible_for_independent_review']}.","","| case | scalar | order | new IC/new rho wall | prefix | rho semantics |","| ---: | ---: | --- | ---: | :---: | :---: |"]
    for row in result["paired_cases"]:lines.append(f"| {row['case_index']} | {row['scalar']} | {','.join(row['order'])} | {row['metrics']['ic_candidate/rho_candidate']['wall']!r} | {(row['prefix_control'] or {}).get('valid')} | {(row['rho_semantics_control'] or {}).get('valid')} |")
    return "\n".join(lines)+"\n"
def self_test():
    v=[.5,1.,2.];a=bootstrap(v);assert a==bootstrap(v) and a["resamples"]==10000
    assert percentile(v,0)==.5 and percentile(v,1)==2.
    print(json.dumps({"self_test":"PASS","tests":3},sort_keys=True))
def main():
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true");a=p.parse_args()
    if a.self_test:self_test();return
    result=analyze();(ROOT/"analysis.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n");(ROOT/"analysis.md").write_text(markdown(result))
if __name__=="__main__":main()
