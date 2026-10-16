#!/usr/bin/env python3
"""Independently replay the six published May 1997 FreeLIP point examples."""

import hashlib
import json
import platform
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TARGETS = REPO / "research/nist_seed_selection_20261016/targets.json"
OUTPUT = HERE / "raw/freelip_basepoint_controls.json"
SOURCE_URL = "https://www.anthropic.com/research/ecdsa-curve-origins"
MODULUS = 2**107 - 1
MULTIPLIER = pow(3, 121, MODULUS)
CASES = (
    ("P-192", 20000, 2, 0x188da80eb03090f67cbf20eb43a18800f4ff0afd82ff1012),
    ("prime239v1", 20420, 3, 0xffa963cdca8816ccc33b8642bedf905c3d358573d3f27fbbd3b3cb9aaaf),
    ("prime239v2", 20507, 2, 0x38af09d98727705120c921bb5e9e26296a3cdcf2f35757a0eafd87b830e7),
    ("prime239v3", 20509, 1, 0x6768ae8e18bb92cfcf005c949aa2c6d94853d0e660bbf854b1c9505fe95a),
    ("prime192v2", 20512, 5, 0xeea2bae7e1497842f2de7769cfe9c989c072ad696f48034a),
    ("prime192v3", 20517, 1, 0x7d29778100c65a1da1783716588dce2b8b4aee8e228f1896),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_x(seed, p, b):
    state = seed
    def draw():
        nonlocal state
        state = state * MULTIPLIER % MODULUS
        return state & ((1 << 26) - 1)
    for _ in range(7):
        draw()
    limbs = (p.bit_length() + 25) // 26 + 1
    for attempt in range(1, 1001):
        x = 0
        for _ in range(limbs):
            x = (x << 26) | draw()
        x %= p
        rhs = (x*x*x - 3*x + b) % p
        if pow(rhs, (p - 1) // 2, p) == 1:
            return x, attempt
    raise TimeoutError("no point in first 1000 candidates")


def main():
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    targets = {item["name"]: item for item in json.loads(TARGETS.read_text())}
    rows = []
    for name, seed, expected_tries, expected_x in CASES:
        p, b = int(targets[name]["p"]), int(targets[name]["published_b"])
        x, tries = first_x(seed, p, b)
        altered_x, altered_tries = first_x(seed + 1, p, b)
        row = {"name": name, "freelip_seed": seed, "tries": tries,
               "expected_tries": expected_tries,
               "x": hex(x), "published_x": hex(expected_x),
               "point_x_matches": x == expected_x,
               "tries_match": tries == expected_tries,
               "on_curve_x": pow((x*x*x - 3*x + b) % p, (p-1)//2, p) == 1,
               "altered_seed": seed + 1, "altered_x": hex(altered_x),
               "altered_tries": altered_tries,
               "altered_seed_differs": altered_x != expected_x}
        rows.append(row)
    result = {"status": "controls_passed" if all(
                  row["point_x_matches"] and row["tries_match"] and row["on_curve_x"]
                  and row["altered_seed_differs"]
                  for row in rows) else "control_failure",
              "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "command": sys.argv, "python": platform.python_version(),
              "script_sha256": digest(Path(__file__)),
              "targets_sha256": digest(TARGETS),
              "source_url": SOURCE_URL, "modulus": str(MODULUS),
              "multiplier": str(MULTIPLIER), "discarded_draws": 7,
              "limb_bits": 26, "candidate_cap_per_case": 1000,
              "rows": rows}
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "output": str(OUTPUT),
                      "sha256": digest(OUTPUT), "matched": sum(
                          row["point_x_matches"] and row["tries_match"] for row in rows)}))
    if result["status"] != "controls_passed":
        raise AssertionError("published FreeLIP control failed")


if __name__ == "__main__":
    main()
