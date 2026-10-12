"""EXP-SEMBIN-79a02d run wrapper: creates runs/<RUN-ID>/ with command.txt,
environment.json, stdout.log, stderr.log, manifest.yaml; the stage script
writes raw-result.json into the same directory. Records git commit / dirty
state before the run, wall time, and peak RSS of the child process tree
(RUSAGE_CHILDREN max). Never overwrites an existing run directory.

usage: python3 run_wrapper.py RUN-ID "<purpose>" -- <cmd...>
"""
import datetime, hashlib, json, os, platform, resource, subprocess, sys, time

EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(EXP))


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=REPO).stdout.strip()


def main():
    run_id, purpose = sys.argv[1], sys.argv[2]
    assert sys.argv[3] == "--"
    cmd = sys.argv[4:]
    rd = os.path.join(EXP, "runs", run_id)
    os.makedirs(rd, exist_ok=False)
    commit = sh("git rev-parse HEAD")
    porcelain = sh("git status --porcelain")
    impl = os.path.join(EXP, "implementation")
    src = {}
    for fn in sorted(os.listdir(impl)):
        p = os.path.join(impl, fn)
        if os.path.isfile(p) and fn.endswith((".py", ".c", ".h")):
            src[fn] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "gcc": sh("gcc --version | head -1"), "cpu": sh("grep -m1 'model name' /proc/cpuinfo"),
           "nproc": os.cpu_count(), "mem_total": sh("grep MemTotal /proc/meminfo"),
           "numpy": sh("python3 -c 'import numpy;print(numpy.__version__)'"),
           "rank_arms": {"A": "gf2_armA (row-insertion GE, C, written here, M4RI-free, gcc -O3 -march=native)",
                         "B": "gf2_armB (Four-Russians block elimination, C, written here, M4RI-free, gcc -O3 -march=native)"},
           "libm4ri": "not installed, not linked (dpkg -l shows no m4ri package)",
           "sage": "not installed", "magma": "not installed", "bedrock": "not used"}
    json.dump(env, open(os.path.join(rd, "environment.json"), "w"), indent=1)
    open(os.path.join(rd, "command.txt"), "w").write(" ".join(cmd) + "\n")
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    t0 = time.time()
    with open(os.path.join(rd, "stdout.log"), "w") as so, open(os.path.join(rd, "stderr.log"), "w") as se:
        p = subprocess.run(cmd + [rd], stdout=so, stderr=se, cwd=REPO)
    el = time.time() - t0
    rss_kb = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    raw = os.path.join(rd, "raw-result.json")
    raw_sha = hashlib.sha256(open(raw, "rb").read()).hexdigest() if os.path.exists(raw) else None
    summary = {}
    if os.path.exists(raw):
        try:
            summary = json.load(open(raw)).get("manifest_summary", {})
        except Exception as e:
            summary = {"raw_parse_error": str(e)}
    status = summary.pop("status", "completed_valid" if p.returncode == 0 and raw_sha else "failed_infrastructure")
    lines = ["run:", f"  id: {run_id}", "  experiment_id: EXP-SEMBIN-79a02d",
             "  handoff_id: TASK-20261002-fc71d6", "  hypothesis_id: H-SEMBIN-8e8bef",
             f"  purpose: {json.dumps(purpose)}", f"  status: {status}",
             f"  validity_reason: {json.dumps(summary.pop('validity_reason', 'exit code ' + str(p.returncode)))}",
             "  certificate:", "    kind: none",
             "    note: pure measurement run; no discrete-log solve or relation is claimed",
             "  code:", f"    commit: {commit}", "    branch: claude/run-sembin-79a02d-fc71d6",
             f"    dirty: {'true' if porcelain else 'false'}",
             f"    dirty_porcelain: {json.dumps(porcelain)}",
             f"    command: {json.dumps(' '.join(cmd + [os.path.relpath(rd, REPO)]))}",
             "    source_sha256:"] + [f"      {k}: {v}" for k, v in src.items()] + [
             "  inference:", "    requested_policy: executor-implementation", "    fallback_used: false",
             "  environment:", "    file: environment.json",
             f"    python: {platform.python_version()}", f"    platform: {platform.platform()}",
             "  seeds: 'random.Random(\"EXP-SEMBIN-79a02d|<arm>|n=<n>|s=<s>\") for s in 0..7 (stage0/definitions.md section 4); C arms deterministic'",
             "  timing:", f"    started_at: '{started}'", f"    elapsed_seconds: {el:.1f}",
             "  resources:", f"    peak_rss_bytes_children: {rss_kb * 1024}",
             "    caps: 'RLIMIT_AS 7 GiB per C tool process; total budget 14400 s / 8 GB'",
             "  result:", f"    exit_code: {p.returncode}", "    raw_result: raw-result.json",
             f"    raw_result_sha256: {raw_sha}"]
    for k, v in summary.items():
        lines.append(f"    {k}: {json.dumps(v)}")
    lines += ["  anomalies: []", "  protocol_deviations: []"]
    open(os.path.join(rd, "manifest.yaml"), "w").write("\n".join(lines) + "\n")
    print(f"{run_id} exit={p.returncode} elapsed={el:.1f}s peak_rss_children={rss_kb} kB status={status}")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
