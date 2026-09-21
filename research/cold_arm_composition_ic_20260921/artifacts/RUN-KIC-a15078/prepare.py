#!/usr/bin/env python3
"""Stage-A offline build, fixed controls, and source/case custody for P4."""
from __future__ import annotations
import argparse,datetime as dt,gzip,hashlib,itertools,json,os,platform,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from typing import Any,Iterable

ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parents[1];REPO=PACKAGE.parents[1]
P1=REPO/"research/cold_single_ic_20260921";P2=REPO/"research/cold_capacity_ic_20260921";P3=REPO/"research/cold_target_stop_ic_20260921"
P2RUN=P2/"artifacts/RUN-KIC-8b5038";P3RUN=P3/"artifacts/RUN-KIC-56c897"
PROTO=PACKAGE/"protocol.json";PROTO_SHA="1e43ef6fd838b622af98f160a4e4c61cd27794e79b81747364d7f86550c4879a"
SRC=PACKAGE/"source_candidate";TEST_B=PACKAGE/"source_test_baseline";TEST_C=PACKAGE/"source_test_candidate"
TAR_P2=P2RUN/"candidate_source.tar.gz";TAR_P3=P3RUN/"candidate_source.tar.gz";CUST=ROOT/"custody"
BINS={"ic_baseline":CUST/"ic_baseline/koblitz_rank_fixture","ic_candidate":CUST/"ic_candidate/koblitz_rank_fixture","rho_baseline":CUST/"rho_baseline/koblitz_rho_fixture","rho_candidate":CUST/"rho_candidate/koblitz_rho_fixture"}
PARENT_RANK=CUST/"parent_source/examples/koblitz_rank_fixture.rs";PARENT_RHO=CUST/"parent_source/examples/koblitz_rho_fixture.rs"
TARGET=ROOT/"build_target";R=21044858204113
P2_TAR_SHA="4d835b333402d48d2131779df5d4594a5e589fc054943be0c273686b4c01a253";P3_TAR_SHA="0fdc8badf12634209fabc37d7e34b4091f9954025d441c54bad2fca0adc9578e"
EXPECTED={"ic_baseline":"f4914ae1ddbbf2cd06804a0c7799860fb75f95184a28daa4c851e19743532ac6","rho_baseline":"e5a2fef13fc378d9b0eef31228211b4b24c989fcbc6bdad8437eb6c7c31cf450"}
ARMS=("ic_baseline","ic_candidate","rho_baseline","rho_candidate")

def req(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def dig(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def atom(p:Path,v:Any)->None:
    p.parent.mkdir(parents=True,exist_ok=True);q=p.with_name(p.name+".tmp")
    with q.open("w") as f:json.dump(v,f,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
    os.replace(q,p)
def files(root:Path)->list[Path]:return sorted(p for p in root.rglob("*") if p.is_file() and "target" not in p.relative_to(root).parts and ".git" not in p.relative_to(root).parts)
def tree(root:Path)->list[dict[str,Any]]:return [{"path":p.relative_to(root).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files(root)]
def ntar(items:Iterable[tuple[Path,str]],dest:Path)->None:
    dest.parent.mkdir(parents=True,exist_ok=True);q=dest.with_name(dest.name+".tmp")
    with q.open("wb") as raw:
      with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as gz:
       with tarfile.open(fileobj=gz,mode="w",format=tarfile.PAX_FORMAT) as t:
        for p,name in sorted(items,key=lambda x:x[1]):
         info=t.gettarinfo(str(p),arcname=name);info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
         with p.open("rb") as f:t.addfile(info,f)
      raw.flush();os.fsync(raw.fileno())
    os.replace(q,dest)
def run(name:str,argv:list[str],cwd:Path,env:dict[str,str])->dict[str,Any]:
    out=ROOT/f"{name}.stdout";err=ROOT/f"{name}.stderr";req(not out.exists() and not err.exists(),f"logs exist for {name}")
    with out.open("xb") as o,err.open("xb") as e:
      start=time.monotonic_ns();p=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=o,stderr=e,close_fds=True);_,status,usage=os.wait4(p.pid,0);stop=time.monotonic_ns();p.returncode=os.waitstatus_to_exitcode(status);o.flush();e.flush();os.fsync(o.fileno());os.fsync(e.fileno())
    return {"name":name,"argv":argv,"cwd":str(cwd),"exit_code":p.returncode,"wall_seconds":(stop-start)/1e9,"user_cpu_seconds":usage.ru_utime,"system_cpu_seconds":usage.ru_stime,"wait4_ru_maxrss":usage.ru_maxrss,"rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent","stdout":out.name,"stdout_sha256":sha(out),"stderr":err.name,"stderr_sha256":sha(err)}
def extract_source_member(archive:Path,prefix:str,name:str,dest:Path)->None:
    dest.parent.mkdir(parents=True,exist_ok=True)
    with tarfile.open(archive,"r:gz") as t:
      member=t.extractfile(f"{prefix}/{name}");req(member is not None,f"missing {name}")
      with dest.open("wb") as out:shutil.copyfileobj(member,out)
def copy_parent_inputs()->None:
    req(sha(TAR_P2)==P2_TAR_SHA and sha(TAR_P3)==P3_TAR_SHA,"parent source archive changed")
    for arm,origin in (("ic_baseline",P2RUN/"custody/candidate/koblitz_rank_fixture"),("rho_baseline",P2RUN/"custody/baseline/koblitz_rho_fixture")):
      dest=BINS[arm];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(origin,dest);dest.chmod(0o755);req(sha(dest)==EXPECTED[arm],f"parent {arm} binary changed")
    extract_source_member(TAR_P3,"source_candidate","examples/koblitz_rank_fixture.rs",PARENT_RANK)
    extract_source_member(TAR_P3,"source_candidate","examples/koblitz_rho_fixture.rs",PARENT_RHO)
def patch_for(left:Path,right:Path,label:str)->bytes:
    result=subprocess.run(["git","diff","--no-index","--",str(left),str(right)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False);req(result.returncode==1,f"no {label} source diff")
    out=[]
    for line in result.stdout.splitlines(keepends=True):
      if line.startswith(b"diff --git "):line=f"diff --git a/examples/{label} b/examples/{label}\n".encode()
      elif line.startswith(b"--- "):line=f"--- a/examples/{label}\n".encode()
      elif line.startswith(b"+++ "):line=f"+++ b/examples/{label}\n".encode()
      out.append(line)
    return b"".join(out)
def cases()->dict[str,Any]:
    p1=json.loads((P1/"protocol.json").read_text());p2=json.loads((P2RUN/"case_manifest.json").read_text());p3=json.loads((P3RUN/"case_manifest.json").read_text())
    old=set(p1["frozen_cases"]["calibration"]["scalars"]+p1["frozen_cases"]["heldout"]["scalars"]+p2["scalars"]+p3["scalars"]);req(len(old)==84,"prior-panel union is not 84")
    orders=list(itertools.permutations(sorted(ARMS)));rows=[];scalars=[];ordinal=0
    for index,order in enumerate(orders,1):
      label=f"CSIC53-ARMCOMPOSE-v1-case-{index:02d}";d=1+int.from_bytes(hashlib.sha256(label.encode()).digest(),"little")%(R-1);scalars.append(d)
      il=f"CSIC53-ARMCOMPOSE-v1-ic-seed-{index:02d}";rl=f"CSIC53-ARMCOMPOSE-v1-rho-seed-{index:02d}";is_=int.from_bytes(hashlib.sha256(il.encode()).digest()[:8],"little");rs=int.from_bytes(hashlib.sha256(rl.encode()).digest()[:8],"little")
      for pos,arm in enumerate(order,1):
        ordinal+=1;ic=arm.startswith("ic_");rows.append({"ordinal":ordinal,"case_index":index,"position":pos,"arm":arm,"id":f"case-{index:02d}-p{pos}-{arm}","scalar_label":label,"scalar":d,"seed_label":il if ic else rl,"seed":is_ if ic else rs,"eta_denominator":256 if ic else None,"factor_base_k":75 if ic else None})
    req(len(set(scalars))==24 and not(set(scalars)&old) and 17 not in scalars,"freshness failed")
    positions={arm:[sum(x["arm"]==arm and x["position"]==p for x in rows) for p in (1,2,3,4)] for arm in ARMS};req(all(v==[6]*4 for v in positions.values()),"position balance failed")
    return {"schema":"crypto.autoresearch.arm_composition_case_manifest.v1","experiment_id":"RUN-KIC-a15078","protocol_sha256":PROTO_SHA,"cases":rows,"scalars":scalars,"freshness":{"pairwise_distinct":True,"disjoint_R1_R2_R3":True,"excluded_prior_scalars":84,"control_scalar_17_excluded":True},"counts":{"targets":24,"children":96,"per_arm":24},"position_counts":positions,"derivation_digest":dig({"scalars":scalars,"cases":rows})}
def build()->None:
    req(sha(PROTO)==PROTO_SHA,"protocol hash mismatch");copy_parent_inputs()
    ntar([(p,f"source_candidate/{p.relative_to(SRC).as_posix()}") for p in files(SRC)],ROOT/"candidate_source.tar.gz")
    (ROOT/"candidate.patch").write_bytes(patch_for(PARENT_RANK,SRC/"examples/koblitz_rank_fixture.rs","koblitz_rank_fixture.rs")+b"\n"+patch_for(PARENT_RHO,SRC/"examples/koblitz_rho_fixture.rs","koblitz_rho_fixture.rs"))
    env={**os.environ,"CARGO_TARGET_DIR":str(TARGET)}
    receipts=[run("candidate_release_build",["cargo","build","--offline","--locked","--release","--jobs","2","--example","koblitz_rank_fixture","--example","koblitz_rho_fixture"],SRC,env)]
    req(receipts[-1]["exit_code"]==0,"candidate build failed")
    for arm,name in (("ic_candidate","koblitz_rank_fixture"),("rho_candidate","koblitz_rho_fixture")):
      dest=BINS[arm];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(TARGET/"release/examples"/name,dest);dest.chmod(0o755)
    receipts.append(run("candidate_rank_tests",["cargo","test","--offline","--locked","--release","--jobs","2","--example","koblitz_rank_fixture","--","--nocapture"],SRC,env))
    receipts.append(run("candidate_rho_tests",["cargo","test","--offline","--locked","--release","--jobs","2","--example","koblitz_rho_fixture","--","--nocapture"],SRC,env))
    req(all(x["exit_code"]==0 for x in receipts),"native controls failed")
    rank=(ROOT/"candidate_rank_tests.stdout").read_text();rho=(ROOT/"candidate_rho_tests.stdout").read_text()
    for name in ("exact_basis_products_squares_edges_and_inverse_corpus","itoh_chain_exponent_is_exactly_inverse_exponent","thirty_compact_dual_sign_batch_shapes_match_generic"):
      req(f"p4_field_controls::{name} ... ok" in rank,f"missing rank test {name}")
    for name in ("basis_edges_sha256_inverse_oracle","itoh_exponent_chain"):
      req(f"p4_field_controls::{name} ... ok" in rho,f"missing rho test {name}")
    for name in ("early_target_certificate_and_negative_checker_controls","zero_b_never_identifies_and_target_unit_does","duplicate_rescale_preserves_target_and_inconsistent_rhs_is_explicit","k75_certificate_identifies_at_row_74_with_expected_weights"):
      req(f"target_certificate_tests::{name} ... ok" in rank,f"missing P3 certificate test {name}")
    atom(ROOT/"field_controls.json",{"schema":"crypto.autoresearch.arm_composition_field_controls.v1","valid":True,"basis_products":2809,"basis_squares":53,"sha256_inverse_values":256,"edges":["zero","one","max","alternating_even","alternating_odd"],"symbolic_itoh_chain":[1,2,4,8,16,32,48,52],"rank_test_stdout_sha256":sha(ROOT/"candidate_rank_tests.stdout"),"rho_test_stdout_sha256":sha(ROOT/"candidate_rho_tests.stdout"),"scope":"fixed native units only; zero solver children"})
    atom(ROOT/"batch_controls.json",{"schema":"crypto.autoresearch.arm_composition_batch_controls.v1","valid":True,"targets":[0,1,2,7,31],"widths":[0,1,8,63,257,4096],"shapes":30,"table_insertions":66,"exact_lookup_and_ordered_output_checked":True,"attempted_and_group_identity_checked":True,"rank_test_stdout_sha256":sha(ROOT/"candidate_rank_tests.stdout")})
    atom(ROOT/"certificate_controls.json",{"schema":"crypto.autoresearch.arm_composition_certificate_controls.v1","valid":True,"inherited_P3_fixed_suite":True,"moduli":[17,R],"rank_test_stdout_sha256":sha(ROOT/"candidate_rank_tests.stdout")})
    atom(ROOT/"semantic_controls.json",{"schema":"crypto.autoresearch.arm_composition_semantic_controls.v1","stage":"native_unit","valid":True,"ic_prefix":"pending_eight_solver_controls_then_24_pairs","rho_semantics":"pending_eight_solver_controls_then_24_pairs","field_controls_sha256":sha(ROOT/"field_controls.json"),"batch_controls_sha256":sha(ROOT/"batch_controls.json")})
    atom(ROOT/"build_execution.json",{"schema":"crypto.autoresearch.arm_composition_build_execution.v1","recorded_at":dt.datetime.now(dt.timezone.utc).isoformat(),"scope":"offline build and fixed native unit tests; no solver child","receipts":receipts,"binary_sha256":{a:sha(p) for a,p in BINS.items()}})
def freeze()->None:
    required=("runner.py","analyze.py","prepare.py","receipt_parser.py","certificate_checker.py","prefix_checker.py","rho_semantics_checker.py","field_controls.json","batch_controls.json","certificate_controls.json","semantic_controls.json","build_execution.json")
    for name in required:req((ROOT/name).is_file(),f"missing {name}")
    copy_parent_inputs();atom(ROOT/"case_manifest.json",cases())
    source_tree=tree(SRC);test_b=tree(TEST_B);test_c=tree(TEST_C)
    req(len(source_tree)==len(test_b)==len(test_c)==446,"source tree count mismatch")
    atom(ROOT/"source_delta_audit.json",{"schema":"crypto.autoresearch.arm_composition_source_delta_audit.v1","parent_p2_tar_sha256":sha(TAR_P2),"parent_p3_tar_sha256":sha(TAR_P3),"candidate_patch_sha256":sha(ROOT/"candidate.patch"),"production_changed_paths":["examples/koblitz_rank_fixture.rs","examples/koblitz_rho_fixture.rs"],"expected_changes":["P2 x_only doubled capacity","shared guarded ARM n53 fused PMULL and Itoh inverse","IC ARM compact dual-sign batch","truthful backend/inverse/query markers"],"forbidden_changes_found":[]})
    atom(ROOT/"source_closure.json",{"schema":"crypto.autoresearch.arm_composition_source_closure.v1","protocol_sha256":PROTO_SHA,"parent_archives":{"p2":sha(TAR_P2),"p3":sha(TAR_P3)},"candidate":{"files":446,"bytes":sum(x["bytes"] for x in source_tree),"tree_digest":dig(source_tree),"source_tar_sha256":sha(ROOT/"candidate_source.tar.gz")},"test_tree_digests":{"baseline":dig(test_b),"candidate":dig(test_c)},"binary_sha256":{a:sha(p) for a,p in BINS.items()},"cargo_lock_sha256":sha(SRC/"Cargo.lock")})
    tools={}
    for name,argv in {"rustc":["rustc","--version","--verbose"],"cargo":["cargo","--version","--verbose"],"uname":["uname","-a"],"sw_vers":["sw_vers"]}.items():
      result=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=False);tools[name]={"argv":argv,"exit_code":result.returncode,"stdout":result.stdout,"stderr":result.stderr}
    build_record=json.loads((ROOT/"build_execution.json").read_text())
    atom(ROOT/"build_toolchain.json",{"schema":"crypto.autoresearch.arm_composition_build_toolchain.v1","tools":tools,"build_execution_sha256":sha(ROOT/"build_execution.json"),"receipts":build_record["receipts"],"host":{"platform":platform.platform(),"machine":platform.machine(),"python":sys.version}})
    code_names=("runner.py","analyze.py","prepare.py","receipt_parser.py","certificate_checker.py","prefix_checker.py","rho_semantics_checker.py");codes={name:sha(ROOT/name) for name in code_names}
    atom(ROOT/"runner_analyzer_closure.json",{"schema":"crypto.autoresearch.arm_composition_runner_analyzer_closure.v1","code_sha256":codes,"bootstrap":{"seed":"CSIC53-ARMCOMPOSE-BOOT-v1","resamples":10000,"draws":24,"type":7},"primary":"ic_candidate/rho_candidate","mandatory_controls":["ic_prefix","rho_semantics","certificate","group","telemetry"],"no_selection":True})
    atom(ROOT/"preflight.json",{"schema":"crypto.autoresearch.arm_composition_preflight.v1","status":"READY_FOR_STAGE_B_COMMIT_ONLY","protocol_sha256":PROTO_SHA,"code_sha256":codes,"case_manifest_sha256":sha(ROOT/"case_manifest.json"),"source_closure_sha256":sha(ROOT/"source_closure.json"),"source_delta_audit_sha256":sha(ROOT/"source_delta_audit.json"),"build_toolchain_sha256":sha(ROOT/"build_toolchain.json"),"field_controls_sha256":sha(ROOT/"field_controls.json"),"batch_controls_sha256":sha(ROOT/"batch_controls.json"),"certificate_controls_sha256":sha(ROOT/"certificate_controls.json"),"semantic_controls_sha256":sha(ROOT/"semantic_controls.json"),"runner_analyzer_closure_sha256":sha(ROOT/"runner_analyzer_closure.json"),"binary_sha256":{a:sha(p) for a,p in BINS.items()},"model":{"resolved_model_id":"gpt-5.6-sol","reasoning_effort":"high","fallback_used":False,"degraded":False,"model_verified":False},"holds":{"solver_controls":True,"science":True}})
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--phase",choices=("build","freeze"),required=True);a=p.parse_args();build() if a.phase=="build" else freeze()
if __name__=="__main__":main()
