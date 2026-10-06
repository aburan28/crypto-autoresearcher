"""AMD-20261002-236691 E-1: the attempt manifest writer of protocol version 6.  TASK-20261002-71b610.

Usage:  finalize_attempt_v6.py finalize-attempt <run_jobs.py finalize-attempt options>
        (--attempt-dir, --run-id, --location-kind, --spec-command, --inputs-json)

(1) Standard library plus PyYAML, plus the pinned run_jobs.py.
(2) Refuses (exit 3, nothing written) unless experiments/EXP-PFDR-011cd0/run_jobs.py has the
    pinned sha256 80f14ec1...
(3) Loads manifest_protocol_block_v6 and manifest_task_id_v6 from the amendment file; holds no
    copy of either value.
(4) Any first argument other than "finalize-attempt": exit 2, nothing written.
(5) Loads run_jobs.py and assigns exactly two module attributes, PROTOCOL and TASK.
(6) Calls run_jobs.py's own main() on the unchanged finalize-attempt command line and returns
    its return code; status, certificate, verify_solves, raw-result, refusal and checksum logic
    are run_jobs.py's own.
(7) After main() returned 0, re-reads <attempt>/manifest.yaml and exits 4 unless run.protocol
    and run.task_id equal the loaded values.  The manifest is never edited.
(8) Writes no file of its own; prints only run_jobs.py's output and, on exit 2, 3 or 4, one line.
"""
import hashlib
import importlib.util
import os
import sys

import yaml

REPO = "/home/user/crypto-autoresearcher"
RUN_JOBS = os.path.join(REPO, "experiments/EXP-PFDR-011cd0/run_jobs.py")
RUN_JOBS_SHA256 = "80f14ec1166893154a1feeb6cf64163b2371e45abfdb83abd3d61a0926626097"
AMENDMENT = os.path.join(REPO, "experiments/EXP-PFDR-011cd0/amendments/AMD-20261002-236691.yaml")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    args = sys.argv[1:]
    if not args or args[0] != "finalize-attempt":
        print("finalize_attempt_v6.py: exit 2: the only accepted first argument is finalize-attempt")
        return 2
    if sha256(RUN_JOBS) != RUN_JOBS_SHA256:
        print("finalize_attempt_v6.py: exit 3: run_jobs.py does not have the pinned sha256")
        return 3
    amd = yaml.safe_load(open(AMENDMENT))["protocol_amendment"]
    block = amd["manifest_protocol_block_v6"]
    task_id = amd["manifest_task_id_v6"]
    spec = importlib.util.spec_from_file_location("run_jobs", RUN_JOBS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PROTOCOL = block
    mod.TASK = task_id
    sys.argv = [RUN_JOBS, "finalize-attempt"] + args[1:]
    rc = mod.main()
    if rc != 0:
        return rc
    ad = None
    rest = args[1:]
    for i, x in enumerate(rest):
        if x == "--attempt-dir" and i + 1 < len(rest):
            ad = rest[i + 1]
        elif x.startswith("--attempt-dir="):
            ad = x.split("=", 1)[1]
    ad = ad if os.path.isabs(ad) else os.path.join(REPO, ad)
    run = yaml.safe_load(open(os.path.join(ad, "manifest.yaml")))["run"]
    if run.get("protocol") != block or run.get("task_id") != task_id:
        print("finalize_attempt_v6.py: exit 4: the written manifest does not carry the v6 protocol block and task id")
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
