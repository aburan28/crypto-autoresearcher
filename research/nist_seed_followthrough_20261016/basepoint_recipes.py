#!/usr/bin/env python3
"""Bounded, preregistered base-point x-coordinate provenance checks."""

import hashlib
import json
import platform
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TRAITS = REPO / "research/nist_seed_skipped_curves_20261016/traits.json"
TARGETS = REPO / "research/nist_seed_selection_20261016/targets.json"
NAMES = ("secp224r1", "prime256v1", "secp384r1", "secp521r1")
CAP = 65536


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_x(seed, counter, p, algorithm, order, expanded):
    cb = counter.to_bytes(4, "big")
    prefix = seed + cb if order == "seed_counter" else cb + seed
    h = getattr(hashlib, algorithm)
    if not expanded:
        output = h(prefix).digest()
    else:
        chunks = []
        bits = 0
        j = 0
        while bits < p.bit_length():
            chunk = h(prefix + j.to_bytes(4, "big")).digest()
            chunks.append(chunk)
            bits += 8 * len(chunk)
            j += 1
        output = b"".join(chunks)
    return int.from_bytes(output, "big") % p


def first_valid_x(p, a, b):
    x = 0
    while True:
        v = (x * x * x + a * x + b) % p
        if v == 0 or pow(v, (p - 1) // 2, p) == 1:
            return x
        x += 1


def main():
    out = HERE / "raw/basepoint_recipes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(out)
    source = json.loads(TRAITS.read_text())["published_controls"]
    targets = {t["openssl_name"]: t for t in json.loads(TARGETS.read_text())}
    if hashlib.sha256(b"abc").hexdigest() != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad":
        raise AssertionError("SHA-256 vector mismatch")
    if hashlib.sha1(b"abc").hexdigest() != "a9993e364706816aba3e25717850c26c9cd0d89d":
        raise AssertionError("SHA-1 vector mismatch")
    variants = [(algorithm, order, expanded) for algorithm in ("sha1", "sha256")
                for order in ("seed_counter", "counter_seed")
                for expanded in (False, True)]
    rows = []
    for name in NAMES:
        record = source[name]
        t = targets[name]
        curve = record["identity"]["curve"]
        p = int(record["identity"]["field"]["characteristic"])
        a, b = int(curve["a4"]), int(curve["a6"])
        gx, gy = map(int, curve["generator"])
        seed = bytes.fromhex(record["seed_hex"])
        if p != int(t["p"]) or b != int(t["published_b"]):
            raise AssertionError("published curve parameters differ")
        if (gy * gy - gx * gx * gx - a * gx - b) % p:
            raise AssertionError("published base point off curve")
        first_x = first_valid_x(p, a, b)
        checks = [{"recipe": "first_valid_nonnegative_x", "match": first_x == gx,
                   "candidate_x": str(first_x), "tested": first_x + 1}]
        for algorithm, order, expanded in variants:
            recipe = f"{algorithm}:{order}:{'expanded' if expanded else 'direct'}"
            bits = hashlib.new(algorithm).digest_size * 8
            if not expanded and gx >= 1 << bits and p > 1 << bits:
                checks.append({"recipe": recipe, "match": False, "tested": 0,
                               "reason": "published x exceeds direct digest range"})
                continue
            found = None
            for counter in range(CAP):
                if hash_x(seed, counter, p, algorithm, order, expanded) == gx:
                    found = counter
                    break
            checks.append({"recipe": recipe, "match": found is not None,
                           "tested": CAP if found is None else found + 1,
                           "counter": found})
        rows.append({"name": name, "seed": seed.hex(), "p": str(p),
                     "Gx": str(gx), "Gy": str(gy), "checks": checks})
    # Synthetic positives verify that each declared hash recipe reaches its
    # own zero-counter coordinate. These do not support historical attribution.
    synthetic_seed = bytes.fromhex("00112233445566778899aabbccddeeff00112233")
    synthetic_p = int(targets["prime256v1"]["p"])
    synthetic = []
    for algorithm, order, expanded in variants:
        expected = hash_x(synthetic_seed, 0, synthetic_p, algorithm, order, expanded)
        observed = next((i for i in range(4) if hash_x(synthetic_seed, i, synthetic_p,
                                                        algorithm, order, expanded) == expected), None)
        if observed != 0:
            raise AssertionError("synthetic recipe control failed")
        synthetic.append({"recipe": f"{algorithm}:{order}:{'expanded' if expanded else 'direct'}",
                          "counter": 0, "x": str(expected)})
    result = {"status": "bounded_complete", "created_utc":
              time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "command": sys.argv, "python": platform.python_version(),
              "script_sha256": digest(Path(__file__)),
              "source_sha256": {str(p.relative_to(REPO)): digest(p)
                                for p in (TRAITS, TARGETS)},
              "counter_cap_exclusive": CAP,
              "hash_vectors_passed": True, "synthetic_controls": synthetic,
              "rows": rows}
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": str(out), "sha256": digest(out),
                      "targets": len(rows), "matches": sum(c["match"] for x in rows for c in x["checks"])}))


if __name__ == "__main__":
    main()
