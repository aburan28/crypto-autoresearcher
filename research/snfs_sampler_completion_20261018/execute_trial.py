"""Producer for the frozen sampler-completion trials; observations only."""
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import platform
import resource
import subprocess
import sys
import tarfile
import tempfile
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BIN=Path("/workspace/snfs-toolchains/sampler-target/release")
SAGE=Path("/workspace/snfs-toolchains/sage-pixi/.pixi/envs/default/bin/python")


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle(files,directory):
    index=[]
    with (directory/"instrument.tar.gz").open("xb") as target:
        with gzip.GzipFile(fileobj=target,mode="wb",filename="",mtime=0) as compressed:
            with tarfile.open(fileobj=compressed,mode="w") as archive:
                for path in files:
                    content=path.read_bytes()
                    info=tarfile.TarInfo(path.name);info.size=len(content);info.mode=0o644
                    archive.addfile(info,io.BytesIO(content))
                    index.append(dict(name=path.name,bytes=len(content),sha256=hashlib.sha256(content).hexdigest()))
    return index


def main(mode,directory):
    runtime=json.loads((HERE/"runtime-bindings.json").read_text())
    for binding in runtime.values():
        assert digest(Path(binding["path"]))==binding["sha256"], "runtime binding changed"
    directory=directory.resolve()
    assert directory.is_dir(), "supervisor must create the run directory"
    launch=json.loads((directory/"launch.json").read_text())
    launch_environment=json.loads((directory/"environment.json").read_text())
    dirty_paths=subprocess.check_output(["git","status","--porcelain"],cwd=ROOT,text=True).splitlines()
    run_id=directory.name;experiment=directory.parents[1].name
    assert run_id.startswith("RUN-") and experiment.startswith("EXP-")
    started=time.time();wall=time.monotonic()
    with tempfile.TemporaryDirectory(prefix="snfs-sampler-") as scratch:
        scratch=Path(scratch)
        print(f"instrument scratch: {scratch}",file=sys.stderr,flush=True)
        try:
            if mode=="panel":
                subprocess.run([str(BIN/"fixed_input"),"--panel",str(HERE/"panel.json"),"--out",str(scratch/"instrument")],check=True)
                result=json.loads((scratch/"instrument/panel-result.json").read_text())
                files=sorted((scratch/"instrument").iterdir())
            else:
                subprocess.run([str(BIN/"screen"),"--coefficients",str(HERE/"coefficients.json"),"--out",str(scratch/"source-screen.jsonl")],check=True)
                subprocess.run([str(SAGE),str(HERE/"full_catalog.py"),"--screen",str(scratch/"source-screen.jsonl"),"--out",str(scratch/"support-catalog.json")],check=True)
                result=json.loads((scratch/"support-catalog.json").read_text())
                files=[scratch/"source-screen.jsonl",scratch/"support-catalog.json"]
        except BaseException:
            partial=bundle(sorted(p for p in scratch.rglob("*") if p.is_file()),directory)
            with (directory/"instrument-index.json").open("x") as h:
                json.dump(partial,h,indent=2);h.write("\n")
            print("Partial instrument files preserved; producer failed and no completed raw result was fabricated.",file=sys.stderr,flush=True)
            raise
        index=bundle(files,directory)
    raw=dict(schema="snfs.sampler_completion_trial.v1",experiment_id=experiment,run_id=run_id,mode=mode,data=result)
    with (directory/"raw-result.json").open("x") as h:json.dump(raw,h,indent=2);h.write("\n")
    with (directory/"instrument-index.json").open("x") as h:json.dump(index,h,indent=2);h.write("\n")
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    manifest=dict(run=dict(id=run_id,experiment_id=experiment,status="completed",
        code=dict(commit=launch_environment["commit"],commit_meaning="supervisor_execution_start",
                  command=launch["argv"],dirty=bool(dirty_paths),dirty_paths_at_start=dirty_paths,
                  source_sha256=launch_environment["source_sha256"],
                  head_at_wrapper_end=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()),
        environment=dict(python=platform.python_version(),platform=platform.platform(),point_binary_sha256=digest(BIN/"fixed_input"),screen_binary_sha256=digest(BIN/"screen")),
        inputs=dict(panel_sha256=digest(HERE/"panel.json"),coefficients_sha256=digest(HERE/"coefficients.json")),
        timing=dict(started_unix=started,finished_unix=time.time(),wall_seconds=time.monotonic()-wall,
                    child_cpu_seconds=usage.ru_utime+usage.ru_stime,child_peak_rss_bytes=usage.ru_maxrss*1024),
        result=dict(raw_result="raw-result.json",outcome="observations_recorded",certificate=dict(kind="none"),
                    raw_sha256=digest(directory/"raw-result.json"),instrument_sha256=digest(directory/"instrument.tar.gz"))))
    # JSON is valid YAML and avoids an extra runtime dependency.
    with (directory/"manifest.yaml").open("x") as h:json.dump(manifest,h,indent=2);h.write("\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode",choices=["support","panel"])
    parser.add_argument("--run-dir",type=Path,required=True)
    args=parser.parse_args();main(args.mode,args.run_dir)
