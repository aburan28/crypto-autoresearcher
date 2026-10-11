"""Sequential runner for the declared F1 jobs (resolve/commands.yaml).
One job process at a time, each under checks/guard.py (nice 19, threads 1,
RSS stop 2.0e9). A job runs at most twice: attempt 1 automatically; attempt 2
only when named with --repeat LABEL (to separate nondeterminism from a defect).
Outputs go to <jobdir>/a<attempt>/ in the scratch directory. Appends one record
per attempt to resolve/run-log.jsonl."""
import json, os, subprocess, sys, time, datetime, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"
GUARD = os.path.join(HERE, "..", "checks", "guard.py")
LOG = os.path.join(HERE, "run-log.jsonl")


def done_attempts():
    out = {}
    if os.path.exists(LOG):
        for l in open(LOG):
            r = json.loads(l)
            out.setdefault(r["label"], []).append(r)
    return out


def run(job, attempt):
    d = f"{job['jobdir']}/a{attempt}"
    if os.path.exists(d):
        raise SystemExit(f"{d} exists; refusing to reuse an attempt directory")
    os.makedirs(d)
    argv = [x.replace(job["jobdir"] + "/", d + "/") for x in job["argv"]]
    cmd = [PY, GUARD, "--label", f"F1-{job['label']}-a{attempt}", "--", PY, os.path.join(HERE, "driver.py"),
           f"{d}/captures.jsonl"] + argv
    env = dict(os.environ, PYTHONPATH=WT + "/src", PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    start = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(f"{d}/stdout.log", "w") as so, open(f"{d}/stderr.log", "w") as se:
        rc = subprocess.call(cmd, cwd=d, env=env, stdout=so, stderr=se)
    rec = {"label": job["label"], "attempt": attempt, "dir": d, "argv": argv, "exit": rc,
           "start": start, "wall_seconds": round(time.time() - t0, 2)}
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps(rec), flush=True)
    return rc


def main():
    doc = yaml.safe_load(open(os.path.join(HERE, "commands.yaml")))
    jobs = {j["label"]: j for j in doc["jobs"]}
    if len(sys.argv) > 2 and sys.argv[1] == "--repeat":
        lab = sys.argv[2]
        att = done_attempts().get(lab, [])
        if len(att) != 1:
            raise SystemExit(f"{lab}: has {len(att)} attempts; a repeat needs exactly one")
        run(jobs[lab], 2)
        return
    da = done_attempts()
    for j in doc["jobs"]:
        if j["label"] in da:
            continue
        run(j, 1)


if __name__ == "__main__":
    main()
