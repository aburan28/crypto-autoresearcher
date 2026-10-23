"""Prepare and independently verify public prime-order ICPERF curve fixtures.

Generate with ``sage -python tools/icperf_prime_fixture.py generate ...``. The
Sage cardinality is used only to find candidates. The saved certificate is
checked with separate Python group arithmetic and the Hasse bound: if a
nonidentity point is killed by prime N, its order is N; when N exceeds the
Hasse interval's width, N is the only possible group order in that interval.

This prepares a curve. It selects no factor base or target and measures no IC
or rho cost. Scientific trials still require their frozen execution contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from crypto_autoresearcher.index_calculus.curve import (  # noqa: E402
    Curve,
    is_probable_prime,
    next_prime,
)

SCHEMA = "icperf-prime-curve-fixture-v1"


def _digest_int(*parts: object) -> int:
    data = "|".join([SCHEMA, *(str(part) for part in parts)]).encode("ascii")
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def curve_parameters(bits: int, seed: int, index: int) -> tuple[int, int, int]:
    """Deterministic, target-blind candidate at a requested order scale."""
    if not 50 <= bits <= 63 or seed < 0 or index < 0:
        raise ValueError("bits must be 50..63; seed and index must be nonnegative")
    # The margin exceeds the Hasse radius, so accepted orders stay below 2^bits.
    margin = 1 << ((bits + 1) // 2 + 2)
    offset = _digest_int(bits, seed, "prime") % (margin // 4)
    p = next_prime((1 << bits) - margin + offset)
    if p.bit_length() != bits or p >= 1 << bits:
        raise AssertionError("deterministic prime left requested bit range")
    a = _digest_int(bits, seed, index, "a") % p
    b = _digest_int(bits, seed, index, "b") % p
    return p, a, b


def verify_prime_order_witness(p: int, a: int, b: int, order: int,
                               point: tuple[int, int]) -> None:
    """Raise on an invalid complete group-order certificate.

    All integer checks and point arithmetic here are independent of Sage's
    cardinality implementation. For the 50..63-bit intended range the
    deterministic Miller-Rabin bases in ``curve.py`` cover p and order.
    """
    if not all(type(value) is int for value in (p, a, b, order, *point)):
        raise ValueError("certificate fields must be integers")
    if not (3 < p < (1 << 63) and p % 2 and is_probable_prime(p)):
        raise ValueError("p is not an admitted prime")
    if not (0 <= a < p and 0 <= b < p):
        raise ValueError("curve coefficients are not canonical")
    if not (1 < order < (1 << 63) and is_probable_prime(order)):
        raise ValueError("claimed group order is not an admitted prime")
    if (order - (p + 1)) ** 2 > 4 * p:
        raise ValueError("claimed order is outside the Hasse interval")
    if order * order <= 16 * p:
        raise ValueError("Hasse interval could contain another multiple")
    if len(point) != 2 or not all(0 <= value < p for value in point):
        raise ValueError("witness coordinates are not canonical")
    curve = Curve(p, a, b)
    if not curve.is_on_curve(point):
        raise ValueError("witness is not on the curve")
    if curve.mul(order, point) is not None:
        raise ValueError("prime order does not annihilate witness")


def verify_record(record: dict) -> None:
    if record.get("schema") != SCHEMA:
        raise ValueError("unknown fixture schema")
    bits, seed, index = (record[name] for name in ("bits", "seed", "candidate_index"))
    if any(type(value) is not int for value in (bits, seed, index)):
        raise ValueError("recipe fields must be integers")
    p, a, b = curve_parameters(bits, seed, index)
    curve = record["curve"]
    if (curve["p"], curve["a"], curve["b"]) != (p, a, b):
        raise ValueError("curve differs from deterministic recipe")
    if curve["order"].bit_length() != bits:
        raise ValueError("order differs from requested bit length")
    verify_prime_order_witness(p, a, b, curve["order"], tuple(record["witness"]))


def generate(bits: int, seed: int, max_curves: int) -> dict:
    if max_curves < 1:
        raise ValueError("max_curves must be positive")
    try:
        from sage.all import EllipticCurve, GF, Integer  # type: ignore
        from sage.version import version as sage_version  # type: ignore
    except ImportError as exc:
        raise RuntimeError("generation requires sage -python") from exc

    p, _, _ = curve_parameters(bits, seed, 0)
    field = GF(Integer(p))
    attempts = []
    for index in range(max_curves):
        _, a, b = curve_parameters(bits, seed, index)
        row = {"index": index, "a": a, "b": b}
        if (4 * a**3 + 27 * b**2) % p == 0:
            row["status"] = "singular"
            attempts.append(row)
            continue
        order = int(EllipticCurve(field, [Integer(a), Integer(b)]).cardinality())
        row["order"] = order
        row["status"] = "prime_order" if is_probable_prime(order) else "composite_order"
        attempts.append(row)
        if row["status"] != "prime_order" or order.bit_length() != bits:
            continue
        # The witness search is deterministic and independent of Sage lifting.
        curve = Curve(p, a, b)
        first_x = _digest_int(bits, seed, index, "point") % p
        witness = None
        for step in range(1024):
            witness = curve.lift_x((first_x + step) % p)
            if witness is not None:
                break
        if witness is None:
            raise RuntimeError("no witness in 1024 deterministic x candidates")
        try:
            verify_prime_order_witness(p, a, b, order, witness)
        except ValueError as exc:
            row["status"] = "independent_certificate_failed"
            row["reason"] = str(exc)
            continue
        record = {
            "schema": SCHEMA,
            "bits": bits,
            "seed": seed,
            "candidate_index": index,
            "curve": {"p": p, "a": a, "b": b, "order": order},
            "witness": list(witness),
            "attempts": attempts,
            "provenance": {
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                           capture_output=True, text=True, check=True).stdout.strip(),
                "sage_version": sage_version,
                "python_version": platform.python_version(),
            },
            "scope": "public prime-order curve fixture only; no factor base, target, or ECDLP timing",
        }
        verify_record(record)
        return record
    raise RuntimeError(f"no independently certified prime-order curve in {max_curves} candidates")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("generate")
    make.add_argument("--bits", type=int, required=True)
    make.add_argument("--seed", type=int, required=True)
    make.add_argument("--max-curves", type=int, default=256)
    make.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("path", type=Path)
    args = parser.parse_args()
    if args.command == "generate":
        record = generate(args.bits, args.seed, args.max_curves)
        with args.out.open("x") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
        print(json.dumps({"path": str(args.out), "bits": record["bits"],
                          "candidate_index": record["candidate_index"],
                          "order": record["curve"]["order"], "status": "verified"},
                         sort_keys=True))
    else:
        verify_record(json.loads(args.path.read_text()))
        print(json.dumps({"path": str(args.path), "status": "verified"}, sort_keys=True))


if __name__ == "__main__":
    main()
