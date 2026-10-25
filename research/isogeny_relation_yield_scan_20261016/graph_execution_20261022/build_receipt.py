"""Record the two local control binaries after their fixed source builds."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEGACY = ROOT / "research/conductor_relation_yield_20261014"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def version(command):
    return subprocess.check_output(command, text=True).splitlines()[0]


def main():
    print(json.dumps({"schema": "ectd.graph-control-build.v1",
                      "platform": platform.platform(),
                      "rustc_version": version(["rustc", "--version"]),
                      "clang_version": version(["clang++", "--version"]),
                      "collector_command": ["rustc", "--edition=2021", "-O",
                                            "research/conductor_relation_yield_20261014/collector.rs",
                                            "-o", "/tmp/ectd-graph-collector"],
                      "count_command": ["clang++", "-std=c++17", "-O2",
                                        "research/conductor_relation_yield_20261014/count_verify.cpp",
                                        "-o", "/tmp/ectd-graph-count"],
                      "collector_source_sha256": sha(LEGACY / "collector.rs"),
                      "count_source_sha256": sha(LEGACY / "count_verify.cpp"),
                      "collector_binary_sha256": sha(HERE / "collector.bin"),
                      "count_binary_sha256": sha(HERE / "count_verify.bin")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
