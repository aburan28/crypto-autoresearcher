"""Run the frozen isobench timing on a fresh, bounded, bare-metal EC2 host without SSH.

    python -m harness.endosweep.isobench.ec2_job --out DIR [--instance-type c7i.metal-24xl] [--dry-run]

Same discipline as crypto's ``ecc2k130/aws/bench_job.py``, for a CPU job:

* one on-demand instance, Amazon Linux 2023 (latest AMI from the public SSM
  parameter), the region's default VPC subnet and default security group,
  **no key pair, no IAM instance profile, no long-lived credential**;
* everything through user-data: the source subset is fetched from a presigned
  S3 URL and checked against its SHA-256, results go back to presigned URLs;
* ``InstanceInitiatedShutdownBehavior=terminate``, a systemd deadline that
  halts the host, and a client-side ``terminate_instances`` in ``finally``;
* on the host: the performance governor where exposed, then the frozen
  ``isobench`` command for both curves pinned with ``taskset`` to one CPU
  whose SMT sibling is left idle, with ``lscpu``, ``/proc/stat`` and load
  averages recorded before and after.

``--dry-run`` builds the source archive and prints the user-data without
calling AWS.  Results land under ``--out``; the launch receipt is
``launch.json`` beside them.  Nothing here edits IAM, launch templates or any
other standing resource; the S3 prefix is unique per run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import signal
import subprocess
import tarfile
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SOURCE_PATHS = ["harness/__init__.py", "harness/endosweep",
                "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"]
ROWS = "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"
CURVES = {"target": "other/BADA55-VPR-224", "control": "control+: 3-isogenous neighbour of NIST P-256"}
FROZEN = ["--points", "64", "--reps", "41", "--bootstrap", "4000", "--seed", "20261016", "--cflags=-O2 -march=native"]
AMI_PARAM = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"


def source_archive(path: Path) -> tuple[str, str, bool]:
    rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", *SOURCE_PATHS], cwd=REPO,
                                capture_output=True, text=True).stdout.strip())
    skip = lambda info: None if "__pycache__" in info.name or info.name.endswith(".pyc") else info
    with tarfile.open(path, "w:gz") as archive:
        for name in SOURCE_PATHS:
            archive.add(REPO / name, arcname=name, filter=skip)
        marker = path.parent / "SOURCE_REV"
        marker.write_text(f"{rev}{' (uncommitted changes)' if dirty else ''}\n")
        archive.add(marker, arcname="SOURCE_REV")
    return hashlib.sha256(path.read_bytes()).hexdigest(), rev, dirty


def user_data(urls: dict, source_sha: str, deadline_minutes: int, job_minutes: int, cpu: int) -> str:
    q = shlex.quote
    runs = "\n".join(
        f"taskset -c {cpu} timeout {job_minutes * 60} python3 -m harness.endosweep.isobench.isobench "
        f"--rows {q(ROWS)} --curve {q(curve)} --out-dir /opt/bench/results/{role} "
        + " ".join(q(a) for a in FROZEN) + f" > /opt/bench/results/{role}.log 2>&1"
        for role, curve in CURVES.items())
    return f"""#!/bin/bash
set -uo pipefail
systemd-run --unit=bench-job-deadline --on-active={int(deadline_minutes)}m /sbin/shutdown -h now
mkdir -p /opt/bench/src /opt/bench/results
exec > /opt/bench/results/bootstrap.log 2>&1
finish() {{
    rc=$?
    trap - EXIT
    set +e
    printf '%s\\n' "$rc" > /opt/bench/results/exit-code
    tar -czf /opt/bench/results.tgz -C /opt/bench/results .
    curl --fail --silent --show-error --retry 3 --max-time 300 --upload-file /opt/bench/results.tgz {q(urls['results'])}
    curl --fail --silent --show-error --retry 3 --max-time 60 --upload-file /opt/bench/results/exit-code {q(urls['done'])}
    shutdown -h now
}}
trap finish EXIT
set -e
curl --fail --silent --show-error --retry 3 --max-time 300 {q(urls['source'])} -o /opt/bench/source.tgz
printf '%s  %s\\n' '{source_sha}' /opt/bench/source.tgz | sha256sum -c -
tar -xzf /opt/bench/source.tgz -C /opt/bench/src
dnf install -y -q gcc python3-pip util-linux >/dev/null
python3 -m pip install -q python-flint sympy pyyaml
cd /opt/bench/src
for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do [ -w "$g" ] && echo performance > "$g" || true; done
lscpu > /opt/bench/results/lscpu.txt
cat /sys/devices/system/cpu/cpu{cpu}/topology/thread_siblings_list > /opt/bench/results/sibling.txt 2>/dev/null || true
cat /sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor > /opt/bench/results/governor.txt 2>/dev/null || echo none > /opt/bench/results/governor.txt
(systemd-detect-virt || true) > /opt/bench/results/virt.txt
uname -a > /opt/bench/results/uname.txt; gcc --version | head -1 > /opt/bench/results/gcc.txt; python3 --version > /opt/bench/results/python.txt
cp SOURCE_REV /opt/bench/results/
cat /proc/loadavg > /opt/bench/results/loadavg.before; cat /proc/stat > /opt/bench/results/stat.before
{runs}
cat /proc/loadavg > /opt/bench/results/loadavg.after; cat /proc/stat > /opt/bench/results/stat.after
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--region", default="us-east-2")
    ap.add_argument("--instance-type", default="c7i.metal-24xl")
    ap.add_argument("--bucket", default=None, help="S3 bucket for the source and results (default ecc2k130-<account>)")
    ap.add_argument("--cpu", type=int, default=2, help="the CPU the job is pinned to")
    ap.add_argument("--job-minutes", type=int, default=30)
    ap.add_argument("--deadline-minutes", type=int, default=60, help="in-instance hard shutdown")
    ap.add_argument("--wait-minutes", type=int, default=55)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source_sha, rev, dirty = source_archive(out / "source.tgz")
    if args.dry_run:
        urls = {k: f"https://example.invalid/{k}" for k in ("source", "results", "done")}
        (out / "user-data.sh").write_text(user_data(urls, source_sha, args.deadline_minutes, args.job_minutes, args.cpu))
        print(json.dumps({"dry_run": True, "source_sha256": source_sha, "rev": rev, "dirty": dirty}))
        return 0
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    config = Config(connect_timeout=30, read_timeout=60, retries={"max_attempts": 3, "mode": "standard"})
    session = boto3.Session(region_name=args.region)
    ec2 = session.client("ec2", config=config)
    account = session.client("sts", config=config).get_caller_identity()["Account"]
    bucket = args.bucket or f"ecc2k130-{account}"
    location = session.client("s3", config=config).get_bucket_location(Bucket=bucket)["LocationConstraint"] or "us-east-1"
    s3 = session.client("s3", region_name=location, config=config.merge(Config(signature_version="s3v4")))
    ami = session.client("ssm", config=config).get_parameter(Name=AMI_PARAM)["Parameter"]["Value"]
    token = uuid.uuid4().hex
    prefix = f"crypto-autoresearcher/isobench/{token}"
    vpc = ec2.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])["Vpcs"][0]["VpcId"]
    group = ec2.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc]},
                                                  {"Name": "group-name", "Values": ["default"]}])["SecurityGroups"][0]
    zones = {o["Location"] for o in ec2.describe_instance_type_offerings(
        LocationType="availability-zone", Filters=[{"Name": "instance-type", "Values": [args.instance_type]}])
        ["InstanceTypeOfferings"]}
    subnets = sorted((s for s in ec2.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc]},
                                                               {"Name": "default-for-az", "Values": ["true"]}])["Subnets"]
                      if s["AvailabilityZone"] in zones and s["MapPublicIpOnLaunch"]),
                     key=lambda s: s["AvailabilityZone"])
    if not subnets:
        raise RuntimeError(f"no default subnet offers {args.instance_type} in {args.region}")
    s3.upload_file(str(out / "source.tgz"), bucket, prefix + "/source.tgz")
    urls = {name: s3.generate_presigned_url(method, Params={"Bucket": bucket, "Key": f"{prefix}/{key}"}, ExpiresIn=3 * 3600)
            for name, method, key in [("source", "get_object", "source.tgz"),
                                      ("results", "put_object", "results.tgz"), ("done", "put_object", "done")]}
    script = user_data(urls, source_sha, args.deadline_minutes, args.job_minutes, args.cpu)
    receipt = dict(valid=False, region=args.region, instanceType=args.instance_type, ami=ami, token=token,
                   sourceSha256=source_sha, gitRev=rev, gitDirty=dirty, bucket=bucket, resultPrefix=prefix,
                   pinnedCpu=args.cpu, frozen=FROZEN, curves=CURVES, instanceId=None, availabilityZone=None,
                   launchedAt=None, doneAt=None)
    save = lambda: (out / "launch.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def stop(signum, frame):
        raise KeyboardInterrupt("cancelled")
    signal.signal(signal.SIGTERM, stop)
    save()
    instance = None
    try:
        last = None
        for subnet in subnets:
            tags = [{"Key": "Name", "Value": "isobench-" + token[:8]}, {"Key": "Project", "Value": "crypto-autoresearcher-isobench"},
                    {"Key": "BenchmarkToken", "Value": token}]
            req = dict(ImageId=ami, InstanceType=args.instance_type, MinCount=1, MaxCount=1, SubnetId=subnet["SubnetId"],
                       SecurityGroupIds=[group["GroupId"]], UserData=script, ClientToken=token + subnet["AvailabilityZone"][-1],
                       InstanceInitiatedShutdownBehavior="terminate",
                       MetadataOptions={"HttpTokens": "required", "HttpPutResponseHopLimit": 1},
                       BlockDeviceMappings=[{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 20, "VolumeType": "gp3",
                                                                                  "DeleteOnTermination": True}}],
                       TagSpecifications=[{"ResourceType": k, "Tags": tags} for k in ("instance", "volume")])
            try:
                launched = ec2.run_instances(**req)["Instances"][0]
            except ClientError as exc:
                code = exc.response["Error"]["Code"]
                print("launch in", subnet["AvailabilityZone"], "failed:", code, exc.response["Error"].get("Message", ""), flush=True)
                last = exc
                if code in ("InsufficientInstanceCapacity", "Unsupported", "InvalidParameterValue"):
                    continue
                raise
            instance = launched["InstanceId"]
            receipt.update(instanceId=instance, availabilityZone=launched["Placement"]["AvailabilityZone"],
                           launchedAt=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            save()
            break
        if instance is None:
            raise RuntimeError("no zone had capacity") from last
        print("started", instance, "in", receipt["availabilityZone"], flush=True)
        deadline = time.monotonic() + args.wait_minutes * 60
        while time.monotonic() < deadline:
            try:
                done = s3.get_object(Bucket=bucket, Key=prefix + "/done")["Body"].read().decode().strip()
            except ClientError as exc:
                if exc.response["Error"]["Code"] not in ("NoSuchKey", "404"):
                    raise
            else:
                receipt.update(doneAt=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), exitCode=done)
                s3.download_file(bucket, prefix + "/results.tgz", str(out / "results.tgz"))
                with tarfile.open(out / "results.tgz") as archive:
                    archive.extractall(out / "results", filter="data")
                receipt["valid"] = done == "0"
                print("job exit code", done, flush=True)
                break
            state = ec2.describe_instances(InstanceIds=[instance])["Reservations"][0]["Instances"][0]["State"]["Name"]
            if state in ("shutting-down", "terminated"):
                raise RuntimeError("instance stopped before uploading a result")
            print(time.strftime("%H:%M:%S"), "instance", state, flush=True)
            time.sleep(30)
        else:
            raise TimeoutError("wait deadline reached")
    finally:
        if instance:
            try:
                ec2.terminate_instances(InstanceIds=[instance])
                receipt["terminationRequestedFor"] = [instance]
            except ClientError as exc:
                receipt["terminationError"] = str(exc)
        save()
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
