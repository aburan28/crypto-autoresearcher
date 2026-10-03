"""AMD-20261002-236691 E-2: parity check P-FA of finalize_attempt_v6.py.  TASK-20261002-71b610.

Standard library plus PyYAML.  Run once, before the helper's first real use:

  check_parity_v6.py --scratch <scratch>

(3) Builds <scratch>/fa/A/attempt-1/ and <scratch>/fa/B/attempt-1/ (refuses if <scratch>/fa
    exists) and byte-copies into each exactly jobs-index.json, jobs-spec.json, command.txt and
    environment.json of the archived R10 attempt
    experiments/EXP-PFDR-011cd0/runs/RUN-PFDR-011cd0-fix-check/attempt-1/ (read-only).
(4) Runs, one after the other, the unchanged run_jobs.py finalize-attempt on A and
    finalize_attempt_v6.py finalize-attempt on B (no --inputs-json; --spec-command P-FA).  Both
    must exit 0.  This tool writes nothing in the repository between them.
(5) Compares MA = A/manifest.yaml["run"] with MB = B/manifest.yaml["run"] and the two
    raw-result.json files; canon() replaces "/fa/A/" by "/fa/B/" in every string and key.
(6) Controls N-PFA-1 (status flipped) and N-PFA-2 (first character of the sha256 of the first
    code.source_sha256 entry advanced by one hex digit), in memory, after (5).
(7) Writes experiments/EXP-PFDR-011cd0/amd-236691/parity-fa.json once (open mode 'x').
Exit 0 iff P-FA passes and both controls behave as stated; otherwise 1.
"""
import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys

import yaml

REPO = "/home/user/crypto-autoresearcher"
EXPDIR = "experiments/EXP-PFDR-011cd0"
PY = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python"
SOURCE = f"{EXPDIR}/runs/RUN-PFDR-011cd0-fix-check/attempt-1"
COPY_FILES = ["jobs-index.json", "jobs-spec.json", "command.txt", "environment.json"]
RUN_JOBS = f"{EXPDIR}/run_jobs.py"
HELPER = f"{EXPDIR}/amd-236691/finalize_attempt_v6.py"
AMENDMENT = f"{EXPDIR}/amendments/AMD-20261002-236691.yaml"
OUT = f"{EXPDIR}/amd-236691/parity-fa.json"
RUN_ID = "RUN-PFDR-011cd0-fix-check"
EXPECTED_DIFF = ["protocol", "task_id"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canon(x):
    if isinstance(x, str):
        return x.replace("/fa/A/", "/fa/B/")
    if isinstance(x, dict):
        return {canon(k): canon(v) for k, v in x.items()}
    if isinstance(x, list):
        return [canon(v) for v in x]
    return x


def compare(ma, mb, v1_block, v6_block, v6_task):
    keys_equal = set(ma) == set(mb)
    differing = sorted(k for k in set(ma) | set(mb) if k not in ma or k not in mb or canon(ma[k]) != mb[k])
    checks = {
        "key_sets_equal": keys_equal,
        "A_protocol_is_run_jobs_version_1_block": ma.get("protocol") == v1_block,
        "A_protocol_version_1_amendments_empty": (isinstance(ma.get("protocol"), dict)
                                                  and ma["protocol"].get("version") == 1
                                                  and ma["protocol"].get("amendments") == []),
        "A_task_id_is_TASK-20261001-7f7a33": ma.get("task_id") == "TASK-20261001-7f7a33",
        "B_protocol_is_manifest_protocol_block_v6": mb.get("protocol") == v6_block,
        "B_task_id_is_TASK-20261002-71b610": mb.get("task_id") == "TASK-20261002-71b610" == v6_task,
        "every_other_key_equal_after_canon": all(canon(ma[k]) == mb[k] for k in set(ma) & set(mb)
                                                 if k not in EXPECTED_DIFF),
        "differing_keys_exactly_protocol_task_id": differing == EXPECTED_DIFF,
    }
    return all(checks.values()), differing, checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    os.chdir(REPO)
    if os.path.exists(OUT):
        print(f"refusing: {OUT} exists", file=sys.stderr)
        return 3
    fa = os.path.join(a.scratch, "fa")
    if os.path.exists(fa):
        print(f"refusing: {fa} exists", file=sys.stderr)
        return 3
    dirs = {s: os.path.join(fa, s, "attempt-1") for s in ("A", "B")}
    for s, d in dirs.items():
        os.makedirs(d)
        for f in COPY_FILES:
            shutil.copyfile(os.path.join(REPO, SOURCE, f), os.path.join(d, f))
    copied = {f: {"source": sha256(os.path.join(SOURCE, f)), "A": sha256(os.path.join(dirs["A"], f)),
                  "B": sha256(os.path.join(dirs["B"], f))} for f in COPY_FILES}
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    cmds = {"A": [PY, RUN_JOBS, "finalize-attempt", "--attempt-dir", dirs["A"], "--run-id", RUN_ID,
                  "--spec-command", "P-FA"],
            "B": [PY, HELPER, "finalize-attempt", "--attempt-dir", dirs["B"], "--run-id", RUN_ID,
                  "--spec-command", "P-FA"]}
    runs = {}
    for s in ("A", "B"):
        r = subprocess.run(cmds[s], cwd=REPO, env=env, capture_output=True, text=True)
        runs[s] = {"command": cmds[s], "exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
                   "ended_at": now()}
    both_exit_0 = runs["A"]["exit_code"] == 0 and runs["B"]["exit_code"] == 0
    rep = {"what": "AMD-20261002-236691 E-2 parity check P-FA", "task_id": "TASK-20261002-71b610",
           "created_at": now(), "source": SOURCE, "scratch": fa,
           "tools_sha256": {RUN_JOBS: sha256(RUN_JOBS), HELPER: sha256(HELPER),
                            f"{EXPDIR}/amd-236691/check_parity_v6.py": sha256(os.path.abspath(__file__))},
           "amendment_sha256": sha256(AMENDMENT),
           "copied_files_sha256": copied, "runs": runs, "both_exit_0": both_exit_0}
    passed = False
    if both_exit_0:
        spec = importlib.util.spec_from_file_location("run_jobs_pfa", os.path.join(REPO, RUN_JOBS))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        v1_block = mod.PROTOCOL
        amd = yaml.safe_load(open(AMENDMENT))["protocol_amendment"]
        v6_block, v6_task = amd["manifest_protocol_block_v6"], amd["manifest_task_id_v6"]
        ma = yaml.safe_load(open(os.path.join(dirs["A"], "manifest.yaml")))["run"]
        mb = yaml.safe_load(open(os.path.join(dirs["B"], "manifest.yaml")))["run"]
        ra = json.load(open(os.path.join(dirs["A"], "raw-result.json")))
        rb = json.load(open(os.path.join(dirs["B"], "raw-result.json")))
        ok, differing, checks = compare(ma, mb, v1_block, v6_block, v6_task)
        raw_equal = canon(ra) == rb
        b0 = {"pass": ok and raw_equal, "differing_keys": differing, "checks": checks,
              "raw_result_equal_after_canon": raw_equal}
        # N-PFA-1: status flipped in a copy of MB
        n1 = copy.deepcopy(mb)
        old_status = n1["status"]
        n1["status"] = "invalid" if old_status == "completed_valid" else "completed_valid"
        ok1, diff1, _ = compare(ma, n1, v1_block, v6_block, v6_task)
        c1 = {"planted": f"status {old_status!r} -> {n1['status']!r}", "comparison_pass": ok1,
              "differing_keys": diff1, "expected_differing_keys": sorted(EXPECTED_DIFF + ["status"]),
              "behaved_as_stated": (not ok1) and diff1 == sorted(EXPECTED_DIFF + ["status"])}
        # N-PFA-2: first character of the sha256 of the first code.source_sha256 entry (file order)
        n2 = copy.deepcopy(mb)
        first_key = next(iter(n2["code"]["source_sha256"]))
        ent = n2["code"]["source_sha256"][first_key]
        old = ent["sha256"] if isinstance(ent, dict) else ent
        new = format((int(old[0], 16) + 1) % 16, "x") + old[1:]
        if isinstance(ent, dict):
            ent["sha256"] = new
        else:
            n2["code"]["source_sha256"][first_key] = new
        ok2, diff2, _ = compare(ma, n2, v1_block, v6_block, v6_task)
        c2 = {"planted": f"code.source_sha256[{first_key!r}].sha256 first character {old[0]!r} -> {new[0]!r}",
              "comparison_pass": ok2, "differing_keys": diff2,
              "expected_differing_keys": sorted(EXPECTED_DIFF + ["code"]),
              "behaved_as_stated": (not ok2) and diff2 == sorted(EXPECTED_DIFF + ["code"])}
        passed = b0["pass"] and b0["differing_keys"] == EXPECTED_DIFF and c1["behaved_as_stated"] and c2["behaved_as_stated"]
        rep.update({
            "manifests_sha256": {"A": sha256(os.path.join(dirs["A"], "manifest.yaml")),
                                 "B": sha256(os.path.join(dirs["B"], "manifest.yaml"))},
            "raw_results_sha256": {"A": sha256(os.path.join(dirs["A"], "raw-result.json")),
                                   "B": sha256(os.path.join(dirs["B"], "raw-result.json"))},
            "compared_keys": sorted(set(ma) | set(mb)),
            "differing_keys": differing,
            "controls": {"B0-PFA": b0, "N-PFA-1": c1, "N-PFA-2": c2}})
    rep["pass"] = passed
    with open(OUT, "x") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps({"pass": passed, "differing_keys": rep.get("differing_keys"),
                      "controls": {k: v.get("behaved_as_stated", v.get("pass"))
                                   for k, v in rep.get("controls", {}).items()}}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
