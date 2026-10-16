#!/usr/bin/env python3
"""Replay every raw seed through the host C library's srand48/lrand48."""

import ctypes
import hashlib
import json
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / "raw" / "libc_replay.json"
    if output.exists():
        raise FileExistsError(output)
    libc = ctypes.CDLL(None)
    libc.srand48.argtypes = [ctypes.c_long]
    libc.srand48.restype = None
    libc.lrand48.argtypes = []
    libc.lrand48.restype = ctypes.c_long
    targets = json.loads((ROOT / "targets.json").read_text())
    source = ROOT / "raw" / "candidates.jsonl"
    by_target = {}
    with source.open() as rows:
        current = json.loads(next(rows))
        for target in targets:
            name = target["name"]
            binary = target["kind"] == "binary"
            libc.srand48(target["unix_time"] // 2 if binary else target["unix_time"])
            matched = 0
            for index in range(1, target["candidate_index"] + 1):
                if current["target"] != name or current["index"] != index:
                    raise ArithmeticError(f"row order mismatch: {name}:{index}")
                outputs = 5 if binary else 20
                seed = "".join(f"{libc.lrand48():08X}" if binary else
                               f"{libc.lrand48() >> 23:02X}" for _ in range(outputs))
                if seed != current["seed"]:
                    raise ArithmeticError(f"libc stream mismatch: {name}:{index}")
                matched += 1
                try:
                    current = json.loads(next(rows))
                except StopIteration:
                    current = None
            by_target[name] = matched
        if current is not None:
            raise ArithmeticError("trailing candidate rows")
    result = {"candidate_sha256": digest(source), "platform": platform.platform(),
              "library": "ctypes.CDLL(None).srand48/lrand48",
              "matched_by_target": by_target, "total_matched": sum(by_target.values()),
              "all_matched": sum(by_target.values()) == 31945}
    if not result["all_matched"]:
        raise ArithmeticError("candidate grid incomplete")
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"total_matched": result["total_matched"],
                      "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
