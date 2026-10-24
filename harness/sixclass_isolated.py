"""Run native six-class custody and solver binaries in separate sealed containers.

The custody container sees the private audit mount; the solver container never
does. This is a local process boundary, not remote host attestation. Docker's
daemon administrator and this orchestrator remain trusted.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from harness.sixclass_native import digest, receipt_for_result

IMAGE = "debian:bookworm-slim@sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8"
SCHEMA = "crypto.autoresearch.sixclass-isolated.v1"


def _docker_prefix(sudo: bool) -> list[str]:
    return (["sudo", "-n"] if sudo else []) + ["docker", "--host=unix:///var/run/docker.sock"]


def _run_container(binary: Path, mounts: list[tuple[Path, str, bool]],
                   arguments: list[str], *, sudo: bool, timeout: int) -> tuple[dict, int]:
    if timeout < 1:
        raise ValueError("timeout must be positive")
    name = "sixclass-" + uuid.uuid4().hex[:16]
    command = _docker_prefix(sudo) + [
        "run", "--rm", "--pull=never", "--name", name, "--network=none",
        "--read-only", "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--pids-limit=64", "--memory=512m", "--cpus=1",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "--env", "HTTP_PROXY=", "--env", "HTTPS_PROXY=", "--env", "ALL_PROXY=",
        "--mount", f"type=bind,src={binary.resolve()},dst=/bin/task,readonly",
    ]
    for source, target, readonly in mounts:
        command += ["--mount", f"type=bind,src={source.resolve()},dst={target}"
                    + (",readonly" if readonly else "")]
    command += ["--entrypoint", "/bin/task", IMAGE, *arguments]
    start = time.monotonic_ns()
    try:
        completed = subprocess.run(command, capture_output=True, text=True,
                                   timeout=timeout)
    except subprocess.TimeoutExpired:
        subprocess.run(_docker_prefix(sudo) + ["rm", "-f", name],
                       capture_output=True, timeout=10, check=False)
        raise
    elapsed_ns = time.monotonic_ns() - start
    if completed.returncode:
        raise RuntimeError(f"container failed with exit {completed.returncode}: "
                           + completed.stderr[-4000:])
    return json.loads(completed.stdout), elapsed_ns


def _write_new(path: Path, document: dict, *, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(document, stream, sort_keys=True, indent=2)
        stream.write("\n")


def generate(template: Path, custody_binary: Path, public_dir: Path,
             private_dir: Path, *, sudo: bool = False, timeout: int = 120) -> dict:
    public_dir, private_dir = public_dir.resolve(), private_dir.resolve()
    if (public_dir == private_dir or public_dir.is_relative_to(private_dir)
            or private_dir.is_relative_to(public_dir)):
        raise ValueError("public and private directories must be disjoint")
    if any(public_dir.iterdir()) or any(private_dir.iterdir()):
        raise FileExistsError("custody output directories must be empty")
    if private_dir.stat().st_mode & 0o077:
        raise ValueError("private directory must be accessible only to its owner")
    publication, elapsed_ns = _run_container(
        custody_binary,
        [(template, "/input/template.json", True),
         (public_dir, "/public", False), (private_dir, "/private", False)],
        ["generate", "/input/template.json", "/public/job.json", "/private/audit.json"],
        sudo=sudo, timeout=timeout)
    job = public_dir / "job.json"
    audit = private_dir / "audit.json"
    if publication["public_job_sha256"] != digest(job) or audit.stat().st_mode & 0o077:
        raise ValueError("custody publication hash or private permissions mismatch")
    receipt = {"schema": SCHEMA, "phase": "custody", "publication": publication,
               "custody_binary_sha256": digest(custody_binary), "template_sha256": digest(template),
               "image": IMAGE, "elapsed_ns": elapsed_ns,
               "isolation": "distinct containers; private audit mount absent from solver"}
    _write_new(public_dir / "publication.json", receipt)
    return receipt


def run(job: Path, worker_binary: Path, walkers: int, out: Path,
        *, sudo: bool = False, timeout: int = 120) -> dict:
    if walkers < 1:
        raise ValueError("walkers must be positive")
    result, elapsed_ns = _run_container(
        worker_binary, [(job, "/input/job.json", True)],
        ["/input/job.json", str(walkers)], sudo=sudo, timeout=timeout)
    receipt = receipt_for_result(job, worker_binary, walkers, elapsed_ns, result)
    receipt["container"] = {"image": IMAGE, "network": "none", "read_only": True,
                            "private_audit_mounted": False, "caps": "none"}
    _write_new(out, receipt)
    return receipt


def verify(job: Path, answer: Path, custody_binary: Path, out: Path,
           *, sudo: bool = False, timeout: int = 120) -> dict:
    result, elapsed_ns = _run_container(
        custody_binary,
        [(job, "/input/job.json", True), (answer, "/input/answer.json", True)],
        ["verify", "/input/job.json", "/input/answer.json"],
        sudo=sudo, timeout=timeout)
    if result["public_job_sha256"] != digest(job) or not isinstance(result["valid"], bool):
        raise ValueError("native answer-check result is not bound to the public job")
    receipt = {"schema": SCHEMA, "phase": "answer-check", "result": result,
               "job_sha256": digest(job), "answer_sha256": digest(answer),
               "checker_sha256": digest(custody_binary), "image": IMAGE,
               "elapsed_ns": elapsed_ns, "private_audit_mounted": False}
    _write_new(out, receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sudo", action="store_true", help="use sudo for the local Docker socket")
    sub = parser.add_subparsers(dest="command", required=True)
    custody = sub.add_parser("generate")
    custody.add_argument("--template", type=Path, required=True)
    custody.add_argument("--binary", type=Path, required=True)
    custody.add_argument("--public-dir", type=Path, required=True)
    custody.add_argument("--private-dir", type=Path, required=True)
    custody.add_argument("--timeout", type=int, default=120)
    solver = sub.add_parser("run")
    solver.add_argument("--job", type=Path, required=True)
    solver.add_argument("--binary", type=Path, required=True)
    solver.add_argument("--walkers", type=int, required=True)
    solver.add_argument("--out", type=Path, required=True)
    solver.add_argument("--timeout", type=int, default=120)
    answer = sub.add_parser("verify")
    answer.add_argument("--job", type=Path, required=True)
    answer.add_argument("--answer", type=Path, required=True)
    answer.add_argument("--binary", type=Path, required=True)
    answer.add_argument("--out", type=Path, required=True)
    answer.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.command == "generate":
        result = generate(args.template, args.binary, args.public_dir,
                          args.private_dir, sudo=args.sudo, timeout=args.timeout)
    elif args.command == "run":
        result = run(args.job, args.binary, args.walkers, args.out,
                     sudo=args.sudo, timeout=args.timeout)
    else:
        result = verify(args.job, args.answer, args.binary, args.out,
                        sudo=args.sudo, timeout=args.timeout)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
