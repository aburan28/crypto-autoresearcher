#!/usr/bin/env python3
"""EXP-CSIDH-7886f6 driver: 30-term class-number truncation at discriminant -83.

Frozen protocol (experiments/EXP-CSIDH-7886f6/specification.yaml, v1):
  1. Label discriminants -83, -84, -92 by one fundamentality criterion routine
     (-83 fundamental, -84 fundamental, -92 non-fundamental); a wrong label
     voids the run (exit 2).
  2. Enumerate the reduced positive-definite binary quadratic forms of
     discriminant -83 twice, by two structurally different loops (E1: outer
     over a then b; E2: outer over c then b, set-deduplicated). A
     disagreement voids the run (exit 3).
  3. Compute chi(n) = (-83/n) for n = 1..30 by a reciprocity-based Kronecker
     routine; chi(1) = 1 or the run is void (exit 4).
  4. L30 = sum chi(n)/n, n = 1..30, exact rational (fractions.Fraction,
     automatically reduced; coprimality re-asserted).
  5. Enclose sqrt(83) and pi in explicit rational intervals (denominator
     10^12, stated in the manifest), multiply out with the sign of L30
     handled, and enclose S = (sqrt(83)/pi) * L30.
  6. Interval gate: length strictly below 1/2, exactly one integer possible
     as "the integer nearest to every point of the interval", and no
     half-integer inside; otherwise the row is instrument_failure and no r is
     scored (the measurement is still complete and valid; exit 0).
  7. Compare r with h; write the reading row. A mismatch is a valid
     measurement, not a driver failure.

Exit codes: 0 = measurement completed with a valid instrument (any recorded
outcome, including instrument_failure); 2 = fundamentality-label mismatch;
3 = enumeration disagreement; 4 = chi(1) != 1 or non-reduced L30. The
scored reading row exists only in the run directory this driver writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from math import floor, isqrt
from pathlib import Path

DISCRIMINANT = -83
TRUNCATION = 30
CONTROL_FUNDAMENTAL = -84
CONTROL_NONFUNDAMENTAL = -92
SCALE = 10 ** 12  # common denominator of every rational enclosure

# Rational enclosures, fixed before any run and recorded in the manifest.
# sqrt(83) in [SQRT_LO, SQRT_HI]: floor/ceil of sqrt(83) * SCALE.
_SQRT_NUM = isqrt(83 * SCALE * SCALE)
SQRT_LO = Fraction(_SQRT_NUM, SCALE)
SQRT_HI = Fraction(_SQRT_NUM + 1, SCALE)
# pi in [PI_LO, PI_HI]: 3.141592653589 < pi < 3.141592653590 (12 decimals).
PI_LO = Fraction(3141592653589, SCALE)
PI_HI = Fraction(3141592653590, SCALE)


def stage_time(note: str, started: float) -> dict:
    return {"stage": note, "seconds": round(time.monotonic() - started, 6)}


def squarefree(n: int) -> bool:
    n = abs(n)
    if n == 0:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            n //= d
            if n % d == 0:
                return False
        d += 1
    return True


def is_fundamental_discriminant(d: int) -> tuple[bool, str]:
    """One criterion routine for every discriminant labeled in this run."""
    if d % 4 == 1:
        ok = squarefree(d)
        return ok, f"D={d} is 1 mod 4 and {'squarefree' if ok else 'not squarefree'}"
    if d % 4 == 0:
        m = d // 4
        residue = m % 4  # Python: -21 % 4 == 3, -23 % 4 == 1
        sf = squarefree(m)
        ok = residue in (2, 3) and sf
        return ok, (f"D={d} = 4*{m} with {m} congruent to {residue} mod 4 and "
                   f"{'squarefree' if sf else 'not squarefree'}")
    return False, f"D={d} is 2 mod 4"


def reduced(d: int, a: int, b: int, c: int) -> bool:
    if b * b - 4 * a * c != d:
        return False
    if a < 1 or c < 1:
        return False
    if abs(b) > a or a > c:
        return False
    if abs(b) == a or a == c:
        if b < 0:
            return False
    return True


def enumerate_e1(d: int) -> list[tuple[int, int, int]]:
    """E1: outer loop over a, then b in [-a, a]; c derived from the equation."""
    amax = isqrt(abs(d) // 3)
    out: list[tuple[int, int, int]] = []
    for a in range(1, amax + 1):
        for b in range(-a, a + 1):
            num = b * b - d
            if num % (4 * a) != 0:
                continue
            c = num // (4 * a)
            if reduced(d, a, b, c):
                out.append((a, b, c))
    return out


def enumerate_e2(d: int) -> list[tuple[int, int, int]]:
    """E2: outer loop over c, then b in [-c, c]; a derived from the equation;
    collected into a set, then sorted. Structurally different from E1."""
    amax = isqrt(abs(d) // 3)
    cmax = (amax * amax + abs(d)) // 4 + 1
    found: set[tuple[int, int, int]] = set()
    for c in range(1, cmax + 1):
        for b in range(-c, c + 1):
            num = b * b - d
            if num % (4 * c) != 0:
                continue
            a = num // (4 * c)
            if a < 1:
                continue
            if reduced(d, a, b, c):
                found.add((a, b, c))
    return sorted(found)


def jacobi(a: int, n: int) -> int:
    """Jacobi symbol (a/n) for odd positive n."""
    a %= n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def kronecker_symbol(a: int, n: int) -> int:
    """Kronecker symbol (a/n) for odd a and positive n, by 2-part stripping
    and quadratic reciprocity (the checker uses a different method)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1:
        return 1
    result = 1
    while n % 2 == 0:
        n //= 2
        result *= 1 if a % 8 in (1, 7) else -1
    if n == 1:
        return result
    return result * jacobi(a, n)


def interval_for_s(l30: Fraction) -> tuple[Fraction, Fraction]:
    """Enclose S = (sqrt(83)/pi) * L30 from the four enclosure corners."""
    if l30 == 0:
        return Fraction(0), Fraction(0)
    corners = [
        SQRT_LO * l30 / PI_LO, SQRT_LO * l30 / PI_HI,
        SQRT_HI * l30 / PI_LO, SQRT_HI * l30 / PI_HI,
    ]
    return min(corners), max(corners)


def decide_r(lo: Fraction, hi: Fraction) -> tuple[str, object, dict]:
    """Return (status, r-or-None, detail). status in
    {'scored', 'instrument_failure'} implementing the frozen gate: the
    interval must contain no half-integer and be short enough that 'the
    integer nearest to every point of the interval' is unique."""
    length = hi - lo
    ints = [k for k in range(floor(lo), floor(hi) + 1) if lo <= k <= hi]
    m_lo, m_hi = 2 * lo, 2 * hi
    halfs = [Fraction(m, 2) for m in range(floor(m_lo), floor(m_hi) + 1)
             if m % 2 == 1 and lo <= Fraction(m, 2) <= hi]
    detail = {
        "length": f"{length.numerator}/{length.denominator}",
        "length_float": float(length),
        "integers_inside": ints,
        "half_integers_inside": [f"{h.numerator}/{h.denominator}" for h in halfs],
        "endpoint_to_nearest_integer": {
            "lo": f"{lo.numerator}/{lo.denominator}",
            "hi": f"{hi.numerator}/{hi.denominator}",
            "floor_lo": floor(lo), "floor_hi": floor(hi),
        },
    }
    if length >= Fraction(1, 2):
        return "instrument_failure", None, {**detail, "reason": "interval_too_long"}
    if len(ints) >= 2:
        return "instrument_failure", None, {**detail, "reason": "two_integers_inside"}
    if halfs:
        return "instrument_failure", None, {**detail, "reason": "half_integer_boundary"}
    midpoint = (lo + hi) / 2
    r = floor(midpoint + Fraction(1, 2))
    if ints and ints[0] != r:
        return "instrument_failure", None, {**detail, "reason": "nearest_integer_inconsistent"}
    return "scored", r, detail


def git_state() -> dict:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], capture_output=True, text=True,
                              check=False).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain"))}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_str(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, help="run directory (created by the caller)")
    parser.add_argument("--run-id", required=True, help="allocated run id, e.g. RUN-CSIDH-db3ad8")
    args = parser.parse_args()
    out = Path(args.out)
    timings: list[dict] = []

    t0 = time.monotonic()
    labels = {}
    for d, expected in ((DISCRIMINANT, True), (CONTROL_FUNDAMENTAL, True),
                        (CONTROL_NONFUNDAMENTAL, False)):
        ok, reason = is_fundamental_discriminant(d)
        labels[str(d)] = {"fundamental": ok, "expected": expected, "reason": reason}
        if ok != expected:
            print(f"VOID: fundamentality label mismatch at D={d}: {reason}",
                  file=sys.stderr)
            return 2
    # The -83 claim row is scored only after all three labels are recorded.
    timings.append(stage_time("fundamentality-labeling", t0))

    t1 = time.monotonic()
    forms_e1 = enumerate_e1(DISCRIMINANT)
    forms_e2 = enumerate_e2(DISCRIMINANT)
    if sorted(forms_e1) != forms_e2:
        print("VOID: E1 and E2 disagree on the reduced forms of -83",
              file=sys.stderr)
        return 3
    h = len(forms_e2)
    timings.append(stage_time("enumerate-forms-83", t1))

    t2 = time.monotonic()
    forms84 = enumerate_e2(CONTROL_FUNDAMENTAL)
    count84 = len(forms84)
    timings.append(stage_time("enumerate-forms-84", t2))

    t3 = time.monotonic()
    chi = {str(n): kronecker_symbol(DISCRIMINANT, n) for n in range(1, TRUNCATION + 1)}
    if chi.get("1") != 1:
        print("VOID: chi(1) != 1", file=sys.stderr)
        return 4
    l30 = sum((Fraction(chi[str(n)], n) for n in range(1, TRUNCATION + 1)),
              Fraction(0))
    if __import__("math").gcd(l30.numerator, l30.denominator) != 1:
        print("VOID: L30 is not a reduced rational", file=sys.stderr)
        return 4
    timings.append(stage_time("kronecker-and-l30", t3))

    t4 = time.monotonic()
    lo, hi = interval_for_s(l30)
    status, r, interval_detail = decide_r(lo, hi)
    timings.append(stage_time("interval-and-decision", t4))

    if status == "scored":
        abs_diff = abs(r - h)
        outcome = "r_equals_h" if r == h else "r_differs_from_h"
    else:
        r, abs_diff = None, None
        outcome = "instrument_failure"

    started = datetime.now(timezone.utc).isoformat()
    manifest = {
        "experiment_id": "EXP-CSIDH-7886f6",
        "run_id": args.run_id,
        "trial_id": "class-number-truncation-83",
        "specification": "experiments/EXP-CSIDH-7886f6/specification.yaml",
        "driver": "experiments/EXP-CSIDH-7886f6/implementation/driver.py",
        "driver_sha256": sha256_file(Path(__file__).resolve()),
        "command": json.dumps(["python3", str(Path(__file__).resolve()),
                               "--out", str(out.resolve()), "--run-id", args.run_id]),
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "git": git_state(),
        "parameters": {
            "discriminant": DISCRIMINANT,
            "truncation_length": TRUNCATION,
            "control_fundamental": CONTROL_FUNDAMENTAL,
            "control_nonfundamental": CONTROL_NONFUNDAMENTAL,
            "reduction_convention": "|b| <= a <= c with b >= 0 when |b| = a or a = c",
            "enclosures": {
                "sqrt_83": {"lo": fraction_str(SQRT_LO), "hi": fraction_str(SQRT_HI),
                            "denominator": str(SCALE)},
                "pi": {"lo": fraction_str(PI_LO), "hi": fraction_str(PI_HI),
                       "denominator": str(SCALE)},
            },
            "seeds": "deterministic; no randomness",
        },
    }
    raw_result = {
        "experiment_id": "EXP-CSIDH-7886f6",
        "run_id": args.run_id,
        "labels": labels,
        "h": h,
        "forms_e1_count": len(forms_e1),
        "forms_e2_count": len(forms_e2),
        "chi_table": chi,
        "L30": {"numerator": l30.numerator, "denominator": l30.denominator,
                "float": float(l30)},
        "S_interval": {"lo": fraction_str(lo), "hi": fraction_str(hi),
                       "lo_float": float(lo), "hi_float": float(hi)},
        "interval_detail": interval_detail,
        "decision": {"status": status, "r": r},
        "abs_r_minus_h": abs_diff,
        "count_84": count84,
        "label_92": labels[str(CONTROL_NONFUNDAMENTAL)],
        "invariant_factors": None,
        "invariant_factors_note": "not computed; recorded as ignored by design",
        "outcome": outcome,
        "timings_seconds": timings,
    }
    reading = {
        "run_id": args.run_id,
        "experiment_id": "EXP-CSIDH-7886f6",
        "claim_row": "r versus h at discriminant -83, truncation 30",
        "outcome": outcome,
        "h": h,
        "r": r,
        "abs_r_minus_h": abs_diff,
        "instrument_checks": {
            "e1_equals_e2": True,
            "chi_1_is_1": True,
            "l30_reduced_rational": True,
            "labels_correct": True,
            "interval_valid": status == "scored",
        },
        "note": ("observation only; interpretation belongs to a later evidence "
                 "review, never to this run record"),
    }

    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.yaml").write_text(
        "# EXP-CSIDH-7886f6 run manifest (generated by driver.py)\n"
        + json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    (out / "raw-result.json").write_text(
        json.dumps(raw_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "forms-83.json").write_text(json.dumps({
        "discriminant": DISCRIMINANT,
        "fundamental": labels[str(DISCRIMINANT)]["fundamental"],
        "enumeration_e1": [list(f) for f in forms_e1],
        "enumeration_e2": [list(f) for f in forms_e2],
        "count": h,
    }, indent=2) + "\n", encoding="utf-8")
    (out / "forms-84.json").write_text(json.dumps({
        "discriminant": CONTROL_FUNDAMENTAL,
        "fundamental": labels[str(CONTROL_FUNDAMENTAL)]["fundamental"],
        "label_note": ("control discriminant; -84 = 4*(-21) with -21 = 3 mod 4 "
                       "squarefree is fundamental (design-time correction of the "
                       "source idea's premise); the non-fundamental probe is -92"),
        "enumeration_e2": [list(f) for f in forms84],
        "count": count84,
    }, indent=2) + "\n", encoding="utf-8")
    (out / "reading.yaml").write_text(
        "# EXP-CSIDH-7886f6 reading row (generated by driver.py)\n"
        + json.dumps(reading, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")

    print(json.dumps({"outcome": outcome, "h": h, "r": r,
                      "abs_r_minus_h": abs_diff}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
