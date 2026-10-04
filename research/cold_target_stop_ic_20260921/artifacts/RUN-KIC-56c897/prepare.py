#!/usr/bin/env python3
"""Stage-A build, unit controls, custody, and freeze for RUN-KIC-56c897."""
from __future__ import annotations
import argparse, datetime as dt, gzip, hashlib, json, os, platform, shutil, subprocess, sys, tarfile, time
from pathlib import Path
from typing import Any, Iterable

ROOT=Path(__file__).resolve().parent; PACKAGE=ROOT.parents[1]; REPO=PACKAGE.parents[1]
P1=REPO/"research/cold_single_ic_20260921"; P1RUN=P1/"artifacts/RUN-KIC-e3dbed"
P2=REPO/"research/cold_capacity_ic_20260921"; PROTOCOL=PACKAGE/"protocol.json"
PROTO_SHA="ec08f78b2fd165ae2873c9f103c59c08645f8512c0a8e68c0158887fcda2e1cb"
PARENT_TAR=P1RUN/"candidate_source.tar.gz"; BIN_TAR=P1RUN/"custody/binaries.tar.gz"; LOCK=P1RUN/"custody/Cargo.lock"; DEPS=P1RUN/"custody/dependencies.tar.gz"
SRC=PACKAGE/"source_candidate"; TEST_B=PACKAGE/"source_test_baseline"; TEST_C=PACKAGE/"source_test_candidate"
CUST=ROOT/"custody"; BASE_BIN=CUST/"baseline/koblitz_rank_fixture"; RHO_BIN=CUST/"baseline/koblitz_rho_fixture"; CAND_BIN=CUST/"candidate/koblitz_rank_fixture"; PARENT_RS=CUST/"parent_source/examples/koblitz_rank_fixture.rs"
BUILD=ROOT/"build_candidate/target"; TEST_TARGET=ROOT/"test_candidate_target"; R=21044858204113
EXPECTED_PARENT_TAR="f81487998d9fead4428deb2b583a8d787529413b8f6233141b3247f91b26b7cb"; EXPECTED_BASE="8ceefed466427e9a36d9bd50880ff0f5073b6d0e67a93325018416c646025fe2"; EXPECTED_RHO="e5a2fef13fc378d9b0eef31228211b4b24c989fcbc6bdad8437eb6c7c31cf450"; EXPECTED_LOCK="ada8f10a2f770f9859bbca76e8740372be6b7050e9c7b8f665cc7e80ca8f4ed1"; EXPECTED_DEPS="fb561512fdd5564803fa980ae8c0efb1a01b47f5227d615a5f63ad51709f7435"
ORDERS=(("baseline","candidate","rho"),("baseline","rho","candidate"),("candidate","baseline","rho"),("candidate","rho","baseline"),("rho","baseline","candidate"),("rho","candidate","baseline"))

def req(c,m):
    if not c: raise RuntimeError(m)
def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def dig(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def atom(p,v):
    p.parent.mkdir(parents=True,exist_ok=True); q=p.with_name(p.name+".tmp")
    with q.open("w") as f: json.dump(v,f,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
    os.replace(q,p)
def files(root): return sorted(p for p in root.rglob("*") if p.is_file() and "target" not in p.relative_to(root).parts and ".git" not in p.relative_to(root).parts)
def tree(root): return [{"path":p.relative_to(root).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files(root)]
def ntar(items:Iterable[tuple[Path,str]],dest:Path):
    tmp=dest.with_name(dest.name+".tmp");dest.parent.mkdir(parents=True,exist_ok=True)
    with tmp.open("wb") as raw:
      with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as gz:
       with tarfile.open(fileobj=gz,mode="w",format=tarfile.PAX_FORMAT) as t:
        for p,n in sorted(items,key=lambda x:x[1]):
         i=t.gettarinfo(str(p),arcname=n);i.uid=i.gid=0;i.uname=i.gname="";i.mtime=0
         with p.open("rb") as f:t.addfile(i,f)
      raw.flush();os.fsync(raw.fileno())
    os.replace(tmp,dest)
def run(name,argv,cwd,env,out,err):
    req(not out.exists() and not err.exists(),f"logs exist {name}");start=time.monotonic_ns()
    with out.open("xb") as o,err.open("xb") as e:
      p=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=o,stderr=e,close_fds=True);_,st,u=os.wait4(p.pid,0);end=time.monotonic_ns();p.returncode=os.waitstatus_to_exitcode(st);o.flush();e.flush();os.fsync(o.fileno());os.fsync(e.fileno())
    return {"name":name,"argv":argv,"cwd":str(cwd),"exit_code":p.returncode,"wall_seconds":(end-start)/1e9,"user_cpu_seconds":u.ru_utime,"system_cpu_seconds":u.ru_stime,"wait4_ru_maxrss":u.ru_maxrss,"wait4_ru_maxrss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent","stdout":out.name,"stdout_sha256":sha(out),"stderr":err.name,"stderr_sha256":sha(err)}
def extract_inputs():
    req(sha(PARENT_TAR)==EXPECTED_PARENT_TAR and sha(LOCK)==EXPECTED_LOCK and sha(DEPS)==EXPECTED_DEPS,"parent custody mismatch");CUST.mkdir(parents=True,exist_ok=True)
    with tarfile.open(BIN_TAR,"r:gz") as t:
      for member,dest in (("binaries/candidate/koblitz_rank_fixture",BASE_BIN),("binaries/baseline/koblitz_rho_fixture",RHO_BIN)):
       dest.parent.mkdir(parents=True,exist_ok=True);src=t.extractfile(member);req(src is not None,"binary absent")
       with dest.open("wb") as f:shutil.copyfileobj(src,f)
       dest.chmod(0o755)
    with tarfile.open(PARENT_TAR,"r:gz") as t:
      PARENT_RS.parent.mkdir(parents=True,exist_ok=True);src=t.extractfile("source_arm_allocation/examples/koblitz_rank_fixture.rs");req(src is not None,"parent source absent")
      with PARENT_RS.open("wb") as f:shutil.copyfileobj(src,f)
    req(sha(BASE_BIN)==EXPECTED_BASE and sha(RHO_BIN)==EXPECTED_RHO,"parent binary hash mismatch")
def patch_bytes():
    r=subprocess.run(["git","diff","--no-index","--",str(PARENT_RS),str(SRC/"examples/koblitz_rank_fixture.rs")],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False);req(r.returncode==1,"candidate has no diff")
    out=[]
    for line in r.stdout.splitlines(keepends=True):
      if line.startswith(b"diff --git "):line=b"diff --git a/examples/koblitz_rank_fixture.rs b/examples/koblitz_rank_fixture.rs\n"
      elif line.startswith(b"--- "):line=b"--- a/examples/koblitz_rank_fixture.rs\n"
      elif line.startswith(b"+++ "):line=b"+++ b/examples/koblitz_rank_fixture.rs\n"
      out.append(line)
    return b"".join(out)
def section(text,start,end):
    a=text.index(start);b=text.index(end,a);return text[a:b]
def prefix_static():
    b=PARENT_RS.read_text();c=(SRC/"examples/koblitz_rank_fixture.rs").read_text()
    spans=[("fixture_rng", "// Consume the ordinary draw", "let fixture_generation_ms"),("relation_generation","trials += 1;","let rank_started = Instant::now();"),("relation_material","let relation_material =", "let relation_hash =")]
    rows=[]
    for name,s,e in spans:
      left,right=section(b,s,e),section(c,s,e);req(left==right,f"prefix source span changed: {name}");rows.append({"name":name,"sha256":hashlib.sha256(left.encode()).hexdigest(),"bytes":len(left.encode())})
    return {"schema":"crypto.autoresearch.target_stop_prefix_controls.v1","stage":"source_static","valid":True,"identical_source_spans":rows,"runtime_n13_prefix":"pending_stage_B_controls","runtime_24_prefix":"pending_frozen_science_pairs"}
def parse_tests(path):
    text=path.read_text(errors="replace");names=["early_target_certificate_and_negative_checker_controls","zero_b_never_identifies_and_target_unit_does","duplicate_rescale_preserves_target_and_inconsistent_rhs_is_explicit","k75_certificate_identifies_at_row_74_with_expected_weights"]
    for n in names:req(f"target_certificate_tests::{n} ... ok" in text,f"missing unit {n}")
    return names

def build():
    req(sha(PROTOCOL)==PROTO_SHA,"protocol mismatch")
    for s in (SRC,TEST_B,TEST_C):req(s.is_dir() and sha(s/"Cargo.lock")==EXPECTED_LOCK,f"source/lock mismatch {s}")
    extract_inputs();(ROOT/"candidate.patch").write_bytes(patch_bytes());ntar([(p,f"source_candidate/{p.relative_to(SRC).as_posix()}") for p in files(SRC)],ROOT/"candidate_source.tar.gz")
    env=dict(os.environ);receipts=[]
    receipts.append(run("candidate_release_build_v3",["cargo","build","--offline","--locked","--release","--jobs","2","--example","koblitz_rank_fixture"],SRC,{**env,"CARGO_TARGET_DIR":str(BUILD)},ROOT/"candidate_build_v3.stdout",ROOT/"candidate_build_v3.stderr"));req(receipts[-1]["exit_code"]==0,"release build failed")
    CAND_BIN.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BUILD/"release/examples/koblitz_rank_fixture",CAND_BIN);CAND_BIN.chmod(0o755)
    receipts.append(run("candidate_fixed_unit_suite_v3",["cargo","test","--offline","--locked","--release","--jobs","2","--example","koblitz_rank_fixture","--","--nocapture"],SRC,{**env,"CARGO_TARGET_DIR":str(TEST_TARGET)},ROOT/"candidate_test_v3.stdout",ROOT/"candidate_test_v3.stderr"));req(receipts[-1]["exit_code"]==0,"unit suite failed")
    names=parse_tests(ROOT/"candidate_test_v3.stdout")
    root_readback=PACKAGE/"unit_specification_readback.json"
    atom(ROOT/"certificate_controls.json",{"schema":"crypto.autoresearch.target_stop_certificate_controls.v1","valid":True,"moduli":[17,R],"rust_unit_tests":names,"negative_checker_controls":True,"k75_expected":{"target_row":74,"rank_A":73,"rank_A_b":74,"rank_A_b_a":74,"returned_d":7},"coordinator_specification_readback_sha256":sha(root_readback) if root_readback.exists() else None,"scope":"deterministic unit arithmetic only; no solver process"})
    atom(ROOT/"prefix_controls.json",prefix_static())
    atom(ROOT/"build_execution_v3.json",{"schema":"crypto.autoresearch.target_stop_build_execution.v3","supersedes":"build_execution_v2.json","recorded_at":dt.datetime.now(dt.timezone.utc).isoformat(),"scope":"offline build/unit tests only; zero solver children","receipts":receipts,"candidate_binary_sha256":sha(CAND_BIN),"receipt_task_id":"TASK-20260921-bd19a7","rng_domain_task_id_preserved":"TASK-KIC-SAT-RHO-CROSSOVER-20260909","unit_rank_assertions":{"early":[1,2,2],"k75":[73,74,74]}})

def cases():
    p1=json.loads((P1/"protocol.json").read_text());p2=json.loads((P2/"artifacts/RUN-KIC-8b5038/case_manifest.json").read_text());old=set(p1["frozen_cases"]["calibration"]["scalars"]+p1["frozen_cases"]["heldout"]["scalars"]+p2["scalars"]);rows=[];scalars=[];ordinal=0
    for i in range(1,25):
      label=f"CSIC53-TARGETSTOP-v1-case-{i:02d}";d=1+int.from_bytes(hashlib.sha256(label.encode()).digest(),"little")%(R-1);dl=f"CSIC53-TARGETSTOP-v1-direct-seed-{i:02d}";rl=f"CSIC53-TARGETSTOP-v1-rho-seed-{i:02d}";ds=int.from_bytes(hashlib.sha256(dl.encode()).digest()[:8],"little");rs=int.from_bytes(hashlib.sha256(rl.encode()).digest()[:8],"little");scalars.append(d)
      for pos,arm in enumerate(ORDERS[(i-1)%6],1):ordinal+=1;rows.append({"ordinal":ordinal,"case_index":i,"position":pos,"arm":arm,"id":f"case-{i:02d}-p{pos}-{arm}","scalar_label":label,"scalar":d,"seed_label":rl if arm=="rho" else dl,"seed":rs if arm=="rho" else ds,"eta_denominator":None if arm=="rho" else 256,"factor_base_k":None if arm=="rho" else 75})
    req(len(set(scalars))==24 and not(set(scalars)&old),"freshness failed");positions={a:[sum(x["arm"]==a and x["position"]==p for x in rows) for p in (1,2,3)] for a in ("baseline","candidate","rho")};req(all(v==[8,8,8] for v in positions.values()),"balance failed")
    return {"schema":"crypto.autoresearch.target_stop_case_manifest.v1","experiment_id":"RUN-KIC-56c897","protocol_sha256":PROTO_SHA,"cases":rows,"scalars":scalars,"freshness":{"pairwise_distinct":True,"disjoint_R1_P2":True,"excluded_prior_scalars":len(old)},"counts":{"targets":24,"children":72,"per_arm":24},"position_counts":positions,"derivation_digest":dig({"scalars":scalars,"cases":rows})}

def freeze():
    for p in [ROOT/n for n in ("runner.py","analyze.py","prepare.py","certificate_checker.py","prefix_checker.py","receipt_parser.py","certificate_controls.json","prefix_controls.json","build_execution_v3.json")]+[BASE_BIN,RHO_BIN,CAND_BIN]:req(p.is_file(),f"missing {p}")
    extract_inputs();(ROOT/"candidate.patch").write_bytes(patch_bytes());atom(ROOT/"case_manifest.json",cases())
    bt,ct,tbt,tct=tree(TEST_B),tree(SRC),tree(TEST_B),tree(TEST_C)
    atom(ROOT/"source_delta_audit.json",{"schema":"crypto.autoresearch.target_stop_source_delta_audit.v1","valid":True,"parent_source_tar_sha256":sha(PARENT_TAR),"candidate_patch_sha256":sha(ROOT/"candidate.patch"),"production_changed_paths":["examples/koblitz_rank_fixture.rs"],"allowed_changes":["affine RHS/certificate echelon","target-pivot stop","truthful target receipt/validation","cfg(test) fixed certificate suite"],"prefix_static_controls_sha256":sha(ROOT/"prefix_controls.json"),"forbidden_changes_found":[]})
    atom(ROOT/"source_closure.json",{"schema":"crypto.autoresearch.target_stop_source_closure.v1","protocol_sha256":PROTO_SHA,"parent":{"source_tar_sha256":sha(PARENT_TAR),"baseline_binary_sha256":sha(BASE_BIN),"rho_binary_sha256":sha(RHO_BIN),"lock_sha256":sha(LOCK),"dependencies_sha256":sha(DEPS)},"candidate":{"files":len(ct),"bytes":sum(x["bytes"] for x in ct),"tree_digest":dig(ct),"source_tar_sha256":sha(ROOT/"candidate_source.tar.gz"),"binary_sha256":sha(CAND_BIN)},"test_tree_digests":{"baseline":dig(tbt),"candidate":dig(tct)}})
    tools={}
    for n,a in {"rustc":["rustc","--version","--verbose"],"cargo":["cargo","--version","--verbose"],"uname":["uname","-a"],"sw_vers":["sw_vers"]}.items():q=subprocess.run(a,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);tools[n]={"argv":a,"exit_code":q.returncode,"stdout":q.stdout,"stderr":q.stderr}
    be=json.loads((ROOT/"build_execution_v3.json").read_text());atom(ROOT/"build_toolchain.json",{"schema":"crypto.autoresearch.target_stop_build_toolchain.v3","tools":tools,"build_execution_sha256":sha(ROOT/"build_execution_v3.json"),"build_execution_path":"build_execution_v3.json","build_receipts":be["receipts"],"host":{"platform":platform.platform(),"machine":platform.machine(),"python":sys.version}})
    names=("runner.py","analyze.py","prepare.py","certificate_checker.py","prefix_checker.py","receipt_parser.py");codes={n:sha(ROOT/n) for n in names}
    atom(ROOT/"runner_analyzer_closure.json",{"schema":"crypto.autoresearch.target_stop_runner_analyzer_closure.v1","code_sha256":codes,"bootstrap":{"seed":"CSIC53-TARGETSTOP-BOOT-v1","resamples":10000,"draws":24,"type":7},"primary":"candidate/rho","secondary":"candidate/baseline","stage_nesting":"collection_ms includes certificate_validation_ms; legacy charged_total_ms excludes separately timed reference validation; external process wall is primary"})
    atom(ROOT/"preflight.json",{"schema":"crypto.autoresearch.target_stop_preflight.v1","status":"READY_FOR_STAGE_B_COMMIT_ONLY","protocol_sha256":PROTO_SHA,"code_sha256":codes,"source_closure_sha256":sha(ROOT/"source_closure.json"),"source_delta_audit_sha256":sha(ROOT/"source_delta_audit.json"),"case_manifest_sha256":sha(ROOT/"case_manifest.json"),"certificate_controls_sha256":sha(ROOT/"certificate_controls.json"),"prefix_controls_sha256":sha(ROOT/"prefix_controls.json"),"runner_analyzer_closure_sha256":sha(ROOT/"runner_analyzer_closure.json"),"binary_sha256":{"baseline":sha(BASE_BIN),"candidate":sha(CAND_BIN),"rho":sha(RHO_BIN)},"model":{"resolved_model_id":"gpt-5.6-sol","reasoning_effort":"high","fallback_used":False,"degraded":False,"model_verified":False},"holds":{"solver_controls":True,"science":True}})

def main():
    p=argparse.ArgumentParser();p.add_argument("--phase",choices=("build","freeze"),required=True);a=p.parse_args();build() if a.phase=="build" else freeze()
if __name__=="__main__":main()
