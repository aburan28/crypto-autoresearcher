"""Frozen finite 4/4-panel analysis; no new solve or target process."""
from __future__ import annotations
import hashlib,json,math,random,statistics
from pathlib import Path
from typing import Any

SEED="N19-AFFINE-SAT-v1-bootstrap"
ARMS=("native_mitm","explicit_onehot","flat_onehot","flat_binary")
def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def percentile(values:list[float],quantile:float)->float:
    rank=(len(values)-1)*quantile;low=math.floor(rank);high=math.ceil(rank)
    return values[low] if low==high else values[low]*(high-rank)+values[high]*(rank-low)
def bootstrap(sat:list[float],unsat:list[float])->dict[str,Any]:
    if len(sat)!=4 or len(unsat)!=4:raise ValueError("bootstrap requires four complete pairs per stratum")
    rng=random.Random(SEED)
    medians=sorted(statistics.median(
        [sat[rng.randrange(4)] for _ in range(4)]+
        [unsat[rng.randrange(4)] for _ in range(4)]) for _ in range(10000))
    return {"seed":SEED,"resamples":10000,"draws_per_stratum":4,"quantile_type":7,
            "lower":percentile(medians,.025),"upper":percentile(medians,.975),
            "sorted_medians_sha256":hashlib.sha256(json.dumps(medians,separators=(",",":")).encode()).hexdigest()}
def analyze(run:Path)->dict[str,Any]:
    frozen=json.loads((run/"case_manifest.json").read_text())
    receipt_path=run/"science_receipts.jsonl"
    rows=[json.loads(line) for line in receipt_path.read_text().splitlines() if line] if receipt_path.is_file() else []
    planned=frozen["science_cases"]
    if len(rows)>32:raise ValueError("science receipt count beyond frozen panel")
    for index,row in enumerate(rows):
        case=planned[index]
        if (row["ordinal"],row["case_id"],row["arm"])!=(case["ordinal"],case["id"],case["arm"]):
            raise ValueError("science receipt order differs from frozen panel")
    by_id={row["case_id"]:row for row in rows}
    case_rows=[];all_valid=len(rows)==32
    sat_ratios=[];unsat_ratios=[]
    for case in frozen["cases"]:
        arms={}
        for arm in ARMS:
            key=next(row["id"] for row in planned if row["case_index"]==case["case_id"] and row["arm"]==arm)
            receipt=by_id.get(key)
            arms[arm]=None if receipt is None else {
                "classification":receipt["classification"],"valid":receipt["valid"],
                "status":(receipt.get("worker_result") or {}).get("status"),
                "wall_seconds":receipt.get("wall_seconds"),
                "wait4":receipt.get("wait4"),
                "worker_stages":(receipt.get("worker_result") or {}).get("stages"),
                "child":(receipt.get("worker_result") or {}).get("child")}
        valid=all(item is not None and item["valid"] for item in arms.values())
        statuses=[item["status"] for item in arms.values() if item is not None]
        same=len(statuses)==4 and len(set(statuses))==1 and statuses[0]==case["stratum"]
        all_valid=all_valid and valid and same
        case_rows.append({"case_index":case["case_id"],"stratum":case["stratum"],
                          "complete_valid":valid and same,"arms":arms})
    all_valid=bool(all_valid)
    # No successful-only effect estimator: an incomplete/censored 32-worker
    # panel has null ratios and bootstrap, while every spent wall remains above.
    comparisons={}
    if all_valid:
        for pair in ("flat_onehot/explicit_onehot","flat_binary/explicit_onehot",
                     "flat_onehot/native_mitm","flat_binary/native_mitm",
                     "explicit_onehot/native_mitm"):
            numerator,denominator=pair.split("/")
            values=[];sat=[];unsat=[]
            for item in case_rows:
                top=item["arms"][numerator]["wall_seconds"]
                bottom=item["arms"][denominator]["wall_seconds"]
                if not (math.isfinite(top) and math.isfinite(bottom) and top>0 and bottom>0):
                    raise ValueError("invalid positive wall measurement")
                ratio=top/bottom
                values.append(ratio)
                (sat if item["stratum"]=="SAT" else unsat).append(ratio)
            entry={"valid_pairs":8,"median":statistics.median(values),
                   "SAT_median":statistics.median(sat),"UNSAT_median":statistics.median(unsat),
                   "paired_ratios":values}
            if pair=="flat_onehot/explicit_onehot":
                entry["stratified_bootstrap_95"]=bootstrap(sat,unsat)
            comparisons[pair]=entry
    else:
        for pair in ("flat_onehot/explicit_onehot","flat_binary/explicit_onehot",
                     "flat_onehot/native_mitm","flat_binary/native_mitm",
                     "explicit_onehot/native_mitm"):
            comparisons[pair]={"valid_pairs_for_effect":0,"median":None,
                               "SAT_median":None,"UNSAT_median":None,
                               "paired_ratios":None,
                               "reason":"fixed 32-worker panel incomplete, censored or incorrect"}
    counts={}
    for arm in ARMS:
        counts[arm]={}
        for stratum in ("SAT","UNSAT"):
            subset=[row for row in rows if row["arm"]==arm and row["stratum"]==stratum]
            counts[arm][stratum]={"launched":len(subset),
                "completed_valid":sum(row["valid"] for row in subset),
                "solver_UNKNOWN_15":sum(row["classification"]=="censored_CMS15" for row in subset),
                "CMS_memory_cap":sum(row["classification"]=="censored_CMS_memory" for row in subset),
                "outer_watchdog":sum(row["classification"]=="censored_outer_watchdog" for row in subset),
                "outer_memory_cap":sum(row["classification"]=="censored_outer_memory" for row in subset),
                "failed":sum(not row["valid"] and not row["classification"].startswith("censored_") for row in subset)}
    primary=comparisons["flat_onehot/explicit_onehot"]
    effect=(all_valid and primary["median"]<=.8 and
            primary["stratified_bootstrap_95"]["upper"]<1)
    result={"schema":"crypto.autoresearch.n19_affine_sat_analysis.v1",
            "experiment_id":"EXP-KIC-c3c732","run_id":"RUN-KIC-859f34",
            "scope":"finite public-synthetic stratified 4 SAT / 4 UNSAT diagnostic panel",
            "inputs":{"science_receipts_sha256":sha(receipt_path) if receipt_path.is_file() else None,
                      "case_manifest_sha256":sha(run/"case_manifest.json")},
            "all32_complete_valid":all_valid,"launched_workers":len(rows),
            "missing_worker_count":32-len(rows),"completion_counts":counts,
            "cases":case_rows,"comparisons":comparisons,
            "finite_prediction_predicate":{"eligible":all_valid,
                                           "median_at_most_point8":primary["median"]<=.8 if all_valid else None,
                                           "bootstrap_upper_below_one":
                                            primary["stratified_bootstrap_95"]["upper"]<1 if all_valid else None,
                                           "passed":bool(effect)},
            "claim_boundary":"finite prototype only; no population, SAT-general, full-IC, rho, security or asymptotic inference"}
    (run/"analysis.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result
