#!/usr/bin/env python3
"""Frozen-process runner for RUN-KIC-e3dbed.

Only `--phase conformance` is usable until the Coordinator commits
measurement_admission.json.  Scientific execution is deliberately refused here.
"""
import argparse, hashlib, json, os, platform, resource, shutil, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PKG = ROOT.parents[1]
PROTO = PKG / "protocol.json"
OUT = ROOT / "conformance" / "attempt2"
DIRECT_FIELDS = ["base_fingerprint", "accepted_relation_digest", "terminal_rank", "recovered_scalar", "group_equation_verification", "result_digest"]

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def seed(label): return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "little")

def clean_env(direct):
    keep={k:os.environ[k] for k in ("PATH","HOME","TMPDIR","SYSTEMROOT") if k in os.environ}
    keep["RAYON_NUM_THREADS"]="1"
    if direct:
        keep.update({"KIC_INCREMENTAL_RANK_CROSSCHECK":"0","KIC_RANK_SURPLUS":"0","KIC_RANK_AWARE_PAIR_SCAN":"1","KIC_PARALLEL_SUPPORT_EXPANSION":"0","KIC_PIPELINED_SUPPORT_EXPANSION":"0"})
    return keep

def json_value(text):
    vals=[]
    dec=json.JSONDecoder()
    for i,c in enumerate(text):
        if c not in "[{": continue
        try:
            v,n=dec.raw_decode(text[i:]); vals.append(v)
        except json.JSONDecodeError: pass
    if not vals: raise ValueError("stdout did not contain a JSON object")
    return vals[-1]

def run(case):
    OUT.mkdir(parents=True,exist_ok=True)
    work=OUT / (case["id"] + ".cwd")
    if work.exists(): raise RuntimeError("immutable conformance directory already exists")
    work.mkdir()
    stdout=OUT/(case["id"]+".stdout"); stderr=OUT/(case["id"]+".stderr")
    binary=Path(case["binary"])
    before=resource.getrusage(resource.RUSAGE_CHILDREN); start=time.monotonic_ns()
    with stdout.open("wb") as so, stderr.open("wb") as se:
        p=subprocess.Popen([str(binary),*map(str,case["argv"])],cwd=work,env=clean_env(case["direct"]),stdout=so,stderr=se)
        try: pid,status,usage=os.wait4(p.pid,0)
        except AttributeError: raise RuntimeError("os.wait4 is required for per-child CPU/RSS")
    wall=time.monotonic_ns()-start
    exit_code=os.waitstatus_to_exitcode(status)
    text=stdout.read_text(errors="replace")
    receipt={"id":case["id"],"phase":"untimed_conformance","argv":[str(binary),*map(str,case["argv"])],"cwd":str(work),"environment":clean_env(case["direct"]),"exit_code":exit_code,"stdout_sha256":digest(stdout),"stderr_sha256":digest(stderr),"output":None,"correct":False,"timing_not_retained":True,"resource_collection":{"method":"os.wait4","darwin_ru_maxrss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent"},"resource_fields_present":True}
    # Do not record conformance wall/CPU/RSS values. They are intentionally discarded.
    if exit_code==0:
        val=json_value(text); receipt["output"]=val
        receipt["correct"]=bool(val.get("recovered_scalar")==17 and val.get("group_equation_verification") is True)
        if case["direct"]:
            receipt["thread_check"]={"query_parallel_threads":val.get("query_parallel_threads"),"parallel_support_expansion_threads":val.get("parallel_support_expansion_threads")}
            receipt["correct"] &= receipt["thread_check"]=={"query_parallel_threads":1,"parallel_support_expansion_threads":0}
    (OUT/(case["id"]+".json")).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

def conformance():
    b=PKG/"build_preparation/target/release/examples"
    c=ROOT/"candidate_target/release/examples"
    cases=[
      {"id":"baseline_ic","binary":b/"koblitz_rank_fixture","argv":[13,0,1,2,13001,"signed_expanded","independent","pair_pair_parallel_4096",1,17],"direct":True},
      {"id":"allocation_ic","binary":c/"koblitz_rank_fixture","argv":[13,0,1,2,13001,"signed_expanded","independent","pair_pair_parallel_4096",1,17],"direct":True},
      {"id":"rho","binary":b/"koblitz_rho_fixture","argv":[13,0,"signed_frobenius",1,"packed",13001,17],"direct":False},]
    rs=[run(x) for x in cases]
    if not all(x["correct"] for x in rs): raise RuntimeError("conformance correctness failed")
    a,bv=rs[0]["output"],rs[1]["output"]
    mismatch={k:[a.get(k),bv.get(k)] for k in DIRECT_FIELDS if a.get(k)!=bv.get(k)}
    if mismatch: raise RuntimeError("allocation semantic mismatch: "+json.dumps(mismatch,sort_keys=True))
    (OUT/"conformance_summary.json").write_text(json.dumps({"children":3,"correct":True,"comparison_fields":DIRECT_FIELDS,"timing_not_retained":True,"receipt_files":[x["id"]+".json" for x in rs]},indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--phase",choices=("conformance","scientific"),required=True); a=p.parse_args()
    if a.phase=="scientific":
        admission=PKG/"measurement_admission.json"
        raise SystemExit("REFUSED: scientific children require committed measurement_admission.json; run only after Coordinator admission")
    conformance()
if __name__=="__main__": main()
