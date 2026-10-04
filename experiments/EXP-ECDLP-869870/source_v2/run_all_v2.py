"""Drive the 16 enumerated v2 fixture cells sequentially (max_concurrent 1).

A failed_infrastructure cell is recorded and the remaining enumerated
runs continue. Never overwrites an existing run directory.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = [
    ("RUN-ECDLP-869870-V2-splitmix-s1", "splitmix64", 1),
    ("RUN-ECDLP-869870-V2-splitmix-s2", "splitmix64", 2),
    ("RUN-ECDLP-869870-V2-splitmix-s3", "splitmix64", 3),
    ("RUN-ECDLP-869870-V2-splitmix-s4", "splitmix64", 4),
    ("RUN-ECDLP-869870-V2-splitmix-s5", "splitmix64", 5),
    ("RUN-ECDLP-869870-V2-splitmix-s6", "splitmix64", 6),
    ("RUN-ECDLP-869870-V2-splitmix-s7", "splitmix64", 7),
    ("RUN-ECDLP-869870-V2-splitmix-s8", "splitmix64", 8),
    ("RUN-ECDLP-869870-V2-murmur3-s1", "murmur3_fmix64", 1),
    ("RUN-ECDLP-869870-V2-murmur3-s2", "murmur3_fmix64", 2),
    ("RUN-ECDLP-869870-V2-murmur3-s3", "murmur3_fmix64", 3),
    ("RUN-ECDLP-869870-V2-murmur3-s4", "murmur3_fmix64", 4),
    ("RUN-ECDLP-869870-V2-murmur3-s5", "murmur3_fmix64", 5),
    ("RUN-ECDLP-869870-V2-murmur3-s6", "murmur3_fmix64", 6),
    ("RUN-ECDLP-869870-V2-murmur3-s7", "murmur3_fmix64", 7),
    ("RUN-ECDLP-869870-V2-murmur3-s8", "murmur3_fmix64", 8),
]


def main():
    py = sys.executable
    wrapper = os.path.join(HERE, "run.py")
    results = []
    for run_id, mixer, seed in RUNS:
        cmd = [
            py, wrapper,
            "--run-id", run_id,
            "--script", "run_generic_exact.py",
            "--kind", "fixture",
            "--note", f"v2 fixture mixer={mixer} seed={seed}",
            "--",
            "--mixer", mixer,
            "--seed", str(seed),
        ]
        print("===", " ".join(cmd), flush=True)
        rc = subprocess.call(cmd, cwd=HERE)
        results.append((run_id, rc))
        print(f"=== {run_id} rc={rc}", flush=True)
    print("SUMMARY", results, flush=True)
    # do not fail the driver: remaining runs already continued
    sys.exit(0)


if __name__ == "__main__":
    main()
