"""Reconstruct and inspect every unpublished prime-field candidate in the cited seed streams.

Run with the local Sage Python environment. OpenSSL supplies the published
domain parameters used as controls; Sage supplies point counts and arithmetic.
The accepted-index list is a transcription of the supplied Valsorda article,
not a fresh exhaustive search through all earlier seeds.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

from sage.all import EllipticCurve, GF, Integer, prime_range
from sage.version import version as sage_version

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.curve_identity import curve_identity  # noqa: E402

OUT = Path(__file__).with_name("traits.json")
MASK48 = (1 << 48) - 1
MULT48 = 0x5DEECE66D

STREAMS = [
    {
        "timestamp": 863711343,
        "bits": 239,
        "published": {2185: "prime239v1", 2320: "prime239v2", 3048: "prime239v3"},
        "skipped": [36, 1562, 2491, 2682, 2863],
        "expected_prefix": {36: "25e5", 1562: "d09b", 2491: "1256", 2682: "d2c1", 2863: "3a70"},
    },
    {
        "timestamp": 863966734,
        "bits": 192,
        "published": {139: "prime192v1", 5228: "prime192v3", 6013: "prime192v2"},
        "skipped": [2198, 5405],
        "expected_prefix": {2198: "692d", 5405: "3ad1"},
    },
    {
        "timestamp": 871002724,
        "bits": 521,
        "published": {1136: "secp521r1"},
        "skipped": [],
        "expected_prefix": {},
    },
    {
        "timestamp": 871696354,
        "bits": 256,
        "published": {1842: "prime256v1"},
        "skipped": [876],
        "expected_prefix": {876: "50c7"},
    },
    {
        "timestamp": 872952608,
        "bits": 384,
        "published": {2688: "secp384r1"},
        "skipped": [],
        "expected_prefix": {},
    },
    {
        "timestamp": 891607927,
        "bits": 224,
        "published": {7026: "secp224r1"},
        "skipped": [777, 1485, 5736],
        "expected_prefix": {777: "d007", 1485: "18cf", 5736: "3c17"},
    },
]


def hexint(v: int) -> str:
    return hex(int(v))


def srand48_seeds(timestamp: int, ordinals: set[int]) -> dict[int, str]:
    state = ((timestamp & 0xFFFFFFFF) << 16) | 0x330E
    result = {}
    for ordinal in range(1, max(ordinals) + 1):
        buf = bytearray()
        for _ in range(20):
            state = (MULT48 * state + 0xB) & MASK48
            buf.append(state >> 40)
        if ordinal in ordinals:
            result[ordinal] = buf.hex()
    return result


def parse_openssl(name: str) -> dict:
    raw = subprocess.check_output(
        ["openssl", "ecparam", "-name", name, "-param_enc", "explicit", "-text", "-noout"],
        text=True,
    )
    sections: dict[str, str] = {}
    key = None
    for line in raw.splitlines():
        if line.startswith("Prime:"):
            key = "p"
        elif line.startswith("A:"):
            key = "a"
        elif line.startswith("B:"):
            key = "b"
        elif line.startswith("Generator (uncompressed):"):
            key = "g"
        elif line.startswith("Order:"):
            key = "n"
        elif line.startswith("Seed:"):
            key = "seed"
        elif line.startswith("Cofactor:"):
            key = None
            sections["h"] = str(int(re.search(r"\d+", line).group()))
        if key is not None:
            fragments = re.findall(r"(?<![0-9a-fA-F])[0-9a-fA-F]{2}(?=[:\s]|$)", line)
            sections[key] = sections.get(key, "") + "".join(fragments)
    needed = {"p", "a", "b", "g", "n", "seed", "h"}
    if not needed <= set(sections):
        raise RuntimeError(f"Missing OpenSSL fields for {name}: {needed - set(sections)}")
    p = int(sections["p"], 16)
    width = (p.bit_length() + 7) // 8
    g = bytes.fromhex(sections["g"])
    if len(g) != 1 + 2 * width or g[0] != 4:
        raise RuntimeError(f"Unexpected generator encoding for {name}")
    return {
        "name": name,
        "p": p,
        "a": int(sections["a"], 16),
        "b": int(sections["b"], 16),
        "n": int(sections["n"], 16),
        "h": int(sections["h"]),
        "seed": sections["seed"].lower(),
        "generator": [int.from_bytes(g[1:1 + width], "big"), int.from_bytes(g[1 + width:], "big")],
    }


def ansi_c(seed_hex: str, bit_length: int) -> int:
    seed = int(seed_hex, 16)
    v = (bit_length - 1) // 160
    w = bit_length - 160 * v - 1
    hashes = [hashlib.sha1(((seed + i) % (1 << 160)).to_bytes(20, "big")).digest() for i in range(v + 1)]
    c = int.from_bytes(hashes[0], "big") & ((1 << w) - 1)
    for digest in hashes[1:]:
        c = (c << 160) | int.from_bytes(digest, "big")
    return c


def candidate_roots(seed_hex: str, p: int) -> tuple[int, list[int]]:
    c = ansi_c(seed_hex, p.bit_length())
    if c == 0 or (4 * c + 27) % p == 0:
        raise ValueError("ANSI hash produced a singular or forbidden coefficient")
    F = GF(p)
    value = F(-27) / F(c)
    if not value.is_square():
        raise ValueError("No b for a=-3 exists over this field")
    b = int(value.sqrt())
    roots = sorted({b, (-b) % p})
    assert all((c * r * r + 27) % p == 0 for r in roots)
    return c, roots


def small_prime_factors(value: int, bound: int = 10000) -> tuple[list[list[int]], int]:
    remainder = int(value)
    factors = []
    for q in prime_range(2, bound + 1):
        q = int(q)
        if remainder % q:
            continue
        exponent = 0
        while remainder % q == 0:
            remainder //= q
            exponent += 1
        factors.append([q, exponent])
    return factors, remainder


def first_generator(E, p: int, n: int) -> list[int]:
    F = E.base_field()
    for x in range(1000):
        value = F(x) ** 3 - 3 * F(x) + F(int(E.a6()))
        if not value.is_square():
            continue
        y0 = int(value.sqrt())
        y = min(y0, (-y0) % p)
        point = E(F(x), F(y))
        if not point.is_zero() and Integer(n) * point == E(0):
            return [x, y]
    raise RuntimeError("No verified generator with x < 1000")


def identity(p: int, b: int, n: int, generator: list[int], tag: str) -> dict:
    field = {
        "characteristic": p,
        "degree": 1,
        "representation": "prime_field",
        "element_encoding": "canonical integer in [0,p-1]",
    }
    curve = {
        "model": "short_weierstrass",
        "a4": p - 3,
        "a6": b,
        "subgroup_order": n,
        "cofactor": 1,
        "generator": generator,
        "target_group": "full rational point group",
    }
    result = curve_identity(field, curve, tag)
    return {**result, "field": field, "curve": curve}


def common_traits(p: int, n: int, b: int, generator: list[int], tag: str) -> dict:
    t = p + 1 - n
    delta = t * t - 4 * p
    twist_n = p + 1 + t
    twist_factors, twist_rest = small_prime_factors(twist_n)
    delta_factors, delta_rest = small_prime_factors(abs(delta))
    j = (1728 * 4 * pow(p - 3, 3, p) * pow((4 * pow(p - 3, 3, p) + 27 * pow(b, 2, p)) % p, -1, p)) % p
    embed_through_100 = next((k for k in range(1, 101) if pow(p, k, n) == 1), None)
    return {
        "p_hex": hexint(p),
        "a_hex": hexint(p - 3),
        "b_hex": hexint(b),
        "n_hex": hexint(n),
        "n_bits": n.bit_length(),
        "n_minus_p_hex_signed": ("-" if n < p else "") + hexint(abs(n - p)),
        "trace_hex_signed": ("-" if t < 0 else "") + hexint(abs(t)),
        "trace_normalized": float(t / (2 * math.sqrt(p))),
        "delta_pi_hex_signed": "-" + hexint(abs(delta)),
        "small_delta_factors_to_10000": delta_factors,
        "delta_unfactored_rest_hex": hexint(delta_rest),
        "twist_order_hex": hexint(twist_n),
        "twist_order_bits": twist_n.bit_length(),
        "twist_small_factors_to_10000": twist_factors,
        "twist_unfactored_rest_hex": hexint(twist_rest),
        "j_hex": hexint(j),
        "j_special": j in (0, 1728),
        "anomalous": n == p,
        "embedding_degree_at_most_100": embed_through_100,
        "identity": identity(p, b, n, generator, tag),
    }


def main() -> None:
    published = {}
    curves = []
    for stream in STREAMS:
        timestamp = stream["timestamp"]
        indices = set(stream["published"]) | set(stream["skipped"])
        seeds = srand48_seeds(timestamp, indices)
        parameters = {index: parse_openssl(name) for index, name in stream["published"].items()}
        field_primes = {entry["p"] for entry in parameters.values()}
        if len(field_primes) != 1:
            raise RuntimeError(f"Inconsistent field primes in {timestamp}")
        p = next(iter(field_primes))
        assert p.bit_length() == stream["bits"]
        for index, entry in parameters.items():
            seed_hex = seeds[index]
            if seed_hex != entry["seed"]:
                raise RuntimeError(f"RNG mismatch at {entry['name']}: {seed_hex} != {entry['seed']}")
            c, roots = candidate_roots(seed_hex, p)
            if entry["b"] not in roots or entry["a"] != p - 3 or entry["h"] != 1:
                raise RuntimeError(f"ANSI coefficient/control mismatch at {entry['name']}")
            name = entry["name"]
            published[name] = {
                "timestamp": timestamp,
                "seed_ordinal_one_based": index,
                "seed_hex": seed_hex,
                "ansi_c_hex": hexint(c),
                "control": "OpenSSL published p,a,b,G,n,h and seed all agree with reproduction",
                **common_traits(p, entry["n"], entry["b"], entry["generator"], name.replace("v", "v")),
            }
        for index in stream["skipped"]:
            seed_hex = seeds[index]
            if not seed_hex.startswith(stream["expected_prefix"][index]):
                raise RuntimeError(f"Article prefix mismatch at {timestamp}:{index}")
            c, roots = candidate_roots(seed_hex, p)
            b0 = roots[0]
            E0 = EllipticCurve(GF(p), [GF(p)(-3), GF(p)(b0)])
            n0 = int(E0.cardinality())
            by_root = {b0: n0}
            by_root[roots[1]] = n0 if p % 4 == 1 else 2 * (p + 1) - n0
            eligible = []
            for root, count in by_root.items():
                if count.bit_length() > p.bit_length():
                    continue
                if Integer(count).is_prime(proof=False) and Integer(count).is_prime(proof=True):
                    eligible.append((root, count))
            if not eligible:
                raise RuntimeError(f"No eligible prime-order sign for {timestamp}:{index}")
            for b, n in eligible:
                E = EllipticCurve(GF(p), [GF(p)(-3), GF(p)(b)])
                generator = first_generator(E, p, n)
                # The point has order n because n is prime and it is nonidentity.
                # Since n > 4 sqrt(p), Hasse's interval contains at most one
                # multiple of n, so this checks the independent point count.
                assert n * n > 16 * p
                row = {
                    "timestamp": timestamp,
                    "seed_ordinal_one_based": index,
                    "seed_hex": seed_hex,
                    "ansi_c_hex": hexint(c),
                    "root_count": len(eligible),
                    "order_source": "Sage SEA/point-count, checked by certified prime n, n*G=O and Hasse uniqueness",
                    "generator_convention": "study-defined: smallest x >= 0 with n*G=O, then smaller y root",
                    **common_traits(p, n, b, generator, f"skip{timestamp}i{index}"),
                }
                curves.append(row)
                print(f"verified {timestamp}:{index} b={hexint(b)[:16]} n_bits={n.bit_length()}", flush=True)
    for row in curves:
        p = int(row["p_hex"], 16)
        n = int(row["n_hex"], 16)
        row["published_same_field_order_matches"] = [
            name for name, control in published.items()
            if int(control["p_hex"], 16) == p and int(control["n_hex"], 16) == n
        ]
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "eleven unpublished qualifying seed indices transcribed from supplied Valsorda article; ten published controls",
        "source_url_nist": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf",
        "source_url_article": "https://words.filippo.io/",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sage_version": sage_version,
        "openssl_version": subprocess.check_output(["openssl", "version"], text=True).strip(),
        "published_controls": published,
        "unpublished_candidates": curves,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT} with {len(curves)} unpublished curve representations", flush=True)


if __name__ == "__main__":
    main()
