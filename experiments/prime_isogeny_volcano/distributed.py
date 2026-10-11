#!/usr/bin/env python3
"""Ray-distributed bounded Sage isogeny jobs with resumable immutable shards."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
SAGE_SCRIPT = HERE / "search.sage"

def job_key(job):
    return hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest()[:20]

def run_job(job, output_dir, sage_bin, timeout):
    key = job_key(job)
    dest = Path(output_dir) / (key + ".jsonl")
    receipt = Path(output_dir) / (key + ".receipt.json")
    if dest.exists() and receipt.exists():
        try:
            old = json.loads(receipt.read_text())
            if old.get("status") == "ok" and old.get("job") == job:
                return {"key": key, "status": "cached"}
        except (ValueError, OSError):
            pass
    tmp = dest.with_suffix(".tmp")
    cmd = [sage_bin, str(SAGE_SCRIPT), "--p", str(job["p"]),
           "--a", str(job["a"]), "--b", str(job["b"]),
           "--primes", *map(str, job["primes"]), "--out", str(tmp)]
    started = time.monotonic()
    status, error = "ok", None
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if proc.returncode != 0:
            status, error = "failed", proc.stderr[-4000:]
        elif not tmp.exists() or sum(1 for _ in tmp.open()) != len(job["primes"]):
            status, error = "failed", "Incomplete JSONL output"
        else:
            os.replace(tmp, dest)
    except (subprocess.TimeoutExpired, OSError) as exc:
        status, error = "failed", str(exc)
    finally:
        tmp.unlink(missing_ok=True)
    result = {"key": key, "job": job, "status": status,
              "elapsed_seconds": time.monotonic()-started, "error": error,
              "command": cmd}
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True))
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="JSONL: {p,a,b,primes:[...]}")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--backend", choices=["local", "ray"], default="local")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--sage-bin", default="sage")
    ap.add_argument("--ray-address", default=None)
    args = ap.parse_args()
    if args.workers < 1 or args.timeout < 1:
        ap.error("workers and timeout must be positive")
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    jobs = [json.loads(line) for line in Path(args.manifest).read_text().splitlines() if line.strip()]
    for job in jobs:
        if not all(k in job for k in ("p", "a", "b", "primes")) or not job["primes"]:
            ap.error("Each manifest row needs p, a, b, nonempty primes")
    results = []
    if args.backend == "ray":
        import ray
        ray.init(address=args.ray_address or None)
        remote = ray.remote(num_cpus=1)(run_job)
        pending = [remote.remote(j, str(output), args.sage_bin, args.timeout) for j in jobs]
        results = ray.get(pending)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(run_job, j, str(output), args.sage_bin, args.timeout) for j in jobs]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
    print(json.dumps({"jobs": len(results), "ok": sum(r["status"] in ("ok", "cached") for r in results),
                      "failed": sum(r["status"] == "failed" for r in results)}, sort_keys=True))
    if any(r["status"] == "failed" for r in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
