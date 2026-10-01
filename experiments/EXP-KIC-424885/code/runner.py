#!/usr/bin/env python3
"""Staged immutable supervisor for EXP-KIC-424885.

Stage A executes native controls and custody only. Stages B/C additionally
require an exact committed admission blob and an explicit root assignment.
"""
from __future__ import annotations
import argparse,contextlib,datetime as dt,fcntl,gzip,hashlib,itertools,json,math,os,platform,random,resource,shlex,shutil,signal,statistics,subprocess,sys,tarfile,tempfile,time,traceback
from pathlib import Path
from typing import Any,Iterable
import field,circuits,checker,worker

CODE=Path(__file__).resolve().parent;EXP=CODE.parent;REPO=EXP.parents[1];RUN=EXP/"runs/RUN-KIC-c2b1b7"
DESIGN=REPO/"research/golden_factor_base_sat_20260921/design_completion.json"
DESIGN_SHA="1419bc2107601476c4fd44f90d67475ec15e98eef68a35888df9abfaed0aa3e5"
SPEC=EXP/"specification.yaml";SOLVER=Path("/opt/homebrew/bin/cryptominisat5")
LIBRARIES=(Path("/opt/homebrew/Cellar/cryptominisat/5.14.7/lib/libcryptominisat5.5.14.dylib"),
           Path("/opt/homebrew/opt/gmp/lib/libgmpxx.4.dylib"),Path("/opt/homebrew/opt/gmp/lib/libgmp.10.dylib"))
ARMS=("flat_sat","explicit_same_B","null_sat","direct_mitm")
TASK="TASK-20260921-882eef";EXPERIMENT="EXP-KIC-424885";RUN_ID="RUN-KIC-c2b1b7"
WORKER_WATCHDOG=120.;CAP=8*1024**3

def require(c:bool,m:str)->None:
    if not c:raise RuntimeError(m)
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def digest(value:Any)->str:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def utc()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def atomic_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+".tmp")
    with tmp.open("w") as f:json.dump(value,f,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
def append_jsonl(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a") as f:f.write(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n");f.flush();os.fsync(f.fileno())
class Tee:
    def __init__(self,original:Any,record:Any):self.original=original;self.record=record
    def write(self,value:str)->int:
        self.original.write(value);self.record.write(value);self.flush();return len(value)
    def flush(self)->None:
        self.original.flush();self.record.flush();os.fsync(self.record.fileno())
def normalized_tar(items:Iterable[tuple[Path,str]],dest:Path)->None:
    dest.parent.mkdir(parents=True,exist_ok=True);tmp=dest.with_name(dest.name+".tmp")
    with tmp.open("wb") as raw:
      with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as gz:
       with tarfile.open(fileobj=gz,mode="w",format=tarfile.PAX_FORMAT) as archive:
        for path,name in sorted(items,key=lambda item:item[1]):
         info=archive.gettarinfo(str(path),arcname=name);info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
         with path.open("rb") as source:archive.addfile(info,source)
      raw.flush();os.fsync(raw.fileno())
    os.replace(tmp,dest)
def code_hashes()->dict[str,str]:
    names=("field.py","circuits.py","worker.py","runner.py","checker.py","analyze.py","tests.py","README.md")
    return {name:sha(CODE/name) for name in names}
def solver_dependency_closure()->dict[str,Any]:
    require(SOLVER.is_file(),"CMS binary absent")
    version=subprocess.run([str(SOLVER),"--version"],capture_output=True,text=True,check=False)
    help_result=subprocess.run([str(SOLVER),"--help"],capture_output=True,text=True,check=False)
    require("CryptoMiniSat version 5.14.7" in version.stdout+version.stderr,"CMS version mismatch")
    (RUN/"cms.version.stdout").write_text(version.stdout);(RUN/"cms.version.stderr").write_text(version.stderr)
    (RUN/"cms.help.stdout").write_text(help_result.stdout);(RUN/"cms.help.stderr").write_text(help_result.stderr)
    deps=subprocess.run(["otool","-L",str(SOLVER)],capture_output=True,text=True,check=False)
    require(deps.returncode==0,"otool -L failed")
    (RUN/"cms.otool.txt").write_text(deps.stdout)
    for library in LIBRARIES:require(library.is_file(),f"non-system dependency absent: {library}")
    binaries=[(SOLVER,"bin/cryptominisat5")]+[(path,f"lib/{path.name}") for path in LIBRARIES]
    normalized_tar(binaries,RUN/"solver_snapshot.tar.gz")
    records=[{"path":str(path),"resolved_path":str(path.resolve()),"sha256":sha(path),"bytes":path.stat().st_size,"archive_name":name} for path,name in binaries]
    manifest={"schema":"crypto.autoresearch.cms_dependency_manifest.v1","binary_and_non_system_libraries":records,"system_dependencies":["/usr/lib/libz.1.dylib","/usr/lib/libc++.1.dylib","/usr/lib/libSystem.B.dylib"],"otool_sha256":sha(RUN/"cms.otool.txt"),"solver_snapshot_sha256":sha(RUN/"solver_snapshot.tar.gz"),"runtime_uses_hash_checked_host_paths":True}
    atomic_json(RUN/"solver_dependency_manifest.json",manifest)
    atomic_json(RUN/"solver_versions.json",{"schema":"crypto.autoresearch.cms_version_receipt.v1","version":"5.14.7","architecture":"arm64","reported_source_commit":"GIT-notfound","source_commit_verified":False,"version":{"argv":[str(SOLVER),"--version"],"exit_code":version.returncode,"stdout_sha256":sha(RUN/"cms.version.stdout"),"stderr_sha256":sha(RUN/"cms.version.stderr")},"help":{"argv":[str(SOLVER),"--help"],"exit_code":help_result.returncode,"stdout_sha256":sha(RUN/"cms.help.stdout"),"stderr_sha256":sha(RUN/"cms.help.stderr")}})
    return manifest
def verify_solver_closure()->dict[str,Any]:
    record=json.loads((RUN/"solver_dependency_manifest.json").read_text())
    for item in record["binary_and_non_system_libraries"]:
        path=Path(item["path"])
        require(path.is_file() and sha(path)==item["sha256"],f"CMS dependency hash mismatch: {path}")
    require(sha(RUN/"solver_snapshot.tar.gz")==record["solver_snapshot_sha256"],"CMS snapshot hash mismatch")
    return record
def bases()->tuple[dict,dict]:
    basis=json.loads((RUN/"basis_manifest.json").read_text())
    return basis["candidate"],basis["null"]
def create_case_manifest()->dict[str,Any]:
    candidate,null=bases();g=field.generator()
    ranked=sorted(range(1,71),key=lambda d:(field.digest(f"GFB-SAT-N7-v1-target-{d}"),d))[:16]
    cases=[];cms_count=0
    for index,d in enumerate(ranked,1):
        q=field.scalar_mul(g,d);assert q is not None
        order=ARMS[(index-1)%4:]+ARMS[:(index-1)%4]
        for pos,arm in enumerate(order,1):
            base=candidate if arm!="null_sat" else null
            shortcut=q in checker.base_points(base)
            needs_cms=arm!="direct_mitm" and not shortcut
            cms_count+=needs_cms
            cases.append({"ordinal":len(cases)+1,"case_index":index,"phase":"diagnostic" if index<=8 else "heldout","arm":arm,"position":pos,"id":f"case-{index:02d}-p{pos}-{arm}","scalar":d,"Q":list(q),"base_recipe":"null" if arm=="null_sat" else "candidate","expected_status":checker.oracle_status(q,base),"expected_shortcut":shortcut,"planned_cms":needs_cms})
    require(len(cases)==64 and cms_count<=48,"science process count mismatch")
    controls=[]
    for d in range(1,71):
        q=field.scalar_mul(g,d);assert q is not None
        expected="SAT" if d in (1,3,68,70) else "UNSAT"
        controls.append({"ordinal":d,"id":f"control-{d:02d}","scalar":d,"Q":list(q),"arm":"explicit_same_B","base_recipe":"small","expected_status":expected,"expected_shortcut":d in (1,70),"planned_cms":d not in (1,70)})
    require(sum(row["planned_cms"] for row in controls)==68,"control CMS count mismatch")
    return {"schema":"crypto.autoresearch.gfb_case_manifest.v1","experiment_id":EXPERIMENT,"run_id":RUN_ID,"target_scalars":ranked,"science_cases":cases,"control_cases":controls,"counts":{"controls":70,"control_cms":68,"science":64,"science_cms":cms_count},"ordering":"cyclic rotations of flat_sat,explicit_same_B,null_sat,direct_mitm","target_derivation":"raw SHA256 bytes ascending then integer tie-break; 16 of 1..70"}
def stage_a()->None:
    RUN.mkdir(parents=True,exist_ok=True)
    require(sha(DESIGN)==DESIGN_SHA,"normative design hash mismatch")
    for name in code_hashes():require((CODE/name).is_file(),f"code file absent: {name}")
    native=json.loads((RUN/"native_controls.json").read_text());require(native.get("status")=="passed","native controls not passed")
    basis=json.loads((RUN/"basis_manifest.json").read_text());require(basis["candidate"]["candidate_index"]==0 and basis["null"]["arrival_index"]==15,"frozen basis recipe mismatch")
    solver=solver_dependency_closure();cases=create_case_manifest()
    atomic_json(RUN/"case_manifest.json",cases)
    closure={"schema":"crypto.autoresearch.gfb_source_closure.v1","experiment_id":EXPERIMENT,"run_id":RUN_ID,"normative_design_sha256":DESIGN_SHA,"specification_sha256":sha(SPEC),"code_sha256":code_hashes(),"basis_manifest_sha256":sha(RUN/"basis_manifest.json"),"case_manifest_sha256":sha(RUN/"case_manifest.json"),"native_controls_sha256":sha(RUN/"native_controls.json"),"solver_versions_sha256":sha(RUN/"solver_versions.json"),"solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json"),"solver_snapshot_sha256":sha(RUN/"solver_snapshot.tar.gz"),"preserved_attempt1_sha256":sha(RUN/"preserved_pool_scan_attempt1/scan.json"),"solver_instances":0,"target_workers":0}
    atomic_json(RUN/"source_closure.json",closure)
    static_readiness_controls()
    atomic_json(RUN/"stage_a_receipt.json",{"schema":"crypto.autoresearch.gfb_stage_a_receipt.v1","status":"ready_for_committed_stage_b_admission","recorded_at":utc(),"source_closure_sha256":sha(RUN/"source_closure.json"),"static_readiness_controls_sha256":sha(RUN/"static_readiness_controls.json"),"solver_binary_sha256":solver["binary_and_non_system_libraries"][0]["sha256"],"native_controls_status":"passed","counts":cases["counts"],"solver_instances":0,"target_workers":0,"serving_model_probe":False,"next":"Coordinator commits readiness and explicitly assigns sole Stage B launch owner"})
    atomic_json(RUN/"readiness_receipt.json",{"schema":"crypto.autoresearch.gfb_readiness.v1","status":"STAGE_A_READY_ONLY","source_closure_sha256":sha(RUN/"source_closure.json"),"stage_a_receipt_sha256":sha(RUN/"stage_a_receipt.json"),"static_readiness_controls_sha256":sha(RUN/"static_readiness_controls.json"),"code_sha256":code_hashes(),"native_controls_sha256":sha(RUN/"native_controls.json"),"basis_manifest_sha256":sha(RUN/"basis_manifest.json"),"case_manifest_sha256":sha(RUN/"case_manifest.json"),"solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json"),"solver_snapshot_sha256":sha(RUN/"solver_snapshot.tar.gz"),"holds":{"controls":"committed Stage B admission and explicit sole launch assignment","science":"committed Stage C admission and explicit sole launch assignment"}})

def verify_stage_a_closure()->None:
    frozen=json.loads((RUN/"source_closure.json").read_text())
    require(frozen["normative_design_sha256"]==sha(DESIGN)==DESIGN_SHA,"normative design changed")
    require(frozen["specification_sha256"]==sha(SPEC),"specification changed")
    require(frozen["code_sha256"]==code_hashes(),"Stage A code changed after custody freeze")
    for key,name in (("basis_manifest_sha256","basis_manifest.json"),("case_manifest_sha256","case_manifest.json"),
                     ("native_controls_sha256","native_controls.json"),("solver_versions_sha256","solver_versions.json"),
                     ("solver_dependency_manifest_sha256","solver_dependency_manifest.json"),
                     ("solver_snapshot_sha256","solver_snapshot.tar.gz")):
        require(frozen[key]==sha(RUN/name),f"Stage A custody changed: {name}")
    verify_solver_closure()

def phase_already_launched(launch_path:Path,receipt_path:Path)->bool:
    return launch_path.exists() or receipt_path.exists()

def static_readiness_controls()->None:
    verify_stage_a_closure()
    original=globals()["code_hashes"]
    try:
        globals()["code_hashes"]=lambda:{**original(),"runner.py":"0"*64}
        try:verify_stage_a_closure()
        except RuntimeError as exc:require("code changed" in str(exc),"wrong hash-change rejection")
        else:raise AssertionError("changed live code hash was accepted")
    finally:globals()["code_hashes"]=original
    with tempfile.TemporaryDirectory(dir=RUN,prefix="static-launch-") as name:
        location=Path(name);marker=location/"launch.json";receipts=location/"receipts.jsonl"
        require(not phase_already_launched(marker,receipts),"fresh phase falsely claimed")
        marker.touch();require(phase_already_launched(marker,receipts),"duplicate phase marker accepted")
        marker.unlink();receipts.touch();require(phase_already_launched(marker,receipts),"duplicate receipt prefix accepted")
        with (location/"lock").open("a+") as first,(location/"lock").open("a+") as second:
            fcntl.flock(first.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            try:fcntl.flock(second.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:pass
            else:raise AssertionError("second parent acquired occupied launch lock")
    require(declared_censor({"status":"UNKNOWN","cms":{"exit_code":0}},False,False)=="declared_CMS_limit_or_resource","CMS censor rejected")
    require(declared_censor(None,True,False)=="outer_memory_cap","memory censor rejected")
    require(declared_censor(None,False,True)=="outer_watchdog","watchdog censor rejected")
    require(declared_censor({"status":"UNKNOWN","cms":{"exit_code":13}},False,False) is None,"unexpected solver code censored")
    atomic_json(RUN/"static_readiness_controls.json",{"schema":"crypto.autoresearch.gfb_static_readiness_controls.v1","status":"passed","tests":["live_code_hash_change_rejected","duplicate_phase_marker_rejected","duplicate_receipt_prefix_rejected","parallel_parent_lock_rejected","declared_CMS_UNKNOWN_and_outer_caps_censored","unexpected_CMS_exit_not_censored"],"solver_instances":0,"target_workers":0})

def declared_censor(result:dict[str,Any]|None,outer_cap:bool,outer_watchdog:bool)->str|None:
    if outer_cap:return "outer_memory_cap"
    if outer_watchdog:return "outer_watchdog"
    if result and result.get("status")=="UNKNOWN":
        cms=result.get("cms") or {}
        if cms.get("exit_code")==0 or cms.get("sampling",{}).get("cap_reached"):
            return "declared_CMS_limit_or_resource"
    return None

def committed_admission(path:Path,commit:str,phase:str)->dict[str,Any]:
    relative=path.relative_to(REPO).as_posix()
    require(subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],cwd=REPO).returncode==0,"admission commit not reachable")
    blob=subprocess.run(["git","show",f"{commit}:{relative}"],cwd=REPO,capture_output=True,check=False)
    require(blob.returncode==0 and path.read_bytes()==blob.stdout,"admission not exactly bound at named commit")
    record=json.loads(blob.stdout)
    require(record.get("status")=="admitted" and record.get("phase")==phase and record.get("task_id")==TASK and record.get("run_id")==RUN_ID,"admission role/scope mismatch")
    require(record.get("source_closure_sha256")==sha(RUN/"source_closure.json"),"admission source closure mismatch")
    require(record.get("solver_dependency_manifest_sha256")==sha(RUN/"solver_dependency_manifest.json"),"admission solver closure mismatch")
    pinned=[RUN/"source_closure.json",RUN/"basis_manifest.json",RUN/"case_manifest.json",
            RUN/"native_controls.json",RUN/"solver_versions.json",RUN/"solver_dependency_manifest.json",
            RUN/"solver_snapshot.tar.gz"]+[CODE/name for name in code_hashes()]
    for current in pinned:
        item=current.relative_to(REPO).as_posix()
        committed=subprocess.run(["git","show",f"{commit}:{item}"],cwd=REPO,capture_output=True,check=False)
        require(committed.returncode==0 and committed.stdout==current.read_bytes(),f"named admission commit readback mismatch: {item}")
    if phase=="science":require(record.get("control_replay_sha256")==sha(RUN/"control_replay.json"),"admission controls mismatch")
    return record

def small_base()->dict:
    g=field.generator();assert g is not None
    return {"points":[list(p) for p in sorted((g,field.neg(g)),key=field.point_key)],"x_values":[g[0]],"recipe":"small"}
def fresh_env(cwd:Path)->dict[str,str]:
    home=cwd/"home";temp=cwd/"tmp";home.mkdir();temp.mkdir()
    return {"PATH":os.defpath,"HOME":str(home),"TMPDIR":str(temp),"LANG":"C","LC_ALL":"C","PYTHONDONTWRITEBYTECODE":"1"}
def run_one(case:dict[str,Any],phase:str,base:dict)->dict[str,Any]:
    raw=RUN/"raw"/phase/f"{case['ordinal']:03d}_{case['id']}";require(not raw.exists(),f"immutable slot already exists: {raw}")
    raw.mkdir(parents=True);cwd=raw/"cwd";cwd.mkdir();stdout=raw/"worker.stdout";stderr=raw/"worker.stderr"
    closure=verify_solver_closure();solver=closure["binary_and_non_system_libraries"][0]
    task={"arm":case["arm"],"Q":case["Q"],"base_recipe":case["base_recipe"],"solver_path":solver["path"],"solver_sha256":solver["sha256"]}
    input_path=cwd/"input.json";input_path.write_text(json.dumps(task,sort_keys=True,indent=2)+"\n")
    env=fresh_env(cwd);sampler=worker.Sampler();peak=None;samples=0;cap=False;watchdog=False;usage=None;status=None;popen_error=None
    argv=[sys.executable,str(CODE/"worker.py"),str(input_path)]
    with stdout.open("xb") as so,stderr.open("xb") as se:
        start=time.monotonic_ns();started=utc()
        try:p=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=so,stderr=se,start_new_session=True,close_fds=True)
        except Exception as exc:popen_error=f"{type(exc).__name__}: {exc}"
        if popen_error is None:
            last=0
            while True:
                pid,st,u=os.wait4(p.pid,os.WNOHANG)
                if pid==p.pid:status=st;usage=u;stop=time.monotonic_ns();break
                now=time.monotonic_ns()
                if now-last>=50_000_000:
                    v=sampler.sample(p.pid);last=now
                    if v is not None:samples+=1;peak=v if peak is None else max(peak,v)
                    if v is not None and v>=CAP:cap=True
                if (now-start)/1e9>=WORKER_WATCHDOG:watchdog=True
                if cap or watchdog:
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    _,status,usage=os.wait4(p.pid,0);stop=time.monotonic_ns();break
                time.sleep(.001)
            p.returncode=os.waitstatus_to_exitcode(status)
        else:stop=time.monotonic_ns()
        so.flush();se.flush();os.fsync(so.fileno());os.fsync(se.fileno())
    result_path=cwd/"result.json";result=None;parse_error=None
    if result_path.is_file():
        try:result=json.loads(result_path.read_text())
        except Exception as exc:parse_error=f"result parse failed: {type(exc).__name__}: {exc}"
    error=popen_error or parse_error;valid=False;replay=None
    censored_reason=declared_censor(result,cap,watchdog)
    if not error and not censored_reason and p.returncode==0 and result is not None and result.get("status")=="UNKNOWN":
        error="unexpected UNKNOWN without declared CMS limit or resource"
    if not error and not censored_reason and p.returncode==0 and result is not None:
        try:
            require(result.get("arm")==case["arm"] and result.get("Q")==case["Q"]
                    and result.get("base_recipe")==case["base_recipe"],"worker result input identity mismatch")
            require(bool(result.get("cms"))==bool(case["planned_cms"]),"planned CMS child mismatch")
            require(bool(result.get("shortcut"))==bool(case["expected_shortcut"]),"frozen shortcut mismatch")
            replay=checker.replay_result(result,tuple(case["Q"]),base)
            require(replay["worker_status"]==case["expected_status"],"worker differs from frozen expected verdict")
            valid=True
        except Exception as exc:error=f"{type(exc).__name__}: {exc}"
    elif error is None and censored_reason is None:error="worker failed or result missing"
    if usage is None or usage.ru_maxrss<=0 or not all(math.isfinite(v) and v>=0 for v in (usage.ru_utime,usage.ru_stime)):
        valid=False;error=error or "missing or nonfinite outer wait4 CPU/RSS"
    # A short-lived worker can be unsampled; wait4 RSS remains mandatory.
    if result and result.get("cms"):
        cms=result["cms"]
        if cms.get("wait4_peak_rss") in (None,0) or not all(
            isinstance(cms.get(name),(int,float)) and math.isfinite(cms[name]) and cms[name]>=0
            for name in ("wait4_user_seconds","wait4_system_seconds")
        ):
            valid=False;error=error or "missing or nonfinite CMS wait4 CPU/RSS"
    classification=("completed_valid" if valid else "censored" if censored_reason and error is None
                    else "failed_implementation" if result and result.get("status")=="FAILED_IMPLEMENTATION"
                    else "invalid_measurement" if result is not None else "failed_infrastructure")
    return {"schema":"crypto.autoresearch.gfb_worker_receipt.v1","phase":phase,"ordinal":case["ordinal"],"case_id":case["id"],"case_index":case.get("case_index"),"arm":case["arm"],"scalar_driver_only":case["scalar"],"Q":case["Q"],"expected_status":case["expected_status"],"valid":valid,"classification":classification,"censored_reason":censored_reason if classification=="censored" else None,"error":error,"replay":replay,"worker_result":result,"argv":argv,"environment":env,"input_sha256":sha(input_path),"stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),"result_sha256":sha(result_path) if result_path.is_file() else None,"started_at":started,"ended_at":utc(),"wall_seconds":(stop-start)/1e9,"outer_wait4":{"exit_code":os.waitstatus_to_exitcode(status) if status is not None else None,"user_seconds":usage.ru_utime if usage else None,"system_seconds":usage.ru_stime if usage else None,"peak_rss":usage.ru_maxrss if usage else None,"rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent"},"outer_sampling":{"method":sampler.method,"samples":samples,"peak_bytes":peak,"unsampled":samples==0,"error":sampler.error},"watchdog_reached":watchdog,"cap_reached":cap,"cms_metric_scope":"child wait4 metrics are separate; do not sum with potentially inclusive outer CPU"}
def rows(path:Path)->list[dict[str,Any]]:
    return [] if not path.exists() else [json.loads(x) for x in path.read_text().splitlines() if x]
def run_phase(phase:str,admission_path:Path,commit:str)->None:
    verify_stage_a_closure()
    committed_admission(admission_path,commit,phase)
    manifest=json.loads((RUN/"case_manifest.json").read_text())
    cases=manifest["control_cases"] if phase=="controls" else manifest["science_cases"]
    receipt_path=RUN/("control_receipts.jsonl" if phase=="controls" else "receipts.jsonl")
    launch_path=RUN/("control_launch.json" if phase=="controls" else "science_launch.json")
    require(not phase_already_launched(launch_path,receipt_path),"phase already launched; frozen batch may not be re-entered")
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()
    atomic_json(launch_path,{"schema":"crypto.autoresearch.gfb_phase_launch.v1","phase":phase,"admission_commit":commit,"execution_head_at_start":head,"admission_path":admission_path.relative_to(REPO).as_posix(),"argv":[sys.executable,*sys.argv],"started_at":utc()})
    print(json.dumps({"phase":phase,"event":"launch","admission_commit":commit,"case_count":len(cases)},sort_keys=True),flush=True)
    candidate,null=bases()
    for case in cases:
        verify_stage_a_closure()
        base=small_base() if phase=="controls" else null if case["arm"]=="null_sat" else candidate
        try:receipt=run_one(case,phase,base)
        except Exception:
            archive_phase(phase,complete=False)
            raise
        append_jsonl(receipt_path,receipt)
        print(json.dumps({"case_id":case["id"],"classification":receipt["classification"],"wall_seconds":receipt["wall_seconds"]},sort_keys=True),flush=True)
        if not receipt["valid"] and receipt["classification"]!="censored":
            archive_phase(phase,complete=False)
            raise RuntimeError(f"frozen slot invalid: {case['id']}: {receipt['error']}")
    require(len(rows(receipt_path))==len(cases),"frozen phase incomplete")
    sys.stdout.flush();sys.stderr.flush()
    archive_phase(phase)
def archive_phase(phase:str,complete:bool=True)->None:
    raw=RUN/"raw"/phase
    files=sorted(p for p in raw.rglob("*") if p.is_file())
    name="control" if phase=="controls" else "raw"
    manifest={"schema":"crypto.autoresearch.gfb_raw_manifest.v1","phase":phase,"files":[{"path":p.relative_to(RUN).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files]}
    atomic_json(RUN/("control_manifest.json" if phase=="controls" else "raw_manifest.json"),manifest)
    normalized_tar([(p,p.relative_to(RUN).as_posix()) for p in files],RUN/("control_outputs.tar.gz" if phase=="controls" else "raw_outputs.tar.gz"))
    if not complete:return
    if phase=="controls":
        rr=rows(RUN/"control_receipts.jsonl")
        expected=json.loads((RUN/"case_manifest.json").read_text())["counts"]
        actual_cms=sum(bool((r["worker_result"] or {}).get("cms")) for r in rr)
        actual_shortcuts=sum(bool((r["worker_result"] or {}).get("shortcut",False)) for r in rr)
        valid=len(rr)==70 and all(r["valid"] for r in rr) and actual_cms==expected["control_cms"] and actual_shortcuts==2
        atomic_json(RUN/"control_replay.json",{"schema":"crypto.autoresearch.gfb_control_replay.v1","valid":valid,"workers":len(rr),"cms_descendants":actual_cms,"expected_cms_descendants":expected["control_cms"],"actual_shortcuts":actual_shortcuts,"expected_shortcuts":2,"receipt_sha256":sha(RUN/"control_receipts.jsonl"),"control_archive_sha256":sha(RUN/"control_outputs.tar.gz")})
    else:
        rr=rows(RUN/"receipts.jsonl")
        science_cases=json.loads((RUN/"case_manifest.json").read_text())["science_cases"]
        expected_cms=sum(bool(case["planned_cms"]) for case in science_cases)
        expected_shortcuts=sum(bool(case["expected_shortcut"]) for case in science_cases)
        actual_cms=sum(bool((r["worker_result"] or {}).get("cms")) for r in rr)
        actual_shortcuts=sum(bool((r["worker_result"] or {}).get("shortcut",False)) for r in rr)
        atomic_json(RUN/"cnf_xor_manifest.json",{"schema":"crypto.autoresearch.gfb_cnf_xor_manifest.v1","cases":[{"id":r["case_id"],"arm":r["arm"],"instance":(r["worker_result"] or {}).get("instance")} for r in rr]})
        atomic_json(RUN/"replay.json",{"schema":"crypto.autoresearch.gfb_replay.v1","valid":len(rr)==64 and all(r["valid"] for r in rr) and actual_cms==expected_cms and actual_shortcuts==expected_shortcuts,"counts":{"actual_cms":actual_cms,"expected_cms":expected_cms,"actual_shortcuts":actual_shortcuts,"expected_shortcuts":expected_shortcuts},"receipts_sha256":sha(RUN/"receipts.jsonl"),"worker_replays":[{"case_id":r["case_id"],"replay":r["replay"]} for r in rr]})
        prefix_diagnostic()
        from analyze import analyze
        analyze()
        finalize_run()

def prefix_diagnostic()->None:
    candidate,_=bases();manifest=json.loads((RUN/"case_manifest.json").read_text())
    records=[];deadline=time.monotonic()+480
    for case_index in range(9,17):
        case=next(row for row in manifest["science_cases"] if row["case_index"]==case_index)
        q=tuple(case["Q"]);d=case["scalar"]
        if q in checker.base_points(candidate):
            records.append({"case_index":case_index,"scalar":d,"shortcut":True,"eligible":False,"reason":"Q_in_candidate_base"})
            continue
        xs=candidate["x_values"]
        pairs=list(itertools.combinations_with_replacement(xs,2))
        pairs.sort(key=lambda pair:(field.digest(f"GFB-SAT-N7-v1-prefix-{d}-{pair[0]}-{pair[1]}"),pair[0],pair[1]))
        prefixes=[(x,None) for x in xs]+pairs[:32]
        require(len(prefixes)==46,"prefix count changed")
        circuits_by_arm={}
        for arm in ("flat_sat","explicit_same_B"):
            c=circuits.Circuit();c.relation(candidate,q,arm);circuits_by_arm[arm]=c
        prefix_rows=[];counts={arm:0 for arm in circuits_by_arm}
        for x1,x2 in prefixes:
            extendible=checker.prefix_extendible(q,candidate,x1,x2)
            entry={"x1":x1,"x2":x2,"oracle_extendible":extendible,"arms":{}}
            for arm,c in circuits_by_arm.items():
                units={var:bool(x1>>bit&1) for bit,var in enumerate(c.inputs["x1"])}
                if x2 is not None:units.update({var:bool(x2>>bit&1) for bit,var in enumerate(c.inputs["x2"])})
                start=time.monotonic_ns();result=circuits.propagate(c,units)
                entry["arms"][arm]={**result,"wall_seconds":(time.monotonic_ns()-start)/1e9}
                counts[arm]+=int(result["contradiction"])
                if result["contradiction"] and extendible:
                    append_jsonl(RUN/"prefix_progress.jsonl",{"case_index":case_index,**entry})
                    raise RuntimeError(f"unsound prefix contradiction at case {case_index}, x1={x1}, x2={x2}")
            prefix_rows.append(entry)
            append_jsonl(RUN/"prefix_progress.jsonl",{"case_index":case_index,**entry})
            if time.monotonic()>deadline:
                raise TimeoutError("prefix diagnostic exceeded declared 480s watchdog; progress preserved")
        scores={arm:counts[arm]/46 for arm in counts}
        records.append({"case_index":case_index,"scalar":d,"shortcut":False,"eligible":True,"prefixes":prefix_rows,"contradiction_counts":counts,"scores":scores,"flat_minus_explicit":scores["flat_sat"]-scores["explicit_same_B"]})
    differences=[r["flat_minus_explicit"] for r in records if r.get("eligible")]
    atomic_json(RUN/"prefix_propagation.json",{"schema":"crypto.autoresearch.gfb_prefix_diagnostic.v1","status":"complete","method":"fresh original CNF/native-XOR plus coordinate units; CNF unit scan then deterministic GF2 RREF, no CDCL or branching","records":records,"eligible_cases":len(differences),"paired_median_flat_minus_explicit":statistics.median(differences) if differences else None,"effect_eligibility":"eligible" if len(differences)>=4 else "INCONCLUSIVE_BELOW_FOUR","progress_sha256":sha(RUN/"prefix_progress.jsonl") if (RUN/"prefix_progress.jsonl").is_file() else None})

def finalize_run()->None:
    receipts=rows(RUN/"receipts.jsonl");analysis=json.loads((RUN/"analysis.json").read_text())
    launch=json.loads((RUN/"science_launch.json").read_text())
    actual_command=shlex.join(launch["argv"])
    (RUN/"command.txt").write_text(actual_command+"\n")
    require((RUN/"stdout.log").is_file() and (RUN/"stderr.log").is_file(),"actual supervisor streams not captured")
    atomic_json(RUN/"raw-result.json",{"schema":"crypto.autoresearch.gfb_aggregate_raw_result.v1","analysis_sha256":sha(RUN/"analysis.json"),"receipts_sha256":sha(RUN/"receipts.jsonl"),"summary":analysis["summary"],"predicate":analysis["finite_effect_predicate"]})
    head=launch["admission_commit"]
    dirty=subprocess.run(["git","status","--porcelain","--",str(EXP.relative_to(REPO))],cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
    atomic_json(RUN/"environment.json",{"schema":"crypto.autoresearch.gfb_environment.v1","platform":platform.platform(),"machine":platform.machine(),"python":sys.version,"solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json"),"child_environment":"fresh HOME/TMPDIR and explicit PATH/LANG/LC_ALL/PYTHONDONTWRITEBYTECODE whitelist","admission_commit":head,"execution_head_at_start":launch["execution_head_at_start"],"dirty_scope_at_finalize":dirty})
    started=min(r["started_at"] for r in receipts);finished=max(r["ended_at"] for r in receipts)
    wall_sum=sum(r["wall_seconds"] for r in receipts)
    manifest={"run":{"id":RUN_ID,"experiment_id":EXPERIMENT,"status":"completed_valid" if all(r["valid"] for r in receipts) else "completed_censored" if any(r["classification"]=="censored" for r in receipts) else "completed_invalid","code":{"commit":head,"execution_head_at_start":launch["execution_head_at_start"],"dirty":bool(dirty),"dirty_scope":dirty,"command":actual_command,"source_sha256":code_hashes()},"inference":{"requested_policy":"executor-implementation","resolved_model_id":"gpt-5.6-sol","reasoning_effort":"high","fallback_used":False,"model_verified":False},"environment":{"operating_system":platform.platform(),"architecture":platform.machine(),"python_version":sys.version.split()[0],"dependencies":{"solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json")}},"inputs":{"parameters":{"field_bits":7,"curve":"Koblitz a=1 b=1","targets":16,"control_workers":70,"science_workers":64,"frozen_normative_sha256":DESIGN_SHA}},"timing":{"started_at":started,"finished_at":finished,"wall_seconds":wall_sum,"wall_scope":"sum of 64 independent outer-worker spawn-to-wait4-reap measurements; not campaign elapsed wall"},"resources":{"peak_rss_bytes":max(r["outer_wait4"]["peak_rss"] for r in receipts),"cpu_seconds":None,"note":"per-worker and CMS CPU/RSS remain separate in receipts"},"result":{"metrics":analysis["summary"],"valid":all(r["valid"] for r in receipts),"invalid_reason":None if all(r["valid"] for r in receipts) else "see receipts.jsonl","certificate":{"kind":"none","verified":True,"verifier":"finite aggregate measurement; individual decompositions group-replayed in replay.json"}},"artifacts":{"command":"command.txt","environment":"environment.json","stdout":"stdout.log","stderr":"stderr.log","raw_result":"raw-result.json"}}}
    (RUN/"manifest.yaml").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    atomic_json(RUN/"execution_receipt.json",{"execution_report":{"experiment_id":EXPERIMENT,"run_id":RUN_ID,"implementation_commit":head,"protocol_deviations":[],"runs":{"control_count":len(rows(RUN/"control_receipts.jsonl")),"science_count":len(receipts),"valid_science_count":sum(r["valid"] for r in receipts)},"observations":[{"analysis":"analysis.json","frozen_prediction":"specification.yaml#experiment.preregistered_prediction"}],"anomalies":[{"id":r["case_id"],"classification":r["classification"],"reason":r["error"] or r.get("censored_reason")} for r in receipts if not r["valid"]],"executor_assessment":{"protocol_complete":len(receipts)==64,"data_quality":"good" if all(r["valid"] for r in receipts) else "limited","requires_rerun":False},"claim_boundary":"finite synthetic observation only"}})
    declared=["source_closure.json","basis_manifest.json","case_manifest.json","solver_versions.json","solver_dependency_manifest.json","native_controls.json","static_readiness_controls.json","readiness_receipt.json","control_launch.json","control_stdout.log","control_stderr.log","science_launch.json","control_receipts.jsonl","control_replay.json","receipts.jsonl","raw_outputs.tar.gz","raw_manifest.json","cnf_xor_manifest.json","replay.json","prefix_propagation.json","analysis.json","execution_receipt.json","solver_snapshot.tar.gz","stage_a_receipt.json","control_outputs.tar.gz","control_manifest.json","manifest.yaml","command.txt","environment.json","stdout.log","stderr.log","raw-result.json"]
    missing=[name for name in declared if not(RUN/name).is_file()];require(not missing,f"required run artifacts missing: {missing}")
    atomic_json(RUN/"snapshot_manifest.json",{"schema":"crypto.autoresearch.gfb_snapshot_manifest.v1","self_hash_omitted":True,"artifacts":[{"path":name,"bytes":(RUN/name).stat().st_size,"sha256":sha(RUN/name)} for name in declared]})

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--phase",choices=("stage-a","controls","science"),required=True)
    p.add_argument("--admission");p.add_argument("--admission-commit");args=p.parse_args()
    if args.phase=="stage-a":stage_a();return
    require(args.admission and args.admission_commit,"explicit root-named admission path and commit required")
    phase=args.phase;admission_path=Path(args.admission).resolve()
    with (RUN/f"{phase}.parent.lock").open("a+") as lock:
        try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError(f"another {phase} parent owns the launch lock")
        receipt_path=RUN/("control_receipts.jsonl" if phase=="controls" else "receipts.jsonl")
        launch_path=RUN/("control_launch.json" if phase=="controls" else "science_launch.json")
        require(not phase_already_launched(launch_path,receipt_path),"phase was previously launched; no duplicate parent or automatic resume")
        verify_stage_a_closure()
        committed_admission(admission_path,args.admission_commit,phase)
        stdout_path=RUN/("control_stdout.log" if phase=="controls" else "stdout.log")
        stderr_path=RUN/("control_stderr.log" if phase=="controls" else "stderr.log")
        with stdout_path.open("x") as stdout_record,stderr_path.open("x") as stderr_record:
            with contextlib.redirect_stdout(Tee(sys.stdout,stdout_record)),contextlib.redirect_stderr(Tee(sys.stderr,stderr_record)):
                try:run_phase(phase,admission_path,args.admission_commit)
                except BaseException:
                    if launch_path.exists() and (RUN/"raw"/phase).exists():
                        try:archive_phase(phase,complete=False)
                        except Exception:traceback.print_exc(file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)
                    raise SystemExit(1)
if __name__=="__main__":main()
