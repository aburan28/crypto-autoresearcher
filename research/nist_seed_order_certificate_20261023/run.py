"""Write-once GP factorization of prime group-order neighbors."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import threading
import time

import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
PUB_NAMES = ("prime192v1", "prime192v2", "prime192v3", "prime239v1",
             "prime239v2", "prime239v3", "secp224r1", "prime256v1")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def curve_rows():
    omitted = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    out = []
    for row in sorted(omitted, key=lambda x: (x["timestamp"], x["seed_ordinal_one_based"])):
        bits = int(row["p_hex"], 16).bit_length()
        out.append((f"omitted_{bits}_{row['seed_ordinal_one_based']}", "omitted", row))
    for key in PUB_NAMES:
        out.append((f"published_{key}", "published", published[key]))
    assert len(out) == 19 and len({name for name, _, _ in out}) == 19
    return out


def gp_factor(number, prefix):
    script = (f"F=factor({number}); print(\"COUNT=\",matsize(F)[1]); "
              "for(i=1,matsize(F)[1],print(F[i,1],\",\",F[i,2])); print(\"DONE\")\n")
    prefix.with_suffix(".gp").write_text(script)
    command = ["gp", "-q", "-s", str(1024**3)]
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    monitored = psutil.Process(process.pid)
    stop = threading.Event()
    peak = 0
    memory_hit = False

    def watch():
        nonlocal peak, memory_hit
        while not stop.wait(0.1):
            try:
                rss = monitored.memory_info().rss
            except psutil.NoSuchProcess:
                return
            peak = max(peak, rss)
            if rss > 2 * 1024**3:
                memory_hit = True
                process.kill()
                return

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    try:
        stdout, stderr = process.communicate(input=script, timeout=180)
        status = "completed"
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        status = "timeout"
    finally:
        stop.set()
        watcher.join(timeout=1)
    if memory_hit:
        status = "memory_limit"
    prefix.with_suffix(".stdout").write_text(stdout)
    prefix.with_suffix(".stderr").write_text(stderr)
    receipt = {"status": status, "exit_code": process.returncode,
               "elapsed_seconds": time.monotonic()-started, "command": command,
               "script_sha256": sha(prefix.with_suffix(".gp")),
               "stdout_sha256": sha(prefix.with_suffix(".stdout")),
               "stderr_sha256": sha(prefix.with_suffix(".stderr")),
               "wall_limit_seconds": 180, "gp_stack_limit_bytes": 1024**3,
               "rss_watchdog_bytes": 2*1024**3, "peak_rss_sampled_bytes": peak}
    if status != "completed" or process.returncode != 0:
        return receipt, None
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("COUNT=") or lines[-1] != "DONE":
        raise ValueError(f"bad GP framing: {prefix.name}")
    count = int(lines[0].split("=", 1)[1])
    factors = [tuple(map(int, line.split(","))) for line in lines[1:-1]]
    if len(factors) != count:
        raise ValueError(f"factor count mismatch: {prefix.name}")
    product = 1
    for q, e in factors:
        product *= q**e
    if product != number:
        raise ValueError(f"factor product mismatch: {prefix.name}")
    return receipt, [[str(q), e] for q, e in factors]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--inject-exception", action="store_true")
    ap.add_argument("--inject-early-return", action="store_true")
    args = ap.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name, digest in EXPECTED.items():
        if sha(ARCH / name) != digest:
            raise ValueError(f"source hash mismatch: {name}")
    gp_ver = subprocess.run(["gp", "--version"], text=True, capture_output=True, check=True)
    sage_ver = subprocess.run(["sage", "--version"], text=True, capture_output=True, check=True)
    (out / "started.json").write_text(json.dumps({
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "host": platform.platform(), "python": sys.version,
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "source_sha256": {name: sha(ARCH / name) for name in EXPECTED},
        "gp_version_stdout": gp_ver.stdout, "gp_version_stderr": gp_ver.stderr,
        "sage_version_stdout": sage_ver.stdout, "sage_version_stderr": sage_ver.stderr,
    }, indent=2) + "\n")
    if args.inject_exception:
        raise RuntimeError("injected exception")
    if args.inject_early_return:
        raise RuntimeError("injected missing completion")
    work = [("control_15", "control", 15, None, None),
            ("control_60", "control", 60, None, None),
            ("control_101", "control", 101, None, None)]
    for name, label, row in curve_rows():
        n = int(row["n_hex"], 16)
        for direction, number in (("minus", n-1), ("plus", n+1)):
            work.append((f"{name}_{direction}", label, number,
                         row["identity"]["curve_uid"], n))
    records = []
    for name, label, number, uid, n in work:
        receipt, factors = gp_factor(number, out / name)
        records.append({"name": name, "label": label, "number": str(number),
                        "curve_uid": uid, "n": str(n) if n else None,
                        "receipt": receipt, "factors": factors})
        (out / "progress.json").write_text(json.dumps(records, indent=2) + "\n")
    (out / "results.json").write_text(json.dumps(records, indent=2) + "\n")
    command = ["sage", "-python", str(HERE / "verify.py"), str(out)]
    check = subprocess.run(command, text=True, capture_output=True)
    (out / "verifier.stdout").write_text(check.stdout)
    (out / "verifier.stderr").write_text(check.stderr)
    (out / "verifier_receipt.json").write_text(json.dumps({
        "command": command, "exit_code": check.returncode,
        "verifier_sha256": sha(HERE / "verify.py"),
        "stdout_sha256": sha(out / "verifier.stdout"),
        "stderr_sha256": sha(out / "verifier.stderr"),
    }, indent=2) + "\n")
    if check.returncode:
        raise RuntimeError("Sage verification failed")
    if any(x["factors"] is None for x in records):
        (out / "censored.json").write_text(json.dumps({
            "censored_cases": [x["name"] for x in records if x["factors"] is None],
            "verified_completed_cases": len([x for x in records if x["factors"] is not None]),
        }, indent=2) + "\n")
    else:
        (out / "complete.ok").write_text("verified\n")
    print(out)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ORDER_CERT_AUDIT_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
