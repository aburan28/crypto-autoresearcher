#!/usr/bin/env python3
"""Single immutable scientific run. No automatic retry or overwrite."""
import contextlib,csv,hashlib,io,json,os,platform,resource,shlex,subprocess,sys,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import sympy
import direct_dual_numbers as direct
import coefficient_reference as reference
from symbolic_audit import certificates,LEMMA

ROOT=Path(__file__).resolve().parents[5]
TASK=Path(__file__).resolve().parents[1]
RUN=TASK/"runs"/"RUN-ECDLP-b7628e"
SPEC=ROOT/"experiments/EXP-ECDLP-a5f766/approved-contract-v2.yaml"
EXPECTED="a81b1476954d80d8042d697299f2522a6658431b17380f3ef423cb5403c6c79d"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()
def put(name,obj):
    p=RUN/name
    with p.open("x") as f:
        f.write(obj if isinstance(obj,str) else json.dumps(obj,indent=2,sort_keys=True)+"\n")
def table(name,rows,fields):
    with (RUN/name).open("x",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def preconditions(p,A,B,n):
    return {"characteristic":p>3,"A0_unit":A%p!=0,"n_invertible":n>1 and n%p!=0,
            "smooth":(4*A**3+27*B**2)%p!=0}

def main():
    # No scientific operation before authority and source provenance.
    if sha(SPEC)!=EXPECTED: raise RuntimeError("Frozen contract hash mismatch")
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((TASK/"source").glob("*.py"))}
    commit=git("rev-parse","HEAD")
    dirty=git("status","--porcelain")
    RUN.mkdir(parents=True,exist_ok=False)
    started=datetime.now(timezone.utc).isoformat()
    t0=time.monotonic();cpu0=time.process_time()
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    command=" ".join(shlex.quote(x) for x in sys.orig_argv)
    put("command.txt",command+"\n")
    put("inputs.json",{"primes":[7,11,13,17],"families":["C","V","G"],"u0":[1,2],
        "v":[0,1],"c":[1,2],"n":3,"truncation":1,"planned_rows":96,"randomness":None,
        "action_order":"active gauge, then entire-family pullback"})
    put("environment.json",{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),
        "sympy":sympy.__version__,"cwd":os.getcwd(),"worker_count":1,"memory_limit_bytes":2*1024**3,
        "model_provenance":{"runtime":"native Codex","requested_policy":"executor-implementation",
        "resolved_model_id":None,"model_verified":False,"fallback_used":False,
        "note":"Parent verified authenticated native ChatGPT login; exact model identifier unavailable to script."}})
    eligible=[];rows=[];rejects=[];certs={};stages={};anomalies=[]
    counters={k:0 for k in ("expansion_failures","gauge_failures","covariance_failures",
        "order_zero_failures","independent_arithmetic_failures","null_nonzero","flex_mismatches",
        "incidence_failures","sign_collision_failures","CG_collision_failures")}
    state="completed_valid";failure_class=None
    log=io.StringIO();err=io.StringIO()
    try:
      with contextlib.redirect_stdout(log),contextlib.redirect_stderr(err):
        start=time.monotonic()
        for p in (7,11,13,17):
            checks=preconditions(p,3,-11,3)
            if not all(checks.values()): raise ArithmeticError(f"Invalid fixture p={p}: {checks}")
            count=direct.point_count(p);trace=p+1-count;h=reference.hasse(p)
            ordinary=trace%p!=0;agree=ordinary==(h!=0)
            eligible.append(dict(p=p,point_count=count,trace=trace,hasse=h,
                ordinary=ordinary,agreement=agree,scope="ordinary" if ordinary else "auxiliary_nonordinary"))
            if not agree: raise ArithmeticError(f"Eligibility disagreement p={p}")
        fixtures=[("p3","characteristic",3,1,1,2),("A0zero","A0_unit",7,0,1,3),
                  ("n=p","n_invertible",7,3,-11,7),("singular","smooth",7,-3,2,3)]
        for name,predicate,p,A,B,n in fixtures:
            checks=preconditions(p,A,B,n)
            correct=not checks[predicate] and all(v for k,v in checks.items() if k!=predicate)
            rejects.append(dict(name=name,p=p,A=A,B=B,n=n,predicates=checks,correct_rejection=correct))
            if not correct: raise ArithmeticError(f"Rejection fixture invalid: {name}")
        stages["preconditions_and_eligibility"]=time.monotonic()-start
        print("Eligibility and four rejection controls complete.")
        start=time.monotonic();certs=certificates()
        stages["symbolic_certificates_and_scoped_lemma"]=time.monotonic()-start
        if any(c["status"]=="FAIL" for c in certs.values()):
            raise ArithmeticError("Nonzero symbolic residual")
        print("Six producer certificate groups recorded.")
        start=time.monotonic();cg={}
        for p in (7,11,13,17):
          for family in ("C","V","G"):
            for u0 in (1,2):
              for v in (0,1):
                for c in (1,2):
                  a=direct.calculate(p,family,u0,v,c)
                  b=reference.calculate(p,family,u0,v,c)
                  A0,A1=a["coords"][0];x0,x1=a["coords"][2]
                  F0,J=a["F"];expected=(-6*c)%p if family=="V" else 0
                  failures={
                    "expansion_failures":((A0*F0-x0*x0)%p!=0 or (A0*J+A1*F0-2*x0*x1)%p!=0),
                    "gauge_failures":a["before"]!=a["base"],
                    "covariance_failures":a["F"]!=[a["before"][0],c*a["before"][1]%p],
                    "order_zero_failures":F0!=x0*x0*pow(A0,-1,p)%p,
                    "independent_arithmetic_failures":a["F"]!=b["F"] or a["coords"]!=b["coords"],
                    "null_nonzero":family in ("C","G") and J!=0,
                    "flex_mismatches":family=="V" and J!=expected,
                    "incidence_failures":a["incidence"]!=[0,0],
                    "sign_collision_failures":a["F"]!=a["Fneg"],
                    "CG_collision_failures":False}
                  key=(p,u0,v,c)
                  if family=="C":cg[key]=a["F"]
                  if family=="G":failures["CG_collision_failures"]=a["F"]!=cg[key]
                  for k,bad in failures.items(): counters[k]+=int(bad)
                  rows.append(dict(p=p,family=family,u0=u0,v=v,c=c,
                    scope=next(x["scope"] for x in eligible if x["p"]==p),
                    coordinates=json.dumps(a["coords"]),negative_coordinates=json.dumps(a["negative_coords"]),
                    F0=F0,J=J,reference_F0=b["F"][0],reference_J=b["F"][1],
                    expected_J=expected,sign_collision=a["F"]==a["Fneg"],
                    CG_collision=(a["F"]==cg[key]) if family=="G" else "",
                    failures=json.dumps(failures,sort_keys=True)))
                  if any(failures.values()):raise ArithmeticError(f"First row discrepancy: {rows[-1]}")
        stages["finite_controls"]=time.monotonic()-start
        print(f"Finite controls recorded: {len(rows)} of 96 rows.")
    except BaseException as ex:
        if isinstance(ex,MemoryError):
            state="resource_exhaustion";failure_class="resource_exhaustion"
        elif isinstance(ex,(OSError,KeyboardInterrupt)):
            state="failed_infrastructure";failure_class="infrastructure_error"
        elif isinstance(ex,ArithmeticError):
            state="completed_invalid";failure_class="invalid_measurement"
        else:
            state="failed_implementation";failure_class="implementation_error"
        anomalies.append({"type":type(ex).__name__,"message":str(ex),"classification":failure_class})
        traceback.print_exc(file=err)
    start=time.monotonic()
    put("symbolic-certificates.json",certs)
    put("lemma-proof.md",LEMMA)
    table("eligibility.csv",eligible,["p","point_count","trace","hasse","ordinary","agreement","scope"])
    fields=["p","family","u0","v","c","scope","coordinates","negative_coordinates",
            "F0","J","reference_F0","reference_J","expected_J","sign_collision","CG_collision","failures"]
    table("finite-controls.csv",rows,fields)
    put("rejection-controls.json",rejects)
    metrics={"planned_rows":96,"executed_rows":len(rows),"failure_counts":counters,
      "certificate_status":{k:v["status"] for k,v in certs.items()},
      "nonzero_symbolic_residual_count":sum(r!="0" for v in certs.values() for r in v.get("residuals",[])),
      "ordinary_eligible_prime_count":sum(x["ordinary"] for x in eligible),
      "correct_rejection_count":sum(x["correct_rejection"] for x in rejects),
      "eligibility_agreements":sum(x["agreement"] for x in eligible)}
    gate_checks={"96_rows":len(rows)==96,
        "six_producer_certificates_PASS":len(certs)==6 and all(v["status"]=="PASS" for v in certs.values()),
        "all_failure_counters_zero":all(v==0 for v in counters.values()),
        "zero_symbolic_residuals":metrics["nonzero_symbolic_residual_count"]==0,
        "ordinary_fixture_present":metrics["ordinary_eligible_prime_count"]>=1,
        "four_eligibility_agreements":metrics["eligibility_agreements"]==4,
        "four_correct_rejections":metrics["correct_rejection_count"]==4}
    metrics["completion_gate_checks"]=gate_checks
    metrics["completion_gate_passed"]=state=="completed_valid" and all(gate_checks.values())
    inconclusive_reasons=[k for k,v in gate_checks.items() if not v]
    metrics["inconclusive_reasons"]=inconclusive_reasons
    metrics["certificate_methods"]={"machine_checked_symbolic_groups":5,
        "producer_supplied_scoped_proofs":1,"independent_proof_review_completed":False}
    put("raw-result.json",{"state":state,"completion_gate_passed":metrics["completion_gate_passed"],
                         "inconclusive_reasons":inconclusive_reasons,
                         "rows":rows,"eligibility":eligible,"rejections":rejects,
                         "certificates":certs,"anomalies":anomalies})
    put("metrics.json",metrics)
    report=f"""# Execution report

Experiment EXP-ECDLP-a5f766; task TASK-20260906-b7628e; run RUN-ECDLP-b7628e.
Terminal state: {state}. Failure classification: {failure_class}.
Predeclared completion gate passed: {metrics['completion_gate_passed']}.
Missing obligations/inconclusive reasons: {json.dumps(inconclusive_reasons)}.
Executed {len(rows)} of 96 frozen rows. Ordinary eligible primes:
{metrics['ordinary_eligible_prime_count']}/4. Correct input rejections:
{metrics['correct_rejection_count']}/4.

Exact observations and comparisons are in metrics.json and finite-controls.csv.
The symbolic certificate statuses are producer submissions; lemma-proof.md
requires independent review. No hypothesis status or ECDLP claim is made.
Evidence scope is equal-characteristic first-order algebra and the four fixed
small fields; nonordinary rows are auxiliary. No statistical inference,
canonical-lift construction, or mixed-characteristic transfer is asserted.

Protocol deviations: none in scientific parameters. The committed research
budget policy makes historical time/CPU stage estimates advisory.
Anomalies: {json.dumps(anomalies)}.
Source commit: {commit}; dirty tree: {bool(dirty)}. The manifest binds exact
source bytes; later Coordinator snapshot is needed for durable publication.
One execution, no retry. Independent validation and Coordinator interpretation
remain pending.
"""
    put("execution-report.md",report)
    put("stdout.log",log.getvalue());put("stderr.log",err.getvalue())
    stages["immutable_artifact_production_before_manifest"]=time.monotonic()-start
    usage=resource.getrusage(resource.RUSAGE_SELF)
    rss=usage.ru_maxrss if sys.platform=="darwin" else usage.ru_maxrss*1024
    artifact_hashes={p.name:sha(p) for p in sorted(RUN.iterdir()) if p.is_file()}
    manifest={"experiment_id":"EXP-ECDLP-a5f766","task_id":"TASK-20260906-b7628e",
      "run_id":"RUN-ECDLP-b7628e","status":state,"valid":state=="completed_valid",
      "validity_reason":"Arithmetic measurements complete; consult completion_gate_passed separately; producer proof pending independent review" if state=="completed_valid" else str(anomalies),
      "completion_gate_passed":metrics["completion_gate_passed"],"inconclusive_reasons":inconclusive_reasons,
      "failure_class":failure_class,"started_at":started,"finished_at":datetime.now(timezone.utc).isoformat(),
      "implementation_commit":commit,"dirty_tree":bool(dirty),"git_status_porcelain":dirty,
      "approved_contract":str(SPEC.relative_to(ROOT)),"approved_contract_sha256":EXPECTED,
      "source_sha256":source_hashes,"artifact_sha256":artifact_hashes,
      "command":command,"cwd":os.getcwd(),"randomness":None,"attempt":1,
      "wall_seconds_before_manifest":time.monotonic()-t0,"cpu_seconds_before_manifest":time.process_time()-cpu0,
      "peak_rss_bytes":rss,"stage_wall_seconds":stages,
      "protocol_deviations":[],"anomalies":anomalies,
      "cost_scope":"Measured process costs after provenance/preflight through artifact production, excluding final manifest write",
      "model_provenance_reference":"environment.json","self_hash_note":"manifest excludes itself to avoid self-reference"}
    put("manifest.json",manifest)
    print(json.dumps({"state":state,"rows":len(rows),"metrics":metrics,"run_path":str(RUN)},sort_keys=True))
    return 0 if state=="completed_valid" else 1

if __name__=="__main__":
    sys.exit(main())
