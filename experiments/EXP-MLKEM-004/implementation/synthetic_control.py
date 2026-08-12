#!/usr/bin/env python3
"""Harness-side CTRL-SYNTHETIC-BASELINE-INVISIBLE for EXP-MLKEM-004.

Comparator (does not modify any library):
  Region R = indices [1536, 1568) of ML-KEM-1024 (final 32 bytes) by default.
  - EQUAL for every single-byte difference confined to R
  - UNEQUAL for at least one seeded multi-byte coordinated pattern in R (G2)
  - UNEQUAL for at least one alignment/lane-boundary pattern in R (G3)
  - Exact outside R

Returns observations only; no library code is altered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PARAM_CT = {
    "ML-KEM-512": 768,
    "ML-KEM-768": 1088,
    "ML-KEM-1024": 1568,
}

DEFAULT_R = list(range(1536, 1568))
SEEDS = [1, 2, 3, 4]


def synthetic_cmp(a: bytes, b: bytes, region: list[int] | None = None) -> int:
    """Return 0 if equal under synthetic rule, nonzero if unequal (wolfSSL-style)."""
    if len(a) != len(b):
        return 1
    region = region if region is not None else DEFAULT_R
    rset = set(region)
    # Outside R: exact
    for i in range(len(a)):
        if i not in rset and a[i] != b[i]:
            return 1
    # Inside R: ignore single-byte-confined diffs; detect multi-byte / alignment patterns
    diffs = [i for i in region if i < len(a) and a[i] != b[i]]
    if not diffs:
        return 0
    if len(diffs) == 1:
        return 0  # G1-silent by construction
    # Multi-byte difference in R => unequal (G2 visible)
    return 1


def _base_ct(seed: int, ct_len: int) -> bytes:
    h = hashlib.sha256(f"synth-base:{seed}:{ct_len}".encode()).digest()
    out = bytearray()
    state = h
    while len(out) < ct_len:
        state = hashlib.sha256(state).digest()
        out.extend(state)
    return bytes(out[:ct_len])


def run_g1(region: list[int], ct_len: int = 1568) -> dict[str, Any]:
    silent = set()
    detected = set()
    for seed in SEEDS:
        base = _base_ct(seed, ct_len)
        for idx in range(ct_len):
            for xorv in (0x01, 0xFF):
                mut = bytearray(base)
                mut[idx] ^= xorv
                rc = synthetic_cmp(base, bytes(mut), region)
                if rc == 0:
                    silent.add(idx)
                else:
                    detected.add(idx)
    # Indices silent under G1 for reportable reproduction: silent on all seeds/ops
    # Here an index is G1-silent if every single-byte mut at that index returned equal.
    g1_silent = sorted(i for i in range(ct_len) if i in silent and i not in detected)
    return {
        "class": "G1_single_byte",
        "silent_byte_set": g1_silent,
        "silent_in_R": sorted(set(g1_silent) & set(region)),
        "silent_outside_R": sorted(set(g1_silent) - set(region)),
        "g1_silent_on_R": set(region).issubset(set(g1_silent)),
    }


def run_g2_patterns(region: list[int], ct_len: int = 1568) -> dict[str, Any]:
    """Seeded multi-byte coordinated patterns confined to R."""
    findings = []
    for seed in SEEDS:
        base = _base_ct(seed, ct_len)
        # Contiguous k=8 flip entirely in R
        start = region[0]
        mut = bytearray(base)
        for j in range(8):
            mut[start + j] ^= 0x01
        rc = synthetic_cmp(base, bytes(mut), region)
        findings.append(
            {
                "seed": seed,
                "kind": "contiguous_k8_in_R",
                "indices": list(range(start, start + 8)),
                "detected": rc != 0,
            }
        )
        # Scattered 4-byte in R
        idxs = [region[0], region[7], region[15], region[31]]
        mut = bytearray(base)
        for i in idxs:
            mut[i] ^= 0xFF
        rc = synthetic_cmp(base, bytes(mut), region)
        findings.append(
            {
                "seed": seed,
                "kind": "scattered_k4_in_R",
                "indices": idxs,
                "detected": rc != 0,
            }
        )
    detected_any = any(f["detected"] for f in findings)
    return {
        "class": "G2_multi_byte",
        "patterns": findings,
        "synthetic_control_detected": detected_any,
        "marginal_findings": [f for f in findings if f["detected"]],
    }


def run_g3_patterns(region: list[int], ct_len: int = 1568) -> dict[str, Any]:
    """Alignment / lane-boundary patterns in R (pair of boundary indices)."""
    findings = []
    # Pair: start of R (1536, 16-aligned) and last byte of 32-byte lane (1567)
    pair = [region[0], region[-1]]
    for seed in SEEDS:
        base = _base_ct(seed, ct_len)
        mut = bytearray(base)
        mut[pair[0]] ^= 0x01
        mut[pair[1]] ^= 0x01
        rc = synthetic_cmp(base, bytes(mut), region)
        findings.append(
            {
                "seed": seed,
                "kind": "align_pair_R_start_and_end",
                "indices": pair,
                "detected": rc != 0,
            }
        )
        # Also 32-byte boundary at 1536 and 1552 (two diffs in R)
        mut = bytearray(base)
        mut[1536] ^= 0xFF
        mut[1552] ^= 0xFF
        rc = synthetic_cmp(base, bytes(mut), region)
        findings.append(
            {
                "seed": seed,
                "kind": "align_32_lane_pair",
                "indices": [1536, 1552],
                "detected": rc != 0,
            }
        )
    detected_any = any(f["detected"] for f in findings)
    return {
        "class": "G3_alignment",
        "patterns": findings,
        "synthetic_control_detected": detected_any,
        "marginal_findings": [f for f in findings if f["detected"]],
    }


def verify_control(region: list[int] | None = None) -> dict[str, Any]:
    region = region if region is not None else DEFAULT_R
    g1 = run_g1(region)
    g2 = run_g2_patterns(region)
    g3 = run_g3_patterns(region)
    g1_silent_set = set(g1["silent_byte_set"])
    # Marginal: G2/G3 findings that G1 did not produce (G1 produces silence on R;
    # detection of multi-byte/align patterns is the marginal instrument signal)
    g2_minus_g1 = ["synthetic_G2_pattern_detected"] if g2["synthetic_control_detected"] else []
    g3_minus_g1 = ["synthetic_G3_pattern_detected"] if g3["synthetic_control_detected"] else []
    # Pass: G1 silent on R (or documented superset confined to R); G2 or G3 detects
    silent_ok = g1["g1_silent_on_R"] and not g1["silent_outside_R"]
    # Allow silent set to equal R exactly
    silent_equals_r = g1["silent_in_R"] == sorted(region) and not g1["silent_outside_R"]
    detected_g2_or_g3 = bool(g2["synthetic_control_detected"] or g3["synthetic_control_detected"])
    pass_condition = (silent_ok or silent_equals_r) and detected_g2_or_g3
    return {
        "control_id": "CTRL-SYNTHETIC-BASELINE-INVISIBLE",
        "region_R": region,
        "parameter_set": "ML-KEM-1024",
        "g1": g1,
        "g2": g2,
        "g3": g3,
        "class_marginal_information_from_synthetic": {
            "G2_minus_G1": g2_minus_g1,
            "G3_minus_G1": g3_minus_g1,
            "note": (
                "Marginal findings are synthetic-control detections only. "
                "Rediscovery of the known wolfSSL defect is never counted here."
            ),
            "added_discriminating_power": detected_g2_or_g3,
        },
        "g1_silent": silent_ok or silent_equals_r,
        "g2_or_g3_detected": detected_g2_or_g3,
        "pass": pass_condition,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    report = verify_control()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"pass": report["pass"], "g1_silent": report["g1_silent"],
                      "g2_or_g3_detected": report["g2_or_g3_detected"]}))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
