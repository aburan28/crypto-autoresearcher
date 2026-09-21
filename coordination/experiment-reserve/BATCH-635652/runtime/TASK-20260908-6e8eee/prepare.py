"""Run the claimed, bounded offline dependency preparation protocol."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import yaml

TASK = "TASK-20260908-6e8eee"
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
DOCKER = ["/usr/local/bin/docker", "--host", "unix:///Users/adamburan/.docker/run/docker.sock"]
BASE = "docker.io/library/python@sha256:c89921a0c7b42f27338ed8c279fb370e69e941c92460f91895d08304e844b0b4"
META = REPO / "coordination/experiment-reserve/BATCH-635652/runtime-bindings/DEC-20260908-f39556/dependencies.json"
TAG = "crypto-autoresearcher/bsgs-deps:task-20260908-6e8eee"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    receipt_path = Path(sys.argv[1])
    assert not receipt_path.exists()
    previous = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    if previous is not None:
        assert previous["task_id"] == TASK and previous["status"] == "failed"
    prior_starts = (previous.get("prior_container_start_attempts", 0)
                    + previous["container_start_attempts"]) if previous is not None else 0
    prior_downloads = (previous.get("prior_wheel_download_invocations", 0)
                       + sum(c["argv"][0] == "/usr/bin/curl" for c in previous["commands"])) if previous is not None else 0
    assert prior_starts + 2 <= 4
    assert prior_downloads + 2 <= 4
    transcript = {"task_id": TASK, "started_utc": utc(), "commands": [],
                  "container_start_attempts": 0, "created_containers": [],
                  "prior_container_start_attempts": prior_starts,
                  "prior_wheel_download_invocations": prior_downloads,
                  "scientific_runs": 0, "status": "running", "cleanup": []}
    temporary = tempfile.TemporaryDirectory(prefix=TASK.lower()+"-")
    scratch = Path(temporary.name)

    def run(argv, timeout=240, check=True):
        index = len(transcript["commands"])
        out, err = scratch / f"command-{index}.stdout", scratch / f"command-{index}.stderr"
        row = {"argv": argv, "started_utc": utc(), "stdout_path": str(out),
               "stderr_path": str(err), "redirection_before_launch": True}
        transcript["commands"].append(row)
        start = time.monotonic()
        with out.open("wb") as stdout, err.open("wb") as stderr:
            proc = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
            row["pid"] = proc.pid
            try:
                code = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                row["watchdog"] = True
                os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait()
        row.update(ended_utc=utc(), wall_seconds=time.monotonic()-start,
                   exit_code=code, terminal_observed=True,
                   stdout=out.read_text(errors="replace"), stderr=err.read_text(errors="replace"))
        if check and code != 0:
            raise RuntimeError(f"command {index} failed with exit {code}")
        return row

    def inspect(container):
        return json.loads(run(DOCKER + ["inspect", container])["stdout"])[0]

    def create(name, image, mode, expected_id, readonly=False):
        argv = DOCKER + ["create", "--pull", "never", "--name", name, "--label", "crypto.autoresearch.task="+TASK,
            "--platform", "linux/arm64", "--network", "none", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges:true", "--cpus", "1", "--memory", "2147483648",
            "--memory-swap", "2147483648", "--pids-limit", "32" if readonly else "64",
            "--user", "65534:65534" if readonly else "0:0",
            "-e", "PYTHONDONTWRITEBYTECODE=1", "-e", "PYTHONHASHSEED=0",
            "-e", "SYMPY_GROUND_TYPES=python"]
        if readonly:
            argv += ["--read-only", "--tmpfs", "/tmp:rw,size=16m,mode=1777"]
        argv += [image, "python3", "-B", "/opt/reserve-inputs/install_verify.py", mode]
        cid = run(argv)["stdout"].strip()
        assert re.fullmatch(r"[0-9a-f]{64}", cid)
        transcript["created_containers"].append(cid)
        info = inspect(cid)
        assert info["Image"] == expected_id
        host = info["HostConfig"]
        assert host["NetworkMode"] == "none" and host["Memory"] == 2147483648
        assert host["MemorySwap"] == 2147483648 and not host["Privileged"]
        assert info["Config"]["Labels"]["crypto.autoresearch.task"] == TASK
        assert host["ReadonlyRootfs"] is readonly
        assert set(host.get("CapDrop") or []) == {"ALL"} and not host.get("CapAdd")
        assert host["PidsLimit"] == (32 if readonly else 64)
        assert host["NanoCpus"] == 1000000000
        assert info["Config"]["User"] == ("65534:65534" if readonly else "0:0")
        assert not host.get("Binds")
        assert any(x.startswith("no-new-privileges") for x in host.get("SecurityOpt", []))
        assert all(readonly and m["Type"] == "tmpfs" and m["Destination"] == "/tmp"
                   for m in info.get("Mounts", []))
        transcript.setdefault("initial_inspections", []).append(info)
        return cid

    def start(cid, timeout):
        transcript["container_start_attempts"] += 1
        assert prior_starts + transcript["container_start_attempts"] <= 4
        result = run(DOCKER + ["start", "--attach", cid], timeout=timeout, check=False)
        info = inspect(cid)
        transcript.setdefault("terminal_inspections", []).append(info)
        if info["State"]["Running"]:
            run(DOCKER + ["kill", cid], check=False)
            transcript["terminal_inspections"].append(inspect(cid))
            raise RuntimeError("container watchdog; no result inferred")
        assert result["exit_code"] == info["State"]["ExitCode"] == 0
        assert not info["State"].get("OOMKilled")
        payload = json.loads(result["stdout"])
        assert payload["status"] == "passed"
        return payload

    try:
        handoff = yaml.safe_load((REPO / "ledger/handoffs" / (TASK+".yaml")).read_text())["handoff"]
        for binding in handoff["source_bindings"]:
            assert sha(REPO / binding["path"]) == binding["sha256"], binding["path"]
        transcript["verified_source_bindings"] = len(handoff["source_bindings"])
        transcript["environment"] = run(DOCKER + ["info", "--format",
            "{{json .CgroupDriver}} {{json .CgroupVersion}} {{json .MemTotal}} {{json .Architecture}}"])["stdout"]
        base = json.loads(run(DOCKER + ["image", "inspect", BASE])["stdout"])[0]
        assert base["Os"] == "linux" and base["Architecture"] == "arm64"
        assert BASE in base["RepoDigests"] or any(x.endswith(BASE.split("@", 1)[1]) for x in base["RepoDigests"])
        transcript["base_image"] = base
        inputs = scratch / "inputs"
        inputs.mkdir()
        metadata = json.loads(META.read_text())
        shutil.copyfile(META, inputs / "dependencies.json")
        shutil.copyfile(ROOT / "install_verify.py", inputs / "install_verify.py")
        requirements = []
        for package in metadata["packages"]:
            wheel = package["wheel"]
            assert wheel["url"].startswith("https://files.pythonhosted.org/")
            assert Path(wheel["filename"]).name == wheel["filename"]
            target = inputs / wheel["filename"]
            run(["/usr/bin/curl", "--fail", "--silent", "--show-error", "--location",
                 "--proto", "=https", "--proto-redir", "=https", "--max-time", "60",
                 "--output", str(target), wheel["url"]], timeout=70)
            assert target.stat().st_size == wheel["size"] and sha(target) == wheel["digests"]["sha256"]
            requirements.append(package["name"]+"=="+package["version"]+" --hash=sha256:"+wheel["digests"]["sha256"])
        (inputs / "requirements.txt").write_text("\n".join(requirements)+"\n")
        transcript["copied_input_sha256"] = {f.name: sha(f) for f in inputs.iterdir()}
        installer = create(TASK.lower()+"-install", BASE, "install", base["Id"])
        run(DOCKER + ["cp", str(inputs), installer+":/opt/reserve-inputs"])
        installed = start(installer, 180)
        transcript["installer_result"] = installed
        committed = run(DOCKER + ["commit", "--change", "USER 65534:65534",
            "--change", 'CMD ["python3"]', "--change", "WORKDIR /tmp", installer, TAG])["stdout"].strip()
        assert re.fullmatch(r"sha256:[0-9a-f]{64}", committed)
        image_info = json.loads(run(DOCKER + ["image", "inspect", committed])["stdout"])[0]
        assert image_info["Id"] == committed
        base_layers = base["RootFS"]["Layers"]
        assert image_info["RootFS"]["Layers"][:len(base_layers)] == base_layers
        verifier = create(TASK.lower()+"-verify", committed, "verify", committed, readonly=True)
        verified = start(verifier, 60)
        assert verified["fresh_inventory_matches"] and installed["inventory"] == verified["inventory"]
        transcript.update(status="passed", image_binding={"task_id": TASK, "base_image": BASE,
            "base_id": base["Id"], "prepared_image_id": committed, "local_tag": TAG,
            "inspection": image_info, "inventory": verified["inventory"],
            "scientific_admission": False, "group_oom_guard_verified": False})
    except BaseException as exc:
        transcript.update(status="failed", error_type=type(exc).__name__, error=str(exc))
    finally:
        for cid in reversed(transcript["created_containers"]):
            try:
                info = inspect(cid)
                if info["State"]["Running"]:
                    run(DOCKER + ["kill", cid], check=False)
                    info = inspect(cid)
                removed = run(DOCKER + ["rm", cid], check=False)
                transcript["cleanup"].append({"container_id": cid, "terminal_before_remove": info,
                    "remove": removed})
                if removed["exit_code"] != 0:
                    transcript["status"] = "failed"
            except BaseException as exc:
                transcript["cleanup"].append({"container_id": cid, "error": repr(exc)})
                transcript["status"] = "failed"
        transcript["ended_utc"] = utc()
        with receipt_path.open("x") as output:
            json.dump(transcript, output, indent=2)
            output.write("\n")
        temporary.cleanup()
    print(json.dumps({"status": transcript["status"], "start_attempts": transcript["container_start_attempts"],
                      "receipt": str(receipt_path), "error": transcript.get("error")}))
    return 0 if transcript["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
