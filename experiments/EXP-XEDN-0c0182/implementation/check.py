#!/usr/bin/env python3
"""EXP-XEDN-0c0182 checker: re-derives the result with independent code.

Validity only, never a prediction: a result that falsifies H-XEDN-5befd8 is
still a valid result. Re-derives group orders from the character sum
#E(F_p) = p + 1 + sum_x chi(x^3 - x^2 + 16x), the Legendre symbols by Euler's
criterion on fresh code, the odd-order affine count (= odd part - 1), the
listed F1 violation points, the aggregate totals, and the accepted-cell count
of every eligible arm by exact rational arithmetic (Fraction) on the lifted
curve equations. Exit 0 valid, 1 invalid.

    check.py RUN_DIR TARGETS_JSON
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

A0, B0 = -1, 16


def chi(a: int, p: int) -> int:
    a %= p
    return 0 if a == 0 else (1 if pow(a, (p - 1) // 2, p) == 1 else -1)


def order_by_character_sum(p: int) -> int:
    return p + 1 + sum(chi(x * x * x - x * x + 16 * x, p) for x in range(p))


def fail(msg: str) -> int:
    print(f"INVALID: {msg}", file=sys.stderr)
    return 1


def recount_arm(p, P, Q, sp, sq, reps_p, reps_q):
    accepted = 0
    for s in reps_p:
        w0 = P[1] * pow(s, -1, p) % p
        for t in reps_q:
            z0 = Q[1] * pow(t, -1, p) % p
            for j in range(-8, 9):
                for k in range(-8, 9):
                    w, z = w0 + p * j, z0 + p * k
                    X1, Y1 = Fraction(sp * s * s), Fraction(s * w)
                    X2, Y2 = Fraction(sq * t * t), Fraction(t * z)
                    # Y^2/X = X^2 + A X + B for both points: linear in (A, B).
                    r1 = Y1 * Y1 / X1 - X1 * X1
                    r2 = Y2 * Y2 / X2 - X2 * X2
                    A = (r1 - r2) / (X1 - X2)
                    B = r1 - A * X1
                    if A.denominator != 1:
                        continue
                    if B * (A * A - 4 * B) == 0:
                        continue
                    accepted += 1
    return accepted


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        return fail("usage: check.py RUN_DIR TARGETS_JSON")
    run_dir, targets_path = Path(argv[1]), Path(argv[2])
    try:
        res = json.loads((run_dir / "raw-result.json").read_text())
    except (OSError, ValueError) as error:
        return fail(f"raw-result.json unreadable: {error}")
    if not (run_dir / "manifest.yaml").is_file():
        return fail("manifest.yaml missing")
    targets_bytes = targets_path.read_bytes()
    targets = json.loads(targets_bytes)
    if res.get("schema") != "xedni.faithful_eligibility.result.v1":
        return fail("schema")
    if res.get("targets_sha256") != hashlib.sha256(targets_bytes).hexdigest():
        return fail("targets_sha256 does not match the frozen targets")
    if res.get("primes") != [31, 43, 59, 83, 353]:
        return fail("primes")
    for row in res["per_prime"]:
        p = row["p"]
        n = order_by_character_sum(p)
        if row["group_order"] != n:
            return fail(f"p={p}: group order {row['group_order']} != {n}")
        odd = n
        while odd % 2 == 0:
            odd //= 2
        if row["odd_part"] != odd or row["odd_order_affine_points"] != odd - 1:
            return fail(f"p={p}: odd part / odd-order count")
        want = {"D_minus_63": chi(-63, p), "minus_1": chi(-1, p), "minus_16": chi(-16, p)}
        if row["legendre"] != want:
            return fail(f"p={p}: Legendre symbols")
        if row["f1_violations"] != len(row["f1_violation_points"]):
            return fail(f"p={p}: F1 list length")
        for x, y in row["f1_violation_points"]:
            if (y * y - x * (x * x - x + 16)) % p or chi(x, p) == 1:
                return fail(f"p={p}: listed F1 violation is not a non-residue point")
        plus = row["odd_order_points_with_plus_sign_eligible"]
        if plus + row["f1_violations"] != row["odd_order_affine_points"]:
            return fail(f"p={p}: plus-eligible + violations != odd-order count")
    if res["f1_violations_total"] != sum(r["f1_violations"] for r in res["per_prime"]):
        return fail("f1 total")
    if len(res["pairs"]) != len(targets["pairs"]) or res["frozen_pairs"] != len(targets["pairs"]):
        return fail("pair count")
    total_accepted = 0
    for out, frozen in zip(res["pairs"], targets["pairs"]):
        if out["id"] != frozen["id"]:
            return fail("pair order")
        p = frozen["p"]
        for a_out, a_frozen in zip(out["arms"], frozen["arms"]):
            reps_p, reps_q = a_frozen["t_representatives"]
            if a_out["eligible"] != bool(reps_p and reps_q):
                return fail(f"{out['id']}: eligibility")
            if a_out["eligible"]:
                sp, sq = a_frozen["signs"]
                got = recount_arm(p, frozen["P"], frozen["Q"], sp, sq, reps_p, reps_q)
                if got != a_out["accepted"]:
                    return fail(f"{out['id']} {a_frozen['signs']}: accepted {a_out['accepted']} != {got}")
                total_accepted += got
    if sum(v["accepted"] for v in res["accepted_by_arm"].values()) != total_accepted:
        return fail("accepted_by_arm total")
    faithful = [r for r in res["pairs"] if r["faithful"]]
    if res["faithful_pairs"] != len(faithful):
        return fail("faithful count")
    print(f"VALID: {len(res['per_prime'])} primes, {len(res['pairs'])} pairs, "
          f"{total_accepted} accepted cells re-derived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
