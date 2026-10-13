#!/usr/bin/env python3
"""Build and run the frozen independent volcano-level rho replication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
HEADER = ("run", "ops", "walks", "cycles", "abandoned", "useless", "ok", "sec")
SHUFFLE_SEED = 2026101317
CONFIG = {
    "m37": {
        "source_dir": REPO / "research/isogeny_volcano_rho_20261005",
        "source_sha256": "7c8195ae671124f057ab913bb10e98f7a75c5c5e16cbbac3f67b5fd87a20b106",
        "sample_sha256": "994caf2b456058c8fee9dc87f6289d7a07a22a0c07b03e64bbfb015797f7d4cd",
        "params_sha256": None,
        "seed_base": 37_000_000_000,
        "rows": 500,
        "crater_chunks": 10,
        "lower_chunks": 2,
        "expected_solves": 136_000,
    },
    "m41": {
        "source_dir": REPO / "research/isogeny_volcano_rho_m41_20261006",
        "source_sha256": "212cd0aebf36e9095b42677a02286c85834763d9b37028b49529020de5cec90f",
        "sample_sha256": "37931f3e0417f1fe0f25965aa18e858e29f6fdc028cff4ae3bccf5d47fd564dc",
        "params_sha256": "89c1c89ef929d8758ad43cebe98553091ed9bbb358a8fbe9aca721865cd58ec3",
        "seed_base": 41_000_000_000,
        "rows": 200,
        "crater_chunks": 15,
        "lower_chunks": 1,
        "expected_solves": 24_000,
    },
}


@dataclass(frozen=True)
class Job:
    study: str
    curve_id: str
    level: str
    b: str
    mode: int
    chunk: int
    rows: int
    seed: int

    @property
    def filename(self) -> str:
        return f"c{self.curve_id}_m{self.mode}_r{self.chunk}.csv"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def command_output(argv: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.run(argv, cwd=cwd, check=True, text=True, capture_output=True).stdout.strip()


def read_sample(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != ("id", "level", "b"):
            raise ValueError(f"{path}: invalid sample schema")
        rows = list(reader)
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise ValueError(f"{path}: empty or duplicate sample")
    if sum(r["level"] == "crater" for r in rows) != 1:
        raise ValueError(f"{path}: expected exactly one crater")
    return rows


def make_jobs(study: str) -> list[Job]:
    cfg = CONFIG[study]
    sample = read_sample(cfg["source_dir"] / "sample.csv")
    jobs: list[Job] = []
    for curve in sample:
        crater = curve["level"] == "crater"
        modes = (0, 1) if crater else (0,)
        chunks = cfg["crater_chunks"] if crater else cfg["lower_chunks"]
        for mode in modes:
            for chunk in range(chunks):
                seed = cfg["seed_base"] + 10_000 * int(curve["id"]) + 1_000 * mode + chunk
                jobs.append(Job(study, curve["id"], curve["level"], curve["b"], mode, chunk, cfg["rows"], seed))
    if sum(j.rows for j in jobs) != cfg["expected_solves"]:
        raise ValueError(f"{study}: internal solve-count mismatch")
    return jobs


def validate_csv(path: Path, rows_expected: int) -> dict[str, int]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if tuple(reader.fieldnames or ()) != HEADER:
            raise ValueError(f"{path}: schema mismatch")
        rows = list(reader)
    if len(rows) != rows_expected:
        raise ValueError(f"{path}: expected {rows_expected} rows, found {len(rows)}")
    indices: set[int] = set()
    for row in rows:
        try:
            run = int(row["run"])
            values = [int(row[k]) for k in HEADER[1:6]]
            ok = int(row["ok"])
            sec = float(row["sec"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{path}: nonnumeric row") from exc
        if run in indices or any(v < 0 for v in values) or ok != 1 or not (sec > 0):
            raise ValueError(f"{path}: duplicate, negative, nonverified, or invalid row {run}")
        indices.add(run)
    if indices != set(range(rows_expected)):
        raise ValueError(f"{path}: run ids are not exactly 0..{rows_expected - 1}")
    return {"rows": len(rows), "verified": sum(int(r["ok"]) for r in rows)}


def verify_inputs(study: str) -> None:
    cfg = CONFIG[study]
    checks = [(cfg["source_dir"] / "rho.c", cfg["source_sha256"]),
              (cfg["source_dir"] / "sample.csv", cfg["sample_sha256"])]
    if cfg["params_sha256"]:
        checks.append((cfg["source_dir"] / "params.h", cfg["params_sha256"]))
    for path, expected in checks:
        actual = sha256(path)
        if actual != expected:
            raise ValueError(f"{path}: sha256 {actual}, expected {expected}")


def build(study: str, out: Path) -> tuple[Path, dict]:
    cfg = CONFIG[study]
    build_dir = out / study / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    binary = build_dir / "rho"
    command = ["gcc", "-O2", "-march=native", "-o", str(binary), "rho.c"]
    partial = binary.with_suffix(".partial")
    if binary.exists() or partial.exists():
        raise FileExistsError(f"{study}: refusing pre-existing build output")
    build_command = command.copy()
    build_command[4] = str(partial)
    proc = subprocess.run(build_command, cwd=cfg["source_dir"], text=True, capture_output=True)
    (build_dir / "gcc.stdout.log").write_text(proc.stdout)
    (build_dir / "gcc.stderr.log").write_text(proc.stderr)
    if proc.returncode:
        raise RuntimeError(f"{study}: gcc failed with {proc.returncode}")
    os.replace(partial, binary)
    receipt = {
        "study": study,
        "command": command,
        "compiler": command_output(["gcc", "--version"]).splitlines()[0],
        "source": str(cfg["source_dir"] / "rho.c"),
        "source_sha256": sha256(cfg["source_dir"] / "rho.c"),
        "sample_sha256": sha256(cfg["source_dir"] / "sample.csv"),
        "params_sha256": sha256(cfg["source_dir"] / "params.h") if cfg["params_sha256"] else None,
        "binary": str(binary),
        "binary_sha256": sha256(binary),
    }
    return binary, receipt


def host_receipt() -> dict:
    cpu_model = None
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    return {
        "utc": utc_now(),
        "platform": platform.platform(),
        "python": sys.version,
        "cpu_model": cpu_model,
        "logical_cpus": os.cpu_count(),
        "affinity": sorted(os.sched_getaffinity(0)),
        "uname": platform.uname()._asdict(),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--studies", choices=("all", "m37", "m41"), default="all")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--cores", default="0,1,2,3")
    args = ap.parse_args()
    studies = ["m37", "m41"] if args.studies == "all" else [args.studies]
    cores = [int(x) for x in args.cores.split(",")]
    if args.workers != len(cores) or args.workers < 1:
        raise ValueError("workers must equal the number of listed cores")
    if not set(cores).issubset(os.sched_getaffinity(0)):
        raise ValueError(f"requested cores {cores} not in affinity {sorted(os.sched_getaffinity(0))}")
    if args.out.exists() and any(args.out.iterdir()):
        raise FileExistsError(f"{args.out} is nonempty; this protocol requires a fresh output root")
    args.out.mkdir(parents=True, exist_ok=True)
    for study in studies:
        verify_inputs(study)
    jobs = [job for study in studies for job in make_jobs(study)]
    random.Random(SHUFFLE_SEED).shuffle(jobs)
    plan = {
        "created_utc": utc_now(), "shuffle_seed": SHUFFLE_SEED,
        "workers": args.workers, "cores": cores, "jobs": [asdict(j) | {"filename": j.filename} for j in jobs],
        "expected_solves": sum(j.rows for j in jobs),
    }
    (args.out / "plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    (args.out / "host.json").write_text(json.dumps(host_receipt(), indent=2, sort_keys=True) + "\n")
    (args.out / "run-command.txt").write_text(" ".join([sys.executable, *map(str, sys.argv)]) + "\n")
    git = {
        "commit": command_output(["git", "rev-parse", "HEAD"], cwd=REPO),
        "status_porcelain": command_output(["git", "status", "--porcelain=v1"], cwd=REPO),
    }
    binaries, builds = {}, []
    for study in studies:
        binaries[study], receipt = build(study, args.out)
        builds.append(receipt)
        (args.out / study / "raw").mkdir(parents=True, exist_ok=True)
    (args.out / "build-provenance.json").write_text(json.dumps({"git": git, "builds": builds}, indent=2, sort_keys=True) + "\n")
    receipt_path = args.out / "jobs.jsonl"
    receipt_lock = threading.Lock()
    progress_lock = threading.Lock()
    error_lock = threading.Lock()
    worker_errors: list[BaseException] = []
    completed = 0
    start = time.monotonic()

    buckets = [[] for _ in cores]
    for i, job in enumerate(jobs):
        buckets[i % len(cores)].append(job)

    def do_job(core: int, job: Job) -> dict:
        raw = args.out / job.study / "raw"
        final = raw / job.filename
        if final.exists():
            raise FileExistsError(f"refusing to overwrite {final}")
        partial = final.with_suffix(final.suffix + ".partial")
        if partial.exists():
            raise FileExistsError(f"refusing pre-existing partial output {partial}")
        cmd = ["taskset", "-c", str(core), str(binaries[job.study]), "run", job.b, "0", str(job.mode),
               str(job.rows), str(job.seed), str(partial)]
        started_utc = utc_now()
        t0 = time.monotonic()
        proc = subprocess.run(cmd, text=True, capture_output=True)
        elapsed = time.monotonic() - t0
        if proc.returncode:
            raise RuntimeError(f"{job.study}/{job.filename}: exit {proc.returncode}; stderr={proc.stderr[-1000:]}")
        validation = validate_csv(partial, job.rows)
        os.replace(partial, final)
        return {"job": asdict(job), "core": core, "status": "completed", "command": cmd,
                "stdout": proc.stdout, "stderr": proc.stderr, "validation": validation,
                "output": str(final), "sha256": sha256(final), "started_utc": started_utc,
                "finished_utc": utc_now(), "elapsed_sec": elapsed}

    def worker(core: int, bucket: list[Job]) -> None:
        nonlocal completed
        for job in bucket:
            try:
                receipt = do_job(core, job)
            except BaseException as exc:
                receipt = {"job": asdict(job), "core": core, "status": "failed", "error": repr(exc), "utc": utc_now()}
                with receipt_lock:
                    with receipt_path.open("a") as f:
                        f.write(json.dumps(receipt, sort_keys=True) + "\n")
                with error_lock:
                    worker_errors.append(exc)
                return
            with receipt_lock:
                with receipt_path.open("a") as f:
                    f.write(json.dumps(receipt, sort_keys=True) + "\n")
            with progress_lock:
                completed += 1
                if completed % 10 == 0 or completed == len(jobs):
                    line = f"{utc_now()} {completed}/{len(jobs)} jobs; elapsed={time.monotonic() - start:.1f}s"
                    print(line, flush=True)
                    with (args.out / "run.stdout.log").open("a") as f:
                        f.write(line + "\n")

    session = {"started_utc": utc_now(), "status": "running", "studies": studies, "jobs": len(jobs),
               "expected_solves": sum(j.rows for j in jobs)}
    (args.out / "session.json").write_text(json.dumps(session, indent=2, sort_keys=True) + "\n")
    errors: list[BaseException] = []
    threads = []
    for core, bucket in zip(cores, buckets):
        thread = threading.Thread(target=lambda c=core, b=bucket: worker(c, b), name=f"core-{core}")
        thread.start(); threads.append(thread)
    for thread in threads:
        thread.join()
    errors.extend(worker_errors)
    # Validate independently even after every worker reports success.
    try:
        expected_by_study = {study: {job.filename: job.rows for job in jobs if job.study == study} for study in studies}
        for study, expected in expected_by_study.items():
            raw = args.out / study / "raw"
            actual = {p.name for p in raw.iterdir() if p.is_file()}
            if actual != set(expected):
                raise RuntimeError(f"{study}: final file mismatch; missing={sorted(set(expected)-actual)[:8]} extra={sorted(actual-set(expected))[:8]}")
            for name, count in expected.items():
                validate_csv(raw / name, count)
        if completed != len(jobs):
            raise RuntimeError(f"only {completed}/{len(jobs)} jobs completed")
    except BaseException as exc:
        errors.append(exc)
    session.update(finished_utc=utc_now(), elapsed_sec=time.monotonic() - start,
                   completed_jobs=completed, status="complete" if not errors else "failed",
                   error=None if not errors else repr(errors[0]))
    (args.out / "session.json").write_text(json.dumps(session, indent=2, sort_keys=True) + "\n")
    if errors:
        raise errors[0]
    print(json.dumps(session, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
