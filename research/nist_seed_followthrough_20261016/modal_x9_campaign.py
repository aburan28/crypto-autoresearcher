#!/usr/bin/env python3
"""Run frozen X9 point-count shards on Modal; return and bind every raw row."""

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import modal


HERE = Path(__file__).resolve().parent
REMOTE = Path("/opt/nist-seed/repo")
REMOTE_HERE = REMOTE / "research/nist_seed_followthrough_20261016"
SOURCE_TREE = (HERE / "count_x9.py").is_file()
REPO = HERE.parents[1] if SOURCE_TREE else REMOTE
INPUTS = [
    "research/nist_seed_followthrough_20261016/count_x9.py",
    "research/nist_seed_selection_20261016/targets.json",
    "research/nist_seed_selection_20261016/raw/candidates.jsonl",
]
INPUTS += [f"research/nist_seed_provenance_20261016/census/orders_{number}.txt"
           for number in (863711343, 863966734, 871002724, 871696354, 872952608, 891607927)]
EXPECTED = ({rel: hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
             for rel in INPUTS} if SOURCE_TREE else {})
TARGETS = ({row["name"]: row for row in json.loads((REPO / INPUTS[1]).read_text())}
           if SOURCE_TREE else {})
ENDPOINTS = ("P-521", "P-384", "P-224", "P-256", "prime239v3", "prime192v2")
IMAGE = modal.Image.debian_slim(python_version="3.12").apt_install("pari-gp", "pari-seadata")
if SOURCE_TREE:
    for rel in INPUTS:
        IMAGE = IMAGE.add_local_file(REPO / rel, str(REMOTE / rel), copy=True)
APP = modal.App("nist-seed-x9-exact-count")


def digest(data):
    return hashlib.sha256(data).hexdigest()


@APP.function(image=IMAGE, cpu=1.0, memory=2048, max_containers=12,
              timeout=7200, retries=0, scaledown_window=5)
def count_shard(item, expected):
    target, start, end, attempt = item
    began = time.monotonic()
    observed = {rel: hashlib.sha256((REMOTE / rel).read_bytes()).hexdigest()
                for rel in expected}
    bad = {rel: [observed[rel], want] for rel, want in expected.items()
           if observed[rel] != want}
    if bad:
        return {"item": item, "status": "INPUT_MISMATCH", "mismatches": bad}
    command = [sys.executable, str(REMOTE_HERE / "count_x9.py"),
               "--target", target, "--start", str(start), "--end", str(end),
               "--attempt", attempt]
    if target == "P-521":
        command.extend(["--stack-mib", "1024"])
    try:
        run = subprocess.run(command, capture_output=True, text=True, timeout=7100)
        stdout, stderr, returncode = run.stdout, run.stderr, run.returncode
        status = "PROCESS_OK" if returncode == 0 else "PROCESS_FAILED"
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or b"").decode("utf-8", "replace")
        stderr = (exc.stderr or b"").decode("utf-8", "replace")
        returncode, status = None, "PROCESS_TIMEOUT"
    stem = f"{start:05d}-{end:05d}-{attempt}.jsonl"
    output = REMOTE_HERE / "raw/x9" / target / stem
    partial = output.with_suffix(".jsonl.partial")
    if output.exists():
        artifact_status, data = "complete_file", output.read_bytes()
    elif partial.exists():
        artifact_status, data = "partial_file", partial.read_bytes()
    else:
        artifact_status, data = "no_file", b""
    return {"item": item, "status": status, "returncode": returncode,
            "command": command, "stdout": stdout, "stderr": stderr,
            "artifact_status": artifact_status, "data": data,
            "data_sha256": digest(data),
            "elapsed_seconds": round(time.monotonic() - began, 6),
            "python": platform.python_version(),
            "gp_version": subprocess.run(["gp", "--version-short"],
                                         capture_output=True, text=True).stdout.strip(),
            "system": platform.platform()}


def build_items(mode, attempt):
    if mode == "pilot":
        return [("P-256", 1, 20, attempt), ("P-256", 1842, 1842, attempt),
                ("P-521", 1, 10, attempt)]
    streams = []
    for name in ENDPOINTS:
        end = TARGETS[name]["candidate_index"]
        streams.append([(name, start, min(start + 99, end), attempt)
                        for start in range(1, end + 1, 100)])
    items = []
    for offset in range(max(map(len, streams))):
        items.extend(stream[offset] for stream in streams if offset < len(stream))
    if len(items) != 221 or sum(end - start + 1 for _, start, end, _ in items) != 21753:
        raise AssertionError("incorrect full grid")
    return items


def check_result(item, result, mode):
    target, start, end, attempt = item
    if result["item"] != item or result["data_sha256"] != digest(result["data"]):
        raise AssertionError("returned shard identity/digest mismatch")
    if result["artifact_status"] != "complete_file":
        raise AssertionError("shard did not return a complete file")
    lines = result["data"].decode().splitlines()
    header = json.loads(lines[0])
    if (header["record"] != "run" or header["target"] != target or
            header["start"] != start or header["end"] != end or
            header["script_sha256"] != EXPECTED[INPUTS[0]] or
            header["targets_sha256"] != EXPECTED[INPUTS[1]] or
            header["candidates_sha256"] != EXPECTED[INPUTS[2]]):
        raise AssertionError("shard header/source mismatch")
    if len(lines) != end - start + 2:
        raise AssertionError("shard row count mismatch")
    rows = [json.loads(line) for line in lines[1:]]
    for index, row in enumerate(rows, start):
        if row["target"] != target or row["index"] != index:
            raise AssertionError("shard row identity mismatch")
    if any(row["status"] != "COMPLETE" for row in rows):
        raise AssertionError("indeterminate candidate remains")
    if mode == "pilot" and target == "P-256" and start == 1842:
        if not rows[0].get("anchor_order_matches"):
            raise AssertionError("published P-256 anchor failed")
    if mode == "pilot" and target == "P-256" and start == 1 and end == 20:
        local = HERE / "raw/x9/P-256/00001-00020-retry1.jsonl"
        controls = [json.loads(line) for line in local.read_text().splitlines()[1:]]
        for row, control in zip(rows, controls, strict=True):
            for mapping in ("unmasked", "strict_x9"):
                if row[mapping]["status"] != control[mapping]["status"]:
                    raise AssertionError("local/cloud variant status mismatch")
                if row[mapping]["status"] == "COUNTED":
                    for key in ("c", "canonical_b", "canonical_order", "other_order"):
                        if row[mapping][key] != control[mapping][key]:
                            raise AssertionError(f"local/cloud {mapping}/{key} mismatch")
    return rows


def save_result(item, result, mode):
    target, start, end, attempt = item
    stem = f"{start:05d}-{end:05d}-{attempt}.jsonl"
    if result.get("data"):
        path = HERE / "raw/x9" / target / stem
        if result.get("artifact_status") == "partial_file":
            path = path.with_suffix(".jsonl.partial")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as sink:
            sink.write(result["data"])
        file_path, file_sha = str(path.relative_to(REPO)), digest(result["data"])
    else:
        file_path, file_sha = None, None
    record = {key: value for key, value in result.items() if key != "data"}
    record.update({"local_path": file_path, "local_sha256": file_sha})
    try:
        rows = check_result(item, result, mode)
        record["rows"] = len(rows)
        record["verification"] = "PASS"
    except Exception as exc:
        record["verification"] = "FAIL"
        record["verification_error"] = f"{type(exc).__name__}: {exc}"
    return record


@APP.local_entrypoint()
def main(mode: str = "pilot", attempt: str = "modalpilot1"):
    if mode not in ("pilot", "full"):
        raise ValueError("mode must be pilot or full")
    if not attempt.isalnum() or len(attempt) > 32:
        raise ValueError("attempt must be 1-32 alphanumeric characters")
    run_dir = HERE / "raw" / f"modal_campaign_{attempt}"
    run_dir.mkdir(parents=True, exist_ok=False)
    items = build_items(mode, attempt)
    plan = {"created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "mode": mode, "attempt": attempt, "items": items,
            "max_containers": 12, "cpu_per_container": 1.0,
            "memory_mib_per_container": 2048, "shard_timeout_seconds": 7200,
            "input_sha256": EXPECTED,
            "runner_sha256": digest(Path(__file__).read_bytes()),
            "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                       check=True, capture_output=True,
                                       text=True).stdout.strip(),
            "local_python": platform.python_version(), "local_command": sys.argv}
    plan_path = run_dir / "plan.json"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    events_path = run_dir / "events.jsonl"
    successful = 0
    with events_path.open("x") as events:
        outputs = count_shard.map(items, kwargs={"expected": EXPECTED},
                                  order_outputs=True, return_exceptions=True)
        for observed_count, (item, response) in enumerate(zip(items, outputs), 1):
            if isinstance(response, BaseException):
                record = {"item": item, "verification": "FAIL",
                          "exception": f"{type(response).__name__}: {response}"}
            else:
                record = save_result(item, response, mode)
            events.write(json.dumps(record, sort_keys=True) + "\n")
            events.flush()
            successful += record["verification"] == "PASS"
            print(json.dumps({"successful": successful, "observed": observed_count,
                              "total": len(items),
                              "last_item": item, "verification": record["verification"]}),
                  flush=True)
    stop = {"status": "complete" if successful == len(items) else "partial",
            "successful_shards": successful, "total_shards": len(items),
            "plan_sha256": digest(plan_path.read_bytes()),
            "events_sha256": digest(events_path.read_bytes()),
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    (run_dir / "stop.json").write_text(json.dumps(stop, indent=2, sort_keys=True) + "\n")
    print(json.dumps(stop, sort_keys=True), flush=True)
    if stop["status"] != "complete":
        raise RuntimeError("one or more shards did not verify")
