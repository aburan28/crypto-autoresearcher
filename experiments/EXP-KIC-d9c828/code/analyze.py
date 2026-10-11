#!/usr/bin/env python3
"""Frozen P9 paired-panel analysis; no successful-only estimator is permitted."""
from __future__ import annotations
import hashlib,json,math,random,statistics
from pathlib import Path

SEED="PAIR-REUSE-v1-bootstrap"
ARMS=("expanded","canonical_normal_x")
REGIMES=("n19_k4","n23_k16")
MS=(1,32,512)
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def q7(a:list[float],p:float)->float:
    a=sorted(a);x=(len(a)-1)*p;i=int(x);j=math.ceil(x)
    return a[i] if i==j else a[i]*(j-x)+a[j]*(x-i)
def interval(values:list[float])->dict:
    rng=random.Random(SEED)
    draws=sorted(statistics.median([values[rng.randrange(8)] for _ in range(8)]) for _ in range(10000))
    return {"seed":SEED,"resamples":10000,"type":7,"lower":q7(draws,.025),"upper":q7(draws,.975),"draws_sha256":hashlib.sha256(json.dumps(draws,separators=(",",":")).encode()).hexdigest()}
def analyze(run:Path)->dict:
    manifest=json.loads((run/"case_manifest.json").read_text()); planned=manifest["jobs"]
    control_path=run/"control_receipt.json";checker_path=run/"checker_receipt.json"
    control=json.loads(control_path.read_text()) if control_path.is_file() else {}
    checker=json.loads(checker_path.read_text()) if checker_path.is_file() else {}
    receipt=run/"benchmark_receipts.jsonl"
    actual=[json.loads(x) for x in receipt.read_text().splitlines() if x] if receipt.exists() else []
    if len(actual)>384:raise ValueError("more than fixed 384 job receipts")
    for i,row in enumerate(actual):
        want=planned[i]
        for k in ("ordinal","regime","M","panel","repeat","arm"):
            if row.get(k)!=want[k]:raise ValueError(f"schedule prefix mismatch ordinal {i+1}: {k}")
    by={(r["regime"],r["M"],r["panel"],r["repeat"],r["arm"]):r for r in actual}
    receipt_keys=[(r["regime"],r["M"],r["panel"],r["repeat"],r["arm"]) for r in actual]
    all_jobs_valid=(len(actual)==384 and len(by)==384 and len(set(receipt_keys))==384 and
        all(r.get("valid") is True and r.get("classification")=="completed_valid" and
            isinstance(r.get("wall_seconds"),(int,float)) and math.isfinite(r["wall_seconds"]) and
            r["wall_seconds"]>0 for r in actual))
    prerequisite_valid=control.get("valid") is True and checker.get("valid") is True
    all_valid=bool(prerequisite_valid and all_jobs_valid)
    # Determine whole-panel eligibility before computing any cell effect.
    cell_inputs={}
    for regime in REGIMES:
      for m in MS:
        cell_inputs[(regime,m)]={}
        for panel in range(8):
          cell_inputs[(regime,m)][panel]={arm:[by.get((regime,m,panel,repeat,arm)) for repeat in range(4)] for arm in ARMS}
    cells=[]
    for regime in REGIMES:
      for m in MS:
        panels=[]
        for panel in range(8):
          med={}
          for arm in ARMS:
            rs=cell_inputs[(regime,m)][panel][arm]
            valid=all_valid and all(r is not None for r in rs)
            med[arm]=statistics.median(r["wall_seconds"] for r in rs) if valid else None
          panels.append({"panel":panel,"arm_medians":med,"ratio":None if None in med.values() else med["canonical_normal_x"]/med["expanded"]})
        ratios=[p["ratio"] for p in panels]
        eligible=all_valid and all(x is not None and math.isfinite(x) and x>0 for x in ratios)
        cells.append({"regime":regime,"M":m,"panels":panels,"eligible":eligible,"median_of_8_paired_ratios":statistics.median(ratios) if eligible else None,"bootstrap_95":interval(ratios) if eligible else None,"reason":None if eligible else "missing, invalid, censored, or nonpositive fixed-schedule receipt; no successful-only statistic"})
    primary=next(c for c in cells if c["regime"]=="n23_k16" and c["M"]==512)
    out={"schema":"crypto.autoresearch.pair_reuse_analysis.v1","scope":"finite public-synthetic cold-job comparison; no IC/rho/scaling inference","planned_jobs":384,"launched_jobs":len(actual),"control_valid":control.get("valid") is True,"checker_valid":checker.get("valid") is True,"all384_jobs_valid":all_jobs_valid,"all384_complete_valid":all_valid,"inputs":{"case_manifest_sha256":sha(run/"case_manifest.json"),"control_receipt_sha256":sha(control_path) if control_path.is_file() else None,"checker_receipt_sha256":sha(checker_path) if checker_path.is_file() else None,"benchmark_receipts_sha256":sha(receipt) if receipt.exists() else None},"cells":cells,"primary":{"regime":"n23_k16","M":512,"eligible":primary["eligible"],"median_at_most_0_90":primary["median_of_8_paired_ratios"]<=.90 if primary["eligible"] else None,"bootstrap_upper_below_one":primary["bootstrap_95"]["upper"]<1 if primary["eligible"] else None,"effect_predicate":bool(primary["eligible"] and primary["median_of_8_paired_ratios"]<=.90 and primary["bootstrap_95"]["upper"]<1)},"claim_boundary":"descriptive finite measurements only; controls, checker, or any missing/censored/nonfinite/nonpositive job prevent every effect classification"}
    (run/"analysis.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n");return out
if __name__=="__main__":
 import argparse
 p=argparse.ArgumentParser();p.add_argument("run",type=Path);a=p.parse_args();print(json.dumps(analyze(a.run),sort_keys=True))
