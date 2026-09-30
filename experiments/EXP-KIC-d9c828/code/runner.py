#!/usr/bin/env python3
"""Immutable, admitted P9 pair-reuse supervisor.

Build is separate from the one control, one checker and 384 benchmark native
children. Benchmark primary wall starts at direct native Popen and ends at
sole wait4 reap; no Python worker exists inside that boundary.
"""
from __future__ import annotations
import argparse,ctypes,datetime as dt,errno,fcntl,gzip,hashlib,json,math,os,platform,resource,select,shutil,signal,stat,subprocess,sys,tarfile,time,traceback
from pathlib import Path
from typing import Any
import analyze,checker

CODE=Path(__file__).resolve().parent
EXP=CODE.parent
REPO=EXP.parents[1]
RUN=EXP/"runs/RUN-KIC-ba86d9"
P=REPO/"research/pair_reuse_20260922"
BASE=P/"inputs/n19_base.json"
SCHEDULE=P/"inputs/schedule.json"
BINDINGS=P/"inputs/bindings.json"
PROTOCOL=P/"protocol.json"
SPEC=EXP/"specification.yaml"
BASE_SHA="f00b5c5710d041bf862525b5f8d1baf15328e4a9bd6a11f659d300b5ca62cfb1"
SCHEDULE_SHA="a1cfbbf5053318c6b568948723abf613d991039c35152d524ee5909ece6387cb"
PROTOCOL_SHA="3de8d70ae219cd2aad2c6ccf67156fdc3d1c6591729efad9e9822224a4d844de"
TASK="TASK-20260922-89d6e6"
RUN_ID="RUN-KIC-ba86d9"
DISPATCH_SNAPSHOT="83c11d0eb89e4ff526aa6b6ffa8a97d00c9fac7a"
AMENDMENT_COMMIT="760b1bbb4d1496280c8b6c91e61d6ca34dfa5fc2"
CLAIM_COMMIT="ef473279360ec131c4a4055b5939d5cf44544d3e"
ARMS=("expanded","canonical_normal_x")
SOURCE_FILES=("native.cpp","checker.py","runner.py","analyze.py","README.md")
BINARY=RUN/"build/native"
CAP=8*1024**3
LIMIT={"control":1800,"checker":3600,"benchmark":60}
CONTROL_FILES=("native_controls.json","bases.json","public_panels.json","panel_files.json","oracle_metadata.json",
               "pair_tables.json","control_queries.json")

def need(ok:bool,message:str)->None:
    if not ok:raise RuntimeError(message)
def utc()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def atomic_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+".tmp")
    with temp.open("w") as f:
        json.dump(value,f,sort_keys=True,indent=2);f.write("\n")
        f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
def append_jsonl(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n")
        f.flush();os.fsync(f.fileno())
def rows(path:Path)->list[dict[str,Any]]:
    return [] if not path.is_file() else [json.loads(line) for line in path.read_text().splitlines() if line]
def source_hashes()->dict[str,str]:return {name:sha(CODE/name) for name in SOURCE_FILES}
def verify_inputs()->None:
    for path,want in ((BASE,BASE_SHA),(SCHEDULE,SCHEDULE_SHA),(PROTOCOL,PROTOCOL_SHA)):
        need(path.is_file() and sha(path)==want,f"frozen input changed: {path}")
    need(BINDINGS.is_file() and SPEC.is_file(),"binding/specification missing")
def normalized_tar(files:list[tuple[Path,str]],out:Path)->None:
    temp=out.with_name(out.name+".tmp")
    with temp.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode="w",format=tarfile.PAX_FORMAT) as archive:
                for path,name in sorted(files,key=lambda item:item[1]):
                    info=archive.gettarinfo(str(path),arcname=name)
                    info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
                    info.type=tarfile.REGTYPE;info.linkname=""
                    with path.open("rb") as f:archive.addfile(info,f)
        raw.flush();os.fsync(raw.fileno())
    os.replace(temp,out)
def case_manifest()->dict[str,Any]:
    workers=json.loads(SCHEDULE.read_text())["jobs"]
    need(len(workers)==384 and [row["ordinal"] for row in workers]==list(range(1,385)),
         "frozen 384-job schedule malformed")
    expected={(r,m,p,a,t) for r in ("n19_k4","n23_k16") for m in (1,32,512)
              for p in range(8) for a in ARMS for t in range(4)}
    actual={(row.get("regime"),row.get("M"),row.get("panel"),row.get("arm"),row.get("repeat")) for row in workers}
    need(actual==expected,"schedule omits or duplicates a P9 cell")
    return {"schema":"crypto.autoresearch.pair_reuse_case_manifest.v1","jobs":workers,
            "counts":{"regimes":2,"M_values":[1,32,512],"panels":8,
                      "technical_repeats":4,"arms":2,"native_workers":384,
                      "control_processes":1,"checker_processes":1},
            "target_scalar_scope":"control/oracle only; native cold job accepts Q-only panel data"}
def build()->None:
    verify_inputs();RUN.mkdir(parents=True,exist_ok=True)
    need(not BINARY.exists() and not (RUN/"source_closure.json").exists() and not (RUN/"build_receipt.json").exists(),
         "final build/source closure already exists; preserve and request additive successor")
    attempt=RUN/"stage_a_attempt_02/build_attempts/attempt-001-final-source"
    need(not attempt.exists(),"additive final-source build attempt already exists")
    folder=attempt/"build";folder.mkdir(parents=True)
    compiler=Path("/usr/bin/clang++")
    version=subprocess.run([str(compiler),"--version"],capture_output=True,check=False)
    need(version.returncode==0,"compiler version read failed")
    (folder/"compiler.version.stdout").write_bytes(version.stdout)
    (folder/"compiler.version.stderr").write_bytes(version.stderr)
    attempt_binary=folder/"native"
    argv=[str(compiler),"-O3","-std=c++20","-DNDEBUG","-Wall","-Wextra","-Wpedantic",
          "-o",str(attempt_binary),str(CODE/"native.cpp")]
    before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic_ns()
    result=subprocess.run(argv,capture_output=True,check=False,cwd=REPO)
    wall=(time.monotonic_ns()-start)/1e9
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    (folder/"compile.stdout").write_bytes(result.stdout)
    (folder/"compile.stderr").write_bytes(result.stderr)
    python_argv=[sys.executable,"-c","import pathlib; [compile(pathlib.Path(p).read_text(),p,'exec') for p in __import__('sys').argv[1:]]",
                 *[str(CODE/name) for name in ("checker.py","runner.py","analyze.py")]]
    python_check=subprocess.run(python_argv,capture_output=True,check=False,cwd=REPO)
    (folder/"python_check.stdout").write_bytes(python_check.stdout)
    (folder/"python_check.stderr").write_bytes(python_check.stderr)
    attempt_receipt={"schema":"crypto.autoresearch.pair_reuse_build_attempt.v1",
        "argv":argv,"exit_code":result.returncode,"wall_seconds":wall,
        "source_sha256":sha(CODE/"native.cpp"),"compiler_sha256":sha(compiler),
        "compiler_version_sha256":sha(folder/"compiler.version.stdout"),
        "binary_sha256":sha(attempt_binary) if attempt_binary.is_file() else None,
        "compile_stdout_sha256":sha(folder/"compile.stdout"),
        "compile_stderr_sha256":sha(folder/"compile.stderr"),
        "python_static_argv":python_argv,"python_static_exit_code":python_check.returncode,
        "python_static_stdout_sha256":sha(folder/"python_check.stdout"),
        "python_static_stderr_sha256":sha(folder/"python_check.stderr"),
        "compiler_child_cpu_user_delta":after.ru_utime-before.ru_utime,
        "compiler_child_cpu_system_delta":after.ru_stime-before.ru_stime,
        "compiler_rss_highwater_before":before.ru_maxrss,
        "compiler_rss_highwater_after":after.ru_maxrss,
        "compiler_rss_scope":"RUSAGE_CHILDREN high-water marks, not a per-build delta",
        "requested_policy":"executor-implementation","resolved_model_id":"gpt-5.6-sol",
        "reasoning_effort":"high","fallback_used":False,"degraded_used":False,"model_verified":False,
        "implementation_runtime_amendment_sha256":sha(P/"implementation_runtime_amendment.md"),
        "amendment_commit":AMENDMENT_COMMIT,"dispatch_snapshot":DISPATCH_SNAPSHOT,"claim_commit":CLAIM_COMMIT,
        "control_processes":0,"checker_processes":0,"benchmark_processes":0}
    atomic_json(attempt/"build_receipt.json",attempt_receipt)
    need(result.returncode==0 and attempt_binary.is_file() and python_check.returncode==0,
         "native/Python build failed; additive attempt receipt retained")
    binary_file=subprocess.run(["file",str(attempt_binary)],capture_output=True,check=False)
    otool=subprocess.run(["otool","-L",str(attempt_binary)],capture_output=True,check=False)
    need(binary_file.returncode==0 and b"arm64" in binary_file.stdout and otool.returncode==0,
         "native architecture/dependency inspection failed")
    (folder/"native.file.stdout").write_bytes(binary_file.stdout)
    (folder/"native.file.stderr").write_bytes(binary_file.stderr)
    (folder/"native.otool.stdout").write_bytes(otool.stdout)
    (folder/"native.otool.stderr").write_bytes(otool.stderr)
    final_build=RUN/"build";final_build.mkdir()
    for path in folder.iterdir():
        if path.is_file():shutil.copyfile(path,final_build/path.name)
    need(BINARY.is_file() and sha(BINARY)==sha(attempt_binary),"final binary custody copy differs")
    final_receipt={**attempt_receipt,"schema":"crypto.autoresearch.pair_reuse_build.v1",
        "attempt_path":attempt.relative_to(REPO).as_posix(),"attempt_receipt_sha256":sha(attempt/"build_receipt.json"),
        "binary_sha256":sha(BINARY),"finalized_after_success":True}
    atomic_json(RUN/"build_receipt.json",final_receipt)
    base=json.loads(BASE.read_text())
    atomic_json(RUN/"base_manifest.json",{"schema":"crypto.autoresearch.pair_reuse_base_recipe.v1",
        "input_sha256":BASE_SHA,"binding_sha256":sha(BINDINGS),
        "source_snapshot":base["source_snapshot"],"n19_seed_points":base["seed_points"],
        "n19_expected_signed_points":152,"n23_recipe":"native SHA256/halftrace/r-subgroup scan regenerated in every cold job",
        "fresh_native_reconstruction":True})
    atomic_json(RUN/"case_manifest.json",case_manifest())
    closure={"schema":"crypto.autoresearch.pair_reuse_source_closure.v1",
        "task_id":TASK,"run_id":RUN_ID,"source_sha256":source_hashes(),
        "binary_sha256":sha(BINARY),"compiler_sha256":sha(compiler),
        "python_executable_sha256":sha(Path(sys.executable).resolve()),
        "build_receipt_sha256":sha(RUN/"build_receipt.json"),
        "binary_file_sha256":sha(folder/"native.file.stdout"),
        "binary_otool_sha256":sha(folder/"native.otool.stdout"),
        "base_manifest_sha256":sha(RUN/"base_manifest.json"),
        "case_manifest_sha256":sha(RUN/"case_manifest.json"),
        "input_sha256":{"base":BASE_SHA,"schedule":SCHEDULE_SHA,"protocol":PROTOCOL_SHA,
                        "bindings":sha(BINDINGS),"specification":sha(SPEC)},
        "implementation_runtime":{"requested_policy":"executor-implementation","resolved_model_id":"gpt-5.6-sol",
            "reasoning_effort":"high","fallback_used":False,"degraded_used":False,"model_verified":False,
            "amendment_sha256":sha(P/"implementation_runtime_amendment.md"),"amendment_commit":AMENDMENT_COMMIT,
            "dispatch_snapshot":DISPATCH_SNAPSHOT,"claim_commit":CLAIM_COMMIT},
        "prior_stage_a_attempt":{"archive":"experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/stage_a_attempt_01_preserved.tar.gz",
            "archive_sha256":sha(RUN/"stage_a_attempt_01_preserved.tar.gz"),
            "manifest":"experiments/EXP-KIC-d9c828/runs/RUN-KIC-ba86d9/stage_a_attempt_01_manifest.json",
            "manifest_sha256":sha(RUN/"stage_a_attempt_01_manifest.json"),"scientific_processes":0},
        "runtime_interruption":{"path":"research/pair_reuse_20260922/runtime_interruption_01.json",
            "sha256":sha(P/"runtime_interruption_01.json"),"scientific_processes":0},
        "control_processes":0,"checker_processes":0,"benchmark_processes":0}
    atomic_json(RUN/"source_closure.json",closure)
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=REPO,capture_output=True,
                        text=True,check=True).stdout.strip()
    atomic_json(RUN/"environment.json",{"schema":"crypto.autoresearch.pair_reuse_environment.v1",
        "platform":platform.platform(),"machine":platform.machine(),"python":sys.version,
        "python_executable":str(Path(sys.executable).resolve()),
        "python_executable_sha256":sha(Path(sys.executable).resolve()),
        "compiler_version":version.stdout.decode(errors="replace").strip(),
        "native_binary_file":binary_file.stdout.decode(errors="replace").strip(),
        "native_binary_otool_sha256":sha(folder/"native.otool.stdout"),
        "system_dependency_scope":"macOS dyld shared-cache libraries documented by otool; not portable regular-byte custody",
        "build_head":head,"requested_policy":"executor-implementation",
        "resolved_model_id":"gpt-5.6-sol","reasoning_effort":"high","native_authenticated_session":True,
        "implementation_runtime_amendment_sha256":sha(P/"implementation_runtime_amendment.md"),
        "fallback_used":False,"degraded_used":False,"model_verified":False,
        "model_verification_scope":"explicit Coordinator amendment; no fresh serving probe claimed"})
    atomic_json(RUN/"implementation_readiness.json",{
        "schema":"crypto.autoresearch.pair_reuse_readiness.v1",
        "status":"IMPLEMENTATION_BUILD_READY_NO_CONTROL_ADMISSION",
        "source_closure_sha256":sha(RUN/"source_closure.json"),
        "native_binary_sha256":sha(BINARY),
        "case_manifest_sha256":sha(RUN/"case_manifest.json"),
        "holds":{"control":"committed control admission and explicit root launch",
                 "checker":"accepted control and committed checker admission",
                 "benchmark":"accepted checker and committed benchmark admission"},
        "process_plan":{"controls":1,"checkers":1,"native_benchmark":384}})
    print(json.dumps({"status":"implementation_ready_only",
                      "source_closure_sha256":sha(RUN/"source_closure.json"),
                      "binary_sha256":sha(BINARY)},sort_keys=True))
def verify_closure()->dict[str,Any]:
    verify_inputs();closure=json.loads((RUN/"source_closure.json").read_text())
    need(closure["source_sha256"]==source_hashes() and closure["binary_sha256"]==sha(BINARY),
         "source/native binary changed after freeze")
    need(closure["python_executable_sha256"]==sha(Path(sys.executable).resolve()),
         "Python interpreter executable changed")
    for field,name in (("build_receipt_sha256","build_receipt.json"),
                       ("binary_file_sha256","build/native.file.stdout"),
                       ("binary_otool_sha256","build/native.otool.stdout"),
                       ("base_manifest_sha256","base_manifest.json"),
                       ("case_manifest_sha256","case_manifest.json")):
        need(closure[field]==sha(RUN/name),f"custody changed: {name}")
    need(closure["input_sha256"]["bindings"]==sha(BINDINGS) and
         closure["input_sha256"]["specification"]==sha(SPEC),
         "binding/specification hash changed")
    return closure
def verify_admission(path:Path,commit:str,phase:str)->dict[str,Any]:
    need(len(commit)==40 and all(c in "0123456789abcdef" for c in commit),
         "literal full40hex admission commit required")
    verify_closure();relative=path.relative_to(REPO).as_posix()
    need(subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],
        cwd=REPO,capture_output=True,check=False).returncode==0,
        "admission commit not reachable")
    blob=subprocess.run(["git","show",f"{commit}:{relative}"],cwd=REPO,
                        capture_output=True,check=False)
    need(blob.returncode==0 and blob.stdout==path.read_bytes(),
         "admission blob not byte-identical at named commit")
    record=json.loads(blob.stdout)
    need(record.get("status")=="admitted" and record.get("phase")==phase and
         record.get("task_id")==TASK and record.get("run_id")==RUN_ID and
         record.get("source_closure_sha256")==sha(RUN/"source_closure.json"),
         "admission phase/task/source mismatch")
    pinned=[RUN/"source_closure.json",BINARY,RUN/"base_manifest.json",RUN/"case_manifest.json"]
    pinned += [CODE/name for name in SOURCE_FILES]
    for current in pinned:
        item=current.relative_to(REPO).as_posix()
        readback=subprocess.run(["git","show",f"{commit}:{item}"],cwd=REPO,
                                capture_output=True,check=False)
        need(readback.returncode==0 and readback.stdout==current.read_bytes(),
             f"admission commit source/binary blob mismatch: {item}")
    if phase in ("checker","benchmark"):
        for name in CONTROL_FILES:
            need(record.get("control_sha256",{}).get(name)==sha(RUN/name),
                 f"admission control hash mismatch: {name}")
            current=RUN/name
            readback=subprocess.run(["git","show",f"{commit}:{current.relative_to(REPO).as_posix()}"],
                                    cwd=REPO,capture_output=True,check=False)
            need(readback.returncode==0 and readback.stdout==current.read_bytes(),
                 f"admission control blob mismatch: {name}")
        panel_manifest=json.loads((RUN/"panel_files.json").read_text())
        for item in panel_manifest["files"]:
            name=item["path"];current=RUN/name
            need(item["sha256"]==sha(current) and record.get("control_sha256",{}).get(name)==sha(current),
                 f"admission Q-only panel hash mismatch: {name}")
            readback=subprocess.run(["git","show",f"{commit}:{current.relative_to(REPO).as_posix()}"],
                                    cwd=REPO,capture_output=True,check=False)
            need(readback.returncode==0 and readback.stdout==current.read_bytes(),
                 f"admission Q-only panel blob mismatch: {name}")
        need(record.get("control_receipt_sha256")==sha(RUN/"control_receipt.json"),
             "admission control process receipt mismatch")
        control_readback=subprocess.run(["git","show",f"{commit}:{(RUN/'control_receipt.json').relative_to(REPO).as_posix()}"],
                                        cwd=REPO,capture_output=True,check=False)
        need(control_readback.returncode==0 and control_readback.stdout==(RUN/"control_receipt.json").read_bytes(),
             "admission control receipt blob mismatch")
    if phase=="benchmark":
        need(record.get("independent_replay_sha256")==sha(RUN/"independent_replay.json") and
             record.get("checker_receipt_sha256")==sha(RUN/"checker_receipt.json"),
             "benchmark admission independent checker mismatch")
        for name in ("independent_replay.json","checker_receipt.json"):
            current=RUN/name;readback=subprocess.run(["git","show",f"{commit}:{current.relative_to(REPO).as_posix()}"],
                                                     cwd=REPO,capture_output=True,check=False)
            need(readback.returncode==0 and readback.stdout==current.read_bytes(),
                 f"benchmark admission checker blob mismatch: {name}")
    return record
class Sampler:
    class Info(ctypes.Structure):
        _fields_=[("uuid",ctypes.c_ubyte*16)]+[(name,ctypes.c_uint64) for name in
            ("user","system","pkg","interrupt","pageins","wired","resident","footprint",
             "start","exit","child_user","child_system","child_pkg","child_interrupt",
             "child_pageins","child_elapsed","disk_read","disk_write")]
    def __init__(self):
        self.method="unavailable";self.error=None;self.function=None
        if platform.system()=="Darwin":
            try:
                fn=ctypes.CDLL("/usr/lib/libproc.dylib",use_errno=True).proc_pid_rusage
                fn.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p];fn.restype=ctypes.c_int
                self.function=fn;self.method="proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint"
            except Exception as exc:self.error=repr(exc)
    def sample(self,pid:int)->int|None:
        if self.function is None:return None
        info=self.Info()
        if self.function(pid,2,ctypes.byref(info))!=0:
            self.error=f"errno={ctypes.get_errno()}";return None
        return int(info.footprint)
def fresh_env(raw:Path)->dict[str,str]:
    home,temp=raw/"home",raw/"tmp";home.mkdir();temp.mkdir()
    return {"PATH":os.defpath,"HOME":str(home),"TMPDIR":str(temp),
            "LANG":"C","LC_ALL":"C","PYTHONDONTWRITEBYTECODE":"1"}
def child(argv:list[str],raw:Path,watchdog_seconds:int)->dict[str,Any]:
    stdout,stderr=raw/"stdout.log",raw/"stderr.log"
    sampler=Sampler();peak=None;samples=0;watchdog=False;memory=False
    status=usage=None;popen_error=None;wakeup_error=None;registration_race_recovered=False
    env=fresh_env(raw)
    with stdout.open("xb") as so,stderr.open("xb") as se:
        start=time.monotonic_ns();started=utc()
        try:p=subprocess.Popen(argv,cwd=raw,env=env,
                stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                start_new_session=True,close_fds=True)
        except Exception as exc:popen_error=f"{type(exc).__name__}: {exc}"
        if popen_error is None:
            pid,status,usage=os.wait4(p.pid,os.WNOHANG)
            if pid==p.pid:stop=time.monotonic_ns()
            else:
                queue=None
                try:
                    need(platform.system()=="Darwin" and hasattr(select,"kqueue"),
                         "kqueue NOTE_EXIT required for direct-native metrology")
                    queue=select.kqueue()
                    event=select.kevent(p.pid,filter=select.KQ_FILTER_PROC,
                                        flags=select.KQ_EV_ADD|select.KQ_EV_ENABLE,
                                        fflags=select.KQ_NOTE_EXIT)
                    try:pending=queue.control([event],1,0)
                    except OSError as exc:
                        if exc.errno!=errno.ESRCH:raise
                        pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                        if pid!=p.pid:raise
                        stop=time.monotonic_ns();registration_race_recovered=True;pending=[]
                    if pending and all((item.flags&select.KQ_EV_ERROR)!=0 and
                                       item.data==errno.ESRCH for item in pending):
                        pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                        if pid!=p.pid:raise RuntimeError("kqueue ESRCH but owned child still running")
                        stop=time.monotonic_ns();registration_race_recovered=True;pending=[]
                    next_sample=start+50_000_000
                    deadline=start+int(watchdog_seconds*1e9)
                    while not registration_race_recovered:
                        if pending:
                            need(all((item.flags&select.KQ_EV_ERROR)==0 and
                                     (item.fflags&select.KQ_NOTE_EXIT)!=0 for item in pending),
                                 "kqueue returned non-exit/error event")
                            _,status,usage=os.wait4(p.pid,0)
                            stop=time.monotonic_ns();break
                        now=time.monotonic_ns()
                        timeout=max(0,min(next_sample,deadline)-now)/1e9
                        pending=queue.control([],1,timeout)
                        if pending:continue
                        # A timeout can race an exit; reap before assessing a cap.
                        pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                        if pid==p.pid:stop=time.monotonic_ns();break
                        now=time.monotonic_ns()
                        if now>=next_sample:
                            value=sampler.sample(p.pid)
                            next_sample=now+50_000_000
                            if value is not None:
                                samples+=1;peak=value if peak is None else max(peak,value)
                                if value>=CAP:memory=True
                        if now>=deadline:watchdog=True
                        if watchdog or memory:
                            try:os.killpg(p.pid,signal.SIGKILL)
                            except ProcessLookupError:pass
                            _,status,usage=os.wait4(p.pid,0)
                            stop=time.monotonic_ns();break
                except Exception as exc:
                    wakeup_error=f"{type(exc).__name__}: {exc}"
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    _,status,usage=os.wait4(p.pid,0)
                    stop=time.monotonic_ns()
                finally:
                    if queue is not None:queue.close()
            p.returncode=os.waitstatus_to_exitcode(status)
        else:stop=time.monotonic_ns()
        so.flush();se.flush();os.fsync(so.fileno());os.fsync(se.fileno())
    telemetry=(usage is not None and usage.ru_maxrss>0 and
               all(math.isfinite(v) and v>=0 for v in (usage.ru_utime,usage.ru_stime)))
    return {"argv":argv,"started_at":started,"ended_at":utc(),
        "wall_seconds":(stop-start)/1e9,
        "exit_code":os.waitstatus_to_exitcode(status) if status is not None else None,
        "wait4":{"user_seconds":usage.ru_utime if usage else None,
                 "system_seconds":usage.ru_stime if usage else None,
                 "peak_rss":usage.ru_maxrss if usage else None,
                 "rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent"},
        "telemetry_valid":telemetry,
        "sampling":{"method":sampler.method,"samples":samples,"peak_bytes":peak,
                    "continuous_bound":False,"error":sampler.error},
        "watchdog_reached":watchdog,"memory_cap_reached":memory,
        "watchdog_limit_seconds":watchdog_seconds,"popen_error":popen_error,
        "wakeup_method":"Darwin kqueue NOTE_EXIT with ESRCH fast-exit wait4 recovery",
        "registration_race_recovered":registration_race_recovered,
        "wakeup_error":wakeup_error,
        "stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),
        "primary_timing_scope":"direct native Popen launch to sole wait4 reap; parent fsync/hash/validation excluded"}

def phase_archive(phase:str,partial:bool=False,count:int=0)->None:
    root=RUN/"raw"/phase
    files=sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:p.as_posix())
    stem=f"raw_{phase}_partial_{count:03d}" if partial else f"raw_{phase}"
    archive=RUN/(stem+"_outputs.tar.gz");manifest=RUN/(stem+"_manifest.json")
    need(not archive.exists() and not manifest.exists(),"phase raw archive already frozen")
    normalized_tar([(p,p.relative_to(RUN).as_posix()) for p in files],archive)
    atomic_json(manifest,{"schema":"crypto.autoresearch.pair_reuse_phase_raw.v1",
        "phase":phase,"partial":partial,"launched_receipts":count,
        "files":[{"path":p.relative_to(RUN).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files],
        "archive_sha256":sha(archive)})
def aggregate_raw()->None:
    files=sorted((p for p in (RUN/"raw").rglob("*") if p.is_file()),key=lambda p:p.as_posix())
    need(not (RUN/"raw_outputs.tar.gz").exists() and not (RUN/"raw_manifest.json").exists(),
         "aggregate raw archive already frozen")
    normalized_tar([(p,p.relative_to(RUN).as_posix()) for p in files],RUN/"raw_outputs.tar.gz")
    atomic_json(RUN/"raw_manifest.json",{"schema":"crypto.autoresearch.pair_reuse_raw.v1",
        "files":[{"path":p.relative_to(RUN).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)} for p in files],
        "archive_sha256":sha(RUN/"raw_outputs.tar.gz")})
def run_control()->None:
    raw=RUN/"raw/control";need(raw.is_dir() and (raw/"launch.json").is_file(),"control launch slot absent")
    argv=[str(BINARY),"--control",str(BASE),str(raw)]
    observation=child(argv,raw,LIMIT["control"])
    required=[raw/name for name in CONTROL_FILES]
    panel_paths=sorted((raw/"panels").glob("*.json")) if (raw/"panels").is_dir() else []
    valid=(observation["exit_code"]==0 and observation["telemetry_valid"] and not observation["wakeup_error"] and
           not observation["watchdog_reached"] and not observation["memory_cap_reached"] and
           all(path.is_file() for path in required) and len(panel_paths)==16)
    if valid:
        try:
            parsed=json.loads((raw/"native_controls.json").read_text())
            regimes={row["id"]:row for row in parsed["regimes"]}
            valid=(parsed.get("status")=="passed" and set(regimes)=={"n19_k4","n23_k16"} and
                   regimes["n19_k4"]["base_points"]==152 and regimes["n19_k4"]["expanded_keys"]==11097 and
                   regimes["n19_k4"]["canonical_keys"]==293 and regimes["n23_k16"]["base_points"]==736 and
                   all(row["panel_queries"]==4096 and row["membership_probes"]==4096 for row in regimes.values()))
            manifest=json.loads((raw/"panel_files.json").read_text())
            valid=valid and len(manifest["files"])==16 and all(
                (raw/item["path"]).is_file() and sha(raw/item["path"])==item["sha256"] for item in manifest["files"])
        except Exception:valid=False
    atomic_json(RUN/"control_receipt.json",{"schema":"crypto.autoresearch.pair_reuse_control_receipt.v1",
        "valid":bool(valid),"classification":"completed_valid" if valid else
        "censored_watchdog" if observation["watchdog_reached"] else
        "censored_memory" if observation["memory_cap_reached"] else "failed_process_or_output",
        "outputs":{name:sha(raw/name) for name in CONTROL_FILES if (raw/name).is_file()},
        "panel_outputs":{p.relative_to(raw).as_posix():sha(p) for p in panel_paths},**observation})
    if valid:
        for name in CONTROL_FILES:
            need(not (RUN/name).exists(),f"immutable control output exists: {name}")
            shutil.copyfile(raw/name,RUN/name)
        need(not (RUN/"panels").exists(),"immutable panel output directory exists")
        shutil.copytree(raw/"panels",RUN/"panels")
    phase_archive("control",partial=not valid,count=1)
    need(valid,"native control invalid; checker/benchmark not admitted")
def run_checker()->None:
    raw=RUN/"raw/checker";need(raw.is_dir() and (raw/"launch.json").is_file(),"checker launch slot absent")
    argv=[sys.executable,str(CODE/"checker.py"),"--base",str(BASE),"--run",str(RUN),
          "--output",str(raw/"independent_replay.json")]
    observation=child(argv,raw,LIMIT["checker"]);output=raw/"independent_replay.json"
    valid=(observation["exit_code"]==0 and observation["telemetry_valid"] and not observation["wakeup_error"] and
           not observation["watchdog_reached"] and not observation["memory_cap_reached"] and output.is_file())
    if valid:
        try:
            result=json.loads(output.read_text());regimes={row["regime"]:row for row in result["regimes"]}
            valid=(result.get("status")=="passed" and set(regimes)=={"n19_k4","n23_k16"} and
                   all(row["panel_queries"]==4096 and row["membership_probes"]==4096 for row in regimes.values()) and
                   regimes["n19_k4"]["expanded_keys"]==11097 and regimes["n19_k4"]["canonical_keys"]==293)
        except Exception:valid=False
    atomic_json(RUN/"checker_receipt.json",{"schema":"crypto.autoresearch.pair_reuse_checker_receipt.v1",
        "valid":bool(valid),"classification":"completed_valid" if valid else
        "censored_watchdog" if observation["watchdog_reached"] else
        "censored_memory" if observation["memory_cap_reached"] else "failed_process_or_output",
        "result_sha256":sha(output) if output.is_file() else None,**observation})
    if valid:
        need(not (RUN/"independent_replay.json").exists(),"checker output already frozen")
        shutil.copyfile(output,RUN/"independent_replay.json")
    phase_archive("checker",partial=not valid,count=1)
    need(valid,"independent checker invalid; benchmark not admitted")
def regime_docs()->tuple[dict,dict,dict]:
    public=json.loads((RUN/"public_panels.json").read_text())
    queries=json.loads((RUN/"control_queries.json").read_text())
    tables=json.loads((RUN/"pair_tables.json").read_text())
    return ({r["id"]:r for r in public["regimes"]},{r["id"]:r for r in queries["regimes"]},
            {r["id"]:r for r in tables["regimes"]})
def validate_witness(regime:str,q:tuple[int,int],answer:dict,points:set[checker.Point],third:checker.Point)->None:
    witness=answer.get("witness")
    need(isinstance(witness,list) and len(witness)==3,"SAT query has no exact three-point witness")
    got=tuple(tuple(row) for row in witness);checker.configure(regime)
    need(all(row in points and checker.oncurve(row) for row in got) and got[2]==third,
         "native benchmark witness outside actual B or not first-hit third")
    need(checker.add(checker.add(got[0],got[1]),got[2])==q,"native benchmark group identity invalid")
def run_benchmark()->None:
    scheduled=json.loads((RUN/"case_manifest.json").read_text())["jobs"]
    panels,control_queries,tables=regime_docs();recipe=json.loads(BASE.read_text());base_cache={}
    table_counts={regime:{"expanded":block["expanded"]["stats"]["keys"],
                          "canonical_normal_x":block["canonical_normal_x"]["stats"]["keys"]}
                  for regime,block in tables.items()}
    path=RUN/"benchmark_receipts.jsonl";need(not path.exists(),"benchmark receipt sequence already exists; no retry")
    started=time.monotonic()
    for case in scheduled:
        verify_closure()
        if time.monotonic()-started>=7200:
            phase_archive("benchmark",partial=True,count=len(rows(path)));analyze.analyze(RUN)
            raise TimeoutError("benchmark parent 7200s watchdog checkpoint")
        regime=case["regime"];panel=case["panel"];m=case["M"]
        panel_path=RUN/"panels"/f"{regime}_panel_{panel}.json"
        raw=RUN/"raw/benchmark"/f"{case['ordinal']:03d}_{regime}_M{m}_p{panel}_r{case['repeat']}_{case['arm']}"
        need(not raw.exists(),"benchmark native worker slot already exists");raw.mkdir(parents=True)
        output=raw/"result.json"
        argv=[str(BINARY),"--job",regime,str(BASE),str(panel_path),str(panel),str(m),case["arm"],str(output)]
        observed=child(argv,raw,LIMIT["benchmark"])
        parent_start=time.monotonic_ns();error=observed["popen_error"];result=timing=None
        if output.is_file():
            try:result=json.loads(output.read_text())
            except Exception as exc:error=error or f"malformed native result: {exc}"
        timing_path=raw/"result.json.timing.json"
        if timing_path.is_file():
            try:timing=json.loads(timing_path.read_text())
            except Exception as exc:error=error or f"malformed output timing receipt: {exc}"
        valid=False
        if (not error and not observed["wakeup_error"] and not observed["watchdog_reached"] and
            not observed["memory_cap_reached"] and observed["exit_code"]==0 and observed["telemetry_valid"]):
            try:
                need(result is not None and timing is not None,"native result/output-stage timing absent")
                need(result.get("status")=="completed" and result.get("regime")==regime and result.get("panel")==panel and
                     result.get("M")==m and result.get("arm")==case["arm"],"native job identity differs")
                answers=result.get("queries");need(isinstance(answers,list) and len(answers)==m,"native did not process exact M queries")
                expected_q=[tuple(q) for q in panels[regime]["panels"][panel][:m]]
                expected_rows=control_queries[regime]["panels"][panel][:m]
                checker.configure(regime)
                if regime not in base_cache:base_cache[regime]=checker.base_from_recipe(recipe)[0]
                points=set(base_cache[regime])
                for index,(saved,q,oracle) in enumerate(zip(answers,expected_q,expected_rows)):
                    answer=saved.get("result") or {}
                    need(saved.get("index")==index and tuple(saved.get("Q",()))==q,"native query identity/order differs")
                    expected=oracle[case["arm"]]
                    need(answer.get("status")==expected["status"] and answer.get("third_index")==expected["third_index"] and
                         answer.get("probes")==expected["probes"],"native query status/first-hit differs from control")
                    if answer["status"]=="SAT":
                        validate_witness(regime,q,answer,points,base_cache[regime][answer["third_index"]])
                    else:need(answer.get("witness") is None and answer["third_index"]==-1 and
                              answer["probes"]==len(base_cache[regime]),"UNSAT query is not exhaustive")
                need(result.get("table",{}).get("keys")==table_counts[regime][case["arm"]],"native table key count differs")
                stages=result.get("stages") or {}
                required=("input_read_seconds","base_construction_validation_seconds","public_Q_validation_seconds",
                          "normal_basis_and_nibble_prep_seconds","table_build_seconds","all_queries_transport_replay_seconds")
                need(all(isinstance(stages.get(k),(int,float)) and math.isfinite(stages[k]) and stages[k]>=0 for k in required),
                     "required native stage timing absent/nonfinite")
                need(all(isinstance(timing.get(k),(int,float)) and math.isfinite(timing[k]) and timing[k]>=0 for k in
                         ("serialization_seconds","result_write_seconds","process_observed_until_timing_file_seconds")),
                     "native output timing absent/nonfinite/negative")
                need(isinstance(observed["wall_seconds"],(int,float)) and math.isfinite(observed["wall_seconds"]) and
                     observed["wall_seconds"]>0,"primary wall nonfinite/nonpositive")
                valid=True
            except Exception as exc:error=f"{type(exc).__name__}: {exc}"
        elif error is None and not (observed["watchdog_reached"] or observed["memory_cap_reached"]):
            error="native process exit or wait4 telemetry invalid"
        classification=("completed_valid" if valid else "censored_watchdog" if observed["watchdog_reached"] else
                        "censored_memory" if observed["memory_cap_reached"] else "failed_process_or_identity")
        receipt={"schema":"crypto.autoresearch.pair_reuse_benchmark_receipt.v1",
            **{k:case[k] for k in ("ordinal","block","regime","M","panel","repeat","arm")},
            "valid":valid,"classification":classification,"error":error,
            "result_sha256":sha(output) if output.is_file() else None,
            "output_timing_sha256":sha(timing_path) if timing_path.is_file() else None,
            "result":result,"output_timing":timing,
            "parent_validation_seconds":(time.monotonic_ns()-parent_start)/1e9,**observed}
        append_jsonl(path,receipt)
        print(json.dumps({"ordinal":case["ordinal"],"classification":classification,
                          "wall_seconds":observed["wall_seconds"]},sort_keys=True),flush=True)
        if not valid:
            phase_archive("benchmark",partial=True,count=len(rows(path)));analyze.analyze(RUN)
            raise RuntimeError(f"benchmark slot {case['ordinal']} invalid/censored: {error}")
    need(len(rows(path))==384,"benchmark job count mismatch")
    phase_archive("benchmark",count=384);finalize()
def finalize()->None:
    receipts=rows(RUN/"benchmark_receipts.jsonl");analysis_result=analyze.analyze(RUN);aggregate_raw()
    control=json.loads((RUN/"control_receipt.json").read_text());independent=json.loads((RUN/"checker_receipt.json").read_text())
    commands=[json.loads((RUN/"raw"/phase/"launch.json").read_text())["argv"] for phase in ("control","checker","benchmark")]
    commands.extend([control["argv"],independent["argv"]]);commands.extend(row["argv"] for row in receipts)
    (RUN/"command.txt").write_text("".join(json.dumps(row,separators=(",",":"))+"\n" for row in commands))
    raw_streams=[RUN/"raw/control/stdout.log",RUN/"raw/checker/stdout.log"]
    raw_streams.extend(RUN/"raw/benchmark"/f"{row['ordinal']:03d}_{row['regime']}_M{row['M']}_p{row['panel']}_r{row['repeat']}_{row['arm']}"/"stdout.log" for row in receipts)
    (RUN/"stdout.log").write_bytes(b"".join(path.read_bytes() for path in raw_streams if path.is_file()))
    (RUN/"stderr.log").write_bytes(b"".join(path.with_name("stderr.log").read_bytes()
        for path in raw_streams if path.with_name("stderr.log").is_file()))
    atomic_json(RUN/"raw-result.json",{"schema":"crypto.autoresearch.pair_reuse_raw_result.v1",
        "analysis_sha256":sha(RUN/"analysis.json"),"benchmark_receipts_sha256":sha(RUN/"benchmark_receipts.jsonl"),
        "control_receipt_sha256":sha(RUN/"control_receipt.json"),"checker_receipt_sha256":sha(RUN/"checker_receipt.json"),
        "launched":len(receipts),"valid":sum(row["valid"] for row in receipts),
        "all384_valid":analysis_result["all384_complete_valid"]})
    commit=json.loads((RUN/"raw/control/launch.json").read_text())["admission_commit"]
    dirty=subprocess.run(["git","status","--porcelain","--",str(EXP.relative_to(REPO))],
                         cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
    manifest={"run":{"id":RUN_ID,"experiment_id":"EXP-KIC-d9c828",
        "status":"completed_valid" if analysis_result["all384_complete_valid"] else "completed_censored_or_partial",
        "code":{"commit":commit,"source_sha256":source_hashes(),"binary_sha256":sha(BINARY),
                "command":commands,"dirty_scope_at_finalize":dirty},
        "environment":{"path":"environment.json","sha256":sha(RUN/"environment.json")},
        "inputs":{"parameters":{"regimes":["n19_k4","n23_k16"],"M":[1,32,512],"panels":8,
                                 "technical_repeats":4,"native_workers":384},
                  "base_sha256":BASE_SHA,"schedule_sha256":SCHEDULE_SHA,"protocol_sha256":PROTOCOL_SHA},
        "timing":{"primary_scope":"each direct native Popen launch to sole wait4 reap",
                  "input_scope":"one frozen 512-Q regime/panel file read in full for every M and arm",
                  "root_supervisor_validation_archive":"separate measured cost"},
        "result":{"analysis_sha256":sha(RUN/"analysis.json"),"all384_valid":analysis_result["all384_complete_valid"],
                  "certificate":{"kind":"finite point decomposition replay" if analysis_result["all384_complete_valid"] else "none",
                                 "verified":analysis_result["all384_complete_valid"],
                                 "verifier":"independent_replay.json plus every native job group replay"}},
        "artifacts":{"command":"command.txt","environment":"environment.json","stdout":"stdout.log",
                     "stderr":"stderr.log","raw_result":"raw-result.json","streams_scope":"byte-exact child streams"}}}
    (RUN/"manifest.yaml").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    (RUN/"execution_report.md").write_text(
        f"# {RUN_ID} execution report\n\nFinite public-synthetic pair-table reuse only. "
        f"One native control, one independent checker, and {len(receipts)} cold native job receipts are retained. "
        f"Analysis SHA-256: {sha(RUN/'analysis.json')}. "
        "The Executor makes no full-IC, rho, asymptotic, private-key, security, novelty, or research-status claim.\n\n"
        "Implementation provenance: the interrupted prior Stage-A source/build attempt is preserved at "
        "`stage_a_attempt_01_preserved.tar.gz` with `stage_a_attempt_01_manifest.json`; it launched zero scientific "
        "processes. The later inference-capacity interruption is recorded at "
        "`research/pair_reuse_20260922/runtime_interruption_01.json`; it also launched zero scientific processes.\n")
def run_phase(phase:str,path:Path,commit:str)->None:
    RUN.mkdir(parents=True,exist_ok=True)
    with (RUN/"parent.lock").open("a+") as lock:
        try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError("another parent owns phase launch lock")
        raw=RUN/"raw"/phase;need(not raw.exists(),"phase raw slot already exists; no retry")
        if phase=="checker":need(json.loads((RUN/"control_receipt.json").read_text())["valid"],"native controls not valid")
        if phase=="benchmark":
            need(json.loads((RUN/"control_receipt.json").read_text())["valid"],"native controls not valid")
            need(json.loads((RUN/"checker_receipt.json").read_text())["valid"],"independent checker not valid")
        verify_admission(path,commit,phase);raw.mkdir(parents=True)
        atomic_json(raw/"launch.json",{"schema":"crypto.autoresearch.pair_reuse_launch.v1","phase":phase,
            "admission_commit":commit,"admission_path":path.relative_to(REPO).as_posix(),
            "argv":[sys.executable,*sys.argv],"started_at":utc()})
        if phase=="control":run_control()
        elif phase=="checker":run_checker()
        else:run_benchmark()
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--phase",choices=("build","control","checker","benchmark"),required=True)
    p.add_argument("--admission");p.add_argument("--admission-commit");args=p.parse_args()
    if args.phase=="build":build();return
    need(args.admission and args.admission_commit,"exact root-named committed phase admission required")
    run_phase(args.phase,Path(args.admission).resolve(),args.admission_commit)
if __name__=="__main__":main()
