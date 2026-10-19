#!/usr/bin/env python3
"""Reproduce every published and preceding lrand48 curve-seed candidate."""

import argparse
import hashlib
import json
import os
from pathlib import Path

from binary_basis import normal_to_polynomial


ROOT = Path(__file__).resolve().parent
MASK48 = (1 << 48) - 1
MASK160 = (1 << 160) - 1


def sha1_int(value: int) -> int:
    return int.from_bytes(hashlib.sha1(value.to_bytes(20, "big")).digest(), "big")


def prime_c(seed: int, p: int, method: str) -> int:
    t = p.bit_length() - 1
    if method == "nist_fips_186_2":
        pieces = t // 160
        low_width = t - 160 * pieces
    elif method == "ansi_x9_62_1998":
        pieces = (t - 1) // 160
        low_width = t - 160 * pieces
    else:
        raise ValueError(method)
    low = sha1_int(seed) & ((1 << low_width) - 1)
    if method == "ansi_x9_62_1998":
        low &= (1 << (low_width - 1)) - 1
    c = low
    for offset in range(1, pieces + 1):
        c = (c << 160) | sha1_int((seed + offset) & MASK160)
    return c


def binary_b(seed: int, m: int) -> int:
    pieces = (m - 1) // 160
    low_width = m - 160 * pieces
    b = sha1_int(seed) & ((1 << low_width) - 1)
    for offset in range(1, pieces + 1):
        b = (b << 160) | sha1_int((seed + offset) & MASK160)
    return b


def modular_sqrt(a: int, p: int) -> int | None:
    """Deterministic Tonelli–Shanks for the odd published field primes."""
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    odd = p - 1
    exponent = 0
    while odd % 2 == 0:
        odd //= 2
        exponent += 1
    nonresidue = 2
    while pow(nonresidue, (p - 1) // 2, p) != p - 1:
        nonresidue += 1
    c = pow(nonresidue, odd, p)
    x = pow(a, (odd + 1) // 2, p)
    t = pow(a, odd, p)
    m = exponent
    while t != 1:
        i = 1
        power = t * t % p
        while power != 1:
            power = power * power % p
            i += 1
            if i >= m:
                raise ArithmeticError("Tonelli-Shanks invariant failed")
        factor = pow(c, 1 << (m - i - 1), p)
        x = x * factor % p
        t = t * factor * factor % p
        c = factor * factor % p
        m = i
    if x * x % p != a:
        raise ArithmeticError("square-root check failed")
    return x


def prime_variant(seed: int, p: int, method: str) -> dict:
    c = prime_c(seed, p, method)
    if c % p == 0:
        return {"c": hex(c), "reason": "c_zero_mod_p", "b_roots": []}
    target_square = -27 * pow(c, -1, p) % p
    root = modular_sqrt(target_square, p)
    if root is None:
        return {"c": hex(c), "reason": "no_b_root", "b_roots": []}
    roots = sorted({root, (-root) % p})
    if any(((-108 + 27 * b * b) % p) == 0 for b in roots):
        return {"c": hex(c), "reason": "singular", "b_roots": [hex(b) for b in roots]}
    return {"c": hex(c), "reason": "nonsingular", "b_roots": [hex(b) for b in roots]}


def seed_stream(target: dict):
    t = target["unix_time"]
    if target["kind"] == "binary":
        t //= 2
        outputs_per_seed = 5
        shift = 17
        width = 8
    else:
        outputs_per_seed = 20
        shift = 40
        width = 2
    state = ((t << 16) | 0x330E) & MASK48
    for index in range(1, target["candidate_index"] + 1):
        words = []
        for _ in range(outputs_per_seed):
            state = (0x5DEECE66D * state + 0xB) & MASK48
            words.append(f"{state >> shift:0{width}X}")
        yield index, "".join(words)


def generate(targets: list[dict], output: Path) -> None:
    if output.exists() or output.with_suffix(output.suffix + ".partial").exists():
        raise FileExistsError(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_suffix(output.suffix + ".partial")
    rows = 0
    anchors = 0
    with partial.open("w") as stream:
        for target in targets:
            name = target["name"]
            for index, seed_hex in seed_stream(target):
                row = {"target": name, "index": index, "seed": seed_hex, "kind": target["kind"]}
                if target["kind"] == "prime":
                    p = int(target["p"])
                    seed = int(seed_hex, 16)
                    row["variants"] = {
                        method: prime_variant(seed, p, method)
                        for method in ("nist_fips_186_2", "ansi_x9_62_1998")
                    }
                    if index == target["candidate_index"]:
                        anchor = row["variants"]["nist_fips_186_2"]
                        if int(target["published_b"]) not in [int(x, 16) for x in anchor["b_roots"]]:
                            raise ValueError(f"{name}: published coefficient does not match seed")
                else:
                    b_normal = binary_b(int(seed_hex, 16), target["m"])
                    b = normal_to_polynomial(b_normal, target["m"], int(target["polynomial"], 16))
                    row["b_normal"] = hex(b_normal)
                    row["b"] = hex(b)
                    row["reason"] = "nonsingular" if b else "b_zero"
                    if index == target["candidate_index"] and b != int(target["published_b"]):
                        raise ValueError(f"{name}: published binary coefficient does not match seed")
                if index == target["candidate_index"]:
                    if seed_hex != target["published_seed"]:
                        raise ValueError(f"{name}: published seed does not match stream")
                    anchors += 1
                stream.write(json.dumps(row, sort_keys=True) + "\n")
                rows += 1
    if rows != 31945 or anchors != 14:
        raise ValueError(f"incomplete enumeration: {rows} rows, {anchors} anchors")
    os.replace(partial, output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({"rows": rows, "anchors": anchors, "sha256": digest, "output": str(output)}, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "raw" / "candidates.jsonl")
    args = parser.parse_args()
    targets = json.loads((ROOT / "targets.json").read_text())
    generate(targets, args.output)


if __name__ == "__main__":
    main()
