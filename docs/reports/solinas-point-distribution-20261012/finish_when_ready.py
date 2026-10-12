"""Wait only for the authorized numerical run, then execute dependent steps."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUN = REPO / "tasks/solinas_point_distribution/runs/point-distribution-20261012"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True)
    args = parser.parse_args()
    proc = Path("/proc") / str(args.pid)
    while proc.exists():
        try:
            if (proc / "stat").read_text().split()[2] == "Z":
                break
        except FileNotFoundError:
            break
        time.sleep(2)
    receipt = json.loads((RUN / "receipt.json").read_text())
    if receipt["status"] != "complete":
        raise SystemExit("measurement failures retained; primary analysis refused")
    shutil.copyfile("/workspace/solinas-point-distribution-20261012.log", RUN / "run.log")
    commands = [
        [sys.executable, "tasks/solinas_point_distribution/verify.py", str(RUN)],
        [sys.executable, "tasks/solinas_point_distribution/analyze.py", str(RUN)],
        [sys.executable, "tasks/solinas_point_distribution/artifact_tools/records.py", "pack", str(RUN)],
        [sys.executable, "tasks/solinas_point_distribution/artifact_tools/records.py", "unpack", str(RUN)],
        [sys.executable, str(HERE / "build_report.py")],
    ]
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
    for command in commands:
        print(json.dumps({"command": command, "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}), flush=True)
        subprocess.run(command, cwd=REPO, env=env, check=True)
    print("Data checks, fixed analysis, lossless shards and derived report finished; PDF inspection and bundle remain.", flush=True)


if __name__ == "__main__":
    main()
