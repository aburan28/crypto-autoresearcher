"""Independent Sage replay of six planted public systems and private witnesses.

This file imports neither the input emitter nor the frozen backend evaluator.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from sage.all import EllipticCurve, GF

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DOMAIN = "ICPERF-PRIME63-PLANTED-V1"


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        return json.load(stream, parse_int=int, parse_float=Decimal)


def evaluate(equation, values, p):
    total = 0
    for term in equation:
        monomial = int(term["coefficient"])
        for index, power in term["powers"]:
            monomial = monomial * pow(int(values[index]), int(power), p) % p
        total = (total + monomial) % p
    return total


def archived_bases():
    scan = read(ROOT / "research/icperf_prime_coset_896_20261017/scan.json")
    controls = read(ROOT / "research/icperf_prime_475_controls_20261017/controls.json")
    selected = next(a for a in scan["attempts"] if a["base_parameters"]["seed"] == scan["selected_seed"])
    result = {"coset": selected["points"]}
    result.update({row["kind"]: row["points"] for row in controls["controls"]})
    return result, selected["base_parameters"]


def check(public, witnesses):
    systems = public["systems"]
    by_cell = {w["cell"]: w for w in witnesses["witnesses"]}
    bases, coset = archived_bases()
    archived = read(ROOT / "research/icperf_prime_475_target_systems_20261017/systems.json.gz")
    targets = {tuple(t["point"]) for t in archived["targets"]}
    if len(systems) != 6 or len(by_cell) != 6:
        raise ValueError("expected six public and private cells")
    c = archived["curve"]
    p = c["p"]
    E = EllipticCurve(GF(p), [c["a"], c["b"]])
    rows = []
    for system in systems:
        arm, m, cell = system["arm"], system["m"], system["cell"]
        witness = by_cell[cell]
        base = bases[arm]
        if len(base) != 475 or [[int(v) for v in point] for point in system["base_points"]] != base:
            raise ValueError(f"{cell}: frozen base changed")
        if system["curve"] != c or int(system["p"]) != p:
            raise ValueError(f"{cell}: curve changed")
        if len(witness["selected"]) != m or len({r["point"][0] for r in witness["selected"]}) != m:
            raise ValueError(f"{cell}: arity or repeated x")
        # Replay every candidate, including rejects, so an arbitrary skipped
        # base point cannot masquerade as the fixed target-blind SHA stream.
        replay_selected, replay_rejected, replay_seen = [], [], set()
        replay_sum = E(0)
        last_index = witness["selected"][-1]["index"]
        for index in range(last_index + 1):
            digest = hashlib.sha256(f"{DOMAIN}|{arm}|{m}|{index}".encode()).digest()
            original = base[int.from_bytes(digest[:16], "big") % len(base)]
            sign = -1 if digest[16] & 1 else 1
            point = E(original) if sign == 1 else -E(original)
            if original[0] in replay_seen:
                replay_rejected.append({"index": index, "reason": "repeated_x"})
                continue
            candidate = replay_sum + point
            if candidate.is_zero():
                replay_rejected.append({"index": index, "reason": "infinity_sum"})
                continue
            if (int(candidate[0]), int(candidate[1])) in targets:
                replay_rejected.append({"index": index, "reason": "public_target_collision"})
                continue
            replay_selected.append({"index": index, "point": original, "sign": sign,
                                    "signed_point": [int(point[0]), int(point[1])],
                                    "digest_sha256": digest.hex()})
            replay_seen.add(original[0])
            replay_sum = candidate
        if replay_selected != witness["selected"] or replay_rejected != witness["rejections"]:
            raise ValueError(f"{cell}: selection stream/rejection log mismatch")
        seen = set()
        sum_point = E(0)
        for row in witness["selected"]:
            index = row["index"]
            digest = hashlib.sha256(f"{DOMAIN}|{arm}|{m}|{index}".encode()).digest()
            if digest.hex() != row["digest_sha256"]:
                raise ValueError(f"{cell}: digest")
            original = base[int.from_bytes(digest[:16], "big") % len(base)]
            if row["point"] != original or row["point"][0] in seen:
                raise ValueError(f"{cell}: selection/base membership")
            sign = -1 if digest[16] & 1 else 1
            if sign != row["sign"]:
                raise ValueError(f"{cell}: sign derivation")
            point = E(original)
            signed = point if sign == 1 else -point
            if [int(signed[0]), int(signed[1])] != row["signed_point"]:
                raise ValueError(f"{cell}: signed point")
            seen.add(original[0])
            sum_point += signed
            if sum_point.is_zero() or (int(sum_point[0]), int(sum_point[1])) in targets:
                raise ValueError(f"{cell}: forbidden partial sum")
        target = tuple(int(x) for x in system["target_point"])
        if target != tuple(int(x) for x in witness["target_point"]):
            raise ValueError(f"{cell}: target mismatch")
        if sum_point != E(target):
            raise ValueError(f"{cell}: full point sum")
        if arm == "coset":
            d, g = coset["d"], coset["coset"]
            for row in witness["selected"]:
                if pow(row["point"][0], d, p) != pow(g, d, p):
                    raise ValueError(f"{cell}: coset gate")
        encoding = system["encoding"]
        names = encoding["variables"]
        root = witness["root"]
        if set(root) != set(names):
            raise ValueError(f"{cell}: root variable mismatch")
        values = [int(root[name]) for name in names]
        if any(not 0 <= value < p for value in values):
            raise ValueError(f"{cell}: root range")
        residuals = [evaluate(eq, values, p) for eq in encoding["equations"]]
        if any(residuals):
            raise ValueError(f"{cell}: polynomial residual")
        modified = list(values)
        modified[0] = (modified[0] + 1) % p
        if not any(evaluate(eq, modified, p) for eq in encoding["equations"]):
            raise ValueError(f"{cell}: modified root passed")
        rows.append({"cell": cell, "m": m, "arm": arm, "base_size": len(base),
                     "equations": len(encoding["equations"]), "polynomial_zero": True,
                     "full_point_sum": True, "modified_root_rejected": True})
    return {"schema": "icperf-prime63-independent-input-replay-v1", "status": "pass",
            "sage": "independent Sage point arithmetic", "cells": rows,
            "systems_checked": len(rows), "natural_systems_solved": 0,
            "full_width_planted_ideals_solved": 0}


def main():
    result = check(read(HERE / "planted_public.json.gz"),
                   read(HERE / "planted_witnesses.json"))
    (HERE / "input_replay.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "cells": result["systems_checked"]}))


if __name__ == "__main__":
    main()
