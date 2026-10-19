#!/usr/bin/env python3
"""Recheck candidate-sign and standard-screen facts from the archived 21-curve data.

This is a derived audit of reported candidate blocks, not a replay of the
unavailable 1997–98 generator or an enumeration of all candidate blocks.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016" / "traits.json"
SELECTION = HERE.parent / "nist_seed_selection_deep_20261016" / "selection_matrix.json"
OUT = HERE / "process_checks.json"


def load(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> dict:
    source = load(SOURCE)
    selection = load(SELECTION)
    published = [("published", name, row) for name, row in source["published_controls"].items()]

    # P-224 has two sign representations for each of three omitted seeds. The
    # two representations are isomorphic, so count each block only once.
    omitted_by_key = {}
    for row in source["unpublished_candidates"]:
        key = (row["timestamp"], row["seed_ordinal_one_based"], row["seed_hex"])
        omitted_by_key.setdefault(key, []).append(row)
    assert len(published) == 10 and len(omitted_by_key) == 11

    rows = []
    for label, name, row in published:
        rows.append((label, name, [row]))
    for key, reps in omitted_by_key.items():
        rows.append(("passed_over", f"{key[0]}:{key[1]}", reps))

    checks = []
    for label, name, reps in rows:
        row = reps[0]
        p = int(row["p_hex"], 16)
        c = int(row["ansi_c_hex"], 16)
        n = int(row["n_hex"], 16)
        b_values = sorted(int(r["b_hex"], 16) for r in reps)
        for b in b_values:
            assert (c * b * b + 27) % p == 0
        assert n.bit_length() <= p.bit_length()
        assert n > 1 << 160 and n * n > 16 * p
        assert all(pow(p, k, n) != 1 for k in range(1, 21))

        if p % 4 == 3:
            assert len(b_values) == 1
            value = (-27 * pow(c, -1, p)) % p
            root = pow(value, (p + 1) // 4, p)
            assert root * root % p == value
            canonical_root_matches = b_values[0] == root
            assert canonical_root_matches
            sign_class = "two twists; recorded prime-order root is exponentiation root"
        else:
            assert p.bit_length() == 224 and p % 4 == 1
            if len(b_values) == 2:
                assert sum(b_values) == p
            # Since -1 is a square, the two signs of b are isomorphic via
            # a scaling with u^2=-1 and u^6=-1. This holds for the published
            # P-224 coefficient too, although the archive contains one sign.
            canonical_root_matches = None
            sign_class = "two isomorphic coefficient signs"

        checks.append({
            "label": label,
            "name": name,
            "timestamp": row["timestamp"],
            "ordinal": row["seed_ordinal_one_based"],
            "field_bits": p.bit_length(),
            "p_mod_4": p % 4,
            "represented_signs": len(b_values),
            "canonical_exponent_root_matches": canonical_root_matches,
            "sign_class": sign_class,
            "x962_min_order_checks": True,
            "mov_exponent_gt_20": True,
            "trace_normalized": row["trace_normalized"],
        })

    checks.sort(key=lambda r: (r["timestamp"], r["ordinal"], r["name"]))
    assert len(checks) == 21
    assert sum(r["canonical_exponent_root_matches"] is True for r in checks) == 17
    assert sum(r["p_mod_4"] == 1 for r in checks) == 4
    assert {(r["timestamp"], r["ordinal"], r["label"]) for r in checks} == {
        (r["timestamp"], r["ordinal"], r["label"]) for r in selection["rows"]
    }

    streams = []
    for timestamp in sorted({r["timestamp"] for r in checks}):
        stream = [r for r in checks if r["timestamp"] == timestamp]
        published_slots = [r["ordinal"] for r in stream if r["label"] == "published"]
        skipped_slots = [r["ordinal"] for r in stream if r["label"] == "passed_over"]
        streams.append({
            "timestamp": timestamp,
            "field_bits": stream[0]["field_bits"],
            "published_slots": published_slots,
            "passed_over_slots": skipped_slots,
            "reported_qualifying_slots": len(stream),
            "first_reported_qualifying_is_published": stream[0]["label"] == "published",
        })

    # POSIX 48-bit LCG: a odd and a=1 (mod 4), c odd, hence full period 2^48.
    # Each candidate consumes 20 consecutive calls. Its first output state is
    # T^(20(j-1)+1)(x0), x0=(timestamp<<16)|0x330e. All such states are 1 mod 4.
    # Since gcd(20, 2^48)=4, T^20 traverses exactly the 2^46 states in that
    # residue class. The 20 output bytes are determined by the first state.
    modulus = 1 << 48
    multiplier, increment = 0x5DEECE66D, 0xB
    assert multiplier % 4 == 1 and increment % 2 == 1
    assert 0x330E % 4 == 2
    assert (multiplier * 0x330E + increment) % 4 == 1
    assert math.gcd(20, modulus) == 4
    strict_block_states = modulus // math.gcd(20, modulus)
    assert strict_block_states == 1 << 46

    result = {
        "scope": "21 reported qualifying blocks in six reconstructed streams; no all-block or historical-code replay",
        "source_sha256": {"traits.json": sha256(SOURCE), "selection_matrix.json": sha256(SELECTION)},
        "counts": {
            "published": 10,
            "passed_over": 11,
            "p_mod_4_eq_3_matching_exponent_root": 17,
            "p224_isomorphic_sign_classes": 4,
            "streams_whose_first_reported_qualifying_slot_is_passed_over": 3,
        },
        "candidate_checks": checks,
        "streams": streams,
        "generator_state_ceiling": {
            "lcg_multiplier": hex(multiplier),
            "lcg_increment": hex(increment),
            "state_bits": 48,
            "candidate_bytes": 20,
            "first_output_state_mod_4": 1,
            "gcd_block_step_and_state_period": 4,
            "strict_20_draw_block_first_states": strict_block_states,
            "strict_20_draw_block_first_state_bits": 46,
            "arbitrary_offset_first_states_upper_bound": modulus,
            "arbitrary_offset_first_state_bits": 48,
            "interpretation": "State-count bounds for contiguous 20-draw candidate windows, with either strict block alignment or arbitrary start offset. Interleaved byte assembly is outside scope. These are not observed attempt counts or empirical weak-curve frequencies.",
        },
        "inference_limit": "Checks standard eligibility and sign convention, not what the original program evaluated or why it stopped.",
    }
    assert sum(not s["first_reported_qualifying_is_published"] for s in streams) == 3
    return result


if __name__ == "__main__":
    OUT.write_text(json.dumps(check(), indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT}")
