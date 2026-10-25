"""Exercise the real ``experiment_execution.execute_trial`` function in a disposable root."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, sys, tarfile, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"tools")); import experiment_execution
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(mode, capture=None):
    with tempfile.TemporaryDirectory(prefix="icperf-v2-fixture-") as temporary:
        root=Path(temporary); spec=root/"experiments/EXP-ICPERF-fixture"; spec.mkdir(parents=True); (spec/"specification.yaml").write_text("fixture: true\n")
        source={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ("execute.py","check.py","output_contract.py")}
        trial={"id":"fixture-"+mode,"run_id":"RUN-ICPERF-abcdef","argv":[sys.executable,str(HERE/"execute.py"),"--run-dir","{run_dir}","--mode",mode],"check_argv":[sys.executable,str(HERE/"check.py"),"--run-dir","{run_dir}"],"artifacts":["manifest.yaml","raw-result.json"],"allow_empty_artifacts":[],"memory_mb":64,"watchdog_seconds":20,"watchdog_reason":"fixture process bound"}
        plan={"schema":"crypto.autoresearch.trial_plan.v1","experiment_id":"EXP-ICPERF-fixture","task_id":"TASK-20261020-f237a2","specification":"experiments/EXP-ICPERF-fixture/specification.yaml","specification_sha256":"0"*64,"source_sha256":source,"trials":[trial]}
        plan_path=root/"fixture-plan.json"; plan_path.write_text(json.dumps(plan,sort_keys=True)+"\n")
        authority={"owner":"fixture-authority","epoch":1,"commit":"fixture-commit","expires_at":"2999-01-01T00:00:00+00:00"}
        status=experiment_execution.execute_trial(root,plan_path,plan,trial,authority,os.open("/dev/null",os.O_RDONLY)); directory=experiment_execution.run_root(root,plan,trial); receipt=json.loads((directory/"execution-receipt.json").read_text())
        if capture is not None: shutil.copytree(directory, Path(capture)/mode)
        return {"mode":mode,"status":status,"receipt_status":receipt["status"],"artifact_sha256":receipt["artifact_sha256"],"run_id":trial["run_id"]}

def build(out):
    """Materialize custody of both disposable fixture directories, then seal it."""
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="icperf-v2-custody-") as temporary:
        capture=Path(temporary)/"raw"; capture.mkdir()
        results=[run(mode,capture) for mode in ("bounded-censor","canned-positive")]
        tar=out/"fixture-custody.tar.gz"
        with tarfile.open(tar,"w:gz") as archive: archive.add(capture,arcname="raw")
        report={"schema":"icperf-prime63-m2-output-contract-v2-fixture-report-v1","task_id":"TASK-20261020-f237a2","fixture_only":True,"scientific_execution":False,"commands":["fixture_supervisor.run(bounded-censor)","fixture_supervisor.run(canned-positive)"],"supervisor_results":results,"custody_tar_sha256":sha(tar),"source_sha256":{name:sha(HERE/name) for name in ("execute.py","check.py","output_contract.py","fixture_supervisor.py","test_output_contract.py","input_manifest.json","output-contract.json","README.md")},"limits":"Temporary fixture authority is not production admission; no solver or scientific trial was invoked."}
        (out/"fixture-report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--out",type=Path,required=True); args=parser.parse_args(); print(json.dumps(build(args.out),sort_keys=True))
