"""Frozen paired technical-repeat statistics for the N19 pair-transport panel."""
from __future__ import annotations
import hashlib,json,math,random,statistics
from pathlib import Path
from typing import Any

ARMS=("expanded","canonical_poly","canonical_normal_x")
SEED="N19-PAIR-TRANSPORT-v1-bootstrap"
PAIRS=("canonical_normal_x/expanded","canonical_poly/expanded",
       "canonical_normal_x/canonical_poly")
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def percentile(sorted_values:list[float],p:float)->float:
    rank=(len(sorted_values)-1)*p;lo=math.floor(rank);hi=math.ceil(rank)
    return sorted_values[lo] if lo==hi else sorted_values[lo]*(hi-rank)+sorted_values[hi]*(rank-lo)
def bootstrap(sat:list[float],unsat:list[float])->dict[str,Any]:
    if len(sat)!=4 or len(unsat)!=4:raise ValueError("stratified bootstrap requires four cases in each stratum")
    rng=random.Random(SEED)
    medians=sorted(statistics.median(
        [sat[rng.randrange(4)] for _ in range(4)]+
        [unsat[rng.randrange(4)] for _ in range(4)]) for _ in range(10000))
    return {"seed":SEED,"resamples":10000,"draws_per_stratum":4,"type":7,
            "lower":percentile(medians,.025),"upper":percentile(medians,.975),
            "sorted_medians_sha256":hashlib.sha256(json.dumps(medians,separators=(",",":")).encode()).hexdigest()}
def analyze(run:Path)->dict[str,Any]:
    schedule=json.loads((run/"case_manifest.json").read_text())
    receipt_path=run/"benchmark_receipts.jsonl"
    rows=[json.loads(x) for x in receipt_path.read_text().splitlines() if x] if receipt_path.is_file() else []
    planned=schedule["workers"]
    if len(rows)>144:raise ValueError("benchmark receipt count exceeds frozen schedule")
    for index,row in enumerate(rows):
        case=planned[index]
        if (row["ordinal"],row["case_id"],row["replicate"],row["arm"],row["Q"])!=(
            case["ordinal"],case["case_id"],case["replicate"],case["arm"],case["Q"]):
            raise ValueError(f"benchmark schedule prefix differs at {index+1}")
    by_key={(r["case_id"],r["replicate"],r["arm"]):r for r in rows}
    cases=json.loads((run/"case_manifest.json").read_text())["cases"]
    complete=len(rows)==144 and all(r["valid"] for r in rows)
    case_summaries=[];ratios={pair:{"SAT":[],"UNSAT":[]} for pair in PAIRS}
    for case in cases:
        per_arm={}
        for arm in ARMS:
            six=[by_key.get((case["case_id"],replicate,arm)) for replicate in range(6)]
            full=all(row is not None and row["valid"] for row in six)
            per_arm[arm]={"actual_receipts":sum(row is not None for row in six),
                          "valid_receipts":sum(bool(row and row["valid"]) for row in six),
                          "all_six_valid":full,
                          "walls":[row["wall_seconds"] if row else None for row in six],
                          "median_wall":statistics.median(row["wall_seconds"] for row in six) if full else None}
        case_complete=all(item["all_six_valid"] for item in per_arm.values())
        complete=complete and case_complete
        case_summaries.append({"case_id":case["case_id"],"stratum":case["stratum"],
                               "all18_valid":case_complete,"arms":per_arm})
    comparisons={}
    if complete:
        for name in PAIRS:
            top,bottom=name.split("/")
            values=[]
            for case in case_summaries:
                numerator=case["arms"][top]["median_wall"]
                denominator=case["arms"][bottom]["median_wall"]
                if not all(math.isfinite(v) and v>0 for v in (numerator,denominator)):
                    raise ValueError("nonpositive/nonfinite case median wall")
                ratio=numerator/denominator
                values.append({"case_id":case["case_id"],"stratum":case["stratum"],"ratio":ratio})
                ratios[name][case["stratum"]].append(ratio)
            sat=ratios[name]["SAT"];unsat=ratios[name]["UNSAT"]
            comparisons[name]={"eligible":True,"case_ratios":values,
                "median_of_eight_case_ratios":statistics.median(row["ratio"] for row in values),
                "SAT_median":statistics.median(sat),"UNSAT_median":statistics.median(unsat),
                "stratified_bootstrap_95":bootstrap(sat,unsat)}
    else:
        for name in PAIRS:
            comparisons[name]={"eligible":False,"case_ratios":None,
                "median_of_eight_case_ratios":None,"SAT_median":None,"UNSAT_median":None,
                "stratified_bootstrap_95":None,
                "reason":"fixed 144-worker panel has missing, censored or invalid receipt; no successful-only effect estimator"}
    count={arm:{stratum:{"launched":0,"valid":0,"watchdog":0,"memory_cap":0,"fault":0}
                for stratum in ("SAT","UNSAT")} for arm in ARMS}
    for row in rows:
        entry=count[row["arm"]][row["stratum"]];entry["launched"]+=1
        entry["valid"]+=bool(row["valid"])
        entry["watchdog"]+=row["classification"]=="censored_watchdog"
        entry["memory_cap"]+=row["classification"]=="censored_memory"
        entry["fault"]+=row["classification"]=="failed_process_or_identity"
    primary=comparisons["canonical_normal_x/expanded"]
    predicate={"eligible":bool(complete),
               "median_at_most_point8":primary["median_of_eight_case_ratios"]<=.8 if complete else None,
               "bootstrap_upper_below_one":primary["stratified_bootstrap_95"]["upper"]<1 if complete else None,
               "passed":bool(complete and primary["median_of_eight_case_ratios"]<=.8 and
                             primary["stratified_bootstrap_95"]["upper"]<1)}
    result={"schema":"crypto.autoresearch.n19_pair_transport_analysis.v1",
            "scope":"finite public-synthetic eight-case/6-technical-repeat panel; not IID targets",
            "inputs":{"schedule_sha256":sha(run/"case_manifest.json"),
                      "benchmark_receipts_sha256":sha(receipt_path) if receipt_path.is_file() else None},
            "planned_workers":144,"launched_workers":len(rows),"unlaunched_workers":144-len(rows),
            "all144_complete_valid":bool(complete),"status_counts":count,
            "cases":case_summaries,"comparisons":comparisons,
            "finite_effect_predicate":predicate,
            "observed_spent_child_wall_seconds":sum(row.get("wall_seconds",0) for row in rows),
            "claim_boundary":"no full-IC, rho, asymptotic, generic population or security inference"}
    (run/"analysis.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result
