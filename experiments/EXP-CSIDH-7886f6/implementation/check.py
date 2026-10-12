#!/usr/bin/env python3
"""EXP-CSIDH-7886f6 checker: re-derive the run's load-bearing quantities from
the frozen statement and parameters alone, then compare with the artifacts.

Independence from the driver:
  - fundamentality labels are re-derived per discriminant by direct reasoning
    (primality by trial division, the residue of D/4, squarefreeness),
    not by the driver's criterion routine;
  - the form count is a third enumeration: a bounded triple loop over
    (a, b, c) with no algebra derived from the discriminant equation beyond
    b^2 - 4ac = D itself;
  - chi(n) is recomputed by prime factorization and Euler's criterion, not by
    quadratic reciprocity;
  - L30, the interval arithmetic and the r decision are recomputed exactly
    from the stated enclosure fractions.

Exit 0 iff every check passes. Any mismatch is invalid output.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from math import floor
from pathlib import Path

DISCRIMINANT = -83
TRUNCATION = 30
CONTROL_FUNDAMENTAL = -84
CONTROL_NONFUNDAMENTAL = -92
SCALE = 10 ** 12


def load(path: Path):
    if path.name.endswith(".json"):
        return json.loads(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    body = "\n".join(line for line in text.splitlines()
                    if not line.lstrip().startswith("#"))
    return json.loads(body)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def squarefree_abs(n: int) -> bool:
    n = abs(n)
    if n <= 1:
        return True
    d = 2
    while d * d <= n:
        if n % d == 0:
            n //= d
            if n % d == 0:
                return False
        d += 1
    return True


def expected_fundamental(d: int) -> bool:
    """Blind re-derivation, one discriminant at a time."""
    if d == -83:
        # 83 is prime (trial division) and -83 = 3 mod 4, so D = -83 is a
        # fundamental discriminant.
        assert is_prime(83) and (-83) % 4 == 1
        return True
    if d == -84:
        # -84 = 4 * (-21); -21 = 3 mod 4 (since -21 = -6*4 + 3) and 21 = 3*7 is
        # squarefree, so -84 is the fundamental discriminant of Q(sqrt(-21)).
        m = -84 // 4
        assert m == -21 and m % 4 == 3 and squarefree_abs(m)
        return True
    if d == -92:
        # -92 = 4 * (-23); -23 = 1 mod 4, so D = 4m with m = 1 mod 4 is NOT
        # fundamental: it is the conductor-2 order of Q(sqrt(-23)).
        m = -92 // 4
        assert m == -23 and m % 4 == 1 and squarefree_abs(m)
        return False
    raise AssertionError(f"unexpected discriminant {d}")


def enumerate_forms_bruteforce(d: int) -> list[tuple[int, int, int]]:
    """Third enumeration: a bounded triple loop, no derived algebra."""
    found: set[tuple[int, int, int]] = set()
    for a in range(1, 40):
        for b in range(-40, 41):
            if abs(b) > a:
                continue
            for c in range(1, 120):
                if a > c:
                    continue
                if b * b - 4 * a * c != d:
                    continue
                if abs(b) == a or a == c:
                    if b < 0:
                        continue
                found.add((a, b, c))
    return sorted(found)


def factorize(n: int) -> dict[int, int]:
    out: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def chi_euler(a: int, n: int) -> int:
    """Kronecker symbol (a/n) by factorization and Euler's criterion."""
    if n == 1:
        return 1
    result = 1
    for p, e in factorize(n).items():
        if p == 2:
            leg = 1 if a % 8 in (1, 7) else -1  # a is odd in this contract
        else:
            ev = pow(a % p, (p - 1) // 2, p)
            if ev == 0:
                return 0
            leg = 1 if ev == 1 else -1
        result *= leg ** e
    return result


def fraction_str(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 64
    out = Path(sys.argv[1])
    problems: list[str] = []

    manifest = load(out / "manifest.yaml")
    raw = load(out / "raw-result.json")
    forms83 = load(out / "forms-83.json")
    forms84 = load(out / "forms-84.json")
    reading = load(out / "reading.yaml")

    # --- manifest: frozen parameters --------------------------------------
    params = manifest.get("parameters", {})
    if manifest.get("experiment_id") != "EXP-CSIDH-7886f6":
        problems.append("manifest experiment_id")
    if manifest.get("run_id") != raw.get("run_id") or reading.get("run_id") != raw.get("run_id"):
        problems.append("run_id disagrees across artifacts")
    if params.get("discriminant") != DISCRIMINANT or params.get("truncation_length") != TRUNCATION:
        problems.append("manifest parameters are not the frozen instance")
    if params.get("control_fundamental") != CONTROL_FUNDAMENTAL or \
            params.get("control_nonfundamental") != CONTROL_NONFUNDAMENTAL:
        problems.append("manifest control discriminants")
    enc = params.get("enclosures", {})
    sqrt_enc, pi_enc = enc.get("sqrt_83", {}), enc.get("pi", {})
    from math import isqrt
    s_num = isqrt(83 * SCALE * SCALE)
    sqrt_lo_expected, sqrt_hi_expected = Fraction(s_num, SCALE), Fraction(s_num + 1, SCALE)
    pi_lo_expected, pi_hi_expected = (Fraction(3141592653589, SCALE),
                                      Fraction(3141592653590, SCALE))
    try:
        sqrt_lo_rec = Fraction(str(sqrt_enc.get("lo")))
        sqrt_hi_rec = Fraction(str(sqrt_enc.get("hi")))
        pi_lo_rec = Fraction(str(pi_enc.get("lo")))
        pi_hi_rec = Fraction(str(pi_enc.get("hi")))
    except (ValueError, ZeroDivisionError, TypeError):
        problems.append("recorded enclosures are not parseable rationals")
        sqrt_lo_rec = sqrt_hi_rec = pi_lo_rec = pi_hi_rec = None
    if sqrt_lo_rec is not None and (sqrt_lo_rec != sqrt_lo_expected
                                    or sqrt_hi_rec != sqrt_hi_expected):
        problems.append("sqrt(83) enclosure is not the stated 10^12-denominator pair")
    if pi_lo_rec is not None and (pi_lo_rec != pi_lo_expected
                                  or pi_hi_rec != pi_hi_expected):
        problems.append("pi enclosure is not the stated 10^12-denominator pair")
    driver_on_disk = Path(__file__).resolve().parent / "driver.py"
    if manifest.get("driver_sha256") != hashlib.sha256(driver_on_disk.read_bytes()).hexdigest():
        problems.append("manifest driver_sha256 does not match driver.py on disk")

    # --- fundamentality labels: blind re-derivation ------------------------
    for d, key in ((DISCRIMINANT, str(DISCRIMINANT)),
                   (CONTROL_FUNDAMENTAL, str(CONTROL_FUNDAMENTAL)),
                   (CONTROL_NONFUNDAMENTAL, str(CONTROL_NONFUNDAMENTAL))):
        recorded = raw.get("labels", {}).get(key, {})
        if recorded.get("fundamental") != expected_fundamental(d):
            problems.append(f"fundamentality label of {d}")

    # --- form counts: third enumeration ----------------------------------
    brute83 = enumerate_forms_bruteforce(DISCRIMINANT)
    if [tuple(f) for f in forms83.get("enumeration_e1", [])] != brute83:
        problems.append("forms-83 E1 list disagrees with the brute-force enumeration")
    if [tuple(f) for f in forms83.get("enumeration_e2", [])] != brute83:
        problems.append("forms-83 E2 list disagrees with the brute-force enumeration")
    if forms83.get("count") != len(brute83) or raw.get("h") != len(brute83):
        problems.append("form count h disagrees with the brute-force enumeration")
    for f in brute83:
        a, b, c = f
        if b * b - 4 * a * c != DISCRIMINANT or abs(b) > a or a > c or a < 1:
            problems.append(f"form {f} violates the reduction conditions")
    brute84 = enumerate_forms_bruteforce(CONTROL_FUNDAMENTAL)
    if forms84.get("count") != len(brute84) or raw.get("count_84") != len(brute84):
        problems.append("count_84 disagrees with the brute-force enumeration")
    if forms84.get("discriminant") != CONTROL_FUNDAMENTAL or \
            forms84.get("fundamental") is not True:
        problems.append("forms-84 label")
    if raw.get("label_92", {}).get("fundamental") is not False:
        problems.append("label_92 must be non-fundamental")

    # --- chi table and L30 -------------------------------------------------
    chi_expected = {str(n): chi_euler(DISCRIMINANT, n)
                   for n in range(1, TRUNCATION + 1)}
    if raw.get("chi_table") != chi_expected:
        problems.append("chi table disagrees with factorization + Euler criterion")
    if chi_expected.get("1") != 1:
        problems.append("chi(1) != 1")
    l30 = sum((Fraction(chi_expected[str(n)], n) for n in range(1, TRUNCATION + 1)),
              Fraction(0))
    rec = raw.get("L30", {})
    if rec.get("numerator") != l30.numerator or rec.get("denominator") != l30.denominator:
        problems.append("L30 disagrees with the recomputed exact sum")
    from math import gcd
    if gcd(l30.numerator, l30.denominator) != 1:
        problems.append("L30 is not reduced")

    # --- interval and r decision -------------------------------------------
    sqrt_lo, sqrt_hi = Fraction(s_num, SCALE), Fraction(s_num + 1, SCALE)
    pi_lo, pi_hi = Fraction(3141592653589, SCALE), Fraction(3141592653590, SCALE)
    if l30 == 0:
        lo = hi = Fraction(0)
    else:
        corners = [sqrt_lo * l30 / pi_lo, sqrt_lo * l30 / pi_hi,
                   sqrt_hi * l30 / pi_lo, sqrt_hi * l30 / pi_hi]
        lo, hi = min(corners), max(corners)
    si = raw.get("S_interval", {})
    if si.get("lo") != fraction_str(lo) or si.get("hi") != fraction_str(hi):
        problems.append("S interval disagrees with the recomputed enclosure")
    length = hi - lo
    ints = [k for k in range(floor(lo), floor(hi) + 1) if lo <= k <= hi]
    m_lo, m_hi = 2 * lo, 2 * hi
    halfs = [Fraction(m, 2) for m in range(floor(m_lo), floor(m_hi) + 1)
             if m % 2 == 1 and lo <= Fraction(m, 2) <= hi]
    if length >= Fraction(1, 2) or len(ints) >= 2 or halfs:
        expected_status, expected_r = "instrument_failure", None
    else:
        expected_status = "scored"
        expected_r = floor((lo + hi) / 2 + Fraction(1, 2))
        if ints and ints[0] != expected_r:
            expected_status, expected_r = "instrument_failure", None
    decision = raw.get("decision", {})
    if decision.get("status") != expected_status or decision.get("r") != expected_r:
        problems.append("r decision disagrees with the recomputed gate")
    if reading.get("r") != expected_r or reading.get("outcome") != raw.get("outcome"):
        problems.append("reading row disagrees with the recomputed decision")
    h = len(brute83)
    if expected_status == "scored":
        if reading.get("h") != h or reading.get("abs_r_minus_h") != abs(expected_r - h):
            problems.append("reading row |r - h| is inconsistent")
        if raw.get("abs_r_minus_h") != abs(expected_r - h):
            problems.append("raw |r - h| is inconsistent")
    if reading.get("claim_row") != "r versus h at discriminant -83, truncation 30":
        problems.append("reading row must score r against h, nothing else")

    if problems:
        for p in problems:
            print(f"CHECK FAIL: {p}", file=sys.stderr)
        return 1
    print(json.dumps({"checks": "all passed", "h": h,
                      "r": expected_r, "status": expected_status}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
