#!/usr/bin/env python3
"""Independent finite-field and witness audit of the four archived BINSTD toy cells.

This validates frozen replay receipts. It does not reconstruct missing original
host traces or measure runtime. Field multiplication uses interleaved modular
reduction; division uses binary polynomial Euclid, unlike the archived worker.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad"
PIN = "4647b1d072ffaebbbb85127bdc60343bbd372ec4"
EXPERIMENT = "experiments/EXP-BINSTD-8bdf86"
SHERIFF = "research/sheriff/SHF-20261024-46b7da/scripts"
MOD = (1 << 17) | (1 << 3) | 1
MASK = (1 << 17) - 1
PANELS = ("ell89-ell8", "ell89-ell9", "ell89r1-ell8", "ell89r1-ell9")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pinned(commit: str, path: str) -> bytes:
    if not path.startswith(EXPERIMENT + "/"):
        raise ValueError(f"unexpected archive path: {path}")
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def poly_mod(a: int, modulus: int) -> int:
    while a and a.bit_length() >= modulus.bit_length():
        a ^= modulus << (a.bit_length() - modulus.bit_length())
    return a


def poly_mul(a: int, b: int) -> int:
    product = 0
    while b:
        if b & 1:
            product ^= a
        a <<= 1
        b >>= 1
    return product


def trial_irreducible(p: int) -> int:
    degree = p.bit_length() - 1
    tested = 0
    for d in range(1, degree // 2 + 1):
        for low in range(1 << d):
            candidate = (1 << d) | low
            tested += 1
            if poly_mod(p, candidate) == 0:
                raise ValueError(f"factor {p} has divisor {candidate}")
    return tested


def mul(a: int, b: int) -> int:
    if a & ~MASK or b & ~MASK or a < 0 or b < 0:
        raise ValueError("field element outside 17-bit range")
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << 17):
            a ^= MOD
    return result


def inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("inverse of zero")
    u, v, g, h = a, MOD, 1, 0
    while u != 1:
        shift = u.bit_length() - v.bit_length()
        if shift < 0:
            u, v = v, u
            g, h = h, g
            shift = -shift
        u ^= v << shift
        g ^= h << shift
        if u == 0:
            raise ValueError("noninvertible residue")
    result = poly_mod(g, MOD)
    if mul(a, result) != 1:
        raise AssertionError("Euclid inverse check failed")
    return result


def point(value: list[int]) -> tuple[int, int]:
    if len(value) != 2 or any(not isinstance(x, int) or x < 0 or x > MASK for x in value):
        raise ValueError("invalid point coordinate")
    return value[0], value[1]


def on_curve(p: tuple[int, int] | None) -> bool:
    if p is None:
        return True
    x, y = p
    return mul(y, y) ^ mul(x, y) == mul(mul(x, x), x) ^ 1


def add(p: tuple[int, int] | None,
        q: tuple[int, int] | None) -> tuple[int, int] | None:
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2:
        if y1 ^ y2 == x1 or x1 == 0:
            return None
        slope = x1 ^ mul(y1, inv(x1))
        x3 = mul(slope, slope) ^ slope
        y3 = mul(x1, x1) ^ mul(slope ^ 1, x3)
    else:
        slope = mul(y1 ^ y2, inv(x1 ^ x2))
        x3 = mul(slope, slope) ^ slope ^ x1 ^ x2
        y3 = mul(slope, x1 ^ x3) ^ x3 ^ y1
    result = x3, y3
    if not on_curve(result):
        raise AssertionError("addition left curve")
    return result


def check_witness(target: tuple[int, int], raw: list[list[int]]) -> None:
    if len(raw) != 3:
        raise ValueError("witness is not a triple")
    triple = [point(p) for p in raw]
    if not all(on_curve(p) for p in triple):
        raise ValueError("off-curve witness")
    if add(add(triple[0], triple[1]), triple[2]) != target:
        raise ValueError("triple does not sum to target")


def check_panel(panel: str) -> dict:
    source = ROOT / SHERIFF / f"binstd-per-target-{panel}.json"
    raw = source.read_bytes()
    rel_source = source.relative_to(ROOT).as_posix()
    if raw != subprocess.check_output(["git", "show", f"{BASE}:{rel_source}"], cwd=ROOT):
        raise ValueError("working replay receipt differs from exact-main baseline")
    data = json.loads(raw)
    if data["schema"] != "binstd.per_target_replay.v1" or data["pin"] != PIN:
        raise ValueError("wrong replay schema or source pin")
    tag, ell = panel.rsplit("-ell", 1)
    if data["panel"] != tag or data["ell"] != int(ell):
        raise ValueError("panel label mismatch")
    hashes = data["source_sha256"]
    receipt_path = f'{EXPERIMENT}/runs/{data["run_id"]}/execution-receipt.json'
    receipt = json.loads(pinned(PIN, receipt_path))
    if data["authority_commit"] != receipt["authority"]["commit"]:
        raise ValueError("replay authority differs from run receipt")
    for path, claimed_hash in sorted(hashes.items()):
        commit = data["authority_commit"] if path.endswith(("/run.py", "/gf2.py")) else PIN
        if digest(pinned(commit, path)) != claimed_hash:
            raise ValueError(f"source hash mismatch: {path}")
    if hashes[receipt_path] != digest(pinned(PIN, receipt_path)):
        raise ValueError("run receipt hash mismatch")
    raw_path = f'{EXPERIMENT}/runs/{data["run_id"]}/raw-result.json'
    raw_result = json.loads(pinned(PIN, raw_path))
    if hashes[raw_path] != receipt["artifact_sha256"]["raw-result.json"]:
        raise ValueError("run receipt does not bind raw result")
    freeze_path = f"{EXPERIMENT}/stage0-{tag}/freeze.json"
    freeze = json.loads(pinned(PIN, freeze_path))
    if freeze["n_stage1"] != 17 or freeze["target_count"] != 40 or freeze["band"] != 1.25:
        raise ValueError("frozen workload mismatch")
    yield_path = f"{EXPERIMENT}/stage1-{tag}/yield-matrix.json"
    expected_paths = {f"{EXPERIMENT}/implementation/run.py",
                      f"{EXPERIMENT}/implementation/gf2.py", receipt_path,
                      raw_path, freeze_path, yield_path}
    if set(hashes) != expected_paths:
        raise ValueError("per-target receipt does not bind exactly six expected paths")
    if hashes[yield_path] != raw_result["result"]["artifact_sha256"]["stage1/yield-matrix.json"]:
        raise ValueError("raw result does not bind yield matrix")
    cells = [c for c in json.loads(pinned(PIN, yield_path))["cells"] if c["ell"] == int(ell)]
    if len(cells) != 1:
        raise ValueError("archived ell cell is missing or duplicated")
    cell = cells[0]
    archived = {"tau": cell["hits_tau"], "open": cell["hits_open"]}
    if data["archived_hits"] != archived or data["observed_hits"] != archived:
        raise ValueError("archived/replayed hit counts differ")
    if data["factor_base_sizes"]["tau"] != cell["fb_tau_size"] or data["factor_base_sizes"]["open"] != cell["fb_open_size"]:
        raise ValueError("factor-base size differs from archive")
    rows = data["targets"]
    if len(rows) != 40 or sorted(row["index"] for row in rows) != list(range(40)):
        raise ValueError("per-target index coverage is incomplete")
    witnessed = {"tau": 0, "open": 0}
    negative_rejected = False
    for row in rows:
        target = point(row["target"])
        if not on_curve(target):
            raise ValueError("target is off curve")
        for arm in witnessed:
            arm_row = row[arm]
            if bool(arm_row["hit"]) != (arm_row["witness"] is not None):
                raise ValueError("hit/witness flag mismatch")
            if arm_row["hit"]:
                check_witness(target, arm_row["witness"])
                witnessed[arm] += 1
                if not negative_rejected and arm_row["witness"][2][0] != 0:
                    mutant = [list(p) for p in arm_row["witness"]]
                    mutant[2][1] ^= mutant[2][0]  # Negate one valid curve point.
                    try:
                        check_witness(target, mutant)
                    except ValueError:
                        negative_rejected = True
                    else:
                        raise AssertionError("on-curve tampered witness passed")
    if witnessed != archived or not negative_rejected:
        raise ValueError("witness count or negative control failed")
    if not (0 < 40 and archived["open"] == 40 and archived["tau"] <= 40 and
            4 * archived["tau"] < 5 * archived["open"]):
        raise ValueError("Lean ceiling premises/conclusion mismatch")
    return {"panel": panel, "receipt_sha256": digest(raw), "run_id": data["run_id"],
            "authority_commit": data["authority_commit"], "targets": len(rows),
            "archived_hits": archived, "independent_valid_witnesses": witnessed,
            "on_curve_mutation_rejected": negative_rejected,
            "conditional_ceiling_premises": True}


def main() -> None:
    subprocess.check_call(["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT)
    if trial_irreducible(MOD) != 510:
        raise AssertionError("unexpected modulus trial count")
    factors_path = f"{EXPERIMENT}/stage1-ell89/admissible-phi-dims.json"
    factors = json.loads(pinned(PIN, factors_path))
    masks = [row["poly"] for row in factors["factors"]]
    if masks != [3, 313, 471] or poly_mul(poly_mul(*masks[:2]), masks[2]) != (1 << 17) | 1:
        raise ValueError("frozen x17 factorization differs")
    if [trial_irreducible(x) for x in masks] != [0, 30, 30]:
        raise ValueError("frozen factors not exhaustively irreducible")
    if sorted({sum(bits[i] * factors["factors"][i]["degree"] for i in range(3))
               for bits in ((a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1))}) != factors["admissible_dimensions"]:
        raise ValueError("frozen dimension subset sums differ")
    panels = [check_panel(p) for p in PANELS]
    out = {"schema": "binstd.independent_witness_audit.v1", "source_main": BASE,
           "archive_pin": PIN, "field_modulus": MOD, "field_modulus_trial_divisors": 510,
           "x17_factor_masks": masks, "factor_trial_divisors": [0, 30, 30],
           "dimension_subset_sums": factors["admissible_dimensions"], "panels": panels,
           "limits": "Validates archived replay witnesses and source hashes; does not prove miss rows, original host execution, timings, or Frobenius normal-basis identification."}
    path = Path(__file__).with_name("evidence.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("panels", len(panels), "targets", sum(p["targets"] for p in panels),
          "witnesses", sum(sum(p["independent_valid_witnesses"].values()) for p in panels))


if __name__ == "__main__":
    main()
