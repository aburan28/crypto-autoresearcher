#!/usr/bin/env python3
"""Admitted one-parent, one-worker N19 SAT pilot supervisor and custody."""
from __future__ import annotations
import argparse,ctypes,datetime as dt,fcntl,gzip,hashlib,json,math,os,platform,resource,shutil,signal,stat,subprocess,sys,tarfile,time,traceback
from pathlib import Path
from typing import Any
import analyze,checker,field,worker

CODE=Path(__file__).resolve().parent
EXP=CODE.parent
REPO=EXP.parents[1]
RUN=EXP/"runs/RUN-KIC-859f34"
BASE=REPO/"research/n19_affine_sat_20260921/inputs/base.json"
CASES=REPO/"research/n19_affine_sat_20260921/inputs/cases.json"
BINDINGS=REPO/"research/n19_affine_sat_20260921/inputs/bindings.json"
PROTOCOL=REPO/"research/n19_affine_sat_20260921/protocol.json"
SPEC=EXP/"specification.yaml"
SOURCE_FILES=("field.py","circuits.py","worker.py","runner.py","checker.py",
              "tests.py","native.cpp","README.md","analyze.py")
NATIVE=RUN/"build/native"
CMS=Path("/opt/homebrew/bin/cryptominisat5")
LIBRARIES=(Path("/opt/homebrew/Cellar/cryptominisat/5.14.7/lib/libcryptominisat5.5.14.dylib"),
           Path("/opt/homebrew/opt/gmp/lib/libgmpxx.4.dylib"),
           Path("/opt/homebrew/opt/gmp/lib/libgmp.10.dylib"))
BASE_SHA="f00b5c5710d041bf862525b5f8d1baf15328e4a9bd6a11f659d300b5ca62cfb1"
CASES_SHA="4c1c05917c85694d7b86f4a7e99a32d1676e585cb0e6a68c89bfd6bfd0508e64"
PROTOCOL_SHA="84861a4b01c544435040847f6ef6efcaa86f852a93f2a0703ce3025655456c40"
TASK="TASK-20260921-52008f"
RUN_ID="RUN-KIC-859f34"
CAP=8*1024**3
ARM_ORDER=("native_mitm","explicit_onehot","flat_onehot","flat_binary")

def require(value:bool,reason:str)->None:
    if not value:raise RuntimeError(reason)
def utc()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def atomic_json(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+".tmp")
    with temp.open("w") as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write("\n")
        stream.flush();os.fsync(stream.fileno())
    os.replace(temp,path)
def append_jsonl(path:Path,value:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("a") as stream:
        stream.write(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n")
        stream.flush();os.fsync(stream.fileno())
def rows(path:Path)->list[dict[str,Any]]:
    return [] if not path.is_file() else [json.loads(line) for line in path.read_text().splitlines() if line]
def code_hashes()->dict[str,str]:return {name:sha(CODE/name) for name in SOURCE_FILES}
def verify_inputs()->None:
    for path,expected in ((BASE,BASE_SHA),(CASES,CASES_SHA),(PROTOCOL,PROTOCOL_SHA)):
        require(path.is_file() and sha(path)==expected,f"frozen input mismatch: {path}")
    require(BINDINGS.is_file() and SPEC.is_file(),"bindings/specification missing")
def normalized_tar(files:list[tuple[Path,str]],destination:Path)->None:
    temp=destination.with_name(destination.name+".tmp")
    with temp.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as zipped:
            with tarfile.open(fileobj=zipped,mode="w",format=tarfile.PAX_FORMAT) as archive:
                for path,name in sorted(files,key=lambda row:row[1]):
                    info=archive.gettarinfo(str(path),arcname=name)
                    info.uid=info.gid=0;info.uname=info.gname="";info.mtime=0
                    info.type=tarfile.REGTYPE;info.linkname=""
                    with path.open("rb") as source:archive.addfile(info,source)
        raw.flush();os.fsync(raw.fileno())
    os.replace(temp,destination)
def dependency_closure()->dict[str,Any]:
    require(CMS.is_file(),"CMS executable missing")
    version=subprocess.run([str(CMS),"--version"],capture_output=True,check=False)
    help_result=subprocess.run([str(CMS),"--help"],capture_output=True,check=False)
    require(b"CryptoMiniSat version 5.14.7" in version.stdout+version.stderr,
            "CMS version differs from 5.14.7")
    for name,payload in (("cms.version.stdout",version.stdout),("cms.version.stderr",version.stderr),
                         ("cms.help.stdout",help_result.stdout),("cms.help.stderr",help_result.stderr)):
        (RUN/name).write_bytes(payload)
    aliases=[CMS,*LIBRARIES];files=[];records=[]
    for index,alias in enumerate(aliases):
        resolved=alias.resolve(strict=True)
        mode=resolved.stat().st_mode
        require(stat.S_ISREG(mode),"CMS payload is not a regular file")
        archive_name=("bin/cryptominisat5" if index==0 else "lib/"+alias.name)
        files.append((resolved,archive_name))
        records.append({"alias":str(alias),"resolved_regular_path":str(resolved),
                        "archive_name":archive_name,"sha256":sha(resolved),
                        "bytes":resolved.stat().st_size,"alias_is_symlink":alias.is_symlink()})
    otools=[]
    for resolved,_ in files:
        result=subprocess.run(["otool","-L",str(resolved)],capture_output=True,check=False)
        require(result.returncode==0,"otool dependency read failed")
        name=f"otool.{len(otools)}.stdout"
        (RUN/name).write_bytes(result.stdout)
        otools.append({"name":name,"sha256":sha(RUN/name),"path":str(resolved)})
    normalized_tar(files,RUN/"solver_snapshot_regular.tar.gz")
    with tarfile.open(RUN/"solver_snapshot_regular.tar.gz","r:gz") as archive:
        for record in records:
            member=archive.getmember(record["archive_name"])
            require(member.isfile() and hashlib.sha256(archive.extractfile(member).read()).hexdigest()==record["sha256"],
                    "regular solver archive payload readback mismatch")
    result={"schema":"crypto.autoresearch.n19_sat_solver_dependency_manifest.v1",
            "version_expected":"5.14.7","reported_source_commit":"GIT-notfound",
            "upstream_source_commit_verified":False,
            "version_exit_code":version.returncode,"help_exit_code":help_result.returncode,
            "version_stdout_sha256":sha(RUN/"cms.version.stdout"),
            "version_stderr_sha256":sha(RUN/"cms.version.stderr"),
            "help_stdout_sha256":sha(RUN/"cms.help.stdout"),
            "help_stderr_sha256":sha(RUN/"cms.help.stderr"),
            "payloads":records,"otool":otools,
            "archive_sha256":sha(RUN/"solver_snapshot_regular.tar.gz"),
            "archive_regular_file_readback":True,
            "system_dependencies":"documented by archived otool outputs; host macOS paths remain host-specific"}
    atomic_json(RUN/"solver_dependency_manifest.json",result)
    return result
def verify_solver()->dict[str,Any]:
    record=json.loads((RUN/"solver_dependency_manifest.json").read_text())
    for item in record["payloads"]:
        path=Path(item["resolved_regular_path"])
        require(path.is_file() and stat.S_ISREG(path.stat().st_mode) and sha(path)==item["sha256"],
                "live resolved solver/dependency payload changed")
        require(Path(item["alias"]).resolve(strict=True)==path,"solver dependency symlink target changed")
    require(sha(RUN/"solver_snapshot_regular.tar.gz")==record["archive_sha256"],
            "solver regular archive changed")
    with tarfile.open(RUN/"solver_snapshot_regular.tar.gz","r:gz") as archive:
        for item in record["payloads"]:
            member=archive.getmember(item["archive_name"])
            require(member.isfile() and hashlib.sha256(archive.extractfile(member).read()).hexdigest()==item["sha256"],
                    "archived regular solver payload changed")
    return record
def manifest_cases()->dict[str,Any]:
    base=json.loads(BASE.read_text());frozen=json.loads(CASES.read_text())
    cases=frozen["cases"]
    require(len(cases)==8 and [c["case_id"] for c in cases]==list(range(1,9)),
            "eight case IDs changed")
    science=[]
    for case in cases:
        require(set(case["arm_order"])==set(ARM_ORDER),"frozen arm rotation invalid")
        for position,arm in enumerate(case["arm_order"],1):
            science.append({"ordinal":len(science)+1,"case_index":case["case_id"],
                "id":f"case-{case['case_id']:02d}-p{position}-{arm}",
                "arm":arm,"position":position,"stratum":case["stratum"],
                "Q":case["Q"],"scalar_driver_only":case["public_scalar"],
                "planned_child":"native" if arm=="native_mitm" else "CMS",
                "base_kind":"selected","allow_shortcut":True})
    ds=[1,2,3,4,5,6,field.R-6,field.R-5,field.R-4,field.R-3,field.R-2,field.R-1]
    controls=[]
    for d in ds:
        q=field.scalar(field.GENERATOR,d)
        require(q is not None,"control Q infinity")
        expected="SAT" if d in (1,3,field.R-3,field.R-1) else "UNSAT"
        controls.append({"ordinal":len(controls)+1,"id":f"control-{len(controls)+1:02d}",
                         "arm":"explicit_onehot","stratum":expected,"Q":list(q),
                         "scalar_driver_only":d,"planned_child":"CMS",
                         "base_kind":"control_small","allow_shortcut":False})
    require(len(science)==32 and len(controls)==12 and
            sum(c["planned_child"]=="CMS" for c in science)==24 and
            sum(c["planned_child"]=="native" for c in science)==8,
            "frozen descendant counts differ")
    return {"schema":"crypto.autoresearch.n19_sat_case_manifest.v1",
            "cases":cases,"science_cases":science,"control_cases":controls,
            "counts":{"native_control_pipeline":1,"external_controls":12,
                      "science_workers":32,"CMS_descendants":36,
                      "native_science_descendants":8},
            "ordering":"case-major exact arm_order from frozen cases.json",
            "scalar_scope":"driver/oracle only; never in cold worker input"}
def build()->None:
    verify_inputs();RUN.mkdir(parents=True,exist_ok=True)
    folder=RUN/"build";folder.mkdir(exist_ok=True)
    require(not NATIVE.exists() and not (RUN/"source_closure.json").exists(),
            "build/source closure already frozen")
    compiler=Path("/usr/bin/clang++")
    version=subprocess.run([str(compiler),"--version"],capture_output=True,check=False)
    (folder/"compiler.version.stdout").write_bytes(version.stdout)
    (folder/"compiler.version.stderr").write_bytes(version.stderr)
    argv=[str(compiler),"-O3","-std=c++20","-DNDEBUG","-Wall","-Wextra","-Wpedantic",
          "-o",str(NATIVE),str(CODE/"native.cpp")]
    before=resource.getrusage(resource.RUSAGE_CHILDREN);started=time.monotonic_ns()
    result=subprocess.run(argv,capture_output=True,check=False,cwd=REPO)
    compile_wall=(time.monotonic_ns()-started)/1e9
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    (folder/"compile.stdout").write_bytes(result.stdout)
    (folder/"compile.stderr").write_bytes(result.stderr)
    atomic_json(RUN/"build_receipt.json",{"schema":"crypto.autoresearch.n19_sat_build_receipt.v1",
        "argv":argv,"exit_code":result.returncode,"wall_seconds":compile_wall,
        "compiler_sha256":sha(compiler),"compiler_version_stdout_sha256":sha(folder/"compiler.version.stdout"),
        "source_sha256":sha(CODE/"native.cpp"),
        "binary_sha256":sha(NATIVE) if NATIVE.is_file() else None,
        "stdout_sha256":sha(folder/"compile.stdout"),"stderr_sha256":sha(folder/"compile.stderr"),
        "compiler_child_cpu_user_delta":after.ru_utime-before.ru_utime,
        "compiler_child_cpu_system_delta":after.ru_stime-before.ru_stime,
        "compiler_child_peak_rss_before":before.ru_maxrss,"compiler_child_peak_rss_after":after.ru_maxrss,
        "cpu_scope":"RUSAGE_CHILDREN delta; high-water RSS values not a per-build difference",
        "native_controls_launched":0,"CMS_instances":0,"science_workers":0})
    require(result.returncode==0 and NATIVE.is_file(),"native compilation failed; receipt retained")
    file_result=subprocess.run(["file",str(NATIVE)],capture_output=True,check=False)
    require(file_result.returncode==0 and b"arm64" in file_result.stdout,
            "native binary not arm64 Mach-O")
    (folder/"native.file.stdout").write_bytes(file_result.stdout)
    (folder/"native.file.stderr").write_bytes(file_result.stderr)
    native_otool=subprocess.run(["otool","-L",str(NATIVE)],capture_output=True,check=False)
    require(native_otool.returncode==0,"native binary dependency inspection failed")
    (folder/"native.otool.stdout").write_bytes(native_otool.stdout)
    (folder/"native.otool.stderr").write_bytes(native_otool.stderr)
    solver=dependency_closure()
    base=json.loads(BASE.read_text())
    atomic_json(RUN/"base_manifest.json",{"schema":"crypto.autoresearch.n19_sat_base_manifest.v1",
        "base_input_sha256":BASE_SHA,"binding_sha256":sha(BINDINGS),
        "source_geometry_snapshot":base["source_snapshot"],
        "plane_key":base["plane_key"],"affine_coordinates":base["affine_coordinates"],
        "seed_points":base["seed_points"],"expected_x_values":76,"expected_signed_points":152,
        "construction":"fresh in every worker; no precomputed points passed to cold workers"})
    atomic_json(RUN/"case_manifest.json",manifest_cases())
    closure={"schema":"crypto.autoresearch.n19_sat_source_closure.v1","task_id":TASK,"run_id":RUN_ID,
        "code_sha256":code_hashes(),"native_binary_sha256":sha(NATIVE),
        "python_executable_sha256":sha(Path(sys.executable).resolve()),
        "compiler_sha256":sha(compiler),"build_receipt_sha256":sha(RUN/"build_receipt.json"),
        "native_otool_sha256":sha(folder/"native.otool.stdout"),
        "solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json"),
        "solver_regular_archive_sha256":sha(RUN/"solver_snapshot_regular.tar.gz"),
        "base_manifest_sha256":sha(RUN/"base_manifest.json"),
        "case_manifest_sha256":sha(RUN/"case_manifest.json"),
        "input_sha256":{"base":BASE_SHA,"cases":CASES_SHA,"bindings":sha(BINDINGS),
                        "protocol":PROTOCOL_SHA,"specification":sha(SPEC)},
        "native_control_processes":0,"CMS_instances":0,"science_workers":0}
    atomic_json(RUN/"source_closure.json",closure)
    head=subprocess.run(["git","rev-parse","HEAD"],cwd=REPO,capture_output=True,text=True,check=True).stdout.strip()
    atomic_json(RUN/"environment.json",{"schema":"crypto.autoresearch.n19_sat_environment.v1",
        "platform":platform.platform(),"machine":platform.machine(),"python":sys.version,
        "python_executable":str(Path(sys.executable).resolve()),
        "python_executable_sha256":sha(Path(sys.executable).resolve()),
        "compiler_version":version.stdout.decode(errors="replace").strip(),
        "native_binary_file":file_result.stdout.decode(errors="replace").strip(),
        "native_otool_sha256":sha(folder/"native.otool.stdout"),
        "native_system_dependencies":"host macOS system libraries in dyld shared cache; otool output archived, no portable-system-byte claim",
        "solver_dependency_manifest_sha256":sha(RUN/"solver_dependency_manifest.json"),
        "execution_head_at_build":head,"requested_policy":"executor-implementation",
        "resolved_model_id":"gpt-5.6-sol","reasoning_effort":"high",
        "fallback_used":False,"degraded_used":False,"model_verified":False})
    atomic_json(RUN/"implementation_readiness.json",{
        "schema":"crypto.autoresearch.n19_sat_implementation_readiness.v1",
        "status":"CODE_BUILD_CUSTODY_READY_NO_NATIVE_OR_SOLVER_ADMISSION",
        "source_closure_sha256":sha(RUN/"source_closure.json"),
        "native_binary_sha256":sha(NATIVE),
        "solver_regular_archive_sha256":sha(RUN/"solver_snapshot_regular.tar.gz"),
        "case_manifest_sha256":sha(RUN/"case_manifest.json"),
        "holds":{"native":"committed root admission and explicit sole launch",
                 "external_controls":"accepted native controls and committed admission",
                 "science":"accepted external controls and committed science admission"}})
    print(json.dumps({"status":"implementation_ready_only",
                      "source_closure_sha256":sha(RUN/"source_closure.json"),
                      "native_binary_sha256":sha(NATIVE),
                      "solver_archive_sha256":solver["archive_sha256"]},sort_keys=True))
def verify_closure()->dict[str,Any]:
    verify_inputs();closure=json.loads((RUN/"source_closure.json").read_text())
    require(closure["code_sha256"]==code_hashes() and closure["native_binary_sha256"]==sha(NATIVE),
            "frozen live code/native binary changed")
    for key,name in (("build_receipt_sha256","build_receipt.json"),
                     ("solver_dependency_manifest_sha256","solver_dependency_manifest.json"),
                     ("solver_regular_archive_sha256","solver_snapshot_regular.tar.gz"),
                     ("base_manifest_sha256","base_manifest.json"),
                     ("case_manifest_sha256","case_manifest.json")):
        require(closure[key]==sha(RUN/name),f"frozen custody changed: {name}")
    require(closure["input_sha256"]["bindings"]==sha(BINDINGS) and
            closure["input_sha256"]["specification"]==sha(SPEC),"binding/specification changed")
    require(closure["python_executable_sha256"]==sha(Path(sys.executable).resolve()),
            "Python interpreter executable changed")
    require(closure["native_otool_sha256"]==sha(RUN/"build/native.otool.stdout"),
            "native dependency readback changed")
    verify_solver()
    return closure
def verify_admission(path:Path,commit:str,phase:str)->dict[str,Any]:
    verify_closure();relative=path.relative_to(REPO).as_posix()
    require(subprocess.run(["git","merge-base","--is-ancestor",commit,"HEAD"],
            cwd=REPO,capture_output=True,check=False).returncode==0,"admission commit not reachable")
    blob=subprocess.run(["git","show",f"{commit}:{relative}"],cwd=REPO,capture_output=True,check=False)
    require(blob.returncode==0 and blob.stdout==path.read_bytes(),
            "admission blob not exact at named commit")
    admission=json.loads(blob.stdout)
    require(admission.get("status")=="admitted" and admission.get("phase")==phase and
            admission.get("task_id")==TASK and admission.get("run_id")==RUN_ID and
            admission.get("source_closure_sha256")==sha(RUN/"source_closure.json"),
            "admission scope/phase/source mismatch")
    pinned=[RUN/"source_closure.json",NATIVE,RUN/"solver_dependency_manifest.json",
            RUN/"solver_snapshot_regular.tar.gz",RUN/"case_manifest.json",RUN/"base_manifest.json"]
    pinned += [CODE/name for name in SOURCE_FILES]
    for current in pinned:
        relative=current.relative_to(REPO).as_posix()
        readback=subprocess.run(["git","show",f"{commit}:{relative}"],
                                cwd=REPO,capture_output=True,check=False)
        require(readback.returncode==0 and readback.stdout==current.read_bytes(),
                f"named-commit readback mismatch: {relative}")
    if phase in ("controls","science"):
        require(admission.get("native_controls_sha256")==sha(RUN/"native_controls.json"),
                "admission native controls mismatch")
    if phase=="science":
        require(admission.get("control_receipts_sha256")==sha(RUN/"control_receipts.jsonl"),
                "admission external controls mismatch")
    return admission

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
def fresh_env(cwd:Path)->dict[str,str]:
    home=cwd/"home";temp=cwd/"tmp";home.mkdir();temp.mkdir()
    return {"PATH":os.defpath,"HOME":str(home),"TMPDIR":str(temp),
            "LANG":"C","LC_ALL":"C","PYTHONDONTWRITEBYTECODE":"1"}
def run_child(argv:list[str],cwd:Path,limit:float)->dict[str,Any]:
    stdout=cwd/"stdout.log";stderr=cwd/"stderr.log"
    sampler=Sampler();peak=None;samples=0;cap=False;watchdog=False
    popen_error=None;usage=status=None
    with stdout.open("xb") as so,stderr.open("xb") as se:
        start=time.monotonic_ns();started=utc()
        try:
            p=subprocess.Popen(argv,cwd=cwd,env=fresh_env(cwd),
                stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                start_new_session=True,close_fds=True)
        except Exception as exc:popen_error=f"{type(exc).__name__}: {exc}"
        if popen_error is None:
            last=0
            while True:
                pid,status,usage=os.wait4(p.pid,os.WNOHANG)
                if pid==p.pid:stop=time.monotonic_ns();break
                now=time.monotonic_ns()
                if now-last>=50_000_000:
                    sample=sampler.sample(p.pid);last=now
                    if sample is not None:
                        samples+=1;peak=sample if peak is None else max(peak,sample)
                        if sample>=CAP:cap=True
                if (now-start)/1e9>=limit:watchdog=True
                if cap or watchdog:
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    _,status,usage=os.wait4(p.pid,0);stop=time.monotonic_ns();break
                time.sleep(.001)
            p.returncode=os.waitstatus_to_exitcode(status)
        else:stop=time.monotonic_ns()
        so.flush();se.flush();os.fsync(so.fileno());os.fsync(se.fileno())
    valid_telemetry=(usage is not None and usage.ru_maxrss>0 and
                     all(math.isfinite(v) and v>=0 for v in (usage.ru_utime,usage.ru_stime)))
    return {"argv":argv,"started_at":started,"ended_at":utc(),
            "wall_seconds":(stop-start)/1e9,
            "exit_code":os.waitstatus_to_exitcode(status) if status is not None else None,
            "wait4":{"user_seconds":usage.ru_utime if usage else None,
                     "system_seconds":usage.ru_stime if usage else None,
                     "peak_rss":usage.ru_maxrss if usage else None,
                     "rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent"},
            "sampling":{"method":sampler.method,"samples":samples,"peak_bytes":peak,
                        "error":sampler.error,"continuous_bound":False},
            "watchdog_reached":watchdog,"memory_cap_reached":cap,
            "telemetry_valid":valid_telemetry,"popen_error":popen_error,
            "stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),
            "timing_scope":"owned Popen launch to wait4 reap; parent fsync/hash excluded"}
def archive_phase(phase:str,partial:bool=False)->None:
    root=RUN/"raw"/phase
    files=sorted((p for p in root.rglob("*") if p.is_file()),key=lambda p:p.as_posix())
    count=(len(rows(RUN/("control_receipts.jsonl" if phase=="controls" else
                         "science_receipts.jsonl"))) if phase!="native" else
           int((RUN/"native_process_receipt.json").is_file()))
    stem=f"raw_{phase}_partial_{count:03d}" if partial else f"raw_{phase}"
    archive=RUN/(stem+"_outputs.tar.gz");manifest=RUN/(stem+"_manifest.json")
    require(not archive.exists() and not manifest.exists(),"phase archive already immutable")
    normalized_tar([(p,p.relative_to(RUN).as_posix()) for p in files],archive)
    atomic_json(manifest,{"schema":"crypto.autoresearch.n19_sat_phase_raw_manifest.v1",
        "phase":phase,"partial":partial,"launched_receipts":count,
        "files":[{"path":p.relative_to(RUN).as_posix(),"bytes":p.stat().st_size,
                  "sha256":sha(p)} for p in files],"archive_sha256":sha(archive)})
def aggregate_raw_archive()->None:
    raw=RUN/"raw";files=sorted((p for p in raw.rglob("*") if p.is_file()),key=lambda p:p.as_posix())
    require(not (RUN/"raw_outputs.tar.gz").exists() and not (RUN/"raw_manifest.json").exists(),
            "aggregate raw archive already immutable")
    normalized_tar([(p,p.relative_to(RUN).as_posix()) for p in files],RUN/"raw_outputs.tar.gz")
    atomic_json(RUN/"raw_manifest.json",{"schema":"crypto.autoresearch.n19_sat_raw_manifest.v1",
        "files":[{"path":p.relative_to(RUN).as_posix(),"bytes":p.stat().st_size,
                  "sha256":sha(p)} for p in files],
        "archive_sha256":sha(RUN/"raw_outputs.tar.gz")})
def input_for(case:dict,phase:str,cwd:Path)->Path:
    solver=verify_solver()
    task={"case_id":case["id"],"arm":case["arm"],"Q":case["Q"],
          "base_kind":case["base_kind"],"base_recipe":json.loads(BASE.read_text()),
          "base_path":str(BASE),"allow_shortcut":case["allow_shortcut"],
          "solver_path":solver["payloads"][0]["resolved_regular_path"],
          "solver_sha256":solver["payloads"][0]["sha256"],
          "native_path":str(NATIVE),"native_sha256":sha(NATIVE)}
    path=cwd/"input.json";path.write_text(json.dumps(task,sort_keys=True,indent=2)+"\n")
    if any(key in task for key in ("scalar","public_scalar","target_scalar","oracle_status",
                                    "expected_status","coverage_cache","pair_table")):
        raise RuntimeError("forbidden cold input field")
    return path
def run_one(case:dict,phase:str)->dict[str,Any]:
    raw=RUN/"raw"/phase/f"{case['ordinal']:03d}_{case['id']}"
    require(not raw.exists(),"immutable worker slot already exists")
    raw.mkdir(parents=True);input_path=input_for(case,phase,raw)
    argv=[sys.executable,str(CODE/"worker.py"),str(input_path)]
    observed=run_child(argv,raw,15)
    result_path=raw/"result.json";result=None;parse_error=None
    if result_path.is_file():
        try:result=json.loads(result_path.read_text())
        except Exception as exc:parse_error=f"{type(exc).__name__}: {exc}"
    parent_validation_start=time.monotonic_ns()
    valid=False;replay=None;error=observed["popen_error"] or parse_error
    outer_watchdog=observed["watchdog_reached"]
    outer_memory=observed["memory_cap_reached"]
    solver_unknown=False
    child_memory=False
    if not error and not outer_watchdog and not outer_memory and observed["exit_code"]==0 and result is not None:
        try:
            require(result.get("case_id")==case["id"] and result.get("arm")==case["arm"] and
                    result.get("Q")==case["Q"] and result.get("base_kind")==case["base_kind"],
                    "worker identity mismatch")
            if result.get("status")=="UNKNOWN":
                child=result.get("child") or {}
                require(case["planned_child"]=="CMS","native child returned UNKNOWN")
                require(child.get("wait4_peak_rss",0)>0 and
                        child.get("wait4_user_seconds") is not None and
                        child.get("wait4_system_seconds") is not None,
                        "UNKNOWN child CPU/RSS receipt missing")
                require(child.get("argv",[None])[0]==verify_solver()["payloads"][0]["resolved_regular_path"],
                        "UNKNOWN child executable differs from pinned CMS")
                instance=result.get("instance") or {}
                require(instance.get("cnf_sha256")==sha(raw/"INSTANCE.cnf") and
                        instance.get("manifest_sha256")==sha(raw/"INSTANCE.manifest.json"),
                        "UNKNOWN original CNF/XOR or variable-map custody missing")
                if (child.get("sampling",{}).get("cap_reached") and
                    result.get("censor_reason")=="sampled_memory_cap"):
                    child_memory=True
                else:
                    require(child.get("exit_code")==15 and
                            result.get("censor_reason")=="CMS_exit_15_INDETERMINATE",
                            "UNKNOWN lacks declared CMS exit15/INDETERMINATE receipt")
                    solver_unknown=True
            else:
                require(result.get("shortcut") is False,"frozen panel unexpectedly used shortcut")
                child=result.get("child") or {}
                require(child.get("wait4_peak_rss",0)>0 and child.get("wait4_user_seconds") is not None and
                        child.get("wait4_system_seconds") is not None,
                        "required CMS/native child wait4 telemetry missing")
                require((case["planned_child"]=="CMS")==(case["arm"]!="native_mitm"),
                        "planned child/arm mismatch")
                expected_child=(verify_solver()["payloads"][0]["resolved_regular_path"]
                                if case["planned_child"]=="CMS" else str(NATIVE))
                require(child.get("argv",[None])[0]==expected_child,
                        "actual child executable differs from frozen planned arm")
                if case["planned_child"]=="CMS":
                    instance=result.get("instance") or {}
                    require(instance.get("cnf_sha256")==sha(raw/"INSTANCE.cnf") and
                            instance.get("manifest_sha256")==sha(raw/"INSTANCE.manifest.json"),
                            "original CNF/XOR or full variable-map custody missing")
                else:
                    require((raw/"native_result.json").is_file() and
                            (result.get("native_details") or {}).get("Q")==case["Q"],
                            "native coordinate result custody missing")
                base=(field.construct_control_base(json.loads(BASE.read_text())) if
                      case["base_kind"]=="control_small" else
                      field.construct_base(json.loads(BASE.read_text()),normal=False))
                replay=checker.replay_result(result,tuple(case["Q"]),
                    {"points":[list(p) for p in base["points"]]},
                    case["stratum"],case["id"],case["arm"])
                valid=bool(replay["valid"])
        except Exception as exc:error=f"{type(exc).__name__}: {exc}"
    elif error is None and not outer_watchdog and not outer_memory:error="worker exit/result invalid"
    if not observed["telemetry_valid"] and error is None:error="missing outer wait4 CPU/RSS"
    if error is not None:solver_unknown=child_memory=outer_watchdog=outer_memory=False;valid=False
    classification=("completed_valid" if valid else "censored_CMS15" if solver_unknown else
                    "censored_CMS_memory" if child_memory else
                    "censored_outer_watchdog" if outer_watchdog else
                    "censored_outer_memory" if outer_memory else
                    "failed_implementation_or_infrastructure")
    return {"schema":"crypto.autoresearch.n19_sat_pipeline_receipt.v1",
            "phase":phase,"ordinal":case["ordinal"],"case_id":case["id"],
            "case_index":case.get("case_index"),"stratum":case["stratum"],
            "arm":case["arm"],"Q":case["Q"],"scalar_driver_only":case["scalar_driver_only"],
            "planned_child":case["planned_child"],"valid":valid,
            "classification":classification,"error":error,
            "censored_reason":(result.get("censor_reason") if (solver_unknown or child_memory) and result else
                               "outer_watchdog" if outer_watchdog else
                               "outer_memory_cap" if outer_memory else None),
            "replay":replay,"worker_result":result,
            "parent_validation_seconds":(time.monotonic_ns()-parent_validation_start)/1e9,
            "argv":argv,"input_sha256":sha(input_path),
            "result_sha256":sha(result_path) if result_path.is_file() else None,
            **observed}
def run_native()->None:
    raw=RUN/"raw/native";require(raw.is_dir() and (raw/"launch.json").is_file(),
                                 "native launch slot absent")
    argv=[sys.executable,str(CODE/"tests.py"),"--base",str(BASE),"--cases",str(CASES),
          "--native",str(NATIVE),"--out",str(raw)]
    receipt=run_child(argv,raw,900)
    result_path=raw/"controls.json"
    valid=(receipt["exit_code"]==0 and receipt["telemetry_valid"] and
           not receipt["watchdog_reached"] and not receipt["memory_cap_reached"] and
           result_path.is_file())
    result=json.loads(result_path.read_text()) if result_path.is_file() else None
    valid=valid and result.get("status")=="passed" and result.get("native_children")==1
    atomic_json(RUN/"native_process_receipt.json",{"phase":"native","valid":valid,**receipt,
        "result_sha256":sha(result_path) if result_path.is_file() else None})
    if valid:
        require(not (RUN/"native_controls.json").exists(),"native controls output exists")
        shutil.copyfile(result_path,RUN/"native_controls.json")
    archive_phase("native",partial=not valid)
    require(valid,"native controls invalid; no later phase authorized")
def run_cells(phase:str)->None:
    manifest=json.loads((RUN/"case_manifest.json").read_text())
    cases=manifest["control_cases"] if phase=="controls" else manifest["science_cases"]
    path=RUN/("control_receipts.jsonl" if phase=="controls" else "science_receipts.jsonl")
    require(not path.exists(),"phase receipts already exist; no automatic resume")
    started=time.monotonic()
    for case in cases:
        verify_closure()
        if time.monotonic()-started>=1200:
            archive_phase(phase,partial=True)
            if phase=="science":analyze.analyze(RUN)
            raise TimeoutError("parent phase watchdog 1200s; partial rows retained")
        receipt=run_one(case,phase)
        append_jsonl(path,receipt)
        print(json.dumps({"phase":phase,"ordinal":case["ordinal"],
                          "case_id":case["id"],"classification":receipt["classification"],
                          "wall_seconds":receipt["wall_seconds"]},sort_keys=True),flush=True)
        if not receipt["valid"] and (phase=="controls" or
                                     receipt["classification"]!="censored_CMS15"):
            archive_phase(phase,partial=True)
            if phase=="science":analyze.analyze(RUN)
            raise RuntimeError(f"frozen {phase} slot invalid: {case['id']}: {receipt['error']}")
    require(len(rows(path))==len(cases),"fixed phase incomplete")
    if phase=="controls":
        actual=sum(bool((r["worker_result"] or {}).get("child")) for r in rows(path))
        require(actual==12 and all(r["valid"] for r in rows(path)),
                "external control CMS count/verdict mismatch")
        atomic_json(RUN/"control_replay.json",{"status":"passed","valid":True,
            "control_receipts_sha256":sha(path),"CMS_children":actual,
            "expected_CMS_children":12})
        archive_phase("controls")
    else:
        observed_rows=rows(path)
        cms_children=sum(r["arm"]!="native_mitm" and bool((r["worker_result"] or {}).get("child"))
                         for r in observed_rows)
        native_children=sum(r["arm"]=="native_mitm" and bool((r["worker_result"] or {}).get("child"))
                            for r in observed_rows)
        if cms_children!=24 or native_children!=8:
            archive_phase("science",partial=True)
            analyze.analyze(RUN)
            raise RuntimeError("full science panel omitted a planned CMS/native child")
        archive_phase("science")
        finalize()
def finalize()->None:
    science=rows(RUN/"science_receipts.jsonl")
    atomic_json(RUN/"cnf_xor_model_manifest.json",{
        "schema":"crypto.autoresearch.n19_sat_cnf_xor_manifest.v1",
        "rows":[{"case_id":r["case_id"],"arm":r["arm"],
                 "instance":(r["worker_result"] or {}).get("instance"),
                 "raw_result_sha256":r.get("result_sha256")} for r in science]})
    atomic_json(RUN/"model_group_replay.json",{
        "schema":"crypto.autoresearch.n19_sat_model_group_replay.v1",
        "all32_present":len(science)==32,
        "all32_valid":len(science)==32 and all(r["valid"] for r in science),
        "science_receipts_sha256":sha(RUN/"science_receipts.jsonl"),
        "rows":[{"case_id":r["case_id"],"replay":r.get("replay"),
                 "classification":r["classification"]} for r in science]})
    analysis_result=analyze.analyze(RUN)
    aggregate_raw_archive()
    controls=rows(RUN/"control_receipts.jsonl")
    actual_control_cms=sum(bool((r["worker_result"] or {}).get("child")) for r in controls)
    actual_science_cms=sum(r["arm"]!="native_mitm" and bool((r["worker_result"] or {}).get("child"))
                           for r in science)
    actual_science_native=sum(r["arm"]=="native_mitm" and bool((r["worker_result"] or {}).get("child"))
                              for r in science)
    phase_paths=[RUN/"raw/native/stdout.log"]
    phase_paths.extend(RUN/"raw/controls"/f"{r['ordinal']:03d}_{r['case_id']}"/"stdout.log"
                       for r in rows(RUN/"control_receipts.jsonl"))
    phase_paths.extend(RUN/"raw/science"/f"{r['ordinal']:03d}_{r['case_id']}"/"stdout.log"
                       for r in science)
    (RUN/"stdout.log").write_bytes(b"".join(path.read_bytes() for path in phase_paths if path.is_file()))
    (RUN/"stderr.log").write_bytes(b"".join(path.with_name("stderr.log").read_bytes()
        for path in phase_paths if path.with_name("stderr.log").is_file()))
    phase_commands=[json.loads((RUN/"raw"/phase/"launch.json").read_text())["argv"]
                    for phase in ("native","controls","science")]
    child_commands=[json.loads((RUN/"native_process_receipt.json").read_text())["argv"]]
    child_commands.extend(r["argv"] for r in rows(RUN/"control_receipts.jsonl"))
    child_commands.extend(r["argv"] for r in science)
    (RUN/"command.txt").write_text("".join(json.dumps({"scope":"root_phase","argv":x},separators=(",",":"))+"\n"
        for x in phase_commands)+"".join(json.dumps({"scope":"cold_child","argv":x},separators=(",",":"))+"\n"
        for x in child_commands))
    atomic_json(RUN/"raw-result.json",{"schema":"crypto.autoresearch.n19_sat_raw_result.v1",
        "analysis_sha256":sha(RUN/"analysis.json"),
        "science_receipts_sha256":sha(RUN/"science_receipts.jsonl"),
        "control_receipts_sha256":sha(RUN/"control_receipts.jsonl"),
        "summary":{"launched_science":len(science),
                   "valid_science":sum(r["valid"] for r in science),
                   "censored_CMS15":sum(r["classification"]=="censored_CMS15" for r in science),
                   "actual_control_CMS_children":actual_control_cms,
                   "planned_control_CMS_children":12,
                   "actual_science_CMS_children":actual_science_cms,
                   "planned_science_CMS_children":24,
                   "actual_science_native_children":actual_science_native,
                   "planned_science_native_children":8,
                   "all32_valid":analysis_result["all32_complete_valid"]}})
    first=json.loads((RUN/"raw/native/launch.json").read_text())["admission_commit"]
    dirty=subprocess.run(["git","status","--porcelain","--",str(EXP.relative_to(REPO))],
                         cwd=REPO,capture_output=True,text=True,check=True).stdout.splitlines()
    manifest={"run":{"id":RUN_ID,"experiment_id":"EXP-KIC-c3c732",
        "status":"completed_valid" if analysis_result["all32_complete_valid"] else "completed_censored_or_partial",
        "code":{"commit":first,"source_sha256":code_hashes(),"native_binary_sha256":sha(NATIVE),
                "dirty_scope_at_finalize":dirty,"command":phase_commands,
                "child_commands":child_commands},
        "environment":{"path":"environment.json","sha256":sha(RUN/"environment.json")},
        "inputs":{"base_sha256":BASE_SHA,"cases_sha256":CASES_SHA,
                  "protocol_sha256":PROTOCOL_SHA,"parameters":{"n":19,"controls":12,
                  "science_workers":32,"SAT_cases":4,"UNSAT_cases":4}},
        "timing":{"worker_wall_scope":"each owned pipeline Popen launch-to-wait4-reap",
                  "supervisor_cost":"root outer supervisor receipts separate; no cache-flush claim"},
        "result":{"analysis_sha256":sha(RUN/"analysis.json"),
                  "complete_valid":analysis_result["all32_complete_valid"],
                  "certificate":{"kind":"decomposition" if analysis_result["all32_complete_valid"] else "none",
                                 "verified":analysis_result["all32_complete_valid"],
                                 "verifier":"model_group_replay.json"}},
        "artifacts":{"command":"command.txt","environment":"environment.json",
                     "stdout":"stdout.log","stderr":"stderr.log","raw_result":"raw-result.json",
                     "stream_scope":"byte-exact concatenation of actual native/control/science child streams in launch order"}}}
    (RUN/"manifest.yaml").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    (RUN/"execution_report.md").write_text(
        f"# {RUN_ID} execution report\n\nFinite public-synthetic N19 SAT diagnostic only.\n\n"
        f"Native controls, 12 external controls and {len(science)} scientific worker receipts are retained. "
        f"Analysis SHA-256: `{sha(RUN/'analysis.json')}`. "
        "The Executor records observations without hypothesis, security or asymptotic status change.\n")
def run_phase(phase:str,admission_path:Path,commit:str)->None:
    RUN.mkdir(parents=True,exist_ok=True)
    with (RUN/"parent.lock").open("a+") as lock:
        try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError("another phase parent owns the launch lock")
        launch=RUN/"raw"/phase/"launch.json"
        require(not launch.exists(),f"{phase} previously launched; no retry")
        if phase=="controls":
            require((RUN/"native_controls.json").is_file(),"native controls not complete")
        if phase=="science":
            control=rows(RUN/"control_receipts.jsonl")
            require(len(control)==12 and all(r["valid"] for r in control),
                    "external controls not fully valid")
        verify_admission(admission_path,commit,phase)
        if phase=="native":
            raw=RUN/"raw/native";raw.mkdir(parents=True)
            atomic_json(raw/"launch.json",{"phase":phase,"admission_commit":commit,
                "argv":[sys.executable,*sys.argv],"started_at":utc()})
            run_native()
        else:
            (RUN/"raw"/phase).mkdir(parents=True,exist_ok=True)
            atomic_json(RUN/"raw"/phase/"launch.json",{
                "phase":phase,"admission_commit":commit,
                "argv":[sys.executable,*sys.argv],"started_at":utc()})
            run_cells(phase)
def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--phase",choices=("build","native","controls","science"),required=True)
    p.add_argument("--admission");p.add_argument("--admission-commit")
    args=p.parse_args()
    if args.phase=="build":build();return
    require(args.admission and args.admission_commit,"exact committed phase admission required")
    run_phase(args.phase,Path(args.admission).resolve(),args.admission_commit)
if __name__=="__main__":main()
