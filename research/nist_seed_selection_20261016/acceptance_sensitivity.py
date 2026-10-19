#!/usr/bin/env python3
"""Reapply stricter public-reference choices to fully counted survivors."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LMAX = (1, 7, 31, 255)
R_EXPONENT = (160, 180, 200)
MOV_THRESHOLD = (20, 50, 100)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def largest_factor(h):
    largest = 1
    for factor in range(2, 256):
        while h % factor == 0:
            h //= factor
            largest = factor
    if h != 1:
        raise ArithmeticError("survivor cofactor is not 255-smooth")
    return largest


def first_mov_failure(q, n):
    value = 1
    for degree in range(1, max(MOV_THRESHOLD) + 1):
        value = value * q % n
        if value == 1:
            return degree
    return None


def annotate(roots, q):
    prepared = []
    for root in roots:
        h = int(root["smooth_cofactor"])
        n = int(root["prime_subgroup"])
        prepared.append({"largest_factor": largest_factor(h), "n": n,
                         "size_ok": n * n > 16 * q,
                         "first_mov_failure": first_mov_failure(q, n)})
    return prepared


def qualify(roots, lmax, exponent, B):
    return any(root["largest_factor"] <= lmax and root["n"] > (1 << exponent) and
               root["size_ok"] and (root["first_mov_failure"] is None or
                                    root["first_mov_failure"] > B)
               for root in roots)


def main():
    output = ROOT / "raw" / "acceptance_sensitivity.json"
    if output.exists():
        raise FileExistsError(output)
    x9_path = ROOT / "raw" / "x9_campaign" / "x9_summary.json"
    binary_path = ROOT / "raw" / "analysis_summary.json"
    x9 = json.loads(x9_path.read_text())
    binary = json.loads(binary_path.read_text())
    targets = {item["name"]: item for item in json.loads((ROOT / "targets.json").read_text())}
    grid = [(lmax, exponent, B) for lmax in LMAX for exponent in R_EXPONENT for B in MOV_THRESHOLD]
    counts = {}
    for name, target in targets.items():
        mappings = {}
        if target["kind"] == "binary":
            survivors = [{"roots": [{"smooth_cofactor": item["cofactor"],
                                      "prime_subgroup": item["prime_subgroup"]}]}
                         for item in binary["binary"][name]["earlier_x9_255_reference"]]
            mappings["binary_published_compatible"] = survivors
            q = 1 << target["m"]
        else:
            q = int(target["p"])
            for mapping, item in x9["named_targets"][name]["mappings"].items():
                mappings[mapping] = item["earlier_reference_eligible"]
        counts[name] = {}
        for mapping, survivors in mappings.items():
            prepared = [annotate(item["roots"], q) for item in survivors]
            counts[name][mapping] = {f"lmax={lmax};r_gt_2^{exponent};MOV_B={B}":
                                     sum(qualify(roots, lmax, exponent, B)
                                         for roots in prepared)
                                     for lmax, exponent, B in grid}
    result = {"x9_summary_sha256": digest(x9_path), "binary_summary_sha256": digest(binary_path),
              "grid": {"lmax": LMAX, "r_min_exponent_strict": R_EXPONENT, "mov_B": MOV_THRESHOLD},
              "earlier_eligible_seed_counts": counts,
              "interpretation": "Nested stricter reference settings only; historical lmax, rmin, and MOV B remain unknown."}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(output), "sha256": digest(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
