#!/usr/bin/env python3
"""Run the two capped PARI/GP twist residual factorizations in FACTOR_PROTOCOL.md."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
TRAITS = HERE.parent / "nist_seed_skipped_curves_20261016" / "traits.json"
TRAITS_SHA256 = "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67"
OUTPUT = HERE / "factor_runs"
TIMEOUT_SECONDS = 300
COMMAND = ["gp", "-q", "-s", "134217728"]


def load_cases() -> list[tuple[str, dict]]:
    raw = TRAITS.read_bytes()
    if hashlib.sha256(raw).hexdigest() != TRAITS_SHA256:
        raise ValueError("The exact trait input has changed")
    source = json.loads(raw)
    controls = source["published_controls"]
    omitted = [r for r in source["unpublished_candidates"]
               if r["timestamp"] == 863711343 and r["seed_ordinal_one_based"] == 2682]
    if len(omitted) != 1:
        raise ValueError("Expected one block-2682 candidate")
    cases = [("prime239v2", controls["prime239v2"]), ("skip239_2682", omitted[0])]
    for name, row in cases:
        if row["seed_ordinal_one_based"] != (2320 if name == "prime239v2" else 2682):
            raise ValueError("Unexpected ordinal")
        twist = int(row["twist_order_hex"], 0)
        residual = int(row["twist_unfactored_rest_hex"], 0)
        known = 1
        for factor, exponent in row["twist_small_factors_to_10000"]:
            known *= int(factor) ** int(exponent)
        if known * residual != twist:
            raise ValueError(f"{name}: old trial factors do not reconstruct the twist order")
    return cases


def decode(value: bytes | str | None) -> str:
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value


def one_case(name: str, row: dict, gp_version: str) -> dict:
    residual = int(row["twist_unfactored_rest_hex"], 0)
    twist = int(row["twist_order_hex"], 0)
    program = (f"N={residual}; F=factor(N);\n"
               'for(i=1,matsize(F)[1],print("FACTOR,",F[i,1],",",F[i,2],",",isprime(F[i,1])));\n'
               'print("DONE");\n')
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    try:
        proc = subprocess.run(COMMAND, input=program, capture_output=True,
                              text=True, timeout=TIMEOUT_SECONDS, check=False)
        elapsed = time.monotonic() - tick
        stdout, stderr = proc.stdout, proc.stderr
        exit_code, timed_out = proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - tick
        stdout, stderr = decode(exc.stdout), decode(exc.stderr)
        exit_code, timed_out = None, True
    factors = []
    complete = not timed_out and exit_code == 0 and "DONE" in stdout.splitlines()
    if complete:
        for line in stdout.splitlines():
            if not line.startswith("FACTOR,"):
                continue
            parts = line.split(",")
            if len(parts) != 4:
                complete = False
                break
            factors.append({"prime": int(parts[1]), "exponent": int(parts[2]),
                            "gp_isprime": int(parts[3])})
        product = 1
        for item in factors:
            product *= item["prime"] ** item["exponent"]
        complete = complete and bool(factors) and product == residual
        complete = complete and all(item["gp_isprime"] == 1 for item in factors)
    else:
        product = None
    return {
        "name": name,
        "ordinal": row["seed_ordinal_one_based"],
        "curve_uid": row["identity"]["curve_uid"],
        "input_sha256": TRAITS_SHA256,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "started_utc": started,
        "elapsed_wall_seconds": elapsed,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "gp_version": gp_version,
        "command": COMMAND,
        "stdin": program,
        "timeout_seconds": TIMEOUT_SECONDS,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout": stdout,
        "stderr": stderr,
        "residual_hex": hex(residual),
        "twist_order_hex": hex(twist),
        "returned_factors": factors,
        "returned_product_hex": hex(product) if product is not None else None,
        "verified_complete": complete,
    }


def main() -> None:
    cases = load_cases()
    OUTPUT.mkdir(exist_ok=True)
    for name, _ in cases:
        if (OUTPUT / f"{name}.json").exists():
            raise FileExistsError("Write-once factorization output already exists")
    version = subprocess.run(["gp", "--version"], capture_output=True,
                             text=True, check=True).stdout.strip()
    for name, row in cases:
        print(f"starting {name}", flush=True)
        result = one_case(name, row, version)
        (OUTPUT / f"{name}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(f"{name}: complete={result['verified_complete']} elapsed={result['elapsed_wall_seconds']:.3f}s",
              flush=True)


if __name__ == "__main__":
    main()
