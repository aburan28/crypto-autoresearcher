"""Benign synthetic subprocess fixture for tests/test_finite_yaml_locked_v1.py.

This script performs NO scientific computation and imports NOTHING from this
repository -- it is standard-library-only, exactly the "inner scientific
child may remain absolute-python -I -S -B and standard-library-only" shape
required by DEC-20260908-195f0f's engineering_successor.lock_compatibility,
so it can be launched the same way a real locked child would be, without
being one. It exists solely to let tests/test_finite_yaml_locked_v1.py
exercise harness/finite_yaml_locked_v1.py's real process-launch, timeout,
and failure-classification code paths (reused from
src/crypto_autoresearcher/runner.py's `_run_child`) against a fixture whose
behavior is fully known in advance.

Modes (selected by the single positional argument):

  success   -- writes a small deterministic JSON object to stdout, exits 0.
  failure   -- writes a message to stderr, exits 2.
  timeout   -- sleeps far longer than any test's configured timeout, so the
               wrapper's timeout-and-kill path is exercised deterministically.
  crash     -- raises an uncaught Python exception (nonzero exit via
               traceback), exercising a different stderr shape than `failure`.
  memory    -- allocates and touches a growing synthetic byte buffer (never
               curve/divisor/section data) until killed or a generous
               internal ceiling is hit, so a test can configure a small
               resource_policy.memory_bytes and observe the wrapper's own
               memory-limit enforcement/detection rather than this script's.

No mode reads or writes anything outside the current working directory that
the wrapper (not this script) is responsible for choosing and pre-creating.
"""
from __future__ import annotations

import json
import sys
import time


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: worker.py {success|failure|timeout|crash}", file=sys.stderr)
        return 64
    mode = argv[0]
    if mode == "success":
        payload = {
            "status": "ok",
            "synthetic": True,
            "kind": "benign_fixture",
            "scientific_content": False,
            "note": "no curve, divisor, section, or scientific enumeration occurred",
        }
        print(json.dumps(payload, sort_keys=True))
        return 0
    if mode == "failure":
        print("synthetic deliberate failure: fixture exit", file=sys.stderr)
        return 2
    if mode == "timeout":
        # Deliberately long relative to any test timeout; the wrapper is
        # expected to kill the process group before this returns.
        time.sleep(3600)
        return 0
    if mode == "crash":
        raise RuntimeError("synthetic deliberate crash: fixture exception")
    if mode == "memory":
        chunks = []
        try:
            # 256 x 4 MiB touched chunks (~1 GiB) -- far above any small test
            # memory_bytes ceiling, so either RLIMIT_AS or the wrapper's own
            # /proc-sampled peak-RSS check should intervene first.
            for _ in range(256):
                block = bytearray(4 * 1024 * 1024)
                for offset in range(0, len(block), 4096):
                    block[offset] = 1
                chunks.append(block)
                time.sleep(0.01)
        except MemoryError:
            print("synthetic MemoryError observed in fixture", file=sys.stderr)
            return 3
        return 0
    print(f"unknown mode: {mode!r}", file=sys.stderr)
    return 65


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
