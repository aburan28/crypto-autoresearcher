#!/usr/bin/env python3
"""Count a bounded range of published-stream curves and check public criteria.

Run through ``run_sage.sh``.  Each invocation writes one immutable JSONL shard;
an exception on one candidate is retained as INDETERMINATE and does not make
later candidates disappear.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from pathlib import Path

from cypari2 import Pari

from generate_candidates import modular_sqrt


ROOT = Path(__file__).resolve().parent
PRIMES_255 = tuple(n for n in range(2, 256) if all(n % d for d in range(2, math.isqrt(n) + 1)))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def field_for_binary(target: dict):
    from sage.all import EllipticCurve, GF, PolynomialRing

    m = target["m"]
    ring = PolynomialRing(GF(2), "z")
    polynomial_bits = int(target["polynomial"], 16)
    polynomial = sum((ring.gen() ** i for i in range(m + 1) if (polynomial_bits >> i) & 1), ring(0))
    field = GF(2**m, name="z", modulus=polynomial)

    def count(b: int) -> int:
        value = sum((field.gen() ** i for i in range(m) if (b >> i) & 1), field(0))
        curve = EllipticCurve(field, [field(1), field(1), field(0), field(0), value])
        return int(curve.cardinality())

    return count


def prime_order_count(pari: Pari, p: int, b: int) -> int:
    curve = pari.ellinit([0, 0, 0, pari.Mod(-3, p), pari.Mod(b, p)])
    return int(pari.ellcard(curve))


def proven_prime(pari: Pari, n: int) -> bool:
    if n < 2 or not bool(pari.ispseudoprime(n)):
        return False
    return bool(pari.isprime(n))


def checks(pari: Pari, order: int, q: int, family_cofactor: int) -> dict:
    if order <= 0 or (order - q - 1) ** 2 > 4 * q:
        raise ArithmeticError("point count violates Hasse bound")
    subgroup = order // family_cofactor if order % family_cofactor == 0 else None
    subgroup_prime = proven_prime(pari, subgroup) if subgroup is not None else False
    subgroup_size = subgroup is not None and subgroup > 2**160 and subgroup * subgroup > 16 * q
    mov20 = subgroup is not None and subgroup_prime and all(pow(q, i, subgroup) != 1 for i in range(1, 21))
    not_anomalous = order != q
    remainder = order
    smooth_cofactor = 1
    for small in PRIMES_255:
        while remainder % small == 0:
            remainder //= small
            smooth_cofactor *= small
    near_prime = proven_prime(pari, remainder)
    near_size = remainder > 2**160 and remainder * remainder > 16 * q
    near_mov20 = near_prime and all(pow(q, i, remainder) != 1 for i in range(1, 21))
    return {
        "order": str(order),
        "family_cofactor": family_cofactor,
        "family_subgroup": str(subgroup) if subgroup is not None else None,
        "family_subgroup_prime_pari": subgroup_prime,
        "family_subgroup_size": subgroup_size,
        "family_mov20": mov20,
        "not_anomalous": not_anomalous,
        "family_accept": bool(subgroup_prime and subgroup_size and mov20 and not_anomalous),
        "x9_255_smooth_cofactor": str(smooth_cofactor),
        "x9_remainder": str(remainder),
        "x9_remainder_prime_pari": near_prime,
        "x9_remainder_size": near_size,
        "x9_mov20": near_mov20,
        "x9_reference_accept": bool(near_prime and near_size and near_mov20 and not_anomalous),
    }


def evaluate(row: dict, target: dict, pari: Pari, binary_count) -> dict:
    started = time.monotonic()
    name = target["name"]
    result = {"target": name, "index": row["index"], "seed": row["seed"], "kind": row["kind"]}
    if row["kind"] == "binary":
        b = int(row["b"], 16)
        result.update({"b_normal": row["b_normal"], "b": row["b"]})
        if b == 0:
            result["status"] = "REJECT_B_ZERO"
        else:
            order = binary_count(b)
            result["status"] = "COUNTED"
            result["checks"] = checks(pari, order, 1 << target["m"], 2)
    else:
        p = int(target["p"])
        variant = row["variants"]["nist_fips_186_2"]
        result.update({"hash_method": "nist_fips_186_2", "c": variant["c"], "root_reason": variant["reason"]})
        strict = row["variants"]["ansi_x9_62_1998"]
        result["strict_x9_same_c"] = strict["c"] == variant["c"]
        if variant["reason"] != "nonsingular":
            result["status"] = "REJECT_" + variant["reason"].upper()
        else:
            c = int(variant["c"], 16)
            roots = [int(value, 16) for value in variant["b_roots"]]
            if p % 4 == 3:
                canonical = pow(-27 * pow(c, -1, p) % p, (p + 1) // 4, p)
            else:
                canonical = roots[0]
            if canonical not in roots:
                raise ArithmeticError("canonical root missing from generated roots")
            other = p - canonical
            order = prime_order_count(pari, p, canonical)
            other_order = 2 * (p + 1) - order if p % 4 == 3 else order
            result.update({"status": "COUNTED", "canonical_b": hex(canonical),
                           "other_b": hex(other), "canonical_root_rule": "power" if p % 4 == 3 else "smallest_isomorphic_root",
                           "canonical": checks(pari, order, p, 1),
                           "other": checks(pari, other_order, p, 1)})
    if row["index"] == target["candidate_index"]:
        if result["status"] != "COUNTED":
            raise ArithmeticError("published anchor rejected before counting")
        observed_order = result["checks"]["order"] if row["kind"] == "binary" else (
            result["canonical"]["order"] if int(result["canonical_b"], 16) == int(target["published_b"]) else result["other"]["order"]
        )
        expected = int(target["published_subgroup_order"]) * target["published_cofactor"]
        result["anchor_order_matches"] = int(observed_order) == expected
        if not result["anchor_order_matches"]:
            raise ArithmeticError("published anchor point count mismatch")
    result["elapsed_seconds"] = round(time.monotonic() - started, 6)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--stack-mib", type=int, default=512)
    args = parser.parse_args()
    targets = {row["name"]: row for row in json.loads((ROOT / "targets.json").read_text())}
    target = targets[args.target]
    if not 1 <= args.start <= args.end <= target["candidate_index"]:
        raise ValueError("range outside target stream")
    candidates = ROOT / "raw" / "candidates.jsonl"
    input_hash = sha256(candidates)
    output_dir = ROOT / "raw" / "evaluations" / target["name"]
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{args.start:05d}-{args.end:05d}.jsonl"
    partial = output.with_suffix(output.suffix + ".partial")
    if output.exists() or partial.exists():
        raise FileExistsError(output)
    pari = Pari()
    pari.allocatemem(args.stack_mib * 1024 * 1024)
    binary_count = field_for_binary(target) if target["kind"] == "binary" else None
    count = 0
    with partial.open("w") as stream, candidates.open() as source:
        header = {"record": "run", "command": sys.argv, "python": platform.python_version(),
                  "candidate_sha256": input_hash, "script_sha256": sha256(Path(__file__)),
                  "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  "target": args.target, "start": args.start, "end": args.end,
                  "stack_mib": args.stack_mib, "pid": os.getpid()}
        stream.write(json.dumps(header, sort_keys=True) + "\n")
        for line in source:
            row = json.loads(line)
            if row["target"] != args.target or not args.start <= row["index"] <= args.end:
                continue
            try:
                record = evaluate(row, target, pari, binary_count)
            except Exception as error:
                record = {"target": args.target, "index": row["index"], "seed": row["seed"],
                          "status": "INDETERMINATE", "error_type": type(error).__name__, "error": str(error)}
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()
            count += 1
    if count != args.end - args.start + 1:
        raise ArithmeticError(f"expected {args.end - args.start + 1} rows, got {count}")
    os.replace(partial, output)
    print(json.dumps({"target": args.target, "start": args.start, "end": args.end,
                      "rows": count, "output": str(output), "sha256": sha256(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
