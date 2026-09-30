"""Predeclared finite N7 analysis; observations only, no status transition."""
from __future__ import annotations
import hashlib,json,math,random,statistics
from pathlib import Path
from typing import Any
import field,checker

ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/"runs/RUN-KIC-c2b1b7"
ARMS=("flat_sat","explicit_same_B","null_sat","direct_mitm")
PAIRS=("flat_sat/explicit_same_B","flat_sat/direct_mitm","flat_sat/null_sat")
SEED="GFB-SAT-N7-v1-bootstrap"
def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def percentile(values:list[float],p:float)->float:
    rank=(len(values)-1)*p;lo=math.floor(rank);hi=math.ceil(rank)
    return values[lo] if lo==hi else values[lo]*(hi-rank)+values[hi]*(rank-lo)
def bootstrap(ratios:list[float])->dict[str,Any]|None:
    if not ratios:return None
    rng=random.Random(SEED);n=len(ratios)
    medians=sorted(statistics.median(ratios[rng.randrange(n)] for _ in range(n)) for _ in range(10000))
    return {"seed":SEED,"resamples":10000,"draws_per_resample":n,"type":7,"lower":percentile(medians,.025),"upper":percentile(medians,.975),"sorted_medians_sha256":hashlib.sha256(json.dumps(medians,separators=(",",":")).encode()).hexdigest()}
def median(values:list[float])->float|None:return statistics.median(values) if values else None
def _rows(path:Path)->list[dict[str,Any]]:return [json.loads(x) for x in path.read_text().splitlines() if x]
def analyze()->dict[str,Any]:
    cases=json.loads((RUN/"case_manifest.json").read_text())["science_cases"]
    rows=_rows(RUN/"receipts.jsonl");controls=json.loads((RUN/"control_replay.json").read_text())
    science_replay=json.loads((RUN/"replay.json").read_text())
    if len(cases)!=64 or len(rows)!=64:raise ValueError("science count mismatch")
    for ordinal,(case,row) in enumerate(zip(cases,rows),1):
        if (case["ordinal"],case["id"],case["arm"],case["scalar"])!=(ordinal,row["case_id"],row["arm"],row["scalar_driver_only"]):raise ValueError(f"science schedule mismatch at {ordinal}")
    grouped=[]
    for i in range(1,17):
        rr=[row for row in rows if row["case_index"]==i]
        if len(rr)!=4:raise ValueError(f"case {i} arm count mismatch")
        arms={r["arm"]:r for r in rr}
        if set(arms)!=set(ARMS):raise ValueError(f"case {i} arm set mismatch")
        flat_result=arms["flat_sat"].get("worker_result")
        same_b=bool(flat_result) and all(
            arms[a].get("worker_result") is not None
            and arms[a]["worker_result"].get("status")==flat_result.get("status")
            for a in ("explicit_same_B","direct_mitm")
        )
        valid=all(arms[a]["valid"] for a in ARMS) and same_b
        ratios={}
        for name in PAIRS:
            left,right=name.split("/")
            denominator=arms[right]["wall_seconds"]
            ratios[name]=arms[left]["wall_seconds"]/denominator if valid and denominator>0 else None
        grouped.append({"case_index":i,"phase":"diagnostic" if i<=8 else "heldout","scalar":arms["flat_sat"]["scalar_driver_only"],"valid":valid,"same_candidate_B_outcome":same_b,"arms":{a:{"wall_seconds":arms[a]["wall_seconds"],"outer_cpu":arms[a]["outer_wait4"],"cms":(arms[a]["worker_result"] or {}).get("cms"),"stages":(arms[a]["worker_result"] or {}).get("stages"),"status":(arms[a]["worker_result"] or {}).get("status"),"valid":arms[a]["valid"]} for a in ARMS},"ratios":ratios})
    held=[row for row in grouped if row["phase"]=="heldout"]
    all16_valid=all(row["valid"] for row in grouped)
    complete=controls["valid"] and science_replay["valid"] and len(rows)==64 and len(held)==8 and all16_valid
    pair_stats={}
    for name in PAIRS:
        values=[row["ratios"][name] for row in held if row["ratios"][name] is not None]
        pair_stats[name]={"valid_pairs":len(values),"median":median(values),"bootstrap_95":bootstrap(values)}
    basis=json.loads((RUN/"basis_manifest.json").read_text());candidate,null=basis["candidate"],basis["null"]
    g=field.generator();coverage={}
    for name,base in (("candidate",candidate),("null",null)):
        coverage[name]=sum(checker.oracle_status(field.scalar_mul(g,d),base)=="SAT" for d in range(1,71))
    prefix=json.loads((RUN/"prefix_propagation.json").read_text())
    prefix_eligible=prefix["eligible_cases"]>=4
    prefix_delta=prefix["paired_median_flat_minus_explicit"]
    effects=complete and coverage["candidate"]>=coverage["null"] and prefix_eligible and prefix_delta is not None and prefix_delta>=.10
    for stats in pair_stats.values():
        effects=effects and stats["valid_pairs"]==8 and stats["median"] is not None and stats["median"]<=.80 and stats["bootstrap_95"] is not None and stats["bootstrap_95"]["upper"]<1
    summary={"controls_valid":controls["valid"],"science_replay_valid":science_replay["valid"],"complete_all_cases":sum(row["valid"] for row in grouped),"complete_heldout_cases":sum(row["valid"] for row in held),"candidate_coverage70":coverage["candidate"],"null_coverage70":coverage["null"],"pair_stats":pair_stats,"prefix_eligible_cases":prefix["eligible_cases"],"prefix_paired_median_flat_minus_explicit":prefix_delta,"prefix_effect_eligibility":prefix["effect_eligibility"],"failed_workers":sum(not row["valid"] for row in rows)}
    result={"schema":"crypto.autoresearch.gfb_analysis.v1","experiment_id":"EXP-KIC-424885","run_id":"RUN-KIC-c2b1b7","scope":"finite public-synthetic N7 exact-three decomposition only","inputs":{"science_receipts_sha256":sha(RUN/"receipts.jsonl"),"control_replay_sha256":sha(RUN/"control_replay.json"),"prefix_propagation_sha256":sha(RUN/"prefix_propagation.json")},"all_raw_rows":rows,"cases":grouped,"summary":summary,"finite_effect_predicate":{"all16_correctness_and_all8_heldout_valid":complete,"candidate_coverage_at_least_null":coverage["candidate"]>=coverage["null"],"three_wall_ratios_and_bootstraps_pass":all(s["median"] is not None and s["median"]<=.80 and s["bootstrap_95"] is not None and s["bootstrap_95"]["upper"]<1 for s in pair_stats.values()),"prefix_effect_pass":prefix_eligible and prefix_delta is not None and prefix_delta>=.10,"eligible_for_independent_review":bool(effects)},"claim_boundary":"finite N7 implementation observation; no N19/asymptotic/security/break conclusion"}
    (RUN/"analysis.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result
