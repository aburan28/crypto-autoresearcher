#!/usr/bin/env python3
"""One fresh N7 target pipeline; never accepts a target scalar."""
from __future__ import annotations
import argparse,ctypes,hashlib,json,os,platform,resource,signal,subprocess,time,traceback
from pathlib import Path
from typing import Any
import field,circuits,checker

SOLVER_ARGS=("--threads","1","--random","0","--verb","1","--maxtime","30","--maxconfl","1000000")
CAP=8*1024**3

def sha(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
class Sampler:
    class Info(ctypes.Structure):
        _fields_=[("uuid",ctypes.c_ubyte*16)]+[(name,ctypes.c_uint64) for name in (
            "user","system","pkg","interrupt","pageins","wired","resident","footprint","start","exit","child_user","child_system","child_pkg","child_interrupt","child_pageins","child_elapsed","disk_read","disk_write")]
    def __init__(self):
        self.method="unavailable";self.function=None;self.error=None
        if platform.system()!="Darwin":return
        try:
            fn=ctypes.CDLL("/usr/lib/libproc.dylib",use_errno=True).proc_pid_rusage
            fn.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_void_p];fn.restype=ctypes.c_int
            self.function=fn;self.method="proc_pid_rusage.RUSAGE_INFO_V2.ri_phys_footprint"
        except Exception as exc:self.error=repr(exc)
    def sample(self,pid:int)->int|None:
        if self.function is None:return None
        info=self.Info()
        if self.function(pid,2,ctypes.byref(info))!=0:self.error=f"errno={ctypes.get_errno()}";return None
        return int(info.footprint)
def cms_run(binary:Path,instance:Path,cwd:Path)->dict[str,Any]:
    stdout=cwd/"cms.stdout";stderr=cwd/"cms.stderr";sampler=Sampler();peak=None;samples=0;outer_peak=None;outer_samples=0;cap=False
    argv=[str(binary),*SOLVER_ARGS,str(instance.name)]
    with stdout.open("xb") as so,stderr.open("xb") as se:
        # The outer worker owns a fresh process group. CMS stays in that group
        # so the outer watchdog can terminate both processes together.
        start=time.monotonic_ns();p=subprocess.Popen(argv,cwd=cwd,stdin=subprocess.DEVNULL,stdout=so,stderr=se,start_new_session=False,close_fds=True)
        last=0
        while True:
            pid,status,usage=os.wait4(p.pid,os.WNOHANG)
            if pid==p.pid:stop=time.monotonic_ns();break
            now=time.monotonic_ns()
            if now-last>=50_000_000:
                v=sampler.sample(p.pid);self_v=sampler.sample(os.getpid());last=now
                if v is not None:samples+=1;peak=v if peak is None else max(peak,v)
                if self_v is not None:outer_samples+=1;outer_peak=self_v if outer_peak is None else max(outer_peak,self_v)
                if v is not None and self_v is not None and v+self_v>=CAP:
                    cap=True
                    try:os.kill(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
            if cap:_,status,usage=os.wait4(p.pid,0);stop=time.monotonic_ns();break
            time.sleep(.001)
        p.returncode=os.waitstatus_to_exitcode(status);so.flush();se.flush();os.fsync(so.fileno());os.fsync(se.fileno())
    return {"argv":argv,"exit_code":p.returncode,"wall_seconds":(stop-start)/1e9,"wait4_user_seconds":usage.ru_utime,"wait4_system_seconds":usage.ru_stime,"wait4_peak_rss":usage.ru_maxrss,"wait4_peak_rss_unit":"bytes" if platform.system()=="Darwin" else "platform-dependent","stdout_sha256":sha(stdout),"stderr_sha256":sha(stderr),"sampling":{"method":sampler.method,"child_samples":samples,"child_peak_bytes":peak,"worker_samples":outer_samples,"worker_peak_bytes":outer_peak,"sampled_simultaneous_upper_bytes":(peak+outer_peak if peak is not None and outer_peak is not None else None),"error":sampler.error,"cap_reached":cap},"timeout":"CMS --maxtime 30 is internal; no child wall kill"}
def construct_base(recipe:str)->dict:
    if recipe=="candidate":return field.select_candidate()
    if recipe=="null":
        candidate=field.select_candidate()
        return field.select_null(candidate["orbit_representatives"])
    if recipe=="small":
        g=field.generator();assert g is not None
        pts=sorted((g,field.neg(g)),key=field.point_key)
        return {"points":[list(p) for p in pts],"x_values":[g[0]],"recipe":"small"}
    raise ValueError("unknown base recipe")
def run_task(task:dict[str,Any],cwd:Path,input_started_ns:int|None=None)->dict[str,Any]:
    stages={name:{"state":"not_run"} for name in ("input_validation","base_construction","shortcut_check_and_verify","direct_mitm_construction_query_and_verify","circuit_build_and_serialization","cms_solve","model_decode_and_independent_verification")}
    began=time.monotonic_ns() if input_started_ns is None else input_started_ns
    if "scalar" in task or "target_scalar" in task:raise ValueError("worker input must not include known scalar")
    arm=task["arm"];q=tuple(task["Q"]);assert field.on_curve(q) and field.scalar_mul(q,71) is None
    stages["input_validation"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    began=time.monotonic_ns()
    base=construct_base(task["base_recipe"]);points=checker.base_points(base)
    stages["base_construction"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    result={"arm":arm,"Q":list(q),"base_recipe":task["base_recipe"],"base_points":len(points),"base_x_values":len(base["x_values"]),"cms":None,"shortcut":False,"stages":stages}
    began=time.monotonic_ns()
    if q in points:
        p=points[0];witness=(q,p,field.neg(p));result.update(status="SAT",witness=[list(p) for p in witness],shortcut=True,shortcut_kind="Q_P_NEG_P")
        assert checker.check_witness(q,base,result["witness"])
        stages["shortcut_check_and_verify"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
        return result
    stages["shortcut_check_and_verify"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    if arm=="direct_mitm":
        began=time.monotonic_ns()
        witness=field.direct_mitm(q,points)
        result.update(status="SAT" if witness else "UNSAT",witness=[list(p) for p in witness] if witness else None,shortcut=False)
        if witness:assert checker.check_witness(q,base,result["witness"])
        stages["direct_mitm_construction_query_and_verify"]={"state":"measured_combined","seconds":(time.monotonic_ns()-began)/1e9,"includes":"unordered pair sums, batched inversions, Q-minus-base queries, exact lookup and group replay"}
        return result
    began=time.monotonic_ns()
    circuit=circuits.Circuit();details=circuit.relation(base,q,arm)
    instance=cwd/"INSTANCE.cnf";instance.write_text(circuit.dimacs())
    manifest=circuit.manifest();(cwd/"INSTANCE.manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    stages["circuit_build_and_serialization"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    binary=Path(task["solver_path"]);expected=task["solver_sha256"]
    if sha(binary)!=expected:raise ValueError("solver snapshot binary hash mismatch")
    cms=cms_run(binary,instance,cwd)
    stages["cms_solve"]={"state":"measured","seconds":cms["wall_seconds"],"scope":"owned CMS child launch-to-wait4-reap"}
    (cwd/"cms_receipt.json").write_text(json.dumps(cms,sort_keys=True,indent=2)+"\n")
    result["cms"]=cms;result["instance"]={**details,"cnf_sha256":sha(instance),"manifest_sha256":sha(cwd/"INSTANCE.manifest.json")}
    stdout=(cwd/"cms.stdout").read_text(errors="replace")
    if cms["sampling"]["cap_reached"]:
        result.update(status="UNKNOWN",witness=None);return result
    if cms["exit_code"]==10:
        began=time.monotonic_ns()
        assignment=checker.assignment_from_cms(stdout,circuit.nvars)
        witness=checker.decode_model(circuit,assignment,q,base)
        result.update(status="SAT",witness=[list(p) for p in witness],model_sha256=hashlib.sha256(json.dumps(assignment,sort_keys=True).encode()).hexdigest())
        if not checker.check_witness(q,base,result["witness"]):
            raise ValueError("SAT witness failed common independent final group checker")
        stages["model_decode_and_independent_verification"]={"state":"measured","seconds":(time.monotonic_ns()-began)/1e9}
    elif cms["exit_code"]==20:result.update(status="UNSAT",witness=None)
    elif cms["exit_code"]==0:result.update(status="UNKNOWN",witness=None)
    else:raise RuntimeError(f"unexpected CMS exit code or signal: {cms['exit_code']}")
    return result
def main()->None:
    p=argparse.ArgumentParser();p.add_argument("input_json");args=p.parse_args();cwd=Path.cwd()
    try:
        input_started_ns=time.monotonic_ns()
        task=json.loads(Path(args.input_json).read_text())
        result=run_task(task,cwd,input_started_ns);result["worker_self_cpu"]={"user":resource.getrusage(resource.RUSAGE_SELF).ru_utime,"system":resource.getrusage(resource.RUSAGE_SELF).ru_stime}
        (cwd/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        print(json.dumps({"status":result["status"],"arm":result["arm"],"result_sha256":sha(cwd/"result.json")}))
    except Exception as exc:
        failure={"status":"FAILED_IMPLEMENTATION","error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()}
        (cwd/"result.json").write_text(json.dumps(failure,sort_keys=True,indent=2)+"\n")
        raise
if __name__=="__main__":main()
