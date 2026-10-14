#!/usr/bin/env python3
"""Independent checks for the frozen keyed modeled 51-bit PRP.

This validates construction/rekey provenance, forward and inverse vectors,
the conditioned nonzero scan range, reduced-width exhaustive bijectivity, and
diagnostic output marginals/avalanche under a disjoint self-test key.  It does
not run the curve sieve or inspect any scientific outcome.
"""

from __future__ import annotations

import hashlib
import json


MASK64 = (1 << 64) - 1
MASK51 = (1 << 51) - 1
SCAN_STOP = 3_600_000_000
ROOT_KEY_HEX = "10456676ccd2e6bd1497bc8de889944eff4f72ebe81da37fbedb0a95b36853c6"
FINAL_KEY_HEX = "c6ac26c5f692baa74a02c14f38de8e93bfe40c2d2ecbdcf7231ac6e79049d7b2"
REKEY_COUNTER = 0
ZERO_PREIMAGE = 1_143_900_985_707_342
EXPECTED_ROUND_KEYS = (
    0x824FED8E0FDE5218, 0x00B2A56B05421B2D, 0xFD0F52502A0D3737,
    0x78CDB4C19DD24202, 0x722CFEF7C6D0EA93, 0xE007ABB4C970F252,
    0xA56276B6D4746BED, 0x08E8F877EC4098BC, 0x02EA18FD04E1DD08,
    0xEFB6477DE16EC1DA, 0xAF1A485BBAF930E9, 0xC80FF63F19D1D47C,
)
VECTORS = {
    0: 325_821_132_841_042,
    1: 2_117_735_011_170_056,
    2: 801_276_827_696_746,
    42: 1_218_540_018_519_903,
    3_599_999_999: 1_615_711_514_229_309,
    MASK51: 976_302_417_368_263,
}


def mix64(value: int) -> int:
    value &= MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def derive_final(root: bytes, counter: int) -> bytes:
    return hashlib.sha256(
        b"m51-deep-scan-prp/v1/rekey" + root + counter.to_bytes(8, "big")
    ).digest()


def derive_rounds(key: bytes) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(
            hashlib.sha256(
                b"m51-deep-scan-prp/v1/round" + key + i.to_bytes(4, "big")
            ).digest()[:8],
            "big",
        )
        for i in range(12)
    )


def forward(value: int, keys: tuple[int, ...], left_width: int = 26, right_width: int = 25) -> int:
    total = left_width + right_width
    if not 0 <= value < 1 << total:
        raise ValueError("outside permutation domain")
    initial_left, initial_right = left_width, right_width
    left = value >> right_width
    right = value & ((1 << right_width) - 1)
    for key in keys:
        output = mix64(right ^ key ^ (right_width << 56)) & ((1 << left_width) - 1)
        left, right = right, left ^ output
        left_width, right_width = right_width, left_width
    if (left_width, right_width) != (initial_left, initial_right):
        raise AssertionError("round parity changed packing")
    return (left << initial_right) | right


def inverse(value: int, keys: tuple[int, ...], left_width: int = 26, right_width: int = 25) -> int:
    total = left_width + right_width
    if not 0 <= value < 1 << total:
        raise ValueError("outside permutation domain")
    initial_left, initial_right = left_width, right_width
    left = value >> right_width
    right = value & ((1 << right_width) - 1)
    for round_index in range(len(keys) - 1, -1, -1):
        old_left_width = initial_left if round_index % 2 == 0 else initial_right
        old_right_width = initial_right if round_index % 2 == 0 else initial_left
        old_right = left
        output = mix64(old_right ^ keys[round_index] ^ (old_right_width << 56)) & ((1 << old_left_width) - 1)
        left, right = right ^ output, old_right
    return (left << initial_right) | right


def selftest_rounds() -> tuple[int, ...]:
    key = hashlib.sha256(b"m51-deep-scan-prp/v1/selftest-key-not-scientific").digest()
    return derive_rounds(key)


def main() -> int:
    root = bytes.fromhex(ROOT_KEY_HEX)
    final = derive_final(root, REKEY_COUNTER)
    if final.hex() != FINAL_KEY_HEX:
        raise RuntimeError("root-to-derived-key vector failed")
    rounds = derive_rounds(final)
    if rounds != EXPECTED_ROUND_KEYS:
        raise RuntimeError("round-key derivation vectors failed")
    for source, expected in VECTORS.items():
        if forward(source, rounds) != expected or inverse(expected, rounds) != source:
            raise RuntimeError(f"forward/inverse vector failed at {source}")
    if inverse(0, rounds) != ZERO_PREIMAGE:
        raise RuntimeError("zero-preimage inverse vector failed")
    if ZERO_PREIMAGE < SCAN_STOP:
        raise RuntimeError("zero preimage lies inside scientific scan range")

    reduced_keys = selftest_rounds()
    reduced_outputs = [forward(value, reduced_keys, 3, 2) for value in range(32)]
    if sorted(reduced_outputs) != list(range(32)):
        raise RuntimeError("reduced-width Feistel is not bijective")
    if not all(inverse(forward(value, reduced_keys, 3, 2), reduced_keys, 3, 2) == value for value in range(32)):
        raise RuntimeError("reduced-width Feistel inverse failed")

    sample_size = 1 << 16
    counts = [0] * 51
    outputs = []
    for value in range(sample_size):
        output = forward(value, reduced_keys)
        outputs.append(output)
        for bit in range(51):
            counts[bit] += (output >> bit) & 1
    proportions = [count / sample_size for count in counts]
    if not 0.485 <= min(proportions) <= max(proportions) <= 0.515:
        raise AssertionError("self-test-key output marginal diagnostic outside frozen gate")

    distances: list[int] = []
    for value in range(1024):
        base = outputs[value]
        for bit in range(51):
            distances.append((base ^ forward(value ^ (1 << bit), reduced_keys)).bit_count())
    mean_distance = sum(distances) / len(distances)
    if not 24.0 <= mean_distance <= 27.0:
        raise AssertionError("self-test-key avalanche diagnostic outside frozen gate")

    report = {
        "schema": "m51-deep-prp-verification/v1",
        "construction": "12-round unbalanced Feistel with mix64 modeled PRF",
        "security_claim": "modeled PRP only; not a cryptographically proven PRP",
        "root_key_hex": ROOT_KEY_HEX,
        "rekey_counter": REKEY_COUNTER,
        "derived_key_hex": FINAL_KEY_HEX,
        "zero_preimage": ZERO_PREIMAGE,
        "scan_range_excludes_zero_preimage": True,
        "ideal_prp_conditioning": "first S outputs modeled as ordered without-replacement sample from nonzero coefficients, conditional on exchangeability",
        "vectors": {str(key): value for key, value in VECTORS.items()},
        "key_derivation_passed": True,
        "round_key_vectors_passed": True,
        "forward_inverse_vectors_passed": True,
        "zero_preimage_check_passed": True,
        "reduced_width_bijection_passed": True,
        "reduced_width_exhaustive_domain": 32,
        "selftest_sample_size": sample_size,
        "selftest_marginal_min": min(proportions),
        "selftest_marginal_max": max(proportions),
        "selftest_avalanche_mean_bits": mean_distance,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
