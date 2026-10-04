#!/usr/bin/env python3
"""One fresh N19 exact-three pipeline; input contains no scalar or coverage cache."""
from __future__ import annotations
import argparse,ctypes,hashlib,json,os,platform,resource,signal,subprocess,time,traceback
from pathlib import Path
from typing import Any
import field,circuits,checker

CMS_FLAGS=("--threads","1","--random","0","--verb","1","--maxtime","2",
           "--maxconfl","1000000")
CAP=8*1024**3

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
class Sampler:
    class Info(ctypes.Structure):
        _fields_=[("uuid",ctypes.c_ubyte*16)]+[(name,ctypes.c_uint64) for name in
            ("user","system","pkg","interrupt","pageins","wired","resident","footprint",
             "start","exit","child_user","child_system","child_pkg","child_interrupt",
             "child_pageins","child_elapsed","disk_read","disk_write")]
    def __init__(self):
        self.method="unavailable";self.function=None;self.error=None
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
def child_run(argv:list[str],cwd:Path,prefix:str)->dict[str,Any]:
    stdout=cwd/(prefix+".stdout");stderr=cwd/(prefix+".stderr")
    sampler=Sampler();samples=0;child_peak=None;parent_peak=None;parent_samples=0;cap=False
    with stdout.open("xb") as so,stderr.open("xb") as se:
        begin=time.monotonic_ns()
        child=subprocess.Popen(argv,cwd=cwd,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                               start_new_session=False,close_fds=True)
        last_sample=0
        while True:
            pid,status,usage=os.wait4(child.pid,os.WNOHANG)
            if pid==child.pid:stop=time.monotonic_ns();break
            now=time.monotonic_ns()
            if now-last_sample>=50_000_000:
                footprint=sampler.sample(child.pid);parent=sampler.sample(os.getpid())
                last_sample=now
                if footprint is not None:
                    samples+=1;child_peak=footprint if child_peak is None else max(child_peak,footprint)
                if parent is not None:
                    parent_samples+=1;parent_peak=parent if parent_peak is None else max(parent_peak,parent)
                if footprint is not None and parent is not None and footprint+parent>=CAP:
                    cap=True
                    try:os.kill(child.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
            if cap:_,status,usage=os.wait4(child.pid,0);stop=time.monotonic_ns();break
            time.sleep(.001)
        child.returncode=os.waitstatus_to_exitcode(status)
        so.flush();se.flush();os.fsync(so.fileno());os.fsync(se.fileno())
    result={"argv":argv,"exit_code":child.returncode,"wall_seconds":(stop-begin)/1e9,
            "wait4_user_seconds":usage.ru_utime,"wait4_system_seconds":usage.ru_stime,
            "wait4_peak_rss":usage.ru_maxrss,
            "wait4_rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent",
            "stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),
            "sampling":{"method":sampler.method,"child_samples":samples,"child_peak_bytes":child_peak,
                        "parent_samples":parent_samples,"parent_peak_bytes":parent_peak,
                        "sum_of_separate_peaks_upper_bytes":child_peak+parent_peak
                         if child_peak is not None and parent_peak is not None else None,
                        "cap_reached":cap,"error":sampler.error,
                        "continuous_bound":False}}
    (cwd/(prefix+".receipt.json")).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    if usage.ru_maxrss<=0 or not all(isinstance(v,(int,float)) and v>=0 for v in
        (usage.ru_utime,usage.ru_stime)):
        raise RuntimeError("missing child wait4 CPU/RSS")
    return result

def run(task:dict[str,Any],cwd:Path,input_started_ns:int)->dict[str,Any]:
    forbidden={"scalar","public_scalar","target_scalar","target_orbit_key",
               "coverage_cache","oracle_status","expected_status","pair_table"}
    if forbidden.intersection(task):raise ValueError("cold worker input contains hidden scalar/oracle/cache")
    case_id=str(task["case_id"]);arm=task["arm"];q=tuple(task["Q"])
    if arm not in ("native_mitm","explicit_onehot","flat_onehot","flat_binary"):
        raise ValueError("unknown arm")
    if not checker.oncurve(q) or checker.times(q,field.R) is not None:
        raise ValueError("invalid public target")
    stages={name:{"state":"not_run"} for name in ("input_validation","base_construction",
            "shortcut_and_verification","circuit_build_and_serialization","child_search",
            "original_rows_and_group_replay")}
    stages["input_validation"]={"state":"measured","seconds":(time.monotonic_ns()-input_started_ns)/1e9}
    started=time.monotonic_ns()
    base_kind=task.get("base_kind")
    if base_kind=="control_small":
        if arm!="explicit_onehot" or task.get("allow_shortcut",False):
            raise ValueError("small control base requires explicit arm and disabled shortcut")
        base=field.construct_control_base(task["base_recipe"])
    elif base_kind=="selected":
        base=(None if arm=="native_mitm" else field.construct_base(task["base_recipe"],normal=True))
    else:raise ValueError("unknown or missing frozen base kind")
    stages["base_construction"]=({"state":"not_run","scope":"native child constructs base within child_search"}
        if base is None else {"state":"measured","seconds":(time.monotonic_ns()-started)/1e9})
    points=(None if base is None else checker.base_points({"points":[list(p) for p in base["points"]]}))
    result={"case_id":case_id,"arm":arm,"base_kind":base_kind,"Q":list(q),"status":None,"witness":None,
            "base_points":152 if base is None else len(points),
            "base_x_values":76 if base is None else len(base["x_values"]),
            "stages":stages,"child":None,"shortcut":False}
    started=time.monotonic_ns()
    q_in_base=(field.in_selected_base(q,task["base_recipe"]) if base is None else q in points)
    if task.get("allow_shortcut",False) and q_in_base:
        p=(tuple(task["base_recipe"]["seed_points"][0]["point"]) if base is None else points[0])
        witness=[list(q),list(p),list(field.neg(p))]
        if base is None:
            if not all(field.in_selected_base(tuple(v),task["base_recipe"]) for v in witness):
                raise ValueError("native shortcut witness outside selected base")
            checker.verify_witness(q,{"points":witness},witness)
        else:checker.verify_witness(q,{"points":[list(v) for v in points]},witness)
        result.update(status="SAT",witness=witness,shortcut=True)
        stages["shortcut_and_verification"]={"state":"measured","seconds":(time.monotonic_ns()-started)/1e9}
        return result
    stages["shortcut_and_verification"]={"state":"measured","seconds":(time.monotonic_ns()-started)/1e9}
    if arm=="native_mitm":
        binary=Path(task["native_path"])
        if sha(binary)!=task["native_sha256"]:raise ValueError("native binary hash mismatch")
        argv=[str(binary),"--solve",str(task["base_path"]),str(q[0]),str(q[1]),
              str(cwd/"native_result.json")]
        child=child_run(argv,cwd,"native")
        result["child"]=child
        stages["child_search"]={"state":"measured","seconds":child["wall_seconds"],
                                "scope":"native child Popen-to-wait4-reap"}
        if child["sampling"]["cap_reached"]:raise RuntimeError("native child memory cap")
        if child["exit_code"]!=0:raise RuntimeError("native child failed")
        raw=json.loads((cwd/"native_result.json").read_text())
        if raw.get("Q")!=list(q):raise ValueError("native result Q mismatch")
        if raw.get("base_points")!=152:raise ValueError("native child base cardinality mismatch")
        result.update(status=raw["status"],witness=raw["witness"],native_details=raw)
        began=time.monotonic_ns()
        if result["status"]=="SAT":
            if not all(field.in_selected_base(tuple(v),task["base_recipe"]) for v in result["witness"]):
                raise ValueError("native witness outside selected base")
            checker.verify_witness(q,{"points":result["witness"]},result["witness"])
        elif result["status"]!="UNSAT":raise ValueError("unexpected native status")
        stages["original_rows_and_group_replay"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    else:
        began=time.monotonic_ns()
        circuit=circuits.Circuit();details=circuit.relation(base,q,arm)
        cnf=cwd/"INSTANCE.cnf";manifest=cwd/"INSTANCE.manifest.json"
        cnf.write_text(circuit.dimacs())
        manifest.write_text(json.dumps(circuit.manifest(),sort_keys=True,indent=2)+"\n")
        stages["circuit_build_and_serialization"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
        binary=Path(task["solver_path"])
        if sha(binary)!=task["solver_sha256"]:raise ValueError("CMS binary hash mismatch")
        child=child_run([str(binary),*CMS_FLAGS,"INSTANCE.cnf"],cwd,"cms")
        result["child"]=child
        result["instance"]={**details,"cnf_sha256":sha(cnf),"manifest_sha256":sha(manifest)}
        stages["child_search"]={"state":"measured","seconds":child["wall_seconds"],
                                "scope":"CMS child Popen-to-wait4-reap; internal --maxtime 2"}
        if child["sampling"]["cap_reached"]:
            result.update(status="UNKNOWN",censor_reason="sampled_memory_cap")
            return result
        stdout=(cwd/"cms.stdout").read_text(errors="replace")
        status,assignment=checker.parse_cms(stdout,child["exit_code"],circuit.nvars)
        result["status"]=status
        if status=="SAT":
            began=time.monotonic_ns()
            witness=checker.decode_sat(circuit,assignment,q,{"points":[list(v) for v in points],
                                                                "x_values":base["x_values"]})
            result["witness"]=[list(p) for p in witness]
            result["model_sha256"]=hashlib.sha256(json.dumps(assignment,sort_keys=True).encode()).hexdigest()
            stages["original_rows_and_group_replay"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
        elif status=="UNKNOWN":
            result["censor_reason"]="CMS_exit_15_INDETERMINATE"
            return result
    return result

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("input_json");args=p.parse_args()
    cwd=Path.cwd();started=time.monotonic_ns()
    try:
        task=json.loads(Path(args.input_json).read_text())
        result=run(task,cwd,started)
        usage=resource.getrusage(resource.RUSAGE_SELF)
        result["worker_self_cpu"]={"user_seconds":usage.ru_utime,"system_seconds":usage.ru_stime}
        (cwd/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        print(json.dumps({"case_id":result["case_id"],"arm":result["arm"],
                          "status":result["status"],"result_sha256":sha(cwd/"result.json")},sort_keys=True))
    except Exception as exc:
        failure={"status":"FAILED_IMPLEMENTATION","error":f"{type(exc).__name__}: {exc}",
                 "traceback":traceback.format_exc()}
        (cwd/"result.json").write_text(json.dumps(failure,sort_keys=True,indent=2)+"\n")
        raise
if __name__=="__main__":main()
